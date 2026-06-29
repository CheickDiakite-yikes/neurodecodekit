"""Text decoding metrics.

The first research loop should use simple, explicit metrics before adding model
complexity. Character error rate (CER) and word error rate (WER) are edit-distance
metrics normalized by target length.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def normalize_text(text: str, *, uppercase: bool = True, collapse_spaces: bool = True) -> str:
    """Normalize text for CER/WER comparisons.

    Parameters
    ----------
    text:
        Input string.
    uppercase:
        Whether to uppercase the text. Brain2Qwerty v1 used uppercase Spanish
        stimuli without accents in the task setup.
    collapse_spaces:
        Whether to strip and collapse repeated whitespace.
    """

    if uppercase:
        text = text.upper()
    if collapse_spaces:
        text = re.sub(r"\s+", " ", text.strip())
    return text


def levenshtein_distance(target: Sequence[T], prediction: Sequence[T]) -> int:
    """Compute Levenshtein edit distance between two sequences.

    This implementation is intentionally dependency-free so tests can run in
    constrained environments.
    """

    n = len(target)
    m = len(prediction)
    if n == 0:
        return m
    if m == 0:
        return n

    previous = list(range(m + 1))
    for i, target_item in enumerate(target, start=1):
        current = [i] + [0] * m
        for j, pred_item in enumerate(prediction, start=1):
            cost = 0 if target_item == pred_item else 1
            current[j] = min(
                previous[j] + 1,      # deletion
                current[j - 1] + 1,   # insertion
                previous[j - 1] + cost,
            )
        previous = current
    return previous[m]


def character_error_rate(
    target: str,
    prediction: str,
    *,
    normalize: bool = True,
    empty_target_value: float = 0.0,
) -> float:
    """Return character error rate as edit_distance / len(target)."""

    if normalize:
        target = normalize_text(target)
        prediction = normalize_text(prediction)
    if len(target) == 0:
        return empty_target_value if len(prediction) == 0 else float("inf")
    return levenshtein_distance(target, prediction) / len(target)


def word_error_rate(
    target: str,
    prediction: str,
    *,
    normalize: bool = True,
    empty_target_value: float = 0.0,
) -> float:
    """Return word error rate as word_edit_distance / number_of_target_words."""

    if normalize:
        target = normalize_text(target)
        prediction = normalize_text(prediction)
    target_words = target.split() if target else []
    pred_words = prediction.split() if prediction else []
    if len(target_words) == 0:
        return empty_target_value if len(pred_words) == 0 else float("inf")
    return levenshtein_distance(target_words, pred_words) / len(target_words)


def sentence_exact_match(target: str, prediction: str, *, normalize: bool = True) -> bool:
    """Return True if target and prediction match exactly after optional normalization."""

    if normalize:
        target = normalize_text(target)
        prediction = normalize_text(prediction)
    return target == prediction


def summarize_text_metrics(target: str, prediction: str) -> dict[str, float | bool]:
    """Return a small metrics dictionary for CLI/demo use."""

    return {
        "cer": character_error_rate(target, prediction),
        "wer": word_error_rate(target, prediction),
        "exact_match": sentence_exact_match(target, prediction),
    }
