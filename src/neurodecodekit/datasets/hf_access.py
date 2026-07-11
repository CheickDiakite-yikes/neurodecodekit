"""Optional Hugging Face Hub helpers.

Imports are kept inside functions so the base package stays lightweight.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HubFileRecord:
    """One repository file discovered through metadata-only Hub access."""

    path: str
    size_bytes: int | None


def _require_hf():
    try:
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Hugging Face helpers require `pip install -e '.[hf]'` "
            "or `pip install huggingface_hub`."
        ) from exc
    return HfApi, snapshot_download


def list_repo_files(repo_id: str, *, repo_type: str = "dataset") -> list[str]:
    """List files in a Hugging Face repository."""

    HfApi, _ = _require_hf()
    return list(HfApi().list_repo_files(repo_id=repo_id, repo_type=repo_type))


def list_repo_file_records(
    repo_id: str,
    *,
    repo_type: str = "dataset",
    revision: str | None = None,
) -> tuple[str, list[HubFileRecord]]:
    """Return the resolved revision and file sizes without downloading payloads."""

    HfApi, _ = _require_hf()
    info = HfApi().repo_info(
        repo_id=repo_id,
        repo_type=repo_type,
        revision=revision,
        files_metadata=True,
    )
    records = [
        HubFileRecord(path=item.rfilename, size_bytes=getattr(item, "size", None))
        for item in info.siblings
    ]
    return str(info.sha), records


def write_file_list(paths: Iterable[str], out: str | Path) -> None:
    """Write repository paths one per line."""

    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(paths) + "\n", encoding="utf-8")


def write_file_record_list(records: Iterable[HubFileRecord], out: str | Path) -> None:
    """Write JSONL that ``manifest-from-paths`` can consume with exact sizes."""

    output = Path(out)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(asdict(record), sort_keys=True) + "\n")


def selective_snapshot_download(
    *,
    repo_id: str,
    allow_patterns: list[str],
    local_dir: str | Path,
    repo_type: str = "dataset",
    revision: str | None = None,
    max_workers: int = 1,
    dry_run: bool = True,
) -> str | None:
    """Download selected files from a HF repo, defaulting to dry-run.

    Returns the local path when a real download occurs. Returns None for dry-runs.
    """

    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")

    if dry_run:
        print("DRY RUN: no files will be downloaded.")
        print(f"repo_id={repo_id!r} repo_type={repo_type!r} local_dir={str(local_dir)!r}")
        print(f"revision={revision!r} max_workers={max_workers}")
        print("allow_patterns:")
        for pattern in allow_patterns:
            print(f"  - {pattern}")
        return None

    _, snapshot_download = _require_hf()
    return snapshot_download(
        repo_id=repo_id,
        repo_type=repo_type,
        local_dir=str(local_dir),
        allow_patterns=allow_patterns,
        revision=revision,
        max_workers=max_workers,
    )
