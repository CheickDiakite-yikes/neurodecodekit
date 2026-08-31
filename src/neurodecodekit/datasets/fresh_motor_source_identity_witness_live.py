"""Execution-locked live adapter for the FMSR1 source-identity witness.

The generated core owns pagination semantics and the canonical hash contract.
This module adds only the separately bound local-proof, marker, direct-TLS,
resource, and variable-length traversal surfaces needed by one live witness.
"""

from __future__ import annotations

import base64
import hashlib
import http.client
import ipaddress
import os
import resource
import signal
import shutil
import socket
import ssl
import stat
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

from neurodecodekit.datasets import fresh_motor_source_identity_witness as core


SCHEMA_VERSION = "0.1.0"
PACKET_ID = core.PACKET_ID
LIVE_IMPLEMENTATION_ID = "FMSR1-R1-W-I1"
LIVE_IMPLEMENTATION_DECISION_ID = "FMSR1-R1-W-I1-D0"
LIVE_IMPLEMENTATION_DECISION_COMMIT = "0c50299dc5223ba0f2b1f337beded51038bffd4d"
LIVE_IMPLEMENTATION_DECISION_CI_RUN_ID = 33_364_407_489
LIVE_IMPLEMENTATION_DECISION_BASE_JOB_ID = 99_401_989_268
LIVE_IMPLEMENTATION_DECISION_OPTIONAL_JOB_ID = 99_401_989_133
LIVE_IMPLEMENTATION_DECISION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_identity_witness_live_implementation_decision.v0.json"
)
LIVE_IMPLEMENTATION_DECISION_BYTES = 4_550
LIVE_IMPLEMENTATION_DECISION_SHA256 = (
    "851125e927aa18d3faf7c94bbd093b28b844de5cd849fc42656c02d1cd152e3b"
)
LIVE_IMPLEMENTATION_DECISION_GIT_BLOB = "731d3925012dd810e7d1fa71e83f6e26bebc9597"
EXECUTION_DECISION_ID = "FMSR1-R1-W-E0-D0"
EXECUTION_DECISION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_identity_witness_execution_decision.v0.json"
)
LIVE_IMPLEMENTATION_RECORD_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_identity_witness_live_implementation.v0.json"
)
OFFICIAL_ROOT_RELATIVE_PATH = Path(".codex_work/fmsr1-r1-w-v0-official")
CONSUMED_MARKER_NAME = "consumed.json"
LEDGER_NAME = "witness_ledger.json"
RESULT_NAME = "result.json"

REPOSITORY_ID = 1_284_309_460
OWNER_ID = 112_525_078
WORKFLOW_PATH = ".github/workflows/ci.yml"
WORKFLOW_BLOB_SHA1 = "4246b7c7f6f8570df53b1b89705b496b30e38a78"
WORKFLOW_SHA256 = "53ea7e06c7989c7e3ae8030eafe7184aad4916fcefca2f8cfcc05ba7a87c2fc3"
WORKFLOW_BYTES = 3_040

PACKET_ARTIFACTS = (
    {
        "path": "docs/FRESH_MOTOR_SOURCE_IDENTITY_WITNESS_AUTHORIZATION_PACKET.md",
        "bytes": 11_780,
        "sha256": "6d9343673713a650ad5d1f2ef06574887aba68aeba947bc373a9f88d542430a2",
        "git_blob": "3e61f44dfeea0e0f763a725ea79bfee8eb717717",
    },
    {
        "path": "registries/fresh_motor_source_identity_witness_authorization_request.v0.json",
        "bytes": 48_747,
        "sha256": "e805ffc8b2a963055c075fe002c83b6c4e6e2348f865dc07f41051dd7968d3f6",
        "git_blob": "73ea1fa1808a7edaa2c8c1e65204e902497fbe5f",
    },
)

MAX_RUNTIME_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_CI_REQUESTS = 3
MAX_CI_RESPONSE_BYTES = 1024**2
MAX_CI_BYTES = 3 * 1024**2
MAX_SOURCE_REQUESTS = 125
MAX_TOTAL_REQUESTS = 128
MAX_SOURCE_WIRE_BYTES = 32 * 1024**2
MAX_SOURCE_ENTITY_BYTES = 32 * 1024**2
MAX_PAGE_BYTES = 8 * 1024**2
MAX_RETAINED_BYTES = 1024**2
MAX_TEMPORARY_BYTES = 2 * 1024**2
MINIMUM_FREE_DISK_BYTES = 2 * 1024**3
MAX_REDIRECTS = 3
MAX_REQUEST_SECONDS = 30.0
MAX_CI_REQUEST_SECONDS = 10.0
MAX_CI_SECONDS = 30.0
MAX_SERVER_DATE_SKEW_SECONDS = 300.0
FINALIZATION_RESERVE_SECONDS = 1.0
MAX_CONTROL_BYTES = 4_096
READ_CHUNK_BYTES = 64 * 1024
SYSTEM_GIT_EXECUTABLE = Path("/usr/bin/git")
ALLOWED_LOCAL_GIT_SUBCOMMANDS = frozenset(
    {"merge-base", "rev-parse", "show", "status", "symbolic-ref"}
)
HERMETIC_GIT_CONFIG = (
    ("core.fsmonitor", "false"),
    ("core.hooksPath", os.devnull),
    ("credential.helper", ""),
    ("status.submoduleSummary", "false"),
)
STATE_MACHINE = (
    "CLOSED",
    "LOCAL_PREFLIGHT",
    "RESERVED_PENDING",
    "ARMED_CONSUMED",
    "CI_W0",
    "SEVENTEEN_ROOT_WITNESS",
    "FINALIZE",
    "COMPLETE_OR_PARK",
)

CI_HOST = "api.github.com"
CI_USER_AGENT = (
    "NeuroDecodeKit-FMSR1-R1-W-v0-CI-W0/0.1 "
    "(+https://github.com/CheickDiakite-yikes/neurodecodekit)"
)
CI_HEADERS = (
    ("User-Agent", CI_USER_AGENT),
    ("Accept", "application/vnd.github+json"),
    ("X-GitHub-Api-Version", "2022-11-28"),
    ("Accept-Encoding", "identity"),
    ("Connection", "close"),
    ("Host", CI_HOST),
)
CI_MAIN_PATH = "/repos/CheickDiakite-yikes/neurodecodekit/git/ref/heads/main"
CI_CHECKS_TEMPLATE = (
    "/repos/CheickDiakite-yikes/neurodecodekit/commits/{head}/check-runs?per_page=100&page=1"
)
CI_WORKFLOW_PATH = "/repos/CheickDiakite-yikes/neurodecodekit/git/blobs/" + WORKFLOW_BLOB_SHA1

THREAD_ENV_KEYS = core.THREAD_ENV_KEYS
FORBIDDEN_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
    "REQUESTS_CA_BUNDLE",
    "CURL_CA_BUNDLE",
    "SSL_CERT_FILE",
    "SSL_CERT_DIR",
    "GH_TOKEN",
    "GITHUB_TOKEN",
    "NETRC",
)
FORBIDDEN_GIT_ENV_KEYS = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_CONFIG",
    "GIT_CONFIG_COUNT",
    "GIT_DIR",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_EXEC_PATH",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
}
SINGLETON_RESPONSE_HEADERS = {
    "age",
    "content-encoding",
    "content-length",
    "content-type",
    "date",
    "location",
    "transfer-encoding",
}
LIVE_WARNINGS = tuple(
    sorted(
        {
            "Candidate entity bytes were read only to count and hash them.",
            "Candidate science fields were not semantically decoded or retained.",
            "No payload, neural signal, target, model, prediction, or score was accessed.",
        }
    )
)
LIVE_UNAVAILABLE_FIELDS = tuple(
    sorted(
        {
            "candidate metadata or source eligibility",
            "EEG EOG EMG signal or geometry",
            "target label event annotation or trial",
            "model prediction score or neural advantage",
            "end-to-end live decoding latency",
        }
    )
)

REFUSAL_CODES = (
    "LIVE_AUTHORITY_REFUSE",
    "LIVE_PATH_REFUSE",
    "LIVE_ENVIRONMENT_REFUSE",
    "LIVE_RESOURCE_REFUSE",
    "LIVE_CI_REFUSE",
    "LIVE_TRANSPORT_REFUSE",
    "LIVE_OUTPUT_REFUSE",
)
EXECUTION_DECISION_STATUS = "one_live_source_witness_effective_only_after_decision_remote_green"
EXECUTION_AUTHORITY = {
    "one_consumed_same_process_live_witness": True,
    "three_request_CI_W0": True,
    "five_profile_seventeen_root_source_witness": True,
    "opaque_candidate_byte_count_and_hash_only": True,
    "candidate_semantic_parsing_ranking_or_selection": False,
    "payload_header_signal_event_annotation_target_or_label": False,
    "model_checkpoint_training_inference_prediction_or_score": False,
    "language_model_provider_stream_device_or_hardware": False,
    "release_or_scientific_claim_upgrade": False,
    "retry_rerun_resume_repair_substitute_or_post_result_amend": False,
    "touch_other_project_or_delete_existing_path": False,
}
EXECUTION_DECISION_OPERATION_COUNTERS = {
    "network_requests": 0,
    "network_bytes": 0,
    "official_index_requests": 0,
    "candidate_semantic_operations": 0,
    "source_selections": 0,
    "payload_or_neural_reads": 0,
    "target_or_label_reads": 0,
    "model_runs": 0,
    "training_runs": 0,
    "prediction_sets": 0,
    "scoring_events": 0,
    "scientific_claim_upgrades": 0,
    "end_to_end_latency_measured": False,
}
EXECUTION_NEXT_BARRIERS = {
    "decision_commit_push_and_both_jobs_green_before_network": True,
    "runtime_clean_local_main_must_equal_live_remote_main": True,
    "durable_consumed_marker_before_first_DNS_or_socket": True,
    "one_invocation_no_retry_or_rerun": True,
    "result_commit_push_and_both_jobs_green_before_D1_packet": True,
    "candidate_or_payload_authority": False,
    "model_or_scoring_authority": False,
    "scientific_claim_upgrade_authority": False,
}
EXECUTION_DECISION_ROOT_FIELDS = {
    "schema_name",
    "schema_version",
    "decision_id",
    "packet_id",
    "recorded_at",
    "status",
    "effective_only_after_decision_commit_pushed_and_both_CI_jobs_green",
    "maintainer_words",
    "maintainer_words_utf8_bytes",
    "maintainer_words_sha256",
    "packet_artifacts",
    "repository_identity",
    "workflow_identity",
    "green_live_implementation",
    "CI_W0_profile",
    "authorization_after_decision_green",
    "decision_only_operation_counters",
    "next_barriers",
    "claim_boundary",
}
RESULT_BASE_FIELDS = {
    "schema_name",
    "schema_version",
    "packet_id",
    "packet_sha256",
    "implementation_id",
    "implementation_commit",
    "implementation_artifact_set_sha256",
    "execution_decision_id",
    "execution_decision_commit",
    "execution_decision_sha256",
    "CI_W0_profile_sha256",
    "route",
    "state_transcript",
    "runtime_seconds",
    "runtime_measurement_endpoint",
    "peak_RSS_bytes",
    "peak_RSS_measurement_endpoint",
    "CPU_threads",
    "workers",
    "numerical_jobs",
    "producer_is_causal",
    "end_to_end_latency_measured",
    "operation_counters",
    "warnings",
    "unavailable_fields",
    "claim_boundary",
    "consumed_marker_bytes",
    "CI_W0_receipt",
    "ledger_artifact_bytes",
    "result_artifact_bytes",
    "retained_artifact_bytes",
    "temporary_artifact_bytes",
}
RESULT_COMPLETE_FIELDS = {
    "profile_count",
    "root_count",
    "page_count",
    "global_ledger_sha256",
    "source_index_snapshot_identity_established",
}


class LiveWitnessRefusal(RuntimeError):
    """Sanitized refusal raised by the live adapter."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code if code in REFUSAL_CODES else "LIVE_AUTHORITY_REFUSE"
        super().__init__(message)


class LiveWitnessPark(RuntimeError):
    """Consumed scientific route that parks without exposing protected bytes."""

    def __init__(self, route: str, reason_class: str) -> None:
        if route not in {"WITNESS_CAP_PARK", "WITNESS_TRANSPORT_PARK"}:
            raise ValueError("unknown witness park route")
        self.route = route
        self.reason_class = reason_class
        super().__init__(f"{route}:{reason_class}")


@dataclass(frozen=True, slots=True)
class PreparedRequest:
    method: str
    url: str
    headers: tuple[tuple[str, str], ...]
    body: bytes
    request_identity_sha256: str
    kind: str
    maximum_response_bytes: int | None = None
    maximum_wire_response_bytes: int | None = None


@dataclass(frozen=True, slots=True)
class ContactResult:
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    DNS_answer_set_sha256: str
    selected_peer_sha256: str
    post_connect_peer_sha256: str
    selected_and_post_connect_peer_equal_and_global: bool
    TLS_version: str
    response_headers_sha256: str
    content_encoding: str
    transfer_framing: str
    wire_body_bytes: int
    request_elapsed_nanoseconds: int
    whole_invocation_elapsed_nanoseconds: int


@dataclass(frozen=True, slots=True)
class TerminalExchange:
    request_identity_sha256: str
    terminal_url: str
    terminal_body: bytes
    media_type: str
    charset: str
    response_body: bytes
    response_headers: tuple[tuple[str, str], ...]
    redirect_transcript: tuple[Mapping[str, object], ...]
    transport_evidence: Mapping[str, object]


@dataclass(slots=True)
class RequestBudget:
    started: float
    CI_requests: int = 0
    CI_bytes: int = 0
    source_requests: int = 0
    source_wire_bytes: int = 0
    source_entity_bytes: int = 0
    total_requests: int = 0

    def claim(self, kind: str) -> int:
        if self.total_requests >= MAX_TOTAL_REQUESTS:
            raise LiveWitnessPark("WITNESS_CAP_PARK", "TOTAL_REQUEST_CAP")
        if kind == "CI":
            if self.CI_requests >= MAX_CI_REQUESTS:
                raise LiveWitnessPark("WITNESS_CAP_PARK", "CI_REQUEST_CAP")
            self.CI_requests += 1
        elif kind == "SOURCE":
            if self.source_requests >= MAX_SOURCE_REQUESTS:
                raise LiveWitnessPark("WITNESS_CAP_PARK", "SOURCE_REQUEST_CAP")
            self.source_requests += 1
        else:
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "request kind differs")
        ordinal = self.total_requests
        self.total_requests += 1
        return ordinal

    def add_body(self, kind: str, wire_bytes: int, entity_bytes: int) -> None:
        if wire_bytes < 0 or entity_bytes < 0 or wire_bytes < entity_bytes:
            raise LiveWitnessRefusal("LIVE_RESOURCE_REFUSE", "negative byte count")
        if kind == "CI":
            self.CI_bytes += entity_bytes
            if self.CI_bytes > MAX_CI_BYTES:
                raise LiveWitnessPark("WITNESS_CAP_PARK", "CI_BYTE_CAP")
        else:
            self.source_wire_bytes += wire_bytes
            self.source_entity_bytes += entity_bytes
            if (
                self.source_wire_bytes > MAX_SOURCE_WIRE_BYTES
                or self.source_entity_bytes > MAX_SOURCE_ENTITY_BYTES
            ):
                raise LiveWitnessPark("WITNESS_CAP_PARK", "SOURCE_BYTE_CAP")


@dataclass(slots=True)
class SemanticAccessAudit:
    candidate_semantic_accesses: int = 0
    control_fields_accessed: int = 0
    opaque_members_skipped: int = 0


@dataclass(frozen=True, slots=True)
class ExecutionAuthority:
    decision: Mapping[str, object]
    decision_payload: bytes
    decision_sha256: str
    decision_git_blob: str
    local_HEAD: str
    implementation_commit: str
    implementation_artifact_set_sha256: str
    CI_W0_profile_sha256: str


@dataclass(frozen=True, slots=True)
class AttemptReservation:
    attempt_root: Path
    marker_payload: bytes
    attempt_device: int
    attempt_inode: int


ContactCallable = Callable[[PreparedRequest, int, float, float], ContactResult]


class _CountingReader:
    def __init__(self, raw: object) -> None:
        self.raw = raw
        self.total_bytes = 0
        self.body_start_bytes: int | None = None
        self.body_limit_bytes: int | None = None

    @property
    def body_bytes(self) -> int:
        if self.body_start_bytes is None:
            return 0
        return self.total_bytes - self.body_start_bytes

    def begin_body(self, maximum_wire_bytes: int) -> None:
        if self.body_start_bytes is not None or maximum_wire_bytes < 0:
            raise LiveWitnessRefusal("LIVE_RESOURCE_REFUSE", "wire counter state differs")
        self.body_start_bytes = self.total_bytes
        self.body_limit_bytes = maximum_wire_bytes

    def _bounded_size(self, requested: int | None) -> int:
        if self.body_limit_bytes is None:
            return -1 if requested is None else requested
        remaining = self.body_limit_bytes - self.body_bytes
        cap_plus_one = remaining + 1
        if requested is None or requested < 0 or requested > cap_plus_one:
            return cap_plus_one
        return requested

    def _record(self, payload: bytes) -> bytes:
        self.total_bytes += len(payload)
        if self.body_limit_bytes is not None and self.body_bytes > self.body_limit_bytes:
            raise LiveWitnessPark("WITNESS_CAP_PARK", "WIRE_BYTE_CAP")
        return payload

    def read(self, size: int = -1) -> bytes:
        return self._record(self.raw.read(self._bounded_size(size)))  # type: ignore[attr-defined,no-any-return]

    def readline(self, size: int = -1) -> bytes:
        return self._record(self.raw.readline(self._bounded_size(size)))  # type: ignore[attr-defined,no-any-return]

    def readinto(self, buffer: object) -> int:
        view = memoryview(buffer)  # type: ignore[arg-type]
        payload = self.read(len(view))
        view[: len(payload)] = payload
        return len(payload)

    def close(self) -> None:
        self.raw.close()  # type: ignore[attr-defined]

    def __getattr__(self, name: str) -> object:
        return getattr(self.raw, name)


class _NoInterimHTTPResponse(http.client.HTTPResponse):
    def _read_status(self) -> tuple[str, int, str]:
        version, status, reason = super()._read_status()
        if status < 200:
            raise http.client.HTTPException("interim HTTP response is forbidden")
        return version, status, reason


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_CI_W0_profile() -> dict[str, object]:
    return {
        "host": CI_HOST,
        "method": "GET",
        "request_body_bytes": 0,
        "request_count": MAX_CI_REQUESTS,
        "maximum_request_seconds_each": MAX_CI_REQUEST_SECONDS,
        "maximum_total_seconds": MAX_CI_SECONDS,
        "maximum_response_bytes_each": MAX_CI_RESPONSE_BYTES,
        "maximum_response_bytes_cumulative": MAX_CI_BYTES,
        "maximum_server_date_skew_seconds": MAX_SERVER_DATE_SKEW_SECONDS,
        "redirects_allowed": False,
        "system_CA_only": True,
        "globally_routable_peer_required": True,
        "TLS_minimum_version": "TLSv1.2",
        "main_ref_path": CI_MAIN_PATH,
        "check_runs_path_template": CI_CHECKS_TEMPLATE,
        "workflow_blob_path": CI_WORKFLOW_PATH,
        "headers": [list(row) for row in CI_HEADERS],
    }


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if os.uname().sysname == "Darwin" else value * 1024)


def _git(repo_root: Path, *arguments: str) -> str:
    if not arguments or arguments[0] not in ALLOWED_LOCAL_GIT_SUBCOMMANDS:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "local Git command is not allowlisted")
    try:
        executable = os.lstat(SYSTEM_GIT_EXECUTABLE)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "system Git is unavailable") from exc
    if (
        stat.S_ISLNK(executable.st_mode)
        or not stat.S_ISREG(executable.st_mode)
        or executable.st_uid != 0
        or executable.st_mode & 0o111 == 0
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "system Git identity differs")
    command = [str(SYSTEM_GIT_EXECUTABLE)]
    for key, value in HERMETIC_GIT_CONFIG:
        command.extend(("-c", f"{key}={value}"))
    command.extend(arguments)
    environment = {
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_PAGER": "cat",
        "GIT_TERMINAL_PROMPT": "0",
        "HOME": "/nonexistent",
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/usr/bin:/bin",
    }
    try:
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=15,
            stdin=subprocess.DEVNULL,
            env=environment,
            close_fds=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "local Git proof failed") from exc
    return completed.stdout


def _read_regular_nofollow(path: Path, maximum_bytes: int = MAX_RETAINED_BYTES) -> bytes:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "bound artifact is absent") from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or not 0 < info.st_size <= maximum_bytes
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "bound artifact shape differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        held = os.fstat(descriptor)
        current = os.lstat(path)
        if (
            not stat.S_ISREG(held.st_mode)
            or held.st_nlink != 1
            or (held.st_dev, held.st_ino) != (info.st_dev, info.st_ino)
            or (held.st_dev, held.st_ino) != (current.st_dev, current.st_ino)
        ):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "bound artifact identity changed")
        chunks: list[bytes] = []
        observed = 0
        while True:
            chunk = os.read(descriptor, min(READ_CHUNK_BYTES, maximum_bytes + 1 - observed))
            if not chunk:
                break
            observed += len(chunk)
            if observed > maximum_bytes:
                raise LiveWitnessRefusal("LIVE_RESOURCE_REFUSE", "artifact read cap exceeded")
            chunks.append(chunk)
        payload = b"".join(chunks)
        final = os.fstat(descriptor)
        current = os.lstat(path)
        if (
            (final.st_dev, final.st_ino, final.st_size) != (held.st_dev, held.st_ino, held.st_size)
            or (current.st_dev, current.st_ino, current.st_size)
            != (held.st_dev, held.st_ino, held.st_size)
            or len(payload) != held.st_size
        ):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "bound artifact changed during read")
        return payload
    finally:
        os.close(descriptor)


def _strict_mapping(payload: bytes) -> Mapping[str, object]:
    try:
        value = core.strict_json_loads(payload)
    except core.WitnessRefusal as exc:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision JSON differs") from exc
    if not isinstance(value, Mapping):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision root differs")
    return value


def _canonical_artifact_set(rows: object) -> tuple[list[Mapping[str, object]], str]:
    if not isinstance(rows, list) or not rows:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact set is absent")
    projected: list[Mapping[str, object]] = []
    seen: set[str] = set()
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact row differs")
        if set(raw) != {"path", "bytes", "sha256", "git_blob"}:
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact fields differ")
        path = raw.get("path")
        size = raw.get("bytes")
        digest = raw.get("sha256")
        blob = raw.get("git_blob")
        if (
            not isinstance(path, str)
            or not path
            or path.startswith("/")
            or ".." in Path(path).parts
            or path in seen
            or not isinstance(size, int)
            or isinstance(size, bool)
            or size <= 0
            or not isinstance(digest, str)
            or core.HEX_64.fullmatch(digest) is None
            or not isinstance(blob, str)
            or len(blob) != 40
            or any(character not in "0123456789abcdef" for character in blob)
        ):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact identity differs")
        seen.add(path)
        projected.append(raw)
    return projected, _sha256(core.canonical_json_bytes(projected))


def _artifact_identity(value: object, *, expected_path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != {
        "path",
        "bytes",
        "sha256",
        "git_blob",
    }:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact identity differs")
    path = value.get("path")
    size = value.get("bytes")
    digest = value.get("sha256")
    blob = value.get("git_blob")
    if (
        path != expected_path
        or not isinstance(size, int)
        or isinstance(size, bool)
        or size <= 0
        or not isinstance(digest, str)
        or core.HEX_64.fullmatch(digest) is None
        or not isinstance(blob, str)
        or len(blob) != 40
        or any(character not in "0123456789abcdef" for character in blob)
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "artifact identity differs")
    return value


def validate_execution_decision(value: Mapping[str, object]) -> None:
    if (
        set(value) != EXECUTION_DECISION_ROOT_FIELDS
        or value.get("schema_name")
        != "neurodecodekit.fresh_motor_source_identity_witness_execution_decision"
        or value.get("schema_version") != SCHEMA_VERSION
        or value.get("decision_id") != EXECUTION_DECISION_ID
        or value.get("packet_id") != PACKET_ID
        or value.get("recorded_at") != "2026-08-31"
        or value.get("status") != EXECUTION_DECISION_STATUS
        or value.get("effective_only_after_decision_commit_pushed_and_both_CI_jobs_green")
        is not True
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "execution decision identity differs")
    repository = value.get("repository_identity")
    workflow = value.get("workflow_identity")
    implementation = value.get("green_live_implementation")
    CI_profile = value.get("CI_W0_profile")
    authority = value.get("authorization_after_decision_green")
    if not all(
        isinstance(row, Mapping)
        for row in (repository, workflow, implementation, CI_profile, authority)
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "execution decision section differs")
    assert isinstance(repository, Mapping)
    assert isinstance(workflow, Mapping)
    assert isinstance(implementation, Mapping)
    assert isinstance(CI_profile, Mapping)
    assert isinstance(authority, Mapping)
    if (
        set(repository)
        != {
            "numeric_repository_id",
            "numeric_owner_id",
            "numeric_head_repository_id",
            "numeric_head_owner_id",
        }
        or set(workflow) != {"path", "bytes", "sha256", "git_blob"}
        or set(implementation)
        != {
            "commit",
            "CI_run_id",
            "base_python_job_id",
            "base_python_job_conclusion",
            "optional_neuro_readers_job_id",
            "optional_neuro_readers_job_conclusion",
            "both_required_jobs_green",
            "on_GitHub_main",
            "implementation_record",
            "artifacts",
            "artifact_count",
            "artifact_set_sha256",
        }
        or set(CI_profile) != {"canonical_profile", "canonical_profile_sha256"}
        or repository.get("numeric_repository_id") != REPOSITORY_ID
        or repository.get("numeric_owner_id") != OWNER_ID
        or repository.get("numeric_head_repository_id") != REPOSITORY_ID
        or repository.get("numeric_head_owner_id") != OWNER_ID
        or workflow.get("path") != WORKFLOW_PATH
        or workflow.get("bytes") != WORKFLOW_BYTES
        or workflow.get("sha256") != WORKFLOW_SHA256
        or workflow.get("git_blob") != WORKFLOW_BLOB_SHA1
        or implementation.get("both_required_jobs_green") is not True
        or implementation.get("on_GitHub_main") is not True
        or implementation.get("base_python_job_conclusion") != "success"
        or implementation.get("optional_neuro_readers_job_conclusion") != "success"
        or any(
            not isinstance(implementation.get(name), int)
            or isinstance(implementation.get(name), bool)
            or int(implementation[name]) <= 0
            for name in (
                "CI_run_id",
                "base_python_job_id",
                "optional_neuro_readers_job_id",
            )
        )
    ):
        raise LiveWitnessRefusal(
            "LIVE_AUTHORITY_REFUSE", "repository or implementation proof differs"
        )
    implementation_commit = implementation.get("commit")
    if (
        not isinstance(implementation_commit, str)
        or len(implementation_commit) != 40
        or any(character not in "0123456789abcdef" for character in implementation_commit)
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "implementation commit differs")
    record_identity = _artifact_identity(
        implementation.get("implementation_record"),
        expected_path=LIVE_IMPLEMENTATION_RECORD_RELATIVE_PATH.as_posix(),
    )
    rows, set_digest = _canonical_artifact_set(implementation.get("artifacts"))
    if (
        implementation.get("artifact_count") != len(rows)
        or implementation.get("artifact_set_sha256") != set_digest
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "implementation artifact set differs")
    if any(row["path"] == record_identity["path"] for row in rows):
        raise LiveWitnessRefusal(
            "LIVE_AUTHORITY_REFUSE", "implementation record is self-referential"
        )
    packet_artifacts = value.get("packet_artifacts")
    if packet_artifacts != [dict(row) for row in PACKET_ARTIFACTS]:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "packet artifacts differ")
    words = value.get("maintainer_words")
    if (
        not isinstance(words, str)
        or not words
        or value.get("maintainer_words_utf8_bytes") != len(words.encode("utf-8"))
        or value.get("maintainer_words_sha256") != _sha256(words.encode("utf-8"))
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "maintainer words differ")
    expected_CI = canonical_CI_W0_profile()
    if (
        CI_profile.get("canonical_profile_sha256")
        != _sha256(core.canonical_json_bytes(expected_CI, newline=True))
        or CI_profile.get("canonical_profile") != expected_CI
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "CI-W0 profile differs")
    if authority != EXECUTION_AUTHORITY:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "execution authority differs")
    if value.get("decision_only_operation_counters") != EXECUTION_DECISION_OPERATION_COUNTERS:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision counters differ")
    if value.get("next_barriers") != EXECUTION_NEXT_BARRIERS:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision barriers differ")
    if value.get("claim_boundary") != core.CLAIM_BOUNDARY:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision claim boundary differs")


def load_execution_authority(repo_root: str | Path) -> ExecutionAuthority:
    root = Path(repo_root).resolve()
    decision_path = root / EXECUTION_DECISION_RELATIVE_PATH
    payload = _read_regular_nofollow(decision_path)
    decision = _strict_mapping(payload)
    validate_execution_decision(decision)

    branch = _git(root, "symbolic-ref", "--short", "HEAD").strip()
    head = _git(root, "rev-parse", "HEAD").strip()
    if branch != "main" or len(head) != 40 or any(ch not in "0123456789abcdef" for ch in head):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "clean local main is required")
    if _git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "working tree or index is not clean")
    tracked = _git(root, "show", f"{head}:{EXECUTION_DECISION_RELATIVE_PATH.as_posix()}").encode()
    if tracked != payload:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision blob differs from HEAD")
    decision_blob = _git(
        root, "rev-parse", f"{head}:{EXECUTION_DECISION_RELATIVE_PATH.as_posix()}"
    ).strip()
    if decision_blob != _git_blob(payload):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "decision Git blob differs")

    implementation = decision["green_live_implementation"]
    assert isinstance(implementation, Mapping)
    implementation_commit = str(implementation["commit"])
    rows, artifact_set_sha256 = _canonical_artifact_set(implementation["artifacts"])
    record_identity = _artifact_identity(
        implementation.get("implementation_record"),
        expected_path=LIVE_IMPLEMENTATION_RECORD_RELATIVE_PATH.as_posix(),
    )
    record_path = root / str(record_identity["path"])
    record_payload = _read_regular_nofollow(record_path, max(int(record_identity["bytes"]), 1))
    committed_record = _git(
        root, "show", f"{implementation_commit}:{record_identity['path']}"
    ).encode()
    if (
        record_payload != committed_record
        or len(record_payload) != record_identity["bytes"]
        or _sha256(record_payload) != record_identity["sha256"]
        or _git_blob(record_payload) != record_identity["git_blob"]
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "implementation record drifted")
    record = _strict_mapping(record_payload)
    if (
        record.get("schema_name")
        != "neurodecodekit.fresh_motor_source_identity_witness_live_implementation"
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("packet_id") != PACKET_ID
        or record.get("implementation_id") != LIVE_IMPLEMENTATION_ID
        or record.get("implementation_artifacts") != [dict(row) for row in rows]
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "implementation record differs")
    for row in rows:
        path = str(row["path"])
        current = _read_regular_nofollow(root / path, max(int(row["bytes"]), 1))
        committed = _git(root, "show", f"{implementation_commit}:{path}").encode()
        if (
            current != committed
            or len(current) != row["bytes"]
            or _sha256(current) != row["sha256"]
            or _git_blob(current) != row["git_blob"]
        ):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "implementation artifact drifted")
    if _git(root, "merge-base", "--is-ancestor", implementation_commit, head).strip():
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "unexpected merge-base output")

    CI_profile = decision["CI_W0_profile"]
    assert isinstance(CI_profile, Mapping)
    return ExecutionAuthority(
        decision=decision,
        decision_payload=payload,
        decision_sha256=_sha256(payload),
        decision_git_blob=decision_blob,
        local_HEAD=head,
        implementation_commit=implementation_commit,
        implementation_artifact_set_sha256=artifact_set_sha256,
        CI_W0_profile_sha256=str(CI_profile["canonical_profile_sha256"]),
    )


def _validate_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise LiveWitnessRefusal("LIVE_ENVIRONMENT_REFUSE", "one-thread environment differs")
    if any(environ.get(key) for key in FORBIDDEN_ENV_KEYS):
        raise LiveWitnessRefusal(
            "LIVE_ENVIRONMENT_REFUSE", "proxy, CA, or credential environment is set"
        )
    if any(
        value
        and (
            key in FORBIDDEN_GIT_ENV_KEYS
            or key.startswith("GIT_CONFIG_KEY_")
            or key.startswith("GIT_CONFIG_VALUE_")
        )
        for key, value in environ.items()
    ):
        raise LiveWitnessRefusal("LIVE_ENVIRONMENT_REFUSE", "Git environment override is set")


def _validate_repo_directory(repo_root: Path) -> os.stat_result:
    try:
        info = os.lstat(repo_root)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "repository root is unavailable") from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "repository root shape differs")
    return info


def local_preflight(
    repo_root: str | Path,
    *,
    environ: Mapping[str, str] | None = None,
) -> ExecutionAuthority:
    root = Path(repo_root).resolve()
    _validate_environment(os.environ if environ is None else environ)
    _validate_repo_directory(root)
    authority = load_execution_authority(root)
    try:
        packet = core.load_packet(root)
        core.build_root_plan(root)
    except core.WitnessRefusal as exc:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "packet or root plan differs") from exc
    if packet.get("packet_id") != PACKET_ID:
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "packet identity differs")
    for row in PACKET_ARTIFACTS:
        payload = _read_regular_nofollow(root / row["path"], int(row["bytes"]))
        if (
            len(payload) != row["bytes"]
            or _sha256(payload) != row["sha256"]
            or _git_blob(payload) != row["git_blob"]
        ):
            raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "packet artifact drifted")
    workflow = _read_regular_nofollow(root / WORKFLOW_PATH, WORKFLOW_BYTES)
    if (
        len(workflow) != WORKFLOW_BYTES
        or _sha256(workflow) != WORKFLOW_SHA256
        or _git_blob(workflow) != WORKFLOW_BLOB_SHA1
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "workflow identity differs")
    free_disk = shutil.disk_usage(root).free
    if free_disk < MINIMUM_FREE_DISK_BYTES:
        raise LiveWitnessRefusal("LIVE_RESOURCE_REFUSE", "free disk floor is not met")
    official_root = root / OFFICIAL_ROOT_RELATIVE_PATH
    try:
        os.lstat(official_root)
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "official root preflight failed") from exc
    else:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "official witness has already been reserved")
    return authority


def _open_directory(path: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "directory admission failed") from exc
    try:
        info = os.fstat(descriptor)
        current = os.lstat(path)
        if (
            not stat.S_ISDIR(info.st_mode)
            or stat.S_ISLNK(current.st_mode)
            or (info.st_dev, info.st_ino) != (current.st_dev, current.st_ino)
        ):
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "directory identity changed")
    except Exception:
        os.close(descriptor)
        raise
    return descriptor


def _recheck_directory(path: Path, descriptor: int) -> os.stat_result:
    try:
        held = os.fstat(descriptor)
        current = os.lstat(path)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "directory recheck failed") from exc
    if (
        not stat.S_ISDIR(held.st_mode)
        or stat.S_ISLNK(current.st_mode)
        or not stat.S_ISDIR(current.st_mode)
        or (held.st_dev, held.st_ino) != (current.st_dev, current.st_ino)
    ):
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "directory identity changed")
    return held


def _write_exclusive_at(
    directory_descriptor: int,
    name: str,
    payload: bytes,
    *,
    mode: int = 0o600,
) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, mode, dir_fd=directory_descriptor)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "exclusive artifact creation failed") from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_nlink != 1
            or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != mode
        ):
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "artifact mode differs")
        offset = 0
        while offset < len(payload):
            written = os.write(descriptor, payload[offset:])
            if written <= 0:
                raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "artifact write did not advance")
            offset += written
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def reserve_consumed_attempt(
    repo_root: str | Path,
    authority: ExecutionAuthority,
) -> AttemptReservation:
    root = Path(repo_root).resolve()
    root_info = _validate_repo_directory(root)
    repository_descriptor = _open_directory(root)
    work_descriptor = -1
    attempt_descriptor = -1
    try:
        work_name = OFFICIAL_ROOT_RELATIVE_PATH.parts[0]
        work_path = root / work_name
        try:
            work_info = os.lstat(work_path)
        except FileNotFoundError:
            try:
                os.mkdir(work_name, 0o700, dir_fd=repository_descriptor)
                os.fsync(repository_descriptor)
            except OSError as exc:
                raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "work root creation failed") from exc
            work_info = os.lstat(work_path)
        if (
            stat.S_ISLNK(work_info.st_mode)
            or not stat.S_ISDIR(work_info.st_mode)
            or work_info.st_uid != os.getuid()
            or bool(work_info.st_mode & 0o022)
            or work_info.st_dev != root_info.st_dev
        ):
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "work root admission differs")
        os.fsync(repository_descriptor)
        work_descriptor = _open_directory(work_path)
        held_work = _recheck_directory(work_path, work_descriptor)
        if held_work.st_dev != root_info.st_dev:
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "work root device differs")

        attempt_name = OFFICIAL_ROOT_RELATIVE_PATH.parts[1]
        try:
            os.mkdir(attempt_name, 0o700, dir_fd=work_descriptor)
            os.fsync(work_descriptor)
        except OSError as exc:
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "attempt reservation failed") from exc
        attempt_path = work_path / attempt_name
        attempt_descriptor = _open_directory(attempt_path)
        attempt_info = os.fstat(attempt_descriptor)
        if (
            attempt_info.st_uid != os.getuid()
            or stat.S_IMODE(attempt_info.st_mode) != 0o700
            or attempt_info.st_dev != root_info.st_dev
        ):
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "attempt directory mode differs")

        marker = {
            "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_consumed_marker",
            "schema_version": SCHEMA_VERSION,
            "packet_id": PACKET_ID,
            "packet_sha256": core.PACKET_SHA256,
            "implementation_commit": authority.implementation_commit,
            "implementation_artifact_set_sha256": authority.implementation_artifact_set_sha256,
            "execution_decision_id": EXECUTION_DECISION_ID,
            "execution_decision_commit": authority.local_HEAD,
            "execution_decision_sha256": authority.decision_sha256,
            "CI_W0_profile_sha256": authority.CI_W0_profile_sha256,
            "stage": "FMSR1_R1_W",
            "state": "ARMED_CONSUMED",
        }
        marker_payload = core.canonical_json_bytes(marker, newline=True)
        _write_exclusive_at(attempt_descriptor, CONSUMED_MARKER_NAME, marker_payload)
        os.fsync(attempt_descriptor)
        held_attempt = _recheck_directory(attempt_path, attempt_descriptor)
        held_work = _recheck_directory(work_path, work_descriptor)
        held_root = _recheck_directory(root, repository_descriptor)
        if not (held_attempt.st_dev == held_work.st_dev == held_root.st_dev == root_info.st_dev):
            raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "directory device changed")
        return AttemptReservation(
            attempt_root=attempt_path,
            marker_payload=marker_payload,
            attempt_device=attempt_info.st_dev,
            attempt_inode=attempt_info.st_ino,
        )
    finally:
        if attempt_descriptor >= 0:
            os.close(attempt_descriptor)
        if work_descriptor >= 0:
            os.close(work_descriptor)
        os.close(repository_descriptor)


def verify_consumed_marker(reservation: AttemptReservation) -> None:
    attempt_root = reservation.attempt_root
    marker_payload = reservation.marker_payload
    try:
        attempt = os.lstat(attempt_root)
        marker = os.lstat(attempt_root / CONSUMED_MARKER_NAME)
    except OSError as exc:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "consumed marker is absent") from exc
    if (
        stat.S_ISLNK(attempt.st_mode)
        or not stat.S_ISDIR(attempt.st_mode)
        or stat.S_IMODE(attempt.st_mode) != 0o700
        or stat.S_ISLNK(marker.st_mode)
        or not stat.S_ISREG(marker.st_mode)
        or marker.st_nlink != 1
        or marker.st_uid != os.getuid()
        or stat.S_IMODE(marker.st_mode) != 0o600
        or marker.st_dev != attempt.st_dev
        or attempt.st_dev != reservation.attempt_device
        or attempt.st_ino != reservation.attempt_inode
    ):
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "consumed marker shape differs")
    observed = _read_regular_nofollow(
        attempt_root / CONSUMED_MARKER_NAME, max(len(marker_payload), 1)
    )
    if observed != marker_payload:
        raise LiveWitnessRefusal("LIVE_PATH_REFUSE", "consumed marker bytes differ")


def _normalize_ip(value: str) -> str:
    try:
        return ipaddress.ip_address(value.split("%", 1)[0]).compressed
    except ValueError as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "PEER_ADDRESS") from exc


def _global_ip(value: str) -> bool:
    try:
        return ipaddress.ip_address(value.split("%", 1)[0]).is_global
    except ValueError:
        return False


def _header_rows(headers: Sequence[tuple[str, str]]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {}
    for name, value in headers:
        key = name.strip().casefold()
        if not key or any(character in "\r\n" for character in name + value):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "HEADER_SHAPE")
        values.setdefault(key, []).append(value.strip())
    if any(len(values.get(name, [])) > 1 for name in SINGLETON_RESPONSE_HEADERS):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DUPLICATE_SINGLETON_HEADER")
    return values


def _one_header(values: Mapping[str, Sequence[str]], name: str) -> str | None:
    rows = values.get(name, ())
    return rows[0] if rows else None


def _validate_cache_headers(values: Mapping[str, Sequence[str]], wall_now: float) -> None:
    age = _one_header(values, "age")
    if age is not None and age != "0":
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CACHE_AGE")
    date_value = _one_header(values, "date")
    if date_value is None:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "SERVER_DATE_ABSENT")
    try:
        parsed = parsedate_to_datetime(date_value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        skew = abs(parsed.timestamp() - wall_now)
    except (TypeError, ValueError, OverflowError) as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "SERVER_DATE_MALFORMED") from exc
    if skew > MAX_SERVER_DATE_SKEW_SECONDS:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "SERVER_DATE_STALE")


def _response_framing(values: Mapping[str, Sequence[str]]) -> tuple[str, int | None]:
    length_value = _one_header(values, "content-length")
    transfer_value = _one_header(values, "transfer-encoding")
    if length_value is not None and transfer_value is not None:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONFLICTING_RESPONSE_FRAMING")
    if transfer_value is not None:
        if transfer_value.casefold() != "chunked":
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "TRANSFER_ENCODING")
        return "chunked", None
    if length_value is None:
        return "connection_close", None
    if not length_value.isascii() or not length_value.isdecimal():
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_LENGTH")
    return "content_length", int(length_value)


def _read_response_body(
    response: http.client.HTTPResponse,
    maximum_bytes: int,
    declared_bytes: int | None,
) -> bytes:
    try:
        body = response.read(maximum_bytes + 1)
    except (OSError, http.client.HTTPException) as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "BODY_READ") from exc
    if not isinstance(body, bytes):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "BODY_TYPE")
    if len(body) > maximum_bytes:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "PAGE_BYTE_CAP")
    if declared_bytes is not None and declared_bytes != len(body):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_LENGTH_MISMATCH")
    return body


def _request_target(url: str) -> tuple[str, str]:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or not parsed.hostname.isascii()
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.port is not None
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REQUEST_URL")
    path = parsed.path or "/"
    target = path + (f"?{parsed.query}" if parsed.query else "")
    if not target.isascii() or any(character in "\r\n " for character in target):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REQUEST_TARGET")
    return parsed.hostname.lower(), target


def _remaining_timeout(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "RUNTIME_CAP")
    return remaining


class _DNSDeadlineExpired(Exception):
    pass


def _bounded_getaddrinfo(host: str, deadline: float) -> list[tuple[object, ...]]:
    remaining = _remaining_timeout(deadline)
    try:
        previous_delay, previous_interval = signal.getitimer(signal.ITIMER_REAL)
        previous_handler = signal.getsignal(signal.SIGALRM)
    except (AttributeError, OSError, ValueError) as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DNS_DEADLINE_UNAVAILABLE") from exc
    if previous_delay > 0 or previous_interval > 0:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DNS_ALARM_ALREADY_ACTIVE")

    def deadline_handler(_signum: int, _frame: object) -> None:
        raise _DNSDeadlineExpired

    handler_installed = False
    timer_armed = False
    try:
        signal.signal(signal.SIGALRM, deadline_handler)
        handler_installed = True
        signal.setitimer(signal.ITIMER_REAL, remaining)
        timer_armed = True
        return socket.getaddrinfo(
            host,
            443,
            family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
    except _DNSDeadlineExpired as exc:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "RUNTIME_CAP") from exc
    except OSError as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DNS") from exc
    except ValueError as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DNS_DEADLINE_UNAVAILABLE") from exc
    finally:
        if timer_armed:
            signal.setitimer(signal.ITIMER_REAL, 0)
        if handler_installed:
            signal.signal(signal.SIGALRM, previous_handler)


def direct_TLS_contact(
    request: PreparedRequest,
    _global_ordinal: int,
    deadline: float,
    invocation_started: float,
) -> ContactResult:
    request_started = time.monotonic()
    request_seconds = MAX_CI_REQUEST_SECONDS if request.kind == "CI" else MAX_REQUEST_SECONDS
    request_deadline = min(deadline, request_started + request_seconds)
    remaining = _remaining_timeout(request_deadline)
    host, target = _request_target(request.url)
    if request.method not in {"GET", "POST"}:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REQUEST_METHOD")
    if any(
        not name.isascii()
        or not value.isascii()
        or any(character in "\r\n" for character in name + value)
        for name, value in request.headers
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REQUEST_HEADER")
    default_maximum = MAX_CI_RESPONSE_BYTES if request.kind == "CI" else MAX_PAGE_BYTES
    default_wire_maximum = MAX_CI_RESPONSE_BYTES if request.kind == "CI" else MAX_SOURCE_WIRE_BYTES
    maximum = request.maximum_response_bytes
    maximum_wire = request.maximum_wire_response_bytes
    if (
        not isinstance(maximum, int)
        or isinstance(maximum, bool)
        or not 0 <= maximum <= default_maximum
        or not isinstance(maximum_wire, int)
        or isinstance(maximum_wire, bool)
        or not 0 <= maximum_wire <= default_wire_maximum
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "per-contact response cap differs")

    answers = _bounded_getaddrinfo(host, request_deadline)
    remaining = _remaining_timeout(request_deadline)
    unique: list[tuple[int, int, int, tuple[object, ...], str]] = []
    seen: set[tuple[int, str]] = set()
    for family, socktype, protocol, _canonname, sockaddr in answers:
        address = _normalize_ip(str(sockaddr[0]))
        key = (family, address)
        if key not in seen:
            seen.add(key)
            unique.append((family, socktype, protocol, sockaddr, address))
    if not unique or any(not _global_ip(row[4]) for row in unique):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "DNS_NON_GLOBAL")
    DNS_digest = _sha256(core.canonical_json_bytes(sorted(row[4] for row in unique), newline=True))
    family, socktype, protocol, sockaddr, selected_address = unique[0]
    raw_socket: socket.socket | None = None
    TLS_socket: ssl.SSLSocket | None = None
    response: http.client.HTTPResponse | None = None
    try:
        raw_socket = socket.socket(family, socktype, protocol)
        raw_socket.settimeout(remaining)
        raw_socket.connect(sockaddr)
        raw_socket.settimeout(_remaining_timeout(request_deadline))
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        TLS_socket = context.wrap_socket(raw_socket, server_hostname=host)
        raw_socket = None
        TLS_socket.settimeout(_remaining_timeout(request_deadline))
        post_address = _normalize_ip(str(TLS_socket.getpeername()[0]))
        if post_address != selected_address or not _global_ip(post_address):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "PEER_BINDING")
        request_head = (
            f"{request.method} {target} HTTP/1.1\r\n"
            + "".join(f"{name}: {value}\r\n" for name, value in request.headers)
            + "\r\n"
        ).encode("ascii")
        TLS_socket.sendall(request_head + request.body)
        TLS_socket.settimeout(_remaining_timeout(request_deadline))
        response = _NoInterimHTTPResponse(TLS_socket, method=request.method)
        counting_reader = _CountingReader(response.fp)
        response.fp = counting_reader  # type: ignore[assignment]
        response.begin()
        if response.version != 11 or response.status < 200:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "HTTP_VERSION_OR_INTERIM")
        headers = tuple((str(name), str(value)) for name, value in response.headers.raw_items())
        values = _header_rows(headers)
        _validate_cache_headers(values, time.time())
        encoding = (_one_header(values, "content-encoding") or "").casefold()
        if encoding not in {"", "identity"}:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_ENCODING")
        framing, declared_bytes = _response_framing(values)
        if request.kind == "CI" and response.status != 200:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_HTTP_STATUS")
        if declared_bytes is not None and declared_bytes > maximum:
            raise LiveWitnessPark("WITNESS_CAP_PARK", "PAGE_BYTE_CAP")
        counting_reader.begin_body(maximum_wire)
        TLS_socket.settimeout(_remaining_timeout(request_deadline))
        body = _read_response_body(response, maximum, declared_bytes)
        wire_body_bytes = counting_reader.body_bytes
        _remaining_timeout(request_deadline)
        TLS_version = TLS_socket.version() or ""
        if TLS_version not in {"TLSv1.2", "TLSv1.3"}:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "TLS_VERSION")
        elapsed = time.monotonic()
        return ContactResult(
            status=response.status,
            headers=headers,
            body=body,
            DNS_answer_set_sha256=DNS_digest,
            selected_peer_sha256=_sha256(selected_address.encode("ascii")),
            post_connect_peer_sha256=_sha256(post_address.encode("ascii")),
            selected_and_post_connect_peer_equal_and_global=True,
            TLS_version=TLS_version,
            response_headers_sha256=_sha256(
                core.canonical_json_bytes([list(row) for row in headers])
            ),
            content_encoding=encoding,
            transfer_framing=framing,
            wire_body_bytes=wire_body_bytes,
            request_elapsed_nanoseconds=int((elapsed - request_started) * 1_000_000_000),
            whole_invocation_elapsed_nanoseconds=int(
                (elapsed - invocation_started) * 1_000_000_000
            ),
        )
    except LiveWitnessPark:
        raise
    except (OSError, ssl.SSLError, http.client.HTTPException) as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "TLS_OR_HTTP") from exc
    finally:
        if response is not None:
            response.close()
        if TLS_socket is not None:
            TLS_socket.close()
        if raw_socket is not None:
            raw_socket.close()


def _CI_request(path: str) -> PreparedRequest:
    if not path.startswith("/") or not path.isascii():
        raise LiveWitnessRefusal("LIVE_CI_REFUSE", "CI request path differs")
    identity = _sha256(
        core.canonical_json_bytes(
            {
                "method": "GET",
                "url": f"https://{CI_HOST}{path}",
                "headers": [list(row) for row in CI_HEADERS],
                "body_bytes": 0,
            },
            newline=True,
        )
    )
    return PreparedRequest(
        method="GET",
        url=f"https://{CI_HOST}{path}",
        headers=CI_HEADERS,
        body=b"",
        request_identity_sha256=identity,
        kind="CI",
    )


def _contact_once(
    request: PreparedRequest,
    *,
    budget: RequestBudget,
    contact: ContactCallable,
    deadline: float,
) -> tuple[int, ContactResult]:
    ordinal = budget.claim(request.kind)
    if (
        request.maximum_response_bytes is not None
        or request.maximum_wire_response_bytes is not None
    ):
        raise LiveWitnessRefusal("LIVE_AUTHORITY_REFUSE", "response cap was prepopulated")
    if request.kind == "CI":
        remaining_bytes = MAX_CI_BYTES - budget.CI_bytes
        maximum_response_bytes = min(MAX_CI_RESPONSE_BYTES, remaining_bytes)
        maximum_wire_response_bytes = maximum_response_bytes
    else:
        remaining_bytes = MAX_SOURCE_ENTITY_BYTES - budget.source_entity_bytes
        maximum_response_bytes = min(MAX_PAGE_BYTES, remaining_bytes)
        maximum_wire_response_bytes = MAX_SOURCE_WIRE_BYTES - budget.source_wire_bytes
    if maximum_response_bytes < 0 or maximum_wire_response_bytes < 0:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "BYTE_CAP")
    bounded_request = replace(
        request,
        maximum_response_bytes=maximum_response_bytes,
        maximum_wire_response_bytes=maximum_wire_response_bytes,
    )
    if time.monotonic() > deadline:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "RUNTIME_CAP")
    if _peak_rss_bytes() > MAX_PEAK_RSS_BYTES:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "PEAK_RSS_CAP")
    result = contact(bounded_request, ordinal, deadline, budget.started)
    if time.monotonic() > deadline:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "RUNTIME_CAP")
    if _peak_rss_bytes() > MAX_PEAK_RSS_BYTES:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "PEAK_RSS_CAP")
    if not isinstance(result, ContactResult):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTACT_RESULT")
    if len(result.body) > maximum_response_bytes:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "PAGE_BYTE_CAP")
    if result.wire_body_bytes > maximum_wire_response_bytes:
        raise LiveWitnessPark("WITNESS_CAP_PARK", "WIRE_BYTE_CAP")
    budget.add_body(request.kind, result.wire_body_bytes, len(result.body))
    if (
        result.selected_and_post_connect_peer_equal_and_global is not True
        or result.TLS_version not in {"TLSv1.2", "TLSv1.3"}
        or result.content_encoding not in {"", "identity"}
        or result.request_elapsed_nanoseconds < 0
        or result.whole_invocation_elapsed_nanoseconds < 0
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTACT_EVIDENCE")
    return ordinal, result


def _strict_CI_JSON(result: ContactResult) -> Mapping[str, object]:
    if result.status != 200:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_HTTP_STATUS")
    headers = _header_rows(result.headers)
    content_type = _one_header(headers, "content-type") or ""
    media_type = content_type.split(";", 1)[0].strip().casefold()
    if media_type not in {"application/json", "application/vnd.github+json"}:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_MEDIA_TYPE")
    try:
        value = core.strict_json_loads(result.body)
    except core.WitnessRefusal as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_JSON") from exc
    if not isinstance(value, Mapping):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_JSON_ROOT")
    return value


def run_CI_W0(
    authority: ExecutionAuthority,
    *,
    budget: RequestBudget,
    contact: ContactCallable,
    deadline: float,
) -> dict[str, object]:
    CI_deadline = min(deadline, time.monotonic() + MAX_CI_SECONDS)
    paths = (
        CI_MAIN_PATH,
        CI_CHECKS_TEMPLATE.format(head=authority.local_HEAD),
        CI_WORKFLOW_PATH,
    )
    responses: list[ContactResult] = []
    request_identities: list[str] = []
    for path in paths:
        request = _CI_request(path)
        _ordinal, response = _contact_once(
            request,
            budget=budget,
            contact=contact,
            deadline=CI_deadline,
        )
        request_identities.append(request.request_identity_sha256)
        responses.append(response)
    if budget.CI_requests != MAX_CI_REQUESTS:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_REQUEST_CARDINALITY")

    main = _strict_CI_JSON(responses[0])
    main_object = main.get("object")
    if (
        main.get("ref") != "refs/heads/main"
        or not isinstance(main_object, Mapping)
        or main_object.get("sha") != authority.local_HEAD
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_MAIN_IDENTITY")

    checks = _strict_CI_JSON(responses[1])
    rows = checks.get("check_runs")
    if checks.get("total_count") != 2 or not isinstance(rows, list) or len(rows) != 2:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_CHECK_CARDINALITY")
    expected_names = {"Base Python", "Optional Neuro Readers"}
    observed_names: set[str] = set()
    check_ids: dict[str, int] = {}
    for raw in rows:
        if not isinstance(raw, Mapping):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_CHECK_ROW")
        app = raw.get("app")
        name = raw.get("name")
        check_id = raw.get("id")
        if (
            not isinstance(app, Mapping)
            or app.get("slug") != "github-actions"
            or name not in expected_names
            or name in observed_names
            or not isinstance(check_id, int)
            or check_id <= 0
            or raw.get("head_sha") != authority.local_HEAD
            or raw.get("status") != "completed"
            or raw.get("conclusion") != "success"
        ):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_CHECK_IDENTITY")
        repository = raw.get("repository")
        head_repository = raw.get("head_repository")
        if not isinstance(repository, Mapping) or not isinstance(head_repository, Mapping):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_REPOSITORY_IDENTITY")
        owner = repository.get("owner")
        head_owner = head_repository.get("owner")
        if (
            repository.get("id") != REPOSITORY_ID
            or not isinstance(owner, Mapping)
            or owner.get("id") != OWNER_ID
            or head_repository.get("id") != REPOSITORY_ID
            or not isinstance(head_owner, Mapping)
            or head_owner.get("id") != OWNER_ID
        ):
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_REPOSITORY_IDENTITY")
        observed_names.add(str(name))
        check_ids[str(name)] = check_id
    if observed_names != expected_names:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_CHECK_NAMES")

    blob = _strict_CI_JSON(responses[2])
    if (
        blob.get("sha") != WORKFLOW_BLOB_SHA1
        or blob.get("encoding") != "base64"
        or blob.get("size") != WORKFLOW_BYTES
        or not isinstance(blob.get("content"), str)
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_WORKFLOW_ENVELOPE")
    content = blob["content"]
    if any(
        character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\r\n"
        for character in content
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_WORKFLOW_BASE64")
    compact_content = content.replace("\r", "").replace("\n", "")
    try:
        decoded = base64.b64decode(compact_content, validate=True)
    except (ValueError, TypeError) as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_WORKFLOW_BASE64") from exc
    if len(decoded) != WORKFLOW_BYTES or _sha256(decoded) != WORKFLOW_SHA256:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CI_WORKFLOW_IDENTITY")
    return {
        "local_HEAD_authority_commit": authority.local_HEAD,
        "authority_decision_blob_sha256": authority.decision_sha256,
        "current_main_ref_request_identity_sha256": request_identities[0],
        "current_main_ref_response_sha256": _sha256(responses[0].body),
        "exact_check_runs_request_identity_sha256": request_identities[1],
        "Base_Python_check_run_id": check_ids["Base Python"],
        "Optional_Neuro_Readers_check_run_id": check_ids["Optional Neuro Readers"],
        "check_runs_response_sha256": _sha256(responses[1].body),
        "workflow_blob_request_identity_sha256": request_identities[2],
        "workflow_blob_response_sha256": _sha256(responses[2].body),
    }


def _parse_content_type(headers: Sequence[tuple[str, str]]) -> tuple[str, str]:
    values = _header_rows(headers)
    raw = _one_header(values, "content-type")
    if raw is None:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_TYPE_ABSENT")
    pieces = [piece.strip() for piece in raw.split(";")]
    media_type = pieces[0].casefold()
    if media_type not in {"application/json", "text/html", "application/xhtml+xml"}:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_TYPE")
    charset = ""
    for piece in pieces[1:]:
        if not piece:
            continue
        if "=" not in piece:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_TYPE_PARAMETER")
        key, value = (part.strip() for part in piece.split("=", 1))
        if key.casefold() != "charset" or charset:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CONTENT_TYPE_PARAMETER")
        charset = value.strip('"').casefold()
    if charset not in {"", "utf-8", "utf8"}:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "CHARSET")
    return media_type, "utf-8" if charset else ""


def _source_request(
    packet: Mapping[str, object],
    root: core.RootRequest,
    url: str,
    body: bytes,
) -> PreparedRequest:
    identity, headers = core.request_identity(packet, root, url=url, body=body)
    return PreparedRequest(
        method=root.method,
        url=url,
        headers=headers,
        body=body,
        request_identity_sha256=identity,
        kind="SOURCE",
    )


def _canonical_redirect_url(
    packet: Mapping[str, object],
    root: core.RootRequest,
    current_url: str,
    location: str,
) -> str:
    if not location or len(location.encode("utf-8")) > MAX_CONTROL_BYTES:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_LOCATION")
    resolved = urljoin(current_url, location)
    try:
        parsed = urlsplit(resolved)
        port = parsed.port
        current = urlsplit(current_url)
    except ValueError as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_URL") from exc
    profile = core._profile(packet, core._profile_id(root.index_id))
    host = parsed.hostname
    if (
        parsed.scheme != "https"
        or host is None
        or not host.isascii()
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or port is not None
        or host.lower() not in profile["allowed_hosts"]
        or (parsed.path or "/") != profile["allowed_path"]
        or parsed.query != current.query
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_ALLOWLIST")
    canonical = urlunsplit(("https", host.lower(), parsed.path or "/", parsed.query, ""))
    if resolved != canonical:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_NONCANONICAL")
    return canonical


def _redirect_record(
    request: PreparedRequest,
    result: ContactResult,
    *,
    hop_ordinal: int,
    global_ordinal: int,
    location_bytes: bytes,
    next_request: PreparedRequest,
) -> dict[str, object]:
    current_host, current_target = _request_target(request.url)
    next_host, next_target = _request_target(next_request.url)
    return {
        "hop_ordinal": hop_ordinal,
        "global_request_ordinal": global_ordinal,
        "request_identity_sha256": request.request_identity_sha256,
        "method": request.method,
        "canonical_request_target_sha256": _sha256(current_target.encode("ascii")),
        "request_headers_sha256": _sha256(
            core.canonical_json_bytes([list(row) for row in request.headers])
        ),
        "request_body_bytes": len(request.body),
        "request_body_sha256": _sha256(request.body),
        "DNS_answer_set_sha256": result.DNS_answer_set_sha256,
        "selected_peer_sha256": result.selected_peer_sha256,
        "post_connect_peer_sha256": result.post_connect_peer_sha256,
        "selected_and_post_connect_peer_equal_and_global": result.selected_and_post_connect_peer_equal_and_global,
        "TLS_hostname": current_host,
        "TLS_SNI": current_host,
        "TLS_version": result.TLS_version,
        "system_CA_verification_succeeded": True,
        "HTTP_status": result.status,
        "response_headers_sha256": result.response_headers_sha256,
        "Location_raw_UTF_8_bytes": len(location_bytes),
        "Location_raw_sha256": _sha256(location_bytes),
        "normalized_next_request_identity_sha256": next_request.request_identity_sha256,
        "normalized_next_scheme": "https",
        "normalized_next_host_ascii": next_host,
        "normalized_next_port": 443,
        "normalized_next_path_and_query_sha256": _sha256(next_target.encode("ascii")),
        "content_encoding": result.content_encoding,
        "transfer_framing": result.transfer_framing,
        "wire_bytes": result.wire_body_bytes,
        "entity_body_bytes": len(result.body),
        "entity_body_sha256": _sha256(result.body),
        "request_elapsed_nanoseconds": result.request_elapsed_nanoseconds,
        "whole_invocation_elapsed_nanoseconds": result.whole_invocation_elapsed_nanoseconds,
    }


def fetch_source_page(
    packet: Mapping[str, object],
    root: core.RootRequest,
    url: str,
    body: bytes,
    *,
    budget: RequestBudget,
    contact: ContactCallable,
    deadline: float,
) -> TerminalExchange:
    active_url = url
    redirects: list[Mapping[str, object]] = []
    for hop_ordinal in range(MAX_REDIRECTS + 1):
        request = _source_request(packet, root, active_url, body)
        global_ordinal, result = _contact_once(
            request,
            budget=budget,
            contact=contact,
            deadline=deadline,
        )
        if result.status == 200:
            media_type, charset = _parse_content_type(result.headers)
            host, target = _request_target(active_url)
            transport = {
                "global_request_ordinal": global_ordinal,
                "method": root.method,
                "scheme": "https",
                "host_ascii": host,
                "port": 443,
                "path_and_query_sha256": _sha256(target.encode("ascii")),
                "request_headers_sha256": _sha256(
                    core.canonical_json_bytes([list(row) for row in request.headers])
                ),
                "request_body_bytes": len(body),
                "request_body_sha256": _sha256(body),
                "DNS_answer_set_sha256": result.DNS_answer_set_sha256,
                "selected_peer_sha256": result.selected_peer_sha256,
                "post_connect_peer_sha256": result.post_connect_peer_sha256,
                "selected_and_post_connect_peer_equal_and_global": result.selected_and_post_connect_peer_equal_and_global,
                "TLS_hostname": host,
                "TLS_SNI": host,
                "TLS_version": result.TLS_version,
                "system_CA_verification_succeeded": True,
                "HTTP_status": result.status,
                "response_headers_sha256": result.response_headers_sha256,
                "normalized_media_type": media_type,
                "charset": charset,
                "content_encoding": result.content_encoding,
                "transfer_framing": result.transfer_framing,
                "wire_bytes": result.wire_body_bytes,
                "entity_body_bytes": len(result.body),
                "request_elapsed_nanoseconds": result.request_elapsed_nanoseconds,
                "whole_invocation_elapsed_nanoseconds": result.whole_invocation_elapsed_nanoseconds,
            }
            core.validate_redirect_transcript(packet, redirects)
            core.validate_transport_evidence(packet, transport)
            return TerminalExchange(
                request_identity_sha256=request.request_identity_sha256,
                terminal_url=active_url,
                terminal_body=body,
                media_type=media_type,
                charset=charset,
                response_body=result.body,
                response_headers=result.headers,
                redirect_transcript=tuple(redirects),
                transport_evidence=transport,
            )
        allowed = {307, 308} if root.method == "POST" else {301, 302, 303, 307, 308}
        if result.status not in allowed or hop_ordinal >= MAX_REDIRECTS:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "HTTP_STATUS_OR_REDIRECT_CAP")
        values = _header_rows(result.headers)
        raw_location = _one_header(values, "location")
        if raw_location is None:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_LOCATION_ABSENT")
        try:
            location_bytes = raw_location.encode("latin-1")
            location = location_bytes.decode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_LOCATION_ENCODING") from exc
        next_url = _canonical_redirect_url(packet, root, active_url, location)
        next_request = _source_request(packet, root, next_url, body)
        redirects.append(
            _redirect_record(
                request,
                result,
                hop_ordinal=hop_ordinal,
                global_ordinal=global_ordinal,
                location_bytes=location_bytes,
                next_request=next_request,
            )
        )
        active_url = next_url
    raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REDIRECT_CAP")


def _selective_object_members(
    raw: str,
    audit: SemanticAccessAudit,
) -> list[tuple[str, str]]:
    offset = core._skip_ws(raw, 0)
    if offset >= len(raw) or raw[offset] != "{":
        raise core.WitnessRefusal("PAGINATION_REFUSE", "JSON control parent is not an object")
    offset += 1
    members: list[tuple[str, str]] = []
    while True:
        offset = core._skip_ws(raw, offset)
        if offset < len(raw) and raw[offset] == "}":
            offset = core._skip_ws(raw, offset + 1)
            if offset != len(raw):
                raise core.WitnessRefusal("PAGINATION_REFUSE", "trailing JSON control bytes")
            return members
        key_end = core._scan_string_end(raw, offset)
        raw_key = raw[offset:key_end]
        offset = core._skip_ws(raw, key_end)
        if offset >= len(raw) or raw[offset] != ":":
            raise core.WitnessRefusal("PAGINATION_REFUSE", "JSON member colon is absent")
        value_start = core._skip_ws(raw, offset + 1)
        value_end = core._raw_value_end(raw, value_start)
        members.append((raw_key, raw[value_start:value_end]))
        offset = core._skip_ws(raw, value_end)
        if offset < len(raw) and raw[offset] == ",":
            offset += 1
            continue
        if offset < len(raw) and raw[offset] == "}":
            continue
        raise core.WitnessRefusal("PAGINATION_REFUSE", "JSON object separator differs")


def _select_control_members(
    raw: str,
    names: Sequence[str],
    audit: SemanticAccessAudit,
    *,
    allow_opaque: bool,
) -> dict[str, str]:
    tokens = {f'"{name}"': name for name in names}
    selected: dict[str, str] = {}
    for raw_key, raw_value in _selective_object_members(raw, audit):
        name = tokens.get(raw_key)
        if name is None:
            audit.opaque_members_skipped += 1
            if not allow_opaque:
                raise core.WitnessRefusal("PAGINATION_REFUSE", "unknown control member is present")
            continue
        if name in selected:
            raise core.WitnessRefusal("PAGINATION_REFUSE", "duplicate control member is present")
        audit.control_fields_accessed += 1
        selected[name] = raw_value
    return selected


def _select_control_object(
    raw: str,
    name: str,
    audit: SemanticAccessAudit,
) -> str:
    selected = _select_control_members(raw, (name,), audit, allow_opaque=True)
    value = selected.get(name)
    if value is None or not value.lstrip().startswith("{"):
        raise core.WitnessRefusal("PAGINATION_REFUSE", f"required control object differs: {name}")
    return value


def _decode_control_scalar(raw: str, audit: SemanticAccessAudit) -> object:
    if "REFERENCE_TARGET_DO_NOT_RETAIN" in raw:
        audit.candidate_semantic_accesses += 1
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "candidate value reached control decoder")
    audit.control_fields_accessed += 1
    return core._parse_scalar(raw)


def _extract_selective_openneuro_control(
    payload: bytes,
    audit: SemanticAccessAudit,
) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise core.WitnessRefusal("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise core.WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    page_info = _select_control_object(
        _select_control_object(_select_control_object(text, "data", audit), "datasets", audit),
        "pageInfo",
        audit,
    )
    members = _select_control_members(
        page_info,
        ("hasNextPage", "endCursor"),
        audit,
        allow_opaque=False,
    )
    if set(members) != {"hasNextPage", "endCursor"}:
        raise core.WitnessRefusal("PAGINATION_REFUSE", "OpenNeuro pageInfo controls differ")
    has_next = _decode_control_scalar(members["hasNextPage"], audit)
    cursor = _decode_control_scalar(members["endCursor"], audit)
    if has_next is True and isinstance(cursor, str):
        return cursor, {
            "variant": "OPENNEURO_CONTINUE",
            "cursor_sha256": _sha256(cursor.encode()),
        }
    if has_next is False and cursor is None:
        return None, {"variant": "OPENNEURO_TERMINAL"}
    raise core.WitnessRefusal("PAGINATION_REFUSE", "OpenNeuro control values differ")


def _extract_selective_generic_JSON_control(
    payload: bytes,
    audit: SemanticAccessAudit,
) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise core.WitnessRefusal("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise core.WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    members = _select_control_members(text, ("next", "pagination"), audit, allow_opaque=True)
    top_present = "next" in members
    pagination_present = "pagination" in members
    if top_present == pagination_present:
        raise core.WitnessRefusal(
            "PAGINATION_REFUSE", "exactly one JSON control variant is required"
        )
    if top_present:
        value = _decode_control_scalar(members["next"], audit)
        if value is None:
            return None, {"variant": "TOP_LEVEL_NEXT", "terminal": True}
        if isinstance(value, str):
            return value, {"variant": "TOP_LEVEL_NEXT", "terminal": False}
        raise core.WitnessRefusal("PAGINATION_REFUSE", "top-level next type differs")
    pagination = _select_control_members(
        members["pagination"],
        ("next", "has_next"),
        audit,
        allow_opaque=False,
    )
    if "next" in pagination and "has_next" not in pagination:
        value = _decode_control_scalar(pagination["next"], audit)
        if value is None:
            return None, {"variant": "PAGINATION_NEXT", "terminal": True}
        if isinstance(value, str):
            return value, {"variant": "PAGINATION_NEXT", "terminal": False}
    if (
        set(pagination) == {"has_next"}
        and _decode_control_scalar(pagination["has_next"], audit) is False
    ):
        return None, {"variant": "PAGINATION_HAS_NEXT_FALSE", "terminal": True}
    raise core.WitnessRefusal("PAGINATION_REFUSE", "pagination control differs")


class _SelectivePaginationHTMLParser(HTMLParser):
    _CONTAINER_ATTRIBUTES = {"aria-label", "class", "id", "role"}
    _NEXT_SELECTOR_ATTRIBUTES = {"class", "rel"}
    _NEXT_VALUE_ATTRIBUTES = {"aria-disabled", "href"}
    _IGNORED_CONTENT_TAGS = {"script", "style", "template"}

    def __init__(self, audit: SemanticAccessAudit) -> None:
        super().__init__(convert_charrefs=True)
        self.audit = audit
        self.depth = 0
        self.container_depth: int | None = None
        self.container_count = 0
        self.next_values: list[str] = []
        self.terminal_count = 0
        self.ignored_depth: int | None = None

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {token.casefold() for token in value.split() if token}

    def _selected_attributes(
        self,
        attrs: Sequence[tuple[str, str | None]],
        names: set[str],
    ) -> dict[str, str]:
        values: dict[str, str] = {}
        for raw_key, raw_value in attrs:
            key = raw_key.casefold()
            if key not in names:
                self.audit.opaque_members_skipped += 1
                continue
            if key in values:
                raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "duplicate HTML control attribute")
            value = raw_value or ""
            if "REFERENCE_TARGET_DO_NOT_RETAIN" in value:
                self.audit.candidate_semantic_accesses += 1
                raise LiveWitnessRefusal(
                    "LIVE_OUTPUT_REFUSE", "candidate attribute reached control decoder"
                )
            self.audit.control_fields_accessed += 1
            values[key] = value
        return values

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.depth += 1
        folded_tag = tag.casefold()
        if self.ignored_depth is not None:
            return
        if folded_tag in self._IGNORED_CONTENT_TAGS:
            self.ignored_depth = self.depth
            return
        values = self._selected_attributes(attrs, self._CONTAINER_ATTRIBUTES)
        classes = self._tokens(values.get("class", ""))
        matches = (
            (
                folded_tag == "nav"
                and values.get("aria-label", "").strip().casefold() == "pagination"
            )
            or (
                values.get("role", "").strip().casefold() == "navigation"
                and values.get("aria-label", "").strip().casefold() == "pagination"
            )
            or bool(classes & {"pagination", "pager"})
            or values.get("id", "").strip().casefold() in {"pagination", "pager"}
        )
        if matches:
            self.container_count += 1
            if self.container_depth is None:
                self.container_depth = self.depth
        if self.container_depth is None or self.depth <= self.container_depth or folded_tag != "a":
            return
        selectors = self._selected_attributes(attrs, self._NEXT_SELECTOR_ATTRIBUTES)
        rel = self._tokens(selectors.get("rel", ""))
        control_classes = self._tokens(selectors.get("class", ""))
        if "next" in rel:
            values = self._selected_attributes(attrs, self._NEXT_VALUE_ATTRIBUTES)
            href = values.get("href", "")
            if href:
                self.next_values.append(href)
            elif values.get("aria-disabled", "").strip().casefold() == "true":
                self.terminal_count += 1
        elif {"next", "disabled"}.issubset(control_classes):
            values = self._selected_attributes(attrs, {"href"})
            if not values.get("href"):
                self.terminal_count += 1

    def handle_endtag(self, _tag: str) -> None:
        if self.ignored_depth == self.depth:
            self.ignored_depth = None
        if self.container_depth == self.depth:
            self.container_depth = None
        self.depth = max(0, self.depth - 1)


def _extract_selective_generic_HTML_control(
    payload: bytes,
    audit: SemanticAccessAudit,
) -> tuple[str | None, Mapping[str, object]]:
    if payload.startswith(b"\xef\xbb\xbf"):
        raise core.WitnessRefusal("PAGINATION_REFUSE", "UTF-8 BOM is forbidden")
    try:
        text = payload.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise core.WitnessRefusal("PAGINATION_REFUSE", "response is not strict UTF-8") from exc
    parser = _SelectivePaginationHTMLParser(audit)
    parser.feed(text)
    parser.close()
    if parser.container_count != 1:
        raise core.WitnessRefusal("PAGINATION_REFUSE", "HTML pagination container count differs")
    if len(parser.next_values) == 1 and parser.terminal_count == 0:
        value = parser.next_values[0]
        if len(value.encode("utf-8")) > MAX_CONTROL_BYTES:
            raise core.WitnessRefusal("PAGINATION_REFUSE", "HTML next href cap exceeded")
        return value, {"variant": "HTML_NEXT", "terminal": False}
    if not parser.next_values and parser.terminal_count == 1:
        return None, {"variant": "HTML_TERMINAL", "terminal": True}
    raise core.WitnessRefusal("PAGINATION_REFUSE", "HTML next or terminal control differs")


def _parse_selective_control(
    packet: Mapping[str, object],
    root: core.RootRequest,
    current_url: str,
    current_body: bytes,
    media_type: str,
    payload: bytes,
    audit: SemanticAccessAudit,
) -> tuple[str | None, bytes | None, Mapping[str, object]]:
    if len(payload) > MAX_PAGE_BYTES:
        raise core.WitnessRefusal("RESOURCE_REFUSE", "page byte cap exceeded")
    profile_id = core._profile_id(root.index_id)
    if profile_id == "OPENNEURO_CRN":
        if media_type != "application/json":
            raise core.WitnessRefusal("PAGINATION_REFUSE", "OpenNeuro media type differs")
        cursor, control = _extract_selective_openneuro_control(payload, audit)
        if cursor is None:
            return None, None, control
        query_index = int(root.query_or_category_id.removeprefix("query_")) - 1
        next_body = core._openneuro_body(core.EXACT_QUERIES[query_index], cursor)
        if next_body == current_body:
            raise core.WitnessRefusal("PAGINATION_REFUSE", "OpenNeuro cursor did not advance")
        return root.url, next_body, control
    if media_type == "application/json":
        reference, control = _extract_selective_generic_JSON_control(payload, audit)
    elif media_type in {"text/html", "application/xhtml+xml"}:
        reference, control = _extract_selective_generic_HTML_control(payload, audit)
    else:
        raise core.WitnessRefusal("TRANSPORT_REFUSE", "normalized media type differs")
    if reference is None:
        return None, None, control
    return (
        core.canonicalize_continuation_url(packet, root, current_url, reference),
        b"",
        control,
    )


def _live_page(
    packet: Mapping[str, object],
    root: core.RootRequest,
    current_url: str,
    current_body: bytes,
    exchange: TerminalExchange,
    page_ordinal: int,
    audit: SemanticAccessAudit,
) -> tuple[dict[str, object], str | None, bytes | None]:
    if exchange.terminal_body != current_body or (
        exchange.request_identity_sha256
        != core.request_identity(
            packet,
            root,
            url=exchange.terminal_url,
            body=exchange.terminal_body,
        )[0]
    ):
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "REQUEST_IDENTITY_DRIFT")
    try:
        next_url, next_body, control = _parse_selective_control(
            packet,
            root,
            exchange.terminal_url,
            exchange.terminal_body,
            exchange.media_type,
            exchange.response_body,
            audit,
        )
    except core.WitnessRefusal as exc:
        route = "WITNESS_CAP_PARK" if exc.route == "RESOURCE_REFUSE" else "WITNESS_TRANSPORT_PARK"
        raise LiveWitnessPark(route, exc.route) from exc
    next_identity = None
    if next_url is not None and next_body is not None:
        next_identity = core.request_identity(packet, root, url=next_url, body=next_body)[0]
    page = {
        "page_ordinal": page_ordinal,
        "request_identity_sha256": exchange.request_identity_sha256,
        "request_body_sha256": _sha256(exchange.terminal_body),
        "redirect_transcript": [dict(row) for row in exchange.redirect_transcript],
        "pagination_identity_sha256": _sha256(core.canonical_json_bytes(control, newline=True)),
        "response_body_bytes": len(exchange.response_body),
        "response_body_sha256": _sha256(exchange.response_body),
        "next_request_identity_sha256": next_identity,
        "terminal_state": "TERMINAL" if next_identity is None else "CONTINUE",
        "transport_evidence": dict(exchange.transport_evidence),
    }
    hash_contract = core._mapping(
        core._mapping(packet["opaque_snapshot_ledger_contract"], "CONTRACT_REFUSE")[
            "canonical_hash_contract"
        ],
        "CONTRACT_REFUSE",
    )
    page["canonical_page_ledger_sha256"] = core._hash_fields(
        page, hash_contract["page_preimage_fields"]
    )
    return page, next_url, next_body


def build_live_ledger(
    repo_root: str | Path,
    *,
    budget: RequestBudget,
    contact: ContactCallable,
    deadline: float,
    audit: SemanticAccessAudit | None = None,
) -> dict[str, object]:
    active_audit = SemanticAccessAudit() if audit is None else audit
    packet = core.load_packet(repo_root)
    roots = core.build_root_plan(repo_root)
    contract = core._mapping(packet["opaque_snapshot_ledger_contract"], "CONTRACT_REFUSE")
    hash_contract = core._mapping(contract["canonical_hash_contract"], "CONTRACT_REFUSE")
    roots_by_profile: dict[str, list[dict[str, object]]] = {name: [] for name in core.PROFILE_ORDER}

    for root in roots:
        current_url = root.url
        current_body = root.body
        initial_identity = core.request_identity(packet, root)[0]
        seen: set[str] = set()
        pages: list[dict[str, object]] = []
        while True:
            if time.monotonic() > deadline:
                raise LiveWitnessPark("WITNESS_CAP_PARK", "RUNTIME_CAP")
            identity = core.request_identity(packet, root, url=current_url, body=current_body)[0]
            if identity in seen:
                raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "PAGINATION_CYCLE")
            seen.add(identity)
            exchange = fetch_source_page(
                packet,
                root,
                current_url,
                current_body,
                budget=budget,
                contact=contact,
                deadline=deadline,
            )
            if exchange.request_identity_sha256 != identity:
                if exchange.request_identity_sha256 in seen:
                    raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", "PAGINATION_CYCLE")
                seen.add(exchange.request_identity_sha256)
            page, next_url, next_body = _live_page(
                packet,
                root,
                current_url,
                current_body,
                exchange,
                len(pages),
                active_audit,
            )
            pages.append(page)
            del exchange
            if next_url is None or next_body is None:
                break
            current_url, current_body = next_url, next_body

        page_hashes = [str(page["canonical_page_ledger_sha256"]) for page in pages]
        root_row = {
            "root_ordinal": root.root_ordinal,
            "index_id": core._profile_id(root.index_id),
            "query_or_category_id": root.query_or_category_id,
            "initial_request_identity_sha256": initial_identity,
            "complete": True,
            "page_count": len(pages),
            "terminal_page_count": 1,
            "pages": pages,
            "page_sha256_values": page_hashes,
        }
        root_row["canonical_root_ledger_sha256"] = core._hash_fields(
            root_row, hash_contract["root_preimage_fields"]
        )
        roots_by_profile[core._profile_id(root.index_id)].append(root_row)

    profiles: list[dict[str, object]] = []
    for profile_ordinal, index_id in enumerate(core.PROFILE_ORDER):
        profile_roots = roots_by_profile[index_id]
        root_hashes = [str(row["canonical_root_ledger_sha256"]) for row in profile_roots]
        profile_row = {
            "profile_ordinal": profile_ordinal,
            "index_id": index_id,
            "mode": "OPAQUE_COMPLETE_SNAPSHOT_REPLAY",
            "root_ordinals": [int(row["root_ordinal"]) for row in profile_roots],
            "roots": profile_roots,
            "root_sha256_values": root_hashes,
            "complete": True,
            "page_count": sum(int(row["page_count"]) for row in profile_roots),
            "terminal_root_count": len(profile_roots),
            "wire_bytes": sum(
                int(page["transport_evidence"]["wire_bytes"])
                for row in profile_roots
                for page in row["pages"]
            ),
            "entity_body_bytes": sum(
                int(page["transport_evidence"]["entity_body_bytes"])
                for row in profile_roots
                for page in row["pages"]
            ),
            "warnings": list(LIVE_WARNINGS),
            "unavailable_fields": list(LIVE_UNAVAILABLE_FIELDS),
        }
        profile_row["canonical_profile_ledger_sha256"] = core._hash_fields(
            profile_row, hash_contract["profile_preimage_fields"]
        )
        profiles.append(profile_row)
    ledger = {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_ledger",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "profiles": profiles,
        "profile_sha256_values": [
            str(profile["canonical_profile_ledger_sha256"]) for profile in profiles
        ],
        "global_root_sha256_values": [
            str(root["canonical_root_ledger_sha256"])
            for profile in profiles
            for root in profile["roots"]
        ],
        "total_root_count": 17,
        "total_page_count": sum(int(profile["page_count"]) for profile in profiles),
        "total_wire_bytes": sum(int(profile["wire_bytes"]) for profile in profiles),
        "total_entity_body_bytes": sum(int(profile["entity_body_bytes"]) for profile in profiles),
    }
    ledger["canonical_global_ledger_sha256"] = core._hash_fields(
        ledger, hash_contract["global_preimage_fields"]
    )
    try:
        core.validate_ledger(packet, ledger)
    except core.WitnessRefusal as exc:
        raise LiveWitnessPark("WITNESS_TRANSPORT_PARK", exc.route) from exc
    return ledger


def _run_contact_sequence(
    repo_root: Path,
    authority: ExecutionAuthority,
    reservation: AttemptReservation,
    *,
    budget: RequestBudget,
    audit: SemanticAccessAudit,
    states: list[str],
    contact: ContactCallable,
    deadline: float,
) -> tuple[dict[str, object], dict[str, object]]:
    def guarded_contact(
        request: PreparedRequest,
        ordinal: int,
        active_deadline: float,
        invocation_started: float,
    ) -> ContactResult:
        verify_consumed_marker(reservation)
        return contact(request, ordinal, active_deadline, invocation_started)

    states.append("CI_W0")
    CI_receipt = run_CI_W0(
        authority,
        budget=budget,
        contact=guarded_contact,
        deadline=deadline,
    )
    states.append("SEVENTEEN_ROOT_WITNESS")
    ledger = build_live_ledger(
        repo_root,
        budget=budget,
        contact=guarded_contact,
        deadline=deadline,
        audit=audit,
    )
    return CI_receipt, ledger


def _operation_counters(
    budget: RequestBudget,
    audit: SemanticAccessAudit | None = None,
) -> dict[str, object]:
    active_audit = SemanticAccessAudit() if audit is None else audit
    return {
        "network_requests": budget.total_requests,
        "network_input_bytes": budget.CI_bytes + budget.source_entity_bytes,
        "CI_requests": budget.CI_requests,
        "CI_decoded_bytes": budget.CI_bytes,
        "official_index_requests": budget.source_requests,
        "official_index_wire_bytes": budget.source_wire_bytes,
        "official_index_decoded_bytes": budget.source_entity_bytes,
        "candidate_semantic_operations": active_audit.candidate_semantic_accesses,
        "pagination_control_fields_accessed": active_audit.control_fields_accessed,
        "opaque_members_skipped": active_audit.opaque_members_skipped,
        "source_selections": 0,
        "payload_or_neural_reads": 0,
        "target_or_label_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "scoring_events": 0,
        "scientific_claim_upgrades": 0,
    }


def _base_result(
    authority: ExecutionAuthority,
    budget: RequestBudget,
    *,
    route: str,
    started: float,
    state_transcript: Sequence[str],
    audit: SemanticAccessAudit | None = None,
) -> dict[str, object]:
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_live_result",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "implementation_id": LIVE_IMPLEMENTATION_ID,
        "implementation_commit": authority.implementation_commit,
        "implementation_artifact_set_sha256": authority.implementation_artifact_set_sha256,
        "packet_sha256": core.PACKET_SHA256,
        "execution_decision_id": EXECUTION_DECISION_ID,
        "execution_decision_commit": authority.local_HEAD,
        "execution_decision_sha256": authority.decision_sha256,
        "CI_W0_profile_sha256": authority.CI_W0_profile_sha256,
        "route": route,
        "state_transcript": list(state_transcript),
        "runtime_seconds": time.monotonic() - started,
        "runtime_measurement_endpoint": "immediately_before_result_serialization",
        "peak_RSS_bytes": _peak_rss_bytes(),
        "peak_RSS_measurement_endpoint": "immediately_before_result_serialization",
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "producer_is_causal": "not_applicable_source_identity_only",
        "end_to_end_latency_measured": False,
        "operation_counters": _operation_counters(budget, audit),
        "warnings": list(LIVE_WARNINGS),
        "unavailable_fields": list(LIVE_UNAVAILABLE_FIELDS),
        "claim_boundary": dict(core.CLAIM_BOUNDARY),
    }


def _validate_result(result: Mapping[str, object], *, allow_complete: bool) -> None:
    try:
        core._walk_public(result)
    except core.WitnessRefusal as exc:
        raise LiveWitnessRefusal(
            "LIVE_OUTPUT_REFUSE", "protected value reached public output"
        ) from exc
    if (
        result.get("schema_name")
        != "neurodecodekit.fresh_motor_source_identity_witness_live_result"
        or result.get("schema_version") != SCHEMA_VERSION
        or result.get("packet_id") != PACKET_ID
        or result.get("implementation_id") != LIVE_IMPLEMENTATION_ID
        or result.get("packet_sha256") != core.PACKET_SHA256
        or result.get("producer_is_causal") != "not_applicable_source_identity_only"
        or result.get("end_to_end_latency_measured") is not False
        or result.get("runtime_measurement_endpoint") != "immediately_before_result_serialization"
        or result.get("peak_RSS_measurement_endpoint") != "immediately_before_result_serialization"
        or result.get("warnings") != list(LIVE_WARNINGS)
        or result.get("unavailable_fields") != list(LIVE_UNAVAILABLE_FIELDS)
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "result identity differs")
    if result.get("route") not in {
        "WITNESS_COMPLETE",
        "WITNESS_CAP_PARK",
        "WITNESS_TRANSPORT_PARK",
        "NAMED_FAIL_CLOSED_REFUSAL",
    }:
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "result route differs")
    if not allow_complete and result.get("route") == "WITNESS_COMPLETE":
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "complete route is unavailable")
    route = str(result["route"])
    route_fields = (
        RESULT_COMPLETE_FIELDS
        if route == "WITNESS_COMPLETE"
        else {"park_reason_class"}
        if route in {"WITNESS_CAP_PARK", "WITNESS_TRANSPORT_PARK"}
        else {"refusal_code"}
    )
    if set(result) != RESULT_BASE_FIELDS | route_fields:
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "result fields differ")
    runtime_seconds = result.get("runtime_seconds")
    peak_RSS = result.get("peak_RSS_bytes")
    if (
        not isinstance(runtime_seconds, (int, float))
        or isinstance(runtime_seconds, bool)
        or float(runtime_seconds) < 0
        or not isinstance(peak_RSS, int)
        or isinstance(peak_RSS, bool)
        or peak_RSS <= 0
        or result.get("CPU_threads") != 1
        or result.get("workers") != 1
        or result.get("numerical_jobs") != 1
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "result measurement differs")
    marker_bytes = result.get("consumed_marker_bytes")
    result_bytes = result.get("result_artifact_bytes")
    ledger_bytes = result.get("ledger_artifact_bytes")
    retained_bytes = result.get("retained_artifact_bytes")
    temporary_bytes = result.get("temporary_artifact_bytes")
    if (
        not all(
            isinstance(value, int) and not isinstance(value, bool)
            for value in (
                marker_bytes,
                result_bytes,
                ledger_bytes,
                retained_bytes,
                temporary_bytes,
            )
        )
        or int(marker_bytes) <= 0
        or int(result_bytes) <= 0
        or int(ledger_bytes) < 0
        or int(temporary_bytes) != 0
        or int(retained_bytes) != int(marker_bytes) + int(result_bytes) + int(ledger_bytes)
        or int(retained_bytes) > MAX_RETAINED_BYTES
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "artifact accounting differs")
    receipt = result.get("CI_W0_receipt")
    if receipt is not None:
        required_receipt_fields = {
            "local_HEAD_authority_commit",
            "authority_decision_blob_sha256",
            "current_main_ref_request_identity_sha256",
            "current_main_ref_response_sha256",
            "exact_check_runs_request_identity_sha256",
            "Base_Python_check_run_id",
            "Optional_Neuro_Readers_check_run_id",
            "check_runs_response_sha256",
            "workflow_blob_request_identity_sha256",
            "workflow_blob_response_sha256",
        }
        if (
            not isinstance(receipt, Mapping)
            or set(receipt) != required_receipt_fields
            or not isinstance(receipt.get("local_HEAD_authority_commit"), str)
            or len(str(receipt["local_HEAD_authority_commit"])) != 40
            or any(
                character not in "0123456789abcdef"
                for character in str(receipt["local_HEAD_authority_commit"])
            )
            or any(
                not isinstance(receipt.get(name), str)
                or core.HEX_64.fullmatch(str(receipt[name])) is None
                for name in required_receipt_fields
                if name
                not in {
                    "local_HEAD_authority_commit",
                    "Base_Python_check_run_id",
                    "Optional_Neuro_Readers_check_run_id",
                }
            )
            or any(
                not isinstance(receipt.get(name), int)
                or isinstance(receipt.get(name), bool)
                or int(receipt[name]) <= 0
                for name in (
                    "Base_Python_check_run_id",
                    "Optional_Neuro_Readers_check_run_id",
                )
            )
        ):
            raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "CI-W0 receipt differs")
    counters = result.get("operation_counters")
    if not isinstance(counters, Mapping) or any(
        counters.get(name) != 0
        for name in (
            "candidate_semantic_operations",
            "source_selections",
            "payload_or_neural_reads",
            "target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "scientific_claim_upgrades",
        )
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "protected operation counter differs")
    assert isinstance(counters, Mapping)
    CI_requests = counters.get("CI_requests")
    source_requests = counters.get("official_index_requests")
    total_requests = counters.get("network_requests")
    CI_bytes = counters.get("CI_decoded_bytes")
    source_wire = counters.get("official_index_wire_bytes")
    source_entity = counters.get("official_index_decoded_bytes")
    network_input = counters.get("network_input_bytes")
    if (
        not all(
            isinstance(value, int)
            for value in (
                CI_requests,
                source_requests,
                total_requests,
                CI_bytes,
                source_wire,
                source_entity,
                network_input,
            )
        )
        or not 0 <= int(CI_requests) <= MAX_CI_REQUESTS
        or not 0 <= int(source_requests) <= MAX_SOURCE_REQUESTS
        or int(total_requests) != int(CI_requests) + int(source_requests)
        or int(total_requests) > MAX_TOTAL_REQUESTS
        or not 0 <= int(CI_bytes) <= MAX_CI_BYTES
        or not 0 <= int(source_wire) <= MAX_SOURCE_WIRE_BYTES
        or not 0 <= int(source_entity) <= MAX_SOURCE_ENTITY_BYTES
        or int(network_input) != int(CI_bytes) + int(source_entity)
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "resource counters differ")
    if result.get("claim_boundary") != core.CLAIM_BOUNDARY:
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "claim boundary differs")
    transcript = result.get("state_transcript")
    if (
        not isinstance(transcript, list)
        or len(transcript) != len(set(transcript))
        or transcript[:2] != list(STATE_MACHINE[:2])
        or transcript[-2:] != list(STATE_MACHINE[-2:])
        or any(state not in STATE_MACHINE for state in transcript)
        or [STATE_MACHINE.index(state) for state in transcript]
        != sorted(STATE_MACHINE.index(state) for state in transcript)
    ):
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "state transcript differs")
    complete = result.get("route") == "WITNESS_COMPLETE"
    if complete:
        if (
            transcript != list(STATE_MACHINE)
            or receipt is None
            or int(ledger_bytes) <= 0
            or int(CI_requests) != MAX_CI_REQUESTS
            or int(source_requests) < 17
            or result.get("source_index_snapshot_identity_established") is not True
            or result.get("profile_count") != 5
            or result.get("root_count") != 17
            or not isinstance(result.get("page_count"), int)
            or int(result["page_count"]) < 17
            or not isinstance(result.get("global_ledger_sha256"), str)
            or core.HEX_64.fullmatch(str(result["global_ledger_sha256"])) is None
            or float(result.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1)) > MAX_RUNTIME_SECONDS
            or int(result.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1)) > MAX_PEAK_RSS_BYTES
        ):
            raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "complete result differs")
    elif int(ledger_bytes) != 0:
        raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "noncomplete result retained a ledger")


def _write_result_artifacts(
    attempt_root: Path,
    *,
    result_payload: bytes,
    ledger_payload: bytes,
) -> None:
    descriptor = _open_directory(attempt_root)
    try:
        if ledger_payload:
            _write_exclusive_at(descriptor, LEDGER_NAME, ledger_payload)
        _write_exclusive_at(descriptor, RESULT_NAME, result_payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _render_result_artifacts(
    result: Mapping[str, object],
    ledger: Mapping[str, object] | None,
    *,
    marker_bytes: int = 0,
) -> tuple[dict[str, object], bytes, bytes]:
    rendered = dict(result)
    ledger_payload = b"" if ledger is None else core.canonical_json_bytes(ledger, newline=True)
    rendered.update(
        {
            "ledger_artifact_bytes": len(ledger_payload),
            "result_artifact_bytes": 0,
            "retained_artifact_bytes": len(ledger_payload) + marker_bytes,
            "temporary_artifact_bytes": 0,
        }
    )
    for _iteration in range(8):
        result_payload = core.canonical_json_bytes(rendered, newline=True)
        next_result_bytes = len(result_payload)
        next_total = next_result_bytes + len(ledger_payload) + marker_bytes
        if (
            rendered["result_artifact_bytes"] == next_result_bytes
            and rendered["retained_artifact_bytes"] == next_total
        ):
            if next_total > MAX_RETAINED_BYTES:
                raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "retained output cap exceeded")
            _validate_result(rendered, allow_complete=ledger is not None)
            return rendered, result_payload, ledger_payload
        rendered["result_artifact_bytes"] = next_result_bytes
        rendered["retained_artifact_bytes"] = next_total
    raise LiveWitnessRefusal("LIVE_OUTPUT_REFUSE", "output byte accounting did not converge")


def execute_registered_witness() -> dict[str, object]:
    root = Path(__file__).resolve().parents[3]
    started = time.monotonic()
    deadline = started + MAX_RUNTIME_SECONDS
    states = ["CLOSED", "LOCAL_PREFLIGHT"]
    authority = local_preflight(root, environ=os.environ)
    reservation = reserve_consumed_attempt(root, authority)
    attempt_root = reservation.attempt_root
    marker_payload = reservation.marker_payload
    states.extend(("RESERVED_PENDING", "ARMED_CONSUMED"))
    budget = RequestBudget(started=started)
    audit = SemanticAccessAudit()
    CI_receipt: Mapping[str, object] | None = None
    ledger: Mapping[str, object] | None = None
    try:
        CI_receipt, ledger = _run_contact_sequence(
            root,
            authority,
            reservation,
            budget=budget,
            audit=audit,
            states=states,
            contact=direct_TLS_contact,
            deadline=deadline,
        )
        if (
            time.monotonic() > deadline - FINALIZATION_RESERVE_SECONDS
            or _peak_rss_bytes() > MAX_PEAK_RSS_BYTES
        ):
            raise LiveWitnessPark("WITNESS_CAP_PARK", "FINAL_RESOURCE_CAP")
        states.extend(("FINALIZE", "COMPLETE_OR_PARK"))
        result = _base_result(
            authority,
            budget,
            route="WITNESS_COMPLETE",
            started=started,
            state_transcript=states,
            audit=audit,
        )
        result.update(
            {
                "consumed_marker_bytes": len(marker_payload),
                "CI_W0_receipt": dict(CI_receipt),
                "profile_count": len(ledger["profiles"]),
                "root_count": ledger["total_root_count"],
                "page_count": ledger["total_page_count"],
                "global_ledger_sha256": ledger["canonical_global_ledger_sha256"],
                "source_index_snapshot_identity_established": True,
            }
        )
        rendered, result_payload, ledger_payload = _render_result_artifacts(
            result, ledger, marker_bytes=len(marker_payload)
        )
        _write_result_artifacts(
            attempt_root,
            result_payload=result_payload,
            ledger_payload=ledger_payload,
        )
        return rendered
    except LiveWitnessRefusal as exc:
        if "FINALIZE" not in states:
            states.append("FINALIZE")
        if "COMPLETE_OR_PARK" not in states:
            states.append("COMPLETE_OR_PARK")
        result = _base_result(
            authority,
            budget,
            route="NAMED_FAIL_CLOSED_REFUSAL",
            started=started,
            state_transcript=states,
            audit=audit,
        )
        result.update(
            {
                "consumed_marker_bytes": len(marker_payload),
                "refusal_code": exc.code,
                "CI_W0_receipt": None if CI_receipt is None else dict(CI_receipt),
            }
        )
        rendered, result_payload, ledger_payload = _render_result_artifacts(
            result, None, marker_bytes=len(marker_payload)
        )
        _write_result_artifacts(
            attempt_root,
            result_payload=result_payload,
            ledger_payload=ledger_payload,
        )
        return rendered
    except (LiveWitnessPark, core.WitnessRefusal) as exc:
        route = exc.route if isinstance(exc, LiveWitnessPark) else "WITNESS_TRANSPORT_PARK"
        reason = exc.reason_class if isinstance(exc, LiveWitnessPark) else exc.route
        if "FINALIZE" not in states:
            states.append("FINALIZE")
        if "COMPLETE_OR_PARK" not in states:
            states.append("COMPLETE_OR_PARK")
        result = _base_result(
            authority,
            budget,
            route=route,
            started=started,
            state_transcript=states,
            audit=audit,
        )
        result.update(
            {
                "consumed_marker_bytes": len(marker_payload),
                "park_reason_class": reason,
                "CI_W0_receipt": None if CI_receipt is None else dict(CI_receipt),
            }
        )
        rendered, result_payload, ledger_payload = _render_result_artifacts(
            result, None, marker_bytes=len(marker_payload)
        )
        _write_result_artifacts(
            attempt_root,
            result_payload=result_payload,
            ledger_payload=ledger_payload,
        )
        return rendered


def registered_live_plan() -> dict[str, object]:
    CI_profile = canonical_CI_W0_profile()
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_identity_witness_live_plan",
        "schema_version": SCHEMA_VERSION,
        "packet_id": PACKET_ID,
        "implementation_id": LIVE_IMPLEMENTATION_ID,
        "execution_decision_id": EXECUTION_DECISION_ID,
        "execution_decision_required": True,
        "commands": ["plan", "qualify-generated", "execute"],
        "generated_qualification_network_requests": 0,
        "official_index_profiles": 5,
        "root_request_count": 17,
        "CI_request_count": MAX_CI_REQUESTS,
        "maximum_official_index_requests": MAX_SOURCE_REQUESTS,
        "maximum_total_network_requests": MAX_TOTAL_REQUESTS,
        "CI_W0_profile_sha256": _sha256(core.canonical_json_bytes(CI_profile, newline=True)),
        "candidate_semantic_operations": 0,
        "payload_or_neural_reads": 0,
        "model_or_score_operations": 0,
        "scientific_claim_established": False,
    }
