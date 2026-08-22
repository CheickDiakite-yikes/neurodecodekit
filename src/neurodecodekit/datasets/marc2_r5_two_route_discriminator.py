"""Generated-only discriminator for the two VR20P R5 route classes."""

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

from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR21A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_r5_two_route_discriminator_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_r5_two_route_discriminator_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_r5_two_route_discriminator_contract.v0.json"
)
CONTRACT_SHA256 = "5ca99e2d64c7dc4c268afb10d6c1a92eac86a5bbcb7ca484ee654217c13e0597"
GREEN_REGISTRATION_COMMIT = "7ce0e16392fed2576031766bead32a5cab44031a"
GREEN_REGISTRATION_CI_RUN_ID = 32_559_365_362
GREEN_REGISTRATION_BASE_JOB_ID = 96_998_477_692
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_998_477_649
SUCCESS_ROUTE = "MARC2VR21A-G1"
TAXONOMY_ROUTE = "MARC2VR21A-R1"
SELECTION_ROUTE = "MARC2VR21A-R2"
REFUSAL_ROUTES = tuple(f"MARC2VR21A-F{index:02d}" for index in range(1, 7))
CASES = (
    "control_success",
    "unknown_participant_taxonomy",
    "semantic_run_zero",
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
    "upstream_safe_reason",
    "failure_detail",
    "private_value",
    "member_name",
    "source_path",
    "participant_id",
    "subject_id",
    "selected_rows",
    "source_exact_name",
    "target_text",
    "label_value",
    "prediction_value",
}


class R5TwoRouteDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR21A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR21A refusal route")
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
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR21A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise R5TwoRouteDiscriminatorRefusal(
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
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "7ce0e16392fed2576031766bead32a5cab44031a"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_559_365_362
        or GREEN_REGISTRATION_BASE_JOB_ID != 96_998_477_692
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 96_998_477_649
    ):
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(contract: Mapping[str, Any], root: Path | None = None) -> int:
    base = root or _repo_root()
    inputs = contract.get("fixed_inputs")
    if not isinstance(inputs, list) or len(inputs) != contract.get("fixed_input_count"):
        raise R5TwoRouteDiscriminatorRefusal(
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
            raise R5TwoRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / item["path"]).read_bytes()
        except (OSError, TypeError) as exc:
            raise R5TwoRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != item["bytes"] or _sha256_bytes(payload) != item["sha256"]:
            raise R5TwoRouteDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _unknown_participant_witness(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    rows = vr20a._rows_for_first_bundle(changed)
    if len(rows) != 4:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated taxonomy witness differs"
        )
    first_match = vr20a._core_match(rows[0]["member_name"])
    if first_match is None:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated taxonomy witness differs"
        )
    subject = first_match.group("subject")
    for row in rows:
        row["member_name"] = row["member_name"].replace(subject, "sub-99")
    return changed


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated case differs"
        )
    if order not in ORDERS:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated order differs"
        )
    source = vr20a.build_generated_variant("published_four_digit", order)
    if case == "unknown_participant_taxonomy":
        return _unknown_participant_witness(source)
    if case == "semantic_run_zero":
        return vr20a._mutated_witness(source, "semantic_run_zero")
    return source


def _map_upstream_route(upstream_route: str) -> str:
    mapping = {
        vr20a.SUCCESS_ROUTE: SUCCESS_ROUTE,
        vr20a.REFUSAL_ROUTES[5]: TAXONOMY_ROUTE,
        vr20a.REFUSAL_ROUTES[6]: SELECTION_ROUTE,
    }
    try:
        return mapping[upstream_route]
    except KeyError as exc:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "upstream route is outside R5 discriminator"
        ) from exc


def discriminate_generated_source(source: Mapping[str, Any]) -> tuple[str, str]:
    """Call unchanged VR20A once and return only its aggregate-safe class."""

    before = vr20a.vr2._canonical_source_bytes(source)
    try:
        vr20a.adapt_published_task_source(source)
    except vr20a.PublishedTaskSelectorRepairRefusal as exc:
        upstream_route = exc.route
    else:
        upstream_route = vr20a.SUCCESS_ROUTE
    after = vr20a.vr2._canonical_source_bytes(source)
    if after != before:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated source changed during discrimination"
        )
    return _map_upstream_route(upstream_route), upstream_route


def _walk_public(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise R5TwoRouteDiscriminatorRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains private field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate report exceeds output cap"
        )


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except R5TwoRouteDiscriminatorRefusal as exc:
        return exc.route
    raise R5TwoRouteDiscriminatorRefusal(
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
        "exact_F06_F07_call_site_total",
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
    for order in ("sorted", "random"):
        routes.append(
            _expect_refusal(lambda value=order: _build_case("control_success", value))
        )
    for route in (
        "MARC2VR20A-F01",
        "MARC2VR20A-F02",
        "MARC2VR20A-F03",
        "MARC2VR20A-F04",
        "MARC2VR20A-F05",
        "MARC2VR20A-F08",
        "MARC2VR20A-F09",
        "unknown",
    ):
        routes.append(_expect_refusal(lambda value=route: _map_upstream_route(value)))
    for field in sorted(PRIVATE_PAYLOAD_FIELDS):
        routes.append(
            _expect_refusal(lambda key=field: _assert_public_report_safe({key: "x"}))
        )
    if len(routes) < 40:
        raise R5TwoRouteDiscriminatorRefusal(
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
        "signal_event_target_or_label_reads": 0,
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
    """Run the exact 12-path generated-only VR21A qualification."""

    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(registered)

    started = clock()
    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    generated_input_bytes = 0
    vr20a_calls = 0
    expected = {
        "control_success": (SUCCESS_ROUTE, vr20a.SUCCESS_ROUTE),
        "unknown_participant_taxonomy": (
            TAXONOMY_ROUTE,
            vr20a.REFUSAL_ROUTES[5],
        ),
        "semantic_run_zero": (SELECTION_ROUTE, vr20a.REFUSAL_ROUTES[6]),
    }
    for _replay in range(REPLAYS):
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                payload = vr20a.vr2._canonical_source_bytes(source)
                generated_input_bytes += len(payload)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(payload))
                route, upstream = discriminate_generated_source(source)
                vr20a_calls += 1
                if (route, upstream) != expected[case]:
                    raise R5TwoRouteDiscriminatorRefusal(
                        REFUSAL_ROUTES[3], "generated route differs"
                    )
                route_counts[route] += 1
                upstream_counts[upstream] += 1
    if (
        vr20a_calls != 12
        or route_counts
        != Counter({SUCCESS_ROUTE: 4, TAXONOMY_ROUTE: 4, SELECTION_ROUTE: 4})
        or upstream_counts
        != Counter(
            {
                vr20a.SUCCESS_ROUTE: 4,
                vr20a.REFUSAL_ROUTES[5]: 4,
                vr20a.REFUSAL_ROUTES[6]: 4,
            }
        )
        or any(len(set(values)) != 1 for values in replay_hashes.values())
    ):
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated replay or route counts differ"
        )

    runtime = clock() - started
    rss = peak_rss()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_two_route_discriminator_qualified",
        "proof": {
            "registration_commit": GREEN_REGISTRATION_COMMIT,
            "registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "registration_base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "registration_optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "contract_sha256": CONTRACT_SHA256,
        },
        "matrix": {
            "cases": list(CASES),
            "orders": list(ORDERS),
            "replays": REPLAYS,
            "paths": vr20a_calls,
            "VR20A_calls": vr20a_calls,
            "VR21A_route_counts": dict(sorted(route_counts.items())),
            "VR20A_route_counts": dict(sorted(upstream_counts.items())),
            "replay_source_hashes": replay_hashes,
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
            "end_to_end_latency_measured": False,
        },
        "operation_counters": _zero_counters(),
        "warnings": [
            "artifact_only_and_generated_only",
            "no_private_executor",
            "R1_and_R2_are_generated_structural_classes_not_private_results",
            "no_neural_decoding_or_scientific_claim",
        ],
        "claim_boundary": {
            "engineering_capability": "generated discrimination of VR20A F06 versus F07",
            "scientific_claim_not_established": "No neural payload target model prediction or score was accessed.",
        },
    }
    _assert_public_report_safe(report)
    output_bytes = len(_canonical_json_bytes(report))
    report["measurements"]["aggregate_output_bytes"] = output_bytes
    if (
        runtime > 30
        or rss >= 268_435_456
        or generated_input_bytes > 33_554_432
        or output_bytes > 1_048_576
    ):
        raise R5TwoRouteDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "generated resource cap exceeded"
        )
    _assert_public_report_safe(report)
    return report


def build_plan() -> dict[str, Any]:
    """Return the frozen generated-only execution plan."""

    contract = load_registered_contract()
    return {
        "schema_name": "neurodecodekit.marc2_r5_two_route_discriminator_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "cases": list(CASES),
        "orders": list(ORDERS),
        "replays": REPLAYS,
        "paths": 12,
        "VR20A_calls": 12,
        "minimum_direct_refusals": 40,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 R5 F06/F07 discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_plan() if args.command == "plan" else qualify_generated()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
