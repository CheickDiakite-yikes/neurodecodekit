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
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

CONTRACT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_artifact_postmortem_contract.v0.json"
)
INPUT_RELATIVE_PATH = Path("registries/bnci_2014_001_stage_t_result.v0.json")
RESULT_RELATIVE_PATH = Path("registries/bnci_2014_001_artifact_postmortem_result.v0.json")
INPUT_BYTES = 4_951
INPUT_SHA256 = "e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2"
CONTRACT_BYTES = 4_506
CONTRACT_SHA256 = "c18facc3cb1c02147d3eaf53f0e3e3df49153fdaab1d0d1ba5f490e0ad74477e"
IMPLEMENTATION_ARTIFACTS = (
    "docs/BNCI_2014_001_ARTIFACT_POSTMORTEM_PROTOCOL.md",
    "registries/bnci_2014_001_artifact_postmortem_contract.v0.json",
    "src/neurodecodekit/bnci_c3c5_postmortem_cli.py",
    "src/neurodecodekit/experiments/bnci_2014_001_artifact_postmortem.py",
    "tests/test_bnci_2014_001_artifact_postmortem.py",
)
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
        "contract_bytes": CONTRACT_BYTES,
        "contract_sha256": CONTRACT_SHA256,
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
        "analysis_network_calls": 0,
        "pre_analysis_control_plane_network": "Git_remote_and_GitHub_Actions_metadata_only",
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
    remote_proof_collector: Callable[[Path], Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Read the one exact aggregate input and publish one no-clobber report."""

    started = time.perf_counter()
    root = Path(repo_root).resolve()
    _validate_thread_environment()
    head = _validate_git_state(root)
    output_path = root / RESULT_RELATIVE_PATH
    if output_path.exists():
        raise ArtifactPostmortemRefusal("postmortem output already exists; rerun refused")

    contract_raw = _strict_read(
        root / CONTRACT_RELATIVE_PATH,
        CONTRACT_BYTES,
        CONTRACT_SHA256,
    )
    contract = json.loads(contract_raw)
    _validate_contract(contract)
    implementation_artifacts = _implementation_artifact_identities(root)
    implementation_artifact_set_sha256 = hashlib.sha256(
        _canonical_json(implementation_artifacts)
    ).hexdigest()
    remote_proof = _collect_remote_green_proof(
        root,
        head=head,
        collector=remote_proof_collector,
    )
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
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "bytes": len(contract_raw),
            "sha256": hashlib.sha256(contract_raw).hexdigest(),
            "verified": True,
        },
        "input_artifact": {
            "path": INPUT_RELATIVE_PATH.as_posix(),
            "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "verified": True,
        },
        "implementation_proof": {
            "remote_green": remote_proof,
            "artifacts": implementation_artifacts,
            "artifact_set_sha256": implementation_artifact_set_sha256,
            "fresh_remote_proof_collected_before_analytical_input": True,
        },
        "analysis": analysis,
        "access_counters": {
            "committed_aggregate_JSON_reads": 1,
            "committed_aggregate_bytes_read": len(raw),
            "governance_JSON_reads": 1,
            "tracked_implementation_artifact_reads": len(implementation_artifacts),
            "git_ignored_or_private_artifact_reads": 0,
            "raw_MAT_or_EEG_reads": 0,
            "target_or_label_reads": 0,
            "individual_prediction_probability_or_participant_outcome_reads": 0,
            "model_or_checkpoint_reads": 0,
            "training_runs": 0,
            "inference_runs": 0,
            "analysis_network_calls": 0,
            "pre_analysis_Git_remote_metadata_calls": 1,
            "pre_analysis_GitHub_Actions_metadata_calls": 2,
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


def _validate_contract(contract: Mapping[str, Any]) -> None:
    expected = {
        "schema_name": "neurodecodekit.bnci_2014_001_artifact_postmortem_contract",
        "schema_version": "0.1.0",
        "contract_id": "BNCI-C3C5-PM1",
        "status": "tier_a_post_outcome_artifact_only_protocol_frozen",
    }
    for key, value in expected.items():
        if contract.get(key) != value:
            raise ArtifactPostmortemRefusal(f"unexpected postmortem contract {key}")
    source = contract.get("input_artifact")
    if not isinstance(source, Mapping) or source.get("path") != INPUT_RELATIVE_PATH.as_posix():
        raise ArtifactPostmortemRefusal("contract input path differs")
    if source.get("bytes") != INPUT_BYTES or source.get("sha256") != INPUT_SHA256:
        raise ArtifactPostmortemRefusal("contract input identity differs")
    caps = contract.get("resource_caps")
    if caps != {
        "CPU_threads": 1,
        "workers": 1,
        "runtime_seconds_maximum": 30,
        "peak_RSS_bytes_maximum": 256 * 1024**2,
        "public_output_bytes_maximum": 1024**2,
    }:
        raise ArtifactPostmortemRefusal("contract resource caps differ")
    forbidden = contract.get("forbidden_operations")
    if not isinstance(forbidden, Mapping) or not forbidden or any(forbidden.values()):
        raise ArtifactPostmortemRefusal("contract forbidden-operation counters differ")


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
    raw = _read_regular_file(path, expected_bytes + 1)
    if len(raw) != expected_bytes:
        raise ArtifactPostmortemRefusal("input byte count mismatch")
    if hashlib.sha256(raw).hexdigest() != expected_sha256:
        raise ArtifactPostmortemRefusal("input SHA-256 mismatch")
    return raw


def _read_regular_file(path: Path, byte_limit: int) -> bytes:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or path.is_symlink():
        raise ArtifactPostmortemRefusal("input must be a no-follow regular file")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        chunks: list[bytes] = []
        total = 0
        while total < byte_limit:
            chunk = os.read(descriptor, min(64 * 1024, byte_limit - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
    finally:
        os.close(descriptor)
    return b"".join(chunks)


def _validate_thread_environment() -> None:
    mismatches = {
        name: os.environ.get(name)
        for name, expected in THREAD_ENVIRONMENT.items()
        if os.environ.get(name) != expected
    }
    if mismatches:
        raise ArtifactPostmortemRefusal(f"single-thread environment mismatch: {mismatches}")


def _validate_git_state(root: Path) -> str:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise ArtifactPostmortemRefusal("HEAD must be a full commit SHA")
    diff = subprocess.run(
        ["git", "diff", "--quiet", "--ignore-submodules", "HEAD"],
        cwd=root,
        check=False,
    )
    if diff.returncode != 0:
        raise ArtifactPostmortemRefusal("tracked worktree changes exist")
    return head


def _collect_remote_green_proof(
    root: Path,
    *,
    head: str,
    collector: Callable[[Path], Mapping[str, Any]] | None,
) -> dict[str, Any]:
    if collector is None:
        from neurodecodekit.datasets.bnci_2014_001_stage_q_live import (
            collect_remote_green_proof,
        )

        collector = collect_remote_green_proof
    try:
        proof = dict(collector(root))
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as exc:
        raise ArtifactPostmortemRefusal("fresh remote-green proof failed") from exc
    if (
        proof.get("head_sha") != head
        or proof.get("remote_head_sha") != head
        or proof.get("CI_head_sha") != head
        or proof.get("CI_conclusion") != "success"
        or proof.get("base_python_job_name") != "Base Python"
        or proof.get("base_python_job_conclusion") != "success"
        or proof.get("optional_neuro_readers_job_name") != "Optional Neuro Readers"
        or proof.get("optional_neuro_readers_job_conclusion") != "success"
        or not all(
            isinstance(proof.get(key), int) and proof[key] > 0
            for key in (
                "CI_run_id",
                "base_python_job_id",
                "optional_neuro_readers_job_id",
            )
        )
    ):
        raise ArtifactPostmortemRefusal("fresh remote-green proof differs")
    return proof


def _implementation_artifact_identities(root: Path) -> list[dict[str, Any]]:
    identities = []
    for relative in IMPLEMENTATION_ARTIFACTS:
        raw = _read_regular_file(root / relative, 2 * 1024**2)
        if not raw or len(raw) >= 2 * 1024**2:
            raise ArtifactPostmortemRefusal(f"implementation artifact size differs: {relative}")
        identities.append(
            {
                "path": relative,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return identities


def _stabilize_output_size(report: dict[str, Any]) -> bytes:
    for _ in range(8):
        payload = _canonical_json(report)
        if report["measurements"]["public_output_bytes"] == len(payload):
            return payload
        report["measurements"]["public_output_bytes"] = len(payload)
    raise ArtifactPostmortemRefusal("could not stabilize output byte count")


def _canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _write_no_clobber(
    path: Path,
    payload: bytes,
    *,
    writer: Callable[[int, memoryview], int] = os.write,
) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor: int | None = None
    created = False
    try:
        descriptor = os.open(path, flags, 0o644)
        created = True
        view = memoryview(payload)
        while view:
            written = writer(descriptor, view)
            if written <= 0:
                raise ArtifactPostmortemRefusal("output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
            descriptor = None
        if created:
            path.unlink(missing_ok=True)
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
    try:
        _strict_read(path, len(payload), hashlib.sha256(payload).hexdigest())
    except Exception:
        path.unlink(missing_ok=True)
        raise


def _peak_rss_bytes() -> int:
    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024
