"""Bounded-memory aggregate scoring for generated COMM-P0 prediction streams.

The scorer makes one target-free verification pass and one post-delivery scoring
pass over the same logical prediction stream. It retains only a duplicate bitset
and participant-level metric accumulators, never the complete prediction rows.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from neurodecodekit.experiments import comm_p0_generated_score_only as score_only

SCHEMA_VERSION = "0.1.0"
MAXIMUM_PREDICTION_ROWS_BUFFERED = 1


@dataclass
class _ConditionState:
    loss_sum: float = 0.0
    observed: int = 0
    invalid: int = 0
    correct_by_target: list[int] = field(default_factory=lambda: [0, 0, 0, 0])


@dataclass
class _GroupState:
    expected: int = 0
    target_counts: list[int] = field(default_factory=lambda: [0, 0, 0, 0])
    conditions: dict[str, _ConditionState] = field(default_factory=dict)


def _prediction_freeze_from_stream(
    records: Iterable[Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    conditions = score_only._validate_contract(contract)
    digest = hashlib.sha256()
    participants: set[str] = set()
    endpoints: set[str] = set()
    observed_conditions: set[str] = set()
    rows = 0
    for index, value in enumerate(records):
        if not isinstance(value, Mapping):
            raise score_only.ScoreOnlyRefusal("noncanonical_record", f"predictions[{index}]")
        record = dict(value)
        score_only._assert_target_free(record)
        digest.update(score_only.canonical_json_bytes(record))
        participants.add(str(record.get("participant_id", "")))
        endpoints.add(str(record.get("endpoint", "")))
        observed_conditions.add(str(record.get("condition", "")))
        rows += 1
    participants.discard("")
    endpoints.intersection_update(score_only.ENDPOINTS)
    observed_conditions.intersection_update(conditions)
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_prediction_freeze",
        "schema_version": str(contract.get("schema_version", SCHEMA_VERSION)),
        "gate_id": str(contract["gate_id"]),
        "prediction_rows": rows,
        "prediction_sets": len(participants) * len(observed_conditions) * len(endpoints),
        "private_prediction_stream_sha256": digest.hexdigest(),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }


def build_prediction_freeze_attestation(
    prediction_records: Iterable[Mapping[str, Any]], contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Build the existing freeze schema without collecting prediction rows."""

    return _prediction_freeze_from_stream(prediction_records, contract)


def _group_keys(trial: Mapping[str, Any]) -> tuple[tuple[str, str, str, str], ...]:
    cohort = str(trial["cohort_id"])
    participant = str(trial["participant_id"])
    endpoint = str(trial["endpoint"])
    phase = str(trial["phase"])
    keys: list[tuple[str, str, str, str]] = []
    if cohort == score_only.LIVE_COHORT and phase == score_only.LIVE_PHASE:
        keys.append(("live", "all", participant, endpoint))
    if cohort == "discovery" or phase == "shadow":
        keys.append(("shadow", cohort, participant, endpoint))
    return tuple(keys)


def _initialize_groups(
    manifest: Mapping[str, Mapping[str, Any]],
    targets: Mapping[str, int],
    conditions: Sequence[str],
) -> dict[tuple[str, str, str, str], _GroupState]:
    groups: dict[tuple[str, str, str, str], _GroupState] = {}
    for item_id, trial in manifest.items():
        if trial.get("endpoint") not in score_only.ENDPOINTS:
            continue
        truth = targets[item_id]
        for key in _group_keys(trial):
            group = groups.setdefault(key, _GroupState())
            group.expected += 1
            group.target_counts[truth] += 1
    for group in groups.values():
        group.conditions = {condition: _ConditionState() for condition in conditions}
    return groups


def _consume_predictions(
    records: Iterable[Mapping[str, Any]],
    *,
    contract: Mapping[str, Any],
    manifest: Mapping[str, Mapping[str, Any]],
    active_item_ids: Sequence[str],
    targets: Mapping[str, int],
    conditions: Sequence[str],
) -> tuple[
    dict[tuple[str, str, str, str], _GroupState],
    dict[str, int],
    dict[str, Any],
]:
    command_count = len(score_only._contract_value(contract, "trial_grammar")["commands"])
    scoring = score_only._contract_value(contract, "participant_first_scoring")
    floor = float(scoring["probability_floor"])
    maximum_loss = float(scoring["maximum_frozen_log_loss"])
    item_positions = {item_id: index for index, item_id in enumerate(active_item_ids)}
    condition_positions = {condition: index for index, condition in enumerate(conditions)}
    expected_pairs = len(item_positions) * len(condition_positions)
    seen = bytearray((expected_pairs + 7) // 8)
    groups = _initialize_groups(manifest, targets, conditions)
    quality = {
        "assigned_prediction_rows": expected_pairs,
        "present_prediction_rows": 0,
        "missing_prediction_rows_retained": 0,
        "invalid_prediction_rows_retained": 0,
        "valid_prediction_rows": 0,
        "rows_dropped": 0,
    }
    digest = hashlib.sha256()
    participants: set[str] = set()
    endpoints: set[str] = set()
    observed_conditions: set[str] = set()

    for index, value in enumerate(records):
        if not isinstance(value, Mapping):
            raise score_only.ScoreOnlyRefusal("noncanonical_record", f"predictions[{index}]")
        record = dict(value)
        score_only._assert_target_free(record)
        digest.update(score_only.canonical_json_bytes(record))
        item_id = str(record.get("item_id", ""))
        condition = str(record.get("condition", ""))
        trial = manifest.get(item_id)
        if trial is None or item_id not in item_positions or condition not in condition_positions:
            raise score_only.ScoreOnlyRefusal("prediction_inventory_missing_duplicate_or_mismatch")
        if (
            str(record.get("cohort_id", "")) != str(trial.get("cohort_id", ""))
            or str(record.get("participant_id", "")) != str(trial.get("participant_id", ""))
            or record.get("endpoint") != trial.get("endpoint")
            or str(record.get("phase", "")) != str(trial.get("phase", ""))
        ):
            raise score_only.ScoreOnlyRefusal("prediction_inventory_missing_duplicate_or_mismatch")
        pair_index = item_positions[item_id] * len(conditions) + condition_positions[condition]
        byte_index, bit_index = divmod(pair_index, 8)
        mask = 1 << bit_index
        if seen[byte_index] & mask:
            raise score_only.ScoreOnlyRefusal("prediction_inventory_missing_duplicate_or_mismatch")
        seen[byte_index] |= mask
        quality["present_prediction_rows"] += 1
        participants.add(str(record["participant_id"]))
        endpoints.add(str(record["endpoint"]))
        observed_conditions.add(condition)

        truth = targets[item_id]
        probability = score_only._validated_probabilities(
            record.get("probabilities"), command_count
        )
        invalid = probability is None
        quality["invalid_prediction_rows_retained" if invalid else "valid_prediction_rows"] += 1
        for key in _group_keys(trial):
            state = groups[key].conditions[condition]
            state.observed += 1
            if invalid:
                state.loss_sum += maximum_loss
                state.invalid += 1
            else:
                assert probability is not None
                state.loss_sum += -math.log(max(probability[truth], floor))
                predicted = max(
                    range(command_count), key=lambda command: (probability[command], -command)
                )
                state.correct_by_target[truth] += int(predicted == truth)

    missing = expected_pairs - quality["present_prediction_rows"]
    quality["missing_prediction_rows_retained"] = missing
    freeze = {
        "schema_name": "neurodecodekit.comm_p0_generated_prediction_freeze",
        "schema_version": str(contract.get("schema_version", SCHEMA_VERSION)),
        "gate_id": str(contract["gate_id"]),
        "prediction_rows": quality["present_prediction_rows"],
        "prediction_sets": len(participants) * len(observed_conditions) * len(endpoints),
        "private_prediction_stream_sha256": digest.hexdigest(),
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
    }
    return groups, quality, freeze


def _condition_metrics(
    group: _GroupState, condition: str, maximum_loss: float
) -> tuple[float, float, int]:
    state = group.conditions[condition]
    missing = group.expected - state.observed
    loss = (state.loss_sum + missing * maximum_loss) / group.expected
    recalls = [
        state.correct_by_target[index] / group.target_counts[index]
        if group.target_counts[index]
        else 0.0
        for index in range(4)
    ]
    return loss, sum(recalls) / 4, state.invalid + missing


def _participant_metric(
    group: _GroupState, contract: Mapping[str, Any], *, prompted: bool
) -> dict[str, float]:
    scoring = score_only._contract_value(contract, "participant_first_scoring")
    conditions = tuple(str(value) for value in contract["conditions"])
    maximum_loss = float(scoring["maximum_frozen_log_loss"])
    metrics = {
        condition: _condition_metrics(group, condition, maximum_loss) for condition in conditions
    }
    candidate = str(scoring["primary_condition"])
    loss_controls = tuple(str(value) for value in scoring["primary_log_loss_comparators"])
    accuracy_controls = tuple(
        str(value) for value in scoring["balanced_accuracy_comparator_inventory"]
    )
    if prompted:
        accuracy_controls = tuple(value for value in accuracy_controls if value != "cue_only")
    return {
        "margin": min(metrics[value][0] - metrics[candidate][0] for value in loss_controls),
        "accuracy_margin": metrics[candidate][1]
        - max(metrics[value][1] for value in accuracy_controls),
        "candidate_loss": metrics[candidate][0],
        "candidate_accuracy": metrics[candidate][1],
        "invalid_assignments": float(sum(value[2] for value in metrics.values())),
    }


def _metric_rows(
    groups: Mapping[tuple[str, str, str, str], _GroupState],
    *,
    kind: str,
    cohort: str,
    endpoint: str,
    contract: Mapping[str, Any],
) -> list[dict[str, float]]:
    selected = [
        (key, group)
        for key, group in groups.items()
        if key[0] == kind and key[1] == cohort and key[3] == endpoint
    ]
    return [
        _participant_metric(group, contract, prompted=endpoint == "prompted_intend")
        for _, group in sorted(selected)
    ]


def _shadow_summary(
    groups: Mapping[tuple[str, str, str, str], _GroupState],
    cohort: str,
    endpoint: str,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    scoring = score_only._contract_value(contract, "participant_first_scoring")
    metrics = _metric_rows(
        groups, kind="shadow", cohort=cohort, endpoint=endpoint, contract=contract
    )
    expected = int(scoring["complete_participants_denominator"])
    if len(metrics) != expected:
        raise score_only.ScoreOnlyRefusal("cohort_cardinality_or_replacement_rule_violation")
    decimals = int(scoring.get("participant_metric_decimal_places", 12))
    margins = [round(row["margin"], decimals) for row in metrics]
    accuracy_margins = [row["accuracy_margin"] for row in metrics]
    p_value, assignments = score_only._exact_sign_flip(margins)
    result: dict[str, Any] = {
        "participant_count": len(metrics),
        "assigned_active_episodes": sum(
            group.expected
            for key, group in groups.items()
            if key[0] == "shadow" and key[1] == cohort and key[3] == endpoint
        ),
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
    required_positive = int(scoring["positive_participants_minimum"])
    if endpoint == "free_choice_intend":
        result["passes"] = bool(
            result["mean_margin_nats_per_item"]
            >= float(scoring["mean_margin_nats_per_item_minimum"])
            and result["positive_participants"] >= required_positive
            and result["exact_one_sided_sign_flip_p"]
            <= float(scoring["exact_one_sided_sign_flip_p_maximum"])
            and result["mean_balanced_accuracy_margin"]
            >= float(scoring["balanced_accuracy_margin_minimum"])
        )
    else:
        result.update(
            {
                "passes_directional_controls": bool(
                    result["mean_margin_nats_per_item"] > 0.0
                    and result["positive_participants"] >= required_positive
                    and result["mean_balanced_accuracy_margin"] > 0.0
                ),
                "cue_only_reported_as_leakage_ceiling": True,
                "may_rescue_free_choice_failure": False,
            }
        )
    return result


def _live_classification(
    groups: Mapping[tuple[str, str, str, str], _GroupState],
    endpoint: str,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    scoring = score_only._contract_value(contract, "participant_first_scoring")
    metrics = _metric_rows(groups, kind="live", cohort="all", endpoint=endpoint, contract=contract)
    mean_margin = sum(row["margin"] for row in metrics) / len(metrics)
    mean_accuracy = sum(row["accuracy_margin"] for row in metrics) / len(metrics)
    return {
        "participant_count": len(metrics),
        "assigned_active_episodes": sum(
            group.expected
            for key, group in groups.items()
            if key[0] == "live" and key[3] == endpoint
        ),
        "primary_condition": str(scoring["primary_condition"]),
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


def _live_summary(
    manifest: Mapping[str, Mapping[str, Any]],
    groups: Mapping[tuple[str, str, str, str], _GroupState],
    observations: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    live_manifest = {
        item_id: row
        for item_id, row in manifest.items()
        if row.get("cohort_id") == score_only.LIVE_COHORT
        and row.get("phase") == score_only.LIVE_PHASE
        and row.get("endpoint") in score_only.ENDPOINTS
    }
    participants = sorted({str(row["participant_id"]) for row in live_manifest.values()})
    active, inactive, structural_invalid = score_only._observation_inventory(
        observations, live_manifest, participants
    )
    shared = score_only._shared_live_metrics(observations, inactive, contract)
    shared["missing_or_structurally_invalid_active_observations_retained"] = structural_invalid
    if structural_invalid:
        shared["passes"] = False
    endpoint_results: dict[str, dict[str, Any]] = {}
    for endpoint in score_only.ENDPOINTS:
        classification = _live_classification(groups, endpoint, contract)
        operational = score_only._endpoint_live_summary(
            endpoint, live_manifest, active, targets, contract
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


def score_records(
    *,
    contract: Mapping[str, Any],
    trial_records: Sequence[Mapping[str, Any]],
    prediction_pass_factory: Callable[[], Iterable[Mapping[str, Any]]],
    live_observation_records: Sequence[Mapping[str, Any]],
    freeze_attestation: Mapping[str, Any],
    authorization: Mapping[str, Any],
    delivered_targets: Mapping[str, Any],
) -> dict[str, Any]:
    """Score a replay with two bounded prediction passes and compact state."""

    score_only._validate_authorization(authorization)
    conditions = score_only._validate_contract(contract)
    first_freeze = _prediction_freeze_from_stream(prediction_pass_factory(), contract)
    if not isinstance(freeze_attestation, Mapping) or dict(freeze_attestation) != first_freeze:
        raise score_only.ScoreOnlyRefusal("prediction_freeze_attestation_mismatch")
    freeze_sha256 = score_only.sha256_json(first_freeze)
    manifest, active_item_ids = score_only._trial_inventory(trial_records, contract)
    commands = tuple(
        str(value)
        for value in score_only._contract_value(contract, "trial_grammar").get("commands", ())
    )
    if len(commands) != 4:
        raise score_only.ScoreOnlyRefusal("contract_mismatch", "four_command_inventory")
    targets = score_only._targets_for_active(delivered_targets, active_item_ids, len(commands))
    groups, quality, second_freeze = _consume_predictions(
        prediction_pass_factory(),
        contract=contract,
        manifest=manifest,
        active_item_ids=active_item_ids,
        targets=targets,
        conditions=conditions,
    )
    if second_freeze != first_freeze:
        raise score_only.ScoreOnlyRefusal("prediction_row_or_probability_tamper_after_freeze")

    cohorts = []
    for cohort in score_only.COHORTS:
        free_choice = _shadow_summary(groups, cohort, "free_choice_intend", contract)
        prompted = _shadow_summary(groups, cohort, "prompted_intend", contract)
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
    result = {
        "schema_name": "neurodecodekit.comm_p0_generated_score_only_aggregate",
        "schema_version": SCHEMA_VERSION,
        "gate_id": str(contract["gate_id"]),
        "prediction_freeze_sha256": freeze_sha256,
        "prediction_quality": quality,
        "cohorts": cohorts,
        "replication_live": _live_summary(
            manifest, groups, live_observation_records, targets, contract
        ),
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
    score_only._assert_aggregate_private(result)
    score_only.canonical_json_bytes(result)
    return result


def capability_audit() -> dict[str, Any]:
    return {
        "schema_name": "neurodecodekit.comm_p0_generated_streaming_score_capability_audit",
        "schema_version": SCHEMA_VERSION,
        "standard_library_only": True,
        "prediction_passes": 2,
        "maximum_prediction_rows_buffered": MAXIMUM_PREDICTION_ROWS_BUFFERED,
        "complete_prediction_records_materialized": False,
        "fit_or_model_capability": False,
        "file_read_or_write_capability": False,
        "network_capability": False,
        "real_or_private_data_capability": False,
        "row_level_output_capability": False,
    }
