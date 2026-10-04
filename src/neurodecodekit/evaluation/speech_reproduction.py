"""Fixed compact comparators and aggregate scoring for SPEECH-REPRO-1.

Prediction functions accept calibration labels and numeric arrays only. Online
labels belong exclusively to ``score_speech_predictions``; the caller freezes
prediction hashes before its single scoring invocation. This module neither
opens files nor enforces that caller-owned transaction boundary.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


N_CLASSES = 5
SEED = 20260906
PRIMARY_ARM = "auxiliary_filtered_eeg"
COMPACT_ARMS = (
    "auxiliary_only",
    "auxiliary_raw_eeg",
    PRIMARY_ARM,
    "auxiliary_preaction_eeg",
    "auxiliary_deranged_eeg",
    "auxiliary_filtered_eeg_shuffled_labels",
    "uniform",
    "training_prior",
)
SUCCESS_COMPARATORS = (
    "auxiliary_only",
    "auxiliary_deranged_eeg",
    "auxiliary_filtered_eeg_shuffled_labels",
    "uniform",
    "training_prior",
)
BANDS = ((2, 4), (4, 8), (8, 13), (13, 30), (30, 60), (60, 118))


def _numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Speech comparators require NumPy.") from exc
    return np


def _matrix(values: Any, name: str):
    np = _numpy()
    matrix = np.asarray(values, dtype=np.float64)
    if matrix.ndim != 2 or not all(matrix.shape):
        raise ValueError(f"{name} must be a nonempty [trials, features] matrix")
    if not np.isfinite(matrix).all():
        raise ValueError(f"{name} contains nonfinite values")
    return matrix


def _labels(values: Any):
    np = _numpy()
    labels = np.asarray(values)
    if labels.ndim != 1 or len(labels) == 0:
        raise ValueError("Labels must be a nonempty one-dimensional array")
    if labels.dtype.kind not in "iu" or not np.isin(labels, np.arange(N_CLASSES)).all():
        raise ValueError("Labels must be integer class indices 0 through 4")
    return labels.astype(np.int64, copy=False)


def _standardized_block(train: Any, evaluation: Any):
    """Use only calibration statistics, then normalize feature-block dimension."""
    np = _numpy()
    train = _matrix(train, "calibration features")
    evaluation = _matrix(evaluation, "evaluation features")
    if train.shape[1] != evaluation.shape[1]:
        raise ValueError("Calibration and evaluation feature dimensions differ")
    mean = train.mean(axis=0)
    scale = train.std(axis=0)
    scale = np.where(scale > 0.0, scale, 1.0)
    denominator = scale * np.sqrt(train.shape[1])
    return (train - mean) / denominator, (evaluation - mean) / denominator


def _recording_groups(recordings: Sequence[str] | None, n_rows: int):
    np = _numpy()
    records = np.asarray(recordings if recordings is not None else ["single"] * n_rows)
    if records.ndim != 1 or len(records) != n_rows:
        raise ValueError("Recording IDs must have one value per trial")
    return [np.flatnonzero(records == record) for record in dict.fromkeys(records.tolist())]


def cyclic_derangement_indices(recordings: Sequence[str] | None, n_rows: int):
    """One-trial cyclic reassignment, independently inside each recording."""
    np = _numpy()
    indices = np.arange(n_rows)
    for group in _recording_groups(recordings, n_rows):
        if len(group) < 2:
            raise ValueError("Derangement requires at least two trials per recording")
        indices[group] = np.roll(group, 1)
    return indices


def shuffled_calibration_labels(
    labels: Any, recordings: Sequence[str] | None = None, *, seed: int = SEED
):
    """A seeded within-recording permutation preserving class counts."""
    np = _numpy()
    original = _labels(labels)
    shuffled = original.copy()
    rng = np.random.default_rng(seed)
    for group in _recording_groups(recordings, len(original)):
        shuffled[group] = original[rng.permutation(group)]
    return shuffled


def ridge_probabilities(train: Any, labels: Any, evaluation: Any):
    """One-hot ridge with penalty 1, an unpenalized intercept, and softmax.

    Inputs are already standardized and dimension-normalized. Solving the dual
    system keeps the fixed high-dimensional comparator inexpensive when the
    calibration trial count is much smaller than the number of features.
    """
    np = _numpy()
    train = _matrix(train, "ridge calibration")
    evaluation = _matrix(evaluation, "ridge evaluation")
    labels = _labels(labels)
    if len(labels) != len(train) or train.shape[1] != evaluation.shape[1]:
        raise ValueError("Ridge input dimensions do not match")
    x_mean = train.mean(axis=0)
    x_centered = train - x_mean
    one_hot = np.eye(N_CLASSES)[labels]
    y_mean = one_hot.mean(axis=0)
    dual = x_centered @ x_centered.T
    dual.flat[:: len(dual) + 1] += 1.0
    coefficients = np.linalg.solve(dual, one_hot - y_mean)
    scores = ((evaluation - x_mean) @ x_centered.T) @ coefficients + y_mean
    scores -= scores.max(axis=1, keepdims=True)
    probabilities = np.exp(scores)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    if not np.isfinite(probabilities).all():
        raise ValueError("Ridge produced nonfinite probabilities")
    return probabilities


def predict_compact_arms(
    train_labels: Any,
    train_auxiliary: Any,
    eval_auxiliary: Any,
    train_eeg: Mapping[str, Any],
    eval_eeg: Mapping[str, Any],
    *,
    train_recordings: Sequence[str] | None = None,
    eval_recordings: Sequence[str] | None = None,
    seed: int = SEED,
) -> dict[str, Any]:
    """Fit all eight frozen arms without receiving online labels.

    EEG mappings must contain ``raw``, ``filtered`` and ``preaction`` matrices
    with identical feature counts. Auxiliary matrices include the caller's
    target-free trial index and elapsed recording time, with the same columns
    in every arm. Invoke separately for each calibration/person/condition pair.
    """
    np = _numpy()
    labels = _labels(train_labels)
    expected_keys = {"raw", "filtered", "preaction"}
    if set(train_eeg) != expected_keys or set(eval_eeg) != expected_keys:
        raise ValueError("EEG feature mappings require exactly raw, filtered, preaction")
    aux_train, aux_eval = _standardized_block(train_auxiliary, eval_auxiliary)
    if len(labels) != len(aux_train):
        raise ValueError("Calibration labels and auxiliary trials differ")
    blocks = {}
    feature_counts = set()
    for name in ("raw", "filtered", "preaction"):
        block_train, block_eval = _standardized_block(train_eeg[name], eval_eeg[name])
        if len(block_train) != len(labels) or len(block_eval) != len(aux_eval):
            raise ValueError(f"{name} EEG trial counts differ from auxiliary trials")
        feature_counts.add(block_train.shape[1])
        blocks[name] = (block_train, block_eval)
    if len(feature_counts) != 1:
        raise ValueError("All populated EEG slots must have identical feature dimensions")

    predictions = {"auxiliary_only": ridge_probabilities(aux_train, labels, aux_eval)}
    for name, (block_train, block_eval) in blocks.items():
        predictions[f"auxiliary_{name}_eeg"] = ridge_probabilities(
            np.concatenate((aux_train, block_train), axis=1),
            labels,
            np.concatenate((aux_eval, block_eval), axis=1),
        )
    primary_train, primary_eval = blocks["filtered"]
    train_order = cyclic_derangement_indices(train_recordings, len(labels))
    eval_order = cyclic_derangement_indices(eval_recordings, len(aux_eval))
    predictions["auxiliary_deranged_eeg"] = ridge_probabilities(
        np.concatenate((aux_train, primary_train[train_order]), axis=1),
        labels,
        np.concatenate((aux_eval, primary_eval[eval_order]), axis=1),
    )
    predictions["auxiliary_filtered_eeg_shuffled_labels"] = ridge_probabilities(
        np.concatenate((aux_train, primary_train), axis=1),
        shuffled_calibration_labels(labels, train_recordings, seed=seed),
        np.concatenate((aux_eval, primary_eval), axis=1),
    )
    predictions["uniform"] = np.full((len(aux_eval), N_CLASSES), 1.0 / N_CLASSES)
    prior = np.bincount(labels, minlength=N_CLASSES).astype(np.float64) / len(labels)
    predictions["training_prior"] = np.tile(prior, (len(aux_eval), 1))
    return predictions


def _log_band_energies(values: Any, sfreq: float):
    np = _numpy()
    n_samples = values.shape[-1]
    frequencies = np.fft.rfftfreq(n_samples, d=1.0 / sfreq)
    energies = np.abs(np.fft.rfft(values, axis=-1)) ** 2 / n_samples**2
    if n_samples % 2 == 0:
        energies[..., 1:-1] *= 2.0
    else:
        energies[..., 1:] *= 2.0
    band_energies = []
    for lower, upper in BANDS:
        mask = (frequencies >= lower) & (frequencies < upper)
        if upper == BANDS[-1][1]:
            mask |= frequencies == upper
        if not mask.any():
            raise ValueError("Signal window has insufficient frequency resolution")
        band_energies.append(energies[..., mask].sum(axis=-1))
    return np.log(np.maximum(np.stack(band_energies, axis=-1), np.finfo(float).tiny))


def fixed_channel_features(averaged: Any, *, full_trial: Any = None, sfreq: float = 256.0):
    """64 temporal bins and six log band powers per averaged channel.

    For auxiliary channels, ``full_trial`` additionally supplies six unaveraged
    band powers, RMS and peak-to-peak per channel. All operations are per trial;
    fitting and normalization occur later using calibration rows only.
    """
    np = _numpy()
    averaged = np.asarray(averaged, dtype=np.float64)
    if averaged.ndim != 3 or not all(averaged.shape) or averaged.shape[-1] % 64:
        raise ValueError("Averaged windows must be [trials, channels, time divisible by 64]")
    if sfreq < 236 or not np.isfinite(averaged).all():
        raise ValueError("Feature input must be finite with sfreq at least 236 Hz")
    bins = averaged.reshape(*averaged.shape[:2], 64, averaged.shape[-1] // 64).mean(-1)
    features = [bins, _log_band_energies(averaged, sfreq)]
    if full_trial is not None:
        full_trial = np.asarray(full_trial, dtype=np.float64)
        if (
            full_trial.ndim != 3
            or full_trial.shape[:2] != averaged.shape[:2]
            or full_trial.shape[-1] == 0
            or not np.isfinite(full_trial).all()
        ):
            raise ValueError("Full-trial auxiliaries must match trial/channel dimensions")
        features.extend(
            (
                _log_band_energies(full_trial, sfreq),
                np.sqrt(np.mean(full_trial**2, axis=-1))[..., None],
                np.ptp(full_trial, axis=-1)[..., None],
            )
        )
    return np.concatenate(features, axis=-1).reshape(len(averaged), -1)


def _probabilities(values: Any, n_rows: int, name: str):
    np = _numpy()
    probabilities = _matrix(values, name)
    if probabilities.shape != (n_rows, N_CLASSES):
        raise ValueError(f"{name} must have one row and five probabilities per trial")
    if (probabilities < 0).any() or (probabilities > 1).any():
        raise ValueError(f"{name} has probabilities outside [0, 1]")
    if not np.allclose(probabilities.sum(axis=1), 1.0, atol=1e-8, rtol=0):
        raise ValueError(f"{name} probabilities must sum to one")
    return probabilities


def _metrics(probabilities: Any, labels: Any) -> dict[str, Any]:
    np = _numpy()
    counts = np.bincount(labels, minlength=N_CLASSES)
    predicted = probabilities.argmax(axis=1)
    complete = bool((counts > 0).all())
    result = {
        "n_trials": int(len(labels)),
        "class_counts": counts.tolist(),
        "complete_five_class_endpoint": complete,
        "accuracy": float(np.mean(predicted == labels)),
        "balanced_accuracy": None,
        "class_macro_log_loss": None,
    }
    if complete:
        losses = -np.log(np.maximum(probabilities[np.arange(len(labels)), labels], 1e-15))
        result["balanced_accuracy"] = float(
            np.mean([np.mean(predicted[labels == c] == c) for c in range(N_CLASSES)])
        )
        result["class_macro_log_loss"] = float(
            np.mean([np.mean(losses[labels == c]) for c in range(N_CLASSES)])
        )
    return result


def score_speech_predictions(
    predictions: Mapping[str, Any],
    targets: Any,
    participants: Sequence[str],
    conditions: Sequence[str],
    *,
    expected_participants: Sequence[str] = ("sub-1", "sub-2", "sub-3"),
    reference_arm: str = "eegnet_reference",
) -> dict[str, Any]:
    """Aggregate one frozen score, pooling online runs within each fixed pair.

    The experiment has one calibration pair per person and condition. Thus
    pooling rows by person/condition pools runs correctly; subsequent means give
    each person equal weight regardless of their trial count. Missing classes
    invalidate the five-class endpoint instead of changing its denominator.
    """
    np = _numpy()
    labels = _labels(targets)
    people = np.asarray(participants)
    tasks = np.asarray([str(item).replace(" ", "").replace("_", "") for item in conditions])
    expected = tuple(expected_participants)
    if len(expected) != 3 or len(set(expected)) != 3:
        raise ValueError("The frozen experiment requires exactly three distinct participants")
    if people.ndim != 1 or tasks.ndim != 1 or len(people) != len(labels) or len(tasks) != len(labels):
        raise ValueError("Participant and condition vectors must match the scored trials")
    if not set(people.tolist()).issubset(set(expected)):
        raise ValueError("Unexpected participant in scored data")
    if not set(tasks.tolist()).issubset({"minimallyovert", "covert"}):
        raise ValueError("Unexpected speech condition")
    required = set(COMPACT_ARMS) | {reference_arm}
    if set(predictions) != required:
        raise ValueError(f"Expected exactly the compact arms and {reference_arm}")
    probability_arrays = {
        name: _probabilities(values, len(labels), name) for name, values in predictions.items()
    }
    result: dict[str, Any] = {
        "experiment_id": "SPEECH-REPRO-1",
        "primary_arm": PRIMARY_ARM,
        "primary_condition": "minimallyovert",
        "primary_endpoint": "equal_person_class_macro_log_loss_gain_over_auxiliary_only",
        "n_people_expected": 3,
        "n_trials": int(len(labels)),
        "minimum_one_sided_person_sign_flip_p": 0.125,
        "population_significance_claim": False,
        "conditions": {},
        "notes": [
            "Historical online recordings are offline evaluation, not our prospective live test.",
            "Raw and preaction EEG are interpretation comparisons, outside the success conjunction.",
            "A conditional failure does not establish missing word information or reference failure.",
            "Positive findings concern release labels beyond measured controls; cue and cortical attribution remain unresolved.",
        ],
    }
    for task in ("minimallyovert", "covert"):
        per_person = {}
        task_notes = []
        for person in expected:
            indices = np.flatnonzero((people == person) & (tasks == task))
            if not len(indices):
                task_notes.append(f"{person}: no scored trials; five-class endpoint incomplete")
                continue
            person_metrics = {
                name: _metrics(probabilities[indices], labels[indices])
                for name, probabilities in probability_arrays.items()
            }
            per_person[person] = person_metrics
            if not person_metrics[PRIMARY_ARM]["complete_five_class_endpoint"]:
                task_notes.append(f"{person}: an evaluation class is absent; endpoint incomplete")
        complete = len(per_person) == 3 and all(
            metrics[PRIMARY_ARM]["complete_five_class_endpoint"] for metrics in per_person.values()
        )
        summaries = {}
        for arm in probability_arrays:
            summaries[arm] = {
                "equal_person_accuracy": None,
                "equal_person_balanced_accuracy": None,
                "equal_person_class_macro_log_loss": None,
            }
            if len(per_person) == 3:
                summaries[arm]["equal_person_accuracy"] = float(
                    np.mean([per_person[person][arm]["accuracy"] for person in expected])
                )
            if complete:
                for metric in ("balanced_accuracy", "class_macro_log_loss"):
                    summaries[arm][f"equal_person_{metric}"] = float(
                        np.mean([per_person[person][arm][metric] for person in expected])
                    )
        edges = {}
        for comparator in COMPACT_ARMS:
            if comparator == PRIMARY_ARM:
                continue
            gains = {}
            for person, metrics in per_person.items():
                if metrics[PRIMARY_ARM]["complete_five_class_endpoint"]:
                    gains[person] = (
                        metrics[comparator]["class_macro_log_loss"]
                        - metrics[PRIMARY_ARM]["class_macro_log_loss"]
                    )
            edges[comparator] = {
                "per_person_log_loss_gain": gains,
                "equal_person_log_loss_gain": float(np.mean(list(gains.values()))) if complete else None,
                "positive_people": sum(gain > 0.0 for gain in gains.values()),
                "all_three_positive": complete and all(gain > 0.0 for gain in gains.values()),
            }
        conditional_success = complete and all(
            edges[comparator]["all_three_positive"] for comparator in SUCCESS_COMPARATORS
        )
        reference_success = complete and all(
            metrics[reference_arm]["balanced_accuracy"] > 1.0 / N_CLASSES
            for metrics in per_person.values()
        )
        result["conditions"][task] = {
            "complete_five_class_endpoint": complete,
            "participant_metrics": per_person,
            "equal_person_metrics": summaries,
            "primary_edges": edges,
            "conditional_descriptive_success": bool(conditional_success),
            "reference_all_three_above_chance": bool(reference_success),
            "status": "incomplete" if not complete else (
                "descriptive_conditional_increment" if conditional_success else "increment_not_demonstrated"
            ),
            "notes": task_notes,
        }
    return result
