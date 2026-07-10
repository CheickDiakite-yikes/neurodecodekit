"""Preregistered language-model-free streaming CTC decoder gate."""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from neurodecodekit.decoding.ctc_prefix import (
    GreedyCTCDecoder,
    PrefixBeamCTCDecoder,
)
from neurodecodekit.evaluation.incremental_ctc import (
    fit_most_frequent_sequence_prior,
    paired_cer_reduction_bootstrap,
    partial_hypothesis_metrics,
    sequence_metrics,
)
from neurodecodekit.evaluation.metrics import levenshtein_distance
from neurodecodekit.experiments.causal_replay_gate import (
    REGISTERED_SCHEDULES,
    registered_chunk_sizes,
)
from neurodecodekit.models.tiny_causal_encoder import (
    canonical_partition_outputs,
    load_tiny_causal_encoder_checkpoint,
)
from neurodecodekit.training.ctc_symbol_stream import (
    PARTITION_NAMES,
    load_ctc_symbol_stream_manifest,
    load_ctc_symbol_stream_partition,
    registered_ctc_symbol_stream_protocol,
    resolve_ctc_symbol_partition_path,
)


STREAMING_CTC_GATE_SCHEMA_NAME = "b2q-streaming-ctc-prefix-gate"
STREAMING_CTC_GATE_SCHEMA_VERSION = 0
PROOF_POSTURE = "synthetic_streaming_ctc_decoder_only_no_language_model"
REGISTERED_CHECKPOINT_SHA256 = (
    "75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1"
)
REGISTERED_PARAMETER_PAYLOAD_SHA256 = (
    "d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98"
)
REGISTERED_CONFIG_SHA256 = (
    "8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2"
)
REGISTERED_PARAMETER_COUNT = 1130
BEAM_WIDTH = 8
MAX_PREFIX_LENGTH = 12
BLANK_ID = 0
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 2322
MAX_PREFIX_CER = 0.10
MIN_EXACT_ACCURACY = 0.75
MIN_REPEAT_RATE = 0.75
MIN_CER_REDUCTION = 0.40
MIN_EXACT_GAIN = 0.50
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
CTC_PAPER = "https://www.cs.toronto.edu/~graves/icml_2006.pdf"
INCREMENTAL_METRICS_PAPER = "https://aclanthology.org/N09-1043/"
PARTIAL_STABILITY_PAPER = (
    "https://research.google/pubs/"
    "analyzing-the-quality-and-stability-of-a-streaming-end-to-end-on-device-speech-recognizer/"
)


@dataclass(frozen=True)
class StreamingCTCGateCaps:
    max_fixture_bytes: int = 1 * 1024 * 1024
    max_items: int = 64
    max_samples_per_item: int = 128
    max_total_frames: int = 2048
    max_encoder_state_bytes: int = 1 * 1024
    max_decoder_state_bytes: int = 4 * 1024
    max_working_bytes: int = 16 * 1024 * 1024
    max_runtime_sec: float = 20.0
    max_peak_rss_bytes: int = 768 * 1024 * 1024
    max_artifact_bytes: int = 1 * 1024 * 1024
    max_total_pushes: int = 50_000

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def registered_streaming_ctc_gate_caps() -> StreamingCTCGateCaps:
    return StreamingCTCGateCaps()


def run_streaming_ctc_gate(
    *,
    fixture_manifest_path: str | Path,
    checkpoint_path: str | Path,
    out_json_path: str | Path,
    out_markdown_path: str | Path | None = None,
    require_registered_protocol: bool = True,
    require_registered_checkpoint: bool = True,
    caps: StreamingCTCGateCaps | None = None,
) -> dict[str, Any]:
    """Run validation replay, then one conditional canonical test evaluation."""

    started_at = time.perf_counter()
    selected_caps = caps or registered_streaming_ctc_gate_caps()
    _validate_caps(selected_caps)
    thread_environment = _require_single_thread_environment()
    manifest_path = Path(fixture_manifest_path)
    frozen_checkpoint_path = Path(checkpoint_path)
    json_path = Path(out_json_path)
    markdown_path = Path(out_markdown_path) if out_markdown_path else None
    _prepare_outputs([json_path, markdown_path])
    access_events: list[dict[str, object]] = []

    manifest = load_ctc_symbol_stream_manifest(
        manifest_path,
        require_registered_protocol=require_registered_protocol,
    )
    access_events.append(
        _access_event(
            access_events,
            stage="manifest_validation",
            split=None,
            action="compact_manifest_opened_no_partition_array",
        )
    )
    protocol = registered_ctc_symbol_stream_protocol()
    protocol_match = manifest["protocol"] == protocol.to_dict()
    fixture_bytes = int(manifest["artifacts"]["total_fixture_bytes"])
    total_items = sum(
        int(manifest["partitions"][split]["items"]) for split in PARTITION_NAMES
    )
    total_frames = sum(
        int(manifest["partitions"][split]["valid_frames"])
        for split in PARTITION_NAMES
    )
    max_samples = max(
        int(manifest["partitions"][split]["signals_shape"][2])
        for split in PARTITION_NAMES
    )
    if fixture_bytes > selected_caps.max_fixture_bytes:
        raise ValueError("Loop 23 fixture exceeds its byte cap")
    if total_items > selected_caps.max_items:
        raise ValueError("Loop 23 fixture exceeds its item cap")
    if total_frames > selected_caps.max_total_frames:
        raise ValueError("Loop 23 fixture exceeds its frame cap")
    if max_samples > selected_caps.max_samples_per_item:
        raise ValueError("Loop 23 fixture exceeds its sample cap")

    checkpoint_sha256 = _file_sha256(frozen_checkpoint_path)
    if require_registered_checkpoint and checkpoint_sha256 != REGISTERED_CHECKPOINT_SHA256:
        raise ValueError("Loop 23 checkpoint does not match the registered file hash")
    producer, checkpoint_metadata = load_tiny_causal_encoder_checkpoint(
        frozen_checkpoint_path
    )
    checkpoint_match = bool(
        checkpoint_sha256 == REGISTERED_CHECKPOINT_SHA256
        and producer.parameter_payload_sha256 == REGISTERED_PARAMETER_PAYLOAD_SHA256
        and checkpoint_metadata.get("config_sha256") == REGISTERED_CONFIG_SHA256
        and producer.trainable_parameter_count == REGISTERED_PARAMETER_COUNT
    )
    if require_registered_checkpoint and not checkpoint_match:
        raise ValueError("Loop 23 checkpoint metadata does not match preregistration")
    if (
        producer.n_channels != protocol.n_channels
        or producer.kernel_size != protocol.kernel_size
        or producer.stride != protocol.stride
        or producer.n_classes != protocol.n_classes
        or producer.embedding_dim != 8
    ):
        raise ValueError("Loop 23 checkpoint geometry does not match the fixture")
    access_events.append(
        _access_event(
            access_events,
            stage="checkpoint_validation",
            split=None,
            action="frozen_checkpoint_hashed_loaded_no_parameter_update",
            checkpoint_sha256=checkpoint_sha256,
        )
    )

    train = _open_partition(
        manifest_path,
        manifest,
        "train",
        access_mode="targets-only",
        access_events=access_events,
        stage="train_targets_open",
    )
    train_targets = _partition_targets(train)
    prior_sequence = fit_most_frequent_sequence_prior(train_targets)
    access_events.append(
        _access_event(
            access_events,
            stage="prior_fit",
            split="train",
            action="most_frequent_complete_sequence_fit_from_train_targets_only",
        )
    )
    validation = _open_partition(
        manifest_path,
        manifest,
        "validation",
        access_mode="full",
        access_events=access_events,
        stage="validation_open",
    )
    validation_report = _canonical_partition_decode(producer, validation)
    validation_targets = validation_report["targets"]
    validation_prior_predictions = [prior_sequence] * len(validation_targets)
    validation_prior = sequence_metrics(
        validation_targets, validation_prior_predictions
    )
    validation_zero_predictions = _zero_signal_predictions(producer, validation)
    validation_zero = sequence_metrics(
        validation_targets, validation_zero_predictions
    )
    replay = _run_validation_replay(
        producer,
        validation,
        validation_report,
        max_total_pushes=selected_caps.max_total_pushes,
        max_chunk_samples=selected_caps.max_samples_per_item,
    )
    state_gate = bool(
        replay["max_encoder_state_bytes"] <= selected_caps.max_encoder_state_bytes
        and replay["max_prefix_state_bytes"] <= selected_caps.max_decoder_state_bytes
        and validation_report["max_prefix_state_bytes"]
        <= selected_caps.max_decoder_state_bytes
    )
    pretest_runtime = time.perf_counter() - started_at
    pretest_peak_rss = _peak_rss_bytes()
    pretest_working_bytes = int(
        _partition_array_bytes(train)
        + _partition_array_bytes(validation)
        + producer.fixed_parameter_bytes
        + replay["max_encoder_state_bytes"]
        + replay["max_prefix_state_bytes"]
    )
    pretest_resource_gate = bool(
        pretest_runtime <= selected_caps.max_runtime_sec
        and pretest_peak_rss is not None
        and pretest_peak_rss <= selected_caps.max_peak_rss_bytes
        and pretest_working_bytes <= selected_caps.max_working_bytes
        and state_gate
    )
    validation_gate = _validation_gate(
        validation_report["prefix_metrics"],
        validation_report["greedy_metrics"],
        validation_prior,
        validation_zero,
        replay_passed=bool(replay["passed"]),
        resource_passed=pretest_resource_gate,
    )
    access_events.append(
        _access_event(
            access_events,
            stage="decoder_config_freeze",
            split="validation",
            action="registered_decoder_config_hashed_after_validation_no_tuning",
            decoder_config_sha256=_decoder_config_sha256(),
        )
    )

    test = None
    test_report: dict[str, Any] | None = None
    test_prior: dict[str, Any] | None = None
    test_zero: dict[str, Any] | None = None
    bootstrap_prior: dict[str, Any] | None = None
    bootstrap_zero: dict[str, Any] | None = None
    test_gate: dict[str, Any] = {
        "opened": False,
        "passed": False,
        "reason": "validation_or_pretest_gate_failed_test_remained_unopened",
    }
    if validation_gate["passed"]:
        test = _open_partition(
            manifest_path,
            manifest,
            "test",
            access_mode="full",
            access_events=access_events,
            stage="frozen_test_open",
            checkpoint_sha256=checkpoint_sha256,
        )
        test_report = _canonical_partition_decode(producer, test)
        test_targets = test_report["targets"]
        test_prior_predictions = [prior_sequence] * len(test_targets)
        test_prior = sequence_metrics(test_targets, test_prior_predictions)
        test_zero_predictions = _zero_signal_predictions(producer, test)
        test_zero = sequence_metrics(test_targets, test_zero_predictions)
        bootstrap_prior = paired_cer_reduction_bootstrap(
            test_targets,
            test_report["prefix_predictions"],
            test_prior_predictions,
            resamples=BOOTSTRAP_RESAMPLES,
            seed=BOOTSTRAP_SEED,
        )
        bootstrap_zero = paired_cer_reduction_bootstrap(
            test_targets,
            test_report["prefix_predictions"],
            test_zero_predictions,
            resamples=BOOTSTRAP_RESAMPLES,
            seed=BOOTSTRAP_SEED,
        )
        test_gate = _test_gate(
            test_report["prefix_metrics"],
            test_report["greedy_metrics"],
            test_prior,
            test_zero,
            bootstrap_prior,
            bootstrap_zero,
        )
        access_events.append(
            _access_event(
                access_events,
                stage="frozen_test_evaluation",
                split="test",
                action="single_canonical_decoder_and_controls_completed_no_fit",
                checkpoint_sha256=checkpoint_sha256,
            )
        )

    runtime_before_report = time.perf_counter() - started_at
    peak_rss = _peak_rss_bytes()
    loaded_array_bytes = _partition_array_bytes(train)
    loaded_array_bytes += _partition_array_bytes(validation)
    if test is not None:
        loaded_array_bytes += _partition_array_bytes(test)
    working_core_bytes = int(
        loaded_array_bytes
        + producer.fixed_parameter_bytes
        + replay["max_encoder_state_bytes"]
        + replay["max_prefix_state_bytes"]
    )
    resource_gate = bool(
        runtime_before_report <= selected_caps.max_runtime_sec
        and peak_rss is not None
        and peak_rss <= selected_caps.max_peak_rss_bytes
        and working_core_bytes <= selected_caps.max_working_bytes
        and state_gate
    )
    test_open_count = _partition_open_count(access_events, "test")
    access_gate = _access_sequence_passed(
        access_events,
        test_opened=test is not None,
    )
    mechanical_gate = bool(
        validation_gate["passed"]
        and test_gate["passed"]
        and resource_gate
        and access_gate
        and producer.producer_right_context_samples == 0
    )
    base_gate = bool(
        mechanical_gate
        and protocol_match
        and checkpoint_match
        and require_registered_protocol
        and require_registered_checkpoint
    )
    report: dict[str, Any] = {
        "schema": {
            "name": STREAMING_CTC_GATE_SCHEMA_NAME,
            "version": STREAMING_CTC_GATE_SCHEMA_VERSION,
        },
        "proof_posture": PROOF_POSTURE,
        "gate_passed": base_gate,
        "mechanical_gate_passed": mechanical_gate,
        "decision": _gate_decision(
            gate_passed=base_gate,
            mechanical_gate_passed=mechanical_gate,
            registered_protocol_match=protocol_match,
            registered_checkpoint_match=checkpoint_match,
            artifact_gate_passed=None,
        ),
        "registered_protocol_match": protocol_match,
        "registered_checkpoint_match": checkpoint_match,
        "fixture": {
            "manifest_path": str(manifest_path),
            "manifest_sha256": _file_sha256(manifest_path),
            "protocol_sha256": manifest["protocol_sha256"],
            "total_bytes": fixture_bytes,
            "total_items": total_items,
            "total_frames": total_frames,
            "max_samples_per_item": max_samples,
            "partitions": manifest["partitions"],
            "raw_data_reads": 0,
            "real_data_reads": 0,
            "natural_text_reads": 0,
            "network_fetches": 0,
        },
        "checkpoint": {
            "path": str(frozen_checkpoint_path),
            "bytes": frozen_checkpoint_path.stat().st_size,
            "sha256": checkpoint_sha256,
            "parameter_payload_sha256": producer.parameter_payload_sha256,
            "config_sha256": checkpoint_metadata.get("config_sha256"),
            "trainable_parameters": producer.trainable_parameter_count,
            "parameter_updates": 0,
            "training_runs": 0,
            "probe_trained_with_ctc_loss": False,
        },
        "decoder": {
            "blank_id": BLANK_ID,
            "symbols": manifest["symbols"],
            "greedy_comparator": True,
            "prefix_primary": True,
            "beam_width": BEAM_WIDTH,
            "max_prefix_length": MAX_PREFIX_LENGTH,
            "language_model": None,
            "lexicon": None,
            "insertion_bonus": 0.0,
            "score_threshold": None,
            "tie_break": "score_desc_then_token_tuple_lexicographic",
            "config_sha256": _decoder_config_sha256(),
            "right_context_samples": 0,
            "online_commit_policy": None,
            "known_item_end_flush": True,
            "live_endpoint_detector": False,
        },
        "train_only_prior": {
            "opened_members": list(train.opened_members),
            "signals_opened": train.signals is not None,
            "fitted_sequence": list(prior_sequence),
            "fit_items": len(train_targets),
            "fit_split": "train",
        },
        "validation": {
            **validation_report,
            "prior": validation_prior,
            "zero_signal": validation_zero,
            "gate": validation_gate,
            "used_for_decoder_tuning": False,
        },
        "streaming_replay": replay,
        "frozen_test": {
            "opened": test is not None,
            "semantic_open_count": test_open_count,
            "canonical": test_report,
            "prior": test_prior,
            "zero_signal": test_zero,
            "bootstrap_vs_prior": bootstrap_prior,
            "bootstrap_vs_zero_signal": bootstrap_zero,
            "gate": test_gate,
            "model_or_decoder_fit_after_open": False,
            "schedule_replay_after_open": False,
        },
        "access_audit": {
            "passed": access_gate,
            "events": access_events,
            "train_semantic_open_count": _partition_open_count(access_events, "train"),
            "validation_semantic_open_count": _partition_open_count(
                access_events, "validation"
            ),
            "test_semantic_open_count": test_open_count,
        },
        "resources": {
            "runtime_before_report_write_sec": round(runtime_before_report, 6),
            "pretest_runtime_sec": round(pretest_runtime, 6),
            "peak_rss_bytes": peak_rss,
            "pretest_peak_rss_bytes": pretest_peak_rss,
            "pretest_working_core_bytes": pretest_working_bytes,
            "working_core_bytes_before_framework_temporaries": working_core_bytes,
            "loaded_partition_array_bytes": loaded_array_bytes,
            "fixed_model_and_normalization_bytes": producer.fixed_parameter_bytes,
            "max_encoder_state_bytes": replay["max_encoder_state_bytes"],
            "max_prefix_state_bytes": replay["max_prefix_state_bytes"],
            "max_greedy_state_bytes": replay["max_greedy_state_bytes"],
            "thread_environment": thread_environment,
            "caps": selected_caps.to_dict(),
            "resource_gate_passed": resource_gate,
        },
        "execution_counts": {
            "training_runs": 0,
            "parameter_updates": 0,
            "decoder_configs": 1,
            "language_model_runs": 0,
            "validation_schedule_replays": len(REGISTERED_SCHEDULES),
            "test_schedule_replays": 0,
            "test_partition_opens": test_open_count,
            "raw_data_reads": 0,
            "real_data_reads": 0,
            "network_fetches": 0,
        },
        "research_sources": {
            "ctc": CTC_PAPER,
            "incremental_metrics": INCREMENTAL_METRICS_PAPER,
            "partial_stability": PARTIAL_STABILITY_PAPER,
        },
        "warnings": [
            "synthetic_symbol_task_not_natural_text",
            "frozen_probe_not_trained_with_ctc_loss",
            "prefix_partials_are_revocable_no_online_commit_policy",
            "known_item_end_is_not_live_endpoint_detection",
            "synthetic_cer_is_not_meg_eeg_or_language_performance",
            "end_to_end_latency_unmeasured",
            "real_neural_holdouts_remain_frozen",
        ],
        "claim_boundaries": [
            "The source motifs are generated, not neural recordings.",
            "The output alphabet is five synthetic symbols, not natural text.",
            "No language model, lexicon, word metric, or semantic metric is used.",
            "Stable-correct timing is retrospective and not an online commitment.",
            "Flush uses a known item end and is not a live endpoint detector.",
            "No real MEG/EEG, unseen-person, portable, clinical, or arbitrary-thought claim follows.",
        ],
        "artifacts": {
            "json_path": str(json_path),
            "markdown_path": str(markdown_path) if markdown_path else None,
            "json_bytes": 0,
            "markdown_bytes": 0,
            "total_artifact_bytes": 0,
            "artifact_gate_passed": False,
        },
    }
    json_text, markdown_text = _finalize_report_texts(
        report,
        markdown_requested=markdown_path is not None,
        max_artifact_bytes=selected_caps.max_artifact_bytes,
        base_gate_passed=base_gate,
    )
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json_text, encoding="utf-8")
    if markdown_path is not None and markdown_text is not None:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown_text, encoding="utf-8")
    return report


def _open_partition(
    manifest_path: Path,
    manifest: Mapping[str, Any],
    split: str,
    *,
    access_mode: str,
    access_events: list[dict[str, object]],
    stage: str,
    checkpoint_sha256: str | None = None,
):
    path = resolve_ctc_symbol_partition_path(manifest_path, manifest, split)
    partition = load_ctc_symbol_stream_partition(
        path,
        expected=manifest["partitions"][split],
        access_mode=access_mode,
    )
    access_events.append(
        _access_event(
            access_events,
            stage=stage,
            split=split,
            action=f"partition_opened_{access_mode}",
            path=str(path),
            sha256=manifest["partitions"][split]["sha256"],
            opened_members=list(partition.opened_members),
            checkpoint_sha256=checkpoint_sha256,
        )
    )
    return partition


def _canonical_partition_decode(producer, partition) -> dict[str, Any]:
    started_at = time.perf_counter()
    outputs = canonical_partition_outputs(producer, partition)
    targets = _partition_targets(partition)
    prefix_predictions = []
    greedy_predictions = []
    item_reports = []
    offset = 0
    max_prefix_state = 0
    max_greedy_state = 0
    for item_index, frame_count_value in enumerate(partition.frame_lengths.tolist()):
        frame_count = int(frame_count_value)
        item_logits = outputs["logits"][offset : offset + frame_count]
        frame_ends = outputs["frame_end_samples"][offset : offset + frame_count]
        item_report = _decode_item_logits(
            item_logits,
            frame_end_samples=frame_ends,
            availability_samples=frame_ends,
            target=targets[item_index],
            motif_end_samples=partition.motif_end_samples[
                item_index, : int(partition.target_lengths[item_index])
            ],
            sampling_rate_hz=producer.source_sampling_rate_hz,
        )
        item_report["item_id"] = str(partition.item_ids[item_index])
        prefix_predictions.append(tuple(item_report["prefix_final"]))
        greedy_predictions.append(tuple(item_report["greedy_final"]))
        max_prefix_state = max(max_prefix_state, item_report["max_prefix_state_bytes"])
        max_greedy_state = max(max_greedy_state, item_report["max_greedy_state_bytes"])
        item_reports.append(item_report)
        offset += frame_count
    if offset != len(outputs["logits"]):
        raise RuntimeError("Loop 23 canonical frame offsets drifted")
    runtime = time.perf_counter() - started_at
    duration = float(partition.input_lengths.sum() / producer.source_sampling_rate_hz)
    return {
        "targets": [list(row) for row in targets],
        "prefix_predictions": [list(row) for row in prefix_predictions],
        "greedy_predictions": [list(row) for row in greedy_predictions],
        "prefix_metrics": sequence_metrics(targets, prefix_predictions),
        "greedy_metrics": sequence_metrics(targets, greedy_predictions),
        "items": item_reports,
        "frames": int(partition.frame_lengths.sum()),
        "duration_sec": duration,
        "runtime_sec": round(runtime, 6),
        "real_time_factor": runtime / duration if duration else None,
        "embedding_payload_sha256": outputs["embedding_payload_sha256"],
        "logit_payload_sha256": _array_sha256(outputs["logits"]),
        "max_prefix_state_bytes": max_prefix_state,
        "max_greedy_state_bytes": max_greedy_state,
    }


def _decode_item_logits(
    logits,
    *,
    frame_end_samples,
    availability_samples,
    target,
    motif_end_samples,
    sampling_rate_hz: float,
) -> dict[str, Any]:
    np = _require_numpy()
    log_probabilities = _log_softmax(np.asarray(logits, dtype="float64"))
    greedy = GreedyCTCDecoder(
        blank_id=BLANK_ID, max_output_length=MAX_PREFIX_LENGTH
    )
    prefix = PrefixBeamCTCDecoder(
        beam_width=BEAM_WIDTH,
        blank_id=BLANK_ID,
        max_prefix_length=MAX_PREFIX_LENGTH,
    )
    trace = []
    prefix_rows = []
    greedy_rows = []
    previous_prefix: tuple[int, ...] = ()
    for frame_index, frame in enumerate(log_probabilities.tolist()):
        greedy_snapshot = greedy.push(frame)
        prefix_snapshot = prefix.push(frame)
        prefix_rows.append(prefix_snapshot.top_prefix)
        greedy_rows.append(greedy_snapshot.hypothesis)
        trace.append(
            {
                "frame_index": frame_index,
                "frame_end_sample": int(frame_end_samples[frame_index]),
                "availability_sample": int(availability_samples[frame_index]),
                "greedy": list(greedy_snapshot.hypothesis),
                "prefix": list(prefix_snapshot.top_prefix),
                "prefix_log_probability": prefix_snapshot.top_log_probability,
                "beam_size": prefix_snapshot.beam_size,
                "prefix_state_bytes": prefix_snapshot.state_payload_bytes,
                "greedy_state_bytes": greedy_snapshot.state_payload_bytes,
                "edit_from_previous_prefix": levenshtein_distance(
                    previous_prefix, prefix_snapshot.top_prefix
                ),
            }
        )
        previous_prefix = prefix_snapshot.top_prefix
    greedy_final = greedy.flush()
    prefix_final = prefix.flush()
    if prefix_rows[-1] != prefix_final or greedy_rows[-1] != greedy_final:
        raise RuntimeError("Loop 23 flush changed a final hypothesis")
    partial_metrics = partial_hypothesis_metrics(
        prefix_rows,
        final_hypothesis=prefix_final,
        frame_end_samples=frame_end_samples,
        availability_samples=availability_samples,
        sampling_rate_hz=sampling_rate_hz,
        motif_end_samples=motif_end_samples,
        target=target,
    )
    for row, common in zip(trace, partial_metrics["longest_common_prefix_by_frame"]):
        row["longest_common_prefix_with_final"] = int(common)
    return {
        "target": [int(value) for value in target],
        "prefix_final": list(prefix_final),
        "greedy_final": list(greedy_final),
        "trace": trace,
        "partial_metrics": partial_metrics,
        "max_prefix_state_bytes": prefix.max_state_payload_bytes,
        "max_greedy_state_bytes": greedy.max_state_payload_bytes,
    }


def _zero_signal_predictions(producer, partition) -> list[tuple[int, ...]]:
    np = _require_numpy()
    raw_mean_frame = np.repeat(
        producer.normalization_mean[:, None], producer.kernel_size, axis=1
    ).reshape(-1)
    embedding = producer.project_frame(raw_mean_frame)[0]
    logits = producer.probe_embedding(embedding)[0]
    log_probability = _log_softmax(logits.astype("float64", copy=False)[None, :])[0]
    predictions = []
    for frame_count_value in partition.frame_lengths.tolist():
        decoder = PrefixBeamCTCDecoder(
            beam_width=BEAM_WIDTH,
            blank_id=BLANK_ID,
            max_prefix_length=MAX_PREFIX_LENGTH,
        )
        for _ in range(int(frame_count_value)):
            decoder.push(log_probability.tolist())
        predictions.append(decoder.flush())
    return predictions


def _run_validation_replay(
    producer,
    partition,
    canonical: Mapping[str, Any],
    *,
    max_total_pushes: int,
    max_chunk_samples: int,
) -> dict[str, Any]:
    schedule_reports = []
    remaining_pushes = int(max_total_pushes)
    for schedule_name in REGISTERED_SCHEDULES:
        started_at = time.perf_counter()
        push_count = 0
        max_encoder_state = 0
        max_prefix_state = 0
        max_greedy_state = 0
        max_delay = 0
        prefix_finals = []
        traces_exact = True
        push_compute = 0.0
        for item_index, length_value in enumerate(partition.input_lengths.tolist()):
            length = int(length_value)
            sizes = registered_chunk_sizes(
                length,
                name=schedule_name,
                kernel_size=producer.kernel_size,
                stride=producer.stride,
            )
            push_count += len(sizes)
            if push_count > remaining_pushes:
                raise ValueError("Loop 23 replay exceeded remaining push cap")
            stream = producer.new_stream(
                max_chunk_samples=max_chunk_samples,
                max_total_samples=max_chunk_samples,
                max_total_tokens=64,
            )
            greedy = GreedyCTCDecoder(
                blank_id=BLANK_ID, max_output_length=MAX_PREFIX_LENGTH
            )
            prefix = PrefixBeamCTCDecoder(
                beam_width=BEAM_WIDTH,
                blank_id=BLANK_ID,
                max_prefix_length=MAX_PREFIX_LENGTH,
            )
            offset = 0
            prefix_trace = []
            greedy_trace = []
            frame_ends = []
            availability = []
            for size in sizes:
                push_started = time.perf_counter()
                batch = stream.push(
                    partition.signals[item_index, :, offset : offset + size]
                )
                push_compute += time.perf_counter() - push_started
                for token, end_sample, available_sample in zip(
                    batch.tokens,
                    batch.frame_end_samples,
                    batch.availability_samples,
                ):
                    logits = producer.probe_embedding(token)[0]
                    log_probability = _log_softmax(
                        logits.astype("float64", copy=False)[None, :]
                    )[0]
                    greedy_trace.append(greedy.push(log_probability.tolist()).hypothesis)
                    prefix_trace.append(prefix.push(log_probability.tolist()).top_prefix)
                    frame_ends.append(int(end_sample))
                    availability.append(int(available_sample))
                offset += size
            flush = stream.flush()
            expected_tail = length - (
                (int(partition.frame_lengths[item_index]) - 1) * producer.stride
                + producer.kernel_size
            )
            if flush.unframed_tail_samples != expected_tail:
                raise RuntimeError("Loop 23 replay tail disagrees with frame geometry")
            prefix_final = prefix.flush()
            greedy_final = greedy.flush()
            canonical_item = canonical["items"][item_index]
            canonical_prefix_trace = [
                tuple(row["prefix"]) for row in canonical_item["trace"]
            ]
            canonical_greedy_trace = [
                tuple(row["greedy"]) for row in canonical_item["trace"]
            ]
            traces_exact = bool(
                traces_exact
                and prefix_trace == canonical_prefix_trace
                and greedy_trace == canonical_greedy_trace
                and prefix_final == tuple(canonical_item["prefix_final"])
                and greedy_final == tuple(canonical_item["greedy_final"])
                and frame_ends
                == [int(row["frame_end_sample"]) for row in canonical_item["trace"]]
            )
            if any(value < end for value, end in zip(availability, frame_ends)):
                raise RuntimeError("Loop 23 transport availability became noncausal")
            max_delay = max(
                max_delay,
                max(
                    (value - end for value, end in zip(availability, frame_ends)),
                    default=0,
                ),
            )
            max_encoder_state = max(max_encoder_state, stream.max_mutable_state_bytes)
            max_prefix_state = max(max_prefix_state, prefix.max_state_payload_bytes)
            max_greedy_state = max(max_greedy_state, greedy.max_state_payload_bytes)
            prefix_finals.append(prefix_final)
        duration = float(partition.input_lengths.sum() / producer.source_sampling_rate_hz)
        final_outputs_exact = prefix_finals == [
            tuple(row) for row in canonical["prefix_predictions"]
        ]
        passed = bool(
            traces_exact
            and final_outputs_exact
            and max_encoder_state <= producer.mutable_state_bound_bytes
        )
        schedule_reports.append(
            {
                "name": schedule_name,
                "passed": passed,
                "push_count": push_count,
                "frames": int(partition.frame_lengths.sum()),
                "frame_indexed_partial_trace_exact": traces_exact,
                "final_outputs_exact": final_outputs_exact,
                "max_encoder_state_bytes": max_encoder_state,
                "max_prefix_state_bytes": max_prefix_state,
                "max_greedy_state_bytes": max_greedy_state,
                "right_context_samples": 0,
                "max_schedule_delay_sec": max_delay
                / producer.source_sampling_rate_hz,
                "producer_compute_real_time_factor": (
                    push_compute / duration if duration else None
                ),
                "runtime_sec": round(time.perf_counter() - started_at, 6),
            }
        )
        remaining_pushes -= push_count
    return {
        "passed": all(bool(row["passed"]) for row in schedule_reports),
        "registered_schedules": list(REGISTERED_SCHEDULES),
        "schedules_passed": sum(bool(row["passed"]) for row in schedule_reports),
        "total_pushes": max_total_pushes - remaining_pushes,
        "max_encoder_state_bytes": max(
            int(row["max_encoder_state_bytes"]) for row in schedule_reports
        ),
        "max_prefix_state_bytes": max(
            int(row["max_prefix_state_bytes"]) for row in schedule_reports
        ),
        "max_greedy_state_bytes": max(
            int(row["max_greedy_state_bytes"]) for row in schedule_reports
        ),
        "schedules": schedule_reports,
    }


def _validation_gate(prefix, greedy, prior, zero, *, replay_passed, resource_passed):
    prior_reduction = float(prior["corpus_cer"]) - float(prefix["corpus_cer"])
    zero_reduction = float(zero["corpus_cer"]) - float(prefix["corpus_cer"])
    exact_gain = float(prefix["exact_sequence_accuracy"]) - max(
        float(prior["exact_sequence_accuracy"]),
        float(zero["exact_sequence_accuracy"]),
    )
    passed = bool(
        float(prefix["corpus_cer"]) <= MAX_PREFIX_CER
        and float(prefix["exact_sequence_accuracy"]) >= MIN_EXACT_ACCURACY
        and float(prefix["repeated_pair_reconstruction_rate"]) >= MIN_REPEAT_RATE
        and prior_reduction >= MIN_CER_REDUCTION
        and zero_reduction >= MIN_CER_REDUCTION
        and exact_gain >= MIN_EXACT_GAIN
        and float(prefix["corpus_cer"]) <= float(greedy["corpus_cer"])
        and replay_passed
        and resource_passed
    )
    return {
        "passed": passed,
        "prefix_cer": prefix["corpus_cer"],
        "prefix_exact_accuracy": prefix["exact_sequence_accuracy"],
        "repeat_reconstruction_rate": prefix["repeated_pair_reconstruction_rate"],
        "cer_reduction_vs_prior": prior_reduction,
        "cer_reduction_vs_zero_signal": zero_reduction,
        "exact_gain_over_stronger_control": exact_gain,
        "prefix_minus_greedy_cer": float(prefix["corpus_cer"])
        - float(greedy["corpus_cer"]),
        "replay_passed": replay_passed,
        "pretest_resource_gate_passed": resource_passed,
        "thresholds": _thresholds(),
    }


def _test_gate(prefix, greedy, prior, zero, bootstrap_prior, bootstrap_zero):
    prior_reduction = float(prior["corpus_cer"]) - float(prefix["corpus_cer"])
    zero_reduction = float(zero["corpus_cer"]) - float(prefix["corpus_cer"])
    exact_gain = float(prefix["exact_sequence_accuracy"]) - max(
        float(prior["exact_sequence_accuracy"]),
        float(zero["exact_sequence_accuracy"]),
    )
    passed = bool(
        float(prefix["corpus_cer"]) <= MAX_PREFIX_CER
        and float(prefix["exact_sequence_accuracy"]) >= MIN_EXACT_ACCURACY
        and float(prefix["repeated_pair_reconstruction_rate"]) >= MIN_REPEAT_RATE
        and prior_reduction >= MIN_CER_REDUCTION
        and zero_reduction >= MIN_CER_REDUCTION
        and exact_gain >= MIN_EXACT_GAIN
        and float(prefix["corpus_cer"]) <= float(greedy["corpus_cer"])
        and float(bootstrap_prior["confidence_interval_95"][0]) > 0
        and float(bootstrap_zero["confidence_interval_95"][0]) > 0
    )
    return {
        "opened": True,
        "passed": passed,
        "prefix_cer": prefix["corpus_cer"],
        "prefix_exact_accuracy": prefix["exact_sequence_accuracy"],
        "repeat_reconstruction_rate": prefix["repeated_pair_reconstruction_rate"],
        "cer_reduction_vs_prior": prior_reduction,
        "cer_reduction_vs_zero_signal": zero_reduction,
        "exact_gain_over_stronger_control": exact_gain,
        "prefix_minus_greedy_cer": float(prefix["corpus_cer"])
        - float(greedy["corpus_cer"]),
        "bootstrap_prior_lower_bound": bootstrap_prior["confidence_interval_95"][0],
        "bootstrap_zero_lower_bound": bootstrap_zero["confidence_interval_95"][0],
        "thresholds": _thresholds(),
        "reason": (
            "all_frozen_test_thresholds_passed"
            if passed
            else "one_or_more_frozen_test_thresholds_failed"
        ),
    }


def _thresholds() -> dict[str, object]:
    return {
        "maximum_prefix_cer": MAX_PREFIX_CER,
        "minimum_exact_accuracy": MIN_EXACT_ACCURACY,
        "minimum_repeat_reconstruction_rate": MIN_REPEAT_RATE,
        "minimum_cer_reduction_per_signal_free_control": MIN_CER_REDUCTION,
        "minimum_exact_gain_over_stronger_control": MIN_EXACT_GAIN,
        "prefix_cer_not_above_greedy": True,
        "bootstrap_lower_bounds_strictly_positive": True,
    }


def _partition_targets(partition) -> list[tuple[int, ...]]:
    return [
        tuple(
            int(value)
            for value in partition.target_token_ids[index, : int(length)].tolist()
        )
        for index, length in enumerate(partition.target_lengths.tolist())
    ]


def _partition_array_bytes(partition) -> int:
    values = (
        partition.target_token_ids,
        partition.target_lengths,
        partition.item_ids,
        partition.signals,
        partition.input_lengths,
        partition.sample_labels,
        partition.frame_labels,
        partition.frame_lengths,
        partition.motif_start_samples,
        partition.motif_end_samples,
    )
    return sum(int(value.nbytes) for value in values if value is not None)


def _log_softmax(logits):
    np = _require_numpy()
    shifted = logits - logits.max(axis=1, keepdims=True)
    return shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))


def _decoder_config_sha256() -> str:
    return _sha256_json(
        {
            "blank_id": BLANK_ID,
            "beam_width": BEAM_WIDTH,
            "max_prefix_length": MAX_PREFIX_LENGTH,
            "language_model": None,
            "lexicon": None,
            "insertion_bonus": 0.0,
            "score_threshold": None,
            "tie_break": "score_desc_then_token_tuple_lexicographic",
            "frame_update": "one_at_a_time",
        }
    )


def _partition_open_count(events: list[dict[str, object]], split: str) -> int:
    return sum(
        event.get("split") == split and str(event.get("action", "")).startswith("partition_opened_")
        for event in events
    )


def _access_sequence_passed(events, *, test_opened: bool) -> bool:
    if _partition_open_count(events, "train") != 1:
        return False
    if _partition_open_count(events, "validation") != 1:
        return False
    if _partition_open_count(events, "test") != (1 if test_opened else 0):
        return False
    stages = {str(event["stage"]): int(event["event_index"]) for event in events}
    required = (
        "manifest_validation",
        "checkpoint_validation",
        "train_targets_open",
        "prior_fit",
        "validation_open",
        "decoder_config_freeze",
    )
    if any(stage not in stages for stage in required):
        return False
    if [stages[stage] for stage in required] != sorted(stages[stage] for stage in required):
        return False
    train_event = next(event for event in events if event["stage"] == "train_targets_open")
    if train_event.get("opened_members") != [
        "metadata",
        "target_token_ids",
        "target_lengths",
        "item_ids",
    ]:
        return False
    if test_opened:
        if "frozen_test_open" not in stages or "frozen_test_evaluation" not in stages:
            return False
        if not (
            stages["decoder_config_freeze"]
            < stages["frozen_test_open"]
            < stages["frozen_test_evaluation"]
        ):
            return False
    return True


def _access_event(events, *, stage, split, action, **values):
    return {
        "event_index": len(events),
        "stage": stage,
        "split": split,
        "action": action,
        **{key: value for key, value in values.items() if value is not None},
    }


def _finalize_report_texts(
    report,
    *,
    markdown_requested: bool,
    max_artifact_bytes: int,
    base_gate_passed: bool,
):
    for _ in range(20):
        markdown = _report_markdown(report) if markdown_requested else None
        markdown_bytes = len(markdown.encode("utf-8")) if markdown else 0
        report["artifacts"]["markdown_bytes"] = markdown_bytes
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_bytes = len(json_text.encode("utf-8"))
        total = json_bytes + markdown_bytes
        artifact_passed = total <= max_artifact_bytes
        changed = (
            report["artifacts"]["json_bytes"] != json_bytes
            or report["artifacts"]["total_artifact_bytes"] != total
            or report["artifacts"]["artifact_gate_passed"] != artifact_passed
            or report["gate_passed"] != bool(base_gate_passed and artifact_passed)
        )
        report["artifacts"]["json_bytes"] = json_bytes
        report["artifacts"]["total_artifact_bytes"] = total
        report["artifacts"]["artifact_gate_passed"] = artifact_passed
        report["gate_passed"] = bool(base_gate_passed and artifact_passed)
        report["decision"] = _gate_decision(
            gate_passed=bool(report["gate_passed"]),
            mechanical_gate_passed=bool(report["mechanical_gate_passed"]),
            registered_protocol_match=bool(report["registered_protocol_match"]),
            registered_checkpoint_match=bool(report["registered_checkpoint_match"]),
            artifact_gate_passed=artifact_passed,
        )
        if not changed:
            final_markdown = _report_markdown(report) if markdown_requested else None
            final_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
            if len(final_json.encode("utf-8")) == report["artifacts"]["json_bytes"]:
                return final_json, final_markdown
    raise RuntimeError("Loop 23 report byte accounting did not converge")


def _report_markdown(report) -> str:
    validation = report["validation"]
    test = report["frozen_test"]
    lines = [
        "# Streaming CTC Prefix Decoder Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Decision: `{report['decision']}`",
        f"- Registered protocol/checkpoint: `{str(report['registered_protocol_match']).lower()}` / `{str(report['registered_checkpoint_match']).lower()}`",
        f"- Validation prefix CER: {validation['prefix_metrics']['corpus_cer']:.6f}",
        f"- Validation exact accuracy: {validation['prefix_metrics']['exact_sequence_accuracy']:.6f}",
        f"- Validation schedules: {report['streaming_replay']['schedules_passed']}/5",
        f"- Frozen test opened: `{str(test['opened']).lower()}`",
    ]
    if test["canonical"] is not None:
        lines.extend(
            [
                f"- Frozen test prefix CER: {test['canonical']['prefix_metrics']['corpus_cer']:.6f}",
                f"- Frozen test exact accuracy: {test['canonical']['prefix_metrics']['exact_sequence_accuracy']:.6f}",
            ]
        )
    lines.extend(
        [
            f"- Runtime: {report['resources']['runtime_before_report_write_sec']:.6f} sec",
            f"- Peak RSS: {report['resources']['peak_rss_bytes']} bytes",
            "",
            "## Access Audit",
            "",
            f"- Train / validation / test opens: {report['access_audit']['train_semantic_open_count']} / {report['access_audit']['validation_semantic_open_count']} / {report['access_audit']['test_semantic_open_count']}",
            "",
            "## Claim Boundaries",
            "",
        ]
    )
    lines.extend(f"- {value}" for value in report["claim_boundaries"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{value}`" for value in report["warnings"])
    return "\n".join(lines) + "\n"


def _gate_decision(
    *,
    gate_passed,
    mechanical_gate_passed,
    registered_protocol_match,
    registered_checkpoint_match,
    artifact_gate_passed,
):
    if gate_passed:
        return "proceed_to_loop24_local_precision_runtime_gate"
    if (
        mechanical_gate_passed
        and (not registered_protocol_match or not registered_checkpoint_match)
        and artifact_gate_passed is not False
    ):
        return "nonregistered_fixture_or_checkpoint_mechanics_only"
    return "park_streaming_ctc_decoder_branch"


def _prepare_outputs(paths) -> None:
    planned = [path for path in paths if path is not None]
    normalized = [path.expanduser().resolve(strict=False) for path in planned]
    if len(normalized) != len(set(normalized)):
        raise ValueError("Loop 23 output paths must be distinct")
    for path in planned:
        if path.exists():
            raise FileExistsError(f"Refusing to replace Loop 23 gate artifact: {path}")


def _validate_caps(caps: StreamingCTCGateCaps) -> None:
    for name, value in asdict(caps).items():
        normalized = float(value)
        if not math.isfinite(normalized) or normalized <= 0:
            raise ValueError(f"{name} must be finite and positive")


def _require_single_thread_environment() -> dict[str, str]:
    values = {name: os.environ.get(name) for name in THREAD_ENV_VARS}
    invalid = [name for name, value in values.items() if value != "1"]
    if invalid:
        assignments = " ".join(f"{name}=1" for name in THREAD_ENV_VARS)
        raise RuntimeError(
            "Loop 23 requires one-thread numeric environment variables before "
            f"NumPy/Torch import; set `{assignments}`. Invalid: {', '.join(invalid)}"
        )
    return {name: str(value) for name, value in values.items()}


def _peak_rss_bytes() -> int | None:
    try:
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (AttributeError, ImportError, OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


def _array_sha256(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Loop 23 gate requires NumPy.") from exc
    return np
