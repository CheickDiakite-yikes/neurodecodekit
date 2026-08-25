"""Target-firewalled Stage Q semantic qualification for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import importlib.metadata
import io
import json
import math
import os
import resource
import shutil
import stat
import subprocess
import tempfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


LANE_ID = "BNCI-C3C5-1-Q"
SCHEMA_VERSION = "0.1.0"
PARTICIPANTS = tuple(f"A{index:02d}" for index in range(1, 10))
SESSIONS = ("T", "E")
CLASSES = ("left_hand", "right_hand", "feet", "tongue")
UPSTREAM_CLASSES = ("left hand", "right hand", "feet", "tongue")
EEG_CHANNELS = (
    "Fz", "FC3", "FC1", "FCz", "FC2", "FC4", "C5", "C3", "C1", "Cz",
    "C2", "C4", "C6", "CP3", "CP1", "CPz", "CP2", "CP4", "P1", "Pz",
    "P2", "POz",
)
EOG_CHANNELS = ("EOG1", "EOG2", "EOG3")
ALL_CHANNELS = EEG_CHANNELS + EOG_CHANNELS
VIEW_CHANNELS = {
    "central_EEG": (
        "FC3", "FC1", "FCz", "FC2", "FC4", "C5", "C3", "C1", "Cz", "C2",
        "C4", "C6", "CP3", "CP1", "CPz", "CP2", "CP4",
    ),
    "frontal_EEG": ("Fz", "FC3", "FC1", "FCz", "FC2", "FC4"),
    "posterior_EEG": ("CP3", "CP1", "CPz", "CP2", "CP4", "P1", "Pz", "P2", "POz"),
}
EEG_BANDS = ((8.0, 12.0), (12.0, 16.0), (16.0, 24.0), (24.0, 30.0))
EOG_BANDS = ((0.5, 4.0), (4.0, 8.0))
FEATURE_DIMENSIONS = {
    "E1": 88,
    "E2": 1012,
    "P": 102,
    "timing_only": 5,
    "pre_cue_EEG": 88,
    "early_cue_EEG": 88,
    "central_EEG": 68,
    "frontal_EEG": 24,
    "posterior_EEG": 36,
    "D_E1": 88,
    "D_E2": 1012,
    "rotated_E1": 88,
    "rotated_E2": 1012,
}

RESEARCH_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json"
)
RESEARCH_SHA256 = "5a333709dbbf8c2e30f33c9f47240d8830d34b78ac9eda5ae22ede68a751ded2"
CONTRACT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_contract.v0.json"
)
CONTRACT_SHA256 = "e11dad351f5a4736dc6ac3ffdad28a65e37b18b40c5bfa9e861f5b0754ad2b74"
DECISION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_authorization_decision.v0.json"
)
DECISION_SHA256 = "687ed0d5afa64ba7c34ab86bf3e0c4f79d08d21041dd1e9e6aa3642629d0f559"
STAGE_A_RESULT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_a_redirect_recovery_result.v0.json"
)
STAGE_A_RESULT_SHA256 = "66232ceeb3cc61b3402d1d01970d6630b5e4a25cf7685e5c65f8f50f8f952ae2"
STAGE_A_RESULT_COMMIT = "96d7f0569a54b05f8031d2e3943658ef598e38a5"
STAGE_A_RESULT_CI_RUN_ID = 32_814_564_120
STAGE_A_RESULT_BASE_JOB_ID = 97_700_176_631
STAGE_A_RESULT_OPTIONAL_JOB_ID = 97_700_176_787
ACTIVATION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_stage_q_implementation_activation.v0.json"
)
STAGE_A_BUNDLE_RELATIVE_PATH = Path(
    ".codex_work/bnci_c3c5/stage_a_redirect_recovery_payload_v1"
)
STAGE_Q_OUTPUT_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_q_v0")
STAGE_Q_MARKER_RELATIVE_PATH = Path(".codex_work/bnci_c3c5/stage_q_v0.consumed.json")
STAGE_Q_RECEIPT_RELATIVE_PATH = STAGE_Q_OUTPUT_RELATIVE_PATH / "receipt.private.v0.json"

THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
EXPECTED_VERSIONS = {"numpy": "2.5.2", "scipy": "1.18.0"}
MAT_FILE_COUNT = 18
TASK_RUNS_PER_FILE = 6
TRIALS_PER_RUN = 48
ROWS_TOTAL = 5_184
SOURCE_ROWS_PER_FOLD = 4_608
HELD_OUT_E_ROWS_PER_FOLD = 288
SAMPLING_RATE_HZ = 250.0
PRIVATE_OUTPUT_CAP_BYTES = 536_870_912
PUBLIC_OUTPUT_CAP_BYTES = 4_194_304
PEAK_RSS_CAP_BYTES = 1_073_741_824
RUNTIME_CAP_SECONDS = 3_600.0
NETWORK_BYTES = 0


class BNCIStageQRefusal(RuntimeError):
    """Fail-closed Stage Q refusal."""


@dataclass(frozen=True)
class PayloadMember:
    relative_path: str
    bytes: int
    sha256: str


@dataclass(frozen=True)
class TaskRun:
    signal: Any
    starts: Any
    targets: Any
    artifacts: Any
    artifacts_available: bool


@dataclass
class OperationLedger:
    private_manifest_opens: int = 0
    MAT_content_opens: int = 0
    MAT_semantic_parses: int = 0
    task_signal_runs_read: int = 0
    calibration_signal_runs_read: int = 0
    target_vectors_isolated: int = 0
    model_runs: int = 0
    training_runs: int = 0
    prediction_sets: int = 0
    target_deliveries: int = 0
    scores: int = 0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_bound_json(root: Path, relative_path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = (root / relative_path).read_bytes()
    if _sha256(payload) != expected_sha256:
        raise BNCIStageQRefusal(f"bound public artifact changed: {relative_path}")
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise BNCIStageQRefusal(f"bound public artifact is not an object: {relative_path}")
    return parsed


def load_public_bindings(root: str | Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    repo = Path(root).resolve()
    research = _load_bound_json(repo, RESEARCH_RELATIVE_PATH, RESEARCH_SHA256)
    contract = _load_bound_json(repo, CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    decision = _load_bound_json(repo, DECISION_RELATIVE_PATH, DECISION_SHA256)
    stage_a = _load_bound_json(repo, STAGE_A_RESULT_RELATIVE_PATH, STAGE_A_RESULT_SHA256)
    if research.get("research_id") != "BNCI-C3C5-1":
        raise BNCIStageQRefusal("research identity changed")
    if contract.get("contract_id") != "BNCI-C3C5-1":
        raise BNCIStageQRefusal("contract identity changed")
    if decision.get("authorization", {}).get("Q_one_target_blind_qualification_after_A_manifest_green") is not True:
        raise BNCIStageQRefusal("Stage Q authority is unavailable")
    if stage_a.get("execution", {}).get("complete_bundle_created") is not True:
        raise BNCIStageQRefusal("Stage A complete-bundle proof is unavailable")
    return research, contract, decision, stage_a


def registered_members(root: str | Path) -> tuple[PayloadMember, ...]:
    research, _contract, _decision, _stage_a = load_public_bindings(root)
    rows = research.get("selected_original_payload", {}).get("members")
    if not isinstance(rows, list) or len(rows) != MAT_FILE_COUNT:
        raise BNCIStageQRefusal("registered MAT member table changed")
    members = tuple(
        PayloadMember(str(row["path"]), int(row["bytes"]), str(row["sha256"]))
        for row in rows
    )
    if sum(member.bytes for member in members) != 779_873_919:
        raise BNCIStageQRefusal("registered MAT payload bytes changed")
    if len({member.relative_path for member in members}) != len(members):
        raise BNCIStageQRefusal("registered MAT member path is duplicated")
    return members


def assert_exact_versions() -> dict[str, str]:
    observed = {name: importlib.metadata.version(name) for name in EXPECTED_VERSIONS}
    if observed != EXPECTED_VERSIONS:
        raise BNCIStageQRefusal(f"Stage Q numerical version set changed: {observed}")
    return observed


def assert_single_thread_environment(environ: Mapping[str, str]) -> None:
    changed = {name: environ.get(name) for name in THREAD_ENVIRONMENT if environ.get(name) != "1"}
    if changed:
        raise BNCIStageQRefusal(f"one-thread environment is not frozen: {sorted(changed)}")


def _np():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Stage Q arrays require: pip install -e '.[classical]'") from exc
    return np


def _scipy_io():
    try:
        from scipy.io import loadmat, savemat
    except ImportError as exc:
        raise RuntimeError("Stage Q MAT support requires: pip install -e '.[classical]'") from exc
    return loadmat, savemat


def _signal_functions():
    try:
        from scipy.signal import butter, sosfilt
    except ImportError as exc:
        raise RuntimeError("Stage Q filters require: pip install -e '.[classical]'") from exc
    return butter, sosfilt


def peak_process_rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if os.uname().sysname == "Darwin" else value * 1024)


def _field(run: Any, name: str) -> Any:
    if isinstance(run, Mapping):
        if name not in run:
            raise BNCIStageQRefusal(f"MAT task run field is absent: {name}")
        return run[name]
    if not hasattr(run, name):
        raise BNCIStageQRefusal(f"MAT task run field is absent: {name}")
    return getattr(run, name)


def _optional_field(run: Any, name: str) -> Any | None:
    if isinstance(run, Mapping):
        return run.get(name)
    return getattr(run, name, None)


def _normalise_classes(raw: Any) -> tuple[str, ...]:
    np = _np()
    values = tuple(str(value).strip() for value in np.asarray(raw).reshape(-1))
    normalised = tuple(value.lower().replace(" ", "_") for value in values)
    if normalised != CLASSES:
        raise BNCIStageQRefusal("MAT public class order differs")
    return normalised


def parse_verified_mat_payload(payload: bytes, member: PayloadMember) -> tuple[list[TaskRun], int]:
    """Parse one already-read exact member without a second filesystem open."""

    np = _np()
    loadmat, _savemat = _scipy_io()
    if len(payload) != member.bytes or _sha256(payload) != member.sha256:
        raise BNCIStageQRefusal("MAT payload identity differs before semantic parse")
    try:
        parsed = loadmat(
            io.BytesIO(payload),
            struct_as_record=False,
            squeeze_me=True,
            verify_compressed_data_integrity=True,
        )
    except Exception as exc:
        raise BNCIStageQRefusal("MAT semantic parse failed") from exc
    if set(parsed) - {"__header__", "__version__", "__globals__", "data"}:
        raise BNCIStageQRefusal("MAT top-level variable inventory differs")
    if "data" not in parsed:
        raise BNCIStageQRefusal("MAT top-level data key is unavailable")
    raw = parsed["data"]
    runs = list(raw.reshape(-1)) if isinstance(raw, np.ndarray) else [raw]
    task_runs: list[TaskRun] = []
    calibration_structs = 0
    for run in runs:
        starts = np.asarray(_field(run, "trial")).reshape(-1)
        if starts.size == 0:
            calibration_structs += 1
            continue
        signal = np.asarray(_field(run, "X"))
        targets = np.asarray(_field(run, "y")).reshape(-1)
        artifacts_raw = _optional_field(run, "artifacts")
        artifacts_available = artifacts_raw is not None and np.asarray(artifacts_raw).size > 0
        artifacts = (
            np.asarray(artifacts_raw).reshape(-1)
            if artifacts_available
            else np.zeros(TRIALS_PER_RUN, dtype="uint8")
        )
        if signal.ndim != 2 or signal.shape[1] != len(ALL_CHANNELS):
            raise BNCIStageQRefusal("MAT task signal channel width differs")
        if not np.issubdtype(signal.dtype, np.number) or not np.isfinite(signal).all():
            raise BNCIStageQRefusal("MAT task signal contains invalid values")
        if float(_field(run, "fs")) != SAMPLING_RATE_HZ:
            raise BNCIStageQRefusal("MAT task sampling rate differs")
        _normalise_classes(_field(run, "classes"))
        if starts.shape != (TRIALS_PER_RUN,) or targets.shape != (TRIALS_PER_RUN,):
            raise BNCIStageQRefusal("MAT task trial or target length differs")
        if artifacts.shape != (TRIALS_PER_RUN,):
            raise BNCIStageQRefusal("MAT artifact flag length differs")
        if (
            not np.issubdtype(starts.dtype, np.number)
            or not np.isfinite(starts).all()
            or not np.equal(starts, np.floor(starts)).all()
            or int(starts.min()) < 1
        ):
            raise BNCIStageQRefusal("MAT trial indices are not finite one-based integers")
        if (
            not np.issubdtype(targets.dtype, np.number)
            or not np.isfinite(targets).all()
            or not np.equal(targets, np.floor(targets)).all()
        ):
            raise BNCIStageQRefusal("MAT targets are not finite integers")
        zero_based = starts.astype("int64") - 1
        if np.any(np.diff(zero_based) < 1500) or int(zero_based[-1] + 1500) > signal.shape[0]:
            raise BNCIStageQRefusal("MAT frozen trial windows are incomplete or unordered")
        if set(int(value) for value in targets) != {1, 2, 3, 4}:
            raise BNCIStageQRefusal("MAT target inventory differs")
        if any(int((targets == value).sum()) != 12 for value in range(1, 5)):
            raise BNCIStageQRefusal("MAT task class balance differs")
        if (
            not np.issubdtype(artifacts.dtype, np.number)
            or not np.isfinite(artifacts).all()
            or not np.equal(artifacts, np.floor(artifacts)).all()
            or not set(int(value) for value in artifacts).issubset({0, 1})
        ):
            raise BNCIStageQRefusal("MAT artifact flags are invalid")
        task_runs.append(
            TaskRun(
                signal=np.asarray(signal, dtype="float64"),
                starts=zero_based,
                targets=targets.astype("uint8"),
                artifacts=artifacts.astype("uint8"),
                artifacts_available=artifacts_available,
            )
        )
    if len(task_runs) != TASK_RUNS_PER_FILE:
        raise BNCIStageQRefusal("MAT nonempty task run count differs")
    return task_runs, calibration_structs


def _causal_filter(values: Any, bands: Sequence[tuple[float, float]]) -> list[Any]:
    np = _np()
    butter, sosfilt = _signal_functions()
    source = np.asarray(values, dtype="float64")
    if source.ndim != 2 or not np.isfinite(source).all():
        raise BNCIStageQRefusal("causal filter input is malformed")
    outputs = []
    for low, high in bands:
        sos = butter(4, (low, high), btype="bandpass", fs=SAMPLING_RATE_HZ, output="sos")
        outputs.append(sosfilt(sos, source, axis=0))
    return outputs


def _log_variance(values: Any) -> Any:
    np = _np()
    return np.log(np.maximum(np.var(values, axis=0, ddof=0), 1e-12))


def _matrix_log_spd(matrix: Any) -> Any:
    np = _np()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    if np.any(eigenvalues <= 0.0):
        raise BNCIStageQRefusal("E2 covariance is not positive definite")
    return (eigenvectors * np.log(eigenvalues)) @ eigenvectors.T


def _e2_from_filtered(filtered: Sequence[Any], start: int, stop: int) -> Any:
    np = _np()
    triangle = np.triu_indices(22)
    features = []
    for values in filtered:
        window = values[start:stop]
        covariance = (window.T @ window) / float(window.shape[0])
        trace = float(np.trace(covariance))
        if not math.isfinite(trace) or trace <= 0.0:
            raise BNCIStageQRefusal("E2 covariance trace is invalid")
        covariance = covariance / trace + np.eye(22) * 1e-5
        features.append(_matrix_log_spd(covariance)[triangle])
    output = np.concatenate(features)
    if output.shape != (FEATURE_DIMENSIONS["E2"],):
        raise BNCIStageQRefusal("E2 feature dimension differs")
    return output


def _eog_from_filtered(filtered: Sequence[Any], start: int, stop: int) -> Any:
    np = _np()
    features: list[float] = []
    for values in filtered:
        window = values[start:stop]
        bins = np.array_split(window, 8, axis=0)
        for channel in range(3):
            for item in bins:
                y = item[:, channel]
                x = np.arange(y.size, dtype="float64")
                centered = x - x.mean()
                slope = float(centered @ (y - y.mean()) / (centered @ centered))
                features.extend((float(y.mean()), slope))
            features.append(float(_log_variance(window[:, [channel]])[0]))
    output = np.asarray(features, dtype="float64")
    if output.shape != (FEATURE_DIMENSIONS["P"],):
        raise BNCIStageQRefusal("P feature dimension differs")
    return output


def rotate_feature_channels(feature: Any, family: str) -> Any:
    np = _np()
    values = np.asarray(feature, dtype="float64")
    if family == "E1":
        if values.shape != (88,):
            raise BNCIStageQRefusal("E1 rotation shape differs")
        return np.roll(values.reshape(4, 22), 7, axis=1).reshape(-1)
    if family != "E2" or values.shape != (1012,):
        raise BNCIStageQRefusal("E2 rotation shape differs")
    triangle = np.triu_indices(22)
    permutation = np.roll(np.arange(22), 7)
    output = []
    for band in values.reshape(4, 253):
        matrix = np.zeros((22, 22), dtype="float64")
        matrix[triangle] = band
        matrix[(triangle[1], triangle[0])] = band
        output.append(matrix[np.ix_(permutation, permutation)][triangle])
    return np.concatenate(output)


def extract_target_free_run_features(signal: Any, starts: Any) -> dict[str, Any]:
    """Extract frozen features without accepting a target or artifact argument."""

    np = _np()
    values = np.asarray(signal, dtype="float64")
    trial_starts = np.asarray(starts, dtype="int64")
    if values.ndim != 2 or values.shape[1] != 25 or trial_starts.shape != (48,):
        raise BNCIStageQRefusal("target-free run input differs")
    referenced = values[:, :22] - values[:, :22].mean(axis=1, keepdims=True)
    eeg_filtered = _causal_filter(referenced, EEG_BANDS)
    eog_filtered = _causal_filter(values[:, 22:25], EOG_BANDS)
    rows: dict[str, list[Any]] = {name: [] for name in FEATURE_DIMENSIONS if not name.startswith(("D_", "rotated_"))}
    for trial_index, start_value in enumerate(trial_starts):
        start = int(start_value)
        late_start, late_stop = start + 875, start + 1500
        e1 = np.concatenate([_log_variance(band[late_start:late_stop]) for band in eeg_filtered])
        rows["E1"].append(e1)
        rows["E2"].append(_e2_from_filtered(eeg_filtered, late_start, late_stop))
        rows["P"].append(_eog_from_filtered(eog_filtered, start + 500, start + 1500))
        previous_interval = 0.0 if trial_index == 0 else (start - int(trial_starts[trial_index - 1])) / 250.0
        rows["timing_only"].append(
            np.asarray([0.0, 0.0, float(trial_index), start / 250.0, previous_interval])
        )
        rows["pre_cue_EEG"].append(
            np.concatenate([_log_variance(band[start : start + 500]) for band in eeg_filtered])
        )
        rows["early_cue_EEG"].append(
            np.concatenate([_log_variance(band[start + 500 : start + 750]) for band in eeg_filtered])
        )
        for name, channels in VIEW_CHANNELS.items():
            indices = [EEG_CHANNELS.index(channel) for channel in channels]
            rows[name].append(
                np.concatenate([_log_variance(band[late_start:late_stop, indices]) for band in eeg_filtered])
            )
    output = {name: np.asarray(items, dtype="float32") for name, items in rows.items()}
    for name, dimension in FEATURE_DIMENSIONS.items():
        if name.startswith(("D_", "rotated_")):
            continue
        if output[name].shape != (48, dimension):
            raise BNCIStageQRefusal(f"target-free feature dimension differs: {name}")
        if not np.isfinite(output[name]).all():
            raise BNCIStageQRefusal(f"target-free feature contains invalid values: {name}")
    for family in ("E1", "E2"):
        values_family = output[family]
        displaced = np.zeros_like(values_family)
        displaced[1:] = values_family[:-1]
        output[f"D_{family}"] = displaced
        output[f"rotated_{family}"] = np.asarray(
            [rotate_feature_channels(row, family) for row in values_family], dtype="float32"
        )
    return output


def _npy_bytes(array: Any) -> bytes:
    np = _np()
    stream = io.BytesIO()
    np.lib.format.write_array(stream, np.asarray(array), allow_pickle=False)
    return stream.getvalue()


def deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(arrays):
            if not name or any(character not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_" for character in name):
                raise BNCIStageQRefusal("NPZ array name is invalid")
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, _npy_bytes(arrays[name]))
    return stream.getvalue()


def _exclusive_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise BNCIStageQRefusal("Stage Q output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _regular_nofollow(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise BNCIStageQRefusal("Stage Q input is not a direct regular file")
    if info.st_nlink != 1:
        raise BNCIStageQRefusal("Stage Q input has an unexpected hard-link count")
    return info


def _assert_direct_ancestry(root: Path, path: Path) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise BNCIStageQRefusal("Stage Q path escaped the repository") from exc
    current = root
    for part in relative.parts[:-1]:
        current = current / part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise BNCIStageQRefusal("Stage Q input ancestry is not direct")


def _read_exact_member(
    path: Path, member: PayloadMember, *, ancestry_root: Path | None = None
) -> bytes:
    if ancestry_root is not None:
        _assert_direct_ancestry(ancestry_root, path)
    if _regular_nofollow(path).st_size != member.bytes:
        raise BNCIStageQRefusal("Stage Q MAT member size differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        chunks: list[bytes] = []
        total = 0
        while total < member.bytes:
            chunk = os.read(descriptor, min(1_048_576, member.bytes - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if os.read(descriptor, 1):
            raise BNCIStageQRefusal("Stage Q MAT member grew during read")
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        raise BNCIStageQRefusal("Stage Q MAT member changed during read")
    payload = b"".join(chunks)
    if len(payload) != member.bytes or _sha256(payload) != member.sha256:
        raise BNCIStageQRefusal("Stage Q MAT member digest differs")
    return payload


def _read_capped_regular(path: Path, maximum_bytes: int) -> bytes:
    _assert_direct_ancestry(_repo_root(), path)
    info = _regular_nofollow(path)
    if info.st_size <= 0 or info.st_size > maximum_bytes:
        raise BNCIStageQRefusal("Stage Q bounded input size differs")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        payload = os.read(descriptor, maximum_bytes + 1)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if len(payload) != info.st_size or (info.st_dev, info.st_ino, info.st_mtime_ns) != (
        after.st_dev,
        after.st_ino,
        after.st_mtime_ns,
    ):
        raise BNCIStageQRefusal("Stage Q bounded input changed during read")
    return payload


def _git_output(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, timeout=30
    )
    return completed.stdout


def read_green_activation(root: str | Path) -> dict[str, Any]:
    repo = Path(root).resolve()
    path = repo / ACTIVATION_RELATIVE_PATH
    payload = path.read_bytes()
    try:
        activation = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BNCIStageQRefusal("Stage Q activation JSON is invalid") from exc
    if activation.get("lane_id") != LANE_ID or activation.get("status") != "remotely_green_live_execution_enabled":
        raise BNCIStageQRefusal("Stage Q activation is not effective")
    stage_a = activation.get("green_stage_a_result", {})
    if stage_a != {
        "commit": STAGE_A_RESULT_COMMIT,
        "CI_run_id": STAGE_A_RESULT_CI_RUN_ID,
        "base_python_job_id": STAGE_A_RESULT_BASE_JOB_ID,
        "optional_neuro_readers_job_id": STAGE_A_RESULT_OPTIONAL_JOB_ID,
        "both_required_jobs_green": True,
    }:
        raise BNCIStageQRefusal("Stage Q Stage A proof binding changed")
    green = activation.get("green_implementation", {})
    if green.get("both_required_jobs_green") is not True or not isinstance(green.get("commit"), str):
        raise BNCIStageQRefusal("Stage Q implementation green proof is unavailable")
    artifacts = activation.get("implementation_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise BNCIStageQRefusal("Stage Q implementation artifact binding is absent")
    for row in artifacts:
        relative = Path(str(row["path"]))
        current = (repo / relative).read_bytes()
        if len(current) != int(row["bytes"]) or _sha256(current) != row["sha256"]:
            raise BNCIStageQRefusal("Stage Q implementation artifact changed")
        if _git_output(repo, "show", f"{green['commit']}:{relative.as_posix()}") != current:
            raise BNCIStageQRefusal("Stage Q implementation differs from its green commit")
    if _git_output(repo, "show", f"HEAD:{ACTIVATION_RELATIVE_PATH.as_posix()}") != payload:
        raise BNCIStageQRefusal("Stage Q activation differs from HEAD")
    _git_output(repo, "merge-base", "--is-ancestor", STAGE_A_RESULT_COMMIT, "HEAD")
    _git_output(repo, "merge-base", "--is-ancestor", green["commit"], "HEAD")
    subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=repo, check=True, timeout=30)
    subprocess.run(["git", "diff", "--cached", "--quiet", "--"], cwd=repo, check=True, timeout=30)
    return activation


def registered_plan(root: str | Path) -> dict[str, Any]:
    members = registered_members(root)
    return {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_q_plan",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "public_plan_only_no_ignored_path_or_MAT_operation",
        "MAT_files": len(members),
        "payload_bytes": sum(member.bytes for member in members),
        "expected_task_runs": 108,
        "expected_trials": ROWS_TOTAL,
        "network_bytes": 0,
        "model_runs": 0,
        "training_runs": 0,
        "prediction_sets": 0,
        "target_deliveries": 0,
        "scores": 0,
        "next_operation": "commit_push_green_exact_implementation_then_green_activation_before_execute",
    }


def _generated_task_run(seed: int, *, targets_shift: int = 0) -> dict[str, Any]:
    np = _np()
    rng = np.random.default_rng(seed)
    starts = 1 + np.arange(48, dtype="int64") * 1500
    sample_count = int(starts[-1] - 1 + 1500)
    signal = rng.normal(0.0, 0.05, size=(sample_count, 25)).astype("float32")
    targets = np.roll(np.tile(np.arange(1, 5, dtype="int64"), 12), targets_shift)
    for one_based_start, target in zip(starts, targets, strict=True):
        start = int(one_based_start - 1)
        phase = 2.0 * math.pi * (8.0 + 2.0 * target) * np.arange(625) / 250.0
        signal[start + 875 : start + 1500, int(target) - 1] += np.sin(phase).astype("float32")
    return {
        "X": signal,
        "trial": starts,
        "y": targets,
        "fs": 250.0,
        "classes": list(UPSTREAM_CLASSES),
        "artifacts": np.zeros(48, dtype="uint8"),
    }


def write_generated_mat(path: Path, *, targets_shift: int = 0) -> PayloadMember:
    np = _np()
    _loadmat, savemat = _scipy_io()
    empty = {
        "X": np.empty((0, 25), dtype="float32"),
        "trial": np.empty(0, dtype="int64"),
        "y": np.empty(0, dtype="int64"),
        "fs": 250.0,
        "classes": list(UPSTREAM_CLASSES),
        "artifacts": np.empty(0, dtype="uint8"),
    }
    runs = [empty, empty, empty] + [
        _generated_task_run(100 + index, targets_shift=targets_shift) for index in range(6)
    ]
    savemat(path, {"data": np.asarray(runs, dtype=object)}, do_compression=True)
    payload = path.read_bytes()
    return PayloadMember(path.name, len(payload), _sha256(payload))


def run_generated_qualification(output_path: str | Path, *, environ: Mapping[str, str]) -> dict[str, Any]:
    registered_output = _repo_root() / "registries/bnci_2014_001_stage_q_generated_result.v0.json"
    if Path(output_path).resolve() != registered_output:
        raise BNCIStageQRefusal("generated Stage Q qualification has one fixed output")
    if registered_output.exists() or registered_output.is_symlink():
        raise BNCIStageQRefusal("generated Stage Q qualification is consumed")
    assert_single_thread_environment(environ)
    versions = assert_exact_versions()
    output = Path(output_path)
    if output.exists() or output.is_symlink():
        raise BNCIStageQRefusal("generated Stage Q output already exists")
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="neurodecodekit-bnci-stage-q-") as temporary:
        root = Path(temporary)
        path = root / "generated.mat"
        member = write_generated_mat(path)
        payload = _read_exact_member(path, member, ancestry_root=root)
        runs, calibration_structs = parse_verified_mat_payload(payload, member)
        first = extract_target_free_run_features(runs[0].signal, runs[0].starts)
        second = extract_target_free_run_features(runs[0].signal, runs[0].starts)
        first_payload = deterministic_npz_bytes(first)
        second_payload = deterministic_npz_bytes(second)
        if first_payload != second_payload:
            raise BNCIStageQRefusal("generated target-free deterministic replay changed")
        original_targets = runs[0].targets.copy()
        runs[0].targets[:] = _np().roll(runs[0].targets, 1)
        altered = extract_target_free_run_features(runs[0].signal, runs[0].starts)
        if deterministic_npz_bytes(altered) != first_payload:
            raise BNCIStageQRefusal("generated target mutation changed predictive features")
        runs[0].targets[:] = original_targets
        malformed = bytearray(payload)
        malformed[-1] ^= 1
        refusals = 0
        try:
            parse_verified_mat_payload(bytes(malformed), member)
        except BNCIStageQRefusal:
            refusals += 1
        if refusals != 1:
            raise BNCIStageQRefusal("generated malformed identity refusal changed")
        input_bytes = len(payload)
    runtime = time.perf_counter() - started
    peak_rss = peak_process_rss_bytes()
    result = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_q_generated_result",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "passed_generated_only_no_private_or_real_operation",
        "case_classes": [
            "nine_structs_with_three_target_ineligible_calibration_structs",
            "six_task_runs_48_trials_25_channels_250_Hz_and_complete_windows",
            "causal_run_boundary_feature_dimensions_and_exact_replay",
            "target_mutation_does_not_change_predictive_feature_bytes",
            "deterministic_target_free_NPZ_serialization",
            "payload_identity_refusal",
        ],
        "measurements": {
            "generated_input_bytes": input_bytes,
            "generated_task_runs": len(runs),
            "generated_trials": sum(len(run.starts) for run in runs),
            "generated_calibration_structs": calibration_structs,
            "target_free_feature_bytes": len(first_payload),
            "runtime_seconds": runtime,
            "peak_process_RSS_bytes": peak_rss,
        },
        "feature_dimensions": FEATURE_DIMENSIONS,
        "versions": versions,
        "operations": {
            "generated_MAT_content_opens": 1,
            "generated_MAT_semantic_parses": 1,
            "real_or_private_path_opens": 0,
            "real_MAT_semantic_opens": 0,
            "network_bytes": 0,
            "model_runs": 0,
            "training_runs": 0,
            "prediction_sets": 0,
            "target_deliveries": 0,
            "scores": 0,
        },
        "resources": {
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
            "runtime_seconds_maximum": RUNTIME_CAP_SECONDS,
            "peak_RSS_bytes_maximum": PEAK_RSS_CAP_BYTES,
            "public_output_bytes_maximum": PUBLIC_OUTPUT_CAP_BYTES,
        },
        "qualification_may_be_repeated": False,
        "scientific_claim_established": False,
    }
    payload_out = _canonical_bytes(result)
    if len(payload_out) > PUBLIC_OUTPUT_CAP_BYTES:
        raise BNCIStageQRefusal("generated Stage Q result exceeds public cap")
    _exclusive_write(output, payload_out)
    return result


def _private_manifest(root: Path, members: Sequence[PayloadMember]) -> dict[str, Any]:
    path = root / STAGE_A_BUNDLE_RELATIVE_PATH / "manifest.private.v0.json"
    payload = _read_capped_regular(path, PUBLIC_OUTPUT_CAP_BYTES)
    try:
        manifest = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise BNCIStageQRefusal("Stage A private manifest is invalid") from exc
    rows = manifest.get("members")
    expected = [
        {"relative_path": member.relative_path, "bytes": member.bytes, "sha256": member.sha256}
        for member in members
    ]
    observed = [
        {"relative_path": str(row.get("relative_path")), "bytes": int(row.get("bytes", -1)), "sha256": str(row.get("sha256"))}
        for row in rows
    ] if isinstance(rows, list) else []
    if observed != expected:
        raise BNCIStageQRefusal("Stage A private manifest member table differs")
    if manifest.get("file_count") != MAT_FILE_COUNT or manifest.get("payload_bytes") != 779_873_919:
        raise BNCIStageQRefusal("Stage A private manifest aggregate differs")
    return manifest


def _row_id(participant: str, session: str, run: int, trial: int) -> str:
    return _sha256(
        _canonical_bytes(
            {"participant": participant, "session": session, "run_ordinal": run, "trial_ordinal": trial}
        )
    )


def _write_private_derivatives(
    output: Path,
    feature_rows: Mapping[str, list[Any]],
    identity: Mapping[str, list[Any]],
    targets: Any,
    artifacts: Any,
) -> tuple[dict[str, Any], int]:
    np = _np()
    arrays: dict[str, Any] = {
        name: np.asarray(rows, dtype="float32") for name, rows in feature_rows.items()
    }
    arrays.update(
        {
            "participant_index": np.asarray(identity["participant_index"], dtype="uint8"),
            "session_index": np.asarray(identity["session_index"], dtype="uint8"),
            "run_ordinal": np.asarray(identity["run_ordinal"], dtype="uint8"),
            "trial_ordinal": np.asarray(identity["trial_ordinal"], dtype="uint8"),
            "trial_start_sample": np.asarray(identity["trial_start_sample"], dtype="int32"),
            "opaque_row_id": np.asarray(identity["opaque_row_id"], dtype="S64"),
        }
    )
    for name, dimension in FEATURE_DIMENSIONS.items():
        if arrays[name].shape != (ROWS_TOTAL, dimension):
            raise BNCIStageQRefusal(f"Stage Q cohort feature shape differs: {name}")
    feature_payload = deterministic_npz_bytes(arrays)
    feature_path = output / "target_free_features.private.v0.npz"
    _exclusive_write(feature_path, feature_payload)
    artifacts_payload = deterministic_npz_bytes(
        {
            "row_index": np.arange(ROWS_TOTAL, dtype="int32"),
            "artifact_flag": np.asarray(artifacts, dtype="uint8"),
        }
    )
    artifacts_path = output / "sealed_artifacts.private.v0.npz"
    _exclusive_write(artifacts_path, artifacts_payload)
    target_values = np.asarray(targets, dtype="uint8")
    participant_values = arrays["participant_index"]
    session_values = arrays["session_index"]
    artifact_rows: list[dict[str, Any]] = [
        {"role": "target_free_features", "file": feature_path.name, "bytes": len(feature_payload), "sha256": _sha256(feature_payload)},
        {"role": "sealed_artifacts", "file": artifacts_path.name, "bytes": len(artifacts_payload), "sha256": _sha256(artifacts_payload)},
    ]
    total = len(feature_payload) + len(artifacts_payload)
    source_dir = output / "source_targets"
    sealed_dir = output / "sealed_held_out_E_targets"
    source_dir.mkdir()
    sealed_dir.mkdir()
    for held_out_index, participant in enumerate(PARTICIPANTS):
        source_mask = participant_values != held_out_index
        held_out_e_mask = (participant_values == held_out_index) & (session_values == 1)
        if int(source_mask.sum()) != SOURCE_ROWS_PER_FOLD or int(held_out_e_mask.sum()) != HELD_OUT_E_ROWS_PER_FOLD:
            raise BNCIStageQRefusal("Stage Q fold target capability count differs")
        source_payload = deterministic_npz_bytes(
            {
                "row_index": np.flatnonzero(source_mask).astype("int32"),
                "target_index": target_values[source_mask],
            }
        )
        sealed_payload = deterministic_npz_bytes(
            {
                "row_index": np.flatnonzero(held_out_e_mask).astype("int32"),
                "target_index": target_values[held_out_e_mask],
            }
        )
        source_path = source_dir / f"fold_{participant}.private.v0.npz"
        sealed_path = sealed_dir / f"fold_{participant}.sealed.v0.npz"
        _exclusive_write(source_path, source_payload)
        _exclusive_write(sealed_path, sealed_payload)
        total += len(source_payload) + len(sealed_payload)
        artifact_rows.extend(
            [
                {"role": "fold_scoped_source_targets", "fold": participant, "file": str(source_path.relative_to(output)), "bytes": len(source_payload), "sha256": _sha256(source_payload)},
                {"role": "sealed_held_out_E_targets", "fold": participant, "file": str(sealed_path.relative_to(output)), "bytes": len(sealed_payload), "sha256": _sha256(sealed_payload)},
            ]
        )
    manifest = {
        "schema_name": "neurodecodekit.bnci_2014_001_stage_q_private_derivative_manifest",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "status": "complete_target_firewalled_capabilities",
        "rows": ROWS_TOTAL,
        "task_runs": 108,
        "channels": list(ALL_CHANNELS),
        "sampling_rate_hz": SAMPLING_RATE_HZ,
        "features": FEATURE_DIMENSIONS,
        "folds": 9,
        "source_rows_per_fold": SOURCE_ROWS_PER_FOLD,
        "held_out_E_rows_per_fold": HELD_OUT_E_ROWS_PER_FOLD,
        "held_out_T_rows_exposed_per_fold": 0,
        "predictive_archive_contains_target_or_artifact_arrays": False,
        "first_trial_previous_interval_seconds_sentinel": 0.0,
        "geometry_available_from_payload": False,
        "artifacts": artifact_rows,
    }
    manifest_payload = _canonical_bytes(manifest)
    manifest_path = output / "manifest.private.v0.json"
    _exclusive_write(manifest_path, manifest_payload)
    total += len(manifest_payload)
    if total > PRIVATE_OUTPUT_CAP_BYTES:
        raise BNCIStageQRefusal("Stage Q private derivatives exceed cap")
    return manifest, total


def execute_registered_stage_q(root: str | Path, *, environ: Mapping[str, str]) -> dict[str, Any]:
    raise BNCIStageQRefusal(
        "generated-qualified core has no live entry point; use the additive live control plane"
    )
    repo = Path(root).resolve()
    if repo != _repo_root():
        raise BNCIStageQRefusal("Stage Q repository root differs")
    assert_single_thread_environment(environ)
    versions = assert_exact_versions()
    load_public_bindings(repo)
    activation = read_green_activation(repo)
    members = registered_members(repo)
    output = repo / STAGE_Q_OUTPUT_RELATIVE_PATH
    marker = repo / STAGE_Q_MARKER_RELATIVE_PATH
    receipt_path = repo / STAGE_Q_RECEIPT_RELATIVE_PATH
    if any(path.exists() or path.is_symlink() for path in (output, marker, receipt_path)):
        raise BNCIStageQRefusal("Stage Q is already consumed or has output")
    marker_payload = _canonical_bytes(
        {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_consumed_marker",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "consumed_before_private_manifest_or_MAT_open",
            "implementation_commit": activation["green_implementation"]["commit"],
            "rerun_allowed": False,
        }
    )
    _exclusive_write(marker, marker_payload)
    ledger = OperationLedger()
    started = time.perf_counter()
    free_before = shutil.disk_usage(repo).free
    temporary = output.with_name(output.name + f".tmp-{os.getpid()}")
    temporary.mkdir(parents=False)
    try:
        _private_manifest(repo, members)
        ledger.private_manifest_opens += 1
        feature_rows: dict[str, list[Any]] = {name: [] for name in FEATURE_DIMENSIONS}
        identity: dict[str, list[Any]] = {
            "participant_index": [],
            "session_index": [],
            "run_ordinal": [],
            "trial_ordinal": [],
            "trial_start_sample": [],
            "opaque_row_id": [],
        }
        targets: list[int] = []
        artifacts: list[int] = []
        calibration_structs = 0
        missing_artifact_runs = 0
        for member in members:
            participant = Path(member.relative_path).stem[:3]
            session = Path(member.relative_path).stem[3:]
            if participant not in PARTICIPANTS or session not in SESSIONS:
                raise BNCIStageQRefusal("Stage Q member participant or session differs")
            member_path = repo / STAGE_A_BUNDLE_RELATIVE_PATH / member.relative_path
            payload = _read_exact_member(member_path, member, ancestry_root=repo)
            ledger.MAT_content_opens += 1
            runs, calibration_count = parse_verified_mat_payload(payload, member)
            ledger.MAT_semantic_parses += 1
            del payload
            calibration_structs += calibration_count
            for run_ordinal, run in enumerate(runs):
                run_features = extract_target_free_run_features(run.signal, run.starts)
                ledger.task_signal_runs_read += 1
                ledger.target_vectors_isolated += 1
                if not run.artifacts_available:
                    missing_artifact_runs += 1
                for name in FEATURE_DIMENSIONS:
                    values = run_features[name]
                    if name == "timing_only":
                        values = values.copy()
                        values[:, 0] = float(SESSIONS.index(session))
                        values[:, 1] = float(run_ordinal)
                    feature_rows[name].extend(values)
                for trial_ordinal, start in enumerate(run.starts):
                    identity["participant_index"].append(PARTICIPANTS.index(participant))
                    identity["session_index"].append(SESSIONS.index(session))
                    identity["run_ordinal"].append(run_ordinal)
                    identity["trial_ordinal"].append(trial_ordinal)
                    identity["trial_start_sample"].append(int(start))
                    identity["opaque_row_id"].append(
                        _row_id(participant, session, run_ordinal, trial_ordinal).encode()
                    )
                targets.extend(int(value) - 1 for value in run.targets)
                artifacts.extend(int(value) for value in run.artifacts)
            if time.perf_counter() - started > RUNTIME_CAP_SECONDS:
                raise BNCIStageQRefusal("Stage Q runtime cap exceeded")
            if peak_process_rss_bytes() > PEAK_RSS_CAP_BYTES:
                raise BNCIStageQRefusal("Stage Q peak RSS cap exceeded")
        if ledger.MAT_content_opens != MAT_FILE_COUNT or ledger.MAT_semantic_parses != MAT_FILE_COUNT:
            raise BNCIStageQRefusal("Stage Q exact MAT open count differs")
        if ledger.task_signal_runs_read != 108 or len(targets) != ROWS_TOTAL:
            raise BNCIStageQRefusal("Stage Q aggregate task inventory differs")
        derivative_manifest, derivative_bytes = _write_private_derivatives(
            temporary, feature_rows, identity, targets, artifacts
        )
        temporary.rename(output)
        runtime = time.perf_counter() - started
        peak_rss = peak_process_rss_bytes()
        free_after = shutil.disk_usage(repo).free
        receipt = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_q_private_receipt",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "passed_consumed_target_firewalled_semantic_qualification",
            "measurements": {
                "input_payload_bytes": sum(member.bytes for member in members),
                "private_derivative_bytes": derivative_bytes,
                "runtime_seconds": runtime,
                "peak_process_RSS_bytes": peak_rss,
                "free_disk_bytes_before": free_before,
                "free_disk_bytes_after": free_after,
                "receipt_bytes": 0,
            },
            "inventory": {
                "MAT_files": MAT_FILE_COUNT,
                "task_runs": ledger.task_signal_runs_read,
                "trials": ROWS_TOTAL,
                "calibration_structs_recognized": calibration_structs,
                "artifact_flag_unavailable_runs": missing_artifact_runs,
                "channels": len(ALL_CHANNELS),
                "EEG_channels": len(EEG_CHANNELS),
                "EOG_channels": len(EOG_CHANNELS),
                "sampling_rate_hz": SAMPLING_RATE_HZ,
                "geometry_available_from_payload": False,
                "folds": derivative_manifest["folds"],
                "source_rows_per_fold": SOURCE_ROWS_PER_FOLD,
                "sealed_held_out_E_rows_per_fold": HELD_OUT_E_ROWS_PER_FOLD,
            },
            "operations": ledger.__dict__,
            "versions": versions,
            "resources": {
                "CPU_threads": 1,
                "workers": 1,
                "numerical_jobs": 1,
                "network_bytes": 0,
                "runtime_seconds_maximum": RUNTIME_CAP_SECONDS,
                "peak_RSS_bytes_maximum": PEAK_RSS_CAP_BYTES,
                "private_derivative_bytes_maximum": PRIVATE_OUTPUT_CAP_BYTES,
            },
            "warnings": [
                "payload_geometry_is_unavailable",
                "first_trial_previous_interval_uses_exact_zero_sentinel",
                "artifact_flags_are_sealed_and_never_used_for_primary_exclusion",
                "semantic_qualification_is_not_model_training_prediction_scoring_or_a_scientific_result",
            ],
            "rerun_allowed": False,
        }
        for _ in range(8):
            receipt_payload = _canonical_bytes(receipt)
            if receipt["measurements"]["receipt_bytes"] == len(receipt_payload):
                break
            receipt["measurements"]["receipt_bytes"] = len(receipt_payload)
        else:
            raise BNCIStageQRefusal("Stage Q receipt byte count did not stabilize")
        if len(receipt_payload) > PUBLIC_OUTPUT_CAP_BYTES:
            raise BNCIStageQRefusal("Stage Q private receipt exceeds cap")
        _exclusive_write(receipt_path, receipt_payload)
        return receipt
    except Exception:
        if temporary.exists() and temporary.is_dir() and not temporary.is_symlink():
            shutil.rmtree(temporary)
        raise
