"""Generated-only discriminator for the two VR26P R5 route classes."""

from __future__ import annotations

import argparse
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

from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR27A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r5_inventory_taxonomy_discriminator_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r5_inventory_taxonomy_discriminator_result"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_r5_inventory_taxonomy_discriminator_contract.v0.json"
)
CONTRACT_SHA256 = "495f83d6428ebc474fd232c9da65808c434a7439e812066ccd9033b9f468ded6"
GREEN_REGISTRATION_COMMIT = "47ceba3ed89df9610540fe3ed2ee8071ac1b84df"
GREEN_REGISTRATION_CI_RUN_ID = 32_611_101_033
GREEN_REGISTRATION_BASE_JOB_ID = 97_124_216_923
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_124_216_871
SUCCESS_ROUTE = "MARC2VR27A-G1"
INVENTORY_ROUTE = "MARC2VR27A-R1"
TAXONOMY_ROUTE = "MARC2VR27A-R2"
REFUSAL_ROUTES = tuple(f"MARC2VR27A-F{index:02d}" for index in range(1, 7))
CASES = (
    "exact_public_control",
    "eligible_bundle_removed",
    "eligible_bundle_added",
    "eligible_distribution_shift",
    "unknown_participant_bundle",
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
PRIVATE_PAYLOAD_FIELDS = {
    "failure_detail",
    "member_name",
    "observed_count",
    "participant_id",
    "private_manifest",
    "private_value",
    "selected_rows",
    "selection_identity",
    "source_exact_name",
    "source_path",
    "subject_id",
    "target_text",
    "target_value",
    "upstream_safe_reason",
    "upstream_value",
    "validation_row",
}


class R5InventoryTaxonomyDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR27A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR27A refusal route")
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
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR27A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise R5InventoryTaxonomyDiscriminatorRefusal(
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
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "47ceba3ed89df9610540fe3ed2ee8071ac1b84df"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_611_101_033
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_124_216_923
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_124_216_871
    ):
        raise R5InventoryTaxonomyDiscriminatorRefusal(
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
        raise R5InventoryTaxonomyDiscriminatorRefusal(
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
            raise R5InventoryTaxonomyDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / item["path"]).read_bytes()
        except (OSError, TypeError) as exc:
            raise R5InventoryTaxonomyDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != item["bytes"] or _sha256_bytes(payload) != item["sha256"]:
            raise R5InventoryTaxonomyDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated case differs"
        )
    if order not in ORDERS:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated order differs"
        )
    return vr25a.build_generated_case(case, order)


def _map_upstream_route(upstream_route: str) -> str:
    mapping = {
        vr25a.SUCCESS_ROUTES[0]: SUCCESS_ROUTE,
        "MARC2VR25A-R1": INVENTORY_ROUTE,
        "MARC2VR25A-R2": TAXONOMY_ROUTE,
    }
    try:
        return mapping[upstream_route]
    except KeyError as exc:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "upstream route is outside R5 discriminator"
        ) from exc


def discriminate_generated_source(source: Mapping[str, Any]) -> tuple[str, str]:
    """Call unchanged VR25A once and return only its aggregate-safe class."""

    before = vr25a._source_bytes(source)
    try:
        outcome = vr25a.apply_selection_boundary_firewall(source)
    except vr25a.SelectionBoundaryFirewallRefusal as exc:
        upstream_route = exc.route
    else:
        upstream_route = outcome.route
    if vr25a._source_bytes(source) != before:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated source changed during discrimination"
        )
    return _map_upstream_route(upstream_route), upstream_route


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise R5InventoryTaxonomyDiscriminatorRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains private field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
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
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except R5InventoryTaxonomyDiscriminatorRefusal as exc:
        return exc.route
    raise R5InventoryTaxonomyDiscriminatorRefusal(
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
        "fixed_input_count",
        "fixed_input_bytes",
        "exact_R1_R2_call_site_total",
        "result_proof",
        "generated_witness_matrix",
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
        routes.append(
            _expect_refusal(lambda value=order: _build_case(CASES[0], value))
        )
    for route in (
        "MARC2VR25A-G2",
        "MARC2VR25A-R3",
        "MARC2VR25A-R4",
        "MARC2VR25A-F01",
        "MARC2VR25A-F02",
        "MARC2VR25A-F03",
        "MARC2VR25A-F04",
        "unknown",
    ):
        routes.append(_expect_refusal(lambda value=route: _map_upstream_route(value)))
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
    if len(routes) < 50:
        raise R5InventoryTaxonomyDiscriminatorRefusal(
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
    """Run the exact 20-path generated-only VR27A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(registered)

    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    generated_input_bytes = 0
    vr25a_calls = 0
    expected = {
        "exact_public_control": (SUCCESS_ROUTE, "MARC2VR25A-G1"),
        "eligible_bundle_removed": (INVENTORY_ROUTE, "MARC2VR25A-R1"),
        "eligible_bundle_added": (INVENTORY_ROUTE, "MARC2VR25A-R1"),
        "eligible_distribution_shift": (INVENTORY_ROUTE, "MARC2VR25A-R1"),
        "unknown_participant_bundle": (TAXONOMY_ROUTE, "MARC2VR25A-R2"),
    }
    replay_signatures: list[list[tuple[str, str, str, str]]] = []
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str, str]] = []
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                payload = vr25a._source_bytes(source)
                generated_input_bytes += len(payload)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(payload))
                route, upstream = discriminate_generated_source(source)
                vr25a_calls += 1
                if (route, upstream) != expected[case]:
                    raise R5InventoryTaxonomyDiscriminatorRefusal(
                        REFUSAL_ROUTES[3], "generated route differs"
                    )
                signature.append((case, order, route, upstream))
                route_counts[route] += 1
                upstream_counts[upstream] += 1
        replay_signatures.append(signature)
    expected_route_counts = Counter(
        registered["generated_witness_matrix"]["expected_VR27A_route_counts"]
    )
    if (
        vr25a_calls != 20
        or route_counts != expected_route_counts
        or upstream_counts
        != Counter(
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-R1": 12,
                "MARC2VR25A-R2": 4,
            }
        )
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
    ):
        raise R5InventoryTaxonomyDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated replay or route counts differ"
        )

    runtime = clock() - started
    rss = peak_rss()
    replay_digest = _sha256_bytes(_canonical_json_bytes(replay_signatures))
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_inventory_taxonomy_discriminator_qualified",
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
            "paths": vr25a_calls,
            "VR25A_calls": vr25a_calls,
            "VR27A_route_counts": dict(sorted(route_counts.items())),
            "VR25A_route_counts": dict(sorted(upstream_counts.items())),
            "exact_replays_match": True,
            "order_invariant_route_distribution": True,
            "replay_digest": replay_digest,
            "direct_refusals_passed": direct_refusals,
            "source_mutations_after_call": 0,
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
            "generated_R1_and_R2_do_not_identify_the_consumed_private_branch",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "consumed_private_R1_or_R2_route",
            "private_predicate_value_count_direction_or_participant",
            "real_target_free_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated discrimination of VR25A eligible-inventory drift "
                "versus unknown-participant taxonomy"
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
            "neurodecodekit.marc2_r5_inventory_taxonomy_discriminator_plan"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": 20,
        "VR25A_calls": 20,
        "minimum_direct_refusals": 50,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 R5 inventory/taxonomy discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_plan() if args.command == "plan" else qualify_generated()
    except R5InventoryTaxonomyDiscriminatorRefusal as exc:
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
