"""Dataset manifest utilities for SpanishBCBL-style files."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass, fields, replace
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class FileRecord:
    """One row in a dataset file manifest."""

    path: str
    repo_id: str | None = None
    size_bytes: int | None = None
    modality: str | None = None
    subject: str | None = None
    session: str | None = None
    block: str | None = None
    kind: str | None = None
    extension: str | None = None
    family: str | None = None
    warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "warnings", tuple(self.warnings or ()))

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, line: str) -> "FileRecord":
        payload = json.loads(line)
        known_fields = {field.name for field in fields(cls)}
        filtered = {key: value for key, value in payload.items() if key in known_fields}
        return cls(**filtered)


@dataclass(frozen=True)
class RawLogPair:
    """Candidate behavioral/log files for one raw recording file."""

    raw_path: str
    candidate_log_paths: tuple[str, ...]
    status: str
    warnings: tuple[str, ...] = ()


def infer_spanishbcbl_record(
    path: str,
    *,
    repo_id: str | None = "bcbl190626/SpanishBCBL",
    size_bytes: int | None = None,
) -> FileRecord:
    """Infer manifest fields from a SpanishBCBL/HF path.

    The public dataset card shows paths like:

    - `pinet2024_public/MEG/FIF/<recording_dir>/block1.fif`
    - `pinet2024_public/MEG/logs/...mat`
    - `pinet2024_public/EEG/EEG/...vhdr`
    - `pinet2024_public/EEG/logs/...mat`

    This parser is deliberately permissive because repository layouts may shift.
    """

    normalized = path.strip().replace("\\", "/")
    parts = normalized.split("/")
    upper_parts = [p.upper() for p in parts]
    ext = Path(normalized).suffix.lower() or None

    modality = None
    if "MEG" in upper_parts:
        modality = "MEG"
    elif "EEG" in upper_parts:
        modality = "EEG"

    upper_path = normalized.upper()

    kind = None
    if "LOCALIZER" in upper_path or "TAPPING" in upper_path:
        kind = "localizer"
    elif ext == ".mat" or "LOGS" in upper_parts:
        kind = "log"
    elif ext in {".fif", ".vhdr", ".eeg", ".vmrk"}:
        kind = "raw"

    eeg_identity = _spanishbcbl_eeg_recording_identity(normalized)
    subject = eeg_identity[0] if eeg_identity else None
    if subject is None:
        subject_match = re.search(r"(?:^|[/_\-])(S\d{1,3})(?=[/_\-.]|$)", normalized, flags=re.I)
        if subject_match:
            subject = subject_match.group(1).upper()
        else:
            subject_match = re.search(r"(?:^|[/_\-])(?:sub|subject)[_\-]?0*(\d{1,3})(?=[/_\-.]|$)", normalized, flags=re.I)
            if subject_match:
                subject = f"S{int(subject_match.group(1))}"
    if subject is None and modality == "MEG":
        subject = _meg_fif_recording_dir_subject(parts)

    block = eeg_identity[2] if eeg_identity else None
    block_match = re.search(r"block[_\-]?0*(\d+)", normalized, flags=re.I)
    if block is None and block_match:
        block = f"block{int(block_match.group(1))}"

    session = eeg_identity[1] if eeg_identity else None
    session_match = re.search(r"(?:^|[/_\-])(?:session|sess|ses)[_\-]?([A-Za-z0-9]+)", normalized, flags=re.I)
    if session is None and session_match:
        session = session_match.group(1)

    family = infer_file_family(modality=modality, kind=kind, extension=ext, path=normalized)
    warnings = infer_record_warnings(
        path=normalized,
        modality=modality,
        subject=subject,
        block=block,
        kind=kind,
        extension=ext,
        family=family,
    )

    return FileRecord(
        repo_id=repo_id,
        path=normalized,
        size_bytes=size_bytes,
        modality=modality,
        subject=subject,
        session=session,
        block=block,
        kind=kind,
        extension=ext,
        family=family,
        warnings=warnings,
    )


def infer_file_family(
    *,
    modality: str | None,
    kind: str | None,
    extension: str | None,
    path: str,
) -> str:
    """Return a stable coarse family for a SpanishBCBL-style file."""

    upper_path = path.upper()
    if kind == "localizer":
        return "localizer_or_tapping"
    if modality == "MEG" and kind == "raw" and extension == ".fif":
        return "meg_fif_raw"
    if modality == "MEG" and kind == "log" and extension == ".mat":
        return "meg_log_mat"
    if modality == "EEG" and kind == "raw" and extension in {".vhdr", ".eeg", ".vmrk"}:
        return f"eeg_brainvision_{extension.lstrip('.')}"
    if modality == "EEG" and kind == "log" and extension == ".mat":
        return "eeg_log_mat"
    if "LOGS" in upper_path and kind == "log":
        return "log_unknown_modality"
    return "unknown"


def infer_record_warnings(
    *,
    path: str,
    modality: str | None,
    subject: str | None,
    block: str | None,
    kind: str | None,
    extension: str | None,
    family: str,
) -> tuple[str, ...]:
    """Return explicit warnings for fields the parser could not infer safely."""

    warnings: list[str] = []
    if modality is None:
        warnings.append("unknown_modality")
    if kind is None:
        warnings.append("unknown_kind")
    if family == "unknown":
        warnings.append("unknown_file_family")
    if kind in {"raw", "log"} and subject is None:
        warnings.append("missing_subject")
    if modality == "MEG" and kind in {"raw", "log"} and block is None:
        warnings.append("missing_block")
    if kind == "log" and extension != ".mat":
        warnings.append("unexpected_log_extension")
    if extension is None and "." not in Path(path).name:
        warnings.append("missing_extension")
    return tuple(warnings)


def parse_manifest_input_line(
    line: str,
    *,
    repo_id: str | None = "bcbl190626/SpanishBCBL",
) -> FileRecord | None:
    """Parse one manifest input line.

    Supported forms:

    - plain repository path
    - JSON object with `path` and optional `size_bytes`/`size`
    - tab-separated `path<TAB>size_bytes` or `size_bytes<TAB>path`
    - whitespace-separated `size_bytes path`
    """

    stripped = line.strip().lstrip("\ufeff")
    if not stripped or stripped.startswith("#"):
        return None

    path = stripped
    size_bytes: int | None = None

    if stripped.startswith("{"):
        payload = json.loads(stripped)
        path_value = payload.get("path") or payload.get("rfilename") or payload.get("name")
        if not path_value:
            raise ValueError(f"JSON manifest line is missing a path: {stripped}")
        path = str(path_value)
        size_bytes = _coerce_size_bytes(payload.get("size_bytes", payload.get("size")))
    elif "\t" in stripped:
        parts = [part.strip() for part in stripped.split("\t") if part.strip()]
        path, size_bytes = _parse_path_size_parts(parts, original=stripped)
    else:
        first, sep, rest = stripped.partition(" ")
        if sep and _coerce_size_bytes(first) is not None:
            size_bytes = _coerce_size_bytes(first)
            path = rest.strip()

    return infer_spanishbcbl_record(path, repo_id=repo_id, size_bytes=size_bytes)


def build_manifest_from_paths(
    paths: Iterable[str],
    *,
    repo_id: str | None = "bcbl190626/SpanishBCBL",
) -> list[FileRecord]:
    """Build manifest records from plain paths."""

    records = []
    for raw_path in paths:
        record = parse_manifest_input_line(raw_path, repo_id=repo_id)
        if record is not None:
            records.append(record)
    return _assign_meg_fif_sessions(records)


def write_jsonl(records: Iterable[FileRecord], path: str | Path) -> None:
    """Write manifest records to JSONL."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(record.to_json() + "\n")


def read_jsonl(path: str | Path) -> list[FileRecord]:
    """Read manifest records from JSONL."""

    with Path(path).open("r", encoding="utf-8") as f:
        return [FileRecord.from_json(line) for line in f if line.strip()]


def summarize_manifest(records: Iterable[FileRecord]) -> dict[str, object]:
    """Return simple counts for a manifest."""

    records = list(records)
    by_modality = Counter(r.modality or "UNKNOWN" for r in records)
    by_kind = Counter(r.kind or "UNKNOWN" for r in records)
    by_ext = Counter(r.extension or "UNKNOWN" for r in records)
    by_family = Counter(r.family or "UNKNOWN" for r in records)
    subjects = sorted({r.subject for r in records if r.subject})
    known_bytes = sum(r.size_bytes or 0 for r in records)
    record_warnings = [
        {
            "path": r.path,
            "warnings": list(r.warnings),
        }
        for r in records
        if r.warnings
    ]
    raw_log_pairs = pair_raw_records_to_logs(records)
    pair_status = Counter(pair.status for pair in raw_log_pairs)
    return {
        "n_files": len(records),
        "by_modality": dict(by_modality),
        "by_kind": dict(by_kind),
        "by_extension": dict(by_ext),
        "by_family": dict(by_family),
        "n_subjects_detected": len(subjects),
        "subjects_preview": subjects[:20],
        "known_bytes": known_bytes,
        "n_files_with_known_size": sum(1 for r in records if r.size_bytes is not None),
        "n_record_warnings": len(record_warnings),
        "record_warnings_preview": record_warnings[:20],
        "raw_log_pairing": {
            "n_raw_records": len(raw_log_pairs),
            "by_status": dict(pair_status),
            "pairs_preview": [
                {
                    "raw_path": pair.raw_path,
                    "candidate_log_paths": list(pair.candidate_log_paths),
                    "status": pair.status,
                    "warnings": list(pair.warnings),
                }
                for pair in raw_log_pairs[:20]
            ],
        },
    }


def pair_raw_records_to_logs(records: Iterable[FileRecord]) -> list[RawLogPair]:
    """Return candidate log files for each raw manifest record."""

    records = list(records)
    raw_records = sorted((r for r in records if r.kind == "raw"), key=_record_sort_key)
    log_records = sorted((r for r in records if r.kind == "log"), key=_record_sort_key)
    return [pair_raw_record_to_logs(raw, log_records) for raw in raw_records]


def pair_raw_record_to_logs(raw: FileRecord, logs: Iterable[FileRecord]) -> RawLogPair:
    """Pair one raw file with exact or fallback candidate log records."""

    logs = [
        log
        for log in logs
        if log.kind == "log"
        and (raw.modality is None or log.modality is None or log.modality == raw.modality)
        and (raw.subject is None or log.subject is None or log.subject == raw.subject)
    ]
    exact = [
        log
        for log in logs
        if raw.block
        and log.block == raw.block
        and _session_compatible(raw.session, log.session)
    ]
    subject_level = [log for log in logs if _session_compatible(raw.session, log.session)]

    warnings: list[str] = []
    if exact:
        candidates = exact
        status = "exact" if len(exact) == 1 else "ambiguous"
        if len(exact) > 1:
            warnings.append("multiple_exact_logs")
    elif subject_level:
        candidates = subject_level
        status = "fallback_subject" if len(subject_level) == 1 else "ambiguous"
        if raw.block:
            warnings.append("no_block_matched_log")
        else:
            warnings.append("raw_missing_block_for_pairing")
        if len(subject_level) > 1:
            warnings.append("multiple_subject_logs")
    else:
        candidates = []
        status = "missing_log"
        warnings.append("no_candidate_log")

    return RawLogPair(
        raw_path=raw.path,
        candidate_log_paths=tuple(log.path for log in candidates),
        status=status,
        warnings=tuple(warnings),
    )


def candidate_logs_for_raw(raw: FileRecord, records: Iterable[FileRecord]) -> list[FileRecord]:
    """Return candidate log records for a raw record using manifest v1 pairing rules."""

    logs = [record for record in records if record.kind == "log"]
    pair = pair_raw_record_to_logs(raw, logs)
    paths = set(pair.candidate_log_paths)
    return [record for record in logs if record.path in paths]


def _parse_path_size_parts(parts: list[str], *, original: str) -> tuple[str, int | None]:
    if len(parts) < 2:
        return original, None
    first_size = _coerce_size_bytes(parts[0])
    last_size = _coerce_size_bytes(parts[-1])
    if first_size is not None:
        return "\t".join(parts[1:]), first_size
    if last_size is not None:
        return "\t".join(parts[:-1]), last_size
    return original, None


def _coerce_size_bytes(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        size = int(value)
    except (TypeError, ValueError):
        return None
    if size < 0:
        return None
    return size


def _record_sort_key(record: FileRecord) -> tuple[str, str, str, str]:
    return (record.modality or "", record.subject or "", record.block or "", record.path)


def _session_compatible(a: str | None, b: str | None) -> bool:
    return a is None or b is None or a == b


def _meg_fif_recording_dir_subject(parts: list[str]) -> str | None:
    """Infer S-prefixed subject IDs from current HF MEG/FIF recording folders."""

    upper_parts = [part.upper() for part in parts]
    try:
        meg_index = upper_parts.index("MEG")
        fif_index = upper_parts.index("FIF", meg_index + 1)
    except ValueError:
        return None
    if len(parts) <= fif_index + 1:
        return None
    recording_dir = parts[fif_index + 1]
    match = re.match(r"0*(\d{1,3})(?:_+|$)", recording_dir)
    if not match:
        return None
    return f"S{int(match.group(1))}"


def _spanishbcbl_eeg_recording_identity(
    path: str,
) -> tuple[str, str, str | None] | None:
    """Parse the official ``002_DECOMEG_S1_*_task1.vhdr`` naming contract.

    The leading number is the participant. The ``S1``/``S2`` token is the
    session, not the subject. Keeping those roles separate is required for
    exact BrainVision-to-MAT pairing.
    """

    name = Path(path).name
    match = re.fullmatch(
        r"0*(?P<subject>\d{1,3})_DECOMEG_S(?P<session>\d+)(?:bis)?_"
        r"[^_./]+_(?P<task>task1|task2|tapping)(?:bis)?(?:_\d+)?"
        r"\.(?:eeg|vhdr|vmrk)",
        name,
        flags=re.I,
    )
    if match is None:
        match = re.fullmatch(
            r"0*(?P<subject>\d{1,3})_DECOMEG_S(?P<session>\d+)(?:bis)?_"
            r"[^_./]+\.(?:eeg|vhdr|vmrk)",
            name,
            flags=re.I,
        )
    if match is None:
        return None
    task = (match.groupdict().get("task") or "").lower()
    block = {"task1": "block1", "task2": "block2"}.get(task)
    return (
        f"S{int(match.group('subject'))}",
        str(int(match.group("session"))),
        block,
    )


def _assign_meg_fif_sessions(records: list[FileRecord]) -> list[FileRecord]:
    """Assign session numbers from MEG/FIF recording-date order when absent."""

    dates_by_subject: dict[str, set[str]] = {}
    for record in records:
        if record.session is not None or record.subject is None:
            continue
        date = _meg_fif_recording_date(record.path)
        if date is None:
            continue
        dates_by_subject.setdefault(record.subject, set()).add(date)

    session_by_subject_date = {
        subject: {date: str(index + 1) for index, date in enumerate(sorted(dates))}
        for subject, dates in dates_by_subject.items()
    }
    updated: list[FileRecord] = []
    for record in records:
        if record.session is not None or record.subject is None:
            updated.append(record)
            continue
        date = _meg_fif_recording_date(record.path)
        session = session_by_subject_date.get(record.subject, {}).get(date)
        updated.append(replace(record, session=session) if session else record)
    return updated


def _meg_fif_recording_date(path: str) -> str | None:
    parts = path.split("/")
    upper_parts = [part.upper() for part in parts]
    try:
        meg_index = upper_parts.index("MEG")
        fif_index = upper_parts.index("FIF", meg_index + 1)
    except ValueError:
        return None
    if len(parts) <= fif_index + 2:
        return None
    date = parts[fif_index + 2]
    if re.fullmatch(r"\d{6}", date):
        return date
    return None
