"""Synthetic no-call bridge for controlled foundation-model decoder requests."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import time
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence


EVIDENCE_SCHEMA_NAME = "neurodecodekit.foundation_model_synthetic_evidence"
EVIDENCE_SCHEMA_VERSION = 0
PLAN_SCHEMA_NAME = "neurodecodekit.foundation_model_ablation_plan"
PLAN_SCHEMA_VERSION = 0
SUMMARY_SCHEMA_NAME = "neurodecodekit.foundation_model_bridge_summary"
SUMMARY_SCHEMA_VERSION = 0
MODEL_ID = "gpt-5.6-sol"
PROVIDER = "OpenAI"
ENDPOINT = "responses"
REASONING_EFFORT = "low"
MAX_INPUT_BYTES = 1024 * 1024
MAX_OUTPUT_BYTES = 1024 * 1024
MAX_ITEMS = 8
MAX_CTC_HYPOTHESES = 8
MAX_NEURAL_FRAMES = 64
MAX_TOP_KEYS = 8
KEY_SYMBOLS = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ") + ("SPACE", "ENTER", "BACKSPACE")
CONDITION_IDS = ("FM-A00", "FM-A01", "FM-A02", "FM-A03")
ACCESS_COUNTER_FIELDS = (
    "external_network_calls",
    "api_credential_reads",
    "provider_model_calls",
    "local_model_calls",
    "real_or_protected_reads",
    "protected_annotation_reads",
    "training_runs",
    "scoring_runs",
)
ALLOWED_WARNINGS = (
    "synthetic_fixture_only_no_real_or_protected_content",
    "no_reference_or_ground_truth_exists",
    "no_provider_or_model_call_executed",
)
FORBIDDEN_KEY_FRAGMENTS = (
    "target",
    "reference",
    "ground_truth",
    "intended",
    "label",
    "raw_eeg",
    "raw_meg",
    "signal_samples",
    "embedding",
    "neurotoken",
    "participant_name",
    "subject_name",
    "local_path",
)
FIXED_INSTRUCTION = (
    "Recover only text supported by the supplied synthetic decoder evidence. "
    "Do not add names, facts, or words that the evidence does not support. "
    "When evidence is insufficient, set abstained to true. Return only the "
    "declared structured result."
)
RESPONSE_CONTRACT = {
    "type": "object",
    "additional_properties": False,
    "required": [
        "decoded_text",
        "abstained",
        "evidence_used",
        "unsupported_content_warning",
    ],
    "properties": {
        "decoded_text": {"type": "string", "maximum_length": 256},
        "abstained": {"type": "boolean"},
        "evidence_used": {"enum": ["none", "ctc", "ctc_and_neural"]},
        "unsupported_content_warning": {"type": "boolean"},
    },
}


class FoundationModelBridgeError(ValueError):
    """Raised when synthetic bridge input or output violates the v0 contract."""


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a JSON-compatible value deterministically and reject NaN."""

    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    """Return the SHA-256 identity of canonical JSON bytes."""

    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def build_synthetic_evidence_fixture(
    *, fixture_id: str = "FM-SYNTH-001"
) -> dict[str, Any]:
    """Build a tiny target-free evidence fixture without model execution."""

    if re.fullmatch(r"FM-SYNTH-[0-9]{3}", fixture_id) is None:
        raise FoundationModelBridgeError("fixture_id must match FM-SYNTH-NNN")
    payload = {
        "schema_name": EVIDENCE_SCHEMA_NAME,
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "fixture_id": fixture_id,
        "proof_posture": "synthetic_target_free_interface_only",
        "task_context": "synthetic_unprompted_typing_without_reference",
        "items": [
            _fixture_item(
                item_id="SYNTH-ITEM-00",
                hypotheses=(("HELLO WURLD", -0.12), ("HELLO WORLD", -0.84)),
                symbols=("H", "E", "L", "O"),
            ),
            _fixture_item(
                item_id="SYNTH-ITEM-01",
                hypotheses=(("OPEN SORCE", -0.18), ("OPEN SOURCE", -0.91)),
                symbols=("O", "P", "E", "N"),
            ),
            _fixture_item(
                item_id="SYNTH-ITEM-02",
                hypotheses=(("BRAIN TOL", -0.21), ("BRAIN TOOL", -0.97)),
                symbols=("B", "R", "A", "I"),
            ),
        ],
        "access_counters": {name: 0 for name in ACCESS_COUNTER_FIELDS},
        "warnings": list(ALLOWED_WARNINGS),
    }
    validate_synthetic_evidence(payload)
    return payload


def validate_synthetic_evidence(payload: Mapping[str, Any]) -> None:
    """Fail closed on malformed, noncausal, sensitive, or target-like evidence."""

    _reject_forbidden_keys(payload)
    _expect_exact_fields(
        payload,
        {
            "schema_name",
            "schema_version",
            "fixture_id",
            "proof_posture",
            "task_context",
            "items",
            "access_counters",
            "warnings",
        },
        "$",
    )
    _expect_equal(payload, "schema_name", EVIDENCE_SCHEMA_NAME, "$.schema_name")
    _expect_equal(payload, "schema_version", EVIDENCE_SCHEMA_VERSION, "$.schema_version")
    _expect_equal(
        payload,
        "proof_posture",
        "synthetic_target_free_interface_only",
        "$.proof_posture",
    )
    _expect_equal(
        payload,
        "task_context",
        "synthetic_unprompted_typing_without_reference",
        "$.task_context",
    )
    fixture_id = payload.get("fixture_id")
    if not isinstance(fixture_id, str) or re.fullmatch(r"FM-SYNTH-[0-9]{3}", fixture_id) is None:
        raise FoundationModelBridgeError("$.fixture_id must match FM-SYNTH-NNN")

    items = _sequence(payload.get("items"), "$.items")
    if not 2 <= len(items) <= MAX_ITEMS:
        raise FoundationModelBridgeError(f"$.items must contain 2 through {MAX_ITEMS} items")
    item_ids: list[str] = []
    for item_index, item_value in enumerate(items):
        item = _mapping(item_value, f"$.items[{item_index}]")
        item_ids.append(_validate_item(item, item_index))
    if len(set(item_ids)) != len(item_ids):
        raise FoundationModelBridgeError("$.items item_id values must be unique")

    counters = _mapping(payload.get("access_counters"), "$.access_counters")
    _expect_exact_fields(counters, set(ACCESS_COUNTER_FIELDS), "$.access_counters")
    for name in ACCESS_COUNTER_FIELDS:
        if type(counters.get(name)) is not int or counters[name] != 0:
            raise FoundationModelBridgeError(f"$.access_counters.{name} must be integer zero")

    warnings = _sequence(payload.get("warnings"), "$.warnings")
    if list(warnings) != list(ALLOWED_WARNINGS):
        raise FoundationModelBridgeError("$.warnings must equal the frozen synthetic warnings")


def build_ablation_plan(
    evidence: Mapping[str, Any],
    *,
    source_input_bytes: int | None = None,
    source_file_sha256: str | None = None,
) -> dict[str, Any]:
    """Compile deterministic blinded request plans for all four conditions."""

    validate_synthetic_evidence(evidence)
    canonical_evidence = canonical_json_bytes(evidence)
    if source_input_bytes is None:
        source_input_bytes = len(canonical_evidence)
    if type(source_input_bytes) is not int or not 1 <= source_input_bytes <= MAX_INPUT_BYTES:
        raise FoundationModelBridgeError("source_input_bytes must be within the 1 MiB cap")
    if source_file_sha256 is None:
        source_file_sha256 = hashlib.sha256(canonical_evidence).hexdigest()
    if not _is_sha256(source_file_sha256):
        raise FoundationModelBridgeError("source_file_sha256 must be a lowercase SHA-256")

    items = [_mapping(row, "$.items[]") for row in _sequence(evidence["items"], "$.items")]
    item_ids = [str(row["item_id"]) for row in items]
    derangement = {
        item_id: item_ids[(index + 1) % len(item_ids)]
        for index, item_id in enumerate(item_ids)
    }
    item_by_id = {str(row["item_id"]): row for row in items}
    item_evidence_hashes = [
        {
            "item_id": str(row["item_id"]),
            "ctc_nbest_sha256": sha256_json(row["ctc_nbest"]),
            "neural_key_frames_sha256": sha256_json(row["neural_key_frames"]),
        }
        for row in items
    ]
    ctc_hypothesis_count = sum(len(row["ctc_nbest"]) for row in items)
    neural_frame_count = sum(len(row["neural_key_frames"]) for row in items)
    top_key_probability_count = sum(
        len(frame["top_keys"])
        for row in items
        for frame in row["neural_key_frames"]
    )
    condition_rows: list[dict[str, Any]] = []
    for item in items:
        item_id = str(item["item_id"])
        for condition_id in CONDITION_IDS:
            ctc_source = item_id if condition_id != "FM-A00" else None
            neural_source = None
            if condition_id == "FM-A02":
                neural_source = item_id
            elif condition_id == "FM-A03":
                neural_source = derangement[item_id]
            source_for_neural = item_by_id[neural_source] if neural_source is not None else None
            request_payload = {
                "instruction": FIXED_INSTRUCTION,
                "task_context": evidence["task_context"],
                "ctc_nbest": deepcopy(item["ctc_nbest"]) if ctc_source else [],
                "neural_key_frames": (
                    deepcopy(source_for_neural["neural_key_frames"])
                    if source_for_neural is not None
                    else []
                ),
                "response_contract": deepcopy(RESPONSE_CONTRACT),
            }
            condition_rows.append(
                {
                    "condition_id": condition_id,
                    "item_id": item_id,
                    "ctc_source_item_id": ctc_source,
                    "neural_source_item_id": neural_source,
                    "blinded_request_payload": request_payload,
                    "request_sha256": sha256_json(request_payload),
                }
            )

    derangement_rows = [
        {"item_id": item_id, "neural_source_item_id": derangement[item_id]}
        for item_id in item_ids
    ]
    core: dict[str, Any] = {
        "schema_name": PLAN_SCHEMA_NAME,
        "schema_version": PLAN_SCHEMA_VERSION,
        "bridge_id": f"{evidence['fixture_id']}-SOL-V0",
        "proof_posture": "synthetic_no_call_request_plan_only",
        "source": {
            "fixture_id": evidence["fixture_id"],
            "input_bytes": source_input_bytes,
            "file_sha256": source_file_sha256,
            "canonical_sha256": hashlib.sha256(canonical_evidence).hexdigest(),
            "item_count": len(items),
            "ctc_hypothesis_count": ctc_hypothesis_count,
            "neural_frame_count": neural_frame_count,
            "top_key_probability_count": top_key_probability_count,
            "item_evidence_hashes": item_evidence_hashes,
        },
        "model": {
            "provider": PROVIDER,
            "model_id": MODEL_ID,
            "endpoint": ENDPOINT,
            "reasoning_effort": REASONING_EFFORT,
            "structured_output_required": True,
            "tools": [],
            "conversation_state": "independent_item_requests",
            "fine_tuning_used": False,
            "external_call_enabled": False,
            "custom_embedding_injection": False,
        },
        "transport": {
            "status": "not_implemented_no_call",
            "wire_request_materialized": False,
            "api_credential_required_or_read": False,
            "raw_or_dense_neural_content_exported": False,
        },
        "fixed_instruction": FIXED_INSTRUCTION,
        "response_contract": deepcopy(RESPONSE_CONTRACT),
        "derangement": {
            "kind": "fixed_cyclic_next_item",
            "frozen_before_model_outputs_or_targets": True,
            "rows": derangement_rows,
            "rows_sha256": sha256_json(derangement_rows),
        },
        "conditions": condition_rows,
        "condition_counts": {
            condition_id: len(items) for condition_id in CONDITION_IDS
        },
        "access_counters": {name: 0 for name in ACCESS_COUNTER_FIELDS},
        "warnings": [
            "synthetic_fixture_only_no_real_or_protected_content",
            "request_payloads_are_plans_not_provider_wire_requests",
            "no_provider_model_or_training_call_executed",
            "fluency_or_schema_validity_would_not_establish_neural_information",
        ],
        "unavailable_fields": [
            "provider_response",
            "provider_response_id",
            "provider_reported_model",
            "input_tokens",
            "output_tokens",
            "provider_latency_seconds",
            "provider_cost",
            "decoded_text_accuracy",
            "end_to_end_latency",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "deterministic synthetic four-condition request-plan compilation"
            ),
            "scientific_claim_not_established": (
                "no model or real neural evidence ran, so no decoding or neural claim exists"
            ),
        },
    }
    core["plan_core_sha256"] = sha256_json(core)
    validate_ablation_plan(core)
    return core


def validate_ablation_plan(plan: Mapping[str, Any]) -> None:
    """Validate plan structure, blinded payloads, derangement, and hashes."""

    _expect_exact_fields(
        plan,
        {
            "schema_name",
            "schema_version",
            "bridge_id",
            "proof_posture",
            "source",
            "model",
            "transport",
            "fixed_instruction",
            "response_contract",
            "derangement",
            "conditions",
            "condition_counts",
            "access_counters",
            "warnings",
            "unavailable_fields",
            "claim_boundary",
            "plan_core_sha256",
        },
        "$",
    )
    _expect_equal(plan, "schema_name", PLAN_SCHEMA_NAME, "$.schema_name")
    _expect_equal(plan, "schema_version", PLAN_SCHEMA_VERSION, "$.schema_version")
    _expect_equal(
        plan,
        "proof_posture",
        "synthetic_no_call_request_plan_only",
        "$.proof_posture",
    )
    _expect_equal(plan, "fixed_instruction", FIXED_INSTRUCTION, "$.fixed_instruction")
    if plan.get("response_contract") != RESPONSE_CONTRACT:
        raise FoundationModelBridgeError("$.response_contract does not match v0")

    source = _mapping(plan.get("source"), "$.source")
    _expect_exact_fields(
        source,
        {
            "fixture_id",
            "input_bytes",
            "file_sha256",
            "canonical_sha256",
            "item_count",
            "ctc_hypothesis_count",
            "neural_frame_count",
            "top_key_probability_count",
            "item_evidence_hashes",
        },
        "$.source",
    )
    if not _is_sha256(source.get("file_sha256")) or not _is_sha256(
        source.get("canonical_sha256")
    ):
        raise FoundationModelBridgeError("$.source hashes must be lowercase SHA-256")
    if type(source.get("input_bytes")) is not int or not 1 <= source["input_bytes"] <= MAX_INPUT_BYTES:
        raise FoundationModelBridgeError("$.source.input_bytes exceeds the v0 cap")
    item_count = source.get("item_count")
    if type(item_count) is not int or not 2 <= item_count <= MAX_ITEMS:
        raise FoundationModelBridgeError("$.source.item_count is outside the v0 range")
    count_caps = {
        "ctc_hypothesis_count": item_count * MAX_CTC_HYPOTHESES,
        "neural_frame_count": item_count * MAX_NEURAL_FRAMES,
        "top_key_probability_count": item_count * MAX_NEURAL_FRAMES * MAX_TOP_KEYS,
    }
    for name, maximum in count_caps.items():
        value = source.get(name)
        if type(value) is not int or not item_count <= value <= maximum:
            raise FoundationModelBridgeError(f"$.source.{name} is outside the v0 range")
    evidence_hash_rows = list(
        _sequence(source.get("item_evidence_hashes"), "$.source.item_evidence_hashes")
    )
    if len(evidence_hash_rows) != item_count:
        raise FoundationModelBridgeError("$.source.item_evidence_hashes must match item_count")
    evidence_hashes: dict[str, Mapping[str, Any]] = {}
    for index, row_value in enumerate(evidence_hash_rows):
        row_path = f"$.source.item_evidence_hashes[{index}]"
        row = _mapping(row_value, row_path)
        _expect_exact_fields(
            row,
            {"item_id", "ctc_nbest_sha256", "neural_key_frames_sha256"},
            row_path,
        )
        item_id = _nonempty_text(row.get("item_id"), f"{row_path}.item_id")
        if item_id in evidence_hashes:
            raise FoundationModelBridgeError("$.source.item_evidence_hashes has duplicates")
        if not _is_sha256(row.get("ctc_nbest_sha256")) or not _is_sha256(
            row.get("neural_key_frames_sha256")
        ):
            raise FoundationModelBridgeError(f"{row_path} contains an invalid SHA-256")
        evidence_hashes[item_id] = row

    model = _mapping(plan.get("model"), "$.model")
    expected_model = {
        "provider": PROVIDER,
        "model_id": MODEL_ID,
        "endpoint": ENDPOINT,
        "reasoning_effort": REASONING_EFFORT,
        "structured_output_required": True,
        "tools": [],
        "conversation_state": "independent_item_requests",
        "fine_tuning_used": False,
        "external_call_enabled": False,
        "custom_embedding_injection": False,
    }
    if model != expected_model:
        raise FoundationModelBridgeError("$.model must equal the frozen no-call model plan")
    transport = _mapping(plan.get("transport"), "$.transport")
    if transport != {
        "status": "not_implemented_no_call",
        "wire_request_materialized": False,
        "api_credential_required_or_read": False,
        "raw_or_dense_neural_content_exported": False,
    }:
        raise FoundationModelBridgeError("$.transport must remain no-call and target-free")

    derangement = _mapping(plan.get("derangement"), "$.derangement")
    _expect_exact_fields(
        derangement,
        {"kind", "frozen_before_model_outputs_or_targets", "rows", "rows_sha256"},
        "$.derangement",
    )
    _expect_equal(derangement, "kind", "fixed_cyclic_next_item", "$.derangement.kind")
    _expect_equal(
        derangement,
        "frozen_before_model_outputs_or_targets",
        True,
        "$.derangement.frozen_before_model_outputs_or_targets",
    )
    derangement_rows = list(_sequence(derangement.get("rows"), "$.derangement.rows"))
    if derangement.get("rows_sha256") != sha256_json(derangement_rows):
        raise FoundationModelBridgeError("$.derangement.rows_sha256 mismatch")
    if len(derangement_rows) != item_count:
        raise FoundationModelBridgeError("$.derangement rows must match item_count")
    item_ids: list[str] = []
    mapping: dict[str, str] = {}
    for index, row_value in enumerate(derangement_rows):
        row = _mapping(row_value, f"$.derangement.rows[{index}]")
        _expect_exact_fields(row, {"item_id", "neural_source_item_id"}, f"$.derangement.rows[{index}]")
        item_id = _nonempty_text(row.get("item_id"), f"$.derangement.rows[{index}].item_id")
        source_id = _nonempty_text(
            row.get("neural_source_item_id"),
            f"$.derangement.rows[{index}].neural_source_item_id",
        )
        item_ids.append(item_id)
        mapping[item_id] = source_id
    if len(set(item_ids)) != len(item_ids):
        raise FoundationModelBridgeError("$.derangement item identities must be unique")
    if list(evidence_hashes) != item_ids:
        raise FoundationModelBridgeError(
            "$.source.item_evidence_hashes order must match derangement item order"
        )
    for index, item_id in enumerate(item_ids):
        if mapping[item_id] != item_ids[(index + 1) % len(item_ids)]:
            raise FoundationModelBridgeError("$.derangement must be exact cyclic next-item mapping")

    conditions = list(_sequence(plan.get("conditions"), "$.conditions"))
    if len(conditions) != item_count * len(CONDITION_IDS):
        raise FoundationModelBridgeError("$.conditions must contain four rows per item")
    by_item: dict[str, list[Mapping[str, Any]]] = {item_id: [] for item_id in item_ids}
    for index, row_value in enumerate(conditions):
        row = _mapping(row_value, f"$.conditions[{index}]")
        _validate_condition_row(row, index, item_ids, mapping, evidence_hashes)
        by_item[str(row["item_id"])].append(row)
    for item_id, rows in by_item.items():
        if [row["condition_id"] for row in rows] != list(CONDITION_IDS):
            raise FoundationModelBridgeError(f"conditions for {item_id} are not in frozen order")

    expected_counts = {condition_id: item_count for condition_id in CONDITION_IDS}
    if plan.get("condition_counts") != expected_counts:
        raise FoundationModelBridgeError("$.condition_counts mismatch")
    counters = _mapping(plan.get("access_counters"), "$.access_counters")
    _expect_exact_fields(counters, set(ACCESS_COUNTER_FIELDS), "$.access_counters")
    if any(type(counters[name]) is not int or counters[name] != 0 for name in ACCESS_COUNTER_FIELDS):
        raise FoundationModelBridgeError("$.access_counters must all be integer zero")

    expected_hash = plan.get("plan_core_sha256")
    if not _is_sha256(expected_hash):
        raise FoundationModelBridgeError("$.plan_core_sha256 must be a lowercase SHA-256")
    hash_payload = dict(plan)
    del hash_payload["plan_core_sha256"]
    if expected_hash != sha256_json(hash_payload):
        raise FoundationModelBridgeError("$.plan_core_sha256 mismatch")
    if len(canonical_json_bytes(plan)) > MAX_OUTPUT_BYTES:
        raise FoundationModelBridgeError("ablation plan exceeds the 1 MiB output cap")


def make_synthetic_evidence_file(
    path: str | Path,
    *,
    fixture_id: str = "FM-SYNTH-001",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write one bounded synthetic evidence file and return measured telemetry."""

    started = time.perf_counter()
    payload = build_synthetic_evidence_fixture(fixture_id=fixture_id)
    output_bytes = write_bounded_json(path, payload, overwrite=overwrite)
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "make_synthetic_evidence",
        "path": str(Path(path)),
        "fixture_id": fixture_id,
        "item_count": len(payload["items"]),
        "canonical_sha256": sha256_json(payload),
        "file_sha256": _file_sha256(Path(path)),
        "input_bytes": 0,
        "output_bytes": output_bytes,
        "runtime_seconds": round(time.perf_counter() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "access_counters": dict(payload["access_counters"]),
        "end_to_end_latency_measured": False,
        "warnings": list(payload["warnings"]),
    }


def build_ablation_plan_file(
    evidence_path: str | Path,
    out_path: str | Path,
    *,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Compile and write one deterministic four-condition no-call plan."""

    started = time.perf_counter()
    source = Path(evidence_path)
    evidence = load_json_object(source)
    plan = build_ablation_plan(
        evidence,
        source_input_bytes=source.stat().st_size,
        source_file_sha256=_file_sha256(source),
    )
    output_bytes = write_bounded_json(out_path, plan, overwrite=overwrite)
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "build_ablation_plan",
        "path": str(Path(out_path)),
        "source_path": str(source),
        "source_input_bytes": source.stat().st_size,
        "output_bytes": output_bytes,
        "plan_core_sha256": plan["plan_core_sha256"],
        "condition_count": len(plan["conditions"]),
        "condition_counts": dict(plan["condition_counts"]),
        "source_ctc_hypothesis_count": plan["source"]["ctc_hypothesis_count"],
        "source_neural_frame_count": plan["source"]["neural_frame_count"],
        "source_top_key_probability_count": plan["source"]["top_key_probability_count"],
        "runtime_seconds": round(time.perf_counter() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "access_counters": dict(plan["access_counters"]),
        "provider": PROVIDER,
        "model_id": MODEL_ID,
        "producer_causal": True,
        "end_to_end_latency_measured": False,
        "warnings": list(plan["warnings"]),
        "unavailable_fields": list(plan["unavailable_fields"]),
    }


def inspect_ablation_plan_file(path: str | Path) -> dict[str, Any]:
    """Validate and summarize a no-call plan without executing any request."""

    started = time.perf_counter()
    source = Path(path)
    plan = load_json_object(source)
    validate_ablation_plan(plan)
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "inspect_ablation_plan",
        "path": str(source),
        "input_bytes": source.stat().st_size,
        "file_sha256": _file_sha256(source),
        "plan_core_sha256": plan["plan_core_sha256"],
        "source_fixture_id": plan["source"]["fixture_id"],
        "item_count": plan["source"]["item_count"],
        "condition_count": len(plan["conditions"]),
        "condition_counts": dict(plan["condition_counts"]),
        "source_ctc_hypothesis_count": plan["source"]["ctc_hypothesis_count"],
        "source_neural_frame_count": plan["source"]["neural_frame_count"],
        "source_top_key_probability_count": plan["source"]["top_key_probability_count"],
        "runtime_seconds": round(time.perf_counter() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "access_counters": dict(plan["access_counters"]),
        "provider": plan["model"]["provider"],
        "model_id": plan["model"]["model_id"],
        "transport_status": plan["transport"]["status"],
        "external_call_enabled": plan["model"]["external_call_enabled"],
        "fine_tuning_used": plan["model"]["fine_tuning_used"],
        "end_to_end_latency_measured": False,
        "warnings": list(plan["warnings"]),
        "unavailable_fields": list(plan["unavailable_fields"]),
        "claim_boundary": dict(plan["claim_boundary"]),
    }


def load_json_object(path: str | Path, *, maximum_bytes: int = MAX_INPUT_BYTES) -> dict[str, Any]:
    """Load one bounded regular JSON object without following a symlink."""

    source = Path(path)
    if source.is_symlink():
        raise FoundationModelBridgeError(f"refusing symlinked JSON input: {source}")
    if not source.is_file():
        raise FoundationModelBridgeError(f"JSON input is not a regular file: {source}")
    size = source.stat().st_size
    if size > maximum_bytes:
        raise FoundationModelBridgeError(f"JSON input exceeds {maximum_bytes} bytes: {source}")
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FoundationModelBridgeError(f"invalid UTF-8 JSON input: {source}") from exc
    if not isinstance(payload, dict):
        raise FoundationModelBridgeError(f"JSON input must contain one object: {source}")
    return payload


def write_bounded_json(
    path: str | Path,
    payload: Mapping[str, Any],
    *,
    maximum_bytes: int = MAX_OUTPUT_BYTES,
    overwrite: bool = False,
) -> int:
    """Write one inspectable JSON object under the exact v0 byte cap."""

    destination = Path(path)
    if destination.is_symlink():
        raise FoundationModelBridgeError(f"refusing symlinked JSON output: {destination}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing output: {destination}")
    raw = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    encoded = raw.encode("utf-8")
    if len(encoded) > maximum_bytes:
        raise FoundationModelBridgeError(f"JSON output exceeds {maximum_bytes} bytes")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(encoded)
    return len(encoded)


def _fixture_item(
    *,
    item_id: str,
    hypotheses: tuple[tuple[str, float], ...],
    symbols: tuple[str, ...],
) -> dict[str, Any]:
    frames = []
    for index, symbol in enumerate(symbols):
        frames.append(
            {
                "frame_index": index,
                "start_ms": index * 100,
                "end_ms": (index + 1) * 100,
                "available_at_ms": (index + 1) * 100,
                "entropy_nats": round(0.62 + index * 0.04, 2),
                "top_keys": [
                    {"symbol": symbol, "probability": round(0.72 - index * 0.03, 2)},
                    {"symbol": "SPACE", "probability": round(0.12 + index * 0.01, 2)},
                ],
            }
        )
    return {
        "item_id": item_id,
        "split_id": "synthetic-development",
        "ctc_nbest": [
            {"rank": rank, "text": text, "log_probability": score}
            for rank, (text, score) in enumerate(hypotheses, start=1)
        ],
        "neural_key_frames": frames,
        "producer": {
            "source_modality": "synthetic",
            "representation_kind": "structured_key_evidence",
            "producer_causal": True,
            "right_context_ms": 0,
            "supervision_content_included": False,
            "dense_vector_exported": False,
        },
    }


def _validate_item(item: Mapping[str, Any], item_index: int) -> str:
    path = f"$.items[{item_index}]"
    _expect_exact_fields(
        item,
        {"item_id", "split_id", "ctc_nbest", "neural_key_frames", "producer"},
        path,
    )
    item_id = _nonempty_text(item.get("item_id"), f"{path}.item_id")
    if re.fullmatch(r"SYNTH-ITEM-[0-9]{2}", item_id) is None:
        raise FoundationModelBridgeError(f"{path}.item_id must match SYNTH-ITEM-NN")
    _expect_equal(item, "split_id", "synthetic-development", f"{path}.split_id")
    _validate_ctc_nbest(item.get("ctc_nbest"), f"{path}.ctc_nbest")
    _validate_neural_frames(item.get("neural_key_frames"), f"{path}.neural_key_frames")
    producer = _mapping(item.get("producer"), f"{path}.producer")
    expected_producer = {
        "source_modality": "synthetic",
        "representation_kind": "structured_key_evidence",
        "producer_causal": True,
        "right_context_ms": 0,
        "supervision_content_included": False,
        "dense_vector_exported": False,
    }
    if producer != expected_producer:
        raise FoundationModelBridgeError(f"{path}.producer must equal the v0 causal contract")
    return item_id


def _validate_ctc_nbest(value: Any, path: str) -> None:
    rows = list(_sequence(value, path))
    if not 1 <= len(rows) <= MAX_CTC_HYPOTHESES:
        raise FoundationModelBridgeError(
            f"{path} must contain 1 through {MAX_CTC_HYPOTHESES} hypotheses"
        )
    seen_text: set[str] = set()
    previous_score = math.inf
    for index, row_value in enumerate(rows):
        row_path = f"{path}[{index}]"
        row = _mapping(row_value, row_path)
        _expect_exact_fields(row, {"rank", "text", "log_probability"}, row_path)
        if type(row.get("rank")) is not int or row["rank"] != index + 1:
            raise FoundationModelBridgeError(f"{row_path}.rank must be sequential from one")
        text = _nonempty_text(row.get("text"), f"{row_path}.text")
        if len(text) > 256 or re.fullmatch(r"[A-Z ]+", text) is None:
            raise FoundationModelBridgeError(f"{row_path}.text must be bounded uppercase ASCII")
        if text in seen_text:
            raise FoundationModelBridgeError(f"{path} hypothesis text must be unique")
        seen_text.add(text)
        score = _finite_number(row.get("log_probability"), f"{row_path}.log_probability")
        if score > 0 or score > previous_score:
            raise FoundationModelBridgeError(f"{path} log probabilities must be nonincreasing <= 0")
        previous_score = score


def _validate_neural_frames(value: Any, path: str) -> None:
    rows = list(_sequence(value, path))
    if not 1 <= len(rows) <= MAX_NEURAL_FRAMES:
        raise FoundationModelBridgeError(
            f"{path} must contain 1 through {MAX_NEURAL_FRAMES} frames"
        )
    previous_end = 0
    for index, row_value in enumerate(rows):
        row_path = f"{path}[{index}]"
        row = _mapping(row_value, row_path)
        _expect_exact_fields(
            row,
            {
                "frame_index",
                "start_ms",
                "end_ms",
                "available_at_ms",
                "entropy_nats",
                "top_keys",
            },
            row_path,
        )
        if type(row.get("frame_index")) is not int or row["frame_index"] != index:
            raise FoundationModelBridgeError(f"{row_path}.frame_index must be sequential from zero")
        start_ms = _nonnegative_int(row.get("start_ms"), f"{row_path}.start_ms")
        end_ms = _nonnegative_int(row.get("end_ms"), f"{row_path}.end_ms")
        available_at = _nonnegative_int(
            row.get("available_at_ms"), f"{row_path}.available_at_ms"
        )
        if start_ms < previous_end or end_ms <= start_ms:
            raise FoundationModelBridgeError(f"{row_path} timestamps must be ordered and positive")
        if available_at < end_ms:
            raise FoundationModelBridgeError(f"{row_path} uses evidence before it is available")
        previous_end = end_ms
        entropy = _finite_number(row.get("entropy_nats"), f"{row_path}.entropy_nats")
        if not 0 <= entropy <= math.log(len(KEY_SYMBOLS)):
            raise FoundationModelBridgeError(f"{row_path}.entropy_nats is outside the key range")
        top_keys = list(_sequence(row.get("top_keys"), f"{row_path}.top_keys"))
        if not 1 <= len(top_keys) <= MAX_TOP_KEYS:
            raise FoundationModelBridgeError(
                f"{row_path}.top_keys must contain 1 through {MAX_TOP_KEYS} rows"
            )
        symbols: set[str] = set()
        total = 0.0
        previous_probability = math.inf
        for key_index, key_value in enumerate(top_keys):
            key_path = f"{row_path}.top_keys[{key_index}]"
            key = _mapping(key_value, key_path)
            _expect_exact_fields(key, {"symbol", "probability"}, key_path)
            symbol = _nonempty_text(key.get("symbol"), f"{key_path}.symbol")
            if symbol not in KEY_SYMBOLS or symbol in symbols:
                raise FoundationModelBridgeError(f"{key_path}.symbol is invalid or duplicated")
            symbols.add(symbol)
            probability = _finite_number(key.get("probability"), f"{key_path}.probability")
            if not 0 < probability <= 1 or probability > previous_probability:
                raise FoundationModelBridgeError(
                    f"{row_path}.top_keys probabilities must be descending in (0, 1]"
                )
            total += probability
            previous_probability = probability
        if total > 1.0 + 1e-12:
            raise FoundationModelBridgeError(f"{row_path}.top_keys probabilities exceed one")


def _validate_condition_row(
    row: Mapping[str, Any],
    index: int,
    item_ids: list[str],
    mapping: Mapping[str, str],
    evidence_hashes: Mapping[str, Mapping[str, Any]],
) -> None:
    path = f"$.conditions[{index}]"
    _expect_exact_fields(
        row,
        {
            "condition_id",
            "item_id",
            "ctc_source_item_id",
            "neural_source_item_id",
            "blinded_request_payload",
            "request_sha256",
        },
        path,
    )
    condition_id = row.get("condition_id")
    item_id = row.get("item_id")
    if condition_id not in CONDITION_IDS or item_id not in item_ids:
        raise FoundationModelBridgeError(f"{path} has an unknown condition or item")
    expected_ctc = None if condition_id == "FM-A00" else item_id
    expected_neural = None
    if condition_id == "FM-A02":
        expected_neural = item_id
    elif condition_id == "FM-A03":
        expected_neural = mapping[str(item_id)]
    if row.get("ctc_source_item_id") != expected_ctc:
        raise FoundationModelBridgeError(f"{path}.ctc_source_item_id mismatch")
    if row.get("neural_source_item_id") != expected_neural:
        raise FoundationModelBridgeError(f"{path}.neural_source_item_id mismatch")
    payload = _mapping(row.get("blinded_request_payload"), f"{path}.blinded_request_payload")
    _expect_exact_fields(
        payload,
        {"instruction", "task_context", "ctc_nbest", "neural_key_frames", "response_contract"},
        f"{path}.blinded_request_payload",
    )
    _expect_equal(payload, "instruction", FIXED_INSTRUCTION, f"{path}.blinded_request_payload.instruction")
    _expect_equal(
        payload,
        "task_context",
        "synthetic_unprompted_typing_without_reference",
        f"{path}.blinded_request_payload.task_context",
    )
    if payload.get("response_contract") != RESPONSE_CONTRACT:
        raise FoundationModelBridgeError(f"{path}.blinded_request_payload response contract mismatch")
    ctc_rows = list(_sequence(payload.get("ctc_nbest"), f"{path}.blinded_request_payload.ctc_nbest"))
    neural_rows = list(
        _sequence(payload.get("neural_key_frames"), f"{path}.blinded_request_payload.neural_key_frames")
    )
    if (expected_ctc is None) != (len(ctc_rows) == 0):
        raise FoundationModelBridgeError(f"{path} CTC presence does not match condition")
    if (expected_neural is None) != (len(neural_rows) == 0):
        raise FoundationModelBridgeError(f"{path} neural presence does not match condition")
    if ctc_rows:
        _validate_ctc_nbest(ctc_rows, f"{path}.blinded_request_payload.ctc_nbest")
        expected_ctc_hash = evidence_hashes[str(expected_ctc)]["ctc_nbest_sha256"]
        if sha256_json(ctc_rows) != expected_ctc_hash:
            raise FoundationModelBridgeError(f"{path} CTC payload is not source-hash bound")
    if neural_rows:
        _validate_neural_frames(
            neural_rows, f"{path}.blinded_request_payload.neural_key_frames"
        )
        expected_neural_hash = evidence_hashes[str(expected_neural)][
            "neural_key_frames_sha256"
        ]
        if sha256_json(neural_rows) != expected_neural_hash:
            raise FoundationModelBridgeError(f"{path} neural payload is not source-hash bound")
    if any(key in payload for key in ("condition_id", "item_id", "source_item_id")):
        raise FoundationModelBridgeError(f"{path} payload leaks condition or item identity")
    if row.get("request_sha256") != sha256_json(payload):
        raise FoundationModelBridgeError(f"{path}.request_sha256 mismatch")


def _reject_forbidden_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                raise FoundationModelBridgeError(f"{path} contains a non-string JSON key")
            lowered = key.lower()
            for fragment in FORBIDDEN_KEY_FRAGMENTS:
                if fragment in lowered:
                    raise FoundationModelBridgeError(
                        f"{path}.{key} contains forbidden field fragment {fragment!r}"
                    )
            _reject_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_forbidden_keys(child, f"{path}[{index}]")


def _expect_exact_fields(value: Mapping[str, Any], expected: set[str], path: str) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        raise FoundationModelBridgeError(f"{path} missing fields: {', '.join(missing)}")
    if unknown:
        raise FoundationModelBridgeError(f"{path} unknown fields: {', '.join(unknown)}")


def _expect_equal(value: Mapping[str, Any], field: str, expected: Any, path: str) -> None:
    actual = value.get(field)
    strict_scalar = isinstance(expected, (bool, int, float, str))
    if actual != expected or (strict_scalar and type(actual) is not type(expected)):
        raise FoundationModelBridgeError(f"{path} must equal {expected!r}")


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FoundationModelBridgeError(f"{path} must be an object")
    return value


def _sequence(value: Any, path: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise FoundationModelBridgeError(f"{path} must be an array")
    return value


def _nonempty_text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise FoundationModelBridgeError(f"{path} must be nonempty text")
    return value


def _nonnegative_int(value: Any, path: str) -> int:
    if type(value) is not int or value < 0:
        raise FoundationModelBridgeError(f"{path} must be a nonnegative integer")
    return value


def _finite_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise FoundationModelBridgeError(f"{path} must be a finite number")
    result = float(value)
    if not math.isfinite(result):
        raise FoundationModelBridgeError(f"{path} must be a finite number")
    return result


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int | None:
    try:
        import resource
    except ImportError:
        return None
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024
