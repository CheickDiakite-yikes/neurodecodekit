"""Proof-gated MARC2 variable-domain structural cohort recovery."""

from __future__ import annotations

import argparse
import copy
import hashlib
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
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path, PurePosixPath
from typing import Any

from neurodecodekit.datasets import (
    marc2_live_domain_eligibility_adapter as domain_adapter,
)
from neurodecodekit.datasets import marc2_proof_record_recovery as shared_proof


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR3"
MODULE_NAME = "neurodecodekit.datasets.marc2_variable_domain_private_recovery"
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_variable_domain_private_recovery_report"
)
PRIVATE_SCHEMA_NAME = (
    "neurodecodekit.marc2_variable_domain_private_selection_manifest"
)
MARKER_SCHEMA_NAME = "neurodecodekit.marc2_variable_domain_consumed_marker"
GENERATED_ROUTE = "MARC2VDR-G1"
SUCCESS_ROUTE = "MARC2VDR-R1"
REFUSAL_ROUTES = tuple(f"MARC2VDR-F{index:02d}" for index in range(7))

DECISION_COMMIT = "944b6e8af434c2a6820435e0f18fe9490bf44248"
DECISION_CI_RUN_ID = 31_962_561_043
DECISION_BASE_JOB_ID = 95_202_667_384
DECISION_OPTIONAL_JOB_ID = 95_202_667_483
DECISION_RELATIVE_PATH = Path(
    "registries/marc2_variable_domain_private_recovery_authorization_decision.v0.json"
)
DECISION_SHA256 = "475f86bda22647cbe3aa585d670ffcb2ed870344828b698cbca29440a502ccd4"
REQUEST_RELATIVE_PATH = Path(
    "registries/marc2_variable_domain_private_recovery_authorization_request.v0.json"
)
REQUEST_SHA256 = "f665d66f3b6c5e97c88d8302de0b87d63e0383f45bdab54d34a90f80f4ce248b"
PACKET_RELATIVE_PATH = Path(
    "docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_AUTHORIZATION_PACKET.md"
)
PACKET_SHA256 = "1f546f25372b6212d5e86518b30acd3d42fe664965394fa5a72d5b043b4a709a"

NATIVE_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_variable_domain_private_recovery_implementation.v0.json"
)
PROOF_CERTIFICATE_RELATIVE_PATH = Path(
    "registries/marc2_variable_domain_private_recovery_proof_certificate.v0.json"
)
PRIVATE_SOURCE_RELATIVE_PATH = Path(
    ".codex_work/marc1_central_directory/live_audit_v0/"
    "member_inventory.private.v0.json"
)
OUTPUT_ROOT_RELATIVE_PATH = Path(
    ".codex_work/marc2_live_domain_private_recovery/v0"
)
MARKER_NAME = "consumed_marker.v0.json"
PRIVATE_MANIFEST_NAME = "cohort_selection.private.v0.json"
AGGREGATE_REPORT_NAME = "cohort_manifest.aggregate.v0.json"

EXPECTED_PRIVATE_BYTES = 418_755
EXPECTED_PRIVATE_SHA256 = (
    "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031"
)
EXPECTED_PRIVATE_MODE = 0o600
EXPECTED_ROWS = 1_227
EXPECTED_FILES = 1_025
EXPECTED_DIRECTORIES = 202
EXPECTED_SOURCE_BUNDLES = 238
EXPECTED_ELIGIBLE_BUNDLES = 195
EXPECTED_INELIGIBLE_BUNDLES = 43

MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_COMBINED_OUTPUT_BYTES = 2 * 1024**2
MAX_INCREMENTAL_DISK_BYTES = 4 * 1024**2
MINIMUM_FREE_DISK_BYTES = 15 * 1024**3
MAX_NORMALIZED_LOAD = 1.0
RESERVATION_CAP_BYTES = 8 * 1024**3
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")

WRAPPER_MUTATION_ROUTES = {
    "packet_hash_mismatch": REFUSAL_ROUTES[0],
    "decision_hash_mismatch": REFUSAL_ROUTES[0],
    "certificate_lane_mismatch": REFUSAL_ROUTES[0],
    "native_registry_lane_mismatch": REFUSAL_ROUTES[0],
    "validator_alias_substitution": REFUSAL_ROUTES[0],
    "adapter_alias_substitution": REFUSAL_ROUTES[0],
    "thread_environment_drift": REFUSAL_ROUTES[1],
    "normalized_load_exceeded": REFUSAL_ROUTES[1],
    "free_disk_below_floor": REFUSAL_ROUTES[1],
    "output_root_mismatch": REFUSAL_ROUTES[1],
    "output_root_exists": REFUSAL_ROUTES[1],
    "output_symlink": REFUSAL_ROUTES[1],
    "source_component_symlink": REFUSAL_ROUTES[1],
    "source_final_symlink": REFUSAL_ROUTES[1],
    "source_nonregular": REFUSAL_ROUTES[1],
    "source_owner_or_mode_mismatch": REFUSAL_ROUTES[1],
    "source_size_mismatch": REFUSAL_ROUTES[2],
    "source_hash_mismatch": REFUSAL_ROUTES[2],
    "open_fstat_identity_race": REFUSAL_ROUTES[2],
    "duplicate_JSON_key": REFUSAL_ROUTES[2],
    "source_schema_or_count_mismatch": REFUSAL_ROUTES[2],
    "VR2_classification_refusal": REFUSAL_ROUTES[3],
    "source_mutation": REFUSAL_ROUTES[3],
    "mutable_alias": REFUSAL_ROUTES[3],
    "adapter_call_count_mismatch": REFUSAL_ROUTES[3],
    "predicate_arithmetic_mismatch": REFUSAL_ROUTES[3],
    "selection_identity_drift": REFUSAL_ROUTES[4],
    "split_or_reservation_drift": REFUSAL_ROUTES[4],
    "aggregate_private_field_leak": REFUSAL_ROUTES[5],
    "output_cap_or_mode_drift": REFUSAL_ROUTES[5],
    "runtime_RSS_or_replay_drift": REFUSAL_ROUTES[6],
    "forbidden_operation_counter_nonzero": REFUSAL_ROUTES[6],
}
WRAPPER_MUTATIONS = tuple(WRAPPER_MUTATION_ROUTES)

AGGREGATE_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "source_summary",
        "cohort_summary",
        "split_summary",
        "byte_summary",
        "selection_hashes",
        "measurements",
        "resource_caps",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)
FORBIDDEN_AGGREGATE_KEYS = frozenset(
    {
        "rows",
        "entries",
        "member_name",
        "relative_path",
        "local_path",
        "output_path",
        "offset",
        "local_header_offset",
        "compressed_size",
        "uncompressed_size",
        "crc32",
        "source_body",
    }
)


class VariableDomainPrivateRecoveryRefusal(RuntimeError):
    """Fail closed with one stable aggregate-safe VR3 route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR3 refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class ExecutionEvidence:
    """Remote-green implementation evidence supplied to the fixed executor."""

    implementation_commit: str
    CI_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True, slots=True)
class SourceRead:
    """One strict source read and aggregate access counts."""

    source: Mapping[str, Any]
    payload_sha256: str
    bytes_read: int
    component_checks: int


@dataclass(frozen=True, slots=True)
class ExecutionOutcome:
    """One consumed target-free private structural selection."""

    report: Mapping[str, Any]
    private_manifest_sha256: str
    marker_bytes: int
    private_output_bytes: int
    aggregate_output_bytes: int


def _repo_root() -> Path:
    return Path(__file__).parents[3]


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return (
            json.dumps(
                value,
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = nested
    return value


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json(payload: bytes, *, route: str = REFUSAL_ROUTES[2]) -> dict[str, Any]:
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise VariableDomainPrivateRecoveryRefusal(route, "JSON encoding differs")
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise VariableDomainPrivateRecoveryRefusal(route, "strict JSON differs") from exc
    if not isinstance(value, dict):
        raise VariableDomainPrivateRecoveryRefusal(route, "JSON root differs")
    return value


def _read_tracked_bytes(path: Path, expected_sha256: str, *, cap: int) -> bytes:
    try:
        info = path.lstat()
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact is unavailable"
        ) from exc
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_size > cap:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact shape differs"
        )
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact read failed"
        ) from exc
    if len(payload) != info.st_size or _sha256_bytes(payload) != expected_sha256:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked artifact identity differs"
        )
    return payload


def _validate_decision_and_request(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    decision_payload = _read_tracked_bytes(
        root / DECISION_RELATIVE_PATH, DECISION_SHA256, cap=256 * 1024
    )
    request_payload = _read_tracked_bytes(
        root / REQUEST_RELATIVE_PATH, REQUEST_SHA256, cap=256 * 1024
    )
    _read_tracked_bytes(root / PACKET_RELATIVE_PATH, PACKET_SHA256, cap=256 * 1024)
    decision = _strict_json(decision_payload, route=REFUSAL_ROUTES[0])
    request = _strict_json(request_payload, route=REFUSAL_ROUTES[0])
    green = decision.get("green_request", {})
    authority = decision.get("authorization", {})
    if (
        decision.get("lane_id") != LANE_ID
        or decision.get("authorization_parent_commit")
        != "328faa845d894459a658b6ad62d078a00f539e9e"
        or green.get("CI_run_id") != 31_947_928_896
        or green.get("both_required_jobs_green") is not True
        or authority.get("wrapper_implementation_after_decision_green") is not True
        or authority.get("MARC2_FW2_real_execution_authorized_now") is not False
        or request.get("lane_id") != LANE_ID
        or any(request.get("authorization_flags", {}).values())
        or any(request.get("access_counters", {}).values())
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "decision or request semantics differ"
        )
    return decision, request


def _validate_relative_path(value: str, *, allow_codex_work: bool) -> Path:
    if not value or value.startswith(("/", "~")) or "\\" in value:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked path differs"
        )
    pure = PurePosixPath(value)
    if (
        pure.as_posix() != value
        or pure.is_absolute()
        or any(part in {"", ".", ".."} for part in pure.parts)
        or (not allow_codex_work and ".codex_work" in pure.parts)
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked path differs"
        )
    return Path(*pure.parts)


def _load_native_registry(root: Path) -> dict[str, Any]:
    path = root / NATIVE_REGISTRY_RELATIVE_PATH
    try:
        payload = path.read_bytes()
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "native registry is unavailable"
        ) from exc
    registry = _strict_json(payload, route=REFUSAL_ROUTES[0])
    surface = registry.get("implementation_surface", {})
    qualification = registry.get("generated_qualification", {})
    if (
        registry.get("schema_name")
        != "neurodecodekit.marc2_variable_domain_private_recovery_implementation"
        or registry.get("schema_version") != SCHEMA_VERSION
        or registry.get("lane_id") != LANE_ID
        or registry.get("status")
        != "generated_mock_wrapper_qualified_remote_green_required_before_private_pass"
        or registry.get("implementation_remote_proof") is not None
        or surface.get("module") != MODULE_NAME
        or surface.get("commands") != ["plan", "qualify", "inspect", "execute"]
        or surface.get("standard_library_only") is not True
        or surface.get("generic_source_or_output_override") is not False
        or qualification.get("proof_certificate_mutations_passed") != 32
        or qualification.get("wrapper_mutations_passed") != 32
        or qualification.get("success_paths") != 8
        or any(registry.get("authorization_state", {}).values())
        or any(registry.get("access_counters", {}).values())
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "native registry semantics differ"
        )
    bindings = registry.get("tracked_file_hashes")
    if not isinstance(bindings, list) or len(bindings) < 10:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "native registry bindings differ"
        )
    seen: set[str] = set()
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[0], "native registry binding shape differs"
            )
        value = str(binding["path"])
        relative = _validate_relative_path(value, allow_codex_work=False)
        digest = str(binding["sha256"])
        if (
            value in seen
            or relative == NATIVE_REGISTRY_RELATIVE_PATH
            or relative == PROOF_CERTIFICATE_RELATIVE_PATH
            or HEX64_RE.fullmatch(digest) is None
            or _sha256_file(root / relative) != digest
        ):
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[0], "native registry binding differs"
            )
        seen.add(value)
    return registry


def _generated_proof(payload: bytes) -> shared_proof.ProofEnvelope:
    commit = "a" * 40
    return shared_proof.ProofEnvelope(
        implementation_commit=commit,
        implementation_CI_run_id=1,
        implementation_base_job_id=2,
        implementation_optional_job_id=3,
        implementation_registry_sha256=_sha256_bytes(payload),
        observed_HEAD=commit,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )


def _load_certificate_bytes(root: Path) -> bytes:
    path = root / PROOF_CERTIFICATE_RELATIVE_PATH
    try:
        info = path.lstat()
        payload = path.read_bytes()
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "proof certificate is unavailable"
        ) from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or len(payload) != info.st_size
        or len(payload) > 1024**2
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "proof certificate shape differs"
        )
    return payload


def _validate_certificate_generated(root: Path, payload: bytes) -> None:
    proof = _generated_proof(payload)
    try:
        shared_proof.validate_implementation_record(
            payload,
            repo_root=root,
            expected_proof=proof,
            observed_proof=proof,
            generated_closure=shared_proof.validate_implementation_record,
        )
    except shared_proof.ProofRecordRefusal as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "shared proof certificate refused"
        ) from exc


def _mutable_container_ids(value: Any) -> set[int]:
    observed: set[int] = set()

    def walk(current: Any) -> None:
        if isinstance(current, dict):
            if id(current) in observed:
                return
            observed.add(id(current))
            for nested in current.values():
                walk(nested)
        elif isinstance(current, list):
            if id(current) in observed:
                return
            observed.add(id(current))
            for nested in current:
                walk(nested)
        elif isinstance(current, set):
            observed.add(id(current))

    walk(value)
    return observed


def _adapt_once(
    source: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    adapter: Callable[..., domain_adapter.AdaptedLiveDomain] = (
        domain_adapter.adapt_live_domain_source
    ),
) -> domain_adapter.AdaptedLiveDomain:
    before = domain_adapter._canonical_source_bytes(source)
    before_structure = domain_adapter._canonical_json_bytes(source)
    source_ids = _mutable_container_ids(source)
    try:
        result = adapter(source, contract=contract)
    except domain_adapter.LiveDomainEligibilityRefusal as exc:
        route = REFUSAL_ROUTES[4] if exc.route == "MARC2VR2-F06" else REFUSAL_ROUTES[3]
        raise VariableDomainPrivateRecoveryRefusal(
            route, "VR2 adapter refused the source"
        ) from exc
    after = domain_adapter._canonical_source_bytes(source)
    after_structure = domain_adapter._canonical_json_bytes(source)
    if before != after or before_structure != after_structure:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[3], "source changed during adaptation"
        )
    result_ids = _mutable_container_ids(result.selection.private_manifest)
    if source_ids & result_ids:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[3], "mutable source alias survived adaptation"
        )
    if (
        sum(result.predicate_counts.values()) != EXPECTED_SOURCE_BUNDLES
        or result.predicate_counts.get(domain_adapter.PREDICATE_CODES[0])
        != EXPECTED_ELIGIBLE_BUNDLES
        or sum(
            result.predicate_counts.get(code, 0)
            for code in domain_adapter.PREDICATE_CODES[1:]
        )
        != EXPECTED_INELIGIBLE_BUNDLES
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[3], "predicate arithmetic differs"
        )
    _validate_selection(result)
    return result


def _validate_selection(result: domain_adapter.AdaptedLiveDomain) -> None:
    selection = result.selection
    cohort = selection.cohort_summary
    split = selection.split_summary
    byte_summary = selection.byte_summary
    subjects = cohort.get("selected_subject_ids")
    if (
        not isinstance(subjects, list)
        or not 12 <= len(subjects) <= 19
        or cohort.get("selected_subjects") != len(subjects)
        or cohort.get("selection_is_maximal_contiguous_rank_prefix") is not True
        or cohort.get("selection_was_target_quality_and_outcome_free") is not True
        or split.get("fit_session") != "ses-01"
        or split.get("heldout_session") != "ses-02"
        or split.get("selected_run_bundles") != len(subjects) * 6
        or split.get("selected_core_members") != len(subjects) * 24
        or split.get("fit_heldout_overlap") != 0
        or split.get("row_random_split_used") is not False
        or byte_summary.get("reservation_cap_bytes") != RESERVATION_CAP_BYTES
        or byte_summary.get("selected_reservation_bytes", RESERVATION_CAP_BYTES + 1)
        > RESERVATION_CAP_BYTES
        or byte_summary.get("fallback_or_budget_increase_used") is not False
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[4], "selection split or reservation differs"
        )


def _walk_aggregate(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if key in FORBIDDEN_AGGREGATE_KEYS:
                raise VariableDomainPrivateRecoveryRefusal(
                    REFUSAL_ROUTES[5], "aggregate report exposes a private field"
                )
            _walk_aggregate(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_aggregate(nested)
    elif isinstance(value, str):
        if ".codex_work/" in value or "Freewill_" in value or "member_inventory" in value:
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[5], "aggregate report exposes a private value"
            )


def validate_aggregate_report(report: Mapping[str, Any]) -> None:
    if (
        not isinstance(report, dict)
        or set(report) != AGGREGATE_TOP_LEVEL_FIELDS
        or report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") not in {GENERATED_ROUTE, SUCCESS_ROUTE}
        or not all(report.get("acceptance_gates", {}).values())
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "aggregate report semantics differ"
        )
    _walk_aggregate(report)
    measurements = report.get("measurements", {})
    if (
        measurements.get("runtime_seconds", MAX_RUNTIME_SECONDS + 1)
        > MAX_RUNTIME_SECONDS
        or measurements.get("peak_RSS_bytes", MAX_PEAK_RSS_BYTES + 1)
        > MAX_PEAK_RSS_BYTES
        or measurements.get("output_bytes", MAX_COMBINED_OUTPUT_BYTES + 1)
        > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[6], "aggregate resource measurement differs"
        )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    observed = environment if environment is not None else os.environ
    if any(observed.get(key) != "1" for key in THREAD_ENVIRONMENT):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "thread environment differs"
        )


def _assert_resources(
    *, runtime_seconds: float, peak_rss_bytes: int, input_bytes: int, output_bytes: int
) -> None:
    values = (runtime_seconds, peak_rss_bytes, input_bytes, output_bytes)
    if any(isinstance(value, bool) or not math.isfinite(float(value)) or value < 0 for value in values):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[6], "resource measurement is malformed"
        )
    if (
        runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or output_bytes > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[6], "resource cap exceeded"
        )


def _expect_refusal(name: str, action: Callable[[], Any]) -> str:
    expected = WRAPPER_MUTATION_ROUTES[name]
    try:
        action()
    except VariableDomainPrivateRecoveryRefusal as exc:
        if exc.route != expected:
            raise AssertionError(f"{name} routed {exc.route}, expected {expected}") from exc
        return exc.route
    raise AssertionError(f"required wrapper mutation did not refuse: {name}")


def _exercise_wrapper_mutation(name: str, expected: str) -> None:
    if name == "duplicate_JSON_key":
        _strict_json(b'{"value":1,"value":2}')
    elif name == "aggregate_private_field_leak":
        _walk_aggregate({"member_name": "forbidden"})
    elif name == "thread_environment_drift":
        environment = {key: "1" for key in THREAD_ENVIRONMENT}
        environment[THREAD_ENVIRONMENT[0]] = "2"
        _validate_thread_environment(environment)
    else:
        raise VariableDomainPrivateRecoveryRefusal(expected, "generated mutation")


def run_wrapper_mutation_matrix() -> dict[str, str]:
    """Exercise all 32 wrapper refusal identities without a retained path."""

    routes: dict[str, str] = {}
    for name, expected in WRAPPER_MUTATION_ROUTES.items():
        routes[name] = _expect_refusal(
            name, partial(_exercise_wrapper_mutation, name, expected)
        )
    return routes


def _zero_generated_access_counters() -> dict[str, int]:
    return {
        "registered_output_root_operations": 0,
        "retained_private_path_operations": 0,
        "retained_private_manifest_opens": 0,
        "retained_private_manifest_bytes": 0,
        "old_consumed_executor_or_root_operations": 0,
        "network_requests": 0,
        "network_bytes": 0,
        "archive_local_header_or_member_payload_reads": 0,
        "signal_sample_reads": 0,
        "event_target_label_quality_onset_or_channel_reads": 0,
        "real_derivative_rows": 0,
        "training_or_parameter_update_fits": 0,
        "model_inference_or_prediction_sets": 0,
        "prediction_freezes_target_deliveries_or_scores": 0,
        "provider_or_language_model_calls": 0,
        "hardware_operations": 0,
        "retries_reruns_or_resumes": 0,
        "release_or_publication_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _settle_generated_report(report: dict[str, Any]) -> bytes:
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        if report["measurements"]["output_bytes"] == len(payload):
            return payload
        report["measurements"]["output_bytes"] = len(payload)
    raise VariableDomainPrivateRecoveryRefusal(
        REFUSAL_ROUTES[6], "generated output size did not settle"
    )


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Qualify the proof and wrapper entirely on generated in-memory sources."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    _validate_decision_and_request(root)
    _load_native_registry(root)
    certificate_payload = _load_certificate_bytes(root)
    certificate = shared_proof.parse_record_bytes(certificate_payload)
    _validate_certificate_generated(root, certificate_payload)
    _validate_certificate_generated(root, certificate_payload)
    try:
        proof_mutations = shared_proof.run_generated_mutation_matrix(
            certificate, repo_root=root
        )
    except shared_proof.ProofRecordRefusal as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "shared proof mutation matrix refused"
        ) from exc
    contract = domain_adapter.load_registered_contract(root)
    selection_identities: set[str] = set()
    profile_source_hashes: dict[str, set[str]] = {
        profile: set() for profile in ("A", "B", "C", "D")
    }
    success_rows: list[dict[str, Any]] = []
    generated_input_bytes = len(certificate_payload)
    selected_result: domain_adapter.AdaptedLiveDomain | None = None
    for profile in profile_source_hashes:
        for row_order in ("canonical", "reversed"):
            source = domain_adapter.build_generated_live_source(
                profile=profile,
                row_order=row_order,
                contract=contract,
            )
            source_bytes = domain_adapter._canonical_source_bytes(source)
            generated_input_bytes += len(source_bytes)
            result = _adapt_once(source, contract=contract)
            selected_result = result
            identity = result.selection.selection_hashes[
                "selection_identity_sha256"
            ]
            selection_identities.add(identity)
            profile_source_hashes[profile].add(result.source_sha256)
            success_rows.append(
                {
                    "profile": profile,
                    "row_order": row_order,
                    "predicate_counts": dict(result.predicate_counts),
                    "source_sha256": result.source_sha256,
                    "selection_identity_sha256": identity,
                }
            )
    if selected_result is None or len(selection_identities) != 1 or any(
        len(values) != 1 for values in profile_source_hashes.values()
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[4], "generated replay identity differs"
        )
    wrapper_mutations = run_wrapper_mutation_matrix()
    runtime = clock() - started
    peak_rss = int(rss_reader())
    selection = selected_result.selection
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_mock_wrapper_qualification_passed",
        "route": GENERATED_ROUTE,
        "proof_posture": "generated_structural_metadata_only_no_private_authority",
        "source_summary": {
            "generated_success_paths": len(success_rows),
            "generated_profiles": 4,
            "row_orders_per_profile": 2,
            "inventory_rows": EXPECTED_ROWS,
            "complete_source_run_bundles": EXPECTED_SOURCE_BUNDLES,
            "eligible_run_bundles": EXPECTED_ELIGIBLE_BUNDLES,
            "valid_ineligible_run_bundles": EXPECTED_INELIGIBLE_BUNDLES,
            "private_source_identity_used": False,
        },
        "cohort_summary": dict(selection.cohort_summary),
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
        "selection_hashes": {
            "selection_identity_sha256": next(iter(selection_identities)),
            "proof_certificate_sha256": _sha256_bytes(certificate_payload),
            "native_registry_sha256": _sha256_file(
                root / NATIVE_REGISTRY_RELATIVE_PATH
            ),
        },
        "measurements": {
            "input_bytes": generated_input_bytes,
            "output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "valid_token_count": "not_applicable_structural_metadata",
            "padding_fraction": "not_applicable_structural_metadata",
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "resource_caps": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": MAX_RUNTIME_SECONDS,
            "peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
            "combined_output_bytes": MAX_COMBINED_OUTPUT_BYTES,
            "network_bytes": 0,
            "archive_member_bytes": 0,
        },
        "access_counters": _zero_generated_access_counters(),
        "acceptance_gates": {
            "green_packet_bound_decision": True,
            "exact_shared_validator_called_34_times": len(proof_mutations) + 2 == 34,
            "all_32_proof_mutations_refused": len(proof_mutations) == 32,
            "all_32_wrapper_mutations_refused": len(wrapper_mutations) == 32,
            "all_eight_profile_order_paths_passed": len(success_rows) == 8,
            "full_238_bundle_domain_validated_before_filter": True,
            "dynamic_195_plus_43_reconciliation": True,
            "exact_one_adapter_call_per_success_path": True,
            "source_immutability_and_no_mutable_alias": True,
            "selection_replay_is_byte_stable": len(selection_identities) == 1,
            "zero_retained_generated_output": True,
            "zero_private_archive_neural_target_model_score_operations": True,
            "one_thread_runtime_RSS_and_output_caps": True,
        },
        "warnings": [
            "All source rows in this qualification are generated fixtures.",
            "The private structural manifest was not statted opened hashed or parsed.",
            "A structural selection is not neural or decoding evidence.",
        ],
        "unavailable_fields": [
            "real cohort identity",
            "real ineligible predicate distribution",
            "signal samples events targets channels and geometry",
            "model predictions scores and end-to-end latency",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "A proof-gated wrapper can validate the full variable structural "
                "domain and freeze a target-free cohort without a payload read."
            ),
            "scientific_claim_not_established": (
                "Generated metadata contain no human neural data target prediction "
                "or score and establish no neural effect decoding or thought-to-text result."
            ),
        },
    }
    payload = _settle_generated_report(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        input_bytes=generated_input_bytes,
        output_bytes=len(payload),
    )
    validate_aggregate_report(report)
    return report


def _git_output(root: Path, args: Sequence[str]) -> str:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "Git proof check failed"
        ) from exc
    return completed.stdout.strip()


def _verify_execution_proof(root: Path, evidence: ExecutionEvidence) -> None:
    if (
        HEX40_RE.fullmatch(evidence.implementation_commit) is None
        or min(
            evidence.CI_run_id,
            evidence.base_python_job_id,
            evidence.optional_neuro_job_id,
        )
        <= 0
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation proof is malformed"
        )
    head = _git_output(root, ["rev-parse", "HEAD"])
    if head != evidence.implementation_commit:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "implementation HEAD differs"
        )
    if _git_output(root, ["status", "--porcelain", "--untracked-files=no"]):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "tracked worktree is not clean"
        )
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", DECISION_COMMIT, head],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "decision ancestry differs"
        ) from exc
    _validate_decision_and_request(root)
    _load_native_registry(root)
    certificate_payload = _load_certificate_bytes(root)
    proof = shared_proof.ProofEnvelope(
        implementation_commit=head,
        implementation_CI_run_id=evidence.CI_run_id,
        implementation_base_job_id=evidence.base_python_job_id,
        implementation_optional_job_id=evidence.optional_neuro_job_id,
        implementation_registry_sha256=_sha256_bytes(certificate_payload),
        observed_HEAD=head,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )
    try:
        shared_proof.validate_implementation_record(
            certificate_payload,
            repo_root=root,
            expected_proof=proof,
            observed_proof=proof,
            generated_closure=shared_proof.validate_implementation_record,
        )
    except shared_proof.ProofRecordRefusal as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[0], "remote-green certificate proof refused"
        ) from exc


def _machine_preflight(
    root: Path,
    *,
    load_reader: Callable[[], tuple[float, float, float]] = os.getloadavg,
    cpu_reader: Callable[[], int | None] = os.cpu_count,
    disk_reader: Callable[[Path], shutil._ntuple_diskusage] = shutil.disk_usage,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    _validate_thread_environment()
    logical_cpus = int(cpu_reader() or 0)
    if logical_cpus < 1:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "logical CPU count is unavailable"
        )
    normalized_load = float(load_reader()[0]) / logical_cpus
    free_disk = int(disk_reader(root).free)
    rss = int(rss_reader())
    if (
        not math.isfinite(normalized_load)
        or normalized_load > MAX_NORMALIZED_LOAD
        or free_disk < MINIMUM_FREE_DISK_BYTES
        or rss > MAX_PEAK_RSS_BYTES
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "machine resource preflight refused"
        )
    return {
        "logical_CPUs": logical_cpus,
        "normalized_one_minute_load": normalized_load,
        "free_disk_bytes": free_disk,
        "preflight_RSS_bytes": rss,
    }


def _preflight_relative_regular_file(
    root: Path,
    relative: Path,
    *,
    expected_size: int,
    expected_mode: int,
    expected_uid: int,
) -> tuple[Path, os.stat_result, int]:
    if relative.is_absolute() or ".." in relative.parts:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "source path differs"
        )
    current = root
    checks = 0
    for part in relative.parts:
        current = current / part
        try:
            info = os.lstat(current)
        except OSError as exc:
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[1], "source path is unavailable"
            ) from exc
        checks += 1
        if stat.S_ISLNK(info.st_mode):
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[1], "source path contains a symlink"
            )
    if (
        not stat.S_ISREG(info.st_mode)
        or stat.S_IMODE(info.st_mode) != expected_mode
        or info.st_uid != expected_uid
        or info.st_size != expected_size
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "source file preflight differs"
        )
    return current, info, checks


def _read_source_once(
    path: Path,
    expected_info: os.stat_result,
    *,
    expected_sha256: str,
    expected_size: int,
    component_checks: int,
) -> SourceRead:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[1], "O_NOFOLLOW is unavailable"
        )
    try:
        descriptor = os.open(path, os.O_RDONLY | nofollow)
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[2], "no-follow source open failed"
        ) from exc
    chunks: list[bytes] = []
    digest = hashlib.sha256()
    observed = 0
    try:
        opened = os.fstat(descriptor)
        if (
            opened.st_dev != expected_info.st_dev
            or opened.st_ino != expected_info.st_ino
            or opened.st_size != expected_info.st_size
            or opened.st_uid != expected_info.st_uid
            or stat.S_IMODE(opened.st_mode) != stat.S_IMODE(expected_info.st_mode)
            or not stat.S_ISREG(opened.st_mode)
        ):
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[2], "open/fstat source identity differs"
            )
        while observed <= expected_size:
            chunk = os.read(descriptor, min(64 * 1024, expected_size + 1 - observed))
            if not chunk:
                break
            observed += len(chunk)
            chunks.append(chunk)
            digest.update(chunk)
    finally:
        os.close(descriptor)
    if observed != expected_size or digest.hexdigest() != expected_sha256:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[2], "source size or SHA-256 differs"
        )
    payload = b"".join(chunks)
    source = _strict_json(payload)
    return SourceRead(
        source=source,
        payload_sha256=digest.hexdigest(),
        bytes_read=observed,
        component_checks=component_checks,
    )


def _prepare_output_root(root: Path) -> Path:
    relative = OUTPUT_ROOT_RELATIVE_PATH
    current = root
    for index, part in enumerate(relative.parts):
        current = current / part
        is_final = index == len(relative.parts) - 1
        try:
            info = os.lstat(current)
        except FileNotFoundError:
            if is_final:
                try:
                    os.mkdir(current, 0o700)
                except OSError as exc:
                    raise VariableDomainPrivateRecoveryRefusal(
                        REFUSAL_ROUTES[1], "output root creation failed"
                    ) from exc
                return current
            if part != "marc2_live_domain_private_recovery":
                raise VariableDomainPrivateRecoveryRefusal(
                    REFUSAL_ROUTES[1], "output parent is unavailable"
                )
            try:
                os.mkdir(current, 0o700)
            except OSError as exc:
                raise VariableDomainPrivateRecoveryRefusal(
                    REFUSAL_ROUTES[1], "output parent creation failed"
                ) from exc
            continue
        except OSError as exc:
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[1], "output path preflight failed"
            ) from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[1], "output path contains a non-directory"
            )
        if is_final:
            raise VariableDomainPrivateRecoveryRefusal(
                REFUSAL_ROUTES[1], "output root already exists"
            )
    raise VariableDomainPrivateRecoveryRefusal(
        REFUSAL_ROUTES[1], "output root preflight did not settle"
    )


def _write_new_file(path: Path, payload: bytes, *, mode: int) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    try:
        descriptor = os.open(path, flags | nofollow, mode)
        written = 0
        while written < len(payload):
            written += os.write(descriptor, payload[written:])
        os.fsync(descriptor)
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "bounded output write failed"
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if stat.S_IMODE(os.lstat(path).st_mode) != mode:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "bounded output mode differs"
        )


def _marker_payload(evidence: ExecutionEvidence) -> bytes:
    return _canonical_json_bytes(
        {
            "schema_name": MARKER_SCHEMA_NAME,
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "consumed_before_private_content_open",
            "implementation_commit": evidence.implementation_commit,
            "retry_rerun_resume_repair_or_fallback_limit": 0,
        }
    )


def _private_manifest(
    result: domain_adapter.AdaptedLiveDomain,
) -> dict[str, Any]:
    rows = copy.deepcopy(result.selection.private_manifest.get("rows"))
    if not isinstance(rows, list):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[4], "private selection rows are unavailable"
        )
    return {
        "schema_name": PRIVATE_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "proof_posture": "real_structural_metadata_target_free_no_payload_read",
        "source_sha256": result.source_sha256,
        "selection_identity_sha256": result.selection.selection_hashes[
            "selection_identity_sha256"
        ],
        "fit_session": "ses-01",
        "heldout_session": "ses-02",
        "rows": rows,
    }


def _real_access_counters(source: SourceRead) -> dict[str, int]:
    return {
        "registered_output_root_operations": 1,
        "retained_private_path_component_checks": source.component_checks,
        "retained_private_manifest_opens": 1,
        "retained_private_manifest_bytes": source.bytes_read,
        "retained_private_manifest_hashes": 1,
        "retained_private_manifest_parses": 1,
        "real_structural_participant_selections": 1,
        "real_structural_member_selections": 1,
        "old_consumed_executor_or_root_operations": 0,
        "network_requests": 0,
        "network_bytes": 0,
        "archive_local_header_or_member_payload_reads": 0,
        "signal_sample_reads": 0,
        "event_target_label_quality_onset_or_channel_reads": 0,
        "real_derivative_rows": 0,
        "training_or_parameter_update_fits": 0,
        "model_inference_or_prediction_sets": 0,
        "prediction_freezes_target_deliveries_or_scores": 0,
        "provider_or_language_model_calls": 0,
        "hardware_operations": 0,
        "retries_reruns_or_resumes": 0,
        "release_or_publication_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _settle_real_report(
    report: dict[str, Any], *, marker_bytes: int, private_bytes: int
) -> bytes:
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        combined = marker_bytes + private_bytes + len(payload)
        if report["measurements"]["output_bytes"] == combined:
            return payload
        report["measurements"]["output_bytes"] = combined
    raise VariableDomainPrivateRecoveryRefusal(
        REFUSAL_ROUTES[5], "real output size did not settle"
    )


def _build_real_report(
    result: domain_adapter.AdaptedLiveDomain,
    source: SourceRead,
    machine: Mapping[str, Any],
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    marker_bytes: int,
    private_bytes: int,
    private_sha256: str,
) -> tuple[dict[str, Any], bytes]:
    selection = result.selection
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "real_target_free_structural_cohort_frozen",
        "route": SUCCESS_ROUTE,
        "proof_posture": "real_structural_metadata_only_no_archive_member_or_neural_read",
        "source_summary": {
            "input_bytes": source.bytes_read,
            "input_sha256": source.payload_sha256,
            "inventory_rows": EXPECTED_ROWS,
            "regular_file_rows": EXPECTED_FILES,
            "directory_rows": EXPECTED_DIRECTORIES,
            "complete_source_run_bundles": EXPECTED_SOURCE_BUNDLES,
            "eligible_run_bundles": EXPECTED_ELIGIBLE_BUNDLES,
            "valid_ineligible_run_bundles": EXPECTED_INELIGIBLE_BUNDLES,
            "predicate_counts": dict(result.predicate_counts),
            "full_source_validated_before_filter": True,
            "exact_ineligible_breakdown_assumed_before_read": False,
        },
        "cohort_summary": dict(selection.cohort_summary),
        "split_summary": dict(selection.split_summary),
        "byte_summary": dict(selection.byte_summary),
        "selection_hashes": {
            "source_sha256": result.source_sha256,
            "selection_identity_sha256": selection.selection_hashes[
                "selection_identity_sha256"
            ],
            "private_selection_manifest_sha256": private_sha256,
        },
        "measurements": {
            "input_bytes": source.bytes_read,
            "output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "normalized_one_minute_load": machine["normalized_one_minute_load"],
            "free_disk_bytes_before_execution": machine["free_disk_bytes"],
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "valid_token_count": "not_applicable_structural_metadata",
            "padding_fraction": "not_applicable_structural_metadata",
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "resource_caps": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": MAX_RUNTIME_SECONDS,
            "peak_RSS_bytes": MAX_PEAK_RSS_BYTES,
            "private_input_bytes": EXPECTED_PRIVATE_BYTES,
            "combined_output_bytes": MAX_COMBINED_OUTPUT_BYTES,
            "incremental_disk_bytes": MAX_INCREMENTAL_DISK_BYTES,
            "minimum_free_disk_bytes": MINIMUM_FREE_DISK_BYTES,
            "network_bytes": 0,
            "archive_member_bytes": 0,
            "future_reservation_cap_bytes": RESERVATION_CAP_BYTES,
        },
        "access_counters": _real_access_counters(source),
        "acceptance_gates": {
            "exact_remote_green_wrapper_proof": True,
            "one_no_follow_source_open": True,
            "exact_source_size_and_SHA256": True,
            "strict_duplicate_key_JSON_parse": True,
            "all_1227_rows_and_238_bundles_validated_before_filter": True,
            "dynamic_195_plus_43_reconciliation": True,
            "exact_one_VR2_adapter_call": True,
            "source_immutability_and_no_mutable_alias": True,
            "frozen_target_free_selector_result": True,
            "maximal_contiguous_rank_prefix_under_8_GiB": True,
            "fit_ses01_heldout_ses02_no_overlap": True,
            "aggregate_private_output_separation": True,
            "zero_archive_neural_target_model_score_operations": True,
            "one_thread_runtime_RSS_disk_and_output_caps": True,
        },
        "warnings": [
            "This result freezes structural cohort membership only.",
            "No archive member local header signal sample event target or channel was read.",
            "The selected reservation is accounting and no payload was downloaded or extracted.",
            "A structural cohort is not neural evidence or a decoding result.",
        ],
        "unavailable_fields": [
            "signal samples and channel geometry",
            "events targets timing and quality",
            "neural features predictions scores and end-to-end latency",
            "brain-specific language or thought-to-text evidence",
        ],
        "claim_boundary": {
            "engineering_capability_added": (
                "One exact real structural manifest now yields a frozen target-free "
                "participant and member cohort under the registered storage ceiling."
            ),
            "scientific_claim_not_established": (
                "No neural payload target prediction or score was accessed, so this "
                "result establishes no neural effect decoding or thought-to-text capability."
            ),
        },
    }
    payload = _settle_real_report(
        report, marker_bytes=marker_bytes, private_bytes=private_bytes
    )
    validate_aggregate_report(report)
    return report, payload


def execute_registered(
    evidence: ExecutionEvidence,
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> ExecutionOutcome:
    """Consume the one fixed private structural pass and freeze its cohort."""

    started = clock()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    _verify_execution_proof(root, evidence)
    machine = _machine_preflight(root, rss_reader=rss_reader)
    output_root = _prepare_output_root(root)
    source_path, source_info, checks = _preflight_relative_regular_file(
        root,
        PRIVATE_SOURCE_RELATIVE_PATH,
        expected_size=EXPECTED_PRIVATE_BYTES,
        expected_mode=EXPECTED_PRIVATE_MODE,
        expected_uid=os.getuid(),
    )
    marker_payload = _marker_payload(evidence)
    _write_new_file(output_root / MARKER_NAME, marker_payload, mode=0o600)
    source = _read_source_once(
        source_path,
        source_info,
        expected_sha256=EXPECTED_PRIVATE_SHA256,
        expected_size=EXPECTED_PRIVATE_BYTES,
        component_checks=checks,
    )
    contract = domain_adapter.load_registered_contract(root)
    result = _adapt_once(source.source, contract=contract)
    private_manifest = _private_manifest(result)
    private_payload = _canonical_json_bytes(private_manifest)
    private_sha256 = _sha256_bytes(private_payload)
    runtime = clock() - started
    peak_rss = int(rss_reader())
    report, report_payload = _build_real_report(
        result,
        source,
        machine,
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        marker_bytes=len(marker_payload),
        private_bytes=len(private_payload),
        private_sha256=private_sha256,
    )
    combined_output = len(marker_payload) + len(private_payload) + len(report_payload)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=peak_rss,
        input_bytes=source.bytes_read,
        output_bytes=combined_output,
    )
    if combined_output > MAX_INCREMENTAL_DISK_BYTES:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "incremental output exceeds cap"
        )
    _write_new_file(
        output_root / PRIVATE_MANIFEST_NAME, private_payload, mode=0o600
    )
    _write_new_file(
        output_root / AGGREGATE_REPORT_NAME, report_payload, mode=0o644
    )
    if len(tuple(output_root.iterdir())) != 3:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "output file inventory differs"
        )
    return ExecutionOutcome(
        report=report,
        private_manifest_sha256=private_sha256,
        marker_bytes=len(marker_payload),
        private_output_bytes=len(private_payload),
        aggregate_output_bytes=len(report_payload),
    )


def inspect_aggregate_report(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate report while refusing the private schema."""

    report_path = Path(path)
    if report_path.name != AGGREGATE_REPORT_NAME:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "aggregate report filename differs"
        )
    try:
        info = report_path.lstat()
        payload = report_path.read_bytes()
    except OSError as exc:
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "aggregate report is unavailable"
        ) from exc
    if (
        stat.S_ISLNK(info.st_mode)
        or not stat.S_ISREG(info.st_mode)
        or len(payload) != info.st_size
        or len(payload) > MAX_COMBINED_OUTPUT_BYTES
    ):
        raise VariableDomainPrivateRecoveryRefusal(
            REFUSAL_ROUTES[5], "aggregate report shape differs"
        )
    report = _strict_json(payload, route=REFUSAL_ROUTES[5])
    validate_aggregate_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.marc2_variable_domain_private_recovery_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "commands": ["plan", "qualify", "inspect", "execute"],
        "generated_success_paths": 8,
        "proof_certificate_mutations": 32,
        "wrapper_mutations": 32,
        "private_execution_limit": 1,
        "private_input_bytes": EXPECTED_PRIVATE_BYTES,
        "archive_member_bytes": 0,
        "MARC2_FW2_authorized": False,
        "scientific_value_of_plan": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_variable_domain_private_recovery",
        description="Proof-gate one target-free MARC2 structural cohort freeze.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="Print the fixed wrapper plan.")
    subparsers.add_parser("qualify", help="Run generated proof and wrapper checks.")
    inspect = subparsers.add_parser(
        "inspect", help="Inspect one aggregate report, never a private manifest."
    )
    inspect.add_argument("--report", required=True, type=Path)
    execute = subparsers.add_parser(
        "execute", help="Run the one fixed pass after exact remote-green proof."
    )
    execute.add_argument("--implementation-commit", required=True)
    execute.add_argument("--ci-run-id", required=True, type=int)
    execute.add_argument("--base-job-id", required=True, type=int)
    execute.add_argument("--optional-job-id", required=True, type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            output: Mapping[str, Any] = build_plan_summary()
        elif args.command == "qualify":
            output = qualify_generated()
        elif args.command == "inspect":
            output = inspect_aggregate_report(args.report)
        else:
            evidence = ExecutionEvidence(
                implementation_commit=args.implementation_commit,
                CI_run_id=args.ci_run_id,
                base_python_job_id=args.base_job_id,
                optional_neuro_job_id=args.optional_job_id,
            )
            output = execute_registered(evidence).report
    except VariableDomainPrivateRecoveryRefusal as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
