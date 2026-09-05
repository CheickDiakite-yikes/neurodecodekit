"""Compact, target-blind inference for a fixed vocabulary of imagined words.

Inputs are already selected, fixed-length EEG epochs [trials, channels, samples].
This module does not read recordings, event codes, annotations, or split files.
It makes no claim that covariance features isolate neural language activity.
Numerical dependencies are optional and imported only when methods are called.
"""

from __future__ import annotations

import json
import math
import time
import warnings
from pathlib import Path


SCHEMA = "neurodecodekit.imagined_word_logcov.v1"
_ARRAY_KEYS = {"metadata", "classes", "mean", "scale", "coef", "intercept"}


def _dependencies():
    try:
        import numpy as np
        from scipy.linalg import eigh
        from threadpoolctl import threadpool_limits
    except ImportError as exc:
        raise RuntimeError(
            "Imagined-word decoding requires numpy, scipy, scikit-learn and threadpoolctl."
        ) from exc
    return np, eigh, threadpool_limits


def _epochs(np, X, *, shape=None):
    values = np.asarray(X, dtype=np.float64)
    if values.ndim != 3 or min(values.shape) < 1 or values.shape[2] < 2:
        raise ValueError("X must be nonempty [trials, channels, samples] with at least 2 samples")
    if shape is not None and values.shape[1:] != shape:
        raise ValueError("prediction channels and samples must match training geometry")
    if not np.isfinite(values).all():
        raise ValueError("X must contain only finite values")
    return values


def _shrinkage(value):
    value = float(value)
    if not math.isfinite(value) or not 0 < value <= 1:
        raise ValueError("shrinkage must be in (0, 1]")
    return value


def covariance_log_features(X, *, shrinkage: float = 0.1):
    """Return log-Euclidean covariance coordinates; no fitted reference is used.

    Each epoch is demeaned independently. Its sample covariance S is replaced
    by (1-a) S + a trace(S)/channels I. The symmetric matrix logarithm is then
    vectorized using its upper triangle, with sqrt(2) on off-diagonal entries.
    Eight channels produce 36 features. No epoch is silently dropped.
    """

    np, eigh, threadpool_limits = _dependencies()
    shrinkage = _shrinkage(shrinkage)
    values = _epochs(np, X)
    n_channels = values.shape[1]
    upper = np.triu_indices(n_channels)
    weights = np.where(upper[0] == upper[1], 1.0, math.sqrt(2.0))
    features = np.empty((len(values), len(weights)), dtype=np.float64)
    with threadpool_limits(limits=1):
        for index, epoch in enumerate(values):
            centered = epoch - epoch.mean(axis=1, keepdims=True)
            # Scaling before multiplication avoids losing tiny physical EEG
            # units or overflowing large but finite input amplitudes.
            amplitude = float(np.max(np.abs(centered)))
            if not math.isfinite(amplitude) or amplitude <= 0:
                raise ValueError("each epoch must have positive finite temporal variance")
            centered = centered / amplitude
            covariance = centered @ centered.T / (epoch.shape[1] - 1)
            isotropic = float(np.trace(covariance) / n_channels)
            covariance *= 1.0 - shrinkage
            covariance.flat[:: n_channels + 1] += shrinkage * isotropic
            eigenvalues, eigenvectors = eigh(covariance, check_finite=True)
            if (eigenvalues <= 0).any():
                raise ValueError("regularized covariance is not positive definite")
            log_covariance = (eigenvectors * np.log(eigenvalues)) @ eigenvectors.T
            log_covariance.flat[:: n_channels + 1] += 2.0 * math.log(amplitude)
            features[index] = log_covariance[upper] * weights
    if not np.isfinite(features).all():
        raise ValueError("covariance logarithm produced non-finite features")
    return features


class ImaginedWordDecoder:
    """Log-covariance features, training-only scaling, then L2 logistic regression.

    `fit` accepts training labels only. Predictions require only EEG epochs and
    preserve the lexicographic order in `classes_`. Use external session-based
    splits and a separate scorer; this class does not choose an evaluation set.
    The fitted object retains coefficients and scaling arrays, not EEG epochs.
    """

    def __init__(self, *, shrinkage: float = 0.1, C: float = 1.0):
        self.shrinkage = _shrinkage(shrinkage)
        self.C = float(C)
        if not math.isfinite(self.C) or self.C <= 0:
            raise ValueError("C must be positive and finite")
        self._fitted = False

    def fit(self, X_train, y_train):
        """Fit once; convergence failure is an error, not a usable model."""

        if self._fitted:
            raise RuntimeError("decoder is already fitted; use a new instance for a new fit")
        np, _eigh, threadpool_limits = _dependencies()
        try:
            from sklearn.exceptions import ConvergenceWarning
            from sklearn.linear_model import LogisticRegression
        except ImportError as exc:
            raise RuntimeError("Imagined-word training requires scikit-learn.") from exc
        values = _epochs(np, X_train)
        labels = np.asarray(y_train)
        if labels.ndim != 1 or len(labels) != len(values):
            raise ValueError("y_train must have one label per training epoch")
        if labels.dtype.kind not in {"U", "S", "i", "u"}:
            raise ValueError("training labels must be strings or integers")
        labels = labels.astype(str)
        if (labels == "").any() or len(np.unique(labels)) < 2:
            raise ValueError("training requires at least two nonempty classes")
        started = time.perf_counter()
        with threadpool_limits(limits=1), warnings.catch_warnings():
            warnings.simplefilter("error", ConvergenceWarning)
            features = covariance_log_features(values, shrinkage=self.shrinkage)
            mean = features.mean(axis=0)
            scale = features.std(axis=0, ddof=0)
            scale = np.where(scale > 1e-12, scale, 1.0)
            # The default penalty is L2 in supported sklearn 1.4--1.x;
            # omitting `penalty` also avoids its deprecation in sklearn 1.9.
            classifier = LogisticRegression(
                C=self.C, solver="lbfgs", fit_intercept=True, class_weight=None,
                max_iter=1000, tol=1e-8, random_state=0,
            )
            classifier.fit((features - mean) / scale, labels)
        self.classes_ = classifier.classes_.astype(str, copy=True)
        self.mean_ = mean
        self.scale_ = scale
        self.coef_ = classifier.coef_.copy()
        self.intercept_ = classifier.intercept_.copy()
        self.input_shape_ = tuple(int(value) for value in values.shape[1:])
        self.training_summary_ = {
            "n_train": len(values), "n_features": features.shape[1],
            "n_classes": len(self.classes_), "num_threads": 1,
            "solver_iterations": [int(value) for value in classifier.n_iter_],
            "runtime_sec": time.perf_counter() - started,
            "model_array_bytes": sum(array.nbytes for array in (
                self.classes_, self.mean_, self.scale_, self.coef_, self.intercept_,
            )),
        }
        self._fitted = True
        return self

    def predict_proba(self, X):
        """Return [trials, classes] probabilities without labels or adaptation."""

        self._require_fitted()
        np, _eigh, threadpool_limits = _dependencies()
        from scipy.special import expit, softmax

        values = _epochs(np, X, shape=self.input_shape_)
        with threadpool_limits(limits=1):
            features = covariance_log_features(values, shrinkage=self.shrinkage)
            scores = ((features - self.mean_) / self.scale_) @ self.coef_.T + self.intercept_
            if len(self.classes_) == 2:
                positive = expit(scores[:, 0])
                return np.column_stack((1.0 - positive, positive))
            return softmax(scores, axis=1)

    def predict(self, X):
        """Return only the vocabulary item selected by the EEG classifier."""

        self._require_fitted()
        return self.classes_[self.predict_proba(X).argmax(axis=1)]

    def save(self, path: str | Path) -> None:
        """Create an inspectable NPZ with numeric arrays and JSON; never pickle."""

        self._require_fitted()
        np, _eigh, _limits = _dependencies()
        metadata = {
            "schema": SCHEMA, "shrinkage": self.shrinkage, "C": self.C,
            "input_shape": list(self.input_shape_), "training": self.training_summary_,
        }
        with Path(path).open("xb") as handle:
            np.savez_compressed(
                handle, metadata=np.asarray(json.dumps(metadata, allow_nan=False, sort_keys=True)),
                classes=self.classes_, mean=self.mean_, scale=self.scale_,
                coef=self.coef_, intercept=self.intercept_,
            )

    @classmethod
    def load(cls, path: str | Path):
        """Load coefficients directly; no sklearn object reconstruction occurs."""

        np, _eigh, _limits = _dependencies()
        with np.load(path, allow_pickle=False) as archive:
            if set(archive.files) != _ARRAY_KEYS:
                raise ValueError("unexpected imagined-word model arrays")
            metadata_array = archive["metadata"]
            if metadata_array.shape != () or metadata_array.dtype.kind != "U":
                raise ValueError("model metadata must be a JSON string scalar")
            metadata = json.loads(str(metadata_array.item()))
            if not isinstance(metadata, dict) or set(metadata) != {
                "schema", "shrinkage", "C", "input_shape", "training",
            } or metadata["schema"] != SCHEMA:
                raise ValueError("invalid imagined-word model schema")
            model = cls(shrinkage=metadata["shrinkage"], C=metadata["C"])
            shape = metadata["input_shape"]
            if (not isinstance(shape, list) or len(shape) != 2
                    or any(type(value) is not int or value < 1 for value in shape)
                    or shape[1] < 2):
                raise ValueError("invalid model input geometry")
            model.input_shape_ = tuple(shape)
            classes = archive["classes"]
            if (classes.ndim != 1 or classes.dtype.kind != "U" or len(classes) < 2
                    or (classes == "").any()
                    or not np.array_equal(classes, np.unique(classes))):
                raise ValueError("invalid model classes")
            model.classes_ = classes.copy()
            n_features = shape[0] * (shape[0] + 1) // 2
            n_rows = 1 if len(classes) == 2 else len(classes)
            expected_shapes = {
                "mean": (n_features,), "scale": (n_features,),
                "coef": (n_rows, n_features), "intercept": (n_rows,),
            }
            for name, expected in expected_shapes.items():
                array = archive[name]
                if (array.dtype.kind != "f" or array.shape != expected
                        or not np.isfinite(array).all()):
                    raise ValueError(f"invalid model {name}")
                setattr(model, name + "_", array.astype(np.float64, copy=True))
            if (model.scale_ <= 0).any():
                raise ValueError("model scale must be positive")
            if not isinstance(metadata["training"], dict):
                raise ValueError("invalid model training summary")
            model.training_summary_ = metadata["training"]
        model._fitted = True
        return model

    def _require_fitted(self):
        if not self._fitted:
            raise RuntimeError("decoder must be fitted before prediction or serialization")
