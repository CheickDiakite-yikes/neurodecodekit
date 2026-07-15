"""Staged execution gate for the shared Loop 26/31/33 S21 validation event."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import subprocess
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from neurodecodekit.cache.row_streaming_npz import (
    inspect_npz_members,
    read_npz_json_scalar,
    sha256_file_once,
    stream_npz_rows,
)
from neurodecodekit.evaluation.shared_s21_validation import (
    ADDITIONAL_CONTROL_IDS,
    PREFIX_SIZES,
    SEEDS,
    apply_channel_derangement,
    apply_time_displacement,
    build_prediction_freeze_record,
    candidate_prediction_id,
    derange_train_targets,
    derange_validation_predictions,
    expected_prediction_ids,
    load_prediction_payload,
    prior_prediction_id,
    registered_prefix_order,
    score_shared_validation,
    timing_only_signals,
    validate_prediction_freeze_record,
    write_prediction_payload,
    zero_valid_signals,
)
from neurodecodekit.models.tiny_causal_sentence_ctc import (
    predict_causal_sentence_ctc,
    registered_candidate_config,
    registered_linear_config,
    save_causal_sentence_ctc_checkpoint,
    train_causal_sentence_ctc,
)
from neurodecodekit.preprocess.ctc_text import decode_ctc_target, normalize_ctc_text


CONTRACT_PATH = "registries/loop26_shared_validation_contract.v0.json"
AUTHORIZATION_PATH = "registries/loop26_authorization_decision.v0.json"
REGISTERED_OUTPUT_ROOT = ".codex_work/loop26"
STATIC_REPORT_NAME = "static_gate.json"
DERIVATIVE_REPORT_NAME = "derivatives.json"
TARGET_BLIND_REPORT_NAME = "target_blind_run.json"
CONSUMED_MARKER_NAME = "validation_scoring_consumed.json"

EXACT_TARGET_BLIND_COUNTERS = {
    "source_cache_stat_reads": 1,
    "source_cache_hash_passes": 1,
    "split_report_metadata_reads": 1,
    "archive_header_reads": 20,
    "archive_row_member_streams": 8,
    "train_signal_rows_delivered": 55,
    "train_target_rows_delivered": 55,
    "validation_signal_rows_delivered": 6,
    "candidate_training_runs": 18,
    "control_training_runs": 3,
    "optimizer_steps": 5040,
    "checkpoint_writes": 21,
    "checkpoint_reads": 0,
    "target_blind_model_inference_runs": 24,
    "no_signal_prior_fits": 6,
    "prediction_sets_frozen": 31,
    "validation_target_rows_delivered_before_prediction_freeze": 0,
    "validation_target_rows_delivered_after_prediction_freeze": 0,
    "validation_scoring_runs": 0,
    "source_test_rows_delivered": 0,
    "session2_rows_delivered": 0,
    "raw_fif_or_mat_reads": 0,
    "post_target_parameter_updates": 0,
    "post_target_configuration_changes": 0,
    "external_network_calls": 0,
    "new_downloads": 0,
    "language_model_or_neurotoken_runs": 0,
    "rw3_stream_device_or_hardware_operations": 0,
}


class SharedS21GateError(RuntimeError):
    """Raised when a registered access, identity, or resource gate fails."""


def new_runtime_access_counters() -> dict[str, int]:
    return {
        "source_cache_stat_reads": 0,
        "source_cache_hash_passes": 0,
        "split_report_metadata_reads": 0,
        "archive_header_reads": 0,
        "archive_row_member_streams": 0,
        "opaque_excluded_row_traversals": 0,
        "train_signal_rows_delivered": 0,
        "train_target_rows_delivered": 0,
        "validation_signal_rows_delivered": 0,
        "validation_target_rows_delivered_before_prediction_freeze": 0,
        "validation_target_rows_delivered_after_prediction_freeze": 0,
        "source_test_rows_delivered": 0,
        "session2_rows_delivered": 0,
        "raw_fif_or_mat_reads": 0,
        "candidate_training_runs": 0,
        "control_training_runs": 0,
        "optimizer_steps": 0,
        "checkpoint_writes": 0,
        "checkpoint_reads": 0,
        "target_blind_model_inference_runs": 0,
        "no_signal_prior_fits": 0,
        "prediction_sets_frozen": 0,
        "validation_scoring_runs": 0,
        "source_test_scoring_runs": 0,
        "session2_scoring_runs": 0,
        "post_target_parameter_updates": 0,
        "post_target_configuration_changes": 0,
        "external_network_calls": 0,
        "new_downloads": 0,
        "language_model_or_neurotoken_runs": 0,
        "rw3_stream_device_or_hardware_operations": 0,
    }


def run_static_shared_s21_gate(
    *,
    repo_root: str | Path,
    implementation_commit: str,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Validate frozen identities and metadata before any signal/target values."""

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
        authorization.get("status") == "authorized_no_implementation_yet"
    )
    checks["authorization_contract_hash"] = authorization["authorized_contract"][
        "contract_sha256"
    ] == _file_sha256(contract_path)
    checks["authorization_request_hash"] = authorization["authorization_request"][
        "request_sha256"
    ] == _file_sha256(root / authorization["authorization_request"]["request_path"])
    checks["implementation_commit_format"] = len(str(implementation_commit)) == 40
    checks["implementation_commit_is_head"] = _git_head(root) == str(implementation_commit)
    checks["tracked_worktree_clean"] = _tracked_worktree_clean(root)
    checks["single_thread_environment"] = _single_thread_environment_ok()
    checks["environment_versions"] = _environment_versions() == {
        "python": "3.13.5",
        "numpy": "2.5.0",
        "torch": "2.13.0",
        "scipy": "1.18.0",
    }
    for binding in [
        *contract["dependency_bindings"].values(),
        *contract["local_evidence_bindings"].values(),
    ]:
        path = root / binding["path"]
        checks[f"binding:{binding['path']}"] = (
            path.is_file() and _file_sha256(path) == binding["sha256"]
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
        split_path.is_file() and _file_sha256(split_path) == split_contract["sha256"]
    )
    split = _read_json(split_path)
    counters["split_report_metadata_reads"] += 1
    checks.update(_validate_split_report(split, source))
    extraction_contract = source["extraction_summary"]
    extraction_path = root / extraction_contract["path"]
    checks["extraction_summary_hash"] = (
        extraction_path.is_file() and _file_sha256(extraction_path) == extraction_contract["sha256"]
    )

    expected_headers = {
        "signals.npy": (tuple(cache_contract["shape"]), cache_contract["dtype"]),
        "input_lengths.npy": ((cache_contract["shape"][0],), "int32"),
        "target_token_ids.npy": (tuple(source["ctc_arrays"]["target_token_ids_shape"]), "int16"),
        "target_lengths.npy": (tuple(source["ctc_arrays"]["target_lengths_shape"]), "int32"),
        "target_texts.npy": (tuple(source["ctc_arrays"]["target_texts_shape"]), None),
        "channel_names.npy": ((source["channels"]["count"],), None),
    }
    headers = inspect_npz_members(cache_path)
    counters["archive_header_reads"] += len(headers)
    audit = contract["legacy_archive_access_audit"]
    with zipfile.ZipFile(cache_path) as bundle:
        infos = bundle.infolist()
    checks["archive_entry_count"] = len(infos) == audit["archive_entries"]
    checks["archive_compressed_bytes"] = (
        sum(info.compress_size for info in infos) == audit["compressed_member_bytes"]
    )
    checks["archive_uncompressed_bytes"] = (
        sum(info.file_size for info in infos) == audit["uncompressed_bytes"]
    )
    checks["signals_compressed_bytes"] = (
        headers["signals.npy"].compressed_bytes == audit["signals_member_compressed_bytes"]
    )
    checks["signals_uncompressed_bytes"] = (
        headers["signals.npy"].uncompressed_bytes == audit["signals_member_uncompressed_bytes"]
    )
    for name, (shape, dtype) in expected_headers.items():
        header = headers.get(name)
        checks[f"header:{name}:present"] = header is not None
        checks[f"header:{name}:shape"] = header is not None and header.shape == shape
        if dtype is not None:
            checks[f"header:{name}:dtype"] = header is not None and header.dtype == dtype

    channels = stream_npz_rows(
        cache_path,
        "channel_names",
        range(source["channels"]["count"]),
        expected_shape=(source["channels"]["count"],),
    )
    counters["archive_row_member_streams"] += 1
    counters["archive_header_reads"] += 1
    counters["opaque_excluded_row_traversals"] += channels.opaque_excluded_rows_traversed
    channel_names = [str(value) for value in channels.values.tolist()]
    checks["ordered_channel_names_sha256"] = (
        _sha256_json(channel_names) == source["channels"]["ordered_names_sha256"]
    )
    metadata = read_npz_json_scalar(cache_path)
    counters["archive_row_member_streams"] += 1
    counters["archive_header_reads"] += 1
    checks["metadata_schema"] = (metadata.get("schema") or {}) == {
        "name": cache_contract["schema_name"],
        "version": cache_contract["schema_version"],
    }
    metadata_text = json.dumps(metadata, sort_keys=True)
    for name, expected in (
        ("scaler_center", source["frozen_scaler"]["center_sha256"]),
        ("scaler_scale", source["frozen_scaler"]["scale_sha256"]),
        ("split_protocol", source["split_report"]["protocol_config_sha256"]),
        ("semantic_membership", source["split_report"]["semantic_membership_sha256"]),
    ):
        checks[f"metadata:{name}"] = expected in metadata_text

    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema_name": "neurodecodekit.loop26_static_gate",
        "schema_version": "0.1.0",
        "status": "passed" if not failed else "failed",
        "proof_posture": "target_free_static_identity_gate_no_signal_or_target_values",
        "implementation_commit": str(implementation_commit),
        "contract_sha256": _file_sha256(contract_path),
        "authorization_decision_sha256": _file_sha256(authorization_path),
        "checks": checks,
        "failed_checks": failed,
        "source_cache": {
            "path": cache_contract["path"],
            "bytes": cache_contract["bytes"],
            "expected_sha256": cache_contract["sha256"],
            "hash_passes": 0,
        },
        "split_partitions": _partition_indices(split),
        "channel_names": channel_names,
        "access_counters": counters,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "warnings": [
            "static_gate_reads_target_free_metadata_and_npy_headers_only",
            "channel_names_and_metadata_are_archive_values_but_not_signal_or_target_values",
            "source_cache_hash_is_deferred_to_the_single_registered_hash_pass",
            "upstream_cache_is_offline_noncausal",
        ],
    }
    _write_bounded_json(report_path, report, maximum_bytes=1024 * 1024)
    if failed:
        raise SharedS21GateError(f"Loop 26 static gate failed: {failed}")
    return report


def create_shared_s21_derivatives(
    *,
    repo_root: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Hash once and create only train plus target-free validation derivatives."""

    np = _require_numpy()
    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    static = _read_json(output / STATIC_REPORT_NAME)
    if static.get("status") != "passed":
        raise SharedS21GateError("static gate must pass before derivative creation")
    report_path = output / DERIVATIVE_REPORT_NAME
    train_path = output / "train_bundle.npz"
    validation_path = output / "validation_inputs.npz"
    for path in (report_path, train_path, validation_path):
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
    partitions = static["split_partitions"]
    train_indices = [int(value) for value in partitions["train"]]
    validation_indices = [int(value) for value in partitions["val"]]
    test_indices = [int(value) for value in partitions["test"]]
    if (len(train_indices), len(validation_indices), len(test_indices)) != (55, 6, 5):
        raise SharedS21GateError("split report does not preserve the registered 55/6/5 rows")
    selected_indices = sorted([*train_indices, *validation_indices])
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
        expected_shape=(66,),
        expected_dtype="int32",
    )
    train_target_ids = stream_npz_rows(
        cache_path,
        "target_token_ids",
        train_indices,
        expected_shape=source["ctc_arrays"]["target_token_ids_shape"],
        expected_dtype="int16",
    )
    train_target_lengths = stream_npz_rows(
        cache_path,
        "target_lengths",
        train_indices,
        expected_shape=source["ctc_arrays"]["target_lengths_shape"],
        expected_dtype="int32",
    )
    train_target_texts = stream_npz_rows(
        cache_path,
        "target_texts",
        train_indices,
        expected_shape=source["ctc_arrays"]["target_texts_shape"],
    )
    channel_rows = stream_npz_rows(
        cache_path,
        "channel_names",
        range(source["channels"]["count"]),
        expected_shape=(source["channels"]["count"],),
    )
    streams = [
        signals,
        lengths,
        train_target_ids,
        train_target_lengths,
        train_target_texts,
        channel_rows,
    ]
    counters["archive_header_reads"] += len(streams)
    counters["archive_row_member_streams"] += len(streams)
    counters["opaque_excluded_row_traversals"] += sum(
        row.opaque_excluded_rows_traversed for row in streams
    )
    selected_position = {row_index: position for position, row_index in enumerate(selected_indices)}
    train_positions = [selected_position[value] for value in train_indices]
    validation_positions = [selected_position[value] for value in validation_indices]
    train_signals = np.ascontiguousarray(signals.values[train_positions], dtype="float32")
    validation_signals = np.ascontiguousarray(signals.values[validation_positions], dtype="float32")
    train_input_lengths = np.ascontiguousarray(lengths.values[train_positions], dtype="int32")
    validation_input_lengths = np.ascontiguousarray(
        lengths.values[validation_positions], dtype="int32"
    )
    membership = _membership_by_index(_read_json(root / source["split_report"]["path"]))
    train_identity = _identity_arrays(np, membership, train_indices)
    validation_identity = _identity_arrays(np, membership, validation_indices)
    target_texts = np.asarray(
        [normalize_ctc_text(str(value)) for value in train_target_texts.values.tolist()]
    )
    _validate_train_targets(
        train_target_ids.values,
        train_target_lengths.values,
        target_texts,
    )
    channel_names = np.asarray([str(value) for value in channel_rows.values.tolist()])
    common_metadata = {
        "source_cache_sha256": hash_report["sha256"],
        "source_cache_bytes": hash_report["bytes"],
        "protocol_config_sha256": source["split_report"]["protocol_config_sha256"],
        "group_assignment_sha256": source["split_report"]["group_assignment_sha256"],
        "semantic_membership_sha256": source["split_report"]["semantic_membership_sha256"],
        "physical_membership_sha256": source["split_report"]["physical_membership_sha256"],
        "ordered_channel_names_sha256": source["channels"]["ordered_names_sha256"],
        "scaler_center_sha256": source["frozen_scaler"]["center_sha256"],
        "scaler_scale_sha256": source["frozen_scaler"]["scale_sha256"],
        "upstream_cache_causal": False,
        "sampling_rate_hz": cache_contract["sampling_rate_hz"],
    }
    train_arrays = {
        "signals": train_signals,
        "input_lengths": train_input_lengths,
        "target_token_ids": np.ascontiguousarray(train_target_ids.values, dtype="int16"),
        "target_lengths": np.ascontiguousarray(train_target_lengths.values, dtype="int32"),
        "target_texts": target_texts,
        "channel_names": channel_names,
        **train_identity,
    }
    validation_arrays = {
        "signals": validation_signals,
        "input_lengths": validation_input_lengths,
        "channel_names": channel_names,
        **validation_identity,
    }
    train_metadata = {
        "schema": {"name": "neurodecodekit.loop26_train_bundle", "version": 0},
        "split": "train",
        "contains_signals": True,
        "contains_targets": True,
        "rows": 55,
        **common_metadata,
    }
    validation_metadata = {
        "schema": {"name": "neurodecodekit.loop26_validation_inputs", "version": 0},
        "split": "val",
        "contains_signals": True,
        "contains_targets": False,
        "rows": 6,
        **common_metadata,
    }
    _write_npz(train_path, train_arrays, train_metadata)
    _write_npz(validation_path, validation_arrays, validation_metadata)
    counters["train_signal_rows_delivered"] += 55
    counters["train_target_rows_delivered"] += 55
    counters["validation_signal_rows_delivered"] += 6
    working_array_bytes = sum(
        int(value.nbytes)
        for value in [
            signals.values,
            lengths.values,
            train_signals,
            validation_signals,
            train_target_ids.values,
            train_target_lengths.values,
            target_texts,
        ]
    )
    report = {
        "schema_name": "neurodecodekit.loop26_isolated_derivatives",
        "schema_version": "0.1.0",
        "status": "passed",
        "source_hash_pass": hash_report,
        "artifacts": {
            "train_bundle": _artifact_descriptor(train_path, train_arrays, train_metadata),
            "validation_inputs": _artifact_descriptor(
                validation_path, validation_arrays, validation_metadata
            ),
        },
        "source_test_derivatives": 0,
        "validation_targets_present_in_prediction_inputs": False,
        "reader_ledgers": [row.ledger() for row in streams],
        "access_counters": counters,
        "working_array_bytes": working_array_bytes,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "warnings": [
            "deflate_required_opaque_traversal_of_excluded_rows",
            "opaque_traversal_is_not_physical_nonaccess",
            "validation_target_bytes_were_not_returned_to_derivatives",
            "source_test_rows_were_not_returned",
        ],
    }
    caps = contract["resource_caps"]
    if working_array_bytes > caps["maximum_working_array_bytes"]:
        raise SharedS21GateError("derivative working arrays exceed 128 MiB cap")
    generated = _directory_bytes(output)
    if generated > caps["total_generated_artifact_bytes"]:
        raise SharedS21GateError("generated artifacts exceed 32 MiB cap")
    report["generated_artifact_bytes_before_report"] = generated
    _write_bounded_json(report_path, report, maximum_bytes=1024 * 1024)
    final_generated = _directory_bytes(output)
    if final_generated > caps["total_generated_artifact_bytes"]:
        raise SharedS21GateError("final derivative artifacts exceed 32 MiB cap")
    return report


def run_target_blind_shared_s21_gate(
    *,
    repo_root: str | Path,
    implementation_commit: str,
    freeze_record_out: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Run all registered fits and freeze 31 prediction sets without targets."""

    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    report_path = output / TARGET_BLIND_REPORT_NAME
    freeze_path = Path(freeze_record_out)
    if not freeze_path.is_absolute():
        freeze_path = root / freeze_path
    for path in (report_path, freeze_path):
        _refuse_existing(path)
    if _git_head(root) != str(implementation_commit):
        raise SharedS21GateError(
            "target-blind run must use the remotely green implementation commit"
        )
    derivatives = _read_json(output / DERIVATIVE_REPORT_NAME)
    train = _load_derivative(
        output / "train_bundle.npz", expected_schema="neurodecodekit.loop26_train_bundle"
    )
    validation = _load_derivative(
        output / "validation_inputs.npz", expected_schema="neurodecodekit.loop26_validation_inputs"
    )
    _validate_target_blind_derivatives(train, validation)
    contract = _read_json(root / CONTRACT_PATH)
    counters = {key: int(value) for key, value in derivatives["access_counters"].items()}
    started_at = time.perf_counter()
    prediction_dir = output / "predictions"
    checkpoint_dir = output / "checkpoints"
    prediction_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    prefix_order = registered_prefix_order(
        train["semantic_ids"].tolist(),
        train["performed_row_ids"].tolist(),
    )
    if len(prefix_order) != 55 or sorted(prefix_order) != list(range(55)):
        raise SharedS21GateError("registered prefix order does not cover all 55 train rows")
    prediction_rows = []
    training_summaries = []
    checkpoint_descriptors = []
    primary_model = None
    primary_prediction_payload = None
    primary_checkpoint_sha256 = None

    for size in PREFIX_SIZES:
        indices = prefix_order[:size]
        prior_prediction = _train_only_prior(train["target_texts"][indices].tolist())
        prior_id = prior_prediction_id(size)
        prior_path = prediction_dir / f"{prior_id}.json"
        prior_config = {
            "kind": "train_only_most_frequent_sentence_prior",
            "prefix_size": size,
            "prefix_indices_sha256": _sha256_json(indices),
            "fit_on_validation_targets": False,
        }
        prediction_rows.append(
            write_prediction_payload(
                prior_path,
                condition_id=prior_id,
                item_ids=validation["item_ids"].tolist(),
                predictions=[prior_prediction] * 6,
                input_lengths=validation["input_lengths"].tolist(),
                configuration=prior_config,
                checkpoint_sha256_or_reason="no_checkpoint_train_only_prior",
                transform={"name": "no_signal_prior"},
                runtime_sec=0.0,
                peak_rss_bytes=_peak_rss_bytes(),
                model_run_count=0,
                blank_fraction=None,
                warnings=["no_neural_signal_used"],
            )
        )
        counters["no_signal_prior_fits"] += 1
        for seed in SEEDS:
            condition_id = candidate_prediction_id(size, seed)
            config = registered_candidate_config(seed=seed)
            training = train_causal_sentence_ctc(
                signals=train["signals"][indices],
                input_lengths=train["input_lengths"][indices],
                target_token_ids=train["target_token_ids"][indices],
                target_lengths=train["target_lengths"][indices],
                config=config,
            )
            checkpoint_path = checkpoint_dir / f"{condition_id}.npz"
            checkpoint = save_causal_sentence_ctc_checkpoint(
                checkpoint_path,
                training=training,
                metadata={
                    "condition_id": condition_id,
                    "prefix_size": size,
                    "prefix_indices_sha256": _sha256_json(indices),
                    "target_source": "train_derivative_only",
                    "validation_targets_available": False,
                },
            )
            prediction = predict_causal_sentence_ctc(
                training.model,
                signals=validation["signals"],
                input_lengths=validation["input_lengths"],
            )
            prediction_path = prediction_dir / f"{condition_id}.json"
            prediction_rows.append(
                write_prediction_payload(
                    prediction_path,
                    condition_id=condition_id,
                    item_ids=validation["item_ids"].tolist(),
                    predictions=prediction["predictions"],
                    input_lengths=validation["input_lengths"].tolist(),
                    configuration={
                        "model_config": config.to_dict(),
                        "prefix_size": size,
                        "prefix_indices_sha256": _sha256_json(indices),
                    },
                    checkpoint_sha256_or_reason=checkpoint["sha256"],
                    transform={"name": "identity"},
                    runtime_sec=prediction["runtime_sec"],
                    peak_rss_bytes=prediction["peak_rss_bytes"],
                    model_run_count=1,
                    blank_fraction=prediction["blank_fraction"],
                    warnings=["model_causal_upstream_cache_noncausal"],
                )
            )
            counters["candidate_training_runs"] += 1
            counters["optimizer_steps"] += training.optimizer_steps
            counters["checkpoint_writes"] += 1
            counters["target_blind_model_inference_runs"] += 1
            training_summaries.append(_compact_training_summary(condition_id, training))
            checkpoint_descriptors.append(
                {
                    "condition_id": condition_id,
                    "bytes": checkpoint["bytes"],
                    "sha256": checkpoint["sha256"],
                    "parameter_payload_sha256": checkpoint["parameter_payload_sha256"],
                }
            )
            if size == 55 and seed == 2601:
                primary_model = training.model
                primary_prediction_payload = prediction
                primary_checkpoint_sha256 = checkpoint["sha256"]

    if (
        primary_model is None
        or primary_prediction_payload is None
        or primary_checkpoint_sha256 is None
    ):
        raise SharedS21GateError("primary size-55 seed-2601 checkpoint is unavailable")

    prediction_rows.extend(
        _run_inference_controls(
            train=train,
            validation=validation,
            output=output,
            primary_model=primary_model,
            primary_prediction=primary_prediction_payload,
            primary_checkpoint_sha256=primary_checkpoint_sha256,
            counters=counters,
            training_summaries=training_summaries,
            checkpoint_descriptors=checkpoint_descriptors,
        )
    )
    total_parameter_runtime = sum(float(row["runtime_sec"]) for row in training_summaries)
    counters["prediction_sets_frozen"] = len(prediction_rows)
    if set(row["condition_id"] for row in prediction_rows) != set(expected_prediction_ids()):
        raise SharedS21GateError("target-blind run did not produce the exact 31-set inventory")
    _validate_exact_target_blind_counters(counters)
    candidate_summaries = [
        row for row in training_summaries if row["condition_id"].startswith("L33-N")
    ]
    control_summaries = {
        row["condition_id"]: row
        for row in training_summaries
        if row["condition_id"].startswith("L31-")
    }
    if len(candidate_summaries) != 18 or any(
        row["parameter_count"] != 2908 for row in candidate_summaries
    ):
        raise SharedS21GateError("candidate parameter accounting differs from 18 x 2,908")
    if set(control_summaries) != {"L31-E06", "L31-E08", "L31-E09"}:
        raise SharedS21GateError("control training inventory differs from the registered three")
    if control_summaries["L31-E06"]["parameter_count"] != 2908:
        raise SharedS21GateError("timing-only candidate exceeds the registered parameter count")
    if control_summaries["L31-E08"]["parameter_count"] != 2908:
        raise SharedS21GateError("target-deranged candidate exceeds the registered parameter count")
    if control_summaries["L31-E09"]["parameter_count"] != 2884:
        raise SharedS21GateError("linear comparator differs from the registered parameter count")
    checkpoint_bytes = sum(int(row["bytes"]) for row in checkpoint_descriptors)
    prediction_payload_bytes = sum(int(row["private_payload_bytes"]) for row in prediction_rows)
    working_array_bytes = _target_blind_working_array_upper_bound(train, validation)
    generated_bytes = _directory_bytes(output)
    end_to_end_runtime = time.perf_counter() - started_at
    freeze = build_prediction_freeze_record(
        contract_sha256=_file_sha256(root / CONTRACT_PATH),
        authorization_decision_sha256=_file_sha256(root / AUTHORIZATION_PATH),
        implementation_commit=str(implementation_commit),
        prediction_rows=prediction_rows,
        access_counters=counters,
        generated_artifact_bytes=generated_bytes,
        checkpoint_bytes=checkpoint_bytes,
        prediction_payload_bytes=prediction_payload_bytes,
        parameter_update_runtime_sec=total_parameter_runtime,
        end_to_end_runtime_sec=end_to_end_runtime,
        peak_rss_bytes=_peak_rss_bytes(),
        warnings=[
            "validation_targets_unavailable_to_prediction_process",
            "upstream_cache_offline_noncausal",
            "six_rows_one_person_one_session",
        ],
    )
    caps = contract["resource_caps"]
    _enforce_run_caps(
        caps,
        generated_bytes=generated_bytes,
        checkpoint_bytes=checkpoint_bytes,
        prediction_bytes=prediction_payload_bytes,
        parameter_runtime=total_parameter_runtime,
        end_to_end_runtime=end_to_end_runtime,
        peak_rss=_peak_rss_bytes(),
    )
    _write_bounded_json(freeze_path, freeze, maximum_bytes=2 * 1024 * 1024)
    report = {
        "schema_name": "neurodecodekit.loop26_target_blind_run",
        "schema_version": "0.1.0",
        "status": "predictions_frozen_targets_unavailable",
        "implementation_commit": str(implementation_commit),
        "prefix_order": prefix_order,
        "prefix_order_sha256": _sha256_json(prefix_order),
        "training_summaries": training_summaries,
        "checkpoints": checkpoint_descriptors,
        "prediction_set_count": len(prediction_rows),
        "prediction_condition_ids": sorted(row["condition_id"] for row in prediction_rows),
        "freeze_record_path": str(freeze_path),
        "freeze_record_sha256": _file_sha256(freeze_path),
        "access_counters": counters,
        "resources": freeze["resources"],
        "working_array_bytes_upper_bound": working_array_bytes,
        "validation_target_rows_delivered": 0,
        "validation_scoring_runs": 0,
        "warnings": freeze["warnings"],
    }
    if working_array_bytes > caps["maximum_working_array_bytes"]:
        raise SharedS21GateError("target-blind working arrays exceed 128 MiB cap")
    _write_bounded_json(report_path, report, maximum_bytes=2 * 1024 * 1024)
    final_generated = _generated_artifact_bytes(output, freeze_path)
    if final_generated > caps["total_generated_artifact_bytes"]:
        raise SharedS21GateError("final target-blind artifacts exceed 32 MiB cap")
    return report


def score_frozen_shared_s21_validation(
    *,
    repo_root: str | Path,
    freeze_record_path: str | Path,
    green_freeze_commit: str,
    public_report_out: str | Path,
    output_root: str | Path = REGISTERED_OUTPUT_ROOT,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Deliver six targets once and score all frozen sets in one consumed event."""

    np = _require_numpy()
    root = Path(repo_root).resolve()
    output = _resolve_output_root(root, output_root, enforce_registered_paths)
    consumed = output / CONSUMED_MARKER_NAME
    _refuse_existing(consumed)
    if _git_head(root) != str(green_freeze_commit):
        raise SharedS21GateError("scoring requires the remotely green freeze commit at HEAD")
    freeze_path = Path(freeze_record_path)
    if not freeze_path.is_absolute():
        freeze_path = root / freeze_path
    freeze = _read_json(freeze_path)
    if not _path_tracked_at_head(root, freeze_path):
        raise SharedS21GateError("prediction freeze record is not tracked at green HEAD")
    validate_prediction_freeze_record(freeze)
    target_blind = _read_json(output / TARGET_BLIND_REPORT_NAME)
    if target_blind["freeze_record_sha256"] != _file_sha256(freeze_path):
        raise SharedS21GateError("committed freeze record differs from target-blind run")
    public_path = Path(public_report_out)
    if not public_path.is_absolute():
        public_path = root / public_path
    _refuse_existing(public_path)
    marker = {
        "status": "target_delivery_started_rerun_forbidden_even_if_interrupted",
        "green_freeze_commit": str(green_freeze_commit),
        "freeze_record_sha256": _file_sha256(freeze_path),
    }
    _write_bounded_json(consumed, marker, maximum_bytes=16 * 1024)
    contract = _read_json(root / CONTRACT_PATH)
    source = contract["source_contract"]
    cache_path = root / source["cache"]["path"]
    validation = _load_derivative(
        output / "validation_inputs.npz", expected_schema="neurodecodekit.loop26_validation_inputs"
    )
    indices = [
        int(value) for value in _read_json(output / STATIC_REPORT_NAME)["split_partitions"]["val"]
    ]
    target_ids = stream_npz_rows(
        cache_path,
        "target_token_ids",
        indices,
        expected_shape=source["ctc_arrays"]["target_token_ids_shape"],
        expected_dtype="int16",
    )
    target_lengths = stream_npz_rows(
        cache_path,
        "target_lengths",
        indices,
        expected_shape=source["ctc_arrays"]["target_lengths_shape"],
        expected_dtype="int32",
    )
    targets = []
    for row, length in zip(target_ids.values, target_lengths.values, strict=True):
        targets.append(decode_ctc_target(row[: int(length)]))
    target_path = output / "validation_targets.npz"
    _refuse_existing(target_path)
    target_arrays = {
        "target_token_ids": np.ascontiguousarray(target_ids.values, dtype="int16"),
        "target_lengths": np.ascontiguousarray(target_lengths.values, dtype="int32"),
        "target_texts": np.asarray(targets),
        "item_ids": validation["item_ids"],
    }
    _write_npz(
        target_path,
        target_arrays,
        {
            "schema": {"name": "neurodecodekit.loop26_validation_targets", "version": 0},
            "rows": 6,
            "created_after_green_prediction_freeze_commit": str(green_freeze_commit),
        },
    )
    payloads = {}
    rows_by_id = {row["condition_id"]: row for row in freeze["prediction_sets"]}
    for condition_id in expected_prediction_ids():
        path = output / "predictions" / f"{condition_id}.json"
        freeze_row = rows_by_id[condition_id]
        try:
            payloads[condition_id] = load_prediction_payload(path, freeze_row)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise SharedS21GateError(
                f"prediction payload changed after freeze: {condition_id}"
            ) from exc
    score = score_shared_validation(
        prediction_payloads=payloads,
        target_item_ids=validation["item_ids"].tolist(),
        targets=targets,
    )
    counters = {key: int(value) for key, value in freeze["access_counters"].items()}
    counters["archive_header_reads"] += 2
    counters["archive_row_member_streams"] += 2
    counters["opaque_excluded_row_traversals"] += (
        target_ids.opaque_excluded_rows_traversed + target_lengths.opaque_excluded_rows_traversed
    )
    counters["validation_target_rows_delivered_after_prediction_freeze"] += 6
    counters["validation_scoring_runs"] += 1
    _validate_exact_scoring_counters(counters)
    score.update(
        {
            "contract_sha256": _file_sha256(root / CONTRACT_PATH),
            "authorization_decision_sha256": _file_sha256(root / AUTHORIZATION_PATH),
            "prediction_freeze_sha256": _file_sha256(freeze_path),
            "green_prediction_freeze_commit": str(green_freeze_commit),
            "access_counters": counters,
            "validation_target_delivery_events": 1,
            "source_test_rows_delivered_or_scored": 0,
            "session2_rows_delivered_or_scored": 0,
            "post_target_parameter_updates": 0,
            "post_target_configuration_changes": 0,
            "generated_artifact_bytes": _directory_bytes(output),
            "validation_target_artifact": {
                "bytes": int(target_path.stat().st_size),
                "sha256": _file_sha256(target_path),
                "target_texts_sha256": _sha256_json(targets),
                "target_item_ids_sha256": _sha256_json(validation["item_ids"].tolist()),
            },
        }
    )
    _write_bounded_json(public_path, score, maximum_bytes=2 * 1024 * 1024)
    final_generated = _generated_artifact_bytes(output, freeze_path, public_path)
    caps = contract["resource_caps"]
    if final_generated > caps["total_generated_artifact_bytes"]:
        raise SharedS21GateError("final scored artifacts exceed 32 MiB cap")
    if _peak_rss_bytes() > caps["peak_rss_bytes"]:
        raise SharedS21GateError("final scoring peak RSS exceeds 1 GiB cap")
    marker.update(
        {
            "status": "consumed_scored_no_rerun_authorized",
            "public_report_sha256": _file_sha256(public_path),
            "result": score["status"],
        }
    )
    _write_replace_json(consumed, marker, maximum_bytes=16 * 1024)
    return score


def _run_inference_controls(
    *,
    train: Mapping[str, Any],
    validation: Mapping[str, Any],
    output: Path,
    primary_model,
    primary_prediction: Mapping[str, Any],
    primary_checkpoint_sha256: str,
    counters: dict[str, int],
    training_summaries: list[dict[str, Any]],
    checkpoint_descriptors: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    prediction_dir = output / "predictions"
    rows = []

    def infer_control(condition_id, signals, transform):
        prediction = predict_causal_sentence_ctc(
            primary_model,
            signals=signals,
            input_lengths=validation["input_lengths"],
        )
        counters["target_blind_model_inference_runs"] += 1
        return write_prediction_payload(
            prediction_dir / f"{condition_id}.json",
            condition_id=condition_id,
            item_ids=validation["item_ids"].tolist(),
            predictions=prediction["predictions"],
            input_lengths=validation["input_lengths"].tolist(),
            configuration={"source_checkpoint": "L33-N55-S2601"},
            checkpoint_sha256_or_reason=primary_checkpoint_sha256,
            transform=transform,
            runtime_sec=prediction["runtime_sec"],
            peak_rss_bytes=prediction["peak_rss_bytes"],
            model_run_count=1,
            blank_fraction=prediction["blank_fraction"],
            warnings=["target_blind_control"],
        )

    rows.append(
        infer_control(
            "L31-E02",
            zero_valid_signals(validation["signals"]),
            {"name": "exact_zero_valid_signal"},
        )
    )
    deranged_predictions, row_mapping = derange_validation_predictions(
        primary_prediction["predictions"], validation["item_ids"].tolist()
    )
    rows.append(
        write_prediction_payload(
            prediction_dir / "L31-E03.json",
            condition_id="L31-E03",
            item_ids=validation["item_ids"].tolist(),
            predictions=deranged_predictions,
            input_lengths=validation["input_lengths"].tolist(),
            configuration={"source_prediction": "L33-N55-S2601"},
            checkpoint_sha256_or_reason=primary_checkpoint_sha256,
            transform={"name": "validation_row_derangement", "mapping": row_mapping},
            runtime_sec=0.0,
            peak_rss_bytes=_peak_rss_bytes(),
            model_run_count=0,
            blank_fraction=primary_prediction["blank_fraction"],
            warnings=["prediction_remap_no_model_run"],
        )
    )
    channel_values, channel_mapping = apply_channel_derangement(
        validation["signals"], validation["channel_names"].tolist()
    )
    rows.append(
        infer_control(
            "L31-E04",
            channel_values,
            {"name": "channel_name_hash_derangement", "mapping": channel_mapping},
        )
    )
    delayed, delay_report = apply_time_displacement(
        validation["signals"], validation["input_lengths"]
    )
    rows.append(infer_control("L31-E05", delayed, {"name": "time_displacement", **delay_report}))

    full_indices = list(range(55))
    timing_train = timing_only_signals(train["signals"], train["input_lengths"])
    timing_validation = timing_only_signals(validation["signals"], validation["input_lengths"])
    timing_row = _fit_control(
        condition_id="L31-E06",
        architecture="candidate",
        train_signals=timing_train,
        validation_signals=timing_validation,
        train=train,
        validation=validation,
        target_token_ids=train["target_token_ids"],
        target_lengths=train["target_lengths"],
        transform={"name": "timing_only", "signal_values_used": False},
        output=output,
        counters=counters,
        training_summaries=training_summaries,
        checkpoint_descriptors=checkpoint_descriptors,
    )
    rows.append(timing_row)
    deranged_ids, deranged_lengths, _texts, target_mapping = derange_train_targets(
        train["target_token_ids"],
        train["target_lengths"],
        train["target_texts"].tolist(),
        train["semantic_ids"].tolist(),
    )
    rows.append(
        _fit_control(
            condition_id="L31-E08",
            architecture="candidate",
            train_signals=train["signals"],
            validation_signals=validation["signals"],
            train=train,
            validation=validation,
            target_token_ids=deranged_ids,
            target_lengths=deranged_lengths,
            transform={"name": "train_target_derangement", "mapping": target_mapping},
            output=output,
            counters=counters,
            training_summaries=training_summaries,
            checkpoint_descriptors=checkpoint_descriptors,
        )
    )
    rows.append(
        _fit_control(
            condition_id="L31-E09",
            architecture="linear",
            train_signals=train["signals"][full_indices],
            validation_signals=validation["signals"],
            train=train,
            validation=validation,
            target_token_ids=train["target_token_ids"],
            target_lengths=train["target_lengths"],
            transform={"name": "identity"},
            output=output,
            counters=counters,
            training_summaries=training_summaries,
            checkpoint_descriptors=checkpoint_descriptors,
        )
    )
    if {row["condition_id"] for row in rows} != set(ADDITIONAL_CONTROL_IDS):
        raise SharedS21GateError("additional Loop 31 controls are incomplete")
    return rows


def _fit_control(
    *,
    condition_id: str,
    architecture: str,
    train_signals,
    validation_signals,
    train: Mapping[str, Any],
    validation: Mapping[str, Any],
    target_token_ids,
    target_lengths,
    transform: Mapping[str, Any],
    output: Path,
    counters: dict[str, int],
    training_summaries: list[dict[str, Any]],
    checkpoint_descriptors: list[dict[str, Any]],
) -> dict[str, Any]:
    config = (
        registered_candidate_config(seed=2601)
        if architecture == "candidate"
        else registered_linear_config(seed=2601)
    )
    training = train_causal_sentence_ctc(
        signals=train_signals,
        input_lengths=train["input_lengths"],
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        config=config,
    )
    checkpoint = save_causal_sentence_ctc_checkpoint(
        output / "checkpoints" / f"{condition_id}.npz",
        training=training,
        metadata={
            "condition_id": condition_id,
            "target_source": "train_derivative_only",
            "validation_targets_available": False,
            "transform_sha256": _sha256_json(dict(transform)),
        },
    )
    prediction = predict_causal_sentence_ctc(
        training.model,
        signals=validation_signals,
        input_lengths=validation["input_lengths"],
    )
    counters["control_training_runs"] += 1
    counters["optimizer_steps"] += training.optimizer_steps
    counters["checkpoint_writes"] += 1
    counters["target_blind_model_inference_runs"] += 1
    training_summaries.append(_compact_training_summary(condition_id, training))
    checkpoint_descriptors.append(
        {
            "condition_id": condition_id,
            "bytes": checkpoint["bytes"],
            "sha256": checkpoint["sha256"],
            "parameter_payload_sha256": checkpoint["parameter_payload_sha256"],
        }
    )
    return write_prediction_payload(
        output / "predictions" / f"{condition_id}.json",
        condition_id=condition_id,
        item_ids=validation["item_ids"].tolist(),
        predictions=prediction["predictions"],
        input_lengths=validation["input_lengths"].tolist(),
        configuration={"model_config": config.to_dict(), "control_id": condition_id},
        checkpoint_sha256_or_reason=checkpoint["sha256"],
        transform=transform,
        runtime_sec=prediction["runtime_sec"],
        peak_rss_bytes=prediction["peak_rss_bytes"],
        model_run_count=1,
        blank_fraction=prediction["blank_fraction"],
        warnings=["target_blind_control_fit"],
    )


def _validate_split_report(split: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, bool]:
    membership = split.get("membership") or {}
    partition_indices = _partition_indices(split)
    expected = source["split_report"]
    return {
        "split_schema": (split.get("schema") or {}).get("name") == "b2q-split-protocol",
        "split_strict_training_ready": membership.get("strict_training_ready") is True,
        "split_partition_rows": {key: len(value) for key, value in partition_indices.items()}
        == expected["partition_rows"],
        "protocol_config_sha256": membership.get("protocol_config_sha256")
        == expected["protocol_config_sha256"],
        "group_assignment_sha256": membership.get("group_assignment_sha256")
        == expected["group_assignment_sha256"],
        "semantic_membership_sha256": membership.get("semantic_membership_sha256")
        == expected["semantic_membership_sha256"],
        "physical_membership_sha256": membership.get("membership_sha256")
        == expected["physical_membership_sha256"],
    }


def _partition_indices(split: Mapping[str, Any]) -> dict[str, list[int]]:
    rows = (split.get("membership") or {}).get("rows") or []
    partitions = {"train": [], "val": [], "test": []}
    seen = set()
    for row in rows:
        index = int(row["source_row_index"])
        split_name = str(row["split"])
        if index in seen or split_name not in partitions:
            raise SharedS21GateError("split membership is duplicated or unknown")
        seen.add(index)
        partitions[split_name].append(index)
    if seen != set(range(len(rows))):
        raise SharedS21GateError("split membership does not cover contiguous source rows")
    return {key: sorted(value) for key, value in partitions.items()}


def _membership_by_index(split: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    return {
        int(row["source_row_index"]): row for row in (split.get("membership") or {}).get("rows", [])
    }


def _identity_arrays(np, membership: Mapping[int, Mapping[str, Any]], indices: Sequence[int]):
    rows = [membership[int(index)] for index in indices]
    return {
        "source_row_indices": np.asarray(indices, dtype="int32"),
        "item_ids": np.asarray([row["row_uid_sha256"] for row in rows]),
        "semantic_ids": np.asarray([row["semantic_row_uid_sha256"] for row in rows]),
        "performed_row_ids": np.asarray([row["row_uid_sha256"] for row in rows]),
    }


def _validate_train_targets(target_ids, target_lengths, target_texts) -> None:
    for row, length, text in zip(target_ids, target_lengths, target_texts, strict=True):
        decoded = decode_ctc_target(row[: int(length)])
        if decoded != str(text):
            raise SharedS21GateError("train target text does not match encoded IDs")


def _write_npz(path: Path, arrays: Mapping[str, Any], metadata: Mapping[str, Any]) -> None:
    np = _require_numpy()
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays, metadata=json.dumps(dict(metadata), sort_keys=True))


def _load_derivative(path: Path, *, expected_schema: str) -> dict[str, Any]:
    np = _require_numpy()
    with np.load(path, allow_pickle=False) as data:
        arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
        metadata_value = data["metadata"].item()
    metadata = json.loads(metadata_value)
    if (metadata.get("schema") or {}).get("name") != expected_schema:
        raise SharedS21GateError(f"unexpected derivative schema at {path}")
    arrays["metadata"] = metadata
    return arrays


def _validate_target_blind_derivatives(
    train: Mapping[str, Any], validation: Mapping[str, Any]
) -> None:
    if train["signals"].shape[:2] != (55, 102):
        raise SharedS21GateError("train derivative geometry is invalid")
    if validation["signals"].shape[:2] != (6, 102):
        raise SharedS21GateError("validation derivative geometry is invalid")
    forbidden = {"target_token_ids", "target_lengths", "target_texts"}
    if forbidden & set(validation):
        raise SharedS21GateError("validation inputs contain forbidden target arrays")
    if train["metadata"].get("source_cache_sha256") != validation["metadata"].get(
        "source_cache_sha256"
    ):
        raise SharedS21GateError("train and validation derivatives bind different sources")
    if train["channel_names"].tolist() != validation["channel_names"].tolist():
        raise SharedS21GateError("train and validation channel identities differ")


def _validate_exact_target_blind_counters(counters: Mapping[str, int]) -> None:
    mismatches = {
        name: {"actual": int(counters.get(name, -1)), "expected": expected}
        for name, expected in EXACT_TARGET_BLIND_COUNTERS.items()
        if int(counters.get(name, -1)) != expected
    }
    if mismatches:
        raise SharedS21GateError(f"target-blind access counters mismatch: {mismatches}")


def _validate_exact_scoring_counters(counters: Mapping[str, int]) -> None:
    expected = {
        **EXACT_TARGET_BLIND_COUNTERS,
        "archive_header_reads": 22,
        "archive_row_member_streams": 10,
        "validation_target_rows_delivered_after_prediction_freeze": 6,
        "validation_scoring_runs": 1,
    }
    mismatches = {
        name: {"actual": int(counters.get(name, -1)), "expected": value}
        for name, value in expected.items()
        if int(counters.get(name, -1)) != value
    }
    if mismatches:
        raise SharedS21GateError(f"scoring access counters mismatch: {mismatches}")


def _target_blind_working_array_upper_bound(
    train: Mapping[str, Any], validation: Mapping[str, Any]
) -> int:
    """Conservative bound for resident derivative and largest transformed arrays."""

    array_bytes = sum(
        int(value.nbytes)
        for bundle in (train, validation)
        for name, value in bundle.items()
        if name != "metadata" and hasattr(value, "nbytes")
    )
    largest_transform = max(int(train["signals"].nbytes), int(validation["signals"].nbytes))
    largest_prefix_copy = int(train["signals"].nbytes)
    return array_bytes + largest_transform + largest_prefix_copy


def _artifact_descriptor(path: Path, arrays: Mapping[str, Any], metadata: Mapping[str, Any]):
    return {
        "path": str(path),
        "bytes": int(path.stat().st_size),
        "sha256": _file_sha256(path),
        "arrays": {
            name: {
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "sha256": _array_sha256(value),
            }
            for name, value in arrays.items()
        },
        "row_ids_sha256": _sha256_json(arrays["item_ids"].tolist()),
        "membership_sha256": metadata["semantic_membership_sha256"],
        "contains_targets": bool(metadata["contains_targets"]),
    }


def _compact_training_summary(condition_id: str, training) -> dict[str, Any]:
    return {
        "condition_id": condition_id,
        "optimizer_steps": training.optimizer_steps,
        "example_presentations": training.example_presentations,
        "completed_epochs": training.completed_epochs,
        "initial_loss": training.loss_history[0],
        "final_loss": training.loss_history[-1],
        "loss_history_sha256": _sha256_json(list(training.loss_history)),
        "parameter_count": training.parameter_count,
        "runtime_sec": training.runtime_sec,
        "peak_rss_bytes": training.peak_rss_bytes,
        "config_sha256": training.config.config_sha256,
    }


def _train_only_prior(targets: Sequence[str]) -> str:
    values = [str(value) for value in targets]
    counts = Counter(values)
    first_seen = {value: values.index(value) for value in counts}
    return min(counts, key=lambda value: (-counts[value], first_seen[value], value))


def _enforce_run_caps(
    caps: Mapping[str, Any],
    *,
    generated_bytes: int,
    checkpoint_bytes: int,
    prediction_bytes: int,
    parameter_runtime: float,
    end_to_end_runtime: float,
    peak_rss: int,
) -> None:
    checks = {
        "generated artifacts": (generated_bytes, caps["total_generated_artifact_bytes"]),
        "checkpoints": (checkpoint_bytes, caps["maximum_checkpoint_bytes"]),
        "prediction payloads": (prediction_bytes, caps["maximum_prediction_payload_bytes"]),
        "parameter runtime": (parameter_runtime, caps["total_parameter_update_runtime_sec"]),
        "end-to-end runtime": (end_to_end_runtime, caps["total_end_to_end_runtime_sec"]),
        "peak RSS": (peak_rss, caps["peak_rss_bytes"]),
    }
    failed = [name for name, (value, cap) in checks.items() if value > cap]
    if failed:
        raise SharedS21GateError(f"Loop 26 resource caps exceeded: {failed}")


def _resolve_output_root(root: Path, output_root: str | Path, enforce: bool) -> Path:
    output = Path(output_root)
    if not output.is_absolute():
        output = root / output
    output = output.resolve()
    registered = (root / REGISTERED_OUTPUT_ROOT).resolve()
    if enforce and output != registered:
        raise SharedS21GateError(f"registered execution output must be {registered}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def _single_thread_environment_ok() -> bool:
    required = (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    )
    return all(os.environ.get(name) == "1" for name in required)


def _environment_versions() -> dict[str, str]:
    import numpy
    import scipy
    import torch

    return {
        "python": platform.python_version(),
        "numpy": str(numpy.__version__),
        "torch": str(torch.__version__),
        "scipy": str(scipy.__version__),
    }


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


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SharedS21GateError(f"JSON object required: {path}")
    return value


def _write_bounded_json(path: Path, value: Mapping[str, Any], *, maximum_bytes: int) -> None:
    payload = (json.dumps(dict(value), indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > maximum_bytes:
        raise SharedS21GateError(f"JSON artifact exceeds {maximum_bytes} bytes: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(payload)


def _write_replace_json(path: Path, value: Mapping[str, Any], *, maximum_bytes: int) -> None:
    payload = (json.dumps(dict(value), indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > maximum_bytes:
        raise SharedS21GateError(f"JSON artifact exceeds {maximum_bytes} bytes: {path}")
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def _refuse_existing(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"Refusing to replace existing Loop 26 artifact: {path}")


def _directory_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def _generated_artifact_bytes(output: Path, *extra_paths: Path) -> int:
    files = {item.resolve() for item in output.rglob("*") if item.is_file()}
    files.update(path.resolve() for path in extra_paths if path.is_file())
    return sum(path.stat().st_size for path in files)


def _array_sha256(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if value > 10_000_000 else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Shared S21 validation requires NumPy: `pip install numpy`.") from exc
    return np
