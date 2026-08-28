"""Aggregate-only generated live scorer for COMM-P0-G.

The scorer consumes target-free compact predictions plus a one-shot scorer target
capability.  It never returns item, participant, probability, or target rows.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from statistics import median
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical

LIVE_COHORT = "independent_replication"
LIVE_PHASE = "live"
INACTIVE_SURFACES = frozenset(
    {
        "washout",
        "prompted_no_intent",
        "free_choice_no_intent",
        "rest",
        "inactive_intertrial",
    }
)


@dataclass(frozen=True, slots=True)
class GeneratedLiveObservation:
    """Target-free operational record for one active episode or inactive interval."""

    interval_id: str
    cohort_id: str
    participant_id: str
    endpoint: str | None
    phase: str
    active_intent: bool
    inactive_surface: str | None
    duration_seconds: float
    stable_commit: bool
    predicted_command_index: int | None
    commit_count: int
    invalid_chunk_count: int
    total_chunk_count: int
    processed_frame_count: int
    total_frame_count: int
    first_output_latency_seconds: float | None
    stable_commit_latency_seconds: float | None
    capture_to_presentation_overhead_seconds: float | None
    clock_map_verified: bool

    def target_free_record(self) -> dict[str, Any]:
        value = {
            "interval_id": self.interval_id,
            "cohort_id": self.cohort_id,
            "participant_id": self.participant_id,
            "endpoint": self.endpoint,
            "phase": self.phase,
            "active_intent": self.active_intent,
            "inactive_surface": self.inactive_surface,
            "duration_seconds": self.duration_seconds,
            "stable_commit": self.stable_commit,
            "predicted_command_index": self.predicted_command_index,
            "commit_count": self.commit_count,
            "invalid_chunk_count": self.invalid_chunk_count,
            "total_chunk_count": self.total_chunk_count,
            "processed_frame_count": self.processed_frame_count,
            "total_frame_count": self.total_frame_count,
            "first_output_latency_seconds": self.first_output_latency_seconds,
            "stable_commit_latency_seconds": self.stable_commit_latency_seconds,
            "capture_to_presentation_overhead_seconds": (
                self.capture_to_presentation_overhead_seconds
            ),
            "clock_map_verified": self.clock_map_verified,
        }
        core.assert_target_free(value)
        return value


@dataclass(frozen=True, slots=True)
class GeneratedLiveScoreAuthorization:
    """One-shot ordering facts supplied to the scorer capability."""

    prediction_freeze_green: bool
    target_delivery_count: int
    prior_score_count: int


def _finite_nonnegative(value: float | None) -> bool:
    return value is not None and math.isfinite(float(value)) and float(value) >= 0.0


def _percentile(values: Sequence[float], quantile: float) -> float:
    if not values:
        return math.inf
    ordered = sorted(float(value) for value in values)
    return ordered[max(0, math.ceil(quantile * len(ordered)) - 1)]


def _validate_authorization(authorization: GeneratedLiveScoreAuthorization) -> None:
    if not authorization.prediction_freeze_green:
        raise core.CommP0GeneratedRefusal("score_before_exact_green_freeze")
    if authorization.target_delivery_count != 1 or authorization.prior_score_count != 0:
        raise core.CommP0GeneratedRefusal("repeated_score_or_target_delivery")


def _live_manifest(
    trial_rows: Sequence[core.TrialPlan], contract: Mapping[str, Any]
) -> tuple[dict[str, core.TrialPlan], tuple[str, ...]]:
    expected = contract["trial_grammar"]["replication_live_rows_per_participant"]
    active = {
        row.item_id: row
        for row in trial_rows
        if row.cohort_id == LIVE_COHORT
        and row.phase == LIVE_PHASE
        and row.endpoint in core.ENDPOINTS
    }
    participants = tuple(sorted({row.participant_id for row in active.values()}))
    required_participants = int(
        contract["participant_first_scoring"]["complete_participants_denominator"]
    )
    if len(participants) != required_participants:
        raise core.CommP0GeneratedRefusal("cohort_cardinality_or_replacement_rule_violation")
    for participant_id in participants:
        rows = [row for row in active.values() if row.participant_id == participant_id]
        for endpoint in core.ENDPOINTS:
            count = sum(row.endpoint == endpoint for row in rows)
            if count != int(expected[endpoint]):
                raise core.CommP0GeneratedRefusal(
                    "required_control_condition_missing_duplicated_or_substituted"
                )
    return active, participants


def _validate_prediction_inventory(
    predictions: Sequence[numerical.CompactPrediction],
    manifest: Mapping[str, core.TrialPlan],
    participants: Sequence[str],
    contract: Mapping[str, Any],
    prediction_freeze: Mapping[str, Any],
) -> dict[tuple[str, str], numerical.CompactPrediction]:
    conditions = tuple(contract["conditions"])
    expected_keys = {(item_id, condition) for item_id in manifest for condition in conditions}
    by_key: dict[tuple[str, str], numerical.CompactPrediction] = {}
    for prediction in predictions:
        prediction.public_record()
        if prediction.cohort_id != LIVE_COHORT or prediction.phase != LIVE_PHASE:
            raise core.CommP0GeneratedRefusal(
                "pooled_result_or_other_cohort_rescues_failed_cohort"
            )
        trial = manifest.get(prediction.item_id)
        if (
            trial is None
            or prediction.participant_id != trial.participant_id
            or prediction.endpoint != trial.endpoint
            or prediction.condition not in conditions
        ):
            raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
        core.validate_probability_vector(prediction.probabilities)
        key = (prediction.item_id, prediction.condition)
        if key in by_key:
            raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")
        by_key[key] = prediction
    if set(by_key) != expected_keys:
        raise core.CommP0GeneratedRefusal("prediction_inventory_missing_or_duplicate")

    expected_rows = len(manifest) * len(conditions)
    expected_sets = len(participants) * len(conditions) * len(core.ENDPOINTS)
    rebuilt = core.build_prediction_freeze(
        (prediction.public_record() for prediction in predictions),
        expected_rows=expected_rows,
        expected_sets=expected_sets,
    )
    if dict(prediction_freeze) != rebuilt:
        raise core.CommP0GeneratedRefusal("prediction_row_or_probability_tamper_after_freeze")
    return by_key


def _validate_delivered_targets(
    delivered_targets: Mapping[str, int], manifest: Mapping[str, core.TrialPlan]
) -> dict[str, int]:
    if set(delivered_targets) != set(manifest):
        raise core.CommP0GeneratedRefusal("scorer_prediction_target_row_mismatch")
    values = {item_id: int(value) for item_id, value in delivered_targets.items()}
    if any(value not in range(len(core.COMMANDS)) for value in values.values()):
        raise core.CommP0GeneratedRefusal("scorer_prediction_target_row_mismatch")
    return values


def _validate_observations(
    observations: Sequence[GeneratedLiveObservation],
    manifest: Mapping[str, core.TrialPlan],
    participants: Sequence[str],
) -> tuple[dict[str, GeneratedLiveObservation], tuple[GeneratedLiveObservation, ...]]:
    if len({row.interval_id for row in observations}) != len(observations):
        raise core.CommP0GeneratedRefusal("false_commit_or_chatter_rate_above_maximum")
    allowed_participants = set(participants)
    active: dict[str, GeneratedLiveObservation] = {}
    inactive: list[GeneratedLiveObservation] = []
    for row in observations:
        row.target_free_record()
        if (
            row.cohort_id != LIVE_COHORT
            or row.phase != LIVE_PHASE
            or row.participant_id not in allowed_participants
            or not _finite_nonnegative(row.duration_seconds)
            or row.duration_seconds == 0.0
            or isinstance(row.commit_count, bool)
            or row.commit_count < 0
            or row.invalid_chunk_count < 0
            or row.total_chunk_count <= 0
            or row.invalid_chunk_count > row.total_chunk_count
            or row.processed_frame_count < 0
            or row.total_frame_count <= 0
            or row.processed_frame_count > row.total_frame_count
        ):
            raise core.CommP0GeneratedRefusal("live_required_metric_missing")
        if row.active_intent:
            trial = manifest.get(row.interval_id)
            if (
                trial is None
                or row.endpoint != trial.endpoint
                or row.inactive_surface is not None
                or row.interval_id in active
            ):
                raise core.CommP0GeneratedRefusal("live_required_metric_missing")
            if row.stable_commit:
                if (
                    row.predicted_command_index not in range(len(core.COMMANDS))
                    or row.commit_count < 1
                    or row.clock_map_verified is not True
                    or not _finite_nonnegative(row.first_output_latency_seconds)
                    or not _finite_nonnegative(row.stable_commit_latency_seconds)
                    or not _finite_nonnegative(row.capture_to_presentation_overhead_seconds)
                ):
                    raise core.CommP0GeneratedRefusal(
                        "capture_to_presentation_overhead_or_clock_map_failure"
                    )
            elif row.predicted_command_index is not None:
                raise core.CommP0GeneratedRefusal("live_required_metric_missing")
            active[row.interval_id] = row
        else:
            if row.endpoint is not None or row.inactive_surface not in INACTIVE_SURFACES:
                raise core.CommP0GeneratedRefusal("live_required_metric_missing")
            if row.commit_count and row.clock_map_verified is not True:
                raise core.CommP0GeneratedRefusal(
                    "capture_to_presentation_overhead_or_clock_map_failure"
                )
            inactive.append(row)
    if set(active) != set(manifest):
        raise core.CommP0GeneratedRefusal("live_required_metric_missing")
    if {row.inactive_surface for row in inactive} != INACTIVE_SURFACES:
        raise core.CommP0GeneratedRefusal("live_required_metric_missing")
    return active, tuple(inactive)


def _balanced_accuracy(targets: Sequence[int], predictions: Sequence[int | None]) -> float:
    recalls = []
    for command_index in range(len(core.COMMANDS)):
        indices = [index for index, value in enumerate(targets) if value == command_index]
        if not indices:
            recalls.append(0.0)
        else:
            recalls.append(
                sum(predictions[index] == command_index for index in indices) / len(indices)
            )
    return sum(recalls) / len(recalls)


def _classification_summary(
    endpoint: str,
    participants: Sequence[str],
    manifest: Mapping[str, core.TrialPlan],
    prediction_by_key: Mapping[tuple[str, str], numerical.CompactPrediction],
    delivered_targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    spec = contract["participant_first_scoring"]
    candidate = str(spec["primary_condition"])
    ll_controls = tuple(spec["primary_log_loss_comparators"])
    ba_controls = tuple(spec["balanced_accuracy_comparator_inventory"])
    if endpoint == "prompted_intend":
        ba_controls = tuple(control for control in ba_controls if control != "cue_only")
    participant_margins: list[float] = []
    accuracy_margins: list[float] = []
    candidate_losses: list[float] = []
    candidate_accuracies: list[float] = []
    for participant_id in participants:
        item_ids = sorted(
            item_id
            for item_id, trial in manifest.items()
            if trial.participant_id == participant_id and trial.endpoint == endpoint
        )
        true_values = [delivered_targets[item_id] for item_id in item_ids]
        losses: dict[str, float] = {}
        accuracies: dict[str, float] = {}
        for condition in contract["conditions"]:
            probabilities = [prediction_by_key[(item_id, condition)].probabilities for item_id in item_ids]
            losses[condition] = sum(
                -math.log(max(float(row[truth]), float(spec["probability_floor"])))
                for row, truth in zip(probabilities, true_values, strict=True)
            ) / len(item_ids)
            predicted = [max(range(len(row)), key=lambda index: (row[index], -index)) for row in probabilities]
            accuracies[condition] = _balanced_accuracy(true_values, predicted)
        margin = min(
            losses[ll_controls[0]] - losses[candidate],
            losses[ll_controls[1]] - losses[candidate],
        )
        participant_margins.append(margin)
        accuracy_margins.append(
            accuracies[candidate] - max(accuracies[control] for control in ba_controls)
        )
        candidate_losses.append(losses[candidate])
        candidate_accuracies.append(accuracies[candidate])
    mean_margin = sum(participant_margins) / len(participant_margins)
    mean_accuracy_margin = sum(accuracy_margins) / len(accuracy_margins)
    return {
        "participant_count": len(participants),
        "assigned_active_episodes": sum(
            trial.endpoint == endpoint for trial in manifest.values()
        ),
        "participant_macro_log_loss": sum(candidate_losses) / len(candidate_losses),
        "participant_macro_balanced_accuracy": (
            sum(candidate_accuracies) / len(candidate_accuracies)
        ),
        "mean_log_loss_margin_over_both_registered_controls": mean_margin,
        "positive_log_loss_margin_participants": sum(
            value > 0.0 for value in participant_margins
        ),
        "mean_balanced_accuracy_margin_over_registered_controls": mean_accuracy_margin,
        "directional_pass": bool(
            mean_margin > 0.0
            and sum(value > 0.0 for value in participant_margins)
            >= int(spec["positive_participants_minimum"])
            and mean_accuracy_margin > 0.0
        ),
        "exact_sign_flip_performed": False,
    }


def _endpoint_live_summary(
    endpoint: str,
    participants: Sequence[str],
    manifest: Mapping[str, core.TrialPlan],
    active: Mapping[str, GeneratedLiveObservation],
    delivered_targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live = contract["live_metrics"]
    rows = [
        active[item_id]
        for item_id, trial in manifest.items()
        if trial.endpoint == endpoint
    ]
    per_participant = []
    for participant_id in participants:
        participant_rows = [row for row in rows if row.participant_id == participant_id]
        per_participant.append(
            sum(
                row.stable_commit
                and row.invalid_chunk_count == 0
                and float(row.stable_commit_latency_seconds or math.inf)
                <= float(live["stable_commit_latency_p95_seconds_maximum"])
                for row in participant_rows
            )
            / len(participant_rows)
        )
    per_command: dict[str, list[bool]] = defaultdict(list)
    first_latencies: list[float] = []
    stable_latencies: list[float] = []
    overheads: list[float] = []
    committed_predictions: list[int | None] = []
    true_values: list[int] = []
    for row in rows:
        truth = delivered_targets[row.interval_id]
        covered = bool(
            row.stable_commit
            and row.invalid_chunk_count == 0
            and float(row.stable_commit_latency_seconds or math.inf)
            <= float(live["stable_commit_latency_p95_seconds_maximum"])
        )
        per_command[core.COMMANDS[truth]].append(covered)
        true_values.append(truth)
        committed_predictions.append(row.predicted_command_index if covered else None)
        if row.first_output_latency_seconds is not None:
            first_latencies.append(float(row.first_output_latency_seconds))
        if row.stable_commit and row.invalid_chunk_count == 0:
            stable_latencies.append(float(row.stable_commit_latency_seconds or math.inf))
            overheads.append(float(row.capture_to_presentation_overhead_seconds or math.inf))
    command_coverage = {
        command: sum(per_command[command]) / len(per_command[command])
        if per_command[command]
        else 0.0
        for command in core.COMMANDS
    }
    participant_macro_coverage = sum(per_participant) / len(per_participant)
    summary = {
        "participant_macro_coverage": participant_macro_coverage,
        "per_command_coverage": command_coverage,
        "missed_activation_fraction": 1.0 - participant_macro_coverage,
        "abstention_fraction": sum(value is None for value in committed_predictions)
        / len(committed_predictions),
        "commit_balanced_accuracy": _balanced_accuracy(true_values, committed_predictions),
        "first_output_latency_median_seconds": (
            median(first_latencies) if first_latencies else math.inf
        ),
        "first_output_latency_p95_seconds": _percentile(first_latencies, 0.95),
        "stable_commit_latency_median_seconds": (
            median(stable_latencies) if stable_latencies else math.inf
        ),
        "stable_commit_latency_p95_seconds": _percentile(stable_latencies, 0.95),
        "capture_to_presentation_processing_overhead_p95_seconds": _percentile(
            overheads, 0.95
        ),
    }
    summary["active_operational_pass"] = bool(
        participant_macro_coverage >= float(live["stable_commit_coverage_fraction_minimum"])
        and all(
            value >= float(live["per_command_coverage_fraction_minimum"])
            for value in command_coverage.values()
        )
        and summary["stable_commit_latency_median_seconds"]
        <= float(live["stable_commit_latency_median_seconds_maximum"])
        and summary["stable_commit_latency_p95_seconds"]
        <= float(live["stable_commit_latency_p95_seconds_maximum"])
        and summary["capture_to_presentation_processing_overhead_p95_seconds"]
        <= float(live["capture_to_presentation_processing_overhead_p95_seconds_maximum"])
    )
    return summary


def _shared_metrics(
    observations: Sequence[GeneratedLiveObservation],
    inactive: Sequence[GeneratedLiveObservation],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live = contract["live_metrics"]
    inactive_seconds = sum(row.duration_seconds for row in inactive)
    false_commits = sum(row.commit_count for row in inactive)
    total_chunks = sum(row.total_chunk_count for row in observations)
    invalid_chunks = sum(row.invalid_chunk_count for row in observations)
    total_frames = sum(row.total_frame_count for row in observations)
    processed_frames = sum(row.processed_frame_count for row in observations)
    false_rate = false_commits / (inactive_seconds / 60.0) if inactive_seconds else math.inf
    dropped_fraction = invalid_chunks / total_chunks
    deadline_fraction = processed_frames / total_frames
    return {
        "inactive_interval_count": len(inactive),
        "inactive_duration_seconds": inactive_seconds,
        "false_commit_count": false_commits,
        "false_commits_per_inactive_minute": false_rate,
        "inactive_surfaces_counted_once": sorted(INACTIVE_SURFACES),
        "dropped_or_invalid_chunk_fraction": dropped_fraction,
        "frames_processed_before_next_deadline_fraction": deadline_fraction,
        "passes": bool(
            false_rate <= float(live["false_commits_per_inactive_minute_maximum"])
            and dropped_fraction <= float(live["dropped_or_invalid_chunk_fraction_maximum"])
            and deadline_fraction
            >= float(live["frames_processed_before_next_deadline_fraction_minimum"])
        ),
    }


def score_generated_replication_live(
    predictions: Sequence[numerical.CompactPrediction],
    trial_rows: Sequence[core.TrialPlan],
    observations: Sequence[GeneratedLiveObservation],
    delivered_targets: Mapping[str, int],
    prediction_freeze: Mapping[str, Any],
    authorization: GeneratedLiveScoreAuthorization,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Score one generated replication live delivery into a target-free aggregate."""

    _validate_authorization(authorization)
    manifest, participants = _live_manifest(trial_rows, contract)
    prediction_by_key = _validate_prediction_inventory(
        predictions, manifest, participants, contract, prediction_freeze
    )
    target_values = _validate_delivered_targets(delivered_targets, manifest)
    active, inactive = _validate_observations(observations, manifest, participants)
    shared = _shared_metrics(observations, inactive, contract)

    endpoint_results: dict[str, dict[str, Any]] = {}
    for endpoint in core.ENDPOINTS:
        classification = _classification_summary(
            endpoint,
            participants,
            manifest,
            prediction_by_key,
            target_values,
            contract,
        )
        operational = _endpoint_live_summary(
            endpoint, participants, manifest, active, target_values, contract
        )
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
    result = {
        "schema_name": "neurodecodekit.comm_p0_generated_live_score",
        "schema_version": "0.1.0",
        "gate_id": core.GATE_ID,
        "cohort": LIVE_COHORT,
        "score_count": 1,
        "target_delivery_count": 1,
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
        "claim_boundary": {
            "generated_only": True,
            "aggregate_only": True,
            "contains_individual_records": False,
            "end_to_end_latency_measured": False,
            "scientific_claim_established": False,
        },
    }
    core.assert_target_free(result)
    return result
