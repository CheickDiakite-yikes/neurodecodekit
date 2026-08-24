"""Generated qualification and frozen computation for BNCI-C3C5-1."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
import resource
import shutil
import stat
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


LANE_ID = "BNCI-C3C5-1"
SCHEMA_VERSION = "0.1.0"
CONTRACT_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_contract.v0.json"
)
DECISION_RELATIVE_PATH = Path(
    "registries/bnci_2014_001_cross_participant_eeg_gain_authorization_decision.v0.json"
)
CONTRACT_SHA256 = "e11dad351f5a4736dc6ac3ffdad28a65e37b18b40c5bfa9e861f5b0754ad2b74"
DECISION_SHA256 = "687ed0d5afa64ba7c34ab86bf3e0c4f79d08d21041dd1e9e6aa3642629d0f559"
PARTICIPANTS = tuple(f"A{index:02d}" for index in range(1, 10))
SESSIONS = ("T", "E")
CLASSES = ("left_hand", "right_hand", "feet", "tongue")
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
}
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class BNCIRefusal(RuntimeError):
    """Fail-closed BNCI experiment refusal."""


@dataclass(frozen=True)
class FrozenLogistic:
    source_reference: Any
    mean: Any
    scale: Any
    classes: tuple[str, ...]
    coefficient: Any
    intercept: Any


@dataclass
class OperationLedger:
    parameter_update_fits: int = 0
    prediction_sets: int = 0
    model_inference_runs: int = 0


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _load_bound_json(path: Path, expected_sha256: str) -> dict[str, Any]:
    payload = (_repo_root() / path).read_bytes()
    if _sha256(payload) != expected_sha256:
        raise BNCIRefusal(f"bound artifact hash changed: {path}")
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise BNCIRefusal(f"bound artifact is not an object: {path}")
    return parsed


def load_contract() -> dict[str, Any]:
    contract = _load_bound_json(CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if contract.get("contract_id") != LANE_ID:
        raise BNCIRefusal("BNCI contract identity changed")
    return contract


def load_decision() -> dict[str, Any]:
    decision = _load_bound_json(DECISION_RELATIVE_PATH, DECISION_SHA256)
    if decision.get("lane_id") != LANE_ID:
        raise BNCIRefusal("BNCI decision identity changed")
    return decision


def _np():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("BNCI arrays require: pip install -e '.[classical]'") from exc
    return np


def _scipy_io():
    try:
        from scipy.io import loadmat, savemat
    except ImportError as exc:
        raise RuntimeError("BNCI MAT qualification requires: pip install -e '.[classical]'") from exc
    return loadmat, savemat


def _signal_functions():
    try:
        from scipy.signal import butter, sosfilt
    except ImportError as exc:
        raise RuntimeError("BNCI causal filters require: pip install -e '.[classical]'") from exc
    return butter, sosfilt


def _logistic_class():
    try:
        from sklearn.linear_model import LogisticRegression
    except ImportError as exc:
        raise RuntimeError("BNCI models require: pip install -e '.[classical]'") from exc
    return LogisticRegression


def assert_exact_versions() -> dict[str, str]:
    expected = {"numpy": "2.5.2", "scipy": "1.18.0", "scikit-learn": "1.9.0"}
    observed = {name: importlib.metadata.version(name) for name in expected}
    if observed != expected:
        raise BNCIRefusal(f"optional numerical version set changed: {observed}")
    return observed


def assert_single_thread_environment() -> None:
    changed = {
        name: os.environ.get(name) for name in THREAD_ENVIRONMENT if os.environ.get(name) != "1"
    }
    if changed:
        raise BNCIRefusal(f"one-thread environment is not frozen: {sorted(changed)}")


def peak_process_tree_rss_bytes() -> int:
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    factor = 1 if os.uname().sysname == "Darwin" else 1024
    return int((own + children) * factor)


def _regular_no_follow(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise BNCIRefusal("path is not a single-link regular file")
    return info


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise BNCIRefusal("output destination already exists")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise BNCIRefusal("output temporary path already exists")
    try:
        with temporary.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise BNCIRefusal("output destination appeared during publication")
        os.rename(temporary, path)
    finally:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def _prepare_output_path(path: str | Path) -> Path:
    candidate = Path(path).expanduser().absolute()
    lowered = {part.lower() for part in candidate.parts}
    if ".." in Path(path).parts:
        raise BNCIRefusal("output traversal is forbidden")
    if lowered.intersection({"data", ".codex_work"}):
        raise BNCIRefusal("generated output cannot use a protected data root")
    if candidate.exists() or candidate.is_symlink():
        raise BNCIRefusal("generated qualification output already exists")
    return candidate


def _causal_band(signal: Any, low: float, high: float, sampling_rate: float) -> Any:
    np = _np()
    butter, sosfilt = _signal_functions()
    values = np.asarray(signal, dtype="float64")
    if values.ndim != 2 or not np.isfinite(values).all():
        raise BNCIRefusal("causal filter input is malformed")
    sos = butter(4, (low, high), btype="bandpass", fs=sampling_rate, output="sos")
    return sosfilt(sos, values, axis=0)


def _common_average(signal: Any) -> Any:
    np = _np()
    values = np.asarray(signal, dtype="float64")
    if values.ndim != 2 or values.shape[1] != 22:
        raise BNCIRefusal("EEG common-average input differs")
    return values - values.mean(axis=1, keepdims=True)


def _log_variance(signal: Any) -> Any:
    np = _np()
    return np.log(np.maximum(np.var(signal, axis=0, ddof=0), 1e-12))


def extract_e1(signal_microvolts: Any, start: int, stop: int) -> Any:
    np = _np()
    referenced = _common_average(np.asarray(signal_microvolts)[:, :22])
    features = [
        _log_variance(_causal_band(referenced, low, high, 250.0)[start:stop])
        for low, high in EEG_BANDS
    ]
    output = np.concatenate(features)
    if output.shape != (88,):
        raise BNCIRefusal("E1 feature dimension differs")
    return output


def extract_e1_view(
    signal_microvolts: Any,
    start: int,
    stop: int,
    channel_names: Sequence[str],
) -> Any:
    np = _np()
    if not channel_names or any(name not in EEG_CHANNELS for name in channel_names):
        raise BNCIRefusal("EEG view channel inventory differs")
    if len(set(channel_names)) != len(channel_names):
        raise BNCIRefusal("EEG view channel is duplicated")
    indices = [EEG_CHANNELS.index(name) for name in channel_names]
    referenced = _common_average(np.asarray(signal_microvolts)[:, :22])
    features = [
        _log_variance(
            _causal_band(referenced, low, high, 250.0)[start:stop, indices]
        )
        for low, high in EEG_BANDS
    ]
    output = np.concatenate(features)
    if output.shape != (4 * len(channel_names),):
        raise BNCIRefusal("EEG view feature dimension differs")
    return output


def _matrix_log_spd(matrix: Any) -> Any:
    np = _np()
    eigenvalues, eigenvectors = np.linalg.eigh(matrix)
    if np.any(eigenvalues <= 0.0):
        raise BNCIRefusal("covariance is not positive definite")
    return (eigenvectors * np.log(eigenvalues)) @ eigenvectors.T


def extract_e2(signal_microvolts: Any, start: int, stop: int) -> Any:
    np = _np()
    referenced = _common_average(np.asarray(signal_microvolts)[:, :22])
    triangle = np.triu_indices(22)
    features = []
    for low, high in EEG_BANDS:
        window = _causal_band(referenced, low, high, 250.0)[start:stop]
        covariance = (window.T @ window) / float(window.shape[0])
        trace = float(np.trace(covariance))
        if not math.isfinite(trace) or trace <= 0.0:
            raise BNCIRefusal("E2 covariance trace is invalid")
        covariance = covariance / trace + np.eye(22) * 1e-5
        features.append(_matrix_log_spd(covariance)[triangle])
    output = np.concatenate(features)
    if output.shape != (1012,):
        raise BNCIRefusal("E2 feature dimension differs")
    return output


def extract_eog(signal_microvolts: Any, start: int, stop: int) -> Any:
    np = _np()
    eog = np.asarray(signal_microvolts, dtype="float64")[:, 22:25]
    features = []
    for low, high in EOG_BANDS:
        window = _causal_band(eog, low, high, 250.0)[start:stop]
        bins = np.array_split(window, 8, axis=0)
        for channel in range(3):
            for item in bins:
                values = item[:, channel]
                x = np.arange(values.size, dtype="float64")
                centered = x - x.mean()
                slope = float(centered @ (values - values.mean()) / (centered @ centered))
                features.extend((float(values.mean()), slope))
            features.append(float(_log_variance(window[:, [channel]])[0]))
    output = np.asarray(features, dtype="float64")
    if output.shape != (102,):
        raise BNCIRefusal("P feature dimension differs")
    return output


def _generated_run(seed: int) -> dict[str, Any]:
    np = _np()
    rng = np.random.default_rng(seed)
    starts = 1 + np.arange(48, dtype="int64") * 1500
    sample_count = int(starts[-1] - 1 + 1500)
    signal = rng.normal(0.0, 0.05, size=(sample_count, 25)).astype("float32")
    targets = np.tile(np.arange(1, 5, dtype="int64"), 12)
    for trial_index, (one_based_start, target) in enumerate(zip(starts, targets, strict=True)):
        start = int(one_based_start - 1)
        phase = 2.0 * math.pi * (8.0 + 2.0 * target) * np.arange(625) / 250.0
        signal[start + 875 : start + 1500, target - 1] += np.sin(phase).astype("float32")
        signal[start + 500 : start + 1500, 22 + ((target - 1) % 3)] += (
            0.25 * np.sin(2.0 * math.pi * target * np.arange(1000) / 250.0)
        ).astype("float32")
        signal[start : start + 20, 21] += trial_index * 1e-4
    return {
        "X": signal,
        "trial": starts,
        "y": targets,
        "fs": 250.0,
        "classes": list(CLASSES),
        "artifacts": np.zeros(48, dtype="uint8"),
    }


def write_generated_mat(path: Path) -> int:
    np = _np()
    _loadmat, savemat = _scipy_io()
    runs = np.asarray([_generated_run(100 + index) for index in range(6)], dtype=object)
    savemat(path, {"data": runs}, do_compression=False)
    return _regular_no_follow(path).st_size


def load_and_validate_mat(path: Path) -> list[dict[str, Any]]:
    np = _np()
    loadmat, _savemat = _scipy_io()
    _regular_no_follow(path)
    parsed = loadmat(path, simplify_cells=True)
    if set(parsed).intersection({"data"}) != {"data"}:
        raise BNCIRefusal("MAT top-level data key is unavailable")
    raw = parsed["data"]
    if isinstance(raw, Mapping):
        runs = [dict(raw)]
    elif isinstance(raw, np.ndarray):
        runs = [dict(item) for item in raw.reshape(-1).tolist()]
    elif isinstance(raw, list):
        runs = [dict(item) for item in raw]
    else:
        raise BNCIRefusal("MAT data structure is malformed")
    if len(runs) != 6:
        raise BNCIRefusal("MAT task run count differs")
    required = {"X", "trial", "y", "fs", "classes", "artifacts"}
    validated: list[dict[str, Any]] = []
    for run in runs:
        if not required.issubset(run):
            raise BNCIRefusal("MAT run field inventory differs")
        signal = np.asarray(run["X"])
        starts = np.asarray(run["trial"]).reshape(-1)
        targets = np.asarray(run["y"]).reshape(-1)
        artifacts = np.asarray(run["artifacts"]).reshape(-1)
        classes = tuple(
            str(value).strip() for value in np.asarray(run["classes"]).reshape(-1)
        )
        if signal.ndim != 2 or signal.shape[1] != 25 or not np.isfinite(signal).all():
            raise BNCIRefusal("MAT signal shape or value differs")
        if starts.shape != (48,) or targets.shape != (48,) or artifacts.shape != (48,):
            raise BNCIRefusal("MAT trial, target, or artifact length differs")
        if float(run["fs"]) != 250.0 or classes != CLASSES:
            raise BNCIRefusal("MAT sampling or class order differs")
        if not np.issubdtype(starts.dtype, np.integer) or int(starts.min()) < 1:
            raise BNCIRefusal("MAT trial indices are not one-based integers")
        zero_based = starts.astype("int64") - 1
        if np.any(np.diff(zero_based) < 1500) or int(zero_based[-1] + 1500) > signal.shape[0]:
            raise BNCIRefusal("MAT trial windows overlap or are incomplete")
        if set(int(value) for value in targets) != {1, 2, 3, 4}:
            raise BNCIRefusal("MAT target inventory differs")
        validated.append(
            {
                "X": signal,
                "trial_zero_based": zero_based,
                "targets": targets.astype("int64"),
                "artifacts": artifacts,
            }
        )
    return validated


def run_generated_mat_cases(root: Path) -> dict[str, Any]:
    np = _np()
    root.mkdir(parents=True, exist_ok=False)
    path = root / "generated.mat"
    input_bytes = write_generated_mat(path)
    runs = load_and_validate_mat(path)
    first = runs[0]
    start = int(first["trial_zero_based"][0])
    signal = first["X"]
    e1 = extract_e1(signal, start + 875, start + 1500)
    e2 = extract_e2(signal, start + 875, start + 1500)
    p = extract_eog(signal, start + 500, start + 1500)
    if (e1.shape, e2.shape, p.shape) != ((88,), (1012,), (102,)):
        raise BNCIRefusal("generated feature dimensions changed")
    temporal_and_spatial = {
        "pre_cue_EEG": extract_e1(signal, start, start + 500),
        "early_cue_EEG": extract_e1(signal, start + 500, start + 750),
        **{
            field: extract_e1_view(signal, start + 875, start + 1500, channels)
            for field, channels in VIEW_CHANNELS.items()
        },
    }
    for field, values in temporal_and_spatial.items():
        if values.shape != (FEATURE_DIMENSIONS[field],):
            raise BNCIRefusal(f"generated temporal or spatial dimension changed: {field}")
    probe = _common_average(np.asarray(signal[:2000, :22], dtype="float64"))
    baseline = _causal_band(probe, 8.0, 12.0, 250.0)
    impulse = probe.copy()
    impulse[1700, :] += 100.0
    changed = _causal_band(impulse, 8.0, 12.0, 250.0)
    if not np.array_equal(baseline[:1700], changed[:1700]):
        raise BNCIRefusal("future impulse changed causal output history")
    malformed = root / "malformed.mat"
    _loadmat, savemat = _scipy_io()
    savemat(malformed, {"wrong": np.zeros(1)})
    refusals = 0
    for candidate in (malformed,):
        try:
            load_and_validate_mat(candidate)
        except BNCIRefusal:
            refusals += 1
    if refusals != 1:
        raise BNCIRefusal("generated malformed MAT refusal changed")
    return {
        "case_classes": [
            "strict_MAT_structure_channel_sampling_trial_and_target_firewall",
            "causal_future_impulse_and_feature_dimension_replay",
            "temporal_and_spatial_control_feature_dimensions",
        ],
        "input_bytes": input_bytes,
        "runs": 6,
        "trials": 288,
        "feature_dimensions": {"E1": 88, "E2": 1012, "P": 102},
        "malformed_refusals": refusals,
        "geometry_available": False,
    }


def _seed_for(*parts: Any) -> int:
    return int.from_bytes(hashlib.sha256("|".join(map(str, parts)).encode()).digest()[:8], "big")


def _synthetic_feature(dimension: int, target_index: int, seed: int, strength: float) -> Any:
    np = _np()
    rng = np.random.default_rng(seed)
    output = rng.normal(0.0, 0.35, size=dimension).astype("float64")
    output[target_index] += strength
    output[4:8] += (target_index - 1.5) * strength * 0.05
    return output


def build_generated_feature_cohort() -> tuple[list[dict[str, Any]], dict[str, str], int]:
    np = _np()
    rows: list[dict[str, Any]] = []
    targets: dict[str, str] = {}
    input_bytes = 0
    for participant in PARTICIPANTS:
        participant_index = PARTICIPANTS.index(participant)
        for session in SESSIONS:
            for run in range(6):
                run_rows: list[dict[str, Any]] = []
                for trial, target in enumerate(CLASSES):
                    seed = _seed_for(participant, session, run, trial)
                    target_index = CLASSES.index(target)
                    identity = {
                        "participant": participant,
                        "session": session,
                        "run_ordinal": run,
                        "trial_ordinal": trial,
                    }
                    row_id = _sha256(_canonical_bytes(identity))
                    row: dict[str, Any] = {
                        **identity,
                        "opaque_row_id": row_id,
                        "E1": _synthetic_feature(88, target_index, seed + 1, 3.5),
                        "E2": _synthetic_feature(1012, target_index, seed + 2, 2.3),
                        "P": _synthetic_feature(102, target_index, seed + 3, 1.2),
                        "timing_only": np.asarray(
                            [session == "E", run / 5.0, trial / 3.0, run * 6.5, 6.5],
                            dtype="float64",
                        ),
                        "pre_cue_EEG": _synthetic_feature(88, target_index, seed + 4, 0.25),
                        "early_cue_EEG": _synthetic_feature(88, target_index, seed + 5, 0.65),
                        "central_EEG": _synthetic_feature(68, target_index, seed + 6, 1.0),
                        "frontal_EEG": _synthetic_feature(24, target_index, seed + 7, 0.55),
                        "posterior_EEG": _synthetic_feature(36, target_index, seed + 8, 0.45),
                    }
                    row["E1"][:4] += participant_index * 0.01
                    row["E2"][:4] += participant_index * 0.01
                    run_rows.append(row)
                    targets[row_id] = target
                for index, row in enumerate(run_rows):
                    for family in ("E1", "E2"):
                        row[f"D_{family}"] = (
                            np.zeros_like(row[family])
                            if index == 0
                            else run_rows[index - 1][family].copy()
                        )
                        row[f"rotated_{family}"] = rotate_feature_channels(row[family], family)
                    rows.append(row)
                    input_bytes += sum(
                        int(value.nbytes) for value in row.values() if isinstance(value, np.ndarray)
                    )
    validate_feature_cohort(rows, targets)
    return rows, targets, input_bytes


def rotate_feature_channels(feature: Any, family: str) -> Any:
    np = _np()
    values = np.asarray(feature, dtype="float64")
    if family == "E1":
        if values.shape != (88,):
            raise BNCIRefusal("E1 rotation shape differs")
        return np.roll(values.reshape(4, 22), 7, axis=1).reshape(-1)
    if family != "E2" or values.shape != (1012,):
        raise BNCIRefusal("E2 rotation shape differs")
    triangle = np.triu_indices(22)
    output = []
    permutation = np.roll(np.arange(22), 7)
    for band in values.reshape(4, 253):
        matrix = np.zeros((22, 22), dtype="float64")
        matrix[triangle] = band
        matrix[(triangle[1], triangle[0])] = band
        output.append(matrix[np.ix_(permutation, permutation)][triangle])
    return np.concatenate(output)


def validate_feature_cohort(rows: Sequence[Mapping[str, Any]], targets: Mapping[str, str]) -> None:
    if len(rows) != 9 * 2 * 6 * 4 or len(targets) != len(rows):
        raise BNCIRefusal("generated feature cohort count differs")
    expected_array_fields = set(FEATURE_DIMENSIONS) | {
        "D_E1", "D_E2", "rotated_E1", "rotated_E2"
    }
    expected_dimensions = {
        **FEATURE_DIMENSIONS,
        "D_E1": 88,
        "D_E2": 1012,
        "rotated_E1": 88,
        "rotated_E2": 1012,
    }
    identities = set()
    for row in rows:
        if set(row).intersection({"target", "label", "class", "classes", "y"}):
            raise BNCIRefusal("target leaked into generated predictive row")
        if row.get("participant") not in PARTICIPANTS or row.get("session") not in SESSIONS:
            raise BNCIRefusal("generated participant or session differs")
        row_id = row.get("opaque_row_id")
        if not isinstance(row_id, str) or row_id not in targets:
            raise BNCIRefusal("generated opaque row identity differs")
        if row_id in identities:
            raise BNCIRefusal("generated opaque row identity is duplicated")
        identities.add(row_id)
        if targets[row_id] not in CLASSES:
            raise BNCIRefusal("generated sealed target differs")
        if not expected_array_fields.issubset(row):
            raise BNCIRefusal("generated predictive feature inventory differs")
        for field, dimension in expected_dimensions.items():
            values = row[field]
            if getattr(values, "shape", None) != (dimension,):
                raise BNCIRefusal(f"generated feature dimension differs: {field}")


def _feature_hash(rows: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for row in sorted(rows, key=lambda item: str(item["opaque_row_id"])):
        digest.update(str(row["opaque_row_id"]).encode())
        for field in sorted(set(FEATURE_DIMENSIONS) | {"D_E1", "D_E2", "rotated_E1", "rotated_E2"}):
            digest.update(_np().ascontiguousarray(row[field], dtype="float64").tobytes())
    return digest.hexdigest()


def _matrix(rows: Sequence[Mapping[str, Any]], field: str) -> Any:
    np = _np()
    return np.stack([np.asarray(row[field], dtype="float64") for row in rows])


def _labels(rows: Sequence[Mapping[str, Any]], targets: Mapping[str, str]) -> list[str]:
    return [targets[str(row["opaque_row_id"])] for row in rows]


def fit_logistic(
    features: Any,
    labels: Sequence[str],
    *,
    C: float,
    log_euclidean_reference: bool = False,
) -> FrozenLogistic:
    np = _np()
    values = np.asarray(features, dtype="float64")
    if values.ndim != 2 or values.shape[0] != len(labels) or set(labels) != set(CLASSES):
        raise BNCIRefusal("logistic fit rows or labels differ")
    source_reference = (
        values.mean(axis=0) if log_euclidean_reference else np.zeros(values.shape[1])
    )
    tangent_values = values - source_reference
    mean = tangent_values.mean(axis=0)
    scale = tangent_values.std(axis=0)
    scale[scale < 1e-12] = 1.0
    standardized = (tangent_values - mean) / scale
    model = _logistic_class()(
        C=C,
        solver="lbfgs",
        max_iter=80,
        tol=1e-6,
        class_weight=None,
        random_state=0,
    )
    model.fit(standardized, list(labels))
    classes = tuple(str(value) for value in model.classes_)
    if set(classes) != set(CLASSES):
        raise BNCIRefusal("logistic fitted class inventory differs")
    return FrozenLogistic(
        source_reference=source_reference,
        mean=mean,
        scale=scale,
        classes=classes,
        coefficient=np.asarray(model.coef_, dtype="float64"),
        intercept=np.asarray(model.intercept_, dtype="float64"),
    )


def predict_probabilities(model: FrozenLogistic, features: Any) -> Any:
    np = _np()
    values = np.asarray(features, dtype="float64")
    if values.ndim != 2 or values.shape[1] != model.mean.shape[0]:
        raise BNCIRefusal("logistic prediction dimension differs")
    tangent_values = values - model.source_reference
    scores = (
        (tangent_values - model.mean) / model.scale
    ) @ model.coefficient.T + model.intercept
    scores -= scores.max(axis=1, keepdims=True)
    probabilities = np.exp(scores)
    probabilities /= probabilities.sum(axis=1, keepdims=True)
    order = [model.classes.index(target) for target in CLASSES]
    return probabilities[:, order]


def _model_hash(model: FrozenLogistic) -> str:
    np = _np()
    digest = hashlib.sha256("|".join(model.classes).encode())
    for value in (
        model.source_reference,
        model.mean,
        model.scale,
        model.coefficient,
        model.intercept,
    ):
        digest.update(np.ascontiguousarray(value, dtype="float64").tobytes())
    return digest.hexdigest()


def _log_loss(labels: Sequence[str], probabilities: Any) -> float:
    np = _np()
    values = np.asarray(probabilities, dtype="float64")
    return float(
        -np.mean(
            [math.log(max(float(values[index, CLASSES.index(label)]), 1e-15)) for index, label in enumerate(labels)]
        )
    )


def _fit(
    rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, str],
    field: str,
    C: float,
    ledger: OperationLedger,
    *,
    labels: Sequence[str] | None = None,
) -> FrozenLogistic:
    ledger.parameter_update_fits += 1
    if ledger.parameter_update_fits > 540:
        raise BNCIRefusal("parameter-update fit cap exceeded")
    return fit_logistic(
        _matrix(rows, field),
        labels or _labels(rows, targets),
        C=C,
        log_euclidean_reference=field in {"E2", "D_E2"},
    )


def _predict(
    model: FrozenLogistic,
    rows: Sequence[Mapping[str, Any]],
    field: str,
    ledger: OperationLedger,
) -> Any:
    ledger.prediction_sets += 1
    ledger.model_inference_runs += 1
    if ledger.prediction_sets > 900:
        raise BNCIRefusal("prediction-set cap exceeded")
    return predict_probabilities(model, _matrix(rows, field))


def _centered_logits(probabilities: Any) -> Any:
    np = _np()
    logits = np.log(np.clip(probabilities, 1e-15, 1.0))
    logits -= logits.mean(axis=1, keepdims=True)
    return logits[:, :3]


def _source_label_rotation(
    rows: Sequence[Mapping[str, Any]], targets: Mapping[str, str]
) -> list[str]:
    output = _labels(rows, targets)
    groups: dict[tuple[str, str, int], list[int]] = {}
    for index, row in enumerate(rows):
        groups.setdefault(
            (str(row["participant"]), str(row["session"]), int(row["run_ordinal"])), []
        ).append(index)
    for indices in groups.values():
        values = [output[index] for index in indices]
        rotated = values[1:] + values[:1]
        for index, value in zip(indices, rotated, strict=True):
            output[index] = value
    return output


def _empirical_prior(labels: Sequence[str]) -> list[float]:
    return [labels.count(target) / len(labels) for target in CLASSES]


def _fusion_source_crossfits(
    source_rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, str],
    family: str,
    ledger: OperationLedger,
) -> tuple[FrozenLogistic, FrozenLogistic]:
    np = _np()
    p_parts = []
    e_parts = []
    d_parts = []
    labels = []
    for participant in sorted({str(row["participant"]) for row in source_rows}):
        train = [row for row in source_rows if row["participant"] != participant]
        check = [row for row in source_rows if row["participant"] == participant]
        p_model = _fit(train, targets, "P", 1.0, ledger)
        e_model = _fit(train, targets, family, 1.0 if family == "E1" else 0.1, ledger)
        d_model = _fit(
            train, targets, f"D_{family}", 1.0 if family == "E1" else 0.1, ledger
        )
        p_parts.append(_centered_logits(_predict(p_model, check, "P", ledger)))
        e_parts.append(_centered_logits(_predict(e_model, check, family, ledger)))
        d_parts.append(_centered_logits(_predict(d_model, check, f"D_{family}", ledger)))
        labels.extend(_labels(check, targets))
    p_values = np.concatenate(p_parts)
    e_values = np.concatenate(e_parts)
    d_values = np.concatenate(d_parts)
    ledger.parameter_update_fits += 2
    if ledger.parameter_update_fits > 540:
        raise BNCIRefusal("fusion fit cap exceeded")
    fusion = fit_logistic(np.concatenate((p_values, e_values), axis=1), labels, C=1.0)
    deranged = fit_logistic(np.concatenate((p_values, d_values), axis=1), labels, C=1.0)
    return fusion, deranged


def _select_family(
    source_rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, str],
    ledger: OperationLedger,
) -> str:
    losses = {"E1": [], "E2": []}
    participants = sorted({str(row["participant"]) for row in source_rows})
    if len(participants) != 8:
        raise BNCIRefusal("inner source participant count differs")
    for family in ("E1", "E2"):
        for participant in participants:
            train = [row for row in source_rows if row["participant"] != participant]
            check = [row for row in source_rows if row["participant"] == participant]
            model = _fit(
                train, targets, family, 1.0 if family == "E1" else 0.1, ledger
            )
            probabilities = _predict(model, check, family, ledger)
            losses[family].append(_log_loss(_labels(check, targets), probabilities))
    mean_e1 = math.fsum(losses["E1"]) / 8.0
    mean_e2 = math.fsum(losses["E2"]) / 8.0
    return "E1" if mean_e1 <= mean_e2 + 1e-12 else "E2"


def _prediction_rows_for_fold(
    source_rows: Sequence[Mapping[str, Any]],
    held_rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, str],
    family: str,
    ledger: OperationLedger,
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    np = _np()
    c_value = 1.0 if family == "E1" else 0.1
    fusion, deranged_fusion = _fusion_source_crossfits(source_rows, targets, family, ledger)
    p_model = _fit(source_rows, targets, "P", 1.0, ledger)
    e_model = _fit(source_rows, targets, family, c_value, ledger)
    d_model = _fit(source_rows, targets, f"D_{family}", c_value, ledger)
    timing_model = _fit(source_rows, targets, "timing_only", 1.0, ledger)
    label_model = _fit(
        source_rows,
        targets,
        family,
        c_value,
        ledger,
        labels=_source_label_rotation(source_rows, targets),
    )
    control_models = {
        field: _fit(source_rows, targets, field, 1.0, ledger)
        for field in (
            "pre_cue_EEG",
            "early_cue_EEG",
            "central_EEG",
            "frontal_EEG",
            "posterior_EEG",
        )
    }
    p_prob = _predict(p_model, held_rows, "P", ledger)
    e_prob = _predict(e_model, held_rows, family, ledger)
    d_prob = _predict(d_model, held_rows, f"D_{family}", ledger)
    fusion_features = np.concatenate((_centered_logits(p_prob), _centered_logits(e_prob)), axis=1)
    deranged_features = np.concatenate(
        (_centered_logits(p_prob), _centered_logits(d_prob)), axis=1
    )
    ledger.prediction_sets += 2
    ledger.model_inference_runs += 2
    probabilities: dict[str, Any] = {
        "selected_E": e_prob,
        "P": p_prob,
        "P_plus_E": predict_probabilities(fusion, fusion_features),
        "P_plus_D_E": predict_probabilities(deranged_fusion, deranged_features),
        "timing_only": _predict(timing_model, held_rows, "timing_only", ledger),
        "exact_zero_EEG": predict_probabilities(
            e_model, np.zeros((len(held_rows), FEATURE_DIMENSIONS[family]))
        ),
        "channel_rotation_EEG": _predict(e_model, held_rows, f"rotated_{family}", ledger),
        "trial_displacement_EEG": _predict(e_model, held_rows, f"D_{family}", ledger),
        "source_label_rotation_EEG": _predict(label_model, held_rows, family, ledger),
    }
    ledger.prediction_sets += 1
    ledger.model_inference_runs += 1
    source_prior = _empirical_prior(_labels(source_rows, targets))
    probabilities["equal_prior_no_signal"] = np.full((len(held_rows), 4), 0.25)
    probabilities["source_empirical_prior"] = np.tile(source_prior, (len(held_rows), 1))
    for field, model in control_models.items():
        probabilities[field] = _predict(model, held_rows, field, ledger)
    rows: list[dict[str, Any]] = []
    from neurodecodekit.evaluation.bnci_2014_001_score import CONDITIONS

    if set(probabilities) != set(CONDITIONS):
        raise BNCIRefusal("final condition inventory differs")
    for row_index, source in enumerate(held_rows):
        identity = {
            "participant": source["participant"],
            "session": source["session"],
            "run_ordinal": source["run_ordinal"],
            "trial_ordinal": source["trial_ordinal"],
            "opaque_row_id": source["opaque_row_id"],
        }
        for condition in CONDITIONS:
            rows.append(
                {
                    **identity,
                    "condition": condition,
                    "probabilities": [float(value) for value in probabilities[condition][row_index]],
                }
            )
    hashes = {
        "P": _model_hash(p_model),
        "selected_E": _model_hash(e_model),
        "D_E": _model_hash(d_model),
        "P_plus_E": _model_hash(fusion),
        "P_plus_D_E": _model_hash(deranged_fusion),
    }
    return rows, hashes


def _source_target_capability(
    source_rows: Sequence[Mapping[str, Any]],
    held_rows: Sequence[Mapping[str, Any]],
    all_targets: Mapping[str, str],
) -> tuple[dict[str, str], dict[str, Any]]:
    source_ids = {str(row["opaque_row_id"]) for row in source_rows}
    held_ids = {str(row["opaque_row_id"]) for row in held_rows}
    if source_ids & held_ids:
        raise BNCIRefusal("source and held-out target identities overlap")
    if not source_ids.issubset(all_targets):
        raise BNCIRefusal("source target capability is incomplete")
    capability = {row_id: str(all_targets[row_id]) for row_id in sorted(source_ids)}
    if set(capability.values()) != set(CLASSES):
        raise BNCIRefusal("source target capability class inventory differs")
    manifest = {
        "source_target_rows": len(capability),
        "held_out_target_rows": 0,
        "held_out_target_identities": 0,
        "capability_sha256": _sha256(_canonical_bytes(capability)),
    }
    return capability, manifest


def _run_single_fold(
    participant: str,
    source_rows: Sequence[Mapping[str, Any]],
    held_rows: Sequence[Mapping[str, Any]],
    source_targets: Mapping[str, str],
) -> dict[str, Any]:
    if participant not in PARTICIPANTS:
        raise BNCIRefusal("outer-fold participant differs")
    if any(row["participant"] == participant for row in source_rows):
        raise BNCIRefusal("held-out participant reached source rows")
    if any(
        row["participant"] != participant or row["session"] != "E"
        for row in held_rows
    ):
        raise BNCIRefusal("held-out fold row identity differs")
    source_ids = {str(row["opaque_row_id"]) for row in source_rows}
    if set(source_targets) != source_ids:
        raise BNCIRefusal("fold target capability exceeds source rows")
    ledger = OperationLedger()
    family = _select_family(source_rows, source_targets, ledger)
    predictions, model_hashes = _prediction_rows_for_fold(
        source_rows, held_rows, source_targets, family, ledger
    )
    return {
        "predictions": predictions,
        "model_hashes": model_hashes,
        "selected_family": family,
        "fit_count": ledger.parameter_update_fits,
        "prediction_sets": ledger.prediction_sets,
        "model_inference_runs": ledger.model_inference_runs,
    }


def _fold_process_main(
    connection: Any,
    participant: str,
    source_rows: Sequence[Mapping[str, Any]],
    held_rows: Sequence[Mapping[str, Any]],
    source_targets: Mapping[str, str],
) -> None:
    try:
        connection.send(
            ("ok", _run_single_fold(participant, source_rows, held_rows, source_targets))
        )
    except Exception as exc:  # pragma: no cover - parent checks the serialized refusal
        connection.send(("error", type(exc).__name__, str(exc)))
    finally:
        connection.close()


def _run_fold_isolated(
    participant: str,
    source_rows: Sequence[Mapping[str, Any]],
    held_rows: Sequence[Mapping[str, Any]],
    source_targets: Mapping[str, str],
) -> dict[str, Any]:
    import multiprocessing

    context = multiprocessing.get_context("spawn")
    receive, send = context.Pipe(duplex=False)
    process = context.Process(
        target=_fold_process_main,
        args=(send, participant, source_rows, held_rows, source_targets),
    )
    process.start()
    send.close()
    if not receive.poll(900.0):
        process.terminate()
        process.join(timeout=10.0)
        raise BNCIRefusal(f"isolated fold timed out: {participant}")
    message = receive.recv()
    receive.close()
    process.join(timeout=30.0)
    if process.is_alive():
        process.terminate()
        process.join(timeout=10.0)
        raise BNCIRefusal(f"isolated fold did not exit: {participant}")
    if process.exitcode != 0 or not isinstance(message, tuple) or not message:
        raise BNCIRefusal(f"isolated fold process failed: {participant}")
    if message[0] != "ok":
        detail = ": ".join(str(value) for value in message[1:])
        raise BNCIRefusal(f"isolated fold refused: {participant}: {detail}")
    result = message[1]
    if not isinstance(result, dict):
        raise BNCIRefusal(f"isolated fold result differs: {participant}")
    return result


def run_nine_folds(
    rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, str],
    *,
    isolate_processes: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    from neurodecodekit.evaluation.bnci_2014_001_score import _prediction_sort_key

    predictions: list[dict[str, Any]] = []
    fold_records = []
    all_model_hashes: dict[str, str] = {}
    held_row_ids: set[str] = set()
    total_fits = 0
    total_prediction_sets = 0
    total_inference_runs = 0
    for participant in PARTICIPANTS:
        source = [row for row in rows if row["participant"] != participant]
        held = [
            row
            for row in rows
            if row["participant"] == participant and row["session"] == "E"
        ]
        forbidden_t = [
            row
            for row in rows
            if row["participant"] == participant and row["session"] == "T"
        ]
        if len(source) != 8 * 2 * 6 * 4 or len(held) != 6 * 4 or len(forbidden_t) != 6 * 4:
            raise BNCIRefusal("outer fold row count differs")
        source_ids = {str(row["opaque_row_id"]) for row in source}
        held_ids = {str(row["opaque_row_id"]) for row in held}
        if source_ids & held_ids:
            raise BNCIRefusal("held-out row reached its source fold")
        source_targets, capability = _source_target_capability(
            source, held + forbidden_t, targets
        )
        result = (
            _run_fold_isolated(participant, source, held, source_targets)
            if isolate_processes
            else _run_single_fold(participant, source, held, source_targets)
        )
        predictions.extend(result["predictions"])
        held_row_ids.update(str(row["opaque_row_id"]) for row in held)
        all_model_hashes.update(
            {
                f"{participant}/{name}": value
                for name, value in result["model_hashes"].items()
            }
        )
        total_fits += int(result["fit_count"])
        total_prediction_sets += int(result["prediction_sets"])
        total_inference_runs += int(result["model_inference_runs"])
        fold_records.append(
            {
                "held_out_participant": participant,
                "source_participants": [value for value in PARTICIPANTS if value != participant],
                "selected_family": result["selected_family"],
                "held_out_E_rows": len(held),
                "held_out_T_rows_used": 0,
                "held_out_calibration_rows": 0,
                "fold_process_isolated": isolate_processes,
                "target_capability": capability,
            }
        )
    expected_held = {
        str(row["opaque_row_id"]) for row in rows if row["session"] == "E"
    }
    if held_row_ids != expected_held:
        raise BNCIRefusal("outer fold held-out identity coverage differs")
    predictions.sort(key=_prediction_sort_key)
    return predictions, {
        "folds": fold_records,
        "fit_count": total_fits,
        "prediction_sets": total_prediction_sets,
        "model_inference_runs": total_inference_runs,
        "isolated_fold_processes": 9 if isolate_processes else 0,
        "model_hashes": dict(sorted(all_model_hashes.items())),
    }


def _sealed_target_rows(
    rows: Sequence[Mapping[str, Any]], targets: Mapping[str, str]
) -> list[dict[str, Any]]:
    from neurodecodekit.evaluation.bnci_2014_001_score import _target_sort_key

    sealed = [
        {
            "participant": row["participant"],
            "session": row["session"],
            "run_ordinal": row["run_ordinal"],
            "trial_ordinal": row["trial_ordinal"],
            "opaque_row_id": row["opaque_row_id"],
            "target": targets[str(row["opaque_row_id"])],
        }
        for row in rows
        if row["session"] == "E"
    ]
    return sorted(sealed, key=_target_sort_key)


def _assert_resources(
    *, started: float, peak_rss: int, output_bytes: int, private_bytes: int
) -> None:
    if time.monotonic() - started > 3600.0:
        raise BNCIRefusal("generated qualification runtime cap exceeded")
    if peak_rss > 1_073_741_824:
        raise BNCIRefusal("generated qualification RSS cap exceeded")
    if output_bytes > 4_194_304:
        raise BNCIRefusal("generated public output cap exceeded")
    if private_bytes > 536_870_912:
        raise BNCIRefusal("generated private derivative cap exceeded")


def run_generated_qualification(output_path: str | Path) -> dict[str, Any]:
    """Run the sole generated/mock G1 qualification and publish one aggregate result."""

    from neurodecodekit.datasets.bnci_2014_001_acquisition import (
        run_generated_acquisition_cases,
    )
    from neurodecodekit.evaluation import bnci_2014_001_score as scorer

    output = _prepare_output_path(output_path)
    started = time.monotonic()
    assert_single_thread_environment()
    versions = assert_exact_versions()
    contract = load_contract()
    decision = load_decision()
    initial_free_disk = shutil.disk_usage(output.parent).free
    if initial_free_disk < 5_368_709_120:
        raise BNCIRefusal("generated qualification free-disk floor failed")
    work_root = Path(tempfile.mkdtemp(prefix="neurodecodekit-bnci-g1-", dir=output.parent))
    try:
        mat_cases = run_generated_mat_cases(work_root / "mat")
        acquisition_cases = run_generated_acquisition_cases(work_root / "acquisition")
        rows, targets, feature_bytes = build_generated_feature_cohort()
        feature_hash_before = _feature_hash(rows)
        target_hash_before = _sha256(_canonical_bytes(dict(sorted(targets.items()))))
        predictions, model_report = run_nine_folds(rows, targets)
        if (
            model_report["fit_count"] != 468
            or model_report["prediction_sets"] != 495
            or model_report["model_inference_runs"] != 495
            or model_report["isolated_fold_processes"] != 9
        ):
            raise BNCIRefusal("generated fixed fit or prediction schedule changed")
        if _feature_hash(rows) != feature_hash_before:
            raise BNCIRefusal("model orchestration mutated target-free features")
        if _sha256(_canonical_bytes(dict(sorted(targets.items())))) != target_hash_before:
            raise BNCIRefusal("model orchestration mutated sealed targets")
        prediction_payload = scorer.canonical_prediction_jsonl(predictions)
        sealed_rows = _sealed_target_rows(rows, targets)
        target_payload = scorer.canonical_target_jsonl(sealed_rows)
        source_hashes = {"generated_feature_cohort": feature_hash_before}
        code_hash = _sha256(
            Path(__file__).read_bytes()
            + Path(scorer.__file__).read_bytes()
            + (_repo_root() / "src/neurodecodekit/datasets/bnci_2014_001_acquisition.py").read_bytes()
        )
        configuration_hash = _sha256(
            CONTRACT_SHA256.encode() + DECISION_SHA256.encode()
        )
        split_protocol_hash = _sha256(
            _canonical_bytes(
                {
                    "participants": PARTICIPANTS,
                    "source_sessions": SESSIONS,
                    "held_out_session": "E",
                    "held_out_T_use": "forbidden",
                    "folds": 9,
                }
            )
        )
        bindings = scorer.FreezeBindings(
            configuration_hash=configuration_hash,
            code_hash=code_hash,
            source_cache_hashes=source_hashes,
            split_protocol_hash=split_protocol_hash,
            sealed_target_payload_sha256=_sha256(target_payload),
        )
        freeze = scorer.build_prediction_freeze(prediction_payload, bindings=bindings)
        scorer.validate_prediction_freeze(freeze, prediction_payload, bindings=bindings)
        swapped_targets = [
            {**row, "target": CLASSES[(CLASSES.index(str(row["target"])) + 1) % 4]}
            for row in sealed_rows
        ]
        swapped_payload = scorer.canonical_target_jsonl(swapped_targets)
        if swapped_payload == target_payload:
            raise BNCIRefusal("generated target-swap canary did not change")
        if scorer.build_prediction_freeze(prediction_payload, bindings=bindings) != freeze:
            raise BNCIRefusal("target-blind freeze replay changed")
        mutation_refusals = 0
        for mutation in ("prediction", "configuration", "target_hash"):
            try:
                if mutation == "prediction":
                    scorer.validate_prediction_freeze(
                        freeze, prediction_payload + b"{}\n", bindings=bindings
                    )
                elif mutation == "configuration":
                    scorer.validate_prediction_freeze(
                        freeze,
                        prediction_payload,
                        bindings=scorer.FreezeBindings(
                            configuration_hash="0" * 64,
                            code_hash=bindings.code_hash,
                            source_cache_hashes=bindings.source_cache_hashes,
                            split_protocol_hash=bindings.split_protocol_hash,
                            sealed_target_payload_sha256=bindings.sealed_target_payload_sha256,
                        ),
                    )
                else:
                    scorer.validate_prediction_freeze(
                        freeze,
                        prediction_payload,
                        bindings=scorer.FreezeBindings(
                            configuration_hash=bindings.configuration_hash,
                            code_hash=bindings.code_hash,
                            source_cache_hashes=bindings.source_cache_hashes,
                            split_protocol_hash=bindings.split_protocol_hash,
                            sealed_target_payload_sha256="0" * 64,
                        ),
                    )
            except scorer.BNCIScoreRefusal:
                mutation_refusals += 1
        if mutation_refusals != 3:
            raise BNCIRefusal("prediction-freeze mutation matrix changed")
        target_loads = 0

        def load_targets_once() -> bytes:
            nonlocal target_loads
            target_loads += 1
            if target_loads != 1:
                raise BNCIRefusal("generated target loader called more than once")
            return target_payload

        score = scorer.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=lambda: all(
                len(value) == 64 for value in model_report["model_hashes"].values()
            ),
            sealed_target_loader=load_targets_once,
        )
        if score["route"] not in {
            "BNCIC3C5-R2", "BNCIC3C5-R3", "BNCIC3C5-R4", "BNCIC3C5-R5"
        }:
            raise BNCIRefusal("generated scorer did not reach a scientific router branch")
        router = {
            scorer.route_result(integrity=False, C3=False, C5_partial=False),
            scorer.route_result(integrity=True, C3=False, C5_partial=False),
            scorer.route_result(integrity=True, C3=True, C5_partial=False),
            scorer.route_result(integrity=True, C3=False, C5_partial=True),
            scorer.route_result(integrity=True, C3=True, C5_partial=True),
        }
        if router != {
            "BNCIC3C5-R0", "BNCIC3C5-R2", "BNCIC3C5-R3", "BNCIC3C5-R4", "BNCIC3C5-R5"
        }:
            raise BNCIRefusal("generated router coverage changed")
        if scorer.exact_sign_flip_p([0.0] * 9) != 1.0:
            raise BNCIRefusal("nine-participant sign-flip tie handling changed")
        case_classes = sorted(
            set(mat_cases["case_classes"])
            | set(acquisition_cases["case_classes"])
            | {
                "nine_outer_and_eight_inner_participant_firewalls",
                "E1_E2_P_fusion_control_and_fit_schedule",
                "target_swap_prediction_and_checkpoint_invariance",
                "canonical_prediction_freeze_and_mutation_refusal",
                "aggregate_C3_C5_sign_flip_and_router_scoring",
                "output_runtime_RSS_disk_and_no_second_publication_refusal",
            }
        )
        runtime = time.monotonic() - started
        peak_rss = peak_process_tree_rss_bytes()
        private_bytes = sum(
            path.stat().st_size
            for path in work_root.rglob("*")
            if path.is_file() and not path.is_symlink()
        ) + len(prediction_payload) + len(target_payload)
        summary: dict[str, Any] = {
            "schema_name": "neurodecodekit.bnci_2014_001_stage_g1_result",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "passed_generated_mocked_qualification_only",
            "qualification_invocations": 1,
            "case_classes": case_classes,
            "case_classes_passed": len(case_classes),
            "generated_MAT_runs": mat_cases["runs"],
            "generated_MAT_trials": mat_cases["trials"],
            "generated_feature_rows": len(rows),
            "generated_held_out_target_rows": len(sealed_rows),
            "outer_folds": len(model_report["folds"]),
            "isolated_fold_processes": model_report["isolated_fold_processes"],
            "inner_source_participant_folds_per_outer": 8,
            "selected_E1_folds": sum(
                fold["selected_family"] == "E1" for fold in model_report["folds"]
            ),
            "selected_E2_folds": sum(
                fold["selected_family"] == "E2" for fold in model_report["folds"]
            ),
            "parameter_update_fits": model_report["fit_count"],
            "prediction_sets": model_report["prediction_sets"],
            "model_inference_runs": model_report["model_inference_runs"],
            "prediction_rows": len(predictions),
            "prediction_freeze_mutation_refusals": mutation_refusals,
            "fold_target_capabilities_with_held_targets": sum(
                fold["target_capability"]["held_out_target_rows"] > 0
                or fold["target_capability"]["held_out_target_identities"] > 0
                for fold in model_report["folds"]
            ),
            "synthetic_target_deliveries": target_loads,
            "synthetic_scoring_events": int(score["scoring_events"]),
            "synthetic_router_route": score["route"],
            "input_bytes": mat_cases["input_bytes"] + feature_bytes + acquisition_cases["accepted_bytes"],
            "private_generated_bytes_peak": private_bytes,
            "output_bytes": 0,
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "initial_free_disk_bytes": initial_free_disk,
            "raw_data_reads": 0,
            "real_cache_reads": 0,
            "real_MAT_opens": 0,
            "real_signal_event_artifact_target_or_label_reads": 0,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "real_parameter_update_fits": 0,
            "real_model_inference_runs": 0,
            "real_prediction_sets": 0,
            "real_target_deliveries": 0,
            "real_scoring_events": 0,
            "retained_generated_payload_bytes": 0,
            "producer_is_causal": True,
            "end_to_end_latency_measured": False,
            "package_versions": versions,
            "configuration_hash": configuration_hash,
            "split_protocol_hash": split_protocol_hash,
            "source_cache_hashes": source_hashes,
            "prediction_freeze_record_sha256": freeze["freeze_record_sha256"],
            "warnings": [
                "generated_fixture_is_engineering_qualification_not_scientific_evidence",
                "synthetic_router_route_has_no_claim_value",
                "geometry_is_unavailable_in_original_MAT_payload_contract",
                "no_real_BNCI_payload_was_opened_or_downloaded",
                "no_unseen_person_or_EEG_beyond_EOG_result_is_established",
                "end_to_end_latency_was_not_measured",
            ],
            "claim_boundary": decision["claim_boundary"],
            "contract_status_before_execution": contract["status"],
        }
        for _ in range(6):
            payload = _canonical_bytes(summary)
            if summary["output_bytes"] == len(payload):
                break
            summary["output_bytes"] = len(payload)
        payload = _canonical_bytes(summary)
        _assert_resources(
            started=started,
            peak_rss=peak_rss,
            output_bytes=len(payload),
            private_bytes=private_bytes,
        )
        _atomic_write(output, payload)
        if _regular_no_follow(output).st_size != len(payload):
            raise BNCIRefusal("published generated result byte count differs")
        try:
            _prepare_output_path(output)
        except BNCIRefusal:
            pass
        else:
            raise BNCIRefusal("second generated publication was not refused")
        return summary
    finally:
        shutil.rmtree(work_root)
