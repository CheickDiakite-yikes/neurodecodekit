"""Generated-only MARC2 F03 five-route discriminator qualification."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_f03_predicate_decomposition as decomp

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR10B"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_f03_five_route_discriminator_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f03_five_route_discriminator_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_f03_five_route_discriminator_contract.v0.json"
)
CONTRACT_SHA256 = "465032260d1e07c7302645e4106ddceb6e755b68b7061b71e9b9d13c7ac0bfc7"
GREEN_REGISTRATION_COMMIT = "d642eae988bdf5200429fb992e7ff25d778ce949"
GREEN_REGISTRATION_CI_RUN_ID = 32_003_674_374
GREEN_REGISTRATION_BASE_JOB_ID = 95_308_775_711
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_308_775_577
SUCCESS_ROUTE = "MARC2VR10B-G1"
RESULT_ROUTES = tuple(f"MARC2VR10B-R{index}" for index in range(1, 6))
REFUSAL_ROUTES = tuple(f"MARC2VR10B-F{index:02d}" for index in range(1, 9))
CASES = decomp.CASES
ORDERS = decomp.ORDERS
CASE_ROUTES = {
    "control_success": SUCCESS_ROUTE,
    "overlong_member_name": RESULT_ROUTES[0],
    "suffix_bearing_BIDS_identity": RESULT_ROUTES[1],
    "task_token_case": RESULT_ROUTES[2],
    "logical_companion_alias": RESULT_ROUTES[3],
    "incomplete_companion_set": RESULT_ROUTES[4],
}
PREDICATE_IDS = tuple(
    value for value in decomp.CASE_PREDICATES.values() if value is not None
)
THREAD_ENVIRONMENT = decomp.THREAD_ENVIRONMENT
FORBIDDEN_IMPORT_ROOTS = decomp.FORBIDDEN_IMPORT_ROOTS
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "crc32",
        "entries",
        "event",
        "exception",
        "failed_value",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "path",
        "prediction",
        "predictions",
        "private_hash",
        "private_manifest",
        "reason",
        "row",
        "row_index",
        "rows",
        "run_id",
        "selection",
        "session_id",
        "signal",
        "source_identity",
        "subject_id",
        "suffix",
        "target",
        "targets",
    }
)


class FiveRouteDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR10B refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR10B refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class DiscriminatorDecision:
    """One coarse route with no failed value or source identity."""

    route: str

    def __post_init__(self) -> None:
        if self.route not in {SUCCESS_ROUTE, *RESULT_ROUTES}:
            raise ValueError("unknown MARC2-VR10B decision route")


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


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
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = nested
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object")
    return value


def _read_fixed(root: Path, relative: str) -> bytes:
    try:
        path = decomp.relay._fixed_path(root, relative)
        return decomp.relay._read_bound_file(path)
    except decomp.relay.GeneratedDiagnosticRelayRefusal as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed artifact read refused"
        ) from exc


def _expected_route_rows() -> list[dict[str, Any]]:
    meanings = (
        "member_name_UTF8_length_class",
        "suffix_bearing_BIDS_identity_class",
        "exact_freewill_task_token_class",
        "logical_run_companion_uniqueness_class",
        "four_companion_completeness_class",
    )
    return [
        {
            "priority": index,
            "predicate_id": predicate,
            "result_route": route,
            "safe_meaning": meaning,
            "first_match_stops": True,
        }
        for index, (predicate, route, meaning) in enumerate(
            zip(PREDICATE_IDS, RESULT_ROUTES, meanings, strict=True), start=1
        )
    ]


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
        or contract.get("fixed_input_count") != 10
        or contract.get("fixed_input_bytes") != 390_842
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract identity differs"
        )
    proof = contract.get("green_prior_proof", {})
    if (
        proof.get("VR10A_implementation_commit")
        != "84103a5fab86b7c7c8d3cf3af00c9efe3457470c"
        or proof.get("VR10A_implementation_CI_run_id") != 31_998_811_585
        or proof.get("VR10A_implementation_base_job_id") != 95_295_212_461
        or proof.get("VR10A_implementation_optional_job_id") != 95_295_212_440
        or proof.get("VR10A_closeout_commit")
        != "92d028139573309e5636b2f520c915e66113f7aa"
        or proof.get("VR10A_closeout_CI_run_id") != 32_001_355_120
        or proof.get("VR10A_closeout_base_job_id") != 95_302_164_129
        or proof.get("VR10A_closeout_optional_job_id") != 95_302_164_150
        or proof.get("both_required_jobs_green_for_both_commits") is not True
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "green prior proof differs"
        )
    if contract.get("ordered_discriminator_routes") != _expected_route_rows():
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered route order differs"
        )
    tree = contract.get("decision_tree_contract", {})
    if (
        tree.get("evaluation_order") != "ascending_priority_first_match_stops"
        or tree.get("source_mutation_allowed") is not False
        or tree.get("multiple_result_routes_allowed") is not False
        or tree.get("ambiguous_state_allowed") is not False
        or tree.get("unsupported_non_F03_drift_returns_generic_refusal") is not True
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered decision tree differs"
        )
    matrix = contract.get("generated_qualification_matrix", {})
    cases = matrix.get("cases")
    if (
        not isinstance(cases, list)
        or [row.get("case") for row in cases] != list(CASES)
        or [row.get("expected_discriminator_route") for row in cases]
        != [CASE_ROUTES[case] for case in CASES]
        or matrix.get("orders") != list(ORDERS)
        or matrix.get("replays") != 2
        or matrix.get("required_paths") != 24
        or matrix.get("required_exact_parser_entry_visits") != 29_448
        or matrix.get("required_VR6_calls") != 24
        or matrix.get("required_discriminator_calls") != 24
        or matrix.get("control_G1_paths") != 4
        or matrix.get("classified_R1_through_R5_paths") != 20
        or matrix.get("each_result_route_paths") != 4
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered generated matrix differs"
        )
    surface = contract.get("implementation_surface", {})
    if (
        surface.get("dependency_free_standard_library") is not True
        or surface.get("generated_fixture_only") is not True
        or surface.get("private_executor_present") is not False
        or surface.get("local_path_reader_present") is not False
        or surface.get("network_client_present") is not False
        or surface.get("execute_mode_present") is not False
        or surface.get("model_or_scorer_present") is not False
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered implementation surface differs"
        )
    firewall = contract.get("output_firewall", {})
    if (
        firewall.get("one_route_per_decision_required") is not True
        or firewall.get("failed_value_allowed") is not False
        or firewall.get("private_G1_result_allowed") is not False
        or firewall.get("recursive_forbidden_key_scan_required") is not True
        or frozenset(firewall.get("forbidden_public_keys", ()))
        != FORBIDDEN_PUBLIC_KEYS
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered output firewall differs"
        )
    caps = contract.get("resource_caps", {})
    if (
        caps.get("CPU_threads") != 1
        or caps.get("workers") != 1
        or caps.get("numerical_jobs") != 1
        or caps.get("runtime_seconds") != 45
        or caps.get("peak_RSS_bytes") != 256 * 1024**2
        or caps.get("generated_input_bytes") != 16 * 1024**2
        or caps.get("aggregate_output_bytes") != 1024**2
        or caps.get("retained_generated_output_bytes") != 0
        or contract.get("direct_refusal_minimum") != 45
        or len(contract.get("acceptance_gates", ())) != 14
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered caps or gates differ"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered authority is not all false"
        )
    if any(contract.get("operation_counters", {}).values()):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered operations are not all zero"
        )


def load_registered_contract(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact remotely green VR10B registration."""

    root = Path(repo_root or _repo_root()).resolve()
    payload = _read_fixed(root, CONTRACT_RELATIVE_PATH.as_posix())
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_fixed_inputs(
    root: Path, contract: Mapping[str, Any]
) -> tuple[dict[str, bytes], int, int]:
    fixed = contract.get("fixed_inputs")
    registration = contract.get("registration_artifacts", {})
    if not isinstance(fixed, list) or len(fixed) != 10:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    combined = [
        *fixed,
        {
            "role": "registration_document",
            "path": registration.get("document_path"),
            "bytes": registration.get("document_bytes"),
            "sha256": registration.get("document_sha256"),
        },
        {
            "role": "registration_test",
            "path": registration.get("test_path"),
            "bytes": registration.get("test_bytes"),
            "sha256": registration.get("test_sha256"),
        },
    ]
    payloads: dict[str, bytes] = {}
    total = 0
    for row in combined:
        if (
            not isinstance(row, dict)
            or set(row) != {"role", "path", "bytes", "sha256"}
            or not isinstance(row.get("role"), str)
            or row["role"] in payloads
            or not isinstance(row.get("path"), str)
            or isinstance(row.get("bytes"), bool)
            or not isinstance(row.get("bytes"), int)
            or not isinstance(row.get("sha256"), str)
        ):
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        payload = _read_fixed(root, row["path"])
        if len(payload) != row["bytes"] or _sha256_bytes(payload) != row["sha256"]:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input size or SHA-256 differs"
            )
        payloads[row["role"]] = payload
        total += len(payload)
    contract_payload = _read_fixed(root, CONTRACT_RELATIVE_PATH.as_posix())
    return payloads, len(combined) + 1, total + len(contract_payload)


def _validate_green_prior_records(payloads: Mapping[str, bytes]) -> None:
    try:
        implementation = _strict_json(payloads["VR10A_implementation_record"])
        result = _strict_json(payloads["VR10A_result_record"])
    except (KeyError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "green prior record differs"
        ) from exc
    proof = implementation.get("remote_implementation_proof", {})
    if (
        implementation.get("status")
        != "exact_generated_implementation_and_result_remotely_green"
        or proof.get("commit")
        != "84103a5fab86b7c7c8d3cf3af00c9efe3457470c"
        or proof.get("CI_run_id") != 31_998_811_585
        or proof.get("both_required_jobs_green") is not True
        or result.get("status")
        != "completed_artifact_only_generated_F03_decomposition_remotely_green"
        or result.get("route") != "MARC2VR10A-G1"
        or result.get("verification", {}).get("remote_CI_pending") is not False
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "green prior proof record differs"
        )


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "one-thread environment is not explicit"
        )


def _validate_module_surface() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
            modules.add(node.module)
    if imported & FORBIDDEN_IMPORT_ROOTS:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "network or heavy import surface is forbidden"
        )
    forbidden_modules = (
        "marc2_two_layer_private_diagnostic",
        "marc2_variable_domain_private_recovery",
        "marc2_dynamic_private_selection_recovery",
    )
    if any(name in module for name in forbidden_modules for module in modules):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "private or consumed implementation import is forbidden"
        )


def _neutralized_identity_row(row: Mapping[str, Any]) -> dict[str, Any]:
    neutral = dict(row)
    neutral["member_name"] = "vr10b_generated_neutral/neutral.bin"
    return neutral


def _classify_entries(entries: Sequence[Any]) -> DiscriminatorDecision:
    selector = decomp.relay.selector
    repair = decomp.relay.vr2.repair
    names: set[str] = set()
    kinds: Counter[str] = Counter()
    grouped: dict[tuple[str, str, int], dict[str, Mapping[str, Any]]] = defaultdict(
        dict
    )
    for row in entries:
        if not isinstance(row, dict) or set(row) != selector.ENTRY_FIELDS:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source row precondition differs"
            )
        raw_name = row.get("member_name")
        if not isinstance(raw_name, str) or not raw_name:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source member precondition differs"
            )
        try:
            name_bytes = raw_name.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source member encoding differs"
            ) from exc
        if len(name_bytes) > 1_024:
            return DiscriminatorDecision(RESULT_ROUTES[0])
        try:
            name = selector._normalize_member_name(raw_name)
        except selector.FreewillPrefixSelectionRefusal as exc:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source normalization precondition differs"
            ) from exc
        match = selector._core_match(name)
        suffix_bearing_mismatch = match is None and any(
            name.endswith(suffix) for suffix in selector.REQUIRED_SUFFIXES
        )
        task_mismatch = match is not None and match.group("task") != "freewill"
        validation_row = (
            _neutralized_identity_row(row)
            if suffix_bearing_mismatch or task_mismatch
            else row
        )
        try:
            selector._validate_entry(validation_row)
        except selector.FreewillPrefixSelectionRefusal as exc:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source nonclassifier precondition differs"
            ) from exc
        if suffix_bearing_mismatch:
            return DiscriminatorDecision(RESULT_ROUTES[1])
        if task_mismatch:
            return DiscriminatorDecision(RESULT_ROUTES[2])
        try:
            validated_name, validated_match = selector._validate_entry(row)
        except selector.FreewillPrefixSelectionRefusal as exc:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source exact-row precondition differs"
            ) from exc
        if validated_name != name or (
            (validated_match is None) != (match is None)
            or (
                match is not None
                and validated_match is not None
                and validated_match.groupdict() != match.groupdict()
            )
        ):
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source exact-row replay differs"
            )
        if name in names:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[2], "source full-name precondition differs"
            )
        names.add(name)
        kinds[row["entry_kind"]] += 1
        if match is None:
            continue
        key = (
            match.group("subject"),
            match.group("session"),
            int(match.group("run")),
        )
        suffix = match.group("suffix")
        if suffix in grouped[key]:
            return DiscriminatorDecision(RESULT_ROUTES[3])
        grouped[key][suffix] = row
    required = set(selector.REQUIRED_SUFFIXES)
    if any(set(companions) != required for companions in grouped.values()):
        return DiscriminatorDecision(RESULT_ROUTES[4])
    try:
        exact_grouped, exact_kinds = repair._group_source_rows(entries)
    except repair.SourceValidityEligibilityRefusal as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "source exact-group replay differs"
        ) from exc
    if (
        set(exact_grouped) != set(grouped)
        or exact_kinds != kinds
        or kinds != Counter({"regular_file": 1_025, "directory": 202})
        or len(grouped) != 238
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "source aggregate precondition differs"
        )
    return DiscriminatorDecision(SUCCESS_ROUTE)


def discriminate_generated_source(
    source: Mapping[str, Any],
    *,
    vr2_contract: Mapping[str, Any],
) -> DiscriminatorDecision:
    """Return one coarse route for an exact generated live-shaped source."""

    before = decomp.relay.vr2._canonical_source_bytes(source)
    try:
        decomp.relay.vr2._verify_contract_mapping(vr2_contract)
        entries = decomp.relay.vr2._validate_live_envelope(source, vr2_contract)
    except decomp.relay.vr2.LiveDomainEligibilityRefusal as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated source envelope differs"
        ) from exc
    decision = _classify_entries(entries)
    if decomp.relay.vr2._canonical_source_bytes(source) != before:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "discriminator mutated source"
        )
    return decision


def _run_path(
    case: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    try:
        composed = decomp._compose_witness(
            case,
            order,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except decomp.F03PredicateDecompositionRefusal as exc:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "exact generated witness composition refused"
        ) from exc
    before = decomp.relay.vr2._canonical_source_bytes(composed.source)
    try:
        decomp.relay.vr6.adapt_dynamic_live_source(
            composed.source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except decomp.relay.vr6.DynamicLiveSelectionRefusal as exc:
        if (
            case == "control_success"
            or exc.route != "MARC2VR6-F02"
            or exc.upstream_route != "MARC2VR2-F03"
        ):
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[7], "broad generated route differs"
            ) from None
        outer_route = exc.route
        nested_route = exc.upstream_route
    else:
        if case != "control_success":
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[7], "generated witness unexpectedly passed VR6"
            )
        outer_route = "VR6_success"
        nested_route = None
    if decomp.relay.vr2._canonical_source_bytes(composed.source) != before:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "VR6 mutated generated source"
        )
    decision = discriminate_generated_source(
        composed.source, vr2_contract=vr2_contract
    )
    if decision.route != CASE_ROUTES[case]:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "generated discriminator route differs"
        )
    if decomp.relay.vr2._canonical_source_bytes(composed.source) != before:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[7], "classifier path mutated generated source"
        )
    outcome = {
        "case": case,
        "order": order,
        "outer_route": outer_route,
        "nested_route": nested_route,
        "discriminator_route": decision.route,
    }
    mechanics = {
        "case": case,
        "order": order,
        "entry_count": composed.entry_count,
        "regular_file_rows": composed.regular_file_rows,
        "directory_rows": composed.directory_rows,
        "materialized_bytes": composed.materialized_bytes,
        "central_directory_bytes": composed.central_directory_bytes,
        "ZIP64_entries": composed.zip64_entries,
        "local_interval_end": composed.local_interval_end,
        "witness_mutation_stage": composed.witness_mutation_stage,
        "synthetic_normalization_fields": list(
            composed.synthetic_normalization_fields
        ),
    }
    return outcome, mechanics


def _run_matrix(
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    outcomes: list[dict[str, Any]] = []
    mechanics: list[dict[str, Any]] = []
    generated_bytes = 0
    for case in CASES:
        order_routes: list[str] = []
        for order in ORDERS:
            outcome, measured = _run_path(
                case,
                order,
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
            )
            outcomes.append(outcome)
            mechanics.append(measured)
            generated_bytes += measured["materialized_bytes"]
            order_routes.append(outcome["discriminator_route"])
        if len(set(order_routes)) != 1:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[3], "discriminator route differs across source order"
            )
    return outcomes, mechanics, generated_bytes


def _validate_replay(
    first: Sequence[Mapping[str, Any]],
    first_mechanics: Sequence[Mapping[str, Any]],
    second: Sequence[Mapping[str, Any]],
    second_mechanics: Sequence[Mapping[str, Any]],
) -> None:
    if first != second or first_mechanics != second_mechanics:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "complete generated discriminator replay differs"
        )


def _base_access_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR9P_path_or_output_operations": 0,
        "network_or_public_request_operations": 0,
        "archive_local_header_or_member_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "derivative_cache_feature_split_or_NeuroToken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "provider_language_model_stream_device_or_hardware_operations": 0,
        "MARC2_FW2_or_CIL1_operations": 0,
        "retry_rerun_release_or_scientific_claim_upgrades": 0,
        "operations_on_other_projects": 0,
    }


def _validate_public_value(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                raise FiveRouteDiscriminatorRefusal(
                    REFUSAL_ROUTES[4], "forbidden aggregate field"
                )
            _validate_public_value(nested)
    elif isinstance(value, list):
        for nested in value:
            _validate_public_value(nested)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            ".codex_work" in lowered
            or "/sub-" in lowered
            or "\\sub-" in lowered
            or lowered.startswith("sub-")
            or "task-freewill" in lowered
        ):
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[4], "private path or identity leaked"
            )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    retained_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    values = (
        (runtime_seconds, caps["runtime_seconds"]),
        (peak_rss_bytes, caps["peak_RSS_bytes"]),
        (generated_input_bytes, caps["generated_input_bytes"]),
        (aggregate_output_bytes, caps["aggregate_output_bytes"]),
        (retained_output_bytes, caps["retained_generated_output_bytes"]),
    )
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value < 0
            or value > cap
            for value, cap in values
        )
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "resource or output cap exceeded"
        )


def _expected_route_counts() -> dict[str, int]:
    return {route: 4 for route in (SUCCESS_ROUTE, *RESULT_ROUTES)}


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report identity differs"
        )
    route_summary = report.get("route_summary", {})
    if (
        route_summary.get("route_counts") != _expected_route_counts()
        or route_summary.get("broad_VR6_success_paths") != 4
        or route_summary.get("broad_outer_F02_nested_F03_paths") != 20
        or route_summary.get("one_route_per_decision") is not True
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "aggregate route summary differs"
        )
    replay = report.get("replay_summary", {})
    digest = replay.get("internal_matrix_digest_sha256")
    if (
        replay.get("exact_replays") != 2
        or replay.get("paths_per_replay") != 12
        or replay.get("total_paths") != 24
        or replay.get("exact_parser_entry_visits") != 29_448
        or replay.get("exact_VR6_calls") != 24
        or replay.get("exact_discriminator_calls") != 24
        or replay.get("order_invariant") is not True
        or replay.get("byte_identical_replay") is not True
        or not isinstance(digest, str)
        or len(digest) != 64
        or any(char not in "0123456789abcdef" for char in digest)
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "aggregate replay summary differs"
        )
    if any(report.get("access_counters", {}).values()):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "forbidden operation counter is nonzero"
        )
    if not all(report.get("acceptance_gates", {}).values()):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "acceptance gate is false"
        )
    refusals = report.get("direct_refusals")
    if not isinstance(refusals, dict) or any(
        value not in REFUSAL_ROUTES for value in refusals.values()
    ):
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "direct refusal report differs"
        )
    _validate_public_value(report)


def _expect_refusal(
    name: str,
    action: Callable[[], Any],
    *,
    expected_route: str,
) -> str:
    try:
        action()
    except FiveRouteDiscriminatorRefusal as exc:
        if exc.route != expected_route:
            raise FiveRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[6], f"refusal route differs: {name}"
            ) from exc
        return exc.route
    raise FiveRouteDiscriminatorRefusal(
        REFUSAL_ROUTES[6], f"required refusal did not occur: {name}"
    )


def _run_required_refusals(
    report: Mapping[str, Any], *, contract: Mapping[str, Any]
) -> dict[str, str]:
    checks: dict[str, tuple[str, Callable[[], Any]]] = {}

    def changed_contract(
        mutator: Callable[[dict[str, Any]], None],
    ) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(contract))
            mutator(changed)
            _verify_contract_mapping(changed)

        return action

    def changed_report(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(report))
            mutator(changed)
            _validate_public_report(changed)

        return action

    checks.update(
        {
            "contract_schema_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("schema_name", "changed")
                ),
            ),
            "contract_status_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(lambda value: value.__setitem__("status", "changed")),
            ),
            "fixed_input_count_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("fixed_input_count", 9)
                ),
            ),
            "fixed_input_bytes_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("fixed_input_bytes", 1)
                ),
            ),
            "green_prior_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["green_prior_proof"].__setitem__(
                        "VR10A_implementation_CI_run_id", 1
                    )
                ),
            ),
            "tree_order_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["decision_tree_contract"].__setitem__(
                        "evaluation_order", "changed"
                    )
                ),
            ),
            "authorization_nonzero": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["authorization_state"].__setitem__(
                        "future_private_discriminator_invocation_authorized_now",
                        True,
                    )
                ),
            ),
            "registered_counter_nonzero": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["operation_counters"].__setitem__(
                        "network_or_public_request_operations", 1
                    )
                ),
            ),
        }
    )
    for index in range(5):
        checks[f"route_priority_drift_{index + 1:02d}"] = (
            REFUSAL_ROUTES[0],
            changed_contract(
                lambda value, index=index: value["ordered_discriminator_routes"][
                    index
                ].__setitem__("priority", 9)
            ),
        )
    for index in range(6):
        checks[f"matrix_route_drift_{index + 1:02d}"] = (
            REFUSAL_ROUTES[0],
            changed_contract(
                lambda value, index=index: value["generated_qualification_matrix"][
                    "cases"
                ][index].__setitem__("expected_discriminator_route", "changed")
            ),
        )
    checks.update(
        {
            "report_identity_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value.__setitem__("schema_name", "changed")
                ),
            ),
            "route_count_drift": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["route_summary"]["route_counts"].__setitem__(
                        RESULT_ROUTES[0], 3
                    )
                ),
            ),
            "replay_count_drift": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["replay_summary"].__setitem__(
                        "total_paths", 23
                    )
                ),
            ),
            "acceptance_gate_false": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["acceptance_gates"].__setitem__(
                        "all_ten_fixed_inputs_match_size_and_SHA256", False
                    )
                ),
            ),
            "public_counter_nonzero": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["access_counters"].__setitem__(
                        "network_or_public_request_operations", 1
                    )
                ),
            ),
            "thread_environment_drift": (
                REFUSAL_ROUTES[5],
                lambda: _validate_thread_environment({}),
            ),
        }
    )
    for index, key in enumerate(sorted(FORBIDDEN_PUBLIC_KEYS)):
        checks[f"forbidden_field_{index + 1:02d}"] = (
            REFUSAL_ROUTES[4],
            changed_report(
                lambda value, key=key: value.__setitem__(key, "redacted")
            ),
        )

    def resource_action(**overrides: Any) -> None:
        values = {
            "runtime_seconds": 0.1,
            "peak_rss_bytes": 1,
            "generated_input_bytes": 1,
            "aggregate_output_bytes": 1,
            "retained_output_bytes": 0,
            "contract": contract,
        }
        values.update(overrides)
        _assert_resources(**values)

    caps = contract["resource_caps"]
    checks.update(
        {
            "runtime_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=caps["runtime_seconds"] + 1),
            ),
            "RSS_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(peak_rss_bytes=caps["peak_RSS_bytes"] + 1),
            ),
            "generated_input_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    generated_input_bytes=caps["generated_input_bytes"] + 1
                ),
            ),
            "aggregate_output_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    aggregate_output_bytes=caps["aggregate_output_bytes"] + 1
                ),
            ),
            "retained_output_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(retained_output_bytes=1),
            ),
            "nonfinite_runtime": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=float("nan")),
            ),
        }
    )
    if len(checks) < contract["direct_refusal_minimum"]:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "required refusal inventory is too small"
        )
    return {
        name: _expect_refusal(name, action, expected_route=route)
        for name, (route, action) in checks.items()
    }


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1_024)


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the frozen 24-path generated-only discriminator qualification."""

    started = clock()
    _validate_thread_environment(environment)
    root = Path(repo_root or _repo_root()).resolve()
    contract = load_registered_contract(root)
    payloads, fixed_artifact_count, fixed_artifact_bytes = _verify_fixed_inputs(
        root, contract
    )
    _validate_green_prior_records(payloads)
    _validate_module_surface()
    vr2_contract = decomp.relay.vr2.load_registered_contract(root)
    selector_contract = decomp.relay.selector.load_registered_contract(root)
    first, first_mechanics, first_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    second, second_mechanics, second_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    _validate_replay(first, first_mechanics, second, second_mechanics)
    all_outcomes = [*first, *second]
    all_mechanics = [*first_mechanics, *second_mechanics]
    route_counts = Counter(row["discriminator_route"] for row in all_outcomes)
    if dict(route_counts) != _expected_route_counts():
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated route counts differ"
        )
    broad_success = sum(row["outer_route"] == "VR6_success" for row in all_outcomes)
    broad_f03 = sum(
        row["outer_route"] == "MARC2VR6-F02"
        and row["nested_route"] == "MARC2VR2-F03"
        for row in all_outcomes
    )
    if broad_success != 4 or broad_f03 != 20:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "broad route counts differ"
        )
    matrix_digest = _sha256_bytes(_canonical_json_bytes(all_outcomes))
    provisional: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_artifact_only_generated_five_route_qualification",
        "proof_posture": (
            "tracked_code_and_generated_structural_interface_only_no_private_or_"
            "scientific_value"
        ),
        "route": SUCCESS_ROUTE,
        "green_registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "tracked_artifact_summary": {
            "count": fixed_artifact_count,
            "bytes": fixed_artifact_bytes,
            "combined_payload_sha256": _sha256_bytes(
                b"".join(payloads[role] for role in sorted(payloads))
            ),
        },
        "route_summary": {
            "ordered_routes": [SUCCESS_ROUTE, *RESULT_ROUTES],
            "route_counts": dict(route_counts),
            "broad_VR6_success_paths": broad_success,
            "broad_outer_F02_nested_F03_paths": broad_f03,
            "one_route_per_decision": True,
            "failed_values_retained": 0,
            "per_item_outcomes_retained": 0,
        },
        "replay_summary": {
            "exact_replays": 2,
            "paths_per_replay": 12,
            "total_paths": len(all_outcomes),
            "exact_parser_entry_visits": sum(
                row["entry_count"] for row in all_mechanics
            ),
            "exact_VR6_calls": len(all_outcomes),
            "exact_discriminator_calls": len(all_outcomes),
            "order_invariant": True,
            "byte_identical_replay": True,
            "internal_matrix_digest_sha256": matrix_digest,
        },
        "mechanics": {
            "entry_count_each": 1_227,
            "regular_file_rows_each": 1_025,
            "directory_rows_each": 202,
            "materialized_bytes_minimum_per_path": min(
                row["materialized_bytes"] for row in all_mechanics
            ),
            "materialized_bytes_maximum_per_path": max(
                row["materialized_bytes"] for row in all_mechanics
            ),
            "central_directory_bytes_minimum": min(
                row["central_directory_bytes"] for row in all_mechanics
            ),
            "central_directory_bytes_maximum": max(
                row["central_directory_bytes"] for row in all_mechanics
            ),
            "ZIP64_entries_minimum": min(
                row["ZIP64_entries"] for row in all_mechanics
            ),
            "ZIP64_entries_maximum": max(
                row["ZIP64_entries"] for row in all_mechanics
            ),
            "maximum_local_interval_end": max(
                row["local_interval_end"] for row in all_mechanics
            ),
            "witness_mutations_before_exact_parser": 20,
            "control_paths_without_witness_mutation": 4,
            "post_parser_witness_mutations": 0,
            "source_mutations_by_discriminator": 0,
            "member_local_header_bytes": 0,
            "member_payload_bytes": 0,
        },
        "measurements": {
            "fixed_artifact_count": fixed_artifact_count,
            "fixed_artifact_bytes": fixed_artifact_bytes,
            "generated_input_bytes": first_bytes + second_bytes,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": 0.0,
            "peak_RSS_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "direct_refusals": {},
        "acceptance_gates": {
            "all_ten_fixed_inputs_match_size_and_SHA256": True,
            "exact_green_VR10A_implementation_and_closeout_proofs_match": True,
            "ordered_P03_P15_P16_P18_P19_route_map_is_byte_stable": True,
            "all_24_exact_parser_and_producer_paths_complete": True,
            "all_20_witness_paths_retain_outer_F02_and_nested_F03": True,
            "all_20_witness_paths_map_to_four_copies_of_each_R1_through_R5_route": True,
            "all_four_control_paths_pass_VR6_and_return_G1": True,
            "canonical_and_reversed_order_decisions_match": True,
            "both_complete_replays_are_byte_identical": True,
            "no_classifier_call_mutates_its_source": True,
            "aggregate_output_firewall_rejects_every_forbidden_field_recursively": True,
            "at_least_45_direct_refusals_pass": True,
            "runtime_RSS_input_output_and_zero_retention_caps_pass": True,
            "all_private_scientific_other_project_retry_release_and_claim_counters_are_zero": True,
        },
        "access_counters": _base_access_counters(),
        "warnings": [
            "Routes classify generated structural failure classes, not a private cause.",
            "G1 is a generated clean-control route and is not private validity evidence.",
            "No failed value, identity, row position, or per-item outcome is retained.",
            "Generated structural witnesses have no scientific or decoding value.",
        ],
        "unavailable_fields": [
            "private F03 class and failed value",
            "private member row identity and cohort",
            "archive payload neural signal event target model prediction and score",
        ],
        "next_gate": {
            "exact_implementation_and_result_commit_push_and_both_jobs_green_required": True,
            "future_private_discriminator_authorized": False,
            "future_private_discriminator_requires_new_Tier_C_packet_and_fresh_decision": True,
            "consumed_VR9P_reuse_allowed": False,
            "F03_rule_relaxation_allowed": False,
            "MARC2_FW2_or_CIL1_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": (
                "artifact_only_generated_five_route_structural_classifier"
            ),
            "scientific_ceiling": "none",
            "private_cause_identified": False,
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "unseen_person_generalization": False,
            "real_time_portable_home_assistive_or_clinical_result": False,
        },
    }
    provisional["direct_refusals"] = _run_required_refusals(
        provisional, contract=contract
    )
    if len(provisional["direct_refusals"]) < contract["direct_refusal_minimum"]:
        raise FiveRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[6], "direct refusal inventory is too small"
        )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    provisional["measurements"]["runtime_seconds"] = runtime_seconds
    provisional["measurements"]["peak_RSS_bytes"] = peak_rss_bytes
    output_bytes = len(_canonical_json_bytes(provisional))
    provisional["measurements"]["aggregate_output_bytes"] = output_bytes
    final_bytes = len(_canonical_json_bytes(provisional))
    if final_bytes != output_bytes:
        provisional["measurements"]["aggregate_output_bytes"] = final_bytes
        final_bytes = len(_canonical_json_bytes(provisional))
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=provisional["measurements"]["generated_input_bytes"],
        aggregate_output_bytes=final_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _validate_public_report(provisional)
    return provisional


def build_plan_summary(
    *, repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return the frozen generated-only plan without running a witness."""

    contract = load_registered_contract(repo_root)
    matrix = contract["generated_qualification_matrix"]
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "green_registration_commit": GREEN_REGISTRATION_COMMIT,
        "fixed_input_count": contract["fixed_input_count"],
        "fixed_input_bytes": contract["fixed_input_bytes"],
        "ordered_result_routes": list(RESULT_ROUTES),
        "generated_control_route": SUCCESS_ROUTE,
        "generated_cases": len(matrix["cases"]),
        "required_paths": matrix["required_paths"],
        "required_VR6_calls": matrix["required_VR6_calls"],
        "required_discriminator_calls": matrix["required_discriminator_calls"],
        "private_access_authorized": False,
        "network_bytes": 0,
        "real_or_private_bytes": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog=(
            "python -m neurodecodekit.datasets."
            "marc2_f03_five_route_discriminator"
        ),
        description=(
            "Qualify the artifact-only MARC2 F03 five-route generated "
            "discriminator."
        ),
    )
    command.add_argument("command", choices=("plan", "qualify"))
    return command


def main(argv: Sequence[str] | None = None) -> int:
    """Run the bounded artifact-only command surface."""

    args = _build_parser().parse_args(argv)
    try:
        output = build_plan_summary() if args.command == "plan" else qualify_generated()
    except FiveRouteDiscriminatorRefusal as exc:
        print(f"{exc.route}: F03 five-route qualification refused", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
