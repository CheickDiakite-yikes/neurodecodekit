"""Versioned packed signal representations for semantic sentence caches."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.cache.sentence_npz import (
    SENTENCE_CACHE_SCHEMA_NAME,
    SENTENCE_CACHE_SCHEMA_VERSION,
    SentenceCacheSummary,
    load_sentence_npz_cache,
    summarize_sentence_cache,
    validate_sentence_cache_arrays,
    validate_sentence_cache_metadata,
)


REPRESENTATION_CACHE_SCHEMA_NAME = "b2q-signal-representation-cache"
REPRESENTATION_CACHE_SCHEMA_VERSION = 0
SUPPORTED_SIGNAL_ENCODINGS = ("float32", "float16", "bfloat16", "qint16", "qint8")
NON_SIGNAL_ARRAY_NAMES = (
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
)


class SignalRepresentationSchemaError(ValueError):
    """Raised when a packed signal representation violates its contract."""


@dataclass(frozen=True)
class SignalRepresentationSummary:
    """Compact shape, encoding, provenance, and resource summary."""

    path: str
    bytes: int | None
    schema_name: str
    schema_version: int | None
    encoding: str
    payload_shape: tuple[int, int, int]
    payload_dtype: str
    payload_bytes: int
    decoded_dtype: str
    bits_per_value: int
    source_cache_path: str
    source_cache_sha256: str | None
    source_cache_bytes: int | None
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class LoadedSignalRepresentation:
    """Decoded sentence-cache interface plus packed representation evidence."""

    path: str
    signal_payload: Any
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
    representation_metadata: dict[str, Any]
    summary: SentenceCacheSummary
    representation_summary: SignalRepresentationSummary


def encode_signal_payload(
    signals,
    encoding: str,
    *,
    clip_abs: float = 5.0,
    allow_clipping: bool = False,
) -> tuple[Any, dict[str, Any]]:
    """Encode finite signals into one explicit storage representation."""

    np = _require_numpy()
    normalized = normalize_signal_encoding(encoding)
    source = np.asarray(signals)
    if source.ndim != 3:
        raise ValueError(f"signals must be 3D, got {source.shape}")
    if not np.issubdtype(source.dtype, np.floating):
        raise ValueError(f"signals must use a floating dtype, got {source.dtype}")
    if not np.isfinite(source).all():
        raise ValueError("signals contain non-finite values")
    values = np.ascontiguousarray(source, dtype="float32")

    config: dict[str, Any] = {
        "name": normalized,
        "source_dtype": str(source.dtype),
        "decoded_dtype": "float32",
        "rounding": None,
        "clip_abs": None,
        "scale": None,
        "zero_point": None,
        "source_values_outside_clip_count": 0,
        "source_values_at_or_outside_clip_count": 0,
        "payload_saturation_count": 0,
        "clipping_allowed": bool(allow_clipping),
    }
    if normalized == "float32":
        payload = values.copy()
        config.update(payload_dtype="float32", bits_per_value=32, rounding="float32_cast")
    elif normalized == "float16":
        payload = values.astype("float16")
        config.update(
            payload_dtype="float16",
            bits_per_value=16,
            rounding="ieee_float16_round_to_nearest",
        )
    elif normalized == "bfloat16":
        source_bits = values.view("uint32")
        least_retained_bit = (source_bits >> 16) & 1
        rounded = source_bits + np.uint32(0x7FFF) + least_retained_bit
        payload = (rounded >> 16).astype("uint16")
        config.update(
            payload_dtype="uint16",
            bits_per_value=16,
            rounding="bfloat16_round_to_nearest_even",
            packed_format="upper_16_bits_of_ieee754_float32",
        )
    else:
        if not np.isfinite(clip_abs) or clip_abs <= 0:
            raise ValueError("clip_abs must be finite and positive for integer encodings")
        qmax = 32767 if normalized == "qint16" else 127
        payload_dtype = "int16" if normalized == "qint16" else "int8"
        outside_count = int(np.count_nonzero(np.abs(values) > clip_abs))
        boundary_count = int(np.count_nonzero(np.abs(values) >= clip_abs))
        if outside_count and not allow_clipping:
            raise ValueError(
                f"{outside_count} source values exceed fixed clip_abs={clip_abs:g}; "
                "refusing implicit clipping"
            )
        scale = float(clip_abs) / qmax
        clipped = np.clip(values, -float(clip_abs), float(clip_abs))
        payload = np.rint(clipped / scale).clip(-qmax, qmax).astype(payload_dtype)
        config.update(
            payload_dtype=payload_dtype,
            bits_per_value=16 if normalized == "qint16" else 8,
            rounding="numpy_rint_ties_to_even",
            quantization="symmetric_per_tensor_fixed_range",
            clip_abs=float(clip_abs),
            scale=scale,
            zero_point=0,
            qmin=-qmax,
            qmax=qmax,
            source_values_outside_clip_count=outside_count,
            source_values_at_or_outside_clip_count=boundary_count,
            payload_saturation_count=int(np.count_nonzero(np.abs(payload.astype("int32")) == qmax)),
        )
    return np.ascontiguousarray(payload), config


def decode_signal_payload(payload, encoding_metadata: dict[str, Any]):
    """Decode one validated payload to float32 semantic signals."""

    np = _require_numpy()
    config = dict(encoding_metadata or {})
    encoding = normalize_signal_encoding(str(config.get("name") or ""))
    packed = np.asarray(payload)
    expected_dtype = str(config.get("payload_dtype") or "")
    if str(packed.dtype) != expected_dtype:
        raise SignalRepresentationSchemaError(
            f"Payload dtype {packed.dtype} does not match metadata {expected_dtype!r}."
        )
    if packed.ndim != 3:
        raise SignalRepresentationSchemaError(
            f"signal_payload must be [sentences, channels, timepoints], got {packed.shape}"
        )

    if encoding in {"float32", "float16"}:
        decoded = packed.astype("float32")
    elif encoding == "bfloat16":
        if packed.dtype != np.dtype("uint16"):
            raise SignalRepresentationSchemaError("bfloat16 payload must use uint16 storage.")
        expanded = np.left_shift(packed.astype("uint32"), np.uint32(16))
        decoded = np.ascontiguousarray(expanded).view("float32")
    else:
        scale = config.get("scale")
        zero_point = config.get("zero_point")
        if not isinstance(scale, (int, float)) or not np.isfinite(scale) or scale <= 0:
            raise SignalRepresentationSchemaError("Integer encoding scale must be finite and positive.")
        if zero_point != 0:
            raise SignalRepresentationSchemaError("Only symmetric zero_point=0 is supported.")
        decoded = (packed.astype("float32") - float(zero_point)) * float(scale)
    if not np.isfinite(decoded).all():
        raise SignalRepresentationSchemaError("Decoded signals contain non-finite values.")
    return np.ascontiguousarray(decoded, dtype="float32")


def save_signal_representation_cache(
    path: str | Path,
    *,
    source_cache,
    encoding: str,
    clip_abs: float = 5.0,
    allow_clipping: bool = False,
    source_sha256: str | None = None,
    metadata_sidecar: str | Path | None = None,
) -> SignalRepresentationSummary:
    """Encode and save one representation from a validated sentence cache."""

    payload, encoding_metadata = encode_signal_payload(
        source_cache.signals,
        encoding,
        clip_abs=clip_abs,
        allow_clipping=allow_clipping,
    )
    return write_signal_representation_cache(
        path,
        source_cache=source_cache,
        signal_payload=payload,
        encoding_metadata=encoding_metadata,
        source_sha256=source_sha256,
        metadata_sidecar=metadata_sidecar,
    )


def write_signal_representation_cache(
    path: str | Path,
    *,
    source_cache,
    signal_payload,
    encoding_metadata: dict[str, Any],
    source_sha256: str | None = None,
    metadata_sidecar: str | Path | None = None,
) -> SignalRepresentationSummary:
    """Write a pre-encoded payload while preserving every non-signal array exactly."""

    np = _require_numpy()
    output = Path(path)
    payload = np.ascontiguousarray(signal_payload)
    decoded = decode_signal_payload(payload, encoding_metadata)
    non_signal = {
        name: np.asarray(getattr(source_cache, name)).copy() for name in NON_SIGNAL_ARRAY_NAMES
    }
    semantic_arrays = {"signals": decoded, **non_signal}
    validate_sentence_cache_arrays(semantic_arrays)
    semantic_metadata = dict(source_cache.metadata)
    validate_sentence_cache_metadata(semantic_metadata)
    if tuple(decoded.shape) != tuple(source_cache.signals.shape):
        raise ValueError("Decoded representation shape does not match source signals.")

    source_path = Path(str(source_cache.path))
    if source_sha256 is None and source_path.is_file():
        source_sha256 = file_sha256(source_path)
    representation_metadata = _build_representation_metadata(
        output=output,
        source_cache=source_cache,
        source_sha256=source_sha256,
        signal_payload=payload,
        encoding_metadata=encoding_metadata,
        non_signal=non_signal,
        semantic_metadata=semantic_metadata,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        signal_payload=payload,
        **non_signal,
        metadata=json.dumps(representation_metadata, sort_keys=True),
    )
    loaded = load_signal_representation_cache(output)
    if metadata_sidecar is not None:
        write_signal_representation_metadata_sidecar(output, metadata_sidecar)
    return loaded.representation_summary


def load_signal_representation_cache(path: str | Path) -> LoadedSignalRepresentation:
    """Load, decode, and validate one packed representation cache."""

    np = _require_numpy()
    cache_path = Path(path)
    required = {"signal_payload", "metadata", *NON_SIGNAL_ARRAY_NAMES}
    with np.load(cache_path, allow_pickle=False) as data:
        missing = sorted(required - set(data.files))
        if missing:
            raise SignalRepresentationSchemaError(
                f"Representation cache is missing arrays: {missing}"
            )
        signal_payload = data["signal_payload"].copy()
        non_signal = {name: data[name].copy() for name in NON_SIGNAL_ARRAY_NAMES}
        representation_metadata = _decode_metadata(data["metadata"])

    _validate_representation_metadata(representation_metadata)
    encoding_metadata = representation_metadata["storage"]["encoding"]
    expected_shape = tuple(
        int(value) for value in representation_metadata["dimensions"]["signals_shape"]
    )
    if tuple(signal_payload.shape) != expected_shape:
        raise SignalRepresentationSchemaError(
            f"Payload shape {signal_payload.shape} does not match metadata {expected_shape}."
        )
    signals = decode_signal_payload(signal_payload, encoding_metadata)
    arrays = {"signals": signals, **non_signal}
    validate_sentence_cache_arrays(arrays)

    semantic_metadata = representation_metadata.get("semantic_metadata")
    if not isinstance(semantic_metadata, dict):
        raise SignalRepresentationSchemaError("semantic_metadata must be an object.")
    validate_sentence_cache_metadata(semantic_metadata)
    summary = summarize_sentence_cache(
        cache_path,
        arrays=arrays,
        metadata=semantic_metadata,
    )
    source = representation_metadata["source_cache"]
    warnings = list(representation_metadata.get("warnings") or [])
    representation_summary = SignalRepresentationSummary(
        path=str(cache_path),
        bytes=_safe_stat_size(cache_path),
        schema_name=REPRESENTATION_CACHE_SCHEMA_NAME,
        schema_version=REPRESENTATION_CACHE_SCHEMA_VERSION,
        encoding=str(encoding_metadata["name"]),
        payload_shape=tuple(int(value) for value in signal_payload.shape),
        payload_dtype=str(signal_payload.dtype),
        payload_bytes=int(signal_payload.nbytes),
        decoded_dtype=str(signals.dtype),
        bits_per_value=int(encoding_metadata["bits_per_value"]),
        source_cache_path=str(source.get("path") or ""),
        source_cache_sha256=source.get("sha256"),
        source_cache_bytes=source.get("bytes"),
        warnings=warnings,
    )
    return LoadedSignalRepresentation(
        path=str(cache_path),
        signal_payload=signal_payload,
        signals=signals,
        metadata=semantic_metadata,
        representation_metadata=representation_metadata,
        summary=summary,
        representation_summary=representation_summary,
        **non_signal,
    )


def load_sentence_cache_auto(path: str | Path):
    """Load either standard float sentence NPZ or a packed representation NPZ."""

    np = _require_numpy()
    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise SignalRepresentationSchemaError("Cache is missing metadata.")
        metadata = _decode_metadata(data["metadata"])
    schema_name = str((metadata.get("schema") or {}).get("name") or "")
    if schema_name == SENTENCE_CACHE_SCHEMA_NAME:
        return load_sentence_npz_cache(cache_path)
    if schema_name == REPRESENTATION_CACHE_SCHEMA_NAME:
        return load_signal_representation_cache(cache_path)
    raise SignalRepresentationSchemaError(f"Unsupported cache schema name: {schema_name!r}")


def write_signal_representation_metadata_sidecar(
    cache_path: str | Path,
    out: str | Path,
) -> None:
    """Write an inspectable JSON sidecar without duplicating signal values."""

    loaded = load_signal_representation_cache(cache_path)
    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "representation_summary": loaded.representation_summary.to_dict(),
        "semantic_summary": loaded.summary.to_dict(),
        "representation_metadata": loaded.representation_metadata,
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def normalize_signal_encoding(value: str) -> str:
    normalized = str(value).strip().lower()
    if normalized not in SUPPORTED_SIGNAL_ENCODINGS:
        raise ValueError(
            f"Unsupported signal encoding {value!r}; choose from {SUPPORTED_SIGNAL_ENCODINGS}."
        )
    return normalized


def array_sha256(array) -> str:
    """Hash array dtype, shape, and exact contiguous bytes."""

    np = _require_numpy()
    value = np.ascontiguousarray(array)
    digest = hashlib.sha256()
    digest.update(str(value.dtype).encode("utf-8"))
    digest.update(json.dumps(list(value.shape), separators=(",", ":")).encode("utf-8"))
    digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _build_representation_metadata(
    *,
    output: Path,
    source_cache,
    source_sha256: str | None,
    signal_payload,
    encoding_metadata: dict[str, Any],
    non_signal: dict[str, Any],
    semantic_metadata: dict[str, Any],
) -> dict[str, Any]:
    encoding = str(encoding_metadata["name"])
    warnings = [
        "representation_cache_decodes_to_float32_before_model_input",
        "representation_fidelity_is_not_retained_decoder_accuracy",
        "single_cache_representation_is_not_a_generalization_test",
    ]
    if encoding.startswith("qint"):
        warnings.extend(
            [
                "integer_signal_storage_is_not_integer_only_model_inference",
                "fixed_range_uses_existing_robust_scale_clamp_not_data_fit_calibration",
            ]
        )
    if encoding == "bfloat16":
        warnings.append("official_v2_bf16_training_does_not_imply_bf16_input_cache_equivalence")
    arrays = {"signal_payload": signal_payload, **non_signal}
    return {
        "schema": {
            "name": REPRESENTATION_CACHE_SCHEMA_NAME,
            "version": REPRESENTATION_CACHE_SCHEMA_VERSION,
        },
        "kind": "packed_sentence_signal_representation",
        "semantic_contract": {
            "name": SENTENCE_CACHE_SCHEMA_NAME,
            "version": SENTENCE_CACHE_SCHEMA_VERSION,
            "decoded_signals_dtype": "float32",
        },
        "source_cache": {
            "path": str(source_cache.path),
            "bytes": source_cache.summary.bytes,
            "sha256": source_sha256,
            "signals_dtype": str(source_cache.signals.dtype),
            "signals_shape": [int(value) for value in source_cache.signals.shape],
            "semantic_metadata_sha256": _json_sha256(semantic_metadata),
        },
        "output_path": str(output),
        "storage": {
            "container": "numpy_npz",
            "compression": "zip_deflated",
            "pickle_required": False,
            "encoding": dict(encoding_metadata),
        },
        "dimensions": {
            "signals_shape": [int(value) for value in signal_payload.shape],
            "n_values": int(signal_payload.size),
        },
        "arrays": {
            name: {
                "shape": [int(value) for value in array.shape],
                "dtype": str(array.dtype),
            }
            for name, array in sorted(arrays.items())
        },
        "semantic_metadata": semantic_metadata,
        "warnings": warnings,
    }


def _validate_representation_metadata(metadata: dict[str, Any]) -> None:
    schema = metadata.get("schema") or {}
    if schema.get("name") != REPRESENTATION_CACHE_SCHEMA_NAME:
        raise SignalRepresentationSchemaError(
            f"Unexpected representation schema name: {schema.get('name')!r}"
        )
    if schema.get("version") != REPRESENTATION_CACHE_SCHEMA_VERSION:
        raise SignalRepresentationSchemaError(
            f"Unsupported representation schema version: {schema.get('version')!r}"
        )
    semantic = metadata.get("semantic_contract") or {}
    if semantic.get("name") != SENTENCE_CACHE_SCHEMA_NAME:
        raise SignalRepresentationSchemaError("Representation semantic contract name is invalid.")
    if semantic.get("version") != SENTENCE_CACHE_SCHEMA_VERSION:
        raise SignalRepresentationSchemaError("Representation semantic contract version is invalid.")
    storage = metadata.get("storage")
    if not isinstance(storage, dict) or not isinstance(storage.get("encoding"), dict):
        raise SignalRepresentationSchemaError("Representation storage encoding is missing.")
    normalize_signal_encoding(str(storage["encoding"].get("name") or ""))
    dimensions = metadata.get("dimensions")
    if not isinstance(dimensions, dict) or not isinstance(dimensions.get("signals_shape"), list):
        raise SignalRepresentationSchemaError("Representation signal dimensions are missing.")
    source = metadata.get("source_cache")
    if not isinstance(source, dict):
        raise SignalRepresentationSchemaError("Representation source_cache provenance is missing.")


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        scalar = value.item() if hasattr(value, "item") else value
        decoded = json.loads(str(scalar))
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise SignalRepresentationSchemaError("Cache metadata is not valid JSON.") from exc
    if not isinstance(decoded, dict):
        raise SignalRepresentationSchemaError("Cache metadata must decode to an object.")
    return decoded


def _json_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Packed signal representations require NumPy: `pip install numpy`."
        ) from exc
    return np
