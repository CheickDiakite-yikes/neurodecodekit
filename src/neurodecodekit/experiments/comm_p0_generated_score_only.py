"""Standard-library-only aggregate score worker for generated COMM-P0 records.

This module is intentionally capability-poor.  It accepts already-frozen mapping
records, holds generated targets only inside the scoring call, and emits no row-level
prediction, probability, target, or participant outcome.
"""

from __future__ import annotations

import hashlib
import json
import math
import types
from collections import defaultdict
from collections.abc import Mapping, Sequence
from statistics import median
from typing import Any

SCHEMA_VERSION = "0.1.0"
ENDPOINTS = ("prompted_intend", "free_choice_intend")
COHORTS = ("discovery", "independent_replication")
LIVE_COHORT = "independent_replication"
LIVE_PHASE = "live"
INACTIVE_SURFACES = frozenset(
    {"washout", "prompted_no_intent", "free_choice_no_intent", "rest", "inactive_intertrial"}
)
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "comm_p0_generated_numerical",
        "comm_p0_generated_scorer",
        "comm_p0_generated_live",
        "numpy",
        "scipy",
        "sklearn",
        "torch",
        "mne",
    }
)
_PRIVATE_ROW_KEYS = frozenset(
    {
        "item_id",
        "participant_id",
        "probabilities",
        "prediction",
        "predicted_command_index",
        "target",
        "targets",
        "delivered_targets",
        "label",
        "labels",
    }
)


class ScoreOnlyRefusal(RuntimeError):
    """Fail-closed refusal with a stable family identifier."""

    def __init__(self, family: str, detail: str | None = None) -> None:
        self.family = family
        self.detail = detail
        message = f"COMM-P0-SCORE-ONLY:{family}"
        if detail:
            message = f"{message}:{detail}"
        super().__init__(message)


def _normalized_for_hash(value: Any) -> Any:
    """Make mapping inputs hashable without treating nonfinite floats as valid JSON."""

    if isinstance(value, Mapping):
        return {str(key): _normalized_for_hash(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalized_for_hash(child) for child in value]
    if isinstance(value, float) and not math.isfinite(value):
        if math.isnan(value):
            marker = "nan"
        elif value > 0:
            marker = "+inf"
        else:
            marker = "-inf"
        return {"__invalid_nonfinite_float__": marker}
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic, newline-terminated JSON bytes for an in-memory record."""

    try:
        payload = json.dumps(
            _normalized_for_hash(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ScoreOnlyRefusal("noncanonical_record", str(exc)) from exc
    return (payload + "\n").encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _as_records(values: Sequence[Mapping[str, Any]], surface: str) -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for index, value in enumerate(values):
        if not isinstance(value, Mapping):
            raise ScoreOnlyRefusal("noncanonical_record", f"{surface}[{index}]")
        record = dict(value)
        canonical_json_bytes(record)
        records.append(record)
    return tuple(records)


def _assert_target_free(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in {"target", "targets", "label", "labels", "delivered_targets"}:
                raise ScoreOnlyRefusal("target_capability_escape", f"{path}.{key}")
            _assert_target_free(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_target_free(child, f"{path}[{index}]")


def _assert_aggregate_private(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in _PRIVATE_ROW_KEYS or normalized.endswith("_target"):
                raise ScoreOnlyRefusal("aggregate_privacy_violation", f"{path}.{key}")
            _assert_aggregate_private(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _assert_aggregate_private(child, f"{path}[{index}]")


def _contract_value(contract: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = contract.get(key)
    if not isinstance(value, Mapping):
        raise ScoreOnlyRefusal("contract_mismatch", key)
    return value


def _validate_contract(contract: Mapping[str, Any]) -> tuple[str, ...]:
    if not isinstance(contract, Mapping) or not str(contract.get("gate_id", "")):
        raise ScoreOnlyRefusal("contract_mismatch", "gate_id")
    conditions_raw = contract.get("conditions")
    if not isinstance(conditions_raw, (list, tuple)):
        raise ScoreOnlyRefusal("contract_mismatch", "conditions")
    conditions = tuple(str(value) for value in conditions_raw)
    if not conditions or len(conditions) != len(set(conditions)):
        raise ScoreOnlyRefusal("contract_mismatch", "conditions")
    scoring = _contract_value(contract, "participant_first_scoring")
    live = _contract_value(contract, "live_metrics")
    required_conditions = {
        str(scoring.get("primary_condition", "")),
        *(str(value) for value in scoring.get("primary_log_loss_comparators", ())),
        *(str(value) for value in scoring.get("balanced_accuracy_comparator_inventory", ())),
    }
    if "" in required_conditions or not required_conditions.issubset(conditions):
        raise ScoreOnlyRefusal("contract_mismatch", "condition_inventory")
    for key in (
        "probability_floor",
        "maximum_frozen_log_loss",
        "complete_participants_denominator",
        "positive_participants_minimum",
    ):
        if key not in scoring:
            raise ScoreOnlyRefusal("contract_mismatch", key)
    for key in (
        "stable_commit_coverage_fraction_minimum",
        "per_command_coverage_fraction_minimum",
        "false_commits_per_inactive_minute_maximum",
        "dropped_or_invalid_chunk_fraction_maximum",
        "frames_processed_before_next_deadline_fraction_minimum",
        "stable_commit_latency_median_seconds_maximum",
        "stable_commit_latency_p95_seconds_maximum",
        "capture_to_presentation_processing_overhead_p95_seconds_maximum",
    ):
        if key not in live:
            raise ScoreOnlyRefusal("contract_mismatch", key)
    return conditions


def build_prediction_freeze_attestation(
    prediction_records: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Build the accepted aggregate freeze shape over the exact record order."""

    conditions = _validate_contract(contract)
    records = _as_records(prediction_records, "predictions")
    digest = hashlib.sha256()
    participants: set[str] = set()
    endpoints: set[str] = set()
    observed_conditions: set[str] = set()
    for record in records:
        _assert_target_free(record)
        digest.update(canonical_json_bytes(record))
        participants.add(str(record.get("participant_id", "")))
        endpoints.add(str(record.get("endpoint", "")))
        observed_conditions.add(str(record.get("condition", "")))
    participants.discard("")
    endpoints.intersection_update(ENDPOINTS)
    observed_conditions.intersection_update(conditions)
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_prediction_freeze",
        "schema_version": str(contract.get("schema_version", SCHEMA_VERSION)),
        "gate_id": str(contract["gate_id"]),
        "prediction_rows": len(records),
        "prediction_sets": len(participants) * len(observed_conditions) * len(endpoints),
        "private_prediction_stream_sha256": digest.hexdigest(),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }


def _validate_freeze(
    records: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
    freeze_attestation: Mapping[str, Any],
) -> str:
    if not isinstance(freeze_attestation, Mapping):
        raise ScoreOnlyRefusal("prediction_freeze_attestation_mismatch")
    rebuilt = build_prediction_freeze_attestation(records, contract)
    if dict(freeze_attestation) != rebuilt:
        raise ScoreOnlyRefusal("prediction_freeze_attestation_mismatch")
    return sha256_json(rebuilt)


def _validate_authorization(authorization: Mapping[str, Any]) -> None:
    if not isinstance(authorization, Mapping):
        raise ScoreOnlyRefusal("one_shot_authorization_invalid")
    if authorization.get("prediction_freeze_green") is not True:
        raise ScoreOnlyRefusal("score_before_exact_green_freeze")
    if authorization.get("replication_artifact_freeze_green") is not True:
        raise ScoreOnlyRefusal("replication_prediction_freeze_not_green_before_delivery")
    if (
        authorization.get("one_shot") is not True
        or authorization.get("target_delivery_count") != 1
        or authorization.get("prior_score_count") != 0
    ):
        raise ScoreOnlyRefusal("repeated_score_or_target_delivery")


def _trial_inventory(
    trial_records: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    records = _as_records(trial_records, "trials")
    _assert_target_free(records)
    manifest: dict[str, dict[str, Any]] = {}
    participants_by_cohort: dict[str, set[str]] = defaultdict(set)
    for record in records:
        item_id = str(record.get("item_id", ""))
        cohort = str(record.get("cohort_id", ""))
        participant = str(record.get("participant_id", ""))
        endpoint = record.get("endpoint")
        phase = str(record.get("phase", ""))
        if (
            not item_id
            or item_id in manifest
            or cohort not in COHORTS
            or not participant
            or not phase
            or (endpoint is not None and endpoint not in ENDPOINTS)
        ):
            raise ScoreOnlyRefusal("trial_inventory_mismatch")
        manifest[item_id] = record
        participants_by_cohort[cohort].add(participant)
    required = int(
        _contract_value(contract, "participant_first_scoring")["complete_participants_denominator"]
    )
    for cohort in COHORTS:
        if len(participants_by_cohort[cohort]) != required:
            raise ScoreOnlyRefusal("cohort_cardinality_or_replacement_rule_violation")
    active = tuple(item_id for item_id, row in manifest.items() if row.get("endpoint") in ENDPOINTS)
    if not active:
        raise ScoreOnlyRefusal("trial_inventory_mismatch")
    return manifest, active


def _prediction_inventory(
    prediction_records: Sequence[Mapping[str, Any]],
    manifest: Mapping[str, Mapping[str, Any]],
    active_item_ids: Sequence[str],
    conditions: Sequence[str],
) -> tuple[dict[tuple[str, str], dict[str, Any]], dict[str, int]]:
    records = _as_records(prediction_records, "predictions")
    _assert_target_free(records)
    active = set(active_item_ids)
    index: dict[tuple[str, str], dict[str, Any]] = {}
    invalid_rows = 0
    for record in records:
        item_id = str(record.get("item_id", ""))
        condition = str(record.get("condition", ""))
        trial = manifest.get(item_id)
        key = (item_id, condition)
        if (
            trial is None
            or item_id not in active
            or condition not in conditions
            or str(record.get("cohort_id", "")) != str(trial.get("cohort_id", ""))
            or str(record.get("participant_id", "")) != str(trial.get("participant_id", ""))
            or record.get("endpoint") != trial.get("endpoint")
            or str(record.get("phase", "")) != str(trial.get("phase", ""))
            or key in index
        ):
            raise ScoreOnlyRefusal("prediction_inventory_missing_duplicate_or_mismatch")
        index[key] = record
        if _validated_probabilities(record.get("probabilities"), 4) is None:
            invalid_rows += 1
    expected = {(item_id, condition) for item_id in active_item_ids for condition in conditions}
    missing_rows = len(expected.difference(index))
    return index, {
        "assigned_prediction_rows": len(expected),
        "present_prediction_rows": len(index),
        "missing_prediction_rows_retained": missing_rows,
        "invalid_prediction_rows_retained": invalid_rows,
        "valid_prediction_rows": len(index) - invalid_rows,
        "rows_dropped": 0,
    }


def _validated_probabilities(value: Any, command_count: int) -> tuple[float, ...] | None:
    if not isinstance(value, (list, tuple)) or len(value) != command_count:
        return None
    converted: list[float] = []
    try:
        for item in value:
            if isinstance(item, bool):
                return None
            converted.append(float(item))
    except (TypeError, ValueError, OverflowError):
        return None
    if any(not math.isfinite(item) or item < 0.0 for item in converted):
        return None
    if not math.isclose(sum(converted), 1.0, rel_tol=0.0, abs_tol=1e-12):
        return None
    return tuple(converted)


def _targets_for_active(
    delivered_targets: Mapping[str, Any], active_item_ids: Sequence[str], command_count: int
) -> dict[str, int]:
    if not isinstance(delivered_targets, Mapping) or set(delivered_targets) != set(active_item_ids):
        raise ScoreOnlyRefusal("scorer_prediction_target_row_mismatch")
    values: dict[str, int] = {}
    for item_id in active_item_ids:
        value = delivered_targets[item_id]
        if isinstance(value, bool):
            raise ScoreOnlyRefusal("scorer_prediction_target_row_mismatch")
        try:
            integer = int(value)
        except (TypeError, ValueError, OverflowError) as exc:
            raise ScoreOnlyRefusal("scorer_prediction_target_row_mismatch") from exc
        if integer != value or integer not in range(command_count):
            raise ScoreOnlyRefusal("scorer_prediction_target_row_mismatch")
        values[item_id] = integer
    return values


def _balanced_accuracy(
    targets: Sequence[int], predictions: Sequence[int | None], command_count: int
) -> float:
    recalls = []
    for command in range(command_count):
        positions = [index for index, value in enumerate(targets) if value == command]
        recalls.append(
            sum(predictions[index] == command for index in positions) / len(positions)
            if positions
            else 0.0
        )
    return sum(recalls) / command_count


def _condition_metrics(
    item_ids: Sequence[str],
    condition: str,
    prediction_index: Mapping[tuple[str, str], Mapping[str, Any]],
    targets: Mapping[str, int],
    scoring: Mapping[str, Any],
    command_count: int,
) -> tuple[float, float, int]:
    floor = float(scoring["probability_floor"])
    maximum_loss = float(scoring["maximum_frozen_log_loss"])
    losses: list[float] = []
    predictions: list[int | None] = []
    invalid = 0
    true_values = [targets[item_id] for item_id in item_ids]
    for item_id, truth in zip(item_ids, true_values, strict=True):
        record = prediction_index.get((item_id, condition))
        probability = _validated_probabilities(
            None if record is None else record.get("probabilities"), command_count
        )
        if probability is None:
            losses.append(maximum_loss)
            predictions.append(None)
            invalid += 1
            continue
        losses.append(-math.log(max(probability[truth], floor)))
        predictions.append(
            max(range(command_count), key=lambda index: (probability[index], -index))
        )
    return (
        sum(losses) / len(losses),
        _balanced_accuracy(true_values, predictions, command_count),
        invalid,
    )


def _participant_metrics(
    rows: Sequence[Mapping[str, Any]],
    prediction_index: Mapping[tuple[str, str], Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
    *,
    prompted: bool,
) -> dict[str, float]:
    scoring = _contract_value(contract, "participant_first_scoring")
    conditions = tuple(str(value) for value in contract["conditions"])
    commands = tuple(
        str(value) for value in _contract_value(contract, "trial_grammar").get("commands", ())
    )
    command_count = len(commands)
    item_ids = sorted(str(row["item_id"]) for row in rows)
    losses: dict[str, float] = {}
    accuracies: dict[str, float] = {}
    invalid_count = 0
    for condition in conditions:
        loss, accuracy, invalid = _condition_metrics(
            item_ids, condition, prediction_index, targets, scoring, command_count
        )
        losses[condition] = loss
        accuracies[condition] = accuracy
        invalid_count += invalid
    candidate = str(scoring["primary_condition"])
    ll_controls = tuple(str(value) for value in scoring["primary_log_loss_comparators"])
    ba_controls = tuple(str(value) for value in scoring["balanced_accuracy_comparator_inventory"])
    if prompted:
        ba_controls = tuple(value for value in ba_controls if value != "cue_only")
    return {
        "margin": min(losses[value] - losses[candidate] for value in ll_controls),
        "accuracy_margin": accuracies[candidate] - max(accuracies[value] for value in ba_controls),
        "candidate_loss": losses[candidate],
        "candidate_accuracy": accuracies[candidate],
        "invalid_assignments": float(invalid_count),
    }


def _exact_sign_flip(values: Sequence[float]) -> tuple[float, int]:
    rounded = tuple(float(value) for value in values)
    assignments = 1 << len(rounded)
    observed = sum(rounded) / len(rounded)
    signed_sum = -sum(rounded)
    extreme = int(signed_sum / len(rounded) >= observed - 1e-12)
    previous_gray = 0
    for assignment in range(1, assignments):
        gray = assignment ^ (assignment >> 1)
        changed = gray ^ previous_gray
        bit = changed.bit_length() - 1
        if gray & changed:
            signed_sum += 2.0 * rounded[bit]
        else:
            signed_sum -= 2.0 * rounded[bit]
        extreme += int(signed_sum / len(rounded) >= observed - 1e-12)
        previous_gray = gray
    return extreme / assignments, assignments


def _shadow_summary(
    cohort: str,
    endpoint: str,
    manifest: Mapping[str, Mapping[str, Any]],
    prediction_index: Mapping[tuple[str, str], Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    scoring = _contract_value(contract, "participant_first_scoring")
    rows = [
        row
        for row in manifest.values()
        if row.get("cohort_id") == cohort
        and row.get("endpoint") == endpoint
        and (cohort == "discovery" or row.get("phase") == "shadow")
    ]
    participants = sorted({str(row["participant_id"]) for row in rows})
    expected = int(scoring["complete_participants_denominator"])
    if len(participants) != expected:
        raise ScoreOnlyRefusal("cohort_cardinality_or_replacement_rule_violation")
    metrics = []
    for participant in participants:
        participant_rows = [row for row in rows if row.get("participant_id") == participant]
        if not participant_rows:
            raise ScoreOnlyRefusal("trial_inventory_mismatch")
        metrics.append(
            _participant_metrics(
                participant_rows,
                prediction_index,
                targets,
                contract,
                prompted=endpoint == "prompted_intend",
            )
        )
    margins = [
        round(row["margin"], int(scoring.get("participant_metric_decimal_places", 12)))
        for row in metrics
    ]
    accuracy_margins = [row["accuracy_margin"] for row in metrics]
    p_value, assignments = _exact_sign_flip(margins)
    required_positive = int(scoring["positive_participants_minimum"])
    summary: dict[str, Any] = {
        "participant_count": len(participants),
        "assigned_active_episodes": len(rows),
        "participant_macro_log_loss": sum(row["candidate_loss"] for row in metrics) / len(metrics),
        "participant_macro_balanced_accuracy": sum(row["candidate_accuracy"] for row in metrics)
        / len(metrics),
        "mean_margin_nats_per_item": sum(margins) / len(margins),
        "positive_participants": sum(value > 0.0 for value in margins),
        "exact_one_sided_sign_flip_p": p_value,
        "sign_flip_assignments_evaluated": assignments,
        "mean_balanced_accuracy_margin": sum(accuracy_margins) / len(accuracy_margins),
        "invalid_or_missing_prediction_assignments_retained": int(
            sum(row["invalid_assignments"] for row in metrics)
        ),
        "rows_dropped": 0,
    }
    if endpoint == "free_choice_intend":
        summary["passes"] = bool(
            summary["mean_margin_nats_per_item"]
            >= float(scoring["mean_margin_nats_per_item_minimum"])
            and summary["positive_participants"] >= required_positive
            and summary["exact_one_sided_sign_flip_p"]
            <= float(scoring["exact_one_sided_sign_flip_p_maximum"])
            and summary["mean_balanced_accuracy_margin"]
            >= float(scoring["balanced_accuracy_margin_minimum"])
        )
    else:
        summary.update(
            {
                "passes_directional_controls": bool(
                    summary["mean_margin_nats_per_item"] > 0.0
                    and summary["positive_participants"] >= required_positive
                    and summary["mean_balanced_accuracy_margin"] > 0.0
                ),
                "cue_only_reported_as_leakage_ceiling": True,
                "may_rescue_free_choice_failure": False,
            }
        )
    return summary


def _finite_nonnegative(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if math.isfinite(converted) and converted >= 0.0 else None


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return math.inf
    ordered = sorted(values)
    return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]


def _observation_inventory(
    observations: Sequence[Mapping[str, Any]],
    live_manifest: Mapping[str, Mapping[str, Any]],
    participants: Sequence[str],
) -> tuple[dict[str, dict[str, Any]], tuple[dict[str, Any], ...], int]:
    records = _as_records(observations, "observations")
    _assert_target_free(records)
    active: dict[str, dict[str, Any]] = {}
    inactive: list[dict[str, Any]] = []
    seen: set[str] = set()
    invalid = 0
    allowed_participants = set(participants)
    for record in records:
        interval_id = str(record.get("interval_id", ""))
        if not interval_id or interval_id in seen:
            raise ScoreOnlyRefusal("live_observation_duplicate_or_mismatch")
        seen.add(interval_id)
        if (
            record.get("cohort_id") != LIVE_COHORT
            or record.get("phase") != LIVE_PHASE
            or str(record.get("participant_id", "")) not in allowed_participants
        ):
            raise ScoreOnlyRefusal("live_observation_duplicate_or_mismatch")
        if record.get("active_intent") is True:
            trial = live_manifest.get(interval_id)
            if trial is None or record.get("endpoint") != trial.get("endpoint"):
                raise ScoreOnlyRefusal("live_observation_duplicate_or_mismatch")
            active[interval_id] = record
        elif record.get("active_intent") is False:
            if (
                record.get("endpoint") is not None
                or record.get("inactive_surface") not in INACTIVE_SURFACES
            ):
                raise ScoreOnlyRefusal("live_observation_duplicate_or_mismatch")
            inactive.append(record)
        else:
            invalid += 1
    invalid += len(set(live_manifest).difference(active))
    return active, tuple(inactive), invalid


def _observation_covered(record: Mapping[str, Any] | None, live: Mapping[str, Any]) -> bool:
    if record is None or record.get("stable_commit") is not True:
        return False
    invalid_chunks = _finite_nonnegative(record.get("invalid_chunk_count"))
    latency = _finite_nonnegative(record.get("stable_commit_latency_seconds"))
    predicted = record.get("predicted_command_index")
    return bool(
        invalid_chunks == 0.0
        and latency is not None
        and latency <= float(live["stable_commit_latency_p95_seconds_maximum"])
        and isinstance(predicted, int)
        and not isinstance(predicted, bool)
        and predicted in range(4)
        and record.get("clock_map_verified") is True
    )


def _endpoint_live_summary(
    endpoint: str,
    live_manifest: Mapping[str, Mapping[str, Any]],
    active: Mapping[str, Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live = _contract_value(contract, "live_metrics")
    commands = tuple(str(value) for value in _contract_value(contract, "trial_grammar")["commands"])
    rows = [row for row in live_manifest.values() if row.get("endpoint") == endpoint]
    participants = sorted({str(row["participant_id"]) for row in rows})
    participant_coverages = []
    per_command: dict[int, list[bool]] = defaultdict(list)
    true_values: list[int] = []
    predictions: list[int | None] = []
    first_latencies: list[float] = []
    stable_latencies: list[float] = []
    overheads: list[float] = []
    invalid_or_missing = 0
    for participant in participants:
        participant_rows = [row for row in rows if row.get("participant_id") == participant]
        covered_count = 0
        for trial in participant_rows:
            item_id = str(trial["item_id"])
            observation = active.get(item_id)
            covered = _observation_covered(observation, live)
            covered_count += int(covered)
            truth = targets[item_id]
            per_command[truth].append(covered)
            true_values.append(truth)
            predictions.append(
                int(observation["predicted_command_index"])
                if covered and observation is not None
                else None
            )
            if observation is None:
                invalid_or_missing += 1
                continue
            first = _finite_nonnegative(observation.get("first_output_latency_seconds"))
            stable = _finite_nonnegative(observation.get("stable_commit_latency_seconds"))
            overhead = _finite_nonnegative(
                observation.get("capture_to_presentation_overhead_seconds")
            )
            if first is not None:
                first_latencies.append(first)
            if covered and stable is not None and overhead is not None:
                stable_latencies.append(stable)
                overheads.append(overhead)
            if not covered:
                invalid_or_missing += 1
        participant_coverages.append(covered_count / len(participant_rows))
    command_coverage = {
        command: (sum(per_command[index]) / len(per_command[index]) if per_command[index] else 0.0)
        for index, command in enumerate(commands)
    }
    coverage = sum(participant_coverages) / len(participant_coverages)
    stable_median_value = median(stable_latencies) if stable_latencies else math.inf
    stable_p95_value = _percentile(stable_latencies, 0.95)
    overhead_p95_value = _percentile(overheads, 0.95)
    summary = {
        "participant_count": len(participants),
        "assigned_active_episodes": len(rows),
        "participant_macro_coverage": coverage,
        "per_command_coverage": command_coverage,
        "missed_activation_fraction": 1.0 - coverage,
        "abstention_fraction": sum(value is None for value in predictions) / len(predictions),
        "commit_balanced_accuracy": _balanced_accuracy(true_values, predictions, len(commands)),
        "first_output_latency_median_seconds": median(first_latencies) if first_latencies else None,
        "first_output_latency_p95_seconds": _percentile(first_latencies, 0.95)
        if first_latencies
        else None,
        "stable_commit_latency_median_seconds": stable_median_value if stable_latencies else None,
        "stable_commit_latency_p95_seconds": stable_p95_value if stable_latencies else None,
        "capture_to_presentation_processing_overhead_p95_seconds": overhead_p95_value
        if overheads
        else None,
        "invalid_or_missing_observations_retained": invalid_or_missing,
        "rows_dropped": 0,
    }
    summary["active_operational_pass"] = bool(
        coverage >= float(live["stable_commit_coverage_fraction_minimum"])
        and all(
            value >= float(live["per_command_coverage_fraction_minimum"])
            for value in command_coverage.values()
        )
        and stable_median_value <= float(live["stable_commit_latency_median_seconds_maximum"])
        and stable_p95_value <= float(live["stable_commit_latency_p95_seconds_maximum"])
        and overhead_p95_value
        <= float(live["capture_to_presentation_processing_overhead_p95_seconds_maximum"])
    )
    return summary


def _shared_live_metrics(
    observations: Sequence[Mapping[str, Any]],
    inactive: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live = _contract_value(contract, "live_metrics")
    invalid_records = 0
    inactive_seconds = 0.0
    false_commits = 0
    total_chunks = 0
    invalid_chunks = 0
    total_frames = 0
    processed_frames = 0
    for record in observations:
        duration = _finite_nonnegative(record.get("duration_seconds"))
        chunks = _finite_nonnegative(record.get("total_chunk_count"))
        bad_chunks = _finite_nonnegative(record.get("invalid_chunk_count"))
        frames = _finite_nonnegative(record.get("total_frame_count"))
        processed = _finite_nonnegative(record.get("processed_frame_count"))
        if (
            duration is None
            or duration <= 0.0
            or chunks is None
            or chunks <= 0.0
            or bad_chunks is None
            or bad_chunks > chunks
            or frames is None
            or frames <= 0.0
            or processed is None
            or processed > frames
        ):
            invalid_records += 1
            continue
        total_chunks += int(chunks)
        invalid_chunks += int(bad_chunks)
        total_frames += int(frames)
        processed_frames += int(processed)
    for record in inactive:
        duration = _finite_nonnegative(record.get("duration_seconds"))
        commits = _finite_nonnegative(record.get("commit_count"))
        if duration is None or duration <= 0.0 or commits is None:
            invalid_records += 1
            continue
        inactive_seconds += duration
        false_commits += int(commits)
    observed_surfaces = {str(record.get("inactive_surface", "")) for record in inactive}
    missing_surfaces = sorted(INACTIVE_SURFACES.difference(observed_surfaces))
    false_rate_value = false_commits / (inactive_seconds / 60.0) if inactive_seconds else math.inf
    dropped_value = invalid_chunks / total_chunks if total_chunks else math.inf
    deadline = processed_frames / total_frames if total_frames else 0.0
    result = {
        "inactive_interval_count": len(inactive),
        "inactive_duration_seconds": inactive_seconds,
        "false_commit_count": false_commits,
        "false_commits_per_inactive_minute": false_rate_value if inactive_seconds else None,
        "inactive_surfaces_counted_once": sorted(INACTIVE_SURFACES),
        "missing_inactive_surface_count": len(missing_surfaces),
        "invalid_observation_records_retained": invalid_records,
        "dropped_or_invalid_chunk_fraction": dropped_value if total_chunks else None,
        "frames_processed_before_next_deadline_fraction": deadline,
    }
    result["passes"] = bool(
        not missing_surfaces
        and invalid_records == 0
        and false_rate_value <= float(live["false_commits_per_inactive_minute_maximum"])
        and dropped_value <= float(live["dropped_or_invalid_chunk_fraction_maximum"])
        and deadline >= float(live["frames_processed_before_next_deadline_fraction_minimum"])
    )
    return result


def _live_summary(
    manifest: Mapping[str, Mapping[str, Any]],
    prediction_index: Mapping[tuple[str, str], Mapping[str, Any]],
    observations: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live_manifest = {
        item_id: row
        for item_id, row in manifest.items()
        if row.get("cohort_id") == LIVE_COHORT
        and row.get("phase") == LIVE_PHASE
        and row.get("endpoint") in ENDPOINTS
    }
    participants = sorted({str(row["participant_id"]) for row in live_manifest.values()})
    active, inactive, structural_invalid = _observation_inventory(
        observations, live_manifest, participants
    )
    shared = _shared_live_metrics(observations, inactive, contract)
    shared["missing_or_structurally_invalid_active_observations_retained"] = structural_invalid
    if structural_invalid:
        shared["passes"] = False
    scoring = _contract_value(contract, "participant_first_scoring")
    candidate = str(scoring["primary_condition"])
    endpoint_results: dict[str, dict[str, Any]] = {}
    for endpoint in ENDPOINTS:
        classification = _live_classification(
            endpoint, live_manifest, prediction_index, targets, contract, candidate
        )
        operational = _endpoint_live_summary(endpoint, live_manifest, active, targets, contract)
        endpoint_results[endpoint] = {
            "classification": classification,
            "operational": operational,
            "passes": bool(
                classification["directional_pass"]
                and operational["active_operational_pass"]
                and shared["passes"]
            ),
        }
    free_choice_pass = endpoint_results["free_choice_intend"]["passes"]
    prompted_pass = endpoint_results["prompted_intend"]["passes"]
    return {
        "free_choice_live": endpoint_results["free_choice_intend"],
        "prompted_live": endpoint_results["prompted_intend"],
        "inactive_null_metrics": shared,
        "router": {
            "primary_endpoint": "free_choice_intend",
            "free_choice_live_pass": free_choice_pass,
            "prompted_live_pass": prompted_pass,
            "prompted_may_rescue_free_choice": False,
            "live_gate_pass": free_choice_pass,
        },
        "end_to_end_latency_measured": False,
        "generated_clock_latency_only": True,
    }


def _live_classification(
    endpoint: str,
    manifest: Mapping[str, Mapping[str, Any]],
    prediction_index: Mapping[tuple[str, str], Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
    candidate: str,
) -> dict[str, Any]:
    scoring = _contract_value(contract, "participant_first_scoring")
    rows = [row for row in manifest.values() if row.get("endpoint") == endpoint]
    participants = sorted({str(row["participant_id"]) for row in rows})
    metrics = [
        _participant_metrics(
            [row for row in rows if row.get("participant_id") == participant],
            prediction_index,
            targets,
            contract,
            prompted=endpoint == "prompted_intend",
        )
        for participant in participants
    ]
    mean_margin = sum(row["margin"] for row in metrics) / len(metrics)
    mean_accuracy = sum(row["accuracy_margin"] for row in metrics) / len(metrics)
    return {
        "participant_count": len(participants),
        "assigned_active_episodes": len(rows),
        "primary_condition": candidate,
        "participant_macro_log_loss": sum(row["candidate_loss"] for row in metrics) / len(metrics),
        "participant_macro_balanced_accuracy": sum(row["candidate_accuracy"] for row in metrics)
        / len(metrics),
        "mean_log_loss_margin_over_both_registered_controls": mean_margin,
        "positive_log_loss_margin_participants": sum(row["margin"] > 0.0 for row in metrics),
        "mean_balanced_accuracy_margin_over_registered_controls": mean_accuracy,
        "invalid_or_missing_prediction_assignments_retained": int(
            sum(row["invalid_assignments"] for row in metrics)
        ),
        "directional_pass": bool(
            mean_margin > 0.0
            and sum(row["margin"] > 0.0 for row in metrics)
            >= int(scoring["positive_participants_minimum"])
            and mean_accuracy > 0.0
        ),
        "exact_sign_flip_performed": False,
        "rows_dropped": 0,
    }


class ScoreOnlyWorker:
    """One-shot in-memory scorer with no fit, model, file, or network capability."""

    __slots__ = ("_consumed", "_contract")

    def __init__(self, contract: Mapping[str, Any]) -> None:
        _validate_contract(contract)
        self._contract = dict(contract)
        self._consumed = False

    @property
    def consumed(self) -> bool:
        return self._consumed

    def score(
        self,
        *,
        trial_records: Sequence[Mapping[str, Any]],
        prediction_records: Sequence[Mapping[str, Any]],
        live_observation_records: Sequence[Mapping[str, Any]],
        freeze_attestation: Mapping[str, Any],
        authorization: Mapping[str, Any],
        delivered_targets: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Consume one generated target delivery and return aggregate-only summaries."""

        if self._consumed:
            raise ScoreOnlyRefusal("repeated_score_or_target_delivery")
        _validate_authorization(authorization)
        conditions = _validate_contract(self._contract)
        predictions = _as_records(prediction_records, "predictions")
        freeze_sha256 = _validate_freeze(predictions, self._contract, freeze_attestation)
        manifest, active_item_ids = _trial_inventory(trial_records, self._contract)
        prediction_index, quality = _prediction_inventory(
            predictions, manifest, active_item_ids, conditions
        )

        # The capability is consumed before generated targets are inspected.  A
        # downstream validation failure therefore cannot permit a second delivery.
        self._consumed = True
        commands = tuple(
            str(value)
            for value in _contract_value(self._contract, "trial_grammar").get("commands", ())
        )
        if len(commands) != 4:
            raise ScoreOnlyRefusal("contract_mismatch", "four_command_inventory")
        target_values = _targets_for_active(delivered_targets, active_item_ids, len(commands))

        cohorts = []
        for cohort in COHORTS:
            free_choice = _shadow_summary(
                cohort,
                "free_choice_intend",
                manifest,
                prediction_index,
                target_values,
                self._contract,
            )
            prompted = _shadow_summary(
                cohort,
                "prompted_intend",
                manifest,
                prediction_index,
                target_values,
                self._contract,
            )
            cohorts.append(
                {
                    "cohort_id": cohort,
                    "free_choice_shadow": free_choice,
                    "prompted_shadow_directional": prompted,
                    "shadow_router": {
                        "primary_endpoint": "free_choice_intend",
                        "free_choice_shadow_pass": free_choice["passes"],
                        "prompted_shadow_pass": prompted["passes_directional_controls"],
                        "prompted_may_rescue_free_choice": False,
                        "shadow_gate_pass": free_choice["passes"],
                    },
                }
            )
        live = _live_summary(
            manifest,
            prediction_index,
            live_observation_records,
            target_values,
            self._contract,
        )
        result = {
            "schema_name": "neurodecodekit.comm_p0_generated_score_only_aggregate",
            "schema_version": SCHEMA_VERSION,
            "gate_id": str(self._contract["gate_id"]),
            "prediction_freeze_sha256": freeze_sha256,
            "prediction_quality": quality,
            "cohorts": cohorts,
            "replication_live": live,
            "target_delivery_count": 1,
            "score_count": 1,
            "post_target_updates": 0,
            "contains_individual_prediction_probability_target_or_participant_outcome": False,
            "claim_boundary": {
                "generated_only": True,
                "aggregate_only": True,
                "contains_individual_records": False,
                "end_to_end_latency_measured": False,
                "scientific_claim_established": False,
            },
            "warnings": [
                "fictional generated records only",
                "missing and invalid predictions are retained as maximum-loss zero-accuracy assignments",
                "generated clock latency is not end-to-end device latency",
                "not scientific evidence",
            ],
        }
        _assert_aggregate_private(result)
        canonical_json_bytes(result)
        return result


def score_records(
    *,
    contract: Mapping[str, Any],
    trial_records: Sequence[Mapping[str, Any]],
    prediction_records: Sequence[Mapping[str, Any]],
    live_observation_records: Sequence[Mapping[str, Any]],
    freeze_attestation: Mapping[str, Any],
    authorization: Mapping[str, Any],
    delivered_targets: Mapping[str, Any],
) -> dict[str, Any]:
    """Convenience entry point for one isolated one-shot score operation."""

    return ScoreOnlyWorker(contract).score(
        trial_records=trial_records,
        prediction_records=prediction_records,
        live_observation_records=live_observation_records,
        freeze_attestation=freeze_attestation,
        authorization=authorization,
        delivered_targets=delivered_targets,
    )


def import_capability_audit() -> dict[str, Any]:
    """Report the module's import and intentionally absent capabilities."""

    imported = sorted(
        {
            value.__name__.split(".", 1)[0]
            for value in globals().values()
            if isinstance(value, types.ModuleType)
        }
    )
    forbidden = sorted(FORBIDDEN_IMPORT_ROOTS.intersection(imported))
    return {
        "schema_name": "neurodecodekit.comm_p0_score_only_capability_audit",
        "schema_version": SCHEMA_VERSION,
        "standard_library_only": not forbidden,
        "imported_module_roots": imported,
        "forbidden_import_roots_present": forbidden,
        "fit_or_model_capability": False,
        "file_read_or_write_capability": False,
        "network_capability": False,
        "real_or_private_data_capability": False,
        "row_level_output_capability": False,
    }
