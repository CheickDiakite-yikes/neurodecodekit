"""Generated-only MARC2 first-failure-stable R4 decomposition."""

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

from neurodecodekit.datasets import (
    marc2_suffix_identity_grammar_decomposition as vr15a,
)
from neurodecodekit.datasets import (
    marc2_variable_width_run_index_repair as vr16a,
)

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR17C"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_first_failure_stable_r4_decomposition_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_first_failure_stable_r4_decomposition_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_first_failure_stable_r4_decomposition_contract.v0.json"
)
CONTRACT_BYTES = 10_380
CONTRACT_SHA256 = "8fdef358e31450be74d8eaf280bb4957d891a19e2364188d5b3d9afc92a26fcc"
GREEN_REGISTRATION_COMMIT = "a34896d1d0e4ebc548f4b92bcbd80a70355dc8c2"
GREEN_REGISTRATION_CI_RUN_ID = 32_470_828_824
GREEN_REGISTRATION_BASE_JOB_ID = 96_737_040_056
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_737_040_177
SUCCESS_ROUTE = "MARC2VR17C-G1"
RESULT_ROUTES = tuple(f"MARC2VR17C-R{index}" for index in range(1, 5))
REFUSAL_ROUTES = tuple(f"MARC2VR17C-F{index:02d}" for index in range(1, 7))
VARIANTS = vr16a.VARIANTS
ORDERS = vr16a.ORDERS
REPLAYS = 2
RESIDUAL_CASES = (
    "control_success",
    "wrong_task_token",
    "mixed_lexical_tokens_within_bundle",
    "same_token_distinct_name_normalized_collision",
    "incomplete_companion_set",
)
CASE_ROUTES = dict(zip(RESIDUAL_CASES, (SUCCESS_ROUTE, *RESULT_ROUTES), strict=True))
RESIDUAL_EVIDENCE = {
    ("MARC2VR16A-F04", "core identity differs"): RESULT_ROUTES[0],
    ("MARC2VR16A-F05", "companion run spelling differs"): RESULT_ROUTES[1],
    ("MARC2VR16A-F05", "normalized run companion is duplicated"): RESULT_ROUTES[2],
    ("MARC2VR16A-F05", "run companion set is incomplete"): RESULT_ROUTES[3],
}
EXPECTED_SEMANTIC_SHA256 = (
    "254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba"
)
THREAD_ENVIRONMENT = vr16a.THREAD_ENVIRONMENT
FORBIDDEN_PUBLIC_KEYS = vr15a.FORBIDDEN_PUBLIC_KEYS


class FirstFailureStableR4Refusal(RuntimeError):
    """Fail closed with one aggregate-safe VR17C route."""

    def __init__(self, route: str, safe_detail: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR17C refusal route")
        super().__init__(f"{route}: {safe_detail}")
        self.route = route
        self.safe_detail = safe_detail


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
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[4], "aggregate JSON differs"
        ) from exc


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR17C contract."""

    path = (root or _repo_root()) / CONTRACT_RELATIVE_PATH
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("contract is not a regular file")
        payload = path.read_bytes()
        value = json.loads(payload.decode("utf-8", "strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if (
        len(payload) != CONTRACT_BYTES
        or _sha256(payload) != CONTRACT_SHA256
        or not isinstance(value, dict)
    ):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[0], "registered contract differs"
        )
    return value


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
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[0], "registered contract mapping differs"
        )


def _verify_registration_proof(
    *,
    commit: str = GREEN_REGISTRATION_COMMIT,
    ci_run_id: int = GREEN_REGISTRATION_CI_RUN_ID,
    base_job_id: int = GREEN_REGISTRATION_BASE_JOB_ID,
    optional_job_id: int = GREEN_REGISTRATION_OPTIONAL_JOB_ID,
) -> None:
    if (
        commit != GREEN_REGISTRATION_COMMIT
        or ci_run_id != GREEN_REGISTRATION_CI_RUN_ID
        or base_job_id != GREEN_REGISTRATION_BASE_JOB_ID
        or optional_job_id != GREEN_REGISTRATION_OPTIONAL_JOB_ID
    ):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _load_fixed_payloads(
    contract: Mapping[str, Any], root: Path | None = None
) -> dict[str, bytes]:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 10:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[1], "fixed input registry differs"
        )
    payloads: dict[str, bytes] = {}
    for row in rows:
        try:
            relative = str(row["path"])
            path = fixed_root / relative
            if path.is_symlink() or not path.is_file():
                raise OSError("fixed input is not regular")
            payloads[relative] = path.read_bytes()
        except (KeyError, OSError) as exc:
            raise FirstFailureStableR4Refusal(
                REFUSAL_ROUTES[1], "fixed input is unavailable"
            ) from exc
    return payloads


def _verify_fixed_payloads(
    contract: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> int:
    rows = contract["fixed_inputs"]
    if set(payloads) != {row["path"] for row in rows}:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[1], "fixed input set differs"
        )
    total = 0
    for row in rows:
        payload = payloads[row["path"]]
        if len(payload) != row["bytes"] or _sha256(payload) != row["sha256"]:
            raise FirstFailureStableR4Refusal(
                REFUSAL_ROUTES[1], "fixed input bytes differ"
            )
        total += len(payload)
    if total != contract["fixed_input_bytes"]:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[1], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _build_collision_witness(source: Mapping[str, Any], order: str) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    target = vr16a._rows_for_first_bundle(changed)[0]
    auxiliary = next(
        row
        for row in changed["entries"]
        if row["entry_kind"] == "regular_file"
        and vr16a._variable_core_match(row["member_name"]) is None
        and not any(
            row["member_name"].endswith(suffix)
            for suffix in vr16a.selector.REQUIRED_SUFFIXES
        )
    )
    auxiliary.update(copy.deepcopy(target))
    auxiliary["member_name"] = target["member_name"].replace(
        "_run-", "_acq-copy_run-", 1
    )
    auxiliary["local_header_offset"] += 1
    changed["entries"] = sorted(changed["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        changed["entries"].reverse()
    return changed


def build_residual_case(case: str, order: str) -> dict[str, Any]:
    """Build one frozen generated residual case."""

    if case not in RESIDUAL_CASES or order not in ORDERS:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[2], "generated residual case differs"
        )
    base = vr16a.build_generated_variant("three_digit", order)
    if case == "control_success":
        return base
    if case == "same_token_distinct_name_normalized_collision":
        return _build_collision_witness(base, order)
    return vr16a._mutated_witness(base, case)


def discriminate_residual(source: Mapping[str, Any]) -> str:
    """Call unchanged VR16A once and return one generated aggregate route."""

    before = vr16a.vr2._canonical_source_bytes(source)
    try:
        vr16a.adapt_variable_width_source(source)
    except vr16a.VariableWidthRunIndexRepairRefusal as exc:
        route = RESIDUAL_EVIDENCE.get((exc.route, exc.safe_reason))
        if route is None:
            raise FirstFailureStableR4Refusal(
                REFUSAL_ROUTES[2], "VR16A residual evidence differs"
            ) from exc
    else:
        route = SUCCESS_ROUTE
    if vr16a.vr2._canonical_source_bytes(source) != before:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[2], "VR16A changed generated source"
        )
    return route


def _expected_vr15a_route(variant: str) -> str:
    return "MARC2VR15A-G1" if variant in VARIANTS[:2] else "MARC2VR15A-R15"


def _run_equivalence_matrix() -> dict[str, Any]:
    replays: list[list[list[str]]] = []
    generated_bytes = 0
    source_hashes: set[str] = set()
    for _replay in range(REPLAYS):
        rows: list[list[str]] = []
        for order in ORDERS:
            for variant in VARIANTS:
                source = vr16a.build_generated_variant(variant, order)
                before = vr16a.vr2._canonical_source_bytes(source)
                generated_bytes += len(before)
                source_hashes.add(_sha256(before))
                vr15a_route = vr15a.discriminate_generated_source(source).route
                outcome = vr16a.adapt_variable_width_source(source)
                if (
                    vr15a_route != _expected_vr15a_route(variant)
                    or outcome.semantic_sha256 != EXPECTED_SEMANTIC_SHA256
                    or vr16a.vr2._canonical_source_bytes(source) != before
                ):
                    raise FirstFailureStableR4Refusal(
                        REFUSAL_ROUTES[2], "equivalence path differs"
                    )
                rows.append([variant, order, vr15a_route, "MARC2VR16A-G1"])
        replays.append(rows)
    matrix = {
        "paths": 24,
        "VR15A_calls": 24,
        "VR16A_calls": 24,
        "control_paths": 8,
        "repair_paths": 16,
        "semantic_sha256": EXPECTED_SEMANTIC_SHA256,
        "distinct_source_hashes": len(source_hashes),
        "replay_digests": [_sha256(_canonical_json_bytes(rows)) for rows in replays],
        "generated_input_bytes": generated_bytes,
        "source_objects_immutable": True,
    }
    _validate_equivalence_matrix(matrix)
    return matrix


def _validate_equivalence_matrix(matrix: Mapping[str, Any]) -> None:
    digests = matrix.get("replay_digests")
    if (
        set(matrix)
        != {
            "paths",
            "VR15A_calls",
            "VR16A_calls",
            "control_paths",
            "repair_paths",
            "semantic_sha256",
            "distinct_source_hashes",
            "replay_digests",
            "generated_input_bytes",
            "source_objects_immutable",
        }
        or matrix.get("paths") != 24
        or matrix.get("VR15A_calls") != 24
        or matrix.get("VR16A_calls") != 24
        or matrix.get("control_paths") != 8
        or matrix.get("repair_paths") != 16
        or matrix.get("semantic_sha256") != EXPECTED_SEMANTIC_SHA256
        or matrix.get("distinct_source_hashes") != 6
        or not isinstance(digests, list)
        or len(digests) != 2
        or digests[0] != digests[1]
        or matrix.get("generated_input_bytes", 0) <= 0
        or matrix.get("source_objects_immutable") is not True
    ):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[3], "equivalence matrix differs"
        )


def _run_residual_matrix() -> dict[str, Any]:
    replays: list[list[list[str]]] = []
    counts: Counter[str] = Counter()
    generated_bytes = 0
    for _replay in range(REPLAYS):
        rows: list[list[str]] = []
        for order in ORDERS:
            for case in RESIDUAL_CASES:
                source = build_residual_case(case, order)
                before = vr16a.vr2._canonical_source_bytes(source)
                generated_bytes += len(before)
                route = discriminate_residual(source)
                if route != CASE_ROUTES[case]:
                    raise FirstFailureStableR4Refusal(
                        REFUSAL_ROUTES[2], "residual route differs"
                    )
                counts[route] += 1
                rows.append([case, order, route])
        replays.append(rows)
    matrix = {
        "paths": 20,
        "VR16A_calls": 20,
        "route_counts": dict(sorted(counts.items())),
        "replay_digests": [_sha256(_canonical_json_bytes(rows)) for rows in replays],
        "generated_input_bytes": generated_bytes,
        "source_objects_immutable": True,
    }
    _validate_residual_matrix(matrix)
    return matrix


def _validate_residual_matrix(matrix: Mapping[str, Any]) -> None:
    digests = matrix.get("replay_digests")
    if (
        set(matrix)
        != {
            "paths",
            "VR16A_calls",
            "route_counts",
            "replay_digests",
            "generated_input_bytes",
            "source_objects_immutable",
        }
        or matrix.get("paths") != 20
        or matrix.get("VR16A_calls") != 20
        or matrix.get("route_counts")
        != {route: 4 for route in (SUCCESS_ROUTE, *RESULT_ROUTES)}
        or not isinstance(digests, list)
        or len(digests) != 2
        or digests[0] != digests[1]
        or matrix.get("generated_input_bytes", 0) <= 0
        or matrix.get("source_objects_immutable") is not True
    ):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[3], "residual matrix differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise FirstFailureStableR4Refusal(
                    REFUSAL_ROUTES[4], "aggregate output key is forbidden"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        lowered = value.casefold()
        if ".codex_work" in lowered or "/users/" in lowered or "private_manifest" in lowered:
            raise FirstFailureStableR4Refusal(
                REFUSAL_ROUTES[4], "aggregate output value is forbidden"
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
    if (
        runtime_seconds > caps["runtime_seconds"]
        or peak_rss_bytes >= caps["peak_RSS_bytes"]
        or generated_input_bytes > caps["generated_input_bytes"]
        or aggregate_output_bytes > caps["aggregate_output_bytes"]
        or retained_output_bytes != caps["retained_generated_output_bytes"]
    ):
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(
    name: str,
    expected_route: str,
    action: Callable[[], Any],
    counts: Counter[str],
) -> None:
    try:
        action()
    except FirstFailureStableR4Refusal as exc:
        if exc.route != expected_route:
            raise FirstFailureStableR4Refusal(
                REFUSAL_ROUTES[3], "direct refusal route differs"
            ) from exc
        counts[exc.route] += 1
        return
    raise FirstFailureStableR4Refusal(
        REFUSAL_ROUTES[3], f"direct mutation passed: {name}"
    )


def _run_direct_refusals(
    contract: Mapping[str, Any],
    payloads: Mapping[str, bytes],
    equivalence: Mapping[str, Any],
    residual: Mapping[str, Any],
) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    for index, mutation in enumerate(
        (
            {**contract, "schema_version": "9.9.9"},
            {**contract, "lane_id": "MARC2-VR17X"},
            {**contract, "status": "implemented"},
            {**contract, "unexpected": True},
            [],
        ),
        start=1,
    ):
        _expect_refusal(
            f"contract_{index}",
            REFUSAL_ROUTES[0],
            lambda value=mutation: _verify_contract_mapping(value),
            counts,
        )
    for key, value in (
        ("commit", "0" * 40),
        ("ci_run_id", 0),
        ("base_job_id", 0),
        ("optional_job_id", 0),
    ):
        _expect_refusal(
            f"proof_{key}",
            REFUSAL_ROUTES[0],
            lambda field=key, item=value: _verify_registration_proof(**{field: item}),
            counts,
        )
    for path in payloads:
        changed = dict(payloads)
        changed[path] += b"x"
        _expect_refusal(
            f"fixed_{path}",
            REFUSAL_ROUTES[1],
            lambda value=changed: _verify_fixed_payloads(contract, value),
            counts,
        )
    first_path = next(iter(payloads))
    missing = {path: payload for path, payload in payloads.items() if path != first_path}
    extra = {**payloads, "registries/unregistered.json": b""}
    for name, changed in (("missing", missing), ("extra", extra)):
        _expect_refusal(
            f"fixed_set_{name}",
            REFUSAL_ROUTES[1],
            lambda value=changed: _verify_fixed_payloads(contract, value),
            counts,
        )
    for key in THREAD_ENVIRONMENT:
        environment = dict(THREAD_ENVIRONMENT)
        environment[key] = "2"
        _expect_refusal(
            f"thread_{key}",
            REFUSAL_ROUTES[5],
            lambda value=environment: _validate_thread_environment(value),
            counts,
        )
    for key, value in (
        ("paths", 0),
        ("VR15A_calls", 0),
        ("VR16A_calls", 0),
        ("control_paths", 0),
        ("repair_paths", 0),
        ("semantic_sha256", "0" * 64),
        ("distinct_source_hashes", 0),
        ("replay_digests", ["a", "b"]),
        ("generated_input_bytes", 0),
        ("source_objects_immutable", False),
    ):
        changed = {**equivalence, key: value}
        _expect_refusal(
            f"equivalence_{key}",
            REFUSAL_ROUTES[3],
            lambda item=changed: _validate_equivalence_matrix(item),
            counts,
        )
    for key, value in (
        ("paths", 0),
        ("VR16A_calls", 0),
        ("route_counts", {}),
        ("replay_digests", ["a", "b"]),
        ("generated_input_bytes", 0),
        ("source_objects_immutable", False),
    ):
        changed = {**residual, key: value}
        _expect_refusal(
            f"residual_{key}",
            REFUSAL_ROUTES[3],
            lambda item=changed: _validate_residual_matrix(item),
            counts,
        )
    for value in ({"path": "x"}, {"target": "x"}, {"ok": "/Users/x"}):
        _expect_refusal(
            "privacy",
            REFUSAL_ROUTES[4],
            lambda item=value: _walk_public(item),
            counts,
        )
    cap = contract["resource_caps"]
    for values in (
        (cap["runtime_seconds"] + 1, 0, 0, 0, 0),
        (0, cap["peak_RSS_bytes"], 0, 0, 0),
        (0, 0, cap["generated_input_bytes"] + 1, 0, 0),
        (0, 0, 0, cap["aggregate_output_bytes"] + 1, 0),
        (0, 0, 0, 0, 1),
    ):
        _expect_refusal(
            "resource",
            REFUSAL_ROUTES[5],
            lambda item=values: _assert_resources(
                runtime_seconds=item[0],
                peak_rss_bytes=item[1],
                generated_input_bytes=item[2],
                aggregate_output_bytes=item[3],
                retained_output_bytes=item[4],
                contract=contract,
            ),
            counts,
        )
    total = sum(counts.values())
    if total < contract["direct_refusal_minimum"]:
        raise FirstFailureStableR4Refusal(
            REFUSAL_ROUTES[3], "direct refusal total differs"
        )
    return {"direct_refusals": total, "route_counts": dict(sorted(counts.items()))}


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR15P_VR16P_VR17A_or_VR17B_operations": 0,
        "real_structural_source_operations": 0,
        "cohort_freezes": 0,
        "archive_or_neural_payload_operations": 0,
        "signal_event_channel_geometry_target_or_label_operations": 0,
        "model_training_inference_prediction_or_score_runs": 0,
        "FW2_operations": 0,
        "CIL1_operations": 0,
        "network_provider_or_language_model_calls": 0,
        "stream_device_or_hardware_operations": 0,
        "other_project_operations": 0,
        "retry_rerun_resume_operations": 0,
        "release_publication_or_scientific_claim_upgrades": 0,
    }


def qualify_generated(
    *,
    contract: Mapping[str, Any] | None = None,
    clock: Callable[[], float] = time.monotonic,
    peak_rss: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the frozen generated matrices and return one aggregate report."""

    started = clock()
    registered = dict(contract or load_registered_contract())
    _verify_contract_mapping(registered)
    _verify_registration_proof()
    payloads = _load_fixed_payloads(registered)
    fixed_bytes = _verify_fixed_payloads(registered, payloads)
    _validate_thread_environment()
    equivalence = _run_equivalence_matrix()
    residual = _run_residual_matrix()
    refusals = _run_direct_refusals(registered, payloads, equivalence, residual)
    runtime = clock() - started
    rss = peak_rss()
    generated_bytes = (
        equivalence["generated_input_bytes"] + residual["generated_input_bytes"]
    )
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_only_qualified_no_private_access",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
        },
        "equivalence": {
            key: value for key, value in equivalence.items() if key != "generated_input_bytes"
        },
        "residual": {
            key: value for key, value in residual.items() if key != "generated_input_bytes"
        },
        "hypotheses": {f"VR17C-H{index}": True for index in range(1, 5)},
        "refusals": refusals,
        "measurements": {
            "fixed_input_bytes": fixed_bytes,
            "generated_input_bytes": generated_bytes,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
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
        "operation_counters": _zero_counters(),
        "warnings": [
            "generated_fixture_only_no_private_or_real_source_access",
            "aggregate_structural_diagnostic_only",
            "no_real_cohort_or_FW2_CIL1_eligibility",
            "no_neural_decoding_or_scientific_claim",
        ],
        "claim_boundary": registered["claim_boundary"],
    }
    previous = -1
    while report["measurements"]["aggregate_output_bytes"] != previous:
        previous = report["measurements"]["aggregate_output_bytes"]
        report["measurements"]["aggregate_output_bytes"] = len(
            _canonical_json_bytes(report)
        )
    _walk_public(report)
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=rss,
        generated_input_bytes=generated_bytes,
        aggregate_output_bytes=report["measurements"]["aggregate_output_bytes"],
        retained_output_bytes=0,
        contract=registered,
    )
    return report


def build_plan() -> dict[str, Any]:
    """Return the fixed generated-only plan."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    fixed_bytes = _verify_fixed_payloads(contract, _load_fixed_payloads(contract))
    return {
        "lane_id": LANE_ID,
        "status": "generated_only_implementation_eligible",
        "fixed_input_bytes": fixed_bytes,
        "equivalence_paths": 24,
        "residual_paths": 20,
        "VR15A_calls": 24,
        "VR16A_calls": 44,
        "direct_refusal_minimum": contract["direct_refusal_minimum"],
        "private_access_authorized": False,
        "execute_surface_available": False,
        "claim_boundary": contract["claim_boundary"],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generated-only MARC2 first-failure-stable R4 audit."
    )
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        payload = build_plan() if args.command == "plan" else qualify_generated()
    except FirstFailureStableR4Refusal as exc:
        print(
            json.dumps(
                {"lane_id": LANE_ID, "route": exc.route, "status": "refused"},
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 2
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
