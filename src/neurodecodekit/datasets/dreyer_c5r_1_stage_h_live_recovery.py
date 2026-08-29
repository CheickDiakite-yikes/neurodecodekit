"""Generated-only transaction recovery for DREYER-C5R-1 H-L1R1."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import shutil
import stat
import sys
import threading
import time
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets.dreyer_c5r_1 import (
    EDFHeaderSummary,
    build_generated_edf_header,
)
from neurodecodekit.experiments import dreyer_c5r_1 as parent

SCHEMA_VERSION = "0.1.0"
PACKET_ID = "DREYER-C5R-1-HL1R1"
LANE_ID = "DREYER-C5R-1-HL"
GREEN_DECISION_COMMIT = "eaff077fc14b10886a6c26f45318ae649765e76d"
GREEN_DECISION_CI_RUN_ID = 33_247_816_266
GREEN_DECISION_BASE_JOB_ID = 99_088_241_281
GREEN_DECISION_OPTIONAL_JOB_ID = 99_088_241_372
DECISION_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_stage_h_live_recovery_decision.v0.json"
)
DECISION_SHA256 = "c6b6f3435d5cf1b5cbb3ce0328f60d6659410fdaf98104f234bb9db1b81d80b1"
FAILURE_PROOF_COMMIT = "a70fda0a808751c6057ed07117b7d22ee715a273"
REQUEST_PROOF_COMMIT = "8868a0866fd8f31bf7ba435e94b1b619314910ec"
PRIVATE_ROOT_RELATIVE_PATH = Path(
    ".codex_work/dreyer_c5r_1_stage_h_live/recovery-v1"
)
CASE_MARKER_NAME = "generated-case-consumed.v0.json"
STAGING_DIRECTORY_NAME = "staging-generated-case"
STAGING_PAYLOAD_NAME = "generated-payload.edf"
FINAL_PAYLOAD_NAME = "accepted-generated-payload.edf"
THREAD_ENV_KEYS = parent.THREAD_ENVIRONMENT
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_IO_BYTES = 8 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 16 * 1024**2
MAX_PUBLIC_OUTPUT_BYTES = 1024**2
MINIMUM_FREE_DISK_BYTES = 2 * MAX_INCREMENTAL_DISK_BYTES
GENERATED_URL = "https://generated.invalid/dreyer-hl1r1.edf"
REFUSAL_CODES = (
    "HL1R1-PROOF",
    "HL1R1-PATH",
    "HL1R1-MARKER",
    "HL1R1-TRANSPORT",
    "HL1R1-PAYLOAD",
    "HL1R1-HEADER",
    "HL1R1-RESOURCE",
    "HL1R1-TEARDOWN",
    "HL1R1-PUBLICATION",
    "HL1R1-ACTIVATION",
)
ORDERED_SUCCESSOR_REFUSAL_CASES = (
    "decision_record_drift",
    "failure_proof_drift",
    "implementation_record_drift",
    "stale_remote_main",
    "failed_base_job",
    "failed_optional_job",
    "shallow_checkout",
    "missing_thread_cap",
    "low_free_disk",
    "symlinked_workspace",
    "preexisting_public_result",
    "preexisting_consumed_marker",
    "occupied_staging_name",
    "foreign_cleanup_capability",
    "staging_create_refusal",
    "opener_factory_refusal",
    "opener_factory_unexpected_exception",
    "request_factory_refusal",
    "request_method_drift",
    "request_header_drift",
    "response_open_refusal",
    "response_open_unexpected_exception",
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
    "stream_runtime_cap",
    "stream_RSS_cap",
    "incremental_disk_cap",
    "promotion_destination_race",
    "response_close_failure",
    "publication_destination_race",
    "public_output_cap",
    "consumed_rerun",
)
PREMARKER_CASES = frozenset(ORDERED_SUCCESSOR_REFUSAL_CASES[:14]) | {
    "consumed_rerun"
}
PUBLICATION_REFUSAL_CASES = {
    "publication_destination_race",
    "public_output_cap",
}
LEGACY_ARTIFACTS = (
    (
        Path("src/neurodecodekit/datasets/dreyer_c5r_1_stage_h_live.py"),
        "cee137233c4625e13c78d8f9ce1d7e0f4b44e213dbe40e7a7608de7c3133196d",
    ),
    (
        Path("src/neurodecodekit/dreyer_c5r_1_stage_h_live_cli.py"),
        "3016bb0dacfa558e732a30b695fc653bc0ca965e1c957423eec25c71d4885a0f",
    ),
    (
        Path("tests/test_dreyer_c5r_1_stage_h_live.py"),
        "c1e14ebf20d62e5d214991b785b75666b899ad46c2a84b51a8d79beec659c54e",
    ),
)
_PARSER_CAPTURE_LOCK = threading.Lock()


class RecoveryRefusal(RuntimeError):
    """Sanitized refusal with an allowlisted public code and case."""

    def __init__(self, code: str, case: str) -> None:
        self.code = code if code in REFUSAL_CODES else "HL1R1-PROOF"
        self.case = (
            case if case in ORDERED_SUCCESSOR_REFUSAL_CASES else "decision_record_drift"
        )
        super().__init__(self.code)


@dataclass(frozen=True)
class ProofSnapshot:
    decision_sha256: str
    failure_proof_commit: str
    implementation_sha256: str
    remote_main_commit: str
    base_job_green: bool
    optional_job_green: bool
    shallow_checkout: bool


@dataclass
class InvocationManifest:
    """Lexical, no-follow inventory of paths created by one invocation."""

    private_root: Path
    created: list[Path] = field(default_factory=list)

    def _contained(self, path: Path) -> bool:
        return path == self.private_root or self.private_root in path.parents

    def record_created(self, path: Path) -> None:
        path = path.absolute()
        if not self._contained(path) or path in self.created:
            raise RecoveryRefusal("HL1R1-PATH", "foreign_cleanup_capability")
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode):
            raise RecoveryRefusal("HL1R1-PATH", "foreign_cleanup_capability")
        self.created.append(path)

    def assert_cleanup_capability(self, path: Path) -> None:
        path = path.absolute()
        if not self._contained(path) or path not in self.created:
            raise RecoveryRefusal("HL1R1-PATH", "foreign_cleanup_capability")


@dataclass
class GeneratedResponse:
    body: bytes
    url: str = GENERATED_URL
    status: int = 200
    headers: Sequence[tuple[str, str]] | None = None
    maximum_read_bytes: int | None = None
    nonbytes_first_read: bool = False
    close_failure: bool = False
    offset: int = 0
    read_calls: int = 0
    close_attempts: int = 0
    closed: bool = False

    def __post_init__(self) -> None:
        if self.headers is None:
            self.headers = (("Content-Length", str(len(self.body))),)

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
        self._values = tuple(values)

    def get_all(self, name: str) -> list[str] | None:
        values = [
            value
            for key, value in self._values
            if key.casefold() == name.casefold()
        ]
        return values or None

    def raw_items(self) -> list[tuple[str, str]]:
        return list(self._values)


@dataclass
class DevelopmentCaseResult:
    report: dict[str, Any]
    events: tuple[str, ...]
    opener_constructions: int
    requests: int
    response_closed: bool
    marker_path: Path
    output_path: Path
    final_payload_path: Path


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


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


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
        raise RecoveryRefusal("HL1R1-PROOF", "decision_record_drift") from exc
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = child
    return value


def _strict_json(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    return json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=lambda _value: (_ for _ in ()).throw(
            ValueError("non-finite JSON")
        ),
    )


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
            raise OSError("identity differs")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        try:
            payload = os.read(descriptor, MAX_PUBLIC_OUTPUT_BYTES + 1)
        finally:
            os.close(descriptor)
        value = _strict_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RecoveryRefusal("HL1R1-PROOF", "decision_record_drift") from exc
    if not isinstance(value, dict):
        raise RecoveryRefusal("HL1R1-PROOF", "decision_record_drift")
    return value


def load_green_recovery_decision(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact remotely green implementation decision."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _read_bound_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    authorization = decision.get("authorization_after_decision_green", {})
    proof = decision.get("green_request_proof", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_decision"
        or decision.get("packet_id") != PACKET_ID
        or decision.get("maintainer_words") != "continue"
        or proof.get("commit") != REQUEST_PROOF_COMMIT
        or proof.get("CI_run_id") != 33_234_406_143
        or proof.get("both_required_jobs_green") is not True
        or authorization.get("implement_additive_standard_library_successor")
        is not True
        or authorization.get("run_registered_successor_generated_qualification")
        is not False
        or authorization.get("make_real_HTTP_request") is not False
        or authorization.get("open_real_or_private_path") is not False
        or authorization.get("write_or_read_real_EDF") is not False
        or authorization.get("train_or_infer") is not False
        or authorization.get("create_prediction_deliver_target_or_score") is not False
    ):
        raise RecoveryRefusal("HL1R1-PROOF", "decision_record_drift")
    for relative, expected in LEGACY_ARTIFACTS:
        if _sha256_file(root / relative) != expected:
            raise RecoveryRefusal("HL1R1-PROOF", "failure_proof_drift")
    return decision


def _valid_proof_snapshot() -> ProofSnapshot:
    return ProofSnapshot(
        decision_sha256=DECISION_SHA256,
        failure_proof_commit=FAILURE_PROOF_COMMIT,
        implementation_sha256="f" * 64,
        remote_main_commit=GREEN_DECISION_COMMIT,
        base_job_green=True,
        optional_job_green=True,
        shallow_checkout=False,
    )


def validate_generated_proof_snapshot(snapshot: ProofSnapshot) -> None:
    """Validate generated proof wiring without reading a future activation."""

    if snapshot.decision_sha256 != DECISION_SHA256:
        raise RecoveryRefusal("HL1R1-PROOF", "decision_record_drift")
    if snapshot.failure_proof_commit != FAILURE_PROOF_COMMIT:
        raise RecoveryRefusal("HL1R1-PROOF", "failure_proof_drift")
    if snapshot.implementation_sha256 != "f" * 64:
        raise RecoveryRefusal("HL1R1-PROOF", "implementation_record_drift")
    if snapshot.remote_main_commit != GREEN_DECISION_COMMIT:
        raise RecoveryRefusal("HL1R1-PROOF", "stale_remote_main")
    if not snapshot.base_job_green:
        raise RecoveryRefusal("HL1R1-PROOF", "failed_base_job")
    if not snapshot.optional_job_green:
        raise RecoveryRefusal("HL1R1-PROOF", "failed_optional_job")
    if snapshot.shallow_checkout:
        raise RecoveryRefusal("HL1R1-PROOF", "shallow_checkout")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _generated_environment() -> dict[str, str]:
    return {key: "1" for key in THREAD_ENV_KEYS}


def _ensure_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise RecoveryRefusal("HL1R1-RESOURCE", "missing_thread_cap")


def _lstat_directory(path: Path, case: str = "symlinked_workspace") -> None:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise RecoveryRefusal("HL1R1-PATH", case) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise RecoveryRefusal("HL1R1-PATH", case)


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise RecoveryRefusal("HL1R1-PATH", "staging_create_refusal") from exc


def _create_private_root(workspace: Path) -> Path:
    if not workspace.is_absolute() or ".." in workspace.parts:
        raise RecoveryRefusal("HL1R1-PATH", "symlinked_workspace")
    _lstat_directory(workspace)
    current = workspace
    for part in PRIVATE_ROOT_RELATIVE_PATH.parts:
        candidate = current / part
        try:
            info = os.lstat(candidate)
        except FileNotFoundError:
            try:
                os.mkdir(candidate, 0o700)
                _fsync_directory(current)
                info = os.lstat(candidate)
            except OSError as exc:
                raise RecoveryRefusal(
                    "HL1R1-PATH", "staging_create_refusal"
                ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise RecoveryRefusal("HL1R1-PATH", "symlinked_workspace")
        current = candidate
    return current


def _write_exclusive(path: Path, payload: bytes, *, mode: int, case: str) -> None:
    _lstat_directory(path.parent, case)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, mode)
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("write made no progress")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        _fsync_directory(path.parent)
    except FileExistsError as exc:
        raise RecoveryRefusal("HL1R1-MARKER", case) from exc
    except OSError as exc:
        code = "HL1R1-PUBLICATION" if "publication" in case else "HL1R1-MARKER"
        raise RecoveryRefusal(code, case) from exc


def _allocated_tree_bytes(root: Path) -> int:
    total = 0
    try:
        for entry in os.scandir(root):
            info = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):
                raise OSError("symlink")
            if stat.S_ISREG(info.st_mode):
                if info.st_nlink != 1:
                    raise OSError("hardlink")
                total += int(getattr(info, "st_blocks", 0)) * 512 or info.st_size
            elif stat.S_ISDIR(info.st_mode):
                total += _allocated_tree_bytes(Path(entry.path))
            else:
                raise OSError("special path")
    except OSError as exc:
        raise RecoveryRefusal("HL1R1-PATH", "foreign_cleanup_capability") from exc
    return total


def _resource_snapshot(
    workspace: Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any],
    rss_reader: Callable[[], int],
    clock: Callable[[], float],
) -> tuple[int, int, float]:
    _ensure_thread_environment(environ)
    try:
        free = int(disk_usage_reader(workspace).free)
        rss = int(rss_reader())
        started = float(clock())
    except Exception as exc:
        raise RecoveryRefusal("HL1R1-RESOURCE", "low_free_disk") from exc
    if free < MINIMUM_FREE_DISK_BYTES:
        raise RecoveryRefusal("HL1R1-RESOURCE", "low_free_disk")
    if rss < 0 or rss > MAX_PEAK_RSS_BYTES or not math.isfinite(started):
        raise RecoveryRefusal("HL1R1-RESOURCE", "stream_RSS_cap")
    return free, rss, started


def _enforce_resources(
    private_root: Path,
    snapshot: tuple[int, int, float],
    *,
    case: str | None,
    disk_usage_reader: Callable[[Path], Any],
    rss_reader: Callable[[], int],
    clock: Callable[[], float],
) -> dict[str, Any]:
    free_before, rss_before, started = snapshot
    runtime = float(clock()) - started
    peak_rss = int(rss_reader())
    free_now = int(disk_usage_reader(private_root).free)
    allocated = _allocated_tree_bytes(private_root)
    if case == "stream_runtime_cap":
        runtime = MAX_RUNTIME_SECONDS + 1
    if case == "stream_RSS_cap":
        peak_rss = MAX_PEAK_RSS_BYTES + 1
    if case == "incremental_disk_cap":
        allocated = MAX_INCREMENTAL_DISK_BYTES + 1
    if (
        not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or peak_rss < 0
        or peak_rss > MAX_PEAK_RSS_BYTES
        or free_now < MINIMUM_FREE_DISK_BYTES
        or allocated > MAX_INCREMENTAL_DISK_BYTES
    ):
        mapped = case if case in {
            "stream_runtime_cap",
            "stream_RSS_cap",
            "incremental_disk_cap",
        } else "incremental_disk_cap"
        raise RecoveryRefusal("HL1R1-RESOURCE", mapped)
    return {
        "runtime_seconds": runtime,
        "peak_process_RSS_bytes": max(rss_before, peak_rss),
        "free_disk_bytes_before": free_before,
        "free_disk_bytes_after": free_now,
        "private_allocated_bytes": allocated,
    }


def _valid_labels() -> tuple[str, ...]:
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
    labels: Sequence[str] | None = None,
    sampling_rate_hz: int = 512,
    wrong_geometry: bool = False,
) -> bytes:
    header = build_generated_edf_header(
        _valid_labels() if labels is None else labels,
        sampling_rate_hz=sampling_rate_hz,
        record_count=1,
    )
    summary = stage_h.parse_edf_fixed_header(header)
    expected = summary.header_bytes + 2 * sum(summary.samples_per_record)
    suffix_bytes = expected - len(header) + (2 if wrong_geometry else 0)
    suffix = bytes((index * 17 + 29) % 256 for index in range(suffix_bytes))
    return header + suffix


def _response_and_spec(case: str | None) -> tuple[GeneratedResponse, stage_h.PreflightSpec]:
    labels: Sequence[str] | None = None
    sampling_rate = 512
    wrong_geometry = case == "header_payload_geometry"
    if case == "wrong_sensor_roster":
        labels = _valid_labels()[:-2] + ("MYSTERY", "EDF Annotations")
    if case == "wrong_sampling_rate":
        sampling_rate = 256
    body = _generated_body(
        labels=labels,
        sampling_rate_hz=sampling_rate,
        wrong_geometry=wrong_geometry,
    )
    if case == "malformed_fixed_header":
        body = b"BROKEN  " + body[8:]
    expected_body = body
    response_body = body
    if case == "short_body":
        response_body = body[:-1]
    elif case == "oversized_body":
        response_body = body + b"x"
    digest = _sha256_bytes(expected_body)
    if case == "wrong_payload_hash":
        digest = "0" * 64
    spec = stage_h.PreflightSpec(GENERATED_URL, "generated/dreyer.edf", len(body), digest)
    headers: Sequence[tuple[str, str]] = (("Content-Length", str(len(body))),)
    if case == "transfer_encoding":
        headers += (("Transfer-Encoding", "chunked"),)
    elif case == "duplicate_content_length":
        headers += (("Content-Length", str(len(body))),)
    elif case == "content_encoding":
        headers += (("Content-Encoding", "gzip"),)
    response = GeneratedResponse(
        response_body,
        url="https://generated.invalid/other.edf"
        if case == "final_URL_drift"
        else GENERATED_URL,
        status=404 if case == "HTTP_status_drift" else 200,
        headers=headers,
        maximum_read_bytes=97,
        nonbytes_first_read=case == "nonbytes_body",
        close_failure=case == "response_close_failure",
    )
    response.headers = _Headers(headers)  # type: ignore[assignment]
    return response, spec


def _validate_request(request: urllib.request.Request) -> None:
    headers = {key.casefold(): value for key, value in request.header_items()}
    if request.get_method() != "GET" or request.full_url != GENERATED_URL:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "request_method_drift")
    if headers != {
        "accept-encoding": "identity",
        "user-agent": "NeuroDecodeKit-DREYER-C5R-1-HL1R1/0.1",
    }:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "request_header_drift")


def _validate_response_transport(
    response: GeneratedResponse,
    spec: stage_h.PreflightSpec,
) -> None:
    if response.status != 200:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "HTTP_status_drift")
    if response.geturl() != spec.url:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "final_URL_drift")
    headers = response.headers
    if not hasattr(headers, "raw_items"):
        raise RecoveryRefusal("HL1R1-TRANSPORT", "transfer_encoding")
    critical: dict[str, str] = {}
    for raw_name, raw_value in headers.raw_items():
        name = str(raw_name).strip().casefold()
        value = str(raw_value).strip()
        if name not in {"content-length", "content-encoding", "transfer-encoding"}:
            continue
        if name in critical:
            raise RecoveryRefusal(
                "HL1R1-TRANSPORT", "duplicate_content_length"
            )
        critical[name] = value
    if "transfer-encoding" in critical:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "transfer_encoding")
    if "content-encoding" in critical:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "content_encoding")
    if critical != {"content-length": str(spec.bytes)}:
        raise RecoveryRefusal("HL1R1-TRANSPORT", "duplicate_content_length")


def _build_request(case: str | None) -> urllib.request.Request:
    if case == "request_factory_refusal":
        raise RecoveryRefusal("HL1R1-TRANSPORT", case)
    method = "POST" if case == "request_method_drift" else "GET"
    headers = {
        "Accept-Encoding": "gzip" if case == "request_header_drift" else "identity",
        "User-Agent": "NeuroDecodeKit-DREYER-C5R-1-HL1R1/0.1",
    }
    request = urllib.request.Request(GENERATED_URL, headers=headers, method=method)
    _validate_request(request)
    return request


def _stream_with_summary(
    response: GeneratedResponse,
    spec: stage_h.PreflightSpec,
    destination: Path,
    *,
    refusal_case: str | None,
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
            mapped_case = refusal_case or "wrong_payload_hash"
            code = "HL1R1-PAYLOAD"
            if mapped_case in {
                "HTTP_status_drift",
                "final_URL_drift",
                "transfer_encoding",
                "duplicate_content_length",
                "content_encoding",
            }:
                code = "HL1R1-TRANSPORT"
            elif mapped_case in {
                "malformed_fixed_header",
                "wrong_sensor_roster",
                "wrong_sampling_rate",
            }:
                code = "HL1R1-HEADER"
            raise RecoveryRefusal(code, mapped_case) from exc
        finally:
            stage_h.parse_edf_fixed_header = original
    if len(captured) != 1:
        raise RecoveryRefusal("HL1R1-HEADER", "malformed_fixed_header")
    return result, captured[0]


def _validate_geometry(summary: EDFHeaderSummary, payload_bytes: int) -> None:
    expected = summary.header_bytes + summary.record_count * 2 * sum(
        summary.samples_per_record
    )
    if expected != payload_bytes:
        raise RecoveryRefusal("HL1R1-HEADER", "header_payload_geometry")


def _remove_owned(path: Path, manifest: InvocationManifest) -> None:
    manifest.assert_cleanup_capability(path)
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise RecoveryRefusal("HL1R1-TEARDOWN", "response_close_failure") from exc
    if stat.S_ISLNK(info.st_mode):
        raise RecoveryRefusal("HL1R1-TEARDOWN", "response_close_failure")
    try:
        if stat.S_ISREG(info.st_mode) and info.st_nlink == 1:
            path.unlink()
        elif stat.S_ISDIR(info.st_mode):
            if any(os.scandir(path)):
                raise OSError("owned directory not empty")
            os.rmdir(path)
        else:
            raise OSError("owned path type differs")
    except OSError as exc:
        raise RecoveryRefusal("HL1R1-TEARDOWN", "response_close_failure") from exc


def _cleanup_transaction_paths(
    manifest: InvocationManifest,
    *,
    keep_final: bool,
) -> int:
    attempts = 0
    for path in reversed(manifest.created):
        if path.name == CASE_MARKER_NAME or (keep_final and path.name == FINAL_PAYLOAD_NAME):
            continue
        attempts += 1
        _remove_owned(path, manifest)
    return attempts


def _promote_no_replace(source: Path, destination: Path, manifest: InvocationManifest) -> None:
    if destination.exists() or destination.is_symlink():
        raise RecoveryRefusal("HL1R1-PUBLICATION", "promotion_destination_race")
    try:
        os.rename(source, destination)
        _fsync_directory(destination.parent)
    except OSError as exc:
        raise RecoveryRefusal(
            "HL1R1-PUBLICATION", "promotion_destination_race"
        ) from exc
    manifest.created.remove(source)
    manifest.record_created(destination)


def _report(
    *,
    route: str,
    refusal: RecoveryRefusal | None,
    sensor_contract: Mapping[str, Any] | None,
    resources: Mapping[str, Any],
    generated_input_bytes: int,
    marker_bytes: int,
    response_close_attempts: int,
    response_closed: bool,
    cleanup_attempts: int,
    cleanup_complete: bool,
    final_payload_retained: bool,
) -> dict[str, Any]:
    report = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_case",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "route": route,
        "refusal_code": refusal.code if refusal is not None else None,
        "refusal_case": refusal.case if refusal is not None else None,
        "sensor_contract": dict(sensor_contract) if sensor_contract else None,
        "resources": {
            **dict(resources),
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 0,
            "generated_input_bytes": generated_input_bytes,
            "public_output_bytes": 0,
            "generated_input_plus_output_bytes": 0,
            "marker_bytes": marker_bytes,
            "generated_input_plus_output_cap_bytes": MAX_GENERATED_IO_BYTES,
            "incremental_disk_cap_bytes": MAX_INCREMENTAL_DISK_BYTES,
            "public_output_cap_bytes": MAX_PUBLIC_OUTPUT_BYTES,
            "producer_causal": None,
            "required_context_seconds": None,
            "end_to_end_latency_measured": False,
        },
        "teardown": {
            "response_close_attempts": response_close_attempts,
            "response_closed": response_closed,
            "cleanup_attempts": cleanup_attempts,
            "cleanup_complete": cleanup_complete,
            "final_payload_retained": final_payload_retained,
        },
        "operation_counters": {
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "real_or_private_path_operations": 0,
            "HTTP_requests": 0,
            "network_bytes": 0,
            "real_EDF_payload_or_header_reads": 0,
            "annotation_signal_target_or_label_reads": 0,
            "model_training_inference_prediction_target_delivery_or_score_operations": 0,
            "provider_calls": 0,
            "stream_device_or_hardware_operations": 0,
            "release_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "warnings": [
            "generated_development_case_not_registered_qualification",
            "generated_fixture_has_no_scientific_value",
            "real_source_EDF_remains_closed",
            "end_to_end_latency_not_measured",
        ],
        "claim_boundary": {
            "engineering_capability": "generated_transaction_failure_containment",
            "scientific_claim_not_established": "real_EEG_neural_decoding_unseen_person_peripheral_adjusted_live_hardware_or_clinical_result",
        },
    }
    previous = -1
    for _ in range(8):
        payload = _canonical_json_bytes(report)
        report["resources"]["public_output_bytes"] = len(payload)
        report["resources"]["generated_input_plus_output_bytes"] = (
            generated_input_bytes + marker_bytes + len(payload)
        )
        if len(payload) == previous:
            break
        previous = len(payload)
    if (
        report["resources"]["generated_input_plus_output_bytes"]
        > MAX_GENERATED_IO_BYTES
    ):
        raise RecoveryRefusal("HL1R1-RESOURCE", "incremental_disk_cap")
    _validate_report(report)
    return report


def _validate_report(report: Mapping[str, Any]) -> None:
    expected = {
        "schema_name",
        "schema_version",
        "packet_id",
        "route",
        "refusal_code",
        "refusal_case",
        "sensor_contract",
        "resources",
        "teardown",
        "operation_counters",
        "warnings",
        "claim_boundary",
    }
    if set(report) != expected or report.get("route") not in {"DREYER-H1", "DREYER-H0"}:
        raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap")
    forbidden = {
        "patient",
        "recording",
        "date",
        "raw_header",
        "annotation",
        "sample",
        "target",
        "label",
        "private_path",
        "exception",
        "traceback",
        "reference",
    }

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for key, child in value.items():
                if str(key).casefold() in forbidden:
                    raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap")
                walk(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                walk(child)
        elif isinstance(value, float) and not math.isfinite(value):
            raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap")

    walk(report)


def _publish_report(path: Path, report: Mapping[str, Any], *, case: str | None) -> None:
    payload = _canonical_json_bytes(report)
    if case == "public_output_cap":
        payload += b" " * MAX_PUBLIC_OUTPUT_BYTES
    if len(payload) > MAX_PUBLIC_OUTPUT_BYTES:
        raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap")
    if case == "publication_destination_race":
        raise RecoveryRefusal("HL1R1-PUBLICATION", case)
    _write_exclusive(path, payload, mode=0o644, case="publication_destination_race")


def _proof_case(case: str) -> None:
    snapshot = _valid_proof_snapshot()
    values = snapshot.__dict__.copy()
    if case == "decision_record_drift":
        values["decision_sha256"] = "0" * 64
    elif case == "failure_proof_drift":
        values["failure_proof_commit"] = "0" * 40
    elif case == "implementation_record_drift":
        values["implementation_sha256"] = "0" * 64
    elif case == "stale_remote_main":
        values["remote_main_commit"] = "0" * 40
    elif case == "failed_base_job":
        values["base_job_green"] = False
    elif case == "failed_optional_job":
        values["optional_job_green"] = False
    elif case == "shallow_checkout":
        values["shallow_checkout"] = True
    validate_generated_proof_snapshot(ProofSnapshot(**values))


def _preconsumption_case_setup(
    workspace: Path,
    output_path: Path,
    private_root: Path,
    case: str | None,
) -> None:
    marker = private_root / CASE_MARKER_NAME
    staging = private_root / STAGING_DIRECTORY_NAME
    if case == "preexisting_public_result":
        output_path.write_bytes(b"foreign")
    if output_path.exists() or output_path.is_symlink():
        raise RecoveryRefusal("HL1R1-PUBLICATION", "preexisting_public_result")
    if case in {"preexisting_consumed_marker", "consumed_rerun"}:
        marker.write_bytes(b"foreign")
    if marker.exists() or marker.is_symlink():
        mapped = "consumed_rerun" if case == "consumed_rerun" else "preexisting_consumed_marker"
        raise RecoveryRefusal("HL1R1-MARKER", mapped)
    if case == "occupied_staging_name":
        staging.mkdir()
    if staging.exists() or staging.is_symlink():
        raise RecoveryRefusal("HL1R1-PATH", "occupied_staging_name")
    if case == "foreign_cleanup_capability":
        manifest = InvocationManifest(private_root)
        manifest.assert_cleanup_capability(workspace.parent / "foreign")


def run_development_case(
    workspace: str | Path,
    *,
    case: str | None = None,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    clock: Callable[[], float] = time.monotonic,
) -> DevelopmentCaseResult:
    """Exercise one generated unit case without consuming the qualification."""

    if case is not None and case not in ORDERED_SUCCESSOR_REFUSAL_CASES:
        raise ValueError("unknown generated development case")
    load_green_recovery_decision(repo_root)
    if case in ORDERED_SUCCESSOR_REFUSAL_CASES[:7]:
        _proof_case(case)
    validate_generated_proof_snapshot(_valid_proof_snapshot())
    root = Path(workspace).absolute()
    if case == "symlinked_workspace":
        link = root / "workspace-link"
        os.symlink(root, link)
        root = link
    effective_environ = _generated_environment() if environ is None else environ
    if case == "missing_thread_cap":
        effective_environ = {}
    effective_disk_reader = disk_usage_reader
    if case == "low_free_disk":
        def low_disk_reader(_path: Path) -> Any:
            return type("Usage", (), {"free": 0})()

        effective_disk_reader = low_disk_reader
    snapshot = _resource_snapshot(
        root,
        environ=effective_environ,
        disk_usage_reader=effective_disk_reader,
        rss_reader=rss_reader,
        clock=clock,
    )
    private_root = _create_private_root(root)
    output_path = root / "generated-case-result.v0.json"
    _preconsumption_case_setup(root, output_path, private_root, case)

    marker_path = private_root / CASE_MARKER_NAME
    staging = private_root / STAGING_DIRECTORY_NAME
    staged_payload = staging / STAGING_PAYLOAD_NAME
    final_payload = private_root / FINAL_PAYLOAD_NAME
    manifest = InvocationManifest(private_root)
    marker_payload = _canonical_json_bytes(
        {
            "schema_name": "neurodecodekit.dreyer_c5r_1_stage_h_live_recovery_case_consumed",
            "schema_version": SCHEMA_VERSION,
            "packet_id": PACKET_ID,
            "generated_development_case": case or "valid_H1",
            "registered_qualification_consumed": False,
            "rerun_allowed": False,
        }
    )
    _write_exclusive(marker_path, marker_payload, mode=0o600, case="preexisting_consumed_marker")
    manifest.record_created(marker_path)
    events = ["marker_durable", "transaction_entered"]
    response, spec = _response_and_spec(case)
    opener_constructions = 0
    requests = 0
    refusal: RecoveryRefusal | None = None
    sensor_contract: Mapping[str, Any] | None = None
    response_open = False
    accepted = False
    cleanup_attempts = 0
    resources: dict[str, Any] = {
        "runtime_seconds": 0.0,
        "peak_process_RSS_bytes": snapshot[1],
        "free_disk_bytes_before": snapshot[0],
        "free_disk_bytes_after": snapshot[0],
        "private_allocated_bytes": len(marker_payload),
    }
    step_code = "HL1R1-PATH"
    step_case = "staging_create_refusal"
    try:
        if case == "staging_create_refusal":
            raise RecoveryRefusal(step_code, step_case)
        os.mkdir(staging, 0o700)
        _fsync_directory(private_root)
        manifest.record_created(staging)
        events.append("staging_created")

        step_code = "HL1R1-TRANSPORT"
        step_case = "opener_factory_refusal"
        if case == "opener_factory_refusal":
            raise RecoveryRefusal(step_code, step_case)
        if case == "opener_factory_unexpected_exception":
            step_case = case
            raise ValueError("generated secret opener failure")
        opener_constructions += 1
        events.append("opener_constructed")

        step_case = "request_factory_refusal"
        request = _build_request(case)
        events.append("request_constructed")

        step_case = "response_open_refusal"
        if case == "response_open_refusal":
            raise RecoveryRefusal(step_code, step_case)
        if case == "response_open_unexpected_exception":
            step_case = case
            raise RuntimeError("generated secret response failure")
        _validate_request(request)
        requests += 1
        response_open = True
        events.append("response_opened")

        _validate_response_transport(response, spec)

        resources = _enforce_resources(
            private_root,
            snapshot,
            case=case,
            disk_usage_reader=effective_disk_reader,
            rss_reader=rss_reader,
            clock=clock,
        )
        step_code = "HL1R1-PAYLOAD"
        step_case = case or "wrong_payload_hash"
        stream_result, summary = _stream_with_summary(
            response,
            spec,
            staged_payload,
            refusal_case=case,
        )
        manifest.record_created(staged_payload)
        _validate_geometry(summary, spec.bytes)
        sensor_contract = stream_result["sensor_contract"]
        events.append("payload_verified")

        step_code = "HL1R1-TEARDOWN"
        step_case = "response_close_failure"
        response.close()
        response_open = False
        events.append("response_closed")

        step_code = "HL1R1-PUBLICATION"
        step_case = "promotion_destination_race"
        if case == "promotion_destination_race":
            raise RecoveryRefusal(step_code, step_case)
        _promote_no_replace(staged_payload, final_payload, manifest)
        accepted = True
        events.append("payload_promoted")
    except RecoveryRefusal as exc:
        refusal = exc
    except Exception:
        refusal = RecoveryRefusal(step_code, step_case)
    finally:
        if response_open or not response.closed:
            try:
                response.close()
                response_open = False
                events.append("response_closed")
            except Exception:
                refusal = RecoveryRefusal(
                    "HL1R1-TEARDOWN", "response_close_failure"
                )
                accepted = False
        try:
            cleanup_attempts += _cleanup_transaction_paths(
                manifest,
                keep_final=accepted and refusal is None,
            )
            events.append("cleanup_complete")
        except RecoveryRefusal as exc:
            refusal = exc
            accepted = False
            try:
                cleanup_attempts += _cleanup_transaction_paths(
                    manifest,
                    keep_final=False,
                )
            except RecoveryRefusal:
                pass
        if refusal is not None and final_payload.exists() and final_payload in manifest.created:
            try:
                _remove_owned(final_payload, manifest)
                cleanup_attempts += 1
            except RecoveryRefusal:
                refusal = RecoveryRefusal(
                    "HL1R1-TEARDOWN", "response_close_failure"
                )
        try:
            resources = _enforce_resources(
                private_root,
                snapshot,
                case=None,
                disk_usage_reader=disk_usage_reader,
                rss_reader=rss_reader,
                clock=clock,
            )
        except RecoveryRefusal:
            if refusal is None:
                refusal = RecoveryRefusal(
                    "HL1R1-RESOURCE", "incremental_disk_cap"
                )
            accepted = False

    route = "DREYER-H1" if refusal is None and accepted else "DREYER-H0"
    report = _report(
        route=route,
        refusal=refusal,
        sensor_contract=sensor_contract if route == "DREYER-H1" else None,
        resources=resources,
        generated_input_bytes=len(response.body),
        marker_bytes=len(marker_payload),
        response_close_attempts=response.close_attempts,
        response_closed=response.closed,
        cleanup_attempts=cleanup_attempts,
        cleanup_complete=not staging.exists() and not staged_payload.exists(),
        final_payload_retained=final_payload.exists() and route == "DREYER-H1",
    )
    try:
        _publish_report(output_path, report, case=case)
    except RecoveryRefusal:
        if final_payload.exists() and final_payload in manifest.created:
            _remove_owned(final_payload, manifest)
        raise
    return DevelopmentCaseResult(
        report=report,
        events=tuple(events),
        opener_constructions=opener_constructions,
        requests=requests,
        response_closed=response.closed,
        marker_path=marker_path,
        output_path=output_path,
        final_payload_path=final_payload,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the generated implementation plan without execution capability."""

    load_green_recovery_decision(repo_root)
    return {
        "packet_id": PACKET_ID,
        "lane_id": LANE_ID,
        "status": "implementation_only_qualification_activation_absent",
        "green_decision": {
            "commit": GREEN_DECISION_COMMIT,
            "CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "ordered_future_qualification_refusal_cases": list(
            ORDERED_SUCCESSOR_REFUSAL_CASES
        ),
        "registered_qualification_authority": False,
        "real_command_available": False,
        "HL2_authority": False,
        "real_EDF_authority": False,
        "warnings": [
            "implementation_is_generated_only",
            "registered_qualification_requires_separate_activation",
            "real_EEG_remains_closed",
        ],
    }


def inspect_generated_report(path: str | Path) -> dict[str, Any]:
    """Strictly inspect one aggregate generated report."""

    candidate = Path(path).expanduser().absolute()
    try:
        info = os.lstat(candidate)
        if (
            stat.S_ISLNK(info.st_mode)
            or not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_size > MAX_PUBLIC_OUTPUT_BYTES
        ):
            raise OSError("report identity differs")
        payload = candidate.read_bytes()
        report = _strict_json(payload)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap") from exc
    if not isinstance(report, dict):
        raise RecoveryRefusal("HL1R1-PUBLICATION", "public_output_cap")
    _validate_report(report)
    return report
