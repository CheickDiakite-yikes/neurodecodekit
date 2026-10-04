"""Source-aligned, target-separated extraction for SPEECH-REPRO-1.

Methods follow arayabrain/uhd-gmail-public at
0dca00584c528b288392684dcec0d496b6aa4951, especially bids/extract_from_bids.py,
DatasetUHD.py and preprocess/{adaptive_filter,padasip_mod}.py. The source
continuous trigger ends its 2880-sample buffer; it is NOT the start of the
following 6.25 seconds despite the generic BIDS event description.

Intentional registered deviations: adaptive state resets per original trial;
evaluation has no jitter; pre-action filtering sees no action samples. Numeric
features exclude trigger and annotations. This module never prints targets.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

SFREQ = 256
N_EEG = 128
TRIAL_SAMPLES = 1600
REPETITION_SAMPLES = 320
BUFFER_SAMPLES = 2880
JITTER_SAMPLES = 26
CENTER_OFFSET = 25
WORDS = ("green", "magenta", "orange", "violet", "yellow")
AUX_PAIRS = (
    ("DISPLAY+", "DISPLAY-"),
    ("MIC+", "MIC-"),
    ("EOG+", "EOG-"),
    ("EMG_UPPER_OOris+", "EMG_UPPER_OOris-"),
    ("EMG_LOWER_OOris+", "EMG_LOWER_OOris-"),
)


def _read_tsv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def validate_source_geometry(electrodes_path, coordsystem_path):
    """Check the pinned release's named 128-electrode geometry, without targets."""
    rows = _read_tsv(electrodes_path)
    expected = {f"EEG{i:03d}" for i in range(1, N_EEG + 1)}
    if len(rows) != N_EEG or {row.get("name") for row in rows} != expected:
        raise ValueError("Source geometry must contain each of EEG001 through EEG128 once")
    for row in rows:
        if not all(math.isfinite(float(row[axis])) for axis in ("x", "y", "z")):
            raise ValueError("Source electrode coordinates must be finite")
    coordinates = json.loads(Path(coordsystem_path).read_text(encoding="utf-8"))
    expected_description = (
        "Subject head coordinate system from g.tec electrode digitization "
        "(electrodes_uhd.xml). 3D coordinates in the subject's head space."
    )
    if (coordinates.get("EEGCoordinateUnits") != "mm"
            or coordinates.get("EEGCoordinateSystem") != "Other"
            or coordinates.get("EEGCoordinateSystemDescription") != expected_description):
        raise ValueError("Source geometry coordinate frame differs from pinned metadata")
    return {"eeg_electrodes": N_EEG, "coordinate_units": "mm",
            "coordinate_system": "Other", "finite_coordinates": True}


def channel_layout(channel_rows, raw_names):
    """Validate the declared source roles; never select channels by position."""
    expected_eeg = [f"EEG{i:03d}" for i in range(1, N_EEG + 1)]
    expected = expected_eeg + [ch for pair in AUX_PAIRS for ch in pair] + ["TRIGGER"]
    rows = {row["name"]: row for row in channel_rows}
    if len(rows) != len(channel_rows) or set(rows) != set(expected):
        raise ValueError("Source channel roles differ from the registered 139-channel layout")
    if len(raw_names) != len(set(raw_names)) or not set(expected).issubset(raw_names):
        raise ValueError("EDF channel names do not match source sidecar")
    for name in expected:
        row = rows[name]
        kind = ("EEG" if name in expected_eeg else "TRIG" if name == "TRIGGER"
                else "EOG" if name.startswith("EOG") else "EMG" if name.startswith("EMG")
                else "MISC")
        if row["type"] != kind or float(row["sampling_frequency"]) != SFREQ:
            raise ValueError("Unexpected source channel type or sample rate")
        if name != "TRIGGER" and row["units"] != "V":
            raise ValueError("Source sidecar does not declare Volts")
    return {
        "eeg": [raw_names.index(name) for name in expected_eeg],
        "aux_pairs": [[raw_names.index(name) for name in pair] for pair in AUX_PAIRS],
        "trigger": raw_names.index("TRIGGER"),
        "bad_eeg_count": sum(rows[name].get("status") == "bad" for name in expected_eeg),
    }


def trial_bounds(trigger, event_onsets, n_samples):
    """Return complete source buffers, action windows, and source timing route.

    Labels are deliberately absent. Continuous event times must agree with the
    corresponding trigger edges. The source NPY converter preserves all 139
    channels, including retained triggers, but creates event times separately
    at i*2880. That exact zero-based grid and matching length select the
    concatenation route regardless of trigger presence. A final incomplete EDF data
    record may have source-exporter edge padding to the next whole second;
    the caller must separately verify those trailing channel values.
    """
    import numpy as np

    trigger = np.asarray(trigger, dtype=np.float64)
    onsets = np.asarray(event_onsets, dtype=np.float64)
    if trigger.shape != (n_samples,) or not np.isfinite(trigger).all():
        raise ValueError("Invalid source trigger signal")
    if onsets.ndim != 1 or not len(onsets) or not np.isfinite(onsets).all():
        raise ValueError("Invalid event onsets")
    samples = np.rint(onsets * SFREQ).astype(np.int64)
    if np.any(np.abs(onsets * SFREQ - samples) > 0.01) or np.any(np.diff(samples) <= 0):
        raise ValueError("Event times are not ordered sample-aligned times")
    edges = np.flatnonzero(np.diff(trigger) > 0.5) + 1
    trailing_padding = 0
    payload_samples = len(samples) * BUFFER_SAMPLES
    padded_samples = math.ceil(payload_samples / SFREQ) * SFREQ
    concatenated_grid = np.array_equal(onsets * SFREQ,
                                       np.arange(len(samples)) * BUFFER_SAMPLES)
    if concatenated_grid:
        if n_samples not in (payload_samples, padded_samples):
            raise ValueError("Concatenated source length does not match complete original trials")
        trailing_padding = n_samples - payload_samples
        starts = samples
        ends = starts + BUFFER_SAMPLES
        route = "source_npy_concatenation"
        extras = 0
    else:
        if not len(edges):
            raise ValueError("Trigger-free recording is not the exact source NPY fallback")
        if len(edges) < len(samples):
            raise ValueError("Fewer source trigger edges than original trials")
        extras = len(edges) - len(samples)
        selected_edges = edges[-len(samples):]
        if not np.array_equal(selected_edges, samples):
            raise ValueError("Source event/trigger timing cannot be reconciled")
        # Exact author extraction: start=(edge//8-359)*8, end=start+2880.
        starts = (selected_edges // 8 - 359) * 8
        ends = starts + BUFFER_SAMPLES
        route = "source_continuous_trigger_buffer"
    # Author dataset rounds total length to 1626 but truncates .1*256 to 25
    # for repetition centers; consequently its last centered sample ends one
    # sample before the original buffer boundary.
    action_starts = ends - (TRIAL_SAMPLES + JITTER_SAMPLES) + CENTER_OFFSET
    if np.any(starts < 0) or np.any(ends > n_samples):
        raise ValueError("Incomplete original trial; refusing source's silent truncation")
    if np.any(action_starts - REPETITION_SAMPLES < starts):
        raise ValueError("Original trial lacks its pre-action comparison")
    return {
        "buffer_starts": starts,
        "buffer_ends": ends,
        "action_starts": action_starts,
        "route": route,
        "extra_leading_triggers": int(extras),
        "trailing_edf_padding_samples": int(trailing_padding),
        "retained_trigger_edges": int(len(edges)),
    }


def _validate_edf_padding(raw, layout, bounds):
    """Inspect only final source sample plus trailing padding; never extract features."""
    import numpy as np

    if bounds["trailing_edf_padding_samples"]:
        picks = layout["eeg"] + [ch for pair in layout["aux_pairs"] for ch in pair]
        tail = raw.get_data(picks=picks + [layout["trigger"]],
                            start=len(bounds["buffer_starts"]) * BUFFER_SAMPLES - 1)
        if not np.isfinite(tail).all() or not np.all(tail == tail[:, :1]):
            raise ValueError("Trailing EDF samples are not source-exporter edge padding")


def _read_onsets_only(events_path):
    """Decode only the first source TSV field; target bytes are not interpreted."""
    onsets = []
    with Path(events_path).open("rb") as stream:
        if stream.readline().partition(b"\t")[0].strip() != b"onset":
            raise ValueError("Source TSV does not have the expected first onset column")
        for line in stream:
            try:
                onset = float(line.partition(b"\t")[0])
            except ValueError:
                raise ValueError("Source onset field is not numeric") from None
            if not math.isfinite(onset):
                raise ValueError("Source onset field is not finite")
            onsets.append(onset)
    return onsets


def preflight_recording_timing(edf_path, events_path, channels_path):
    """Validate one recording's timing using metadata, onsets, trigger and tail.

    No broker, targets, original neural windows, filtering, fitting, prediction,
    or scoring are invoked. Only aggregate timing diagnostics are returned.
    The caller enforces its stage deadline around this bounded preflight.
    """
    import mne

    raw = mne.io.read_raw_edf(str(edf_path), preload=False, verbose=False)
    try:
        if raw.info["sfreq"] != SFREQ:
            raise ValueError("Source EDF sampling rate mismatch")
        layout = channel_layout(_read_tsv(channels_path), raw.ch_names)
        bounds = trial_bounds(raw.get_data(picks=[layout["trigger"]])[0],
                              _read_onsets_only(events_path), raw.n_times)
        _validate_edf_padding(raw, layout, bounds)
        return {"route": bounds["route"], "trials": len(bounds["buffer_starts"]),
                "extra_leading_triggers": bounds["extra_leading_triggers"],
                "retained_trigger_edges": bounds["retained_trigger_edges"],
                "trailing_edf_padding_samples": bounds["trailing_edf_padding_samples"],
                "retained_bad_eeg_channels": layout["bad_eeg_count"],
                "target_fields_read": False}
    finally:
        raw.close()


def broker_event_rows(event_rows, recording_id, role, private_target_path=None):
    """Isolate online values into a scorer-only JSON; return target-free rows.

    Calibration labels may be returned for training. The caller must keep the
    private destination outside tracked code and away from model input paths.
    Existing target files are never overwritten.
    """
    if role not in {"calibration", "online"}:
        raise ValueError("Unknown acquisition role")
    if role == "online" and private_target_path is None:
        raise ValueError("Online labels require a private scorer destination")
    if not event_rows:
        raise ValueError("No original trials")
    timing, labels, ids = [], [], []
    for index, row in enumerate(event_rows):
        label = int(row["value"])
        if label not in range(len(WORDS)) or row["trial_type"] != WORDS[label]:
            raise ValueError("Source word label schema mismatch")
        duration = float(row["duration"])
        if row["session_type"] != role or not math.isfinite(duration) or abs(duration - 6.25) > 1e-6:
            raise ValueError("Unexpected source acquisition role or trial duration")
        onset = float(row["onset"])
        if not math.isfinite(onset):
            raise ValueError("Nonfinite event time")
        ids.append(f"{recording_id}:trial-{index:04d}")
        timing.append(onset)
        labels.append(label)
    result = {"trial_ids": ids, "event_onsets": timing, "role": role}
    if role == "calibration":
        result["calibration_labels"] = labels
    else:
        path = Path(private_target_path)
        payload = json.dumps({"recording_id": recording_id, "trial_ids": ids,
                              "labels": labels}, sort_keys=True).encode("utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(payload)
        result["private_targets_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def source_filter(eeg, auxiliary):
    """Source notch/CAR/FIR recipe on one supplied window, in physical Volts.

    Source EDF conversion already applied 1e-6. Correct the EEG-only preamp
    gain here once. All 128 registered EEG channels remain in the experiment.
    """
    import mne
    import numpy as np

    eeg = np.array(eeg, dtype=np.float64, copy=True) / 10.0
    auxiliary = np.asarray(auxiliary, dtype=np.float64)
    if eeg.shape[0] != N_EEG or auxiliary.shape != (5, eeg.shape[1]):
        raise ValueError("Unexpected numerical channel layout")
    data = np.concatenate((eeg, auxiliary), axis=0)
    if not np.isfinite(data).all():
        raise ValueError("Nonfinite source samples")
    info = mne.create_info([f"EEG{i}" for i in range(N_EEG)] +
                           ["DISPLAY", "MIC", "EOG", "UPPER", "LOWER"],
                           SFREQ, ["eeg"] * N_EEG + ["misc", "misc", "eog", "emg", "emg"])
    raw = mne.io.RawArray(data, info, verbose=False)
    # Source notch omits picks: MNE defaults to EEG data channels, excluding
    # EOG/EMG. The subsequent source bandpass explicitly includes all channels.
    raw.notch_filter([50.0, 100.0], picks=list(range(N_EEG)), filter_length=min(round(6.6 * SFREQ),
                      data.shape[1] - 1), fir_design="firwin", trans_bandwidth=1.5,
                      verbose=False)
    raw.set_eeg_reference("average", verbose=False)
    raw.filter(2.0, 118.0, picks="all", verbose=False)
    filtered = raw.get_data()
    return filtered[:N_EEG], filtered[N_EEG:]


def adaptive_residual(eeg, physiological_auxiliary, seed=20260906):
    """Per-trial source NLMS: z-score ddof=1, mu=.1, eps=.001, random weights."""
    import numpy as np

    data = np.asarray(eeg, dtype=np.float64)
    noise = np.asarray(physiological_auxiliary, dtype=np.float64)
    if data.ndim != 2 or noise.shape != (3, data.shape[1]):
        raise ValueError("Adaptive filter requires the EOG and two lip pairs")
    eps = np.finfo(float).eps
    data = (data - data.mean(axis=1, keepdims=True)) / (data.std(axis=1, ddof=1,
                    keepdims=True) + eps)
    noise = (noise - noise.mean(axis=1, keepdims=True)) / (noise.std(axis=1, ddof=1,
                    keepdims=True) + eps)
    weights = np.random.default_rng(seed).normal(0.0, 0.5, (3, data.shape[0]))
    residual = np.empty_like(data)
    for sample in range(data.shape[1]):
        x = noise[:, sample]
        error = data[:, sample] - x @ weights
        residual[:, sample] = error
        weights += 0.1 / (0.001 + x @ x) * np.outer(x, error)
    if not np.isfinite(residual).all():
        raise ValueError("Nonfinite adaptive-filter output")
    return residual


def average_repetitions(data):
    import numpy as np

    data = np.asarray(data)
    if data.shape[-1] != TRIAL_SAMPLES:
        raise ValueError("Expected exactly five complete 1.25-second repetitions")
    return data.reshape(*data.shape[:-1], 5, REPETITION_SAMPLES).mean(axis=-2)


def extract_recording(edf_path, events_path, channels_path, *, recording_id,
                      role, private_target_path=None, seed=20260906, progress=None):
    """Extract one recording without exposing online targets to downstream code.

    The returned adaptive_trials array retains the 26-sample pre-margin for
    calibration jitter. Evaluation uses the separately returned deterministic
    320-sample averages. Read one source buffer at a time; never preload EDF.
    Optional progress(completed_trials, total_trials) can enforce the caller's
    deadline and memory budget by raising before the next trial is processed.
    """
    import mne
    import numpy as np

    raw = mne.io.read_raw_edf(str(edf_path), preload=False, verbose=False)
    try:
        if raw.info["sfreq"] != SFREQ:
            raise ValueError("Source EDF sampling rate mismatch")
        layout = channel_layout(_read_tsv(channels_path), raw.ch_names)
        broker = broker_event_rows(_read_tsv(events_path), recording_id, role,
                                   private_target_path)
        bounds = trial_bounds(raw.get_data(picks=[layout["trigger"]])[0],
                              broker["event_onsets"], raw.n_times)
        n = len(broker["trial_ids"])
        eeg_raw = np.empty((n, N_EEG, REPETITION_SAMPLES), dtype="float32")
        eeg_adaptive = np.empty_like(eeg_raw)
        eeg_preaction = np.empty_like(eeg_raw)
        adaptive_trials = np.empty((n, N_EEG, TRIAL_SAMPLES + JITTER_SAMPLES),
                                   dtype="float32") if role == "calibration" else None
        nuisance_full = np.empty((n, 5, TRIAL_SAMPLES), dtype="float32")
        timing = np.empty((n, 2), dtype="float64")
        picks = layout["eeg"] + [ch for pair in layout["aux_pairs"] for ch in pair]
        _validate_edf_padding(raw, layout, bounds)
        for index, (start, end, action_start) in enumerate(zip(bounds["buffer_starts"],
                                  bounds["buffer_ends"], bounds["action_starts"])):
            if progress is not None:
                progress(index, n)
            buffer = raw.get_data(picks=picks, start=int(start), stop=int(end))
            aux = buffer[N_EEG::2] - buffer[N_EEG + 1::2]
            # Main source trial plus its pre-margin. No cross-trial filter state.
            eeg_f, aux_f = source_filter(buffer[:N_EEG, -(TRIAL_SAMPLES + JITTER_SAMPLES):],
                                        aux[:, -(TRIAL_SAMPLES + JITTER_SAMPLES):])
            residual = adaptive_residual(eeg_f, aux_f[2:], seed)
            centered = slice(CENTER_OFFSET, CENTER_OFFSET + TRIAL_SAMPLES)
            eeg_raw[index] = average_repetitions(eeg_f[:, centered])
            eeg_adaptive[index] = average_repetitions(residual[:, centered])
            if adaptive_trials is not None:
                adaptive_trials[index] = residual
            # This prefix stops before action; zero-phase FIR cannot see action.
            prefix_length = int(action_start - start)
            pre_eeg, pre_aux = source_filter(buffer[:N_EEG, :prefix_length],
                                            aux[:, :prefix_length])
            pre_residual = adaptive_residual(pre_eeg, pre_aux[2:], seed)
            eeg_preaction[index] = pre_residual[:, -REPETITION_SAMPLES:]
            nuisance_full[index] = aux_f[:, centered]
            timing[index] = [index, float(action_start) / SFREQ]
        if progress is not None:
            progress(n, n)
        result = {**broker, "eeg_raw": eeg_raw, "eeg_adaptive": eeg_adaptive,
                  "eeg_preaction": eeg_preaction,
                  "nuisance_averaged": average_repetitions(nuisance_full),
                  "nuisance_full": nuisance_full, "timing": timing,
                  "action_start_samples": bounds["action_starts"],
                  "timing_summary": {"route": bounds["route"], "trials": n,
                      "extra_leading_triggers": bounds["extra_leading_triggers"],
                      "trailing_edf_padding_samples": bounds["trailing_edf_padding_samples"],
                      "retained_bad_eeg_channels": layout["bad_eeg_count"]}}
        if adaptive_trials is not None:
            result["adaptive_trials"] = adaptive_trials
        return result
    finally:
        raw.close()
