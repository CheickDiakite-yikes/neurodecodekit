"""Target-firewalled IACKD cue-to-action reversal experiment."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import resource
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from neurodecodekit.datasets import iackd_cue_action_acquisition as acquisition


SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = acquisition.CONTRACT_RELATIVE_PATH
DECISION_RELATIVE_PATH = acquisition.DECISION_RELATIVE_PATH
IMPLEMENTATION_RELATIVE_PATH = acquisition.IMPLEMENTATION_RELATIVE_PATH
CONTRACT_SHA256 = acquisition.CONTRACT_SHA256
DECISION_SHA256 = acquisition.DECISION_SHA256
DECISION_COMMIT = acquisition.DECISION_COMMIT
DECISION_CI_RUN_ID = acquisition.DECISION_CI_RUN_ID
DECISION_BASE_JOB_ID = acquisition.DECISION_BASE_JOB_ID
DECISION_OPTIONAL_JOB_ID = acquisition.DECISION_OPTIONAL_JOB_ID
BUNDLE_RELATIVE_PATH = Path("data/iackd_cue_action_dissociation/raw_v1.0.0")
ACQUISITION_MANIFEST_RELATIVE_PATH = Path(
    ".codex_work/iackd_cue_action_dissociation/acquisition_receipt/acquisition_manifest.v0.json"
)
EXECUTION_ROOT_RELATIVE_PATH = Path(
    ".codex_work/iackd_cue_action_dissociation/execution"
)
FREEZE_RELATIVE_PATH = Path(
    "registries/iackd_cue_action_dissociation_prediction_freeze.v0.json"
)
RESULT_RELATIVE_PATH = Path("registries/iackd_cue_action_dissociation_result.v0.json")
FIT_DERIVATIVE_NAME = "fit_private.v0.npz"
FINAL_DERIVATIVE_NAME = "final_target_free.v0.npz"
SEALED_TARGET_NAME = "sealed_dual_targets.v0.npz"
PRIVATE_PREDICTIONS_NAME = "private_predictions.v0.json"
PHYSIOLOGY_SUMMARY_NAME = "physiology_summary.v0.npz"
EXECUTION_CONSUMED_NAME = "execution_consumed.v0.json"
SCORING_CONSUMED_NAME = "scoring_consumed.v0.json"
CONDITION_IDS = (
    "whole_head_primary",
    "central_C3_C4_Cz",
    "HEOG_VEOG_only",
    "fit_only_EOG_orthogonalized_whole_head",
    "early_half",
    "late_half",
    "pre_window_baseline",
    "event_index_and_timing_only",
    "train_only_no_signal_prior",
    "all_zero_final_EEG_through_primary",
    "fixed_train_label_derangement_seed_6841",
    "one_row_cyclic_final_feature_displacement",
    "fixed_final_only_EEG_channel_permutation_seed_6842",
    "opposite_hand_primary_without_adaptation",
)
FIT_IDS = CONDITION_IDS[:8] + (
    "fixed_train_label_derangement_seed_6841",
    "train_only_no_signal_prior",
)
EEG_CHANNELS = (
    "Fp1",
    "Fp2",
    "F7",
    "F3",
    "Fz",
    "F4",
    "F8",
    "FC5",
    "FC1",
    "FC2",
    "FC6",
    "T7",
    "C3",
    "Cz",
    "C4",
    "T8",
    "CP5",
    "CP1",
    "CP2",
    "CP6",
    "P7",
    "P3",
    "Pz",
    "P4",
    "P8",
    "PO9",
    "O1",
    "Oz",
    "O2",
    "PO10",
    "AF7",
    "AF8",
)
REQUIRED_NON_EEG = ("M1", "M2", "HEOG", "VEOG")
THREAD_ENV_KEYS = acquisition.THREAD_ENV_KEYS


class IACKDRefusal(RuntimeError):
    """A registered precondition failed before consuming an execution."""


class IACKDFailure(RuntimeError):
    """A consumed IACKD stage failed closed."""

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


@dataclass(frozen=True)
class TrialRecord:
    trial_id: str
    event_index: int
    event_55_seconds: float
    event_14_seconds: float
    boundary_seconds: float
    condition: str
    leap_timestamps_seconds: Any
    leap_xyz_mm: Any
    ball_timestamps_seconds: Any
    ball_x_pixels: Any
    ball_move_direct: str


@dataclass(frozen=True)
class RunRecord:
    subject: str
    hand: str
    run: str
    sampling_rate_hz: float
    channel_names: tuple[str, ...]
    channel_types: tuple[str, ...]
    channel_geometry_m: Any
    signal_volts: Any
    trials: tuple[TrialRecord, ...]


@dataclass(frozen=True)
class _EventTrial:
    trial_id: str
    event_index: int
    event_55_seconds: float
    event_14_seconds: float
    boundary_seconds: float
    condition: str | None


@dataclass(frozen=True)
class _StreamGroup:
    trial_id: str
    timestamps: Any
    x: Any
    y: Any | None
    z: Any | None
    condition: str | None
    move_direct: str | None


@dataclass(frozen=True)
class ExtractedRun:
    subject: str
    hand: str
    run: str
    event_ids: Any
    conditions: Any
    whole: Any
    central: Any
    eog: Any
    early: Any
    late: Any
    prewindow: Any
    timing: Any
    physiology: Any
    readiness_traces: Any
    actual_directions: Any
    visual_directions: Any
    motion_guard_milliseconds: Any
    reader_metadata_sha256: str
    exclusion_counts: dict[str, int]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _np():
    try:
        import numpy as np
    except ImportError as exc:
        raise IACKDRefusal("IACKD arrays require NumPy") from exc
    return np


def _signal():
    try:
        from scipy import signal
    except ImportError as exc:
        raise IACKDRefusal("IACKD causal filters require SciPy") from exc
    return signal


def _lda_class():
    try:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    except ImportError as exc:
        raise IACKDRefusal("IACKD fitting requires scikit-learn") from exc
    return LinearDiscriminantAnalysis


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _canonical_sha256(value: Any) -> str:
    return _sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def _array_sha256(value: Any) -> str:
    np = _np()
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(b"|")
    digest.update(json.dumps(list(array.shape), separators=(",", ":")).encode("ascii"))
    digest.update(b"|")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _file_sha256(path: Path) -> str:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDFailure("integrity", f"hash input is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    digest = hashlib.sha256()
    with os.fdopen(descriptor, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _deterministic_npz_bytes(values: Mapping[str, Any]) -> bytes:
    np = _np()
    payload = io.BytesIO()
    with zipfile.ZipFile(
        payload,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as archive:
        for name in sorted(values):
            if not name or "/" in name or "\\" in name:
                raise IACKDFailure("output", f"unsafe NPZ member name: {name!r}")
            member = io.BytesIO()
            np.lib.format.write_array(
                member,
                np.asarray(values[name]),
                allow_pickle=False,
            )
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 0
            info.external_attr = 0o600 << 16
            archive.writestr(info, member.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return payload.getvalue()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if sys.platform == "darwin" else value * 1024


def load_registered_contract(repo_root: str | Path | None = None) -> dict[str, Any]:
    return acquisition.load_registered_contract(repo_root)


def load_registered_decision(repo_root: str | Path | None = None) -> dict[str, Any]:
    return acquisition.load_registered_decision(repo_root)


def dependency_versions() -> dict[str, str]:
    versions = {
        "numpy": metadata.version("numpy"),
        "scipy": metadata.version("scipy"),
        "mne": metadata.version("mne"),
        "scikit_learn": metadata.version("scikit-learn"),
    }
    expected = load_registered_contract()["dependency_contract"]["versions"]
    if versions != expected:
        raise IACKDRefusal(f"optional dependency drift: expected {expected}, got {versions}")
    return versions


def _check_thread_environment(environ: Mapping[str, str]) -> None:
    try:
        acquisition._check_thread_environment(environ)
    except acquisition.IACKDAcquisitionRefusal as exc:
        raise IACKDRefusal(str(exc)) from exc


def registered_plan(repo_root: str | Path | None = None) -> dict[str, Any]:
    """Return the target-free analysis plan without touching local payloads."""

    contract = load_registered_contract(repo_root)
    load_registered_decision(repo_root)
    binding = contract["dataset_binding"]
    return {
        "schema_name": "neurodecodekit.iackd_cue_action_analysis_plan",
        "schema_version": SCHEMA_VERSION,
        "mode": "dry_run_no_local_IACKD_stat_open_hash_parse_target_or_model",
        "participants": binding["participant_ids"],
        "participant_hand_units": binding["participant_hand_unit_count"],
        "BIDS_runs": binding["bids_run_count"],
        "object_count": binding["selected_object_count"],
        "payload_bytes": binding["exact_selected_payload_bytes"],
        "fit_condition": contract["split_contract"]["fit_condition"],
        "sealed_final_condition": contract["split_contract"]["sealed_final_condition"],
        "parameter_update_fits": contract["fit_inventory"]["maximum_parameter_update_fits"],
        "prediction_sets": contract["prediction_inventory"]["required_prediction_sets"],
        "condition_ids": list(CONDITION_IDS),
        "caps": contract["resource_caps"]["analysis_and_scoring"],
        "next_gate": "exact_implementation_commit_and_both_ci_jobs_must_be_green",
        "warnings": [
            "dry_run_only_no_local_IACKD_operation",
            "final_signed_directions_remain_sealed_until_remote_green_freeze",
            "offline_oracle_aligned_causal_in_samples_not_real_time",
            "no_scientific_claim_from_plan_or_fixture",
        ],
    }


def _normalize_channel(value: str) -> str:
    return "".join(character for character in value.upper() if character.isalnum())


def _channel_indices(record: RunRecord) -> tuple[list[int], list[int], list[int]]:
    if len(record.channel_names) != len(record.channel_types):
        raise IACKDFailure("reader", "channel name/type lengths differ")
    normalized_names = [_normalize_channel(name) for name in record.channel_names]
    if any(not name for name in normalized_names) or len(set(normalized_names)) != len(
        normalized_names
    ):
        raise IACKDFailure("reader", "channel names are empty or duplicated")
    eeg = [index for index, kind in enumerate(record.channel_types) if kind.lower() == "eeg"]
    if len(eeg) != 32:
        raise IACKDFailure("reader", "exactly 32 EEG channels are required")
    normalized = {_normalize_channel(name): index for index, name in enumerate(record.channel_names)}
    for required in REQUIRED_NON_EEG:
        if _normalize_channel(required) not in normalized:
            raise IACKDFailure("reader", f"required channel is missing: {required}")
    eog = [normalized[_normalize_channel(name)] for name in ("HEOG", "VEOG")]
    central = []
    for name in ("C3", "C4", "Cz"):
        key = _normalize_channel(name)
        if key not in normalized or normalized[key] not in eeg:
            raise IACKDFailure("reader", f"central EEG channel is missing: {name}")
        central.append(eeg.index(normalized[key]))
    return eeg, eog, central


def _validate_run(record: RunRecord) -> tuple[Any, Any, list[int], list[int], list[int]]:
    np = _np()
    contract = load_registered_contract()
    if record.subject not in contract["dataset_binding"]["participant_ids"]:
        raise IACKDFailure("reader", "participant is outside the registered cohort")
    if record.hand not in contract["dataset_binding"]["moving_hand_entities"]:
        raise IACKDFailure("reader", "moving hand is outside the registered cohort")
    allowed_runs = {"01", "02", "03", "04", "05", "06"}
    if record.run not in allowed_runs:
        raise IACKDFailure("reader", "run is outside the registered geometry")
    if not math.isclose(record.sampling_rate_hz, 1024.0, abs_tol=1e-9):
        raise IACKDFailure("reader", "sampling rate is not 1,024 Hz")
    values = np.asarray(record.signal_volts, dtype="float64")
    geometry = np.asarray(record.channel_geometry_m, dtype="float64")
    if values.ndim != 2 or values.shape[0] != len(record.channel_names):
        raise IACKDFailure("reader", "signal dimensions do not match channels")
    if geometry.shape != (len(record.channel_names), 3):
        raise IACKDFailure("reader", "geometry dimensions do not match channels")
    if not np.isfinite(values).all():
        raise IACKDFailure("reader", "signal contains nonfinite samples")
    if not (np.isfinite(geometry) | np.isnan(geometry)).all():
        raise IACKDFailure("reader", "geometry contains invalid values")
    eeg, eog, central = _channel_indices(record)
    if not np.isfinite(geometry[eeg]).all():
        raise IACKDFailure("reader", "one or more EEG channel positions are unavailable")
    return values, geometry, eeg, eog, central


def _feature_row(values: Any) -> Any:
    np = _np()
    matrix = np.asarray(values, dtype="float64")
    if matrix.ndim != 2 or matrix.shape[1] < 8:
        raise IACKDFailure("feature", "feature window is too short")
    boundaries = np.linspace(0, matrix.shape[1], 5, dtype="int64")
    means = np.stack(
        [matrix[:, boundaries[index] : boundaries[index + 1]].mean(axis=1) for index in range(4)],
        axis=1,
    )
    x = np.linspace(-0.5, 0.5, matrix.shape[1], dtype="float64")
    denominator = float(np.dot(x, x))
    slopes = (matrix @ x / denominator)[:, None]
    return np.concatenate((means, slopes), axis=1).reshape(-1).astype("float32")


def _direction(values: Any, minimum_magnitude: float) -> int:
    np = _np()
    array = np.asarray(values, dtype="float64")
    if array.ndim != 1 or array.size < 10 or not np.isfinite(array).all():
        raise IACKDFailure("target", "trajectory direction input is malformed")
    width = max(1, int(math.ceil(array.size * 0.2)))
    displacement = float(np.median(array[-width:]) - np.median(array[:width]))
    if abs(displacement) < minimum_magnitude:
        raise IACKDFailure("target", "trajectory displacement is below the frozen minimum")
    return int(displacement > 0.0)


def _move_direct(value: str) -> int:
    normalized = "".join(character for character in value.lower() if character.isalnum())
    if normalized in {"right", "r", "1", "positive", "pos", "rightward"} or normalized.endswith(
        "right"
    ):
        return 1
    if normalized in {"left", "l", "0", "negative", "neg", "2", "leftward"} or normalized.endswith(
        "left"
    ):
        return 0
    raise IACKDFailure("target", f"unrecognized move_direct value: {value!r}")


def _motion_onset(trial: TrialRecord) -> tuple[float, float]:
    np = _np()
    times = np.asarray(trial.leap_timestamps_seconds, dtype="float64")
    xyz = np.asarray(trial.leap_xyz_mm, dtype="float64")
    if times.ndim != 1 or xyz.shape != (times.size, 3) or times.size < 8:
        raise IACKDFailure("motion_guard", "Leap trajectory shape is malformed")
    if not np.isfinite(times).all() or not np.isfinite(xyz).all():
        raise IACKDFailure("motion_guard", "Leap trajectory contains nonfinite values")
    deltas = np.diff(times)
    if not np.all(deltas > 0.0):
        raise IACKDFailure("motion_guard", "Leap timestamps are not strictly increasing")
    speed = np.linalg.norm(np.diff(xyz, axis=0), axis=1) / deltas
    speed_times = times[1:]
    baseline = speed[speed_times < trial.event_14_seconds]
    if baseline.size < 3:
        raise IACKDFailure("motion_guard", "Leap baseline is too short")
    median = float(np.median(baseline))
    mad = float(np.median(np.abs(baseline - median)))
    threshold = max(20.0, median + 10.0 * mad)
    candidates = speed_times >= trial.event_14_seconds
    above = (speed >= threshold) & candidates
    persistence = 3
    onset_index = None
    for index in range(0, above.size - persistence + 1):
        if bool(np.all(above[index : index + persistence])):
            onset_index = index
            break
    if onset_index is None:
        raise IACKDFailure("motion_guard", "persistent Leap motion onset is unavailable")
    onset = float(speed_times[onset_index])
    if trial.event_14_seconds > onset - 0.03 + 1e-12:
        raise IACKDFailure("motion_guard", "event 14 violates the 30 ms motion guard")
    stop = min(trial.event_14_seconds, onset - 0.03)
    return stop, (onset - stop) * 1000.0


def _sample_slice(start: float, stop: float, sampling_rate: float, sample_count: int) -> slice:
    first = int(round(start * sampling_rate))
    last = int(round(stop * sampling_rate))
    if first < 0 or last > sample_count or last <= first:
        raise IACKDFailure("window", "requested half-open window is outside the run")
    return slice(first, last)


def extract_run_features(record: RunRecord) -> ExtractedRun:
    """Extract target-firewall-ready causal features from one run in memory."""

    np = _np()
    signal = _signal()
    values, _, eeg_indices, eog_indices, central_indices = _validate_run(record)
    sampling_rate = record.sampling_rate_hz
    eeg = values[eeg_indices]
    eeg = eeg - eeg.mean(axis=0, keepdims=True)
    eog = values[eog_indices]
    low_sos = signal.butter(4, (0.5, 4.0), btype="bandpass", fs=sampling_rate, output="sos")
    filtered_eeg = signal.sosfilt(low_sos, eeg, axis=1)
    filtered_eog = signal.sosfilt(low_sos, eog, axis=1)
    mu_sos = signal.butter(4, (8.0, 13.0), btype="bandpass", fs=sampling_rate, output="sos")
    beta_sos = signal.butter(4, (13.0, 30.0), btype="bandpass", fs=sampling_rate, output="sos")
    central_signal = eeg[central_indices]
    mu = signal.sosfilt(mu_sos, central_signal, axis=1)
    beta = signal.sosfilt(beta_sos, central_signal, axis=1)
    rows = {
        key: []
        for key in (
            "event_ids",
            "conditions",
            "whole",
            "central",
            "eog",
            "early",
            "late",
            "prewindow",
            "timing",
            "physiology",
            "readiness",
            "actual",
            "visual",
            "guard",
        )
    }
    exclusions: dict[str, int] = {}

    def exclude(reason: str) -> None:
        exclusions[reason] = exclusions.get(reason, 0) + 1

    for trial in record.trials:
        try:
            if not (
                trial.event_55_seconds < trial.event_14_seconds < trial.boundary_seconds
            ):
                raise IACKDFailure("marker", "trial marker order is not 55, 14, boundary")
            condition = trial.condition.strip().lower()
            if condition not in {"red", "yellow"}:
                raise IACKDFailure("trial", "condition is neither red nor yellow")
            stop, guard_ms = _motion_onset(trial)
            main_slice = _sample_slice(stop - 1.0, stop, sampling_rate, values.shape[1])
            early_slice = _sample_slice(stop - 1.0, stop - 0.5, sampling_rate, values.shape[1])
            late_slice = _sample_slice(stop - 0.5, stop, sampling_rate, values.shape[1])
            pre_slice = _sample_slice(stop - 2.0, stop - 1.0, sampling_rate, values.shape[1])
            leap_x = np.asarray(trial.leap_xyz_mm, dtype="float64")[:, 0]
            actual = _direction(leap_x, 5.0)
            visual = _direction(trial.ball_x_pixels, 5.0)
            if _move_direct(trial.ball_move_direct) != visual:
                raise IACKDFailure("target", "ball move_direct disagrees with displacement")
            if condition == "red" and actual != visual:
                raise IACKDFailure("target", "red trial directions are not congruent")
            if condition == "yellow" and actual == visual:
                raise IACKDFailure("target", "yellow trial directions are not opposite")
            main = filtered_eeg[:, main_slice]
            rows["event_ids"].append(
                f"{record.subject}-{record.hand}-{record.run}-{trial.trial_id}"
            )
            rows["conditions"].append(condition)
            rows["whole"].append(_feature_row(main))
            rows["central"].append(_feature_row(main[central_indices]))
            rows["eog"].append(_feature_row(filtered_eog[:, main_slice]))
            rows["early"].append(_feature_row(filtered_eeg[:, early_slice]))
            rows["late"].append(_feature_row(filtered_eeg[:, late_slice]))
            rows["prewindow"].append(_feature_row(filtered_eeg[:, pre_slice]))
            rows["timing"].append(
                np.asarray(
                    [
                        float(trial.event_index),
                        trial.event_14_seconds - trial.event_55_seconds,
                        trial.boundary_seconds - trial.event_14_seconds,
                        guard_ms / 1000.0,
                    ],
                    dtype="float32",
                )
            )
            central_window = main[central_indices]
            rows["physiology"].append(
                np.asarray(
                    [
                        *central_window.mean(axis=1),
                        float(np.mean(mu[:, main_slice] ** 2)),
                        float(np.mean(beta[:, main_slice] ** 2)),
                        float(central_window[:, : central_window.shape[1] // 2].mean()),
                        float(central_window[:, central_window.shape[1] // 2 :].mean()),
                    ],
                    dtype="float32",
                )
            )
            rows["readiness"].append(central_window.astype("float32", copy=True))
            rows["actual"].append(actual)
            rows["visual"].append(visual)
            rows["guard"].append(guard_ms)
        except IACKDFailure as exc:
            if exc.stage == "target":
                raise
            exclude(exc.stage)
    if not rows["event_ids"]:
        raise IACKDFailure("trial", "run retained no valid trials")
    stack = lambda values, dtype: np.asarray(values, dtype=dtype)  # noqa: E731
    return ExtractedRun(
        subject=record.subject,
        hand=record.hand,
        run=record.run,
        event_ids=stack(rows["event_ids"], "U96"),
        conditions=stack(rows["conditions"], "U8"),
        whole=np.stack(rows["whole"]).astype("float32"),
        central=np.stack(rows["central"]).astype("float32"),
        eog=np.stack(rows["eog"]).astype("float32"),
        early=np.stack(rows["early"]).astype("float32"),
        late=np.stack(rows["late"]).astype("float32"),
        prewindow=np.stack(rows["prewindow"]).astype("float32"),
        timing=np.stack(rows["timing"]).astype("float32"),
        physiology=np.stack(rows["physiology"]).astype("float32"),
        readiness_traces=np.stack(rows["readiness"]).astype("float32"),
        actual_directions=stack(rows["actual"], "int8"),
        visual_directions=stack(rows["visual"], "int8"),
        motion_guard_milliseconds=stack(rows["guard"], "float32"),
        reader_metadata_sha256=_canonical_sha256(
            {
                "channel_names": list(record.channel_names),
                "channel_types": list(record.channel_types),
                "geometry_sha256": _array_sha256(record.channel_geometry_m),
                "sampling_rate_hz": record.sampling_rate_hz,
            }
        ),
        exclusion_counts=exclusions,
    )


def _split_kind(subject: str, run: str) -> str:
    if subject in {"sub-04", "sub-05"}:
        if run in {"01", "02", "03", "04", "05"}:
            return "fit"
        if run == "06":
            return "final"
    else:
        if run in {"01", "02", "03"}:
            return "fit"
        if run == "04":
            return "final"
    raise IACKDFailure("split", f"run is outside the frozen split: {subject}/{run}")


def _unit(subject: str, hand: str) -> str:
    return f"{subject}|{hand}"


def _append_rows(destination: dict[str, list[Any]], extracted: ExtractedRun, mask: Any) -> None:
    np = _np()
    count = int(np.count_nonzero(mask))
    if count == 0:
        return
    destination["event_ids"].extend(extracted.event_ids[mask].tolist())
    destination["subjects"].extend([extracted.subject] * count)
    destination["hands"].extend([extracted.hand] * count)
    destination["runs"].extend([extracted.run] * count)
    destination["conditions"].extend(extracted.conditions[mask].tolist())
    for key in ("whole", "central", "eog", "early", "late", "prewindow", "timing", "physiology"):
        destination[key].extend(getattr(extracted, key)[mask])
    destination["actual"].extend(extracted.actual_directions[mask].tolist())
    destination["visual"].extend(extracted.visual_directions[mask].tolist())
    destination["guard"].extend(extracted.motion_guard_milliseconds[mask].tolist())


def _empty_rows() -> dict[str, list[Any]]:
    return {
        key: []
        for key in (
            "event_ids",
            "subjects",
            "hands",
            "runs",
            "conditions",
            "whole",
            "central",
            "eog",
            "early",
            "late",
            "prewindow",
            "timing",
            "physiology",
            "actual",
            "visual",
            "guard",
        )
    }


def _array_rows(rows: Mapping[str, list[Any]], *, include_targets: bool) -> dict[str, Any]:
    np = _np()
    condition_ids = [
        "congruent" if value == "red" else "incongruent" if value == "yellow" else "invalid"
        for value in rows["conditions"]
    ]
    if "invalid" in condition_ids:
        raise IACKDFailure("split", "derivative contains an unknown condition")
    value = {
        "event_ids": np.asarray(rows["event_ids"], dtype="U96"),
        "subjects": np.asarray(rows["subjects"], dtype="U8"),
        "hands": np.asarray(rows["hands"], dtype="U5"),
        "runs": np.asarray(rows["runs"], dtype="U2"),
        "condition_ids": np.asarray(condition_ids, dtype="U12"),
        "whole_features": np.asarray(rows["whole"], dtype="float32"),
        "central_features": np.asarray(rows["central"], dtype="float32"),
        "eog_features": np.asarray(rows["eog"], dtype="float32"),
        "early_features": np.asarray(rows["early"], dtype="float32"),
        "late_features": np.asarray(rows["late"], dtype="float32"),
        "prewindow_features": np.asarray(rows["prewindow"], dtype="float32"),
        "timing_features": np.asarray(rows["timing"], dtype="float32"),
        "physiology": np.asarray(rows["physiology"], dtype="float32"),
        "motion_guard_milliseconds": np.asarray(rows["guard"], dtype="float32"),
    }
    if include_targets:
        value["fit_labels"] = np.asarray(rows["actual"], dtype="int8")
    return value


def _sealed_rows(rows: Mapping[str, list[Any]]) -> dict[str, Any]:
    np = _np()
    return {
        "event_ids": np.asarray(rows["event_ids"], dtype="U96"),
        "subjects": np.asarray(rows["subjects"], dtype="U8"),
        "hands": np.asarray(rows["hands"], dtype="U5"),
        "runs": np.asarray(rows["runs"], dtype="U2"),
        "actual_hand_directions": np.asarray(rows["actual"], dtype="int8"),
        "visual_target_directions": np.asarray(rows["visual"], dtype="int8"),
    }


def _write_npz_exclusive(path: Path, values: Mapping[str, Any], cap: int) -> int:
    payload = _deterministic_npz_bytes(values)
    if len(payload) > cap:
        raise IACKDFailure("output", f"NPZ exceeds output cap: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise IACKDRefusal(f"refusing to replace output: {path}") from None
    return len(payload)


def _write_json_exclusive(path: Path, value: Mapping[str, Any], cap: int) -> int:
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if len(payload) > cap:
        raise IACKDFailure("output", f"JSON exceeds output cap: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as handle:
            handle.write(payload)
    except FileExistsError:
        raise IACKDRefusal(f"refusing to replace output: {path}") from None
    return len(payload)


def _load_npz(path: Path, *, target_free: bool = False) -> dict[str, Any]:
    np = _np()
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDFailure("integrity", f"NPZ input is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        with np.load(handle, allow_pickle=False) as archive:
            values = {key: archive[key] for key in archive.files}
    if target_free:
        forbidden = ("target", "label", "direction", "signed", "prediction", "probability")
        leaked = [key for key in values if any(token in key.lower() for token in forbidden)]
        if leaked:
            raise IACKDFailure("firewall", f"target-free derivative leaks keys: {leaked}")
    return values


def _directory_bytes(path: Path) -> int:
    total = 0
    for root, directories, filenames in os.walk(path, followlinks=False):
        current = Path(root)
        if any((current / name).is_symlink() for name in directories):
            raise IACKDFailure("output", "output contains symlink directory")
        for filename in filenames:
            candidate = current / filename
            if candidate.is_symlink():
                raise IACKDFailure("output", "output contains symlink file")
            total += candidate.stat().st_size
    return total


def _validate_unit_counts(fit: Mapping[str, Any], final: Mapping[str, Any]) -> None:
    np = _np()
    contract = load_registered_contract()
    participants = contract["dataset_binding"]["participant_ids"]
    for subject in participants:
        for hand in ("left", "right"):
            fit_mask = (fit["subjects"] == subject) & (fit["hands"] == hand)
            final_mask = (final["subjects"] == subject) & (final["hands"] == hand)
            for label in (0, 1):
                if int(np.count_nonzero(fit_mask & (fit["fit_labels"] == label))) < 24:
                    raise IACKDFailure("minimum_count", f"fit minimum failed: {subject}/{hand}")
            if int(np.count_nonzero(final_mask)) < 16:
                raise IACKDFailure("minimum_count", f"final minimum failed: {subject}/{hand}")
            if "actual" in final:
                for label in (0, 1):
                    if int(np.count_nonzero(final_mask & (final["actual"] == label))) < 8:
                        raise IACKDFailure(
                            "minimum_count", f"final class minimum failed: {subject}/{hand}"
                        )
    units = {_unit(str(subject), str(hand)) for subject, hand in zip(final["subjects"], final["hands"], strict=True)}
    if len(units) != 30:
        raise IACKDFailure("minimum_count", "all 30 participant-hand units are required")


def extract_records_to_derivatives(
    records: Iterable[RunRecord],
    output_root: str | Path,
    *,
    source_hashes: Mapping[str, str],
    manifest_sha256: str,
    maximum_output_bytes: int,
    allow_existing_consumed_marker: bool = False,
) -> dict[str, Any]:
    """Stream run records into fit, target-free final, and sealed derivatives."""

    np = _np()
    if maximum_output_bytes <= 0 or maximum_output_bytes > 512 * 1024 * 1024:
        raise IACKDRefusal("derivative output cap must be within 1 byte and 512 MiB")
    output = Path(output_root)
    if output.exists():
        allowed = allow_existing_consumed_marker and sorted(path.name for path in output.iterdir()) == [
            EXECUTION_CONSUMED_NAME
        ]
        if not allowed:
            raise IACKDRefusal(f"exclusive derivative root already exists: {output}")
    else:
        output.mkdir(parents=True, exist_ok=False)
    fit_rows = _empty_rows()
    final_rows = _empty_rows()
    run_count = 0
    exclusions: dict[str, int] = {}
    seen_runs: set[tuple[str, str, str]] = set()
    reader_metadata_hashes: dict[str, str] = {}
    readiness_sums: dict[str, Any] = {}
    physiology_sums: dict[str, Any] = {}
    guard_values: dict[str, list[float]] = {}
    physiology_counts: dict[str, int] = {}
    for record in records:
        identity = (record.subject, record.hand, record.run)
        if identity in seen_runs:
            raise IACKDFailure("split", f"duplicate run record: {identity}")
        seen_runs.add(identity)
        extracted = extract_run_features(record)
        run_key = "/".join(identity)
        reader_metadata_hashes[run_key] = extracted.reader_metadata_sha256
        split = _split_kind(record.subject, record.run)
        if split == "fit":
            mask = extracted.conditions == "red"
            _append_rows(fit_rows, extracted, mask)
        else:
            mask = extracted.conditions == "yellow"
            _append_rows(final_rows, extracted, mask)
            count = int(np.count_nonzero(mask))
            if count:
                unit = _unit(record.subject, record.hand)
                readiness_sums[unit] = readiness_sums.get(
                    unit,
                    np.zeros_like(extracted.readiness_traces[0], dtype="float64"),
                ) + extracted.readiness_traces[mask].astype("float64").sum(axis=0)
                physiology_sums[unit] = physiology_sums.get(
                    unit,
                    np.zeros(extracted.physiology.shape[1], dtype="float64"),
                ) + extracted.physiology[mask].astype("float64").sum(axis=0)
                guard_values.setdefault(unit, []).extend(
                    extracted.motion_guard_milliseconds[mask].astype(float).tolist()
                )
                physiology_counts[unit] = physiology_counts.get(unit, 0) + count
        for reason, count in extracted.exclusion_counts.items():
            exclusions[reason] = exclusions.get(reason, 0) + count
        run_count += 1
    if run_count != 128:
        raise IACKDFailure("split", f"exactly 128 run records are required, got {run_count}")
    fit = _array_rows(fit_rows, include_targets=True)
    final = _array_rows(final_rows, include_targets=False)
    sealed = _sealed_rows(final_rows)
    contract = load_registered_contract()
    source_hashes_sha256 = _canonical_sha256(dict(sorted(source_hashes.items())))
    split_protocol_sha256 = _canonical_sha256(contract["split_contract"])
    feature_configuration_sha256 = _canonical_sha256(
        {
            "reader_contract": contract["reader_contract"],
            "kinematic_guard": contract["kinematic_guard"],
            "primary_model": contract["primary_model"],
            "EOG_projection": contract["EOG_projection"],
            "fit_inventory": contract["fit_inventory"],
            "prediction_inventory": contract["prediction_inventory"],
        }
    )
    reader_metadata_sha256 = _canonical_sha256(dict(sorted(reader_metadata_hashes.items())))
    provenance = {
        "source_manifest_sha256": manifest_sha256,
        "source_hashes_sha256": source_hashes_sha256,
        "split_protocol_sha256": split_protocol_sha256,
        "feature_configuration_sha256": feature_configuration_sha256,
        "reader_metadata_sha256": reader_metadata_sha256,
    }
    for values in (fit, final):
        values.update({key: np.asarray(value, dtype="U64") for key, value in provenance.items()})
    _validate_unit_counts(fit, {**final, "actual": np.asarray(final_rows["actual"], dtype="int8")})
    if not np.all(fit["condition_ids"] == "congruent"):
        raise IACKDFailure("split", "fit derivative contains a non-congruent row")
    if not np.all(final["condition_ids"] == "incongruent"):
        raise IACKDFailure("split", "final derivative contains a non-incongruent row")
    if not np.array_equal(sealed["event_ids"], final["event_ids"]):
        raise IACKDFailure("firewall", "sealed and target-free final identities differ")
    if not np.all(sealed["actual_hand_directions"] != sealed["visual_target_directions"]):
        raise IACKDFailure("firewall", "final target views are not exact opposites")
    fit_path = output / FIT_DERIVATIVE_NAME
    final_path = output / FINAL_DERIVATIVE_NAME
    sealed_path = output / SEALED_TARGET_NAME
    physiology_path = output / PHYSIOLOGY_SUMMARY_NAME
    _write_npz_exclusive(fit_path, fit, maximum_output_bytes)
    _write_npz_exclusive(final_path, final, maximum_output_bytes)
    _write_npz_exclusive(sealed_path, sealed, maximum_output_bytes)
    unit_order = [
        _unit(subject, hand)
        for subject in contract["dataset_binding"]["participant_ids"]
        for hand in ("left", "right")
    ]
    if set(physiology_counts) != set(unit_order):
        raise IACKDFailure("physiology", "physiology summary lacks a participant-hand unit")
    physiology_summary = {
        "unit_ids": np.asarray(unit_order, dtype="U16"),
        "readiness_mean_C3_C4_Cz": np.stack(
            [readiness_sums[unit] / physiology_counts[unit] for unit in unit_order]
        ).astype("float32"),
        "mu_beta_and_early_late_summary": np.stack(
            [physiology_sums[unit] / physiology_counts[unit] for unit in unit_order]
        ).astype("float32"),
        "motion_guard_min_mean_max_milliseconds": np.asarray(
            [
                [min(guard_values[unit]), sum(guard_values[unit]) / len(guard_values[unit]), max(guard_values[unit])]
                for unit in unit_order
            ],
            dtype="float32",
        ),
        "trial_counts": np.asarray([physiology_counts[unit] for unit in unit_order], dtype="int32"),
        **{key: np.asarray(value, dtype="U64") for key, value in provenance.items()},
    }
    _write_npz_exclusive(physiology_path, physiology_summary, maximum_output_bytes)
    _load_npz(final_path, target_free=True)
    reloaded_physiology = _load_npz(physiology_path, target_free=True)
    if reloaded_physiology["readiness_mean_C3_C4_Cz"].shape != (30, 3, 1024):
        raise IACKDFailure("physiology", "readiness-potential trace inventory is incomplete")
    summary = {
        "schema_name": "neurodecodekit.iackd_derivative_summary",
        "schema_version": SCHEMA_VERSION,
        "run_count": run_count,
        "fit_rows": int(fit["event_ids"].size),
        "final_rows": int(final["event_ids"].size),
        "participant_hand_units": 30,
        "source_file_count": len(source_hashes),
        "source_hashes_sha256": source_hashes_sha256,
        "source_manifest_sha256": manifest_sha256,
        "split_protocol_sha256": split_protocol_sha256,
        "feature_configuration_sha256": feature_configuration_sha256,
        "reader_metadata_sha256": reader_metadata_sha256,
        "fit_derivative_sha256": _file_sha256(fit_path),
        "prediction_derivative_sha256": _file_sha256(final_path),
        "sealed_target_sha256": _file_sha256(sealed_path),
        "physiology_summary_sha256": _file_sha256(physiology_path),
        "physiology_content_sha256": _canonical_sha256(
            {key: _array_sha256(value) for key, value in sorted(physiology_summary.items())}
        ),
        "readiness_trace_shape": [30, 3, 1024],
        "target_free_final_keys": sorted(final),
        "fit_target_rows_available_to_fit_stage": int(fit["fit_labels"].size),
        "final_target_rows_available_to_model_stage": 0,
        "target_views_in_sealed_scorer_input": 2,
        "aggregate_exclusion_counts": dict(sorted(exclusions.items())),
        "motion_guard_minimum_milliseconds": float(final["motion_guard_milliseconds"].min()),
    }
    _write_json_exclusive(output / "derivative_summary.v0.json", summary, 2 * 1024 * 1024)
    if _directory_bytes(output) > maximum_output_bytes:
        raise IACKDFailure("output", "private derivatives exceed output cap")
    return summary


class _Prior:
    def __init__(self, value: int) -> None:
        self.value = int(value)

    def predict(self, values: Any) -> Any:
        np = _np()
        return np.full(len(values), self.value, dtype="int8")


def _fit_lda(values: Any, labels: Any):
    np = _np()
    matrix = np.asarray(values, dtype="float64")
    targets = np.asarray(labels, dtype="int8")
    if matrix.ndim != 2 or matrix.shape[0] != targets.size:
        raise IACKDFailure("model", "fit feature/target dimensions differ")
    if set(np.unique(targets).tolist()) != {0, 1}:
        raise IACKDFailure("model", "both fit classes are required")
    model = _lda_class()(solver="lsqr", shrinkage=0.1, priors=np.asarray([0.5, 0.5]))
    model.fit(matrix, targets)
    return model


def _fit_prior(labels: Any) -> _Prior:
    np = _np()
    counts = np.bincount(np.asarray(labels, dtype="int8"), minlength=2)
    return _Prior(int(counts[1] > counts[0]))


def _eog_residuals(
    fit_eeg: Any,
    final_eeg: Any,
    fit_eog: Any,
    final_eog: Any,
) -> tuple[Any, Any]:
    np = _np()
    fit_design = np.column_stack((np.ones(len(fit_eog)), fit_eog)).astype("float64")
    final_design = np.column_stack((np.ones(len(final_eog)), final_eog)).astype("float64")
    penalty = np.eye(fit_design.shape[1], dtype="float64") * 0.001
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        fit_design.T @ fit_design + penalty,
        fit_design.T @ np.asarray(fit_eeg, dtype="float64"),
    )
    return (
        np.asarray(fit_eeg, dtype="float64") - fit_design @ coefficients,
        np.asarray(final_eeg, dtype="float64") - final_design @ coefficients,
    )


def _prediction_sha256(values: Sequence[int]) -> str:
    return _sha256_bytes(bytes(int(value) for value in values))


def _predict(model: Any, values: Any) -> list[int]:
    np = _np()
    predictions = np.asarray(model.predict(values), dtype="int8")
    if predictions.ndim != 1 or not set(np.unique(predictions).tolist()).issubset({0, 1}):
        raise IACKDFailure("model", "predictions are not binary")
    return [int(value) for value in predictions]


def validate_public_freeze(freeze: Mapping[str, Any]) -> None:
    required_keys = {
        "schema_name",
        "schema_version",
        "status",
        "proof_posture",
        "contract_sha256",
        "authorization_decision_sha256",
        "source_kind",
        "source_manifest_sha256",
        "source_file_count",
        "source_payload_bytes",
        "source_hashes_sha256",
        "reader_metadata_sha256",
        "split_protocol_sha256",
        "feature_configuration_sha256",
        "condition_ids",
        "participant_hand_units",
        "prediction_set_sha256",
        "canonical_private_prediction_sha256",
        "private_prediction_payload_sha256",
        "private_prediction_payload_bytes",
        "fit_derivative_sha256",
        "prediction_derivative_sha256",
        "sealed_target_sha256",
        "physiology_summary_sha256",
        "physiology_content_sha256",
        "quality_summary_sha256",
        "dependency_versions",
        "operation_counters",
        "target_firewall_summary",
        "target_firewall_sha256",
        "upstream_access_counters",
        "resources",
        "implementation_commit",
        "implementation_ci_run_id",
        "implementation_base_python_job_id",
        "implementation_optional_neuro_job_id",
        "implementation_registry_sha256",
        "implementation_tracked_file_hashes_sha256",
        "warnings",
        "freeze_record_sha256",
    }
    if set(freeze) != required_keys:
        raise IACKDFailure("freeze", "prediction freeze fields differ from the strict schema")
    if freeze.get("schema_name") != "neurodecodekit.iackd_prediction_freeze":
        raise IACKDFailure("freeze", "prediction freeze schema mismatch")
    if freeze.get("schema_version") != SCHEMA_VERSION:
        raise IACKDFailure("freeze", "prediction freeze version mismatch")
    if freeze.get("status") != "target_blind_predictions_frozen":
        raise IACKDFailure("freeze", "prediction freeze status mismatch")
    if freeze.get("contract_sha256") != CONTRACT_SHA256:
        raise IACKDFailure("freeze", "prediction freeze contract mismatch")
    if freeze.get("authorization_decision_sha256") != DECISION_SHA256:
        raise IACKDFailure("freeze", "prediction freeze decision mismatch")
    if freeze.get("source_kind") not in {"generated_synthetic_fixture", "real_IACKD"}:
        raise IACKDFailure("freeze", "prediction freeze source kind is invalid")
    if tuple(freeze.get("condition_ids", ())) != CONDITION_IDS:
        raise IACKDFailure("freeze", "prediction condition inventory mismatch")
    if freeze.get("participant_hand_units") != 30:
        raise IACKDFailure("freeze", "prediction freeze unit count mismatch")
    counters = freeze.get("operation_counters", {})
    expected = {
        "parameter_update_fits": 300,
        "target_blind_model_inference_calls": 420,
        "participant_condition_prediction_sets": 420,
        "final_target_rows_available_to_model_stage": 0,
        "target_deliveries": 0,
        "scoring_events": 0,
        "post_target_updates": 0,
    }
    if counters != expected:
        raise IACKDFailure("freeze", "prediction operation counters mismatch")
    hashes = freeze.get("prediction_set_sha256")
    expected_units = {
        _unit(subject, hand)
        for subject in load_registered_contract()["dataset_binding"]["participant_ids"]
        for hand in ("left", "right")
    }
    if not isinstance(hashes, Mapping) or set(hashes) != set(CONDITION_IDS):
        raise IACKDFailure("freeze", "prediction hash condition inventory mismatch")
    for condition in CONDITION_IDS:
        unit_hashes = hashes[condition]
        if not isinstance(unit_hashes, Mapping) or set(unit_hashes) != expected_units:
            raise IACKDFailure("freeze", f"prediction hash unit inventory mismatch: {condition}")
        if not all(_is_sha256(value) for value in unit_hashes.values()):
            raise IACKDFailure("freeze", f"prediction hash is malformed: {condition}")
    hash_fields = (
        "source_manifest_sha256",
        "source_hashes_sha256",
        "reader_metadata_sha256",
        "split_protocol_sha256",
        "feature_configuration_sha256",
        "canonical_private_prediction_sha256",
        "private_prediction_payload_sha256",
        "fit_derivative_sha256",
        "prediction_derivative_sha256",
        "sealed_target_sha256",
        "physiology_summary_sha256",
        "physiology_content_sha256",
        "quality_summary_sha256",
        "target_firewall_sha256",
    )
    if not all(_is_sha256(freeze.get(key)) for key in hash_fields):
        raise IACKDFailure("freeze", "prediction freeze contains a malformed hash")
    firewall = freeze.get("target_firewall_summary")
    expected_firewall_keys = {
        "final_target_rows_available_to_model_stage",
        "sealed_target_file_content_reads",
        "signed_trajectory_values_available_to_model_stage",
        "prediction_derivative_contains_targets",
        "both_final_target_sets_frozen_together",
        "target_free_final_keys",
    }
    if not isinstance(firewall, Mapping) or set(firewall) != expected_firewall_keys:
        raise IACKDFailure("freeze", "target firewall summary fields mismatch")
    if any(
        firewall[key] != 0
        for key in (
            "final_target_rows_available_to_model_stage",
            "sealed_target_file_content_reads",
            "signed_trajectory_values_available_to_model_stage",
        )
    ):
        raise IACKDFailure("freeze", "target firewall reports protected model-stage access")
    if firewall["prediction_derivative_contains_targets"] is not False:
        raise IACKDFailure("freeze", "prediction derivative target firewall failed")
    if firewall["both_final_target_sets_frozen_together"] is not True:
        raise IACKDFailure("freeze", "dual-target freeze binding failed")
    if freeze["target_firewall_sha256"] != _canonical_sha256(firewall):
        raise IACKDFailure("freeze", "target firewall hash mismatch")
    real = freeze["source_kind"] == "real_IACKD"
    implementation_fields = (
        freeze["implementation_commit"],
        freeze["implementation_ci_run_id"],
        freeze["implementation_base_python_job_id"],
        freeze["implementation_optional_neuro_job_id"],
        freeze["implementation_registry_sha256"],
        freeze["implementation_tracked_file_hashes_sha256"],
    )
    if real:
        if not isinstance(implementation_fields[0], str) or not re.fullmatch(
            r"[0-9a-f]{40}", implementation_fields[0]
        ):
            raise IACKDFailure("freeze", "real freeze implementation commit is malformed")
        if not all(isinstance(value, int) and value > 0 for value in implementation_fields[1:4]):
            raise IACKDFailure("freeze", "real freeze implementation CI evidence is malformed")
        if not all(_is_sha256(value) for value in implementation_fields[4:]):
            raise IACKDFailure("freeze", "real freeze implementation hashes are malformed")
        if freeze["source_file_count"] != 1340 or freeze["source_payload_bytes"] != 7249113684:
            raise IACKDFailure("freeze", "real freeze source inventory mismatch")
    elif any(value is not None for value in implementation_fields):
        raise IACKDFailure("freeze", "synthetic freeze contains real implementation evidence")
    forbidden = {
        "predictions",
        "probabilities",
        "targets",
        "actual_hand_directions",
        "visual_target_directions",
        "participant_outcomes",
        "signed_trajectories",
    }

    def keys(value: Any) -> set[str]:
        observed = set()
        if isinstance(value, Mapping):
            for key, nested in value.items():
                observed.add(str(key))
                observed.update(keys(nested))
        elif isinstance(value, list):
            for nested in value:
                observed.update(keys(nested))
        return observed

    if forbidden.intersection(keys(freeze)):
        raise IACKDFailure("freeze", "public freeze contains individual protected output")
    record = dict(freeze)
    observed_hash = record.pop("freeze_record_sha256", None)
    if observed_hash != _canonical_sha256(record):
        raise IACKDFailure("freeze", "prediction freeze record hash mismatch")


def run_target_blind_predictions(
    *,
    output_root: str | Path,
    freeze_path: str | Path,
    source_kind: str,
    maximum_output_bytes: int,
    implementation_evidence: ImplementationEvidence | None = None,
    implementation_registry: Mapping[str, Any] | None = None,
    execution_started_monotonic: float | None = None,
    upstream_access_counters: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    """Fit the exact 300 models and freeze 420 target-blind prediction sets."""

    np = _np()
    dependency_versions()
    output = Path(output_root)
    freeze_output = Path(freeze_path)
    fit_path = output / FIT_DERIVATIVE_NAME
    final_path = output / FINAL_DERIVATIVE_NAME
    physiology_path = output / PHYSIOLOGY_SUMMARY_NAME
    derivative_summary_path = output / "derivative_summary.v0.json"
    private_path = output / PRIVATE_PREDICTIONS_NAME
    if private_path.exists() or freeze_output.exists():
        raise IACKDRefusal("prediction output already exists")
    derivative_summary = _read_json_nofollow(derivative_summary_path, 2 * 1024 * 1024)
    if derivative_summary.get("schema_name") != "neurodecodekit.iackd_derivative_summary":
        raise IACKDFailure("integrity", "derivative summary schema mismatch")
    bound_files = {
        "fit_derivative_sha256": fit_path,
        "prediction_derivative_sha256": final_path,
        "physiology_summary_sha256": physiology_path,
    }
    for key, path in bound_files.items():
        if _file_sha256(path) != derivative_summary.get(key):
            raise IACKDFailure("integrity", f"derivative summary hash mismatch: {key}")
    fit = _load_npz(fit_path)
    final = _load_npz(final_path, target_free=True)
    physiology = _load_npz(physiology_path, target_free=True)
    _validate_unit_counts(fit, final)
    if physiology["readiness_mean_C3_C4_Cz"].shape != (30, 3, 1024):
        raise IACKDFailure("physiology", "readiness-potential trace inventory is incomplete")
    for key in (
        "source_manifest_sha256",
        "source_hashes_sha256",
        "split_protocol_sha256",
        "feature_configuration_sha256",
        "reader_metadata_sha256",
    ):
        if str(final[key].item()) != derivative_summary.get(key):
            raise IACKDFailure("integrity", f"final provenance mismatch: {key}")
    participants = load_registered_contract()["dataset_binding"]["participant_ids"]
    models: dict[str, Any] = {}
    final_primary: dict[str, Any] = {}
    event_ids: dict[str, list[str]] = {}
    predictions = {condition: {} for condition in CONDITION_IDS}
    fit_count = 0
    prediction_count = 0
    for subject in participants:
        for hand in ("left", "right"):
            unit = _unit(subject, hand)
            fit_mask = (fit["subjects"] == subject) & (fit["hands"] == hand)
            final_mask = (final["subjects"] == subject) & (final["hands"] == hand)
            y = fit["fit_labels"][fit_mask]
            fit_whole = fit["whole_features"][fit_mask]
            final_whole = final["whole_features"][final_mask]
            fit_eog_residual, final_eog_residual = _eog_residuals(
                fit_whole,
                final_whole,
                fit["eog_features"][fit_mask],
                final["eog_features"][final_mask],
            )
            feature_pairs = {
                "whole_head_primary": (fit_whole, final_whole),
                "central_C3_C4_Cz": (
                    fit["central_features"][fit_mask],
                    final["central_features"][final_mask],
                ),
                "HEOG_VEOG_only": (
                    fit["eog_features"][fit_mask],
                    final["eog_features"][final_mask],
                ),
                "fit_only_EOG_orthogonalized_whole_head": (
                    fit_eog_residual,
                    final_eog_residual,
                ),
                "early_half": (
                    fit["early_features"][fit_mask],
                    final["early_features"][final_mask],
                ),
                "late_half": (
                    fit["late_features"][fit_mask],
                    final["late_features"][final_mask],
                ),
                "pre_window_baseline": (
                    fit["prewindow_features"][fit_mask],
                    final["prewindow_features"][final_mask],
                ),
                "event_index_and_timing_only": (
                    fit["timing_features"][fit_mask],
                    final["timing_features"][final_mask],
                ),
            }
            fitted = {}
            for condition, (fit_values, final_values) in feature_pairs.items():
                model = _fit_lda(fit_values, y)
                fitted[condition] = model
                predictions[condition][unit] = _predict(model, final_values)
                fit_count += 1
                prediction_count += 1
            rng = np.random.default_rng(6841)
            deranged = np.asarray(y, dtype="int8").copy()
            rng.shuffle(deranged)
            deranged_model = _fit_lda(fit_whole, deranged)
            predictions["fixed_train_label_derangement_seed_6841"][unit] = _predict(
                deranged_model, final_whole
            )
            fit_count += 1
            prediction_count += 1
            prior = _fit_prior(y)
            predictions["train_only_no_signal_prior"][unit] = _predict(prior, final_whole)
            fit_count += 1
            prediction_count += 1
            primary = fitted["whole_head_primary"]
            predictions["all_zero_final_EEG_through_primary"][unit] = _predict(
                primary, np.zeros_like(final_whole)
            )
            prediction_count += 1
            predictions["one_row_cyclic_final_feature_displacement"][unit] = _predict(
                primary, np.roll(final_whole, 1, axis=0)
            )
            prediction_count += 1
            permutation = np.random.default_rng(6842).permutation(32)
            permuted = final_whole.reshape(len(final_whole), 32, 5)[:, permutation, :].reshape(
                len(final_whole), 160
            )
            predictions["fixed_final_only_EEG_channel_permutation_seed_6842"][unit] = _predict(
                primary, permuted
            )
            prediction_count += 1
            models[unit] = primary
            final_primary[unit] = final_whole
            event_ids[unit] = [str(value) for value in final["event_ids"][final_mask]]
    for subject in participants:
        for hand, opposite in (("left", "right"), ("right", "left")):
            unit = _unit(subject, hand)
            predictions["opposite_hand_primary_without_adaptation"][unit] = _predict(
                models[_unit(subject, opposite)], final_primary[unit]
            )
            prediction_count += 1
    if fit_count != 300 or prediction_count != 420:
        raise IACKDFailure("inventory", "fit or prediction inventory is incomplete")
    prediction_hashes = {
        condition: {
            unit: _prediction_sha256(values)
            for unit, values in sorted(unit_predictions.items())
        }
        for condition, unit_predictions in predictions.items()
    }
    counters = {
        "parameter_update_fits": fit_count,
        "target_blind_model_inference_calls": prediction_count,
        "participant_condition_prediction_sets": prediction_count,
        "final_target_rows_available_to_model_stage": 0,
        "target_deliveries": 0,
        "scoring_events": 0,
        "post_target_updates": 0,
    }
    private = {
        "schema_name": "neurodecodekit.iackd_private_predictions",
        "schema_version": SCHEMA_VERSION,
        "contract_sha256": CONTRACT_SHA256,
        "source_kind": source_kind,
        "condition_ids": list(CONDITION_IDS),
        "unit_event_ids": event_ids,
        "predictions": predictions,
        "operation_counters": counters,
    }
    private["canonical_prediction_sha256"] = _canonical_sha256(private)
    private_bytes = _write_json_exclusive(private_path, private, maximum_output_bytes)
    if _read_json_nofollow(private_path, maximum_output_bytes) != private:
        raise IACKDFailure("replay", "private prediction payload does not replay exactly")
    implementation_registry_sha256 = None
    implementation_tracked_file_hashes_sha256 = None
    if implementation_registry is not None:
        implementation_registry_sha256 = _file_sha256(
            _repo_root() / IMPLEMENTATION_RELATIVE_PATH
        )
        implementation_tracked_file_hashes_sha256 = _canonical_sha256(
            {"tracked_file_hashes": implementation_registry["tracked_file_hashes"]}
        )
    target_firewall_summary = {
        "final_target_rows_available_to_model_stage": 0,
        "sealed_target_file_content_reads": 0,
        "signed_trajectory_values_available_to_model_stage": 0,
        "prediction_derivative_contains_targets": False,
        "both_final_target_sets_frozen_together": True,
        "target_free_final_keys": derivative_summary["target_free_final_keys"],
    }
    freeze = {
        "schema_name": "neurodecodekit.iackd_prediction_freeze",
        "schema_version": SCHEMA_VERSION,
        "status": "target_blind_predictions_frozen",
        "proof_posture": (
            "aggregate_hash_only_real_target_blind_prediction_freeze"
            if source_kind == "real_IACKD"
            else "aggregate_hash_only_generated_fixture_qualification"
        ),
        "contract_sha256": CONTRACT_SHA256,
        "authorization_decision_sha256": DECISION_SHA256,
        "source_kind": source_kind,
        "source_manifest_sha256": derivative_summary["source_manifest_sha256"],
        "source_file_count": derivative_summary["source_file_count"],
        "source_payload_bytes": (
            load_registered_contract()["dataset_binding"]["exact_selected_payload_bytes"]
            if source_kind == "real_IACKD"
            else 0
        ),
        "source_hashes_sha256": derivative_summary["source_hashes_sha256"],
        "reader_metadata_sha256": derivative_summary["reader_metadata_sha256"],
        "split_protocol_sha256": derivative_summary["split_protocol_sha256"],
        "feature_configuration_sha256": derivative_summary[
            "feature_configuration_sha256"
        ],
        "condition_ids": list(CONDITION_IDS),
        "participant_hand_units": 30,
        "prediction_set_sha256": prediction_hashes,
        "canonical_private_prediction_sha256": private["canonical_prediction_sha256"],
        "private_prediction_payload_sha256": _file_sha256(private_path),
        "private_prediction_payload_bytes": private_bytes,
        "fit_derivative_sha256": derivative_summary["fit_derivative_sha256"],
        "prediction_derivative_sha256": derivative_summary["prediction_derivative_sha256"],
        "sealed_target_sha256": derivative_summary["sealed_target_sha256"],
        "physiology_summary_sha256": derivative_summary["physiology_summary_sha256"],
        "physiology_content_sha256": derivative_summary["physiology_content_sha256"],
        "quality_summary_sha256": _canonical_sha256(
            {
                "aggregate_exclusion_counts": derivative_summary[
                    "aggregate_exclusion_counts"
                ],
                "motion_guard_minimum_milliseconds": derivative_summary[
                    "motion_guard_minimum_milliseconds"
                ],
                "fit_rows": derivative_summary["fit_rows"],
                "final_rows": derivative_summary["final_rows"],
            }
        ),
        "dependency_versions": dependency_versions(),
        "operation_counters": counters,
        "target_firewall_summary": target_firewall_summary,
        "target_firewall_sha256": _canonical_sha256(target_firewall_summary),
        "upstream_access_counters": dict(upstream_access_counters or {}),
        "resources": {
            "runtime_seconds_through_freeze": (
                None
                if execution_started_monotonic is None
                else round(time.monotonic() - execution_started_monotonic, 6)
            ),
            "peak_rss_bytes": _peak_rss_bytes(),
            "generated_private_bytes": _directory_bytes(output),
            "end_to_end_latency_measured": False,
        },
        "implementation_commit": (
            None if implementation_evidence is None else implementation_evidence.implementation_commit
        ),
        "implementation_ci_run_id": (
            None
            if implementation_evidence is None
            else implementation_evidence.implementation_ci_run_id
        ),
        "implementation_base_python_job_id": (
            None if implementation_evidence is None else implementation_evidence.base_python_job_id
        ),
        "implementation_optional_neuro_job_id": (
            None
            if implementation_evidence is None
            else implementation_evidence.optional_neuro_job_id
        ),
        "implementation_registry_sha256": implementation_registry_sha256,
        "implementation_tracked_file_hashes_sha256": (
            implementation_tracked_file_hashes_sha256
        ),
        "warnings": [
            "offline_oracle_aligned_causal_in_samples_not_real_time",
            "prediction_freeze_contains_hashes_not_individual_outputs",
            "target_views_remain_sealed",
            "no_scientific_claim_before_one_registered_score",
        ],
    }
    freeze["freeze_record_sha256"] = _canonical_sha256(freeze)
    validate_public_freeze(freeze)
    _write_json_exclusive(freeze_output, freeze, 2 * 1024 * 1024)
    if _directory_bytes(output) > maximum_output_bytes:
        raise IACKDFailure("output", "private prediction output exceeds cap")
    return freeze


def _balanced_accuracy(targets: Any, predictions: Any) -> float:
    np = _np()
    y = np.asarray(targets, dtype="int8")
    p = np.asarray(predictions, dtype="int8")
    recalls = []
    for label in (0, 1):
        mask = y == label
        if not np.any(mask):
            raise IACKDFailure("score", "balanced accuracy requires both classes")
        recalls.append(float(np.mean(p[mask] == label)))
    return sum(recalls) / 2.0


def _sign_flip_p(values: Sequence[float]) -> float:
    if len(values) != 15:
        raise IACKDFailure("score", "participant sign-flip test requires 15 values")
    observed = sum(values) / len(values)
    exceed = 0
    for assignment in range(1 << len(values)):
        mean = sum(
            value if assignment & (1 << index) else -value
            for index, value in enumerate(values)
        ) / len(values)
        if mean >= observed - 1e-15:
            exceed += 1
    return exceed / float(1 << len(values))


def _condition_metrics(
    targets_actual: Any,
    targets_visual: Any,
    predictions: Any,
    subjects: Any,
) -> tuple[dict[str, Any], list[float], list[float]]:
    np = _np()
    participants = load_registered_contract()["dataset_binding"]["participant_ids"]
    action_scores = []
    visual_scores = []
    for subject in participants:
        mask = subjects == subject
        action_scores.append(_balanced_accuracy(targets_actual[mask], predictions[mask]))
        visual_scores.append(_balanced_accuracy(targets_visual[mask], predictions[mask]))
    metric = {
        "pooled_action_balanced_accuracy": _balanced_accuracy(targets_actual, predictions),
        "pooled_visual_balanced_accuracy": _balanced_accuracy(targets_visual, predictions),
        "macro_participant_action_balanced_accuracy": float(np.mean(action_scores)),
        "macro_participant_visual_balanced_accuracy": float(np.mean(visual_scores)),
        "macro_action_minus_visual_margin": float(
            np.mean(np.asarray(action_scores) - np.asarray(visual_scores))
        ),
        "participants_above_chance_action": int(sum(value > 0.5 for value in action_scores)),
        "participants_above_chance_visual": int(sum(value > 0.5 for value in visual_scores)),
    }
    return metric, action_scores, visual_scores


def score_private_predictions(
    *,
    freeze: Mapping[str, Any],
    private_predictions: Mapping[str, Any],
    sealed: Mapping[str, Any],
    final: Mapping[str, Any],
    physiology: Mapping[str, Any],
) -> dict[str, Any]:
    """Score both target views once and return aggregate-only evidence."""

    np = _np()
    validate_public_freeze(freeze)
    required_private_keys = {
        "schema_name",
        "schema_version",
        "contract_sha256",
        "source_kind",
        "condition_ids",
        "unit_event_ids",
        "predictions",
        "operation_counters",
        "canonical_prediction_sha256",
    }
    if set(private_predictions) != required_private_keys:
        raise IACKDFailure("score", "private prediction fields differ from the strict schema")
    if private_predictions.get("schema_name") != "neurodecodekit.iackd_private_predictions":
        raise IACKDFailure("score", "private prediction schema mismatch")
    if private_predictions.get("schema_version") != SCHEMA_VERSION:
        raise IACKDFailure("score", "private prediction version mismatch")
    if private_predictions.get("contract_sha256") != CONTRACT_SHA256:
        raise IACKDFailure("score", "private prediction contract mismatch")
    if private_predictions.get("source_kind") != freeze["source_kind"]:
        raise IACKDFailure("score", "private prediction source kind mismatch")
    if tuple(private_predictions.get("condition_ids", ())) != CONDITION_IDS:
        raise IACKDFailure("score", "private prediction condition inventory mismatch")
    if private_predictions.get("operation_counters") != freeze["operation_counters"]:
        raise IACKDFailure("score", "private prediction operation counters mismatch")
    private = dict(private_predictions)
    private_hash = private.pop("canonical_prediction_sha256", None)
    if private_hash != _canonical_sha256(private):
        raise IACKDFailure("score", "private prediction record hash mismatch")
    if private_hash != freeze["canonical_private_prediction_sha256"]:
        raise IACKDFailure("score", "private prediction record differs from the freeze")
    if not np.array_equal(sealed["event_ids"], final["event_ids"]):
        raise IACKDFailure("score", "sealed and final event identities do not align")
    if not np.array_equal(sealed["subjects"], final["subjects"]):
        raise IACKDFailure("score", "sealed and final participant identities do not align")
    if not np.array_equal(sealed["hands"], final["hands"]):
        raise IACKDFailure("score", "sealed and final hand identities do not align")
    actual = np.asarray(sealed["actual_hand_directions"], dtype="int8")
    visual = np.asarray(sealed["visual_target_directions"], dtype="int8")
    if actual.shape != visual.shape or actual.shape != final["event_ids"].shape:
        raise IACKDFailure("score", "sealed target dimensions differ from final rows")
    if not set(np.unique(actual).tolist()).issubset({0, 1}) or not set(
        np.unique(visual).tolist()
    ).issubset({0, 1}):
        raise IACKDFailure("score", "sealed targets are not binary")
    if not np.all(actual != visual):
        raise IACKDFailure("score", "sealed target views are not opposites")
    expected_units = {
        _unit(subject, hand)
        for subject in load_registered_contract()["dataset_binding"]["participant_ids"]
        for hand in ("left", "right")
    }
    if set(private_predictions["unit_event_ids"]) != expected_units:
        raise IACKDFailure("score", "private event unit inventory mismatch")
    if set(private_predictions["predictions"]) != set(CONDITION_IDS):
        raise IACKDFailure("score", "private prediction condition inventory mismatch")
    if any(
        set(private_predictions["predictions"][condition]) != expected_units
        for condition in CONDITION_IDS
    ):
        raise IACKDFailure("score", "private prediction unit inventory mismatch")
    if len(set(str(value) for value in final["event_ids"])) != len(actual):
        raise IACKDFailure("score", "final event identities are not unique")
    condition_metrics = {}
    participant_action = {}
    participant_visual = {}
    for condition in CONDITION_IDS:
        combined = np.empty(len(actual), dtype="int8")
        for unit, ids in private_predictions["unit_event_ids"].items():
            subject, hand = unit.split("|", 1)
            mask = (final["subjects"] == subject) & (final["hands"] == hand)
            observed_ids = [str(value) for value in final["event_ids"][mask]]
            if observed_ids != ids:
                raise IACKDFailure("score", "private and final event identities do not align")
            values = private_predictions["predictions"][condition][unit]
            if len(values) != int(np.count_nonzero(mask)) or any(
                not isinstance(value, int) or value not in {0, 1} for value in values
            ):
                raise IACKDFailure("score", "private prediction rows are malformed")
            if _prediction_sha256(values) != freeze["prediction_set_sha256"][condition][unit]:
                raise IACKDFailure("score", "prediction hash or values mismatch")
            combined[mask] = np.asarray(values, dtype="int8")
        metric, action_scores, visual_scores = _condition_metrics(
            actual, visual, combined, final["subjects"]
        )
        condition_metrics[condition] = metric
        participant_action[condition] = action_scores
        participant_visual[condition] = visual_scores
    contract = load_registered_contract()
    gates = contract["gates"]
    primary = condition_metrics["whole_head_primary"]
    primary_margins = [
        action - visual
        for action, visual in zip(
            participant_action["whole_head_primary"],
            participant_visual["whole_head_primary"],
            strict=True,
        )
    ]
    action_p = _sign_flip_p(primary_margins)
    visual_p = _sign_flip_p([-value for value in primary_margins])
    prior = condition_metrics["train_only_no_signal_prior"]
    h1_spec = gates["H1_action_over_cue_reversal"]
    h1 = all(
        (
            primary["pooled_action_balanced_accuracy"]
            >= h1_spec["minimum_pooled_action_balanced_accuracy"],
            primary["macro_participant_action_balanced_accuracy"]
            >= h1_spec["minimum_macro_participant_action_balanced_accuracy"],
            primary["participants_above_chance_action"]
            >= h1_spec["minimum_participants_above_0_5_action_balanced_accuracy"],
            action_p <= h1_spec["maximum_exact_participant_sign_flip_p"],
            primary["macro_action_minus_visual_margin"]
            >= h1_spec["minimum_macro_action_minus_visual_margin"],
            primary["macro_participant_visual_balanced_accuracy"]
            <= h1_spec["maximum_macro_visual_balanced_accuracy"],
            primary["macro_participant_action_balanced_accuracy"]
            - prior["macro_participant_action_balanced_accuracy"]
            >= h1_spec["minimum_macro_action_margin_over_no_signal_prior"],
        )
    )
    cue_bound = all(
        (
            primary["pooled_visual_balanced_accuracy"] >= 0.6,
            primary["macro_participant_visual_balanced_accuracy"] >= 0.6,
            primary["participants_above_chance_visual"] >= 12,
            visual_p <= 0.01,
            primary["macro_action_minus_visual_margin"] <= -0.2,
            primary["macro_participant_action_balanced_accuracy"] <= 0.4,
        )
    )
    h2_spec = gates["H2_recorded_peripheral_and_timing_controls"]
    eog = condition_metrics["HEOG_VEOG_only"]
    orthogonal = condition_metrics["fit_only_EOG_orthogonalized_whole_head"]
    fixed_controls = (
        "all_zero_final_EEG_through_primary",
        "fixed_train_label_derangement_seed_6841",
        "one_row_cyclic_final_feature_displacement",
        "fixed_final_only_EEG_channel_permutation_seed_6842",
        "opposite_hand_primary_without_adaptation",
    )
    h2 = all(
        (
            primary["macro_participant_action_balanced_accuracy"]
            - eog["macro_participant_action_balanced_accuracy"]
            >= h2_spec["minimum_primary_minus_EOG_only_macro_action_margin"],
            orthogonal["macro_participant_action_balanced_accuracy"]
            >= h2_spec["minimum_EOG_orthogonalized_macro_action_balanced_accuracy"],
            orthogonal["macro_action_minus_visual_margin"]
            >= h2_spec["minimum_EOG_orthogonalized_action_minus_visual_margin"],
            condition_metrics["event_index_and_timing_only"][
                "macro_participant_action_balanced_accuracy"
            ]
            <= h2_spec["maximum_timing_only_macro_action_balanced_accuracy"],
            condition_metrics["pre_window_baseline"][
                "macro_participant_action_balanced_accuracy"
            ]
            <= h2_spec["maximum_pre_window_macro_action_balanced_accuracy"],
            all(
                condition_metrics[condition]["macro_participant_action_balanced_accuracy"]
                <= h2_spec["maximum_each_fixed_control_macro_action_balanced_accuracy"]
                and condition_metrics[condition]["macro_action_minus_visual_margin"]
                <= h2_spec["maximum_each_fixed_control_action_minus_visual_margin"]
                for condition in fixed_controls
            ),
        )
    )
    h3_spec = gates["H3_motor_compatible_support"]
    central = condition_metrics["central_C3_C4_Cz"]
    physiology_complete = all(
        (
            physiology.get("readiness_mean_C3_C4_Cz", np.empty(0)).shape == (30, 3, 1024),
            physiology.get("mu_beta_and_early_late_summary", np.empty(0)).shape == (30, 7),
            physiology.get("motion_guard_min_mean_max_milliseconds", np.empty(0)).shape
            == (30, 3),
            physiology.get("trial_counts", np.empty(0)).shape == (30,),
        )
    )
    h3 = all(
        (
            central["macro_participant_action_balanced_accuracy"]
            >= h3_spec["minimum_central_macro_action_balanced_accuracy"],
            central["macro_action_minus_visual_margin"]
            >= h3_spec["minimum_central_action_minus_visual_margin"],
            central["participants_above_chance_action"]
            >= h3_spec["minimum_participants_above_0_5_central_action_balanced_accuracy"],
            physiology_complete,
        )
    )
    h4 = all(
        (
            freeze["participant_hand_units"] == 30,
            freeze["operation_counters"]["parameter_update_fits"] == 300,
            freeze["operation_counters"]["participant_condition_prediction_sets"] == 420,
            freeze["operation_counters"]["final_target_rows_available_to_model_stage"] == 0,
            float(final["motion_guard_milliseconds"].min()) >= 30.0,
        )
    )
    if cue_bound:
        verdict = "IACKD-R1"
    elif not h1 or not h4:
        verdict = "IACKD-R0"
    elif not h2:
        verdict = "IACKD-R2"
    elif not h3:
        verdict = "IACKD-R3"
    else:
        verdict = "IACKD-R4"
    outcome_claim = next(
        row["maximum_claim"] for row in contract["ordered_router"] if row["verdict"] == verdict
    )
    return {
        "schema_name": "neurodecodekit.iackd_aggregate_score",
        "schema_version": SCHEMA_VERSION,
        "status": "scored_once_frozen_router_applied",
        "verdict": verdict,
        "H1_action_over_cue_reversal_passed": h1,
        "H2_recorded_peripheral_and_timing_controls_passed": h2,
        "H3_motor_compatible_support_passed": h3,
        "H4_integrity_and_causality_passed": h4,
        "cue_bound_route_passed": cue_bound,
        "primary_exact_participant_action_minus_visual_sign_flip_p": action_p,
        "primary_exact_participant_visual_minus_action_sign_flip_p": visual_p,
        "condition_metrics": condition_metrics,
        "physiology": {
            "participant_hand_trace_count": int(
                physiology["readiness_mean_C3_C4_Cz"].shape[0]
            ),
            "trace_channels": int(physiology["readiness_mean_C3_C4_Cz"].shape[1]),
            "trace_samples": int(physiology["readiness_mean_C3_C4_Cz"].shape[2]),
            "summary_fields_per_unit": int(
                physiology["mu_beta_and_early_late_summary"].shape[1]
            ),
            "descriptive_nonselecting": True,
            "readiness_mu_beta_complete": bool(physiology_complete),
        },
        "final_target_deliveries": 1,
        "scoring_events": 1,
        "post_target_updates": 0,
        "individual_participant_metrics_published": False,
        "warnings": [
            "within_dataset_same_team_study_not_independent_replication",
            "recorded_EOG_without_synchronized_EMG_cannot_prove_absolute_brain_specific_origin",
            "offline_oracle_aligned_causal_in_samples_not_real_time",
            "no_typing_language_thought_hardware_assistive_or_clinical_claim",
        ],
        "claim_boundary": {
            "outcome_maximum": outcome_claim,
            "absolute_ceiling": contract["claim_boundary"]["maximum_future_IACKD_R4"],
            "not_established": (
                "absolute brain-specific origin independent-team replication unseen-person "
                "generalization typing language or thought decoding real-time operation "
                "portable hardware home use assistive benefit or clinical utility"
            ),
        },
    }


def _synthetic_runs(subject: str) -> tuple[str, ...]:
    return ("01", "02", "03", "04", "05", "06") if subject in {"sub-04", "sub-05"} else (
        "01",
        "02",
        "03",
        "04",
    )


def build_synthetic_run_record(subject: str, hand: str, run: str) -> RunRecord:
    """Generate one deterministic source-independent 1,024 Hz run."""

    np = _np()
    contract = load_registered_contract()
    if subject not in contract["dataset_binding"]["participant_ids"]:
        raise ValueError("synthetic participant is outside IACKD")
    if hand not in {"left", "right"} or run not in _synthetic_runs(subject):
        raise ValueError("synthetic hand or run is outside IACKD")
    seed = int.from_bytes(
        hashlib.sha256(f"IACKD|6840|{subject}|{hand}|{run}".encode()).digest()[:8],
        "big",
    )
    rng = np.random.default_rng(seed)
    labels = np.asarray([0] * 8 + [1] * 8, dtype="int8")
    rng.shuffle(labels)
    event_14 = np.asarray([4.0 + 3.0 * index for index in range(16)], dtype="float64")
    sample_count = int(math.ceil((event_14[-1] + 2.0) * 1024.0))
    channel_names = EEG_CHANNELS + REQUIRED_NON_EEG
    channel_types = ("eeg",) * 32 + ("misc", "misc", "eog", "eog")
    values = rng.normal(0.0, 0.15e-6, size=(36, sample_count)).astype("float64")
    geometry = np.full((36, 3), np.nan, dtype="float64")
    for index in range(32):
        angle = 2.0 * math.pi * index / 32.0
        geometry[index] = [0.09 * math.cos(angle), 0.09 * math.sin(angle), 0.04]
    spatial = rng.normal(0.0, 0.15, size=32)
    for name, weight in (("C3", 1.3), ("C4", -1.1), ("Cz", 1.0)):
        spatial[EEG_CHANNELS.index(name)] = weight
    spatial -= spatial.mean()
    trials = []
    condition = "red" if _split_kind(subject, run) == "fit" else "yellow"
    for event_index, (onset, actual) in enumerate(zip(event_14, labels, strict=True)):
        visual = int(actual) if condition == "red" else 1 - int(actual)
        window = _sample_slice(onset - 1.0, onset, 1024.0, sample_count)
        phase = np.linspace(-math.pi, 0.0, window.stop - window.start, endpoint=False)
        waveform = np.sin(phase) + 0.35 * np.linspace(-1.0, 1.0, phase.size)
        signed = (1.0 if actual else -1.0) * 2.5e-6
        values[:32, window] += spatial[:, None] * signed * waveform[None, :]
        leap_times = np.arange(onset - 0.5, onset + 1.301, 0.005, dtype="float64")
        progress = np.clip((leap_times - (onset + 0.2)) / 0.8, 0.0, 1.0)
        leap_xyz = np.zeros((leap_times.size, 3), dtype="float64")
        leap_xyz[:, 0] = (1.0 if actual else -1.0) * 50.0 * progress
        ball_times = np.arange(onset - 0.5, onset + 1.301, 1.0 / 60.0, dtype="float64")
        ball_progress = np.clip((ball_times - (onset + 0.2)) / 0.8, 0.0, 1.0)
        ball_x = (1.0 if visual else -1.0) * 100.0 * ball_progress
        trials.append(
            TrialRecord(
                trial_id=f"T{event_index:03d}",
                event_index=event_index,
                event_55_seconds=float(onset - 1.5),
                event_14_seconds=float(onset),
                boundary_seconds=float(onset + 1.25),
                condition=condition,
                leap_timestamps_seconds=leap_times,
                leap_xyz_mm=leap_xyz,
                ball_timestamps_seconds=ball_times,
                ball_x_pixels=ball_x,
                ball_move_direct="right" if visual else "left",
            )
        )
    return RunRecord(
        subject=subject,
        hand=hand,
        run=run,
        sampling_rate_hz=1024.0,
        channel_names=channel_names,
        channel_types=channel_types,
        channel_geometry_m=geometry,
        signal_volts=values,
        trials=tuple(trials),
    )


def run_synthetic_qualification(
    output_root: str | Path,
    *,
    maximum_output_bytes: int = 512 * 1024 * 1024,
) -> dict[str, Any]:
    """Exercise every IACKD interface on generated arrays and trajectories."""

    if maximum_output_bytes <= 0 or maximum_output_bytes > 512 * 1024 * 1024:
        raise IACKDRefusal("synthetic output cap must be within 1 byte and 512 MiB")
    started = time.monotonic()
    contract = load_registered_contract()

    def records():
        for subject in contract["dataset_binding"]["participant_ids"]:
            for hand in ("left", "right"):
                for run in _synthetic_runs(subject):
                    yield build_synthetic_run_record(subject, hand, run)

    source_hashes = {
        f"{subject}/{hand}/run-{run}.synthetic": _sha256_bytes(
            f"IACKD|fixture|6840|{subject}|{hand}|{run}".encode()
        )
        for subject in contract["dataset_binding"]["participant_ids"]
        for hand in ("left", "right")
        for run in _synthetic_runs(subject)
    }
    derivative = extract_records_to_derivatives(
        records(),
        output_root,
        source_hashes=source_hashes,
        manifest_sha256=_sha256_bytes(b"IACKD-generated-fixture-manifest-v0"),
        maximum_output_bytes=maximum_output_bytes,
    )
    output = Path(output_root)
    freeze_path = output / "synthetic_prediction_freeze.v0.json"
    freeze = run_target_blind_predictions(
        output_root=output,
        freeze_path=freeze_path,
        source_kind="generated_synthetic_fixture",
        maximum_output_bytes=maximum_output_bytes,
        execution_started_monotonic=started,
        upstream_access_counters={
            "synthetic_run_records": 128,
            "real_object_hash_passes": 0,
            "real_brainvision_parses": 0,
            "real_stream_parses": 0,
        },
    )
    private = json.loads((output / PRIVATE_PREDICTIONS_NAME).read_text(encoding="utf-8"))
    sealed = _load_npz(output / SEALED_TARGET_NAME)
    final = _load_npz(output / FINAL_DERIVATIVE_NAME, target_free=True)
    physiology = _load_npz(output / PHYSIOLOGY_SUMMARY_NAME, target_free=True)
    scored = score_private_predictions(
        freeze=freeze,
        private_predictions=private,
        sealed=sealed,
        final=final,
        physiology=physiology,
    )
    runtime = time.monotonic() - started
    summary = {
        "schema_name": "neurodecodekit.iackd_synthetic_qualification",
        "schema_version": SCHEMA_VERSION,
        "status": "passed_generated_fixture_only",
        "synthetic_runs": 128,
        "synthetic_trials": derivative["fit_rows"] + derivative["final_rows"],
        "fit_rows": derivative["fit_rows"],
        "final_rows": derivative["final_rows"],
        "participant_hand_units": 30,
        "parameter_update_fits": freeze["operation_counters"]["parameter_update_fits"],
        "target_blind_model_inference_calls": freeze["operation_counters"][
            "target_blind_model_inference_calls"
        ],
        "participant_condition_prediction_sets": freeze["operation_counters"][
            "participant_condition_prediction_sets"
        ],
        "final_target_rows_available_to_model_stage": 0,
        "synthetic_router_verdict": scored["verdict"],
        "runtime_seconds": round(runtime, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "generated_bytes": 0,
        "all_gates_passed": True,
        "real_metadata_requests": 0,
        "real_payload_requests": 0,
        "real_payload_bytes": 0,
        "real_data_reads": 0,
        "real_target_reads": 0,
        "network_bytes": 0,
        "dependency_installs": 0,
        "scientific_claim_upgrade": False,
        "end_to_end_latency_measured": False,
        "warnings": [
            "synthetic_fixture_is_interface_qualification_not_scientific_evidence",
            "synthetic_router_verdict_has_no_claim_value",
            "no_real_IACKD_content_was_accessed",
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
        raise IACKDFailure("output", "synthetic byte measurement did not converge")
    if total > maximum_output_bytes:
        raise IACKDFailure("output", "synthetic qualification exceeds cap")
    _write_json_exclusive(output / "qualification_summary.v0.json", summary, 2 * 1024 * 1024)
    if _directory_bytes(output) != summary["generated_bytes"]:
        raise IACKDFailure("output", "synthetic byte measurement is not exact")
    return summary


def remove_synthetic_qualification(path: str | Path) -> None:
    """Remove only a caller-named generated qualification directory."""

    candidate = Path(path)
    if candidate.exists() and not candidate.is_symlink():
        shutil.rmtree(candidate)


def _normalized_field(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())


def _find_field(
    fieldnames: Sequence[str],
    exact: Sequence[str],
    *,
    suffix: str | None = None,
    contains: Sequence[str] = (),
) -> str | None:
    normalized = {_normalized_field(name): name for name in fieldnames}
    for candidate in exact:
        if _normalized_field(candidate) in normalized:
            return normalized[_normalized_field(candidate)]
    if suffix is not None:
        for key, original in normalized.items():
            if key.endswith(suffix) and (not contains or any(token in key for token in contains)):
                return original
    return None


def _event_code(value: str) -> int | None:
    stripped = value.strip()
    try:
        numeric = int(float(stripped))
    except ValueError:
        numeric = None
    if numeric in {14, 55, 66, 1000001}:
        return numeric
    matches = re.findall(r"(?<!\d)(1000001|66|55|14)(?!\d)", stripped)
    return int(matches[-1]) if matches else None


def _condition(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _normalized_field(value)
    if "yellow" in normalized or "incongruent" in normalized:
        return "yellow"
    if "red" in normalized or "congruent" in normalized:
        return "red"
    return None


def parse_events_tsv(text: str) -> tuple[_EventTrial, ...]:
    """Parse strict 55 -> 14 -> boundary trial triples from generated or real TSV."""

    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if not reader.fieldnames:
        raise IACKDFailure("event", "events TSV lacks a header")
    onset_field = _find_field(reader.fieldnames, ("onset", "time", "timestamp"))
    code_field = _find_field(
        reader.fieldnames,
        ("value", "event_code", "marker", "trigger", "stim", "trial_type", "description"),
    )
    trial_field = _find_field(
        reader.fieldnames,
        ("trial_id", "trial", "trial_index", "trial_number", "trial_num"),
    )
    condition_field = _find_field(
        reader.fieldnames,
        ("condition", "color", "ball_color", "congruency", "trial_condition"),
    )
    if onset_field is None or code_field is None:
        raise IACKDFailure("event", "events TSV lacks onset or marker code")
    triples = []
    pending: dict[str, Any] | None = None
    for row in reader:
        code = _event_code(str(row.get(code_field, "")))
        if code is None:
            continue
        try:
            onset = float(str(row.get(onset_field, "")))
        except ValueError as exc:
            raise IACKDFailure("event", "event onset is not numeric") from exc
        if not math.isfinite(onset):
            raise IACKDFailure("event", "event onset is nonfinite")
        observed_condition = _condition(row.get(condition_field)) if condition_field else None
        if code == 55:
            if pending is not None:
                raise IACKDFailure("event", "new event 55 appeared before a boundary")
            pending = {
                "trial_id": (
                    str(row.get(trial_field, "")).strip()
                    if trial_field
                    else f"ORDER-{len(triples):04d}"
                ),
                "event_index": len(triples),
                "event_55": onset,
                "event_14": None,
                "condition": observed_condition,
            }
        elif code == 14:
            if pending is None or pending["event_14"] is not None:
                raise IACKDFailure("event", "event 14 is outside a unique trial")
            pending["event_14"] = onset
            if pending["condition"] is None:
                pending["condition"] = observed_condition
        else:
            if pending is None or pending["event_14"] is None:
                raise IACKDFailure("event", "boundary is outside a complete trial")
            if not pending["trial_id"]:
                pending["trial_id"] = f"ORDER-{len(triples):04d}"
            triples.append(
                _EventTrial(
                    trial_id=str(pending["trial_id"]),
                    event_index=int(pending["event_index"]),
                    event_55_seconds=float(pending["event_55"]),
                    event_14_seconds=float(pending["event_14"]),
                    boundary_seconds=onset,
                    condition=pending["condition"],
                )
            )
            pending = None
    if pending is not None or not triples:
        raise IACKDFailure("event", "events TSV ends with an incomplete or empty trial set")
    return tuple(triples)


def _stream_groups(
    text: str,
    *,
    kind: str,
    time_scale_to_seconds: float = 1.0,
    position_scale: float = 1.0,
) -> tuple[_StreamGroup, ...]:
    np = _np()
    if time_scale_to_seconds not in {1.0, 1e-3, 1e-6, 1e-9}:
        raise IACKDFailure("stream", "stream time scale is not allowlisted")
    if not math.isfinite(position_scale) or position_scale <= 0.0:
        raise IACKDFailure("stream", "stream position scale is invalid")
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if not reader.fieldnames:
        raise IACKDFailure("stream", f"{kind} TSV lacks a header")
    fields = reader.fieldnames
    time_field = _find_field(
        fields,
        ("timestamp", "time_stamp", "time", "onset", "time_seconds", "eeg_time"),
        suffix="time",
        contains=("receive", "record", "frame", "device", "eeg"),
    )
    trial_field = _find_field(
        fields,
        ("trial_id", "trial", "trial_index", "trial_number", "trial_num"),
    )
    x_field = _find_field(
        fields,
        ("x", "position_x", "pos_x", "palm_position_x", "hand_x", "ball_x"),
        suffix="x",
        contains=("position", "palm", "hand", "ball", "coord"),
    )
    y_field = _find_field(
        fields,
        ("y", "position_y", "pos_y", "palm_position_y", "hand_y"),
        suffix="y",
        contains=("position", "palm", "hand", "coord"),
    )
    z_field = _find_field(
        fields,
        ("z", "position_z", "pos_z", "palm_position_z", "hand_z"),
        suffix="z",
        contains=("position", "palm", "hand", "coord"),
    )
    condition_field = _find_field(
        fields,
        (
            "condition",
            "color",
            "ball_color",
            "congruency",
            "trial_condition",
            "move_con",
            "move_condition",
        ),
    )
    move_field = _find_field(
        fields,
        ("move_direct", "move_direction", "direction", "target_direction"),
    )
    if time_field is None or x_field is None:
        raise IACKDFailure("stream", f"{kind} TSV lacks time or x position")
    if kind == "leap" and (y_field is None or z_field is None):
        raise IACKDFailure("stream", "Leap TSV lacks y or z position")
    raw_groups: list[tuple[str, list[dict[str, str]]]] = []
    by_identity: dict[str, list[dict[str, str]]] = {}
    previous_time = None
    group_index = 0
    active_identity = "ORDER-0000"
    for row_index, row in enumerate(reader):
        try:
            timestamp = float(str(row.get(time_field, ""))) * time_scale_to_seconds
        except ValueError as exc:
            raise IACKDFailure("stream", f"{kind} timestamp is not numeric") from exc
        if not math.isfinite(timestamp):
            raise IACKDFailure("stream", f"{kind} timestamp is nonfinite")
        if trial_field:
            identity = str(row.get(trial_field, "")).strip()
            if not identity:
                raise IACKDFailure("stream", f"{kind} row lacks trial identity")
        else:
            if previous_time is not None and timestamp <= previous_time:
                group_index += 1
                active_identity = f"ORDER-{group_index:04d}"
            identity = active_identity
        previous_time = timestamp
        if identity not in by_identity:
            by_identity[identity] = []
            raw_groups.append((identity, by_identity[identity]))
        row["__row_index__"] = str(row_index)
        by_identity[identity].append(row)
    groups = []
    for identity, rows in raw_groups:
        try:
            timestamps = np.asarray(
                [float(row[time_field]) * time_scale_to_seconds for row in rows],
                dtype="float64",
            )
            x = np.asarray(
                [float(row[x_field]) * position_scale for row in rows],
                dtype="float64",
            )
            y = (
                None
                if y_field is None
                else np.asarray(
                    [float(row[y_field]) * position_scale for row in rows],
                    dtype="float64",
                )
            )
            z = (
                None
                if z_field is None
                else np.asarray(
                    [float(row[z_field]) * position_scale for row in rows],
                    dtype="float64",
                )
            )
        except (TypeError, ValueError) as exc:
            raise IACKDFailure("stream", f"{kind} position or timestamp is not numeric") from exc
        coordinates = [x, *(value for value in (y, z) if value is not None)]
        if not all(np.isfinite(value).all() for value in coordinates):
            raise IACKDFailure("stream", f"{kind} position contains nonfinite values")
        if timestamps.size < 8 or not np.all(np.diff(timestamps) > 0.0):
            raise IACKDFailure("stream", f"{kind} group timestamps are not strictly increasing")
        conditions = {
            observed
            for row in rows
            if condition_field and (observed := _condition(row.get(condition_field))) is not None
        }
        moves = {
            str(row.get(move_field, "")).strip()
            for row in rows
            if move_field and str(row.get(move_field, "")).strip()
        }
        if len(conditions) > 1 or len(moves) > 1:
            raise IACKDFailure("stream", f"{kind} group has inconsistent metadata")
        groups.append(
            _StreamGroup(
                trial_id=identity,
                timestamps=timestamps,
                x=x,
                y=y,
                z=z,
                condition=next(iter(conditions), None),
                move_direct=next(iter(moves), None),
            )
        )
    if not groups:
        raise IACKDFailure("stream", f"{kind} TSV contains no trajectory groups")
    return tuple(groups)


def _align_stream_times(values: Any, event: _EventTrial) -> Any:
    np = _np()
    times = np.asarray(values, dtype="float64")
    tolerance = 0.05
    if times[0] <= event.event_14_seconds <= times[-1] + tolerance:
        aligned = times
    else:
        relative = times - times[0]
        duration = float(relative[-1])
        full_trial = event.boundary_seconds - event.event_55_seconds
        movement = event.boundary_seconds - event.event_14_seconds
        if duration >= full_trial - 0.1:
            aligned = event.event_55_seconds + relative
        elif duration >= movement - 0.1:
            aligned = event.event_14_seconds + relative
        else:
            raise IACKDFailure("stream", "trajectory duration cannot be aligned to trial markers")
    if aligned[0] > event.event_14_seconds + tolerance:
        raise IACKDFailure("stream", "trajectory begins after movement cue")
    if aligned[-1] < event.boundary_seconds - tolerance:
        raise IACKDFailure("stream", "trajectory ends before the boundary hit")
    return aligned


def _identity_number(value: str) -> int | None:
    if value.startswith("ORDER-"):
        return None
    matches = re.findall(r"\d+", value)
    return int(matches[-1]) if matches else None


def reconcile_trials(
    event_trials: Sequence[_EventTrial],
    ball_groups: Sequence[_StreamGroup],
    leap_groups: Sequence[_StreamGroup],
) -> tuple[TrialRecord, ...]:
    """Join event, ball, and Leap groups without exposing directions to preprocessing."""

    np = _np()
    if not (len(event_trials) == len(ball_groups) == len(leap_groups)):
        raise IACKDFailure("join", "event, ball, and Leap trial counts differ")
    trials = []
    for index, (event, ball, leap) in enumerate(
        zip(event_trials, ball_groups, leap_groups, strict=True)
    ):
        explicit = [_identity_number(value) for value in (event.trial_id, ball.trial_id, leap.trial_id)]
        observed = {value for value in explicit if value is not None}
        if len(observed) > 1:
            raise IACKDFailure("join", "cross-stream trial identities differ")
        conditions = {value for value in (event.condition, ball.condition, leap.condition) if value}
        if len(conditions) != 1:
            raise IACKDFailure("join", "cross-stream condition is missing or inconsistent")
        if ball.move_direct is None:
            raise IACKDFailure("join", "ball move_direct is unavailable")
        leap_times = _align_stream_times(leap.timestamps, event)
        ball_times = _align_stream_times(ball.timestamps, event)
        if leap.y is None or leap.z is None:
            raise IACKDFailure("join", "Leap y/z arrays are unavailable")
        trials.append(
            TrialRecord(
                trial_id=event.trial_id or f"T{index:04d}",
                event_index=event.event_index,
                event_55_seconds=event.event_55_seconds,
                event_14_seconds=event.event_14_seconds,
                boundary_seconds=event.boundary_seconds,
                condition=next(iter(conditions)),
                leap_timestamps_seconds=leap_times,
                leap_xyz_mm=np.column_stack((leap.x, leap.y, leap.z)),
                ball_timestamps_seconds=ball_times,
                ball_x_pixels=ball.x,
                ball_move_direct=ball.move_direct,
            )
        )
    return tuple(trials)


def _annotation_trials(raw: Any) -> tuple[_EventTrial, ...]:
    rows = ["onset\tvalue"]
    for onset, description in zip(raw.annotations.onset, raw.annotations.description, strict=True):
        if _event_code(str(description)) is not None:
            rows.append(f"{float(onset):.12f}\t{description}")
    return parse_events_tsv("\n".join(rows) + "\n")


def _compare_annotation_trials(
    events: Sequence[_EventTrial],
    annotations: Sequence[_EventTrial],
    sampling_rate: float,
) -> None:
    if len(events) != len(annotations):
        raise IACKDFailure("marker", "events TSV and VMRK trial counts differ")
    tolerance = 2.0 / sampling_rate
    for left, right in zip(events, annotations, strict=True):
        for field in ("event_55_seconds", "event_14_seconds", "boundary_seconds"):
            if abs(getattr(left, field) - getattr(right, field)) > tolerance:
                raise IACKDFailure("marker", "events TSV and VMRK timing differ")


def _read_text_nofollow(path: Path, maximum_bytes: int = 32 * 1024 * 1024) -> str:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDFailure("integrity", f"input is not a regular file: {path}")
    if observed.st_size > maximum_bytes:
        raise IACKDFailure("resource", f"text input exceeds cap: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        payload = handle.read(maximum_bytes + 1)
    if len(payload) > maximum_bytes:
        raise IACKDFailure("resource", f"text input exceeds cap: {path}")
    try:
        return payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise IACKDFailure("reader", f"text input is not UTF-8: {path}") from exc


def _read_json_nofollow(path: Path, maximum_bytes: int = 1024 * 1024) -> dict[str, Any]:
    try:
        value = json.loads(_read_text_nofollow(path, maximum_bytes))
    except json.JSONDecodeError as exc:
        raise IACKDFailure("reader", f"JSON input is malformed: {path}") from exc
    if not isinstance(value, dict):
        raise IACKDFailure("reader", f"JSON input is not an object: {path}")
    return value


def _declared_unit_scale(
    sidecar: Mapping[str, Any],
    *,
    field_tokens: Sequence[str],
    unit_scales: Mapping[str, float],
    default: float,
) -> float:
    candidates: set[float] = set()

    def walk(value: Any, path: tuple[str, ...]) -> None:
        if isinstance(value, Mapping):
            for key, nested in value.items():
                walk(nested, (*path, _normalized_field(str(key))))
        elif isinstance(value, str):
            joined = "".join(path)
            if not any(
                (len(token) > 1 and token in joined) or token in path
                for token in field_tokens
            ):
                return
            normalized = _normalized_field(value)
            if normalized in unit_scales:
                candidates.add(float(unit_scales[normalized]))

    walk(sidecar, ())
    if len(candidates) > 1:
        raise IACKDFailure("stream", "sidecar declares conflicting units")
    return next(iter(candidates), default)


def _stream_scales(sidecar: Mapping[str, Any], *, kind: str) -> tuple[float, float]:
    time_scale = _declared_unit_scale(
        sidecar,
        field_tokens=("time", "timestamp"),
        unit_scales={
            "s": 1.0,
            "sec": 1.0,
            "second": 1.0,
            "seconds": 1.0,
            "ms": 1e-3,
            "millisecond": 1e-3,
            "milliseconds": 1e-3,
            "us": 1e-6,
            "microsecond": 1e-6,
            "microseconds": 1e-6,
            "ns": 1e-9,
            "nanosecond": 1e-9,
            "nanoseconds": 1e-9,
        },
        default=1.0,
    )
    if kind == "ball":
        return time_scale, 1.0
    position_scale = _declared_unit_scale(
        sidecar,
        field_tokens=("position", "coordinate", "palm", "spatial", "x", "y", "z"),
        unit_scales={
            "m": 1000.0,
            "meter": 1000.0,
            "meters": 1000.0,
            "metre": 1000.0,
            "metres": 1000.0,
            "cm": 10.0,
            "centimeter": 10.0,
            "centimeters": 10.0,
            "centimetre": 10.0,
            "centimetres": 10.0,
            "mm": 1.0,
            "millimeter": 1.0,
            "millimeters": 1.0,
            "millimetre": 1.0,
            "millimetres": 1.0,
        },
        default=1.0,
    )
    return time_scale, position_scale


def _geometry_from_files(
    electrode_path: Path,
    coordinate_path: Path,
    channel_names: Sequence[str],
) -> Any:
    np = _np()
    coordinate = _read_json_nofollow(coordinate_path)
    unit = str(coordinate.get("EEGCoordinateUnits", "")).lower()
    scales = {"m": 1.0, "cm": 0.01, "mm": 0.001}
    if unit not in scales:
        raise IACKDFailure("geometry", "EEG coordinate unit is unavailable")
    reader = csv.DictReader(io.StringIO(_read_text_nofollow(electrode_path)), delimiter="\t")
    if not reader.fieldnames:
        raise IACKDFailure("geometry", "electrodes TSV lacks a header")
    name_field = _find_field(reader.fieldnames, ("name", "channel", "electrode"))
    x_field = _find_field(reader.fieldnames, ("x",))
    y_field = _find_field(reader.fieldnames, ("y",))
    z_field = _find_field(reader.fieldnames, ("z",))
    if None in {name_field, x_field, y_field, z_field}:
        raise IACKDFailure("geometry", "electrodes TSV lacks name/x/y/z")
    positions = {}
    for row in reader:
        name = _normalize_channel(str(row[name_field]))
        if not name or name in positions:
            if name in positions:
                raise IACKDFailure("geometry", "electrode coordinate name is duplicated")
            continue
        try:
            coordinate_row = [
                float(row[x_field]) * scales[unit],
                float(row[y_field]) * scales[unit],
                float(row[z_field]) * scales[unit],
            ]
        except (TypeError, ValueError):
            continue
        if not np.isfinite(coordinate_row).all():
            continue
        positions[name] = coordinate_row
    geometry = np.full((len(channel_names), 3), np.nan, dtype="float64")
    matched = 0
    for index, name in enumerate(channel_names):
        if _normalize_channel(name) in positions:
            geometry[index] = positions[_normalize_channel(name)]
            matched += 1
    if matched < 32:
        raise IACKDFailure("geometry", "fewer than 32 channel positions are available")
    return geometry


def _run_groups(inventory: Mapping[str, Any]) -> tuple[dict[str, str], ...]:
    available = {row["path"] for row in inventory["selected_objects"]}
    groups = []
    for subject in load_registered_contract()["dataset_binding"]["participant_ids"]:
        for hand in ("left", "right"):
            for run in _synthetic_runs(subject):
                eeg_base = f"{subject}/eeg/{subject}_task-ihc_acq-{hand}_run-{run}"
                behavior_base = f"{subject}/sourcedata/beh/{subject}_task-ihc_run-{run}_hand-{hand}"
                geometry_base = f"{subject}/eeg/{subject}_acq-{hand}_space-CapTrak"
                paths = {
                    "subject": subject,
                    "hand": hand,
                    "run": run,
                    "vhdr": f"{eeg_base}_eeg.vhdr",
                    "signal": f"{eeg_base}_eeg.eeg",
                    "marker": f"{eeg_base}_eeg.vmrk",
                    "eeg_sidecar": f"{eeg_base}_eeg.json",
                    "channels": f"{eeg_base}_channels.tsv",
                    "events": f"{eeg_base}_events.tsv",
                    "ball": f"{behavior_base}_ball.tsv",
                    "ball_sidecar": f"{behavior_base}_ball.json",
                    "leap": f"{behavior_base}_leap.tsv",
                    "leap_sidecar": f"{behavior_base}_leap.json",
                    "electrodes": f"{geometry_base}_electrodes.tsv",
                    "coordsystem": f"{geometry_base}_coordsystem.json",
                }
                missing = [value for key, value in paths.items() if key not in {"subject", "hand", "run"} and value not in available]
                if missing:
                    raise IACKDFailure("inventory", f"run companion inventory is incomplete: {missing}")
                groups.append(paths)
    if len(groups) != 128:
        raise IACKDFailure("inventory", "run grouping did not produce 128 runs")
    return tuple(groups)


def _validate_channels_tsv(path: Path, raw_names: Sequence[str]) -> None:
    reader = csv.DictReader(io.StringIO(_read_text_nofollow(path)), delimiter="\t")
    if not reader.fieldnames:
        raise IACKDFailure("channel", "channels TSV lacks a header")
    name_field = _find_field(reader.fieldnames, ("name", "channel", "channel_name"))
    type_field = _find_field(reader.fieldnames, ("type", "channel_type"))
    if name_field is None or type_field is None:
        raise IACKDFailure("channel", "channels TSV lacks name/type")
    rows = list(reader)
    names = [str(row[name_field]) for row in rows]
    if [_normalize_channel(name) for name in names] != [
        _normalize_channel(name) for name in raw_names
    ]:
        raise IACKDFailure("channel", "channels TSV and BrainVision order differ")
    types = [str(row[type_field]).upper() for row in rows]
    eeg_count = sum(value == "EEG" for value in types)
    if eeg_count not in {32, 34}:
        raise IACKDFailure("channel", "channels TSV EEG count is incompatible")


def load_run_from_bundle(bundle: Path, paths: Mapping[str, str]) -> RunRecord:
    """Read one exact BrainVision run and its synchronized source streams."""

    np = _np()
    try:
        import mne
    except ImportError as exc:
        raise IACKDRefusal("real IACKD parsing requires MNE") from exc
    vhdr = bundle / acquisition._safe_relative_path(paths["vhdr"])
    raw = mne.io.read_raw_brainvision(vhdr, preload=False, verbose="ERROR")
    try:
        sampling_rate = float(raw.info["sfreq"])
        if not math.isclose(sampling_rate, 1024.0, abs_tol=1e-9):
            raise IACKDFailure("reader", "BrainVision sampling rate is not 1,024 Hz")
        channel_names = tuple(str(value) for value in raw.ch_names)
        normalized = {_normalize_channel(name) for name in channel_names}
        required = {_normalize_channel(name) for name in REQUIRED_NON_EEG}
        if len(channel_names) != 36 or not required.issubset(normalized):
            raise IACKDFailure("reader", "BrainVision channel inventory is not 32+4")
        channel_types = tuple(
            "eog"
            if _normalize_channel(name) in {_normalize_channel("HEOG"), _normalize_channel("VEOG")}
            else "misc"
            if _normalize_channel(name) in {_normalize_channel("M1"), _normalize_channel("M2")}
            else "eeg"
            for name in channel_names
        )
        values = raw.get_data().astype("float64", copy=False)
        annotations = _annotation_trials(raw)
    finally:
        raw.close()
    _validate_channels_tsv(
        bundle / acquisition._safe_relative_path(paths["channels"]), channel_names
    )
    sidecar = _read_json_nofollow(
        bundle / acquisition._safe_relative_path(paths["eeg_sidecar"])
    )
    sidecar_rate = sidecar.get("SamplingFrequency")
    if sidecar_rate is not None and not math.isclose(float(sidecar_rate), 1024.0, abs_tol=1e-9):
        raise IACKDFailure("reader", "EEG sidecar sampling rate mismatch")
    geometry = _geometry_from_files(
        bundle / acquisition._safe_relative_path(paths["electrodes"]),
        bundle / acquisition._safe_relative_path(paths["coordsystem"]),
        channel_names,
    )
    events = parse_events_tsv(
        _read_text_nofollow(bundle / acquisition._safe_relative_path(paths["events"]))
    )
    _compare_annotation_trials(events, annotations, sampling_rate)
    ball_sidecar = _read_json_nofollow(
        bundle / acquisition._safe_relative_path(paths["ball_sidecar"])
    )
    leap_sidecar = _read_json_nofollow(
        bundle / acquisition._safe_relative_path(paths["leap_sidecar"])
    )
    ball_time_scale, ball_position_scale = _stream_scales(ball_sidecar, kind="ball")
    leap_time_scale, leap_position_scale = _stream_scales(leap_sidecar, kind="leap")
    ball = _stream_groups(
        _read_text_nofollow(bundle / acquisition._safe_relative_path(paths["ball"])),
        kind="ball",
        time_scale_to_seconds=ball_time_scale,
        position_scale=ball_position_scale,
    )
    leap = _stream_groups(
        _read_text_nofollow(bundle / acquisition._safe_relative_path(paths["leap"])),
        kind="leap",
        time_scale_to_seconds=leap_time_scale,
        position_scale=leap_position_scale,
    )
    trials = reconcile_trials(events, ball, leap)
    return RunRecord(
        subject=paths["subject"],
        hand=paths["hand"],
        run=paths["run"],
        sampling_rate_hz=sampling_rate,
        channel_names=channel_names,
        channel_types=channel_types,
        channel_geometry_m=geometry,
        signal_volts=np.asarray(values, dtype="float64"),
        trials=trials,
    )


def _hash_regular_nofollow(path: Path) -> tuple[int, str]:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDFailure("integrity", f"payload is not a regular file: {path}")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    digest = hashlib.sha256()
    total = 0
    with os.fdopen(descriptor, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            total += len(chunk)
            digest.update(chunk)
    return total, digest.hexdigest()


def _exact_bundle_membership(bundle: Path, expected_paths: Sequence[str]) -> dict[str, int]:
    observed_root = os.lstat(bundle)
    if stat.S_ISLNK(observed_root.st_mode) or not stat.S_ISDIR(observed_root.st_mode):
        raise IACKDFailure("integrity", "bundle root is not a regular directory")
    observed = []
    directory_count = 0
    for root, directories, filenames in os.walk(bundle, followlinks=False):
        current = Path(root)
        directory_count += len(directories)
        if any((current / name).is_symlink() for name in directories):
            raise IACKDFailure("integrity", "bundle contains symlink directory")
        for filename in filenames:
            path = current / filename
            if path.is_symlink():
                raise IACKDFailure("integrity", "bundle contains symlink file")
            observed.append(path.relative_to(bundle).as_posix())
    if sorted(observed) != sorted(expected_paths):
        raise IACKDFailure("integrity", "bundle membership differs from registration")
    return {"file_stats": len(observed), "directory_stats": directory_count}


def _verify_manifest(
    path: Path,
    inventory: Mapping[str, Any],
) -> tuple[dict[str, str], str]:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise IACKDFailure("integrity", "acquisition manifest is not a regular file")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as handle:
        payload = handle.read(8 * 1024 * 1024 + 1)
    if len(payload) > 8 * 1024 * 1024:
        raise IACKDFailure("resource", "acquisition manifest exceeds 8 MiB")
    try:
        manifest = json.loads(payload)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IACKDFailure("integrity", "acquisition manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise IACKDFailure("integrity", "acquisition manifest root must be an object")
    if manifest.get("schema_name") != "neurodecodekit.iackd_acquisition_manifest":
        raise IACKDFailure("integrity", "acquisition manifest schema mismatch")
    if manifest.get("status") != "passed":
        raise IACKDFailure("integrity", "acquisition manifest is not passed")
    if manifest.get("canonical_inventory_sha256") != inventory["selection"][
        "canonical_identity_sha256"
    ]:
        raise IACKDFailure("integrity", "acquisition manifest inventory hash mismatch")
    expected = {
        row["path"]: (row["size_bytes"], row["etag"], row["last_modified"])
        for row in inventory["selected_objects"]
    }
    actual = {}
    hashes = {}
    records = manifest.get("file_records", [])
    if not isinstance(records, list) or len(records) != len(expected):
        raise IACKDFailure("integrity", "acquisition manifest record count mismatch")
    for row in records:
        digest = str(row.get("observed_local_sha256", ""))
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise IACKDFailure("integrity", "manifest SHA-256 is malformed")
        path_value = str(row["path"])
        if path_value in actual:
            raise IACKDFailure("integrity", "acquisition manifest contains a duplicate path")
        actual[path_value] = (
            int(row["size_bytes"]),
            str(row["registered_etag"]),
            str(row["registered_last_modified"]),
        )
        hashes[path_value] = digest
        if row.get("stream_hash_passes") != 1 or row.get("post_write_content_opens") != 0:
            raise IACKDFailure("integrity", "manifest acquisition counters mismatch")
    if actual != expected:
        raise IACKDFailure("integrity", "acquisition manifest object identities differ")
    return hashes, _sha256_bytes(payload)


def run_registered_prediction_execution(
    *,
    repo_root: str | Path,
    evidence: ImplementationEvidence,
    environ: Mapping[str, str],
) -> dict[str, Any]:
    """Consume the one real target-blind IACKD analysis through public freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    inventory = acquisition.load_registered_inventory(root)
    _check_thread_environment(environ)
    implementation = acquisition._validate_implementation_registry(root, evidence)
    dependency_versions()
    bundle = root / BUNDLE_RELATIVE_PATH
    manifest_path = root / ACQUISITION_MANIFEST_RELATIVE_PATH
    output = root / EXECUTION_ROOT_RELATIVE_PATH
    freeze_path = root / FREEZE_RELATIVE_PATH
    for path in (bundle, manifest_path, output, freeze_path):
        acquisition._assert_safe_path_chain(root, path)
    if output.exists() or output.is_symlink() or freeze_path.exists() or freeze_path.is_symlink():
        raise IACKDRefusal("execution output or public freeze already exists")
    started = time.monotonic()
    output.mkdir(parents=True, exist_ok=False)
    _write_json_exclusive(
        output / EXECUTION_CONSUMED_NAME,
        {
            "schema_name": "neurodecodekit.iackd_execution_consumed",
            "schema_version": SCHEMA_VERSION,
            "retry_allowed": False,
            "rerun_allowed": False,
        },
        64 * 1024,
    )
    expected_paths = [row["path"] for row in inventory["selected_objects"]]
    membership = _exact_bundle_membership(bundle, expected_paths)
    manifest_hashes, manifest_sha256 = _verify_manifest(manifest_path, inventory)
    source_hashes = {}
    caps = contract["resource_caps"]["analysis_and_scoring"]
    for row in sorted(inventory["selected_objects"], key=lambda value: value["path"]):
        path = bundle / acquisition._safe_relative_path(row["path"])
        size, digest = _hash_regular_nofollow(path)
        if size != row["size_bytes"] or digest != manifest_hashes[row["path"]]:
            raise IACKDFailure("integrity", f"payload hash mismatch: {row['path']}")
        source_hashes[row["path"]] = digest
        if time.monotonic() - started > caps["wall_time_seconds_through_prediction_freeze"]:
            raise IACKDFailure("resource", "analysis wall cap exceeded during hash pass")
        if _peak_rss_bytes() > caps["peak_rss_bytes"]:
            raise IACKDFailure("resource", "analysis RSS cap exceeded during hash pass")

    def records():
        for paths in _run_groups(inventory):
            yield load_run_from_bundle(bundle, paths)
            if time.monotonic() - started > caps["wall_time_seconds_through_prediction_freeze"]:
                raise IACKDFailure("resource", "analysis wall cap exceeded during parse")
            if _peak_rss_bytes() > caps["peak_rss_bytes"]:
                raise IACKDFailure("resource", "analysis RSS cap exceeded during parse")

    derivative = extract_records_to_derivatives(
        records(),
        output,
        source_hashes=source_hashes,
        manifest_sha256=manifest_sha256,
        maximum_output_bytes=caps["private_generated_output_bytes"],
        allow_existing_consumed_marker=True,
    )
    freeze = run_target_blind_predictions(
        output_root=output,
        freeze_path=freeze_path,
        source_kind="real_IACKD",
        implementation_evidence=evidence,
        implementation_registry=implementation,
        maximum_output_bytes=caps["private_generated_output_bytes"],
        execution_started_monotonic=started,
        upstream_access_counters={
            "acquisition_manifest_reads": 1,
            "bundle_root_stats": 1,
            "bundle_membership_file_stats": membership["file_stats"],
            "bundle_membership_directory_stats": membership["directory_stats"],
            "real_object_hash_passes": 1340,
            "real_brainvision_semantic_parses": 128,
            "real_header_marker_event_reads": 128,
            "real_signal_reads": 128,
            "real_ball_stream_parses": 128,
            "real_leap_stream_parses": 128,
            "firewalled_final_rows_materialized": derivative["final_rows"],
        },
    )
    runtime = time.monotonic() - started
    if runtime > caps["wall_time_seconds_through_prediction_freeze"]:
        raise IACKDFailure("resource", "analysis wall cap exceeded")
    if _peak_rss_bytes() > caps["peak_rss_bytes"]:
        raise IACKDFailure("resource", "analysis RSS cap exceeded")
    private_bytes = _directory_bytes(output)
    if private_bytes > caps["private_generated_output_bytes"]:
        raise IACKDFailure("resource", "private output cap exceeded")
    return {
        "status": freeze["status"],
        "condition_count": len(CONDITION_IDS),
        "participant_hand_units": 30,
        "operation_counters": freeze["operation_counters"],
        "runtime_seconds": round(runtime, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "generated_private_bytes": private_bytes,
        "input_payload_bytes": contract["dataset_binding"]["exact_selected_payload_bytes"],
        "raw_data_reads": 1340,
        "real_cache_reads": 0,
        "model_runs": 420,
        "training_runs": 300,
        "producer_is_causal": True,
        "end_to_end_latency_measured": False,
        "warnings": freeze["warnings"],
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
    """Open both sealed target views once after a remotely green freeze."""

    root = Path(repo_root).resolve()
    contract = load_registered_contract(root)
    load_registered_decision(root)
    _check_thread_environment(environ)
    if _git_head(root) != evidence.freeze_commit:
        raise IACKDRefusal("current HEAD differs from freeze evidence")
    if min(
        evidence.freeze_ci_run_id,
        evidence.base_python_job_id,
        evidence.optional_neuro_job_id,
    ) <= 0:
        raise IACKDRefusal("positive freeze CI identifiers are required")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", DECISION_COMMIT, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise IACKDRefusal("green authorization decision is not a freeze ancestor")
    if subprocess.run(
        ("git", "status", "--porcelain", "--untracked-files=no"),
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip():
        raise IACKDRefusal("tracked worktree must be clean before scoring")
    output = root / EXECUTION_ROOT_RELATIVE_PATH
    freeze_path = root / FREEZE_RELATIVE_PATH
    result_path = root / RESULT_RELATIVE_PATH
    consumed_path = output / SCORING_CONSUMED_NAME
    if consumed_path.exists() or result_path.exists() or result_path.is_symlink():
        raise IACKDRefusal("IACKD score is already consumed")
    if subprocess.run(
        ("git", "cat-file", "-e", f"HEAD:{FREEZE_RELATIVE_PATH}"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise IACKDRefusal("public prediction freeze is not tracked at HEAD")
    freeze = _read_json_nofollow(freeze_path, 2 * 1024 * 1024)
    validate_public_freeze(freeze)
    if freeze.get("source_kind") != "real_IACKD":
        raise IACKDRefusal("only the real IACKD freeze may be scored")
    implementation_commit = freeze.get("implementation_commit")
    if not isinstance(implementation_commit, str) or len(implementation_commit) != 40:
        raise IACKDRefusal("freeze implementation commit binding is unavailable")
    if subprocess.run(
        ("git", "merge-base", "--is-ancestor", implementation_commit, "HEAD"),
        cwd=root,
        check=False,
        capture_output=True,
    ).returncode:
        raise IACKDRefusal("freeze implementation commit is not an ancestor")
    private_path = output / PRIVATE_PREDICTIONS_NAME
    sealed_path = output / SEALED_TARGET_NAME
    final_path = output / FINAL_DERIVATIVE_NAME
    physiology_path = output / PHYSIOLOGY_SUMMARY_NAME
    _write_json_exclusive(
        consumed_path,
        {
            "schema_name": "neurodecodekit.iackd_score_consumed",
            "schema_version": SCHEMA_VERSION,
            "freeze_commit": evidence.freeze_commit,
            "retry_allowed": False,
            "rerun_allowed": False,
        },
        64 * 1024,
    )
    if _file_sha256(private_path) != freeze["private_prediction_payload_sha256"]:
        raise IACKDFailure("integrity", "private prediction payload hash mismatch")
    if _file_sha256(sealed_path) != freeze["sealed_target_sha256"]:
        raise IACKDFailure("integrity", "sealed target payload hash mismatch")
    if _file_sha256(final_path) != freeze["prediction_derivative_sha256"]:
        raise IACKDFailure("integrity", "target-free final derivative hash mismatch")
    if _file_sha256(physiology_path) != freeze["physiology_summary_sha256"]:
        raise IACKDFailure("integrity", "physiology summary hash mismatch")
    private = _read_json_nofollow(private_path, 512 * 1024 * 1024)
    sealed = _load_npz(sealed_path)
    final = _load_npz(final_path, target_free=True)
    physiology = _load_npz(physiology_path, target_free=True)
    physiology_content_sha256 = _canonical_sha256(
        {key: _array_sha256(value) for key, value in sorted(physiology.items())}
    )
    if physiology_content_sha256 != freeze["physiology_content_sha256"]:
        raise IACKDFailure("integrity", "physiology content hash mismatch")
    result = score_private_predictions(
        freeze=freeze,
        private_predictions=private,
        sealed=sealed,
        final=final,
        physiology=physiology,
    )
    result.update(
        {
            "freeze_commit": evidence.freeze_commit,
            "freeze_ci_run_id": evidence.freeze_ci_run_id,
            "base_python_job_id": evidence.base_python_job_id,
            "optional_neuro_job_id": evidence.optional_neuro_job_id,
            "input_payload_bytes": contract["dataset_binding"]["exact_selected_payload_bytes"],
            "public_result_bytes": 0,
        }
    )
    for _ in range(8):
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if result["public_result_bytes"] == len(payload):
            break
        result["public_result_bytes"] = len(payload)
    else:
        raise IACKDFailure("output", "public result byte measurement did not converge")
    if len(payload) > contract["resource_caps"]["analysis_and_scoring"][
        "public_freeze_and_result_bytes"
    ]:
        raise IACKDFailure("output", "public result exceeds cap")
    _write_json_exclusive(result_path, result, 2 * 1024 * 1024)
    return result
