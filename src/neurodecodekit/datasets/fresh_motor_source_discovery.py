"""Bounded metadata-only discovery for the FMSR1 fresh motor source lane."""

from __future__ import annotations

import hashlib
import io
import ipaddress
import json
import os
import resource
import socket
import stat
import subprocess
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from email.message import Message
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

SCHEMA_NAME = "neurodecodekit.fresh_motor_source_discovery"
SCHEMA_VERSION = "0.1.0"
PROTOCOL_ID = "FMSR1-DISCOVERY-M0-G1"

GREEN_DECISION_COMMIT = "b66a3a14c644e828eaffc5bd96a8251e6306d6e3"
GREEN_DECISION_CI_RUN_ID = 33_333_549_395
GREEN_DECISION_BASE_JOB_ID = 99_316_322_973
GREEN_DECISION_OPTIONAL_JOB_ID = 99_316_322_922
DECISION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_discovery_authorization_decision.v0.json"
)
DECISION_SHA256 = "e6fcd319856bbd43476bdcb2d8ba6f7b93317a34ce2d525d667c8175570c6d49"
CONTRACT_RELATIVE_PATH = Path("registries/fresh_motor_source_research_contract.v1.json")
CONTRACT_SHA256 = "9667b31282d7e5c852fc3de1b6fe07692952ec5720b79a0ba7c31345ccfbc8cb"
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_discovery_implementation.v0.json"
)
IMPLEMENTATION_PROOF_RELATIVE_PATH = Path(
    "registries/fresh_motor_source_discovery_implementation_proof.v0.json"
)

EXACT_QUERIES = (
    '"motor imagery" EEG EOG EMG',
    '"movement intention" EEG EOG EMG',
    '"motor execution" EEG EOG EMG',
    '"hand movement" EEG EOG EMG',
)
EXCLUDED_SOURCE_IDS = frozenset(
    {
        "BNCI-2014-001__NEMAR-nm000139",
        "DREYER-DATASET-A__NEMAR-nm000250",
        "OFNER-2017__NEMAR-nm000173",
        "IACKD__OPENNEURO-ds006840",
        "PHYSIONET-EEGMMIDB",
        "SPANISHBCBL-S7-S20-S21-S24-S25",
    }
)
MAX_REQUESTS = 128
MAX_WIRE_BYTES = 32 * 1024**2
MAX_DECODED_BYTES = 32 * 1024**2
MAX_RETAINED_BYTES = 8 * 1024**2
MAX_RUNTIME_SECONDS = 300.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_TIMEOUT_SECONDS = 30.0
MAX_REDIRECTS = 3
MAX_SELECTED_PAYLOAD_BYTES = 12 * 1024**3
MAX_PAGE_BYTES = 8 * 1024**2
READ_CHUNK_BYTES = 64 * 1024
USER_AGENT = "NeuroDecodeKit-FMSR1Discovery/0.1"
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
REDIRECT_STATUSES = frozenset({301, 302, 303, 307, 308})
TARGET_LIKE_KEYS = frozenset(
    {
        "answer",
        "ground_truth",
        "intended_text",
        "label",
        "outcome",
        "participant_outcome",
        "prediction",
        "probability",
        "reference_text",
        "response",
        "score",
        "sentence",
        "target",
        "targets",
        "trial_target",
    }
)
FORBIDDEN_RETAINED_KEYS = frozenset(
    {
        "archive_url",
        "download_url",
        "file_url",
        "member_url",
        "payload_url",
        "presigned_url",
        "raw_body",
        "raw_headers",
        "signal",
        "targets",
    }
)
RETAINED_CANDIDATE_FIELDS = frozenset(
    {
        "official_index_id",
        "packet_bound_index_revision",
        "query_or_category_id",
        "pagination_identity",
        "ordered_redirect_transcript",
        "canonical_candidate_id",
        "immutable_source_identifier",
        "immutable_release_identifier",
        "official_title",
        "official_landing_URL",
        "motor_task_description",
        "declared_sensor_modalities_and_roles",
        "declared_complete_participant_count",
        "declared_named_channel_and_geometry_availability",
        "declared_reference_sampling_event_and_target_semantics_availability",
        "declared_motor_classes",
        "payload_license_identifier",
        "declared_member_manifest_availability",
        "declared_complete_selected_payload_bytes",
        "documented_format_and_reader",
        "deterministic_sort_fields",
        "route",
        "exclusion_reason",
        "source_field_provenance",
    }
)
SORT_FIELDS = (
    "complete_participant_count",
    "bilateral_EMG_coverage_boolean",
    "kinematic_coverage_boolean",
    "independent_laboratory_device_participant_component_count",
    "minimum_trials_per_participant",
    "storage_headroom_bytes",
)
SUCCESS_ROUTE = "ELIGIBLE_FOR_METADATA_RESEARCH"
NO_SOURCE_ROUTE = "NO_QUALIFYING_SOURCE"
CAP_PARK_ROUTE = "DISCOVERY_CAP_PARK"
FAILURE_ROUTES = frozenset(
    {
        CAP_PARK_ROUTE,
        "UNREGISTERED_ENDPOINT_REFUSE",
        "UNREGISTERED_METHOD_REFUSE",
        "OFF_ALLOWLIST_REDIRECT_REFUSE",
        "REDIRECT_METHOD_REWRITE_REFUSE",
        "PAGINATION_CYCLE_REFUSE",
        "DUPLICATE_PAGE_REFUSE",
        "TRUNCATED_RESPONSE_REFUSE",
        "UNSUPPORTED_CONTENT_ENCODING_REFUSE",
        "RESPONSE_CAP_REFUSE",
        "RETAINED_FIELD_REFUSE",
        "MALFORMED_RESPONSE_REFUSE",
        "RESOURCE_CAP_REFUSE",
        "AUTHORITY_REFUSE",
    }
)


class FreshMotorDiscoveryRefusal(RuntimeError):
    """Fail closed with one registered aggregate-safe route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown FMSR1 discovery refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class IndexSpec:
    index_id: str
    endpoint: str
    method: str
    query_parameter: str | None
    traversal_mode: str
    parser_kind: str
    allowed_hosts: tuple[str, ...]
    profile_revision: str
    packet_bound_official_revision: str | None


INDEX_SPECS = (
    IndexSpec(
        "OPENNEURO",
        "https://openneuro.org/crn/graphql",
        "POST",
        None,
        "four_exact_queries",
        "json",
        ("openneuro.org",),
        "openneuro_crn_graphql_public_profile_2026-08-30",
        None,
    ),
    IndexSpec(
        "NEMAR",
        "https://nemar.org/search",
        "GET",
        "q",
        "four_exact_queries",
        "html_or_json",
        ("nemar.org", "www.nemar.org"),
        "nemar_public_search_profile_2026-08-30",
        None,
    ),
    IndexSpec(
        "PHYSIONET",
        "https://physionet.org/search/",
        "GET",
        "q",
        "four_exact_queries",
        "html_or_json",
        ("physionet.org", "www.physionet.org"),
        "physionet_public_search_profile_2026-08-30",
        None,
    ),
    IndexSpec(
        "GIGADB",
        "https://gigadb.org/search/new",
        "GET",
        "keyword",
        "four_exact_queries",
        "html_or_json",
        ("gigadb.org", "www.gigadb.org"),
        "gigadb_public_search_profile_2026-08-30",
        None,
    ),
    IndexSpec(
        "BNCI_HORIZON_2020",
        "https://bnci-horizon-2020.eu/database/data-sets",
        "GET",
        None,
        "complete_motor_EEG_category",
        "html_or_json",
        ("bnci-horizon-2020.eu", "www.bnci-horizon-2020.eu"),
        "bnci_horizon_2020_dataset_catalogue_profile_2026-08-30",
        None,
    ),
)
PAGINATION_QUERY_KEYS = {
    "OPENNEURO": frozenset(),
    "NEMAR": frozenset({"q", "page", "cursor", "offset", "limit"}),
    "PHYSIONET": frozenset({"q", "page", "cursor", "offset"}),
    "GIGADB": frozenset({"keyword", "page", "cursor", "offset"}),
    "BNCI_HORIZON_2020": frozenset({"page", "cursor", "offset"}),
}
SENSITIVE_QUERY_TOKENS = frozenset(
    {"auth", "credential", "download", "file", "key", "path", "signature", "token"}
)


@dataclass(frozen=True, slots=True)
class PlannedRequest:
    index_id: str
    query_or_category_id: str
    url: str
    method: str
    body: bytes | None
    page_identity: str


@dataclass(frozen=True, slots=True)
class ParsedPage:
    revision: str
    pagination_identity: str
    candidates: tuple[Mapping[str, Any], ...]
    next_url: str | None
    next_body: bytes | None


@dataclass(slots=True)
class AccessLedger:
    values: dict[str, int] = field(
        default_factory=lambda: {
            "planned_root_requests": 0,
            "request_attempts": 0,
            "redirect_hops": 0,
            "mock_HTTP_calls": 0,
            "real_network_requests": 0,
            "wire_body_bytes": 0,
            "decoded_body_bytes": 0,
            "body_read_calls": 0,
            "response_closes": 0,
            "pages_parsed": 0,
            "candidate_hits": 0,
            "canonical_candidates": 0,
            "selected_candidates": 0,
            "payload_or_header_reads": 0,
            "signal_event_annotation_target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scores": 0,
            "provider_calls": 0,
            "stream_device_or_hardware_runs": 0,
            "operations_on_other_projects": 0,
            "cleanup_or_deletion_operations": 0,
            "retries": 0,
            "reruns": 0,
            "scientific_claim_upgrades": 0,
        }
    )

    def increment(self, key: str, amount: int = 1) -> None:
        if key not in self.values or amount < 0:
            raise ValueError("invalid access-ledger update")
        self.values[key] += amount


@dataclass(frozen=True, slots=True)
class GreenImplementationEvidence:
    implementation_commit: str
    implementation_registry_sha256: str
    implementation_proof_commit: str
    implementation_proof_sha256: str
    CI_run_id: int
    base_python_job_id: int
    optional_neuro_readers_job_id: int
    execution_ordinal: int = 1


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


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON number")


def _strict_json(payload: bytes) -> Any:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ValueError("JSON encoding differs")
    return json.loads(
        payload.decode("utf-8", errors="strict"),
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )


def _read_exact_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    try:
        observed = os.lstat(path)
        if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
            raise OSError("tracked object type differs")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            payload = os.read(descriptor, 2 * 1024**2 + 1)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal("AUTHORITY_REFUSE", "tracked proof unavailable") from exc
    if len(payload) > 2 * 1024**2 or _sha256(payload) != expected_sha256:
        raise FreshMotorDiscoveryRefusal("AUTHORITY_REFUSE", "tracked proof identity differs")
    try:
        value = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise FreshMotorDiscoveryRefusal("AUTHORITY_REFUSE", "tracked proof JSON differs") from exc
    if not isinstance(value, dict):
        raise FreshMotorDiscoveryRefusal("AUTHORITY_REFUSE", "tracked proof root differs")
    return value


def load_green_decision(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    decision = _read_exact_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    contract = _read_exact_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    green = decision.get("green_request_and_proof", {})
    authority = decision.get("authorization_after_decision_green", {})
    if (
        decision.get("decision_id") != "FMSR1-DISCOVERY-M0-D0"
        or green.get("both_required_jobs_green") is not True
        or authority.get("implement_additive_standard_library_discovery_system") is not True
        or authority.get("run_generated_fixture_and_mock_network_qualification") is not True
        or authority.get("payload_URL_archive_range_member_or_header_access") is not False
        or authority.get("model_checkpoint_training_inference_prediction_or_score") is not False
        or contract.get("protocol_id") != "FMSR1-v1"
        or tuple(
            row.get("id") for row in contract["frozen_discovery_universe"]["official_indexes"]
        )
        != tuple(spec.index_id for spec in INDEX_SPECS)
        or tuple(contract["frozen_discovery_universe"]["exact_text_queries"])
        != EXACT_QUERIES
    ):
        raise FreshMotorDiscoveryRefusal("AUTHORITY_REFUSE", "authorization proof differs")
    return decision


def _ascii_trim(value: str) -> str:
    return value.strip(" \t\r\n\f\v")


def _canonical_component(value: Any) -> str:
    if not isinstance(value, str):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "canonical identity component is not text"
        )
    normalized = _ascii_trim(unicodedata.normalize("NFKC", value))
    if not normalized or "::" in normalized:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "canonical identity is incomplete or ambiguous"
        )
    return normalized


def canonical_candidate_id(index_id: str, source_id: str, release_id: str) -> str:
    parts = [_canonical_component(value) for value in (index_id, source_id, release_id)]
    return "::".join(parts)


def _normalized_key(value: Any) -> str:
    return unicodedata.normalize("NFKC", str(value)).casefold()


def _assert_target_free(value: Any, path: tuple[str, ...] = ()) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = _normalized_key(key)
            child_path = (*path, normalized)
            allowed_semantics_flag = child_path[-2:] == (
                "declared_reference_sampling_event_and_target_semantics_availability",
                "targets",
            ) and child is True
            if normalized in TARGET_LIKE_KEYS and not allowed_semantics_flag:
                raise FreshMotorDiscoveryRefusal(
                    "RETAINED_FIELD_REFUSE", "target-like metadata field encountered"
                )
            _assert_target_free(child, child_path)
    elif isinstance(value, list):
        for child in value:
            _assert_target_free(child, path)


def _assert_no_forbidden_retained_fields(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = _normalized_key(key)
            if normalized in FORBIDDEN_RETAINED_KEYS - {"targets"}:
                raise FreshMotorDiscoveryRefusal(
                    "RETAINED_FIELD_REFUSE", "payload-like retained field encountered"
                )
            _assert_no_forbidden_retained_fields(child)
    elif isinstance(value, list):
        for child in value:
            _assert_no_forbidden_retained_fields(child)


def _explicit_true(value: Any) -> bool:
    return value is True


def _is_excluded_consumed_source(candidate: Mapping[str, Any]) -> bool:
    index_id = _string_or_empty(candidate.get("official_index_id")).casefold()
    source_id = _string_or_empty(candidate.get("immutable_source_identifier")).casefold()
    title = _string_or_empty(candidate.get("official_title")).casefold()
    candidate_id = _string_or_empty(candidate.get("canonical_candidate_id")).casefold()
    excluded_ids = {value.casefold() for value in EXCLUDED_SOURCE_IDS}
    if source_id in excluded_ids or candidate_id in excluded_ids:
        return True
    exact_index_sources = {
        ("nemar", "nm000139"),
        ("nemar", "nm000250"),
        ("nemar", "nm000173"),
        ("openneuro", "ds006840"),
        ("bnci_horizon_2020", "001-2014"),
        ("bnci_horizon_2020", "2014-001"),
        ("bnci_horizon_2020", "bnci-2014-001"),
    }
    if (index_id, source_id) in exact_index_sources:
        return True
    combined = f"{source_id} {title} {candidate_id}"
    return (
        index_id == "physionet" and "eegmmidb" in combined
    ) or "spanishbcbl" in combined


def evaluate_candidate(candidate: Mapping[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    candidate_id = str(candidate.get("canonical_candidate_id", ""))
    provenance = candidate.get("source_field_provenance")
    roles = candidate.get("declared_sensor_modalities_and_roles")
    semantics = candidate.get(
        "declared_reference_sampling_event_and_target_semantics_availability"
    )
    manifest = candidate.get("declared_member_manifest_availability")
    documented = candidate.get("documented_format_and_reader")
    sort_fields = candidate.get("deterministic_sort_fields")
    motor_classes = candidate.get("declared_motor_classes")
    participant_count = candidate.get("declared_complete_participant_count")
    selected_bytes = candidate.get("declared_complete_selected_payload_bytes")

    if not candidate_id:
        reasons.append("canonical_candidate_id_complete")
    if _is_excluded_consumed_source(candidate):
        reasons.append("source_not_in_excluded_consumed_source_ids")
    if not _ascii_trim(str(candidate.get("motor_task_description", ""))):
        reasons.append("official_motor_task_description_present")
    if not isinstance(roles, list) or "raw_synchronized_EEG" not in roles:
        reasons.append("raw_synchronized_EEG_explicit")
    if not isinstance(roles, list) or "recorded_EOG" not in roles:
        reasons.append("recorded_EOG_explicit")
    if not isinstance(roles, list) or "task_relevant_EMG_all_named_effectors" not in roles:
        reasons.append("task_relevant_EMG_for_every_named_effector_explicit")
    if not isinstance(participant_count, int) or isinstance(participant_count, bool) or participant_count < 10:
        reasons.append("complete_participant_count_at_least_10")
    geometry = candidate.get("declared_named_channel_and_geometry_availability")
    geometry_fields = {
        "named_EEG_channels",
        "geometry",
        "posterior_comparator_constructible",
    }
    if (
        not isinstance(geometry, dict)
        or set(geometry) != geometry_fields
        or not all(_explicit_true(geometry.get(key)) for key in geometry_fields)
    ):
        reasons.append("named_EEG_channels_and_geometry_availability_explicit")
    semantics_true_fields = {
        "reference",
        "sampling",
        "events",
        "targets",
        "decision_semantics",
    }
    if (
        not isinstance(semantics, dict)
        or set(semantics) != semantics_true_fields | {"cue_identity_may_equal_target"}
        or not all(_explicit_true(semantics.get(key)) for key in semantics_true_fields)
        or semantics.get("cue_identity_may_equal_target") is not False
    ):
        reasons.append("reference_sampling_event_and_target_semantics_availability_explicit")
    if (
        not isinstance(motor_classes, list)
        or not all(isinstance(value, str) and _ascii_trim(value) for value in motor_classes)
        or len({_ascii_trim(value) for value in motor_classes}) < 2
    ):
        reasons.append("at_least_two_noncue_motor_classes_explicit")
    if not _ascii_trim(str(candidate.get("immutable_release_identifier", ""))):
        reasons.append("immutable_official_release_explicit")
    if not _ascii_trim(str(candidate.get("payload_license_identifier", ""))):
        reasons.append("reusable_payload_license_identifier_explicit")
    manifest_fields = {"complete", "sizes", "sha256"}
    if (
        not isinstance(manifest, dict)
        or set(manifest) != manifest_fields
        or not all(_explicit_true(manifest.get(key)) for key in manifest_fields)
    ):
        reasons.append("complete_cohort_member_sizes_and_hashes_obtainable_without_payload_read")
    if (
        not isinstance(selected_bytes, int)
        or isinstance(selected_bytes, bool)
        or selected_bytes < 0
        or selected_bytes > MAX_SELECTED_PAYLOAD_BYTES
    ):
        reasons.append("declared_complete_selected_payload_bytes_at_most_12884901888")
    if (
        not isinstance(documented, dict)
        or set(documented) != {"format", "reader"}
        or not all(
            isinstance(documented.get(key), str) and _ascii_trim(documented[key])
            for key in ("format", "reader")
        )
    ):
        reasons.append("documented_public_format_and_reader_explicit")
    if not isinstance(sort_fields, dict) or set(sort_fields) != set(SORT_FIELDS):  # noqa: SIM114
        reasons.append("complete_values_for_every_deterministic_sort_field")
    elif (
        not isinstance(sort_fields["complete_participant_count"], int)
        or isinstance(sort_fields["complete_participant_count"], bool)
        or sort_fields["complete_participant_count"] != participant_count
        or not isinstance(sort_fields["bilateral_EMG_coverage_boolean"], bool)
        or not isinstance(sort_fields["kinematic_coverage_boolean"], bool)
        or not isinstance(
            sort_fields["independent_laboratory_device_participant_component_count"], int
        )
        or isinstance(
            sort_fields["independent_laboratory_device_participant_component_count"], bool
        )
        or sort_fields["independent_laboratory_device_participant_component_count"] < 0
        or not isinstance(sort_fields["minimum_trials_per_participant"], int)
        or isinstance(sort_fields["minimum_trials_per_participant"], bool)
        or sort_fields["minimum_trials_per_participant"] <= 0
        or not isinstance(sort_fields["storage_headroom_bytes"], int)
        or isinstance(sort_fields["storage_headroom_bytes"], bool)
        or not isinstance(selected_bytes, int)
        or sort_fields["storage_headroom_bytes"]
        != MAX_SELECTED_PAYLOAD_BYTES - selected_bytes
    ):
        reasons.append("complete_values_for_every_deterministic_sort_field")
    if not isinstance(provenance, dict) or not provenance:
        reasons.append("source_field_provenance_complete")
    return (SUCCESS_ROUTE if not reasons else "PARK"), reasons


def _selection_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    fields = candidate["deterministic_sort_fields"]
    return (
        -int(fields["complete_participant_count"]),
        -int(bool(fields["bilateral_EMG_coverage_boolean"])),
        -int(bool(fields["kinematic_coverage_boolean"])),
        -int(fields["independent_laboratory_device_participant_component_count"]),
        -int(fields["minimum_trials_per_participant"]),
        -int(fields["storage_headroom_bytes"]),
        str(candidate["canonical_candidate_id"]),
    )


def _validate_retained_candidate(candidate: Mapping[str, Any]) -> None:
    landing = candidate.get("official_landing_URL")
    if landing is not None:
        if not isinstance(landing, str):
            raise FreshMotorDiscoveryRefusal(
                "RETAINED_FIELD_REFUSE", "landing URL is not text"
            )
        parsed = urlsplit(landing)
        lowered = landing.casefold()
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
            or any(
                marker in lowered
                for marker in (
                    "/download",
                    "presigned",
                    ".edf",
                    ".gdf",
                    ".mat",
                    ".zip",
                    "token=",
                    "signature=",
                )
            )
        ):
            raise FreshMotorDiscoveryRefusal(
                "RETAINED_FIELD_REFUSE", "landing URL resembles a payload surface"
            )
    provenance = candidate.get("source_field_provenance")
    context_fields = {
        "official_index_id",
        "packet_bound_index_revision",
        "query_or_category_id",
        "pagination_identity",
        "ordered_redirect_transcript",
        "canonical_candidate_id",
        "route",
        "exclusion_reason",
        "source_field_provenance",
    }
    expected_provenance_fields = set(candidate) - context_fields
    if provenance is not None and (
        not isinstance(provenance, dict)
        or set(provenance) != expected_provenance_fields
        or any(
            key not in RETAINED_CANDIDATE_FIELDS
            or not isinstance(value, str)
            or not _ascii_trim(value)
            or "://" in value
            or value.startswith(("/", "~"))
            or ".." in value
            for key, value in provenance.items()
        )
    ):
        raise FreshMotorDiscoveryRefusal(
            "RETAINED_FIELD_REFUSE", "source-field provenance differs"
        )


def route_candidates(
    candidates: Sequence[Mapping[str, Any]], *, ledger: AccessLedger
) -> dict[str, Any]:
    merged: dict[str, dict[str, Any]] = {}
    exclusions: list[dict[str, Any]] = []
    for raw in candidates:
        _assert_target_free(raw)
        _assert_no_forbidden_retained_fields(raw)
        unknown = set(raw) - RETAINED_CANDIDATE_FIELDS
        if unknown or set(raw) & FORBIDDEN_RETAINED_KEYS:
            raise FreshMotorDiscoveryRefusal(
                "RETAINED_FIELD_REFUSE", "candidate retained-field set differs"
            )
        _validate_retained_candidate(raw)
        try:
            index_id = _canonical_component(raw.get("official_index_id"))
            source_id = _canonical_component(raw.get("immutable_source_identifier"))
            release_id = _canonical_component(raw.get("immutable_release_identifier"))
            candidate_id = canonical_candidate_id(index_id, source_id, release_id)
        except FreshMotorDiscoveryRefusal:
            exclusions.append(
                {
                    "official_index_id": str(raw.get("official_index_id", "")),
                    "query_or_category_id": str(raw.get("query_or_category_id", "")),
                    "route": "PARK",
                    "exclusion_reason": ["canonical_candidate_id_complete"],
                }
            )
            continue
        candidate = dict(raw)
        supplied_candidate_id = candidate.get("canonical_candidate_id")
        if supplied_candidate_id is not None and supplied_candidate_id != candidate_id:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "supplied canonical identity conflicts"
            )
        candidate["official_index_id"] = index_id
        candidate["immutable_source_identifier"] = source_id
        candidate["immutable_release_identifier"] = release_id
        candidate["canonical_candidate_id"] = candidate_id
        prior = merged.get(candidate_id)
        if prior is None:
            merged[candidate_id] = candidate
            continue
        stable_fields = RETAINED_CANDIDATE_FIELDS - {
            "query_or_category_id",
            "pagination_identity",
            "ordered_redirect_transcript",
            "route",
            "exclusion_reason",
        }
        if any(prior.get(key) != candidate.get(key) for key in stable_fields):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "merged candidate evidence conflicts"
            )
        evidence = sorted(
            {
                *str(prior.get("query_or_category_id", "")).split("|"),
                *str(candidate.get("query_or_category_id", "")).split("|"),
            }
        )
        prior["query_or_category_id"] = "|".join(value for value in evidence if value)

    ledger.values["canonical_candidates"] = len(merged)
    eligible: list[dict[str, Any]] = []
    routed: list[dict[str, Any]] = []
    for candidate_id in sorted(merged):
        candidate = merged[candidate_id]
        route, reasons = evaluate_candidate(candidate)
        candidate["route"] = route
        candidate["exclusion_reason"] = reasons
        routed.append(candidate)
        if route == SUCCESS_ROUTE:
            eligible.append(candidate)
    eligible.sort(key=_selection_key)
    selected = eligible[:1]
    ledger.values["selected_candidates"] = len(selected)
    return {
        "route": SUCCESS_ROUTE if selected else NO_SOURCE_ROUTE,
        "candidate_hits": len(candidates),
        "canonical_candidates": len(merged),
        "eligible_candidates": len(eligible),
        "selected_candidates": selected,
        "routed_candidates": routed,
        "incomplete_identity_exclusions": exclusions,
    }


def _openneuro_body(query: str, cursor: str | None = None) -> bytes:
    value = {
        "operationName": "FMSR1DatasetSearch",
        "query": (
            "query FMSR1DatasetSearch($query:String!,$first:Int!,$after:String){"
            "datasets(query:$query,first:$first,after:$after){edges{node{id name}}"
            "pageInfo{hasNextPage endCursor}}}"
        ),
        "variables": {"after": cursor, "first": 100, "query": query},
    }
    return _canonical_json_bytes(value)


def build_plan() -> tuple[PlannedRequest, ...]:
    requests: list[PlannedRequest] = []
    for spec in INDEX_SPECS:
        if spec.traversal_mode == "complete_motor_EEG_category":
            requests.append(
                PlannedRequest(
                    index_id=spec.index_id,
                    query_or_category_id="complete_motor_EEG_category",
                    url=spec.endpoint,
                    method=spec.method,
                    body=None,
                    page_identity=f"{spec.index_id}:category:1",
                )
            )
            continue
        for query_index, query in enumerate(EXACT_QUERIES, start=1):
            if spec.method == "POST":
                url = spec.endpoint
                body = _openneuro_body(query)
            else:
                if spec.query_parameter is None:
                    raise AssertionError("GET search spec lacks a query parameter")
                query_string = urlencode(((spec.query_parameter, query),))
                url = f"{spec.endpoint}?{query_string}"
                body = None
            requests.append(
                PlannedRequest(
                    index_id=spec.index_id,
                    query_or_category_id=f"query_{query_index}",
                    url=url,
                    method=spec.method,
                    body=body,
                    page_identity=f"{spec.index_id}:query_{query_index}:1",
                )
            )
    if len(requests) != 17:
        raise AssertionError("frozen root-request cardinality differs")
    return tuple(requests)


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    if repo_root is not None:
        load_green_decision(repo_root)
    plan = build_plan()
    return {
        "schema_name": f"{SCHEMA_NAME}.plan",
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "green_decision_commit": GREEN_DECISION_COMMIT,
        "index_specs": [
            {
                "index_id": spec.index_id,
                "endpoint": spec.endpoint,
                "method": spec.method,
                "query_parameter": spec.query_parameter,
                "traversal_mode": spec.traversal_mode,
                "parser_kind": spec.parser_kind,
                "allowed_hosts": list(spec.allowed_hosts),
                "allowed_path": urlsplit(spec.endpoint).path or "/",
                "allowed_query_keys": sorted(PAGINATION_QUERY_KEYS[spec.index_id]),
                "profile_revision": spec.profile_revision,
                "packet_bound_official_revision": spec.packet_bound_official_revision,
            }
            for spec in INDEX_SPECS
        ],
        "exact_queries": list(EXACT_QUERIES),
        "root_request_count": len(plan),
        "request_identities": [
            {
                "index_id": request.index_id,
                "query_or_category_id": request.query_or_category_id,
                "url": request.url,
                "method": request.method,
                "body_sha256": _sha256(request.body or b""),
                "page_identity": request.page_identity,
            }
            for request in plan
        ],
        "caps": {
            "requests": MAX_REQUESTS,
            "wire_bytes": MAX_WIRE_BYTES,
            "decoded_bytes": MAX_DECODED_BYTES,
            "retained_bytes": MAX_RETAINED_BYTES,
            "runtime_seconds": MAX_RUNTIME_SECONDS,
            "peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
            "timeout_seconds": MAX_TIMEOUT_SECONDS,
            "redirects_per_request": MAX_REDIRECTS,
            "CPU_threads": 1,
            "workers": 1,
            "retries": 0,
            "reruns": 0,
        },
        "network_authorized_before_implementation_remote_green": False,
        "tracked_remote_green_implementation_proof_required_before_execution": True,
        "live_execution_armable_under_current_packet": False,
        "live_execution_blocker": "exact_official_index_revisions_not_packet_bound",
        "generated_fixture_envelope_allowed_on_live_surface": False,
        "payload_model_score_or_claim_authority": False,
    }


def _spec(index_id: str) -> IndexSpec:
    for spec in INDEX_SPECS:
        if spec.index_id == index_id:
            return spec
    raise FreshMotorDiscoveryRefusal("UNREGISTERED_ENDPOINT_REFUSE", "index differs")


def _canonical_url(url: str, *, spec: IndexSpec) -> str:
    parsed = urlsplit(url)
    expected_path = urlsplit(spec.endpoint).path or "/"
    if (
        parsed.scheme != "https"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.hostname not in spec.allowed_hosts
        or parsed.port not in (None, 443)
        or (parsed.path or "/") != expected_path
    ):
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "URL origin differs"
        )
    try:
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True, strict_parsing=True)
    except ValueError as exc:
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "URL query differs"
        ) from exc
    query_keys = [_normalized_key(key) for key, _value in query_pairs]
    if (
        len(query_keys) != len(set(query_keys))
        or any(key not in PAGINATION_QUERY_KEYS[spec.index_id] for key in query_keys)
        or any(
            key in SENSITIVE_QUERY_TOKENS
            or key.endswith(("_token", "_key", "_signature", "_credential"))
            for key in query_keys
        )
    ):
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "URL query is not allowlisted"
        )
    path = parsed.path or "/"
    return urlunsplit(("https", parsed.hostname or "", path, parsed.query, ""))


def _request_headers(request: urllib.request.Request) -> dict[str, str]:
    return {key.casefold(): value for key, value in request.header_items()}


def _validate_pagination_transition(
    root: PlannedRequest, current: PlannedRequest, parsed: ParsedPage
) -> None:
    if parsed.next_url is None:
        if parsed.next_body is not None:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "orphan pagination body"
            )
        return
    spec = _spec(root.index_id)
    next_url = _canonical_url(parsed.next_url, spec=spec)
    if root.method == "POST":
        if next_url != root.url or parsed.next_body is None or parsed.next_body == current.body:
            raise FreshMotorDiscoveryRefusal(
                "PAGINATION_CYCLE_REFUSE", "POST pagination transition differs"
            )
        return
    if parsed.next_body is not None:
        raise FreshMotorDiscoveryRefusal(
            "UNREGISTERED_METHOD_REFUSE", "GET pagination body present"
        )
    root_query = dict(parse_qsl(urlsplit(root.url).query, keep_blank_values=True))
    current_query = dict(parse_qsl(urlsplit(current.url).query, keep_blank_values=True))
    next_query = dict(parse_qsl(urlsplit(next_url).query, keep_blank_values=True))
    if spec.query_parameter is not None and (
        next_query.get(spec.query_parameter) != root_query.get(spec.query_parameter)
    ):
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "pagination changed the frozen query"
        )
    if next_query == current_query:
        raise FreshMotorDiscoveryRefusal(
            "PAGINATION_CYCLE_REFUSE", "pagination query did not advance"
        )


def _build_request(planned: PlannedRequest) -> urllib.request.Request:
    spec = _spec(planned.index_id)
    url = _canonical_url(planned.url, spec=spec)
    if planned.method != spec.method or planned.method not in {"GET", "POST"}:
        raise FreshMotorDiscoveryRefusal("UNREGISTERED_METHOD_REFUSE", "method differs")
    if planned.method == "GET" and planned.body is not None:
        raise FreshMotorDiscoveryRefusal("UNREGISTERED_METHOD_REFUSE", "GET body present")
    if planned.method == "POST" and not planned.body:
        raise FreshMotorDiscoveryRefusal("UNREGISTERED_METHOD_REFUSE", "POST body absent")
    headers = {
        "Accept": "application/json, text/html;q=0.9",
        "Accept-Encoding": "identity",
        "User-Agent": USER_AGENT,
    }
    if planned.method == "POST":
        headers["Content-Type"] = "application/json"
    return urllib.request.Request(
        url,
        data=planned.body,
        headers=headers,
        method=planned.method,
    )


def _validate_public_resolution(host: str, resolver: Callable[..., Any]) -> None:
    try:
        rows = resolver(host, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "host resolution failed"
        ) from exc
    addresses = []
    for row in rows:
        address = row[4][0]
        try:
            parsed = ipaddress.ip_address(address)
        except ValueError as exc:
            raise FreshMotorDiscoveryRefusal(
                "OFF_ALLOWLIST_REDIRECT_REFUSE", "resolved address is malformed"
            ) from exc
        addresses.append(parsed)
    if not addresses or any(
        not value.is_global
        or value.is_multicast
        or value.is_reserved
        or value.is_unspecified
        for value in addresses
    ):
        raise FreshMotorDiscoveryRefusal(
            "OFF_ALLOWLIST_REDIRECT_REFUSE", "resolved address is not public"
        )


def _header_values(headers: Any, name: str) -> list[str]:
    if hasattr(headers, "get_all"):
        return [str(value) for value in headers.get_all(name, [])]
    value = headers.get(name) if hasattr(headers, "get") else None
    return [] if value is None else [str(value)]


def _one_header(headers: Any, name: str, *, required: bool = False) -> str | None:
    values = _header_values(headers, name)
    if len(values) > 1 or (required and len(values) != 1):
        raise FreshMotorDiscoveryRefusal("MALFORMED_RESPONSE_REFUSE", "header differs")
    return values[0] if values else None


def _read_response_body(
    response: BinaryIO, *, ledger: AccessLedger, deadline: float | None = None
) -> bytes:
    headers = getattr(response, "headers", {})
    transfer_encodings = _header_values(headers, "Transfer-Encoding")
    if transfer_encodings:
        raise FreshMotorDiscoveryRefusal(
            "UNSUPPORTED_CONTENT_ENCODING_REFUSE", "transfer encoding is unsupported"
        )
    encodings = _header_values(headers, "Content-Encoding")
    if len(encodings) > 1 or (encodings and encodings[0].strip().casefold() not in {"", "identity"}):
        raise FreshMotorDiscoveryRefusal(
            "UNSUPPORTED_CONTENT_ENCODING_REFUSE", "content encoding differs"
        )
    declared = _one_header(headers, "Content-Length")
    if declared is not None:
        try:
            declared_bytes = int(declared)
        except ValueError as exc:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "content length is malformed"
            ) from exc
        if declared_bytes < 0 or declared_bytes > MAX_PAGE_BYTES:
            raise FreshMotorDiscoveryRefusal("RESPONSE_CAP_REFUSE", "page cap exceeded")
    chunks: list[bytes] = []
    page_bytes = 0
    while True:
        if deadline is not None and time.monotonic() >= deadline:
            raise FreshMotorDiscoveryRefusal(
                "RESOURCE_CAP_REFUSE", "monotonic execution deadline exceeded"
            )
        ledger.increment("body_read_calls")
        remaining = min(
            MAX_PAGE_BYTES - page_bytes,
            MAX_WIRE_BYTES - ledger.values["wire_body_bytes"],
            MAX_DECODED_BYTES - ledger.values["decoded_body_bytes"],
        )
        read_size = min(READ_CHUNK_BYTES, max(0, remaining) + 1)
        try:
            chunk = response.read(read_size)
        except OSError as exc:
            raise FreshMotorDiscoveryRefusal(
                "TRUNCATED_RESPONSE_REFUSE", "response read failed"
            ) from exc
        if not isinstance(chunk, bytes):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "response body is not bytes"
            )
        if not chunk:
            break
        page_bytes += len(chunk)
        ledger.increment("wire_body_bytes", len(chunk))
        ledger.increment("decoded_body_bytes", len(chunk))
        if (
            page_bytes > MAX_PAGE_BYTES
            or ledger.values["wire_body_bytes"] > MAX_WIRE_BYTES
            or ledger.values["decoded_body_bytes"] > MAX_DECODED_BYTES
        ):
            raise FreshMotorDiscoveryRefusal("RESPONSE_CAP_REFUSE", "body cap exceeded")
        chunks.append(chunk)
    body = b"".join(chunks)
    if declared is not None and len(body) != declared_bytes:
        raise FreshMotorDiscoveryRefusal(
            "TRUNCATED_RESPONSE_REFUSE", "content length does not match body"
        )
    return body


@dataclass(frozen=True, slots=True)
class FixtureExchange:
    method: str
    url: str
    body: bytes | None
    response: FixtureResponse


class FixtureResponse(io.BytesIO):
    def __init__(
        self,
        body: bytes,
        *,
        status: int = 200,
        url: str,
        headers: Sequence[tuple[str, str]] = (),
        nonbytes_body: bool = False,
    ) -> None:
        super().__init__(body)
        self.status = status
        self.code = status
        self._url = url
        self.headers = Message()
        for key, value in headers:
            self.headers.add_header(key, value)
        self.nonbytes_body = nonbytes_body
        self.close_calls = 0

    def geturl(self) -> str:
        return self._url

    def getcode(self) -> int:
        return self.status

    def read(self, size: int = -1) -> bytes:  # type: ignore[override]
        value = super().read(size)
        if self.nonbytes_body:
            return "not-bytes"  # type: ignore[return-value]
        return value

    def close(self) -> None:
        self.close_calls += 1
        super().close()


class FixtureOpener:
    def __init__(self, exchanges: Sequence[FixtureExchange]) -> None:
        self.exchanges = list(exchanges)
        self.calls = 0

    def __call__(self, request: urllib.request.Request, timeout: float) -> BinaryIO:
        self.calls += 1
        if not self.exchanges:
            raise FreshMotorDiscoveryRefusal(CAP_PARK_ROUTE, "unexpected mock request")
        expected = self.exchanges.pop(0)
        if (
            request.get_method() != expected.method
            or request.full_url != expected.url
            or request.data != expected.body
            or timeout <= 0
            or timeout > MAX_TIMEOUT_SECONDS
        ):
            raise FreshMotorDiscoveryRefusal(
                "UNREGISTERED_ENDPOINT_REFUSE", "mock request differs"
            )
        return expected.response

    def assert_consumed(self) -> None:
        if self.exchanges:
            raise FreshMotorDiscoveryRefusal(CAP_PARK_ROUTE, "mock responses remain")


def _mock_resolver(_host: str, _port: int, **_kwargs: Any) -> list[Any]:
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


def fetch_page(
    planned: PlannedRequest,
    *,
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    resolver: Callable[..., Any],
    ledger: AccessLedger,
    deadline: float | None = None,
) -> tuple[bytes, tuple[dict[str, Any], ...], Mapping[str, Any]]:
    """Read one generated fixture page; this API has no real-network mode."""

    if type(opener) is not FixtureOpener or resolver is not _mock_resolver:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "only the generated transport capability is available"
        )
    spec = _spec(planned.index_id)
    request = _build_request(planned)
    redirects: list[dict[str, Any]] = []
    current_method = planned.method
    current_body = planned.body
    for redirect_index in range(MAX_REDIRECTS + 1):
        if ledger.values["request_attempts"] >= MAX_REQUESTS:
            raise FreshMotorDiscoveryRefusal(CAP_PARK_ROUTE, "request cap reached")
        current_url = _canonical_url(request.full_url, spec=spec)
        host = urlsplit(current_url).hostname or ""
        ledger.increment("request_attempts")
        _validate_public_resolution(host, resolver)
        ledger.increment("mock_HTTP_calls")
        request_deadline = time.monotonic() + MAX_TIMEOUT_SECONDS
        if deadline is not None:
            request_deadline = min(request_deadline, deadline)
        timeout_seconds = request_deadline - time.monotonic()
        if timeout_seconds <= 0:
            raise FreshMotorDiscoveryRefusal(
                "RESOURCE_CAP_REFUSE", "monotonic request deadline exceeded"
            )
        try:
            response = opener(request, timeout_seconds)
        except (OSError, urllib.error.URLError) as exc:
            raise FreshMotorDiscoveryRefusal(CAP_PARK_ROUTE, "network open failed") from exc
        try:
            status = int(getattr(response, "status", response.getcode()))
            final_url = str(response.geturl())
            if final_url != current_url:
                raise FreshMotorDiscoveryRefusal(
                    "OFF_ALLOWLIST_REDIRECT_REFUSE", "automatic redirect detected"
                )
            if status in REDIRECT_STATUSES:
                if redirect_index >= MAX_REDIRECTS:
                    raise FreshMotorDiscoveryRefusal(
                        "OFF_ALLOWLIST_REDIRECT_REFUSE", "redirect cap exceeded"
                    )
                _read_response_body(
                    response, ledger=ledger, deadline=request_deadline
                )
                location = _one_header(getattr(response, "headers", {}), "Location", required=True)
                if location is None:
                    raise FreshMotorDiscoveryRefusal(
                        "OFF_ALLOWLIST_REDIRECT_REFUSE", "redirect location absent"
                    )
                if status == 303 or (status in {301, 302} and current_method == "POST"):
                    raise FreshMotorDiscoveryRefusal(
                        "REDIRECT_METHOD_REWRITE_REFUSE", "redirect would rewrite method"
                    )
                target = _canonical_url(urljoin(current_url, location), spec=spec)
                if urlsplit(target).query != urlsplit(current_url).query:
                    raise FreshMotorDiscoveryRefusal(
                        "OFF_ALLOWLIST_REDIRECT_REFUSE", "redirect changed the frozen query"
                    )
                redirects.append(
                    {
                        "status": status,
                        "from": current_url,
                        "to": target,
                        "method": current_method,
                    }
                )
                ledger.increment("redirect_hops")
                request = urllib.request.Request(
                    target,
                    data=current_body,
                    headers=dict(request.header_items()),
                    method=current_method,
                )
                continue
            if status != 200:
                body = _read_response_body(
                    response, ledger=ledger, deadline=request_deadline
                )
                raise FreshMotorDiscoveryRefusal(
                    CAP_PARK_ROUTE, f"terminal HTTP status {status} with {len(body)} bytes"
                )
            body = _read_response_body(
                response, ledger=ledger, deadline=request_deadline
            )
            raw_content_type = (
                _one_header(response.headers, "Content-Type") or ""
            ).casefold()
            content_type = raw_content_type.split(";", 1)[0].strip()
            if content_type not in {
                "application/json",
                "application/ld+json",
                "text/json",
                "text/html",
                "application/xhtml+xml",
            }:
                raise FreshMotorDiscoveryRefusal(
                    "MALFORMED_RESPONSE_REFUSE", "content type is unsupported"
                )
            revision_header = (
                _one_header(response.headers, "X-FMSR1-Index-Revision")
                or _one_header(response.headers, "ETag")
                or _one_header(response.headers, "Last-Modified")
            )
            if revision_header != spec.profile_revision:
                raise FreshMotorDiscoveryRefusal(
                    "MALFORMED_RESPONSE_REFUSE",
                    "generated index revision differs from its registered profile",
                )
            transport = {
                "terminal_url": current_url,
                "terminal_method": current_method,
                "terminal_status": status,
                "content_type": content_type,
                "packet_bound_index_revision": revision_header,
                "ordered_redirect_transcript": tuple(redirects),
                "wire_bytes": len(body),
                "decoded_bytes": len(body),
                "body_sha256": _sha256(body),
            }
            return body, tuple(redirects), transport
        finally:
            try:
                response.close()
            except OSError as exc:
                raise FreshMotorDiscoveryRefusal(
                    "MALFORMED_RESPONSE_REFUSE", "response close failed"
                ) from exc
            finally:
                ledger.increment("response_closes")
    raise AssertionError("redirect loop did not terminate")


class _HTMLMetadataParser(HTMLParser):
    """Extract only dataset landing links, pagination links, and JSON-LD."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.dataset_links: list[tuple[str, str]] = []
        self.next_links: list[str] = []
        self.json_ld_blocks: list[str] = []
        self._anchor_href: str | None = None
        self._anchor_text: list[str] = []
        self._json_ld = False
        self._json_ld_text: list[str] = []
        self.search_surface_seen = False
        self.pagination_seen = False
        self.terminal_pagination_seen = False
        self.visible_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        class_and_id = f"{values.get('class', '')} {values.get('id', '')}".casefold()
        if any(
            token in class_and_id
            for token in ("search-result", "dataset-list", "dataset-result", "datasets")
        ):
            self.search_surface_seen = True
        if any(token in class_and_id for token in ("pagination", "pager", "page-nav")):
            self.pagination_seen = True
        if "next" in class_and_id:
            self.pagination_seen = True
            if (
                "disabled" in class_and_id
                or values.get("aria-disabled", "").casefold() == "true"
            ):
                self.terminal_pagination_seen = True
        if tag.casefold() == "a":
            href = values.get("href", "")
            relations = {value.casefold() for value in values.get("rel", "").split()}
            if "next" in relations and href:
                self.next_links.append(href)
            self._anchor_href = href or None
            self._anchor_text = []
        elif (
            tag.casefold() == "script"
            and values.get("type", "").casefold() == "application/ld+json"
        ):
            self._json_ld = True
            self._json_ld_text = []

    def handle_data(self, data: str) -> None:
        if _ascii_trim(data):
            self.visible_text.append(data)
        if self._anchor_href is not None:
            self._anchor_text.append(data)
        if self._json_ld:
            self._json_ld_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "a" and self._anchor_href is not None:
            text = _ascii_trim(" ".join(self._anchor_text))
            href = self._anchor_href
            lowered = href.casefold()
            if text and any(token in lowered for token in ("dataset", "record", "study")):
                self.dataset_links.append((href, text))
            self._anchor_href = None
            self._anchor_text = []
        elif tag.casefold() == "script" and self._json_ld:
            self.json_ld_blocks.append("".join(self._json_ld_text))
            self._json_ld = False
            self._json_ld_text = []


def _empty_candidate(
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
    pagination_identity: str,
) -> dict[str, Any]:
    return {
        "official_index_id": planned.index_id,
        "packet_bound_index_revision": str(
            transport["packet_bound_index_revision"]
        ),
        "query_or_category_id": planned.query_or_category_id,
        "pagination_identity": pagination_identity,
        "ordered_redirect_transcript": list(
            transport["ordered_redirect_transcript"]
        ),
    }


def _string_or_empty(value: Any) -> str:
    return _ascii_trim(value) if isinstance(value, str) else ""


def _candidate_from_fixture(
    raw: Any,
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
    pagination_identity: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "fixture candidate is not an object"
        )
    _assert_target_free(raw)
    if set(raw) - RETAINED_CANDIDATE_FIELDS:
        raise FreshMotorDiscoveryRefusal(
            "RETAINED_FIELD_REFUSE", "fixture candidate field is not allowlisted"
        )
    candidate = dict(raw)
    expected = _empty_candidate(
        planned=planned,
        transport=transport,
        pagination_identity=pagination_identity,
    )
    for key, value in expected.items():
        supplied = candidate.get(key)
        if supplied is not None and supplied != value:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "fixture context binding differs"
            )
        candidate[key] = value
    return candidate


def _candidate_from_public_mapping(
    raw: Mapping[str, Any],
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
    pagination_identity: str,
) -> dict[str, Any]:
    """Map explicit public metadata without inferring any eligibility fact."""

    _assert_target_free(raw)
    candidate = _empty_candidate(
        planned=planned,
        transport=transport,
        pagination_identity=pagination_identity,
    )
    context_fields = set(candidate)
    for key in context_fields:
        if key in raw and raw[key] != candidate[key]:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "public candidate context conflicts"
            )
    explicit_fields = RETAINED_CANDIDATE_FIELDS - context_fields - {
        "route",
        "exclusion_reason",
    }
    for key in explicit_fields:
        if key in raw:
            candidate[key] = raw[key]
    source_id = ""
    for key in ("immutable_source_identifier", "dataset_id", "accession", "identifier", "id"):
        source_id = _string_or_empty(raw.get(key))
        if source_id:
            break
    release_id = ""
    for key in ("immutable_release_identifier", "release", "version", "revision"):
        release_id = _string_or_empty(raw.get(key))
        if release_id:
            break
    title = ""
    for key in ("official_title", "name", "title"):
        title = _string_or_empty(raw.get(key))
        if title:
            break
    landing = ""
    for key in ("official_landing_URL", "landing_url", "url"):
        landing = _string_or_empty(raw.get(key))
        if landing:
            break
    if source_id and "immutable_source_identifier" not in candidate:
        candidate["immutable_source_identifier"] = source_id
    if release_id and "immutable_release_identifier" not in candidate:
        candidate["immutable_release_identifier"] = release_id
    if title and "official_title" not in candidate:
        candidate["official_title"] = title
    if (
        landing
        and "official_landing_URL" not in candidate
        and not any(token in landing.casefold() for token in ("download", "archive", "file="))
    ):
        candidate["official_landing_URL"] = landing
    if "source_field_provenance" not in candidate:
        candidate["source_field_provenance"] = {
            key: "official_index_search_response"
            for key in (
                "immutable_source_identifier",
                "immutable_release_identifier",
                "official_title",
                "official_landing_URL",
            )
            if key in candidate
        }
    return candidate


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_mappings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_mappings(child)


def _looks_like_dataset_record(value: Mapping[str, Any]) -> bool:
    kind = value.get("@type") or value.get("type")
    if isinstance(kind, str) and kind.casefold() in {"dataset", "study"}:
        return True
    keys = {str(key).casefold() for key in value}
    return bool(keys & {"dataset_id", "accession"}) or (
        "id" in keys and bool(keys & {"name", "title"})
    )


def _graphql_records(value: Mapping[str, Any]) -> tuple[list[Mapping[str, Any]], str | None]:
    try:
        datasets = value["data"]["datasets"]
    except (KeyError, TypeError):
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "GraphQL dataset envelope is unavailable"
        )
    if not isinstance(datasets, dict) or not isinstance(datasets.get("edges"), list):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "GraphQL dataset envelope differs"
        )
    rows: list[Mapping[str, Any]] = []
    for edge in datasets["edges"]:
        if not isinstance(edge, dict) or not isinstance(edge.get("node"), dict):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "GraphQL dataset edge differs"
            )
        rows.append(edge["node"])
    page_info = datasets.get("pageInfo")
    if not isinstance(page_info, dict):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "GraphQL pageInfo differs"
        )
    has_next = page_info.get("hasNextPage")
    cursor = page_info.get("endCursor")
    if has_next is True and not _string_or_empty(cursor):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "GraphQL cursor is absent"
        )
    if has_next not in {True, False}:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "GraphQL pagination flag differs"
        )
    return rows, _string_or_empty(cursor) if has_next else None


def _generic_json_records(
    value: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], str | None]:
    container_key = next(
        (
            key
            for key in ("results", "datasets", "items")
            if isinstance(value.get(key), list)
        ),
        None,
    )
    if container_key is None:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "JSON result container is unavailable"
        )
    records = value[container_key]
    if not all(isinstance(row, dict) for row in records):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "JSON result row differs"
        )
    pagination = value.get("pagination")
    next_value: Any = value.get("next") if "next" in value else None
    pagination_explicit = "next" in value
    if pagination is not None:
        if not isinstance(pagination, dict):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "JSON pagination object differs"
            )
        if "next" in pagination:
            next_value = pagination["next"]
            pagination_explicit = True
        elif "has_next" in pagination:
            has_next = pagination["has_next"]
            if has_next is True:
                raise FreshMotorDiscoveryRefusal(
                    CAP_PARK_ROUTE, "JSON next-page identity is unavailable"
                )
            if has_next is not False:
                raise FreshMotorDiscoveryRefusal(
                    "MALFORMED_RESPONSE_REFUSE", "JSON pagination flag differs"
                )
            pagination_explicit = True
    if not pagination_explicit:
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "JSON pagination completeness is unavailable"
        )
    if next_value is not None and not isinstance(next_value, str):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "JSON next-page URL differs"
        )
    next_url = _ascii_trim(next_value) if isinstance(next_value, str) else None
    return list(records), next_url or None


def _parse_json_page(
    value: Any,
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
    allow_fixture_envelope: bool,
) -> ParsedPage:
    if not isinstance(value, dict):
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "JSON response root is not an object"
        )
    _assert_target_free(value)
    if "fmsr1_page" in value:
        if not allow_fixture_envelope:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "generated fixture envelope on live surface"
            )
        if set(value) != {"fmsr1_page"} or not isinstance(value["fmsr1_page"], dict):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "fixture page envelope differs"
            )
        page = value["fmsr1_page"]
        allowed = {"revision", "pagination_identity", "candidates", "next_url", "next_cursor"}
        if set(page) - allowed or not isinstance(page.get("candidates"), list):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "fixture page fields differ"
            )
        revision = _string_or_empty(page.get("revision"))
        pagination_identity = _string_or_empty(page.get("pagination_identity"))
        if not revision or not pagination_identity:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "fixture page identity is incomplete"
            )
        if revision != str(transport["packet_bound_index_revision"]):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "fixture revision differs"
            )
        candidates = tuple(
            _candidate_from_fixture(
                raw,
                planned=planned,
                transport=transport,
                pagination_identity=pagination_identity,
            )
            for raw in page["candidates"]
        )
        next_url = page.get("next_url")
        next_cursor = page.get("next_cursor")
        if next_url is not None and next_cursor is not None:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "multiple pagination continuations"
            )
        if next_url is not None and not isinstance(next_url, str):
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "next URL differs"
            )
        next_body = None
        if next_cursor is not None:
            if planned.index_id != "OPENNEURO" or not isinstance(next_cursor, str):
                raise FreshMotorDiscoveryRefusal(
                    "MALFORMED_RESPONSE_REFUSE", "cursor continuation differs"
                )
            query_index = int(planned.query_or_category_id.removeprefix("query_")) - 1
            next_body = _openneuro_body(EXACT_QUERIES[query_index], next_cursor)
            next_url = planned.url
        return ParsedPage(revision, pagination_identity, candidates, next_url, next_body)

    if planned.index_id == "OPENNEURO":
        if "errors" in value or "data" not in value:
            raise FreshMotorDiscoveryRefusal(
                CAP_PARK_ROUTE, "GraphQL response is incomplete"
            )
        records, cursor = _graphql_records(value)
        next_url_from_generic = None
    else:
        records, next_url_from_generic = _generic_json_records(value)
        cursor = None
    pagination_identity = f"{planned.page_identity}:{transport['body_sha256']}"
    candidates = tuple(
        _candidate_from_public_mapping(
            row,
            planned=planned,
            transport=transport,
            pagination_identity=pagination_identity,
        )
        for row in records
    )
    next_body = None
    next_url = None
    if cursor is not None:
        query_index = int(planned.query_or_category_id.removeprefix("query_")) - 1
        next_body = _openneuro_body(EXACT_QUERIES[query_index], cursor)
        next_url = planned.url
    elif next_url_from_generic is not None:
        next_url = next_url_from_generic
    return ParsedPage(
        str(transport["packet_bound_index_revision"]),
        pagination_identity,
        candidates,
        next_url,
        next_body,
    )


def _parse_html_page(
    body: bytes,
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
) -> ParsedPage:
    try:
        text = body.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "HTML encoding differs"
        ) from exc
    parser = _HTMLMetadataParser()
    try:
        parser.feed(text)
        parser.close()
    except (AssertionError, ValueError) as exc:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "HTML parsing failed"
        ) from exc
    pagination_identity = f"{planned.page_identity}:{transport['body_sha256']}"
    candidates: list[dict[str, Any]] = []
    for block in parser.json_ld_blocks:
        try:
            parsed = _strict_json(block.encode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "JSON-LD differs"
            ) from exc
        _assert_target_free(parsed)
        for row in _walk_mappings(parsed):
            if _looks_like_dataset_record(row):
                candidates.append(
                    _candidate_from_public_mapping(
                        row,
                        planned=planned,
                        transport=transport,
                        pagination_identity=pagination_identity,
                    )
                )
    if not candidates:
        spec = _spec(planned.index_id)
        for href, title in parser.dataset_links:
            landing = _canonical_url(urljoin(planned.url, href), spec=spec)
            source_id = Path(urlsplit(landing).path.rstrip("/")).name
            row = {"id": source_id, "name": title, "url": landing}
            candidates.append(
                _candidate_from_public_mapping(
                    row,
                    planned=planned,
                    transport=transport,
                    pagination_identity=pagination_identity,
                )
            )
    if len(parser.next_links) > 1:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "multiple next-page links"
        )
    visible = " ".join(parser.visible_text).casefold()
    explicit_no_results = any(
        marker in visible
        for marker in ("no results", "0 results", "no datasets found", "zero datasets")
    )
    if not candidates and not explicit_no_results:
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "HTML result completeness is unavailable"
        )
    if candidates and not parser.search_surface_seen:
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "HTML result surface is ambiguous"
        )
    if candidates and not parser.pagination_seen:
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "HTML pagination declaration is unavailable"
        )
    if parser.pagination_seen and not parser.next_links and not parser.terminal_pagination_seen:
        raise FreshMotorDiscoveryRefusal(
            CAP_PARK_ROUTE, "HTML pagination terminal state is unavailable"
        )
    next_url = urljoin(planned.url, parser.next_links[0]) if parser.next_links else None
    return ParsedPage(
        str(transport["packet_bound_index_revision"]),
        pagination_identity,
        tuple(candidates),
        next_url,
        None,
    )


def parse_page(
    body: bytes,
    *,
    planned: PlannedRequest,
    transport: Mapping[str, Any],
    ledger: AccessLedger,
    allow_fixture_envelope: bool,
) -> ParsedPage:
    content_type = str(transport["content_type"])
    try:
        if "json" in content_type:
            value = _strict_json(body)
            parsed = _parse_json_page(
                value,
                planned=planned,
                transport=transport,
                allow_fixture_envelope=allow_fixture_envelope,
            )
        elif "html" in content_type:
            parsed = _parse_html_page(body, planned=planned, transport=transport)
        else:
            raise FreshMotorDiscoveryRefusal(
                "MALFORMED_RESPONSE_REFUSE", "parser content type differs"
            )
    except FreshMotorDiscoveryRefusal:
        raise
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise FreshMotorDiscoveryRefusal(
            "MALFORMED_RESPONSE_REFUSE", "response schema differs"
        ) from exc
    ledger.increment("pages_parsed")
    ledger.increment("candidate_hits", len(parsed.candidates))
    return parsed


def _peak_rss_bytes() -> int:
    observed = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return observed if sys.platform == "darwin" else observed * 1024


def _enforce_resources(
    started_at: float, *, baseline_peak_rss_bytes: int = 0
) -> tuple[float, int]:
    runtime = time.monotonic() - started_at
    peak_rss = _peak_rss_bytes()
    attributable_peak_rss = max(0, peak_rss - baseline_peak_rss_bytes)
    if runtime > MAX_RUNTIME_SECONDS or attributable_peak_rss > MAX_PEAK_RSS_BYTES:
        raise FreshMotorDiscoveryRefusal(
            "RESOURCE_CAP_REFUSE", "runtime or peak RSS cap exceeded"
        )
    return runtime, peak_rss


def _request_fingerprint(planned: PlannedRequest) -> str:
    return _sha256(
        _canonical_json_bytes(
            {
                "body_sha256": _sha256(planned.body or b""),
                "method": planned.method,
                "url": planned.url,
            }
        )
    )


def _claim_boundary() -> dict[str, bool]:
    return {
        "scientific_claim_established": False,
        "source_selected_for_payload_access": False,
        "real_EEG_accessed": False,
        "neural_advantage_established": False,
        "unseen_person_generalization_established": False,
        "EEG_beyond_joint_nuisance_established": False,
        "movement_intention_or_motor_cortex_established": False,
        "thought_or_language_decoding_established": False,
        "causal_live_decoding_established": False,
        "hardware_or_clinical_value_established": False,
    }


def _bounded_report(report: dict[str, Any]) -> dict[str, Any]:
    report["measurements"]["retained_public_report_bytes"] = 0
    for _ in range(4):
        payload = _canonical_json_bytes(report)
        observed = len(payload)
        if observed > MAX_RETAINED_BYTES:
            raise FreshMotorDiscoveryRefusal(
                "RESOURCE_CAP_REFUSE", "retained report cap exceeded"
            )
        if report["measurements"]["retained_public_report_bytes"] == observed:
            return report
        report["measurements"]["retained_public_report_bytes"] = observed
    raise FreshMotorDiscoveryRefusal(
        "RESOURCE_CAP_REFUSE", "retained report size did not converge"
    )


def _run_discovery(
    *,
    opener: Callable[[urllib.request.Request, float], BinaryIO],
    resolver: Callable[..., Any],
    execution_mode: str,
    plan: Sequence[PlannedRequest] | None = None,
    ledger: AccessLedger | None = None,
) -> dict[str, Any]:
    """Traverse the frozen surface completely or refuse before routing."""

    if (
        execution_mode != "generated_mock_HTTP"
        or type(opener) is not FixtureOpener
        or resolver is not _mock_resolver
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE",
            "only generated discovery is implemented under the current packet",
        )
    allow_fixture_envelope = True
    baseline_peak_rss = _peak_rss_bytes()
    started_at = time.monotonic()
    deadline = started_at + MAX_RUNTIME_SECONDS
    ledger = ledger or AccessLedger()
    roots = tuple(plan or build_plan())
    if roots != build_plan():
        raise FreshMotorDiscoveryRefusal(
            "UNREGISTERED_ENDPOINT_REFUSE", "root request plan differs"
        )
    ledger.values["planned_root_requests"] = len(roots)
    candidates: list[Mapping[str, Any]] = []
    page_records: list[dict[str, Any]] = []
    seen_global_page_keys: set[tuple[str, str, str]] = set()

    for root in roots:
        current = root
        seen_request_fingerprints: set[str] = set()
        seen_response_hashes: set[str] = set()
        page_number = 0
        while True:
            _enforce_resources(
                started_at, baseline_peak_rss_bytes=baseline_peak_rss
            )
            fingerprint = _request_fingerprint(current)
            if fingerprint in seen_request_fingerprints:
                raise FreshMotorDiscoveryRefusal(
                    "PAGINATION_CYCLE_REFUSE", "pagination request cycle detected"
                )
            seen_request_fingerprints.add(fingerprint)
            body, redirects, transport = fetch_page(
                current,
                opener=opener,
                resolver=resolver,
                ledger=ledger,
                deadline=deadline,
            )
            if transport["body_sha256"] in seen_response_hashes:
                raise FreshMotorDiscoveryRefusal(
                    "DUPLICATE_PAGE_REFUSE", "duplicate page body detected"
                )
            seen_response_hashes.add(str(transport["body_sha256"]))
            parsed = parse_page(
                body,
                planned=current,
                transport=transport,
                ledger=ledger,
                allow_fixture_envelope=allow_fixture_envelope,
            )
            _enforce_resources(
                started_at, baseline_peak_rss_bytes=baseline_peak_rss
            )
            page_key = (root.index_id, root.query_or_category_id, parsed.pagination_identity)
            if page_key in seen_global_page_keys:
                raise FreshMotorDiscoveryRefusal(
                    "DUPLICATE_PAGE_REFUSE", "duplicate pagination identity detected"
                )
            seen_global_page_keys.add(page_key)
            page_number += 1
            page_records.append(
                {
                    "index_id": root.index_id,
                    "query_or_category_id": root.query_or_category_id,
                    "pagination_identity": parsed.pagination_identity,
                    "packet_bound_index_revision": parsed.revision,
                    "ordered_redirect_transcript": list(redirects),
                }
            )
            candidates.extend(parsed.candidates)
            if parsed.next_url is None:
                break
            _validate_pagination_transition(root, current, parsed)
            current = PlannedRequest(
                index_id=root.index_id,
                query_or_category_id=root.query_or_category_id,
                url=parsed.next_url,
                method=root.method,
                body=parsed.next_body,
                page_identity=f"{root.page_identity}:page_{page_number + 1}",
            )

    routed = route_candidates(candidates, ledger=ledger)
    runtime, peak_rss = _enforce_resources(
        started_at, baseline_peak_rss_bytes=baseline_peak_rss
    )
    unavailable = Counter(
        reason
        for candidate in routed["routed_candidates"]
        for reason in candidate.get("exclusion_reason", [])
    )
    for candidate in routed["incomplete_identity_exclusions"]:
        unavailable.update(candidate.get("exclusion_reason", []))
    warnings = [
        "metadata_only_discovery_not_neural_evidence",
        "index_search_metadata_not_source_specific_confirmation",
        "unknown_missing_ambiguous_or_conflicting_fields_treated_as_false",
        "selected_candidate_if_any_requires_a_separate_target_free_metadata_packet",
        "live_motor_success_would_not_validate_language_decoding",
    ]
    report = {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "complete_frozen_surface_traversal",
        "execution_surface": execution_mode,
        "route": routed["route"],
        "traversal": {
            "official_indexes_complete": len({row["index_id"] for row in page_records}),
            "root_requests_complete": len(roots),
            "pages_complete": len(page_records),
            "page_records": page_records,
        },
        "routing": routed,
        "operation_ledger": dict(ledger.values),
        "measurements": {
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "wire_body_bytes": ledger.values["wire_body_bytes"],
            "decoded_body_bytes": ledger.values["decoded_body_bytes"],
            "retained_public_report_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "end_to_end_latency_measured": False,
        },
        "unavailable_field_counts": dict(sorted(unavailable.items())),
        "warnings": warnings,
        "claim_boundary": _claim_boundary(),
    }
    return _bounded_report(report)


def _fixture_candidate(
    *, source_id: str = "FMSR1-GENERATED-001", participant_count: int = 12
) -> dict[str, Any]:
    provenance_fields = (
        "immutable_source_identifier",
        "immutable_release_identifier",
        "official_title",
        "official_landing_URL",
        "motor_task_description",
        "declared_sensor_modalities_and_roles",
        "declared_complete_participant_count",
        "declared_named_channel_and_geometry_availability",
        "declared_reference_sampling_event_and_target_semantics_availability",
        "declared_motor_classes",
        "payload_license_identifier",
        "declared_member_manifest_availability",
        "declared_complete_selected_payload_bytes",
        "documented_format_and_reader",
        "deterministic_sort_fields",
    )
    return {
        "immutable_source_identifier": source_id,
        "immutable_release_identifier": "generated-v1",
        "official_title": "Generated synchronized motor-control cohort",
        "official_landing_URL": "https://openneuro.org/datasets/generated-fmsr1",
        "motor_task_description": "Generated bilateral hand motor execution and imagery",
        "declared_sensor_modalities_and_roles": [
            "raw_synchronized_EEG",
            "recorded_EOG",
            "task_relevant_EMG_all_named_effectors",
        ],
        "declared_complete_participant_count": participant_count,
        "declared_named_channel_and_geometry_availability": {
            "named_EEG_channels": True,
            "geometry": True,
            "posterior_comparator_constructible": True,
        },
        "declared_reference_sampling_event_and_target_semantics_availability": {
            "reference": True,
            "sampling": True,
            "events": True,
            "targets": True,
            "decision_semantics": True,
            "cue_identity_may_equal_target": False,
        },
        "declared_motor_classes": ["left_hand", "right_hand"],
        "payload_license_identifier": "CC0-1.0-GENERATED",
        "declared_member_manifest_availability": {
            "complete": True,
            "sizes": True,
            "sha256": True,
        },
        "declared_complete_selected_payload_bytes": 512 * 1024**2,
        "documented_format_and_reader": {"format": "generated", "reader": "fixture"},
        "deterministic_sort_fields": {
            "complete_participant_count": participant_count,
            "bilateral_EMG_coverage_boolean": True,
            "kinematic_coverage_boolean": True,
            "independent_laboratory_device_participant_component_count": 3,
            "minimum_trials_per_participant": 80,
            "storage_headroom_bytes": MAX_SELECTED_PAYLOAD_BYTES - 512 * 1024**2,
        },
        "source_field_provenance": {
            field: "generated_fixture_explicit" for field in provenance_fields
        },
    }


def _fixture_page_bytes(
    planned: PlannedRequest,
    *,
    candidates: Sequence[Mapping[str, Any]] = (),
    pagination_identity: str | None = None,
    next_url: str | None = None,
    next_cursor: str | None = None,
) -> bytes:
    return _canonical_json_bytes(
        {
            "fmsr1_page": {
                "revision": _spec(planned.index_id).profile_revision,
                "pagination_identity": pagination_identity or planned.page_identity,
                "candidates": list(candidates),
                "next_url": next_url,
                "next_cursor": next_cursor,
            }
        }
    )


def _fixture_response(
    planned: PlannedRequest,
    body: bytes,
    *,
    status: int = 200,
    url: str | None = None,
    extra_headers: Sequence[tuple[str, str]] = (),
    declared_length: int | None = None,
    nonbytes_body: bool = False,
) -> FixtureResponse:
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(body) if declared_length is None else declared_length)),
        ("X-FMSR1-Index-Revision", _spec(planned.index_id).profile_revision),
        *extra_headers,
    ]
    return FixtureResponse(
        body,
        status=status,
        url=url or planned.url,
        headers=headers,
        nonbytes_body=nonbytes_body,
    )


def build_success_fixture_exchanges(
    *, candidates: Sequence[Mapping[str, Any]] | None = None
) -> tuple[FixtureExchange, ...]:
    plan = build_plan()
    rows = tuple(candidates) if candidates is not None else (_fixture_candidate(),)
    exchanges: list[FixtureExchange] = []
    for index, planned in enumerate(plan):
        body = _fixture_page_bytes(planned, candidates=rows if index == 0 else ())
        exchanges.append(
            FixtureExchange(
                method=planned.method,
                url=planned.url,
                body=planned.body,
                response=_fixture_response(planned, body),
            )
        )
    return tuple(exchanges)


def _run_success_fixture(
    *, candidates: Sequence[Mapping[str, Any]] | None = None
) -> dict[str, Any]:
    opener = FixtureOpener(build_success_fixture_exchanges(candidates=candidates))
    report = _run_discovery(
        opener=opener,
        resolver=_mock_resolver,
        execution_mode="generated_mock_HTTP",
    )
    opener.assert_consumed()
    if report["operation_ledger"]["real_network_requests"] != 0:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "generated qualification touched the network"
        )
    return report


def _deterministic_projection(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in report.items()
        if key not in {"measurements"}
    }


def _expect_refusal(
    expected_route: str, operation: Callable[[], Any]
) -> dict[str, str]:
    try:
        operation()
    except FreshMotorDiscoveryRefusal as exc:
        if exc.route != expected_route:
            raise AssertionError(
                f"expected {expected_route}, observed {exc.route}"
            ) from exc
        return {"expected": expected_route, "observed": exc.route, "status": "passed"}
    raise AssertionError(f"expected refusal {expected_route}")


def _fetch_first_fixture(
    response: FixtureResponse,
    *,
    resolver: Callable[..., Any] = _mock_resolver,
) -> tuple[bytes, tuple[dict[str, Any], ...], Mapping[str, Any]]:
    planned = build_plan()[0]
    opener = FixtureOpener(
        (FixtureExchange(planned.method, planned.url, planned.body, response),)
    )
    result = fetch_page(
        planned,
        opener=opener,
        resolver=resolver,
        ledger=AccessLedger(),
    )
    opener.assert_consumed()
    return result


def _run_first_page_mutation(body: bytes) -> dict[str, Any]:
    exchanges = list(build_success_fixture_exchanges())
    planned = build_plan()[0]
    exchanges[0] = FixtureExchange(
        planned.method,
        planned.url,
        planned.body,
        _fixture_response(planned, body),
    )
    opener = FixtureOpener(exchanges)
    return _run_discovery(
        opener=opener,
        resolver=_mock_resolver,
        execution_mode="generated_mock_HTTP",
    )


def _run_nemar_pagination_mutation(*, duplicate_identity: bool) -> dict[str, Any]:
    plan = build_plan()
    exchanges = list(build_success_fixture_exchanges(candidates=()))
    root_index = 4
    root = plan[root_index]
    next_url = f"{root.url}&page=2"
    first = _fixture_page_bytes(root, next_url=next_url)
    second_planned = PlannedRequest(
        root.index_id,
        root.query_or_category_id,
        next_url,
        root.method,
        None,
        f"{root.page_identity}:page_2",
    )
    second = _fixture_page_bytes(
        second_planned,
        pagination_identity=root.page_identity if duplicate_identity else second_planned.page_identity,
    )
    exchanges[root_index : root_index + 1] = [
        FixtureExchange(root.method, root.url, root.body, _fixture_response(root, first)),
        FixtureExchange(
            second_planned.method,
            second_planned.url,
            second_planned.body,
            _fixture_response(second_planned, second),
        ),
    ]
    opener = FixtureOpener(exchanges)
    return _run_discovery(
        opener=opener,
        resolver=_mock_resolver,
        execution_mode="generated_mock_HTTP",
    )


def _run_nemar_cycle_mutation() -> dict[str, Any]:
    plan = build_plan()
    exchanges = list(build_success_fixture_exchanges(candidates=()))
    root = plan[4]
    first = _fixture_page_bytes(root, next_url=root.url)
    exchanges[4] = FixtureExchange(
        root.method,
        root.url,
        root.body,
        _fixture_response(root, first),
    )
    opener = FixtureOpener(exchanges)
    return _run_discovery(
        opener=opener,
        resolver=_mock_resolver,
        execution_mode="generated_mock_HTTP",
    )


def _run_incomplete_surface_mutation() -> dict[str, Any]:
    opener = FixtureOpener(build_success_fixture_exchanges()[:-1])
    return _run_discovery(
        opener=opener,
        resolver=_mock_resolver,
        execution_mode="generated_mock_HTTP",
    )


def _ordering_observation() -> dict[str, Any]:
    first = _fixture_candidate(source_id="FMSR1-GENERATED-A", participant_count=12)
    second = _fixture_candidate(source_id="FMSR1-GENERATED-B", participant_count=14)
    context = {
        "official_index_id": "OPENNEURO",
        "packet_bound_index_revision": INDEX_SPECS[0].profile_revision,
        "query_or_category_id": "query_1",
        "pagination_identity": "ordering-page",
        "ordered_redirect_transcript": [],
    }
    candidates = [{**first, **context}, {**second, **context}]
    result = route_candidates(candidates, ledger=AccessLedger())
    selected = result["selected_candidates"]
    if len(selected) != 1 or selected[0]["immutable_source_identifier"] != "FMSR1-GENERATED-B":
        raise AssertionError("deterministic descending participant ordering differs")
    return {
        "status": "passed",
        "selected_canonical_candidate_id": selected[0]["canonical_candidate_id"],
    }


def _stream_cap_plus_one_observation() -> None:
    planned = build_plan()[0]
    body = b"x" * (MAX_PAGE_BYTES + 1)
    response = FixtureResponse(
        body,
        url=planned.url,
        headers=(
            ("Content-Type", "application/json"),
            ("X-FMSR1-Index-Revision", _spec(planned.index_id).profile_revision),
        ),
    )
    opener = FixtureOpener(
        (FixtureExchange(planned.method, planned.url, planned.body, response),)
    )
    ledger = AccessLedger()
    try:
        fetch_page(
            planned,
            opener=opener,
            resolver=_mock_resolver,
            ledger=ledger,
        )
    except FreshMotorDiscoveryRefusal:
        if ledger.values["wire_body_bytes"] != MAX_PAGE_BYTES + 1:
            raise AssertionError("cap-plus-one reader consumed the wrong byte count")
        raise


def _unsupported_content_type_accounting_observation() -> None:
    planned = build_plan()[0]
    body = b"x" * 4096
    response = FixtureResponse(
        body,
        url=planned.url,
        headers=(
            ("Content-Type", "application/octet-stream"),
            ("Content-Length", str(len(body))),
            ("X-FMSR1-Index-Revision", _spec(planned.index_id).profile_revision),
        ),
    )
    opener = FixtureOpener(
        (FixtureExchange(planned.method, planned.url, planned.body, response),)
    )
    ledger = AccessLedger()
    try:
        fetch_page(
            planned,
            opener=opener,
            resolver=_mock_resolver,
            ledger=ledger,
        )
    except FreshMotorDiscoveryRefusal:
        if (
            ledger.values["wire_body_bytes"] != len(body)
            or ledger.values["decoded_body_bytes"] != len(body)
        ):
            raise AssertionError("unsupported content-type body was not counted")
        raise


def _html_terminal_ambiguity_observation() -> None:
    planned = build_plan()[4]
    body = (
        b'<script type="application/ld+json">'
        b'{"@type":"Dataset","identifier":"fresh","name":"Fresh"}'
        b"</script>"
    )
    _parse_html_page(
        body,
        planned=planned,
        transport={
            "packet_bound_index_revision": _spec(planned.index_id).profile_revision,
            "ordered_redirect_transcript": (),
            "body_sha256": _sha256(body),
        },
    )


def _non_global_resolution_observation() -> None:
    def resolver(*_args: Any, **_kwargs: Any) -> list[Any]:
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("100.64.0.1", 443))]

    _validate_public_resolution("openneuro.org", resolver)


def _generated_transport_bypass_observation() -> None:
    planned = build_plan()[0]
    opener = FixtureOpener(
        (
            FixtureExchange(
                planned.method,
                planned.url,
                planned.body,
                _fixture_response(planned, _fixture_page_bytes(planned)),
            ),
        )
    )
    fetch_page(
        planned,
        opener=opener,
        resolver=socket.getaddrinfo,
        ledger=AccessLedger(),
    )


def _run_refusal_matrix(repo_root: Path) -> dict[str, Any]:
    first = build_plan()[0]
    valid_body = _fixture_page_bytes(first)
    cases: dict[str, dict[str, str]] = {}
    cases["declared_response_cap"] = _expect_refusal(
        "RESPONSE_CAP_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(first, b"", declared_length=MAX_PAGE_BYTES + 1)
        ),
    )
    cases["truncated_response"] = _expect_refusal(
        "TRUNCATED_RESPONSE_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(first, valid_body, declared_length=len(valid_body) + 1)
        ),
    )
    cases["unsupported_content_encoding"] = _expect_refusal(
        "UNSUPPORTED_CONTENT_ENCODING_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(first, valid_body, extra_headers=(("Content-Encoding", "gzip"),))
        ),
    )
    cases["unsupported_transfer_encoding"] = _expect_refusal(
        "UNSUPPORTED_CONTENT_ENCODING_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(first, valid_body, extra_headers=(("Transfer-Encoding", "chunked"),))
        ),
    )
    cases["streamed_response_cap_plus_one"] = _expect_refusal(
        "RESPONSE_CAP_REFUSE", _stream_cap_plus_one_observation
    )
    cases["unsupported_content_type_body_accounting"] = _expect_refusal(
        "MALFORMED_RESPONSE_REFUSE",
        _unsupported_content_type_accounting_observation,
    )
    cases["nonbytes_body"] = _expect_refusal(
        "MALFORMED_RESPONSE_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(first, valid_body, nonbytes_body=True)
        ),
    )
    cases["off_allowlist_redirect"] = _expect_refusal(
        "OFF_ALLOWLIST_REDIRECT_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(
                first,
                b"",
                status=307,
                extra_headers=(("Location", "https://example.org/off-surface"),),
            )
        ),
    )
    cases["same_host_endpoint_drift"] = _expect_refusal(
        "OFF_ALLOWLIST_REDIRECT_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(
                first,
                b"",
                status=307,
                extra_headers=(("Location", "https://openneuro.org/download/payload"),),
            )
        ),
    )
    cases["redirect_method_rewrite"] = _expect_refusal(
        "REDIRECT_METHOD_REWRITE_REFUSE",
        lambda: _fetch_first_fixture(
            _fixture_response(
                first,
                b"",
                status=302,
                extra_headers=(("Location", first.url),),
            )
        ),
    )
    cases["duplicate_JSON_key"] = _expect_refusal(
        "MALFORMED_RESPONSE_REFUSE",
        lambda: _run_first_page_mutation(
            b'{"fmsr1_page":{},"fmsr1_page":{}}\n'
        ),
    )
    leaking = _fixture_candidate()
    leaking["target"] = "forbidden"
    cases["target_like_field"] = _expect_refusal(
        "RETAINED_FIELD_REFUSE",
        lambda: _run_first_page_mutation(
            _fixture_page_bytes(first, candidates=(leaking,))
        ),
    )
    unicode_leaking = _fixture_candidate()
    unicode_leaking["\uff34\uff21\uff32\uff27\uff25\uff34"] = "forbidden"
    cases["NFKC_target_like_field"] = _expect_refusal(
        "RETAINED_FIELD_REFUSE",
        lambda: _run_first_page_mutation(
            _fixture_page_bytes(first, candidates=(unicode_leaking,))
        ),
    )
    plural_leaking = _fixture_candidate()
    plural_leaking["targets"] = ["forbidden"]
    cases["plural_target_like_field"] = _expect_refusal(
        "RETAINED_FIELD_REFUSE",
        lambda: _run_first_page_mutation(
            _fixture_page_bytes(first, candidates=(plural_leaking,))
        ),
    )
    unknown = _fixture_candidate()
    unknown["convenience_metric"] = 1
    cases["retained_field"] = _expect_refusal(
        "RETAINED_FIELD_REFUSE",
        lambda: _run_first_page_mutation(
            _fixture_page_bytes(first, candidates=(unknown,))
        ),
    )
    conflict_a = _fixture_candidate()
    conflict_b = _fixture_candidate()
    conflict_b["official_title"] = "Conflicting generated title"
    cases["identity_conflict"] = _expect_refusal(
        "MALFORMED_RESPONSE_REFUSE",
        lambda: _run_success_fixture(candidates=(conflict_a, conflict_b)),
    )
    cases["duplicate_page_identity"] = _expect_refusal(
        "DUPLICATE_PAGE_REFUSE",
        lambda: _run_nemar_pagination_mutation(duplicate_identity=True),
    )
    cases["pagination_cycle"] = _expect_refusal(
        "PAGINATION_CYCLE_REFUSE", _run_nemar_cycle_mutation
    )
    cases["incomplete_surface"] = _expect_refusal(
        CAP_PARK_ROUTE, _run_incomplete_surface_mutation
    )
    cases["ambiguous_JSON_pagination"] = _expect_refusal(
        CAP_PARK_ROUTE,
        lambda: _run_first_page_mutation(b'{"results":[]}\n'),
    )
    cases["ambiguous_HTML_terminal"] = _expect_refusal(
        CAP_PARK_ROUTE,
        _html_terminal_ambiguity_observation,
    )
    cases["non_global_resolution"] = _expect_refusal(
        "OFF_ALLOWLIST_REDIRECT_REFUSE",
        _non_global_resolution_observation,
    )
    cases["generated_transport_bypass"] = _expect_refusal(
        "AUTHORITY_REFUSE",
        _generated_transport_bypass_observation,
    )
    cases["runtime_cap"] = _expect_refusal(
        "RESOURCE_CAP_REFUSE",
        lambda: _enforce_resources(time.monotonic() - MAX_RUNTIME_SECONDS - 1.0),
    )
    cases["authority_proof"] = _expect_refusal(
        "AUTHORITY_REFUSE",
        lambda: _read_exact_json(
            repo_root / "registries" / "not-a-tracked-proof.json", "0" * 64
        ),
    )
    return {
        "case_count": len(cases),
        "all_passed": all(row["status"] == "passed" for row in cases.values()),
        "cases": cases,
        "ordering": _ordering_observation(),
    }


def run_generated_qualification(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Run two mock-HTTP replays and the frozen adversarial refusal matrix."""

    root = Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[3]
    load_green_decision(root)
    baseline_peak_rss = _peak_rss_bytes()
    started_at = time.monotonic()
    original_environment = {key: os.environ.get(key) for key in THREAD_ENV_KEYS}
    try:
        for key in THREAD_ENV_KEYS:
            os.environ[key] = "1"
        first = _run_success_fixture()
        second = _run_success_fixture()
        first_projection = _deterministic_projection(first)
        second_projection = _deterministic_projection(second)
        first_digest = _sha256(_canonical_json_bytes(first_projection))
        second_digest = _sha256(_canonical_json_bytes(second_projection))
        if first_projection != second_projection or first_digest != second_digest:
            raise AssertionError("generated discovery replay differs")
        refusals = _run_refusal_matrix(root)
        if not refusals["all_passed"]:
            raise AssertionError("generated refusal matrix differs")
        runtime, peak_rss = _enforce_resources(
            started_at, baseline_peak_rss_bytes=baseline_peak_rss
        )
    finally:
        for key, value in original_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    result = {
        "schema_name": f"{SCHEMA_NAME}.generated_qualification",
        "schema_version": SCHEMA_VERSION,
        "protocol_id": PROTOCOL_ID,
        "status": "passed_generated_only_two_replay_qualification",
        "replay_count": 2,
        "deterministic_replay_digest": first_digest,
        "replay_route": first["route"],
        "replay_selected_candidate_count": len(
            first["routing"]["selected_candidates"]
        ),
        "root_requests_per_replay": len(build_plan()),
        "mock_HTTP_calls_across_success_replays": (
            first["operation_ledger"]["mock_HTTP_calls"]
            + second["operation_ledger"]["mock_HTTP_calls"]
        ),
        "refusal_matrix": refusals,
        "measurements": {
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "retained_public_report_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
        },
        "operation_counters": {
            "real_network_requests": 0,
            "real_network_bytes": 0,
            "payload_or_header_reads": 0,
            "signal_event_annotation_target_or_label_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "scores": 0,
            "provider_calls": 0,
            "stream_device_or_hardware_runs": 0,
            "operations_on_other_projects": 0,
            "cleanup_or_deletion_operations": 0,
            "scientific_claim_upgrades": 0,
        },
        "warnings": [
            "generated_fixture_only_not_source_discovery",
            "mock_HTTP_only_zero_live_network",
            "synthetic_candidate_not_a_real_dataset",
            "qualification_not_neural_evidence",
        ],
        "claim_boundary": _claim_boundary(),
    }
    return _bounded_report(result)


def _read_no_follow_bytes(path: Path, *, maximum_bytes: int) -> bytes:
    try:
        info = os.lstat(path)
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise OSError("object type differs")
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        try:
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = os.read(descriptor, min(READ_CHUNK_BYTES, maximum_bytes + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > maximum_bytes:
                    raise OSError("tracked artifact cap exceeded")
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "tracked implementation artifact unavailable"
        ) from exc
    return b"".join(chunks)


def _git(repo_root: Path, *arguments: str) -> str:
    try:
        completed = subprocess.run(
            ("git", *arguments),
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "Git proof check failed"
        ) from exc
    return completed.stdout.strip()


def verify_green_implementation_evidence(
    repo_root: str | Path, evidence: GreenImplementationEvidence
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    load_green_decision(root)
    hex_fields = (
        (evidence.implementation_commit, 40),
        (evidence.implementation_registry_sha256, 64),
        (evidence.implementation_proof_commit, 40),
        (evidence.implementation_proof_sha256, 64),
    )
    if (
        any(
            len(value) != length
            or any(character not in "0123456789abcdef" for character in value)
            for value, length in hex_fields
        )
        or evidence.execution_ordinal != 1
        or evidence.CI_run_id <= GREEN_DECISION_CI_RUN_ID
        or evidence.base_python_job_id <= GREEN_DECISION_BASE_JOB_ID
        or evidence.optional_neuro_readers_job_id <= GREEN_DECISION_OPTIONAL_JOB_ID
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "implementation green evidence is malformed"
        )
    if _git(root, "rev-parse", "HEAD") != evidence.implementation_proof_commit:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "implementation proof commit is not exact HEAD"
        )
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "tracked worktree differs from exact implementation"
        )
    untracked = _git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
    sensitive_prefixes = (
        "src/neurodecodekit/",
        "registries/fresh_motor_source_discovery",
        "docs/FRESH_MOTOR_SOURCE_DISCOVERY",
    )
    if any(
        row.startswith("?? ") and row[3:].startswith(sensitive_prefixes)
        for row in untracked
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "untracked execution-sensitive artifact exists"
        )
    _git(root, "merge-base", "--is-ancestor", GREEN_DECISION_COMMIT, evidence.implementation_commit)
    _git(
        root,
        "merge-base",
        "--is-ancestor",
        evidence.implementation_commit,
        evidence.implementation_proof_commit,
    )
    _git(root, "merge-base", "--is-ancestor", "HEAD", "origin/main")
    registry_path = root / IMPLEMENTATION_RELATIVE_PATH
    registry = _read_exact_json(
        registry_path, evidence.implementation_registry_sha256
    )
    proof = _read_exact_json(
        root / IMPLEMENTATION_PROOF_RELATIVE_PATH,
        evidence.implementation_proof_sha256,
    )
    registry_blob = _git(root, "hash-object", str(IMPLEMENTATION_RELATIVE_PATH))
    proof_blob = _git(root, "hash-object", str(IMPLEMENTATION_PROOF_RELATIVE_PATH))
    if (
        _git(root, "ls-files", "--error-unmatch", str(IMPLEMENTATION_RELATIVE_PATH))
        != str(IMPLEMENTATION_RELATIVE_PATH)
        or _git(root, "ls-files", "--error-unmatch", str(IMPLEMENTATION_PROOF_RELATIVE_PATH))
        != str(IMPLEMENTATION_PROOF_RELATIVE_PATH)
        or _git(
            root,
            "rev-parse",
            f"{evidence.implementation_commit}:{IMPLEMENTATION_RELATIVE_PATH}",
        )
        != registry_blob
        or _git(
            root,
            "rev-parse",
            f"{evidence.implementation_proof_commit}:{IMPLEMENTATION_PROOF_RELATIVE_PATH}",
        )
        != proof_blob
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "implementation proof is not a tracked exact blob"
        )
    authority = registry.get("execution_authority_after_exact_remote_green", {})
    qualification = registry.get("generated_qualification", {})
    if (
        registry.get("implementation_id") != PROTOCOL_ID
        or registry.get("green_decision_commit") != GREEN_DECISION_COMMIT
        or registry.get("implementation_commit_binding")
        != "this_exact_commit_after_push_and_both_required_CI_jobs_green"
        or authority.get("one_metadata_only_public_discovery_execution") is not True
        or authority.get("maximum_registered_executions") != 1
        or authority.get("retry_or_rerun") is not False
        or authority.get("payload_model_score_or_claim_authority") is not False
        or qualification.get("status")
        != "passed_generated_only_two_replay_qualification"
        or qualification.get("real_network_requests") != 0
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "implementation registry boundary differs"
        )
    jobs = proof.get("required_jobs", [])
    expected_jobs = {
        "Base Python": evidence.base_python_job_id,
        "Optional Neuro Readers": evidence.optional_neuro_readers_job_id,
    }
    observed_jobs = {
        row.get("name"): row.get("job_id")
        for row in jobs
        if isinstance(row, dict) and row.get("conclusion") == "success"
    }
    if (
        proof.get("schema_name")
        != "neurodecodekit.fresh_motor_source_discovery_implementation_proof"
        or proof.get("status") != "exact_implementation_remotely_green"
        or proof.get("proof_commit_binding") != "this_exact_commit"
        or proof.get("implementation_commit") != evidence.implementation_commit
        or proof.get("implementation_registry_sha256")
        != evidence.implementation_registry_sha256
        or proof.get("CI_run_id") != evidence.CI_run_id
        or proof.get("CI_head_sha") != evidence.implementation_commit
        or proof.get("CI_head_branch") != "main"
        or proof.get("CI_conclusion") != "success"
        or observed_jobs != expected_jobs
        or proof.get("both_required_jobs_green") is not True
        or proof.get("network_execution_authority_created") is not False
        or proof.get("payload_model_score_or_claim_authority") is not False
    ):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "tracked remote-green proof differs"
        )
    artifacts = registry.get("bound_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "implementation artifact binding is absent"
        )
    for row in artifacts:
        if not isinstance(row, dict):
            raise FreshMotorDiscoveryRefusal(
                "AUTHORITY_REFUSE", "implementation artifact binding differs"
            )
        relative = Path(str(row.get("path", "")))
        if relative.is_absolute() or ".." in relative.parts:
            raise FreshMotorDiscoveryRefusal(
                "AUTHORITY_REFUSE", "implementation artifact path differs"
            )
        payload = _read_no_follow_bytes(root / relative, maximum_bytes=2 * 1024**2)
        tracked_blob = _git(root, "ls-files", "--error-unmatch", str(relative))
        commit_blob = _git(
            root,
            "rev-parse",
            f"{evidence.implementation_commit}:{relative}",
        )
        if (
            tracked_blob != str(relative)
            or len(payload) != row.get("bytes")
            or _sha256(payload) != row.get("sha256")
            or _git(root, "hash-object", str(relative)) != row.get("git_blob")
            or commit_blob != row.get("git_blob")
        ):
            raise FreshMotorDiscoveryRefusal(
                "AUTHORITY_REFUSE", "implementation artifact identity differs"
            )
    return registry


def _ensure_directory_no_follow(path: Path, *, stop: Path) -> None:
    missing: list[Path] = []
    current = path
    while current != stop and not current.exists():
        missing.append(current)
        current = current.parent
    try:
        current_info = os.lstat(current)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "output parent is unavailable"
        ) from exc
    if stat.S_ISLNK(current_info.st_mode) or not stat.S_ISDIR(current_info.st_mode):
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "output parent type differs"
        )
    for candidate in reversed(missing):
        try:
            os.mkdir(candidate, 0o700)
        except OSError as exc:
            raise FreshMotorDiscoveryRefusal(
                "AUTHORITY_REFUSE", "output directory creation failed"
            ) from exc


def _write_new_json(path: Path, value: Mapping[str, Any], *, maximum_bytes: int) -> int:
    payload = _canonical_json_bytes(value)
    if len(payload) > maximum_bytes:
        raise FreshMotorDiscoveryRefusal(
            "RESOURCE_CAP_REFUSE", "public artifact cap exceeded"
        )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("short artifact write")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "exclusive artifact publication failed"
        ) from exc
    try:
        parent_descriptor = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(parent_descriptor)
        finally:
            os.close(parent_descriptor)
    except OSError as exc:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE", "artifact directory durability failed"
        ) from exc
    return len(payload)


def _assert_single_thread_environment() -> None:
    if any(os.environ.get(key) != "1" for key in THREAD_ENV_KEYS):
        raise FreshMotorDiscoveryRefusal(
            "RESOURCE_CAP_REFUSE", "single-thread environment is not explicit"
        )


def execute_registered_discovery(
    evidence: GreenImplementationEvidence,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Refuse live execution because the current packet cannot be armed exactly."""

    del evidence, repo_root
    missing_revisions = [
        spec.index_id
        for spec in INDEX_SPECS
        if spec.packet_bound_official_revision is None
    ]
    if missing_revisions:
        raise FreshMotorDiscoveryRefusal(
            "AUTHORITY_REFUSE",
            "exact official index revisions are not packet-bound",
        )
    raise FreshMotorDiscoveryRefusal(
        "AUTHORITY_REFUSE",
        "authenticated remote CI verification and a live transport are not implemented",
    )
