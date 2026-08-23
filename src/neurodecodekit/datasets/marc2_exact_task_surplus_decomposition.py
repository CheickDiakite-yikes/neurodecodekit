"""Generated-only decomposition of MARC2 exact-task surplus topology."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a
from neurodecodekit.datasets import marc2_task_aware_eligibility_repair as vr35a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR37A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_exact_task_surplus_decomposition_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_exact_task_surplus_decomposition_result"
CONTRACT_RELATIVE_PATH = Path("registries/marc2_exact_task_surplus_decomposition_contract.v0.json")
CONTRACT_SHA256 = "4dd92ec97bcd63837174bc9cd1e7562cc395affae3a618677e22fd44fb3a8c2e"
GREEN_REGISTRATION_COMMIT = "a677e7abd2b89e92bb7bcc3f823a3493c6a32ad0"
GREEN_REGISTRATION_CI_RUN_ID = 32_652_807_264
GREEN_REGISTRATION_BASE_JOB_ID = 97_226_913_287
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_226_913_421
ROUTES = (
    "MARC2VR37A-G1",
    "MARC2VR37A-R1",
    "MARC2VR37A-R2",
    "MARC2VR37A-R3",
    "MARC2VR37A-R4",
    "MARC2VR37A-R5",
)
REFUSAL_ROUTES = tuple(f"MARC2VR37A-F{index:02d}" for index in range(1, 7))
CASES = (
    "public_map_exact_control",
    "single_cell_contiguous_extension",
    "single_cell_noncontiguous_extension",
    "multi_cell_pure_surplus",
    "mixed_surplus_and_deficit_net_positive",
    "structural_or_task_firewall_refusal",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_PUBLIC_KEYS = {
    "actual_count",
    "cell_delta",
    "cell_identity",
    "cohort",
    "difference",
    "eligible_count",
    "member_name",
    "observed_count",
    "participant_id",
    "private_manifest",
    "private_value",
    "run_index",
    "selected_rows",
    "selection_identity",
    "source_exact_name",
    "source_path",
    "subject_id",
    "target_text",
    "target_value",
    "task_distribution",
}


class ExactTaskSurplusDecompositionRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR37A refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR37A refusal route")
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
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR37A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract schema differs"
        )
    return payload


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    registered = load_registered_contract()
    matrix = contract.get("generated_matrix", {})
    implementation = contract.get("implementation_contract", {})
    resources = contract.get("resource_limits", {})
    forbidden = contract.get("forbidden_operations", {})
    if (
        not isinstance(contract, dict)
        or contract != registered
        or contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_generated_only_implementation_blocked_until_remote_green"
        or matrix.get("cases") != list(CASES)
        or matrix.get("orders") != list(ORDERS)
        or matrix.get("replays") != REPLAYS
        or matrix.get("required_paths") != 24
        or matrix.get("VR35A_calls") != 24
        or matrix.get("minimum_direct_refusals", 0) < 60
        or implementation.get("commands") != ["plan", "qualify"]
        or implementation.get("private_executor_allowed") is not False
        or implementation.get("dependency_policy") != "standard_library_only"
        or resources.get("CPU_threads") != 1
        or resources.get("workers") != 1
        or resources.get("numerical_jobs") != 1
        or resources.get("network_bytes") != 0
        or resources.get("new_payload_bytes") != 0
        or not forbidden
        or any(value != 0 for value in forbidden.values())
    ):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT != "a677e7abd2b89e92bb7bcc3f823a3493c6a32ad0"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_652_807_264
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_226_913_287
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_226_913_421
    ):
        raise ExactTaskSurplusDecompositionRefusal(REFUSAL_ROUTES[0], "registration proof differs")


def _verify_fixed_inputs(contract: Mapping[str, Any], root: Path | None = None) -> int:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 8:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    for row in rows:
        if not isinstance(row, dict):
            raise ExactTaskSurplusDecompositionRefusal(REFUSAL_ROUTES[0], "fixed input row differs")
        try:
            payload = (fixed_root / str(row["path"])).read_bytes()
        except (KeyError, OSError) as exc:
            raise ExactTaskSurplusDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get("sha256"):
            raise ExactTaskSurplusDecompositionRefusal(REFUSAL_ROUTES[0], "fixed input differs")
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _source_bytes(source: Mapping[str, Any]) -> bytes:
    try:
        return vr35a._source_bytes(source)
    except vr35a.TaskAwareEligibilityRepairRefusal as exc:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[1], "generated source is not canonical"
        ) from exc


def _expected_cell_runs(vr2_contract: Mapping[str, Any]) -> dict[tuple[str, str], set[int]]:
    try:
        counts = vr2_contract["published_eligible_session_counts"]
        subjects = vr2_contract["participant_taxonomy"]["eligible_subject_ids"]
        expected = {
            (subject, session): set(range(1, int(counts[subject][index]) + 1))
            for subject in subjects
            for index, session in enumerate(("ses-01", "ses-02"))
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[2], "public cell map differs"
        ) from exc
    if len(expected) != 38 or sum(len(runs) for runs in expected.values()) != 195:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[2], "public cell arithmetic differs"
        )
    return expected


def _observed_eligible_cell_runs(
    source: Mapping[str, Any], vr2_contract: Mapping[str, Any]
) -> dict[tuple[str, str], set[int]]:
    try:
        entries = vr35a.vr2._validate_live_envelope(source, vr2_contract)
        grouped, _kinds = vr35a._group_task_rows(entries)
        projected = vr35a._project_published_task(grouped)
        labels = vr35a._classify(projected, vr2_contract)
    except (
        vr35a.TaskAwareEligibilityRepairRefusal,
        vr35a.vr2.LiveDomainEligibilityRefusal,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[2], "exact-task topology validation refused"
        ) from exc
    observed: dict[tuple[str, str], set[int]] = defaultdict(set)
    for (subject, session, run), label in labels.items():
        if label == vr35a.vr2.PREDICATE_CODES[0]:
            observed[(subject, session)].add(run)
    return dict(observed)


def _classify_topology(
    observed: Mapping[tuple[str, str], set[int]],
    expected: Mapping[tuple[str, str], set[int]],
) -> str:
    if set(observed) - set(expected):
        return ROUTES[5]
    positive: list[tuple[tuple[str, str], set[int], set[int]]] = []
    negative: list[tuple[tuple[str, str], set[int], set[int]]] = []
    for cell, expected_runs in expected.items():
        observed_runs = observed.get(cell, set())
        if len(observed_runs) > len(expected_runs):
            positive.append((cell, observed_runs, expected_runs))
        elif len(observed_runs) < len(expected_runs):
            negative.append((cell, observed_runs, expected_runs))
        elif observed_runs != expected_runs:
            return ROUTES[5]
    observed_total = sum(len(runs) for runs in observed.values())
    expected_total = sum(len(runs) for runs in expected.values())
    if not positive and not negative and observed_total == expected_total:
        return ROUTES[0]
    if observed_total <= expected_total:
        return ROUTES[5]
    if len(positive) == 1 and not negative:
        _cell, observed_runs, expected_runs = positive[0]
        if len(observed_runs) != len(expected_runs) + 1:
            return ROUTES[5]
        extra = observed_runs - expected_runs
        if extra == {len(expected_runs) + 1} and expected_runs <= observed_runs:
            return ROUTES[1]
        if len(extra) == 1 and expected_runs <= observed_runs:
            return ROUTES[2]
        return ROUTES[5]
    if len(positive) > 1 and not negative:
        return ROUTES[3]
    if positive and negative:
        return ROUTES[4]
    return ROUTES[5]


def classify_generated_source(
    source: Mapping[str, Any], *, contract: Mapping[str, Any] | None = None
) -> str:
    """Classify one generated source without exposing cell identities or deltas."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    _verify_fixed_inputs(registered)
    before = _source_bytes(source)
    try:
        upstream_route, _outcome = vr35a._route_case(source)
    except (vr35a.TaskAwareEligibilityRepairRefusal, TypeError, ValueError):
        return ROUTES[5]
    if upstream_route not in (vr35a.SUCCESS_ROUTES[0], vr35a.DIAGNOSTIC_ROUTES[0]):
        return ROUTES[5]
    vr2_contract = vr35a.vr2.load_registered_contract()
    expected = _expected_cell_runs(vr2_contract)
    try:
        observed = _observed_eligible_cell_runs(source, vr2_contract)
    except ExactTaskSurplusDecompositionRefusal:
        return ROUTES[5]
    route = _classify_topology(observed, expected)
    if (
        (upstream_route == vr35a.SUCCESS_ROUTES[0] and route != ROUTES[0])
        or (upstream_route == vr35a.DIAGNOSTIC_ROUTES[0] and route == ROUTES[0])
        or _source_bytes(source) != before
    ):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[3], "upstream route topology or immutability differs"
        )
    return route


def build_generated_case(case: str, order: str) -> dict[str, Any]:
    """Build one exact generated VR37A topology witness."""

    if case not in CASES:
        raise ValueError("unknown generated case")
    if order not in ORDERS:
        raise ValueError("unknown generated row order")
    if case == "public_map_exact_control":
        source = vr35a.build_generated_case("baseline_exact_task_exact_total", "canonical")
    elif case == "single_cell_contiguous_extension":
        source = vr35a.build_generated_case("target_task_surplus", "canonical")
    else:
        source = vr35a.build_generated_case("baseline_exact_task_exact_total", "canonical")
        if case == "single_cell_noncontiguous_extension":
            vr25a._replace_auxiliary_with_bundle(source, ("sub-07", "ses-01", 5))
        elif case == "multi_cell_pure_surplus":
            vr25a._replace_auxiliary_with_bundle(source, ("sub-07", "ses-01", 4))
            vr25a._replace_auxiliary_with_bundle(source, ("sub-07", "ses-02", 4))
        elif case == "mixed_surplus_and_deficit_net_positive":
            vr25a._replace_auxiliary_with_bundle(source, ("sub-07", "ses-01", 4))
            vr25a._replace_auxiliary_with_bundle(source, ("sub-07", "ses-02", 4))
            vr25a._replace_bundle_with_auxiliary(source, ("sub-05", "ses-01", 4), "mixed-topology")
        else:
            source = vr35a.build_generated_case("selection_or_task_firewall_refusal", "canonical")
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise ExactTaskSurplusDecompositionRefusal(REFUSAL_ROUTES[5], "thread environment differs")


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise ExactTaskSurplusDecompositionRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains forbidden field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _assert_resources(
    *,
    runtime_seconds: float,
    peak_rss_bytes: int,
    aggregate_output_bytes: int,
    contract: Mapping[str, Any],
) -> None:
    limits = contract["resource_limits"]
    if (
        runtime_seconds < 0
        or runtime_seconds > limits["runtime_seconds_maximum"]
        or peak_rss_bytes < 0
        or peak_rss_bytes >= limits["peak_RSS_bytes_maximum_exclusive"]
        or aggregate_output_bytes > limits["generated_output_bytes_maximum"]
    ):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(expected_route: str, action: Callable[[], Any]) -> str:
    try:
        action()
    except ExactTaskSurplusDecompositionRefusal as exc:
        if exc.route != expected_route:
            raise ExactTaskSurplusDecompositionRefusal(
                REFUSAL_ROUTES[2], "direct refusal route differs"
            ) from exc
        return exc.route
    raise ExactTaskSurplusDecompositionRefusal(
        REFUSAL_ROUTES[2], "direct mutation unexpectedly passed"
    )


def _leaf_paths(value: Any, prefix: tuple[Any, ...] = ()) -> list[tuple[Any, ...]]:
    paths: list[tuple[Any, ...]] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            paths.extend(_leaf_paths(child, (*prefix, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_leaf_paths(child, (*prefix, index)))
    else:
        paths.append(prefix)
    return paths


def _mutate_leaf(value: Any) -> Any:
    if isinstance(value, bool):
        return not value
    if isinstance(value, int):
        return value + 1
    if value is None:
        return "changed"
    return "changed" if value != "changed" else "changed-again"


def _contract_mutations(contract: Mapping[str, Any]) -> list[dict[str, Any]]:
    mutations: list[dict[str, Any]] = []
    for path in _leaf_paths(contract)[:64]:
        changed = copy.deepcopy(dict(contract))
        cursor: Any = changed
        for part in path[:-1]:
            cursor = cursor[part]
        cursor[path[-1]] = _mutate_leaf(cursor[path[-1]])
        mutations.append(changed)
    return mutations


def _run_direct_refusals(contract: Mapping[str, Any]) -> Counter[str]:
    routes: Counter[str] = Counter()
    for changed in _contract_mutations(contract):
        route = _expect_refusal(
            REFUSAL_ROUTES[0],
            lambda item=changed: _verify_contract_mapping(item),
        )
        routes[route] += 1
    for key in sorted(FORBIDDEN_PUBLIC_KEYS):
        route = _expect_refusal(
            REFUSAL_ROUTES[4],
            lambda value=key: _assert_public_report_safe({value: "forbidden"}),
        )
        routes[route] += 1
    limits = contract["resource_limits"]
    mutations = (
        (limits["runtime_seconds_maximum"] + 1.0, 1, 1),
        (1.0, limits["peak_RSS_bytes_maximum_exclusive"], 1),
        (1.0, 1, limits["generated_output_bytes_maximum"] + 1),
    )
    for runtime_seconds, rss, output_bytes in mutations:
        route = _expect_refusal(
            REFUSAL_ROUTES[5],
            lambda a=runtime_seconds, b=rss, c=output_bytes: _assert_resources(
                runtime_seconds=a,
                peak_rss_bytes=b,
                aggregate_output_bytes=c,
                contract=contract,
            ),
        )
        routes[route] += 1
    if sum(routes.values()) < contract["generated_matrix"]["minimum_direct_refusals"]:
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[2], "direct refusal coverage is incomplete"
        )
    return routes


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the sole registered 24-path generated-only VR37A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    refusal_counts = _run_direct_refusals(registered)
    expected_routes = dict(zip(CASES, ROUTES, strict=True))
    route_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    replay_signatures: list[list[tuple[str, str, str]]] = []
    generated_input_bytes = 0
    vr35a_calls = 0
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str]] = []
        for order in ORDERS:
            for case in CASES:
                source = build_generated_case(case, order)
                before = _source_bytes(source)
                generated_input_bytes += len(before)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(before))
                route = classify_generated_source(source, contract=registered)
                vr35a_calls += 1
                if route != expected_routes[case] or _source_bytes(source) != before:
                    raise ExactTaskSurplusDecompositionRefusal(
                        REFUSAL_ROUTES[3], "generated route or immutability differs"
                    )
                route_counts[route] += 1
                signature.append((case, order, route))
        replay_signatures.append(signature)
    matrix = registered["generated_matrix"]
    if (
        route_counts != Counter(matrix["expected_route_counts"])
        or vr35a_calls != matrix["VR35A_calls"]
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
    ):
        raise ExactTaskSurplusDecompositionRefusal(
            REFUSAL_ROUTES[3], "generated matrix acceptance gate differs"
        )
    runtime = clock() - started
    rss = peak_rss()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_exact_task_surplus_decomposition_qualified",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        },
        "matrix": {
            "paths": sum(route_counts.values()),
            "cases": len(CASES),
            "orders": len(ORDERS),
            "replays": REPLAYS,
            "route_counts": dict(sorted(route_counts.items())),
            "VR35A_calls": vr35a_calls,
            "source_immutability_checks": sum(route_counts.values()),
            "exact_replays_match": True,
        },
        "decomposition": {
            "published_subject_session_cells": 38,
            "published_cell_total": 195,
            "public_map_exact_control_distinguished": True,
            "single_cell_contiguous_extension_distinguished": True,
            "single_cell_noncontiguous_extension_distinguished": True,
            "multi_cell_pure_surplus_distinguished": True,
            "mixed_surplus_and_deficit_distinguished": True,
            "structural_or_task_firewall_refusal_distinguished": True,
        },
        "refusals": {
            "direct_refusals": sum(refusal_counts.values()),
            "route_counts": dict(sorted(refusal_counts.items())),
        },
        "measurements": {
            "fixed_input_bytes": fixed_input_bytes,
            "generated_input_bytes": generated_input_bytes,
            "aggregate_output_bytes": 0,
            "retained_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "operation_counters": dict(registered["forbidden_operations"]),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "topology_classes_do_not_identify_the_consumed_private_topology",
            "no_real_cohort_archive_member_neural_payload_or_scientific_result",
        ],
        "unavailable_fields": [
            "private_exact_task_total_or_difference",
            "private_cell_topology_identity_or_run_set",
            "real_target_free_cohort",
            "archive_member_integrity",
            "neural_signal_event_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": registered["claim_boundary"],
    }
    output_bytes = -1
    while report["measurements"]["aggregate_output_bytes"] != output_bytes:
        report["measurements"]["aggregate_output_bytes"] = output_bytes
        output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    _assert_public_report_safe(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        aggregate_output_bytes=output_bytes,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the fixed generated-only plan with no private executor."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "lane_id": LANE_ID,
        "status": "registered_generated_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": len(CASES) * len(ORDERS) * REPLAYS,
        "VR35A_calls": contract["generated_matrix"]["VR35A_calls"],
        "direct_refusal_minimum": contract["generated_matrix"]["minimum_direct_refusals"],
        "private_access_authorized": False,
        "real_cohort_freeze_authorized": False,
        "FW2_or_CIL1_authorized": False,
        "execute_surface_available": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 exact-task surplus decomposition."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except ExactTaskSurplusDecompositionRefusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                allow_nan=False,
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 2
    print(_canonical_json_bytes(payload).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
