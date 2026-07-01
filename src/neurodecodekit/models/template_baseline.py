"""Tiny neural-window template baseline.

The template baseline averages training windows by label and predicts the label
whose average window is nearest. It is intentionally transparent and small.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Iterable

from neurodecodekit.models.template_classifier import TemplateClassifier


@dataclass(frozen=True)
class TemplateBaselineResult:
    """Predictions and metadata for a nearest-template baseline."""

    predictions: list[str]
    targets: list[str]
    strategy: str
    split_mode: str
    seed: int
    train_fraction: float | None
    n_train_rows: int
    n_eval_rows: int
    n_classes: int
    train_label_counts: dict[str, int]
    eval_label_counts: dict[str, int]
    missing_eval_labels_in_train: list[str]
    feature_shape: tuple[int, int]
    train_indices: list[int] | None
    eval_indices: list[int] | None
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("predictions")
        payload.pop("targets")
        payload["kind"] = "template-window"
        payload["description"] = (
            "Nearest-centroid baseline over neural-window arrays; no deep learning used."
        )
        payload["uses_neural_windows"] = True
        payload["no_deep_learning"] = True
        return payload


def run_template_baseline_from_single_cache(
    *,
    windows,
    labels: Iterable[str],
    train_fraction: float = 0.5,
    seed: int = 7,
) -> TemplateBaselineResult:
    """Split one cache into train/eval rows and run the template baseline."""

    np = _require_numpy()
    x = np.asarray(windows)
    y = _labels_array(labels)
    _validate_windows_and_labels(x, y)
    train_idx, eval_idx, split_warnings = stratified_holdout_indices(
        y.tolist(),
        train_fraction=train_fraction,
        seed=seed,
    )
    return run_template_baseline(
        train_windows=x[train_idx],
        train_labels=y[train_idx].tolist(),
        eval_windows=x[eval_idx],
        eval_labels=y[eval_idx].tolist(),
        split_mode="single-cache-stratified-holdout",
        seed=seed,
        train_fraction=train_fraction,
        train_indices=train_idx,
        eval_indices=eval_idx,
        extra_warnings=split_warnings,
    )


def run_template_baseline(
    *,
    train_windows,
    train_labels: Iterable[str],
    eval_windows,
    eval_labels: Iterable[str],
    split_mode: str = "separate-cache",
    seed: int = 7,
    train_fraction: float | None = None,
    train_indices: list[int] | None = None,
    eval_indices: list[int] | None = None,
    extra_warnings: Iterable[str] | None = None,
) -> TemplateBaselineResult:
    """Fit templates on train windows and predict eval windows."""

    np = _require_numpy()
    train_x = np.asarray(train_windows)
    eval_x = np.asarray(eval_windows)
    train_y = _labels_array(train_labels)
    eval_y = _labels_array(eval_labels)
    _validate_windows_and_labels(train_x, train_y, role="train")
    _validate_windows_and_labels(eval_x, eval_y, role="eval")
    if train_x.shape[1:] != eval_x.shape[1:]:
        raise ValueError(
            "train and eval windows must have matching [channels, timepoints] shape: "
            f"{train_x.shape[1:]} vs {eval_x.shape[1:]}"
        )

    classifier = TemplateClassifier().fit(train_x, train_y)
    predictions = [str(value) for value in classifier.predict(eval_x).tolist()]
    targets = [str(value) for value in eval_y.tolist()]
    train_counts = _count_labels(train_y.tolist())
    eval_counts = _count_labels(targets)
    missing = sorted(set(targets) - set(train_counts))
    warnings = ["template_baseline_uses_neural_windows", "template_baseline_no_deep_learning"]
    if split_mode == "single-cache-stratified-holdout":
        warnings.append("template_single_cache_holdout_split")
    warnings.extend(extra_warnings or [])
    if missing:
        warnings.append("template_eval_labels_missing_from_train")

    return TemplateBaselineResult(
        predictions=predictions,
        targets=targets,
        strategy="nearest-centroid",
        split_mode=split_mode,
        seed=seed,
        train_fraction=train_fraction,
        n_train_rows=int(train_x.shape[0]),
        n_eval_rows=int(eval_x.shape[0]),
        n_classes=len(train_counts),
        train_label_counts=train_counts,
        eval_label_counts=eval_counts,
        missing_eval_labels_in_train=missing,
        feature_shape=(int(train_x.shape[1]), int(train_x.shape[2])),
        train_indices=list(train_indices) if train_indices is not None else None,
        eval_indices=list(eval_indices) if eval_indices is not None else None,
        warnings=warnings,
    )


def stratified_holdout_indices(
    labels: Iterable[str],
    *,
    train_fraction: float = 0.5,
    seed: int = 7,
) -> tuple[list[int], list[int], list[str]]:
    """Return deterministic stratified train/eval row indices."""

    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must be between 0 and 1.")
    label_rows: dict[str, list[int]] = defaultdict(list)
    for index, label in enumerate(str(value) for value in labels):
        label_rows[label].append(index)
    if not label_rows:
        raise ValueError("template baseline requires at least one labeled row.")

    rng = random.Random(seed)
    train: list[int] = []
    eval_: list[int] = []
    warnings: list[str] = []
    for label in sorted(label_rows):
        rows = list(label_rows[label])
        rng.shuffle(rows)
        if len(rows) == 1:
            train.extend(rows)
            warnings.append("template_label_has_no_eval_example")
            continue
        n_train = int(round(len(rows) * train_fraction))
        n_train = min(max(1, n_train), len(rows) - 1)
        train.extend(rows[:n_train])
        eval_.extend(rows[n_train:])

    train.sort()
    eval_.sort()
    if not train:
        raise ValueError("template baseline split produced no train rows.")
    if not eval_:
        raise ValueError(
            "template baseline split produced no eval rows; use more examples or a separate eval cache."
        )
    return train, eval_, sorted(set(warnings))


def _labels_array(labels: Iterable[str]):
    np = _require_numpy()
    return np.asarray([str(value) for value in labels])


def _validate_windows_and_labels(windows, labels, *, role: str = "cache") -> None:
    if windows.ndim != 3:
        raise ValueError(f"Expected {role} windows [samples, channels, times], got {windows.shape}")
    if len(windows) != len(labels):
        raise ValueError(f"{role} windows and labels must have the same length")
    if len(labels) == 0:
        raise ValueError(f"template baseline requires at least one {role} row.")


def _count_labels(labels: Iterable[str]) -> dict[str, int]:
    counts = Counter(str(value) for value in labels)
    return {label: int(counts[label]) for label in sorted(counts)}


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Template baseline requires NumPy: `pip install numpy`.") from exc
    return np
