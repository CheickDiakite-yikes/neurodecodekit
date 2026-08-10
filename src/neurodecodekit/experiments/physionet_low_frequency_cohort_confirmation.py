"""Frozen WO9R low-frequency cohort confirmation and isolated scorer."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import stat
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from neurodecodekit.datasets import physionet_low_frequency_acquisition as acquisition
from neurodecodekit.experiments import physionet_motor_positive_control as wo9


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = acquisition.CONTRACT_RELATIVE_PATH
DECISION_RELATIVE_PATH = acquisition.DECISION_RELATIVE_PATH
IMPLEMENTATION_RELATIVE_PATH = acquisition.IMPLEMENTATION_RELATIVE_PATH
CONTRACT_SHA256 = acquisition.CONTRACT_SHA256
DECISION_SHA256 = acquisition.DECISION_SHA256
DECISION_COMMIT = acquisition.DECISION_COMMIT
BUNDLE_RELATIVE_PATH = Path("data/physionet_motor/wo9r-eegmmidb-1.0.0")
ACQUISITION_MANIFEST_RELATIVE_PATH = Path(
    ".codex_work/physionet_low_frequency_cohort_confirmation/acquisition_receipt/"
    "physionet_low_frequency_cohort_acquisition_manifest.v0.json"
)
EXECUTION_ROOT_RELATIVE_PATH = Path(
    ".codex_work/physionet_low_frequency_cohort_confirmation/execution"
)
FREEZE_RELATIVE_PATH = Path(
    "registries/physionet_low_frequency_cohort_confirmation_prediction_freeze.v0.json"
)
RESULT_RELATIVE_PATH = Path(
    "registries/physionet_low_frequency_cohort_confirmation_result.v0.json"
)
FIT_DERIVATIVE_NAME = "fit_derivative.v0.npz"
PREDICTION_DERIVATIVE_NAME = "prediction_derivative.v0.npz"
SEALED_TARGET_NAME = "sealed_run11_and_run12_targets.v0.npz"
EXTRACTION_REPORT_NAME = "extraction_report.v0.json"
PRIVATE_PREDICTIONS_NAME = "private_predictions.v0.json"
TARGET_BLIND_REPORT_NAME = "target_blind_report.v0.json"
EXECUTION_CONSUMED_NAME = "execution_consumed.v0.json"
SCORING_CONSUMED_NAME = "scoring_consumed.v0.json"
SEED = 5909
CONDITION_IDS = (
    "execution_native_primary",
    "imagery_native",
    "execution_to_imagery",
    "imagery_to_execution",
    "execution_central_sensorimotor",
    "execution_frontal_proxy",
    "execution_occipital_proxy",
    "execution_frontal_asymmetry",
    "execution_early_cue",
    "execution_pre_cue",
    "execution_timing_only",
    "execution_no_signal_prior",
    "imagery_no_signal_prior",
    "execution_all_zero_final_signal",
    "execution_train_label_derangement",
    "execution_one_trial_final_signal_displacement",
    "execution_channel_derangement",
    "execution_central_hemisphere_swap",
)


class WO9RRefusal(RuntimeError):
    """A WO9R gate failed before a registered one-shot operation began."""


class WO9RFailure(RuntimeError):
    """A registered WO9R operation was consumed and parked."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


ImplementationEvidence = acquisition.ImplementationEvidence


@dataclass(frozen=True)
class FreezeEvidence:
    freeze_commit: str
    freeze_ci_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


Annotation = wo9.Annotation
RunRecord = wo9.RunRecord


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _np():
    return wo9._require_numpy()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return wo9._file_sha256(path)


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    return wo9._canonical_sha256(value)


def _write_json(path: Path, value: Mapping[str, Any], cap: int = 1024 * 1024) -> int:
    try:
        return wo9._write_json_exclusive(path, value, cap)
    except (wo9.WO9Failure, wo9.WO9Refusal) as exc:
        raise WO9RFailure("output", str(exc)) from exc


def _directory_bytes(path: Path) -> int:
    try:
        return wo9._directory_bytes(path)
    except wo9.WO9Failure as exc:
        raise WO9RFailure("output", str(exc)) from exc


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    return acquisition.load_registered_contract(repo_root)


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    return acquisition.load_registered_decision(repo_root)


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the frozen analysis plan without statting a real payload or target."""

    contract = load_registered_contract(repo_root)
    load_registered_decision(repo_root)
    binding = contract["dataset_binding"]
    caps = contract["resource_caps"]["analysis_and_scoring"]
    return {
        "schema_name": "neurodecodekit.physionet_low_frequency_confirmation_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_local_physionet_stat_open_hash_parse_or_target_read",
        "participants": binding["participants"],
        "execution_fit_runs": binding["execution_fit_runs"],
        "execution_final_run": binding["execution_sealed_final_run"],
        "imagery_fit_runs": binding["imagery_fit_runs"],
        "imagery_final_run": binding["imagery_sealed_final_run"],
        "file_count": binding["file_count"],
        "payload_bytes": binding["exact_payload_bytes"],
        "fit_rows": 720,
        "sealed_final_rows": 360,
        "model_family": contract["primary_model_template"]["family_id"],
        "parameter_update_fits": 144,
        "condition_families": list(CONDITION_IDS),
        "target_blind_inference_runs": 216,
        "caps": caps,
        "next_gate": "exact_implementation_commit_and_both_ci_jobs_must_be_green",
        "claim_ceiling": contract["claim_boundary"]["maximum_scientific_claim_if_WO9R_R4"],
    }


def dependency_versions() -> dict[str, str]:
    versions = wo9.dependency_versions()
    expected = load_registered_contract()["dependency_contract"]["exact_required_versions"]
    if versions != expected:
        raise WO9RRefusal(f"optional environment versions differ: {versions}")
    return versions


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    try:
        wo9._check_thread_environment(environ)
    except wo9.WO9Refusal as exc:
        raise WO9RRefusal(str(exc)) from exc


def _channel_indices(channel_names: Sequence[str], requested: Sequence[str]):
    try:
        return wo9._channel_indices(channel_names, requested)
    except wo9.WO9Failure as exc:
        raise WO9RFailure("channel", str(exc)) from exc


def _feature_rows(epoch: Any):
    np = _np()
    values = np.asarray(epoch, dtype="float64")
    if values.ndim != 2 or values.shape[0] != 64:
        raise WO9RFailure("feature", "feature epoch must have 64 channels")
    if values.shape[1] not in {160, 320} or values.shape[1] % 4:
        raise WO9RFailure("feature", "feature epoch must contain 160 or 320 samples")
    bins = values.reshape(64, 4, values.shape[1] // 4).mean(axis=-1)
    time_axis = np.linspace(-1.0, 1.0, values.shape[1], dtype="float64")
    slopes = values @ time_axis / float(np.dot(time_axis, time_axis))
    return np.ascontiguousarray(
        np.concatenate([bins, slopes[:, None]], axis=1),
        dtype="float32",
    )


def _window(values: Any, onset: float, start: float, stop: float):
    try:
        return wo9._window(values, onset, start, stop)
    except wo9.WO9Failure as exc:
        raise WO9RFailure("event_window", str(exc)) from exc


def extract_run_features(
    record: RunRecord,
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate one run and retain only compact causal features and identities."""

    np = _np()
    frozen = contract if contract is not None else load_registered_contract()
    binding = frozen["dataset_binding"]
    reader = frozen["reader_and_derivative_contract"]
    participants = set(binding["participants"])
    allowed_runs = set(reader["fit_derivative_runs"]) | set(
        reader["target_blind_prediction_derivative_runs"]
    )
    if record.subject not in participants or record.run not in allowed_runs:
        raise WO9RFailure("identity", "record identity is outside the WO9R grid")
    if not math.isclose(record.sampling_rate_hz, 160.0, rel_tol=0.0, abs_tol=1e-9):
        raise WO9RFailure("header", "sampling rate is not exactly 160 Hz")
    expected_channels = tuple(reader["standardized_channel_names"])
    if record.channel_names != expected_channels:
        raise WO9RFailure("header", "64-channel identity or order mismatch")
    values = np.asarray(record.signal_volts, dtype="float64")
    geometry = np.asarray(record.channel_geometry_m, dtype="float64")
    if values.ndim != 2 or values.shape[0] != 64 or values.shape[1] < 1:
        raise WO9RFailure("header", "signal shape is invalid")
    if geometry.shape != (64, 3) or not np.isfinite(geometry).all():
        raise WO9RFailure("geometry", "registered geometry is unavailable")
    if not np.isfinite(values).all():
        raise WO9RFailure("signal", "signal contains a nonfinite sample")
    annotations = sorted(record.annotations, key=lambda row: row.onset_seconds)
    if tuple(annotations) != record.annotations:
        raise WO9RFailure("annotation", "annotations are not monotone")
    allowed_annotations = set(reader["allowed_annotations"])
    if any(row.description not in allowed_annotations for row in annotations):
        raise WO9RFailure("annotation", "annotation is outside T0/T1/T2")
    task = [row for row in annotations if row.description in {"T1", "T2"}]
    if len(task) != 15 or len({row.onset_seconds for row in task}) != 15:
        raise WO9RFailure("annotation", "run must contain 15 unique task events")
    referenced = values - values.mean(axis=0, keepdims=True)
    try:
        low = wo9._causal_filter(referenced, 0.5, 4.0, 160.0)
    except wo9.WO9Failure as exc:
        raise WO9RFailure("filter", str(exc)) from exc
    features = []
    early = []
    pre = []
    physiology = []
    labels = []
    event_ids = []
    onsets = []
    previous_intervals = []
    previous_onset = None
    for event_index, annotation in enumerate(task):
        features.append(_feature_rows(_window(low, annotation.onset_seconds, 1.0, 3.0)))
        early.append(_feature_rows(_window(low, annotation.onset_seconds, 0.0, 1.0)))
        pre.append(_feature_rows(_window(low, annotation.onset_seconds, -2.0, 0.0)))
        baseline = _window(low, annotation.onset_seconds, -1.0, 0.0).astype("float64")
        active = _window(low, annotation.onset_seconds, 1.0, 3.0).astype("float64")
        physiology.append(active.mean(axis=1) - baseline.mean(axis=1))
        labels.append(0 if annotation.description == "T1" else 1)
        event_ids.append(f"{record.subject}-{record.run}-E{event_index:02d}")
        onsets.append(annotation.onset_seconds)
        previous_intervals.append(
            0.0 if previous_onset is None else annotation.onset_seconds - previous_onset
        )
        previous_onset = annotation.onset_seconds
    return {
        "features": np.stack(features).astype("float32"),
        "early_features": np.stack(early).astype("float32"),
        "pre_features": np.stack(pre).astype("float32"),
        "physiology_deltas": np.stack(physiology).astype("float32"),
        "labels": np.asarray(labels, dtype="int8"),
        "event_ids": np.asarray(event_ids),
        "subjects": np.asarray([record.subject] * 15),
        "runs": np.asarray([record.run] * 15),
        "event_indices": np.arange(15, dtype="int16"),
        "event_onsets_seconds": np.asarray(onsets, dtype="float64"),
        "previous_intervals_seconds": np.asarray(previous_intervals, dtype="float64"),
        "channel_names": np.asarray(record.channel_names),
        "channel_geometry_m": np.ascontiguousarray(geometry, dtype="float64"),
    }


def _concatenate(rows: Sequence[Mapping[str, Any]], *, include_labels: bool):
    np = _np()
    if not rows:
        raise WO9RFailure("derivative", "partition is empty")
    keys = (
        "features",
        "early_features",
        "pre_features",
        "physiology_deltas",
        "event_ids",
        "subjects",
        "runs",
        "event_indices",
        "event_onsets_seconds",
        "previous_intervals_seconds",
    )
    combined = {key: np.concatenate([row[key] for row in rows], axis=0) for key in keys}
    if include_labels:
        combined["labels"] = np.concatenate([row["labels"] for row in rows])
    combined["channel_names"] = rows[0]["channel_names"]
    combined["channel_geometry_m"] = rows[0]["channel_geometry_m"]
    for row in rows[1:]:
        if not np.array_equal(row["channel_names"], combined["channel_names"]):
            raise WO9RFailure("geometry", "channel names differ between runs")
        if not np.allclose(
            row["channel_geometry_m"],
            combined["channel_geometry_m"],
            rtol=0.0,
            atol=1e-12,
        ):
            raise WO9RFailure("geometry", "channel geometry differs between runs")
    return combined


def _validate_prediction_keys(keys: Iterable[str]) -> None:
    for key in keys:
        lowered = key.lower()
        if any(term in lowered for term in ("label", "target", "outcome", "reference")):
            raise WO9RFailure("firewall", f"prediction derivative contains {key!r}")


def extract_records_to_derivatives(
    records: Iterable[RunRecord],
    output_root: str | Path,
    *,
    source_file_hashes: Mapping[str, str],
    manifest_sha256: str,
    maximum_output_bytes: int = 64 * 1024 * 1024,
    contract: Mapping[str, Any] | None = None,
    allow_existing_consumed_marker: bool = False,
) -> dict[str, Any]:
    """Create compact fit, target-free final, and sealed-target derivatives."""

    frozen = contract if contract is not None else load_registered_contract()
    output = Path(output_root)
    if output.is_symlink():
        raise WO9RRefusal("exclusive derivative output is a symlink")
    if output.exists():
        allowed = {EXECUTION_CONSUMED_NAME} if allow_existing_consumed_marker else set()
        if not output.is_dir() or {row.name for row in output.iterdir()} != allowed:
            raise WO9RRefusal("exclusive derivative output already exists")
    else:
        output.mkdir(parents=True, exist_ok=False)
    fit_rows = []
    final_rows = []
    observed = []
    for record in records:
        transformed = extract_run_features(record, contract=frozen)
        observed.append((record.subject, record.run))
        if record.run in {"03", "04", "07", "08"}:
            fit_rows.append(transformed)
        else:
            final_rows.append(transformed)
    expected = [
        (subject, run)
        for subject in frozen["dataset_binding"]["participants"]
        for run in ("03", "04", "07", "08", "11", "12")
    ]
    if observed != expected:
        raise WO9RFailure("split", "participant/run order or membership mismatch")
    expected_real_hashes = {row["path"] for row in frozen["selected_files"]}
    expected_synthetic_hashes = {
        f"{subject}/{subject}R{run}.synthetic"
        for subject in frozen["dataset_binding"]["participants"]
        for run in ("03", "04", "07", "08", "11", "12")
    }
    if frozenset(source_file_hashes) not in {
        frozenset(expected_real_hashes),
        frozenset(expected_synthetic_hashes),
    }:
        raise WO9RFailure("integrity", "source hash inventory is not exact")
    if any(
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
        for value in source_file_hashes.values()
    ):
        raise WO9RFailure("integrity", "source hash inventory contains an invalid SHA-256")
    fit = _concatenate(fit_rows, include_labels=True)
    final_with_targets = _concatenate(final_rows, include_labels=True)
    if fit["features"].shape != (720, 64, 5):
        raise WO9RFailure("derivative", "fit feature shape mismatch")
    if final_with_targets["features"].shape != (360, 64, 5):
        raise WO9RFailure("derivative", "final feature shape mismatch")
    final = {key: value for key, value in final_with_targets.items() if key != "labels"}
    _validate_prediction_keys(final)
    sealed = {
        "event_ids": final_with_targets["event_ids"],
        "subjects": final_with_targets["subjects"],
        "runs": final_with_targets["runs"],
        "targets": final_with_targets["labels"].astype("int8"),
    }
    fit_path = output / FIT_DERIVATIVE_NAME
    prediction_path = output / PREDICTION_DERIVATIVE_NAME
    sealed_path = output / SEALED_TARGET_NAME
    try:
        wo9._write_npz_exclusive(fit_path, fit)
        wo9._write_npz_exclusive(prediction_path, final)
        wo9._write_npz_exclusive(sealed_path, sealed)
    except (wo9.WO9Failure, wo9.WO9Refusal) as exc:
        raise WO9RFailure("output", str(exc)) from exc
    generated = _directory_bytes(output)
    if generated > maximum_output_bytes:
        raise WO9RFailure("output", "derivatives exceed private-output cap")
    report = {
        "schema_name": "neurodecodekit.physionet_low_frequency_extraction",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_target_firewalled_compact_derivatives_created",
        "contract_sha256": CONTRACT_SHA256,
        "source_manifest_sha256": manifest_sha256,
        "source_file_hashes": dict(sorted(source_file_hashes.items())),
        "fit_derivative": {
            "path": FIT_DERIVATIVE_NAME,
            "sha256": _file_sha256(fit_path),
            "bytes": fit_path.stat().st_size,
            "rows": 720,
            "contains_targets": True,
        },
        "prediction_derivative": {
            "path": PREDICTION_DERIVATIVE_NAME,
            "sha256": _file_sha256(prediction_path),
            "bytes": prediction_path.stat().st_size,
            "rows": 360,
            "contains_targets": False,
        },
        "sealed_scorer_input": {
            "path": SEALED_TARGET_NAME,
            "sha256": _file_sha256(sealed_path),
            "bytes": sealed_path.stat().st_size,
            "rows": 360,
            "target_values_printed_or_returned": False,
        },
        "observed": {
            "files": 72,
            "task_events": 1080,
            "fit_events": 720,
            "sealed_final_events": 360,
            "channels": 64,
            "sampling_rate_hz": 160,
            "feature_shape_fit": list(fit["features"].shape),
            "feature_shape_prediction": list(final["features"].shape),
            "duplicate_event_identities": 0,
            "group_cross_partition": 0,
        },
        "causality": {
            "producer": "fourth_order_Butterworth_SOS_sosfilt_continuous_run",
            "right_context_seconds": 0.0,
            "decision_latency_seconds_from_cue": 3.0,
            "causal_claim": "cue_causal_only_not_pre_movement_or_end_to_end_realtime",
            "end_to_end_latency_measured": False,
        },
        "generated_private_bytes": generated,
        "warnings": [
            "final_annotations_were_materialized_once_by_firewalled_extraction",
            "prediction_derivative_contains_no_target_field",
            "movement_onset_EOG_and_EMG_are_unavailable",
            "visual_cue_is_class_correlated",
        ],
    }
    _write_json(output / EXTRACTION_REPORT_NAME, report)
    if _directory_bytes(output) > maximum_output_bytes:
        raise WO9RFailure("output", "extraction report exceeds cap")
    return report


def _load_npz(path: Path, *, target_free: bool = False):
    try:
        value = wo9._load_npz(path, prediction_derivative=False)
    except Exception as exc:
        raise WO9RFailure("integrity", f"cannot load derivative: {path.name}") from exc
    if target_free:
        _validate_prediction_keys(value)
    return value


class _Prior:
    def __init__(self, value: int) -> None:
        self.value = int(value)

    def predict(self, rows: Any):
        np = _np()
        return np.full(len(rows), self.value, dtype="int8")


def _flatten(values: Any, channel_indices: Any | None = None):
    np = _np()
    rows = np.asarray(values, dtype="float64")
    if channel_indices is not None:
        rows = rows[:, channel_indices, :]
    return rows.reshape(rows.shape[0], -1)


def _fit_lda(values: Any, labels: Any):
    try:
        return wo9._fit_feature_lda(values, labels)
    except Exception as exc:
        raise WO9RFailure("model", "fixed shrinkage LDA fit failed") from exc


def _prior(labels: Any) -> _Prior:
    np = _np()
    counts = np.bincount(np.asarray(labels, dtype="int8"), minlength=2)
    return _Prior(0 if counts[0] >= counts[1] else 1)


def _timing(bundle: Mapping[str, Any]):
    np = _np()
    return np.stack(
        [
            np.asarray(bundle["event_indices"], dtype="float64") / 14.0,
            np.asarray(bundle["event_onsets_seconds"], dtype="float64"),
            np.asarray(bundle["previous_intervals_seconds"], dtype="float64"),
        ],
        axis=1,
    )


def _deranged_labels(labels: Any, runs: Any, permutation: Sequence[int]):
    np = _np()
    labels = np.asarray(labels, dtype="int8")
    runs = np.asarray(runs).astype(str)
    output = labels.copy()
    for run in ("03", "07"):
        indices = np.flatnonzero(runs == run)
        if len(indices) != 15:
            raise WO9RFailure("control", "derangement requires 15 labels per fit run")
        output[indices] = labels[indices[np.asarray(permutation, dtype=int)]]
    return output


def _predict(model: Any, values: Any):
    np = _np()
    predicted = np.asarray(model.predict(values), dtype="int8")
    if predicted.shape != (15,) or not set(predicted.tolist()).issubset({0, 1}):
        raise WO9RFailure("prediction", "model did not emit 15 binary predictions")
    return predicted


def _fit_models_for_participant(
    fit: Mapping[str, Any],
    participant: str,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _np()
    subjects = np.asarray(fit["subjects"]).astype(str)
    runs = np.asarray(fit["runs"]).astype(str)
    labels = np.asarray(fit["labels"], dtype="int8")
    execution = (subjects == participant) & np.isin(runs, ["03", "07"])
    imagery = (subjects == participant) & np.isin(runs, ["04", "08"])
    if execution.sum() != 30 or imagery.sum() != 30:
        raise WO9RFailure("split", "participant fit rows are incomplete")
    channels = contract["channel_sets"]
    names = np.asarray(fit["channel_names"]).astype(str).tolist()
    central = _channel_indices(
        names,
        tuple(channels["sensorimotor_left"]) + tuple(channels["sensorimotor_right"]),
    )
    frontal = _channel_indices(names, channels["frontal_ocular_sensitive"])
    occipital = _channel_indices(names, channels["occipital_visual_sensitive"])
    asymmetry = _channel_indices(
        names,
        tuple(channels["frontal_asymmetry_left"])
        + tuple(channels["frontal_asymmetry_right"]),
    )
    permutation = contract["control_contract"]["train_label_derangement_indices"]
    deranged = _deranged_labels(labels[execution], runs[execution], permutation)
    return {
        "execution_primary": _fit_lda(
            _flatten(fit["features"][execution]), labels[execution]
        ),
        "imagery_primary": _fit_lda(_flatten(fit["features"][imagery]), labels[imagery]),
        "execution_central": _fit_lda(
            _flatten(fit["features"][execution], central), labels[execution]
        ),
        "execution_frontal": _fit_lda(
            _flatten(fit["features"][execution], frontal), labels[execution]
        ),
        "execution_occipital": _fit_lda(
            _flatten(fit["features"][execution], occipital), labels[execution]
        ),
        "execution_frontal_asymmetry": _fit_lda(
            _flatten(fit["features"][execution], asymmetry), labels[execution]
        ),
        "execution_early_cue": _fit_lda(
            _flatten(fit["early_features"][execution]), labels[execution]
        ),
        "execution_pre_cue": _fit_lda(
            _flatten(fit["pre_features"][execution]), labels[execution]
        ),
        "execution_timing_only": _fit_lda(_timing(fit)[execution], labels[execution]),
        "execution_no_signal_prior": _prior(labels[execution]),
        "imagery_no_signal_prior": _prior(labels[imagery]),
        "execution_train_label_derangement": _fit_lda(
            _flatten(fit["features"][execution]), deranged
        ),
        "channel_indices": {
            "central": central,
            "frontal": frontal,
            "occipital": occipital,
            "asymmetry": asymmetry,
        },
    }


def _participant_predictions(
    fit: Mapping[str, Any],
    final: Mapping[str, Any],
    participant: str,
    contract: Mapping[str, Any],
) -> dict[str, list[int]]:
    np = _np()
    models = _fit_models_for_participant(fit, participant, contract)
    subjects = np.asarray(final["subjects"]).astype(str)
    runs = np.asarray(final["runs"]).astype(str)
    execution = (subjects == participant) & (runs == "11")
    imagery = (subjects == participant) & (runs == "12")
    if execution.sum() != 15 or imagery.sum() != 15:
        raise WO9RFailure("split", "participant final rows are incomplete")
    x_execution = np.asarray(final["features"][execution], dtype="float64")
    x_imagery = np.asarray(final["features"][imagery], dtype="float64")
    indices = models["channel_indices"]
    channel_permutation = np.asarray(
        contract["control_contract"]["channel_derangement_indices"], dtype=int
    )
    swapped = x_execution.copy()
    names = np.asarray(final["channel_names"]).astype(str).tolist()
    for left, right in contract["channel_sets"]["hemisphere_swap_pairs"]:
        left_index = names.index(left)
        right_index = names.index(right)
        swapped[:, [left_index, right_index], :] = swapped[:, [right_index, left_index], :]
    predictions = {
        "execution_native_primary": _predict(
            models["execution_primary"], _flatten(x_execution)
        ),
        "imagery_native": _predict(models["imagery_primary"], _flatten(x_imagery)),
        "execution_to_imagery": _predict(
            models["execution_primary"], _flatten(x_imagery)
        ),
        "imagery_to_execution": _predict(
            models["imagery_primary"], _flatten(x_execution)
        ),
        "execution_central_sensorimotor": _predict(
            models["execution_central"], _flatten(x_execution, indices["central"])
        ),
        "execution_frontal_proxy": _predict(
            models["execution_frontal"], _flatten(x_execution, indices["frontal"])
        ),
        "execution_occipital_proxy": _predict(
            models["execution_occipital"], _flatten(x_execution, indices["occipital"])
        ),
        "execution_frontal_asymmetry": _predict(
            models["execution_frontal_asymmetry"],
            _flatten(x_execution, indices["asymmetry"]),
        ),
        "execution_early_cue": _predict(
            models["execution_early_cue"],
            _flatten(final["early_features"][execution]),
        ),
        "execution_pre_cue": _predict(
            models["execution_pre_cue"],
            _flatten(final["pre_features"][execution]),
        ),
        "execution_timing_only": _predict(
            models["execution_timing_only"], _timing(final)[execution]
        ),
        "execution_no_signal_prior": _predict(
            models["execution_no_signal_prior"], x_execution
        ),
        "imagery_no_signal_prior": _predict(models["imagery_no_signal_prior"], x_imagery),
        "execution_all_zero_final_signal": _predict(
            models["execution_primary"], np.zeros((15, 320), dtype="float64")
        ),
        "execution_train_label_derangement": _predict(
            models["execution_train_label_derangement"], _flatten(x_execution)
        ),
        "execution_one_trial_final_signal_displacement": _predict(
            models["execution_primary"], _flatten(np.roll(x_execution, 1, axis=0))
        ),
        "execution_channel_derangement": _predict(
            models["execution_primary"], _flatten(x_execution[:, channel_permutation, :])
        ),
        "execution_central_hemisphere_swap": _predict(
            models["execution_central"], _flatten(swapped, indices["central"])
        ),
    }
    if tuple(predictions) != CONDITION_IDS:
        raise WO9RFailure("prediction", "condition inventory or order mismatch")
    return {key: value.tolist() for key, value in predictions.items()}


def _validate_derivatives(fit: Mapping[str, Any], final: Mapping[str, Any]) -> None:
    np = _np()
    _validate_prediction_keys(final)
    if fit["features"].shape != (720, 64, 5):
        raise WO9RFailure("derivative", "fit derivative shape changed")
    if final["features"].shape != (360, 64, 5):
        raise WO9RFailure("derivative", "final derivative shape changed")
    if set(np.asarray(fit["runs"]).astype(str)) != {"03", "04", "07", "08"}:
        raise WO9RFailure("split", "fit derivative run set changed")
    if set(np.asarray(final["runs"]).astype(str)) != {"11", "12"}:
        raise WO9RFailure("split", "final derivative run set changed")
    fit_ids = np.asarray(fit["event_ids"]).astype(str).tolist()
    final_ids = np.asarray(final["event_ids"]).astype(str).tolist()
    if len(set(fit_ids)) != 720 or len(set(final_ids)) != 360:
        raise WO9RFailure("split", "event identities are not unique")
    if set(fit_ids).intersection(final_ids):
        raise WO9RFailure("split", "fit and final event identities overlap")


def run_target_blind_predictions(
    *,
    output_root: str | Path,
    freeze_path: str | Path,
    source_kind: str,
    implementation_evidence: ImplementationEvidence | None = None,
    implementation_registry: Mapping[str, Any] | None = None,
    maximum_output_bytes: int = 64 * 1024 * 1024,
    execution_started_monotonic: float | None = None,
    upstream_access_counters: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Fit 144 registered templates and freeze 216 target-blind prediction sets."""

    output = Path(output_root)
    extraction = json.loads((output / EXTRACTION_REPORT_NAME).read_text(encoding="utf-8"))
    fit_path = output / FIT_DERIVATIVE_NAME
    prediction_path = output / PREDICTION_DERIVATIVE_NAME
    if _file_sha256(fit_path) != extraction["fit_derivative"]["sha256"]:
        raise WO9RFailure("integrity", "fit derivative hash mismatch")
    if _file_sha256(prediction_path) != extraction["prediction_derivative"]["sha256"]:
        raise WO9RFailure("integrity", "prediction derivative hash mismatch")
    fit = _load_npz(fit_path)
    final = _load_npz(prediction_path, target_free=True)
    _validate_derivatives(fit, final)
    contract = load_registered_contract()
    started = time.monotonic()
    by_condition: dict[str, dict[str, list[int]]] = {key: {} for key in CONDITION_IDS}
    for participant in contract["dataset_binding"]["participants"]:
        participant_predictions = _participant_predictions(fit, final, participant, contract)
        for condition_id in CONDITION_IDS:
            by_condition[condition_id][participant] = participant_predictions[condition_id]
    prediction_sets = sum(len(rows) for rows in by_condition.values())
    inference_runs = prediction_sets
    fit_runs = 12 * len(contract["dataset_binding"]["participants"])
    if fit_runs != 144 or inference_runs != 216 or prediction_sets != 216:
        raise WO9RFailure("resource", "fit or inference inventory mismatch")
    prediction_hashes = {
        condition_id: {
            participant: wo9._prediction_set_sha256(values)
            for participant, values in participant_rows.items()
        }
        for condition_id, participant_rows in by_condition.items()
    }
    private_payload = {
        "schema_name": "neurodecodekit.physionet_low_frequency_private_predictions",
        "schema_version": SCHEMA_VERSION,
        "status": "target_blind_predictions_complete",
        "contract_sha256": CONTRACT_SHA256,
        "source_kind": source_kind,
        "event_ids": _np().asarray(final["event_ids"]).astype(str).tolist(),
        "participant_ids": _np().asarray(final["subjects"]).astype(str).tolist(),
        "run_ids": _np().asarray(final["runs"]).astype(str).tolist(),
        "predictions": by_condition,
        "operation_counters": {
            "parameter_update_fits": fit_runs,
            "target_blind_model_inference_runs": inference_runs,
            "participant_condition_prediction_sets": prediction_sets,
            "individual_predictions": 3240,
            "final_target_rows_available_to_model_stage": 0,
            "scoring_events": 0,
        },
        "sealed_target_sha256": extraction["sealed_scorer_input"]["sha256"],
        "prediction_derivative_sha256": extraction["prediction_derivative"]["sha256"],
    }
    private_payload["canonical_prediction_sha256"] = _canonical_sha256(private_payload)
    private_path = output / PRIVATE_PREDICTIONS_NAME
    private_bytes = _write_json(private_path, private_payload, 8 * 1024 * 1024)
    if json.loads(private_path.read_text(encoding="utf-8")) != private_payload:
        raise WO9RFailure("replay", "private prediction replay differs")
    runtime = time.monotonic() - started
    total_runtime = (
        time.monotonic() - execution_started_monotonic
        if execution_started_monotonic is not None
        else runtime
    )
    implementation_registry_sha256 = None
    if implementation_registry is not None:
        implementation_registry_sha256 = _file_sha256(
            _repo_root() / IMPLEMENTATION_RELATIVE_PATH
        )
    freeze = {
        "schema_name": "neurodecodekit.physionet_low_frequency_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "status": "all_run11_and_run12_predictions_frozen_targets_not_delivered",
        "proof_posture": (
            "aggregate_hash_only_real_target_blind_prediction_freeze"
            if source_kind == "real_physionet"
            else "aggregate_hash_only_generated_fixture_qualification"
        ),
        "contract_sha256": CONTRACT_SHA256,
        "authorization_decision_sha256": DECISION_SHA256,
        "implementation_commit": (
            implementation_evidence.implementation_commit
            if implementation_evidence is not None
            else None
        ),
        "implementation_ci_run_id": (
            implementation_evidence.implementation_ci_run_id
            if implementation_evidence is not None
            else None
        ),
        "implementation_base_python_job_id": (
            implementation_evidence.base_python_job_id
            if implementation_evidence is not None
            else None
        ),
        "implementation_optional_neuro_job_id": (
            implementation_evidence.optional_neuro_job_id
            if implementation_evidence is not None
            else None
        ),
        "implementation_registry_sha256": implementation_registry_sha256,
        "source_kind": source_kind,
        "source_manifest_sha256": extraction["source_manifest_sha256"],
        "source_file_count": extraction["observed"]["files"],
        "source_payload_bytes": 184252032 if source_kind == "real_physionet" else 0,
        "fit_derivative_sha256": extraction["fit_derivative"]["sha256"],
        "prediction_derivative_sha256": extraction["prediction_derivative"]["sha256"],
        "sealed_target_sha256": extraction["sealed_scorer_input"]["sha256"],
        "private_prediction_payload_sha256": _file_sha256(private_path),
        "private_prediction_payload_bytes": private_bytes,
        "condition_ids": list(CONDITION_IDS),
        "condition_count": 18,
        "participant_condition_prediction_sets": 216,
        "prediction_set_sha256": prediction_hashes,
        "configuration_sha256": _canonical_sha256(
            {
                "primary_model_template": contract["primary_model_template"],
                "causal_preprocessing": contract["causal_preprocessing"],
                "channel_sets": contract["channel_sets"],
                "control_contract": contract["control_contract"],
            }
        ),
        "split_protocol_sha256": _canonical_sha256(
            {
                "dataset_binding": contract["dataset_binding"],
                "target_firewall_and_split": contract["target_firewall_and_split"],
            }
        ),
        "dependency_versions": dependency_versions(),
        "operation_counters": {
            **dict(upstream_access_counters or {}),
            **private_payload["operation_counters"],
        },
        "resources_through_freeze": {
            "target_blind_runtime_seconds": round(runtime, 6),
            "runtime_seconds": round(total_runtime, 6),
            "peak_rss_bytes": wo9._peak_rss_bytes(),
            "generated_private_bytes": _directory_bytes(output),
            "cpu_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "target_firewall": {
            "fit_target_rows_available": 720,
            "final_signal_rows_available": 360,
            "final_target_rows_available_to_model_stage": 0,
            "prediction_derivative_contains_targets": False,
            "both_final_target_sets_frozen_together": True,
            "individual_outputs_committed": False,
        },
        "determinism_checks": {
            "private_json_roundtrip_exact": True,
            "participant_condition_hashes_complete": len(CONDITION_IDS) * 12 == 216,
            "post_fit_parameter_update_runs": 0,
        },
        "warnings": [
            "final_targets_not_delivered_until_remote_green_freeze",
            "visual_cue_is_class_correlated",
            "separate_EOG_EMG_and_movement_onset_are_unavailable",
            "end_to_end_latency_not_measured",
        ],
        "claim_boundary": {
            "current": "prediction_hashes_only_no_scientific_result",
            "maximum_after_WO9R_R4": contract["claim_boundary"][
                "maximum_scientific_claim_if_WO9R_R4"
            ],
            "not_established": contract["claim_boundary"]["not_established_even_if_WO9R_R4"],
        },
    }
    freeze["freeze_record_sha256"] = _canonical_sha256(freeze)
    freeze_output = Path(freeze_path)
    _write_json(freeze_output, freeze)
    report = {
        "schema_name": "neurodecodekit.physionet_low_frequency_target_blind_run",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_predictions_frozen_final_targets_not_delivered",
        "condition_count": 18,
        "participant_condition_prediction_sets": 216,
        "operation_counters": freeze["operation_counters"],
        "resources": freeze["resources_through_freeze"],
        "private_prediction_payload_sha256": freeze["private_prediction_payload_sha256"],
        "freeze_record_file_sha256": _file_sha256(freeze_output),
        "final_target_deliveries": 0,
        "scoring_events": 0,
        "warnings": freeze["warnings"],
    }
    _write_json(output / TARGET_BLIND_REPORT_NAME, report)
    if _directory_bytes(output) > maximum_output_bytes:
        raise WO9RFailure("output", "target-blind artifacts exceed cap")
    return report


def validate_public_freeze(freeze: Mapping[str, Any]) -> None:
    if freeze.get("schema_name") != "neurodecodekit.physionet_low_frequency_prediction_freeze":
        raise WO9RFailure("freeze", "freeze schema mismatch")
    if freeze.get("schema_version") != SCHEMA_VERSION:
        raise WO9RFailure("freeze", "freeze version mismatch")
    if freeze.get("contract_sha256") != CONTRACT_SHA256:
        raise WO9RFailure("freeze", "freeze contract binding mismatch")
    if freeze.get("authorization_decision_sha256") != DECISION_SHA256:
        raise WO9RFailure("freeze", "freeze decision binding mismatch")
    if tuple(freeze.get("condition_ids", [])) != CONDITION_IDS:
        raise WO9RFailure("freeze", "freeze condition inventory mismatch")
    if freeze.get("participant_condition_prediction_sets") != 216:
        raise WO9RFailure("freeze", "freeze prediction-set count mismatch")
    forbidden_public_fields = {"predictions", "targets", "probabilities", "participant_outcomes"}
    if forbidden_public_fields.intersection(freeze):
        raise WO9RFailure("freeze", "freeze contains an individual-output field")
    hashes = freeze.get("prediction_set_sha256")
    participants = tuple(load_registered_contract()["dataset_binding"]["participants"])
    if not isinstance(hashes, dict) or set(hashes) != set(CONDITION_IDS):
        raise WO9RFailure("freeze", "freeze prediction hash conditions mismatch")
    for condition_id in CONDITION_IDS:
        rows = hashes[condition_id]
        if not isinstance(rows, dict) or set(rows) != set(participants):
            raise WO9RFailure("freeze", "freeze participant hash inventory mismatch")
        if any(
            not isinstance(value, str)
            or len(value) != 64
            or any(character not in "0123456789abcdef" for character in value)
            for value in rows.values()
        ):
            raise WO9RFailure("freeze", "freeze contains an invalid prediction hash")
    if freeze.get("target_firewall", {}).get("final_target_rows_available_to_model_stage") != 0:
        raise WO9RFailure("freeze", "freeze reports target leakage")
    counters = freeze.get("operation_counters", {})
    expected_counters = {
        "parameter_update_fits": 144,
        "target_blind_model_inference_runs": 216,
        "participant_condition_prediction_sets": 216,
        "individual_predictions": 3240,
        "final_target_rows_available_to_model_stage": 0,
        "scoring_events": 0,
    }
    if any(counters.get(key) != value for key, value in expected_counters.items()):
        raise WO9RFailure("freeze", "freeze operation counters mismatch")
    expected = freeze.get("freeze_record_sha256")
    copy = dict(freeze)
    copy.pop("freeze_record_sha256", None)
    if expected != _canonical_sha256(copy):
        raise WO9RFailure("freeze", "freeze canonical hash mismatch")


def _balanced_accuracy(labels: Any, predictions: Any) -> float:
    try:
        return wo9.balanced_accuracy(labels, predictions)
    except wo9.WO9Failure as exc:
        raise WO9RFailure("score", str(exc)) from exc


def _sign_flip_p(values: Sequence[float]) -> float:
    observed = sum(values) / len(values)
    count = 0
    total = 1 << len(values)
    for mask in range(total):
        statistic = sum(
            value if mask & (1 << index) else -value
            for index, value in enumerate(values)
        ) / len(values)
        if statistic >= observed - 1e-15:
            count += 1
    return count / total


def _condition_metrics(
    labels: Any,
    subjects: Any,
    predictions_by_subject: Mapping[str, Sequence[int]],
) -> tuple[dict[str, Any], list[float]]:
    np = _np()
    labels = np.asarray(labels, dtype="int8")
    subjects = np.asarray(subjects).astype(str)
    predictions = []
    participant_scores = []
    correct = 0
    for participant in load_registered_contract()["dataset_binding"]["participants"]:
        mask = subjects == participant
        target = labels[mask]
        predicted = np.asarray(predictions_by_subject[participant], dtype="int8")
        if len(target) != 15 or predicted.shape != (15,):
            raise WO9RFailure("score", "participant score rows are incomplete")
        predictions.extend(predicted.tolist())
        correct += int((target == predicted).sum())
        participant_scores.append(_balanced_accuracy(target, predicted))
    pooled = _balanced_accuracy(labels, np.asarray(predictions, dtype="int8"))
    macro = float(np.mean(participant_scores))
    return (
        {
            "correct_count": correct,
            "event_count": len(labels),
            "pooled_balanced_accuracy": pooled,
            "macro_participant_balanced_accuracy": macro,
            "participants_strictly_above_chance": sum(score > 0.5 for score in participant_scores),
            "exact_one_sided_participant_sign_flip_p": _sign_flip_p(
                [score - 0.5 for score in participant_scores]
            ),
        },
        participant_scores,
    )


def _physiology_metrics(
    final: Mapping[str, Any],
    labels: Any,
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    np = _np()
    subjects = np.asarray(final["subjects"]).astype(str)
    runs = np.asarray(final["runs"]).astype(str)
    labels = np.asarray(labels, dtype="int8")
    deltas = np.asarray(final["physiology_deltas"], dtype="float64")
    names = np.asarray(final["channel_names"]).astype(str).tolist()
    left = _channel_indices(names, contract["channel_sets"]["sensorimotor_left"])
    right = _channel_indices(names, contract["channel_sets"]["sensorimotor_right"])
    participant_values = []
    for participant in contract["dataset_binding"]["participants"]:
        mask = (subjects == participant) & (runs == "11")
        rows = deltas[mask]
        target = labels[mask]
        values = []
        for row, label in zip(rows, target, strict=True):
            ipsilateral = row[left].mean() if label == 0 else row[right].mean()
            contralateral = row[right].mean() if label == 0 else row[left].mean()
            values.append(float(ipsilateral - contralateral))
        participant_values.append(float(np.mean(values)))
    direction_count = sum(value > 0.0 for value in participant_values)
    p_value = _sign_flip_p(participant_values)
    assay = contract["physiology_assay"]
    return {
        "participants_in_registered_direction": direction_count,
        "participant_count": 12,
        "exact_one_sided_sign_flip_p": p_value,
        "passed": (
            direction_count >= assay["minimum_participants_in_registered_direction"]
            and p_value <= assay["maximum_exact_one_sided_participant_sign_flip_p"]
        ),
    }


def score_private_predictions(
    *,
    freeze: Mapping[str, Any],
    private_predictions: Mapping[str, Any],
    sealed: Mapping[str, Any],
    final: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply the frozen aggregate router after one isolated target delivery."""

    np = _np()
    validate_public_freeze(freeze)
    if private_predictions.get("canonical_prediction_sha256") != _canonical_sha256(
        {key: value for key, value in private_predictions.items() if key != "canonical_prediction_sha256"}
    ):
        raise WO9RFailure("score", "private prediction canonical hash mismatch")
    event_ids = np.asarray(final["event_ids"]).astype(str)
    sealed_ids = np.asarray(sealed["event_ids"]).astype(str)
    if not np.array_equal(event_ids, sealed_ids):
        raise WO9RFailure("score", "sealed target identities do not align")
    final_subjects = np.asarray(final["subjects"]).astype(str)
    final_runs = np.asarray(final["runs"]).astype(str)
    if not np.array_equal(final_subjects, np.asarray(sealed["subjects"]).astype(str)):
        raise WO9RFailure("score", "sealed participant identities do not align")
    if not np.array_equal(final_runs, np.asarray(sealed["runs"]).astype(str)):
        raise WO9RFailure("score", "sealed run identities do not align")
    if private_predictions.get("contract_sha256") != CONTRACT_SHA256:
        raise WO9RFailure("score", "private prediction contract binding mismatch")
    if private_predictions.get("source_kind") != freeze.get("source_kind"):
        raise WO9RFailure("score", "private prediction source binding mismatch")
    if private_predictions.get("event_ids") != event_ids.tolist():
        raise WO9RFailure("score", "private event identities do not align")
    if private_predictions.get("participant_ids") != final_subjects.tolist():
        raise WO9RFailure("score", "private participant identities do not align")
    if private_predictions.get("run_ids") != final_runs.tolist():
        raise WO9RFailure("score", "private run identities do not align")
    labels = np.asarray(sealed["targets"], dtype="int8")
    sealed_subjects = np.asarray(sealed["subjects"]).astype(str)
    sealed_runs = np.asarray(sealed["runs"]).astype(str)
    if labels.shape != (360,) or set(labels.tolist()) != {0, 1}:
        raise WO9RFailure("score", "sealed target shape or values changed")
    metrics: dict[str, dict[str, Any]] = {}
    participant_scores: dict[str, list[float]] = {}
    contract = load_registered_contract()
    predictions = private_predictions["predictions"]
    participants = tuple(contract["dataset_binding"]["participants"])
    if set(predictions) != set(CONDITION_IDS):
        raise WO9RFailure("score", "private prediction condition inventory mismatch")
    for condition_id in CONDITION_IDS:
        if set(predictions[condition_id]) != set(participants):
            raise WO9RFailure("score", "private prediction participant inventory mismatch")
        for participant in participants:
            values = predictions[condition_id][participant]
            if (
                len(values) != 15
                or not set(values).issubset({0, 1})
                or wo9._prediction_set_sha256(values)
                != freeze["prediction_set_sha256"][condition_id][participant]
            ):
                raise WO9RFailure("score", "private prediction hash or values mismatch")
    private_counters = private_predictions.get("operation_counters", {})
    if any(
        private_counters.get(key) != value
        for key, value in {
            "parameter_update_fits": 144,
            "target_blind_model_inference_runs": 216,
            "participant_condition_prediction_sets": 216,
            "individual_predictions": 3240,
            "final_target_rows_available_to_model_stage": 0,
            "scoring_events": 0,
        }.items()
    ):
        raise WO9RFailure("score", "private prediction operation counters mismatch")
    for condition_id in CONDITION_IDS:
        run = "12" if condition_id in {
            "imagery_native",
            "execution_to_imagery",
            "imagery_no_signal_prior",
        } else "11"
        mask = sealed_runs == run
        metric, scores = _condition_metrics(
            labels[mask],
            sealed_subjects[mask],
            predictions[condition_id],
        )
        metrics[condition_id] = metric
        participant_scores[condition_id] = scores
    gates = contract["frozen_gates"]
    execution = metrics["execution_native_primary"]
    execution_prior = metrics["execution_no_signal_prior"]
    h1_spec = gates["H1_execution_native_cohort_confirmation"]
    h1 = all(
        (
            execution["correct_count"] >= h1_spec["minimum_correct_count"],
            execution["pooled_balanced_accuracy"]
            >= h1_spec["minimum_pooled_balanced_accuracy"],
            execution["macro_participant_balanced_accuracy"]
            >= h1_spec["minimum_macro_participant_balanced_accuracy"],
            execution["participants_strictly_above_chance"]
            >= h1_spec["minimum_participants_strictly_above_0_5_balanced_accuracy"],
            execution["exact_one_sided_participant_sign_flip_p"]
            <= h1_spec["maximum_exact_one_sided_participant_sign_flip_p"],
            execution["pooled_balanced_accuracy"]
            - execution_prior["pooled_balanced_accuracy"]
            >= h1_spec["minimum_pooled_margin_over_execution_no_signal"],
            execution["macro_participant_balanced_accuracy"]
            - execution_prior["macro_participant_balanced_accuracy"]
            >= h1_spec["minimum_macro_margin_over_execution_no_signal"],
        )
    )
    imagery = metrics["imagery_native"]
    h2_spec = gates["H2_imagery_native_task_mode_robustness"]
    h2 = all(
        (
            imagery["pooled_balanced_accuracy"] >= h2_spec["minimum_pooled_balanced_accuracy"],
            imagery["macro_participant_balanced_accuracy"]
            >= h2_spec["minimum_macro_participant_balanced_accuracy"],
            imagery["participants_strictly_above_chance"]
            >= h2_spec["minimum_participants_strictly_above_0_5_balanced_accuracy"],
            imagery["exact_one_sided_participant_sign_flip_p"]
            <= h2_spec["maximum_exact_one_sided_participant_sign_flip_p"],
        )
    )
    central = metrics["execution_central_sensorimotor"]
    proxy_ids = gates["H3_motor_compatible_localization"]["strongest_proxy_set"]
    strongest_pooled = max(metrics[key]["pooled_balanced_accuracy"] for key in proxy_ids)
    strongest_macro = max(metrics[key]["macro_participant_balanced_accuracy"] for key in proxy_ids)
    strongest_participant = max(
        (participant_scores[key] for key in proxy_ids),
        key=lambda values: sum(values),
    )
    paired_p = _sign_flip_p(
        [
            central_value - proxy_value
            for central_value, proxy_value in zip(
                participant_scores["execution_central_sensorimotor"],
                strongest_participant,
                strict=True,
            )
        ]
    )
    physiology = _physiology_metrics(final, labels, contract)
    h3_spec = gates["H3_motor_compatible_localization"]
    h3 = all(
        (
            central["pooled_balanced_accuracy"]
            >= h3_spec["minimum_central_pooled_balanced_accuracy"],
            central["macro_participant_balanced_accuracy"]
            >= h3_spec["minimum_central_macro_participant_balanced_accuracy"],
            central["pooled_balanced_accuracy"] - strongest_pooled
            >= h3_spec["minimum_central_minus_strongest_proxy_pooled_margin"],
            central["macro_participant_balanced_accuracy"] - strongest_macro
            >= h3_spec["minimum_central_minus_strongest_proxy_macro_margin"],
            paired_p <= h3_spec["maximum_exact_paired_participant_sign_flip_p"],
            physiology["passed"],
        )
    )
    control_spec = gates["mandatory_control_ceilings"]
    control_components = {}
    for condition_id in control_spec["conditions"]:
        metric = metrics[condition_id]
        control_components[condition_id] = (
            metric["pooled_balanced_accuracy"]
            <= control_spec["maximum_pooled_and_macro_balanced_accuracy"]
            and metric["macro_participant_balanced_accuracy"]
            <= control_spec["maximum_pooled_and_macro_balanced_accuracy"]
        )
    swapped = metrics["execution_central_hemisphere_swap"]
    control_components["execution_central_hemisphere_swap"] = all(
        (
            swapped["pooled_balanced_accuracy"]
            <= control_spec["central_hemisphere_swap_maximum_pooled_and_macro_balanced_accuracy"],
            swapped["macro_participant_balanced_accuracy"]
            <= control_spec["central_hemisphere_swap_maximum_pooled_and_macro_balanced_accuracy"],
            central["pooled_balanced_accuracy"] - swapped["pooled_balanced_accuracy"]
            >= control_spec["minimum_unswapped_central_minus_swapped_pooled_and_macro_margin"],
            central["macro_participant_balanced_accuracy"]
            - swapped["macro_participant_balanced_accuracy"]
            >= control_spec["minimum_unswapped_central_minus_swapped_pooled_and_macro_margin"],
        )
    )
    for condition_id in ("execution_no_signal_prior", "imagery_no_signal_prior"):
        control_components[condition_id] = all(
            math.isclose(metrics[condition_id][field], 0.5, abs_tol=1e-12)
            for field in (
                "pooled_balanced_accuracy",
                "macro_participant_balanced_accuracy",
            )
        )
    controls_passed = all(control_components.values())
    if not h1:
        verdict = "WO9R-R1"
    elif not h2:
        verdict = "WO9R-R2"
    elif not h3 or not controls_passed:
        verdict = "WO9R-R3"
    else:
        verdict = "WO9R-R4"
    return {
        "schema_name": "neurodecodekit.physionet_low_frequency_aggregate_score",
        "schema_version": SCHEMA_VERSION,
        "status": "scored_once_frozen_router_applied",
        "verdict": verdict,
        "H1_execution_native_passed": h1,
        "H2_imagery_native_passed": h2,
        "H3_motor_compatible_localization_passed": h3,
        "mandatory_controls_passed": controls_passed,
        "condition_metrics": metrics,
        "localization": {
            "central_minus_strongest_proxy_pooled_margin": (
                central["pooled_balanced_accuracy"] - strongest_pooled
            ),
            "central_minus_strongest_proxy_macro_margin": (
                central["macro_participant_balanced_accuracy"] - strongest_macro
            ),
            "exact_paired_participant_sign_flip_p": paired_p,
        },
        "physiology": physiology,
        "control_components": control_components,
        "final_target_deliveries": 1,
        "scoring_events": 1,
        "post_target_updates": 0,
        "individual_participant_metrics_published": False,
        "warnings": [
            "visual_cue_is_class_correlated",
            "separate_EOG_EMG_and_movement_onset_are_unavailable",
            "proxy_controls_do_not_establish_brain_specific_origin",
            "within_dataset_same_team_confirmation_not_independent_replication",
            "end_to_end_latency_not_measured",
        ],
        "claim_boundary": {
            "maximum": contract["claim_boundary"]["maximum_scientific_claim_if_WO9R_R4"],
            "not_established": contract["claim_boundary"]["not_established_even_if_WO9R_R4"],
        },
    }


def build_synthetic_run_record(subject: str, run: str) -> RunRecord:
    """Generate one deterministic 64-channel fixture with no public or real input."""

    np = _np()
    contract = load_registered_contract()
    if subject not in contract["dataset_binding"]["participants"]:
        raise ValueError("synthetic participant is outside WO9R")
    if run not in {"03", "04", "07", "08", "11", "12"}:
        raise ValueError("synthetic run is outside WO9R")
    channels = tuple(contract["reader_and_derivative_contract"]["standardized_channel_names"])
    onsets = np.asarray([3.0 + 4.0 * index for index in range(15)], dtype="float64")
    sample_count = int(round((onsets[-1] + 3.5) * 160))
    seed = int.from_bytes(
        hashlib.sha256(f"WO9R|{SEED}|{subject}|{run}".encode()).digest()[:8], "big"
    )
    rng = np.random.default_rng(seed)
    values = rng.normal(0.0, 0.25e-6, size=(64, sample_count)).astype("float64")
    geometry = np.zeros((64, 3), dtype="float64")
    for index in range(64):
        angle = 2.0 * math.pi * index / 64.0
        geometry[index] = [0.09 * math.cos(angle), 0.09 * math.sin(angle), 0.04]
    left = [channels.index(name) for name in contract["channel_sets"]["sensorimotor_left"]]
    right = [channels.index(name) for name in contract["channel_sets"]["sensorimotor_right"]]
    time_axis = np.arange(sample_count, dtype="float64") / 160.0
    run_offset = {"03": 0, "04": 1, "07": 1, "08": 0, "11": 0, "12": 1}[run]
    annotations = []
    for event_index, onset in enumerate(onsets):
        label = (event_index + run_offset) % 2
        annotations.append(Annotation(float(onset), "T1" if label == 0 else "T2"))
        active = (time_axis >= onset + 1.0) & (time_axis < onset + 3.0)
        wave = np.sin(2.0 * math.pi * 1.25 * (time_axis[active] - onset))
        signed = 2.2e-6 * wave * (1.0 if label == 0 else -1.0)
        values[np.ix_(left + right, np.flatnonzero(active))] += signed
        contralateral = right if label == 0 else left
        values[np.ix_(contralateral, np.flatnonzero(active))] -= 0.8e-6
    return RunRecord(
        subject=subject,
        run=run,
        sampling_rate_hz=160.0,
        channel_names=channels,
        channel_geometry_m=geometry,
        signal_volts=values,
        annotations=tuple(annotations),
    )


def run_synthetic_qualification(
    output_root: str | Path,
    *,
    maximum_output_bytes: int = 64 * 1024 * 1024,
) -> dict[str, Any]:
    """Exercise all interfaces on generated records, including isolated scoring."""

    if maximum_output_bytes <= 0 or maximum_output_bytes > 64 * 1024 * 1024:
        raise WO9RRefusal("synthetic output cap must be within 1 to 64 MiB")
    started = time.monotonic()
    contract = load_registered_contract()
    records = (
        build_synthetic_run_record(subject, run)
        for subject in contract["dataset_binding"]["participants"]
        for run in ("03", "04", "07", "08", "11", "12")
    )
    source_hashes = {
        f"{subject}/{subject}R{run}.synthetic": _sha256_bytes(
            f"WO9R|synthetic|{SEED}|{subject}|{run}".encode()
        )
        for subject in contract["dataset_binding"]["participants"]
        for run in ("03", "04", "07", "08", "11", "12")
    }
    extraction = extract_records_to_derivatives(
        records,
        output_root,
        source_file_hashes=source_hashes,
        manifest_sha256=_sha256_bytes(b"WO9R-generated-fixture-manifest-v0"),
        maximum_output_bytes=maximum_output_bytes,
    )
    output = Path(output_root)
    freeze_path = output / "synthetic_prediction_freeze.v0.json"
    report = run_target_blind_predictions(
        output_root=output,
        freeze_path=freeze_path,
        source_kind="generated_synthetic_fixture",
        maximum_output_bytes=maximum_output_bytes,
        execution_started_monotonic=started,
        upstream_access_counters={
            "synthetic_run_records": 72,
            "real_edf_hash_passes": 0,
            "real_edf_semantic_parses": 0,
        },
    )
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    private = json.loads((output / PRIVATE_PREDICTIONS_NAME).read_text(encoding="utf-8"))
    sealed = _load_npz(output / SEALED_TARGET_NAME)
    final = _load_npz(output / PREDICTION_DERIVATIVE_NAME, target_free=True)
    scored = score_private_predictions(
        freeze=freeze,
        private_predictions=private,
        sealed=sealed,
        final=final,
    )
    summary = {
        "schema_name": "neurodecodekit.physionet_low_frequency_qualification",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_only",
        "synthetic_runs": 72,
        "synthetic_events": 1080,
        "fit_rows": 720,
        "final_rows": 360,
        "parameter_update_fits": report["operation_counters"]["parameter_update_fits"],
        "target_blind_model_inference_runs": report["operation_counters"][
            "target_blind_model_inference_runs"
        ],
        "participant_condition_prediction_sets": report["operation_counters"][
            "participant_condition_prediction_sets"
        ],
        "synthetic_router_verdict": scored["verdict"],
        "runtime_seconds": round(time.monotonic() - started, 6),
        "peak_rss_bytes": wo9._peak_rss_bytes(),
        "generated_bytes": 0,
        "all_gates_passed": True,
        "real_data_reads": 0,
        "real_target_reads": 0,
        "network_bytes": 0,
        "scientific_claim_upgrade": False,
        "warnings": [
            "synthetic_fixture_is_interface_qualification_not_scientific_evidence",
            "synthetic_router_verdict_has_no_claim_value",
        ],
    }
    before_summary = _directory_bytes(output)
    for _ in range(8):
        payload = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
        total = before_summary + len(payload)
        if summary["generated_bytes"] == total:
            break
        summary["generated_bytes"] = total
    else:
        raise WO9RFailure("output", "synthetic byte measurement did not converge")
    if total > maximum_output_bytes:
        raise WO9RFailure("output", "synthetic qualification exceeds cap")
    _write_json(output / "qualification_summary.v0.json", summary)
    if _directory_bytes(output) != summary["generated_bytes"]:
        raise WO9RFailure("output", "synthetic byte measurement is not exact")
    if extraction["prediction_derivative"]["contains_targets"]:
        raise WO9RFailure("firewall", "synthetic prediction derivative leaks targets")
    return summary


def _assert_directory(path: Path) -> None:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise WO9RFailure("integrity", f"not a regular directory: {path}")


def _exact_bundle_membership(bundle: Path, expected_paths: Sequence[str]) -> dict[str, int]:
    observed = []
    directory_count = 0
    for root, directories, filenames in os.walk(bundle, followlinks=False):
        current = Path(root)
        directory_count += len(directories)
        if any((current / name).is_symlink() for name in directories):
            raise WO9RFailure("integrity", "bundle contains symlink directory")
        for filename in filenames:
            path = current / filename
            if path.is_symlink():
                raise WO9RFailure("integrity", "bundle contains symlink file")
            observed.append(path.relative_to(bundle).as_posix())
    if sorted(observed) != sorted(expected_paths):
        raise WO9RFailure("integrity", "bundle membership mismatch")
    return {"file_stats": len(observed), "directory_stats": directory_count}


def _load_mne(path: Path, subject: str, run: str) -> RunRecord:
    try:
        return wo9._load_mne_run(path, subject, run)
    except wo9.WO9Failure as exc:
        raise WO9RFailure(exc.stage, str(exc)) from exc


def _verify_manifest(path: Path, contract: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise WO9RFailure("integrity", "acquisition manifest is not regular")
    payload = path.read_bytes()
    manifest = json.loads(payload)
    if manifest.get("schema_name") != "neurodecodekit.physionet_low_frequency_acquisition_manifest":
        raise WO9RFailure("integrity", "acquisition manifest schema mismatch")
    if manifest.get("status") != "passed":
        raise WO9RFailure("integrity", "acquisition manifest is not passed")
    expected = {
        row["path"]: (row["size_bytes"], row["sha256"], row["sha256"], 1)
        for row in contract["selected_files"]
    }
    actual = {
        row["path"]: (
            row["size_bytes"],
            row["official_sha256"],
            row["observed_local_sha256"],
            row["local_hash_passes"],
        )
        for row in manifest.get("file_records", [])
    }
    if actual != expected:
        raise WO9RFailure("integrity", "acquisition manifest identity mismatch")
    return manifest, _sha256_bytes(payload)


def run_registered_prediction_execution(
    *,
    repo_root: str | Path,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Consume the one real target-blind analysis through aggregate freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    implementation = acquisition._validate_implementation_registry(root, evidence)
    bundle = root / BUNDLE_RELATIVE_PATH
    manifest_path = root / ACQUISITION_MANIFEST_RELATIVE_PATH
    output = root / EXECUTION_ROOT_RELATIVE_PATH
    freeze_path = root / FREEZE_RELATIVE_PATH
    for path in (output, freeze_path):
        acquisition._assert_safe_path_chain(root, path)
    if output.exists() or output.is_symlink() or freeze_path.exists() or freeze_path.is_symlink():
        raise WO9RRefusal("execution output or public freeze already exists")
    started = time.monotonic()
    output.mkdir(parents=True, exist_ok=False)
    _write_json(
        output / EXECUTION_CONSUMED_NAME,
        {
            "schema_name": "neurodecodekit.physionet_low_frequency_execution_consumed",
            "schema_version": SCHEMA_VERSION,
            "retry_allowed": False,
            "rerun_allowed": False,
        },
        64 * 1024,
    )
    for path in (bundle, manifest_path):
        acquisition._assert_safe_path_chain(root, path)
    _assert_directory(bundle)
    expected_paths = [row["path"] for row in contract["selected_files"]]
    membership = _exact_bundle_membership(bundle, expected_paths)
    _, manifest_sha256 = _verify_manifest(manifest_path, contract)
    source_hashes: dict[str, str] = {}
    caps = contract["resource_caps"]["analysis_and_scoring"]

    def records():
        for row in contract["selected_files"]:
            path = bundle / acquisition._safe_relative_path(row["path"])
            size, digest = acquisition._hash_regular_nofollow(path)
            if size != row["size_bytes"] or digest != row["sha256"]:
                raise WO9RFailure("integrity", f"EDF mismatch: {row['path']}")
            source_hashes[row["path"]] = digest
            record = _load_mne(path, row["subject"], row["run"])
            if time.monotonic() - started > caps["wall_time_seconds_through_prediction_freeze"]:
                raise WO9RFailure("resource", "analysis wall cap exceeded")
            if wo9._peak_rss_bytes() > caps["peak_rss_bytes"]:
                raise WO9RFailure("resource", "analysis RSS cap exceeded")
            yield record
            if time.monotonic() - started > caps["wall_time_seconds_through_prediction_freeze"]:
                raise WO9RFailure("resource", "analysis wall cap exceeded")
            if wo9._peak_rss_bytes() > caps["peak_rss_bytes"]:
                raise WO9RFailure("resource", "analysis RSS cap exceeded")

    extract_records_to_derivatives(
        records(),
        output,
        source_file_hashes=source_hashes,
        manifest_sha256=manifest_sha256,
        maximum_output_bytes=64 * 1024 * 1024,
        contract=contract,
        allow_existing_consumed_marker=True,
    )
    report = run_target_blind_predictions(
        output_root=output,
        freeze_path=freeze_path,
        source_kind="real_physionet",
        implementation_evidence=evidence,
        implementation_registry=implementation,
        maximum_output_bytes=64 * 1024 * 1024,
        execution_started_monotonic=started,
        upstream_access_counters={
            "acquisition_manifest_reads": 1,
            "bundle_root_stats": 1,
            "bundle_membership_file_stats": membership["file_stats"],
            "bundle_membership_directory_stats": membership["directory_stats"],
            "real_edf_hash_passes": 72,
            "real_edf_semantic_parses": 72,
            "real_header_reads": 72,
            "real_annotation_reads": 72,
            "real_signal_reads": 72,
            "firewalled_target_rows_materialized": 360,
        },
    )
    runtime = time.monotonic() - started
    if runtime > caps["wall_time_seconds_through_prediction_freeze"]:
        raise WO9RFailure("resource", "analysis wall cap exceeded")
    if wo9._peak_rss_bytes() > caps["peak_rss_bytes"]:
        raise WO9RFailure("resource", "analysis RSS cap exceeded")
    if _directory_bytes(output) > caps["private_generated_bytes"]:
        raise WO9RFailure("resource", "private output cap exceeded")
    return {
        **report,
        "runtime_seconds": round(runtime, 6),
        "peak_rss_bytes": wo9._peak_rss_bytes(),
        "generated_private_bytes": _directory_bytes(output),
        "input_payload_bytes": 184252032,
        "end_to_end_latency_measured": False,
    }


def _git_head(root: Path) -> str:
    return subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def score_registered_execution(
    *,
    repo_root: str | Path,
    evidence: FreezeEvidence,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Deliver the same combined final targets once after remote-green freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    if _git_head(root) != evidence.freeze_commit:
        raise WO9RRefusal("current HEAD differs from freeze evidence")
    if min(
        evidence.freeze_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise WO9RRefusal("positive freeze CI identifiers are required")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise WO9RRefusal("green authorization decision is not a freeze ancestor")
    if subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=no"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip():
        raise WO9RRefusal("tracked worktree must be clean before scoring")
    output = root / EXECUTION_ROOT_RELATIVE_PATH
    freeze_path = root / FREEZE_RELATIVE_PATH
    result_path = root / RESULT_RELATIVE_PATH
    consumed_path = output / SCORING_CONSUMED_NAME
    if consumed_path.exists() or result_path.exists() or result_path.is_symlink():
        raise WO9RRefusal("WO9R score is already consumed")
    if subprocess.run(
        ("git", "cat-file", "-e", f"HEAD:{FREEZE_RELATIVE_PATH}"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise WO9RRefusal("public freeze is not tracked at HEAD")
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    validate_public_freeze(freeze)
    if freeze.get("source_kind") != "real_physionet":
        raise WO9RRefusal("only the real PhysioNet freeze may be scored")
    implementation_commit = freeze.get("implementation_commit")
    if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
        raise WO9RRefusal("freeze implementation commit binding is unavailable")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", implementation_commit, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise WO9RRefusal("freeze implementation commit is not an ancestor")
    private_path = output / PRIVATE_PREDICTIONS_NAME
    sealed_path = output / SEALED_TARGET_NAME
    final_path = output / PREDICTION_DERIVATIVE_NAME
    _write_json(
        consumed_path,
        {
            "schema_name": "neurodecodekit.physionet_low_frequency_score_consumed",
            "schema_version": SCHEMA_VERSION,
            "freeze_commit": evidence.freeze_commit,
            "retry_allowed": False,
            "rerun_allowed": False,
        },
        64 * 1024,
    )
    if _file_sha256(private_path) != freeze["private_prediction_payload_sha256"]:
        raise WO9RFailure("integrity", "private predictions hash mismatch")
    if _file_sha256(sealed_path) != freeze["sealed_target_sha256"]:
        raise WO9RFailure("integrity", "sealed targets hash mismatch")
    if _file_sha256(final_path) != freeze["prediction_derivative_sha256"]:
        raise WO9RFailure("integrity", "final derivative hash mismatch")
    private = json.loads(private_path.read_text(encoding="utf-8"))
    sealed = _load_npz(sealed_path)
    final = _load_npz(final_path, target_free=True)
    result = score_private_predictions(
        freeze=freeze,
        private_predictions=private,
        sealed=sealed,
        final=final,
    )
    result["freeze_commit"] = evidence.freeze_commit
    result["freeze_ci_run_id"] = evidence.freeze_ci_run_id
    result["base_python_job_id"] = evidence.base_python_job_id
    result["optional_neuro_job_id"] = evidence.optional_neuro_job_id
    result["input_payload_bytes"] = 184252032
    result["public_result_bytes"] = 0
    for _ in range(8):
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if result["public_result_bytes"] == len(payload):
            break
        result["public_result_bytes"] = len(payload)
    else:
        raise WO9RFailure("output", "result byte measurement did not converge")
    if len(payload) > contract["resource_caps"]["analysis_and_scoring"][
        "public_freeze_and_result_bytes"
    ]:
        raise WO9RFailure("output", "public result exceeds cap")
    _write_json(result_path, result, 2 * 1024 * 1024)
    return result


def remove_synthetic_qualification(path: str | Path) -> None:
    """Remove only a caller-named generated qualification directory."""

    candidate = Path(path)
    if candidate.exists() and not candidate.is_symlink():
        shutil.rmtree(candidate)
