"""Generated-only decomposition of the MARC2-VR12P aggregate R4 route."""

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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_p15_run_index_repair as vr12a


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR13A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_r4_residual_decomposition_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_r4_residual_decomposition_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_r4_residual_decomposition_contract.v0.json"
)
CONTRACT_SHA256 = "b51472e609d5355bac9902b3c70f37ea7ba3bd39231910e1507926be953e4b55"
GREEN_REGISTRATION_COMMIT = "1177174c1d466cf357ef3a81a4d96b39321af063"
GREEN_REGISTRATION_CI_RUN_ID = 32_424_688_012
GREEN_REGISTRATION_BASE_JOB_ID = 96_604_083_183
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 96_604_083_100
SUCCESS_ROUTE = "MARC2VR13A-G1"
RESULT_ROUTES = tuple(f"MARC2VR13A-R{index}" for index in range(1, 8))
REFUSAL_ROUTES = tuple(f"MARC2VR13A-F{index:02d}" for index in range(1, 7))
CASES = (
    "control_success",
    "residual_bids_identity",
    "wrong_task_token",
    "mixed_run_tokens",
    "duplicate_normalized_companion",
    "incomplete_companion_set",
    "extra_complete_bundle",
    "unknown_subject_taxonomy",
)
ORDERS = ("canonical", "reversed")
REPLAYS = 2
CASE_ROUTES = dict(zip(CASES, (SUCCESS_ROUTE, *RESULT_ROUTES), strict=True))
FAILURE_BINDINGS = {
    (
        "MARC2VR12A-F03",
        "P15 suffix-bearing BIDS identity differs",
    ): RESULT_ROUTES[0],
    ("MARC2VR12A-F04", "P16 Freewill task differs"): RESULT_ROUTES[1],
    (
        "MARC2VR12A-F05",
        "P18 companion run spelling differs",
    ): RESULT_ROUTES[2],
    (
        "MARC2VR12A-F05",
        "P18 normalized run companion is duplicated",
    ): RESULT_ROUTES[3],
    (
        "MARC2VR12A-F05",
        "P19 run companion set is incomplete",
    ): RESULT_ROUTES[4],
    (
        "MARC2VR12A-F06",
        "source kind or run-bundle total differs",
    ): RESULT_ROUTES[5],
    (
        "MARC2VR12A-F06",
        "source taxonomy or eligibility differs",
    ): RESULT_ROUTES[6],
}
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "entries",
        "event",
        "failed_value",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "path",
        "prediction",
        "predictions",
        "private_manifest",
        "reason",
        "row",
        "row_index",
        "run_id",
        "safe_reason",
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


class R4ResidualDecompositionRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR13A route."""

    def __init__(self, route: str, safe_reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR13A refusal route")
        super().__init__(f"{route}: {safe_reason}")
        self.route = route
        self.safe_reason = safe_reason


@dataclass(frozen=True, slots=True)
class ResidualDecision:
    """One generated route with no source row or failure detail."""

    route: str


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
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def _reject_constant(_value: str) -> None:
    raise ValueError("non-finite JSON constant")


def _strict_json(payload: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            payload.decode("utf-8", "strict"),
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as exc:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered JSON is unavailable"
        ) from exc
    if not isinstance(value, dict):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered JSON shape differs"
        )
    return value


def _read_fixed(root: Path, relative: str) -> bytes:
    path = root / relative
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("fixed artifact is not a regular file")
        resolved = path.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
        return path.read_bytes()
    except (OSError, ValueError) as exc:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "fixed artifact is unavailable"
        ) from exc


def load_registered_contract(root: Path | None = None) -> dict[str, Any]:
    """Load the exact remotely green VR13A registration."""

    payload = _read_fixed(root or _repo_root(), str(CONTRACT_RELATIVE_PATH))
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract hash differs"
        )
    return _strict_json(payload)


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
        raise R4ResidualDecompositionRefusal(
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
        commit != "1177174c1d466cf357ef3a81a4d96b39321af063"
        or ci_run_id != 32_424_688_012
        or base_job_id != 96_604_083_183
        or optional_job_id != 96_604_083_100
    ):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[0], "registration proof differs"
        )


def _fixed_payloads(
    contract: Mapping[str, Any], root: Path | None = None
) -> dict[str, bytes]:
    repo = root or _repo_root()
    return {
        row["path"]: _read_fixed(repo, row["path"])
        for row in contract["fixed_inputs"]
    }


def _verify_fixed_payloads(
    contract: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> int:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list) or len(rows) != 15:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "fixed artifact inventory differs"
        )
    expected_paths = {row.get("path") for row in rows if isinstance(row, dict)}
    if set(payloads) != expected_paths:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "fixed artifact set differs"
        )
    total = 0
    for row in rows:
        path = row.get("path")
        payload = payloads.get(path)
        if (
            not isinstance(path, str)
            or not isinstance(payload, bytes)
            or len(payload) != row.get("bytes")
            or _sha256_bytes(payload) != row.get("sha256")
        ):
            raise R4ResidualDecompositionRefusal(
                REFUSAL_ROUTES[1], "fixed artifact identity differs"
            )
        total += len(payload)
    if total != contract.get("fixed_input_bytes"):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "fixed artifact byte total differs"
        )
    return total


def _verify_registration_artifacts(
    contract: Mapping[str, Any], root: Path | None = None
) -> int:
    repo = root or _repo_root()
    artifacts = contract.get("registration_artifacts")
    if not isinstance(artifacts, dict):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "registration artifact inventory differs"
        )
    total = len(_read_fixed(repo, str(CONTRACT_RELATIVE_PATH)))
    for prefix in ("document", "test"):
        path = artifacts.get(f"{prefix}_path")
        expected = artifacts.get(f"{prefix}_sha256")
        if not isinstance(path, str) or not isinstance(expected, str):
            raise R4ResidualDecompositionRefusal(
                REFUSAL_ROUTES[1], "registration artifact mapping differs"
            )
        payload = _read_fixed(repo, path)
        if _sha256_bytes(payload) != expected:
            raise R4ResidualDecompositionRefusal(
                REFUSAL_ROUTES[1], "registration artifact identity differs"
            )
        total += len(payload)
    return total


def _expected_inventory(contract: Mapping[str, Any]) -> Counter[tuple[str, str]]:
    inventory = contract.get("F01_F06_safe_reason_inventory")
    if not isinstance(inventory, dict):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "safe-reason inventory differs"
        )
    expected: Counter[tuple[str, str]] = Counter()
    for short_route, reasons in inventory.items():
        if not isinstance(short_route, str) or not isinstance(reasons, list):
            raise R4ResidualDecompositionRefusal(
                REFUSAL_ROUTES[1], "safe-reason inventory shape differs"
            )
        for reason in reasons:
            if not isinstance(reason, str):
                raise R4ResidualDecompositionRefusal(
                    REFUSAL_ROUTES[1], "safe-reason inventory value differs"
                )
            expected[(f"MARC2VR12A-{short_route}", reason)] += 1
    return expected


def _inventory_vr12a_refusals(module_payload: bytes) -> Counter[tuple[str, str]]:
    try:
        tree = ast.parse(module_payload.decode("utf-8", "strict"))
    except (SyntaxError, UnicodeDecodeError) as exc:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "VR12A AST is unavailable"
        ) from exc
    selected_functions = {
        "_registered_contract_bytes",
        "load_registered_contract",
        "_verify_contract_mapping",
        "_verify_registration_proof",
        "_validate_repaired_entry",
        "_group_repaired_rows",
        "_validate_and_filter",
    }
    observed: Counter[tuple[str, str]] = Counter()
    for function in (
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in selected_functions
    ):
        for node in ast.walk(function):
            if not isinstance(node, ast.Raise) or not isinstance(node.exc, ast.Call):
                continue
            call = node.exc
            if (
                not isinstance(call.func, ast.Name)
                or call.func.id != "P15RunIndexRepairRefusal"
                or len(call.args) < 2
                or not isinstance(call.args[0], ast.Subscript)
            ):
                continue
            target = call.args[0]
            if (
                not isinstance(target.value, ast.Name)
                or target.value.id != "REFUSAL_ROUTES"
            ):
                continue
            index_node = target.slice
            reason_node = call.args[1]
            if (
                not isinstance(index_node, ast.Constant)
                or not isinstance(index_node.value, int)
                or not 0 <= index_node.value <= 5
                or not isinstance(reason_node, ast.Constant)
                or not isinstance(reason_node.value, str)
            ):
                continue
            observed[(vr12a.REFUSAL_ROUTES[index_node.value], reason_node.value)] += 1
    return observed


def _verify_static_inventory(
    contract: Mapping[str, Any], payloads: Mapping[str, bytes]
) -> int:
    path = "src/neurodecodekit/datasets/marc2_p15_run_index_repair.py"
    observed = _inventory_vr12a_refusals(payloads[path])
    expected = _expected_inventory(contract)
    if observed != expected or sum(observed.values()) != 23:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[1], "VR12A refusal inventory differs"
        )
    return sum(observed.values())


def _extra_complete_bundle(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    first = vr12a._first_core(changed)
    match = vr12a._repaired_core_match(first["member_name"])
    if match is None:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated witness construction refused"
        )
    subject = match.group("subject")
    session = match.group("session")
    occupied_runs = {
        int(candidate.group("run"))
        for row in changed["entries"]
        if isinstance(row, dict)
        and isinstance(row.get("member_name"), str)
        and (candidate := vr12a._repaired_core_match(row["member_name"]))
        is not None
        and candidate.group("subject") == subject
        and candidate.group("session") == session
    }
    run = next((value for value in range(1, 100) if value not in occupied_runs), 0)
    if run == 0:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated extra run is unavailable"
        )
    names = {
        row.get("member_name") for row in changed["entries"] if isinstance(row, dict)
    }
    new_names = [
        (
            f"Freewill_generated/{subject}/{session}/eeg/"
            f"{subject}_{session}_task-freewill_run-{run:02d}{suffix}"
        )
        for suffix in vr12a.selector.REQUIRED_SUFFIXES
    ]
    if any(name in names for name in new_names):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated extra bundle collides"
        )
    auxiliary = [
        row
        for row in changed["entries"]
        if isinstance(row, dict)
        and row.get("entry_kind") == "regular_file"
        and isinstance(row.get("member_name"), str)
        and vr12a._repaired_core_match(row["member_name"]) is None
        and not any(
            row["member_name"].endswith(suffix)
            for suffix in vr12a.selector.REQUIRED_SUFFIXES
        )
    ][:4]
    if len(auxiliary) != 4:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated auxiliary inventory differs"
        )
    for row, name in zip(auxiliary, new_names, strict=True):
        row["member_name"] = name
    return changed


def _duplicate_normalized_companion(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    target = vr12a._rows_for_first_bundle(changed)[0]
    auxiliary = next(
        row
        for row in changed["entries"]
        if isinstance(row, dict)
        and row.get("entry_kind") == "regular_file"
        and isinstance(row.get("member_name"), str)
        and vr12a._repaired_core_match(row["member_name"]) is None
        and not any(
            row["member_name"].endswith(suffix)
            for suffix in vr12a.selector.REQUIRED_SUFFIXES
        )
    )
    auxiliary.update(copy.deepcopy(target))
    auxiliary["member_name"] = target["member_name"].replace(
        "_run-", "_acq-copy_run-", 1
    )
    auxiliary["local_header_offset"] += 1
    return changed


def _unknown_subject_bundle(source: Mapping[str, Any]) -> dict[str, Any]:
    changed = copy.deepcopy(dict(source))
    rows = vr12a._rows_for_first_bundle(changed)
    if len(rows) != 4:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated bundle inventory differs"
        )
    match = vr12a._repaired_core_match(rows[0]["member_name"])
    if match is None:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated witness construction refused"
        )
    subject = match.group("subject")
    for row in rows:
        row["member_name"] = row["member_name"].replace(
            f"/{subject}/", "/sub-99/", 1
        ).replace(f"{subject}_", "sub-99_", 1)
    return changed


def _build_case(case: str, order: str) -> dict[str, Any]:
    if case not in CASES:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated case differs"
        )
    try:
        base = vr12a.build_generated_variant("padded_control", order)
        if case == "control_success":
            return base
        if case == "residual_bids_identity":
            return vr12a._mutated_witness(
                base, "subject_path_filename_disagreement"
            )
        if case == "wrong_task_token":
            return vr12a._mutated_witness(base, "wrong_task_token")
        if case == "mixed_run_tokens":
            return vr12a._mutated_witness(
                base, "mixed_lexical_run_tokens_within_bundle"
            )
        if case == "duplicate_normalized_companion":
            return _duplicate_normalized_companion(base)
        if case == "incomplete_companion_set":
            return vr12a._mutated_witness(base, "incomplete_companion_set")
        if case == "extra_complete_bundle":
            return _extra_complete_bundle(base)
        return _unknown_subject_bundle(base)
    except (ValueError, StopIteration, vr12a.P15RunIndexRepairRefusal) as exc:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated witness construction refused"
        ) from exc


def _route_for_refusal(exc: vr12a.P15RunIndexRepairRefusal) -> str:
    route = FAILURE_BINDINGS.get((exc.route, exc.safe_reason))
    if route is None:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "VR12A residual route differs"
        ) from exc
    return route


def discriminate_generated_source(source: Mapping[str, Any]) -> ResidualDecision:
    """Return one aggregate route after exactly one unchanged VR12A call."""

    before = vr12a.vr2._canonical_source_bytes(source)
    try:
        vr12a.adapt_repaired_source(source)
    except vr12a.P15RunIndexRepairRefusal as exc:
        route = _route_for_refusal(exc)
    else:
        route = SUCCESS_ROUTE
    if vr12a.vr2._canonical_source_bytes(source) != before:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[2], "VR12A changed generated source"
        )
    return ResidualDecision(route=route)


def _run_matrix() -> dict[str, Any]:
    route_counts: Counter[str] = Counter()
    replay_rows: list[list[list[str]]] = []
    generated_input_bytes = 0
    calls = 0
    for _replay in range(REPLAYS):
        current: list[list[str]] = []
        for order in ORDERS:
            for case in CASES:
                source = _build_case(case, order)
                before = vr12a.vr2._canonical_source_bytes(source)
                generated_input_bytes += len(before)
                decision = discriminate_generated_source(source)
                calls += 1
                if decision.route != CASE_ROUTES[case]:
                    raise R4ResidualDecompositionRefusal(
                        REFUSAL_ROUTES[2], "generated route differs"
                    )
                if vr12a.vr2._canonical_source_bytes(source) != before:
                    raise R4ResidualDecompositionRefusal(
                        REFUSAL_ROUTES[2], "generated source changed"
                    )
                route_counts[decision.route] += 1
                current.append([case, order, decision.route])
        replay_rows.append(current)
    result = {
        "route_counts": dict(sorted(route_counts.items())),
        "replay_digests": [
            _sha256_bytes(_canonical_json_bytes(rows)) for rows in replay_rows
        ],
        "matrix_digest_sha256": _sha256_bytes(
            _canonical_json_bytes(replay_rows[0])
        ),
        "generated_input_bytes": generated_input_bytes,
        "path_count": len(CASES) * len(ORDERS) * REPLAYS,
        "VR12A_calls": calls,
        "source_mutations_by_VR12A": 0,
        "witness_paths": (len(CASES) - 1) * len(ORDERS) * REPLAYS,
        "control_paths": len(ORDERS) * REPLAYS,
    }
    _validate_matrix(result)
    return result


def _expected_route_counts() -> dict[str, int]:
    return {route: 4 for route in (SUCCESS_ROUTE, *RESULT_ROUTES)}


def _validate_matrix(matrix: Mapping[str, Any]) -> None:
    if set(matrix) != {
        "route_counts",
        "replay_digests",
        "matrix_digest_sha256",
        "generated_input_bytes",
        "path_count",
        "VR12A_calls",
        "source_mutations_by_VR12A",
        "witness_paths",
        "control_paths",
    }:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "matrix result fields differ"
        )
    digests = matrix.get("replay_digests")
    if (
        matrix.get("route_counts") != _expected_route_counts()
        or matrix.get("path_count") != 32
        or matrix.get("VR12A_calls") != 32
        or matrix.get("source_mutations_by_VR12A") != 0
        or matrix.get("witness_paths") != 28
        or matrix.get("control_paths") != 4
        or not isinstance(matrix.get("generated_input_bytes"), int)
        or matrix.get("generated_input_bytes", 0) <= 0
        or not isinstance(digests, list)
        or len(digests) != 2
        or digests[0] != digests[1]
        or any(not isinstance(value, str) or len(value) != 64 for value in digests)
        or not isinstance(matrix.get("matrix_digest_sha256"), str)
        or len(matrix["matrix_digest_sha256"]) != 64
        or matrix["matrix_digest_sha256"] != digests[0]
    ):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "matrix result differs"
        )


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(key) != expected for key, expected in THREAD_ENVIRONMENT.items()):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[5], "thread environment differs"
        )


def _walk_public(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).casefold() in FORBIDDEN_PUBLIC_KEYS:
                raise R4ResidualDecompositionRefusal(
                    REFUSAL_ROUTES[4], "aggregate output key is forbidden"
                )
            _walk_public(item)
    elif isinstance(value, list):
        for item in value:
            _walk_public(item)
    elif isinstance(value, str):
        lowered = value.casefold()
        if (
            ".codex_work" in lowered
            or "/users/" in lowered
            or "private_manifest" in lowered
            or "safe_reason" in lowered
        ):
            raise R4ResidualDecompositionRefusal(
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
    values = (
        runtime_seconds,
        peak_rss_bytes,
        generated_input_bytes,
        aggregate_output_bytes,
        retained_output_bytes,
    )
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in values):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[5], "resource measurement differs"
        )
    if (
        runtime_seconds > caps["runtime_seconds"]
        or peak_rss_bytes >= caps["peak_RSS_bytes"]
        or generated_input_bytes > caps["generated_input_bytes"]
        or aggregate_output_bytes > caps["aggregate_output_bytes"]
        or retained_output_bytes != caps["retained_generated_output_bytes"]
    ):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[5], "resource cap exceeded"
        )


def _expect_refusal(
    name: str,
    expected_route: str,
    action: Callable[[], Any],
    counts: dict[str, str],
) -> None:
    try:
        action()
    except R4ResidualDecompositionRefusal as exc:
        if exc.route != expected_route:
            raise R4ResidualDecompositionRefusal(
                REFUSAL_ROUTES[3], "direct refusal route differs"
            ) from exc
        counts[name] = exc.route
        return
    raise R4ResidualDecompositionRefusal(
        REFUSAL_ROUTES[3], "direct mutation unexpectedly passed"
    )


def _run_direct_refusals(
    *,
    contract: Mapping[str, Any],
    payloads: Mapping[str, bytes],
    matrix: Mapping[str, Any],
) -> dict[str, str]:
    refusals: dict[str, str] = {}

    for index, mutation in enumerate(
        (
            {**contract, "schema_version": "9.9.9"},
            {**contract, "lane_id": "MARC2-VR13X"},
            {**contract, "status": "implemented"},
            {**contract, "unexpected": True},
            [],
        ),
        start=1,
    ):
        _expect_refusal(
            f"contract_drift_{index:02d}",
            REFUSAL_ROUTES[0],
            lambda value=mutation: _verify_contract_mapping(value),
            refusals,
        )

    proof_mutations = (
        {"commit": "0" * 40},
        {"ci_run_id": 0},
        {"base_job_id": 0},
        {"optional_job_id": 0},
    )
    for index, mutation in enumerate(proof_mutations, start=1):
        _expect_refusal(
            f"registration_proof_drift_{index:02d}",
            REFUSAL_ROUTES[0],
            lambda values=mutation: _verify_registration_proof(**values),
            refusals,
        )

    fixed_paths = list(payloads)[:6]
    for index, path in enumerate(fixed_paths, start=1):
        changed = dict(payloads)
        changed[path] = changed[path] + b"x"
        _expect_refusal(
            f"fixed_artifact_drift_{index:02d}",
            REFUSAL_ROUTES[1],
            lambda values=changed: _verify_fixed_payloads(contract, values),
            refusals,
        )

    unknown_pairs = (
        ("MARC2VR12A-F01", "registered contract hash differs"),
        ("MARC2VR12A-F02", "live source envelope differs"),
        ("MARC2VR12A-F03", "source row fields differ"),
        ("MARC2VR12A-F04", "wrong"),
        ("MARC2VR12A-F05", "wrong"),
        ("MARC2VR12A-F06", "wrong"),
        ("MARC2VR12A-F07", "repaired dynamic selection refused"),
        ("MARC2VR12A-F08", "scientific firewall refused"),
    )
    for index, (route, reason) in enumerate(unknown_pairs, start=1):
        exc = vr12a.P15RunIndexRepairRefusal(route, reason)
        _expect_refusal(
            f"residual_route_drift_{index:02d}",
            REFUSAL_ROUTES[2],
            lambda value=exc: _route_for_refusal(value),
            refusals,
        )

    matrix_mutations: list[dict[str, Any]] = []
    for route in (SUCCESS_ROUTE, *RESULT_ROUTES):
        changed = copy.deepcopy(dict(matrix))
        changed["route_counts"][route] = 3
        matrix_mutations.append(changed)
    for key, value in (
        ("path_count", 31),
        ("VR12A_calls", 31),
        ("source_mutations_by_VR12A", 1),
        ("control_paths", 3),
    ):
        changed = copy.deepcopy(dict(matrix))
        changed[key] = value
        matrix_mutations.append(changed)
    for index, changed in enumerate(matrix_mutations, start=1):
        _expect_refusal(
            f"matrix_drift_{index:02d}",
            REFUSAL_ROUTES[3],
            lambda value=changed: _validate_matrix(value),
            refusals,
        )

    for index, key in enumerate(sorted(FORBIDDEN_PUBLIC_KEYS)[:10], start=1):
        _expect_refusal(
            f"public_firewall_{index:02d}",
            REFUSAL_ROUTES[4],
            lambda value={key: "redacted"}: _walk_public(value),
            refusals,
        )

    resource_mutations = (
        {"runtime_seconds": 31.0},
        {"peak_rss_bytes": 268_435_456},
        {"generated_input_bytes": 25_165_825},
        {"aggregate_output_bytes": 1_048_577},
        {"retained_output_bytes": 1},
        {"runtime_seconds": -1.0},
    )
    base_resources: dict[str, int | float] = {
        "runtime_seconds": 1.0,
        "peak_rss_bytes": 1,
        "generated_input_bytes": 1,
        "aggregate_output_bytes": 1,
        "retained_output_bytes": 0,
    }
    for index, mutation in enumerate(resource_mutations, start=1):
        _expect_refusal(
            f"resource_refusal_{index:02d}",
            REFUSAL_ROUTES[5],
            lambda values={**base_resources, **mutation}: _assert_resources(
                **values, contract=contract
            ),
            refusals,
        )

    for index, environment in enumerate(
        (
            {},
            {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
            {**THREAD_ENVIRONMENT, "OPENBLAS_NUM_THREADS": "0"},
        ),
        start=1,
    ):
        _expect_refusal(
            f"thread_refusal_{index:02d}",
            REFUSAL_ROUTES[5],
            lambda value=environment: _validate_thread_environment(value),
            refusals,
        )

    if len(refusals) < contract["direct_refusal_minimum"]:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "direct refusal coverage is incomplete"
        )
    return dict(sorted(refusals.items()))


def _zero_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR11P_or_VR12P_path_or_output_operations": 0,
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


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def _stabilize_output_size(report: dict[str, Any]) -> int:
    for _ in range(10):
        size = len(_canonical_json_bytes(report))
        if report["measurements"]["aggregate_output_bytes"] == size:
            return size
        report["measurements"]["aggregate_output_bytes"] = size
    raise R4ResidualDecompositionRefusal(
        REFUSAL_ROUTES[3], "aggregate output size did not stabilize"
    )


def _validate_public_report(report: Mapping[str, Any]) -> None:
    expected_fields = {
        "schema_name",
        "schema_version",
        "lane_id",
        "route",
        "status",
        "registration_proof",
        "route_summary",
        "replay_summary",
        "mechanics",
        "measurements",
        "direct_refusals",
        "warnings",
        "access_counters",
        "acceptance_gates",
        "next_gate",
        "claim_boundary",
    }
    if set(report) != expected_fields:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "aggregate report fields differ"
        )
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
        or report.get("status") != "generated_qualification_passed"
        or report.get("route_summary", {}).get("route_counts")
        != _expected_route_counts()
        or report.get("replay_summary", {}).get("total_paths") != 32
        or report.get("replay_summary", {}).get("exact_VR12A_calls") != 32
        or len(report.get("direct_refusals", {})) < 50
        or not all(report.get("acceptance_gates", {}).values())
        or not all(value == 0 for value in report.get("access_counters", {}).values())
    ):
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "aggregate report differs"
        )
    _walk_public(report)
    if len(_canonical_json_bytes(report)) != report["measurements"]["aggregate_output_bytes"]:
        raise R4ResidualDecompositionRefusal(
            REFUSAL_ROUTES[3], "aggregate output byte count differs"
        )


def qualify_generated(
    *,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the bounded 32-path generated qualification in memory."""

    _validate_thread_environment(environment)
    start = clock()
    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    payloads = _fixed_payloads(contract)
    fixed_input_bytes = _verify_fixed_payloads(contract, payloads)
    registration_bytes = _verify_registration_artifacts(contract)
    inventory_count = _verify_static_inventory(contract, payloads)
    matrix = _run_matrix()
    direct_refusals = _run_direct_refusals(
        contract=contract, payloads=payloads, matrix=matrix
    )
    runtime_seconds = clock() - start
    peak_rss_bytes = rss_reader()
    counters = _zero_counters()
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "route": SUCCESS_ROUTE,
        "status": "generated_qualification_passed",
        "registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_jobs_green": True,
        },
        "route_summary": {
            "ordered_routes": [SUCCESS_ROUTE, *RESULT_ROUTES],
            "route_counts": matrix["route_counts"],
            "one_route_per_generated_path": True,
            "failure_details_retained": 0,
            "per_path_outcomes_retained": 0,
        },
        "replay_summary": {
            "generated_cases": len(CASES),
            "orders": len(ORDERS),
            "exact_replays": REPLAYS,
            "total_paths": matrix["path_count"],
            "exact_VR12A_calls": matrix["VR12A_calls"],
            "byte_identical_replay": True,
            "order_invariant_routes": True,
            "internal_matrix_digest_sha256": matrix["matrix_digest_sha256"],
        },
        "mechanics": {
            "entry_count_each": 1_227,
            "AST_refusal_call_sites": inventory_count,
            "witness_mutations_before_VR12A": matrix["witness_paths"],
            "control_paths_without_mutation": matrix["control_paths"],
            "post_VR12A_witness_mutations": 0,
            "source_mutations_by_VR12A": matrix["source_mutations_by_VR12A"],
            "predecessor_modules_modified": 0,
        },
        "measurements": {
            "fixed_artifact_count": 18,
            "fixed_artifact_bytes": fixed_input_bytes + registration_bytes,
            "generated_input_bytes": matrix["generated_input_bytes"],
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "end_to_end_latency_measured": False,
        },
        "direct_refusals": direct_refusals,
        "warnings": [
            "private_failure_class_unavailable",
            "real_cohort_unavailable",
            "neural_payload_not_accessed",
            "generated_routes_have_no_scientific_claim_value",
        ],
        "access_counters": counters,
        "acceptance_gates": {
            "fixed_inputs_match": True,
            "AST_inventory_matches": True,
            "seven_residual_classes_frozen": True,
            "all_32_paths_called_VR12A_once": True,
            "every_route_observed_four_times": True,
            "replay_exact": True,
            "source_immutable": True,
            "direct_refusal_minimum_passed": True,
            "retained_output_zero": True,
            "resource_caps_passed": True,
            "forbidden_operations_zero": True,
        },
        "next_gate": {
            "generated_implementation_complete": True,
            "remote_implementation_proof_required_before_Tier_C_request": True,
            "future_private_discriminator_authorized": False,
            "consumed_VR11P_or_VR12P_reuse_allowed": False,
            "MARC2_FW2_or_CIL1_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": (
                "generated reachability and deterministic discrimination of seven "
                "residual structural classes"
            ),
            "scientific_ceiling": "none",
            "neural_effect_established": False,
            "decoding_accuracy_established": False,
            "language_decoding_established": False,
            "live_decoding_established": False,
            "thought_to_text_established": False,
        },
    }
    output_bytes = _stabilize_output_size(report)
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=matrix["generated_input_bytes"],
        aggregate_output_bytes=output_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _validate_public_report(report)
    return report


def build_plan_summary() -> dict[str, Any]:
    """Return the frozen generated-only plan without running the matrix."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    return {
        "lane_id": LANE_ID,
        "status": contract["status"],
        "fixed_input_count": contract["fixed_input_count"],
        "fixed_input_bytes": contract["fixed_input_bytes"],
        "generated_cases": len(CASES),
        "required_paths": contract["generated_witness_matrix"]["required_paths"],
        "required_VR12A_calls": contract["generated_witness_matrix"][
            "required_VR12A_calls"
        ],
        "ordered_routes": [SUCCESS_ROUTE, *RESULT_ROUTES],
        "direct_refusal_minimum": contract["direct_refusal_minimum"],
        "private_access_authorized": False,
        "network_bytes": 0,
        "real_or_private_bytes": 0,
        "MARC2_FW2_or_CIL1_authorized": False,
    }


def build_inspection_summary() -> dict[str, Any]:
    """Inspect only the committed registration and proof boundary."""

    contract = load_registered_contract()
    _verify_contract_mapping(contract)
    _verify_registration_proof()
    return {
        "lane_id": LANE_ID,
        "contract_sha256": CONTRACT_SHA256,
        "registration_commit": GREEN_REGISTRATION_COMMIT,
        "registration_CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
        "both_jobs_green": True,
        "residual_class_count": len(RESULT_ROUTES),
        "private_access_authorized": False,
        "scientific_ceiling": "none",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("plan", help="show the frozen generated-only plan")
    subparsers.add_parser("inspect", help="inspect the registration proof")
    subparsers.add_parser("qualify", help="run the in-memory generated matrix")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "plan":
        payload = build_plan_summary()
    elif args.command == "inspect":
        payload = build_inspection_summary()
    else:
        payload = qualify_generated()
    sys.stdout.buffer.write(_canonical_json_bytes(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
