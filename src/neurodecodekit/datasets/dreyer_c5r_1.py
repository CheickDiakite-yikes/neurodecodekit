"""Strict generated-fixture primitives for the DREYER-C5R-1 lane."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence


EXPECTED_SAMPLING_RATE_HZ = 512.0
BANDS_HZ = ((8.0, 12.0), (12.0, 20.0), (20.0, 30.0))
NORMALIZATION_BAND_HZ = (5.0, 35.0)
EPSILON = 1e-18


class DreyerDataRefusal(RuntimeError):
    """Fail-closed refusal for malformed generated or future real inputs."""


@dataclass(frozen=True)
class EDFHeaderSummary:
    """Allowlisted EDF header facts; patient and recording text never leave the parser."""

    header_bytes: int
    signal_count: int
    labels: tuple[str, ...]
    record_count: int
    record_duration_seconds: float
    samples_per_record: tuple[int, ...]
    sampling_rates_hz: tuple[float, ...]


def _np() -> Any:
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "DREYER-C5R-1 arrays require: pip install -e '.[classical]'"
        ) from exc
    return np


def _ascii_field(payload: bytes, start: int, width: int, name: str) -> str:
    field = payload[start : start + width]
    if len(field) != width:
        raise DreyerDataRefusal(f"truncated EDF {name} field")
    try:
        value = field.decode("ascii")
    except UnicodeDecodeError as exc:
        raise DreyerDataRefusal(f"non-ASCII EDF {name} field") from exc
    if any(ord(character) < 32 or ord(character) > 126 for character in value):
        raise DreyerDataRefusal(f"non-printable EDF {name} field")
    return value.strip()


def _parse_int_field(payload: bytes, start: int, width: int, name: str) -> int:
    value = _ascii_field(payload, start, width, name)
    if not value or any(character not in "-0123456789" for character in value):
        raise DreyerDataRefusal(f"malformed EDF integer field: {name}")
    try:
        return int(value)
    except ValueError as exc:
        raise DreyerDataRefusal(f"malformed EDF integer field: {name}") from exc


def _parse_float_field(payload: bytes, start: int, width: int, name: str) -> float:
    value = _ascii_field(payload, start, width, name)
    try:
        parsed = float(value)
    except ValueError as exc:
        raise DreyerDataRefusal(f"malformed EDF float field: {name}") from exc
    if not math.isfinite(parsed):
        raise DreyerDataRefusal(f"non-finite EDF float field: {name}")
    return parsed


def _signal_fields(payload: bytes, signal_count: int) -> dict[str, tuple[str, ...]]:
    widths = (
        ("labels", 16),
        ("transducers", 80),
        ("physical_dimensions", 8),
        ("physical_minimums", 8),
        ("physical_maximums", 8),
        ("digital_minimums", 8),
        ("digital_maximums", 8),
        ("prefilters", 80),
        ("samples_per_record", 8),
        ("reserved", 32),
    )
    offset = 256
    output: dict[str, tuple[str, ...]] = {}
    for name, width in widths:
        values = tuple(
            _ascii_field(payload, offset + index * width, width, f"{name}[{index}]")
            for index in range(signal_count)
        )
        output[name] = values
        offset += width * signal_count
    if offset != len(payload):
        raise DreyerDataRefusal("EDF fixed-header length differs from signal inventory")
    return output


def parse_edf_fixed_header(payload: bytes) -> EDFHeaderSummary:
    """Parse exactly one fixed EDF header and return only allowlisted structural facts."""

    if not isinstance(payload, bytes) or len(payload) < 512:
        raise DreyerDataRefusal("EDF fixed header is missing or too short")
    if _ascii_field(payload, 0, 8, "version") != "0":
        raise DreyerDataRefusal("EDF version differs from ASCII 0")
    header_bytes = _parse_int_field(payload, 184, 8, "header_bytes")
    record_count = _parse_int_field(payload, 236, 8, "record_count")
    record_duration = _parse_float_field(payload, 244, 8, "record_duration")
    signal_count = _parse_int_field(payload, 252, 4, "signal_count")
    if signal_count < 1 or signal_count > 128:
        raise DreyerDataRefusal("EDF signal count is outside the frozen safety range")
    expected_header_bytes = 256 * (signal_count + 1)
    if header_bytes != expected_header_bytes or len(payload) != header_bytes:
        raise DreyerDataRefusal("EDF header byte count differs from the fixed layout")
    if record_count < 1 or record_duration <= 0.0:
        raise DreyerDataRefusal("EDF record inventory is invalid")
    fields = _signal_fields(payload, signal_count)
    labels = fields["labels"]
    normalized = tuple(label.strip().casefold() for label in labels)
    if any(not label for label in normalized) or len(set(normalized)) != signal_count:
        raise DreyerDataRefusal("EDF signal labels are blank or duplicated")
    samples: list[int] = []
    rates: list[float] = []
    for index, value in enumerate(fields["samples_per_record"]):
        if not value.isdigit() or int(value) < 1:
            raise DreyerDataRefusal(f"invalid EDF samples-per-record field: {index}")
        count = int(value)
        rate = count / record_duration
        if not math.isfinite(rate) or rate <= 0.0:
            raise DreyerDataRefusal(f"invalid EDF sampling rate: {index}")
        samples.append(count)
        rates.append(rate)
    return EDFHeaderSummary(
        header_bytes=header_bytes,
        signal_count=signal_count,
        labels=labels,
        record_count=record_count,
        record_duration_seconds=record_duration,
        samples_per_record=tuple(samples),
        sampling_rates_hz=tuple(rates),
    )


def _pad_ascii(value: str, width: int) -> bytes:
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("generated EDF fields must be ASCII") from exc
    if len(encoded) > width:
        raise ValueError("generated EDF field exceeds fixed width")
    return encoded.ljust(width, b" ")


def build_generated_edf_header(
    labels: Sequence[str],
    *,
    sampling_rate_hz: int = 512,
    record_count: int = 8,
    record_duration_seconds: int = 1,
) -> bytes:
    """Build a synthetic EDF fixed header for generated-only qualification."""

    if not labels or sampling_rate_hz < 1 or record_count < 1 or record_duration_seconds < 1:
        raise ValueError("generated EDF header configuration is invalid")
    signal_count = len(labels)
    header_bytes = 256 * (signal_count + 1)
    fixed = b"".join(
        (
            _pad_ascii("0", 8),
            _pad_ascii("GENERATED-PATIENT", 80),
            _pad_ascii("GENERATED-RECORDING", 80),
            _pad_ascii("01.01.01", 8),
            _pad_ascii("01.01.01", 8),
            _pad_ascii(str(header_bytes), 8),
            _pad_ascii("EDF+C", 44),
            _pad_ascii(str(record_count), 8),
            _pad_ascii(str(record_duration_seconds), 8),
            _pad_ascii(str(signal_count), 4),
        )
    )
    if len(fixed) != 256:
        raise AssertionError("generated EDF fixed prefix differs")
    fields = (
        (labels, 16),
        (["generated"] * signal_count, 80),
        (["uV"] * signal_count, 8),
        (["-100"] * signal_count, 8),
        (["100"] * signal_count, 8),
        (["-32768"] * signal_count, 8),
        (["32767"] * signal_count, 8),
        (["none"] * signal_count, 80),
        ([str(sampling_rate_hz * record_duration_seconds)] * signal_count, 8),
        ([""] * signal_count, 32),
    )
    signal_header = b"".join(
        _pad_ascii(str(value), width) for values, width in fields for value in values
    )
    payload = fixed + signal_header
    if len(payload) != header_bytes:
        raise AssertionError("generated EDF header length differs")
    return payload


def periodic_hann(sample_count: int) -> Any:
    """Return the frozen periodic Hann window."""

    if sample_count < 2:
        raise DreyerDataRefusal("spectral segment is too short")
    np = _np()
    index = np.arange(sample_count, dtype="float64")
    return 0.5 - 0.5 * np.cos(2.0 * np.pi * index / sample_count)


def log_relative_band_features(
    signal: Any,
    *,
    sampling_rate_hz: float = EXPECTED_SAMPLING_RATE_HZ,
) -> Any:
    """Extract the frozen one-second causal channel-band features without labels."""

    np = _np()
    values = np.asarray(signal, dtype="float64")
    expected_samples = int(EXPECTED_SAMPLING_RATE_HZ)
    if sampling_rate_hz != EXPECTED_SAMPLING_RATE_HZ:
        raise DreyerDataRefusal("sampling rate differs from 512 Hz")
    if values.ndim != 2 or values.shape[0] < 1 or values.shape[1] != expected_samples:
        raise DreyerDataRefusal("spectral input must be channels by exactly 512 samples")
    if not np.isfinite(values).all():
        raise DreyerDataRefusal("spectral input contains a non-finite value")
    centered = values - values.mean(axis=1, keepdims=True)
    window = periodic_hann(expected_samples)
    transformed = np.fft.rfft(centered * window, axis=1)
    power = np.square(np.abs(transformed)) / float(np.square(window).sum())
    frequencies = np.fft.rfftfreq(expected_samples, 1.0 / sampling_rate_hz)
    normalization = (frequencies >= NORMALIZATION_BAND_HZ[0]) & (
        frequencies <= NORMALIZATION_BAND_HZ[1]
    )
    total = power[:, normalization].sum(axis=1)
    if np.any(total <= 0.0):
        raise DreyerDataRefusal("spectral normalization power is zero")
    output = []
    for index, (low, high) in enumerate(BANDS_HZ):
        if index < len(BANDS_HZ) - 1:
            selected = (frequencies >= low) & (frequencies < high)
        else:
            selected = (frequencies >= low) & (frequencies <= high)
        band = power[:, selected].sum(axis=1)
        output.append(np.log10(band + EPSILON) - np.log10(total + EPSILON))
    result = np.stack(output, axis=1)
    if result.shape != (values.shape[0], len(BANDS_HZ)) or not np.isfinite(result).all():
        raise DreyerDataRefusal("spectral feature output is malformed")
    return result


def window_band_features(
    trial_signal: Any,
    segments_seconds: Sequence[Sequence[float]],
    *,
    sampling_rate_hz: float = EXPECTED_SAMPLING_RATE_HZ,
) -> Any:
    """Average frozen one-second features across target-free trial intervals."""

    np = _np()
    values = np.asarray(trial_signal, dtype="float64")
    if values.ndim != 2 or values.shape[0] < 1 or not segments_seconds:
        raise DreyerDataRefusal("trial signal or segment inventory is malformed")
    parts = []
    for segment in segments_seconds:
        if len(segment) != 2:
            raise DreyerDataRefusal("segment boundary inventory is malformed")
        start, stop = (float(segment[0]), float(segment[1]))
        if stop - start != 1.0 or start < 0.0:
            raise DreyerDataRefusal("every spectral segment must be one nonnegative second")
        first = int(round(start * sampling_rate_hz))
        last = int(round(stop * sampling_rate_hz))
        if last > values.shape[1] or last - first != int(sampling_rate_hz):
            raise DreyerDataRefusal("segment exceeds the available trial signal")
        parts.append(
            log_relative_band_features(
                values[:, first:last], sampling_rate_hz=sampling_rate_hz
            )
        )
    return np.mean(np.stack(parts, axis=0), axis=0)
