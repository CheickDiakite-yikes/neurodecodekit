"""Versioned continuous neurotoken cache and bounded mock producer."""

from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


NEUROTOKEN_CACHE_SCHEMA_NAME = "neurotoken-cache"
NEUROTOKEN_CACHE_SCHEMA_VERSION = 0
OFFICIAL_V2_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_MODEL_SOURCE = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/models.py"
)
OFFICIAL_V2_CONFIG_SOURCE = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/config/model_config.py"
)
OFFICIAL_V2_PAPER = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
SUPPORTED_TOKEN_DTYPES = ("float32", "float16")


class NeuroTokenCacheSchemaError(ValueError):
    """Raised when a neurotoken cache violates its semantic contract."""


@dataclass(frozen=True)
class NeuroTokenCacheSummary:
    """Compact shape, timing, geometry, split, and provenance summary."""

    path: str
    bytes: int | None
    schema_name: str
    schema_version: int | None
    kind: str
    modality: str
    device_type: str
    tokens_shape: tuple[int, int, int]
    tokens_dtype: str
    n_items: int
    max_tokens: int
    embedding_dim: int
    total_valid_tokens: int
    padding_fraction: float
    source_channel_count: int
    positioned_source_channel_count: int
    split_counts: dict[str, int]
    continuous_tokens: bool
    learned_representation: bool
    producer_causal: bool
    end_to_end_latency_measured: bool
    source_cache_sha256: str
    token_payload_sha256: str
    arrays: dict[str, dict[str, object]]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LoadedNeuroTokenCache:
    """Validated neurotoken arrays and metadata."""

    path: str
    tokens: Any
    token_lengths: Any
    token_mask: Any
    token_start_sec: Any
    token_end_sec: Any
    item_ids: Any
    split_labels: Any
    source_row_indices: Any
    source_trial_indices: Any
    source_input_lengths: Any
    source_start_sec: Any
    source_end_sec: Any
    subject_ids: Any
    session_ids: Any
    source_channel_names: Any
    source_channel_positions: Any
    source_channel_position_mask: Any
    metadata: dict[str, Any]
    summary: NeuroTokenCacheSummary


def save_neurotoken_cache(
    path: str | Path,
    *,
    tokens,
    token_lengths,
    token_mask,
    token_start_sec,
    token_end_sec,
    item_ids,
    split_labels,
    source_row_indices,
    source_trial_indices,
    source_input_lengths,
    source_start_sec,
    source_end_sec,
    subject_ids,
    session_ids,
    source_channel_names,
    source_channel_positions,
    source_channel_position_mask,
    metadata: Mapping[str, Any],
    metadata_sidecar: str | Path | None = None,
) -> None:
    """Validate and save one continuous neurotoken cache."""

    np = _require_numpy()
    arrays = {
        "tokens": np.asarray(tokens),
        "token_lengths": np.asarray(token_lengths),
        "token_mask": np.asarray(token_mask),
        "token_start_sec": np.asarray(token_start_sec),
        "token_end_sec": np.asarray(token_end_sec),
        "item_ids": np.asarray(item_ids),
        "split_labels": np.asarray(split_labels),
        "source_row_indices": np.asarray(source_row_indices),
        "source_trial_indices": np.asarray(source_trial_indices),
        "source_input_lengths": np.asarray(source_input_lengths),
        "source_start_sec": np.asarray(source_start_sec),
        "source_end_sec": np.asarray(source_end_sec),
        "subject_ids": np.asarray(subject_ids),
        "session_ids": np.asarray(session_ids),
        "source_channel_names": np.asarray(source_channel_names),
        "source_channel_positions": np.asarray(source_channel_positions),
        "source_channel_position_mask": np.asarray(source_channel_position_mask),
    }
    _validate_arrays(arrays)
    normalized_metadata = _normalize_metadata(metadata, arrays)
    _validate_metadata(normalized_metadata)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        **arrays,
        metadata=json.dumps(normalized_metadata, sort_keys=True),
    )
    if metadata_sidecar is not None:
        write_neurotoken_metadata_sidecar(output, metadata_sidecar)


def load_neurotoken_cache(path: str | Path) -> LoadedNeuroTokenCache:
    """Load and validate one NeuroTokenCache v0 artifact."""

    np = _require_numpy()
    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        missing = sorted(_required_array_names() - set(data.files))
        if "metadata" not in data.files:
            missing.append("metadata")
        if missing:
            raise NeuroTokenCacheSchemaError(
                f"Neurotoken cache is missing arrays: {missing}"
            )
        arrays = {name: data[name].copy() for name in _required_array_names()}
        metadata = _decode_metadata(data["metadata"])
    _validate_arrays(arrays)
    _validate_metadata(metadata)
    normalized_metadata = _normalize_metadata(metadata, arrays)
    if normalized_metadata != metadata:
        raise NeuroTokenCacheSchemaError(
            "Neurotoken metadata is not normalized for its stored arrays."
        )
    summary = summarize_neurotoken_cache(
        cache_path,
        arrays=arrays,
        metadata=metadata,
    )
    return LoadedNeuroTokenCache(
        path=str(cache_path),
        metadata=metadata,
        summary=summary,
        **arrays,
    )


def write_neurotoken_metadata_sidecar(
    cache_path: str | Path,
    out_path: str | Path,
) -> None:
    """Write compact inspectable metadata without duplicating token arrays."""

    loaded = load_neurotoken_cache(cache_path)
    output = Path(out_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": loaded.summary.to_dict(), "metadata": loaded.metadata}
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_neurotoken_cache(
    path: str | Path,
    *,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> NeuroTokenCacheSummary:
    """Build a compact report after validation."""

    tokens = arrays["tokens"]
    lengths = arrays["token_lengths"]
    total_valid = int(lengths.sum())
    total_slots = int(tokens.shape[0] * tokens.shape[1])
    schema = metadata["schema"]
    representation = metadata["representation"]
    streaming = metadata["streaming_contract"]
    source = metadata["source"]
    return NeuroTokenCacheSummary(
        path=str(Path(path)),
        bytes=_safe_stat_size(Path(path)),
        schema_name=str(schema["name"]),
        schema_version=int(schema["version"]),
        kind=str(metadata["kind"]),
        modality=str(metadata["modality"]),
        device_type=str(metadata["device_type"]),
        tokens_shape=tuple(int(value) for value in tokens.shape),
        tokens_dtype=str(tokens.dtype),
        n_items=int(tokens.shape[0]),
        max_tokens=int(tokens.shape[1]),
        embedding_dim=int(tokens.shape[2]),
        total_valid_tokens=total_valid,
        padding_fraction=(1.0 - total_valid / total_slots) if total_slots else 0.0,
        source_channel_count=int(len(arrays["source_channel_names"])),
        positioned_source_channel_count=int(arrays["source_channel_position_mask"].sum()),
        split_counts={
            name: int(count)
            for name, count in sorted(
                Counter(str(value) for value in arrays["split_labels"].tolist()).items()
            )
        },
        continuous_tokens=bool(representation["continuous"]),
        learned_representation=bool(representation["learned"]),
        producer_causal=bool(streaming["producer_causal"]),
        end_to_end_latency_measured=bool(streaming["end_to_end_latency_measured"]),
        source_cache_sha256=str(source["cache_sha256"]),
        token_payload_sha256=str(metadata["token_payload_sha256"]),
        arrays=dict(metadata["arrays"]),
        warnings=list(metadata["warnings"]),
    )


def project_sentence_cache_to_neurotokens(
    *,
    source_cache_path: str | Path,
    split_report_path: str | Path,
    out_path: str | Path,
    modality: str,
    device_type: str,
    subject_id: str,
    session_id: str,
    source_sampling_rate_hz: float | None = None,
    embedding_dim: int = 32,
    kernel_size: int = 16,
    stride: int = 4,
    seed: int = 23,
    token_dtype: str = "float32",
    max_items: int = 128,
    max_tokens_per_item: int = 4096,
    max_output_mb: float = 32.0,
    overwrite: bool = False,
    metadata_sidecar: str | Path | None = None,
) -> dict[str, Any]:
    """Create a target-free mock embedding cache from one sentence cache."""

    from neurodecodekit.cache.sentence_npz import load_sentence_npz_cache
    from neurodecodekit.evaluation.split_protocol import load_training_partitions

    started_at = time.perf_counter()
    source_path = Path(source_cache_path)
    split_path = Path(split_report_path)
    output = Path(out_path)
    if output.exists() and not overwrite:
        raise FileExistsError(f"Refusing to replace existing neurotoken cache: {output}")
    if metadata_sidecar is not None and Path(metadata_sidecar).exists() and not overwrite:
        raise FileExistsError(f"Refusing to replace metadata sidecar: {metadata_sidecar}")
    _validate_projection_params(
        embedding_dim=embedding_dim,
        kernel_size=kernel_size,
        stride=stride,
        token_dtype=token_dtype,
        max_items=max_items,
        max_tokens_per_item=max_tokens_per_item,
        max_output_mb=max_output_mb,
    )
    source = load_sentence_npz_cache(source_path)
    n_items = int(source.signals.shape[0])
    if n_items > max_items:
        raise ValueError(f"Source has {n_items} items, exceeding --max-items {max_items}.")
    partitions = load_training_partitions(
        split_path,
        source_path,
        eval_partition="test",
        require_strict=True,
    )
    sfreq = _resolve_source_sampling_rate(source.metadata, source_sampling_rate_hz)
    projection = project_mock_temporal_embeddings(
        signals=source.signals,
        input_lengths=source.input_lengths,
        source_start_sec=source.sentence_start_sec,
        source_sampling_rate_hz=sfreq,
        embedding_dim=embedding_dim,
        kernel_size=kernel_size,
        stride=stride,
        seed=seed,
        token_dtype=token_dtype,
        max_tokens_per_item=max_tokens_per_item,
        max_output_mb=max_output_mb,
    )
    split_labels = _split_labels(partitions, n_items=n_items)
    source_sha256 = _file_sha256(source_path)
    split_sha256 = _file_sha256(split_path)
    source_rows = _require_numpy().arange(n_items, dtype="int32")
    trial_indices = _require_numpy().asarray(source.trial_indices, dtype="int32")
    item_ids = _item_ids(source_sha256, source_rows, trial_indices)
    positions, position_mask, geometry_metadata = _source_channel_geometry(source)
    warnings = [
        "continuous_neurotokens_are_not_discrete_codes",
        "mock_random_projection_is_not_a_learned_neural_representation",
        "mock_projection_uses_no_target_text_or_target_labels",
        "cache_contract_does_not_establish_decoding_accuracy",
        "official_v2_reference_encoder_is_noncausal_whole_sentence",
        "real_time_requires_a_causal_decoder_and_measured_end_to_end_latency",
        "not_arbitrary_thought_decoding",
    ]
    if not bool(position_mask.all()):
        warnings.append("some_or_all_source_channel_geometry_unavailable")
    if str(modality).strip().lower() == "synthetic":
        warnings.append("synthetic_source_only_no_real_neural_representation_claim")
    runtime_before_write = time.perf_counter() - started_at
    metadata = {
        "kind": "mock_continuous_neurotokens",
        "modality": _required_text(modality, "modality"),
        "device_type": _required_text(device_type, "device_type"),
        "representation": {
            "name": "mock_temporal_gaussian_projection_v1",
            "continuous": True,
            "discrete": False,
            "learned": False,
            "fit_scope": "none",
            "uses_target_labels": False,
            "embedding_dim": int(embedding_dim),
            "seed": int(seed),
            "weights_sha256": projection["weights_sha256"],
            "source_layout": "items,channels,timepoints",
            "token_layout": "items,time,embedding",
        },
        "source": {
            "cache_path": str(source_path),
            "cache_sha256": source_sha256,
            "cache_bytes": int(source_path.stat().st_size),
            "cache_schema": source.metadata.get("schema"),
            "split_report_path": str(split_path),
            "split_report_sha256": split_sha256,
            "source_signal_array_loaded": True,
            "target_text_array_used_by_projection": False,
            "target_token_array_used_by_projection": False,
        },
        "split_protocol": {
            "name": "b2q-split-protocol",
            "version": 1,
            "protocol": partitions.protocol,
            "protocol_config_sha256": partitions.protocol_config_sha256,
            "group_assignment_sha256": partitions.group_assignment_sha256,
            "semantic_membership_sha256": partitions.semantic_membership_sha256,
            "source_cache_sha256": partitions.source_cache_sha256,
        },
        "source_timebase": {
            "sampling_rate_hz": float(sfreq),
            "input_layout": "items,channels,timepoints",
        },
        "streaming_contract": {
            "asynchronous_input": True,
            "producer_causal": True,
            "producer_right_context_samples": 0,
            "token_timestamp_reference": "frame_end",
            "kernel_samples": int(kernel_size),
            "stride_samples": int(stride),
            "receptive_field_sec": float(kernel_size / sfreq),
            "token_step_sec": float(stride / sfreq),
            "minimum_producer_latency_sec": float(kernel_size / sfreq),
            "downstream_decoder_causality": "unspecified",
            "end_to_end_latency_measured": False,
        },
        "source_geometry": geometry_metadata,
        "official_v2_compatibility": {
            "official_commit": OFFICIAL_V2_COMMIT,
            "model_source": OFFICIAL_V2_MODEL_SOURCE,
            "config_source": OFFICIAL_V2_CONFIG_SOURCE,
            "paper": OFFICIAL_V2_PAPER,
            "maps_to_public_tensor": "z_final",
            "public_tensor_layout": "batch,time,embedding",
            "public_downsampling_kernel_samples": 16,
            "public_downsampling_stride_samples": 4,
            "matches_public_kernel_stride": kernel_size == 16 and stride == 4,
            "public_encoder_causal": False,
            "englishbcbl_public_data_available": False,
        },
        "resources": {
            "runtime_before_write_sec": round(runtime_before_write, 6),
            "peak_rss_bytes": _peak_rss_bytes(),
            "token_payload_bytes": int(projection["tokens"].nbytes),
            "projected_uncompressed_core_bytes": int(projection["projected_core_bytes"]),
            "max_output_bytes": int(max_output_mb * 1024 * 1024),
            "num_threads_requested": 1,
        },
        "transformations": [
            {
                "name": "mock_temporal_gaussian_projection_v1",
                "description": (
                    "Projected fixed overlapping source-signal frames with deterministic "
                    "target-free Gaussian weights for interface validation only."
                ),
                "params": {
                    "embedding_dim": int(embedding_dim),
                    "kernel_size": int(kernel_size),
                    "stride": int(stride),
                    "seed": int(seed),
                    "token_dtype": token_dtype,
                },
            }
        ],
        "claim_boundaries": [
            "Interface and serialization proof only.",
            "No encoder was trained and no decoding metric was evaluated.",
            "Mock projections are not semantic or physiological neurotokens.",
            "Producer causality does not imply a causal downstream decoder.",
            "No end-to-end or device latency was measured.",
            "No EnglishBCBL or unreleased Brain2Qwerty v2 data was used.",
        ],
        "warnings": warnings,
    }
    subject_ids = _require_numpy().full(n_items, _required_text(subject_id, "subject_id"))
    session_ids = _require_numpy().full(n_items, _required_text(session_id, "session_id"))
    save_neurotoken_cache(
        output,
        tokens=projection["tokens"],
        token_lengths=projection["token_lengths"],
        token_mask=projection["token_mask"],
        token_start_sec=projection["token_start_sec"],
        token_end_sec=projection["token_end_sec"],
        item_ids=item_ids,
        split_labels=split_labels,
        source_row_indices=source_rows,
        source_trial_indices=trial_indices,
        source_input_lengths=source.input_lengths,
        source_start_sec=source.sentence_start_sec,
        source_end_sec=source.sentence_end_sec,
        subject_ids=subject_ids,
        session_ids=session_ids,
        source_channel_names=source.channel_names,
        source_channel_positions=positions,
        source_channel_position_mask=position_mask,
        metadata=metadata,
        metadata_sidecar=metadata_sidecar,
    )
    output_bytes = int(output.stat().st_size)
    max_output_bytes = int(max_output_mb * 1024 * 1024)
    if output_bytes > max_output_bytes:
        output.unlink(missing_ok=True)
        if metadata_sidecar is not None:
            Path(metadata_sidecar).unlink(missing_ok=True)
        raise ValueError(
            f"Neurotoken cache output {output_bytes} bytes exceeds cap {max_output_bytes}."
        )
    loaded = load_neurotoken_cache(output)
    return {
        "proof_posture": "synthetic_neurotoken_interface_roundtrip_only",
        "summary": loaded.summary.to_dict(),
        "source_cache_path": str(source_path),
        "split_report_path": str(split_path),
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "output_bytes": output_bytes,
        "metadata_sidecar_bytes": (
            int(Path(metadata_sidecar).stat().st_size) if metadata_sidecar is not None else 0
        ),
        "model_runs": 0,
        "training_runs": 0,
        "real_data_reads": 0 if str(modality).strip().lower() == "synthetic" else None,
        "warnings": loaded.summary.warnings,
    }


def project_mock_temporal_embeddings(
    *,
    signals,
    input_lengths,
    source_start_sec,
    source_sampling_rate_hz: float,
    embedding_dim: int,
    kernel_size: int,
    stride: int,
    seed: int,
    token_dtype: str = "float32",
    max_tokens_per_item: int = 4096,
    max_output_mb: float = 32.0,
) -> dict[str, Any]:
    """Project fixed source frames without labels, fitting, or training."""

    np = _require_numpy()
    x = np.asarray(signals)
    lengths = np.asarray(input_lengths, dtype="int64")
    starts_sec = np.asarray(source_start_sec, dtype="float64")
    if x.ndim != 3 or not np.issubdtype(x.dtype, np.floating):
        raise ValueError("signals must be floating [items, channels, timepoints]")
    if not np.isfinite(x).all():
        raise ValueError("signals contain non-finite values")
    if lengths.ndim != 1 or len(lengths) != x.shape[0]:
        raise ValueError("input_lengths must contain one value per item")
    if starts_sec.ndim != 1 or len(starts_sec) != x.shape[0]:
        raise ValueError("source_start_sec must contain one value per item")
    if not math.isfinite(source_sampling_rate_hz) or source_sampling_rate_hz <= 0:
        raise ValueError("source_sampling_rate_hz must be finite and positive")
    if (lengths < kernel_size).any() or (lengths > x.shape[2]).any():
        raise ValueError("Every valid input length must fit at least one complete kernel frame.")
    token_lengths = 1 + (lengths - kernel_size) // stride
    max_tokens = int(token_lengths.max())
    if max_tokens > max_tokens_per_item:
        raise ValueError(
            f"Projection needs {max_tokens} tokens per item, exceeding cap "
            f"{max_tokens_per_item}."
        )
    dtype = _normalize_token_dtype(token_dtype)
    itemsize = np.dtype(dtype).itemsize
    tokens_bytes = int(x.shape[0] * max_tokens * embedding_dim * itemsize)
    timing_bytes = int(x.shape[0] * max_tokens * (1 + 8 + 8))
    projected_core_bytes = tokens_bytes + timing_bytes
    max_output_bytes = int(max_output_mb * 1024 * 1024)
    if projected_core_bytes > max_output_bytes:
        raise ValueError(
            f"Projected core arrays need {projected_core_bytes} bytes, exceeding cap "
            f"{max_output_bytes}."
        )
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    weights = rng.standard_normal(
        size=(int(x.shape[1]) * kernel_size, embedding_dim)
    ).astype("float32")
    weights /= math.sqrt(int(x.shape[1]) * kernel_size)
    tokens = np.zeros((x.shape[0], max_tokens, embedding_dim), dtype=dtype)
    mask = np.zeros((x.shape[0], max_tokens), dtype="bool")
    token_start = np.full((x.shape[0], max_tokens), -1.0, dtype="float64")
    token_end = np.full((x.shape[0], max_tokens), -1.0, dtype="float64")
    for row_index, length in enumerate(lengths.tolist()):
        frame_starts = list(range(0, int(length) - kernel_size + 1, stride))
        frames = np.stack(
            [x[row_index, :, start : start + kernel_size].reshape(-1) for start in frame_starts]
        ).astype("float32", copy=False)
        count = len(frame_starts)
        tokens[row_index, :count] = (frames @ weights).astype(dtype)
        mask[row_index, :count] = True
        token_start[row_index, :count] = starts_sec[row_index] + (
            np.asarray(frame_starts, dtype="float64") / source_sampling_rate_hz
        )
        token_end[row_index, :count] = starts_sec[row_index] + (
            (np.asarray(frame_starts, dtype="float64") + kernel_size)
            / source_sampling_rate_hz
        )
    return {
        "tokens": tokens,
        "token_lengths": token_lengths.astype("int32"),
        "token_mask": mask,
        "token_start_sec": token_start,
        "token_end_sec": token_end,
        "weights_sha256": hashlib.sha256(weights.tobytes(order="C")).hexdigest(),
        "projected_core_bytes": projected_core_bytes,
    }


def _validate_arrays(arrays: Mapping[str, Any]) -> None:
    np = _require_numpy()
    tokens = arrays["tokens"]
    if tokens.ndim != 3 or min(tokens.shape) < 1:
        raise NeuroTokenCacheSchemaError(
            f"tokens must be nonempty [items, time, embedding], got {tokens.shape}"
        )
    if str(tokens.dtype) not in SUPPORTED_TOKEN_DTYPES:
        raise NeuroTokenCacheSchemaError(
            f"tokens dtype must be one of {SUPPORTED_TOKEN_DTYPES}, got {tokens.dtype}"
        )
    if not np.isfinite(tokens).all():
        raise NeuroTokenCacheSchemaError("tokens contain non-finite values")
    n_items, max_tokens, _ = tokens.shape
    vector_names = {
        "token_lengths",
        "item_ids",
        "split_labels",
        "source_row_indices",
        "source_trial_indices",
        "source_input_lengths",
        "source_start_sec",
        "source_end_sec",
        "subject_ids",
        "session_ids",
    }
    for name in vector_names:
        value = arrays[name]
        if value.ndim != 1 or len(value) != n_items:
            raise NeuroTokenCacheSchemaError(
                f"{name} must contain {n_items} rows, got {value.shape}"
            )
    for name in ("token_lengths", "source_row_indices", "source_trial_indices", "source_input_lengths"):
        if not np.issubdtype(arrays[name].dtype, np.integer):
            raise NeuroTokenCacheSchemaError(f"{name} must use an integer dtype")
    lengths = arrays["token_lengths"].astype("int64", copy=False)
    if (lengths < 1).any() or (lengths > max_tokens).any():
        raise NeuroTokenCacheSchemaError("token_lengths must fit the padded token width")
    mask = arrays["token_mask"]
    if mask.shape != (n_items, max_tokens) or mask.dtype != np.dtype("bool"):
        raise NeuroTokenCacheSchemaError("token_mask must be boolean [items, time]")
    expected_mask = np.arange(max_tokens)[None, :] < lengths[:, None]
    if not np.array_equal(mask, expected_mask):
        raise NeuroTokenCacheSchemaError("token_mask must exactly match token_lengths")
    for name in ("token_start_sec", "token_end_sec"):
        value = arrays[name]
        if value.shape != (n_items, max_tokens) or not np.issubdtype(
            value.dtype, np.floating
        ):
            raise NeuroTokenCacheSchemaError(f"{name} must be floating [items, time]")
        if not np.isfinite(value).all():
            raise NeuroTokenCacheSchemaError(f"{name} contains non-finite values")
    start = arrays["token_start_sec"]
    end = arrays["token_end_sec"]
    if (end[mask] <= start[mask]).any() or (start[mask] < 0).any():
        raise NeuroTokenCacheSchemaError("valid token intervals must be nonnegative and ordered")
    if not np.all(start[~mask] == -1.0) or not np.all(end[~mask] == -1.0):
        raise NeuroTokenCacheSchemaError("padded token timestamps must use -1")
    if np.any(tokens[~mask] != 0):
        raise NeuroTokenCacheSchemaError("padded token vectors must be zero")
    for row_index, length in enumerate(lengths.tolist()):
        if length > 1 and np.any(np.diff(start[row_index, :length]) <= 0):
            raise NeuroTokenCacheSchemaError("valid token starts must increase monotonically")
    source_start = arrays["source_start_sec"]
    source_end = arrays["source_end_sec"]
    if not np.isfinite(source_start).all() or not np.isfinite(source_end).all():
        raise NeuroTokenCacheSchemaError("source item timing must be finite")
    if (source_end <= source_start).any():
        raise NeuroTokenCacheSchemaError("source item end must follow source item start")
    for row_index, length in enumerate(lengths.tolist()):
        if start[row_index, 0] < source_start[row_index] - 1e-9:
            raise NeuroTokenCacheSchemaError("token starts before its source item")
        if end[row_index, length - 1] > source_end[row_index] + 1e-6:
            raise NeuroTokenCacheSchemaError("token ends after its source item")
    _validate_unique_text_vector(arrays["item_ids"], "item_ids")
    _validate_nonempty_text_vector(arrays["split_labels"], "split_labels")
    _validate_nonempty_text_vector(arrays["subject_ids"], "subject_ids")
    _validate_nonempty_text_vector(arrays["session_ids"], "session_ids")
    if len(set(int(value) for value in arrays["source_row_indices"].tolist())) != n_items:
        raise NeuroTokenCacheSchemaError("source_row_indices must be unique")
    if len(set(int(value) for value in arrays["source_trial_indices"].tolist())) != n_items:
        raise NeuroTokenCacheSchemaError("source_trial_indices must be unique")
    channel_names = arrays["source_channel_names"]
    _validate_unique_text_vector(channel_names, "source_channel_names")
    n_channels = len(channel_names)
    positions = arrays["source_channel_positions"]
    position_mask = arrays["source_channel_position_mask"]
    if positions.shape != (n_channels, 3) or not np.issubdtype(
        positions.dtype, np.floating
    ):
        raise NeuroTokenCacheSchemaError(
            "source_channel_positions must be floating [source_channels, 3]"
        )
    if position_mask.shape != (n_channels,) or position_mask.dtype != np.dtype("bool"):
        raise NeuroTokenCacheSchemaError(
            "source_channel_position_mask must be boolean [source_channels]"
        )
    if not np.isfinite(positions).all():
        raise NeuroTokenCacheSchemaError("source_channel_positions contain non-finite values")
    if np.any(positions[~position_mask] != 0):
        raise NeuroTokenCacheSchemaError("unknown source-channel positions must be zero")


def _normalize_metadata(
    metadata: Mapping[str, Any], arrays: Mapping[str, Any]
) -> dict[str, Any]:
    normalized = dict(metadata)
    normalized["schema"] = {
        "name": NEUROTOKEN_CACHE_SCHEMA_NAME,
        "version": NEUROTOKEN_CACHE_SCHEMA_VERSION,
    }
    normalized["dimensions"] = {
        "n_items": int(arrays["tokens"].shape[0]),
        "max_tokens": int(arrays["tokens"].shape[1]),
        "embedding_dim": int(arrays["tokens"].shape[2]),
        "source_channel_count": int(len(arrays["source_channel_names"])),
    }
    normalized["arrays"] = _array_descriptors(arrays)
    normalized["token_payload_sha256"] = _token_payload_sha256(arrays)
    normalized["semantic_identity_sha256"] = _semantic_identity_sha256(arrays)
    transformations = list(normalized.get("transformations") or [])
    if not any(
        isinstance(value, Mapping) and value.get("name") == "npz_compressed_write"
        for value in transformations
    ):
        transformations.append(
            {
                "name": "npz_compressed_write",
                "description": "Saved NeuroTokenCache v0 arrays with numpy.savez_compressed.",
            }
        )
    normalized["transformations"] = transformations
    normalized["warnings"] = list(dict.fromkeys(normalized.get("warnings") or []))
    normalized["claim_boundaries"] = list(
        dict.fromkeys(normalized.get("claim_boundaries") or [])
    )
    return normalized


def _validate_metadata(metadata: Mapping[str, Any]) -> None:
    schema = metadata.get("schema") or {}
    if schema.get("name") != NEUROTOKEN_CACHE_SCHEMA_NAME:
        raise NeuroTokenCacheSchemaError(
            f"Unexpected neurotoken schema name: {schema.get('name')!r}"
        )
    if schema.get("version") != NEUROTOKEN_CACHE_SCHEMA_VERSION:
        raise NeuroTokenCacheSchemaError(
            f"Unsupported neurotoken schema version: {schema.get('version')!r}"
        )
    for name in ("kind", "modality", "device_type", "token_payload_sha256"):
        if not str(metadata.get(name) or "").strip():
            raise NeuroTokenCacheSchemaError(f"metadata.{name} must be nonempty")
    required_objects = (
        "representation",
        "source",
        "split_protocol",
        "source_timebase",
        "streaming_contract",
        "source_geometry",
        "official_v2_compatibility",
        "resources",
        "arrays",
        "dimensions",
    )
    for name in required_objects:
        if not isinstance(metadata.get(name), Mapping):
            raise NeuroTokenCacheSchemaError(f"metadata.{name} must be an object")
    representation = metadata["representation"]
    if representation.get("continuous") is not True or representation.get("discrete") is not False:
        raise NeuroTokenCacheSchemaError(
            "NeuroTokenCache v0 requires continuous=true and discrete=false"
        )
    if representation.get("uses_target_labels") is not False:
        raise NeuroTokenCacheSchemaError("representation must declare uses_target_labels=false")
    source = metadata["source"]
    for name in ("cache_sha256", "split_report_sha256"):
        if not _is_sha256(str(source.get(name) or "")):
            raise NeuroTokenCacheSchemaError(f"source.{name} must be a SHA-256 digest")
    split = metadata["split_protocol"]
    for name in (
        "protocol_config_sha256",
        "group_assignment_sha256",
        "semantic_membership_sha256",
        "source_cache_sha256",
    ):
        if not _is_sha256(str(split.get(name) or "")):
            raise NeuroTokenCacheSchemaError(f"split_protocol.{name} must be SHA-256")
    if split["source_cache_sha256"] != source["cache_sha256"]:
        raise NeuroTokenCacheSchemaError("split protocol must bind the exact source cache")
    streaming = metadata["streaming_contract"]
    required_streaming = (
        "producer_causal",
        "producer_right_context_samples",
        "minimum_producer_latency_sec",
        "downstream_decoder_causality",
        "end_to_end_latency_measured",
    )
    if any(name not in streaming for name in required_streaming):
        raise NeuroTokenCacheSchemaError("streaming contract is incomplete")
    if not isinstance(metadata.get("claim_boundaries"), list) or not metadata[
        "claim_boundaries"
    ]:
        raise NeuroTokenCacheSchemaError("claim_boundaries must be a nonempty list")
    if not isinstance(metadata.get("warnings"), list):
        raise NeuroTokenCacheSchemaError("warnings must be a list")


def _source_channel_geometry(source) -> tuple[Any, Any, dict[str, Any]]:
    np = _require_numpy()
    names = [str(value) for value in source.channel_names.tolist()]
    positions = np.zeros((len(names), 3), dtype="float32")
    mask = np.zeros(len(names), dtype="bool")
    frames: Counter[str] = Counter()
    rows = list(((source.metadata.get("channels") or {}).get("geometry") or []))
    by_name = {
        str(row.get("name")): row for row in rows if isinstance(row, Mapping)
    }
    for index, name in enumerate(names):
        row = by_name.get(name) or {}
        value = row.get("position_m")
        if isinstance(value, list) and len(value) == 3:
            vector = np.asarray(value, dtype="float32")
            if np.isfinite(vector).all():
                positions[index] = vector
                mask[index] = True
                frames[str(row.get("coord_frame", "unknown"))] += 1
    return positions, mask, {
        "position_units": "m",
        "coordinate_dimensions": 3,
        "positioned_channel_count": int(mask.sum()),
        "missing_position_count": int((~mask).sum()),
        "coordinate_frame_counts": dict(sorted(frames.items())),
        "position_source": (
            "source_cache_metadata.channels.geometry.position_m"
            if mask.any()
            else "unavailable"
        ),
    }


def _resolve_source_sampling_rate(
    metadata: Mapping[str, Any], explicit: float | None
) -> float:
    if explicit is not None:
        value = float(explicit)
    elif metadata.get("sampling_rate_hz") is not None:
        value = float(metadata["sampling_rate_hz"])
    else:
        params = metadata.get("extraction_params") or {}
        value = float(params.get("sfreq", 0.0))
    if not math.isfinite(value) or value <= 0:
        raise ValueError(
            "Source sampling rate is unavailable; pass --source-sfreq explicitly."
        )
    return value


def _split_labels(partitions, *, n_items: int):
    np = _require_numpy()
    labels = np.full(n_items, "", dtype="U8")
    for name, indices in (
        ("train", partitions.train_indices),
        ("val", partitions.validation_indices),
        ("test", partitions.test_indices),
    ):
        labels[np.asarray(indices, dtype="int64")] = name
    if any(not str(value) for value in labels.tolist()):
        raise ValueError("Split protocol did not label every source row")
    return labels


def _item_ids(source_sha256: str, source_rows, trial_indices):
    np = _require_numpy()
    values = [
        hashlib.sha256(
            json.dumps(
                {
                    "source_cache_sha256": source_sha256,
                    "source_row_index": int(row),
                    "source_trial_index": int(trial),
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        for row, trial in zip(source_rows.tolist(), trial_indices.tolist(), strict=True)
    ]
    return np.asarray(values, dtype="U64")


def _token_payload_sha256(arrays: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in ("tokens", "token_lengths", "token_mask", "token_start_sec", "token_end_sec"):
        value = _require_numpy().ascontiguousarray(arrays[name])
        digest.update(name.encode("ascii"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(json.dumps(list(value.shape)).encode("ascii"))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _semantic_identity_sha256(arrays: Mapping[str, Any]) -> str:
    payload = [
        {
            "item_id": str(item),
            "split": str(split),
            "source_row_index": int(row),
            "source_trial_index": int(trial),
            "subject_id": str(subject),
            "session_id": str(session),
        }
        for item, split, row, trial, subject, session in zip(
            arrays["item_ids"].tolist(),
            arrays["split_labels"].tolist(),
            arrays["source_row_indices"].tolist(),
            arrays["source_trial_indices"].tolist(),
            arrays["subject_ids"].tolist(),
            arrays["session_ids"].tolist(),
            strict=True,
        )
    ]
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _array_descriptors(arrays: Mapping[str, Any]) -> dict[str, dict[str, object]]:
    return {
        name: {
            "shape": [int(value) for value in array.shape],
            "dtype": str(array.dtype),
        }
        for name, array in sorted(arrays.items())
    }


def _required_array_names() -> set[str]:
    return {
        "tokens",
        "token_lengths",
        "token_mask",
        "token_start_sec",
        "token_end_sec",
        "item_ids",
        "split_labels",
        "source_row_indices",
        "source_trial_indices",
        "source_input_lengths",
        "source_start_sec",
        "source_end_sec",
        "subject_ids",
        "session_ids",
        "source_channel_names",
        "source_channel_positions",
        "source_channel_position_mask",
    }


def _validate_projection_params(
    *,
    embedding_dim: int,
    kernel_size: int,
    stride: int,
    token_dtype: str,
    max_items: int,
    max_tokens_per_item: int,
    max_output_mb: float,
) -> None:
    if embedding_dim < 1 or embedding_dim > 4096:
        raise ValueError("embedding_dim must be between 1 and 4096")
    if kernel_size < 1 or stride < 1:
        raise ValueError("kernel_size and stride must be positive")
    _normalize_token_dtype(token_dtype)
    if max_items < 1 or max_tokens_per_item < 1:
        raise ValueError("item and token caps must be positive")
    if not math.isfinite(max_output_mb) or max_output_mb <= 0:
        raise ValueError("max_output_mb must be finite and positive")


def _normalize_token_dtype(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in SUPPORTED_TOKEN_DTYPES:
        raise ValueError(f"token_dtype must be one of: {', '.join(SUPPORTED_TOKEN_DTYPES)}")
    return normalized


def _validate_nonempty_text_vector(value, name: str) -> None:
    if value.ndim != 1 or any(not str(item).strip() for item in value.tolist()):
        raise NeuroTokenCacheSchemaError(f"{name} must be a nonempty text vector")


def _validate_unique_text_vector(value, name: str) -> None:
    _validate_nonempty_text_vector(value, name)
    rows = [str(item) for item in value.tolist()]
    if len(set(rows)) != len(rows):
        raise NeuroTokenCacheSchemaError(f"{name} must contain unique values")


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        scalar = value.item() if hasattr(value, "item") else value
        decoded = json.loads(str(scalar))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise NeuroTokenCacheSchemaError("Neurotoken metadata is not valid JSON") from exc
    if not isinstance(decoded, dict):
        raise NeuroTokenCacheSchemaError("Neurotoken metadata must decode to an object")
    return decoded


def _required_text(value: str, name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{name} must be nonempty")
    return normalized


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(char in "0123456789abcdef" for char in value.lower())


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (AttributeError, ImportError, OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("NeuroTokenCache requires NumPy: `pip install numpy`.") from exc
    return np
