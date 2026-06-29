"""Dataset manifest utilities for SpanishBCBL-style files."""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


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

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

    @classmethod
    def from_json(cls, line: str) -> "FileRecord":
        return cls(**json.loads(line))


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

    normalized = path.replace("\\", "/")
    parts = normalized.split("/")
    upper_parts = [p.upper() for p in parts]
    ext = Path(normalized).suffix.lower() or None

    modality = None
    if "MEG" in upper_parts:
        modality = "MEG"
    elif "EEG" in upper_parts:
        modality = "EEG"

    kind = None
    if ext == ".mat" or "LOGS" in upper_parts:
        kind = "log"
    elif ext in {".fif", ".vhdr", ".eeg", ".vmrk"}:
        kind = "raw"
    elif "LOCALIZER" in normalized.upper() or "TAPPING" in normalized.upper():
        kind = "localizer"

    subject = None
    subject_match = re.search(r"(?:^|[/_\-])(S\d{1,3})(?:[/_\-.]|$)", normalized, flags=re.I)
    if subject_match:
        subject = subject_match.group(1).upper()

    block = None
    block_match = re.search(r"(block\d+)", normalized, flags=re.I)
    if block_match:
        block = block_match.group(1).lower()

    session = None
    session_match = re.search(r"(?:session|sess|ses)[_\-]?([A-Za-z0-9]+)", normalized, flags=re.I)
    if session_match:
        session = session_match.group(1)

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
    )


def build_manifest_from_paths(
    paths: Iterable[str],
    *,
    repo_id: str | None = "bcbl190626/SpanishBCBL",
) -> list[FileRecord]:
    """Build manifest records from plain paths."""

    records = []
    for raw_path in paths:
        path = raw_path.strip()
        if not path or path.startswith("#"):
            continue
        records.append(infer_spanishbcbl_record(path, repo_id=repo_id))
    return records


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
    subjects = sorted({r.subject for r in records if r.subject})
    known_bytes = sum(r.size_bytes or 0 for r in records)
    return {
        "n_files": len(records),
        "by_modality": dict(by_modality),
        "by_kind": dict(by_kind),
        "by_extension": dict(by_ext),
        "n_subjects_detected": len(subjects),
        "subjects_preview": subjects[:20],
        "known_bytes": known_bytes,
    }
