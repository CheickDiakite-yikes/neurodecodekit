"""Bounded FM-1 provider transport over the committed synthetic FM-0 plan."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.evaluation.foundation_model_bridge import (
    build_ablation_plan,
    canonical_json_bytes,
    load_json_object,
    validate_ablation_plan,
    write_bounded_json,
)


CONTRACT_RELATIVE_PATH = Path("registries/foundation_model_live_smoke_contract.v0.json")
DECISION_RELATIVE_PATH = Path(
    "registries/foundation_model_live_smoke_authorization_decision.v0.json"
)
FIXTURE_RELATIVE_PATH = Path("fixtures/foundation_model_bridge_synthetic_evidence.v0.json")
CONTRACT_SHA256 = "30dd5fc7475f4985e97f496166792a65d0f2e9353230652cb5c2526c74f86eae"
DECISION_SHA256 = "01ba69b0fc1e1c3e372721076de4b75de9a9c92541d73fa4a95f8e56491b3295"
CONTRACT_COMMIT = "7db14d51cbe8bde5a5d7ac43479b20e575e9ae7c"
CONTRACT_PUSH_CI_RUN_ID = 31267860543
DECISION_COMMIT = "04fc00987d2c68827054acaac32ab6edfae5430b"
DECISION_PUSH_CI_RUN_ID = 31268358553
RESULT_SCHEMA_NAME = "neurodecodekit.foundation_model_live_smoke_result"
RESULT_SCHEMA_VERSION = "0.1.0"
SUMMARY_SCHEMA_NAME = "neurodecodekit.foundation_model_live_smoke_summary"
SUMMARY_SCHEMA_VERSION = "0.1.0"
API_KEY_ENVIRONMENT_VARIABLE = "OPENAI_API_KEY"
EXPECTED_MODEL_ID = "gpt-5.6-terra"
EXPECTED_ENDPOINT = "https://api.openai.com/v1/responses"
EXPECTED_PLAN_CORE_SHA256 = "355e018f6cd33d7a0d8213fa20eb0798f571c84e4c2e5a2f84dff33ed6c47b5d"
EXPECTED_PLAN_FILE_SHA256 = "66f7af99c418945ac878608a64203277e1c7413680e0fd9c5af93f1b5b07d3be"
EXPECTED_PLAN_BYTES = 34349
EXPECTED_FIXTURE_SHA256 = "12f1b68f3241c80e4ba54872a3c97769e666ad2342f84328b1a5df91f0089bdb"
EXPECTED_CONDITION_COUNT = 12
CONDITION_IDS = ("FM-A00", "FM-A01", "FM-A02", "FM-A03")
THREAD_ENVIRONMENT_VARIABLES = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
PROVIDER_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "decoded_text",
        "abstained",
        "evidence_used",
        "unsupported_content_warning",
    ],
    "properties": {
        "decoded_text": {"type": "string", "maxLength": 256},
        "abstained": {"type": "boolean"},
        "evidence_used": {"type": "string", "enum": ["none", "ctc", "ctc_and_neural"]},
        "unsupported_content_warning": {"type": "boolean"},
    },
}
RESULT_ACCESS_COUNTER_FIELDS = (
    "external_network_calls",
    "API_credential_reads",
    "provider_spend_events",
    "provider_model_calls",
    "real_or_protected_data_reads",
    "target_or_reference_reads",
    "raw_or_dense_neural_uploads",
    "training_runs",
    "fine_tuning_runs",
    "scoring_runs",
)
RESULT_WARNINGS = (
    "synthetic_fixture_only_no_real_or_protected_content",
    "no_targets_references_accuracy_scoring_or_model_selection",
    "provider_outputs_are_nondeterministic_and_this_stage_has_no_rerun",
    "descriptive_output_changes_are_not_neural_or_decoding_evidence",
)
RESULT_UNAVAILABLE_FIELDS = (
    "decoded_text_accuracy",
    "CER",
    "WER",
    "neural_advantage",
    "brain_specific_information",
    "real_signal_latency",
    "end_to_end_capture_latency",
    "unseen_person_generalization",
)
RESULT_CLAIM_BOUNDARY = {
    "engineering_capability": (
        "bounded synthetic provider transport and strict response parsing for the exact matrix"
    ),
    "scientific_claim_not_established": (
        "no target or real neural evidence was used, so no decoding or neural claim exists"
    ),
}


class FoundationModelLiveRefusal(RuntimeError):
    """Raised before the one-shot provider invocation can begin."""


class FoundationModelLiveFailure(RuntimeError):
    """Raised for a consumed provider call failure without exposing response content."""

    def __init__(
        self,
        category: str,
        detail: str,
        *,
        wire_response_bytes: int = 0,
        provider_response_sha256: str | None = None,
    ) -> None:
        super().__init__(detail)
        self.category = category
        self.wire_response_bytes = wire_response_bytes
        self.provider_response_sha256 = provider_response_sha256


@dataclass(frozen=True)
class ExecutionEvidence:
    """Remote-green implementation evidence supplied to the one-shot runner."""

    implementation_commit: str
    implementation_push_ci_run_id: int


@dataclass(frozen=True)
class WireRequest:
    """One locally identified request whose provider payload remains blinded."""

    condition_id: str
    item_id: str
    plan_request_sha256: str
    body: bytes
    body_sha256: str


@dataclass(frozen=True)
class LiveContext:
    """Locked contract, source plan, and bounded provider request set."""

    contract: Mapping[str, Any]
    decision: Mapping[str, Any]
    plan: Mapping[str, Any]
    wire_requests: tuple[WireRequest, ...]


Transport = Callable[[bytes, str, int, int], bytes]


def repository_root() -> Path:
    """Return the checkout root without consulting the current directory."""

    return Path(__file__).resolve().parents[3]


def build_live_context(repo_root: str | Path | None = None) -> LiveContext:
    """Rebuild and verify the frozen FM-0 plan without credential or network access."""

    root = Path(repo_root) if repo_root is not None else repository_root()
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    _validate_contract_and_decision(contract, decision)

    fixture_path = root / FIXTURE_RELATIVE_PATH
    if fixture_path.is_symlink() or not fixture_path.is_file():
        raise FoundationModelLiveRefusal("the locked FM-0 fixture must be a regular file")
    fixture_bytes = fixture_path.read_bytes()
    if hashlib.sha256(fixture_bytes).hexdigest() != EXPECTED_FIXTURE_SHA256:
        raise FoundationModelLiveRefusal("the locked FM-0 fixture hash does not match")
    evidence = load_json_object(fixture_path)
    plan = build_ablation_plan(
        evidence,
        source_input_bytes=len(fixture_bytes),
        source_file_sha256=EXPECTED_FIXTURE_SHA256,
    )
    validate_ablation_plan(plan)
    plan_bytes = _pretty_json_bytes(plan)
    if len(plan_bytes) != EXPECTED_PLAN_BYTES:
        raise FoundationModelLiveRefusal("the rebuilt FM-0 plan byte count does not match")
    if hashlib.sha256(plan_bytes).hexdigest() != EXPECTED_PLAN_FILE_SHA256:
        raise FoundationModelLiveRefusal("the rebuilt FM-0 plan file hash does not match")
    if plan.get("plan_core_sha256") != EXPECTED_PLAN_CORE_SHA256:
        raise FoundationModelLiveRefusal("the rebuilt FM-0 plan-core hash does not match")

    wire_requests = tuple(_build_wire_request(row, contract) for row in plan["conditions"])
    if len(wire_requests) != EXPECTED_CONDITION_COUNT:
        raise FoundationModelLiveRefusal("the FM-1 request count must equal exactly 12")
    request_cap = contract["resource_caps"]["maximum_wire_request_bytes_per_call"]
    total_cap = contract["resource_caps"]["maximum_total_wire_request_bytes"]
    if any(len(row.body) > request_cap for row in wire_requests):
        raise FoundationModelLiveRefusal("a provider request exceeds the per-call byte cap")
    if sum(len(row.body) for row in wire_requests) > total_cap:
        raise FoundationModelLiveRefusal("provider requests exceed the total byte cap")
    return LiveContext(
        contract=contract,
        decision=decision,
        plan=plan,
        wire_requests=wire_requests,
    )


def dry_run_summary(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the exact zero-network execution plan and all zero access counters."""

    started = time.perf_counter()
    context = build_live_context(repo_root)
    request_sizes = [len(row.body) for row in context.wire_requests]
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "dry_run",
        "stage_id": "FM-1",
        "mode": "dry_run_no_credential_read_no_network",
        "contract_sha256": CONTRACT_SHA256,
        "decision_sha256": DECISION_SHA256,
        "source_plan_core_sha256": EXPECTED_PLAN_CORE_SHA256,
        "source_plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "source_plan_bytes": EXPECTED_PLAN_BYTES,
        "model_id": EXPECTED_MODEL_ID,
        "endpoint": EXPECTED_ENDPOINT,
        "request_count": len(context.wire_requests),
        "condition_counts": {
            condition_id: sum(
                row.condition_id == condition_id for row in context.wire_requests
            )
            for condition_id in CONDITION_IDS
        },
        "minimum_wire_request_bytes": min(request_sizes),
        "maximum_wire_request_bytes": max(request_sizes),
        "total_wire_request_bytes": sum(request_sizes),
        "maximum_total_output_tokens": context.contract["resource_caps"][
            "maximum_total_output_tokens"
        ],
        "maximum_estimated_standard_provider_charge_usd": context.contract[
            "resource_caps"
        ]["maximum_standard_provider_charge_usd"],
        "runtime_seconds": round(time.perf_counter() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "access_counters": {name: 0 for name in RESULT_ACCESS_COUNTER_FIELDS},
        "warnings": [
            "synthetic_fixture_only",
            "wire_requests_materialized_locally_but_not_sent",
            "no_credential_read_network_call_model_call_or_spend_occurred",
            "provider_outputs_and_end_to_end_latency_remain_unavailable",
        ],
        "claim_boundary": (
            "dry-run verifies only the locked provider interface; no model or scientific result exists"
        ),
    }


def execute_live_smoke(
    out_path: str | Path,
    *,
    evidence: ExecutionEvidence,
    repo_root: str | Path | None = None,
    transport: Transport | None = None,
) -> dict[str, Any]:
    """Consume one bounded live invocation after all local and remote-green gates."""

    root = Path(repo_root) if repo_root is not None else repository_root()
    context = build_live_context(root)
    destination = Path(out_path)
    _verify_execution_evidence(root, evidence)
    _verify_output_preflight(root, destination, context.contract)
    api_key = _read_api_key_once()
    result = execute_context_with_transport(
        context,
        api_key=api_key,
        transport=transport or _openai_transport,
        implementation_evidence=evidence,
    )
    output_bytes = write_bounded_json(
        destination,
        result,
        maximum_bytes=context.contract["resource_caps"]["maximum_generated_result_bytes"],
    )
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "execute",
        "stage_id": "FM-1",
        "status": result["status"],
        "result_sha256": _file_sha256(destination),
        "output_bytes": output_bytes,
        "request_count": result["request_count"],
        "completed_response_count": result["completed_response_count"],
        "schema_valid_response_count": result["schema_valid_response_count"],
        "refusal_count": result["refusal_count"],
        "input_tokens": result["usage"]["input_tokens"],
        "output_tokens": result["usage"]["output_tokens"],
        "estimated_standard_cost_usd": result["estimated_standard_cost_usd"],
        "runtime_seconds": result["runtime_seconds"],
        "peak_rss_bytes": result["peak_rss_bytes"],
        "access_counters": dict(result["access_counters"]),
        "warnings": list(result["warnings"]),
        "claim_boundary": dict(result["claim_boundary"]),
    }


def execute_context_with_transport(
    context: LiveContext,
    *,
    api_key: str,
    transport: Transport,
    implementation_evidence: ExecutionEvidence,
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    """Execute the exact matrix once using an injected transport and sanitized outputs."""

    if not isinstance(api_key, str) or not api_key:
        raise FoundationModelLiveRefusal("the API credential is missing or empty")
    caps = context.contract["resource_caps"]
    started = clock()
    responses: list[dict[str, Any]] = []
    counters = {name: 0 for name in RESULT_ACCESS_COUNTER_FIELDS}
    counters["API_credential_reads"] = 1
    wire_response_bytes = 0
    terminal_failure: dict[str, Any] | None = None

    for request_index, row in enumerate(context.wire_requests):
        if clock() - started > caps["maximum_wall_seconds"]:
            terminal_failure = {
                "request_index": request_index,
                "category": "wall_time_cap_exceeded_before_call",
                "wire_response_bytes": 0,
                "provider_response_sha256": None,
            }
            break
        counters["external_network_calls"] += 1
        counters["provider_model_calls"] += 1
        counters["provider_spend_events"] += 1
        call_started = clock()
        response_count_before_call = len(responses)
        raw_response: bytes | None = None
        try:
            raw_response = transport(
                row.body,
                api_key,
                caps["request_timeout_seconds"],
                caps["maximum_wire_response_bytes_per_call"],
            )
            wire_response_bytes += len(raw_response)
            if len(raw_response) > caps["maximum_wire_response_bytes_per_call"]:
                raise FoundationModelLiveFailure(
                    "response_byte_cap_exceeded",
                    "provider response exceeded the registered byte cap",
                )
            if wire_response_bytes > caps["maximum_total_wire_response_bytes"]:
                raise FoundationModelLiveFailure(
                    "total_response_byte_cap_exceeded",
                    "provider responses exceeded the total registered byte cap",
                )
            parsed = _parse_provider_response(raw_response)
            parsed.update(
                {
                    "request_index": request_index,
                    "condition_id": row.condition_id,
                    "item_id": row.item_id,
                    "plan_request_sha256": row.plan_request_sha256,
                    "wire_request_sha256": row.body_sha256,
                    "wire_request_bytes": len(row.body),
                    "wire_response_bytes": len(raw_response),
                    "latency_seconds": round(clock() - call_started, 9),
                }
            )
            responses.append(parsed)
            _enforce_cumulative_result_caps(responses, context.contract)
        except FoundationModelLiveFailure as exc:
            failed_response_bytes = 0
            failed_response_sha256 = None
            if len(responses) == response_count_before_call:
                if raw_response is not None:
                    failed_response_bytes = len(raw_response)
                    failed_response_sha256 = hashlib.sha256(raw_response).hexdigest()
                else:
                    failed_response_bytes = exc.wire_response_bytes
                    failed_response_sha256 = exc.provider_response_sha256
                    wire_response_bytes += failed_response_bytes
            terminal_failure = {
                "request_index": request_index,
                "category": exc.category,
                "wire_response_bytes": failed_response_bytes,
                "provider_response_sha256": failed_response_sha256,
            }
            break
        if clock() - started > caps["maximum_wall_seconds"]:
            terminal_failure = {
                "request_index": request_index,
                "category": "wall_time_cap_exceeded_after_call",
                "wire_response_bytes": 0,
                "provider_response_sha256": None,
            }
            break
        if _peak_rss_bytes() > caps["maximum_peak_rss_bytes"]:
            terminal_failure = {
                "request_index": request_index,
                "category": "peak_rss_cap_exceeded",
                "wire_response_bytes": 0,
                "provider_response_sha256": None,
            }
            break

    usage = _sum_usage(responses)
    estimated_cost = _estimated_standard_cost_usd(usage)
    status = "passed" if len(responses) == EXPECTED_CONDITION_COUNT and terminal_failure is None else "parked"
    result = {
        "schema_name": RESULT_SCHEMA_NAME,
        "schema_version": RESULT_SCHEMA_VERSION,
        "stage_id": "FM-1",
        "status": status,
        "consumed": True,
        "rerun_authorized": False,
        "contract_sha256": CONTRACT_SHA256,
        "decision_sha256": DECISION_SHA256,
        "contract_commit": CONTRACT_COMMIT,
        "contract_push_CI_run_id": CONTRACT_PUSH_CI_RUN_ID,
        "decision_commit": DECISION_COMMIT,
        "decision_push_CI_run_id": DECISION_PUSH_CI_RUN_ID,
        "implementation_commit": implementation_evidence.implementation_commit,
        "implementation_push_CI_run_id": implementation_evidence.implementation_push_ci_run_id,
        "source_plan_core_sha256": EXPECTED_PLAN_CORE_SHA256,
        "source_plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "executed_model_id": EXPECTED_MODEL_ID,
        "provider_reported_models": sorted(
            {row["provider_reported_model"] for row in responses if row["provider_reported_model"]}
        ),
        "request_count": counters["provider_model_calls"],
        "completed_response_count": sum(row["status"] == "completed" for row in responses),
        "schema_valid_response_count": sum(row["schema_valid"] for row in responses),
        "refusal_count": sum(row["refused"] for row in responses),
        "usage": usage,
        "estimated_standard_cost_usd": estimated_cost,
        "wire_request_bytes": sum(
            len(row.body) for row in context.wire_requests[: counters["provider_model_calls"]]
        ),
        "wire_response_bytes": wire_response_bytes,
        "runtime_seconds": round(clock() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "responses": responses,
        "condition_summaries": _condition_summaries(responses),
        "descriptive_pairing": _descriptive_pairing(responses),
        "terminal_failure": terminal_failure,
        "access_counters": counters,
        "warnings": list(RESULT_WARNINGS),
        "unavailable_fields": list(RESULT_UNAVAILABLE_FIELDS),
        "claim_boundary": dict(RESULT_CLAIM_BOUNDARY),
    }
    validate_live_result(result, context.contract, context.wire_requests)
    if len(_pretty_json_bytes(result)) > caps["maximum_generated_result_bytes"]:
        raise FoundationModelLiveFailure(
            "generated_result_cap_exceeded",
            "sanitized result exceeds the registered generated-output cap",
        )
    return result


def inspect_live_result(
    path: str | Path,
    *,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Validate and summarize a sanitized FM-1 result without provider access."""

    started = time.perf_counter()
    context = build_live_context(repo_root)
    source = Path(path)
    payload = load_json_object(
        source,
        maximum_bytes=context.contract["resource_caps"]["maximum_generated_result_bytes"],
    )
    validate_live_result(payload, context.contract, context.wire_requests)
    return {
        "schema_name": SUMMARY_SCHEMA_NAME,
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "operation": "inspect_result",
        "stage_id": "FM-1",
        "status": payload["status"],
        "consumed": payload["consumed"],
        "result_bytes": source.stat().st_size,
        "result_sha256": _file_sha256(source),
        "request_count": payload["request_count"],
        "completed_response_count": payload["completed_response_count"],
        "schema_valid_response_count": payload["schema_valid_response_count"],
        "refusal_count": payload["refusal_count"],
        "input_tokens": payload["usage"]["input_tokens"],
        "output_tokens": payload["usage"]["output_tokens"],
        "estimated_standard_cost_usd": payload["estimated_standard_cost_usd"],
        "runtime_seconds": round(time.perf_counter() - started, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "access_counters": dict(payload["access_counters"]),
        "warnings": list(payload["warnings"]),
        "claim_boundary": dict(payload["claim_boundary"]),
    }


def validate_live_result(
    result: Mapping[str, Any],
    contract: Mapping[str, Any],
    wire_requests: Sequence[WireRequest] | None = None,
) -> None:
    """Fail closed on malformed, expanded, over-budget, or non-synthetic results."""

    expected_fields = {
        "schema_name",
        "schema_version",
        "stage_id",
        "status",
        "consumed",
        "rerun_authorized",
        "contract_sha256",
        "decision_sha256",
        "contract_commit",
        "contract_push_CI_run_id",
        "decision_commit",
        "decision_push_CI_run_id",
        "implementation_commit",
        "implementation_push_CI_run_id",
        "source_plan_core_sha256",
        "source_plan_file_sha256",
        "executed_model_id",
        "provider_reported_models",
        "request_count",
        "completed_response_count",
        "schema_valid_response_count",
        "refusal_count",
        "usage",
        "estimated_standard_cost_usd",
        "wire_request_bytes",
        "wire_response_bytes",
        "runtime_seconds",
        "peak_rss_bytes",
        "responses",
        "condition_summaries",
        "descriptive_pairing",
        "terminal_failure",
        "access_counters",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    _expect_exact_fields(result, expected_fields, "$")
    if result.get("schema_name") != RESULT_SCHEMA_NAME:
        raise FoundationModelLiveRefusal("result schema name mismatch")
    if result.get("schema_version") != RESULT_SCHEMA_VERSION or result.get("stage_id") != "FM-1":
        raise FoundationModelLiveRefusal("result schema version or stage mismatch")
    if result.get("status") not in {"passed", "parked"}:
        raise FoundationModelLiveRefusal("result status must be passed or parked")
    if result.get("consumed") is not True or result.get("rerun_authorized") is not False:
        raise FoundationModelLiveRefusal("FM-1 result must be consumed with no rerun")
    fixed_values = {
        "contract_sha256": CONTRACT_SHA256,
        "decision_sha256": DECISION_SHA256,
        "contract_commit": CONTRACT_COMMIT,
        "contract_push_CI_run_id": CONTRACT_PUSH_CI_RUN_ID,
        "decision_commit": DECISION_COMMIT,
        "decision_push_CI_run_id": DECISION_PUSH_CI_RUN_ID,
        "source_plan_core_sha256": EXPECTED_PLAN_CORE_SHA256,
        "source_plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
        "executed_model_id": EXPECTED_MODEL_ID,
    }
    for name, expected in fixed_values.items():
        if result.get(name) != expected or type(result.get(name)) is not type(expected):
            raise FoundationModelLiveRefusal(f"result {name} mismatch")
    if not _is_sha256_commit(result.get("implementation_commit")):
        raise FoundationModelLiveRefusal("result implementation commit must be a full SHA")
    if type(result.get("implementation_push_CI_run_id")) is not int or result[
        "implementation_push_CI_run_id"
    ] <= 0:
        raise FoundationModelLiveRefusal("result implementation CI run must be positive")

    responses = _sequence(result.get("responses"), "$.responses")
    request_count = _bounded_int(result.get("request_count"), "$.request_count", 0, 12)
    if len(responses) != result.get("completed_response_count"):
        raise FoundationModelLiveRefusal("every stored response must be completed")
    if len(responses) > request_count:
        raise FoundationModelLiveRefusal("stored responses cannot exceed attempted requests")
    if result.get("status") == "passed" and (request_count != 12 or len(responses) != 12):
        raise FoundationModelLiveRefusal("a passed result requires all 12 responses")
    if result.get("status") == "parked" and result.get("terminal_failure") is None:
        raise FoundationModelLiveRefusal("a parked result requires a terminal failure")
    if result.get("status") == "passed" and result.get("terminal_failure") is not None:
        raise FoundationModelLiveRefusal("a passed result cannot have a terminal failure")

    valid_count = 0
    refusal_count = 0
    observed_pairs: set[tuple[str, str]] = set()
    for index, response_value in enumerate(responses):
        response = _mapping(response_value, f"$.responses[{index}]")
        _validate_sanitized_response(response, index)
        if wire_requests is not None:
            expected_wire = wire_requests[index]
            expected_fields = {
                "item_id": expected_wire.item_id,
                "condition_id": expected_wire.condition_id,
                "plan_request_sha256": expected_wire.plan_request_sha256,
                "wire_request_sha256": expected_wire.body_sha256,
                "wire_request_bytes": len(expected_wire.body),
            }
            for name, expected in expected_fields.items():
                if response.get(name) != expected:
                    raise FoundationModelLiveRefusal(
                        f"$.responses[{index}].{name} is not bound to the frozen request"
                    )
        pair = (str(response["item_id"]), str(response["condition_id"]))
        if pair in observed_pairs:
            raise FoundationModelLiveRefusal("result contains a duplicate item-condition pair")
        observed_pairs.add(pair)
        valid_count += int(response["schema_valid"])
        refusal_count += int(response["refused"])
    if result.get("schema_valid_response_count") != valid_count:
        raise FoundationModelLiveRefusal("schema-valid count mismatch")
    if result.get("refusal_count") != refusal_count:
        raise FoundationModelLiveRefusal("refusal count mismatch")

    usage = _mapping(result.get("usage"), "$.usage")
    expected_usage = _sum_usage([dict(row) for row in responses])
    if usage != expected_usage:
        raise FoundationModelLiveRefusal("result usage aggregate mismatch")
    expected_cost = _estimated_standard_cost_usd(expected_usage)
    if result.get("estimated_standard_cost_usd") != expected_cost:
        raise FoundationModelLiveRefusal("result estimated cost mismatch")
    caps = contract["resource_caps"]
    terminal_category = _terminal_failure_category(result.get("terminal_failure"))
    _allow_only_parked_cap_failure(
        exceeded=expected_usage["output_tokens"] > caps["maximum_total_output_tokens"],
        result=result,
        terminal_category=terminal_category,
        allowed_categories={"output_token_cap_exceeded"},
        message="result output-token cap exceeded without a matching parked failure",
    )
    _allow_only_parked_cap_failure(
        exceeded=expected_cost > caps["maximum_standard_provider_charge_usd"],
        result=result,
        terminal_category=terminal_category,
        allowed_categories={"provider_charge_cap_exceeded", "output_token_cap_exceeded"},
        message="result provider-charge cap exceeded without a matching parked failure",
    )
    if result.get("wire_request_bytes", 0) > caps["maximum_total_wire_request_bytes"]:
        raise FoundationModelLiveRefusal("result request-byte cap exceeded")
    terminal_response_bytes = 0
    if result.get("terminal_failure") is not None:
        terminal_response_bytes = int(result["terminal_failure"]["wire_response_bytes"])
    if result.get("wire_response_bytes") != (
        sum(int(row["wire_response_bytes"]) for row in responses)
        + terminal_response_bytes
    ):
        raise FoundationModelLiveRefusal("result response-byte aggregate mismatch")
    if wire_requests is not None:
        expected_request_bytes = sum(
            len(row.body) for row in wire_requests[:request_count]
        )
        if result.get("wire_request_bytes") != expected_request_bytes:
            raise FoundationModelLiveRefusal("result request-byte aggregate mismatch")
    _allow_only_parked_cap_failure(
        exceeded=result.get("wire_response_bytes", 0)
        > caps["maximum_total_wire_response_bytes"],
        result=result,
        terminal_category=terminal_category,
        allowed_categories={"total_response_byte_cap_exceeded"},
        message="result response-byte cap exceeded without a matching parked failure",
    )
    _allow_only_parked_cap_failure(
        exceeded=result.get("runtime_seconds", 0) > caps["maximum_wall_seconds"],
        result=result,
        terminal_category=terminal_category,
        allowed_categories={
            "wall_time_cap_exceeded_before_call",
            "wall_time_cap_exceeded_after_call",
        },
        message="result wall-time cap exceeded without a matching parked failure",
    )
    _allow_only_parked_cap_failure(
        exceeded=result.get("peak_rss_bytes", 0) > caps["maximum_peak_rss_bytes"],
        result=result,
        terminal_category=terminal_category,
        allowed_categories={"peak_rss_cap_exceeded"},
        message="result peak-RSS cap exceeded without a matching parked failure",
    )

    counters = _mapping(result.get("access_counters"), "$.access_counters")
    _expect_exact_fields(counters, set(RESULT_ACCESS_COUNTER_FIELDS), "$.access_counters")
    expected_counters = {
        "external_network_calls": request_count,
        "API_credential_reads": 1,
        "provider_spend_events": request_count,
        "provider_model_calls": request_count,
        "real_or_protected_data_reads": 0,
        "target_or_reference_reads": 0,
        "raw_or_dense_neural_uploads": 0,
        "training_runs": 0,
        "fine_tuning_runs": 0,
        "scoring_runs": 0,
    }
    if counters != expected_counters:
        raise FoundationModelLiveRefusal("result access counters mismatch")
    if request_count > contract["resource_caps"]["maximum_provider_requests"]:
        raise FoundationModelLiveRefusal("result request-count cap exceeded")
    if result.get("provider_reported_models") != sorted(
        {row["provider_reported_model"] for row in responses if row["provider_reported_model"]}
    ):
        raise FoundationModelLiveRefusal("provider model aggregate mismatch")
    if result.get("condition_summaries") != _condition_summaries(responses):
        raise FoundationModelLiveRefusal("result condition summaries mismatch")
    if result.get("descriptive_pairing") != _descriptive_pairing(responses):
        raise FoundationModelLiveRefusal("result descriptive pairing mismatch")
    if result.get("warnings") != list(RESULT_WARNINGS):
        raise FoundationModelLiveRefusal("result warnings mismatch")
    if result.get("unavailable_fields") != list(RESULT_UNAVAILABLE_FIELDS):
        raise FoundationModelLiveRefusal("result unavailable fields mismatch")
    if result.get("claim_boundary") != RESULT_CLAIM_BOUNDARY:
        raise FoundationModelLiveRefusal("result claim boundary mismatch")


def _build_wire_request(row: Mapping[str, Any], contract: Mapping[str, Any]) -> WireRequest:
    payload = _mapping(row.get("blinded_request_payload"), "$.conditions[].blinded_request_payload")
    evidence_packet = {
        "task_context": payload["task_context"],
        "ctc_nbest": payload["ctc_nbest"],
        "neural_key_frames": payload["neural_key_frames"],
    }
    provider = contract["provider_contract"]
    body = {
        "model": provider["model_id"],
        "instructions": payload["instruction"],
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": canonical_json_bytes(evidence_packet).decode("ascii"),
                    }
                ],
            }
        ],
        "reasoning": {"effort": provider["reasoning_effort"]},
        "max_output_tokens": provider["maximum_output_tokens_per_request"],
        "service_tier": provider["service_tier"],
        "store": provider["store"],
        "stream": provider["stream"],
        "tools": provider["tools"],
        "text": {
            "verbosity": provider["text_verbosity"],
            "format": {
                "type": "json_schema",
                "name": "neurodecodekit_fm1_result",
                "strict": True,
                "schema": PROVIDER_OUTPUT_SCHEMA,
            },
        },
    }
    encoded = canonical_json_bytes(body)
    decoded = encoded.decode("ascii")
    if row.get("condition_id") in decoded or row.get("item_id") in decoded:
        raise FoundationModelLiveRefusal("provider request leaks condition or item identity")
    for forbidden in (
        "target_text",
        "reference_text",
        "intended_text",
        "raw_eeg",
        "raw_meg",
        "neurotoken",
        "embedding",
        "participant_name",
        "local_path",
    ):
        if forbidden in decoded.lower():
            raise FoundationModelLiveRefusal(
                f"provider request contains forbidden content marker {forbidden}"
            )
    return WireRequest(
        condition_id=str(row["condition_id"]),
        item_id=str(row["item_id"]),
        plan_request_sha256=str(row["request_sha256"]),
        body=encoded,
        body_sha256=hashlib.sha256(encoded).hexdigest(),
    )


def _parse_provider_response(raw: bytes) -> dict[str, Any]:
    response_sha256 = hashlib.sha256(raw).hexdigest()
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FoundationModelLiveFailure(
            "invalid_provider_JSON",
            "provider response was not valid UTF-8 JSON",
        ) from exc
    if not isinstance(payload, dict):
        raise FoundationModelLiveFailure(
            "invalid_provider_object",
            "provider response must be a JSON object",
        )
    status = payload.get("status")
    if status != "completed":
        raise FoundationModelLiveFailure(
            "provider_response_not_completed",
            "provider response status was not completed",
        )
    provider_model = payload.get("model")
    if not isinstance(provider_model, str) or not provider_model.startswith(EXPECTED_MODEL_ID):
        raise FoundationModelLiveFailure(
            "provider_model_mismatch",
            "provider reported a model outside the registered Terra identity",
        )
    try:
        usage = _parse_usage(payload.get("usage"))
    except FoundationModelLiveRefusal as exc:
        raise FoundationModelLiveFailure(
            "invalid_usage",
            "provider usage did not match the bounded numeric contract",
        ) from exc
    output_texts: list[str] = []
    refused = False
    output = payload.get("output")
    if not isinstance(output, list):
        raise FoundationModelLiveFailure("missing_output", "provider output must be an array")
    for item in output:
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for part in content:
            if not isinstance(part, dict):
                continue
            if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                output_texts.append(part["text"])
            if part.get("type") == "refusal":
                refused = True
    if refused:
        return {
            "status": "completed",
            "provider_reported_model": provider_model,
            "provider_response_sha256": response_sha256,
            "schema_valid": False,
            "refused": True,
            "parsed_output": None,
            "usage": usage,
        }
    if len(output_texts) != 1:
        raise FoundationModelLiveFailure(
            "output_text_count_mismatch",
            "provider response must contain exactly one output_text part",
        )
    try:
        parsed_output = json.loads(output_texts[0])
    except json.JSONDecodeError as exc:
        raise FoundationModelLiveFailure(
            "structured_output_invalid_JSON",
            "provider structured output was not valid JSON",
        ) from exc
    try:
        _validate_provider_output(parsed_output)
    except FoundationModelLiveRefusal as exc:
        raise FoundationModelLiveFailure(
            "structured_output_schema_mismatch",
            "provider structured output did not match the registered schema",
        ) from exc
    return {
        "status": "completed",
        "provider_reported_model": provider_model,
        "provider_response_sha256": response_sha256,
        "schema_valid": True,
        "refused": False,
        "parsed_output": parsed_output,
        "usage": usage,
    }


def _parse_usage(value: Any) -> dict[str, int]:
    usage = _mapping(value, "$.usage")
    input_tokens = _bounded_int(usage.get("input_tokens"), "$.usage.input_tokens", 0, 1_000_000)
    output_tokens = _bounded_int(
        usage.get("output_tokens"), "$.usage.output_tokens", 0, 1_000_000
    )
    input_details = usage.get("input_tokens_details")
    output_details = usage.get("output_tokens_details")
    cached_tokens = 0
    cache_write_tokens = 0
    reasoning_tokens = 0
    if isinstance(input_details, Mapping):
        cached_tokens = _bounded_int(
            input_details.get("cached_tokens", 0),
            "$.usage.input_tokens_details.cached_tokens",
            0,
            input_tokens,
        )
        cache_write_tokens = _bounded_int(
            input_details.get("cache_write_tokens", 0),
            "$.usage.input_tokens_details.cache_write_tokens",
            0,
            input_tokens,
        )
    if cached_tokens + cache_write_tokens > input_tokens:
        raise FoundationModelLiveFailure(
            "invalid_usage",
            "cached and cache-write tokens exceed input tokens",
        )
    if isinstance(output_details, Mapping):
        reasoning_tokens = _bounded_int(
            output_details.get("reasoning_tokens", 0),
            "$.usage.output_tokens_details.reasoning_tokens",
            0,
            output_tokens,
        )
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached_tokens,
        "cache_write_input_tokens": cache_write_tokens,
        "output_tokens": output_tokens,
        "reasoning_tokens": reasoning_tokens,
    }


def _validate_provider_output(value: Any) -> None:
    output = _mapping(value, "provider_output")
    _expect_exact_fields(
        output,
        {
            "decoded_text",
            "abstained",
            "evidence_used",
            "unsupported_content_warning",
        },
        "provider_output",
    )
    decoded_text = output.get("decoded_text")
    if not isinstance(decoded_text, str) or len(decoded_text) > 256:
        raise FoundationModelLiveRefusal("provider_output.decoded_text is invalid")
    if type(output.get("abstained")) is not bool:
        raise FoundationModelLiveRefusal("provider_output.abstained must be Boolean")
    if output.get("evidence_used") not in {"none", "ctc", "ctc_and_neural"}:
        raise FoundationModelLiveRefusal("provider_output.evidence_used is invalid")
    if type(output.get("unsupported_content_warning")) is not bool:
        raise FoundationModelLiveRefusal(
            "provider_output.unsupported_content_warning must be Boolean"
        )


def _validate_sanitized_response(response: Mapping[str, Any], index: int) -> None:
    path = f"$.responses[{index}]"
    _expect_exact_fields(
        response,
        {
            "status",
            "provider_reported_model",
            "provider_response_sha256",
            "schema_valid",
            "refused",
            "parsed_output",
            "usage",
            "request_index",
            "condition_id",
            "item_id",
            "plan_request_sha256",
            "wire_request_sha256",
            "wire_request_bytes",
            "wire_response_bytes",
            "latency_seconds",
        },
        path,
    )
    if response.get("status") != "completed" or response.get("request_index") != index:
        raise FoundationModelLiveRefusal(f"{path} status or request index mismatch")
    if response.get("condition_id") not in CONDITION_IDS:
        raise FoundationModelLiveRefusal(f"{path} condition is invalid")
    if not isinstance(response.get("item_id"), str) or re.fullmatch(
        r"SYNTH-ITEM-[0-9]{2}", response["item_id"]
    ) is None:
        raise FoundationModelLiveRefusal(f"{path} item identity is invalid")
    for hash_field in (
        "provider_response_sha256",
        "plan_request_sha256",
        "wire_request_sha256",
    ):
        if not _is_sha256(response.get(hash_field)):
            raise FoundationModelLiveRefusal(f"{path}.{hash_field} is invalid")
    if not isinstance(response.get("provider_reported_model"), str) or not response[
        "provider_reported_model"
    ].startswith(EXPECTED_MODEL_ID):
        raise FoundationModelLiveRefusal(f"{path} provider model mismatch")
    if type(response.get("schema_valid")) is not bool or type(response.get("refused")) is not bool:
        raise FoundationModelLiveRefusal(f"{path} schema/refusal flags must be Boolean")
    if response["refused"]:
        if response["schema_valid"] or response.get("parsed_output") is not None:
            raise FoundationModelLiveRefusal(f"{path} refusal fields are inconsistent")
    else:
        if not response["schema_valid"]:
            raise FoundationModelLiveRefusal(f"{path} non-refusal must be schema-valid")
        _validate_provider_output(response.get("parsed_output"))
    parsed_usage = _parse_usage(
        {
            "input_tokens": response["usage"].get("input_tokens"),
            "output_tokens": response["usage"].get("output_tokens"),
            "input_tokens_details": {
                "cached_tokens": response["usage"].get("cached_input_tokens"),
                "cache_write_tokens": response["usage"].get("cache_write_input_tokens"),
            },
            "output_tokens_details": {
                "reasoning_tokens": response["usage"].get("reasoning_tokens")
            },
        }
    )
    if parsed_usage != response["usage"]:
        raise FoundationModelLiveRefusal(f"{path} usage is invalid")
    for field in ("wire_request_bytes", "wire_response_bytes"):
        _bounded_int(response.get(field), f"{path}.{field}", 1, 262144)
    latency = response.get("latency_seconds")
    if isinstance(latency, bool) or not isinstance(latency, (int, float)) or latency < 0:
        raise FoundationModelLiveRefusal(f"{path}.latency_seconds is invalid")


def _condition_summaries(responses: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for condition_id in CONDITION_IDS:
        rows = [row for row in responses if row["condition_id"] == condition_id]
        summaries[condition_id] = {
            "response_count": len(rows),
            "schema_valid_count": sum(row["schema_valid"] for row in rows),
            "refusal_count": sum(row["refused"] for row in rows),
            "abstained_count": sum(
                bool(row["parsed_output"]["abstained"])
                for row in rows
                if row["parsed_output"] is not None
            ),
            "nonempty_decoded_text_count": sum(
                bool(row["parsed_output"]["decoded_text"])
                for row in rows
                if row["parsed_output"] is not None
            ),
        }
    return summaries


def _descriptive_pairing(responses: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_pair = {
        (str(row["item_id"]), str(row["condition_id"])): row
        for row in responses
        if row.get("parsed_output") is not None
    }
    item_ids = sorted({item_id for item_id, _ in by_pair})
    ctc_vs_matched_comparable = 0
    ctc_vs_matched_changed = 0
    matched_vs_deranged_comparable = 0
    matched_vs_deranged_changed = 0
    for item_id in item_ids:
        ctc = by_pair.get((item_id, "FM-A01"))
        matched = by_pair.get((item_id, "FM-A02"))
        deranged = by_pair.get((item_id, "FM-A03"))
        if ctc is not None and matched is not None:
            ctc_vs_matched_comparable += 1
            ctc_vs_matched_changed += int(
                ctc["parsed_output"]["decoded_text"]
                != matched["parsed_output"]["decoded_text"]
            )
        if matched is not None and deranged is not None:
            matched_vs_deranged_comparable += 1
            matched_vs_deranged_changed += int(
                matched["parsed_output"]["decoded_text"]
                != deranged["parsed_output"]["decoded_text"]
            )
    return {
        "CTC_only_vs_matched_comparable_items": ctc_vs_matched_comparable,
        "CTC_only_vs_matched_changed_text_items": ctc_vs_matched_changed,
        "matched_vs_deranged_comparable_items": matched_vs_deranged_comparable,
        "matched_vs_deranged_changed_text_items": matched_vs_deranged_changed,
        "interpretation": "descriptive synthetic output sensitivity only; no correctness direction exists",
    }


def _sum_usage(responses: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    fields = (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_tokens",
    )
    return {field: sum(int(row["usage"][field]) for row in responses) for field in fields}


def _estimated_standard_cost_usd(usage: Mapping[str, int]) -> float:
    cached = usage["cached_input_tokens"]
    cache_write = usage["cache_write_input_tokens"]
    ordinary = max(0, usage["input_tokens"] - cached - cache_write)
    cost = ordinary * 2.0 + cached * 0.2 + cache_write * 2.5 + usage["output_tokens"] * 12.0
    return round(cost / 1_000_000, 9)


def _enforce_cumulative_result_caps(
    responses: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> None:
    caps = contract["resource_caps"]
    usage = _sum_usage(responses)
    if usage["output_tokens"] > caps["maximum_total_output_tokens"]:
        raise FoundationModelLiveFailure(
            "output_token_cap_exceeded",
            "provider output tokens exceeded the registered cap",
        )
    if _estimated_standard_cost_usd(usage) > caps["maximum_standard_provider_charge_usd"]:
        raise FoundationModelLiveFailure(
            "provider_charge_cap_exceeded",
            "estimated provider charge exceeded the registered cap",
        )


def _terminal_failure_category(value: Any) -> str | None:
    if value is None:
        return None
    failure = _mapping(value, "$.terminal_failure")
    _expect_exact_fields(
        failure,
        {
            "request_index",
            "category",
            "wire_response_bytes",
            "provider_response_sha256",
        },
        "$.terminal_failure",
    )
    _bounded_int(failure.get("request_index"), "$.terminal_failure.request_index", 0, 11)
    category = failure.get("category")
    if not isinstance(category, str) or re.fullmatch(r"[a-zA-Z0-9_.-]{1,200}", category) is None:
        raise FoundationModelLiveRefusal("$.terminal_failure.category is invalid")
    response_bytes = _bounded_int(
        failure.get("wire_response_bytes"),
        "$.terminal_failure.wire_response_bytes",
        0,
        262145,
    )
    response_sha256 = failure.get("provider_response_sha256")
    if response_bytes == 0 and response_sha256 is not None:
        raise FoundationModelLiveRefusal(
            "$.terminal_failure response hash requires response bytes"
        )
    if response_bytes > 0 and not _is_sha256(response_sha256):
        raise FoundationModelLiveRefusal(
            "$.terminal_failure response bytes require a SHA-256"
        )
    if response_bytes > 262144 and category != "response_byte_cap_exceeded":
        raise FoundationModelLiveRefusal(
            "$.terminal_failure oversized response category mismatch"
        )
    return category


def _allow_only_parked_cap_failure(
    *,
    exceeded: bool,
    result: Mapping[str, Any],
    terminal_category: str | None,
    allowed_categories: set[str],
    message: str,
) -> None:
    if exceeded and not (
        result.get("status") == "parked" and terminal_category in allowed_categories
    ):
        raise FoundationModelLiveRefusal(message)


def _openai_transport(body: bytes, api_key: str, timeout: int, maximum_bytes: int) -> bytes:
    request = urllib.request.Request(
        EXPECTED_ENDPOINT,
        data=body,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "identity",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            encoding = response.headers.get("Content-Encoding")
            if encoding not in (None, "identity"):
                raise FoundationModelLiveFailure(
                    "unexpected_content_encoding",
                    "provider response used an unexpected content encoding",
                )
            raw = response.read(maximum_bytes + 1)
    except urllib.error.HTTPError as exc:
        try:
            raw_error = exc.read(maximum_bytes + 1)
        except Exception:  # noqa: BLE001 - never surface raw provider error details
            raw_error = b""
        if len(raw_error) > maximum_bytes:
            raise FoundationModelLiveFailure(
                "response_byte_cap_exceeded",
                "provider error response exceeded the registered byte cap",
                wire_response_bytes=len(raw_error),
                provider_response_sha256=hashlib.sha256(raw_error).hexdigest(),
            ) from None
        category = _sanitized_provider_error_category(raw_error, exc.code)
        raise FoundationModelLiveFailure(
            category,
            "provider returned an HTTP error",
            wire_response_bytes=len(raw_error),
            provider_response_sha256=(
                hashlib.sha256(raw_error).hexdigest() if raw_error else None
            ),
        ) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        category = "provider_timeout" if isinstance(exc, TimeoutError) else "provider_transport_error"
        raise FoundationModelLiveFailure(category, "provider transport failed") from None
    if len(raw) > maximum_bytes:
        raise FoundationModelLiveFailure(
            "response_byte_cap_exceeded",
            "provider response exceeded the registered byte cap",
            wire_response_bytes=len(raw),
            provider_response_sha256=hashlib.sha256(raw).hexdigest(),
        )
    return raw


def _sanitized_provider_error_category(raw: bytes, status_code: int) -> str:
    provider_type = "unknown"
    provider_code = "unknown"
    try:
        payload = json.loads(raw)
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            if isinstance(error.get("type"), str):
                provider_type = re.sub(r"[^a-zA-Z0-9_.-]", "_", error["type"])[:64]
            if isinstance(error.get("code"), str):
                provider_code = re.sub(r"[^a-zA-Z0-9_.-]", "_", error["code"])[:64]
    except (UnicodeDecodeError, json.JSONDecodeError):
        pass
    return f"provider_http_{status_code}_{provider_type}_{provider_code}"


def _verify_execution_evidence(repo_root: Path, evidence: ExecutionEvidence) -> None:
    if not _is_sha256_commit(evidence.implementation_commit):
        raise FoundationModelLiveRefusal("implementation commit must be a full lowercase Git SHA")
    if evidence.implementation_commit in {CONTRACT_COMMIT, DECISION_COMMIT}:
        raise FoundationModelLiveRefusal("implementation commit must follow the decision commit")
    if evidence.implementation_push_ci_run_id <= 0:
        raise FoundationModelLiveRefusal("implementation push CI run ID must be positive")

    head = _git(repo_root, "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != evidence.implementation_commit:
        raise FoundationModelLiveRefusal("current HEAD does not equal the implementation commit")
    ancestor = _git(repo_root, "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD")
    if ancestor.returncode:
        raise FoundationModelLiveRefusal("implementation commit does not descend from the decision")
    tracked = _git(repo_root, "status", "--porcelain", "--untracked-files=no")
    if tracked.returncode or tracked.stdout.strip():
        raise FoundationModelLiveRefusal("tracked worktree must be clean before execution")
    remote = _git(repo_root, "branch", "-r", "--contains", evidence.implementation_commit)
    if remote.returncode or "origin/" not in remote.stdout:
        raise FoundationModelLiveRefusal("implementation commit is not present on an origin branch")


def _verify_output_preflight(
    repo_root: Path, destination: Path, contract: Mapping[str, Any]
) -> None:
    if destination.is_symlink():
        raise FoundationModelLiveRefusal("refusing symlinked FM-1 output")
    if destination.exists():
        raise FoundationModelLiveRefusal("FM-1 output already exists; rerun is forbidden")
    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(parent).free < contract["resource_caps"]["minimum_free_disk_bytes"]:
        raise FoundationModelLiveRefusal("less than one GiB free disk remains")
    if _peak_rss_bytes() > contract["resource_caps"]["maximum_peak_rss_bytes"]:
        raise FoundationModelLiveRefusal(
            "process peak RSS already exceeds the registered cap"
        )
    for name in THREAD_ENVIRONMENT_VARIABLES:
        value = os.environ.get(name)
        if value not in (None, "1"):
            raise FoundationModelLiveRefusal(f"{name} must be unset or equal one")
    if not repo_root.is_dir():
        raise FoundationModelLiveRefusal("repository root is not a directory")


def _read_api_key_once() -> str:
    value = os.environ.get(API_KEY_ENVIRONMENT_VARIABLE)
    if not isinstance(value, str) or not value:
        raise FoundationModelLiveRefusal("OPENAI_API_KEY is missing or empty")
    return value


def _validate_contract_and_decision(
    contract: Mapping[str, Any], decision: Mapping[str, Any]
) -> None:
    if contract.get("schema_name") != "neurodecodekit.foundation_model_live_smoke_contract":
        raise FoundationModelLiveRefusal("FM-1 contract schema mismatch")
    if contract.get("status") != "preregistered_not_authorized_not_implemented_not_executed":
        raise FoundationModelLiveRefusal("FM-1 contract status mismatch")
    if decision.get("schema_name") != (
        "neurodecodekit.foundation_model_live_smoke_authorization_decision"
    ):
        raise FoundationModelLiveRefusal("FM-1 decision schema mismatch")
    if decision.get("status") != "authorized_pending_implementation_and_execution":
        raise FoundationModelLiveRefusal("FM-1 decision status mismatch")
    if decision.get("exact_authorization_text") != contract.get("exact_authorization_request"):
        raise FoundationModelLiveRefusal("FM-1 exact authorization text mismatch")
    binding = _mapping(decision.get("contract_binding"), "$.contract_binding")
    if binding.get("contract_sha256") != CONTRACT_SHA256:
        raise FoundationModelLiveRefusal("FM-1 decision contract hash mismatch")
    if binding.get("contract_commit") != CONTRACT_COMMIT:
        raise FoundationModelLiveRefusal("FM-1 decision contract commit mismatch")
    if binding.get("contract_push_CI_run_id") != CONTRACT_PUSH_CI_RUN_ID:
        raise FoundationModelLiveRefusal("FM-1 decision contract CI mismatch")
    provider = _mapping(contract.get("provider_contract"), "$.provider_contract")
    expected_provider_fields = {
        "model_id": EXPECTED_MODEL_ID,
        "endpoint": EXPECTED_ENDPOINT,
        "reasoning_effort": "low",
        "service_tier": "default",
        "store": False,
        "stream": False,
        "tools": [],
        "maximum_output_tokens_per_request": 256,
        "retry_count": 0,
    }
    for name, expected in expected_provider_fields.items():
        if provider.get(name) != expected or type(provider.get(name)) is not type(expected):
            raise FoundationModelLiveRefusal(f"FM-1 provider field {name} mismatch")


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise FoundationModelLiveRefusal(f"locked JSON must be a regular file: {path.name}")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise FoundationModelLiveRefusal(f"locked JSON hash mismatch: {path.name}")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FoundationModelLiveRefusal(f"locked JSON is invalid: {path.name}") from exc
    if not isinstance(payload, dict):
        raise FoundationModelLiveRefusal(f"locked JSON must contain an object: {path.name}")
    return payload


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", *args),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise FoundationModelLiveRefusal(f"{path} must be an object")
    return value


def _sequence(value: Any, path: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise FoundationModelLiveRefusal(f"{path} must be an array")
    return value


def _expect_exact_fields(value: Mapping[str, Any], expected: set[str], path: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        raise FoundationModelLiveRefusal(f"{path} missing fields: {', '.join(missing)}")
    if unknown:
        raise FoundationModelLiveRefusal(f"{path} unknown fields: {', '.join(unknown)}")


def _bounded_int(value: Any, path: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise FoundationModelLiveRefusal(f"{path} must be an integer in [{minimum}, {maximum}]")
    return value


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _is_sha256_commit(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _pretty_json_bytes(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    try:
        import resource
    except ImportError:
        return 0
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024
