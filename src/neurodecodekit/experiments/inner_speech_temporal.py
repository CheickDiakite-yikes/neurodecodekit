"""Fixed arrays-only temporal development comparison; prediction never scores targets."""

from __future__ import annotations

import time

from neurodecodekit.evaluation.speech_reproduction import _matrix, _numpy, _standardized_block
from neurodecodekit.experiments import inner_speech as spectral
from neurodecodekit.experiments.inner_speech import (
    BETA_BOUNDS,
    BISECTION_STEPS,
    N_CLASSES,
    SEED,
    SFREQ,
    _four_classes,
    _labels,
    _metrics,
    _nested_plan,
    _probabilities,
    _retention_record,
    _ridge_probabilities,
    _window,
    fit_inverse_temperature,
    temperature_probabilities,
)


LEARNED_ARMS = (
    "P", "joint", "cue_joint", "late_joint", "deranged_joint", "joint_shuffled",
    "spectral_joint", "action_eeg", "action_eeg_shuffled", "cue_eeg", "cue_eeg_shuffled",
)
ARMS = (*LEARNED_ARMS, "uniform", "training_prior")
SHUFFLED_ARMS = ("joint_shuffled", "action_eeg_shuffled", "cue_eeg_shuffled")
PRIMARY_COMPARATORS = (
    "P", "deranged_joint", "joint_shuffled", "uniform", "training_prior", "spectral_joint",
)
FEATURE_WIDTHS = {"P": 440, "E_action": 4096, "E_cue": 4096, "E_late": 4096, "E_spectral": 640}


def temporal_window_features(eeg_uV, exg_uV, *, sfreq=SFREQ):
    """Return E[4096], P_temporal[352], channel-major then 32 signed bin means.

    Windows contain exactly 2048 or 384 samples. EEG-only CAR precedes channel
    demean; EXG uses the existing eight referenced channels plus three bipolar
    differences, each demeaned independently. No filter, outside sample, learned
    transform, trial normalization or EEG/EXG cross-input enters either block.
    Caller concatenates old P[77], timing/availability[11], P_temporal[352].
    """
    np = _numpy()
    if sfreq != SFREQ:
        raise ValueError("The fixed temporal recipe requires 1024 Hz")
    eeg, exg = _window(eeg_uV, 128), _window(exg_uV, 8)
    if eeg.shape[1] != exg.shape[1]:
        raise ValueError("EEG and EXG must use the same complete window")
    eeg = eeg - eeg.mean(axis=0, keepdims=True)
    exg = exg - exg[:2].mean(axis=0, keepdims=True)
    exg = np.concatenate((exg, exg[2:8:2] - exg[3:8:2]), axis=0)

    def bins(values):
        centered = values - values.mean(axis=1, keepdims=True)
        result = centered.reshape(len(values), 32, values.shape[1] // 32).mean(axis=2)
        if not np.isfinite(result).all():
            raise ValueError("Nonfinite temporal window features")
        return result.reshape(-1)

    return {"E": bins(eeg), "P_temporal": bins(exg)}


def preflight_condition(labels, original_trial_indices, *, seed=SEED, nominal_trial_indices=None):
    """Preserve original nominal blocks and both embargo levels, without any fit.

    The inherited numerical retention ceiling is not an eligibility policy.
    The caller must enforce the separately frozen session-2 admission rule.
    """
    if nominal_trial_indices is None:
        raise ValueError("Temporal development requires original nominal condition indices")
    return spectral.preflight_condition(labels, original_trial_indices, seed=seed,
                                        nominal_trial_indices=nominal_trial_indices)


def _predict_arms(features, labels, null_labels, train, validation, check):
    np = _numpy()
    scaled = {name: _standardized_block(values[train], values[validation])
              for name, values in features.items()}
    p_train, p_test = scaled["P"]

    def joint(name, *, deranged=False):
        e_train, e_test = scaled[name]
        if deranged:
            e_train, e_test = np.roll(e_train, 1, axis=0), np.roll(e_test, 1, axis=0)
        return np.concatenate((p_train, e_train), axis=1), np.concatenate((p_test, e_test), axis=1)

    action_joint = joint("E_action")
    blocks = {"P": scaled["P"], "joint": action_joint, "joint_shuffled": action_joint,
              "cue_joint": joint("E_cue"), "late_joint": joint("E_late"),
              "deranged_joint": joint("E_action", deranged=True),
              "spectral_joint": joint("E_spectral"),
              "action_eeg": scaled["E_action"], "action_eeg_shuffled": scaled["E_action"],
              "cue_eeg": scaled["E_cue"], "cue_eeg_shuffled": scaled["E_cue"]}
    predictions = {}
    for arm in LEARNED_ARMS:
        if check is not None:
            check()
        predictions[arm] = _ridge_probabilities(blocks[arm][0],
            null_labels[train] if arm in SHUFFLED_ARMS else labels[train], blocks[arm][1])
    return predictions


def run_condition(features, labels, original_trial_indices, *, seed=SEED, check=None,
                  nominal_trial_indices=None):
    """Return 13 prediction arrays, 11 raw arrays and JSON-safe fit diagnostics.

    No outer-target metric is computed here. All eleven models share the exact
    nominal-slot nested plan; three null arms share one outer-training label
    permutation throughout inner fitting, scalar calibration and outer fitting.
    P is one 440-column block, identical for every joint or nuisance arm.
    """
    np = _numpy()
    started = time.monotonic()
    if nominal_trial_indices is None:
        raise ValueError("Temporal development requires original nominal condition indices")
    labels, plans, records = _nested_plan(labels, original_trial_indices, seed, nominal_trial_indices)
    if set(features) != set(FEATURE_WIDTHS):
        raise ValueError("Expected exactly P, E_action, E_cue, E_late and E_spectral")
    features = {name: _matrix(features[name], name) for name in FEATURE_WIDTHS}
    if any(values.shape != (len(labels), FEATURE_WIDTHS[name]) for name, values in features.items()):
        raise ValueError("Expected P440, three temporal EEG4096 blocks, and spectral EEG640")
    predictions = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in ARMS}
    raw_predictions = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in LEARNED_ARMS}
    for fold, (train, validation, inner, null_labels) in enumerate(plans):
        oof = {arm: np.full((len(labels), N_CLASSES), np.nan) for arm in LEARNED_ARMS}
        for inner_train, inner_validation in inner:
            fitted = _predict_arms(features, labels, null_labels, inner_train, inner_validation, check)
            for arm in LEARNED_ARMS:
                oof[arm][inner_validation] = fitted[arm]
        temperatures = {}
        for arm in LEARNED_ARMS:
            if check is not None:
                check()
            temperatures[arm] = fit_inverse_temperature(oof[arm][train],
                null_labels[train] if arm in SHUFFLED_ARMS else labels[train])
        fitted = _predict_arms(features, labels, null_labels, train, validation, check)
        for arm in LEARNED_ARMS:
            raw_predictions[arm][validation] = fitted[arm]
            predictions[arm][validation] = temperature_probabilities(
                fitted[arm], temperatures[arm]["inverse_temperature"], diagnostics=temperatures[arm])
        predictions["uniform"][validation] = 1.0 / N_CLASSES
        predictions["training_prior"][validation] = (
            np.bincount(labels[train], minlength=N_CLASSES) + 1) / (len(train) + N_CLASSES)
        records[fold]["temperatures"] = temperatures
    for values in (*predictions.values(), *raw_predictions.values()):
        _probabilities(values, len(labels))
    diagnostics = {
        "n_trials": len(labels), "seed_block": [seed, seed + 3], "outer_folds": records,
        "feature_dimensions": dict(FEATURE_WIDTHS), "peripheral_timing_features": 440,
        "peripheral_feature_order": ["spectral_variance_77", "timing_availability_11", "temporal_352"],
        "temporal_bins_per_channel": 32, "temporal_demean": "per-window per-channel",
        "temporal_filter": "none", "EEG_reference": "128-channel EEG-only common average",
        "EXG_reference": "mean(EXG1,EXG2); eight referenced channels plus EXG3-4,EXG5-6,EXG7-8",
        "ridge_fits": 176, "temperature_fits": 44, "ridge_alpha": 1.0,
        "beta_bounds": list(BETA_BOUNDS), "bisection_steps": BISECTION_STEPS,
        "standardization": "current training rows only; each P/EEG block divided by sqrt(dimension)",
        "inner_folds": "three remaining original outer blocks, intersected with outer training",
        "embargo": "original temporal index adjacency plus/minus one at both split levels",
        "shuffle": "one outer-training permutation shared by all null arms, inner fits and calibration",
        "class_support_policy": "four classes globally; missing training classes permitted; temperature macro over observed calibration classes",
        "window_samples": {"action": 2048, "cue": 384, "matched_late": 384},
        "samples_per_temporal_bin": {"action": 64, "cue": 12, "matched_late": 12},
        "training_prior": "outer-training add-one counts divided by ntrain+4",
        "derangement": "one-row cyclic EEG reassignment within each current training/test fold separately",
        "argmax_rounding_tie_corrections": sum(
            record["temperatures"][arm]["argmax_rounding_tie_corrections"]
            for record in records for arm in LEARNED_ARMS),
        "argmax_tie_policy": "exact output ties only; mathematical lost gap at most4ULPs; original winner advanced1ULP; strict reversals refuse",
        "argmax_changes": 0, "outer_scores_computed": False,
        "elapsed_seconds": time.monotonic() - started,
        **_retention_record(original_trial_indices, nominal_trial_indices),
    }
    return {"predictions": predictions, "uncalibrated": raw_predictions, "fit_diagnostics": diagnostics}


def score_condition(predictdict, labels):
    """Score a frozen bundle into aggregates only; the caller owns the one-shot gate."""
    np = _numpy()
    labels = _labels(labels)
    _four_classes(labels)
    predictions, raw = predictdict["predictions"], predictdict["uncalibrated"]
    if set(predictions) != set(ARMS) or set(raw) != set(LEARNED_ARMS):
        raise ValueError("All thirteen arms and eleven uncalibrated diagnostics are required")
    metrics = {arm: _metrics(predictions[arm], labels) for arm in ARMS}
    uncalibrated = {arm: _metrics(raw[arm], labels) for arm in LEARNED_ARMS}
    if any(not np.array_equal(np.asarray(predictions[arm]).argmax(axis=1), np.asarray(raw[arm]).argmax(axis=1))
           for arm in LEARNED_ARMS):
        raise ValueError("Frozen calibrated and uncalibrated argmax decisions differ")
    gains = {arm: metrics[arm]["class_macro_nll"] - metrics["joint"]["class_macro_nll"]
             for arm in PRIMARY_COMPARATORS}
    sensitivity = {arm: {control: metrics[control]["class_macro_nll"] - metrics[arm]["class_macro_nll"]
                        for control in (f"{arm}_shuffled", "uniform", "training_prior")}
                   for arm in ("action_eeg", "cue_eeg")}
    return {"metrics": metrics, "uncalibrated_diagnostic": uncalibrated,
            "primary_joint_nll_gains": gains, "eeg_sensitivity_nll_gains": sensitivity,
            "joint_nll_gain_over_cue_joint": metrics["cue_joint"]["class_macro_nll"] -
                                           metrics["joint"]["class_macro_nll"],
            "matched_late_nll_gain_over_cue_joint": metrics["cue_joint"]["class_macro_nll"] -
                                                  metrics["late_joint"]["class_macro_nll"],
            "cue_comparison_establishes_neural_origin": False,
            "eeg_sensitivity_establishes_neural_origin": False}
