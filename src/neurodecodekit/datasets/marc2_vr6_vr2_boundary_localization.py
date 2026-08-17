"""Artifact-only localization of the MARC2 VR6-to-VR2 refusal boundary."""

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
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR8A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_vr6_vr2_boundary_localization_contract"
)
REPORT_SCHEMA_NAME = (
    "neurodecodekit.marc2_vr6_vr2_boundary_localization_result"
)
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_vr6_vr2_boundary_localization_contract.v0.json"
)
CONTRACT_SHA256 = "264c93989e8b2b7868c86c70945bc558699b0b132c3f5552661c6b8022efbae7"
GREEN_REGISTRATION_COMMIT = "d33eaf397a8f8444db4d7abd777bf2e9b3333e43"
GREEN_REGISTRATION_CI_RUN_ID = 31_984_475_999
GREEN_REGISTRATION_BASE_JOB_ID = 95_256_950_555
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_256_950_656
SUCCESS_ROUTES = ("MARC2VR8A-R1", "MARC2VR8A-R2", "MARC2VR8A-R3")
FAILURE_ROUTES = tuple(f"MARC2VR8A-F{index:02d}" for index in range(1, 5))
VR2_ROUTES = tuple(f"MARC2VR2-F{index:02d}" for index in range(1, 9))
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
EXPECTED_ROLES = frozenset(
    {
        "VR7P_wrapper_module",
        "VR7P_consumed_result",
        "VR7P_implementation_record",
        "VR6_adapter_module",
        "VR6_contract",
        "VR6_implementation_record",
        "VR2_validator_module",
        "VR2_contract",
        "VR1_source_repair_module",
        "selector_module",
        "exact_manifest_producer_module",
        "exact_central_directory_parser_module",
        "producer_public_result",
        "producer_implementation_record",
        "prior_VR5A_result",
        "prior_validation_coverage_result",
        "prior_schema_lineage_result",
    }
)
PYTHON_ROLES = frozenset(
    {
        "VR7P_wrapper_module",
        "VR6_adapter_module",
        "VR2_validator_module",
        "VR1_source_repair_module",
        "selector_module",
        "exact_manifest_producer_module",
        "exact_central_directory_parser_module",
    }
)


class Vr6Vr2BoundaryLocalizationRefusal(RuntimeError):
    """Fail closed with one frozen artifact-only refusal route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-VR8A refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
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
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[2], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, nested in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = nested
    return value


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _strict_json(payload: bytes) -> dict[str, Any]:
    value = json.loads(
        payload.decode("utf-8"),
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def _fixed_path(root: Path, relative_text: str) -> Path:
    relative = Path(relative_text)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", "..", ".codex_work"} for part in relative.parts)
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact path is not fixed"
        )
    current = root
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact path is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact path contains a symlink"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact is not a regular file"
        )
    return current


def _read_once(path: Path, *, cap: int) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact open failed"
        ) from exc
    chunks: list[bytes] = []
    total = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact type or size differs"
            )
        while True:
            chunk = os.read(descriptor, min(65_536, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise Vr6Vr2BoundaryLocalizationRefusal(
                    FAILURE_ROUTES[0], "artifact exceeds cap"
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
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact identity changed during read"
        )
    return b"".join(chunks)


def _load_contract(root: Path) -> tuple[dict[str, Any], bytes]:
    path = _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    payload = _read_once(path, cap=1024**2)
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "contract JSON differs"
        ) from exc
    proof = contract.get("upstream_closeout_green_proof", {})
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "frozen_artifact_only_contract_implementation_pending"
        or proof.get("commit")
        != "5fc1226b3b0a0246b17609d74d741ed20c24ab61"
        or proof.get("CI_run_id") != 31_983_540_816
        or proof.get("base_python_job_id") != 95_254_474_934
        or proof.get("optional_neuro_job_id") != 95_254_475_001
        or proof.get("both_required_jobs_green") is not True
        or proof.get("consumed_wrapper_route") != "MARC2VR7P-F07"
        or proof.get("preserved_VR6_route") != "MARC2VR6-F02"
        or proof.get("nested_VR2_route_available") is not False
        or proof.get("private_source_reinspection_or_rerun_allowed") is not False
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "contract identity or upstream proof differs"
        )
    authority = contract.get("authorization_state", {})
    allowed_true = {
        "artifact_only_implementation",
        "fixed_committed_artifact_reads",
    }
    if (
        not isinstance(authority, dict)
        or any(authority.get(name) is not True for name in allowed_true)
        or any(value for name, value in authority.items() if name not in allowed_true)
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact-only authority differs"
        )
    return contract, payload


def _bindings(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "fixed inputs differ"
        )
    bindings: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "role",
            "path",
            "bytes",
            "sha256",
        }:
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact binding fields differ"
            )
        role = row.get("role")
        if not isinstance(role, str) or role in bindings:
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact role differs"
            )
        bindings[role] = row
    if set(bindings) != EXPECTED_ROLES:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact role inventory differs"
        )
    return bindings


def _read_bound_artifact(
    root: Path, binding: Mapping[str, Any], *, cap: int
) -> tuple[bytes, dict[str, Any]]:
    path_text = binding["path"]
    expected_bytes = binding["bytes"]
    expected_sha256 = binding["sha256"]
    if (
        not isinstance(path_text, str)
        or isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or not isinstance(expected_sha256, str)
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact binding type differs"
        )
    payload = _read_once(_fixed_path(root, path_text), cap=cap)
    observed = _sha256_bytes(payload)
    if len(payload) != expected_bytes or observed != expected_sha256:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact size or SHA-256 differs"
        )
    return payload, {
        "role": binding["role"],
        "bytes": len(payload),
        "sha256": observed,
    }


def _function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    ]
    if len(matches) != 1:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[1], f"function anchor is unavailable: {name}"
        )
    return matches[0]


def _normalized_function(tree: ast.Module, name: str) -> str:
    return ast.unparse(_function(tree, name))


def _class(tree: ast.Module, name: str) -> ast.ClassDef:
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == name
    ]
    if len(matches) != 1:
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[1], f"class anchor is unavailable: {name}"
        )
    return matches[0]


def _require_fragments(text: str, fragments: Sequence[str], anchor: str) -> None:
    if any(fragment not in text for fragment in fragments):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[1], f"AST anchor differs: {anchor}"
        )


def _called_names(function: ast.FunctionDef) -> set[str]:
    return {
        ast.unparse(node.func)
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
    }


def inspect_route_relay(
    vr7_tree: ast.Module,
    vr6_tree: ast.Module,
    consumed_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Trace the outer and nested exception attributes across both wrappers."""

    vr6_class = ast.unparse(_class(vr6_tree, "DynamicLiveSelectionRefusal"))
    preserve = _normalized_function(vr6_tree, "_preserve_upstream_route")
    adapt = _normalized_function(vr6_tree, "adapt_dynamic_live_source")
    vr7_sequence = _normalized_function(vr7_tree, "_run_structural_sequence")
    vr7_main = _normalized_function(vr7_tree, "main")
    _require_fragments(
        vr6_class,
        (
            "self.route = route",
            "self.upstream_route = upstream_route",
            "upstream_route not in UPSTREAM_ROUTES",
        ),
        "VR6 exception attributes",
    )
    _require_fragments(
        preserve,
        (
            "REFUSAL_ROUTES[1]",
            "upstream_route=route",
            "route not in UPSTREAM_ROUTES",
        ),
        "VR6 route preservation",
    )
    _require_fragments(
        adapt,
        (
            "except vr2.LiveDomainEligibilityRefusal as exc",
            "raise _preserve_upstream_route(exc.route)",
        ),
        "VR6 catch",
    )
    _require_fragments(
        vr7_sequence,
        (
            "except dynamic.DynamicLiveSelectionRefusal as exc",
            "upstream = exc.route",
            "upstream_route=upstream",
        ),
        "VR7P catch",
    )
    _require_fragments(
        vr7_main,
        ("upstream_VR6_route", "exc.upstream_route"),
        "VR7P aggregate refusal",
    )
    nested_forwarded_by_vr7 = "upstream = exc.upstream_route" in vr7_sequence
    stop = consumed_result.get("stop_result", {})
    if (
        consumed_result.get("route") != "MARC2VR7P-F07"
        or consumed_result.get("upstream_VR6_route") != "MARC2VR6-F02"
        or stop.get("stage") != "VR6_upstream_VR2_validation"
        or stop.get("allowlisted_upstream_VR6_route_available") is not True
        or stop.get("nested_VR2_route_available") is not False
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "consumed route relay result differs"
        )
    return {
        "VR2_route_stored_by_VR6_exception": True,
        "VR6_outer_route": "MARC2VR6-F02",
        "VR6_nested_route_attribute": "upstream_route",
        "VR7P_reads_VR6_outer_route_attribute": "route",
        "VR7P_reads_VR6_nested_route_attribute": nested_forwarded_by_vr7,
        "VR7P_published_outer_VR6_route": True,
        "VR7P_published_nested_VR2_route": False,
        "nested_reason_or_value_preserved": False,
        "route_relay_loss_proven": not nested_forwarded_by_vr7,
    }


def inspect_call_path_and_reachability(
    vr7_tree: ast.Module,
    vr6_tree: ast.Module,
    vr2_tree: ast.Module,
) -> dict[str, Any]:
    """Classify VR2 routes on the exact preselection source-validation path."""

    execute = _normalized_function(vr7_tree, "execute_registered")
    sequence = _normalized_function(vr7_tree, "_run_structural_sequence")
    vr6_adapt = _normalized_function(vr6_tree, "adapt_dynamic_live_source")
    vr2_load = _normalized_function(vr2_tree, "load_registered_contract")
    vr2_validate = _normalized_function(vr2_tree, "validate_live_domain_source")
    _require_fragments(
        execute,
        (
            "vr2_contract=vr2.load_registered_contract(root)",
            "selector_contract=selector.load_registered_contract(root)",
        ),
        "preloaded contracts",
    )
    _require_fragments(
        sequence,
        (
            "source = _strict_json(source_payload",
            "dynamic.adapt_dynamic_live_source",
            "vr2_contract=vr2_contract",
            "selector_contract=selector_contract",
        ),
        "strict source to VR6",
    )
    _require_fragments(
        vr2_load,
        ("_verify_contract_mapping(contract)", "return contract"),
        "verified VR2 contract load",
    )
    _require_fragments(
        vr6_adapt,
        (
            "registered_vr2 = dict(vr2_contract or vr2.load_registered_contract())",
            "vr2.validate_live_domain_source",
            "repair._select_from_filtered",
        ),
        "VR6 validation before selection",
    )
    if vr6_adapt.index("vr2.validate_live_domain_source") > vr6_adapt.index(
        "repair._select_from_filtered"
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[1], "VR6 validation order differs"
        )
    _require_fragments(
        vr2_validate,
        (
            "_verify_contract_mapping(contract)",
            "_validate_live_envelope(source, contract)",
            "repair._group_source_rows(entries)",
            "if kinds != Counter",
            "if len(grouped) != domain['complete_source_run_bundles']",
            "_assert_classification_arithmetic",
            "_filter_and_validate_eligible",
        ),
        "VR2 source validation",
    )
    route_accounting = [
        {
            "route": "MARC2VR2-F01",
            "status": "excluded_prevalidated_unchanged_contract",
            "source_dependent": False,
        },
        {
            "route": "MARC2VR2-F02",
            "status": "candidate_pending_producer_lineage",
            "source_dependent": True,
        },
        {
            "route": "MARC2VR2-F03",
            "status": "compatible_path_companion_or_kind_class",
            "source_dependent": True,
        },
        {
            "route": "MARC2VR2-F04",
            "status": "compatible_bundle_or_taxonomy_class",
            "source_dependent": True,
        },
        {
            "route": "MARC2VR2-F05",
            "status": "excluded_prevalidated_unchanged_contract",
            "source_dependent": False,
        },
        {
            "route": "MARC2VR2-F06",
            "status": "excluded_selection_not_reached",
            "source_dependent": False,
        },
        {
            "route": "MARC2VR2-F07",
            "status": "excluded_prevalidated_surface_and_strict_JSON",
            "source_dependent": False,
        },
        {
            "route": "MARC2VR2-F08",
            "status": "excluded_qualification_resource_path_not_called",
            "source_dependent": False,
        },
    ]
    return {
        "VR2_contract_loaded_and_verified_before_private_sequence": True,
        "same_VR2_contract_passed_unchanged_to_validation": True,
        "strict_JSON_preceded_VR6": True,
        "VR2_full_source_validation_preceded_dynamic_selection": True,
        "VR2_selection_or_resource_stage_reached": False,
        "routes_accounted_for": route_accounting,
        "route_count": len(route_accounting),
        "pre_lineage_source_candidates": [
            "MARC2VR2-F02",
            "MARC2VR2-F03",
            "MARC2VR2-F04",
        ],
    }


def inspect_producer_envelope(
    producer_tree: ast.Module,
    parser_tree: ast.Module,
    vr2_tree: ast.Module,
    contract: Mapping[str, Any],
    producer_result: Mapping[str, Any],
    producer_implementation: Mapping[str, Any],
    vr2_contract: Mapping[str, Any],
    vr7_implementation: Mapping[str, Any],
    vr7_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Prove the exact retained source satisfies the VR2 envelope predicate."""

    producer = _normalized_function(producer_tree, "_private_manifest")
    parser = _normalized_function(parser_tree, "parse_central_directory")
    envelope = _normalized_function(vr2_tree, "_validate_live_envelope")
    _require_fragments(
        producer,
        (
            "manifest = copy.deepcopy(dict(run.inventory.private_manifest))",
            "neurodecodekit.marc1_central_directory_private_manifest",
            "live_archive_private_central_directory_metadata_only",
            "'provider': 'generated_fixture' if generated else 'Figshare'",
            "manifest['transport_body_sha256'] = dict(run.transport.get('response_body_sha256', {}))",
        ),
        "exact manifest producer",
    )
    _require_fragments(
        parser,
        (
            "'schema_name': PRIVATE_SCHEMA_NAME",
            "'schema_version': SCHEMA_VERSION",
            "'proof_posture': 'generated_private_fixture_only'",
            "'entries': records",
        ),
        "parser private manifest",
    )
    _require_fragments(
        envelope,
        (
            "set(source) != SOURCE_TOP_LEVEL_FIELDS",
            "source.get('schema_name') != domain['schema_name']",
            "source.get('source_identity') != domain['source_identity']",
            "source.get('transport_body_sha256') != domain['transport_body_sha256']",
            "len(entries) != domain['inventory_rows']",
        ),
        "VR2 envelope",
    )
    facts = contract["registered_facts"]
    domain = vr2_contract.get("generated_live_source_domain", {})
    archive = producer_result.get("archive_summary", {})
    source = producer_result.get("source", {})
    transport = producer_result.get("transport_summary", {}).get(
        "response_body_sha256", {}
    )
    producer_surface = producer_implementation.get("implementation_surface", {})
    domain_source = domain.get("source_identity", {})
    public_source_projection = {
        key: source.get(key) for key in domain_source
    } if isinstance(domain_source, dict) else {}
    private_identity = vr7_implementation.get("registered_identities", {}).get(
        "private_source", {}
    )
    private_execution = vr7_result.get("private_execution", {})
    expected_top = sorted(facts["producer_manifest_top_level_fields"])
    expected_rows = sorted(facts["producer_row_fields"])
    if (
        producer_surface.get("module_SHA256")
        != "f25464be139a0f4dad813f255be6d91eb803f35a50b045baea4aa7b27e5549d5"
        or producer_surface.get("green_parser_imported_without_modification")
        is not True
        or sorted(facts["VR2_source_top_level_fields"]) != expected_top
        or sorted(facts["selector_row_fields"]) != expected_rows
        or sorted(facts["producer_transport_keys"])
        != sorted(facts["VR2_transport_keys"])
        or public_source_projection != domain_source
        or transport != domain.get("transport_body_sha256")
        or archive.get("entry_count") != domain.get("inventory_rows")
        or archive.get("regular_file_entries") != domain.get("regular_file_rows")
        or archive.get("directory_entries") != domain.get("directory_rows")
        or archive.get("private_manifest_sha256")
        != facts["private_source_sha256"]
        or private_identity.get("sha256") != facts["private_source_sha256"]
        or private_identity.get("bytes") != facts["private_source_bytes"]
        or private_execution.get("private_structural_registered_SHA256_matched")
        is not True
        or private_execution.get("strict_JSON_parses") != 1
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[2], "producer-to-VR2 envelope lineage differs"
        )
    return {
        "producer_module_hash_matches_green_implementation": True,
        "parser_module_imported_without_modification": True,
        "retained_source_hash_equals_producer_private_manifest_hash": True,
        "retained_source_size_and_hash_passed_before_VR6": True,
        "producer_and_VR2_top_level_fields_match": True,
        "producer_and_selector_row_fields_match": True,
        "producer_and_VR2_schema_version_match": True,
        "producer_and_VR2_proof_posture_match": True,
        "producer_and_VR2_source_identity_match": True,
        "producer_and_VR2_transport_keys_and_digests_match": True,
        "producer_and_VR2_inventory_row_count_match": True,
        "VR2_F02_envelope_route_excluded": True,
        "private_source_content_opened_by_audit": False,
        "private_field_value_observed_by_audit": False,
    }


def inspect_parser_and_fixture_boundary(
    parser_tree: ast.Module,
    selector_tree: ast.Module,
    repair_tree: ast.Module,
    vr2_tree: ast.Module,
    producer_result: Mapping[str, Any],
    producer_implementation: Mapping[str, Any],
) -> dict[str, Any]:
    """Separate parser guarantees from source-dependent grammar and fixtures."""

    parser = _normalized_function(parser_tree, "parse_central_directory")
    validate_entry = _normalized_function(selector_tree, "_validate_entry")
    build_selector_node = _function(selector_tree, "build_generated_manifest")
    build_repair_node = _function(repair_tree, "build_generated_full_source")
    build_vr2_node = _function(vr2_tree, "build_generated_live_source")
    build_repair = ast.unparse(build_repair_node)
    build_vr2 = ast.unparse(build_vr2_node)
    _require_fragments(
        parser,
        (
            "if name in names",
            "_validate_member_name(name)",
            "if method not in {0, 8}",
            "'entry_kind': kind",
            "'member_name': name",
        ),
        "central-directory parser guarantees",
    )
    _require_fragments(
        validate_entry,
        (
            "set(row) != ENTRY_FIELDS",
            "match = _core_match(name)",
            "Freewill BIDS identity differs",
            "match.group('task') != 'freewill'",
        ),
        "selector path grammar",
    )
    _require_fragments(
        build_repair,
        ("selector.build_generated_manifest", "Freewill_generated/generated_aux/"),
        "repair fixture lineage",
    )
    _require_fragments(
        build_vr2,
        ("repair.build_generated_full_source", "_rename_all_ineligible_keys"),
        "VR2 fixture lineage",
    )
    generated_call_targets = set().union(
        _called_names(build_selector_node),
        _called_names(build_repair_node),
        _called_names(build_vr2_node),
    )
    exact_producer_called = bool(
        generated_call_targets
        & {
            "marc1_central_directory_live._private_manifest",
            "marc1_central_directory_audit.parse_central_directory",
            "producer._private_manifest",
            "audit.parse_central_directory",
        }
    )
    archive = producer_result.get("archive_summary", {})
    generated = producer_implementation.get("generated_qualification", {})
    if (
        archive.get("regular_file_entries") != 1025
        or archive.get("directory_entries") != 202
        or generated.get("entry_count") != 18
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[2], "parser or fixture aggregate differs"
        )
    return {
        "parser_guarantees": [
            "exact row field emission",
            "unique full member paths",
            "normalized safe member paths",
            "regular versus directory type",
            "stored or deflated compression",
            "nonnegative parsed sizes and offsets",
        ],
        "VR2_F03_source_dependent_checks": [
            "suffix-bearing path matches frozen Freewill BIDS grammar",
            "task token equals lowercase freewill",
            "logical run companion identities do not collide",
            "every matched logical run has four required companions",
            "entry-kind aggregate remains exact after selector validation",
        ],
        "VR2_F04_source_dependent_checks": [
            "exactly 238 complete logical bundles",
            "every participant belongs to the frozen taxonomy",
            "classification equals 195 eligible plus 43 valid ineligible",
            "eligible participant-session counts equal the published map",
        ],
        "VR2_generated_builder_starts_from_selector_fixture": True,
        "VR2_generated_builder_calls_exact_parser_or_producer": exact_producer_called,
        "selector_generated_root_vocabulary": "Freewill_generated",
        "exact_producer_generated_fixture_rows": generated["entry_count"],
        "VR2_generated_success_rows": 1227,
        "full_scale_producer_to_VR2_fixture_exists": False,
        "producer_integration_coverage_gap_proven": not exact_producer_called,
    }


def classify_result(*, relay_loss: bool, F02_excluded: bool) -> str:
    """Apply the frozen VR8A route classifier."""

    if relay_loss and F02_excluded:
        return SUCCESS_ROUTES[0]
    if relay_loss:
        return SUCCESS_ROUTES[1]
    return SUCCESS_ROUTES[2]


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[3], "one-thread environment is not explicit"
        )


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _walk_public(value: Any) -> None:
    forbidden_keys = {
        "crc32",
        "decoded_text",
        "labels",
        "member_name",
        "participant_id",
        "predictions",
        "private_path",
        "signal",
        "subject_id",
        "target",
        "targets",
    }
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in forbidden_keys:
                raise Vr6Vr2BoundaryLocalizationRefusal(
                    FAILURE_ROUTES[2], "forbidden private or scientific field"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str) and (
        ".codex_work" in value or value.startswith("sub-")
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[2], "private path or identity leaked"
        )


def audit_repository(
    *,
    repo_root: str | Path,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the fixed committed-artifact MARC2-VR8A audit."""

    _validate_thread_environment()
    started = clock()
    root = Path(repo_root).resolve()
    contract, contract_payload = _load_contract(root)
    caps = contract["resource_caps"]
    bindings = _bindings(contract)

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
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[3], "total input cap exceeded"
        )

    trees: dict[str, ast.Module] = {}
    values: dict[str, dict[str, Any]] = {}
    for role, payload in payloads.items():
        try:
            if role in PYTHON_ROLES:
                trees[role] = ast.parse(payload.decode("utf-8"))
            else:
                values[role] = _strict_json(payload)
        except (SyntaxError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise Vr6Vr2BoundaryLocalizationRefusal(
                FAILURE_ROUTES[0], f"artifact parse failed: {role}"
            ) from exc

    consumed = values["VR7P_consumed_result"]
    private_execution = consumed.get("private_execution", {})
    if (
        consumed.get("route") != "MARC2VR7P-F07"
        or consumed.get("upstream_VR6_route") != "MARC2VR6-F02"
        or private_execution.get("VR6_adapter_calls") != 1
        or private_execution.get("VR2_validation_calls") != 1
        or private_execution.get("VR2_validation_successes") != 0
        or values["prior_VR5A_result"].get("route") != "MARC2VR5-R2"
        or values["prior_validation_coverage_result"].get("route")
        != "MARC2VL-R2"
        or values["prior_schema_lineage_result"].get("route") != "MARC2SL-R2"
        or values["VR6_implementation_record"].get("measured_qualification", {}).get(
            "route"
        )
        != "MARC2VR6-G1"
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[0], "upstream aggregate evidence differs"
        )

    relay = inspect_route_relay(
        trees["VR7P_wrapper_module"],
        trees["VR6_adapter_module"],
        consumed,
    )
    reachability = inspect_call_path_and_reachability(
        trees["VR7P_wrapper_module"],
        trees["VR6_adapter_module"],
        trees["VR2_validator_module"],
    )
    envelope = inspect_producer_envelope(
        trees["exact_manifest_producer_module"],
        trees["exact_central_directory_parser_module"],
        trees["VR2_validator_module"],
        contract,
        values["producer_public_result"],
        values["producer_implementation_record"],
        values["VR2_contract"],
        values["VR7P_implementation_record"],
        consumed,
    )
    fixture = inspect_parser_and_fixture_boundary(
        trees["exact_central_directory_parser_module"],
        trees["selector_module"],
        trees["VR1_source_repair_module"],
        trees["VR2_validator_module"],
        values["producer_public_result"],
        values["producer_implementation_record"],
    )
    route = classify_result(
        relay_loss=relay["route_relay_loss_proven"],
        F02_excluded=envelope["VR2_F02_envelope_route_excluded"],
    )

    runtime = clock() - started
    peak_rss = int(rss_reader())
    if (
        not isinstance(runtime, (int, float))
        or runtime < 0
        or runtime > caps["runtime_seconds"]
        or peak_rss < 0
        or peak_rss >= caps["peak_RSS_bytes"]
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[3], "runtime or RSS cap exceeded"
        )

    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_artifact_only_VR6_to_VR2_boundary_localization",
        "proof_posture": (
            "fixed_committed_code_and_aggregate_results_only_no_private_or_scientific_value"
        ),
        "green_registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
        },
        "upstream_consumed_result": {
            "wrapper_route": consumed["route"],
            "upstream_VR6_route": consumed["upstream_VR6_route"],
            "VR6_adapter_calls": private_execution["VR6_adapter_calls"],
            "VR2_validation_calls": private_execution["VR2_validation_calls"],
            "VR2_validation_successes": private_execution[
                "VR2_validation_successes"
            ],
            "nested_VR2_route_available": False,
            "private_reinspection_allowed": False,
        },
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "sha256": CONTRACT_SHA256,
            "fixed_input_artifacts": len(measured_inputs),
            "private_or_Git_ignored_input_artifacts": 0,
        },
        "route_relay": relay,
        "call_path_and_reachability": reachability,
        "producer_envelope": envelope,
        "parser_and_fixture_boundary": fixture,
        "final_compatible_VR2_classes": [
            {
                "route": "MARC2VR2-F03",
                "class": "BIDS path run-companion or structural grouping",
            },
            {
                "route": "MARC2VR2-F04",
                "class": "bundle participant session or taxonomy arithmetic",
            },
        ],
        "root_cause": {
            "class": (
                "nested_route_dropped_at_VR7P_boundary_plus_missing_full_scale_"
                "producer_to_VR2_fixture"
            ),
            "why_the_nested_route_is_unavailable": (
                "VR6 stores the VR2 code in upstream_route but VR7P forwards only "
                "the VR6 outer route attribute"
            ),
            "why_F02_is_excluded": (
                "the retained source hash equals the exact producer manifest hash "
                "and every VR2 envelope field digest and count matches"
            ),
            "why_generated_success_did_not_cover_the_remaining_boundary": (
                "VR2 starts from a selector-authored full-scale manifest and never "
                "traverses the exact central-directory parser or producer"
            ),
            "exact_private_F03_or_F04_predicate_proven": False,
            "private_source_malformed_inferred": False,
            "data_or_scientific_failure": False,
        },
        "prospective_repair": contract["prospective_repair"],
        "measurements": {
            "input_artifact_count": len(measured_inputs) + 1,
            "input_bytes": input_bytes,
            "Python_AST_parses": len(trees),
            "strict_JSON_parses": len(values) + 1,
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
        "access_counters": {
            "committed_contract_and_artifact_reads": len(measured_inputs) + 1,
            "private_or_Git_ignored_path_operations": 0,
            "consumed_marker_certificate_output_or_source_operations": 0,
            "archive_local_header_or_member_payload_reads": 0,
            "signal_event_target_label_quality_channel_geometry_or_human_text_reads": 0,
            "derivative_cache_feature_split_or_neurotoken_operations": 0,
            "training_inference_prediction_freeze_delivery_or_score_operations": 0,
            "network_download_provider_or_language_model_operations": 0,
            "stream_device_or_hardware_operations": 0,
            "consumed_executor_patch_retry_rerun_resume_or_repair_operations": 0,
            "MARC2_FW2_or_CIL1_operations": 0,
            "scientific_claim_upgrades": 0,
            "operations_on_other_projects": 0,
        },
        "acceptance_gates": {
            "green_registration_preceded_implementation": True,
            "all_fixed_artifact_sizes_and_hashes_passed": True,
            "VR6_nested_route_storage_proven": relay[
                "VR2_route_stored_by_VR6_exception"
            ],
            "VR7P_nested_route_relay_loss_proven": relay[
                "route_relay_loss_proven"
            ],
            "all_eight_VR2_routes_classified": reachability["route_count"] == 8,
            "VR2_F02_excluded_by_exact_producer_lineage": envelope[
                "VR2_F02_envelope_route_excluded"
            ],
            "F03_and_F04_preserved_as_unresolved_classes": True,
            "producer_integration_fixture_gap_proven": fixture[
                "producer_integration_coverage_gap_proven"
            ],
            "exact_private_predicate_left_unresolved": True,
            "one_thread_runtime_RSS_input_output_and_retention_caps": True,
            "zero_private_archive_neural_target_model_score_network_operations": True,
        },
        "route": route,
        "warnings": [
            "The consumed nested VR2 route remains unavailable; this audit narrows compatible classes only.",
            "F03 versus F04 cannot be selected without a new diagnostic relay and separately authorized source read.",
            "Generated VR2 success did not traverse the exact full-scale producer path.",
            "No private source ignored path archive member neural value target model prediction or score was accessed.",
        ],
        "unavailable_fields": [
            "observed nested VR2 route reason predicate and value",
            "private member paths participant session run and companion identities",
            "real selected cohort reservation bytes and selection hash",
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
        or len(payload) > caps["aggregate_output_bytes"]
    ):
        raise Vr6Vr2BoundaryLocalizationRefusal(
            FAILURE_ROUTES[3], "aggregate output cap differs"
        )
    _walk_public(report)
    return report


def plan(*, repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    contract, _payload = _load_contract(root)
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": contract["lane_id"],
        "status": contract["status"],
        "fixed_input_count": len(contract["fixed_inputs"]),
        "fixed_input_bytes": contract["registered_facts"]["fixed_input_bytes"],
        "private_or_Git_ignored_bytes": contract["resource_caps"][
            "private_or_Git_ignored_bytes"
        ],
        "network_bytes": contract["resource_caps"]["network_bytes"],
        "private_access_authorized": False,
        "MARC2_FW2_authorized": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=(
            "python -m neurodecodekit.datasets."
            "marc2_vr6_vr2_boundary_localization"
        ),
        description=(
            "Localize the VR6-to-VR2 refusal boundary from fixed committed "
            "artifacts without private data access."
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
    except Vr6Vr2BoundaryLocalizationRefusal as exc:
        print(f"{exc.route}: {exc.safe_reason}", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(value).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
