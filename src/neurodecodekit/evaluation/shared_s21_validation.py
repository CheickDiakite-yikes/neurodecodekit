"""Target-blind controls, prediction freezing, and isolated S21 scoring."""

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


PREFIX_SALT = "neurodecodekit-loop26-31-33-shared-validation-v0-prefix"
CHANNEL_SALT = "neurodecodekit-L31-E04-channel-cycle-v0"
VALIDATION_ROW_SALT = "neurodecodekit-L31-E03-validation-row-cycle-v0"
TRAIN_TARGET_SALT = "neurodecodekit-L31-E08-train-target-cycle-v0"
PREFIX_SIZES = (8, 16, 24, 32, 44, 55)
SEEDS = (2601, 2602, 2603)
ADDITIONAL_CONTROL_IDS = (
    "L31-E02",
    "L31-E03",
    "L31-E04",
    "L31-E05",
    "L31-E06",
    "L31-E08",
    "L31-E09",
)
REQUIRED_EXACT_CONTROL_IDS = (
    "L31-E01",
    "L31-E02",
    "L31-E03",
    "L31-E04",
    "L31-E05",
    "L31-E06",
    "L31-E08",
)


def candidate_prediction_id(size: int, seed: int) -> str:
    if int(size) not in PREFIX_SIZES or int(seed) not in SEEDS:
        raise ValueError("candidate prediction ID requires a registered size and seed")
    return f"L33-N{int(size):02d}-S{int(seed)}"


def prior_prediction_id(size: int) -> str:
    if int(size) not in PREFIX_SIZES:
        raise ValueError("prior prediction ID requires a registered size")
    return f"L33-P{int(size):02d}"


def expected_prediction_ids() -> tuple[str, ...]:
    candidates = tuple(
        candidate_prediction_id(size, seed) for size in PREFIX_SIZES for seed in SEEDS
    )
    priors = tuple(prior_prediction_id(size) for size in PREFIX_SIZES)
    return (*candidates, *priors, *ADDITIONAL_CONTROL_IDS)


def registered_prefix_order(
    semantic_ids: Sequence[str],
    performed_row_ids: Sequence[str],
) -> list[int]:
    """Return the frozen target-independent order for the 55 training rows."""

    if len(semantic_ids) != len(performed_row_ids) or len(semantic_ids) < 1:
        raise ValueError("prefix identities must be nonempty equal-length sequences")
    if len(set(performed_row_ids)) != len(performed_row_ids):
        raise ValueError("performed row IDs must be unique")

    def key(index: int) -> str:
        payload = (
            PREFIX_SALT.encode("utf-8")
            + b"\0"
            + str(semantic_ids[index]).encode("utf-8")
            + b"\0"
            + str(performed_row_ids[index]).encode("utf-8")
        )
        return hashlib.sha256(payload).hexdigest()

    return sorted(range(len(semantic_ids)), key=lambda index: (key(index), index))


def channel_derangement_indices(channel_names: Sequence[str]) -> list[int]:
    """Map each source channel to the next hash-ordered destination slot."""

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


def apply_time_displacement(signals, input_lengths, *, offset_samples: int = 100):
    np = _require_numpy()
    values = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or lengths.shape != (len(values),):
        raise ValueError("time displacement requires signals and matching lengths")
    if offset_samples != 100:
        raise ValueError("registered time displacement is exactly 100 samples")
    output = np.zeros_like(values)
    lost_valid_samples = 0
    for index, length_value in enumerate(lengths):
        length = int(length_value)
        copied = max(0, length - offset_samples)
        if copied:
            output[index, :, offset_samples:length] = values[index, :, :copied]
        lost_valid_samples += min(length, offset_samples)
    return output, {
        "offset_samples": offset_samples,
        "offset_seconds": 1.0,
        "wrapping": False,
        "lost_valid_samples_per_channel": lost_valid_samples,
        "lost_values_total": lost_valid_samples * values.shape[1],
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


def zero_valid_signals(signals):
    np = _require_numpy()
    values = np.asarray(signals)
    if values.ndim != 3:
        raise ValueError("zero-signal control requires a three-dimensional array")
    return np.zeros(values.shape, dtype="float32")


def derange_train_targets(
    target_token_ids,
    target_lengths,
    target_texts: Sequence[str],
    semantic_ids: Sequence[str],
):
    """Assign every signal the next hash-ordered train target, with no fixed point."""

    np = _require_numpy()
    ids = [str(value) for value in semantic_ids]
    if len(ids) < 2 or len(ids) != len(set(ids)):
        raise ValueError("target derangement requires unique semantic IDs")
    ordered = sorted(
        range(len(ids)),
        key=lambda index: (_salted_hash(TRAIN_TARGET_SALT, ids[index]), ids[index]),
    )
    source_for_signal = list(range(len(ids)))
    for position, signal_index in enumerate(ordered):
        source_for_signal[signal_index] = ordered[(position + 1) % len(ordered)]
    if any(source == index for index, source in enumerate(source_for_signal)):
        raise RuntimeError("train-target derangement unexpectedly contains a fixed point")
    token_ids = np.asarray(target_token_ids)[source_for_signal].copy()
    lengths = np.asarray(target_lengths)[source_for_signal].copy()
    texts = [str(target_texts[source]) for source in source_for_signal]
    return token_ids, lengths, texts, source_for_signal


def derange_validation_predictions(
    predictions: Sequence[str], item_ids: Sequence[str]
) -> tuple[list[str], list[int]]:
    ids = [str(value) for value in item_ids]
    values = [str(value) for value in predictions]
    if len(ids) < 2 or len(ids) != len(values) or len(ids) != len(set(ids)):
        raise ValueError("validation derangement requires unique IDs and matching predictions")
    ordered = sorted(
        range(len(ids)),
        key=lambda index: (_salted_hash(VALIDATION_ROW_SALT, ids[index]), ids[index]),
    )
    source_for_destination = list(range(len(ids)))
    for position, source_index in enumerate(ordered):
        destination_index = ordered[(position + 1) % len(ordered)]
        source_for_destination[destination_index] = source_index
    if any(source == index for index, source in enumerate(source_for_destination)):
        raise RuntimeError("validation-row derangement unexpectedly contains a fixed point")
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
    if len(ids) != 6 or len(values) != 6 or len(lengths) != 6:
        raise ValueError("every registered prediction set must contain exactly six rows")
    if len(set(ids)) != 6:
        raise ValueError("prediction item IDs must be unique")
    payload = {
        "schema": {"name": "neurodecodekit.loop26_prediction_payload", "version": 0},
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
    prediction_payload_sha256 = _sha256_json({"item_ids": ids, "predictions": values})
    return {
        "condition_id": str(condition_id),
        "configuration_sha256": _sha256_json(dict(configuration)),
        "checkpoint_sha256_or_no_checkpoint_reason": str(checkpoint_sha256_or_reason),
        "transform_sha256_or_identity": (
            "identity" if dict(transform) == {"name": "identity"} else _sha256_json(dict(transform))
        ),
        "ordered_item_ids_sha256": _sha256_json(ids),
        "prediction_payload_sha256": prediction_payload_sha256,
        "lengths_sha256": _sha256_json(lengths),
        "runtime_sec": float(runtime_sec),
        "peak_rss_bytes": int(peak_rss_bytes),
        "model_run_count": int(model_run_count),
        "warnings": [str(value) for value in warnings],
        "private_payload_bytes": int(output.stat().st_size),
        "private_payload_file_sha256": _file_sha256(output),
    }


def load_prediction_payload(path: str | Path, freeze_row: Mapping[str, Any]) -> dict[str, Any]:
    """Load one private payload only when every frozen identity still matches."""

    payload_path = Path(path)
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    if payload.get("condition_id") != freeze_row.get("condition_id"):
        raise ValueError("prediction condition does not match freeze row")
    if _file_sha256(payload_path) != freeze_row.get("private_payload_file_sha256"):
        raise ValueError("prediction file hash does not match freeze row")
    expected = _sha256_json(
        {"item_ids": payload.get("item_ids"), "predictions": payload.get("predictions")}
    )
    if expected != freeze_row.get("prediction_payload_sha256"):
        raise ValueError("prediction payload hash does not match freeze row")
    if _sha256_json(payload.get("item_ids")) != freeze_row.get("ordered_item_ids_sha256"):
        raise ValueError("prediction item order does not match freeze row")
    if _sha256_json(payload.get("input_lengths")) != freeze_row.get("lengths_sha256"):
        raise ValueError("prediction lengths do not match freeze row")
    if _sha256_json(payload.get("configuration")) != freeze_row.get("configuration_sha256"):
        raise ValueError("prediction configuration does not match freeze row")
    if payload.get("checkpoint_sha256_or_reason") != freeze_row.get(
        "checkpoint_sha256_or_no_checkpoint_reason"
    ):
        raise ValueError("prediction checkpoint identity does not match freeze row")
    transform = payload.get("transform")
    transform_identity = (
        "identity" if transform == {"name": "identity"} else _sha256_json(transform)
    )
    if transform_identity != freeze_row.get("transform_sha256_or_identity"):
        raise ValueError("prediction transform does not match freeze row")
    return payload


def build_prediction_freeze_record(
    *,
    contract_sha256: str,
    authorization_decision_sha256: str,
    implementation_commit: str,
    prediction_rows: Iterable[Mapping[str, Any]],
    access_counters: Mapping[str, int],
    generated_artifact_bytes: int,
    checkpoint_bytes: int,
    prediction_payload_bytes: int,
    parameter_update_runtime_sec: float,
    end_to_end_runtime_sec: float,
    peak_rss_bytes: int,
    warnings: Sequence[str],
) -> dict[str, Any]:
    rows = [dict(value) for value in prediction_rows]
    record = {
        "schema_name": "neurodecodekit.loop26_prediction_freeze",
        "schema_version": "0.1.0",
        "status": "predictions_frozen_targets_unavailable",
        "proof_posture": "hash_only_prediction_freeze_no_validation_targets_or_scores",
        "contract_sha256": str(contract_sha256),
        "authorization_decision_sha256": str(authorization_decision_sha256),
        "implementation_commit": str(implementation_commit),
        "prediction_set_count": len(rows),
        "prediction_sets": sorted(rows, key=lambda row: row["condition_id"]),
        "primary_aliases": {
            "L31-E00": candidate_prediction_id(55, 2601),
            "L31-E01": prior_prediction_id(55),
        },
        "access_counters": {str(key): int(value) for key, value in access_counters.items()},
        "resources": {
            "generated_artifact_bytes": int(generated_artifact_bytes),
            "checkpoint_bytes": int(checkpoint_bytes),
            "prediction_payload_bytes": int(prediction_payload_bytes),
            "parameter_update_runtime_sec": float(parameter_update_runtime_sec),
            "end_to_end_runtime_sec": float(end_to_end_runtime_sec),
            "peak_rss_bytes": int(peak_rss_bytes),
        },
        "validation_target_rows_delivered": 0,
        "validation_scoring_runs": 0,
        "plaintext_predictions_committed": False,
        "warnings": [str(value) for value in warnings],
    }
    validate_prediction_freeze_record(record)
    return record


def validate_prediction_freeze_record(record: Mapping[str, Any]) -> None:
    if record.get("schema_name") != "neurodecodekit.loop26_prediction_freeze":
        raise ValueError("unsupported Loop 26 prediction-freeze schema")
    if record.get("schema_version") != "0.1.0":
        raise ValueError("unsupported Loop 26 prediction-freeze version")
    rows = record.get("prediction_sets")
    if not isinstance(rows, list) or len(rows) != 31:
        raise ValueError("prediction freeze must contain exactly 31 sets")
    by_id = {str(row.get("condition_id")): row for row in rows}
    if len(by_id) != 31 or set(by_id) != set(expected_prediction_ids()):
        raise ValueError("prediction freeze condition inventory is incomplete or duplicated")
    required = {
        "condition_id",
        "configuration_sha256",
        "checkpoint_sha256_or_no_checkpoint_reason",
        "transform_sha256_or_identity",
        "ordered_item_ids_sha256",
        "prediction_payload_sha256",
        "lengths_sha256",
        "runtime_sec",
        "peak_rss_bytes",
        "model_run_count",
        "warnings",
    }
    item_hashes = set()
    for row in rows:
        if not required <= set(row):
            raise ValueError(f"prediction freeze row lacks fields: {row.get('condition_id')}")
        if any(key in row for key in ("prediction", "predictions", "target", "targets", "text")):
            raise ValueError("committed prediction freeze must not contain plaintext")
        item_hashes.add(row["ordered_item_ids_sha256"])
    if len(item_hashes) != 1:
        raise ValueError("all prediction sets must share one ordered six-item identity")
    if record.get("prediction_set_count") != 31:
        raise ValueError("prediction set count does not match inventory")
    if record.get("validation_target_rows_delivered") != 0:
        raise ValueError("prediction freeze cannot record validation target delivery")
    if record.get("validation_scoring_runs") != 0:
        raise ValueError("prediction freeze cannot contain validation scoring")
    if record.get("plaintext_predictions_committed") is not False:
        raise ValueError("prediction freeze must declare no committed plaintext")


def score_shared_validation(
    *,
    prediction_payloads: Mapping[str, Mapping[str, Any]],
    target_item_ids: Sequence[str],
    targets: Sequence[str],
) -> dict[str, Any]:
    """Score all 31 frozen sets together without returning plaintext text."""

    started_at = time.perf_counter()
    ids = [str(value) for value in target_item_ids]
    target_values = [normalize_text(str(value)) for value in targets]
    if len(ids) != 6 or len(target_values) != 6 or len(set(ids)) != 6:
        raise ValueError("isolated scoring requires six unique ordered validation items")
    if set(prediction_payloads) != set(expected_prediction_ids()):
        raise ValueError("isolated scoring requires all 31 prediction sets together")
    metrics: dict[str, dict[str, Any]] = {}
    for condition_id in expected_prediction_ids():
        payload = prediction_payloads[condition_id]
        if [str(value) for value in payload.get("item_ids", [])] != ids:
            raise ValueError(f"prediction item order mismatch for {condition_id}")
        predictions = [normalize_text(str(value)) for value in payload.get("predictions", [])]
        if len(predictions) != 6:
            raise ValueError(f"prediction set {condition_id} does not contain six rows")
        metrics[condition_id] = _condition_metrics(
            ids,
            target_values,
            predictions,
            blank_fraction=payload.get("blank_fraction"),
        )

    primary_id = candidate_prediction_id(55, 2601)
    prior_id = prior_prediction_id(55)
    comparisons = {}
    aliases = {"L31-E00": primary_id, "L31-E01": prior_id}
    for control_id in REQUIRED_EXACT_CONTROL_IDS:
        comparator_id = aliases.get(control_id, control_id)
        comparisons[control_id] = _paired_exact_comparison(
            metrics[primary_id], metrics[comparator_id]
        )
    primary = comparisons["L31-E01"]
    primary_margin = (
        metrics[prior_id]["macro_sentence_cer"] - metrics[primary_id]["macro_sentence_cer"]
    )
    exact_controls_pass = all(row["one_sided_greater_p"] <= 0.05 for row in comparisons.values())
    primary_pass = (
        primary_margin >= 0.05
        and primary["wins"] == 6
        and primary["ties"] == 0
        and primary["losses"] == 0
        and primary["one_sided_greater_p"] <= 0.05
    )
    linear_pass = (
        metrics[primary_id]["macro_sentence_cer"] < metrics["L31-E09"]["macro_sentence_cer"]
    )
    scaling = _scaling_gate(metrics)
    overall = primary_pass and exact_controls_pass and linear_pass and scaling["passed"]
    return {
        "schema_name": "neurodecodekit.loop26_shared_validation_score",
        "schema_version": "0.1.0",
        "status": "passed" if overall else "parked_registered_gate_failed",
        "proof_posture": "one_same_person_same_session_shared_validation_scoring_event",
        "validation_items": 6,
        "condition_count": 31,
        "primary_candidate_prediction_id": primary_id,
        "primary_prior_prediction_id": prior_id,
        "condition_metrics": metrics,
        "exact_comparisons": comparisons,
        "primary_macro_cer_margin": primary_margin,
        "primary_gate_passed": primary_pass,
        "required_exact_controls_passed": exact_controls_pass,
        "linear_comparator_gate_passed": linear_pass,
        "scaling_gate": scaling,
        "intersection_union_gate_passed": overall,
        "plaintext_targets_or_predictions_present": False,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "warnings": [
            "same_person_same_session_six_sentence_result",
            "upstream_cache_is_offline_noncausal",
            "brain_specific_origin_unavailable_before_peripheral_controls",
            "no_source_test_session2_unseen_person_realtime_portable_or_clinical_claim",
        ],
    }


def _condition_metrics(
    item_ids: Sequence[str],
    targets: Sequence[str],
    predictions: Sequence[str],
    *,
    blank_fraction: float | None,
) -> dict[str, Any]:
    per_item = []
    total_character_edits = 0
    total_characters = 0
    total_word_edits = 0
    total_words = 0
    exact_count = 0
    for item_id, target, prediction in zip(item_ids, targets, predictions, strict=True):
        character_edits = levenshtein_distance(target, prediction)
        word_edits = levenshtein_distance(target.split(), prediction.split())
        cer = character_error_rate(target, prediction, normalize=False)
        exact = sentence_exact_match(target, prediction, normalize=False)
        total_character_edits += character_edits
        total_characters += len(target)
        total_word_edits += word_edits
        total_words += len(target.split())
        exact_count += int(exact)
        per_item.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "character_edits": character_edits,
                "cer": cer,
                "word_edits": word_edits,
                "exact": exact,
                "target_characters": len(target),
                "target_words": len(target.split()),
            }
        )
    return {
        "per_item": per_item,
        "macro_sentence_cer": statistics.fmean(row["cer"] for row in per_item),
        "corpus_cer": total_character_edits / total_characters,
        "corpus_wer": total_word_edits / total_words,
        "exact_sentence_count": exact_count,
        "blank_fraction": None if blank_fraction is None else float(blank_fraction),
    }


def _paired_exact_comparison(
    candidate: Mapping[str, Any], comparator: Mapping[str, Any]
) -> dict[str, Any]:
    candidate_cer = [float(row["cer"]) for row in candidate["per_item"]]
    comparator_cer = [float(row["cer"]) for row in comparator["per_item"]]
    differences = [b - a for a, b in zip(candidate_cer, comparator_cer, strict=True)]
    observed = statistics.fmean(differences)
    null_statistics = []
    for assignment in range(64):
        signed = [
            value if assignment & (1 << index) else -value
            for index, value in enumerate(differences)
        ]
        null_statistics.append(statistics.fmean(signed))
    tolerance = 1e-15
    greater = sum(value >= observed - tolerance for value in null_statistics) / 64
    less = sum(value <= observed + tolerance for value in null_statistics) / 64
    return {
        "differences": differences,
        "observed_mean_difference": observed,
        "null_statistics_binary_order": null_statistics,
        "one_sided_greater_p": greater,
        "two_sided_p": min(1.0, 2 * min(greater, less)),
        "wins": sum(value > 0 for value in differences),
        "ties": sum(value == 0 for value in differences),
        "losses": sum(value < 0 for value in differences),
    }


def _scaling_gate(metrics: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    medians = {}
    seed_slopes = {}
    for size in PREFIX_SIZES:
        values = [
            float(metrics[candidate_prediction_id(size, seed)]["macro_sentence_cer"])
            for seed in SEEDS
        ]
        medians[str(size)] = statistics.median(values)
    x_values = [math.log2(size) for size in PREFIX_SIZES]
    for seed in SEEDS:
        y_values = [
            float(metrics[candidate_prediction_id(size, seed)]["macro_sentence_cer"])
            for size in PREFIX_SIZES
        ]
        seed_slopes[str(seed)] = _ols_slope(x_values, y_values)
    small_mean = statistics.fmean(medians[str(size)] for size in (8, 16))
    upper_mean = statistics.fmean(medians[str(size)] for size in (44, 55))
    prior_gain = float(metrics[prior_prediction_id(55)]["macro_sentence_cer"]) - medians["55"]
    rules = {
        "smallest_to_upper_macro_cer_gain": small_mean - upper_mean,
        "smallest_to_upper_gain_at_least_0_05": small_mean - upper_mean >= 0.05,
        "size55_gain_over_matched_prior": prior_gain,
        "size55_gain_over_matched_prior_at_least_0_05": prior_gain >= 0.05,
        "every_seed_ols_slope_negative": all(value < 0 for value in seed_slopes.values()),
    }
    return {
        "prefix_sizes": list(PREFIX_SIZES),
        "median_seed_macro_sentence_cer": medians,
        "seed_ols_slopes": seed_slopes,
        "rules": rules,
        "passed": all(
            value
            for key, value in rules.items()
            if key.endswith("at_least_0_05") or key.endswith("negative")
        ),
        "formal_slope_p_value": None,
        "universal_scaling_claim_available": False,
    }


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


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if value > 10_000_000 else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Shared S21 controls require NumPy: `pip install numpy`.") from exc
    return np
