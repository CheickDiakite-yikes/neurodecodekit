"""Synthetic data for the smallest possible research loop."""

from __future__ import annotations

from pathlib import Path


ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ ")


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("Synthetic shard generation requires NumPy: `pip install numpy`.") from exc
    return np


def make_synthetic_windows(
    *,
    samples: int = 128,
    channels: int = 8,
    times: int = 25,
    classes: int = 8,
    seed: int = 7,
):
    """Create a toy neural shard where class identity is weakly encoded.

    This is not a neuroscience simulation. It is a deterministic smoke test for
    cache/model/report plumbing.
    """

    np = _require_numpy()
    rng = np.random.default_rng(seed)
    labels_idx = rng.integers(0, classes, size=samples)
    windows = rng.normal(0, 0.2, size=(samples, channels, times)).astype("float32")

    # Encode the class as a simple bump pattern in the first few channels.
    center = times // 2
    for i, label in enumerate(labels_idx):
        channel = int(label % channels)
        windows[i, channel, max(0, center - 1) : min(times, center + 2)] += 1.0

    labels = np.array([ALPHABET[i % len(ALPHABET)] for i in labels_idx], dtype="U1")
    metadata = {
        "kind": "synthetic",
        "samples": samples,
        "channels": channels,
        "times": times,
        "classes": classes,
        "seed": seed,
        "note": "Toy smoke-test data, not real neural data.",
    }
    return windows, labels, metadata


def save_synthetic_npz(
    out: str | Path,
    *,
    samples: int = 128,
    channels: int = 8,
    times: int = 25,
    classes: int = 8,
    seed: int = 7,
) -> dict[str, object]:
    """Generate and save a synthetic shard."""

    from neurodecodekit.cache.npz_cache import save_npz_cache

    windows, labels, metadata = make_synthetic_windows(
        samples=samples,
        channels=channels,
        times=times,
        classes=classes,
        seed=seed,
    )
    save_npz_cache(out, windows=windows, labels=labels, metadata=metadata)
    path = Path(out)
    return {
        "path": str(path),
        "bytes": path.stat().st_size,
        "shape": tuple(windows.shape),
        "n_labels": len(set(labels.tolist())),
    }
