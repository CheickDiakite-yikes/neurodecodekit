"""Sequence and partial-hypothesis metrics for synthetic incremental CTC."""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Sequence

from neurodecodekit.evaluation.metrics import levenshtein_distance


def fit_most_frequent_sequence_prior(
    targets: Iterable[Sequence[int]],
) -> tuple[int, ...]:
    """Fit one signal-free complete-sequence prior with lexical tie breaking."""

    rows = [tuple(int(value) for value in target) for target in targets]
    if not rows or any(not row for row in rows):
        raise ValueError("sequence prior requires nonempty target sequences")
    counts = Counter(rows)
    best_count = max(counts.values())
    return min(row for row, count in counts.items() if count == best_count)


def sequence_metrics(
    targets: Iterable[Sequence[int]], predictions: Iterable[Sequence[int]]
) -> dict[str, object]:
    """Compute aggregate CER, exactness, and adjacent-repeat reconstruction."""

    target_rows = [tuple(int(value) for value in row) for row in targets]
    prediction_rows = [tuple(int(value) for value in row) for row in predictions]
    if not target_rows or len(target_rows) != len(prediction_rows):
        raise ValueError("sequence metrics require equal nonempty target/prediction rows")
    if any(not row for row in target_rows):
        raise ValueError("sequence metric targets must be nonempty")
    edits = [
        levenshtein_distance(target, prediction)
        for target, prediction in zip(target_rows, prediction_rows)
    ]
    target_lengths = [len(row) for row in target_rows]
    exact = [target == prediction for target, prediction in zip(target_rows, prediction_rows)]
    repeated_pairs = 0
    reconstructed_pairs = 0
    for target, prediction in zip(target_rows, prediction_rows):
        for index in range(1, len(target)):
            if target[index] != target[index - 1]:
                continue
            repeated_pairs += 1
            if (
                index < len(prediction)
                and prediction[index - 1] == target[index - 1]
                and prediction[index] == target[index]
            ):
                reconstructed_pairs += 1
    if repeated_pairs < 1:
        raise ValueError("sequence metrics require at least one adjacent repeated pair")
    return {
        "items": len(target_rows),
        "target_tokens": sum(target_lengths),
        "edit_distance": sum(edits),
        "corpus_cer": sum(edits) / sum(target_lengths),
        "exact_items": sum(exact),
        "exact_sequence_accuracy": sum(exact) / len(exact),
        "per_item_cer": [
            edit / length for edit, length in zip(edits, target_lengths)
        ],
        "per_item_exact": exact,
        "repeated_pair_count": repeated_pairs,
        "repeated_pair_reconstructed": reconstructed_pairs,
        "repeated_pair_reconstruction_rate": reconstructed_pairs / repeated_pairs,
    }


def partial_hypothesis_metrics(
    partials: Sequence[Sequence[int]],
    *,
    final_hypothesis: Sequence[int],
    frame_end_samples: Sequence[int],
    availability_samples: Sequence[int],
    sampling_rate_hz: float,
    motif_end_samples: Sequence[int] | None = None,
    target: Sequence[int] | None = None,
) -> dict[str, object]:
    """Measure revisions and retrospective first/stable/final symbol timing."""

    trace = [tuple(int(value) for value in row) for row in partials]
    final = tuple(int(value) for value in final_hypothesis)
    frame_ends = [int(value) for value in frame_end_samples]
    availability = [int(value) for value in availability_samples]
    if (
        not trace
        or len(trace) != len(frame_ends)
        or len(trace) != len(availability)
    ):
        raise ValueError("partial metrics require aligned nonempty frame traces")
    if trace[-1] != final:
        raise ValueError("last partial hypothesis must equal the final hypothesis")
    if sampling_rate_hz <= 0:
        raise ValueError("sampling_rate_hz must be positive")
    if any(right < left for left, right in zip(frame_ends, frame_ends[1:])):
        raise ValueError("frame-end samples must be monotonic")
    if any(value < frame_end for value, frame_end in zip(availability, frame_ends)):
        raise ValueError("availability cannot precede frame end")

    previous: tuple[int, ...] = ()
    total_edit_operations = 0
    revision_events = 0
    prefix_correct_frames = 0
    longest_common_prefix = []
    changes = 0
    for current in trace:
        if current != previous:
            changes += 1
            total_edit_operations += levenshtein_distance(previous, current)
            pure_append = len(current) >= len(previous) and current[: len(previous)] == previous
            if not pure_append:
                revision_events += 1
        common = _longest_common_prefix_length(current, final)
        longest_common_prefix.append(common)
        if len(current) <= len(final) and current == final[: len(current)]:
            prefix_correct_frames += 1
        previous = current
    necessary_edits = len(final)
    spurious_edits = max(0, total_edit_operations - necessary_edits)
    edit_overhead = (
        spurious_edits / total_edit_operations if total_edit_operations else 0.0
    )

    target_row = tuple(int(value) for value in target) if target is not None else None
    motif_ends = (
        [int(value) for value in motif_end_samples]
        if motif_end_samples is not None
        else None
    )
    motif_alignment_available = bool(
        target_row is not None
        and motif_ends is not None
        and final == target_row
        and len(motif_ends) == len(final)
    )
    symbol_timing = []
    final_frame_index = len(trace) - 1
    for position, final_symbol in enumerate(final):
        first_emission = _first_index(trace, lambda row: len(row) > position)
        first_correct = _first_index(
            trace,
            lambda row: len(row) > position and row[position] == final_symbol,
        )
        stable_correct = _stable_prefix_index(trace, final, position)
        row = {
            "position": position,
            "symbol_id": final_symbol,
            "first_emission_frame": first_emission,
            "first_correct_frame": first_correct,
            "stable_correct_frame": stable_correct,
            "finalization_frame": final_frame_index,
            "first_emission_sec": frame_ends[first_emission] / sampling_rate_hz,
            "first_correct_sec": frame_ends[first_correct] / sampling_rate_hz,
            "stable_correct_sec": frame_ends[stable_correct] / sampling_rate_hz,
            "finalization_sec": availability[final_frame_index] / sampling_rate_hz,
            "first_emission_available_sec": (
                availability[first_emission] / sampling_rate_hz
            ),
            "first_correct_available_sec": (
                availability[first_correct] / sampling_rate_hz
            ),
            "stable_correct_available_sec": (
                availability[stable_correct] / sampling_rate_hz
            ),
            "correction_delay_sec": (
                availability[stable_correct] - availability[first_correct]
            )
            / sampling_rate_hz,
            "motif_timing_available": motif_alignment_available,
        }
        if motif_alignment_available and motif_ends is not None:
            row["motif_end_sec"] = motif_ends[position] / sampling_rate_hz
            row["stable_delay_from_motif_end_sec"] = (
                availability[stable_correct] - motif_ends[position]
            ) / sampling_rate_hz
        symbol_timing.append(row)
    return {
        "frames": len(trace),
        "partial_changes": changes,
        "revision_events": revision_events,
        "total_edit_operations": total_edit_operations,
        "necessary_final_edits": necessary_edits,
        "spurious_edit_operations": spurious_edits,
        "edit_overhead": edit_overhead,
        "prefix_correct_frame_fraction": prefix_correct_frames / len(trace),
        "longest_common_prefix_by_frame": longest_common_prefix,
        "symbol_timing": symbol_timing,
        "finalization_frame": final_frame_index,
        "finalization_available_sec": availability[final_frame_index]
        / sampling_rate_hz,
        "motif_timing_available": motif_alignment_available,
    }


def paired_cer_reduction_bootstrap(
    targets: Iterable[Sequence[int]],
    learned_predictions: Iterable[Sequence[int]],
    control_predictions: Iterable[Sequence[int]],
    *,
    resamples: int = 2000,
    seed: int = 2322,
) -> dict[str, object]:
    """Bootstrap item-level CER reduction: control CER minus learned CER."""

    if resamples < 1:
        raise ValueError("bootstrap resamples must be positive")
    target_rows = [tuple(int(value) for value in row) for row in targets]
    learned_rows = [tuple(int(value) for value in row) for row in learned_predictions]
    control_rows = [tuple(int(value) for value in row) for row in control_predictions]
    if (
        not target_rows
        or len(target_rows) != len(learned_rows)
        or len(target_rows) != len(control_rows)
    ):
        raise ValueError("bootstrap rows must be equal and nonempty")
    reductions = []
    for target, learned, control in zip(target_rows, learned_rows, control_rows):
        if not target:
            raise ValueError("bootstrap target rows must be nonempty")
        learned_cer = levenshtein_distance(target, learned) / len(target)
        control_cer = levenshtein_distance(target, control) / len(target)
        reductions.append(control_cer - learned_cer)
    np = _require_numpy()
    values = np.asarray(reductions, dtype="float64")
    rng = np.random.Generator(np.random.PCG64(seed))
    samples = np.empty(resamples, dtype="float64")
    for index in range(resamples):
        selected = rng.integers(0, len(values), size=len(values))
        samples[index] = values[selected].mean()
    return {
        "unit": "item",
        "items": len(values),
        "resamples": resamples,
        "seed": seed,
        "mean_cer_reduction": float(values.mean()),
        "per_item_cer_reduction": [float(value) for value in values.tolist()],
        "confidence_interval_95": [
            float(np.percentile(samples, 2.5)),
            float(np.percentile(samples, 97.5)),
        ],
    }


def _longest_common_prefix_length(left: Sequence[int], right: Sequence[int]) -> int:
    length = 0
    for left_value, right_value in zip(left, right):
        if left_value != right_value:
            break
        length += 1
    return length


def _first_index(rows, predicate) -> int:
    for index, row in enumerate(rows):
        if predicate(row):
            return index
    raise ValueError("final hypothesis symbol never appeared in the partial trace")


def _stable_prefix_index(
    rows: Sequence[tuple[int, ...]], final: tuple[int, ...], position: int
) -> int:
    expected = final[: position + 1]
    for index in range(len(rows)):
        if all(len(row) > position and row[: position + 1] == expected for row in rows[index:]):
            return index
    raise ValueError("final prefix never stabilized")


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Incremental CTC bootstrap requires NumPy.") from exc
    return np
