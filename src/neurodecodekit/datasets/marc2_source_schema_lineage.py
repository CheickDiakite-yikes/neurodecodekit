"""Artifact-only MARC-2 source-schema lineage audit."""

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
from typing import Any, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_SCHEMA_NAME = "neurodecodekit.marc2_source_schema_lineage_contract"
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_source_schema_lineage_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_source_schema_lineage_contract.v0.json"
)
CONTRACT_SHA256 = "1ef2f481219a002318acddeca02b0dccf2b54b636c93b712defce82b9e7ff1ce"
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
EXPECTED_ROLES = {
    "producer_live_module",
    "producer_implementation_registry",
    "producer_public_live_result",
    "selector_module",
    "selector_contract",
    "selector_implementation_registry",
    "recovery_module",
    "recovery_implementation_registry",
    "recovery_failure_result",
}
PYTHON_ROLES = {
    "producer_live_module",
    "selector_module",
    "recovery_module",
}
MAX_ARTIFACT_BYTES = 2 * 1024**2
MAX_TOTAL_INPUT_BYTES = 4 * 1024**2


class SourceSchemaLineageRefusal(RuntimeError):
    """Fail-closed refusal with a frozen MARC2-SL1 route."""

    def __init__(self, route: str, message: str) -> None:
        super().__init__(message)
        self.route = route


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_json(payload: bytes) -> dict[str, Any]:
    def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    value = json.loads(payload.decode("utf-8"), object_pairs_hook=reject_duplicates)
    if not isinstance(value, dict):
        raise ValueError("top-level JSON must be an object")
    return value


def _fixed_path(root: Path, relative_text: str) -> Path:
    relative = Path(relative_text)
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact path is not fixed")
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        try:
            mode = os.lstat(current).st_mode
        except OSError as exc:
            raise SourceSchemaLineageRefusal(
                "MARC2SL-F01", "artifact parent is unavailable"
            ) from exc
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise SourceSchemaLineageRefusal(
                "MARC2SL-F01", "artifact parent is not a real directory"
            )
    path = root / relative
    try:
        mode = os.lstat(path).st_mode
    except OSError as exc:
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F01", "artifact is unavailable"
        ) from exc
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F01", "artifact is not a regular no-follow file"
        )
    return path


def _read_once(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact open failed") from exc
    chunks: list[bytes] = []
    total = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_ARTIFACT_BYTES:
            raise SourceSchemaLineageRefusal(
                "MARC2SL-F01", "artifact type or size differs"
            )
        while True:
            chunk = os.read(descriptor, min(65_536, MAX_ARTIFACT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_ARTIFACT_BYTES:
                raise SourceSchemaLineageRefusal(
                    "MARC2SL-F01", "artifact exceeds the read cap"
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
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F01", "artifact identity changed during read"
        )
    return b"".join(chunks)


def _read_bound_artifact(
    root: Path,
    binding: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    if set(binding) != {"role", "path", "sha256"}:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact binding differs")
    role = binding["role"]
    path_text = binding["path"]
    expected_sha256 = binding["sha256"]
    if not all(isinstance(value, str) for value in (role, path_text, expected_sha256)):
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact binding type differs")
    path = _fixed_path(root, path_text)
    payload = _read_once(path)
    observed_sha256 = _sha256_bytes(payload)
    if observed_sha256 != expected_sha256:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact SHA-256 differs")
    return payload, {
        "role": role,
        "path": path_text,
        "bytes": len(payload),
        "sha256": observed_sha256,
    }


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(matches) != 1:
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F02", f"function anchor is unavailable: {name}"
        )
    return matches[0]


def _literal_string_set(node: ast.AST) -> set[str] | None:
    if not isinstance(node, ast.Set):
        return None
    values: set[str] = set()
    for item in node.elts:
        if not isinstance(item, ast.Constant) or not isinstance(item.value, str):
            return None
        values.add(item.value)
    return values


def _set_call_name(node: ast.AST) -> str | None:
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "set"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and not node.keywords
    ):
        return node.args[0].id
    return None


def _validator_transport_keys(tree: ast.Module, function_name: str) -> list[str]:
    function = _function(tree, function_name)
    matches: list[set[str]] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Compare) or len(node.ops) != 1:
            continue
        if not isinstance(node.ops[0], (ast.Eq, ast.NotEq)):
            continue
        right = node.comparators[0]
        if _set_call_name(node.left) == "transport":
            value = _literal_string_set(right)
        elif _set_call_name(right) == "transport":
            value = _literal_string_set(node.left)
        else:
            value = None
        if value is not None:
            matches.append(value)
    if len(matches) != 1:
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F02", f"transport set anchor is ambiguous: {function_name}"
        )
    return sorted(matches[0])


def _generated_transport_keys(tree: ast.Module, function_name: str) -> list[str]:
    function = _function(tree, function_name)
    matches: list[set[str]] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if (
                isinstance(key, ast.Constant)
                and key.value == "transport_body_sha256"
                and isinstance(value, ast.Dict)
            ):
                nested: set[str] = set()
                for nested_key in value.keys:
                    if (
                        not isinstance(nested_key, ast.Constant)
                        or not isinstance(nested_key.value, str)
                    ):
                        raise SourceSchemaLineageRefusal(
                            "MARC2SL-F02", "generated transport key is not literal"
                        )
                    nested.add(nested_key.value)
                matches.append(nested)
    if len(matches) != 1:
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F02", "generated transport mapping anchor is ambiguous"
        )
    return sorted(matches[0])


def _subscript_string(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Subscript):
        return None
    value = node.slice
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


def _producer_forwards_transport(
    tree: ast.Module,
    *,
    function_name: str,
    destination_field: str,
    source_field: str,
) -> bool:
    function = _function(tree, function_name)
    matches = 0
    for node in ast.walk(function):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if _subscript_string(node.targets[0]) != destination_field:
            continue
        constants = {
            nested.value
            for nested in ast.walk(node.value)
            if isinstance(nested, ast.Constant) and isinstance(nested.value, str)
        }
        attributes = {
            nested.attr for nested in ast.walk(node.value) if isinstance(nested, ast.Attribute)
        }
        if source_field in constants and "transport" in attributes:
            matches += 1
    if matches != 1:
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F02", "producer transport forwarding anchor is ambiguous"
        )
    return True


def classify_transport_lineage(
    *,
    producer_keys: Sequence[str],
    selector_fixture_keys: Sequence[str],
    selector_validator_keys: Sequence[str],
    recovery_validator_keys: Sequence[str],
) -> dict[str, Any]:
    """Classify exact key-set compatibility without reading any artifact."""

    producer = set(producer_keys)
    fixture = set(selector_fixture_keys)
    selector_validator = set(selector_validator_keys)
    recovery_validator = set(recovery_validator_keys)
    if any(len(values) != len(set(values)) for values in (
        producer_keys,
        selector_fixture_keys,
        selector_validator_keys,
        recovery_validator_keys,
    )):
        raise SourceSchemaLineageRefusal("MARC2SL-F02", "duplicate transport key")
    if fixture != selector_validator or fixture != recovery_validator:
        return {
            "route": "MARC2SL-R3",
            "shared_keys": sorted(producer & fixture),
            "producer_only_keys": sorted(producer - fixture),
            "consumer_only_keys": sorted(fixture - producer),
            "consumer_internal_consistent": False,
            "exact_single_alias_mismatch": False,
        }
    producer_only = sorted(producer - fixture)
    consumer_only = sorted(fixture - producer)
    if not producer_only and not consumer_only:
        route = "MARC2SL-R1"
    elif producer_only == ["directory"] and consumer_only == ["central_directory"]:
        route = "MARC2SL-R2"
    else:
        route = "MARC2SL-R3"
    return {
        "route": route,
        "shared_keys": sorted(producer & fixture),
        "producer_only_keys": producer_only,
        "consumer_only_keys": consumer_only,
        "consumer_internal_consistent": True,
        "exact_single_alias_mismatch": route == "MARC2SL-R2",
    }


def _binding_by_role(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    bindings = contract.get("fixed_inputs")
    if not isinstance(bindings, list):
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "fixed inputs differ")
    result: dict[str, Mapping[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, dict) or not isinstance(binding.get("role"), str):
            raise SourceSchemaLineageRefusal("MARC2SL-F01", "fixed input differs")
        role = binding["role"]
        if role in result:
            raise SourceSchemaLineageRefusal("MARC2SL-F01", "duplicate artifact role")
        result[role] = binding
    if set(result) != EXPECTED_ROLES:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "artifact roles differ")
    return result


def _walk_forbidden_keys(value: Any) -> None:
    forbidden = {
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
            if key.lower() in forbidden:
                raise SourceSchemaLineageRefusal(
                    "MARC2SL-F01", "forbidden private or scientific field"
                )
            _walk_forbidden_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_forbidden_keys(nested)


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F01", "one-thread environment is not explicit"
        )


def _registry_hash(rows: Sequence[Mapping[str, Any]], path: str) -> str | None:
    matches = [row.get("sha256") for row in rows if row.get("path") == path]
    if len(matches) != 1 or not isinstance(matches[0], str):
        return None
    return matches[0]


def audit_repository(*, repo_root: str | Path) -> dict[str, Any]:
    """Run the fixed, artifact-only MARC2-SL1 audit."""

    started = time.perf_counter()
    _validate_thread_environment()
    root = Path(repo_root).resolve()
    contract_payload = _read_once(_fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix()))
    if _sha256_bytes(contract_payload) != CONTRACT_SHA256:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "contract SHA-256 differs")
    try:
        contract = _strict_json(contract_payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "contract JSON differs") from exc
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != "MARC2-SL1"
    ):
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "contract identity differs")

    bindings = _binding_by_role(contract)
    payloads: dict[str, bytes] = {}
    measured_inputs: list[dict[str, Any]] = []
    total_input_bytes = len(contract_payload)
    for role in sorted(bindings):
        payload, measured = _read_bound_artifact(root, bindings[role])
        payloads[role] = payload
        measured_inputs.append(measured)
        total_input_bytes += len(payload)
    if total_input_bytes > MAX_TOTAL_INPUT_BYTES:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "total input cap exceeded")

    python_trees: dict[str, ast.Module] = {}
    json_values: dict[str, dict[str, Any]] = {}
    for role, payload in payloads.items():
        try:
            if role in PYTHON_ROLES:
                python_trees[role] = ast.parse(payload.decode("utf-8"))
            else:
                json_values[role] = _strict_json(payload)
        except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise SourceSchemaLineageRefusal(
                "MARC2SL-F01", f"artifact parse failed: {role}"
            ) from exc

    lineage = contract["registered_lineage"]
    producer_result = json_values["producer_public_live_result"]
    producer_implementation = json_values["producer_implementation_registry"]
    selector_contract = json_values["selector_contract"]
    selector_implementation = json_values["selector_implementation_registry"]
    recovery_implementation = json_values["recovery_implementation_registry"]
    recovery_result = json_values["recovery_failure_result"]

    producer_module_hash = bindings["producer_live_module"]["sha256"]
    selector_module_hash = bindings["selector_module"]["sha256"]
    recovery_module_hash = bindings["recovery_module"]["sha256"]
    if (
        producer_implementation.get("implementation_surface", {}).get("module_SHA256")
        != producer_module_hash
        or selector_implementation.get("artifact_bindings", {}).get("module", {}).get(
            "sha256"
        )
        != selector_module_hash
        or _registry_hash(
            recovery_implementation.get("tracked_file_hashes", []),
            bindings["recovery_module"]["path"],
        )
        != recovery_module_hash
    ):
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "module lineage differs")

    producer_keys = sorted(
        producer_result.get("transport_summary", {})
        .get("response_body_sha256", {})
        .keys()
    )
    producer_forwarding = _producer_forwards_transport(
        python_trees["producer_live_module"],
        function_name=lineage["producer_manifest_function"],
        destination_field=lineage["producer_forwarded_field"],
        source_field=lineage["producer_forwarded_source_field"],
    )
    fixture_keys = _generated_transport_keys(
        python_trees["selector_module"], lineage["selector_fixture_function"]
    )
    selector_validator_keys = _validator_transport_keys(
        python_trees["selector_module"], lineage["selector_validator_function"]
    )
    recovery_validator_keys = _validator_transport_keys(
        python_trees["recovery_module"], lineage["recovery_validator_function"]
    )
    classification = classify_transport_lineage(
        producer_keys=producer_keys,
        selector_fixture_keys=fixture_keys,
        selector_validator_keys=selector_validator_keys,
        recovery_validator_keys=recovery_validator_keys,
    )

    expected = {
        "producer_keys": lineage["producer_public_transport_keys"],
        "fixture_keys": lineage["selector_fixture_transport_keys"],
        "selector_validator_keys": lineage["selector_validator_transport_keys"],
        "recovery_validator_keys": lineage["recovery_validator_transport_keys"],
        "shared_keys": lineage["expected_shared_transport_keys"],
        "producer_only_keys": lineage["expected_producer_only_transport_keys"],
        "consumer_only_keys": lineage["expected_consumer_only_transport_keys"],
    }
    observed = {
        "producer_keys": producer_keys,
        "fixture_keys": fixture_keys,
        "selector_validator_keys": selector_validator_keys,
        "recovery_validator_keys": recovery_validator_keys,
        "shared_keys": classification["shared_keys"],
        "producer_only_keys": classification["producer_only_keys"],
        "consumer_only_keys": classification["consumer_only_keys"],
    }
    if observed != expected or classification["route"] != "MARC2SL-R2":
        raise SourceSchemaLineageRefusal(
            "MARC2SL-F02", "committed lineage differs from the frozen audit"
        )

    private_sha = lineage["private_manifest_sha256"]
    private_bytes = lineage["private_manifest_bytes"]
    source_bindings_match = (
        producer_result.get("archive_summary", {}).get("private_manifest_sha256")
        == private_sha
        and selector_contract.get("source_identity", {}).get("private_manifest_sha256")
        == private_sha
        and selector_contract.get("source_identity", {}).get("private_manifest_bytes")
        == private_bytes
        and recovery_implementation.get("private_source_binding", {}).get("sha256")
        == private_sha
        and recovery_implementation.get("private_source_binding", {}).get("bytes")
        == private_bytes
        and recovery_result.get("measurements", {}).get("input_bytes") == private_bytes
    )
    failure_identity_matches = (
        recovery_result.get("route") == lineage["observed_consumed_route"]
        and recovery_result.get("failure_boundary", {}).get("stage")
        == lineage["observed_consumed_stage"]
        and recovery_result.get("failure_boundary", {}).get("safe_reason")
        == lineage["observed_safe_reason"]
    )
    if not producer_forwarding or not source_bindings_match or not failure_identity_matches:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "bound lineage proof differs")

    runtime_seconds = time.perf_counter() - started
    peak_rss_bytes = _peak_rss_bytes()
    caps = contract["resource_caps"]
    if runtime_seconds > caps["runtime_seconds"] or peak_rss_bytes > caps["peak_RSS_bytes"]:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "resource cap exceeded")

    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": "MARC2-SL1",
        "status": "completed_exact_committed_transport_key_lineage_diagnosis",
        "route": classification["route"],
        "proof_posture": "post_failure_artifact_only_engineering_diagnosis_no_private_or_scientific_value",
        "contract_sha256": CONTRACT_SHA256,
        "artifact_inputs": measured_inputs,
        "lineage": {
            "producer_forwarded_transport_hash_map": producer_forwarding,
            "producer_public_transport_keys": producer_keys,
            "selector_fixture_transport_keys": fixture_keys,
            "selector_validator_transport_keys": selector_validator_keys,
            "recovery_validator_transport_keys": recovery_validator_keys,
            "shared_transport_keys": classification["shared_keys"],
            "producer_only_transport_keys": classification["producer_only_keys"],
            "consumer_only_transport_keys": classification["consumer_only_keys"],
            "consumer_internal_consistent": classification[
                "consumer_internal_consistent"
            ],
            "exact_single_alias_mismatch": classification[
                "exact_single_alias_mismatch"
            ],
            "source_binding_hash_and_bytes_match_across_committed_records": (
                source_bindings_match
            ),
            "observed_failure_identity_matches": failure_identity_matches,
            "sufficient_to_explain_observed_structural_refusal": True,
            "actual_private_field_or_value_observed": False,
        },
        "prospective_adapter_design": contract["prospective_adapter_design"],
        "measurements": {
            "input_artifact_count": len(measured_inputs) + 1,
            "input_bytes": total_input_bytes,
            "Python_AST_parses": len(python_trees),
            "strict_JSON_parses": len(json_values) + 1,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "generated_output_bytes": 0,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_artifact_only",
            "end_to_end_latency_measured": False,
        },
        "access_counters": {
            "committed_public_artifact_reads": len(measured_inputs) + 1,
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
        },
        "warnings": [
            "This is a post-failure engineering diagnosis over committed public artifacts.",
            "The audit did not reopen the private manifest or identify a private value.",
            "A future adapter remains unimplemented and cannot authorize another live read.",
        ],
        "unavailable_fields": [
            "private manifest field values beyond committed aggregate identities",
            "archive member headers payloads signals events targets and quality",
            "neural features predictions scores and causal latency",
        ],
        "claim_boundary": contract["claim_boundary"],
    }
    for _ in range(4):
        payload = _canonical_json_bytes(report)
        measured = len(payload)
        if report["measurements"]["generated_output_bytes"] == measured:
            break
        report["measurements"]["generated_output_bytes"] = measured
    payload = _canonical_json_bytes(report)
    if (
        len(payload) != report["measurements"]["generated_output_bytes"]
        or len(payload) > caps["generated_output_bytes"]
    ):
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "output cap differs")
    _walk_forbidden_keys(report)
    return report


def plan(*, repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    payload = _read_once(_fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix()))
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise SourceSchemaLineageRefusal("MARC2SL-F01", "contract SHA-256 differs")
    contract = _strict_json(payload)
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
        "future_live_access_authorized": False,
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m neurodecodekit.datasets.marc2_source_schema_lineage",
        description="Audit fixed committed MARC-2 source-schema lineage artifacts.",
    )
    parser.add_argument("command", choices=("plan", "audit"))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        value = plan(repo_root=_repo_root()) if args.command == "plan" else audit_repository(
            repo_root=_repo_root()
        )
    except SourceSchemaLineageRefusal as exc:
        print(f"{exc.route}: {exc}", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(value).decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
