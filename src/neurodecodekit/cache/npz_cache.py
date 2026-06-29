"""Small NPZ cache helpers.

NPZ is the v0 cache format because it is simple. Zarr should replace it for
larger real caches once the schema stabilizes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


CACHE_SCHEMA_NAME = "b2q-mini-cache"
CACHE_SCHEMA_VERSION = 0


class CacheSchemaError(ValueError):
    """Raised when an NPZ file does not match the B2Q-mini cache contract."""


@dataclass(frozen=True)
class CacheSummary:
    """Small serializable summary of a loaded B2Q-mini cache."""

    path: str
    bytes: int | None
    schema_name: str
    schema_version: int | None
    kind: str
    windows_shape: tuple[int, int, int]
    windows_dtype: str
    labels_shape: tuple[int, ...]
    labels_dtype: str
    n_events: int
    n_channels: int
    n_timepoints: int
    n_unique_labels: int
    arrays: dict[str, dict[str, object]]
    metadata_keys: list[str]
    source_files: dict[str, object]
    transformations: list[object]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LoadedCache:
    """Loaded cache arrays plus normalized metadata and summary."""

    path: str
    windows: Any
    labels: Any
    metadata: dict[str, Any]
    arrays: dict[str, Any]
    summary: CacheSummary

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "summary": self.summary.to_dict(),
            "metadata": self.metadata,
            "arrays": {
                key: {
                    "shape": tuple(int(dim) for dim in value.shape),
                    "dtype": str(value.dtype),
                }
                for key, value in self.arrays.items()
            },
        }


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("NPZ cache helpers require NumPy: `pip install numpy`.") from exc
    return np


def save_npz_cache(
    path: str | Path,
    *,
    windows,
    labels,
    metadata: dict[str, Any],
    extra_arrays: dict[str, Any] | None = None,
    metadata_sidecar: str | Path | None = None,
) -> None:
    """Save windows/labels/metadata to a compressed NPZ file.

    This is the canonical B2Q-mini cache writer. It validates the array
    contract and enriches metadata with schema, dimension, array, and
    transformation records so later loops can inspect the cache without
    knowing whether it came from synthetic data or a real FIF/MAT extraction.
    """

    np = _require_numpy()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    windows_array = np.asarray(windows)
    labels_array = np.asarray(labels)
    extra_arrays = extra_arrays or {}
    extra_arrays = {key: np.asarray(value) for key, value in extra_arrays.items()}

    _validate_cache_arrays(windows_array, labels_array, extra_arrays)
    normalized_metadata = _normalize_metadata(
        metadata,
        windows=windows_array,
        labels=labels_array,
        extra_arrays=extra_arrays,
    )
    arrays = {
        "windows": windows_array,
        "labels": labels_array,
        "metadata": json.dumps(normalized_metadata, sort_keys=True),
    }
    arrays.update(extra_arrays)
    np.savez_compressed(
        output,
        **arrays,
    )
    if metadata_sidecar is not None:
        write_cache_metadata_sidecar(output, metadata_sidecar)


def load_npz_cache(path: str | Path) -> LoadedCache:
    """Load and validate a compressed NPZ cache file."""

    np = _require_numpy()
    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise CacheSchemaError("NPZ cache is missing required `metadata` entry.")
        metadata = _decode_metadata(data["metadata"])
        if "windows" not in data.files:
            raise CacheSchemaError("NPZ cache is missing required `windows` array.")
        if "labels" not in data.files:
            raise CacheSchemaError("NPZ cache is missing required `labels` array.")

        windows = data["windows"].copy()
        labels = data["labels"].copy()
        arrays = {
            key: data[key].copy()
            for key in data.files
            if key not in {"windows", "labels", "metadata"}
        }
    _validate_cache_arrays(windows, labels, arrays)
    metadata = _normalize_metadata(
        metadata,
        windows=windows,
        labels=labels,
        extra_arrays=arrays,
    )
    summary = summarize_cache(
        path=cache_path,
        windows=windows,
        labels=labels,
        metadata=metadata,
        extra_arrays=arrays,
    )
    return LoadedCache(
        path=str(cache_path),
        windows=windows,
        labels=labels,
        metadata=metadata,
        arrays=arrays,
        summary=summary,
    )


def summarize_npz_cache(path: str | Path) -> CacheSummary:
    """Load a cache and return only the summary object."""

    return load_npz_cache(path).summary


def write_cache_metadata_sidecar(cache_path: str | Path, out: str | Path) -> None:
    """Write a JSON sidecar containing cache metadata and a compact summary."""

    loaded = load_npz_cache(cache_path)
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": loaded.summary.to_dict(),
        "metadata": loaded.metadata,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_cache(
    *,
    path: str | Path,
    windows: Any,
    labels: Any,
    metadata: dict[str, Any],
    extra_arrays: dict[str, Any],
) -> CacheSummary:
    """Create a serializable summary for already-loaded cache arrays."""

    schema = metadata.get("schema") or {}
    dimensions = metadata.get("dimensions") or {}
    warnings = list(metadata.get("warnings") or [])
    if schema.get("name") != CACHE_SCHEMA_NAME:
        warnings.append("legacy_or_missing_schema_name")
    if schema.get("version") != CACHE_SCHEMA_VERSION:
        warnings.append("legacy_or_missing_schema_version")
    source_files = metadata.get("source_files") or metadata.get("provenance", {}).get("source_files") or {}
    transformations = list(metadata.get("transformations") or [])
    arrays = _array_descriptors(windows, labels, extra_arrays)
    label_values = labels.tolist()
    if not isinstance(label_values, list):
        label_values = [label_values]
    return CacheSummary(
        path=str(Path(path)),
        bytes=_safe_stat_size(Path(path)),
        schema_name=str(schema.get("name") or "unknown"),
        schema_version=schema.get("version"),
        kind=str(metadata.get("kind") or metadata.get("cache_kind") or "unknown"),
        windows_shape=tuple(int(dim) for dim in windows.shape),
        windows_dtype=str(windows.dtype),
        labels_shape=tuple(int(dim) for dim in labels.shape),
        labels_dtype=str(labels.dtype),
        n_events=int(dimensions.get("n_events", windows.shape[0])),
        n_channels=int(dimensions.get("n_channels", windows.shape[1])),
        n_timepoints=int(dimensions.get("n_timepoints", windows.shape[2])),
        n_unique_labels=len(set(str(value) for value in label_values)),
        arrays=arrays,
        metadata_keys=sorted(metadata.keys()),
        source_files=source_files,
        transformations=transformations,
        warnings=warnings,
    )


def _normalize_metadata(
    metadata: dict[str, Any],
    *,
    windows: Any,
    labels: Any,
    extra_arrays: dict[str, Any],
) -> dict[str, Any]:
    normalized = dict(metadata or {})
    transformations = list(normalized.get("transformations") or [])
    if not transformations:
        transformations = [
            {
                "name": "unspecified_upstream_generation",
                "description": "Upstream cache producer did not provide transformation details.",
            }
        ]
    if not any(_transformation_name(item) == "npz_compressed_write" for item in transformations):
        transformations.append(
            {
                "name": "npz_compressed_write",
                "description": "Saved arrays with numpy.savez_compressed.",
            }
        )

    normalized["schema"] = {
        "name": CACHE_SCHEMA_NAME,
        "version": CACHE_SCHEMA_VERSION,
    }
    normalized["cache_schema_version"] = CACHE_SCHEMA_VERSION
    normalized["dimensions"] = {
        "n_events": int(windows.shape[0]),
        "n_channels": int(windows.shape[1]),
        "n_timepoints": int(windows.shape[2]),
    }
    normalized["arrays"] = _array_descriptors(windows, labels, extra_arrays)
    normalized["transformations"] = transformations
    normalized.setdefault("warnings", [])
    return normalized


def _validate_cache_arrays(windows: Any, labels: Any, extra_arrays: dict[str, Any]) -> None:
    if windows.ndim != 3:
        raise CacheSchemaError(
            "Expected `windows` with shape [events, channels, timepoints], "
            f"got {tuple(windows.shape)}."
        )
    if labels.ndim > 1:
        raise CacheSchemaError(f"Expected one-dimensional `labels`, got {tuple(labels.shape)}.")
    if len(labels) != int(windows.shape[0]):
        raise CacheSchemaError(
            "`labels` length must match number of windows: "
            f"{len(labels)} labels for {windows.shape[0]} windows."
        )

    event_length_arrays = {"event_start_sec", "event_source_index"}
    for name in event_length_arrays:
        if name in extra_arrays and len(extra_arrays[name]) != int(windows.shape[0]):
            raise CacheSchemaError(
                f"`{name}` length must match number of windows: "
                f"{len(extra_arrays[name])} values for {windows.shape[0]} windows."
            )
    if "channel_names" in extra_arrays and len(extra_arrays["channel_names"]) != int(windows.shape[1]):
        raise CacheSchemaError(
            "`channel_names` length must match number of channels: "
            f"{len(extra_arrays['channel_names'])} names for {windows.shape[1]} channels."
        )


def _array_descriptors(windows: Any, labels: Any, extra_arrays: dict[str, Any]) -> dict[str, dict[str, object]]:
    arrays = {
        "windows": _array_descriptor(windows),
        "labels": _array_descriptor(labels),
    }
    for key, value in sorted(extra_arrays.items()):
        arrays[key] = _array_descriptor(value)
    return arrays


def _array_descriptor(value: Any) -> dict[str, object]:
    return {
        "shape": tuple(int(dim) for dim in value.shape),
        "dtype": str(value.dtype),
    }


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        text = str(value.item())
    except AttributeError:
        text = str(value)
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise CacheSchemaError("NPZ cache metadata is not valid JSON.") from exc
    if not isinstance(payload, dict):
        raise CacheSchemaError("NPZ cache metadata must decode to a JSON object.")
    return payload


def _transformation_name(value: object) -> str:
    if isinstance(value, dict):
        return str(value.get("name") or "")
    return str(value)


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None
        for key in data.files:
            if key not in loaded:
                loaded[key] = data[key]
        return loaded
