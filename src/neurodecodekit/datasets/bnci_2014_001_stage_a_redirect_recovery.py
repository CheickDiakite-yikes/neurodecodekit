"""Signed-object recovery for the consumed BNCI-C3C5-1 Stage A acquisition.

The recovery interprets public manifest metadata and opaque payload bytes only.
It is additive so the original generated downloader and consumed Stage A wrapper
remain byte-identical.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import resource
import secrets
import shutil
import signal
import ssl
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import Message
from contextlib import contextmanager
from pathlib import Path
from typing import Any, BinaryIO, Callable, Iterable, Mapping, Sequence

from neurodecodekit.datasets.bnci_2014_001_acquisition import (
    ATTEMPT_CAP_PER_FILE,
    BASE_URL,
    DISK_CAP_BYTES,
    FREE_DISK_FLOOR_BYTES,
    LANE_ID,
    NETWORK_CAP_BYTES,
    REGISTERED_BYTES,
    REGISTERED_FILES,
    REQUEST_CAP,
    SCHEMA_VERSION,
    BNCIAcquisitionRefusal,
    PayloadMember,
    Transport,
    TransportResponse,
    registered_members,
)
from neurodecodekit.datasets.bnci_2014_001_stage_a import (
    CHUNK_BYTES,
    PEAK_RSS_CAP_BYTES,
    PUBLIC_OUTPUT_CAP_BYTES,
    REQUEST_TIMEOUT_SECONDS,
    RUNTIME_CAP_SECONDS,
)


DECISION_RELATIVE_PATH = Path(
    "registries/"
    "bnci_2014_001_stage_a_redirect_recovery_authorization_decision.v0.json"
)
DECISION_SHA256 = "fe8ec85f92b871e41a5c5abf6ff28f3de2b0681f0e93852946565fef587a875d"
DECISION_COMMIT = "588dd70c62a6f7041d677f9baf35e476ef739627"
DECISION_CI_RUN_ID = 32_803_138_246
DECISION_BASE_JOB_ID = 97_667_897_074
DECISION_OPTIONAL_JOB_ID = 97_667_896_798
IMPLEMENTATION_ACTIVATION_RELATIVE_PATH = Path(
    "registries/"
    "bnci_2014_001_stage_a_redirect_recovery_implementation_activation.v0.json"
)
QUALIFICATION_RESULT_RELATIVE_PATH = Path(
    "registries/"
    "bnci_2014_001_stage_a_redirect_recovery_generated_result.v0.json"
)
MANIFEST_URL = "https://data.nemar.org/nm000139/v1.0.2/manifest.json"
MANIFEST_BODY_CAP_BYTES = 1_048_576
MANIFEST_NODE_CAP = 100_000
SIGNED_OBJECT_HOST = "nemar.s3.us-east-2.amazonaws.com"
SIGNED_OBJECT_PATH_PREFIX = "/nm000139/objects/"
TOTAL_NETWORK_CAP_BYTES = NETWORK_CAP_BYTES + MANIFEST_BODY_CAP_BYTES
ORIGINAL_MARKER_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_acquisition_v0.consumed.json"
)
ORIGINAL_MARKER_BYTES = 297
ORIGINAL_MARKER_SHA256 = (
    "e30e2abf7c1e55eca6663e5ed06b0d36d3e351865213af78bb3d9ccb6b94b854"
)
RECOVERY_BUNDLE_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_redirect_recovery_payload_v1"
)
RECOVERY_MARKER_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_redirect_recovery_v1.consumed.json"
)
RECOVERY_RECEIPT_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_redirect_recovery_receipt.private.v1.json"
)
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
_SIGNED_QUERY_REQUIRED = {
    "X-Amz-Algorithm",
    "X-Amz-Credential",
    "X-Amz-Date",
    "X-Amz-Expires",
    "X-Amz-SignedHeaders",
    "X-Amz-Signature",
}
_SIGNED_QUERY_OPTIONAL = {"response-content-disposition"}
_SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
_GIT_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}\Z")
_AMZ_DATE_PATTERN = re.compile(r"[0-9]{8}T[0-9]{6}Z\Z")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


ManifestOpenRequest = Callable[[urllib.request.Request, float], BinaryIO]


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _single_decimal_header(headers: Message, name: str) -> int:
    values = headers.get_all(name, [])
    if len(values) != 1 or not values[0].isdigit():
        raise BNCIAcquisitionRefusal(f"manifest response {name} is invalid")
    return int(values[0])


def _read_regular_nofollow(path: Path, maximum_bytes: int) -> bytes:
    try:
        info = path.lstat()
    except FileNotFoundError as exc:
        raise BNCIAcquisitionRefusal("required recovery proof path is absent") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BNCIAcquisitionRefusal("recovery proof path is not a direct regular file")
    if info.st_size > maximum_bytes:
        raise BNCIAcquisitionRefusal("recovery proof path exceeds its byte cap")
    with path.open("rb") as handle:
        payload = handle.read(maximum_bytes + 1)
    if len(payload) != info.st_size:
        raise BNCIAcquisitionRefusal("recovery proof path changed during read")
    return payload


def _directory_open_flags() -> int:
    return (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )


@contextmanager
def _anchored_directory(root: Path, target: Path):
    _assert_safe_directory_ancestry(root, target, create=False)
    relative = target.relative_to(root)
    descriptor = os.open(root, _directory_open_flags())
    try:
        for part in relative.parts:
            next_descriptor = os.open(part, _directory_open_flags(), dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_descriptor
        yield descriptor
    finally:
        os.close(descriptor)


def _exclusive_write(path: Path, payload: bytes) -> None:
    root = _repo_root()
    flags = (
        os.O_WRONLY
        | os.O_CREAT
        | os.O_EXCL
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        with _anchored_directory(root, path.parent) as parent_fd:
            file_descriptor = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
    except FileExistsError as exc:
        raise BNCIAcquisitionRefusal("recovery output already exists") from exc
    try:
        view = memoryview(payload)
        while view:
            written = os.write(file_descriptor, view)
            if written <= 0:
                raise BNCIAcquisitionRefusal("recovery output write made no progress")
            view = view[written:]
        os.fsync(file_descriptor)
    finally:
        os.close(file_descriptor)


def _read_regular_anchored(root: Path, path: Path, maximum_bytes: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    with _anchored_directory(root, path.parent) as parent_fd:
        try:
            file_descriptor = os.open(path.name, flags, dir_fd=parent_fd)
        except FileNotFoundError as exc:
            raise BNCIAcquisitionRefusal("required anchored file is absent") from exc
    try:
        info = os.fstat(file_descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > maximum_bytes:
            raise BNCIAcquisitionRefusal("anchored file identity is unsafe")
        chunks: list[bytes] = []
        observed = 0
        while True:
            chunk = os.read(file_descriptor, min(CHUNK_BYTES, maximum_bytes + 1 - observed))
            if not chunk:
                break
            observed += len(chunk)
            if observed > maximum_bytes:
                raise BNCIAcquisitionRefusal("anchored file exceeds its byte cap")
            chunks.append(chunk)
        if observed != info.st_size:
            raise BNCIAcquisitionRefusal("anchored file changed during read")
        return b"".join(chunks)
    finally:
        os.close(file_descriptor)


def _freeze_threads(environ: Mapping[str, str]) -> None:
    if any(environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise BNCIAcquisitionRefusal("recovery thread environment is not frozen")


def _peak_rss_bytes() -> int:
    observed = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(observed if sys.platform == "darwin" else observed * 1024)


def _assert_safe_directory_ancestry(root: Path, target: Path, *, create: bool) -> None:
    root_info = root.lstat()
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise BNCIAcquisitionRefusal("recovery repository root is not direct")
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise BNCIAcquisitionRefusal("recovery output escaped the repository") from exc
    current = root
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if create:
                current.mkdir()
                info = current.lstat()
            else:
                raise BNCIAcquisitionRefusal("recovery output ancestor is absent") from None
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise BNCIAcquisitionRefusal("recovery output ancestry is not direct")


class ResourceMonitor:
    """Enforce live wall-clock and process RSS limits between bounded reads."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.started = time.perf_counter()
        self.free_disk_started = shutil.disk_usage(root).free

    def check(self, *, required_free_bytes: int = 0) -> None:
        if time.perf_counter() - self.started > RUNTIME_CAP_SECONDS:
            raise BNCIAcquisitionRefusal("redirect recovery runtime cap exceeded")
        if _peak_rss_bytes() > PEAK_RSS_CAP_BYTES:
            raise BNCIAcquisitionRefusal("redirect recovery peak RSS cap exceeded")
        free_now = shutil.disk_usage(self.root).free
        if self.free_disk_started - free_now > DISK_CAP_BYTES:
            raise BNCIAcquisitionRefusal("redirect recovery incremental-disk cap exceeded")
        if free_now < required_free_bytes:
            raise BNCIAcquisitionRefusal("redirect recovery lacks space for the next chunk")

    def request_timeout(self) -> float:
        self.check()
        remaining = RUNTIME_CAP_SECONDS - (time.perf_counter() - self.started)
        if remaining <= 0:
            raise BNCIAcquisitionRefusal("redirect recovery runtime cap exhausted")
        return min(REQUEST_TIMEOUT_SECONDS, remaining)


def read_green_recovery_decision(repo_root: str | Path) -> dict[str, Any]:
    payload = _read_regular_nofollow(
        Path(repo_root) / DECISION_RELATIVE_PATH,
        PUBLIC_OUTPUT_CAP_BYTES,
    )
    if _sha256(payload) != DECISION_SHA256:
        raise BNCIAcquisitionRefusal("redirect-recovery decision hash changed")
    try:
        decision = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BNCIAcquisitionRefusal("redirect-recovery decision JSON is invalid") from exc
    maintainer = decision.get("maintainer_decision", {})
    request = decision.get("green_request", {})
    proof = decision.get("green_request_proof", {})
    authority = decision.get("authorized_after_own_remote_green", {})
    if (
        decision.get("status")
        != "packet_bound_short_form_authorized_delayed_effect_until_own_remote_green"
        or maintainer.get("message") != "continue, "
        or maintainer.get("sha256")
        != "ce4f9af7b90d5ee833a97e706595b5d72470f09570be4c2c69050971f3defb4f"
        or request.get("both_required_jobs_green") is not True
        or proof.get("both_required_jobs_green") is not True
        or authority.get("one_generated_recovery_implementation") is not True
        or authority.get("one_replacement_Stage_A_recovery_invocation") is not True
    ):
        raise BNCIAcquisitionRefusal("redirect-recovery authority changed")
    return decision


def read_green_implementation_activation(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    payload = _read_regular_nofollow(
        root / IMPLEMENTATION_ACTIVATION_RELATIVE_PATH,
        PUBLIC_OUTPUT_CAP_BYTES,
    )
    try:
        activation = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BNCIAcquisitionRefusal("recovery implementation activation is invalid") from exc
    green = activation.get("green_implementation", {})
    artifacts = activation.get("implementation_artifacts", [])
    required_paths = {
        "src/neurodecodekit/datasets/bnci_2014_001_stage_a_redirect_recovery.py",
        "src/neurodecodekit/bnci_c3c5_stage_a_redirect_recovery_cli.py",
        "tests/test_bnci_2014_001_stage_a_redirect_recovery_implementation.py",
    }
    if (
        activation.get("status")
        != "implementation_activation_effective_after_own_remote_green"
        or not isinstance(green.get("commit"), str)
        or not _GIT_COMMIT_PATTERN.fullmatch(green["commit"])
        or type(green.get("CI_run_id")) is not int
        or type(green.get("base_python_job_id")) is not int
        or type(green.get("optional_neuro_readers_job_id")) is not int
        or green.get("both_required_jobs_green") is not True
        or not isinstance(artifacts, list)
        or len(artifacts) != len(required_paths)
        or any(not isinstance(row, Mapping) for row in artifacts)
        or {row.get("path") for row in artifacts if isinstance(row, Mapping)}
        != required_paths
    ):
        raise BNCIAcquisitionRefusal("recovery implementation activation changed")
    for row in artifacts:
        path = row.get("path")
        digest = row.get("sha256")
        if not isinstance(path, str) or not _SHA256_PATTERN.fullmatch(str(digest)):
            raise BNCIAcquisitionRefusal("recovery implementation artifact is invalid")
        artifact = _read_regular_nofollow(root / path, PUBLIC_OUTPUT_CAP_BYTES)
        if _sha256(artifact) != digest:
            raise BNCIAcquisitionRefusal("recovery implementation artifact hash changed")
        committed = _git_output(root, "show", f"{green['commit']}:{path}")
        if _sha256(committed) != digest or committed != artifact:
            raise BNCIAcquisitionRefusal(
                "recovery implementation artifact differs from its green commit"
            )
    activation_path = IMPLEMENTATION_ACTIVATION_RELATIVE_PATH.as_posix()
    if _git_output(root, "show", f"HEAD:{activation_path}") != payload:
        raise BNCIAcquisitionRefusal("recovery activation differs from HEAD")
    _git_require_success(root, "diff", "--quiet", "HEAD", "--")
    _git_require_success(root, "diff", "--cached", "--quiet", "--")
    _git_require_success(root, "merge-base", "--is-ancestor", green["commit"], "HEAD")
    return activation


def _git_output(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        check=False,
        capture_output=True,
        timeout=15,
    )
    if completed.returncode != 0:
        raise BNCIAcquisitionRefusal("required Git proof lookup failed")
    return completed.stdout


def _git_require_success(root: Path, *arguments: str) -> None:
    completed = subprocess.run(
        ("git", *arguments),
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=15,
    )
    if completed.returncode != 0:
        raise BNCIAcquisitionRefusal("required Git proof relation failed")


@contextmanager
def _runtime_alarm(seconds: float):
    if not hasattr(signal, "setitimer") or seconds <= 0:
        raise BNCIAcquisitionRefusal("strict wall-clock alarm is unavailable")
    previous_timer = signal.getitimer(signal.ITIMER_REAL)
    if previous_timer != (0.0, 0.0):
        raise BNCIAcquisitionRefusal("another wall-clock alarm is already active")
    previous_handler = signal.getsignal(signal.SIGALRM)

    def refuse_timeout(_signum, _frame):  # noqa: ANN001, ANN202
        raise BNCIAcquisitionRefusal("redirect recovery wall-clock cap exceeded")

    signal.signal(signal.SIGALRM, refuse_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0.0)
        signal.signal(signal.SIGALRM, previous_handler)


class StandardLibraryManifestClient:
    """TLS-verified, proxy-free, no-redirect client for one bounded manifest GET."""

    def __init__(
        self,
        *,
        opener: ManifestOpenRequest | None = None,
        monitor: ResourceMonitor | None = None,
    ) -> None:
        self._monitor = monitor
        if opener is not None:
            self._open = opener
            return
        context = ssl.create_default_context()
        built = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )
        self._open = lambda request, timeout: built.open(request, timeout=timeout)

    def fetch(self, url: str = MANIFEST_URL) -> bytes:
        if url != MANIFEST_URL:
            raise BNCIAcquisitionRefusal("manifest URL differs from the pinned source")
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "identity",
                "User-Agent": "NeuroDecodeKit-BNCI-C3C5-1-Recovery/0.1",
            },
            method="GET",
        )
        timeout = (
            self._monitor.request_timeout()
            if self._monitor is not None
            else REQUEST_TIMEOUT_SECONDS
        )
        try:
            response = self._open(request, timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise BNCIAcquisitionRefusal("pinned manifest request failed") from exc
        try:
            if response.geturl() != url or response.getcode() != 200:
                raise BNCIAcquisitionRefusal("pinned manifest redirected or returned non-200")
            content_length = _single_decimal_header(response.headers, "Content-Length")
            if not 0 < content_length <= MANIFEST_BODY_CAP_BYTES:
                raise BNCIAcquisitionRefusal("pinned manifest length exceeds its cap")
            if response.headers.get("Content-Encoding") not in (None, "identity"):
                raise BNCIAcquisitionRefusal("pinned manifest encoding is not identity")
            chunks: list[bytes] = []
            observed = 0
            while True:
                if self._monitor is not None:
                    self._monitor.check()
                chunk = response.read(min(CHUNK_BYTES, MANIFEST_BODY_CAP_BYTES + 1 - observed))
                if self._monitor is not None:
                    self._monitor.check()
                if not chunk:
                    break
                if not isinstance(chunk, bytes):
                    raise BNCIAcquisitionRefusal("pinned manifest yielded non-bytes")
                observed += len(chunk)
                if observed > MANIFEST_BODY_CAP_BYTES:
                    raise BNCIAcquisitionRefusal("pinned manifest body exceeded its cap")
                chunks.append(chunk)
            if observed != content_length:
                raise BNCIAcquisitionRefusal("pinned manifest body length differs")
            return b"".join(chunks)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise BNCIAcquisitionRefusal("pinned manifest body read failed") from exc
        finally:
            response.close()


class ResourceBoundRangeTransport:
    """Direct signed-object transport with per-read time and RSS enforcement."""

    def __init__(
        self,
        monitor: ResourceMonitor,
        *,
        opener: ManifestOpenRequest | None = None,
    ) -> None:
        self._monitor = monitor
        if opener is not None:
            self._open = opener
            return
        context = ssl.create_default_context()
        built = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )
        self._open = lambda request, timeout: built.open(request, timeout=timeout)

    def __call__(self, url: str, offset: int) -> TransportResponse:
        validate_url = urllib.parse.urlsplit(url)
        if validate_url.scheme != "https" or validate_url.hostname != SIGNED_OBJECT_HOST:
            raise BNCIAcquisitionRefusal("payload transport URL escaped the signed host")
        headers = {
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-BNCI-C3C5-1-Recovery/0.1",
        }
        if offset:
            headers["Range"] = f"bytes={offset}-"
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            response = self._open(request, self._monitor.request_timeout())
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ConnectionError("signed payload request failed") from exc
        if response.geturl() != url:
            response.close()
            raise BNCIAcquisitionRefusal("signed payload response redirected")
        content_length = _single_decimal_header(response.headers, "Content-Length")
        if response.headers.get("Content-Encoding") not in (None, "identity"):
            response.close()
            raise BNCIAcquisitionRefusal("signed payload response encoding is not identity")
        status = response.getcode()
        content_range = response.headers.get_all("Content-Range", [])
        if len(content_range) > 1:
            response.close()
            raise BNCIAcquisitionRefusal("signed payload Content-Range is duplicated")
        range_start: int | None = None
        if content_range:
            value = content_range[0]
            if not value.startswith("bytes ") or "-" not in value or "/" not in value:
                response.close()
                raise BNCIAcquisitionRefusal("signed payload Content-Range is invalid")
            raw_start = value.removeprefix("bytes ").split("-", 1)[0]
            if not raw_start.isdigit():
                response.close()
                raise BNCIAcquisitionRefusal("signed payload range start is invalid")
            range_start = int(raw_start)

        def body() -> Iterable[bytes]:
            observed = 0
            try:
                while True:
                    self._monitor.check(required_free_bytes=CHUNK_BYTES)
                    chunk = response.read(CHUNK_BYTES)
                    self._monitor.check(required_free_bytes=len(chunk))
                    if not chunk:
                        break
                    if not isinstance(chunk, bytes):
                        raise BNCIAcquisitionRefusal("signed payload yielded non-bytes")
                    if observed + len(chunk) > content_length:
                        raise BNCIAcquisitionRefusal("signed payload exceeded declared bytes")
                    observed += len(chunk)
                    yield chunk
                if observed != content_length:
                    raise ConnectionError("signed payload stream ended early")
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                raise ConnectionError("signed payload stream failed") from exc
            finally:
                response.close()

        return TransportResponse(status, content_length, range_start, body())


def _strict_json_loads(payload: bytes) -> Any:
    def object_pairs(pairs):  # noqa: ANN001, ANN202
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise BNCIAcquisitionRefusal("manifest JSON key is duplicated")
            result[key] = value
        return result

    def reject_constant(_value):  # noqa: ANN001, ANN202
        raise BNCIAcquisitionRefusal("manifest JSON constant is non-finite")

    try:
        return json.loads(
            payload,
            object_pairs_hook=object_pairs,
            parse_constant=reject_constant,
        )
    except BNCIAcquisitionRefusal:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise BNCIAcquisitionRefusal("manifest JSON is invalid") from exc


def _manifest_rows(parsed: Any) -> list[Mapping[str, Any]]:
    if isinstance(parsed, list):
        rows = parsed
    elif isinstance(parsed, Mapping) and isinstance(parsed.get("files"), list):
        rows = parsed["files"]
    else:
        raise BNCIAcquisitionRefusal("manifest record container is invalid")
    if len(rows) > MANIFEST_NODE_CAP or any(not isinstance(row, Mapping) for row in rows):
        raise BNCIAcquisitionRefusal("manifest record table is invalid or exceeds its cap")
    return rows


def _row_signed_url_candidates(row: Mapping[str, Any]) -> list[str]:
    candidates: list[str] = []
    for key in ("url", "signed_url", "signed_object_url", "download_url"):
        value = row.get(key)
        if isinstance(value, str):
            candidates.append(value)
    urls = row.get("urls")
    if isinstance(urls, Mapping):
        candidates.extend(value for value in urls.values() if isinstance(value, str))
    elif isinstance(urls, list):
        candidates.extend(value for value in urls if isinstance(value, str))
    return candidates


def _expected_object_path(member: PayloadMember) -> str:
    return (
        f"{SIGNED_OBJECT_PATH_PREFIX}SHA256E-s{member.bytes}--{member.sha256}.mat"
    )


def validate_signed_object_url(url: str, member: PayloadMember) -> str:
    if not isinstance(url, str) or len(url) > 8_192:
        raise BNCIAcquisitionRefusal("signed object URL is malformed")
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise BNCIAcquisitionRefusal("signed object URL authority is invalid") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != SIGNED_OBJECT_HOST
        or port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.path != _expected_object_path(member)
    ):
        raise BNCIAcquisitionRefusal("signed object URL authority or path differs")
    pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    if len(pairs) != len({key for key, _value in pairs}):
        raise BNCIAcquisitionRefusal("signed object URL query key is duplicated")
    query = dict(pairs)
    if set(query) - (_SIGNED_QUERY_REQUIRED | _SIGNED_QUERY_OPTIONAL):
        raise BNCIAcquisitionRefusal("signed object URL query key is not allowlisted")
    if not _SIGNED_QUERY_REQUIRED.issubset(query):
        raise BNCIAcquisitionRefusal("signed object URL query is incomplete")
    if (
        query["X-Amz-Algorithm"] != "AWS4-HMAC-SHA256"
        or not query["X-Amz-Credential"].endswith("/aws4_request")
        or not _AMZ_DATE_PATTERN.fullmatch(query["X-Amz-Date"])
        or not query["X-Amz-Expires"].isdigit()
        or not 0 < int(query["X-Amz-Expires"]) <= 3_600
        or query["X-Amz-SignedHeaders"] != "host"
        or not _SHA256_PATTERN.fullmatch(query["X-Amz-Signature"])
    ):
        raise BNCIAcquisitionRefusal("signed object URL query value is invalid")
    disposition = query.get("response-content-disposition")
    if disposition is not None and (not disposition or "\r" in disposition or "\n" in disposition):
        raise BNCIAcquisitionRefusal("signed object content disposition is invalid")
    return url


def _row_size(row: Mapping[str, Any]) -> int:
    values = [row[key] for key in ("bytes", "size") if key in row]
    if (
        not values
        or any(type(value) is not int or value <= 0 for value in values)
        or len(set(values)) != 1
    ):
        raise BNCIAcquisitionRefusal("selected manifest size is missing or ambiguous")
    return values[0]


def _row_sha256(row: Mapping[str, Any]) -> str:
    values = [row[key] for key in ("sha256", "checksum") if key in row]
    if not values or any(not isinstance(value, str) for value in values):
        raise BNCIAcquisitionRefusal("selected manifest digest is missing or ambiguous")
    normalized = {
        value.removeprefix("sha256:").removeprefix("SHA256:").lower()
        for value in values
    }
    if len(normalized) != 1:
        raise BNCIAcquisitionRefusal("selected manifest digest fields disagree")
    value = normalized.pop()
    if not _SHA256_PATTERN.fullmatch(value):
        raise BNCIAcquisitionRefusal("selected manifest digest is invalid")
    return value


def validate_manifest_signed_urls(
    manifest_payload: bytes,
    members: Sequence[PayloadMember],
) -> dict[str, str]:
    if not isinstance(manifest_payload, bytes) or not 0 < len(manifest_payload) <= MANIFEST_BODY_CAP_BYTES:
        raise BNCIAcquisitionRefusal("manifest payload is absent or exceeds its cap")
    parsed = _strict_json_loads(manifest_payload)
    normalized = tuple(members)
    expected = {member.relative_path: member for member in normalized}
    if len(expected) != len(normalized):
        raise BNCIAcquisitionRefusal("registered recovery member path is duplicated")
    selected_rows: dict[str, list[Mapping[str, Any]]] = {path: [] for path in expected}
    for row in _manifest_rows(parsed):
        path = row.get("path")
        if isinstance(path, str) and path in selected_rows:
            selected_rows[path].append(row)
    signed_urls: dict[str, str] = {}
    for path, member in expected.items():
        selected = selected_rows[path]
        if len(selected) != 1:
            raise BNCIAcquisitionRefusal("selected manifest record is missing or duplicated")
        row = selected[0]
        if _row_size(row) != member.bytes or _row_sha256(row) != member.sha256:
            raise BNCIAcquisitionRefusal("selected manifest identity differs")
        candidates: list[str] = []
        for value in _row_signed_url_candidates(row):
            try:
                parsed_url = urllib.parse.urlsplit(value)
            except ValueError:
                continue
            if parsed_url.hostname == SIGNED_OBJECT_HOST:
                candidates.append(validate_signed_object_url(value, member))
        unique = list(dict.fromkeys(candidates))
        if len(unique) != 1:
            raise BNCIAcquisitionRefusal("selected manifest signed URL is missing or ambiguous")
        signed_urls[path] = unique[0]
    if len(signed_urls) != len(normalized):
        raise BNCIAcquisitionRefusal("validated signed URL inventory is incomplete")
    return dict(sorted(signed_urls.items()))


class SignedObjectTransportAdapter:
    """Map frozen logical members to validated signed object URLs."""

    def __init__(self, signed_urls: Mapping[str, str], *, transport: Transport) -> None:
        if not callable(transport) or not signed_urls:
            raise BNCIAcquisitionRefusal("signed object transport mapping is invalid")
        self._signed_urls = dict(signed_urls)
        self._transport = transport

    def __call__(self, logical_url: str, offset: int) -> TransportResponse:
        if not logical_url.startswith(BASE_URL):
            raise BNCIAcquisitionRefusal("logical recovery URL escaped the pinned base")
        relative_path = logical_url.removeprefix(BASE_URL)
        if BASE_URL + relative_path != logical_url or relative_path not in self._signed_urls:
            raise BNCIAcquisitionRefusal("logical recovery member is not registered")
        return self._transport(self._signed_urls[relative_path], offset)


def _exists_at(directory_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except FileNotFoundError:
        return False
    return True


def _validate_recovery_member(member: PayloadMember) -> None:
    path = Path(member.relative_path)
    if (
        path.is_absolute()
        or path.parts[:1] != ("sourcedata",)
        or len(path.parts) != 2
        or ".." in path.parts
        or not path.name.endswith(".mat")
        or type(member.bytes) is not int
        or member.bytes <= 0
        or not _SHA256_PATTERN.fullmatch(member.sha256)
    ):
        raise BNCIAcquisitionRefusal("anchored recovery member is invalid")


def _write_all(file_descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(file_descriptor, view)
        if written <= 0:
            raise BNCIAcquisitionRefusal("anchored payload write made no progress")
        view = view[written:]


def _regular_size_at(directory_fd: int, name: str) -> int:
    info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BNCIAcquisitionRefusal("anchored payload member is not direct and regular")
    return info.st_size


def _hash_file_at(directory_fd: int, name: str) -> tuple[int, str]:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)
    file_descriptor = os.open(name, flags, dir_fd=directory_fd)
    try:
        expected_size = os.fstat(file_descriptor).st_size
        observed = 0
        digest = hashlib.sha256()
        while True:
            chunk = os.read(file_descriptor, CHUNK_BYTES)
            if not chunk:
                break
            observed += len(chunk)
            digest.update(chunk)
        if observed != expected_size:
            raise BNCIAcquisitionRefusal("anchored payload changed during hash pass")
        return observed, digest.hexdigest()
    finally:
        os.close(file_descriptor)


def _cleanup_work_directory(parent_fd: int, work_name: str) -> None:
    work_fd = os.open(work_name, _directory_open_flags(), dir_fd=parent_fd)
    try:
        entries = set(os.listdir(work_fd))
        if "sourcedata" in entries:
            source_fd = os.open("sourcedata", _directory_open_flags(), dir_fd=work_fd)
            try:
                for name in os.listdir(source_fd):
                    info = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
                    if not stat.S_ISREG(info.st_mode):
                        raise BNCIAcquisitionRefusal(
                            "anchored cleanup found an unexpected payload type"
                        )
                    os.unlink(name, dir_fd=source_fd)
            finally:
                os.close(source_fd)
            os.rmdir("sourcedata", dir_fd=work_fd)
            entries.remove("sourcedata")
        if "manifest.private.v0.json" in entries:
            info = os.stat(
                "manifest.private.v0.json",
                dir_fd=work_fd,
                follow_symlinks=False,
            )
            if not stat.S_ISREG(info.st_mode):
                raise BNCIAcquisitionRefusal("anchored cleanup manifest is not regular")
            os.unlink("manifest.private.v0.json", dir_fd=work_fd)
            entries.remove("manifest.private.v0.json")
        if entries:
            raise BNCIAcquisitionRefusal("anchored cleanup found an unexpected entry")
    finally:
        os.close(work_fd)
    os.rmdir(work_name, dir_fd=parent_fd)


def acquire_members_anchored(
    root: Path,
    members: Sequence[PayloadMember],
    destination: Path,
    *,
    transport: Transport,
    attempts_per_file: int = ATTEMPT_CAP_PER_FILE,
    request_cap: int = REQUEST_CAP,
    network_cap_bytes: int = NETWORK_CAP_BYTES,
    disk_cap_bytes: int = DISK_CAP_BYTES,
    minimum_free_bytes: int = FREE_DISK_FLOOR_BYTES,
) -> dict[str, Any]:
    """Acquire opaque members with all mutations anchored to directory FDs."""

    normalized = tuple(members)
    if not normalized or not callable(transport):
        raise BNCIAcquisitionRefusal("anchored member table or transport is invalid")
    for member in normalized:
        _validate_recovery_member(member)
    if len({member.relative_path for member in normalized}) != len(normalized):
        raise BNCIAcquisitionRefusal("anchored recovery member path is duplicated")
    expected_bytes = sum(member.bytes for member in normalized)
    if expected_bytes > disk_cap_bytes:
        raise BNCIAcquisitionRefusal("anchored recovery exceeds its disk cap")
    if type(attempts_per_file) is not int or not 1 <= attempts_per_file <= 3:
        raise BNCIAcquisitionRefusal("anchored recovery attempt cap is invalid")
    try:
        destination.parent.relative_to(root)
    except ValueError as exc:
        raise BNCIAcquisitionRefusal("anchored recovery destination escaped root") from exc
    if "/" in destination.name or destination.name in ("", ".", ".."):
        raise BNCIAcquisitionRefusal("anchored recovery destination is invalid")
    with _anchored_directory(root, destination.parent) as parent_fd:
        free_bytes = os.fstatvfs(parent_fd).f_bavail * os.fstatvfs(parent_fd).f_frsize
        if free_bytes < minimum_free_bytes:
            raise BNCIAcquisitionRefusal("anchored recovery free-disk floor is not satisfied")
        if _exists_at(parent_fd, destination.name):
            raise BNCIAcquisitionRefusal("anchored recovery destination already exists")
        work_name = f".{destination.name}.partial-{secrets.token_hex(8)}"
        os.mkdir(work_name, 0o700, dir_fd=parent_fd)
        request_count = 0
        network_bytes = 0
        manifest_rows: list[dict[str, Any]] = []
        published = False
        try:
            work_fd = os.open(work_name, _directory_open_flags(), dir_fd=parent_fd)
            try:
                os.mkdir("sourcedata", 0o700, dir_fd=work_fd)
                source_fd = os.open("sourcedata", _directory_open_flags(), dir_fd=work_fd)
                try:
                    for member in normalized:
                        final_name = Path(member.relative_path).name
                        partial_name = final_name + ".part"
                        completed = False
                        for attempt in range(1, attempts_per_file + 1):
                            if _exists_at(source_fd, final_name):
                                raise BNCIAcquisitionRefusal(
                                    "anchored completed member was requested twice"
                                )
                            offset = (
                                _regular_size_at(source_fd, partial_name)
                                if _exists_at(source_fd, partial_name)
                                else 0
                            )
                            if offset < 0 or offset >= member.bytes:
                                raise BNCIAcquisitionRefusal(
                                    "anchored partial payload offset is invalid"
                                )
                            request_count += 1
                            if request_count > request_cap:
                                raise BNCIAcquisitionRefusal(
                                    "anchored payload request cap exceeded"
                                )
                            response = transport(BASE_URL + member.relative_path, offset)
                            if not isinstance(response, TransportResponse):
                                raise BNCIAcquisitionRefusal(
                                    "anchored transport response type is invalid"
                                )
                            expected_status = 200 if offset == 0 else 206
                            if response.status != expected_status:
                                raise BNCIAcquisitionRefusal(
                                    "anchored transport status differs"
                                )
                            if offset and response.range_start != offset:
                                raise BNCIAcquisitionRefusal(
                                    "anchored transport range differs"
                                )
                            if not offset and response.range_start not in (None, 0):
                                raise BNCIAcquisitionRefusal(
                                    "anchored initial transport returned a range"
                                )
                            if response.content_length != member.bytes - offset:
                                raise BNCIAcquisitionRefusal(
                                    "anchored transport length differs"
                                )
                            flags = (
                                os.O_WRONLY
                                | getattr(os, "O_NOFOLLOW", 0)
                                | getattr(os, "O_CLOEXEC", 0)
                            )
                            flags |= os.O_APPEND if offset else os.O_CREAT | os.O_EXCL
                            payload_fd = os.open(
                                partial_name,
                                flags,
                                0o600,
                                dir_fd=source_fd,
                            )
                            try:
                                for chunk in response.body:
                                    if not isinstance(chunk, bytes) or not chunk:
                                        raise BNCIAcquisitionRefusal(
                                            "anchored transport yielded a malformed chunk"
                                        )
                                    network_bytes += len(chunk)
                                    if network_bytes > network_cap_bytes:
                                        raise BNCIAcquisitionRefusal(
                                            "anchored network-byte cap exceeded"
                                        )
                                    _write_all(payload_fd, chunk)
                            except (ConnectionError, TimeoutError):
                                if attempt == attempts_per_file:
                                    raise BNCIAcquisitionRefusal(
                                        "anchored transport attempts exhausted"
                                    )
                                continue
                            finally:
                                os.close(payload_fd)
                            observed_size, observed_hash = _hash_file_at(
                                source_fd,
                                partial_name,
                            )
                            if (
                                observed_size != member.bytes
                                or observed_hash != member.sha256
                            ):
                                raise BNCIAcquisitionRefusal(
                                    "anchored payload size or digest differs"
                                )
                            os.rename(
                                partial_name,
                                final_name,
                                src_dir_fd=source_fd,
                                dst_dir_fd=source_fd,
                            )
                            manifest_rows.append(
                                {
                                    "relative_path": member.relative_path,
                                    "bytes": observed_size,
                                    "sha256": observed_hash,
                                    "attempts": attempt,
                                }
                            )
                            completed = True
                            break
                        if not completed:
                            raise BNCIAcquisitionRefusal(
                                "anchored payload acquisition did not complete"
                            )
                finally:
                    os.close(source_fd)
                manifest = {
                    "schema_name": "neurodecodekit.bnci_2014_001_private_acquisition_manifest",
                    "schema_version": SCHEMA_VERSION,
                    "lane_id": LANE_ID,
                    "status": "complete_opaque_payload_bundle",
                    "members": manifest_rows,
                    "file_count": len(manifest_rows),
                    "payload_bytes": sum(row["bytes"] for row in manifest_rows),
                    "payload_requests": request_count,
                    "network_bytes": network_bytes,
                    "MAT_content_opens": 0,
                    "MAT_semantic_parses": 0,
                }
                manifest_payload = _canonical_bytes(manifest)
                manifest_fd = os.open(
                    "manifest.private.v0.json",
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
                    0o600,
                    dir_fd=work_fd,
                )
                try:
                    _write_all(manifest_fd, manifest_payload)
                    os.fsync(manifest_fd)
                finally:
                    os.close(manifest_fd)
            finally:
                os.close(work_fd)
            if _exists_at(parent_fd, destination.name):
                raise BNCIAcquisitionRefusal(
                    "anchored recovery destination appeared during execution"
                )
            os.rename(
                work_name,
                destination.name,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            published = True
            return manifest
        finally:
            if not published and _exists_at(parent_fd, work_name):
                _cleanup_work_directory(parent_fd, work_name)


def acquire_from_validated_manifest(
    root: Path,
    members: Sequence[PayloadMember],
    destination: str | Path,
    *,
    manifest_client: StandardLibraryManifestClient,
    payload_transport: Transport,
    network_cap_bytes: int = TOTAL_NETWORK_CAP_BYTES,
    disk_cap_bytes: int = DISK_CAP_BYTES,
    minimum_free_bytes: int = FREE_DISK_FLOOR_BYTES,
) -> tuple[bytes, dict[str, Any]]:
    """Fetch one manifest, validate it, then invoke the opaque downloader."""

    manifest_payload = manifest_client.fetch()
    if network_cap_bytes <= len(manifest_payload):
        raise BNCIAcquisitionRefusal("manifest exhausted the recovery network cap")
    signed_urls = validate_manifest_signed_urls(manifest_payload, members)
    private_manifest = acquire_members_anchored(
        root,
        members,
        destination,
        transport=SignedObjectTransportAdapter(
            signed_urls,
            transport=payload_transport,
        ),
        network_cap_bytes=network_cap_bytes - len(manifest_payload),
        disk_cap_bytes=disk_cap_bytes,
        minimum_free_bytes=minimum_free_bytes,
    )
    return manifest_payload, private_manifest


def _signed_url(member: PayloadMember, *, suffix: str = "") -> str:
    query = urllib.parse.urlencode(
        {
            "X-Amz-Algorithm": "AWS4-HMAC-SHA256",
            "X-Amz-Credential": "generated/20260824/us-east-2/s3/aws4_request",
            "X-Amz-Date": "20260824T000000Z",
            "X-Amz-Expires": "3600",
            "X-Amz-SignedHeaders": "host",
            "X-Amz-Signature": "1" * 64,
        }
    )
    return f"https://{SIGNED_OBJECT_HOST}{_expected_object_path(member)}?{query}{suffix}"


def _generated_manifest(members: Sequence[PayloadMember]) -> bytes:
    return _canonical_bytes(
        {
            "dataset": "generated-nm000139",
            "files": [
                {
                    "path": member.relative_path,
                    "bytes": member.bytes,
                    "sha256": member.sha256,
                    "signed_object_url": _signed_url(member),
                }
                for member in members
            ],
        }
    )


class _GeneratedHTTPResponse:
    def __init__(
        self,
        payload: bytes,
        *,
        url: str,
        status: int = 200,
        content_range: str | None = None,
        fail_after: int | None = None,
    ) -> None:
        self._payload = payload
        self._position = 0
        self._fail_after = fail_after
        self._url = url
        self._status = status
        self.headers = Message()
        self.headers.add_header("Content-Length", str(len(payload)))
        if content_range is not None:
            self.headers.add_header("Content-Range", content_range)

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self._status

    def read(self, size: int = -1) -> bytes:
        if self._fail_after is not None and self._position >= self._fail_after:
            raise OSError("generated interrupted stream")
        available_end = len(self._payload)
        if self._fail_after is not None:
            available_end = min(available_end, self._fail_after)
        if size < 0:
            end = available_end
        else:
            end = min(available_end, self._position + size)
        chunk = self._payload[self._position : end]
        self._position = end
        return chunk

    def close(self) -> None:
        return None


def run_generated_recovery_qualification() -> dict[str, Any]:
    """Run the one generated metadata/adapter qualification without real I/O."""

    if (_repo_root() / QUALIFICATION_RESULT_RELATIVE_PATH).exists():
        raise BNCIAcquisitionRefusal("generated recovery qualification is already closed")
    _freeze_threads(os.environ)
    started = time.perf_counter()
    members = registered_members()
    fixture = _generated_manifest(members)
    first = validate_manifest_signed_urls(fixture, members)
    second = validate_manifest_signed_urls(fixture, members)
    if first != second:
        raise BNCIAcquisitionRefusal("generated signed URL validation replay differs")
    adapter_calls: list[tuple[str, int]] = []

    def mock_transport(url: str, offset: int) -> TransportResponse:
        adapter_calls.append((url, offset))
        return TransportResponse(200, 1, None, (b"x",))

    adapter = SignedObjectTransportAdapter(first, transport=mock_transport)
    adapter(BASE_URL + members[0].relative_path, 0)
    adversarial = 0

    def expect_refusal(payload: bytes, changed_members: Sequence[PayloadMember] = members) -> None:
        nonlocal adversarial
        try:
            validate_manifest_signed_urls(payload, changed_members)
        except BNCIAcquisitionRefusal:
            adversarial += 1

    parsed = json.loads(fixture)
    mutations: list[dict[str, Any]] = []
    for field, value in (
        ("bytes", members[0].bytes + 1),
        ("sha256", "0" * 64),
        ("path", "sourcedata/A99E.mat"),
        ("signed_object_url", _signed_url(members[0]).replace(SIGNED_OBJECT_HOST, "example.invalid")),
        ("signed_object_url", _signed_url(members[0]).replace("https://", "http://")),
        ("signed_object_url", _signed_url(members[0]).replace("SHA256E-s", "SHA256E-s1")),
        ("signed_object_url", _signed_url(members[0]) + "&unexpected=1"),
    ):
        mutation = json.loads(json.dumps(parsed))
        mutation["files"][0][field] = value
        mutations.append(mutation)
    duplicate = json.loads(json.dumps(parsed))
    duplicate["files"].append(dict(duplicate["files"][0]))
    mutations.append(duplicate)
    ambiguous = json.loads(json.dumps(parsed))
    ambiguous["files"][0]["signed_url"] = ambiguous["files"][0]["signed_object_url"].replace(
        "1" * 64, "2" * 64
    )
    mutations.append(ambiguous)
    for mutation in mutations:
        expect_refusal(_canonical_bytes(mutation))
    for logical in (
        "https://example.invalid/sourcedata/A01E.mat",
        BASE_URL + "sourcedata/A99E.mat",
        BASE_URL + "../escape.mat",
    ):
        try:
            adapter(logical, 0)
        except BNCIAcquisitionRefusal:
            adversarial += 1
    if adversarial != 12 or len(adapter_calls) != 1:
        raise BNCIAcquisitionRefusal("generated recovery qualification accounting changed")

    generated_payloads = {
        "sourcedata/A01E.mat": b"generated-recovery-A01E",
        "sourcedata/A01T.mat": b"generated-recovery-A01T-longer",
        "sourcedata/A02E.mat": b"generated-recovery-A02E",
    }
    generated_members = tuple(
        PayloadMember(path, len(payload), _sha256(payload))
        for path, payload in sorted(generated_payloads.items())
    )
    generated_fixture = _generated_manifest(generated_members)
    manifest_requests = 0
    payload_requests: list[tuple[str, int]] = []
    interrupted = False

    def manifest_opener(request, _timeout):  # noqa: ANN001, ANN202
        nonlocal manifest_requests
        manifest_requests += 1
        return _GeneratedHTTPResponse(generated_fixture, url=request.full_url)

    url_to_member = {
        _signed_url(member): member for member in generated_members
    }

    def payload_opener(request, _timeout):  # noqa: ANN001, ANN202
        nonlocal interrupted
        member = url_to_member.get(request.full_url)
        if member is None:
            raise BNCIAcquisitionRefusal("generated payload URL is not registered")
        raw_range = request.headers.get("Range")
        offset = int(raw_range.removeprefix("bytes=").removesuffix("-")) if raw_range else 0
        payload_requests.append((member.relative_path, offset))
        payload = generated_payloads[member.relative_path][offset:]
        status = 206 if offset else 200
        content_range = (
            f"bytes {offset}-{member.bytes - 1}/{member.bytes}" if offset else None
        )
        fail_after = None
        if member.relative_path.endswith("A01T.mat") and offset == 0 and not interrupted:
            interrupted = True
            fail_after = len(payload) // 2
        return _GeneratedHTTPResponse(
            payload,
            url=request.full_url,
            status=status,
            content_range=content_range,
            fail_after=fail_after,
        )

    with tempfile.TemporaryDirectory(prefix="neurodecodekit-bnci-recovery-") as tmp:
        root = Path(tmp)
        monitor = ResourceMonitor(root)
        manifest_payload, private_manifest = acquire_from_validated_manifest(
            root,
            generated_members,
            root / "bundle",
            manifest_client=StandardLibraryManifestClient(
                opener=manifest_opener,
                monitor=monitor,
            ),
            payload_transport=ResourceBoundRangeTransport(
                monitor,
                opener=payload_opener,
            ),
            network_cap_bytes=4096,
            disk_cap_bytes=4096,
            minimum_free_bytes=0,
        )
        if manifest_payload != generated_fixture:
            raise BNCIAcquisitionRefusal("generated manifest client output changed")
        if private_manifest.get("file_count") != len(generated_members):
            raise BNCIAcquisitionRefusal("generated end-to-end file count changed")
        if private_manifest.get("payload_requests") != 4:
            raise BNCIAcquisitionRefusal("generated end-to-end resume count changed")
        if not any(offset > 0 for _path, offset in payload_requests):
            raise BNCIAcquisitionRefusal("generated end-to-end resume was not exercised")
        for member in generated_members:
            accepted = (root / "bundle" / member.relative_path).read_bytes()
            if accepted != generated_payloads[member.relative_path]:
                raise BNCIAcquisitionRefusal("generated end-to-end payload changed")
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_a_redirect_recovery_generated_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": f"{LANE_ID}-A-R",
        "status": "passed_generated_manifest_and_transport_qualification_only",
        "case_classes_passed": 18,
        "validated_exact_members": len(first),
        "validated_exact_member_bytes": sum(member.bytes for member in members),
        "deterministic_replays": 1,
        "generated_manifest_requests": manifest_requests,
        "generated_payload_requests": len(payload_requests),
        "generated_resume_requests": sum(offset > 0 for _path, offset in payload_requests),
        "generated_accepted_files": private_manifest["file_count"],
        "generated_accepted_bytes": private_manifest["payload_bytes"],
        "mock_adapter_calls": len(adapter_calls),
        "direct_refusals": adversarial,
        "generated_fixture_bytes": len(fixture) + len(generated_fixture),
        "temporary_generated_payload_bytes": sum(map(len, generated_payloads.values())),
        "retained_generated_payload_bytes": 0,
        "runtime_seconds": time.perf_counter() - started,
        "peak_process_RSS_bytes": _peak_rss_bytes(),
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "real_manifest_requests": 0,
        "real_payload_requests": 0,
        "real_payload_bytes": 0,
        "ignored_path_operations": 0,
        "MAT_semantic_content_opens": 0,
        "MAT_semantic_parses": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scores": 0,
        "scientific_claim_established": False,
        "qualification_may_be_repeated": False,
    }


def registered_recovery_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the green-decision-bound plan without ignored-path or network access."""

    read_green_recovery_decision(repo_root)
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_a_redirect_recovery_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": f"{LANE_ID}-A-R",
        "status": "plan_only_no_ignored_path_or_network_operation",
        "manifest_url": MANIFEST_URL,
        "payload_host_allowlist": [SIGNED_OBJECT_HOST],
        "payload_files": REGISTERED_FILES,
        "payload_bytes": REGISTERED_BYTES,
        "decision_commit": DECISION_COMMIT,
        "decision_CI_run_id": DECISION_CI_RUN_ID,
        "decision_base_job_id": DECISION_BASE_JOB_ID,
        "decision_optional_job_id": DECISION_OPTIONAL_JOB_ID,
        "next_operation": "commit_push_green_then_activate_before_live_recovery",
    }


def _stable_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    observed = -1
    for _ in range(8):
        payload = _canonical_bytes(receipt)
        if len(payload) == observed:
            return payload
        observed = len(payload)
        receipt["measurements"]["receipt_bytes"] = observed
    raise BNCIAcquisitionRefusal("recovery receipt byte count did not stabilize")


def execute_registered_recovery(
    repo_root: str | Path,
    *,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Run the one authorized manifest-bound signed-object recovery."""

    root = Path(repo_root).resolve()
    if root != _repo_root():
        raise BNCIAcquisitionRefusal("recovery repository root differs")
    _freeze_threads(environ)
    read_green_recovery_decision(root)
    read_green_implementation_activation(root)
    with _runtime_alarm(RUNTIME_CAP_SECONDS):
        return _execute_registered_recovery_after_green(root)


def _execute_registered_recovery_after_green(root: Path) -> dict[str, Any]:
    monitor = ResourceMonitor(root)
    original_marker = root / ORIGINAL_MARKER_RELATIVE_PATH
    original_payload = _read_regular_anchored(
        root,
        original_marker,
        ORIGINAL_MARKER_BYTES,
    )
    if len(original_payload) != ORIGINAL_MARKER_BYTES or _sha256(original_payload) != ORIGINAL_MARKER_SHA256:
        raise BNCIAcquisitionRefusal("original consumed marker identity changed")
    bundle = root / RECOVERY_BUNDLE_RELATIVE_PATH
    marker = root / RECOVERY_MARKER_RELATIVE_PATH
    receipt_path = root / RECOVERY_RECEIPT_RELATIVE_PATH
    _assert_safe_directory_ancestry(root, marker.parent, create=False)
    for protected in (bundle, marker, receipt_path):
        if protected.exists() or protected.is_symlink():
            raise BNCIAcquisitionRefusal("redirect recovery is already consumed or has output")
    free_before = shutil.disk_usage(root).free
    if free_before < FREE_DISK_FLOOR_BYTES:
        raise BNCIAcquisitionRefusal("redirect recovery free-disk floor is not satisfied")
    marker_payload = _canonical_bytes(
        {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_a_redirect_recovery_consumed_marker",
            "schema_version": SCHEMA_VERSION,
            "lane_id": f"{LANE_ID}-A-R",
            "status": "consumed_before_manifest_network_client_construction",
            "decision_commit": DECISION_COMMIT,
            "decision_CI_run_id": DECISION_CI_RUN_ID,
            "original_consumed_marker_sha256": ORIGINAL_MARKER_SHA256,
            "rerun_allowed": False,
        }
    )
    _exclusive_write(marker, marker_payload)
    members = registered_members()
    monitor.check()
    manifest_payload, private_manifest = acquire_from_validated_manifest(
        root,
        members,
        bundle,
        manifest_client=StandardLibraryManifestClient(monitor=monitor),
        payload_transport=ResourceBoundRangeTransport(monitor),
    )
    monitor.check()
    runtime_seconds = time.perf_counter() - monitor.started
    peak_rss_bytes = _peak_rss_bytes()
    if runtime_seconds > RUNTIME_CAP_SECONDS:
        raise BNCIAcquisitionRefusal("redirect recovery runtime cap exceeded")
    if peak_rss_bytes > PEAK_RSS_CAP_BYTES:
        raise BNCIAcquisitionRefusal("redirect recovery peak RSS cap exceeded")
    if (
        private_manifest.get("file_count") != REGISTERED_FILES
        or private_manifest.get("payload_bytes") != REGISTERED_BYTES
        or private_manifest.get("network_bytes", 0) + len(manifest_payload)
        > TOTAL_NETWORK_CAP_BYTES
    ):
        raise BNCIAcquisitionRefusal("redirect recovery aggregate differs")
    original_after = _read_regular_anchored(
        root,
        original_marker,
        ORIGINAL_MARKER_BYTES,
    )
    if original_after != original_payload:
        raise BNCIAcquisitionRefusal("original consumed marker changed during recovery")
    bundle_manifest_path = bundle / "manifest.private.v0.json"
    bundle_manifest_bytes = len(
        _read_regular_anchored(root, bundle_manifest_path, PUBLIC_OUTPUT_CAP_BYTES)
    )
    free_after = shutil.disk_usage(root).free
    receipt: dict[str, Any] = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_a_redirect_recovery_receipt",
        "schema_version": SCHEMA_VERSION,
        "lane_id": f"{LANE_ID}-A-R",
        "status": "complete_opaque_exact_payload_bundle_from_validated_signed_objects",
        "proof_barrier": {
            "decision_commit": DECISION_COMMIT,
            "decision_CI_run_id": DECISION_CI_RUN_ID,
            "decision_base_job_id": DECISION_BASE_JOB_ID,
            "decision_optional_job_id": DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "measurements": {
            "manifest_input_bytes": len(manifest_payload),
            "payload_network_bytes": private_manifest["network_bytes"],
            "total_network_bytes": len(manifest_payload) + private_manifest["network_bytes"],
            "accepted_payload_bytes": private_manifest["payload_bytes"],
            "bundle_manifest_bytes": bundle_manifest_bytes,
            "incremental_output_bytes_excluding_marker_and_receipt": (
                private_manifest["payload_bytes"] + bundle_manifest_bytes
            ),
            "recovery_marker_bytes": len(marker_payload),
            "receipt_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_process_RSS_bytes": peak_rss_bytes,
            "free_disk_bytes_before": free_before,
            "free_disk_bytes_after": free_after,
        },
        "operations": {
            "manifest_GETs": 1,
            "payload_files": private_manifest["file_count"],
            "payload_requests": private_manifest["payload_requests"],
            "opaque_post_write_hash_opens": private_manifest["file_count"],
            "original_marker_identity_reads": 2,
            "MAT_semantic_content_opens": 0,
            "MAT_semantic_parses": 0,
            "signal_event_target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "scores": 0,
        },
        "resources": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "payload_files_exact": REGISTERED_FILES,
            "payload_bytes_exact": REGISTERED_BYTES,
            "payload_requests_maximum": REQUEST_CAP,
            "attempts_per_file_maximum": ATTEMPT_CAP_PER_FILE,
            "network_bytes_maximum": TOTAL_NETWORK_CAP_BYTES,
            "incremental_disk_bytes_maximum": DISK_CAP_BYTES,
            "free_disk_bytes_minimum": FREE_DISK_FLOOR_BYTES,
            "runtime_seconds_maximum": RUNTIME_CAP_SECONDS,
            "peak_RSS_bytes_maximum": PEAK_RSS_CAP_BYTES,
        },
        "original_consumed_marker": {
            "bytes": ORIGINAL_MARKER_BYTES,
            "sha256_before": ORIGINAL_MARKER_SHA256,
            "sha256_after": _sha256(original_after),
            "byte_identical": True,
        },
        "warnings": [
            "payload_is_private_and_Git_ignored",
            "signed_URL_credentials_were_not_retained",
            "payload_bytes_were_hashed_but_not_semantically_interpreted",
            "recovery_is_consumed_and_cannot_be_rerun",
            "no_scientific_or_decoding_claim_is_established",
        ],
        "next_gate": "commit_push_and_green_aggregate_recovery_result_before_Stage_Q",
        "claim_boundary": {
            "engineering_capability": "exact_private_BNCI_payload_bundle_acquired_via_validated_signed_objects",
            "scientific_claim_established": False,
            "unseen_person_generalization": False,
            "EEG_beyond_EOG": False,
            "decoding_performance": False,
        },
    }
    receipt_bytes = _stable_receipt_bytes(receipt)
    if len(receipt_bytes) > PUBLIC_OUTPUT_CAP_BYTES:
        raise BNCIAcquisitionRefusal("redirect recovery receipt exceeds output cap")
    _exclusive_write(receipt_path, receipt_bytes)
    return receipt
