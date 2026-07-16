"""Pure Loop 48 Stage B split, control, freeze, and scoring contracts."""

from __future__ import annotations

import hashlib
import json
import math
import resource
import statistics
import time
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from neurodecodekit.evaluation.metrics import (
    character_error_rate,
    levenshtein_distance,
    normalize_text,
    sentence_exact_match,
)


SCHEMA_VERSION = "0.1.0"
FIT_PREFIX_SIZES = (8, 16, 24, 32, 44)
SEEDS = (4801, 4802, 4803)
PRIMARY_SEED = 4801
CHECK_ROWS = 11
SPLIT_SALT = "neurodecodekit-loop48-stage-b-v0-fit-check"
CHECK_ROW_SALT = "neurodecodekit-loop48-stage-b-v0-check-row-cycle"
CHANNEL_SALT = "neurodecodekit-loop48-stage-b-v0-channel-cycle"
FIT_TARGET_SALT = "neurodecodekit-loop48-stage-b-v0-fit-target-cycle"
FINE_SHIFT_OFFSETS = (-50, -25, 25, 50)
RESOURCE_CAPS = {
    "generated_artifact_bytes_before_freeze": 32 * 1024 * 1024,
    "checkpoint_bytes": 4 * 1024 * 1024,
    "prediction_payload_bytes": 4 * 1024 * 1024,
    "working_array_bytes_upper_bound": 128 * 1024 * 1024,
    "parameter_update_runtime_sec": 600.0,
    "cumulative_execution_runtime_sec": 900.0,
    "peak_rss_bytes": 1024 * 1024 * 1024,
}


def candidate_condition_id(size: int, seed: int) -> str:
    if int(size) not in FIT_PREFIX_SIZES or int(seed) not in SEEDS:
        raise ValueError("candidate condition requires a registered size and seed")
    return f"candidate_size{int(size)}_seed{int(seed)}"


def prior_condition_id(size: int) -> str:
    if int(size) not in FIT_PREFIX_SIZES:
        raise ValueError("prior condition requires a registered size")
    return f"prior_size{int(size)}"


def linear_condition_id(seed: int) -> str:
    if int(seed) not in SEEDS:
        raise ValueError("linear condition requires a registered seed")
    return f"linear_size44_seed{int(seed)}"


def fine_shift_condition_id(offset_samples: int, seed: int) -> str:
    if int(offset_samples) not in FINE_SHIFT_OFFSETS or int(seed) not in SEEDS:
        raise ValueError("fine-shift condition requires a registered offset and seed")
    direction = "neg" if int(offset_samples) < 0 else "pos"
    return f"fine_shift_{direction}{abs(int(offset_samples))}_seed{int(seed)}"


def expected_fit_ids() -> tuple[str, ...]:
    candidates = tuple(
        candidate_condition_id(size, seed) for size in FIT_PREFIX_SIZES for seed in SEEDS
    )
    linear = tuple(linear_condition_id(seed) for seed in SEEDS)
    return (*candidates, *linear, "timing_only_fit", "fit_target_derangement_fit")


def expected_prediction_ids() -> tuple[str, ...]:
    candidates = tuple(
        candidate_condition_id(size, seed) for size in FIT_PREFIX_SIZES for seed in SEEDS
    )
    priors = tuple(prior_condition_id(size) for size in FIT_PREFIX_SIZES)
    linear = tuple(linear_condition_id(seed) for seed in SEEDS)
    shifts = tuple(
        fine_shift_condition_id(offset, seed) for offset in FINE_SHIFT_OFFSETS for seed in SEEDS
    )
    return (
        *candidates,
        *priors,
        *linear,
        "zero_signal",
        "check_row_derangement",
        "channel_derangement",
        *shifts,
        "severe_plus100_sample_displacement",
        "timing_only_fit",
        "fit_target_derangement_fit",
    )


def diagnostic_split(
    membership_rows: Sequence[Mapping[str, Any]],
    *,
    expected_source_rows: int = 55,
    fit_rows: int = 44,
) -> dict[str, Any]:
    """Create the frozen target-independent fit/check assignment."""

    rows = [dict(row) for row in membership_rows]
    if len(rows) != expected_source_rows:
        raise ValueError(
            f"diagnostic split requires {expected_source_rows} source rows, got {len(rows)}"
        )
    if not 0 < fit_rows < expected_source_rows:
        raise ValueError("fit row count must leave a nonempty check partition")
    required = {"source_row_index", "row_uid_sha256", "semantic_row_uid_sha256"}
    if any(not required <= set(row) for row in rows):
        raise ValueError("diagnostic split membership lacks required identities")
    source_indices = [int(row["source_row_index"]) for row in rows]
    row_ids = [str(row["row_uid_sha256"]) for row in rows]
    semantic_ids = [str(row["semantic_row_uid_sha256"]) for row in rows]
    if len(set(source_indices)) != len(rows):
        raise ValueError("diagnostic split source row indices must be unique")
    if len(set(row_ids)) != len(rows):
        raise ValueError("diagnostic split row IDs must be unique")
    if len(set(semantic_ids)) != len(rows):
        raise ValueError("diagnostic split semantic IDs must be unique")

    def key(row: Mapping[str, Any]) -> tuple[str, int]:
        payload = (
            SPLIT_SALT.encode("utf-8")
            + b"\0"
            + str(row["semantic_row_uid_sha256"]).encode("utf-8")
            + b"\0"
            + str(row["row_uid_sha256"]).encode("utf-8")
        )
        return hashlib.sha256(payload).hexdigest(), int(row["source_row_index"])

    ordered = sorted(rows, key=key)
    fit = ordered[:fit_rows]
    check = ordered[fit_rows:]
    assignment = [
        {
            "source_row_index": int(row["source_row_index"]),
            "row_uid_sha256": str(row["row_uid_sha256"]),
            "semantic_row_uid_sha256": str(row["semantic_row_uid_sha256"]),
            "diagnostic_partition": "fit" if position < fit_rows else "check",
            "diagnostic_order": position,
        }
        for position, row in enumerate(ordered)
    ]
    return {
        "salt": SPLIT_SALT,
        "source_rows": len(rows),
        "fit_rows": len(fit),
        "check_rows": len(check),
        "ordered_source_row_indices": [int(row["source_row_index"]) for row in ordered],
        "fit_source_row_indices": [int(row["source_row_index"]) for row in fit],
        "check_source_row_indices": [int(row["source_row_index"]) for row in check],
        "fit_row_ids": [str(row["row_uid_sha256"]) for row in fit],
        "check_row_ids": [str(row["row_uid_sha256"]) for row in check],
        "fit_semantic_ids": [str(row["semantic_row_uid_sha256"]) for row in fit],
        "check_semantic_ids": [str(row["semantic_row_uid_sha256"]) for row in check],
        "assignment_sha256": sha256_json(assignment),
    }


def channel_derangement_indices(channel_names: Sequence[str]) -> list[int]:
    names = [str(value) for value in channel_names]
    if len(names) < 2 or len(names) != len(set(names)):
        raise ValueError("channel derangement requires unique channel names")
    ordered = sorted(
        range(len(names)),
        key=lambda index: (_salted_hash(CHANNEL_SALT, names[index]), names[index]),
    )
    source_for_destination = list(range(len(names)))
    for position, source_index in enumerate(ordered):
        destination_index = ordered[(position + 1) % len(ordered)]
        source_for_destination[destination_index] = source_index
    if any(source == destination for destination, source in enumerate(source_for_destination)):
        raise RuntimeError("channel derangement unexpectedly contains a fixed point")
    return source_for_destination


def apply_channel_derangement(signals, channel_names: Sequence[str]):
    np = _require_numpy()
    values = np.asarray(signals)
    if values.ndim != 3 or values.shape[1] != len(channel_names):
        raise ValueError("signals and channel names do not share channel geometry")
    mapping = channel_derangement_indices(channel_names)
    return np.ascontiguousarray(values[:, mapping, :]), mapping


def apply_nonwrapping_shift(signals, input_lengths, *, offset_samples: int):
    """Shift valid samples without wrapping; positive offsets delay the signal."""

    np = _require_numpy()
    values = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or lengths.shape != (len(values),):
        raise ValueError("time shift requires signals and matching lengths")
    if int(offset_samples) == 0:
        raise ValueError("registered shifted controls require a nonzero offset")
    if (lengths < 1).any() or (lengths > values.shape[2]).any():
        raise ValueError("input lengths fall outside padded signal width")
    output = np.zeros(values.shape, dtype="float32")
    lost_valid_samples = 0
    offset = int(offset_samples)
    for index, length_value in enumerate(lengths):
        length = int(length_value)
        shift = min(abs(offset), length)
        copied = length - shift
        if copied > 0 and offset > 0:
            output[index, :, shift:length] = values[index, :, :copied]
        elif copied > 0:
            output[index, :, :copied] = values[index, :, shift:length]
        lost_valid_samples += shift
    return output, {
        "offset_samples": offset,
        "offset_seconds": offset / 100.0,
        "wrapping": False,
        "fill_value": 0.0,
        "lost_valid_samples_per_channel": lost_valid_samples,
        "lost_values_total": lost_valid_samples * values.shape[1],
        "offline_noncausal_diagnostic_only": offset < 0,
    }


def timing_only_signals(signals, input_lengths):
    np = _require_numpy()
    values = np.asarray(signals)
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or values.shape[1] != 102 or lengths.shape != (len(values),):
        raise ValueError("timing-only controls require [items, 102, time] and lengths")
    output = np.zeros(values.shape, dtype="float32")
    for index, length_value in enumerate(lengths):
        length = int(length_value)
        output[index, 0, :length] = 1.0
        if length > 1:
            output[index, 1, :length] = np.arange(length, dtype="float32") / (length - 1)
    return output


def zero_signals(signals):
    np = _require_numpy()
    values = np.asarray(signals)
    if values.ndim != 3:
        raise ValueError("zero-signal control requires a three-dimensional array")
    return np.zeros(values.shape, dtype="float32")


def derange_fit_targets(
    target_token_ids,
    target_lengths,
    target_texts: Sequence[str],
    semantic_ids: Sequence[str],
):
    np = _require_numpy()
    ids = [str(value) for value in semantic_ids]
    if len(ids) < 2 or len(ids) != len(set(ids)):
        raise ValueError("fit-target derangement requires unique semantic IDs")
    ordered = sorted(
        range(len(ids)),
        key=lambda index: (_salted_hash(FIT_TARGET_SALT, ids[index]), ids[index]),
    )
    source_for_signal = list(range(len(ids)))
    for position, signal_index in enumerate(ordered):
        source_for_signal[signal_index] = ordered[(position + 1) % len(ordered)]
    if any(source == index for index, source in enumerate(source_for_signal)):
        raise RuntimeError("fit-target derangement unexpectedly contains a fixed point")
    return (
        np.asarray(target_token_ids)[source_for_signal].copy(),
        np.asarray(target_lengths)[source_for_signal].copy(),
        [str(target_texts[source]) for source in source_for_signal],
        source_for_signal,
    )


def derange_check_predictions(
    predictions: Sequence[str], item_ids: Sequence[str]
) -> tuple[list[str], list[int]]:
    ids = [str(value) for value in item_ids]
    values = [str(value) for value in predictions]
    if len(ids) < 2 or len(ids) != len(values) or len(ids) != len(set(ids)):
        raise ValueError("check-row derangement requires unique IDs and matching predictions")
    ordered = sorted(
        range(len(ids)),
        key=lambda index: (_salted_hash(CHECK_ROW_SALT, ids[index]), ids[index]),
    )
    source_for_destination = list(range(len(ids)))
    for position, source_index in enumerate(ordered):
        destination_index = ordered[(position + 1) % len(ordered)]
        source_for_destination[destination_index] = source_index
    if any(source == index for index, source in enumerate(source_for_destination)):
        raise RuntimeError("check-row derangement unexpectedly contains a fixed point")
    return [values[source] for source in source_for_destination], source_for_destination


def write_prediction_payload(
    path: str | Path,
    *,
    condition_id: str,
    item_ids: Sequence[str],
    predictions: Sequence[str],
    input_lengths: Sequence[int],
    configuration: Mapping[str, Any],
    checkpoint_sha256_or_reason: str,
    transform: Mapping[str, Any],
    runtime_sec: float,
    peak_rss_bytes: int,
    model_run_count: int,
    blank_fraction: float | None,
    warnings: Sequence[str],
) -> dict[str, Any]:
    """Write one ignored plaintext payload and return its hash-only freeze row."""

    output = Path(path)
    if output.exists():
        raise FileExistsError(f"Refusing to replace prediction payload: {output}")
    ids = [str(value) for value in item_ids]
    values = [str(value) for value in predictions]
    lengths = [int(value) for value in input_lengths]
    if len(ids) != CHECK_ROWS or len(values) != CHECK_ROWS or len(lengths) != CHECK_ROWS:
        raise ValueError(f"every registered prediction set must contain {CHECK_ROWS} rows")
    if len(set(ids)) != CHECK_ROWS:
        raise ValueError("prediction item IDs must be unique")
    payload = {
        "schema": {"name": "neurodecodekit.loop48_stage_b_prediction_payload", "version": 0},
        "condition_id": str(condition_id),
        "item_ids": ids,
        "predictions": values,
        "input_lengths": lengths,
        "configuration": dict(configuration),
        "checkpoint_sha256_or_reason": str(checkpoint_sha256_or_reason),
        "transform": dict(transform),
        "runtime_sec": float(runtime_sec),
        "peak_rss_bytes": int(peak_rss_bytes),
        "model_run_count": int(model_run_count),
        "blank_fraction": None if blank_fraction is None else float(blank_fraction),
        "warnings": [str(value) for value in warnings],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "condition_id": str(condition_id),
        "configuration_sha256": sha256_json(dict(configuration)),
        "checkpoint_sha256_or_no_checkpoint_reason": str(checkpoint_sha256_or_reason),
        "transform_sha256_or_identity": (
            "identity" if dict(transform) == {"name": "identity"} else sha256_json(transform)
        ),
        "ordered_check_item_ids_sha256": sha256_json(ids),
        "prediction_payload_sha256": sha256_json({"item_ids": ids, "predictions": values}),
        "lengths_sha256": sha256_json(lengths),
        "runtime_sec": float(runtime_sec),
        "peak_rss_bytes": int(peak_rss_bytes),
        "model_run_count": int(model_run_count),
        "warnings": [str(value) for value in warnings],
        "private_payload_bytes": int(output.stat().st_size),
        "private_payload_file_sha256": file_sha256(output),
    }


def load_prediction_payload(path: str | Path, freeze_row: Mapping[str, Any]) -> dict[str, Any]:
    payload_path = Path(path)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if payload.get("condition_id") != freeze_row.get("condition_id"):
        raise ValueError("prediction condition does not match freeze row")
    if file_sha256(payload_path) != freeze_row.get("private_payload_file_sha256"):
        raise ValueError("prediction file hash does not match freeze row")
    checks = {
        "prediction payload": (
            sha256_json(
                {"item_ids": payload.get("item_ids"), "predictions": payload.get("predictions")}
            ),
            freeze_row.get("prediction_payload_sha256"),
        ),
        "item order": (
            sha256_json(payload.get("item_ids")),
            freeze_row.get("ordered_check_item_ids_sha256"),
        ),
        "input lengths": (
            sha256_json(payload.get("input_lengths")),
            freeze_row.get("lengths_sha256"),
        ),
        "configuration": (
            sha256_json(payload.get("configuration")),
            freeze_row.get("configuration_sha256"),
        ),
    }
    for name, (actual, expected) in checks.items():
        if actual != expected:
            raise ValueError(f"prediction {name} does not match freeze row")
    if payload.get("checkpoint_sha256_or_reason") != freeze_row.get(
        "checkpoint_sha256_or_no_checkpoint_reason"
    ):
        raise ValueError("prediction checkpoint identity does not match freeze row")
    transform = payload.get("transform")
    transform_hash = "identity" if transform == {"name": "identity"} else sha256_json(transform)
    if transform_hash != freeze_row.get("transform_sha256_or_identity"):
        raise ValueError("prediction transform does not match freeze row")
    return payload


def build_prediction_freeze_record(
    *,
    contract_sha256: str,
    authorization_decision_sha256: str,
    implementation_commit: str,
    prediction_rows: Iterable[Mapping[str, Any]],
    fit_rows: Iterable[Mapping[str, Any]],
    static_audit: Mapping[str, Any],
    access_counters: Mapping[str, int],
    resources: Mapping[str, Any],
    environment: Mapping[str, Any],
    warnings: Sequence[str],
) -> dict[str, Any]:
    record = {
        "schema_name": "neurodecodekit.loop48_stage_b_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "status": "predictions_frozen_check_targets_unavailable",
        "proof_posture": "hash_only_train_check_prediction_freeze_no_check_targets_or_scores",
        "contract_sha256": str(contract_sha256),
        "authorization_decision_sha256": str(authorization_decision_sha256),
        "implementation_commit": str(implementation_commit),
        "prediction_set_count": len(listed_predictions := [dict(row) for row in prediction_rows]),
        "prediction_sets": sorted(listed_predictions, key=lambda row: row["condition_id"]),
        "fit_telemetry_bundle_count": len(listed_fits := [dict(row) for row in fit_rows]),
        "fit_telemetry_bundles": sorted(listed_fits, key=lambda row: row["condition_id"]),
        "static_audit": dict(static_audit),
        "access_counters": {str(key): int(value) for key, value in access_counters.items()},
        "resources": dict(resources),
        "environment": dict(environment),
        "check_target_rows_delivered": 0,
        "check_scoring_runs": 0,
        "plaintext_predictions_committed": False,
        "plaintext_targets_committed": False,
        "warnings": [str(value) for value in warnings],
    }
    validate_prediction_freeze_record(record)
    return record


def validate_prediction_freeze_record(record: Mapping[str, Any]) -> None:
    if record.get("schema_name") != "neurodecodekit.loop48_stage_b_prediction_freeze":
        raise ValueError("unsupported Loop 48 Stage B prediction-freeze schema")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported Loop 48 Stage B prediction-freeze version")
    predictions = record.get("prediction_sets")
    if not isinstance(predictions, list) or len(predictions) != 41:
        raise ValueError("prediction freeze must contain exactly 41 sets")
    prediction_ids = [str(row.get("condition_id")) for row in predictions]
    if len(set(prediction_ids)) != 41 or set(prediction_ids) != set(expected_prediction_ids()):
        raise ValueError("prediction freeze inventory is incomplete or duplicated")
    required_prediction = {
        "condition_id",
        "configuration_sha256",
        "checkpoint_sha256_or_no_checkpoint_reason",
        "transform_sha256_or_identity",
        "ordered_check_item_ids_sha256",
        "prediction_payload_sha256",
        "lengths_sha256",
        "runtime_sec",
        "peak_rss_bytes",
        "model_run_count",
        "warnings",
    }
    item_hashes = set()
    for row in predictions:
        if not required_prediction <= set(row):
            raise ValueError(f"prediction freeze row lacks fields: {row.get('condition_id')}")
        if {"prediction", "predictions", "target", "targets", "text", "texts"} & set(row):
            raise ValueError("committed prediction freeze must not contain plaintext")
        item_hashes.add(str(row["ordered_check_item_ids_sha256"]))
    if len(item_hashes) != 1:
        raise ValueError("all prediction sets must share one ordered 11-item identity")
    expected_model_runs = {
        condition_id: 0
        if condition_id.startswith("prior_") or condition_id == "check_row_derangement"
        else 1
        for condition_id in expected_prediction_ids()
    }
    run_mismatches = {
        str(row["condition_id"]): {
            "expected": expected_model_runs[str(row["condition_id"])],
            "actual": row["model_run_count"],
        }
        for row in predictions
        if row["model_run_count"] != expected_model_runs[str(row["condition_id"])]
    }
    if run_mismatches or sum(int(row["model_run_count"]) for row in predictions) != 35:
        raise ValueError(f"prediction freeze model-run inventory is invalid: {run_mismatches}")

    fits = record.get("fit_telemetry_bundles")
    if not isinstance(fits, list) or len(fits) != 20:
        raise ValueError("prediction freeze must contain exactly 20 fit telemetry bundles")
    fit_ids = [str(row.get("condition_id")) for row in fits]
    if len(set(fit_ids)) != 20 or set(fit_ids) != set(expected_fit_ids()):
        raise ValueError("fit telemetry inventory is incomplete or duplicated")
    required_fit = {
        "condition_id",
        "seed",
        "prefix_size",
        "configuration_sha256",
        "checkpoint_sha256",
        "telemetry_sha256",
        "optimizer_steps",
        "runtime_sec",
        "peak_rss_bytes",
        "warnings",
    }
    for row in fits:
        if not required_fit <= set(row):
            raise ValueError(f"fit telemetry row lacks fields: {row.get('condition_id')}")
        if int(row["optimizer_steps"]) != 240:
            raise ValueError("every registered fit must record exactly 240 optimizer steps")
        if {"target", "targets", "text", "texts", "prediction", "predictions"} & set(row):
            raise ValueError("committed fit telemetry must not contain plaintext")

    counters = record.get("access_counters") or {}
    exact = {
        "source_cache_stat_reads": 1,
        "source_cache_hash_passes": 1,
        "split_report_metadata_reads": 1,
        "archive_header_reads": 14,
        "archive_row_member_streams": 7,
        "fit_signal_rows_delivered": 44,
        "fit_target_rows_delivered": 44,
        "check_signal_rows_delivered": 11,
        "candidate_training_runs": 15,
        "linear_training_runs": 3,
        "control_training_runs": 2,
        "optimizer_steps": 4800,
        "checkpoint_writes": 20,
        "checkpoint_reads": 0,
        "target_blind_model_inference_runs": 35,
        "no_signal_prior_fits": 5,
        "prediction_sets_frozen": 41,
        "check_target_rows_delivered_before_green_freeze": 0,
        "check_target_rows_delivered_after_green_freeze": 0,
        "check_scoring_runs": 0,
        "validation_signal_rows_delivered": 0,
        "validation_target_rows_delivered": 0,
        "source_test_signal_rows_delivered": 0,
        "source_test_target_rows_delivered": 0,
        "session2_rows_delivered": 0,
        "raw_fif_or_mat_reads": 0,
        "network_calls": 0,
        "new_download_bytes": 0,
        "language_model_or_neurotoken_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "post_check_parameter_updates": 0,
        "post_check_configuration_changes": 0,
        "reruns": 0,
    }
    mismatches = {
        key: {"expected": expected, "actual": counters.get(key)}
        for key, expected in exact.items()
        if counters.get(key) != expected
    }
    if mismatches:
        raise ValueError(f"prediction-freeze counters mismatch: {mismatches}")
    if record.get("prediction_set_count") != 41 or record.get("fit_telemetry_bundle_count") != 20:
        raise ValueError("prediction-freeze summary counts are invalid")
    if record.get("check_target_rows_delivered") != 0 or record.get("check_scoring_runs") != 0:
        raise ValueError("prediction freeze cannot contain check target delivery or scoring")
    if record.get("plaintext_predictions_committed") is not False:
        raise ValueError("prediction freeze must declare no committed plaintext predictions")
    if record.get("plaintext_targets_committed") is not False:
        raise ValueError("prediction freeze must declare no committed plaintext targets")
    resources = record.get("resources") or {}
    resource_failures = {
        name: {"actual": resources.get(name), "cap": cap}
        for name, cap in RESOURCE_CAPS.items()
        if not isinstance(resources.get(name), (int, float))
        or float(resources[name]) < 0
        or float(resources[name]) > cap
    }
    if resource_failures:
        raise ValueError(f"prediction-freeze resources exceed caps: {resource_failures}")
    if resources.get("producer_is_causal") is not True:
        raise ValueError("prediction freeze must identify the model producer as causal")
    if resources.get("upstream_cache_is_causal") is not False:
        raise ValueError("prediction freeze must identify the upstream cache as noncausal")
    if resources.get("end_to_end_latency_measured") is not False:
        raise ValueError("prediction freeze cannot claim end-to-end latency measurement")


def score_failure_discrimination(
    *,
    prediction_payloads: Mapping[str, Mapping[str, Any]],
    target_item_ids: Sequence[str],
    targets: Sequence[str],
    freeze_record: Mapping[str, Any],
) -> dict[str, Any]:
    """Score every frozen set together and emit the six-hypothesis support vector."""

    started_at = time.perf_counter()
    validate_prediction_freeze_record(freeze_record)
    ids = [str(value) for value in target_item_ids]
    target_values = [normalize_text(str(value)) for value in targets]
    if len(ids) != CHECK_ROWS or len(target_values) != CHECK_ROWS or len(set(ids)) != CHECK_ROWS:
        raise ValueError("isolated scoring requires 11 unique ordered check items")
    if set(prediction_payloads) != set(expected_prediction_ids()):
        raise ValueError("isolated scoring requires all 41 frozen prediction sets")
    expected_item_hash = sha256_json(ids)
    frozen_item_hashes = {
        str(row["ordered_check_item_ids_sha256"]) for row in freeze_record["prediction_sets"]
    }
    if frozen_item_hashes != {expected_item_hash}:
        raise ValueError("scoring check item order does not match the prediction freeze")
    metrics: dict[str, dict[str, Any]] = {}
    for condition_id in expected_prediction_ids():
        payload = prediction_payloads[condition_id]
        if [str(value) for value in payload.get("item_ids", [])] != ids:
            raise ValueError(f"prediction item order mismatch for {condition_id}")
        if sha256_json(ids) != expected_item_hash:
            raise RuntimeError("check item identity changed during scoring")
        predictions = [normalize_text(str(value)) for value in payload.get("predictions", [])]
        if len(predictions) != CHECK_ROWS:
            raise ValueError(f"prediction set {condition_id} does not contain 11 rows")
        metrics[condition_id] = _condition_metrics(
            ids,
            target_values,
            predictions,
            blank_fraction=payload.get("blank_fraction"),
        )

    primary_id = candidate_condition_id(44, PRIMARY_SEED)
    prior_id = prior_condition_id(44)
    comparator_ids = (
        prior_id,
        "zero_signal",
        "check_row_derangement",
        "channel_derangement",
        "severe_plus100_sample_displacement",
        "timing_only_fit",
        "fit_target_derangement_fit",
    )
    comparisons = {
        comparator_id: paired_exact_comparison(metrics[primary_id], metrics[comparator_id])
        for comparator_id in comparator_ids
    }
    conjunction_components = {
        comparator_id: _comparison_passed(row, margin=0.05, p_max=0.05)
        for comparator_id, row in comparisons.items()
    }
    intact_conjunction_passed = all(conjunction_components.values())
    timing = _timing_sensitivity(metrics)
    probe = _registered_probe_separability(metrics, freeze_record)
    scaling = _bounded_scaling(metrics)
    check_ctc_feasibility = _check_text_ctc_feasibility(
        item_ids=ids,
        targets=target_values,
        input_lengths=prediction_payloads[primary_id]["input_lengths"],
    )
    hypotheses = _hypothesis_support_vector(
        metrics=metrics,
        freeze_record=freeze_record,
        conjunction_components=conjunction_components,
        intact_conjunction_passed=intact_conjunction_passed,
        timing=timing,
        probe=probe,
        scaling=scaling,
        check_infeasible_count=check_ctc_feasibility["infeasible_row_count"],
    )
    return {
        "schema_name": "neurodecodekit.loop48_stage_b_failure_discrimination_score",
        "schema_version": SCHEMA_VERSION,
        "status": "completed_registered_diagnostic_no_rerun",
        "proof_posture": "post_outcome_train_only_e2_pipeline_discriminative_diagnostic",
        "check_items": CHECK_ROWS,
        "condition_count": len(metrics),
        "primary_candidate": primary_id,
        "primary_prior": prior_id,
        "condition_metrics": metrics,
        "primary_comparisons": comparisons,
        "intact_signal_conjunction_components": conjunction_components,
        "intact_signal_conjunction_passed": intact_conjunction_passed,
        "timing_sensitivity": timing,
        "registered_probe_separability": probe,
        "bounded_scaling": scaling,
        "check_ctc_feasibility": check_ctc_feasibility,
        "hypothesis_support_vector": hypotheses,
        "orthogonal_T1_peripheral_or_task_locked_shortcut": "unresolved_by_stage_b",
        "maximum_evidence_level": "E2_pipeline_discriminative",
        "plaintext_targets_or_predictions_present": False,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": peak_rss_bytes(),
        "warnings": [
            "all_55_source_train_rows_were_used_historically",
            "check_rows_are_withheld_only_from_this_registered_prediction_process",
            "upstream_sentence_cache_is_offline_noncausal",
            "negative_time_shifts_are_offline_diagnostics_only",
            "stage_b_cannot_establish_neural_advantage_or_brain_specific_origin",
            "no_validation_source_test_session2_unseen_person_realtime_eeg_home_or_clinical_claim",
        ],
    }


def paired_exact_comparison(
    candidate: Mapping[str, Any], comparator: Mapping[str, Any]
) -> dict[str, Any]:
    candidate_cer = [float(row["cer"]) for row in candidate["per_item"]]
    comparator_cer = [float(row["cer"]) for row in comparator["per_item"]]
    if len(candidate_cer) != CHECK_ROWS or len(comparator_cer) != CHECK_ROWS:
        raise ValueError("paired exact comparison requires 11 paired rows")
    differences = [b - a for a, b in zip(candidate_cer, comparator_cer, strict=True)]
    observed = statistics.fmean(differences)
    null_statistics = []
    for assignment in range(1 << CHECK_ROWS):
        signed = [
            value if assignment & (1 << index) else -value
            for index, value in enumerate(differences)
        ]
        null_statistics.append(statistics.fmean(signed))
    tolerance = 1e-15
    greater = sum(value >= observed - tolerance for value in null_statistics) / len(null_statistics)
    less = sum(value <= observed + tolerance for value in null_statistics) / len(null_statistics)
    return {
        "differences": differences,
        "observed_mean_difference": observed,
        "null_assignments": len(null_statistics),
        "one_sided_greater_p": greater,
        "two_sided_p": min(1.0, 2 * min(greater, less)),
        "wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
    }


def _condition_metrics(
    item_ids: Sequence[str],
    targets: Sequence[str],
    predictions: Sequence[str],
    *,
    blank_fraction: float | None,
) -> dict[str, Any]:
    per_item = []
    character_edits = 0
    characters = 0
    word_edits = 0
    words = 0
    exact_count = 0
    for item_id, target, prediction in zip(item_ids, targets, predictions, strict=True):
        row_character_edits = levenshtein_distance(target, prediction)
        row_word_edits = levenshtein_distance(target.split(), prediction.split())
        exact = sentence_exact_match(target, prediction, normalize=False)
        character_edits += row_character_edits
        characters += len(target)
        word_edits += row_word_edits
        words += len(target.split())
        exact_count += int(exact)
        per_item.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "character_edits": row_character_edits,
                "cer": character_error_rate(target, prediction, normalize=False),
                "word_edits": row_word_edits,
                "exact": exact,
                "target_characters": len(target),
                "target_words": len(target.split()),
            }
        )
    return {
        "per_item": per_item,
        "macro_sentence_cer": statistics.fmean(row["cer"] for row in per_item),
        "corpus_cer": character_edits / characters,
        "corpus_wer": word_edits / words,
        "exact_sentence_count": exact_count,
        "blank_fraction": None if blank_fraction is None else float(blank_fraction),
    }


def _timing_sensitivity(metrics: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    intact_by_seed = {seed: candidate_condition_id(44, seed) for seed in SEEDS}
    offsets = {}
    for offset in FINE_SHIFT_OFFSETS:
        per_seed = {}
        for seed in SEEDS:
            shifted = fine_shift_condition_id(offset, seed)
            comparison = paired_exact_comparison(metrics[shifted], metrics[intact_by_seed[seed]])
            per_seed[str(seed)] = {
                "macro_cer_improvement": comparison["observed_mean_difference"],
                "one_sided_greater_p": comparison["one_sided_greater_p"],
            }
        primary = per_seed[str(PRIMARY_SEED)]
        same_direction = all(row["macro_cer_improvement"] > 0 for row in per_seed.values())
        passed = (
            primary["macro_cer_improvement"] >= 0.05
            and primary["one_sided_greater_p"] <= 0.0125
            and same_direction
        )
        offsets[str(offset)] = {
            "per_seed": per_seed,
            "same_improving_direction_all_seeds": same_direction,
            "corrected_rule_passed": passed,
        }
    return {
        "offsets": offsets,
        "support_rule_passed": any(row["corrected_rule_passed"] for row in offsets.values()),
        "against_rule_passed": all(
            not row["corrected_rule_passed"] and not row["same_improving_direction_all_seeds"]
            for row in offsets.values()
        ),
        "selected_shift": None,
        "transform_change_authorized": False,
    }


def _registered_probe_separability(
    metrics: Mapping[str, Mapping[str, Any]], freeze_record: Mapping[str, Any]
) -> dict[str, Any]:
    fit_by_id = {str(row["condition_id"]): row for row in freeze_record["fit_telemetry_bundles"]}
    prior = metrics[prior_condition_id(44)]
    families = {
        "candidate": [candidate_condition_id(44, seed) for seed in SEEDS],
        "linear": [linear_condition_id(seed) for seed in SEEDS],
    }
    family_rows = {}
    for family, condition_ids in families.items():
        rows = []
        for condition_id in condition_ids:
            comparison = paired_exact_comparison(metrics[condition_id], prior)
            telemetry_stable = bool(fit_by_id[condition_id].get("telemetry_finite", False))
            rows.append(
                {
                    "condition_id": condition_id,
                    "telemetry_finite_and_stable": telemetry_stable,
                    "macro_cer_margin": comparison["observed_mean_difference"],
                    "one_sided_greater_p": comparison["one_sided_greater_p"],
                    "clears_prior": telemetry_stable
                    and _comparison_passed(comparison, margin=0.05, p_max=0.05),
                }
            )
        family_rows[family] = rows
    all_six_stable = all(
        row["telemetry_finite_and_stable"] for rows in family_rows.values() for row in rows
    )
    none_clear = all(not row["clears_prior"] for rows in family_rows.values() for row in rows)
    family_all_clear = {
        family: all(row["clears_prior"] for row in rows) for family, rows in family_rows.items()
    }
    return {
        "families": family_rows,
        "all_six_fits_finite_and_stable": all_six_stable,
        "none_of_six_clears_prior": none_clear,
        "support_rule_passed": all_six_stable and none_clear,
        "against_rule_passed": any(family_all_clear.values()),
        "family_all_three_seeds_clear_prior": family_all_clear,
    }


def _bounded_scaling(metrics: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    medians = {}
    dispersion = {}
    seed_slopes = {}
    for size in FIT_PREFIX_SIZES:
        values = [
            float(metrics[candidate_condition_id(size, seed)]["macro_sentence_cer"])
            for seed in SEEDS
        ]
        medians[str(size)] = statistics.median(values)
        dispersion[str(size)] = max(values) - min(values)
    x_values = [math.log2(size) for size in FIT_PREFIX_SIZES]
    for seed in SEEDS:
        y_values = [
            float(metrics[candidate_condition_id(size, seed)]["macro_sentence_cer"])
            for size in FIT_PREFIX_SIZES
        ]
        seed_slopes[str(seed)] = _ols_slope(x_values, y_values)
    small_mean = statistics.fmean(medians[str(size)] for size in (8, 16))
    large_mean = statistics.fmean(medians[str(size)] for size in (32, 44))
    gain = small_mean - large_mean
    support = gain >= 0.05 and all(value < 0 for value in seed_slopes.values())
    against = gain < 0.02 and all(abs(value) <= 0.01 for value in seed_slopes.values())
    return {
        "prefix_sizes": list(FIT_PREFIX_SIZES),
        "median_seed_macro_check_cer": medians,
        "seed_dispersion_range": dispersion,
        "seed_ols_slopes_per_log2_unit": seed_slopes,
        "small_band_mean_minus_large_band_mean": gain,
        "size32_to_size44_median_change": medians["32"] - medians["44"],
        "support_rule_passed": support,
        "against_rule_passed": against,
        "power_law_or_extrapolation_available": False,
    }


def _hypothesis_support_vector(
    *,
    metrics: Mapping[str, Mapping[str, Any]],
    freeze_record: Mapping[str, Any],
    conjunction_components: Mapping[str, bool],
    intact_conjunction_passed: bool,
    timing: Mapping[str, Any],
    probe: Mapping[str, Any],
    scaling: Mapping[str, Any],
    check_infeasible_count: int,
) -> list[dict[str, Any]]:
    fit_by_id = {str(row["condition_id"]): row for row in freeze_record["fit_telemetry_bundles"]}
    size8 = [fit_by_id[candidate_condition_id(8, seed)] for seed in SEEDS]
    fit_infeasible_count = int(
        (freeze_record.get("static_audit") or {}).get("infeasible_row_count", 0)
    )
    infeasible = fit_infeasible_count + int(check_infeasible_count) > 0
    any_nonfinite = any(not bool(row.get("telemetry_finite", False)) for row in fit_by_id.values())
    size8_fails_blank = all(
        float(row.get("fit_cer_gain_over_prior", float("-inf"))) < 0.05
        and float(row.get("fit_blank_fraction", 0.0)) >= 0.98
        for row in size8
    )
    size8_succeeds = all(
        float(row.get("fit_cer_gain_over_prior", float("-inf"))) >= 0.05
        and float(row.get("fit_blank_fraction", 1.0)) < 0.98
        and bool(row.get("telemetry_finite", False))
        for row in size8
    )
    h1_support = infeasible or any_nonfinite or size8_fails_blank
    h1_against = not infeasible and not any_nonfinite and size8_succeeds

    gross_defect = bool((freeze_record.get("static_audit") or {}).get("gross_defect", False))
    corruption_ids = (
        "zero_signal",
        "check_row_derangement",
        "channel_derangement",
        "severe_plus100_sample_displacement",
        "timing_only_fit",
        "fit_target_derangement_fit",
    )
    clears_corruptions = all(conjunction_components[condition] for condition in corruption_ids)
    clears_prior = conjunction_components[prior_condition_id(44)]

    decisions = [
        _decision_row(
            "H1",
            "fixed_tiny_ctc_recipe_feasibility_or_optimization_failure",
            h1_support,
            h1_against,
            {
                "infeasible_alignment": infeasible,
                "fit_infeasible_row_count": fit_infeasible_count,
                "check_infeasible_row_count": int(check_infeasible_count),
                "nonfinite_telemetry": any_nonfinite,
                "all_size8_fail_and_at_least_98_percent_blank": size8_fails_blank,
            },
        ),
        {
            "hypothesis_id": "H2",
            "label": "sensor_or_trial_quality_insufficiency",
            "status": "supported" if gross_defect else "unresolved_evidence_against_unavailable",
            "support_rule_passed": gross_defect,
            "against_rule_passed": False,
            "evidence_against_available": False,
            "evidence": {"gross_transformed_cache_defect": gross_defect},
        },
        _decision_row(
            "H3",
            "timing_or_preprocessing_information_mismatch",
            bool(timing["support_rule_passed"]),
            bool(timing["against_rule_passed"]),
            {"timing_sensitivity": timing},
        ),
        _decision_row(
            "H4",
            "stable_but_nonseparable_representation",
            bool(probe["support_rule_passed"]),
            bool(probe["against_rule_passed"]),
            {"registered_probe_separability": probe},
        ),
        _decision_row(
            "H5",
            "prior_dominated_task_regime",
            clears_corruptions and not clears_prior,
            intact_conjunction_passed,
            {
                "intact_clears_registered_corruptions": clears_corruptions,
                "intact_clears_prior": clears_prior,
                "full_conjunction": intact_conjunction_passed,
            },
        ),
        _decision_row(
            "H6",
            "data_quantity_or_sentence_diversity_insufficiency",
            bool(scaling["support_rule_passed"]),
            bool(scaling["against_rule_passed"]),
            {"bounded_scaling": scaling},
        ),
    ]
    return decisions


def _check_text_ctc_feasibility(
    *,
    item_ids: Sequence[str],
    targets: Sequence[str],
    input_lengths: Sequence[int],
) -> dict[str, Any]:
    if not (len(item_ids) == len(targets) == len(input_lengths) == CHECK_ROWS):
        raise ValueError("check CTC feasibility requires 11 aligned rows")
    rows = []
    for item_id, target, input_length in zip(item_ids, targets, input_lengths, strict=True):
        if not target:
            raise ValueError("check CTC target must be nonempty")
        repeats = sum(current == previous for previous, current in zip(target, target[1:]))
        minimum = len(target) + repeats
        rows.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "input_length": int(input_length),
                "target_length": len(target),
                "adjacent_repeat_count": repeats,
                "minimum_alignment_steps": minimum,
                "frame_to_target_ratio": int(input_length) / len(target),
                "alignment_feasible": int(input_length) >= minimum,
            }
        )
    return {
        "rows": rows,
        "infeasible_row_count": sum(not row["alignment_feasible"] for row in rows),
    }


def _decision_row(
    hypothesis_id: str,
    label: str,
    support: bool,
    against: bool,
    evidence: Mapping[str, Any],
) -> dict[str, Any]:
    if support and against:
        status = "conflicting_registered_evidence"
    elif support:
        status = "supported"
    elif against:
        status = "evidence_against"
    else:
        status = "mixed_or_unresolved"
    return {
        "hypothesis_id": hypothesis_id,
        "label": label,
        "status": status,
        "support_rule_passed": bool(support),
        "against_rule_passed": bool(against),
        "evidence": dict(evidence),
    }


def _comparison_passed(comparison: Mapping[str, Any], *, margin: float, p_max: float) -> bool:
    return (
        float(comparison["observed_mean_difference"]) >= margin
        and float(comparison["one_sided_greater_p"]) <= p_max
    )


def _ols_slope(x_values: Sequence[float], y_values: Sequence[float]) -> float:
    x_mean = statistics.fmean(x_values)
    y_mean = statistics.fmean(y_values)
    denominator = sum((value - x_mean) ** 2 for value in x_values)
    return (
        sum(
            (x_value - x_mean) * (y_value - y_mean)
            for x_value, y_value in zip(x_values, y_values, strict=True)
        )
        / denominator
    )


def _salted_hash(salt: str, value: str) -> str:
    return hashlib.sha256(salt.encode("utf-8") + b"\0" + str(value).encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if value > 10_000_000 else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Loop 48 Stage B arrays require NumPy: `pip install numpy`.") from exc
    return np
