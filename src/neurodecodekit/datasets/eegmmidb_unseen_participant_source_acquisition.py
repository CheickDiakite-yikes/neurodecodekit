"""Proof-gated opaque source acquisition for EEGMMIDB-UG1 Stage S-A.

The public surface in this module is generated/mock only.  The live transport
exists for the later Stage S-A2 wrapper, but it cannot be reached without an
exact, remotely green Stage S-A1 proof record and is intentionally absent from
the sidecar CLI.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import json
import os
import re
import resource
import shutil
import ssl
import stat
import sys
import time
import urllib.request
from dataclasses import dataclass
from email.message import Message
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Callable, Mapping, Sequence
from urllib.parse import urlsplit


SCHEMA_VERSION = "0.1.0"
LANE_ID = "EEGMMIDB-UG1-SA"
GENERATED_ROUTE = "EEGMMIDBUG1SA1-G1"
DECISION_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_source_acquisition_authorization_decision.v0.json"
)
REQUEST_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_source_acquisition_authorization_request.v0.json"
)
INVENTORY_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_metadata_inventory.v0.json"
)
DECISION_SHA256 = "2e8dabf57162bd9c93392ccf406d23789915977749788dc2e007e736834bec7c"
REQUEST_SHA256 = "791710dfff61bc6bd752d1d17ad5fafcc19e07db96b9f04705990dfddc6022f3"
INVENTORY_SHA256 = "1b8f16f846a1bb3e0dccdbf71ea39f375872ad732bdffeecd100dbfc161a7dac"
GREEN_DECISION_COMMIT = "1b5c9195f384e5867f18131aa7d669f7c9cd0e2b"
GREEN_DECISION_CI_RUN_ID = 32_725_633_524
GREEN_DECISION_BASE_JOB_ID = 97_426_157_639
GREEN_DECISION_OPTIONAL_JOB_ID = 97_426_157_381
CHECKSUM_URL = "https://physionet.org/files/eegmmidb/1.0.0/SHA256SUMS.txt"
FILE_ROOT_URL = "https://physionet.org/files/eegmmidb/1.0.0/"
REQUEST_TIMEOUT_SECONDS = 30.0
CHUNK_BYTES = 1_048_576
MAX_CHECKSUM_BYTES = 1_048_576
EXACT_PAYLOAD_BYTES = 15_498_816
MAX_PAYLOAD_NETWORK_BYTES = 16_777_216
MAX_HEADER_BYTES = 262_144
MAX_INCREMENTAL_DISK_BYTES = 67_108_864
MAX_METADATA_BYTES = 1_048_576
MAX_WALL_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 268_435_456
MINIMUM_FREE_DISK_BYTES = 2_147_483_648
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")
CHECKSUM_LINE_RE = re.compile(r"([0-9a-f]{64})  ([A-Za-z0-9][A-Za-z0-9._/-]*)\Z")
GENERATED_SENTINEL = b"NEURODECODEKIT-UG1-SA1-GENERATED-NOT-EDF\x00"
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "checksum",
        "etag",
        "file",
        "identity",
        "label",
        "last_modified",
        "participant",
        "path",
        "prediction",
        "run",
        "target",
        "url",
    }
)
QUALIFICATION_CASES = (
    "complete_bundle",
    "deterministic_replay",
    "checksum_missing",
    "checksum_duplicate",
    "checksum_uppercase",
    "checksum_alias",
    "checksum_malformed",
    "request_order",
    "missing_response",
    "redirect",
    "status",
    "content_length",
    "etag",
    "last_modified",
    "accept_ranges",
    "content_encoding",
    "content_range",
    "short_body",
    "oversized_body",
    "nonbytes_body",
    "output_collision",
    "second_invocation",
    "thread_environment",
    "free_disk",
    "peak_rss",
    "wall_time",
    "fresh_final_refusal",
)


class UG1SourceAcquisitionRefusal(RuntimeError):
    """Refuse before or during a bounded source-acquisition invocation."""


@dataclass(frozen=True)
class SourceFileSpec:
    repository_path: str
    url: str
    participant: str
    run: str
    partition: str
    size_bytes: int
    etag: str
    last_modified: str
    accept_ranges: str


@dataclass(frozen=True)
class SourceAcquisitionCaps:
    checksum_bytes: int = MAX_CHECKSUM_BYTES
    payload_network_bytes: int = MAX_PAYLOAD_NETWORK_BYTES
    header_bytes: int = MAX_HEADER_BYTES
    incremental_disk_bytes: int = MAX_INCREMENTAL_DISK_BYTES
    metadata_bytes: int = MAX_METADATA_BYTES
    chunk_bytes: int = CHUNK_BYTES
    wall_seconds: float = MAX_WALL_SECONDS
    peak_rss_bytes: int = MAX_PEAK_RSS_BYTES
    minimum_free_disk_bytes: int = MINIMUM_FREE_DISK_BYTES


@dataclass(frozen=True)
class OutputLayout:
    payload_relative: str
    temporary_relative: str
    marker_relative: str


@dataclass(frozen=True)
class SourceAcquisitionOutcome:
    manifest: Mapping[str, Any]
    manifest_bytes: bytes
    receipt: Mapping[str, Any]
    receipt_bytes: bytes
    payload_root: Path
    marker_path: Path
    measurements: Mapping[str, Any]


@dataclass(frozen=True)
class SA1ProofEvidence:
    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    proof_closeout_commit: str
    proof_closeout_ci_run_id: int
    proof_closeout_base_job_id: int
    proof_closeout_optional_job_id: int
    proof_closeout_registry_sha256: str


@dataclass(frozen=True)
class FixtureExchange:
    url: str
    response: "FixtureGetResponse"
    expected_headers: Mapping[str, str]


class FixtureGetResponse:
    """urllib-shaped streaming response used only by generated qualification."""

    def __init__(
        self,
        *,
        url: str,
        headers: Sequence[tuple[str, str]],
        payload: bytes | None = None,
        spec: SourceFileSpec | None = None,
        spec_index: int = 0,
        body_size: int | None = None,
        status: int = 200,
        nonbytes: bool = False,
    ) -> None:
        self.status = status
        self.code = status
        self._url = url
        self.headers = Message()
        for key, value in headers:
            self.headers.add_header(key, value)
        self._payload = payload
        self._spec = spec
        self._spec_index = spec_index
        self._body_size = (
            len(payload)
            if payload is not None
            else body_size if body_size is not None else spec.size_bytes if spec is not None else 0
        )
        self._position = 0
        self._nonbytes = nonbytes
        self.closed = False
        self.read_calls = 0
        self.maximum_requested_read = 0

    def __enter__(self) -> "FixtureGetResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def close(self) -> None:
        self.closed = True

    def read(self, size: int = -1) -> bytes:
        self.read_calls += 1
        self.maximum_requested_read = max(self.maximum_requested_read, size)
        if self._nonbytes and self._position == 0:
            self._position = self._body_size
            return "not-bytes"  # type: ignore[return-value]
        if size < 0:
            size = self._body_size - self._position
        count = min(size, self._body_size - self._position)
        if count <= 0:
            return b""
        if self._payload is not None:
            result = self._payload[self._position : self._position + count]
        elif self._spec is not None:
            result = _generated_payload_slice(
                self._spec,
                self._spec_index,
                self._position,
                count,
            )
        else:
            result = b""
        self._position += len(result)
        return result


class FixtureGetOpener:
    """Strict sequential injected opener with no network capability."""

    def __init__(self, exchanges: Sequence[FixtureExchange]) -> None:
        self._exchanges = list(exchanges)
        self.calls: list[dict[str, Any]] = []

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        if not self._exchanges:
            raise UG1SourceAcquisitionRefusal("unexpected source-acquisition request")
        expected = self._exchanges.pop(0)
        observed_headers = {key.lower(): value for key, value in request.header_items()}
        observed = {
            "url": request.full_url,
            "method": request.get_method(),
            "timeout": timeout,
            "data": request.data,
            "headers": observed_headers,
        }
        self.calls.append(observed)
        if request.full_url != expected.url:
            raise UG1SourceAcquisitionRefusal("request order or URL differs")
        if (
            observed["method"] != "GET"
            or observed["timeout"] != REQUEST_TIMEOUT_SECONDS
            or observed["data"] is not None
            or observed_headers != dict(expected.expected_headers)
        ):
            raise UG1SourceAcquisitionRefusal("request semantics differ")
        return expected.response

    def assert_consumed(self) -> None:
        if self._exchanges:
            raise UG1SourceAcquisitionRefusal("response sequence is incomplete")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


class StandardLibraryGetOpener:
    """TLS-verified, proxy-free, no-redirect transport for later Stage S-A2."""

    def __init__(self) -> None:
        context = ssl.create_default_context()
        self._opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            _NoRedirect(),
            urllib.request.HTTPSHandler(context=context),
        )

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        return self._opener.open(request, timeout=timeout)


GetOpener = Callable[[urllib.request.Request, float], BinaryIO]


def _canonical_json(value: Any) -> bytes:
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


def _peak_process_tree_rss_bytes() -> int:
    own = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    children = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
    multiplier = 1 if sys.platform == "darwin" else 1024
    return (own + children) * multiplier


def _read_regular_nofollow(path: Path, maximum_bytes: int) -> bytes:
    if not hasattr(os, "O_NOFOLLOW"):
        raise UG1SourceAcquisitionRefusal("O_NOFOLLOW is unavailable")
    try:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise OSError("unsafe locked file")
        if before.st_size > maximum_bytes:
            raise OSError("locked file exceeds cap")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as handle:
            observed = os.fstat(handle.fileno())
            if (
                not stat.S_ISREG(observed.st_mode)
                or observed.st_nlink != 1
                or (observed.st_dev, observed.st_ino) != (before.st_dev, before.st_ino)
            ):
                raise OSError("locked file identity changed")
            payload = handle.read(maximum_bytes + 1)
    except OSError as exc:
        raise UG1SourceAcquisitionRefusal(f"locked artifact is unavailable: {path.name}") from exc
    if len(payload) != before.st_size or len(payload) > maximum_bytes:
        raise UG1SourceAcquisitionRefusal(f"locked artifact size differs: {path.name}")
    return payload


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = _read_regular_nofollow(path, MAX_METADATA_BYTES)
    if _sha256(payload) != expected_sha256:
        raise UG1SourceAcquisitionRefusal(f"locked artifact hash differs: {path.name}")
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UG1SourceAcquisitionRefusal(f"locked artifact JSON differs: {path.name}") from exc
    if not isinstance(value, dict):
        raise UG1SourceAcquisitionRefusal(f"locked artifact must be an object: {path.name}")
    return value


def _load_locked_scope(repo_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    decision = _load_locked_json(repo_root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    request = _load_locked_json(repo_root / REQUEST_RELATIVE_PATH, REQUEST_SHA256)
    inventory = _load_locked_json(repo_root / INVENTORY_RELATIVE_PATH, INVENTORY_SHA256)
    authorization = decision.get("authorization", {})
    if (
        decision.get("lane_id") != LANE_ID
        or decision.get("green_request", {}).get("both_required_jobs_green") is not True
        or decision.get("green_proof_closeout", {}).get("both_required_jobs_green") is not True
        or authorization.get(
            "stage_SA1_generated_source_acquisition_implementation_after_decision_green"
        )
        is not True
        or authorization.get("network_or_remote_request_authorized_now") is not False
        or authorization.get("payload_download_or_acquisition_authorized_now") is not False
    ):
        raise UG1SourceAcquisitionRefusal("green Stage S-A decision scope differs")
    if request.get("request_id") != LANE_ID or request.get("status") != "all_authority_false_request_only":
        raise UG1SourceAcquisitionRefusal("source-acquisition request scope differs")
    if inventory.get("lane_id") != "EEGMMIDB-UG1-M":
        raise UG1SourceAcquisitionRefusal("Stage M inventory scope differs")
    return decision, request, inventory


def _source_specs(repo_root: Path) -> tuple[SourceFileSpec, ...]:
    _decision, request, inventory = _load_locked_scope(repo_root)
    rows = request.get("source_boundary", {}).get("exact_files_in_request_order")
    if not isinstance(rows, list) or len(rows) != 6:
        raise UG1SourceAcquisitionRefusal("source allowlist must contain exactly six rows")
    specs: list[SourceFileSpec] = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "repository_path",
            "url",
            "participant",
            "run",
            "partition",
            "size_bytes",
            "etag",
            "last_modified",
            "accept_ranges",
        }:
            raise UG1SourceAcquisitionRefusal("source allowlist row schema differs")
        specs.append(SourceFileSpec(**row))
    inventory_rows = inventory.get("files")
    if not isinstance(inventory_rows, list):
        raise UG1SourceAcquisitionRefusal("Stage M inventory rows differ")
    by_path = {row.get("repository_path"): row for row in inventory_rows if isinstance(row, dict)}
    for spec in specs:
        if by_path.get(spec.repository_path) != {
            "repository_path": spec.repository_path,
            "partition": spec.partition,
            "participant": spec.participant,
            "run": spec.run,
            "url": spec.url,
            "size_bytes": spec.size_bytes,
            "etag": spec.etag,
            "last_modified": spec.last_modified,
            "accept_ranges": spec.accept_ranges,
        }:
            raise UG1SourceAcquisitionRefusal("source allowlist differs from Stage M inventory")
    if sum(row.size_bytes for row in specs) != EXACT_PAYLOAD_BYTES:
        raise UG1SourceAcquisitionRefusal("source allowlist payload total differs")
    return tuple(specs)


def registered_source_acquisition_plan(repo_root: str | Path) -> dict[str, Any]:
    """Return the exact Stage S-A plan without network or local payload access."""

    specs = _source_specs(Path(repo_root))
    return {
        "schema_name": "neurodecodekit.eegmmidb_ug1_source_acquisition_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "mode": "dry_run_no_network_no_payload_path_no_EDF_read",
        "file_count": len(specs),
        "payload_bytes_exact": sum(row.size_bytes for row in specs),
        "requests_if_later_proof_authorized": 7,
        "stream_chunk_bytes_maximum": CHUNK_BYTES,
        "operation_counters": _zero_operation_counters(),
        "warnings": [
            "plan_only",
            "generated_qualification_is_not_real_EEG_access",
            "live_execution_has_no_CLI_command",
            "stage_SA2_requires_exact_remote_green_SA1_result_and_proof",
            "no_scientific_or_decoding_claim",
        ],
    }


def _zero_operation_counters() -> dict[str, int]:
    return {
        "mock_checksum_requests": 0,
        "mock_EDF_requests": 0,
        "real_checksum_requests": 0,
        "real_EDF_requests": 0,
        "redirects": 0,
        "retries": 0,
        "EDF_semantic_reads": 0,
        "target_or_label_reads": 0,
        "parameter_update_fits": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "scoring_events": 0,
        "scientific_claim_upgrades": 0,
    }


def _validate_url(url: str, *, checksum: bool = False) -> None:
    parsed = urlsplit(url)
    expected_path = "/files/eegmmidb/1.0.0/SHA256SUMS.txt" if checksum else None
    if (
        parsed.scheme != "https"
        or parsed.hostname != "physionet.org"
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or (checksum and parsed.path != expected_path)
        or (not checksum and not parsed.path.startswith("/files/eegmmidb/1.0.0/"))
    ):
        raise UG1SourceAcquisitionRefusal("URL differs from the frozen HTTPS allowlist")


def _checksum_request() -> urllib.request.Request:
    _validate_url(CHECKSUM_URL, checksum=True)
    return urllib.request.Request(
        CHECKSUM_URL,
        method="GET",
        headers={
            "Accept": "text/plain",
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-EEGMMIDBUG1SA/0.1",
        },
    )


def _payload_request(spec: SourceFileSpec) -> urllib.request.Request:
    _validate_url(spec.url)
    if spec.url != f"{FILE_ROOT_URL}{spec.repository_path}":
        raise UG1SourceAcquisitionRefusal("payload URL and repository path differ")
    return urllib.request.Request(
        spec.url,
        method="GET",
        headers={
            "Accept": "application/octet-stream",
            "Accept-Encoding": "identity",
            "If-Match": spec.etag,
            "If-Unmodified-Since": spec.last_modified,
            "User-Agent": "NeuroDecodeKit-EEGMMIDBUG1SA/0.1",
        },
    )


def _single_header(headers: Message, name: str, *, required: bool) -> str | None:
    values = headers.get_all(name, failobj=[])
    if len(values) > 1 or (required and len(values) != 1):
        raise UG1SourceAcquisitionRefusal(f"{name} header count differs")
    if not values:
        return None
    value = values[0]
    if not isinstance(value, str) or value != value.strip() or "\r" in value or "\n" in value:
        raise UG1SourceAcquisitionRefusal(f"{name} header syntax differs")
    return value


def _header_bytes(headers: Message) -> int:
    total = 0
    for key, value in headers.raw_items():
        try:
            total += len(key.encode("ascii")) + len(value.encode("ascii")) + 4
        except UnicodeEncodeError as exc:
            raise UG1SourceAcquisitionRefusal("response headers must be ASCII") from exc
    return total


def _validate_response_identity(
    response: BinaryIO,
    *,
    requested_url: str,
    expected_size: int | None,
    expected_spec: SourceFileSpec | None,
    caps: SourceAcquisitionCaps,
) -> tuple[int, int]:
    status_code = getattr(response, "status", getattr(response, "code", None))
    final_url = response.geturl()  # type: ignore[attr-defined]
    headers = response.headers  # type: ignore[attr-defined]
    if status_code != 200 or final_url != requested_url:
        raise UG1SourceAcquisitionRefusal("response status or final URL differs")
    if not isinstance(headers, Message):
        raise UG1SourceAcquisitionRefusal("response headers adapter differs")
    observed_header_bytes = _header_bytes(headers)
    if observed_header_bytes > caps.header_bytes:
        raise UG1SourceAcquisitionRefusal("response header bytes exceed cap")
    content_length = _single_header(headers, "Content-Length", required=True)
    if content_length is None or DECIMAL_RE.fullmatch(content_length) is None:
        raise UG1SourceAcquisitionRefusal("Content-Length must be one canonical decimal")
    size = int(content_length)
    if expected_size is not None and size != expected_size:
        raise UG1SourceAcquisitionRefusal("Content-Length differs from frozen size")
    if _single_header(headers, "Content-Encoding", required=False) is not None:
        raise UG1SourceAcquisitionRefusal("Content-Encoding is forbidden")
    if _single_header(headers, "Content-Range", required=False) is not None:
        raise UG1SourceAcquisitionRefusal("Content-Range is forbidden")
    if _single_header(headers, "Transfer-Encoding", required=False) is not None:
        raise UG1SourceAcquisitionRefusal("Transfer-Encoding is forbidden")
    if expected_spec is not None:
        expected_headers = {
            "ETag": expected_spec.etag,
            "Last-Modified": expected_spec.last_modified,
            "Accept-Ranges": expected_spec.accept_ranges,
        }
        for name, expected in expected_headers.items():
            if _single_header(headers, name, required=True) != expected:
                raise UG1SourceAcquisitionRefusal(f"{name} differs from frozen value")
    return size, observed_header_bytes


def _read_bounded_body(response: BinaryIO, maximum_bytes: int, chunk_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(min(chunk_bytes, maximum_bytes - total + 1))
        if not isinstance(chunk, bytes):
            raise UG1SourceAcquisitionRefusal("response body read returned non-bytes")
        if len(chunk) > chunk_bytes:
            raise UG1SourceAcquisitionRefusal("response body chunk exceeds cap")
        if not chunk:
            break
        total += len(chunk)
        if total > maximum_bytes:
            raise UG1SourceAcquisitionRefusal("response body exceeds cap")
        chunks.append(chunk)
    return b"".join(chunks)


def parse_checksum_manifest(payload: bytes, specs: Sequence[SourceFileSpec]) -> dict[str, str]:
    """Strictly freeze one lowercase SHA-256 for each exact allowlisted path."""

    try:
        text = payload.decode("ascii")
    except UnicodeDecodeError as exc:
        raise UG1SourceAcquisitionRefusal("checksum manifest must be ASCII") from exc
    if "\x00" in text or not text.endswith("\n") or "\r" in text:
        raise UG1SourceAcquisitionRefusal("checksum manifest framing differs")
    allowlist = tuple(spec.repository_path for spec in specs)
    allowed = set(allowlist)
    frozen: dict[str, str] = {}
    for line in text.splitlines():
        match = CHECKSUM_LINE_RE.fullmatch(line)
        if match is None:
            raise UG1SourceAcquisitionRefusal("checksum manifest line syntax differs")
        digest, repository_path = match.groups()
        path = PurePosixPath(repository_path)
        if (
            path.is_absolute()
            or repository_path.startswith("./")
            or "\\" in repository_path
            or "%" in repository_path
            or any(part in {"", ".", ".."} for part in path.parts)
        ):
            raise UG1SourceAcquisitionRefusal("checksum manifest path alias is forbidden")
        if repository_path in allowed:
            if repository_path in frozen:
                raise UG1SourceAcquisitionRefusal("duplicate checksum manifest entry")
            frozen[repository_path] = digest
    if tuple(path for path in allowlist if path in frozen) != allowlist or len(frozen) != 6:
        raise UG1SourceAcquisitionRefusal("checksum manifest allowlist is incomplete")
    return {path: frozen[path] for path in allowlist}


def _generated_payload_slice(
    spec: SourceFileSpec,
    index: int,
    offset: int,
    count: int,
) -> bytes:
    prefix = GENERATED_SENTINEL + f"{index}|{spec.repository_path}|".encode("ascii")
    block = hashlib.sha256(prefix).digest()
    end = offset + count
    result = bytearray()
    if offset < len(prefix):
        prefix_end = min(end, len(prefix))
        result.extend(prefix[offset:prefix_end])
        offset = prefix_end
    if offset < end:
        block_offset = (offset - len(prefix)) % len(block)
        remaining = end - offset
        if block_offset:
            take = min(remaining, len(block) - block_offset)
            result.extend(block[block_offset : block_offset + take])
            remaining -= take
        if remaining:
            repeats, tail = divmod(remaining, len(block))
            result.extend(block * repeats)
            result.extend(block[:tail])
    return bytes(result)


def _generated_digest(spec: SourceFileSpec, index: int, body_size: int | None = None) -> str:
    size = spec.size_bytes if body_size is None else body_size
    digest = hashlib.sha256()
    offset = 0
    while offset < size:
        count = min(CHUNK_BYTES, size - offset)
        digest.update(_generated_payload_slice(spec, index, offset, count))
        offset += count
    return digest.hexdigest()


def _checksum_headers(size: int) -> tuple[tuple[str, str], ...]:
    return (("Content-Length", str(size)), ("Content-Type", "text/plain"))


def _payload_headers(spec: SourceFileSpec) -> tuple[tuple[str, str], ...]:
    return (
        ("Content-Length", str(spec.size_bytes)),
        ("ETag", spec.etag),
        ("Last-Modified", spec.last_modified),
        ("Accept-Ranges", spec.accept_ranges),
    )


def _request_headers(request: urllib.request.Request) -> dict[str, str]:
    return {key.lower(): value for key, value in request.header_items()}


def build_generated_exchanges(
    repo_root: str | Path,
) -> tuple[FixtureExchange, ...]:
    """Build seven deterministic streaming mock exchanges at exact real sizes."""

    specs = _source_specs(Path(repo_root))
    digests = [_generated_digest(spec, index) for index, spec in enumerate(specs)]
    checksum_payload = "".join(
        f"{digest}  {spec.repository_path}\n" for spec, digest in zip(specs, digests, strict=True)
    ).encode("ascii")
    checksum_request = _checksum_request()
    exchanges = [
        FixtureExchange(
            url=CHECKSUM_URL,
            response=FixtureGetResponse(
                url=CHECKSUM_URL,
                headers=_checksum_headers(len(checksum_payload)),
                payload=checksum_payload,
            ),
            expected_headers=_request_headers(checksum_request),
        )
    ]
    for index, spec in enumerate(specs):
        request = _payload_request(spec)
        exchanges.append(
            FixtureExchange(
                url=spec.url,
                response=FixtureGetResponse(
                    url=spec.url,
                    headers=_payload_headers(spec),
                    spec=spec,
                    spec_index=index,
                ),
                expected_headers=_request_headers(request),
            )
        )
    return tuple(exchanges)


def _assert_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise UG1SourceAcquisitionRefusal("one-thread environment is not exact")


def _safe_relative(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise UG1SourceAcquisitionRefusal("unsafe output path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise UG1SourceAcquisitionRefusal("unsafe output path")
    return path


def _workspace_root(path: str | Path) -> Path:
    root = Path(os.path.abspath(os.fspath(path)))
    try:
        observed = os.lstat(root)
    except OSError as exc:
        raise UG1SourceAcquisitionRefusal("workspace root is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise UG1SourceAcquisitionRefusal("workspace root must be a non-symlink directory")
    return root


def _assert_chain_safe(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise UG1SourceAcquisitionRefusal("output path escapes workspace") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(observed.st_mode):
            raise UG1SourceAcquisitionRefusal("output path crosses a symlink")
        if current != path and not stat.S_ISDIR(observed.st_mode):
            raise UG1SourceAcquisitionRefusal("output parent is not a directory")


def _mkdir_chain(root: Path, parent: Path, tracked_dirs: dict[Path, tuple[int, int]]) -> None:
    relative = parent.relative_to(root)
    current = root
    for part in relative.parts:
        current /= part
        try:
            os.mkdir(current, 0o700)
        except FileExistsError:
            observed = os.lstat(current)
            if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
                raise UG1SourceAcquisitionRefusal("output parent is unsafe")
        else:
            observed = os.lstat(current)
            tracked_dirs[current] = (observed.st_dev, observed.st_ino)


def _fsync_directory(path: Path) -> None:
    if not hasattr(os, "O_DIRECTORY"):
        raise UG1SourceAcquisitionRefusal("O_DIRECTORY is unavailable")
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _write_exclusive_synced(path: Path, payload: bytes) -> tuple[int, int]:
    if not hasattr(os, "O_NOFOLLOW"):
        raise UG1SourceAcquisitionRefusal("O_NOFOLLOW is unavailable")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            written = handle.write(payload)
            if written != len(payload):
                raise UG1SourceAcquisitionRefusal("short exclusive metadata write")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise
    observed = os.lstat(path)
    if not stat.S_ISREG(observed.st_mode) or observed.st_nlink != 1:
        raise UG1SourceAcquisitionRefusal("exclusive metadata output is unsafe")
    _fsync_directory(path.parent)
    return observed.st_dev, observed.st_ino


def _rename_noreplace(source: Path, destination: Path) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform == "darwin":
        rename = getattr(libc, "renamex_np", None)
        if rename is None:
            raise UG1SourceAcquisitionRefusal("atomic no-replace rename is unavailable")
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        result = rename(os.fsencode(source), os.fsencode(destination), 0x00000004)
    elif sys.platform.startswith("linux"):
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise UG1SourceAcquisitionRefusal("atomic no-replace rename is unavailable")
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        rename.restype = ctypes.c_int
        result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    else:
        raise UG1SourceAcquisitionRefusal("atomic no-replace rename is unsupported")
    if result == 0:
        _fsync_directory(destination.parent)
        return
    error = ctypes.get_errno()
    if error == errno.EEXIST:
        raise UG1SourceAcquisitionRefusal("destination appeared before promotion")
    raise OSError(error, os.strerror(error), destination)


def _hash_regular_nofollow(path: Path) -> tuple[int, str]:
    if not hasattr(os, "O_NOFOLLOW"):
        raise UG1SourceAcquisitionRefusal("O_NOFOLLOW is unavailable")
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise UG1SourceAcquisitionRefusal("payload is not a single-link regular file")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    digest = hashlib.sha256()
    total = 0
    with os.fdopen(descriptor, "rb") as handle:
        observed = os.fstat(handle.fileno())
        if (
            not stat.S_ISREG(observed.st_mode)
            or observed.st_nlink != 1
            or (observed.st_dev, observed.st_ino) != (before.st_dev, before.st_ino)
        ):
            raise UG1SourceAcquisitionRefusal("payload identity changed before hash pass")
        while True:
            chunk = handle.read(CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def _file_disk_bytes(path: Path) -> int:
    observed = os.lstat(path)
    return max(observed.st_size, getattr(observed, "st_blocks", 0) * 512)


def _check_resources(
    *,
    started: float,
    root: Path,
    caps: SourceAcquisitionCaps,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_usage_reader: Callable[[Path], Any],
) -> tuple[float, int]:
    runtime = clock() - started
    peak_rss = int(rss_reader())
    if runtime < 0 or runtime > caps.wall_seconds:
        raise UG1SourceAcquisitionRefusal("wall-time cap exceeded")
    if peak_rss < 0 or peak_rss > caps.peak_rss_bytes:
        raise UG1SourceAcquisitionRefusal("peak RSS cap exceeded")
    if int(disk_usage_reader(root).free) < caps.minimum_free_disk_bytes:
        raise UG1SourceAcquisitionRefusal("free-disk requirement is not met")
    return runtime, peak_rss


def _remove_tracked(
    files: Mapping[Path, tuple[int, int]],
    directories: Mapping[Path, tuple[int, int]],
) -> None:
    for path, identity in reversed(tuple(files.items())):
        try:
            observed = os.lstat(path)
        except FileNotFoundError:
            continue
        if (
            stat.S_ISREG(observed.st_mode)
            and observed.st_nlink == 1
            and (observed.st_dev, observed.st_ino) == identity
        ):
            path.unlink()
    for path, identity in sorted(directories.items(), key=lambda item: len(item[0].parts), reverse=True):
        try:
            observed = os.lstat(path)
        except FileNotFoundError:
            continue
        if stat.S_ISDIR(observed.st_mode) and (observed.st_dev, observed.st_ino) == identity:
            try:
                path.rmdir()
            except OSError:
                pass


def _validate_layout(root: Path, layout: OutputLayout) -> tuple[Path, Path, Path]:
    payload = root / _safe_relative(layout.payload_relative)
    temporary = root / _safe_relative(layout.temporary_relative)
    marker = root / _safe_relative(layout.marker_relative)
    if len({payload, temporary, marker}) != 3 or not (
        payload.parent == temporary.parent == marker.parent
    ):
        raise UG1SourceAcquisitionRefusal("output layout must use three distinct sibling paths")
    for path in (payload, temporary, marker):
        _assert_chain_safe(root, path)
        try:
            os.lstat(path)
        except FileNotFoundError:
            continue
        raise UG1SourceAcquisitionRefusal("output path already exists")
    return payload, temporary, marker


def _write_payload_stream(
    *,
    response: BinaryIO,
    destination: Path,
    spec: SourceFileSpec,
    expected_sha256: str,
    caps: SourceAcquisitionCaps,
    started: float,
    root: Path,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_usage_reader: Callable[[Path], Any],
) -> tuple[int, str, tuple[int, int], int, int]:
    descriptor = os.open(
        destination,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
        0o600,
    )
    created = os.fstat(descriptor)
    created_identity = (created.st_dev, created.st_ino)
    transfer_digest = hashlib.sha256()
    total = 0
    maximum_requested = 0
    try:
        with os.fdopen(descriptor, "wb") as handle:
            while True:
                requested = min(caps.chunk_bytes, spec.size_bytes - total + 1)
                maximum_requested = max(maximum_requested, requested)
                chunk = response.read(requested)
                if not isinstance(chunk, bytes):
                    raise UG1SourceAcquisitionRefusal("payload stream returned non-bytes")
                if len(chunk) > caps.chunk_bytes:
                    raise UG1SourceAcquisitionRefusal("payload stream chunk exceeds cap")
                if not chunk:
                    break
                total += len(chunk)
                if total > spec.size_bytes or total > caps.payload_network_bytes:
                    raise UG1SourceAcquisitionRefusal("payload body exceeds frozen size")
                written = handle.write(chunk)
                if written != len(chunk):
                    raise UG1SourceAcquisitionRefusal("short payload write")
                transfer_digest.update(chunk)
                _check_resources(
                    started=started,
                    root=root,
                    caps=caps,
                    clock=clock,
                    rss_reader=rss_reader,
                    disk_usage_reader=disk_usage_reader,
                )
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            observed = os.lstat(destination)
        except FileNotFoundError:
            pass
        else:
            if (
                stat.S_ISREG(observed.st_mode)
                and observed.st_nlink == 1
                and (observed.st_dev, observed.st_ino) == created_identity
            ):
                destination.unlink()
        raise
    try:
        observed = os.lstat(destination)
        identity = (observed.st_dev, observed.st_ino)
        if identity != created_identity:
            raise UG1SourceAcquisitionRefusal("payload identity changed after write")
        if total != spec.size_bytes:
            raise UG1SourceAcquisitionRefusal("payload body is shorter than frozen size")
        transfer_sha256 = transfer_digest.hexdigest()
        if transfer_sha256 != expected_sha256:
            raise UG1SourceAcquisitionRefusal("transfer SHA-256 differs from official manifest")
        local_size, local_sha256 = _hash_regular_nofollow(destination)
        if local_size != total or local_sha256 != transfer_sha256:
            raise UG1SourceAcquisitionRefusal("opaque post-write integrity pass differs")
        return total, local_sha256, identity, maximum_requested, _file_disk_bytes(destination)
    except Exception:
        try:
            observed = os.lstat(destination)
        except FileNotFoundError:
            pass
        else:
            if (
                stat.S_ISREG(observed.st_mode)
                and observed.st_nlink == 1
                and (observed.st_dev, observed.st_ino) == created_identity
            ):
                destination.unlink()
        raise


def _assert_private_membership(temporary: Path, specs: Sequence[SourceFileSpec]) -> None:
    expected_files = {spec.repository_path for spec in specs} | {"manifest.json"}
    observed_files: set[str] = set()
    expected_directories = {spec.participant for spec in specs}
    for child in os.scandir(temporary):
        if child.is_symlink():
            raise UG1SourceAcquisitionRefusal("temporary bundle contains a symlink")
        if child.is_file(follow_symlinks=False):
            observed_files.add(child.name)
        elif child.is_dir(follow_symlinks=False) and child.name in expected_directories:
            for nested in os.scandir(child.path):
                if not nested.is_file(follow_symlinks=False) or nested.is_symlink():
                    raise UG1SourceAcquisitionRefusal("temporary bundle member type differs")
                observed_files.add(f"{child.name}/{nested.name}")
        else:
            raise UG1SourceAcquisitionRefusal("temporary bundle membership differs")
    if observed_files != expected_files:
        raise UG1SourceAcquisitionRefusal("temporary bundle membership differs")


def _assert_public_receipt(receipt: Mapping[str, Any]) -> None:
    allowed = {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "file_count",
        "payload_bytes",
        "checksum_request_count",
        "payload_request_count",
        "redirect_count",
        "retry_count",
        "opaque_post_write_pass_count",
        "producer_mode",
        "warnings",
        "claim_boundary",
    }
    if set(receipt) != allowed:
        raise UG1SourceAcquisitionRefusal("public receipt schema differs")

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                    raise UG1SourceAcquisitionRefusal("public receipt contains protected detail")
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)
        elif isinstance(value, str):
            lowered = value.lower()
            if "physionet.org" in lowered or ".edf" in lowered or "/users/" in lowered:
                raise UG1SourceAcquisitionRefusal("public receipt contains protected value")

    visit(receipt)


def run_source_acquisition(
    *,
    repo_root: str | Path,
    opener: GetOpener,
    generated: bool,
    workspace_root: str | Path,
    layout: OutputLayout,
    environ: Mapping[str, str],
    caps: SourceAcquisitionCaps = SourceAcquisitionCaps(),
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_process_tree_rss_bytes,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
) -> SourceAcquisitionOutcome:
    """Acquire one exact six-file bundle through an injected sequential opener."""

    if caps.chunk_bytes <= 0 or caps.chunk_bytes > CHUNK_BYTES:
        raise UG1SourceAcquisitionRefusal("stream chunk cap differs")
    _assert_thread_environment(environ)
    specs = _source_specs(Path(repo_root))
    root = _workspace_root(workspace_root)
    started = clock()
    _check_resources(
        started=started,
        root=root,
        caps=caps,
        clock=clock,
        rss_reader=rss_reader,
        disk_usage_reader=disk_usage_reader,
    )
    payload_root, temporary_root, marker_path = _validate_layout(root, layout)
    tracked_files: dict[Path, tuple[int, int]] = {}
    tracked_dirs: dict[Path, tuple[int, int]] = {}
    marker_identity: tuple[int, int] | None = None
    payload_body_bytes = 0
    header_bytes = 0
    metadata_bytes = 0
    peak_disk_bytes = 0
    maximum_requested_read = 0
    post_write_passes = 0
    checksum_requests = 0
    payload_requests = 0
    try:
        _mkdir_chain(root, marker_path.parent, tracked_dirs)
        marker_payload = _canonical_json(
            {
                "schema_name": "neurodecodekit.eegmmidb_ug1_source_acquisition_consumed",
                "schema_version": SCHEMA_VERSION,
                "lane_id": LANE_ID,
                "status": "consumed_before_first_request",
                "retry_allowed": False,
                "rerun_allowed": False,
            }
        )
        marker_identity = _write_exclusive_synced(marker_path, marker_payload)
        metadata_bytes += len(marker_payload)
        peak_disk_bytes += _file_disk_bytes(marker_path)
        checksum_response = opener(_checksum_request(), REQUEST_TIMEOUT_SECONDS)
        checksum_requests += 1
        try:
            checksum_size, observed_headers = _validate_response_identity(
                checksum_response,
                requested_url=CHECKSUM_URL,
                expected_size=None,
                expected_spec=None,
                caps=caps,
            )
            header_bytes += observed_headers
            if checksum_size > caps.checksum_bytes:
                raise UG1SourceAcquisitionRefusal("checksum manifest body exceeds cap")
            checksum_payload = _read_bounded_body(
                checksum_response,
                caps.checksum_bytes,
                caps.chunk_bytes,
            )
        finally:
            close_checksum = getattr(checksum_response, "close", None)
            if callable(close_checksum):
                close_checksum()
        if len(checksum_payload) != checksum_size:
            raise UG1SourceAcquisitionRefusal("checksum manifest body framing differs")
        frozen_checksums = parse_checksum_manifest(checksum_payload, specs)
        metadata_bytes += len(checksum_payload)
        os.mkdir(temporary_root, 0o700)
        observed_temp = os.lstat(temporary_root)
        tracked_dirs[temporary_root] = (observed_temp.st_dev, observed_temp.st_ino)
        records: list[dict[str, Any]] = []
        for spec in specs:
            participant_dir = temporary_root / spec.participant
            if participant_dir not in tracked_dirs:
                os.mkdir(participant_dir, 0o700)
                observed_dir = os.lstat(participant_dir)
                tracked_dirs[participant_dir] = (observed_dir.st_dev, observed_dir.st_ino)
            response = opener(_payload_request(spec), REQUEST_TIMEOUT_SECONDS)
            payload_requests += 1
            try:
                _size, observed_headers = _validate_response_identity(
                    response,
                    requested_url=spec.url,
                    expected_size=spec.size_bytes,
                    expected_spec=spec,
                    caps=caps,
                )
                header_bytes += observed_headers
                if header_bytes > caps.header_bytes:
                    raise UG1SourceAcquisitionRefusal(
                        "aggregate response header bytes exceed cap"
                    )
                destination = temporary_root / spec.repository_path
                (
                    body_bytes,
                    digest,
                    identity,
                    requested_read,
                    disk_bytes,
                ) = _write_payload_stream(
                    response=response,
                    destination=destination,
                    spec=spec,
                    expected_sha256=frozen_checksums[spec.repository_path],
                    caps=caps,
                    started=started,
                    root=root,
                    clock=clock,
                    rss_reader=rss_reader,
                    disk_usage_reader=disk_usage_reader,
                )
            finally:
                close_response = getattr(response, "close", None)
                if callable(close_response):
                    close_response()
            tracked_files[destination] = identity
            payload_body_bytes += body_bytes
            maximum_requested_read = max(maximum_requested_read, requested_read)
            peak_disk_bytes += disk_bytes
            post_write_passes += 1
            if payload_body_bytes > caps.payload_network_bytes:
                raise UG1SourceAcquisitionRefusal("aggregate payload bytes exceed cap")
            records.append(
                {
                    "repository_path": spec.repository_path,
                    "participant": spec.participant,
                    "run": spec.run,
                    "partition": spec.partition,
                    "size_bytes": body_bytes,
                    "sha256": digest,
                    "etag": spec.etag,
                    "last_modified": spec.last_modified,
                    "accept_ranges": spec.accept_ranges,
                }
            )
        if payload_body_bytes != EXACT_PAYLOAD_BYTES:
            raise UG1SourceAcquisitionRefusal("aggregate payload bytes differ")
        if payload_requests != 6 or checksum_requests != 1:
            raise UG1SourceAcquisitionRefusal("request counts differ")
        assert_consumed = getattr(opener, "assert_consumed", None)
        if callable(assert_consumed):
            assert_consumed()
        manifest = {
            "schema_name": "neurodecodekit.eegmmidb_ug1_source_bundle_manifest",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "dataset": {
                "provider": "PhysioNet",
                "dataset_id": "eegmmidb",
                "version": "1.0.0",
                "doi": "10.13026/C28G6P",
            },
            "partition": "source_fit_missing",
            "file_count": 6,
            "payload_bytes": payload_body_bytes,
            "files": records,
            "integrity": {
                "transfer_hash": "SHA-256",
                "official_manifest_match": True,
                "opaque_post_write_passes": post_write_passes,
                "EDF_semantic_reads": 0,
            },
            "claim_boundary": {
                "scientific_claim_established": False,
                "neural_or_decoding_advantage_established": False,
                "unseen_participant_generalization_established": False,
            },
        }
        manifest_bytes = _canonical_json(manifest)
        metadata_bytes += len(manifest_bytes)
        if metadata_bytes > caps.metadata_bytes:
            raise UG1SourceAcquisitionRefusal("combined metadata bytes exceed cap")
        manifest_path = temporary_root / "manifest.json"
        manifest_identity = _write_exclusive_synced(manifest_path, manifest_bytes)
        tracked_files[manifest_path] = manifest_identity
        manifest_size, manifest_sha256 = _hash_regular_nofollow(manifest_path)
        if manifest_size != len(manifest_bytes) or manifest_sha256 != _sha256(manifest_bytes):
            raise UG1SourceAcquisitionRefusal("private manifest verification differs")
        peak_disk_bytes += _file_disk_bytes(manifest_path)
        if peak_disk_bytes > caps.incremental_disk_bytes:
            raise UG1SourceAcquisitionRefusal("incremental disk cap exceeded")
        _assert_private_membership(temporary_root, specs)
        receipt = {
            "schema_name": "neurodecodekit.eegmmidb_ug1_source_acquisition_receipt",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "complete",
            "route": GENERATED_ROUTE if generated else "EEGMMIDBUG1SA2-PASS",
            "file_count": 6,
            "payload_bytes": payload_body_bytes,
            "checksum_request_count": checksum_requests,
            "payload_request_count": payload_requests,
            "redirect_count": 0,
            "retry_count": 0,
            "opaque_post_write_pass_count": post_write_passes,
            "producer_mode": "generated_mock" if generated else "registered_live_opaque",
            "warnings": [
                "opaque_bytes_not_semantically_read",
                "acquisition_is_not_decoding_evidence",
                "no_scientific_claim_upgrade",
            ],
            "claim_boundary": {
                "scientific_claim_established": False,
                "neural_or_decoding_advantage_established": False,
                "unseen_generalization_established": False,
            },
        }
        _assert_public_receipt(receipt)
        receipt_bytes = _canonical_json(receipt)
        metadata_bytes += len(receipt_bytes)
        if metadata_bytes > caps.metadata_bytes:
            raise UG1SourceAcquisitionRefusal("combined metadata bytes exceed cap")
        runtime, peak_rss = _check_resources(
            started=started,
            root=root,
            caps=caps,
            clock=clock,
            rss_reader=rss_reader,
            disk_usage_reader=disk_usage_reader,
        )
        _rename_noreplace(temporary_root, payload_root)
        return SourceAcquisitionOutcome(
            manifest=manifest,
            manifest_bytes=manifest_bytes,
            receipt=receipt,
            receipt_bytes=receipt_bytes,
            payload_root=payload_root,
            marker_path=marker_path,
            measurements={
                "checksum_manifest_body_bytes": len(checksum_payload),
                "payload_body_bytes": payload_body_bytes,
                "application_visible_response_header_bytes": header_bytes,
                "maximum_requested_stream_read_bytes": maximum_requested_read,
                "opaque_post_write_passes": post_write_passes,
                "incremental_disk_bytes_peak": peak_disk_bytes,
                "combined_metadata_bytes": metadata_bytes,
                "runtime_seconds": runtime,
                "peak_process_tree_RSS_bytes": peak_rss,
                "checksum_requests": checksum_requests,
                "payload_requests": payload_requests,
            },
        )
    except Exception:
        _remove_tracked(tracked_files, tracked_dirs)
        if marker_identity is None:
            _remove_tracked({}, tracked_dirs)
        raise


def _generated_layout(name: str) -> OutputLayout:
    return OutputLayout(
        payload_relative=f"{name}/bundle",
        temporary_relative=f"{name}/.bundle.tmp",
        marker_relative=f"{name}/consumed.json",
    )


def _remove_generated_layout(root: Path, layout: OutputLayout, specs: Sequence[SourceFileSpec]) -> None:
    payload = root / layout.payload_relative
    temporary = root / layout.temporary_relative
    marker = root / layout.marker_relative
    for base in (payload, temporary):
        for spec in reversed(specs):
            try:
                (base / spec.repository_path).unlink()
            except FileNotFoundError:
                pass
        try:
            (base / "manifest.json").unlink()
        except FileNotFoundError:
            pass
        for participant in reversed(tuple(dict.fromkeys(spec.participant for spec in specs))):
            try:
                (base / participant).rmdir()
            except OSError:
                pass
        try:
            base.rmdir()
        except OSError:
            pass
    try:
        marker.unlink()
    except FileNotFoundError:
        pass
    try:
        marker.parent.rmdir()
    except OSError:
        pass


def _replace_header(
    exchange: FixtureExchange,
    name: str,
    value: str | None,
) -> FixtureExchange:
    headers = [(key, item) for key, item in exchange.response.headers.raw_items() if key.lower() != name.lower()]
    if value is not None:
        headers.append((name, value))
    response = exchange.response
    return FixtureExchange(
        url=exchange.url,
        response=FixtureGetResponse(
            url=response.geturl(),
            headers=headers,
            payload=response._payload,
            spec=response._spec,
            spec_index=response._spec_index,
            body_size=response._body_size,
            status=response.status,
            nonbytes=response._nonbytes,
        ),
        expected_headers=exchange.expected_headers,
    )


def run_generated_qualification(
    *,
    repo_root: str | Path,
    workspace_root: str | Path,
    environ: Mapping[str, str],
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_process_tree_rss_bytes,
) -> dict[str, Any]:
    """Run the sole registered Stage S-A1 generated/mock qualification."""

    root = _workspace_root(workspace_root)
    specs = _source_specs(Path(repo_root))
    source = build_generated_exchanges(repo_root)
    source_fingerprint = _sha256(
        _canonical_json(
            {
                "checksum_sha256": _sha256(source[0].response._payload or b""),
                "payload_sha256s": [
                    _generated_digest(spec, index) for index, spec in enumerate(specs)
                ],
            }
        )
    )
    started = clock()
    passed: list[str] = []
    mock_requests = 0
    payload_bytes = 0
    metadata_bytes = 0
    generated_body_bytes_read = 0
    successful_bundle_count = 0
    opaque_post_write_passes = 0
    peak_incremental_disk_bytes = 0
    maximum_stream_read_bytes = 0
    peak_response_header_bytes = 0
    direct_refusals = 0

    def execute(
        name: str,
        exchanges: Sequence[FixtureExchange],
        *,
        case_environ: Mapping[str, str] = environ,
        case_clock: Callable[[], float] = lambda: 10.0,
        case_rss: Callable[[], int] = lambda: 32 * 1024 * 1024,
        disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
        expect_success: bool,
        layout: OutputLayout | None = None,
        cleanup: bool = True,
    ) -> SourceAcquisitionOutcome | None:
        nonlocal mock_requests, payload_bytes, metadata_bytes
        nonlocal generated_body_bytes_read, successful_bundle_count
        nonlocal opaque_post_write_passes, peak_incremental_disk_bytes
        nonlocal maximum_stream_read_bytes, peak_response_header_bytes
        case_layout = layout or _generated_layout(name)
        opener = FixtureGetOpener(exchanges)
        try:
            outcome = run_source_acquisition(
                repo_root=repo_root,
                opener=opener,
                generated=True,
                workspace_root=root,
                layout=case_layout,
                environ=case_environ,
                clock=case_clock,
                rss_reader=case_rss,
                disk_usage_reader=disk_usage_reader,
            )
        except UG1SourceAcquisitionRefusal:
            mock_requests += len(opener.calls)
            generated_body_bytes_read += sum(
                row.response._position for row in exchanges
            )
            if expect_success:
                raise
            passed.append(name)
            if cleanup:
                _remove_generated_layout(root, case_layout, specs)
            return None
        if not expect_success:
            raise UG1SourceAcquisitionRefusal(f"generated mutation unexpectedly passed: {name}")
        mock_requests += len(opener.calls)
        generated_body_bytes_read += sum(row.response._position for row in exchanges)
        payload_bytes += int(outcome.measurements["payload_body_bytes"])
        metadata_bytes += int(outcome.measurements["combined_metadata_bytes"])
        successful_bundle_count += 1
        opaque_post_write_passes += int(outcome.measurements["opaque_post_write_passes"])
        peak_incremental_disk_bytes = max(
            peak_incremental_disk_bytes,
            int(outcome.measurements["incremental_disk_bytes_peak"]),
        )
        maximum_stream_read_bytes = max(
            maximum_stream_read_bytes,
            int(outcome.measurements["maximum_requested_stream_read_bytes"]),
        )
        peak_response_header_bytes = max(
            peak_response_header_bytes,
            int(outcome.measurements["application_visible_response_header_bytes"]),
        )
        passed.append(name)
        _remove_generated_layout(root, case_layout, specs)
        return outcome

    complete = execute("complete_bundle", source, expect_success=True)
    replay = execute(
        "deterministic_replay",
        build_generated_exchanges(repo_root),
        expect_success=True,
    )
    if complete is None or replay is None or complete.manifest_bytes != replay.manifest_bytes:
        raise UG1SourceAcquisitionRefusal("generated deterministic replay differs")

    def checksum_mutation(name: str, payload: bytes) -> None:
        rows = list(build_generated_exchanges(repo_root))
        rows[0] = FixtureExchange(
            url=CHECKSUM_URL,
            response=FixtureGetResponse(
                url=CHECKSUM_URL,
                headers=_checksum_headers(len(payload)),
                payload=payload,
            ),
            expected_headers=rows[0].expected_headers,
        )
        execute(name, rows, expect_success=False)

    checksum_payload = source[0].response._payload or b""
    checksum_lines = checksum_payload.decode("ascii").splitlines()
    checksum_mutation("checksum_missing", ("\n".join(checksum_lines[:-1]) + "\n").encode("ascii"))
    checksum_mutation(
        "checksum_duplicate",
        ("\n".join([*checksum_lines, checksum_lines[0]]) + "\n").encode("ascii"),
    )
    checksum_mutation(
        "checksum_uppercase",
        (checksum_lines[0].upper() + "\n" + "\n".join(checksum_lines[1:]) + "\n").encode("ascii"),
    )
    alias = checksum_lines[0].replace("  ", "  ./", 1)
    checksum_mutation(
        "checksum_alias",
        (alias + "\n" + "\n".join(checksum_lines[1:]) + "\n").encode("ascii"),
    )
    checksum_mutation("checksum_malformed", b"malformed\n")

    reordered = list(build_generated_exchanges(repo_root))
    reordered[1], reordered[2] = reordered[2], reordered[1]
    execute("request_order", reordered, expect_success=False)
    execute("missing_response", build_generated_exchanges(repo_root)[:-1], expect_success=False)

    for case in (
        "redirect",
        "status",
        "content_length",
        "etag",
        "last_modified",
        "accept_ranges",
        "content_encoding",
        "content_range",
        "short_body",
        "oversized_body",
        "nonbytes_body",
    ):
        rows = list(build_generated_exchanges(repo_root))
        target = rows[1]
        response = target.response
        if case == "redirect":
            rows[1] = FixtureExchange(
                target.url,
                FixtureGetResponse(
                    url=f"{target.url}.mirror",
                    headers=tuple(response.headers.raw_items()),
                    spec=response._spec,
                    spec_index=response._spec_index,
                ),
                target.expected_headers,
            )
        elif case == "status":
            rows[1] = FixtureExchange(
                target.url,
                FixtureGetResponse(
                    url=target.url,
                    headers=tuple(response.headers.raw_items()),
                    spec=response._spec,
                    spec_index=response._spec_index,
                    status=206,
                ),
                target.expected_headers,
            )
        elif case == "content_length":
            rows[1] = _replace_header(target, "Content-Length", str(specs[0].size_bytes - 1))
        elif case == "etag":
            rows[1] = _replace_header(target, "ETag", '"different"')
        elif case == "last_modified":
            rows[1] = _replace_header(target, "Last-Modified", "Thu, 01 Jan 1970 00:00:00 GMT")
        elif case == "accept_ranges":
            rows[1] = _replace_header(target, "Accept-Ranges", "none")
        elif case == "content_encoding":
            rows[1] = _replace_header(target, "Content-Encoding", "identity")
        elif case == "content_range":
            rows[1] = _replace_header(target, "Content-Range", "bytes 0-1/2")
        elif case == "short_body":
            rows[1] = FixtureExchange(
                target.url,
                FixtureGetResponse(
                    url=target.url,
                    headers=tuple(response.headers.raw_items()),
                    spec=specs[0],
                    spec_index=0,
                    body_size=specs[0].size_bytes - 1,
                ),
                target.expected_headers,
            )
        elif case == "oversized_body":
            rows[1] = FixtureExchange(
                target.url,
                FixtureGetResponse(
                    url=target.url,
                    headers=tuple(response.headers.raw_items()),
                    spec=specs[0],
                    spec_index=0,
                    body_size=specs[0].size_bytes + 1,
                ),
                target.expected_headers,
            )
        else:
            rows[1] = FixtureExchange(
                target.url,
                FixtureGetResponse(
                    url=target.url,
                    headers=tuple(response.headers.raw_items()),
                    spec=specs[0],
                    spec_index=0,
                    nonbytes=True,
                ),
                target.expected_headers,
            )
        execute(case, rows, expect_success=False)

    collision_layout = _generated_layout("output_collision")
    collision_parent = root / Path(collision_layout.payload_relative).parent
    collision_parent.mkdir(mode=0o700)
    collision_payload = root / collision_layout.payload_relative
    collision_payload.write_bytes(b"preexisting")
    execute(
        "output_collision",
        build_generated_exchanges(repo_root),
        expect_success=False,
        layout=collision_layout,
        cleanup=False,
    )
    collision_payload.unlink()
    collision_parent.rmdir()

    second_layout = _generated_layout("second_invocation")
    second_source = build_generated_exchanges(repo_root)
    opener = FixtureGetOpener(second_source)
    first = run_source_acquisition(
        repo_root=repo_root,
        opener=opener,
        generated=True,
        workspace_root=root,
        layout=second_layout,
        environ=environ,
        clock=lambda: 10.0,
        rss_reader=lambda: 32 * 1024 * 1024,
    )
    mock_requests += len(opener.calls)
    generated_body_bytes_read += sum(row.response._position for row in second_source)
    payload_bytes += int(first.measurements["payload_body_bytes"])
    metadata_bytes += int(first.measurements["combined_metadata_bytes"])
    successful_bundle_count += 1
    opaque_post_write_passes += int(first.measurements["opaque_post_write_passes"])
    peak_incremental_disk_bytes = max(
        peak_incremental_disk_bytes,
        int(first.measurements["incremental_disk_bytes_peak"]),
    )
    maximum_stream_read_bytes = max(
        maximum_stream_read_bytes,
        int(first.measurements["maximum_requested_stream_read_bytes"]),
    )
    peak_response_header_bytes = max(
        peak_response_header_bytes,
        int(first.measurements["application_visible_response_header_bytes"]),
    )
    second_opener = FixtureGetOpener(build_generated_exchanges(repo_root))
    try:
        run_source_acquisition(
            repo_root=repo_root,
            opener=second_opener,
            generated=True,
            workspace_root=root,
            layout=second_layout,
            environ=environ,
            clock=lambda: 10.0,
            rss_reader=lambda: 32 * 1024 * 1024,
        )
    except UG1SourceAcquisitionRefusal:
        passed.append("second_invocation")
    else:
        raise UG1SourceAcquisitionRefusal("second invocation unexpectedly passed")
    _remove_generated_layout(root, second_layout, specs)

    resource_cases = (
        (
            "thread_environment",
            {**environ, THREAD_ENV_KEYS[0]: "2"},
            lambda: 10.0,
            lambda: 32 * 1024 * 1024,
            shutil.disk_usage,
        ),
        (
            "free_disk",
            environ,
            lambda: 10.0,
            lambda: 32 * 1024 * 1024,
            lambda _path: type("Disk", (), {"free": 0})(),
        ),
        (
            "peak_rss",
            environ,
            lambda: 10.0,
            lambda: MAX_PEAK_RSS_BYTES + 1,
            shutil.disk_usage,
        ),
        (
            "wall_time",
            environ,
            iter((0.0, MAX_WALL_SECONDS + 1)).__next__,
            lambda: 32 * 1024 * 1024,
            shutil.disk_usage,
        ),
    )
    for case, case_env, case_clock, case_rss, disk_reader in resource_cases:
        execute(
            case,
            build_generated_exchanges(repo_root),
            case_environ=case_env,
            case_clock=case_clock,
            case_rss=case_rss,
            disk_usage_reader=disk_reader,
            expect_success=False,
        )

    try:
        _validate_url(f"{FILE_ROOT_URL}S016/S016R11.edf")
        if f"{FILE_ROOT_URL}S016/S016R11.edf" not in {spec.url for spec in specs}:
            raise UG1SourceAcquisitionRefusal("fresh-final URL is outside the exact source allowlist")
    except UG1SourceAcquisitionRefusal:
        direct_refusals += 1
        passed.append("fresh_final_refusal")
    else:
        raise UG1SourceAcquisitionRefusal("fresh-final URL unexpectedly passed")

    if tuple(passed) != QUALIFICATION_CASES:
        raise UG1SourceAcquisitionRefusal("generated qualification case order differs")
    if (
        successful_bundle_count != 3
        or payload_bytes != 3 * EXACT_PAYLOAD_BYTES
        or opaque_post_write_passes != 18
        or maximum_stream_read_bytes <= 0
        or maximum_stream_read_bytes > CHUNK_BYTES
        or peak_incremental_disk_bytes > MAX_INCREMENTAL_DISK_BYTES
        or peak_response_header_bytes > MAX_HEADER_BYTES
    ):
        raise UG1SourceAcquisitionRefusal("generated qualification measurements differ")
    if source_fingerprint != _sha256(
        _canonical_json(
            {
                "checksum_sha256": _sha256(
                    (build_generated_exchanges(repo_root)[0].response._payload or b"")
                ),
                "payload_sha256s": [
                    _generated_digest(spec, index) for index, spec in enumerate(specs)
                ],
            }
        )
    ):
        raise UG1SourceAcquisitionRefusal("generated source fixtures mutated")
    runtime = clock() - started
    peak_rss = int(rss_reader())
    if runtime < 0 or runtime > MAX_WALL_SECONDS or peak_rss > MAX_PEAK_RSS_BYTES:
        raise UG1SourceAcquisitionRefusal("generated qualification resource cap exceeded")
    summary = {
        "schema_name": "neurodecodekit.eegmmidb_ug1_source_acquisition_stage_sa1_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": GENERATED_ROUTE,
        "case_count": len(passed),
        "cases": passed,
        "mock_requests": mock_requests,
        "real_requests": 0,
        "generated_body_bytes_read": generated_body_bytes_read,
        "successful_generated_bundle_count": successful_bundle_count,
        "successful_generated_payload_body_bytes": payload_bytes,
        "generated_metadata_bytes": metadata_bytes,
        "retained_generated_output_bytes": 0,
        "opaque_post_write_passes": opaque_post_write_passes,
        "peak_incremental_disk_bytes": peak_incremental_disk_bytes,
        "peak_application_visible_response_header_bytes": peak_response_header_bytes,
        "direct_refusals": direct_refusals,
        "deterministic_replay": True,
        "source_immutability_checks": 1,
        "maximum_stream_chunk_bytes": maximum_stream_read_bytes,
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": peak_rss,
        "source_fixture_sha256": source_fingerprint,
        "operation_counters": _zero_operation_counters(),
        "warnings": [
            "generated_mock_only",
            "live_transport_not_invoked",
            "no_real_EEG_or_target_access",
            "not_neural_or_decoding_evidence",
        ],
        "claim_boundary": {
            "scientific_claim_established": False,
            "real_EEG_accessed": False,
            "unseen_participant_generalization_established": False,
            "end_to_end_decoding_latency_measured": False,
        },
    }
    payload = _canonical_json(summary)
    if len(payload) > MAX_METADATA_BYTES:
        raise UG1SourceAcquisitionRefusal("generated summary exceeds output cap")
    return summary


def write_generated_summary(path: str | Path, summary: Mapping[str, Any]) -> tuple[int, str]:
    """Write one exclusive canonical generated summary outside protected roots."""

    destination = Path(path)
    if any(part in {".codex_work", "data"} for part in destination.parts):
        raise UG1SourceAcquisitionRefusal("generated summary path uses a protected root")
    payload = _canonical_json(dict(summary))
    if len(payload) > MAX_METADATA_BYTES:
        raise UG1SourceAcquisitionRefusal("generated summary exceeds output cap")
    parent = _workspace_root(destination.parent)
    _assert_chain_safe(parent, destination)
    _write_exclusive_synced(destination, payload)
    return len(payload), _sha256(payload)


def _read_green_sa1_proof(repo_root: Path, evidence: SA1ProofEvidence) -> None:
    proof_path = repo_root / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_proof_closeout.v0.json"
    payload = _read_regular_nofollow(proof_path, MAX_METADATA_BYTES)
    if _sha256(payload) != evidence.proof_closeout_registry_sha256:
        raise UG1SourceAcquisitionRefusal("Stage S-A1 proof registry hash differs")
    try:
        proof = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UG1SourceAcquisitionRefusal("Stage S-A1 proof registry JSON differs") from exc
    implementation = proof.get("green_implementation", {})
    closeout = proof.get("green_proof_closeout", {})
    expected = {
        "implementation_commit": evidence.implementation_commit,
        "implementation_CI_run_id": evidence.implementation_ci_run_id,
        "implementation_base_job_id": evidence.implementation_base_job_id,
        "implementation_optional_job_id": evidence.implementation_optional_job_id,
        "proof_closeout_commit": evidence.proof_closeout_commit,
        "proof_closeout_CI_run_id": evidence.proof_closeout_ci_run_id,
        "proof_closeout_base_job_id": evidence.proof_closeout_base_job_id,
        "proof_closeout_optional_job_id": evidence.proof_closeout_optional_job_id,
    }
    observed = {
        "implementation_commit": implementation.get("commit"),
        "implementation_CI_run_id": implementation.get("CI_run_id"),
        "implementation_base_job_id": implementation.get("base_python_job_id"),
        "implementation_optional_job_id": implementation.get("optional_neuro_job_id"),
        "proof_closeout_commit": closeout.get("commit"),
        "proof_closeout_CI_run_id": closeout.get("CI_run_id"),
        "proof_closeout_base_job_id": closeout.get("base_python_job_id"),
        "proof_closeout_optional_job_id": closeout.get("optional_neuro_job_id"),
    }
    if observed != expected or proof.get("both_required_stages_remotely_green") is not True:
        raise UG1SourceAcquisitionRefusal("Stage S-A1 green proof evidence differs")


def execute_registered_source_acquisition(
    repo_root: str | Path,
    *,
    evidence: SA1ProofEvidence,
    environ: Mapping[str, str],
) -> SourceAcquisitionOutcome:
    """Execute later Stage S-A2 only after exact proof evidence is supplied.

    This function is intentionally absent from the CLI.  It validates the
    future proof record before constructing a live opener or touching the
    registered output paths.
    """

    root = Path(repo_root)
    _read_green_sa1_proof(root, evidence)
    opener = StandardLibraryGetOpener()
    return run_source_acquisition(
        repo_root=root,
        opener=opener,
        generated=False,
        workspace_root=root,
        layout=OutputLayout(
            payload_relative=".codex_work/eegmmidb_ug1/source_fit_s001_s003_runs_04_08_v0",
            temporary_relative=".codex_work/eegmmidb_ug1/.source_fit_s001_s003_runs_04_08_v0.tmp",
            marker_relative=".codex_work/eegmmidb_ug1/source_fit_s001_s003_runs_04_08_v0.consumed.json",
        ),
        environ=environ,
    )
