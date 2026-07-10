"""Inspectable NPZ contract for variable-length continuous sentence signals."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.preprocess.ctc_text import (
    CTC_VOCAB,
    decode_ctc_target,
    minimum_ctc_input_steps,
    normalize_ctc_text,
)


SENTENCE_CACHE_SCHEMA_NAME = "b2q-sentence-cache"
SENTENCE_CACHE_SCHEMA_VERSION = 0


class SentenceCacheSchemaError(ValueError):
    """Raised when a sentence cache violates the CTC data contract."""


@dataclass(frozen=True)
class SentenceCacheSummary:
    """Compact resource and shape summary for a sentence cache."""

    path: str
    bytes: int | None
    schema_name: str
    schema_version: int | None
    kind: str
    signals_shape: tuple[int, int, int]
    signals_dtype: str
    n_sentences: int
    n_channels: int
    max_timepoints: int
    total_valid_timepoints: int
    padding_fraction: float
    min_input_length: int
    max_input_length: int
    min_target_length: int
    max_target_length: int
    arrays: dict[str, dict[str, object]]
    source_files: dict[str, object]
    transformations: list[object]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LoadedSentenceCache:
    """Validated sentence-cache arrays plus metadata."""

    path: str
    signals: Any
    input_lengths: Any
    target_token_ids: Any
    target_lengths: Any
    target_texts: Any
    reference_texts: Any
    mat_response_texts: Any
    trial_indices: Any
    sentence_start_sec: Any
    sentence_end_sec: Any
    channel_names: Any
    metadata: dict[str, Any]
    summary: SentenceCacheSummary


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Sentence NPZ caches require NumPy: `pip install numpy`.") from exc
    return np


def save_sentence_npz_cache(
    path: str | Path,
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    target_texts,
    reference_texts,
    mat_response_texts,
    trial_indices,
    sentence_start_sec,
    sentence_end_sec,
    channel_names,
    metadata: dict[str, Any],
    metadata_sidecar: str | Path | None = None,
) -> None:
    """Validate and save padded continuous signals and variable-length CTC targets."""

    np = _require_numpy()
    arrays = {
        "signals": np.asarray(signals),
        "input_lengths": np.asarray(input_lengths),
        "target_token_ids": np.asarray(target_token_ids),
        "target_lengths": np.asarray(target_lengths),
        "target_texts": np.asarray(target_texts),
        "reference_texts": np.asarray(reference_texts),
        "mat_response_texts": np.asarray(mat_response_texts),
        "trial_indices": np.asarray(trial_indices),
        "sentence_start_sec": np.asarray(sentence_start_sec),
        "sentence_end_sec": np.asarray(sentence_end_sec),
        "channel_names": np.asarray(channel_names),
    }
    _validate_sentence_arrays(arrays)
    normalized_metadata = _normalize_metadata(metadata, arrays)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        **arrays,
        metadata=json.dumps(normalized_metadata, sort_keys=True),
    )
    if metadata_sidecar is not None:
        write_sentence_cache_metadata_sidecar(output, metadata_sidecar)


def load_sentence_npz_cache(path: str | Path) -> LoadedSentenceCache:
    """Load and validate one sentence cache."""

    np = _require_numpy()
    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        required = _required_array_names()
        missing = sorted(required - set(data.files))
        if "metadata" not in data.files:
            missing.append("metadata")
        if missing:
            raise SentenceCacheSchemaError(f"Sentence cache is missing arrays: {missing}")
        arrays = {name: data[name].copy() for name in required}
        metadata = _decode_metadata(data["metadata"])
    _validate_sentence_arrays(arrays)
    _validate_metadata_schema(metadata)
    metadata = _normalize_metadata(metadata, arrays)
    summary = summarize_sentence_cache(cache_path, arrays=arrays, metadata=metadata)
    return LoadedSentenceCache(
        path=str(cache_path),
        metadata=metadata,
        summary=summary,
        **arrays,
    )


def summarize_sentence_npz_cache(path: str | Path) -> SentenceCacheSummary:
    return load_sentence_npz_cache(path).summary


def validate_sentence_cache_arrays(arrays: dict[str, Any]) -> None:
    """Validate arrays against the semantic sentence-cache contract."""

    _validate_sentence_arrays(arrays)


def validate_sentence_cache_metadata(metadata: dict[str, Any]) -> None:
    """Validate the schema declaration for semantic sentence-cache metadata."""

    _validate_metadata_schema(metadata)


def write_sentence_cache_metadata_sidecar(cache_path: str | Path, out: str | Path) -> None:
    loaded = load_sentence_npz_cache(cache_path)
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"summary": loaded.summary.to_dict(), "metadata": loaded.metadata}
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_sentence_cache(
    path: str | Path,
    *,
    arrays: dict[str, Any],
    metadata: dict[str, Any],
) -> SentenceCacheSummary:
    signals = arrays["signals"]
    input_lengths = arrays["input_lengths"]
    target_lengths = arrays["target_lengths"]
    total_valid = int(input_lengths.sum())
    total_padded = int(signals.shape[0] * signals.shape[2])
    schema = metadata.get("schema") or {}
    warnings = list(metadata.get("warnings") or [])
    if schema.get("name") != SENTENCE_CACHE_SCHEMA_NAME:
        warnings.append("legacy_or_missing_sentence_schema_name")
    if schema.get("version") != SENTENCE_CACHE_SCHEMA_VERSION:
        warnings.append("legacy_or_missing_sentence_schema_version")
    return SentenceCacheSummary(
        path=str(Path(path)),
        bytes=_safe_stat_size(Path(path)),
        schema_name=str(schema.get("name") or "unknown"),
        schema_version=schema.get("version"),
        kind=str(metadata.get("kind") or "unknown"),
        signals_shape=tuple(int(value) for value in signals.shape),
        signals_dtype=str(signals.dtype),
        n_sentences=int(signals.shape[0]),
        n_channels=int(signals.shape[1]),
        max_timepoints=int(signals.shape[2]),
        total_valid_timepoints=total_valid,
        padding_fraction=(1.0 - total_valid / total_padded) if total_padded else 0.0,
        min_input_length=int(input_lengths.min()),
        max_input_length=int(input_lengths.max()),
        min_target_length=int(target_lengths.min()),
        max_target_length=int(target_lengths.max()),
        arrays=_array_descriptors(arrays),
        source_files=dict(metadata.get("source_files") or {}),
        transformations=list(metadata.get("transformations") or []),
        warnings=warnings,
    )


def _validate_sentence_arrays(arrays: dict[str, Any]) -> None:
    np = _require_numpy()
    signals = arrays["signals"]
    if signals.ndim != 3:
        raise SentenceCacheSchemaError(
            f"signals must be [sentences, channels, timepoints], got {signals.shape}"
        )
    if signals.shape[0] < 1 or signals.shape[1] < 1 or signals.shape[2] < 1:
        raise SentenceCacheSchemaError("signals dimensions must all be nonzero.")
    if not np.issubdtype(signals.dtype, np.floating):
        raise SentenceCacheSchemaError(f"signals must use a floating dtype, got {signals.dtype}")
    if not np.isfinite(signals).all():
        raise SentenceCacheSchemaError("signals contain non-finite values.")

    n_sentences, n_channels, max_timepoints = signals.shape
    vector_names = {
        "input_lengths",
        "target_lengths",
        "target_texts",
        "reference_texts",
        "mat_response_texts",
        "trial_indices",
        "sentence_start_sec",
        "sentence_end_sec",
    }
    for name in vector_names:
        value = arrays[name]
        if value.ndim != 1 or len(value) != n_sentences:
            raise SentenceCacheSchemaError(
                f"{name} must be a vector with {n_sentences} rows, got {value.shape}"
            )
    if arrays["channel_names"].ndim != 1 or len(arrays["channel_names"]) != n_channels:
        raise SentenceCacheSchemaError(
            f"channel_names must contain {n_channels} rows, got {arrays['channel_names'].shape}"
        )

    target_ids = arrays["target_token_ids"]
    if target_ids.ndim != 2 or target_ids.shape[0] != n_sentences:
        raise SentenceCacheSchemaError(
            "target_token_ids must be [sentences, max_target_length], got "
            f"{target_ids.shape}"
        )
    if not np.issubdtype(target_ids.dtype, np.integer):
        raise SentenceCacheSchemaError("target_token_ids must use an integer dtype.")
    for name in ("input_lengths", "target_lengths", "trial_indices"):
        if not np.issubdtype(arrays[name].dtype, np.integer):
            raise SentenceCacheSchemaError(f"{name} must use an integer dtype.")

    input_lengths = arrays["input_lengths"].astype("int64", copy=False)
    target_lengths = arrays["target_lengths"].astype("int64", copy=False)
    if (input_lengths < 1).any() or (input_lengths > max_timepoints).any():
        raise SentenceCacheSchemaError("input_lengths must be within the padded signal width.")
    if (target_lengths < 1).any() or (target_lengths > target_ids.shape[1]).any():
        raise SentenceCacheSchemaError("target_lengths must be within target_token_ids width.")
    if len(set(int(value) for value in arrays["trial_indices"].tolist())) != n_sentences:
        raise SentenceCacheSchemaError("trial_indices must be unique.")
    if not np.isfinite(arrays["sentence_start_sec"]).all() or not np.isfinite(
        arrays["sentence_end_sec"]
    ).all():
        raise SentenceCacheSchemaError("sentence timing arrays must be finite.")
    if (arrays["sentence_end_sec"] <= arrays["sentence_start_sec"]).any():
        raise SentenceCacheSchemaError("Each sentence end time must be after its start time.")
    channel_names = [str(value) for value in arrays["channel_names"].tolist()]
    if any(not value for value in channel_names) or len(set(channel_names)) != n_channels:
        raise SentenceCacheSchemaError("channel_names must be nonempty and unique.")

    for row_index in range(n_sentences):
        input_length = int(input_lengths[row_index])
        target_length = int(target_lengths[row_index])
        valid_ids = [int(value) for value in target_ids[row_index, :target_length].tolist()]
        padded_ids = target_ids[row_index, target_length:]
        if any(value <= 0 or value >= len(CTC_VOCAB) for value in valid_ids):
            raise SentenceCacheSchemaError(
                f"row {row_index} target IDs must exclude blank and stay inside the vocabulary."
            )
        if padded_ids.size and (padded_ids != 0).any():
            raise SentenceCacheSchemaError(f"row {row_index} target padding must use blank zero.")
        if input_length < minimum_ctc_input_steps(valid_ids):
            raise SentenceCacheSchemaError(
                f"row {row_index} has too few input steps for its CTC target."
            )
        decoded = decode_ctc_target(valid_ids)
        try:
            target_text = normalize_ctc_text(str(arrays["target_texts"][row_index]))
        except ValueError as exc:
            raise SentenceCacheSchemaError(str(exc)) from exc
        if decoded != target_text:
            raise SentenceCacheSchemaError(
                f"row {row_index} target text does not match target_token_ids: "
                f"{target_text!r} vs {decoded!r}"
            )
        if input_length < max_timepoints and np.any(signals[row_index, :, input_length:] != 0):
            raise SentenceCacheSchemaError(f"row {row_index} signal padding must be zero.")


def _normalize_metadata(metadata: dict[str, Any], arrays: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(metadata or {})
    normalized["schema"] = {
        "name": SENTENCE_CACHE_SCHEMA_NAME,
        "version": SENTENCE_CACHE_SCHEMA_VERSION,
    }
    normalized["dimensions"] = {
        "n_sentences": int(arrays["signals"].shape[0]),
        "n_channels": int(arrays["signals"].shape[1]),
        "max_timepoints": int(arrays["signals"].shape[2]),
        "max_target_length": int(arrays["target_token_ids"].shape[1]),
    }
    normalized["arrays"] = _array_descriptors(arrays)
    normalized["ctc_vocabulary"] = {
        "blank_id": 0,
        "tokens": list(CTC_VOCAB),
        "target_case": "uppercase",
    }
    transformations = list(normalized.get("transformations") or [])
    if not any(
        isinstance(item, dict) and item.get("name") == "npz_compressed_write"
        for item in transformations
    ):
        transformations.append(
            {
                "name": "npz_compressed_write",
                "description": "Saved sentence arrays with numpy.savez_compressed.",
            }
        )
    normalized["transformations"] = transformations
    normalized["warnings"] = list(dict.fromkeys(normalized.get("warnings") or []))
    return normalized


def _validate_metadata_schema(metadata: dict[str, Any]) -> None:
    schema = metadata.get("schema") or {}
    if schema.get("name") != SENTENCE_CACHE_SCHEMA_NAME:
        raise SentenceCacheSchemaError(
            f"Unexpected sentence cache schema name: {schema.get('name')!r}"
        )
    if schema.get("version") != SENTENCE_CACHE_SCHEMA_VERSION:
        raise SentenceCacheSchemaError(
            f"Unsupported sentence cache schema version: {schema.get('version')!r}"
        )


def _array_descriptors(arrays: dict[str, Any]) -> dict[str, dict[str, object]]:
    return {
        name: {
            "shape": [int(value) for value in array.shape],
            "dtype": str(array.dtype),
        }
        for name, array in sorted(arrays.items())
    }


def _required_array_names() -> set[str]:
    return {
        "signals",
        "input_lengths",
        "target_token_ids",
        "target_lengths",
        "target_texts",
        "reference_texts",
        "mat_response_texts",
        "trial_indices",
        "sentence_start_sec",
        "sentence_end_sec",
        "channel_names",
    }


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        scalar = value.item() if hasattr(value, "item") else value
        decoded = json.loads(str(scalar))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SentenceCacheSchemaError("Sentence cache metadata is not valid JSON.") from exc
    if not isinstance(decoded, dict):
        raise SentenceCacheSchemaError("Sentence cache metadata must decode to an object.")
    return decoded


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None
