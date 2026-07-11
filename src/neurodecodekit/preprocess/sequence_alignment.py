"""Lightweight typed-key sequence grouping and MAT target alignment."""

from __future__ import annotations

import json
import math
import statistics
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from neurodecodekit.evaluation.metrics import (
    character_error_rate,
    levenshtein_distance,
    normalize_text,
)


SEQUENCE_SCHEMA_NAME = "neurodecodekit-sequence-alignment-report"
SEQUENCE_SCHEMA_VERSION = 3
DEFAULT_HIGH_CONFIDENCE_CER = 0.15
DEFAULT_MODERATE_CONFIDENCE_CER = 0.35


@dataclass(frozen=True)
class KeySequence:
    """One typed sequence reconstructed from key labels."""

    index: int
    text: str
    normalized_text: str
    start_event_index: int
    end_event_index: int
    start_sec: float | None
    end_sec: float | None
    n_key_events: int
    ended_by: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TargetSequence:
    """One text sequence from a MATLAB log."""

    index: int
    text: str
    normalized_text: str
    source_path: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MatTrialIndexMap:
    """Deterministic raw-sequence to MAT-trial mapping evidence."""

    strategy: str
    raw_to_mat_trial_indices: tuple[int, ...]
    skipped_mat_trial_indices: tuple[int, ...]
    response_indices_match_performed_trials: bool | None
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy": self.strategy,
            "raw_to_mat_trial_indices": list(self.raw_to_mat_trial_indices),
            "skipped_mat_trial_indices": list(self.skipped_mat_trial_indices),
            "response_indices_match_performed_trials": (
                self.response_indices_match_performed_trials
            ),
            "warnings": list(self.warnings),
        }


class TrialMappingUnavailableError(ValueError):
    """Raised when a partial raw shard cannot cover the performed MAT trials."""


@dataclass(frozen=True)
class SequenceAlignment:
    """Best target match for one typed key sequence."""

    key_index: int
    target_index: int | None
    target_source_path: str | None
    typed_text: str
    target_text: str | None
    cer: float | None
    edit_distance: int | None
    exact_match: bool
    confidence: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def load_key_sequences_from_npz_cache(
    path: str | Path,
) -> tuple[list[KeySequence], dict[str, object]]:
    """Load only labels/timing/metadata from an NPZ cache and group sequences.

    This intentionally avoids reading the `windows` array so a sequence audit
    can run cheaply even when the neural cache is much larger than today's
    tiny shard.
    """

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Sequence alignment requires NumPy to read NPZ caches: `pip install numpy`."
        ) from exc

    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        if "labels" not in data.files:
            raise ValueError(f"NPZ cache is missing labels: {cache_path}")
        labels = [str(value) for value in data["labels"].tolist()]
        event_times = None
        if "event_start_sec" in data.files:
            event_times = [float(value) for value in data["event_start_sec"].tolist()]
        metadata = _decode_npz_metadata(data["metadata"]) if "metadata" in data.files else {}

    sequences = group_key_labels_into_sequences(labels, event_times=event_times)
    summary = _cache_summary_from_metadata(cache_path, metadata, n_labels=len(labels))
    return sequences, summary


def load_key_event_time_sequences_from_npz_cache(path: str | Path) -> list[list[float]]:
    """Load cache event times and group them into ENTER-delimited trials."""

    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Sequence timing audit requires NumPy: `pip install numpy`.") from exc

    cache_path = Path(path)
    with np.load(cache_path, allow_pickle=False) as data:
        if "labels" not in data.files or "event_start_sec" not in data.files:
            raise ValueError(
                f"NPZ cache timing audit requires labels and event_start_sec arrays: {cache_path}"
            )
        labels = [str(value) for value in data["labels"].tolist()]
        event_times = [float(value) for value in data["event_start_sec"].tolist()]
    return group_key_event_times_into_sequences(labels, event_times)


def group_key_labels_into_sequences(
    labels: Iterable[str],
    *,
    event_times: Iterable[float] | None = None,
    boundary_label: str = "ENTER",
    space_label: str = "SPACE",
) -> list[KeySequence]:
    """Group key labels into text rows using ENTER as the sequence boundary."""

    label_values = [str(label) for label in labels]
    if event_times is None:
        time_values: list[float | None] = [None] * len(label_values)
    else:
        time_values = [float(value) for value in event_times]
        if len(time_values) != len(label_values):
            raise ValueError(
                "event_times must match labels length: "
                f"{len(time_values)} times vs {len(label_values)} labels."
            )

    sequences: list[KeySequence] = []
    current_chars: list[str] = []
    current_start: int | None = None
    current_start_sec: float | None = None
    for event_index, (label, time_sec) in enumerate(zip(label_values, time_values)):
        if label == boundary_label:
            if current_start is not None:
                sequences.append(
                    _make_key_sequence(
                        index=len(sequences),
                        chars=current_chars,
                        start_event_index=current_start,
                        end_event_index=event_index,
                        start_sec=current_start_sec,
                        end_sec=time_sec,
                        ended_by=boundary_label,
                    )
                )
            current_chars = []
            current_start = None
            current_start_sec = None
            continue

        if current_start is None:
            current_start = event_index
            current_start_sec = time_sec
        current_chars.append(_label_to_text(label, space_label=space_label))

    if current_start is not None:
        sequences.append(
            _make_key_sequence(
                index=len(sequences),
                chars=current_chars,
                start_event_index=current_start,
                end_event_index=len(label_values) - 1,
                start_sec=current_start_sec,
                end_sec=time_values[-1] if time_values else None,
                ended_by="end_of_cache",
            )
        )
    return sequences


def group_key_event_times_into_sequences(
    labels: Iterable[str],
    event_times: Iterable[float],
    *,
    boundary_label: str = "ENTER",
) -> list[list[float]]:
    """Group per-key timestamps into trials, including each ENTER timestamp."""

    label_values = [str(label) for label in labels]
    time_values = [float(value) for value in event_times]
    if len(time_values) != len(label_values):
        raise ValueError(
            "event_times must match labels length: "
            f"{len(time_values)} times vs {len(label_values)} labels."
        )

    sequences: list[list[float]] = []
    current: list[float] = []
    for label, time_sec in zip(label_values, time_values):
        if label == boundary_label:
            if current:
                current.append(time_sec)
                sequences.append(current)
            current = []
            continue
        current.append(time_sec)
    if current:
        sequences.append(current)
    return sequences


def extract_target_sequences_from_payload(
    payload: dict[str, Any],
) -> tuple[list[TargetSequence], list[str]]:
    """Extract target text rows from a MATLAB payload."""

    candidates: list[tuple[str, list[str]]] = []
    pr_trials = _get_field(payload, "pr_trials")
    if pr_trials is not None:
        for field in ("sequence", "sequences"):
            values = _string_vector(_get_field(pr_trials, field))
            if values:
                candidates.append((f"mat.pr_trials.{field}", values))
    for field in ("sequences", "sequence", "sequences_tr", "sequence1"):
        values = _string_vector(_get_field(payload, field))
        if values:
            candidates.append((f"mat.{field}", values))

    if not candidates:
        top_keys = (
            ", ".join(
                sorted(key for key in _payload_keys(payload) if not key.startswith("__"))[:12]
            )
            or "<none>"
        )
        return [], [f"no_target_sequence_field_found:{top_keys}"]

    source_path, values = sorted(
        candidates,
        key=lambda item: (_target_source_priority(item[0]), len(item[1])),
        reverse=True,
    )[0]
    targets: list[TargetSequence] = []
    preserve_trial_rows = source_path == "mat.pr_trials.sequence"
    seen: set[str] = set()
    for source_index, value in enumerate(values):
        normalized = normalize_text(str(value))
        if not normalized:
            continue
        if not preserve_trial_rows and normalized in seen:
            continue
        seen.add(normalized)
        targets.append(
            TargetSequence(
                index=source_index if preserve_trial_rows else len(targets),
                text=str(value).strip(),
                normalized_text=normalized,
                source_path=source_path,
            )
        )
    warnings = []
    if len(candidates) > 1:
        alternates = [path for path, _ in candidates if path != source_path][:4]
        warnings.append(f"target_sequence_source_selected:{source_path};alternates:{alternates}")
    return targets, warnings


def extract_response_sequences_from_payload(
    payload: dict[str, Any],
) -> tuple[list[TargetSequence], list[str]]:
    """Extract MAT-recorded typed responses from `pr_trials.key`."""

    pr_trials = _get_field(payload, "pr_trials")
    key_rows = _get_field(pr_trials, "key") if pr_trials is not None else None
    if key_rows is None:
        return [], ["no_pr_trials_key_response_field_found"]

    responses: list[TargetSequence] = []
    for index, key_row in enumerate(_iter_items(key_rows)):
        text = _key_event_array_to_text(key_row)
        normalized = normalize_text(text)
        if not normalized:
            continue
        responses.append(
            TargetSequence(
                index=index,
                text=text,
                normalized_text=normalized,
                source_path="mat.pr_trials.key",
            )
        )
    warnings = []
    if not responses:
        warnings.append("no_nonempty_pr_trials_key_responses_found")
    return responses, warnings


def load_mat_target_sequences(path: str | Path) -> tuple[list[TargetSequence], list[str]]:
    """Load target sequences from one MATLAB log file."""

    targets, _, warnings = load_mat_sequence_sources(path)
    return targets, warnings


def load_mat_sequence_sources(
    path: str | Path,
) -> tuple[list[TargetSequence], list[TargetSequence], list[str]]:
    """Load target prompts and recorded typed responses from one MATLAB log."""

    try:
        from scipy.io import loadmat
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "MAT target extraction requires SciPy. Install optional neuro dependencies with: "
            "pip install -e '.[neuro]'"
        ) from exc

    mat_path = Path(path)
    payload = loadmat(
        mat_path,
        squeeze_me=True,
        struct_as_record=False,
        simplify_cells=False,
    )
    cleaned = {key: value for key, value in payload.items() if not key.startswith("__")}
    targets, target_warnings = extract_target_sequences_from_payload(cleaned)
    responses, response_warnings = extract_response_sequences_from_payload(cleaned)
    return targets, responses, [*target_warnings, *response_warnings]


def extract_mat_key_trigger_time_sequences_from_payload(
    payload: dict[str, Any],
) -> tuple[list[list[float]], list[str]]:
    """Extract the trial-aligned `pr_trials.keyTrig` timestamp arrays."""

    pr_trials = _get_field(payload, "pr_trials")
    key_trigger_rows = _get_field(pr_trials, "keyTrig") if pr_trials is not None else None
    if key_trigger_rows is None:
        return [], ["no_pr_trials_keyTrig_field_found"]

    rows: list[list[float]] = []
    non_finite_count = 0
    for row in _iter_items(key_trigger_rows):
        values: list[float] = []
        for item in _iter_items(row):
            try:
                value = float(item)
            except (TypeError, ValueError):
                continue
            if not math.isfinite(value):
                non_finite_count += 1
                continue
            values.append(value)
        rows.append(values)

    warnings = []
    if non_finite_count:
        warnings.append(f"dropped_non_finite_mat_keyTrig_values:{non_finite_count}")
    if not any(rows):
        warnings.append("no_finite_pr_trials_keyTrig_values_found")
    return rows, warnings


def load_mat_key_trigger_time_sequences(
    path: str | Path,
) -> tuple[list[list[float]], list[str]]:
    """Load trial-aligned `keyTrig` arrays from one MAT log."""

    try:
        from scipy.io import loadmat
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "MAT timing audit requires SciPy. Install optional neuro dependencies with: "
            "pip install -e '.[neuro]'"
        ) from exc

    payload = loadmat(
        Path(path),
        squeeze_me=True,
        struct_as_record=False,
        simplify_cells=False,
    )
    cleaned = {key: value for key, value in payload.items() if not key.startswith("__")}
    return extract_mat_key_trigger_time_sequences_from_payload(cleaned)


def build_mat_trial_index_map(
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    response_sequences: list[TargetSequence],
    mat_key_trigger_time_sequences: list[list[float]],
) -> MatTrialIndexMap:
    """Map raw ENTER-delimited rows to performed MAT trial slots.

    Official logs preserve unperformed trial slots as empty `keyTrig` rows. The
    mapping uses those nonempty slots in source order and never infers trial
    identity from fuzzy target text.
    """

    if not key_sequences:
        raise ValueError("Trial mapping requires at least one raw key sequence.")
    key_indices = [sequence.index for sequence in key_sequences]
    if key_indices != list(range(len(key_sequences))):
        raise ValueError("Raw key sequence indices must be contiguous and start at zero.")

    target_indices = [sequence.index for sequence in target_sequences]
    if len(set(target_indices)) != len(target_indices):
        raise ValueError("MAT target trial indices must be unique.")
    response_indices = [sequence.index for sequence in response_sequences]
    if len(set(response_indices)) != len(response_indices):
        raise ValueError("MAT response trial indices must be unique.")

    warnings: list[str] = []
    if mat_key_trigger_time_sequences:
        expected_target_indices = list(range(len(mat_key_trigger_time_sequences)))
        if target_indices != expected_target_indices:
            raise ValueError(
                "MAT keyTrig rows require one source-ordered target per trial slot: "
                f"target indices {target_indices[:8]}... vs "
                f"expected 0..{len(expected_target_indices) - 1}."
            )
        performed_indices = [
            index for index, values in enumerate(mat_key_trigger_time_sequences) if len(values) > 0
        ]
        skipped_indices = [
            index for index, values in enumerate(mat_key_trigger_time_sequences) if len(values) == 0
        ]
        if len(key_sequences) != len(performed_indices):
            raise TrialMappingUnavailableError(
                "Raw key sequences do not match nonempty MAT keyTrig trial slots: "
                f"{len(key_sequences)} vs {len(performed_indices)} "
                f"(empty MAT slots: {skipped_indices})."
            )
        if skipped_indices:
            warnings.append(
                "empty_mat_keyTrig_trials_skipped:"
                + ",".join(str(index) for index in skipped_indices)
            )
        response_match = response_indices == performed_indices
        if not response_match:
            warnings.append("mat_response_indices_do_not_exactly_match_performed_keyTrig_slots")
        strategy = "nonempty_mat_keyTrig_trial_order"
    else:
        if len(key_sequences) != len(target_sequences):
            raise TrialMappingUnavailableError(
                "Trial mapping has no MAT keyTrig evidence and raw/target counts differ: "
                f"{len(key_sequences)} vs {len(target_sequences)}."
            )
        performed_indices = target_indices
        skipped_indices = []
        response_match = response_indices == performed_indices if response_indices else None
        strategy = "equal_count_target_source_order_without_keyTrig"
        warnings.append("trial_mapping_lacks_mat_keyTrig_evidence")

    if len(set(performed_indices)) != len(performed_indices):
        raise ValueError("Mapped MAT trial indices must be unique.")
    if any(left >= right for left, right in zip(performed_indices, performed_indices[1:])):
        raise ValueError("Mapped MAT trial indices must be strictly increasing.")
    return MatTrialIndexMap(
        strategy=strategy,
        raw_to_mat_trial_indices=tuple(performed_indices),
        skipped_mat_trial_indices=tuple(skipped_indices),
        response_indices_match_performed_trials=response_match,
        warnings=tuple(warnings),
    )


def align_key_sequences_to_targets(
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    *,
    high_confidence_cer: float = DEFAULT_HIGH_CONFIDENCE_CER,
    moderate_confidence_cer: float = DEFAULT_MODERATE_CONFIDENCE_CER,
) -> list[SequenceAlignment]:
    """Match each typed key sequence to its closest MAT target sequence."""

    _validate_confidence_thresholds(
        high_confidence_cer=high_confidence_cer,
        moderate_confidence_cer=moderate_confidence_cer,
    )

    alignments: list[SequenceAlignment] = []
    for key_sequence in key_sequences:
        if not target_sequences:
            alignments.append(
                SequenceAlignment(
                    key_index=key_sequence.index,
                    target_index=None,
                    target_source_path=None,
                    typed_text=key_sequence.text,
                    target_text=None,
                    cer=None,
                    edit_distance=None,
                    exact_match=False,
                    confidence="unmatched",
                )
            )
            continue
        best = min(
            target_sequences,
            key=lambda target: (
                character_error_rate(target.text, key_sequence.text),
                target.index,
            ),
        )
        alignments.append(
            _compare_key_sequence_to_target(
                key_sequence,
                best,
                high_confidence_cer=high_confidence_cer,
                moderate_confidence_cer=moderate_confidence_cer,
            )
        )
    return alignments


def align_key_sequences_by_trial_map(
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    trial_index_map: Iterable[int],
    *,
    high_confidence_cer: float = DEFAULT_HIGH_CONFIDENCE_CER,
    moderate_confidence_cer: float = DEFAULT_MODERATE_CONFIDENCE_CER,
) -> list[SequenceAlignment]:
    """Compare text after MAT trial identity has been established by order."""

    _validate_confidence_thresholds(
        high_confidence_cer=high_confidence_cer,
        moderate_confidence_cer=moderate_confidence_cer,
    )
    mapped_indices = [int(value) for value in trial_index_map]
    if len(mapped_indices) != len(key_sequences):
        raise ValueError(
            "trial_index_map must contain one MAT index per key sequence: "
            f"{len(mapped_indices)} vs {len(key_sequences)}."
        )
    if len(set(mapped_indices)) != len(mapped_indices):
        raise ValueError("trial_index_map values must be unique.")
    if any(left >= right for left, right in zip(mapped_indices, mapped_indices[1:])):
        raise ValueError("trial_index_map values must be strictly increasing.")

    targets_by_index = {target.index: target for target in target_sequences}
    if len(targets_by_index) != len(target_sequences):
        raise ValueError("Target sequence indices must be unique.")

    alignments = []
    for key_sequence, target_index in zip(key_sequences, mapped_indices, strict=True):
        target = targets_by_index.get(target_index)
        if target is None:
            raise ValueError(f"Target sequence is missing mapped MAT trial index {target_index}.")
        alignments.append(
            _compare_key_sequence_to_target(
                key_sequence,
                target,
                high_confidence_cer=high_confidence_cer,
                moderate_confidence_cer=moderate_confidence_cer,
            )
        )
    return alignments


def build_sequence_alignment_report(
    *,
    cache_path: str | Path,
    events_path: str | Path,
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    alignments: list[SequenceAlignment],
    response_sequences: list[TargetSequence] | None = None,
    response_alignments: list[SequenceAlignment] | None = None,
    trial_index_map: MatTrialIndexMap | None = None,
    key_trigger_timing_audit: dict[str, object] | None = None,
    cache_summary: dict[str, object] | None = None,
    warnings: Iterable[str] | None = None,
    run_name: str | None = None,
    runtime_sec: float | None = None,
    high_confidence_cer: float = DEFAULT_HIGH_CONFIDENCE_CER,
    moderate_confidence_cer: float = DEFAULT_MODERATE_CONFIDENCE_CER,
) -> dict[str, object]:
    """Build a JSON-serializable sequence alignment report."""

    report_warnings = list(warnings or [])
    if any(alignment.confidence in {"low", "unmatched"} for alignment in alignments):
        report_warnings.append("some_typed_sequences_do_not_confidently_match_mat_targets")
    response_alignments = response_alignments or []
    if response_alignments and any(
        alignment.confidence in {"low", "unmatched"} for alignment in response_alignments
    ):
        report_warnings.append(
            "some_typed_sequences_do_not_confidently_match_mat_recorded_responses"
        )
    target_order = summarize_alignment_order(alignments)
    if target_order["target_index_order_is_monotonic"] is False:
        report_warnings.append("best_mat_target_matches_are_not_monotonic_in_trial_order")
    response_order = summarize_alignment_order(response_alignments)
    if response_order["target_index_order_is_monotonic"] is False:
        report_warnings.append("best_mat_response_matches_are_not_monotonic_in_trial_order")
    if key_trigger_timing_audit:
        mismatch_indices = key_trigger_timing_audit.get("length_mismatch_trial_indices") or []
        if mismatch_indices:
            report_warnings.append(f"mat_keyTrig_length_mismatch_trial_indices:{mismatch_indices}")
        report_warnings.append("mat_keyTrig_clock_offset_is_run_specific")
    if trial_index_map is None:
        report_warnings.append("assignment_uses_best_text_similarity_without_mat_trial_map")
    else:
        report_warnings.extend(trial_index_map.warnings)
    report_warnings.append("no_raw_fif_loaded_for_sequence_alignment")

    return {
        "schema": {
            "name": SEQUENCE_SCHEMA_NAME,
            "version": SEQUENCE_SCHEMA_VERSION,
        },
        "run": {
            "name": run_name or "sequence-alignment",
            "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
        "source_files": {
            "cache": str(cache_path),
            "events": str(events_path),
        },
        "params": {
            "boundary_label": "ENTER",
            "space_label": "SPACE",
            "high_confidence_cer": high_confidence_cer,
            "moderate_confidence_cer": moderate_confidence_cer,
        },
        "assignment": {
            "strategy": (
                trial_index_map.strategy if trial_index_map else "best_text_similarity"
            ),
            "uses_mat_trial_order": trial_index_map is not None,
            "has_mat_key_trigger_evidence": (
                trial_index_map is not None
                and trial_index_map.strategy == "nonempty_mat_keyTrig_trial_order"
            ),
            "uses_text_similarity_for_assignment": trial_index_map is None,
        },
        "trial_index_map": trial_index_map.to_dict() if trial_index_map else None,
        "resources": {
            "runtime_sec": runtime_sec,
            "cache_bytes": _safe_file_size(cache_path),
            "events_bytes": _safe_file_size(events_path),
        },
        "cache": cache_summary or {},
        "summary": summarize_alignments(
            key_sequences=key_sequences,
            target_sequences=target_sequences,
            alignments=alignments,
        ),
        "response_summary": summarize_alignments(
            key_sequences=key_sequences,
            target_sequences=response_sequences or [],
            alignments=response_alignments,
        )
        if response_alignments
        else None,
        "key_trigger_timing_audit": key_trigger_timing_audit,
        "warnings": report_warnings,
        "key_sequences": [sequence.to_dict() for sequence in key_sequences],
        "target_sequences": [sequence.to_dict() for sequence in target_sequences],
        "alignments": [alignment.to_dict() for alignment in alignments],
        "response_sequences": [sequence.to_dict() for sequence in response_sequences or []],
        "response_alignments": [alignment.to_dict() for alignment in response_alignments],
    }


def summarize_alignments(
    *,
    key_sequences: list[KeySequence],
    target_sequences: list[TargetSequence],
    alignments: list[SequenceAlignment],
) -> dict[str, object]:
    """Summarize target matching quality."""

    finite_cers = [
        alignment.cer
        for alignment in alignments
        if alignment.cer is not None and math.isfinite(alignment.cer)
    ]
    confidence_counts: dict[str, int] = {}
    for alignment in alignments:
        confidence_counts[alignment.confidence] = confidence_counts.get(alignment.confidence, 0) + 1
    matched_indices = sorted(
        {
            int(alignment.target_index)
            for alignment in alignments
            if alignment.target_index is not None
        }
    )
    low_confidence_key_indices = [
        alignment.key_index
        for alignment in alignments
        if alignment.confidence in {"low", "unmatched"}
    ]
    order_summary = summarize_alignment_order(alignments)
    return {
        "n_key_sequences": len(key_sequences),
        "n_target_sequences": len(target_sequences),
        "n_alignments": len(alignments),
        "exact_match_count": sum(1 for alignment in alignments if alignment.exact_match),
        "usable_high_or_moderate_count": sum(
            1 for alignment in alignments if alignment.confidence in {"high", "moderate"}
        ),
        "confidence_counts": confidence_counts,
        "mean_cer": sum(finite_cers) / len(finite_cers) if finite_cers else None,
        "max_cer": max(finite_cers) if finite_cers else None,
        "matched_target_indices": matched_indices,
        "low_confidence_key_indices": low_confidence_key_indices,
        **order_summary,
    }


def summarize_alignment_order(alignments: list[SequenceAlignment]) -> dict[str, object]:
    """Summarize whether best text matches preserve MAT trial order."""

    indexed = [
        (alignment.key_index, int(alignment.target_index))
        for alignment in alignments
        if alignment.target_index is not None
    ]
    backtracks = []
    previous_key_index: int | None = None
    previous_target_index: int | None = None
    for key_index, target_index in indexed:
        if previous_target_index is not None and target_index < previous_target_index:
            backtracks.append(
                {
                    "key_index": key_index,
                    "target_index": target_index,
                    "previous_key_index": previous_key_index,
                    "previous_target_index": previous_target_index,
                }
            )
        previous_key_index = key_index
        previous_target_index = target_index
    target_indices = [target_index for _, target_index in indexed]
    duplicate_count = len(target_indices) - len(set(target_indices))
    identity_mapping = (
        bool(indexed)
        and len(indexed) == len(alignments)
        and all(key_index == target_index for key_index, target_index in indexed)
    )
    return {
        "target_indices_in_key_order": target_indices,
        "target_index_order_is_monotonic": None if not indexed else not backtracks,
        "target_index_mapping_is_identity": identity_mapping,
        "target_index_duplicate_count": duplicate_count,
        "target_index_backtrack_count": len(backtracks),
        "target_index_backtracks": backtracks,
    }


def summarize_key_trigger_timing(
    cache_time_sequences: list[list[float]],
    mat_time_sequences: list[list[float]],
) -> dict[str, object]:
    """Estimate the run-specific MAT-to-cache clock offset on equal-length trials."""

    n_compared = min(len(cache_time_sequences), len(mat_time_sequences))
    mismatch_indices = [
        index
        for index in range(n_compared)
        if len(cache_time_sequences[index]) != len(mat_time_sequences[index])
    ]
    mismatch_indices.extend(
        range(n_compared, max(len(cache_time_sequences), len(mat_time_sequences)))
    )

    exact_length_indices = [
        index
        for index in range(n_compared)
        if cache_time_sequences[index]
        and len(cache_time_sequences[index]) == len(mat_time_sequences[index])
    ]
    offsets = [
        mat_time - cache_time
        for index in exact_length_indices
        for cache_time, mat_time in zip(
            cache_time_sequences[index],
            mat_time_sequences[index],
        )
    ]
    summary: dict[str, object] = {
        "n_cache_trials": len(cache_time_sequences),
        "n_mat_key_trigger_trials": len(mat_time_sequences),
        "n_trials_compared": n_compared,
        "n_exact_length_trials": len(exact_length_indices),
        "exact_length_trial_indices": exact_length_indices,
        "length_mismatch_trial_indices": mismatch_indices,
        "n_keypress_pairs": len(offsets),
        "clock_offset_sec": None,
        "median_abs_residual_ms": None,
        "p95_abs_residual_ms": None,
        "max_abs_residual_ms": None,
        "n_residuals_within_1ms": 0,
        "fraction_residuals_within_1ms": None,
    }
    if not offsets:
        return summary

    clock_offset = statistics.median(offsets)
    absolute_residuals_ms = sorted(abs(offset - clock_offset) * 1000.0 for offset in offsets)
    within_1ms = sum(residual <= 1.0 for residual in absolute_residuals_ms)
    summary.update(
        {
            "clock_offset_sec": clock_offset,
            "median_abs_residual_ms": statistics.median(absolute_residuals_ms),
            "p95_abs_residual_ms": _linear_quantile(absolute_residuals_ms, 0.95),
            "max_abs_residual_ms": max(absolute_residuals_ms),
            "n_residuals_within_1ms": within_1ms,
            "fraction_residuals_within_1ms": within_1ms / len(offsets),
        }
    )
    return summary


def write_sequence_alignment_json(report: dict[str, object], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sequence_alignment_markdown(report: dict[str, object], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_sequence_alignment_markdown(report), encoding="utf-8")


def render_sequence_alignment_markdown(report: dict[str, object]) -> str:
    summary = report["summary"]
    run = report["run"]
    source_files = report["source_files"]
    lines = [
        "# NeuroDecodeKit Sequence Alignment",
        "",
        f"- Run: `{_md_inline(str(run.get('name', 'sequence-alignment')))}`",
        f"- Created UTC: `{_md_inline(str(run.get('created_at_utc', '')))}`",
        f"- Cache: `{_md_inline(str(source_files.get('cache', '')))}`",
        f"- MAT log: `{_md_inline(str(source_files.get('events', '')))}`",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key in (
        "n_key_sequences",
        "n_target_sequences",
        "exact_match_count",
        "usable_high_or_moderate_count",
        "mean_cer",
        "max_cer",
        "low_confidence_key_indices",
        "target_index_order_is_monotonic",
        "target_index_mapping_is_identity",
        "target_index_duplicate_count",
        "target_index_backtrack_count",
        "target_indices_in_key_order",
    ):
        lines.append(f"| `{key}` | {_format_value(summary.get(key))} |")
    lines.append(
        f"| `confidence_counts` | `{_md_inline(str(summary.get('confidence_counts', {})))}` |"
    )

    assignment = report.get("assignment") or {}
    trial_index_map = report.get("trial_index_map")
    lines.extend(
        [
            "",
            "## Assignment Evidence",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| `strategy` | `{_md_inline(str(assignment.get('strategy', 'unknown')))}` |",
            "| `uses_mat_trial_order` | "
            f"{_format_value(assignment.get('uses_mat_trial_order'))} |",
            "| `has_mat_key_trigger_evidence` | "
            f"{_format_value(assignment.get('has_mat_key_trigger_evidence'))} |",
            "| `uses_text_similarity_for_assignment` | "
            f"{_format_value(assignment.get('uses_text_similarity_for_assignment'))} |",
        ]
    )
    if trial_index_map:
        for key in (
            "raw_to_mat_trial_indices",
            "skipped_mat_trial_indices",
            "response_indices_match_performed_trials",
        ):
            lines.append(f"| `{key}` | {_format_value(trial_index_map.get(key))} |")

    resources = report.get("resources") or {}
    lines.extend(["", "## Resources", "", "| Metric | Value |", "|---|---:|"])
    for key in ("runtime_sec", "cache_bytes", "events_bytes"):
        lines.append(f"| `{key}` | {_format_value(resources.get(key))} |")

    response_summary = report.get("response_summary")
    if response_summary:
        lines.extend(["", "## Recorded Response Summary", "", "| Metric | Value |", "|---|---:|"])
        for key in (
            "n_target_sequences",
            "exact_match_count",
            "usable_high_or_moderate_count",
            "mean_cer",
            "max_cer",
            "low_confidence_key_indices",
            "target_index_order_is_monotonic",
            "target_index_mapping_is_identity",
            "target_index_duplicate_count",
            "target_index_backtrack_count",
            "target_indices_in_key_order",
        ):
            lines.append(f"| `{key}` | {_format_value(response_summary.get(key))} |")
        lines.append(
            "| `confidence_counts` | "
            f"`{_md_inline(str(response_summary.get('confidence_counts', {})))}` |"
        )

    timing_audit = report.get("key_trigger_timing_audit")
    if timing_audit:
        lines.extend(
            ["", "## MAT Key-Trigger Timing Audit", "", "| Metric | Value |", "|---|---:|"]
        )
        for key in (
            "n_cache_trials",
            "n_mat_key_trigger_trials",
            "n_trials_compared",
            "n_exact_length_trials",
            "length_mismatch_trial_indices",
            "n_keypress_pairs",
            "clock_offset_sec",
            "median_abs_residual_ms",
            "p95_abs_residual_ms",
            "max_abs_residual_ms",
            "n_residuals_within_1ms",
            "fraction_residuals_within_1ms",
        ):
            lines.append(f"| `{key}` | {_format_value(timing_audit.get(key))} |")

    warnings = report.get("warnings") or []
    if warnings:
        lines.extend(["", "## Warnings", ""])
        for warning in warnings:
            lines.append(f"- `{_md_inline(str(warning))}`")

    strict_assignment = bool(assignment.get("uses_mat_trial_order"))
    target_column = "MAT Target" if strict_assignment else "Best MAT Target"
    response_column = "MAT Response" if strict_assignment else "Best MAT Response"
    lines.extend(
        [
            "",
            "## Alignments",
            "",
            "| # | Target Conf. | Target CER | Response Conf. | Response CER | Typed | "
            f"{target_column} | {response_column} |",
            "|---:|---|---:|---|---:|---|---|---|",
        ]
    )
    response_by_key = {
        alignment.get("key_index"): alignment for alignment in report.get("response_alignments", [])
    }
    for alignment in report.get("alignments", []):
        response_alignment = response_by_key.get(alignment.get("key_index"), {})
        lines.append(
            "| "
            f"{alignment.get('key_index')} | "
            f"`{_md_inline(str(alignment.get('confidence')))}` | "
            f"{_format_value(alignment.get('cer'))} | "
            f"`{_md_inline(str(response_alignment.get('confidence', '')))}` | "
            f"{_format_value(response_alignment.get('cer'))} | "
            f"`{_md_inline(str(alignment.get('typed_text', '')))}` | "
            f"`{_md_inline(str(alignment.get('target_text') or ''))}` | "
            f"`{_md_inline(str(response_alignment.get('target_text') or ''))}` |"
        )
    return "\n".join(lines) + "\n"


def _make_key_sequence(
    *,
    index: int,
    chars: list[str],
    start_event_index: int,
    end_event_index: int,
    start_sec: float | None,
    end_sec: float | None,
    ended_by: str,
) -> KeySequence:
    text = "".join(chars).strip()
    return KeySequence(
        index=index,
        text=text,
        normalized_text=normalize_text(text),
        start_event_index=start_event_index,
        end_event_index=end_event_index,
        start_sec=start_sec,
        end_sec=end_sec,
        n_key_events=end_event_index - start_event_index + 1,
        ended_by=ended_by,
    )


def _label_to_text(label: str, *, space_label: str) -> str:
    if label == space_label:
        return " "
    return label


def _alignment_confidence(
    cer: float,
    *,
    high_confidence_cer: float,
    moderate_confidence_cer: float,
) -> str:
    if cer <= high_confidence_cer:
        return "high"
    if cer <= moderate_confidence_cer:
        return "moderate"
    return "low"


def _validate_confidence_thresholds(
    *,
    high_confidence_cer: float,
    moderate_confidence_cer: float,
) -> None:
    if high_confidence_cer < 0:
        raise ValueError("high_confidence_cer must be >= 0")
    if moderate_confidence_cer < high_confidence_cer:
        raise ValueError("moderate_confidence_cer must be >= high_confidence_cer")


def _compare_key_sequence_to_target(
    key_sequence: KeySequence,
    target: TargetSequence,
    *,
    high_confidence_cer: float,
    moderate_confidence_cer: float,
) -> SequenceAlignment:
    target_norm = normalize_text(target.text)
    typed_norm = normalize_text(key_sequence.text)
    edit_distance = levenshtein_distance(target_norm, typed_norm)
    cer = edit_distance / len(target_norm) if target_norm else math.inf
    return SequenceAlignment(
        key_index=key_sequence.index,
        target_index=target.index,
        target_source_path=target.source_path,
        typed_text=key_sequence.text,
        target_text=target.text,
        cer=cer,
        edit_distance=edit_distance,
        exact_match=target_norm == typed_norm,
        confidence=_alignment_confidence(
            cer,
            high_confidence_cer=high_confidence_cer,
            moderate_confidence_cer=moderate_confidence_cer,
        ),
    )


def _linear_quantile(sorted_values: list[float], quantile: float) -> float | None:
    if not sorted_values:
        return None
    if not 0.0 <= quantile <= 1.0:
        raise ValueError("quantile must be between 0 and 1")
    position = (len(sorted_values) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _safe_file_size(path: str | Path) -> int | None:
    try:
        return Path(path).stat().st_size
    except OSError:
        return None


def _string_vector(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if hasattr(value, "ravel"):
        try:
            return [str(item) for item in value.ravel().tolist() if isinstance(item, str)]
        except TypeError:
            return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if isinstance(item, str)]
    return []


def _target_source_priority(path: str) -> int:
    if path == "mat.pr_trials.sequence":
        return 5
    if path == "mat.pr_trials.sequences":
        return 4
    if path == "mat.sequences":
        return 3
    return 1


def _get_field(value: Any, field: str) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(field)
    if hasattr(value, field):
        return getattr(value, field)
    return None


def _payload_keys(value: Any) -> list[str]:
    if isinstance(value, dict):
        return list(value.keys())
    if hasattr(value, "_fieldnames"):
        return list(value._fieldnames)
    return []


def _iter_items(value: Any) -> list[Any]:
    if value is None:
        return []
    if hasattr(value, "ravel"):
        return list(value.ravel())
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _key_event_array_to_text(value: Any) -> str:
    chars: list[str] = []
    for event in _iter_items(value):
        if not _event_pressed(event):
            continue
        code = _event_code(event)
        if code in {0, None}:
            continue
        if code in {10, 13}:
            break
        if code == 8:
            if chars:
                chars.pop()
            continue
        if code == 32:
            chars.append(" ")
        elif 32 <= code < 127:
            chars.append(chr(code))
    return "".join(chars).strip()


def _event_pressed(event: Any) -> bool:
    pressed = _get_field(event, "Pressed")
    try:
        return int(pressed) == 1
    except (TypeError, ValueError):
        return False


def _event_code(event: Any) -> int | None:
    for field in ("CookedKey", "Keycode"):
        value = _get_field(event, field)
        try:
            code = int(value)
        except (TypeError, ValueError):
            continue
        if code:
            return code
    return None


def _decode_npz_metadata(value: Any) -> dict[str, Any]:
    if hasattr(value, "shape") and value.shape == ():
        text = str(value.item())
    else:
        text = str(value.tolist())
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return decoded if isinstance(decoded, dict) else {}


def _cache_summary_from_metadata(
    path: Path, metadata: dict[str, Any], *, n_labels: int
) -> dict[str, object]:
    dimensions = metadata.get("dimensions") or {}
    source_files = metadata.get("source_files") or {}
    return {
        "path": str(path),
        "bytes": _safe_stat_size(path),
        "kind": metadata.get("kind") or "unknown",
        "n_labels": n_labels,
        "n_events": dimensions.get("n_events"),
        "n_channels": dimensions.get("n_channels"),
        "n_timepoints": dimensions.get("n_timepoints"),
        "source_files": source_files,
        "warnings": list(metadata.get("warnings") or []),
    }


def _safe_stat_size(path: Path) -> int | None:
    try:
        return int(path.stat().st_size)
    except OSError:
        return None


def _format_value(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if value is None:
        return "`null`"
    return f"`{_md_inline(str(value))}`"


def _md_inline(value: str) -> str:
    return value.replace("|", "\\|").replace("`", "'")
