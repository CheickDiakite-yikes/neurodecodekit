"""Generated-only MARC2-VR19A F04 task-implication audit."""

from __future__ import annotations

import argparse
import ast
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
    marc2_first_failure_stable_r4_decomposition as vr17c,
)
from neurodecodekit.datasets import (
    marc2_variable_width_run_index_repair as vr16a,
)

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR19A"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_f04_task_implication_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f04_task_implication_result"
CONTRACT_RELATIVE_PATH = Path("registries/marc2_f04_task_implication_contract.v0.json")
CONTRACT_BYTES = 9_199
CONTRACT_SHA256 = "b4cb5e3420a67ed50ccb7d5c0e14c6f99cfc15b13360057ae693985c601ffe37"
GREEN_REGISTRATION_COMMIT = "9365b0ff7bfd5dbd3b37217a80ab01e6770de212"
GREEN_REGISTRATION_CI_RUN_ID = 32_480_420_157
GREEN_REGISTRATION_BASE_JOB_ID = 96_765_347_691
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_765_347_974
SUCCESS_ROUTE = "MARC2VR19A-G1"
RESULT_ROUTES = ("MARC2VR19A-R1", "MARC2VR19A-R2")
REFUSAL_ROUTES = tuple(f"MARC2VR19A-F{index:02d}" for index in range(1, 7))
ORDERS = ("canonical", "reversed")
REPLAYS = 2
CASES = (
    "freewill_control",
    "task_motor",
    "task_rest",
    "task_Freewill",
    "task_freewill2",
    "subject_repeat_mismatch",
    "session_repeat_mismatch",
    "subject_width_mismatch",
)
CASE_CLASSES = {
    "freewill_control": "control",
    "task_motor": "nonfreewill",
    "task_rest": "nonfreewill",
    "task_Freewill": "nonfreewill",
    "task_freewill2": "nonfreewill",
    "subject_repeat_mismatch": "identity_counterexample",
    "session_repeat_mismatch": "identity_counterexample",
    "subject_width_mismatch": "identity_counterexample",
}
CASE_ROUTES = {
    case: (
        SUCCESS_ROUTE
        if kind == "control"
        else RESULT_ROUTES[0]
        if kind == "nonfreewill"
        else RESULT_ROUTES[1]
    )
    for case, kind in CASE_CLASSES.items()
}
THREAD_ENVIRONMENT = vr16a.THREAD_ENVIRONMENT
FORBIDDEN_PUBLIC_KEYS = vr17c.FORBIDDEN_PUBLIC_KEYS


class F04TaskImplicationRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR19A route."""

    def __init__(self, route: str, safe_detail: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR19A refusal route")
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
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON differs"
        ) from exc


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR19A contract."""

    path = (root or _repo_root()) / CONTRACT_RELATIVE_PATH
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("contract is not a regular file")
        payload = path.read_bytes()
        value = json.loads(payload.decode("utf-8", "strict"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[0], "registered contract is unavailable"
        ) from exc
    if (
        len(payload) != CONTRACT_BYTES
        or _sha256(payload) != CONTRACT_SHA256
        or not isinstance(value, dict)
    ):
        raise F04TaskImplicationRefusal(
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
        raise F04TaskImplicationRefusal(
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
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _load_fixed_payloads(
    contract: Mapping[str, Any], root: Path | None = None
) -> dict[str, bytes]:
    fixed_root = root or _repo_root()
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 8:
        raise F04TaskImplicationRefusal(
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
            raise F04TaskImplicationRefusal(
                REFUSAL_ROUTES[1], "fixed input is unavailable"
            ) from exc
    return payloads


def _verify_fixed_payloads(
    contract: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> int:
    rows = contract["fixed_inputs"]
    if set(payloads) != {row["path"] for row in rows}:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[1], "fixed input set differs"
        )
    total = 0
    for row in rows:
        payload = payloads[row["path"]]
        if len(payload) != row["bytes"] or _sha256(payload) != row["sha256"]:
            raise F04TaskImplicationRefusal(
                REFUSAL_ROUTES[1], "fixed input bytes differ"
            )
        total += len(payload)
    if total != contract["fixed_input_bytes"]:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[1], "fixed input byte total differs"
        )
    return total


def _validate_thread_environment(environment: Mapping[str, str] | None = None) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _is_refusal_index(node: ast.AST, index: int) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == "REFUSAL_ROUTES"
        and isinstance(node.slice, ast.Constant)
        and node.slice.value == index
    )


def _is_task_inequality(node: ast.AST) -> bool:
    return ast.dump(node, include_attributes=False) == ast.dump(
        ast.parse('match.group("task") != "freewill"', mode="eval").body,
        include_attributes=False,
    )


def audit_f04_producers(source_payload: bytes) -> dict[str, Any]:
    """Bind the exact F04-producing AST without exposing source text."""

    try:
        tree = ast.parse(source_payload.decode("utf-8", "strict"))
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[2], "bound source AST differs"
        ) from exc
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_validate_variable_entry"
    ]
    if len(functions) != 1:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[2], "validator function inventory differs"
        )
    function = functions[0]
    f04_references = [
        node for node in ast.walk(function) if _is_refusal_index(node, 3)
    ]
    translated = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.IfExp)
        and _is_refusal_index(node.body, 3)
        and _is_refusal_index(node.orelse, 2)
        and _is_task_inequality(node.test)
    ]
    direct = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.If)
        and _is_task_inequality(node.test)
        and any(_is_refusal_index(child, 3) for child in ast.walk(node))
    ]
    reasons = {
        value.value
        for value in ast.walk(function)
        if isinstance(value, ast.Constant)
        and value.value in {"core identity differs", "Freewill task differs"}
    }
    if (
        len(f04_references) != 2
        or len(translated) != 1
        or len(direct) != 1
        or reasons != {"core identity differs", "Freewill task differs"}
    ):
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[2], "F04 producer inventory differs"
        )
    return {
        "F04_producer_references": 2,
        "translated_task_guard": True,
        "direct_task_guard": True,
        "exact_R4_pair_unique_to_translated_reference": True,
        "private_value_inspected": False,
    }


def build_generated_case(case: str, order: str) -> dict[str, Any]:
    """Build one generated control, task witness, or identity counterexample."""

    if case not in CASES or order not in ORDERS:
        raise ValueError("unknown generated case or order")
    source = vr16a.build_generated_variant("three_digit", "canonical")
    if case.startswith("task_"):
        token = case.removeprefix("task_")
        for row in source["entries"]:
            name = row.get("member_name") if isinstance(row, dict) else None
            if isinstance(name, str):
                row["member_name"] = name.replace(
                    "_task-freewill_", f"_task-{token}_"
                )
    elif case != "freewill_control":
        target = next(
            row
            for row in source["entries"]
            if isinstance(row, dict)
            and vr16a._variable_core_match(row.get("member_name", "")) is not None
        )
        match = vr16a._variable_core_match(target["member_name"])
        assert match is not None
        if case == "subject_repeat_mismatch":
            target["member_name"] = target["member_name"].replace(
                f"/eeg/{match.group('subject')}_", "/eeg/sub-99_", 1
            )
        elif case == "session_repeat_mismatch":
            target["member_name"] = target["member_name"].replace(
                f"_{match.group('session')}_task-", "_ses-99_task-", 1
            )
        elif case == "subject_width_mismatch":
            target["member_name"] = target["member_name"].replace(
                match.group("subject"), "sub-1", 1
            )
    source["entries"] = sorted(source["entries"], key=lambda row: row["member_name"])
    if order == "reversed":
        source["entries"].reverse()
    return source


def discriminate_generated(source: Mapping[str, Any]) -> str:
    """Call unchanged VR16A once and retain only a generated aggregate route."""

    before = vr16a.vr2._canonical_source_bytes(source)
    try:
        vr16a.adapt_variable_width_source(source)
    except vr16a.VariableWidthRunIndexRepairRefusal as exc:
        if (exc.route, exc.safe_reason) == (
            "MARC2VR16A-F04",
            "core identity differs",
        ):
            route = RESULT_ROUTES[0]
        elif (exc.route, exc.safe_reason) == (
            "MARC2VR16A-F03",
            "suffix-bearing identity differs",
        ):
            route = RESULT_ROUTES[1]
        else:
            raise F04TaskImplicationRefusal(
                REFUSAL_ROUTES[3], "generated upstream evidence differs"
            ) from exc
    else:
        route = SUCCESS_ROUTE
    if vr16a.vr2._canonical_source_bytes(source) != before:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[3], "generated source mutated"
        )
    return route


def _run_matrix() -> dict[str, Any]:
    replay_digests: list[str] = []
    final_counts: Counter[str] = Counter()
    total_input = 0
    for _replay in range(REPLAYS):
        rows: list[dict[str, str]] = []
        replay_counts: Counter[str] = Counter()
        for order in ORDERS:
            for case in CASES:
                source = build_generated_case(case, order)
                source_bytes = vr16a.vr2._canonical_source_bytes(source)
                route = discriminate_generated(source)
                if route != CASE_ROUTES[case]:
                    raise F04TaskImplicationRefusal(
                        REFUSAL_ROUTES[3], "generated case route differs"
                    )
                total_input += len(source_bytes)
                replay_counts[route] += 1
                rows.append(
                    {"class": CASE_CLASSES[case], "order": order, "route": route}
                )
        replay_digests.append(_sha256(_canonical_json_bytes(rows)))
        final_counts.update(replay_counts)
    return {
        "paths": len(CASES) * len(ORDERS) * REPLAYS,
        "VR16A_calls": len(CASES) * len(ORDERS) * REPLAYS,
        "route_counts": dict(sorted(final_counts.items())),
        "replay_digests": replay_digests,
        "generated_input_bytes": total_input,
        "source_objects_immutable": True,
    }


def _validate_matrix(matrix: Mapping[str, Any]) -> None:
    expected = {SUCCESS_ROUTE: 4, RESULT_ROUTES[0]: 16, RESULT_ROUTES[1]: 12}
    if (
        matrix.get("paths") != 32
        or matrix.get("VR16A_calls") != 32
        or matrix.get("route_counts") != expected
        or len(set(matrix.get("replay_digests", []))) != 1
        or not isinstance(matrix.get("generated_input_bytes"), int)
        or matrix["generated_input_bytes"] <= 0
        or matrix.get("source_objects_immutable") is not True
    ):
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[3], "generated matrix differs"
        )


def _walk_public(value: Any, key: str = "") -> None:
    if key.lower() in FORBIDDEN_PUBLIC_KEYS:
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[4], "private key leaked"
        )
    if isinstance(value, str) and (value.startswith("/") or ":\\" in value):
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[4], "private path leaked"
        )
    if isinstance(value, Mapping):
        for child_key, child in value.items():
            _walk_public(child, str(child_key))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _walk_public(child)


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


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
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[5], "generated resource cap exceeded"
        )


def _expect_refusal(
    expected_route: str, action: Callable[[], Any], counts: Counter[str]
) -> None:
    try:
        action()
    except F04TaskImplicationRefusal as exc:
        if exc.route != expected_route:
            raise F04TaskImplicationRefusal(
                REFUSAL_ROUTES[3], "direct refusal route differs"
            ) from exc
        counts[exc.route] += 1
        return
    raise F04TaskImplicationRefusal(
        REFUSAL_ROUTES[3], "direct mutation passed"
    )


def _run_direct_refusals(
    contract: Mapping[str, Any],
    payloads: Mapping[str, bytes],
    matrix: Mapping[str, Any],
) -> int:
    counts: Counter[str] = Counter()
    for mutation in (
        {**contract, "schema_version": "9.9.9"},
        {**contract, "lane_id": "MARC2-VR19X"},
        {**contract, "status": "implemented"},
        {**contract, "unexpected": True},
        [],
    ):
        _expect_refusal(
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
            REFUSAL_ROUTES[0],
            lambda field=key, item=value: _verify_registration_proof(
                **{field: item}
            ),
            counts,
        )
    for path in payloads:
        changed = dict(payloads)
        changed[path] += b"x"
        _expect_refusal(
            REFUSAL_ROUTES[1],
            lambda value=changed: _verify_fixed_payloads(contract, value),
            counts,
        )
    first_path = next(iter(payloads))
    missing = {path: value for path, value in payloads.items() if path != first_path}
    extra = {**payloads, "registries/unregistered.json": b""}
    for changed in (missing, extra):
        _expect_refusal(
            REFUSAL_ROUTES[1],
            lambda value=changed: _verify_fixed_payloads(contract, value),
            counts,
        )
    for key in THREAD_ENVIRONMENT:
        environment = dict(THREAD_ENVIRONMENT)
        environment[key] = "2"
        _expect_refusal(
            REFUSAL_ROUTES[5],
            lambda value=environment: _validate_thread_environment(value),
            counts,
        )
    for payload in (b"not python", b"def another_function():\n    pass\n"):
        _expect_refusal(
            REFUSAL_ROUTES[2],
            lambda value=payload: audit_f04_producers(value),
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
        changed = {**matrix, key: value}
        _expect_refusal(
            REFUSAL_ROUTES[3],
            lambda item=changed: _validate_matrix(item),
            counts,
        )
    for value in ({"path": "x"}, {"target": "x"}, {"ok": "/Users/x"}):
        _expect_refusal(
            REFUSAL_ROUTES[4], lambda item=value: _walk_public(item), counts
        )
    caps = contract["resource_caps"]
    for values in (
        (caps["runtime_seconds"] + 1, 0, 0, 0, 0),
        (0, caps["peak_RSS_bytes"], 0, 0, 0),
        (0, 0, caps["generated_input_bytes"] + 1, 0, 0),
        (0, 0, 0, caps["aggregate_output_bytes"] + 1, 0),
        (0, 0, 0, 0, 1),
    ):
        _expect_refusal(
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
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[3], "direct refusal count differs"
        )
    return total


def qualify_generated(
    *, peak_rss: Callable[[], int] = _peak_rss_bytes
) -> dict[str, Any]:
    """Run the exact generated-only VR19A qualification."""

    started = time.monotonic()
    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    _validate_thread_environment()
    payloads = _load_fixed_payloads(contract)
    fixed_bytes = _verify_fixed_payloads(contract, payloads)
    source_payload = payloads[
        "src/neurodecodekit/datasets/marc2_variable_width_run_index_repair.py"
    ]
    static = audit_f04_producers(source_payload)
    matrix = _run_matrix()
    _validate_matrix(matrix)
    hypotheses = {
        "VR19A-H1": static["translated_task_guard"] and static["direct_task_guard"],
        "VR19A-H2": static["exact_R4_pair_unique_to_translated_reference"],
        "VR19A-H3": matrix["route_counts"][RESULT_ROUTES[0]] == 16,
        "VR19A-H4": matrix["route_counts"][RESULT_ROUTES[1]] == 12,
    }
    if not all(hypotheses.values()):
        raise F04TaskImplicationRefusal(
            REFUSAL_ROUTES[3], "registered hypothesis failed"
        )
    refusal_count = _run_direct_refusals(contract, payloads, matrix)
    runtime = time.monotonic() - started
    measured_rss = peak_rss()
    report = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "generated_qualification_passed",
        "route": SUCCESS_ROUTE,
        "proof": {
            "registration_commit": GREEN_REGISTRATION_COMMIT,
            "registration_CI": GREEN_REGISTRATION_CI_RUN_ID,
        },
        "static": static,
        "matrix": {
            "paths": matrix["paths"],
            "VR16A_calls": matrix["VR16A_calls"],
            "route_counts": matrix["route_counts"],
            "replay_sha256": matrix["replay_digests"][0],
            "both_replays_equal": True,
            "source_objects_immutable": True,
        },
        "hypotheses": hypotheses,
        "refusals": {"direct_refusals": refusal_count},
        "measurements": {
            "fixed_input_bytes": fixed_bytes,
            "generated_input_bytes": matrix["generated_input_bytes"],
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": measured_rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "network_bytes": 0,
        },
        "operation_counters": dict(contract["operation_counters"]),
        "warnings": [
            "Generated task witnesses do not identify the private task token.",
            "This is a code-level structural implication, not neural evidence.",
            "VR18P remains consumed with no retry or private reinspection.",
        ],
        "unavailable_fields": [
            "private_task_value",
            "private_row_path_or_identity",
            "real_cohort",
            "neural_payload",
            "decoding_metric",
            "live_latency",
            "FW2_result",
            "CIL1_result",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "exact non-freewill task-class implication under bound VR16A semantics"
            ),
            "scientific_ceiling": "none",
            "private_task_value_known": False,
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "live_decoding": False,
        },
    }
    for _iteration in range(3):
        report["measurements"]["aggregate_output_bytes"] = len(
            _canonical_json_bytes(report)
        )
    output_bytes = len(_canonical_json_bytes(report))
    _assert_resources(
        runtime_seconds=runtime,
        peak_rss_bytes=measured_rss,
        generated_input_bytes=matrix["generated_input_bytes"],
        aggregate_output_bytes=output_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _walk_public(report)
    return report


def build_plan() -> dict[str, Any]:
    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "schema_name": "neurodecodekit.marc2_f04_task_implication_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "registration_green_generated_qualification_available",
        "generated_paths": contract["generated_matrix"]["paths"],
        "VR16A_calls": contract["generated_matrix"]["VR16A_calls"],
        "private_access_authorized": False,
        "execute_surface_available": False,
        "scientific_ceiling": "none",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("plan", "qualify"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_plan() if args.command == "plan" else qualify_generated()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
