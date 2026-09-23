"""Four-class, arrays-only nested comparison; prediction and scoring are separate.

No file/network access or feature/model search. The caller preflights every
participant/condition before fitting, appends only target-free timing/run/order
columns to P, and supplies distinct four-integer seed blocks across conditions.
"""

from __future__ import annotations

import hashlib
import json
import time

from neurodecodekit.evaluation.speech_reproduction import _matrix, _numpy, _standardized_block
from neurodecodekit.experiments.speech_probability_calibration import _temperature_log_softmax


N_CLASSES = 4
SFREQ = 1024
WINDOW_SAMPLES = (384, 2048)
EEG_BANDS = ((1, 4), (4, 8), (8, 13), (13, 30), (30, 40))
PERIPHERAL_BANDS = ((1, 4), (4, 8), (8, 13), (13, 30), (30, 45), (55, 100))
LEARNED_ARMS = ("P", "joint", "cue_joint", "late_joint", "deranged_joint", "joint_shuffled")
ARMS = (*LEARNED_ARMS, "uniform", "training_prior")
PRIMARY_COMPARATORS = ("P", "deranged_joint", "joint_shuffled", "uniform", "training_prior")
BETA_BOUNDS = (0.05, 20.0)
BISECTION_STEPS = 60
SEED = 20260922


def _labels(values):
    np = _numpy()
    labels = np.asarray(values)
    if labels.ndim != 1 or not len(labels) or labels.dtype.kind not in "iu" or (
            (labels < 0).any() or (labels >= N_CLASSES).any()):
        raise ValueError("Expected integer labels 0..3")
    return labels.astype(np.int64, copy=False)


def _four_classes(labels):
    np = _numpy()
    counts = np.bincount(labels, minlength=N_CLASSES)
    if len(counts) != N_CLASSES or (counts == 0).any():
        raise ValueError("The complete condition requires all four classes")
    return counts


def _probabilities(values, n_rows):
    np = _numpy()
    values = _matrix(values, "four-class probabilities")
    if values.shape != (n_rows, N_CLASSES) or (values < 0).any() or (values > 1).any() or not (
            np.allclose(values.sum(axis=1), 1.0, atol=1e-8, rtol=0)):
        raise ValueError("Expected four finite probabilities summing to one per original trial")
    return values


def _window(values, channels):
    np = _numpy()
    values = _matrix(values, "microvolt signal window")
    if values.shape[0] != channels or values.shape[1] not in WINDOW_SAMPLES:
        raise ValueError("Expected a complete 384- or 2048-sample window and all declared channels")
    return np.asarray(values, dtype=np.float64)


def _window_log_power(values, bands):
    np = _numpy()
    n_samples = values.shape[1]
    centered = values - values.mean(axis=1, keepdims=True)
    hann = np.hanning(n_samples)
    # One-sided, window-energy-corrected power in microvolt squared.
    power = np.abs(np.fft.rfft(centered * hann, axis=1)) ** 2 / (n_samples * (hann @ hann))
    power[:, 1:-1] *= 2
    if not np.isfinite(power).all():
        raise ValueError("Nonfinite generated spectral power")
    frequencies = np.fft.rfftfreq(n_samples, 1.0 / SFREQ)
    result = []
    for index, (lower, upper) in enumerate(bands):
        mask = (frequencies >= lower) & (frequencies < upper)
        if index == len(bands) - 1:
            mask |= frequencies == upper
        result.append(power[:, mask].sum(axis=1))
    return np.log(np.maximum(np.stack(result, axis=1), np.finfo(float).tiny))


def window_features(eeg_uV, exg_uV, *, sfreq=SFREQ):
    """Return E[640], P[77] from an admitted 384/2048-sample window in microvolts.

    EEG uses a 128-channel-only common average, then per-window demean/Hann.
    EXG uses eight channels referenced to mean(EXG1,EXG2), plus EXG3-4,
    EXG5-6 and EXG7-8 bipolar differences. Each has six log bands and unwindowed
    log population variance. EXG1/EXG2 are opposite duplicate references.
    No outside samples, filtering, adaptive
    subtraction, trial normalization, EEG-to-EXG or EXG-to-EEG input is used.
    Features flatten channel first, then bands (and final EXG variance).
    P is retained only from the 2048-sample action window by the caller.
    FFT resolution is 1024/N: 0.5 Hz action; 8/3 Hz cue/matched-late.
    """
    np = _numpy()
    if sfreq != SFREQ:
        raise ValueError("The fixed feature recipe requires 1024 Hz")
    eeg, exg = _window(eeg_uV, 128), _window(exg_uV, 8)
    if eeg.shape[1] != exg.shape[1]:
        raise ValueError("EEG and EXG must use the same complete window")
    eeg = eeg - eeg.mean(axis=0, keepdims=True)
    exg = exg - exg[:2].mean(axis=0, keepdims=True)
    exg = np.concatenate((exg, exg[2:8:2] - exg[3:8:2]), axis=0)
    peripheral = np.concatenate((_window_log_power(exg, PERIPHERAL_BANDS),
        np.log(np.maximum(exg.var(axis=1), np.finfo(float).tiny))[:, None]), axis=1)
    return {"E": _window_log_power(eeg, EEG_BANDS).reshape(-1), "P": peripheral.reshape(-1)}


def _embargoed_split(pool, validation, original_indices):
    """Embargo immediate original-trial neighbours, not compressed row ranks."""
    np = _numpy()
    forbidden = np.concatenate(tuple(original_indices[validation] + offset for offset in (-1, 0, 1)))
    train = pool[~np.isin(original_indices[pool], forbidden)]
    if len(train) < 2 or len(validation) < 2 or np.intersect1d(train, validation).size:
        raise ValueError("Temporal split is empty, overlapping, or too small for derangement")
    return train, validation


def _split_record(train, validation, original_indices, labels, null_labels):
    payload = {"train": original_indices[train].tolist(), "validation": original_indices[validation].tolist()}
    return {"training_trials": len(train), "validation_trials": len(validation),
            "training_class_counts": _numpy().bincount(labels[train], minlength=N_CLASSES).tolist(),
            "shuffled_training_class_counts": _numpy().bincount(null_labels[train], minlength=N_CLASSES).tolist(),
            "original_split_sha256": hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()}


def _nested_plan(labels, original_trial_indices, seed):
    np = _numpy()
    labels = _labels(labels)
    original = np.asarray(original_trial_indices)
    if len(labels) not in (40, 80, 120) or original.shape != labels.shape or original.dtype.kind not in "iu":
        raise ValueError("Conditions require 40, 80 or 120 original whole trials and integer indices")
    if (original < 0).any() or np.any(original[1:] <= original[:-1]):
        raise ValueError("Original trial indices must be nonnegative, unique and chronological")
    if type(seed) is not int or seed < 0:
        raise ValueError("Seed must be a nonnegative Python integer with a distinct four-seed block")
    original = original.astype(np.int64, copy=False)
    _four_classes(labels)
    rows = np.arange(len(labels))
    blocks = np.array_split(rows, 4)
    plans, records = [], []
    for fold, block in enumerate(blocks):
        train, validation = _embargoed_split(rows, block, original)
        null_labels = np.full(len(labels), -1, dtype=np.int64)
        permutation = np.random.default_rng(seed + fold).permutation(len(train))
        null_labels[train] = labels[train][permutation]
        record = _split_record(train, validation, original, labels, null_labels)
        record.update({"outer_fold": fold, "shuffle_seed": seed + fold,
                       "temperature_calibration_trials": len(train), "inner_folds": []})
        inner, coverage = [], np.zeros(len(labels), dtype=int)
        for other, inner_block in enumerate(blocks):
            if other == fold:
                continue
            inner_validation = np.intersect1d(train, inner_block, assume_unique=True)
            inner_train, inner_validation = _embargoed_split(train, inner_validation, original)
            inner.append((inner_train, inner_validation))
            coverage[inner_validation] += 1
            record["inner_folds"].append(_split_record(
                inner_train, inner_validation, original, labels, null_labels))
        if not np.all(coverage[train] == 1) or coverage.sum() != len(train):
            raise ValueError("Inner OOF must cover outer training exactly once, without outer test rows")
        plans.append((train, validation, inner, null_labels))
        records.append(record)
    return labels, plans, records


def preflight_condition(labels, original_trial_indices, *, seed=SEED):
    """Validate fixed splits and record true/null supports, without changing folds."""
    return {"n_trials": len(labels), "seed_block": [seed, seed + 3],
            "folds": _nested_plan(labels, original_trial_indices, seed)[2]}


def _ridge_probabilities(train, labels, evaluation):
    """Four-class specialization of the existing fixed alpha=1 dual ridge."""
    np = _numpy()
    labels = _labels(labels)
    x_mean = train.mean(axis=0)
    centered = train - x_mean
    one_hot = np.eye(N_CLASSES)[labels]
    y_mean = one_hot.mean(axis=0)
    dual = centered @ centered.T
    dual.flat[::len(dual) + 1] += 1.0
    coefficients = np.linalg.solve(dual, one_hot - y_mean)
    scores = ((evaluation - x_mean) @ centered.T) @ coefficients + y_mean
    scores -= scores.max(axis=1, keepdims=True)
    probabilities = np.exp(scores)
    return _probabilities(probabilities / probabilities.sum(axis=1, keepdims=True), len(evaluation))


def temperature_probabilities(probabilities, beta, *, diagnostics=None):
    """Positive calibration with bounded restoration of float64-only ties.

    A positive transform cannot reverse an ordering mathematically, but a small
    temperature can round distinct maxima to the same float. Only exact output
    ties whose lost mathematical gap is at most four output ULPs are repaired:
    advance the original winner by one ULP. A strict reversal always refuses.
    The row-sum perturbation is at most that single rounding ULP.
    """
    np = _numpy()
    values = _probabilities(probabilities, len(probabilities))
    if not np.isfinite(beta) or not BETA_BOUNDS[0] <= beta <= BETA_BOUNDS[1]:
        raise ValueError("Inverse temperature must be positive and within [.05,20]")
    result = np.exp(_temperature_log_softmax(np.log(np.maximum(values, np.finfo(float).tiny)), beta))
    original_winners = values.argmax(axis=1)
    changed_rows = np.flatnonzero(result.argmax(axis=1) != original_winners)
    for row in changed_rows:
        winner = original_winners[row]
        maximum = result[row].max()
        if result[row, winner] != maximum:
            raise ValueError("Positive calibration caused a strict numerical order reversal")
        tied = np.flatnonzero(result[row] == maximum)
        tied_values = values[row, tied]
        if (tied_values <= 0).any():
            raise ValueError("Calibration tie exceeds a rounding-only correction")
        # p_w^beta / p_t^beta, evaluated accurately even for adjacent floats.
        log_ratios = beta * np.log1p((values[row, winner] - tied_values) / tied_values)
        lost_gaps = -maximum * np.expm1(-log_ratios)
        if (lost_gaps > 4 * np.spacing(maximum)).any():
            raise ValueError("Calibration tie exceeds a rounding-only correction")
        result[row, winner] = np.nextafter(maximum, np.inf)
    if not np.array_equal(result.argmax(axis=1), original_winners):
        raise ValueError("Positive calibration changed a numerical argmax")
    if diagnostics is not None:
        diagnostics["argmax_rounding_tie_corrections"] = int(len(changed_rows))
    return _probabilities(result, len(values))


def fit_inverse_temperature(probabilities, calibration_labels):
    """The frozen bounded class-macro scalar optimizer, specialized to four classes."""
    np = _numpy()
    labels = _labels(calibration_labels)
    values = _probabilities(probabilities, len(labels))
    counts = np.bincount(labels, minlength=N_CLASSES)
    logs = np.log(np.maximum(values, np.finfo(float).tiny))
    weights = 1.0 / (np.count_nonzero(counts) * counts[labels])
    target = logs[np.arange(len(labels)), labels]

    def objective(beta):
        return float(-np.sum(weights * _temperature_log_softmax(logs, beta)[np.arange(len(labels)), labels]))

    def derivative(beta):
        calibrated = np.exp(_temperature_log_softmax(logs, beta))
        return float(np.sum(weights * ((calibrated * logs).sum(axis=1) - target)))

    lower, upper = BETA_BOUNDS
    steps = 0
    if np.all(np.ptp(logs, axis=1) == 0):
        beta, boundary = 1.0, "flat"
    elif derivative(lower) >= 0:
        beta, boundary = lower, "lower"
    elif derivative(upper) <= 0:
        beta, boundary = upper, "upper"
    else:
        for _ in range(BISECTION_STEPS):
            middle = (lower + upper) / 2
            if derivative(middle) > 0:
                upper = middle
            else:
                lower = middle
        beta, boundary, steps = (lower + upper) / 2, "interior", BISECTION_STEPS
    before, after = objective(1.0), objective(beta)
    if after > before + 1e-12:
        raise ValueError("Temperature optimization increased its inner calibration objective")
    return {"inverse_temperature": float(beta), "boundary": boundary, "bisection_steps": steps,
            "calibration_trials": len(labels), "class_macro_nll_before": before,
            "class_macro_nll_after": after, "observed_calibration_classes": int(np.count_nonzero(counts)),
            "calibration_class_counts": counts.tolist()}


def _predict_arms(features, labels, null_labels, train, validation, check):
    np = _numpy()
    p_train, p_test = _standardized_block(features["P"][train], features["P"][validation])
    e_train, e_test = _standardized_block(features["E_action"][train], features["E_action"][validation])
    c_train, c_test = _standardized_block(features["E_cue"][train], features["E_cue"][validation])
    late_train, late_test = _standardized_block(features["E_late"][train], features["E_late"][validation])
    joint = (np.concatenate((p_train, e_train), axis=1), np.concatenate((p_test, e_test), axis=1))
    blocks = {"P": (p_train, p_test), "joint": joint, "joint_shuffled": joint,
              "cue_joint": (np.concatenate((p_train, c_train), axis=1), np.concatenate((p_test, c_test), axis=1)),
              "late_joint": (np.concatenate((p_train, late_train), axis=1),
                             np.concatenate((p_test, late_test), axis=1)),
              "deranged_joint": (np.concatenate((p_train, np.roll(e_train, 1, axis=0)), axis=1),
                                  np.concatenate((p_test, np.roll(e_test, 1, axis=0)), axis=1))}
    result = {}
    for arm in LEARNED_ARMS:
        if check is not None:
            check()
        result[arm] = _ridge_probabilities(blocks[arm][0],
            null_labels[train] if arm == "joint_shuffled" else labels[train], blocks[arm][1])
    return result


def run_condition(features, labels, original_trial_indices, *, seed=SEED, check=None):
    """Return prediction arrays and fit diagnostics; never score outer targets.

    Return keys are predictions (eight calibrated/control arrays), uncalibrated
    (six learned arrays), and fit_diagnostics (JSON-safe counts/settings/fits).
    P includes all 77 peripheral features plus exactly eight caller-supplied
    target-free timing/run/order columns; no direction identity may enter them.
    """
    np = _numpy()
    started = time.monotonic()
    labels, plans, fold_records = _nested_plan(labels, original_trial_indices, seed)
    if set(features) != {"P", "E_action", "E_cue", "E_late"}:
        raise ValueError("Expected exactly P, E_action, E_cue and E_late feature blocks")
    features = {name: _matrix(values, name) for name, values in features.items()}
    if features["P"].shape != (len(labels), 85) or any(
            features[name].shape != (len(labels), 640) for name in ("E_action", "E_cue", "E_late")):
        raise ValueError("Expected n×85 peripheral/timing and three n×640 EEG blocks")
    predictions = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in ARMS}
    raw_predictions = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in LEARNED_ARMS}
    for fold, (train, validation, inner, null_labels) in enumerate(plans):
        oof = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in LEARNED_ARMS}
        for inner_train, inner_validation in inner:
            inner_predictions = _predict_arms(features, labels, null_labels, inner_train, inner_validation, check)
            for arm in LEARNED_ARMS:
                oof[arm][inner_validation] = inner_predictions[arm]
        temperatures = {}
        for arm in LEARNED_ARMS:
            if check is not None:
                check()
            temperatures[arm] = fit_inverse_temperature(oof[arm][train],
                null_labels[train] if arm == "joint_shuffled" else labels[train])
        outer_predictions = _predict_arms(features, labels, null_labels, train, validation, check)
        for arm in LEARNED_ARMS:
            raw_predictions[arm][validation] = outer_predictions[arm]
            predictions[arm][validation] = temperature_probabilities(
                outer_predictions[arm], temperatures[arm]["inverse_temperature"], diagnostics=temperatures[arm])
        predictions["uniform"][validation] = 1.0 / N_CLASSES
        predictions["training_prior"][validation] = (
            np.bincount(labels[train], minlength=N_CLASSES) + 1) / (len(train) + N_CLASSES)
        fold_records[fold]["temperatures"] = temperatures
    for values in (*predictions.values(), *raw_predictions.values()):
        _probabilities(values, len(labels))
    return {"predictions": predictions, "uncalibrated": raw_predictions, "fit_diagnostics": {
        "n_trials": len(labels), "seed_block": [seed, seed + 3], "outer_folds": fold_records,
        "ridge_fits": 96, "temperature_fits": 24, "ridge_alpha": 1.0,
        "beta_bounds": list(BETA_BOUNDS), "bisection_steps": BISECTION_STEPS,
        "standardization": "current training rows only; each P/EEG block divided by sqrt(dimension)",
        "inner_folds": "three remaining original outer blocks, intersected with outer training",
        "embargo": "original temporal index adjacency plus/minus one at both split levels",
        "shuffle": "one outer-training permutation preserved across all inner fits and temperature calibration",
        "class_support_policy": "four classes globally; missing training classes permitted; temperature macro over observed calibration classes",
        "window_samples": {"action": 2048, "cue": 384, "matched_late": 384},
        "fft_resolution_hz": {"action": 0.5, "cue_and_matched_late": SFREQ / 384},
        "spectral_power_normalization": "one-sided abs(rfft(demean(x)*hanning(N)))^2/(N*sum(hanning(N)^2))",
        "log_power_variance_floor": float(np.finfo(float).tiny), "variance_ddof": 0,
        "training_prior": "outer-training add-one counts divided by ntrain+4",
        "derangement": "one-row cyclic EEG reassignment within each current training/test fold separately",
        "argmax_rounding_tie_corrections": sum(
            record["temperatures"][arm]["argmax_rounding_tie_corrections"]
            for record in fold_records for arm in LEARNED_ARMS),
        "argmax_tie_policy": "exact output ties only; mathematical lost gap at most4ULPs; original winner advanced1ULP; strict reversals refuse",
        "argmax_changes": 0, "outer_scores_computed": False,
        "elapsed_seconds": time.monotonic() - started}}


def _metrics(probabilities, labels):
    np = _numpy()
    values = _probabilities(probabilities, len(labels))
    counts = _four_classes(labels)
    predicted = values.argmax(axis=1)
    confusion = np.zeros((N_CLASSES, N_CLASSES), dtype=np.int64)
    np.add.at(confusion, (labels, predicted), 1)
    losses = -np.log(np.maximum(values[np.arange(len(labels)), labels], 1e-15))
    return {"n_trials": len(labels), "class_counts": counts.tolist(),
            "class_macro_nll": float(np.mean([losses[labels == c].mean() for c in range(N_CLASSES)])),
            "balanced_accuracy": float(np.mean(np.diag(confusion) / counts)),
            "confusion_matrix_actual_by_predicted": confusion.tolist()}


def score_condition(predictdict, labels):
    """Score a frozen run_condition result once; all outputs are aggregates."""
    np = _numpy()
    labels = _labels(labels)
    _four_classes(labels)
    predictions, raw = predictdict["predictions"], predictdict["uncalibrated"]
    if set(predictions) != set(ARMS) or set(raw) != set(LEARNED_ARMS):
        raise ValueError("All eight matched arms and six uncalibrated diagnostics are required")
    metrics = {arm: _metrics(values, labels) for arm, values in predictions.items()}
    uncalibrated = {arm: _metrics(values, labels) for arm, values in raw.items()}
    if any(not np.array_equal(np.asarray(predictions[arm]).argmax(axis=1), np.asarray(raw[arm]).argmax(axis=1))
           for arm in LEARNED_ARMS):
        raise ValueError("Frozen calibrated and uncalibrated argmax decisions differ")
    gains = {arm: metrics[arm]["class_macro_nll"] - metrics["joint"]["class_macro_nll"]
             for arm in PRIMARY_COMPARATORS}
    return {"metrics": metrics, "uncalibrated_diagnostic": uncalibrated,
            "primary_joint_nll_gains": gains,
            "joint_nll_gain_over_cue_joint": metrics["cue_joint"]["class_macro_nll"] -
                                           metrics["joint"]["class_macro_nll"],
            "matched_late_nll_gain_over_cue_joint": metrics["cue_joint"]["class_macro_nll"] -
                                                  metrics["late_joint"]["class_macro_nll"],
            "cue_comparison_establishes_neural_origin": False}
