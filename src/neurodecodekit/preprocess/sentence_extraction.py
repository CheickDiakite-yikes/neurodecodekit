"""Continuous sentence extraction for the resource-bounded CTC loop."""

from __future__ import annotations

import hashlib
import math
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Mapping

from neurodecodekit.cache.sentence_npz import save_sentence_npz_cache
from neurodecodekit.evaluation.split_protocol import build_sentence_text_membership
from neurodecodekit.preprocess.ctc_text import encode_ctc_text
from neurodecodekit.preprocess.fif_mat_extraction import (
    _apply_channel_picks,
    require_neuro_dependencies,
    stim_key_event_rows,
)
from neurodecodekit.preprocess.sequence_alignment import (
    KeySequence,
    TargetSequence,
    build_mat_trial_index_map,
    group_key_event_times_into_sequences,
    group_key_labels_into_sequences,
    load_mat_key_trigger_time_sequences,
    load_mat_sequence_sources,
    summarize_key_trigger_timing,
)


@dataclass(frozen=True)
class SentenceRecord:
    """One aligned trial and its continuous extraction boundary."""

    trial_index: int
    typed_text: str
    reference_text: str
    mat_response_text: str
    start_sec: float
    end_sec: float


@dataclass(frozen=True)
class SentenceExtractionSummary:
    """Resource and shape report for one sentence-cache extraction."""

    raw_path: str
    events_path: str
    out_path: str
    n_candidate_key_events: int
    n_key_events_after_sweep: int
    n_sentences: int
    n_channels: int
    max_timepoints: int
    total_valid_timepoints: int
    min_input_length: int
    max_input_length: int
    min_target_length: int
    max_target_length: int
    sfreq: float
    output_bytes: int
    runtime_sec: float
    peak_rss_bytes: int | None
    channel_names: list[str]
    scaler_fit_scope: str
    split_partition_counts: dict[str, int] | None
    split_protocol_config_sha256: str | None
    semantic_membership_sha256: str | None
    trial_index_mapping_strategy: str
    skipped_mat_trial_indices: list[int]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def build_sentence_records(
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    response_sequences: list[TargetSequence],
    *,
    pre_context_sec: float,
    post_context_sec: float,
    raw_duration_sec: float,
    trial_index_map: list[int] | tuple[int, ...] | None = None,
    max_sentences: int | None = None,
) -> list[SentenceRecord]:
    """Pair strict trial-order text rows with first-key-through-ENTER boundaries."""

    if pre_context_sec < 0 or post_context_sec < 0:
        raise ValueError("sentence context durations must be >= 0")
    if raw_duration_sec <= 0:
        raise ValueError("raw_duration_sec must be > 0")
    if max_sentences is not None and max_sentences < 1:
        raise ValueError("max_sentences must be >= 1 when provided")
    if trial_index_map is None:
        if len(key_sequences) != len(target_sequences):
            raise ValueError(
                "Strict sentence extraction requires equal key and MAT target trial counts "
                "when no trial map is supplied: "
                f"{len(key_sequences)} vs {len(target_sequences)}."
            )
        mapped_trial_indices = [sequence.index for sequence in key_sequences]
    else:
        mapped_trial_indices = [int(value) for value in trial_index_map]
        if len(mapped_trial_indices) != len(key_sequences):
            raise ValueError("trial_index_map must contain one MAT index per key sequence.")
        if len(set(mapped_trial_indices)) != len(mapped_trial_indices):
            raise ValueError("trial_index_map values must be unique.")
        if any(
            left >= right for left, right in zip(mapped_trial_indices, mapped_trial_indices[1:])
        ):
            raise ValueError("trial_index_map values must be strictly increasing.")

    targets_by_index = {sequence.index: sequence for sequence in target_sequences}
    responses_by_index = {sequence.index: sequence for sequence in response_sequences}
    records: list[SentenceRecord] = []
    for sequence, mat_trial_index in zip(
        key_sequences,
        mapped_trial_indices,
        strict=True,
    ):
        target = targets_by_index.get(mat_trial_index)
        if target is None:
            raise ValueError(f"MAT target is missing mapped trial index {mat_trial_index}.")
        if sequence.start_sec is None or sequence.end_sec is None:
            raise ValueError(f"Key sequence {sequence.index} is missing timing boundaries.")
        start_sec = max(0.0, float(sequence.start_sec) - pre_context_sec)
        end_sec = min(raw_duration_sec, float(sequence.end_sec) + post_context_sec)
        if end_sec <= start_sec:
            raise ValueError(f"Key sequence {sequence.index} has an empty sentence boundary.")
        response = responses_by_index.get(mat_trial_index)
        records.append(
            SentenceRecord(
                trial_index=mat_trial_index,
                typed_text=sequence.text,
                reference_text=target.text,
                mat_response_text=response.text if response is not None else "",
                start_sec=start_sec,
                end_sec=end_sec,
            )
        )
    if max_sentences is not None:
        records = records[:max_sentences]
    return records


def extract_padded_sentence_arrays(signal, *, sfreq: float, records: list[SentenceRecord]):
    """Slice and zero-pad continuous [channels, time] signal by sentence boundary."""

    np = _require_numpy()
    data = np.asarray(signal)
    if data.ndim != 2:
        raise ValueError(f"signal must be [channels, timepoints], got {data.shape}")
    if sfreq <= 0:
        raise ValueError("sfreq must be > 0")
    if not records:
        raise ValueError("at least one sentence record is required")

    sample_ranges: list[tuple[int, int]] = []
    for record in records:
        start = max(0, int(math.floor(record.start_sec * sfreq)))
        stop = min(data.shape[1], int(math.ceil(record.end_sec * sfreq)))
        if stop <= start:
            raise ValueError(f"trial {record.trial_index} is outside the signal bounds")
        sample_ranges.append((start, stop))
    input_lengths = np.asarray([stop - start for start, stop in sample_ranges], dtype="int32")
    max_timepoints = int(input_lengths.max())
    signals = np.zeros((len(records), data.shape[0], max_timepoints), dtype="float32")
    starts = np.zeros(len(records), dtype="float64")
    ends = np.zeros(len(records), dtype="float64")
    for row_index, (start, stop) in enumerate(sample_ranges):
        length = stop - start
        signals[row_index, :, :length] = data[:, start:stop]
        starts[row_index] = start / sfreq
        ends[row_index] = stop / sfreq

    encoded = [encode_ctc_text(record.typed_text) for record in records]
    target_lengths = np.asarray([len(values) for values in encoded], dtype="int32")
    target_token_ids = np.zeros((len(records), int(target_lengths.max())), dtype="int16")
    for row_index, values in enumerate(encoded):
        target_token_ids[row_index, : len(values)] = values

    return {
        "signals": signals,
        "input_lengths": input_lengths,
        "target_token_ids": target_token_ids,
        "target_lengths": target_lengths,
        "target_texts": np.asarray([record.typed_text for record in records], dtype="U"),
        "reference_texts": np.asarray([record.reference_text for record in records], dtype="U"),
        "mat_response_texts": np.asarray(
            [record.mat_response_text for record in records], dtype="U"
        ),
        "trial_indices": np.asarray([record.trial_index for record in records], dtype="int32"),
        "sentence_start_sec": starts,
        "sentence_end_sec": ends,
    }


def robust_scale_channels(signal, *, clamp: float | None = 5.0):
    """Apply per-channel median/IQR scaling without a scikit-learn dependency."""

    np = _require_numpy()
    data = np.asarray(signal, dtype="float32")
    if data.ndim != 2:
        raise ValueError(f"signal must be [channels, timepoints], got {data.shape}")
    if clamp is not None and clamp <= 0:
        raise ValueError("clamp must be > 0 when provided")
    median = np.median(data, axis=1, keepdims=True).astype("float32")
    q25, q75 = np.percentile(data, [25, 75], axis=1, keepdims=True).astype("float32")
    scale = q75 - q25
    zero_iqr = scale == 0
    scale[zero_iqr] = 1.0
    scaled = (data - median) / scale
    if clamp is not None:
        np.clip(scaled, -float(clamp), float(clamp), out=scaled)
    return scaled.astype("float32", copy=False), int(zero_iqr.sum())


def fit_robust_scaler_from_padded(
    signals,
    input_lengths,
    *,
    fit_indices: list[int],
):
    """Fit per-channel median/IQR using only valid samples from selected rows."""

    np = _require_numpy()
    data = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if data.ndim != 3:
        raise ValueError(f"signals must be [sentences, channels, timepoints], got {data.shape}")
    if lengths.ndim != 1 or len(lengths) != data.shape[0]:
        raise ValueError("input_lengths must contain one value per sentence row")
    indices = [int(value) for value in fit_indices]
    if not indices:
        raise ValueError("fit_indices must contain at least one train row")
    if len(set(indices)) != len(indices):
        raise ValueError("fit_indices must be unique")
    if any(index < 0 or index >= data.shape[0] for index in indices):
        raise ValueError("fit_indices contain a row outside the signal array")
    if (lengths < 1).any() or (lengths > data.shape[2]).any():
        raise ValueError("input_lengths are outside the padded signal width")

    valid_segments = [data[index, :, : int(lengths[index])] for index in indices]
    fit_data = np.concatenate(valid_segments, axis=1)
    center = np.median(fit_data, axis=1).astype("float32")
    q25, q75 = np.percentile(fit_data, [25, 75], axis=1).astype("float32")
    scale = (q75 - q25).astype("float32")
    zero_iqr = scale == 0
    scale[zero_iqr] = 1.0
    return (
        center,
        scale,
        {
            "n_fit_rows": len(indices),
            "n_fit_valid_timepoints": int(sum(int(lengths[index]) for index in indices)),
            "zero_iqr_channels": int(zero_iqr.sum()),
        },
    )


def apply_robust_scaler_to_padded(
    signals,
    input_lengths,
    *,
    center,
    scale,
    clamp: float | None = 5.0,
):
    """Apply frozen channel statistics while preserving exact zero padding."""

    np = _require_numpy()
    data = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    center_values = np.asarray(center, dtype="float32")
    scale_values = np.asarray(scale, dtype="float32")
    if data.ndim != 3:
        raise ValueError(f"signals must be [sentences, channels, timepoints], got {data.shape}")
    if lengths.ndim != 1 or len(lengths) != data.shape[0]:
        raise ValueError("input_lengths must contain one value per sentence row")
    if center_values.shape != (data.shape[1],) or scale_values.shape != (data.shape[1],):
        raise ValueError("center and scale must contain one value per channel")
    if not np.isfinite(center_values).all() or not np.isfinite(scale_values).all():
        raise ValueError("center and scale must be finite")
    if (scale_values <= 0).any():
        raise ValueError("scale values must be positive")
    if clamp is not None and clamp <= 0:
        raise ValueError("clamp must be > 0 when provided")

    output = np.zeros_like(data, dtype="float32")
    for row_index, length_value in enumerate(lengths):
        length = int(length_value)
        if length < 1 or length > data.shape[2]:
            raise ValueError("input_lengths are outside the padded signal width")
        valid = (data[row_index, :, :length] - center_values[:, None]) / scale_values[:, None]
        if clamp is not None:
            np.clip(valid, -float(clamp), float(clamp), out=valid)
        output[row_index, :, :length] = valid
    return output


def describe_raw_channels(raw) -> list[dict[str, object]]:
    """Return JSON-safe channel type and device-coordinate provenance."""

    channel_names = [str(name) for name in raw.ch_names]
    channel_types = [str(value) for value in raw.get_channel_types()]
    channel_info = list(raw.info["chs"])
    if not (len(channel_names) == len(channel_types) == len(channel_info)):
        raise ValueError("Raw channel names, types, and info rows must have equal lengths.")

    rows: list[dict[str, object]] = []
    for name, channel_type, info in zip(
        channel_names,
        channel_types,
        channel_info,
        strict=True,
    ):
        loc = info.get("loc")
        position = None
        if loc is not None and len(loc) >= 3:
            values = [float(value) for value in loc[:3]]
            if all(math.isfinite(value) for value in values):
                position = values
        rows.append(
            {
                "name": name,
                "type": channel_type,
                "position_m": position,
                "coord_frame": _optional_int(info.get("coord_frame")),
                "coil_type": _optional_int(info.get("coil_type")),
                "unit": _optional_int(info.get("unit")),
            }
        )
    return rows


def extract_fif_mat_sentence_cache(
    *,
    raw_path: str | Path,
    events_path: str | Path,
    out_path: str | Path,
    sfreq: float = 100.0,
    pre_context_sec: float = 0.4,
    post_context_sec: float = 0.45,
    picks: str | None = "meg",
    max_channels: int | None = 16,
    stim_channel: str = "STI101",
    l_freq: float | None = 0.5,
    h_freq: float | None = 45.0,
    notch_freq: float | None = 50.0,
    robust_scale: bool = True,
    clamp: float | None = 5.0,
    scaler_fit_scope: str = "recording",
    split_text_normalization: str = "official-exact",
    split_ratios: Mapping[str, float] | None = None,
    split_seed: float = 0.0,
    max_sentences: int | None = None,
) -> SentenceExtractionSummary:
    """Build one continuous, trial-aligned sentence cache from a FIF/MAT pair."""

    if sfreq <= 0:
        raise ValueError("sfreq must be > 0")
    if max_channels is not None and max_channels < 1:
        raise ValueError("max_channels must be >= 1 when provided")
    if scaler_fit_scope not in {"recording", "train"}:
        raise ValueError("scaler_fit_scope must be one of: recording, train")
    raw_file = Path(raw_path)
    events_file = Path(events_path)
    output_file = Path(out_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw FIF file not found: {raw_file}")
    if not events_file.exists():
        raise FileNotFoundError(f"MAT event/log file not found: {events_file}")

    started_at = time.perf_counter()
    mne, _loadmat, np = require_neuro_dependencies()
    raw = mne.io.read_raw_fif(str(raw_file), preload=False, verbose="ERROR")
    raw_part_paths = [Path(str(value)) for value in raw.filenames if value is not None]
    raw_parts = [{"path": str(path), "bytes": _safe_stat_size(path)} for path in raw_part_paths]
    raw_total_bytes = sum(int(row["bytes"] or 0) for row in raw_parts)
    original_sfreq = float(raw.info["sfreq"])
    original_n_times = int(raw.n_times)
    raw_duration_sec = original_n_times / original_sfreq
    first_samp = int(raw.first_samp)

    stim_events = mne.find_events(
        raw,
        stim_channel=stim_channel,
        shortest_event=1,
        verbose="ERROR",
    )
    stim_key = stim_key_event_rows(
        stim_events,
        sfreq=original_sfreq,
        stim_channel=stim_channel,
        source_path=str(raw_file),
        first_samp=first_samp,
    )
    labels = [row.label for row in stim_key.rows]
    event_times = [row.time_sec for row in stim_key.rows]
    key_sequences = group_key_labels_into_sequences(labels, event_times=event_times)
    key_time_sequences = group_key_event_times_into_sequences(labels, event_times)
    target_sequences, response_sequences, mat_warnings = load_mat_sequence_sources(events_file)
    mat_time_sequences, mat_timing_warnings = load_mat_key_trigger_time_sequences(events_file)
    trial_mapping = build_mat_trial_index_map(
        key_sequences,
        target_sequences,
        response_sequences,
        mat_time_sequences,
    )
    key_trigger_timing_audit = None
    if mat_time_sequences:
        mapped_mat_time_sequences = [
            mat_time_sequences[index] for index in trial_mapping.raw_to_mat_trial_indices
        ]
        key_trigger_timing_audit = summarize_key_trigger_timing(
            key_time_sequences,
            mapped_mat_time_sequences,
        )
    records = build_sentence_records(
        key_sequences,
        target_sequences,
        response_sequences,
        pre_context_sec=pre_context_sec,
        post_context_sec=post_context_sec,
        raw_duration_sec=raw_duration_sec,
        trial_index_map=trial_mapping.raw_to_mat_trial_indices,
        max_sentences=max_sentences,
    )

    _apply_channel_picks(raw, picks=picks, max_channels=None)
    n_channels_after_picks = len(raw.ch_names)
    _apply_channel_picks(raw, picks=None, max_channels=max_channels)
    channel_cap_applied = len(raw.ch_names) < n_channels_after_picks
    channel_geometry = describe_raw_channels(raw)
    raw.load_data()
    if notch_freq is not None:
        raw.notch_filter(freqs=[float(notch_freq)], n_jobs=1, verbose="ERROR")
    if l_freq is not None or h_freq is not None:
        raw.filter(
            l_freq=l_freq,
            h_freq=h_freq,
            n_jobs=1,
            verbose="ERROR",
        )
    if float(raw.info["sfreq"]) != float(sfreq):
        raw.resample(float(sfreq), npad="auto", n_jobs=1, verbose="ERROR")

    processed_sfreq = float(raw.info["sfreq"])
    signal = raw.get_data().astype("float32", copy=False)
    zero_iqr_channels = 0
    scaler_stats: dict[str, object] | None = None
    split_membership: dict[str, object] | None = None
    if robust_scale and scaler_fit_scope == "recording":
        signal, zero_iqr_channels = robust_scale_channels(signal, clamp=clamp)
    arrays = extract_padded_sentence_arrays(signal, sfreq=processed_sfreq, records=records)
    if scaler_fit_scope == "train":
        split_membership = build_sentence_text_membership(
            arrays["reference_texts"].tolist(),
            trial_indices=arrays["trial_indices"].tolist(),
            text_source="reference",
            text_normalization=split_text_normalization,
            ratios=split_ratios,
            seed=split_seed,
        )
        empty_partitions = [
            name for name, count in split_membership["partition_row_counts"].items() if count == 0
        ]
        if empty_partitions:
            raise ValueError(
                "Train-fit extraction requires non-empty split partitions; empty: "
                + ", ".join(empty_partitions)
            )
        if robust_scale:
            train_indices = [
                int(row["source_row_index"])
                for row in split_membership["rows"]
                if row["split"] == "train"
            ]
            center, scale, fitted = fit_robust_scaler_from_padded(
                arrays["signals"],
                arrays["input_lengths"],
                fit_indices=train_indices,
            )
            arrays["signals"] = apply_robust_scaler_to_padded(
                arrays["signals"],
                arrays["input_lengths"],
                center=center,
                scale=scale,
                clamp=clamp,
            )
            zero_iqr_channels = int(fitted["zero_iqr_channels"])
            scaler_stats = {
                **fitted,
                "center": [float(value) for value in center],
                "scale": [float(value) for value in scale],
                "center_sha256": scaler_array_sha256(center),
                "scale_sha256": scaler_array_sha256(scale),
                "fit_row_indices": train_indices,
                "fit_trial_indices": [
                    int(arrays["trial_indices"][index]) for index in train_indices
                ],
            }
    channel_names = list(raw.ch_names)
    warnings = [
        *mat_warnings,
        *mat_timing_warnings,
        *trial_mapping.warnings,
        *stim_key.warnings,
        "ctc_targets_are_raw_stim_typed_text_without_enter",
        "reference_text_is_stored_separately_from_typed_ctc_target",
        "real_cache_records_physical_typing_not_arbitrary_thoughts",
    ]
    if channel_cap_applied:
        warnings.append(
            "first_n_channels_are_a_resource_smoke_subset_not_an_optimized_sensor_layout"
        )
    if str(picks).lower() == "mag":
        warnings.append("magnetometer_only_cache_is_not_the_full_306_channel_v2_input")
    if any(row["position_m"] is None for row in channel_geometry):
        warnings.append("one_or_more_selected_channels_lack_finite_device_coordinates")
    if robust_scale and scaler_fit_scope == "train":
        warnings.append("robust_scaler_fit_on_train_sentence_rows_only")
    elif robust_scale:
        warnings.append("robust_scaler_fit_on_complete_recording_is_transductive")
    if zero_iqr_channels:
        warnings.append(f"robust_scaler_zero_iqr_channels:{zero_iqr_channels}")

    scaler_params: dict[str, object] = {
        "enabled": robust_scale,
        "clamp": clamp,
        "fit_split": scaler_fit_scope,
        "fit_scope": (
            "valid_train_sentence_timepoints"
            if scaler_fit_scope == "train"
            else "complete_continuous_recording"
        ),
    }
    if split_membership is not None:
        scaler_params.update(
            {
                "split_protocol_config_sha256": split_membership["protocol_config_sha256"],
                "semantic_membership_sha256": split_membership["semantic_membership_sha256"],
            }
        )
    if scaler_stats is not None:
        scaler_params["statistics"] = scaler_stats

    transformations: list[dict[str, object]] = [
        {
            "name": "mne_read_raw_fif",
            "description": "Opened the explicit FIF recording and all required split parts without preloading.",
            "params": {"raw_path": str(raw_file), "raw_parts": raw_parts},
        },
        {
            "name": "stim_key_sentence_boundaries",
            "description": (
                "Grouped raw STI101 key triggers by ENTER and used first key through ENTER "
                "as each trial boundary."
            ),
            "params": {
                "stim_channel": stim_channel,
                "raw_first_samp": first_samp,
                "pre_context_sec": pre_context_sec,
                "post_context_sec": post_context_sec,
            },
        },
        {
            "name": "strict_mat_trial_pairing",
            "description": "Paired raw typed rows to performed MAT trial slots without fuzzy text ordering.",
            "params": {
                "events_path": str(events_file),
                **trial_mapping.to_dict(),
                "key_trigger_timing_audit": key_trigger_timing_audit,
            },
        },
        {
            "name": "channel_picking_before_load",
            "description": "Applied channel picks and cap before loading signal samples.",
            "params": {
                "picks": picks,
                "max_channels": max_channels,
                "n_channels_after_picks_before_cap": n_channels_after_picks,
                "channel_cap_applied": channel_cap_applied,
            },
        },
    ]
    if notch_freq is not None:
        transformations.append(
            {
                "name": "notch_filter",
                "description": "Applied a single-thread MNE notch filter before downsampling.",
                "params": {"frequency_hz": notch_freq, "n_jobs": 1},
            }
        )
    if l_freq is not None or h_freq is not None:
        transformations.append(
            {
                "name": "bandpass_filter",
                "description": "Applied a single-thread MNE bandpass filter before downsampling.",
                "params": {"l_freq": l_freq, "h_freq": h_freq, "n_jobs": 1},
            }
        )
    transformations.extend(
        [
            {
                "name": "resample",
                "description": "Downsampled the selected continuous channels.",
                "params": {
                    "original_sfreq": original_sfreq,
                    "target_sfreq": processed_sfreq,
                    "n_jobs": 1,
                },
            },
            {
                "name": "per_channel_robust_scaler",
                "description": "Centered each channel by its median and divided by its IQR.",
                "params": scaler_params,
            },
            {
                "name": "zero_pad_variable_sentences",
                "description": "Padded variable sentence signals and targets while storing true lengths.",
            },
        ]
    )
    metadata = {
        "kind": "real_fif_mat_continuous_sentences",
        "source_files": {
            "raw": str(raw_file),
            "raw_parts": [str(path) for path in raw_part_paths],
            "events": str(events_file),
        },
        "transformations": transformations,
        "extraction_params": {
            "sfreq": processed_sfreq,
            "pre_context_sec": pre_context_sec,
            "post_context_sec": post_context_sec,
            "picks": picks,
            "max_channels": max_channels,
            "stim_channel": stim_channel,
            "l_freq": l_freq,
            "h_freq": h_freq,
            "notch_freq": notch_freq,
            "robust_scale": robust_scale,
            "clamp": clamp,
            "scaler_fit_scope": scaler_fit_scope,
            "split_text_normalization": split_text_normalization,
            "split_ratios": (
                split_membership["protocol"]["ratios"] if split_membership is not None else None
            ),
            "split_seed": split_seed if split_membership is not None else None,
            "max_sentences": max_sentences,
        },
        "raw": {
            "original_sfreq": original_sfreq,
            "original_n_times": original_n_times,
            "duration_sec": raw_duration_sec,
            "first_samp": first_samp,
            "bytes": raw_total_bytes,
            "parts": raw_parts,
        },
        "events": {
            "stim_key_candidates": stim_key.n_candidate_events,
            "stim_key_after_initial_sweep_drop": len(stim_key.rows),
            "initial_ascii_sweep_dropped": stim_key.n_dropped_initial_ascii_sweep,
            "key_sequences": len(key_sequences),
            "mat_targets": len(target_sequences),
            "mat_responses": len(response_sequences),
            "mat_key_trigger_trials": len(mat_time_sequences),
            "trial_index_mapping": trial_mapping.to_dict(),
            "key_trigger_timing_audit": key_trigger_timing_audit,
            "sentences_written": len(records),
        },
        "channels": {
            "n_channels": len(channel_names),
            "names": channel_names,
            "geometry": channel_geometry,
            "position_units": "m",
            "position_source": "raw.info['chs'][index]['loc'][:3]",
        },
        "split_membership": split_membership,
        "warnings": warnings,
    }
    save_sentence_npz_cache(
        output_file,
        **arrays,
        channel_names=np.asarray(channel_names, dtype="U"),
        metadata=metadata,
    )
    runtime_sec = round(time.perf_counter() - started_at, 6)
    input_lengths = arrays["input_lengths"]
    target_lengths = arrays["target_lengths"]
    return SentenceExtractionSummary(
        raw_path=str(raw_file),
        events_path=str(events_file),
        out_path=str(output_file),
        n_candidate_key_events=stim_key.n_candidate_events,
        n_key_events_after_sweep=len(stim_key.rows),
        n_sentences=len(records),
        n_channels=len(channel_names),
        max_timepoints=int(arrays["signals"].shape[2]),
        total_valid_timepoints=int(input_lengths.sum()),
        min_input_length=int(input_lengths.min()),
        max_input_length=int(input_lengths.max()),
        min_target_length=int(target_lengths.min()),
        max_target_length=int(target_lengths.max()),
        sfreq=processed_sfreq,
        output_bytes=int(output_file.stat().st_size),
        runtime_sec=runtime_sec,
        peak_rss_bytes=_peak_rss_bytes(),
        channel_names=channel_names,
        scaler_fit_scope=scaler_fit_scope,
        split_partition_counts=(
            dict(split_membership["partition_row_counts"]) if split_membership is not None else None
        ),
        split_protocol_config_sha256=(
            str(split_membership["protocol_config_sha256"])
            if split_membership is not None
            else None
        ),
        semantic_membership_sha256=(
            str(split_membership["semantic_membership_sha256"])
            if split_membership is not None
            else None
        ),
        trial_index_mapping_strategy=trial_mapping.strategy,
        skipped_mat_trial_indices=list(trial_mapping.skipped_mat_trial_indices),
        warnings=list(dict.fromkeys(warnings)),
    )


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Sentence extraction requires NumPy: `pip install numpy`.") from exc
    return np


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (ImportError, OSError, ValueError):  # pragma: no cover - platform-dependent
        return None
    return value if sys.platform == "darwin" else value * 1024


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None


def scaler_array_sha256(value) -> str:
    """Hash frozen scaler arrays using the cache metadata contract."""

    np = _require_numpy()
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(tuple(array.shape)).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def _optional_int(value) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError, OverflowError):
        return None
