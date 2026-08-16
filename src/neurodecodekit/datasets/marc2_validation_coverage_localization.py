"""Artifact-only MARC2 live-validation coverage localization."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import resource
import stat
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VL1"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_validation_coverage_localization_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_validation_coverage_localization_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_validation_coverage_localization_contract.v0.json"
)
CONTRACT_SHA256 = "39fe2c2c99a824f6baf1d59294f68e5e021ecf9eca1e6a3dec14ef8e7ef6d277"
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
EXPECTED_ROLES = frozenset(
    {
        "producer_parser_module",
        "producer_live_module",
        "producer_public_result",
        "selector_module",
        "selector_contract",
        "live_adapter_module",
        "live_adapter_contract",
        "recovery_module",
        "recovery_failure_result",
    }
)
PYTHON_ROLES = frozenset(
    {
        "producer_parser_module",
        "producer_live_module",
        "selector_module",
        "live_adapter_module",
        "recovery_module",
    }
)
SUCCESS_ROUTES = ("MARC2VL-R1", "MARC2VL-R2", "MARC2VL-R3")
FAILURE_ROUTES = ("MARC2VL-F01", "MARC2VL-F02", "MARC2VL-F03")


class ValidationCoverageRefusal(RuntimeError):
    """Fail closed with one frozen MARC2-VL1 route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-VL1 refusal route")
        super().__init__(reason)
        self.route = route
        self.safe_reason = reason


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_json(payload: bytes) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, nested in pairs:
            if key in value:
                raise ValueError(f"duplicate JSON key: {key}")
            value[key] = nested
        return value

    value = json.loads(payload.decode("utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON must be an object")
    return value


def _fixed_path(root: Path, relative_text: str) -> Path:
    relative = Path(relative_text)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValidationCoverageRefusal("MARC2VL-F01", "artifact path is not fixed")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except OSError as exc:
            raise ValidationCoverageRefusal(
                "MARC2VL-F01", "artifact parent is unavailable"
            ) from exc
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ValidationCoverageRefusal(
                "MARC2VL-F01", "artifact parent is not a real directory"
            )
    path = root / relative
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact is unavailable"
        ) from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact is not a regular no-follow file"
        )
    return path


def _read_once(path: Path, *, cap: int) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValidationCoverageRefusal("MARC2VL-F01", "artifact open failed") from exc
    chunks: list[bytes] = []
    total = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise ValidationCoverageRefusal(
                "MARC2VL-F01", "artifact type or size differs"
            )
        while True:
            chunk = os.read(descriptor, min(65_536, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise ValidationCoverageRefusal(
                    "MARC2VL-F01", "artifact exceeds its read cap"
                )
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if (
        before.st_dev != after.st_dev
        or before.st_ino != after.st_ino
        or before.st_size != after.st_size
        or total != before.st_size
    ):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact identity changed during read"
        )
    return b"".join(chunks)


def _read_bound_artifact(
    root: Path,
    binding: Mapping[str, Any],
    *,
    cap: int,
) -> tuple[bytes, dict[str, Any]]:
    if set(binding) != {"role", "path", "sha256"}:
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact binding fields differ"
        )
    role = binding["role"]
    path_text = binding["path"]
    expected = binding["sha256"]
    if not all(isinstance(value, str) for value in (role, path_text, expected)):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact binding types differ"
        )
    payload = _read_once(_fixed_path(root, path_text), cap=cap)
    observed = _sha256_bytes(payload)
    if observed != expected:
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact SHA-256 differs"
        )
    return payload, {"role": role, "bytes": len(payload), "sha256": observed}


def _binding_by_role(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list):
        raise ValidationCoverageRefusal("MARC2VL-F01", "fixed inputs differ")
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("role"), str):
            raise ValidationCoverageRefusal("MARC2VL-F01", "fixed input differs")
        role = row["role"]
        if role in result:
            raise ValidationCoverageRefusal(
                "MARC2VL-F01", "artifact role is duplicated"
            )
        result[role] = row
    if set(result) != EXPECTED_ROLES:
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "artifact role inventory differs"
        )
    return result


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(matches) != 1:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"function anchor is unavailable: {name}"
        )
    return matches[0]


def _assignment_literal(tree: ast.Module, name: str) -> Any:
    matches: list[ast.AST] = []
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            matches.append(node.value)
    if len(matches) != 1:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"constant anchor is unavailable: {name}"
        )
    try:
        return ast.literal_eval(matches[0])
    except (ValueError, TypeError) as exc:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"constant is not literal: {name}"
        ) from exc


def _string_literals(node: ast.AST) -> set[str]:
    return {
        nested.value
        for nested in ast.walk(node)
        if isinstance(nested, ast.Constant) and isinstance(nested.value, str)
    }


def _name_anchors(node: ast.AST) -> set[str]:
    return {nested.id for nested in ast.walk(node) if isinstance(nested, ast.Name)}


def _require_function_anchors(
    tree: ast.Module,
    function_name: str,
    *,
    strings: Sequence[str] = (),
    names: Sequence[str] = (),
) -> ast.FunctionDef:
    function = _function(tree, function_name)
    observed_strings = _string_literals(function)
    observed_names = _name_anchors(function)
    if not set(strings).issubset(observed_strings) or not set(names).issubset(
        observed_names
    ):
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"function anchors differ: {function_name}"
        )
    return function


def _route_index_for_prefix(
    tree: ast.Module,
    *,
    function_name: str,
    prefix: str,
) -> int:
    function = _function(tree, function_name)
    matches: list[int] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.If) or prefix not in _string_literals(node.test):
            continue
        for nested in node.body:
            for candidate in ast.walk(nested):
                if not isinstance(candidate, ast.Assign) or len(candidate.targets) != 1:
                    continue
                target = candidate.targets[0]
                value = candidate.value
                if (
                    isinstance(target, ast.Name)
                    and target.id == "route"
                    and isinstance(value, ast.Subscript)
                    and isinstance(value.value, ast.Name)
                    and value.value.id == "FAILURE_ROUTES"
                    and isinstance(value.slice, ast.Constant)
                    and isinstance(value.slice.value, int)
                ):
                    matches.append(value.slice.value)
    if len(matches) != 1:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", "recovery route mapping anchor is ambiguous"
        )
    return matches[0]


def _line_with_reason(function: ast.FunctionDef, reason: str) -> int:
    matches = [
        node.lineno
        for node in ast.walk(function)
        if isinstance(node, ast.If) and reason in _string_literals(node)
    ]
    if len(matches) != 1:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"validation reason anchor is ambiguous: {reason}"
        )
    return matches[0]


def _assignment_line(function: ast.FunctionDef, target_name: str) -> int:
    matches: list[int] = []
    for node in ast.walk(function):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if any(
            isinstance(target, ast.Name) and target.id == target_name
            for target in targets
        ):
            matches.append(node.lineno)
    if len(matches) != 1:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", f"assignment anchor is ambiguous: {target_name}"
        )
    return matches[0]


def _selector_fixture_coverage(tree: ast.Module) -> dict[str, bool]:
    function = _require_function_anchors(
        tree,
        "build_generated_manifest",
        strings=(
            "public_eligibility",
            "published_session_1_2_run_counts",
            "Freewill_generated/generated_aux/aux-",
        ),
        names=(
            "EXPECTED_FILES",
            "REQUIRED_SUFFIXES",
            "auxiliary_count",
            "counts",
            "file_names",
        ),
    )
    normalized = ast.unparse(function)
    uses_eligible_counts = (
        "counts = registered['public_eligibility']['published_session_1_2_run_counts']"
        in normalized
        and "for subject in sorted(counts):" in normalized
    )
    fills_remaining_as_auxiliary = (
        "auxiliary_count = EXPECTED_FILES - len(file_names)" in normalized
        and "Freewill_generated/generated_aux/aux-{index:04d}.txt" in normalized
    )
    if not uses_eligible_counts or not fills_remaining_as_auxiliary:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", "generated fixture coverage anchors differ"
        )
    return {
        "uses_only_eligible_session_1_2_count_map": uses_eligible_counts,
        "fills_remaining_regular_rows_with_generic_auxiliary_names": (
            fills_remaining_as_auxiliary
        ),
    }


def _live_validator_order(tree: ast.Module) -> dict[str, Any]:
    function = _require_function_anchors(
        tree,
        "_validate_live_source_manifest",
        strings=(
            "live source entry count differs",
            "live source entry-kind counts differ",
            "live source run inventory differs",
            "live source public run counts differ",
        ),
        names=(
            "grouped",
            "eligibility",
            "observed_counts",
        ),
    )
    global_group_total_line = _line_with_reason(
        function, "live source run inventory differs"
    )
    eligibility_line = _assignment_line(function, "eligibility")
    if global_group_total_line >= eligibility_line:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", "live validator filtering order differs"
        )
    return {
        "global_group_total_line": global_group_total_line,
        "eligibility_lookup_line": eligibility_line,
        "global_exact_group_total_precedes_eligibility_counting": True,
    }


def _producer_guarantees(
    parser_tree: ast.Module,
    live_tree: ast.Module,
) -> dict[str, bool]:
    parser = _require_function_anchors(
        parser_tree,
        "parse_central_directory",
        strings=(
            "normalized member name repeats",
            "compression method is unsupported",
            "directory entry differs",
            "regular member ends in slash",
            "CRC32",
            "ZIP64_extra_used",
            "member_name",
        ),
        names=("records", "names", "kinds"),
    )
    live = _require_function_anchors(
        live_tree,
        "_private_manifest",
        strings=(
            "neurodecodekit.marc1_central_directory_private_manifest",
            "live_archive_private_central_directory_metadata_only",
            "Figshare",
            "transport_body_sha256",
            "response_body_sha256",
        ),
        names=("manifest", "run"),
    )
    return {
        "duplicate_full_member_names_refused": (
            "normalized member name repeats" in _string_literals(parser)
        ),
        "row_fields_are_emitted_by_the_parser": "CRC32" in _string_literals(parser),
        "live_envelope_is_added_by_the_exact_producer": (
            "live_archive_private_central_directory_metadata_only"
            in _string_literals(live)
        ),
    }


def classify_coverage(
    *,
    published_participants: int,
    published_runs: int,
    eligible_participants: int,
    eligible_runs: int,
    required_companions: int,
    expected_regular_rows: int,
    expected_source_run_bundles: int,
    fixture_uses_eligible_counts: bool,
    fixture_fills_auxiliary_rows: bool,
    validator_global_equality_before_filter: bool,
    observed_outer_route: str,
) -> dict[str, Any]:
    """Classify source-domain coverage without reading source rows."""

    values = (
        published_participants,
        published_runs,
        eligible_participants,
        eligible_runs,
        required_companions,
        expected_regular_rows,
        expected_source_run_bundles,
    )
    if any(isinstance(value, bool) or not isinstance(value, int) or value < 0 for value in values):
        raise ValidationCoverageRefusal("MARC2VL-F03", "coverage count differs")
    generated_core_rows = eligible_runs * required_companions
    published_space_slots = published_runs * required_companions
    gap_runs = published_runs - eligible_runs
    gap_participants = published_participants - eligible_participants
    gap_slots = published_space_slots - generated_core_rows
    generated_auxiliary_rows = expected_regular_rows - generated_core_rows
    if min(gap_runs, gap_participants, gap_slots, generated_auxiliary_rows) < 0:
        return {
            "route": "MARC2VL-R3",
            "published_minus_eligible_runs": gap_runs,
            "published_minus_eligible_participants": gap_participants,
            "generated_coverage_gap_companion_slots": gap_slots,
            "generated_auxiliary_regular_rows": generated_auxiliary_rows,
        }
    blind_spot = (
        observed_outer_route == "MARC2LAR-F02"
        and expected_source_run_bundles == eligible_runs
        and gap_runs > 0
        and gap_participants > 0
        and fixture_uses_eligible_counts
        and fixture_fills_auxiliary_rows
        and validator_global_equality_before_filter
    )
    if blind_spot:
        route = "MARC2VL-R2"
    elif gap_runs == 0 and gap_participants == 0 and not validator_global_equality_before_filter:
        route = "MARC2VL-R1"
    else:
        route = "MARC2VL-R3"
    return {
        "route": route,
        "published_minus_eligible_runs": gap_runs,
        "published_minus_eligible_participants": gap_participants,
        "generated_eligible_core_rows": generated_core_rows,
        "published_space_companion_slots": published_space_slots,
        "generated_coverage_gap_companion_slots": gap_slots,
        "generated_auxiliary_regular_rows": generated_auxiliary_rows,
        "source_domain_coverage_blind_spot": blind_spot,
    }


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise ValidationCoverageRefusal(
            "MARC2VL-F03", "one-thread environment is not explicit"
        )


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "crc32",
        "decoded_text",
        "labels",
        "member_name",
        "predictions",
        "private_path",
        "signal",
        "target",
        "targets",
    }
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in forbidden_keys:
                raise ValidationCoverageRefusal(
                    "MARC2VL-F03", "forbidden private or scientific field"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str) and ".codex_work" in value:
        raise ValidationCoverageRefusal(
            "MARC2VL-F03", "private path leaked into aggregate"
        )


def _contract(root: Path) -> tuple[dict[str, Any], bytes]:
    path = _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    payload = _read_once(path, cap=2 * 1024**2)
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise ValidationCoverageRefusal("MARC2VL-F01", "contract SHA-256 differs")
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValidationCoverageRefusal("MARC2VL-F01", "contract JSON differs") from exc
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
    ):
        raise ValidationCoverageRefusal("MARC2VL-F01", "contract identity differs")
    return contract, payload


def audit_repository(
    *,
    repo_root: str | Path,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the fixed artifact-only MARC2-VL1 audit."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root).resolve()
    contract, contract_payload = _contract(root)
    caps = contract["resource_caps"]
    bindings = _binding_by_role(contract)

    payloads: dict[str, bytes] = {}
    measured_inputs: list[dict[str, Any]] = []
    input_bytes = len(contract_payload)
    for role in sorted(bindings):
        payload, measured = _read_bound_artifact(
            root,
            bindings[role],
            cap=caps["per_artifact_bytes"],
        )
        payloads[role] = payload
        measured_inputs.append(measured)
        input_bytes += len(payload)
    if input_bytes > caps["total_input_bytes"]:
        raise ValidationCoverageRefusal("MARC2VL-F03", "total input cap exceeded")

    python_trees: dict[str, ast.Module] = {}
    json_values: dict[str, dict[str, Any]] = {}
    for role, payload in payloads.items():
        try:
            if role in PYTHON_ROLES:
                python_trees[role] = ast.parse(payload.decode("utf-8"))
            else:
                json_values[role] = _strict_json(payload)
        except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise ValidationCoverageRefusal(
                "MARC2VL-F01", f"artifact parse failed: {role}"
            ) from exc

    selector_tree = python_trees["selector_module"]
    constants = {
        name: _assignment_literal(selector_tree, name)
        for name in (
            "EXPECTED_ROWS",
            "EXPECTED_FILES",
            "EXPECTED_DIRECTORIES",
            "EXPECTED_SOURCE_RUN_BUNDLES",
            "REQUIRED_SUFFIXES",
        )
    }
    fixture = _selector_fixture_coverage(selector_tree)
    validator = _live_validator_order(python_trees["live_adapter_module"])
    producer = _producer_guarantees(
        python_trees["producer_parser_module"],
        python_trees["producer_live_module"],
    )
    route_index = _route_index_for_prefix(
        python_trees["recovery_module"],
        function_name="adapt_and_select",
        prefix="MARC2LA-F02",
    )
    if route_index != 2:
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", "LA1 F02 route mapping differs"
        )

    selector_contract = json_values["selector_contract"]
    producer_result = json_values["producer_public_result"]
    recovery_result = json_values["recovery_failure_result"]
    live_contract = json_values["live_adapter_contract"]
    public = selector_contract.get("public_eligibility", {})
    eligible_ids = public.get("eligible_subject_ids")
    count_map = public.get("published_session_1_2_run_counts")
    if not isinstance(eligible_ids, list) or not isinstance(count_map, dict):
        raise ValidationCoverageRefusal("MARC2VL-F01", "eligibility registry differs")
    if set(eligible_ids) != set(count_map):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "eligibility count-map membership differs"
        )
    if any(
        not isinstance(row, list)
        or len(row) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) for value in row)
        for row in count_map.values()
    ):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "eligibility run-count shape differs"
        )
    eligible_runs = sum(sum(row) for row in count_map.values())
    archive = producer_result.get("archive_summary", {})
    facts = contract["registered_facts"]
    if (
        archive.get("entry_count") != constants["EXPECTED_ROWS"]
        or archive.get("regular_file_entries") != constants["EXPECTED_FILES"]
        or archive.get("directory_entries") != constants["EXPECTED_DIRECTORIES"]
        or len(eligible_ids) != facts["eligible_participants"]
        or eligible_runs != facts["eligible_session_1_2_runs"]
        or live_contract.get("generated_live_shaped_source", {}).get("entries")
        != constants["EXPECTED_ROWS"]
        or recovery_result.get("route") != "MARC2LAR-F02"
        or recovery_result.get("stop_result", {}).get("stage")
        != "live_adapter_and_frozen_selector"
        or recovery_result.get("stop_result", {}).get("aggregate_safe_reason")
        != "LA1 adapter refused source"
    ):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "committed aggregate facts differ"
        )

    coverage = classify_coverage(
        published_participants=public["published_participants"],
        published_runs=public["published_runs"],
        eligible_participants=len(eligible_ids),
        eligible_runs=eligible_runs,
        required_companions=len(constants["REQUIRED_SUFFIXES"]),
        expected_regular_rows=constants["EXPECTED_FILES"],
        expected_source_run_bundles=constants["EXPECTED_SOURCE_RUN_BUNDLES"],
        fixture_uses_eligible_counts=fixture[
            "uses_only_eligible_session_1_2_count_map"
        ],
        fixture_fills_auxiliary_rows=fixture[
            "fills_remaining_regular_rows_with_generic_auxiliary_names"
        ],
        validator_global_equality_before_filter=validator[
            "global_exact_group_total_precedes_eligibility_counting"
        ],
        observed_outer_route=recovery_result["route"],
    )
    if coverage["route"] != "MARC2VL-R2":
        raise ValidationCoverageRefusal(
            "MARC2VL-F02", "frozen coverage classification differs"
        )
    expected_coverage = {
        key: facts[key]
        for key in (
            "published_minus_eligible_participants",
            "published_minus_eligible_runs",
            "generated_eligible_core_rows",
            "published_space_companion_slots",
            "generated_coverage_gap_companion_slots",
            "generated_auxiliary_regular_rows",
        )
    }
    if any(coverage[key] != value for key, value in expected_coverage.items()):
        raise ValidationCoverageRefusal(
            "MARC2VL-F01", "registered coverage arithmetic differs"
        )

    runtime = clock() - started
    peak_rss = int(rss_reader())
    if runtime > caps["runtime_seconds"] or peak_rss > caps["peak_RSS_bytes"]:
        raise ValidationCoverageRefusal("MARC2VL-F03", "resource cap exceeded")
    access_counters = {
        "committed_contract_and_artifact_reads": len(measured_inputs) + 1,
        "private_or_Git_ignored_path_operations": 0,
        "consumed_marker_or_output_root_operations": 0,
        "archive_local_header_or_member_payload_reads": 0,
        "signal_event_target_label_quality_channel_or_geometry_reads": 0,
        "derivative_cache_feature_split_or_neurotoken_operations": 0,
        "training_inference_prediction_freeze_delivery_or_score_operations": 0,
        "network_download_provider_or_language_model_operations": 0,
        "stream_device_or_hardware_operations": 0,
        "consumed_executor_patch_retry_rerun_resume_or_repair_operations": 0,
        "MARC2_FW2_operations": 0,
        "scientific_claim_upgrades": 0,
    }
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_artifact_only_validation_coverage_localization",
        "proof_posture": (
            "fixed_committed_code_and_aggregate_artifacts_only_no_private_or_scientific_value"
        ),
        "upstream_consumed_result": contract["upstream_consumed_result_proof"],
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "sha256": CONTRACT_SHA256,
            "fixed_input_artifacts": len(measured_inputs),
            "private_or_Git_ignored_input_artifacts": 0,
        },
        "route_class_localization": {
            "observed_outer_route": recovery_result["route"],
            "observed_stage": recovery_result["stop_result"]["stage"],
            "LA1_F02_maps_to_outer_failure_index": route_index,
            "source_envelope_or_entry_class_consistent": True,
            "transport_or_digest_class_reached": False,
            "identity_bridge_class_reached": False,
            "green_adapter_or_selector_execution_reached": False,
            "exact_private_predicate_identified": False,
        },
        "public_source_space": {
            "inventory_rows": archive["entry_count"],
            "regular_file_rows": archive["regular_file_entries"],
            "directory_rows": archive["directory_entries"],
            "published_participants": public["published_participants"],
            "published_runs": public["published_runs"],
            "eligible_participants": len(eligible_ids),
            "eligible_session_1_2_runs": eligible_runs,
        },
        "generated_fixture_coverage": {
            **fixture,
            **coverage,
            "required_companions_per_run": len(constants["REQUIRED_SUFFIXES"]),
        },
        "validator_order": validator,
        "producer_guarantees": producer,
        "candidate_leaf_boundary": contract["candidate_leaf_boundary"],
        "prospective_repair_design": contract["prospective_repair_design"],
        "measurements": {
            "input_artifact_count": len(measured_inputs) + 1,
            "input_bytes": input_bytes,
            "Python_AST_parses": len(python_trees),
            "strict_JSON_parses": len(json_values) + 1,
            "runtime_seconds": runtime,
            "peak_RSS_bytes": peak_rss,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_artifact_only",
            "end_to_end_latency_measured": False,
        },
        "access_counters": access_counters,
        "acceptance_gates": {
            "all_fixed_artifact_hashes_passed": True,
            "exact_outer_to_LA1_route_class_mapping": True,
            "producer_envelope_and_row_guarantees_anchored": True,
            "public_and_generated_count_arithmetic_reconciled": True,
            "generated_fixture_coverage_hole_localized": True,
            "global_run_total_precedes_eligibility_filter": True,
            "exact_private_predicate_left_unresolved": True,
            "one_thread_runtime_RSS_and_output_caps": True,
            "zero_private_archive_neural_target_model_score_network_operations": True,
        },
        "route": coverage["route"],
        "warnings": [
            "The audit localizes a generated-fixture and validator-domain blind spot; it does not identify the exact private refusal predicate.",
            "Published run totals are aggregate source-space facts, not a publication of private archive row identities.",
            "The prospective repair is a generated-only design and authorizes no new private read or MARC2-FW2 work.",
        ],
        "unavailable_fields": [
            "exact private LA1 predicate and source row identities",
            "actual excluded-run or extra-session archive membership",
            "archive member payload integrity signals events targets and quality",
            "neural features predictions scores and causal latency",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    for _ in range(5):
        payload = _canonical_json_bytes(report)
        measured = len(payload)
        if report["measurements"]["aggregate_output_bytes"] == measured:
            break
        report["measurements"]["aggregate_output_bytes"] = measured
    payload = _canonical_json_bytes(report)
    if (
        len(payload) != report["measurements"]["aggregate_output_bytes"]
        or len(payload) > caps["generated_output_bytes"]
    ):
        raise ValidationCoverageRefusal("MARC2VL-F03", "output cap differs")
    _walk_public(report)
    return report


def plan(*, repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    contract, _payload = _contract(root)
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": contract["lane_id"],
        "status": contract["status"],
        "fixed_input_count": len(contract["fixed_inputs"]),
        "private_or_Git_ignored_bytes": contract["resource_caps"][
            "private_or_Git_ignored_bytes"
        ],
        "network_bytes": contract["resource_caps"]["network_bytes"],
        "private_access_authorized": False,
        "MARC2_FW2_authorized": False,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=(
            "python -m neurodecodekit.datasets."
            "marc2_validation_coverage_localization"
        ),
        description=(
            "Audit fixed committed MARC2 validation-coverage artifacts without "
            "private data access."
        ),
    )
    parser.add_argument("command", choices=("plan", "audit"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        value = (
            plan(repo_root=_repo_root())
            if args.command == "plan"
            else audit_repository(repo_root=_repo_root())
        )
    except ValidationCoverageRefusal as exc:
        print(f"{exc.route}: {exc.safe_reason}", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(value).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
