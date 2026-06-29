"""FIF + MAT extraction for the first real NeuroDecodeKit shard.

This module deliberately keeps MNE, SciPy, and NumPy imports inside the real
extraction path so the base package remains lightweight.
"""

from __future__ import annotations

import importlib
import math
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Iterable

from neurodecodekit.cache.npz_cache import save_npz_cache
from neurodecodekit.preprocess.windowing import (
    WindowSpec,
    extract_windows_from_array_with_report,
)


NEURO_INSTALL_MESSAGE = "pip install -e '.[neuro]'"
TIME_FIELD_HINTS = (
    "time",
    "times",
    "timestamp",
    "timestamps",
    "onset",
    "onsets",
    "sample",
    "samples",
    "latency",
    "latencies",
)
LABEL_FIELD_HINTS = (
    "label",
    "labels",
    "target",
    "targets",
    "key",
    "keys",
    "char",
    "chars",
    "letter",
    "letters",
    "response",
    "responses",
    "stim",
    "code",
)
EVENT_CONTAINER_HINTS = (
    "event",
    "events",
    "trial",
    "trials",
    "log",
    "logs",
    "key",
    "keyboard",
    "press",
    "trigger",
    "trig",
    "stim",
)


@dataclass(frozen=True)
class EventRow:
    """One parsed behavioral event."""

    time_sec: float
    label: str
    source_index: int
    source_path: str
    confidence: str = "heuristic"


@dataclass(frozen=True)
class ParsedEvents:
    """Events parsed from a `.mat` payload plus parser warnings."""

    rows: list[EventRow]
    warnings: list[str]
    source_fields: list[str]

    @property
    def n_events_found(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class ExtractionSummary:
    """Human-readable summary for a real extraction run."""

    raw_path: str
    events_path: str
    out_path: str
    n_events_found: int
    n_events_kept: int
    dropped_by_reason: dict[str, int]
    output_shape: tuple[int, int, int]
    sfreq: float
    raw_bytes: int | None
    output_bytes: int
    channel_names: list[str]
    warnings: list[str]

    @property
    def n_events_dropped(self) -> int:
        return sum(self.dropped_by_reason.values())


@dataclass
class _EventCandidate:
    source_path: str
    rows: list[EventRow]
    score: int
    warnings: list[str]


def require_neuro_dependencies(
    import_module: Callable[[str], Any] = importlib.import_module,
) -> tuple[Any, Callable[..., Any], Any]:
    """Import optional neuro dependencies or raise a helpful install message."""

    missing = []
    modules: dict[str, Any] = {}
    for module_name, display_name in (
        ("mne", "MNE"),
        ("scipy.io", "SciPy"),
        ("numpy", "NumPy"),
    ):
        try:
            modules[module_name] = import_module(module_name)
        except ImportError:
            missing.append(display_name)

    if missing:
        missing_text = ", ".join(missing)
        raise RuntimeError(
            "Real FIF/MAT extraction requires optional neuro dependencies "
            f"({missing_text}). Install them with: {NEURO_INSTALL_MESSAGE}"
        )

    return modules["mne"], modules["scipy.io"].loadmat, modules["numpy"]


def parse_mat_event_payload(
    payload: dict[str, Any],
    *,
    source_sfreq: float | None = None,
    raw_duration_sec: float | None = None,
    raw_n_times: int | None = None,
) -> ParsedEvents:
    """Parse event timestamps and labels from a loaded MATLAB payload.

    The SpanishBCBL log schema can be inspected once a user supplies a real
    `.mat` file. Until then, this parser uses transparent heuristics over common
    event-table shapes: record lists, parallel time/label arrays, and numeric
    event matrices.
    """

    cleaned = {key: value for key, value in payload.items() if not key.startswith("__")}
    candidates = []
    candidates.extend(
        _record_sequence_candidates(
            cleaned,
            source_sfreq=source_sfreq,
            raw_duration_sec=raw_duration_sec,
            raw_n_times=raw_n_times,
        )
    )
    candidates.extend(
        _matrix_candidates(
            cleaned,
            source_sfreq=source_sfreq,
            raw_duration_sec=raw_duration_sec,
            raw_n_times=raw_n_times,
        )
    )
    candidates.extend(
        _parallel_array_candidates(
            cleaned,
            source_sfreq=source_sfreq,
            raw_duration_sec=raw_duration_sec,
            raw_n_times=raw_n_times,
        )
    )

    candidates = [candidate for candidate in candidates if candidate.rows]
    if not candidates:
        top_keys = ", ".join(sorted(cleaned)[:12]) or "<none>"
        return ParsedEvents(
            rows=[],
            source_fields=[],
            warnings=[
                "No confident event timestamp table was found in the .mat file. "
                f"Top-level keys inspected: {top_keys}"
            ],
        )

    candidates.sort(key=lambda item: (item.score, len(item.rows)), reverse=True)
    selected = candidates[0]
    warnings = list(selected.warnings)
    if selected.score < 60:
        warnings.append(
            "Event timestamp parsing used a low-confidence heuristic; inspect the .mat "
            "fields before treating labels as ground truth."
        )
    if not any(row.label for row in selected.rows):
        warnings.append(
            "No per-event labels or targets were confidently parsed; labels are blank."
        )
    if len(candidates) > 1:
        alternates = [candidate.source_path for candidate in candidates[1:4]]
        warnings.append(
            "Multiple possible event tables were found; selected "
            f"{selected.source_path!r}. Other candidates: {alternates}"
        )

    return ParsedEvents(
        rows=selected.rows,
        warnings=warnings,
        source_fields=[selected.source_path],
    )


def load_mat_events(
    path: str | Path,
    *,
    source_sfreq: float | None = None,
    raw_duration_sec: float | None = None,
    raw_n_times: int | None = None,
) -> ParsedEvents:
    """Load and parse one MATLAB behavioral/log file."""

    _, loadmat, _ = require_neuro_dependencies()
    payload = loadmat(
        Path(path),
        squeeze_me=True,
        struct_as_record=False,
        simplify_cells=True,
    )
    return parse_mat_event_payload(
        payload,
        source_sfreq=source_sfreq,
        raw_duration_sec=raw_duration_sec,
        raw_n_times=raw_n_times,
    )


def extract_fif_mat_windows(
    *,
    raw_path: str | Path,
    events_path: str | Path,
    out_path: str | Path,
    tmin: float,
    tmax: float,
    sfreq: float,
    picks: str | None = None,
    max_events: int | None = None,
    max_channels: int | None = None,
) -> ExtractionSummary:
    """Extract event-aligned windows from one FIF block and one MAT log."""

    mne, loadmat, np = require_neuro_dependencies()

    raw_file = Path(raw_path)
    events_file = Path(events_path)
    output_file = Path(out_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw FIF file not found: {raw_file}")
    if not events_file.exists():
        raise FileNotFoundError(f"MAT event/log file not found: {events_file}")
    if max_events is not None and max_events < 1:
        raise ValueError("max_events must be >= 1 when provided")
    if max_channels is not None and max_channels < 1:
        raise ValueError("max_channels must be >= 1 when provided")

    raw = mne.io.read_raw_fif(str(raw_file), preload=True, verbose="ERROR")
    original_sfreq = float(raw.info["sfreq"])
    original_n_times = int(raw.n_times)
    raw_duration_sec = original_n_times / original_sfreq if original_sfreq else None

    _apply_channel_picks(raw, picks=picks, max_channels=max_channels)
    if float(sfreq) != float(raw.info["sfreq"]):
        raw.resample(float(sfreq), npad="auto", verbose="ERROR")

    payload = loadmat(
        events_file,
        squeeze_me=True,
        struct_as_record=False,
        simplify_cells=True,
    )
    parsed = parse_mat_event_payload(
        payload,
        source_sfreq=original_sfreq,
        raw_duration_sec=raw_duration_sec,
        raw_n_times=original_n_times,
    )

    rows_for_window = parsed.rows
    dropped_by_reason = Counter()
    if max_events is not None and len(rows_for_window) > max_events:
        dropped_by_reason["max_events"] = len(rows_for_window) - max_events
        rows_for_window = rows_for_window[:max_events]

    spec = WindowSpec(sfreq=float(raw.info["sfreq"]), tmin=tmin, tmax=tmax)
    event_times = [row.time_sec for row in rows_for_window]
    data = raw.get_data().astype("float32", copy=False)
    result = extract_windows_from_array_with_report(data, event_times, spec)
    dropped_by_reason.update(result.dropped_by_reason)

    kept_rows = [rows_for_window[index] for index in result.kept_event_indices]
    labels = np.array([row.label for row in kept_rows], dtype="U")
    event_start_sec = np.array([row.time_sec for row in kept_rows], dtype="float64")
    event_source_index = np.array([row.source_index for row in kept_rows], dtype="int32")
    channel_names = list(raw.ch_names)
    windows = result.windows.astype("float32", copy=False)

    metadata = {
        "kind": "real_fif_mat_windows",
        "source_files": {
            "raw": str(raw_file),
            "events": str(events_file),
        },
        "transformations": [
            {
                "name": "mne_read_raw_fif",
                "description": "Loaded one explicit FIF block with preload=True.",
                "params": {"raw_path": str(raw_file)},
            },
            {
                "name": "channel_picking",
                "description": "Applied optional MNE channel picks and max-channel cap.",
                "params": {"picks": picks, "max_channels": max_channels},
            },
            {
                "name": "resample",
                "description": "Resampled raw signal when requested sfreq differed from source sfreq.",
                "params": {
                    "original_sfreq": original_sfreq,
                    "target_sfreq": float(raw.info["sfreq"]),
                    "requested_sfreq": float(sfreq),
                },
            },
            {
                "name": "scipy_loadmat_event_parse",
                "description": "Loaded one explicit MAT log and parsed event rows with transparent heuristics.",
                "params": {"events_path": str(events_file)},
            },
            {
                "name": "event_window_extraction",
                "description": "Extracted fixed windows around parsed event timestamps.",
                "params": {"tmin": tmin, "tmax": tmax, "sfreq": float(raw.info["sfreq"])},
            },
        ],
        "extraction_params": {
            "tmin": tmin,
            "tmax": tmax,
            "sfreq": float(raw.info["sfreq"]),
            "requested_sfreq": float(sfreq),
            "picks": picks,
            "max_events": max_events,
            "max_channels": max_channels,
        },
        "raw": {
            "original_sfreq": original_sfreq,
            "original_n_times": original_n_times,
            "duration_sec": raw_duration_sec,
            "bytes": _safe_stat_size(raw_file),
        },
        "events": {
            "found": parsed.n_events_found,
            "used_for_windowing": len(rows_for_window),
            "kept": len(kept_rows),
            "dropped_by_reason": dict(dropped_by_reason),
            "parser_source_fields": parsed.source_fields,
            "kept_event_metadata": [asdict(row) for row in kept_rows],
        },
        "channels": {
            "n_channels": len(channel_names),
            "names": channel_names,
        },
        "warnings": parsed.warnings,
    }

    save_npz_cache(
        output_file,
        windows=windows,
        labels=labels,
        metadata=metadata,
        extra_arrays={
            "event_start_sec": event_start_sec,
            "event_source_index": event_source_index,
            "channel_names": np.array(channel_names, dtype="U"),
        },
    )

    return ExtractionSummary(
        raw_path=str(raw_file),
        events_path=str(events_file),
        out_path=str(output_file),
        n_events_found=parsed.n_events_found,
        n_events_kept=len(kept_rows),
        dropped_by_reason=dict(dropped_by_reason),
        output_shape=tuple(int(dim) for dim in windows.shape),
        sfreq=float(raw.info["sfreq"]),
        raw_bytes=_safe_stat_size(raw_file),
        output_bytes=int(output_file.stat().st_size),
        channel_names=channel_names,
        warnings=parsed.warnings,
    )


def _apply_channel_picks(raw: Any, *, picks: str | None, max_channels: int | None) -> None:
    if picks:
        parsed = _parse_picks_arg(picks)
        raw.pick(parsed)
    if max_channels is not None and len(raw.ch_names) > max_channels:
        raw.pick(raw.ch_names[:max_channels])


def _parse_picks_arg(picks: str) -> str | list[str]:
    parts = [part.strip() for part in picks.split(",") if part.strip()]
    if len(parts) == 1 and parts[0].lower() in {
        "meg",
        "eeg",
        "mag",
        "grad",
        "stim",
        "misc",
    }:
        return parts[0].lower()
    return parts


def _record_sequence_candidates(
    payload: dict[str, Any],
    *,
    source_sfreq: float | None,
    raw_duration_sec: float | None,
    raw_n_times: int | None,
) -> list[_EventCandidate]:
    candidates: list[_EventCandidate] = []
    for path, records in _iter_record_sequences(payload):
        rows: list[EventRow] = []
        warnings: list[str] = []
        for index, record in enumerate(records):
            leaves = list(_iter_leaves(record, path))
            time_leaf = _best_leaf(leaves, TIME_FIELD_HINTS, numeric=True)
            if time_leaf is None:
                continue
            time_path, time_value = time_leaf
            numeric = _as_numeric_vector(time_value)
            if not numeric:
                continue
            times, time_warnings = _coerce_times_sec(
                numeric[:1],
                time_path,
                source_sfreq=source_sfreq,
                raw_duration_sec=raw_duration_sec,
                raw_n_times=raw_n_times,
            )
            warnings.extend(time_warnings)
            if not times:
                continue
            label = ""
            label_leaf = _best_leaf(leaves, LABEL_FIELD_HINTS, numeric=False)
            if label_leaf is not None:
                labels = _as_label_vector(label_leaf[1])
                if labels:
                    label = labels[0]
            rows.append(EventRow(times[0], label, index, time_path, "record"))
        if rows:
            score = 80 + _field_score(path, EVENT_CONTAINER_HINTS)
            candidates.append(_EventCandidate(path, rows, score, warnings))
    return candidates


def _parallel_array_candidates(
    payload: dict[str, Any],
    *,
    source_sfreq: float | None,
    raw_duration_sec: float | None,
    raw_n_times: int | None,
) -> list[_EventCandidate]:
    leaves = list(_iter_leaves(payload, "mat"))
    time_leaves = [
        (path, value, _field_score(path, TIME_FIELD_HINTS))
        for path, value in leaves
        if _field_score(path, TIME_FIELD_HINTS) > 0 and _as_numeric_vector(value)
    ]
    label_leaves = [
        (path, value, _field_score(path, LABEL_FIELD_HINTS))
        for path, value in leaves
        if _field_score(path, LABEL_FIELD_HINTS) > 0 and _as_label_vector(value)
    ]

    candidates: list[_EventCandidate] = []
    for time_path, time_value, time_score in time_leaves:
        numeric = _as_numeric_vector(time_value) or []
        if not numeric:
            continue
        times, warnings = _coerce_times_sec(
            numeric,
            time_path,
            source_sfreq=source_sfreq,
            raw_duration_sec=raw_duration_sec,
            raw_n_times=raw_n_times,
        )
        if not times:
            continue

        labels = [""] * len(times)
        label_score = 0
        label_path = ""
        for candidate_path, candidate_value, candidate_score in sorted(
            label_leaves,
            key=lambda item: item[2],
            reverse=True,
        ):
            if candidate_path == time_path:
                continue
            candidate_labels = _as_label_vector(candidate_value) or []
            if len(candidate_labels) == len(times):
                labels = candidate_labels
                label_score = candidate_score
                label_path = candidate_path
                break

        source_path = time_path if not label_path else f"{time_path} + {label_path}"
        rows = [
            EventRow(time_sec, labels[index], index, source_path, "parallel")
            for index, time_sec in enumerate(times)
        ]
        score = 45 + time_score + label_score
        candidates.append(_EventCandidate(source_path, rows, score, warnings))
    return candidates


def _matrix_candidates(
    payload: dict[str, Any],
    *,
    source_sfreq: float | None,
    raw_duration_sec: float | None,
    raw_n_times: int | None,
) -> list[_EventCandidate]:
    candidates: list[_EventCandidate] = []
    for path, value in _iter_leaves(payload, "mat"):
        matrix = _as_numeric_matrix(value)
        if not matrix or len(matrix[0]) < 2:
            continue
        path_score = _field_score(path, EVENT_CONTAINER_HINTS)
        if path_score <= 0 and len(matrix[0]) != 3:
            continue

        first_col = [row[0] for row in matrix]
        labels = [_label_to_string(row[-1]) for row in matrix]
        times, warnings = _coerce_times_sec(
            first_col,
            path,
            source_sfreq=source_sfreq,
            raw_duration_sec=raw_duration_sec,
            raw_n_times=raw_n_times,
        )
        rows = [
            EventRow(time_sec, labels[index], index, f"{path}[:,0]", "matrix")
            for index, time_sec in enumerate(times)
        ]
        score = 55 + path_score
        candidates.append(_EventCandidate(path, rows, score, warnings))
    return candidates


def _iter_record_sequences(value: Any, path: str = "mat") -> Iterable[tuple[str, list[dict[str, Any]]]]:
    plain = _plain(value)
    if isinstance(plain, dict):
        for key, child in plain.items():
            if str(key).startswith("__"):
                continue
            yield from _iter_record_sequences(child, _join_path(path, str(key)))
        return
    if isinstance(plain, (list, tuple)) and plain:
        mappings = [_as_mapping(item) for item in plain]
        if all(mapping is not None for mapping in mappings):
            yield path, [mapping for mapping in mappings if mapping is not None]
            return
        for index, child in enumerate(plain):
            yield from _iter_record_sequences(child, f"{path}[{index}]")


def _iter_leaves(value: Any, path: str) -> Iterable[tuple[str, Any]]:
    plain = _plain(value)
    if isinstance(plain, dict):
        for key, child in plain.items():
            if str(key).startswith("__"):
                continue
            yield from _iter_leaves(child, _join_path(path, str(key)))
        return
    yield path, plain


def _best_leaf(
    leaves: list[tuple[str, Any]],
    hints: tuple[str, ...],
    *,
    numeric: bool,
) -> tuple[str, Any] | None:
    scored = []
    for path, value in leaves:
        if numeric and not _as_numeric_vector(value):
            continue
        if not numeric and not _as_label_vector(value):
            continue
        score = _field_score(path, hints)
        if score > 0:
            scored.append((score, path, value))
    if not scored:
        return None
    scored.sort(reverse=True)
    _, path, value = scored[0]
    return path, value


def _plain(value: Any) -> Any:
    if hasattr(value, "_fieldnames"):
        return {name: getattr(value, name) for name in value._fieldnames}
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except TypeError:
            pass
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _as_mapping(value: Any) -> dict[str, Any] | None:
    plain = _plain(value)
    if isinstance(plain, dict):
        return plain
    return None


def _as_vector(value: Any) -> list[Any] | None:
    plain = _plain(value)
    if _is_scalar(plain):
        return [plain]
    if not isinstance(plain, (list, tuple)):
        return None
    items = list(plain)
    if not items:
        return []
    if all(_is_scalar(item) for item in items):
        return items
    if len(items) == 1 and isinstance(items[0], (list, tuple)):
        return _as_vector(items[0])
    if all(isinstance(item, (list, tuple)) and len(item) == 1 for item in items):
        column = [item[0] for item in items]
        if all(_is_scalar(item) for item in column):
            return column
    return None


def _as_numeric_vector(value: Any) -> list[float] | None:
    vector = _as_vector(value)
    if vector is None:
        return None
    numeric = []
    for item in vector:
        number = _try_float(item)
        if number is None:
            return None
        numeric.append(number)
    return numeric


def _as_label_vector(value: Any) -> list[str] | None:
    vector = _as_vector(value)
    if vector is None:
        return None
    labels = []
    for item in vector:
        if isinstance(_plain(item), (dict, list, tuple)):
            return None
        labels.append(_label_to_string(item))
    return labels


def _as_numeric_matrix(value: Any) -> list[list[float]] | None:
    plain = _plain(value)
    if not isinstance(plain, (list, tuple)) or not plain:
        return None
    rows = []
    expected_len = None
    for row in plain:
        row = _plain(row)
        if not isinstance(row, (list, tuple)) or len(row) < 2:
            return None
        numeric_row = []
        for item in row:
            number = _try_float(item)
            if number is None:
                return None
            numeric_row.append(number)
        expected_len = expected_len or len(numeric_row)
        if len(numeric_row) != expected_len:
            return None
        rows.append(numeric_row)
    return rows


def _coerce_times_sec(
    values: list[float],
    field_path: str,
    *,
    source_sfreq: float | None,
    raw_duration_sec: float | None,
    raw_n_times: int | None,
) -> tuple[list[float], list[str]]:
    warnings: list[str] = []
    if not values:
        return [], warnings

    lower = field_path.lower()
    finite = [value for value in values if math.isfinite(value)]
    if len(finite) != len(values):
        warnings.append(f"Dropped {len(values) - len(finite)} non-finite event timestamps from {field_path!r}.")
    if not finite:
        return [], warnings

    sample_like_name = any(token in lower for token in ("sample", "latency"))
    max_value = max(finite)
    convert_from_samples = False
    if sample_like_name and source_sfreq:
        convert_from_samples = True
    elif source_sfreq and raw_duration_sec and max_value > raw_duration_sec + 1.0:
        if raw_n_times is None or max_value <= raw_n_times * 1.05:
            convert_from_samples = True
            warnings.append(
                f"Interpreted {field_path!r} as sample indices because values exceed raw duration."
            )

    if sample_like_name and not source_sfreq:
        warnings.append(
            f"{field_path!r} looks sample-based but no source sampling rate was provided; treating values as seconds."
        )

    if convert_from_samples:
        times = [value / float(source_sfreq) for value in finite]
    else:
        times = finite
    return times, warnings


def _field_score(path: str, hints: tuple[str, ...]) -> int:
    lower = path.lower()
    score = 0
    for hint in hints:
        if hint in lower:
            score += 10
    for hint in EVENT_CONTAINER_HINTS:
        if hint in lower:
            score += 2
    return score


def _try_float(value: Any) -> float | None:
    value = _plain(value)
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _label_to_string(value: Any) -> str:
    value = _plain(value)
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _is_scalar(value: Any) -> bool:
    value = _plain(value)
    return value is None or isinstance(value, (str, bytes, int, float, bool))


def _join_path(parent: str, child: str) -> str:
    if not parent:
        return child
    return f"{parent}.{child}"


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None
