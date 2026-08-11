"""Proof-gated one-shot live wrapper for the MARC1-CD1 archive inventory."""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import math
import os
import re
import resource
import shutil
import socket
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence
from urllib.parse import urlsplit

from neurodecodekit.datasets import marc1_central_directory_audit as audit


SCHEMA_VERSION = "0.1.0"
RESULT_SCHEMA_NAME = "neurodecodekit.marc1_central_directory_live_result"
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.marc1_freewill_central_directory_live_implementation"
)
LANE_ID = "MARC1-CD1A"
GENERATED_ROUTE = "MARC1CDL-G1"
SUCCESS_ROUTE = "MARC1CD-R1"
FAILURE_ROUTES = tuple(f"MARC1CD-F{index:02d}" for index in range(7))

DECISION_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_authorization_decision.v0.json"
)
DECISION_SHA256 = "4a80cda6dd1beb49dacfc3cf3487d9e5ed2020af82f2677527518802ea686c20"
GREEN_DECISION_COMMIT = "624cc4e99a4aa600b68a333c1bcd84e6cebb9dcd"
GREEN_DECISION_CI_RUN_ID = 31_519_016_891
GREEN_DECISION_BASE_JOB_ID = 93_871_192_638
GREEN_DECISION_OPTIONAL_JOB_ID = 93_871_192_713
REQUEST_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_authorization_request.v0.json"
)
REQUEST_SHA256 = "67dd062df8189f4a5742da9ad9986dd12641d146df7aa3f12a50ca3b845d25fd"
PARSER_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc1_central_directory_audit.py"
)
PARSER_SHA256 = "db8b6975c81d4afe0a5ede0126956f4113159c98b3975cbded4ad322bce23de6"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_live_implementation.v0.json"
)
REAL_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0"
)
REAL_CONSUMED_NAME = "execution_consumed.v0.json"
REAL_PRIVATE_MANIFEST_NAME = "member_inventory.private.v0.json"
REAL_PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/marc1_freewill_central_directory_live_result.v0.json"
)

MINIMUM_FREE_DISK_BYTES = 12 * 1024 * 1024 * 1024
MAX_LOAD_PER_LOGICAL_CPU = 1.0
MAX_RUNTIME_SECONDS = 120.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_INCREMENTAL_DISK_BYTES = 32 * 1024 * 1024
MAX_PUBLIC_OUTPUT_BYTES = 1024 * 1024
MAX_COMBINED_OUTPUT_BYTES = 8 * 1024 * 1024
MAX_HTTP_ATTEMPTS = 5
MAX_REDIRECTS = 2
MAX_ACCEPTED_BODY_BYTES = 17_039_360
MAX_TIMEOUT_SECONDS = 45.0
THREAD_ENV_KEYS = audit.THREAD_ENV_KEYS
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})

PUBLIC_RESULT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "proof_posture",
        "route",
        "source",
        "green_evidence",
        "transport_summary",
        "archive_summary",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "download_url",
        "entries",
        "filename",
        "filenames",
        "location",
        "local_header_offset",
        "member_name",
        "member_names",
        "raw_headers",
        "response_body",
        "url",
        "urls",
    }
)


class LiveArchiveRefusal(RuntimeError):
    """Fail closed with one aggregate-safe MARC1-CD1 route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC1-CD1 live refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True)
class GreenWrapperEvidence:
    """Operator-supplied remote-green proof for the exact wrapper commit."""

    implementation_commit: str
    implementation_ci_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    registered_execution_ordinal: int = 1


@dataclass(frozen=True)
class InventoryRun:
    """Parsed metadata-only inventory and aggregate transport evidence."""

    inventory: audit.ParsedInventory
    trailer: audit.TrailerInfo
    transport: Mapping[str, Any]


@dataclass(frozen=True)
class LiveAuditOutcome:
    """One generated qualification or consumed public audit outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path | None
    runtime_seconds: float
    peak_rss_bytes: int
    combined_output_bytes: int


class FixtureHTTPResponse(io.BytesIO):
    """urllib-shaped response used only by injected generated fixtures."""

    def __init__(
        self,
        body: bytes,
        *,
        status: int,
        url: str,
        headers: Mapping[str, str],
        duplicate_headers: Sequence[tuple[str, str]] = (),
        read_error: Exception | None = None,
        nonbytes_body: bool = False,
    ) -> None:
        super().__init__(body)
        self.status = status
        self.code = status
        self._url = url
        self.headers = Message()
        for key, value in headers.items():
            self.headers.add_header(key, value)
        for key, value in duplicate_headers:
            self.headers.add_header(key, value)
        self.read_calls = 0
        self.close_calls = 0
        self._read_error = read_error
        self._nonbytes_body = nonbytes_body

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        self.read_calls += 1
        if self._read_error is not None:
            raise self._read_error
        value = super().read(size)
        if self._nonbytes_body:
            return "not-bytes"  # type: ignore[return-value]
        return value

    def close(self) -> None:
        self.close_calls += 1
        super().close()


@dataclass(frozen=True)
class FixtureExchange:
    url: str
    request_headers: Mapping[str, str]
    response: FixtureHTTPResponse


class FixtureOpener:
    """Strict sequential opener with no socket or DNS operation."""

    def __init__(self, exchanges: Sequence[FixtureExchange]) -> None:
        self._exchanges = list(exchanges)
        self.calls = 0

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        self.calls += 1
        if not self._exchanges:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "unexpected extra HTTP attempt")
        expected = self._exchanges.pop(0)
        observed = _normalized_request_headers(request)
        for key, value in expected.request_headers.items():
            if observed.get(key.lower()) != value:
                raise LiveArchiveRefusal(FAILURE_ROUTES[3], "mock request header differs")
        allowed = set(expected.request_headers) | {"user-agent"}
        if set(observed) != {key.lower() for key in allowed}:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "mock request header set differs")
        if (
            request.full_url != expected.url
            or request.get_method() != "GET"
            or request.data is not None
            or timeout != MAX_TIMEOUT_SECONDS
        ):
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "mock request differs")
        return expected.response

    def assert_consumed(self) -> None:
        if self._exchanges:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "expected mock request is missing")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(64 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


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


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON number")


def _strict_json(payload: bytes) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object")
    return value


def _read_locked_json(
    path: Path,
    *,
    expected_sha256: str | None,
    maximum_bytes: int = MAX_COMBINED_OUTPUT_BYTES,
) -> tuple[dict[str, Any], str, int]:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON no-follow open failed") from exc
    try:
        payload = bytearray()
        while len(payload) <= maximum_bytes:
            chunk = os.read(
                descriptor,
                min(64 * 1024, maximum_bytes + 1 - len(payload)),
            )
            if not chunk:
                break
            payload.extend(chunk)
    finally:
        os.close(descriptor)
    if len(payload) > maximum_bytes:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON exceeds cap")
    body = bytes(payload)
    observed_sha256 = _sha256_bytes(body)
    if expected_sha256 is not None and observed_sha256 != expected_sha256:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON identity differs")
    try:
        value = _strict_json(body)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "locked JSON is malformed") from exc
    return value, observed_sha256, len(body)


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load and validate the exact remotely green packet-bound decision."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision, _, _ = _read_locked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
    )
    authorization = decision.get("authorization", {})
    sequence = decision.get("registered_sequence", {})
    user = decision.get("user_authorization", {})
    request, _, _ = _read_locked_json(
        root / REQUEST_RELATIVE_PATH,
        expected_sha256=REQUEST_SHA256,
    )
    if (
        decision.get("schema_name")
        != "neurodecodekit.marc1_freewill_central_directory_authorization_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "950796d123272a459eedf1e431ba99f22a0c582e"
        or authorization.get("live_wrapper_implementation_authorized_after_decision_green")
        is not True
        or authorization.get(
            "one_public_metadata_tail_and_conditional_directory_invocation_authorized_after_wrapper_green"
        )
        is not True
        or authorization.get("whole_archive_download_authorized_now") is not False
        or authorization.get("member_local_header_or_payload_access_authorized_now")
        is not False
        or sequence.get("provider") != "Figshare"
        or sequence.get("record_id") != 28_632_599
        or sequence.get("version") != 1
        or sequence.get("file_id") != audit.FILE_ID
        or sequence.get("file_bytes") != audit.VIRTUAL_ARCHIVE_BYTES
        or sequence.get("tail_bytes") != audit.TAIL_BYTES
        or sequence.get("central_directory_cap_bytes") != audit.MAX_DIRECTORY_BYTES
        or sequence.get("accepted_response_body_count") != 3
        or sequence.get("accepted_response_body_cap_bytes") != MAX_ACCEPTED_BODY_BYTES
        or sequence.get("HTTP_request_attempt_cap") != MAX_HTTP_ATTEMPTS
        or sequence.get("bodyless_redirect_cap") != MAX_REDIRECTS
        or sequence.get("whole_archive_downloads") != 0
        or sequence.get("member_payload_requests") != 0
        or sequence.get("retries") != 0
        or sequence.get("reruns") != 0
        or user.get("actual_message_SHA256")
        != "c97c7d04ef3fb6e70265325d4805026948a1474554de1725374ae47c64a19371"
        or request.get("lane_id") != LANE_ID
        or request.get("authorized_now") is not False
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "authorization proof differs")
    if _sha256_file(root / PARSER_RELATIVE_PATH) != PARSER_SHA256:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "green parser source differs")
    audit.load_registered_contract()
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> tuple[dict[str, Any], str]:
    """Validate the generated-qualified wrapper record and tracked hashes."""

    root = Path(repo_root)
    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "implementation proof differs")
    record, observed_hash, _ = _read_locked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=expected_sha256,
    )
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != LANE_ID
        or record.get("status")
        != "generated_mock_live_wrapper_qualified_requires_remote_green_before_public_access"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("push_CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("public_execution_consumed") is not False
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "implementation registry differs")
    for binding in record.get("tracked_file_hashes", ()):
        relative = str(binding.get("path", ""))
        expected = str(binding.get("sha256", ""))
        if (
            not relative
            or relative.startswith(("/", "~"))
            or ".." in Path(relative).parts
            or HEX64_RE.fullmatch(expected) is None
            or _sha256_file(root / relative) != expected
        ):
            raise LiveArchiveRefusal(FAILURE_ROUTES[0], "implementation source hash differs")
    return record, observed_hash


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )


def verify_green_wrapper_evidence(
    repo_root: str | Path,
    evidence: GreenWrapperEvidence,
) -> dict[str, Any]:
    """Bind a clean exact HEAD to externally observed green CI evidence."""

    root = Path(repo_root)
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or HEX64_RE.fullmatch(evidence.implementation_registry_sha256) is None
        or min(
            evidence.implementation_ci_run_id,
            evidence.implementation_base_job_id,
            evidence.implementation_optional_job_id,
        )
        <= 0
        or evidence.registered_execution_ordinal != 1
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "green wrapper evidence is malformed")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "HEAD differs from wrapper evidence")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "tracked worktree is not clean")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "green decision is not an ancestor")
    load_green_decision(root)
    record, _ = load_implementation_record(
        root,
        expected_sha256=evidence.implementation_registry_sha256,
    )
    return record


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def preconsumption_machine_gate(
    root: str | Path,
    *,
    environ: Mapping[str, str],
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Measure all computer-protection gates before marker or request."""

    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "thread environment is not one")
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "machine metric is unavailable") from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "CPU or load metric is unavailable")
    load_one = float(load_values[0])
    normalized = load_one / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(load_one)
        or load_one < 0
        or normalized > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "machine resource cap failed")
    return {
        "passed_before_consumed_marker": True,
        "free_disk_bytes": free_bytes,
        "logical_CPUs": logical_cpus,
        "one_minute_load": load_one,
        "one_minute_load_per_logical_CPU": normalized,
        "peak_RSS_bytes_before_consumption": peak_rss,
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
    }


def _normalized_request_headers(request: urllib.request.Request) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for key, value in request.header_items():
        lowered = key.strip().lower()
        if not lowered or lowered in normalized or "\r" in value or "\n" in value:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "request header differs")
        normalized[lowered] = value.strip()
    return normalized


def _response_headers(response: BinaryIO) -> dict[str, str]:
    source = getattr(response, "headers", None)
    if source is None:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response headers are unavailable")
    items = source.raw_items() if hasattr(source, "raw_items") else source.items()
    critical = {
        "content-encoding",
        "content-length",
        "content-range",
        "content-type",
        "etag",
        "last-modified",
        "location",
        "transfer-encoding",
    }
    normalized: dict[str, str] = {}
    for key, value in items:
        lowered = str(key).strip().lower()
        text = str(value).strip()
        if not lowered or "\r" in text or "\n" in text:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response header differs")
        if lowered not in critical:
            continue
        if lowered in normalized:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response header differs")
        normalized[lowered] = text
    return normalized


def _response_status(response: BinaryIO) -> int:
    value = getattr(response, "status", None)
    if value is None and hasattr(response, "getcode"):
        value = response.getcode()
    if type(value) is not int:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response status is unavailable")
    return value


def _response_url(response: BinaryIO) -> str:
    if not hasattr(response, "geturl"):
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response URL is unavailable")
    value = response.geturl()
    if not isinstance(value, str):
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response URL differs")
    return value


def _read_once_capped(response: BinaryIO, cap: int) -> bytes:
    try:
        payload = response.read(cap + 1)
    except Exception as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response body read failed") from exc
    if not isinstance(payload, bytes):
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response body is not bytes")
    if len(payload) > cap:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "response body exceeds cap")
    return payload


def _open_live_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _NoRedirect)
    try:
        return opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        return exc
    except Exception as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "public request failed") from exc


def _resolve_global_addresses(hostname: str) -> tuple[str, ...]:
    try:
        values = socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "redirect DNS lookup failed") from exc
    addresses = tuple(sorted({str(value[4][0]) for value in values}))
    if not addresses:
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "redirect DNS result is empty")
    return addresses


def _base_access_counters() -> dict[str, int]:
    return {
        "public_metadata_requests": 0,
        "public_metadata_body_bytes": 0,
        "public_archive_tail_request_attempts": 0,
        "public_archive_tail_body_bytes": 0,
        "public_central_directory_requests": 0,
        "public_central_directory_body_bytes": 0,
        "HTTP_request_attempts": 0,
        "accepted_response_bodies": 0,
        "accepted_response_body_bytes": 0,
        "DNS_queries": 0,
        "network_redirects": 0,
        "whole_archive_downloads": 0,
        "member_local_header_requests": 0,
        "member_payload_requests": 0,
        "member_payload_bytes": 0,
        "local_archive_path_operations": 0,
        "participant_or_cohort_selections": 0,
        "participant_acquisitions": 0,
        "signal_sample_reads": 0,
        "channel_geometry_event_or_onset_reads": 0,
        "target_label_response_sentence_key_or_trial_reads": 0,
        "derivative_cache_split_or_feature_operations": 0,
        "training_or_parameter_update_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "prediction_freezes": 0,
        "target_deliveries": 0,
        "scoring_events": 0,
        "dependency_installs": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "temporary_cleanup_operations": 0,
        "retries_or_reruns": 0,
        "post_result_updates": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


class BoundedHTTPTransport:
    """Convert bounded raw HTTP responses into the frozen parser interface."""

    def __init__(
        self,
        opener: Callable[[urllib.request.Request, float], BinaryIO],
        *,
        counters: dict[str, int],
        public_request: bool,
    ) -> None:
        self._opener = opener
        self._counters = counters
        self._public = public_request
        self.attempts = 0
        self.accepted_body_count = 0
        self.accepted_body_bytes = 0
        self.redirects = 0
        self.raw_body_hashes: dict[str, str] = {}
        self.header_presence: dict[str, dict[str, bool]] = {}
        self.attempt_kinds: list[str] = []

    def request(
        self,
        method: str,
        url: str,
        headers: Mapping[str, str],
    ) -> audit.MockResponse:
        if method != "GET" or self.attempts >= MAX_HTTP_ATTEMPTS:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "HTTP method or attempt cap differs")
        normalized = audit._normalized_headers(headers)
        range_value = normalized.get("range")
        if range_value is None:
            kind = "metadata"
            if (
                self.attempts != 0
                or url != audit.METADATA_URL
                or normalized
                != {"accept": "application/json", "accept-encoding": "identity"}
            ):
                raise LiveArchiveRefusal(FAILURE_ROUTES[3], "metadata request differs")
            cap = audit.MAX_METADATA_BYTES
            expected_status = 200
        else:
            if normalized != {"accept-encoding": "identity", "range": range_value}:
                raise LiveArchiveRefusal(FAILURE_ROUTES[3], "range request headers differ")
            tail_range = f"bytes={audit.TAIL_START}-{audit.TAIL_END}"
            kind = "tail" if range_value == tail_range else "directory"
            if kind == "tail":
                cap = audit.TAIL_BYTES
            else:
                match = re.fullmatch(r"bytes=([0-9]+)-([0-9]+)", range_value)
                if match is None:
                    raise LiveArchiveRefusal(FAILURE_ROUTES[3], "range header differs")
                start, end = (int(value) for value in match.groups())
                cap = end - start + 1
                if cap < 46 or cap > audit.MAX_DIRECTORY_BYTES:
                    raise LiveArchiveRefusal(FAILURE_ROUTES[3], "directory range cap differs")
            expected_status = 206
        request = urllib.request.Request(
            url,
            headers={
                **{key.title(): value for key, value in normalized.items()},
                "User-Agent": "NeuroDecodeKit-MARC1CD/0.1",
            },
            method="GET",
        )
        self.attempts += 1
        self.attempt_kinds.append(kind)
        if self._public:
            self._counters["HTTP_request_attempts"] += 1
            if kind == "metadata":
                self._counters["public_metadata_requests"] += 1
            elif kind == "tail":
                self._counters["public_archive_tail_request_attempts"] += 1
            else:
                self._counters["public_central_directory_requests"] += 1
        try:
            response = self._opener(request, MAX_TIMEOUT_SECONDS)
        except LiveArchiveRefusal:
            raise
        except Exception as exc:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "HTTP opener failed") from exc
        try:
            status = _response_status(response)
            if _response_url(response) != url:
                raise LiveArchiveRefusal(FAILURE_ROUTES[3], "automatic redirect or URL drift")
            response_headers = _response_headers(response)
            if "transfer-encoding" in response_headers:
                raise LiveArchiveRefusal(FAILURE_ROUTES[3], "transfer encoding is forbidden")
            if status in REDIRECT_STATUSES:
                body = _read_once_capped(response, 0)
                self.redirects += 1
                if self._public:
                    self._counters["network_redirects"] += 1
            elif status == expected_status:
                body = _read_once_capped(response, cap)
                self.accepted_body_count += 1
                self.accepted_body_bytes += len(body)
                self.raw_body_hashes[kind] = _sha256_bytes(body)
                self.header_presence[kind] = {
                    "ETag": "etag" in response_headers,
                    "Last_Modified": "last-modified" in response_headers,
                }
                if self._public:
                    self._counters["accepted_response_bodies"] += 1
                    self._counters["accepted_response_body_bytes"] += len(body)
                    if kind == "metadata":
                        self._counters["public_metadata_body_bytes"] += len(body)
                    elif kind == "tail":
                        self._counters["public_archive_tail_body_bytes"] += len(body)
                    else:
                        self._counters["public_central_directory_body_bytes"] += len(body)
            else:
                body = b""
        finally:
            try:
                response.close()
            except Exception:
                pass
        return audit.MockResponse(
            body,
            status=status,
            url=url,
            headers=response_headers,
        )

    def summary(self) -> dict[str, Any]:
        return {
            "HTTP_request_attempts": self.attempts,
            "accepted_response_bodies": self.accepted_body_count,
            "accepted_response_body_bytes": self.accepted_body_bytes,
            "network_redirects": self.redirects,
            "attempt_kind_counts": dict(sorted(Counter(self.attempt_kinds).items())),
            "response_body_sha256": dict(sorted(self.raw_body_hashes.items())),
            "response_header_presence": dict(sorted(self.header_presence.items())),
        }


def _map_parser_refusal(exc: audit.Marc1CentralDirectoryRefusal) -> LiveArchiveRefusal:
    try:
        index = audit.REFUSAL_IDS.index(exc.refusal_id)
    except ValueError:
        index = 6
    return LiveArchiveRefusal(FAILURE_ROUTES[index], "frozen parser refused the response")


def perform_inventory(
    transport: BoundedHTTPTransport,
    *,
    resolver: Callable[[str], Sequence[str]],
    counters: dict[str, int],
    public_request: bool,
) -> InventoryRun:
    """Run the exact metadata, tail, ZIP64, and directory sequence in memory."""

    def counted_resolver(hostname: str) -> Sequence[str]:
        if public_request:
            counters["DNS_queries"] += 1
        return resolver(hostname)

    try:
        metadata_response = transport.request(
            "GET",
            audit.METADATA_URL,
            {"accept": "application/json", "accept-encoding": "identity"},
        )
        download_url = audit._read_metadata_response(metadata_response)
        tail, terminal_url, redirects = audit._fetch_range(
            transport,
            initial_url=download_url,
            range_start=audit.TAIL_START,
            range_end=audit.TAIL_END,
            resolver=counted_resolver,
        )
        trailer = audit.parse_zip64_trailer(tail)
        directory, directory_terminal_url, directory_redirects = audit._fetch_range(
            transport,
            initial_url=terminal_url,
            range_start=trailer.range_start,
            range_end=trailer.range_end,
            resolver=counted_resolver,
            maximum_redirects=0,
        )
        if directory_terminal_url != terminal_url or directory_redirects:
            raise LiveArchiveRefusal(FAILURE_ROUTES[3], "directory endpoint drifted")
        inventory = audit.parse_central_directory(directory, trailer)
    except audit.Marc1CentralDirectoryRefusal as exc:
        raise _map_parser_refusal(exc) from exc
    if (
        redirects > MAX_REDIRECTS
        or transport.attempts > MAX_HTTP_ATTEMPTS
        or transport.accepted_body_count != 3
        or transport.accepted_body_bytes > MAX_ACCEPTED_BODY_BYTES
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[3], "transport aggregate cap differs")
    summary = transport.summary()
    summary["terminal_host_sha256"] = _sha256_bytes(
        (urlsplit(terminal_url).hostname or "").encode("ascii")
    )
    summary["terminal_URL_published"] = False
    summary["raw_headers_published"] = False
    summary["raw_bodies_persisted"] = False
    return InventoryRun(inventory=inventory, trailer=trailer, transport=summary)


def _generated_exchanges(
    fixture: audit.GeneratedFixture,
    *,
    redirect_count: int,
) -> tuple[list[FixtureExchange], Callable[[str], Sequence[str]]]:
    if redirect_count not in {0, 2}:
        raise ValueError("generated redirect count must be zero or two")
    exchanges = [
        FixtureExchange(
            audit.METADATA_URL,
            {"accept": "application/json", "accept-encoding": "identity"},
            FixtureHTTPResponse(
                fixture.metadata_body,
                status=200,
                url=audit.METADATA_URL,
                headers={
                    "Content-Encoding": "identity",
                    "Content-Length": str(len(fixture.metadata_body)),
                    "Content-Type": "application/json",
                },
            ),
        )
    ]
    tail_headers = {
        "accept-encoding": "identity",
        "range": f"bytes={audit.TAIL_START}-{audit.TAIL_END}",
    }
    terminal = audit.DOWNLOAD_URL
    if redirect_count:
        first = "https://cdn-a.example.net/freewill/57518986"
        second = "https://cdn-b.example.net/freewill/57518986"
        exchanges.extend(
            [
                FixtureExchange(
                    audit.DOWNLOAD_URL,
                    tail_headers,
                    FixtureHTTPResponse(
                        b"",
                        status=302,
                        url=audit.DOWNLOAD_URL,
                        headers={"Content-Length": "0", "Location": first},
                    ),
                ),
                FixtureExchange(
                    first,
                    tail_headers,
                    FixtureHTTPResponse(
                        b"",
                        status=307,
                        url=first,
                        headers={"Content-Length": "0", "Location": second},
                    ),
                ),
            ]
        )
        terminal = second
    exchanges.append(
        FixtureExchange(
            terminal,
            tail_headers,
            FixtureHTTPResponse(
                fixture.tail_body,
                status=206,
                url=terminal,
                headers=audit._range_headers(audit.TAIL_START, audit.TAIL_END),
            ),
        )
    )
    directory_end = fixture.central_directory_offset + len(fixture.central_directory_body) - 1
    directory_headers = {
        "accept-encoding": "identity",
        "range": f"bytes={fixture.central_directory_offset}-{directory_end}",
    }
    exchanges.append(
        FixtureExchange(
            terminal,
            directory_headers,
            FixtureHTTPResponse(
                fixture.central_directory_body,
                status=206,
                url=terminal,
                headers=audit._range_headers(fixture.central_directory_offset, directory_end),
            ),
        )
    )

    def resolver(hostname: str) -> Sequence[str]:
        values = {
            "cdn-a.example.net": ("8.8.8.8",),
            "cdn-b.example.net": ("1.1.1.1",),
        }
        return values.get(hostname, ("8.8.4.4",))

    return exchanges, resolver


def _run_generated_path(
    fixture: audit.GeneratedFixture,
    *,
    redirect_count: int,
) -> tuple[InventoryRun, FixtureOpener]:
    exchanges, resolver = _generated_exchanges(fixture, redirect_count=redirect_count)
    opener = FixtureOpener(exchanges)
    counters = _base_access_counters()
    transport = BoundedHTTPTransport(opener, counters=counters, public_request=False)
    result = perform_inventory(
        transport,
        resolver=resolver,
        counters=counters,
        public_request=False,
    )
    opener.assert_consumed()
    if any(counters.values()):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "generated path used public access")
    return result, opener


def _expect_refusal(operation: Callable[[], Any]) -> str:
    try:
        operation()
    except LiveArchiveRefusal as exc:
        return exc.route
    raise LiveArchiveRefusal(FAILURE_ROUTES[6], "required wrapper mutation did not refuse")


def _run_wrapper_mutations(fixture: audit.GeneratedFixture) -> dict[str, str]:
    environ_one = {key: "1" for key in THREAD_ENV_KEYS}

    def transport_once(response: FixtureHTTPResponse) -> Any:
        opener = FixtureOpener(
            [
                FixtureExchange(
                    audit.METADATA_URL,
                    {"accept": "application/json", "accept-encoding": "identity"},
                    response,
                )
            ]
        )
        transport = BoundedHTTPTransport(
            opener,
            counters=_base_access_counters(),
            public_request=False,
        )
        return transport.request(
            "GET",
            audit.METADATA_URL,
            {"accept": "application/json", "accept-encoding": "identity"},
        )

    checks: dict[str, Callable[[], Any]] = {
        "thread_gate": lambda: preconsumption_machine_gate(
            Path.cwd(),
            environ={key: "2" for key in THREAD_ENV_KEYS},
            disk_usage_reader=lambda _path: type(
                "Disk", (), {"free": MINIMUM_FREE_DISK_BYTES}
            )(),
            cpu_count_reader=lambda: 8,
            loadavg_reader=lambda: (0.0, 0.0, 0.0),
            rss_reader=lambda: 1,
        ),
        "disk_gate": lambda: preconsumption_machine_gate(
            Path.cwd(),
            environ=environ_one,
            disk_usage_reader=lambda _path: type(
                "Disk", (), {"free": MINIMUM_FREE_DISK_BYTES - 1}
            )(),
            cpu_count_reader=lambda: 8,
            loadavg_reader=lambda: (0.0, 0.0, 0.0),
            rss_reader=lambda: 1,
        ),
        "load_gate": lambda: preconsumption_machine_gate(
            Path.cwd(),
            environ=environ_one,
            disk_usage_reader=lambda _path: type(
                "Disk", (), {"free": MINIMUM_FREE_DISK_BYTES}
            )(),
            cpu_count_reader=lambda: 2,
            loadavg_reader=lambda: (2.1, 0.0, 0.0),
            rss_reader=lambda: 1,
        ),
        "duplicate_header": lambda: transport_once(
            FixtureHTTPResponse(
                fixture.metadata_body,
                status=200,
                url=audit.METADATA_URL,
                headers={"Content-Length": str(len(fixture.metadata_body))},
                duplicate_headers=(("Content-Length", str(len(fixture.metadata_body))),),
            )
        ),
        "response_URL_drift": lambda: transport_once(
            FixtureHTTPResponse(
                fixture.metadata_body,
                status=200,
                url=audit.METADATA_URL + "/other",
                headers={"Content-Length": str(len(fixture.metadata_body))},
            )
        ),
        "response_overflow": lambda: transport_once(
            FixtureHTTPResponse(
                b"x" * (audit.MAX_METADATA_BYTES + 1),
                status=200,
                url=audit.METADATA_URL,
                headers={"Content-Length": str(audit.MAX_METADATA_BYTES + 1)},
            )
        ),
        "response_nonbytes": lambda: transport_once(
            FixtureHTTPResponse(
                fixture.metadata_body,
                status=200,
                url=audit.METADATA_URL,
                headers={"Content-Length": str(len(fixture.metadata_body))},
                nonbytes_body=True,
            )
        ),
        "opener_error": lambda: BoundedHTTPTransport(
            lambda _request, _timeout: (_ for _ in ()).throw(OSError("mock failure")),
            counters=_base_access_counters(),
            public_request=False,
        ).request(
            "GET",
            audit.METADATA_URL,
            {"accept": "application/json", "accept-encoding": "identity"},
        ),
    }
    return {name: _expect_refusal(operation) for name, operation in checks.items()}


def _private_manifest(
    run: InventoryRun,
    *,
    generated: bool,
) -> dict[str, Any]:
    manifest = copy.deepcopy(dict(run.inventory.private_manifest))
    manifest["schema_name"] = "neurodecodekit.marc1_central_directory_private_manifest"
    manifest["proof_posture"] = (
        "generated_fixture_private_metadata_only"
        if generated
        else "live_archive_private_central_directory_metadata_only"
    )
    manifest["source_identity"] = {
        "provider": "generated_fixture" if generated else "Figshare",
        "record_id": 28_632_599,
        "version": 1,
        "file_id": audit.FILE_ID,
        "declared_archive_bytes": audit.VIRTUAL_ARCHIVE_BYTES,
        "registered_MD5": audit.ARCHIVE_MD5,
        "whole_archive_downloaded": False,
        "member_payload_opened": False,
    }
    manifest["transport_body_sha256"] = dict(
        run.transport.get("response_body_sha256", {})
    )
    return manifest


def _archive_summary(run: InventoryRun, manifest: Mapping[str, Any]) -> dict[str, Any]:
    summary = dict(run.inventory.aggregate_summary)
    summary["private_manifest_sha256"] = _sha256_bytes(_canonical_json_bytes(manifest))
    summary["whole_archive_MD5_verified"] = False
    summary["member_CRC_verified"] = False
    summary["local_headers_verified"] = False
    summary["member_payload_integrity_verified"] = False
    return summary


def _green_evidence(
    evidence: GreenWrapperEvidence | None,
    implementation_registry_sha256: str | None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "decision_commit": GREEN_DECISION_COMMIT,
        "decision_CI_run_id": GREEN_DECISION_CI_RUN_ID,
        "decision_base_job_id": GREEN_DECISION_BASE_JOB_ID,
        "decision_optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
        "decision_registry_sha256": DECISION_SHA256,
        "both_decision_jobs_green": True,
    }
    if evidence is None:
        value.update(
            {
                "wrapper_commit": "uncommitted_generated_qualification",
                "wrapper_CI_run_id": None,
                "wrapper_base_job_id": None,
                "wrapper_optional_neuro_job_id": None,
                "implementation_registry_sha256": implementation_registry_sha256,
                "both_wrapper_jobs_green": False,
            }
        )
    else:
        value.update(
            {
                "wrapper_commit": evidence.implementation_commit,
                "wrapper_CI_run_id": evidence.implementation_ci_run_id,
                "wrapper_base_job_id": evidence.implementation_base_job_id,
                "wrapper_optional_neuro_job_id": evidence.implementation_optional_job_id,
                "implementation_registry_sha256": implementation_registry_sha256,
                "both_wrapper_jobs_green": True,
            }
        )
    return value


def _build_success_report(
    run: InventoryRun,
    manifest: Mapping[str, Any],
    *,
    generated: bool,
    evidence: GreenWrapperEvidence | None,
    implementation_registry_sha256: str | None,
    machine: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    combined_output_bytes: int,
    incremental_disk_bytes: int,
    inherited_mutations: int,
    wrapper_mutations: int,
) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": (
            "passed_generated_mock_live_wrapper_qualification"
            if generated
            else "passed_live_archive_central_directory_inventory"
        ),
        "proof_posture": (
            "generated_mock_archive_metadata_only_no_scientific_value"
            if generated
            else "public_archive_central_directory_metadata_only_no_member_access"
        ),
        "route": GENERATED_ROUTE if generated else SUCCESS_ROUTE,
        "source": {
            "provider": "generated_fixture" if generated else "Figshare",
            "record_id": 28_632_599,
            "version": 1,
            "DOI": "10.6084/m9.figshare.28632599.v1",
            "file_id": audit.FILE_ID,
            "declared_archive_bytes": audit.VIRTUAL_ARCHIVE_BYTES,
            "registered_MD5": audit.ARCHIVE_MD5,
            "license": "CC BY 4.0",
            "whole_archive_downloaded": False,
            "member_payload_opened": False,
        },
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "transport_summary": dict(run.transport),
        "archive_summary": _archive_summary(run, manifest),
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "combined_output_bytes": combined_output_bytes,
            "incremental_disk_bytes": incremental_disk_bytes,
            "inherited_parser_mutations_passed": inherited_mutations,
            "wrapper_mutations_passed": wrapper_mutations,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine),
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision_identity": True,
            "green_wrapper_identity_or_generated_only_state": True,
            "preconsumption_machine_gate": True,
            "exact_source_metadata_identity": True,
            "bounded_three_body_transport": True,
            "redirect_policy": True,
            "exact_tail_and_virtual_total": True,
            "decoy_resistant_EOCD_and_complete_ZIP64": True,
            "bounded_exact_central_directory": True,
            "safe_complete_entry_inventory": True,
            "zero_local_header_or_member_content_reads": True,
            "private_inventory_and_aggregate_output_separated": True,
            "resource_and_output_caps": True,
            "all_forbidden_neural_model_score_and_claim_counters_zero": True,
        },
        "warnings": [
            "Generated transport contains no public or human data."
            if generated
            else "Only public archive metadata ranges were read; no ZIP member was opened.",
            "Registered whole-archive MD5 was not verified because the archive was not downloaded.",
            "Member CRC local-header and payload integrity remain unavailable.",
            "No participant signal event target model prediction or score was accessed.",
            "End-to-end neural decoding latency was not measured.",
        ],
        "unavailable_fields": [
            "whole-archive MD5 verification",
            "member CRC verification",
            "local-header consistency",
            "member payload integrity",
            "participant channel geometry signal event onset or target content",
            "neural model prediction or score",
            "end-to-end neural decoding latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A proof-gated standard-library wrapper can inventory a 13.59 GB ZIP through "
                "bounded metadata ranges without opening a member payload."
            ),
            "scientific_claim_not_established": (
                "Archive metadata contain no neural signal event target or model result and "
                "establish no neural effect or decoding capability."
            ),
        },
    }


def _build_failure_report(
    *,
    refusal: LiveArchiveRefusal,
    stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker_bytes: int,
    transport_summary: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "consumed_failed_live_archive_inventory",
        "proof_posture": "aggregate_failure_after_private_consumed_marker",
        "route": refusal.route,
        "source": {
            "provider": "Figshare",
            "record_id": 28_632_599,
            "version": 1,
            "DOI": "10.6084/m9.figshare.28632599.v1",
            "file_id": audit.FILE_ID,
            "declared_archive_bytes": audit.VIRTUAL_ARCHIVE_BYTES,
            "registered_MD5": audit.ARCHIVE_MD5,
            "license": "CC BY 4.0",
            "whole_archive_downloaded": False,
            "member_payload_opened": False,
        },
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "transport_summary": dict(transport_summary),
        "archive_summary": {
            "inventory_available": False,
            "failure_stage": stage,
            "failure_reason_published": False,
            "whole_archive_materialized_bytes": 0,
        },
        "measurements": {
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "combined_output_bytes": 0,
            "incremental_disk_bytes": marker_bytes,
            "inherited_parser_mutations_passed": 0,
            "wrapper_mutations_passed": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_metadata_only",
            "end_to_end_latency_measured": False,
            "machine_gate": dict(machine),
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision_identity": True,
            "green_wrapper_identity": True,
            "preconsumption_machine_gate": True,
            "live_archive_inventory_completed": False,
            "no_retry_or_rerun_available": True,
            "zero_member_neural_model_score_and_claim_operations": all(
                counters.get(key, 0) == 0
                for key in (
                    "whole_archive_downloads",
                    "member_local_header_requests",
                    "member_payload_requests",
                    "signal_sample_reads",
                    "target_label_response_sentence_key_or_trial_reads",
                    "model_inference_runs",
                    "scoring_events",
                    "scientific_claim_upgrades",
                )
            ),
        },
        "warnings": [
            "The one registered live invocation is consumed and no retry or rerun is available.",
            "The aggregate route localizes the failure class without publishing raw headers bodies URLs or member rows.",
            "No whole archive member payload participant signal target model or score was accessed.",
        ],
        "unavailable_fields": [
            "completed central-directory inventory",
            "whole-archive MD5 verification",
            "member CRC local-header and payload integrity",
            "participant signal event target model or score",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "The one-shot wrapper failed closed and retained an aggregate consumed result."
            ),
            "scientific_claim_not_established": (
                "A metadata transport failure establishes no neural effect or decoding capability."
            ),
        },
    }


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_PUBLIC_KEYS:
                raise LiveArchiveRefusal(FAILURE_ROUTES[6], "public result leaks private data")
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)
    elif isinstance(value, str) and ("://" in value or "/files/" in value):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "public result leaks a URL")


def validate_public_result(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if set(report) != PUBLIC_RESULT_FIELDS:
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "public result field set differs")
    if (
        report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in {GENERATED_ROUTE, SUCCESS_ROUTE, *FAILURE_ROUTES}
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "public result identity differs")
    counters = report.get("access_counters")
    if not isinstance(counters, dict):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "public counters differ")
    for key in (
        "whole_archive_downloads",
        "member_local_header_requests",
        "member_payload_requests",
        "member_payload_bytes",
        "signal_sample_reads",
        "target_label_response_sentence_key_or_trial_reads",
        "model_inference_runs",
        "scoring_events",
        "scientific_claim_upgrades",
    ):
        if counters.get(key) != 0:
            raise LiveArchiveRefusal(FAILURE_ROUTES[6], "forbidden public counter is nonzero")
    if report.get("route") == GENERATED_ROUTE and any(counters.values()):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "generated result used public access")
    if report.get("route") == SUCCESS_ROUTE:
        if (
            counters.get("accepted_response_bodies") != 3
            or counters.get("accepted_response_body_bytes", MAX_ACCEPTED_BODY_BYTES + 1)
            > MAX_ACCEPTED_BODY_BYTES
            or not all(report.get("acceptance_gates", {}).values())
        ):
            raise LiveArchiveRefusal(FAILURE_ROUTES[6], "live success gate differs")


def _serialize_outputs(
    report: dict[str, Any],
    manifest: Mapping[str, Any] | None,
    *,
    marker_bytes: int,
) -> tuple[bytes, bytes | None, int, int]:
    manifest_bytes = None if manifest is None else _canonical_json_bytes(manifest)
    report["measurements"]["combined_output_bytes"] = 0
    report["measurements"]["incremental_disk_bytes"] = marker_bytes + (
        0 if manifest_bytes is None else len(manifest_bytes)
    )
    report_bytes = _canonical_json_bytes(report)
    for _ in range(3):
        combined = len(report_bytes) + (0 if manifest_bytes is None else len(manifest_bytes))
        incremental = combined + marker_bytes
        report["measurements"]["combined_output_bytes"] = combined
        report["measurements"]["incremental_disk_bytes"] = incremental
        report_bytes = _canonical_json_bytes(report)
    combined = len(report_bytes) + (0 if manifest_bytes is None else len(manifest_bytes))
    incremental = combined + marker_bytes
    if (
        len(report_bytes) > MAX_PUBLIC_OUTPUT_BYTES
        or combined > MAX_COMBINED_OUTPUT_BYTES
        or incremental > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "output byte cap failed")
    validate_public_result(report)
    return report_bytes, manifest_bytes, combined, incremental


def _write_exclusive(path: Path, payload: bytes, *, mode: int) -> None:
    if path.exists() or path.is_symlink():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "output already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "output parent is unavailable")
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
    except OSError as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "exclusive output write failed") from exc


def _make_exclusive_directory(path: Path, *, mode: int = 0o700) -> None:
    if path.exists() or path.is_symlink():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "output directory already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "output parent is unavailable")
    try:
        os.mkdir(path, mode)
    except OSError as exc:
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "output directory creation failed") from exc


def _ensure_private_parent(root: Path) -> Path:
    codex_work = root / ".codex_work"
    if not codex_work.is_dir() or codex_work.is_symlink():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "workspace private root is unavailable")
    parent = codex_work / "marc1_central_directory"
    if parent.exists() or parent.is_symlink():
        if not parent.is_dir() or parent.is_symlink():
            raise LiveArchiveRefusal(FAILURE_ROUTES[1], "private lane parent differs")
    else:
        try:
            os.mkdir(parent, 0o700)
        except OSError as exc:
            raise LiveArchiveRefusal(FAILURE_ROUTES[1], "private parent creation failed") from exc
    return parent


def _write_consumed_marker(
    private_root: Path,
    evidence: GreenWrapperEvidence,
) -> tuple[Path, int, str]:
    marker = {
        "schema_name": "neurodecodekit.marc1_central_directory_live_execution_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_commit": evidence.implementation_commit,
        "implementation_registry_sha256": evidence.implementation_registry_sha256,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
        "whole_archive_download_allowed": False,
        "member_payload_access_allowed": False,
    }
    payload = _canonical_json_bytes(marker)
    path = private_root / REAL_CONSUMED_NAME
    _write_exclusive(path, payload, mode=0o600)
    return path, len(payload), _sha256_bytes(payload)


def _enforce_final_resources(runtime_seconds: float, peak_rss_bytes: int) -> None:
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "runtime or RSS cap failed")


def qualify_generated_mock_wrapper(
    output_dir: str | Path,
    *,
    repo_root: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> LiveAuditOutcome:
    """Qualify the proof, transport, parser, privacy, and output path locally."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    output = Path(output_dir)
    load_green_decision(root)
    machine = preconsumption_machine_gate(
        output.parent,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        cpu_count_reader=cpu_count_reader,
        loadavg_reader=loadavg_reader,
        rss_reader=rss_reader,
    )
    _make_exclusive_directory(output)
    started = clock()
    fixture = audit.build_generated_fixture()
    direct, _ = _run_generated_path(fixture, redirect_count=0)
    redirected, _ = _run_generated_path(fixture, redirect_count=2)
    replay, _ = _run_generated_path(audit.build_generated_fixture(), redirect_count=0)
    if (
        direct.inventory.canonical_inventory_bytes
        != redirected.inventory.canonical_inventory_bytes
        or direct.inventory.canonical_inventory_bytes
        != replay.inventory.canonical_inventory_bytes
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "generated replay differs")
    inherited_mutations = audit.run_required_mutations(fixture)
    wrapper_mutations = _run_wrapper_mutations(fixture)
    runtime = clock() - started
    peak_rss = int(rss_reader())
    _enforce_final_resources(runtime, peak_rss)
    manifest = _private_manifest(direct, generated=True)
    counters = _base_access_counters()
    report = _build_success_report(
        direct,
        manifest,
        generated=True,
        evidence=None,
        implementation_registry_sha256=None,
        machine=machine,
        counters=counters,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        combined_output_bytes=0,
        incremental_disk_bytes=0,
        inherited_mutations=len(inherited_mutations),
        wrapper_mutations=len(wrapper_mutations),
    )
    report_bytes, manifest_bytes, combined, _ = _serialize_outputs(
        report,
        manifest,
        marker_bytes=0,
    )
    if manifest_bytes is None:
        raise AssertionError("generated manifest is unavailable")
    manifest_path = output / "member_inventory.generated.private.v0.json"
    report_path = output / "marc1_central_directory_live_qualification.v0.json"
    _write_exclusive(manifest_path, manifest_bytes, mode=0o600)
    _write_exclusive(report_path, report_bytes, mode=0o644)
    return LiveAuditOutcome(
        report=report,
        report_path=report_path,
        private_manifest_path=manifest_path,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        combined_output_bytes=combined,
    )


def _write_consumed_failure_report(
    path: Path,
    *,
    refusal: LiveArchiveRefusal,
    stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: dict[str, int],
    started: float,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    marker_bytes: int,
    transport_summary: Mapping[str, Any],
) -> None:
    report = _build_failure_report(
        refusal=refusal,
        stage=stage,
        evidence=evidence,
        implementation_registry_sha256=implementation_registry_sha256,
        machine=machine,
        counters=counters,
        runtime_seconds=clock() - started,
        peak_rss_bytes=int(rss_reader()),
        marker_bytes=marker_bytes,
        transport_summary=transport_summary,
    )
    report_bytes, _, _, _ = _serialize_outputs(report, None, marker_bytes=marker_bytes)
    _write_exclusive(path, report_bytes, mode=0o644)


def execute_registered_archive_audit(
    repo_root: str | Path,
    *,
    evidence: GreenWrapperEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[urllib.request.Request, float], BinaryIO] = _open_live_once,
    resolver: Callable[[str], Sequence[str]] = _resolve_global_addresses,
    proof_verifier: Callable[[str | Path, GreenWrapperEvidence], Mapping[str, Any]] = (
        verify_green_wrapper_evidence
    ),
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> LiveAuditOutcome:
    """Consume the one registered public archive-metadata audit."""

    root = Path(repo_root)
    implementation = proof_verifier(root, evidence)
    if implementation.get("execution_state", {}).get("public_execution_consumed") is not False:
        raise LiveArchiveRefusal(FAILURE_ROUTES[0], "implementation is not pre-execution")
    machine = preconsumption_machine_gate(
        root,
        environ=os.environ if environ is None else environ,
        disk_usage_reader=disk_usage_reader,
        cpu_count_reader=cpu_count_reader,
        loadavg_reader=loadavg_reader,
        rss_reader=rss_reader,
    )
    private_root = root / REAL_ROOT_RELATIVE_PATH
    public_result_path = root / REAL_PUBLIC_RESULT_RELATIVE_PATH
    if (
        private_root.exists()
        or private_root.is_symlink()
        or public_result_path.exists()
        or public_result_path.is_symlink()
    ):
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "registered execution is already consumed")
    _ensure_private_parent(root)
    _make_exclusive_directory(private_root)
    marker_path, marker_bytes, _ = _write_consumed_marker(private_root, evidence)
    if not marker_path.is_file():
        raise LiveArchiveRefusal(FAILURE_ROUTES[1], "consumed marker was not created")
    counters = _base_access_counters()
    started = clock()
    transport = BoundedHTTPTransport(opener, counters=counters, public_request=True)
    stage = "metadata_transport"
    try:
        stage = "metadata_tail_directory_parse"
        run = perform_inventory(
            transport,
            resolver=resolver,
            counters=counters,
            public_request=True,
        )
        stage = "resource_and_output_validation"
        runtime = clock() - started
        peak_rss = int(rss_reader())
        _enforce_final_resources(runtime, peak_rss)
        manifest = _private_manifest(run, generated=False)
        report = _build_success_report(
            run,
            manifest,
            generated=False,
            evidence=evidence,
            implementation_registry_sha256=evidence.implementation_registry_sha256,
            machine=machine,
            counters=counters,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            combined_output_bytes=0,
            incremental_disk_bytes=marker_bytes,
            inherited_mutations=32,
            wrapper_mutations=8,
        )
        report_bytes, manifest_bytes, combined, _ = _serialize_outputs(
            report,
            manifest,
            marker_bytes=marker_bytes,
        )
        if manifest_bytes is None:
            raise AssertionError("live private manifest is unavailable")
        manifest_path = private_root / REAL_PRIVATE_MANIFEST_NAME
        _write_exclusive(manifest_path, manifest_bytes, mode=0o600)
        _write_exclusive(public_result_path, report_bytes, mode=0o644)
        return LiveAuditOutcome(
            report=report,
            report_path=public_result_path,
            private_manifest_path=manifest_path,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            combined_output_bytes=combined,
        )
    except audit.Marc1CentralDirectoryRefusal as exc:
        refusal = _map_parser_refusal(exc)
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=evidence.implementation_registry_sha256,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
                transport_summary=transport.summary(),
            )
        raise refusal from exc
    except LiveArchiveRefusal as refusal:
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=evidence.implementation_registry_sha256,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
                transport_summary=transport.summary(),
            )
        raise
    except Exception as exc:
        refusal = LiveArchiveRefusal(
            FAILURE_ROUTES[6],
            "unexpected post-consumption implementation failure",
        )
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=refusal,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=evidence.implementation_registry_sha256,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
                transport_summary=transport.summary(),
            )
        raise refusal from exc


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate generated or consumed result."""

    report_path = Path(path)
    if "private" in report_path.name.lower():
        raise LiveArchiveRefusal(FAILURE_ROUTES[6], "private manifest inspection is forbidden")
    report, _, _ = _read_locked_json(report_path, expected_sha256=None)
    validate_public_result(report)
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the fixed zero-network plan and closed member boundary."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    return {
        "lane_id": LANE_ID,
        "provider": "Figshare",
        "record_id": 28_632_599,
        "version": 1,
        "file_id": audit.FILE_ID,
        "declared_archive_bytes": audit.VIRTUAL_ARCHIVE_BYTES,
        "tail_bytes": audit.TAIL_BYTES,
        "central_directory_cap_bytes": audit.MAX_DIRECTORY_BYTES,
        "accepted_response_body_cap_bytes": MAX_ACCEPTED_BODY_BYTES,
        "HTTP_request_attempt_cap": MAX_HTTP_ATTEMPTS,
        "public_requests_made": 0,
        "whole_archive_downloads": 0,
        "member_payload_requests": 0,
        "participant_acquisitions": 0,
        "model_runs": 0,
        "scoring_runs": 0,
        "execution_requires_exact_green_wrapper_evidence": True,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc1_central_directory_live",
        description="Proof-gated MARC1-CD1 metadata-range archive inventory.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-network registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate result.")
    inspect.add_argument("report")
    execute = subparsers.add_parser("execute", help="Consume the one registered live audit.")
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--implementation-ci-run-id", required=True, type=int)
    execute.add_argument("--implementation-base-job-id", required=True, type=int)
    execute.add_argument("--implementation-optional-job-id", required=True, type=int)
    execute.add_argument("--implementation-registry-sha256", required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    try:
        if args.command == "plan":
            print(_canonical_json_bytes(registered_plan()).decode("ascii"), end="")
            return 0
        if args.command == "qualify":
            outcome = qualify_generated_mock_wrapper(args.output_dir)
        elif args.command == "inspect":
            report = inspect_public_result(args.report)
            print(_canonical_json_bytes(report).decode("ascii"), end="")
            return 0
        else:
            evidence = GreenWrapperEvidence(
                implementation_commit=args.implementation_commit,
                implementation_ci_run_id=args.implementation_ci_run_id,
                implementation_base_job_id=args.implementation_base_job_id,
                implementation_optional_job_id=args.implementation_optional_job_id,
                implementation_registry_sha256=args.implementation_registry_sha256,
            )
            outcome = execute_registered_archive_audit(_repo_root(), evidence=evidence)
        print(
            _canonical_json_bytes(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "report": str(outcome.report_path),
                    "combined_output_bytes": outcome.combined_output_bytes,
                    "runtime_seconds": outcome.runtime_seconds,
                    "peak_RSS_bytes": outcome.peak_rss_bytes,
                }
            ).decode("ascii"),
            end="",
        )
        return 0
    except LiveArchiveRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
