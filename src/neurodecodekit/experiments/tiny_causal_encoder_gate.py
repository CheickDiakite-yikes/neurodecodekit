"""Preregistered synthetic gate for one tiny learned causal encoder."""

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

from neurodecodekit.experiments.causal_replay_gate import (
    REGISTERED_SCHEDULES,
    registered_chunk_sizes,
)
from neurodecodekit.models.tiny_causal_encoder import (
    batched_partition_outputs,
    canonical_partition_outputs,
    classification_metrics,
    load_tiny_causal_encoder_checkpoint,
    registered_tiny_causal_encoder_config,
    save_tiny_causal_encoder_checkpoint,
    train_only_prior_class,
    train_tiny_causal_encoder,
)
from neurodecodekit.training.causal_motifs import (
    PARTITION_NAMES,
    load_causal_motif_manifest,
    load_causal_motif_partition,
    registered_causal_motif_protocol,
    resolve_manifest_partition_path,
)


TINY_CAUSAL_GATE_SCHEMA_NAME = "b2q-tiny-causal-encoder-gate"
TINY_CAUSAL_GATE_SCHEMA_VERSION = 0
PROOF_POSTURE = "synthetic_learned_causal_motif_encoder_only_no_text_decoder"
BOOTSTRAP_SEED = 2222
BOOTSTRAP_RESAMPLES = 2000
COMPATIBILITY_ATOL = 1e-6
VALIDATION_MIN_BALANCED_ACCURACY = 0.70
VALIDATION_MIN_BALANCED_GAIN = 0.35
VALIDATION_MIN_ACCURACY_GAIN = 0.20
TEST_MIN_BALANCED_GAIN = 0.35
TEST_MIN_ACCURACY_GAIN = 0.20
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)
OFFICIAL_V2_COMMIT = "3bf5a4099ca0d23bbe994b2287905760236e56e0"
OFFICIAL_V2_PAPER = (
    "https://facebookresearch.github.io/brain2qwerty/assets/brain2qwerty_v2.pdf"
)
OFFICIAL_V2_CONFIG = (
    "https://github.com/facebookresearch/brain2qwerty/blob/"
    f"{OFFICIAL_V2_COMMIT}/brain2qwerty_v2/config/model_config.py"
)
TCN_REFERENCE = "https://openreview.net/forum?id=rk8wKk-R-"
PYTORCH_REPRODUCIBILITY = (
    "https://docs.pytorch.org/docs/2.13/notes/randomness.html"
)


@dataclass(frozen=True)
class TinyCausalGateCaps:
    max_fixture_bytes: int = 1 * 1024 * 1024
    max_items: int = 80
    max_samples_per_item: int = 128
    max_total_frames: int = 2048
    max_trainable_parameters: int = 2048
    max_parameter_bytes: int = 16 * 1024
    max_checkpoint_bytes: int = 64 * 1024
    max_state_bytes: int = 1 * 1024
    max_working_bytes: int = 16 * 1024 * 1024
    max_runtime_sec: float = 30.0
    max_peak_rss_bytes: int = 768 * 1024 * 1024
    max_artifact_bytes: int = 1 * 1024 * 1024
    max_total_pushes: int = 50_000

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def registered_tiny_causal_gate_caps() -> TinyCausalGateCaps:
    return TinyCausalGateCaps()


def run_tiny_causal_encoder_gate(
    *,
    fixture_manifest_path: str | Path,
    checkpoint_out_path: str | Path,
    out_json_path: str | Path,
    out_markdown_path: str | Path | None = None,
    require_registered_protocol: bool = True,
    caps: TinyCausalGateCaps | None = None,
) -> dict[str, Any]:
    """Train/select once, freeze an NPZ checkpoint, and open synthetic test once."""

    started_at = time.perf_counter()
    selected_caps = caps or registered_tiny_causal_gate_caps()
    _validate_caps(selected_caps)
    thread_environment = _require_single_thread_environment()
    manifest_path = Path(fixture_manifest_path)
    checkpoint_path = Path(checkpoint_out_path)
    json_path = Path(out_json_path)
    markdown_path = Path(out_markdown_path) if out_markdown_path else None
    _prepare_outputs([checkpoint_path, json_path, markdown_path])
    access_events: list[dict[str, object]] = []
    access_events.append(
        _access_event(
            access_events,
            stage="manifest_validation",
            split=None,
            action="compact_manifest_opened_no_partition_array",
        )
    )
    manifest = load_causal_motif_manifest(
        manifest_path,
        require_registered_protocol=require_registered_protocol,
    )
    registered_protocol = registered_causal_motif_protocol()
    registered_protocol_match = manifest["protocol"] == registered_protocol.to_dict()
    fixture_bytes = int(manifest["artifacts"]["total_fixture_bytes"])
    if fixture_bytes > selected_caps.max_fixture_bytes:
        raise ValueError("causal motif fixture exceeds the registered byte cap")
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
    if total_items > selected_caps.max_items:
        raise ValueError("causal motif fixture exceeds the registered item cap")
    if total_frames > selected_caps.max_total_frames:
        raise ValueError("causal motif fixture exceeds the registered frame cap")
    if max_samples > selected_caps.max_samples_per_item:
        raise ValueError("causal motif fixture exceeds the registered sample cap")

    train = _open_partition(
        manifest_path,
        manifest,
        "train",
        access_events=access_events,
        stage="train_open",
    )
    validation = _open_partition(
        manifest_path,
        manifest,
        "validation",
        access_events=access_events,
        stage="validation_open",
    )
    if set(train.item_ids.tolist()).intersection(validation.item_ids.tolist()):
        raise ValueError("train and validation fixture item IDs overlap")

    config = registered_tiny_causal_encoder_config()
    training, fit_report = train_tiny_causal_encoder(train, validation, config=config)
    access_events.append(
        _access_event(
            access_events,
            stage="train_fit",
            split="train",
            action="train_only_normalization_weights_and_parameter_updates_completed",
        )
    )
    access_events.append(
        _access_event(
            access_events,
            stage="validation_selection",
            split="validation",
            action="best_epoch_selected_without_test_access",
        )
    )
    parameter_gate = (
        training.parameter_count <= selected_caps.max_trainable_parameters
        and training.parameter_bytes_float32 <= selected_caps.max_parameter_bytes
    )
    train_frames = _valid_frame_labels(train)
    validation_frames = _valid_frame_labels(validation)
    prior_class = train_only_prior_class(
        train_frames["labels"], n_classes=registered_protocol.n_classes
    )
    validation_prior_predictions = _constant_predictions(
        len(validation_frames["labels"]), prior_class
    )
    validation_prior = classification_metrics(
        validation_frames["labels"],
        validation_prior_predictions,
        n_classes=registered_protocol.n_classes,
    )
    validation_gate = _validation_gate(
        training.validation_metrics, validation_prior
    )

    checkpoint_summary: dict[str, Any] | None = None
    producer = None
    checkpoint_metadata: dict[str, Any] | None = None
    replay_report: dict[str, Any] | None = None
    validation_canonical: dict[str, Any] | None = None
    validation_zero: dict[str, Any] | None = None
    batch_compatibility: dict[str, Any] | None = None
    validation_canonical_runtime_sec: float | None = None
    validation_canonical_rtf: float | None = None
    pretest_gate = False
    if validation_gate["passed"] and parameter_gate:
        checkpoint_summary = save_tiny_causal_encoder_checkpoint(
            checkpoint_path,
            training=training,
            metadata={
                "proof_posture": PROOF_POSTURE,
                "fixture_manifest_path": str(manifest_path),
                "fixture_manifest_sha256": _file_sha256(manifest_path),
                "fixture_protocol_sha256": manifest["protocol_sha256"],
                "train_partition_sha256": manifest["partitions"]["train"]["sha256"],
                "validation_partition_sha256": manifest["partitions"]["validation"][
                    "sha256"
                ],
                "test_partition_declared_sha256": manifest["partitions"]["test"][
                    "sha256"
                ],
                "selection_frozen_before_test": True,
                "selection_metric": "validation_balanced_accuracy_then_loss_then_epoch",
                "validation_metrics": training.validation_metrics,
                "validation_prior_metrics": validation_prior,
                "geometry": {
                    "n_channels": registered_protocol.n_channels,
                    "kernel_size": registered_protocol.kernel_size,
                    "stride": registered_protocol.stride,
                    "n_classes": registered_protocol.n_classes,
                    "sampling_rate_hz": registered_protocol.sampling_rate_hz,
                },
                "claim_boundary": "synthetic_motif_probe_not_text_decoding",
            },
        )
        if int(checkpoint_summary["bytes"]) > selected_caps.max_checkpoint_bytes:
            raise ValueError("tiny causal checkpoint exceeds the registered byte cap")
        producer, checkpoint_metadata = load_tiny_causal_encoder_checkpoint(
            checkpoint_path
        )
        access_events.append(
            _access_event(
                access_events,
                stage="checkpoint_freeze",
                split=None,
                action="validation_selected_npz_checkpoint_saved_hashed_and_reloaded",
                checkpoint_sha256=checkpoint_summary["sha256"],
            )
        )
        validation_canonical_started = time.perf_counter()
        validation_canonical = canonical_partition_outputs(producer, validation)
        validation_canonical_runtime_sec = (
            time.perf_counter() - validation_canonical_started
        )
        validation_duration_sec = float(
            validation.input_lengths.sum() / producer.source_sampling_rate_hz
        )
        validation_canonical_rtf = (
            validation_canonical_runtime_sec / validation_duration_sec
            if validation_duration_sec
            else None
        )
        validation_batch = batched_partition_outputs(producer, validation)
        batch_compatibility = _batch_compatibility(
            validation_canonical, validation_batch
        )
        validation_canonical_metrics = classification_metrics(
            validation_canonical["labels"],
            validation_canonical["predictions"],
            n_classes=registered_protocol.n_classes,
        )
        validation_zero = _zero_signal_metrics(
            producer,
            labels=validation_canonical["labels"],
            n_classes=registered_protocol.n_classes,
        )
        replay_report = _run_stream_replay(
            producer,
            validation,
            validation_canonical,
            max_total_pushes=selected_caps.max_total_pushes,
            max_chunk_samples=selected_caps.max_samples_per_item,
        )
        validation_metric_identity = (
            validation_canonical_metrics == training.validation_metrics
        )
        pretest_gate = bool(
            validation_metric_identity
            and batch_compatibility["passed"]
            and replay_report["passed"]
            and replay_report["max_mutable_state_bytes"]
            <= selected_caps.max_state_bytes
        )
    else:
        validation_canonical_metrics = None

    test = None
    test_canonical: dict[str, Any] | None = None
    test_metrics: dict[str, Any] | None = None
    test_prior: dict[str, Any] | None = None
    test_zero: dict[str, Any] | None = None
    bootstrap: dict[str, Any] | None = None
    test_canonical_runtime_sec: float | None = None
    test_gate: dict[str, Any] = {
        "opened": False,
        "passed": False,
        "reason": "pretest_gate_failed_test_remained_unopened",
    }
    if pretest_gate and producer is not None and checkpoint_summary is not None:
        test = _open_partition(
            manifest_path,
            manifest,
            "test",
            access_events=access_events,
            stage="frozen_test_open",
            checkpoint_sha256=checkpoint_summary["sha256"],
        )
        if set(train.item_ids.tolist()).intersection(test.item_ids.tolist()):
            raise ValueError("train and test fixture item IDs overlap")
        if set(validation.item_ids.tolist()).intersection(test.item_ids.tolist()):
            raise ValueError("validation and test fixture item IDs overlap")
        test_canonical_started = time.perf_counter()
        test_canonical = canonical_partition_outputs(producer, test)
        test_canonical_runtime_sec = time.perf_counter() - test_canonical_started
        test_metrics = classification_metrics(
            test_canonical["labels"],
            test_canonical["predictions"],
            n_classes=registered_protocol.n_classes,
        )
        test_prior_predictions = _constant_predictions(
            len(test_canonical["labels"]), prior_class
        )
        test_prior = classification_metrics(
            test_canonical["labels"],
            test_prior_predictions,
            n_classes=registered_protocol.n_classes,
        )
        test_zero = _zero_signal_metrics(
            producer,
            labels=test_canonical["labels"],
            n_classes=registered_protocol.n_classes,
        )
        bootstrap = _paired_item_bootstrap(
            test_canonical["labels"],
            test_canonical["predictions"],
            test_prior_predictions,
            test_canonical["item_indices"],
            resamples=BOOTSTRAP_RESAMPLES,
            seed=BOOTSTRAP_SEED,
        )
        test_gate = _test_gate(test_metrics, test_prior, test_zero, bootstrap)
        access_events.append(
            _access_event(
                access_events,
                stage="frozen_test_evaluation",
                split="test",
                action="single_canonical_model_and_comparator_evaluation_completed",
                checkpoint_sha256=checkpoint_summary["sha256"],
            )
        )

    runtime_before_report_sec = time.perf_counter() - started_at
    peak_rss_bytes = _peak_rss_bytes()
    loaded_partition_bytes = _partition_array_bytes(train) + _partition_array_bytes(
        validation
    )
    if test is not None:
        loaded_partition_bytes += _partition_array_bytes(test)
    working_core_bytes = int(
        loaded_partition_bytes
        + fit_report["train_frame_array_bytes"]
        + fit_report["validation_frame_array_bytes"]
        + training.parameter_bytes_float32
        + training.normalization_mean.nbytes
        + training.normalization_std.nbytes
        + training.class_weights.nbytes
    )
    resource_gate = bool(
        runtime_before_report_sec <= selected_caps.max_runtime_sec
        and peak_rss_bytes is not None
        and peak_rss_bytes <= selected_caps.max_peak_rss_bytes
        and working_core_bytes <= selected_caps.max_working_bytes
        and parameter_gate
    )
    test_semantic_open_count = sum(
        event.get("split") == "test" and event.get("action") == "partition_arrays_opened"
        for event in access_events
    )
    access_gate = _access_sequence_passed(
        access_events,
        test_opened=test is not None,
    )
    mechanical_gate_passed = bool(
        pretest_gate
        and test_gate["passed"]
        and resource_gate
        and access_gate
        and producer is not None
        and producer.producer_right_context_samples == 0
    )
    base_gate_passed = bool(mechanical_gate_passed and registered_protocol_match)
    report: dict[str, Any] = {
        "schema": {
            "name": TINY_CAUSAL_GATE_SCHEMA_NAME,
            "version": TINY_CAUSAL_GATE_SCHEMA_VERSION,
        },
        "proof_posture": PROOF_POSTURE,
        "gate_passed": base_gate_passed,
        "mechanical_gate_passed": mechanical_gate_passed,
        "decision": (
            _gate_decision(
                gate_passed=base_gate_passed,
                mechanical_gate_passed=mechanical_gate_passed,
                registered_protocol_match=registered_protocol_match,
                artifact_gate_passed=None,
            )
        ),
        "registered_protocol_match": registered_protocol_match,
        "fixture": {
            "manifest_path": str(manifest_path),
            "manifest_sha256": _file_sha256(manifest_path),
            "protocol_sha256": manifest["protocol_sha256"],
            "total_bytes": fixture_bytes,
            "total_items": total_items,
            "total_frames": total_frames,
            "max_samples_per_item": max_samples,
            "partitions": manifest["partitions"],
            "real_data_reads": 0,
            "raw_data_reads": 0,
            "text_target_reads": 0,
            "network_fetches": 0,
        },
        "model": {
            "name": "tiny_shared_window_mlp_encoder_probe_v0",
            "causal": True,
            "producer_right_context_samples": 0,
            "kernel_size_samples": registered_protocol.kernel_size,
            "stride_samples": registered_protocol.stride,
            "sampling_rate_hz": registered_protocol.sampling_rate_hz,
            "first_frame_availability_sec": (
                registered_protocol.kernel_size / registered_protocol.sampling_rate_hz
            ),
            "frame_step_sec": (
                registered_protocol.stride / registered_protocol.sampling_rate_hz
            ),
            "hidden_dim": config.hidden_dim,
            "embedding_dim": config.embedding_dim,
            "motif_classes_including_background": registered_protocol.n_classes,
            "trainable_parameters": training.parameter_count,
            "encoder_parameters": training.encoder_parameter_count,
            "probe_parameters": training.probe_parameter_count,
            "parameter_bytes_float32": training.parameter_bytes_float32,
            "motif_probe_is_text_decoder": False,
            "checkpoint": (
                {key: checkpoint_summary[key] for key in checkpoint_summary if key != "metadata"}
                if checkpoint_summary
                else None
            ),
        },
        "selection": {
            "config": config.to_dict(),
            "config_sha256": config.config_sha256,
            "fit_report": fit_report,
            "best_epoch": training.best_epoch,
            "epochs_ran": training.epochs_ran,
            "stopped_early": training.stopped_early,
            "history": training.training_history,
            "train_metrics": training.train_metrics,
            "validation_metrics_batch": training.validation_metrics,
            "validation_metrics_canonical": validation_canonical_metrics,
            "validation_prior_class": prior_class,
            "validation_prior": validation_prior,
            "validation_zero_signal": validation_zero,
            "validation_gate": validation_gate,
            "checkpoint_frozen_before_test": checkpoint_summary is not None,
            "test_metrics_used_for_selection": False,
            "architecture_candidates": 1,
            "initialization_restarts": 0,
            "model_seed": config.model_seed,
        },
        "streaming_replay": replay_report,
        "batch_compatibility": batch_compatibility,
        "frozen_test": {
            "opened": test is not None,
            "semantic_open_count": test_semantic_open_count,
            "metrics": test_metrics,
            "prior": test_prior,
            "zero_signal": test_zero,
            "paired_item_bootstrap_vs_prior": bootstrap,
            "gate": test_gate,
            "model_fit_after_open": False,
            "checkpoint_changed_after_open": False,
        },
        "access_audit": {
            "passed": access_gate,
            "events": access_events,
            "train_semantic_open_count": _partition_open_count(access_events, "train"),
            "validation_semantic_open_count": _partition_open_count(
                access_events, "validation"
            ),
            "test_semantic_open_count": test_semantic_open_count,
        },
        "resources": {
            "runtime_before_report_write_sec": round(runtime_before_report_sec, 6),
            "training_runtime_sec": training.runtime_sec,
            "validation_canonical_inference_runtime_sec": (
                round(validation_canonical_runtime_sec, 6)
                if validation_canonical_runtime_sec is not None
                else None
            ),
            "validation_canonical_inference_real_time_factor": (
                validation_canonical_rtf
            ),
            "test_canonical_inference_runtime_sec": (
                round(test_canonical_runtime_sec, 6)
                if test_canonical_runtime_sec is not None
                else None
            ),
            "peak_rss_bytes": peak_rss_bytes,
            "working_core_bytes_before_framework_temporaries": working_core_bytes,
            "loaded_partition_array_bytes": loaded_partition_bytes,
            "mutable_array_state_bytes": (
                replay_report["max_mutable_state_bytes"] if replay_report else None
            ),
            "mutable_state_accounting": "raw_numpy_overlap_buffer_payload_only",
            "fixed_model_and_normalization_bytes": (
                producer.fixed_parameter_bytes if producer is not None else None
            ),
            "thread_environment": thread_environment,
            "torch_intraop_threads": config.num_threads,
            "torch_interop_threads_requested": 1,
            "torch_version": training.torch_version,
            "caps": selected_caps.to_dict(),
            "resource_gate_passed": resource_gate,
        },
        "execution_counts": {
            "fixture_generation_runs": 0,
            "training_runs": 1,
            "architecture_candidates": 1,
            "initialization_restarts": 0,
            "checkpoint_saves": 1 if checkpoint_summary is not None else 0,
            "checkpoint_loads": 1 if checkpoint_summary is not None else 0,
            "test_partition_opens": test_semantic_open_count,
            "real_data_reads": 0,
            "raw_data_reads": 0,
            "text_target_reads": 0,
            "network_fetches": 0,
        },
        "research_sources": {
            "official_v2_paper": OFFICIAL_V2_PAPER,
            "official_v2_config": OFFICIAL_V2_CONFIG,
            "causal_temporal_convolution": TCN_REFERENCE,
            "pytorch_reproducibility": PYTORCH_REPRODUCIBILITY,
        },
        "claim_boundaries": [
            "The learned task uses synthetic generated motifs, not neural recordings.",
            "The motif probe is not CTC, a character decoder, or a language model.",
            "Producer causality does not establish text-emission causality.",
            "The 160 ms first frame is not user-perceived text latency.",
            "No real MEG/EEG cache or observed holdout was opened.",
            "No at-home sensor, unseen-person, clinical, or arbitrary-thought claim follows.",
        ],
        "warnings": [
            "synthetic_supervised_motif_task_only",
            "tiny_model_mechanism_gate_not_brain_decoding_quality",
            "probe_metrics_are_frame_classification_not_cer_or_wer",
            "checkpoint_npz_contains_plain_numeric_weights_no_pickle",
            "end_to_end_latency_unmeasured",
            "real_neural_holdouts_remain_frozen",
        ],
        "artifacts": {
            "json_path": str(json_path),
            "markdown_path": str(markdown_path) if markdown_path else None,
            "checkpoint_path": str(checkpoint_path) if checkpoint_summary else None,
            "json_bytes": 0,
            "markdown_bytes": 0,
            "checkpoint_bytes": (
                int(checkpoint_summary["bytes"]) if checkpoint_summary else 0
            ),
            "total_artifact_bytes": 0,
            "artifact_gate_passed": False,
        },
    }
    json_text, markdown_text = _finalize_report_texts(
        report,
        markdown_requested=markdown_path is not None,
        max_artifact_bytes=selected_caps.max_artifact_bytes,
        base_gate_passed=base_gate_passed,
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
    access_events: list[dict[str, object]],
    stage: str,
    checkpoint_sha256: str | None = None,
):
    path = resolve_manifest_partition_path(manifest_path, manifest, split)
    loaded = load_causal_motif_partition(
        path, expected=manifest["partitions"][split]
    )
    access_events.append(
        _access_event(
            access_events,
            stage=stage,
            split=split,
            action="partition_arrays_opened",
            path=str(path),
            sha256=manifest["partitions"][split]["sha256"],
            checkpoint_sha256=checkpoint_sha256,
        )
    )
    return loaded


def _run_stream_replay(
    producer,
    partition,
    canonical: Mapping[str, Any],
    *,
    max_total_pushes: int,
    max_chunk_samples: int,
) -> dict[str, Any]:
    np = _require_numpy()
    schedule_reports = []
    remaining_pushes = int(max_total_pushes)
    canonical_hash = _array_sha256(canonical["embeddings"])
    for schedule_name in REGISTERED_SCHEDULES:
        started_at = time.perf_counter()
        embeddings = []
        starts = []
        ends = []
        availability = []
        delays = []
        push_compute_sec = 0.0
        push_count = 0
        max_state = 0
        offset = 0
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
                raise ValueError("learned replay exceeded remaining push cap")
            stream = producer.new_stream(
                max_chunk_samples=max_chunk_samples,
                max_total_samples=max_chunk_samples,
                max_total_tokens=64,
            )
            item_batches = []
            source_offset = 0
            for size in sizes:
                push_started = time.perf_counter()
                batch = stream.push(
                    partition.signals[
                        item_index, :, source_offset : source_offset + size
                    ]
                )
                push_compute_sec += time.perf_counter() - push_started
                item_batches.append(batch)
                source_offset += size
            flush = stream.flush()
            expected_tail = length - (
                (int(partition.frame_lengths[item_index]) - 1) * producer.stride
                + producer.kernel_size
            )
            if flush.unframed_tail_samples != expected_tail:
                raise RuntimeError("learned replay flush tail disagrees with frame grid")
            max_state = max(max_state, stream.max_mutable_state_bytes)
            item_embeddings = np.concatenate(
                [batch.tokens for batch in item_batches], axis=0
            )
            count = int(partition.frame_lengths[item_index])
            expected = canonical["embeddings"][offset : offset + count]
            embeddings.append(item_embeddings)
            starts.append(
                np.concatenate(
                    [batch.frame_start_samples for batch in item_batches]
                )
            )
            ends.append(
                np.concatenate([batch.frame_end_samples for batch in item_batches])
            )
            availability.append(
                np.concatenate(
                    [batch.availability_samples for batch in item_batches]
                )
            )
            delays.extend(
                np.concatenate(
                    [batch.schedule_delay_samples for batch in item_batches]
                ).tolist()
            )
            if not np.array_equal(item_embeddings, expected):
                raise RuntimeError("learned stream embedding bits changed across chunks")
            offset += count
        payload = np.concatenate(embeddings, axis=0)
        frame_starts = np.concatenate(starts)
        frame_ends = np.concatenate(ends)
        available = np.concatenate(availability)
        payload_hash = _array_sha256(payload)
        frame_grid_exact = bool(
            np.array_equal(frame_starts, canonical["frame_start_samples"])
            and np.array_equal(frame_ends, canonical["frame_end_samples"])
        )
        causal_availability = bool((available >= frame_ends).all())
        duration_sec = float(
            partition.input_lengths.sum() / producer.source_sampling_rate_hz
        )
        passed = bool(
            payload_hash == canonical_hash
            and frame_grid_exact
            and causal_availability
            and max_state <= producer.mutable_state_bound_bytes
        )
        schedule_reports.append(
            {
                "name": schedule_name,
                "passed": passed,
                "push_count": push_count,
                "emitted_frames": int(len(payload)),
                "embedding_payload_sha256": payload_hash,
                "frame_grid_exact": frame_grid_exact,
                "causal_availability_passed": causal_availability,
                "right_context_samples": 0,
                "max_mutable_state_bytes": max_state,
                "max_schedule_delay_sec": (
                    max(delays) / producer.source_sampling_rate_hz if delays else 0.0
                ),
                "producer_compute_real_time_factor": (
                    push_compute_sec / duration_sec if duration_sec else None
                ),
                "runtime_sec": round(time.perf_counter() - started_at, 6),
            }
        )
        remaining_pushes -= push_count
    hashes = {
        str(report["embedding_payload_sha256"]) for report in schedule_reports
    }
    return {
        "passed": all(bool(report["passed"]) for report in schedule_reports)
        and len(hashes) == 1,
        "registered_schedules": list(REGISTERED_SCHEDULES),
        "schedules_passed": sum(bool(report["passed"]) for report in schedule_reports),
        "schedule_bits_invariant": len(hashes) == 1,
        "canonical_embedding_payload_sha256": canonical_hash,
        "max_mutable_state_bytes": max(
            int(report["max_mutable_state_bytes"]) for report in schedule_reports
        ),
        "total_pushes": max_total_pushes - remaining_pushes,
        "schedules": schedule_reports,
    }


def _batch_compatibility(canonical: Mapping[str, Any], batched: Mapping[str, Any]):
    np = _require_numpy()
    embedding_error = float(
        np.abs(canonical["embeddings"] - batched["embeddings"]).max()
    )
    logit_error = float(np.abs(canonical["logits"] - batched["logits"]).max())
    predictions_equal = bool(
        np.array_equal(canonical["predictions"], batched["predictions"])
    )
    return {
        "passed": max(embedding_error, logit_error) <= COMPATIBILITY_ATOL
        and predictions_equal,
        "absolute_tolerance": COMPATIBILITY_ATOL,
        "max_embedding_absolute_error": embedding_error,
        "max_logit_absolute_error": logit_error,
        "predictions_equal": predictions_equal,
    }


def _zero_signal_metrics(producer, *, labels, n_classes: int) -> dict[str, Any]:
    np = _require_numpy()
    raw_zero_after_normalization = np.repeat(
        producer.normalization_mean[:, None], producer.kernel_size, axis=1
    ).reshape(-1)
    embedding = producer.project_frame(raw_zero_after_normalization)[0]
    predicted_class = int(producer.probe_embedding(embedding)[0].argmax())
    predictions = np.full(len(labels), predicted_class, dtype="int64")
    metrics = classification_metrics(labels, predictions, n_classes=n_classes)
    return {"predicted_class": predicted_class, **metrics}


def _validation_gate(learned: Mapping[str, Any], prior: Mapping[str, Any]):
    balanced_gain = float(learned["balanced_accuracy"]) - float(
        prior["balanced_accuracy"]
    )
    accuracy_gain = float(learned["accuracy"]) - float(prior["accuracy"])
    return {
        "passed": bool(
            float(learned["balanced_accuracy"])
            >= VALIDATION_MIN_BALANCED_ACCURACY
            and balanced_gain >= VALIDATION_MIN_BALANCED_GAIN
            and accuracy_gain >= VALIDATION_MIN_ACCURACY_GAIN
        ),
        "balanced_accuracy": float(learned["balanced_accuracy"]),
        "prior_balanced_accuracy": float(prior["balanced_accuracy"]),
        "balanced_accuracy_gain": balanced_gain,
        "accuracy_gain": accuracy_gain,
        "thresholds": {
            "minimum_balanced_accuracy": VALIDATION_MIN_BALANCED_ACCURACY,
            "minimum_balanced_gain": VALIDATION_MIN_BALANCED_GAIN,
            "minimum_accuracy_gain": VALIDATION_MIN_ACCURACY_GAIN,
        },
    }


def _test_gate(learned, prior, zero_signal, bootstrap):
    control_balanced = max(
        float(prior["balanced_accuracy"]),
        float(zero_signal["balanced_accuracy"]),
    )
    control_accuracy = max(float(prior["accuracy"]), float(zero_signal["accuracy"]))
    balanced_gain = float(learned["balanced_accuracy"]) - control_balanced
    accuracy_gain = float(learned["accuracy"]) - control_accuracy
    passed = bool(
        balanced_gain >= TEST_MIN_BALANCED_GAIN
        and accuracy_gain >= TEST_MIN_ACCURACY_GAIN
        and float(bootstrap["confidence_interval_95"][0]) > 0
    )
    return {
        "opened": True,
        "passed": passed,
        "balanced_accuracy_gain_over_stronger_control": balanced_gain,
        "accuracy_gain_over_stronger_control": accuracy_gain,
        "paired_bootstrap_lower_bound": bootstrap["confidence_interval_95"][0],
        "thresholds": {
            "minimum_balanced_gain": TEST_MIN_BALANCED_GAIN,
            "minimum_accuracy_gain": TEST_MIN_ACCURACY_GAIN,
            "paired_bootstrap_lower_bound_strictly_positive": True,
        },
        "reason": (
            "all_frozen_test_thresholds_passed"
            if passed
            else "one_or_more_frozen_test_thresholds_failed"
        ),
    }


def _paired_item_bootstrap(
    targets,
    learned_predictions,
    prior_predictions,
    item_indices,
    *,
    resamples: int,
    seed: int,
) -> dict[str, Any]:
    np = _require_numpy()
    y_true = np.asarray(targets, dtype="int64")
    learned = np.asarray(learned_predictions, dtype="int64")
    prior = np.asarray(prior_predictions, dtype="int64")
    items = np.asarray(item_indices, dtype="int64")
    unique_items = np.unique(items)
    gains = []
    for item in unique_items.tolist():
        mask = items == item
        gains.append(
            float((learned[mask] == y_true[mask]).mean())
            - float((prior[mask] == y_true[mask]).mean())
        )
    gains_array = np.asarray(gains, dtype="float64")
    rng = np.random.Generator(np.random.PCG64(seed))
    samples = np.empty(resamples, dtype="float64")
    for index in range(resamples):
        selected = rng.integers(0, len(gains_array), size=len(gains_array))
        samples[index] = gains_array[selected].mean()
    return {
        "unit": "item",
        "items": int(len(unique_items)),
        "resamples": int(resamples),
        "seed": int(seed),
        "mean_accuracy_gain": float(gains_array.mean()),
        "per_item_accuracy_gain": [float(value) for value in gains_array.tolist()],
        "confidence_interval_95": [
            float(np.percentile(samples, 2.5)),
            float(np.percentile(samples, 97.5)),
        ],
    }


def _valid_frame_labels(partition) -> dict[str, Any]:
    np = _require_numpy()
    labels = []
    items = []
    for item_index, length_value in enumerate(partition.frame_lengths.tolist()):
        length = int(length_value)
        labels.append(partition.frame_labels[item_index, :length])
        items.append(np.full(length, item_index, dtype="int32"))
    return {"labels": np.concatenate(labels), "item_indices": np.concatenate(items)}


def _constant_predictions(length: int, predicted_class: int):
    return _require_numpy().full(length, predicted_class, dtype="int64")


def _partition_array_bytes(partition) -> int:
    return int(
        partition.signals.nbytes
        + partition.input_lengths.nbytes
        + partition.sample_labels.nbytes
        + partition.frame_labels.nbytes
        + partition.frame_lengths.nbytes
        + partition.item_ids.nbytes
        + partition.motif_sequences.nbytes
        + partition.motif_lengths.nbytes
    )


def _partition_open_count(events: list[dict[str, object]], split: str) -> int:
    return sum(
        event.get("split") == split and event.get("action") == "partition_arrays_opened"
        for event in events
    )


def _checkpoint_event_index(events: list[dict[str, object]]) -> int:
    indices = [
        int(event["event_index"])
        for event in events
        if event.get("stage") == "checkpoint_freeze"
    ]
    return min(indices) if indices else sys.maxsize


def _access_sequence_passed(
    events: list[dict[str, object]], *, test_opened: bool
) -> bool:
    if _partition_open_count(events, "train") != 1:
        return False
    if _partition_open_count(events, "validation") != 1:
        return False
    if _partition_open_count(events, "test") != (1 if test_opened else 0):
        return False
    stage_indices = {
        str(event["stage"]): int(event["event_index"])
        for event in events
    }
    required = (
        "manifest_validation",
        "train_open",
        "validation_open",
        "train_fit",
        "validation_selection",
    )
    if any(stage not in stage_indices for stage in required):
        return False
    if [stage_indices[stage] for stage in required] != sorted(
        stage_indices[stage] for stage in required
    ):
        return False
    if test_opened:
        test_required = (
            "checkpoint_freeze",
            "frozen_test_open",
            "frozen_test_evaluation",
        )
        if any(stage not in stage_indices for stage in test_required):
            return False
        if [stage_indices[stage] for stage in test_required] != sorted(
            stage_indices[stage] for stage in test_required
        ):
            return False
        if stage_indices["validation_selection"] >= stage_indices["checkpoint_freeze"]:
            return False
    return not any(
        event.get("split") == "test"
        and int(event["event_index"]) < _checkpoint_event_index(events)
        for event in events
    )


def _access_event(
    events: list[dict[str, object]],
    *,
    stage: str,
    split: str | None,
    action: str,
    **values,
) -> dict[str, object]:
    return {
        "event_index": len(events),
        "stage": stage,
        "split": split,
        "action": action,
        **{key: value for key, value in values.items() if value is not None},
    }


def _finalize_report_texts(
    report: dict[str, Any],
    *,
    markdown_requested: bool,
    max_artifact_bytes: int,
    base_gate_passed: bool,
) -> tuple[str, str | None]:
    checkpoint_bytes = int(report["artifacts"]["checkpoint_bytes"])
    for _ in range(16):
        markdown = _report_markdown(report) if markdown_requested else None
        markdown_bytes = len(markdown.encode("utf-8")) if markdown else 0
        report["artifacts"]["markdown_bytes"] = markdown_bytes
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_bytes = len(json_text.encode("utf-8"))
        total = checkpoint_bytes + markdown_bytes + json_bytes
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
            artifact_gate_passed=artifact_passed,
        )
        if not changed:
            final_markdown = _report_markdown(report) if markdown_requested else None
            final_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
            if len(final_json.encode("utf-8")) != report["artifacts"]["json_bytes"]:
                continue
            return final_json, final_markdown
    raise RuntimeError("tiny causal gate report byte accounting did not converge")


def _report_markdown(report: Mapping[str, Any]) -> str:
    selection = report["selection"]
    test = report["frozen_test"]
    resources = report["resources"]
    lines = [
        "# Tiny Learned Causal Encoder Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Decision: `{report['decision']}`",
        f"- Registered protocol: `{str(report['registered_protocol_match']).lower()}`",
        f"- Parameters: {report['model']['trainable_parameters']}",
        f"- Selected epoch: {selection['best_epoch']} / {selection['epochs_ran']}",
        (
            "- Validation balanced accuracy: "
            f"{selection['validation_metrics_batch']['balanced_accuracy']:.6f}"
        ),
        f"- Frozen test opened: `{str(test['opened']).lower()}`",
    ]
    if test["metrics"] is not None:
        lines.extend(
            [
                f"- Frozen test accuracy: {test['metrics']['accuracy']:.6f}",
                (
                    "- Frozen test balanced accuracy: "
                    f"{test['metrics']['balanced_accuracy']:.6f}"
                ),
                (
                    "- Prior / zero-signal balanced accuracy: "
                    f"{test['prior']['balanced_accuracy']:.6f} / "
                    f"{test['zero_signal']['balanced_accuracy']:.6f}"
                ),
            ]
        )
    lines.extend(
        [
            f"- Streaming schedules passed: {report['streaming_replay']['schedules_passed'] if report['streaming_replay'] else 0}/5",
            f"- Mutable array state: {resources['mutable_array_state_bytes']} bytes",
            f"- Runtime: {resources['runtime_before_report_write_sec']:.6f} sec",
            f"- Peak RSS: {resources['peak_rss_bytes']} bytes",
            "",
            "## Access Audit",
            "",
            f"- Train opens: {report['access_audit']['train_semantic_open_count']}",
            f"- Validation opens: {report['access_audit']['validation_semantic_open_count']}",
            f"- Test opens: {report['access_audit']['test_semantic_open_count']}",
            f"- Checkpoint frozen before test: `{str(selection['checkpoint_frozen_before_test']).lower()}`",
            "",
            "## Claim Boundaries",
            "",
        ]
    )
    lines.extend(f"- {value}" for value in report["claim_boundaries"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- `{value}`" for value in report["warnings"])
    return "\n".join(lines) + "\n"


def _prepare_outputs(paths: list[Path | None]) -> None:
    planned = [path for path in paths if path is not None]
    normalized = [path.expanduser().resolve(strict=False) for path in planned]
    if len(set(normalized)) != len(normalized):
        raise ValueError("tiny causal gate output paths must be distinct")
    for path in planned:
        if path.exists():
            raise FileExistsError(f"Refusing to replace existing Loop 22 artifact: {path}")


def _validate_caps(caps: TinyCausalGateCaps) -> None:
    values = asdict(caps)
    for name, value in values.items():
        normalized = float(value)
        if not math.isfinite(normalized) or normalized <= 0:
            raise ValueError(f"{name} must be finite and positive")


def _require_single_thread_environment() -> dict[str, str]:
    values = {name: os.environ.get(name) for name in THREAD_ENV_VARS}
    invalid = [name for name, value in values.items() if value != "1"]
    if invalid:
        assignments = " ".join(f"{name}=1" for name in THREAD_ENV_VARS)
        raise RuntimeError(
            "Loop 22 requires one-thread numeric environment variables before "
            f"NumPy/Torch import; set `{assignments}`. Invalid: {', '.join(invalid)}"
        )
    return {name: str(value) for name, value in values.items()}


def _gate_decision(
    *,
    gate_passed: bool,
    mechanical_gate_passed: bool,
    registered_protocol_match: bool,
    artifact_gate_passed: bool | None,
) -> str:
    if gate_passed:
        return "proceed_to_preregistered_synthetic_streaming_decoder_gate"
    if (
        mechanical_gate_passed
        and not registered_protocol_match
        and artifact_gate_passed is not False
    ):
        return "nonregistered_fixture_mechanics_only"
    return "park_tiny_causal_encoder_branch"


def _array_sha256(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        raise RuntimeError(
            "Tiny causal encoder gate requires NumPy: `pip install numpy`."
        ) from exc
    return np
