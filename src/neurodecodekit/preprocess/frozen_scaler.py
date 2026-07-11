"""Apply a train-fitted robust scaler to an independent sentence cache."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from neurodecodekit.cache.sentence_npz import (
    load_sentence_npz_cache,
    save_sentence_npz_cache,
)
from neurodecodekit.cache.signal_representation import file_sha256
from neurodecodekit.preprocess.sentence_extraction import (
    apply_robust_scaler_to_padded,
    scaler_array_sha256,
)


PREPROCESSING_KEYS = (
    "sfreq",
    "pre_context_sec",
    "post_context_sec",
    "picks",
    "max_channels",
    "stim_channel",
    "l_freq",
    "h_freq",
    "notch_freq",
)


@dataclass(frozen=True)
class FrozenScalerSummary:
    """Resource and provenance summary for one frozen-scaler transform."""

    source_cache: str
    source_cache_sha256: str
    fit_cache: str
    fit_cache_sha256: str
    output_cache: str
    output_cache_sha256: str
    output_bytes: int
    signals_shape: tuple[int, int, int]
    center_sha256: str
    scale_sha256: str
    clamp: float | None
    runtime_sec: float
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def apply_frozen_train_scaler_to_cache(
    *,
    source_cache_path: str | Path,
    fit_cache_path: str | Path,
    output_path: str | Path,
    overwrite: bool = False,
) -> FrozenScalerSummary:
    """Scale an independent cache with statistics fitted on another cache's train rows."""

    source_path = Path(source_cache_path)
    fit_path = Path(fit_cache_path)
    output = Path(output_path)
    if source_path.resolve() == fit_path.resolve():
        raise ValueError("source_cache and fit_cache must be different files.")
    if output.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {output}. Pass overwrite=True to replace it."
        )

    started_at = time.perf_counter()
    source = load_sentence_npz_cache(source_path)
    fit = load_sentence_npz_cache(fit_path)
    if source.channel_names.tolist() != fit.channel_names.tolist():
        raise ValueError("Source and fit caches must have identical channel names and order.")

    source_scaler = _find_scaler_transform(source.metadata)
    if source_scaler.get("enabled") is not False:
        raise ValueError("Source cache must explicitly declare robust scaling disabled.")
    fit_scaler = _find_scaler_transform(fit.metadata)
    _validate_train_fit_scaler(fit_scaler)
    _validate_preprocessing_match(source.metadata, fit.metadata)

    np = _require_numpy()
    statistics = fit_scaler["statistics"]
    center = np.asarray(statistics["center"], dtype="float32")
    scale = np.asarray(statistics["scale"], dtype="float32")
    center_sha256 = scaler_array_sha256(center)
    scale_sha256 = scaler_array_sha256(scale)
    if center_sha256 != statistics["center_sha256"]:
        raise ValueError("Frozen scaler center hash does not match fit-cache metadata.")
    if scale_sha256 != statistics["scale_sha256"]:
        raise ValueError("Frozen scaler scale hash does not match fit-cache metadata.")
    clamp_value = fit_scaler.get("clamp")
    clamp = float(clamp_value) if clamp_value is not None else None
    scaled = apply_robust_scaler_to_padded(
        source.signals,
        source.input_lengths,
        center=center,
        scale=scale,
        clamp=clamp,
    )

    source_sha256 = file_sha256(source_path)
    fit_sha256 = file_sha256(fit_path)
    provenance = {
        "source_cache": {
            "path": str(source_path),
            "sha256": source_sha256,
            "bytes": source.summary.bytes,
        },
        "fit_cache": {
            "path": str(fit_path),
            "sha256": fit_sha256,
            "bytes": fit.summary.bytes,
        },
        "fit_scope": fit_scaler["fit_scope"],
        "fit_split": fit_scaler["fit_split"],
        "split_protocol_config_sha256": fit_scaler["split_protocol_config_sha256"],
        "semantic_membership_sha256": fit_scaler["semantic_membership_sha256"],
        "center_sha256": center_sha256,
        "scale_sha256": scale_sha256,
        "n_fit_rows": int(statistics["n_fit_rows"]),
        "clamp": clamp,
        "preprocessing_signature": _preprocessing_signature(source.metadata),
    }
    metadata = json.loads(json.dumps(source.metadata))
    metadata["kind"] = f"{source.metadata.get('kind', 'sentence_cache')}_frozen_train_scaled"
    metadata["transformations"] = [
        *list(metadata.get("transformations") or []),
        {
            "name": "frozen_train_cache_robust_scaler",
            "description": (
                "Applied channel statistics fitted only on the independent fit cache's "
                "training rows; source rows did not influence the scaler."
            ),
            "params": provenance,
        },
    ]
    metadata["frozen_scaler"] = provenance
    warnings = [
        *list(metadata.get("warnings") or []),
        "robust_scaler_applied_from_independent_train_cache",
        "source_cache_rows_not_used_to_fit_scaler",
    ]
    metadata["warnings"] = list(dict.fromkeys(warnings))
    save_sentence_npz_cache(
        output,
        signals=scaled,
        input_lengths=source.input_lengths,
        target_token_ids=source.target_token_ids,
        target_lengths=source.target_lengths,
        target_texts=source.target_texts,
        reference_texts=source.reference_texts,
        mat_response_texts=source.mat_response_texts,
        trial_indices=source.trial_indices,
        sentence_start_sec=source.sentence_start_sec,
        sentence_end_sec=source.sentence_end_sec,
        channel_names=source.channel_names,
        metadata=metadata,
    )
    output_sha256 = file_sha256(output)
    return FrozenScalerSummary(
        source_cache=str(source_path),
        source_cache_sha256=source_sha256,
        fit_cache=str(fit_path),
        fit_cache_sha256=fit_sha256,
        output_cache=str(output),
        output_cache_sha256=output_sha256,
        output_bytes=int(output.stat().st_size),
        signals_shape=tuple(int(value) for value in scaled.shape),
        center_sha256=center_sha256,
        scale_sha256=scale_sha256,
        clamp=clamp,
        runtime_sec=round(time.perf_counter() - started_at, 6),
        warnings=[
            "robust_scaler_applied_from_independent_train_cache",
            "source_cache_rows_not_used_to_fit_scaler",
        ],
    )


def _find_scaler_transform(metadata: dict[str, Any]) -> dict[str, Any]:
    matches = [
        item.get("params") or {}
        for item in metadata.get("transformations") or []
        if isinstance(item, dict) and item.get("name") == "per_channel_robust_scaler"
    ]
    if len(matches) != 1:
        raise ValueError("Cache must declare exactly one per_channel_robust_scaler transform.")
    return dict(matches[0])


def _validate_train_fit_scaler(params: dict[str, Any]) -> None:
    if params.get("enabled") is not True:
        raise ValueError("Fit cache must explicitly declare robust scaling enabled.")
    if params.get("fit_split") != "train":
        raise ValueError("Fit cache scaler must declare fit_split='train'.")
    if params.get("fit_scope") != "valid_train_sentence_timepoints":
        raise ValueError("Fit cache scaler must use valid_train_sentence_timepoints.")
    for key in ("split_protocol_config_sha256", "semantic_membership_sha256"):
        if not params.get(key):
            raise ValueError(f"Fit cache scaler is missing {key}.")
    statistics = params.get("statistics")
    if not isinstance(statistics, dict):
        raise ValueError("Fit cache scaler statistics are missing.")
    for key in ("center", "scale", "center_sha256", "scale_sha256", "n_fit_rows"):
        if key not in statistics:
            raise ValueError(f"Fit cache scaler statistics are missing {key}.")
    if int(statistics["n_fit_rows"]) < 1:
        raise ValueError("Fit cache scaler must contain at least one fit row.")


def _validate_preprocessing_match(
    source_metadata: dict[str, Any],
    fit_metadata: dict[str, Any],
) -> None:
    source = _preprocessing_signature(source_metadata)
    fit = _preprocessing_signature(fit_metadata)
    mismatches = [key for key in PREPROCESSING_KEYS if source[key] != fit[key]]
    if mismatches:
        details = ", ".join(f"{key}={source[key]!r} vs {fit[key]!r}" for key in mismatches)
        raise ValueError(f"Source and fit preprocessing differ: {details}.")


def _preprocessing_signature(metadata: dict[str, Any]) -> dict[str, Any]:
    params = metadata.get("extraction_params")
    if not isinstance(params, dict):
        raise ValueError("Cache extraction_params metadata is missing.")
    missing = [key for key in PREPROCESSING_KEYS if key not in params]
    if missing:
        raise ValueError(f"Cache extraction_params are missing: {missing}.")
    return {key: params[key] for key in PREPROCESSING_KEYS}


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Frozen scaling requires NumPy: `pip install numpy`.") from exc
    return np
