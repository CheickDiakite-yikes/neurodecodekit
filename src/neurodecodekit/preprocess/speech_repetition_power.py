"""Stream original calibration trials into paired EEG power representations.

Only the six established calibration filenames are admitted. EEG preprocessing
is unchanged: one source_filter and one trial-reset adaptive_residual per
1626-sample window. Each original trial, containing five repetitions, supplies
one feature row. No EEG waveform cache, online access, model fit, or file write
is performed. The caller verifies source identities and enforces resource caps.
"""

from __future__ import annotations

import math
import time

from neurodecodekit.evaluation.speech_reproduction import BANDS, fixed_channel_features
from neurodecodekit.preprocess.speech_auxiliary import _calibration_paths, _dependencies
from neurodecodekit.preprocess.speech_reproduction import (
    CENTER_OFFSET,
    JITTER_SAMPLES,
    N_EEG,
    REPETITION_SAMPLES,
    SFREQ,
    TRIAL_SAMPLES,
    _read_tsv,
    _validate_edf_padding,
    adaptive_residual,
    average_repetitions,
    broker_event_rows,
    channel_layout,
    source_filter,
    trial_bounds,
)


EXPECTED_TRIALS = 100
ADAPTIVE_SEED = 20260906
EEG_FEATURES = N_EEG * len(BANDS)
EEG_ARMS = ("raw_evoked", "raw_repetition", "filtered_evoked", "filtered_repetition")


def _trial_features(eeg, auxiliary):
    """Transform one original trial, retaining no waveform beyond this call."""
    from neurodecodekit.experiments.speech_repetition_power import paired_power_features

    _, np = _dependencies()
    filtered_eeg, filtered_auxiliary = source_filter(eeg, auxiliary)
    residual = adaptive_residual(filtered_eeg, filtered_auxiliary[2:], seed=ADAPTIVE_SEED)
    center = slice(CENTER_OFFSET, CENTER_OFFSET + TRIAL_SAMPLES)
    raw_full = filtered_eeg[:, center].astype(np.float32)[None]
    filtered_full = residual[:, center].astype(np.float32)[None]
    auxiliary_full = filtered_auxiliary[:, center].astype(np.float32)[None]
    raw_power = paired_power_features(raw_full)
    filtered_power = paired_power_features(filtered_full)
    nuisance = fixed_channel_features(average_repetitions(auxiliary_full),
                                      full_trial=auxiliary_full, sfreq=SFREQ)[0]
    features = {
        "raw_evoked": raw_power["evoked"][0],
        "raw_repetition": raw_power["repetition"][0],
        "filtered_evoked": filtered_power["evoked"][0],
        "filtered_repetition": filtered_power["repetition"][0],
    }
    if nuisance.shape != (390,) or not np.isfinite(nuisance).all():
        raise ValueError("Original auxiliary features must contain 390 finite values")
    for values in features.values():
        if values.shape != (EEG_FEATURES,) or not np.isfinite(values).all():
            raise ValueError("Paired EEG power features must contain 768 finite values")
    return nuisance, features, {"raw": raw_power["diagnostics"],
                                 "filtered": filtered_power["diagnostics"]}


def _empty_diagnostic():
    return {
        "n_trials": 0, "n_channels": N_EEG, "repetitions": 5,
        "samples_per_repetition": REPETITION_SAMPLES,
        "bands": [list(band) for band in BANDS],
        "coherent_band_power_sum": [0.0] * len(BANDS),
        "total_band_power_sum": [0.0] * len(BANDS),
    }


def _merge_diagnostic(aggregate, single):
    """Sum target-free band-power totals, never average per-trial ratios."""
    fixed = {"n_trials": 1, "n_channels": N_EEG, "repetitions": 5,
             "samples_per_repetition": REPETITION_SAMPLES,
             "bands": [list(band) for band in BANDS]}
    if not isinstance(single, dict) or any(single.get(key) != value for key, value in fixed.items()):
        raise ValueError("Power diagnostics must describe one complete original five-repetition trial")
    for name in ("coherent_band_power_sum", "total_band_power_sum"):
        values = single.get(name)
        if (not isinstance(values, list) or len(values) != len(BANDS)
                or any(type(value) not in (float, int) or not math.isfinite(value) or value < 0
                       for value in values)):
            raise ValueError("Power diagnostics must contain six finite nonnegative band totals")
        aggregate[name] = [old + new for old, new in zip(aggregate[name], values)]
    aggregate["n_trials"] += 1


def _finish_diagnostic(aggregate):
    if aggregate["n_trials"] != EXPECTED_TRIALS:
        raise ValueError("Power diagnostics do not retain all 100 original trials")
    pairs = list(zip(aggregate["coherent_band_power_sum"], aggregate["total_band_power_sum"]))
    if any(not math.isfinite(value) for pair in pairs for value in pair):
        raise ValueError("Nonfinite aggregate power diagnostic")
    aggregate["coherent_to_total_band_power_ratio"] = [
        coherent / total if total > 0 else None for coherent, total in pairs
    ]
    return aggregate


def extract_calibration_power(edf_path, events_path, channels_path, *, progress=None):
    """Return 100 auxiliary rows and four matched 100x768 EEG feature matrices.

    ``progress(completed_trials, total_trials)`` may raise to enforce the
    caller's deadline. Raw here means before adaptive filtering, not unfiltered
    EDF values. Diagnostics pool powers across channels and original trials;
    their ratios are ratios of totals, with no individual-trial payload.
    """
    edf, events, channels, recording_id = _calibration_paths(edf_path, events_path, channels_path)
    mne, np = _dependencies()
    broker = broker_event_rows(_read_tsv(events), recording_id, role="calibration")
    if len(broker["trial_ids"]) != EXPECTED_TRIALS:
        raise ValueError("Calibration requires exactly 100 complete original trials")
    labels = np.asarray(broker["calibration_labels"], dtype=np.int64)
    if set(labels.tolist()) != set(range(5)):
        raise ValueError("Calibration must retain all five original classes")
    started = time.monotonic()
    raw = mne.io.read_raw_edf(str(edf), preload=False, verbose=False)
    try:
        if raw.info["sfreq"] != SFREQ:
            raise ValueError("Source EDF sampling rate mismatch")
        layout = channel_layout(_read_tsv(channels), raw.ch_names)
        bounds = trial_bounds(raw.get_data(picks=[layout["trigger"]])[0],
                              broker["event_onsets"], raw.n_times)
        action_starts = bounds["action_starts"]
        if np.any(action_starts[1:] < action_starts[:-1] + TRIAL_SAMPLES):
            raise ValueError("Original calibration action windows overlap")
        _validate_edf_padding(raw, layout, bounds)
        picks = layout["eeg"] + [index for pair in layout["aux_pairs"] for index in pair]
        auxiliary_features = np.empty((EXPECTED_TRIALS, 392), dtype=np.float64)
        eeg_features = {arm: np.empty((EXPECTED_TRIALS, EEG_FEATURES), dtype=np.float64)
                        for arm in EEG_ARMS}
        diagnostics = {name: _empty_diagnostic() for name in ("raw", "filtered")}
        for index, (end, action_start) in enumerate(zip(bounds["buffer_ends"], action_starts)):
            if progress is not None:
                progress(index, EXPECTED_TRIALS)
            samples = raw.get_data(picks=picks, start=int(end) - (TRIAL_SAMPLES + JITTER_SAMPLES),
                                   stop=int(end))
            if samples.shape != (N_EEG + 10, TRIAL_SAMPLES + JITTER_SAMPLES):
                raise ValueError("Source read must retain 128 EEG and ten auxiliary columns")
            auxiliary = samples[N_EEG::2] - samples[N_EEG + 1::2]
            nuisance, powers, diagnostic = _trial_features(samples[:N_EEG], auxiliary)
            auxiliary_features[index, :-2] = nuisance
            auxiliary_features[index, -2:] = (index, float(action_start) / SFREQ)
            for arm in EEG_ARMS:
                eeg_features[arm][index] = powers[arm]
            for name in diagnostics:
                _merge_diagnostic(diagnostics[name], diagnostic[name])
        if progress is not None:
            progress(EXPECTED_TRIALS, EXPECTED_TRIALS)
        if not np.isfinite(auxiliary_features).all() or any(
                not np.isfinite(values).all() for values in eeg_features.values()):
            raise ValueError("Nonfinite complete calibration feature matrix")
        return {
            "auxiliary": auxiliary_features, "eeg_features": eeg_features,
            "calibration_labels": labels, "trial_ids": broker["trial_ids"],
            "timing_summary": {
                "route": bounds["route"], "trials": EXPECTED_TRIALS,
                "extra_leading_triggers": bounds["extra_leading_triggers"],
                "trailing_edf_padding_samples": bounds["trailing_edf_padding_samples"],
                "padding_validation_channels": "all_declared_channels",
                "action_windows_nonoverlapping": True,
                "retained_eeg_channels": N_EEG,
                "retained_bad_eeg_channels": layout["bad_eeg_count"],
                "waveform_cache_retained": False,
                "maximum_original_trials_per_numeric_window": 1,
                "auxiliary_feature_columns": 392, "eeg_feature_columns_per_arm": EEG_FEATURES,
                "adaptive_seed": ADAPTIVE_SEED, "adaptive_state_reset_each_trial": True,
                "elapsed_seconds": time.monotonic() - started,
            },
            "power_diagnostics": {name: _finish_diagnostic(values)
                                  for name, values in diagnostics.items()},
        }
    finally:
        raw.close()
