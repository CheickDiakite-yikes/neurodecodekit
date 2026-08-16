"""Artifact-only localization of the consumed MARC2 VR2 refusal boundary."""

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
LANE_ID = "MARC2-VR5A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_vr2_refusal_localization_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_vr2_refusal_localization_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_vr2_refusal_localization_contract.v0.json"
)
CONTRACT_SHA256 = "268545b9bf1d517edd9b25960f4148f3c5ce17beac9c25ce6a9a8ea1f12c7fea"
GREEN_REGISTRATION_COMMIT = "926e1ba1189c86f4f7bde8019c64395c086c9327"
GREEN_REGISTRATION_CI_RUN_ID = 31_972_332_778
GREEN_REGISTRATION_BASE_JOB_ID = 95_226_555_204
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_226_555_153
SUCCESS_ROUTES = ("MARC2VR5-R1", "MARC2VR5-R2", "MARC2VR5-R3")
FAILURE_ROUTES = tuple(f"MARC2VR5-F{index:02d}" for index in range(1, 5))
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
EXPECTED_ROLES = frozenset(
    {
        "VR2_adapter_module",
        "VR2_contract",
        "VR2_generated_result",
        "VR1_repair_module",
        "selector_module",
        "exact_producer_module",
        "producer_public_result",
        "VR4P_executor_module",
        "VR4P_consumed_result",
        "prior_coverage_result",
        "prior_schema_lineage_result",
    }
)
PYTHON_ROLES = frozenset(
    {
        "VR2_adapter_module",
        "VR1_repair_module",
        "selector_module",
        "exact_producer_module",
        "VR4P_executor_module",
    }
)
NESTED_ROUTES = tuple(f"MARC2VR2-F{index:02d}" for index in range(1, 9))


class Vr2RefusalLocalizationRefusal(RuntimeError):
    """Fail closed with one frozen artifact-only route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in FAILURE_ROUTES:
            raise ValueError("unknown MARC2-VR5A refusal route")
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
        raise Vr2RefusalLocalizationRefusal(
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
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact path is not fixed"
        )
    current = root
    for part in relative.parts:
        current = current / part
        try:
            info = current.lstat()
        except OSError as exc:
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact path is unavailable"
            ) from exc
        if stat.S_ISLNK(info.st_mode):
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact path contains a symlink"
            )
    if not stat.S_ISREG(current.lstat().st_mode):
        raise Vr2RefusalLocalizationRefusal(
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
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact open failed"
        ) from exc
    chunks: list[bytes] = []
    total = 0
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact type or size differs"
            )
        while True:
            chunk = os.read(descriptor, min(65_536, cap + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > cap:
                raise Vr2RefusalLocalizationRefusal(
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
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact identity changed during read"
        )
    return b"".join(chunks)


def _load_contract(root: Path) -> tuple[dict[str, Any], bytes]:
    path = _fixed_path(root, CONTRACT_RELATIVE_PATH.as_posix())
    payload = _read_once(path, cap=1024**2)
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = _strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise Vr2RefusalLocalizationRefusal(
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
        != "0618fc3c62d5dfa308547862209a55c6ba85ed90"
        or proof.get("CI_run_id") != 31_971_716_473
        or proof.get("base_python_job_id") != 95_225_078_285
        or proof.get("optional_neuro_job_id") != 95_225_078_127
        or proof.get("both_required_jobs_green") is not True
        or proof.get("underlying_VR2_route_available") is not False
    ):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "contract identity or green proof differs"
        )
    authority = contract.get("authorization_state", {})
    allowed_true = {
        "generated_or_artifact_only_implementation",
        "committed_artifact_reads",
    }
    if (
        not isinstance(authority, dict)
        or any(authority.get(name) is not True for name in allowed_true)
        or any(value for name, value in authority.items() if name not in allowed_true)
    ):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact-only authority differs"
        )
    return contract, payload


def _bindings(contract: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = contract.get("fixed_inputs")
    if not isinstance(rows, list):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "fixed inputs differ"
        )
    bindings: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"role", "path", "sha256"}:
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact binding fields differ"
            )
        role = row.get("role")
        if not isinstance(role, str) or role in bindings:
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], "artifact role differs"
            )
        bindings[role] = row
    if set(bindings) != EXPECTED_ROLES:
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact role inventory differs"
        )
    return bindings


def _read_bound_artifact(
    root: Path, binding: Mapping[str, Any], *, cap: int
) -> tuple[bytes, dict[str, Any]]:
    path_text = binding["path"]
    expected = binding["sha256"]
    if not isinstance(path_text, str) or not isinstance(expected, str):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact binding type differs"
        )
    payload = _read_once(_fixed_path(root, path_text), cap=cap)
    observed = _sha256_bytes(payload)
    if observed != expected:
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "artifact SHA-256 differs"
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
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[1], f"function anchor is unavailable: {name}"
        )
    return matches[0]


def _normalized_function(tree: ast.Module, name: str) -> str:
    return ast.unparse(_function(tree, name))


def _require_fragments(text: str, fragments: Sequence[str], anchor: str) -> None:
    if any(fragment not in text for fragment in fragments):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[1], f"AST anchor differs: {anchor}"
        )


def inspect_wrapper_route_collapse(tree: ast.Module) -> dict[str, Any]:
    """Verify that VR4P discards the nested aggregate-safe VR2 route."""

    function = _function(tree, "_run_structural_sequence")
    handlers = [
        handler
        for node in ast.walk(function)
        if isinstance(node, ast.Try)
        for handler in node.handlers
        if ast.unparse(handler.type) == "adapter.LiveDomainEligibilityRefusal"
    ]
    if len(handlers) != 1:
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[1], "VR2 catch anchor differs"
        )
    handler = handlers[0]
    normalized = ast.unparse(handler)
    _require_fragments(
        normalized,
        (
            "as exc",
            "MachineStableRecoveryRefusal",
            "REFUSAL_ROUTES[7]",
            "VR2 structural adapter refused",
        ),
        "VR2 catch",
    )
    nested_route_preserved = "exc.route" in normalized
    nested_reason_preserved = "exc.reason" in normalized or "str(exc)" in normalized
    return {
        "VR2_exception_catches": 1,
        "outer_route": "MARC2MSP-F07",
        "nested_route_preserved": nested_route_preserved,
        "nested_reason_preserved": nested_reason_preserved,
        "diagnostic_classes_before_catch": len(NESTED_ROUTES),
        "diagnostic_classes_after_catch": 1,
        "diagnostic_class_reduction": len(NESTED_ROUTES) - 1,
        "collapse_proven": not nested_route_preserved,
    }


def inspect_selection_contract(
    vr2_tree: ast.Module,
    repair_tree: ast.Module,
    selector_tree: ast.Module,
    vr2_contract: Mapping[str, Any],
    vr2_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Inspect generated-result requirements applied to a live selection."""

    select_filtered = _normalized_function(vr2_tree, "_select_filtered")
    assert_selection = _normalized_function(repair_tree, "_assert_selection")
    producer = _normalized_function(repair_tree, "_select_from_filtered")
    candidate_rows = _normalized_function(selector_tree, "_candidate_rows")
    _require_fragments(
        select_filtered,
        (
            "repair._select_from_filtered",
            "repair._assert_selection",
            "REFUSAL_ROUTES[5]",
        ),
        "VR2 selection integration",
    )
    expected_fields = (
        "selected_subjects",
        "selected_run_bundles",
        "selected_core_members",
        "fit_run_bundles",
        "heldout_run_bundles",
        "fit_heldout_overlap",
        "selected_reservation_bytes",
        "reservation_cap_bytes",
        "selection_identity_sha256",
    )
    _require_fragments(
        assert_selection,
        (
            "expected = contract['expected_selection']",
            "observed[key] != expected[key]",
            *tuple(repr(field) for field in expected_fields),
        ),
        "exact generated selection assertion",
    )
    _require_fragments(
        producer,
        (
            "'generated_fixture_selection_only_no_scientific_value'",
            "'generated_inventory_sha256': source_sha256",
        ),
        "generated selection semantics",
    )
    _require_fragments(
        candidate_rows,
        ("'source_id': 'freewill_23_generated'",),
        "generated row source identity",
    )
    expected = vr2_contract.get("expected_selection")
    if not isinstance(expected, dict) or set(expected_fields) - set(expected):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "VR2 expected selection differs"
        )
    selection_summary = vr2_result.get("selection_summary", {})
    if any(selection_summary.get(field) != expected[field] for field in expected_fields):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "generated selection result differs"
        )
    profiles = vr2_result.get("profile_summary")
    replay = vr2_result.get("replay_summary", {})
    if (
        not isinstance(profiles, list)
        or len(profiles) != 4
        or replay.get("success_paths") != 8
        or replay.get("all_selection_identities_equal") is not True
    ):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "generated profile replay differs"
        )
    return {
        "exact_generated_fields_required_of_every_selection": list(expected_fields),
        "exact_generated_field_count": len(expected_fields),
        "generated_selected_subjects": expected["selected_subjects"],
        "generated_selected_reservation_bytes": expected[
            "selected_reservation_bytes"
        ],
        "generated_selection_identity_sha256": expected[
            "selection_identity_sha256"
        ],
        "generated_profiles": len(profiles),
        "generated_success_paths": replay["success_paths"],
        "all_generated_selection_identities_equal": True,
        "dynamic_live_subject_count_accepted": False,
        "dynamic_live_reservation_bytes_accepted": False,
        "measured_live_selection_hash_accepted_before_freeze": False,
        "live_selection_overconstraint_proven": True,
        "hardcoded_row_source_id": "freewill_23_generated",
        "hardcoded_private_proof_posture": (
            "generated_fixture_selection_only_no_scientific_value"
        ),
        "hardcoded_source_hash_key": "generated_inventory_sha256",
        "live_source_semantics_preserved": False,
    }


def inspect_call_path(
    vr2_tree: ast.Module,
    wrapper_tree: ast.Module,
) -> dict[str, Any]:
    """Anchor the strict-JSON-to-VR2 call path and route relevance."""

    execute = _normalized_function(wrapper_tree, "execute_registered")
    sequence = _normalized_function(wrapper_tree, "_run_structural_sequence")
    adapt = _normalized_function(vr2_tree, "adapt_live_domain_source")
    validate = _normalized_function(vr2_tree, "validate_live_domain_source")
    _require_fragments(
        execute,
        (
            "adapter_contract = adapter.load_registered_contract(root)",
            "selector_contract = selector.load_registered_contract(root)",
            "adapter_contract=adapter_contract",
            "selector_contract=selector_contract",
        ),
        "preloaded contracts",
    )
    _require_fragments(
        sequence,
        (
            "source = _strict_json(source_payload, route=REFUSAL_ROUTES[7])",
            "adapter.adapt_live_domain_source",
            "contract=adapter_contract",
            "selector_contract=selector_contract",
        ),
        "strict JSON to VR2",
    )
    _require_fragments(
        adapt,
        (
            "validate_live_domain_source",
            "_select_filtered",
            "contract=registered",
        ),
        "VR2 public call path",
    )
    _require_fragments(
        validate,
        (
            "_verify_contract_mapping(contract)",
            "_validate_live_envelope(source, contract)",
            "repair._group_source_rows(entries)",
            "_assert_classification_arithmetic",
            "_filter_and_validate_eligible",
            "_canonical_source_bytes(source)",
        ),
        "VR2 validation path",
    )
    return {
        "contracts_loaded_before_private_sequence": True,
        "source_strict_JSON_before_VR2": True,
        "same_loaded_contracts_passed_into_VR2": True,
        "VR2_validation_precedes_selection": True,
        "route_accounting": [
            {
                "route": "MARC2VR2-F01",
                "class": "contract_or_green_proof",
                "context": "same contract already loaded successfully before source open",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F02",
                "class": "source_envelope_identity_transport_or_row_count",
                "context": "producer lineage is aggregate-consistent but nested route was not retained",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F03",
                "class": "row_path_ZIP_BIDS_or_companion_structure",
                "context": "unresolved without forbidden private reinspection",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F04",
                "class": "taxonomy_classification_or_238_195_43_arithmetic",
                "context": "unresolved without forbidden private reinspection",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F05",
                "class": "contract_live_acceptance_policy",
                "context": "same contract already loaded successfully before source open",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F06",
                "class": "rank_split_reservation_or_selection",
                "context": "observed route unknown; independent generated-result overconstraint proven",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F07",
                "class": "canonical_aggregate_or_surface_boundary",
                "context": "strict JSON is canonicalizable; nested route remains unavailable",
                "observed_private_route": False,
            },
            {
                "route": "MARC2VR2-F08",
                "class": "qualification_resource_boundary",
                "context": "not called by adapt_live_domain_source",
                "observed_private_route": False,
            },
        ],
        "nested_routes_accounted_for": len(NESTED_ROUTES),
        "observed_nested_route_available": False,
    }


def inspect_producer_lineage(
    producer_tree: ast.Module,
    producer_result: Mapping[str, Any],
    vr2_contract: Mapping[str, Any],
    consumed_result: Mapping[str, Any],
) -> dict[str, Any]:
    """Check committed producer-envelope facts without reading the manifest."""

    producer = _normalized_function(producer_tree, "_private_manifest")
    _require_fragments(
        producer,
        (
            "neurodecodekit.marc1_central_directory_private_manifest",
            "live_archive_private_central_directory_metadata_only",
            "'provider': 'generated_fixture' if generated else 'Figshare'",
            "'transport_body_sha256'",
            "response_body_sha256",
        ),
        "exact producer envelope",
    )
    domain = vr2_contract.get("generated_live_source_domain", {})
    archive = producer_result.get("archive_summary", {})
    transport = producer_result.get("transport_summary", {}).get(
        "response_body_sha256", {}
    )
    source = producer_result.get("source", {})
    private_execution = consumed_result.get("private_execution", {})
    if (
        source.get("provider") != domain.get("source_identity", {}).get("provider")
        or source.get("record_id")
        != domain.get("source_identity", {}).get("record_id")
        or source.get("file_id") != domain.get("source_identity", {}).get("file_id")
        or source.get("registered_MD5")
        != domain.get("source_identity", {}).get("registered_MD5")
        or transport != domain.get("transport_body_sha256")
        or archive.get("entry_count") != domain.get("inventory_rows")
        or archive.get("regular_file_entries") != domain.get("regular_file_rows")
        or archive.get("directory_entries") != domain.get("directory_rows")
        or private_execution.get("private_structural_registered_SHA256_matched")
        is not True
        or private_execution.get("strict_JSON_parses") != 1
    ):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "producer or consumed aggregate lineage differs"
        )
    return {
        "producer_schema_and_proof_posture_anchored": True,
        "producer_source_identity_matches_VR2_contract": True,
        "producer_transport_hashes_match_VR2_contract": True,
        "producer_row_and_kind_counts_match_VR2_contract": True,
        "consumed_source_registered_hash_passed": True,
        "consumed_source_strict_JSON_passed": True,
        "F02_lineage_consistent": True,
        "F02_formally_identified_or_excluded_as_observed_route": False,
        "private_field_or_row_inspected": False,
    }


def classify_result(
    *, route_collapsed: bool, live_selection_overconstrained: bool
) -> str:
    """Apply the frozen three-route artifact-only classifier."""

    if route_collapsed and live_selection_overconstrained:
        return SUCCESS_ROUTES[1]
    if route_collapsed or live_selection_overconstrained:
        return SUCCESS_ROUTES[2]
    return SUCCESS_ROUTES[0]


def _validate_thread_environment() -> None:
    if any(os.environ.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise Vr2RefusalLocalizationRefusal(
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
        "predictions",
        "private_path",
        "signal",
        "target",
        "targets",
    }
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in forbidden_keys:
                raise Vr2RefusalLocalizationRefusal(
                    FAILURE_ROUTES[2], "forbidden private or scientific field"
                )
            _walk_public(nested)
    elif isinstance(value, list):
        for nested in value:
            _walk_public(nested)
    elif isinstance(value, str) and ".codex_work" in value:
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[2], "private path leaked into aggregate"
        )


def audit_repository(
    *,
    repo_root: str | Path,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
) -> dict[str, Any]:
    """Run the fixed committed-artifact MARC2-VR5A audit."""

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
        raise Vr2RefusalLocalizationRefusal(
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
            raise Vr2RefusalLocalizationRefusal(
                FAILURE_ROUTES[0], f"artifact parse failed: {role}"
            ) from exc

    consumed = values["VR4P_consumed_result"]
    if (
        consumed.get("route") != "MARC2MSP-F07"
        or consumed.get("stop_result", {}).get("stage")
        != "VR2_structural_adapter"
        or consumed.get("stop_result", {}).get("underlying_adapter_route_available")
        is not False
        or consumed.get("private_execution", {}).get("VR2_adapter_calls") != 1
        or consumed.get("private_execution", {}).get("VR2_adapter_successes") != 0
        or values["prior_coverage_result"].get("route") != "MARC2VL-R2"
        or values["prior_schema_lineage_result"].get("route") != "MARC2SL-R2"
        or values["VR2_generated_result"].get("route") != "MARC2VR2-G1"
    ):
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[0], "upstream aggregate result differs"
        )

    collapse = inspect_wrapper_route_collapse(trees["VR4P_executor_module"])
    call_path = inspect_call_path(
        trees["VR2_adapter_module"], trees["VR4P_executor_module"]
    )
    selection = inspect_selection_contract(
        trees["VR2_adapter_module"],
        trees["VR1_repair_module"],
        trees["selector_module"],
        values["VR2_contract"],
        values["VR2_generated_result"],
    )
    lineage = inspect_producer_lineage(
        trees["exact_producer_module"],
        values["producer_public_result"],
        values["VR2_contract"],
        consumed,
    )
    route = classify_result(
        route_collapsed=collapse["collapse_proven"],
        live_selection_overconstrained=selection[
            "live_selection_overconstraint_proven"
        ],
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
        raise Vr2RefusalLocalizationRefusal(
            FAILURE_ROUTES[3], "runtime or RSS cap exceeded"
        )

    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_artifact_only_VR2_refusal_localization",
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
            "route": consumed["route"],
            "stage": consumed["stop_result"]["stage"],
            "VR2_adapter_calls": consumed["private_execution"]["VR2_adapter_calls"],
            "VR2_adapter_successes": consumed["private_execution"][
                "VR2_adapter_successes"
            ],
            "underlying_VR2_route_available": False,
            "private_reinspection_allowed": False,
        },
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "sha256": CONTRACT_SHA256,
            "fixed_input_artifacts": len(measured_inputs),
            "private_or_Git_ignored_input_artifacts": 0,
        },
        "wrapper_diagnostic": collapse,
        "call_path_and_route_accounting": call_path,
        "producer_lineage": lineage,
        "selection_contract_diagnostic": selection,
        "root_cause": {
            "class": (
                "aggregate_route_collapse_plus_generated_selection_identity_"
                "overconstraint"
            ),
            "why_the_failure_is_opaque": (
                "VR4P maps every LiveDomainEligibilityRefusal to one outer F07 "
                "without retaining exc.route"
            ),
            "why_generated_VR2_passed": (
                "all eight generated success paths intentionally reproduce one "
                "generated selection count reservation total and identity hash"
            ),
            "why_VR2_is_not_yet_live_selection_compatible": (
                "the live path compares measured selection outputs against those "
                "exact generated values and emits generated source semantics"
            ),
            "exact_private_predicate_proven": False,
            "observed_nested_route_inferred": False,
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
            "signal_event_target_label_quality_channel_or_geometry_reads": 0,
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
            "all_fixed_artifact_hashes_passed": True,
            "outer_wrapper_route_collapse_proven": collapse["collapse_proven"],
            "all_eight_nested_routes_accounted_for": (
                call_path["nested_routes_accounted_for"] == 8
            ),
            "producer_envelope_lineage_reconciled": True,
            "exact_generated_selection_assertions_enumerated": (
                selection["exact_generated_field_count"] == 9
            ),
            "live_selection_overconstraint_proven": selection[
                "live_selection_overconstraint_proven"
            ],
            "generated_source_semantics_on_live_path_proven": (
                not selection["live_source_semantics_preserved"]
            ),
            "exact_private_predicate_left_unresolved": True,
            "one_thread_runtime_RSS_input_and_output_caps": True,
            "zero_private_archive_neural_target_model_score_network_operations": True,
        },
        "route": route,
        "warnings": [
            "The consumed private VR2 route was not retained and remains unavailable.",
            "F06 is a proven compatibility hazard, not a claim that the consumed attempt reached F06.",
            "Producer-envelope consistency constrains F02 but does not identify or exclude the observed nested route.",
            "No private source, ignored path, consumed output, archive member, neural value, target, model, or score was accessed.",
        ],
        "unavailable_fields": [
            "observed nested VR2 route reason predicate and value",
            "private source rows and real selected cohort identity",
            "real selected reservation bytes subject count and selection hash",
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
        raise Vr2RefusalLocalizationRefusal(
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
            "marc2_vr2_refusal_localization"
        ),
        description=(
            "Localize the consumed VR2 boundary from fixed committed artifacts "
            "without private data access."
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
    except Vr2RefusalLocalizationRefusal as exc:
        print(f"{exc.route}: {exc.safe_reason}", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(value).decode("ascii"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
