"""Safe tiny-selection helpers for huge neurodata repositories."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from neurodecodekit.datasets.manifest import FileRecord, pair_raw_record_to_logs, read_jsonl


BYTES_PER_GB = 1024**3
DEFAULT_MAX_FILES = 8
DEFAULT_MAX_TOTAL_GB = 5.0
DEFAULT_MAX_TOTAL_BYTES = int(DEFAULT_MAX_TOTAL_GB * BYTES_PER_GB)


@dataclass(frozen=True)
class TinySelection:
    """A small set of files approved for selective download."""

    repo_id: str
    records: list[FileRecord]
    purpose: str = "b2q-mini-v0"
    dry_run_required_by_default: bool = True
    max_files: int | None = DEFAULT_MAX_FILES
    max_total_bytes: int | None = DEFAULT_MAX_TOTAL_BYTES
    safety_warnings: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "safety_warnings", tuple(self.safety_warnings or ()))

    @property
    def allow_patterns(self) -> list[str]:
        return [record.path for record in self.records]

    @property
    def n_files(self) -> int:
        return len(self.records)

    @property
    def known_bytes(self) -> int:
        return sum(int(r.size_bytes or 0) for r in self.records if r.size_bytes is not None)

    @property
    def missing_size_count(self) -> int:
        return sum(1 for r in self.records if r.size_bytes is None)

    @property
    def estimated_bytes(self) -> int | None:
        if any(r.size_bytes is None for r in self.records):
            return None
        return self.known_bytes

    def to_dict(self) -> dict[str, object]:
        return {
            "repo_id": self.repo_id,
            "purpose": self.purpose,
            "dry_run_required_by_default": self.dry_run_required_by_default,
            "estimated_bytes": self.estimated_bytes,
            "known_bytes": self.known_bytes,
            "missing_size_count": self.missing_size_count,
            "max_files": self.max_files,
            "max_total_bytes": self.max_total_bytes,
            "safety_warnings": list(self.safety_warnings),
            "safety": {
                "n_files": self.n_files,
                "estimated_bytes": self.estimated_bytes,
                "known_bytes": self.known_bytes,
                "missing_size_count": self.missing_size_count,
                "max_files": self.max_files,
                "max_total_bytes": self.max_total_bytes,
                "warnings": list(self.safety_warnings),
            },
            "records": [asdict(record) for record in self.records],
        }


class SelectionError(ValueError):
    """Raised when a tiny data selection cannot be created safely."""


@dataclass(frozen=True)
class _RawCandidate:
    raw: FileRecord
    logs: tuple[FileRecord, ...]
    pairing_status: str
    estimated_bytes: int | None
    missing_size_count: int


def _sort_key(record: FileRecord) -> tuple[str, str, str]:
    return (record.subject or "", record.block or "", record.path)


def select_tiny_records(
    records: Iterable[FileRecord],
    *,
    modality: str = "MEG",
    subject: str | None = None,
    blocks: int = 1,
    include_logs: bool = True,
    max_files: int | None = DEFAULT_MAX_FILES,
    max_total_bytes: int | None = DEFAULT_MAX_TOTAL_BYTES,
) -> TinySelection:
    """Select a tiny, safe subset from manifest records.

    The selector intentionally chooses the smallest useful slice: one subject and
    a small number of raw blocks, plus relevant logs when available. When file
    sizes are present, the selector prefers the smallest complete raw+log
    candidate before falling back to path order.
    """

    records = list(records)
    if blocks < 1:
        raise SelectionError("blocks must be >= 1")
    validate_selection_limits([], max_files=max_files, max_total_bytes=max_total_bytes)

    modality = modality.upper()
    subject = subject.upper() if subject else None

    candidates = [
        r
        for r in records
        if (r.modality or "").upper() == modality
        and r.kind == "raw"
        and (subject is None or r.subject == subject)
    ]
    if modality == "MEG":
        candidates = [r for r in candidates if r.extension == ".fif"]
    elif modality == "EEG":
        candidates = [r for r in candidates if r.extension in {".vhdr", ".eeg", ".vmrk"}]

    if not candidates:
        subject_msg = f" for subject {subject}" if subject else ""
        raise SelectionError(f"No raw {modality} candidates found{subject_msg}.")

    raw_candidates = sorted(
        [_make_raw_candidate(raw, records, include_logs=include_logs) for raw in candidates],
        key=_candidate_sort_key,
    )

    # Prefer subjects with explicit IDs. If no subject was supplied, choose the
    # subject attached to the best safe candidate rather than blindly taking the
    # first lexicographic path.
    if subject is None:
        first_subject_candidate = next(
            (candidate for candidate in raw_candidates if candidate.raw.subject),
            None,
        )
        if first_subject_candidate is None:
            raise SelectionError("No subject IDs could be inferred from raw candidates.")
        subject = first_subject_candidate.raw.subject

    subject_candidates = [candidate for candidate in raw_candidates if candidate.raw.subject == subject]
    if not subject_candidates:
        raise SelectionError(f"No raw {modality} candidates found for subject {subject}.")

    if modality == "MEG":
        # Pick by unique block where possible to avoid multiple large files.
        selected_candidates: list[_RawCandidate] = []
        seen_blocks: set[str] = set()
        for candidate in subject_candidates:
            block_id = candidate.raw.block or candidate.raw.path
            if block_id in seen_blocks:
                continue
            selected_candidates.append(candidate)
            seen_blocks.add(block_id)
            if len(selected_candidates) >= blocks:
                break
    else:
        # EEG files are often triplets; for now keep the first files up to a
        # small cap. Codex should improve this once exact layout is observed.
        selected_candidates = subject_candidates[: max(blocks, 1) * 3]

    selected = [candidate.raw for candidate in selected_candidates]
    if include_logs:
        selected_logs: list[FileRecord] = []
        seen_log_paths: set[str] = set()
        for candidate in selected_candidates:
            for log in candidate.logs:
                if log.path in seen_log_paths:
                    continue
                selected_logs.append(log)
                seen_log_paths.add(log.path)
        selected.extend(sorted(selected_logs, key=_sort_key))

    safety_warnings = validate_selection_limits(
        selected,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
    )
    repo_ids = sorted({r.repo_id for r in selected if r.repo_id})
    repo_id = repo_ids[0] if repo_ids else "bcbl190626/SpanishBCBL"
    return TinySelection(
        repo_id=repo_id,
        records=selected,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
        safety_warnings=safety_warnings,
    )


def write_selection(selection: TinySelection, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(selection.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def read_selection(path: str | Path) -> TinySelection:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = [FileRecord(**row) for row in payload["records"]]
    safety = payload.get("safety") or {}
    max_files = payload.get("max_files", safety.get("max_files", DEFAULT_MAX_FILES))
    max_total_bytes = payload.get(
        "max_total_bytes",
        safety.get("max_total_bytes", DEFAULT_MAX_TOTAL_BYTES),
    )
    warnings = payload.get("safety_warnings", safety.get("warnings", ()))
    return TinySelection(
        repo_id=payload["repo_id"],
        records=records,
        purpose=payload.get("purpose", "b2q-mini-v0"),
        dry_run_required_by_default=payload.get("dry_run_required_by_default", True),
        max_files=max_files,
        max_total_bytes=max_total_bytes,
        safety_warnings=tuple(warnings),
    )


def select_tiny_from_manifest(
    manifest_path: str | Path,
    *,
    modality: str = "MEG",
    subject: str | None = None,
    blocks: int = 1,
    include_logs: bool = True,
    max_files: int | None = DEFAULT_MAX_FILES,
    max_total_bytes: int | None = DEFAULT_MAX_TOTAL_BYTES,
) -> TinySelection:
    records = read_jsonl(manifest_path)
    return select_tiny_records(
        records,
        modality=modality,
        subject=subject,
        blocks=blocks,
        include_logs=include_logs,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
    )


def validate_selection_limits(
    records: Iterable[FileRecord],
    *,
    max_files: int | None,
    max_total_bytes: int | None,
    require_known_sizes: bool = False,
) -> tuple[str, ...]:
    """Validate selected files against file-count and byte limits.

    Unknown sizes are allowed for planning so a manifest from plain paths still
    works, but real execution can opt into strict known-size enforcement.
    """

    records = list(records)
    if max_files is not None and max_files < 1:
        raise SelectionError("max_files must be >= 1 when provided")
    if max_total_bytes is not None and max_total_bytes < 1:
        raise SelectionError("max_total_bytes must be >= 1 when provided")
    if max_files is not None and len(records) > max_files:
        raise SelectionError(f"Selection has {len(records)} files, exceeding max_files={max_files}.")

    known_bytes = sum(
        int(record.size_bytes or 0)
        for record in records
        if record.size_bytes is not None
    )
    missing_size_count = sum(1 for record in records if record.size_bytes is None)
    if max_total_bytes is not None and known_bytes > max_total_bytes:
        raise SelectionError(
            "Selection has at least "
            f"{format_bytes(known_bytes)}, exceeding max_total_bytes={format_bytes(max_total_bytes)}."
        )

    warnings: list[str] = []
    if missing_size_count:
        warning = f"size_unknown_for_{missing_size_count}_files"
        if require_known_sizes:
            raise SelectionError(
                "Cannot confirm selected download size because "
                f"{missing_size_count} file(s) are missing size metadata. "
                "Use a manifest with file sizes, lower max-files, or pass --allow-unknown-size "
                "with --execute after reviewing the exact file list."
            )
        warnings.append(warning)
    return tuple(warnings)


def gb_to_bytes(value: float | None) -> int | None:
    if value is None:
        return None
    if value <= 0:
        raise SelectionError("max-total-gb must be > 0 when provided")
    return int(value * BYTES_PER_GB)


def format_bytes(n_bytes: int | None) -> str:
    if n_bytes is None:
        return "unknown"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(n_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{n_bytes} B"


def _make_raw_candidate(
    raw: FileRecord,
    records: Iterable[FileRecord],
    *,
    include_logs: bool,
) -> _RawCandidate:
    logs = [record for record in records if record.kind == "log"]
    pair = pair_raw_record_to_logs(raw, logs)
    log_by_path = {record.path: record for record in logs}
    selected_logs = tuple(
        log_by_path[path]
        for path in pair.candidate_log_paths
        if path in log_by_path
    )
    candidate_records: tuple[FileRecord, ...]
    if include_logs:
        candidate_records = (raw, *selected_logs)
    else:
        candidate_records = (raw,)
    missing_size_count = sum(1 for record in candidate_records if record.size_bytes is None)
    estimated_bytes = None
    if missing_size_count == 0:
        estimated_bytes = sum(int(record.size_bytes or 0) for record in candidate_records)
    return _RawCandidate(
        raw=raw,
        logs=selected_logs if include_logs else (),
        pairing_status=pair.status,
        estimated_bytes=estimated_bytes,
        missing_size_count=missing_size_count,
    )


def _candidate_sort_key(candidate: _RawCandidate) -> tuple[int, int, int, str, str, str]:
    status_rank = {
        "exact": 0,
        "fallback_subject": 1,
        "ambiguous": 2,
        "missing_log": 3,
    }.get(candidate.pairing_status, 4)
    size_unknown_rank = 1 if candidate.estimated_bytes is None else 0
    size_value = candidate.estimated_bytes or 0
    raw_sort = _sort_key(candidate.raw)
    return (
        status_rank,
        size_unknown_rank,
        size_value,
        raw_sort[0],
        raw_sort[1],
        raw_sort[2],
    )
