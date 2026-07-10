"""Streaming BrainVision/MAT extraction for the task-compatible EEG bridge."""

from __future__ import annotations

import math
import re
import statistics
import time
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.cache.npz_cache import load_npz_cache, save_npz_cache


@dataclass(frozen=True)
class RawTriggerEvent:
    """One numeric trigger from a BrainVision annotation."""

    source_index: int
    time_sec: float
    trigger: int


@dataclass(frozen=True)
class MatTriggerEvent:
    """One ordered perception or key-press trigger from the behavioral log."""

    source_index: int
    time_sec: float
    trigger: int
    kind: str
    trial_index: int
    label: str | None


@dataclass(frozen=True)
class TriggerMatch:
    """One exact trigger-code match across raw and MAT clocks."""

    raw_index: int
    mat_index: int


@dataclass(frozen=True)
class TriggerAlignment:
    """Strict ordered trigger alignment plus timing residual evidence."""

    matches: tuple[TriggerMatch, ...]
    unmatched_raw_indices: tuple[int, ...]
    clock_offset_sec: float
    median_abs_residual_sec: float
    p99_abs_residual_sec: float
    max_abs_residual_sec: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy": "greedy_exact_trigger_subsequence_with_timing_audit",
            "n_matches": len(self.matches),
            "unmatched_raw_indices": list(self.unmatched_raw_indices),
            "clock_offset_sec": self.clock_offset_sec,
            "median_abs_residual_sec": self.median_abs_residual_sec,
            "p99_abs_residual_sec": self.p99_abs_residual_sec,
            "max_abs_residual_sec": self.max_abs_residual_sec,
        }


@dataclass(frozen=True)
class EEGExtractionSummary:
    """Resource and alignment summary for one EEG event-window cache."""

    raw_path: str
    events_path: str
    out_path: str
    original_sfreq: float
    output_sfreq: float
    raw_duration_sec: float
    raw_channels: int
    selected_channels: int
    raw_annotation_triggers: int
    mat_triggers: int
    aligned_triggers: int
    aligned_key_events: int
    output_events: int
    output_shape: tuple[int, int, int]
    dropped_by_reason: dict[str, int]
    alignment: dict[str, Any]
    raw_preloaded: bool
    runtime_sec: float
    output_bytes: int
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def align_trigger_sequences(
    raw_events: Iterable[RawTriggerEvent],
    mat_events: Iterable[MatTriggerEvent],
    *,
    max_abs_residual_sec: float = 0.05,
) -> TriggerAlignment:
    """Match every MAT trigger to an ordered raw trigger and audit both clocks."""

    raw_rows = list(raw_events)
    mat_rows = list(mat_events)
    if not raw_rows or not mat_rows:
        raise ValueError("trigger alignment requires nonempty raw and MAT events")
    if max_abs_residual_sec <= 0:
        raise ValueError("max_abs_residual_sec must be positive")

    cursor = 0
    matches: list[TriggerMatch] = []
    for mat_index, mat_event in enumerate(mat_rows):
        while cursor < len(raw_rows) and raw_rows[cursor].trigger != mat_event.trigger:
            cursor += 1
        if cursor >= len(raw_rows):
            raise ValueError(
                "raw trigger sequence cannot cover MAT trigger "
                f"{mat_index} with code {mat_event.trigger}"
            )
        matches.append(TriggerMatch(raw_index=cursor, mat_index=mat_index))
        cursor += 1

    matched_raw = {match.raw_index for match in matches}
    unmatched = tuple(index for index in range(len(raw_rows)) if index not in matched_raw)
    offsets = [
        raw_rows[match.raw_index].time_sec - mat_rows[match.mat_index].time_sec
        for match in matches
    ]
    clock_offset = float(statistics.median(offsets))
    residuals = sorted(abs(value - clock_offset) for value in offsets)
    maximum = float(residuals[-1])
    if maximum > max_abs_residual_sec:
        raise ValueError(
            f"trigger timing residual {maximum:.6f} sec exceeds "
            f"{max_abs_residual_sec:.6f} sec"
        )
    return TriggerAlignment(
        matches=tuple(matches),
        unmatched_raw_indices=unmatched,
        clock_offset_sec=clock_offset,
        median_abs_residual_sec=float(statistics.median(residuals)),
        p99_abs_residual_sec=float(_percentile(residuals, 0.99)),
        max_abs_residual_sec=maximum,
    )


def label_for_keycode(keycode: int) -> str | None:
    """Map the key labels used by the existing B2Q-mini event cache."""

    value = int(keycode)
    if 65 <= value <= 90:
        return chr(value)
    if 97 <= value <= 122:
        return chr(value).upper()
    if value == 32:
        return "SPACE"
    if value == 13:
        return "ENTER"
    return None


def extract_brainvision_mat_windows(
    *,
    raw_path: str | Path,
    events_path: str | Path,
    out_path: str | Path,
    sfreq: float = 50.0,
    tmin: float = -0.2,
    tmax: float = 0.3,
    max_events: int | None = None,
    max_channels: int | None = None,
    max_alignment_residual_sec: float = 0.05,
    max_output_mb: float = 64.0,
    overwrite: bool = False,
) -> EEGExtractionSummary:
    """Build one bounded EEG key-event cache by streaming raw windows."""

    mne, loadmat, np, resample_poly = _require_neuro_dependencies()
    if sfreq <= 0 or tmax <= tmin:
        raise ValueError("sfreq must be positive and tmax must exceed tmin")
    if max_events is not None and max_events < 1:
        raise ValueError("max_events must be positive when provided")
    if max_channels is not None and max_channels < 1:
        raise ValueError("max_channels must be positive when provided")
    if max_output_mb <= 0:
        raise ValueError("max_output_mb must be positive")

    raw_file = Path(raw_path)
    events_file = Path(events_path)
    output_file = Path(out_path)
    if raw_file.suffix.lower() != ".vhdr":
        raise ValueError("raw_path must point to a BrainVision .vhdr file")
    if not raw_file.is_file() or not events_file.is_file():
        raise FileNotFoundError("BrainVision header and MAT log must both exist")
    for extension in (".eeg", ".vmrk"):
        companion = raw_file.with_suffix(extension)
        if not companion.is_file():
            raise FileNotFoundError(f"missing BrainVision companion: {companion}")
    if output_file.exists() and not overwrite:
        raise FileExistsError(f"output cache already exists: {output_file}")

    started = time.perf_counter()
    raw = mne.io.read_raw_brainvision(raw_file, preload=False, verbose=False)
    raw_preloaded = bool(raw.preload)
    original_sfreq = float(raw.info["sfreq"])
    raw_duration_sec = float(raw.n_times / original_sfreq)
    raw_channel_count = len(raw.ch_names)
    all_channel_names = list(raw.ch_names)
    selected_names = [name for name in all_channel_names if "EOG" not in name.upper()]
    if max_channels is not None:
        selected_names = selected_names[:max_channels]
    excluded_names = [name for name in all_channel_names if name not in selected_names]
    raw.pick(selected_names)

    raw_triggers = _raw_annotation_triggers(raw)
    mat_triggers = _mat_trigger_events(events_file, loadmat=loadmat, np=np)
    alignment = align_trigger_sequences(
        raw_triggers,
        mat_triggers,
        max_abs_residual_sec=max_alignment_residual_sec,
    )
    aligned_key_rows = []
    dropped_by_reason: dict[str, int] = {}
    for match in alignment.matches:
        mat_event = mat_triggers[match.mat_index]
        if mat_event.kind != "key":
            continue
        if mat_event.label is None:
            dropped_by_reason["unsupported_keycode"] = (
                dropped_by_reason.get("unsupported_keycode", 0) + 1
            )
            continue
        aligned_key_rows.append((raw_triggers[match.raw_index], mat_event))
    if max_events is not None and len(aligned_key_rows) > max_events:
        dropped_by_reason["max_events_cap"] = len(aligned_key_rows) - max_events
        aligned_key_rows = aligned_key_rows[:max_events]

    output_n_times = int(round((tmax - tmin) * sfreq))
    estimated_uncompressed_bytes = (
        len(aligned_key_rows) * len(selected_names) * output_n_times * 4
    )
    max_output_bytes = int(max_output_mb * 1024 * 1024)
    if estimated_uncompressed_bytes > max_output_bytes:
        raise ValueError(
            f"planned float32 windows need {estimated_uncompressed_bytes} bytes before "
            f"compression; cap is {max_output_bytes}"
        )

    ratio = Fraction(float(sfreq) / original_sfreq).limit_denominator(1000)
    effective_sfreq = original_sfreq * ratio.numerator / ratio.denominator
    if not math.isclose(effective_sfreq, sfreq, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("requested sfreq cannot be represented by bounded rational resampling")

    windows = []
    labels = []
    event_times = []
    event_source_indices = []
    trial_indices = []
    for raw_event, mat_event in aligned_key_rows:
        start = int(round((raw_event.time_sec + tmin) * original_sfreq))
        stop = int(round((raw_event.time_sec + tmax) * original_sfreq))
        if start < 0:
            dropped_by_reason["before_start"] = dropped_by_reason.get("before_start", 0) + 1
            continue
        if stop > raw.n_times:
            dropped_by_reason["after_end"] = dropped_by_reason.get("after_end", 0) + 1
            continue
        window = raw.get_data(start=start, stop=stop)
        window = resample_poly(
            window,
            up=ratio.numerator,
            down=ratio.denominator,
            axis=1,
        )
        if window.shape[1] != output_n_times:
            raise ValueError(
                f"resampled window has {window.shape[1]} samples; expected {output_n_times}"
            )
        windows.append(window.astype("float32", copy=False))
        labels.append(mat_event.label)
        event_times.append(raw_event.time_sec)
        event_source_indices.append(raw_event.source_index)
        trial_indices.append(mat_event.trial_index)
    if not windows:
        raise ValueError("no aligned EEG key events remained after window bounds")
    window_array = np.stack(windows, axis=0)

    metadata = {
        "kind": "real_brainvision_mat_windows",
        "modality": "EEG",
        "subject": _subject_from_name(raw_file.name),
        "session": _session_from_name(raw_file.name),
        "block": _block_from_name(raw_file.name),
        "source_files": {
            "raw_header": str(raw_file),
            "raw_data": str(raw_file.with_suffix(".eeg")),
            "raw_markers": str(raw_file.with_suffix(".vmrk")),
            "events": str(events_file),
        },
        "raw": {
            "format": "BrainVision",
            "original_sfreq": original_sfreq,
            "duration_sec": raw_duration_sec,
            "n_channels": raw_channel_count,
            "preload": raw_preloaded,
            "annotation_trigger_count": len(raw_triggers),
        },
        "channels": {
            "selected_names": selected_names,
            "excluded_names": excluded_names,
            "eog_name_rule": "exclude channel names containing EOG",
        },
        "events": {
            "mat_trigger_count": len(mat_triggers),
            "alignment": alignment.to_dict(),
            "aligned_key_events_before_label_filter": sum(
                1 for event in mat_triggers if event.kind == "key"
            ),
            "output_key_events": len(window_array),
            "label_source": "MAT key press Keycode aligned to raw annotation trigger code",
            "direct_mat_timestamps_used": False,
        },
        "extraction_params": {
            "sfreq": sfreq,
            "tmin": tmin,
            "tmax": tmax,
            "streamed_window_reads": True,
            "max_events": max_events,
            "max_channels": max_channels,
            "max_alignment_residual_sec": max_alignment_residual_sec,
        },
        "transformations": [
            {
                "name": "mne_read_raw_brainvision",
                "description": "Opened one complete BrainVision triplet with preload=False.",
            },
            {
                "name": "annotation_mat_trigger_alignment",
                "description": (
                    "Matched every ordered MAT trigger code to raw BrainVision annotations "
                    "and audited the independent clocks."
                ),
                "params": alignment.to_dict(),
            },
            {
                "name": "streamed_event_window_extraction",
                "description": (
                    "Read one bounded raw window at a time and polyphase-resampled it."
                ),
                "params": {
                    "original_sfreq": original_sfreq,
                    "target_sfreq": sfreq,
                    "tmin": tmin,
                    "tmax": tmax,
                },
            },
        ],
        "warnings": [
            "real_eeg_typed_sentence_production_task",
            "direct_mat_clock_not_used",
            "eog_named_channels_excluded",
            "minimally_processed_no_filter_or_artifact_rejection",
            "event_windows_are_keystroke_aligned_not_v2_continuous_decoding",
            "eeg_result_does_not_establish_consumer_or_at_home_hardware_readiness",
            "not_arbitrary_thought_decoding",
        ],
    }
    save_npz_cache(
        output_file,
        windows=window_array,
        labels=np.asarray(labels, dtype="U5"),
        metadata=metadata,
        extra_arrays={
            "event_start_sec": np.asarray(event_times, dtype="float64"),
            "event_source_index": np.asarray(event_source_indices, dtype="int32"),
            "trial_indices": np.asarray(trial_indices, dtype="int32"),
            "channel_names": np.asarray(selected_names, dtype="U16"),
        },
    )
    cache = load_npz_cache(output_file)
    runtime_sec = round(time.perf_counter() - started, 6)
    return EEGExtractionSummary(
        raw_path=str(raw_file),
        events_path=str(events_file),
        out_path=str(output_file),
        original_sfreq=original_sfreq,
        output_sfreq=float(sfreq),
        raw_duration_sec=raw_duration_sec,
        raw_channels=raw_channel_count,
        selected_channels=len(selected_names),
        raw_annotation_triggers=len(raw_triggers),
        mat_triggers=len(mat_triggers),
        aligned_triggers=len(alignment.matches),
        aligned_key_events=sum(1 for event in mat_triggers if event.kind == "key"),
        output_events=cache.summary.n_events,
        output_shape=cache.summary.windows_shape,
        dropped_by_reason=dropped_by_reason,
        alignment=alignment.to_dict(),
        raw_preloaded=raw_preloaded,
        runtime_sec=runtime_sec,
        output_bytes=output_file.stat().st_size,
        warnings=list(metadata["warnings"]),
    )


def _raw_annotation_triggers(raw: Any) -> list[RawTriggerEvent]:
    rows = []
    for source_index, annotation in enumerate(raw.annotations):
        description = str(annotation["description"])
        match = re.fullmatch(r"Stimulus/S\s*(\d+)", description)
        if match is not None:
            rows.append(
                RawTriggerEvent(
                    source_index=source_index,
                    time_sec=float(annotation["onset"]),
                    trigger=int(match.group(1)),
                )
            )
    if not rows:
        raise ValueError("BrainVision recording contains no Stimulus/S annotations")
    return rows


def _mat_trigger_events(path: Path, *, loadmat: Any, np: Any) -> list[MatTriggerEvent]:
    payload = loadmat(path, squeeze_me=True, struct_as_record=False)
    pr_trials = payload.get("pr_trials")
    if pr_trials is None or not hasattr(pr_trials, "key") or not hasattr(pr_trials, "rsvp"):
        raise ValueError("MAT log is missing pr_trials.key or pr_trials.rsvp")
    rows: list[tuple[float, int, str, int, str | None]] = []
    for trial_index, (keys, rsvp) in enumerate(zip(pr_trials.key, pr_trials.rsvp)):
        for item in np.atleast_1d(rsvp):
            rows.append((float(item.t), 10, "rsvp", trial_index, None))
        for item in np.atleast_1d(keys):
            if int(item.Pressed) != 1:
                continue
            keycode = int(item.Keycode)
            rows.append(
                (
                    float(item.Time),
                    keycode,
                    "key",
                    trial_index,
                    label_for_keycode(keycode),
                )
            )
    rows.sort(key=lambda item: item[0])
    return [
        MatTriggerEvent(
            source_index=index,
            time_sec=time_sec,
            trigger=trigger,
            kind=kind,
            trial_index=trial_index,
            label=label,
        )
        for index, (time_sec, trigger, kind, trial_index, label) in enumerate(rows)
    ]


def _require_neuro_dependencies():
    try:
        import mne
        import numpy as np
        from scipy.io import loadmat
        from scipy.signal import resample_poly
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "BrainVision extraction requires `pip install -e '.[neuro]'`."
        ) from exc
    return mne, loadmat, np, resample_poly


def _percentile(values: list[float], quantile: float) -> float:
    if not values:
        raise ValueError("percentile requires values")
    position = quantile * (len(values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(values[lower])
    fraction = position - lower
    return float(values[lower] * (1 - fraction) + values[upper] * fraction)


def _subject_from_name(name: str) -> str | None:
    match = re.match(r"0*(\d+)_DECOMEG_", name, flags=re.I)
    return f"S{int(match.group(1))}" if match else None


def _session_from_name(name: str) -> str | None:
    match = re.search(r"_S(\d+)(?:bis)?_", name, flags=re.I)
    return str(int(match.group(1))) if match else None


def _block_from_name(name: str) -> str | None:
    match = re.search(r"_task(\d+)", name, flags=re.I)
    return f"block{int(match.group(1))}" if match else None
