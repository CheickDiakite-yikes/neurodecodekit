"""A tiny template classifier for sanity checks.

This model averages windows by label and predicts the nearest class template. It
is not meant to be SOTA. Its job is to catch broken labels/windows before using
heavier models.
"""

from __future__ import annotations


class TemplateClassifier:
    """Nearest-template classifier for arrays shaped [samples, channels, times]."""

    def __init__(self) -> None:
        self.labels_: list[str] | None = None
        self.templates_ = None

    def fit(self, windows, labels):
        np = _require_numpy()
        x = np.asarray(windows)
        y = np.asarray(labels)
        if x.ndim != 3:
            raise ValueError(f"Expected windows [samples, channels, times], got {x.shape}")
        if len(x) != len(y):
            raise ValueError("windows and labels must have the same length")
        labels_unique = sorted(set(y.tolist()))
        templates = []
        for label in labels_unique:
            templates.append(x[y == label].mean(axis=0))
        self.labels_ = labels_unique
        self.templates_ = np.stack(templates, axis=0)
        return self

    def predict(self, windows):
        np = _require_numpy()
        if self.labels_ is None or self.templates_ is None:
            raise RuntimeError("TemplateClassifier must be fitted before predict().")
        x = np.asarray(windows)
        flat_x = x.reshape((x.shape[0], -1))
        flat_templates = self.templates_.reshape((self.templates_.shape[0], -1))
        # Squared Euclidean distance: [samples, classes]
        dists = ((flat_x[:, None, :] - flat_templates[None, :, :]) ** 2).sum(axis=2)
        pred_idx = dists.argmin(axis=1)
        return np.array([self.labels_[int(i)] for i in pred_idx])


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError("TemplateClassifier requires NumPy: `pip install numpy`.") from exc
    return np
