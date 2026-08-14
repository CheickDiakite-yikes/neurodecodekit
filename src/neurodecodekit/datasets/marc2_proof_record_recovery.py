"""Generated-only MARC2-FW1B implementation-record recovery."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import resource
import stat
import sys
import time
from dataclasses import asdict, dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-FW1B"
MODULE_NAME = "neurodecodekit.datasets.marc2_proof_record_recovery"
GENERATED_ROUTE = "MARC2FWR-G1"
FAILURE_ROUTES = tuple(f"MARC2FWR-F0{index}" for index in range(6))

CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_proof_record_recovery_contract.v0.json"
)
CONTRACT_SHA256 = "0ec54f915289fd66983696bd28c2eb799c59703d1d5ccebece628f83da8b1e4b"
GREEN_CONTRACT_COMMIT = "b86aa940d47a232535ee1e72fb22ad58ea5c2729"
GREEN_CONTRACT_CI_RUN_ID = 31_767_373_647
GREEN_CONTRACT_BASE_JOB_ID = 94_665_902_722
GREEN_CONTRACT_OPTIONAL_JOB_ID = 94_665_902_761

IMPLEMENTATION_REGISTRY_RELATIVE_PATH = Path(
    "registries/marc2_proof_record_recovery_implementation.v0.json"
)
MODULE_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_proof_record_recovery.py"
)
REPORT_NAME = "marc2_proof_record_recovery_qualification.v0.json"

MAX_RUNTIME_SECONDS = 30.0
MAX_PEAK_RSS_BYTES = 256 * 1024**2
MAX_GENERATED_INPUT_BYTES = 1024**2
MAX_COMBINED_OUTPUT_BYTES = 1024**2
MAX_INCREMENTAL_DISK_BYTES = 2 * 1024**2

HEX40_RE = re.compile(r"[0-9a-f]{40}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
EXPECTED_TOP_LEVEL_FIELDS = (
    "schema_name",
    "schema_version",
    "lane_id",
    "implementation_id",
    "recorded_at_local",
    "status",
    "predecessor_proof",
    "tracked_file_hashes",
    "implementation_surface",
    "generated_qualification",
    "execution_state",
    "authorization_flags",
    "access_counters",
    "next_gate",
    "claim_boundary",
)
ORDERED_MUTATIONS = (
    "schema_name_missing",
    "schema_name_wrong",
    "schema_version_wrong",
    "lane_id_missing",
    "lane_id_wrong",
    "implementation_id_wrong",
    "status_wrong",
    "predecessor_commit_wrong",
    "predecessor_CI_or_job_wrong",
    "predecessor_result_hash_wrong",
    "tracked_files_empty",
    "tracked_path_absolute",
    "tracked_path_traversal",
    "tracked_path_duplicate",
    "tracked_hash_malformed",
    "tracked_hash_mismatch",
    "registry_self_binding",
    "qualification_all_gates_false",
    "qualification_selector_count_wrong",
    "qualification_wrapper_count_wrong",
    "qualification_mutation_order_wrong",
    "execution_already_consumed",
    "execution_limit_wrong",
    "retry_limit_nonzero",
    "access_counter_nonzero",
    "private_authority_enabled",
    "payload_or_MARC2_FW2_authority_enabled",
    "next_gate_wrong",
    "claim_boundary_missing",
    "proof_commit_malformed_or_HEAD_mismatch",
    "proof_CI_job_or_registry_hash_mismatch",
    "generated_closure_uses_different_validator",
)
DEFAULT_TRACKED_ARTIFACTS = (
    MODULE_RELATIVE_PATH,
    CONTRACT_RELATIVE_PATH,
    Path("docs/MARC_2_PROOF_RECORD_RECOVERY_PREREGISTRATION.md"),
    Path("tests/test_marc2_proof_record_recovery_contract.py"),
)
EXPECTED_EXECUTION_STATE = {
    "registered_private_execution_consumed": False,
    "registered_private_execution_limit": 0,
    "retry_rerun_resume_repair_or_fallback_limit": 0,
    "private_selection_result_available": False,
    "MARC2_FW2_eligible": False,
}
EXPECTED_NEXT_GATE = {
    "implementation_commit_push_and_both_remote_jobs_green_required": True,
    "private_access_authorized_now": False,
    "all_false_Tier_C_request_only_after_green_implementation": True,
    "fresh_packet_bound_decision_required_before_live_wrapper": True,
    "live_wrapper_remote_green_required_before_private_path": True,
    "MARC2_FW2_eligible_now": False,
    "earlier_continue_is_retroactive_authority": False,
}
PUBLIC_REPORT_FIELDS = frozenset(
    {
        "schema_name",
        "schema_version",
        "lane_id",
        "status",
        "route",
        "proof_posture",
        "green_contract_proof",
        "candidate_summary",
        "shared_validator",
        "mutation_summary",
        "replay_summary",
        "measurements",
        "access_counters",
        "acceptance_gates",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
)


class ProofRecordRefusal(RuntimeError):
    """Fail closed with one stable aggregate-safe MARC2-FW1B route."""

    def __init__(self, route: str, reason: str):
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-FW1B failure route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class ProofEnvelope:
    """Expected or observed remote proof supplied to the shared validator."""

    implementation_commit: str
    implementation_CI_run_id: int
    implementation_base_job_id: int
    implementation_optional_job_id: int
    implementation_registry_sha256: str
    observed_HEAD: str
    tracked_worktree_clean: bool
    green_decision_ancestor: bool


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    """Deterministic aggregate result from one accepted record."""

    lane_id: str
    record_sha256: str
    top_level_field_count: int
    tracked_binding_count: int
    validator_module: str
    validator_symbol: str
    validator_source_sha256: str
    implementation_commit: str

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QualificationOutcome:
    """One generated qualification and exact-cleanup result."""

    report: Mapping[str, Any]
    report_bytes: bytes
    report_sha256: str
    mutation_routes: Mapping[str, str]
    runtime_seconds: float
    peak_rss_bytes: int
    generated_input_bytes: int
    generated_output_bytes: int
    output_removed: bool


def _repo_root() -> Path:
    return Path(__file__).parents[3]


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


def _record_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=False,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("ascii")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_regular_bytes(path: Path, maximum_bytes: int) -> bytes:
    try:
        before = os.lstat(path)
    except OSError as exc:
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked artifact unavailable") from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked artifact type differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    payload = bytearray()
    try:
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if (
                opened.st_dev != before.st_dev
                or opened.st_ino != before.st_ino
                or opened.st_size != before.st_size
            ):
                raise ProofRecordRefusal(
                    "MARC2FWR-F01", "tracked artifact identity changed"
                )
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
    except ProofRecordRefusal:
        raise
    except OSError as exc:
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked artifact open failed") from exc
    if len(payload) > maximum_bytes or len(payload) != before.st_size:
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked artifact size differs")
    return bytes(payload)


def _sha256_file(path: Path, maximum_bytes: int = MAX_GENERATED_INPUT_BYTES) -> str:
    return _sha256_bytes(_read_regular_bytes(path, maximum_bytes))


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_value: str) -> None:
    raise ValueError("nonfinite JSON value")


def parse_record_bytes(payload: bytes) -> dict[str, Any]:
    """Parse one strict implementation record without filesystem access."""

    if len(payload) > MAX_GENERATED_INPUT_BYTES:
        raise ProofRecordRefusal("MARC2FWR-F01", "record byte cap exceeded")
    if payload.startswith(b"\xef\xbb\xbf") or b"\x00" in payload:
        raise ProofRecordRefusal("MARC2FWR-F01", "record encoding differs")
    try:
        value = json.loads(
            payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ProofRecordRefusal("MARC2FWR-F01", "record JSON differs") from exc
    if not isinstance(value, dict):
        raise ProofRecordRefusal("MARC2FWR-F01", "record root differs")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Load the exact contract that passed both required remote jobs."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    payload = _read_regular_bytes(
        root / CONTRACT_RELATIVE_PATH,
        MAX_GENERATED_INPUT_BYTES,
    )
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise ProofRecordRefusal("MARC2FWR-F02", "contract identity differs")
    contract = parse_record_bytes(payload)
    proof = contract.get("green_predecessor_result", {})
    identity = contract.get("candidate_record_identity", {})
    surface = contract.get("implementation_surface", {})
    if (
        contract.get("schema_name")
        != "neurodecodekit.marc2_proof_record_recovery_contract"
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_generated_only_contract_no_implementation_or_private_execution"
        or proof.get("commit")
        != "4f08553eaa27c83e3f9ace9226dce64d933be1d4"
        or proof.get("CI_run_id") != 31_766_526_262
        or proof.get("base_python_job_id") != 94_663_482_811
        or proof.get("optional_neuro_job_id") != 94_663_482_786
        or proof.get("both_required_jobs_green") is not True
        or tuple(identity.get("required_top_level_fields_in_order", ()))
        != EXPECTED_TOP_LEVEL_FIELDS
        or surface.get("module") != MODULE_NAME
        or surface.get("shared_validator_symbol")
        != validate_implementation_record.__name__
        or surface.get("commands") != ["plan", "qualify", "inspect"]
        or surface.get("execute_command") is not False
        or contract.get("execution_state", {}).get(
            "registered_private_execution_limit"
        )
        != 0
        or any(contract.get("authorization_flags", {}).values())
        or any(contract.get("access_counters", {}).values())
    ):
        raise ProofRecordRefusal("MARC2FWR-F02", "contract semantics differ")
    for binding in contract.get("artifact_bindings", ()):
        relative = _validate_relative_artifact_path(str(binding.get("path", "")))
        digest = str(binding.get("sha256", ""))
        if HEX64_RE.fullmatch(digest) is None:
            raise ProofRecordRefusal("MARC2FWR-F02", "contract binding differs")
        if _sha256_file(root / relative) != digest:
            raise ProofRecordRefusal("MARC2FWR-F02", "contract artifact differs")
    return contract


def _validate_relative_artifact_path(value: str) -> Path:
    if not value or value.startswith(("/", "~")) or "\\" in value:
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked path differs")
    pure = PurePosixPath(value)
    if (
        pure.as_posix() != value
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.is_absolute()
    ):
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked path differs")
    return Path(*pure.parts)


def _validate_proof_shape(proof: ProofEnvelope) -> None:
    if (
        HEX40_RE.fullmatch(proof.implementation_commit) is None
        or HEX40_RE.fullmatch(proof.observed_HEAD) is None
        or HEX64_RE.fullmatch(proof.implementation_registry_sha256) is None
        or min(
            proof.implementation_CI_run_id,
            proof.implementation_base_job_id,
            proof.implementation_optional_job_id,
        )
        <= 0
        or not isinstance(proof.tracked_worktree_clean, bool)
        or not isinstance(proof.green_decision_ancestor, bool)
    ):
        raise ProofRecordRefusal("MARC2FWR-F02", "implementation proof malformed")


def _expected_predecessor_proof(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "green_contract": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "consumed_result": copy.deepcopy(contract["green_predecessor_result"]),
    }


def _expected_surface(module_sha256: str) -> dict[str, Any]:
    return {
        "module": MODULE_NAME,
        "shared_validator_symbol": validate_implementation_record.__name__,
        "validator_source_path": MODULE_RELATIVE_PATH.as_posix(),
        "validator_source_sha256": module_sha256,
        "commands": ["plan", "qualify", "inspect"],
        "execute_command": False,
        "standard_library_only": True,
        "heavy_dependency_imports": 0,
        "private_path_or_output_root_constant": False,
        "URL_network_or_download_client": False,
        "archive_header_member_or_payload_reader": False,
        "signal_event_target_label_quality_or_channel_reader": False,
        "derivative_cache_split_feature_model_or_score_interface": False,
        "old_consumed_executor_import_or_call": False,
        "generated_closure_symbol": validate_implementation_record.__name__,
    }


def _validate_tracked_bindings(
    record: Mapping[str, Any],
    root: Path,
    contract: Mapping[str, Any],
) -> tuple[int, str]:
    bindings = record.get("tracked_file_hashes")
    if not isinstance(bindings, list) or len(bindings) < int(
        contract["tracked_artifact_policy"]["minimum_bindings"]
    ):
        raise ProofRecordRefusal("MARC2FWR-F01", "tracked bindings differ")
    seen: set[str] = set()
    module_sha256: str | None = None
    for binding in bindings:
        if not isinstance(binding, dict) or set(binding) != {"path", "sha256"}:
            raise ProofRecordRefusal("MARC2FWR-F01", "tracked binding shape differs")
        value = str(binding["path"])
        relative = _validate_relative_artifact_path(value)
        if value in seen or relative == IMPLEMENTATION_REGISTRY_RELATIVE_PATH:
            raise ProofRecordRefusal("MARC2FWR-F01", "tracked binding is circular")
        seen.add(value)
        digest = str(binding["sha256"])
        if HEX64_RE.fullmatch(digest) is None:
            raise ProofRecordRefusal("MARC2FWR-F01", "tracked hash malformed")
        if _sha256_file(root / relative) != digest:
            raise ProofRecordRefusal("MARC2FWR-F01", "tracked hash differs")
        if relative == MODULE_RELATIVE_PATH:
            module_sha256 = digest
    if module_sha256 is None:
        raise ProofRecordRefusal("MARC2FWR-F01", "validator source binding missing")
    return len(bindings), module_sha256


def _validate_qualification(
    qualification: Any,
    contract: Mapping[str, Any],
) -> None:
    if not isinstance(qualification, dict):
        raise ProofRecordRefusal("MARC2FWR-F03", "qualification shape differs")
    required = contract["required_candidate_qualification_values"]
    if (
        qualification.get("route") != GENERATED_ROUTE
        or qualification.get("all_gates_passed") is not True
        or qualification.get("predecessor_selector_mutations_passed")
        != required["predecessor_selector_mutations_passed"]
        or qualification.get("predecessor_wrapper_mutations_passed")
        != required["predecessor_wrapper_mutations_passed"]
        or qualification.get("proof_record_mutations_passed")
        != len(ORDERED_MUTATIONS)
        or tuple(qualification.get("proof_record_mutation_order", ()))
        != ORDERED_MUTATIONS
        or qualification.get("shared_validator_module") != MODULE_NAME
        or qualification.get("shared_validator_symbol")
        != validate_implementation_record.__name__
        or qualification.get("shared_validator_call_count") != 34
        or qualification.get("canonical_replays") != 2
        or qualification.get("canonical_summary_byte_identical") is not True
        or qualification.get("CPU_threads") != 1
        or qualification.get("workers") != 1
        or qualification.get("numerical_jobs") != 1
        or qualification.get(
            "private_real_network_payload_neural_target_model_score_counters_zero"
        )
        is not True
        or qualification.get("end_to_end_latency_measured") is not False
        or qualification.get("producer_is_causal")
        != "not_applicable_metadata_only"
        or qualification.get("temporary_output_removed") is not True
    ):
        raise ProofRecordRefusal("MARC2FWR-F03", "qualification values differ")
    measurements = (
        ("runtime_seconds", MAX_RUNTIME_SECONDS),
        ("peak_RSS_bytes", MAX_PEAK_RSS_BYTES),
        ("generated_input_bytes", MAX_GENERATED_INPUT_BYTES),
        ("combined_output_bytes", MAX_COMBINED_OUTPUT_BYTES),
    )
    for field, maximum in measurements:
        value = qualification.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ProofRecordRefusal("MARC2FWR-F03", "qualification measure differs")
        if not math.isfinite(float(value)) or value < 0 or value > maximum:
            raise ProofRecordRefusal("MARC2FWR-F03", "qualification cap differs")


def _validate_state_and_authority(
    record: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> None:
    if record.get("execution_state") != EXPECTED_EXECUTION_STATE:
        raise ProofRecordRefusal("MARC2FWR-F04", "execution state differs")
    authority = record.get("authorization_flags")
    if (
        not isinstance(authority, dict)
        or tuple(authority) != tuple(contract["authorization_flags"])
        or any(value is not False for value in authority.values())
    ):
        raise ProofRecordRefusal("MARC2FWR-F04", "authority differs")
    counters = record.get("access_counters")
    if (
        not isinstance(counters, dict)
        or tuple(counters) != tuple(contract["access_counters"])
        or any(isinstance(value, bool) or value != 0 for value in counters.values())
    ):
        raise ProofRecordRefusal("MARC2FWR-F04", "access counters differ")
    if record.get("next_gate") != EXPECTED_NEXT_GATE:
        raise ProofRecordRefusal("MARC2FWR-F04", "next gate differs")


def _validate_claim_boundary(value: Any) -> None:
    if not isinstance(value, dict) or set(value) != {
        "engineering_capability_added",
        "scientific_claim_not_established",
    }:
        raise ProofRecordRefusal("MARC2FWR-F05", "claim boundary differs")
    engineering = value["engineering_capability_added"]
    scientific = value["scientific_claim_not_established"]
    if (
        not isinstance(engineering, str)
        or "shared implementation-record validator" not in engineering
        or not isinstance(scientific, str)
        or "no human neural data" not in scientific.lower()
        or "thought-to-text" not in scientific
    ):
        raise ProofRecordRefusal("MARC2FWR-F05", "claim boundary differs")


def validate_implementation_record(
    record_bytes: bytes,
    *,
    repo_root: str | Path,
    expected_proof: ProofEnvelope,
    observed_proof: ProofEnvelope,
    generated_closure: Callable[..., Any] | None = None,
) -> ValidationSummary:
    """Validate one complete record through the shared future-live code path."""

    record = parse_record_bytes(record_bytes)
    if tuple(record) != EXPECTED_TOP_LEVEL_FIELDS:
        raise ProofRecordRefusal("MARC2FWR-F00", "top-level record fields differ")
    root = Path(repo_root)
    contract = load_registered_contract(root)
    identity = contract["candidate_record_identity"]
    if (
        record.get("schema_name") != identity["schema_name"]
        or record.get("schema_version") != identity["schema_version"]
        or record.get("lane_id") != identity["lane_id"]
        or record.get("implementation_id") != identity["implementation_id"]
        or record.get("recorded_at_local") != "2026-08-13"
        or record.get("status") != identity["status"]
    ):
        raise ProofRecordRefusal("MARC2FWR-F00", "fixed record identity differs")
    if record.get("predecessor_proof") != _expected_predecessor_proof(contract):
        raise ProofRecordRefusal("MARC2FWR-F02", "predecessor proof differs")
    binding_count, module_sha256 = _validate_tracked_bindings(record, root, contract)
    if record.get("implementation_surface") != _expected_surface(module_sha256):
        raise ProofRecordRefusal("MARC2FWR-F05", "validator surface differs")
    _validate_qualification(record.get("generated_qualification"), contract)
    _validate_state_and_authority(record, contract)
    _validate_claim_boundary(record.get("claim_boundary"))
    closure = generated_closure or validate_implementation_record
    if closure is not validate_implementation_record:
        raise ProofRecordRefusal("MARC2FWR-F05", "shared validator closure differs")
    _validate_proof_shape(expected_proof)
    _validate_proof_shape(observed_proof)
    if (
        expected_proof != observed_proof
        or observed_proof.observed_HEAD != observed_proof.implementation_commit
        or observed_proof.tracked_worktree_clean is not True
        or observed_proof.green_decision_ancestor is not True
        or observed_proof.implementation_registry_sha256
        != _sha256_bytes(record_bytes)
    ):
        raise ProofRecordRefusal("MARC2FWR-F02", "remote green proof differs")
    return ValidationSummary(
        lane_id=LANE_ID,
        record_sha256=_sha256_bytes(record_bytes),
        top_level_field_count=len(record),
        tracked_binding_count=binding_count,
        validator_module=MODULE_NAME,
        validator_symbol=validate_implementation_record.__name__,
        validator_source_sha256=module_sha256,
        implementation_commit=observed_proof.implementation_commit,
    )


def _generated_proof(record_bytes: bytes) -> ProofEnvelope:
    commit = "a" * 40
    return ProofEnvelope(
        implementation_commit=commit,
        implementation_CI_run_id=1,
        implementation_base_job_id=2,
        implementation_optional_job_id=3,
        implementation_registry_sha256=_sha256_bytes(record_bytes),
        observed_HEAD=commit,
        tracked_worktree_clean=True,
        green_decision_ancestor=True,
    )


def build_generated_candidate_record(
    repo_root: str | Path | None = None,
    *,
    tracked_artifacts: Sequence[Path] = DEFAULT_TRACKED_ARTIFACTS,
) -> dict[str, Any]:
    """Build one target-free generated candidate with real public-source hashes."""

    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    bindings = [
        {
            "path": path.as_posix(),
            "sha256": _sha256_file(root / path),
        }
        for path in tracked_artifacts
    ]
    module_sha256 = next(
        item["sha256"]
        for item in bindings
        if item["path"] == MODULE_RELATIVE_PATH.as_posix()
    )
    record = {
        "schema_name": contract["candidate_record_identity"]["schema_name"],
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "implementation_id": contract["candidate_record_identity"][
            "implementation_id"
        ],
        "recorded_at_local": "2026-08-13",
        "status": contract["candidate_record_identity"]["status"],
        "predecessor_proof": _expected_predecessor_proof(contract),
        "tracked_file_hashes": bindings,
        "implementation_surface": _expected_surface(module_sha256),
        "generated_qualification": {
            "route": GENERATED_ROUTE,
            "all_gates_passed": True,
            "predecessor_selector_mutations_passed": 40,
            "predecessor_wrapper_mutations_passed": 18,
            "proof_record_mutations_passed": len(ORDERED_MUTATIONS),
            "proof_record_mutation_order": list(ORDERED_MUTATIONS),
            "shared_validator_module": MODULE_NAME,
            "shared_validator_symbol": validate_implementation_record.__name__,
            "shared_validator_call_count": 34,
            "canonical_replays": 2,
            "canonical_summary_byte_identical": True,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "private_real_network_payload_neural_target_model_score_counters_zero": True,
            "runtime_seconds": 0.0,
            "peak_RSS_bytes": 0,
            "generated_input_bytes": 0,
            "combined_output_bytes": 0,
            "temporary_output_removed": True,
            "end_to_end_latency_measured": False,
            "producer_is_causal": "not_applicable_metadata_only",
        },
        "execution_state": copy.deepcopy(EXPECTED_EXECUTION_STATE),
        "authorization_flags": copy.deepcopy(contract["authorization_flags"]),
        "access_counters": copy.deepcopy(contract["access_counters"]),
        "next_gate": copy.deepcopy(EXPECTED_NEXT_GATE),
        "claim_boundary": {
            "engineering_capability_added": "A shared implementation-record validator now checks generated records through the exact future-live code path.",
            "scientific_claim_not_established": "This generated record contains no human neural data targets predictions or scores and establishes no neural effect decoding accuracy language decoding or thought-to-text capability.",
        },
    }
    for _ in range(8):
        payload = _record_json_bytes(record)
        generated_input_bytes = len(payload) + sum(
            (root / Path(binding["path"])).stat().st_size for binding in bindings
        )
        if (
            record["generated_qualification"]["generated_input_bytes"]
            == generated_input_bytes
        ):
            break
        record["generated_qualification"][
            "generated_input_bytes"
        ] = generated_input_bytes
    return record


def _apply_record_mutation(name: str, record: dict[str, Any]) -> None:
    if name == "schema_name_missing":
        record.pop("schema_name")
    elif name == "schema_name_wrong":
        record["schema_name"] = "wrong"
    elif name == "schema_version_wrong":
        record["schema_version"] = "9.9.9"
    elif name == "lane_id_missing":
        record.pop("lane_id")
    elif name == "lane_id_wrong":
        record["lane_id"] = "MARC2-FW1A"
    elif name == "implementation_id_wrong":
        record["implementation_id"] = "wrong"
    elif name == "status_wrong":
        record["status"] = "authorized"
    elif name == "predecessor_commit_wrong":
        record["predecessor_proof"]["consumed_result"]["commit"] = "b" * 40
    elif name == "predecessor_CI_or_job_wrong":
        record["predecessor_proof"]["green_contract"]["CI_run_id"] += 1
    elif name == "predecessor_result_hash_wrong":
        record["predecessor_proof"]["consumed_result"][
            "result_registry_sha256"
        ] = "b" * 64
    elif name == "tracked_files_empty":
        record["tracked_file_hashes"] = []
    elif name == "tracked_path_absolute":
        record["tracked_file_hashes"][0]["path"] = "/tmp/file"
    elif name == "tracked_path_traversal":
        record["tracked_file_hashes"][0]["path"] = "../file"
    elif name == "tracked_path_duplicate":
        record["tracked_file_hashes"].append(
            copy.deepcopy(record["tracked_file_hashes"][0])
        )
    elif name == "tracked_hash_malformed":
        record["tracked_file_hashes"][0]["sha256"] = "not-a-hash"
    elif name == "tracked_hash_mismatch":
        record["tracked_file_hashes"][0]["sha256"] = "b" * 64
    elif name == "registry_self_binding":
        record["tracked_file_hashes"][0][
            "path"
        ] = IMPLEMENTATION_REGISTRY_RELATIVE_PATH.as_posix()
    elif name == "qualification_all_gates_false":
        record["generated_qualification"]["all_gates_passed"] = False
    elif name == "qualification_selector_count_wrong":
        record["generated_qualification"][
            "predecessor_selector_mutations_passed"
        ] = 39
    elif name == "qualification_wrapper_count_wrong":
        record["generated_qualification"][
            "predecessor_wrapper_mutations_passed"
        ] = 17
    elif name == "qualification_mutation_order_wrong":
        record["generated_qualification"]["proof_record_mutation_order"].reverse()
    elif name == "execution_already_consumed":
        record["execution_state"]["registered_private_execution_consumed"] = True
    elif name == "execution_limit_wrong":
        record["execution_state"]["registered_private_execution_limit"] = 1
    elif name == "retry_limit_nonzero":
        record["execution_state"][
            "retry_rerun_resume_repair_or_fallback_limit"
        ] = 1
    elif name == "access_counter_nonzero":
        first = next(iter(record["access_counters"]))
        record["access_counters"][first] = 1
    elif name == "private_authority_enabled":
        record["authorization_flags"]["private_path_component_check"] = True
    elif name == "payload_or_MARC2_FW2_authority_enabled":
        record["authorization_flags"][
            "MARC2_FW2_CIL1_ORTH1_or_NDK_LANG1"
        ] = True
    elif name == "next_gate_wrong":
        record["next_gate"]["private_access_authorized_now"] = True
    elif name == "claim_boundary_missing":
        record["claim_boundary"].pop("scientific_claim_not_established")


def run_generated_mutation_matrix(
    canonical_record: Mapping[str, Any],
    *,
    repo_root: str | Path,
) -> dict[str, str]:
    """Require all 32 malformed candidates to refuse on frozen routes."""

    root = Path(repo_root)
    contract = load_registered_contract(root)
    expected_routes = contract["mutation_routes"]
    if tuple(expected_routes) != ORDERED_MUTATIONS:
        raise ProofRecordRefusal("MARC2FWR-F03", "mutation registration differs")
    observed_routes: dict[str, str] = {}
    for name in ORDERED_MUTATIONS:
        record = copy.deepcopy(dict(canonical_record))
        if name not in {
            "proof_commit_malformed_or_HEAD_mismatch",
            "proof_CI_job_or_registry_hash_mismatch",
            "generated_closure_uses_different_validator",
        }:
            _apply_record_mutation(name, record)
        payload = _record_json_bytes(record)
        expected = _generated_proof(payload)
        observed = expected
        closure: Callable[..., Any] | None = None
        if name == "proof_commit_malformed_or_HEAD_mismatch":
            observed = replace(observed, observed_HEAD="b" * 40)
        elif name == "proof_CI_job_or_registry_hash_mismatch":
            observed = replace(observed, implementation_CI_run_id=99)
        elif name == "generated_closure_uses_different_validator":
            def different_validator(*_args: Any, **_kwargs: Any) -> None:
                return None

            closure = different_validator
        try:
            validate_implementation_record(
                payload,
                repo_root=root,
                expected_proof=expected,
                observed_proof=observed,
                generated_closure=closure,
            )
        except ProofRecordRefusal as exc:
            if exc.route != expected_routes[name]:
                raise AssertionError(
                    f"{name} routed {exc.route}, expected {expected_routes[name]}"
                ) from exc
            observed_routes[name] = exc.route
        else:
            raise AssertionError(f"required mutation did not refuse: {name}")
    return observed_routes


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if set(report) != PUBLIC_REPORT_FIELDS:
        raise ProofRecordRefusal("MARC2FWR-F03", "public report fields differ")
    if (
        report.get("schema_name")
        != "neurodecodekit.marc2_proof_record_recovery_qualification"
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != GENERATED_ROUTE
        or report.get("status") != "generated_only_qualified"
        or report.get("mutation_summary", {}).get("passed") != len(ORDERED_MUTATIONS)
        or tuple(report.get("mutation_summary", {}).get("order", ()))
        != ORDERED_MUTATIONS
        or set(report.get("mutation_summary", {}).get("routes", {}))
        != set(ORDERED_MUTATIONS)
        or not all(report.get("acceptance_gates", {}).values())
        or any(report.get("access_counters", {}).values())
    ):
        raise ProofRecordRefusal("MARC2FWR-F03", "public report semantics differ")


def _serialize_report_with_size(report: dict[str, Any]) -> bytes:
    for _ in range(12):
        payload = _canonical_json_bytes(report)
        measurements = report["measurements"]
        if (
            measurements["combined_output_bytes"] == len(payload)
            and measurements["incremental_disk_bytes"] == len(payload)
        ):
            return payload
        measurements["combined_output_bytes"] = len(payload)
        measurements["incremental_disk_bytes"] = len(payload)
    raise ProofRecordRefusal("MARC2FWR-F03", "output byte measurement did not settle")


def inspect_qualification_report(path: str | Path) -> dict[str, Any]:
    """Inspect one aggregate generated report with no peer or source access."""

    report_path = Path(path)
    if report_path.name != REPORT_NAME:
        raise ProofRecordRefusal("MARC2FWR-F03", "report filename differs")
    payload = _read_regular_bytes(report_path, MAX_COMBINED_OUTPUT_BYTES)
    report = parse_record_bytes(payload)
    _validate_public_report(report)
    if report["measurements"]["combined_output_bytes"] != len(payload):
        raise ProofRecordRefusal("MARC2FWR-F03", "report byte count differs")
    return report


def qualify_generated_proof_record(
    output_directory: str | Path,
    *,
    repo_root: str | Path | None = None,
    peak_rss_reader: Callable[[], int] | None = None,
) -> QualificationOutcome:
    """Run canonical replay and 32 refusals, inspect output, then remove it."""

    started = time.perf_counter()
    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = load_registered_contract(root)
    record = build_generated_candidate_record(root)
    record_bytes = _record_json_bytes(record)
    proof = _generated_proof(record_bytes)
    first = validate_implementation_record(
        record_bytes,
        repo_root=root,
        expected_proof=proof,
        observed_proof=proof,
    )
    second = validate_implementation_record(
        record_bytes,
        repo_root=root,
        expected_proof=proof,
        observed_proof=proof,
    )
    first_bytes = _canonical_json_bytes(first.to_mapping())
    second_bytes = _canonical_json_bytes(second.to_mapping())
    if first_bytes != second_bytes:
        raise ProofRecordRefusal("MARC2FWR-F03", "canonical replay differs")
    mutation_routes = run_generated_mutation_matrix(record, repo_root=root)
    generated_input_bytes = record["generated_qualification"]["generated_input_bytes"]
    runtime_seconds = time.perf_counter() - started
    peak_rss_bytes = (peak_rss_reader or _peak_rss_bytes)()
    if (
        runtime_seconds > MAX_RUNTIME_SECONDS
        or peak_rss_bytes > MAX_PEAK_RSS_BYTES
        or generated_input_bytes > MAX_GENERATED_INPUT_BYTES
    ):
        raise ProofRecordRefusal("MARC2FWR-F03", "generated resource cap exceeded")
    report: dict[str, Any] = {
        "schema_name": "neurodecodekit.marc2_proof_record_recovery_qualification",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_qualified",
        "route": GENERATED_ROUTE,
        "proof_posture": "generated_record_interface_only_no_private_or_scientific_value",
        "green_contract_proof": {
            "commit": GREEN_CONTRACT_COMMIT,
            "CI_run_id": GREEN_CONTRACT_CI_RUN_ID,
            "base_python_job_id": GREEN_CONTRACT_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_CONTRACT_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "candidate_summary": {
            "record_sha256": first.record_sha256,
            "record_bytes": len(record_bytes),
            "top_level_fields": first.top_level_field_count,
            "lane_id_present_and_exact": True,
            "tracked_bindings": first.tracked_binding_count,
            "registry_self_binding": False,
            "private_execution_limit": 0,
        },
        "shared_validator": {
            "module": first.validator_module,
            "symbol": first.validator_symbol,
            "source_sha256": first.validator_source_sha256,
            "canonical_calls": 2,
            "mutation_calls": len(ORDERED_MUTATIONS),
            "total_calls": 34,
            "future_live_wrapper_must_use_same_symbol": True,
        },
        "mutation_summary": {
            "registered": len(ORDERED_MUTATIONS),
            "passed": len(mutation_routes),
            "order": list(ORDERED_MUTATIONS),
            "routes": mutation_routes,
        },
        "replay_summary": {
            "canonical_runs": 2,
            "summary_bytes_identical": True,
            "summary_sha256": _sha256_bytes(first_bytes),
        },
        "measurements": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "generated_input_bytes": generated_input_bytes,
            "combined_output_bytes": 0,
            "incremental_disk_bytes": 0,
            "network_bytes": 0,
            "private_or_real_input_bytes": 0,
            "end_to_end_latency_measured": False,
            "producer_is_causal": "not_applicable_metadata_only",
        },
        "access_counters": copy.deepcopy(contract["access_counters"]),
        "acceptance_gates": {
            name: True for name in contract["acceptance_gates"]
        },
        "warnings": copy.deepcopy(contract["warnings"]),
        "unavailable_fields": copy.deepcopy(contract["unavailable_fields"]),
        "claim_boundary": {
            "engineering_capability_added": "A shared implementation-record validator now accepts the complete generated MARC2-FW1B record and rejects all 32 registered defects.",
            "scientific_claim_not_established": "No human neural data target prediction or score was accessed so this establishes no neural effect decoding accuracy language decoding or thought-to-text capability.",
        },
    }
    report_bytes = _serialize_report_with_size(report)
    if len(report_bytes) > MAX_COMBINED_OUTPUT_BYTES:
        raise ProofRecordRefusal("MARC2FWR-F03", "generated output cap exceeded")
    _validate_public_report(report)

    output = Path(output_directory)
    if os.path.lexists(output):
        raise ProofRecordRefusal("MARC2FWR-F03", "generated output exists")
    parent = output.parent
    parent_stat = os.lstat(parent)
    if stat.S_ISLNK(parent_stat.st_mode) or not stat.S_ISDIR(parent_stat.st_mode):
        raise ProofRecordRefusal("MARC2FWR-F03", "generated output parent differs")
    report_path = output / REPORT_NAME
    removed = False
    try:
        output.mkdir(mode=0o700)
        with report_path.open("xb") as handle:
            handle.write(report_bytes)
        inspected = inspect_qualification_report(report_path)
        if _canonical_json_bytes(inspected) != report_bytes:
            raise ProofRecordRefusal("MARC2FWR-F03", "report inspection differs")
        report_path.unlink()
        output.rmdir()
        removed = True
    finally:
        if not removed and output.exists():
            if report_path.exists() and report_path.is_file():
                report_path.unlink()
            try:
                output.rmdir()
            except OSError:
                pass
    if os.path.lexists(output):
        raise ProofRecordRefusal("MARC2FWR-F03", "generated cleanup differs")
    return QualificationOutcome(
        report=report,
        report_bytes=report_bytes,
        report_sha256=_sha256_bytes(report_bytes),
        mutation_routes=mutation_routes,
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=generated_input_bytes,
        generated_output_bytes=len(report_bytes),
        output_removed=True,
    )


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the fixed generated-only plan without constructing a candidate."""

    contract = load_registered_contract(repo_root)
    return {
        "lane_id": LANE_ID,
        "commands": list(contract["implementation_surface"]["commands"]),
        "required_top_level_fields": list(EXPECTED_TOP_LEVEL_FIELDS),
        "ordered_mutations": list(ORDERED_MUTATIONS),
        "shared_validator_module": MODULE_NAME,
        "shared_validator_symbol": validate_implementation_record.__name__,
        "registered_private_execution_limit": 0,
        "network_bytes": 0,
        "private_or_real_input_bytes": 0,
        "MARC2_FW2_eligible": False,
        "scientific_claim_upgrade": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="print the frozen generated-only plan")
    plan.add_argument("--repo-root", type=Path)
    qualify = subparsers.add_parser(
        "qualify", help="run generated record qualification and exact cleanup"
    )
    qualify.add_argument("--output", type=Path, required=True)
    qualify.add_argument("--repo-root", type=Path)
    inspect = subparsers.add_parser(
        "inspect", help="inspect one aggregate generated qualification report"
    )
    inspect.add_argument("--report", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = registered_plan(args.repo_root)
        elif args.command == "qualify":
            outcome = qualify_generated_proof_record(
                args.output,
                repo_root=args.repo_root,
            )
            result = {
                "route": outcome.report["route"],
                "report_sha256": outcome.report_sha256,
                "mutations_passed": len(outcome.mutation_routes),
                "runtime_seconds": outcome.runtime_seconds,
                "peak_RSS_bytes": outcome.peak_rss_bytes,
                "generated_input_bytes": outcome.generated_input_bytes,
                "generated_output_bytes": outcome.generated_output_bytes,
                "output_removed": outcome.output_removed,
                "private_or_real_input_bytes": 0,
                "network_bytes": 0,
            }
        else:
            result = inspect_qualification_report(args.report)
    except (OSError, ProofRecordRefusal) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
