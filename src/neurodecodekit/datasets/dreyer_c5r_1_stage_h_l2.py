"""Activation-locked one-file fixed-header adapter for DREYER-C5R-1 H-L2."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import shutil
import ssl
import stat
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, BinaryIO

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live_recovery as recovery
from neurodecodekit.datasets.dreyer_c5r_1 import EDFHeaderSummary
from neurodecodekit.experiments import dreyer_c5r_1 as parent

SCHEMA_VERSION = "0.1.0"
REQUEST_ID = "DREYER-C5R-1-HL2-A0"
DECISION_ID = "DREYER-C5R-1-HL2-A0-D0"
LANE_ID = "DREYER-C5R-1-HL"
GREEN_DECISION_COMMIT = "53f2c48831d1db7875bf09a35f107e35f97c6bf4"
GREEN_DECISION_CI_RUN_ID = 33_257_975_186
GREEN_DECISION_BASE_JOB_ID = 99_114_895_023
GREEN_DECISION_OPTIONAL_JOB_ID = 99_114_895_128
DECISION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_l2_fixed_header_activation_decision.v0.json"
)
DECISION_SHA256 = "c365e0a3a33807bc22bddc481146486475e0ad352244cbec43da59fbabd619bf"
ACTIVATION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_l2_fixed_header_activation.v0.json"
)
PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_l2_fixed_header_result.v0.json"
)
PRIVATE_ROOT_RELATIVE_PATH = Path(".codex_work/dreyer_c5r_1_stage_h_l2/v0")
CONSUMED_MARKER_NAME = "execution-consumed.v0.json"
STAGING_DIRECTORY_NAME = "staging-invocation-0001"
STAGING_PAYLOAD_NAME = "verified-payload.edf"
PRIVATE_PAYLOAD_NAME = "sub-01_task-R1acquisition_eeg.edf"
THREAD_ENV_KEYS = parent.THREAD_ENVIRONMENT
MAX_RUNTIME_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_NETWORK_BODY_BYTES = 16 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 32 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MAX_STREAM_CHUNK_BYTES = 1024**2
MINIMUM_FREE_DISK_BYTES = 10 * 1024**3
FROZEN_RECOVERY_ARTIFACTS = (
    (
        Path("docs/DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_IMPLEMENTATION.md"),
        "08c1df8d721a36d1ce677ffeaf9e20aca19cf9184f4c26fc478a0b0ee1a71b1b",
    ),
    (
        Path("registries/dreyer_c5r_1_stage_h_live_recovery_implementation.v0.json"),
        "9a55b0cf8407b881cc57cd4e68337b8d93e558436928041f26a949c330031607",
    ),
    (
        Path("src/neurodecodekit/datasets/dreyer_c5r_1_stage_h_live_recovery.py"),
        "e73ddce32724db7dd814c60aed2dd1dad12c4e69e4d147f14488eb7c61596257",
    ),
    (
        Path("src/neurodecodekit/dreyer_c5r_1_stage_h_live_recovery_cli.py"),
        "502dc90065226e511bb9f51481364779892962e210cdb28e40f8b359e1c8495d",
    ),
    (
        Path("tests/test_dreyer_c5r_1_stage_h_live_recovery.py"),
        "d2384f8ea8d9d281d64148f749eac806c9b40ba400d9ea190995b8db1925228d",
    ),
    (
        Path("tests/test_dreyer_c5r_1_stage_h_live_recovery_implementation.py"),
        "e4423298a2ab13c80ee923395076743fe7161498baba0de89f0b748829fed259",
    ),
)
REFUSAL_CODES = (
    "HL2-PROOF",
    "HL2-PATH",
    "HL2-MARKER",
    "HL2-TRANSPORT",
    "HL2-PAYLOAD",
    "HL2-HEADER",
    "HL2-RESOURCE",
    "HL2-TEARDOWN",
    "HL2-PUBLICATION",
)
GENERATED_TRANSACTION_CASES = (
    "valid_H1",
    "missing_thread_cap",
    "low_free_disk",
    "preexisting_public_result",
    "preexisting_consumed_marker",
    "occupied_staging_name",
    "preexisting_final_payload",
    "staging_create_refusal",
    "opener_factory_refusal",
    "request_factory_refusal",
    "response_open_refusal",
    "HTTP_status_drift",
    "final_URL_drift",
    "transfer_encoding",
    "duplicate_content_length",
    "content_encoding",
    "short_body",
    "oversized_body",
    "nonbytes_body",
    "wrong_payload_hash",
    "malformed_fixed_header",
    "wrong_sensor_roster",
    "wrong_sampling_rate",
    "header_payload_geometry",
    "runtime_cap",
    "RSS_cap",
    "incremental_disk_cap",
    "promotion_destination_race",
    "response_close_failure",
    "publication_destination_race",
    "public_output_cap",
    "consumed_rerun",
)
GENERATED_PRECONSUMPTION_REFUSALS = frozenset(
    {
        "missing_thread_cap",
        "low_free_disk",
        "preexisting_public_result",
        "preexisting_consumed_marker",
        "occupied_staging_name",
        "preexisting_final_payload",
        "consumed_rerun",
        "RSS_cap",
    }
)
GENERATED_POSTMARKER_H0_CASES = frozenset(
    {
        "staging_create_refusal",
        "opener_factory_refusal",
        "request_factory_refusal",
        "response_open_refusal",
        "HTTP_status_drift",
        "final_URL_drift",
        "transfer_encoding",
        "duplicate_content_length",
        "content_encoding",
        "short_body",
        "oversized_body",
        "nonbytes_body",
        "wrong_payload_hash",
        "malformed_fixed_header",
        "wrong_sensor_roster",
        "wrong_sampling_rate",
        "header_payload_geometry",
        "runtime_cap",
        "incremental_disk_cap",
        "response_close_failure",
        "promotion_destination_race",
    }
)
GENERATED_PUBLICATION_REFUSALS = frozenset(
    {"publication_destination_race", "public_output_cap"}
)
_PARSER_CAPTURE_LOCK = threading.Lock()


class HL2Refusal(RuntimeError):
    """Sanitized H-L2 refusal containing only an allowlisted code."""

    def __init__(self, code: str) -> None:
        self.code = code if code in REFUSAL_CODES else "HL2-PROOF"
        super().__init__(self.code)


@dataclass(frozen=True)
class ActivationEvidence:
    """Externally observed identity of the remotely green activation commit."""

    activation_sha256: str
    activation_commit: str
    activation_ci_run_id: int
    activation_base_job_id: int
    activation_optional_job_id: int
    registered_execution_ordinal: int = 1


@dataclass
class InvocationManifest:
    """No-follow inventory limiting cleanup to invocation-created paths."""

    private_root: Path
    created: list[Path] = field(default_factory=list)

    def record(self, path: Path) -> None:
        candidate = path.absolute()
        if candidate != self.private_root and self.private_root not in candidate.parents:
            raise HL2Refusal("HL2-PATH")
        info = os.lstat(candidate)
        if stat.S_ISLNK(info.st_mode):
            raise HL2Refusal("HL2-PATH")
        if candidate not in self.created:
            self.created.append(candidate)

    def owns(self, path: Path) -> bool:
        return path.absolute() in self.created


@dataclass
class GeneratedResponse:
    body: bytes
    url: str
    status: int = 200
    headers: Sequence[tuple[str, str]] | None = None
    maximum_read_bytes: int | None = 97
    nonbytes_first_read: bool = False
    close_failure: bool = False
    offset: int = 0
    read_calls: int = 0
    close_attempts: int = 0
    closed: bool = False

    def __post_init__(self) -> None:
        if self.headers is None:
            self.headers = (("Content-Length", str(len(self.body))),)
        self.headers = _Headers(self.headers)

    def geturl(self) -> str:
        return self.url

    def read(self, size: int) -> bytes | str:
        self.read_calls += 1
        if self.nonbytes_first_read and self.read_calls == 1:
            return "nonbytes"
        amount = size
        if self.maximum_read_bytes is not None:
            amount = min(amount, self.maximum_read_bytes)
        chunk = self.body[self.offset : self.offset + amount]
        self.offset += len(chunk)
        return chunk

    def close(self) -> None:
        self.close_attempts += 1
        self.closed = True
        if self.close_failure and self.close_attempts == 1:
            raise OSError("generated close refusal")


class _Headers:
    def __init__(self, values: Sequence[tuple[str, str]]) -> None:
        self._values = tuple((str(key), str(value)) for key, value in values)

    def get_all(self, name: str) -> list[str] | None:
        values = [
            value for key, value in self._values if key.casefold() == name.casefold()
        ]
        return values or None

    def raw_items(self) -> list[tuple[str, str]]:
        return list(self._values)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _MonitoredResponse:
    def __init__(
        self,
        response: BinaryIO,
        private_root: Path,
        snapshot: tuple[int, int, float],
        *,
        clock: Callable[[], float],
        rss_reader: Callable[[], int],
        disk_usage_reader: Callable[[Path], Any],
    ) -> None:
        self._response = response
        self._private_root = private_root
        self._snapshot = snapshot
        self._clock = clock
        self._rss_reader = rss_reader
        self._disk_usage_reader = disk_usage_reader
        self.status = getattr(response, "status", None)
        self.headers = getattr(response, "headers", None)
        self.body_bytes = 0

    def geturl(self) -> str:
        getter = getattr(self._response, "geturl", None)
        return getter() if callable(getter) else ""

    def read(self, size: int) -> bytes:
        if size <= 0 or size > MAX_STREAM_CHUNK_BYTES:
            raise HL2Refusal("HL2-RESOURCE")
        _enforce_resources(
            self._private_root,
            self._snapshot,
            clock=self._clock,
            rss_reader=self._rss_reader,
            disk_usage_reader=self._disk_usage_reader,
        )
        try:
            chunk = self._response.read(size)
        except Exception as exc:
            raise HL2Refusal("HL2-TRANSPORT") from exc
        if type(chunk) is not bytes:
            raise HL2Refusal("HL2-PAYLOAD")
        self.body_bytes += len(chunk)
        if self.body_bytes > MAX_NETWORK_BODY_BYTES:
            raise HL2Refusal("HL2-RESOURCE")
        return chunk


@dataclass
class DevelopmentResult:
    report: dict[str, Any]
    events: tuple[str, ...]
    marker_path: Path
    final_payload_path: Path
    output_path: Path
    opener_constructions: int
    requests: int
    response_closed: bool


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
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


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            while chunk := os.read(descriptor, 64 * 1024):
                digest.update(chunk)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise HL2Refusal("HL2-PROOF") from exc
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _read_bound_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        info = os.lstat(path)
        if (
            stat.S_ISLNK(info.st_mode)
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size > MAX_PUBLIC_OUTPUT_BYTES
            or _sha256_file(path) != expected_sha256
        ):
            raise HL2Refusal("HL2-PROOF")
        payload = path.read_bytes()
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda _value: (_ for _ in ()).throw(
                ValueError("non-finite JSON")
            ),
        )
    except (OSError, UnicodeError, ValueError) as exc:
        raise HL2Refusal("HL2-PROOF") from exc
    if not isinstance(value, dict):
        raise HL2Refusal("HL2-PROOF")
    return value


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_bound_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    proof = decision.get("green_request_proof")
    authorization = decision.get("authorization_after_decision_green")
    expected = {
        "decision_id": DECISION_ID,
        "request_id": REQUEST_ID,
        "maintainer_words": "continue",
    }
    if any(decision.get(key) != value for key, value in expected.items()):
        raise HL2Refusal("HL2-PROOF")
    if not isinstance(proof, dict) or proof.get("both_required_jobs_green") is not True:
        raise HL2Refusal("HL2-PROOF")
    if not isinstance(authorization, dict) or authorization.get(
        "implement_additive_standard_library_HL2_execution_adapter"
    ) is not True:
        raise HL2Refusal("HL2-PROOF")
    return decision


def verify_frozen_recovery(repo_root: str | Path | None = None) -> None:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    for relative, expected in FROZEN_RECOVERY_ARTIFACTS:
        if _sha256_file(root / relative) != expected:
            raise HL2Refusal("HL2-PROOF")
    recovery.load_green_recovery_decision(root)


def validate_activation(
    activation: Mapping[str, Any],
    evidence: ActivationEvidence,
    *,
    repo_root: str | Path | None = None,
    verify_artifacts: bool = True,
) -> None:
    if (
        activation.get("schema_name")
        != "neurodecodekit.dreyer_c5r_1_stage_h_l2_fixed_header_activation"
        or activation.get("activation_id") != "DREYER-C5R-1-HL2-ACT0"
        or activation.get("request_id") != REQUEST_ID
        or activation.get("decision_id") != DECISION_ID
        or activation.get("decision_commit") != GREEN_DECISION_COMMIT
        or activation.get("status")
        != "no_authority_record_effective_only_after_own_remote_green"
        or evidence.registered_execution_ordinal != 1
        or len(evidence.activation_commit) != 40
        or any(
            character not in "0123456789abcdef"
            for character in evidence.activation_commit
        )
        or any(
            value <= 0
            for value in (
                evidence.activation_ci_run_id,
                evidence.activation_base_job_id,
                evidence.activation_optional_job_id,
            )
        )
    ):
        raise HL2Refusal("HL2-PROOF")
    member = activation.get("exact_member")
    if not isinstance(member, dict) or member != {
        "path": stage_h.PREFLIGHT_PATH,
        "url": stage_h.PREFLIGHT_URL,
        "bytes": stage_h.PREFLIGHT_BYTES,
        "sha256": stage_h.PREFLIGHT_SHA256,
    }:
        raise HL2Refusal("HL2-PROOF")
    ordered = activation.get("ordered_execution_after_remote_green")
    if not isinstance(ordered, dict) or any(
        ordered.get(key) != value
        for key, value in {
            "registered_invocations_maximum": 1,
            "marker_before_opener_or_request": True,
            "real_HTTP_GET_requests_exact": 1,
            "fixed_header_semantic_parses_maximum": 1,
            "retries": 0,
            "reruns": 0,
        }.items()
    ):
        raise HL2Refusal("HL2-PROOF")
    if verify_artifacts:
        root = Path(repo_root) if repo_root is not None else _repo_root()
        rows = activation.get("bound_implementation_artifacts")
        if not isinstance(rows, list) or not rows:
            raise HL2Refusal("HL2-PROOF")
        for row in rows:
            if not isinstance(row, dict) or _sha256_file(root / row["path"]) != row.get(
                "sha256"
            ):
                raise HL2Refusal("HL2-PROOF")


def load_activation(
    evidence: ActivationEvidence,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    activation = _read_bound_json(
        root / ACTIVATION_RELATIVE_PATH, evidence.activation_sha256
    )
    validate_activation(activation, evidence, repo_root=root)
    return activation


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _ensure_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise HL2Refusal("HL2-RESOURCE")


def _lstat_directory(path: Path) -> None:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise HL2Refusal("HL2-PATH") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise HL2Refusal("HL2-PATH")


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _private_root(workspace: Path) -> Path:
    _lstat_directory(workspace)
    current = workspace
    for part in PRIVATE_ROOT_RELATIVE_PATH.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            _lstat_directory(current)
        else:
            try:
                os.mkdir(current, 0o700)
                _fsync_directory(current.parent)
            except OSError as exc:
                raise HL2Refusal("HL2-PATH") from exc
            _lstat_directory(current)
    return current


def _allocated_tree_bytes(root: Path) -> int:
    total = 0
    if not root.exists():
        return 0
    for directory, names, files in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        _lstat_directory(directory_path)
        for name in (*names, *files):
            path = directory_path / name
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode):
                raise HL2Refusal("HL2-PATH")
            total += int(getattr(info, "st_blocks", 0)) * 512
    return total


def _resource_snapshot(
    workspace: Path,
    private_root: Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any],
    rss_reader: Callable[[], int],
    clock: Callable[[], float],
) -> tuple[int, int, float]:
    _ensure_thread_environment(environ)
    free = int(disk_usage_reader(workspace).free)
    rss = int(rss_reader())
    started = float(clock())
    if free < MINIMUM_FREE_DISK_BYTES or rss > MAX_PEAK_RSS_BYTES:
        raise HL2Refusal("HL2-RESOURCE")
    if _allocated_tree_bytes(private_root) > MAX_INCREMENTAL_DISK_BYTES:
        raise HL2Refusal("HL2-RESOURCE")
    return free, rss, started


def _enforce_resources(
    private_root: Path,
    snapshot: tuple[int, int, float],
    *,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    disk_usage_reader: Callable[[Path], Any],
) -> dict[str, Any]:
    free_before, peak_before, started = snapshot
    runtime = float(clock()) - started
    peak = max(peak_before, int(rss_reader()))
    free_after = int(disk_usage_reader(private_root).free)
    allocated = _allocated_tree_bytes(private_root)
    if (
        not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or peak > MAX_PEAK_RSS_BYTES
        or free_before - free_after > MAX_INCREMENTAL_DISK_BYTES
        or allocated > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise HL2Refusal("HL2-RESOURCE")
    return {
        "runtime_seconds": runtime,
        "peak_process_tree_RSS_bytes": peak,
        "free_disk_bytes_before": free_before,
        "free_disk_bytes_after": free_after,
        "private_allocated_bytes": allocated,
    }


def _write_exclusive(path: Path, payload: bytes, *, mode: int = 0o600) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            offset = 0
            while offset < len(payload):
                offset += os.write(descriptor, payload[offset:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _fsync_directory(path.parent)
    except OSError as exc:
        raise HL2Refusal("HL2-MARKER") from exc


def _build_request(spec: stage_h.PreflightSpec) -> urllib.request.Request:
    request = urllib.request.Request(
        spec.url,
        headers={
            "Accept-Encoding": "identity",
            "User-Agent": "NeuroDecodeKit-DREYER-C5R-1-HL2/0.1",
        },
        method="GET",
    )
    headers = {key.casefold(): value for key, value in request.header_items()}
    if (
        request.get_method() != "GET"
        or request.full_url != spec.url
        or headers
        != {
            "accept-encoding": "identity",
            "user-agent": "NeuroDecodeKit-DREYER-C5R-1-HL2/0.1",
        }
    ):
        raise HL2Refusal("HL2-TRANSPORT")
    return request


def build_live_opener() -> Callable[[urllib.request.Request, float], BinaryIO]:
    """Build one proxy-free verified-TLS opener with redirects disabled."""

    context = ssl.create_default_context()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        _NoRedirect,
        urllib.request.HTTPSHandler(context=context),
    )

    def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
        try:
            return opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            return exc
        except Exception as exc:
            raise HL2Refusal("HL2-TRANSPORT") from exc

    return open_once


def _validate_transport(response: Any, spec: stage_h.PreflightSpec) -> None:
    getter = getattr(response, "geturl", None)
    headers = getattr(response, "headers", None)
    raw_items = getattr(headers, "raw_items", None)
    if (
        getattr(response, "status", None) != 200
        or not callable(getter)
        or getter() != spec.url
        or not callable(raw_items)
    ):
        raise HL2Refusal("HL2-TRANSPORT")
    critical: dict[str, str] = {}
    for raw_name, raw_value in raw_items():
        name = str(raw_name).strip().casefold()
        value = str(raw_value).strip()
        if name not in {"content-length", "content-encoding", "transfer-encoding"}:
            continue
        if name in critical:
            raise HL2Refusal("HL2-TRANSPORT")
        critical[name] = value
    if critical != {"content-length": str(spec.bytes)}:
        raise HL2Refusal("HL2-TRANSPORT")


def _stream_with_single_summary(
    response: Any,
    spec: stage_h.PreflightSpec,
    destination: Path,
) -> tuple[dict[str, Any], EDFHeaderSummary]:
    captured: list[EDFHeaderSummary] = []
    original = stage_h.parse_edf_fixed_header

    def capture(payload: bytes) -> EDFHeaderSummary:
        summary = original(payload)
        captured.append(summary)
        return summary

    with _PARSER_CAPTURE_LOCK:
        stage_h.parse_edf_fixed_header = capture
        try:
            result = stage_h.stream_verified_preflight(response, spec, destination)
        except stage_h.StageHRefusal as exc:
            raise HL2Refusal("HL2-PAYLOAD") from exc
        finally:
            stage_h.parse_edf_fixed_header = original
    if len(captured) != 1:
        raise HL2Refusal("HL2-HEADER")
    return result, captured[0]


def _validate_geometry(summary: EDFHeaderSummary, expected_bytes: int) -> None:
    total = summary.header_bytes + summary.record_count * 2 * sum(
        summary.samples_per_record
    )
    if total != expected_bytes:
        raise HL2Refusal("HL2-HEADER")


def _remove_owned_file(path: Path, manifest: InvocationManifest) -> None:
    if not manifest.owns(path):
        raise HL2Refusal("HL2-PATH")
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise HL2Refusal("HL2-TEARDOWN")
    path.unlink()


def _cleanup_staging(staging: Path, manifest: InvocationManifest) -> int:
    if not manifest.owns(staging):
        return 0
    attempts = 0
    try:
        info = os.lstat(staging)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise HL2Refusal("HL2-TEARDOWN")
        for child in tuple(staging.iterdir()):
            manifest.record(child)
            _remove_owned_file(child, manifest)
            attempts += 1
        os.rmdir(staging)
        attempts += 1
    except FileNotFoundError:
        return attempts
    except OSError as exc:
        raise HL2Refusal("HL2-TEARDOWN") from exc
    return attempts


def _promote_no_replace(
    source: Path,
    destination: Path,
    manifest: InvocationManifest,
) -> None:
    if destination.exists() or destination.is_symlink() or not manifest.owns(source):
        raise HL2Refusal("HL2-PUBLICATION")
    try:
        source_info = os.lstat(source)
        if (
            stat.S_ISLNK(source_info.st_mode)
            or not stat.S_ISREG(source_info.st_mode)
            or source_info.st_nlink != 1
        ):
            raise HL2Refusal("HL2-PUBLICATION")
        os.link(source, destination, follow_symlinks=False)
        manifest.record(destination)
        source.unlink()
        manifest.created.remove(source)
        _fsync_directory(destination.parent)
        destination_info = os.lstat(destination)
        if destination_info.st_nlink != 1:
            raise HL2Refusal("HL2-PUBLICATION")
    except (OSError, HL2Refusal) as exc:
        if destination.exists() and not destination.is_symlink() and manifest.owns(
            destination
        ):
            _remove_owned_file(destination, manifest)
        raise HL2Refusal("HL2-PUBLICATION") from exc


def _operation_counters(*, generated_only: bool) -> dict[str, int]:
    return {
        "raw_data_reads": 0,
        "real_cache_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "real_or_private_path_operations": 0,
        "real_HTTP_GET_requests": 0,
        "real_response_opens": 0,
        "real_network_body_bytes": 0,
        "real_payload_SHA256_passes": 0,
        "real_fixed_header_reads": 0,
        "real_fixed_header_semantic_parses": 0,
        "annotation_semantic_reads": 0,
        "signal_sample_semantic_reads": 0,
        "target_or_label_reads": 0,
        "model_training_inference_prediction_target_delivery_or_score_operations": 0,
        "provider_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _public_report(
    *,
    route: str,
    refusal_code: str | None,
    sensor_contract: Mapping[str, Any] | None,
    resources: Mapping[str, Any],
    counters: Mapping[str, int],
    evidence: ActivationEvidence,
    marker_bytes: int,
    response_closed: bool,
    cleanup_attempts: int,
    cleanup_complete: bool,
    payload_retained: bool,
    generated_only: bool,
) -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_l2_fixed_header_result",
        "schema_version": SCHEMA_VERSION,
        "request_id": REQUEST_ID,
        "decision_id": DECISION_ID,
        "route": route,
        "refusal_code": refusal_code,
        "exact_member": {
            "path": stage_h.PREFLIGHT_PATH,
            "bytes": stage_h.PREFLIGHT_BYTES,
            "sha256": stage_h.PREFLIGHT_SHA256,
        },
        "sensor_contract": dict(sensor_contract) if sensor_contract else None,
        "activation_evidence": {
            "activation_commit": evidence.activation_commit,
            "activation_CI_run_id": evidence.activation_ci_run_id,
            "activation_base_job_id": evidence.activation_base_job_id,
            "activation_optional_job_id": evidence.activation_optional_job_id,
            "registered_execution_ordinal": evidence.registered_execution_ordinal,
        },
        "resources": {
            **dict(resources),
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 0,
            "runtime_cap_seconds": MAX_RUNTIME_SECONDS,
            "peak_process_tree_RSS_cap_bytes": MAX_PEAK_RSS_BYTES,
            "network_body_cap_bytes": MAX_NETWORK_BODY_BYTES,
            "incremental_disk_cap_bytes": MAX_INCREMENTAL_DISK_BYTES,
            "public_output_cap_bytes": MAX_PUBLIC_OUTPUT_BYTES,
            "stream_chunk_cap_bytes": MAX_STREAM_CHUNK_BYTES,
            "producer_causal": None,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "transport": {
            "verified_TLS": True,
            "Accept_Encoding": "identity",
            "proxies": 0,
            "redirects": 0,
            "retries": 0,
            "ranges": 0,
            "resume": 0,
            "TLS_and_header_bytes": "unavailable_to_standard_library",
        },
        "operation_counters": dict(counters),
        "teardown": {
            "marker_bytes": marker_bytes,
            "response_closed": response_closed,
            "cleanup_attempts": cleanup_attempts,
            "cleanup_complete": cleanup_complete,
            "payload_retained": payload_retained,
        },
        "generated_only": generated_only,
        "geometry_available": False,
        "warnings": [
            "fixed_header_only_no_annotation_or_signal_sample_read",
            "sensor_labels_are_not_geometry",
            "end_to_end_latency_not_measured",
            "no_decoding_or_scientific_claim",
        ],
        "claim_boundary": {
            "scientific_claim_established": False,
            "neural_information_established": False,
            "decoding_established": False,
            "unseen_person_generalization_established": False,
            "EEG_beyond_peripheral_controls_established": False,
            "causal_live_decoding_established": False,
            "hardware_or_clinical_value_established": False,
        },
    }


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if report.get("route") not in {"DREYER-H1", "DREYER-H0"}:
        raise HL2Refusal("HL2-PUBLICATION")
    counters = report.get("operation_counters")
    claims = report.get("claim_boundary")
    if not isinstance(counters, dict) or not isinstance(claims, dict):
        raise HL2Refusal("HL2-PUBLICATION")
    for key in (
        "annotation_semantic_reads",
        "signal_sample_semantic_reads",
        "target_or_label_reads",
        "model_training_inference_prediction_target_delivery_or_score_operations",
        "provider_calls",
        "stream_device_or_hardware_operations",
        "release_operations",
        "scientific_claim_upgrades",
    ):
        if counters.get(key) != 0:
            raise HL2Refusal("HL2-PUBLICATION")
    if any(value is not False for value in claims.values()):
        raise HL2Refusal("HL2-PUBLICATION")
    payload = _canonical_json_bytes(report)
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise HL2Refusal("HL2-PUBLICATION")


def _publish_report(path: Path, report: Mapping[str, Any]) -> None:
    _validate_public_report(report)
    if path.exists() or path.is_symlink():
        raise HL2Refusal("HL2-PUBLICATION")
    _write_exclusive(path, _canonical_json_bytes(report), mode=0o644)


def _execute_after_activation(
    workspace: Path,
    output_path: Path,
    evidence: ActivationEvidence,
    opener_factory: Callable[[], Callable[[urllib.request.Request, float], BinaryIO]],
    spec: stage_h.PreflightSpec,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any],
    rss_reader: Callable[[], int],
    clock: Callable[[], float],
    generated_only: bool,
    case: str | None = None,
) -> DevelopmentResult:
    root = workspace.absolute()
    private_root = _private_root(root)
    snapshot = _resource_snapshot(
        root,
        private_root,
        environ=environ,
        disk_usage_reader=disk_usage_reader,
        rss_reader=rss_reader,
        clock=clock,
    )
    marker = private_root / CONSUMED_MARKER_NAME
    staging = private_root / STAGING_DIRECTORY_NAME
    staged_payload = staging / STAGING_PAYLOAD_NAME
    final_payload = private_root / PRIVATE_PAYLOAD_NAME
    if output_path.exists() or output_path.is_symlink():
        raise HL2Refusal("HL2-PUBLICATION")
    if marker.exists() or marker.is_symlink():
        raise HL2Refusal("HL2-MARKER")
    if staging.exists() or staging.is_symlink():
        raise HL2Refusal("HL2-PATH")
    if final_payload.exists() or final_payload.is_symlink():
        raise HL2Refusal("HL2-PUBLICATION")
    marker_payload = _canonical_json_bytes(
        {
            "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_l2_consumed",
            "schema_version": SCHEMA_VERSION,
            "request_id": REQUEST_ID,
            "activation_commit": evidence.activation_commit,
            "registered_execution_ordinal": evidence.registered_execution_ordinal,
            "attempt_consumed": True,
            "rerun_allowed": False,
        }
    )
    _write_exclusive(marker, marker_payload)
    manifest = InvocationManifest(private_root)
    manifest.record(marker)
    events = ["marker_durable", "transaction_entered"]
    opener_constructions = 0
    requests = 0
    response: BinaryIO | None = None
    monitored: _MonitoredResponse | None = None
    response_closed = False
    refusal: HL2Refusal | None = None
    sensor_contract: Mapping[str, Any] | None = None
    accepted = False
    cleanup_attempts = 0
    counters = _operation_counters(generated_only=generated_only)
    resources: dict[str, Any] = {
        "runtime_seconds": 0.0,
        "peak_process_tree_RSS_bytes": snapshot[1],
        "free_disk_bytes_before": snapshot[0],
        "free_disk_bytes_after": snapshot[0],
        "private_allocated_bytes": len(marker_payload),
    }
    step_code = "HL2-PATH"
    try:
        if case == "staging_create_refusal":
            raise HL2Refusal(step_code)
        os.mkdir(staging, 0o700)
        _fsync_directory(private_root)
        manifest.record(staging)
        events.append("staging_created")

        step_code = "HL2-TRANSPORT"
        if case == "opener_factory_refusal":
            raise HL2Refusal(step_code)
        opener = opener_factory()
        opener_constructions += 1
        events.append("opener_constructed")
        if case == "request_factory_refusal":
            raise HL2Refusal(step_code)
        request = _build_request(spec)
        events.append("request_constructed")
        if case == "response_open_refusal":
            raise HL2Refusal(step_code)
        if not generated_only:
            counters["real_HTTP_GET_requests"] = 1
        response = opener(request, MAX_RUNTIME_SECONDS)
        requests += 1
        if not generated_only:
            counters["real_response_opens"] = 1
            counters["real_or_private_path_operations"] = 1
        events.append("response_opened")
        _validate_transport(response, spec)
        monitored = _MonitoredResponse(
            response,
            private_root,
            snapshot,
            clock=clock,
            rss_reader=rss_reader,
            disk_usage_reader=disk_usage_reader,
        )
        step_code = "HL2-PAYLOAD"
        stream_result, summary = _stream_with_single_summary(
            monitored,
            spec,
            staged_payload,
        )
        manifest.record(staged_payload)
        step_code = "HL2-HEADER"
        _validate_geometry(summary, spec.bytes)
        sensor_contract = stream_result["sensor_contract"]
        events.append("payload_verified")

        step_code = "HL2-TEARDOWN"
        response.close()
        response = None
        response_closed = True
        events.append("response_closed")

        resources = _enforce_resources(
            private_root,
            snapshot,
            clock=clock,
            rss_reader=rss_reader,
            disk_usage_reader=disk_usage_reader,
        )
        step_code = "HL2-PUBLICATION"
        if case == "promotion_destination_race":
            final_payload.write_bytes(b"foreign")
        _promote_no_replace(staged_payload, final_payload, manifest)
        accepted = True
        events.append("payload_promoted")
    except HL2Refusal as exc:
        refusal = exc
    except Exception:
        refusal = HL2Refusal(step_code)
    finally:
        if response is not None:
            try:
                response.close()
                response_closed = True
                events.append("response_closed")
            except Exception:
                refusal = HL2Refusal("HL2-TEARDOWN")
                accepted = False
        try:
            cleanup_attempts += _cleanup_staging(staging, manifest)
            events.append("cleanup_complete")
        except HL2Refusal as exc:
            refusal = exc
            accepted = False
        if refusal is not None and final_payload.exists() and manifest.owns(final_payload):
            try:
                _remove_owned_file(final_payload, manifest)
                cleanup_attempts += 1
            except HL2Refusal:
                refusal = HL2Refusal("HL2-TEARDOWN")
        try:
            resources = _enforce_resources(
                private_root,
                snapshot,
                clock=clock,
                rss_reader=rss_reader,
                disk_usage_reader=disk_usage_reader,
            )
        except HL2Refusal as exc:
            refusal = exc
            accepted = False

    if monitored is not None and not generated_only:
        counters["real_network_body_bytes"] = monitored.body_bytes
        if monitored.body_bytes:
            counters["raw_data_reads"] = 1
    route = "DREYER-H1" if refusal is None and accepted else "DREYER-H0"
    if route == "DREYER-H1" and not generated_only:
        counters["real_payload_SHA256_passes"] = 1
        counters["real_fixed_header_reads"] = 1
        counters["real_fixed_header_semantic_parses"] = 1
    report = _public_report(
        route=route,
        refusal_code=refusal.code if refusal else None,
        sensor_contract=sensor_contract if route == "DREYER-H1" else None,
        resources=resources,
        counters=counters,
        evidence=evidence,
        marker_bytes=len(marker_payload),
        response_closed=response_closed,
        cleanup_attempts=cleanup_attempts,
        cleanup_complete=not staging.exists(),
        payload_retained=final_payload.exists() and route == "DREYER-H1",
        generated_only=generated_only,
    )
    if case == "publication_destination_race":
        output_path.write_bytes(b"foreign")
    if case == "public_output_cap":
        report["warnings"] = ["x" * MAX_PUBLIC_OUTPUT_BYTES]
    try:
        _publish_report(output_path, report)
    except HL2Refusal:
        if final_payload.exists() and manifest.owns(final_payload):
            _remove_owned_file(final_payload, manifest)
        raise
    return DevelopmentResult(
        report=report,
        events=tuple(events),
        marker_path=marker,
        final_payload_path=final_payload,
        output_path=output_path,
        opener_constructions=opener_constructions,
        requests=requests,
        response_closed=response_closed,
    )


def _generated_environment() -> dict[str, str]:
    return {key: "1" for key in THREAD_ENV_KEYS}


def _generated_labels() -> tuple[str, ...]:
    return stage_h.EXPECTED_EEG_LABELS + (
        "EOG-VU",
        "EOG-VD",
        "EOG-H",
        "EMG-LH",
        "EMG-RH",
        "EDF Annotations",
    )


def _generated_body(
    *,
    wrong_roster: bool = False,
    wrong_sampling_rate: bool = False,
    wrong_geometry: bool = False,
) -> bytes:
    labels = list(_generated_labels())
    if wrong_roster:
        labels[0] = "UNKNOWN"
    body = recovery._generated_body(  # noqa: SLF001
        labels=labels,
        sampling_rate_hz=511 if wrong_sampling_rate else 512,
        wrong_geometry=wrong_geometry,
    )
    return body


def _generated_response_and_spec(
    case: str | None,
) -> tuple[GeneratedResponse, stage_h.PreflightSpec]:
    body = _generated_body(
        wrong_roster=case == "wrong_sensor_roster",
        wrong_sampling_rate=case == "wrong_sampling_rate",
        wrong_geometry=case == "header_payload_geometry",
    )
    if case == "malformed_fixed_header":
        body = b"BROKEN  " + body[8:]
    expected = body
    response_body = body
    if case == "short_body":
        response_body = body[:-1]
    elif case == "oversized_body":
        response_body = body + b"x"
    sha256 = hashlib.sha256(expected).hexdigest()
    if case == "wrong_payload_hash":
        sha256 = "0" * 64
    url = "https://generated.invalid/dreyer-hl2.edf"
    spec = stage_h.PreflightSpec(url, "generated/dreyer-hl2.edf", len(expected), sha256)
    headers: Sequence[tuple[str, str]] = (("Content-Length", str(len(expected))),)
    if case == "transfer_encoding":
        headers += (("Transfer-Encoding", "chunked"),)
    elif case == "duplicate_content_length":
        headers += (("Content-Length", str(len(expected))),)
    elif case == "content_encoding":
        headers += (("Content-Encoding", "gzip"),)
    response = GeneratedResponse(
        response_body,
        url="https://generated.invalid/other.edf"
        if case == "final_URL_drift"
        else url,
        status=404 if case == "HTTP_status_drift" else 200,
        headers=headers,
        nonbytes_first_read=case == "nonbytes_body",
        close_failure=case == "response_close_failure",
    )
    return response, spec


def _generated_evidence() -> ActivationEvidence:
    return ActivationEvidence(
        activation_sha256="0" * 64,
        activation_commit="1" * 40,
        activation_ci_run_id=1,
        activation_base_job_id=1,
        activation_optional_job_id=1,
    )


def run_generated_case(
    workspace: str | Path,
    *,
    case: str = "valid_H1",
) -> DevelopmentResult:
    """Exercise one adapter case without activation, network, or real data."""

    if case not in GENERATED_TRANSACTION_CASES:
        raise ValueError("unknown H-L2 generated case")
    root = Path(workspace).absolute()
    root.mkdir(parents=True, exist_ok=True)
    private_root = _private_root(root)
    output = root / "generated-hl2-result.v0.json"
    marker = private_root / CONSUMED_MARKER_NAME
    staging = private_root / STAGING_DIRECTORY_NAME
    final_payload = private_root / PRIVATE_PAYLOAD_NAME
    if case == "preexisting_public_result":
        output.write_bytes(b"foreign")
    if case in {"preexisting_consumed_marker", "consumed_rerun"}:
        marker.write_bytes(b"foreign")
    if case == "occupied_staging_name":
        staging.mkdir()
    if case == "preexisting_final_payload":
        final_payload.write_bytes(b"foreign")
    response, spec = _generated_response_and_spec(case)
    constructions = 0

    def opener_factory() -> Callable[[urllib.request.Request, float], BinaryIO]:
        nonlocal constructions
        constructions += 1

        def open_once(_request: urllib.request.Request, _timeout: float) -> BinaryIO:
            return response  # type: ignore[return-value]

        return open_once

    environ = _generated_environment()
    if case == "missing_thread_cap":
        environ = {}

    disk_calls = 0

    def disk_reader(path: Path) -> Any:
        nonlocal disk_calls
        disk_calls += 1
        usage = shutil.disk_usage(path)
        if case == "low_free_disk":
            return type("Usage", (), {"free": 0})()
        if case == "incremental_disk_cap" and disk_calls > 1:
            return type("Usage", (), {"free": usage.free - MAX_INCREMENTAL_DISK_BYTES - 1})()
        return usage

    started = time.monotonic()
    clock_calls = 0

    def clock() -> float:
        nonlocal clock_calls
        clock_calls += 1
        if case == "runtime_cap" and clock_calls > 1:
            return started + MAX_RUNTIME_SECONDS + 1
        return started if case == "runtime_cap" else time.monotonic()

    def rss_reader() -> int:
        return MAX_PEAK_RSS_BYTES + 1 if case == "RSS_cap" else 0

    result = _execute_after_activation(
        root,
        output,
        _generated_evidence(),
        opener_factory,
        spec,
        environ=environ,
        disk_usage_reader=disk_reader,
        rss_reader=rss_reader,
        clock=clock,
        generated_only=True,
        case=case,
    )
    result.opener_constructions = constructions
    return result


def _logical_tree_bytes(root: Path) -> int:
    total = 0
    for directory, _names, files in os.walk(root, followlinks=False):
        for name in files:
            path = Path(directory) / name
            info = os.lstat(path)
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
                raise HL2Refusal("HL2-PROOF")
            total += info.st_size
    return total


def _stable_replay_digest(report: Mapping[str, Any]) -> str:
    stable = {
        key: report[key]
        for key in (
            "route",
            "refusal_code",
            "exact_member",
            "sensor_contract",
            "transport",
            "operation_counters",
            "warnings",
            "claim_boundary",
        )
    }
    return hashlib.sha256(_canonical_json_bytes(stable)).hexdigest()


def run_generated_qualification() -> dict[str, Any]:
    """Run the complete generated adapter matrix without real or network access."""

    if set(GENERATED_TRANSACTION_CASES) != (
        {"valid_H1"}
        | GENERATED_PRECONSUMPTION_REFUSALS
        | GENERATED_POSTMARKER_H0_CASES
        | GENERATED_PUBLICATION_REFUSALS
    ):
        raise HL2Refusal("HL2-PROOF")
    started = time.monotonic()
    peak_before = _peak_rss_bytes()
    h1 = 0
    h0 = 0
    raised = 0
    generated_bytes = 0
    maximum_attempt_bytes = 0
    replay_digests: list[str] = []
    refusal_codes: dict[str, str] = {}
    attempts = ("valid_H1",) + GENERATED_TRANSACTION_CASES
    for ordinal, case in enumerate(attempts, start=1):
        with tempfile.TemporaryDirectory(prefix=f"ndk-hl2-q{ordinal:02d}-") as name:
            root = Path(name)
            try:
                result = run_generated_case(root, case=case)
            except HL2Refusal as exc:
                if case not in (
                    GENERATED_PRECONSUMPTION_REFUSALS
                    | GENERATED_PUBLICATION_REFUSALS
                ):
                    raise HL2Refusal("HL2-PROOF") from exc
                raised += 1
                refusal_codes[f"{ordinal:02d}:{case}"] = exc.code
            else:
                expected_route = (
                    "DREYER-H1" if case == "valid_H1" else "DREYER-H0"
                )
                if result.report["route"] != expected_route:
                    raise HL2Refusal("HL2-PROOF")
                if any(result.report["operation_counters"].values()) or any(
                    result.report["claim_boundary"].values()
                ):
                    raise HL2Refusal("HL2-PROOF")
                inspect_public_result(result.output_path)
                if expected_route == "DREYER-H1":
                    h1 += 1
                    replay_digests.append(_stable_replay_digest(result.report))
                else:
                    h0 += 1
                    refusal_codes[f"{ordinal:02d}:{case}"] = result.report[
                        "refusal_code"
                    ]
            attempt_bytes = _logical_tree_bytes(root)
            generated_bytes += attempt_bytes
            maximum_attempt_bytes = max(maximum_attempt_bytes, attempt_bytes)
        if Path(name).exists():
            raise HL2Refusal("HL2-TEARDOWN")
    runtime = time.monotonic() - started
    peak = max(peak_before, _peak_rss_bytes())
    if (
        h1 != 2
        or h0 != len(GENERATED_POSTMARKER_H0_CASES)
        or raised
        != len(GENERATED_PRECONSUMPTION_REFUSALS)
        + len(GENERATED_PUBLICATION_REFUSALS)
        or len(set(replay_digests)) != 1
        or runtime > MAX_RUNTIME_SECONDS
        or peak > MAX_PEAK_RSS_BYTES
        or maximum_attempt_bytes > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise HL2Refusal("HL2-PROOF")
    return {
        "schema_name": (
            "neurodecodekit.dreyer_c5r_1_stage_h_l2_generated_qualification"
        ),
        "schema_version": SCHEMA_VERSION,
        "request_id": REQUEST_ID,
        "decision_id": DECISION_ID,
        "transaction_case_count": len(GENERATED_TRANSACTION_CASES),
        "attempt_count": len(attempts),
        "accepted_H1_count": h1,
        "aggregate_H0_count": h0,
        "raised_refusal_count": raised,
        "refusal_observation_count": h0 + raised,
        "refusal_codes": refusal_codes,
        "deterministic_H1_replay_sha256": replay_digests[0],
        "runtime_seconds": runtime,
        "peak_process_RSS_bytes": peak,
        "generated_logical_bytes_across_attempts": generated_bytes,
        "maximum_single_attempt_logical_bytes": maximum_attempt_bytes,
        "retained_generated_payload_bytes": 0,
        "network_bytes": 0,
        "real_or_private_operations": 0,
        "model_runs": 0,
        "training_runs": 0,
        "target_or_label_reads": 0,
        "scientific_claim_established": False,
    }


def execute_registered_preflight(
    evidence: ActivationEvidence,
    *,
    repo_root: str | Path | None = None,
    opener_factory: Callable[
        [], Callable[[urllib.request.Request, float], BinaryIO]
    ] = build_live_opener,
    environ: Mapping[str, str] | None = None,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> dict[str, Any]:
    """Execute the sole activation-bound real fixed-header invocation."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    root = root.expanduser().absolute()
    _lstat_directory(root)
    load_green_decision(root)
    verify_frozen_recovery(root)
    load_activation(evidence, root)
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip()
        status_result = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        raise HL2Refusal("HL2-PROOF") from exc
    if (
        head != evidence.activation_commit
        or status_result.returncode != 0
        or status_result.stdout.strip()
    ):
        raise HL2Refusal("HL2-PROOF")
    result = _execute_after_activation(
        root,
        root / PUBLIC_RESULT_RELATIVE_PATH,
        evidence,
        opener_factory,
        stage_h.REGISTERED_SPEC,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        rss_reader=rss_reader,
        clock=clock,
        generated_only=False,
    )
    return result.report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Inspect the activation-locked H-L2 plan without opening private paths."""

    load_green_decision(repo_root)
    verify_frozen_recovery(repo_root)
    return {
        "request_id": REQUEST_ID,
        "decision_id": DECISION_ID,
        "lane_id": LANE_ID,
        "status": "implementation_only_activation_absent",
        "green_decision": {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "exact_member": {
            "path": stage_h.PREFLIGHT_PATH,
            "bytes": stage_h.PREFLIGHT_BYTES,
            "sha256": stage_h.PREFLIGHT_SHA256,
        },
        "generated_transaction_cases": list(GENERATED_TRANSACTION_CASES),
        "activation_present": (Path(repo_root) if repo_root else _repo_root())
        .joinpath(ACTIVATION_RELATIVE_PATH)
        .exists(),
        "registered_execution_authority_now": False,
        "real_EDF_access_authority_now": False,
        "warnings": [
            "implementation_must_be_remotely_green_before_activation",
            "activation_must_be_remotely_green_before_execution",
            "no_real_EEG_accessed_by_plan",
        ],
    }


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Strictly inspect one aggregate H-L2 result without private access."""

    candidate = Path(path).expanduser().absolute()
    try:
        info = os.lstat(candidate)
        if (
            stat.S_ISLNK(info.st_mode)
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size > MAX_PUBLIC_OUTPUT_BYTES
        ):
            raise HL2Refusal("HL2-PUBLICATION")
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise HL2Refusal("HL2-PUBLICATION") from exc
    if not isinstance(value, dict):
        raise HL2Refusal("HL2-PUBLICATION")
    _validate_public_report(value)
    return value
