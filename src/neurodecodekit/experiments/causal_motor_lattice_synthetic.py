"""Bounded synthetic-only execution shell for Causal Motor Lattice v0."""

from __future__ import annotations

import hashlib
import io
import json
import math
import resource
import shutil
import subprocess
import sys
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from neurodecodekit.models.causal_motor_lattice import (
    CONTEXT_SAMPLES,
    CROP_SAMPLES,
    EXPECTED_PARAMETER_COUNT,
    INPUT_CHANNELS,
    REGISTERED_CONTRACT_BYTES,
    REGISTERED_CONTRACT_SHA256,
    RESIDUAL_GAIN,
    SOURCE_CHANNELS,
    VIEW_NAMES,
    build_causal_motor_lattice_model,
    build_lattice_incidence,
    build_synthetic_projection,
    load_registered_cml_synthetic_contract,
    validate_causal_motor_lattice_model,
)


SCHEMA_NAME = "neurodecodekit.causal_motor_lattice_synthetic_result"
SCHEMA_VERSION = "0.1.0"
PLAN_SCHEMA_NAME = "neurodecodekit.causal_motor_lattice_synthetic_plan"
PLAN_SCHEMA_VERSION = "0.1.0"
PROOF_POSTURE = "synthetic_architecture_mechanics_only_no_real_EEG_or_scientific_evidence"
IMPLEMENTATION_REGISTRY_RELATIVE_PATH = Path(
    "registries/causal_motor_lattice_synthetic_implementation.v0.json"
)
CHECKPOINT_NAME = "checkpoint.npz"
REPORT_NAME = "report.json"
MAX_OUTPUT_BYTES = 4 * 1024 * 1024
MAX_REPORT_BYTES = 1024 * 1024
MINIMUM_FREE_DISK_BYTES = 20 * 1024 * 1024 * 1024
POSITIVE_FACTORS = (
    "potential_shape_signal",
    "mu_energy_signal",
    "beta_energy_signal",
    "mixed_potential_mu_beta_signal",
)
DIAGNOSTIC_FACTORS = (
    "left_right_spatial_reversal",
    "timing_only_labels_without_signal_relation",
    "peripheral_like_common_mode_artifact",
    "pure_noise",
)
FACTOR_TO_VIEW = {
    "potential_shape_signal": "potential",
    "mu_energy_signal": "mu",
    "beta_energy_signal": "beta",
}
CONDITION_NAMES = (
    "full",
    "potential_muted",
    "mu_muted",
    "beta_muted",
    "all_views_muted",
    "channel_deranged",
    "time_displaced",
    "hemisphere_mirrored",
    "peripheral_proxy_only",
)
WARNINGS = (
    "Every signal target key channel and geometry identity in this gate is synthetic.",
    "The 8-to-64 projection adds no information and represents no anatomical montage.",
    "Matched-view auxiliary supervision is a synthetic mechanics device and is not a real-data recipe.",
    "Branch ablations cannot prove cortical potential mu beta or brain-specific origin.",
    "The peripheral proxy is a constructed shortcut and not validated EOG.",
    "The synthetic final partition is an engineering stop gate and not scientific evidence.",
    "Passing this gate does not reopen Loop 54 B or C, authorize PhysioNet, or qualify Loop 55.",
)
UNAVAILABLE_FIELDS = (
    "real_EEG_signal_quality",
    "real_channel_names_reference_or_geometry",
    "real_event_trial_or_key_ontology",
    "biological_or_brain_specific_origin",
    "real_decoding_accuracy_or_neural_advantage",
    "unseen_person_or_cross_session_generalization",
    "end_to_end_latency",
    "portable_earbud_or_home_device_performance",
    "assistive_diagnostic_or_clinical_utility",
)
FORBIDDEN_REPORT_KEY_FRAGMENTS = (
    "target_text",
    "reference_text",
    "intended_text",
    "participant_id",
    "subject_id",
    "local_path",
    "protected_path",
    "per_item_prediction",
    "per_item_target",
    "per_item_label",
)


@dataclass(frozen=True)
class CMLSyntheticInputs:
    """Validated synthetic arrays and non-model routing metadata."""

    normalized_signal: Any
    source_crops: Any
    peripheral_crops: Any
    valid_mask: Any
    normalization_location: Any
    normalization_scale: Any
    projection: Any
    factor_ids: Any
    partition_ids: Any
    pair_ids: Any
    synthetic_hand_class: Any
    source_bytes_generated: int
    provenance: Mapping[str, Any]


def build_cml_synthetic_execution_plan(
    *, contract_path: str | Path | None = None
) -> dict[str, Any]:
    """Return the exact dry-run plan without importing scientific libraries."""

    contract = load_registered_cml_synthetic_contract(contract_path)
    return {
        "schema": {"name": PLAN_SCHEMA_NAME, "version": PLAN_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "execution_requested": False,
        "contract": {
            "path": (
                Path(contract_path).as_posix()
                if contract_path is not None
                else "registries/causal_motor_lattice_synthetic_contract.v0.json"
            ),
            "bytes": REGISTERED_CONTRACT_BYTES,
            "sha256": REGISTERED_CONTRACT_SHA256,
        },
        "candidate": {
            "id": contract["architecture"]["candidate_id"],
            "trainable_parameters": EXPECTED_PARAMETER_COUNT,
            "input_shape": [96, INPUT_CHANNELS, CROP_SAMPLES],
            "view_feature_shape": [96, len(VIEW_NAMES), 24],
            "producer_is_causal": True,
            "required_left_context_samples": CONTEXT_SAMPLES,
            "required_right_context_samples": 0,
        },
        "protocol": {
            "experiment_seed": contract["source_fixture"]["experiment_seed"],
            "parameter_update_rows": contract["partition_and_target_protocol"][
                "parameter_update_rows"
            ],
            "parameter_update_runs": contract["training_recipe"]["parameter_update_runs"],
            "optimizer_steps": contract["training_recipe"]["optimizer_steps"],
            "check_rows": contract["partition_and_target_protocol"]["check_rows"],
            "conditional_final_rows": contract["partition_and_target_protocol"][
                "final_rows"
            ],
            "same_checkpoint_conditions": list(CONDITION_NAMES),
            "rerun_allowed": False,
        },
        "required_proof_before_execute": {
            "exact_implementation_commit": "required_40_character_SHA",
            "successful_remote_CI_run": "required_positive_integer",
            "tracked_worktree_clean": True,
        },
        "resource_caps": dict(contract["resource_caps"]),
        "access_counters": dict(contract["current_access_counters"]),
        "warnings": list(WARNINGS),
        "unavailable_fields": list(UNAVAILABLE_FIELDS),
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def prepare_cml_synthetic_inputs(
    *, contract_path: str | Path | None = None
) -> CMLSyntheticInputs:
    """Replay and adapt only the exact registered synthetic motor fixture."""

    contract = load_registered_cml_synthetic_contract(contract_path)
    _verify_contract_source_bindings(contract)
    np = _require_numpy()
    from neurodecodekit.training.synthetic_motor_fixture import make_synthetic_motor_arrays

    arrays, fixture_metadata = make_synthetic_motor_arrays()
    signals = np.asarray(arrays["signals"], dtype="float32")
    peripheral = np.asarray(arrays["peripheral_proxy"], dtype="float32")
    lengths = np.asarray(arrays["valid_lengths"], dtype="int32")
    pairs = np.asarray(arrays["pair_ids"])
    crops = np.zeros((96, SOURCE_CHANNELS, CROP_SAMPLES), dtype="float32")
    proxy_crops = np.zeros((96, CROP_SAMPLES), dtype="float32")
    seen_pairs: set[str] = set()
    for row_index, pair_value in enumerate(pairs.tolist()):
        pair_id = str(pair_value)
        if pair_id in seen_pairs:
            continue
        seen_pairs.add(pair_id)
        pair_rows = np.flatnonzero(pairs == pair_value)
        if pair_rows.shape != (2,):
            raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")
        anchor = int(lengths[pair_rows].min())
        start = anchor - CROP_SAMPLES
        if start < 0 or anchor > signals.shape[2]:
            raise ValueError("CML-SYN-F04-pair-anchor-or-crop-mismatch")
        for member in pair_rows.tolist():
            crops[member] = signals[member, :, start:anchor]
            proxy_crops[member] = peripheral[member, start:anchor]
    if len(seen_pairs) != 48:
        raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")

    factors = np.asarray(arrays["factor_ids"])
    partitions = np.asarray(arrays["partition_ids"])
    hands = np.asarray(arrays["synthetic_hand_class"], dtype="int64")
    _validate_pair_equalities(np, crops, factors, partitions, pairs)
    projection = build_synthetic_projection(contract=contract)
    projected = np.einsum("oc,nct->not", projection, crops, optimize=False).astype("float32")
    train_mask = (partitions == "train") & np.isin(factors, np.asarray(POSITIVE_FACTORS))
    if int(train_mask.sum()) != 24:
        raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")
    train_values = projected[train_mask]
    location = np.median(train_values, axis=(0, 2)).astype("float32")
    lower = np.quantile(train_values, 0.25, axis=(0, 2), method="linear")
    upper = np.quantile(train_values, 0.75, axis=(0, 2), method="linear")
    scale = np.maximum((upper - lower) / 1.349, 1e-4).astype("float32")
    normalized = ((projected - location[None, :, None]) / scale[None, :, None]).astype(
        "float32"
    )
    if not np.isfinite(normalized).all():
        raise ValueError("CML-SYN-F17-nonfinite-loss-logit-or-parameter")
    valid_mask = np.ones((96, CROP_SAMPLES), dtype="bool")
    source_bytes = sum(
        int(np.asarray(value).nbytes)
        for name, value in arrays.items()
        if name != "metadata"
    )
    provenance = {
        "fixture_schema": fixture_metadata["schema"],
        "fixture_seed": fixture_metadata["identity"]["seed"],
        "fixture_array_hashes_sha256": _json_sha256(fixture_metadata["array_sha256"]),
        "source_crop_sha256": _raw_array_sha256(crops, dtype="<f4"),
        "peripheral_crop_sha256": _raw_array_sha256(proxy_crops, dtype="<f4"),
        "projection_sha256": contract["synthetic_projection"]["matrix_sha256"],
        "normalization_location_sha256": _raw_array_sha256(location, dtype="<f4"),
        "normalization_scale_sha256": _raw_array_sha256(scale, dtype="<f4"),
        "normalized_signal_sha256": _raw_array_sha256(normalized, dtype="<f4"),
        "partition_membership_sha256": _raw_array_sha256(partitions),
        "factor_membership_sha256": _raw_array_sha256(factors),
        "pair_membership_sha256": _raw_array_sha256(pairs),
    }
    return CMLSyntheticInputs(
        normalized_signal=normalized,
        source_crops=crops,
        peripheral_crops=proxy_crops,
        valid_mask=valid_mask,
        normalization_location=location,
        normalization_scale=scale,
        projection=projection,
        factor_ids=factors,
        partition_ids=partitions,
        pair_ids=pairs,
        synthetic_hand_class=hands,
        source_bytes_generated=source_bytes,
        provenance=provenance,
    )


def execute_cml_synthetic_gate(
    out_dir: str | Path,
    *,
    implementation_commit: str,
    implementation_ci_run: int,
    contract_path: str | Path | None = None,
    implementation_registry_path: str | Path | None = None,
    max_output_bytes: int = MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Consume the one registered synthetic CML-v0 execution."""

    contract = load_registered_cml_synthetic_contract(contract_path)
    _validate_execution_preconditions(
        out_dir=out_dir,
        implementation_commit=implementation_commit,
        implementation_ci_run=implementation_ci_run,
        contract=contract,
        implementation_registry_path=implementation_registry_path,
        max_output_bytes=max_output_bytes,
    )
    output = Path(out_dir)
    free_disk_before = _free_disk_bytes_for(output)
    if free_disk_before < MINIMUM_FREE_DISK_BYTES:
        raise RuntimeError("CML-SYN-F18-thread-worker-runtime-RSS-or-disk-cap")

    started = time.perf_counter()
    torch, functional = _require_torch()
    torch.set_num_threads(1)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        if torch.get_num_interop_threads() != 1:
            raise RuntimeError("CML-SYN-F18-thread-worker-runtime-RSS-or-disk-cap") from None
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(int(contract["training_recipe"]["random_seed"]))

    inputs = prepare_cml_synthetic_inputs(contract_path=contract_path)
    model = build_causal_motor_lattice_model(contract=contract)
    model_summary = validate_causal_motor_lattice_model(model, contract=contract)
    training = _fit_registered_checkpoint(
        torch=torch,
        functional=functional,
        model=model,
        inputs=inputs,
        contract=contract,
    )

    check_outputs = _predict_conditions(
        torch=torch,
        model=model,
        inputs=inputs,
        partition="check",
        contract=contract,
    )
    check_metrics, check_gates, mutation_metrics = _score_check_partition(
        torch=torch,
        model=model,
        inputs=inputs,
        outputs=check_outputs,
        contract=contract,
    )
    check_passed = all(check_gates.values())

    final_outputs: dict[str, dict[str, Any]] | None = None
    final_metrics: dict[str, Any] | None = None
    final_gates: dict[str, bool] | None = None
    if check_passed:
        final_outputs = _predict_conditions(
            torch=torch,
            model=model,
            inputs=inputs,
            partition="final",
            contract=contract,
        )
        final_metrics, final_gates = _score_final_partition(
            inputs=inputs,
            outputs=final_outputs,
            contract=contract,
        )

    checkpoint_arrays = _checkpoint_arrays(
        model=model,
        inputs=inputs,
        contract=contract,
    )
    checkpoint_payload = _deterministic_npz_bytes(checkpoint_arrays)
    if len(checkpoint_payload) > max_output_bytes:
        raise RuntimeError("CML-SYN-F19-output-file-byte-or-schema-cap")
    replay_model = _load_checkpoint_model(
        checkpoint_payload,
        contract=contract,
    )
    replay = _replay_prediction_hashes(
        torch=torch,
        model=replay_model,
        inputs=inputs,
        check_outputs=check_outputs,
        final_outputs=final_outputs,
        contract=contract,
    )
    if final_gates is not None:
        final_gates["deterministic_replay_prediction_hash_match"] = bool(
            replay["all_hashes_match"]
        )

    scientific_and_access_counters = _result_access_counters(
        inputs=inputs,
        check_passed=check_passed,
        final_delivered=final_outputs is not None,
    )
    runtime_seconds = time.perf_counter() - started
    peak_rss_bytes = _peak_rss_bytes()
    resource_gates = {
        "one_CPU_thread": torch.get_num_threads() == 1,
        "one_worker": True,
        "runtime_within_600_seconds": runtime_seconds
        <= int(contract["resource_caps"]["maximum_wall_seconds"]),
        "peak_RSS_within_512_MiB": peak_rss_bytes
        <= int(contract["resource_caps"]["maximum_peak_RSS_bytes"]),
        "free_disk_at_least_20_GiB_before": free_disk_before
        >= int(contract["resource_caps"]["minimum_free_disk_bytes_before"]),
        "network_and_download_bytes_zero": True,
    }
    scientific_zero_fields = (
        "real_or_public_data_reads",
        "protected_target_or_label_reads",
        "S20_path_stats_or_reads",
        "PhysioNet_downloads_or_reads",
        "network_calls",
        "provider_calls",
        "pretrained_weight_or_external_embedding_reads",
        "stream_device_or_hardware_operations",
        "release_operations",
        "scientific_claim_upgrades",
    )
    access_gates = {
        "every_real_network_hardware_and_claim_counter_zero": all(
            scientific_and_access_counters[name] == 0 for name in scientific_zero_fields
        ),
        "operation_counts_within_contract": (
            scientific_and_access_counters["parameter_update_runs"] == 1
            and scientific_and_access_counters["optimizer_steps"] == 600
            and scientific_and_access_counters["model_inference_stages"] <= 3
            and scientific_and_access_counters["prediction_sets"] <= 20
        ),
    }
    final_passed = final_gates is not None and all(final_gates.values())
    all_nonoutput_gates = (
        check_passed
        and final_passed
        and replay["all_hashes_match"]
        and all(resource_gates.values())
        and all(access_gates.values())
    )
    decision = {
        "status": "pass" if all_nonoutput_gates else "park",
        "route": "CML-SYN-PASS" if all_nonoutput_gates else "CML-R0",
        "check_passed": check_passed,
        "final_targets_delivered": final_outputs is not None,
        "final_passed": final_passed,
        "rerun_allowed": False,
        "implementation_mechanics_only": True,
        "scientific_claim_upgrade": False,
    }
    implementation_registry = _load_implementation_registry(
        implementation_registry_path,
        require_source_hashes=True,
    )
    report: dict[str, Any] = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "contract": {
            "path": "registries/causal_motor_lattice_synthetic_contract.v0.json",
            "bytes": REGISTERED_CONTRACT_BYTES,
            "sha256": REGISTERED_CONTRACT_SHA256,
        },
        "implementation_proof": {
            "commit": implementation_commit,
            "remote_CI_run": int(implementation_ci_run),
            "registry_path": IMPLEMENTATION_REGISTRY_RELATIVE_PATH.as_posix(),
            "registry_sha256": _json_file_sha256(
                Path(implementation_registry_path)
                if implementation_registry_path is not None
                else _repo_root() / IMPLEMENTATION_REGISTRY_RELATIVE_PATH
            ),
            "registry_status": implementation_registry["status"],
            "tracked_worktree_clean_before_execution": True,
        },
        "decision": decision,
        "source_and_adapter": {
            "source_fixture_seed": contract["source_fixture"]["fixture_seed"],
            "experiment_seed": contract["source_fixture"]["experiment_seed"],
            "input_shape": [96, INPUT_CHANNELS, CROP_SAMPLES],
            "valid_sample_count": int(inputs.valid_mask.sum()),
            "padding_fraction": 0.0,
            "source_bytes_generated": inputs.source_bytes_generated,
            "train_normalization_rows": 24,
            "geometry_available": False,
            "source_channel_identity": "synthetic_not_anatomical",
            "projected_channel_identity": "generic_synthetic_not_anatomical",
            "provenance": dict(inputs.provenance),
        },
        "model": {
            **model_summary,
            "view_feature_shape": [96, 3, 24],
            "residual_gain_rho": RESIDUAL_GAIN,
            "parameter_bytes_float32": EXPECTED_PARAMETER_COUNT * 4,
            "end_to_end_latency_measured": False,
        },
        "training": training,
        "check": {
            "metrics": check_metrics,
            "gates": check_gates,
        },
        "conditional_final": {
            "delivered": final_outputs is not None,
            "metrics": final_metrics,
            "gates": final_gates,
        },
        "mutations": mutation_metrics,
        "replay": replay,
        "resources": {
            "input_contract_bytes": REGISTERED_CONTRACT_BYTES,
            "synthetic_source_bytes_generated": inputs.source_bytes_generated,
            "checkpoint_bytes": len(checkpoint_payload),
            "report_bytes": 0,
            "total_generated_output_bytes": 0,
            "maximum_generated_output_bytes": max_output_bytes,
            "runtime_seconds": runtime_seconds,
            "peak_RSS_bytes": peak_rss_bytes,
            "free_disk_bytes_before": free_disk_before,
            "configured_CPU_threads": 1,
            "worker_count": 1,
            "resource_gates": resource_gates,
        },
        "artifacts": {
            "checkpoint": {
                "path": CHECKPOINT_NAME,
                "bytes": len(checkpoint_payload),
                "sha256": hashlib.sha256(checkpoint_payload).hexdigest(),
                "members": sorted(checkpoint_arrays),
            },
            "report": {
                "path": REPORT_NAME,
                "bytes": 0,
            },
            "output_files": 2,
            "invocation_files_committed": False,
        },
        "access_counters": scientific_and_access_counters,
        "access_gates": access_gates,
        "warnings": list(WARNINGS),
        "unavailable_fields": list(UNAVAILABLE_FIELDS),
        "claim_boundary": dict(contract["claim_boundary"]),
    }
    _validate_forbidden_report_keys(report)
    report_payload = _self_sized_report_payload(report)
    total_output_bytes = len(checkpoint_payload) + len(report_payload)
    if total_output_bytes > max_output_bytes:
        raise RuntimeError("CML-SYN-F19-output-file-byte-or-schema-cap")
    report["resources"]["report_bytes"] = len(report_payload)
    report["resources"]["total_generated_output_bytes"] = total_output_bytes
    report["artifacts"]["report"]["bytes"] = len(report_payload)
    report["resources"]["resource_gates"]["generated_output_within_4_MiB"] = True
    report_payload = _self_sized_report_payload(report)
    total_output_bytes = len(checkpoint_payload) + len(report_payload)
    if report["resources"]["total_generated_output_bytes"] != total_output_bytes:
        report["resources"]["total_generated_output_bytes"] = total_output_bytes
        report["resources"]["report_bytes"] = len(report_payload)
        report["artifacts"]["report"]["bytes"] = len(report_payload)
        report_payload = _self_sized_report_payload(report)
    if len(checkpoint_payload) + len(report_payload) > max_output_bytes:
        raise RuntimeError("CML-SYN-F19-output-file-byte-or-schema-cap")

    output.mkdir(parents=True, exist_ok=False)
    (output / CHECKPOINT_NAME).write_bytes(checkpoint_payload)
    (output / REPORT_NAME).write_bytes(report_payload)
    validated = load_cml_synthetic_result(
        output / REPORT_NAME,
        contract_path=contract_path,
        max_output_bytes=max_output_bytes,
    )
    return validated


def load_cml_synthetic_result(
    report_path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Validate aggregate result and checkpoint identity without loading arrays."""

    if max_output_bytes <= 0 or max_output_bytes > MAX_OUTPUT_BYTES:
        raise ValueError("CML-v0 result cap must be positive and at most 4 MiB")
    source = Path(report_path)
    report_bytes = source.stat().st_size
    if report_bytes > MAX_REPORT_BYTES:
        raise ValueError("CML-v0 report exceeds 1 MiB")
    report = json.loads(source.read_text(encoding="utf-8"))
    _validate_forbidden_report_keys(report)
    if report.get("schema") != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("CML-v0 result schema mismatch")
    if report.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("CML-v0 result proof posture mismatch")
    load_registered_cml_synthetic_contract(contract_path)
    if report.get("contract") != {
        "path": "registries/causal_motor_lattice_synthetic_contract.v0.json",
        "bytes": REGISTERED_CONTRACT_BYTES,
        "sha256": REGISTERED_CONTRACT_SHA256,
    }:
        raise ValueError("CML-v0 result contract binding mismatch")
    artifacts = report.get("artifacts", {})
    if artifacts.get("output_files") != 2:
        raise ValueError("CML-v0 result must bind exactly two files")
    checkpoint = artifacts.get("checkpoint", {})
    relative = PurePosixPath(str(checkpoint.get("path", "")))
    if relative.is_absolute() or len(relative.parts) != 1 or relative.name != CHECKPOINT_NAME:
        raise ValueError("CML-v0 checkpoint path is unsafe")
    checkpoint_path = source.parent / relative.name
    if checkpoint_path.stat().st_size != checkpoint.get("bytes"):
        raise ValueError("CML-v0 checkpoint byte count mismatch")
    if _json_file_sha256(checkpoint_path) != checkpoint.get("sha256"):
        raise ValueError("CML-v0 checkpoint SHA-256 mismatch")
    members, uncompressed_bytes = _npz_member_inventory(checkpoint_path)
    if members != tuple(checkpoint.get("members", ())):
        raise ValueError("CML-v0 checkpoint member inventory mismatch")
    if uncompressed_bytes > MAX_OUTPUT_BYTES:
        raise ValueError("CML-v0 checkpoint uncompressed bytes exceed cap")
    resources = report.get("resources", {})
    total = report_bytes + checkpoint_path.stat().st_size
    if resources.get("report_bytes") != report_bytes:
        raise ValueError("CML-v0 report byte accounting mismatch")
    if resources.get("checkpoint_bytes") != checkpoint_path.stat().st_size:
        raise ValueError("CML-v0 checkpoint accounting mismatch")
    if resources.get("total_generated_output_bytes") != total:
        raise ValueError("CML-v0 total output accounting mismatch")
    if total > max_output_bytes or total > resources.get("maximum_generated_output_bytes", -1):
        raise ValueError("CML-v0 output exceeds cap")
    if report.get("warnings") != list(WARNINGS):
        raise ValueError("CML-v0 warnings drifted")
    if report.get("unavailable_fields") != list(UNAVAILABLE_FIELDS):
        raise ValueError("CML-v0 unavailable-field ledger drifted")
    return report


def summarize_cml_synthetic_result(report: Mapping[str, Any]) -> dict[str, Any]:
    """Return an inspectable aggregate-only CML-v0 result summary."""

    return {
        "proof_posture": report["proof_posture"],
        "status": report["decision"]["status"],
        "route": report["decision"]["route"],
        "check_passed": report["decision"]["check_passed"],
        "final_targets_delivered": report["decision"]["final_targets_delivered"],
        "final_passed": report["decision"]["final_passed"],
        "trainable_parameters": report["model"]["trainable_parameters"],
        "input_shape": report["source_and_adapter"]["input_shape"],
        "valid_sample_count": report["source_and_adapter"]["valid_sample_count"],
        "padding_fraction": report["source_and_adapter"]["padding_fraction"],
        "runtime_seconds": report["resources"]["runtime_seconds"],
        "peak_RSS_bytes": report["resources"]["peak_RSS_bytes"],
        "total_generated_output_bytes": report["resources"][
            "total_generated_output_bytes"
        ],
        "producer_is_causal": report["model"]["producer_is_causal"],
        "end_to_end_latency_measured": report["model"]["end_to_end_latency_measured"],
        "check_metrics": report["check"]["metrics"],
        "conditional_final": report["conditional_final"],
        "access_counters": report["access_counters"],
        "warnings": report["warnings"],
        "unavailable_fields": report["unavailable_fields"],
        "claim_boundary": report["claim_boundary"],
    }


def _fit_registered_checkpoint(
    *,
    torch: Any,
    functional: Any,
    model: Any,
    inputs: CMLSyntheticInputs,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _require_numpy()
    train_indices = np.flatnonzero(
        (inputs.partition_ids == "train")
        & np.isin(inputs.factor_ids, np.asarray(POSITIVE_FACTORS))
    )
    if train_indices.shape != (24,):
        raise ValueError("CML-SYN-F12-gradient-ineligible-row-entered-loss")
    signal = torch.as_tensor(inputs.normalized_signal[train_indices], dtype=torch.float32)
    valid = torch.as_tensor(inputs.valid_mask[train_indices], dtype=torch.bool)
    hand_targets, key_targets = _targets_for_indices(inputs, train_indices, contract=contract)
    hand_tensor = torch.as_tensor(hand_targets, dtype=torch.long)
    key_tensor = torch.as_tensor(key_targets, dtype=torch.long)
    incidence = torch.as_tensor(build_lattice_incidence(contract=contract), dtype=torch.float32)
    primitive_targets = incidence[key_tensor]
    recipe = contract["training_recipe"]
    weights = recipe["loss_weights"]
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(recipe["learning_rate"]),
        betas=tuple(float(value) for value in recipe["betas"]),
        eps=float(recipe["epsilon"]),
        weight_decay=float(recipe["weight_decay"]),
    )
    factors = inputs.factor_ids[train_indices]
    trace_steps = {0, 99, 199, 299, 399, 499, 599}
    loss_trace: list[dict[str, float | int]] = []
    model.train()
    for step in range(int(recipe["optimizer_steps"])):
        optimizer.zero_grad(set_to_none=True)
        views = model.extract_views(signal, valid)
        full_output = model.forward_from_views(views)
        full_loss, components = _supervised_loss(
            functional=functional,
            output=full_output,
            key_targets=key_tensor,
            hand_targets=hand_tensor,
            primitive_targets=primitive_targets,
            weights=weights,
        )
        auxiliary_losses = []
        for factor_id, matching_view in FACTOR_TO_VIEW.items():
            local = np.flatnonzero(factors == factor_id)
            local_tensor = torch.as_tensor(local, dtype=torch.long)
            local_views = {name: value[local_tensor] for name, value in views.items()}
            muted = tuple(name for name in VIEW_NAMES if name != matching_view)
            isolated_output = model.forward_from_views(local_views, muted_views=muted)
            isolated_loss, _ = _supervised_loss(
                functional=functional,
                output=isolated_output,
                key_targets=key_tensor[local_tensor],
                hand_targets=hand_tensor[local_tensor],
                primitive_targets=primitive_targets[local_tensor],
                weights=weights,
            )
            auxiliary_losses.append(isolated_loss)
        auxiliary = torch.stack(auxiliary_losses).mean()
        objective = full_loss + float(weights["matching_isolated_view_auxiliary"]) * auxiliary
        if not bool(torch.isfinite(objective).item()):
            raise RuntimeError("CML-SYN-F17-nonfinite-loss-logit-or-parameter")
        objective.backward()
        gradient_norm = torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            max_norm=float(recipe["maximum_gradient_norm"]),
        )
        if not bool(torch.isfinite(gradient_norm).item()):
            raise RuntimeError("CML-SYN-F17-nonfinite-loss-logit-or-parameter")
        optimizer.step()
        if step in trace_steps:
            loss_trace.append(
                {
                    "step": step + 1,
                    "objective": float(objective.detach().cpu().item()),
                    "full": float(full_loss.detach().cpu().item()),
                    "auxiliary": float(auxiliary.detach().cpu().item()),
                    "key": float(components["key"].detach().cpu().item()),
                    "hand": float(components["hand"].detach().cpu().item()),
                    "primitive": float(components["primitive"].detach().cpu().item()),
                    "gradient_norm": float(gradient_norm.detach().cpu().item()),
                }
            )
    model.eval()
    if any(not bool(torch.isfinite(parameter).all().item()) for parameter in model.parameters()):
        raise RuntimeError("CML-SYN-F17-nonfinite-loss-logit-or-parameter")
    return {
        "parameter_update_runs": 1,
        "optimizer": "AdamW",
        "optimizer_steps": int(recipe["optimizer_steps"]),
        "training_rows": 24,
        "training_factor_ids": list(POSITIVE_FACTORS),
        "gradient_ineligible_factor_ids": list(DIAGNOSTIC_FACTORS),
        "random_seed": int(recipe["random_seed"]),
        "dtype": "float32",
        "device": "CPU",
        "deterministic_algorithms": True,
        "loss_trace": loss_trace,
        "early_stopping": False,
        "checkpoint_selection": False,
        "rerun_allowed": False,
    }


def _supervised_loss(
    *,
    functional: Any,
    output: Mapping[str, Any],
    key_targets: Any,
    hand_targets: Any,
    primitive_targets: Any,
    weights: Mapping[str, Any],
) -> tuple[Any, dict[str, Any]]:
    key_loss = functional.cross_entropy(output["key_logits"], key_targets)
    hand_probability = output["hand_probabilities"].gather(1, hand_targets[:, None])[:, 0]
    hand_loss = -torch_log(hand_probability.clamp_min(1e-12)).mean()
    primitive_loss = functional.binary_cross_entropy_with_logits(
        output["primitive_logits"],
        primitive_targets,
    )
    total = (
        float(weights["key_cross_entropy"]) * key_loss
        + float(weights["hand_marginal_negative_log_likelihood"]) * hand_loss
        + float(weights["primitive_multilabel_BCE"]) * primitive_loss
    )
    return total, {"key": key_loss, "hand": hand_loss, "primitive": primitive_loss}


def torch_log(value: Any) -> Any:
    """Keep Torch out of module globals while retaining a small loss helper."""

    return value.log()


def _predict_conditions(
    *,
    torch: Any,
    model: Any,
    inputs: CMLSyntheticInputs,
    partition: str,
    contract: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    np = _require_numpy()
    indices = np.flatnonzero(inputs.partition_ids == partition)
    if indices.size != (32 if partition == "check" else 16):
        raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")
    model.eval()
    signal_variants = _condition_signals(inputs, indices, contract=contract)
    valid = torch.as_tensor(inputs.valid_mask[indices], dtype=torch.bool)
    outputs: dict[str, dict[str, Any]] = {}
    with torch.no_grad():
        full_signal = torch.as_tensor(signal_variants["full"], dtype=torch.float32)
        full_views = model.extract_views(full_signal, valid)
        for condition, muted in (
            ("full", ()),
            ("potential_muted", ("potential",)),
            ("mu_muted", ("mu",)),
            ("beta_muted", ("beta",)),
            ("all_views_muted", VIEW_NAMES),
        ):
            outputs[condition] = _detach_prediction(
                model.forward_from_views(full_views, muted_views=muted)
            )
        for condition in (
            "channel_deranged",
            "time_displaced",
            "hemisphere_mirrored",
            "peripheral_proxy_only",
        ):
            value = torch.as_tensor(signal_variants[condition], dtype=torch.float32)
            outputs[condition] = _detach_prediction(model(value, valid))
    if tuple(outputs) != CONDITION_NAMES:
        raise RuntimeError("CML-v0 condition inventory drifted")
    return outputs


def _condition_signals(
    inputs: CMLSyntheticInputs,
    indices: Any,
    *,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _require_numpy()
    source = inputs.source_crops[indices]
    projection = inputs.projection
    location = inputs.normalization_location
    scale = inputs.normalization_scale

    def normalize(value: Any) -> Any:
        projected = np.einsum("oc,nct->not", projection, value, optimize=False).astype(
            "float32"
        )
        return ((projected - location[None, :, None]) / scale[None, :, None]).astype(
            "float32"
        )

    derangement = np.asarray(
        contract["mutation_contract"]["channel_derangement_source_permutation"],
        dtype="int64",
    )
    mirror = np.asarray(
        contract["mutation_contract"]["hemisphere_mirror_source_permutation"],
        dtype="int64",
    )
    displaced = np.zeros_like(source)
    shift = int(contract["mutation_contract"]["time_displacement_samples"])
    displaced[:, :, : CROP_SAMPLES - shift] = source[:, :, shift:]
    weights = np.asarray([0.80, 0.88, 0.96, 1.04, 1.04, 0.96, 0.88, 0.80])
    peripheral = (
        weights[None, :, None] * inputs.peripheral_crops[indices, None, :]
    ).astype("float32")
    return {
        "full": inputs.normalized_signal[indices],
        "channel_deranged": normalize(source[:, derangement, :]),
        "time_displaced": normalize(displaced),
        "hemisphere_mirrored": normalize(source[:, mirror, :]),
        "peripheral_proxy_only": normalize(peripheral),
    }


def _detach_prediction(output: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "key_logits": output["key_logits"].detach().cpu().numpy().astype("float32"),
        "key_probabilities": output["key_probabilities"]
        .detach()
        .cpu()
        .numpy()
        .astype("float32"),
        "hand_probabilities": output["hand_probabilities"]
        .detach()
        .cpu()
        .numpy()
        .astype("float32"),
        "bounded_residual": output["bounded_residual"]
        .detach()
        .cpu()
        .numpy()
        .astype("float32"),
    }


def _score_check_partition(
    *,
    torch: Any,
    model: Any,
    inputs: CMLSyntheticInputs,
    outputs: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, bool], dict[str, Any]]:
    np = _require_numpy()
    indices = np.flatnonzero(inputs.partition_ids == "check")
    hands, keys = _targets_for_indices(inputs, indices, contract=contract)
    factors = inputs.factor_ids[indices]
    positive = np.isin(factors, np.asarray(POSITIVE_FACTORS))
    full = outputs["full"]
    full_hand_accuracy = _accuracy(full["hand_probabilities"][positive], hands[positive])
    full_key_accuracy = _accuracy(full["key_probabilities"][positive], keys[positive])
    muted_hand_accuracy = _accuracy(
        outputs["all_views_muted"]["hand_probabilities"][positive],
        hands[positive],
    )
    factor_diagnostics: dict[str, Any] = {}
    branch_gates: dict[str, bool] = {}
    for factor_id, matching_view in FACTOR_TO_VIEW.items():
        local = factors == factor_id
        full_nll = _negative_log_likelihood(full["hand_probabilities"][local], hands[local])
        nll_by_ablation = {
            view: _negative_log_likelihood(
                outputs[f"{view}_muted"]["hand_probabilities"][local],
                hands[local],
            )
            for view in VIEW_NAMES
        }
        matching_increase = nll_by_ablation[matching_view] - full_nll
        nonmatching = [value for view, value in nll_by_ablation.items() if view != matching_view]
        factor_diagnostics[factor_id] = {
            "full_hand_NLL": full_nll,
            "hand_NLL_by_single_view_ablation": nll_by_ablation,
            "matching_view": matching_view,
            "matching_ablation_NLL_increase": matching_increase,
        }
        branch_gates[f"{matching_view}_matching_ablation_increase"] = matching_increase >= float(
            contract["check_acceptance_gates"][
                "matching_branch_ablation_hand_NLL_increase_minimum"
            ]
        )
        branch_gates[f"{matching_view}_matching_ablation_is_largest"] = (
            nll_by_ablation[matching_view] >= max(nonmatching)
        )
    mixed = factors == "mixed_potential_mu_beta_signal"
    mixed_full_nll = _negative_log_likelihood(full["hand_probabilities"][mixed], hands[mixed])
    mixed_muted_nll = _negative_log_likelihood(
        outputs["all_views_muted"]["hand_probabilities"][mixed],
        hands[mixed],
    )
    spatial = factors == "left_right_spatial_reversal"
    spatial_unmirrored_accuracy = _accuracy(full["hand_probabilities"][spatial], hands[spatial])
    spatial_mirrored_accuracy = _accuracy(
        outputs["hemisphere_mirrored"]["hand_probabilities"][spatial],
        hands[spatial],
    )
    timing_difference = _maximum_pair_probability_difference(
        inputs,
        indices,
        factor_id="timing_only_labels_without_signal_relation",
        probabilities=full["hand_probabilities"],
    )
    noise_difference = _maximum_pair_probability_difference(
        inputs,
        indices,
        factor_id="pure_noise",
        probabilities=full["hand_probabilities"],
    )
    hand_key_error = _maximum_hand_key_marginal_error(full)
    residual_maximum = float(np.max(np.abs(full["bounded_residual"])))
    mutation_metrics = _causal_and_common_mode_checks(
        torch=torch,
        model=model,
        inputs=inputs,
        indices=indices,
        contract=contract,
    )
    thresholds = contract["check_acceptance_gates"]
    gates = {
        "signal_bearing_hand_accuracy": full_hand_accuracy
        >= float(thresholds["signal_bearing_hand_accuracy_minimum"]),
        "signal_bearing_key_accuracy": full_key_accuracy
        >= float(thresholds["signal_bearing_key_accuracy_minimum"]),
        "all_views_muted_hand_accuracy": muted_hand_accuracy
        <= float(thresholds["all_views_muted_hand_accuracy_maximum"]),
        "full_minus_all_views_muted_hand_accuracy": (
            full_hand_accuracy - muted_hand_accuracy
            >= float(thresholds["full_minus_all_views_muted_hand_accuracy_minimum"])
        ),
        **branch_gates,
        "mixed_all_views_muted_NLL_increase": (
            mixed_muted_nll - mixed_full_nll
            >= float(thresholds["mixed_all_views_muted_hand_NLL_increase_minimum"])
        ),
        "mirrored_spatial_reversal_hand_accuracy": spatial_mirrored_accuracy
        >= float(thresholds["mirrored_spatial_reversal_hand_accuracy_minimum"]),
        "mirrored_minus_unmirrored_spatial_reversal_hand_accuracy": (
            spatial_mirrored_accuracy - spatial_unmirrored_accuracy
            >= float(
                thresholds[
                    "mirrored_minus_unmirrored_spatial_reversal_hand_accuracy_minimum"
                ]
            )
        ),
        "timing_only_pair_probability_equality": timing_difference
        <= float(thresholds["timing_only_pair_hand_probability_maximum_difference"]),
        "pure_noise_pair_probability_equality": noise_difference
        <= float(thresholds["pure_noise_pair_hand_probability_maximum_difference"]),
        "exact_hand_key_marginal": hand_key_error
        <= float(thresholds["hand_key_marginal_maximum_error"]),
        "bounded_residual": residual_maximum <= RESIDUAL_GAIN + 1e-7,
        "common_mode_invariance": mutation_metrics["common_mode_logit_maximum_error"]
        <= float(thresholds["common_mode_logit_maximum_error"]),
        "causal_future_tail_prefix_invariance": mutation_metrics[
            "causal_future_tail_prefix_logit_maximum_error"
        ]
        <= float(thresholds["causal_future_tail_prefix_logit_maximum_error"]),
    }
    metrics = {
        "signal_bearing_rows": int(positive.sum()),
        "signal_bearing_hand_accuracy": full_hand_accuracy,
        "signal_bearing_key_accuracy": full_key_accuracy,
        "all_views_muted_hand_accuracy": muted_hand_accuracy,
        "factor_diagnostics": factor_diagnostics,
        "mixed_full_hand_NLL": mixed_full_nll,
        "mixed_all_views_muted_hand_NLL": mixed_muted_nll,
        "spatial_reversal_unmirrored_hand_accuracy": spatial_unmirrored_accuracy,
        "spatial_reversal_mirrored_hand_accuracy": spatial_mirrored_accuracy,
        "timing_only_pair_hand_probability_maximum_difference": timing_difference,
        "pure_noise_pair_hand_probability_maximum_difference": noise_difference,
        "hand_key_marginal_maximum_error": hand_key_error,
        "bounded_residual_maximum_absolute_value": residual_maximum,
        "peripheral_proxy_only_hand_accuracy": _accuracy(
            outputs["peripheral_proxy_only"]["hand_probabilities"][
                factors == "peripheral_like_common_mode_artifact"
            ],
            hands[factors == "peripheral_like_common_mode_artifact"],
        ),
        "channel_deranged_signal_bearing_hand_accuracy": _accuracy(
            outputs["channel_deranged"]["hand_probabilities"][positive], hands[positive]
        ),
        "time_displaced_signal_bearing_hand_accuracy": _accuracy(
            outputs["time_displaced"]["hand_probabilities"][positive], hands[positive]
        ),
    }
    return metrics, gates, mutation_metrics


def _score_final_partition(
    *,
    inputs: CMLSyntheticInputs,
    outputs: Mapping[str, Mapping[str, Any]],
    contract: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, bool]]:
    np = _require_numpy()
    indices = np.flatnonzero(inputs.partition_ids == "final")
    hands, keys = _targets_for_indices(inputs, indices, contract=contract)
    factors = inputs.factor_ids[indices]
    positive = np.isin(factors, np.asarray(POSITIVE_FACTORS))
    full = outputs["full"]
    hand_accuracy = _accuracy(full["hand_probabilities"][positive], hands[positive])
    key_accuracy = _accuracy(full["key_probabilities"][positive], keys[positive])
    spatial = factors == "left_right_spatial_reversal"
    mirrored_accuracy = _accuracy(
        outputs["hemisphere_mirrored"]["hand_probabilities"][spatial],
        hands[spatial],
    )
    timing_difference = _maximum_pair_probability_difference(
        inputs,
        indices,
        factor_id="timing_only_labels_without_signal_relation",
        probabilities=full["hand_probabilities"],
    )
    noise_difference = _maximum_pair_probability_difference(
        inputs,
        indices,
        factor_id="pure_noise",
        probabilities=full["hand_probabilities"],
    )
    hand_key_error = _maximum_hand_key_marginal_error(full)
    thresholds = contract["conditional_final_acceptance_gates"]
    metrics = {
        "signal_bearing_rows": int(positive.sum()),
        "signal_bearing_hand_accuracy": hand_accuracy,
        "signal_bearing_key_accuracy": key_accuracy,
        "mirrored_spatial_reversal_hand_accuracy": mirrored_accuracy,
        "timing_only_pair_hand_probability_maximum_difference": timing_difference,
        "pure_noise_pair_hand_probability_maximum_difference": noise_difference,
        "hand_key_marginal_maximum_error": hand_key_error,
    }
    gates = {
        "signal_bearing_hand_accuracy": hand_accuracy
        >= float(thresholds["signal_bearing_hand_accuracy_minimum"]),
        "signal_bearing_key_accuracy": key_accuracy
        >= float(thresholds["signal_bearing_key_accuracy_minimum"]),
        "mirrored_spatial_reversal_hand_accuracy": mirrored_accuracy
        >= float(thresholds["mirrored_spatial_reversal_hand_accuracy_minimum"]),
        "timing_only_pair_probability_equality": timing_difference
        <= float(thresholds["timing_only_pair_hand_probability_maximum_difference"]),
        "pure_noise_pair_probability_equality": noise_difference
        <= float(thresholds["pure_noise_pair_hand_probability_maximum_difference"]),
        "exact_hand_key_marginal": hand_key_error
        <= float(thresholds["hand_key_marginal_maximum_error"]),
        "deterministic_replay_prediction_hash_match": False,
    }
    return metrics, gates


def _causal_and_common_mode_checks(
    *,
    torch: Any,
    model: Any,
    inputs: CMLSyntheticInputs,
    indices: Any,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _require_numpy()
    signal = inputs.normalized_signal[indices]
    time_axis = np.arange(CROP_SAMPLES, dtype="float32") / 128.0
    common = 0.5 * np.sin(2.0 * math.pi * 3.0 * time_axis)
    common_signal = (signal + common[None, None, :]).astype("float32")
    full_mask = torch.ones((len(indices), CROP_SAMPLES), dtype=torch.bool)
    with torch.no_grad():
        original_logits = model(
            torch.as_tensor(signal, dtype=torch.float32),
            full_mask,
        )["key_logits"]
        common_logits = model(
            torch.as_tensor(common_signal, dtype=torch.float32),
            full_mask,
        )["key_logits"]
    common_error = float((original_logits - common_logits).abs().max().cpu().item())

    source = inputs.source_crops[indices]
    amplitude = 0.25 * np.arange(1, SOURCE_CHANNELS + 1, dtype="float32")
    maximum_prefix_error = 0.0
    cutoff_errors: dict[str, float] = {}
    for cutoff in contract["mutation_contract"]["causal_prefix_cutoffs_samples"]:
        mutated = source.copy()
        mutated[:, :, int(cutoff) :] += amplitude[None, :, None]
        projected = np.einsum(
            "oc,nct->not",
            inputs.projection,
            mutated,
            optimize=False,
        ).astype("float32")
        mutated_normalized = (
            (projected - inputs.normalization_location[None, :, None])
            / inputs.normalization_scale[None, :, None]
        ).astype("float32")
        prefix_mask = np.zeros((len(indices), CROP_SAMPLES), dtype="bool")
        prefix_mask[:, : int(cutoff)] = True
        with torch.no_grad():
            base = model(
                torch.as_tensor(signal, dtype=torch.float32),
                torch.as_tensor(prefix_mask, dtype=torch.bool),
            )["key_logits"]
            changed = model(
                torch.as_tensor(mutated_normalized, dtype=torch.float32),
                torch.as_tensor(prefix_mask, dtype=torch.bool),
            )["key_logits"]
        error = float((base - changed).abs().max().cpu().item())
        cutoff_errors[str(cutoff)] = error
        maximum_prefix_error = max(maximum_prefix_error, error)
    return {
        "common_mode_logit_maximum_error": common_error,
        "causal_future_tail_prefix_logit_maximum_error": maximum_prefix_error,
        "causal_prefix_cutoff_errors": cutoff_errors,
        "common_mode_applied_after_train_normalization": True,
        "future_tail_mutation_applied_only_after_declared_cutoff": True,
    }


def _checkpoint_arrays(
    *,
    model: Any,
    inputs: CMLSyntheticInputs,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    arrays: dict[str, Any] = {
        "normalization_location": inputs.normalization_location,
        "normalization_scale": inputs.normalization_scale,
        "projection": inputs.projection,
        "lattice_incidence": build_lattice_incidence(contract=contract),
    }
    for name, value in sorted(model.state_dict().items()):
        member = f"state__{name.replace('.', '__')}"
        arrays[member] = value.detach().cpu().numpy()
    return arrays


def _load_checkpoint_model(
    checkpoint_payload: bytes,
    *,
    contract: Mapping[str, Any],
) -> Any:
    np = _require_numpy()
    torch, _ = _require_torch()
    model = build_causal_motor_lattice_model(contract=contract)
    with np.load(io.BytesIO(checkpoint_payload), allow_pickle=False) as archive:
        state = {}
        for name in model.state_dict():
            member = f"state__{name.replace('.', '__')}"
            if member not in archive.files:
                raise ValueError("CML-v0 checkpoint state member missing")
            state[name] = torch.as_tensor(archive[member]).clone()
    model.load_state_dict(state, strict=True)
    model.eval()
    validate_causal_motor_lattice_model(model, contract=contract)
    return model


def _replay_prediction_hashes(
    *,
    torch: Any,
    model: Any,
    inputs: CMLSyntheticInputs,
    check_outputs: Mapping[str, Mapping[str, Any]],
    final_outputs: Mapping[str, Mapping[str, Any]] | None,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    replayed: dict[str, Any] = {}
    for partition, original in (("check", check_outputs), ("final", final_outputs)):
        if original is None:
            continue
        np = _require_numpy()
        indices = np.flatnonzero(inputs.partition_ids == partition)
        signal = torch.as_tensor(inputs.normalized_signal[indices], dtype=torch.float32)
        mask = torch.as_tensor(inputs.valid_mask[indices], dtype=torch.bool)
        with torch.no_grad():
            output = _detach_prediction(model(signal, mask))
        expected_hash = _raw_array_sha256(
            original["full"]["key_probabilities"],
            dtype="<f4",
        )
        observed_hash = _raw_array_sha256(output["key_probabilities"], dtype="<f4")
        replayed[partition] = {
            "expected_prediction_sha256": expected_hash,
            "replayed_prediction_sha256": observed_hash,
            "match": expected_hash == observed_hash,
        }
    return {
        "second_training_run": False,
        "checkpoint_loads": 1,
        "prediction_sets": len(replayed),
        "partitions": replayed,
        "all_hashes_match": all(value["match"] for value in replayed.values()),
    }


def _targets_for_indices(
    inputs: CMLSyntheticInputs,
    indices: Any,
    *,
    contract: Mapping[str, Any],
) -> tuple[Any, Any]:
    np = _require_numpy()
    hand = np.asarray(inputs.synthetic_hand_class[indices], dtype="int64")
    keys = np.zeros(len(indices), dtype="int64")
    mapping = contract["synthetic_target_map"]
    for local, row_index in enumerate(indices.tolist()):
        factor_id = str(inputs.factor_ids[row_index])
        keys[local] = int(mapping[factor_id][int(hand[local])])
    return hand, keys


def _accuracy(probabilities: Any, targets: Any) -> float:
    np = _require_numpy()
    if len(targets) == 0:
        raise ValueError("CML-v0 accuracy received no rows")
    return float(np.mean(np.argmax(probabilities, axis=1) == targets))


def _negative_log_likelihood(probabilities: Any, targets: Any) -> float:
    np = _require_numpy()
    selected = probabilities[np.arange(len(targets)), targets]
    return float(np.mean(-np.log(np.maximum(selected, 1e-12))))


def _maximum_pair_probability_difference(
    inputs: CMLSyntheticInputs,
    partition_indices: Any,
    *,
    factor_id: str,
    probabilities: Any,
) -> float:
    np = _require_numpy()
    local_rows = np.flatnonzero(inputs.factor_ids[partition_indices] == factor_id)
    pair_values = inputs.pair_ids[partition_indices][local_rows]
    maximum = 0.0
    for pair in sorted(set(pair_values.tolist())):
        members = local_rows[pair_values == pair]
        if members.shape != (2,):
            raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")
        maximum = max(
            maximum,
            float(np.max(np.abs(probabilities[members[0]] - probabilities[members[1]]))),
        )
    return maximum


def _maximum_hand_key_marginal_error(output: Mapping[str, Any]) -> float:
    np = _require_numpy()
    key = output["key_probabilities"]
    left = key[:, :14].sum(axis=1)
    right = key[:, 14:28].sum(axis=1)
    eligible = np.maximum(left + right, 1e-12)
    recomputed = np.stack((left / eligible, right / eligible), axis=1)
    return float(np.max(np.abs(recomputed - output["hand_probabilities"])))


def _validate_pair_equalities(
    np: Any,
    crops: Any,
    factors: Any,
    partitions: Any,
    pairs: Any,
) -> None:
    for factor_id in (
        "timing_only_labels_without_signal_relation",
        "pure_noise",
    ):
        factor_pairs = sorted(set(pairs[factors == factor_id].tolist()))
        for pair_id in factor_pairs:
            rows = np.flatnonzero(pairs == pair_id)
            if rows.shape != (2,) or partitions[rows[0]] != partitions[rows[1]]:
                raise ValueError("CML-SYN-F03-source-shape-or-partition-mismatch")
            if not np.array_equal(crops[rows[0]], crops[rows[1]]):
                raise ValueError("CML-SYN-F05-timing-or-noise-pair-waveform-mismatch")


def _result_access_counters(
    *,
    inputs: CMLSyntheticInputs,
    check_passed: bool,
    final_delivered: bool,
) -> dict[str, int]:
    return {
        "synthetic_fixture_generations": 1,
        "synthetic_signal_bytes_generated": int(inputs.source_bytes_generated),
        "model_or_checkpoint_loads": 1,
        "parameter_update_runs": 1,
        "optimizer_steps": 600,
        "model_inference_stages": 3 if final_delivered else 2,
        "prediction_sets": (18 if final_delivered else 9) + (2 if final_delivered else 1),
        "check_scoring_events": 1,
        "final_scoring_events": 1 if final_delivered else 0,
        "real_or_public_data_reads": 0,
        "protected_target_or_label_reads": 0,
        "S20_path_stats_or_reads": 0,
        "PhysioNet_downloads_or_reads": 0,
        "network_calls": 0,
        "provider_calls": 0,
        "pretrained_weight_or_external_embedding_reads": 0,
        "stream_device_or_hardware_operations": 0,
        "release_operations": 0,
        "scientific_claim_upgrades": 0,
    }


def _validate_execution_preconditions(
    *,
    out_dir: str | Path,
    implementation_commit: str,
    implementation_ci_run: int,
    contract: Mapping[str, Any],
    implementation_registry_path: str | Path | None,
    max_output_bytes: int,
) -> None:
    if max_output_bytes <= 0 or max_output_bytes > MAX_OUTPUT_BYTES:
        raise ValueError("CML-SYN-F19-output-file-byte-or-schema-cap")
    output = Path(out_dir)
    if output.exists():
        raise FileExistsError(f"refusing to replace CML-v0 output directory: {output}")
    if len(implementation_commit) != 40 or any(
        character not in "0123456789abcdef" for character in implementation_commit
    ):
        raise ValueError("exact 40-character implementation commit is required")
    if int(implementation_ci_run) <= 0:
        raise ValueError("positive remote CI run ID is required")
    if contract["execution_order"][
        "exact_implementation_commit_must_be_pushed_and_remotely_green_before_execution"
    ] is not True:
        raise ValueError("CML-v0 execution-order contract drifted")
    root = _repo_root()
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head != implementation_commit:
        raise ValueError("implementation commit must equal current HEAD")
    tracked_status = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if tracked_status.strip():
        raise ValueError("tracked worktree must be clean before CML-v0 execution")
    registry = _load_implementation_registry(
        implementation_registry_path,
        require_source_hashes=True,
    )
    for binding in registry["source_bindings"].values():
        path = str(binding["path"])
        committed = subprocess.run(
            ["git", "show", f"{implementation_commit}:{path}"],
            cwd=root,
            check=True,
            capture_output=True,
        ).stdout
        if hashlib.sha256(committed).hexdigest() != binding["sha256"]:
            raise ValueError("implementation commit source binding mismatch")


def _load_implementation_registry(
    path: str | Path | None,
    *,
    require_source_hashes: bool,
) -> dict[str, Any]:
    source = (
        Path(path)
        if path is not None
        else _repo_root() / IMPLEMENTATION_REGISTRY_RELATIVE_PATH
    )
    registry = json.loads(source.read_text(encoding="utf-8"))
    if registry.get("schema_name") != (
        "neurodecodekit.causal_motor_lattice_synthetic_implementation"
    ):
        raise ValueError("CML-v0 implementation registry schema mismatch")
    if registry.get("schema_version") != "0.1.0":
        raise ValueError("CML-v0 implementation registry version mismatch")
    if registry.get("status") != "implementation_qualified_not_executed":
        raise ValueError("CML-v0 implementation registry status mismatch")
    if registry.get("contract_binding", {}).get("sha256") != REGISTERED_CONTRACT_SHA256:
        raise ValueError("CML-v0 implementation contract binding mismatch")
    if require_source_hashes:
        for binding in registry["source_bindings"].values():
            source_path = _repo_root() / binding["path"]
            if _json_file_sha256(source_path) != binding["sha256"]:
                raise ValueError(f"CML-v0 implementation source hash mismatch: {binding['path']}")
    return registry


def _verify_contract_source_bindings(contract: Mapping[str, Any]) -> None:
    for binding in contract["source_bindings"].values():
        path = _repo_root() / binding["path"]
        if _json_file_sha256(path) != binding["sha256"]:
            raise ValueError(f"CML-SYN-F02-source-fixture-hash-mismatch: {binding['path']}")


def _deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    np = _require_numpy()
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(arrays):
            member = io.BytesIO()
            np.save(member, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, member.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return output.getvalue()


def _npz_member_inventory(path: Path) -> tuple[tuple[str, ...], int]:
    try:
        with zipfile.ZipFile(path, mode="r") as archive:
            entries = archive.infolist()
    except zipfile.BadZipFile as exc:
        raise ValueError("CML-v0 checkpoint is not a valid NPZ") from exc
    names: list[str] = []
    uncompressed = 0
    for entry in entries:
        member = PurePosixPath(entry.filename)
        if member.is_absolute() or len(member.parts) != 1 or member.suffix != ".npy":
            raise ValueError("CML-v0 checkpoint contains unsafe member")
        names.append(member.stem)
        uncompressed += int(entry.file_size)
    if len(names) != len(set(names)):
        raise ValueError("CML-v0 checkpoint contains duplicate members")
    return tuple(names), uncompressed


def _self_sized_report_payload(report: dict[str, Any]) -> bytes:
    for _ in range(12):
        payload = (_canonical_json(report, pretty=True) + "\n").encode("utf-8")
        report["resources"]["report_bytes"] = len(payload)
        report["resources"]["total_generated_output_bytes"] = (
            report["resources"]["checkpoint_bytes"] + len(payload)
        )
        report["artifacts"]["report"]["bytes"] = len(payload)
    return (_canonical_json(report, pretty=True) + "\n").encode("utf-8")


def _validate_forbidden_report_keys(value: Any, *, prefix: str = "") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_REPORT_KEY_FRAGMENTS):
                raise ValueError(f"CML-v0 report contains forbidden field: {prefix}{key}")
            _validate_forbidden_report_keys(nested, prefix=f"{prefix}{key}.")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _validate_forbidden_report_keys(nested, prefix=f"{prefix}{index}.")


def _raw_array_sha256(value: Any, *, dtype: str | None = None) -> str:
    np = _require_numpy()
    array = np.asarray(value, dtype=dtype, order="C")
    if array.dtype.kind in {"U", "S"}:
        payload = _canonical_json(array.tolist()).encode("utf-8")
    else:
        payload = array.tobytes(order="C")
    return hashlib.sha256(payload).hexdigest()


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _json_file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: Any, *, pretty: bool = False) -> str:
    if pretty:
        return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _free_disk_bytes_for(path: Path) -> int:
    parent = path.parent
    while not parent.exists() and parent != parent.parent:
        parent = parent.parent
    return int(shutil.disk_usage(parent).free)


def _require_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("NumPy is required. Install with: pip install -e '.[neuro]'") from exc
    return np


def _require_torch() -> tuple[Any, Any]:
    try:
        import torch
        from torch.nn import functional
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError("PyTorch is required. Install with: pip install -e '.[ml]'") from exc
    return torch, functional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
