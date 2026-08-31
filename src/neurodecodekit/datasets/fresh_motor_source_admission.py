"""Generated-only admission qualification for the FMSR1 source-discovery lane."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import resource
import stat
import sys
import tempfile
import time
from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path

SCHEMA_NAME = "neurodecodekit.fresh_motor_source_admission_generated_qualification"
SCHEMA_VERSION = "0.1.0"
PROTOCOL_ID = "FMSR1-R1-G-v0"

GENERATED_API_HOST = "api.github.invalid"
GENERATED_API_PORT = 443
GENERATED_API_VERSION = "generated-api-version"
GENERATED_ACCEPT = "application/vnd.github+json"
GENERATED_CONTENT_TYPE = "application/json; charset=utf-8"
GENERATED_TLS_PROFILE = "GENERATED_TLS_1_3_PEER_ATTESTATION"
GENERATED_REQUEST_HEADERS = (
    ("Accept", GENERATED_ACCEPT),
    ("X-GitHub-Api-Version", GENERATED_API_VERSION),
)
_ACTIVE_QUALIFICATION_ROOTS: set[Path] = set()

GREEN_REGISTRATION_COMMIT = "d53f3e8870b1f3ae6f014411c9932f20474b8092"
GREEN_REGISTRATION_CI_RUN_ID = 33_341_954_248
GREEN_REGISTRATION_BASE_JOB_ID = 99_339_083_749
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 99_339_083_636
CONTRACT_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_admission_generated_qualification_contract.v0.json"
)
CONTRACT_SHA256 = "e4716d08f85cdadce01afc4d96b65f92919f6eebdc580f68345193927bcc7979"
CONTRACT_BYTES = 14_837
CONTRACT_GIT_BLOB = "993120646633506bf4c6d4089aa534668aa04128"
FRONTIER_RELATIVE_PATH = Path("registries/current_research_frontier.v16.json")
FRONTIER_SHA256 = "e8f69c4359344827592e81161f85bbfd79278049e23394f1c4c891d5408b3e21"
FRONTIER_BYTES = 7_638
FRONTIER_GIT_BLOB = "7c3b7bb34442073d88f5c1d8377b0104284d6d4a"
ACTIVATION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_admission_generated_qualification_activation.v0.json"
)
OFFICIAL_QUALIFICATION_ROOT = Path(".codex_work/fmsr1-r1-g-v0-official")
IMPLEMENTATION_ARTIFACT_PATHS = (
    Path("src/neurodecodekit/datasets/fresh_motor_source_admission.py"),
    Path("src/neurodecodekit/fmsr1_admission_cli.py"),
    Path("tests/test_fresh_motor_source_admission.py"),
    Path("tests/test_fmsr1_admission_cli.py"),
)

MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_INPUT_BYTES = 4 * 1024**2
MAX_REPORT_BYTES = 1024**2
MAX_TEMP_BYTES = 2 * 1024**2
MAX_TEMP_FILES = 16
MAX_JSON_DEPTH = 16
MAX_STRING_BYTES = 65_536
MAX_CONTAINER_ITEMS = 4_096
MAX_CI_RESPONSE_BYTES = 1024**2
MAX_CI_TOTAL_BYTES = 2 * 1024**2
MAX_SERVER_DATE_SKEW_SECONDS = 300
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
INDEX_IDS = (
    "OPENNEURO_CRN",
    "NEMAR",
    "PHYSIONET",
    "GIGADB",
    "BNCI_HORIZON_2020",
)
GLOBAL_REVISION_IDS = frozenset({"OPENNEURO_CRN", "PHYSIONET"})
SNAPSHOT_IDS = frozenset({"NEMAR", "GIGADB", "BNCI_HORIZON_2020"})
REQUIRED_JOB_NAMES = ("Base Python", "Optional Neuro Readers")
REJECTED_ENV_NAMES = frozenset(
    {
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "no_proxy",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "REQUESTS_CA_BUNDLE",
        "CURL_CA_BUNDLE",
    }
)
REFUSAL_PRECEDENCE = (
    "AUTHORITY_REFUSE",
    "QUALIFICATION_NETWORK_REFUSE",
    "ORDER_REFUSE",
    "RESOURCE_REFUSE",
    "ENCODING_REFUSE",
    "DUPLICATE_REFUSE",
    "SCHEMA_REFUSE",
    "TRANSPORT_REFUSE",
    "IDENTITY_REFUSE",
    "REVISION_REFUSE",
    "SNAPSHOT_REFUSE",
    "CI_RUN_REFUSE",
    "CI_JOB_REFUSE",
)
REFUSAL_ROUTES = frozenset(REFUSAL_PRECEDENCE)
OPERATION_COUNTER_KEYS = (
    "DNS_calls",
    "socket_calls",
    "TLS_calls",
    "HTTP_calls",
    "credential_reads",
    "default_opener_calls",
    "real_or_captured_response_bytes",
    "real_source_reads",
    "candidate_metadata_reads",
    "payload_or_header_reads",
    "signal_event_annotation_target_or_label_reads",
    "model_runs",
    "training_runs",
    "prediction_sets",
    "scores",
    "provider_calls",
    "stream_device_or_hardware_runs",
    "operations_on_other_projects",
    "release_operations",
    "scientific_claim_upgrades",
)
WARNINGS = (
    "generated_fixtures_only_not_source_authentication",
    "injected_CI_responses_only_not_live_GitHub_verification",
    "generated_index_modes_do_not_admit_real_sources",
    "historical_run_branch_is_not_current_refs_heads_main",
    "workflow_blob_identity_remains_unavailable",
    "one_shot_generated_audit_marker_retained_under_git_ignored_codex_work",
    "qualification_is_not_neural_evidence",
)
UNAVAILABLE_FIELDS = (
    "live_GitHub_identity",
    "official_index_revision_or_snapshot",
    "source_authenticity",
    "workflow_blob_identity",
    "current_main_ref_identity",
    "candidate_dataset",
    "neural_measurement",
    "end_to_end_latency",
)
CLAIM_BOUNDARY = {
    "engineering_capability_added": (
        "A dependency-free generated validator separates revision, snapshot, "
        "attempt-specific CI, and consumed-marker evidence from malformed or "
        "ambiguous counterexamples without exposing live transport."
    ),
    "scientific_claim_not_established": (
        "Generated fixtures contain no human neural measurements, targets, "
        "predictions, or scores and establish no source authenticity, neural "
        "advantage, intention decoding, unseen-person generalization, language "
        "decoding, or live operation."
    ),
}


class FMSR1AdmissionRefusal(RuntimeError):
    """Fail closed with one stable R1-G refusal route."""

    def __init__(self, route: str, reason: str):
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown FMSR1 admission refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class InjectedResponse:
    """One generated HTTP envelope with no opener or transport capability."""

    request_identity_sha256: str
    status: int
    headers: tuple[tuple[str, str], ...]
    body: bytes
    provenance: str = "GENERATED_IN_PROCESS"
    request_host: str = GENERATED_API_HOST
    request_port: int = GENERATED_API_PORT
    request_headers: tuple[tuple[str, str], ...] = GENERATED_REQUEST_HEADERS
    preconnect_peer_global: bool = True
    postconnect_peer_unchanged: bool = True
    TLS_profile: str = GENERATED_TLS_PROFILE


@dataclass(slots=True)
class QualificationMetrics:
    generated_input_bytes: int = 0
    response_envelopes: int = 0
    marker_creates: int = 0
    marker_file_fsyncs: int = 0
    marker_directory_fsyncs: int = 0
    temporary_generated_bytes: int = 0
    temporary_generated_files: int = 0
    operation_counters: dict[str, int] = field(
        default_factory=lambda: {key: 0 for key in OPERATION_COUNTER_KEYS}
    )


def _refuse(route: str, reason: str) -> None:
    raise FMSR1AdmissionRefusal(route, reason)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("ascii")


def _reject_float(_value: str) -> object:
    _refuse("ENCODING_REFUSE", "floating-point JSON number")


def _reject_constant(_value: str) -> object:
    _refuse("ENCODING_REFUSE", "non-finite JSON number")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _refuse("DUPLICATE_REFUSE", "duplicate JSON key")
        result[key] = value
    return result


def _walk_json(value: object, *, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        _refuse("ENCODING_REFUSE", "JSON depth cap")
    if isinstance(value, str):
        if len(value.encode("utf-8")) > MAX_STRING_BYTES:
            _refuse("ENCODING_REFUSE", "JSON string cap")
        return
    if isinstance(value, Mapping):
        if len(value) > MAX_CONTAINER_ITEMS:
            _refuse("ENCODING_REFUSE", "JSON object item cap")
        for key, child in value.items():
            if not isinstance(key, str):
                _refuse("SCHEMA_REFUSE", "JSON object key is not text")
            _walk_json(key, depth=depth + 1)
            _walk_json(child, depth=depth + 1)
        return
    if isinstance(value, list):
        if len(value) > MAX_CONTAINER_ITEMS:
            _refuse("ENCODING_REFUSE", "JSON array item cap")
        for child in value:
            _walk_json(child, depth=depth + 1)


def strict_json_loads(payload: bytes) -> object:
    """Decode bounded canonical-input JSON while preserving ambiguity refusals."""

    if type(payload) is not bytes:
        _refuse("SCHEMA_REFUSE", "JSON payload is not exact bytes")
    if len(payload) > MAX_GENERATED_INPUT_BYTES:
        _refuse("RESOURCE_REFUSE", "generated input cap")
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        _refuse("ENCODING_REFUSE", "BOM or NUL in JSON")
    try:
        text = payload.decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_unique_object,
            parse_float=_reject_float,
            parse_constant=_reject_constant,
        )
    except UnicodeDecodeError as exc:
        raise FMSR1AdmissionRefusal(
            "ENCODING_REFUSE", "invalid UTF-8"
        ) from exc
    except json.JSONDecodeError as exc:
        raise FMSR1AdmissionRefusal(
            "ENCODING_REFUSE", "malformed or trailing JSON"
        ) from exc
    _walk_json(value)
    return value


def _exact_keys(value: Mapping[str, object], expected: set[str], route: str) -> None:
    if set(value) != expected:
        _refuse(route, "field set differs")


def _mapping(value: object, route: str = "SCHEMA_REFUSE") -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        _refuse(route, "expected object")
    return value


def _list(value: object, route: str = "SCHEMA_REFUSE") -> list[object]:
    if not isinstance(value, list):
        _refuse(route, "expected array")
    return value


def _text(value: object, route: str = "SCHEMA_REFUSE") -> str:
    if type(value) is not str or not value:
        _refuse(route, "expected nonempty text")
    return value


def _ascii_token(value: object, route: str = "SCHEMA_REFUSE") -> str:
    token = _text(value, route)
    try:
        encoded = token.encode("ascii")
    except UnicodeEncodeError:
        _refuse(route, "token is not exact ASCII")
    if encoded.decode("ascii") != token or token.strip() != token:
        _refuse(route, "token normalization differs")
    return token


def _positive_int(value: object, route: str = "SCHEMA_REFUSE") -> int:
    if type(value) is not int or value <= 0:
        _refuse(route, "expected positive exact integer")
    return value


def _nonnegative_int(value: object, route: str = "SCHEMA_REFUSE") -> int:
    if type(value) is not int or value < 0:
        _refuse(route, "expected nonnegative exact integer")
    return value


def _digest(value: object, route: str = "IDENTITY_REFUSE") -> str:
    digest = _ascii_token(value, route)
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        _refuse(route, "SHA-256 value differs")
    return digest


def _read_exact_artifact(path: Path, expected_bytes: int, expected_sha256: str) -> bytes:
    try:
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise OSError("artifact type differs")
        payload = path.read_bytes()
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "AUTHORITY_REFUSE", "registered artifact unavailable"
        ) from exc
    if len(payload) != expected_bytes or _sha256(payload) != expected_sha256:
        _refuse("AUTHORITY_REFUSE", "registered artifact identity differs")
    return payload


def _load_contract(repo_root: str | Path | None = None) -> Mapping[str, object]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    payload = _read_exact_artifact(
        root / CONTRACT_RELATIVE_PATH, CONTRACT_BYTES, CONTRACT_SHA256
    )
    _read_exact_artifact(root / FRONTIER_RELATIVE_PATH, FRONTIER_BYTES, FRONTIER_SHA256)
    contract = _mapping(strict_json_loads(payload), "AUTHORITY_REFUSE")
    predecessor = _mapping(contract.get("predecessor"), "AUTHORITY_REFUSE")
    surface = _mapping(contract.get("additive_surface"), "AUTHORITY_REFUSE")
    authority = _mapping(
        contract.get("operation_authority_after_exact_registration_green"),
        "AUTHORITY_REFUSE",
    )
    if (
        contract.get("protocol_id") != PROTOCOL_ID
        or predecessor.get("exact_green_state_commit")
        != "8fe98df7e08e7e1e40860e6023832c3b092d78d2"
        or predecessor.get("main_CI_run_id") != 33_340_527_773
        or surface.get("commands") != ["plan", "qualify-generated"]
        or surface.get("execute_command_present") is not False
        or surface.get("network_imports_allowed") != []
        or authority.get("additive_generated_only_implementation") is not True
        or authority.get("network_or_GitHub_API") is not False
        or authority.get("official_index_contact_or_source_witness") is not False
    ):
        _refuse("AUTHORITY_REFUSE", "registration boundary differs")
    return contract


def _load_implementation_activation(
    repo_root: str | Path | None = None,
) -> Mapping[str, object]:
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    path = root / ACTIVATION_RELATIVE_PATH
    try:
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise OSError("activation type differs")
        if info.st_size > 65_536:
            _refuse("RESOURCE_REFUSE", "activation byte cap")
        payload = path.read_bytes()
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "AUTHORITY_REFUSE", "implementation activation is not present"
        ) from exc
    record = _mapping(strict_json_loads(payload), "AUTHORITY_REFUSE")
    _exact_keys(
        record,
        {
            "schema_name",
            "schema_version",
            "protocol_id",
            "recorded_at",
            "status",
            "implementation_commit",
            "implementation_CI_run_id",
            "base_python_job_id",
            "optional_neuro_readers_job_id",
            "both_required_jobs_green",
            "bound_artifacts",
            "maximum_official_qualification_executions",
            "official_qualification_root",
            "network_or_GitHub_API_authority",
            "official_index_or_real_source_authority",
            "model_score_or_scientific_claim_authority",
        },
        "AUTHORITY_REFUSE",
    )
    commit = _ascii_token(record.get("implementation_commit"), "AUTHORITY_REFUSE")
    if len(commit) != 40 or any(character not in "0123456789abcdef" for character in commit):
        _refuse("AUTHORITY_REFUSE", "implementation commit identity differs")
    if (
        record.get("schema_name")
        != "neurodecodekit.fresh_motor_source_admission_generated_qualification_activation"
        or record.get("schema_version") != SCHEMA_VERSION
        or record.get("protocol_id") != PROTOCOL_ID
        or record.get("status") != "implementation_exact_green_activation"
        or commit == GREEN_REGISTRATION_COMMIT
        or _positive_int(record.get("implementation_CI_run_id"), "AUTHORITY_REFUSE")
        <= GREEN_REGISTRATION_CI_RUN_ID
        or _positive_int(record.get("base_python_job_id"), "AUTHORITY_REFUSE") <= 0
        or _positive_int(
            record.get("optional_neuro_readers_job_id"), "AUTHORITY_REFUSE"
        )
        <= 0
        or record.get("both_required_jobs_green") is not True
        or record.get("maximum_official_qualification_executions") != 1
        or record.get("official_qualification_root")
        != OFFICIAL_QUALIFICATION_ROOT.as_posix()
        or record.get("network_or_GitHub_API_authority") is not False
        or record.get("official_index_or_real_source_authority") is not False
        or record.get("model_score_or_scientific_claim_authority") is not False
    ):
        _refuse("AUTHORITY_REFUSE", "implementation activation boundary differs")
    artifacts = _list(record.get("bound_artifacts"), "AUTHORITY_REFUSE")
    if len(artifacts) != len(IMPLEMENTATION_ARTIFACT_PATHS):
        _refuse("AUTHORITY_REFUSE", "implementation artifact count differs")
    for row_value, expected_path in zip(
        artifacts, IMPLEMENTATION_ARTIFACT_PATHS, strict=True
    ):
        row = _mapping(row_value, "AUTHORITY_REFUSE")
        _exact_keys(row, {"path", "bytes", "sha256"}, "AUTHORITY_REFUSE")
        if row.get("path") != expected_path.as_posix():
            _refuse("AUTHORITY_REFUSE", "implementation artifact path differs")
        expected_bytes = _positive_int(row.get("bytes"), "AUTHORITY_REFUSE")
        expected_sha256 = _digest(row.get("sha256"), "AUTHORITY_REFUSE")
        _read_exact_artifact(root / expected_path, expected_bytes, expected_sha256)
    return record


def _generated_authority_profile() -> dict[str, object]:
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_admission.authority",
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "contract_sha256": CONTRACT_SHA256,
        "stage": "R1_G_GENERATED_ONLY",
        "saved_receipt_authority": False,
        "live_profile_state": "ABSENT",
        "captured_real_response_bytes": 0,
        "network_authority": False,
        "official_source_authority": False,
        "scientific_claim_authority": False,
    }


def validate_generated_authority_profile(value: object) -> dict[str, object]:
    """Accept only the exact closed-authority generated fixture profile."""

    profile = _mapping(value, "AUTHORITY_REFUSE")
    expected = _generated_authority_profile()
    _exact_keys(profile, set(expected), "AUTHORITY_REFUSE")
    if profile != expected:
        _refuse("AUTHORITY_REFUSE", "generated authority profile differs")
    return {
        "protocol_id": PROTOCOL_ID,
        "stage": "R1_G_GENERATED_ONLY",
        "network_authority": False,
        "official_source_authority": False,
        "scientific_claim_authority": False,
    }


def _generated_CI_profile() -> dict[str, object]:
    return {
        "run_request_identity_sha256": _sha256(b"generated-run-attempt-request"),
        "jobs_request_identity_sha256": _sha256(b"generated-jobs-attempt-request"),
        "api_version": GENERATED_API_VERSION,
        "accept": GENERATED_ACCEPT,
        "content_type": GENERATED_CONTENT_TYPE,
        "now_epoch": 1_800_000_000,
        "repository_id": 1001,
        "owner_id": 2001,
        "head_repository_id": 1001,
        "head_owner_id": 2001,
        "workflow_id": 3001,
        "run_id": 4001,
        "head_sha": "1234567890abcdef1234567890abcdef12345678",
        "event": "push",
        "head_branch": "main",
        "run_attempt": 1,
        "required_job_ids": {
            "Base Python": 5001,
            "Optional Neuro Readers": 5002,
        },
    }


def _validate_global_revision(index_id: str, value: object) -> dict[str, object]:
    revision = _mapping(value)
    expected = {
        "index_id",
        "issuer_id",
        "source_host",
        "revision_kind",
        "extraction_location",
        "revision_raw_bytes",
        "revision_raw_bytes_sha256",
        "extraction_rule_sha256",
        "request_profile_sha256",
        "scope_evidence_sha256",
        "complete_registered_traversal_scope",
        "pre_traversal_revision_raw_bytes_sha256",
        "post_traversal_revision_raw_bytes_sha256",
    }
    _exact_keys(revision, expected, "SCHEMA_REFUSE")
    if revision.get("index_id") != index_id:
        _refuse("IDENTITY_REFUSE", "global revision index differs")
    expected_revision = _generated_global_revision(index_id)
    issuer = _ascii_token(revision.get("issuer_id"), "IDENTITY_REFUSE")
    host = _ascii_token(revision.get("source_host"), "IDENTITY_REFUSE")
    if host != host.lower() or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789.-" for character in host):
        _refuse("IDENTITY_REFUSE", "source host differs")
    if issuer != expected_revision["issuer_id"] or host != expected_revision["source_host"]:
        _refuse("IDENTITY_REFUSE", "issuer or source host identity differs")
    if revision.get("revision_kind") != expected_revision["revision_kind"]:
        _refuse("REVISION_REFUSE", "revision kind is not source-global")
    extraction_location = _ascii_token(
        revision.get("extraction_location"), "REVISION_REFUSE"
    )
    if extraction_location != expected_revision["extraction_location"]:
        _refuse("REVISION_REFUSE", "revision extraction location differs")
    raw_text = _text(revision.get("revision_raw_bytes"), "REVISION_REFUSE")
    raw_digest = _sha256(raw_text.encode("utf-8"))
    if _digest(revision.get("revision_raw_bytes_sha256"), "REVISION_REFUSE") != raw_digest:
        _refuse("REVISION_REFUSE", "raw revision hash differs")
    if (
        raw_text != expected_revision["revision_raw_bytes"]
        or raw_digest != expected_revision["revision_raw_bytes_sha256"]
        or _digest(revision.get("extraction_rule_sha256"), "REVISION_REFUSE")
        != expected_revision["extraction_rule_sha256"]
        or _digest(revision.get("scope_evidence_sha256"), "REVISION_REFUSE")
        != expected_revision["scope_evidence_sha256"]
    ):
        _refuse("REVISION_REFUSE", "registered revision evidence differs")
    request_profile_digest = _digest(
        revision.get("request_profile_sha256"), "IDENTITY_REFUSE"
    )
    expected_request_profile_digest = expected_revision["request_profile_sha256"]
    if request_profile_digest != expected_request_profile_digest:
        _refuse("IDENTITY_REFUSE", "request profile identity differs")
    if revision.get("complete_registered_traversal_scope") is not True:
        _refuse("REVISION_REFUSE", "revision scope is incomplete")
    if (
        _digest(
            revision.get("pre_traversal_revision_raw_bytes_sha256"),
            "REVISION_REFUSE",
        )
        != raw_digest
        or _digest(
            revision.get("post_traversal_revision_raw_bytes_sha256"),
            "REVISION_REFUSE",
        )
        != raw_digest
    ):
        _refuse("REVISION_REFUSE", "pre/post revision observation differs")
    return {
        "index_id": index_id,
        "mode": "SOURCE_GLOBAL_REVISION",
        "revision_sha256": raw_digest,
    }


def _validate_redirects(value: object) -> list[dict[str, object]]:
    redirects = _list(value)
    projected: list[dict[str, object]] = []
    for ordinal, row_value in enumerate(redirects):
        row = _mapping(row_value)
        _exact_keys(
            row,
            {
                "ordinal",
                "status",
                "request_identity_sha256",
                "location_identity_sha256",
                "method",
            },
            "SNAPSHOT_REFUSE",
        )
        if row.get("ordinal") != ordinal or row.get("status") not in {301, 302, 303, 307, 308}:
            _refuse("SNAPSHOT_REFUSE", "redirect transcript differs")
        projected.append(
            {
                "ordinal": ordinal,
                "status": row["status"],
                "request_identity_sha256": _digest(
                    row.get("request_identity_sha256"), "SNAPSHOT_REFUSE"
                ),
                "location_identity_sha256": _digest(
                    row.get("location_identity_sha256"), "SNAPSHOT_REFUSE"
                ),
                "method": _ascii_token(row.get("method"), "SNAPSHOT_REFUSE"),
            }
        )
    return projected


def _validate_snapshot(index_id: str, value: object) -> dict[str, object]:
    snapshot = _mapping(value)
    _exact_keys(snapshot, {"complete", "ledger_sha256", "pages"}, "SCHEMA_REFUSE")
    if snapshot.get("complete") is not True:
        _refuse("SNAPSHOT_REFUSE", "snapshot is incomplete")
    pages = _list(snapshot.get("pages"), "SNAPSHOT_REFUSE")
    if not pages:
        _refuse("SNAPSHOT_REFUSE", "snapshot has no pages")
    projected: list[dict[str, object]] = []
    request_ids: list[str] = []
    pagination_ids: set[str] = set()
    body_hashes: set[str] = set()
    for ordinal, page_value in enumerate(pages):
        page = _mapping(page_value, "SNAPSHOT_REFUSE")
        _exact_keys(
            page,
            {
                "ordinal",
                "request_identity_sha256",
                "redirect_transcript",
                "pagination_identity_sha256",
                "response_body_bytes",
                "response_body_sha256",
                "next_request_identity_sha256",
                "terminal_state",
            },
            "SNAPSHOT_REFUSE",
        )
        if page.get("ordinal") != ordinal:
            _refuse("SNAPSHOT_REFUSE", "snapshot page ordinal gap")
        request_id = _digest(page.get("request_identity_sha256"), "SNAPSHOT_REFUSE")
        pagination_id = _digest(
            page.get("pagination_identity_sha256"), "SNAPSHOT_REFUSE"
        )
        body_hash = _digest(page.get("response_body_sha256"), "SNAPSHOT_REFUSE")
        body_bytes = _positive_int(page.get("response_body_bytes"), "SNAPSHOT_REFUSE")
        if request_id in request_ids or pagination_id in pagination_ids or body_hash in body_hashes:
            _refuse("SNAPSHOT_REFUSE", "snapshot duplicate or cycle")
        request_ids.append(request_id)
        pagination_ids.add(pagination_id)
        body_hashes.add(body_hash)
        terminal = page.get("terminal_state")
        next_request = page.get("next_request_identity_sha256")
        if terminal not in {"CONTINUE", "TERMINAL"}:
            _refuse("SNAPSHOT_REFUSE", "snapshot terminal state differs")
        if terminal == "TERMINAL":
            if ordinal != len(pages) - 1 or next_request is not None:
                _refuse("SNAPSHOT_REFUSE", "terminal snapshot page differs")
        else:
            if ordinal == len(pages) - 1:
                _refuse("SNAPSHOT_REFUSE", "snapshot lacks terminal page")
            next_request = _digest(next_request, "SNAPSHOT_REFUSE")
        projected.append(
            {
                "ordinal": ordinal,
                "request_identity_sha256": request_id,
                "redirect_transcript": _validate_redirects(
                    page.get("redirect_transcript")
                ),
                "pagination_identity_sha256": pagination_id,
                "response_body_bytes": body_bytes,
                "response_body_sha256": body_hash,
                "next_request_identity_sha256": next_request,
                "terminal_state": terminal,
            }
        )
    for ordinal, page in enumerate(projected[:-1]):
        if page["next_request_identity_sha256"] != projected[ordinal + 1][
            "request_identity_sha256"
        ]:
            _refuse("SNAPSHOT_REFUSE", "snapshot pagination fork")
    expected_ledger = _sha256(canonical_json_bytes(projected))
    if _digest(snapshot.get("ledger_sha256"), "IDENTITY_REFUSE") != expected_ledger:
        _refuse("IDENTITY_REFUSE", "snapshot ledger identity differs")
    generated_snapshot = _generated_snapshot(index_id)
    if (
        projected != generated_snapshot["pages"]
        or expected_ledger != generated_snapshot["ledger_sha256"]
    ):
        _refuse("IDENTITY_REFUSE", "generated snapshot evidence differs")
    return {
        "index_id": index_id,
        "mode": "OPAQUE_COMPLETE_SNAPSHOT_REPLAY",
        "page_count": len(projected),
        "ledger_sha256": expected_ledger,
    }


def validate_revision_bundle(payload: bytes) -> dict[str, object]:
    """Validate all five generated revision/snapshot profiles."""

    root = _mapping(strict_json_loads(payload))
    _exact_keys(root, {"schema_name", "schema_version", "profiles"}, "SCHEMA_REFUSE")
    if (
        root.get("schema_name")
        != "neurodecodekit.fresh_motor_source_admission.revision_bundle"
        or root.get("schema_version") != SCHEMA_VERSION
    ):
        _refuse("SCHEMA_REFUSE", "revision bundle identity differs")
    profiles = _list(root.get("profiles"))
    if len(profiles) != len(INDEX_IDS):
        _refuse("IDENTITY_REFUSE", "revision profile count differs")
    projected: list[dict[str, object]] = []
    observed_ids: list[str] = []
    for expected_id, profile_value in zip(INDEX_IDS, profiles, strict=True):
        profile = _mapping(profile_value)
        _exact_keys(
            profile,
            {"index_id", "mode", "source_global_revision", "opaque_complete_snapshot_replay"},
            "SCHEMA_REFUSE",
        )
        index_id = _ascii_token(profile.get("index_id"), "IDENTITY_REFUSE")
        if index_id in observed_ids:
            _refuse("DUPLICATE_REFUSE", "duplicate index identity")
        if index_id != expected_id:
            _refuse("IDENTITY_REFUSE", "index order differs")
        observed_ids.append(index_id)
        mode = profile.get("mode")
        global_value = profile.get("source_global_revision")
        snapshot_value = profile.get("opaque_complete_snapshot_replay")
        if mode == "SOURCE_GLOBAL_REVISION":
            if index_id not in GLOBAL_REVISION_IDS or global_value is None or snapshot_value is not None:
                _refuse("SCHEMA_REFUSE", "global revision one-of differs")
            projected.append(_validate_global_revision(index_id, global_value))
        elif mode == "OPAQUE_COMPLETE_SNAPSHOT_REPLAY":
            if index_id not in SNAPSHOT_IDS or snapshot_value is None or global_value is not None:
                _refuse("SCHEMA_REFUSE", "snapshot one-of differs")
            projected.append(_validate_snapshot(index_id, snapshot_value))
        else:
            _refuse("SCHEMA_REFUSE", "revision mode differs")
    return {
        "profile_count": len(projected),
        "global_revision_count": sum(
            row["mode"] == "SOURCE_GLOBAL_REVISION" for row in projected
        ),
        "snapshot_count": sum(
            row["mode"] == "OPAQUE_COMPLETE_SNAPSHOT_REPLAY" for row in projected
        ),
        "profiles": projected,
        "bundle_sha256": _sha256(canonical_json_bytes(projected)),
    }


def _header_map(headers: Sequence[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for name, value in headers:
        if type(name) is not str or type(value) is not str:
            _refuse("TRANSPORT_REFUSE", "header type differs")
        key = name.casefold()
        if key in result:
            _refuse("DUPLICATE_REFUSE", "duplicate singleton header")
        result[key] = value
    return result


def validate_transport_environment(
    environ: Mapping[str, str],
    *,
    system_proxy_present: bool = False,
    custom_SSL_context_supplied: bool = False,
) -> None:
    """Reject every generated proxy, custom-CA, or caller-TLS mutation."""

    if system_proxy_present or custom_SSL_context_supplied:
        _refuse("TRANSPORT_REFUSE", "system proxy or custom SSL context")
    for name, value in environ.items():
        folded = name.casefold()
        if value and (
            name in REJECTED_ENV_NAMES
            or "proxy" in folded
            or folded
            in {
                "ssl_cert_file",
                "ssl_cert_dir",
                "requests_ca_bundle",
                "curl_ca_bundle",
            }
        ):
            _refuse("TRANSPORT_REFUSE", "proxy or custom-CA environment")


def _validate_envelope(
    response: InjectedResponse,
    *,
    expected_request_identity: str,
    expected_content_type: str,
    now_epoch: int,
    jobs_response: bool,
) -> Mapping[str, object]:
    if type(response) is not InjectedResponse:
        _refuse("AUTHORITY_REFUSE", "captured or unregistered response type")
    if response.provenance != "GENERATED_IN_PROCESS":
        _refuse("AUTHORITY_REFUSE", "captured or real response provenance")
    if (
        response.request_host != GENERATED_API_HOST
        or response.request_port != GENERATED_API_PORT
        or response.preconnect_peer_global is not True
        or response.postconnect_peer_unchanged is not True
        or response.TLS_profile != GENERATED_TLS_PROFILE
    ):
        _refuse("TRANSPORT_REFUSE", "host port peer or TLS profile differs")
    request_headers = _header_map(response.request_headers)
    if request_headers != {
        "accept": GENERATED_ACCEPT,
        "x-github-api-version": GENERATED_API_VERSION,
    }:
        _refuse("TRANSPORT_REFUSE", "request header profile differs")
    if response.request_identity_sha256 != expected_request_identity:
        _refuse("TRANSPORT_REFUSE", "request identity differs")
    if type(response.status) is not int or response.status != 200:
        _refuse("TRANSPORT_REFUSE", "HTTP status differs")
    if len(response.body) > MAX_CI_RESPONSE_BYTES:
        _refuse("RESOURCE_REFUSE", "CI response byte cap")
    headers = _header_map(response.headers)
    if any(key in headers for key in ("location", "set-cookie", "www-authenticate")):
        _refuse("TRANSPORT_REFUSE", "redirect credential or cookie header")
    if headers.get("content-type") != expected_content_type:
        _refuse("TRANSPORT_REFUSE", "content type differs")
    if headers.get("content-encoding", "identity") != "identity":
        _refuse("TRANSPORT_REFUSE", "content encoding differs")
    if headers.get("age", "0") != "0":
        _refuse("CI_RUN_REFUSE", "cached response age differs")
    if jobs_response and "link" in headers:
        _refuse("CI_JOB_REFUSE", "job pagination is present")
    if "content-length" not in headers:
        _refuse("TRANSPORT_REFUSE", "content length is absent")
    try:
        content_length = int(headers["content-length"])
    except ValueError as exc:
        raise FMSR1AdmissionRefusal(
            "TRANSPORT_REFUSE", "content length is malformed"
        ) from exc
    if content_length != len(response.body):
        _refuse("TRANSPORT_REFUSE", "content length differs")
    try:
        server_date = parsedate_to_datetime(headers["date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise FMSR1AdmissionRefusal(
            "CI_RUN_REFUSE", "server date is unavailable"
        ) from exc
    if server_date.tzinfo is None:
        server_date = server_date.replace(tzinfo=UTC)
    if abs(server_date.timestamp() - now_epoch) > MAX_SERVER_DATE_SKEW_SECONDS:
        _refuse("CI_RUN_REFUSE", "server date is stale")
    return _mapping(strict_json_loads(response.body))


def validate_github_ci_evidence(
    profile: Mapping[str, object],
    run_response: InjectedResponse,
    jobs_response: InjectedResponse,
    *,
    environ: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Validate generated attempt-specific GitHub run and jobs responses."""

    _exact_keys(
        profile,
        {
            "run_request_identity_sha256",
            "jobs_request_identity_sha256",
            "api_version",
            "accept",
            "content_type",
            "now_epoch",
            "repository_id",
            "owner_id",
            "head_repository_id",
            "head_owner_id",
            "workflow_id",
            "run_id",
            "head_sha",
            "event",
            "head_branch",
            "run_attempt",
            "required_job_ids",
        },
        "SCHEMA_REFUSE",
    )
    expected_profile = _generated_CI_profile()
    validate_transport_environment({} if environ is None else environ)
    run_request = _digest(profile.get("run_request_identity_sha256"), "IDENTITY_REFUSE")
    jobs_request = _digest(profile.get("jobs_request_identity_sha256"), "IDENTITY_REFUSE")
    if (
        run_request != expected_profile["run_request_identity_sha256"]
        or jobs_request != expected_profile["jobs_request_identity_sha256"]
    ):
        _refuse("IDENTITY_REFUSE", "generated request identity differs")
    api_version = _ascii_token(profile.get("api_version"), "TRANSPORT_REFUSE")
    accept = _ascii_token(profile.get("accept"), "TRANSPORT_REFUSE")
    content_type = _ascii_token(profile.get("content_type"), "TRANSPORT_REFUSE")
    if (
        api_version != expected_profile["api_version"]
        or accept != expected_profile["accept"]
        or content_type != expected_profile["content_type"]
    ):
        _refuse("CI_RUN_REFUSE", "generated API profile differs")
    now_epoch = _positive_int(profile.get("now_epoch"), "CI_RUN_REFUSE")
    repository_id = _positive_int(profile.get("repository_id"), "CI_RUN_REFUSE")
    owner_id = _positive_int(profile.get("owner_id"), "CI_RUN_REFUSE")
    head_repository_id = _positive_int(
        profile.get("head_repository_id"), "CI_RUN_REFUSE"
    )
    head_owner_id = _positive_int(profile.get("head_owner_id"), "CI_RUN_REFUSE")
    if repository_id != head_repository_id or owner_id != head_owner_id:
        _refuse("CI_RUN_REFUSE", "repository/head repository identity differs")
    workflow_id = _positive_int(profile.get("workflow_id"), "CI_RUN_REFUSE")
    run_id = _positive_int(profile.get("run_id"), "CI_RUN_REFUSE")
    head_sha = _ascii_token(profile.get("head_sha"), "CI_RUN_REFUSE")
    if len(head_sha) != 40 or any(character not in "0123456789abcdef" for character in head_sha):
        _refuse("CI_RUN_REFUSE", "head SHA differs")
    if profile.get("event") != "push" or profile.get("head_branch") != "main":
        _refuse("CI_RUN_REFUSE", "event or historical branch differs")
    if profile.get("run_attempt") != 1:
        _refuse("CI_RUN_REFUSE", "run attempt differs")
    if any(
        profile.get(key) != expected_profile[key]
        for key in (
            "now_epoch",
            "repository_id",
            "owner_id",
            "head_repository_id",
            "head_owner_id",
            "workflow_id",
            "run_id",
            "head_sha",
            "event",
            "head_branch",
            "run_attempt",
        )
    ):
        _refuse("CI_RUN_REFUSE", "generated CI run profile differs")
    required_ids = _mapping(profile.get("required_job_ids"), "CI_JOB_REFUSE")
    if set(required_ids) != set(REQUIRED_JOB_NAMES):
        _refuse("CI_JOB_REFUSE", "required job names differ")
    expected_job_ids = {
        name: _positive_int(required_ids[name], "CI_JOB_REFUSE")
        for name in REQUIRED_JOB_NAMES
    }
    if len(set(expected_job_ids.values())) != 2:
        _refuse("DUPLICATE_REFUSE", "duplicate required job ID")
    if expected_job_ids != expected_profile["required_job_ids"]:
        _refuse("CI_JOB_REFUSE", "generated CI job profile differs")
    if len(run_response.body) + len(jobs_response.body) > MAX_CI_TOTAL_BYTES:
        _refuse("RESOURCE_REFUSE", "cumulative CI response byte cap")
    run = _validate_envelope(
        run_response,
        expected_request_identity=run_request,
        expected_content_type=content_type,
        now_epoch=now_epoch,
        jobs_response=False,
    )
    jobs_root = _validate_envelope(
        jobs_response,
        expected_request_identity=jobs_request,
        expected_content_type=content_type,
        now_epoch=now_epoch,
        jobs_response=True,
    )
    repository = _mapping(run.get("repository"), "CI_RUN_REFUSE")
    head_repository = _mapping(run.get("head_repository"), "CI_RUN_REFUSE")
    repository_owner = _mapping(repository.get("owner"), "CI_RUN_REFUSE")
    head_owner = _mapping(head_repository.get("owner"), "CI_RUN_REFUSE")
    if (
        run.get("id") != run_id
        or run.get("workflow_id") != workflow_id
        or run.get("run_attempt") != 1
        or run.get("head_sha") != head_sha
        or run.get("event") != "push"
        or run.get("head_branch") != "main"
        or run.get("status") != "completed"
        or run.get("conclusion") != "success"
        or repository.get("id") != repository_id
        or repository_owner.get("id") != owner_id
        or head_repository.get("id") != head_repository_id
        or head_owner.get("id") != head_owner_id
    ):
        _refuse("CI_RUN_REFUSE", "workflow run identity or conclusion differs")
    jobs = _list(jobs_root.get("jobs"), "CI_JOB_REFUSE")
    if jobs_root.get("total_count") != 2 or len(jobs) != 2:
        _refuse("CI_JOB_REFUSE", "job total count differs")
    observed_names: set[str] = set()
    observed_ids: set[int] = set()
    for job_value in jobs:
        job = _mapping(job_value, "CI_JOB_REFUSE")
        name = _ascii_token(job.get("name"), "CI_JOB_REFUSE")
        job_id = _positive_int(job.get("id"), "CI_JOB_REFUSE")
        if name in observed_names:
            _refuse("CI_JOB_REFUSE", "duplicate required job name")
        if job_id in observed_ids:
            _refuse("DUPLICATE_REFUSE", "duplicate job ID")
        observed_names.add(name)
        observed_ids.add(job_id)
        if (
            name not in expected_job_ids
            or expected_job_ids[name] != job_id
            or job.get("run_id") != run_id
            or job.get("run_attempt") != 1
            or job.get("head_sha") != head_sha
            or job.get("status") != "completed"
            or job.get("conclusion") != "success"
        ):
            _refuse("CI_JOB_REFUSE", "required job identity or conclusion differs")
    if observed_names != set(REQUIRED_JOB_NAMES):
        _refuse("CI_JOB_REFUSE", "required job set differs")
    return {
        "run_id": run_id,
        "workflow_id": workflow_id,
        "head_sha": head_sha,
        "head_branch": "main",
        "event": "push",
        "run_attempt": 1,
        "required_jobs": [
            {"name": name, "job_id": expected_job_ids[name]}
            for name in REQUIRED_JOB_NAMES
        ],
        "response_count": 2,
        "response_bytes": len(run_response.body) + len(jobs_response.body),
    }


def validate_execution_order(
    events: Sequence[str],
    *,
    marker_already_exists: bool = False,
    resumed_from_receipt: bool = False,
    mutable_handoff: bool = False,
    reused_stage: bool = False,
) -> dict[str, object]:
    """Validate the future same-process marker -> CI -> source order."""

    if marker_already_exists:
        _refuse("ORDER_REFUSE", "consumed marker already exists")
    if resumed_from_receipt or mutable_handoff or reused_stage:
        _refuse("ORDER_REFUSE", "resume handoff or CI-stage reuse")
    exact = ("marker_durable", "CI_W0_success", "source_contact_started")
    if tuple(events) != exact:
        _refuse("ORDER_REFUSE", "execution event order differs")
    return {"events": list(exact), "same_process": True, "receipt_authority": False}


@contextmanager
def _qualification_temp_root(prefix: str = "fmsr1-r1g-") -> Iterator[Path]:
    """Create and register the only filesystem root generated work may mutate."""

    with tempfile.TemporaryDirectory(prefix=prefix) as temporary:
        root = Path(temporary).resolve(strict=True)
        info = os.lstat(root)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            _refuse("ORDER_REFUSE", "qualification root type differs")
        if root in _ACTIVE_QUALIFICATION_ROOTS:
            _refuse("ORDER_REFUSE", "qualification root is already active")
        _ACTIVE_QUALIFICATION_ROOTS.add(root)
        try:
            yield root
        finally:
            _ACTIVE_QUALIFICATION_ROOTS.discard(root)


@contextmanager
def _official_qualification_root(
    repo_root: str | Path | None = None,
) -> Iterator[tuple[Path, dict[str, object]]]:
    """Create the durable one-shot generated audit root without deleting it."""

    root = (
        Path(repo_root).resolve(strict=True)
        if repo_root is not None
        else Path(__file__).resolve().parents[3]
    )
    root_info = os.lstat(root)
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        _refuse("ORDER_REFUSE", "repository root type differs")
    work_root = root / OFFICIAL_QUALIFICATION_ROOT.parent
    try:
        os.mkdir(work_root, 0o700)
    except FileExistsError:
        pass
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "generated work root unavailable"
        ) from exc
    _assert_regular_directory_no_follow(work_root)
    attempt_root = root / OFFICIAL_QUALIFICATION_ROOT
    try:
        os.mkdir(attempt_root, 0o700)
    except FileExistsError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "official generated qualification is already consumed"
        ) from exc
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "official qualification root unavailable"
        ) from exc
    attempt_root = attempt_root.resolve(strict=True)
    _ACTIVE_QUALIFICATION_ROOTS.add(attempt_root)
    marker_bytes = canonical_json_bytes(
        {
            "execution_ordinal": 1,
            "generated": True,
            "protocol_id": PROTOCOL_ID,
            "stage": "OFFICIAL_GENERATED_QUALIFICATION",
        }
    )
    try:
        marker = create_consumed_marker(
            attempt_root,
            marker_bytes,
            expected_stage="OFFICIAL_GENERATED_QUALIFICATION",
        )
        yield attempt_root, marker
    finally:
        _ACTIVE_QUALIFICATION_ROOTS.discard(attempt_root)


def _assert_regular_directory_no_follow(path: Path) -> None:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "generated directory unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
        _refuse("ORDER_REFUSE", "generated directory type differs")


def _assert_qualification_owned_directory(path: Path) -> None:
    try:
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError("directory type differs")
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "qualification directory unavailable"
        ) from exc
    if not any(
        resolved == root or root in resolved.parents
        for root in _ACTIVE_QUALIFICATION_ROOTS
    ):
        _refuse("ORDER_REFUSE", "directory is outside active qualification root")


def create_consumed_marker(
    parent: str | Path,
    marker_bytes: bytes,
    *,
    expected_stage: str,
    file_fsync: Callable[[int], None] = os.fsync,
    directory_fsync: Callable[[int], None] = os.fsync,
) -> dict[str, object]:
    """Create one durable no-follow generated consumed marker."""

    parent_path = Path(parent)
    _assert_qualification_owned_directory(parent_path)
    if type(marker_bytes) is not bytes or not marker_bytes:
        _refuse("SCHEMA_REFUSE", "marker bytes differ")
    marker_value = strict_json_loads(marker_bytes)
    if canonical_json_bytes(marker_value) != marker_bytes:
        _refuse("SCHEMA_REFUSE", "marker bytes are not canonical")
    marker = _mapping(marker_value, "SCHEMA_REFUSE")
    _exact_keys(
        marker,
        {"protocol_id", "stage", "execution_ordinal", "generated"},
        "SCHEMA_REFUSE",
    )
    if expected_stage not in {"CI_W0", "OFFICIAL_GENERATED_QUALIFICATION"}:
        _refuse("AUTHORITY_REFUSE", "marker stage authority differs")
    if marker != {
        "protocol_id": PROTOCOL_ID,
        "stage": expected_stage,
        "execution_ordinal": 1,
        "generated": True,
    }:
        _refuse("ORDER_REFUSE", "marker identity differs")
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        _refuse("ORDER_REFUSE", "required no-follow directory flags unavailable")
    try:
        info = os.lstat(parent_path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise OSError("parent type differs")
        directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        parent_fd = os.open(parent_path, directory_flags)
        opened_info = os.fstat(parent_fd)
        if (opened_info.st_dev, opened_info.st_ino) != (info.st_dev, info.st_ino):
            raise OSError("parent identity changed")
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "marker parent unavailable"
        ) from exc
    marker_fd: int | None = None
    try:
        marker_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW
        marker_fd = os.open(
            "consumed.json", marker_flags, 0o600, dir_fd=parent_fd
        )
        offset = 0
        while offset < len(marker_bytes):
            written = os.write(marker_fd, marker_bytes[offset:])
            if written <= 0:
                raise OSError("marker write stalled")
            offset += written
        file_fsync(marker_fd)
        os.close(marker_fd)
        marker_fd = None
        directory_fsync(parent_fd)
        marker_info = os.stat("consumed.json", dir_fd=parent_fd, follow_symlinks=False)
        if stat.S_IMODE(marker_info.st_mode) != 0o600 or not stat.S_ISREG(marker_info.st_mode):
            _refuse("ORDER_REFUSE", "marker mode or type differs")
    except FMSR1AdmissionRefusal:
        raise
    except OSError as exc:
        raise FMSR1AdmissionRefusal(
            "ORDER_REFUSE", "marker creation or durability failed"
        ) from exc
    finally:
        if marker_fd is not None:
            os.close(marker_fd)
        os.close(parent_fd)
    return {
        "marker_name": "consumed.json",
        "bytes": len(marker_bytes),
        "sha256": _sha256(marker_bytes),
        "mode": "0600",
        "file_fsyncs": 1,
        "directory_fsyncs": 1,
    }


def _generated_global_revision(index_id: str) -> dict[str, object]:
    raw = f"generated-{index_id.casefold()}-revision-v1"
    raw_digest = _sha256(raw.encode("utf-8"))
    return {
        "index_id": index_id,
        "issuer_id": f"GENERATED_{index_id}_ISSUER",
        "source_host": f"{index_id.casefold().replace('_', '-')}.example.org",
        "revision_kind": "CATALOG_REVISION",
        "extraction_location": "generated.response.revision",
        "revision_raw_bytes": raw,
        "revision_raw_bytes_sha256": raw_digest,
        "extraction_rule_sha256": _sha256(f"extract:{index_id}".encode()),
        "request_profile_sha256": _sha256(f"request:{index_id}".encode()),
        "scope_evidence_sha256": _sha256(f"scope:{index_id}".encode()),
        "complete_registered_traversal_scope": True,
        "pre_traversal_revision_raw_bytes_sha256": raw_digest,
        "post_traversal_revision_raw_bytes_sha256": raw_digest,
    }


def _generated_snapshot(index_id: str) -> dict[str, object]:
    pages: list[dict[str, object]] = []
    for ordinal in range(2):
        request_id = _sha256(f"request:{index_id}:{ordinal}".encode())
        body = (
            b"\xffPOISON-CANDIDATE-SUBTREE-DO-NOT-PARSE"
            + index_id.encode("ascii")
            + str(ordinal).encode("ascii")
        )
        page: dict[str, object] = {
            "ordinal": ordinal,
            "request_identity_sha256": request_id,
            "redirect_transcript": [],
            "pagination_identity_sha256": _sha256(
                f"pagination:{index_id}:{ordinal}".encode()
            ),
            "response_body_bytes": len(body),
            "response_body_sha256": _sha256(body),
            "next_request_identity_sha256": None,
            "terminal_state": "TERMINAL" if ordinal == 1 else "CONTINUE",
        }
        pages.append(page)
    pages[0]["next_request_identity_sha256"] = pages[1][
        "request_identity_sha256"
    ]
    return {
        "complete": True,
        "pages": pages,
        "ledger_sha256": _sha256(canonical_json_bytes(pages)),
    }


def _generated_revision_bundle_object() -> dict[str, object]:
    profiles: list[dict[str, object]] = []
    for index_id in INDEX_IDS:
        if index_id in GLOBAL_REVISION_IDS:
            profiles.append(
                {
                    "index_id": index_id,
                    "mode": "SOURCE_GLOBAL_REVISION",
                    "source_global_revision": _generated_global_revision(index_id),
                    "opaque_complete_snapshot_replay": None,
                }
            )
        else:
            profiles.append(
                {
                    "index_id": index_id,
                    "mode": "OPAQUE_COMPLETE_SNAPSHOT_REPLAY",
                    "source_global_revision": None,
                    "opaque_complete_snapshot_replay": _generated_snapshot(index_id),
                }
            )
    return {
        "schema_name": "neurodecodekit.fresh_motor_source_admission.revision_bundle",
        "schema_version": SCHEMA_VERSION,
        "profiles": profiles,
    }


def _response_headers(body: bytes, now_epoch: int) -> tuple[tuple[str, str], ...]:
    date = format_datetime(datetime.fromtimestamp(now_epoch, tz=UTC), usegmt=True)
    return (
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body))),
        ("Content-Encoding", "identity"),
        ("Date", date),
        ("Age", "0"),
    )


def build_generated_fixture() -> dict[str, object]:
    """Build one deterministic five-index and two-response generated fixture."""

    revision_bundle = canonical_json_bytes(_generated_revision_bundle_object())
    authority_profile = _generated_authority_profile()
    profile = _generated_CI_profile()
    now_epoch = _positive_int(profile["now_epoch"])
    head_sha = _ascii_token(profile["head_sha"])
    run_body = canonical_json_bytes(
        {
            "id": 4001,
            "workflow_id": 3001,
            "run_attempt": 1,
            "head_sha": head_sha,
            "head_branch": "main",
            "event": "push",
            "status": "completed",
            "conclusion": "success",
            "repository": {"id": 1001, "owner": {"id": 2001}},
            "head_repository": {"id": 1001, "owner": {"id": 2001}},
            "unrelated_future_field": "ignored_after_strict_decode",
        }
    )
    jobs_body = canonical_json_bytes(
        {
            "total_count": 2,
            "jobs": [
                {
                    "id": 5001,
                    "name": "Base Python",
                    "run_id": 4001,
                    "run_attempt": 1,
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "id": 5002,
                    "name": "Optional Neuro Readers",
                    "run_id": 4001,
                    "run_attempt": 1,
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": "success",
                },
            ],
        }
    )
    marker_bytes = canonical_json_bytes(
        {
            "protocol_id": PROTOCOL_ID,
            "stage": "CI_W0",
            "execution_ordinal": 1,
            "generated": True,
        }
    )
    return {
        "authority_profile": authority_profile,
        "revision_bundle": revision_bundle,
        "ci_profile": profile,
        "run_response": InjectedResponse(
            request_identity_sha256=profile["run_request_identity_sha256"],
            status=200,
            headers=_response_headers(run_body, now_epoch),
            body=run_body,
        ),
        "jobs_response": InjectedResponse(
            request_identity_sha256=profile["jobs_request_identity_sha256"],
            status=200,
            headers=_response_headers(jobs_body, now_epoch),
            body=jobs_body,
        ),
        "marker_bytes": marker_bytes,
    }


def _run_acceptance_replay(temp_parent: Path, metrics: QualificationMetrics) -> dict[str, object]:
    fixture = build_generated_fixture()
    authority_profile = fixture["authority_profile"]
    revision_bundle = fixture["revision_bundle"]
    run_response = fixture["run_response"]
    jobs_response = fixture["jobs_response"]
    marker_bytes = fixture["marker_bytes"]
    assert isinstance(revision_bundle, bytes)
    assert isinstance(run_response, InjectedResponse)
    assert isinstance(jobs_response, InjectedResponse)
    assert isinstance(marker_bytes, bytes)
    authority = validate_generated_authority_profile(authority_profile)
    revision = validate_revision_bundle(revision_bundle)
    ci = validate_github_ci_evidence(
        _mapping(fixture["ci_profile"]), run_response, jobs_response, environ={}
    )
    marker_dir = temp_parent / f"replay-{metrics.marker_creates}"
    marker_dir.mkdir(mode=0o700)
    marker = create_consumed_marker(
        marker_dir, marker_bytes, expected_stage="CI_W0"
    )
    ordering = validate_execution_order(
        ("marker_durable", "CI_W0_success", "source_contact_started")
    )
    metrics.generated_input_bytes += (
        len(canonical_json_bytes(authority_profile))
        + len(revision_bundle)
        + len(run_response.body)
        + len(jobs_response.body)
        + len(marker_bytes)
    )
    metrics.response_envelopes += 2
    metrics.marker_creates += 1
    metrics.marker_file_fsyncs += 1
    metrics.marker_directory_fsyncs += 1
    metrics.temporary_generated_bytes += marker["bytes"]
    metrics.temporary_generated_files += 1
    return {
        "authority": authority,
        "revision": revision,
        "CI": ci,
        "marker": marker,
        "ordering": ordering,
    }


def _observe_refusal(
    expected_route: str,
    operation: Callable[[], object],
) -> dict[str, str]:
    try:
        operation()
    except FMSR1AdmissionRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError(
                f"expected {expected_route} but observed {exc.route}"
            ) from exc
        return {"route": exc.route, "status": "passed"}
    raise AssertionError(f"expected {expected_route} refusal")


def _bundle_mutation(
    fixture: Mapping[str, object],
    mutate: Callable[[dict[str, object]], None],
) -> None:
    payload = fixture["revision_bundle"]
    assert isinstance(payload, bytes)
    value = copy.deepcopy(_mapping(strict_json_loads(payload)))
    mutate(value)
    validate_revision_bundle(canonical_json_bytes(value))


def _ci_mutation(
    fixture: Mapping[str, object],
    *,
    profile_mutator: Callable[[dict[str, object]], None] | None = None,
    run_mutator: Callable[[dict[str, object]], None] | None = None,
    jobs_mutator: Callable[[dict[str, object]], None] | None = None,
    run_headers: tuple[tuple[str, str], ...] | None = None,
    jobs_headers: tuple[tuple[str, str], ...] | None = None,
    run_status: int = 200,
) -> None:
    profile = copy.deepcopy(dict(_mapping(fixture["ci_profile"])))
    original_run = fixture["run_response"]
    original_jobs = fixture["jobs_response"]
    assert isinstance(original_run, InjectedResponse)
    assert isinstance(original_jobs, InjectedResponse)
    run_value = copy.deepcopy(_mapping(strict_json_loads(original_run.body)))
    jobs_value = copy.deepcopy(_mapping(strict_json_loads(original_jobs.body)))
    if profile_mutator is not None:
        profile_mutator(profile)
    if run_mutator is not None:
        run_mutator(run_value)
    if jobs_mutator is not None:
        jobs_mutator(jobs_value)
    run_body = canonical_json_bytes(run_value)
    jobs_body = canonical_json_bytes(jobs_value)
    run_response = InjectedResponse(
        original_run.request_identity_sha256,
        run_status,
        run_headers
        if run_headers is not None
        else _response_headers(run_body, _positive_int(profile["now_epoch"])),
        run_body,
    )
    jobs_response = InjectedResponse(
        original_jobs.request_identity_sha256,
        200,
        jobs_headers
        if jobs_headers is not None
        else _response_headers(jobs_body, _positive_int(profile["now_epoch"])),
        jobs_body,
    )
    validate_github_ci_evidence(profile, run_response, jobs_response, environ={})


def _authority_observation(name: str, fixture: Mapping[str, object]) -> None:
    if name == "captured_real_response_fixture":
        run_response = fixture["run_response"]
        jobs_response = fixture["jobs_response"]
        assert isinstance(run_response, InjectedResponse)
        assert isinstance(jobs_response, InjectedResponse)
        validate_github_ci_evidence(
            _mapping(fixture["ci_profile"]),
            replace(run_response, provenance="CAPTURED_REAL_RESPONSE"),
            jobs_response,
            environ={},
        )
        return
    profile = copy.deepcopy(dict(_mapping(fixture["authority_profile"])))
    mutations: dict[str, tuple[str, object]] = {
        "contract_digest_drift": ("contract_sha256", "0" * 64),
        "unregistered_stage": ("stage", "R1_W_LIVE"),
        "saved_receipt_as_authority": ("saved_receipt_authority", True),
        "incomplete_live_profile": ("live_profile_state", "INCOMPLETE"),
    }
    if name not in mutations:
        raise AssertionError("unknown authority mutation")
    key, value = mutations[name]
    profile[key] = value
    validate_generated_authority_profile(profile)


def _enforce_resources(
    *,
    response_count: int = 2,
    input_bytes: int = 0,
    runtime_seconds: float = 0.0,
    peak_RSS_bytes: int = 1,
    report_bytes: int = 0,
    temporary_bytes: int = 0,
    temporary_files: int = 0,
    thread_values: Mapping[str, str] | None = None,
) -> None:
    threads = {key: "1" for key in THREAD_ENV_KEYS} if thread_values is None else thread_values
    if (
        response_count > 2
        or input_bytes > MAX_GENERATED_INPUT_BYTES
        or runtime_seconds < 0
        or runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_RSS_bytes <= 0
        or peak_RSS_bytes > MAX_PEAK_RSS_BYTES
        or report_bytes > MAX_REPORT_BYTES
        or temporary_bytes > MAX_TEMP_BYTES
        or temporary_files > MAX_TEMP_FILES
        or any(threads.get(key) != "1" for key in THREAD_ENV_KEYS)
    ):
        _refuse("RESOURCE_REFUSE", "resource contract differs")


def _assert_qualification_isolated(
    counters: Mapping[str, int], *, imported_network_module: bool = False
) -> None:
    if imported_network_module or set(counters) != set(OPERATION_COUNTER_KEYS):
        _refuse("QUALIFICATION_NETWORK_REFUSE", "network surface differs")
    if any(type(value) is not int or value != 0 for value in counters.values()):
        _refuse("QUALIFICATION_NETWORK_REFUSE", "forbidden operation observed")


def _route_for_mutation(contract: Mapping[str, object]) -> dict[str, str]:
    mutations = _mapping(contract.get("refusal_mutations"), "AUTHORITY_REFUSE")
    routes: dict[str, str] = {}
    for route, names_value in mutations.items():
        expected_route = "ORDER_REFUSE" if route == "marker_durability" else route
        if expected_route not in REFUSAL_ROUTES:
            _refuse("AUTHORITY_REFUSE", "registered refusal route differs")
        for name_value in _list(names_value, "AUTHORITY_REFUSE"):
            name = _ascii_token(name_value, "AUTHORITY_REFUSE")
            if name in routes:
                _refuse("AUTHORITY_REFUSE", "duplicate mutation name")
            routes[name] = expected_route
    if len(routes) != 82 or contract.get("refusal_mutation_count") != 82:
        _refuse("AUTHORITY_REFUSE", "mutation inventory differs")
    return routes


def _fixture_material_bytes(fixture: Mapping[str, object]) -> int:
    revision = fixture["revision_bundle"]
    run = fixture["run_response"]
    jobs = fixture["jobs_response"]
    marker = fixture["marker_bytes"]
    assert isinstance(revision, bytes)
    assert isinstance(run, InjectedResponse)
    assert isinstance(jobs, InjectedResponse)
    assert isinstance(marker, bytes)
    return (
        len(canonical_json_bytes(fixture["authority_profile"]))
        + len(revision)
        + len(run.body)
        + len(jobs.body)
        + len(marker)
        + len(canonical_json_bytes(fixture["ci_profile"]))
    )


def _raise_oserror(_descriptor: int) -> None:
    raise OSError("generated fsync failure")


def _snapshot_profile(value: dict[str, object], index: int = 1) -> dict[str, object]:
    profiles = value["profiles"]
    assert isinstance(profiles, list)
    profile = profiles[index]
    assert isinstance(profile, dict)
    snapshot = profile["opaque_complete_snapshot_replay"]
    assert isinstance(snapshot, dict)
    return snapshot


def _global_profile(value: dict[str, object], index: int = 0) -> dict[str, object]:
    profiles = value["profiles"]
    assert isinstance(profiles, list)
    profile = profiles[index]
    assert isinstance(profile, dict)
    revision = profile["source_global_revision"]
    assert isinstance(revision, dict)
    return revision


def _jobs(value: dict[str, object]) -> list[dict[str, object]]:
    jobs = value["jobs"]
    assert isinstance(jobs, list)
    return [dict(_mapping(row)) for row in jobs]


def _exercise_mutation(
    name: str,
    fixture: Mapping[str, object],
    temp_root: Path,
) -> None:
    if name in {
        "contract_digest_drift",
        "unregistered_stage",
        "saved_receipt_as_authority",
        "incomplete_live_profile",
        "captured_real_response_fixture",
    }:
        _authority_observation(name, fixture)
        return

    order_cases: dict[str, Callable[[], object]] = {
        "network_before_marker": lambda: validate_execution_order(
            ("CI_W0_success", "marker_durable", "source_contact_started")
        ),
        "existing_consumed_marker": lambda: validate_execution_order(
            ("marker_durable", "CI_W0_success", "source_contact_started"),
            marker_already_exists=True,
        ),
        "marker_after_CI": lambda: validate_execution_order(
            ("CI_W0_success", "marker_durable", "source_contact_started")
        ),
        "CI_W0_reused_as_CI_W1": lambda: validate_execution_order(
            ("marker_durable", "CI_W0_success", "source_contact_started"),
            reused_stage=True,
        ),
        "process_resume_from_receipt": lambda: validate_execution_order(
            ("marker_durable", "CI_W0_success", "source_contact_started"),
            resumed_from_receipt=True,
        ),
        "mutable_receipt_handoff": lambda: validate_execution_order(
            ("marker_durable", "CI_W0_success", "source_contact_started"),
            mutable_handoff=True,
        ),
        "source_contact_before_CI": lambda: validate_execution_order(
            ("marker_durable", "source_contact_started", "CI_W0_success")
        ),
        "post_CI_process_exit_resume": lambda: validate_execution_order(
            ("marker_durable", "CI_W0_success", "source_contact_started"),
            resumed_from_receipt=True,
        ),
    }
    if name in order_cases:
        order_cases[name]()
        return

    encoding_payloads = {
        "invalid_UTF8": b'{"x":"\xff"}\n',
        "UTF8_BOM": b"\xef\xbb\xbf{}\n",
        "NUL_byte": b'{"x":"\x00"}\n',
        "trailing_JSON": b"{}\n{}\n",
        "nonfinite_number": b'{"x":NaN}\n',
    }
    if name in encoding_payloads:
        strict_json_loads(encoding_payloads[name])
        return
    if name == "depth_or_container_cap":
        value: object = "leaf"
        for _ in range(MAX_JSON_DEPTH + 2):
            value = [value]
        strict_json_loads(canonical_json_bytes(value))
        return
    if name == "duplicate_root_key":
        strict_json_loads(b'{"x":1,"x":2}\n')
        return
    if name == "duplicate_nested_key":
        strict_json_loads(b'{"x":{"y":1,"y":2}}\n')
        return
    if name == "duplicate_index_id":
        def mutate(value: dict[str, object]) -> None:
            profiles = value["profiles"]
            assert isinstance(profiles, list)
            assert isinstance(profiles[1], dict)
            profiles[1]["index_id"] = "OPENNEURO_CRN"

        _bundle_mutation(fixture, mutate)
        return
    if name == "duplicate_job_id":
        _ci_mutation(
            fixture,
            profile_mutator=lambda profile: profile.__setitem__(
                "required_job_ids",
                {"Base Python": 5001, "Optional Neuro Readers": 5001},
            ),
        )
        return
    if name == "duplicate_singleton_header":
        run = fixture["run_response"]
        assert isinstance(run, InjectedResponse)
        _ci_mutation(fixture, run_headers=run.headers + (("Date", run.headers[3][1]),))
        return

    if name == "unknown_authority_field":
        _ci_mutation(
            fixture,
            profile_mutator=lambda profile: profile.__setitem__("authority_alias", True),
        )
        return
    if name == "missing_required_field":
        _ci_mutation(
            fixture,
            profile_mutator=lambda profile: profile.pop("workflow_id"),
        )
        return
    if name == "boolean_numeric_identity":
        _positive_int(True)
        return
    if name == "float_numeric_identity":
        _positive_int(1.0)
        return
    if name == "confusable_enum_or_job_name":
        _bundle_mutation(
            fixture,
            lambda value: _mapping(_list(value["profiles"])[0]).__setitem__(
                "mode", "SOURCE_GLOBAL_REVISIОN"
            ),
        )
        return
    if name == "mixed_mode_payload":
        def mutate_mixed(value: dict[str, object]) -> None:
            profile = _mapping(_list(value["profiles"])[0])
            profile["opaque_complete_snapshot_replay"] = _generated_snapshot(
                "OPENNEURO_CRN"
            )

        _bundle_mutation(fixture, mutate_mixed)
        return

    if name == "wrong_index_or_issuer":
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__(
                "issuer_id", "WRONG_GENERATED_ISSUER"
            ),
        )
        return
    if name == "wrong_request_profile_hash":
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__(
                "request_profile_sha256", "0" * 63 + "1"
            ),
        )
        return
    if name == "cross_source_evidence":
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__("index_id", "PHYSIONET"),
        )
        return
    if name == "ledger_identity_drift":
        _bundle_mutation(
            fixture,
            lambda value: _snapshot_profile(value).__setitem__(
                "ledger_sha256", "0" * 64
            ),
        )
        return

    if name in {
        "weak_ETag_surrogate",
        "Last_Modified_surrogate",
        "body_hash_or_schema_surrogate",
    }:
        surrogate = {
            "weak_ETag_surrogate": "ETag",
            "Last_Modified_surrogate": "Last-Modified",
            "body_hash_or_schema_surrogate": "BODY_SHA256",
        }[name]
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__("revision_kind", surrogate),
        )
        return
    if name == "partial_scope":
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__(
                "complete_registered_traversal_scope", False
            ),
        )
        return
    if name == "pre_post_revision_drift":
        _bundle_mutation(
            fixture,
            lambda value: _global_profile(value).__setitem__(
                "post_traversal_revision_raw_bytes_sha256", "0" * 64
            ),
        )
        return

    def snapshot_pages(value: dict[str, object]) -> list[dict[str, object]]:
        pages = _snapshot_profile(value)["pages"]
        assert isinstance(pages, list)
        return [dict(_mapping(page)) for page in pages]

    if name == "snapshot_page_gap":
        def mutate_gap(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[1]["ordinal"] = 2
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_gap)
        return
    if name == "snapshot_cycle_or_fork":
        def mutate_cycle(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[0]["next_request_identity_sha256"] = pages[0][
                "request_identity_sha256"
            ]
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_cycle)
        return
    if name == "snapshot_reordered_body_hash":
        def mutate_body(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[1]["response_body_sha256"] = pages[0]["response_body_sha256"]
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_body)
        return
    if name == "snapshot_redirect_omission":
        def mutate_redirect(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[0]["redirect_transcript"] = [{"ordinal": 0}]
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_redirect)
        return
    if name == "snapshot_pagination_conflict":
        def mutate_pagination(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[1]["pagination_identity_sha256"] = pages[0][
                "pagination_identity_sha256"
            ]
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_pagination)
        return
    if name == "snapshot_early_terminal":
        def mutate_early(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[0]["terminal_state"] = "TERMINAL"
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_early)
        return
    if name == "snapshot_terminal_with_next":
        def mutate_terminal(value: dict[str, object]) -> None:
            snapshot = _snapshot_profile(value)
            pages = snapshot_pages(value)
            pages[1]["next_request_identity_sha256"] = pages[0][
                "request_identity_sha256"
            ]
            snapshot["pages"] = pages

        _bundle_mutation(fixture, mutate_terminal)
        return

    if name == "proxy_or_custom_CA_environment":
        validate_transport_environment({"HTTPS_PROXY": "https://proxy.invalid"})
        return
    if name == "custom_SSL_context_or_system_proxy":
        validate_transport_environment({}, custom_SSL_context_supplied=True)
        return
    if name == "redirect_or_alternate_host_port":
        run = fixture["run_response"]
        jobs = fixture["jobs_response"]
        assert isinstance(run, InjectedResponse)
        assert isinstance(jobs, InjectedResponse)
        validate_github_ci_evidence(
            _mapping(fixture["ci_profile"]),
            replace(run, request_host="alternate.invalid"),
            jobs,
            environ={},
        )
        return
    if name == "credential_cookie_or_conditional_request":
        run = fixture["run_response"]
        jobs = fixture["jobs_response"]
        assert isinstance(run, InjectedResponse)
        assert isinstance(jobs, InjectedResponse)
        validate_github_ci_evidence(
            _mapping(fixture["ci_profile"]),
            replace(
                run,
                request_headers=run.request_headers
                + (("Authorization", "generated-secret"),),
            ),
            jobs,
            environ={},
        )
        return
    if name == "nonglobal_or_postconnect_peer":
        run = fixture["run_response"]
        jobs = fixture["jobs_response"]
        assert isinstance(run, InjectedResponse)
        assert isinstance(jobs, InjectedResponse)
        validate_github_ci_evidence(
            _mapping(fixture["ci_profile"]),
            replace(run, postconnect_peer_unchanged=False),
            jobs,
            environ={},
        )
        return
    if name == "cache_or_content_encoding":
        run = fixture["run_response"]
        assert isinstance(run, InjectedResponse)
        headers = tuple(
            (key, "gzip" if key.casefold() == "content-encoding" else value)
            for key, value in run.headers
        )
        _ci_mutation(fixture, run_headers=headers)
        return

    run_mutations: dict[str, Callable[[dict[str, object]], None]] = {
        "wrong_repository_or_owner_ID": lambda run: _mapping(
            run["repository"]
        ).__setitem__("id", 9999),
        "wrong_head_repository_or_owner_ID": lambda run: _mapping(
            run["head_repository"]
        ).__setitem__("id", 9999),
        "wrong_workflow_or_run_ID": lambda run: run.__setitem__("workflow_id", 9999),
        "wrong_head_SHA": lambda run: run.__setitem__("head_sha", "0" * 40),
        "wrong_event_or_branch": lambda run: run.__setitem__("event", "pull_request"),
        "wrong_attempt": lambda run: run.__setitem__("run_attempt", 2),
        "noncompleted_or_nonsuccess_run": lambda run: run.__setitem__(
            "conclusion", "failure"
        ),
    }
    if name in run_mutations:
        _ci_mutation(fixture, run_mutator=run_mutations[name])
        return
    if name == "stale_Date_or_nonzero_Age":
        run = fixture["run_response"]
        assert isinstance(run, InjectedResponse)
        headers = tuple(
            (key, "1" if key.casefold() == "age" else value)
            for key, value in run.headers
        )
        _ci_mutation(fixture, run_headers=headers)
        return
    if name == "wrong_API_media_or_version_profile":
        _ci_mutation(
            fixture,
            profile_mutator=lambda profile: profile.__setitem__(
                "api_version", "wrong-generated-api-version"
            ),
        )
        return

    if name == "job_total_count_or_pagination":
        _ci_mutation(
            fixture,
            jobs_mutator=lambda jobs: jobs.__setitem__("total_count", 3),
        )
        return
    if name == "missing_required_job":
        def remove_job(jobs: dict[str, object]) -> None:
            rows = _list(jobs["jobs"])
            jobs["jobs"] = rows[:1]
            jobs["total_count"] = 1

        _ci_mutation(fixture, jobs_mutator=remove_job)
        return
    if name == "duplicate_required_job_name":
        def duplicate_name(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[1]["name"] = "Base Python"
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=duplicate_name)
        return
    if name == "wrong_job_ID":
        def wrong_job_id(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[0]["id"] = 9999
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=wrong_job_id)
        return
    if name == "wrong_job_run_or_attempt":
        def wrong_job_run(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[0]["run_attempt"] = 2
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=wrong_job_run)
        return
    if name == "wrong_job_head_SHA":
        def wrong_job_sha(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[0]["head_sha"] = "0" * 40
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=wrong_job_sha)
        return
    if name == "skipped_or_nonsuccess_job":
        def skipped_job(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[0]["conclusion"] = "skipped"
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=skipped_job)
        return
    if name == "null_or_confusable_job_name":
        def null_job(jobs: dict[str, object]) -> None:
            rows = _jobs(jobs)
            rows[0]["name"] = None
            jobs["jobs"] = rows

        _ci_mutation(fixture, jobs_mutator=null_job)
        return

    resource_operations: dict[str, Callable[[], None]] = {
        "request_count_cap": lambda: _enforce_resources(response_count=3),
        "wire_or_decoded_byte_cap": lambda: _enforce_resources(
            input_bytes=MAX_GENERATED_INPUT_BYTES + 1
        ),
        "runtime_or_RSS_cap": lambda: _enforce_resources(
            runtime_seconds=MAX_RUNTIME_SECONDS + 1
        ),
        "generated_output_or_temp_disk_cap": lambda: _enforce_resources(
            report_bytes=MAX_REPORT_BYTES + 1
        ),
        "thread_worker_or_file_count_cap": lambda: _enforce_resources(
            thread_values={key: "2" for key in THREAD_ENV_KEYS}
        ),
    }
    if name in resource_operations:
        resource_operations[name]()
        return

    if name == "DNS_socket_TLS_HTTP_tripwire":
        counters = {key: 0 for key in OPERATION_COUNTER_KEYS}
        counters["DNS_calls"] = 1
        _assert_qualification_isolated(counters)
        return
    if name == "credential_environment_tripwire":
        counters = {key: 0 for key in OPERATION_COUNTER_KEYS}
        counters["credential_reads"] = 1
        _assert_qualification_isolated(counters)
        return
    if name == "default_opener_or_network_import_tripwire":
        _assert_qualification_isolated(
            {key: 0 for key in OPERATION_COUNTER_KEYS}, imported_network_module=True
        )
        return

    marker_bytes = fixture["marker_bytes"]
    assert isinstance(marker_bytes, bytes)
    marker_parent = temp_root / name
    if name == "marker_symlink_or_nonregular_parent":
        target = temp_root / f"{name}-target"
        target.mkdir()
        marker_parent.symlink_to(target, target_is_directory=True)
        create_consumed_marker(
            marker_parent, marker_bytes, expected_stage="CI_W0"
        )
        return
    marker_parent.mkdir()
    if name == "marker_create_flags_or_permissions":
        (marker_parent / "consumed.json").write_bytes(marker_bytes)
        create_consumed_marker(
            marker_parent, marker_bytes, expected_stage="CI_W0"
        )
        return
    if name == "marker_file_fsync_failure":
        create_consumed_marker(
            marker_parent,
            marker_bytes,
            expected_stage="CI_W0",
            file_fsync=_raise_oserror,
        )
        return
    if name == "marker_parent_fsync_failure":
        create_consumed_marker(
            marker_parent,
            marker_bytes,
            expected_stage="CI_W0",
            directory_fsync=_raise_oserror,
        )
        return
    if name == "marker_atomic_second_creator":
        create_consumed_marker(
            marker_parent, marker_bytes, expected_stage="CI_W0"
        )
        create_consumed_marker(
            marker_parent, marker_bytes, expected_stage="CI_W0"
        )
        return
    raise AssertionError(f"unimplemented registered mutation: {name}")


def run_refusal_matrix(
    repo_root: str | Path | None = None,
    *,
    temp_root: str | Path | None = None,
    metrics: QualificationMetrics | None = None,
) -> dict[str, object]:
    """Run all 82 generated mutation observations in frozen order."""

    contract = _load_contract(repo_root)
    routes = _route_for_mutation(contract)
    local_metrics = QualificationMetrics() if metrics is None else metrics
    if temp_root is None:
        with _qualification_temp_root("fmsr1-r1g-refusals-") as temporary:
            return run_refusal_matrix(
                repo_root,
                temp_root=temporary,
                metrics=local_metrics,
            )
    root = Path(temp_root)
    _assert_qualification_owned_directory(root)
    cases: list[dict[str, str]] = []
    for name, expected_route in routes.items():
        fixture = build_generated_fixture()
        local_metrics.generated_input_bytes += _fixture_material_bytes(fixture)
        observation = _observe_refusal(
            expected_route,
            lambda name=name, fixture=fixture: _exercise_mutation(name, fixture, root),
        )
        cases.append(
            {
                "mutation": name,
                "expected_route": expected_route,
                "observed_route": observation["route"],
                "status": observation["status"],
            }
        )
    return {
        "case_count": len(cases),
        "all_passed": all(row["status"] == "passed" for row in cases),
        "cases": cases,
        "distinct_routes": len({row["observed_route"] for row in cases}),
    }


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


def _validate_thread_environment(environ: Mapping[str, str]) -> None:
    if any(environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        _refuse("RESOURCE_REFUSE", "thread environment differs")


def _walk_public(value: object, *, parent_key: str | None = None) -> None:
    forbidden_keys = {
        "url",
        "path",
        "host",
        "credential",
        "cookie",
        "raw_body",
        "raw_headers",
        "candidate",
        "payload",
        "signal",
        "target",
        "prediction",
        "score",
    }
    if isinstance(value, Mapping):
        for key, child in value.items():
            folded = str(key).casefold()
            aggregate_counter = (
                parent_key == "operation_counters" and folded in OPERATION_COUNTER_KEYS
            )
            if not aggregate_counter and (folded in forbidden_keys or any(
                token in folded
                for token in ("credential", "cookie", "payload_url", "raw_response")
            )):
                _refuse("SCHEMA_REFUSE", "private or transport field escaped")
            if not aggregate_counter and "candidate_metadata" in folded:
                _refuse("SCHEMA_REFUSE", "candidate metadata escaped")
            _walk_public(child, parent_key=folded)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child, parent_key=parent_key)


def validate_public_report(report: Mapping[str, object]) -> None:
    """Validate the aggregate generated qualification report."""

    _exact_keys(
        report,
        {
            "schema_name",
            "schema_version",
            "protocol_id",
            "status",
            "green_registration",
            "qualification",
            "measurements",
            "operation_counters",
            "warnings",
            "unavailable",
            "claim_boundary",
        },
        "SCHEMA_REFUSE",
    )
    if (
        report.get("schema_name") != SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("protocol_id") != PROTOCOL_ID
        or report.get("status") != "passed_generated_only_zero_network"
    ):
        _refuse("SCHEMA_REFUSE", "public report identity differs")
    registration = _mapping(report.get("green_registration"))
    _exact_keys(
        registration,
        {
            "commit",
            "CI_run_id",
            "base_python_job_id",
            "optional_neuro_readers_job_id",
            "both_required_jobs_green",
        },
        "SCHEMA_REFUSE",
    )
    if (
        registration.get("commit") != GREEN_REGISTRATION_COMMIT
        or registration.get("CI_run_id") != GREEN_REGISTRATION_CI_RUN_ID
        or registration.get("base_python_job_id") != GREEN_REGISTRATION_BASE_JOB_ID
        or registration.get("optional_neuro_readers_job_id")
        != GREEN_REGISTRATION_OPTIONAL_JOB_ID
        or registration.get("both_required_jobs_green") is not True
    ):
        _refuse("AUTHORITY_REFUSE", "green registration evidence differs")
    qualification = _mapping(report.get("qualification"))
    _exact_keys(
        qualification,
        {
            "deterministic_replays",
            "replay_digest",
            "replay_digests_equal",
            "profile_count_per_replay",
            "global_revision_count_per_replay",
            "snapshot_count_per_replay",
            "CI_responses_per_replay",
            "legal_ordering_sequences_per_replay",
            "refusal_case_count",
            "distinct_refusal_routes",
            "all_refusals_passed",
            "refusals",
        },
        "SCHEMA_REFUSE",
    )
    if (
        qualification.get("deterministic_replays") != 2
        or qualification.get("profile_count_per_replay") != 5
        or qualification.get("global_revision_count_per_replay") != 2
        or qualification.get("snapshot_count_per_replay") != 3
        or qualification.get("CI_responses_per_replay") != 2
        or qualification.get("legal_ordering_sequences_per_replay") != 1
        or qualification.get("refusal_case_count") != 82
        or qualification.get("distinct_refusal_routes") != len(REFUSAL_ROUTES)
        or qualification.get("all_refusals_passed") is not True
        or qualification.get("replay_digests_equal") is not True
    ):
        _refuse("SCHEMA_REFUSE", "qualification summary differs")
    _digest(qualification.get("replay_digest"), "IDENTITY_REFUSE")
    expected_refusals = tuple(_route_for_mutation(_load_contract()).items())
    refusals = _list(qualification.get("refusals"))
    if len(refusals) != len(expected_refusals):
        _refuse("SCHEMA_REFUSE", "refusal inventory length differs")
    for row_value, (expected_name, expected_route) in zip(
        refusals, expected_refusals, strict=True
    ):
        row = _mapping(row_value)
        _exact_keys(
            row,
            {"mutation", "expected_route", "observed_route", "status"},
            "SCHEMA_REFUSE",
        )
        if row != {
            "mutation": expected_name,
            "expected_route": expected_route,
            "observed_route": expected_route,
            "status": "passed",
        }:
            _refuse("SCHEMA_REFUSE", "refusal route record differs")
    measurements = _mapping(report.get("measurements"))
    _exact_keys(
        measurements,
        {
            "generated_input_bytes",
            "generated_output_bytes",
            "temporary_generated_bytes",
            "temporary_generated_file_count",
            "accepted_response_envelopes",
            "marker_creates",
            "marker_file_fsyncs",
            "marker_directory_fsyncs",
            "runtime_seconds",
            "absolute_peak_RSS_bytes",
            "CPU_threads",
            "workers",
            "numerical_jobs",
            "producer_is_causal",
            "end_to_end_latency_measured",
        },
        "SCHEMA_REFUSE",
    )
    if (
        _nonnegative_int(measurements.get("generated_input_bytes"))
        > MAX_GENERATED_INPUT_BYTES
        or _nonnegative_int(measurements.get("generated_output_bytes"))
        > MAX_REPORT_BYTES
        or _nonnegative_int(measurements.get("temporary_generated_bytes"))
        > MAX_TEMP_BYTES
        or _nonnegative_int(measurements.get("temporary_generated_file_count"))
        > MAX_TEMP_FILES
        or measurements.get("CPU_threads") != 1
        or measurements.get("workers") != 1
        or measurements.get("numerical_jobs") != 1
        or measurements.get("accepted_response_envelopes") != 4
        or measurements.get("marker_creates") != 3
        or measurements.get("marker_file_fsyncs") != 3
        or measurements.get("marker_directory_fsyncs") != 3
        or measurements.get("producer_is_causal") is not None
        or measurements.get("end_to_end_latency_measured") is not False
    ):
        _refuse("RESOURCE_REFUSE", "measurement contract differs")
    runtime = measurements.get("runtime_seconds")
    peak_rss = measurements.get("absolute_peak_RSS_bytes")
    if (
        not isinstance(runtime, (int, float))
        or isinstance(runtime, bool)
        or not math.isfinite(runtime)
        or runtime < 0
        or runtime > MAX_RUNTIME_SECONDS
        or type(peak_rss) is not int
        or peak_rss <= 0
        or peak_rss > MAX_PEAK_RSS_BYTES
    ):
        _refuse("RESOURCE_REFUSE", "runtime or RSS measurement differs")
    counters = _mapping(report.get("operation_counters"))
    _assert_qualification_isolated(
        {str(key): value for key, value in counters.items()}  # type: ignore[arg-type]
    )
    if tuple(report.get("warnings", [])) != WARNINGS:
        _refuse("SCHEMA_REFUSE", "warning inventory differs")
    if tuple(report.get("unavailable", [])) != UNAVAILABLE_FIELDS:
        _refuse("SCHEMA_REFUSE", "unavailable inventory differs")
    if report.get("claim_boundary") != CLAIM_BOUNDARY:
        _refuse("SCHEMA_REFUSE", "claim boundary differs")
    _walk_public(report)
    encoded = canonical_json_bytes(report)
    if (
        len(encoded) > MAX_REPORT_BYTES
        or measurements.get("generated_output_bytes") != len(encoded)
    ):
        _refuse("RESOURCE_REFUSE", "aggregate report byte count differs")


def registered_plan(repo_root: str | Path | None = None) -> dict[str, object]:
    """Return the exact generated-only plan after registration verification."""

    contract = _load_contract(repo_root)
    routes = _route_for_mutation(contract)
    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    activation_path = root / ACTIVATION_RELATIVE_PATH
    try:
        activation_info = os.lstat(activation_path)
        activation_present = stat.S_ISREG(activation_info.st_mode) and not stat.S_ISLNK(
            activation_info.st_mode
        )
    except OSError:
        activation_present = False
    return {
        "schema_name": f"{SCHEMA_NAME}.plan",
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "generated_only_implementation_registered",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "generated_index_profiles": len(INDEX_IDS),
        "revision_modes": 2,
        "deterministic_replays": 2,
        "named_refusal_mutations": len(routes),
        "maximum_runtime_seconds": MAX_RUNTIME_SECONDS,
        "maximum_absolute_peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
        "maximum_generated_input_bytes": MAX_GENERATED_INPUT_BYTES,
        "maximum_report_bytes": MAX_REPORT_BYTES,
        "maximum_temporary_generated_bytes": MAX_TEMP_BYTES,
        "CPU_threads": 1,
        "workers": 1,
        "network_imports": [],
        "live_command_present": False,
        "implementation_activation_present": activation_present,
        "official_qualification_consumed": (
            root / OFFICIAL_QUALIFICATION_ROOT
        ).exists(),
        "network_or_real_source_authority": False,
        "scientific_claim_authority": False,
    }


def run_generated_qualification(
    repo_root: str | Path | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, object]:
    """Run the one bounded generated-only qualification when externally gated."""

    _load_contract(repo_root)
    _load_implementation_activation(repo_root)
    _validate_thread_environment(os.environ if environ is None else environ)
    started = clock()
    metrics = QualificationMetrics()
    with _official_qualification_root(repo_root) as (temp_root, attempt_marker):
        metrics.generated_input_bytes += int(attempt_marker["bytes"])
        metrics.marker_creates += 1
        metrics.marker_file_fsyncs += 1
        metrics.marker_directory_fsyncs += 1
        first = _run_acceptance_replay(temp_root, metrics)
        second = _run_acceptance_replay(temp_root, metrics)
        first_digest = _sha256(canonical_json_bytes(first))
        second_digest = _sha256(canonical_json_bytes(second))
        if first != second or first_digest != second_digest:
            _refuse("IDENTITY_REFUSE", "deterministic replay differs")
        refusal_matrix = run_refusal_matrix(
            repo_root, temp_root=temp_root, metrics=metrics
        )
        if refusal_matrix["all_passed"] is not True:
            raise AssertionError("generated refusal matrix differs")
        generated_files = [path for path in temp_root.rglob("*") if path.is_file()]
        metrics.temporary_generated_files = len(generated_files)
        metrics.temporary_generated_bytes = sum(path.stat().st_size for path in generated_files)
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    _enforce_resources(
        input_bytes=metrics.generated_input_bytes,
        runtime_seconds=runtime_seconds,
        peak_RSS_bytes=peak_rss_bytes,
        temporary_bytes=metrics.temporary_generated_bytes,
        temporary_files=metrics.temporary_generated_files,
        thread_values=os.environ if environ is None else environ,
    )
    _assert_qualification_isolated(metrics.operation_counters)
    report: dict[str, object] = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "passed_generated_only_zero_network",
        "green_registration": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_readers_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "qualification": {
            "deterministic_replays": 2,
            "replay_digest": first_digest,
            "replay_digests_equal": True,
            "profile_count_per_replay": 5,
            "global_revision_count_per_replay": 2,
            "snapshot_count_per_replay": 3,
            "CI_responses_per_replay": 2,
            "legal_ordering_sequences_per_replay": 1,
            "refusal_case_count": refusal_matrix["case_count"],
            "distinct_refusal_routes": refusal_matrix["distinct_routes"],
            "all_refusals_passed": refusal_matrix["all_passed"],
            "refusals": refusal_matrix["cases"],
        },
        "measurements": {
            "generated_input_bytes": metrics.generated_input_bytes,
            "generated_output_bytes": 0,
            "temporary_generated_bytes": metrics.temporary_generated_bytes,
            "temporary_generated_file_count": metrics.temporary_generated_files,
            "accepted_response_envelopes": metrics.response_envelopes,
            "marker_creates": metrics.marker_creates,
            "marker_file_fsyncs": metrics.marker_file_fsyncs,
            "marker_directory_fsyncs": metrics.marker_directory_fsyncs,
            "runtime_seconds": runtime_seconds,
            "absolute_peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "producer_is_causal": None,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": dict(metrics.operation_counters),
        "warnings": list(WARNINGS),
        "unavailable": list(UNAVAILABLE_FIELDS),
        "claim_boundary": dict(CLAIM_BOUNDARY),
    }
    for _ in range(8):
        encoded = canonical_json_bytes(report)
        if report["measurements"]["generated_output_bytes"] == len(encoded):  # type: ignore[index]
            break
        report["measurements"]["generated_output_bytes"] = len(encoded)  # type: ignore[index]
    else:
        _refuse("RESOURCE_REFUSE", "report size did not stabilize")
    validate_public_report(report)
    return report
