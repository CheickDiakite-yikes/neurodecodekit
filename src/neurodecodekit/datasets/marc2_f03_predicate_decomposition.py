"""Artifact-only MARC2 F03 decomposition and generated witness qualification."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import os
import resource
import sys
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.datasets import marc2_generated_diagnostic_relay as relay

SCHEMA_VERSION = "0.1.0"
LANE_ID = "MARC2-VR10A"
CONTRACT_SCHEMA_NAME = (
    "neurodecodekit.marc2_f03_predicate_decomposition_contract"
)
REPORT_SCHEMA_NAME = "neurodecodekit.marc2_f03_predicate_decomposition_result"
CONTRACT_RELATIVE_PATH = Path(
    "registries/marc2_f03_predicate_decomposition_contract.v0.json"
)
CONTRACT_SHA256 = "2aa08e08f1f36b499ec0526cc9d7d3b2abf01a20f9e3cf78ef6f62bdfeb1760c"
GREEN_REGISTRATION_COMMIT = "80175a7e6483a6d156b23a24f9503a9ae32e7201"
GREEN_REGISTRATION_CI_RUN_ID = 31_997_129_703
GREEN_REGISTRATION_BASE_JOB_ID = 95_290_665_076
GREEN_REGISTRATION_OPTIONAL_JOB_ID = 95_290_665_173
SUCCESS_ROUTE = "MARC2VR10A-G1"
REFUSAL_ROUTES = tuple(f"MARC2VR10A-F{index:02d}" for index in range(1, 8))
CASES = (
    "control_success",
    "overlong_member_name",
    "suffix_bearing_BIDS_identity",
    "task_token_case",
    "logical_companion_alias",
    "incomplete_companion_set",
)
ORDERS = ("canonical", "reversed")
CASE_PREDICATES = {
    "control_success": None,
    "overlong_member_name": "F03P03_member_name_UTF8_length_at_most_1024",
    "suffix_bearing_BIDS_identity": "F03P15_suffix_bearing_BIDS_identity",
    "task_token_case": "F03P16_exact_freewill_task_token",
    "logical_companion_alias": "F03P18_unique_logical_run_companion",
    "incomplete_companion_set": "F03P19_complete_four_companion_set",
}
THREAD_ENVIRONMENT = relay.THREAD_ENVIRONMENT
FORBIDDEN_IMPORT_ROOTS = relay.FORBIDDEN_IMPORT_ROOTS
FORBIDDEN_PUBLIC_KEYS = frozenset(
    {
        "candidate",
        "cohort",
        "crc32",
        "entries",
        "event",
        "exception",
        "failed_value",
        "label",
        "labels",
        "member_name",
        "participant_id",
        "path",
        "prediction",
        "predictions",
        "private_hash",
        "private_manifest",
        "reason",
        "row",
        "rows",
        "safe_reason",
        "selection",
        "session_id",
        "signal",
        "source_identity",
        "subject_id",
        "target",
        "targets",
    }
)


class F03PredicateDecompositionRefusal(RuntimeError):
    """Fail closed with one aggregate-safe VR10A route."""

    def __init__(self, route: str, reason: str) -> None:
        if route not in REFUSAL_ROUTES:
            raise ValueError("unknown MARC2-VR10A refusal route")
        super().__init__(f"{route}: {reason}")
        self.route = route
        self.safe_reason = reason


@dataclass(frozen=True, slots=True)
class PredicateSignature:
    predicate_id: str
    module_role: str
    function_name: str
    fragments: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ComposedWitness:
    source: Mapping[str, Any]
    materialized_bytes: int
    central_directory_bytes: int
    entry_count: int
    regular_file_rows: int
    directory_rows: int
    zip64_entries: int
    local_interval_end: int
    witness_mutation_stage: str
    synthetic_normalization_fields: tuple[str, ...]


PREDICATE_SIGNATURES = (
    PredicateSignature(
        "F03P01_row_object_and_exact_field_set",
        "freewill_selector_module",
        "_validate_entry",
        ("not isinstance(row, dict)", "set(row) != ENTRY_FIELDS"),
    ),
    PredicateSignature(
        "F03P02_member_name_string_and_nonempty",
        "freewill_selector_module",
        "_normalize_member_name",
        ("not isinstance(value, str)", "not value"),
    ),
    PredicateSignature(
        "F03P03_member_name_UTF8_length_at_most_1024",
        "freewill_selector_module",
        "_normalize_member_name",
        ('len(value.encode("utf-8")) > 1024',),
    ),
    PredicateSignature(
        "F03P04_member_name_NFC",
        "freewill_selector_module",
        "_normalize_member_name",
        ('unicodedata.normalize("NFC", value) != value',),
    ),
    PredicateSignature(
        "F03P05_safe_relative_prefix_and_separators",
        "freewill_selector_module",
        "_normalize_member_name",
        ("member path is not safe POSIX relative",),
    ),
    PredicateSignature(
        "F03P06_no_control_characters",
        "freewill_selector_module",
        "_normalize_member_name",
        ("ord(char) < 32", "ord(char) == 127"),
    ),
    PredicateSignature(
        "F03P07_no_empty_dot_or_parent_components",
        "freewill_selector_module",
        "_normalize_member_name",
        ("member path has unsafe component",),
    ),
    PredicateSignature(
        "F03P08_lowercase_eight_hex_CRC",
        "freewill_selector_module",
        "_validate_entry",
        ('CRC_RE.fullmatch(row["CRC32"])',),
    ),
    PredicateSignature(
        "F03P09_nonboolean_integer_fields",
        "freewill_selector_module",
        "_validate_entry",
        ("for key in integer_fields", "not isinstance(row[key], int)"),
    ),
    PredicateSignature(
        "F03P10_nonnegative_sizes",
        "freewill_selector_module",
        "_validate_entry",
        ('row["compressed_size"] < 0', 'row["uncompressed_size"] < 0'),
    ),
    PredicateSignature(
        "F03P11_boolean_ZIP64_declaration",
        "freewill_selector_module",
        "_validate_entry",
        ('not isinstance(row["ZIP64_extra_used"], bool)',),
    ),
    PredicateSignature(
        "F03P12_unencrypted_method_zero_or_eight",
        "freewill_selector_module",
        "_validate_entry",
        (
            'row["compression_method"] not in {0, 8}',
            'row["general_purpose_flags"] & 0x1',
        ),
    ),
    PredicateSignature(
        "F03P13_exact_directory_shape",
        "freewill_selector_module",
        "_validate_entry",
        ('row["entry_kind"] == "directory"', 'row["compression_method"] != 0'),
    ),
    PredicateSignature(
        "F03P14_exact_regular_file_shape",
        "freewill_selector_module",
        "_validate_entry",
        ('row["entry_kind"] != "regular_file"', "name.endswith(\"/\")"),
    ),
    PredicateSignature(
        "F03P15_suffix_bearing_BIDS_identity",
        "freewill_selector_module",
        "_validate_entry",
        ("match is None and any", "Freewill BIDS identity differs"),
    ),
    PredicateSignature(
        "F03P16_exact_freewill_task_token",
        "freewill_selector_module",
        "_validate_entry",
        ('match.group("task") != "freewill"',),
    ),
    PredicateSignature(
        "F03P17_unique_full_member_name",
        "source_validity_module",
        "_group_source_rows",
        ("if name in names",),
    ),
    PredicateSignature(
        "F03P18_unique_logical_run_companion",
        "source_validity_module",
        "_group_source_rows",
        ("if suffix in grouped[key]",),
    ),
    PredicateSignature(
        "F03P19_complete_four_companion_set",
        "source_validity_module",
        "_group_source_rows",
        ("set(companions) != set(selector.REQUIRED_SUFFIXES)",),
    ),
    PredicateSignature(
        "F03P20_exact_regular_and_directory_counts",
        "VR2_validator_module",
        "validate_live_domain_source",
        ("if kinds != Counter", '"regular_file": domain["regular_file_rows"]'),
    ),
)


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
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate JSON is not canonical"
        ) from exc


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read_fixed(root: Path, relative: str) -> bytes:
    try:
        path = relay._fixed_path(root, relative)
        return relay._read_bound_file(path)
    except relay.GeneratedDiagnosticRelayRefusal as exc:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed artifact read refused"
        ) from exc


def _verify_contract_mapping(contract: Mapping[str, Any]) -> None:
    if (
        contract.get("schema_name") != CONTRACT_SCHEMA_NAME
        or contract.get("schema_version") != SCHEMA_VERSION
        or contract.get("lane_id") != LANE_ID
        or contract.get("status")
        != "preregistered_artifact_only_generated_only_no_private_access"
        or contract.get("fixed_input_count") != 14
        or contract.get("fixed_input_bytes") != 453_477
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered contract identity differs"
        )
    predicates = contract.get("F03_leaf_predicates")
    expected_ids = [row.predicate_id for row in PREDICATE_SIGNATURES]
    if (
        not isinstance(predicates, list)
        or [row.get("predicate_id") for row in predicates] != expected_ids
        or any(row.get("private_observation") is not False for row in predicates)
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "registered predicate inventory differs"
        )
    partition = contract.get("partition_summary", {})
    if partition != {
        "leaf_predicates": 20,
        "excluded_by_committed_evidence": 15,
        "unresolved_source_dependent": 5,
        "private_observations": 0,
        "causal_claims": 0,
    }:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "registered predicate partition differs"
        )
    matrix = contract.get("generated_witness_matrix", {})
    rows = matrix.get("cases")
    if (
        not isinstance(rows, list)
        or [row.get("case") for row in rows] != list(CASES)
        or matrix.get("orders") != list(ORDERS)
        or matrix.get("replays") != 2
        or matrix.get("required_paths") != 24
        or matrix.get("required_exact_parser_entry_visits") != 29_448
        or matrix.get("required_VR6_calls") != 24
        or matrix.get("control_success_paths") != 4
        or matrix.get("nested_F03_paths") != 20
        or matrix.get("mutation_before_exact_parser_required") is not True
        or matrix.get("mutation_after_parser_or_producer_allowed") is not False
        or matrix.get("refused_source_immutability_required") is not True
        or matrix.get("deterministic_replay_required") is not True
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered generated matrix differs"
        )
    if contract.get("direct_refusal_minimum") != 40:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered refusal minimum differs"
        )
    if any(contract.get("authorization_state", {}).values()):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered authority is not all false"
        )
    if any(contract.get("operation_counters", {}).values()):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "registered operations are not all zero"
        )


def load_registered_contract(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact remotely green VR10A registration."""

    root = Path(repo_root or _repo_root()).resolve()
    payload = _read_fixed(root, CONTRACT_RELATIVE_PATH.as_posix())
    if _sha256_bytes(payload) != CONTRACT_SHA256:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "contract SHA-256 differs"
        )
    try:
        contract = relay._strict_json(payload)
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "contract JSON differs"
        ) from exc
    _verify_contract_mapping(contract)
    return contract


def _verify_fixed_inputs(
    root: Path, contract: Mapping[str, Any]
) -> tuple[dict[str, bytes], int, int]:
    fixed = contract.get("fixed_inputs")
    registration = contract.get("registration_artifacts", {})
    if not isinstance(fixed, list) or len(fixed) != 14:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "fixed input inventory differs"
        )
    combined = [
        *fixed,
        {
            "role": "registration_document",
            "path": registration.get("document_path"),
            "sha256": registration.get("document_sha256"),
        },
        {
            "role": "registration_test",
            "path": registration.get("test_path"),
            "sha256": registration.get("test_sha256"),
        },
    ]
    payloads: dict[str, bytes] = {}
    total = 0
    for row in combined:
        expected = {"role", "path", "sha256"}
        if "bytes" in row:
            expected.add("bytes")
        if (
            not isinstance(row, dict)
            or set(row) != expected
            or not isinstance(row.get("role"), str)
            or row["role"] in payloads
            or not isinstance(row.get("path"), str)
            or not isinstance(row.get("sha256"), str)
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input binding differs"
            )
        payload = _read_fixed(root, row["path"])
        if (
            ("bytes" in row and len(payload) != row["bytes"])
            or _sha256_bytes(payload) != row["sha256"]
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[0], "fixed input size or SHA-256 differs"
            )
        payloads[row["role"]] = payload
        total += len(payload)
    contract_payload = _read_fixed(root, CONTRACT_RELATIVE_PATH.as_posix())
    return payloads, len(combined) + 1, total + len(contract_payload)


def _function_source(payload: bytes, function_name: str) -> str:
    try:
        source = payload.decode("utf-8")
        tree = ast.parse(source)
    except (UnicodeDecodeError, SyntaxError) as exc:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "bound validator AST is unavailable"
        ) from exc
    matches = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function_name
    ]
    if len(matches) != 1:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "bound validator function inventory differs"
        )
    segment = ast.get_source_segment(source, matches[0])
    if not isinstance(segment, str):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "bound validator function source is unavailable"
        )
    return segment


def _inventory_predicates(
    payloads: Mapping[str, bytes], contract: Mapping[str, Any]
) -> list[dict[str, str]]:
    registered = {
        row["predicate_id"]: row["status"]
        for row in contract["F03_leaf_predicates"]
    }
    cache: dict[tuple[str, str], str] = {}
    rows: list[dict[str, str]] = []
    for signature in PREDICATE_SIGNATURES:
        key = (signature.module_role, signature.function_name)
        if key not in cache:
            if signature.module_role not in payloads:
                raise F03PredicateDecompositionRefusal(
                    REFUSAL_ROUTES[1], "predicate source role is unavailable"
                )
            cache[key] = _function_source(
                payloads[signature.module_role], signature.function_name
            )
        if any(fragment not in cache[key] for fragment in signature.fragments):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[1], "predicate AST signature differs"
            )
        rows.append(
            {
                "predicate_id": signature.predicate_id,
                "status": registered[signature.predicate_id],
            }
        )
    _validate_inventory(rows, contract)
    return rows


def _validate_inventory(
    rows: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> None:
    expected = [
        {"predicate_id": row["predicate_id"], "status": row["status"]}
        for row in contract["F03_leaf_predicates"]
    ]
    counts = Counter(row.get("status") for row in rows)
    if (
        list(rows) != expected
        or len(rows) != 20
        or counts
        != Counter(
            {
                "excluded_by_committed_evidence": 15,
                "unresolved_source_dependent": 5,
            }
        )
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "predicate inventory or partition differs"
        )


def _validate_live_aggregate(payloads: Mapping[str, bytes]) -> None:
    try:
        result = relay._strict_json(payloads["central_directory_live_aggregate_result"])
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "live aggregate JSON differs"
        ) from exc
    summary = result.get("archive_summary", {})
    if (
        result.get("route") != "MARC1CD-R1"
        or summary.get("entry_count") != 1_227
        or summary.get("regular_file_entries") != 1_025
        or summary.get("directory_entries") != 202
        or summary.get("method_counts") != {"0": 202, "8": 1_025}
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[1], "live aggregate entry counts differ"
        )


def _core_rows(source: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = [
        row
        for row in source["entries"]
        if relay.selector._core_match(row["member_name"]) is not None
    ]
    if len(rows) != 952:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[2], "generated core row count differs"
        )
    return sorted(rows, key=lambda row: row["member_name"])


def _mutate_blueprint(source: dict[str, Any], case: str) -> None:
    if case == "control_success":
        return
    core = _core_rows(source)
    target = next(row for row in core if row["member_name"].endswith("_eeg.vhdr"))
    original = target["member_name"]
    if case == "overlong_member_name":
        target["member_name"] = f"vr10a_{'x' * 1_024}/{original}"
        if (
            len(target["member_name"].encode("utf-8")) <= 1_024
            or relay.selector._core_match(target["member_name"]) is None
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[2], "overlong generated witness differs"
            )
        return
    if case == "suffix_bearing_BIDS_identity":
        match = relay.selector._core_match(original)
        if match is None:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[2], "BIDS identity witness source differs"
            )
        subject = match.group("subject")
        changed_subject = "sub-99" if subject != "sub-99" else "sub-98"
        parent, basename = original.rsplit("/", 1)
        target["member_name"] = (
            f"{parent}/{basename.replace(f'{subject}_', f'{changed_subject}_', 1)}"
        )
        if (
            relay.selector._core_match(target["member_name"]) is not None
            or not target["member_name"].endswith("_eeg.vhdr")
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[2], "BIDS identity generated witness differs"
            )
        return
    if case == "task_token_case":
        relay._mutate_blueprint(source, "F03")
        return
    if case == "logical_companion_alias":
        auxiliary = next(
            row
            for row in source["entries"]
            if row["entry_kind"] == "regular_file"
            and relay.selector._core_match(row["member_name"]) is None
            and not any(
                row["member_name"].endswith(suffix)
                for suffix in relay.selector.REQUIRED_SUFFIXES
            )
        )
        auxiliary["member_name"] = f"vr10a_alias/{original}"
        if relay.selector._core_match(auxiliary["member_name"]) is None:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[2], "logical companion alias witness differs"
            )
        return
    if case == "incomplete_companion_set":
        replacement = "Freewill_generated/generated_aux/vr10a_removed_core.bin"
        if any(row["member_name"] == replacement for row in source["entries"]):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[2], "incomplete companion replacement collides"
            )
        target["member_name"] = replacement
        return
    raise ValueError("unknown generated F03 witness case")


def _compose_witness(
    case: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> ComposedWitness:
    if case not in CASES or order not in ORDERS:
        raise ValueError("unknown generated F03 witness path")
    blueprint = relay.vr2.build_generated_live_source(
        profile="A",
        row_order="canonical",
        contract=vr2_contract,
        selector_contract=selector_contract,
    )
    before = relay.vr2._canonical_source_bytes(blueprint)
    _mutate_blueprint(blueprint, case)
    after = relay.vr2._canonical_source_bytes(blueprint)
    if (case == "control_success" and before != after) or (
        case != "control_success" and before == after
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[2], "pre-parser witness mutation differs"
        )
    specs = relay._entry_specs(blueprint, order)
    try:
        fixture = relay.parser.build_generated_fixture(specs)
        local_end = relay._validate_specs(
            specs, central_directory_offset=fixture.central_directory_offset
        )
        run, _opener = relay.producer._run_generated_path(fixture, redirect_count=0)
        source = relay.producer._private_manifest(run, generated=False)
    except (
        relay.parser.Marc1CentralDirectoryRefusal,
        relay.producer.LiveArchiveRefusal,
        relay.GeneratedDiagnosticRelayRefusal,
    ) as exc:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[2], "exact generated parser or producer refused"
        ) from exc
    normalization_before = copy.deepcopy(source)
    source["transport_body_sha256"] = copy.deepcopy(
        vr2_contract["generated_live_source_domain"]["transport_body_sha256"]
    )
    normalization_fields = tuple(
        key
        for key in sorted(source)
        if source.get(key) != normalization_before.get(key)
    )
    if normalization_fields != ("transport_body_sha256",):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[2], "synthetic transport normalization differs"
        )
    entries = source.get("entries")
    kinds = Counter(
        row.get("entry_kind") for row in entries if isinstance(row, dict)
    )
    if (
        not isinstance(entries, list)
        or len(entries) != 1_227
        or kinds != Counter({"regular_file": 1_025, "directory": 202})
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[2], "exact parser output shape differs"
        )
    return ComposedWitness(
        source=source,
        materialized_bytes=fixture.materialized_bytes,
        central_directory_bytes=len(fixture.central_directory_body),
        entry_count=len(entries),
        regular_file_rows=kinds["regular_file"],
        directory_rows=kinds["directory"],
        zip64_entries=sum(spec.force_zip64 for spec in specs),
        local_interval_end=local_end,
        witness_mutation_stage=(
            "none_control" if case == "control_success" else "before_exact_parser"
        ),
        synthetic_normalization_fields=normalization_fields,
    )


def _safe_outcome(
    *,
    case: str,
    disposition: str,
    outer_route: str,
    nested_route: str | None,
) -> dict[str, Any]:
    predicate = CASE_PREDICATES[case]
    digest = _sha256_bytes(
        _canonical_json_bytes(
            {
                "case": case,
                "predicate_id": predicate,
                "disposition": disposition,
                "outer_route": outer_route,
                "nested_route": nested_route,
            }
        )
    )
    return {
        "case": case,
        "predicate_id": predicate,
        "predicate_status": (
            "control" if predicate is None else "unresolved_source_dependent"
        ),
        "disposition": disposition,
        "outer_VR6_route": outer_route,
        "nested_VR2_route": nested_route,
        "outcome_digest_sha256": digest,
    }


def _run_path(
    case: str,
    order: str,
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    composed = _compose_witness(
        case,
        order,
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    before = relay.vr2._canonical_source_bytes(composed.source)
    try:
        relay.vr6.adapt_dynamic_live_source(
            composed.source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
    except relay.vr6.DynamicLiveSelectionRefusal as exc:
        if relay.vr2._canonical_source_bytes(composed.source) != before:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[3], "VR6 mutated a refused witness source"
            ) from None
        if (
            case == "control_success"
            or exc.route != "MARC2VR6-F02"
            or exc.upstream_route != "MARC2VR2-F03"
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[3], "generated witness route differs"
            ) from None
        outcome = _safe_outcome(
            case=case,
            disposition="aggregate_refusal",
            outer_route=exc.route,
            nested_route=exc.upstream_route,
        )
    else:
        if relay.vr2._canonical_source_bytes(composed.source) != before:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[3], "VR6 mutated a successful control source"
            )
        if case != "control_success":
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[3], "generated witness unexpectedly passed"
            )
        outcome = _safe_outcome(
            case=case,
            disposition="VR6_success",
            outer_route="VR6_success",
            nested_route=None,
        )
    mechanics = {
        "case": case,
        "order": order,
        "entry_count": composed.entry_count,
        "regular_file_rows": composed.regular_file_rows,
        "directory_rows": composed.directory_rows,
        "materialized_bytes": composed.materialized_bytes,
        "central_directory_bytes": composed.central_directory_bytes,
        "ZIP64_entries": composed.zip64_entries,
        "local_interval_end": composed.local_interval_end,
        "witness_mutation_stage": composed.witness_mutation_stage,
        "synthetic_normalization_fields": list(
            composed.synthetic_normalization_fields
        ),
    }
    return outcome, mechanics


def _run_matrix(
    *,
    vr2_contract: Mapping[str, Any],
    selector_contract: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    outcomes: list[dict[str, Any]] = []
    mechanics: list[dict[str, Any]] = []
    generated_bytes = 0
    for case in CASES:
        order_outcomes: list[dict[str, Any]] = []
        for order in ORDERS:
            outcome, measured = _run_path(
                case,
                order,
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
            )
            order_outcomes.append(outcome)
            mechanics.append(measured)
            generated_bytes += measured["materialized_bytes"]
        if order_outcomes[0] != order_outcomes[1]:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[3], "witness route differs across source order"
            )
        outcomes.append(order_outcomes[0])
    return outcomes, mechanics, generated_bytes


def _validate_replay(
    first: Sequence[Mapping[str, Any]],
    first_mechanics: Sequence[Mapping[str, Any]],
    second: Sequence[Mapping[str, Any]],
    second_mechanics: Sequence[Mapping[str, Any]],
) -> None:
    if first != second or first_mechanics != second_mechanics:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[3], "complete generated witness replay differs"
        )


def _validate_thread_environment(
    environment: Mapping[str, str] | None = None,
) -> None:
    values = os.environ if environment is None else environment
    if any(values.get(name) != "1" for name in THREAD_ENVIRONMENT):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[5], "one-thread environment is not explicit"
        )


def _validate_module_surface() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported: set[str] = set()
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
            modules.add(node.module)
    if imported & FORBIDDEN_IMPORT_ROOTS:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "network or heavy import surface is forbidden"
        )
    if any("marc2_two_layer_private_diagnostic" in value for value in modules):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[0], "consumed VR9P import is forbidden"
        )


def _base_access_counters() -> dict[str, int]:
    return {
        "private_or_Git_ignored_path_operations": 0,
        "consumed_VR9P_path_or_output_operations": 0,
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


def _validate_public_value(value: Any) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in FORBIDDEN_PUBLIC_KEYS:
                raise F03PredicateDecompositionRefusal(
                    REFUSAL_ROUTES[4], "forbidden aggregate field"
                )
            _validate_public_value(nested)
    elif isinstance(value, list):
        for nested in value:
            _validate_public_value(nested)
    elif isinstance(value, str):
        lowered = value.lower()
        if (
            ".codex_work" in lowered
            or "/sub-" in lowered
            or "\\sub-" in lowered
            or lowered.startswith("sub-")
            or "task-freewill" in lowered
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[4], "private path or identity leaked"
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
        (runtime_seconds, caps["runtime_seconds"]),
        (peak_rss_bytes, caps["peak_RSS_bytes"]),
        (generated_input_bytes, caps["generated_input_bytes"]),
        (aggregate_output_bytes, caps["aggregate_output_bytes"]),
        (retained_output_bytes, caps["retained_generated_output_bytes"]),
    )
    if (
        not math.isfinite(runtime_seconds)
        or runtime_seconds < 0
        or any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or value < 0
            or value > cap
            for value, cap in values
        )
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[5], "resource or output cap exceeded"
        )


def _validate_public_report(report: Mapping[str, Any]) -> None:
    if (
        report.get("schema_name") != REPORT_SCHEMA_NAME
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("lane_id") != LANE_ID
        or report.get("route") != SUCCESS_ROUTE
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate report identity differs"
        )
    inventory = report.get("predicate_inventory")
    if not isinstance(inventory, list) or len(inventory) != 20:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate predicate inventory differs"
        )
    matrix = report.get("witness_matrix")
    if not isinstance(matrix, list) or [row.get("case") for row in matrix] != list(
        CASES
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[4], "aggregate witness matrix differs"
        )
    for index, row in enumerate(matrix):
        expected_keys = {
            "case",
            "predicate_id",
            "predicate_status",
            "disposition",
            "outer_VR6_route",
            "nested_VR2_route",
            "outcome_digest_sha256",
        }
        if set(row) != expected_keys:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[4], "aggregate witness row fields differ"
            )
        if index == 0:
            valid = (
                row.get("predicate_id") is None
                and row.get("predicate_status") == "control"
                and row.get("disposition") == "VR6_success"
                and row.get("outer_VR6_route") == "VR6_success"
                and row.get("nested_VR2_route") is None
            )
        else:
            valid = (
                row.get("predicate_id") == CASE_PREDICATES[row["case"]]
                and row.get("predicate_status") == "unresolved_source_dependent"
                and row.get("disposition") == "aggregate_refusal"
                and row.get("outer_VR6_route") == "MARC2VR6-F02"
                and row.get("nested_VR2_route") == "MARC2VR2-F03"
            )
        digest = row.get("outcome_digest_sha256")
        if (
            not valid
            or not isinstance(digest, str)
            or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)
        ):
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[4], "aggregate witness route differs"
            )
    replay = report.get("replay_summary", {})
    if (
        replay.get("exact_replays") != 2
        or replay.get("paths_per_replay") != 12
        or replay.get("total_paths") != 24
        or replay.get("exact_parser_entry_visits") != 29_448
        or replay.get("exact_VR6_calls") != 24
        or replay.get("control_success_paths") != 4
        or replay.get("nested_F03_paths") != 20
        or replay.get("route_and_mechanics_replay_byte_identical") is not True
    ):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[3], "aggregate replay summary differs"
        )
    if any(report.get("access_counters", {}).values()):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[4], "forbidden operation counter is nonzero"
        )
    if not all(report.get("acceptance_gates", {}).values()):
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[3], "acceptance gate is false"
        )
    _validate_public_value(report)


def _expect_refusal(
    name: str,
    action: Callable[[], Any],
    *,
    expected_route: str,
) -> str:
    try:
        action()
    except F03PredicateDecompositionRefusal as exc:
        if exc.route != expected_route:
            raise F03PredicateDecompositionRefusal(
                REFUSAL_ROUTES[6], f"refusal route differs: {name}"
            ) from exc
        return exc.route
    raise F03PredicateDecompositionRefusal(
        REFUSAL_ROUTES[6], f"required refusal did not occur: {name}"
    )


def _run_required_refusals(
    report: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
    inventory: Sequence[Mapping[str, Any]],
) -> dict[str, str]:
    checks: dict[str, tuple[str, Callable[[], Any]]] = {}

    def changed_contract(
        mutator: Callable[[dict[str, Any]], None],
    ) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(contract))
            mutator(changed)
            _verify_contract_mapping(changed)

        return action

    def changed_report(mutator: Callable[[dict[str, Any]], None]) -> Callable[[], Any]:
        def action() -> None:
            changed = copy.deepcopy(dict(report))
            mutator(changed)
            _validate_public_report(changed)

        return action

    checks.update(
        {
            "contract_schema_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("schema_name", "changed")
                ),
            ),
            "contract_status_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(lambda value: value.__setitem__("status", "changed")),
            ),
            "fixed_input_count_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("fixed_input_count", 13)
                ),
            ),
            "fixed_input_bytes_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value.__setitem__("fixed_input_bytes", 1)
                ),
            ),
            "partition_leaf_count_drift": (
                REFUSAL_ROUTES[1],
                changed_contract(
                    lambda value: value["partition_summary"].__setitem__(
                        "leaf_predicates", 19
                    )
                ),
            ),
            "matrix_case_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["generated_witness_matrix"]["cases"][
                        0
                    ].__setitem__("case", "changed")
                ),
            ),
            "matrix_path_count_drift": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["generated_witness_matrix"].__setitem__(
                        "required_paths", 23
                    )
                ),
            ),
            "authorization_nonzero": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["authorization_state"].__setitem__(
                        "private_manifest_or_consumed_root_access_authorized_now",
                        True,
                    )
                ),
            ),
            "registered_counter_nonzero": (
                REFUSAL_ROUTES[0],
                changed_contract(
                    lambda value: value["operation_counters"].__setitem__(
                        "network_or_public_request_operations", 1
                    )
                ),
            ),
        }
    )
    for row in inventory:
        predicate_id = row["predicate_id"]
        checks[f"missing_{predicate_id}"] = (
            REFUSAL_ROUTES[1],
            lambda predicate_id=predicate_id: _validate_inventory(
                [
                    value
                    for value in inventory
                    if value["predicate_id"] != predicate_id
                ],
                contract,
            ),
        )
    checks.update(
        {
            "replay_mismatch": (
                REFUSAL_ROUTES[3],
                lambda: _validate_replay(
                    ({"case": "control_success"},),
                    ({"entry_count": 1_227},),
                    ({"case": "changed"},),
                    ({"entry_count": 1_227},),
                ),
            ),
            "report_schema_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value.__setitem__("schema_name", "changed")
                ),
            ),
            "report_case_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["witness_matrix"][1].__setitem__(
                        "case", "changed"
                    )
                ),
            ),
            "report_outer_route_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["witness_matrix"][1].__setitem__(
                        "outer_VR6_route", "MARC2VR6-F03"
                    )
                ),
            ),
            "report_nested_route_drift": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["witness_matrix"][1].__setitem__(
                        "nested_VR2_route", "MARC2VR2-F04"
                    )
                ),
            ),
            "reason_key_leak": (
                REFUSAL_ROUTES[4],
                changed_report(lambda value: value.__setitem__("reason", "hidden")),
            ),
            "member_name_key_leak": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value.__setitem__("member_name", "hidden")
                ),
            ),
            "private_path_leak": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["warnings"].append(".codex_work/hidden")
                ),
            ),
            "acceptance_gate_false": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["acceptance_gates"].__setitem__(
                        "AST_inventory_finds_exactly_20_F03_leaf_predicates", False
                    )
                ),
            ),
            "public_counter_nonzero": (
                REFUSAL_ROUTES[4],
                changed_report(
                    lambda value: value["access_counters"].__setitem__(
                        "network_or_public_request_operations", 1
                    )
                ),
            ),
            "replay_path_count_drift": (
                REFUSAL_ROUTES[3],
                changed_report(
                    lambda value: value["replay_summary"].__setitem__(
                        "total_paths", 23
                    )
                ),
            ),
            "thread_environment_drift": (
                REFUSAL_ROUTES[5],
                lambda: _validate_thread_environment({}),
            ),
        }
    )

    def resource_action(**overrides: Any) -> None:
        values = {
            "runtime_seconds": 0.1,
            "peak_rss_bytes": 1,
            "generated_input_bytes": 1,
            "aggregate_output_bytes": 1,
            "retained_output_bytes": 0,
            "contract": contract,
        }
        values.update(overrides)
        _assert_resources(**values)

    caps = contract["resource_caps"]
    checks.update(
        {
            "runtime_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=caps["runtime_seconds"] + 1),
            ),
            "RSS_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(peak_rss_bytes=caps["peak_RSS_bytes"] + 1),
            ),
            "generated_input_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    generated_input_bytes=caps["generated_input_bytes"] + 1
                ),
            ),
            "aggregate_output_cap_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(
                    aggregate_output_bytes=caps["aggregate_output_bytes"] + 1
                ),
            ),
            "retained_output_drift": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(retained_output_bytes=1),
            ),
            "nonfinite_runtime": (
                REFUSAL_ROUTES[5],
                lambda: resource_action(runtime_seconds=float("nan")),
            ),
        }
    )
    if len(checks) < contract["direct_refusal_minimum"]:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[6], "required refusal inventory is too small"
        )
    return {
        name: _expect_refusal(name, action, expected_route=route)
        for name, (route, action) in checks.items()
    }


def _peak_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1_024)


def qualify_generated(
    *,
    repo_root: str | Path | None = None,
    clock: Callable[[], float] = time.perf_counter,
    rss_reader: Callable[[], int] = _peak_rss_bytes,
    environment: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Run the frozen 24-path artifact-only generated qualification."""

    started = clock()
    _validate_thread_environment(environment)
    root = Path(repo_root or _repo_root()).resolve()
    contract = load_registered_contract(root)
    payloads, fixed_artifact_count, fixed_artifact_bytes = _verify_fixed_inputs(
        root, contract
    )
    _validate_module_surface()
    inventory = _inventory_predicates(payloads, contract)
    _validate_live_aggregate(payloads)
    vr2_contract = relay.vr2.load_registered_contract(root)
    selector_contract = relay.selector.load_registered_contract(root)
    first, first_mechanics, first_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    second, second_mechanics, second_bytes = _run_matrix(
        vr2_contract=vr2_contract,
        selector_contract=selector_contract,
    )
    _validate_replay(first, first_mechanics, second, second_mechanics)
    all_mechanics = [*first_mechanics, *second_mechanics]
    provisional: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "completed_artifact_only_generated_F03_decomposition",
        "proof_posture": (
            "tracked_code_and_generated_structural_interface_only_no_private_or_"
            "scientific_value"
        ),
        "route": SUCCESS_ROUTE,
        "green_registration_proof": {
            "commit": GREEN_REGISTRATION_COMMIT,
            "CI_run_id": GREEN_REGISTRATION_CI_RUN_ID,
            "base_python_job_id": GREEN_REGISTRATION_BASE_JOB_ID,
            "optional_neuro_job_id": GREEN_REGISTRATION_OPTIONAL_JOB_ID,
            "both_required_jobs_green_before_implementation": True,
            "contract_sha256": CONTRACT_SHA256,
        },
        "predicate_inventory": inventory,
        "partition_summary": {
            "leaf_predicates": 20,
            "excluded_by_committed_evidence": 15,
            "unresolved_source_dependent": 5,
            "private_observations": 0,
            "causal_claims": 0,
        },
        "witness_matrix": first,
        "replay_summary": {
            "exact_replays": 2,
            "paths_per_replay": 12,
            "total_paths": len(all_mechanics),
            "exact_parser_entry_visits": sum(
                row["entry_count"] for row in all_mechanics
            ),
            "exact_VR6_calls": len(all_mechanics),
            "control_success_paths": sum(
                row["case"] == "control_success" for row in all_mechanics
            ),
            "nested_F03_paths": sum(
                row["case"] != "control_success" for row in all_mechanics
            ),
            "route_and_mechanics_replay_byte_identical": True,
        },
        "mechanics": {
            "entry_count_each": 1_227,
            "regular_file_rows_each": 1_025,
            "directory_rows_each": 202,
            "materialized_bytes_minimum_per_path": min(
                row["materialized_bytes"] for row in all_mechanics
            ),
            "materialized_bytes_maximum_per_path": max(
                row["materialized_bytes"] for row in all_mechanics
            ),
            "central_directory_bytes_minimum": min(
                row["central_directory_bytes"] for row in all_mechanics
            ),
            "central_directory_bytes_maximum": max(
                row["central_directory_bytes"] for row in all_mechanics
            ),
            "ZIP64_entries_minimum": min(
                row["ZIP64_entries"] for row in all_mechanics
            ),
            "ZIP64_entries_maximum": max(
                row["ZIP64_entries"] for row in all_mechanics
            ),
            "maximum_local_interval_end": max(
                row["local_interval_end"] for row in all_mechanics
            ),
            "witness_mutations_before_exact_parser": 20,
            "control_paths_without_witness_mutation": 4,
            "post_parser_witness_mutations": 0,
            "synthetic_normalization_fields": ["transport_body_sha256"],
            "member_local_header_bytes": 0,
            "member_payload_bytes": 0,
        },
        "measurements": {
            "fixed_artifact_count": fixed_artifact_count,
            "fixed_artifact_bytes": fixed_artifact_bytes,
            "generated_input_bytes": first_bytes + second_bytes,
            "aggregate_output_bytes": 0,
            "retained_generated_output_bytes": 0,
            "runtime_seconds": 0.0,
            "peak_RSS_bytes": 0,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "producer_is_causal": "not_applicable_structural_metadata_only",
            "end_to_end_latency_measured": False,
        },
        "direct_refusals": {},
        "acceptance_gates": {
            "all_fixed_inputs_match_size_and_SHA256": True,
            "AST_inventory_finds_exactly_20_F03_leaf_predicates": True,
            "exactly_15_leaf_predicates_excluded_by_committed_evidence": True,
            "exactly_five_frozen_source_dependent_predicates_remain": True,
            "all_24_exact_parser_producer_paths_replay_identically": True,
            "four_control_paths_succeed_and_20_witness_paths_relay_outer_F02_nested_F03": True,
            "all_witness_mutations_precede_exact_parser": True,
            "refused_VR6_calls_do_not_mutate_source": True,
            "at_least_40_direct_refusals_pass": True,
            "retained_generated_output_is_zero": True,
            "runtime_RSS_input_and_output_caps_pass": True,
            "all_private_scientific_other_project_retry_and_claim_counters_are_zero": True,
        },
        "access_counters": _base_access_counters(),
        "warnings": [
            "Fifteen exclusions are tracked-code or aggregate implications, not private row observations.",
            "Five unresolved predicates are a frozen possibility set, not private-cause findings.",
            "Synthetic transport digest normalization is identical across control and witnesses and is not a witness mutation or live evidence.",
            "Generated F03 witnesses have no scientific or decoding value.",
        ],
        "unavailable_fields": [
            "failed private F03 predicate and value",
            "private row member participant session run and cohort",
            "archive payload signal event target model prediction and score",
        ],
        "next_gate": {
            "exact_implementation_and_result_commit_push_and_both_jobs_green_required": True,
            "future_private_discriminator_authorized": False,
            "future_private_read_requires_new_Tier_C_packet_and_fresh_decision": True,
            "consumed_VR9P_reuse_allowed": False,
            "F03_rule_relaxation_allowed": False,
            "MARC2_FW2_or_CIL1_authorized": False,
        },
        "claim_boundary": {
            "engineering_ceiling": (
                "artifact_only_F03_leaf_inventory_and_full_scale_generated_"
                "witness_coverage"
            ),
            "scientific_ceiling": "none",
            "neural_effect": False,
            "decoding_accuracy": False,
            "language_or_thought_decoding": False,
            "unseen_person_generalization": False,
            "real_time_portable_home_assistive_or_clinical_result": False,
        },
    }
    provisional["direct_refusals"] = _run_required_refusals(
        provisional,
        contract=contract,
        inventory=inventory,
    )
    if len(provisional["direct_refusals"]) < contract["direct_refusal_minimum"]:
        raise F03PredicateDecompositionRefusal(
            REFUSAL_ROUTES[6], "direct refusal inventory is too small"
        )
    runtime_seconds = clock() - started
    peak_rss_bytes = rss_reader()
    provisional["measurements"]["runtime_seconds"] = runtime_seconds
    provisional["measurements"]["peak_RSS_bytes"] = peak_rss_bytes
    output_bytes = len(_canonical_json_bytes(provisional))
    provisional["measurements"]["aggregate_output_bytes"] = output_bytes
    final_bytes = len(_canonical_json_bytes(provisional))
    if final_bytes != output_bytes:
        provisional["measurements"]["aggregate_output_bytes"] = final_bytes
        final_bytes = len(_canonical_json_bytes(provisional))
    _assert_resources(
        runtime_seconds=runtime_seconds,
        peak_rss_bytes=peak_rss_bytes,
        generated_input_bytes=provisional["measurements"]["generated_input_bytes"],
        aggregate_output_bytes=final_bytes,
        retained_output_bytes=0,
        contract=contract,
    )
    _validate_public_report(provisional)
    return provisional


def build_plan_summary(
    *, repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return the frozen generated-only plan without running a witness."""

    contract = load_registered_contract(repo_root)
    matrix = contract["generated_witness_matrix"]
    return {
        "schema_name": CONTRACT_SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": contract["status"],
        "green_registration_commit": GREEN_REGISTRATION_COMMIT,
        "fixed_input_count": contract["fixed_input_count"],
        "fixed_input_bytes": contract["fixed_input_bytes"],
        "leaf_predicates": contract["partition_summary"]["leaf_predicates"],
        "excluded_predicates": contract["partition_summary"][
            "excluded_by_committed_evidence"
        ],
        "unresolved_predicates": contract["partition_summary"][
            "unresolved_source_dependent"
        ],
        "generated_cases": len(matrix["cases"]),
        "required_paths": matrix["required_paths"],
        "private_access_authorized": False,
        "network_bytes": 0,
        "real_or_private_bytes": 0,
    }


def _build_parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser(
        prog=(
            "python -m neurodecodekit.datasets."
            "marc2_f03_predicate_decomposition"
        ),
        description=(
            "Qualify the artifact-only MARC2 F03 leaf inventory and generated "
            "witness matrix."
        ),
    )
    command.add_argument("command", choices=("plan", "qualify"))
    return command


def main(argv: Sequence[str] | None = None) -> int:
    """Run the bounded artifact-only command surface."""

    args = _build_parser().parse_args(argv)
    try:
        output = build_plan_summary() if args.command == "plan" else qualify_generated()
    except F03PredicateDecompositionRefusal as exc:
        print(f"{exc.route}: F03 predicate decomposition refused", file=sys.stderr)
        return 2
    print(_canonical_json_bytes(output).decode("ascii"), end="")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
