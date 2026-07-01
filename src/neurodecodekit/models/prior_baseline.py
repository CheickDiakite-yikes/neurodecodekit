"""No-brain prior baselines for text/label decoding.

These baselines deliberately ignore neural windows. Their job is to make the
language-prior floor visible before any model claims signal from brain data.
"""

from __future__ import annotations

import random
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable, Literal


PriorStrategy = Literal["most-frequent", "frequency-sample", "uniform-random"]

VALID_PRIOR_STRATEGIES: tuple[PriorStrategy, ...] = (
    "most-frequent",
    "frequency-sample",
    "uniform-random",
)


@dataclass(frozen=True)
class PriorBaselineResult:
    """Predictions and metadata for a no-brain prior baseline."""

    predictions: list[str]
    strategy: str
    seed: int
    n_train_rows: int
    n_eval_rows: int
    vocab_size: int
    counts: dict[str, int]
    top_target: str
    top_count: int
    fit_on_eval_targets: bool
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        """Return report-friendly metadata without duplicating all predictions."""

        payload = asdict(self)
        payload.pop("predictions")
        payload["kind"] = "prior-only"
        payload["description"] = "No neural signal used; predictions come only from target priors."
        return payload


def run_prior_baseline(
    *,
    eval_targets: Iterable[str],
    train_targets: Iterable[str] | None = None,
    strategy: PriorStrategy = "most-frequent",
    seed: int = 7,
) -> PriorBaselineResult:
    """Fit a tiny no-brain prior and produce predictions for eval rows.

    If ``train_targets`` is omitted, the baseline fits on the eval targets and
    emits a warning. That mode is useful for smoke tests, but clean experiments
    should pass a separate train target set.
    """

    if strategy not in VALID_PRIOR_STRATEGIES:
        valid = ", ".join(VALID_PRIOR_STRATEGIES)
        raise ValueError(f"unknown prior strategy {strategy!r}; choose one of: {valid}")

    eval_rows = [str(row) for row in eval_targets]
    if not eval_rows:
        raise ValueError("prior baseline requires at least one eval target row.")

    fit_on_eval = train_targets is None
    train_rows = list(eval_rows if train_targets is None else [str(row) for row in train_targets])
    if not train_rows:
        raise ValueError("prior baseline requires at least one train target row.")

    counts = Counter(train_rows)
    first_seen = _first_seen_index(train_rows)
    ranked = _rank_targets(counts, first_seen)
    predictions = _predict_rows(strategy=strategy, n_rows=len(eval_rows), ranked=ranked, counts=counts, seed=seed)
    top_target = ranked[0]
    warnings = ["prior_baseline_no_neural_signal"]
    if fit_on_eval:
        warnings.append("prior_fit_on_eval_targets_for_smoke_only")

    return PriorBaselineResult(
        predictions=predictions,
        strategy=strategy,
        seed=seed,
        n_train_rows=len(train_rows),
        n_eval_rows=len(eval_rows),
        vocab_size=len(ranked),
        counts={target: int(counts[target]) for target in ranked},
        top_target=top_target,
        top_count=int(counts[top_target]),
        fit_on_eval_targets=fit_on_eval,
        warnings=warnings,
    )


def _first_seen_index(rows: list[str]) -> dict[str, int]:
    first_seen: dict[str, int] = {}
    for index, row in enumerate(rows):
        first_seen.setdefault(row, index)
    return first_seen


def _rank_targets(counts: Counter[str], first_seen: dict[str, int]) -> list[str]:
    return sorted(counts, key=lambda value: (-counts[value], first_seen[value], value))


def _predict_rows(
    *,
    strategy: str,
    n_rows: int,
    ranked: list[str],
    counts: Counter[str],
    seed: int,
) -> list[str]:
    if strategy == "most-frequent":
        return [ranked[0]] * n_rows

    rng = random.Random(seed)
    if strategy == "frequency-sample":
        weights = [counts[target] for target in ranked]
        return rng.choices(ranked, weights=weights, k=n_rows)
    if strategy == "uniform-random":
        return [rng.choice(ranked) for _ in range(n_rows)]

    valid = ", ".join(VALID_PRIOR_STRATEGIES)
    raise ValueError(f"unknown prior strategy {strategy!r}; choose one of: {valid}")
