"""One-shot, metadata-only public snapshot identity wrapper for IACKD-M1A."""

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
import stat
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Any, BinaryIO, Callable, Mapping, Sequence

from neurodecodekit.datasets import iackd_snapshot_identity as identity


SCHEMA_VERSION = "0.1.0"
RESULT_SCHEMA_NAME = "neurodecodekit.iackd_snapshot_identity_public_result"
IMPLEMENTATION_SCHEMA_NAME = (
    "neurodecodekit.iackd_snapshot_identity_public_implementation"
)
ENDPOINT = "https://openneuro.org/crn/graphql"
QUERY = """query IackdSnapshotIdentity {
  snapshot(datasetId: \"ds006840\", tag: \"1.0.0\") {
    id
    tag
    hexsha
    description {
      id
      Name
      BIDSVersion
      License
      DatasetDOI
    }
    files(recursive: true) {
      id
      filename
      size
      directory
      annexed
      urls
    }
  }
}
"""
REQUEST_BODY = (
    json.dumps(
        {"query": QUERY},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    + "\n"
).encode("ascii")
QUERY_SHA256 = "246db737c72bcd001c60191b6f31bef24d5bfc9a40ca5fa61b8ba215b30e3db0"
REQUEST_SHA256 = "913b033e430cbbb28ae14850dd744a50bd0418ecb64206645f4367d32ddd8896"
QUERY_BYTES = 316
REQUEST_BYTES = 355
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
READ_LIMIT_BYTES = MAX_RESPONSE_BYTES + 1
MAX_COMBINED_OUTPUT_BYTES = 1024 * 1024
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024 * 1024
MINIMUM_FREE_DISK_BYTES = 2 * 1024 * 1024 * 1024
MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024 * 1024
MAX_LOAD_PER_LOGICAL_CPU = 1.0
THREAD_ENV_KEYS = identity.THREAD_ENV_KEYS

DECISION_RELATIVE_PATH = Path(
    "registries/iackd_snapshot_identity_authorization_decision.v0.json"
)
DECISION_SHA256 = "73cb45db87f1d73957fdb06c588e88718a7f0855ca4c09de9a2352f41f7597e1"
GREEN_DECISION_COMMIT = "4165c24cdad9768c7e36b5e4893602d02434be50"
GREEN_DECISION_CI_RUN_ID = 31_485_359_989
GREEN_DECISION_BASE_JOB_ID = 93_759_373_384
GREEN_DECISION_OPTIONAL_JOB_ID = 93_759_373_333
CANONICALIZER_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/iackd_snapshot_identity.py"
)
CANONICALIZER_SHA256 = "e4ba0aaca4ebe515be7b323defc730eb0e288c04e263293e1218c75e750b3e72"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/iackd_snapshot_identity_public_implementation.v0.json"
)
REAL_ROOT_RELATIVE_PATH = Path(
    ".codex_work/iackd_snapshot_identity/public_audit_v0"
)
REAL_CONSUMED_NAME = "execution_consumed.v0.json"
REAL_PRIVATE_MANIFEST_NAME = "selected_manifest.private.v0.json"
REAL_PUBLIC_RESULT_RELATIVE_PATH = Path(
    "registries/iackd_snapshot_identity_public_result.v0.json"
)

HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
CANONICAL_DECIMAL_RE = re.compile(r"(?:0|[1-9][0-9]*)\Z")
REFUSAL_IDS = (
    "IACKDMP-F00-green-proof-registration-source-or-request-mismatch",
    "IACKDMP-F01-machine-resource-or-thread-gate-failure",
    "IACKDMP-F02-consumed-marker-output-collision-or-path-failure",
    "IACKDMP-F03-HTTP-status-redirect-encoding-or-framing-failure",
    "IACKDMP-F04-one-read-body-cap-hash-or-length-failure",
    "IACKDMP-F05-snapshot-semantic-canonicalization-failure",
    "IACKDMP-F06-output-privacy-runtime-RSS-or-byte-cap-failure",
    "IACKDMP-F07-generated-mock-qualification-failure",
)
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
        "transport",
        "snapshot_anchor",
        "tree_summary",
        "selected_summary",
        "critical_metadata",
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
        "filename",
        "filenames",
        "git_object_id",
        "rows",
        "s3_key",
        "s3_version_id",
        "url",
        "urls",
        "version_id",
        "version_ids",
    }
)


class PublicSnapshotRefusal(RuntimeError):
    """Fail closed with a stable, aggregate-safe refusal identifier."""

    def __init__(self, refusal_id: str, reason: str):
        if refusal_id not in REFUSAL_IDS:
            raise ValueError("unknown IACKD-M1A refusal identifier")
        super().__init__(f"{refusal_id}: {reason}")
        self.refusal_id = refusal_id
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
class TransportEvidence:
    """Aggregate transport facts retained after the response body is discarded."""

    http_status: int
    final_url: str
    framing_profile: str
    content_length: int | None
    response_bytes: int
    response_sha256: str
    read_calls: int


@dataclass(frozen=True)
class PublicAuditOutcome:
    """One generated qualification or consumed public metadata outcome."""

    report: Mapping[str, Any]
    report_path: Path
    private_manifest_path: Path | None
    runtime_seconds: float
    peak_rss_bytes: int
    combined_output_bytes: int


class FixtureResponse(io.BytesIO):
    """urllib-shaped one-read response used only by generated tests."""

    def __init__(
        self,
        payload: bytes,
        *,
        url: str = ENDPOINT,
        status: int = 200,
        content_length: str | None = None,
        content_encoding: str | None = None,
        transfer_encoding: str | None = None,
        duplicate_headers: Sequence[tuple[str, str]] = (),
        read_error: Exception | None = None,
        nonbytes_body: bool = False,
    ) -> None:
        super().__init__(payload)
        self._url = url
        self.status = status
        self.headers = Message()
        if content_length is None and transfer_encoding is None:
            content_length = str(len(payload))
        if content_length is not None:
            self.headers.add_header("Content-Length", content_length)
        if content_encoding is not None:
            self.headers.add_header("Content-Encoding", content_encoding)
        if transfer_encoding is not None:
            self.headers.add_header("Transfer-Encoding", transfer_encoding)
        for name, value in duplicate_headers:
            self.headers.add_header(name, value)
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
        payload = super().read(size)
        if self._nonbytes_body:
            return "not-bytes"  # type: ignore[return-value]
        return payload

    def close(self) -> None:
        self.close_calls += 1
        super().close()


class _RejectRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "redirect is forbidden")


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
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON is unavailable") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON is not a regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON no-follow open failed") from exc
    try:
        payload = b""
        while len(payload) <= maximum_bytes:
            chunk = os.read(descriptor, min(64 * 1024, maximum_bytes + 1 - len(payload)))
            if not chunk:
                break
            payload += chunk
    finally:
        os.close(descriptor)
    if len(payload) > maximum_bytes:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON exceeds cap")
    observed_sha256 = _sha256_bytes(payload)
    if expected_sha256 is not None and observed_sha256 != expected_sha256:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON identity differs")
    try:
        value = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "locked JSON is malformed") from exc
    return value, observed_sha256, len(payload)


def _validate_locked_request() -> None:
    if (
        len(QUERY.encode("utf-8")) != QUERY_BYTES
        or _sha256_bytes(QUERY.encode("utf-8")) != QUERY_SHA256
        or len(REQUEST_BODY) != REQUEST_BYTES
        or _sha256_bytes(REQUEST_BODY) != REQUEST_SHA256
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "query or request body differs")


def load_green_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green packet-bound decision and source anchors."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    _validate_locked_request()
    decision, _, _ = _read_locked_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=DECISION_SHA256,
    )
    authorization = decision.get("authorization", {})
    sequence = decision.get("registered_sequence", {})
    user = decision.get("user_authorization", {})
    if (
        decision.get("schema_name")
        != "neurodecodekit.iackd_snapshot_identity_authorization_decision"
        or decision.get("schema_version") != SCHEMA_VERSION
        or decision.get("lane_id") != "IACKD-M1A"
        or decision.get("authorization_parent_commit")
        != "ce847383ab1e327523cbc172bb6d3be417b46a11"
        or authorization.get("wrapper_implementation_authorized_after_decision_green")
        is not True
        or authorization.get("one_public_GraphQL_request_authorized_after_wrapper_green")
        is not True
        or authorization.get("S3_payload_request_or_download_authorized_now") is not False
        or authorization.get("local_IACKD_path_operation_authorized_now") is not False
        or sequence.get("endpoint") != ENDPOINT
        or sequence.get("query_SHA256") != QUERY_SHA256
        or sequence.get("request_body_SHA256") != REQUEST_SHA256
        or sequence.get("GraphQL_requests") != 1
        or sequence.get("S3_payload_requests") != 0
        or sequence.get("retries") != 0
        or sequence.get("reruns") != 0
        or user.get("actual_message_SHA256")
        != "c97c7d04ef3fb6e70265325d4805026948a1474554de1725374ae47c64a19371"
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "authorization decision differs")
    if _sha256_file(root / CANONICALIZER_RELATIVE_PATH) != CANONICALIZER_SHA256:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "green canonicalizer source differs")
    identity.load_registered_contract(root)
    return decision


def load_implementation_record(
    repo_root: str | Path,
    *,
    expected_sha256: str,
) -> tuple[dict[str, Any], str]:
    """Validate the generated-qualified wrapper record and every tracked hash."""

    root = Path(repo_root)
    if HEX64_RE.fullmatch(expected_sha256) is None:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "implementation registry proof differs")
    record, observed_hash, _ = _read_locked_json(
        root / IMPLEMENTATION_RELATIVE_PATH,
        expected_sha256=expected_sha256,
    )
    if (
        record.get("schema_name") != IMPLEMENTATION_SCHEMA_NAME
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("lane_id") != "IACKD-M1A"
        or record.get("status")
        != "generated_mock_wrapper_qualified_requires_remote_green_before_public_access"
        or record.get("green_decision", {}).get("commit") != GREEN_DECISION_COMMIT
        or record.get("green_decision", {}).get("push_CI_run_id")
        != GREEN_DECISION_CI_RUN_ID
        or record.get("generated_qualification", {}).get("all_gates_passed") is not True
        or record.get("execution_state", {}).get("public_execution_consumed") is not False
        or any(record.get("implementation_access_counters", {}).values())
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "implementation registry differs")
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
            raise PublicSnapshotRefusal(REFUSAL_IDS[0], "implementation source hash differs")
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
    """Bind a clean exact HEAD to the externally verified green CI evidence."""

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
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "green wrapper evidence is malformed")
    head = _git(root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "HEAD differs from wrapper evidence")
    clean = _git(root, "status", "--porcelain", "--untracked-files=no")
    if clean.returncode or clean.stdout.strip():
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "tracked worktree is not clean")
    ancestor = _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "green decision is not an ancestor")
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
    """Measure all computer-protection gates before a marker or request."""

    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise PublicSnapshotRefusal(REFUSAL_IDS[1], "thread environment is not one")
    try:
        free_bytes = int(disk_usage_reader(Path(root)).free)
        logical_cpus = cpu_count_reader()
        load_values = loadavg_reader()
        peak_rss = int(rss_reader())
    except Exception as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[1], "machine metric is unavailable") from exc
    if logical_cpus is None or logical_cpus <= 0 or not load_values:
        raise PublicSnapshotRefusal(REFUSAL_IDS[1], "CPU or load metric is unavailable")
    load_one = float(load_values[0])
    normalized = load_one / logical_cpus
    if (
        free_bytes < MINIMUM_FREE_DISK_BYTES
        or not math.isfinite(load_one)
        or load_one < 0
        or normalized > MAX_LOAD_PER_LOGICAL_CPU
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[1], "machine resource cap failed")
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


def build_locked_request() -> urllib.request.Request:
    """Build the one frozen POST without credentials, variables, or alternatives."""

    _validate_locked_request()
    request = urllib.request.Request(
        ENDPOINT,
        data=REQUEST_BODY,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Content-Type": "application/json",
            "User-Agent": "NeuroDecodeKit-IACKDM/0.1",
        },
        method="POST",
    )
    if (
        request.full_url != ENDPOINT
        or request.get_method() != "POST"
        or request.data != REQUEST_BODY
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[0], "constructed request differs")
    return request


def _open_public_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
    try:
        return urllib.request.build_opener(_RejectRedirect).open(request, timeout=timeout)
    except PublicSnapshotRefusal:
        raise
    except Exception as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "single public request failed") from exc


def _header_values(headers: Any, name: str) -> list[str]:
    if hasattr(headers, "get_all"):
        values = headers.get_all(name, [])
        return [str(value) for value in values]
    if isinstance(headers, Mapping):
        return [str(value) for key, value in headers.items() if str(key).casefold() == name.casefold()]
    raise PublicSnapshotRefusal(REFUSAL_IDS[3], "response headers are unavailable")


def _single_header(headers: Any, name: str) -> str | None:
    values = _header_values(headers, name)
    if len(values) > 1:
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "duplicate transport header")
    return values[0].strip() if values else None


def _read_transport_response(
    response: BinaryIO,
    *,
    counters: dict[str, int],
    public_request: bool,
) -> tuple[bytes, TransportEvidence]:
    try:
        status = int(response.getcode())  # type: ignore[attr-defined]
        final_url = str(response.geturl())  # type: ignore[attr-defined]
        headers = response.headers  # type: ignore[attr-defined]
    except Exception as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "response metadata is unavailable") from exc
    if status != 200 or final_url != ENDPOINT:
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "HTTP status or final URL differs")
    content_encoding = _single_header(headers, "Content-Encoding")
    if content_encoding is not None and content_encoding.casefold() != "identity":
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "content encoding is not identity")
    transfer_encoding = _single_header(headers, "Transfer-Encoding")
    content_length_text = _single_header(headers, "Content-Length")
    if transfer_encoding is not None:
        if transfer_encoding.casefold() != "chunked" or content_length_text is not None:
            raise PublicSnapshotRefusal(REFUSAL_IDS[3], "transfer framing differs")
        framing = "chunked"
        content_length = None
    elif content_length_text is not None:
        if CANONICAL_DECIMAL_RE.fullmatch(content_length_text) is None:
            raise PublicSnapshotRefusal(REFUSAL_IDS[3], "Content-Length is not canonical")
        content_length = int(content_length_text)
        if content_length > MAX_RESPONSE_BYTES:
            raise PublicSnapshotRefusal(REFUSAL_IDS[4], "Content-Length exceeds cap")
        framing = "fixed_length"
    else:
        framing = "close_delimited"
        content_length = None
    read_counter = (
        "public_response_body_reads" if public_request else "mock_response_body_reads"
    )
    byte_counter = (
        "public_response_body_bytes" if public_request else "mock_response_body_bytes"
    )
    hash_counter = "public_response_hashes" if public_request else "mock_response_hashes"
    counters[read_counter] += 1
    try:
        body = response.read(READ_LIMIT_BYTES)
    except Exception as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[4], "response body read failed") from exc
    if not isinstance(body, bytes):
        raise PublicSnapshotRefusal(REFUSAL_IDS[4], "response body is not bytes")
    if len(body) > MAX_RESPONSE_BYTES:
        raise PublicSnapshotRefusal(REFUSAL_IDS[4], "response body exceeds cap")
    if content_length is not None and content_length != len(body):
        raise PublicSnapshotRefusal(REFUSAL_IDS[4], "Content-Length differs from body")
    response_sha256 = _sha256_bytes(body)
    counters[byte_counter] += len(body)
    counters[hash_counter] += 1
    return body, TransportEvidence(
        http_status=status,
        final_url=final_url,
        framing_profile=framing,
        content_length=content_length,
        response_bytes=len(body),
        response_sha256=response_sha256,
        read_calls=1,
    )


def perform_locked_transport(
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    *,
    counters: dict[str, int],
    public_request: bool,
) -> tuple[bytes, TransportEvidence]:
    """Open, inspect, read once, close once, and retain no raw header."""

    request = build_locked_request()
    if public_request:
        counters["public_GraphQL_requests"] += 1
    else:
        counters["mock_transport_calls"] += 1
    try:
        response = opener(request, 20.0)
    except PublicSnapshotRefusal:
        raise
    except Exception as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[3], "transport opener failed") from exc
    if public_request:
        counters["public_response_opens"] += 1
    else:
        counters["mock_response_opens"] += 1
    try:
        return _read_transport_response(
            response,
            counters=counters,
            public_request=public_request,
        )
    finally:
        try:
            response.close()
        except Exception as exc:
            raise PublicSnapshotRefusal(REFUSAL_IDS[4], "response close failed") from exc


def _base_access_counters() -> dict[str, int]:
    return {
        "mock_transport_calls": 0,
        "mock_response_opens": 0,
        "mock_response_body_reads": 0,
        "mock_response_body_bytes": 0,
        "mock_response_hashes": 0,
        "public_GraphQL_requests": 0,
        "public_response_opens": 0,
        "public_response_body_reads": 0,
        "public_response_body_bytes": 0,
        "public_response_hashes": 0,
        "public_response_semantic_parses": 0,
        "private_consumed_markers": 0,
        "private_selected_manifests": 0,
        "public_aggregate_reports": 0,
        "S3_payload_requests": 0,
        "S3_payload_bytes": 0,
        "local_IACKD_path_operations": 0,
        "old_consumed_root_operations": 0,
        "signal_sample_reads": 0,
        "channel_geometry_event_or_trajectory_reads": 0,
        "target_label_or_trial_reads": 0,
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
        "retries_or_reruns": 0,
        "post_result_updates": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
        "end_to_end_latency_measurements": 0,
    }


def _canonicalize_public_body(
    body: bytes,
    *,
    contract: Mapping[str, Any],
    counters: dict[str, int],
    public_request: bool,
) -> identity.CanonicalSnapshot:
    try:
        canonical = identity.canonicalize_generated_response(body, contract=contract)
    except identity.SnapshotIdentityRefusal as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[5], "snapshot identity is incompatible") from exc
    if public_request:
        counters["public_response_semantic_parses"] += 1
    return canonical


def _private_manifest(
    canonical: identity.CanonicalSnapshot,
    transport: TransportEvidence,
    *,
    generated: bool,
) -> dict[str, Any]:
    manifest = copy.deepcopy(dict(canonical.private_manifest))
    manifest["status"] = (
        "generated_mock_private_manifest"
        if generated
        else "public_metadata_selected_manifest_private"
    )
    manifest["source_response_sha256"] = transport.response_sha256
    manifest["source_response_bytes"] = transport.response_bytes
    manifest["raw_response_persisted"] = False
    return manifest


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise PublicSnapshotRefusal(REFUSAL_IDS[6], "private row field is public")
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        if "s3.amazonaws.com" in value or "versionId=" in value or re.search(
            r"sub-[0-9]{2}/", value
        ):
            raise PublicSnapshotRefusal(REFUSAL_IDS[6], "private row value is public")


def validate_public_result(report: Mapping[str, Any]) -> None:
    """Validate aggregate-only output for both success and consumed failure."""

    if set(report) != PUBLIC_RESULT_FIELDS:
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "public result fields differ")
    if (
        report.get("schema_name") != RESULT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != "IACKD-M1A"
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "public result identity differs")
    counters = report.get("access_counters")
    if not isinstance(counters, dict):
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "access counters are unavailable")
    for forbidden in (
        "S3_payload_requests",
        "S3_payload_bytes",
        "local_IACKD_path_operations",
        "old_consumed_root_operations",
        "signal_sample_reads",
        "channel_geometry_event_or_trajectory_reads",
        "target_label_or_trial_reads",
        "training_or_parameter_update_runs",
        "model_inference_runs",
        "prediction_sets",
        "prediction_freezes",
        "target_deliveries",
        "scoring_events",
        "dependency_installs",
        "provider_or_language_model_calls",
        "stream_device_or_hardware_operations",
        "retries_or_reruns",
        "post_result_updates",
        "release_operations",
        "scientific_claim_upgrades",
        "end_to_end_latency_measurements",
    ):
        if counters.get(forbidden) != 0:
            raise PublicSnapshotRefusal(REFUSAL_IDS[6], "forbidden counter is nonzero")
    measurements = report.get("measurements")
    if not isinstance(measurements, dict):
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "measurements are unavailable")
    if measurements.get("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1) > MAX_COMBINED_OUTPUT_BYTES:
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "combined output cap failed")
    if measurements.get("incremental_disk_bytes", MAX_INCREMENTAL_DISK_BYTES + 1) > MAX_INCREMENTAL_DISK_BYTES:
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "incremental disk cap failed")
    _walk_public(report)


def _green_evidence(
    evidence: GreenWrapperEvidence | None,
    implementation_registry_sha256: str | None,
) -> dict[str, Any]:
    wrapper = (
        {
            "commit": evidence.implementation_commit,
            "push_CI_run_id": evidence.implementation_ci_run_id,
            "base_python_job_id": evidence.implementation_base_job_id,
            "optional_neuro_job_id": evidence.implementation_optional_job_id,
            "implementation_registry_sha256": implementation_registry_sha256,
        }
        if evidence is not None
        else None
    )
    return {
        "decision": {
            "commit": GREEN_DECISION_COMMIT,
            "push_CI_run_id": GREEN_DECISION_CI_RUN_ID,
            "base_python_job_id": GREEN_DECISION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_DECISION_OPTIONAL_JOB_ID,
            "decision_sha256": DECISION_SHA256,
        },
        "wrapper": wrapper,
    }


def _build_success_report(
    canonical: identity.CanonicalSnapshot,
    transport: TransportEvidence,
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
) -> dict[str, Any]:
    source = canonical.report
    report = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": "IACKD-M1A",
        "status": (
            "generated_mock_wrapper_qualified"
            if generated
            else "public_snapshot_metadata_compatible"
        ),
        "proof_posture": (
            "generated_body_mock_transport_zero_network_zero_real_or_local_data"
            if generated
            else "one_consumed_public_metadata_response_zero_payload_zero_neural_or_target_data"
        ),
        "route": "IACKDMP-R0" if generated else "IACKDM-R1",
        "source": {
            "provider": "generated_fixture" if generated else "OpenNeuro",
            "dataset_accession": "ds006840",
            "snapshot_tag": "1.0.0",
            "metadata_response_only": True,
            "S3_payload_authorized": False,
        },
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "transport": {
            "method": "POST",
            "request_bytes": REQUEST_BYTES,
            "request_sha256": REQUEST_SHA256,
            "query_bytes": QUERY_BYTES,
            "query_sha256": QUERY_SHA256,
            "HTTP_status": transport.http_status,
            "final_endpoint_exact": transport.final_url == ENDPOINT,
            "redirects": 0,
            "content_encoding_identity": True,
            "framing_profile": transport.framing_profile,
            "content_length": transport.content_length,
            "response_bytes": transport.response_bytes,
            "response_sha256": transport.response_sha256,
            "response_sha256_is_acceptance_identity": False,
            "read_calls": transport.read_calls,
            "raw_headers_persisted": False,
            "raw_body_persisted": False,
        },
        "snapshot_anchor": copy.deepcopy(source["snapshot_anchor"]),
        "tree_summary": copy.deepcopy(source["tree_summary"]),
        "selected_summary": copy.deepcopy(source["selected_summary"]),
        "critical_metadata": copy.deepcopy(source["critical_metadata"]),
        "measurements": {
            "runtime_seconds_at_final_serialization": runtime_seconds,
            "peak_RSS_bytes_at_final_serialization": peak_rss_bytes,
            "free_disk_bytes_before_consumption": machine["free_disk_bytes"],
            "logical_CPUs": machine["logical_CPUs"],
            "one_minute_load": machine["one_minute_load"],
            "one_minute_load_per_logical_CPU": machine[
                "one_minute_load_per_logical_CPU"
            ],
            "request_body_bytes": REQUEST_BYTES,
            "response_body_bytes": transport.response_bytes,
            "network_body_bytes": 0 if generated else REQUEST_BYTES + transport.response_bytes,
            "combined_output_bytes": combined_output_bytes,
            "incremental_disk_bytes": incremental_disk_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision": True,
            "green_exact_wrapper": generated or evidence is not None,
            "preconsumption_machine_gate": True,
            "exact_request": True,
            "HTTP_status_final_URL_and_zero_redirects": True,
            "identity_encoding_and_registered_framing": True,
            "one_read_body_cap_and_hash": True,
            "snapshot_anchor": True,
            "recursive_tree": True,
            "selected_inventory": True,
            "critical_metadata": True,
            "aggregate_only_public_output": True,
            "runtime_RSS_output_and_disk_caps": True,
            "zero_payload_neural_target_model_and_score_access": True,
        },
        "warnings": [
            (
                "Constructed metadata validates only the wrapper mechanics."
                if generated
                else "This result validates public metadata compatibility only."
            ),
            "The raw response hash is provenance, not snapshot acceptance identity.",
            "No EEG payload, signal, event, trajectory, target, model, prediction, or score was accessed.",
            "Metadata compatibility does not authorize a payload request or scientific claim.",
        ],
        "unavailable_fields": [
            "neural_effect",
            "brain_specific_origin",
            "decoding_accuracy",
            "unseen_person_generalization",
            "language_or_thought_decoding",
            "producer_causality_for_neural_derivative",
            "end_to_end_decoding_latency",
            "portable_or_home_hardware_result",
        ],
        "claim_boundary": {
            "engineering_capability_added": "One bounded standard-library wrapper can bind and test the frozen public snapshot metadata identity without requesting its payload objects.",
            "maximum_result": (
                "Generated fixtures show wrapper mechanics only."
                if generated
                else "The current public metadata is compatible with the frozen ds006840 snapshot tree selected inventory and critical metadata contract."
            ),
            "scientific_claim_not_established": "Metadata and zero neural reads establish no neural effect decoding accuracy brain-specific origin generalization language or thought decoding real-time operation hardware capability assistive benefit home use or clinical utility.",
        },
    }
    return report


def _build_failure_report(
    *,
    refusal_id: str,
    failure_stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: Mapping[str, int],
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker_bytes: int,
) -> dict[str, Any]:
    return {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": "IACKD-M1A",
        "status": "public_snapshot_audit_consumed_and_parked",
        "proof_posture": "one_consumed_metadata_attempt_failed_closed_zero_payload_zero_scientific_value",
        "route": refusal_id,
        "source": {
            "provider": "OpenNeuro",
            "dataset_accession": "ds006840",
            "snapshot_tag": "1.0.0",
            "metadata_response_only": True,
            "S3_payload_authorized": False,
        },
        "green_evidence": _green_evidence(evidence, implementation_registry_sha256),
        "transport": {
            "method": "POST",
            "request_bytes": REQUEST_BYTES,
            "request_sha256": REQUEST_SHA256,
            "query_bytes": QUERY_BYTES,
            "query_sha256": QUERY_SHA256,
            "failure_stage": failure_stage,
            "raw_headers_persisted": False,
            "raw_body_persisted": False,
        },
        "snapshot_anchor": None,
        "tree_summary": None,
        "selected_summary": None,
        "critical_metadata": None,
        "measurements": {
            "runtime_seconds_at_final_serialization": runtime_seconds,
            "peak_RSS_bytes_at_final_serialization": peak_rss_bytes,
            "free_disk_bytes_before_consumption": machine["free_disk_bytes"],
            "logical_CPUs": machine["logical_CPUs"],
            "one_minute_load": machine["one_minute_load"],
            "one_minute_load_per_logical_CPU": machine[
                "one_minute_load_per_logical_CPU"
            ],
            "request_body_bytes": REQUEST_BYTES,
            "response_body_bytes": counters["public_response_body_bytes"],
            "network_body_bytes": REQUEST_BYTES * counters["public_GraphQL_requests"]
            + counters["public_response_body_bytes"],
            "combined_output_bytes": 0,
            "incremental_disk_bytes": marker_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "access_counters": dict(counters),
        "acceptance_gates": {
            "green_decision": True,
            "green_exact_wrapper": True,
            "preconsumption_machine_gate": True,
            "exact_request": counters["public_GraphQL_requests"] == 1,
            "snapshot_metadata_compatible": False,
            "aggregate_only_public_output": True,
            "zero_payload_neural_target_model_and_score_access": True,
        },
        "warnings": [
            "The one registered public metadata attempt is consumed and cannot be retried or rerun.",
            "Only an aggregate refusal identifier and stage are published.",
            "No EEG payload, signal, event, trajectory, target, model, prediction, or score was accessed.",
        ],
        "unavailable_fields": [
            "current_public_snapshot_anchor_identity",
            "current_public_recursive_tree_identity",
            "current_public_selected_manifest_identity",
            "current_public_critical_metadata_identity",
            "neural_effect",
            "decoding_accuracy",
            "brain_specific_origin",
            "end_to_end_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": "The wrapper consumed one bounded public metadata attempt and failed closed without cascading into payload access.",
            "maximum_result": "No public snapshot compatibility result was established.",
            "scientific_claim_not_established": "A metadata refusal and zero neural reads establish no neural effect decoding accuracy brain-specific origin generalization language or thought decoding real-time operation hardware capability assistive benefit home use or clinical utility.",
        },
    }


def _serialize_report_and_manifest(
    report: dict[str, Any],
    manifest: Mapping[str, Any] | None,
    *,
    marker_bytes: int,
) -> tuple[bytes, bytes | None, int, int]:
    manifest_bytes = _canonical_json_bytes(manifest) if manifest is not None else None
    private_bytes = len(manifest_bytes) if manifest_bytes is not None else 0
    for _ in range(4):
        report_bytes = _canonical_json_bytes(report)
        combined = len(report_bytes) + private_bytes
        incremental = combined + marker_bytes
        report["measurements"]["combined_output_bytes"] = combined
        report["measurements"]["incremental_disk_bytes"] = incremental
    report_bytes = _canonical_json_bytes(report)
    combined = len(report_bytes) + private_bytes
    incremental = combined + marker_bytes
    if (
        combined != report["measurements"]["combined_output_bytes"]
        or incremental != report["measurements"]["incremental_disk_bytes"]
        or combined > MAX_COMBINED_OUTPUT_BYTES
        or incremental > MAX_INCREMENTAL_DISK_BYTES
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "output byte fixed point or cap failed")
    validate_public_result(report)
    return report_bytes, manifest_bytes, combined, incremental


def _write_exclusive(path: Path, payload: bytes, *, mode: int) -> None:
    if path.exists() or path.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "output already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "output parent is unavailable")
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
    except PublicSnapshotRefusal:
        raise
    except OSError as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "exclusive output write failed") from exc


def _make_exclusive_directory(path: Path, *, mode: int = 0o700) -> None:
    if path.exists() or path.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "output directory already exists")
    if not path.parent.is_dir() or path.parent.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "output parent is unavailable")
    try:
        os.mkdir(path, mode)
    except OSError as exc:
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "output directory creation failed") from exc


def _ensure_private_parent(root: Path) -> Path:
    codex_work = root / ".codex_work"
    if not codex_work.is_dir() or codex_work.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "workspace private root is unavailable")
    parent = codex_work / "iackd_snapshot_identity"
    if parent.exists() or parent.is_symlink():
        if not parent.is_dir() or parent.is_symlink():
            raise PublicSnapshotRefusal(REFUSAL_IDS[2], "private lane parent differs")
    else:
        try:
            os.mkdir(parent, 0o700)
        except OSError as exc:
            raise PublicSnapshotRefusal(REFUSAL_IDS[2], "private lane parent creation failed") from exc
    return parent


def _write_consumed_marker(
    private_root: Path,
    evidence: GreenWrapperEvidence,
) -> tuple[Path, int, str]:
    marker = {
        "schema_name": "neurodecodekit.iackd_snapshot_identity_public_execution_consumed",
        "schema_version": SCHEMA_VERSION,
        "lane_id": "IACKD-M1A",
        "implementation_commit": evidence.implementation_commit,
        "implementation_registry_sha256": evidence.implementation_registry_sha256,
        "registered_execution_ordinal": 1,
        "retry_allowed": False,
        "rerun_allowed": False,
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
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "runtime or RSS cap failed")


def _fixture_opener(response: FixtureResponse) -> Callable[[urllib.request.Request, float], BinaryIO]:
    calls = 0

    def open_once(request: urllib.request.Request, timeout: float) -> BinaryIO:
        nonlocal calls
        calls += 1
        if calls != 1 or request.full_url != ENDPOINT or timeout != 20.0:
            raise PublicSnapshotRefusal(REFUSAL_IDS[7], "mock opener contract differs")
        return response

    return open_once


def _expect_refusal(function: Callable[[], Any]) -> str:
    try:
        function()
    except PublicSnapshotRefusal as exc:
        return exc.refusal_id
    raise PublicSnapshotRefusal(REFUSAL_IDS[7], "required mutation did not refuse")


def _run_mock_transport_mutations(payload: bytes) -> dict[str, str]:
    checks: dict[str, Callable[[], Any]] = {}

    def run(response: FixtureResponse) -> Any:
        return perform_locked_transport(
            _fixture_opener(response),
            counters=_base_access_counters(),
            public_request=False,
        )

    checks["HTTP_status"] = lambda: run(FixtureResponse(payload, status=503))
    checks["final_URL"] = lambda: run(FixtureResponse(payload, url=ENDPOINT + "/other"))
    checks["content_encoding"] = lambda: run(FixtureResponse(payload, content_encoding="gzip"))
    checks["transfer_encoding"] = lambda: run(
        FixtureResponse(payload, content_length=None, transfer_encoding="gzip")
    )
    checks["conflicting_framing"] = lambda: run(
        FixtureResponse(payload, content_length=str(len(payload)), transfer_encoding="chunked")
    )
    checks["duplicate_content_length"] = lambda: run(
        FixtureResponse(
            payload,
            content_length=str(len(payload)),
            duplicate_headers=(("Content-Length", str(len(payload))),),
        )
    )
    checks["malformed_content_length"] = lambda: run(
        FixtureResponse(payload, content_length="01")
    )
    checks["oversized_content_length"] = lambda: run(
        FixtureResponse(payload, content_length=str(MAX_RESPONSE_BYTES + 1))
    )
    checks["content_length_mismatch"] = lambda: run(
        FixtureResponse(payload, content_length=str(len(payload) + 1))
    )
    checks["body_overflow"] = lambda: run(
        FixtureResponse(b"x" * (MAX_RESPONSE_BYTES + 1))
    )
    checks["body_read_error"] = lambda: run(
        FixtureResponse(payload, read_error=OSError("fixture read failure"))
    )
    checks["nonbytes_body"] = lambda: run(FixtureResponse(payload, nonbytes_body=True))
    checks["opener_error"] = lambda: perform_locked_transport(
        lambda _request, _timeout: (_ for _ in ()).throw(OSError("fixture opener failure")),
        counters=_base_access_counters(),
        public_request=False,
    )
    checks["redirect"] = lambda: _RejectRedirect().redirect_request(
        None, None, 302, "Found", {}, ENDPOINT + "/redirect"
    )
    checks["thread_gate"] = lambda: preconsumption_machine_gate(
        Path.cwd(),
        environ={key: "2" for key in THREAD_ENV_KEYS},
        disk_usage_reader=lambda _path: type("Disk", (), {"free": MINIMUM_FREE_DISK_BYTES})(),
        cpu_count_reader=lambda: 8,
        loadavg_reader=lambda: (0.0, 0.0, 0.0),
        rss_reader=lambda: 1,
    )
    checks["disk_gate"] = lambda: preconsumption_machine_gate(
        Path.cwd(),
        environ={key: "1" for key in THREAD_ENV_KEYS},
        disk_usage_reader=lambda _path: type("Disk", (), {"free": MINIMUM_FREE_DISK_BYTES - 1})(),
        cpu_count_reader=lambda: 8,
        loadavg_reader=lambda: (0.0, 0.0, 0.0),
        rss_reader=lambda: 1,
    )
    checks["load_gate"] = lambda: preconsumption_machine_gate(
        Path.cwd(),
        environ={key: "1" for key in THREAD_ENV_KEYS},
        disk_usage_reader=lambda _path: type("Disk", (), {"free": MINIMUM_FREE_DISK_BYTES})(),
        cpu_count_reader=lambda: 2,
        loadavg_reader=lambda: (2.1, 0.0, 0.0),
        rss_reader=lambda: 1,
    )
    checks["load_unavailable"] = lambda: preconsumption_machine_gate(
        Path.cwd(),
        environ={key: "1" for key in THREAD_ENV_KEYS},
        disk_usage_reader=lambda _path: type("Disk", (), {"free": MINIMUM_FREE_DISK_BYTES})(),
        cpu_count_reader=lambda: 2,
        loadavg_reader=lambda: (_ for _ in ()).throw(OSError("unavailable")),
        rss_reader=lambda: 1,
    )
    checks["runtime_gate"] = lambda: _enforce_final_resources(MAX_RUNTIME_SECONDS + 1, 1)
    checks["RSS_gate"] = lambda: _enforce_final_resources(0.1, MAX_PEAK_RSS_BYTES + 1)
    return {name: _expect_refusal(function) for name, function in checks.items()}


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
) -> PublicAuditOutcome:
    """Qualify the wrapper with one generated body and one mocked response."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    output = Path(output_dir)
    load_green_decision(root)
    contract = identity.load_registered_contract(root)
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
    payload = identity.make_generated_response(contract)
    counters = _base_access_counters()
    response = FixtureResponse(payload)
    body, transport = perform_locked_transport(
        _fixture_opener(response),
        counters=counters,
        public_request=False,
    )
    canonical = _canonicalize_public_body(
        body,
        contract=contract,
        counters=counters,
        public_request=False,
    )
    body = b""
    replay = identity.canonicalize_generated_response(payload, contract=contract)
    if (
        _canonical_json_bytes(canonical.report) != _canonical_json_bytes(replay.report)
        or _canonical_json_bytes(canonical.private_manifest)
        != _canonical_json_bytes(replay.private_manifest)
    ):
        raise PublicSnapshotRefusal(REFUSAL_IDS[7], "deterministic replay differs")
    mutations = _run_mock_transport_mutations(payload)
    runtime = clock() - started
    peak_rss = int(rss_reader())
    _enforce_final_resources(runtime, peak_rss)
    manifest = _private_manifest(canonical, transport, generated=True)
    counters["private_selected_manifests"] = 1
    counters["public_aggregate_reports"] = 1
    report = _build_success_report(
        canonical,
        transport,
        generated=True,
        evidence=None,
        implementation_registry_sha256=None,
        machine=machine,
        counters=counters,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        combined_output_bytes=0,
        incremental_disk_bytes=0,
    )
    report["measurements"]["deterministic_replays"] = 2
    report["measurements"]["mock_refusal_mutations_passed"] = len(mutations)
    report_bytes, manifest_bytes, combined, _ = _serialize_report_and_manifest(
        report,
        manifest,
        marker_bytes=0,
    )
    if manifest_bytes is None:
        raise AssertionError("generated manifest is unavailable")
    manifest_path = output / REAL_PRIVATE_MANIFEST_NAME
    report_path = output / "snapshot_identity_public_qualification.v0.json"
    _write_exclusive(manifest_path, manifest_bytes, mode=0o600)
    _write_exclusive(report_path, report_bytes, mode=0o644)
    return PublicAuditOutcome(
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
    refusal: PublicSnapshotRefusal,
    stage: str,
    evidence: GreenWrapperEvidence,
    implementation_registry_sha256: str,
    machine: Mapping[str, Any],
    counters: dict[str, int],
    started: float,
    clock: Callable[[], float],
    rss_reader: Callable[[], int],
    marker_bytes: int,
) -> None:
    counters["public_aggregate_reports"] = 1
    report = _build_failure_report(
        refusal_id=refusal.refusal_id,
        failure_stage=stage,
        evidence=evidence,
        implementation_registry_sha256=implementation_registry_sha256,
        machine=machine,
        counters=counters,
        runtime_seconds=clock() - started,
        peak_rss_bytes=int(rss_reader()),
        marker_bytes=marker_bytes,
    )
    report_bytes, _, _, _ = _serialize_report_and_manifest(
        report,
        None,
        marker_bytes=marker_bytes,
    )
    _write_exclusive(path, report_bytes, mode=0o644)


def execute_registered_public_audit(
    repo_root: str | Path,
    *,
    evidence: GreenWrapperEvidence,
    environ: Mapping[str, str] | None = None,
    opener: Callable[[urllib.request.Request, float], BinaryIO] = _open_public_once,
    disk_usage_reader: Callable[[Path], Any] = shutil.disk_usage,
    cpu_count_reader: Callable[[], int | None] = os.cpu_count,
    loadavg_reader: Callable[[], Sequence[float]] = os.getloadavg,
    clock: Callable[[], float] = time.monotonic,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> PublicAuditOutcome:
    """Consume the one registered public response after every green gate."""

    root = Path(repo_root)
    implementation = verify_green_wrapper_evidence(root, evidence)
    implementation_hash = evidence.implementation_registry_sha256
    contract = identity.load_registered_contract(root)
    active_environ = os.environ if environ is None else environ
    machine = preconsumption_machine_gate(
        root,
        environ=active_environ,
        disk_usage_reader=disk_usage_reader,
        cpu_count_reader=cpu_count_reader,
        loadavg_reader=loadavg_reader,
        rss_reader=rss_reader,
    )
    if implementation.get("execution_state", {}).get("public_execution_consumed") is not False:
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "implementation is not pre-execution")
    private_parent = root / REAL_ROOT_RELATIVE_PATH.parent
    private_root = root / REAL_ROOT_RELATIVE_PATH
    public_result_path = root / REAL_PUBLIC_RESULT_RELATIVE_PATH
    if private_root.exists() or private_root.is_symlink() or public_result_path.exists() or public_result_path.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "registered execution is already consumed")
    _ensure_private_parent(root)
    if private_parent.is_symlink():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "private parent is a symlink")
    _make_exclusive_directory(private_root)
    marker_path, marker_bytes, _marker_sha256 = _write_consumed_marker(private_root, evidence)
    if not marker_path.is_file():
        raise PublicSnapshotRefusal(REFUSAL_IDS[2], "consumed marker was not created")
    counters = _base_access_counters()
    counters["private_consumed_markers"] = 1
    started = clock()
    stage = "transport"
    try:
        body, transport = perform_locked_transport(
            opener,
            counters=counters,
            public_request=True,
        )
        stage = "semantic_canonicalization"
        canonical = _canonicalize_public_body(
            body,
            contract=contract,
            counters=counters,
            public_request=True,
        )
        body = b""
        runtime = clock() - started
        peak_rss = int(rss_reader())
        _enforce_final_resources(runtime, peak_rss)
        manifest = _private_manifest(canonical, transport, generated=False)
        counters["private_selected_manifests"] = 1
        counters["public_aggregate_reports"] = 1
        report = _build_success_report(
            canonical,
            transport,
            generated=False,
            evidence=evidence,
            implementation_registry_sha256=implementation_hash,
            machine=machine,
            counters=counters,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            combined_output_bytes=0,
            incremental_disk_bytes=marker_bytes,
        )
        report_bytes, manifest_bytes, combined, incremental = _serialize_report_and_manifest(
            report,
            manifest,
            marker_bytes=marker_bytes,
        )
        if manifest_bytes is None:
            raise AssertionError("public private manifest is unavailable")
        manifest_path = private_root / REAL_PRIVATE_MANIFEST_NAME
        _write_exclusive(manifest_path, manifest_bytes, mode=0o600)
        _write_exclusive(public_result_path, report_bytes, mode=0o644)
        if incremental > MAX_INCREMENTAL_DISK_BYTES:
            raise PublicSnapshotRefusal(REFUSAL_IDS[6], "incremental disk cap failed")
        return PublicAuditOutcome(
            report=report,
            report_path=public_result_path,
            private_manifest_path=manifest_path,
            runtime_seconds=runtime,
            peak_rss_bytes=peak_rss,
            combined_output_bytes=combined,
        )
    except PublicSnapshotRefusal as exc:
        if not public_result_path.exists() and not public_result_path.is_symlink():
            _write_consumed_failure_report(
                public_result_path,
                refusal=exc,
                stage=stage,
                evidence=evidence,
                implementation_registry_sha256=implementation_hash,
                machine=machine,
                counters=counters,
                started=started,
                clock=clock,
                rss_reader=rss_reader,
                marker_bytes=marker_bytes,
            )
        raise


def inspect_public_result(path: str | Path) -> dict[str, Any]:
    """Inspect only an aggregate result; private row manifests are refused."""

    report_path = Path(path)
    if report_path.name == REAL_PRIVATE_MANIFEST_NAME:
        raise PublicSnapshotRefusal(REFUSAL_IDS[6], "private manifest inspection is forbidden")
    report, _, _ = _read_locked_json(report_path, expected_sha256=None)
    validate_public_result(report)
    return report


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return a zero-network plan without opening any IACKD payload path."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    load_green_decision(root)
    return {
        "lane_id": "IACKD-M1A",
        "provider": "OpenNeuro",
        "dataset_accession": "ds006840",
        "snapshot_tag": "1.0.0",
        "request_body_bytes": REQUEST_BYTES,
        "response_body_cap_bytes": MAX_RESPONSE_BYTES,
        "GraphQL_requests_made": 0,
        "S3_payload_requests": 0,
        "local_IACKD_path_operations": 0,
        "execution_requires_exact_green_wrapper_evidence": True,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.iackd_snapshot_identity_public",
        description="Bounded IACKD public snapshot metadata identity wrapper.",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("plan", help="Print the zero-network registered plan.")
    qualify = subparsers.add_parser("qualify", help="Run generated/mock qualification.")
    qualify.add_argument("--output-dir", required=True)
    inspect = subparsers.add_parser("inspect", help="Inspect an aggregate result.")
    inspect.add_argument("report")
    execute = subparsers.add_parser("execute", help="Consume the one registered public response.")
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
            print(json.dumps(registered_plan(), sort_keys=True))
            return 0
        if args.command == "qualify":
            outcome = qualify_generated_mock_wrapper(args.output_dir)
            print(
                json.dumps(
                    {
                        "status": outcome.report["status"],
                        "route": outcome.report["route"],
                        "runtime_seconds": outcome.runtime_seconds,
                        "peak_RSS_bytes": outcome.peak_rss_bytes,
                        "combined_output_bytes": outcome.combined_output_bytes,
                        "report": str(outcome.report_path),
                    },
                    sort_keys=True,
                )
            )
            return 0
        if args.command == "inspect":
            report = inspect_public_result(args.report)
            print(
                json.dumps(
                    {
                        "status": report["status"],
                        "route": report["route"],
                        "tree_summary": report["tree_summary"],
                        "selected_summary": report["selected_summary"],
                        "warnings": report["warnings"],
                        "unavailable_fields": report["unavailable_fields"],
                    },
                    sort_keys=True,
                )
            )
            return 0
        evidence = GreenWrapperEvidence(
            implementation_commit=args.implementation_commit,
            implementation_ci_run_id=args.implementation_ci_run_id,
            implementation_base_job_id=args.implementation_base_job_id,
            implementation_optional_job_id=args.implementation_optional_job_id,
            implementation_registry_sha256=args.implementation_registry_sha256,
        )
        outcome = execute_registered_public_audit(_repo_root(), evidence=evidence)
        print(
            json.dumps(
                {
                    "status": outcome.report["status"],
                    "route": outcome.report["route"],
                    "report": str(outcome.report_path),
                },
                sort_keys=True,
            )
        )
        return 0
    except PublicSnapshotRefusal as exc:
        print(
            json.dumps({"status": "refused", "refusal_id": exc.refusal_id}),
            file=sys.stderr,
            sort_keys=True,
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
