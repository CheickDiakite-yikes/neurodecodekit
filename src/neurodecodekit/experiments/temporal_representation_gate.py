"""Bounded synthetic-only Loop 48 Stage C temporal-representation gate."""

from __future__ import annotations

import hashlib
import json
import os
import resource
import shutil
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from neurodecodekit.evaluation.metrics import character_error_rate
from neurodecodekit.models.tiny_causal_temporal_ctc import (
    ABLATION_MODEL_ID,
    CANDIDATE_MODEL_ID,
    REGISTERED_RECIPE_IDS,
    load_tiny_causal_temporal_checkpoint,
    predict_tiny_causal_temporal_ctc,
    registered_temporal_ctc_config,
    save_tiny_causal_temporal_checkpoint,
    train_tiny_causal_temporal_ctc,
)
from neurodecodekit.training.temporal_motif_sentences import (
    generate_registered_temporal_motif_fixture,
    validate_temporal_motif_fixture,
)


RESULT_SCHEMA_NAME = "neurodecodekit.loop48_stage_c_synthetic_result"
RESULT_SCHEMA_VERSION = 0
PROOF_POSTURE = "synthetic_temporal_representation_mechanics_only"
THREAD_ENV_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


@dataclass(frozen=True)
class StageCSyntheticCaps:
    max_training_runs: int = 4
    max_optimizer_steps: int = 1800
    max_runtime_sec: float = 600.0
    max_peak_rss_bytes: int = 1024**3
    max_generated_artifact_bytes: int = 16 * 1024**2
    minimum_free_disk_bytes: int = 20 * 1024**3
    max_fixture_array_bytes: int = 4 * 1024**2
    cpu_threads: int = 1
    workers: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def registered_stage_c_synthetic_caps() -> StageCSyntheticCaps:
    return StageCSyntheticCaps()


def run_stage_c_synthetic_gate(
    *,
    research_registry_path: str | Path,
    output_dir: str | Path,
    caps: StageCSyntheticCaps | None = None,
) -> dict[str, Any]:
    """Run the one frozen four-fit synthetic calibration and final opening."""

    started_at = time.perf_counter()
    selected_caps = caps or registered_stage_c_synthetic_caps()
    _validate_caps(selected_caps)
    thread_environment = _require_single_thread_environment()
    registry_path = Path(research_registry_path)
    registry = _load_and_validate_research_registry(registry_path)
    output = Path(output_dir)
    _prepare_output_directory(output)
    free_disk_before = int(shutil.disk_usage(output.parent).free)
    if free_disk_before < selected_caps.minimum_free_disk_bytes:
        raise RuntimeError("Stage C synthetic gate requires at least 20 GiB free disk")

    fixture = generate_registered_temporal_motif_fixture()
    fixture_summary = validate_temporal_motif_fixture(fixture)
    if fixture_summary["array_bytes"] > selected_caps.max_fixture_array_bytes:
        raise RuntimeError("Stage C synthetic fixture exceeds its in-memory array cap")
    train = fixture.train
    selection = fixture.selection
    access_events = [
        _access_event(0, "fixture_generated", None, "synthetic_arrays_created_in_memory"),
        _access_event(1, "train_open", "train", "24_synthetic_rows_opened_for_fit"),
        _access_event(
            2,
            "selection_open",
            "selection",
            "8_synthetic_rows_opened_for_optimizer_selection",
        ),
    ]

    candidate_runs: list[dict[str, Any]] = []
    selected_training = None
    selected_prediction = None
    selected_key = None
    training_run_count = 0
    optimizer_steps = 0
    model_inference_runs = 0
    for recipe_id in REGISTERED_RECIPE_IDS:
        config = registered_temporal_ctc_config(recipe_id, architecture="candidate")
        training = train_tiny_causal_temporal_ctc(
            signals=train.signals,
            input_lengths=train.input_lengths,
            target_token_ids=train.target_token_ids,
            target_lengths=train.target_lengths,
            config=config,
        )
        training_run_count += 1
        optimizer_steps += training.optimizer_steps
        selection_prediction = predict_tiny_causal_temporal_ctc(
            training.model,
            signals=selection.signals,
            input_lengths=selection.input_lengths,
        )
        model_inference_runs += 1
        selection_metrics = _score_predictions(
            selection.target_texts,
            selection_prediction["predictions"],
        )
        run_summary = training.summary()
        run_summary.pop("loss_history")
        run_summary["final_loss"] = float(training.loss_history[-1])
        run_summary["selection_metrics"] = selection_metrics
        run_summary["selection_prediction_sha256"] = _sha256_json(
            selection_prediction["predictions"]
        )
        candidate_runs.append(run_summary)
        key = (
            float(selection_metrics["macro_cer"]),
            int(training.optimizer_steps),
            recipe_id,
        )
        if selected_key is None or key < selected_key:
            selected_key = key
            selected_training = training
            selected_prediction = selection_prediction

    if selected_training is None or selected_prediction is None or selected_key is None:
        raise RuntimeError("Stage C candidate calibration did not select a recipe")
    selected_recipe_id = selected_training.config.recipe_id
    access_events.append(
        _access_event(
            len(access_events),
            "candidate_selection_frozen",
            "selection",
            f"selected_{selected_recipe_id}_by_frozen_tie_break",
        )
    )

    ablation_config = registered_temporal_ctc_config(
        selected_recipe_id,
        architecture="ablation",
    )
    ablation_training = train_tiny_causal_temporal_ctc(
        signals=train.signals,
        input_lengths=train.input_lengths,
        target_token_ids=train.target_token_ids,
        target_lengths=train.target_lengths,
        config=ablation_config,
    )
    training_run_count += 1
    optimizer_steps += ablation_training.optimizer_steps
    if training_run_count > selected_caps.max_training_runs:
        raise RuntimeError("Stage C training-run cap exceeded")
    if optimizer_steps > selected_caps.max_optimizer_steps:
        raise RuntimeError("Stage C optimizer-step cap exceeded")

    candidate_checkpoint_path = output / "candidate_checkpoint.npz"
    ablation_checkpoint_path = output / "ablation_checkpoint.npz"
    common_checkpoint_metadata = {
        "proof_posture": PROOF_POSTURE,
        "fixture_sha256": fixture_summary["fixture_sha256"],
        "research_registry_sha256": _file_sha256(registry_path),
        "checkpoint_selection": "final_optimizer_step_only",
        "synthetic_final_opened_at_checkpoint_time": False,
        "real_data_rows_read": 0,
    }
    candidate_checkpoint = save_tiny_causal_temporal_checkpoint(
        candidate_checkpoint_path,
        model=selected_training.model,
        config=selected_training.config,
        metadata=common_checkpoint_metadata,
    )
    ablation_checkpoint = save_tiny_causal_temporal_checkpoint(
        ablation_checkpoint_path,
        model=ablation_training.model,
        config=ablation_training.config,
        metadata=common_checkpoint_metadata,
    )
    _require_artifact_cap(output, selected_caps.max_generated_artifact_bytes)

    final = fixture.final
    access_events.append(
        _access_event(
            len(access_events),
            "synthetic_final_open",
            "final",
            "same_8_synthetic_final_rows_opened_once_for_candidate_and_ablation",
        )
    )
    candidate_final = predict_tiny_causal_temporal_ctc(
        selected_training.model,
        signals=final.signals,
        input_lengths=final.input_lengths,
        include_logits=True,
    )
    ablation_final = predict_tiny_causal_temporal_ctc(
        ablation_training.model,
        signals=final.signals,
        input_lengths=final.input_lengths,
    )
    model_inference_runs += 2
    candidate_final_metrics = _score_predictions(
        final.target_texts,
        candidate_final["predictions"],
    )
    ablation_final_metrics = _score_predictions(
        final.target_texts,
        ablation_final["predictions"],
    )

    loaded_candidate, loaded_config, loaded_metadata = load_tiny_causal_temporal_checkpoint(
        candidate_checkpoint_path
    )
    checkpoint_replay = predict_tiny_causal_temporal_ctc(
        loaded_candidate,
        signals=final.signals,
        input_lengths=final.input_lengths,
        include_logits=True,
    )
    model_inference_runs += 1
    checkpoint_replay_identical = _prediction_reports_bitwise_equal(
        candidate_final,
        checkpoint_replay,
    )
    if loaded_config != selected_training.config:
        checkpoint_replay_identical = False
    if (
        loaded_metadata["parameter_payload_sha256"]
        != candidate_checkpoint["parameter_payload_sha256"]
    ):
        checkpoint_replay_identical = False

    future_mutation = _future_mutation_check(
        selected_training.model,
        final,
        candidate_final,
    )
    model_inference_runs += int(future_mutation["model_inference_runs"])
    prefix_resume = _prefix_resume_check(
        selected_training.model,
        final,
        candidate_final,
    )
    model_inference_runs += int(prefix_resume["model_inference_runs"])
    candidate_minus_ablation = float(ablation_final_metrics["macro_cer"]) - float(
        candidate_final_metrics["macro_cer"]
    )
    gates = {
        "candidate_final_cer": float(candidate_final_metrics["macro_cer"]),
        "candidate_final_cer_max": 0.1,
        "candidate_final_cer_passed": float(candidate_final_metrics["macro_cer"]) <= 0.1,
        "candidate_final_exact_sequences": int(candidate_final_metrics["exact_sequences"]),
        "candidate_final_exact_sequences_min": 7,
        "candidate_final_exact_sequences_passed": int(candidate_final_metrics["exact_sequences"])
        >= 7,
        "candidate_minus_ablation_cer_improvement": candidate_minus_ablation,
        "candidate_minus_ablation_cer_improvement_min": 0.1,
        "candidate_minus_ablation_passed": candidate_minus_ablation >= 0.1,
        "deterministic_checkpoint_replay_passed": checkpoint_replay_identical,
        "future_mutation_controls_passed": bool(future_mutation["passed"]),
        "resume_equivalence_passed": bool(prefix_resume["passed"]),
    }
    gate_passed = all(bool(value) for name, value in gates.items() if name.endswith("_passed"))
    runtime_before_report_write = time.perf_counter() - started_at
    peak_rss_bytes = _peak_rss_bytes()
    resource_gates = {
        "training_runs": training_run_count,
        "training_runs_max": selected_caps.max_training_runs,
        "training_runs_passed": training_run_count <= selected_caps.max_training_runs,
        "optimizer_steps": optimizer_steps,
        "optimizer_steps_max": selected_caps.max_optimizer_steps,
        "optimizer_steps_passed": optimizer_steps <= selected_caps.max_optimizer_steps,
        "runtime_before_report_write_sec": round(runtime_before_report_write, 6),
        "runtime_sec_max": selected_caps.max_runtime_sec,
        "runtime_passed": runtime_before_report_write <= selected_caps.max_runtime_sec,
        "peak_rss_bytes": peak_rss_bytes,
        "peak_rss_bytes_max": selected_caps.max_peak_rss_bytes,
        "peak_rss_passed": peak_rss_bytes <= selected_caps.max_peak_rss_bytes,
        "free_disk_before_bytes": free_disk_before,
        "minimum_free_disk_bytes": selected_caps.minimum_free_disk_bytes,
        "free_disk_passed": free_disk_before >= selected_caps.minimum_free_disk_bytes,
    }
    if not all(bool(value) for name, value in resource_gates.items() if name.endswith("_passed")):
        gate_passed = False

    report: dict[str, Any] = {
        "schema": {"name": RESULT_SCHEMA_NAME, "version": RESULT_SCHEMA_VERSION},
        "status": "passed" if gate_passed else "parked_gate_failed",
        "proof_posture": PROOF_POSTURE,
        "research_registry": {
            "path": str(registry_path),
            "sha256": _file_sha256(registry_path),
            "research_id": registry["research_id"],
        },
        "fixture": fixture_summary,
        "candidate": {
            "model_id": CANDIDATE_MODEL_ID,
            "parameter_count": selected_training.parameter_count,
            "required_left_context_frames": 47,
            "required_left_context_ms": 470,
            "right_context_frames": 0,
            "output_sampling_rate_hz": 25,
            "selected_recipe_id": selected_recipe_id,
            "selection_metrics": next(
                row["selection_metrics"]
                for row in candidate_runs
                if row["config"]["recipe_id"] == selected_recipe_id
            ),
            "final_metrics": candidate_final_metrics,
            "candidate_runs": candidate_runs,
            "checkpoint": _public_checkpoint_summary(candidate_checkpoint),
        },
        "ablation": {
            "model_id": ABLATION_MODEL_ID,
            "parameter_count": ablation_training.parameter_count,
            "required_left_context_frames": 0,
            "right_context_frames": 0,
            "output_sampling_rate_hz": 25,
            "recipe_id": selected_recipe_id,
            "final_metrics": ablation_final_metrics,
            "training": _training_summary_without_history(ablation_training),
            "checkpoint": _public_checkpoint_summary(ablation_checkpoint),
        },
        "mechanics": {
            "candidate_checkpoint_replay": checkpoint_replay_identical,
            "future_mutation": future_mutation,
            "prefix_resume": prefix_resume,
            "candidate_final_prediction_sha256": _sha256_json(candidate_final["predictions"]),
            "ablation_final_prediction_sha256": _sha256_json(ablation_final["predictions"]),
            "plaintext_targets_or_predictions_emitted": False,
        },
        "gates": gates,
        "gate_passed": gate_passed,
        "resources": {
            "caps": selected_caps.to_dict(),
            "measurements": resource_gates,
            "fixture_input_array_bytes": fixture_summary["array_bytes"],
            "generated_artifact_bytes": 0,
            "generated_artifact_cap_bytes": selected_caps.max_generated_artifact_bytes,
            "generated_artifact_bytes_passed": False,
            "thread_environment": thread_environment,
        },
        "operation_counters": {
            "research_registry_reads": 1,
            "synthetic_fixture_rows_generated": 40,
            "synthetic_train_rows_used": 24,
            "synthetic_selection_rows_used": 8,
            "synthetic_final_rows_opened_once": 8,
            "training_runs": training_run_count,
            "parameter_updates": optimizer_steps,
            "model_inference_runs": model_inference_runs,
            "checkpoint_writes": 2,
            "checkpoint_reads": 1,
            "raw_data_reads": 0,
            "real_cache_stat_reads": 0,
            "real_cache_hash_passes": 0,
            "real_cache_member_reads": 0,
            "real_signal_rows_read": 0,
            "real_target_rows_read": 0,
            "downloads": 0,
            "download_bytes": 0,
            "s24_or_s25_operations": 0,
            "stream_device_hardware_or_rw3_operations": 0,
        },
        "access_events": access_events,
        "producer": {
            "causal": True,
            "upstream_real_cache_causality": "not_applicable_synthetic_fixture",
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            "synthetic_fixture_only",
            "synthetic_labels_define_motifs_and_are_not_real_neural_targets",
            "learned_stride4_features_are_not_anti_aliased_waveform_resampling",
            "no_real_signal_target_or_cache_was_opened",
            "synthetic_success_does_not_predict_real_data_benefit",
            "sensor_signal_dependence_and_brain_specific_origin_remain_unavailable",
            "end_to_end_latency_was_not_measured",
        ],
        "claim_boundary": {
            "engineering_capability": (
                "The exact causal temporal candidate, zero-context ablation, synthetic "
                "selection, checkpoint replay, causality, padding, and resource gate ran "
                "under the registered interface."
            ),
            "scientific_claim_not_established": (
                "No real signal or target was opened; neural advantage, sensor-signal "
                "dependence, brain-specific origin, real decoding improvement, "
                "generalization, real-time performance, and portable or home EEG "
                "performance remain unestablished."
            ),
        },
    }
    _write_stable_reports(report, output, selected_caps.max_generated_artifact_bytes)
    return load_stage_c_synthetic_result(output / "result.json")


def load_stage_c_synthetic_result(path: str | Path) -> dict[str, Any]:
    """Load and strictly validate one aggregate Stage C synthetic result."""

    result_path = Path(path)
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    if payload.get("schema") != {
        "name": RESULT_SCHEMA_NAME,
        "version": RESULT_SCHEMA_VERSION,
    }:
        raise ValueError("unsupported Stage C synthetic result schema")
    if payload.get("status") not in {"passed", "parked_gate_failed"}:
        raise ValueError("invalid Stage C synthetic result status")
    if payload.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("invalid Stage C synthetic proof posture")
    counters = payload.get("operation_counters") or {}
    for name in (
        "raw_data_reads",
        "real_cache_stat_reads",
        "real_cache_hash_passes",
        "real_cache_member_reads",
        "real_signal_rows_read",
        "real_target_rows_read",
        "downloads",
        "download_bytes",
        "s24_or_s25_operations",
        "stream_device_hardware_or_rw3_operations",
    ):
        if counters.get(name) != 0:
            raise ValueError(f"forbidden Stage C synthetic counter is nonzero: {name}")
    if payload.get("mechanics", {}).get("plaintext_targets_or_predictions_emitted") is not False:
        raise ValueError("Stage C result plaintext leakage boundary is invalid")
    return payload


def summarize_stage_c_synthetic_result(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact inspect surface used by the CLI."""

    return {
        "status": report["status"],
        "gate_passed": report["gate_passed"],
        "selected_recipe_id": report["candidate"]["selected_recipe_id"],
        "candidate_final_cer": report["candidate"]["final_metrics"]["macro_cer"],
        "candidate_final_exact_sequences": report["candidate"]["final_metrics"]["exact_sequences"],
        "ablation_final_cer": report["ablation"]["final_metrics"]["macro_cer"],
        "candidate_minus_ablation_cer_improvement": report["gates"][
            "candidate_minus_ablation_cer_improvement"
        ],
        "training_runs": report["operation_counters"]["training_runs"],
        "parameter_updates": report["operation_counters"]["parameter_updates"],
        "model_inference_runs": report["operation_counters"]["model_inference_runs"],
        "runtime_sec": report["resources"]["measurements"]["runtime_before_report_write_sec"],
        "peak_rss_bytes": report["resources"]["measurements"]["peak_rss_bytes"],
        "input_array_bytes": report["resources"]["fixture_input_array_bytes"],
        "generated_artifact_bytes": report["resources"]["generated_artifact_bytes"],
        "producer_causal": report["producer"]["causal"],
        "end_to_end_latency_measured": report["producer"]["end_to_end_latency_measured"],
        "warnings": list(report["warnings"]),
        "scientific_claim_not_established": report["claim_boundary"][
            "scientific_claim_not_established"
        ],
    }


def _future_mutation_check(model, partition, baseline: Mapping[str, Any]) -> dict[str, Any]:
    np = _require_numpy()
    mutated = partition.signals.copy()
    cuts: list[int] = []
    for index, input_length in enumerate(partition.input_lengths.tolist()):
        output_length = (int(input_length) + 3) // 4
        cut_output = output_length // 2
        cut_source = cut_output * 4
        cuts.append(cut_output)
        future = mutated[index, :, cut_source + 1 : int(input_length)]
        future *= -1.75
        future += 0.125
        mutated[index, :, int(input_length) :] = 0.0
    prediction = predict_tiny_causal_temporal_ctc(
        model,
        signals=mutated,
        input_lengths=partition.input_lengths,
        include_logits=True,
    )
    rows = []
    for baseline_logits, mutated_logits, cut in zip(
        baseline["logits"],
        prediction["logits"],
        cuts,
        strict=True,
    ):
        rows.append(bool(np.array_equal(baseline_logits[: cut + 1], mutated_logits[: cut + 1])))
    return {
        "passed": all(rows),
        "rows_checked": len(rows),
        "rows_passed": sum(rows),
        "model_inference_runs": 1,
    }


def _prefix_resume_check(model, partition, baseline: Mapping[str, Any]) -> dict[str, Any]:
    np = _require_numpy()
    prefixes = np.zeros_like(partition.signals)
    prefix_lengths = np.empty_like(partition.input_lengths)
    cuts: list[int] = []
    for index, input_length in enumerate(partition.input_lengths.tolist()):
        output_length = (int(input_length) + 3) // 4
        cut_output = output_length // 2
        prefix_length = cut_output * 4 + 1
        cuts.append(cut_output)
        prefix_lengths[index] = prefix_length
        prefixes[index, :, :prefix_length] = partition.signals[index, :, :prefix_length]
    prediction = predict_tiny_causal_temporal_ctc(
        model,
        signals=prefixes,
        input_lengths=prefix_lengths,
        include_logits=True,
    )
    rows = []
    for baseline_logits, prefix_logits, cut in zip(
        baseline["logits"],
        prediction["logits"],
        cuts,
        strict=True,
    ):
        rows.append(bool(np.array_equal(baseline_logits[: cut + 1], prefix_logits)))
    return {
        "passed": all(rows),
        "rows_checked": len(rows),
        "rows_passed": sum(rows),
        "model_inference_runs": 1,
    }


def _prediction_reports_bitwise_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    np = _require_numpy()
    if left["predictions"] != right["predictions"]:
        return False
    if left["token_rows"] != right["token_rows"]:
        return False
    if left["output_lengths"] != right["output_lengths"]:
        return False
    return all(
        np.array_equal(left_row, right_row)
        for left_row, right_row in zip(left["logits"], right["logits"], strict=True)
    )


def _score_predictions(targets, predictions) -> dict[str, Any]:
    if len(targets) != len(predictions) or not targets:
        raise ValueError("Stage C targets and predictions must have the same nonzero length")
    row_cers = [
        character_error_rate(target, prediction, normalize=False)
        for target, prediction in zip(targets, predictions, strict=True)
    ]
    exact = [target == prediction for target, prediction in zip(targets, predictions, strict=True)]
    return {
        "rows": len(targets),
        "macro_cer": sum(row_cers) / len(row_cers),
        "exact_sequences": sum(exact),
        "exact_fraction": sum(exact) / len(exact),
        "row_cer_sha256": _sha256_json(row_cers),
    }


def _training_summary_without_history(training) -> dict[str, Any]:
    summary = training.summary()
    summary.pop("loss_history")
    summary["final_loss"] = float(training.loss_history[-1])
    return summary


def _public_checkpoint_summary(checkpoint: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": checkpoint["path"],
        "bytes": checkpoint["bytes"],
        "sha256": checkpoint["sha256"],
        "parameter_payload_sha256": checkpoint["parameter_payload_sha256"],
        "serialization": "numpy_npz_allow_pickle_false",
    }


def _write_stable_reports(report: dict[str, Any], output: Path, cap: int) -> None:
    json_path = output / "result.json"
    markdown_path = output / "result.md"
    checkpoint_bytes = _directory_bytes(output)
    for _ in range(8):
        json_bytes = _json_bytes(report)
        markdown_bytes = _markdown_bytes(report)
        total = checkpoint_bytes + len(json_bytes) + len(markdown_bytes)
        previous = report["resources"]["generated_artifact_bytes"]
        report["resources"]["generated_artifact_bytes"] = total
        report["resources"]["generated_artifact_bytes_passed"] = total <= cap
        if total == previous:
            break
    json_bytes = _json_bytes(report)
    markdown_bytes = _markdown_bytes(report)
    total = checkpoint_bytes + len(json_bytes) + len(markdown_bytes)
    if total > cap:
        raise RuntimeError("Stage C synthetic artifacts exceed the 16 MiB cap")
    json_path.write_bytes(json_bytes)
    markdown_path.write_bytes(markdown_bytes)
    _require_artifact_cap(output, cap)


def _json_bytes(report: Mapping[str, Any]) -> bytes:
    return (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _markdown_bytes(report: Mapping[str, Any]) -> bytes:
    candidate = report["candidate"]["final_metrics"]
    ablation = report["ablation"]["final_metrics"]
    resources = report["resources"]
    lines = [
        "# Loop 48 Stage C Synthetic Temporal-Representation Result",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- candidate CER / exact: `{candidate['macro_cer']:.6f}` / "
        f"`{candidate['exact_sequences']}/8`",
        f"- ablation CER / exact: `{ablation['macro_cer']:.6f}` / "
        f"`{ablation['exact_sequences']}/8`",
        "- candidate minus ablation CER improvement: "
        f"`{report['gates']['candidate_minus_ablation_cer_improvement']:.6f}`",
        f"- selected recipe: `{report['candidate']['selected_recipe_id']}`",
        f"- training runs / updates: `{report['operation_counters']['training_runs']}` / "
        f"`{report['operation_counters']['parameter_updates']}`",
        f"- runtime before report write: "
        f"`{resources['measurements']['runtime_before_report_write_sec']:.6f}` sec",
        f"- peak RSS: `{resources['measurements']['peak_rss_bytes']}` bytes",
        f"- fixture arrays / generated output: `{resources['fixture_input_array_bytes']}` / "
        f"`{resources['generated_artifact_bytes']}` bytes",
        "- raw-data reads / real-cache reads / downloads: `0 / 0 / 0`",
        "- producer causal: `true`; end-to-end latency measured: `false`",
        "",
        "Engineering capability added: " + report["claim_boundary"]["engineering_capability"],
        "",
        "Scientific claim not established: "
        + report["claim_boundary"]["scientific_claim_not_established"],
        "",
        "Warnings: " + ", ".join(report["warnings"]),
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _load_and_validate_research_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_name") != (
        "neurodecodekit.loop48_stage_c_representation_repair_research"
    ):
        raise ValueError("Stage C research registry schema is invalid")
    if payload.get("schema_version") != "0.1.0":
        raise ValueError("Stage C research registry version is invalid")
    if payload.get("status") != (
        "planning_research_complete_synthetic_calibration_not_started_"
        "protected_execution_unauthorized"
    ):
        raise ValueError("Stage C research status is not the frozen pre-implementation state")
    plan = payload.get("synthetic_calibration_plan") or {}
    if plan.get("fixture_seed") != 4850 or plan.get("partitions") != {
        "train": 24,
        "selection": 8,
        "final": 8,
    }:
        raise ValueError("Stage C synthetic plan identity drifted")
    if plan.get("total_parameter_update_runs") != 4:
        raise ValueError("Stage C training-run count drifted")
    if (
        payload.get("authorization", {}).get("protected_stage_c_execution_authorized_now")
        is not False
    ):
        raise ValueError("Stage C protected authorization boundary expanded")
    return payload


def _prepare_output_directory(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"Refusing to reuse nonempty Stage C output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def _validate_caps(caps: StageCSyntheticCaps) -> None:
    if caps.cpu_threads != 1 or caps.workers != 1:
        raise ValueError("Stage C synthetic gate requires one thread and one worker")
    if caps.max_training_runs != 4 or caps.max_optimizer_steps != 1800:
        raise ValueError("Stage C training caps must remain exactly 4 runs and 1,800 steps")
    if caps.max_runtime_sec > 600 or caps.max_peak_rss_bytes > 1024**3:
        raise ValueError("Stage C runtime or RSS cap exceeds the research boundary")
    if caps.max_generated_artifact_bytes > 16 * 1024**2:
        raise ValueError("Stage C generated-artifact cap exceeds 16 MiB")
    if caps.minimum_free_disk_bytes < 20 * 1024**3:
        raise ValueError("Stage C free-disk floor may not fall below 20 GiB")


def _require_single_thread_environment() -> dict[str, str]:
    values = {name: os.environ.get(name, "") for name in THREAD_ENV_VARS}
    invalid = {name: value for name, value in values.items() if value != "1"}
    if invalid:
        raise RuntimeError(f"Stage C requires all thread environment variables at 1: {invalid}")
    return values


def _require_artifact_cap(path: Path, cap: int) -> None:
    if _directory_bytes(path) > cap:
        raise RuntimeError("Stage C synthetic artifacts exceed the 16 MiB cap")


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _access_event(index: int, stage: str, split: str | None, action: str) -> dict[str, Any]:
    return {"index": index, "stage": stage, "split": split, "action": action}


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
        raise RuntimeError(
            "Stage C synthetic gate requires NumPy: `pip install -e '.[array]'`."
        ) from exc
    return np
