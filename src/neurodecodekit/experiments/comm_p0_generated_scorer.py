"""Post-freeze aggregate scorer for the generated-only COMM-P0-G qualification."""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical


@dataclass(frozen=True, slots=True)
class CohortScore:
    cohort_id: str
    free_choice_shadow: Mapping[str, Any]
    prompted_shadow_directional: Mapping[str, Any]
    live: Mapping[str, Any] | None
    target_delivery_count: int
    score_count: int


@dataclass(frozen=True, slots=True)
class AggregateScore:
    schema_name: str
    schema_version: str
    gate_id: str
    prediction_freeze_sha256: str
    cohorts: tuple[CohortScore, ...]
    target_deliveries: int
    scores: int
    post_target_updates: int
    contains_individual_prediction_probability_target_or_participant_outcome: bool
    claim_boundary: Mapping[str, bool]
    warnings: tuple[str, ...]

    def public_record(self) -> dict[str, Any]:
        value = asdict(self)
        core.assert_target_free(value)
        return value


def _target_for_trial(row: core.TrialPlan) -> int:
    # This function belongs only in the scorer process in the official runner.
    payload = f"{row.participant_id}:{row.trial_index}:{row.role}:20260827".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") % len(core.COMMANDS)


def _log_loss(targets: Sequence[int], probabilities: Sequence[Sequence[float]]) -> float:
    if len(targets) != len(probabilities) or not targets:
        raise core.CommP0GeneratedRefusal("scorer_prediction_target_row_mismatch")
    total = 0.0
    for target, probability in zip(targets, probabilities, strict=True):
        values = core.validate_probability_vector(probability)
        total -= math.log(max(values[target], 1e-6))
    return total / len(targets)


def _balanced_accuracy(targets: Sequence[int], probabilities: Sequence[Sequence[float]]) -> float:
    by_class: dict[int, list[bool]] = defaultdict(list)
    for target, probability in zip(targets, probabilities, strict=True):
        predicted = max(range(4), key=lambda index: probability[index])
        by_class[target].append(predicted == target)
    if set(by_class) != {0, 1, 2, 3}:
        raise core.CommP0GeneratedRefusal("scorer_prediction_target_row_mismatch")
    return sum(sum(values) / len(values) for values in by_class.values()) / 4.0


def _prediction_index(
    predictions: Sequence[numerical.CompactPrediction],
) -> dict[tuple[str, str], numerical.CompactPrediction]:
    index = {}
    for prediction in predictions:
        key = (prediction.item_id, prediction.condition)
        if key in index:
            raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
        core.validate_probability_vector(prediction.probabilities)
        index[key] = prediction
    return index


def _participant_metrics(
    participant_rows: Sequence[core.TrialPlan],
    prediction_index: Mapping[tuple[str, str], numerical.CompactPrediction],
    contract: Mapping[str, Any],
) -> dict[str, float]:
    targets = [_target_for_trial(row) for row in participant_rows]
    conditions = tuple(contract["conditions"])
    losses = {}
    accuracies = {}
    for condition in conditions:
        probabilities = [
            prediction_index[(row.item_id, condition)].probabilities for row in participant_rows
        ]
        losses[condition] = _log_loss(targets, probabilities)
        accuracies[condition] = _balanced_accuracy(targets, probabilities)
    scoring = contract["participant_first_scoring"]
    best_control = max(
        accuracies[condition] for condition in scoring["balanced_accuracy_comparator_inventory"]
    )
    noncue_controls = tuple(
        condition
        for condition in scoring["balanced_accuracy_comparator_inventory"]
        if condition not in {"cue_only", "all_recorded_peripheral_P"}
    )
    return {
        "LL_P": losses["all_recorded_peripheral_P"],
        "LL_P_plus_EEG": losses["P_plus_residual_central_EEG"],
        "LL_P_plus_deranged_EEG": losses["P_plus_class_destroyed_residual_central_EEG"],
        "BA_P_plus_EEG": accuracies["P_plus_residual_central_EEG"],
        "BA_best_control": best_control,
        "BA_best_noncue_control": max(accuracies[condition] for condition in noncue_controls),
    }


def _general_participant_summary(
    metrics: Mapping[str, Mapping[str, float]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    spec = contract["participant_first_scoring"]
    margins = []
    accuracy_margins = []
    for participant_id in sorted(metrics):
        row = metrics[participant_id]
        margins.append(
            round(
                min(
                    row["LL_P"] - row["LL_P_plus_EEG"],
                    row["LL_P_plus_deranged_EEG"] - row["LL_P_plus_EEG"],
                ),
                int(spec["participant_metric_decimal_places"]),
            )
        )
        accuracy_margins.append(row["BA_P_plus_EEG"] - row["BA_best_control"])
    p_value, assignments = core.exact_one_sided_sign_flip(margins)
    summary = {
        "participant_count": len(margins),
        "mean_margin_nats_per_item": sum(margins) / len(margins),
        "positive_participants": sum(value > 0.0 for value in margins),
        "exact_one_sided_sign_flip_p": p_value,
        "sign_flip_assignments_evaluated": assignments,
        "mean_balanced_accuracy_margin": sum(accuracy_margins) / len(accuracy_margins),
    }
    return summary


def _confirmatory_summary(
    metrics: Mapping[str, Mapping[str, float]],
    contract: Mapping[str, Any],
    *,
    exact_registered_cohort: bool,
) -> dict[str, Any]:
    if exact_registered_cohort:
        return core.participant_first_summary(metrics, contract)
    summary = _general_participant_summary(metrics, contract)
    summary["passes"] = False
    summary["development_only_small_cohort"] = True
    return summary


def _prompted_directional_summary(
    metrics: Mapping[str, Mapping[str, float]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    margins = [
        min(
            row["LL_P"] - row["LL_P_plus_EEG"],
            row["LL_P_plus_deranged_EEG"] - row["LL_P_plus_EEG"],
        )
        for row in metrics.values()
    ]
    accuracy_margins = [
        row["BA_P_plus_EEG"] - row["BA_best_noncue_control"] for row in metrics.values()
    ]
    spec = contract["participant_first_scoring"]
    required_positive = math.ceil(
        len(margins)
        * spec["positive_participants_minimum"]
        / spec["complete_participants_denominator"]
    )
    return {
        "participant_count": len(margins),
        "mean_directional_margin_nats_per_item": sum(margins) / len(margins),
        "positive_participants": sum(value > 0.0 for value in margins),
        "positive_participants_required": required_positive,
        "mean_balanced_accuracy_margin_over_noncue_controls": sum(accuracy_margins)
        / len(accuracy_margins),
        "cue_only_reported_as_leakage_ceiling": True,
        "passes_directional_controls": bool(
            sum(margins) / len(margins) > 0.0
            and sum(value > 0.0 for value in margins) >= required_positive
            and sum(accuracy_margins) / len(accuracy_margins) > 0.0
        ),
        "may_rescue_free_choice_failure": False,
    }


def _live_score(
    trial_rows: Sequence[core.TrialPlan],
    prediction_index: Mapping[tuple[str, str], numerical.CompactPrediction],
    contract: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    primary = "P_plus_residual_central_EEG"
    live_trials = [
        row
        for row in trial_rows
        if row.cohort_id == "independent_replication" and row.phase == "live"
    ]
    active_trials = [row for row in live_trials if row.endpoint in core.ENDPOINTS]
    records: list[dict[str, Any]] = []
    active_targets = []
    active_probabilities = []
    correct = 0
    for row in active_trials:
        probability = prediction_index[(row.item_id, primary)].probabilities
        target = _target_for_trial(row)
        predicted = max(range(4), key=lambda index: probability[index])
        confidence = max(probability)
        committed = confidence >= 0.40
        correct += int(committed and predicted == target)
        active_targets.append(target)
        active_probabilities.append(probability)
        records.append(
            {
                "participant_id": row.participant_id,
                "command": core.COMMANDS[target],
                "active_intent": True,
                "stable_commit": committed,
                "invalid": False,
                "processed_before_deadline": True,
                "clock_map_verified": True,
                "stable_commit_latency_seconds": 1.2 + 0.5 * (1.0 - confidence),
                "capture_to_presentation_overhead_seconds": 0.08 + 0.02 * (1.0 - confidence),
            }
        )
    for row in live_trials:
        if row.endpoint in core.ENDPOINTS or row.role == "peripheral_calibration":
            continue
        records.append(
            {
                "participant_id": row.participant_id,
                "active_intent": False,
                "duration_seconds": float(row.duration_seconds),
                "commit_count": 0,
                "surface": row.role,
            }
        )
    live = core.summarize_live_records(records, contract)
    live.update(
        {
            "balanced_accuracy": _balanced_accuracy(active_targets, active_probabilities),
            "log_loss": _log_loss(active_targets, active_probabilities),
            "false_activation_rate_on_null_trials": 0.0,
            "missed_activation_rate": live["noncommits_retained"] / len(active_trials),
            "abstention_fraction": live["noncommits_retained"] / len(active_trials),
            "first_output_latency_median_seconds": 0.5,
            "correct_stable_commits": correct,
            "active_intent_episodes": len(active_trials),
            "end_to_end_latency_measured": False,
            "generated_clock_latency_only": True,
        }
    )
    return live, core.sha256_json(records)


def score_after_freeze(
    predictions: Sequence[numerical.CompactPrediction],
    trial_rows: Sequence[core.TrialPlan],
    prediction_freeze: Mapping[str, Any],
    contract: Mapping[str, Any],
    *,
    prediction_freeze_green: bool,
    replication_artifact_freeze_green: bool,
    exact_registered_cohort: bool = True,
) -> tuple[AggregateScore, str]:
    if not prediction_freeze_green:
        raise core.CommP0GeneratedRefusal("score_before_exact_green_freeze")
    if not replication_artifact_freeze_green:
        raise core.CommP0GeneratedRefusal("replication_prediction_freeze_not_green_before_delivery")
    expected_hash = core.sha256_json(dict(prediction_freeze))
    index = _prediction_index(predictions)
    active_rows = [row for row in trial_rows if row.endpoint in core.ENDPOINTS]
    expected_conditions = set(contract["conditions"])
    if len(index) != len(active_rows) * len(expected_conditions):
        raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
    cohort_scores = []
    target_deliveries = 0
    scores = 0
    live_record_sha256 = ""
    for cohort_id in core.COHORTS:
        shadow_rows = [
            row
            for row in active_rows
            if row.cohort_id == cohort_id and (cohort_id == "discovery" or row.phase == "shadow")
        ]
        by_endpoint: dict[str, list[core.TrialPlan]] = defaultdict(list)
        for row in shadow_rows:
            by_endpoint[row.endpoint or ""].append(row)
        endpoint_metrics = {}
        for endpoint in core.ENDPOINTS:
            by_participant: dict[str, list[core.TrialPlan]] = defaultdict(list)
            for row in by_endpoint[endpoint]:
                by_participant[row.participant_id].append(row)
            endpoint_metrics[endpoint] = {
                participant_id: _participant_metrics(rows, index, contract)
                for participant_id, rows in by_participant.items()
            }
        free_choice = _confirmatory_summary(
            endpoint_metrics["free_choice_intend"],
            contract,
            exact_registered_cohort=exact_registered_cohort,
        )
        prompted = _prompted_directional_summary(endpoint_metrics["prompted_intend"], contract)
        live = None
        if cohort_id == "independent_replication":
            live, live_record_sha256 = _live_score(trial_rows, index, contract)
        target_deliveries += 1
        scores += 1
        cohort_scores.append(
            CohortScore(
                cohort_id=cohort_id,
                free_choice_shadow=free_choice,
                prompted_shadow_directional=prompted,
                live=live,
                target_delivery_count=1,
                score_count=1,
            )
        )
    result = AggregateScore(
        schema_name="neurodecodekit.comm_p0_generated_aggregate_score",
        schema_version="0.1.0",
        gate_id=core.GATE_ID,
        prediction_freeze_sha256=expected_hash,
        cohorts=tuple(cohort_scores),
        target_deliveries=target_deliveries,
        scores=scores,
        post_target_updates=0,
        contains_individual_prediction_probability_target_or_participant_outcome=False,
        claim_boundary=contract["claim_boundary"],
        warnings=(
            "fictional procedural signals only",
            "generated clock latency is not end-to-end device latency",
            "not scientific evidence",
        ),
    )
    result.public_record()
    return result, live_record_sha256


def aggregate_score_sha256(result: AggregateScore) -> str:
    return core.sha256_json(result.public_record())
