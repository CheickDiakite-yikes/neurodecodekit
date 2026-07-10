"""Report-card utilities for tiny neural decoding loops."""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.evaluation.keyboard import aligned_keyboard_distance
from neurodecodekit.evaluation.metrics import (
    character_error_rate,
    levenshtein_distance,
    normalize_text,
    sentence_exact_match,
    word_error_rate,
)


@dataclass(frozen=True)
class TextExampleScore:
    """One target/prediction example and its local metrics."""

    index: int
    target: str
    prediction: str
    cer: float | None
    wer: float | None
    keyboard_distance: float
    exact_match: bool
    target_chars: int
    prediction_chars: int
    target_words: int
    prediction_words: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def read_text_rows(path: str | Path) -> list[str]:
    """Read one target or prediction per line, preserving intentional blanks."""

    return Path(path).read_text(encoding="utf-8").splitlines()


def labels_to_text_rows(labels: Any) -> list[str]:
    """Convert a loaded cache label array to text rows."""

    values = labels.tolist()
    if not isinstance(values, list):
        values = [values]
    return [str(value) for value in values]


def build_text_report(
    *,
    targets: Iterable[str],
    predictions: Iterable[str],
    cache_summary: dict[str, Any] | None = None,
    run_name: str | None = None,
    split: str | None = None,
    max_examples: int = 10,
    warnings: Iterable[str] | None = None,
    runtime_sec: float | None = None,
) -> dict[str, Any]:
    """Build a JSON-serializable text decoding report."""

    target_rows = [str(row) for row in targets]
    prediction_rows = [str(row) for row in predictions]
    if len(target_rows) != len(prediction_rows):
        raise ValueError(
            "targets and predictions must contain the same number of rows: "
            f"{len(target_rows)} targets vs {len(prediction_rows)} predictions."
        )
    if not target_rows:
        raise ValueError("report requires at least one target/prediction row.")
    if max_examples < 1:
        raise ValueError("max_examples must be >= 1")

    examples = [
        score_text_example(index, target, prediction)
        for index, (target, prediction) in enumerate(zip(target_rows, prediction_rows))
    ]
    aggregate = aggregate_text_scores(examples)
    worst_examples = sorted(
        examples,
        key=lambda item: (
            _sort_metric(item.cer),
            _sort_metric(item.wer),
            item.keyboard_distance,
        ),
        reverse=True,
    )[:max_examples]

    run = {
        "name": run_name or "unnamed-run",
        "split": split or "unspecified",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runtime_sec": runtime_sec,
    }
    report_warnings = list(warnings or [])
    if cache_summary and cache_summary.get("warnings"):
        report_warnings.extend(f"cache:{warning}" for warning in cache_summary["warnings"])

    return {
        "schema": {
            "name": "neurodecodekit-report",
            "version": 1,
        },
        "run": run,
        "summary": aggregate,
        "cache": cache_summary,
        "warnings": report_warnings,
        "examples": [example.to_dict() for example in examples[:max_examples]],
        "worst_examples": [example.to_dict() for example in worst_examples],
    }


def score_text_example(index: int, target: str, prediction: str) -> TextExampleScore:
    """Score one target/prediction pair."""

    normalized_target = normalize_text(target)
    normalized_prediction = normalize_text(prediction)
    target_words = normalized_target.split() if normalized_target else []
    prediction_words = normalized_prediction.split() if normalized_prediction else []
    return TextExampleScore(
        index=index,
        target=target,
        prediction=prediction,
        cer=_finite_or_none(character_error_rate(target, prediction)),
        wer=_finite_or_none(word_error_rate(target, prediction)),
        keyboard_distance=aligned_keyboard_distance(normalized_target, normalized_prediction),
        exact_match=sentence_exact_match(target, prediction),
        target_chars=len(normalized_target),
        prediction_chars=len(normalized_prediction),
        target_words=len(target_words),
        prediction_words=len(prediction_words),
    )


def aggregate_text_scores(examples: list[TextExampleScore]) -> dict[str, object]:
    """Aggregate per-example metrics into a compact report summary."""

    target_chars = sum(example.target_chars for example in examples)
    prediction_chars = sum(example.prediction_chars for example in examples)
    target_words = sum(example.target_words for example in examples)
    prediction_words = sum(example.prediction_words for example in examples)
    char_edits = 0
    word_edits = 0
    for example in examples:
        target = normalize_text(example.target)
        prediction = normalize_text(example.prediction)
        char_edits += levenshtein_distance(target, prediction)
        word_edits += levenshtein_distance(
            target.split() if target else [],
            prediction.split() if prediction else [],
        )

    exact_count = sum(1 for example in examples if example.exact_match)
    return {
        "n_examples": len(examples),
        "exact_match_count": exact_count,
        "exact_match_rate": exact_count / len(examples),
        "mean_cer": _mean_metric(example.cer for example in examples),
        "mean_wer": _mean_metric(example.wer for example in examples),
        "mean_keyboard_distance": _mean_metric(example.keyboard_distance for example in examples),
        "corpus_cer": char_edits / target_chars if target_chars else None,
        "corpus_wer": word_edits / target_words if target_words else None,
        "char_edits": char_edits,
        "word_edits": word_edits,
        "target_chars": target_chars,
        "prediction_chars": prediction_chars,
        "target_words": target_words,
        "prediction_words": prediction_words,
    }


def compare_paired_predictions(
    *,
    targets: Iterable[str],
    predictions_a: Iterable[str],
    predictions_b: Iterable[str],
    label_a: str,
    label_b: str,
    bootstrap_iterations: int = 5000,
    seed: int = 17,
) -> dict[str, object]:
    """Compare two prediction sets with a paired sentence bootstrap over CER."""

    target_rows = [normalize_text(str(value)) for value in targets]
    rows_a = [normalize_text(str(value)) for value in predictions_a]
    rows_b = [normalize_text(str(value)) for value in predictions_b]
    if not target_rows or not (len(target_rows) == len(rows_a) == len(rows_b)):
        raise ValueError("paired comparison requires equal non-empty row counts")
    if bootstrap_iterations < 100:
        raise ValueError("bootstrap_iterations must be >= 100")
    target_chars = [len(value) for value in target_rows]
    if sum(target_chars) == 0:
        raise ValueError("paired CER comparison requires at least one target character")
    edits_a = [
        levenshtein_distance(target, prediction)
        for target, prediction in zip(target_rows, rows_a, strict=True)
    ]
    edits_b = [
        levenshtein_distance(target, prediction)
        for target, prediction in zip(target_rows, rows_b, strict=True)
    ]
    observed_a = sum(edits_a) / sum(target_chars)
    observed_b = sum(edits_b) / sum(target_chars)
    rng = random.Random(seed)
    bootstrap_deltas = []
    for _ in range(bootstrap_iterations):
        sampled = [rng.randrange(len(target_rows)) for _ in target_rows]
        sampled_chars = sum(target_chars[index] for index in sampled)
        sampled_a = sum(edits_a[index] for index in sampled) / sampled_chars
        sampled_b = sum(edits_b[index] for index in sampled) / sampled_chars
        bootstrap_deltas.append(sampled_a - sampled_b)
    bootstrap_deltas.sort()
    lower_index = int(0.025 * (bootstrap_iterations - 1))
    upper_index = int(0.975 * (bootstrap_iterations - 1))
    wins = sum(a < b for a, b in zip(edits_a, edits_b, strict=True))
    ties = sum(a == b for a, b in zip(edits_a, edits_b, strict=True))
    losses = sum(a > b for a, b in zip(edits_a, edits_b, strict=True))
    return {
        "label_a": label_a,
        "label_b": label_b,
        "n_paired_sentences": len(target_rows),
        "corpus_cer_a": observed_a,
        "corpus_cer_b": observed_b,
        "corpus_cer_delta_a_minus_b": observed_a - observed_b,
        "char_edits_a": sum(edits_a),
        "char_edits_b": sum(edits_b),
        "char_edit_delta_a_minus_b": sum(edits_a) - sum(edits_b),
        "sentence_wins_a": wins,
        "sentence_ties": ties,
        "sentence_losses_a": losses,
        "paired_bootstrap_iterations": bootstrap_iterations,
        "paired_bootstrap_seed": seed,
        "paired_bootstrap_delta_ci95": [
            bootstrap_deltas[lower_index],
            bootstrap_deltas[upper_index],
        ],
        "bootstrap_probability_a_better": (
            sum(value < 0 for value in bootstrap_deltas) / bootstrap_iterations
        ),
        "interpretation_boundary": (
            "Sentence-level paired bootstrap; small partitions remain highly uncertain."
        ),
    }


def compare_paired_label_predictions(
    *,
    targets: Iterable[str],
    predictions_a: Iterable[str],
    predictions_b: Iterable[str],
    label_a: str,
    label_b: str,
    bootstrap_iterations: int = 5000,
    seed: int = 17,
) -> dict[str, object]:
    """Compare exact label correctness with a paired row bootstrap."""

    target_rows = [str(value) for value in targets]
    rows_a = [str(value) for value in predictions_a]
    rows_b = [str(value) for value in predictions_b]
    if not target_rows or not (len(target_rows) == len(rows_a) == len(rows_b)):
        raise ValueError("paired label comparison requires equal non-empty row counts")
    if bootstrap_iterations < 100:
        raise ValueError("bootstrap_iterations must be >= 100")

    correct_a = [target == prediction for target, prediction in zip(target_rows, rows_a)]
    correct_b = [target == prediction for target, prediction in zip(target_rows, rows_b)]
    accuracy_a = sum(correct_a) / len(correct_a)
    accuracy_b = sum(correct_b) / len(correct_b)
    rng = random.Random(seed)
    bootstrap_deltas = []
    for _ in range(bootstrap_iterations):
        sampled = [rng.randrange(len(target_rows)) for _ in target_rows]
        sampled_a = sum(correct_a[index] for index in sampled) / len(sampled)
        sampled_b = sum(correct_b[index] for index in sampled) / len(sampled)
        bootstrap_deltas.append(sampled_a - sampled_b)
    bootstrap_deltas.sort()
    lower_index = int(0.025 * (bootstrap_iterations - 1))
    upper_index = int(0.975 * (bootstrap_iterations - 1))
    wins = sum(a and not b for a, b in zip(correct_a, correct_b, strict=True))
    ties = sum(a == b for a, b in zip(correct_a, correct_b, strict=True))
    losses = sum(not a and b for a, b in zip(correct_a, correct_b, strict=True))
    return {
        "metric_kind": "label_accuracy",
        "label_a": label_a,
        "label_b": label_b,
        "n_paired_labels": len(target_rows),
        "label_accuracy_a": accuracy_a,
        "label_accuracy_b": accuracy_b,
        "label_accuracy_delta_a_minus_b": accuracy_a - accuracy_b,
        "label_errors_a": len(target_rows) - sum(correct_a),
        "label_errors_b": len(target_rows) - sum(correct_b),
        "paired_label_wins_a": wins,
        "paired_label_ties": ties,
        "paired_label_losses_a": losses,
        "paired_bootstrap_iterations": bootstrap_iterations,
        "paired_bootstrap_seed": seed,
        "paired_bootstrap_delta_ci95": [
            bootstrap_deltas[lower_index],
            bootstrap_deltas[upper_index],
        ],
        "bootstrap_probability_a_better": (
            sum(value > 0 for value in bootstrap_deltas) / bootstrap_iterations
        ),
        "interpretation_boundary": (
            "Paired event-label bootstrap within one session; this does not establish "
            "cross-session or cross-subject generalization."
        ),
    }


def render_report_markdown(report: dict[str, Any]) -> str:
    """Render a report dictionary as lightweight Markdown."""

    run = report["run"]
    summary = report["summary"]
    lines = [
        "# NeuroDecodeKit Report",
        "",
        f"- Run: `{_md_inline(run['name'])}`",
        f"- Split: `{_md_inline(run['split'])}`",
        f"- Created UTC: `{_md_inline(run['created_at_utc'])}`",
        f"- Runtime seconds: `{_format_metric(run.get('runtime_sec'))}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in (
        "primary_metric",
        "label_accuracy",
        "label_error_count",
        "n_examples",
        "exact_match_rate",
        "corpus_cer",
        "corpus_wer",
        "mean_cer",
        "mean_wer",
        "mean_keyboard_distance",
        "char_edits",
        "word_edits",
    ):
        lines.append(f"| `{key}` | {_format_metric(summary.get(key))} |")

    cache = report.get("cache")
    if cache:
        cache_shape = cache.get("windows_shape", cache.get("signals_shape"))
        lines.extend(
            [
                "",
                "## Cache",
                "",
                f"- Path: `{_md_inline(cache.get('path', ''))}`",
                f"- Kind: `{_md_inline(cache.get('kind', 'unknown'))}`",
                f"- Shape: `{_md_inline(str(cache_shape))}`",
                f"- Bytes: `{_format_metric(cache.get('bytes'))}`",
            ]
        )

    baseline = report.get("baseline")
    if baseline:
        lines.extend(["", "## Baseline", ""])
        lines.append(f"- Kind: `{_md_inline(str(baseline.get('kind', 'unknown')))}`")
        lines.append(f"- Strategy: `{_md_inline(str(baseline.get('strategy', 'unknown')))}`")
        if baseline.get("model_name") is not None:
            lines.append(f"- Model: `{_md_inline(str(baseline.get('model_name')))}`")
        if "uses_neural_windows" in baseline:
            lines.append(f"- Uses neural windows: `{_format_bool_or_unknown(baseline.get('uses_neural_windows'))}`")
        if baseline.get("kind") == "prior-only":
            lines.append("- No neural signal: `yes`")
        if "no_deep_learning" in baseline:
            lines.append(f"- No deep learning: `{_format_bool_or_unknown(baseline.get('no_deep_learning'))}`")
        if "uses_deep_learning" in baseline:
            lines.append(f"- Uses deep learning: `{_format_bool_or_unknown(baseline.get('uses_deep_learning'))}`")
        if baseline.get("split_mode") is not None:
            lines.append(f"- Split mode: `{_md_inline(str(baseline.get('split_mode')))}`")
        lines.append(f"- Train rows: `{_format_metric(baseline.get('n_train_rows'))}`")
        lines.append(f"- Eval rows: `{_format_metric(baseline.get('n_eval_rows'))}`")
        vocab_size = baseline.get("vocab_size", baseline.get("n_classes"))
        lines.append(f"- Vocabulary size: `{_format_metric(vocab_size)}`")
        if baseline.get("epochs") is not None:
            lines.append(f"- Epochs: `{_format_metric(baseline.get('epochs'))}`")
        if baseline.get("learning_rate") is not None:
            lines.append(f"- Learning rate: `{_format_metric(baseline.get('learning_rate'))}`")
        if baseline.get("device") is not None:
            lines.append(f"- Device: `{_md_inline(str(baseline.get('device')))}`")
        if baseline.get("train_accuracy") is not None:
            lines.append(f"- Train accuracy: `{_format_metric(baseline.get('train_accuracy'))}`")
        if baseline.get("eval_accuracy") is not None:
            lines.append(f"- Eval accuracy: `{_format_metric(baseline.get('eval_accuracy'))}`")
        if baseline.get("parameter_count") is not None:
            lines.append(f"- Parameters: `{_format_metric(baseline.get('parameter_count'))}`")
        if baseline.get("train_cer") is not None:
            lines.append(f"- Train CER: `{_format_metric(baseline.get('train_cer'))}`")
        if baseline.get("eval_cer") is not None:
            lines.append(f"- Eval CER: `{_format_metric(baseline.get('eval_cer'))}`")
        if baseline.get("eval_blank_fraction") is not None:
            lines.append(
                f"- Eval blank fraction: `{_format_metric(baseline.get('eval_blank_fraction'))}`"
            )
        if baseline.get("causal") is not None:
            lines.append(f"- Causal: `{_format_bool_or_unknown(baseline.get('causal'))}`")
        if baseline.get("top_target") not in (None, ""):
            lines.append(f"- Top target: `{_md_inline(str(baseline.get('top_target')))}`")
        if baseline.get("top_count") is not None:
            lines.append(f"- Top count: `{_format_metric(baseline.get('top_count'))}`")

    split_protocol = report.get("split_protocol")
    if split_protocol:
        lines.extend(
            [
                "",
                "## Split Protocol",
                "",
                f"- Evaluation partition: `{_md_inline(str(split_protocol.get('eval_partition')))}`",
                f"- Train rows: `{len(split_protocol.get('train_indices') or [])}`",
                f"- Validation rows: `{len(split_protocol.get('validation_indices') or [])}`",
                f"- Test rows: `{len(split_protocol.get('test_indices') or [])}`",
                "- Signal arrays loaded by membership reader: "
                f"`{_format_bool_or_unknown(split_protocol.get('signal_array_members_loaded'))}`",
                "- Protocol config SHA-256: "
                f"`{_md_inline(str(split_protocol.get('protocol_config_sha256')))}`",
                "- Semantic membership SHA-256: "
                f"`{_md_inline(str(split_protocol.get('semantic_membership_sha256')))}`",
            ]
        )

    comparators = report.get("comparators") or {}
    if comparators:
        lines.extend(["", "## Comparators", ""])
        for name, comparator in comparators.items():
            comparator_summary = comparator.get("summary") or {}
            if comparator_summary.get("primary_metric") == "label_accuracy":
                lines.append(
                    f"- `{_md_inline(str(name))}` label accuracy: "
                    f"`{_format_metric(comparator_summary.get('label_accuracy'))}`"
                )
            else:
                lines.append(
                    f"- `{_md_inline(str(name))}` corpus CER: "
                    f"`{_format_metric(comparator_summary.get('corpus_cer'))}`"
                )

    comparisons = report.get("comparisons") or {}
    if comparisons:
        lines.extend(["", "## Paired Comparisons", ""])
        for name, comparison in comparisons.items():
            interval = comparison.get("paired_bootstrap_delta_ci95") or [None, None]
            if comparison.get("metric_kind") == "label_accuracy":
                lines.extend(
                    [
                        f"### {_md_inline(str(name))}",
                        "",
                        "- Label accuracy delta (A minus B): "
                        f"`{_format_metric(comparison.get('label_accuracy_delta_a_minus_b'))}`",
                        "- Label accuracy A/B: "
                        f"`{_format_metric(comparison.get('label_accuracy_a'))}/"
                        f"{_format_metric(comparison.get('label_accuracy_b'))}`",
                        "- Paired label wins/ties/losses for A: "
                        f"`{comparison.get('paired_label_wins_a')}/"
                        f"{comparison.get('paired_label_ties')}/"
                        f"{comparison.get('paired_label_losses_a')}`",
                        "- Paired bootstrap 95% interval: "
                        f"`[{_format_metric(interval[0])}, {_format_metric(interval[1])}]`",
                    ]
                )
                continue
            lines.extend(
                [
                    f"### {_md_inline(str(name))}",
                    "",
                    "- Corpus CER delta (A minus B): "
                    f"`{_format_metric(comparison.get('corpus_cer_delta_a_minus_b'))}`",
                    "- Character-edit delta (A minus B): "
                    f"`{_format_metric(comparison.get('char_edit_delta_a_minus_b'))}`",
                    "- Sentence wins/ties/losses for A: "
                    f"`{comparison.get('sentence_wins_a')}/"
                    f"{comparison.get('sentence_ties')}/"
                    f"{comparison.get('sentence_losses_a')}`",
                    "- Paired bootstrap 95% interval: "
                    f"`[{_format_metric(interval[0])}, {_format_metric(interval[1])}]`",
                ]
            )

    warnings = report.get("warnings") or []
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- `{_md_inline(str(warning))}`" for warning in warnings)

    lines.extend(
        [
            "",
            "## Examples",
            "",
            "| # | Target | Prediction | CER | WER | Keyboard | Exact |",
            "|---:|---|---|---:|---:|---:|---|",
        ]
    )
    for example in report.get("examples", []):
        lines.append(
            "| {index} | {target} | {prediction} | {cer} | {wer} | {keyboard} | {exact} |".format(
                index=example["index"],
                target=_md_cell(example["target"]),
                prediction=_md_cell(example["prediction"]),
                cer=_format_metric(example["cer"]),
                wer=_format_metric(example["wer"]),
                keyboard=_format_metric(example["keyboard_distance"]),
                exact="yes" if example["exact_match"] else "no",
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_report_json(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report_markdown(report: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_report_markdown(report), encoding="utf-8")


def _mean_metric(values: Iterable[float | None]) -> float | None:
    finite = [float(value) for value in values if value is not None and math.isfinite(float(value))]
    if not finite:
        return None
    return sum(finite) / len(finite)


def _finite_or_none(value: float) -> float | None:
    return value if math.isfinite(value) else None


def _sort_metric(value: float | None) -> float:
    return -1.0 if value is None else float(value)


def _format_metric(value: object) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value)


def _format_bool_or_unknown(value: object) -> str:
    if value is True:
        return "yes"
    if value is False:
        return "no"
    return "unknown"


def _md_cell(value: object) -> str:
    return _md_inline(str(value)).replace("\n", " ").replace("|", "\\|")


def _md_inline(value: str) -> str:
    return value.replace("`", "'")
