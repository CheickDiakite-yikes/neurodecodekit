"""Bounded SPEECH-REPRO-1 EEGNet reproduction, with no online-target input.

Architecture and source ensemble follow arayabrain/uhd-gmail-public at
0dca00584c528b288392684dcec0d496b6aa4951 (CC0-1.0; Sato et al., Araya).
Pinned source license: https://github.com/arayabrain/uhd-gmail-public/blob/
0dca00584c528b288392684dcec0d496b6aa4951/LICENSE
The caller supplies already filtered
EEG: trial-wise notch/CAR/bandpass/adaptive-filter normalization belongs to
preprocessing. This module neither reads recordings nor infers their labels.

Calibration inputs are [trial, 128, 1626] at 256 Hz, with 25 leading samples
before the five 320-sample repetitions. Jitter stays inside each original
trial, affects training only, and leaves the final repetition unshifted.
Online inputs may use that same representation or deterministic [trial,128,320]
repetition averages. All checkpoints and predictions must remain local.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from collections.abc import Mapping
from pathlib import Path


AUTHOR_COMMIT = "0dca00584c528b288392684dcec0d496b6aa4951"
SEED = 20260906
N_FOLDS = 10
N_EPOCHS = 100
N_ENSEMBLE = 4
BATCH_SIZE = 16
N_PARAMETERS = 12293
TRIAL_SAMPLES = 1626
WINDOW_SAMPLES = 320
LEADING_SAMPLES = 25


def _numpy():
    try:
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Speech reference requires neurodecodekit[ml].") from exc
    return np


def _torch():
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("Speech reference requires neurodecodekit[ml].") from exc
    return torch


def build_reference_eegnet():
    """Construct the author's 128-channel/320-sample, 12,293-parameter EEGNet."""
    torch = _torch()
    nn = torch.nn

    class EEGNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Sequential(
                nn.Conv2d(1, 16, (1, 30), padding="same", bias=False),
                nn.BatchNorm2d(16),
            )
            self.conv2 = nn.Sequential(
                nn.Conv2d(16, 32, (128, 1), groups=16, bias=False),
                nn.BatchNorm2d(32),
                nn.ELU(),
                nn.AvgPool2d((1, 2)),
                nn.Dropout(0.50),
            )
            self.conv3 = nn.Sequential(
                nn.Conv2d(32, 32, (1, 4), padding="same", groups=32, bias=False),
                nn.Conv2d(32, 32, (1, 1), bias=False),
                nn.BatchNorm2d(32),
                nn.ELU(),
                nn.AvgPool2d((1, 4)),
                nn.Dropout(0.75),
            )
            # Preserve the source's constructor probe, including its initial
            # BatchNorm running-state update and dropout RNG consumption.
            with torch.no_grad():
                probe = self.conv3(self.conv2(self.conv1(torch.zeros(1, 1, 128, 320))))
            self.n_dim = int(probe.numel())
            self.classifier = nn.Linear(self.n_dim, 5, bias=True)

        def forward(self, values):
            values = self.conv3(self.conv2(self.conv1(values)))
            return self.classifier(values.reshape(-1, self.n_dim))

    model = EEGNet()
    if sum(p.numel() for p in model.parameters()) != N_PARAMETERS:
        raise RuntimeError("Reference EEGNet parameter identity differs")
    return model.to(memory_format=torch.channels_last)


def _windows(values, *, name, calibration=False):
    np = _numpy()
    array = np.asarray(values, dtype=np.float32)
    allowed = (TRIAL_SAMPLES,) if calibration else (TRIAL_SAMPLES, WINDOW_SAMPLES)
    if (
        array.ndim != 3
        or array.shape[0] == 0
        or array.shape[1] != 128
        or array.shape[2] not in allowed
        or not np.isfinite(array).all()
    ):
        raise ValueError(f"{name} must be finite nonempty [trials,128,{allowed}] EEG")
    return array


def average_repetitions(windows, *, rng=None):
    """Average five repetitions; an explicit RNG enables training-only jitter.

    The source's float randint bounds +/-25.6 truncate to integer bounds
    [-25,25), i.e. offsets -25 through +24 samples. Explicit integer bounds
    avoid NumPy-version-dependent coercion. The fifth offset is always zero.
    """
    np = _numpy()
    values = _windows(windows, name="repetition windows")
    if values.shape[2] == WINDOW_SAMPLES:
        if rng is not None:
            raise ValueError("Training jitter requires complete 1626-sample trials")
        return values
    result = np.empty((len(values), 128, WINDOW_SAMPLES), dtype=np.float32)
    for trial, samples in enumerate(values):
        offsets = [0] * 5 if rng is None else [*rng.randint(-25, 25, size=4), 0]
        segments = [
            samples[:, LEADING_SAMPLES + 320 * repeat + int(offset) :
                    LEADING_SAMPLES + 320 * (repeat + 1) + int(offset)]
            for repeat, offset in enumerate(offsets)
        ]
        result[trial] = np.stack(segments, axis=0).mean(axis=0)
    return result


def zscore_mean_probabilities(fold_logits):
    """Source per-trial logit z-score/mean, followed by an explicit softmax.

    Source evaluation takes argmax of the mean standardized logits. Softmax
    preserves that exact decision but is not a source-calibrated probability.
    Constant logits cannot be standardized and are rejected, never hidden.
    """
    np = _numpy()
    logits = np.asarray(fold_logits, dtype=np.float64)
    if logits.ndim != 3 or logits.shape[0] != N_ENSEMBLE or logits.shape[-1] != 5:
        raise ValueError("Expected [4 folds, trials, 5 classes] logits")
    if not np.isfinite(logits).all() or logits.shape[1] == 0:
        raise ValueError("Ensemble logits must be finite and nonempty")
    deviation = logits.std(axis=-1, keepdims=True, ddof=0)
    if np.any(deviation <= 0):
        raise ValueError("Source z-score ensemble is undefined for constant logits")
    averaged = ((logits - logits.mean(axis=-1, keepdims=True)) / deviation).mean(axis=0)
    exponent = np.exp(averaged - averaged.max(axis=1, keepdims=True))
    return exponent / exponent.sum(axis=1, keepdims=True)


def calibration_folds(calibration_labels):
    """Source stratification: no shuffle; every original trial enters one fold."""
    np = _numpy()
    try:
        from sklearn.model_selection import StratifiedKFold
    except ImportError as exc:
        raise RuntimeError("Speech reference requires neurodecodekit[ml].") from exc
    labels = np.asarray(calibration_labels)
    if labels.ndim != 1 or labels.dtype.kind not in "iu":
        raise ValueError("Calibration labels must be one-dimensional integer classes 0..4")
    if set(labels.tolist()) != set(range(5)):
        raise ValueError("Calibration must contain exactly five classes 0..4")
    if np.min(np.bincount(labels, minlength=5)) < N_FOLDS:
        raise ValueError("Ten-fold calibration needs at least ten original trials per class")
    splitter = StratifiedKFold(n_splits=N_FOLDS, shuffle=False)
    return labels.astype(np.int64), list(splitter.split(np.zeros(len(labels)), labels))


def _check_deadline(deadline):
    if deadline is not None and time.monotonic() >= deadline:
        raise TimeoutError("SPEECH-REPRO-1 reference execution deadline exceeded")


def _predict_logits(model, values, deadline):
    np, torch = _numpy(), _torch()
    model.eval()
    batches = []
    with torch.inference_mode():
        for start in range(0, len(values), BATCH_SIZE):
            _check_deadline(deadline)
            tensor = torch.from_numpy(values[start : start + BATCH_SIZE, None]).contiguous(
                memory_format=torch.channels_last
            )
            batches.append(model(tensor).cpu().numpy().copy())
    result = np.concatenate(batches)
    if not np.isfinite(result).all():
        raise ValueError("Nonfinite EEGNet logits")
    return result


def _state_hash(state):
    digest = hashlib.sha256()
    for name, tensor in sorted(state.items()):
        array = tensor.detach().cpu().numpy()
        digest.update(name.encode("utf-8"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(str(array.shape).encode("ascii"))
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _fit_fold(calibration, labels, deterministic, train, validation, *, fold,
              deadline, progress, epochs=N_EPOCHS):
    np, torch = _numpy(), _torch()
    torch.manual_seed(SEED + fold)
    rng = np.random.RandomState(SEED + fold)
    model = build_reference_eegnet()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, eps=1e-8, weight_decay=0.01)
    criterion = torch.nn.CrossEntropyLoss()
    targets = torch.from_numpy(labels)
    best_state, best_loss, best_accuracy, best_epoch = None, float("inf"), None, None
    started = time.monotonic()
    for epoch in range(epochs):
        _check_deadline(deadline)
        model.train()
        order = train[torch.randperm(len(train)).numpy()]
        for start in range(0, len(order), BATCH_SIZE):
            _check_deadline(deadline)
            indices = order[start : start + BATCH_SIZE]
            values = average_repetitions(calibration[indices], rng=rng)
            optimizer.zero_grad(set_to_none=True)
            tensor = torch.from_numpy(values[:, None]).contiguous(memory_format=torch.channels_last)
            logits = model(tensor)
            loss = criterion(logits, targets[indices])
            if not torch.isfinite(loss):
                raise ValueError("Nonfinite reference training loss")
            loss.backward()
            optimizer.step()
        logits = _predict_logits(model, deterministic[validation], deadline)
        # Correct sample-weighted validation CE. The author trainer overwrites
        # each validation batch's loss and adds a stale final training loss.
        validation_loss = float(criterion(torch.from_numpy(logits), targets[validation]))
        validation_accuracy = float(np.mean(logits.argmax(axis=1) == labels[validation]))
        if validation_loss < best_loss:
            best_loss, best_accuracy, best_epoch = validation_loss, validation_accuracy, epoch + 1
            best_state = {name: value.detach().cpu().clone()
                          for name, value in model.state_dict().items()}
        if progress is not None and ((epoch + 1) % 10 == 0 or epoch + 1 == epochs):
            progress({"event": "reference_epoch", "fold": fold, "epoch": epoch + 1,
                      "best_validation_loss": best_loss,
                      "elapsed_seconds": time.monotonic() - started})
    _check_deadline(deadline)
    record = {
        "fold": fold, "epochs": epochs, "best_epoch": best_epoch,
        "best_validation_loss": best_loss, "checkpoint_validation_accuracy": best_accuracy,
        "training_trials": len(train), "validation_trials": len(validation),
        "validation_indices": validation.tolist(), "state_sha256": _state_hash(best_state),
        "elapsed_seconds": time.monotonic() - started,
    }
    return best_state, record


def train_predict(cal_windows, cal_labels, online_windows, *, deadline=None,
                  progress=None, checkpoint_dir=None):
    """Run all ten frozen folds and predict online data without online targets.

    ``online_windows`` is an array or a mapping from recording IDs to arrays;
    the returned probabilities preserve that structure. ``deadline`` is an
    absolute time.monotonic() deadline from the approved six-hour executor.
    A separate 15-minute cap applies to every fit. A progress callback receives
    calibration-only diagnostics. No reduced-fold/epoch public option exists.
    """
    # Even direct callers cannot accidentally remove the experiment's total
    # runtime ceiling. The executor normally supplies its earlier deadline.
    own_deadline = time.monotonic() + 6 * 60 * 60
    deadline = own_deadline if deadline is None else min(own_deadline, deadline)
    np, torch = _numpy(), _torch()
    _check_deadline(deadline)
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.backends.mkldnn.enabled = True
    torch.use_deterministic_algorithms(True)
    calibration = _windows(cal_windows, name="calibration", calibration=True)
    labels, folds = calibration_folds(cal_labels)
    if len(calibration) != len(labels):
        raise ValueError("Calibration labels must align one-to-one with original trials")
    mapped = isinstance(online_windows, Mapping)
    raw_online = online_windows if mapped else {"online": online_windows}
    if not raw_online:
        raise ValueError("At least one online recording is required")
    online = {name: average_repetitions(values) for name, values in raw_online.items()}
    deterministic = average_repetitions(calibration)
    checkpoint_root = None if checkpoint_dir is None else Path(checkpoint_dir)
    if checkpoint_root is not None:
        checkpoint_root.mkdir(parents=True, exist_ok=True)
        if any((checkpoint_root / f"fold-{fold:02d}.pt").exists() for fold in range(N_FOLDS)):
            raise FileExistsError("Reference checkpoints already exist; refusing overwrite")
    started, states, records = time.monotonic(), [], []
    for fold, (train, validation) in enumerate(folds):
        _check_deadline(deadline)
        if progress is not None:
            progress({"event": "reference_fold_start", "fold": fold})
        fold_deadline = time.monotonic() + 15 * 60
        if deadline is not None:
            fold_deadline = min(fold_deadline, deadline)
        state, record = _fit_fold(
            calibration, labels, deterministic, train, validation,
            fold=fold, deadline=fold_deadline, progress=progress,
        )
        if checkpoint_root is not None:
            with (checkpoint_root / f"fold-{fold:02d}.pt").open("xb") as handle:
                torch.save(state, handle)
        states.append(state)
        records.append(record)
        if progress is not None:
            progress({"event": "reference_fold_complete", **record})
    # The source ranks checkpoint accuracy, not minimum loss. Ties use the
    # original fold index, an explicit deterministic choice before scoring.
    selected = sorted(range(N_FOLDS),
                      key=lambda fold: (-records[fold]["checkpoint_validation_accuracy"], fold))[
                          :N_ENSEMBLE]
    predictions = {name: [] for name in online}
    for fold in selected:
        model = build_reference_eegnet()
        model.load_state_dict(states[fold], strict=True)
        for name, values in online.items():
            predictions[name].append(_predict_logits(model, values, deadline))
    probabilities = {name: zscore_mean_probabilities(np.stack(logits))
                     for name, logits in predictions.items()}
    metadata = {
        "author_commit": AUTHOR_COMMIT, "architecture": "EEGNet-128x320",
        "parameters": N_PARAMETERS, "seed": SEED, "folds": records,
        "selected_folds": selected, "epochs_per_fold": N_EPOCHS,
        "batch_size": BATCH_SIZE, "optimizer": "AdamW", "learning_rate": 1e-4,
        "weight_decay": 0.01, "split": "StratifiedKFold(10, shuffle=False)",
        "fold_selection": "highest accuracy at lowest validation-loss checkpoint; fold-index ties",
        "training_jitter_samples": [-25, 24], "final_repetition_jitter_samples": 0,
        "validation_and_online_jitter": False, "additional_input_normalization": False,
        "ensemble": "per-model per-trial five-logit population z-score, four-fold mean, softmax",
        "deviations": [
            "100 manuscript epochs instead of source YAML 1000",
            "seed 20260906 plus fold index; CPU deterministic execution",
            "deterministic calibration validation instead of source dataset jitter",
            "correct sample-weighted validation loss instead of source stale-training-loss bug",
            "stable fold-index tie-break for calibration accuracy ranking",
            "softmax of source ensemble scores supplies uncalibrated probabilities",
        ],
        "torch_version": str(torch.__version__), "threads": 1,
        "memory_format": "channels_last", "mkldnn": True,
        "memory_format_eval_equivalence_tolerance": {"atol": 1e-6, "rtol": 1e-5},
        "source_license": "CC0-1.0", "maximum_total_seconds": 6 * 60 * 60,
        "elapsed_seconds": time.monotonic() - started,
        "online_recording_trials": {str(name): len(values) for name, values in online.items()},
        "online_labels_received": False,
    }
    return (probabilities if mapped else probabilities["online"]), metadata


def _validate_checkpoint_metadata(metadata, cal_labels):
    """Check existing records without recomputing any calibration score."""
    torch = _torch()
    fixed = {
        "author_commit": AUTHOR_COMMIT, "architecture": "EEGNet-128x320",
        "parameters": N_PARAMETERS, "seed": SEED, "epochs_per_fold": N_EPOCHS,
        "batch_size": BATCH_SIZE, "optimizer": "AdamW", "learning_rate": 1e-4,
        "weight_decay": 0.01, "split": "StratifiedKFold(10, shuffle=False)",
        "fold_selection": "highest accuracy at lowest validation-loss checkpoint; fold-index ties",
        "training_jitter_samples": [-25, 24], "final_repetition_jitter_samples": 0,
        "validation_and_online_jitter": False, "additional_input_normalization": False,
        "ensemble": "per-model per-trial five-logit population z-score, four-fold mean, softmax",
        "torch_version": str(torch.__version__), "threads": 1,
        "memory_format": "channels_last", "mkldnn": True,
        "memory_format_eval_equivalence_tolerance": {"atol": 1e-6, "rtol": 1e-5},
        "source_license": "CC0-1.0", "maximum_total_seconds": 6 * 60 * 60,
        "online_labels_received": False,
    }
    if not isinstance(metadata, dict):
        raise ValueError("Original reference metadata must be a dictionary")
    for key, expected in fixed.items():
        actual = metadata.get(key)
        if type(actual) is not type(expected) or actual != expected:
            raise ValueError(f"Original reference metadata differs: {key}")
    _, splits = calibration_folds(cal_labels)
    records = metadata.get("folds")
    if not isinstance(records, list) or len(records) != N_FOLDS:
        raise ValueError("Original reference must contain exactly ten fold records")
    for index, (record, (train, validation)) in enumerate(zip(records, splits)):
        if not isinstance(record, dict):
            raise ValueError("Original fold record must be a dictionary")
        integer_fields = {"fold": index, "epochs": N_EPOCHS,
                          "training_trials": len(train), "validation_trials": len(validation)}
        if any(type(record.get(key)) is not int or record[key] != value
               for key, value in integer_fields.items()):
            raise ValueError("Original fold identity, schedule, or calibration counts differ")
        if record.get("validation_indices") != validation.tolist():
            raise ValueError("Original calibration split indices differ")
        best_epoch = record.get("best_epoch")
        if type(best_epoch) is not int or not 1 <= best_epoch <= N_EPOCHS:
            raise ValueError("Original best epoch is invalid")
        accuracy, loss = record.get("checkpoint_validation_accuracy"), record.get("best_validation_loss")
        if (type(accuracy) not in (int, float) or not math.isfinite(accuracy)
                or not 0 <= accuracy <= 1 or type(loss) not in (int, float)
                or not math.isfinite(loss) or loss < 0):
            raise ValueError("Original calibration checkpoint metrics are invalid")
        digest = record.get("state_sha256")
        if (not isinstance(digest, str) or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)):
            raise ValueError("Original checkpoint hash is invalid")
    selected = metadata.get("selected_folds")
    ranked = sorted(range(N_FOLDS),
                    key=lambda fold: (-records[fold]["checkpoint_validation_accuracy"], fold))[
                        :N_ENSEMBLE]
    if (not isinstance(selected, list) or any(type(index) is not int for index in selected)
            or selected != ranked):
        raise ValueError("Original selected folds do not match the frozen calibration ranking")
    return records, selected


def _validate_checkpoint_state(state, record):
    """Validate tensors directly, before constructing a model or doing inference."""
    torch = _torch()
    shapes = {
        "conv1.0.weight": (16, 1, 1, 30), "conv2.0.weight": (32, 1, 128, 1),
        "conv3.0.weight": (32, 1, 1, 4), "conv3.1.weight": (32, 32, 1, 1),
        "classifier.weight": (5, 1280), "classifier.bias": (5,),
    }
    for prefix, width in (("conv1.1", 16), ("conv2.1", 32), ("conv3.2", 32)):
        shapes.update({f"{prefix}.{name}": (width,)
                       for name in ("weight", "bias", "running_mean", "running_var")})
        shapes[f"{prefix}.num_batches_tracked"] = ()
    if not isinstance(state, dict) or set(state) != set(shapes):
        raise ValueError("Checkpoint tensor names differ from the reference architecture")
    batches = 1 + record["best_epoch"] * math.ceil(record["training_trials"] / BATCH_SIZE)
    for name, shape in shapes.items():
        value = state[name]
        counter = name.endswith("num_batches_tracked")
        dtype = torch.int64 if counter else torch.float32
        if (not isinstance(value, torch.Tensor) or tuple(value.shape) != shape
                or value.dtype != dtype or value.device.type != "cpu"
                or not bool(torch.isfinite(value).all())):
            raise ValueError("Checkpoint contains invalid tensor shape, dtype, device, or values")
        if counter and int(value) != batches:
            raise ValueError("Checkpoint BatchNorm history differs from its recorded best epoch")
        if name.endswith("running_var") and bool((value < 0).any()):
            raise ValueError("Checkpoint BatchNorm variance is negative")
    if _state_hash(state) != record["state_sha256"]:
        raise ValueError("Checkpoint canonical state hash does not match the original record")


def predict_from_checkpoints(online_windows, model_metadata, checkpoint_dir, *,
                             cal_labels, deadline, progress=None):
    """Reuse an existing ten-fold fit without fitting or validating on signals.

    Calibration labels recreate the original split only. No calibration
    waveform or online label is accepted. All ten saved states are checked
    before the originally selected four run unchanged inference. The caller
    retains ``model_metadata`` unchanged and stores the returned reuse receipt
    separately. Its checkpoint/source authorization and prediction freeze
    remain the caller's responsibility.
    """
    if type(deadline) not in (int, float) or not math.isfinite(deadline):
        raise ValueError("Recovery requires a finite absolute monotonic deadline")
    deadline = min(float(deadline), time.monotonic() + 2 * 60 * 60)
    _check_deadline(deadline)
    np, torch = _numpy(), _torch()
    records, selected = _validate_checkpoint_metadata(model_metadata, cal_labels)
    torch.set_num_threads(1)
    if torch.get_num_interop_threads() != 1:
        torch.set_num_interop_threads(1)
    torch.backends.mkldnn.enabled = True
    torch.use_deterministic_algorithms(True)
    mapped = isinstance(online_windows, Mapping)
    raw_online = online_windows if mapped else {"online": online_windows}
    if not raw_online or any(not isinstance(name, str) or not name for name in raw_online):
        raise ValueError("Online recordings need nonempty string identifiers")
    online = {name: average_repetitions(values) for name, values in raw_online.items()}
    counts = {name: len(values) for name, values in online.items()}
    if counts != model_metadata.get("online_recording_trials"):
        raise ValueError("Online recording identities or trial counts differ from the original")
    checkpoint_root = Path(checkpoint_dir)
    expected = {f"fold-{index:02d}.pt" for index in range(N_FOLDS)}
    if {path.name for path in checkpoint_root.glob("*.pt")} != expected:
        raise ValueError("Exactly the original ten checkpoint files are required")
    started, states, total_bytes = time.monotonic(), {}, 0
    for record in records:
        _check_deadline(deadline)
        path = checkpoint_root / f"fold-{record['fold']:02d}.pt"
        if path.is_symlink() or not path.is_file():
            raise ValueError("Checkpoint must be an ordinary existing file")
        state = torch.load(path, map_location="cpu", weights_only=True)
        _validate_checkpoint_state(state, record)
        total_bytes += path.stat().st_size
        if record["fold"] in selected:
            states[record["fold"]] = state
    if progress is not None:
        progress({"event": "reference_checkpoints_verified", "verified_checkpoints": N_FOLDS})
    predictions = {name: [] for name in online}
    for fold in selected:
        _check_deadline(deadline)
        model = build_reference_eegnet()
        model.load_state_dict(states[fold], strict=True)
        for name, values in online.items():
            predictions[name].append(_predict_logits(model, values, deadline))
        if progress is not None:
            progress({"event": "reference_checkpoint_prediction_complete", "fold": fold})
    probabilities = {name: zscore_mean_probabilities(np.stack(logits))
                     for name, logits in predictions.items()}
    _check_deadline(deadline)
    receipt = {
        "reused_fits": N_FOLDS, "new_fit_count": 0, "verified_checkpoint_count": N_FOLDS,
        "selected_folds": list(selected), "serialized_checkpoint_bytes": total_bytes,
        "original_metadata_sha256": hashlib.sha256(json.dumps(
            model_metadata, sort_keys=True, separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")).hexdigest(),
        "calibration_labels_used_for_split_validation_only": True,
        "calibration_validation_scored": False, "online_labels_received": False,
        "original_selection_preserved": True, "elapsed_seconds": time.monotonic() - started,
    }
    return (probabilities if mapped else probabilities["online"]), receipt
