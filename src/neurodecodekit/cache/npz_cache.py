"""Small NPZ cache helpers.

NPZ is the v0 cache format because it is simple. Zarr should replace it for
larger real caches once the schema stabilizes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("NPZ cache helpers require NumPy: `pip install numpy`.") from exc
    return np


def save_npz_cache(
    path: str | Path,
    *,
    windows,
    labels,
    metadata: dict[str, Any],
    extra_arrays: dict[str, Any] | None = None,
) -> None:
    """Save windows/labels/metadata to a compressed NPZ file."""

    np = _require_numpy()
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    arrays = {
        "windows": windows,
        "labels": labels,
        "metadata": json.dumps(metadata, sort_keys=True),
    }
    if extra_arrays:
        arrays.update(extra_arrays)
    np.savez_compressed(
        output,
        **arrays,
    )


def load_npz_cache(path: str | Path) -> dict[str, Any]:
    """Load a compressed NPZ cache file."""

    np = _require_numpy()
    with np.load(Path(path), allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata"]))
        loaded = {
            "windows": data["windows"],
            "labels": data["labels"],
            "metadata": metadata,
        }
        for key in data.files:
            if key not in loaded:
                loaded[key] = data[key]
        return loaded
