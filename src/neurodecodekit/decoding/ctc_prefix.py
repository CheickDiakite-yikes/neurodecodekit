"""Dependency-free incremental CTC greedy and prefix-beam decoding."""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import Iterable, Sequence


NEGATIVE_INFINITY = float("-inf")


@dataclass(frozen=True)
class GreedyCTCSnapshot:
    """One frame-indexed greedy CTC partial hypothesis."""

    frame_index: int
    path_class: int
    hypothesis: tuple[int, ...]
    state_payload_bytes: int


@dataclass(frozen=True)
class PrefixBeamSnapshot:
    """One frame-indexed top prefix and bounded decoder-state accounting."""

    frame_index: int
    top_prefix: tuple[int, ...]
    top_log_probability: float
    beam_size: int
    state_payload_bytes: int


def ctc_collapse(path: Iterable[int], *, blank_id: int = 0) -> tuple[int, ...]:
    """Collapse adjacent path repeats, then remove blanks."""

    if blank_id < 0:
        raise ValueError("blank_id must be nonnegative")
    output: list[int] = []
    previous: int | None = None
    for raw_value in path:
        value = int(raw_value)
        if value < 0:
            raise ValueError("CTC path classes must be nonnegative")
        if value != blank_id and value != previous:
            output.append(value)
        previous = value
    return tuple(output)


class GreedyCTCDecoder:
    """Incremental argmax path decoder with explicit blank/repeat state."""

    def __init__(self, *, blank_id: int = 0, max_output_length: int = 12) -> None:
        if blank_id < 0:
            raise ValueError("blank_id must be nonnegative")
        if max_output_length < 1:
            raise ValueError("max_output_length must be positive")
        self.blank_id = int(blank_id)
        self.max_output_length = int(max_output_length)
        self.previous_path_class: int | None = None
        self.output: list[int] = []
        self.frame_count = 0
        self.closed = False
        self.max_state_payload_bytes = self.state_payload_bytes

    @property
    def state_payload_bytes(self) -> int:
        # int32 frame index, int16 previous class, int16 output tokens.
        return 4 + 2 + 2 * len(self.output)

    def push(self, log_probabilities: Sequence[float]) -> GreedyCTCSnapshot:
        values = _validate_log_probabilities(log_probabilities, blank_id=self.blank_id)
        if self.closed:
            raise RuntimeError("greedy CTC decoder is already closed")
        path_class = min(
            range(len(values)),
            key=lambda index: (-values[index], index),
        )
        if path_class != self.blank_id and path_class != self.previous_path_class:
            if len(self.output) >= self.max_output_length:
                raise ValueError("greedy CTC output exceeds maximum prefix length")
            self.output.append(path_class)
        self.previous_path_class = path_class
        snapshot = GreedyCTCSnapshot(
            frame_index=self.frame_count,
            path_class=path_class,
            hypothesis=tuple(self.output),
            state_payload_bytes=self.state_payload_bytes,
        )
        self.frame_count += 1
        self.max_state_payload_bytes = max(
            self.max_state_payload_bytes, self.state_payload_bytes
        )
        return snapshot

    def flush(self) -> tuple[int, ...]:
        if self.closed:
            raise RuntimeError("greedy CTC decoder is already closed")
        self.closed = True
        return tuple(self.output)


class PrefixBeamCTCDecoder:
    """Frame-synchronous CTC prefix beam with deterministic pruning."""

    def __init__(
        self,
        *,
        beam_width: int = 8,
        blank_id: int = 0,
        max_prefix_length: int = 12,
    ) -> None:
        if beam_width < 1 or beam_width > 65536:
            raise ValueError("beam_width must be between 1 and 65536")
        if blank_id < 0:
            raise ValueError("blank_id must be nonnegative")
        if max_prefix_length < 1 or max_prefix_length > 65536:
            raise ValueError("max_prefix_length must be between 1 and 65536")
        self.beam_width = int(beam_width)
        self.blank_id = int(blank_id)
        self.max_prefix_length = int(max_prefix_length)
        self.beams: dict[tuple[int, ...], tuple[float, float]] = {
            (): (0.0, NEGATIVE_INFINITY)
        }
        self.frame_count = 0
        self.n_classes: int | None = None
        self.closed = False
        self.max_state_payload_bytes = self.state_payload_bytes

    @property
    def state_payload_bytes(self) -> int:
        # int32 frame index plus, per beam, int16 length/tokens and 2 float64 scores.
        return 4 + sum(18 + 2 * len(prefix) for prefix in self.beams)

    def beam_scores(self) -> dict[tuple[int, ...], float]:
        return {
            prefix: _logaddexp(blank_score, nonblank_score)
            for prefix, (blank_score, nonblank_score) in self.beams.items()
        }

    def push(self, log_probabilities: Sequence[float]) -> PrefixBeamSnapshot:
        values = _validate_log_probabilities(log_probabilities, blank_id=self.blank_id)
        if self.closed:
            raise RuntimeError("prefix CTC decoder is already closed")
        if self.n_classes is None:
            self.n_classes = len(values)
        elif len(values) != self.n_classes:
            raise ValueError("CTC class count changed within one stream")

        next_beams: dict[tuple[int, ...], tuple[float, float]] = {}
        for prefix, (prob_blank, prob_nonblank) in self.beams.items():
            total = _logaddexp(prob_blank, prob_nonblank)
            _accumulate(
                next_beams,
                prefix,
                blank_score=total + values[self.blank_id],
            )
            final_symbol = prefix[-1] if prefix else None
            for symbol, log_probability in enumerate(values):
                if symbol == self.blank_id:
                    continue
                if symbol == final_symbol:
                    _accumulate(
                        next_beams,
                        prefix,
                        nonblank_score=prob_nonblank + log_probability,
                    )
                    if len(prefix) < self.max_prefix_length:
                        _accumulate(
                            next_beams,
                            prefix + (symbol,),
                            nonblank_score=prob_blank + log_probability,
                        )
                elif len(prefix) < self.max_prefix_length:
                    _accumulate(
                        next_beams,
                        prefix + (symbol,),
                        nonblank_score=total + log_probability,
                    )

        reachable = [
            item
            for item in next_beams.items()
            if _logaddexp(item[1][0], item[1][1]) != NEGATIVE_INFINITY
        ]
        ranked = sorted(
            reachable,
            key=lambda item: (
                -_logaddexp(item[1][0], item[1][1]),
                item[0],
            ),
        )
        self.beams = dict(ranked[: self.beam_width])
        if not self.beams:
            raise RuntimeError("prefix CTC beam became empty")
        top_prefix, (top_blank, top_nonblank) = next(iter(self.beams.items()))
        snapshot = PrefixBeamSnapshot(
            frame_index=self.frame_count,
            top_prefix=top_prefix,
            top_log_probability=_logaddexp(top_blank, top_nonblank),
            beam_size=len(self.beams),
            state_payload_bytes=self.state_payload_bytes,
        )
        self.frame_count += 1
        self.max_state_payload_bytes = max(
            self.max_state_payload_bytes, self.state_payload_bytes
        )
        return snapshot

    def flush(self) -> tuple[int, ...]:
        if self.closed:
            raise RuntimeError("prefix CTC decoder is already closed")
        self.closed = True
        return next(iter(self.beams))


def prefix_beam_decode(
    log_probabilities: Iterable[Sequence[float]],
    *,
    beam_width: int = 8,
    blank_id: int = 0,
    max_prefix_length: int = 12,
) -> tuple[int, ...]:
    decoder = PrefixBeamCTCDecoder(
        beam_width=beam_width,
        blank_id=blank_id,
        max_prefix_length=max_prefix_length,
    )
    for frame in log_probabilities:
        decoder.push(frame)
    return decoder.flush()


def exhaustive_ctc_distribution(
    log_probabilities: Sequence[Sequence[float]],
    *,
    blank_id: int = 0,
    max_paths: int = 100_000,
) -> dict[tuple[int, ...], float]:
    """Enumerate tiny CTC paths for an independent test oracle."""

    frames = [
        _validate_log_probabilities(frame, blank_id=blank_id)
        for frame in log_probabilities
    ]
    if not frames:
        return {(): 0.0}
    n_classes = len(frames[0])
    if any(len(frame) != n_classes for frame in frames):
        raise ValueError("CTC class count changed across exhaustive frames")
    path_count = n_classes ** len(frames)
    if path_count > max_paths:
        raise ValueError(
            f"exhaustive CTC oracle needs {path_count} paths, exceeding {max_paths}"
        )
    distribution: dict[tuple[int, ...], float] = {}
    for path in itertools.product(range(n_classes), repeat=len(frames)):
        score = sum(frames[index][symbol] for index, symbol in enumerate(path))
        collapsed = ctc_collapse(path, blank_id=blank_id)
        distribution[collapsed] = _logaddexp(
            distribution.get(collapsed, NEGATIVE_INFINITY), score
        )
    return distribution


def _accumulate(
    beams: dict[tuple[int, ...], tuple[float, float]],
    prefix: tuple[int, ...],
    *,
    blank_score: float = NEGATIVE_INFINITY,
    nonblank_score: float = NEGATIVE_INFINITY,
) -> None:
    old_blank, old_nonblank = beams.get(
        prefix, (NEGATIVE_INFINITY, NEGATIVE_INFINITY)
    )
    beams[prefix] = (
        _logaddexp(old_blank, blank_score),
        _logaddexp(old_nonblank, nonblank_score),
    )


def _validate_log_probabilities(
    values: Sequence[float], *, blank_id: int
) -> tuple[float, ...]:
    normalized = tuple(float(value) for value in values)
    if len(normalized) < 2:
        raise ValueError("CTC frame must contain blank and at least one label")
    if blank_id >= len(normalized):
        raise ValueError("blank_id falls outside the CTC class vector")
    if any(math.isnan(value) or value == float("inf") for value in normalized):
        raise ValueError("CTC log probabilities contain NaN or positive infinity")
    if all(value == NEGATIVE_INFINITY for value in normalized):
        raise ValueError("CTC frame cannot assign zero probability to every class")
    return normalized


def _logaddexp(left: float, right: float) -> float:
    if left == NEGATIVE_INFINITY:
        return right
    if right == NEGATIVE_INFINITY:
        return left
    maximum = max(left, right)
    return maximum + math.log(math.exp(left - maximum) + math.exp(right - maximum))
