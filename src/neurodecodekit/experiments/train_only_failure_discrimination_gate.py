"""Staged execution gate for the registered Loop 48 Stage B diagnostic."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import shutil
import subprocess
import time
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from neurodecodekit.cache.row_streaming_npz import (
    inspect_npz_members,
    read_npz_json_scalar,
    sha256_file_once,
    stream_npz_rows,
)
from neurodecodekit.evaluation.metrics import character_error_rate
from neurodecodekit.evaluation.train_only_failure_discrimination import (
    CHECK_ROWS,
    FINE_SHIFT_OFFSETS,
    FIT_PREFIX_SIZES,
    PRIMARY_SEED,
    SEEDS,
    apply_channel_derangement,
    apply_nonwrapping_shift,
    build_prediction_freeze_record,
    candidate_condition_id,
    derange_check_predictions,
    derange_fit_targets,
    diagnostic_split,
    expected_fit_ids,
    expected_prediction_ids,
    file_sha256,
    fine_shift_condition_id,
    linear_condition_id,
    load_prediction_payload,
    peak_rss_bytes,
    prior_condition_id,
    score_failure_discrimination,
    sha256_json,
    timing_only_signals,
    validate_prediction_freeze_record,
    write_prediction_payload,
    zero_signals,
)
from neurodecodekit.models.tiny_causal_sentence_ctc import (
    build_causal_sentence_ctc,
    registered_candidate_config,
    registered_linear_config,
)
from neurodecodekit.preprocess.ctc_text import (
    decode_ctc_target,
    greedy_decode_ctc_ids,
    normalize_ctc_text,
)


CONTRACT_PATH = "registries/loop48_train_only_discrimination_contract.v0.json"
AUTHORIZATION_PATH = "registries/loop48_stage_b_authorization_decision.v0.json"
LOOP26_CONTRACT_PATH = "registries/loop26_shared_validation_contract.v0.json"
REGISTERED_OUTPUT_ROOT = ".codex_work/loop48_stage_b"
STATIC_REPORT_NAME = "static_gate.json"
DERIVATIVE_REPORT_NAME = "derivatives.json"
TARGET_BLIND_REPORT_NAME = "target_blind_run.json"
CONSUMED_MARKER_NAME = "check_scoring_consumed.json"
FIT_BUNDLE_NAME = "fit_bundle.npz"
CHECK_INPUTS_NAME = "check_inputs.npz"
CHECK_TARGETS_NAME = "check_targets.npz"
FREEZE_SCHEMA_NAME = "neurodecodekit.loop48_stage_b_prediction_freeze"


class StageBGateError(RuntimeError):
    """Raised when a registered identity, access, or resource gate fails."""


def new_runtime_access_counters() -> dict[str, int]:
    """Return exactly the machine-registered access counter inventory."""

    root = Path(__file__).resolve().parents[3]
    contract = _read_json(root / CONTRACT_PATH)
    return {str(name): 0 for name in contract["required_runtime_access_counters"]}


def run_static_stage_b_gate(
    *,
    repo_root: str | Path,
    implementation_commit: str,
    implementation_push_ci_run_id: int,
    implementation_pr_ci_run_id: int,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Bind identities and target-free metadata before signals or targets open."""

    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    report_path = output / STATIC_REPORT_NAME
    _refuse_existing(report_path)
    started_at = time.perf_counter()
    counters = new_runtime_access_counters()
    contract_path = root / CONTRACT_PATH
    authorization_path = root / AUTHORIZATION_PATH
    contract = _read_json(contract_path)
    authorization = _read_json(authorization_path)
    checks: dict[str, bool] = {}

    checks["authorization_status"] = (
        authorization.get("status") == "authorized_no_implementation_or_execution_yet"
    )
    checks["authorization_contract_hash"] = authorization["authorized_contract"][
        "sha256"
    ] == file_sha256(contract_path)
    checks["authorization_exact_scope"] = all(
        bool(value)
        for key, value in authorization["authorization"].items()
        if key.endswith("authorized_now")
        and key
        in {
            "stage_b_implementation_authorized_now",
            "one_source_cache_sha256_pass_authorized_now",
            "target_free_split_metadata_read_authorized_now",
            "opaque_deflated_member_traversal_authorized_now",
            "fit_and_check_derivative_creation_authorized_now",
            "forty_four_fit_signal_target_row_delivery_authorized_now",
            "eleven_check_signal_row_pre_freeze_delivery_authorized_now",
            "twenty_parameter_update_runs_authorized_now",
            "thirty_five_target_blind_inference_runs_authorized_now",
            "five_train_only_prior_fits_authorized_now",
            "forty_one_prediction_sets_authorized_now",
            "one_registered_stage_b_execution_authorized_now",
        }
    )
    checks["implementation_commit_format"] = len(str(implementation_commit)) == 40
    checks["implementation_commit_is_head"] = _git_head(root) == str(implementation_commit)
    checks["tracked_worktree_clean"] = _tracked_worktree_clean(root)
    checks["implementation_push_ci_run_id_recorded"] = implementation_push_ci_run_id > 0
    checks["implementation_pr_ci_run_id_recorded"] = implementation_pr_ci_run_id > 0
    checks["single_thread_environment"] = _single_thread_environment_ok()
    checks["output_root_git_ignored"] = _path_git_ignored(root, output)
    free_disk_bytes = shutil.disk_usage(root).free
    checks["minimum_free_disk"] = (
        free_disk_bytes >= contract["resource_caps"]["minimum_free_disk_bytes_before_execution"]
    )
    for binding in [
        *contract["dependency_bindings"].values(),
        *contract["implementation_source_bindings"].values(),
    ]:
        path = root / binding["path"]
        checks[f"binding:{binding['path']}"] = (
            path.is_file() and file_sha256(path) == binding["sha256"]
        )

    source = contract["source_contract"]
    cache_contract = source["cache"]
    cache_path = root / cache_contract["path"]
    counters["source_cache_stat_reads"] += 1
    checks["source_cache_exists"] = cache_path.is_file()
    checks["source_cache_bytes"] = (
        cache_path.is_file() and cache_path.stat().st_size == cache_contract["bytes"]
    )
    split_contract = source["split_report"]
    split_path = root / split_contract["path"]
    checks["split_report_hash"] = (
        split_path.is_file() and file_sha256(split_path) == split_contract["sha256"]
    )
    split = _read_json(split_path)
    counters["split_report_metadata_reads"] += 1
    checks.update(_validate_split_report(split, source))
    membership_rows = (split.get("membership") or {}).get("rows") or []
    train_rows = [row for row in membership_rows if row.get("split") == "train"]
    registered_split = diagnostic_split(train_rows)
    checks["diagnostic_fit_rows"] = registered_split["fit_rows"] == 44
    checks["diagnostic_check_rows"] = registered_split["check_rows"] == 11

    loop26_contract = _read_json(root / LOOP26_CONTRACT_PATH)
    loop26_source = loop26_contract["source_contract"]
    expected_members = {
        "signals": (tuple(cache_contract["shape"]), cache_contract["dtype"]),
        "input_lengths": ((cache_contract["shape"][0],), "int32"),
        "target_token_ids": (
            tuple(loop26_source["ctc_arrays"]["target_token_ids_shape"]),
            "int16",
        ),
        "target_lengths": (
            tuple(loop26_source["ctc_arrays"]["target_lengths_shape"]),
            "int32",
        ),
        "target_texts": (
            tuple(loop26_source["ctc_arrays"]["target_texts_shape"]),
            None,
        ),
        "channel_names": ((source["channels"]["count"],), None),
        "metadata": ((), None),
    }
    headers = inspect_npz_members(cache_path, member_names=expected_members)
    counters["archive_header_reads"] += len(headers)
    for name, (shape, dtype) in expected_members.items():
        header = headers.get(f"{name}.npy")
        checks[f"header:{name}:present"] = header is not None
        checks[f"header:{name}:shape"] = header is not None and header.shape == shape
        if dtype is not None:
            checks[f"header:{name}:dtype"] = header is not None and header.dtype == dtype

    channel_rows = stream_npz_rows(
        cache_path,
        "channel_names",
        range(source["channels"]["count"]),
        expected_shape=(source["channels"]["count"],),
    )
    counters["archive_header_reads"] += 1
    counters["archive_row_member_streams"] += 1
    counters["opaque_excluded_rows_traversed"] += channel_rows.opaque_excluded_rows_traversed
    channel_names = [str(value) for value in channel_rows.values.tolist()]
    checks["ordered_channel_names_sha256"] = (
        sha256_json(channel_names) == source["channels"]["ordered_names_sha256"]
    )
    metadata = read_npz_json_scalar(cache_path)
    counters["archive_header_reads"] += 1
    counters["archive_row_member_streams"] += 1
    checks["metadata_schema"] = (metadata.get("schema") or {}) == {
        "name": cache_contract["schema_name"],
        "version": cache_contract["schema_version"],
    }
    metadata_text = json.dumps(metadata, sort_keys=True)
    checks["metadata_scaler_center"] = source["frozen_scaler"]["center_sha256"] in metadata_text
    checks["metadata_scaler_scale"] = source["frozen_scaler"]["scale_sha256"] in metadata_text

    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema_name": "neurodecodekit.loop48_stage_b_static_gate",
        "schema_version": "0.1.0",
        "status": "passed" if not failed else "failed",
        "proof_posture": "target_free_identity_gate_no_signal_or_target_values",
        "implementation": {
            "commit": str(implementation_commit),
            "push_ci_run_id": int(implementation_push_ci_run_id),
            "pr_ci_run_id": int(implementation_pr_ci_run_id),
            "operator_confirmed_both_runs_green_before_execution": True,
        },
        "contract_sha256": file_sha256(contract_path),
        "authorization_decision_sha256": file_sha256(authorization_path),
        "checks": checks,
        "failed_checks": failed,
        "source_cache": {
            "path": cache_contract["path"],
            "input_bytes": cache_contract["bytes"],
            "expected_sha256": cache_contract["sha256"],
            "hash_passes": 0,
        },
        "source_partition_counts": {
            key: sum(row.get("split") == key for row in membership_rows)
            for key in ("train", "val", "test")
        },
        "diagnostic_split": registered_split,
        "channel_names": channel_names,
        "archive_headers": {name: header.to_dict() for name, header in headers.items()},
        "access_counters": counters,
        "environment": _environment_versions(),
        "resources": {
            "free_disk_bytes_before_execution": free_disk_bytes,
            "minimum_free_disk_bytes": contract["resource_caps"][
                "minimum_free_disk_bytes_before_execution"
            ],
            "runtime_sec": round(time.perf_counter() - started_at, 6),
            "peak_rss_bytes": peak_rss_bytes(),
            "generated_artifact_bytes_before_report": _directory_bytes(output),
        },
        "producer": {
            "model_is_causal": True,
            "model_right_context_frames": 0,
            "model_left_context_frames": 2,
            "upstream_cache_is_causal": False,
            "end_to_end_latency_measured": False,
        },
        "warnings": [
            "static_gate_reads_target_free_split_metadata_headers_channel_names_and_cache_metadata",
            "source_cache_hash_is_deferred_to_the_single_registered_hash_pass",
            "upstream_sentence_cache_is_offline_noncausal",
            "implementation_ci_run_ids_are_operator_confirmed_remote_green_evidence",
        ],
    }
    _write_bounded_json(report_path, report, maximum_bytes=2 * 1024 * 1024)
    if failed:
        raise StageBGateError(f"Loop 48 Stage B static gate failed: {failed}")
    return report


def create_stage_b_derivatives(
    *,
    repo_root: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Hash once and create only fit plus target-free check-input derivatives."""

    np = _require_numpy()
    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    static = _read_json(output / STATIC_REPORT_NAME)
    if static.get("status") != "passed":
        raise StageBGateError("static gate must pass before derivative creation")
    report_path = output / DERIVATIVE_REPORT_NAME
    fit_path = output / FIT_BUNDLE_NAME
    check_path = output / CHECK_INPUTS_NAME
    for path in (report_path, fit_path, check_path):
        _refuse_existing(path)
    started_at = time.perf_counter()
    contract = _read_json(root / CONTRACT_PATH)
    source = contract["source_contract"]
    cache_contract = source["cache"]
    cache_path = root / cache_contract["path"]
    counters = {key: int(value) for key, value in static["access_counters"].items()}
    hash_report = sha256_file_once(
        cache_path,
        expected_bytes=cache_contract["bytes"],
        expected_sha256=cache_contract["sha256"],
    )
    counters["source_cache_hash_passes"] += 1
    split = static["diagnostic_split"]
    fit_indices = [int(value) for value in split["fit_source_row_indices"]]
    check_indices = [int(value) for value in split["check_source_row_indices"]]
    if len(fit_indices) != 44 or len(check_indices) != 11:
        raise StageBGateError("diagnostic split drifted from the registered 44/11 assignment")
    selected_indices = [*fit_indices, *check_indices]
    loop26_source = _read_json(root / LOOP26_CONTRACT_PATH)["source_contract"]
    signals = stream_npz_rows(
        cache_path,
        "signals",
        selected_indices,
        expected_shape=cache_contract["shape"],
        expected_dtype="float32",
    )
    lengths = stream_npz_rows(
        cache_path,
        "input_lengths",
        selected_indices,
        expected_shape=(cache_contract["shape"][0],),
        expected_dtype="int32",
    )
    fit_target_ids = stream_npz_rows(
        cache_path,
        "target_token_ids",
        fit_indices,
        expected_shape=loop26_source["ctc_arrays"]["target_token_ids_shape"],
        expected_dtype="int16",
    )
    fit_target_lengths = stream_npz_rows(
        cache_path,
        "target_lengths",
        fit_indices,
        expected_shape=loop26_source["ctc_arrays"]["target_lengths_shape"],
        expected_dtype="int32",
    )
    fit_target_texts = stream_npz_rows(
        cache_path,
        "target_texts",
        fit_indices,
        expected_shape=loop26_source["ctc_arrays"]["target_texts_shape"],
    )
    streams = [signals, lengths, fit_target_ids, fit_target_lengths, fit_target_texts]
    counters["archive_header_reads"] += len(streams)
    counters["archive_row_member_streams"] += len(streams)
    counters["opaque_excluded_rows_traversed"] += sum(
        row.opaque_excluded_rows_traversed for row in streams
    )

    fit_signals = np.ascontiguousarray(signals.values[:44], dtype="float32")
    check_signals = np.ascontiguousarray(signals.values[44:], dtype="float32")
    fit_input_lengths = np.ascontiguousarray(lengths.values[:44], dtype="int32")
    check_input_lengths = np.ascontiguousarray(lengths.values[44:], dtype="int32")
    target_texts = np.asarray(
        [normalize_ctc_text(str(value)) for value in fit_target_texts.values.tolist()]
    )
    _validate_fit_targets(
        fit_target_ids.values,
        fit_target_lengths.values,
        target_texts,
    )
    channel_names = np.asarray(static["channel_names"])
    fit_arrays = {
        "signals": fit_signals,
        "input_lengths": fit_input_lengths,
        "target_token_ids": np.ascontiguousarray(fit_target_ids.values, dtype="int16"),
        "target_lengths": np.ascontiguousarray(fit_target_lengths.values, dtype="int32"),
        "target_texts": target_texts,
        "channel_names": channel_names,
        "source_row_indices": np.asarray(fit_indices, dtype="int32"),
        "item_ids": np.asarray(split["fit_row_ids"]),
        "semantic_ids": np.asarray(split["fit_semantic_ids"]),
    }
    check_arrays = {
        "signals": check_signals,
        "input_lengths": check_input_lengths,
        "channel_names": channel_names,
        "source_row_indices": np.asarray(check_indices, dtype="int32"),
        "item_ids": np.asarray(split["check_row_ids"]),
        "semantic_ids": np.asarray(split["check_semantic_ids"]),
    }
    common_metadata = {
        "source_cache_sha256": hash_report["sha256"],
        "source_cache_bytes": hash_report["bytes"],
        "split_report_sha256": source["split_report"]["sha256"],
        "diagnostic_assignment_sha256": split["assignment_sha256"],
        "protocol_config_sha256": source["split_report"]["protocol_config_sha256"],
        "semantic_membership_sha256": source["split_report"]["semantic_membership_sha256"],
        "physical_membership_sha256": source["split_report"]["physical_membership_sha256"],
        "ordered_channel_names_sha256": source["channels"]["ordered_names_sha256"],
        "scaler_center_sha256": source["frozen_scaler"]["center_sha256"],
        "scaler_scale_sha256": source["frozen_scaler"]["scale_sha256"],
        "sampling_rate_hz": cache_contract["sampling_rate_hz"],
        "upstream_cache_causal": False,
    }
    fit_metadata = {
        "schema": {"name": "neurodecodekit.loop48_stage_b_fit_bundle", "version": 0},
        "diagnostic_partition": "fit",
        "contains_signals": True,
        "contains_targets": True,
        "rows": 44,
        **common_metadata,
    }
    check_metadata = {
        "schema": {"name": "neurodecodekit.loop48_stage_b_check_inputs", "version": 0},
        "diagnostic_partition": "check",
        "contains_signals": True,
        "contains_targets": False,
        "rows": 11,
        **common_metadata,
    }
    _write_npz(fit_path, fit_arrays, fit_metadata)
    _write_npz(check_path, check_arrays, check_metadata)
    counters["fit_signal_rows_delivered"] += 44
    counters["fit_target_rows_delivered"] += 44
    counters["check_signal_rows_delivered"] += 11
    static_audit = transformed_cache_audit(
        fit_signals=fit_signals,
        fit_input_lengths=fit_input_lengths,
        fit_target_token_ids=fit_arrays["target_token_ids"],
        fit_target_lengths=fit_arrays["target_lengths"],
        fit_item_ids=fit_arrays["item_ids"].tolist(),
        check_signals=check_signals,
        check_input_lengths=check_input_lengths,
        check_item_ids=check_arrays["item_ids"].tolist(),
        sampling_rate_hz=float(cache_contract["sampling_rate_hz"]),
    )
    working_array_bytes = _derivative_working_array_upper_bound(
        signals.values,
        lengths.values,
        fit_arrays,
        check_arrays,
    )
    caps = contract["resource_caps"]
    if working_array_bytes > caps["maximum_working_array_bytes"]:
        raise StageBGateError("derivative working arrays exceed 128 MiB cap")
    generated_before_report = _directory_bytes(output)
    if generated_before_report > caps["total_generated_artifact_bytes"]:
        raise StageBGateError("generated derivative artifacts exceed 32 MiB cap")
    report = {
        "schema_name": "neurodecodekit.loop48_stage_b_isolated_derivatives",
        "schema_version": "0.1.0",
        "status": "passed",
        "source_hash_pass": hash_report,
        "artifacts": {
            "fit_bundle": _artifact_descriptor(fit_path, fit_arrays, fit_metadata),
            "check_inputs": _artifact_descriptor(check_path, check_arrays, check_metadata),
        },
        "static_audit": static_audit,
        "validation_derivatives": 0,
        "source_test_derivatives": 0,
        "check_targets_present_before_green_freeze": False,
        "reader_ledgers": [row.ledger() for row in streams],
        "access_counters": counters,
        "resources": {
            "input_bytes": hash_report["bytes"],
            "output_bytes_before_report": generated_before_report,
            "working_array_bytes_upper_bound": working_array_bytes,
            "runtime_sec": round(time.perf_counter() - started_at, 6),
            "peak_rss_bytes": peak_rss_bytes(),
        },
        "warnings": [
            "deflate_required_opaque_traversal_of_excluded_rows",
            "opaque_traversal_is_not_physical_nonaccess",
            "check_target_values_were_not_returned_or_written",
            "validation_and_source_test_rows_were_not_returned",
            "transformed_cache_audit_cannot_assess_raw_sensor_quality",
        ],
    }
    _write_bounded_json(report_path, report, maximum_bytes=2 * 1024 * 1024)
    if _directory_bytes(output) > caps["total_generated_artifact_bytes"]:
        raise StageBGateError("final derivative artifacts exceed 32 MiB cap")
    return report


def transformed_cache_audit(
    *,
    fit_signals,
    fit_input_lengths,
    fit_target_token_ids,
    fit_target_lengths,
    fit_item_ids: Sequence[str],
    check_signals,
    check_input_lengths,
    check_item_ids: Sequence[str],
    sampling_rate_hz: float,
) -> dict[str, Any]:
    """Audit transformed arrays without interpreting absent raw-quality evidence."""

    np = _require_numpy()
    fit_values = np.asarray(fit_signals, dtype="float32")
    fit_lengths = np.asarray(fit_input_lengths, dtype="int64")
    target_ids = np.asarray(fit_target_token_ids, dtype="int64")
    target_lengths = np.asarray(fit_target_lengths, dtype="int64")
    check_values = np.asarray(check_signals, dtype="float32")
    check_lengths = np.asarray(check_input_lengths, dtype="int64")
    if fit_values.ndim != 3 or fit_values.shape[:2] != (len(fit_lengths), 102):
        raise StageBGateError("fit audit geometry is invalid")
    if check_values.ndim != 3 or check_values.shape[:2] != (len(check_lengths), 102):
        raise StageBGateError("check audit geometry is invalid")
    if target_ids.shape[0] != len(fit_values) or target_lengths.shape != (len(fit_values),):
        raise StageBGateError("fit audit target geometry is invalid")

    fit_trial_rows = _trial_quality_rows(
        fit_values, fit_lengths, fit_item_ids, sampling_rate_hz=sampling_rate_hz
    )
    check_trial_rows = _trial_quality_rows(
        check_values, check_lengths, check_item_ids, sampling_rate_hz=sampling_rate_hz
    )
    valid_blocks = [fit_values[index, :, : int(length)] for index, length in enumerate(fit_lengths)]
    valid_concat = np.concatenate(valid_blocks, axis=1)
    finite_concat = np.where(np.isfinite(valid_concat), valid_concat, np.nan)
    with np.errstate(invalid="ignore"):
        channel_variance = np.nanvar(finite_concat.astype("float64"), axis=1)
        channel_median = np.nanmedian(finite_concat.astype("float64"), axis=1)
        channel_mad = np.nanmedian(
            np.abs(finite_concat.astype("float64") - channel_median[:, None]), axis=1
        )
    ctc_rows = []
    for item_id, input_length, token_row, target_length in zip(
        fit_item_ids,
        fit_lengths,
        target_ids,
        target_lengths,
        strict=True,
    ):
        valid_tokens = token_row[: int(target_length)]
        repeats = int((valid_tokens[1:] == valid_tokens[:-1]).sum()) if len(valid_tokens) > 1 else 0
        minimum_steps = int(target_length) + repeats
        ctc_rows.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "input_length": int(input_length),
                "target_length": int(target_length),
                "adjacent_repeat_count": repeats,
                "minimum_alignment_steps": minimum_steps,
                "frame_to_target_ratio": int(input_length) / int(target_length),
                "alignment_feasible": int(input_length) >= minimum_steps,
            }
        )
    nonfinite = sum(row["nonfinite_count"] for row in (*fit_trial_rows, *check_trial_rows))
    nonzero_padding = sum(
        row["nonzero_padding_count"] for row in (*fit_trial_rows, *check_trial_rows)
    )
    channel_defects = [
        index
        for index, value in enumerate(channel_variance)
        if not math.isfinite(float(value)) or float(value) <= 1e-8
    ]
    near_flat_trials = [
        row["item_id_sha256"]
        for row in (*fit_trial_rows, *check_trial_rows)
        if row["trial_near_flat_channel_fraction"] >= 0.2
    ]
    infeasible = sum(not row["alignment_feasible"] for row in ctc_rows)
    gross_defect = bool(nonfinite or nonzero_padding or channel_defects or near_flat_trials)
    return {
        "scope": {
            "fit_rows_with_signal_and_ctc_feasibility": len(fit_trial_rows),
            "check_rows_with_target_free_signal_quality": len(check_trial_rows),
            "check_target_lengths_available_before_green_freeze": False,
        },
        "ctc_feasibility_rows": ctc_rows,
        "infeasible_row_count": infeasible,
        "fit_trial_quality": fit_trial_rows,
        "check_trial_quality": check_trial_rows,
        "fit_channel_variance": [_finite_or_none(value) for value in channel_variance],
        "fit_channel_median_absolute_deviation": [_finite_or_none(value) for value in channel_mad],
        "nonfinite_count": nonfinite,
        "nonzero_padding_count": nonzero_padding,
        "near_flat_global_channel_indices": channel_defects,
        "near_flat_trial_item_hashes": near_flat_trials,
        "gross_defect": gross_defect,
        "raw_sensor_quality_available": False,
        "bad_channel_annotations_available": False,
        "line_noise_interpretation_available": False,
        "head_motion_available": False,
        "peripheral_physiology_available": False,
        "passing_audit_weighs_against_H2": False,
    }


def _trial_quality_rows(
    values,
    lengths,
    item_ids: Sequence[str],
    *,
    sampling_rate_hz: float,
) -> list[dict[str, Any]]:
    np = _require_numpy()
    rows = []
    for index, (length_value, item_id) in enumerate(zip(lengths, item_ids, strict=True)):
        length = int(length_value)
        valid = values[index, :, :length]
        padding = values[index, :, length:]
        finite_valid = np.where(np.isfinite(valid), valid, np.nan).astype("float64")
        with np.errstate(invalid="ignore"):
            variances = np.nanvar(finite_valid, axis=1)
            rms = np.sqrt(np.nanmean(finite_valid * finite_valid))
            median_abs = np.nanmedian(np.abs(finite_valid))
        near_flat = np.logical_or(~np.isfinite(variances), variances <= 1e-8)
        rows.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "nonfinite_count": int((~np.isfinite(valid)).sum()),
                "nonzero_padding_count": int((padding != 0).sum()),
                "trial_rms": _finite_or_none(rms),
                "trial_median_absolute_amplitude": _finite_or_none(median_abs),
                "trial_near_flat_channel_fraction": float(near_flat.mean()),
                "sentence_duration_sec": length / sampling_rate_hz,
                "valid_sample_count": length,
            }
        )
    return rows


def _finite_or_none(value) -> float | None:
    measured = float(value)
    return measured if math.isfinite(measured) else None


def run_target_blind_stage_b_gate(
    *,
    repo_root: str | Path,
    implementation_commit: str,
    freeze_record_out: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Run exactly 20 fits and freeze 41 sets without check targets."""

    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    report_path = output / TARGET_BLIND_REPORT_NAME
    freeze_path = Path(freeze_record_out)
    if not freeze_path.is_absolute():
        freeze_path = root / freeze_path
    freeze_path = freeze_path.resolve()
    registered_freeze = (root / "registries/loop48_stage_b_prediction_freeze.v0.json").resolve()
    if enforce_registered_paths and freeze_path != registered_freeze:
        raise StageBGateError(f"registered prediction freeze must be {registered_freeze}")
    for path in (report_path, freeze_path, output / CONSUMED_MARKER_NAME):
        _refuse_existing(path)
    if _git_head(root) != str(implementation_commit):
        raise StageBGateError("target-blind run requires the remotely green implementation HEAD")
    if not _tracked_worktree_clean(root):
        raise StageBGateError("target-blind run requires a clean tracked worktree")
    derivatives = _read_json(output / DERIVATIVE_REPORT_NAME)
    if derivatives.get("status") != "passed":
        raise StageBGateError("isolated derivatives must pass before target-blind execution")
    fit = _load_derivative(
        output / FIT_BUNDLE_NAME,
        expected_schema="neurodecodekit.loop48_stage_b_fit_bundle",
    )
    check = _load_derivative(
        output / CHECK_INPUTS_NAME,
        expected_schema="neurodecodekit.loop48_stage_b_check_inputs",
    )
    _validate_target_blind_derivatives(fit, check)
    contract = _read_json(root / CONTRACT_PATH)
    counters = {key: int(value) for key, value in derivatives["access_counters"].items()}
    started_at = time.perf_counter()
    prediction_dir = output / "predictions"
    checkpoint_dir = output / "checkpoints"
    prediction_dir.mkdir(parents=True, exist_ok=False)
    checkpoint_dir.mkdir(parents=True, exist_ok=False)
    prediction_rows: list[dict[str, Any]] = []
    fit_rows: list[dict[str, Any]] = []
    checkpoint_descriptors: list[dict[str, Any]] = []
    primary_prediction: dict[str, Any] | None = None
    primary_checkpoint_sha256: str | None = None

    for size in FIT_PREFIX_SIZES:
        indices = list(range(size))
        prefix_targets = fit["target_texts"][indices].tolist()
        prior_prediction = _train_only_prior(prefix_targets)
        prior_id = prior_condition_id(size)
        prediction_rows.append(
            write_prediction_payload(
                prediction_dir / f"{prior_id}.json",
                condition_id=prior_id,
                item_ids=check["item_ids"].tolist(),
                predictions=[prior_prediction] * CHECK_ROWS,
                input_lengths=check["input_lengths"].tolist(),
                configuration={
                    "kind": "train_only_most_frequent_sentence_prior",
                    "prefix_size": size,
                    "fit_item_ids_sha256": sha256_json(fit["item_ids"][indices].tolist()),
                    "check_targets_available": False,
                },
                checkpoint_sha256_or_reason="no_checkpoint_train_only_prior",
                transform={"name": "no_signal_prior"},
                runtime_sec=0.0,
                peak_rss_bytes=peak_rss_bytes(),
                model_run_count=0,
                blank_fraction=None,
                warnings=["no_neural_signal_used"],
            )
        )
        counters["no_signal_prior_fits"] += 1
        for seed in SEEDS:
            condition_id = candidate_condition_id(size, seed)
            run = _run_fit_and_prediction(
                condition_id=condition_id,
                architecture="candidate",
                execution_seed=seed,
                prefix_size=size,
                fit_signals=fit["signals"][indices],
                fit_input_lengths=fit["input_lengths"][indices],
                target_token_ids=fit["target_token_ids"][indices],
                target_lengths=fit["target_lengths"][indices],
                target_texts=prefix_targets,
                fit_item_ids=fit["item_ids"][indices].tolist(),
                check_signals=check["signals"],
                check_input_lengths=check["input_lengths"],
                check_item_ids=check["item_ids"].tolist(),
                checkpoint_path=checkpoint_dir / f"{condition_id}.npz",
                prediction_path=prediction_dir / f"{condition_id}.json",
                transform={"name": "identity"},
            )
            prediction_rows.append(run["prediction_freeze_row"])
            fit_rows.append(run["fit_freeze_row"])
            checkpoint_descriptors.append(run["checkpoint"])
            counters["candidate_training_runs"] += 1
            counters["optimizer_steps"] += 240
            counters["checkpoint_writes"] += 1
            counters["target_blind_model_inference_runs"] += 1
            if size == 44:
                for offset in FINE_SHIFT_OFFSETS:
                    shifted, shift_report = apply_nonwrapping_shift(
                        check["signals"],
                        check["input_lengths"],
                        offset_samples=offset,
                    )
                    prediction_rows.append(
                        _write_control_inference(
                            condition_id=fine_shift_condition_id(offset, seed),
                            model=run["model"],
                            signals=shifted,
                            check=check,
                            checkpoint_sha256=run["checkpoint"]["sha256"],
                            transform={"name": "nonwrapping_time_shift", **shift_report},
                            configuration={
                                "source_model_condition_id": condition_id,
                                "execution_seed": seed,
                            },
                            prediction_dir=prediction_dir,
                        )
                    )
                    counters["target_blind_model_inference_runs"] += 1
                if seed == PRIMARY_SEED:
                    primary_prediction = run["prediction_payload"]
                    primary_checkpoint_sha256 = run["checkpoint"]["sha256"]
                    prediction_rows.append(
                        _write_control_inference(
                            condition_id="zero_signal",
                            model=run["model"],
                            signals=zero_signals(check["signals"]),
                            check=check,
                            checkpoint_sha256=primary_checkpoint_sha256,
                            transform={"name": "exact_zero_valid_and_padding_signal"},
                            configuration={"source_model_condition_id": condition_id},
                            prediction_dir=prediction_dir,
                        )
                    )
                    counters["target_blind_model_inference_runs"] += 1
                    channel_values, channel_mapping = apply_channel_derangement(
                        check["signals"], check["channel_names"].tolist()
                    )
                    prediction_rows.append(
                        _write_control_inference(
                            condition_id="channel_derangement",
                            model=run["model"],
                            signals=channel_values,
                            check=check,
                            checkpoint_sha256=primary_checkpoint_sha256,
                            transform={
                                "name": "channel_name_hash_derangement",
                                "mapping": channel_mapping,
                            },
                            configuration={"source_model_condition_id": condition_id},
                            prediction_dir=prediction_dir,
                        )
                    )
                    counters["target_blind_model_inference_runs"] += 1
                    severe, severe_report = apply_nonwrapping_shift(
                        check["signals"], check["input_lengths"], offset_samples=100
                    )
                    prediction_rows.append(
                        _write_control_inference(
                            condition_id="severe_plus100_sample_displacement",
                            model=run["model"],
                            signals=severe,
                            check=check,
                            checkpoint_sha256=primary_checkpoint_sha256,
                            transform={"name": "severe_time_displacement", **severe_report},
                            configuration={"source_model_condition_id": condition_id},
                            prediction_dir=prediction_dir,
                        )
                    )
                    counters["target_blind_model_inference_runs"] += 1
            del run["model"]

    if primary_prediction is None or primary_checkpoint_sha256 is None:
        raise StageBGateError("primary candidate prediction was not retained")
    row_predictions, row_mapping = derange_check_predictions(
        primary_prediction["predictions"], check["item_ids"].tolist()
    )
    prediction_rows.append(
        write_prediction_payload(
            prediction_dir / "check_row_derangement.json",
            condition_id="check_row_derangement",
            item_ids=check["item_ids"].tolist(),
            predictions=row_predictions,
            input_lengths=check["input_lengths"].tolist(),
            configuration={"source_prediction": candidate_condition_id(44, PRIMARY_SEED)},
            checkpoint_sha256_or_reason=primary_checkpoint_sha256,
            transform={"name": "check_row_hash_cycle", "mapping": row_mapping},
            runtime_sec=0.0,
            peak_rss_bytes=peak_rss_bytes(),
            model_run_count=0,
            blank_fraction=primary_prediction["blank_fraction"],
            warnings=["prediction_remap_no_model_run"],
        )
    )

    full_indices = list(range(44))
    for seed in SEEDS:
        condition_id = linear_condition_id(seed)
        run = _run_fit_and_prediction(
            condition_id=condition_id,
            architecture="linear",
            execution_seed=seed,
            prefix_size=44,
            fit_signals=fit["signals"],
            fit_input_lengths=fit["input_lengths"],
            target_token_ids=fit["target_token_ids"],
            target_lengths=fit["target_lengths"],
            target_texts=fit["target_texts"].tolist(),
            fit_item_ids=fit["item_ids"].tolist(),
            check_signals=check["signals"],
            check_input_lengths=check["input_lengths"],
            check_item_ids=check["item_ids"].tolist(),
            checkpoint_path=checkpoint_dir / f"{condition_id}.npz",
            prediction_path=prediction_dir / f"{condition_id}.json",
            transform={"name": "identity"},
        )
        prediction_rows.append(run["prediction_freeze_row"])
        fit_rows.append(run["fit_freeze_row"])
        checkpoint_descriptors.append(run["checkpoint"])
        counters["linear_training_runs"] += 1
        counters["optimizer_steps"] += 240
        counters["checkpoint_writes"] += 1
        counters["target_blind_model_inference_runs"] += 1
        del run["model"]

    timing_fit = timing_only_signals(fit["signals"], fit["input_lengths"])
    timing_check = timing_only_signals(check["signals"], check["input_lengths"])
    timing_run = _run_fit_and_prediction(
        condition_id="timing_only_fit",
        architecture="candidate",
        execution_seed=PRIMARY_SEED,
        prefix_size=44,
        fit_signals=timing_fit,
        fit_input_lengths=fit["input_lengths"],
        target_token_ids=fit["target_token_ids"],
        target_lengths=fit["target_lengths"],
        target_texts=fit["target_texts"].tolist(),
        fit_item_ids=fit["item_ids"].tolist(),
        check_signals=timing_check,
        check_input_lengths=check["input_lengths"],
        check_item_ids=check["item_ids"].tolist(),
        checkpoint_path=checkpoint_dir / "timing_only_fit.npz",
        prediction_path=prediction_dir / "timing_only_fit.json",
        transform={"name": "timing_only", "signal_values_used": False},
    )
    prediction_rows.append(timing_run["prediction_freeze_row"])
    fit_rows.append(timing_run["fit_freeze_row"])
    checkpoint_descriptors.append(timing_run["checkpoint"])
    counters["control_training_runs"] += 1
    counters["optimizer_steps"] += 240
    counters["checkpoint_writes"] += 1
    counters["target_blind_model_inference_runs"] += 1
    del timing_run["model"]

    deranged_ids, deranged_lengths, deranged_texts, target_mapping = derange_fit_targets(
        fit["target_token_ids"],
        fit["target_lengths"],
        fit["target_texts"].tolist(),
        fit["semantic_ids"].tolist(),
    )
    target_run = _run_fit_and_prediction(
        condition_id="fit_target_derangement_fit",
        architecture="candidate",
        execution_seed=PRIMARY_SEED,
        prefix_size=44,
        fit_signals=fit["signals"][full_indices],
        fit_input_lengths=fit["input_lengths"][full_indices],
        target_token_ids=deranged_ids,
        target_lengths=deranged_lengths,
        target_texts=deranged_texts,
        fit_item_ids=fit["item_ids"].tolist(),
        check_signals=check["signals"],
        check_input_lengths=check["input_lengths"],
        check_item_ids=check["item_ids"].tolist(),
        checkpoint_path=checkpoint_dir / "fit_target_derangement_fit.npz",
        prediction_path=prediction_dir / "fit_target_derangement_fit.json",
        transform={"name": "fit_target_hash_cycle", "mapping": target_mapping},
    )
    prediction_rows.append(target_run["prediction_freeze_row"])
    fit_rows.append(target_run["fit_freeze_row"])
    checkpoint_descriptors.append(target_run["checkpoint"])
    counters["control_training_runs"] += 1
    counters["optimizer_steps"] += 240
    counters["checkpoint_writes"] += 1
    counters["target_blind_model_inference_runs"] += 1
    del target_run["model"]

    counters["prediction_sets_frozen"] = len(prediction_rows)
    if set(row["condition_id"] for row in prediction_rows) != set(expected_prediction_ids()):
        raise StageBGateError("target-blind run did not produce the exact 41-set inventory")
    if set(row["condition_id"] for row in fit_rows) != set(expected_fit_ids()):
        raise StageBGateError("target-blind run did not produce the exact 20-fit inventory")
    _validate_parameter_inventory(fit_rows)
    parameter_runtime = sum(float(row["runtime_sec"]) for row in fit_rows)
    checkpoint_bytes = sum(int(row["bytes"]) for row in checkpoint_descriptors)
    prediction_bytes = sum(int(row["private_payload_bytes"]) for row in prediction_rows)
    working_array_bytes = _target_blind_working_array_upper_bound(fit, check)
    generated_before_freeze = _directory_bytes(output)
    stage_runtime = time.perf_counter() - started_at
    cumulative_runtime = (
        float(_read_json(output / STATIC_REPORT_NAME)["resources"]["runtime_sec"])
        + float(derivatives["resources"]["runtime_sec"])
        + stage_runtime
    )
    resources = {
        "input_source_cache_bytes": contract["source_contract"]["cache"]["bytes"],
        "generated_artifact_bytes_before_freeze": generated_before_freeze,
        "checkpoint_bytes": checkpoint_bytes,
        "prediction_payload_bytes": prediction_bytes,
        "working_array_bytes_upper_bound": working_array_bytes,
        "parameter_update_runtime_sec": round(parameter_runtime, 6),
        "target_blind_stage_runtime_sec": round(stage_runtime, 6),
        "cumulative_execution_runtime_sec": round(cumulative_runtime, 6),
        "peak_rss_bytes": peak_rss_bytes(),
        "raw_data_reads": counters["raw_fif_or_mat_reads"],
        "real_cache_hash_passes": counters["source_cache_hash_passes"],
        "model_runs": counters["target_blind_model_inference_runs"],
        "training_runs": (
            counters["candidate_training_runs"]
            + counters["linear_training_runs"]
            + counters["control_training_runs"]
        ),
        "producer_is_causal": True,
        "producer_right_context_frames": 0,
        "producer_required_left_context_frames": 2,
        "upstream_cache_is_causal": False,
        "end_to_end_latency_measured": False,
        "direct_energy_measurement": "unavailable",
    }
    _enforce_resource_caps(
        contract["resource_caps"],
        generated_bytes=generated_before_freeze,
        checkpoint_bytes=checkpoint_bytes,
        prediction_bytes=prediction_bytes,
        working_array_bytes=working_array_bytes,
        parameter_runtime=parameter_runtime,
        end_to_end_runtime=cumulative_runtime,
        peak_rss=peak_rss_bytes(),
    )
    freeze = build_prediction_freeze_record(
        contract_sha256=file_sha256(root / CONTRACT_PATH),
        authorization_decision_sha256=file_sha256(root / AUTHORIZATION_PATH),
        implementation_commit=str(implementation_commit),
        prediction_rows=prediction_rows,
        fit_rows=fit_rows,
        static_audit=derivatives["static_audit"],
        access_counters=counters,
        resources=resources,
        environment=_environment_versions(),
        warnings=[
            "check_targets_unavailable_to_fit_prediction_threshold_and_stop_process",
            "all_55_source_train_rows_were_used_historically",
            "upstream_sentence_cache_is_offline_noncausal",
            "negative_time_shifts_are_offline_diagnostics_only",
            "maximum_evidence_level_is_E2_pipeline_discriminative",
        ],
    )
    _write_bounded_json(freeze_path, freeze, maximum_bytes=4 * 1024 * 1024)
    report = {
        "schema_name": "neurodecodekit.loop48_stage_b_target_blind_run",
        "schema_version": "0.1.0",
        "status": "predictions_frozen_check_targets_unavailable",
        "implementation_commit": str(implementation_commit),
        "fit_condition_ids": sorted(row["condition_id"] for row in fit_rows),
        "prediction_condition_ids": sorted(row["condition_id"] for row in prediction_rows),
        "checkpoint_descriptors": checkpoint_descriptors,
        "freeze_record_path": str(freeze_path),
        "freeze_record_sha256": file_sha256(freeze_path),
        "access_counters": counters,
        "resources": resources,
        "check_target_rows_delivered": 0,
        "check_scoring_runs": 0,
        "plaintext_targets_or_predictions_present": False,
        "warnings": freeze["warnings"],
    }
    _write_bounded_json(report_path, report, maximum_bytes=2 * 1024 * 1024)
    final_generated = _generated_artifact_bytes(output, freeze_path)
    if final_generated > contract["resource_caps"]["total_generated_artifact_bytes"]:
        raise StageBGateError("final target-blind artifacts exceed 32 MiB cap")
    return report


def _run_fit_and_prediction(
    *,
    condition_id: str,
    architecture: str,
    execution_seed: int,
    prefix_size: int,
    fit_signals,
    fit_input_lengths,
    target_token_ids,
    target_lengths,
    target_texts: Sequence[str],
    fit_item_ids: Sequence[str],
    check_signals,
    check_input_lengths,
    check_item_ids: Sequence[str],
    checkpoint_path: Path,
    prediction_path: Path,
    transform: Mapping[str, Any],
) -> dict[str, Any]:
    np = _require_numpy()
    training = _train_exact_registered_fit(
        signals=fit_signals,
        input_lengths=fit_input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        architecture=architecture,
        execution_seed=execution_seed,
    )
    configuration = {
        "model_id": (
            "tiny-causal-sentence-ctc-v0"
            if architecture == "candidate"
            else "linear-causal-sentence-ctc-v0"
        ),
        "architecture": architecture,
        "execution_seed": execution_seed,
        "prefix_size": prefix_size,
        "optimizer": {
            "name": "Adam",
            "learning_rate": 0.02,
            "betas": [0.9, 0.999],
            "epsilon": 1e-8,
            "weight_decay": 0.0,
            "amsgrad": False,
        },
        "optimizer_steps": 240,
        "batch_size_ceiling": 16,
        "torch_deterministic_algorithms": True,
        "fit_item_ids_sha256": sha256_json([str(value) for value in fit_item_ids]),
        "check_targets_available": False,
    }
    checkpoint = _write_stage_b_checkpoint(
        checkpoint_path,
        model=training["model"],
        metadata={
            "condition_id": condition_id,
            "configuration": configuration,
            "configuration_sha256": sha256_json(configuration),
            "checkpoint_selection": "state_after_optimizer_step_240_only",
            "check_targets_available": False,
        },
    )
    combined_signals = np.concatenate(
        [np.asarray(fit_signals, dtype="float32"), np.asarray(check_signals, dtype="float32")],
        axis=0,
    )
    combined_lengths = np.concatenate(
        [
            np.asarray(fit_input_lengths, dtype="int64"),
            np.asarray(check_input_lengths, dtype="int64"),
        ]
    )
    inference = _predict_one_model_run(
        training["model"], signals=combined_signals, input_lengths=combined_lengths
    )
    fit_count = len(fit_item_ids)
    fit_predictions = inference["predictions"][:fit_count]
    check_predictions = inference["predictions"][fit_count:]
    fit_blank_counts = inference["blank_counts"][:fit_count]
    fit_valid_steps = inference["valid_steps_by_row"][:fit_count]
    check_blank_counts = inference["blank_counts"][fit_count:]
    check_valid_steps = inference["valid_steps_by_row"][fit_count:]
    normalized_targets = [normalize_ctc_text(str(value)) for value in target_texts]
    fit_macro_cer = statistics_fmean(
        character_error_rate(target, prediction, normalize=False)
        for target, prediction in zip(normalized_targets, fit_predictions, strict=True)
    )
    prior = _train_only_prior(normalized_targets)
    fit_prior_macro_cer = statistics_fmean(
        character_error_rate(target, prior, normalize=False) for target in normalized_targets
    )
    fit_blank_fraction = sum(fit_blank_counts) / sum(fit_valid_steps)
    check_blank_fraction = sum(check_blank_counts) / sum(check_valid_steps)
    telemetry_sha256 = sha256_json(training["telemetry"])
    fit_freeze_row = {
        "condition_id": condition_id,
        "seed": int(execution_seed),
        "prefix_size": int(prefix_size),
        "configuration_sha256": sha256_json(configuration),
        "checkpoint_sha256": checkpoint["sha256"],
        "telemetry_sha256": telemetry_sha256,
        "optimizer_steps": 240,
        "runtime_sec": training["runtime_sec"],
        "peak_rss_bytes": training["peak_rss_bytes"],
        "warnings": [
            "fit_targets_from_isolated_fit_derivative_only",
            "check_targets_unavailable",
        ],
        "telemetry_finite": training["telemetry_finite"],
        "telemetry_points": training["telemetry"],
        "initial_loss": training["initial_loss"],
        "final_loss": training["final_loss"],
        "loss_history_sha256": training["loss_history_sha256"],
        "fit_macro_cer": fit_macro_cer,
        "fit_prior_macro_cer": fit_prior_macro_cer,
        "fit_cer_gain_over_prior": fit_prior_macro_cer - fit_macro_cer,
        "fit_blank_fraction": fit_blank_fraction,
        "fit_prediction_payload_sha256": sha256_json(
            {"item_ids": list(fit_item_ids), "predictions": fit_predictions}
        ),
        "parameter_count": training["parameter_count"],
        "example_presentations": training["example_presentations"],
        "completed_epochs": training["completed_epochs"],
        "torch_version": training["torch_version"],
    }
    prediction_freeze_row = write_prediction_payload(
        prediction_path,
        condition_id=condition_id,
        item_ids=check_item_ids,
        predictions=check_predictions,
        input_lengths=np.asarray(check_input_lengths).tolist(),
        configuration=configuration,
        checkpoint_sha256_or_reason=checkpoint["sha256"],
        transform=transform,
        runtime_sec=inference["runtime_sec"],
        peak_rss_bytes=inference["peak_rss_bytes"],
        model_run_count=1,
        blank_fraction=check_blank_fraction,
        warnings=["model_causal_upstream_cache_noncausal", "check_targets_unavailable"],
    )
    prediction_payload = {
        "predictions": check_predictions,
        "blank_fraction": check_blank_fraction,
    }
    return {
        "model": training["model"],
        "checkpoint": checkpoint,
        "fit_freeze_row": fit_freeze_row,
        "prediction_freeze_row": prediction_freeze_row,
        "prediction_payload": prediction_payload,
    }


def _train_exact_registered_fit(
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    architecture: str,
    execution_seed: int,
) -> dict[str, Any]:
    np, torch = _require_ml_dependencies()
    if architecture not in {"candidate", "linear"} or execution_seed not in SEEDS:
        raise StageBGateError("fit architecture or seed is outside the registered inventory")
    values = np.ascontiguousarray(signals, dtype="float32")
    lengths = np.ascontiguousarray(input_lengths, dtype="int64")
    target_ids = np.ascontiguousarray(target_token_ids, dtype="int64")
    target_len = np.ascontiguousarray(target_lengths, dtype="int64")
    _validate_training_arrays(values, lengths, target_ids, target_len)
    torch.set_num_threads(1)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.manual_seed(int(execution_seed))
    architecture_config = (
        registered_candidate_config(seed=2601)
        if architecture == "candidate"
        else registered_linear_config(seed=2601)
    )
    model = build_causal_sentence_ctc(architecture_config)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.02,
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=0.0,
        amsgrad=False,
        maximize=False,
    )
    criterion = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=False)
    rng = np.random.default_rng(int(execution_seed))
    telemetry_steps = {1, 8, 16, 32, 64, 120, 180, 240}
    telemetry = []
    losses = []
    order = np.empty(0, dtype="int64")
    cursor = 0
    completed_epochs = 0
    example_presentations = 0
    started_at = time.perf_counter()
    model.train()
    for step in range(1, 241):
        if cursor >= len(order):
            order = rng.permutation(len(values)).astype("int64", copy=False)
            cursor = 0
            completed_epochs += 1
        batch_indices = order[cursor : cursor + 16]
        cursor += len(batch_indices)
        xb = torch.from_numpy(values[batch_indices])
        input_len = torch.from_numpy(lengths[batch_indices])
        targets = torch.from_numpy(target_ids[batch_indices])
        target_length = torch.from_numpy(target_len[batch_indices])
        optimizer.zero_grad(set_to_none=True)
        logits = model(xb)
        loss = criterion(
            logits.log_softmax(dim=2).permute(1, 0, 2),
            targets,
            input_len,
            target_length,
        )
        if not bool(torch.isfinite(loss)):
            raise StageBGateError("registered fit produced non-finite CTC loss")
        loss.backward()
        is_telemetry = step in telemetry_steps
        before = (
            [parameter.detach().clone() for parameter in model.parameters()] if is_telemetry else []
        )
        gradient_sq = sum(
            float(torch.sum(parameter.grad.detach() ** 2).cpu())
            for parameter in model.parameters()
            if parameter.grad is not None
        )
        if not math.isfinite(gradient_sq):
            raise StageBGateError("registered fit produced non-finite gradient telemetry")
        if is_telemetry:
            valid_mask = torch.arange(logits.shape[1])[None, :] < input_len[:, None]
            probabilities = logits.softmax(dim=2)
            valid_probabilities = probabilities[valid_mask]
            valid_logits = logits[valid_mask]
            blank_posterior = float(valid_probabilities[:, 0].mean().detach().cpu())
            entropy = float(
                (-(valid_probabilities * valid_probabilities.clamp_min(1e-12).log()).sum(dim=1))
                .mean()
                .detach()
                .cpu()
            )
            margin = float(
                (valid_logits[:, 1:].max(dim=1).values - valid_logits[:, 0]).mean().detach().cpu()
            )
        optimizer.step()
        loss_value = float(loss.detach().cpu())
        losses.append(loss_value)
        example_presentations += int(len(batch_indices))
        if is_telemetry:
            update_sq = sum(
                float(torch.sum((parameter.detach() - previous) ** 2).cpu())
                for parameter, previous in zip(model.parameters(), before, strict=True)
            )
            row = {
                "step": step,
                "ctc_loss": loss_value,
                "gradient_l2_norm": math.sqrt(gradient_sq),
                "parameter_update_l2_norm": math.sqrt(update_sq),
                "mean_blank_posterior": blank_posterior,
                "posterior_entropy": entropy,
                "best_nonblank_minus_blank_logit_margin": margin,
            }
            if not all(math.isfinite(float(value)) for key, value in row.items() if key != "step"):
                raise StageBGateError("registered fit produced non-finite telemetry")
            telemetry.append(row)
    model.eval()
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    expected_parameters = 2908 if architecture == "candidate" else 2884
    if parameter_count != expected_parameters:
        raise StageBGateError("registered fit parameter count drifted")
    return {
        "model": model,
        "telemetry": telemetry,
        "telemetry_finite": True,
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "loss_history_sha256": sha256_json(losses),
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": peak_rss_bytes(),
        "parameter_count": parameter_count,
        "example_presentations": example_presentations,
        "completed_epochs": completed_epochs,
        "torch_version": str(torch.__version__),
    }


def _predict_one_model_run(model, *, signals, input_lengths) -> dict[str, Any]:
    np, torch = _require_ml_dependencies()
    values = np.ascontiguousarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or values.shape[1] != 102 or lengths.shape != (len(values),):
        raise StageBGateError("model inference arrays have invalid geometry")
    predictions = []
    blank_counts = []
    valid_steps_by_row = []
    started_at = time.perf_counter()
    model.eval()
    with torch.no_grad():
        for start in range(0, len(values), 16):
            stop = min(len(values), start + 16)
            logits = model(torch.from_numpy(values[start:stop]))
            token_rows = logits.argmax(dim=2).cpu().numpy()
            for token_row, length in zip(token_rows, lengths[start:stop], strict=True):
                valid = token_row[: int(length)]
                predictions.append(greedy_decode_ctc_ids(valid))
                blank_counts.append(int((valid == 0).sum()))
                valid_steps_by_row.append(int(length))
    return {
        "predictions": predictions,
        "blank_counts": blank_counts,
        "valid_steps_by_row": valid_steps_by_row,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": peak_rss_bytes(),
        "model_run_count": 1,
    }


def _write_control_inference(
    *,
    condition_id: str,
    model,
    signals,
    check: Mapping[str, Any],
    checkpoint_sha256: str,
    transform: Mapping[str, Any],
    configuration: Mapping[str, Any],
    prediction_dir: Path,
) -> dict[str, Any]:
    inference = _predict_one_model_run(
        model,
        signals=signals,
        input_lengths=check["input_lengths"],
    )
    blank_fraction = sum(inference["blank_counts"]) / sum(inference["valid_steps_by_row"])
    return write_prediction_payload(
        prediction_dir / f"{condition_id}.json",
        condition_id=condition_id,
        item_ids=check["item_ids"].tolist(),
        predictions=inference["predictions"],
        input_lengths=check["input_lengths"].tolist(),
        configuration=dict(configuration),
        checkpoint_sha256_or_reason=checkpoint_sha256,
        transform=transform,
        runtime_sec=inference["runtime_sec"],
        peak_rss_bytes=inference["peak_rss_bytes"],
        model_run_count=1,
        blank_fraction=blank_fraction,
        warnings=["target_blind_control_inference", "check_targets_unavailable"],
    )


def _write_stage_b_checkpoint(
    path: Path,
    *,
    model,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    np = _require_numpy()
    _refuse_existing(path)
    arrays = {
        name: value.detach().cpu().numpy().astype("float32", copy=True)
        for name, value in model.state_dict().items()
    }
    payload_sha256 = _array_map_sha256(arrays)
    checkpoint_metadata = {
        "schema": {"name": "neurodecodekit.loop48_stage_b_checkpoint", "version": 0},
        "serialization": "numpy_npz_allow_pickle_false",
        "parameter_payload_sha256": payload_sha256,
        "parameter_count": sum(int(value.size) for value in arrays.values()),
        **dict(metadata),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays, metadata=json.dumps(checkpoint_metadata, sort_keys=True))
    return {
        "condition_id": str(metadata["condition_id"]),
        "path": str(path),
        "bytes": int(path.stat().st_size),
        "sha256": file_sha256(path),
        "parameter_payload_sha256": payload_sha256,
        "parameter_count": checkpoint_metadata["parameter_count"],
    }


def _validate_training_arrays(values, lengths, target_ids, target_lengths) -> None:
    np = _require_numpy()
    if values.ndim != 3 or values.shape[0] < 1 or values.shape[1] != 102:
        raise StageBGateError("training signals must be nonempty [items, 102, time]")
    if not np.isfinite(values).all():
        raise StageBGateError("training signals contain non-finite values")
    if lengths.shape != (len(values),) or target_lengths.shape != (len(values),):
        raise StageBGateError("training lengths do not match signal rows")
    if target_ids.ndim != 2 or target_ids.shape[0] != len(values):
        raise StageBGateError("training target IDs have invalid geometry")
    if (lengths < 1).any() or (lengths > values.shape[2]).any():
        raise StageBGateError("training input lengths are invalid")
    if (target_lengths < 1).any() or (target_lengths > target_ids.shape[1]).any():
        raise StageBGateError("training target lengths are invalid")
    for row, length in zip(target_ids, target_lengths, strict=True):
        if (row[: int(length)] <= 0).any() or (row[: int(length)] >= 28).any():
            raise StageBGateError("valid target IDs must exclude blank and stay in vocabulary")
        if (row[int(length) :] != 0).any():
            raise StageBGateError("target padding must use blank zero")


def _validate_parameter_inventory(fit_rows: Sequence[Mapping[str, Any]]) -> None:
    for row in fit_rows:
        condition_id = str(row["condition_id"])
        expected = 2884 if condition_id.startswith("linear_") else 2908
        if int(row["parameter_count"]) != expected:
            raise StageBGateError(f"parameter count drifted for {condition_id}")


def _train_only_prior(targets: Sequence[str]) -> str:
    values = [str(value) for value in targets]
    counts = Counter(values)
    first_seen = {value: values.index(value) for value in counts}
    return min(counts, key=lambda value: (-counts[value], first_seen[value], value))


def statistics_fmean(values) -> float:
    measured = [float(value) for value in values]
    return sum(measured) / len(measured)


def score_frozen_stage_b(
    *,
    repo_root: str | Path,
    freeze_record_path: str | Path,
    green_freeze_commit: str,
    freeze_push_ci_run_id: int,
    freeze_pr_ci_run_id: int,
    public_report_out: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Deliver the 11 check targets once and score every frozen set together."""

    np = _require_numpy()
    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    consumed = output / CONSUMED_MARKER_NAME
    _refuse_existing(consumed)
    if _git_head(root) != str(green_freeze_commit):
        raise StageBGateError("scoring requires the remotely green freeze commit at HEAD")
    if freeze_push_ci_run_id <= 0 or freeze_pr_ci_run_id <= 0:
        raise StageBGateError("both remotely green freeze CI run IDs are required")
    if not _tracked_worktree_clean(root):
        raise StageBGateError("scoring requires a clean tracked worktree")
    freeze_path = Path(freeze_record_path)
    if not freeze_path.is_absolute():
        freeze_path = root / freeze_path
    freeze_path = freeze_path.resolve()
    freeze = _read_json(freeze_path)
    if not _path_tracked_at_head(root, freeze_path):
        raise StageBGateError("prediction freeze is not tracked at the green HEAD")
    validate_prediction_freeze_record(freeze)
    target_blind = _read_json(output / TARGET_BLIND_REPORT_NAME)
    if target_blind["freeze_record_sha256"] != file_sha256(freeze_path):
        raise StageBGateError("committed freeze differs from the target-blind run")
    public_path = Path(public_report_out)
    if not public_path.is_absolute():
        public_path = root / public_path
    public_path = public_path.resolve()
    registered_result = (
        root / "registries/loop48_train_only_discrimination_result.v0.json"
    ).resolve()
    if enforce_registered_paths and public_path != registered_result:
        raise StageBGateError(f"registered Stage B result must be {registered_result}")
    _refuse_existing(public_path)
    marker = {
        "status": "target_delivery_started_rerun_forbidden_even_if_interrupted",
        "green_freeze_commit": str(green_freeze_commit),
        "freeze_record_sha256": file_sha256(freeze_path),
        "freeze_push_ci_run_id": int(freeze_push_ci_run_id),
        "freeze_pr_ci_run_id": int(freeze_pr_ci_run_id),
    }
    _write_bounded_json(consumed, marker, maximum_bytes=16 * 1024)
    started_at = time.perf_counter()
    contract = _read_json(root / CONTRACT_PATH)
    source = contract["source_contract"]
    cache_path = root / source["cache"]["path"]
    check = _load_derivative(
        output / CHECK_INPUTS_NAME,
        expected_schema="neurodecodekit.loop48_stage_b_check_inputs",
    )
    check_indices = [
        int(value)
        for value in _read_json(output / STATIC_REPORT_NAME)["diagnostic_split"][
            "check_source_row_indices"
        ]
    ]
    loop26_source = _read_json(root / LOOP26_CONTRACT_PATH)["source_contract"]
    target_ids = stream_npz_rows(
        cache_path,
        "target_token_ids",
        check_indices,
        expected_shape=loop26_source["ctc_arrays"]["target_token_ids_shape"],
        expected_dtype="int16",
    )
    target_lengths = stream_npz_rows(
        cache_path,
        "target_lengths",
        check_indices,
        expected_shape=loop26_source["ctc_arrays"]["target_lengths_shape"],
        expected_dtype="int32",
    )
    targets = [
        decode_ctc_target(row[: int(length)])
        for row, length in zip(target_ids.values, target_lengths.values, strict=True)
    ]
    target_path = output / CHECK_TARGETS_NAME
    _refuse_existing(target_path)
    target_arrays = {
        "target_token_ids": np.ascontiguousarray(target_ids.values, dtype="int16"),
        "target_lengths": np.ascontiguousarray(target_lengths.values, dtype="int32"),
        "target_texts": np.asarray(targets),
        "item_ids": check["item_ids"],
        "source_row_indices": check["source_row_indices"],
    }
    _write_npz(
        target_path,
        target_arrays,
        {
            "schema": {"name": "neurodecodekit.loop48_stage_b_check_targets", "version": 0},
            "rows": 11,
            "delivery_event": 1,
            "created_after_green_prediction_freeze_commit": str(green_freeze_commit),
            "prediction_freeze_sha256": file_sha256(freeze_path),
        },
    )
    payloads = {}
    rows_by_id = {row["condition_id"]: row for row in freeze["prediction_sets"]}
    for condition_id in expected_prediction_ids():
        path = output / "predictions" / f"{condition_id}.json"
        try:
            payloads[condition_id] = load_prediction_payload(path, rows_by_id[condition_id])
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise StageBGateError(
                f"prediction payload changed after freeze: {condition_id}"
            ) from exc
    score = score_failure_discrimination(
        prediction_payloads=payloads,
        target_item_ids=check["item_ids"].tolist(),
        targets=targets,
        freeze_record=freeze,
    )
    counters = {key: int(value) for key, value in freeze["access_counters"].items()}
    counters["archive_header_reads"] += 2
    counters["archive_row_member_streams"] += 2
    counters["opaque_excluded_rows_traversed"] += (
        target_ids.opaque_excluded_rows_traversed + target_lengths.opaque_excluded_rows_traversed
    )
    counters["check_target_rows_delivered_after_green_freeze"] += 11
    counters["check_scoring_runs"] += 1
    _validate_scored_counters(counters)
    check_ctc_audit = _check_ctc_feasibility(
        item_ids=check["item_ids"].tolist(),
        input_lengths=check["input_lengths"],
        target_token_ids=target_ids.values,
        target_lengths=target_lengths.values,
    )
    if (
        score["check_ctc_feasibility"]["infeasible_row_count"]
        != check_ctc_audit["infeasible_row_count"]
    ):
        raise StageBGateError("text-derived and token-derived check CTC audits disagree")
    score_runtime = time.perf_counter() - started_at
    generated_before_public = _generated_artifact_bytes(output, freeze_path)
    score.update(
        {
            "contract_sha256": file_sha256(root / CONTRACT_PATH),
            "authorization_decision_sha256": file_sha256(root / AUTHORIZATION_PATH),
            "prediction_freeze_sha256": file_sha256(freeze_path),
            "green_prediction_freeze": {
                "commit": str(green_freeze_commit),
                "push_ci_run_id": int(freeze_push_ci_run_id),
                "pr_ci_run_id": int(freeze_pr_ci_run_id),
                "operator_confirmed_both_runs_green_before_target_delivery": True,
            },
            "access_counters": counters,
            "check_target_delivery_events": 1,
            "check_ctc_feasibility_after_green_delivery": check_ctc_audit,
            "validation_rows_delivered_or_scored": 0,
            "source_test_rows_delivered_or_scored": 0,
            "session2_rows_delivered_or_scored": 0,
            "post_check_parameter_updates": 0,
            "post_check_configuration_changes": 0,
            "reruns": 0,
            "resources": {
                **freeze["resources"],
                "scoring_runtime_sec": round(score_runtime, 6),
                "generated_artifact_bytes_before_public_result": generated_before_public,
                "public_report_bytes": 0,
                "total_generated_artifact_bytes": 0,
                "peak_rss_bytes": peak_rss_bytes(),
            },
            "check_target_artifact": {
                "path": target_path.relative_to(root).as_posix(),
                "bytes": int(target_path.stat().st_size),
                "sha256": file_sha256(target_path),
                "target_payload_sha256": sha256_json(
                    {
                        "item_ids": check["item_ids"].tolist(),
                        "target_texts": targets,
                    }
                ),
                "committed": False,
            },
            "claim_boundary": {
                "maximum_evidence_level": "E2_pipeline_discriminative",
                "maximum_wording": contract["claim_ceiling"]["maximum_wording"],
                "not_established": (
                    "Independent validation, neural advantage, brain-specific origin, useful "
                    "decoding, unseen-person generalization, causal preprocessing, real-time "
                    "behavior, EEG or home-device performance, assistive value, diagnostic "
                    "value, and clinical utility remain unestablished."
                ),
            },
        }
    )
    _write_measured_result_json(
        public_path,
        score,
        base_generated_bytes=generated_before_public,
        maximum_bytes=4 * 1024 * 1024,
    )
    final_generated = _generated_artifact_bytes(output, freeze_path, public_path)
    caps = contract["resource_caps"]
    if final_generated > caps["total_generated_artifact_bytes"]:
        raise StageBGateError("final scored artifacts exceed 32 MiB cap")
    if peak_rss_bytes() > caps["peak_rss_bytes"]:
        raise StageBGateError("final scoring peak RSS exceeds 1 GiB cap")
    marker.update(
        {
            "status": "consumed_scored_no_rerun_authorized",
            "public_report_sha256": file_sha256(public_path),
            "result": score["status"],
        }
    )
    _write_replace_json(consumed, marker, maximum_bytes=16 * 1024)
    return _read_json(public_path)


def _check_ctc_feasibility(
    *,
    item_ids: Sequence[str],
    input_lengths,
    target_token_ids,
    target_lengths,
) -> dict[str, Any]:
    rows = []
    for item_id, input_length, token_row, target_length in zip(
        item_ids,
        input_lengths,
        target_token_ids,
        target_lengths,
        strict=True,
    ):
        valid = token_row[: int(target_length)]
        repeats = int((valid[1:] == valid[:-1]).sum()) if len(valid) > 1 else 0
        minimum = int(target_length) + repeats
        rows.append(
            {
                "item_id_sha256": hashlib.sha256(str(item_id).encode("utf-8")).hexdigest(),
                "input_length": int(input_length),
                "target_length": int(target_length),
                "adjacent_repeat_count": repeats,
                "minimum_alignment_steps": minimum,
                "frame_to_target_ratio": int(input_length) / int(target_length),
                "alignment_feasible": int(input_length) >= minimum,
            }
        )
    return {
        "rows": rows,
        "infeasible_row_count": sum(not row["alignment_feasible"] for row in rows),
    }


def _validate_split_report(split: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, bool]:
    membership = split.get("membership") or {}
    rows = membership.get("rows") or []
    counts = {key: sum(row.get("split") == key for row in rows) for key in ("train", "val", "test")}
    indices = [int(row["source_row_index"]) for row in rows]
    expected = source["split_report"]
    return {
        "split_schema": (split.get("schema") or {}).get("name") == "b2q-split-protocol",
        "split_strict_training_ready": membership.get("strict_training_ready") is True,
        "split_partition_rows": counts == expected["partition_rows"],
        "split_contiguous_unique_source_rows": sorted(indices) == list(range(len(rows))),
        "protocol_config_sha256": membership.get("protocol_config_sha256")
        == expected["protocol_config_sha256"],
        "group_assignment_sha256": membership.get("group_assignment_sha256")
        == expected["group_assignment_sha256"],
        "semantic_membership_sha256": membership.get("semantic_membership_sha256")
        == expected["semantic_membership_sha256"],
        "physical_membership_sha256": membership.get("membership_sha256")
        == expected["physical_membership_sha256"],
    }


def _validate_fit_targets(target_ids, target_lengths, target_texts) -> None:
    for row, length, text in zip(target_ids, target_lengths, target_texts, strict=True):
        if decode_ctc_target(row[: int(length)]) != str(text):
            raise StageBGateError("fit target text does not match encoded IDs")


def _write_npz(path: Path, arrays: Mapping[str, Any], metadata: Mapping[str, Any]) -> None:
    np = _require_numpy()
    _refuse_existing(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays, metadata=json.dumps(dict(metadata), sort_keys=True))


def _load_derivative(path: Path, *, expected_schema: str) -> dict[str, Any]:
    np = _require_numpy()
    with np.load(path, allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise StageBGateError(f"derivative lacks metadata: {path}")
        arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
        metadata_value = data["metadata"].item()
    metadata = json.loads(metadata_value)
    if (metadata.get("schema") or {}).get("name") != expected_schema:
        raise StageBGateError(f"unexpected derivative schema at {path}")
    arrays["metadata"] = metadata
    return arrays


def _validate_target_blind_derivatives(fit: Mapping[str, Any], check: Mapping[str, Any]) -> None:
    if fit["signals"].shape[:2] != (44, 102):
        raise StageBGateError("fit derivative geometry is invalid")
    if check["signals"].shape[:2] != (11, 102):
        raise StageBGateError("check derivative geometry is invalid")
    forbidden = {"target_token_ids", "target_lengths", "target_texts"}
    if forbidden & set(check):
        raise StageBGateError("check inputs contain forbidden target arrays")
    if fit["metadata"].get("source_cache_sha256") != check["metadata"].get("source_cache_sha256"):
        raise StageBGateError("fit and check derivatives bind different sources")
    if fit["metadata"].get("diagnostic_assignment_sha256") != check["metadata"].get(
        "diagnostic_assignment_sha256"
    ):
        raise StageBGateError("fit and check derivatives bind different diagnostic splits")
    if fit["channel_names"].tolist() != check["channel_names"].tolist():
        raise StageBGateError("fit and check channel identities differ")
    if len(set(fit["item_ids"].tolist())) != 44 or len(set(check["item_ids"].tolist())) != 11:
        raise StageBGateError("derivative item IDs are not unique")
    if set(fit["item_ids"].tolist()) & set(check["item_ids"].tolist()):
        raise StageBGateError("fit and check identities overlap")


def _validate_scored_counters(counters: Mapping[str, int]) -> None:
    expected = {
        "source_cache_stat_reads": 1,
        "source_cache_hash_passes": 1,
        "split_report_metadata_reads": 1,
        "archive_header_reads": 16,
        "archive_row_member_streams": 9,
        "fit_signal_rows_delivered": 44,
        "fit_target_rows_delivered": 44,
        "check_signal_rows_delivered": 11,
        "candidate_training_runs": 15,
        "linear_training_runs": 3,
        "control_training_runs": 2,
        "optimizer_steps": 4800,
        "checkpoint_writes": 20,
        "checkpoint_reads": 0,
        "target_blind_model_inference_runs": 35,
        "no_signal_prior_fits": 5,
        "prediction_sets_frozen": 41,
        "check_target_rows_delivered_before_green_freeze": 0,
        "check_target_rows_delivered_after_green_freeze": 11,
        "check_scoring_runs": 1,
        "post_check_parameter_updates": 0,
        "post_check_configuration_changes": 0,
        "validation_signal_rows_delivered": 0,
        "validation_target_rows_delivered": 0,
        "source_test_signal_rows_delivered": 0,
        "source_test_target_rows_delivered": 0,
        "session2_rows_delivered": 0,
        "raw_fif_or_mat_reads": 0,
        "network_calls": 0,
        "new_download_bytes": 0,
        "language_model_or_neurotoken_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
        "reruns": 0,
    }
    mismatches = {
        name: {"expected": value, "actual": counters.get(name)}
        for name, value in expected.items()
        if counters.get(name) != value
    }
    if mismatches:
        raise StageBGateError(f"scored access counters mismatch: {mismatches}")


def _artifact_descriptor(
    path: Path,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "path": str(path),
        "bytes": int(path.stat().st_size),
        "sha256": file_sha256(path),
        "arrays": {
            name: {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "sha256": _array_sha256(value),
            }
            for name, value in arrays.items()
        },
        "row_ids_sha256": sha256_json(arrays["item_ids"].tolist()),
        "diagnostic_assignment_sha256": metadata["diagnostic_assignment_sha256"],
        "contains_targets": bool(metadata["contains_targets"]),
    }


def _derivative_working_array_upper_bound(
    streamed_signals,
    streamed_lengths,
    fit_arrays: Mapping[str, Any],
    check_arrays: Mapping[str, Any],
) -> int:
    resident = int(streamed_signals.nbytes) + int(streamed_lengths.nbytes)
    resident += sum(
        int(value.nbytes)
        for bundle in (fit_arrays, check_arrays)
        for value in bundle.values()
        if hasattr(value, "nbytes")
    )
    quality_copy = int(fit_arrays["signals"].nbytes)
    float64_quality_copy = 4 * quality_copy
    return resident + quality_copy + float64_quality_copy


def _target_blind_working_array_upper_bound(
    fit: Mapping[str, Any], check: Mapping[str, Any]
) -> int:
    resident = sum(
        int(value.nbytes)
        for bundle in (fit, check)
        for name, value in bundle.items()
        if name != "metadata" and hasattr(value, "nbytes")
    )
    largest_combined_inference = int(fit["signals"].nbytes + check["signals"].nbytes)
    largest_transform = max(int(fit["signals"].nbytes), int(check["signals"].nbytes))
    return resident + largest_combined_inference + 2 * largest_transform


def _enforce_resource_caps(
    caps: Mapping[str, Any],
    *,
    generated_bytes: int,
    checkpoint_bytes: int,
    prediction_bytes: int,
    working_array_bytes: int,
    parameter_runtime: float,
    end_to_end_runtime: float,
    peak_rss: int,
) -> None:
    checks = {
        "generated artifacts": (generated_bytes, caps["total_generated_artifact_bytes"]),
        "checkpoints": (checkpoint_bytes, caps["maximum_checkpoint_bytes"]),
        "prediction payloads": (prediction_bytes, caps["maximum_prediction_payload_bytes"]),
        "working arrays": (working_array_bytes, caps["maximum_working_array_bytes"]),
        "parameter runtime": (parameter_runtime, caps["parameter_update_runtime_sec"]),
        "end-to-end runtime": (end_to_end_runtime, caps["end_to_end_runtime_sec"]),
        "peak RSS": (peak_rss, caps["peak_rss_bytes"]),
    }
    failed = [name for name, (value, cap) in checks.items() if value > cap]
    if failed:
        raise StageBGateError(f"Loop 48 Stage B resource caps exceeded: {failed}")


def _resolve_output_root(root: Path, output_root: str | Path, enforce: bool) -> Path:
    output = Path(output_root)
    if not output.is_absolute():
        output = root / output
    output = output.resolve()
    registered = (root / REGISTERED_OUTPUT_ROOT).resolve()
    if enforce and output != registered:
        raise StageBGateError(f"registered execution output must be {registered}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def _single_thread_environment_ok() -> bool:
    names = (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
    return all(os.environ.get(name) == "1" for name in names)


def _environment_versions() -> dict[str, Any]:
    versions: dict[str, Any] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_threads": 1,
        "workers": 1,
        "concurrent_numerical_jobs": 1,
    }
    for name in ("numpy", "scipy", "torch"):
        try:
            module = __import__(name)
            versions[name] = str(module.__version__)
        except ImportError:
            versions[name] = "unavailable"
    return versions


def _tracked_worktree_clean(root: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return not result.stdout.strip()


def _git_head(root: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()


def _path_tracked_at_head(root: Path, path: Path) -> bool:
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{relative.as_posix()}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _path_git_ignored(root: Path, path: Path) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(path)],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise StageBGateError(f"JSON object required: {path}")
    return value


def _write_bounded_json(path: Path, value: Mapping[str, Any], *, maximum_bytes: int) -> None:
    payload = (json.dumps(dict(value), indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    if len(payload) > maximum_bytes:
        raise StageBGateError(f"JSON artifact exceeds {maximum_bytes} bytes: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def _write_measured_result_json(
    path: Path,
    value: Mapping[str, Any],
    *,
    base_generated_bytes: int,
    maximum_bytes: int,
) -> None:
    measured = dict(value)
    measured["resources"] = dict(value["resources"])
    for _ in range(10):
        payload = (json.dumps(measured, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
            "utf-8"
        )
        size = len(payload)
        total = base_generated_bytes + size
        if (
            measured["resources"].get("public_report_bytes") == size
            and measured["resources"].get("total_generated_artifact_bytes") == total
        ):
            break
        measured["resources"]["public_report_bytes"] = size
        measured["resources"]["total_generated_artifact_bytes"] = total
    payload = (json.dumps(measured, indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    if len(payload) > maximum_bytes:
        raise StageBGateError(f"JSON artifact exceeds {maximum_bytes} bytes: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def _write_replace_json(path: Path, value: Mapping[str, Any], *, maximum_bytes: int) -> None:
    payload = (json.dumps(dict(value), indent=2, sort_keys=True, allow_nan=False) + "\n").encode(
        "utf-8"
    )
    if len(payload) > maximum_bytes:
        raise StageBGateError(f"JSON artifact exceeds {maximum_bytes} bytes: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _refuse_existing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to replace existing Loop 48 Stage B artifact: {path}")


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _generated_artifact_bytes(output: Path, *extra_paths: Path) -> int:
    files = {item.resolve() for item in output.rglob("*") if item.is_file()}
    files.update(path.resolve() for path in extra_paths if path.is_file())
    return sum(path.stat().st_size for path in files)


def _array_sha256(value) -> str:
    np = _require_numpy()
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _array_map_sha256(arrays: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in sorted(arrays):
        value = arrays[name]
        digest.update(name.encode("utf-8"))
        digest.update(_array_sha256(value).encode("ascii"))
    return digest.hexdigest()


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Loop 48 Stage B requires NumPy: `pip install numpy`.") from exc
    return np


def _require_ml_dependencies():
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Loop 48 Stage B training requires NumPy and Torch: `pip install -e '.[ml]'`."
        ) from exc
    return np, torch
