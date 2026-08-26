"""Generated qualification and frozen compact model core for DREYER-C5R-1."""

from __future__ import annotations

import hashlib
import json
import math
import os
import resource
import stat
import time
import warnings
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from neurodecodekit.datasets.dreyer_c5r_1 import (
    DreyerDataRefusal,
    build_generated_edf_header,
    log_relative_band_features,
    parse_edf_fixed_header,
)
from neurodecodekit.evaluation import dreyer_c5r_1_score as scorer


LANE_ID = "DREYER-C5R-1"
CONTRACT_RELATIVE_PATH = Path("registries/dreyer_c5r_1_contract.v0.json")
CONTRACT_SHA256 = "ea6357a7b079aa3de885ef0a7c0e391c7810e2b94cbbb1702f934f65cc6b8fed"
REGISTERED_RESULT_RELATIVE_PATH = Path(
    "registries/dreyer_c5r_1_generated_qualification_result.v0.json"
)
CALIBRATED_CONDITIONS = (
    "late_N",
    "late_N_plus_R",
    "late_N_plus_deranged_R",
    "late_N_without_posterior",
    "late_N_without_posterior_plus_R",
    "pre_N",
    "pre_N_plus_R",
    "cue_N",
    "cue_N_plus_R",
)
UNCALIBRATED_FITTED_CONDITIONS = (
    "timing_only",
    "EOG_only",
    "EMG_only",
    "posterior_only",
    "late_central_E",
    "late_residual_R",
    "source_label_rotated_late_N_plus_R",
)
WINDOWS = ("late", "pre", "cue")
FEATURE_DIMENSIONS = {
    "E": 27,
    "EOG": 9,
    "EMG": 6,
    "posterior": 9,
    "frontal": 9,
    "timing": 4,
}
THREAD_ENVIRONMENT = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)
GENERATED_QUALIFICATION_CAPS = {
    "runtime_seconds_maximum": 180,
    "peak_process_tree_RSS_bytes_maximum": 805_306_368,
    "generated_input_bytes_maximum": 33_554_432,
    "private_temporary_bytes_maximum": 33_554_432,
    "public_output_bytes_maximum": 1_048_576,
}


class DreyerExperimentRefusal(RuntimeError):
    """Fail-closed DREYER-C5R-1 experiment refusal."""


@dataclass
class OperationLedger:
    parameter_update_fits: int = 0
    model_inference_runs: int = 0
    held_out_prediction_sets: int = 0
    held_out_target_deliveries: int = 0
    scores: int = 0
    post_target_updates: int = 0


@dataclass(frozen=True)
class FrozenBinaryLogistic:
    mean: Any
    scale: Any
    coefficient: Any
    intercept: float


@dataclass(frozen=True)
class FrozenMultiRidge:
    input_mean: Any
    input_scale: Any
    output_mean: Any
    output_scale: Any
    coefficient: Any
    intercept: Any


@dataclass(frozen=True)
class FoldCapability:
    held_out_participant: str
    source_rows: tuple[dict[str, Any], ...]
    source_targets: Mapping[str, int]
    held_out_rows: tuple[dict[str, Any], ...]
    inner_folds: int


class SealedTargetVault:
    """Generated stand-in for a target vault unavailable to the prediction path."""

    def __init__(self, targets: Mapping[str, int]) -> None:
        self.__targets = dict(targets)
        self.deliveries = 0

    def deliver(self, *, prediction_freeze_green: bool) -> dict[str, int]:
        if not prediction_freeze_green:
            raise DreyerExperimentRefusal("held-out targets remain sealed before green freeze")
        if self.deliveries != 0:
            raise DreyerExperimentRefusal("held-out targets may be delivered exactly once")
        self.deliveries = 1
        return dict(self.__targets)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _canonical_bytes(value: Any) -> bytes:
    return scorer.canonical_bytes(value)


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _np() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "DREYER-C5R-1 arrays require: pip install -e '.[classical]'"
        ) from exc
    return np


def _sklearn_classes() -> tuple[Any, Any]:
    try:
        from sklearn.linear_model import LogisticRegression, Ridge
    except ImportError as exc:
        raise RuntimeError(
            "DREYER-C5R-1 compact models require: pip install -e '.[classical]'"
        ) from exc
    return LogisticRegression, Ridge


def load_contract(root: str | Path | None = None) -> dict[str, Any]:
    repository = Path(root) if root is not None else _repo_root()
    payload = (repository / CONTRACT_RELATIVE_PATH).read_bytes()
    if _sha256(payload) != CONTRACT_SHA256:
        raise DreyerExperimentRefusal("DREYER-C5R-1 contract hash changed")
    value = json.loads(payload)
    if not isinstance(value, dict) or value.get("lane_id") != LANE_ID:
        raise DreyerExperimentRefusal("DREYER-C5R-1 contract identity changed")
    if tuple(value.get("conditions", ())) != scorer.CONDITIONS:
        raise DreyerExperimentRefusal("DREYER-C5R-1 condition inventory changed")
    schedule = value.get("schedule")
    if not isinstance(schedule, dict):
        raise DreyerExperimentRefusal("DREYER-C5R-1 schedule is missing")
    expected = {
        "outer_folds": 60,
        "conditions_per_fold": 17,
        "parameter_update_fits": 4740,
        "held_out_prediction_sets": 1020,
        "held_out_prediction_rows": 81600,
    }
    if any(schedule.get(key) != value for key, value in expected.items()):
        raise DreyerExperimentRefusal("DREYER-C5R-1 schedule changed")
    return value


def assert_single_thread_environment() -> None:
    changed = {
        name: os.environ.get(name)
        for name in THREAD_ENVIRONMENT
        if os.environ.get(name) != "1"
    }
    if changed:
        raise DreyerExperimentRefusal(f"one-thread environment differs: {sorted(changed)}")


def peak_process_tree_rss_bytes() -> int:
    own = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    children = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    factor = 1 if os.uname().sysname == "Darwin" else 1024
    return int((own + children) * factor)


def _regular_no_follow(path: Path) -> os.stat_result:
    info = path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise DreyerExperimentRefusal("path is not a single-link regular file")
    return info


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise DreyerExperimentRefusal("output destination already exists")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise DreyerExperimentRefusal("output temporary path already exists")
    try:
        with temporary.open("xb") as handle:
            offset = 0
            while offset < len(payload):
                written = handle.write(payload[offset:])
                if written is None or written <= 0:
                    raise DreyerExperimentRefusal("output write made no progress")
                offset += written
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists() or path.is_symlink():
            raise DreyerExperimentRefusal("output destination appeared during publication")
        os.rename(temporary, path)
        observed = _regular_no_follow(path)
        if observed.st_size != len(payload) or _sha256(path.read_bytes()) != _sha256(payload):
            raise DreyerExperimentRefusal("published output readback differs")
    finally:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def _prepare_output_path(path: str | Path) -> Path:
    source = Path(path)
    if ".." in source.parts:
        raise DreyerExperimentRefusal("output traversal is forbidden")
    candidate = source.expanduser().absolute()
    lowered = {part.lower() for part in candidate.parts}
    if lowered.intersection({"data", ".codex_work"}):
        raise DreyerExperimentRefusal("generated output cannot use a protected data root")
    if candidate.exists() or candidate.is_symlink():
        raise DreyerExperimentRefusal("generated output already exists")
    return candidate


def plan_real_schedule() -> dict[str, int]:
    """Return the frozen exact real model schedule without touching data."""

    outer_folds = 60
    inner_folds = 5
    parameter_update_fits = outer_folds * (
        len(WINDOWS) * inner_folds
        + len(CALIBRATED_CONDITIONS) * inner_folds
        + len(WINDOWS)
        + len(CALIBRATED_CONDITIONS)
        + len(UNCALIBRATED_FITTED_CONDITIONS)
    )
    model_inference_runs = outer_folds * (
        len(CALIBRATED_CONDITIONS) * inner_folds
        + len(CALIBRATED_CONDITIONS)
        + len(UNCALIBRATED_FITTED_CONDITIONS)
    )
    return {
        "outer_folds": outer_folds,
        "inner_folds": inner_folds,
        "parameter_update_fits": parameter_update_fits,
        "model_inference_runs": model_inference_runs,
        "held_out_prediction_sets": outer_folds * len(scorer.CONDITIONS),
        "held_out_prediction_rows": outer_folds * len(scorer.CONDITIONS) * 80,
    }


def _feature_template(dimension: int, offset: int) -> Any:
    np = _np()
    values = np.asarray(
        [math.sin((index + 1) * (offset + 1) * 0.37) for index in range(dimension)],
        dtype="float64",
    )
    norm = float(np.linalg.norm(values))
    if norm <= 0.0:
        raise AssertionError("generated feature template is zero")
    return values / norm * math.sqrt(dimension)


def generate_feature_fixture(
    *, participants: int = 6, trials_per_run: int = 10, seed: int = 260825
) -> tuple[list[dict[str, Any]], dict[str, int], int]:
    """Generate deterministic synthetic features and separately sealed labels."""

    if participants < 4 or trials_per_run < 4 or trials_per_run % 2:
        raise DreyerExperimentRefusal("generated participant/trial inventory is invalid")
    np = _np()
    rng = np.random.default_rng(seed)
    templates = {
        name: _feature_template(dimension, offset)
        for offset, (name, dimension) in enumerate(FEATURE_DIMENSIONS.items())
        if name != "timing"
    }
    rows: list[dict[str, Any]] = []
    targets: dict[str, int] = {}
    generated_bytes = 0
    for participant_index in range(1, participants + 1):
        participant = f"g-{participant_index:02d}"
        participant_bias = rng.normal(0.0, 0.18, FEATURE_DIMENSIONS["E"])
        for run in (1, 2):
            for trial in range(trials_per_run):
                target = (trial + run) % 2
                sign = -1.0 if target == 0 else 1.0
                row_id = f"{participant}-r{run}-t{trial:02d}"
                timing = np.asarray(
                    [
                        float(run == 2),
                        trial / float(trials_per_run - 1),
                        math.sin(2.0 * math.pi * trial / trials_per_run),
                        math.cos(2.0 * math.pi * trial / trials_per_run),
                    ],
                    dtype="float64",
                )
                features: dict[str, list[float]] = {"timing": timing.tolist()}
                generated_bytes += timing.nbytes
                for window in WINDOWS:
                    if window == "late":
                        amplitudes = {
                            "E": 1.50,
                            "EOG": 0.15,
                            "EMG": 0.10,
                            "posterior": 0.20,
                            "frontal": 0.10,
                        }
                    elif window == "cue":
                        amplitudes = {
                            "E": 0.28,
                            "EOG": 0.95,
                            "EMG": 0.10,
                            "posterior": 1.25,
                            "frontal": 0.45,
                        }
                    else:
                        amplitudes = {
                            "E": 0.0,
                            "EOG": 0.0,
                            "EMG": 0.0,
                            "posterior": 0.0,
                            "frontal": 0.0,
                        }
                    for block in ("E", "EOG", "EMG", "posterior", "frontal"):
                        noise_scale = 0.72 if block == "E" else 0.90
                        values = rng.normal(
                            0.0, noise_scale, FEATURE_DIMENSIONS[block]
                        ) + sign * amplitudes[block] * templates[block]
                        if block == "E":
                            values = values + participant_bias
                        features[f"{window}_{block}"] = values.tolist()
                        generated_bytes += values.nbytes
                rows.append(
                    {
                        "participant": participant,
                        "run": run,
                        "trial": trial,
                        "row_id": row_id,
                        "features": features,
                    }
                )
                targets[row_id] = target
    validate_feature_rows(rows, expected_trials_per_run=trials_per_run)
    if set(targets) != {row["row_id"] for row in rows}:
        raise AssertionError("generated target identity inventory differs")
    return rows, targets, generated_bytes


def validate_feature_rows(
    rows: Sequence[Mapping[str, Any]], *, expected_trials_per_run: int
) -> None:
    np = _np()
    identities: set[tuple[str, int, int, str]] = set()
    groups: dict[tuple[str, int], set[int]] = defaultdict(set)
    for row in rows:
        try:
            participant = str(row["participant"])
            run = int(row["run"])
            trial = int(row["trial"])
            row_id = str(row["row_id"])
            features = row["features"]
        except (KeyError, TypeError, ValueError) as exc:
            raise DreyerExperimentRefusal("feature row identity is malformed") from exc
        if not participant or run not in (1, 2) or not row_id:
            raise DreyerExperimentRefusal("feature row identity is outside the frozen domain")
        identity = (participant, run, trial, row_id)
        if identity in identities:
            raise DreyerExperimentRefusal("feature row identity is duplicated")
        identities.add(identity)
        groups[(participant, run)].add(trial)
        if not isinstance(features, Mapping):
            raise DreyerExperimentRefusal("feature block inventory is malformed")
        expected_keys = {"timing"} | {
            f"{window}_{block}"
            for window in WINDOWS
            for block in ("E", "EOG", "EMG", "posterior", "frontal")
        }
        if set(features) != expected_keys:
            raise DreyerExperimentRefusal("feature block key inventory differs")
        for key, source in features.items():
            block = "timing" if key == "timing" else key.split("_", 1)[1]
            values = np.asarray(source, dtype="float64")
            if values.shape != (FEATURE_DIMENSIONS[block],) or not np.isfinite(values).all():
                raise DreyerExperimentRefusal(f"feature block is malformed: {key}")
    expected = set(range(expected_trials_per_run))
    if not groups or any(trials != expected for trials in groups.values()):
        raise DreyerExperimentRefusal("participant/run trial grid differs")


def build_fold_capability(
    rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    held_out_participant: str,
    *,
    inner_folds: int,
) -> tuple[FoldCapability, dict[str, int]]:
    source_rows = tuple(dict(row) for row in rows if row["participant"] != held_out_participant)
    held_rows = tuple(dict(row) for row in rows if row["participant"] == held_out_participant)
    if not source_rows or not held_rows:
        raise DreyerExperimentRefusal("fold source or held-out feature inventory is empty")
    source_ids = {row["row_id"] for row in source_rows}
    held_ids = {row["row_id"] for row in held_rows}
    if source_ids & held_ids or source_ids | held_ids != set(targets):
        raise DreyerExperimentRefusal("fold source and held-out identity partition differs")
    source_targets = {row_id: int(targets[row_id]) for row_id in sorted(source_ids)}
    held_targets = {row_id: int(targets[row_id]) for row_id in sorted(held_ids)}
    capability = FoldCapability(
        held_out_participant=held_out_participant,
        source_rows=source_rows,
        source_targets=source_targets,
        held_out_rows=held_rows,
        inner_folds=inner_folds,
    )
    if any(row_id in capability.source_targets for row_id in held_ids):
        raise DreyerExperimentRefusal("held-out target leaked into the source capability")
    return capability, held_targets


def _matrix(rows: Sequence[Mapping[str, Any]], key: str) -> Any:
    np = _np()
    try:
        values = np.asarray([row["features"][key] for row in rows], dtype="float64")
    except (KeyError, TypeError, ValueError) as exc:
        raise DreyerExperimentRefusal(f"feature matrix is malformed: {key}") from exc
    if values.ndim != 2 or values.shape[0] != len(rows) or not np.isfinite(values).all():
        raise DreyerExperimentRefusal(f"feature matrix is malformed: {key}")
    return values


def _nuisance(rows: Sequence[Mapping[str, Any]], window: str, *, posterior: bool) -> Any:
    np = _np()
    blocks = [
        _matrix(rows, f"{window}_EOG"),
        _matrix(rows, f"{window}_EMG"),
    ]
    if posterior:
        blocks.append(_matrix(rows, f"{window}_posterior"))
    blocks.append(_matrix(rows, "timing"))
    return np.concatenate(blocks, axis=1)


def _standardization(values: Any) -> tuple[Any, Any]:
    np = _np()
    mean = values.mean(axis=0)
    scale = values.std(axis=0)
    scale = np.where(scale <= 1e-12, 1.0, scale)
    return mean, scale


def _fit_logistic(features: Any, labels: Sequence[int], ledger: OperationLedger) -> FrozenBinaryLogistic:
    np = _np()
    LogisticRegression, _Ridge = _sklearn_classes()
    values = np.asarray(features, dtype="float64")
    target = np.asarray(labels, dtype="int64")
    if values.ndim != 2 or values.shape[0] != target.shape[0] or values.shape[0] < 4:
        raise DreyerExperimentRefusal("logistic fit arrays are malformed")
    if set(target.tolist()) != {0, 1} or not np.isfinite(values).all():
        raise DreyerExperimentRefusal("logistic fit class or value inventory differs")
    mean, scale = _standardization(values)
    standardized = (values - mean) / scale
    model = LogisticRegression(
        C=0.1,
        solver="lbfgs",
        max_iter=1000,
        tol=1e-6,
        class_weight=None,
        random_state=0,
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(standardized, target)
    if caught:
        raise DreyerExperimentRefusal(
            f"logistic fit emitted a warning: {type(caught[0].message).__name__}"
        )
    if model.classes_.tolist() != [0, 1] or model.coef_.shape != (1, values.shape[1]):
        raise DreyerExperimentRefusal("logistic fitted shape or class order differs")
    coefficient = np.asarray(model.coef_[0], dtype="float64")
    intercept = float(model.intercept_[0])
    if not np.isfinite(coefficient).all() or not math.isfinite(intercept):
        raise DreyerExperimentRefusal("logistic fitted parameter is non-finite")
    ledger.parameter_update_fits += 1
    return FrozenBinaryLogistic(
        mean=mean,
        scale=scale,
        coefficient=coefficient,
        intercept=intercept,
    )


def _predict_logits(model: FrozenBinaryLogistic, features: Any, ledger: OperationLedger) -> Any:
    np = _np()
    values = np.asarray(features, dtype="float64")
    if values.ndim != 2 or values.shape[1] != model.mean.shape[0]:
        raise DreyerExperimentRefusal("logistic prediction dimension differs")
    logits = ((values - model.mean) / model.scale) @ model.coefficient + model.intercept
    if not np.isfinite(logits).all():
        raise DreyerExperimentRefusal("logistic prediction is non-finite")
    ledger.model_inference_runs += 1
    return logits


def _fit_ridge(predictors: Any, central: Any, ledger: OperationLedger) -> FrozenMultiRidge:
    np = _np()
    _LogisticRegression, Ridge = _sklearn_classes()
    values = np.asarray(predictors, dtype="float64")
    output = np.asarray(central, dtype="float64")
    if values.ndim != 2 or output.ndim != 2 or values.shape[0] != output.shape[0]:
        raise DreyerExperimentRefusal("ridge fit arrays are malformed")
    input_mean, input_scale = _standardization(values)
    output_mean, output_scale = _standardization(output)
    x = (values - input_mean) / input_scale
    y = (output - output_mean) / output_scale
    model = Ridge(alpha=10.0, fit_intercept=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(x, y)
    if caught:
        raise DreyerExperimentRefusal(
            f"ridge fit emitted a warning: {type(caught[0].message).__name__}"
        )
    coefficient = np.asarray(model.coef_, dtype="float64")
    intercept = np.asarray(model.intercept_, dtype="float64")
    if coefficient.shape != (output.shape[1], values.shape[1]):
        raise DreyerExperimentRefusal("ridge fitted dimension differs")
    if not np.isfinite(coefficient).all() or not np.isfinite(intercept).all():
        raise DreyerExperimentRefusal("ridge fitted parameter is non-finite")
    ledger.parameter_update_fits += 1
    return FrozenMultiRidge(
        input_mean=input_mean,
        input_scale=input_scale,
        output_mean=output_mean,
        output_scale=output_scale,
        coefficient=coefficient,
        intercept=intercept,
    )


def _ridge_residual(model: FrozenMultiRidge, predictors: Any, central: Any) -> Any:
    np = _np()
    values = np.asarray(predictors, dtype="float64")
    observed = np.asarray(central, dtype="float64")
    x = (values - model.input_mean) / model.input_scale
    predicted_standard = x @ model.coefficient.T + model.intercept
    predicted = predicted_standard * model.output_scale + model.output_mean
    residual = observed - predicted
    if residual.shape != observed.shape or not np.isfinite(residual).all():
        raise DreyerExperimentRefusal("ridge residual output is malformed")
    return residual


def _adjacent_derangement(rows: Sequence[Mapping[str, Any]], values: Any) -> Any:
    np = _np()
    source = np.asarray(values, dtype="float64")
    if source.ndim != 2 or source.shape[0] != len(rows):
        raise DreyerExperimentRefusal("derangement input shape differs")
    result = np.empty_like(source)
    groups: dict[tuple[str, int], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[(str(row["participant"]), int(row["run"]))].append(index)
    for indices in groups.values():
        ordered = sorted(indices, key=lambda index: int(rows[index]["trial"]))
        if len(ordered) % 2:
            raise DreyerExperimentRefusal("derangement requires an even trial grid")
        observed_trials = [int(rows[index]["trial"]) for index in ordered]
        if observed_trials != list(range(len(ordered))):
            raise DreyerExperimentRefusal("derangement trial grid is not contiguous")
        for first in range(0, len(ordered), 2):
            left, right = ordered[first], ordered[first + 1]
            result[left] = source[right]
            result[right] = source[left]
    if np.array_equal(result, source):
        raise DreyerExperimentRefusal("derangement did not change the feature array")
    return result


def _rotated_labels(rows: Sequence[Mapping[str, Any]], labels: Sequence[int]) -> list[int]:
    output = list(int(value) for value in labels)
    groups: dict[tuple[str, int], list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        groups[(str(row["participant"]), int(row["run"]))].append(index)
    for indices in groups.values():
        ordered = sorted(indices, key=lambda index: int(rows[index]["trial"]))
        values = [output[index] for index in ordered]
        rotated = values[1:] + values[:1]
        for index, value in zip(ordered, rotated, strict=True):
            output[index] = value
    return output


def _fit_window_residuals(
    train_rows: Sequence[Mapping[str, Any]],
    apply_rows: Sequence[Mapping[str, Any]],
    ledger: OperationLedger,
) -> tuple[dict[str, Any], dict[str, Any]]:
    train_residuals: dict[str, Any] = {}
    apply_residuals: dict[str, Any] = {}
    for window in WINDOWS:
        model = _fit_ridge(
            _nuisance(train_rows, window, posterior=True),
            _matrix(train_rows, f"{window}_E"),
            ledger,
        )
        train_residuals[window] = _ridge_residual(
            model,
            _nuisance(train_rows, window, posterior=True),
            _matrix(train_rows, f"{window}_E"),
        )
        apply_residuals[window] = _ridge_residual(
            model,
            _nuisance(apply_rows, window, posterior=True),
            _matrix(apply_rows, f"{window}_E"),
        )
    return train_residuals, apply_residuals


def _condition_matrices(
    rows: Sequence[Mapping[str, Any]], residuals: Mapping[str, Any]
) -> dict[str, Any]:
    np = _np()
    late_n = _nuisance(rows, "late", posterior=True)
    late_no_p = _nuisance(rows, "late", posterior=False)
    pre_n = _nuisance(rows, "pre", posterior=True)
    cue_n = _nuisance(rows, "cue", posterior=True)
    late_r = residuals["late"]
    output = {
        "timing_only": _matrix(rows, "timing"),
        "EOG_only": _matrix(rows, "late_EOG"),
        "EMG_only": _matrix(rows, "late_EMG"),
        "posterior_only": _matrix(rows, "late_posterior"),
        "late_N": late_n,
        "late_central_E": _matrix(rows, "late_E"),
        "late_residual_R": late_r,
        "late_N_plus_R": np.concatenate((late_n, late_r), axis=1),
        "late_N_plus_deranged_R": np.concatenate(
            (late_n, _adjacent_derangement(rows, late_r)), axis=1
        ),
        "late_N_without_posterior": late_no_p,
        "late_N_without_posterior_plus_R": np.concatenate((late_no_p, late_r), axis=1),
        "pre_N": pre_n,
        "pre_N_plus_R": np.concatenate((pre_n, residuals["pre"]), axis=1),
        "cue_N": cue_n,
        "cue_N_plus_R": np.concatenate((cue_n, residuals["cue"]), axis=1),
    }
    output["source_label_rotated_late_N_plus_R"] = output["late_N_plus_R"]
    return output


def _sigmoid(logits: Any, temperature: float) -> Any:
    np = _np()
    scaled = np.asarray(logits, dtype="float64") / temperature
    output = np.empty_like(scaled)
    positive = scaled >= 0.0
    output[positive] = 1.0 / (1.0 + np.exp(-scaled[positive]))
    exponent = np.exp(scaled[~positive])
    output[~positive] = exponent / (1.0 + exponent)
    return np.clip(output, 1e-6, 1.0 - 1e-6)


def _temperature(logits: Any, labels: Sequence[int]) -> float:
    np = _np()
    values = np.asarray(logits, dtype="float64")
    target = np.asarray(labels, dtype="int64")
    if values.shape != target.shape or not np.isfinite(values).all():
        raise DreyerExperimentRefusal("temperature source logits are malformed")
    candidates = [2.0 ** (index / 16.0) for index in range(-32, 33)]
    ranked = []
    for value in candidates:
        probability = _sigmoid(values, value)
        selected = np.where(target == 1, probability, 1.0 - probability)
        loss = float(-np.log(selected).mean())
        ranked.append((loss, abs(math.log2(value)), value))
    return min(ranked)[2]


def _fold_number(participant: str, inner_folds: int) -> int:
    try:
        number = int(participant.rsplit("-", 1)[1])
    except (IndexError, ValueError) as exc:
        raise DreyerExperimentRefusal("participant number is malformed") from exc
    return (number - 1) % inner_folds


def _probability_rows(
    held_rows: Sequence[Mapping[str, Any]], probabilities: Mapping[str, Any]
) -> list[dict[str, Any]]:
    if set(probabilities) != set(scorer.CONDITIONS):
        raise DreyerExperimentRefusal("held-out probability condition inventory differs")
    output: list[dict[str, Any]] = []
    for index, row in enumerate(held_rows):
        for condition in scorer.CONDITIONS:
            probability = float(probabilities[condition][index])
            if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                raise DreyerExperimentRefusal("held-out probability is malformed")
            output.append(
                {
                    "participant": str(row["participant"]),
                    "run": int(row["run"]),
                    "trial": int(row["trial"]),
                    "row_id": str(row["row_id"]),
                    "condition": condition,
                    "probabilities": [1.0 - probability, probability],
                }
            )
    return output


def predict_fold(capability: FoldCapability, ledger: OperationLedger) -> list[dict[str, Any]]:
    """Fit one isolated fold without receiving any held-out target capability."""

    np = _np()
    source_rows = list(capability.source_rows)
    held_rows = list(capability.held_out_rows)
    source_labels = [capability.source_targets[row["row_id"]] for row in source_rows]
    participants = sorted({str(row["participant"]) for row in source_rows})
    if capability.held_out_participant in participants:
        raise DreyerExperimentRefusal("held-out participant appears in source rows")
    inner_folds = capability.inner_folds
    if inner_folds < 2 or len({_fold_number(value, inner_folds) for value in participants}) != inner_folds:
        raise DreyerExperimentRefusal("inner participant-fold inventory differs")
    oof_logits = {
        condition: np.full(len(source_rows), np.nan, dtype="float64")
        for condition in CALIBRATED_CONDITIONS
    }
    for inner_fold in range(inner_folds):
        train_indices = [
            index
            for index, row in enumerate(source_rows)
            if _fold_number(str(row["participant"]), inner_folds) != inner_fold
        ]
        check_indices = [
            index
            for index, row in enumerate(source_rows)
            if _fold_number(str(row["participant"]), inner_folds) == inner_fold
        ]
        train_rows = [source_rows[index] for index in train_indices]
        check_rows = [source_rows[index] for index in check_indices]
        train_labels = [source_labels[index] for index in train_indices]
        train_residuals, check_residuals = _fit_window_residuals(
            train_rows, check_rows, ledger
        )
        train_matrices = _condition_matrices(train_rows, train_residuals)
        check_matrices = _condition_matrices(check_rows, check_residuals)
        for condition in CALIBRATED_CONDITIONS:
            model = _fit_logistic(train_matrices[condition], train_labels, ledger)
            logits = _predict_logits(model, check_matrices[condition], ledger)
            for index, value in zip(check_indices, logits, strict=True):
                oof_logits[condition][index] = value
    if any(not np.isfinite(values).all() for values in oof_logits.values()):
        raise DreyerExperimentRefusal("source cross-fitted calibration logits are incomplete")
    temperatures = {
        condition: _temperature(values, source_labels)
        for condition, values in oof_logits.items()
    }
    source_residuals, held_residuals = _fit_window_residuals(source_rows, held_rows, ledger)
    source_matrices = _condition_matrices(source_rows, source_residuals)
    held_matrices = _condition_matrices(held_rows, held_residuals)
    probabilities: dict[str, Any] = {}
    for condition in CALIBRATED_CONDITIONS:
        model = _fit_logistic(source_matrices[condition], source_labels, ledger)
        logits = _predict_logits(model, held_matrices[condition], ledger)
        probabilities[condition] = _sigmoid(logits, temperatures[condition])
    for condition in UNCALIBRATED_FITTED_CONDITIONS:
        labels = (
            _rotated_labels(source_rows, source_labels)
            if condition == "source_label_rotated_late_N_plus_R"
            else source_labels
        )
        model = _fit_logistic(source_matrices[condition], labels, ledger)
        logits = _predict_logits(model, held_matrices[condition], ledger)
        probabilities[condition] = _sigmoid(logits, 1.0)
    probabilities["equal_prior"] = np.full(len(held_rows), 0.5, dtype="float64")
    ledger.held_out_prediction_sets += len(scorer.CONDITIONS)
    return _probability_rows(held_rows, probabilities)


def run_target_blind_predictions(
    rows: Sequence[Mapping[str, Any]],
    targets: Mapping[str, int],
    *,
    inner_folds: int,
) -> tuple[list[dict[str, Any]], SealedTargetVault, OperationLedger]:
    participants = sorted({str(row["participant"]) for row in rows})
    if len(participants) < inner_folds + 1:
        raise DreyerExperimentRefusal("generated participant inventory is too small")
    ledger = OperationLedger()
    predictions: list[dict[str, Any]] = []
    sealed_targets: dict[str, int] = {}
    for participant in participants:
        capability, fold_targets = build_fold_capability(
            rows, targets, participant, inner_folds=inner_folds
        )
        predictions.extend(predict_fold(capability, ledger))
        if set(sealed_targets) & set(fold_targets):
            raise DreyerExperimentRefusal("held-out target vault identities overlap")
        sealed_targets.update(fold_targets)
    if set(sealed_targets) != set(targets):
        raise DreyerExperimentRefusal("held-out target vault is incomplete")
    if ledger.held_out_target_deliveries or ledger.scores or ledger.post_target_updates:
        raise DreyerExperimentRefusal("target-blind prediction stage touched scoring state")
    return predictions, SealedTargetVault(sealed_targets), ledger


def _generated_header_cases() -> dict[str, int]:
    eeg = (
        "Fz", "FCz", "Cz", "CPz", "Pz", "C1", "C3", "C5", "C2", "C4",
        "C6", "F4", "FC2", "FC4", "FC6", "CP2", "CP4", "CP6", "P4", "F3",
        "FC1", "FC3", "FC5", "CP1", "CP3", "CP5", "P3",
    )
    labels = eeg + ("EOG-V", "EOG-H", "EOG-S", "EMG-L", "EMG-R", "EDF Annotations")
    valid = build_generated_edf_header(labels)
    summary = parse_edf_fixed_header(valid)
    if summary.signal_count != 33 or summary.labels != labels:
        raise DreyerExperimentRefusal("generated valid EDF header summary differs")
    malformed: list[bytes] = [
        valid[:-1],
        b"1" + valid[1:],
        valid[:184] + b"99999999" + valid[192:],
        valid[:252] + b"0000" + valid[256:],
        valid[:236] + b"00000000" + valid[244:],
        valid[:244] + b"00000000" + valid[252:],
        valid[:256] + valid[256:272] + valid[256:272] + valid[288:],
        valid[:256] + b"\xff" + valid[257:],
    ]
    refused = 0
    for payload in malformed:
        try:
            parse_edf_fixed_header(payload)
        except DreyerDataRefusal:
            refused += 1
        else:
            raise DreyerExperimentRefusal("malformed generated EDF header was accepted")
    return {"valid_cases": 1, "malformed_cases_refused": refused, "header_bytes": len(valid)}


def _generated_spectral_case() -> dict[str, Any]:
    np = _np()
    time_axis = np.arange(512, dtype="float64") / 512.0
    signal = np.stack(
        (
            np.sin(2.0 * np.pi * 10.0 * time_axis),
            np.sin(2.0 * np.pi * 16.0 * time_axis),
            np.sin(2.0 * np.pi * 25.0 * time_axis),
        )
    )
    first = log_relative_band_features(signal)
    second = log_relative_band_features(signal.copy())
    if first.shape != (3, 3) or not np.array_equal(first, second):
        raise DreyerExperimentRefusal("generated spectral replay differs")
    if [int(np.argmax(row)) for row in first] != [0, 1, 2]:
        raise DreyerExperimentRefusal("generated spectral band localization differs")
    return {
        "channels": 3,
        "samples": 512,
        "feature_shape": [3, 3],
        "sha256": _sha256(np.ascontiguousarray(first).tobytes()),
    }


def _result_payload(result: dict[str, Any]) -> bytes:
    previous = -1
    payload = b""
    for _ in range(8):
        payload = _canonical_bytes(result)
        current = len(payload)
        result["measurements"]["public_output_bytes"] = current
        if current == previous:
            return _canonical_bytes(result)
        previous = current
    raise DreyerExperimentRefusal("public output byte accounting did not converge")


def run_generated_qualification(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run one bounded generated-only qualification and publish one result."""

    assert_single_thread_environment()
    load_contract(root)
    output = _prepare_output_path(output_path)
    started = time.monotonic()
    header_cases = _generated_header_cases()
    spectral_case = _generated_spectral_case()
    rows, targets, generated_feature_bytes = generate_feature_fixture()
    replay_rows, replay_targets, replay_feature_bytes = generate_feature_fixture()
    fixture_hash = _sha256(_canonical_bytes(rows))
    if fixture_hash != _sha256(_canonical_bytes(replay_rows)):
        raise DreyerExperimentRefusal("generated feature fixture replay differs")
    if targets != replay_targets or generated_feature_bytes != replay_feature_bytes:
        raise DreyerExperimentRefusal("generated target or byte replay differs")
    predictions, vault, ledger = run_target_blind_predictions(rows, targets, inner_folds=3)
    if vault.deliveries != 0:
        raise DreyerExperimentRefusal("generated target vault was opened during prediction")
    premature_refusals = 0
    try:
        vault.deliver(prediction_freeze_green=False)
    except DreyerExperimentRefusal:
        premature_refusals += 1
    else:
        raise DreyerExperimentRefusal("generated targets were delivered before freeze")
    freeze = scorer.build_prediction_freeze(
        predictions,
        expected_participants=6,
        expected_rows_per_participant=20,
        contract_sha256=CONTRACT_SHA256,
    )
    freeze_payload = _canonical_bytes(freeze)
    forbidden = (
        '"probabilities"',
        '"target"',
        '"participant":"',
        ".codex_work",
        "/Users/",
    )
    if any(value in freeze_payload.decode("utf-8") for value in forbidden):
        raise DreyerExperimentRefusal("generated public freeze contains a forbidden field")
    delivered_targets = vault.deliver(prediction_freeze_green=True)
    ledger.held_out_target_deliveries += 1
    score = scorer.score_frozen_predictions(
        predictions,
        delivered_targets,
        freeze,
        expected_participants=6,
        expected_rows_per_participant=20,
        contract_sha256=CONTRACT_SHA256,
        positive_participants_minimum=4,
    )
    ledger.scores += 1
    repeat_delivery_refusals = 0
    try:
        vault.deliver(prediction_freeze_green=True)
    except DreyerExperimentRefusal:
        repeat_delivery_refusals += 1
    else:
        raise DreyerExperimentRefusal("generated targets were delivered twice")
    tampered = [dict(row) for row in predictions]
    tampered[0] = {**tampered[0], "probabilities": [0.25, 0.75]}
    tamper_refusals = 0
    try:
        scorer.verify_prediction_freeze(
            tampered,
            freeze,
            expected_participants=6,
            expected_rows_per_participant=20,
            contract_sha256=CONTRACT_SHA256,
        )
    except scorer.DreyerScoreRefusal:
        tamper_refusals += 1
    else:
        raise DreyerExperimentRefusal("tampered generated prediction passed freeze verification")
    private_prediction_bytes = len(_canonical_bytes(predictions))
    generated_input_bytes = generated_feature_bytes + header_cases["header_bytes"] + 3 * 512 * 8
    runtime = time.monotonic() - started
    peak_rss = peak_process_tree_rss_bytes()
    expected_fits = 6 * (12 * 3 + 19)
    expected_inference = 6 * (9 * 3 + 16)
    if ledger.parameter_update_fits != expected_fits:
        raise DreyerExperimentRefusal("generated parameter-update schedule differs")
    if ledger.model_inference_runs != expected_inference:
        raise DreyerExperimentRefusal("generated model-inference schedule differs")
    if ledger.held_out_prediction_sets != 6 * len(scorer.CONDITIONS):
        raise DreyerExperimentRefusal("generated held-out prediction schedule differs")
    caps = GENERATED_QUALIFICATION_CAPS
    if runtime > caps["runtime_seconds_maximum"]:
        raise DreyerExperimentRefusal("generated qualification runtime cap exceeded")
    if peak_rss > caps["peak_process_tree_RSS_bytes_maximum"]:
        raise DreyerExperimentRefusal("generated qualification RSS cap exceeded")
    if generated_input_bytes > caps["generated_input_bytes_maximum"]:
        raise DreyerExperimentRefusal("generated input byte cap exceeded")
    if private_prediction_bytes > caps["private_temporary_bytes_maximum"]:
        raise DreyerExperimentRefusal("generated private byte cap exceeded")
    result = {
        "schema_name": "neurodecodekit.dreyer_c5r_1_generated_qualification_result",
        "schema_version": "0.1.0",
        "lane_id": LANE_ID,
        "status": "passed_generated_only_no_real_or_private_data",
        "contract": {
            "path": str(CONTRACT_RELATIVE_PATH),
            "sha256": CONTRACT_SHA256,
            "verified": True,
        },
        "cases": {
            "EDF_fixed_header": header_cases,
            "causal_spectral_feature": spectral_case,
            "deterministic_feature_replay": True,
            "target_delivery_before_freeze_refusals": premature_refusals,
            "target_repeat_delivery_refusals": repeat_delivery_refusals,
            "prediction_tamper_refusals": tamper_refusals,
            "public_freeze_forbidden_field_refusals": 0,
        },
        "generated_fixture": {
            "participants": 6,
            "runs_per_participant": 2,
            "trials_per_run": 10,
            "identity_rows": 120,
            "feature_fixture_sha256": fixture_hash,
            "feature_bytes": generated_feature_bytes,
        },
        "schedule": {
            "parameter_update_fits": ledger.parameter_update_fits,
            "model_inference_runs": ledger.model_inference_runs,
            "held_out_prediction_sets": ledger.held_out_prediction_sets,
            "prediction_rows": len(predictions),
            "synthetic_target_deliveries": ledger.held_out_target_deliveries,
            "synthetic_scores": ledger.scores,
            "post_target_updates": ledger.post_target_updates,
        },
        "synthetic_router": {
            "route": score["route"],
            "primary_gate_passed": score["primary_gate_passed"],
            "scientific_value": "none_generated_positive_control_only",
        },
        "prediction_freeze": {
            "bytes": len(freeze_payload),
            "sha256": _sha256(freeze_payload),
            "contains_individual_prediction_probability_target_or_outcome": False,
        },
        "access_counters": {
            "real_or_private_path_opens": 0,
            "real_EDF_payload_downloads": 0,
            "real_EDF_header_reads": 0,
            "real_annotation_reads": 0,
            "real_signal_sample_reads": 0,
            "real_target_or_label_reads": 0,
            "network_bytes": 0,
            "model_downloads": 0,
            "language_model_calls": 0,
            "real_training_runs": 0,
            "real_prediction_sets": 0,
            "real_target_deliveries": 0,
            "real_scores": 0,
            "claim_upgrades": 0,
        },
        "measurements": {
            "runtime_seconds": runtime,
            "peak_process_tree_RSS_bytes": peak_rss,
            "generated_input_bytes": generated_input_bytes,
            "private_temporary_prediction_bytes": private_prediction_bytes,
            "public_output_bytes": 0,
            "producer_causal": True,
            "required_context_seconds": 1.0,
            "end_to_end_latency_measured": False,
        },
        "real_schedule_plan": plan_real_schedule(),
        "warnings": [
            "synthetic_positive_control_has_no_scientific_claim_value",
            "source_EDF_sensor_roster_remains_unverified",
            "no_real_payload_header_annotation_signal_target_model_or_score_was_accessed",
        ],
        "claim_boundary": {
            "engineering_capability": "generated_target_firewall_compact_model_prediction_freeze_and_aggregate_scorer",
            "scientific_claim_not_established": "any_real_EEG_information_unseen_person_generalization_EEG_beyond_peripherals_movement_intention_language_live_hardware_or_clinical_result",
        },
    }
    payload = _result_payload(result)
    if len(payload) > caps["public_output_bytes_maximum"]:
        raise DreyerExperimentRefusal("generated public output cap exceeded")
    _atomic_write(output, payload)
    return result


def inspect_generated_result(path: str | Path) -> dict[str, Any]:
    candidate = Path(path).expanduser().absolute()
    info = _regular_no_follow(candidate)
    if info.st_size > 1_048_576:
        raise DreyerExperimentRefusal("generated result exceeds inspect cap")
    value = json.loads(candidate.read_bytes())
    if not isinstance(value, dict) or value.get("lane_id") != LANE_ID:
        raise DreyerExperimentRefusal("generated result identity differs")
    return {
        "status": value.get("status"),
        "synthetic_route": value.get("synthetic_router", {}).get("route"),
        "measurements": value.get("measurements"),
        "access_counters": value.get("access_counters"),
        "warnings": value.get("warnings"),
        "claim_boundary": value.get("claim_boundary"),
    }
