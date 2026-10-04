"""Calibration-only extraction of the original SPEECH-REPRO-1 nuisance features.

This branch reads the five bipolar auxiliary pairs and the timing trigger;
it computes no EEG feature or adaptive residual. The caller must verify the
pinned source hashes before calling. No online filename is admitted, and no
model fitting, scoring, or file writing occurs in this module.
"""

from __future__ import annotations

import time
from pathlib import Path

from neurodecodekit.evaluation.speech_reproduction import fixed_channel_features
from neurodecodekit.preprocess.speech_reproduction import (
    AUX_PAIRS,
    CENTER_OFFSET,
    JITTER_SAMPLES,
    SFREQ,
    TRIAL_SAMPLES,
    _read_tsv,
    _validate_edf_padding,
    average_repetitions,
    broker_event_rows,
    channel_layout,
    trial_bounds,
)


CALIBRATION_IDENTITIES = (
    ("1", "20230511", "minimallyovert"), ("1", "20230529", "covert"),
    ("2", "20230512", "minimallyovert"), ("2", "20230516", "covert"),
    ("3", "20230523", "minimallyovert"), ("3", "20230524", "covert"),
)
CALIBRATION_BASENAMES = frozenset(
    f"sub-{person}_ses-{session}_task-{condition}_acq-calibration_run-01"
    for person, session, condition in CALIBRATION_IDENTITIES
)
AUXILIARY_NAMES = ("DISPLAY", "MIC", "EOG", "UPPER", "LOWER")
EXPECTED_TRIALS = 100
FEATURES_PER_AUXILIARY = 78


def _dependencies():
    try:
        import mne
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Calibration auxiliary extraction requires neurodecodekit[neuro].") from exc
    return mne, np


def _calibration_paths(edf_path, events_path, channels_path):
    """Reject foreign/online paths before any file access or numerical import."""
    edf, events, channels = map(Path, (edf_path, events_path, channels_path))
    suffix = "_eeg.edf"
    if not edf.name.endswith(suffix) or edf.name[:-len(suffix)] not in CALIBRATION_BASENAMES:
        raise ValueError("Only the six selected calibration EDF filenames are admitted")
    identity = edf.name[:-len(suffix)]
    if events.name != f"{identity}_events.tsv" or channels.name != f"{identity}_channels.tsv":
        raise ValueError("Calibration event/channel filenames must match their EDF sibling")
    if not (edf.parent == events.parent == channels.parent):
        raise ValueError("Calibration EDF and sidecars must be in the same directory")
    return edf, events, channels, identity


def auxiliary_feature_row(auxiliary_window):
    """Match the original nuisance filter, float32 crop, average, and features.

    EEG-only notch/CAR and adaptive filtering in the original source_filter
    cannot change the auxiliary rows. Its all-channel raw.filter(2,118) uses
    these same filter_data defaults. Crucially, float32 conversion happens
    before repetition averaging, as in the original nuisance_full array.
    """
    mne, np = _dependencies()
    values = np.asarray(auxiliary_window, dtype=np.float64)
    if values.shape != (5, TRIAL_SAMPLES + JITTER_SAMPLES) or not np.isfinite(values).all():
        raise ValueError("Expected finite five-pair, 1626-sample auxiliary trial")
    filtered = mne.filter.filter_data(values, SFREQ, 2.0, 118.0, verbose=False)
    full = filtered[:, CENTER_OFFSET:CENTER_OFFSET + TRIAL_SAMPLES].astype(np.float32)[None]
    averaged = average_repetitions(full)
    return fixed_channel_features(averaged, full_trial=full, sfreq=SFREQ)[0]


def extract_calibration_auxiliary(edf_path, events_path, channels_path, *,
                                  recording_id=None, progress=None):
    """Return exactly 100 original-trial rows by 392 auxiliary/timing features.

    Feature order is 78 columns each for DISPLAY, MIC, EOG, UPPER, LOWER,
    followed by original trial index and action start time in recording seconds.
    ``progress(completed_trials, total_trials)`` follows the existing extractor
    and may raise to enforce the caller's resource deadline. Padding checks
    inspect auxiliary/trigger channels only; no EEG samples are requested.
    """
    edf, events, channels, identity = _calibration_paths(edf_path, events_path, channels_path)
    if recording_id is None:
        recording_id = identity
    if not isinstance(recording_id, str) or not recording_id:
        raise ValueError("A nonempty calibration recording identifier is required")
    mne, np = _dependencies()
    broker = broker_event_rows(_read_tsv(events), recording_id, role="calibration")
    if len(broker["trial_ids"]) != EXPECTED_TRIALS:
        raise ValueError("The selected calibration recording must contain exactly 100 original trials")
    labels = np.asarray(broker["calibration_labels"], dtype=np.int64)
    if set(labels.tolist()) != set(range(5)):
        raise ValueError("Calibration must retain all five original word classes")
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
        # The existing validator is reused with only admitted numerical picks.
        # This is explicitly not a claim about unseen EEG padding values.
        _validate_edf_padding(raw, {**layout, "eeg": []}, bounds)
        picks = [channel for pair in layout["aux_pairs"] for channel in pair]
        features = np.empty((EXPECTED_TRIALS, 5 * FEATURES_PER_AUXILIARY + 2), dtype=np.float64)
        for index, (end, action_start) in enumerate(zip(bounds["buffer_ends"], action_starts)):
            if progress is not None:
                progress(index, EXPECTED_TRIALS)
            samples = raw.get_data(picks=picks, start=int(end) - (TRIAL_SAMPLES + JITTER_SAMPLES),
                                   stop=int(end))
            if samples.shape != (2 * len(AUX_PAIRS), TRIAL_SAMPLES + JITTER_SAMPLES):
                raise ValueError("Auxiliary source read does not contain the complete original trial")
            auxiliary = samples[::2] - samples[1::2]
            features[index, :-2] = auxiliary_feature_row(auxiliary)
            features[index, -2:] = (index, float(action_start) / SFREQ)
        if not np.isfinite(features).all():
            raise ValueError("Nonfinite calibration auxiliary features")
        if progress is not None:
            progress(EXPECTED_TRIALS, EXPECTED_TRIALS)
        return {
            "features": features,
            "calibration_labels": labels,
            "trial_ids": broker["trial_ids"],
            "action_start_samples": action_starts.copy(),
            "timing_summary": {
                "route": bounds["route"], "trials": EXPECTED_TRIALS,
                "extra_leading_triggers": bounds["extra_leading_triggers"],
                "trailing_edf_padding_samples": bounds["trailing_edf_padding_samples"],
                "action_windows_nonoverlapping": True,
                "padding_validation_channels": "auxiliary_and_trigger_only",
                "numerical_auxiliary_pairs": list(AUXILIARY_NAMES),
                "eeg_samples_requested": False,
                "feature_columns": features.shape[1],
                "elapsed_seconds": time.monotonic() - started,
            },
        }
    finally:
        raw.close()
