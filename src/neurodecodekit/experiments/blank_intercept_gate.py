"""Preregistered fresh-split blank-intercept calibration gate."""

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

from neurodecodekit.evaluation.blank_calibration import (
    BLANK_CALIBRATION_CONFIG_SHA256,
    blank_binary_metrics,
    blank_margins_from_logits,
    fit_blank_intercept,
    paired_metric_bootstrap,
    paired_sequence_change_metrics,
)
from neurodecodekit.evaluation.incremental_ctc import (
    fit_most_frequent_sequence_prior,
    sequence_metrics,
)
from neurodecodekit.experiments.causal_replay_gate import REGISTERED_SCHEDULES
from neurodecodekit.experiments.streaming_ctc_gate import (
    BEAM_WIDTH,
    MAX_PREFIX_LENGTH,
    REGISTERED_CHECKPOINT_SHA256,
    REGISTERED_CONFIG_SHA256,
    REGISTERED_PARAMETER_COUNT,
    REGISTERED_PARAMETER_PAYLOAD_SHA256,
    _access_event,
    _canonical_partition_decode,
    _partition_array_bytes,
    _partition_targets,
    _run_validation_replay,
    _zero_signal_predictions,
)
from neurodecodekit.models.tiny_causal_encoder import (
    canonical_partition_outputs,
    load_tiny_causal_encoder_checkpoint,
)
from neurodecodekit.training.ctc_symbol_stream import (
    FRAME_ONLY_MEMBERS,
    PARTITION_NAMES,
    TARGET_ONLY_MEMBERS,
    load_blank_calibration_manifest,
    load_ctc_symbol_stream_partition,
    registered_blank_calibration_protocol,
    resolve_ctc_symbol_partition_path,
)


BLANK_INTERCEPT_GATE_SCHEMA_NAME = "b2q-blank-intercept-calibration-gate"
BLANK_INTERCEPT_GATE_SCHEMA_VERSION = 0
PROOF_POSTURE = "supervised_synthetic_blank_calibration_only"
REGISTERED_PROTOCOL_SHA256 = (
    "ac8b0dfa1ee512dd55645356546a068bc6b7e145f945a2e947d63dcf87185cc9"
)
REGISTERED_GATE_CONFIG_SHA256 = (
    "7b2c7c061d1a286b1dc051677c19f4395601e5cbb3e80c5b8f3c991ee912ac58"
)
BOOTSTRAP_RESAMPLES = 2000
BOOTSTRAP_SEED = 2354
MAXIMUM_CER = 0.03
MINIMUM_EXACT_ACCURACY = 0.875
MINIMUM_EXACT_GAIN = 0.125
MINIMUM_CORRECTED_ITEMS = 2
MAXIMUM_NEW_ERROR_ITEMS = 0
MINIMUM_TAIL_TOKEN_REDUCTION = 2
MINIMUM_REPEAT_RATE = 0.875
MINIMUM_CONTROL_CER_REDUCTION = 0.40
MINIMUM_CONTROL_EXACT_GAIN = 0.50
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


@dataclass(frozen=True)
class BlankInterceptGateCaps:
    max_fixture_bytes: int = 1 * 1024 * 1024
    max_items: int = 96
    max_samples_per_item: int = 128
    max_total_frames: int = 3000
    max_calibration_parameter_bytes: int = 8
    max_encoder_state_bytes: int = 1 * 1024
    max_decoder_state_bytes: int = 4 * 1024
    max_working_bytes: int = 16 * 1024 * 1024
    max_runtime_sec: float = 20.0
    max_peak_rss_bytes: int = 768 * 1024 * 1024
    max_report_bytes: int = 1 * 1024 * 1024
    max_total_generated_bytes: int = 2 * 1024 * 1024
    max_total_pushes: int = 100_000

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def registered_blank_intercept_gate_caps() -> BlankInterceptGateCaps:
    return BlankInterceptGateCaps()


def run_blank_intercept_gate(
    *,
    fixture_manifest_path: str | Path,
    checkpoint_path: str | Path,
    out_json_path: str | Path,
    out_markdown_path: str | Path | None = None,
    require_registered_protocol: bool = True,
    require_registered_checkpoint: bool = True,
    caps: BlankInterceptGateCaps | None = None,
) -> dict[str, Any]:
    """Fit one train-frame blank intercept, validate, then conditionally test."""

    started_at = time.perf_counter()
    selected_caps = caps or registered_blank_intercept_gate_caps()
    _validate_caps(selected_caps)
    thread_environment = _require_single_thread_environment()
    manifest_path = Path(fixture_manifest_path)
    frozen_checkpoint_path = Path(checkpoint_path)
    json_path = Path(out_json_path)
    markdown_path = Path(out_markdown_path) if out_markdown_path else None
    _prepare_outputs([json_path, markdown_path])
    access_events: list[dict[str, object]] = []

    manifest = load_blank_calibration_manifest(
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
    registered_protocol = registered_blank_calibration_protocol()
    protocol_match = manifest["protocol"] == registered_protocol.to_dict()
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
        raise ValueError("Loop 23.5 fixture exceeds its byte cap")
    if total_items > selected_caps.max_items:
        raise ValueError("Loop 23.5 fixture exceeds its item cap")
    if total_frames > selected_caps.max_total_frames:
        raise ValueError("Loop 23.5 fixture exceeds its frame cap")
    if max_samples > selected_caps.max_samples_per_item:
        raise ValueError("Loop 23.5 fixture exceeds its sample cap")

    checkpoint_sha256 = _file_sha256(frozen_checkpoint_path)
    if require_registered_checkpoint and checkpoint_sha256 != REGISTERED_CHECKPOINT_SHA256:
        raise ValueError("Loop 23.5 checkpoint does not match the registered file hash")
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
        raise ValueError("Loop 23.5 checkpoint metadata does not match preregistration")
    if (
        producer.n_channels != registered_protocol.n_channels
        or producer.kernel_size != registered_protocol.kernel_size
        or producer.stride != registered_protocol.stride
        or producer.n_classes != registered_protocol.n_classes
        or producer.embedding_dim != 8
        or producer.producer_right_context_samples != 0
    ):
        raise ValueError("Loop 23.5 checkpoint geometry does not match the fixture")
    access_events.append(
        _access_event(
            access_events,
            stage="checkpoint_validation",
            split=None,
            action="frozen_checkpoint_hashed_loaded_no_parameter_update",
            checkpoint_sha256=checkpoint_sha256,
        )
    )

    train_frames = _open_partition(
        manifest_path,
        manifest,
        "train",
        access_mode="frames-only",
        access_events=access_events,
        stage="train_frames_open",
    )
    train_outputs = canonical_partition_outputs(producer, train_frames)
    train_labels = _flatten_frame_labels(train_frames)
    train_margins = blank_margins_from_logits(train_outputs["logits"].tolist())
    fit = fit_blank_intercept(train_margins, [value == 0 for value in train_labels])
    if fit.config_sha256 != BLANK_CALIBRATION_CONFIG_SHA256:
        raise RuntimeError("Loop 23.5 fitted calibration config hash drifted")
    if selected_caps.max_calibration_parameter_bytes < 8:
        raise ValueError("Loop 23.5 calibration parameter exceeds its byte cap")
    access_events.append(
        _access_event(
            access_events,
            stage="calibration_freeze",
            split="train",
            action="one_blank_intercept_fitted_frozen_and_hashed",
            calibration_config_sha256=fit.config_sha256,
            calibration_payload_sha256=fit.parameter_payload_sha256,
        )
    )

    train_targets_partition = _open_partition(
        manifest_path,
        manifest,
        "train",
        access_mode="targets-only",
        access_events=access_events,
        stage="train_targets_open",
    )
    train_targets = _partition_targets(train_targets_partition)
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
    validation_outputs = canonical_partition_outputs(producer, validation)
    validation_unmodified = _canonical_partition_decode(
        producer, validation, outputs=validation_outputs
    )
    validation_calibrated = _canonical_partition_decode(
        producer,
        validation,
        outputs=validation_outputs,
        blank_logit_bias=fit.intercept,
    )
    validation_targets = [tuple(row) for row in validation_calibrated["targets"]]
    validation_prior_predictions = [prior_sequence] * len(validation_targets)
    validation_prior = sequence_metrics(
        validation_targets, validation_prior_predictions
    )
    validation_zero_unmodified_predictions = _zero_signal_predictions(
        producer, validation
    )
    validation_zero_calibrated_predictions = _zero_signal_predictions(
        producer, validation, blank_logit_bias=fit.intercept
    )
    validation_zero_unmodified = sequence_metrics(
        validation_targets, validation_zero_unmodified_predictions
    )
    validation_zero_calibrated = sequence_metrics(
        validation_targets, validation_zero_calibrated_predictions
    )
    validation_paired = paired_sequence_change_metrics(
        validation_targets,
        validation_unmodified["prefix_predictions"],
        validation_calibrated["prefix_predictions"],
    )
    validation_blank = _partition_blank_metrics(
        validation_outputs, validation, intercept=fit.intercept
    )
    replay_unmodified = _run_validation_replay(
        producer,
        validation,
        validation_unmodified,
        max_total_pushes=selected_caps.max_total_pushes,
        max_chunk_samples=selected_caps.max_samples_per_item,
    )
    replay_calibrated = _run_validation_replay(
        producer,
        validation,
        validation_calibrated,
        max_total_pushes=selected_caps.max_total_pushes,
        max_chunk_samples=selected_caps.max_samples_per_item,
        blank_logit_bias=fit.intercept,
    )
    combined_pushes = int(
        replay_unmodified["total_pushes"] + replay_calibrated["total_pushes"]
    )
    replay_passed = bool(
        replay_unmodified["passed"]
        and replay_calibrated["passed"]
        and combined_pushes <= selected_caps.max_total_pushes
    )
    max_encoder_state = max(
        int(replay_unmodified["max_encoder_state_bytes"]),
        int(replay_calibrated["max_encoder_state_bytes"]),
    )
    max_prefix_state = max(
        int(replay_unmodified["max_prefix_state_bytes"]),
        int(replay_calibrated["max_prefix_state_bytes"]),
    )
    max_greedy_state = max(
        int(replay_unmodified["max_greedy_state_bytes"]),
        int(replay_calibrated["max_greedy_state_bytes"]),
    )
    state_gate = bool(
        max_encoder_state <= selected_caps.max_encoder_state_bytes
        and max_prefix_state <= selected_caps.max_decoder_state_bytes
        and max_greedy_state <= selected_caps.max_decoder_state_bytes
    )
    pretest_runtime = time.perf_counter() - started_at
    pretest_peak_rss = _peak_rss_bytes()
    pretest_working_bytes = int(
        _partition_array_bytes(train_frames)
        + _partition_array_bytes(train_targets_partition)
        + _partition_array_bytes(validation)
        + _mapping_array_bytes(train_outputs)
        + _mapping_array_bytes(validation_outputs)
        + producer.fixed_parameter_bytes
        + 8
        + max_encoder_state
        + max_prefix_state
        + max_greedy_state
    )
    pretest_resource_gate = bool(
        pretest_runtime <= selected_caps.max_runtime_sec
        and pretest_peak_rss is not None
        and pretest_peak_rss <= selected_caps.max_peak_rss_bytes
        and pretest_working_bytes <= selected_caps.max_working_bytes
        and state_gate
    )
    validation_gate = _sequence_gate(
        calibrated=validation_calibrated,
        unmodified=validation_unmodified,
        prior=validation_prior,
        zero_calibrated=validation_zero_calibrated,
        paired=validation_paired,
        blank_metrics=validation_blank,
        replay_passed=replay_passed,
        resource_passed=pretest_resource_gate,
    )
    access_events.append(
        _access_event(
            access_events,
            stage="validation_decision",
            split="validation",
            action="fixed_validation_rule_applied_no_calibration_or_decoder_update",
            gate_passed=validation_gate["passed"],
        )
    )

    test = None
    test_outputs = None
    test_calibrated = None
    test_unmodified = None
    test_prior = None
    test_zero_calibrated = None
    test_zero_unmodified = None
    test_blank = None
    test_paired = None
    test_bootstrap = None
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
        test_outputs = canonical_partition_outputs(producer, test)
        test_unmodified = _canonical_partition_decode(
            producer, test, outputs=test_outputs
        )
        test_calibrated = _canonical_partition_decode(
            producer,
            test,
            outputs=test_outputs,
            blank_logit_bias=fit.intercept,
        )
        test_targets = [tuple(row) for row in test_calibrated["targets"]]
        test_prior_predictions = [prior_sequence] * len(test_targets)
        test_prior = sequence_metrics(test_targets, test_prior_predictions)
        test_zero_unmodified_predictions = _zero_signal_predictions(producer, test)
        test_zero_calibrated_predictions = _zero_signal_predictions(
            producer, test, blank_logit_bias=fit.intercept
        )
        test_zero_unmodified = sequence_metrics(
            test_targets, test_zero_unmodified_predictions
        )
        test_zero_calibrated = sequence_metrics(
            test_targets, test_zero_calibrated_predictions
        )
        test_paired = paired_sequence_change_metrics(
            test_targets,
            test_unmodified["prefix_predictions"],
            test_calibrated["prefix_predictions"],
        )
        test_blank = _partition_blank_metrics(
            test_outputs, test, intercept=fit.intercept
        )
        test_bootstrap = paired_metric_bootstrap(
            test_targets,
            test_unmodified["prefix_predictions"],
            test_calibrated["prefix_predictions"],
            resamples=BOOTSTRAP_RESAMPLES,
            seed=BOOTSTRAP_SEED,
        )
        test_gate = _sequence_gate(
            calibrated=test_calibrated,
            unmodified=test_unmodified,
            prior=test_prior,
            zero_calibrated=test_zero_calibrated,
            paired=test_paired,
            blank_metrics=test_blank,
            replay_passed=True,
            resource_passed=True,
            bootstrap=test_bootstrap,
        )
        test_gate = {
            **test_gate,
            "opened": True,
            "reason": (
                "all_frozen_test_thresholds_passed"
                if test_gate["passed"]
                else "one_or_more_frozen_test_thresholds_failed"
            ),
        }
        access_events.append(
            _access_event(
                access_events,
                stage="frozen_test_evaluation",
                split="test",
                action="single_canonical_calibrated_and_comparator_evaluation_no_fit",
                checkpoint_sha256=checkpoint_sha256,
            )
        )

    runtime_before_report = time.perf_counter() - started_at
    peak_rss = _peak_rss_bytes()
    loaded_array_bytes = int(
        _partition_array_bytes(train_frames)
        + _partition_array_bytes(train_targets_partition)
        + _partition_array_bytes(validation)
        + (_partition_array_bytes(test) if test is not None else 0)
    )
    output_array_bytes = int(
        _mapping_array_bytes(train_outputs)
        + _mapping_array_bytes(validation_outputs)
        + (_mapping_array_bytes(test_outputs) if test_outputs is not None else 0)
    )
    working_core_bytes = int(
        loaded_array_bytes
        + output_array_bytes
        + producer.fixed_parameter_bytes
        + 8
        + max_encoder_state
        + max_prefix_state
        + max_greedy_state
    )
    resource_gate = bool(
        runtime_before_report <= selected_caps.max_runtime_sec
        and peak_rss is not None
        and peak_rss <= selected_caps.max_peak_rss_bytes
        and working_core_bytes <= selected_caps.max_working_bytes
        and state_gate
    )
    test_open_count = _partition_open_count(access_events, "test")
    access_gate = _access_sequence_passed(access_events, test_opened=test is not None)
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
            "name": BLANK_INTERCEPT_GATE_SCHEMA_NAME,
            "version": BLANK_INTERCEPT_GATE_SCHEMA_VERSION,
        },
        "proof_posture": PROOF_POSTURE,
        "gate_passed": base_gate,
        "mechanical_gate_passed": mechanical_gate,
        "decision": _gate_decision(
            gate_passed=base_gate,
            mechanical_gate_passed=mechanical_gate,
            protocol_match=protocol_match,
            checkpoint_match=checkpoint_match,
            artifact_passed=None,
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
        },
        "calibration": {
            "method": "intercept_only_blank_vs_aggregate_nonblank",
            "intercept": fit.intercept,
            "parameters": 1,
            "parameter_bytes_float64": 8,
            "fit_iterations": fit.iterations,
            "fit_bracket_final": [fit.lower_bound, fit.upper_bound],
            "final_gradient": fit.final_gradient,
            "train_frames": fit.train_frames,
            "train_blank_frames": fit.train_blank_frames,
            "train_metrics_before": fit.train_metrics_before,
            "train_metrics_after": fit.train_metrics_after,
            "config_sha256": fit.config_sha256,
            "parameter_payload_sha256": fit.parameter_payload_sha256,
            "fit_split": "train_frames",
            "target_ids_opened_during_fit": False,
            "validation_used_for_fit": False,
            "test_used_for_fit": False,
            "slope": 1.0,
            "temperature": None,
            "regularization": None,
            "candidates": 1,
            "restarts": 0,
        },
        "decoder": {
            "blank_id": 0,
            "beam_width": BEAM_WIDTH,
            "max_prefix_length": MAX_PREFIX_LENGTH,
            "symbol_logits_changed": False,
            "blank_intercept_only": True,
            "language_model": None,
            "lexicon": None,
            "insertion_bonus": 0.0,
            "score_threshold": None,
            "target_length_trim": False,
            "endpoint_detector": False,
            "known_item_end_flush": True,
            "right_context_samples": 0,
        },
        "train_only_prior": {
            "opened_members": list(train_targets_partition.opened_members),
            "signals_opened": train_targets_partition.signals is not None,
            "fitted_sequence": list(prior_sequence),
            "fit_items": len(train_targets),
        },
        "validation": {
            "calibrated": validation_calibrated,
            "unmodified": _compact_decode_report(validation_unmodified),
            "blank_calibration": validation_blank,
            "paired_change": validation_paired,
            "prior": validation_prior,
            "zero_signal_calibrated": validation_zero_calibrated,
            "zero_signal_unmodified": validation_zero_unmodified,
            "gate": validation_gate,
            "used_for_calibration_fit": False,
        },
        "streaming_replay": {
            "passed": replay_passed,
            "registered_schedules": list(REGISTERED_SCHEDULES),
            "unmodified": replay_unmodified,
            "calibrated": replay_calibrated,
            "combined_pushes": combined_pushes,
            "test_replays": 0,
        },
        "frozen_test": {
            "opened": test is not None,
            "semantic_open_count": test_open_count,
            "calibrated": (
                _compact_decode_report(test_calibrated)
                if test_calibrated is not None
                else None
            ),
            "unmodified": (
                _compact_decode_report(test_unmodified)
                if test_unmodified is not None
                else None
            ),
            "blank_calibration": test_blank,
            "paired_change": test_paired,
            "bootstrap_vs_unmodified": test_bootstrap,
            "prior": test_prior,
            "zero_signal_calibrated": test_zero_calibrated,
            "zero_signal_unmodified": test_zero_unmodified,
            "gate": test_gate,
            "calibration_or_model_fit_after_open": False,
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
            "producer_output_array_bytes": output_array_bytes,
            "fixed_model_and_normalization_bytes": producer.fixed_parameter_bytes,
            "max_encoder_state_bytes": max_encoder_state,
            "max_prefix_state_bytes": max_prefix_state,
            "max_greedy_state_bytes": max_greedy_state,
            "thread_environment": thread_environment,
            "caps": selected_caps.to_dict(),
            "resource_gate_passed": resource_gate,
        },
        "execution_counts": {
            "training_runs": 0,
            "parameter_updates": 0,
            "calibration_fits": 1,
            "calibration_candidates": 1,
            "decoder_configs": 2,
            "language_model_runs": 0,
            "validation_schedule_replays": 10,
            "test_schedule_replays": 0,
            "test_partition_opens": test_open_count,
            "raw_data_reads": 0,
            "real_data_reads": 0,
            "network_fetches": 0,
        },
        "warnings": [
            "supervised_synthetic_frame_calibration_only",
            "target_length_independent_inference_not_label_free_fit",
            "frozen_probe_not_trained_with_ctc_loss",
            "prefix_partials_are_revocable_no_online_commit_policy",
            "known_item_end_is_not_live_endpoint_detection",
            "synthetic_cer_is_not_meg_eeg_or_language_performance",
            "end_to_end_latency_unmeasured",
            "seeds_2203_and_2303_remain_consumed",
        ],
        "claim_boundaries": [
            "The source motifs and frame labels are generated, not neural recordings.",
            "The fitted scalar uses supervised blank labels and is not label-free.",
            "The output alphabet is five synthetic symbols, not natural text.",
            "No language model, endpoint, target-length trim, or online commitment is used.",
            "No real MEG/EEG, unseen-person, portable, clinical, or arbitrary-thought claim follows.",
        ],
        "artifacts": {
            "json_path": str(json_path),
            "markdown_path": str(markdown_path) if markdown_path else None,
            "json_bytes": 0,
            "markdown_bytes": 0,
            "report_bytes": 0,
            "fixture_plus_report_bytes": fixture_bytes,
            "artifact_gate_passed": False,
        },
    }
    json_text, markdown_text = _finalize_report_texts(
        report,
        markdown_requested=markdown_path is not None,
        fixture_bytes=fixture_bytes,
        caps=selected_caps,
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


def _flatten_frame_labels(partition) -> list[int]:
    rows = []
    for index, length_value in enumerate(partition.frame_lengths.tolist()):
        rows.extend(
            int(value)
            for value in partition.frame_labels[index, : int(length_value)].tolist()
        )
    if not rows:
        raise ValueError("Loop 23.5 partition has no valid frame labels")
    return rows


def _partition_blank_metrics(outputs, partition, *, intercept: float) -> dict[str, Any]:
    margins = blank_margins_from_logits(outputs["logits"].tolist())
    labels = [value == 0 for value in _flatten_frame_labels(partition)]
    return {
        "before": blank_binary_metrics(margins, labels, intercept=0.0),
        "after": blank_binary_metrics(margins, labels, intercept=intercept),
    }


def _sequence_gate(
    *,
    calibrated,
    unmodified,
    prior,
    zero_calibrated,
    paired,
    blank_metrics,
    replay_passed: bool,
    resource_passed: bool,
    bootstrap=None,
) -> dict[str, Any]:
    calibrated_metrics = calibrated["prefix_metrics"]
    unmodified_metrics = unmodified["prefix_metrics"]
    greedy_metrics = calibrated["greedy_metrics"]
    exact_gain = float(calibrated_metrics["exact_sequence_accuracy"]) - float(
        unmodified_metrics["exact_sequence_accuracy"]
    )
    prior_reduction = float(prior["corpus_cer"]) - float(
        calibrated_metrics["corpus_cer"]
    )
    zero_reduction = float(zero_calibrated["corpus_cer"]) - float(
        calibrated_metrics["corpus_cer"]
    )
    control_exact_gain = float(calibrated_metrics["exact_sequence_accuracy"]) - max(
        float(prior["exact_sequence_accuracy"]),
        float(zero_calibrated["exact_sequence_accuracy"]),
    )
    blank_nll_improved = float(
        blank_metrics["after"]["negative_log_likelihood"]
    ) < float(blank_metrics["before"]["negative_log_likelihood"])
    blank_brier_improved = float(blank_metrics["after"]["brier_score"]) < float(
        blank_metrics["before"]["brier_score"]
    )
    bootstrap_passed = bool(
        bootstrap is None
        or (
            float(bootstrap["exact_accuracy_gain_interval_95"][0]) >= 0.0
            and float(bootstrap["cer_reduction_interval_95"][0]) >= 0.0
        )
    )
    passed = bool(
        float(calibrated_metrics["corpus_cer"]) <= MAXIMUM_CER
        and float(calibrated_metrics["exact_sequence_accuracy"])
        >= MINIMUM_EXACT_ACCURACY
        and float(calibrated_metrics["repeated_pair_reconstruction_rate"])
        >= MINIMUM_REPEAT_RATE
        and exact_gain >= MINIMUM_EXACT_GAIN
        and int(paired["corrected_items"]) >= MINIMUM_CORRECTED_ITEMS
        and int(paired["new_error_items"]) <= MAXIMUM_NEW_ERROR_ITEMS
        and int(paired["items_with_worse_cer"]) == 0
        and int(paired["tail_inserted_token_reduction"])
        >= MINIMUM_TAIL_TOKEN_REDUCTION
        and blank_nll_improved
        and blank_brier_improved
        and prior_reduction >= MINIMUM_CONTROL_CER_REDUCTION
        and zero_reduction >= MINIMUM_CONTROL_CER_REDUCTION
        and control_exact_gain >= MINIMUM_CONTROL_EXACT_GAIN
        and float(calibrated_metrics["corpus_cer"])
        <= float(greedy_metrics["corpus_cer"])
        and replay_passed
        and resource_passed
        and bootstrap_passed
    )
    return {
        "passed": passed,
        "calibrated_cer": calibrated_metrics["corpus_cer"],
        "unmodified_cer": unmodified_metrics["corpus_cer"],
        "calibrated_exact_accuracy": calibrated_metrics["exact_sequence_accuracy"],
        "unmodified_exact_accuracy": unmodified_metrics["exact_sequence_accuracy"],
        "exact_accuracy_gain": exact_gain,
        "repeat_reconstruction_rate": calibrated_metrics[
            "repeated_pair_reconstruction_rate"
        ],
        "corrected_items": paired["corrected_items"],
        "new_error_items": paired["new_error_items"],
        "items_with_worse_cer": paired["items_with_worse_cer"],
        "tail_inserted_token_reduction": paired["tail_inserted_token_reduction"],
        "blank_nll_improved": blank_nll_improved,
        "blank_brier_improved": blank_brier_improved,
        "cer_reduction_vs_prior": prior_reduction,
        "cer_reduction_vs_zero_signal": zero_reduction,
        "exact_gain_over_stronger_signal_free_control": control_exact_gain,
        "calibrated_prefix_minus_greedy_cer": float(
            calibrated_metrics["corpus_cer"]
        )
        - float(greedy_metrics["corpus_cer"]),
        "replay_passed": replay_passed,
        "resource_gate_passed": resource_passed,
        "bootstrap_passed": bootstrap_passed,
        "thresholds": _registered_thresholds(),
        "config_sha256": REGISTERED_GATE_CONFIG_SHA256,
    }


def _registered_thresholds() -> dict[str, object]:
    values = {
        "maximum_cer": MAXIMUM_CER,
        "maximum_new_error_items": MAXIMUM_NEW_ERROR_ITEMS,
        "minimum_control_cer_reduction": MINIMUM_CONTROL_CER_REDUCTION,
        "minimum_control_exact_gain": MINIMUM_CONTROL_EXACT_GAIN,
        "minimum_corrected_items": MINIMUM_CORRECTED_ITEMS,
        "minimum_exact_accuracy": MINIMUM_EXACT_ACCURACY,
        "minimum_exact_gain": MINIMUM_EXACT_GAIN,
        "minimum_repeat_rate": MINIMUM_REPEAT_RATE,
        "minimum_tail_token_reduction": MINIMUM_TAIL_TOKEN_REDUCTION,
        "require_blank_brier_improvement": True,
        "require_blank_nll_improvement": True,
        "require_no_item_cer_worsening": True,
        "require_prefix_not_worse_than_greedy": True,
    }
    if _sha256_json(values) != REGISTERED_GATE_CONFIG_SHA256:
        raise RuntimeError("registered Loop 23.5 threshold hash drifted")
    return values


def _compact_decode_report(report: Mapping[str, Any]) -> dict[str, Any]:
    item_rows = []
    trace_payload = []
    for item in report["items"]:
        trace_payload.append(item["trace"])
        item_rows.append(
            {
                "item_id": item["item_id"],
                "target": item["target"],
                "prefix_final": item["prefix_final"],
                "greedy_final": item["greedy_final"],
                "partial_metrics": {
                    key: value
                    for key, value in item["partial_metrics"].items()
                    if key != "longest_common_prefix_by_frame"
                },
            }
        )
    return {
        key: value
        for key, value in report.items()
        if key not in {"targets", "items"}
    } | {
        "items": item_rows,
        "frame_trace_sha256": _sha256_json(trace_payload),
        "frame_traces_stored": False,
    }


def _access_sequence_passed(events, *, test_opened: bool) -> bool:
    if _partition_open_count(events, "train") != 2:
        return False
    if _partition_open_count(events, "validation") != 1:
        return False
    if _partition_open_count(events, "test") != (1 if test_opened else 0):
        return False
    stages = {str(event["stage"]): int(event["event_index"]) for event in events}
    required = (
        "manifest_validation",
        "checkpoint_validation",
        "train_frames_open",
        "calibration_freeze",
        "train_targets_open",
        "prior_fit",
        "validation_open",
        "validation_decision",
    )
    if any(stage not in stages for stage in required):
        return False
    if [stages[stage] for stage in required] != sorted(stages[stage] for stage in required):
        return False
    frame_event = next(event for event in events if event["stage"] == "train_frames_open")
    target_event = next(event for event in events if event["stage"] == "train_targets_open")
    if frame_event.get("opened_members") != list(FRAME_ONLY_MEMBERS):
        return False
    if target_event.get("opened_members") != list(TARGET_ONLY_MEMBERS):
        return False
    if test_opened:
        if "frozen_test_open" not in stages or "frozen_test_evaluation" not in stages:
            return False
        if not (
            stages["validation_decision"]
            < stages["frozen_test_open"]
            < stages["frozen_test_evaluation"]
        ):
            return False
    return True


def _partition_open_count(events, split: str) -> int:
    return sum(
        event.get("split") == split
        and str(event.get("action", "")).startswith("partition_opened_")
        for event in events
    )


def _mapping_array_bytes(values: Mapping[str, Any] | None) -> int:
    if values is None:
        return 0
    return sum(
        int(value.nbytes)
        for value in values.values()
        if hasattr(value, "nbytes")
    )


def _finalize_report_texts(
    report,
    *,
    markdown_requested: bool,
    fixture_bytes: int,
    caps: BlankInterceptGateCaps,
    base_gate_passed: bool,
):
    for _ in range(20):
        markdown = _report_markdown(report) if markdown_requested else None
        markdown_bytes = len(markdown.encode("utf-8")) if markdown else 0
        report["artifacts"]["markdown_bytes"] = markdown_bytes
        json_text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        json_bytes = len(json_text.encode("utf-8"))
        report_bytes = json_bytes + markdown_bytes
        combined = fixture_bytes + report_bytes
        artifact_passed = bool(
            report_bytes <= caps.max_report_bytes
            and combined <= caps.max_total_generated_bytes
        )
        changed = (
            report["artifacts"]["json_bytes"] != json_bytes
            or report["artifacts"]["report_bytes"] != report_bytes
            or report["artifacts"]["fixture_plus_report_bytes"] != combined
            or report["artifacts"]["artifact_gate_passed"] != artifact_passed
            or report["gate_passed"] != bool(base_gate_passed and artifact_passed)
        )
        report["artifacts"]["json_bytes"] = json_bytes
        report["artifacts"]["report_bytes"] = report_bytes
        report["artifacts"]["fixture_plus_report_bytes"] = combined
        report["artifacts"]["artifact_gate_passed"] = artifact_passed
        report["gate_passed"] = bool(base_gate_passed and artifact_passed)
        report["decision"] = _gate_decision(
            gate_passed=bool(report["gate_passed"]),
            mechanical_gate_passed=bool(report["mechanical_gate_passed"]),
            protocol_match=bool(report["registered_protocol_match"]),
            checkpoint_match=bool(report["registered_checkpoint_match"]),
            artifact_passed=artifact_passed,
        )
        if not changed:
            final_markdown = _report_markdown(report) if markdown_requested else None
            final_json = json.dumps(report, indent=2, sort_keys=True) + "\n"
            if len(final_json.encode("utf-8")) == report["artifacts"]["json_bytes"]:
                return final_json, final_markdown
    raise RuntimeError("Loop 23.5 report byte accounting did not converge")


def _report_markdown(report) -> str:
    validation = report["validation"]
    test = report["frozen_test"]
    lines = [
        "# Blank Intercept Calibration Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Decision: `{report['decision']}`",
        f"- Blank intercept: {report['calibration']['intercept']:.12f}",
        f"- Validation calibrated/unmodified exact: {validation['calibrated']['prefix_metrics']['exact_sequence_accuracy']:.6f} / {validation['unmodified']['prefix_metrics']['exact_sequence_accuracy']:.6f}",
        f"- Validation calibrated/unmodified CER: {validation['calibrated']['prefix_metrics']['corpus_cer']:.6f} / {validation['unmodified']['prefix_metrics']['corpus_cer']:.6f}",
        f"- Validation schedules: {report['streaming_replay']['calibrated']['schedules_passed']}/5 calibrated and {report['streaming_replay']['unmodified']['schedules_passed']}/5 unmodified",
        f"- Frozen test opened: `{str(test['opened']).lower()}`",
    ]
    if test["calibrated"] is not None:
        lines.extend(
            [
                f"- Frozen test calibrated/unmodified exact: {test['calibrated']['prefix_metrics']['exact_sequence_accuracy']:.6f} / {test['unmodified']['prefix_metrics']['exact_sequence_accuracy']:.6f}",
                f"- Frozen test calibrated/unmodified CER: {test['calibrated']['prefix_metrics']['corpus_cer']:.6f} / {test['unmodified']['prefix_metrics']['corpus_cer']:.6f}",
            ]
        )
    lines.extend(
        [
            f"- Runtime: {report['resources']['runtime_before_report_write_sec']:.6f} sec",
            f"- Peak RSS: {report['resources']['peak_rss_bytes']} bytes",
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
    protocol_match,
    checkpoint_match,
    artifact_passed,
):
    if gate_passed:
        return "proceed_to_loop24_local_precision_runtime_gate"
    if (
        mechanical_gate_passed
        and (not protocol_match or not checkpoint_match)
        and artifact_passed is not False
    ):
        return "nonregistered_blank_calibration_mechanics_only"
    return "park_blank_intercept_calibration_branch"


def _prepare_outputs(paths) -> None:
    planned = [path for path in paths if path is not None]
    normalized = [path.expanduser().resolve(strict=False) for path in planned]
    if len(normalized) != len(set(normalized)):
        raise ValueError("Loop 23.5 output paths must be distinct")
    for path in planned:
        if path.exists():
            raise FileExistsError(f"Refusing to replace Loop 23.5 gate artifact: {path}")


def _validate_caps(caps: BlankInterceptGateCaps) -> None:
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
            "Loop 23.5 requires one-thread numeric environment variables before "
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


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()
