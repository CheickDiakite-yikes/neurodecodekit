"""Authorized target-free Loop 25 causal preprocessing mechanics gate."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.preprocess.causal_preprocessing import (
    CausalPreprocessingRefusal,
    CausalPreprocessor,
    FilterBundle,
    audit_static_filter_design,
    design_registered_filter_bundle,
    load_filter_bundle,
    load_registered_contract,
    save_filter_bundle,
    validate_loop25_authorization,
)
from neurodecodekit.training.causal_preprocessing_fixture import (
    LoadedCausalPreprocessingPartition,
    load_causal_preprocessing_manifest,
    load_causal_preprocessing_partition,
)


STATIC_REPORT_SCHEMA_NAME = "b2q-causal-preprocessing-static-gate"
GATE_REPORT_SCHEMA_NAME = "b2q-causal-preprocessing-gate"
REPORT_SCHEMA_VERSION = 0
AUDIT_SCHEMA_NAME = "b2q-causal-preprocessing-audit"
AUDIT_SCHEMA_VERSION = 0
PROOF_POSTURE = "target_free_synthetic_causal_preprocessing_mechanics_only"
AUTHORIZATION_COMMIT = "1e7296a81e59810b87ead48e36cb134b3909c6c7"
AUTHORIZATION_CI_RUN = 29275552886
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_COUNTERS = (
    "normalization_fit_runs",
    "real_data_reads",
    "real_cache_reads",
    "consumed_evidence_reads",
    "target_label_text_prediction_reads",
    "checkpoint_reads",
    "model_runs",
    "training_runs",
    "parameter_updates",
    "external_network_calls",
    "rw3_operations",
    "stream_socket_board_device_hardware_operations",
)


@dataclass(frozen=True)
class CausalPreprocessingCaps:
    """Frozen Loop 25 v1 resource limits."""

    maximum_fixture_bytes_total: int = 4 * 1024 * 1024
    maximum_materialized_working_array_bytes: int = 16 * 1024 * 1024
    maximum_mutable_state_bytes: int = 4 * 1024
    maximum_report_bytes: int = 1 * 1024 * 1024
    maximum_generated_bytes_total: int = 8 * 1024 * 1024
    maximum_internal_runtime_sec: float = 45.0
    maximum_peak_rss_bytes: int = 1024**3
    cpu_threads: int = 1
    maximum_concurrent_workers: int = 1

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def registered_causal_preprocessing_caps() -> CausalPreprocessingCaps:
    """Return resource limits and verify them against the v1 contract."""

    caps = CausalPreprocessingCaps()
    registered = load_registered_contract()["resource_caps"]
    expected = {
        "maximum_fixture_bytes_total": registered["maximum_fixture_bytes_total"],
        "maximum_materialized_working_array_bytes": registered[
            "maximum_materialized_working_array_bytes"
        ],
        "maximum_mutable_state_bytes": registered["maximum_mutable_state_bytes"],
        "maximum_report_bytes": registered["maximum_report_bytes"],
        "maximum_generated_bytes_total": registered["maximum_generated_bytes_total"],
        "maximum_internal_runtime_sec": registered["maximum_internal_runtime_sec"],
        "maximum_peak_rss_bytes": registered["maximum_peak_rss_bytes"],
        "cpu_threads": registered["cpu_threads"],
        "maximum_concurrent_workers": registered["maximum_concurrent_workers"],
    }
    for name, value in expected.items():
        if getattr(caps, name) != value:
            raise RuntimeError(f"Loop 25 resource cap drifted at {name}")
    return caps


def run_static_causal_preprocessing_gate(
    *,
    out_dir: str | Path,
    enforce_authorized_output_root: bool = True,
    require_registered_environment: bool = True,
    design_factory: Callable[[], FilterBundle] | None = None,
    audit_runner: Callable[[FilterBundle], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Design once and run the complete static gate before fixture access."""

    started = time.perf_counter()
    caps = registered_causal_preprocessing_caps()
    output = Path(out_dir)
    _validate_output_directory(output, enforce_authorized_output_root)
    contract = load_registered_contract()
    authorization = validate_loop25_authorization()
    environment = _validate_environment(require_registered_environment)
    counters = _new_access_counters(contract)
    events: list[dict[str, Any]] = []
    _event(events, "contract_authorization_environment_validated", counters)

    factory = design_factory or design_registered_filter_bundle
    bundle = factory()
    counters["filter_design_runs"] += 1
    _event(events, "registered_coefficients_designed_and_hashed_once", counters)
    runner = audit_runner or audit_static_filter_design
    static_audit = runner(bundle)
    counters["static_filter_design_gate_runs"] += 1
    counters["alias_fold_map_runs"] += 1
    counters["frequency_response_runs"] += 1
    _event(events, "static_pole_response_alias_impulse_step_gate_completed", counters)

    runtime = time.perf_counter() - started
    peak_rss = _peak_rss_bytes()
    counter_check = _check_access_counters(
        counters,
        _expected_static_counters(contract),
    )
    resource_checks = _resource_checks(
        caps,
        runtime_sec=runtime,
        peak_rss_bytes=peak_rss,
        fixture_bytes=0,
        working_array_bytes=0,
        state_bytes=bundle.filter_state_array_bytes,
    )
    static_passed = bool(
        static_audit.get("passed")
        and counter_check["exact"]
        and all(resource_checks.values())
    )
    report: dict[str, Any] = {
        "schema": {"name": STATIC_REPORT_SCHEMA_NAME, "version": REPORT_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "gate_stage": "static_before_fixture_access",
        "gate_passed": static_passed,
        "decision": (
            "static_pass_fixture_generation_may_proceed"
            if static_passed
            else "park_loop25_both_seeds_unopened"
        ),
        "contract": _contract_identity(contract),
        "authorization": _authorization_identity(authorization),
        "environment": environment,
        "static_filter_audit": static_audit,
        "access": {
            "counters": counters,
            "expected_counters": counter_check["expected"],
            "counter_mismatches": counter_check["mismatches"],
            "exact_counter_match": counter_check["exact"],
            "ordered_events": events,
            "development_seed_opened": False,
            "qualification_seed_opened": False,
            "partition_arrays_opened": 0,
        },
        "resources": {
            **caps.to_dict(),
            "internal_runtime_sec": runtime,
            "peak_rss_bytes": peak_rss,
            "filter_state_array_bytes": bundle.filter_state_array_bytes,
            "input_bytes": 0,
            "output_bytes": 0,
            "upstream_generated_bytes": 0,
            "output_artifact_bytes": 0,
            "report_bytes": 0,
            "total_generated_bytes": 0,
            "checks": resource_checks,
            "all_caps_passed": all(resource_checks.values()),
        },
        "producer": {
            "causal": True,
            "right_context_source_samples": 0,
            "right_context_ms": 0.0,
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            *static_audit.get("warnings", []),
            *(
                []
                if counter_check["exact"]
                else ["Access counters did not match the frozen static schedule."]
            ),
            *(
                []
                if all(resource_checks.values())
                else ["At least one static resource ceiling was exceeded."]
            ),
        ],
        "claim_boundaries": [
            "A static pass qualifies only the registered filter design mechanics.",
            "No neural data, target, model, training, decoding, or latency result exists.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    bundle_path = output / "filter_bundle.json"
    save_filter_bundle(bundle_path, bundle, static_audit)
    report["filter_bundle"] = {
        "path": bundle_path.name,
        "bytes": bundle_path.stat().st_size,
        "sha256": _file_sha256(bundle_path),
    }
    _write_report_artifacts(
        output,
        report,
        prefix="static_gate",
        caps=caps,
        upstream_generated_bytes=0,
        failure_decision="park_loop25_both_seeds_unopened",
    )
    return json.loads((output / "static_gate.json").read_text(encoding="utf-8"))


def run_causal_preprocessing_gate(
    *,
    fixture_manifest_path: str | Path,
    filter_bundle_path: str | Path,
    out_dir: str | Path,
    enforce_authorized_output_root: bool = True,
    require_registered_environment: bool = True,
    require_registered_fixture: bool = True,
    require_registered_filter: bool = True,
) -> dict[str, Any]:
    """Run development and conditional one-time qualification under v1."""

    started = time.perf_counter()
    caps = registered_causal_preprocessing_caps()
    output = Path(out_dir)
    _validate_output_directory(output, enforce_authorized_output_root)
    contract = load_registered_contract()
    authorization = validate_loop25_authorization()
    environment = _validate_environment(require_registered_environment)
    bundle_path = Path(filter_bundle_path)
    bundle, static_audit = load_filter_bundle(
        bundle_path,
        require_registered=require_registered_filter,
    )
    if not static_audit.get("passed"):
        raise CausalPreprocessingRefusal(
            "full_folding_band_attenuation_failed",
            "static filter gate failed; partitions remain unopened",
        )
    counters = _new_access_counters(contract)
    counters["filter_design_runs"] = 1
    counters["static_filter_design_gate_runs"] = 1
    counters["alias_fold_map_runs"] = 1
    counters["frequency_response_runs"] = 1
    events: list[dict[str, Any]] = []
    _event(events, "authorization_and_static_filter_pass_validated", counters)

    manifest = load_causal_preprocessing_manifest(
        fixture_manifest_path,
        max_total_bytes=caps.maximum_fixture_bytes_total,
        require_registered_protocol=require_registered_fixture,
    )
    counters["manifest_metadata_reads"] += 1
    if manifest["static_filter_bundle_sha256"] != _file_sha256(bundle_path):
        raise CausalPreprocessingRefusal(
            "filter_configuration_or_coefficient_hash_mismatch",
            "fixture is not bound to the supplied static filter bundle",
        )
    _event(events, "fixture_manifest_validated_without_array_open", counters)

    output.mkdir(parents=True, exist_ok=False)
    development = load_causal_preprocessing_partition(
        fixture_manifest_path,
        "development",
        max_total_bytes=caps.maximum_fixture_bytes_total,
        require_registered_protocol=require_registered_fixture,
    )
    counters["development_partition_opens"] += 1
    _event(events, "development_partition_opened_once", counters)
    development_report = _evaluate_partition(
        development,
        bundle=bundle,
        contract=contract,
        counters=counters,
    )
    development_path = output / "development.json"
    _write_bounded_json(development_path, development_report, caps.maximum_report_bytes)
    development_frozen = {
        "path": development_path.name,
        "bytes": development_path.stat().st_size,
        "sha256": _file_sha256(development_path),
        "passed": development_report["passed"],
    }
    _event(events, "development_report_frozen_and_hashed", counters)

    qualification_report: dict[str, Any]
    if development_report["passed"]:
        qualification = load_causal_preprocessing_partition(
            fixture_manifest_path,
            "qualification",
            max_total_bytes=caps.maximum_fixture_bytes_total,
            require_registered_protocol=require_registered_fixture,
        )
        counters["qualification_partition_opens"] += 1
        _event(events, "qualification_partition_opened_once_after_development_freeze", counters)
        qualification_report = _evaluate_partition(
            qualification,
            bundle=bundle,
            contract=contract,
            counters=counters,
        )
        qualification_path = output / "qualification.json"
        _write_bounded_json(qualification_path, qualification_report, caps.maximum_report_bytes)
        qualification_frozen = {
            "path": qualification_path.name,
            "bytes": qualification_path.stat().st_size,
            "sha256": _file_sha256(qualification_path),
            "passed": qualification_report["passed"],
        }
        _event(events, "qualification_report_frozen_and_hashed", counters)
    else:
        qualification_report = {
            "split": "qualification",
            "opened": False,
            "passed": False,
            "reason": "development_failed_qualification_not_opened",
        }
        qualification_frozen = None
        _event(events, "development_failed_qualification_kept_unopened", counters)

    runtime = time.perf_counter() - started
    peak_rss = _peak_rss_bytes()
    qualification_opened = qualification_frozen is not None
    counter_check = _check_access_counters(
        counters,
        _expected_full_counters(
            contract,
            development_items=len(development_report["items"]),
            qualification_items=(
                len(qualification_report["items"]) if qualification_opened else 0
            ),
            qualification_opened=qualification_opened,
        ),
    )
    forbidden_zero = all(counters[name] == 0 for name in FORBIDDEN_COUNTERS)
    maximum_partition_array_bytes = max(
        development.array_bytes,
        int(qualification_report.get("array_bytes", 0)),
    )
    input_bytes = development.array_bytes + int(qualification_report.get("array_bytes", 0))
    output_bytes = int(development_report["summary"]["output_bytes"]) + int(
        qualification_report.get("summary", {}).get("output_bytes", 0)
    )
    upstream_generated_bytes = int(manifest["artifacts"]["total_bytes"]) + _directory_file_bytes(
        bundle_path.parent
    )
    resource_checks = _resource_checks(
        caps,
        runtime_sec=runtime,
        peak_rss_bytes=peak_rss,
        fixture_bytes=int(manifest["artifacts"]["total_bytes"]),
        working_array_bytes=maximum_partition_array_bytes,
        state_bytes=bundle.filter_state_array_bytes,
    )
    gate_passed = bool(
        development_report["passed"]
        and qualification_opened
        and qualification_report["passed"]
        and forbidden_zero
        and counter_check["exact"]
        and all(resource_checks.values())
    )
    report: dict[str, Any] = {
        "schema": {"name": GATE_REPORT_SCHEMA_NAME, "version": REPORT_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "gate_stage": "development_and_conditional_qualification",
        "gate_passed": gate_passed,
        "decision": (
            "loop25_causal_preprocessing_mechanics_passed_ready_for_separate_loop26_decision"
            if gate_passed
            else "park_loop25_and_block_loop26_real_model_gate"
        ),
        "contract": _contract_identity(contract),
        "authorization": _authorization_identity(authorization),
        "environment": environment,
        "filter_bundle": {
            "path": bundle_path.name,
            "bytes": bundle_path.stat().st_size,
            "sha256": _file_sha256(bundle_path),
            "filter_sos_sha256": bundle.filter_sos_sha256,
            "static_gate_passed": True,
        },
        "fixture": {
            "manifest_path": Path(fixture_manifest_path).name,
            "manifest_sha256": _file_sha256(Path(fixture_manifest_path)),
            "protocol_sha256": manifest["protocol_sha256"],
            "bytes": manifest["artifacts"]["total_bytes"],
        },
        "development": {**development_frozen, "summary": development_report["summary"]},
        "qualification": (
            {
                **qualification_frozen,
                "opened": True,
                "summary": qualification_report["summary"],
            }
            if qualification_frozen is not None
            else qualification_report
        ),
        "access": {
            "counters": counters,
            "expected_counters": counter_check["expected"],
            "counter_mismatches": counter_check["mismatches"],
            "exact_counter_match": counter_check["exact"],
            "ordered_events": events,
            "forbidden_counters_zero": forbidden_zero,
        },
        "resources": {
            **caps.to_dict(),
            "internal_runtime_sec": runtime,
            "peak_rss_bytes": peak_rss,
            "maximum_partition_array_bytes": maximum_partition_array_bytes,
            "filter_state_array_bytes": bundle.filter_state_array_bytes,
            "input_bytes": input_bytes,
            "output_bytes": output_bytes,
            "upstream_generated_bytes": upstream_generated_bytes,
            "output_artifact_bytes": 0,
            "report_bytes": 0,
            "total_generated_bytes": 0,
            "checks": resource_checks,
            "all_caps_passed": all(resource_checks.values()),
        },
        "producer": {
            "causal": True,
            "right_context_source_samples": 0,
            "right_context_ms": 0.0,
            "sample_grid_timestamps": True,
            "effective_signal_timestamp": "unavailable_frequency_dependent_delay",
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            "The causal path is not numerically equivalent to the official offline MNE FFT resampler.",
            "A mechanics pass does not prove that neural information is retained.",
            "Frequency-dependent filter delay is not end-to-end latency.",
            *(
                []
                if counter_check["exact"]
                else ["Access counters did not match the frozen execution schedule."]
            ),
            *(
                []
                if all(resource_checks.values())
                else ["At least one registered resource ceiling was exceeded."]
            ),
        ],
        "claim_boundaries": [
            "This gate can establish target-free causal preprocessing mechanics only.",
            "It cannot establish neural advantage, decoding accuracy, unseen-person transfer, device behavior, or clinical utility.",
        ],
    }
    _write_report_artifacts(
        output,
        report,
        prefix="gate",
        caps=caps,
        upstream_generated_bytes=upstream_generated_bytes,
        failure_decision="park_loop25_and_block_loop26_real_model_gate",
    )
    return json.loads((output / "gate.json").read_text(encoding="utf-8"))


def inspect_causal_preprocessing_report(path: str | Path) -> dict[str, Any]:
    """Strictly validate a static or complete report without opening fixture arrays."""

    source = Path(path)
    if source.stat().st_size > 1024 * 1024:
        raise ValueError("Loop 25 report exceeds 1 MiB")
    report = json.loads(source.read_text(encoding="utf-8"))
    schema = report.get("schema", {})
    if schema.get("name") not in {STATIC_REPORT_SCHEMA_NAME, GATE_REPORT_SCHEMA_NAME}:
        raise ValueError("Loop 25 report schema mismatch")
    if schema.get("version") != REPORT_SCHEMA_VERSION:
        raise ValueError("Loop 25 report version mismatch")
    audit_path = source.with_name(f"{source.stem}.audit.json")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("schema") != {"name": AUDIT_SCHEMA_NAME, "version": AUDIT_SCHEMA_VERSION}:
        raise ValueError("Loop 25 audit schema mismatch")
    if audit["report_sha256"] != _file_sha256(source):
        raise ValueError("Loop 25 report hash mismatch")
    markdown_path = source.with_suffix(".md")
    if audit["markdown_sha256"] != _file_sha256(markdown_path):
        raise ValueError("Loop 25 Markdown hash mismatch")
    counters = report["access"]["counters"]
    for name in FORBIDDEN_COUNTERS:
        if counters[name] != 0:
            raise ValueError(f"forbidden access counter is nonzero: {name}")
    if not report["access"]["exact_counter_match"]:
        raise ValueError("Loop 25 access counters do not match the frozen schedule")
    resources = report["resources"]
    if resources["report_bytes"] > resources["maximum_report_bytes"]:
        raise ValueError("Loop 25 report cap exceeded")
    if resources["total_generated_bytes"] > resources["maximum_generated_bytes_total"]:
        raise ValueError("Loop 25 generated byte cap exceeded")
    if resources["all_caps_passed"] != all(resources["checks"].values()):
        raise ValueError("Loop 25 resource-check summary mismatch")
    if resources["output_artifact_bytes"] != _directory_file_bytes(source.parent):
        raise ValueError("Loop 25 output artifact byte count mismatch")
    if resources["total_generated_bytes"] != (
        resources["upstream_generated_bytes"] + resources["output_artifact_bytes"]
    ):
        raise ValueError("Loop 25 total generated byte count mismatch")
    return {
        "schema": schema,
        "proof_posture": report["proof_posture"],
        "gate_stage": report["gate_stage"],
        "gate_passed": report["gate_passed"],
        "decision": report["decision"],
        "development_partition_opens": counters["development_partition_opens"],
        "qualification_partition_opens": counters["qualification_partition_opens"],
        "producer_causal": report["producer"]["causal"],
        "right_context_source_samples": report["producer"]["right_context_source_samples"],
        "end_to_end_latency_measured": report["producer"]["end_to_end_latency_measured"],
        "runtime_sec": resources["internal_runtime_sec"],
        "peak_rss_bytes": resources["peak_rss_bytes"],
        "report_bytes": resources["report_bytes"],
        "total_generated_bytes": resources["total_generated_bytes"],
        "warnings": report["warnings"],
        "claim_boundaries": report["claim_boundaries"],
    }


def _evaluate_partition(
    partition: LoadedCausalPreprocessingPartition,
    *,
    bundle: FilterBundle,
    contract: Mapping[str, Any],
    counters: dict[str, int],
) -> dict[str, Any]:
    np = _require_numpy()
    schedules = contract["registered_chunk_schedules"]
    resume_cuts = contract["registered_resume_cut_source_samples"]
    future_cuts = contract["registered_future_mutation_cut_source_samples"]
    rows = []
    partition_started = time.perf_counter()
    passed = True
    for item_index, item_id in enumerate(partition.item_ids.tolist()):
        length = int(partition.input_lengths[item_index])
        source_start = int(partition.source_start_samples[item_index])
        signal = partition.signals[item_index, :, :length]
        canonical = _run_schedule(
            signal,
            bundle=bundle,
            source_start_sample=source_start,
            schedule_rule="all_remaining_samples",
            schedule_seed=2511,
        )
        counters["canonical_preprocessing_runs"] += 1
        counters["chunk_schedule_runs"] += 1
        schedule_results = {"whole_item": True}
        for schedule in schedules[1:]:
            replay = _run_schedule(
                signal,
                bundle=bundle,
                source_start_sample=source_start,
                schedule_rule=schedule["rule"],
                schedule_seed=2511,
            )
            counters["chunk_schedule_runs"] += 1
            schedule_results[schedule["schedule_id"]] = _runs_bitwise_equal(canonical, replay)

        resume_results = {}
        for cut in resume_cuts:
            resumed = _run_resume(
                signal,
                cut=int(cut),
                bundle=bundle,
                source_start_sample=source_start,
            )
            counters["resume_runs"] += 1
            resume_results[str(cut)] = _runs_bitwise_equal(canonical, resumed)

        mutation_results = {}
        for cut in future_cuts:
            unchanged = _future_mutation_control(
                signal,
                cut=int(cut),
                bundle=bundle,
                source_start_sample=source_start,
            )
            counters["future_mutation_control_runs"] += 1
            mutation_results[str(cut)] = unchanged

        expected_indices = np.arange(0, length, 10, dtype="int64")
        expected_timestamps = (source_start + expected_indices).astype("float64") / 1000.0
        timing_passed = bool(
            np.array_equal(canonical["source_indices"], expected_indices)
            and np.array_equal(canonical["timestamps_sec"], expected_timestamps)
            and canonical["values"].shape[1] == (length - 1) // 10 + 1
            and np.all(np.diff(canonical["source_indices"]) > 0)
            and np.all(np.diff(canonical["timestamps_sec"]) > 0)
        )
        item_passed = bool(
            all(schedule_results.values())
            and all(resume_results.values())
            and all(mutation_results.values())
            and timing_passed
            and np.isfinite(canonical["values"]).all()
            and float(canonical["values"].min()) >= -5.0
            and float(canonical["values"].max()) <= 5.0
            and canonical["flush"]["invented_source_samples"] == 0
            and canonical["flush"]["invented_output_samples"] == 0
        )
        passed = passed and item_passed
        rows.append(
            {
                "item_id": item_id,
                "input_samples": length,
                "output_samples": int(canonical["values"].shape[1]),
                "output_bytes": int(
                    canonical["values"].nbytes
                    + canonical["source_indices"].nbytes
                    + canonical["timestamps_sec"].nbytes
                ),
                "schedule_results": schedule_results,
                "resume_results": resume_results,
                "future_mutation_results": mutation_results,
                "timing_passed": timing_passed,
                "final_state_sha256": canonical["final_state_sha256"],
                "passed": item_passed,
            }
        )
    runtime = time.perf_counter() - partition_started
    return {
        "schema": {"name": "b2q-causal-preprocessing-partition-gate", "version": 0},
        "split": partition.split,
        "opened": True,
        "passed": passed,
        "items": rows,
        "summary": {
            "items": len(rows),
            "items_passed": sum(row["passed"] for row in rows),
            "valid_source_samples": int(partition.input_lengths.sum()),
            "valid_output_samples": sum(row["output_samples"] for row in rows),
            "chunk_schedule_checks": len(rows) * len(schedules),
            "resume_checks": len(rows) * len(resume_cuts),
            "future_mutation_checks": len(rows) * len(future_cuts),
            "input_array_bytes": partition.array_bytes,
            "output_bytes": sum(row["output_bytes"] for row in rows),
            "runtime_sec": runtime,
            "padding_fraction": float(
                1.0
                - partition.input_lengths.sum()
                / (partition.signals.shape[0] * partition.signals.shape[2])
            ),
        },
        "array_bytes": partition.array_bytes,
    }


def _run_schedule(
    signal: Any,
    *,
    bundle: FilterBundle,
    source_start_sample: int,
    schedule_rule: str,
    schedule_seed: int,
) -> dict[str, Any]:
    np = _require_numpy()
    processor = CausalPreprocessor(
        bundle,
        source_start_sample=source_start_sample,
        require_registered=bundle.contract_sha256 != "test-contract",
    )
    chunks = _schedule_sizes(schedule_rule, int(signal.shape[1]), seed=schedule_seed)
    outputs = []
    cursor = 0
    for size in chunks:
        result = processor.push(
            signal[:, cursor : cursor + size],
            chunk_start_sample=source_start_sample + cursor,
        )
        outputs.append(result)
        cursor += size
    if cursor != signal.shape[1]:
        raise RuntimeError("chunk schedule did not consume the complete item")
    flush = processor.flush()
    return _combine_outputs(np, outputs, processor.snapshot(), flush)


def _run_resume(
    signal: Any,
    *,
    cut: int,
    bundle: FilterBundle,
    source_start_sample: int,
) -> dict[str, Any]:
    np = _require_numpy()
    registered = bundle.contract_sha256 != "test-contract"
    first = CausalPreprocessor(
        bundle,
        source_start_sample=source_start_sample,
        require_registered=registered,
    )
    prefix = first.push(signal[:, :cut], chunk_start_sample=source_start_sample)
    state = first.snapshot()
    resumed = CausalPreprocessor(
        bundle,
        source_start_sample=source_start_sample,
        require_registered=registered,
        state=state,
    )
    suffix = resumed.push(
        signal[:, cut:],
        chunk_start_sample=source_start_sample + cut,
    )
    flush = resumed.flush()
    return _combine_outputs(np, [prefix, suffix], resumed.snapshot(), flush)


def _future_mutation_control(
    signal: Any,
    *,
    cut: int,
    bundle: FilterBundle,
    source_start_sample: int,
) -> bool:
    np = _require_numpy()
    mutated = signal.copy()
    mutated[:, cut:] = np.clip(-mutated[:, cut:] + 0.125, -4.0, 4.0)
    original = _run_prefix(
        signal[:, :cut], bundle=bundle, source_start_sample=source_start_sample
    )
    changed = _run_prefix(
        mutated[:, :cut], bundle=bundle, source_start_sample=source_start_sample
    )
    return bool(
        np.array_equal(original["values"], changed["values"])
        and np.array_equal(original["source_indices"], changed["source_indices"])
        and np.array_equal(original["timestamps_sec"], changed["timestamps_sec"])
        and original["state"] == changed["state"]
    )


def _run_prefix(signal: Any, *, bundle: FilterBundle, source_start_sample: int) -> dict[str, Any]:
    processor = CausalPreprocessor(
        bundle,
        source_start_sample=source_start_sample,
        require_registered=bundle.contract_sha256 != "test-contract",
    )
    output = processor.push(signal, chunk_start_sample=source_start_sample)
    return {
        "values": output.values,
        "source_indices": output.source_indices,
        "timestamps_sec": output.timestamps_sec,
        "state": processor.snapshot(),
    }


def _combine_outputs(np: Any, outputs: Sequence[Any], state: Mapping[str, Any], flush: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "values": np.concatenate([value.values for value in outputs], axis=1),
        "source_indices": np.concatenate([value.source_indices for value in outputs]),
        "timestamps_sec": np.concatenate([value.timestamps_sec for value in outputs]),
        "state": dict(state),
        "final_state_sha256": state["semantic_sha256"],
        "flush": dict(flush),
    }


def _runs_bitwise_equal(reference: Mapping[str, Any], candidate: Mapping[str, Any]) -> bool:
    np = _require_numpy()
    return bool(
        np.array_equal(reference["values"], candidate["values"])
        and np.array_equal(reference["source_indices"], candidate["source_indices"])
        and np.array_equal(reference["timestamps_sec"], candidate["timestamps_sec"])
        and reference["final_state_sha256"] == candidate["final_state_sha256"]
        and reference["flush"] == candidate["flush"]
    )


def _schedule_sizes(rule: str, length: int, *, seed: int) -> list[int]:
    np = _require_numpy()
    if rule == "all_remaining_samples":
        return [length]
    if rule.startswith("repeat_"):
        cycle = [int(rule.removeprefix("repeat_"))]
    elif rule.startswith("cycle_"):
        cycle = [int(value) for value in rule.removeprefix("cycle_").split("_")]
    elif rule == "uniform_integer_1_to_257_seed_2511":
        rng = np.random.default_rng(seed)
        values = []
        remaining = length
        while remaining:
            size = min(int(rng.integers(1, 258)), remaining)
            values.append(size)
            remaining -= size
        return values
    else:
        raise ValueError(f"unknown registered chunk schedule: {rule}")
    values = []
    remaining = length
    cursor = 0
    while remaining:
        size = min(cycle[cursor % len(cycle)], remaining)
        values.append(size)
        remaining -= size
        cursor += 1
    return values


def _new_access_counters(contract: Mapping[str, Any]) -> dict[str, int]:
    return {name: 0 for name in contract["required_access_counters"]}


def _expected_static_counters(contract: Mapping[str, Any]) -> dict[str, int]:
    expected = _new_access_counters(contract)
    expected.update(
        {
            "filter_design_runs": 1,
            "static_filter_design_gate_runs": 1,
            "alias_fold_map_runs": 1,
            "frequency_response_runs": 1,
        }
    )
    return expected


def _expected_full_counters(
    contract: Mapping[str, Any],
    *,
    development_items: int,
    qualification_items: int,
    qualification_opened: bool,
) -> dict[str, int]:
    expected = _expected_static_counters(contract)
    total_items = development_items + qualification_items
    expected.update(
        {
            "manifest_metadata_reads": 1,
            "development_partition_opens": 1,
            "qualification_partition_opens": int(qualification_opened),
            "canonical_preprocessing_runs": total_items,
            "chunk_schedule_runs": total_items
            * len(contract["registered_chunk_schedules"]),
            "resume_runs": total_items
            * len(contract["registered_resume_cut_source_samples"]),
            "future_mutation_control_runs": total_items
            * len(contract["registered_future_mutation_cut_source_samples"]),
        }
    )
    return expected


def _check_access_counters(
    counters: Mapping[str, int], expected: Mapping[str, int]
) -> dict[str, Any]:
    mismatches = {
        name: {"expected": int(expected[name]), "observed": int(counters.get(name, -1))}
        for name in expected
        if counters.get(name) != expected[name]
    }
    unexpected = sorted(set(counters).difference(expected))
    if unexpected:
        mismatches["__unexpected_counters__"] = {
            "expected": 0,
            "observed": len(unexpected),
            "names": unexpected,
        }
    return {
        "exact": not mismatches,
        "expected": {name: int(value) for name, value in expected.items()},
        "mismatches": mismatches,
    }


def _resource_checks(
    caps: CausalPreprocessingCaps,
    *,
    runtime_sec: float,
    peak_rss_bytes: int,
    fixture_bytes: int,
    working_array_bytes: int,
    state_bytes: int,
) -> dict[str, bool]:
    return {
        "runtime_within_cap": runtime_sec <= caps.maximum_internal_runtime_sec,
        "peak_rss_within_cap": peak_rss_bytes <= caps.maximum_peak_rss_bytes,
        "fixture_bytes_within_cap": fixture_bytes <= caps.maximum_fixture_bytes_total,
        "working_array_bytes_within_cap": (
            working_array_bytes <= caps.maximum_materialized_working_array_bytes
        ),
        "mutable_state_bytes_within_cap": state_bytes <= caps.maximum_mutable_state_bytes,
        "report_bytes_within_cap": True,
        "all_generated_bytes_within_cap": True,
    }


def _event(events: list[dict[str, Any]], action: str, counters: Mapping[str, int]) -> None:
    events.append(
        {
            "index": len(events),
            "action": action,
            "counter_snapshot_sha256": _sha256_json(counters),
        }
    )


def _contract_identity(contract: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "contract_id": contract["contract_id"],
        "schema_version": contract["schema_version"],
        "sha256": _file_sha256(_repo_root() / "registries/causal_preprocessing_contract.v1.json"),
        "pipeline_id": contract["planned_pipeline"]["pipeline_id"],
    }


def _authorization_identity(decision: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "decision_id": decision["decision_id"],
        "path": "registries/loop25_authorization_decision.v1.json",
        "sha256": _file_sha256(
            _repo_root() / "registries/loop25_authorization_decision.v1.json"
        ),
        "commit": AUTHORIZATION_COMMIT,
        "ci_run_id": AUTHORIZATION_CI_RUN,
        "ci_conclusion": "success",
    }


def _validate_environment(require_registered: bool) -> dict[str, Any]:
    scipy = _require_scipy()
    missing = [name for name, value in THREAD_ENVIRONMENT.items() if os.environ.get(name) != value]
    if require_registered and missing:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded",
            f"one-thread environment missing: {missing}",
        )
    for name in ("iirnotch", "tf2sos", "butter", "iirdesign", "sosfilt", "sosfilt_zi"):
        if not hasattr(scipy.signal, name):
            raise CausalPreprocessingRefusal(
                "unsupported_scipy_version_or_api", f"SciPy signal API missing {name}"
            )
    if not (hasattr(scipy.signal, "freqz_sos") or hasattr(scipy.signal, "sosfreqz")):
        raise CausalPreprocessingRefusal(
            "unsupported_scipy_version_or_api", "SciPy lacks an SOS response API"
        )
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": _require_numpy().__version__,
        "scipy": scipy.__version__,
        "thread_environment": {name: os.environ.get(name) for name in THREAD_ENVIRONMENT},
        "registered_thread_environment_match": not missing,
    }


def _write_report_artifacts(
    output: Path,
    report: dict[str, Any],
    *,
    prefix: str,
    caps: CausalPreprocessingCaps,
    upstream_generated_bytes: int,
    failure_decision: str,
) -> None:
    report_path = output / f"{prefix}.json"
    markdown_path = output / f"{prefix}.md"
    audit_path = output / f"{prefix}.audit.json"
    report["artifacts"] = {
        "report_path": report_path.name,
        "markdown_path": markdown_path.name,
        "audit_path": audit_path.name,
    }
    artifact_paths = {report_path, markdown_path, audit_path}
    fixed_output_bytes = sum(
        path.stat().st_size
        for path in output.iterdir()
        if path.is_file() and path not in artifact_paths
    )
    stable_payloads: tuple[bytes, bytes, bytes] | None = None
    for _ in range(12):
        report_payload = _json_payload(report)
        markdown_payload = _report_markdown(report).encode("utf-8")
        audit = {
            "schema": {"name": AUDIT_SCHEMA_NAME, "version": AUDIT_SCHEMA_VERSION},
            "report_path": report_path.name,
            "report_bytes": len(report_payload),
            "report_sha256": hashlib.sha256(report_payload).hexdigest(),
            "markdown_path": markdown_path.name,
            "markdown_bytes": len(markdown_payload),
            "markdown_sha256": hashlib.sha256(markdown_payload).hexdigest(),
            "fixture_array_members_opened_by_inspector": 0,
        }
        audit_payload = _json_payload(audit)
        output_artifact_bytes = (
            fixed_output_bytes
            + len(report_payload)
            + len(markdown_payload)
            + len(audit_payload)
        )
        total_generated_bytes = upstream_generated_bytes + output_artifact_bytes
        resources = report["resources"]
        checks = resources["checks"]
        checks["report_bytes_within_cap"] = len(report_payload) <= caps.maximum_report_bytes
        checks["all_generated_bytes_within_cap"] = (
            total_generated_bytes <= caps.maximum_generated_bytes_total
        )
        all_caps_passed = all(checks.values())
        updated = {
            "report_bytes": len(report_payload),
            "output_artifact_bytes": output_artifact_bytes,
            "total_generated_bytes": total_generated_bytes,
            "all_caps_passed": all_caps_passed,
        }
        changed = any(resources.get(name) != value for name, value in updated.items())
        resources.update(updated)
        if not all_caps_passed:
            if report["gate_passed"] or report["decision"] != failure_decision:
                changed = True
            report["gate_passed"] = False
            report["decision"] = failure_decision
        if not changed:
            stable_payloads = (report_payload, markdown_payload, audit_payload)
            break
    if stable_payloads is None:
        raise RuntimeError("Loop 25 report-size accounting did not converge")
    report_payload, markdown_payload, audit_payload = stable_payloads
    if len(report_payload) > caps.maximum_report_bytes:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded", "Loop 25 report exceeds 1 MiB"
        )
    if report["resources"]["total_generated_bytes"] > caps.maximum_generated_bytes_total:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded", "Loop 25 artifacts exceed 8 MiB"
        )
    report_path.write_bytes(report_payload)
    markdown_path.write_bytes(markdown_payload)
    audit_path.write_bytes(audit_payload)
    if _directory_file_bytes(output) != report["resources"]["output_artifact_bytes"]:
        raise RuntimeError("Loop 25 output byte accounting mismatch")


def _write_bounded_json(path: Path, value: Mapping[str, Any], cap: int) -> None:
    payload = _json_payload(value)
    if len(payload) > cap:
        raise CausalPreprocessingRefusal(
            "resource_or_output_cap_exceeded", f"{path.name} exceeds {cap} bytes"
        )
    path.write_bytes(payload)


def _json_payload(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _report_markdown(report: Mapping[str, Any]) -> str:
    counters = report["access"]["counters"]
    resources = report["resources"]
    lines = [
        "# Loop 25 Causal Preprocessing Report",
        "",
        f"- Gate stage: `{report['gate_stage']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Decision: `{report['decision']}`",
        f"- Producer causal: `{str(report['producer']['causal']).lower()}`",
        f"- Right context: `{report['producer']['right_context_source_samples']}` source samples",
        f"- End-to-end latency measured: `{str(report['producer']['end_to_end_latency_measured']).lower()}`",
        f"- Runtime: `{resources['internal_runtime_sec']:.6f}` sec",
        f"- Peak RSS: `{resources['peak_rss_bytes']}` bytes",
        "",
        "## Access Counters",
        "",
    ]
    lines.extend(f"- `{name}`: {value}" for name, value in counters.items())
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Claim Boundaries", ""])
    lines.extend(f"- {claim}" for claim in report["claim_boundaries"])
    return "\n".join(lines) + "\n"


def _validate_output_directory(output: Path, enforce_authorized_root: bool) -> None:
    if output.exists():
        raise FileExistsError(f"refusing to replace Loop 25 output directory: {output}")
    if not enforce_authorized_root:
        return
    resolved = output.resolve(strict=False)
    roots = [
        (_repo_root() / "cache" / "loop25").resolve(strict=False),
        (_repo_root() / "outputs" / "loop25").resolve(strict=False),
        (_repo_root() / ".codex_work" / "loop25").resolve(strict=False),
    ]
    if not any(resolved != root and root in resolved.parents for root in roots):
        raise ValueError("Loop 25 output must be nested under an authorized loop25 root")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if platform.system() == "Darwin" else value * 1024


def _directory_file_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("Loop 25 requires NumPy. Install neurodecodekit[neuro].") from exc
    return np


def _require_scipy():
    try:
        import scipy
        import scipy.signal
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("Loop 25 requires SciPy. Install neurodecodekit[neuro].") from exc
    return scipy
