"""Stream original calibration trials into paired EEG power representations.

Only the six established calibration filenames are admitted. Default EEG
preprocessing is unchanged; the optional attribution mode adds matched
normalization and fixed-sham controls. Each original trial, containing five repetitions, supplies
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
ATTRIBUTION_ARMS = ("raw_repetition", "normalized_repetition", "filtered_repetition",
                    "sham_normalized_repetition", "sham_filtered_repetition")
SHAM_SEED = 20260922
TIME_FREQUENCY_BANDS = ("band_2_4", "band_4_8", "band_8_13", "band_13_30",
                        "band_30_60", "band_60_118")
TIME_FREQUENCY_WIDTHS = {"full_all": EEG_FEATURES,
                         **{name: N_EEG for name in TIME_FREQUENCY_BANDS},
                         "early_all": EEG_FEATURES, "late_all": EEG_FEATURES}


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


def _source_normalize(values):
    """Exact EEG normalization inside adaptive_residual, before any cropping."""
    _, np = _dependencies()
    data = np.asarray(values, dtype=np.float64)
    return ((data - data.mean(axis=1, keepdims=True)) /
            (data.std(axis=1, ddof=1, keepdims=True) + np.finfo(float).eps))


def _sham_template():
    """One fixed conventionally filtered Gaussian input, with no data arguments."""
    _, np = _dependencies()
    length = TRIAL_SAMPLES + JITTER_SAMPLES
    gaussian = np.random.default_rng(SHAM_SEED).normal(0.0, 1.0, (N_EEG, length))
    template, _ = source_filter(gaussian, np.zeros((5, length), dtype=np.float64))
    return template


def _attribution_trial_features(eeg, auxiliary, sham):
    """Hold physiological inputs and source NLMS fixed across real/sham EEG."""
    from neurodecodekit.experiments.speech_repetition_power import paired_power_features

    _, np = _dependencies()
    filtered_eeg, filtered_auxiliary = source_filter(eeg, auxiliary)
    physiological = filtered_auxiliary[2:]
    views = {
        "raw_repetition": filtered_eeg,
        "normalized_repetition": _source_normalize(filtered_eeg),
        "filtered_repetition": adaptive_residual(filtered_eeg, physiological, seed=ADAPTIVE_SEED),
        "sham_normalized_repetition": _source_normalize(sham),
        "sham_filtered_repetition": adaptive_residual(sham, physiological, seed=ADAPTIVE_SEED),
    }
    center = slice(CENTER_OFFSET, CENTER_OFFSET + TRIAL_SAMPLES)
    auxiliary_full = filtered_auxiliary[:, center].astype(np.float32)[None]
    nuisance = fixed_channel_features(average_repetitions(auxiliary_full),
                                      full_trial=auxiliary_full, sfreq=SFREQ)[0]
    features, diagnostics = {}, {}
    for name, values in views.items():
        powers = paired_power_features(values[:, center].astype(np.float32)[None])
        features[name] = powers["repetition"][0]
        diagnostics[name] = powers["diagnostics"]
    if nuisance.shape != (390,) or not np.isfinite(nuisance).all():
        raise ValueError("Original auxiliary features must contain 390 finite values")
    if any(values.shape != (EEG_FEATURES,) or not np.isfinite(values).all()
           for values in features.values()):
        raise ValueError("Attribution EEG power features must contain 768 finite values")
    return nuisance, features, diagnostics


def _time_frequency_trial_features(eeg, auxiliary):
    """Independent EEG/auxiliary transforms; repetitions remain one trial row."""
    from neurodecodekit.experiments.speech_repetition_power import _band_energies

    _, np = _dependencies()
    filtered_eeg, filtered_auxiliary = source_filter(eeg, auxiliary)
    center = slice(CENTER_OFFSET, CENTER_OFFSET + TRIAL_SAMPLES)
    eeg_full = _source_normalize(filtered_eeg)[:, center].astype(np.float32).astype(np.float64)
    repetitions = eeg_full.reshape(N_EEG, 5, REPETITION_SAMPLES)
    energies = _band_energies(repetitions)
    total = energies.mean(axis=1)
    floor = np.finfo(float).tiny

    def log_flat(values):
        return np.log(np.maximum(values, floor)).reshape(-1)

    powers = {"full_all": log_flat(total)}
    powers.update({name: log_flat(total[:, band])
                   for band, name in enumerate(TIME_FREQUENCY_BANDS)})
    powers["early_all"] = log_flat(energies[:, :2].mean(axis=1))
    powers["late_all"] = log_flat(energies[:, -2:].mean(axis=1))
    auxiliary_full = filtered_auxiliary[:, center].astype(np.float32)[None]
    original = fixed_channel_features(average_repetitions(auxiliary_full),
                                       full_trial=auxiliary_full, sfreq=SFREQ)[0]
    raw_aux = auxiliary_full.astype(np.float64).reshape(5, 5, REPETITION_SAMPLES)
    normalized_aux = _source_normalize(filtered_auxiliary)[:, center].astype(np.float32)
    normalized_aux = normalized_aux.astype(np.float64).reshape(5, 5, REPETITION_SAMPLES)
    nuisance = np.concatenate((original, log_flat(_band_energies(raw_aux)),
                               log_flat(_band_energies(normalized_aux))))
    coherent_sum = _band_energies(repetitions.mean(axis=1)).sum(axis=0)
    diagnostic = {**_empty_diagnostic(), "n_trials": 1,
                  "coherent_band_power_sum": coherent_sum.tolist(),
                  "total_band_power_sum": total.sum(axis=0).tolist()}
    if nuisance.shape != (690,) or not np.isfinite(nuisance).all():
        raise ValueError("Time-frequency auxiliary features require 690 finite values before timing")
    if any(values.shape != (TIME_FREQUENCY_WIDTHS[name],) or not np.isfinite(values).all()
           for name, values in powers.items()):
        raise ValueError("Invalid time-frequency EEG features")
    return nuisance, powers, {"full_all": diagnostic}


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


def extract_calibration_power(edf_path, events_path, channels_path, *, progress=None,
                              mode="repetition_power"):
    """Return 100 auxiliary rows and matched original-trial EEG feature matrices.

    ``progress(completed_trials, total_trials)`` may raise to enforce the
    caller's deadline. Raw here means before adaptive filtering, not unfiltered
    EDF values. Diagnostics pool powers across channels and original trials;
    their ratios are ratios of totals, with no individual-trial payload.
    The default four views are unchanged. ``mode='adaptive_attribution'``
    returns five repetition-power views, including normalization-only and
    fixed-sham controls. Of the two sham views, only sham_filtered depends
    on real auxiliary input; neither sham input uses recorded EEG samples.
    ``mode='time_frequency'`` supplies nine auxiliary-independent EEG views
    and 692 auxiliary columns. Early/late identify repetition positions, not
    temporal localization after whole-trial noncausal preprocessing.
    """
    edf, events, channels, recording_id = _calibration_paths(edf_path, events_path, channels_path)
    if mode not in ("repetition_power", "adaptive_attribution", "time_frequency"):
        raise ValueError("Unknown calibration power extraction mode")
    attribution = mode == "adaptive_attribution"
    time_frequency = mode == "time_frequency"
    widths = (TIME_FREQUENCY_WIDTHS if time_frequency else
              {arm: EEG_FEATURES for arm in (ATTRIBUTION_ARMS if attribution else EEG_ARMS)})
    arms = tuple(widths)
    auxiliary_columns = 692 if time_frequency else 392
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
        auxiliary_features = np.empty((EXPECTED_TRIALS, auxiliary_columns), dtype=np.float64)
        eeg_features = {arm: np.empty((EXPECTED_TRIALS, widths[arm]), dtype=np.float64)
                        for arm in arms}
        diagnostics = {name: _empty_diagnostic()
                       for name in (("full_all",) if time_frequency else
                                    arms if attribution else ("raw", "filtered"))}
        sham = _sham_template() if attribution else None
        for index, (end, action_start) in enumerate(zip(bounds["buffer_ends"], action_starts)):
            if progress is not None:
                progress(index, EXPECTED_TRIALS)
            samples = raw.get_data(picks=picks, start=int(end) - (TRIAL_SAMPLES + JITTER_SAMPLES),
                                   stop=int(end))
            if samples.shape != (N_EEG + 10, TRIAL_SAMPLES + JITTER_SAMPLES):
                raise ValueError("Source read must retain 128 EEG and ten auxiliary columns")
            auxiliary = samples[N_EEG::2] - samples[N_EEG + 1::2]
            if time_frequency:
                nuisance, powers, diagnostic = _time_frequency_trial_features(samples[:N_EEG], auxiliary)
                auxiliary_features[index, 392:] = nuisance[390:]
            elif attribution:
                nuisance, powers, diagnostic = _attribution_trial_features(samples[:N_EEG], auxiliary, sham)
            else:
                nuisance, powers, diagnostic = _trial_features(samples[:N_EEG], auxiliary)
            auxiliary_features[index, :390] = nuisance[:390]
            auxiliary_features[index, 390:392] = (index, float(action_start) / SFREQ)
            for arm in arms:
                eeg_features[arm][index] = powers[arm]
            for name in diagnostics:
                _merge_diagnostic(diagnostics[name], diagnostic[name])
        if progress is not None:
            progress(EXPECTED_TRIALS, EXPECTED_TRIALS)
        if not np.isfinite(auxiliary_features).all() or any(
                not np.isfinite(values).all() for values in eeg_features.values()):
            raise ValueError("Nonfinite complete calibration feature matrix")
        result = {
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
                "auxiliary_feature_columns": auxiliary_columns,
                "eeg_feature_columns_per_arm": widths if time_frequency else EEG_FEATURES,
                **({"adaptive_filter_used": False} if time_frequency else
                   {"adaptive_seed": ADAPTIVE_SEED, "adaptive_state_reset_each_trial": True}),
                "elapsed_seconds": time.monotonic() - started,
            },
            "power_diagnostics": {name: _finish_diagnostic(values)
                                  for name, values in diagnostics.items()},
        }
        if attribution:
            result["timing_summary"].update({
                "mode": mode,
                "normalization": "full_1626_samples_float64_channelwise_ddof1_plus_float64_epsilon",
                "sham": {
                    "seed": SHAM_SEED, "generator": "numpy_default_rng_standard_normal",
                    "shape": [N_EEG, TRIAL_SAMPLES + JITTER_SAMPLES],
                    "source_filter_calls_per_extraction": 1,
                    "preprocessing_auxiliary": "five_zero_channels",
                    "identical_input_all_trials_and_recordings": True,
                    "input_independent_of_real_data_labels_and_trial_ids": True,
                    "recorded_eeg_channel_samples_in_sham_input": False,
                    "filtered_view_uses_real_filtered_eog_and_lips": True,
                },
            })
        if time_frequency:
            result["timing_summary"].update({
                "mode": mode,
                "physiological_auxiliary_in_eeg_preprocessing": False,
                "normalization": "full_1626_samples_float64_channelwise_ddof1_plus_float64_epsilon",
                "power_order": "crop_float32_then_float64_320_fft_mean_powers_before_log",
                "time_position_interpretation": "repetition_position_not_temporal_localization",
                "whole_trial_noncausal_preprocessing": True,
                "repetition_positions": {"full_all": [0, 1, 2, 3, 4],
                                         "early_all": [0, 1], "late_all": [3, 4]},
                "auxiliary_column_ranges": {"original": [0, 392], "timing": [390, 392],
                                             "raw_repetition_log_power": [392, 542],
                                             "normalized_repetition_log_power": [542, 692]},
                "auxiliary_power_flatten_order": "channel_repetition_band",
                "auxiliary_normalization_per_repetition": False,
            })
        return result
    finally:
        raw.close()
