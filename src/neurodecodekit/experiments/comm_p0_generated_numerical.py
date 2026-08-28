"""Compact numerical schedule for the generated-only COMM-P0-G qualification.

Fixture construction is separate from fold fitting so a later process coordinator
can keep held-out generated targets outside every model capability.  No function in
this module accepts a real path, a device, a provider, or a network surface.
"""

from __future__ import annotations

import hashlib
import os
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from neurodecodekit.experiments import comm_p0_generated as core


THREAD_ENVIRONMENT = (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
NONPRIOR_CONDITIONS = tuple(
    condition
    for condition in (
        "cue_only",
        "timing_only",
        "EOG_only",
        "oral_EMG_only",
        "microphone_only",
        "all_recorded_peripheral_P",
        "central_EEG_only",
        "posterior_EEG_only",
        "P_plus_residual_central_EEG",
        "P_plus_class_destroyed_residual_central_EEG",
        "prechoice_or_early_window_EEG",
        "null_or_rest_endpoint",
        "language_only",
        "neural_plus_language",
        "deranged_neural_plus_language",
    )
)
TEMPERATURE_GRID = tuple(0.5 + 0.05 * index for index in range(31))


@dataclass(frozen=True, slots=True)
class FeatureRow:
    item_id: str
    cohort_id: str
    participant_id: str
    endpoint: str
    phase: str
    central: tuple[float, ...]
    posterior: tuple[float, ...]
    eog: tuple[float, ...]
    oral_emg: tuple[float, ...]
    microphone: tuple[float, ...]
    cue: tuple[float, ...]
    timing: tuple[float, ...]
    prechoice: tuple[float, ...]
    language: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class CompactPrediction:
    item_id: str
    cohort_id: str
    participant_id: str
    endpoint: str
    phase: str
    condition: str
    probabilities: tuple[float, float, float, float]

    def public_record(self) -> dict[str, Any]:
        value = {
            "item_id": self.item_id,
            "cohort_id": self.cohort_id,
            "participant_id": self.participant_id,
            "endpoint": self.endpoint,
            "phase": self.phase,
            "condition": self.condition,
            "probabilities": list(self.probabilities),
        }
        core.assert_target_free(value)
        return value


@dataclass(slots=True)
class NumericalLedger:
    prior_fits: int = 0
    residualizer_fits: int = 0
    classifier_fits: int = 0
    temperature_calibration_fits: int = 0
    model_inference_runs: int = 0
    prediction_sets: int = 0
    prediction_rows: int = 0
    target_deliveries: int = 0
    scores: int = 0
    post_target_updates: int = 0


def _np() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("COMM-P0-G arrays require: pip install -e '.[classical]'") from exc
    return np


def _model_classes() -> tuple[Any, Any, Any]:
    try:
        from sklearn.linear_model import LogisticRegression, Ridge
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("COMM-P0-G models require: pip install -e '.[classical]'") from exc
    return LogisticRegression, Ridge, StandardScaler


def numerical_dependencies_available() -> bool:
    try:
        _np()
        _model_classes()
    except RuntimeError:
        return False
    return True


def assert_single_thread_environment() -> None:
    changed = [name for name in THREAD_ENVIRONMENT if os.environ.get(name) != "1"]
    if changed:
        raise core.CommP0GeneratedRefusal(
            "total_permission_or_free_space_floor_breach", ",".join(changed)
        )


def _noise(item_id: str, surface: str, length: int, scale: float = 0.08) -> tuple[float, ...]:
    values = []
    for index in range(length):
        digest = hashlib.sha256(f"{item_id}:{surface}:{index}".encode()).digest()
        unit = int.from_bytes(digest[:8], "big") / float(2**64 - 1)
        values.append((2.0 * unit - 1.0) * scale)
    return tuple(values)


def _fixture_command(row: core.TrialPlan) -> int:
    """Recreate only the fictional target inside the fixture-construction boundary."""

    payload = f"{row.participant_id}:{row.trial_index}:{row.role}:20260827".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "big") % len(core.COMMANDS)


def generate_feature_rows(rows: Sequence[core.TrialPlan]) -> tuple[FeatureRow, ...]:
    """Create target-free procedural views; do not return generated target values."""

    result: list[FeatureRow] = []
    for row in rows:
        if row.endpoint not in core.ENDPOINTS:
            continue
        command = _fixture_command(row)
        one_hot = tuple(1.0 if index == command else 0.0 for index in range(4))
        central_noise = _noise(row.item_id, "central", 4)
        central = tuple(one_hot[index] + central_noise[index] for index in range(4)) + _noise(
            row.item_id, "central-extra", 4
        )
        cue = one_hot if row.endpoint == "prompted_intend" else (0.25,) * 4
        feature = FeatureRow(
            item_id=row.item_id,
            cohort_id=row.cohort_id,
            participant_id=row.participant_id,
            endpoint=row.endpoint,
            phase=row.phase,
            central=central,
            posterior=_noise(row.item_id, "posterior", 4),
            eog=_noise(row.item_id, "eog", 4),
            oral_emg=_noise(row.item_id, "oral-emg", 4),
            microphone=_noise(row.item_id, "microphone", 4),
            cue=cue,
            timing=(
                (row.trial_index % 17) / 16.0,
                row.intention_window_start_seconds / 1650.0,
            ),
            prechoice=_noise(row.item_id, "prechoice", 4),
            language=(0.25,) * 4,
        )
        core.assert_target_free(
            feature.__dict__
            if hasattr(feature, "__dict__")
            else {
                "item_id": feature.item_id,
                "cohort_id": feature.cohort_id,
                "participant_id": feature.participant_id,
                "endpoint": feature.endpoint,
                "phase": feature.phase,
            }
        )
        result.append(feature)
    return tuple(result)


def _targets_for_rows(
    rows: Sequence[FeatureRow], trial_by_item: Mapping[str, core.TrialPlan]
) -> Any:
    np = _np()
    # This helper is called only on source/calibration capabilities by the model runner.
    return np.asarray([_fixture_command(trial_by_item[row.item_id]) for row in rows], dtype="int64")


def _matrix(rows: Sequence[FeatureRow], field: str) -> Any:
    np = _np()
    return np.asarray([getattr(row, field) for row in rows], dtype="float64")


def _peripheral(rows: Sequence[FeatureRow]) -> Any:
    np = _np()
    return np.concatenate(
        (
            _matrix(rows, "eog"),
            _matrix(rows, "oral_emg"),
            _matrix(rows, "microphone"),
            _matrix(rows, "cue"),
            _matrix(rows, "timing"),
        ),
        axis=1,
    )


def _fit_residualizer(source_context: Any, source_signal: Any) -> tuple[Any, Any, Any]:
    _, Ridge, StandardScaler = _model_classes()
    x_scaler = StandardScaler().fit(source_context)
    y_scaler = StandardScaler().fit(source_signal)
    model = Ridge(alpha=10.0, fit_intercept=True).fit(
        x_scaler.transform(source_context), y_scaler.transform(source_signal)
    )
    return x_scaler, y_scaler, model


def _residualize(bundle: tuple[Any, Any, Any], context: Any, signal: Any) -> Any:
    x_scaler, y_scaler, model = bundle
    predicted = y_scaler.inverse_transform(model.predict(x_scaler.transform(context)))
    return signal - predicted


def _derange_by_class(rows: Sequence[FeatureRow], features: Any, targets: Any) -> Any:
    np = _np()
    values = np.asarray(features, dtype="float64")
    result = np.empty_like(values)
    for endpoint in core.ENDPOINTS:
        endpoint_indices = np.asarray(
            [index for index, row in enumerate(rows) if row.endpoint == endpoint],
            dtype="int64",
        )
        by_class = {
            class_index: endpoint_indices[targets[endpoint_indices] == class_index]
            for class_index in range(4)
        }
        if any(len(indices) == 0 for indices in by_class.values()):
            raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
        for class_index, destinations in by_class.items():
            sources = by_class[(class_index + 1) % 4]
            for offset, destination in enumerate(destinations):
                result[destination] = values[sources[offset % len(sources)]]
    return result


def _fit_endpoint_residualizers(
    rows: Sequence[FeatureRow], context: Any, signal: Any
) -> dict[str, tuple[Any, Any, Any]]:
    bundles = {}
    for endpoint in core.ENDPOINTS:
        indices = [index for index, row in enumerate(rows) if row.endpoint == endpoint]
        if not indices:
            raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
        bundles[endpoint] = _fit_residualizer(context[indices], signal[indices])
    return bundles


def _residualize_by_endpoint(
    rows: Sequence[FeatureRow],
    bundles: Mapping[str, tuple[Any, Any, Any]],
    context: Any,
    signal: Any,
) -> Any:
    np = _np()
    result = np.empty_like(signal, dtype="float64")
    for endpoint in core.ENDPOINTS:
        indices = [index for index, row in enumerate(rows) if row.endpoint == endpoint]
        result[indices] = _residualize(bundles[endpoint], context[indices], signal[indices])
    return result


def _condition_matrix(
    condition: str,
    rows: Sequence[FeatureRow],
    residual: Any,
    deranged_residual: Any,
) -> Any:
    np = _np()
    peripheral = _peripheral(rows)
    direct = {
        "cue_only": _matrix(rows, "cue"),
        "timing_only": _matrix(rows, "timing"),
        "EOG_only": _matrix(rows, "eog"),
        "oral_EMG_only": _matrix(rows, "oral_emg"),
        "microphone_only": _matrix(rows, "microphone"),
        "all_recorded_peripheral_P": peripheral,
        "central_EEG_only": _matrix(rows, "central"),
        "posterior_EEG_only": _matrix(rows, "posterior"),
        "prechoice_or_early_window_EEG": _matrix(rows, "prechoice"),
        "null_or_rest_endpoint": np.zeros((len(rows), 1), dtype="float64"),
        "language_only": _matrix(rows, "language"),
    }
    if condition in direct:
        return direct[condition]
    if condition == "P_plus_residual_central_EEG":
        return np.concatenate((peripheral, residual), axis=1)
    if condition == "P_plus_class_destroyed_residual_central_EEG":
        return np.concatenate((peripheral, deranged_residual), axis=1)
    if condition == "neural_plus_language":
        return np.concatenate((peripheral, residual, _matrix(rows, "language")), axis=1)
    if condition == "deranged_neural_plus_language":
        return np.concatenate((peripheral, deranged_residual, _matrix(rows, "language")), axis=1)
    raise core.CommP0GeneratedRefusal(
        "required_control_condition_missing_duplicated_or_substituted", condition
    )


def _fit_classifier(features: Any, targets: Any) -> tuple[Any, Any]:
    LogisticRegression, _, StandardScaler = _model_classes()
    scaler = StandardScaler().fit(features)
    model = LogisticRegression(
        C=0.1,
        solver="lbfgs",
        max_iter=300,
        tol=1e-6,
        class_weight=None,
        random_state=0,
    ).fit(scaler.transform(features), targets)
    if tuple(int(value) for value in model.classes_) != (0, 1, 2, 3):
        raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
    return scaler, model


def _temperature_fit(probabilities: Any, targets: Any) -> float:
    np = _np()
    clipped = np.clip(np.asarray(probabilities, dtype="float64"), 1e-6, 1.0)
    losses = []
    for temperature in TEMPERATURE_GRID:
        logits = np.log(clipped) / temperature
        logits -= logits.max(axis=1, keepdims=True)
        adjusted = np.exp(logits)
        adjusted /= adjusted.sum(axis=1, keepdims=True)
        loss = -np.log(np.clip(adjusted[np.arange(len(targets)), targets], 1e-6, 1.0)).mean()
        losses.append((float(loss), temperature))
    return min(losses)[1]


def _apply_temperature(probabilities: Any, temperature: float) -> Any:
    np = _np()
    clipped = np.clip(np.asarray(probabilities, dtype="float64"), 1e-6, 1.0)
    logits = np.log(clipped) / temperature
    logits -= logits.max(axis=1, keepdims=True)
    adjusted = np.exp(logits)
    adjusted /= adjusted.sum(axis=1, keepdims=True)
    return adjusted


def _calibration_participants(source_participants: Sequence[str]) -> frozenset[str]:
    ordered = sorted(source_participants)
    count = max(1, len(ordered) // 5)
    return frozenset(ordered[:count])


def _append_predictions(
    destination: list[CompactPrediction],
    rows: Sequence[FeatureRow],
    condition: str,
    probabilities: Any,
    ledger: NumericalLedger,
) -> None:
    for row, probability in zip(rows, probabilities, strict=True):
        normalized = core.validate_probability_vector(probability.tolist())
        destination.append(
            CompactPrediction(
                item_id=row.item_id,
                cohort_id=row.cohort_id,
                participant_id=row.participant_id,
                endpoint=row.endpoint,
                phase=row.phase,
                condition=condition,
                probabilities=normalized,
            )
        )
    ledger.model_inference_runs += 1
    ledger.prediction_sets += len(core.ENDPOINTS)
    ledger.prediction_rows += len(rows)


def run_target_blind_schedule(
    trial_rows: Sequence[core.TrialPlan],
    contract: Mapping[str, Any],
    *,
    exact_registered_schedule: bool = True,
) -> tuple[tuple[CompactPrediction, ...], NumericalLedger]:
    """Run fixed participant-held-out models without computing held-out targets."""

    assert_single_thread_environment()
    np = _np()
    if tuple(contract["conditions"]) != (
        "equal_prior",
        "source_class_prior",
        *NONPRIOR_CONDITIONS,
    ):
        raise core.CommP0GeneratedRefusal(
            "required_control_condition_missing_duplicated_or_substituted"
        )
    feature_rows = generate_feature_rows(trial_rows)
    trial_by_item = {row.item_id: row for row in trial_rows}
    predictions: list[CompactPrediction] = []
    ledger = NumericalLedger()
    by_cohort: dict[str, list[FeatureRow]] = defaultdict(list)
    for row in feature_rows:
        by_cohort[row.cohort_id].append(row)
    for cohort_id in core.COHORTS:
        cohort_rows = by_cohort[cohort_id]
        participants = sorted({row.participant_id for row in cohort_rows})
        for held_out in participants:
            held_rows = [row for row in cohort_rows if row.participant_id == held_out]
            source_participants = [
                participant for participant in participants if participant != held_out
            ]
            calibration_ids = _calibration_participants(source_participants)
            fit_rows = [
                row
                for row in cohort_rows
                if row.participant_id in source_participants
                and row.participant_id not in calibration_ids
            ]
            calibration_rows = [row for row in cohort_rows if row.participant_id in calibration_ids]
            if not fit_rows or not calibration_rows or not held_rows:
                raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")
            fit_y = _targets_for_rows(fit_rows, trial_by_item)
            calibration_y = _targets_for_rows(calibration_rows, trial_by_item)
            counts = Counter(int(value) for value in fit_y.tolist())
            if set(counts) != {0, 1, 2, 3}:
                raise core.CommP0GeneratedRefusal("calibration_source_method_or_row_violation")

            fit_peripheral = _peripheral(fit_rows)
            calibration_peripheral = _peripheral(calibration_rows)
            held_peripheral = _peripheral(held_rows)
            central_residualizers = _fit_endpoint_residualizers(
                fit_rows, fit_peripheral, _matrix(fit_rows, "central")
            )
            ledger.residualizer_fits += 2
            fit_residual = _residualize_by_endpoint(
                fit_rows,
                central_residualizers,
                fit_peripheral,
                _matrix(fit_rows, "central"),
            )
            calibration_residual = _residualize_by_endpoint(
                calibration_rows,
                central_residualizers,
                calibration_peripheral,
                _matrix(calibration_rows, "central"),
            )
            held_residual = _residualize_by_endpoint(
                held_rows,
                central_residualizers,
                held_peripheral,
                _matrix(held_rows, "central"),
            )
            fit_deranged = _derange_by_class(fit_rows, fit_residual, fit_y)
            # Destruction is source-only. Calibration and held-out EEG stay intact.
            calibration_deranged = calibration_residual
            held_deranged = held_residual

            equal = np.full((len(held_rows), 4), 0.25, dtype="float64")
            _append_predictions(predictions, held_rows, "equal_prior", equal, ledger)
            prior = np.asarray([counts[index] for index in range(4)], dtype="float64")
            prior /= prior.sum()
            prior_rows = np.tile(prior, (len(held_rows), 1))
            ledger.prior_fits += 1
            _append_predictions(predictions, held_rows, "source_class_prior", prior_rows, ledger)

            for condition in NONPRIOR_CONDITIONS:
                fit_x = _condition_matrix(condition, fit_rows, fit_residual, fit_deranged)
                calibration_x = _condition_matrix(
                    condition,
                    calibration_rows,
                    calibration_residual,
                    calibration_deranged,
                )
                held_x = _condition_matrix(condition, held_rows, held_residual, held_deranged)
                scaler, model = _fit_classifier(fit_x, fit_y)
                ledger.classifier_fits += 1
                calibration_probabilities = model.predict_proba(scaler.transform(calibration_x))
                temperature = _temperature_fit(calibration_probabilities, calibration_y)
                ledger.temperature_calibration_fits += 1
                held_probabilities = _apply_temperature(
                    model.predict_proba(scaler.transform(held_x)), temperature
                )
                _append_predictions(predictions, held_rows, condition, held_probabilities, ledger)

    if exact_registered_schedule:
        expected = contract["numerical_schedule_per_replay"]
        observed = {
            "prior_fits": ledger.prior_fits,
            "residualizer_fits": ledger.residualizer_fits,
            "classifier_fits": ledger.classifier_fits,
            "temperature_calibration_fits": ledger.temperature_calibration_fits,
            "prediction_sets": ledger.prediction_sets,
            "prediction_rows": ledger.prediction_rows,
        }
        for key, value in observed.items():
            if value != expected[key]:
                raise core.CommP0GeneratedRefusal(
                    "prediction_inventory_missing_or_duplicate", f"{key}:{value}"
                )
    if ledger.target_deliveries or ledger.scores or ledger.post_target_updates:
        raise core.CommP0GeneratedRefusal("post_target_update_rerun_or_model_substitution")
    return tuple(predictions), ledger


def prediction_stream_sha256(predictions: Sequence[CompactPrediction]) -> str:
    digest = hashlib.sha256()
    for prediction in predictions:
        digest.update(core.canonical_json_bytes(prediction.public_record()))
    return digest.hexdigest()
