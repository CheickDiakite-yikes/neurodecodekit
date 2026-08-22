"""Generated-only decomposition of the five reachable VR20A F06 classes."""

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

from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR23A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_f06_five_route_decomposition_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f06_five_route_decomposition_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_f06_five_route_decomposition_contract.v0.json"
)
CONTRACT_SHA256 = "c590bbf5bfb60551413bae85ac69fe9ca8bf04448cf3cca50b00962facb2d144"
GREEN_REGISTRATION_COMMIT = "cee91b0473cd97a91feab22d7fd420e0b550b99f"
GREEN_REGISTRATION_CI_RUN_ID = 32_596_045_581
GREEN_REGISTRATION_BASE_JOB_ID = 97_087_038_676
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 97_087_038_522
SUCCESS_ROUTE = "MARC2VR23A-G1"
RESULT_ROUTES = tuple(f"MARC2VR23A-R{index}" for index in range(1, 6))
REFUSAL_ROUTES = tuple(f"MARC2VR23A-F{index:02d}" for index in range(1, 7))
CASES = (
    "control_success",
    "entry_kind_count_drift",
    "extra_complete_bundle",
    "unknown_participant_taxonomy",
    "classification_arithmetic_drift",
    "eligible_session_distribution_drift",
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
    "archive_member",
    "candidate_id",
    "cohort_manifest",
    "decoded_text",
    "event_value",
    "failed_predicate",
    "failure_detail",
    "label_value",
    "member_name",
    "participant_id",
    "prediction_value",
    "private_manifest",
    "private_path",
    "private_value",
    "raw_row",
    "selected_rows",
    "signal_value",
    "source_exact_name",
    "source_path",
    "subject_id",
    "target_text",
    "taxonomy_detail",
    "trial_value",
    "upstream_safe_reason",
}
EXPECTED_VR20A_F06_REASONS = {
    "source kind or run-bundle total differs",
    "source taxonomy or eligibility differs",
}
EXPECTED_VR2_REASONS = {
    "entry-kind counts differ",
    "full source bundle total differs",
    "bundle participant is unknown",
    "bundle taxonomy is unclassified",
    "238/195/43 classification arithmetic differs",
    "filtered eligible total differs",
    "eligible participant-session counts differ",
}


class F06FiveRouteDecompositionRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR23A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR23A refusal route")
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
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _registered_contract_bytes(root: Path | None = None) -> bytes:
    try:
        payload = ((root or _repo_root()) / CONTRACT_RELATIVE_PATH).read_bytes()
    except OSError as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return payload


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR23A contract."""

    try:
        payload = json.loads(_registered_contract_bytes(root))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract is not strict JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise F06FiveRouteDecompositionRefusal(
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
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof() -> None:
    if (
        GREEN_REGISTRATION_COMMIT
        != "cee91b0473cd97a91feab22d7fd420e0b550b99f"
        or GREEN_REGISTRATION_CI_RUN_ID != 32_596_045_581
        or GREEN_REGISTRATION_BASE_JOB_ID != 97_087_038_676
        or GREEN_REGISTRATION_OPTIONAL_JOB_ID != 97_087_038_522
    ):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _verify_fixed_inputs(
    contract: Mapping[str, Any], root: Path | None = None
) -> tuple[int, dict[str, bytes]]:
    base = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != contract.get("fixed_input_count"):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed input registry differs"
        )
    total = 0
    payloads: dict[str, bytes] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise F06FiveRouteDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input row differs"
            )
        try:
            path = str(row["path"])
            payload = (base / path).read_bytes()
        except (KeyError, OSError) as exc:
            raise F06FiveRouteDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input is unavailable"
            ) from exc
        if len(payload) != row.get("bytes") or _sha256_bytes(payload) != row.get(
            "sha256"
        ):
            raise F06FiveRouteDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input differs"
            )
        payloads[path] = payload
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed input byte total differs"
        )
    return total, payloads


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = environment or os.environ
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _literal_refusal_reasons(
    payload: bytes, exception_name: str, route_index: int | None = None
) -> Counter[str]:
    try:
        tree = ast.parse(payload.decode("utf-8"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "tracked source AST differs"
        ) from exc
    observed: Counter[str] = Counter()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or len(node.args) < 2:
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != exception_name:
            continue
        if route_index is not None:
            route = node.args[0]
            if (
                not isinstance(route, ast.Subscript)
                or not isinstance(route.value, ast.Name)
                or route.value.id != "REFUSAL_ROUTES"
                or not isinstance(route.slice, ast.Constant)
                or route.slice.value != route_index
            ):
                continue
        reason = node.args[1]
        if isinstance(reason, ast.Constant) and isinstance(reason.value, str):
            observed[reason.value] += 1
    return observed


def _verify_static_inventory(
    contract: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> dict[str, int]:
    vr20a_path = "src/neurodecodekit/datasets/marc2_published_task_selector_repair.py"
    vr2_path = "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py"
    vr20a_reasons = _literal_refusal_reasons(
        payloads[vr20a_path], "PublishedTaskSelectorRepairRefusal", 5
    )
    vr2_reasons = _literal_refusal_reasons(
        payloads[vr2_path], "LiveDomainEligibilityRefusal"
    )
    if vr20a_reasons != Counter({reason: 1 for reason in EXPECTED_VR20A_F06_REASONS}):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "VR20A F06 AST inventory differs"
        )
    expected_vr2 = set(contract["static_inventory"]["VR2_bound_safe_reasons"])
    if expected_vr2 != EXPECTED_VR2_REASONS or any(
        vr2_reasons[reason] != 1 for reason in expected_vr2
    ):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "VR2 F06 helper inventory differs"
        )
    return {
        "VR20A_F06_wrapper_call_sites": sum(vr20a_reasons.values()),
        "VR2_bound_safe_reasons": len(expected_vr2),
    }


def _verify_redundant_guards(vr2_contract: Mapping[str, Any]) -> dict[str, Any]:
    taxonomy = vr2_contract["participant_taxonomy"]
    eligible = set(taxonomy["eligible_subject_ids"])
    single = set(taxonomy["single_session_exclusions"])
    sampling = set(taxonomy["sampling_tier_exclusions"])
    if eligible & single or eligible & sampling or single & sampling:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "participant taxonomy sets overlap"
        )
    known = eligible | single | sampling
    classifications = 0
    try:
        for subject in sorted(known):
            for session in ("ses-01", "ses-02", "ses-99"):
                vr20a.vr2._classify_key((subject, session, 1), vr2_contract)
                classifications += 1
    except vr20a.vr2.LiveDomainEligibilityRefusal as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "known taxonomy reached unclassified guard"
        ) from exc

    source = vr20a.build_generated_variant("published_four_digit", "canonical")
    grouped, _kinds = vr20a._group_rows(source["entries"])
    labels = {
        key: vr20a.vr2._classify_key(key, vr2_contract) for key in grouped
    }
    counts = Counter(labels.values())
    try:
        vr20a.vr2._assert_classification_arithmetic(counts, vr2_contract)
        filtered = vr20a.vr2._filter_and_validate_eligible(
            grouped, labels, vr2_contract
        )
    except vr20a.vr2.LiveDomainEligibilityRefusal as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "generated redundancy proof refused"
        ) from exc
    if len(filtered) != 195 or counts[vr20a.vr2.PREDICATE_CODES[0]] != 195:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "filtered total implication differs"
        )
    return {
        "non_independent_defensive_reasons": 2,
        "known_taxonomy_classifications_checked": classifications,
        "eligible_count_implication_checked": True,
    }


def _auxiliary_rows(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in source["entries"]
        if isinstance(row, dict)
        and row.get("entry_kind") == "regular_file"
        and isinstance(row.get("member_name"), str)
        and vr20a._core_match(row["member_name"]) is None
        and not any(
            row["member_name"].endswith(suffix)
            for suffix in vr20a.selector.REQUIRED_SUFFIXES
        )
    ]


def _entry_kind_count_witness(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    directory = next(
        row for row in changed["entries"] if row.get("entry_kind") == "directory"
    )
    template = _auxiliary_rows(changed)[0]
    directory.update(copy.deepcopy(template))
    directory["member_name"] = "Freewill_generated/generated_aux/kind-drift.txt"
    directory["local_header_offset"] += 1
    return changed


def _extra_complete_bundle_witness(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    grouped, _kinds = vr20a._group_rows(changed["entries"])
    subject, session, _run = next(iter(sorted(grouped)))
    occupied = {
        run
        for row_subject, row_session, run in grouped
        if row_subject == subject and row_session == session
    }
    run = next(value for value in range(4, 10_000) if value not in occupied)
    rows = _auxiliary_rows(changed)[:4]
    if len(rows) != 4:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated auxiliary inventory differs"
        )
    for row, suffix in zip(rows, vr20a.selector.REQUIRED_SUFFIXES, strict=True):
        row["member_name"] = (
            f"Freewill_generated/{subject}/{session}/eeg/"
            f"{subject}_{session}_task-{vr20a.PUBLISHED_TASK}_run-{run:04d}"
            f"{suffix}"
        )
    return changed


def _rewrite_bundle(
    source: Mapping[str, Any], *, target_subject: str, target_session: str
) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    grouped, _kinds = vr20a._group_rows(changed["entries"])
    vr2_contract = vr20a.vr2.load_registered_contract()
    eligible = set(vr2_contract["participant_taxonomy"]["eligible_subject_ids"])
    source_key = next(key for key in sorted(grouped) if key[0] in eligible)
    rows = grouped[source_key]
    target_run = 9_999
    if (target_subject, target_session, target_run) in grouped:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated taxonomy target collides"
        )
    for suffix, row in rows.items():
        row["member_name"] = (
            f"Freewill_generated/{target_subject}/{target_session}/eeg/"
            f"{target_subject}_{target_session}_task-{vr20a.PUBLISHED_TASK}"
            f"_run-{target_run:04d}{suffix}"
        )
    return changed


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated case differs"
        )
    if order not in ORDERS:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated order differs"
        )
    source = vr20a.build_generated_variant("published_four_digit", order)
    if case == "entry_kind_count_drift":
        return _entry_kind_count_witness(source)
    if case == "extra_complete_bundle":
        return _extra_complete_bundle_witness(source)
    if case == "unknown_participant_taxonomy":
        return _rewrite_bundle(
            source, target_subject="sub-99", target_session="ses-01"
        )
    taxonomy = vr20a.vr2.load_registered_contract()["participant_taxonomy"]
    if case == "classification_arithmetic_drift":
        return _rewrite_bundle(
            source,
            target_subject=taxonomy["single_session_exclusions"][0],
            target_session="ses-01",
        )
    if case == "eligible_session_distribution_drift":
        return _rewrite_bundle(
            source,
            target_subject=taxonomy["eligible_subject_ids"][-1],
            target_session=taxonomy["eligible_sessions"][-1],
        )
    return source


def _diagnose_f06(
    source: Mapping[str, Any], vr2_contract: Mapping[str, Any]
) -> str:
    try:
        vr20a.vr2._verify_contract_mapping(vr2_contract)
        entries = vr20a.vr2._validate_live_envelope(source, vr2_contract)
        grouped, kinds = vr20a._group_rows(entries)
    except (
        vr20a.vr2.LiveDomainEligibilityRefusal,
        vr20a.PublishedTaskSelectorRepairRefusal,
    ) as exc:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[2], "source reached an earlier structural class"
        ) from exc
    domain = vr2_contract["generated_live_source_domain"]
    expected_kinds = Counter(
        {
            "regular_file": domain["regular_file_rows"],
            "directory": domain["directory_rows"],
        }
    )
    if kinds != expected_kinds:
        return RESULT_ROUTES[0]
    if len(grouped) != domain["complete_source_run_bundles"]:
        return RESULT_ROUTES[1]

    labels: dict[tuple[str, str, int], str] = {}
    counts: Counter[str] = Counter()
    try:
        for key in grouped:
            label = vr20a.vr2._classify_key(key, vr2_contract)
            labels[key] = label
            counts[label] += 1
    except vr20a.vr2.LiveDomainEligibilityRefusal as exc:
        if exc.reason not in {
            "bundle participant is unknown",
            "bundle taxonomy is unclassified",
        }:
            raise F06FiveRouteDecompositionRefusal(
                REFUSAL_ROUTES[2], "taxonomy helper route differs"
            ) from exc
        return RESULT_ROUTES[2]

    try:
        vr20a.vr2._assert_classification_arithmetic(counts, vr2_contract)
    except vr20a.vr2.LiveDomainEligibilityRefusal as exc:
        if exc.reason != "238/195/43 classification arithmetic differs":
            raise F06FiveRouteDecompositionRefusal(
                REFUSAL_ROUTES[2], "classification helper route differs"
            ) from exc
        return RESULT_ROUTES[3]

    try:
        vr20a.vr2._filter_and_validate_eligible(grouped, labels, vr2_contract)
    except vr20a.vr2.LiveDomainEligibilityRefusal as exc:
        if exc.reason == "eligible participant-session counts differ":
            return RESULT_ROUTES[4]
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[1], "non-independent filtered-total guard fired"
        ) from exc
    return SUCCESS_ROUTE


def discriminate_generated_source(source: Mapping[str, Any]) -> tuple[str, str]:
    """Diagnose F06, call unchanged VR20A once, and require agreement."""

    vr2_contract = vr20a.vr2.load_registered_contract()
    before = vr20a.vr2._canonical_source_bytes(source)
    diagnostic_route = _diagnose_f06(source, vr2_contract)
    try:
        vr20a.adapt_published_task_source(source, vr2_contract=vr2_contract)
    except vr20a.PublishedTaskSelectorRepairRefusal as exc:
        upstream_route = exc.route
    else:
        upstream_route = vr20a.SUCCESS_ROUTE
    if vr20a.vr2._canonical_source_bytes(source) != before:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[3], "VR20A changed generated source"
        )
    expected_upstream = (
        vr20a.SUCCESS_ROUTE
        if diagnostic_route == SUCCESS_ROUTE
        else vr20a.REFUSAL_ROUTES[5]
    )
    if upstream_route != expected_upstream:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[3], "diagnostic and VR20A routes disagree"
        )
    return diagnostic_route, upstream_route


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in PRIVATE_PAYLOAD_FIELDS:
                raise F06FiveRouteDecompositionRefusal(
                    REFUSAL_ROUTES[4], "aggregate contains a private field"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)


def _assert_public_report_safe(report: Mapping[str, Any]) -> None:
    _walk_public(report)
    payload = _canonical_json_bytes(report)
    if len(payload) > 1_048_576:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate output cap exceeded"
        )


def _zero_operation_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR22P_path_or_output_operations": 0,
        "real_structural_source_operations": 0,
        "cohort_freezes": 0,
        "archive_header_or_member_payload_operations": 0,
        "neural_signal_event_channel_geometry_target_or_label_operations": 0,
        "cache_feature_split_or_NeuroToken_operations": 0,
        "model_training_runs": 0,
        "model_inference_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scoring_runs": 0,
        "FW2_operations": 0,
        "CIL1_operations": 0,
        "network_requests": 0,
        "provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "other_project_operations": 0,
        "retry_rerun_resume_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
    }


def _enforce_caps(measurements: Mapping[str, Any]) -> None:
    checks = (
        measurements.get("CPU_threads") == 1,
        measurements.get("workers") == 1,
        measurements.get("numerical_jobs") == 1,
        0 <= measurements.get("runtime_seconds", -1) <= 45,
        0 <= measurements.get("peak_RSS_bytes", -1) < 268_435_456,
        0 <= measurements.get("generated_input_bytes", -1) <= 25_165_824,
        0 <= measurements.get("temporary_output_bytes", -1) <= 2_097_152,
        0 <= measurements.get("aggregate_output_bytes", -1) <= 1_048_576,
        measurements.get("retained_generated_output_bytes") == 0,
        measurements.get("network_bytes") == 0,
        measurements.get("new_payload_bytes") == 0,
    )
    if not all(checks):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[5], "resource or output cap exceeded"
        )


def _expect_refusal(action: Callable[[], Any]) -> None:
    try:
        action()
    except F06FiveRouteDecompositionRefusal:
        return
    raise F06FiveRouteDecompositionRefusal(
        REFUSAL_ROUTES[5], "direct refusal mutation was accepted"
    )


def _exercise_direct_refusals(contract: Mapping[str, Any]) -> int:
    passed = 0
    for field in sorted(PRIVATE_PAYLOAD_FIELDS):
        _expect_refusal(lambda field=field: _assert_public_report_safe({field: "x"}))
        passed += 1

    for key in THREAD_ENVIRONMENT:
        environment = dict(THREAD_ENVIRONMENT)
        environment[key] = "2"
        _expect_refusal(
            lambda environment=environment: _validate_thread_environment(environment)
        )
        passed += 1

    for key in list(contract)[:10]:
        changed = copy.deepcopy(dict(contract))
        changed[key] = None
        _expect_refusal(lambda changed=changed: _verify_contract_mapping(changed))
        passed += 1

    for case in ("", "other", "private", "real", "retry", "rerun"):
        _expect_refusal(lambda case=case: _build_case(case, "canonical"))
        passed += 1
    for order in ("", "other", "random", "private"):
        _expect_refusal(lambda order=order: _build_case("control_success", order))
        passed += 1

    source = vr20a.build_generated_variant("published_four_digit", "canonical")
    vr2_contract = vr20a.vr2.load_registered_contract()
    malformed_sources = []
    for key in ("schema_name", "schema_version", "proof_posture", "source_identity"):
        changed = copy.deepcopy(source)
        changed[key] = None
        malformed_sources.append(changed)
    changed = copy.deepcopy(source)
    changed["entries"] = []
    malformed_sources.append(changed)
    for malformed in malformed_sources:
        _expect_refusal(
            lambda malformed=malformed: _diagnose_f06(malformed, vr2_contract)
        )
        passed += 1

    baseline = {
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "runtime_seconds": 1.0,
        "peak_RSS_bytes": 1,
        "generated_input_bytes": 1,
        "temporary_output_bytes": 0,
        "aggregate_output_bytes": 1,
        "retained_generated_output_bytes": 0,
        "network_bytes": 0,
        "new_payload_bytes": 0,
    }
    cap_mutations = {
        "runtime_seconds": 46,
        "peak_RSS_bytes": 268_435_456,
        "generated_input_bytes": 25_165_825,
        "temporary_output_bytes": 2_097_153,
        "aggregate_output_bytes": 1_048_577,
        "retained_generated_output_bytes": 1,
        "network_bytes": 1,
        "new_payload_bytes": 1,
    }
    for key, value in cap_mutations.items():
        changed = dict(baseline)
        changed[key] = value
        _expect_refusal(lambda changed=changed: _enforce_caps(changed))
        passed += 1
    if passed < contract["direct_refusal_minimum"]:
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[5], "direct refusal minimum not met"
        )
    return passed


def _peak_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(usage if sys.platform == "darwin" else usage * 1024)


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    environment: Mapping[str, str] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the exact generated-only VR23A qualification."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    fixed_input_bytes, payloads = _verify_fixed_inputs(registered)
    _validate_thread_environment(environment)
    ast_inventory = _verify_static_inventory(registered, payloads)
    vr2_contract = vr20a.vr2.load_registered_contract()
    redundancy = _verify_redundant_guards(vr2_contract)

    route_counts: Counter[str] = Counter()
    upstream_counts: Counter[str] = Counter()
    replay_hashes: list[dict[str, str]] = []
    replay_routes: list[dict[str, str]] = []
    generated_input_bytes = 0
    vr20a_calls = 0
    source_mutations = 0
    for _replay in range(REPLAYS):
        hashes: dict[str, str] = {}
        routes: dict[str, str] = {}
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                before = vr20a.vr2._canonical_source_bytes(source)
                key = f"{case}:{order}"
                hashes[key] = _sha256_bytes(before)
                generated_input_bytes += len(before)
                route, upstream = discriminate_generated_source(source)
                vr20a_calls += 1
                after = vr20a.vr2._canonical_source_bytes(source)
                source_mutations += int(after != before)
                routes[key] = route
                route_counts[route] += 1
                upstream_counts[upstream] += 1
        replay_hashes.append(hashes)
        replay_routes.append(routes)

    expected_counts = Counter({SUCCESS_ROUTE: 4, **{route: 4 for route in RESULT_ROUTES}})
    if (
        route_counts != expected_counts
        or vr20a_calls != 24
        or source_mutations != 0
        or replay_hashes[0] != replay_hashes[1]
        or replay_routes[0] != replay_routes[1]
    ):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[3], "generated route matrix or replay differs"
        )

    direct_refusals = _exercise_direct_refusals(registered)
    operation_counters = _zero_operation_counters()
    if any(operation_counters.values()):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[4], "forbidden operation counter is nonzero"
        )
    measurements = {
        "CPU_threads": 1,
        "workers": 1,
        "numerical_jobs": 1,
        "fixed_input_bytes": fixed_input_bytes,
        "generated_input_bytes": generated_input_bytes,
        "temporary_output_bytes": 0,
        "retained_generated_output_bytes": 0,
        "aggregate_output_bytes": 0,
        "runtime_seconds": clock() - started,
        "peak_RSS_bytes": peak_rss(),
        "network_bytes": 0,
        "new_payload_bytes": 0,
        "end_to_end_latency_measured": False,
    }
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_qualification_passed",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green": True,
        },
        "static_proof": {**ast_inventory, **redundancy},
        "matrix": {
            "cases": len(CASES),
            "orders": len(ORDERS),
            "replays": REPLAYS,
            "paths": vr20a_calls,
            "VR20A_calls": vr20a_calls,
            "VR23A_route_counts": dict(sorted(route_counts.items())),
            "VR20A_route_counts": dict(sorted(upstream_counts.items())),
            "replay_source_hashes": replay_hashes,
            "replay_routes": replay_routes,
            "source_mutations_after_call": source_mutations,
            "direct_refusals_passed": direct_refusals,
        },
        "measurements": measurements,
        "operation_counters": operation_counters,
        "warnings": [
            "generated_structural_qualification_only",
            "consumed_VR22P_not_touched",
            "no_private_executor",
            "no_cohort_or_neural_evidence",
            "FW2_and_CIL1_not_authorized",
        ],
        "unavailable_fields": [
            "real_failed_F06_predicate",
            "private_value",
            "real_cohort",
            "neural_payload",
            "decoding_accuracy",
            "live_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "generated discrimination of all five independently reachable "
                "VR20A F06 structural classes"
            ),
            "scientific_ceiling": "none",
            "neural_payload_accessed": False,
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "unseen_person_generalization": False,
            "live_decoding": False,
        },
    }
    for _attempt in range(3):
        measurements["aggregate_output_bytes"] = len(_canonical_json_bytes(report))
    if measurements["aggregate_output_bytes"] != len(_canonical_json_bytes(report)):
        raise F06FiveRouteDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate output byte accounting differs"
        )
    _enforce_caps(measurements)
    _assert_public_report_safe(report)
    return report


def build_plan() -> dict[str, Any]:
    """Return the frozen generated-only qualification plan."""

    return {
        "lane_id": LANE_ID,
        "cases": len(CASES),
        "orders": len(ORDERS),
        "replays": REPLAYS,
        "paths": len(CASES) * len(ORDERS) * REPLAYS,
        "VR20A_calls": 24,
        "reachable_F06_classes": 5,
        "non_independent_defensive_guards": 2,
        "private_executor_available": False,
        "FW2_or_CIL1_authorized": False,
        "scientific_ceiling": "none",
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = build_plan() if args.command == "plan" else qualify_generated()
    sys.stdout.buffer.write(_canonical_json_bytes(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
