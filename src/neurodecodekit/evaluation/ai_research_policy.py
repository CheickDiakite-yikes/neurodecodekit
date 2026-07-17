"""Strict synthetic proposal policy for bounded AI-assisted research."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any


POLICY_SCHEMA_NAME = "neurodecodekit.loop55_ai_research_policy"
POLICY_SCHEMA_VERSION = 0
PROPOSAL_SCHEMA_NAME = "neurodecodekit.ai_research_proposal"
PROPOSAL_SCHEMA_VERSION = 0
REPORT_SCHEMA_NAME = "neurodecodekit.ai_research_validation_report"
REPORT_SCHEMA_VERSION = 0
MAX_INPUT_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 1024 * 1024


@dataclass(frozen=True)
class PolicyViolation:
    """One stable proposal-policy rejection."""

    code: str
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": self.message}


@dataclass(frozen=True)
class ProposalValidationReport:
    """Deterministic validation result, separate from runtime telemetry."""

    accepted: bool
    policy_sha256: str
    proposal_sha256: str
    violations: tuple[PolicyViolation, ...]
    proposal_warnings: tuple[str, ...]
    access_counters: Mapping[str, int]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_name": REPORT_SCHEMA_NAME,
            "schema_version": REPORT_SCHEMA_VERSION,
            "proof_posture": "synthetic_policy_validation_only_no_protected_access",
            "accepted": self.accepted,
            "policy_sha256": self.policy_sha256,
            "proposal_sha256": self.proposal_sha256,
            "violations": [row.to_dict() for row in self.violations],
            "proposal_warnings": list(self.proposal_warnings),
            "access_counters": dict(self.access_counters),
            "claim_boundary": (
                "AI proposal governance mechanics only; no neural or decoding claim"
            ),
        }
        payload["validation_core_sha256"] = sha256_json(payload)
        return payload


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize one JSON-compatible value deterministically and reject NaN."""

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


def load_json_object(path: str | Path, *, maximum_bytes: int = MAX_INPUT_BYTES) -> dict[str, Any]:
    """Read one bounded JSON object without resolving any referenced path."""

    source = Path(path)
    if source.is_symlink():
        raise ValueError(f"refusing symlinked JSON input: {source}")
    if not source.is_file():
        raise ValueError(f"JSON input is not a regular file: {source}")
    size = source.stat().st_size
    if size > maximum_bytes:
        raise ValueError(f"JSON input exceeds {maximum_bytes} bytes: {source}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON input must contain one object: {source}")
    return payload


def validate_ai_research_policy(policy: Mapping[str, Any]) -> None:
    """Fail closed when the committed policy cannot govern a proposal."""

    if policy.get("schema_name") != POLICY_SCHEMA_NAME:
        raise ValueError("unsupported AI research policy schema")
    if policy.get("schema_version") != POLICY_SCHEMA_VERSION:
        raise ValueError("unsupported AI research policy version")
    if policy.get("loop_id") != 55:
        raise ValueError("AI research policy must remain bound to Loop 55")

    authorization = _mapping(policy.get("authorization"), "authorization")
    allowed_true = {
        "planning_research_authorized",
        "synthetic_policy_validator_implementation_authorized",
        "synthetic_proposal_validation_authorized",
    }
    for name, value in authorization.items():
        expected = name in allowed_true
        if value is not expected:
            raise ValueError(f"AI research policy authorization mismatch: {name}")

    phases = _sequence(policy.get("phase_sequence"), "phase_sequence")
    if [row.get("eligible_now") for row in phases if isinstance(row, Mapping)] != [
        True,
        False,
        False,
    ]:
        raise ValueError("only the synthetic AI policy phase may be eligible")

    contract = _mapping(policy.get("proposal_contract"), "proposal_contract")
    if contract.get("proposal_schema_name") != PROPOSAL_SCHEMA_NAME:
        raise ValueError("policy proposal schema identity mismatch")
    if contract.get("proposal_schema_version") != PROPOSAL_SCHEMA_VERSION:
        raise ValueError("policy proposal schema version mismatch")
    required = _string_set(contract.get("required_top_level_fields"), "required fields")
    allowed = _string_set(contract.get("allowed_top_level_fields"), "allowed fields")
    if required != allowed:
        raise ValueError("proposal required and allowed top-level fields must match")
    if contract.get("required_input_window_ms") != [-500, 0]:
        raise ValueError("policy must preserve the causal [-500, 0) ms window")
    if contract.get("right_context_ms_required") != 0:
        raise ValueError("policy must require zero right context")
    if contract.get("maximum_trainable_parameters") != 10000:
        raise ValueError("policy must preserve the 10,000-parameter ceiling")

    caps = _mapping(contract.get("synthetic_budget_caps"), "synthetic budget caps")
    exact_caps = {
        "parameter_update_runs": 0,
        "cpu_threads": 1,
        "workers": 1,
    }
    for name, expected in exact_caps.items():
        if caps.get(name) != expected:
            raise ValueError(f"synthetic budget cap mismatch: {name}")
    if _plain_int(caps.get("maximum_runtime_seconds")) > 30:
        raise ValueError("synthetic runtime cap exceeds 30 seconds")
    if _plain_int(caps.get("maximum_peak_rss_bytes")) > 256 * 1024**2:
        raise ValueError("synthetic RSS cap exceeds 256 MiB")
    if _plain_int(caps.get("maximum_generated_output_bytes")) > MAX_REPORT_BYTES:
        raise ValueError("synthetic output cap exceeds 1 MiB")


def load_ai_research_policy(path: str | Path) -> dict[str, Any]:
    """Load and validate one committed AI research policy."""

    policy = load_json_object(path)
    validate_ai_research_policy(policy)
    return policy


def build_synthetic_proposal(
    policy: Mapping[str, Any],
    *,
    proposal_id: str = "L55-AI-SYNTH-001",
    pretraining_objective: str = "masked_reconstruction",
) -> dict[str, Any]:
    """Build one deterministic synthetic proposal without model execution."""

    validate_ai_research_policy(policy)
    contract = _mapping(policy["proposal_contract"], "proposal_contract")
    fixed = _mapping(contract["synthetic_fixed_values"], "synthetic_fixed_values")
    caps = _mapping(contract["synthetic_budget_caps"], "synthetic_budget_caps")
    counter_names = _string_sequence(contract["access_counter_fields"], "access counters")
    mask_fraction = 0.15 if pretraining_objective == "masked_reconstruction" else 0.0
    return {
        "schema_name": PROPOSAL_SCHEMA_NAME,
        "schema_version": PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id,
        "phase_id": fixed["phase_id"],
        "objective_id": fixed["objective_id"],
        "agent_role": fixed["agent_role"],
        "observation_scope": fixed["observation_scope"],
        "representation_recipe": {
            "family": contract["representation_family"],
            "pretraining_objective": pretraining_objective,
            "input_window_ms": list(contract["required_input_window_ms"]),
            "right_endpoint_exclusive": True,
            "right_context_ms": 0,
            "producer_causal": True,
            "trainable_parameters": 8192,
            "uses_target_text": False,
            "uses_performed_labels_during_pretraining": False,
            "uses_pretrained_weights": False,
            "uses_language_model": False,
        },
        "search_parameters": {
            "learning_rate": 0.001,
            "weight_decay": 0.0001,
            "dropout": 0.1,
            "temporal_kernel_samples": 9,
            "mask_fraction": mask_fraction,
            "hand_loss_weight": 1.0,
        },
        "requested_budget": {
            "proposal_round": 1,
            "parameter_update_runs": 0,
            "cpu_threads": 1,
            "workers": 1,
            "maximum_runtime_seconds": caps["maximum_runtime_seconds"],
            "maximum_peak_rss_bytes": caps["maximum_peak_rss_bytes"],
            "maximum_generated_output_bytes": caps["maximum_generated_output_bytes"],
        },
        "access_counters": {name: 0 for name in counter_names},
        "claim_boundary": fixed["claim_boundary"],
        "warnings": ["synthetic_fixture_only_no_real_or_protected_access"],
    }


def validate_ai_research_proposal(
    proposal: Mapping[str, Any], policy: Mapping[str, Any]
) -> ProposalValidationReport:
    """Validate an untrusted synthetic proposal without executing it."""

    validate_ai_research_policy(policy)
    contract = _mapping(policy["proposal_contract"], "proposal_contract")
    violations: list[PolicyViolation] = []

    required = _string_set(contract["required_top_level_fields"], "required fields")
    _check_exact_fields(proposal, required, "$", "V001", violations)
    _check_equal(proposal, "schema_name", PROPOSAL_SCHEMA_NAME, "$.schema_name", "V002", violations)
    _check_equal(
        proposal,
        "schema_version",
        PROPOSAL_SCHEMA_VERSION,
        "$.schema_version",
        "V003",
        violations,
    )

    proposal_id = proposal.get("proposal_id")
    pattern = str(contract["proposal_id_pattern"])
    if not isinstance(proposal_id, str) or re.fullmatch(pattern, proposal_id) is None:
        _add(violations, "V004", "$.proposal_id", "proposal ID does not match synthetic pattern")

    fixed = _mapping(contract["synthetic_fixed_values"], "synthetic fixed values")
    for field, expected in fixed.items():
        _check_equal(proposal, field, expected, f"$.{field}", "V005", violations)

    recipe = _proposal_mapping(proposal, "representation_recipe", violations)
    recipe_fields = _string_set(contract["representation_recipe_fields"], "recipe fields")
    _check_exact_fields(recipe, recipe_fields, "$.representation_recipe", "V006", violations)
    _check_equal(
        recipe,
        "family",
        contract["representation_family"],
        "$.representation_recipe.family",
        "V007",
        violations,
    )
    if recipe.get("pretraining_objective") not in contract["allowed_pretraining_objectives"]:
        _add(
            violations,
            "V008",
            "$.representation_recipe.pretraining_objective",
            "pretraining objective is outside the frozen menu",
        )
    _check_equal(
        recipe,
        "input_window_ms",
        contract["required_input_window_ms"],
        "$.representation_recipe.input_window_ms",
        "V009",
        violations,
    )
    _check_equal(
        recipe,
        "right_endpoint_exclusive",
        True,
        "$.representation_recipe.right_endpoint_exclusive",
        "V010",
        violations,
    )
    _check_equal(
        recipe,
        "right_context_ms",
        0,
        "$.representation_recipe.right_context_ms",
        "V011",
        violations,
    )
    _check_equal(
        recipe,
        "producer_causal",
        True,
        "$.representation_recipe.producer_causal",
        "V012",
        violations,
    )
    parameters = recipe.get("trainable_parameters")
    if (
        not _is_plain_int(parameters)
        or parameters < 1
        or parameters > contract["maximum_trainable_parameters"]
    ):
        _add(
            violations,
            "V013",
            "$.representation_recipe.trainable_parameters",
            "trainable parameters must be an integer from 1 through 10,000",
        )
    for field in contract["required_false_recipe_fields"]:
        _check_equal(recipe, field, False, f"$.representation_recipe.{field}", "V014", violations)

    search = _proposal_mapping(proposal, "search_parameters", violations)
    search_fields = _string_set(contract["search_parameter_fields"], "search fields")
    _check_exact_fields(search, search_fields, "$.search_parameters", "V015", violations)
    menu = _mapping(contract["search_parameter_menu"], "search parameter menu")
    for field, allowed_values in menu.items():
        value = search.get(field)
        if isinstance(value, bool) or value not in allowed_values:
            _add(
                violations,
                "V016",
                f"$.search_parameters.{field}",
                "search value is outside the frozen menu",
            )
    objective = recipe.get("pretraining_objective")
    mask_fraction = search.get("mask_fraction")
    if objective == "masked_reconstruction" and mask_fraction not in (0.15, 0.3):
        _add(
            violations,
            "V017",
            "$.search_parameters.mask_fraction",
            "masked reconstruction requires a positive frozen mask fraction",
        )
    if objective in ("none", "contrastive_next_window") and mask_fraction != 0.0:
        _add(
            violations,
            "V018",
            "$.search_parameters.mask_fraction",
            "this pretraining objective requires zero mask fraction",
        )

    budget = _proposal_mapping(proposal, "requested_budget", violations)
    budget_fields = _string_set(contract["requested_budget_fields"], "budget fields")
    _check_exact_fields(budget, budget_fields, "$.requested_budget", "V019", violations)
    caps = _mapping(contract["synthetic_budget_caps"], "synthetic budget caps")
    round_value = budget.get("proposal_round")
    if (
        not _is_plain_int(round_value)
        or round_value < caps["proposal_round_minimum"]
        or round_value > caps["proposal_round_maximum"]
    ):
        _add(violations, "V020", "$.requested_budget.proposal_round", "proposal round exceeds bounds")
    for field in ("parameter_update_runs", "cpu_threads", "workers"):
        _check_equal(budget, field, caps[field], f"$.requested_budget.{field}", "V021", violations)
    for field in (
        "maximum_runtime_seconds",
        "maximum_peak_rss_bytes",
        "maximum_generated_output_bytes",
    ):
        value = budget.get(field)
        if not _is_plain_int(value) or value < 1 or value > caps[field]:
            _add(
                violations,
                "V022",
                f"$.requested_budget.{field}",
                "requested resource must be a positive integer within the synthetic cap",
            )

    counters = _proposal_mapping(proposal, "access_counters", violations)
    counter_fields = _string_set(contract["access_counter_fields"], "access counter fields")
    _check_exact_fields(counters, counter_fields, "$.access_counters", "V023", violations)
    for field in counter_fields:
        if counters.get(field) != 0 or isinstance(counters.get(field), bool):
            _add(
                violations,
                "V024",
                f"$.access_counters.{field}",
                "synthetic proposal access counters must all be integer zero",
            )

    warnings = proposal.get("warnings")
    allowed_warnings = set(contract["allowed_warning_values"])
    if (
        not isinstance(warnings, list)
        or len(warnings) < contract["warnings_minimum_count"]
        or len(warnings) > contract["warnings_maximum_count"]
        or any(not isinstance(item, str) or item not in allowed_warnings for item in warnings)
    ):
        _add(violations, "V025", "$.warnings", "warnings must use only frozen safe values")

    safe_warnings = (
        tuple(item for item in warnings if isinstance(item, str) and item in allowed_warnings)
        if isinstance(warnings, list)
        else ()
    )
    safe_counters = {
        field: value
        for field, value in counters.items()
        if field in counter_fields and _is_plain_int(value)
    }
    return ProposalValidationReport(
        accepted=not violations,
        policy_sha256=sha256_json(policy),
        proposal_sha256=sha256_json(proposal),
        violations=tuple(violations),
        proposal_warnings=safe_warnings,
        access_counters=safe_counters,
    )


def inspect_ai_research_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact public policy summary."""

    validate_ai_research_policy(policy)
    contract = _mapping(policy["proposal_contract"], "proposal_contract")
    budget = _mapping(policy["future_fit_budget_recommendation"], "future fit budget")
    return {
        "schema_name": "neurodecodekit.ai_research_policy_summary",
        "schema_version": 0,
        "policy_sha256": sha256_json(policy),
        "loop_id": policy["loop_id"],
        "status": policy["status"],
        "eligible_phase": "L55-AI-A_synthetic_policy_rehearsal_only",
        "primary_endpoint": policy["scientific_objective"]["fixed_primary_endpoint"],
        "maximum_trainable_parameters": contract["maximum_trainable_parameters"],
        "maximum_future_fit_runs": budget["maximum_total_parameter_update_runs"],
        "maximum_future_ai_proposal_runs": budget[
            "maximum_ai_guided_train_inner_proposal_runs"
        ],
        "allowed_pretraining_objectives": list(contract["allowed_pretraining_objectives"]),
        "real_or_protected_execution_authorized": False,
        "claim_boundary": policy["claim_boundary"],
        "warnings": list(policy["current_warnings"]),
        "unavailable_fields": list(policy["current_unavailable_fields"]),
    }


def build_validation_envelope(
    policy_path: str | Path, proposal_path: str | Path
) -> dict[str, Any]:
    """Validate named files and add nonidentity operational telemetry."""

    start = time.perf_counter()
    policy_source = Path(policy_path)
    proposal_source = Path(proposal_path)
    policy = load_ai_research_policy(policy_source)
    proposal = load_json_object(proposal_source)
    report = validate_ai_research_proposal(proposal, policy).to_dict()
    report["measurements"] = {
        "policy_input_bytes": policy_source.stat().st_size,
        "proposal_input_bytes": proposal_source.stat().st_size,
        "validation_core_bytes": len(canonical_json_bytes(report)),
        "runtime_seconds": round(time.perf_counter() - start, 9),
        "peak_rss_bytes": _peak_rss_bytes(),
        "raw_data_reads": 0,
        "real_cache_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "end_to_end_latency_measured": False,
    }
    return report


def write_bounded_json(
    path: str | Path,
    payload: Mapping[str, Any],
    *,
    maximum_bytes: int = MAX_REPORT_BYTES,
    overwrite: bool = False,
) -> int:
    """Write one inspectable JSON file under an exact byte cap."""

    destination = Path(path)
    if destination.is_symlink():
        raise ValueError(f"refusing symlinked JSON output: {destination}")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing output: {destination}")
    raw = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    encoded = raw.encode("utf-8")
    if len(encoded) > maximum_bytes:
        raise ValueError(f"JSON output exceeds {maximum_bytes} bytes")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(encoded)
    return len(encoded)


def _proposal_mapping(
    proposal: Mapping[str, Any], field: str, violations: list[PolicyViolation]
) -> Mapping[str, Any]:
    value = proposal.get(field)
    if not isinstance(value, Mapping):
        _add(violations, "V000", f"$.{field}", "field must be an object")
        return {}
    return value


def _check_exact_fields(
    value: Mapping[str, Any],
    expected: set[str],
    path: str,
    code: str,
    violations: list[PolicyViolation],
) -> None:
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        _add(violations, code, path, f"missing fields: {', '.join(missing)}")
    if unknown:
        _add(violations, code, path, f"unknown fields: {', '.join(unknown)}")


def _check_equal(
    value: Mapping[str, Any],
    field: str,
    expected: Any,
    path: str,
    code: str,
    violations: list[PolicyViolation],
) -> None:
    actual = value.get(field)
    strict_scalar = isinstance(expected, (bool, int, float, str))
    if actual != expected or (strict_scalar and type(actual) is not type(expected)):
        _add(violations, code, path, f"must equal {expected!r}")


def _add(
    violations: list[PolicyViolation], code: str, path: str, message: str
) -> None:
    violations.append(PolicyViolation(code=f"L55-AI-{code}", path=path, message=message))


def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be an object")
    return value


def _sequence(value: Any, name: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{name} must be an array")
    return value


def _string_sequence(value: Any, name: str) -> list[str]:
    rows = list(_sequence(value, name))
    if any(not isinstance(row, str) or not row for row in rows):
        raise ValueError(f"{name} must contain only nonempty strings")
    if len(set(rows)) != len(rows):
        raise ValueError(f"{name} must not contain duplicates")
    return rows


def _string_set(value: Any, name: str) -> set[str]:
    return set(_string_sequence(value, name))


def _is_plain_int(value: Any) -> bool:
    return type(value) is int


def _plain_int(value: Any) -> int:
    if not _is_plain_int(value):
        raise ValueError("expected an integer policy value")
    return value


def _peak_rss_bytes() -> int | None:
    try:
        import resource
    except ImportError:
        return None
    peak = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return peak if sys.platform == "darwin" else peak * 1024
