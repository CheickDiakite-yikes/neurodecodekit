"""Small session-alignment primitives with explicit fit provenance."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class SyntheticChannelShift:
    """Known diagonal affine shift used only for synthetic validation."""

    gains: tuple[float, ...]
    offsets: tuple[float, ...]
    seed: int
    gain_min: float
    gain_max: float
    offset_std: float

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "synthetic_diagonal_channel_affine",
            "gains": list(self.gains),
            "offsets": list(self.offsets),
            "seed": self.seed,
            "gain_min": self.gain_min,
            "gain_max": self.gain_max,
            "offset_std": self.offset_std,
            "uses_real_data": False,
        }


@dataclass(frozen=True)
class SyntheticChannelMixingShift:
    """Known stationary cross-channel shift for synthetic stress tests."""

    mixing_matrix: tuple[tuple[float, ...], ...]
    offsets: tuple[float, ...]
    seed: int
    cross_talk: float
    offset_std: float
    condition_number: float

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "synthetic_stationary_channel_mixing",
            "mixing_matrix": [list(row) for row in self.mixing_matrix],
            "offsets": list(self.offsets),
            "seed": self.seed,
            "cross_talk": self.cross_talk,
            "offset_std": self.offset_std,
            "condition_number": self.condition_number,
            "uses_real_data": False,
        }


@dataclass(frozen=True)
class SyntheticTimeVaryingShift:
    """Known within-row diagonal drift for synthetic stress tests."""

    start_gains: tuple[float, ...]
    end_gains: tuple[float, ...]
    start_offsets: tuple[float, ...]
    end_offsets: tuple[float, ...]
    seed: int
    gain_min: float
    gain_max: float
    gain_drift_std: float
    offset_std: float
    offset_drift_std: float

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": "synthetic_within_row_time_varying_diagonal",
            "start_gains": list(self.start_gains),
            "end_gains": list(self.end_gains),
            "start_offsets": list(self.start_offsets),
            "end_offsets": list(self.end_offsets),
            "seed": self.seed,
            "gain_min": self.gain_min,
            "gain_max": self.gain_max,
            "gain_drift_std": self.gain_drift_std,
            "offset_std": self.offset_std,
            "offset_drift_std": self.offset_drift_std,
            "uses_real_data": False,
        }


@dataclass(frozen=True)
class RobustChannelAffineState:
    """Unlabeled diagonal affine map from a target domain to a source domain."""

    source_center: tuple[float, ...]
    source_scale: tuple[float, ...]
    target_center: tuple[float, ...]
    target_scale: tuple[float, ...]
    source_fit_indices: tuple[int, ...]
    target_fit_indices: tuple[int, ...]
    source_valid_timepoints: int
    target_valid_timepoints: int
    epsilon: float
    source_zero_iqr_channels: int
    target_zero_iqr_channels: int

    @property
    def n_channels(self) -> int:
        return len(self.source_center)

    def to_dict(self) -> dict[str, object]:
        source_center = list(self.source_center)
        source_scale = list(self.source_scale)
        target_center = list(self.target_center)
        target_scale = list(self.target_scale)
        return {
            "schema": {"name": "robust-channel-affine-adapter", "version": 1},
            "formula": "((target - target_center) / target_scale) * source_scale + source_center",
            "n_channels": self.n_channels,
            "learned_parameter_count": 0,
            "fitted_state_scalar_count": self.n_channels * 4,
            "target_labels_used": False,
            "source_center": source_center,
            "source_scale": source_scale,
            "target_center": target_center,
            "target_scale": target_scale,
            "source_statistics_sha256": _statistics_sha256(
                source_center,
                source_scale,
            ),
            "target_statistics_sha256": _statistics_sha256(
                target_center,
                target_scale,
            ),
            "source_fit_indices": list(self.source_fit_indices),
            "target_fit_indices": list(self.target_fit_indices),
            "source_fit_rows": len(self.source_fit_indices),
            "target_fit_rows": len(self.target_fit_indices),
            "source_valid_timepoints": self.source_valid_timepoints,
            "target_valid_timepoints": self.target_valid_timepoints,
            "epsilon": self.epsilon,
            "source_zero_iqr_channels": self.source_zero_iqr_channels,
            "target_zero_iqr_channels": self.target_zero_iqr_channels,
        }


def make_synthetic_channel_shift(
    n_channels: int,
    *,
    seed: int,
    gain_min: float = 0.35,
    gain_max: float = 2.5,
    offset_std: float = 1.25,
) -> SyntheticChannelShift:
    """Create a deterministic positive-gain channel shift for a synthetic gate."""

    if n_channels < 1:
        raise ValueError("n_channels must be >= 1")
    if gain_min <= 0 or gain_max < gain_min:
        raise ValueError("gain bounds must satisfy 0 < gain_min <= gain_max")
    if offset_std < 0:
        raise ValueError("offset_std must be >= 0")
    np = _require_numpy()
    rng = np.random.default_rng(seed)
    gains = np.exp(
        rng.uniform(math.log(gain_min), math.log(gain_max), size=n_channels)
    ).astype("float32")
    offsets = rng.normal(0.0, offset_std, size=n_channels).astype("float32")
    return SyntheticChannelShift(
        gains=tuple(float(value) for value in gains.tolist()),
        offsets=tuple(float(value) for value in offsets.tolist()),
        seed=seed,
        gain_min=gain_min,
        gain_max=gain_max,
        offset_std=offset_std,
    )


def apply_synthetic_channel_shift(signals, input_lengths, shift: SyntheticChannelShift):
    """Apply a known shift only to valid samples and keep padding exactly zero."""

    np = _require_numpy()
    data, lengths, indices = _validated_signal_view(signals, input_lengths, None)
    if data.shape[1] != len(shift.gains):
        raise ValueError(
            "Synthetic shift channel count does not match signals: "
            f"{len(shift.gains)} vs {data.shape[1]}."
        )
    gains = np.asarray(shift.gains, dtype="float32")[:, None]
    offsets = np.asarray(shift.offsets, dtype="float32")[:, None]
    output = np.zeros(data.shape, dtype="float32")
    for row_index in indices:
        length = int(lengths[row_index])
        output[row_index, :, :length] = data[row_index, :, :length] * gains + offsets
    return output


def make_synthetic_channel_mixing_shift(
    n_channels: int,
    *,
    seed: int,
    cross_talk: float = 0.45,
    offset_std: float = 0.75,
) -> SyntheticChannelMixingShift:
    """Create a deterministic, well-conditioned cross-channel mixing shift."""

    if n_channels < 2:
        raise ValueError("channel mixing requires at least two channels")
    if not 0 < cross_talk < 1:
        raise ValueError("cross_talk must be between 0 and 1")
    if offset_std < 0:
        raise ValueError("offset_std must be >= 0")
    np = _require_numpy()
    rng = np.random.default_rng(seed)
    off_diagonal = rng.normal(0.0, 1.0, size=(n_channels, n_channels))
    np.fill_diagonal(off_diagonal, 0.0)
    row_norms = np.linalg.norm(off_diagonal, axis=1, keepdims=True)
    off_diagonal = np.divide(
        off_diagonal,
        row_norms,
        out=np.zeros_like(off_diagonal),
        where=row_norms > 0,
    )
    matrix = np.eye(n_channels) + cross_talk * off_diagonal
    offsets = rng.normal(0.0, offset_std, size=n_channels)
    condition_number = float(np.linalg.cond(matrix))
    return SyntheticChannelMixingShift(
        mixing_matrix=tuple(
            tuple(float(value) for value in row) for row in matrix.astype("float32")
        ),
        offsets=tuple(float(value) for value in offsets.astype("float32")),
        seed=seed,
        cross_talk=cross_talk,
        offset_std=offset_std,
        condition_number=condition_number,
    )


def apply_synthetic_channel_mixing_shift(
    signals,
    input_lengths,
    shift: SyntheticChannelMixingShift,
):
    """Apply stationary channel mixing to valid samples and preserve padding."""

    np = _require_numpy()
    data, lengths, indices = _validated_signal_view(signals, input_lengths, None)
    matrix = np.asarray(shift.mixing_matrix, dtype="float32")
    if matrix.shape != (data.shape[1], data.shape[1]):
        raise ValueError(
            "Mixing matrix must be square and match the signal channels: "
            f"{matrix.shape} vs {data.shape[1]}."
        )
    offsets = np.asarray(shift.offsets, dtype="float32")[:, None]
    output = np.zeros(data.shape, dtype="float32")
    for row_index in indices:
        length = int(lengths[row_index])
        output[row_index, :, :length] = (
            matrix @ data[row_index, :, :length] + offsets
        )
    return output


def make_synthetic_time_varying_shift(
    n_channels: int,
    *,
    seed: int,
    gain_min: float = 0.65,
    gain_max: float = 1.65,
    gain_drift_std: float = 0.45,
    offset_std: float = 0.55,
    offset_drift_std: float = 0.9,
) -> SyntheticTimeVaryingShift:
    """Create deterministic gain/offset drift over each valid synthetic row."""

    if n_channels < 1:
        raise ValueError("n_channels must be >= 1")
    if gain_min <= 0 or gain_max < gain_min:
        raise ValueError("gain bounds must satisfy 0 < gain_min <= gain_max")
    if gain_drift_std < 0 or offset_std < 0 or offset_drift_std < 0:
        raise ValueError("drift and offset standard deviations must be >= 0")
    np = _require_numpy()
    rng = np.random.default_rng(seed)
    start_gains = np.exp(
        rng.uniform(math.log(gain_min), math.log(gain_max), size=n_channels)
    )
    end_gains = start_gains * np.exp(
        rng.normal(0.0, gain_drift_std, size=n_channels)
    )
    start_offsets = rng.normal(0.0, offset_std, size=n_channels)
    end_offsets = start_offsets + rng.normal(
        0.0,
        offset_drift_std,
        size=n_channels,
    )
    return SyntheticTimeVaryingShift(
        start_gains=tuple(float(value) for value in start_gains.astype("float32")),
        end_gains=tuple(float(value) for value in end_gains.astype("float32")),
        start_offsets=tuple(float(value) for value in start_offsets.astype("float32")),
        end_offsets=tuple(float(value) for value in end_offsets.astype("float32")),
        seed=seed,
        gain_min=gain_min,
        gain_max=gain_max,
        gain_drift_std=gain_drift_std,
        offset_std=offset_std,
        offset_drift_std=offset_drift_std,
    )


def apply_synthetic_time_varying_shift(
    signals,
    input_lengths,
    shift: SyntheticTimeVaryingShift,
):
    """Apply linearly varying channel gains/offsets over valid samples only."""

    np = _require_numpy()
    data, lengths, indices = _validated_signal_view(signals, input_lengths, None)
    if data.shape[1] != len(shift.start_gains):
        raise ValueError(
            "Time-varying shift channel count does not match signals: "
            f"{len(shift.start_gains)} vs {data.shape[1]}."
        )
    start_gains = np.asarray(shift.start_gains, dtype="float32")[:, None]
    end_gains = np.asarray(shift.end_gains, dtype="float32")[:, None]
    start_offsets = np.asarray(shift.start_offsets, dtype="float32")[:, None]
    end_offsets = np.asarray(shift.end_offsets, dtype="float32")[:, None]
    output = np.zeros(data.shape, dtype="float32")
    for row_index in indices:
        length = int(lengths[row_index])
        alpha = np.linspace(0.0, 1.0, num=length, dtype="float32")[None, :]
        gains = start_gains + alpha * (end_gains - start_gains)
        offsets = start_offsets + alpha * (end_offsets - start_offsets)
        output[row_index, :, :length] = (
            data[row_index, :, :length] * gains + offsets
        )
    return output


def fit_robust_channel_affine(
    *,
    source_signals,
    source_input_lengths,
    target_calibration_signals,
    target_input_lengths,
    source_fit_indices: Iterable[int] | None = None,
    target_fit_indices: Iterable[int] | None = None,
    epsilon: float = 1e-6,
) -> RobustChannelAffineState:
    """Fit source and target median/IQR statistics without target labels."""

    if epsilon <= 0:
        raise ValueError("epsilon must be > 0")
    source, source_lengths, source_indices = _validated_signal_view(
        source_signals,
        source_input_lengths,
        source_fit_indices,
    )
    target, target_lengths, target_indices = _validated_signal_view(
        target_calibration_signals,
        target_input_lengths,
        target_fit_indices,
    )
    if source.shape[1] != target.shape[1]:
        raise ValueError(
            "Source and target calibration signals must have equal channel counts: "
            f"{source.shape[1]} vs {target.shape[1]}."
        )
    source_center, source_scale, source_zero = _channel_robust_statistics(
        source,
        source_lengths,
        source_indices,
        epsilon=epsilon,
    )
    target_center, target_scale, target_zero = _channel_robust_statistics(
        target,
        target_lengths,
        target_indices,
        epsilon=epsilon,
    )
    return RobustChannelAffineState(
        source_center=tuple(float(value) for value in source_center.tolist()),
        source_scale=tuple(float(value) for value in source_scale.tolist()),
        target_center=tuple(float(value) for value in target_center.tolist()),
        target_scale=tuple(float(value) for value in target_scale.tolist()),
        source_fit_indices=tuple(source_indices),
        target_fit_indices=tuple(target_indices),
        source_valid_timepoints=sum(int(source_lengths[index]) for index in source_indices),
        target_valid_timepoints=sum(int(target_lengths[index]) for index in target_indices),
        epsilon=epsilon,
        source_zero_iqr_channels=source_zero,
        target_zero_iqr_channels=target_zero,
    )


def apply_robust_channel_affine(signals, input_lengths, state: RobustChannelAffineState):
    """Map valid target samples to source robust statistics and zero padding."""

    np = _require_numpy()
    data, lengths, indices = _validated_signal_view(signals, input_lengths, None)
    if data.shape[1] != state.n_channels:
        raise ValueError(
            "Adapter channel count does not match signals: "
            f"{state.n_channels} vs {data.shape[1]}."
        )
    source_center = np.asarray(state.source_center, dtype="float32")[:, None]
    source_scale = np.asarray(state.source_scale, dtype="float32")[:, None]
    target_center = np.asarray(state.target_center, dtype="float32")[:, None]
    target_scale = np.asarray(state.target_scale, dtype="float32")[:, None]
    output = np.zeros(data.shape, dtype="float32")
    for row_index in indices:
        length = int(lengths[row_index])
        valid = data[row_index, :, :length]
        output[row_index, :, :length] = (
            (valid - target_center) / target_scale * source_scale + source_center
        )
    return output


def summarize_signal_reconstruction(reference, candidate, input_lengths) -> dict[str, float | int]:
    """Measure reconstruction error over valid samples only."""

    np = _require_numpy()
    reference_data, lengths, indices = _validated_signal_view(reference, input_lengths, None)
    candidate_data, candidate_lengths, _ = _validated_signal_view(
        candidate,
        input_lengths,
        None,
    )
    if reference_data.shape != candidate_data.shape:
        raise ValueError("Reference and candidate signals must have equal shapes.")
    if not np.array_equal(lengths, candidate_lengths):
        raise ValueError("Reference and candidate input lengths must match.")
    absolute_sum = 0.0
    squared_sum = 0.0
    max_absolute = 0.0
    value_count = 0
    for row_index in indices:
        length = int(lengths[row_index])
        difference = (
            candidate_data[row_index, :, :length] - reference_data[row_index, :, :length]
        ).astype("float64", copy=False)
        absolute = np.abs(difference)
        absolute_sum += float(absolute.sum())
        squared_sum += float(np.square(difference).sum())
        max_absolute = max(max_absolute, float(absolute.max(initial=0.0)))
        value_count += int(difference.size)
    return {
        "valid_value_count": value_count,
        "mae": absolute_sum / value_count,
        "rmse": math.sqrt(squared_sum / value_count),
        "max_abs_error": max_absolute,
    }


def padding_is_zero(signals, input_lengths) -> bool:
    """Return whether every padded sample is exactly zero."""

    np = _require_numpy()
    data, lengths, indices = _validated_signal_view(signals, input_lengths, None)
    return all(np.all(data[index, :, int(lengths[index]) :] == 0) for index in indices)


def _channel_robust_statistics(data, lengths, indices, *, epsilon: float):
    np = _require_numpy()
    centers = []
    scales = []
    zero_iqr = 0
    for channel_index in range(data.shape[1]):
        values = np.concatenate(
            [
                data[row_index, channel_index, : int(lengths[row_index])]
                for row_index in indices
            ]
        ).astype("float64", copy=False)
        q25, median, q75 = np.quantile(values, [0.25, 0.5, 0.75])
        scale = float(q75 - q25)
        if not math.isfinite(scale) or scale < epsilon:
            scale = 1.0
            zero_iqr += 1
        centers.append(float(median))
        scales.append(scale)
    return (
        np.asarray(centers, dtype="float32"),
        np.asarray(scales, dtype="float32"),
        zero_iqr,
    )


def _validated_signal_view(signals, input_lengths, indices: Iterable[int] | None):
    np = _require_numpy()
    data = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if data.ndim != 3:
        raise ValueError(f"signals must be [rows, channels, time], got {data.shape}")
    if lengths.ndim != 1 or len(lengths) != data.shape[0]:
        raise ValueError("input_lengths must contain one value per signal row")
    if np.any(lengths < 1) or np.any(lengths > data.shape[2]):
        raise ValueError("input_lengths must be between 1 and the padded signal width")
    selected = list(range(data.shape[0])) if indices is None else [int(value) for value in indices]
    if not selected:
        raise ValueError("at least one fit row is required")
    if len(set(selected)) != len(selected):
        raise ValueError("fit indices must be unique")
    if min(selected) < 0 or max(selected) >= data.shape[0]:
        raise ValueError("fit indices are outside the signal row range")
    return data, lengths, selected


def _statistics_sha256(center: list[float], scale: list[float]) -> str:
    np = _require_numpy()
    values = np.asarray([center, scale], dtype="<f8")
    return hashlib.sha256(values.tobytes(order="C")).hexdigest()


def _require_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Session adapters require NumPy: `pip install numpy`.") from exc
    return np
