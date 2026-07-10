"""Dependency-free intercept-only blank calibration and paired audits."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Iterable, Sequence

from neurodecodekit.evaluation.metrics import levenshtein_distance


BLANK_CALIBRATION_CONFIG_SHA256 = (
    "43de56b1d275c0fd5b08a92d9dabc6893f7fe7ee49e02195623f6d61caa57e47"
)


@dataclass(frozen=True)
class BlankInterceptConfig:
    """Preregistered one-parameter calibration fit."""

    blank_id: int = 0
    fit_bracket: tuple[float, float] = (-8.0, 8.0)
    fit_iterations: int = 80
    fit_objective: str = "mean_binary_negative_log_likelihood"
    fit_split: str = "train_frames"
    nonblank_score: str = "logsumexp_classes_1_to_5"
    slope: float = 1.0

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["fit_bracket"] = list(self.fit_bracket)
        return value

    @property
    def config_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class BlankInterceptFit:
    """One deterministic fitted intercept and its train-only evidence."""

    intercept: float
    iterations: int
    lower_bound: float
    upper_bound: float
    final_gradient: float
    train_frames: int
    train_blank_frames: int
    train_metrics_before: dict[str, object]
    train_metrics_after: dict[str, object]
    config_sha256: str

    @property
    def parameter_payload_sha256(self) -> str:
        return _sha256_json(
            {
                "dtype": "float64",
                "intercept": self.intercept,
                "shape": [1],
            }
        )


def registered_blank_intercept_config() -> BlankInterceptConfig:
    config = BlankInterceptConfig()
    if config.config_sha256 != BLANK_CALIBRATION_CONFIG_SHA256:
        raise RuntimeError("registered blank calibration config hash drifted")
    return config


def blank_margins_from_logits(
    logits: Iterable[Sequence[float]], *, blank_id: int = 0
) -> list[float]:
    """Return blank logit minus logsumexp of all nonblank logits."""

    rows = []
    class_count: int | None = None
    for raw_row in logits:
        row = tuple(float(value) for value in raw_row)
        if class_count is None:
            class_count = len(row)
            if class_count < 2 or blank_id < 0 or blank_id >= class_count:
                raise ValueError("blank calibration needs a valid blank plus nonblank classes")
        elif len(row) != class_count:
            raise ValueError("blank calibration class count changed across frames")
        if any(not math.isfinite(value) for value in row):
            raise ValueError("blank calibration logits must be finite")
        nonblank = [value for index, value in enumerate(row) if index != blank_id]
        rows.append(row[blank_id] - _logsumexp(nonblank))
    if not rows:
        raise ValueError("blank calibration needs at least one frame")
    return rows


def fit_blank_intercept(
    margins: Iterable[float],
    blank_labels: Iterable[int | bool],
    *,
    config: BlankInterceptConfig | None = None,
) -> BlankInterceptFit:
    """Fit one intercept by the preregistered fixed-iteration bisection."""

    selected = config or registered_blank_intercept_config()
    _validate_config(selected)
    values, labels = _validate_binary_rows(margins, blank_labels)
    lower, upper = selected.fit_bracket
    lower_gradient = _mean_gradient(values, labels, lower)
    upper_gradient = _mean_gradient(values, labels, upper)
    if lower_gradient > 0.0 or upper_gradient < 0.0:
        raise ValueError("blank intercept root is not bracketed")
    for _ in range(selected.fit_iterations):
        midpoint = (lower + upper) / 2.0
        gradient = _mean_gradient(values, labels, midpoint)
        if gradient < 0.0:
            lower = midpoint
        else:
            upper = midpoint
    intercept = (lower + upper) / 2.0
    final_gradient = _mean_gradient(values, labels, intercept)
    before = blank_binary_metrics(values, labels, intercept=0.0)
    after = blank_binary_metrics(values, labels, intercept=intercept)
    if not float(after["negative_log_likelihood"]) < float(
        before["negative_log_likelihood"]
    ):
        raise ValueError("blank intercept did not strictly improve train log loss")
    return BlankInterceptFit(
        intercept=intercept,
        iterations=selected.fit_iterations,
        lower_bound=lower,
        upper_bound=upper,
        final_gradient=final_gradient,
        train_frames=len(values),
        train_blank_frames=sum(labels),
        train_metrics_before=before,
        train_metrics_after=after,
        config_sha256=selected.config_sha256,
    )


def blank_binary_metrics(
    margins: Iterable[float],
    blank_labels: Iterable[int | bool],
    *,
    intercept: float,
    bins: int = 10,
) -> dict[str, object]:
    """Measure binary blank calibration without external dependencies."""

    values, labels = _validate_binary_rows(margins, blank_labels)
    if not math.isfinite(intercept):
        raise ValueError("blank intercept must be finite")
    if bins < 1 or bins > 10000:
        raise ValueError("calibration bin count must be between 1 and 10000")
    probabilities = [_sigmoid(value + intercept) for value in values]
    nll = sum(
        _softplus(-(value + intercept)) if label else _softplus(value + intercept)
        for value, label in zip(values, labels, strict=True)
    ) / len(values)
    brier = sum(
        (probability - label) ** 2
        for probability, label in zip(probabilities, labels, strict=True)
    ) / len(values)
    counts = [0] * bins
    probability_sums = [0.0] * bins
    label_sums = [0] * bins
    for probability, label in zip(probabilities, labels, strict=True):
        index = min(int(probability * bins), bins - 1)
        counts[index] += 1
        probability_sums[index] += probability
        label_sums[index] += label
    calibration_rows = []
    ece = 0.0
    for index, count in enumerate(counts):
        if count:
            mean_probability = probability_sums[index] / count
            empirical_fraction = label_sums[index] / count
            ece += count / len(values) * abs(mean_probability - empirical_fraction)
        else:
            mean_probability = None
            empirical_fraction = None
        calibration_rows.append(
            {
                "bin_index": index,
                "lower": index / bins,
                "upper": (index + 1) / bins,
                "count": count,
                "mean_probability": mean_probability,
                "empirical_blank_fraction": empirical_fraction,
            }
        )
    predicted = [probability >= 0.5 for probability in probabilities]
    true_positive = sum(p and bool(y) for p, y in zip(predicted, labels, strict=True))
    false_positive = sum(p and not y for p, y in zip(predicted, labels, strict=True))
    true_negative = sum(not p and not y for p, y in zip(predicted, labels, strict=True))
    false_negative = sum(not p and bool(y) for p, y in zip(predicted, labels, strict=True))
    return {
        "frames": len(values),
        "blank_frames": sum(labels),
        "empirical_blank_fraction": sum(labels) / len(values),
        "mean_predicted_blank_probability": sum(probabilities) / len(values),
        "negative_log_likelihood": nll,
        "brier_score": brier,
        "expected_calibration_error_10_bin": ece,
        "confusion_at_0_5": {
            "true_blank": true_positive,
            "false_blank": false_positive,
            "true_nonblank": true_negative,
            "missed_blank": false_negative,
        },
        "calibration_bins": calibration_rows,
    }


def apply_blank_intercept(
    logits: Sequence[float], *, intercept: float, blank_id: int = 0
) -> tuple[float, ...]:
    """Add one finite scalar to only the blank logit."""

    values = [float(value) for value in logits]
    if len(values) < 2 or blank_id < 0 or blank_id >= len(values):
        raise ValueError("blank intercept needs a valid blank plus nonblank classes")
    if any(not math.isfinite(value) for value in values) or not math.isfinite(intercept):
        raise ValueError("blank intercept inputs must be finite")
    values[blank_id] += intercept
    return tuple(values)


def paired_sequence_change_metrics(
    targets: Sequence[Sequence[int]],
    unmodified: Sequence[Sequence[int]],
    calibrated: Sequence[Sequence[int]],
) -> dict[str, object]:
    """Audit item-level corrections, regressions, and strict tail insertions."""

    if not targets or len(targets) != len(unmodified) or len(targets) != len(calibrated):
        raise ValueError("paired sequence audit needs equal nonempty collections")
    rows = []
    corrected = 0
    new_errors = 0
    worsened_cer = 0
    improved_cer = 0
    for target_raw, base_raw, calibrated_raw in zip(
        targets, unmodified, calibrated, strict=True
    ):
        target = tuple(int(value) for value in target_raw)
        base = tuple(int(value) for value in base_raw)
        adjusted = tuple(int(value) for value in calibrated_raw)
        if not target:
            raise ValueError("paired sequence targets must be nonempty")
        base_distance = levenshtein_distance(target, base)
        adjusted_distance = levenshtein_distance(target, adjusted)
        base_exact = base_distance == 0
        adjusted_exact = adjusted_distance == 0
        corrected += int(not base_exact and adjusted_exact)
        new_errors += int(base_exact and not adjusted_exact)
        worsened_cer += int(adjusted_distance > base_distance)
        improved_cer += int(adjusted_distance < base_distance)
        rows.append(
            {
                "target": list(target),
                "unmodified": list(base),
                "calibrated": list(adjusted),
                "unmodified_edit_distance": base_distance,
                "calibrated_edit_distance": adjusted_distance,
                "unmodified_tail_insertions": _strict_tail_insertions(target, base),
                "calibrated_tail_insertions": _strict_tail_insertions(target, adjusted),
            }
        )
    base_tail = sum(int(row["unmodified_tail_insertions"]) for row in rows)
    adjusted_tail = sum(int(row["calibrated_tail_insertions"]) for row in rows)
    return {
        "items": len(rows),
        "corrected_items": corrected,
        "new_error_items": new_errors,
        "items_with_worse_cer": worsened_cer,
        "items_with_improved_cer": improved_cer,
        "unmodified_tail_inserted_tokens": base_tail,
        "calibrated_tail_inserted_tokens": adjusted_tail,
        "tail_inserted_token_reduction": base_tail - adjusted_tail,
        "items_detail": rows,
    }


def paired_metric_bootstrap(
    targets: Sequence[Sequence[int]],
    unmodified: Sequence[Sequence[int]],
    calibrated: Sequence[Sequence[int]],
    *,
    resamples: int,
    seed: int,
) -> dict[str, object]:
    """Deterministic item bootstrap for exact gain and CER reduction."""

    if resamples < 1 or resamples > 1_000_000:
        raise ValueError("bootstrap resamples must be between 1 and 1000000")
    paired_sequence_change_metrics(targets, unmodified, calibrated)
    try:
        import random

        rng = random.Random(seed)
    except (TypeError, ValueError) as exc:
        raise ValueError("bootstrap seed is invalid") from exc
    exact_deltas = []
    cer_deltas = []
    item_count = len(targets)
    per_item_exact = []
    per_item_cer = []
    for target, base, adjusted in zip(targets, unmodified, calibrated, strict=True):
        target_length = len(target)
        if target_length < 1:
            raise ValueError("bootstrap targets must be nonempty")
        base_distance = levenshtein_distance(target, base)
        adjusted_distance = levenshtein_distance(target, adjusted)
        per_item_exact.append(float(adjusted_distance == 0) - float(base_distance == 0))
        per_item_cer.append((base_distance - adjusted_distance) / target_length)
    for _ in range(resamples):
        indices = [rng.randrange(item_count) for _ in range(item_count)]
        exact_deltas.append(sum(per_item_exact[index] for index in indices) / item_count)
        cer_deltas.append(sum(per_item_cer[index] for index in indices) / item_count)
    exact_deltas.sort()
    cer_deltas.sort()
    return {
        "items": item_count,
        "resamples": resamples,
        "seed": seed,
        "exact_accuracy_gain_mean": sum(per_item_exact) / item_count,
        "cer_reduction_mean": sum(per_item_cer) / item_count,
        "exact_accuracy_gain_interval_95": _percentile_interval(exact_deltas),
        "cer_reduction_interval_95": _percentile_interval(cer_deltas),
    }


def _validate_config(config: BlankInterceptConfig) -> None:
    lower, upper = config.fit_bracket
    if (
        config.blank_id != 0
        or config.fit_iterations != 80
        or config.fit_objective != "mean_binary_negative_log_likelihood"
        or config.fit_split != "train_frames"
        or config.nonblank_score != "logsumexp_classes_1_to_5"
        or config.slope != 1.0
        or not math.isfinite(lower)
        or not math.isfinite(upper)
        or lower != -8.0
        or upper != 8.0
    ):
        raise ValueError("blank intercept config does not match preregistration")
    if config.config_sha256 != BLANK_CALIBRATION_CONFIG_SHA256:
        raise ValueError("blank intercept config hash does not match preregistration")


def _validate_binary_rows(
    margins: Iterable[float], blank_labels: Iterable[int | bool]
) -> tuple[list[float], list[int]]:
    values = [float(value) for value in margins]
    raw_labels = list(blank_labels)
    if not values or len(values) != len(raw_labels):
        raise ValueError("blank calibration margins and labels must be equal and nonempty")
    if any(not math.isfinite(value) for value in values):
        raise ValueError("blank calibration margins must be finite")
    labels = []
    for value in raw_labels:
        if isinstance(value, bool):
            labels.append(int(value))
        elif isinstance(value, int) and value in {0, 1}:
            labels.append(value)
        else:
            raise ValueError("blank calibration labels must be binary integers")
    if not any(labels) or all(labels):
        raise ValueError("blank calibration needs both blank and nonblank frames")
    return values, labels


def _mean_gradient(margins: Sequence[float], labels: Sequence[int], intercept: float) -> float:
    return sum(
        _sigmoid(value + intercept) - label
        for value, label in zip(margins, labels, strict=True)
    ) / len(margins)


def _strict_tail_insertions(target: tuple[int, ...], prediction: tuple[int, ...]) -> int:
    if len(prediction) > len(target) and prediction[: len(target)] == target:
        return len(prediction) - len(target)
    return 0


def _logsumexp(values: Sequence[float]) -> float:
    maximum = max(values)
    return maximum + math.log(sum(math.exp(value - maximum) for value in values))


def _sigmoid(value: float) -> float:
    if value >= 0:
        inverse = math.exp(-value)
        return 1.0 / (1.0 + inverse)
    exponential = math.exp(value)
    return exponential / (1.0 + exponential)


def _softplus(value: float) -> float:
    return max(value, 0.0) + math.log1p(math.exp(-abs(value)))


def _percentile_interval(values: Sequence[float]) -> list[float]:
    lower_index = int(math.floor(0.025 * (len(values) - 1)))
    upper_index = int(math.ceil(0.975 * (len(values) - 1)))
    return [float(values[lower_index]), float(values[upper_index])]


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
