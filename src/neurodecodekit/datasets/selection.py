"""Safe tiny-selection helpers for huge neurodata repositories."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from neurodecodekit.datasets.manifest import FileRecord, candidate_logs_for_raw, read_jsonl


@dataclass(frozen=True)
class TinySelection:
    """A small set of files approved for selective download."""

    repo_id: str
    records: list[FileRecord]
    purpose: str = "b2q-mini-v0"
    dry_run_required_by_default: bool = True

    @property
    def allow_patterns(self) -> list[str]:
        return [record.path for record in self.records]

    @property
    def estimated_bytes(self) -> int | None:
        if any(r.size_bytes is None for r in self.records):
            return None
        return sum(int(r.size_bytes or 0) for r in self.records)

    def to_dict(self) -> dict[str, object]:
        return {
            "repo_id": self.repo_id,
            "purpose": self.purpose,
            "dry_run_required_by_default": self.dry_run_required_by_default,
            "estimated_bytes": self.estimated_bytes,
            "records": [asdict(record) for record in self.records],
        }


class SelectionError(ValueError):
    """Raised when a tiny data selection cannot be created safely."""


def _sort_key(record: FileRecord) -> tuple[str, str, str]:
    return (record.subject or "", record.block or "", record.path)


def select_tiny_records(
    records: Iterable[FileRecord],
    *,
    modality: str = "MEG",
    subject: str | None = None,
    blocks: int = 1,
    include_logs: bool = True,
) -> TinySelection:
    """Select a tiny, safe subset from manifest records.

    The selector intentionally chooses the smallest useful slice: one subject and
    a small number of raw blocks, plus relevant logs when available.
    """

    records = list(records)
    if blocks < 1:
        raise SelectionError("blocks must be >= 1")

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

    # Prefer subjects with explicit IDs. If no subject was supplied, choose the
    # first subject that has raw data, sorted for deterministic behavior.
    if subject is None:
        subjects = sorted({r.subject for r in candidates if r.subject})
        if not subjects:
            raise SelectionError("No subject IDs could be inferred from raw candidates.")
        subject = subjects[0]

    subject_raw = sorted([r for r in candidates if r.subject == subject], key=_sort_key)
    if not subject_raw:
        raise SelectionError(f"No raw {modality} candidates found for subject {subject}.")

    if modality == "MEG":
        # Pick by unique block where possible to avoid multiple large files.
        selected_raw: list[FileRecord] = []
        seen_blocks: set[str] = set()
        for record in subject_raw:
            block_id = record.block or record.path
            if block_id in seen_blocks:
                continue
            selected_raw.append(record)
            seen_blocks.add(block_id)
            if len(selected_raw) >= blocks:
                break
    else:
        # EEG files are often triplets; for now keep the first files up to a
        # small cap. Codex should improve this once exact layout is observed.
        selected_raw = subject_raw[: max(blocks, 1) * 3]

    selected = list(selected_raw)
    if include_logs:
        selected_logs: list[FileRecord] = []
        seen_log_paths: set[str] = set()
        for raw in selected_raw:
            for log in candidate_logs_for_raw(raw, records):
                if log.path in seen_log_paths:
                    continue
                selected_logs.append(log)
                seen_log_paths.add(log.path)
        selected.extend(sorted(selected_logs, key=_sort_key))

    repo_ids = sorted({r.repo_id for r in selected if r.repo_id})
    repo_id = repo_ids[0] if repo_ids else "bcbl190626/SpanishBCBL"
    return TinySelection(repo_id=repo_id, records=selected)


def write_selection(selection: TinySelection, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(selection.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_selection(path: str | Path) -> TinySelection:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    records = [FileRecord(**row) for row in payload["records"]]
    return TinySelection(repo_id=payload["repo_id"], records=records, purpose=payload.get("purpose", "b2q-mini-v0"))


def select_tiny_from_manifest(
    manifest_path: str | Path,
    *,
    modality: str = "MEG",
    subject: str | None = None,
    blocks: int = 1,
    include_logs: bool = True,
) -> TinySelection:
    records = read_jsonl(manifest_path)
    return select_tiny_records(
        records,
        modality=modality,
        subject=subject,
        blocks=blocks,
        include_logs=include_logs,
    )
