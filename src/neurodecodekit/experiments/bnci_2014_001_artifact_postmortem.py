"""Deterministic artifact-only postmortem for the consumed BNCI C3/C5 result."""

from __future__ import annotations

import hashlib
import json
import os
import resource
import stat
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

CONTRACT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_artifact_postmortem_contract.v0.json"
)
INPUT_RELATIVE_PATH = Path("registries/bnci_2014_001_stage_t_result.v0.json")
RESULT_RELATIVE_PATH = Path("registries/bnci_2014_001_artifact_postmortem_result.v0.json")
INPUT_BYTES = 4_951
INPUT_SHA256 = "e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2"
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_PLAINTEXT_KEYS = {
    "target",
    "targets",
    "label",
    "labels",
    "prediction",
    "predictions",
    "probability",
    "probabilities",
    "per_participant",
    "participant_outcomes",
}


class ArtifactPostmortemRefusal(RuntimeError):
    """Fail-closed refusal for an invalid artifact-only operation."""


def plan_postmortem() -> dict[str, Any]:
    """Return the bounded Tier A execution envelope."""

    return {
        "contract": CONTRACT_RELATIVE_PATH.as_posix(),
        "input": INPUT_RELATIVE_PATH.as_posix(),
        "input_bytes": INPUT_BYTES,
        "input_sha256": INPUT_SHA256,
        "output": RESULT_RELATIVE_PATH.as_posix(),
        "CPU_threads": 1,
        "workers": 1,
        "runtime_seconds_maximum": 30,
        "peak_RSS_bytes_maximum": 256 * 1024**2,
        "public_output_bytes_maximum": 1024**2,
        "private_or_ignored_reads": 0,
        "target_reads": 0,
        "model_runs": 0,
        "training_runs": 0,
        "inference_runs": 0,
        "network_calls": 0,
        "scientific_claim_upgrades": 0,
    }


def analyze_stage_t_aggregate(result: Mapping[str, Any]) -> dict[str, Any]:
    """Apply the frozen descriptive rules to one aggregate Stage T result."""

    _validate_stage_t_result(result)
    metrics = result["aggregate_metrics"]
    accuracy = metrics["participant_macro_balanced_accuracy"]
    loss = metrics["participant_macro_log_loss"]

    c3 = {
        "selected_E_balanced_accuracy": accuracy["selected_E"],
        "selected_E_minus_equal_prior_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["equal_prior_no_signal"]
        ),
        "selected_E_minus_timing_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["timing_only"]
        ),
        "selected_E_minus_posterior_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["posterior_EEG"]
        ),
        "selected_E_minus_central_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["central_EEG"]
        ),
        "selected_E_minus_frontal_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["frontal_EEG"]
        ),
        "selected_E_minus_early_cue_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["early_cue_EEG"]
        ),
        "selected_E_minus_pre_cue_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["pre_cue_EEG"]
        ),
        "selected_E_minus_trial_displacement_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["trial_displacement_EEG"]
        ),
        "selected_E_minus_channel_rotation_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["channel_rotation_EEG"]
        ),
        "selected_E_minus_source_label_rotation_EEG_balanced_accuracy": _difference(
            accuracy["selected_E"], accuracy["source_label_rotation_EEG"]
        ),
        "selected_E_minus_equal_prior_log_loss": _difference(
            loss["selected_E"], loss["equal_prior_no_signal"]
        ),
        "selected_E_minus_timing_log_loss": _difference(
            loss["selected_E"], loss["timing_only"]
        ),
        "posterior_EEG_minus_equal_prior_log_loss": _difference(
            loss["posterior_EEG"], loss["equal_prior_no_signal"]
        ),
        "positive_participant_margins": metrics["C3_positive_participant_margins"],
        "exact_one_sided_sign_flip_p": metrics["C3_exact_one_sided_sign_flip_p"],
    }
    c5 = {
        "EOG_only_balanced_accuracy": accuracy["P"],
        "EOG_plus_EEG_balanced_accuracy": accuracy["P_plus_E"],
        "EOG_plus_deranged_EEG_balanced_accuracy": accuracy["P_plus_D_E"],
        "P_plus_E_minus_P_balanced_accuracy": _difference(
            accuracy["P_plus_E"], accuracy["P"]
        ),
        "P_plus_E_minus_P_plus_D_E_balanced_accuracy": _difference(
            accuracy["P_plus_E"], accuracy["P_plus_D_E"]
        ),
        "P_minus_P_plus_E_log_loss": metrics["C5_macro_EOG_delta"],
        "P_plus_D_E_minus_P_plus_E_log_loss": metrics["C5_macro_deranged_delta"],
        "positive_EOG_deltas": metrics["C5_positive_EOG_deltas"],
        "positive_deranged_deltas": metrics["C5_positive_deranged_deltas"],
        "exact_EOG_delta_sign_flip_p": metrics["C5_exact_EOG_delta_sign_flip_p"],
        "exact_deranged_delta_sign_flip_p": metrics[
            "C5_exact_deranged_delta_sign_flip_p"
        ],
    }

    diagnostics = [
        {
            "id": "D1",
            "name": "aggregate_candidate_protocol_information",
            "state": (
                "supported_descriptively"
                if metrics["C3_components"]["macro_balanced_accuracy_at_least_0_35"]
                and metrics["C3_components"][
                    "macro_no_signal_timing_margin_at_least_0_08"
                ]
                else "not_supported"
            ),
        },
        {
            "id": "D2",
            "name": "posterior_visual_specificity",
            "state": (
                "failed_posterior_control_outperformed_selected_E"
                if c3["selected_E_minus_posterior_EEG_balanced_accuracy"] < 0.02
                else "passed"
            ),
        },
        {
            "id": "D3",
            "name": "probability_calibration_reliability",
            "state": (
                "failed_selected_E_log_loss_worse_than_equal_prior"
                if c3["selected_E_minus_equal_prior_log_loss"] >= 0.0
                else "supported"
            ),
        },
        {
            "id": "D4",
            "name": "incremental_EEG_beyond_recorded_EOG",
            "state": (
                "weak_directional_only_not_validated"
                if c5["P_minus_P_plus_E_log_loss"] > 0.0
                and c5["P_plus_D_E_minus_P_plus_E_log_loss"] > 0.0
                and not result["C5_partial_passed"]
                else "not_supported"
            ),
        },
        {
            "id": "D5",
            "name": "held_out_participant_consistency",
            "state": (
                "failed"
                if c3["positive_participant_margins"] < 8
                or c3["exact_one_sided_sign_flip_p"] > 0.05
                or c5["positive_EOG_deltas"] < 8
                or c5["positive_deranged_deltas"] < 8
                else "passed"
            ),
        },
        {
            "id": "D6",
            "name": "brain_specific_causal_origin",
            "state": "unavailable_from_aggregate_artifact",
        },
    ]
    return {
        "C3_failure_map": c3,
        "C5_failure_map": c5,
        "diagnostics": diagnostics,
        "replication_priority_order": [
            "separate_selected_EEG_from_posterior_visual_information",
            "estimate_EEG_increment_after_source_cross_fitted_EOG_residualization",
            "freeze_probability_calibration_on_source_participants_only",
            "test_consistency_in_a_fresh_independent_participant_cohort",
        ],
        "root_cause_established": False,
    }


def run_registered_postmortem(
    repo_root: str | Path,
    *,
    implementation_commit: str,
    ci_run_id: int,
    base_job_id: int,
    optional_job_id: int,
) -> dict[str, Any]:
    """Read the one exact aggregate input and publish one no-clobber report."""

    started = time.perf_counter()
    root = Path(repo_root).resolve()
    _validate_thread_environment()
    _validate_git_state(root, implementation_commit)
    if min(ci_run_id, base_job_id, optional_job_id) <= 0:
        raise ArtifactPostmortemRefusal("positive remotely green proof IDs are required")
    output_path = root / RESULT_RELATIVE_PATH
    if output_path.exists():
        raise ArtifactPostmortemRefusal("postmortem output already exists; rerun refused")

    raw = _strict_read(root / INPUT_RELATIVE_PATH, INPUT_BYTES, INPUT_SHA256)
    aggregate = json.loads(raw)
    _reject_plaintext_fields(aggregate)
    analysis = analyze_stage_t_aggregate(aggregate)
    runtime_seconds = time.perf_counter() - started
    peak_rss_bytes = _peak_rss_bytes()
    caps = plan_postmortem()
    if runtime_seconds > caps["runtime_seconds_maximum"]:
        raise ArtifactPostmortemRefusal("runtime cap exceeded")
    if peak_rss_bytes > caps["peak_RSS_bytes_maximum"]:
        raise ArtifactPostmortemRefusal("RSS cap exceeded")

    report: dict[str, Any] = {
        "schema_name": "neurodecodekit.bnci_2014_001_artifact_postmortem_result",
        "schema_version": "0.1.0",
        "status": "completed_artifact_only_descriptive_postmortem",
        "proof_posture": "post_outcome_descriptive_not_prospective_validation",
        "input_artifact": {
            "path": INPUT_RELATIVE_PATH.as_posix(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "verified": True,
        },
        "implementation_proof": {
            "commit": implementation_commit,
            "CI_run_id": ci_run_id,
            "base_job_id": base_job_id,
            "optional_job_id": optional_job_id,
            "operator_confirmed_remotely_green_before_execution": True,
        },
        "analysis": analysis,
        "access_counters": {
            "committed_aggregate_JSON_reads": 1,
            "committed_aggregate_bytes_read": len(raw),
            "git_ignored_or_private_artifact_reads": 0,
            "raw_MAT_or_EEG_reads": 0,
            "target_or_label_reads": 0,
            "individual_prediction_probability_or_participant_outcome_reads": 0,
            "model_or_checkpoint_reads": 0,
            "training_runs": 0,
            "inference_runs": 0,
            "network_calls": 0,
            "downloads": 0,
            "scientific_reruns": 0,
            "claim_upgrades": 0,
        },
        "measurements": {
            "runtime_seconds": round(runtime_seconds, 9),
            "peak_process_RSS_bytes": peak_rss_bytes,
            "public_output_bytes": 0,
            "end_to_end_live_decoding_latency_measured": False,
        },
        "resource_caps": {
            "CPU_threads": 1,
            "workers": 1,
            "runtime_seconds_maximum": 30,
            "peak_RSS_bytes_maximum": 256 * 1024**2,
            "public_output_bytes_maximum": 1024**2,
        },
        "warnings": [
            "post_outcome_descriptive_analysis_not_a_prospective_scientific_test",
            "aggregate_only_evidence_cannot_identify_a_causal_root_source",
            "consumed_private_predictions_targets_and_participant_outcomes_were_not_read",
            "no_model_training_inference_scoring_rerun_or_claim_upgrade",
        ],
        "claim_boundary": {
            "maximum_claim": "descriptive_failure_map_of_one_committed_aggregate_result",
            "not_established": (
                "fresh replication, unseen-person EEG decoding, EEG beyond EOG, "
                "brain-specific origin, movement intention, language decoding, live "
                "behavior, hardware performance, or clinical utility"
            ),
        },
    }
    payload = _stabilize_output_size(report)
    if len(payload) > 1024**2:
        raise ArtifactPostmortemRefusal("public output cap exceeded")
    _reject_plaintext_fields(report)
    _write_no_clobber(output_path, payload)
    return summarize_postmortem(report)


def inspect_postmortem(repo_root: str | Path) -> dict[str, Any]:
    """Validate and summarize the committed artifact-only report."""

    path = Path(repo_root).resolve() / RESULT_RELATIVE_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_name") != "neurodecodekit.bnci_2014_001_artifact_postmortem_result":
        raise ArtifactPostmortemRefusal("unexpected postmortem schema")
    _reject_plaintext_fields(payload)
    return summarize_postmortem(payload)


def summarize_postmortem(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact human-inspectable summary."""

    return {
        "status": report["status"],
        "diagnostics": report["analysis"]["diagnostics"],
        "replication_priority_order": report["analysis"]["replication_priority_order"],
        "root_cause_established": report["analysis"]["root_cause_established"],
        "measurements": report["measurements"],
        "warnings": report["warnings"],
        "claim_boundary": report["claim_boundary"],
    }


def _validate_stage_t_result(result: Mapping[str, Any]) -> None:
    expected = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_t_result",
        "schema_version": "0.1.0",
        "status": "scored_once_frozen_router_applied_consumed",
        "route": "BNCIC3C5-R2",
        "C3_passed": False,
        "C5_partial_passed": False,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ArtifactPostmortemRefusal(f"unexpected Stage T {key}")
    metrics = result.get("aggregate_metrics")
    if not isinstance(metrics, Mapping):
        raise ArtifactPostmortemRefusal("aggregate_metrics are required")
    required_accuracy = {
        "P",
        "P_plus_D_E",
        "P_plus_E",
        "central_EEG",
        "channel_rotation_EEG",
        "early_cue_EEG",
        "equal_prior_no_signal",
        "frontal_EEG",
        "posterior_EEG",
        "pre_cue_EEG",
        "selected_E",
        "source_label_rotation_EEG",
        "timing_only",
        "trial_displacement_EEG",
    }
    accuracy = metrics.get("participant_macro_balanced_accuracy")
    loss = metrics.get("participant_macro_log_loss")
    if not isinstance(accuracy, Mapping) or not required_accuracy.issubset(accuracy):
        raise ArtifactPostmortemRefusal("balanced-accuracy aggregate is incomplete")
    if not isinstance(loss, Mapping) or not {
        "selected_E",
        "posterior_EEG",
        "equal_prior_no_signal",
        "timing_only",
    }.issubset(loss):
        raise ArtifactPostmortemRefusal("log-loss aggregate is incomplete")


def _difference(left: Any, right: Any) -> float:
    return float(left) - float(right)


def _reject_plaintext_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in FORBIDDEN_PLAINTEXT_KEYS:
                raise ArtifactPostmortemRefusal(f"forbidden plaintext field: {key}")
            _reject_plaintext_fields(child)
    elif isinstance(value, list):
        for child in value:
            _reject_plaintext_fields(child)


def _strict_read(path: Path, expected_bytes: int, expected_sha256: str) -> bytes:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise ArtifactPostmortemRefusal("input must be a no-follow regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        raw = os.read(descriptor, expected_bytes + 1)
    finally:
        os.close(descriptor)
    if len(raw) != expected_bytes:
        raise ArtifactPostmortemRefusal("input byte count mismatch")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ArtifactPostmortemRefusal("input SHA-256 mismatch")
    return raw


def _validate_thread_environment() -> None:
    mismatches = {
        name: os.environ.get(name)
        for name, expected in THREAD_ENVIRONMENT.items()
        if os.environ.get(name) != expected
    }
    if mismatches:
        raise ArtifactPostmortemRefusal(f"single-thread environment mismatch: {mismatches}")


def _validate_git_state(root: Path, implementation_commit: str) -> None:
    if len(implementation_commit) != 40 or any(
        character not in "0123456789abcdef" for character in implementation_commit
    ):
        raise ArtifactPostmortemRefusal("implementation commit must be a full SHA")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != implementation_commit:
        raise ArtifactPostmortemRefusal("implementation commit must equal HEAD")
    diff = subprocess.run(
        ["git", "diff", "--quiet", "--ignore-submodules", "HEAD"],
        cwd=root,
        check=False,
    )
    if diff.returncode != 0:
        raise ArtifactPostmortemRefusal("tracked worktree changes exist")


def _stabilize_output_size(report: dict[str, Any]) -> bytes:
    for _ in range(8):
        payload = _canonical_json(report)
        if report["measurements"]["public_output_bytes"] == len(payload):
            return payload
        report["measurements"]["public_output_bytes"] = len(payload)
    raise ArtifactPostmortemRefusal("could not stabilize output byte count")


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_no_clobber(path: Path, payload: bytes) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o644)
    try:
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _peak_rss_bytes() -> int:
    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024
