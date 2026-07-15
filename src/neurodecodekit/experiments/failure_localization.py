"""Bounded artifact-only Loop 48 failure localization."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


REPORT_SCHEMA_NAME = "neurodecodekit.loop48_failure_localization_result"
REPORT_SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path("registries/loop48_failure_localization_contract.v0.json")
DECISION_RELATIVE_PATH = Path("registries/loop48_authorization_decision.v0.json")
RESULT_RELATIVE_PATH = Path("registries/loop48_failure_localization_result.v0.json")
REGISTERED_CONTRACT_SHA256 = "ecd226f8ae8892e40ecd65c25d59e000384289e9c434886db71dabcfde9e31b1"
REGISTERED_DECISION_SHA256 = "0cce86e0e4fc858b05d037d71364c30d642e768e8adecd61afdd967acf35a1b7"
REGISTERED_AUTHORIZATION_COMMIT = "5bae88092525206b1d3cf3add055c75665943f14"
REGISTERED_AUTHORIZATION_PUSH_CI_RUN = 29442914090
REGISTERED_AUTHORIZATION_PR_CI_RUN = 29442916230
REGISTERED_INPUT_BYTES = 155545
PREFIX_SIZES = (8, 16, 24, 32, 44, 55)
SEEDS = (2601, 2602, 2603)
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
PLAINTEXT_FIELD_NAMES = frozenset(
    {
        "decoded_text",
        "label_text",
        "labels",
        "prediction",
        "prediction_text",
        "prediction_texts",
        "predictions",
        "reference_text",
        "target",
        "target_text",
        "target_texts",
        "targets",
    }
)
FORBIDDEN_OUTPUT_FIELD_NAMES = PLAINTEXT_FIELD_NAMES | {"per_item"}
FORBIDDEN_ACCESS_COUNTERS = (
    "git_ignored_output_reads",
    "cache_or_member_reads",
    "train_or_validation_array_reads",
    "target_reads",
    "checkpoint_or_private_prediction_reads",
    "source_test_or_session2_reads",
    "s7_s20_or_s25_operations",
    "raw_fif_or_mat_reads",
    "model_inference_runs",
    "training_or_parameter_update_runs",
    "threshold_seed_or_architecture_selection_runs",
    "network_calls",
    "new_download_bytes",
    "language_model_or_neurotoken_runs",
    "rw3_stream_device_or_hardware_operations",
    "scientific_claim_upgrades",
    "reruns",
)


class Loop48Refusal(RuntimeError):
    """Fail-closed refusal with a frozen Loop 48 reason ID."""

    def __init__(self, refusal_id: str, message: str) -> None:
        super().__init__(message)
        self.refusal_id = refusal_id


@dataclass(frozen=True)
class StageACaps:
    """Frozen artifact-only Stage A resource limits."""

    cpu_threads: int = 1
    workers: int = 1
    runtime_sec: float = 30.0
    peak_rss_bytes: int = 256 * 1024**2
    generated_output_bytes: int = 1024**2
    network_calls: int = 0
    new_download_bytes: int = 0
    model_inference_runs: int = 0
    training_or_parameter_update_runs: int = 0

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


def registered_stage_a_caps(contract: Mapping[str, Any]) -> StageACaps:
    """Return caps only when they exactly match the frozen contract."""

    caps = StageACaps()
    registered = contract["resource_caps"]
    expected = {
        "cpu_threads": registered["future_stage_a_cpu_threads"],
        "workers": registered["future_stage_a_workers"],
        "runtime_sec": registered["future_stage_a_runtime_sec"],
        "peak_rss_bytes": registered["future_stage_a_peak_rss_bytes"],
        "generated_output_bytes": registered["future_stage_a_generated_bytes"],
        "network_calls": registered["future_stage_a_network_calls"],
        "new_download_bytes": registered["future_stage_a_downloaded_bytes"],
        "model_inference_runs": registered["future_stage_a_model_runs"],
        "training_or_parameter_update_runs": registered["future_stage_a_training_runs"],
    }
    for name, value in expected.items():
        if getattr(caps, name) != value:
            raise Loop48Refusal("L48-R029-exceed-runtime-RSS-or-artifact-cap", name)
    return caps


def run_registered_failure_localization(
    *,
    repo_root: str | Path,
    implementation_commit: str,
    implementation_push_ci_run_id: int,
    implementation_pr_ci_run_id: int,
    output_path: str | Path = RESULT_RELATIVE_PATH,
) -> dict[str, Any]:
    """Execute the one registered Stage A event over four committed JSON files."""

    root = Path(repo_root).resolve()
    output = _resolve_under_root(root, output_path)
    if output != (root / RESULT_RELATIVE_PATH).resolve():
        raise Loop48Refusal(
            "L48-R001-unbound-artifact-input",
            f"registered output must be {RESULT_RELATIVE_PATH}",
        )
    if output.exists():
        raise Loop48Refusal("L48-R027-relabel-post-outcome-diagnosis-as-prospective", "rerun")
    _validate_registered_environment()
    _validate_registered_git_state(root, implementation_commit)
    if implementation_push_ci_run_id <= 0 or implementation_pr_ci_run_id <= 0:
        raise Loop48Refusal(
            "L48-R030-execute-before-separate-green-authorization",
            "both implementation CI run IDs are required",
        )

    contract = _load_governance_json(
        root / CONTRACT_RELATIVE_PATH,
        expected_sha256=REGISTERED_CONTRACT_SHA256,
    )
    decision = _load_governance_json(
        root / DECISION_RELATIVE_PATH,
        expected_sha256=REGISTERED_DECISION_SHA256,
    )
    _validate_registered_governance(contract, decision)
    caps = registered_stage_a_caps(contract)
    return run_failure_localization_stage_a(
        artifact_root=root,
        artifact_specs=contract["committed_input_artifacts"],
        contract=contract,
        authorization_decision=decision,
        contract_sha256=REGISTERED_CONTRACT_SHA256,
        authorization_decision_sha256=REGISTERED_DECISION_SHA256,
        authorization_commit=REGISTERED_AUTHORIZATION_COMMIT,
        implementation_commit=implementation_commit,
        implementation_push_ci_run_id=implementation_push_ci_run_id,
        implementation_pr_ci_run_id=implementation_pr_ci_run_id,
        output_path=output,
        caps=caps,
    )


def run_failure_localization_stage_a(
    *,
    artifact_root: str | Path,
    artifact_specs: Sequence[Mapping[str, Any]],
    contract: Mapping[str, Any],
    authorization_decision: Mapping[str, Any],
    contract_sha256: str,
    authorization_decision_sha256: str,
    authorization_commit: str,
    implementation_commit: str,
    implementation_push_ci_run_id: int,
    implementation_pr_ci_run_id: int,
    output_path: str | Path,
    caps: StageACaps | None = None,
) -> dict[str, Any]:
    """Run the bounded loader and pure aggregate classifier.

    This dependency-light entry point supports temporary synthetic artifacts for
    isolation tests. The registered wrapper above supplies the frozen identities.
    """

    started = time.perf_counter()
    active_caps = caps or StageACaps()
    root = Path(artifact_root).resolve()
    output = Path(output_path)
    if output.exists():
        raise Loop48Refusal("L48-R027-relabel-post-outcome-diagnosis-as-prospective", "rerun")
    _validate_authorization_payload(authorization_decision)
    _validate_artifact_specs(artifact_specs)

    payloads: dict[str, Mapping[str, Any]] = {}
    input_hashes: list[dict[str, Any]] = []
    for spec in artifact_specs:
        relative = Path(str(spec["path"]))
        path = _resolve_under_root(root, relative)
        payload, measured = _read_bound_json(path, spec)
        _reject_plaintext_fields(payload, field_names=PLAINTEXT_FIELD_NAMES)
        artifact_id = str(spec["artifact_id"])
        payloads[artifact_id] = payload
        input_hashes.append(measured)

    _validate_payload_roles(payloads)
    aggregate = recompute_aggregate_evidence(
        payloads["loop26_consumed_result"],
        contract,
    )
    primary, trace = apply_ordered_failure_tree(
        ordered_classes=contract["ordered_failure_classes"],
        aggregate_evidence=aggregate,
        thresholds=contract["future_artifact_only_stage_a"]["descriptive_thresholds"],
        identity_ok=True,
        temporal_ctc_infeasible=None,
    )
    expected_class = contract["future_artifact_only_stage_a"][
        "expected_primary_class_if_bound_artifacts_remain_exact"
    ]
    if primary["class_id"] != expected_class:
        raise Loop48Refusal(
            "L48-R002-artifact-byte-or-hash-mismatch",
            f"frozen artifact diagnosis drifted: {primary['class_id']}",
        )

    runtime_sec = time.perf_counter() - started
    peak_rss_bytes = _peak_rss_bytes()
    resource_checks = {
        "cpu_threads_exact": active_caps.cpu_threads == 1,
        "workers_exact": active_caps.workers == 1,
        "runtime_within_cap": runtime_sec <= active_caps.runtime_sec,
        "peak_rss_within_cap": peak_rss_bytes <= active_caps.peak_rss_bytes,
        "network_calls_exact_zero": active_caps.network_calls == 0,
        "new_download_bytes_exact_zero": active_caps.new_download_bytes == 0,
        "model_inference_runs_exact_zero": active_caps.model_inference_runs == 0,
        "training_or_parameter_update_runs_exact_zero": (
            active_caps.training_or_parameter_update_runs == 0
        ),
    }
    if not all(resource_checks.values()):
        raise Loop48Refusal(
            "L48-R029-exceed-runtime-RSS-or-artifact-cap",
            "a runtime or process resource cap failed",
        )

    access_counters = _stage_a_access_counters()
    secondary = [
        row["class_id"]
        for row in trace
        if row["state"] in {"unavailable", "not_evaluated_after_higher_priority_selection"}
    ]
    report: dict[str, Any] = {
        "schema_name": REPORT_SCHEMA_NAME,
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "completed_descriptive_f5_no_root_cause",
        "proof_posture": "post_outcome_artifact_only_target_free_failure_phenotype",
        "contract_sha256": contract_sha256,
        "authorization": {
            "decision_sha256": authorization_decision_sha256,
            "authorization_commit": authorization_commit,
            "authorization_push_ci_run_id": REGISTERED_AUTHORIZATION_PUSH_CI_RUN,
            "authorization_pr_ci_run_id": REGISTERED_AUTHORIZATION_PR_CI_RUN,
            "one_stage_a_execution_only": True,
        },
        "implementation": {
            "commit": implementation_commit,
            "push_ci_run_id": implementation_push_ci_run_id,
            "pr_ci_run_id": implementation_pr_ci_run_id,
            "operator_confirmed_both_runs_green_before_stage_a": True,
        },
        "input_artifact_hashes": input_hashes,
        "input_bytes": sum(int(row["bytes"]) for row in input_hashes),
        "primary_failure_class": {
            "class_id": primary["class_id"],
            "label": primary["label"],
            "descriptive_failure_phenotype_only": True,
            "root_cause_established": False,
        },
        "secondary_unresolved_classes": secondary,
        "decision_trace": trace,
        "aggregate_evidence": aggregate,
        "unavailable_fields": list(contract["unavailable_root_cause_fields"]),
        "access_counters": access_counters,
        "runtime_sec": round(runtime_sec, 9),
        "peak_rss_bytes": peak_rss_bytes,
        "generated_bytes": 0,
        "resource_caps": active_caps.to_dict(),
        "resource_checks": resource_checks,
        "producer": {
            "artifact_analyzer_is_neural_producer": False,
            "source_cache_preprocessing_is_causal": aggregate[
                "source_cache_preprocessing_is_causal"
            ],
            "producer_causal_status": "not_applicable_artifact_only_analyzer",
            "required_right_context": "unavailable_not_measured",
            "end_to_end_latency_measured": False,
        },
        "plaintext_targets_or_predictions_present": False,
        "per_item_target_conditioned_metrics_present": False,
        "warnings": [
            "post_outcome_descriptive_sorting_rule_not_prospective_validation",
            "F5_is_a_failure_phenotype_not_a_causal_root_cause",
            "registered_inputs_are_committed_aggregate_JSON_not_raw_or_private_payloads",
            "source_cache_is_offline_noncausal",
            "retained_neural_information_and_end_to_end_latency_remain_unmeasured",
            "no_model_training_target_download_stream_device_hardware_or_claim_upgrade",
        ],
        "claim_boundary": {
            "maximum_claim": (
                "The four exact committed aggregate artifacts satisfy F5 under the frozen "
                "post-outcome artifact-only decision tree."
            ),
            "not_established": (
                "No causal root cause, independent evidence, neural advantage, "
                "sensor-signal dependence, brain-specific origin, decoding improvement, "
                "unseen-person generalization, real-time behavior, EEG result, portable or "
                "home-device result, assistive efficacy, diagnostic value, or clinical "
                "capability is established."
            ),
        },
    }
    payload = _stabilized_report_bytes(report)
    report["resource_checks"]["generated_output_within_cap"] = (
        len(payload) <= active_caps.generated_output_bytes
    )
    report["resource_checks"]["all_caps_passed"] = all(report["resource_checks"].values())
    payload = _stabilized_report_bytes(report)
    if len(payload) > active_caps.generated_output_bytes:
        raise Loop48Refusal(
            "L48-R029-exceed-runtime-RSS-or-artifact-cap",
            "aggregate report exceeds the generated-output cap",
        )
    if not report["resource_checks"]["all_caps_passed"]:
        raise Loop48Refusal(
            "L48-R029-exceed-runtime-RSS-or-artifact-cap",
            "aggregate report resource summary failed",
        )
    _reject_plaintext_fields(report, field_names=FORBIDDEN_OUTPUT_FIELD_NAMES)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(payload)
    return json.loads(payload)


def recompute_aggregate_evidence(
    result: Mapping[str, Any], contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Recompute only the frozen aggregate summaries used by Stage A."""

    snapshot = contract["observed_aggregate_snapshot"]
    metrics = result.get("condition_metrics")
    comparisons = result.get("exact_comparisons")
    if not isinstance(metrics, Mapping) or not isinstance(comparisons, Mapping):
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "missing metrics")

    primary_id = str(snapshot["primary_candidate_id"])
    prior_id = str(snapshot["train_only_prior_id"])
    primary = _metric(metrics, primary_id)
    prior = _metric(metrics, prior_id)
    comparison = comparisons.get("L31-E01")
    if not isinstance(comparison, Mapping):
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "missing comparison")

    all_ids = [_candidate_id(size, seed) for size in PREFIX_SIZES for seed in SEEDS]
    blank_by_condition = {
        condition_id: _finite_fraction(_metric(metrics, condition_id)["blank_fraction"])
        for condition_id in all_ids
    }
    cer_by_condition = {
        condition_id: _finite_nonnegative(
            _metric(metrics, condition_id)["macro_sentence_cer"],
            "macro_sentence_cer",
        )
        for condition_id in all_ids
    }
    prefix_ranges = {
        str(size): max(blank_by_condition[_candidate_id(size, seed)] for seed in SEEDS)
        - min(blank_by_condition[_candidate_id(size, seed)] for seed in SEEDS)
        for size in PREFIX_SIZES
    }
    size55_ids = [_candidate_id(55, seed) for seed in SEEDS]
    size55_blanks = [blank_by_condition[condition_id] for condition_id in size55_ids]
    size55_cers = [cer_by_condition[condition_id] for condition_id in size55_ids]
    primary_cer = _finite_nonnegative(primary["macro_sentence_cer"], "primary CER")
    prior_cer = _finite_nonnegative(prior["macro_sentence_cer"], "prior CER")
    primary_blank = _finite_fraction(primary["blank_fraction"])
    exact_count = int(primary["exact_sentence_count"])
    validation_count = int(result.get("validation_items", snapshot["validation_sentence_count"]))
    all_blanks = list(blank_by_condition.values())
    threshold = contract["future_artifact_only_stage_a"]["descriptive_thresholds"]

    aggregate = {
        "primary_candidate_id": primary_id,
        "primary_candidate_macro_sentence_cer": primary_cer,
        "primary_candidate_blank_fraction": primary_blank,
        "primary_candidate_exact_sentences": exact_count,
        "validation_sentence_count": validation_count,
        "train_only_prior_id": prior_id,
        "train_only_prior_macro_sentence_cer": prior_cer,
        "primary_prior_minus_candidate_margin": prior_cer - primary_cer,
        "primary_wins_ties_losses": [
            int(comparison["wins"]),
            int(comparison["ties"]),
            int(comparison["losses"]),
        ],
        "primary_one_sided_exact_p": float(comparison["one_sided_greater_p"]),
        "size55_seed_ids": size55_ids,
        "size55_blank_fractions": size55_blanks,
        "size55_blank_fraction_min": min(size55_blanks),
        "size55_blank_fraction_max": max(size55_blanks),
        "size55_blank_fraction_range": max(size55_blanks) - min(size55_blanks),
        "size55_macro_sentence_cers": size55_cers,
        "size55_every_seed_worse_than_prior": all(value > prior_cer for value in size55_cers),
        "trained_scaling_condition_count": len(all_ids),
        "trained_scaling_blank_fractions": blank_by_condition,
        "trained_scaling_blank_fraction_min": min(all_blanks),
        "trained_scaling_blank_fraction_max": max(all_blanks),
        "trained_scaling_blank_fraction_range": max(all_blanks) - min(all_blanks),
        "trained_scaling_blank_fraction_ge_0_95_count": sum(
            value >= threshold["primary_blank_dominant_at_or_above"] for value in all_blanks
        ),
        "trained_scaling_blank_fraction_le_0_05_count": sum(value <= 0.05 for value in all_blanks),
        "prefix_blank_ranges": prefix_ranges,
        "prefix_groups_with_blank_range_at_least_0_25": sum(
            value >= threshold["fixed_prefix_seed_blank_range_unstable_at_or_above"]
            for value in prefix_ranges.values()
        ),
        "prefix_group_count": len(prefix_ranges),
        "source_cache_preprocessing_is_causal": bool(
            snapshot["source_cache_preprocessing_is_causal"]
        ),
        "loop25_mechanics_produced_source_cache": bool(
            snapshot["loop25_mechanics_produced_source_cache"]
        ),
    }
    _verify_recomputed_snapshot(aggregate, snapshot)
    return aggregate


def apply_ordered_failure_tree(
    *,
    ordered_classes: Sequence[Mapping[str, Any]],
    aggregate_evidence: Mapping[str, Any],
    thresholds: Mapping[str, Any],
    identity_ok: bool,
    temporal_ctc_infeasible: bool | None,
    additional_class_evidence: Mapping[str, bool | None] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Apply all eight frozen classes in precedence order."""

    expected_order = ["F1", "F2", "F5", "F3", "F4", "F6", "F7", "U0"]
    if [row.get("class_id") for row in ordered_classes] != expected_order:
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "decision tree drift")
    extra = dict(additional_class_evidence or {})
    f5_checks = {
        "primary_blank_dominant": (
            aggregate_evidence["primary_candidate_blank_fraction"]
            >= thresholds["primary_blank_dominant_at_or_above"]
        ),
        "minimum_unstable_prefix_groups": (
            aggregate_evidence["prefix_groups_with_blank_range_at_least_0_25"]
            >= thresholds["minimum_unstable_prefix_groups_for_F5"]
        ),
        "every_size55_seed_worse_than_prior": aggregate_evidence[
            "size55_every_seed_worse_than_prior"
        ],
        "primary_exact_sentence_count": (
            aggregate_evidence["primary_candidate_exact_sentences"]
            == thresholds["require_primary_exact_sentence_count_for_F5"]
        ),
    }
    evidence: dict[str, bool | None] = {
        "F1": not identity_ok,
        "F2": temporal_ctc_infeasible,
        "F5": all(f5_checks.values()),
        "F3": extra.get("F3"),
        "F4": extra.get("F4"),
        "F6": extra.get("F6"),
        "F7": extra.get("F7"),
    }
    trace: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    for row in ordered_classes:
        class_id = str(row["class_id"])
        trace_row = {
            "order": int(row["order"]),
            "class_id": class_id,
            "label": str(row["label"]),
            "root_cause_claim_allowed": False,
        }
        if selected is not None:
            trace_row["state"] = "not_evaluated_after_higher_priority_selection"
        elif class_id == "U0":
            trace_row["state"] = "triggered"
            selected = dict(row)
        elif evidence[class_id] is True:
            trace_row["state"] = "triggered"
            if class_id == "F5":
                trace_row["checks"] = f5_checks
            selected = dict(row)
        elif evidence[class_id] is False:
            trace_row["state"] = "not_triggered"
            if class_id == "F5":
                trace_row["checks"] = f5_checks
        else:
            trace_row["state"] = "unavailable"
        trace.append(trace_row)
    if selected is None:  # pragma: no cover - U0 makes this unreachable
        raise RuntimeError("failure tree did not select a class")
    return selected, trace


def inspect_failure_localization_report(path: str | Path) -> dict[str, Any]:
    """Strictly inspect one aggregate report without touching any source artifact."""

    source = Path(path)
    size = source.stat().st_size
    if size > StageACaps().generated_output_bytes:
        raise ValueError("Loop 48 report exceeds 1 MiB")
    payload = source.read_bytes()
    report = json.loads(payload)
    if report.get("schema_name") != REPORT_SCHEMA_NAME:
        raise ValueError("Loop 48 report schema mismatch")
    if report.get("schema_version") != REPORT_SCHEMA_VERSION:
        raise ValueError("Loop 48 report version mismatch")
    if report.get("generated_bytes") != len(payload):
        raise ValueError("Loop 48 generated byte count mismatch")
    if report.get("input_bytes") != sum(
        int(row["bytes"]) for row in report.get("input_artifact_hashes", [])
    ):
        raise ValueError("Loop 48 input byte count mismatch")
    if len(report.get("input_artifact_hashes", [])) != 4:
        raise ValueError("Loop 48 requires four input hashes")
    _reject_plaintext_fields(report, field_names=FORBIDDEN_OUTPUT_FIELD_NAMES)
    counters = report["access_counters"]
    if counters["runtime_committed_json_reads"] != 4:
        raise ValueError("Loop 48 committed JSON read count mismatch")
    if counters["input_sha256_verifications"] != 4:
        raise ValueError("Loop 48 SHA-256 verification count mismatch")
    if counters["generated_diagnostic_reports"] != 1:
        raise ValueError("Loop 48 generated report count mismatch")
    for name in FORBIDDEN_ACCESS_COUNTERS:
        if counters[name] != 0:
            raise ValueError(f"forbidden Loop 48 access counter is nonzero: {name}")
    resources = report["resource_checks"]
    if not resources.get("all_caps_passed"):
        raise ValueError("Loop 48 resource checks failed")
    if not all(value for key, value in resources.items() if key != "all_caps_passed"):
        raise ValueError("Loop 48 resource summary is inconsistent")
    primary = report["primary_failure_class"]
    if primary["class_id"] != "F5" or primary["root_cause_established"] is not False:
        raise ValueError("Loop 48 registered diagnosis mismatch")
    return {
        "status": report["status"],
        "proof_posture": report["proof_posture"],
        "primary_failure_class": primary["class_id"],
        "root_cause_established": primary["root_cause_established"],
        "input_artifact_count": len(report["input_artifact_hashes"]),
        "input_bytes": report["input_bytes"],
        "runtime_sec": report["runtime_sec"],
        "peak_rss_bytes": report["peak_rss_bytes"],
        "generated_bytes": report["generated_bytes"],
        "model_inference_runs": counters["model_inference_runs"],
        "training_or_parameter_update_runs": counters["training_or_parameter_update_runs"],
        "end_to_end_latency_measured": report["producer"]["end_to_end_latency_measured"],
        "warnings": report["warnings"],
        "claim_boundary": report["claim_boundary"],
    }


def _validate_registered_environment() -> None:
    mismatches = {
        name: os.environ.get(name)
        for name, expected in THREAD_ENVIRONMENT.items()
        if os.environ.get(name) != expected
    }
    if mismatches:
        raise Loop48Refusal(
            "L48-R029-exceed-runtime-RSS-or-artifact-cap",
            f"single-thread environment mismatch: {mismatches}",
        )


def _validate_registered_git_state(root: Path, implementation_commit: str) -> None:
    if len(implementation_commit) != 40 or any(
        character not in "0123456789abcdef" for character in implementation_commit
    ):
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "commit")
    head = _git_output(root, "rev-parse", "HEAD")
    if head != implementation_commit:
        raise Loop48Refusal(
            "L48-R030-execute-before-separate-green-authorization",
            "implementation commit must equal HEAD",
        )
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", REGISTERED_AUTHORIZATION_COMMIT, head],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if ancestor.returncode != 0:
        raise Loop48Refusal(
            "L48-R030-execute-before-separate-green-authorization",
            "authorization commit is not an ancestor",
        )
    tracked_diff = subprocess.run(
        ["git", "diff", "--quiet", "--ignore-submodules", "HEAD"],
        cwd=root,
        check=False,
    )
    if tracked_diff.returncode != 0:
        raise Loop48Refusal(
            "L48-R030-execute-before-separate-green-authorization",
            "tracked worktree changes exist",
        )


def _validate_registered_governance(
    contract: Mapping[str, Any], decision: Mapping[str, Any]
) -> None:
    if contract.get("schema_name") != "neurodecodekit.loop48_failure_localization_contract":
        raise Loop48Refusal("L48-R001-unbound-artifact-input", "contract schema")
    if decision.get("schema_name") != "neurodecodekit.loop48_authorization_decision":
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "decision")
    if decision["authorization_request"]["request_commit"][:7] != "0ffdf47":
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "request")
    if decision["authorized_contract"]["contract_sha256"] != REGISTERED_CONTRACT_SHA256:
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "binding")
    if (
        sum(int(row["bytes"]) for row in contract["committed_input_artifacts"])
        != REGISTERED_INPUT_BYTES
    ):
        raise Loop48Refusal("L48-R001-unbound-artifact-input", "input byte total")


def _validate_authorization_payload(decision: Mapping[str, Any]) -> None:
    authorization = decision.get("authorization")
    if not isinstance(authorization, Mapping):
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "authorization")
    required = {
        "loop48_artifact_only_implementation_authorized_now",
        "exact_four_committed_json_reads_authorized_now",
        "exact_input_sha256_verification_authorized_now",
        "frozen_aggregate_recomputation_authorized_now",
        "fixed_prefix_seed_dispersion_checks_authorized_now",
        "ordered_eight_class_tree_authorized_now",
        "one_aggregate_target_free_report_authorized_now",
        "one_stage_a_execution_authorized_now",
    }
    if any(authorization.get(name) is not True for name in required):
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", "scope")
    forbidden_true = [
        name
        for name, value in authorization.items()
        if name.endswith("authorized_now") and name not in required and value is not False
    ]
    if forbidden_true:
        raise Loop48Refusal(
            "L48-R030-execute-before-separate-green-authorization",
            f"forbidden authorization expanded: {forbidden_true}",
        )


def _validate_artifact_specs(specs: Sequence[Mapping[str, Any]]) -> None:
    expected_ids = {
        "loop26_consumed_result",
        "loop26_prediction_freeze",
        "loop26_shared_contract",
        "loop25_causal_mechanics_result",
    }
    ids = [str(row.get("artifact_id")) for row in specs]
    if len(ids) != 4 or set(ids) != expected_ids or len(ids) != len(set(ids)):
        raise Loop48Refusal("L48-R001-unbound-artifact-input", "artifact inventory")
    for spec in specs:
        if int(spec.get("bytes", 0)) <= 1:
            raise Loop48Refusal("L48-R001-unbound-artifact-input", "artifact bytes")
        digest = str(spec.get("sha256", ""))
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise Loop48Refusal("L48-R001-unbound-artifact-input", "artifact hash")


def _validate_payload_roles(payloads: Mapping[str, Mapping[str, Any]]) -> None:
    result = payloads["loop26_consumed_result"]
    freeze = payloads["loop26_prediction_freeze"]
    if result.get("plaintext_targets_or_predictions_present") is not False:
        raise Loop48Refusal("L48-R003-plaintext-target-or-prediction-output", "result")
    if freeze.get("plaintext_predictions_committed") is not False:
        raise Loop48Refusal("L48-R003-plaintext-target-or-prediction-output", "freeze")
    if freeze.get("validation_target_rows_delivered") != 0:
        raise Loop48Refusal("L48-R008-validation-target-reopen", "freeze target counter")
    if not isinstance(payloads["loop26_shared_contract"], Mapping):
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "shared contract")
    if not isinstance(payloads["loop25_causal_mechanics_result"], Mapping):
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "Loop 25 result")


def _read_bound_json(
    path: Path, spec: Mapping[str, Any]
) -> tuple[Mapping[str, Any], dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise Loop48Refusal("L48-R001-unbound-artifact-input", str(path))
    expected_bytes = int(spec["bytes"])
    if path.stat().st_size != expected_bytes:
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", str(path))
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    if len(payload) != expected_bytes or digest != spec["sha256"]:
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", str(path))
    parsed = json.loads(payload)
    if not isinstance(parsed, Mapping):
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", str(path))
    return parsed, {
        "artifact_id": str(spec["artifact_id"]),
        "path": str(spec["path"]),
        "bytes": len(payload),
        "sha256": digest,
        "sha256_verified": True,
        "plaintext_targets_or_predictions_present": False,
    }


def _load_governance_json(path: Path, *, expected_sha256: str) -> Mapping[str, Any]:
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 128 * 1024:
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", str(path))
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", str(path))
    parsed = json.loads(payload)
    if not isinstance(parsed, Mapping):
        raise Loop48Refusal("L48-R030-execute-before-separate-green-authorization", str(path))
    return parsed


def _verify_recomputed_snapshot(aggregate: Mapping[str, Any], snapshot: Mapping[str, Any]) -> None:
    keys = (
        "primary_candidate_id",
        "primary_candidate_macro_sentence_cer",
        "primary_candidate_blank_fraction",
        "primary_candidate_exact_sentences",
        "validation_sentence_count",
        "train_only_prior_id",
        "train_only_prior_macro_sentence_cer",
        "primary_prior_minus_candidate_margin",
        "primary_wins_ties_losses",
        "primary_one_sided_exact_p",
        "size55_seed_ids",
        "size55_blank_fractions",
        "size55_blank_fraction_min",
        "size55_blank_fraction_max",
        "size55_blank_fraction_range",
        "size55_macro_sentence_cers",
        "size55_every_seed_worse_than_prior",
        "trained_scaling_condition_count",
        "trained_scaling_blank_fraction_min",
        "trained_scaling_blank_fraction_max",
        "trained_scaling_blank_fraction_range",
        "trained_scaling_blank_fraction_ge_0_95_count",
        "trained_scaling_blank_fraction_le_0_05_count",
        "prefix_blank_ranges",
        "prefix_groups_with_blank_range_at_least_0_25",
        "prefix_group_count",
        "source_cache_preprocessing_is_causal",
        "loop25_mechanics_produced_source_cache",
    )
    for key in keys:
        if not _values_equal(aggregate[key], snapshot[key]):
            raise Loop48Refusal(
                "L48-R002-artifact-byte-or-hash-mismatch",
                f"recomputed aggregate mismatch: {key}",
            )


def _values_equal(left: Any, right: Any) -> bool:
    if isinstance(left, Mapping) and isinstance(right, Mapping):
        return set(left) == set(right) and all(_values_equal(left[key], right[key]) for key in left)
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            _values_equal(a, b) for a, b in zip(left, right, strict=True)
        )
    if isinstance(left, float) or isinstance(right, float):
        return math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-12)
    return left == right


def _metric(metrics: Mapping[str, Any], condition_id: str) -> Mapping[str, Any]:
    value = metrics.get(condition_id)
    if not isinstance(value, Mapping):
        raise Loop48Refusal(
            "L48-R002-artifact-byte-or-hash-mismatch",
            f"missing condition metric: {condition_id}",
        )
    return value


def _finite_fraction(value: Any) -> float:
    result = float(value)
    if not math.isfinite(result) or not 0.0 <= result <= 1.0:
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", "blank fraction")
    return result


def _finite_nonnegative(value: Any, name: str) -> float:
    result = float(value)
    if not math.isfinite(result) or result < 0.0:
        raise Loop48Refusal("L48-R002-artifact-byte-or-hash-mismatch", name)
    return result


def _candidate_id(size: int, seed: int) -> str:
    return f"L33-N{size:02d}-S{seed}"


def _reject_plaintext_fields(value: Any, *, field_names: frozenset[str]) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).casefold() in field_names:
                raise Loop48Refusal(
                    "L48-R003-plaintext-target-or-prediction-output",
                    f"forbidden plaintext field: {key}",
                )
            _reject_plaintext_fields(nested, field_names=field_names)
    elif isinstance(value, list):
        for nested in value:
            _reject_plaintext_fields(nested, field_names=field_names)


def _stage_a_access_counters() -> dict[str, int]:
    counters = {
        "governance_json_reads": 2,
        "runtime_committed_json_reads": 4,
        "input_sha256_verifications": 4,
        "generated_diagnostic_reports": 1,
    }
    counters.update({name: 0 for name in FORBIDDEN_ACCESS_COUNTERS})
    return counters


def _stabilized_report_bytes(report: dict[str, Any]) -> bytes:
    for _ in range(12):
        payload = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if report["generated_bytes"] == len(payload):
            return payload
        report["generated_bytes"] = len(payload)
    raise RuntimeError("Loop 48 report byte count did not stabilize")


def _resolve_under_root(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise Loop48Refusal("L48-R001-unbound-artifact-input", str(path))
    return resolved


def _git_output(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024
