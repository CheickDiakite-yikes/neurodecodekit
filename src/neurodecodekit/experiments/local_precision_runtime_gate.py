"""Authorized target-free Loop 24 local precision and runtime gate."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import multiprocessing
import os
import platform
import resource
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.decoding.ctc_prefix import GreedyCTCDecoder, PrefixBeamCTCDecoder
from neurodecodekit.evaluation.blank_calibration import (
    BLANK_CALIBRATION_CONFIG_SHA256,
    registered_blank_intercept_config,
)
from neurodecodekit.models.precision_candidates import (
    CANDIDATE_IDS,
    DYNAMIC_QINT8_QNNPACK,
    FLOAT16_EAGER_CPU,
    FLOAT32_REFERENCE,
    CandidateUnavailableError,
    FrozenProducerPayload,
    build_precision_candidate,
    build_precision_candidate_from_payload,
    candidate_storage_summary,
    extract_frozen_producer_payload,
    profile_candidate_operator,
    serialize_candidate_numeric_payload,
)
from neurodecodekit.models.tiny_causal_encoder import (
    load_tiny_causal_encoder_checkpoint,
)
from neurodecodekit.training.precision_runtime_fixture import (
    LoadedPrecisionRuntimePartition,
    load_precision_runtime_manifest,
    load_precision_runtime_partition,
)


REPORT_SCHEMA_NAME = "b2q-local-precision-runtime-gate"
REPORT_SCHEMA_VERSION = 0
AUDIT_SCHEMA_NAME = "b2q-local-precision-runtime-audit"
AUDIT_SCHEMA_VERSION = 0
PROOF_POSTURE = "target_free_synthetic_platform_bound_precision_runtime_only"
CONTRACT_RELATIVE_PATH = Path("registries/local_precision_runtime_contract.v0.json")
AUTHORIZATION_RELATIVE_PATH = Path("registries/loop24_authorization_decision.v0.json")
REGISTERED_CONTRACT_SHA256 = (
    "58e9d5407fef9419bc3bb0dc8cd3fa68d36dd238cb636d2f833dd9c5c6c3ae5d"
)
REGISTERED_CHECKPOINT_SHA256 = (
    "75fd5e3c549f28af819f358f3e12d4ee3e3b42a4d87f645fb8aa36b57c7bfab1"
)
REGISTERED_PARAMETER_PAYLOAD_SHA256 = (
    "d7f4c1bdf7cb36ead01cc9571eb4167083f48537b5930b3dfc0fe7852a3f2d98"
)
REGISTERED_MODEL_CONFIG_SHA256 = (
    "8b331beeb236eaf54a938c5aca6b12c59d81fb87e28d2ff92e5edf66ef26dcc2"
)
REGISTERED_DECODER_CONFIG_SHA256 = (
    "3a70a3e7890487eb8a1d5c871eb8540e8265ea524a62a5d3be8c5ac55f760544"
)
REGISTERED_BLANK_INTERCEPT = 5.130175197684084
REGISTERED_BLANK_PAYLOAD_SHA256 = (
    "10ed3f4fd2bf29841aebe31b81d7726910361df5ecc10a2c29ae7de4563d174f"
)
BLANK_ID = 0
BEAM_WIDTH = 8
MAX_PREFIX_LENGTH = 12
TIMED_PATHS = (
    "producer_frame_normalize_encode_probe",
    "fixed_float64_decoder_frame_update",
    "full_incremental_frame_pipeline",
)
THREAD_ENVIRONMENT = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
FORBIDDEN_COUNTERS = (
    "training_runs",
    "parameter_updates",
    "target_label_text_reads",
    "consumed_seed_2203_reads",
    "consumed_seed_2303_reads",
    "consumed_seed_2353_reads",
    "s7_s21_reads",
    "real_data_reads",
    "external_network_calls",
    "rw3_source_chunk_operations",
    "rw3_socket_stream_board_xdf_operations",
)


class Loop24GateRefusal(RuntimeError):
    """Fail-closed refusal carrying one exact registered reason ID."""

    def __init__(self, refusal_id: str, message: str) -> None:
        super().__init__(message)
        self.refusal_id = refusal_id


@dataclass(frozen=True)
class LocalPrecisionRuntimeCaps:
    maximum_fixture_bytes_total: int = 512 * 1024
    maximum_checkpoint_bytes: int = 64 * 1024
    maximum_candidate_serialized_bytes_each: int = 64 * 1024
    maximum_working_array_bytes: int = 32 * 1024 * 1024
    maximum_report_bytes_total: int = 1 * 1024 * 1024
    maximum_generated_bytes_total: int = 4 * 1024 * 1024
    maximum_internal_runtime_sec: float = 60.0
    maximum_peak_rss_bytes_each_worker: int = 1 * 1024 * 1024 * 1024
    maximum_worker_processes_spawned: int = 48
    cpu_threads: int = 1
    maximum_concurrent_workers: int = 1

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FrameBundle:
    """Target-free complete frames and item boundaries held only in memory."""

    frames: Any
    frame_start_samples: Any
    frame_end_samples: Any
    item_ids: tuple[str, ...]
    input_lengths: tuple[int, ...]
    group_lengths: tuple[int, ...]
    source_sampling_rate_hz: float

    @property
    def frame_count(self) -> int:
        return int(self.frames.shape[0])

    @property
    def array_bytes(self) -> int:
        return int(
            self.frames.nbytes
            + self.frame_start_samples.nbytes
            + self.frame_end_samples.nbytes
        )

    @property
    def duration_sec(self) -> float:
        return sum(self.input_lengths) / self.source_sampling_rate_hz


def registered_local_precision_runtime_caps() -> LocalPrecisionRuntimeCaps:
    """Return resource limits and verify them against the frozen contract."""

    caps = LocalPrecisionRuntimeCaps()
    contract = _load_contract()
    registered = contract["resource_caps"]
    expected = {
        "maximum_fixture_bytes_total": registered["maximum_fixture_bytes_total"],
        "maximum_checkpoint_bytes": registered["maximum_checkpoint_bytes"],
        "maximum_candidate_serialized_bytes_each": registered[
            "maximum_candidate_serialized_bytes_each"
        ],
        "maximum_working_array_bytes": registered["maximum_working_array_bytes"],
        "maximum_report_bytes_total": registered["maximum_report_bytes_total"],
        "maximum_generated_bytes_total": registered["maximum_generated_bytes_total"],
        "maximum_internal_runtime_sec": registered["maximum_internal_runtime_sec"],
        "maximum_peak_rss_bytes_each_worker": registered[
            "maximum_peak_rss_bytes_each_worker"
        ],
        "maximum_worker_processes_spawned": registered[
            "maximum_worker_processes_spawned"
        ],
        "cpu_threads": registered["cpu_threads"],
        "maximum_concurrent_workers": registered["maximum_concurrent_workers"],
    }
    for name, value in expected.items():
        if getattr(caps, name) != value:
            raise RuntimeError(f"Loop 24 resource cap drifted at {name}")
    return caps


def run_local_precision_runtime_gate(
    *,
    fixture_manifest_path: str | Path,
    checkpoint_path: str | Path,
    out_dir: str | Path,
    require_registered_environment: bool = True,
    require_registered_fixture: bool = True,
    require_registered_checkpoint: bool = True,
    enforce_authorized_output_root: bool = True,
    timing_worker_runner: Callable[[FrozenProducerPayload, str, FrameBundle], dict[str, Any]]
    | None = None,
) -> dict[str, Any]:
    """Execute selection and conditional qualification under the frozen contract."""

    started_at = time.perf_counter()
    caps = registered_local_precision_runtime_caps()
    output_dir = Path(out_dir)
    _validate_output_directory(
        output_dir,
        enforce_authorized_output_root=enforce_authorized_output_root,
    )
    counters = _new_access_counters()
    events: list[dict[str, Any]] = []

    contract, authorization, environment = _validate_prerun_boundary(
        require_registered_environment=require_registered_environment,
    )
    _record_stage(
        events,
        contract,
        0,
        action="contract_authorization_source_environment_validated",
        checkpoint_reads=0,
        partition_opens=0,
    )

    fixture_manifest = load_precision_runtime_manifest(
        fixture_manifest_path,
        max_total_bytes=caps.maximum_fixture_bytes_total,
        require_registered_protocol=require_registered_fixture,
    )
    counters["manifest_metadata_reads"] += 1
    _record_stage(
        events,
        contract,
        1,
        action="manifest_hashed_and_validated_without_npz_member_open",
        partition_array_members_opened=0,
    )

    checkpoint_file = Path(checkpoint_path)
    producer, checkpoint = _load_and_validate_checkpoint(
        checkpoint_file,
        caps=caps,
        require_registered_checkpoint=require_registered_checkpoint,
    )
    counters["checkpoint_file_reads"] += 1
    _record_stage(
        events,
        contract,
        2,
        action="checkpoint_hashed_and_loaded_once_without_training",
        checkpoint_sha256=checkpoint["sha256"],
    )

    selection_partition = load_precision_runtime_partition(
        fixture_manifest_path,
        "selection",
        max_total_bytes=caps.maximum_fixture_bytes_total,
        require_registered_protocol=require_registered_fixture,
    )
    counters["selection_partition_opens"] += 1
    selection_frames = _extract_frame_bundle(producer, selection_partition)
    _validate_working_bytes(
        selection_partition,
        selection_frames,
        caps.maximum_working_array_bytes,
    )
    _record_stage(
        events,
        contract,
        3,
        action="selection_input_only_partition_opened_once",
        opened_members=list(selection_partition.opened_members),
        items=len(selection_partition.item_ids),
        frames=selection_frames.frame_count,
    )

    source_payload = extract_frozen_producer_payload(producer)
    candidates: dict[str, Any] = {}
    candidate_records: dict[str, dict[str, Any]] = {}
    payload_bytes: dict[str, bytes] = {}
    for candidate_id in CANDIDATE_IDS:
        try:
            candidate = build_precision_candidate(producer, candidate_id)
            storage = candidate_storage_summary(candidate)
            payload = serialize_candidate_numeric_payload(candidate)
            if len(payload) > caps.maximum_candidate_serialized_bytes_each:
                raise Loop24GateRefusal(
                    "resource_cap_exceeded",
                    f"{candidate_id} numeric payload exceeds the frozen cap",
                )
            candidates[candidate_id] = candidate
            payload_bytes[candidate_id] = payload
            candidate_records[candidate_id] = {
                "candidate_id": candidate_id,
                "status": "available",
                "provenance": candidate.provenance.to_dict(),
                "storage": storage,
                "profiler": None,
                "correctness": None,
                "selection_eligibility": None,
            }
            counters["candidate_conversions"] += 1
        except CandidateUnavailableError as exc:
            candidate_records[candidate_id] = _unavailable_candidate_record(
                candidate_id,
                refusal_id=exc.refusal_id,
                message=str(exc),
            )
    if FLOAT32_REFERENCE not in candidates:
        raise Loop24GateRefusal(
            "candidate_dtype_or_module_contract_mismatch",
            "the float32 reference candidate is unavailable",
        )
    _record_stage(
        events,
        contract,
        4,
        action="all_three_candidate_statuses_frozen_without_parameter_update",
        statuses={key: value["status"] for key, value in candidate_records.items()},
        conversions=counters["candidate_conversions"],
    )

    reference_replays = []
    for _ in range(int(contract["correctness_gates"]["reference_replay_repeats"])):
        reference_replays.append(
            _run_candidate_replay(
                candidates[FLOAT32_REFERENCE],
                selection_frames,
                blank_intercept=REGISTERED_BLANK_INTERCEPT,
            )
        )
        counters["reference_inference_runs"] += 1
    reference_hashes = [row["payload_sha256"] for row in reference_replays]
    if len(set(reference_hashes)) != 1:
        raise Loop24GateRefusal(
            "reference_replay_nondeterministic",
            "float32 reference replay changed bits across three repeats",
        )
    reference_output = reference_replays[0]
    candidate_records[FLOAT32_REFERENCE]["correctness"] = {
        "passed": True,
        "reference_replay_hashes": reference_hashes,
        "reference_replay_bitwise_exact": True,
        **_replay_public_summary(reference_output),
    }
    for candidate_id in CANDIDATE_IDS[1:]:
        if candidate_id not in candidates:
            continue
        try:
            output = _run_candidate_replay(
                candidates[candidate_id],
                selection_frames,
                blank_intercept=REGISTERED_BLANK_INTERCEPT,
            )
            counters["candidate_inference_runs"] += 1
            comparison = _compare_candidate_replay(
                reference_output,
                output,
                contract["correctness_gates"]["numeric_tolerances"],
            )
            candidate_records[candidate_id]["correctness"] = comparison
        except (RuntimeError, ValueError) as exc:
            candidate_records[candidate_id]["correctness"] = {
                "passed": False,
                "refusal_id": "candidate_output_nonfinite",
                "message": str(exc),
            }
    _record_stage(
        events,
        contract,
        5,
        action="reference_repeats_and_candidate_correctness_completed",
        reference_payload_sha256=reference_output["payload_sha256"],
        correctness={
            key: bool((value.get("correctness") or {}).get("passed"))
            for key, value in candidate_records.items()
        },
    )

    first_frame = selection_frames.frames[0]
    for candidate_id, candidate in candidates.items():
        try:
            profiler = profile_candidate_operator(candidate, first_frame)
            candidate_records[candidate_id]["profiler"] = profiler
            if profiler["required"]:
                counters["profiler_runs"] += 1
        except CandidateUnavailableError as exc:
            candidate_records[candidate_id]["profiler"] = {
                "required": candidate_id == DYNAMIC_QINT8_QNNPACK,
                "passed": False,
                "refusal_id": exc.refusal_id,
                "message": str(exc),
                "raw_trace_saved": False,
            }
    _record_stage(
        events,
        contract,
        6,
        action="untimed_operator_provenance_completed_without_raw_trace",
        profiler_runs=counters["profiler_runs"],
    )

    worker_runner = timing_worker_runner or _run_timing_worker
    selection_timing_rows = _run_balanced_timing_protocol(
        contract["benchmark_protocol"]["selection_candidate_orders"],
        source_payload=source_payload,
        frames=selection_frames,
        candidate_records=candidate_records,
        worker_runner=worker_runner,
        label="selection",
        counters=counters,
        caps=caps,
    )
    selection_timing = _aggregate_timing_rows(
        selection_timing_rows,
        candidate_ids=CANDIDATE_IDS,
        reference_id=FLOAT32_REFERENCE,
        bootstrap_seed=int(contract["benchmark_protocol"]["paired_bootstrap_seed"]),
        bootstrap_resamples=int(
            contract["benchmark_protocol"]["paired_bootstrap_resamples"]
        ),
        stride_samples=int(producer.stride),
        sampling_rate_hz=float(producer.source_sampling_rate_hz),
    )
    _record_stage(
        events,
        contract,
        7,
        action="twelve_balanced_fresh_sequential_worker_rounds_completed",
        worker_processes=counters["timing_worker_processes"],
        raw_rows=len(selection_timing_rows),
    )

    selection = _select_candidate(
        candidate_records=candidate_records,
        timing=selection_timing,
        contract=contract,
    )
    selection_core = {
        "schema": {"name": "b2q-loop24-selection-decision", "version": 0},
        "contract_sha256": REGISTERED_CONTRACT_SHA256,
        "fixture_manifest_sha256": _file_sha256(Path(fixture_manifest_path)),
        "checkpoint_sha256": checkpoint["sha256"],
        "selection_partition_sha256": fixture_manifest["partitions"]["selection"][
            "sha256"
        ],
        "candidate_decision": selection,
        "qualification_opened": False,
        "thresholds_frozen": contract["selection_rules"],
        "targets_labels_text_read": 0,
    }
    selection_sha256 = _sha256_json(selection_core)
    selection_document = {**selection_core, "selection_document_sha256": selection_sha256}
    output_dir.mkdir(parents=True, exist_ok=False)
    selection_path = output_dir / "selection.json"
    selection_path.write_bytes(_stable_json_bytes(selection_document))
    _record_stage(
        events,
        contract,
        8,
        action="selection_report_and_candidate_decision_written_and_hashed",
        selection_document_sha256=selection_sha256,
        provisional_replacement=selection["provisional_replacement_candidate"],
    )

    qualification: dict[str, Any]
    selected_candidate_id = selection["provisional_replacement_candidate"]
    if selected_candidate_id is None:
        qualification = {
            "opened": False,
            "reason": "no_nonreference_replacement_candidate_selected",
            "candidate_id": None,
            "correctness": None,
            "timing": None,
            "passed": None,
        }
        _record_stage(
            events,
            contract,
            9,
            action="qualification_physically_unopened_no_replacement_candidate",
            qualification_partition_opens=0,
        )
        _record_stage(
            events,
            contract,
            10,
            action="qualification_comparison_skipped_by_frozen_rule",
            compared_candidates=[],
        )
    else:
        qualification_partition = load_precision_runtime_partition(
            fixture_manifest_path,
            "qualification",
            max_total_bytes=caps.maximum_fixture_bytes_total,
            require_registered_protocol=require_registered_fixture,
        )
        counters["qualification_partition_opens"] += 1
        qualification_frames = _extract_frame_bundle(producer, qualification_partition)
        _validate_working_bytes(
            qualification_partition,
            qualification_frames,
            caps.maximum_working_array_bytes,
        )
        _record_stage(
            events,
            contract,
            9,
            action="qualification_input_only_partition_opened_once_after_selection_freeze",
            candidate_id=selected_candidate_id,
            opened_members=list(qualification_partition.opened_members),
        )
        qualification_reference = _run_candidate_replay(
            candidates[FLOAT32_REFERENCE],
            qualification_frames,
            blank_intercept=REGISTERED_BLANK_INTERCEPT,
        )
        qualification_candidate = _run_candidate_replay(
            candidates[selected_candidate_id],
            qualification_frames,
            blank_intercept=REGISTERED_BLANK_INTERCEPT,
        )
        counters["reference_inference_runs"] += 1
        counters["candidate_inference_runs"] += 1
        correctness = _compare_candidate_replay(
            qualification_reference,
            qualification_candidate,
            contract["correctness_gates"]["numeric_tolerances"],
        )
        qualification_orders = [
            [
                FLOAT32_REFERENCE if value == FLOAT32_REFERENCE else selected_candidate_id
                for value in order
            ]
            for order in contract["benchmark_protocol"]["qualification_orders"]
        ]
        qualification_timing_rows = _run_balanced_timing_protocol(
            qualification_orders,
            source_payload=source_payload,
            frames=qualification_frames,
            candidate_records=candidate_records,
            worker_runner=worker_runner,
            label="qualification",
            counters=counters,
            caps=caps,
        )
        qualification_timing = _aggregate_timing_rows(
            qualification_timing_rows,
            candidate_ids=(FLOAT32_REFERENCE, selected_candidate_id),
            reference_id=FLOAT32_REFERENCE,
            bootstrap_seed=int(contract["benchmark_protocol"]["paired_bootstrap_seed"]),
            bootstrap_resamples=int(
                contract["benchmark_protocol"]["paired_bootstrap_resamples"]
            ),
            stride_samples=int(producer.stride),
            sampling_rate_hz=float(producer.source_sampling_rate_hz),
        )
        qualification_thresholds = _replacement_threshold_result(
            candidate_id=selected_candidate_id,
            candidate_records=candidate_records,
            timing=qualification_timing,
            contract=contract,
            include_storage=False,
        )
        passed = bool(correctness["passed"] and qualification_thresholds["passed"])
        qualification = {
            "opened": True,
            "reason": "provisional_replacement_candidate_selected",
            "candidate_id": selected_candidate_id,
            "correctness": correctness,
            "timing": qualification_timing,
            "raw_timing_rows": qualification_timing_rows,
            "replacement_thresholds": qualification_thresholds,
            "passed": passed,
        }
        _record_stage(
            events,
            contract,
            10,
            action="reference_and_frozen_selected_candidate_compared_once",
            compared_candidates=[FLOAT32_REFERENCE, selected_candidate_id],
            passed=passed,
        )

    decision = _final_decision(selection, qualification)
    elapsed = time.perf_counter() - started_at
    worker_peak_rss = max(
        [
            int(row.get("worker_peak_rss_bytes") or 0)
            for row in selection_timing_rows
            + (qualification.get("raw_timing_rows") or [])
        ]
        or [0]
    )
    resource_passed = bool(
        elapsed <= caps.maximum_internal_runtime_sec
        and counters["timing_worker_processes"]
        <= caps.maximum_worker_processes_spawned
        and worker_peak_rss <= caps.maximum_peak_rss_bytes_each_worker
    )
    available_candidate_ids = [
        candidate_id
        for candidate_id, row in candidate_records.items()
        if row["status"] == "available"
    ]
    selection_timing_passed = all(
        selection_timing["candidates"][candidate_id]["status"] == "measured"
        for candidate_id in available_candidate_ids
    )
    qualification_timing_passed = bool(
        not qualification["opened"]
        or all(
            qualification["timing"]["candidates"][candidate_id]["status"]
            == "measured"
            for candidate_id in (FLOAT32_REFERENCE, selected_candidate_id)
        )
    )
    timing_protocol_passed = bool(
        selection_timing_passed and qualification_timing_passed
    )
    gate_passed = bool(resource_passed and timing_protocol_passed)
    if not resource_passed:
        decision = "park_resource_cap_exceeded"
    elif not timing_protocol_passed:
        decision = "park_timer_protocol_or_balanced_order_mismatch"

    _record_stage(
        events,
        contract,
        11,
        action="reports_ready_without_partition_reopen",
        final_decision=decision,
        selection_partition_opens=counters["selection_partition_opens"],
        qualification_partition_opens=counters["qualification_partition_opens"],
    )
    _validate_access_boundary(counters)
    _validate_event_sequence(events, contract)

    warnings_out = _collect_warnings(candidate_records)
    if not timing_protocol_passed:
        warnings_out.append(
            "One or more available candidates did not complete every frozen timing round."
        )
    unavailable_fields = sorted(
        {
            "energy_measurement",
            "hardware_accumulation_dtype_float16",
            "thermal_state",
            "cpu_frequency",
            *(
                ["qualification_metrics"]
                if not qualification["opened"]
                else []
            ),
        }
    )
    report: dict[str, Any] = {
        "schema": {"name": REPORT_SCHEMA_NAME, "version": REPORT_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "gate_passed": gate_passed,
        "decision": decision,
        "contract": {
            "id": contract["contract_id"],
            "schema_version": contract["schema_version"],
            "sha256": REGISTERED_CONTRACT_SHA256,
            "preregistration_commit": "186bb6f",
        },
        "authorization": {
            "decision_id": authorization["decision_id"],
            "proof_posture": authorization["proof_posture"],
            "target_free_loop24_authorized": True,
            "real_data_authorized": False,
            "training_authorized": False,
            "rw3_authorized": False,
        },
        "source_commit": environment["git_commit"],
        "environment": environment,
        "fixture": {
            "manifest_file": Path(fixture_manifest_path).name,
            "manifest_sha256": _file_sha256(Path(fixture_manifest_path)),
            "bytes": fixture_manifest["artifacts"]["total_bytes"],
            "selection": {
                "seed": fixture_manifest["partitions"]["selection"]["seed"],
                "items": fixture_manifest["partitions"]["selection"]["items"],
                "frames": selection_frames.frame_count,
                "partition_sha256": fixture_manifest["partitions"]["selection"][
                    "sha256"
                ],
            },
            "qualification": {
                "seed": fixture_manifest["partitions"]["qualification"]["seed"],
                "items": fixture_manifest["partitions"]["qualification"]["items"],
                "opened": qualification["opened"],
                "partition_sha256": fixture_manifest["partitions"]["qualification"][
                    "sha256"
                ],
            },
            "target_free": True,
        },
        "checkpoint": checkpoint,
        "blank_intercept": {
            "value": REGISTERED_BLANK_INTERCEPT,
            "dtype": "float64",
            "parameter_payload_sha256": REGISTERED_BLANK_PAYLOAD_SHA256,
            "config_sha256": BLANK_CALIBRATION_CONFIG_SHA256,
            "recalibrated": False,
        },
        "decoder": {
            **_decoder_config(),
            "config_sha256": REGISTERED_DECODER_CONFIG_SHA256,
            "registered_runtime_semantics": contract["reference_pipeline"]["decoder"],
        },
        "producer": {
            "name": contract["reference_pipeline"]["producer_name"],
            "causal": True,
            "right_context_samples": 0,
            "required_context_samples": int(producer.kernel_size),
            "end_to_end_latency_measured": False,
            "logical_parameter_count": int(producer.trainable_parameter_count),
        },
        "candidates": candidate_records,
        "selection": {
            **selection,
            "document_file": selection_path.name,
            "document_sha256": _file_sha256(selection_path),
            "timing": selection_timing,
            "raw_timing_rows": selection_timing_rows,
        },
        "qualification": qualification,
        "access": {"counters": counters, "ordered_events": events},
        "resources": {
            "caps": caps.to_dict(),
            "input_bytes": int(
                fixture_manifest["artifacts"]["total_bytes"] + checkpoint["bytes"]
            ),
            "working_array_bytes": int(
                selection_partition.array_bytes + selection_frames.array_bytes
            ),
            "runtime_sec": round(elapsed, 6),
            "runtime_scope": "through_decision_before_final_artifact_serialization",
            "parent_peak_rss_bytes": _peak_rss_bytes(),
            "maximum_worker_peak_rss_bytes": worker_peak_rss,
            "timing_worker_processes": counters["timing_worker_processes"],
            "report_bytes": 0,
            "output_bytes": 0,
            "total_generated_bytes": 0,
            "resource_caps_passed": resource_passed,
            "timing_protocol_passed": timing_protocol_passed,
            "passed": gate_passed,
        },
        "energy": {
            "status": "unavailable_not_authorized_for_this_execution",
            "measured": False,
            "sudo_prompted": False,
            "selection_used_energy": False,
        },
        "warnings": warnings_out,
        "unavailable_fields": unavailable_fields,
        "claim_boundary": [
            "This gate measures one frozen target-free synthetic pipeline on one local CPU.",
            "A smaller payload is not proof of faster or integer-only execution.",
            "A lower local runtime is not end-to-end text latency or cross-device energy efficiency.",
            "No neural advantage, real-data accuracy, CER/WER improvement, unseen-person transfer, useful EEG, portable-hardware, arbitrary-thought, assistive, diagnostic, or clinical claim follows.",
        ],
        "artifacts": {
            "selection": selection_path.name,
            "candidate_payloads": {},
            "report_json": "gate.json",
            "report_markdown": "gate.md",
            "audit_json": "audit.json",
            "sizes": {},
        },
    }
    _write_final_artifacts(
        output_dir=output_dir,
        report=report,
        payload_bytes=payload_bytes,
        fixture_bytes=int(fixture_manifest["artifacts"]["total_bytes"]),
        caps=caps,
    )
    return report


def inspect_local_precision_runtime_report(path: str | Path) -> dict[str, Any]:
    """Strictly validate a saved report and its measured audit sidecar."""

    report_path = Path(path)
    caps = registered_local_precision_runtime_caps()
    if not report_path.is_file() or report_path.stat().st_size > caps.maximum_report_bytes_total:
        raise ValueError("Loop 24 report is missing or exceeds the report cap")
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Loop 24 report is not valid JSON") from exc
    if not isinstance(report, dict):
        raise ValueError("Loop 24 report must be an object")
    if report.get("schema") != {"name": REPORT_SCHEMA_NAME, "version": REPORT_SCHEMA_VERSION}:
        raise ValueError("unsupported Loop 24 report schema")
    if report.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("Loop 24 report proof posture is invalid")
    if (report.get("contract") or {}).get("sha256") != REGISTERED_CONTRACT_SHA256:
        raise ValueError("Loop 24 report contract hash mismatch")
    access = report.get("access") or {}
    counters = access.get("counters") or {}
    if set(counters) != set(_new_access_counters()):
        raise ValueError("Loop 24 report access counter set is incomplete")
    _validate_access_boundary(counters)
    if counters["selection_partition_opens"] != 1:
        raise ValueError("Loop 24 report must record one selection partition open")
    qualification = report.get("qualification") or {}
    expected_qualification_opens = 1 if qualification.get("opened") else 0
    if counters["qualification_partition_opens"] != expected_qualification_opens:
        raise ValueError("Loop 24 qualification access count is inconsistent")
    if not (report.get("producer") or {}).get("causal"):
        raise ValueError("Loop 24 report must preserve producer causality")
    if (report.get("producer") or {}).get("right_context_samples") != 0:
        raise ValueError("Loop 24 report right context drifted")
    if (report.get("producer") or {}).get("end_to_end_latency_measured") is not False:
        raise ValueError("Loop 24 report end-to-end latency field is invalid")
    if not report.get("warnings") or not report.get("unavailable_fields"):
        raise ValueError("Loop 24 report omits warnings or unavailable fields")
    resources = report.get("resources") or {}
    if resources.get("output_bytes", 0) > caps.maximum_generated_bytes_total:
        raise ValueError("Loop 24 report output exceeds generated-byte cap")
    if resources.get("report_bytes", 0) > caps.maximum_report_bytes_total:
        raise ValueError("Loop 24 report bytes exceed report cap")
    audit_path = report_path.parent / str(report["artifacts"]["audit_json"])
    try:
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Loop 24 measured audit is not valid JSON") from exc
    if audit.get("schema") != {"name": AUDIT_SCHEMA_NAME, "version": AUDIT_SCHEMA_VERSION}:
        raise ValueError("unsupported Loop 24 measured audit schema")
    if audit.get("report_sha256") != _file_sha256(report_path):
        raise ValueError("Loop 24 report/audit hash binding mismatch")
    if audit.get("access_counters") != counters:
        raise ValueError("Loop 24 report/audit access counters differ")
    contract = _load_contract()
    try:
        _validate_event_sequence(access.get("ordered_events") or [], contract)
    except Loop24GateRefusal as exc:
        raise ValueError("Loop 24 report access-event sequence is invalid") from exc
    audit_artifacts = audit.get("artifacts") or {}
    if not isinstance(audit_artifacts, dict) or not audit_artifacts:
        raise ValueError("Loop 24 measured audit omits artifact bindings")
    measured_output_bytes = 0
    for file_name, identity in audit_artifacts.items():
        if Path(file_name).name != file_name or file_name in ("", ".", ".."):
            raise ValueError("Loop 24 measured audit contains an unsafe artifact name")
        artifact_path = report_path.parent / file_name
        if not artifact_path.is_file():
            raise ValueError(f"Loop 24 artifact is missing: {file_name}")
        actual_bytes = int(artifact_path.stat().st_size)
        if identity.get("bytes") != actual_bytes:
            raise ValueError(f"Loop 24 artifact byte count mismatch: {file_name}")
        measured_output_bytes += actual_bytes
        expected_hash = identity.get("sha256")
        if file_name == str(report["artifacts"]["audit_json"]):
            if expected_hash is not None:
                raise ValueError("Loop 24 audit sidecar must not claim a self-hash")
        elif expected_hash != _file_sha256(artifact_path):
            raise ValueError(f"Loop 24 artifact hash mismatch: {file_name}")
    audit_resources = audit.get("resources") or {}
    if audit_resources.get("output_bytes") != measured_output_bytes:
        raise ValueError("Loop 24 measured output-byte accounting mismatch")
    if resources.get("output_bytes") != measured_output_bytes:
        raise ValueError("Loop 24 report output-byte accounting mismatch")
    if audit_resources.get("report_bytes") != sum(
        int(audit_artifacts[name]["bytes"])
        for name in ("gate.json", "gate.md", "audit.json")
    ):
        raise ValueError("Loop 24 report-artifact byte accounting mismatch")
    if audit_resources.get("report_bytes") > caps.maximum_report_bytes_total:
        raise ValueError("Loop 24 measured reports exceed the report cap")
    if audit_resources.get("total_generated_bytes") > caps.maximum_generated_bytes_total:
        raise ValueError("Loop 24 measured generated bytes exceed the total cap")
    if resources.get("report_bytes") != audit_resources.get("report_bytes"):
        raise ValueError("Loop 24 report/audit report-byte values differ")
    if resources.get("total_generated_bytes") != audit_resources.get(
        "total_generated_bytes"
    ):
        raise ValueError("Loop 24 report/audit generated-byte values differ")
    reported_sizes = report.get("artifacts", {}).get("sizes") or {}
    measured_sizes = {
        name: int(identity["bytes"]) for name, identity in audit_artifacts.items()
    }
    if reported_sizes != measured_sizes:
        raise ValueError("Loop 24 report/audit artifact sizes differ")
    selection_path = report_path.parent / str(report["artifacts"]["selection"])
    if (report.get("selection") or {}).get("document_sha256") != _file_sha256(
        selection_path
    ):
        raise ValueError("Loop 24 selection decision hash binding mismatch")
    selection_document = _load_json_object(selection_path, "Loop 24 selection decision")
    selection_core = dict(selection_document)
    internal_selection_hash = selection_core.pop("selection_document_sha256", None)
    if internal_selection_hash != _sha256_json(selection_core):
        raise ValueError("Loop 24 selection decision internal hash mismatch")
    if selection_core.get("contract_sha256") != REGISTERED_CONTRACT_SHA256:
        raise ValueError("Loop 24 selection decision contract hash mismatch")
    if selection_core.get("qualification_opened") is not False:
        raise ValueError("Loop 24 selection decision was not frozen before qualification")
    if selection_core.get("targets_labels_text_read") != 0:
        raise ValueError("Loop 24 selection decision reports forbidden target access")
    candidate_decision = selection_core.get("candidate_decision") or {}
    if any(report["selection"].get(key) != value for key, value in candidate_decision.items()):
        raise ValueError("Loop 24 report differs from its frozen selection decision")
    try:
        _validate_report_privacy(
            report_path.read_bytes(),
            (
                report_path.parent / str(report["artifacts"]["report_markdown"])
            ).read_bytes(),
            audit_path.read_bytes(),
        )
    except Loop24GateRefusal as exc:
        raise ValueError("Loop 24 report contains forbidden private fields") from exc
    return {
        "schema": report["schema"],
        "proof_posture": report["proof_posture"],
        "gate_passed": report["gate_passed"],
        "decision": report["decision"],
        "selected_candidate": report["selection"][
            "provisional_replacement_candidate"
        ],
        "qualification_opened": qualification["opened"],
        "producer_causal": report["producer"]["causal"],
        "end_to_end_latency_measured": report["producer"][
            "end_to_end_latency_measured"
        ],
        "runtime_sec": resources["runtime_sec"],
        "input_bytes": resources["input_bytes"],
        "output_bytes": resources["output_bytes"],
        "warnings": report["warnings"],
        "unavailable_fields": report["unavailable_fields"],
        "access_counters": counters,
        "report_sha256": _file_sha256(report_path),
    }


def _validate_prerun_boundary(
    *,
    require_registered_environment: bool,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    contract_path = _repo_root() / CONTRACT_RELATIVE_PATH
    authorization_path = _repo_root() / AUTHORIZATION_RELATIVE_PATH
    contract = _load_json_object(contract_path, "Loop 24 machine contract")
    authorization = _load_json_object(
        authorization_path,
        "Loop 24 authorization decision",
    )
    if _file_sha256(contract_path) != REGISTERED_CONTRACT_SHA256:
        raise Loop24GateRefusal(
            "contract_or_source_binding_mismatch",
            "Loop 24 machine contract hash drifted",
        )
    binding = authorization.get("authorized_contract") or {}
    if binding.get("contract_sha256") != REGISTERED_CONTRACT_SHA256:
        raise Loop24GateRefusal(
            "loop24_execution_not_authorized",
            "Loop 24 authorization does not bind the frozen contract hash",
        )
    allowed_true = {
        "loop24_implementation_authorized_now",
        "target_free_fixture_generation_authorized_now",
        "frozen_checkpoint_validation_and_open_authorized_now",
        "registered_candidate_conversion_authorized_now",
        "registered_model_inference_authorized_now",
        "registered_selection_authorized_now",
        "conditional_one_time_qualification_authorized_now",
        "report_and_cli_implementation_authorized_now",
    }
    flags = authorization.get("authorization") or {}
    if not allowed_true.issubset(flags) or any(flags[name] is not True for name in allowed_true):
        raise Loop24GateRefusal(
            "loop24_execution_not_authorized",
            "Loop 24 target-free authorization fields are incomplete",
        )
    forbidden_true = set(flags) - allowed_true
    if any(flags[name] is not False for name in forbidden_true):
        raise Loop24GateRefusal(
            "loop24_execution_not_authorized",
            "Loop 24 authorization includes a forbidden scope",
        )
    for row in contract["source_bindings"]:
        path = _repo_root() / row["path"]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["file_sha256_at_parent"]:
            raise Loop24GateRefusal(
                "contract_or_source_binding_mismatch",
                f"source binding hash drifted: {row['path']}",
            )
        git_blob = hashlib.sha1(  # noqa: S324 - Git object identity, not security
            f"blob {len(payload)}\0".encode("ascii") + payload
        ).hexdigest()
        if git_blob != row["git_blob_sha1_at_parent"]:
            raise Loop24GateRefusal(
                "contract_or_source_binding_mismatch",
                f"source binding Git blob drifted: {row['path']}",
            )
    if registered_blank_intercept_config().config_sha256 != BLANK_CALIBRATION_CONFIG_SHA256:
        raise Loop24GateRefusal(
            "blank_intercept_value_config_or_hash_mismatch",
            "blank-intercept config hash drifted",
        )
    if _sha256_json(
        {
            "dtype": "float64",
            "intercept": REGISTERED_BLANK_INTERCEPT,
            "shape": [1],
        }
    ) != REGISTERED_BLANK_PAYLOAD_SHA256:
        raise Loop24GateRefusal(
            "blank_intercept_value_config_or_hash_mismatch",
            "blank-intercept payload hash drifted",
        )
    if _sha256_json(_decoder_config()) != REGISTERED_DECODER_CONFIG_SHA256:
        raise Loop24GateRefusal(
            "decoder_config_or_semantics_mismatch",
            "fixed CTC decoder config hash drifted",
        )
    environment = _environment_summary()
    if require_registered_environment:
        _require_registered_environment(environment, contract)
        _require_clean_committed_execution(environment)
    return contract, authorization, environment


def _load_and_validate_checkpoint(
    path: Path,
    *,
    caps: LocalPrecisionRuntimeCaps,
    require_registered_checkpoint: bool,
):
    started_at = time.perf_counter()
    if not path.is_file():
        raise Loop24GateRefusal(
            "checkpoint_file_or_payload_hash_mismatch",
            "Loop 24 checkpoint file is missing",
        )
    size = int(path.stat().st_size)
    if size > caps.maximum_checkpoint_bytes:
        raise Loop24GateRefusal(
            "resource_cap_exceeded",
            "Loop 24 checkpoint exceeds the frozen byte cap",
        )
    file_sha256 = _file_sha256(path)
    if require_registered_checkpoint and file_sha256 != REGISTERED_CHECKPOINT_SHA256:
        raise Loop24GateRefusal(
            "checkpoint_file_or_payload_hash_mismatch",
            "Loop 24 checkpoint file hash does not match the frozen identity",
        )
    try:
        producer, metadata = load_tiny_causal_encoder_checkpoint(path)
    except (OSError, RuntimeError, ValueError) as exc:
        raise Loop24GateRefusal(
            "checkpoint_file_or_payload_hash_mismatch",
            f"Loop 24 checkpoint cannot be loaded safely: {exc}",
        ) from exc
    match = bool(
        file_sha256 == REGISTERED_CHECKPOINT_SHA256
        and producer.parameter_payload_sha256 == REGISTERED_PARAMETER_PAYLOAD_SHA256
        and metadata.get("config_sha256") == REGISTERED_MODEL_CONFIG_SHA256
        and int(producer.trainable_parameter_count) == 1130
    )
    if require_registered_checkpoint and not match:
        raise Loop24GateRefusal(
            "model_config_or_parameter_count_mismatch",
            "Loop 24 checkpoint metadata or parameter identity drifted",
        )
    geometry = {
        "n_channels": int(producer.n_channels),
        "sampling_rate_hz": float(producer.source_sampling_rate_hz),
        "kernel_size_samples": int(producer.kernel_size),
        "stride_samples": int(producer.stride),
        "embedding_dim": int(producer.embedding_dim),
        "output_classes": int(producer.n_classes),
    }
    expected_geometry = {
        "n_channels": 5,
        "sampling_rate_hz": 100.0,
        "kernel_size_samples": 16,
        "stride_samples": 4,
        "embedding_dim": 8,
        "output_classes": 6,
    }
    if require_registered_checkpoint and geometry != expected_geometry:
        raise Loop24GateRefusal(
            "model_config_or_parameter_count_mismatch",
            "Loop 24 checkpoint geometry drifted",
        )
    return producer, {
        "file": path.name,
        "bytes": size,
        "sha256": file_sha256,
        "parameter_payload_sha256": str(producer.parameter_payload_sha256),
        "model_config_sha256": metadata.get("config_sha256"),
        "registered_identity_match": match,
        "loaded_once": True,
        "training_runs": 0,
        "parameter_updates": 0,
        "geometry": geometry,
        "validate_load_sec": round(time.perf_counter() - started_at, 9),
    }


def _extract_frame_bundle(producer, partition: LoadedPrecisionRuntimePartition) -> FrameBundle:
    np = _require_numpy()
    frames: list[Any] = []
    starts: list[int] = []
    ends: list[int] = []
    group_lengths: list[int] = []
    for item_index, raw_length in enumerate(partition.input_lengths.tolist()):
        length = int(raw_length)
        frame_count = 1 + (length - int(producer.kernel_size)) // int(producer.stride)
        if frame_count < 1:
            raise Loop24GateRefusal(
                "frame_grid_timestamp_shape_or_causality_mismatch",
                "fixture item is shorter than one producer frame",
            )
        group_lengths.append(frame_count)
        for local_index in range(frame_count):
            start = local_index * int(producer.stride)
            end = start + int(producer.kernel_size)
            frames.append(
                partition.signals[item_index, :, start:end].reshape(-1).copy()
            )
            starts.append(start)
            ends.append(end)
    frame_array = np.stack(frames).astype("float32", copy=False)
    return FrameBundle(
        frames=frame_array,
        frame_start_samples=np.asarray(starts, dtype="int32"),
        frame_end_samples=np.asarray(ends, dtype="int32"),
        item_ids=tuple(str(value) for value in partition.item_ids.tolist()),
        input_lengths=tuple(int(value) for value in partition.input_lengths.tolist()),
        group_lengths=tuple(group_lengths),
        source_sampling_rate_hz=float(producer.source_sampling_rate_hz),
    )


def _run_candidate_replay(candidate, frames: FrameBundle, *, blank_intercept: float):
    np = _require_numpy()
    embeddings = np.empty((frames.frame_count, candidate.embedding_dim), dtype="float32")
    logits = np.empty((frames.frame_count, candidate.n_classes), dtype="float32")
    log_probabilities = np.empty((frames.frame_count, candidate.n_classes), dtype="float64")
    blank_margins = np.empty(frames.frame_count, dtype="float64")
    greedy_path: list[int] = []
    greedy_partial: list[list[list[int]]] = []
    prefix_partial: list[list[list[int]]] = []
    greedy_final: list[list[int]] = []
    prefix_final: list[list[int]] = []
    flush_behavior: list[dict[str, Any]] = []
    max_greedy_state = 0
    max_prefix_state = 0
    cursor = 0
    for group_length in frames.group_lengths:
        greedy = GreedyCTCDecoder(blank_id=BLANK_ID, max_output_length=MAX_PREFIX_LENGTH)
        prefix = PrefixBeamCTCDecoder(
            beam_width=BEAM_WIDTH,
            blank_id=BLANK_ID,
            max_prefix_length=MAX_PREFIX_LENGTH,
        )
        item_greedy: list[list[int]] = []
        item_prefix: list[list[int]] = []
        for _ in range(group_length):
            embedding, logit = candidate.run_frame(frames.frames[cursor])
            if not np.isfinite(embedding).all() or not np.isfinite(logit).all():
                raise ValueError("candidate returned non-finite embedding or logit")
            embeddings[cursor] = embedding
            logits[cursor] = logit
            adjusted = logit.astype("float64", copy=True)
            adjusted[BLANK_ID] += blank_intercept
            log_probability = _log_softmax_row(adjusted)
            if not np.isfinite(log_probability).all():
                raise ValueError("candidate returned non-finite log probabilities")
            log_probabilities[cursor] = log_probability
            blank_margins[cursor] = adjusted[BLANK_ID] - _logsumexp(
                adjusted[1:].tolist()
            )
            greedy_snapshot = greedy.push(log_probability.tolist())
            prefix_snapshot = prefix.push(log_probability.tolist())
            if not math.isfinite(prefix_snapshot.top_log_probability):
                raise ValueError("candidate returned a non-finite beam score")
            if any(not math.isfinite(value) for value in prefix.beam_scores().values()):
                raise ValueError("candidate returned a non-finite beam state")
            greedy_path.append(int(greedy_snapshot.path_class))
            item_greedy.append([int(value) for value in greedy_snapshot.hypothesis])
            item_prefix.append([int(value) for value in prefix_snapshot.top_prefix])
            max_greedy_state = max(max_greedy_state, greedy_snapshot.state_payload_bytes)
            max_prefix_state = max(max_prefix_state, prefix_snapshot.state_payload_bytes)
            cursor += 1
        greedy_row = [int(value) for value in greedy.flush()]
        prefix_row = [int(value) for value in prefix.flush()]
        flush_behavior.append(
            {
                "greedy_unchanged": item_greedy[-1] == greedy_row,
                "prefix_unchanged": item_prefix[-1] == prefix_row,
                "drop_incomplete": True,
            }
        )
        greedy_partial.append(item_greedy)
        prefix_partial.append(item_prefix)
        greedy_final.append(greedy_row)
        prefix_final.append(prefix_row)
    if cursor != frames.frame_count:
        raise RuntimeError("candidate replay frame cursor drifted")
    token_start_sec = frames.frame_start_samples.astype("float64") / frames.source_sampling_rate_hz
    token_end_sec = frames.frame_end_samples.astype("float64") / frames.source_sampling_rate_hz
    fixed_ledger = [
        "target_free_synthetic_input",
        "training_runs_zero",
        "real_and_consumed_reads_zero",
        "producer_right_context_zero",
    ]
    public = {
        "item_ids": list(frames.item_ids),
        "input_lengths": list(frames.input_lengths),
        "frame_counts": list(frames.group_lengths),
        "greedy_path_class_by_frame": greedy_path,
        "greedy_partial_hypothesis_by_frame": greedy_partial,
        "prefix_top_hypothesis_by_frame": prefix_partial,
        "greedy_final_hypothesis_by_item": greedy_final,
        "prefix_final_hypothesis_by_item": prefix_final,
        "flush_behavior": flush_behavior,
        "right_context_zero": candidate.producer_right_context_samples == 0,
        "warning_and_access_ledger": fixed_ledger,
        "max_greedy_state_bytes": max_greedy_state,
        "max_prefix_state_bytes": max_prefix_state,
    }
    array_hashes = {
        "frame_start_samples": _array_sha256(frames.frame_start_samples),
        "frame_end_samples": _array_sha256(frames.frame_end_samples),
        "token_start_sec": _array_sha256(token_start_sec),
        "token_end_sec": _array_sha256(token_end_sec),
        "embeddings": _array_sha256(embeddings),
        "logits": _array_sha256(logits),
        "log_probabilities": _array_sha256(log_probabilities),
        "blank_margins": _array_sha256(blank_margins),
    }
    payload_sha256 = _sha256_json({"public": public, "array_hashes": array_hashes})
    return {
        "embeddings": embeddings,
        "logits": logits,
        "log_probabilities": log_probabilities,
        "blank_margins": blank_margins,
        "frame_start_samples": frames.frame_start_samples,
        "frame_end_samples": frames.frame_end_samples,
        "token_start_sec": token_start_sec,
        "token_end_sec": token_end_sec,
        "public": public,
        "array_hashes": array_hashes,
        "payload_sha256": payload_sha256,
    }


def _compare_candidate_replay(reference, candidate, tolerances: Mapping[str, Any]):
    np = _require_numpy()
    exact_checks = {
        "item_ids": reference["public"]["item_ids"] == candidate["public"]["item_ids"],
        "input_lengths": reference["public"]["input_lengths"]
        == candidate["public"]["input_lengths"],
        "frame_counts": reference["public"]["frame_counts"]
        == candidate["public"]["frame_counts"],
        "frame_start_samples": np.array_equal(
            reference["frame_start_samples"], candidate["frame_start_samples"]
        ),
        "frame_end_samples": np.array_equal(
            reference["frame_end_samples"], candidate["frame_end_samples"]
        ),
        "token_timestamps": np.array_equal(
            reference["token_start_sec"], candidate["token_start_sec"]
        )
        and np.array_equal(reference["token_end_sec"], candidate["token_end_sec"]),
        "embedding_shape": reference["embeddings"].shape == candidate["embeddings"].shape,
        "logit_shape": reference["logits"].shape == candidate["logits"].shape,
        "greedy_path_class_by_frame": reference["public"][
            "greedy_path_class_by_frame"
        ]
        == candidate["public"]["greedy_path_class_by_frame"],
        "greedy_partial_hypothesis_by_frame": reference["public"][
            "greedy_partial_hypothesis_by_frame"
        ]
        == candidate["public"]["greedy_partial_hypothesis_by_frame"],
        "prefix_top_hypothesis_by_frame": reference["public"][
            "prefix_top_hypothesis_by_frame"
        ]
        == candidate["public"]["prefix_top_hypothesis_by_frame"],
        "greedy_final_hypothesis_by_item": reference["public"][
            "greedy_final_hypothesis_by_item"
        ]
        == candidate["public"]["greedy_final_hypothesis_by_item"],
        "prefix_final_hypothesis_by_item": reference["public"][
            "prefix_final_hypothesis_by_item"
        ]
        == candidate["public"]["prefix_final_hypothesis_by_item"],
        "flush_behavior": reference["public"]["flush_behavior"]
        == candidate["public"]["flush_behavior"],
        "right_context_zero": candidate["public"]["right_context_zero"] is True,
        "warning_and_access_ledger": reference["public"]["warning_and_access_ledger"]
        == candidate["public"]["warning_and_access_ledger"],
    }
    embedding = _numeric_comparison(
        reference["embeddings"],
        candidate["embeddings"],
        absolute_max=float(tolerances["embedding_max_absolute_error"]),
        relative_rmse_max=float(tolerances["embedding_relative_rmse_max"]),
    )
    embedding["minimum_cosine_similarity"] = _minimum_cosine_similarity(
        reference["embeddings"],
        candidate["embeddings"],
        norm_floor=float(tolerances["cosine_zero_norm_floor"]),
        absolute_error_threshold=float(tolerances["embedding_max_absolute_error"]),
    )
    embedding["cosine_passed"] = bool(
        embedding["minimum_cosine_similarity"]
        >= float(tolerances["embedding_cosine_similarity_min"])
    )
    logits = _numeric_comparison(
        reference["logits"],
        candidate["logits"],
        absolute_max=float(tolerances["logit_max_absolute_error"]),
        relative_rmse_max=float(tolerances["logit_relative_rmse_max"]),
    )
    blank_error = float(
        np.max(np.abs(reference["blank_margins"] - candidate["blank_margins"]))
    )
    log_probability_error = float(
        np.max(
            np.abs(reference["log_probabilities"] - candidate["log_probabilities"])
        )
    )
    finite = bool(
        all(
            np.isfinite(value).all()
            for value in (
                candidate["embeddings"],
                candidate["logits"],
                candidate["blank_margins"],
                candidate["log_probabilities"],
            )
        )
    )
    numeric_passed = bool(
        embedding["passed"]
        and embedding["cosine_passed"]
        and logits["passed"]
        and blank_error <= float(tolerances["blank_margin_max_absolute_error"])
        and log_probability_error
        <= float(tolerances["log_probability_max_absolute_error"])
    )
    exact_passed = all(exact_checks.values())
    return {
        "passed": bool(exact_passed and numeric_passed and finite),
        "exact_behavior_passed": exact_passed,
        "exact_checks": exact_checks,
        "numeric_passed": numeric_passed,
        "finite_passed": finite,
        "embedding": embedding,
        "logits": logits,
        "blank_margin_max_absolute_error": blank_error,
        "log_probability_max_absolute_error": log_probability_error,
        "reference_payload_sha256": reference["payload_sha256"],
        "candidate_payload_sha256": candidate["payload_sha256"],
        **_replay_public_summary(candidate),
    }


def _replay_public_summary(output) -> dict[str, Any]:
    return {
        "frames": int(output["embeddings"].shape[0]),
        "embedding_shape": [int(value) for value in output["embeddings"].shape],
        "logit_shape": [int(value) for value in output["logits"].shape],
        "array_hashes": output["array_hashes"],
        "payload_sha256": output["payload_sha256"],
        "max_greedy_state_bytes": output["public"]["max_greedy_state_bytes"],
        "max_prefix_state_bytes": output["public"]["max_prefix_state_bytes"],
        "greedy_final_hypotheses_sha256": _sha256_json(
            output["public"]["greedy_final_hypothesis_by_item"]
        ),
        "prefix_final_hypotheses_sha256": _sha256_json(
            output["public"]["prefix_final_hypothesis_by_item"]
        ),
    }


def _run_balanced_timing_protocol(
    orders: Sequence[Sequence[str]],
    *,
    source_payload: FrozenProducerPayload,
    frames: FrameBundle,
    candidate_records: Mapping[str, Mapping[str, Any]],
    worker_runner: Callable[[FrozenProducerPayload, str, FrameBundle], dict[str, Any]],
    label: str,
    counters: dict[str, int],
    caps: LocalPrecisionRuntimeCaps,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for round_index, order in enumerate(orders):
        for position, candidate_id in enumerate(order):
            record = candidate_records[candidate_id]
            if record["status"] != "available":
                rows.append(
                    {
                        "partition": label,
                        "round": round_index + 1,
                        "position": position + 1,
                        "candidate_id": candidate_id,
                        "status": "unavailable_no_fallback",
                        "refusal_id": record.get("refusal_id"),
                    }
                )
                continue
            counters["timing_worker_processes"] += 1
            if candidate_id == FLOAT32_REFERENCE:
                counters["reference_inference_runs"] += 1
            else:
                counters["candidate_inference_runs"] += 1
            if counters["timing_worker_processes"] > caps.maximum_worker_processes_spawned:
                raise Loop24GateRefusal(
                    "resource_cap_exceeded",
                    "Loop 24 spawned more timing workers than registered",
                )
            try:
                result = worker_runner(source_payload, candidate_id, frames)
            except (RuntimeError, ValueError) as exc:
                rows.append(
                    {
                        "partition": label,
                        "round": round_index + 1,
                        "position": position + 1,
                        "candidate_id": candidate_id,
                        "status": "timing_failed_no_fallback",
                        "refusal_id": "timer_protocol_or_balanced_order_mismatch",
                        "message": str(exc),
                    }
                )
                continue
            if int(result["worker_peak_rss_bytes"]) > caps.maximum_peak_rss_bytes_each_worker:
                raise Loop24GateRefusal(
                    "resource_cap_exceeded",
                    f"{candidate_id} timing worker exceeded the RSS cap",
                )
            rows.append(
                {
                    "partition": label,
                    "round": round_index + 1,
                    "position": position + 1,
                    "candidate_id": candidate_id,
                    "status": "measured",
                    **result,
                }
            )
    return rows


def _run_timing_worker(
    source_payload: FrozenProducerPayload,
    candidate_id: str,
    frames: FrameBundle,
) -> dict[str, Any]:
    """Run one candidate-round in one fresh sequential isolated worker."""

    available_methods = multiprocessing.get_all_start_methods()
    method = "forkserver" if "forkserver" in available_methods else "spawn"
    if method not in available_methods:
        raise RuntimeError("registered timing workers require forkserver or spawn")
    context = multiprocessing.get_context(method)
    parent, child = context.Pipe(duplex=False)
    process = context.Process(
        target=_timing_worker_entry,
        args=(child, source_payload, candidate_id, frames),
    )
    process.start()
    child.close()
    process.join(timeout=5.0)
    if process.is_alive():
        process.terminate()
        process.join(timeout=1.0)
        parent.close()
        raise RuntimeError(f"{candidate_id} timing worker exceeded five seconds")
    try:
        if not parent.poll():
            raise RuntimeError(
                f"{candidate_id} timing worker exited without a result (code {process.exitcode})"
            )
        try:
            result = parent.recv()
        except EOFError as exc:
            raise RuntimeError(
                f"{candidate_id} timing worker closed before returning a result"
            ) from exc
    finally:
        parent.close()
    if process.exitcode != 0:
        raise RuntimeError(f"{candidate_id} timing worker failed with code {process.exitcode}")
    if not result.get("ok"):
        raise RuntimeError(str(result.get("error") or "timing worker failed"))
    return result["result"]


def _timing_worker_entry(connection, source_payload, candidate_id, frames) -> None:
    try:
        imported_empty_rss = _peak_rss_bytes() or 0
        construction_started = time.perf_counter()
        candidate = build_precision_candidate_from_payload(source_payload, candidate_id)
        construction_sec = time.perf_counter() - construction_started
        after_construction_rss = _peak_rss_bytes() or imported_empty_rss
        first_started = time.perf_counter()
        candidate.run_frame(frames.frames[0])
        first_frame_sec = time.perf_counter() - first_started
        candidate_logits = _producer_logits(candidate, frames.frames)

        def producer_path():
            return _producer_checksum(candidate, frames.frames)

        def decoder_path():
            return _decoder_checksum(candidate_logits, frames.group_lengths)

        def full_path():
            return _full_pipeline_checksum(candidate, frames)

        paths = {
            TIMED_PATHS[0]: _benchmark_callable(producer_path, frames.frame_count),
            TIMED_PATHS[1]: _benchmark_callable(decoder_path, frames.frame_count),
            TIMED_PATHS[2]: _benchmark_callable(full_path, frames.frame_count),
        }
        peak_rss = _peak_rss_bytes() or after_construction_rss
        connection.send(
            {
                "ok": True,
                "result": {
                    "frames_per_call": frames.frame_count,
                    "candidate_construct_sec": round(construction_sec, 9),
                    "first_frame_sec": round(first_frame_sec, 9),
                    "imported_empty_worker_peak_rss_bytes": int(imported_empty_rss),
                    "worker_peak_rss_bytes": int(peak_rss),
                    "worker_peak_rss_delta_bytes": max(
                        0, int(peak_rss) - int(imported_empty_rss)
                    ),
                    "candidate_construction_temporary_bytes": max(
                        0, int(after_construction_rss) - int(imported_empty_rss)
                    ),
                    "paths": paths,
                    "candidate_materialized_from_in_memory_payload": True,
                    "checkpoint_reads": 0,
                    "partition_file_opens": 0,
                },
            }
        )
    except Exception as exc:  # noqa: BLE001 - child must return an inspectable error
        try:
            connection.send({"ok": False, "error": f"{type(exc).__name__}: {exc}"})
        except (BrokenPipeError, EOFError, OSError):
            pass
    finally:
        connection.close()


def _benchmark_callable(function: Callable[[], Any], frame_count: int) -> dict[str, Any]:
    from torch.utils.benchmark import Timer

    measurement = Timer(
        stmt="function()",
        globals={"function": function},
        num_threads=1,
    ).adaptive_autorange(
        threshold=0.1,
        min_run_time=0.05,
        max_run_time=0.25,
    )
    per_call = [
        float(value) / int(measurement.number_per_run)
        for value in measurement.raw_times
    ]
    ns_per_frame = [value * 1e9 / frame_count for value in per_call]
    return {
        "raw_times_sec": [round(value, 12) for value in measurement.raw_times],
        "number_per_run": int(measurement.number_per_run),
        "measurement_repeats": len(measurement.raw_times),
        "median_ns_per_frame": _percentile(ns_per_frame, 50.0),
        "p25_ns_per_frame": _percentile(ns_per_frame, 25.0),
        "p75_ns_per_frame": _percentile(ns_per_frame, 75.0),
        "p95_ns_per_frame": _percentile(ns_per_frame, 95.0),
        "iqr_over_median": _safe_ratio(
            _percentile(ns_per_frame, 75.0) - _percentile(ns_per_frame, 25.0),
            _percentile(ns_per_frame, 50.0),
        ),
        "timer_threshold_iqr_over_median": 0.1,
        "timer_min_run_time_sec": 0.05,
        "timer_max_run_time_sec": 0.25,
        "timer_num_threads": 1,
    }


def _producer_logits(candidate, frames):
    np = _require_numpy()
    rows = np.empty((len(frames), candidate.n_classes), dtype="float32")
    for index, frame in enumerate(frames):
        _embedding, rows[index] = candidate.run_frame(frame)
    return rows


def _producer_checksum(candidate, frames) -> float:
    checksum = 0.0
    for frame in frames:
        embedding, logits = candidate.run_frame(frame)
        checksum += float(embedding[0]) + float(logits[0])
    return checksum


def _decoder_checksum(logits, group_lengths: Sequence[int]) -> int:
    cursor = 0
    checksum = 0
    for group_length in group_lengths:
        greedy = GreedyCTCDecoder(blank_id=BLANK_ID, max_output_length=MAX_PREFIX_LENGTH)
        prefix = PrefixBeamCTCDecoder(
            beam_width=BEAM_WIDTH,
            blank_id=BLANK_ID,
            max_prefix_length=MAX_PREFIX_LENGTH,
        )
        for _ in range(group_length):
            row = logits[cursor].astype("float64", copy=True)
            row[BLANK_ID] += REGISTERED_BLANK_INTERCEPT
            log_probability = _log_softmax_row(row)
            greedy.push(log_probability.tolist())
            prefix.push(log_probability.tolist())
            cursor += 1
        checksum += len(greedy.flush()) + len(prefix.flush())
    return checksum


def _full_pipeline_checksum(candidate, frames: FrameBundle) -> int:
    cursor = 0
    checksum = 0
    for group_length in frames.group_lengths:
        greedy = GreedyCTCDecoder(blank_id=BLANK_ID, max_output_length=MAX_PREFIX_LENGTH)
        prefix = PrefixBeamCTCDecoder(
            beam_width=BEAM_WIDTH,
            blank_id=BLANK_ID,
            max_prefix_length=MAX_PREFIX_LENGTH,
        )
        for _ in range(group_length):
            _embedding, logit = candidate.run_frame(frames.frames[cursor])
            row = logit.astype("float64", copy=True)
            row[BLANK_ID] += REGISTERED_BLANK_INTERCEPT
            log_probability = _log_softmax_row(row)
            greedy.push(log_probability.tolist())
            prefix.push(log_probability.tolist())
            cursor += 1
        checksum += len(greedy.flush()) + len(prefix.flush())
    return checksum


def _aggregate_timing_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    candidate_ids: Sequence[str],
    reference_id: str,
    bootstrap_seed: int,
    bootstrap_resamples: int,
    stride_samples: int,
    sampling_rate_hz: float,
) -> dict[str, Any]:
    expected_rounds = len({int(row["round"]) for row in rows})
    aggregates: dict[str, Any] = {}
    measured_by_candidate = {
        candidate_id: [
            row
            for row in rows
            if row["candidate_id"] == candidate_id and row["status"] == "measured"
        ]
        for candidate_id in candidate_ids
    }
    reference_rows = {
        int(row["round"]): row for row in measured_by_candidate.get(reference_id, [])
    }
    for candidate_id in candidate_ids:
        candidate_rows = measured_by_candidate[candidate_id]
        if not candidate_rows:
            aggregates[candidate_id] = {
                "status": "unavailable_or_unmeasured",
                "rounds": 0,
                "expected_rounds": expected_rounds,
                "paths": {},
            }
            continue
        path_rows: dict[str, Any] = {}
        for path in TIMED_PATHS:
            values = [float(row["paths"][path]["median_ns_per_frame"]) for row in candidate_rows]
            paired_ratios = []
            for row in candidate_rows:
                reference = reference_rows.get(int(row["round"]))
                if reference is None:
                    continue
                paired_ratios.append(
                    _safe_ratio(
                        float(row["paths"][path]["median_ns_per_frame"]),
                        float(reference["paths"][path]["median_ns_per_frame"]),
                    )
                )
            interval = _paired_bootstrap_interval(
                paired_ratios,
                seed=bootstrap_seed,
                resamples=bootstrap_resamples,
            )
            reference_values = [
                float(row["paths"][path]["median_ns_per_frame"])
                for row in measured_by_candidate.get(reference_id, [])
            ]
            median_value = _percentile(values, 50.0)
            p25_value = _percentile(values, 25.0)
            p75_value = _percentile(values, 75.0)
            p95_value = _percentile(values, 95.0)
            path_rows[path] = {
                "median_ns_per_frame": median_value,
                "p25_ns_per_frame": p25_value,
                "p75_ns_per_frame": p75_value,
                "p95_ns_per_frame": p95_value,
                "iqr_over_median": _safe_ratio(p75_value - p25_value, median_value),
                "paired_latency_ratios": paired_ratios,
                "paired_latency_ratio": (
                    _percentile(paired_ratios, 50.0) if paired_ratios else None
                ),
                "paired_latency_ratio_bootstrap_95_interval": interval,
                "p95_latency_ratio": (
                    _safe_ratio(p95_value, _percentile(reference_values, 95.0))
                    if reference_values
                    else None
                ),
                "compute_real_time_factor": _safe_ratio(
                    median_value / 1e9,
                    stride_samples / sampling_rate_hz,
                ),
            }
        rss_values = [int(row["worker_peak_rss_bytes"]) for row in candidate_rows]
        empty_rss = [
            int(row["imported_empty_worker_peak_rss_bytes"]) for row in candidate_rows
        ]
        aggregates[candidate_id] = {
            "status": (
                "measured" if len(candidate_rows) == expected_rounds else "incomplete"
            ),
            "rounds": len(candidate_rows),
            "expected_rounds": expected_rounds,
            "paths": path_rows,
            "candidate_construct_sec_median": _percentile(
                [float(row["candidate_construct_sec"]) for row in candidate_rows], 50.0
            ),
            "first_frame_sec_median": _percentile(
                [float(row["first_frame_sec"]) for row in candidate_rows], 50.0
            ),
            "absolute_worker_peak_rss_bytes_median": _percentile(rss_values, 50.0),
            "absolute_worker_peak_rss_bytes_max": max(rss_values),
            "imported_empty_worker_peak_rss_bytes_median": _percentile(
                empty_rss, 50.0
            ),
            "worker_peak_rss_delta_bytes_median": _percentile(
                [int(row["worker_peak_rss_delta_bytes"]) for row in candidate_rows],
                50.0,
            ),
        }
    return {
        "candidates": aggregates,
        "raw_rows": len(rows),
        "reference_id": reference_id,
        "bootstrap_seed": bootstrap_seed,
        "bootstrap_resamples": bootstrap_resamples,
        "expected_rounds": expected_rounds,
    }


def _select_candidate(
    *,
    candidate_records: dict[str, dict[str, Any]],
    timing: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen material-runtime and storage-only rules exactly once."""

    results: dict[str, Any] = {}
    replacement_candidates: list[str] = []
    storage_only_candidates: list[str] = []
    for candidate_id in CANDIDATE_IDS[1:]:
        record = candidate_records[candidate_id]
        provenance = record.get("provenance") or {}
        correctness = record.get("correctness") or {}
        profiler = record.get("profiler") or {}
        provenance_passed = bool(
            record.get("status") == "available"
            and provenance.get("fallback_used") is False
            and provenance.get("autocast_used") is False
            and provenance.get("compile_used") is False
            and provenance.get("architecture_changed") is False
            and provenance.get("training_runs") == 0
            and provenance.get("parameter_updates") == 0
        )
        profiler_passed = bool(
            not profiler.get("required") or profiler.get("passed") is True
        )
        correctness_passed = bool(correctness.get("passed") is True)
        eligible = bool(provenance_passed and profiler_passed and correctness_passed)
        replacement = _replacement_threshold_result(
            candidate_id=candidate_id,
            candidate_records=candidate_records,
            timing=timing,
            contract=contract,
            include_storage=True,
        )
        storage_only = _storage_only_threshold_result(
            candidate_id=candidate_id,
            candidate_records=candidate_records,
            timing=timing,
            contract=contract,
        )
        replacement_passed = bool(eligible and replacement["passed"])
        storage_only_passed = bool(
            eligible and storage_only["passed"] and not replacement_passed
        )
        if replacement_passed:
            replacement_candidates.append(candidate_id)
        if storage_only_passed:
            storage_only_candidates.append(candidate_id)
        result = {
            "eligible": eligible,
            "provenance_passed": provenance_passed,
            "profiler_passed": profiler_passed,
            "correctness_passed": correctness_passed,
            "replacement_thresholds": replacement,
            "replacement_passed": replacement_passed,
            "storage_only_thresholds": storage_only,
            "storage_only_passed": storage_only_passed,
        }
        record["selection_eligibility"] = result
        results[candidate_id] = result

    replacement_candidates.sort(
        key=lambda candidate_id: _replacement_tie_break_key(
            results[candidate_id], candidate_id
        )
    )
    selected = replacement_candidates[0] if replacement_candidates else None
    if selected is not None:
        status = "provisional_replacement_requires_one_time_qualification"
    elif storage_only_candidates:
        status = "storage_only_result_retain_float32"
    else:
        status = contract["selection_rules"]["no_material_candidate_decision"]
    return {
        "default_before_gate": FLOAT32_REFERENCE,
        "status": status,
        "provisional_replacement_candidate": selected,
        "replacement_candidates_passing": replacement_candidates,
        "storage_only_candidates": sorted(storage_only_candidates),
        "candidate_results": results,
        "qualification_required": selected is not None,
        "thresholds_candidates_and_fixture_changed_after_open": False,
        "tie_break": list(contract["selection_rules"]["replacement_tie_break"]),
    }


def _replacement_threshold_result(
    *,
    candidate_id: str,
    candidate_records: Mapping[str, Mapping[str, Any]],
    timing: Mapping[str, Any],
    contract: Mapping[str, Any],
    include_storage: bool,
) -> dict[str, Any]:
    rules = contract["selection_rules"]["default_replacement_requires_all"]
    reference_timing = timing["candidates"].get(FLOAT32_REFERENCE) or {}
    candidate_timing = timing["candidates"].get(candidate_id) or {}
    reference_storage = (candidate_records[FLOAT32_REFERENCE].get("storage") or {})
    candidate_storage = (candidate_records[candidate_id].get("storage") or {})
    model_path = (candidate_timing.get("paths") or {}).get(TIMED_PATHS[0]) or {}
    full_path = (candidate_timing.get("paths") or {}).get(TIMED_PATHS[2]) or {}
    interval = full_path.get("paired_latency_ratio_bootstrap_95_interval") or {}
    rss_delta = _difference_or_none(
        candidate_timing.get("worker_peak_rss_delta_bytes_median"),
        reference_timing.get("worker_peak_rss_delta_bytes_median"),
    )
    checks = {
        "model_path_median_latency_ratio": _maximum_check(
            model_path.get("paired_latency_ratio"),
            rules["model_path_median_latency_ratio_max"],
        ),
        "full_pipeline_median_latency_ratio": _maximum_check(
            full_path.get("paired_latency_ratio"),
            rules["full_pipeline_median_latency_ratio_max"],
        ),
        "full_pipeline_p95_latency_ratio": _maximum_check(
            full_path.get("p95_latency_ratio"),
            rules["full_pipeline_p95_latency_ratio_max"],
        ),
        "full_pipeline_bootstrap_upper_95": _maximum_check(
            interval.get("upper"),
            rules["full_pipeline_latency_ratio_bootstrap_upper_95_max"],
        ),
        "worker_peak_rss_delta_vs_reference_bytes": _maximum_check(
            rss_delta,
            rules["worker_peak_rss_delta_vs_reference_max_bytes"],
        ),
    }
    if include_storage:
        payload_ratio = _optional_ratio(
            candidate_storage.get("deterministic_serialized_numeric_payload_bytes"),
            reference_storage.get("deterministic_serialized_numeric_payload_bytes"),
        )
        checks["serialized_numeric_payload_ratio"] = _maximum_check(
            payload_ratio,
            rules["serialized_numeric_payload_ratio_max"],
        )
    measured = bool(
        reference_timing.get("status") == "measured"
        and candidate_timing.get("status") == "measured"
    )
    return {
        "passed": bool(measured and all(row["passed"] for row in checks.values())),
        "timing_measured": measured,
        "checks": checks,
    }


def _storage_only_threshold_result(
    *,
    candidate_id: str,
    candidate_records: Mapping[str, Mapping[str, Any]],
    timing: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    rules = contract["selection_rules"]["storage_only_candidate_requires_all"]
    reference_timing = timing["candidates"].get(FLOAT32_REFERENCE) or {}
    candidate_timing = timing["candidates"].get(candidate_id) or {}
    reference_storage = candidate_records[FLOAT32_REFERENCE].get("storage") or {}
    candidate_storage = candidate_records[candidate_id].get("storage") or {}
    reference_bytes = reference_storage.get(
        "deterministic_serialized_numeric_payload_bytes"
    )
    candidate_bytes = candidate_storage.get(
        "deterministic_serialized_numeric_payload_bytes"
    )
    full_path = (candidate_timing.get("paths") or {}).get(TIMED_PATHS[2]) or {}
    savings = _difference_or_none(reference_bytes, candidate_bytes)
    checks = {
        "serialized_numeric_payload_ratio": _maximum_check(
            _optional_ratio(candidate_bytes, reference_bytes),
            rules["serialized_numeric_payload_ratio_max"],
        ),
        "absolute_payload_savings_bytes": _minimum_check(
            savings,
            rules["absolute_payload_savings_min_bytes"],
        ),
        "full_pipeline_median_latency_ratio": _maximum_check(
            full_path.get("paired_latency_ratio"),
            rules["full_pipeline_median_latency_ratio_max"],
        ),
        "full_pipeline_p95_latency_ratio": _maximum_check(
            full_path.get("p95_latency_ratio"),
            rules["full_pipeline_p95_latency_ratio_max"],
        ),
    }
    measured = bool(
        reference_timing.get("status") == "measured"
        and candidate_timing.get("status") == "measured"
    )
    return {
        "passed": bool(measured and all(row["passed"] for row in checks.values())),
        "timing_measured": measured,
        "replaces_default": False,
        "checks": checks,
    }


def _replacement_tie_break_key(result: Mapping[str, Any], candidate_id: str):
    checks = result["replacement_thresholds"]["checks"]
    return (
        checks["full_pipeline_p95_latency_ratio"]["actual"],
        checks["full_pipeline_median_latency_ratio"]["actual"],
        checks["model_path_median_latency_ratio"]["actual"],
        checks["serialized_numeric_payload_ratio"]["actual"],
        candidate_id,
    )


def _final_decision(
    selection: Mapping[str, Any], qualification: Mapping[str, Any]
) -> str:
    selected = selection.get("provisional_replacement_candidate")
    if selected is not None:
        if qualification.get("opened") is not True:
            raise Loop24GateRefusal(
                "qualification_opened_without_replacement_candidate",
                "a selected replacement was not qualified exactly once",
            )
        if qualification.get("candidate_id") != selected:
            raise Loop24GateRefusal(
                "qualification_opened_without_replacement_candidate",
                "qualification candidate differs from the frozen selection",
            )
        if qualification.get("passed") is True:
            return f"proceed_with_{selected}_for_this_frozen_pipeline"
        return "retain_float32_and_reject_selected_candidate"
    if qualification.get("opened"):
        raise Loop24GateRefusal(
            "qualification_opened_without_replacement_candidate",
            "qualification opened without a selected replacement",
        )
    if selection.get("storage_only_candidates"):
        return "record_storage_only_result_and_retain_float32"
    return "retain_float32_no_material_gain"


def _paired_bootstrap_interval(
    ratios: Sequence[float], *, seed: int, resamples: int
) -> dict[str, Any]:
    values = [float(value) for value in ratios]
    if not values:
        return {"lower": None, "upper": None, "resamples": int(resamples)}
    if any(not math.isfinite(value) or value < 0 for value in values):
        raise ValueError("paired latency ratios must be finite and nonnegative")
    if resamples < 1:
        raise ValueError("bootstrap resamples must be positive")
    np = _require_numpy()
    rng = np.random.default_rng(int(seed))
    source = np.asarray(values, dtype="float64")
    samples = rng.choice(source, size=(int(resamples), len(values)), replace=True)
    medians = np.median(samples, axis=1)
    return {
        "lower": float(np.percentile(medians, 2.5)),
        "upper": float(np.percentile(medians, 97.5)),
        "resamples": int(resamples),
    }


def _numeric_comparison(
    reference,
    candidate,
    *,
    absolute_max: float,
    relative_rmse_max: float,
) -> dict[str, Any]:
    np = _require_numpy()
    left = np.asarray(reference, dtype="float64")
    right = np.asarray(candidate, dtype="float64")
    if left.shape != right.shape:
        return {
            "passed": False,
            "max_absolute_error": None,
            "relative_rmse": None,
            "shape_match": False,
        }
    delta = right - left
    max_absolute_error = float(np.max(np.abs(delta))) if delta.size else 0.0
    rmse = float(np.sqrt(np.mean(np.square(delta)))) if delta.size else 0.0
    source_rms = float(np.sqrt(np.mean(np.square(left)))) if left.size else 0.0
    relative_rmse = rmse / max(source_rms, 1e-12)
    return {
        "passed": bool(
            math.isfinite(max_absolute_error)
            and math.isfinite(relative_rmse)
            and max_absolute_error <= absolute_max
            and relative_rmse <= relative_rmse_max
        ),
        "shape_match": True,
        "max_absolute_error": max_absolute_error,
        "rmse": rmse,
        "source_rms": source_rms,
        "relative_rmse": relative_rmse,
        "max_absolute_error_limit": float(absolute_max),
        "relative_rmse_limit": float(relative_rmse_max),
    }


def _minimum_cosine_similarity(
    reference,
    candidate,
    *,
    norm_floor: float,
    absolute_error_threshold: float,
) -> float:
    np = _require_numpy()
    left = np.asarray(reference, dtype="float64")
    right = np.asarray(candidate, dtype="float64")
    if left.shape != right.shape or left.ndim < 2:
        return 0.0
    rows = []
    for left_row, right_row in zip(left.reshape(left.shape[0], -1), right.reshape(right.shape[0], -1)):
        left_norm = float(np.linalg.norm(left_row))
        right_norm = float(np.linalg.norm(right_row))
        if left_norm <= norm_floor and right_norm <= norm_floor:
            rows.append(
                1.0
                if float(np.max(np.abs(left_row - right_row)))
                <= absolute_error_threshold
                else 0.0
            )
        elif left_norm <= norm_floor or right_norm <= norm_floor:
            rows.append(0.0)
        else:
            rows.append(
                float(np.dot(left_row, right_row) / (left_norm * right_norm))
            )
    return min(rows, default=1.0)


def _maximum_check(actual: Any, limit: Any) -> dict[str, Any]:
    numeric = _finite_float_or_none(actual)
    maximum = float(limit)
    return {
        "actual": numeric,
        "maximum": maximum,
        "passed": bool(numeric is not None and numeric <= maximum),
    }


def _minimum_check(actual: Any, limit: Any) -> dict[str, Any]:
    numeric = _finite_float_or_none(actual)
    minimum = float(limit)
    return {
        "actual": numeric,
        "minimum": minimum,
        "passed": bool(numeric is not None and numeric >= minimum),
    }


def _finite_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def _optional_ratio(numerator: Any, denominator: Any) -> float | None:
    top = _finite_float_or_none(numerator)
    bottom = _finite_float_or_none(denominator)
    if top is None or bottom is None or bottom <= 0:
        return None
    return top / bottom


def _difference_or_none(left: Any, right: Any) -> float | None:
    first = _finite_float_or_none(left)
    second = _finite_float_or_none(right)
    if first is None or second is None:
        return None
    return first - second


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile from no values")
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise ValueError("percentile values must be finite")
    if not 0.0 <= percentile <= 100.0:
        raise ValueError("percentile must be between zero and one hundred")
    position = (len(ordered) - 1) * percentile / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _safe_ratio(numerator: float, denominator: float) -> float:
    top = float(numerator)
    bottom = float(denominator)
    if not math.isfinite(top) or not math.isfinite(bottom) or bottom <= 0:
        raise ValueError("runtime ratios require finite values and a positive denominator")
    return top / bottom


def _logsumexp(values: Sequence[float]) -> float:
    if not values:
        return -math.inf
    maximum = max(float(value) for value in values)
    if not math.isfinite(maximum):
        return maximum
    return maximum + math.log(sum(math.exp(float(value) - maximum) for value in values))


def _log_softmax_row(values):
    np = _require_numpy()
    row = np.asarray(values, dtype="float64")
    if row.ndim != 1 or row.size < 2 or not np.isfinite(row).all():
        raise ValueError("decoder logits must be one finite row")
    normalizer = _logsumexp(row.tolist())
    return row - normalizer


def _new_access_counters() -> dict[str, int]:
    contract = _load_contract()
    return {str(name): 0 for name in contract["access_counters"]}


def _record_stage(
    events: list[dict[str, Any]],
    contract: Mapping[str, Any],
    index: int,
    *,
    action: str,
    **details: Any,
) -> None:
    sequence = contract["partition_access_sequence"]
    if index != len(events) or index < 0 or index >= len(sequence):
        raise Loop24GateRefusal(
            "qualification_opened_before_selection_freeze",
            "Loop 24 access stages were attempted out of order",
        )
    events.append(
        {
            "index": int(index),
            "registered_step": str(sequence[index]),
            "action": str(action),
            "details": details,
        }
    )


def _validate_event_sequence(
    events: Sequence[Mapping[str, Any]], contract: Mapping[str, Any]
) -> None:
    expected = list(contract["partition_access_sequence"])
    if len(events) != len(expected):
        raise Loop24GateRefusal(
            "qualification_opened_before_selection_freeze",
            "Loop 24 access ledger is incomplete",
        )
    if [row.get("index") for row in events] != list(range(len(expected))):
        raise Loop24GateRefusal(
            "qualification_opened_before_selection_freeze",
            "Loop 24 access ledger indices drifted",
        )
    if [row.get("registered_step") for row in events] != expected:
        raise Loop24GateRefusal(
            "qualification_opened_before_selection_freeze",
            "Loop 24 registered access sequence drifted",
        )


def _validate_access_boundary(counters: Mapping[str, Any]) -> None:
    expected = _new_access_counters()
    if set(counters) != set(expected):
        raise Loop24GateRefusal(
            "report_omits_warning_unavailable_field_or_access_counter",
            "Loop 24 access counters are incomplete",
        )
    for name, value in counters.items():
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise Loop24GateRefusal(
                "report_omits_warning_unavailable_field_or_access_counter",
                f"Loop 24 access counter {name} is invalid",
            )
    forbidden = [name for name in FORBIDDEN_COUNTERS if counters[name] != 0]
    if forbidden:
        refusal_id = (
            "rw3_operation_not_authorized"
            if any(name.startswith("rw3_") for name in forbidden)
            else "consumed_seed_or_real_evidence_accessed"
        )
        if "training_runs" in forbidden or "parameter_updates" in forbidden:
            refusal_id = "training_or_parameter_update_attempted"
        raise Loop24GateRefusal(
            refusal_id,
            f"Loop 24 forbidden access counters are nonzero: {forbidden}",
        )
    exact = {
        "manifest_metadata_reads": 1,
        "checkpoint_file_reads": 1,
        "selection_partition_opens": 1,
    }
    for name, expected_value in exact.items():
        if counters[name] != expected_value:
            raise Loop24GateRefusal(
                "report_omits_warning_unavailable_field_or_access_counter",
                f"Loop 24 requires {name}={expected_value}",
            )
    if counters["qualification_partition_opens"] not in (0, 1):
        raise Loop24GateRefusal(
            "qualification_opened_without_replacement_candidate",
            "Loop 24 qualification partition may be opened at most once",
        )
    if not 1 <= counters["candidate_conversions"] <= len(CANDIDATE_IDS):
        raise Loop24GateRefusal(
            "candidate_dtype_or_module_contract_mismatch",
            "Loop 24 candidate conversion count is invalid",
        )
    if counters["timing_worker_processes"] > LocalPrecisionRuntimeCaps().maximum_worker_processes_spawned:
        raise Loop24GateRefusal(
            "resource_cap_exceeded",
            "Loop 24 timing worker count exceeds the frozen cap",
        )


def _validate_working_bytes(
    partition: LoadedPrecisionRuntimePartition,
    frames: FrameBundle,
    maximum_bytes: int,
) -> None:
    total = int(partition.array_bytes + frames.array_bytes)
    if total > int(maximum_bytes):
        raise Loop24GateRefusal(
            "resource_cap_exceeded",
            f"Loop 24 materialized {total} working bytes, above {maximum_bytes}",
        )


def _unavailable_candidate_record(
    candidate_id: str, *, refusal_id: str, message: str
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "status": "unavailable_no_fallback",
        "refusal_id": refusal_id,
        "message": message,
        "provenance": None,
        "storage": None,
        "profiler": None,
        "correctness": None,
        "selection_eligibility": None,
    }


def _collect_warnings(candidate_records: Mapping[str, Mapping[str, Any]]) -> list[str]:
    values = [
        "Synthetic numerical stress signals are not neural recordings.",
        "CPU runtime is local-platform-specific and is not end-to-end text latency.",
        "Energy measurement was not authorized and is unavailable.",
        "Serialized numeric payload bytes are not a deployable package size.",
        "Tensor dtype does not prove hardware kernel accumulation dtype.",
    ]
    for candidate_id in CANDIDATE_IDS:
        row = candidate_records[candidate_id]
        if row.get("status") != "available":
            values.append(
                f"{candidate_id} unavailable without fallback: {row.get('refusal_id')}."
            )
        provenance = row.get("provenance") or {}
        values.extend(str(value) for value in provenance.get("warnings") or [])
        if candidate_id == FLOAT16_EAGER_CPU:
            values.append("Float16 hardware accumulation dtype is unavailable.")
    return list(dict.fromkeys(values))


def _decoder_config() -> dict[str, Any]:
    return {
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


def _validate_output_directory(
    output_dir: Path, *, enforce_authorized_output_root: bool
) -> None:
    if output_dir.exists():
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            f"refusing to replace existing Loop 24 output: {output_dir.name}",
        )
    resolved = output_dir.expanduser().resolve(strict=False)
    if resolved == resolved.parent:
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            "Loop 24 output may not be a filesystem root",
        )
    if not enforce_authorized_output_root:
        return
    root = _repo_root().resolve()
    allowed_roots = (
        root / "cache" / "loop24",
        root / "outputs" / "loop24",
        root / ".codex_work" / "loop24",
    )
    if not any(
        resolved != allowed.resolve(strict=False)
        and resolved.is_relative_to(allowed.resolve(strict=False))
        for allowed in allowed_roots
    ):
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            "Loop 24 output must be nested under an authorized ignored root",
        )


def _environment_summary() -> dict[str, Any]:
    np = _require_numpy()
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - optional environment
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            "Loop 24 requires the existing optional PyTorch environment",
        ) from exc
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass
    git_commit = _run_text(("git", "rev-parse", "HEAD"), cwd=_repo_root())
    tracked_status = _run_text(
        ("git", "status", "--porcelain=v1", "--untracked-files=no"),
        cwd=_repo_root(),
    )
    git_branch = _run_text(("git", "branch", "--show-current"), cwd=_repo_root())
    return {
        "git_commit": git_commit,
        "git_branch": git_branch,
        "tracked_worktree_clean": not bool(tracked_status),
        "architecture": platform.machine(),
        "host_model": _sysctl("hw.model"),
        "cpu_name": _sysctl("machdep.cpu.brand_string"),
        "physical_cores": _int_or_none(_sysctl("hw.physicalcpu")),
        "logical_cores": _int_or_none(_sysctl("hw.logicalcpu")),
        "memory_bytes": _int_or_none(_sysctl("hw.memsize")),
        "operating_system": f"macOS {platform.mac_ver()[0]}",
        "operating_system_build": _sysctl("kern.osversion"),
        "python_version": platform.python_version(),
        "numpy_version": str(np.__version__),
        "torch_version": str(torch.__version__),
        "torch_git_version": str(torch.version.git_version),
        "torchao_installed": importlib.util.find_spec("torchao") is not None,
        "legacy_quantize_dynamic_available": bool(
            getattr(getattr(torch, "ao", None), "quantization", None)
            and getattr(torch.ao.quantization, "quantize_dynamic", None)
        ),
        "supported_quantized_engines": [
            str(value) for value in torch.backends.quantized.supported_engines
        ],
        "quantized_engine_before_gate": str(torch.backends.quantized.engine),
        "torch_intraop_threads": int(torch.get_num_threads()),
        "torch_interop_threads": int(torch.get_num_interop_threads()),
        "execution_device": "cpu",
        "thread_environment": {
            name: os.environ.get(name) for name in THREAD_ENVIRONMENT
        },
        "private_fields_omitted": [
            "absolute_paths",
            "hostname",
            "ip_addresses",
            "user_name",
        ],
    }


def _require_registered_environment(
    environment: Mapping[str, Any], contract: Mapping[str, Any]
) -> None:
    registered = contract["preregistration_host_snapshot"]
    comparisons = {
        "architecture": registered["architecture"],
        "host_model": registered["host_model"],
        "cpu_name": registered["cpu_name"],
        "physical_cores": registered["physical_cores"],
        "logical_cores": registered["logical_cores"],
        "memory_bytes": registered["memory_bytes"],
        "operating_system": registered["operating_system"],
        "operating_system_build": registered["operating_system_build"],
        "python_version": registered["python_version"],
        "numpy_version": registered["numpy_version"],
        "torch_version": registered["torch_version"],
        "torch_git_version": registered["torch_git_version"],
        "torchao_installed": registered["torchao_installed"],
        "legacy_quantize_dynamic_available": registered[
            "legacy_quantize_dynamic_available"
        ],
        "supported_quantized_engines": registered["supported_quantized_engines"],
        "quantized_engine_before_gate": registered["quantized_engine_before_gate"],
    }
    drift = [
        name for name, expected in comparisons.items() if environment.get(name) != expected
    ]
    if drift:
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            f"registered Loop 24 environment drifted: {drift}",
        )
    if environment.get("execution_device") != "cpu":
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            "Loop 24 execution device must be CPU",
        )
    if environment.get("torch_intraop_threads") != 1 or environment.get(
        "torch_interop_threads"
    ) != 1:
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            "Loop 24 PyTorch thread counts must both equal one",
        )
    thread_environment = environment.get("thread_environment") or {}
    if thread_environment != THREAD_ENVIRONMENT:
        assignments = " ".join(f"{name}=1" for name in THREAD_ENVIRONMENT)
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            f"Loop 24 requires one-thread environment values: {assignments}",
        )


def _require_clean_committed_execution(environment: Mapping[str, Any]) -> None:
    if environment.get("tracked_worktree_clean") is not True:
        raise Loop24GateRefusal(
            "contract_or_source_binding_mismatch",
            "registered Loop 24 execution requires a clean tracked worktree",
        )
    commit = str(environment.get("git_commit") or "")
    if len(commit) != 40 or any(value not in "0123456789abcdef" for value in commit):
        raise Loop24GateRefusal(
            "contract_or_source_binding_mismatch",
            "registered Loop 24 execution requires a committed source identity",
        )


def _load_contract() -> dict[str, Any]:
    path = _repo_root() / CONTRACT_RELATIVE_PATH
    value = _load_json_object(path, "Loop 24 machine contract")
    if _file_sha256(path) != REGISTERED_CONTRACT_SHA256:
        raise RuntimeError("Loop 24 machine contract hash drifted")
    return value


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is not valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _run_text(command: Sequence[str], *, cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            list(command),
            cwd=cwd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise Loop24GateRefusal(
            "thread_or_device_contract_mismatch",
            f"Loop 24 environment command failed: {command[0]}",
        ) from exc
    return result.stdout.strip()


def _sysctl(name: str) -> str | None:
    try:
        value = subprocess.run(
            ["sysctl", "-n", name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=2.0,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return value or None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _array_sha256(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_stable_json_bytes(value, newline=False)).hexdigest()


def _stable_json_bytes(value: object, *, newline: bool = True) -> bytes:
    suffix = "\n" if newline else ""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        + suffix
    ).encode("utf-8")


def _peak_rss_bytes() -> int | None:
    try:
        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    except (AttributeError, OSError, ValueError):
        return None
    return value if sys.platform == "darwin" else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "Loop 24 precision/runtime work requires NumPy: `pip install -e '.[ml]'`."
        ) from exc
    return np


def _write_final_artifacts(
    *,
    output_dir: Path,
    report: dict[str, Any],
    payload_bytes: Mapping[str, bytes],
    fixture_bytes: int,
    caps: LocalPrecisionRuntimeCaps,
) -> None:
    selection_path = output_dir / "selection.json"
    if not selection_path.is_file():
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            "Loop 24 selection decision is missing before final report write",
        )
    existing = sorted(path.name for path in output_dir.iterdir())
    if existing != [selection_path.name]:
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            f"unexpected Loop 24 output collision: {existing}",
        )

    payload_artifacts: dict[str, dict[str, Any]] = {}
    for candidate_id, payload in sorted(payload_bytes.items()):
        if len(payload) > caps.maximum_candidate_serialized_bytes_each:
            raise Loop24GateRefusal(
                "resource_cap_exceeded",
                f"{candidate_id} payload exceeds the frozen cap",
            )
        payload_artifacts[candidate_id] = {
            "file": f"{candidate_id}.numeric.bin",
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "deployable_package": False,
        }
    report["artifacts"]["candidate_payloads"] = payload_artifacts
    selection_info = {
        "file": selection_path.name,
        "bytes": int(selection_path.stat().st_size),
        "sha256": _file_sha256(selection_path),
    }
    static_output_bytes = selection_info["bytes"] + sum(
        row["bytes"] for row in payload_artifacts.values()
    )

    final_payloads: tuple[bytes, bytes, bytes] | None = None
    for _ in range(24):
        report_bytes = _stable_json_bytes(report)
        markdown_bytes = _render_local_precision_runtime_markdown(report).encode("utf-8")
        audit, audit_bytes = _build_measured_audit(
            report=report,
            report_bytes=report_bytes,
            markdown_bytes=markdown_bytes,
            selection_info=selection_info,
            payload_artifacts=payload_artifacts,
            static_output_bytes=static_output_bytes,
            fixture_bytes=int(fixture_bytes),
            caps=caps,
        )
        report_artifact_bytes = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
        output_bytes = static_output_bytes + report_artifact_bytes
        total_generated_bytes = int(fixture_bytes) + output_bytes
        sizes = {
            selection_path.name: selection_info["bytes"],
            **{
                row["file"]: row["bytes"] for row in payload_artifacts.values()
            },
            "gate.json": len(report_bytes),
            "gate.md": len(markdown_bytes),
            "audit.json": len(audit_bytes),
        }
        updated = False
        resource_updates = {
            "report_bytes": report_artifact_bytes,
            "output_bytes": output_bytes,
            "total_generated_bytes": total_generated_bytes,
        }
        for name, value in resource_updates.items():
            if report["resources"].get(name) != value:
                report["resources"][name] = value
                updated = True
        if report["artifacts"].get("sizes") != sizes:
            report["artifacts"]["sizes"] = sizes
            updated = True
        if not updated:
            final_payloads = (report_bytes, markdown_bytes, audit_bytes)
            break
    if final_payloads is None:  # pragma: no cover - defensive convergence guard
        raise RuntimeError("Loop 24 artifact byte accounting did not converge")

    report_bytes, markdown_bytes, audit_bytes = final_payloads
    report_total = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
    output_total = static_output_bytes + report_total
    generated_total = int(fixture_bytes) + output_total
    if report_total > caps.maximum_report_bytes_total:
        raise Loop24GateRefusal(
            "resource_cap_exceeded",
            f"Loop 24 reports require {report_total} bytes, above the frozen cap",
        )
    if generated_total > caps.maximum_generated_bytes_total:
        raise Loop24GateRefusal(
            "resource_cap_exceeded",
            f"Loop 24 generated artifacts require {generated_total} bytes, above the cap",
        )
    _validate_report_privacy(report_bytes, markdown_bytes, audit_bytes)

    for candidate_id, payload in sorted(payload_bytes.items()):
        _write_exclusive(
            output_dir / payload_artifacts[candidate_id]["file"],
            payload,
        )
    _write_exclusive(output_dir / "gate.json", report_bytes)
    _write_exclusive(output_dir / "gate.md", markdown_bytes)
    _write_exclusive(output_dir / "audit.json", audit_bytes)


def _build_measured_audit(
    *,
    report: Mapping[str, Any],
    report_bytes: bytes,
    markdown_bytes: bytes,
    selection_info: Mapping[str, Any],
    payload_artifacts: Mapping[str, Mapping[str, Any]],
    static_output_bytes: int,
    fixture_bytes: int,
    caps: LocalPrecisionRuntimeCaps,
) -> tuple[dict[str, Any], bytes]:
    artifacts: dict[str, Any] = {
        selection_info["file"]: {
            "bytes": selection_info["bytes"],
            "sha256": selection_info["sha256"],
        },
        **{
            row["file"]: {"bytes": row["bytes"], "sha256": row["sha256"]}
            for row in payload_artifacts.values()
        },
        "gate.json": {
            "bytes": len(report_bytes),
            "sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "gate.md": {
            "bytes": len(markdown_bytes),
            "sha256": hashlib.sha256(markdown_bytes).hexdigest(),
        },
        "audit.json": {"bytes": 0, "sha256": None},
    }
    audit: dict[str, Any] = {
        "schema": {"name": AUDIT_SCHEMA_NAME, "version": AUDIT_SCHEMA_VERSION},
        "proof_posture": "measured_target_free_synthetic_platform_audit",
        "report_sha256": artifacts["gate.json"]["sha256"],
        "access_counters": dict(report["access"]["counters"]),
        "measurements": {
            "runtime_sec": report["resources"]["runtime_sec"],
            "parent_peak_rss_bytes": report["resources"]["parent_peak_rss_bytes"],
            "maximum_worker_peak_rss_bytes": report["resources"][
                "maximum_worker_peak_rss_bytes"
            ],
            "producer_causal": report["producer"]["causal"],
            "end_to_end_latency_measured": False,
            "energy_measured": False,
        },
        "resources": {
            "fixture_bytes": int(fixture_bytes),
            "report_bytes": 0,
            "output_bytes": 0,
            "total_generated_bytes": 0,
            "maximum_report_bytes": caps.maximum_report_bytes_total,
            "maximum_generated_bytes": caps.maximum_generated_bytes_total,
            "report_cap_passed": True,
            "generated_cap_passed": True,
        },
        "artifacts": artifacts,
        "warnings": [
            "Measured timing, RSS, and byte counts are platform-bound.",
            "This audit sidecar intentionally does not self-hash.",
        ],
    }
    audit_bytes = b""
    for _ in range(16):
        audit_bytes = _stable_json_bytes(audit)
        report_total = len(report_bytes) + len(markdown_bytes) + len(audit_bytes)
        output_total = int(static_output_bytes) + report_total
        generated_total = int(fixture_bytes) + output_total
        updates = {
            "report_bytes": report_total,
            "output_bytes": output_total,
            "total_generated_bytes": generated_total,
            "maximum_report_bytes": caps.maximum_report_bytes_total,
            "maximum_generated_bytes": caps.maximum_generated_bytes_total,
            "report_cap_passed": report_total <= caps.maximum_report_bytes_total,
            "generated_cap_passed": generated_total
            <= caps.maximum_generated_bytes_total,
        }
        changed = audit["resources"] != updates
        audit["resources"] = updates
        if audit["artifacts"]["audit.json"]["bytes"] != len(audit_bytes):
            audit["artifacts"]["audit.json"]["bytes"] = len(audit_bytes)
            changed = True
        if not changed:
            break
    else:  # pragma: no cover - defensive convergence guard
        raise RuntimeError("Loop 24 measured audit byte accounting did not converge")
    audit_bytes = _stable_json_bytes(audit)
    return audit, audit_bytes


def _render_local_precision_runtime_markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# Loop 24 Local Precision And Runtime Gate",
        "",
        f"- Proof posture: `{report['proof_posture']}`",
        f"- Decision: `{report['decision']}`",
        f"- Gate passed: `{str(report['gate_passed']).lower()}`",
        f"- Producer causal: `{str(report['producer']['causal']).lower()}`",
        "- End-to-end latency measured: `false`",
        "- Energy measured: `false`",
        "",
        "## Candidates",
        "",
        "| Candidate | Status | Correctness | Payload bytes | Producer ratio | Full ratio |",
        "|---|---|---:|---:|---:|---:|",
    ]
    timing = report["selection"]["timing"]["candidates"]
    for candidate_id in CANDIDATE_IDS:
        candidate = report["candidates"][candidate_id]
        candidate_timing = timing.get(candidate_id) or {}
        paths = candidate_timing.get("paths") or {}
        producer_ratio = (paths.get(TIMED_PATHS[0]) or {}).get(
            "paired_latency_ratio"
        )
        full_ratio = (paths.get(TIMED_PATHS[2]) or {}).get("paired_latency_ratio")
        payload = (candidate.get("storage") or {}).get(
            "deterministic_serialized_numeric_payload_bytes"
        )
        correctness = (candidate.get("correctness") or {}).get("passed")
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{candidate_id}`",
                    f"`{candidate['status']}`",
                    _markdown_value(correctness),
                    _markdown_value(payload),
                    _markdown_value(producer_ratio),
                    _markdown_value(full_ratio),
                )
            )
            + " |"
        )
    resources = report["resources"]
    counters = report["access"]["counters"]
    lines.extend(
        [
            "",
            "## Resources",
            "",
            f"- Input bytes: {resources['input_bytes']}",
            f"- Working array bytes: {resources['working_array_bytes']}",
            f"- Report bytes: {resources['report_bytes']}",
            f"- Output bytes: {resources['output_bytes']}",
            f"- Total generated bytes: {resources['total_generated_bytes']}",
            f"- Runtime: {resources['runtime_sec']:.6f} sec",
            f"- Parent peak RSS: {_markdown_value(resources['parent_peak_rss_bytes'])}",
            "- Maximum worker peak RSS: "
            f"{_markdown_value(resources['maximum_worker_peak_rss_bytes'])}",
            "",
            "## Access",
            "",
        ]
    )
    lines.extend(f"- `{name}`: {value}" for name, value in counters.items())
    lines.extend(["", "## Warnings", ""])
    lines.extend(f"- {value}" for value in report["warnings"])
    lines.extend(["", "## Unavailable Fields", ""])
    lines.extend(f"- `{value}`" for value in report["unavailable_fields"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {value}" for value in report["claim_boundary"])
    return "\n".join(lines) + "\n"


def _markdown_value(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def _validate_report_privacy(*payloads: bytes) -> None:
    text = b"\n".join(payloads).decode("utf-8")
    forbidden = {
        str(Path.home()),
        str(_repo_root()),
        "/Users/",
        "file://",
    }
    leaked = sorted(value for value in forbidden if value and value in text)
    if leaked:
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            "Loop 24 report contains a forbidden private path",
        )


def _write_exclusive(path: Path, payload: bytes) -> None:
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError as exc:
        raise Loop24GateRefusal(
            "output_collision_or_unsafe_path",
            f"refusing to replace existing Loop 24 artifact: {path.name}",
        ) from exc
