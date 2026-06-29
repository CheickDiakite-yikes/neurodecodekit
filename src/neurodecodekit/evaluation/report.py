"""Report-card utilities for tiny neural decoding loops."""

from __future__ import annotations

import json
import math
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
        lines.extend(
            [
                "",
                "## Cache",
                "",
                f"- Path: `{_md_inline(cache.get('path', ''))}`",
                f"- Kind: `{_md_inline(cache.get('kind', 'unknown'))}`",
                f"- Shape: `{_md_inline(str(cache.get('windows_shape')))}`",
                f"- Bytes: `{_format_metric(cache.get('bytes'))}`",
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


def _md_cell(value: object) -> str:
    return _md_inline(str(value)).replace("\n", " ").replace("|", "\\|")


def _md_inline(value: str) -> str:
    return value.replace("`", "'")
