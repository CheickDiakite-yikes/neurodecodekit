"""Prediction freezing and aggregate-only scoring for DREYER-C5R-1."""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Any, Mapping, Sequence


CONDITIONS = (
    "equal_prior",
    "timing_only",
    "EOG_only",
    "EMG_only",
    "posterior_only",
    "late_N",
    "late_central_E",
    "late_residual_R",
    "late_N_plus_R",
    "late_N_plus_deranged_R",
    "late_N_without_posterior",
    "late_N_without_posterior_plus_R",
    "pre_N",
    "pre_N_plus_R",
    "cue_N",
    "cue_N_plus_R",
    "source_label_rotated_late_N_plus_R",
)


class DreyerScoreRefusal(RuntimeError):
    """Fail-closed refusal for malformed or unfrozen predictions."""


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _prediction_identity(row: Mapping[str, Any]) -> tuple[str, int, int, str]:
    try:
        participant = str(row["participant"])
        run = int(row["run"])
        trial = int(row["trial"])
        row_id = str(row["row_id"])
    except (KeyError, TypeError, ValueError) as exc:
        raise DreyerScoreRefusal("prediction identity is malformed") from exc
    if not participant or run < 1 or trial < 0 or not row_id:
        raise DreyerScoreRefusal("prediction identity is outside the allowed domain")
    return participant, run, trial, row_id


def _probabilities(row: Mapping[str, Any]) -> tuple[float, float]:
    values = row.get("probabilities")
    if not isinstance(values, list) or len(values) != 2:
        raise DreyerScoreRefusal("binary probability inventory differs")
    try:
        first, second = (float(values[0]), float(values[1]))
    except (TypeError, ValueError) as exc:
        raise DreyerScoreRefusal("probability value is malformed") from exc
    if not all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in (first, second)):
        raise DreyerScoreRefusal("probability is non-finite or outside zero to one")
    if not math.isclose(first + second, 1.0, rel_tol=0.0, abs_tol=1e-10):
        raise DreyerScoreRefusal("binary probabilities do not sum to one")
    return first, second


def validate_prediction_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_participants: int,
    expected_rows_per_participant: int,
) -> list[dict[str, Any]]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise DreyerScoreRefusal("prediction rows are not a sequence")
    normalized: list[dict[str, Any]] = []
    inventory: dict[tuple[str, int, int, str], set[str]] = defaultdict(set)
    row_ids: dict[str, tuple[str, int, int]] = {}
    for source in rows:
        if not isinstance(source, Mapping):
            raise DreyerScoreRefusal("prediction row is not an object")
        participant, run, trial, row_id = _prediction_identity(source)
        condition = str(source.get("condition", ""))
        if condition not in CONDITIONS:
            raise DreyerScoreRefusal("prediction condition differs from the frozen inventory")
        probability = _probabilities(source)
        identity = (participant, run, trial, row_id)
        if condition in inventory[identity]:
            raise DreyerScoreRefusal("duplicate prediction identity and condition")
        inventory[identity].add(condition)
        prior = row_ids.setdefault(row_id, (participant, run, trial))
        if prior != (participant, run, trial):
            raise DreyerScoreRefusal("row ID maps to multiple identities")
        normalized.append(
            {
                "participant": participant,
                "run": run,
                "trial": trial,
                "row_id": row_id,
                "condition": condition,
                "probabilities": [probability[0], probability[1]],
            }
        )
    if not inventory or any(values != set(CONDITIONS) for values in inventory.values()):
        raise DreyerScoreRefusal("prediction condition grid is incomplete")
    participants: dict[str, int] = defaultdict(int)
    for participant, _run, _trial, _row_id in inventory:
        participants[participant] += 1
    if len(participants) != expected_participants:
        raise DreyerScoreRefusal("prediction participant count differs")
    if any(count != expected_rows_per_participant for count in participants.values()):
        raise DreyerScoreRefusal("prediction rows per participant differ")
    expected_total = expected_participants * expected_rows_per_participant * len(CONDITIONS)
    if len(normalized) != expected_total:
        raise DreyerScoreRefusal("prediction row total differs")
    return sorted(
        normalized,
        key=lambda row: (
            row["participant"],
            row["run"],
            row["trial"],
            row["row_id"],
            row["condition"],
        ),
    )


def build_prediction_freeze(
    rows: Sequence[Mapping[str, Any]],
    *,
    expected_participants: int,
    expected_rows_per_participant: int,
    contract_sha256: str,
) -> dict[str, Any]:
    normalized = validate_prediction_rows(
        rows,
        expected_participants=expected_participants,
        expected_rows_per_participant=expected_rows_per_participant,
    )
    condition_hashes: dict[str, str] = {}
    for condition in CONDITIONS:
        payload = canonical_bytes([row for row in normalized if row["condition"] == condition])
        condition_hashes[condition] = sha256(payload)
    payload = canonical_bytes(normalized)
    return {
        "schema_name": "neurodecodekit.dreyer_c5r_1_prediction_freeze",
        "schema_version": "0.1.0",
        "lane_id": "DREYER-C5R-1",
        "contract_sha256": contract_sha256,
        "participant_count": expected_participants,
        "identity_rows": expected_participants * expected_rows_per_participant,
        "prediction_rows": len(normalized),
        "condition_ids": list(CONDITIONS),
        "condition_sha256": condition_hashes,
        "all_predictions_sha256": sha256(payload),
        "contains_individual_prediction_probability_target_or_outcome": false_value(),
        "targets_delivered": 0,
        "scores": 0,
    }


def false_value() -> bool:
    """Return a JSON boolean without using a magic truthy sentinel."""

    return False


def verify_prediction_freeze(
    rows: Sequence[Mapping[str, Any]],
    freeze: Mapping[str, Any],
    *,
    expected_participants: int,
    expected_rows_per_participant: int,
    contract_sha256: str,
) -> list[dict[str, Any]]:
    if not isinstance(freeze, Mapping):
        raise DreyerScoreRefusal("prediction freeze is not an object")
    rebuilt = build_prediction_freeze(
        rows,
        expected_participants=expected_participants,
        expected_rows_per_participant=expected_rows_per_participant,
        contract_sha256=contract_sha256,
    )
    if dict(freeze) != rebuilt:
        raise DreyerScoreRefusal("prediction freeze does not match private predictions")
    return validate_prediction_rows(
        rows,
        expected_participants=expected_participants,
        expected_rows_per_participant=expected_rows_per_participant,
    )


def _binary_log_loss(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    losses = []
    for target, probability in zip(targets, probabilities, strict=True):
        selected = probability if target == 1 else 1.0 - probability
        losses.append(-math.log(min(max(selected, 1e-6), 1.0 - 1e-6)))
    return math.fsum(losses) / len(losses)


def _balanced_accuracy(targets: Sequence[int], probabilities: Sequence[float]) -> float:
    recalls = []
    predictions = [int(value >= 0.5) for value in probabilities]
    for label in (0, 1):
        indices = [index for index, target in enumerate(targets) if target == label]
        if not indices:
            raise DreyerScoreRefusal("participant target class inventory is incomplete")
        recalls.append(
            sum(predictions[index] == label for index in indices) / float(len(indices))
        )
    return math.fsum(recalls) / 2.0


def _expected_calibration_error(
    targets: Sequence[int], probabilities: Sequence[float], bins: int = 10
) -> float:
    if bins != 10:
        raise DreyerScoreRefusal("ECE bin count differs from the frozen value")
    total = len(targets)
    error = 0.0
    for index in range(bins):
        low = index / bins
        high = (index + 1) / bins
        selected = [
            row
            for row, probability in enumerate(probabilities)
            if probability >= low and (probability < high or (index == bins - 1 and probability <= high))
        ]
        if not selected:
            continue
        confidence = math.fsum(probabilities[row] for row in selected) / len(selected)
        frequency = math.fsum(targets[row] for row in selected) / len(selected)
        error += len(selected) / total * abs(confidence - frequency)
    return error


def _exact_one_sided_sign_p(positive: int, total: int) -> float:
    if positive < 0 or positive > total or total < 1:
        raise DreyerScoreRefusal("sign-test inventory is invalid")
    return math.fsum(math.comb(total, value) for value in range(positive, total + 1)) / (
        2**total
    )


def _macro(values: Mapping[str, float]) -> float:
    if not values:
        raise DreyerScoreRefusal("participant metric inventory is empty")
    return math.fsum(values.values()) / len(values)


def score_frozen_predictions(
    rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    freeze: Mapping[str, Any],
    *,
    expected_participants: int,
    expected_rows_per_participant: int,
    contract_sha256: str,
    positive_participants_minimum: int,
) -> dict[str, Any]:
    normalized = verify_prediction_freeze(
        rows,
        freeze,
        expected_participants=expected_participants,
        expected_rows_per_participant=expected_rows_per_participant,
        contract_sha256=contract_sha256,
    )
    identity_rows = {
        row["row_id"]: (row["participant"], row["run"], row["trial"])
        for row in normalized
    }
    if set(targets) != set(identity_rows):
        raise DreyerScoreRefusal("delivered target identity inventory differs")
    if any(type(value) is not int or value not in (0, 1) for value in targets.values()):
        raise DreyerScoreRefusal("delivered target value differs from binary encoding")
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in normalized:
        grouped[row["participant"]][row["condition"]].append(row)
    participant_loss: dict[str, dict[str, float]] = defaultdict(dict)
    participant_accuracy: dict[str, dict[str, float]] = defaultdict(dict)
    participant_ece: dict[str, dict[str, float]] = defaultdict(dict)
    for participant, condition_rows in grouped.items():
        for condition, values in condition_rows.items():
            ordered = sorted(values, key=lambda row: (row["run"], row["trial"], row["row_id"]))
            y = [targets[row["row_id"]] for row in ordered]
            probability = [float(row["probabilities"][1]) for row in ordered]
            participant_loss[participant][condition] = _binary_log_loss(y, probability)
            participant_accuracy[participant][condition] = _balanced_accuracy(y, probability)
            participant_ece[participant][condition] = _expected_calibration_error(y, probability)
    macro_loss = {
        condition: _macro(
            {
                participant: participant_loss[participant][condition]
                for participant in sorted(participant_loss)
            }
        )
        for condition in CONDITIONS
    }
    macro_accuracy = {
        condition: _macro(
            {
                participant: participant_accuracy[participant][condition]
                for participant in sorted(participant_accuracy)
            }
        )
        for condition in CONDITIONS
    }
    macro_ece = {
        condition: _macro(
            {
                participant: participant_ece[participant][condition]
                for participant in sorted(participant_ece)
            }
        )
        for condition in CONDITIONS
    }
    nuisance_deltas = {
        participant: values["late_N"] - values["late_N_plus_R"]
        for participant, values in participant_loss.items()
    }
    deranged_deltas = {
        participant: values["late_N_plus_deranged_R"] - values["late_N_plus_R"]
        for participant, values in participant_loss.items()
    }
    nuisance_delta = _macro(nuisance_deltas)
    deranged_delta = _macro(deranged_deltas)
    positive_nuisance = sum(value > 0.0 for value in nuisance_deltas.values())
    positive_deranged = sum(value > 0.0 for value in deranged_deltas.values())
    nuisance_sign_p = _exact_one_sided_sign_p(positive_nuisance, expected_participants)
    deranged_sign_p = _exact_one_sided_sign_p(positive_deranged, expected_participants)
    posterior_ablation_delta = (
        macro_loss["late_N_without_posterior"]
        - macro_loss["late_N_without_posterior_plus_R"]
    )
    pre_delta = macro_loss["pre_N"] - macro_loss["pre_N_plus_R"]
    no_signal_or_timing = max(
        macro_accuracy["equal_prior"], macro_accuracy["timing_only"]
    )
    components = {
        "nuisance_effect_size": nuisance_delta >= 0.020,
        "deranged_effect_size": deranged_delta >= 0.020,
        "nuisance_participant_consistency": positive_nuisance
        >= positive_participants_minimum,
        "deranged_participant_consistency": positive_deranged
        >= positive_participants_minimum,
        "nuisance_sign_test": nuisance_sign_p <= 0.025,
        "deranged_sign_test": deranged_sign_p <= 0.025,
        "posterior_ablation": posterior_ablation_delta >= 0.015,
        "late_over_precue": nuisance_delta - pre_delta >= 0.010,
        "probability_log_loss": macro_loss["late_N_plus_R"] < math.log(2.0),
        "probability_ECE": macro_ece["late_N_plus_R"] <= 0.10,
        "balanced_accuracy": macro_accuracy["late_N_plus_R"] >= 0.60,
        "no_signal_or_timing_margin": macro_accuracy["late_N_plus_R"]
        - no_signal_or_timing
        >= 0.05,
    }
    if all(components.values()):
        route = "DREYERC5R-R1"
    elif nuisance_delta > 0.0 or macro_accuracy["late_N_plus_R"] > no_signal_or_timing:
        route = "DREYERC5R-R2"
    else:
        route = "DREYERC5R-R3"
    return {
        "schema_name": "neurodecodekit.dreyer_c5r_1_aggregate_score",
        "schema_version": "0.1.0",
        "lane_id": "DREYER-C5R-1",
        "route": route,
        "primary_gate_passed": route == "DREYERC5R-R1",
        "primary_components": components,
        "aggregate_metrics": {
            "participant_macro_log_loss": macro_loss,
            "participant_macro_balanced_accuracy": macro_accuracy,
            "participant_macro_ECE": macro_ece,
            "nuisance_log_loss_delta": nuisance_delta,
            "deranged_log_loss_delta": deranged_delta,
            "posterior_ablation_log_loss_delta": posterior_ablation_delta,
            "precue_log_loss_delta": pre_delta,
            "positive_nuisance_participants": positive_nuisance,
            "positive_deranged_participants": positive_deranged,
            "nuisance_exact_one_sided_sign_p": nuisance_sign_p,
            "deranged_exact_one_sided_sign_p": deranged_sign_p,
        },
        "inventory": {
            "participants": expected_participants,
            "target_rows": len(targets),
            "prediction_rows": len(normalized),
            "conditions": len(CONDITIONS),
        },
        "contains_individual_prediction_probability_target_or_participant_outcome": False,
        "claim_boundary": {
            "maximum_on_R1": "incremental_predeclared_central_EEG_sensor_information_under_registered_controls_in_this_protocol",
            "not_established": "spontaneous_intention_exclusive_motor_cortex_origin_eye_independent_causation_language_live_hardware_or_clinical_utility",
        },
    }
