"""Validation helpers for same-subject, independent-session evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from neurodecodekit.cache.signal_representation import file_sha256


def validate_cross_session_contract(
    *,
    train_cache,
    eval_cache,
    partitions,
) -> dict[str, Any]:
    """Fail closed unless split, scaler, cache, and channel provenance agree."""

    train_path = Path(str(train_cache.path))
    eval_path = Path(str(eval_cache.path))
    train_sha256 = file_sha256(train_path)
    eval_sha256 = file_sha256(eval_path)
    if train_sha256 != partitions.source_cache_sha256:
        raise ValueError("Train cache hash does not match the strict split report.")
    if train_sha256 == eval_sha256:
        raise ValueError("Cross-session evaluation requires a distinct evaluation cache.")
    train_channels = [str(value) for value in train_cache.channel_names.tolist()]
    eval_channels = [str(value) for value in eval_cache.channel_names.tolist()]
    if train_channels != eval_channels:
        raise ValueError("Cross-session caches must have identical channel names and order.")

    frozen = eval_cache.metadata.get("frozen_scaler")
    if not isinstance(frozen, dict):
        raise ValueError("Evaluation cache lacks frozen-scaler provenance.")
    fit_cache = frozen.get("fit_cache")
    source_cache = frozen.get("source_cache")
    if not isinstance(fit_cache, dict) or not isinstance(source_cache, dict):
        raise ValueError("Evaluation frozen-scaler cache provenance is incomplete.")
    if fit_cache.get("sha256") != train_sha256:
        raise ValueError("Evaluation scaler was not fitted from the requested train cache.")
    if frozen.get("fit_split") != "train":
        raise ValueError("Evaluation scaler provenance must declare fit_split='train'.")
    if frozen.get("fit_scope") != "valid_train_sentence_timepoints":
        raise ValueError("Evaluation scaler provenance has the wrong fit scope.")
    if frozen.get("split_protocol_config_sha256") != partitions.protocol_config_sha256:
        raise ValueError("Evaluation scaler split protocol hash does not match source membership.")
    if frozen.get("semantic_membership_sha256") != partitions.semantic_membership_sha256:
        raise ValueError(
            "Evaluation scaler semantic membership hash does not match source membership."
        )

    source_verified = False
    source_path_value = source_cache.get("path")
    source_sha256 = source_cache.get("sha256")
    if source_path_value and source_sha256:
        source_path = Path(str(source_path_value))
        if source_path.is_file():
            if file_sha256(source_path) != source_sha256:
                raise ValueError("Frozen-scaler source cache hash no longer matches its file.")
            source_verified = True

    train_raw = _raw_source_path(train_cache.metadata)
    eval_raw = _raw_source_path(eval_cache.metadata)
    if train_raw and eval_raw and train_raw == eval_raw:
        raise ValueError("Cross-session caches point to the same raw recording.")
    eval_events = eval_cache.metadata.get("events") or {}
    trial_mapping = eval_events.get("trial_index_mapping") or {}
    return {
        "proof_posture": "real_same_subject_independent_session_local_evaluation",
        "train_cache": {
            "path": str(train_path),
            "sha256": train_sha256,
            "bytes": train_cache.summary.bytes,
            "signals_shape": list(train_cache.summary.signals_shape),
            "raw_source": train_raw,
        },
        "eval_cache": {
            "path": str(eval_path),
            "sha256": eval_sha256,
            "bytes": eval_cache.summary.bytes,
            "signals_shape": list(eval_cache.summary.signals_shape),
            "raw_source": eval_raw,
            "trial_indices": [int(value) for value in eval_cache.trial_indices.tolist()],
            "skipped_mat_trial_indices": list(trial_mapping.get("skipped_mat_trial_indices") or []),
        },
        "channel_names_identical": True,
        "n_channels": len(train_channels),
        "frozen_scaler": frozen,
        "unscaled_eval_source_cache_hash_verified": source_verified,
        "source_membership": {
            "report_path": partitions.report_path,
            "train_indices": list(partitions.train_indices),
            "reserved_validation_indices": list(partitions.validation_indices),
            "reserved_test_indices": list(partitions.test_indices),
            "protocol_config_sha256": partitions.protocol_config_sha256,
            "group_assignment_sha256": partitions.group_assignment_sha256,
            "semantic_membership_sha256": partitions.semantic_membership_sha256,
        },
    }


def summarize_text_overlap(
    *,
    train_texts: list[str],
    eval_texts: list[str],
) -> dict[str, Any]:
    train_unique = set(str(value) for value in train_texts)
    eval_unique = set(str(value) for value in eval_texts)
    overlap = sorted(train_unique & eval_unique)
    return {
        "train_unique_texts": len(train_unique),
        "eval_unique_texts": len(eval_unique),
        "overlap_unique_texts": len(overlap),
        "eval_unique_overlap_fraction": (len(overlap) / len(eval_unique) if eval_unique else 0.0),
        "overlap_texts": overlap,
    }


def _raw_source_path(metadata: dict[str, Any]) -> str | None:
    source_files = metadata.get("source_files") or {}
    value = source_files.get("raw")
    return str(value) if value else None
