"""Window extraction helpers for event-aligned neural data."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class WindowSpec:
    """Configuration for event-aligned windows."""

    sfreq: float
    tmin: float = -0.2
    tmax: float = 0.3

    def __post_init__(self) -> None:
        if self.sfreq <= 0:
            raise ValueError("sfreq must be > 0")
        if self.tmax <= self.tmin:
            raise ValueError("tmax must be greater than tmin")

    @property
    def n_times(self) -> int:
        return int(round((self.tmax - self.tmin) * self.sfreq))


@dataclass(frozen=True)
class DroppedWindow:
    """One event that could not be windowed."""

    event_index: int
    reason: str
    start_sample: int
    stop_sample: int


@dataclass(frozen=True)
class WindowBounds:
    """Sample bounds for event-aligned extraction."""

    event_index: int
    start_sample: int
    stop_sample: int


@dataclass(frozen=True)
class WindowExtractionResult:
    """Event-window extraction output plus keep/drop bookkeeping."""

    windows: object
    kept_event_indices: list[int]
    dropped: list[DroppedWindow]

    @property
    def dropped_by_reason(self) -> dict[str, int]:
        return dict(Counter(drop.reason for drop in self.dropped))


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Window extraction requires NumPy: `pip install numpy`.") from exc
    return np


def event_sample_indices(event_times_sec: Sequence[float], sfreq: float) -> list[int]:
    """Convert event times in seconds to sample indices."""

    return [int(round(t * sfreq)) for t in event_times_sec]


def window_bounds_for_events(
    event_times_sec: Sequence[float],
    spec: WindowSpec,
    *,
    n_samples: int,
) -> tuple[list[WindowBounds], list[DroppedWindow]]:
    """Return sample windows and edge-drop reasons for event times."""

    start_offset = int(round(spec.tmin * spec.sfreq))
    n_times = spec.n_times
    event_samples = event_sample_indices(event_times_sec, spec.sfreq)

    kept: list[WindowBounds] = []
    dropped: list[DroppedWindow] = []
    for event_i, center in enumerate(event_samples):
        start = center + start_offset
        stop = start + n_times
        if start < 0:
            dropped.append(DroppedWindow(event_i, "before_start", start, stop))
            continue
        if stop > n_samples:
            dropped.append(DroppedWindow(event_i, "after_end", start, stop))
            continue
        kept.append(WindowBounds(event_i, start, stop))
    return kept, dropped


def extract_windows_from_array(
    data,
    event_times_sec: Sequence[float],
    spec: WindowSpec,
    *,
    channel_axis: int = 0,
):
    """Extract fixed windows around event times from an array.

    Parameters
    ----------
    data:
        Array shaped `[channels, times]` by default.
    event_times_sec:
        Event onset times in seconds.
    spec:
        Window configuration.
    channel_axis:
        Currently only `0` is supported in v0.

    Returns
    -------
    windows:
        NumPy array shaped `[n_events_kept, n_channels, n_times]`.
    kept_event_indices:
        Original event indices that did not fall off the data edges.
    """

    result = extract_windows_from_array_with_report(
        data,
        event_times_sec,
        spec,
        channel_axis=channel_axis,
    )
    return result.windows, result.kept_event_indices


def extract_windows_from_array_with_report(
    data,
    event_times_sec: Sequence[float],
    spec: WindowSpec,
    *,
    channel_axis: int = 0,
) -> WindowExtractionResult:
    """Extract event windows and return explicit keep/drop metadata."""

    if channel_axis != 0:
        raise NotImplementedError("v0 only supports channel_axis=0")

    np = _require_numpy()
    arr = np.asarray(data)
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D array [channels, times], got shape {arr.shape}")

    n_times = spec.n_times
    bounds, dropped = window_bounds_for_events(event_times_sec, spec, n_samples=arr.shape[1])

    windows = []
    kept = []
    for bound in bounds:
        windows.append(arr[:, bound.start_sample : bound.stop_sample])
        kept.append(bound.event_index)

    if not windows:
        empty = np.empty((0, arr.shape[0], n_times), dtype=arr.dtype)
        return WindowExtractionResult(empty, kept, dropped)
    return WindowExtractionResult(np.stack(windows, axis=0), kept, dropped)
