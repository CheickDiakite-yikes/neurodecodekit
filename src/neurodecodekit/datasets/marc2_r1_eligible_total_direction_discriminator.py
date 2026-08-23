"""Generated-only discriminator for the direction of the VR30P R1 total."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import resource
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import (
    marc2_r1_inventory_distribution_discriminator as vr29a,
)

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR31A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r1_eligible_total_direction_discriminator_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r1_eligible_total_direction_discriminator_result"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_r1_eligible_total_direction_discriminator_contract.v0.json"
)
VR2_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py"
)
CONTRACT_SHA256 = "d02b95029e3c3b2b61388d0d838d81108ca11675b752a1530c6135c17f1cdf00"
GREEN_REGISTRATION_COMMIT = "eeab6785b8eadc6d65199fa1ac519173f9c160c7"
GREEN_REGISTRATION_CI_RUN_ID = 32_626_878_097
GREEN_REGISTRATION_BASE_JOB_ID = 97_163_443_088
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_163_443_152
EXPECTED_TOTAL = 195
SUCCESS_ROUTES = ("MARC2VR31A-G1", "MARC2VR31A-G2")
BELOW_EXPECTED_ROUTE = "MARC2VR31A-R1"
ABOVE_EXPECTED_ROUTE = "MARC2VR31A-R2"
OUT_OF_SCOPE_ROUTE = "MARC2VR31A-R3"
REFUSAL_ROUTES = tuple(f"MARC2VR31A-F{index:02d}" for index in range(1, 7))
CASES = vr29a.CASES
ORDERS = vr29a.ORDERS
REPLAYS = 2
THREAD_ENVIRONMENT = dict(vr29a.THREAD_ENVIRONMENT)
PRIVATE_PAYLOAD_FIELDS = set(vr29a.PRIVATE_PAYLOAD_FIELDS) | {
    "actual_total",
    "count_delta",
    "eligible_count",
    "filtered_count",
    "private_count",
    "total_difference",
}


class R1EligibleTotalDirectionDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR31A refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR31A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


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
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR31A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "eeab6785b8eadc6d65199fa1ac519173f9c160c7"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_626_878_097
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_163_443_088
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_163_443_152
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(
    contract: Mapping[str, Any], root: Path | None = None
) -> int:
    base = root or _repo_root()
    inputs = contract.get("fixed_inputs")
    if not isinstance(inputs, list) or len(inputs) != contract.get(
        "fixed_input_count"
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for item in inputs:
        if not isinstance(item, dict) or not {
            "role",
            "path",
            "bytes",
            "sha256",
        }.issubset(item):
            raise R1EligibleTotalDirectionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / item["path"]).read_bytes()
        except (OSError, TypeError) as exc:
            raise R1EligibleTotalDirectionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != item["bytes"] or _sha256_bytes(payload) != item["sha256"]:
            raise R1EligibleTotalDirectionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _is_threshold_predicate(node: ast.AST) -> bool:
    if not isinstance(node, ast.Compare):
        return False
    if len(node.ops) != 1 or not isinstance(node.ops[0], ast.NotEq):
        return False
    if len(node.comparators) != 1:
        return False
    comparator = node.comparators[0]
    left = node.left
    return (
        isinstance(comparator, ast.Constant)
        and comparator.value == EXPECTED_TOTAL
        and isinstance(left, ast.Call)
        and isinstance(left.func, ast.Name)
        and left.func.id == "len"
        and len(left.args) == 1
        and isinstance(left.args[0], ast.Name)
        and left.args[0].id == "filtered"
    )


def _verify_threshold_predicate(
    contract: Mapping[str, Any], root: Path | None = None
) -> int:
    try:
        source = ((root or _repo_root()) / VR2_RELATIVE_PATH).read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "VR2 threshold source is unavailable"
        ) from exc
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_filter_and_validate_eligible"
    ]
    count = sum(
        1 for function in functions for node in ast.walk(function) if _is_threshold_predicate(node)
    )
    expected = contract.get("immutable_threshold_predicate")
    if (
        len(functions) != 1
        or count != 1
        or not isinstance(expected, dict)
        or expected.get("function_name") != "_filter_and_validate_eligible"
        or expected.get("expression") != "len(filtered) != 195"
        or expected.get("expected_total") != EXPECTED_TOTAL
        or expected.get("exact_AST_match_count") != count
        or expected.get("threshold_override_allowed")
        or expected.get("observed_total_or_difference_output_allowed")
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "immutable threshold predicate differs"
        )
    return count


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _build_case(case: str, order: str) -> dict[str, Any]:
    try:
        return vr29a._build_case(case, order)
    except vr29a.R1InventoryDistributionDiscriminatorRefusal as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated case or order differs"
        ) from exc


def _map_non_r1_upstream(upstream_route: str) -> str:
    mapping = {
        vr29a.SUCCESS_ROUTES[0]: SUCCESS_ROUTES[0],
        vr29a.SUCCESS_ROUTES[1]: SUCCESS_ROUTES[1],
        vr29a.DISTRIBUTION_ROUTE: OUT_OF_SCOPE_ROUTE,
        vr29a.OUT_OF_SCOPE_ROUTE: OUT_OF_SCOPE_ROUTE,
    }
    try:
        return mapping[upstream_route]
    except KeyError as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "upstream route is outside direction discriminator"
        ) from exc


def _direction_from_generated_source(source: Mapping[str, Any]) -> str:
    contract = vr2.load_registered_contract()
    try:
        vr2._verify_contract_mapping(contract)
        entries = vr2._validate_live_envelope(source, contract)
        grouped, _kinds = vr29a.vr25a.vr20a._group_rows(entries)
        labels = {key: vr2._classify_key(key, contract) for key in grouped}
    except (
        vr2.LiveDomainEligibilityRefusal,
        vr29a.vr25a.vr20a.PublishedTaskSelectorRepairRefusal,
    ) as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "direction replay refused"
        ) from exc
    eligible_count = sum(
        1 for key in grouped if labels[key] == vr2.PREDICATE_CODES[0]
    )
    if eligible_count < EXPECTED_TOTAL:
        return BELOW_EXPECTED_ROUTE
    if eligible_count > EXPECTED_TOTAL:
        return ABOVE_EXPECTED_ROUTE
    raise R1EligibleTotalDirectionDiscriminatorRefusal(
        REFUSAL_ROUTES[2], "R1 direction unexpectedly equals threshold"
    )


def discriminate_generated_source(source: Mapping[str, Any]) -> tuple[str, str, int]:
    """Call unchanged VR29A once and return only an aggregate-safe route."""

    before = vr29a.vr25a._source_bytes(source)
    try:
        upstream_route, _vr25a_route, _filter_calls = (
            vr29a.discriminate_generated_source(source)
        )
    except vr29a.R1InventoryDistributionDiscriminatorRefusal as exc:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "VR29A discrimination refused"
        ) from exc
    direction_comparisons = 0
    if upstream_route == vr29a.INVENTORY_TOTAL_ROUTE:
        route = _direction_from_generated_source(source)
        direction_comparisons = 1
    else:
        route = _map_non_r1_upstream(upstream_route)
    if vr29a.vr25a._source_bytes(source) != before:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated source changed during discrimination"
        )
    return route, upstream_route, direction_comparisons


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise R1EligibleTotalDirectionDiscriminatorRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains private field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    generated_input_bytes: int,
    aggregate_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_limits"]
    if (
        runtime_seconds < 0
        or runtime_seconds > caps["runtime_seconds"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= caps["peak_RSS_bytes"]
        or generated_input_bytes > caps["generated_input_bytes"]
        or aggregate_output_bytes > caps["aggregate_output_bytes"]
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except R1EligibleTotalDirectionDiscriminatorRefusal as exc:
        return exc.route
    raise R1EligibleTotalDirectionDiscriminatorRefusal(
        REFUSAL_ROUTES[4], "direct refusal unexpectedly passed"
    )


def _run_direct_refusals(contract: Mapping[str, Any]) -> int:
    routes: list[str] = []
    mutation_keys = (
        "schema_name",
        "schema_version",
        "contract_id",
        "lane_id",
        "status",
        "objective",
        "result_proof",
        "fixed_inputs",
        "fixed_input_count",
        "fixed_input_bytes",
        "immutable_threshold_predicate",
        "ordered_R1_direction_inventory",
        "generated_witness_matrix",
        "implementation_contract",
        "resource_limits",
        "authorization",
    )
    for index, key in enumerate(mutation_keys):
        changed = copy.deepcopy(dict(contract))
        changed[key] = f"mutated-{index}"
        routes.append(_expect_refusal(lambda item=changed: _verify_contract_mapping(item)))
    for key in THREAD_ENVIRONMENT:
        changed = dict(THREAD_ENVIRONMENT)
        changed[key] = "2"
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
        changed = dict(THREAD_ENVIRONMENT)
        del changed[key]
        routes.append(
            _expect_refusal(lambda item=changed: _validate_thread_environment(item))
        )
    for case in ("unknown", "", "private", "override"):
        routes.append(_expect_refusal(lambda value=case: _build_case(value, "canonical")))
    for order in ("sorted", "random", "private"):
        routes.append(_expect_refusal(lambda value=order: _build_case(CASES[0], value)))
    for upstream in (
        vr29a.INVENTORY_TOTAL_ROUTE,
        "MARC2VR29A-R4",
        "MARC2VR29A-F01",
        "MARC2VR29A-F02",
        "MARC2VR29A-F03",
        "MARC2VR29A-F04",
        "unknown",
    ):
        routes.append(_expect_refusal(lambda value=upstream: _map_non_r1_upstream(value)))
    routes.append(
        _expect_refusal(
            lambda: _direction_from_generated_source(
                _build_case("exact_public_control", "canonical")
            )
        )
    )
    for field in sorted(PRIVATE_PAYLOAD_FIELDS):
        routes.append(
            _expect_refusal(lambda key=field: _assert_public_report_safe({key: "x"}))
        )
    caps = contract["resource_limits"]
    resource_mutations = (
        (caps["runtime_seconds"] + 1.0, 1, 1, 1),
        (1.0, caps["peak_RSS_bytes"], 1, 1),
        (1.0, 1, caps["generated_input_bytes"] + 1, 1),
        (1.0, 1, 1, caps["aggregate_output_bytes"] + 1),
    )
    for values in resource_mutations:
        routes.append(
            _expect_refusal(
                lambda item=values: _assert_resources(
                    runtime_seconds=item[0],
                    peak_rss_bytes=item[1],
                    generated_input_bytes=item[2],
                    aggregate_output_bytes=item[3],
                    contract=contract,
                )
            )
        )
    if len(routes) < contract["generated_witness_matrix"]["minimum_direct_refusals"]:
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "direct refusal coverage is incomplete"
        )
    return len(routes)


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "readiness_or_consumed_state_operations": 0,
        "archive_header_or_member_reads": 0,
        "neural_signal_operations": 0,
        "target_or_label_operations": 0,
        "model_training_inference_prediction_or_scoring_runs": 0,
        "network_or_provider_calls": 0,
        "new_payload_bytes": 0,
        "FW2_or_CIL1_operations": 0,
        "other_project_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the exact 32-path generated-only VR31A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    threshold_predicates = _verify_threshold_predicate(registered)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(registered)

    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    generated_input_bytes = 0
    vr29a_calls = 0
    direction_comparisons = 0
    expected = {
        "exact_public_control": (SUCCESS_ROUTES[0], vr29a.SUCCESS_ROUTES[0], 0),
        "single_session_exclusion_removed": (
            SUCCESS_ROUTES[1],
            vr29a.SUCCESS_ROUTES[1],
            0,
        ),
        "eligible_bundle_removed": (
            BELOW_EXPECTED_ROUTE,
            vr29a.INVENTORY_TOTAL_ROUTE,
            1,
        ),
        "eligible_bundle_added": (
            ABOVE_EXPECTED_ROUTE,
            vr29a.INVENTORY_TOTAL_ROUTE,
            1,
        ),
        "eligible_distribution_shift": (
            OUT_OF_SCOPE_ROUTE,
            vr29a.DISTRIBUTION_ROUTE,
            0,
        ),
        "eligible_distribution_shift_second": (
            OUT_OF_SCOPE_ROUTE,
            vr29a.DISTRIBUTION_ROUTE,
            0,
        ),
        "unknown_participant_bundle": (
            OUT_OF_SCOPE_ROUTE,
            vr29a.OUT_OF_SCOPE_ROUTE,
            0,
        ),
        "incomplete_companion_set": (
            OUT_OF_SCOPE_ROUTE,
            vr29a.OUT_OF_SCOPE_ROUTE,
            0,
        ),
    }
    replay_signatures: list[list[tuple[str, str, str, str, int]]] = []
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str, str, int]] = []
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                payload = vr29a.vr25a._source_bytes(source)
                generated_input_bytes += len(payload)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(payload))
                route, upstream, case_comparisons = discriminate_generated_source(source)
                vr29a_calls += 1
                direction_comparisons += case_comparisons
                if (route, upstream, case_comparisons) != expected[case]:
                    raise R1EligibleTotalDirectionDiscriminatorRefusal(
                        REFUSAL_ROUTES[3], "generated route differs"
                    )
                signature.append((case, order, route, upstream, case_comparisons))
                route_counts[route] += 1
                upstream_counts[upstream] += 1
        replay_signatures.append(signature)
    matrix = registered["generated_witness_matrix"]
    if (
        vr29a_calls != matrix["required_VR29A_calls"]
        or direction_comparisons != matrix["required_R1_direction_comparisons"]
        or route_counts != Counter(matrix["expected_VR31A_route_counts"])
        or upstream_counts
        != Counter(
            {
                vr29a.SUCCESS_ROUTES[0]: 4,
                vr29a.SUCCESS_ROUTES[1]: 4,
                vr29a.INVENTORY_TOTAL_ROUTE: 8,
                vr29a.DISTRIBUTION_ROUTE: 8,
                vr29a.OUT_OF_SCOPE_ROUTE: 8,
            }
        )
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
    ):
        raise R1EligibleTotalDirectionDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated replay or route counts differ"
        )

    runtime = clock() - started
    rss = peak_rss()
    replay_digest = _sha256_bytes(_canonical_json_bytes(replay_signatures))
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTES[0],
        "status": "generated_eligible_total_direction_discriminator_qualified",
        "proof": {
            "registration_commit": GREEN_REGISTRATION_COMMIT,
            "registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "registration_base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "registration_optional_neuro_job_id": (
                GREEN_REGISTRATION_OPTIONAL_JOB_ID
            ),
            "contract_sha256": CONTRACT_SHA256,
        },
        "matrix": {
            "cases": list(CASES),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "paths": vr29a_calls,
            "VR29A_calls": vr29a_calls,
            "R1_direction_comparisons": direction_comparisons,
            "immutable_threshold_predicates": threshold_predicates,
            "VR31A_route_counts": dict(sorted(route_counts.items())),
            "VR29A_route_counts": dict(sorted(upstream_counts.items())),
            "exact_replays_match": True,
            "order_invariant_route_distribution": True,
            "replay_digest": replay_digest,
            "direct_refusals_passed": direct_refusals,
            "source_mutations_after_call": 0,
            "observed_total_or_difference_retained": False,
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "retained_output_bytes": 0,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _zero_counters(),
        "warnings": [
            "artifact_only_and_generated_only",
            "no_private_executor",
            "generated_direction_routes_do_not_identify_the_consumed_private_direction",
            "no_observed_total_or_difference_retained",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "consumed_private_R1_direction",
            "private_observed_total_or_difference",
            "private_distribution_participant_or_source_detail",
            "real_target_free_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated discrimination of below-expected versus above-expected "
                "filtered eligible totals without count exposure"
            ),
            "scientific_claim_not_established": (
                "No neural payload target model prediction or score was accessed."
            ),
        },
    }
    output_bytes = -1
    while report["measurements"].get("aggregate_output_bytes") != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_public_report_safe(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        generated_input_bytes=generated_input_bytes,
        aggregate_output_bytes=output_bytes,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the frozen generated-only plan with no private authority."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "schema_name": (
            "neurodecodekit.marc2_r1_eligible_total_direction_discriminator_plan"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "immutable_threshold_predicates": _verify_threshold_predicate(contract),
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": 32,
        "VR29A_calls": 32,
        "R1_direction_comparisons": 8,
        "minimum_direct_refusals": 70,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 R1 eligible-total direction discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_plan() if args.command == "plan" else qualify_generated()
    except R1EligibleTotalDirectionDiscriminatorRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
