"""Bounded Work Order 9 public motor-task EEG positive control.

Heavy numerical and EEG dependencies are imported only inside the functions
that need them. The default plan reads only committed governance artifacts and
does not stat the registered PhysioNet bundle.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import os
import resource
import shutil
import stat
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/physionet_motor_positive_control_contract.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/physionet_motor_positive_control_authorization_decision.v0.json"
)
IMPLEMENTATION_RELATIVE_PATH = Path(
    "registries/physionet_motor_positive_control_implementation.v0.json"
)
ACQUISITION_MANIFEST_RELATIVE_PATH = Path(
    ".codex_work/physionet_motor_acquisition/receipt/"
    "physionet_motor_acquisition_manifest.v0.json"
)
BUNDLE_RELATIVE_PATH = Path("data/physionet_motor/eegmmidb-1.0.0")
EXECUTION_ROOT_RELATIVE_PATH = Path(
    ".codex_work/physionet_motor_positive_control/execution"
)
FREEZE_RELATIVE_PATH = Path(
    "registries/physionet_motor_positive_control_prediction_freeze.v0.json"
)
RESULT_RELATIVE_PATH = Path(
    "registries/physionet_motor_positive_control_result.v0.json"
)
CONTRACT_SHA256 = "4f00f8e2cb257e912a947b49268c1476554f3e671eb9322926592df4908b144e"
DECISION_SHA256 = "33c066ecc54953d7ec5fb17da894856a7622e66c1aadd4a5b709c79429e0a246"
DECISION_COMMIT = "da9399c4290fc2be81834ed1036a6bede5f52154"
DECISION_CI_RUN_ID = 31348287824
DECISION_BASE_JOB_ID = 93334251403
DECISION_OPTIONAL_JOB_ID = 93334251379
ACQUISITION_MANIFEST_SHA256 = (
    "5ebe954a07ced8c2d0c549af0e22c5246ff563613d56cd5e0d0b91fb305d3902"
)
MAX_LOCKED_JSON_BYTES = 1024 * 1024
CHUNK_BYTES = 1024 * 1024
SEED = 5509
CONDITION_IDS = (
    "selected_full_head_primary",
    "low_frequency_shrinkage_lda_comparator",
    "train_only_no_signal_prior",
    "all_zero_final_signal",
    "pre_cue_model",
    "event_index_and_timing_only_model",
    "fixed_train_label_derangement",
    "fixed_one_trial_final_signal_displacement",
    "fixed_validation_channel_derangement",
    "fixed_left_right_hemisphere_swap",
    "frontal_occipital_proxy_channel_model",
    "central_sensorimotor_channel_model",
)
THREAD_ENV_KEYS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
REGISTERED_CHANNEL_NAMES = (
    "FC5",
    "FC3",
    "FC1",
    "FCz",
    "FC2",
    "FC4",
    "FC6",
    "C5",
    "C3",
    "C1",
    "Cz",
    "C2",
    "C4",
    "C6",
    "CP5",
    "CP3",
    "CP1",
    "CPz",
    "CP2",
    "CP4",
    "CP6",
    "Fp1",
    "Fpz",
    "Fp2",
    "AF7",
    "AF3",
    "AFz",
    "AF4",
    "AF8",
    "F7",
    "F5",
    "F3",
    "F1",
    "Fz",
    "F2",
    "F4",
    "F6",
    "F8",
    "FT7",
    "FT8",
    "T7",
    "T8",
    "T9",
    "T10",
    "TP7",
    "TP8",
    "P7",
    "P5",
    "P3",
    "P1",
    "Pz",
    "P2",
    "P4",
    "P6",
    "P8",
    "PO7",
    "PO3",
    "POz",
    "PO4",
    "PO8",
    "O1",
    "Oz",
    "O2",
    "Iz",
)
FIT_DERIVATIVE_NAME = "fit_derivative.v0.npz"
PREDICTION_DERIVATIVE_NAME = "prediction_derivative.v0.npz"
SEALED_TARGET_NAME = "sealed_run11_targets.v0.npz"
EXTRACTION_REPORT_NAME = "extraction_report.v0.json"
PRIVATE_PREDICTIONS_NAME = "private_predictions.v0.json"
TARGET_BLIND_REPORT_NAME = "target_blind_report.v0.json"
EXECUTION_CONSUMED_NAME = "execution_consumed.v0.json"
SCORING_CONSUMED_NAME = "scoring_consumed.v0.json"


class WO9Refusal(RuntimeError):
    """A gate failed before the one registered evidence operation began."""


class WO9Failure(RuntimeError):
    """The one registered operation was consumed and parked."""

    def __init__(self, stage: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage


@dataclass(frozen=True)
class ImplementationEvidence:
    """Remote-green implementation proof supplied to the real executor."""

    implementation_commit: str
    implementation_ci_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True)
class FreezeEvidence:
    """Remote-green prediction-freeze proof supplied to the isolated scorer."""

    freeze_commit: str
    freeze_ci_run_id: int
    base_python_job_id: int
    optional_neuro_job_id: int


@dataclass(frozen=True)
class Annotation:
    onset_seconds: float
    description: str


@dataclass(frozen=True)
class RunRecord:
    """One normalized EEG run supplied by MNE or a generated fixture."""

    subject: str
    run: str
    sampling_rate_hz: float
    channel_names: tuple[str, ...]
    channel_geometry_m: Any
    signal_volts: Any
    annotations: tuple[Annotation, ...]


@dataclass(frozen=True)
class ExtractionOutcome:
    report: dict[str, Any]
    fit_path: Path
    prediction_path: Path
    sealed_target_path: Path


RawLoader = Callable[[Path, str, str], RunRecord]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: Mapping[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_sha256(value: Mapping[str, Any]) -> str:
    return _sha256_bytes(_canonical_json_bytes(value))


def _prediction_set_sha256(values: Sequence[Any]) -> str:
    normalized = []
    for value in values:
        integer = int(value)
        if integer not in {0, 1} or value != integer:
            raise WO9Failure("prediction", "prediction sets must contain only binary values")
        normalized.append(integer)
    return _sha256_bytes(json.dumps(normalized, separators=(",", ":")).encode("utf-8"))


def _load_locked_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    with path.open("rb") as handle:
        payload = handle.read(MAX_LOCKED_JSON_BYTES + 1)
    if len(payload) > MAX_LOCKED_JSON_BYTES:
        raise WO9Refusal(f"locked JSON exceeds 1 MiB: {path}")
    observed = _sha256_bytes(payload)
    if observed != expected_sha256:
        raise WO9Refusal(
            f"locked JSON SHA-256 mismatch for {path}: expected {expected_sha256}, "
            f"got {observed}"
        )
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise WO9Refusal(f"locked JSON must contain an object: {path}")
    return value


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    contract = _load_locked_json(root / CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if contract.get("schema_name") != (
        "neurodecodekit.physionet_motor_positive_control_contract"
    ):
        raise WO9Refusal("Work Order 9 contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise WO9Refusal("Work Order 9 contract version mismatch")
    if contract.get("status") != (
        "preregistered_tier_c_not_authorized_not_implemented_not_executed"
    ):
        raise WO9Refusal("Work Order 9 contract status mismatch")
    if tuple(contract["mandatory_final_prediction_sets"]) != CONDITION_IDS:
        raise WO9Refusal("Work Order 9 prediction-set inventory mismatch")
    return contract


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root) if repo_root is not None else _repo_root()
    decision = _load_locked_json(root / DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision.get("schema_name") != (
        "neurodecodekit.physionet_motor_positive_control_authorization_decision"
    ):
        raise WO9Refusal("Work Order 9 decision schema mismatch")
    if decision.get("authorized_contract", {}).get("sha256") != CONTRACT_SHA256:
        raise WO9Refusal("Work Order 9 decision does not bind the frozen contract")
    if decision.get("green_request", {}).get("both_required_jobs_green") is not True:
        raise WO9Refusal("Work Order 9 decision lacks green request proof")
    return decision


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the frozen plan without statting any local data or private receipt."""

    contract = load_registered_contract(repo_root)
    decision = load_registered_decision(repo_root)
    caps = contract["resource_caps"]
    return {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_local_physionet_stat_open_hash_or_parse",
        "decision_commit": DECISION_COMMIT,
        "decision_ci_run_id": DECISION_CI_RUN_ID,
        "decision_green": decision["green_request"]["both_required_jobs_green"],
        "subjects": contract["dataset_binding"]["subjects"],
        "fit_and_selection_runs": contract["dataset_binding"][
            "fit_and_selection_runs"
        ],
        "sealed_final_run": contract["dataset_binding"]["sealed_final_run"],
        "file_count": contract["dataset_binding"]["file_count"],
        "payload_bytes": contract["dataset_binding"]["payload_bytes"],
        "expected_task_events": contract["required_real_observations"][
            "task_events_total"
        ],
        "prediction_set_count": len(CONDITION_IDS),
        "maximum_fits": caps["maximum_classical_parameter_update_fits"],
        "maximum_prediction_sets": caps["maximum_prediction_sets"],
        "registered_executions": caps["registered_executions"],
        "retries": caps["retries"],
        "reruns": caps["reruns"],
        "next_gate": "exact_fixture_qualified_implementation_must_be_remotely_green",
        "claim_ceiling": contract["claim_boundary"][
            "maximum_scientific_claim_if_future_WO9_V3"
        ],
    }


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Work Order 9 arrays require the optional classical dependencies. "
            "Install with: pip install -e '.[classical]'"
        ) from exc
    return np


def _require_scipy_signal():
    try:
        from scipy import signal
    except ImportError as exc:
        raise RuntimeError(
            "Work Order 9 causal filters require the optional classical dependencies. "
            "Install with: pip install -e '.[classical]'"
        ) from exc
    return signal


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def _git_head(repo_root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _path_tracked_at_head(repo_root: Path, path: Path) -> bool:
    try:
        relative = path.relative_to(repo_root).as_posix()
    except ValueError:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"HEAD:{relative}"],
        cwd=repo_root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    mismatches = {key: environ.get(key) for key in THREAD_ENV_KEYS if environ.get(key) != "1"}
    if mismatches:
        raise WO9Refusal(f"one-thread environment is not exact: {mismatches}")


def _safe_relative_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        raise WO9Refusal(f"unsafe registered relative path: {value!r}")
    return path


def _open_nofollow(path: Path):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise WO9Failure("integrity", f"cannot open registered regular file: {path}") from exc
    return os.fdopen(descriptor, "rb")


def _lstat_regular(path: Path) -> os.stat_result:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise WO9Failure("integrity", f"registered path is unavailable: {path}") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise WO9Failure("integrity", f"registered path is not a regular non-symlink: {path}")
    return observed


def _read_and_hash_nofollow(path: Path, maximum_bytes: int | None = None) -> tuple[bytes, str]:
    _lstat_regular(path)
    digest = hashlib.sha256()
    chunks: list[bytes] = []
    total = 0
    with _open_nofollow(path) as handle:
        while True:
            chunk = handle.read(CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            if maximum_bytes is not None and total > maximum_bytes:
                raise WO9Failure("integrity", f"registered file exceeds cap: {path}")
            chunks.append(chunk)
            digest.update(chunk)
    return b"".join(chunks), digest.hexdigest()


def _hash_registered_edf(path: Path, expected_size: int, expected_sha256: str) -> str:
    observed = _lstat_regular(path)
    if int(observed.st_size) != int(expected_size):
        raise WO9Failure("integrity", f"EDF size mismatch: {path.name}")
    digest = hashlib.sha256()
    total = 0
    with _open_nofollow(path) as handle:
        while True:
            chunk = handle.read(CHUNK_BYTES)
            if not chunk:
                break
            total += len(chunk)
            digest.update(chunk)
    observed_sha256 = digest.hexdigest()
    if total != expected_size or observed_sha256 != expected_sha256:
        raise WO9Failure("integrity", f"EDF SHA-256 mismatch: {path.name}")
    return observed_sha256


def _verify_private_acquisition_manifest(path: Path, contract: Mapping[str, Any]) -> dict[str, Any]:
    payload, observed_sha256 = _read_and_hash_nofollow(path, MAX_LOCKED_JSON_BYTES)
    if observed_sha256 != ACQUISITION_MANIFEST_SHA256:
        raise WO9Failure("integrity", "private acquisition manifest SHA-256 mismatch")
    manifest = json.loads(payload.decode("utf-8"))
    if manifest.get("schema_name") != "neurodecodekit.physionet_motor_acquisition_manifest":
        raise WO9Failure("integrity", "private acquisition manifest schema mismatch")
    if manifest.get("status") != "passed":
        raise WO9Failure("integrity", "private acquisition manifest is not passed")
    rows = manifest.get("file_paths_sizes_official_and_observed_sha256")
    if not isinstance(rows, list) or len(rows) != 9:
        raise WO9Failure("integrity", "private acquisition manifest membership mismatch")
    observed_rows = {
        row.get("path"): (
            row.get("size_bytes"),
            row.get("official_sha256"),
            row.get("observed_local_sha256"),
            row.get("hash_pass_count"),
        )
        for row in rows
    }
    expected_rows = {
        row["path"]: (row["size_bytes"], row["sha256"], row["sha256"], 1)
        for row in contract["selected_files"]
    }
    if observed_rows != expected_rows:
        raise WO9Failure("integrity", "private acquisition manifest file identities mismatch")
    return manifest


def _load_mne_run(path: Path, subject: str, run: str) -> RunRecord:
    """Make the one authorized MNE parse and normalize one EDF run."""

    try:
        import mne
        from mne.datasets import eegbci
    except ImportError as exc:
        raise RuntimeError(
            "Work Order 9 EDF parsing requires MNE 1.12.x. "
            "Install with: pip install -e '.[classical]'"
        ) from exc
    if not str(mne.__version__).startswith("1.12."):
        raise WO9Failure("dependency", f"MNE version is not 1.12.x: {mne.__version__}")
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_edf(str(path), preload=True, verbose="ERROR")
    try:
        eegbci.standardize(raw)
        if tuple(raw.get_channel_types()) != ("eeg",) * len(raw.ch_names):
            raise WO9Failure("header", "EDF contains a non-EEG source channel")
        montage = mne.channels.make_standard_montage("standard_1005")
        raw.set_montage(montage, on_missing="raise", verbose="ERROR")
        positions = raw.get_montage().get_positions()["ch_pos"]
        np = _require_numpy()
        geometry = np.asarray([positions[name] for name in raw.ch_names], dtype="float64")
        annotations = tuple(
            Annotation(float(onset), str(description))
            for onset, description in zip(
                raw.annotations.onset,
                raw.annotations.description,
                strict=True,
            )
        )
        signal_volts = raw.get_data().astype("float64", copy=False)
        return RunRecord(
            subject=subject,
            run=run,
            sampling_rate_hz=float(raw.info["sfreq"]),
            channel_names=tuple(raw.ch_names),
            channel_geometry_m=geometry,
            signal_volts=np.ascontiguousarray(signal_volts),
            annotations=annotations,
        )
    finally:
        raw.close()


def _butter_sos(low_hz: float, high_hz: float, sampling_rate_hz: float):
    signal = _require_scipy_signal()
    return signal.butter(
        4,
        [float(low_hz), float(high_hz)],
        btype="bandpass",
        fs=float(sampling_rate_hz),
        output="sos",
    )


def _causal_filter(values: Any, low_hz: float, high_hz: float, sampling_rate_hz: float):
    signal = _require_scipy_signal()
    return signal.sosfilt(
        _butter_sos(low_hz, high_hz, sampling_rate_hz),
        values,
        axis=-1,
    )


def _window(values: Any, onset_seconds: float, start_seconds: float, stop_seconds: float):
    np = _require_numpy()
    sampling_rate_hz = 160
    start = int(round((onset_seconds + start_seconds) * sampling_rate_hz))
    stop = int(round((onset_seconds + stop_seconds) * sampling_rate_hz))
    if start < 0 or stop > values.shape[-1] or stop <= start:
        raise WO9Failure("event_window", "registered event window is out of bounds")
    return np.ascontiguousarray(values[:, start:stop], dtype="float32")


def _low_frequency_features(epoch: Any):
    np = _require_numpy()
    if epoch.shape[-1] != 320:
        raise WO9Failure("feature", "low-frequency epoch must contain 320 samples")
    bins = epoch.reshape(epoch.shape[0], 4, 80).mean(axis=-1)
    time_axis = np.linspace(-1.0, 1.0, epoch.shape[-1], dtype="float64")
    denominator = float(np.dot(time_axis, time_axis))
    slopes = np.asarray(epoch, dtype="float64") @ time_axis / denominator
    return np.ascontiguousarray(
        np.concatenate([bins, slopes[:, None]], axis=1).reshape(-1),
        dtype="float32",
    )


def _physiology_log_power(
    mu_values: Any,
    beta_values: Any,
    onset_seconds: float,
):
    np = _require_numpy()
    rows = []
    tiny = np.finfo("float64").tiny
    for band in (mu_values, beta_values):
        baseline = _window(band, onset_seconds, -1.0, 0.0).astype("float64")
        active = _window(band, onset_seconds, 1.0, 3.0).astype("float64")
        rows.append(
            np.stack(
                [
                    np.log(np.mean(baseline * baseline, axis=-1) + tiny),
                    np.log(np.mean(active * active, axis=-1) + tiny),
                ],
                axis=0,
            )
        )
    return np.ascontiguousarray(np.stack(rows, axis=0), dtype="float32")


def extract_run_features(record: RunRecord) -> dict[str, Any]:
    """Validate and transform one normalized run without excluding any event."""

    np = _require_numpy()
    if record.subject not in {"S001", "S002", "S003"}:
        raise WO9Failure("identity", "unexpected participant identity")
    if record.run not in {"03", "07", "11"}:
        raise WO9Failure("identity", "unexpected run identity")
    if not math.isclose(record.sampling_rate_hz, 160.0, rel_tol=0.0, abs_tol=1e-9):
        raise WO9Failure("header", "sampling rate is not exactly 160 Hz")
    if record.channel_names != REGISTERED_CHANNEL_NAMES:
        raise WO9Failure("header", "standardized 64-channel identity/order mismatch")
    values = np.asarray(record.signal_volts, dtype="float64")
    geometry = np.asarray(record.channel_geometry_m, dtype="float64")
    if values.ndim != 2 or values.shape[0] != 64:
        raise WO9Failure("header", "signal shape does not contain all 64 EEG channels")
    if geometry.shape != (64, 3) or not np.isfinite(geometry).all():
        raise WO9Failure("geometry", "registered 64-channel geometry is unavailable")
    if not np.isfinite(values).all():
        raise WO9Failure("signal", "signal contains a nonfinite sample")
    if values.shape[-1] < 1:
        raise WO9Failure("signal", "signal has no samples")
    annotations = sorted(record.annotations, key=lambda row: row.onset_seconds)
    if tuple(annotations) != record.annotations:
        raise WO9Failure("annotation", "annotations are not monotone")
    if any(row.description not in {"T0", "T1", "T2"} for row in annotations):
        raise WO9Failure("annotation", "annotation description is outside T0/T1/T2")
    task = [row for row in annotations if row.description in {"T1", "T2"}]
    if len(task) != 15:
        raise WO9Failure("annotation", "run does not contain exactly 15 task events")
    if len({row.onset_seconds for row in task}) != 15:
        raise WO9Failure("annotation", "task event onsets are not unique")

    referenced = values - values.mean(axis=0, keepdims=True)
    motor = _causal_filter(referenced, 8.0, 30.0, 160.0)
    low = _causal_filter(referenced, 0.5, 4.0, 160.0)
    mu = _causal_filter(referenced, 8.0, 13.0, 160.0)
    beta = _causal_filter(referenced, 13.0, 30.0, 160.0)
    primary_rows = []
    pre_cue_rows = []
    low_rows = []
    physiology_rows = []
    labels = []
    event_ids = []
    onsets = []
    for event_index, annotation in enumerate(task):
        primary_rows.append(_window(motor, annotation.onset_seconds, 1.0, 3.0))
        pre_cue_rows.append(_window(motor, annotation.onset_seconds, -2.0, 0.0))
        low_rows.append(
            _low_frequency_features(_window(low, annotation.onset_seconds, 1.0, 3.0))
        )
        physiology_rows.append(_physiology_log_power(mu, beta, annotation.onset_seconds))
        labels.append(0 if annotation.description == "T1" else 1)
        event_ids.append(f"{record.subject}-{record.run}-E{event_index:02d}")
        onsets.append(annotation.onset_seconds)
    return {
        "primary": np.stack(primary_rows, axis=0),
        "pre_cue": np.stack(pre_cue_rows, axis=0),
        "low_frequency_features": np.stack(low_rows, axis=0),
        "physiology_log_power": np.stack(physiology_rows, axis=0),
        "labels": np.asarray(labels, dtype="int8"),
        "event_ids": np.asarray(event_ids),
        "subjects": np.asarray([record.subject] * 15),
        "runs": np.asarray([record.run] * 15),
        "event_indices": np.arange(15, dtype="int16"),
        "event_onsets_seconds": np.asarray(onsets, dtype="float64"),
        "channel_names": np.asarray(record.channel_names),
        "channel_geometry_m": np.ascontiguousarray(geometry, dtype="float64"),
    }


def _concatenate_rows(rows: Sequence[Mapping[str, Any]], *, include_labels: bool) -> dict[str, Any]:
    np = _require_numpy()
    if not rows:
        raise WO9Failure("derivative", "derivative partition is empty")
    event_keys = (
        "primary",
        "pre_cue",
        "low_frequency_features",
        "physiology_log_power",
        "event_ids",
        "subjects",
        "runs",
        "event_indices",
        "event_onsets_seconds",
    )
    combined = {key: np.concatenate([row[key] for row in rows], axis=0) for key in event_keys}
    if include_labels:
        combined["labels"] = np.concatenate([row["labels"] for row in rows], axis=0)
    combined["channel_names"] = rows[0]["channel_names"]
    combined["channel_geometry_m"] = rows[0]["channel_geometry_m"]
    for row in rows[1:]:
        if not np.array_equal(row["channel_names"], combined["channel_names"]):
            raise WO9Failure("geometry", "channel names differ across runs")
        if not np.allclose(
            row["channel_geometry_m"],
            combined["channel_geometry_m"],
            rtol=0.0,
            atol=1e-12,
        ):
            raise WO9Failure("geometry", "channel geometry differs across runs")
    return combined


def _write_npz_exclusive(path: Path, arrays: Mapping[str, Any]) -> None:
    np = _require_numpy()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            np.savez_compressed(handle, **arrays)
    except FileExistsError:
        raise WO9Refusal(f"refusing to replace private derivative: {path}") from None


def _write_json_exclusive(path: Path, value: Mapping[str, Any], maximum_bytes: int) -> int:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > maximum_bytes:
        raise WO9Failure("output", f"JSON output exceeds cap: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise WO9Refusal(f"refusing to replace output: {path}") from None
    return len(payload)


def _directory_bytes(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path, followlinks=False):
        for filename in files:
            candidate = Path(root) / filename
            if candidate.is_symlink():
                raise WO9Failure("output", "generated output contains a symlink")
            total += candidate.stat().st_size
    return total


def _validate_prediction_derivative_keys(keys: Iterable[str]) -> None:
    forbidden = ("label", "target", "reference", "intended", "outcome")
    for key in keys:
        lowered = key.lower()
        if any(fragment in lowered for fragment in forbidden):
            raise WO9Failure("firewall", f"prediction derivative contains forbidden key: {key}")


def _load_npz(path: Path, *, prediction_derivative: bool = False) -> dict[str, Any]:
    np = _require_numpy()
    with np.load(path, allow_pickle=False) as archive:
        keys = tuple(archive.files)
        if prediction_derivative:
            _validate_prediction_derivative_keys(keys)
        return {key: np.array(archive[key], copy=True) for key in keys}


def extract_records_to_derivatives(
    records: Iterable[RunRecord],
    output_root: str | Path,
    *,
    source_file_hashes: Mapping[str, str],
    manifest_sha256: str,
    maximum_output_bytes: int = 64 * 1024 * 1024,
) -> ExtractionOutcome:
    """Create strict fit, target-blind prediction, and sealed-target derivatives."""

    np = _require_numpy()
    output = Path(output_root)
    output.mkdir(parents=True, exist_ok=True)
    fit_rows = []
    prediction_rows = []
    observed_identities = []
    for record in records:
        features = extract_run_features(record)
        observed_identities.append((record.subject, record.run))
        if record.run in {"03", "07"}:
            fit_rows.append(features)
        elif record.run == "11":
            prediction_rows.append(features)
    expected_identities = [
        (subject, run)
        for subject in ("S001", "S002", "S003")
        for run in ("03", "07", "11")
    ]
    if observed_identities != expected_identities:
        raise WO9Failure("split", "record order or exact participant-run membership mismatch")
    fit = _concatenate_rows(fit_rows, include_labels=True)
    prediction_with_targets = _concatenate_rows(prediction_rows, include_labels=True)
    if fit["primary"].shape != (90, 64, 320):
        raise WO9Failure("derivative", "fit derivative primary shape mismatch")
    if prediction_with_targets["primary"].shape != (45, 64, 320):
        raise WO9Failure("derivative", "prediction derivative primary shape mismatch")
    prediction = {
        key: value for key, value in prediction_with_targets.items() if key != "labels"
    }
    _validate_prediction_derivative_keys(prediction)
    sealed = {
        "event_ids": prediction_with_targets["event_ids"],
        "targets": np.ascontiguousarray(prediction_with_targets["labels"], dtype="int8"),
    }
    fit_path = output / FIT_DERIVATIVE_NAME
    prediction_path = output / PREDICTION_DERIVATIVE_NAME
    sealed_path = output / SEALED_TARGET_NAME
    _write_npz_exclusive(fit_path, fit)
    _write_npz_exclusive(prediction_path, prediction)
    _write_npz_exclusive(sealed_path, sealed)
    fit_hash = _file_sha256(fit_path)
    prediction_hash = _file_sha256(prediction_path)
    sealed_hash = _file_sha256(sealed_path)
    generated = _directory_bytes(output)
    if generated > maximum_output_bytes:
        raise WO9Failure("output", "private derivatives exceed the 64 MiB cap")
    report = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_extraction",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_target_firewalled_derivatives_created",
        "contract_sha256": CONTRACT_SHA256,
        "source_manifest_sha256": manifest_sha256,
        "source_file_hashes": dict(sorted(source_file_hashes.items())),
        "fit_derivative": {
            "path": FIT_DERIVATIVE_NAME,
            "sha256": fit_hash,
            "bytes": fit_path.stat().st_size,
            "rows": 90,
            "runs": ["03", "07"],
            "contains_targets": True,
        },
        "prediction_derivative": {
            "path": PREDICTION_DERIVATIVE_NAME,
            "sha256": prediction_hash,
            "bytes": prediction_path.stat().st_size,
            "rows": 45,
            "runs": ["11"],
            "contains_targets": False,
        },
        "sealed_scorer_input": {
            "path": SEALED_TARGET_NAME,
            "sha256": sealed_hash,
            "bytes": sealed_path.stat().st_size,
            "rows": 45,
            "target_values_printed_or_returned": False,
        },
        "observed": {
            "files": 9,
            "task_events": 135,
            "fit_events": 90,
            "sealed_final_events": 45,
            "channels": 64,
            "sampling_rate_hz": 160,
            "primary_shape_fit": list(fit["primary"].shape),
            "primary_shape_prediction": list(prediction["primary"].shape),
            "nonfinite_samples": 0,
            "duplicate_event_identities": 0,
            "out_of_bounds_windows": 0,
            "group_cross_partition": 0,
        },
        "causality": {
            "producer": "fourth_order_Butterworth_SOS_sosfilt_continuous_run",
            "right_context_seconds": 0.0,
            "decision_latency_seconds_from_cue": 3.0,
            "causal_claim": "cue_causal_only_not_pre_movement",
            "end_to_end_latency_measured": False,
        },
        "generated_private_bytes": generated,
        "warnings": [
            "run11_targets_are_sealed_but_were_parsed_once_during_firewalled_extraction",
            "movement_onset_unavailable",
            "no_separate_EOG_or_EMG_channels",
            "class_is_coupled_to_left_right_visual_cue",
        ],
    }
    _write_json_exclusive(output / EXTRACTION_REPORT_NAME, report, 1024 * 1024)
    if _directory_bytes(output) > maximum_output_bytes:
        raise WO9Failure("output", "extraction report exceeds private output cap")
    return ExtractionOutcome(report, fit_path, prediction_path, sealed_path)


class _CSPModel:
    def __init__(self, csp: Any, lda: Any) -> None:
        self.csp = csp
        self.lda = lda

    def predict(self, values: Any):
        np = _require_numpy()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            features = self.csp.transform(np.asarray(values, dtype="float64"))
        floor = math.log(np.finfo("float64").tiny)
        ceiling = math.log(np.finfo("float64").max)
        features = np.nan_to_num(features, nan=floor, neginf=floor, posinf=ceiling)
        return np.asarray(self.lda.predict(features), dtype="int8")


class _MDMModel:
    def __init__(self, covariance_transformer: Any, mdm: Any) -> None:
        self.covariance_transformer = covariance_transformer
        self.mdm = mdm

    def predict(self, values: Any):
        covariances = self.covariance_transformer.transform(values)
        return _require_numpy().asarray(
            self.mdm.predict(_regularize_covariances(covariances)),
            dtype="int8",
        )


class _FeatureLDAModel:
    def __init__(self, scaler: Any, lda: Any) -> None:
        self.scaler = scaler
        self.lda = lda

    def predict(self, values: Any):
        np = _require_numpy()
        features = self.scaler.transform(np.asarray(values, dtype="float64"))
        return np.asarray(self.lda.predict(features), dtype="int8")


def _require_classical_backends() -> dict[str, Any]:
    try:
        import mne
        import pyriemann
        import sklearn
        from mne.decoding import CSP
        from pyriemann.classification import MDM
        from pyriemann.estimation import Covariances
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError(
            "Work Order 9 classical models require the optional classical extra. "
            "Install with: pip install -e '.[classical]'"
        ) from exc
    versions = {
        "mne": str(mne.__version__),
        "pyriemann": str(pyriemann.__version__),
        "scikit_learn": str(sklearn.__version__),
    }
    if not versions["mne"].startswith("1.12."):
        raise WO9Failure("dependency", "MNE is outside the frozen 1.12.x family")
    if versions["pyriemann"] != "0.12":
        raise WO9Failure("dependency", "pyRiemann is not the frozen 0.12 release")
    mne.set_log_level("ERROR")
    return {
        "CSP": CSP,
        "MDM": MDM,
        "Covariances": Covariances,
        "LDA": LinearDiscriminantAnalysis,
        "StandardScaler": StandardScaler,
        "versions": versions,
    }


def dependency_versions() -> dict[str, str]:
    np = _require_numpy()
    signal = _require_scipy_signal()
    backends = _require_classical_backends()
    import scipy

    del signal
    return {
        "numpy": str(np.__version__),
        "scipy": str(scipy.__version__),
        **backends["versions"],
    }


def _regularize_covariances(covariances: Any):
    np = _require_numpy()
    values = np.asarray(covariances, dtype="float64")
    output = np.empty_like(values)
    for index, covariance in enumerate(values):
        scale = float(np.trace(covariance) / covariance.shape[0])
        numerical_scale = max(abs(scale), 1.0) * np.finfo("float64").eps
        output[index] = (
            0.9 * covariance
            + 0.1 * scale * np.eye(covariance.shape[0], dtype="float64")
            + numerical_scale * np.eye(covariance.shape[0], dtype="float64")
        )
    return output


def fit_registered_family(family_id: str, values: Any, labels: Any):
    """Fit one exact registered family with no fallback or parameter search."""

    np = _require_numpy()
    backends = _require_classical_backends()
    x = np.asarray(values, dtype="float64")
    y = np.asarray(labels, dtype="int8")
    if x.ndim != 3 or x.shape[0] != y.shape[0] or x.shape[-1] != 320:
        raise WO9Failure("model", "classical family input shape mismatch")
    if set(y.tolist()) != {0, 1} or not np.isfinite(x).all():
        raise WO9Failure("model", "classical family requires finite two-class train rows")
    if family_id == "fixed_8_to_30_hz_csp_lda":
        csp = backends["CSP"](
            n_components=4,
            reg=0.1,
            log=True,
            cov_est="concat",
            transform_into="average_power",
            norm_trace=False,
        )
        features = csp.fit_transform(x, y)
        lda = backends["LDA"](
            solver="lsqr",
            shrinkage=0.1,
            priors=np.asarray([0.5, 0.5], dtype="float64"),
        )
        lda.fit(features, y)
        return _CSPModel(csp, lda)
    if family_id == "regularized_riemannian_mdm":
        covariance_transformer = backends["Covariances"](estimator="scm")
        covariances = covariance_transformer.transform(x)
        mdm = backends["MDM"](metric="riemann", n_jobs=1)
        mdm.fit(_regularize_covariances(covariances), y)
        return _MDMModel(covariance_transformer, mdm)
    raise WO9Failure("model", f"unregistered family requested: {family_id}")


def _fit_feature_lda(features: Any, labels: Any):
    np = _require_numpy()
    backends = _require_classical_backends()
    x = np.asarray(features, dtype="float64")
    y = np.asarray(labels, dtype="int8")
    if x.ndim != 2 or x.shape[0] != y.shape[0] or not np.isfinite(x).all():
        raise WO9Failure("model", "feature LDA input mismatch")
    if set(y.tolist()) != {0, 1}:
        raise WO9Failure("model", "feature LDA requires both train classes")
    scaler = backends["StandardScaler"]()
    standardized = scaler.fit_transform(x)
    lda = backends["LDA"](
        solver="lsqr",
        shrinkage=0.1,
        priors=np.asarray([0.5, 0.5], dtype="float64"),
    )
    lda.fit(standardized, y)
    return _FeatureLDAModel(scaler, lda)


def balanced_accuracy(labels: Any, predictions: Any) -> float:
    np = _require_numpy()
    y = np.asarray(labels, dtype="int8")
    predicted = np.asarray(predictions, dtype="int8")
    if y.shape != predicted.shape or y.ndim != 1:
        raise WO9Failure("score", "balanced-accuracy input shape mismatch")
    recalls = []
    for class_id in (0, 1):
        mask = y == class_id
        if not bool(mask.any()):
            raise WO9Failure("score", "balanced accuracy requires both classes")
        recalls.append(float(np.mean(predicted[mask] == class_id)))
    return float(sum(recalls) / 2.0)


def _stable_seed(*parts: str) -> int:
    payload = "|".join(parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _nonidentity_permutation(length: int, seed: int):
    np = _require_numpy()
    if length < 2:
        raise WO9Failure("control", "nonidentity permutation requires at least two rows")
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(length)
    if np.array_equal(permutation, np.arange(length)):
        permutation = np.roll(permutation, 1)
    return permutation


def _derange_train_labels(labels: Any, subjects: Any, runs: Any):
    np = _require_numpy()
    output = np.asarray(labels, dtype="int8").copy()
    subject_values = np.asarray(subjects).astype(str)
    run_values = np.asarray(runs).astype(str)
    for subject in ("S001", "S002", "S003"):
        for run in ("03", "07"):
            indices = np.flatnonzero((subject_values == subject) & (run_values == run))
            permutation = _nonidentity_permutation(
                len(indices),
                _stable_seed(str(SEED), subject, run, "train_label_derangement"),
            )
            candidate = output[indices][permutation]
            if np.array_equal(candidate, output[indices]):
                candidate = 1 - output[indices]
            output[indices] = candidate
    return output


def _channel_indices(channel_names: Any, requested: Sequence[str]):
    np = _require_numpy()
    names = [str(value) for value in np.asarray(channel_names).tolist()]
    missing = [name for name in requested if name not in names]
    if missing:
        raise WO9Failure("channel", f"registered channels are unavailable: {missing}")
    return np.asarray([names.index(name) for name in requested], dtype="int64")


def _hemisphere_swapped(values: Any, channel_names: Any, pairs: Sequence[Sequence[str]]):
    np = _require_numpy()
    output = np.asarray(values).copy()
    names = [str(value) for value in np.asarray(channel_names).tolist()]
    for left, right in pairs:
        if left not in names or right not in names:
            raise WO9Failure("control", "hemisphere-swap channel is unavailable")
        left_index = names.index(left)
        right_index = names.index(right)
        output[:, [left_index, right_index], :] = output[:, [right_index, left_index], :]
    return output


def _timing_features(bundle: Mapping[str, Any]):
    np = _require_numpy()
    return np.stack(
        [
            np.asarray(bundle["event_indices"], dtype="float64"),
            np.asarray(bundle["event_onsets_seconds"], dtype="float64"),
        ],
        axis=1,
    )


def select_registered_family(
    fit: Mapping[str, Any],
    counters: dict[str, int],
) -> tuple[str, dict[str, float]]:
    """Select CSP-LDA versus Riemannian MDM using only runs 03 and 07."""

    np = _require_numpy()
    subjects = np.asarray(fit["subjects"]).astype(str)
    runs = np.asarray(fit["runs"]).astype(str)
    labels = np.asarray(fit["labels"], dtype="int8")
    values = np.asarray(fit["primary"], dtype="float64")
    scores: dict[str, float] = {}
    candidates = (
        "fixed_8_to_30_hz_csp_lda",
        "regularized_riemannian_mdm",
    )
    for family_id in candidates:
        directional_scores = []
        for subject in ("S001", "S002", "S003"):
            for train_run, check_run in (("03", "07"), ("07", "03")):
                train_mask = (subjects == subject) & (runs == train_run)
                check_mask = (subjects == subject) & (runs == check_run)
                model = fit_registered_family(family_id, values[train_mask], labels[train_mask])
                counters["classical_parameter_update_fits"] += 1
                predicted = model.predict(values[check_mask])
                counters["target_blind_model_inference_runs"] += 1
                directional_scores.append(balanced_accuracy(labels[check_mask], predicted))
        scores[family_id] = float(np.mean(directional_scores))
    winner = candidates[0]
    if scores[candidates[1]] > scores[candidates[0]]:
        winner = candidates[1]
    return winner, scores


def _validate_target_blind_inputs(fit: Mapping[str, Any], prediction: Mapping[str, Any]) -> None:
    np = _require_numpy()
    _validate_prediction_derivative_keys(prediction)
    if "labels" not in fit:
        raise WO9Failure("firewall", "fit derivative has no train targets")
    if fit["primary"].shape != (90, 64, 320):
        raise WO9Failure("derivative", "fit primary shape changed")
    if prediction["primary"].shape != (45, 64, 320):
        raise WO9Failure("derivative", "prediction primary shape changed")
    if set(np.asarray(fit["runs"]).astype(str).tolist()) != {"03", "07"}:
        raise WO9Failure("split", "fit derivative contains a non-fit run")
    if set(np.asarray(prediction["runs"]).astype(str).tolist()) != {"11"}:
        raise WO9Failure("split", "prediction derivative contains a non-final run")
    if len(set(np.asarray(fit["event_ids"]).astype(str).tolist())) != 90:
        raise WO9Failure("split", "fit event identities are not unique")
    if len(set(np.asarray(prediction["event_ids"]).astype(str).tolist())) != 45:
        raise WO9Failure("split", "prediction event identities are not unique")
    if set(np.asarray(fit["event_ids"]).astype(str)).intersection(
        np.asarray(prediction["event_ids"]).astype(str)
    ):
        raise WO9Failure("split", "fit and prediction identities overlap")


def run_target_blind_predictions(
    *,
    output_root: str | Path,
    freeze_path: str | Path,
    implementation_evidence: ImplementationEvidence | None,
    implementation_registry: Mapping[str, Any] | None,
    source_kind: str,
    maximum_output_bytes: int = 64 * 1024 * 1024,
    execution_started_monotonic: float | None = None,
    upstream_access_counters: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Fit the frozen families and emit 12 private target-blind prediction sets."""

    np = _require_numpy()
    output = Path(output_root)
    extraction = json.loads((output / EXTRACTION_REPORT_NAME).read_text(encoding="utf-8"))
    fit_path = output / FIT_DERIVATIVE_NAME
    prediction_path = output / PREDICTION_DERIVATIVE_NAME
    if _file_sha256(fit_path) != extraction["fit_derivative"]["sha256"]:
        raise WO9Failure("integrity", "fit derivative hash mismatch")
    if _file_sha256(prediction_path) != extraction["prediction_derivative"]["sha256"]:
        raise WO9Failure("integrity", "prediction derivative hash mismatch")
    fit = _load_npz(fit_path)
    prediction = _load_npz(prediction_path, prediction_derivative=True)
    _validate_target_blind_inputs(fit, prediction)
    contract = load_registered_contract()
    channel_sets = contract["channel_sets"]
    counters = {
        "classical_parameter_update_fits": 0,
        "target_blind_model_inference_runs": 0,
        "train_only_no_signal_prior_fits": 0,
        "prediction_sets_frozen": 0,
        "sealed_final_target_rows_delivered_to_model_stage": 0,
        "final_scoring_events": 0,
    }
    started = time.monotonic()
    selected_family, selection_scores = select_registered_family(fit, counters)
    train_subjects = np.asarray(fit["subjects"]).astype(str)
    final_subjects = np.asarray(prediction["subjects"]).astype(str)
    train_labels = np.asarray(fit["labels"], dtype="int8")
    deranged_labels = _derange_train_labels(
        train_labels,
        fit["subjects"],
        fit["runs"],
    )
    central_names = tuple(channel_sets["sensorimotor_left"]) + tuple(
        channel_sets["sensorimotor_right"]
    )
    central_indices = _channel_indices(fit["channel_names"], central_names)
    proxy_indices = _channel_indices(
        fit["channel_names"],
        tuple(channel_sets["frontal_occipital_proxy"]),
    )
    channel_permutation = _nonidentity_permutation(
        64,
        _stable_seed(str(SEED), "validation_channel_derangement"),
    )
    predictions_by_condition: dict[str, list[int]] = {key: [] for key in CONDITION_IDS}
    for subject in ("S001", "S002", "S003"):
        train_mask = train_subjects == subject
        final_mask = final_subjects == subject
        x_train = np.asarray(fit["primary"][train_mask], dtype="float64")
        x_final = np.asarray(prediction["primary"][final_mask], dtype="float64")
        y_train = train_labels[train_mask]

        primary = fit_registered_family(selected_family, x_train, y_train)
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["selected_full_head_primary"].extend(
            primary.predict(x_final).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        low_model = _fit_feature_lda(fit["low_frequency_features"][train_mask], y_train)
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["low_frequency_shrinkage_lda_comparator"].extend(
            low_model.predict(prediction["low_frequency_features"][final_mask]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        counts = np.bincount(y_train, minlength=2)
        prior = int(0 if counts[0] >= counts[1] else 1)
        predictions_by_condition["train_only_no_signal_prior"].extend([prior] * 15)
        counters["train_only_no_signal_prior_fits"] += 1

        predictions_by_condition["all_zero_final_signal"].extend(
            primary.predict(np.zeros_like(x_final)).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        pre_model = fit_registered_family(
            selected_family,
            fit["pre_cue"][train_mask],
            y_train,
        )
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["pre_cue_model"].extend(
            pre_model.predict(prediction["pre_cue"][final_mask]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        timing_model = _fit_feature_lda(_timing_features(fit)[train_mask], y_train)
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["event_index_and_timing_only_model"].extend(
            timing_model.predict(_timing_features(prediction)[final_mask]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        deranged_model = fit_registered_family(
            selected_family,
            x_train,
            deranged_labels[train_mask],
        )
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["fixed_train_label_derangement"].extend(
            deranged_model.predict(x_final).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        predictions_by_condition["fixed_one_trial_final_signal_displacement"].extend(
            primary.predict(np.roll(x_final, 1, axis=0)).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        predictions_by_condition["fixed_validation_channel_derangement"].extend(
            primary.predict(x_final[:, channel_permutation, :]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        swapped = _hemisphere_swapped(
            x_final,
            prediction["channel_names"],
            channel_sets["hemisphere_swap_pairs"],
        )
        predictions_by_condition["fixed_left_right_hemisphere_swap"].extend(
            primary.predict(swapped).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        proxy_model = fit_registered_family(
            selected_family,
            x_train[:, proxy_indices, :],
            y_train,
        )
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["frontal_occipital_proxy_channel_model"].extend(
            proxy_model.predict(x_final[:, proxy_indices, :]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

        central_model = fit_registered_family(
            selected_family,
            x_train[:, central_indices, :],
            y_train,
        )
        counters["classical_parameter_update_fits"] += 1
        predictions_by_condition["central_sensorimotor_channel_model"].extend(
            central_model.predict(x_final[:, central_indices, :]).tolist()
        )
        counters["target_blind_model_inference_runs"] += 1

    if tuple(predictions_by_condition) != CONDITION_IDS:
        raise WO9Failure("prediction", "prediction condition order mismatch")
    if any(len(values) != 45 for values in predictions_by_condition.values()):
        raise WO9Failure("prediction", "a prediction set does not contain 45 rows")
    if counters["classical_parameter_update_fits"] != 33:
        raise WO9Failure("resource", "classical fit inventory differs from exact 33")
    if counters["target_blind_model_inference_runs"] != 45:
        raise WO9Failure("resource", "model-inference inventory differs from exact 45")
    counters["prediction_sets_frozen"] = len(predictions_by_condition)
    prediction_set_hashes = {
        condition_id: _prediction_set_sha256(values)
        for condition_id, values in predictions_by_condition.items()
    }
    private_payload = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_private_predictions",
        "schema_version": SCHEMA_VERSION,
        "status": "target_blind_predictions_complete",
        "contract_sha256": CONTRACT_SHA256,
        "source_kind": source_kind,
        "selected_family": selected_family,
        "selection_scores_runs03_07_only": selection_scores,
        "event_ids": np.asarray(prediction["event_ids"]).astype(str).tolist(),
        "participant_ids": final_subjects.tolist(),
        "predictions": predictions_by_condition,
        "operation_counters": counters,
        "sealed_target_sha256": extraction["sealed_scorer_input"]["sha256"],
        "prediction_derivative_sha256": extraction["prediction_derivative"]["sha256"],
        "created_at_utc": _utc_now(),
    }
    private_payload["canonical_prediction_sha256"] = _canonical_sha256(private_payload)
    private_path = output / PRIVATE_PREDICTIONS_NAME
    private_bytes = _write_json_exclusive(private_path, private_payload, 4 * 1024 * 1024)
    reloaded = json.loads(private_path.read_text(encoding="utf-8"))
    if reloaded != private_payload:
        raise WO9Failure("replay", "private prediction payload does not replay exactly")
    private_sha256 = _file_sha256(private_path)
    runtime = time.monotonic() - started
    total_runtime = (
        time.monotonic() - execution_started_monotonic
        if execution_started_monotonic is not None
        else runtime
    )
    generated = _directory_bytes(output)
    if generated > maximum_output_bytes:
        raise WO9Failure("output", "target-blind artifacts exceed the 64 MiB cap")
    evidence = implementation_evidence
    implementation_registry_sha256 = (
        _file_sha256(_repo_root() / IMPLEMENTATION_RELATIVE_PATH)
        if implementation_registry is not None
        else None
    )
    implementation_tracked_file_hashes_sha256 = (
        _canonical_sha256(
            {"tracked_file_hashes": implementation_registry["tracked_file_hashes"]}
        )
        if implementation_registry is not None
        else None
    )
    freeze = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "status": "predictions_frozen_run11_sealed_target_file_unopened_by_model_stage",
        "proof_posture": (
            "aggregate_hash_only_real_target_blind_prediction_freeze"
            if source_kind == "real_physionet"
            else "aggregate_hash_only_generated_fixture_qualification"
        ),
        "contract_sha256": CONTRACT_SHA256,
        "authorization_decision_sha256": DECISION_SHA256,
        "implementation_commit": evidence.implementation_commit if evidence else None,
        "implementation_ci_run_id": evidence.implementation_ci_run_id if evidence else None,
        "implementation_base_python_job_id": evidence.base_python_job_id if evidence else None,
        "implementation_optional_neuro_job_id": (
            evidence.optional_neuro_job_id if evidence else None
        ),
        "implementation_registry_sha256": implementation_registry_sha256,
        "implementation_tracked_file_hashes_sha256": (
            implementation_tracked_file_hashes_sha256
        ),
        "source_kind": source_kind,
        "source_manifest_sha256": extraction["source_manifest_sha256"],
        "source_file_count": extraction["observed"]["files"],
        "source_payload_bytes": 23_248_224 if source_kind == "real_physionet" else 0,
        "fit_derivative_sha256": extraction["fit_derivative"]["sha256"],
        "prediction_derivative_sha256": extraction["prediction_derivative"]["sha256"],
        "sealed_target_sha256": extraction["sealed_scorer_input"]["sha256"],
        "private_prediction_payload_sha256": private_sha256,
        "private_prediction_payload_bytes": private_bytes,
        "selected_family": selected_family,
        "selection_metric_runs03_07_only": "macro_directional_balanced_accuracy",
        "prediction_set_ids": list(CONDITION_IDS),
        "prediction_set_count": len(CONDITION_IDS),
        "prediction_set_sha256": prediction_set_hashes,
        "configuration_sha256": _canonical_sha256(
            {
                "candidate_families": contract["candidate_families"],
                "fixed_comparator": contract["fixed_comparator"],
                "causal_preprocessing": contract["causal_preprocessing"],
                "channel_sets": contract["channel_sets"],
                "determinism": contract["determinism"],
            }
        ),
        "split_protocol_sha256": _canonical_sha256(
            {
                "dataset_binding": contract["dataset_binding"],
                "split_and_selection": contract["split_and_selection"],
            }
        ),
        "dependency_versions": dependency_versions(),
        "operation_counters": {
            **dict(upstream_access_counters or {}),
            **counters,
        },
        "resources_through_freeze": {
            "target_blind_runtime_seconds": round(runtime, 6),
            "runtime_seconds": round(total_runtime, 6),
            "peak_rss_bytes": _peak_rss_bytes(),
            "generated_private_bytes_before_target_blind_report": generated,
            "cpu_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
        },
        "target_firewall": {
            "fit_target_rows_available": 90,
            "run11_signal_rows_available": 45,
            "run11_target_rows_available_to_model_stage": 0,
            "prediction_derivative_contains_targets": False,
            "individual_outputs_committed": False,
        },
        "determinism_checks": {
            "private_payload_reload_exact": True,
            "zero_signal_prediction_set_complete": True,
            "no_signal_prediction_set_complete": True,
            "zero_signal_prediction_sha256": prediction_set_hashes[
                "all_zero_final_signal"
            ],
            "no_signal_prediction_sha256": prediction_set_hashes[
                "train_only_no_signal_prior"
            ],
            "fixed_seed": SEED,
        },
        "warnings": [
            "final_targets_remain_sealed_until_remote_green_freeze",
            "visual_cue_is_class_correlated",
            "separate_EOG_and_EMG_unavailable",
            "movement_onset_unavailable",
            "CSP_zero_variance_features_use_a_fixed_machine_epsilon_log_floor",
            "Riemannian_zero_trace_covariance_uses_a_fixed_machine_epsilon_SPD_floor",
            "end_to_end_latency_not_measured",
        ],
        "claim_boundary": {
            "current": "target_blind_prediction_hashes_only_no_scientific_result",
            "maximum_after_future_WO9_V3": contract["claim_boundary"][
                "maximum_scientific_claim_if_future_WO9_V3"
            ],
            "not_established": contract["claim_boundary"][
                "not_established_even_if_future_WO9_V3"
            ],
        },
    }
    freeze["freeze_record_sha256"] = _canonical_sha256(freeze)
    freeze_output = Path(freeze_path)
    _write_json_exclusive(freeze_output, freeze, 1024 * 1024)
    report = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_target_blind_run",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_predictions_frozen_sealed_targets_unopened_by_model_stage",
        "selected_family": selected_family,
        "prediction_set_count": len(CONDITION_IDS),
        "private_prediction_payload_sha256": private_sha256,
        "freeze_record_sha256": _file_sha256(freeze_output),
        "sealed_target_rows_delivered": 0,
        "scoring_events": 0,
        "operation_counters": freeze["operation_counters"],
        "resources": freeze["resources_through_freeze"],
        "warnings": freeze["warnings"],
    }
    _write_json_exclusive(output / TARGET_BLIND_REPORT_NAME, report, 1024 * 1024)
    if _directory_bytes(output) > maximum_output_bytes:
        raise WO9Failure("output", "target-blind report exceeds the private output cap")
    return report


def validate_public_freeze_ledger(freeze: Mapping[str, Any]) -> None:
    if freeze.get("schema_name") != (
        "neurodecodekit.physionet_motor_positive_control_prediction_freeze"
    ):
        raise WO9Failure("freeze", "prediction-freeze schema mismatch")
    if freeze.get("schema_version") != SCHEMA_VERSION:
        raise WO9Failure("freeze", "prediction-freeze version mismatch")
    if freeze.get("contract_sha256") != CONTRACT_SHA256:
        raise WO9Failure("freeze", "prediction-freeze contract binding mismatch")
    if freeze.get("authorization_decision_sha256") != DECISION_SHA256:
        raise WO9Failure("freeze", "prediction-freeze decision binding mismatch")
    if tuple(freeze.get("prediction_set_ids", [])) != CONDITION_IDS:
        raise WO9Failure("freeze", "prediction-freeze condition inventory mismatch")
    if freeze.get("prediction_set_count") != len(CONDITION_IDS):
        raise WO9Failure("freeze", "prediction-freeze set count mismatch")
    contract = load_registered_contract()
    expected_configuration_sha256 = _canonical_sha256(
        {
            "candidate_families": contract["candidate_families"],
            "fixed_comparator": contract["fixed_comparator"],
            "causal_preprocessing": contract["causal_preprocessing"],
            "channel_sets": contract["channel_sets"],
            "determinism": contract["determinism"],
        }
    )
    if freeze.get("configuration_sha256") != expected_configuration_sha256:
        raise WO9Failure("freeze", "prediction-freeze configuration binding mismatch")
    expected_split_sha256 = _canonical_sha256(
        {
            "dataset_binding": contract["dataset_binding"],
            "split_and_selection": contract["split_and_selection"],
        }
    )
    if freeze.get("split_protocol_sha256") != expected_split_sha256:
        raise WO9Failure("freeze", "prediction-freeze split binding mismatch")
    if freeze.get("source_kind") == "real_physionet":
        registry_path = _repo_root() / IMPLEMENTATION_RELATIVE_PATH
        if freeze.get("implementation_registry_sha256") != _file_sha256(registry_path):
            raise WO9Failure("freeze", "prediction-freeze implementation binding mismatch")
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        tracked_hashes_sha256 = _canonical_sha256(
            {"tracked_file_hashes": registry["tracked_file_hashes"]}
        )
        if (
            freeze.get("implementation_tracked_file_hashes_sha256")
            != tracked_hashes_sha256
        ):
            raise WO9Failure("freeze", "prediction-freeze code-hash binding mismatch")
    prediction_hashes = freeze.get("prediction_set_sha256")
    if not isinstance(prediction_hashes, Mapping):
        raise WO9Failure("freeze", "prediction-freeze hash inventory is missing")
    if len(prediction_hashes) != len(CONDITION_IDS) or set(prediction_hashes) != set(
        CONDITION_IDS
    ):
        raise WO9Failure("freeze", "prediction-freeze hash inventory mismatch")
    if any(
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
        for value in prediction_hashes.values()
    ):
        raise WO9Failure("freeze", "prediction-freeze contains an invalid SHA-256")
    determinism = freeze.get("determinism_checks", {})
    if determinism.get("zero_signal_prediction_sha256") != prediction_hashes.get(
        "all_zero_final_signal"
    ):
        raise WO9Failure("freeze", "zero-signal determinism hash mismatch")
    if determinism.get("no_signal_prediction_sha256") != prediction_hashes.get(
        "train_only_no_signal_prior"
    ):
        raise WO9Failure("freeze", "no-signal determinism hash mismatch")
    firewall = freeze.get("target_firewall", {})
    if firewall.get("run11_target_rows_available_to_model_stage") != 0:
        raise WO9Failure("freeze", "prediction-freeze reports final target delivery")
    if firewall.get("prediction_derivative_contains_targets") is not False:
        raise WO9Failure("freeze", "prediction-freeze reports target-bearing predictions")
    if firewall.get("individual_outputs_committed") is not False:
        raise WO9Failure("freeze", "prediction-freeze reports individual public outputs")
    forbidden_keys = {
        "event_ids",
        "participant_ids",
        "predictions",
        "probabilities",
        "targets",
        "participant_outcomes",
    }

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            overlap = forbidden_keys.intersection(value)
            if overlap:
                raise WO9Failure(
                    "freeze", f"public freeze contains individual-output keys: {sorted(overlap)}"
                )
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    walk(freeze)
    expected = dict(freeze)
    observed_digest = expected.pop("freeze_record_sha256", None)
    if observed_digest != _canonical_sha256(expected):
        raise WO9Failure("freeze", "prediction-freeze canonical SHA-256 mismatch")


def _read_json_once(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload, observed = _read_and_hash_nofollow(path, 8 * 1024 * 1024)
    if observed != expected_sha256:
        raise WO9Failure("integrity", f"private JSON hash mismatch: {path.name}")
    value = json.loads(payload.decode("utf-8"))
    if not isinstance(value, dict):
        raise WO9Failure("integrity", f"private JSON is not an object: {path.name}")
    return value


def _read_npz_once(path: Path, expected_sha256: str) -> dict[str, Any]:
    np = _require_numpy()
    payload, observed = _read_and_hash_nofollow(path, 64 * 1024 * 1024)
    if observed != expected_sha256:
        raise WO9Failure("integrity", f"private NPZ hash mismatch: {path.name}")
    with np.load(io.BytesIO(payload), allow_pickle=False) as archive:
        return {key: np.array(archive[key], copy=True) for key in archive.files}


def _aggregate_condition_metrics(
    labels: Any,
    predictions: Any,
    participants: Any,
    *,
    permutation_draws: int,
) -> tuple[dict[str, Any], list[float]]:
    np = _require_numpy()
    y = np.asarray(labels, dtype="int8")
    predicted = np.asarray(predictions, dtype="int8")
    subject_values = np.asarray(participants).astype(str)
    participant_scores = [
        balanced_accuracy(y[subject_values == subject], predicted[subject_values == subject])
        for subject in ("S001", "S002", "S003")
    ]
    pooled = balanced_accuracy(y, predicted)
    rng = np.random.default_rng(SEED)
    null_at_least = 0
    subject_indices = [
        np.flatnonzero(subject_values == subject) for subject in ("S001", "S002", "S003")
    ]
    for _ in range(permutation_draws):
        permuted = y.copy()
        for indices in subject_indices:
            permuted[indices] = rng.permutation(permuted[indices])
        if balanced_accuracy(permuted, predicted) >= pooled - 1e-15:
            null_at_least += 1
    p_value = (1 + null_at_least) / (1 + permutation_draws)
    metrics = {
        "correct_count": int(np.sum(y == predicted)),
        "pooled_balanced_accuracy": pooled,
        "macro_participant_balanced_accuracy": float(np.mean(participant_scores)),
        "participants_above_0_5_balanced_accuracy": int(
            sum(score > 0.5 for score in participant_scores)
        ),
        "minimum_participant_balanced_accuracy": float(min(participant_scores)),
        "one_sided_within_participant_permutation_p": float(p_value),
        "permutation_draws": permutation_draws,
    }
    return metrics, participant_scores


def _predictive_thresholds_pass(metrics: Mapping[str, Any]) -> bool:
    return bool(
        metrics["correct_count"] >= 30
        and metrics["pooled_balanced_accuracy"] >= 0.65
        and metrics["macro_participant_balanced_accuracy"] >= 0.60
        and metrics["participants_above_0_5_balanced_accuracy"] >= 2
        and metrics["minimum_participant_balanced_accuracy"] >= 0.40
        and metrics["one_sided_within_participant_permutation_p"] <= 0.05
    )


def _physiology_metrics(
    physiology_log_power: Any,
    labels: Any,
    participants: Any,
    channel_names: Any,
    *,
    sign_flip_draws: int,
) -> dict[str, Any]:
    np = _require_numpy()
    contract = load_registered_contract()
    left_indices = _channel_indices(
        channel_names,
        tuple(contract["channel_sets"]["sensorimotor_left"]),
    )
    right_indices = _channel_indices(
        channel_names,
        tuple(contract["channel_sets"]["sensorimotor_right"]),
    )
    values = np.asarray(physiology_log_power, dtype="float64")
    y = np.asarray(labels, dtype="int8")
    subject_values = np.asarray(participants).astype(str)
    if values.shape != (45, 2, 2, 64):
        raise WO9Failure("physiology", "physiology array shape mismatch")
    active_minus_baseline = values[:, :, 1, :] - values[:, :, 0, :]
    left_change = active_minus_baseline[:, :, left_indices].mean(axis=2)
    right_change = active_minus_baseline[:, :, right_indices].mean(axis=2)
    event_effects = np.where(
        y[:, None] == 0,
        right_change - left_change,
        left_change - right_change,
    ).mean(axis=1)
    participant_effects = [
        float(np.mean(event_effects[subject_values == subject]))
        for subject in ("S001", "S002", "S003")
    ]
    pooled = float(np.mean(event_effects))
    rng = np.random.default_rng(SEED)
    null_at_most = 0
    for _ in range(sign_flip_draws):
        signs = rng.choice(np.asarray([-1.0, 1.0]), size=event_effects.shape[0])
        if float(np.mean(event_effects * signs)) <= pooled + 1e-15:
            null_at_most += 1
    p_value = (1 + null_at_most) / (1 + sign_flip_draws)
    participant_direction_count = int(sum(effect < 0.0 for effect in participant_effects))
    return {
        "registered_direction": "contralateral_minus_ipsilateral_is_negative",
        "pooled_contralateral_minus_ipsilateral": pooled,
        "participants_with_registered_direction": participant_direction_count,
        "paired_event_sign_flip_p": float(p_value),
        "sign_flip_draws": sign_flip_draws,
        "gate_passed": bool(
            participant_direction_count >= 2 and pooled < 0.0 and p_value <= 0.05
        ),
    }


def score_private_predictions(
    *,
    freeze: Mapping[str, Any],
    private_predictions: Mapping[str, Any],
    sealed: Mapping[str, Any],
    prediction_derivative: Mapping[str, Any],
    permutation_draws: int = 32_767,
) -> dict[str, Any]:
    """Apply the frozen aggregate scorer without exposing individual outcomes."""

    np = _require_numpy()
    validate_public_freeze_ledger(freeze)
    event_ids = np.asarray(private_predictions.get("event_ids", [])).astype(str)
    participants = np.asarray(private_predictions.get("participant_ids", [])).astype(str)
    target_event_ids = np.asarray(sealed.get("event_ids", [])).astype(str)
    labels = np.asarray(sealed.get("targets", []), dtype="int8")
    if event_ids.shape != (45,) or not np.array_equal(event_ids, target_event_ids):
        raise WO9Failure("score", "frozen prediction and target event identities differ")
    if participants.shape != (45,) or labels.shape != (45,):
        raise WO9Failure("score", "final participant or target shape mismatch")
    if set(labels.tolist()) != {0, 1}:
        raise WO9Failure("score", "sealed final set does not contain both classes")
    predictions = private_predictions.get("predictions")
    if not isinstance(predictions, Mapping) or set(predictions) != set(CONDITION_IDS):
        raise WO9Failure("score", "private prediction inventory mismatch")
    prediction_hashes = freeze["prediction_set_sha256"]
    for condition_id in CONDITION_IDS:
        if _prediction_set_sha256(predictions[condition_id]) != prediction_hashes[condition_id]:
            raise WO9Failure(
                "score", f"private prediction hash mismatch for {condition_id}"
            )
    condition_metrics = {}
    participant_scores_by_condition = {}
    for condition_id in CONDITION_IDS:
        metrics, participant_scores = _aggregate_condition_metrics(
            labels,
            predictions[condition_id],
            participants,
            permutation_draws=permutation_draws,
        )
        condition_metrics[condition_id] = metrics
        participant_scores_by_condition[condition_id] = participant_scores
    primary = condition_metrics["selected_full_head_primary"]
    no_signal = condition_metrics["train_only_no_signal_prior"]
    primary_thresholds = _predictive_thresholds_pass(primary)
    primary_beats_prior = bool(
        primary["pooled_balanced_accuracy"] > no_signal["pooled_balanced_accuracy"]
        and primary["macro_participant_balanced_accuracy"]
        > no_signal["macro_participant_balanced_accuracy"]
    )
    primary_passed = primary_thresholds and primary_beats_prior
    physiology = _physiology_metrics(
        prediction_derivative["physiology_log_power"],
        labels,
        participants,
        prediction_derivative["channel_names"],
        sign_flip_draws=permutation_draws,
    )
    pre_cue = condition_metrics["pre_cue_model"]
    timing = condition_metrics["event_index_and_timing_only_model"]
    label_deranged = condition_metrics["fixed_train_label_derangement"]
    displaced = condition_metrics["fixed_one_trial_final_signal_displacement"]
    channel_deranged = condition_metrics["fixed_validation_channel_derangement"]
    hemisphere_swap = condition_metrics["fixed_left_right_hemisphere_swap"]
    proxy = condition_metrics["frontal_occipital_proxy_channel_model"]
    central = condition_metrics["central_sensorimotor_channel_model"]
    determinism = freeze["determinism_checks"]
    confound_components = {
        "pre_cue_below_0_60": pre_cue["pooled_balanced_accuracy"] < 0.60,
        "timing_only_below_0_60": timing["pooled_balanced_accuracy"] < 0.60,
        "train_label_deranged_below_0_60": (
            label_deranged["pooled_balanced_accuracy"] < 0.60
        ),
        "one_trial_displaced_below_0_60": displaced["pooled_balanced_accuracy"] < 0.60,
        "zero_signal_deterministic": bool(
            determinism.get("zero_signal_prediction_set_complete")
            and len(predictions["all_zero_final_signal"]) == 45
            and all(value in {0, 1} for value in predictions["all_zero_final_signal"])
        ),
        "no_signal_deterministic": bool(
            determinism.get("no_signal_prediction_set_complete")
            and len(predictions["train_only_no_signal_prior"]) == 45
            and all(value in {0, 1} for value in predictions["train_only_no_signal_prior"])
        ),
        "validation_channel_derangement_fails_primary": not _predictive_thresholds_pass(
            channel_deranged
        ),
        "central_minus_proxy_at_least_0_05": (
            central["pooled_balanced_accuracy"]
            - proxy["pooled_balanced_accuracy"]
            >= 0.05
        ),
        "frontal_occipital_proxy_fails_primary": not _predictive_thresholds_pass(proxy),
        "hemisphere_swap_fails_primary": not _predictive_thresholds_pass(hemisphere_swap),
    }
    confound_passed = all(confound_components.values())
    if not primary_passed:
        verdict = "WO9-V1"
    elif not physiology["gate_passed"] or not confound_passed:
        verdict = "WO9-V2"
    else:
        verdict = "WO9-V3"
    return {
        "verdict": verdict,
        "selected_family": freeze["selected_family"],
        "scored_final_events": 45,
        "primary_gate": {
            "passed": primary_passed,
            "threshold_components_passed": primary_thresholds,
            "beats_train_only_no_signal": primary_beats_prior,
            "metrics": primary,
            "train_only_no_signal_metrics": no_signal,
        },
        "physiology_gate": physiology,
        "confound_gate": {
            "passed": confound_passed,
            "components": confound_components,
        },
        "condition_metrics": condition_metrics,
        "individual_participant_metrics_published": False,
        "participant_metric_count_retained_privately": sum(
            len(values) for values in participant_scores_by_condition.values()
        ),
        "warnings": [
            "left_right_motor_action_is_coupled_to_a_left_right_visual_cue",
            "separate_EOG_and_EMG_are_unavailable",
            "proxy_failure_does_not_prove_absence_of_ocular_or_muscle_confound",
            "movement_onset_is_unavailable",
            "result_is_held_out_run_not_unseen_person_generalization",
            "end_to_end_latency_was_not_measured",
        ],
    }


def _validate_implementation_registry(
    repo_root: Path,
    evidence: ImplementationEvidence,
) -> dict[str, Any]:
    registry_path = repo_root / IMPLEMENTATION_RELATIVE_PATH
    if not _path_tracked_at_head(repo_root, registry_path):
        raise WO9Refusal("Work Order 9 implementation registry is not tracked at HEAD")
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("schema_name") != (
        "neurodecodekit.physionet_motor_positive_control_implementation"
    ):
        raise WO9Refusal("Work Order 9 implementation registry schema mismatch")
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise WO9Refusal("Work Order 9 implementation registry version mismatch")
    if registry.get("status") != (
        "fixture_qualified_exact_implementation_requires_remote_green_before_real_access"
    ):
        raise WO9Refusal("Work Order 9 implementation registry status mismatch")
    decision = registry.get("green_authorization_decision", {})
    expected_decision = {
        "commit": DECISION_COMMIT,
        "push_ci_run_id": DECISION_CI_RUN_ID,
        "base_python_job_id": DECISION_BASE_JOB_ID,
        "optional_neuro_job_id": DECISION_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }
    if decision != expected_decision:
        raise WO9Refusal("implementation registry authorization proof mismatch")
    if _git_head(repo_root) != evidence.implementation_commit:
        raise WO9Refusal("real execution requires the exact implementation commit at HEAD")
    if min(
        evidence.implementation_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise WO9Refusal("real execution requires positive remote-green CI identifiers")
    for row in registry.get("tracked_file_hashes", []):
        path = repo_root / _safe_relative_path(str(row["path"]))
        if _file_sha256(path) != row["sha256"]:
            raise WO9Refusal(f"implementation file hash mismatch: {row['path']}")
    if registry.get("fixture_qualification", {}).get("all_gates_passed") is not True:
        raise WO9Refusal("implementation fixture qualification did not pass")
    verification = registry.get("verification", {})
    required_verification = (
        "focused_base_passed",
        "focused_optional_passed",
        "complete_base_suite_passed",
        "complete_optional_suite_passed",
        "ruff_passed",
        "compileall_passed",
        "registry_json_validation_passed",
        "cli_help_and_dry_run_passed",
        "git_diff_check_passed",
    )
    if any(verification.get(name) is not True for name in required_verification):
        raise WO9Refusal("implementation registry reports an incomplete verification gate")
    current_versions = dependency_versions()
    if current_versions != registry.get("optional_environment", {}).get(
        "qualified_versions"
    ):
        raise WO9Refusal("runtime dependency versions differ from the qualified environment")
    real_counters = registry.get("implementation_access_counters", {})
    if any(value != 0 for value in real_counters.values()):
        raise WO9Refusal("implementation registry reports a real-data or target operation")
    return registry


def _assert_directory_nofollow(path: Path) -> None:
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise WO9Failure("integrity", f"registered directory is unavailable: {path}") from exc
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise WO9Failure("integrity", f"registered directory is not a non-symlink: {path}")


def _exact_bundle_membership(bundle_root: Path, expected_paths: Sequence[str]) -> None:
    observed_files = []
    for current_root, directories, filenames in os.walk(bundle_root, followlinks=False):
        current = Path(current_root)
        for directory in directories:
            candidate = current / directory
            if candidate.is_symlink():
                raise WO9Failure("integrity", "registered bundle contains a symlink directory")
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink():
                raise WO9Failure("integrity", "registered bundle contains a symlink file")
            observed_files.append(candidate.relative_to(bundle_root).as_posix())
    if sorted(observed_files) != sorted(expected_paths):
        raise WO9Failure("integrity", "registered bundle has missing or additional files")


def _assert_live_caps(
    *,
    started: float,
    output_root: Path,
    contract: Mapping[str, Any],
) -> None:
    caps = contract["resource_caps"]
    if time.monotonic() - started > int(caps["wall_time_seconds"]):
        raise WO9Failure("resource", "Work Order 9 exceeded the 1,800-second wall cap")
    if _peak_rss_bytes() > int(caps["peak_rss_bytes"]):
        raise WO9Failure("resource", "Work Order 9 exceeded the 768 MiB RSS cap")
    if _directory_bytes(output_root) > int(caps["generated_private_output_bytes"]):
        raise WO9Failure("resource", "Work Order 9 exceeded the 64 MiB private-output cap")


def run_registered_prediction_execution(
    *,
    repo_root: str | Path,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
    bundle_root: str | Path | None = None,
    acquisition_manifest_path: str | Path | None = None,
    output_root: str | Path | None = None,
    freeze_path: str | Path | None = None,
    raw_loader: RawLoader = _load_mne_run,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Consume the one real execution through target-blind prediction freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    implementation_registry = _validate_implementation_registry(root, evidence)
    expected_bundle = root / BUNDLE_RELATIVE_PATH
    expected_manifest = root / ACQUISITION_MANIFEST_RELATIVE_PATH
    expected_output = root / EXECUTION_ROOT_RELATIVE_PATH
    expected_freeze = root / FREEZE_RELATIVE_PATH
    bundle = Path(bundle_root) if bundle_root is not None else expected_bundle
    manifest_path = (
        Path(acquisition_manifest_path)
        if acquisition_manifest_path is not None
        else expected_manifest
    )
    output = Path(output_root) if output_root is not None else expected_output
    public_freeze = Path(freeze_path) if freeze_path is not None else expected_freeze
    if enforce_registered_paths:
        for observed, expected, label in (
            (bundle, expected_bundle, "bundle"),
            (manifest_path, expected_manifest, "private acquisition manifest"),
            (output, expected_output, "execution output"),
            (public_freeze, expected_freeze, "prediction freeze"),
        ):
            if observed.absolute() != expected.absolute():
                raise WO9Refusal(f"{label} path differs from the registered path")
    if output.exists() or output.is_symlink():
        raise WO9Refusal("registered Work Order 9 execution root already exists")
    if public_freeze.exists() or public_freeze.is_symlink():
        raise WO9Refusal("registered Work Order 9 prediction-freeze path already exists")
    free_before = shutil.disk_usage(root).free
    if free_before < int(contract["resource_caps"]["minimum_free_disk_bytes_before"]):
        raise WO9Refusal("free disk is below the frozen 2 GiB minimum")
    if _peak_rss_bytes() > int(contract["resource_caps"]["peak_rss_bytes"]):
        raise WO9Refusal("process RSS already exceeds the frozen cap")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    started_at = _utc_now()
    _write_json_exclusive(
        output / EXECUTION_CONSUMED_NAME,
        {
            "status": "registered_execution_started_no_retry_or_rerun",
            "started_at_utc": started_at,
            "implementation_commit": evidence.implementation_commit,
            "contract_sha256": CONTRACT_SHA256,
        },
        16 * 1024,
    )
    counters = {
        "registered_executions": 1,
        "private_manifest_opens": 0,
        "edf_sha256_passes": 0,
        "edf_semantic_parses": 0,
        "edf_header_reads": 0,
        "edf_annotation_reads": 0,
        "edf_signal_reads": 0,
        "fit_target_rows_delivered": 0,
        "run11_signal_rows_delivered": 0,
        "run11_target_rows_delivered_to_model_process": 0,
        "event_sidecar_operations": 0,
        "network_requests": 0,
        "network_bytes": 0,
        "new_payload_bytes": 0,
        "additional_files_participants_runs_or_datasets": 0,
        "retries": 0,
        "reruns": 0,
    }
    try:
        _verify_private_acquisition_manifest(manifest_path, contract)
        counters["private_manifest_opens"] = 1
        _assert_directory_nofollow(bundle)
        expected_paths = [row["path"] for row in contract["selected_files"]]
        _exact_bundle_membership(bundle, expected_paths)
        source_hashes: dict[str, str] = {}

        def records():
            for row in contract["selected_files"]:
                relative = _safe_relative_path(row["path"])
                path = bundle / relative
                source_hashes[row["path"]] = _hash_registered_edf(
                    path,
                    int(row["size_bytes"]),
                    str(row["sha256"]),
                )
                counters["edf_sha256_passes"] += 1
                record = raw_loader(path, str(row["subject"]), str(row["run"]))
                counters["edf_semantic_parses"] += 1
                counters["edf_header_reads"] += 1
                counters["edf_annotation_reads"] += 1
                counters["edf_signal_reads"] += 1
                yield record
                _assert_live_caps(started=started, output_root=output, contract=contract)

        extraction = extract_records_to_derivatives(
            records(),
            output,
            source_file_hashes=source_hashes,
            manifest_sha256=ACQUISITION_MANIFEST_SHA256,
            maximum_output_bytes=int(contract["resource_caps"]["generated_private_output_bytes"]),
        )
        del extraction
        counters["fit_target_rows_delivered"] = 90
        counters["run11_signal_rows_delivered"] = 45
        if counters["edf_sha256_passes"] != 9 or counters["edf_semantic_parses"] != 9:
            raise WO9Failure("resource", "EDF hash or semantic-parse count mismatch")
        report = run_target_blind_predictions(
            output_root=output,
            freeze_path=public_freeze,
            implementation_evidence=evidence,
            implementation_registry=implementation_registry,
            source_kind="real_physionet",
            maximum_output_bytes=int(contract["resource_caps"]["generated_private_output_bytes"]),
            execution_started_monotonic=started,
            upstream_access_counters=counters,
        )
        _assert_live_caps(started=started, output_root=output, contract=contract)
        freeze = json.loads(public_freeze.read_text(encoding="utf-8"))
        validate_public_freeze_ledger(freeze)
        operations = freeze["operation_counters"]
        if operations["classical_parameter_update_fits"] > int(
            contract["resource_caps"]["maximum_classical_parameter_update_fits"]
        ):
            raise WO9Failure("resource", "classical fit cap exceeded")
        if operations["target_blind_model_inference_runs"] > int(
            contract["resource_caps"]["maximum_prediction_sets"]
        ):
            raise WO9Failure("resource", "target-blind inference cap exceeded")
        return {
            **report,
            "execution_started_at_utc": started_at,
            "execution_finished_at_utc": _utc_now(),
            "runtime_seconds": round(time.monotonic() - started, 6),
            "peak_rss_bytes": _peak_rss_bytes(),
            "free_disk_before_bytes": free_before,
            "free_disk_after_bytes": shutil.disk_usage(root).free,
            "generated_private_bytes": _directory_bytes(output),
            "input_payload_bytes": 23_248_224,
            "output_root": str(output),
            "freeze_path": str(public_freeze),
            "final_target_deliveries": 0,
            "scoring_events": 0,
            "end_to_end_latency_measured": False,
        }
    except Exception as exc:
        failure = {
            "schema_name": "neurodecodekit.physionet_motor_positive_control_failure",
            "schema_version": SCHEMA_VERSION,
            "status": "WO9-V0_registered_execution_consumed_and_parked",
            "failure_stage": exc.stage if isinstance(exc, WO9Failure) else "unexpected",
            "failure_type": type(exc).__name__,
            "failure_reason": str(exc),
            "started_at_utc": started_at,
            "finished_at_utc": _utc_now(),
            "runtime_seconds": round(time.monotonic() - started, 6),
            "peak_rss_bytes": _peak_rss_bytes(),
            "access_counters": counters,
            "retry_or_rerun_authorized": False,
            "scientific_claim_upgrade": False,
        }
        try:
            _write_json_exclusive(output / "failure.v0.json", failure, 1024 * 1024)
        except Exception:
            pass
        raise


def score_registered_execution(
    *,
    repo_root: str | Path,
    evidence: FreezeEvidence,
    environ: Mapping[str, str],
    output_root: str | Path | None = None,
    freeze_path: str | Path | None = None,
    result_path: str | Path | None = None,
    enforce_registered_paths: bool = True,
) -> dict[str, Any]:
    """Open the sealed targets once and apply the frozen aggregate verdict router."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    _check_thread_environment(environ)
    output = (
        Path(output_root)
        if output_root is not None
        else root / EXECUTION_ROOT_RELATIVE_PATH
    )
    public_freeze = (
        Path(freeze_path) if freeze_path is not None else root / FREEZE_RELATIVE_PATH
    )
    public_result = (
        Path(result_path) if result_path is not None else root / RESULT_RELATIVE_PATH
    )
    if enforce_registered_paths:
        expected = (
            (output, root / EXECUTION_ROOT_RELATIVE_PATH),
            (public_freeze, root / FREEZE_RELATIVE_PATH),
            (public_result, root / RESULT_RELATIVE_PATH),
        )
        if any(observed.absolute() != wanted.absolute() for observed, wanted in expected):
            raise WO9Refusal("scoring path differs from the registered path")
    if _git_head(root) != evidence.freeze_commit:
        raise WO9Refusal("scoring requires the remotely green freeze commit at HEAD")
    if min(
        evidence.freeze_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise WO9Refusal("scoring requires positive remote-green freeze CI identifiers")
    if not _path_tracked_at_head(root, public_freeze):
        raise WO9Refusal("prediction-freeze ledger is not tracked at green HEAD")
    if public_result.exists() or public_result.is_symlink():
        raise WO9Refusal("registered Work Order 9 public result already exists")
    consumed_path = output / SCORING_CONSUMED_NAME
    if consumed_path.exists() or consumed_path.is_symlink():
        raise WO9Refusal("registered Work Order 9 scoring event is already consumed")
    freeze = json.loads(public_freeze.read_text(encoding="utf-8"))
    validate_public_freeze_ledger(freeze)
    if freeze.get("source_kind") != "real_physionet":
        raise WO9Refusal("registered scorer refuses a non-real prediction freeze")
    _write_json_exclusive(
        consumed_path,
        {
            "status": "sealed_target_delivery_started_no_retry_or_rerun",
            "started_at_utc": _utc_now(),
            "freeze_commit": evidence.freeze_commit,
            "freeze_record_sha256": _file_sha256(public_freeze),
        },
        16 * 1024,
    )
    started = time.monotonic()
    private_predictions = _read_json_once(
        output / PRIVATE_PREDICTIONS_NAME,
        str(freeze["private_prediction_payload_sha256"]),
    )
    private_canonical = dict(private_predictions)
    private_digest = private_canonical.pop("canonical_prediction_sha256", None)
    if private_digest != _canonical_sha256(private_canonical):
        raise WO9Failure("integrity", "private prediction canonical hash mismatch")
    sealed = _read_npz_once(
        output / SEALED_TARGET_NAME,
        str(freeze["sealed_target_sha256"]),
    )
    prediction_derivative = _read_npz_once(
        output / PREDICTION_DERIVATIVE_NAME,
        str(freeze["prediction_derivative_sha256"]),
    )
    scored = score_private_predictions(
        freeze=freeze,
        private_predictions=private_predictions,
        sealed=sealed,
        prediction_derivative=prediction_derivative,
        permutation_draws=int(contract["determinism"]["permutation_test_draws"]),
    )
    generated = _directory_bytes(output)
    total_runtime = float(freeze["resources_through_freeze"]["runtime_seconds"]) + (
        time.monotonic() - started
    )
    peak_rss = max(
        int(freeze["resources_through_freeze"]["peak_rss_bytes"]),
        _peak_rss_bytes(),
    )
    resource_gates = {
        "runtime_within_1800_seconds": total_runtime <= 1800.0,
        "peak_rss_within_805306368_bytes": peak_rss <= 805_306_368,
        "private_output_within_67108864_bytes": generated <= 67_108_864,
        "one_thread_worker_and_numerical_job": True,
        "zero_network_and_new_payload_bytes": True,
        "fits_within_40": int(
            freeze["operation_counters"]["classical_parameter_update_fits"]
        )
        <= 40,
        "target_blind_inferences_within_64": int(
            freeze["operation_counters"]["target_blind_model_inference_runs"]
        )
        <= 64,
        "one_target_delivery_and_score": True,
        "zero_retry_and_rerun": True,
    }
    if not all(resource_gates.values()):
        scored["verdict"] = "WO9-V0"
    result = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_result",
        "schema_version": SCHEMA_VERSION,
        "status": "consumed_one_final_score_no_retry_no_rerun",
        "proof_posture": "aggregate_three_axis_held_out_run_motor_task_EEG_pilot",
        "verdict": scored["verdict"],
        "contract_sha256": CONTRACT_SHA256,
        "authorization_decision_sha256": DECISION_SHA256,
        "implementation_commit": freeze["implementation_commit"],
        "prediction_freeze": {
            "commit": evidence.freeze_commit,
            "ci_run_id": evidence.freeze_ci_run_id,
            "base_python_job_id": evidence.base_python_job_id,
            "optional_neuro_job_id": evidence.optional_neuro_job_id,
            "ledger_sha256": _file_sha256(public_freeze),
        },
        "source": {
            "dataset": "PhysioNet EEGMMIDB 1.0.0",
            "subjects": 3,
            "fit_selection_runs": ["03", "07"],
            "sealed_final_run": "11",
            "files": 9,
            "input_bytes": 23_248_224,
            "task_events": 135,
            "scored_final_events": 45,
        },
        "selected_family": scored["selected_family"],
        "primary_gate": scored["primary_gate"],
        "physiology_gate": scored["physiology_gate"],
        "confound_gate": scored["confound_gate"],
        "condition_metrics": scored["condition_metrics"],
        "resource_gates": resource_gates,
        "measurements": {
            "input_payload_bytes": 23_248_224,
            "generated_private_output_bytes": generated,
            "public_result_bytes": 0,
            "runtime_seconds_through_freeze": freeze["resources_through_freeze"][
                "runtime_seconds"
            ],
            "scoring_runtime_seconds": round(time.monotonic() - started, 6),
            "total_runtime_seconds": round(total_runtime, 6),
            "peak_rss_bytes": peak_rss,
            "cpu_threads": 1,
            "workers": 1,
            "concurrent_numerical_jobs": 1,
            "classical_parameter_update_fits": freeze["operation_counters"][
                "classical_parameter_update_fits"
            ],
            "target_blind_model_inference_runs": freeze["operation_counters"][
                "target_blind_model_inference_runs"
            ],
            "prediction_sets": freeze["prediction_set_count"],
            "raw_data_reads": freeze["operation_counters"].get("edf_semantic_parses", 0),
            "real_cache_reads": 0,
            "final_target_deliveries": 1,
            "final_scoring_events": 1,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "retries": 0,
            "reruns": 0,
            "producer_is_causal": True,
            "right_context_seconds": 0.0,
            "decision_latency_seconds_from_cue": 3.0,
            "end_to_end_latency_measured": False,
        },
        "individual_outputs": {
            "targets_published": False,
            "predictions_published": False,
            "probabilities_published": False,
            "participant_outcomes_published": False,
        },
        "warnings": scored["warnings"],
        "unavailable_fields": {
            "actual_movement_onset": "not provided by the registered dataset surface",
            "separate_EOG": "not present in the registered 64-channel EEG payload",
            "separate_EMG": "not present in the registered payload",
            "unseen_person_generalization": "not tested; all models are participant-specific",
            "brain_specific_origin": "not identifiable from this visually cued task",
            "end_to_end_latency": "not measured",
            "portable_or_home_hardware": "not tested",
        },
        "claim_boundary": {
            "maximum_if_WO9_V3": contract["claim_boundary"][
                "maximum_scientific_claim_if_future_WO9_V3"
            ],
            "not_established": contract["claim_boundary"][
                "not_established_even_if_future_WO9_V3"
            ],
        },
    }
    for _ in range(8):
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
        observed_bytes = len(payload)
        if result["measurements"]["public_result_bytes"] == observed_bytes:
            break
        result["measurements"]["public_result_bytes"] = observed_bytes
    else:
        raise WO9Failure("output", "public result byte measurement did not converge")
    written = _write_json_exclusive(public_result, result, 1024 * 1024)
    if written != result["measurements"]["public_result_bytes"]:
        raise WO9Failure("output", "public result byte measurement is not exact")
    return result


def build_synthetic_run_record(subject: str, run: str) -> RunRecord:
    """Generate one deterministic 64-channel fixture run with no real-data input."""

    np = _require_numpy()
    if subject not in {"S001", "S002", "S003"} or run not in {"03", "07", "11"}:
        raise ValueError("synthetic Work Order 9 identity is outside the registered grid")
    sampling_rate_hz = 160
    onsets = np.asarray([3.0 + 4.0 * index for index in range(15)], dtype="float64")
    sample_count = int(round((onsets[-1] + 3.5) * sampling_rate_hz))
    rng = np.random.default_rng(_stable_seed("synthetic", subject, run, str(SEED)))
    values = rng.normal(0.0, 0.35e-6, size=(64, sample_count))
    common = rng.normal(0.0, 0.15e-6, size=sample_count)
    values += common[None, :]
    geometry = np.zeros((64, 3), dtype="float64")
    for index in range(64):
        angle = 2.0 * math.pi * index / 64.0
        geometry[index] = [0.09 * math.cos(angle), 0.09 * math.sin(angle), 0.04]
    left_names = load_registered_contract()["channel_sets"]["sensorimotor_left"]
    right_names = load_registered_contract()["channel_sets"]["sensorimotor_right"]
    left_indices = [REGISTERED_CHANNEL_NAMES.index(name) for name in left_names]
    right_indices = [REGISTERED_CHANNEL_NAMES.index(name) for name in right_names]
    annotations = []
    time_axis = np.arange(sample_count, dtype="float64") / sampling_rate_hz
    run_offset = {"03": 0, "07": 1, "11": 0}[run]
    for event_index, onset in enumerate(onsets):
        label = (event_index + run_offset) % 2
        description = "T1" if label == 0 else "T2"
        annotations.append(Annotation(float(onset), description))
        active = (time_axis >= onset + 1.0) & (time_axis < onset + 3.0)
        carrier = np.sin(2.0 * math.pi * 10.0 * (time_axis[active] - onset))
        if label == 0:
            values[np.ix_(right_indices, np.flatnonzero(active))] += 0.15e-6 * carrier
            values[np.ix_(left_indices, np.flatnonzero(active))] += 1.8e-6 * carrier
        else:
            values[np.ix_(left_indices, np.flatnonzero(active))] += 0.15e-6 * carrier
            values[np.ix_(right_indices, np.flatnonzero(active))] += 1.8e-6 * carrier
    return RunRecord(
        subject=subject,
        run=run,
        sampling_rate_hz=float(sampling_rate_hz),
        channel_names=REGISTERED_CHANNEL_NAMES,
        channel_geometry_m=geometry,
        signal_volts=np.ascontiguousarray(values, dtype="float64"),
        annotations=tuple(annotations),
    )


def run_synthetic_qualification(
    output_root: str | Path,
    *,
    maximum_output_bytes: int = 64 * 1024 * 1024,
    permutation_draws: int = 255,
) -> dict[str, Any]:
    """Exercise the complete interface on generated arrays without a real path."""

    if maximum_output_bytes <= 0 or maximum_output_bytes > 64 * 1024 * 1024:
        raise WO9Refusal("synthetic qualification cap must be positive and at most 64 MiB")
    if permutation_draws <= 0 or permutation_draws > 32_767:
        raise WO9Refusal("synthetic permutation draws must be between 1 and 32,767")
    output = Path(output_root)
    if output.exists() or output.is_symlink():
        raise WO9Refusal("synthetic qualification output already exists")
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    records = (
        build_synthetic_run_record(subject, run)
        for subject in ("S001", "S002", "S003")
        for run in ("03", "07", "11")
    )
    source_hashes = {
        f"{subject}/{subject}R{run}.synthetic": _sha256_bytes(
            f"synthetic|{subject}|{run}|{SEED}".encode("utf-8")
        )
        for subject in ("S001", "S002", "S003")
        for run in ("03", "07", "11")
    }
    extraction = extract_records_to_derivatives(
        records,
        output,
        source_file_hashes=source_hashes,
        manifest_sha256=_sha256_bytes(b"generated_fixture_manifest_v0"),
        maximum_output_bytes=maximum_output_bytes,
    )
    freeze_path = output / "synthetic_prediction_freeze.v0.json"
    target_blind = run_target_blind_predictions(
        output_root=output,
        freeze_path=freeze_path,
        implementation_evidence=None,
        implementation_registry=None,
        source_kind="generated_synthetic_fixture",
        maximum_output_bytes=maximum_output_bytes,
        execution_started_monotonic=started,
        upstream_access_counters={
            "real_data_hash_passes": 0,
            "real_edf_semantic_parses": 0,
            "synthetic_run_records": 9,
        },
    )
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    private_predictions = _read_json_once(
        output / PRIVATE_PREDICTIONS_NAME,
        str(freeze["private_prediction_payload_sha256"]),
    )
    sealed = _read_npz_once(output / SEALED_TARGET_NAME, extraction.report[
        "sealed_scorer_input"
    ]["sha256"])
    prediction = _read_npz_once(
        output / PREDICTION_DERIVATIVE_NAME,
        extraction.report["prediction_derivative"]["sha256"],
    )
    scored = score_private_predictions(
        freeze=freeze,
        private_predictions=private_predictions,
        sealed=sealed,
        prediction_derivative=prediction,
        permutation_draws=permutation_draws,
    )
    generated_before_summary = _directory_bytes(output)
    if generated_before_summary > maximum_output_bytes:
        raise WO9Failure("output", "synthetic qualification exceeded its output cap")
    summary = {
        "schema_name": "neurodecodekit.physionet_motor_positive_control_qualification",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_only",
        "source": "generated_arrays_no_real_or_protected_data",
        "synthetic_runs": 9,
        "synthetic_events": 135,
        "selected_family": target_blind["selected_family"],
        "prediction_sets": target_blind["prediction_set_count"],
        "classical_parameter_update_fits": target_blind["operation_counters"][
            "classical_parameter_update_fits"
        ],
        "target_blind_model_inference_runs": target_blind["operation_counters"][
            "target_blind_model_inference_runs"
        ],
        "synthetic_router_verdict": scored["verdict"],
        "runtime_seconds": round(time.monotonic() - started, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
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
    for _ in range(8):
        summary_payload = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode(
            "utf-8"
        )
        generated = generated_before_summary + len(summary_payload)
        if summary["generated_bytes"] == generated:
            break
        summary["generated_bytes"] = generated
    else:
        raise WO9Failure("output", "synthetic output byte measurement did not converge")
    if generated > maximum_output_bytes:
        raise WO9Failure("output", "synthetic qualification exceeded its output cap")
    _write_json_exclusive(output / "qualification_summary.v0.json", summary, 1024 * 1024)
    if _directory_bytes(output) != summary["generated_bytes"]:
        raise WO9Failure("output", "synthetic output byte measurement is not exact")
    return summary
