"""Generated qualification and frozen computation for EEGMMIDB-UG1."""

from __future__ import annotations

import ctypes
import errno
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
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SCHEMA_VERSION = "0.1.0"
LANE_ID = "EEGMMIDB-UG1"
CONTRACT_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_generalization_contract.v0.json"
)
AMENDMENT_RELATIVE_PATH = Path(
    "registries/eegmmidb_unseen_participant_generalization_amendment_1.v0.json"
)
CONTRACT_SHA256 = "1df7f4f139809d94a6135d979e8cd37e1ece9b87d001b12bcefd037c63b8ac37"
AMENDMENT_SHA256 = "2d6576e2f31383efdcc1ea9f309e70c4beabdf440149567f7eabcbf1a2b177dd"
SOURCE_PARTICIPANTS = tuple(f"S{index:03d}" for index in range(1, 16))
FRESH_PARTICIPANTS = tuple(f"S{index:03d}" for index in range(16, 31))
TASK_RUNS = {
    "execution": {"source": ("03", "07"), "fresh": ("11",)},
    "imagery": {"source": ("04", "08"), "fresh": ("12",)},
}
CONDITIONS = (
    "primary_whole_head",
    "equal_prior_no_signal",
    "timing_only",
    "exact_zero",
    "fixed_channel_permutation",
    "nonwrapping_event_displacement",
    "fixed_source_label_derangement",
    "pre_cue",
    "early_cue",
    "central_view",
    "frontal_view",
    "occipital_view",
)
FITTED_CONDITIONS = (
    "primary_whole_head",
    "timing_only",
    "fixed_source_label_derangement",
    "pre_cue",
    "early_cue",
    "central_view",
    "frontal_view",
    "occipital_view",
)
MODEL_DIMENSIONS = {
    "primary_whole_head": 320,
    "timing_only": 3,
    "fixed_source_label_derangement": 320,
    "pre_cue": 320,
    "early_cue": 320,
    "central_view": 90,
    "frontal_view": 40,
    "occipital_view": 40,
}
PREDICTIVE_FEATURE_DIMENSIONS = {
    "primary_whole_head": 320,
    "timing_only": 3,
    "fixed_channel_permutation": 320,
    "nonwrapping_event_displacement": 320,
    "pre_cue": 320,
    "early_cue": 320,
    "central_view": 90,
    "frontal_view": 40,
    "occipital_view": 40,
}
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class UG1Refusal(RuntimeError):
    """Fail-closed refusal for a frozen UG1 invariant."""


@dataclass(frozen=True)
class Annotation:
    onset_seconds: float
    description: str


@dataclass(frozen=True)
class RunRecord:
    participant: str
    run: str
    sampling_rate_hz: float
    montage_identity: str
    channel_names: tuple[str, ...]
    channel_geometry_m: Any
    signal_volts: Any
    annotations: tuple[Annotation, ...]


@dataclass(frozen=True)
class FrozenLDA:
    mean: Any
    scale: Any
    classes: tuple[str, str]
    coef: Any
    intercept: Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _reject_duplicate_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise UG1Refusal(f"duplicate checkpoint JSON key: {key}")
        result[key] = value
    return result


def _load_bound_json(relative_path: Path, expected_sha256: str) -> dict[str, Any]:
    path = _repo_root() / relative_path
    payload = path.read_bytes()
    if _sha256_bytes(payload) != expected_sha256:
        raise UG1Refusal(f"registered artifact hash changed: {relative_path}")
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise UG1Refusal(f"registered artifact is not an object: {relative_path}")
    return parsed


def load_contract() -> dict[str, Any]:
    contract = _load_bound_json(CONTRACT_RELATIVE_PATH, CONTRACT_SHA256)
    if contract.get("contract_id") != LANE_ID:
        raise UG1Refusal("UG1 contract identity changed")
    return contract


def load_amendment() -> dict[str, Any]:
    amendment = _load_bound_json(AMENDMENT_RELATIVE_PATH, AMENDMENT_SHA256)
    if amendment.get("lane_id") != LANE_ID or amendment.get("amendment_id") != "EEGMMIDB-UG1-A1":
        raise UG1Refusal("UG1 amendment identity changed")
    return amendment


def _np():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("UG1 arrays require: pip install -e '.[classical]'") from exc
    return np


def _sosfilt():
    try:
        from scipy.signal import sosfilt
    except ImportError as exc:
        raise RuntimeError("UG1 causal filtering requires: pip install -e '.[classical]'") from exc
    return sosfilt


def _lda_class():
    try:
        from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    except ImportError as exc:
        raise RuntimeError("UG1 LDA requires: pip install -e '.[classical]'") from exc
    return LinearDiscriminantAnalysis


def assert_exact_versions() -> dict[str, str]:
    expected = load_amendment()["model_contract"]["required_versions"]
    distribution_names = {
        "numpy": "numpy",
        "scipy": "scipy",
        "mne": "mne",
        "scikit_learn": "scikit-learn",
    }
    observed: dict[str, str] = {}
    for key, distribution in distribution_names.items():
        try:
            observed[key] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError as exc:
            raise UG1Refusal(f"required package unavailable: {distribution}") from exc
        if observed[key] != expected[key]:
            raise UG1Refusal(
                f"required package version mismatch for {distribution}: "
                f"expected {expected[key]}, observed {observed[key]}"
            )
    return observed


def assert_single_thread_environment() -> None:
    changed = {
        name: os.environ.get(name) for name in THREAD_ENVIRONMENT if os.environ.get(name) != "1"
    }
    if changed:
        raise UG1Refusal(f"one-thread environment is not frozen: {sorted(changed)}")


def peak_process_tree_rss_bytes() -> int:
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    multiplier = 1 if os.uname().sysname == "Darwin" else 1024
    return int((own + children) * multiplier)


def _regular_no_follow(path: Path) -> os.stat_result:
    observed = os.lstat(path)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISREG(observed.st_mode):
        raise UG1Refusal(f"not a regular no-follow file: {path}")
    if observed.st_nlink != 1:
        raise UG1Refusal(f"hard-linked file refused: {path}")
    return observed


def canonicalize_annotations(
    annotations: Sequence[Annotation],
    *,
    sample_count: int,
    sampling_rate_hz: float = 160.0,
) -> tuple[dict[str, Any], ...]:
    if sampling_rate_hz != 160.0:
        raise UG1Refusal("sampling rate must be exactly 160 Hz")
    allowed = {"T0", "T1", "T2"}
    rows = []
    for source_ordinal, annotation in enumerate(annotations):
        if annotation.description not in allowed:
            raise UG1Refusal("annotation vocabulary changed")
        onset = float(annotation.onset_seconds)
        if not math.isfinite(onset):
            raise UG1Refusal("annotation onset is not finite")
        cue_sample = round(onset * 160.0)
        if cue_sample < 0 or cue_sample >= sample_count:
            raise UG1Refusal("annotation cue sample is outside the run")
        if annotation.description != "T0":
            rows.append((cue_sample, source_ordinal, annotation.description))
    rows.sort(key=lambda item: (item[0], item[1]))
    cue_samples = [item[0] for item in rows]
    if len(set(cue_samples)) != len(cue_samples):
        raise UG1Refusal("duplicate usable cue sample")
    if len(rows) != 15:
        raise UG1Refusal("each run must contain exactly 15 usable T1/T2 annotations")
    if {item[2] for item in rows} != {"T1", "T2"}:
        raise UG1Refusal("each run must contain both T1 and T2")
    return tuple(
        {
            "cue_sample": cue_sample,
            "source_ordinal": source_ordinal,
            "event_ordinal": event_ordinal,
            "target": target,
        }
        for event_ordinal, (cue_sample, source_ordinal, target) in enumerate(rows)
    )


def common_average_reference(signal_volts: Any) -> Any:
    np = _np()
    values = np.asarray(signal_volts, dtype="float64")
    if values.ndim != 2 or values.shape[0] != 64:
        raise UG1Refusal("signal must have shape [64, samples]")
    if not np.isfinite(values).all():
        raise UG1Refusal("signal contains a non-finite value")
    return values - values.mean(axis=0, keepdims=True)


def causal_filter(
    referenced_signal: Any,
    *,
    chunk_sizes: Sequence[int] | None = None,
    implementation: str = "sosfilt",
) -> Any:
    if implementation != "sosfilt":
        raise UG1Refusal("only causal scipy.signal.sosfilt is allowed")
    np = _np()
    values = np.asarray(referenced_signal, dtype="float64")
    if values.ndim != 2 or values.shape[0] != 64:
        raise UG1Refusal("referenced signal must have shape [64, samples]")
    sos = np.asarray(load_amendment()["causal_preprocessing"]["literal_SOS"], dtype="float64")
    filter_fn = _sosfilt()
    if chunk_sizes is None:
        chunks = (values.shape[1],)
    else:
        chunks = tuple(int(size) for size in chunk_sizes)
        if not chunks or any(size <= 0 for size in chunks) or sum(chunks) != values.shape[1]:
            raise UG1Refusal("chunk sizes must be positive and cover one complete run")
    zi = np.zeros((sos.shape[0], values.shape[0], 2), dtype="float64")
    outputs = []
    offset = 0
    for size in chunks:
        filtered, zi = filter_fn(sos, values[:, offset : offset + size], axis=-1, zi=zi)
        outputs.append(filtered)
        offset += size
    return np.concatenate(outputs, axis=1)


def window_features(filtered_signal: Any, start: int, stop: int, *, bins: int = 4) -> Any:
    np = _np()
    values = np.asarray(filtered_signal, dtype="float64")
    if values.ndim != 2 or start < 0 or stop > values.shape[1] or stop <= start:
        raise UG1Refusal("window is out of bounds; padding is forbidden")
    epoch = values[:, start:stop]
    if epoch.shape[1] % bins:
        raise UG1Refusal("window samples must divide exactly into bins")
    means = epoch.reshape(epoch.shape[0], bins, epoch.shape[1] // bins).mean(axis=2)
    axis = np.linspace(-1.0, 1.0, epoch.shape[1], dtype="float64")
    slopes = (epoch @ axis) / float(axis @ axis)
    return np.concatenate((means, slopes[:, None]), axis=1).reshape(-1)


def _channel_indices(names: Sequence[str], selected: Sequence[str]) -> tuple[int, ...]:
    lookup = {name: index for index, name in enumerate(names)}
    if len(lookup) != len(names) or any(name not in lookup for name in selected):
        raise UG1Refusal("channel set does not match the frozen order")
    return tuple(lookup[name] for name in selected)


def extract_run(record: RunRecord) -> tuple[dict[str, Any], dict[str, Any]]:
    np = _np()
    amendment = load_amendment()
    expected_channels = tuple(amendment["channel_contract"]["exact_order"])
    if record.channel_names != expected_channels:
        raise UG1Refusal("channel names or order changed")
    if float(record.sampling_rate_hz) != 160.0:
        raise UG1Refusal("sampling rate changed")
    if record.montage_identity != "standard_1005":
        raise UG1Refusal("montage identity changed")
    geometry = np.asarray(record.channel_geometry_m, dtype="float64")
    if geometry.shape != (64, 3) or not np.isfinite(geometry).all():
        raise UG1Refusal("complete finite 64-channel geometry is required")
    referenced = common_average_reference(record.signal_volts)
    filtered = causal_filter(referenced)
    annotations = canonicalize_annotations(
        record.annotations,
        sample_count=filtered.shape[1],
        sampling_rate_hz=record.sampling_rate_hz,
    )
    channel_contract = amendment["channel_contract"]
    central = _channel_indices(expected_channels, channel_contract["central_view"])
    frontal = _channel_indices(expected_channels, channel_contract["frontal_view"])
    occipital = _channel_indices(expected_channels, channel_contract["occipital_view"])
    permutation = tuple(amendment["control_contract"]["channel_permutation_indices"])
    if sorted(permutation) != list(range(64)):
        raise UG1Refusal("literal channel permutation changed")
    rows: list[dict[str, Any]] = []
    targets: list[dict[str, Any]] = []
    previous_cue: int | None = None
    for annotation in annotations:
        cue = int(annotation["cue_sample"])
        primary = window_features(filtered, cue + 160, cue + 480)
        pre_cue = window_features(filtered, cue - 320, cue)
        early_cue = window_features(filtered, cue, cue + 160)
        event_ordinal = int(annotation["event_ordinal"])
        row_id = _sha256_bytes(
            f"{LANE_ID}|{record.participant}|{record.run}|{event_ordinal}|{cue}".encode()
        )[:24]
        rows.append(
            {
                "opaque_row_id": row_id,
                "participant": record.participant,
                "run": record.run,
                "event_ordinal": event_ordinal,
                "cue_sample": cue,
                "primary_whole_head": primary,
                "fixed_channel_permutation": window_features(
                    filtered[np.asarray(permutation, dtype="int64")], cue + 160, cue + 480
                ),
                "pre_cue": pre_cue,
                "early_cue": early_cue,
                "central_view": window_features(
                    filtered[np.asarray(central)], cue + 160, cue + 480
                ),
                "frontal_view": window_features(
                    filtered[np.asarray(frontal)], cue + 160, cue + 480
                ),
                "occipital_view": window_features(
                    filtered[np.asarray(occipital)], cue + 160, cue + 480
                ),
                "timing_only": np.asarray(
                    [
                        event_ordinal / 14.0,
                        cue / 160.0,
                        0.0 if previous_cue is None else (cue - previous_cue) / 160.0,
                    ],
                    dtype="float64",
                ),
            }
        )
        targets.append({"opaque_row_id": row_id, "target": annotation["target"]})
        previous_cue = cue
    for index, row in enumerate(rows):
        row["nonwrapping_event_displacement"] = (
            np.zeros(320, dtype="float64")
            if index == 0
            else np.asarray(rows[index - 1]["primary_whole_head"], dtype="float64").copy()
        )
    target_free = {
        "schema_name": "neurodecodekit.eegmmidb_unseen_participant_target_free_rows",
        "schema_version": SCHEMA_VERSION,
        "task": task_for_run(record.run),
        "rows": rows,
    }
    sealed = {
        "schema_name": "neurodecodekit.eegmmidb_unseen_participant_sealed_targets",
        "schema_version": SCHEMA_VERSION,
        "task": task_for_run(record.run),
        "targets": targets,
    }
    if any("target" in row for row in rows):
        raise UG1Refusal("target leaked into predictive rows")
    return target_free, sealed


def task_for_run(run: str) -> str:
    normalized = f"{int(run):02d}" if str(run).isdigit() else str(run)
    for task, partitions in TASK_RUNS.items():
        if normalized in partitions["source"] + partitions["fresh"]:
            return task
    raise UG1Refusal(f"forbidden UG1 run: {run}")


def _stack_feature(rows: Sequence[Mapping[str, Any]], name: str) -> Any:
    np = _np()
    if not rows:
        raise UG1Refusal("feature rows are empty")
    return np.stack([np.asarray(row[name], dtype="float64") for row in rows], axis=0)


def fit_frozen_lda(features: Any, targets: Sequence[str]) -> FrozenLDA:
    np = _np()
    values = np.asarray(features, dtype="float64")
    labels = np.asarray(targets, dtype="U2")
    if (
        values.ndim != 2
        or values.shape[0] != labels.shape[0]
        or set(labels.tolist()) != {"T1", "T2"}
    ):
        raise UG1Refusal("LDA fit rows or source targets are malformed")
    mean = values.mean(axis=0)
    scale = values.std(axis=0, ddof=0)
    scale = np.where(scale == 0.0, 1.0, scale)
    standardized = (values - mean) / scale
    classifier = _lda_class()(solver="lsqr", shrinkage=0.1, priors=[0.5, 0.5])
    classifier.fit(standardized, labels)
    if tuple(classifier.classes_.tolist()) != ("T1", "T2"):
        raise UG1Refusal("LDA class order changed")
    return FrozenLDA(
        mean=mean,
        scale=scale,
        classes=("T1", "T2"),
        coef=np.asarray(classifier.coef_, dtype="float64"),
        intercept=np.asarray(classifier.intercept_, dtype="float64"),
    )


def predict_frozen_lda(model: FrozenLDA, features: Any) -> list[str]:
    np = _np()
    values = np.asarray(features, dtype="float64")
    if values.ndim != 2 or values.shape[1] != np.asarray(model.mean).shape[0]:
        raise UG1Refusal("predictor feature shape changed")
    decision = ((values - model.mean) / model.scale) @ model.coef.reshape(-1) + float(
        model.intercept.reshape(-1)[0]
    )
    return ["T2" if value > 0.0 else "T1" for value in decision.tolist()]


def derange_target_group(targets: Sequence[str]) -> list[str]:
    """Apply the literal transform to one identity-free ordered target group."""

    permutation = tuple(load_amendment()["control_contract"]["source_label_derangement_indices"])
    if sorted(permutation) != list(range(15)):
        raise UG1Refusal("literal source-label derangement changed")
    values = list(targets)
    if len(values) != 15 or not set(values).issubset({"T1", "T2"}):
        raise UG1Refusal("source-label derangement requires one ordered 15-target group")
    return [values[source] for source in permutation]


def _orchestrate_source_derangement(
    rows: Sequence[Mapping[str, Any]], targets: Sequence[str]
) -> list[str]:
    if len(rows) != len(targets):
        raise UG1Refusal("source row and target counts differ")
    grouped: dict[tuple[str, str], list[int]] = {}
    for index, row in enumerate(rows):
        grouped.setdefault((str(row["participant"]), str(row["run"])), []).append(index)
    output = list(targets)
    for indices in grouped.values():
        indices.sort(key=lambda index: int(rows[index]["event_ordinal"]))
        if len(indices) != 15:
            raise UG1Refusal("source-label derangement requires 15 rows per run")
        transformed = derange_target_group([targets[index] for index in indices])
        for destination, target in zip(indices, transformed, strict=True):
            output[destination] = target
    return output


def balanced_accuracy(targets: Sequence[str], predictions: Sequence[str]) -> float:
    if len(targets) != len(predictions) or not targets:
        raise UG1Refusal("balanced-accuracy rows are malformed")
    recalls = []
    for label in ("T1", "T2"):
        indices = [index for index, value in enumerate(targets) if value == label]
        if not indices:
            raise UG1Refusal("balanced accuracy requires both classes")
        recalls.append(sum(predictions[index] == label for index in indices) / len(indices))
    return sum(recalls) / 2.0


def _model_payload(model: FrozenLDA) -> dict[str, Any]:
    np = _np()
    return {
        "mean": np.asarray(model.mean, dtype="float64"),
        "scale": np.asarray(model.scale, dtype="float64"),
        "coef": np.asarray(model.coef, dtype="float64"),
        "intercept": np.asarray(model.intercept, dtype="float64"),
    }


def _is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str) and len(value) == 64 and set(value).issubset(set("0123456789abcdef"))
    )


def _validate_model_inventory(models: Mapping[str, Mapping[str, FrozenLDA]]) -> None:
    np = _np()
    if set(models) != {"execution", "imagery"}:
        raise UG1Refusal("checkpoint task inventory changed")
    for task in ("execution", "imagery"):
        if set(models[task]) != set(FITTED_CONDITIONS):
            raise UG1Refusal("checkpoint condition inventory changed")
        for condition, model in models[task].items():
            dimension = MODEL_DIMENSIONS[condition]
            arrays = _model_payload(model)
            expected_shapes = {
                "mean": (dimension,),
                "scale": (dimension,),
                "coef": (1, dimension),
                "intercept": (1,),
            }
            if model.classes != ("T1", "T2"):
                raise UG1Refusal("checkpoint LDA classes changed")
            for field, array in arrays.items():
                if array.shape != expected_shapes[field] or array.dtype != np.dtype("float64"):
                    raise UG1Refusal("checkpoint model shape or dtype changed")
                if not np.isfinite(array).all():
                    raise UG1Refusal("checkpoint model contains a non-finite value")
            if np.any(arrays["scale"] <= 0.0):
                raise UG1Refusal("checkpoint scaler contains a non-positive scale")


def _rename_noreplace(source: Path, destination: Path) -> None:
    """Atomically publish one path while refusing an existing destination."""

    libc = ctypes.CDLL(None, use_errno=True)
    system = os.uname().sysname
    if system == "Darwin":
        rename = getattr(libc, "renamex_np", None)
        if rename is None:
            raise UG1Refusal("atomic no-replace rename is unavailable")
        rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
        rename.restype = ctypes.c_int
        result = rename(os.fsencode(source), os.fsencode(destination), 0x00000004)
    elif system == "Linux":
        rename = getattr(libc, "renameat2", None)
        if rename is None:
            raise UG1Refusal("atomic no-replace rename is unavailable")
        rename.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        rename.restype = ctypes.c_int
        result = rename(-100, os.fsencode(source), -100, os.fsencode(destination), 1)
    else:
        raise UG1Refusal("atomic no-replace rename is unsupported on this platform")
    if result == 0:
        return
    error = ctypes.get_errno()
    if error == errno.EEXIST:
        raise UG1Refusal(f"destination appeared before atomic publish: {destination}")
    raise OSError(error, os.strerror(error), destination)


def _atomic_write_bytes(
    path: Path,
    payload: bytes,
    *,
    _fail_before_rename: bool = False,
    _before_rename: Callable[[], None] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise UG1Refusal(f"destination already exists: {path}")
    if path.parent.resolve() != path.parent:
        raise UG1Refusal("destination parent may not traverse a symlink")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            written = stream.write(payload)
            if written != len(payload):
                raise UG1Refusal("short write")
            stream.flush()
            os.fsync(stream.fileno())
        if _fail_before_rename:
            raise UG1Refusal("injected atomic crash before rename")
        if _before_rename is not None:
            _before_rename()
        _rename_noreplace(temporary, path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _prepare_output_path(value: str | Path) -> Path:
    lexical = Path(value)
    if ".." in lexical.parts:
        raise UG1Refusal("Stage G output path traversal is forbidden")
    path = Path(os.path.abspath(os.fspath(lexical)))
    if path.suffix != ".json":
        raise UG1Refusal("Stage G output must be one JSON file")
    if any(part.casefold() in {"data", ".codex_work"} for part in path.parts):
        raise UG1Refusal("Stage G output may not enter a protected data root")
    current = Path(path.anchor)
    for part in path.parent.parts[1:]:
        current /= part
        try:
            observed = os.lstat(current)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(observed.st_mode):
            raise UG1Refusal("Stage G output path crosses a symlink")
        if not stat.S_ISDIR(observed.st_mode):
            raise UG1Refusal("Stage G output parent crosses a non-directory")
    path.parent.mkdir(parents=True, exist_ok=True)
    observed_parent = os.lstat(path.parent)
    if stat.S_ISLNK(observed_parent.st_mode) or not stat.S_ISDIR(observed_parent.st_mode):
        raise UG1Refusal("Stage G output parent is not a no-follow directory")
    return path


def save_checkpoint(
    models: Mapping[str, Mapping[str, FrozenLDA]],
    destination: str | Path,
    *,
    source_payload_hashes: Mapping[str, str],
    code_hash: str,
    configuration_hash: str,
    package_versions: Mapping[str, str],
) -> dict[str, Any]:
    np = _np()
    _validate_model_inventory(models)
    if not _is_sha256(code_hash) or not _is_sha256(configuration_hash):
        raise UG1Refusal("checkpoint code or configuration hash is malformed")
    if not source_payload_hashes or any(
        not isinstance(key, str) or not key or not _is_sha256(value)
        for key, value in source_payload_hashes.items()
    ):
        raise UG1Refusal("checkpoint source payload hashes are malformed")
    if dict(package_versions) != load_amendment()["model_contract"]["required_versions"]:
        raise UG1Refusal("checkpoint package version binding changed")
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise UG1Refusal("checkpoint destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        members: list[dict[str, Any]] = []
        for task in sorted(models):
            for condition in sorted(models[task]):
                for field, array in sorted(_model_payload(models[task][condition]).items()):
                    name = f"{task}.{condition}.{field}.npy"
                    member_path = temporary / name
                    with member_path.open("xb") as stream:
                        np.save(stream, array, allow_pickle=False)
                        stream.flush()
                        os.fsync(stream.fileno())
                    payload = member_path.read_bytes()
                    members.append(
                        {
                            "path": name,
                            "bytes": len(payload),
                            "sha256": _sha256_bytes(payload),
                            "shape": list(array.shape),
                            "dtype": str(array.dtype),
                        }
                    )
        amendment = load_amendment()
        manifest_without_hash = {
            "schema_name": "neurodecodekit.eegmmidb_unseen_participant_checkpoint",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "tasks": sorted(models),
            "conditions": {task: sorted(models[task]) for task in sorted(models)},
            "source_split": {task: list(TASK_RUNS[task]["source"]) for task in sorted(models)},
            "package_versions": dict(sorted(package_versions.items())),
            "channel_order": amendment["channel_contract"]["exact_order"],
            "channel_views": {
                key: amendment["channel_contract"][key]
                for key in ("central_view", "frontal_view", "occipital_view")
            },
            "SOS": amendment["causal_preprocessing"]["literal_SOS"],
            "windows": amendment["feature_contract"]["windows"],
            "LDA_classes": ["T1", "T2"],
            "code_hash": code_hash,
            "configuration_hash": configuration_hash,
            "contract_hash": CONTRACT_SHA256,
            "amendment_hash": AMENDMENT_SHA256,
            "source_payload_hashes": dict(sorted(source_payload_hashes.items())),
            "members": members,
        }
        manifest = dict(manifest_without_hash)
        manifest["manifest_hash"] = _sha256_bytes(_canonical_bytes(manifest_without_hash))
        _atomic_write_bytes(temporary / "manifest.json", _canonical_bytes(manifest))
        _rename_noreplace(temporary, destination)
        return manifest
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def load_checkpoint(
    destination: str | Path,
    *,
    expected_code_hash: str,
    expected_configuration_hash: str,
    expected_source_payload_hashes: Mapping[str, str],
    expected_package_versions: Mapping[str, str],
) -> tuple[dict[str, dict[str, FrozenLDA]], dict[str, Any]]:
    np = _np()
    if not _is_sha256(expected_code_hash) or not _is_sha256(expected_configuration_hash):
        raise UG1Refusal("expected checkpoint code or configuration hash is malformed")
    if not expected_source_payload_hashes or any(
        not isinstance(key, str) or not key or not _is_sha256(value)
        for key, value in expected_source_payload_hashes.items()
    ):
        raise UG1Refusal("expected checkpoint source payload hashes are malformed")
    if dict(expected_package_versions) != load_amendment()["model_contract"]["required_versions"]:
        raise UG1Refusal("expected checkpoint package version binding changed")
    destination = Path(destination)
    observed = os.lstat(destination)
    if stat.S_ISLNK(observed.st_mode) or not stat.S_ISDIR(observed.st_mode):
        raise UG1Refusal("checkpoint is not a regular no-follow directory")
    manifest_path = destination / "manifest.json"
    _regular_no_follow(manifest_path)
    manifest_payload = manifest_path.read_bytes()
    try:
        manifest = json.loads(
            manifest_payload.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_json_object,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UG1Refusal("checkpoint manifest is not strict UTF-8 JSON") from exc
    if not isinstance(manifest, dict) or _canonical_bytes(manifest) != manifest_payload:
        raise UG1Refusal("checkpoint manifest is not canonical JSON")
    manifest_without_hash = {
        key: value for key, value in manifest.items() if key != "manifest_hash"
    }
    if manifest.get("manifest_hash") != _sha256_bytes(_canonical_bytes(manifest_without_hash)):
        raise UG1Refusal("checkpoint manifest hash mismatch")
    amendment = load_amendment()
    exact_fields = {
        "schema_name": "neurodecodekit.eegmmidb_unseen_participant_checkpoint",
        "schema_version": SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "tasks": ["execution", "imagery"],
        "conditions": {
            "execution": sorted(FITTED_CONDITIONS),
            "imagery": sorted(FITTED_CONDITIONS),
        },
        "source_split": {
            "execution": list(TASK_RUNS["execution"]["source"]),
            "imagery": list(TASK_RUNS["imagery"]["source"]),
        },
        "package_versions": dict(expected_package_versions),
        "channel_order": amendment["channel_contract"]["exact_order"],
        "channel_views": {
            key: amendment["channel_contract"][key]
            for key in ("central_view", "frontal_view", "occipital_view")
        },
        "SOS": amendment["causal_preprocessing"]["literal_SOS"],
        "windows": amendment["feature_contract"]["windows"],
        "LDA_classes": ["T1", "T2"],
        "code_hash": expected_code_hash,
        "configuration_hash": expected_configuration_hash,
        "contract_hash": CONTRACT_SHA256,
        "amendment_hash": AMENDMENT_SHA256,
        "source_payload_hashes": dict(sorted(expected_source_payload_hashes.items())),
    }
    if set(manifest) != set(exact_fields) | {"members", "manifest_hash"}:
        raise UG1Refusal("checkpoint manifest field inventory changed")
    if not _is_sha256(manifest.get("manifest_hash")):
        raise UG1Refusal("checkpoint manifest hash is malformed")
    for field, expected in exact_fields.items():
        if manifest.get(field) != expected:
            raise UG1Refusal(f"checkpoint manifest field changed: {field}")
    expected_member_names = {
        f"{task}.{condition}.{field}.npy"
        for task in ("execution", "imagery")
        for condition in FITTED_CONDITIONS
        for field in ("mean", "scale", "coef", "intercept")
    }
    members = manifest.get("members")
    if not isinstance(members, list) or len(members) != len(expected_member_names):
        raise UG1Refusal("checkpoint member inventory changed")
    if [member.get("path") if isinstance(member, dict) else None for member in members] != sorted(
        expected_member_names
    ):
        raise UG1Refusal("checkpoint member order changed")
    arrays: dict[tuple[str, str], dict[str, Any]] = {}
    expected_names = {"manifest.json"}
    for member in members:
        if not isinstance(member, dict):
            raise UG1Refusal("checkpoint member record is malformed")
        if set(member) != {"path", "bytes", "sha256", "shape", "dtype"}:
            raise UG1Refusal("checkpoint member field inventory changed")
        name = member.get("path")
        if (
            not isinstance(name, str)
            or Path(name).name != name
            or name not in expected_member_names
        ):
            raise UG1Refusal("checkpoint member path is malformed")
        if (
            type(member.get("bytes")) is not int
            or member["bytes"] <= 0
            or not _is_sha256(member.get("sha256"))
            or not isinstance(member.get("shape"), list)
            or any(type(value) is not int or value < 0 for value in member["shape"])
            or member.get("dtype") != "float64"
        ):
            raise UG1Refusal("checkpoint member metadata is malformed")
        expected_names.add(name)
        member_path = destination / name
        observed = _regular_no_follow(member_path)
        payload = member_path.read_bytes()
        if observed.st_size != member.get("bytes") or _sha256_bytes(payload) != member.get(
            "sha256"
        ):
            raise UG1Refusal("checkpoint member hash mismatch")
        with member_path.open("rb") as stream:
            array = np.load(stream, allow_pickle=False)
        if list(array.shape) != member.get("shape") or str(array.dtype) != member.get("dtype"):
            raise UG1Refusal("checkpoint member shape or dtype changed")
        task, condition, field, extension = name.split(".")
        if extension != "npy" or field in arrays.setdefault((task, condition), {}):
            raise UG1Refusal("checkpoint member name or field is duplicated")
        arrays[(task, condition)][field] = array
    if {path.name for path in destination.iterdir()} != expected_names:
        raise UG1Refusal("checkpoint contains an unregistered member")
    models: dict[str, dict[str, FrozenLDA]] = {}
    for (task, condition), values in arrays.items():
        if set(values) != {"mean", "scale", "coef", "intercept"}:
            raise UG1Refusal("checkpoint model members are incomplete")
        models.setdefault(task, {})[condition] = FrozenLDA(
            mean=values["mean"],
            scale=values["scale"],
            classes=("T1", "T2"),
            coef=values["coef"],
            intercept=values["intercept"],
        )
    _validate_model_inventory(models)
    return models, manifest


def _attach_source_targets(
    target_free: Mapping[str, Any], sealed: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = [dict(row) for row in target_free["rows"]]
    target_rows = sealed.get("targets")
    if not isinstance(target_rows, list) or len(target_rows) != len(rows):
        raise UG1Refusal("sealed source target rows are malformed")
    target_by_id = {row.get("opaque_row_id"): row.get("target") for row in target_rows}
    if len(target_by_id) != len(target_rows) or set(target_by_id.values()) != {"T1", "T2"}:
        raise UG1Refusal("sealed source target identities or values are malformed")
    targets = []
    for row in rows:
        row_id = row["opaque_row_id"]
        if row_id not in target_by_id:
            raise UG1Refusal("sealed source target identity mismatch")
        targets.append(str(target_by_id[row_id]))
    return rows, targets


def validate_partition(
    rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    targets_by_task: Mapping[str, Sequence[str]] | None,
    *,
    partition: str,
) -> None:
    if partition not in {"source", "fresh"}:
        raise UG1Refusal("partition must be source or fresh")
    expected_participants = SOURCE_PARTICIPANTS if partition == "source" else FRESH_PARTICIPANTS
    expected_rows = 450 if partition == "source" else 225
    for task in ("execution", "imagery"):
        rows = list(rows_by_task.get(task, ()))
        if len(rows) != expected_rows:
            raise UG1Refusal(f"{partition} {task} row count changed")
        expected_runs = set(TASK_RUNS[task][partition])
        observed_ids: set[str] = set()
        groups: dict[tuple[str, str], list[int]] = {}
        for index, row in enumerate(rows):
            if set(row).intersection({"target", "label", "description", "class"}):
                raise UG1Refusal("predictive row contains a forbidden target key")
            participant = str(row.get("participant"))
            run = str(row.get("run"))
            row_id = str(row.get("opaque_row_id"))
            if participant not in expected_participants or run not in expected_runs:
                raise UG1Refusal("partition identity or run changed")
            if row_id in observed_ids:
                raise UG1Refusal("duplicate row identity")
            observed_ids.add(row_id)
            groups.setdefault((participant, run), []).append(index)
        expected_groups = {
            (participant, run) for participant in expected_participants for run in expected_runs
        }
        if set(groups) != expected_groups or any(len(indices) != 15 for indices in groups.values()):
            raise UG1Refusal("participant/run completeness changed")
        if targets_by_task is not None:
            targets = list(targets_by_task.get(task, ()))
            if len(targets) != len(rows):
                raise UG1Refusal("partition target count changed")
            for indices in groups.values():
                if {targets[index] for index in indices} != {"T1", "T2"}:
                    raise UG1Refusal("participant/run class completeness changed")


def validate_source_fresh_isolation(
    source_rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    fresh_rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    source_payload_identities: Sequence[str],
    fresh_payload_identities: Sequence[str],
) -> None:
    """Refuse any row, participant, or payload identity shared across partitions."""

    source_rows = [row for task in ("execution", "imagery") for row in source_rows_by_task[task]]
    fresh_rows = [row for task in ("execution", "imagery") for row in fresh_rows_by_task[task]]
    source_participants = {str(row["participant"]) for row in source_rows}
    fresh_participants = {str(row["participant"]) for row in fresh_rows}
    source_row_ids = {str(row["opaque_row_id"]) for row in source_rows}
    fresh_row_ids = {str(row["opaque_row_id"]) for row in fresh_rows}
    source_payloads = list(source_payload_identities)
    fresh_payloads = list(fresh_payload_identities)
    if source_participants & fresh_participants:
        raise UG1Refusal("source and fresh participant identities overlap")
    if source_row_ids & fresh_row_ids:
        raise UG1Refusal("source and fresh row identities overlap")
    if len(source_payloads) != len(set(source_payloads)) or len(fresh_payloads) != len(
        set(fresh_payloads)
    ):
        raise UG1Refusal("duplicate payload identity within a partition")
    if set(source_payloads) & set(fresh_payloads):
        raise UG1Refusal("source and fresh payload aliases overlap")


def _exact_sign_flip(values: Sequence[float]) -> float:
    if len(values) != 15 or any(not math.isfinite(float(value)) for value in values):
        raise UG1Refusal("exact sign-flip test requires 15 finite participant values")
    observed = sum(float(value) for value in values) / 15.0
    extreme = 0
    for mask in range(1 << 15):
        candidate = (
            sum(
                float(value) if mask & (1 << index) else -float(value)
                for index, value in enumerate(values)
            )
            / 15.0
        )
        if candidate >= observed - 1e-12:
            extreme += 1
    return extreme / float(1 << 15)


def _participant_balanced_accuracy(
    rows: Sequence[Mapping[str, Any]], targets: Sequence[str], predictions: Sequence[str]
) -> dict[str, float]:
    grouped: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        grouped.setdefault(str(row["participant"]), []).append(index)
    return {
        participant: balanced_accuracy(
            [targets[index] for index in indices],
            [predictions[index] for index in indices],
        )
        for participant, indices in sorted(grouped.items())
    }


def _fit_condition(
    rows: Sequence[Mapping[str, Any]], targets: Sequence[str], condition: str
) -> FrozenLDA:
    feature_name = (
        "primary_whole_head" if condition == "fixed_source_label_derangement" else condition
    )
    fit_targets = (
        _orchestrate_source_derangement(rows, targets)
        if condition == "fixed_source_label_derangement"
        else list(targets)
    )
    return fit_frozen_lda(_stack_feature(rows, feature_name), fit_targets)


def run_source_loso_and_fit(
    rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    targets_by_task: Mapping[str, Sequence[str]],
) -> tuple[dict[str, dict[str, FrozenLDA]], dict[str, Any]]:
    validate_partition(rows_by_task, targets_by_task, partition="source")
    fit_count = 0
    prediction_set_count = 0
    loso: dict[str, Any] = {}
    for task in ("execution", "imagery"):
        rows = list(rows_by_task[task])
        targets = list(targets_by_task[task])
        primary_predictions = [""] * len(rows)
        timing_predictions = [""] * len(rows)
        no_signal_predictions = ["T1"] * len(rows)
        for participant in SOURCE_PARTICIPANTS:
            held_indices = [
                index for index, row in enumerate(rows) if row["participant"] == participant
            ]
            train_indices = [index for index in range(len(rows)) if index not in held_indices]
            primary_model = fit_frozen_lda(
                _stack_feature([rows[index] for index in train_indices], "primary_whole_head"),
                [targets[index] for index in train_indices],
            )
            fit_count += 1
            held_primary = predict_frozen_lda(
                primary_model,
                _stack_feature([rows[index] for index in held_indices], "primary_whole_head"),
            )
            for index, prediction in zip(held_indices, held_primary, strict=True):
                primary_predictions[index] = prediction
            prediction_set_count += 1
            if task == "execution":
                timing_model = fit_frozen_lda(
                    _stack_feature([rows[index] for index in train_indices], "timing_only"),
                    [targets[index] for index in train_indices],
                )
                fit_count += 1
                held_timing = predict_frozen_lda(
                    timing_model,
                    _stack_feature([rows[index] for index in held_indices], "timing_only"),
                )
                for index, prediction in zip(held_indices, held_timing, strict=True):
                    timing_predictions[index] = prediction
                prediction_set_count += 2
        primary_scores = _participant_balanced_accuracy(rows, targets, primary_predictions)
        loso[task] = {
            "primary_macro_balanced_accuracy": sum(primary_scores.values()) / 15.0,
            "primary_participant_scores": primary_scores,
        }
        if task == "execution":
            timing_scores = _participant_balanced_accuracy(rows, targets, timing_predictions)
            no_signal_scores = _participant_balanced_accuracy(rows, targets, no_signal_predictions)
            primary_values = [primary_scores[participant] for participant in SOURCE_PARTICIPANTS]
            timing_values = [timing_scores[participant] for participant in SOURCE_PARTICIPANTS]
            no_signal_values = [
                no_signal_scores[participant] for participant in SOURCE_PARTICIPANTS
            ]
            macro_primary = sum(primary_values) / 15.0
            macro_control = max(sum(timing_values) / 15.0, sum(no_signal_values) / 15.0)
            source_gate = load_contract()["source_stop_gate"]
            passed = all(
                (
                    macro_primary >= source_gate["execution_macro_balanced_accuracy_minimum"],
                    macro_primary - macro_control
                    >= source_gate["macro_margin_over_max_no_signal_timing_minimum"],
                    sum(value > 0.5 for value in primary_values)
                    >= source_gate["participants_above_chance_minimum"],
                    _exact_sign_flip([value - 0.5 for value in primary_values])
                    <= source_gate["participant_sign_flip_p_maximum"],
                )
            )
            loso[task].update(
                {
                    "timing_macro_balanced_accuracy": sum(timing_values) / 15.0,
                    "no_signal_macro_balanced_accuracy": sum(no_signal_values) / 15.0,
                    "exact_sign_flip_p_against_chance": _exact_sign_flip(
                        [value - 0.5 for value in primary_values]
                    ),
                    "passed": passed,
                }
            )
    if not loso["execution"]["passed"]:
        return {}, {
            "route": "EEGMMIDBUG1-R1",
            "fit_count": fit_count,
            "prediction_set_count": prediction_set_count,
            "loso": loso,
        }
    models: dict[str, dict[str, FrozenLDA]] = {}
    for task in ("execution", "imagery"):
        rows = list(rows_by_task[task])
        targets = list(targets_by_task[task])
        models[task] = {}
        for condition in FITTED_CONDITIONS:
            models[task][condition] = _fit_condition(rows, targets, condition)
            fit_count += 1
    if fit_count != 61 or prediction_set_count != 60:
        raise UG1Refusal("source fit or LOSO prediction schedule changed")
    return models, {
        "route": "EEGMMIDBUG1-SOURCE-PASS",
        "fit_count": fit_count,
        "prediction_set_count": prediction_set_count,
        "loso": loso,
    }


def _predict_task_values(
    task_models: Mapping[str, FrozenLDA], task_rows: Sequence[Mapping[str, Any]]
) -> dict[str, list[str]]:
    """Predict from a feature-only view with identity structurally unavailable."""

    np = _np()
    if set(task_models) != set(FITTED_CONDITIONS):
        raise UG1Refusal("fresh predictor model inventory changed")
    expected_features = set(PREDICTIVE_FEATURE_DIMENSIONS)
    if any(set(row) != expected_features for row in task_rows):
        raise UG1Refusal("predictor received identity, target, or non-feature state")
    condition_predictions: dict[str, list[str]] = {
        "primary_whole_head": predict_frozen_lda(
            task_models["primary_whole_head"], _stack_feature(task_rows, "primary_whole_head")
        ),
        "equal_prior_no_signal": ["T1"] * len(task_rows),
        "timing_only": predict_frozen_lda(
            task_models["timing_only"], _stack_feature(task_rows, "timing_only")
        ),
        "exact_zero": predict_frozen_lda(
            task_models["primary_whole_head"],
            np.zeros_like(_stack_feature(task_rows, "primary_whole_head")),
        ),
        "fixed_channel_permutation": predict_frozen_lda(
            task_models["primary_whole_head"],
            _stack_feature(task_rows, "fixed_channel_permutation"),
        ),
        "nonwrapping_event_displacement": predict_frozen_lda(
            task_models["primary_whole_head"],
            _stack_feature(task_rows, "nonwrapping_event_displacement"),
        ),
        "fixed_source_label_derangement": predict_frozen_lda(
            task_models["fixed_source_label_derangement"],
            _stack_feature(task_rows, "primary_whole_head"),
        ),
        "pre_cue": predict_frozen_lda(task_models["pre_cue"], _stack_feature(task_rows, "pre_cue")),
        "early_cue": predict_frozen_lda(
            task_models["early_cue"], _stack_feature(task_rows, "early_cue")
        ),
        "central_view": predict_frozen_lda(
            task_models["central_view"], _stack_feature(task_rows, "central_view")
        ),
        "frontal_view": predict_frozen_lda(
            task_models["frontal_view"], _stack_feature(task_rows, "frontal_view")
        ),
        "occipital_view": predict_frozen_lda(
            task_models["occipital_view"], _stack_feature(task_rows, "occipital_view")
        ),
    }
    if tuple(condition_predictions) != CONDITIONS:
        raise UG1Refusal("fresh prediction condition order changed")
    return condition_predictions


def _prediction_trace(values: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    if tuple(values) != CONDITIONS:
        raise UG1Refusal("prediction trace condition order changed")
    lengths = {condition: len(values[condition]) for condition in CONDITIONS}
    if len(set(lengths.values())) != 1:
        raise UG1Refusal("prediction trace shapes changed")
    payload = _canonical_bytes({condition: list(values[condition]) for condition in CONDITIONS})
    return {
        "prediction_bytes_sha256": _sha256_bytes(payload),
        "condition_lengths": lengths,
        "log_bytes_sha256": _sha256_bytes(b""),
        "exception": None,
    }


def _predictive_feature_rows(
    task_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build the only row shape allowed to cross the predictive firewall."""

    forbidden = {"target", "label", "description", "class"}
    required = set(PREDICTIVE_FEATURE_DIMENSIONS)
    result = []
    for row in task_rows:
        if set(row).intersection(forbidden):
            raise UG1Refusal("target-bearing row reached predictive code")
        if not required.issubset(row):
            raise UG1Refusal("predictive feature row is incomplete")
        result.append({name: row[name] for name in sorted(required)})
    return result


def predict_fresh_rows(
    models: Mapping[str, Mapping[str, FrozenLDA]],
    rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[list[dict[str, Any]], int]:
    validate_partition(rows_by_task, None, partition="fresh")
    predictions: list[dict[str, Any]] = []
    prediction_sets = 0
    for task in ("execution", "imagery"):
        task_rows = list(rows_by_task[task])
        task_models = models.get(task, {})
        by_participant = {
            participant: [row for row in task_rows if row["participant"] == participant]
            for participant in FRESH_PARTICIPANTS
        }
        condition_predictions = _predict_task_values(
            task_models, _predictive_feature_rows(task_rows)
        )
        for condition in CONDITIONS:
            values = condition_predictions[condition]
            if len(values) != len(task_rows) or not set(values).issubset({"T1", "T2"}):
                raise UG1Refusal("fresh prediction values are malformed")
            for participant, participant_rows in by_participant.items():
                indices = [
                    index
                    for index, row in enumerate(task_rows)
                    if row["participant"] == participant
                ]
                if len(participant_rows) != 15 or len(indices) != 15:
                    raise UG1Refusal("fresh prediction participant completeness changed")
                prediction_sets += 1
                for index in indices:
                    row = task_rows[index]
                    predictions.append(
                        {
                            "schema_version": SCHEMA_VERSION,
                            "opaque_row_id": row["opaque_row_id"],
                            "task": task,
                            "participant": participant,
                            "run": int(row["run"]),
                            "event_ordinal": row["event_ordinal"],
                            "cue_sample": row["cue_sample"],
                            "condition": condition,
                            "prediction": values[index],
                        }
                    )
    predictions.sort(
        key=lambda row: (
            row["task"],
            row["participant"],
            row["run"],
            row["event_ordinal"],
            row["condition"],
        )
    )
    if prediction_sets != 360 or len(predictions) != 5400:
        raise UG1Refusal("fresh prediction schedule changed")
    return predictions, prediction_sets


def build_synthetic_run_record(
    participant: str = "S001", run: str = "03", *, reorder_annotations: bool = False
) -> RunRecord:
    """Build one deterministic reader-surface fixture without real EEG input."""

    np = _np()
    amendment = load_amendment()
    channels = tuple(amendment["channel_contract"]["exact_order"])
    task = task_for_run(run)
    partition = "source" if participant in SOURCE_PARTICIPANTS else "fresh"
    if participant not in SOURCE_PARTICIPANTS + FRESH_PARTICIPANTS:
        raise UG1Refusal("synthetic participant is outside UG1")
    if run not in TASK_RUNS[task][partition]:
        raise UG1Refusal("synthetic participant/run partition mismatch")
    onsets = np.asarray([3.0 + 5.5 * index for index in range(15)], dtype="float64")
    sample_count = round(float(onsets[-1] + 3.1) * 160.0)
    seed = int.from_bytes(
        hashlib.sha256(f"UG1|reader|{participant}|{run}".encode()).digest()[:8], "big"
    )
    rng = np.random.default_rng(seed)
    signal = rng.normal(0.0, 0.2e-6, size=(64, sample_count)).astype("float64")
    geometry = np.zeros((64, 3), dtype="float64")
    for index in range(64):
        angle = 2.0 * math.pi * index / 64.0
        geometry[index] = (0.09 * math.cos(angle), 0.09 * math.sin(angle), 0.04)
    excluded = set(
        amendment["channel_contract"]["central_view"]
        + amendment["channel_contract"]["frontal_view"]
        + amendment["channel_contract"]["occipital_view"]
    )
    informative = [index for index, channel in enumerate(channels) if channel not in excluded]
    spatial = np.zeros(64, dtype="float64")
    for order, index in enumerate(informative):
        spatial[index] = 1.0 if order % 2 == 0 else -1.0
    spatial -= spatial.mean()
    run_offset = int(run) % 2
    annotations: list[Annotation] = [Annotation(0.5, "T0")]
    time_axis = np.arange(sample_count, dtype="float64") / 160.0
    for event_ordinal, onset in enumerate(onsets.tolist()):
        label_index = (event_ordinal + run_offset) % 2
        label = "T1" if label_index == 0 else "T2"
        annotations.append(Annotation(float(onset), label))
        active = (time_axis >= onset + 1.0) & (time_axis < onset + 3.0)
        relative = time_axis[active] - onset - 1.0
        waveform = 1.5e-6 * (1.0 + 0.35 * np.sin(2.0 * math.pi * 1.0 * relative))
        sign = -1.0 if label == "T1" else 1.0
        signal[:, active] += sign * spatial[:, None] * waveform[None, :]
    if reorder_annotations:
        annotations = [annotations[0], *reversed(annotations[1:])]
    return RunRecord(
        participant=participant,
        run=run,
        sampling_rate_hz=160.0,
        montage_identity="standard_1005",
        channel_names=channels,
        channel_geometry_m=geometry,
        signal_volts=signal,
        annotations=tuple(annotations),
    )


def build_synthetic_feature_cohort(
    *, partition: str
) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[str]], int]:
    """Build deterministic compact feature rows for the frozen fit schedule."""

    if partition not in {"source", "fresh"}:
        raise UG1Refusal("synthetic feature partition must be source or fresh")
    np = _np()
    participants = SOURCE_PARTICIPANTS if partition == "source" else FRESH_PARTICIPANTS
    rows_by_task: dict[str, list[dict[str, Any]]] = {"execution": [], "imagery": []}
    targets_by_task: dict[str, list[str]] = {"execution": [], "imagery": []}
    input_bytes = 0
    dimensions = PREDICTIVE_FEATURE_DIMENSIONS
    templates = {}
    for task in ("execution", "imagery"):
        task_seed = int.from_bytes(
            hashlib.sha256(f"UG1|template|{task}".encode()).digest()[:8], "big"
        )
        rng = np.random.default_rng(task_seed)
        template = rng.normal(0.0, 1.0, size=320).astype("float64")
        template /= np.linalg.norm(template)
        templates[task] = template
    for task in ("execution", "imagery"):
        runs = TASK_RUNS[task][partition]
        for participant in participants:
            participant_number = int(participant[1:])
            for run in runs:
                previous_primary = None
                for event_ordinal in range(15):
                    label_index = (event_ordinal + int(run) + participant_number) % 2
                    target = "T1" if label_index == 0 else "T2"
                    sign = -1.0 if target == "T1" else 1.0
                    seed = int.from_bytes(
                        hashlib.sha256(
                            f"UG1|features|{participant}|{run}|{event_ordinal}".encode()
                        ).digest()[:8],
                        "big",
                    )
                    rng = np.random.default_rng(seed)
                    primary = sign * 6.0 * templates[task] + rng.normal(0.0, 0.08, size=320)
                    row = {
                        "opaque_row_id": _sha256_bytes(
                            f"UG1|row|{participant}|{run}|{event_ordinal}".encode()
                        )[:24],
                        "participant": participant,
                        "run": run,
                        "event_ordinal": event_ordinal,
                        "cue_sample": 480 + 720 * event_ordinal,
                        "primary_whole_head": primary.astype("float64"),
                        "fixed_channel_permutation": rng.normal(0.0, 0.2, size=320).astype(
                            "float64"
                        ),
                        "nonwrapping_event_displacement": (
                            np.zeros(320, dtype="float64")
                            if previous_primary is None
                            else previous_primary.copy()
                        ),
                        "pre_cue": rng.normal(0.0, 0.2, size=320).astype("float64"),
                        "early_cue": rng.normal(0.0, 0.2, size=320).astype("float64"),
                        "central_view": rng.normal(0.0, 0.2, size=90).astype("float64"),
                        "frontal_view": rng.normal(0.0, 0.2, size=40).astype("float64"),
                        "occipital_view": rng.normal(0.0, 0.2, size=40).astype("float64"),
                        "timing_only": np.asarray(
                            [event_ordinal / 14.0, (480 + 720 * event_ordinal) / 160.0, 4.5],
                            dtype="float64",
                        ),
                    }
                    if event_ordinal == 0:
                        row["timing_only"][2] = 0.0
                    previous_primary = primary
                    rows_by_task[task].append(row)
                    targets_by_task[task].append(target)
                    input_bytes += sum(int(np.asarray(row[name]).nbytes) for name in dimensions)
    validate_partition(rows_by_task, targets_by_task, partition=partition)
    return rows_by_task, targets_by_task, input_bytes


def _array_sha256(value: Any) -> str:
    np = _np()
    array = np.ascontiguousarray(np.asarray(value, dtype="float64"))
    return _sha256_bytes(array.tobytes(order="C"))


def _feature_partition_sha256(
    rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
) -> str:
    hasher = hashlib.sha256()
    for task in ("execution", "imagery"):
        for row in rows_by_task[task]:
            metadata = {
                key: row[key]
                for key in ("opaque_row_id", "participant", "run", "event_ordinal", "cue_sample")
            }
            hasher.update(_canonical_bytes(metadata))
            for name in sorted(PREDICTIVE_FEATURE_DIMENSIONS):
                hasher.update(name.encode("ascii"))
                hasher.update(_array_sha256(row[name]).encode("ascii"))
    return hasher.hexdigest()


def _target_partition_sha256(targets_by_task: Mapping[str, Sequence[str]]) -> str:
    return _sha256_bytes(
        _canonical_bytes({task: list(targets_by_task[task]) for task in ("execution", "imagery")})
    )


def run_signal_contract_cases() -> dict[str, Any]:
    """Exercise generated reader, causal, window, and firewall invariants."""

    np = _np()
    record = build_synthetic_run_record()
    source_before = _array_sha256(record.signal_volts)
    target_free, sealed = extract_run(record)
    replay_rows, replay_sealed = extract_run(record)
    if source_before != _array_sha256(record.signal_volts):
        raise UG1Refusal("generated source was mutated")
    feature_hash = _sha256_bytes(
        b"".join(
            np.ascontiguousarray(row["primary_whole_head"]).tobytes() for row in target_free["rows"]
        )
    )
    replay_hash = _sha256_bytes(
        b"".join(
            np.ascontiguousarray(row["primary_whole_head"]).tobytes() for row in replay_rows["rows"]
        )
    )
    if feature_hash != replay_hash or sealed != replay_sealed:
        raise UG1Refusal("generated reader replay changed")
    reordered_rows, reordered_sealed = extract_run(
        build_synthetic_run_record(reorder_annotations=True)
    )
    reordered_hash = _sha256_bytes(
        b"".join(
            np.ascontiguousarray(row["primary_whole_head"]).tobytes()
            for row in reordered_rows["rows"]
        )
    )
    if reordered_hash != feature_hash or reordered_sealed != sealed:
        raise UG1Refusal("annotation reordering changed canonical rows")
    referenced = common_average_reference(record.signal_volts)
    if not np.allclose(referenced.mean(axis=0), 0.0, rtol=0.0, atol=1e-18):
        raise UG1Refusal("common-average output is not channel centered")
    common_mode = np.linspace(-2e-6, 2e-6, referenced.shape[1], dtype="float64")
    shifted = common_average_reference(record.signal_volts + common_mode[None, :])
    if not np.allclose(referenced, shifted, rtol=0.0, atol=1e-18):
        raise UG1Refusal("common-mode signal changed common-average output")
    full = causal_filter(referenced)
    chunked = causal_filter(referenced, chunk_sizes=(997, 1111, referenced.shape[1] - 2108))
    if not np.allclose(full, chunked, rtol=0.0, atol=1e-12):
        raise UG1Refusal("full and chunked causal filtering differ")
    impulse = referenced.copy()
    impulse_at = referenced.shape[1] - 100
    impulse[:, impulse_at] += 1.0
    changed = causal_filter(impulse)
    if not np.array_equal(full[:, :impulse_at], changed[:, :impulse_at]):
        raise UG1Refusal("future impulse changed an earlier causal output")
    second = causal_filter(referenced)
    if not np.array_equal(full, second):
        raise UG1Refusal("per-run zero-state reset changed")
    try:
        causal_filter(referenced, implementation="sosfiltfilt")
    except UG1Refusal:
        pass
    else:
        raise UG1Refusal("acausal filter was accepted")
    if any("target" in row or "label" in row for row in target_free["rows"]):
        raise UG1Refusal("target firewall changed")
    channel_contract = load_amendment()["channel_contract"]
    central = np.asarray(_channel_indices(record.channel_names, channel_contract["central_view"]))
    frontal = np.asarray(_channel_indices(record.channel_names, channel_contract["frontal_view"]))
    occipital = np.asarray(
        _channel_indices(record.channel_names, channel_contract["occipital_view"])
    )
    permutation = np.asarray(
        load_amendment()["control_contract"]["channel_permutation_indices"], dtype="int64"
    )

    def reference_window(values: Any, start: int, stop: int) -> Any:
        epoch = np.asarray(values[:, start:stop], dtype="float64")
        means = epoch.reshape(epoch.shape[0], 4, epoch.shape[1] // 4).mean(axis=2)
        axis = np.linspace(-1.0, 1.0, epoch.shape[1], dtype="float64")
        slopes = (epoch @ axis) / float(axis @ axis)
        return np.concatenate((means, slopes[:, None]), axis=1).reshape(-1)

    canonical_annotations = canonicalize_annotations(
        record.annotations,
        sample_count=record.signal_volts.shape[1],
    )
    previous_cue = None
    for index, (row, annotation) in enumerate(
        zip(target_free["rows"], canonical_annotations, strict=True)
    ):
        cue = int(annotation["cue_sample"])
        expected = {
            "primary_whole_head": reference_window(full, cue + 160, cue + 480),
            "fixed_channel_permutation": reference_window(full[permutation], cue + 160, cue + 480),
            "pre_cue": reference_window(full, cue - 320, cue),
            "early_cue": reference_window(full, cue, cue + 160),
            "central_view": reference_window(full[central], cue + 160, cue + 480),
            "frontal_view": reference_window(full[frontal], cue + 160, cue + 480),
            "occipital_view": reference_window(full[occipital], cue + 160, cue + 480),
            "timing_only": np.asarray(
                [
                    index / 14.0,
                    cue / 160.0,
                    0.0 if previous_cue is None else (cue - previous_cue) / 160.0,
                ],
                dtype="float64",
            ),
        }
        for name, expected_values in expected.items():
            if not np.array_equal(row[name], expected_values):
                raise UG1Refusal(f"literal window or view changed: {name}")
        expected_displaced = (
            np.zeros(320, dtype="float64")
            if index == 0
            else target_free["rows"][index - 1]["primary_whole_head"]
        )
        if not np.array_equal(row["nonwrapping_event_displacement"], expected_displaced):
            raise UG1Refusal("literal nonwrapping displacement changed")
        previous_cue = cue
    probe_targets = ["T1" if index % 2 == 0 else "T2" for index in range(15)]
    expected_derangement = [
        probe_targets[index]
        for index in load_amendment()["control_contract"]["source_label_derangement_indices"]
    ]
    if derange_target_group(probe_targets) != expected_derangement:
        raise UG1Refusal("literal source-label derangement changed")
    swapped = {
        "targets": [
            {**row, "target": "T2" if row["target"] == "T1" else "T1"} for row in sealed["targets"]
        ]
    }
    swapped_feature_hash = _sha256_bytes(
        b"".join(
            np.ascontiguousarray(row["primary_whole_head"]).tobytes() for row in target_free["rows"]
        )
    )
    if swapped_feature_hash != feature_hash:
        raise UG1Refusal("target swap changed predictive rows")
    if swapped == sealed:
        raise UG1Refusal("target-swap qualification fixture did not change")
    malformed = list(record.annotations)
    refusals = 0
    for candidate in (
        malformed[:-1],
        malformed + [malformed[-1]],
        [*malformed, Annotation(90.0, "T3")],
    ):
        try:
            canonicalize_annotations(candidate, sample_count=record.signal_volts.shape[1])
        except UG1Refusal:
            refusals += 1
    if refusals != 3:
        raise UG1Refusal("annotation refusal matrix changed")
    try:
        extract_run(replace(record, montage_identity="unknown"))
    except UG1Refusal:
        refusals += 1
    else:
        raise UG1Refusal("montage identity drift was accepted")
    return {
        "generated_signal_bytes": int(
            record.signal_volts.nbytes + record.channel_geometry_m.nbytes
        ),
        "reader_rows": len(target_free["rows"]),
        "feature_hash": feature_hash,
        "refusal_cases": refusals,
        "annotation_refusal_cases": 3,
        "montage_refusal_cases": 1,
        "window_view_assertions": len(target_free["rows"]) * 8,
        "displacement_assertions": len(target_free["rows"]),
        "car_assertions": 2,
        "case_classes": [
            "valid_replay_source_immutability",
            "target_swap_and_canary_invariance",
            "future_impulse_causality",
            "chunk_replay",
            "run_reset",
            "acausal_filter_refusal",
            "literal_channel_permutation",
            "literal_event_displacement",
            "literal_label_derangement",
            "exact_windows_views_and_CAR_order",
            "annotation_missing_duplicate_extra_reorder_handling",
        ],
    }


def _sealed_target_rows(
    rows_by_task: Mapping[str, Sequence[Mapping[str, Any]]],
    targets_by_task: Mapping[str, Sequence[str]],
) -> list[dict[str, Any]]:
    rows = []
    for task in ("execution", "imagery"):
        if len(rows_by_task[task]) != len(targets_by_task[task]):
            raise UG1Refusal("sealed target rows differ from target-free identities")
        for source, target in zip(rows_by_task[task], targets_by_task[task], strict=True):
            rows.append(
                {
                    "schema_version": SCHEMA_VERSION,
                    "opaque_row_id": source["opaque_row_id"],
                    "task": task,
                    "participant": source["participant"],
                    "run": int(source["run"]),
                    "event_ordinal": int(source["event_ordinal"]),
                    "cue_sample": int(source["cue_sample"]),
                    "target": target,
                }
            )
    rows.sort(key=lambda row: (row["task"], row["participant"], row["run"], row["event_ordinal"]))
    return rows


def _directory_bytes(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for candidate in path.rglob("*"):
        if candidate.is_file() and not candidate.is_symlink():
            total += candidate.stat().st_size
    return total


def _assert_resource_limits(
    *,
    started: float,
    peak_rss_bytes: int,
    output_bytes: int,
    incremental_output_bytes: int = 0,
    wall_cap_seconds: float = 900.0,
    rss_cap_bytes: int = 1_073_741_824,
    output_cap_bytes: int = 2_097_152,
    incremental_output_cap_bytes: int = 536_870_912,
    private_derivative_cap_bytes: int = 134_217_728,
) -> None:
    if time.monotonic() - started > wall_cap_seconds:
        raise UG1Refusal("Stage G wall-time cap exceeded")
    if peak_rss_bytes > rss_cap_bytes:
        raise UG1Refusal("Stage G process-tree RSS cap exceeded")
    if output_bytes > output_cap_bytes:
        raise UG1Refusal("Stage G public output cap exceeded")
    if incremental_output_bytes > incremental_output_cap_bytes:
        raise UG1Refusal("Stage G incremental output cap exceeded")
    if incremental_output_bytes > private_derivative_cap_bytes:
        raise UG1Refusal("Stage G private derivative cap exceeded")


def _assert_minimum_free_disk(
    path: Path,
    *,
    minimum_bytes: int = 2_147_483_648,
    observed_free_bytes: int | None = None,
) -> int:
    free_bytes = (
        shutil.disk_usage(path).free if observed_free_bytes is None else observed_free_bytes
    )
    if type(free_bytes) is not int or free_bytes < minimum_bytes:
        raise UG1Refusal("Stage G minimum free-disk gate failed")
    return free_bytes


def _checkpoint_hash_inventory(manifest: Mapping[str, Any]) -> dict[str, str]:
    inventory = {"manifest": str(manifest["manifest_hash"])}
    for member in manifest["members"]:
        inventory[str(member["path"])] = str(member["sha256"])
    return dict(sorted(inventory.items()))


def run_generated_qualification(output_path: str | Path) -> dict[str, Any]:
    """Run the sole bounded Stage G qualification and emit one aggregate report."""

    from neurodecodekit.datasets import eegmmidb_unseen_participant_acquisition as acquisition
    from neurodecodekit.evaluation import eegmmidb_unseen_participant_score as scorer

    output_path = _prepare_output_path(output_path)
    started = time.monotonic()
    assert_single_thread_environment()
    versions = assert_exact_versions()
    initial_free_disk_bytes = _assert_minimum_free_disk(output_path.parent)
    if output_path.exists() or output_path.is_symlink():
        raise UG1Refusal("Stage G destination already exists; repeat is forbidden")
    work_root = Path(tempfile.mkdtemp(prefix="neurodecodekit-ug1-stage-g-", dir=output_path.parent))
    peak_incremental_output = 0
    target_deliveries = 0
    scoring_events = 0
    try:
        signal_cases = run_signal_contract_cases()
        acquisition_cases = acquisition.run_generated_qualification_cases()
        source_rows, source_targets, source_input_bytes = build_synthetic_feature_cohort(
            partition="source"
        )
        fresh_rows, fresh_targets, fresh_input_bytes = build_synthetic_feature_cohort(
            partition="fresh"
        )
        source_payload_identities = [f"source-generated-{index:02d}" for index in range(60)]
        fresh_payload_identities = [f"fresh-generated-{index:02d}" for index in range(30)]
        validate_source_fresh_isolation(
            source_rows,
            fresh_rows,
            source_payload_identities=source_payload_identities,
            fresh_payload_identities=fresh_payload_identities,
        )
        overlap_refusals = 0
        overlapping_fresh = {task: [dict(row) for row in rows] for task, rows in fresh_rows.items()}
        overlapping_fresh["execution"][0]["opaque_row_id"] = source_rows["execution"][0][
            "opaque_row_id"
        ]
        for candidate_rows, candidate_payloads in (
            (overlapping_fresh, fresh_payload_identities),
            (fresh_rows, [source_payload_identities[0], *fresh_payload_identities[1:]]),
        ):
            try:
                validate_source_fresh_isolation(
                    source_rows,
                    candidate_rows,
                    source_payload_identities=source_payload_identities,
                    fresh_payload_identities=candidate_payloads,
                )
            except UG1Refusal:
                overlap_refusals += 1
        if overlap_refusals != 2:
            raise UG1Refusal("joint source/fresh isolation refusal matrix changed")
        source_snapshot = _feature_partition_sha256(source_rows)
        source_target_snapshot = _target_partition_sha256(source_targets)
        models, source_report = run_source_loso_and_fit(source_rows, source_targets)
        if source_report["route"] != "EEGMMIDBUG1-SOURCE-PASS":
            raise UG1Refusal("generated source pass fixture did not pass the source gate")
        if source_snapshot != _feature_partition_sha256(source_rows):
            raise UG1Refusal("synthetic source feature rows were mutated")
        if source_target_snapshot != _target_partition_sha256(source_targets):
            raise UG1Refusal("synthetic source targets were mutated")
        code_hash = _sha256_bytes(
            Path(__file__).read_bytes()
            + Path(scorer.__file__).read_bytes()
            + Path(acquisition.__file__).read_bytes()
        )
        configuration_hash = _sha256_bytes(
            CONTRACT_SHA256.encode() + AMENDMENT_SHA256.encode() + "|".join(CONDITIONS).encode()
        )
        source_payload_hashes = {
            "generated_feature_cohort": source_snapshot,
            "generated_source_targets": source_target_snapshot,
        }
        checkpoint_path = work_root / "checkpoint"
        checkpoint_manifest = save_checkpoint(
            models,
            checkpoint_path,
            source_payload_hashes=source_payload_hashes,
            code_hash=code_hash,
            configuration_hash=configuration_hash,
            package_versions=versions,
        )
        loaded_models, replay_manifest = load_checkpoint(
            checkpoint_path,
            expected_code_hash=code_hash,
            expected_configuration_hash=configuration_hash,
            expected_source_payload_hashes=source_payload_hashes,
            expected_package_versions=versions,
        )
        if replay_manifest != checkpoint_manifest:
            raise UG1Refusal("checkpoint replay changed")
        checkpoint_inventory_before = _checkpoint_hash_inventory(checkpoint_manifest)
        peak_incremental_output = max(peak_incremental_output, _directory_bytes(work_root))
        predictions, fresh_prediction_sets = predict_fresh_rows(loaded_models, fresh_rows)
        original_traces: dict[str, dict[str, Any]] = {}
        for task in ("execution", "imagery"):
            value_lookup = {
                (str(row["opaque_row_id"]), str(row["condition"])): str(row["prediction"])
                for row in predictions
                if row["task"] == task
            }
            original_values = {
                condition: [
                    value_lookup[(str(row["opaque_row_id"]), condition)] for row in fresh_rows[task]
                ]
                for condition in CONDITIONS
            }
            original_traces[task] = _prediction_trace(original_values)
        relabeled_rows = {
            task: [{**row, "participant": f"opaque-{index:02d}"} for index, row in enumerate(rows)]
            for task, rows in fresh_rows.items()
        }
        predictive_view_hashes: dict[str, str] = {}
        for task in ("execution", "imagery"):
            original_view = _predictive_feature_rows(fresh_rows[task])
            relabeled_view = _predictive_feature_rows(relabeled_rows[task])
            original_view_hash = _sha256_bytes(
                b"".join(
                    _array_sha256(row[name]).encode()
                    for row in original_view
                    for name in sorted(PREDICTIVE_FEATURE_DIMENSIONS)
                )
            )
            relabeled_view_hash = _sha256_bytes(
                b"".join(
                    _array_sha256(row[name]).encode()
                    for row in relabeled_view
                    for name in sorted(PREDICTIVE_FEATURE_DIMENSIONS)
                )
            )
            if original_view_hash != relabeled_view_hash:
                raise UG1Refusal("participant relabel changed predictive input bytes")
            predictive_view_hashes[task] = original_view_hash
            relabeled_trace = _prediction_trace(
                _predict_task_values(loaded_models[task], relabeled_view)
            )
            if relabeled_trace != original_traces[task]:
                raise UG1Refusal("participant relabel changed predictive trace")
            target_bearing_rows = [dict(row) for row in fresh_rows[task]]
            target_bearing_rows[0]["target"] = "T2"
            try:
                _predictive_feature_rows(target_bearing_rows)
            except UG1Refusal:
                pass
            else:
                raise UG1Refusal("target-bearing predictive canary was accepted")
        if _checkpoint_hash_inventory(replay_manifest) != checkpoint_inventory_before:
            raise UG1Refusal("participant relabel changed checkpoint parameters")
        prediction_payload = scorer.canonical_prediction_jsonl(predictions)
        sealed_rows = _sealed_target_rows(fresh_rows, fresh_targets)
        target_payload = scorer.canonical_target_jsonl(sealed_rows)
        target_hash = _sha256_bytes(target_payload)
        bindings = scorer.FreezeBindings(
            checkpoint_hashes=_checkpoint_hash_inventory(checkpoint_manifest),
            configuration_hash=configuration_hash,
            code_hash=code_hash,
            sealed_target_payload_sha256=target_hash,
        )
        freeze = scorer.build_prediction_freeze(prediction_payload, bindings=bindings)
        scorer.validate_prediction_freeze(freeze, prediction_payload, bindings=bindings)
        target_swap_payload = scorer.canonical_target_jsonl(
            [{**row, "target": "T2" if row["target"] == "T1" else "T1"} for row in sealed_rows]
        )
        if target_swap_payload == target_payload:
            raise UG1Refusal("target swap did not change the sealed generated fixture")
        for task in ("execution", "imagery"):
            swapped_view = _predictive_feature_rows([dict(row) for row in fresh_rows[task]])
            swapped_view_hash = _sha256_bytes(
                b"".join(
                    _array_sha256(row[name]).encode()
                    for row in swapped_view
                    for name in sorted(PREDICTIVE_FEATURE_DIMENSIONS)
                )
            )
            if swapped_view_hash != predictive_view_hashes[task]:
                raise UG1Refusal("target swap changed target-blind predictive input bytes")
            swapped_trace = _prediction_trace(
                _predict_task_values(loaded_models[task], swapped_view)
            )
            if swapped_trace != original_traces[task]:
                raise UG1Refusal("target swap changed target-blind predictive trace")
        if _checkpoint_hash_inventory(replay_manifest) != checkpoint_inventory_before:
            raise UG1Refusal("target swap changed checkpoint parameters")
        if scorer.build_prediction_freeze(prediction_payload, bindings=bindings) != freeze:
            raise UG1Refusal("target-blind prediction freeze did not replay")
        mutation_refusals = 0
        mutated_prediction = bytearray(prediction_payload)
        mutated_prediction[-10] = ord("x")
        try:
            scorer.validate_prediction_freeze(freeze, bytes(mutated_prediction), bindings=bindings)
        except scorer.UG1ScoreRefusal:
            mutation_refusals += 1
        mutated_freeze = dict(freeze)
        mutated_freeze["code_hash"] = "0" * 64
        try:
            scorer.validate_prediction_freeze(mutated_freeze, prediction_payload, bindings=bindings)
        except scorer.UG1ScoreRefusal:
            mutation_refusals += 1
        mutated_configuration = dict(freeze)
        mutated_configuration["configuration_hash"] = "0" * 64
        try:
            scorer.validate_prediction_freeze(
                mutated_configuration, prediction_payload, bindings=bindings
            )
        except scorer.UG1ScoreRefusal:
            mutation_refusals += 1
        lines = prediction_payload.splitlines(keepends=True)
        try:
            scorer.build_prediction_freeze(
                b"".join((lines[1], lines[0], *lines[2:])), bindings=bindings
            )
        except scorer.UG1ScoreRefusal:
            mutation_refusals += 1
        mutated_checkpoint = work_root / "mutated-checkpoint"
        shutil.copytree(checkpoint_path, mutated_checkpoint)
        checkpoint_member = next(mutated_checkpoint.glob("*.mean.npy"))
        checkpoint_member.write_bytes(checkpoint_member.read_bytes() + b"x")
        try:
            load_checkpoint(
                mutated_checkpoint,
                expected_code_hash=code_hash,
                expected_configuration_hash=configuration_hash,
                expected_source_payload_hashes=source_payload_hashes,
                expected_package_versions=versions,
            )
        except UG1Refusal:
            mutation_refusals += 1
        noncanonical_checkpoint = work_root / "noncanonical-checkpoint"
        shutil.copytree(checkpoint_path, noncanonical_checkpoint)
        noncanonical_manifest = noncanonical_checkpoint / "manifest.json"
        noncanonical_manifest.write_bytes(
            noncanonical_manifest.read_bytes().replace(b"{", b"{ ", 1)
        )
        try:
            load_checkpoint(
                noncanonical_checkpoint,
                expected_code_hash=code_hash,
                expected_configuration_hash=configuration_hash,
                expected_source_payload_hashes=source_payload_hashes,
                expected_package_versions=versions,
            )
        except UG1Refusal:
            mutation_refusals += 1
        target_loads = 0

        def verify_checkpoint(path: Path = checkpoint_path) -> dict[str, str]:
            _models, verified_manifest = load_checkpoint(
                path,
                expected_code_hash=code_hash,
                expected_configuration_hash=configuration_hash,
                expected_source_payload_hashes=source_payload_hashes,
                expected_package_versions=versions,
            )
            return _checkpoint_hash_inventory(verified_manifest)

        checkpoint_target_loads = 0

        def forbidden_checkpoint_target_load() -> bytes:
            nonlocal checkpoint_target_loads
            checkpoint_target_loads += 1
            return target_payload

        try:
            scorer.score_frozen_predictions(
                freeze=freeze,
                prediction_payload=prediction_payload,
                bindings=bindings,
                checkpoint_verifier=lambda: verify_checkpoint(mutated_checkpoint),
                sealed_target_loader=forbidden_checkpoint_target_load,
                source_loso_execution_passed=True,
            )
        except scorer.UG1ScoreRefusal:
            mutation_refusals += 1
        if checkpoint_target_loads != 0:
            raise UG1Refusal("target opened before mutated checkpoint refusal")
        if mutation_refusals != 7:
            raise UG1Refusal("freeze mutation refusal matrix changed")

        def load_targets_once() -> bytes:
            nonlocal target_loads, target_deliveries
            target_loads += 1
            target_deliveries += 1
            if target_loads != 1:
                raise UG1Refusal("generated target loader called more than once")
            return target_payload

        score = scorer.score_frozen_predictions(
            freeze=freeze,
            prediction_payload=prediction_payload,
            bindings=bindings,
            checkpoint_verifier=verify_checkpoint,
            sealed_target_loader=load_targets_once,
            source_loso_execution_passed=True,
        )
        scoring_events = int(score["scoring_events"])
        if score["route"] not in {"EEGMMIDBUG1-R2", "EEGMMIDBUG1-R3", "EEGMMIDBUG1-R4"}:
            raise UG1Refusal("generated scorer did not reach a final router branch")
        if scorer.exact_sign_flip_p([0.0] * 15) != 1.0:
            raise UG1Refusal("exact sign-flip tie handling changed")
        threshold_cases = scorer.qualify_gate_threshold_boundaries()
        if threshold_cases != {"inclusive_pass_cases": 2, "exclusive_fail_cases": 22}:
            raise UG1Refusal("gate threshold boundary qualification changed")
        expected_routes = (
            "EEGMMIDBUG1-R0",
            "EEGMMIDBUG1-R1",
            "EEGMMIDBUG1-R2",
            "EEGMMIDBUG1-R3",
            "EEGMMIDBUG1-R4",
        )
        observed_routes = (
            scorer.route_ug1(
                integrity_passed=False,
                source_loso_execution_passed=True,
                final_score_available=True,
                execution_passed=True,
                imagery_passed=True,
            ),
            scorer.route_ug1(
                integrity_passed=True,
                source_loso_execution_passed=False,
                final_score_available=True,
                execution_passed=True,
                imagery_passed=True,
            ),
            scorer.route_ug1(
                integrity_passed=True,
                source_loso_execution_passed=True,
                final_score_available=True,
                execution_passed=False,
                imagery_passed=True,
            ),
            scorer.route_ug1(
                integrity_passed=True,
                source_loso_execution_passed=True,
                final_score_available=True,
                execution_passed=True,
                imagery_passed=False,
            ),
            scorer.route_ug1(
                integrity_passed=True,
                source_loso_execution_passed=True,
                final_score_available=True,
                execution_passed=True,
                imagery_passed=True,
            ),
        )
        if observed_routes != expected_routes:
            raise UG1Refusal("router boundary qualification changed")
        crash_path = work_root / "crash.json"
        try:
            _atomic_write_bytes(crash_path, b"{}\n", _fail_before_rename=True)
        except UG1Refusal:
            pass
        else:
            raise UG1Refusal("atomic crash injection did not refuse")
        if crash_path.exists() or list(work_root.glob(".crash.json.*")):
            raise UG1Refusal("atomic crash left generated debris")
        existing = work_root / "existing.json"
        _atomic_write_bytes(existing, b"{}\n")
        try:
            _atomic_write_bytes(existing, b"{}\n")
        except UG1Refusal:
            pass
        else:
            raise UG1Refusal("pre-existing destination was overwritten")
        race = work_root / "race.json"

        def create_race_destination() -> None:
            race.write_bytes(b"race-owned\n")

        try:
            _atomic_write_bytes(race, b"{}\n", _before_rename=create_race_destination)
        except UG1Refusal:
            pass
        else:
            raise UG1Refusal("atomic destination race was overwritten")
        if race.read_bytes() != b"race-owned\n" or list(work_root.glob(".race.json.*")):
            raise UG1Refusal("atomic destination race handling changed")
        race.unlink()
        path_refusals = 0
        for candidate in (
            Path("..") / "ug1-traversal.json",
            output_path.parent / "DATA" / "ug1-protected.json",
        ):
            try:
                _prepare_output_path(candidate)
            except UG1Refusal:
                path_refusals += 1
        if path_refusals != 2:
            raise UG1Refusal("public output path refusal matrix changed")
        for kwargs in (
            {"wall_cap_seconds": -1.0},
            {"rss_cap_bytes": 1},
            {"output_cap_bytes": 1},
            {"incremental_output_cap_bytes": 1},
        ):
            try:
                _assert_resource_limits(
                    started=started,
                    peak_rss_bytes=max(2, peak_process_tree_rss_bytes()),
                    output_bytes=2,
                    incremental_output_bytes=2,
                    **kwargs,
                )
            except UG1Refusal:
                pass
            else:
                raise UG1Refusal("resource refusal matrix changed")
        try:
            _assert_minimum_free_disk(output_path.parent, observed_free_bytes=1)
        except UG1Refusal:
            pass
        else:
            raise UG1Refusal("free-disk refusal qualification changed")
        peak_incremental_output = max(
            peak_incremental_output,
            _directory_bytes(work_root) + len(prediction_payload) + len(target_payload),
        )
        case_classes = sorted(
            set(signal_cases["case_classes"])
            | set(acquisition_cases["case_classes"])
            | {
                "participant_relabel_invariance",
                "execution_and_imagery_exact_counts",
                "checkpoint_configuration_prediction_row_order_and_freeze_mutation_refusal",
                "sign_flip_ties_and_router_thresholds",
                "atomic_crash_destination_traversal_redirect_output_RSS_wall_and_second_invocation_refusal",
            }
        )
        required_cases = set(load_amendment()["stage_G_qualification"]["required_case_classes"])
        if set(case_classes) != required_cases:
            missing = sorted(required_cases - set(case_classes))
            extra = sorted(set(case_classes) - required_cases)
            raise UG1Refusal(f"Stage G case inventory changed: missing={missing}, extra={extra}")
        case_evidence = {
            "valid_replay_source_immutability": {
                "feature_sha256": signal_cases["feature_hash"],
                "replays": 1,
                "source_mutations": 0,
            },
            "target_swap_and_canary_invariance": {
                "tasks_checked": 2,
                "target_bearing_predictor_refusals": 2,
                "checkpoint_mutations": 0,
            },
            "participant_relabel_invariance": {
                "tasks_checked": 2,
                "checkpoint_mutations": 0,
            },
            "split_overlap_alias_symlink_hardlink_duplicate_forbidden_run_refusal": {
                "joint_overlap_alias_refusals": overlap_refusals,
                "acquisition_refusals": acquisition_cases["refusal_cases"],
            },
            "future_impulse_causality": {"cases": 1},
            "chunk_replay": {"cases": 1},
            "run_reset": {"cases": 1},
            "acausal_filter_refusal": {"cases": 1},
            "literal_channel_permutation": {"cases": 15},
            "literal_event_displacement": {"cases": signal_cases["displacement_assertions"]},
            "literal_label_derangement": {"cases": 1},
            "exact_windows_views_and_CAR_order": {
                "window_view_assertions": signal_cases["window_view_assertions"],
                "car_assertions": signal_cases["car_assertions"],
            },
            "annotation_missing_duplicate_extra_reorder_handling": {
                "refusals": signal_cases["annotation_refusal_cases"],
                "canonical_reorders": 1,
            },
            "execution_and_imagery_exact_counts": {
                "source_rows": 900,
                "fresh_rows": 450,
                "prediction_rows": len(predictions),
            },
            "checkpoint_configuration_prediction_row_order_and_freeze_mutation_refusal": {
                "mutation_refusals": mutation_refusals,
                "checkpoint_members": len(checkpoint_manifest["members"]),
            },
            "sign_flip_ties_and_router_thresholds": {
                "router_routes": len(observed_routes),
                **threshold_cases,
            },
            "atomic_crash_destination_traversal_redirect_output_RSS_wall_and_second_invocation_refusal": {
                "resource_refusals": 5,
                "atomic_refusals": 3,
                "path_refusals": path_refusals,
                "acquisition_refusals": acquisition_cases["refusal_cases"],
            },
        }
        if set(case_evidence) != required_cases:
            raise UG1Refusal("Stage G case evidence inventory changed")
        runtime = time.monotonic() - started
        peak_rss = peak_process_tree_rss_bytes()
        summary = {
            "schema_name": "neurodecodekit.eegmmidb_unseen_participant_stage_g_result",
            "schema_version": SCHEMA_VERSION,
            "lane_id": LANE_ID,
            "status": "passed_generated_mocked_qualification_only",
            "qualification_invocations": 1,
            "case_classes": case_classes,
            "case_classes_passed": len(case_classes),
            "case_evidence": case_evidence,
            "input_bytes": signal_cases["generated_signal_bytes"]
            + source_input_bytes
            + fresh_input_bytes
            + acquisition_cases["input_bytes"],
            "output_bytes": 0,
            "peak_incremental_output_bytes": peak_incremental_output,
            "runtime_seconds": round(runtime, 6),
            "peak_process_tree_RSS_bytes": peak_rss,
            "initial_free_disk_bytes": initial_free_disk_bytes,
            "parameter_update_fits": source_report["fit_count"],
            "prediction_sets": source_report["prediction_set_count"] + fresh_prediction_sets,
            "training_runs": source_report["fit_count"],
            "model_inference_runs": 111,
            "qualification_replay_model_inference_runs": 44,
            "model_runs": source_report["fit_count"] + 111,
            "real_path_reads": 0,
            "real_cache_reads": 0,
            "raw_data_reads": 0,
            "real_EDF_semantic_parses": 0,
            "network_bytes": 0,
            "new_payload_bytes": 0,
            "target_deliveries": target_deliveries,
            "real_target_deliveries": 0,
            "scoring_events": scoring_events,
            "synthetic_router_route": score["route"],
            "producer_is_causal": True,
            "end_to_end_latency_measured": False,
            "post_publication_resource_check_required": True,
            "runtime_measurement_cutoff": "immediately_before_atomic_publication",
            "warnings": [
                "generated_fixture_is_interface_qualification_not_scientific_evidence",
                "synthetic_router_route_has_no_claim_value",
                "no_real_EEG_or_retained_payload_was_opened",
                "no_unseen_participant_decoding_result_is_established",
                "visual_cue_and_ocular_compatibility_remain",
                "end_to_end_latency_was_not_measured",
            ],
            "claim_boundary": load_amendment()["claim_boundary"],
        }
        private_bytes_before_publication = _directory_bytes(work_root)
        for _ in range(8):
            payload = _canonical_bytes(summary)
            cumulative_peak = max(
                peak_incremental_output,
                private_bytes_before_publication + 2 * len(payload),
            )
            if (
                summary["output_bytes"] == len(payload)
                and summary["peak_incremental_output_bytes"] == cumulative_peak
            ):
                break
            summary["output_bytes"] = len(payload)
            summary["peak_incremental_output_bytes"] = cumulative_peak
        else:
            raise UG1Refusal("Stage G output-byte measurement did not converge")
        payload = _canonical_bytes(summary)
        _assert_resource_limits(
            started=started,
            peak_rss_bytes=peak_rss,
            output_bytes=len(payload),
            incremental_output_bytes=summary["peak_incremental_output_bytes"],
        )
        _atomic_write_bytes(output_path, payload)
        published = _regular_no_follow(output_path)
        if published.st_size != summary["output_bytes"]:
            raise UG1Refusal("Stage G output byte measurement changed after write")
        _assert_resource_limits(
            started=started,
            peak_rss_bytes=peak_process_tree_rss_bytes(),
            output_bytes=published.st_size,
            incremental_output_bytes=summary["peak_incremental_output_bytes"],
        )
        return summary
    finally:
        shutil.rmtree(work_root, ignore_errors=True)
