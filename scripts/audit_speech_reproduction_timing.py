"""Read-only, label-blind timing audit of the existing SPEECH-REPRO-1 source.

Read only the event TSV's first (onset) column and EDF TRIGGER channel. No
decoder, EEG features, target broker, training, prediction or scoring runs.
Print aggregate timing evidence, not event rows or word values. The optional
output path must be new; source files and failed-run markers are never edited.
"""

import argparse
import hashlib
import json
from pathlib import Path


def digest(path, git_blob=False):
    result = hashlib.sha1() if git_blob else hashlib.sha256()
    if git_blob:
        result.update(f"blob {path.stat().st_size}\0".encode())
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def audit_recording(root, item):
    import mne
    import numpy as np

    signal = root / item["path"]
    events = root / item["events_path"]
    if signal.stat().st_size != item["signal_bytes"] or digest(signal) != item["signal_sha256"]:
        raise ValueError("Pinned signal identity changed")
    if events.stat().st_size != item["events_bytes"] or digest(events, True) != item["events_git_blob_sha"]:
        raise ValueError("Pinned event identity changed")
    with events.open(encoding="utf-8-sig") as stream:
        if stream.readline().split("\t", 1)[0] != "onset":
            raise ValueError("Expected onset as first TSV column; refuse other fields")
        # Discard the suffix without parsing or using any label-bearing field.
        onsets = np.asarray([float(line.partition("\t")[0]) for line in stream])
    raw = mne.io.read_raw_edf(str(signal), include=["TRIGGER"], preload=False, verbose=False)
    try:
        if raw.ch_names != ["TRIGGER"] or raw.info["sfreq"] != 256:
            raise ValueError("Unexpected trigger channel or sample rate")
        trigger = raw.get_data()[0]
        n_samples = raw.n_times
    finally:
        raw.close()
    if not len(onsets) or not np.isfinite(onsets).all() or not np.isfinite(trigger).all():
        raise ValueError("Empty or nonfinite timing inputs")
    samples = np.rint(onsets * 256).astype(np.int64)
    if np.any(np.abs(onsets * 256 - samples) > 0.01) or np.any(np.diff(samples) <= 0):
        raise ValueError("Event onsets are not strictly increasing sample times")
    edges = np.flatnonzero(np.diff(trigger) > 0.5) + 1
    selected = edges[-len(samples):]
    comparable = len(selected) == len(samples)
    difference = samples - selected if comparable else None
    payload = len(samples) * 2880
    whole_seconds = ((payload + 255) // 256) * 256
    fixed_grid = bool(np.array_equal(samples, np.arange(len(samples)) * 2880))
    matching_length = n_samples in (payload, whole_seconds)
    if fixed_grid and matching_length:
        route = "source_npy_concatenation"
        starts = samples
        ends = starts + 2880
    elif comparable and np.array_equal(samples, selected):
        route = "source_continuous_trigger_buffer"
        starts = (selected // 8 - 359) * 8
        ends = starts + 2880
    else:
        route = "unresolved"
        starts = ends = np.asarray([], dtype=np.int64)
    padding = n_samples - payload if fixed_grid and matching_length else 0
    return {
        "recording_id": signal.name.removesuffix("_eeg.edf"),
        "signal_sha256_matches_manifest": True, "events_git_blob_matches_manifest": True,
        "event_count": int(len(samples)), "trigger_rise_count": int(len(edges)),
        "edf_samples": int(n_samples), "first_event_sample": int(samples[0]),
        "last_event_sample": int(samples[-1]),
        "exact_2880_sample_onset_grid": fixed_grid,
        "matches_concatenated_length_or_edf_padding": bool(matching_length),
        "event_rise_matches": int(np.sum(samples == selected)) if comparable else None,
        "event_minus_selected_rise_min_samples": int(difference.min()) if comparable else None,
        "event_minus_selected_rise_max_samples": int(difference.max()) if comparable else None,
        "source_supported_timing_route": route,
        "all_original_buffers_in_bounds": bool(len(starts) == len(samples)
            and np.all(starts >= 0) and np.all(ends <= n_samples)),
        "trailing_edf_padding_samples": int(padding),
        "trigger_padding_is_edge_repetition": bool(np.all(trigger[payload:] == trigger[payload - 1]))
            if padding else None,
        "current_reader_would_reject_retained_trigger_fallback": bool(
            route == "source_npy_concatenation" and len(edges) and
            not (comparable and np.array_equal(samples, selected))),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    manifest = json.loads((repo / "registries/speech_reproduction_source_manifest.v0.json").read_text())
    root = repo / "data/speech_repro_1_20260921/source"
    report = {
        "experiment_id": "SPEECH-REPRO-1", "audit_only": True,
        "source_commit": manifest["source_commit"],
        "source_event_fields_used": ["onset"], "signal_channels_read": ["TRIGGER"],
        "label_fields_parsed": False, "models_trained": 0, "scoring_invocations": 0,
        "recordings": [audit_recording(root, item) for item in manifest["files"]],
    }
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text)
    print(text)


if __name__ == "__main__":
    main()
