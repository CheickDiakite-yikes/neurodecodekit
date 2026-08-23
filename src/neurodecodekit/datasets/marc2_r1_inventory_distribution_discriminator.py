"""Generated-only discriminator for the two VR28P R1 route classes."""

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
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR29A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r1_inventory_distribution_discriminator_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r1_inventory_distribution_discriminator_result"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_r1_inventory_distribution_discriminator_contract.v0.json"
)
VR2_RELATIVE_PATH = Path(
    "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py"
)
CONTRACT_SHA256 = "09fc1baa9e84d65bf8d9e8780d77a2d6707c27a8c30b6b49387c027ac020c607"
GREEN_REGISTRATION_COMMIT = "fcd088cc2eef6556f36ed596c6d9bb6c7ee9d7c3"
GREEN_REGISTRATION_CI_RUN_ID = 32_618_866_986
GREEN_REGISTRATION_BASE_JOB_ID = 97_143_828_645
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_143_828_576
SUCCESS_ROUTES = ("MARC2VR29A-G1", "MARC2VR29A-G2")
INVENTORY_TOTAL_ROUTE = "MARC2VR29A-R1"
DISTRIBUTION_ROUTE = "MARC2VR29A-R2"
OUT_OF_SCOPE_ROUTE = "MARC2VR29A-R3"
REFUSAL_ROUTES = tuple(f"MARC2VR29A-F{index:02d}" for index in range(1, 7))
FILTER_REASON_ROUTES = {
    "filtered eligible total differs": INVENTORY_TOTAL_ROUTE,
    "eligible participant-session counts differ": DISTRIBUTION_ROUTE,
}
CASES = (
    "exact_public_control",
    "single_session_exclusion_removed",
    "eligible_bundle_removed",
    "eligible_bundle_added",
    "eligible_distribution_shift",
    "eligible_distribution_shift_second",
    "unknown_participant_bundle",
    "incomplete_companion_set",
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
    "cohort",
    "difference_direction",
    "difference_magnitude",
    "distribution",
    "eligible_total",
    "failed_predicate",
    "failure_detail",
    "member_name",
    "observed_count",
    "observed_distribution",
    "participant_id",
    "participant_session_counts",
    "private_manifest",
    "private_value",
    "reason",
    "reservation",
    "safe_reason",
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


class R1InventoryDistributionDiscriminatorRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR29A refusal route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR29A refusal route")
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
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR29A registration."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise R1InventoryDistributionDiscriminatorRefusal(
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
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "fcd088cc2eef6556f36ed596c6d9bb6c7ee9d7c3"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_618_866_986
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_143_828_645
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_143_828_576
    ):
        raise R1InventoryDistributionDiscriminatorRefusal(
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
        raise R1InventoryDistributionDiscriminatorRefusal(
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
            raise R1InventoryDistributionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            payload = (base / item["path"]).read_bytes()
        except (OSError, TypeError) as exc:
            raise R1InventoryDistributionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != item["bytes"] or _sha256_bytes(payload) != item["sha256"]:
            raise R1InventoryDistributionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total


def _filter_site_reasons(root: Path | None = None) -> tuple[str, ...]:
    try:
        source = ((root or _repo_root()) / VR2_RELATIVE_PATH).read_text(
            encoding="utf-8"
        )
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "VR2 source inventory is unavailable"
        ) from exc
    function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_filter_and_validate_eligible"
        ),
        None,
    )
    if function is None:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "VR2 filter helper is unavailable"
        )
    reasons: list[str] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
            continue
        if not isinstance(node.exc.func, ast.Name):
            continue
        if node.exc.func.id != "LiveDomainEligibilityRefusal":
            continue
        if len(node.exc.args) != 2 or not isinstance(node.exc.args[1], ast.Constant):
            raise R1InventoryDistributionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "VR2 filter refusal signature differs"
            )
        reason = node.exc.args[1].value
        if not isinstance(reason, str):
            raise R1InventoryDistributionDiscriminatorRefusal(
                REFUSAL_ROUTES[0], "VR2 filter reason differs"
            )
        reasons.append(reason)
    return tuple(reasons)


def _verify_filter_sites(contract: Mapping[str, Any]) -> int:
    expected = tuple(
        row["frozen_internal_safe_reason"]
        for row in contract["ordered_R1_route_inventory"].values()
    )
    reasons = _filter_site_reasons()
    if reasons != expected or set(reasons) != set(FILTER_REASON_ROUTES):
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[0], "VR2 filter refusal inventory differs"
        )
    return len(reasons)


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != value for key, value in THREAD_ENVIRONMENT.items()):
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated case differs"
        )
    if order not in ORDERS:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[1], "generated order differs"
        )
    if case != "eligible_distribution_shift_second":
        return vr25a.build_generated_case(case, order)
    source = vr25a.build_generated_case("exact_public_control", "canonical")
    vr25a._move_bundle(
        source,
        ("sub-20", "ses-02", 5),
        ("sub-22", "ses-02", 4),
    )
    source["entries"] = sorted(
        source["entries"], key=lambda row: row["member_name"]
    )
    if order == "reversed":
        source["entries"].reverse()
    return source


def _map_filter_reason(reason: str) -> str:
    try:
        return FILTER_REASON_ROUTES[reason]
    except KeyError as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "VR2 filter route is outside R1 discriminator"
        ) from exc


def _map_non_r1_upstream(upstream_route: str) -> str:
    mapping = {
        vr25a.SUCCESS_ROUTES[0]: SUCCESS_ROUTES[0],
        vr25a.SUCCESS_ROUTES[1]: SUCCESS_ROUTES[1],
        "MARC2VR25A-R2": OUT_OF_SCOPE_ROUTE,
        "MARC2VR25A-R3": OUT_OF_SCOPE_ROUTE,
    }
    try:
        return mapping[upstream_route]
    except KeyError as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "upstream route is outside R1 discriminator"
        ) from exc


def _discriminate_r1_filter(source: Mapping[str, Any]) -> str:
    contract = vr2.load_registered_contract()
    try:
        vr2._verify_contract_mapping(contract)
        entries = vr2._validate_live_envelope(source, contract)
        grouped, _kinds = vr25a.vr20a._group_rows(entries)
        labels = {key: vr2._classify_key(key, contract) for key in grouped}
        vr2._filter_and_validate_eligible(grouped, labels, contract)
    except vr2.LiveDomainEligibilityRefusal as exc:
        return _map_filter_reason(exc.reason)
    except vr25a.vr20a.PublishedTaskSelectorRepairRefusal as exc:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[2], "R1 structural replay refused"
        ) from exc
    raise R1InventoryDistributionDiscriminatorRefusal(
        REFUSAL_ROUTES[2], "R1 filter unexpectedly passed"
    )


def discriminate_generated_source(source: Mapping[str, Any]) -> tuple[str, str, int]:
    """Call unchanged VR25A once and return only the aggregate-safe R1 subclass."""

    before = vr25a._source_bytes(source)
    try:
        outcome = vr25a.apply_selection_boundary_firewall(source)
    except vr25a.SelectionBoundaryFirewallRefusal as exc:
        upstream_route = exc.route
    else:
        upstream_route = outcome.route
    filter_calls = 0
    if upstream_route == "MARC2VR25A-R1":
        route = _discriminate_r1_filter(source)
        filter_calls = 1
    else:
        route = _map_non_r1_upstream(upstream_route)
    if vr25a._source_bytes(source) != before:
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[3], "generated source changed during discrimination"
        )
    return route, upstream_route, filter_calls


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise R1InventoryDistributionDiscriminatorRefusal(
                    REFUSAL_ROUTES[4], "aggregate report contains private field"
                )
            _walk_public(child)
    elif isinstance(value, list):
        for child in value:
            _walk_public(child)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    if len(_canonical_json_bytes(report)) > 1_048_576:
        raise R1InventoryDistributionDiscriminatorRefusal(
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
        raise R1InventoryDistributionDiscriminatorRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(action: Callable[[], Any]) -> str:
    try:
        action()
    except R1InventoryDistributionDiscriminatorRefusal as exc:
        return exc.route
    raise R1InventoryDistributionDiscriminatorRefusal(
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
        "ordered_R1_route_inventory",
        "exact_R1_call_site_total",
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
    for reason in ("", "unknown", "private", "count", "distribution", "participant"):
        routes.append(_expect_refusal(lambda value=reason: _map_filter_reason(value)))
    for upstream in (
        "MARC2VR25A-R1",
        "MARC2VR25A-R4",
        "MARC2VR25A-F01",
        "MARC2VR25A-F02",
        "MARC2VR25A-F03",
        "MARC2VR25A-F04",
        "unknown",
    ):
        routes.append(_expect_refusal(lambda value=upstream: _map_non_r1_upstream(value)))
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
        raise R1InventoryDistributionDiscriminatorRefusal(
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
    """Run the exact 32-path generated-only VR29A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes = _verify_fixed_inputs(registered)
    filter_site_count = _verify_filter_sites(registered)
    _validate_thread_environment(environment)
    direct_refusals = _run_direct_refusals(registered)

    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_hashes: dict[str, list[str]] = {
        f"{case}:{order}": [] for case in CASES for order in ORDERS
    }
    generated_input_bytes = 0
    vr25a_calls = 0
    filter_calls = 0
    expected = {
        "exact_public_control": (SUCCESS_ROUTES[0], "MARC2VR25A-G1", 0),
        "single_session_exclusion_removed": (
            SUCCESS_ROUTES[1],
            "MARC2VR25A-G2",
            0,
        ),
        "eligible_bundle_removed": (
            INVENTORY_TOTAL_ROUTE,
            "MARC2VR25A-R1",
            1,
        ),
        "eligible_bundle_added": (
            INVENTORY_TOTAL_ROUTE,
            "MARC2VR25A-R1",
            1,
        ),
        "eligible_distribution_shift": (
            DISTRIBUTION_ROUTE,
            "MARC2VR25A-R1",
            1,
        ),
        "eligible_distribution_shift_second": (
            DISTRIBUTION_ROUTE,
            "MARC2VR25A-R1",
            1,
        ),
        "unknown_participant_bundle": (
            OUT_OF_SCOPE_ROUTE,
            "MARC2VR25A-R2",
            0,
        ),
        "incomplete_companion_set": (
            OUT_OF_SCOPE_ROUTE,
            "MARC2VR25A-R3",
            0,
        ),
    }
    replay_signatures: list[list[tuple[str, str, str, str, int]]] = []
    for _replay in range(REPLAYS):
        signature: list[tuple[str, str, str, str, int]] = []
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                payload = vr25a._source_bytes(source)
                generated_input_bytes += len(payload)
                replay_hashes[f"{case}:{order}"].append(_sha256_bytes(payload))
                route, upstream, case_filter_calls = discriminate_generated_source(source)
                vr25a_calls += 1
                filter_calls += case_filter_calls
                if (route, upstream, case_filter_calls) != expected[case]:
                    raise R1InventoryDistributionDiscriminatorRefusal(
                        REFUSAL_ROUTES[3], "generated route differs"
                    )
                signature.append((case, order, route, upstream, case_filter_calls))
                route_counts[route] += 1
                upstream_counts[upstream] += 1
        replay_signatures.append(signature)
    matrix = registered["generated_witness_matrix"]
    expected_route_counts = Counter(matrix["expected_VR29A_route_counts"])
    if (
        vr25a_calls != matrix["required_VR25A_calls"]
        or filter_calls != matrix["required_R1_filter_discriminator_calls"]
        or route_counts != expected_route_counts
        or upstream_counts
        != Counter(
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-G2": 4,
                "MARC2VR25A-R1": 16,
                "MARC2VR25A-R2": 4,
                "MARC2VR25A-R3": 4,
            }
        )
        or replay_signatures[0] != replay_signatures[1]
        or any(len(set(values)) != 1 for values in replay_hashes.values())
    ):
        raise R1InventoryDistributionDiscriminatorRefusal(
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
        "status": "generated_inventory_distribution_discriminator_qualified",
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
            "R1_filter_discriminator_calls": filter_calls,
            "VR2_filter_refusal_sites": filter_site_count,
            "VR29A_route_counts": dict(sorted(route_counts.items())),
            "VR25A_route_counts": dict(sorted(upstream_counts.items())),
            "exact_replays_match": True,
            "order_invariant_route_distribution": True,
            "replay_digest": replay_digest,
            "direct_refusals_passed": direct_refusals,
            "source_mutations_after_call": 0,
            "private_reason_or_value_retained": False,
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
            "generated_R1_subclasses_do_not_identify_the_consumed_private_subclass",
            "no_real_cohort_neural_decoding_or_scientific_claim",
        ],
        "unavailable_fields": [
            "consumed_private_R1_subclass",
            "private_predicate_value_count_direction_distribution_or_participant",
            "real_target_free_cohort",
            "archive_member_neural_signal_target_model_prediction_or_score",
            "end_to_end_neural_decoding_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated discrimination of filtered eligible-total arithmetic "
                "versus participant-session distribution arithmetic"
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
            "neurodecodekit.marc2_r1_inventory_distribution_discriminator_plan"
        ),
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": _verify_fixed_inputs(contract),
        "VR2_filter_refusal_sites": _verify_filter_sites(contract),
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": 32,
        "VR25A_calls": 32,
        "R1_filter_discriminator_calls": 16,
        "minimum_direct_refusals": 70,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 R1 inventory/distribution discriminator."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        report = build_plan() if args.command == "plan" else qualify_generated()
    except R1InventoryDistributionDiscriminatorRefusal as exc:
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
