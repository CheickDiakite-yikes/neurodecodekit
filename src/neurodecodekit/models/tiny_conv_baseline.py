"""Optional tiny ConvNet baseline for cache-window smoke tests.

This module intentionally imports PyTorch only inside the training path. The
base package should stay light; install the optional ML extras to run this
baseline.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable

from neurodecodekit.models.template_baseline import stratified_holdout_indices


ML_INSTALL_HINT = "pip install -e '.[ml]'"


@dataclass(frozen=True)
class TinyConvBaselineResult:
    """Predictions and metadata for the optional tiny ConvNet baseline."""

    predictions: list[str]
    targets: list[str]
    strategy: str
    model_name: str
    split_mode: str
    seed: int
    train_fraction: float | None
    n_train_rows: int
    n_eval_rows: int
    n_classes: int
    train_label_counts: dict[str, int]
    eval_label_counts: dict[str, int]
    missing_eval_labels_in_train: list[str]
    feature_shape: tuple[int, int]
    train_indices: list[int] | None
    eval_indices: list[int] | None
    epochs: int
    batch_size: int
    learning_rate: float
    hidden_channels: int
    device: str
    num_threads: int
    loss_history: list[float]
    train_accuracy: float
    eval_accuracy: float
    warnings: list[str]

    def metadata(self) -> dict[str, object]:
        payload = asdict(self)
        payload.pop("predictions")
        payload.pop("targets")
        payload["kind"] = "tiny-conv-window"
        payload["description"] = (
            "Optional PyTorch tiny ConvNet baseline over neural-window arrays; "
            "CPU-safe smoke baseline, not a production decoder."
        )
        payload["uses_neural_windows"] = True
        payload["uses_deep_learning"] = True
        payload["optional_dependency_extra"] = "ml"
        return payload


def run_tiny_conv_baseline_from_single_cache(
    *,
    windows,
    labels: Iterable[str],
    train_fraction: float = 0.5,
    seed: int = 7,
    epochs: int = 20,
    batch_size: int = 16,
    learning_rate: float = 0.01,
    hidden_channels: int = 8,
    device: str = "cpu",
    num_threads: int = 1,
) -> TinyConvBaselineResult:
    """Split one cache into train/eval rows and run the tiny ConvNet baseline."""

    np, _torch = _require_ml_dependencies()
    x = np.asarray(windows, dtype="float32")
    y = _labels_array(labels)
    _validate_windows_and_labels(x, y)
    train_idx, eval_idx, split_warnings = stratified_holdout_indices(
        y.tolist(),
        train_fraction=train_fraction,
        seed=seed,
    )
    return run_tiny_conv_baseline(
        train_windows=x[train_idx],
        train_labels=y[train_idx].tolist(),
        eval_windows=x[eval_idx],
        eval_labels=y[eval_idx].tolist(),
        split_mode="single-cache-stratified-holdout",
        seed=seed,
        train_fraction=train_fraction,
        train_indices=train_idx,
        eval_indices=eval_idx,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=device,
        num_threads=num_threads,
        extra_warnings=split_warnings,
    )


def run_tiny_conv_baseline(
    *,
    train_windows,
    train_labels: Iterable[str],
    eval_windows,
    eval_labels: Iterable[str],
    split_mode: str = "separate-cache",
    seed: int = 7,
    train_fraction: float | None = None,
    train_indices: list[int] | None = None,
    eval_indices: list[int] | None = None,
    epochs: int = 20,
    batch_size: int = 16,
    learning_rate: float = 0.01,
    hidden_channels: int = 8,
    device: str = "cpu",
    num_threads: int = 1,
    extra_warnings: Iterable[str] | None = None,
) -> TinyConvBaselineResult:
    """Fit a tiny ConvNet on train windows and predict eval windows."""

    _validate_training_params(
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        num_threads=num_threads,
    )
    np, torch = _require_ml_dependencies()
    train_x = np.asarray(train_windows, dtype="float32")
    eval_x = np.asarray(eval_windows, dtype="float32")
    train_y = _labels_array(train_labels)
    eval_y = _labels_array(eval_labels)
    _validate_windows_and_labels(train_x, train_y, role="train")
    _validate_windows_and_labels(eval_x, eval_y, role="eval")
    if train_x.shape[1:] != eval_x.shape[1:]:
        raise ValueError(
            "train and eval windows must have matching [channels, timepoints] shape: "
            f"{train_x.shape[1:]} vs {eval_x.shape[1:]}"
        )

    torch.manual_seed(seed)
    torch.set_num_threads(num_threads)
    np.random.seed(seed)
    resolved_device = _resolve_device(torch, device)
    label_vocab, train_encoded, _eval_encoded, missing = encode_labels(
        train_y.tolist(),
        eval_y.tolist(),
    )

    train_x, eval_x = _standardize_from_train(train_x, eval_x)
    x_train = torch.as_tensor(train_x[:, None, :, :], dtype=torch.float32, device=resolved_device)
    x_eval = torch.as_tensor(eval_x[:, None, :, :], dtype=torch.float32, device=resolved_device)
    y_train = torch.as_tensor(train_encoded, dtype=torch.long, device=resolved_device)

    model = _build_tiny_conv_net(
        torch,
        n_channels=int(train_x.shape[1]),
        n_timepoints=int(train_x.shape[2]),
        n_classes=len(label_vocab),
        hidden_channels=hidden_channels,
    ).to(resolved_device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    loss_fn = torch.nn.CrossEntropyLoss()
    generator = torch.Generator(device=str(resolved_device))
    generator.manual_seed(seed)
    loss_history: list[float] = []

    model.train()
    n_train = int(x_train.shape[0])
    for _epoch in range(epochs):
        order = torch.randperm(n_train, generator=generator, device=resolved_device)
        epoch_loss = 0.0
        seen = 0
        for start in range(0, n_train, batch_size):
            batch_idx = order[start : start + batch_size]
            optimizer.zero_grad(set_to_none=True)
            logits = model(x_train[batch_idx])
            loss = loss_fn(logits, y_train[batch_idx])
            loss.backward()
            optimizer.step()
            batch_rows = int(batch_idx.numel())
            epoch_loss += float(loss.detach().cpu()) * batch_rows
            seen += batch_rows
        loss_history.append(epoch_loss / max(seen, 1))

    model.eval()
    with torch.no_grad():
        train_pred_idx = model(x_train).argmax(dim=1)
        eval_pred_idx = model(x_eval).argmax(dim=1)
    predictions = [label_vocab[int(index)] for index in eval_pred_idx.cpu().tolist()]
    targets = [str(value) for value in eval_y.tolist()]
    train_predictions = [label_vocab[int(index)] for index in train_pred_idx.cpu().tolist()]
    train_accuracy = _accuracy(train_predictions, train_y.tolist())
    eval_accuracy = _accuracy(predictions, targets)

    warnings = ["tiny_conv_baseline_uses_neural_windows", "tiny_conv_baseline_optional_ml"]
    if resolved_device.type == "cpu":
        warnings.append("tiny_conv_cpu_smoke_mode")
    if split_mode == "single-cache-stratified-holdout":
        warnings.append("tiny_conv_single_cache_holdout_split")
    warnings.extend(extra_warnings or [])
    if missing:
        warnings.append("tiny_conv_eval_labels_missing_from_train")

    return TinyConvBaselineResult(
        predictions=predictions,
        targets=targets,
        strategy="tiny-conv",
        model_name="TinyConvNet",
        split_mode=split_mode,
        seed=seed,
        train_fraction=train_fraction,
        n_train_rows=int(train_x.shape[0]),
        n_eval_rows=int(eval_x.shape[0]),
        n_classes=len(label_vocab),
        train_label_counts=_count_labels(train_y.tolist()),
        eval_label_counts=_count_labels(targets),
        missing_eval_labels_in_train=missing,
        feature_shape=(int(train_x.shape[1]), int(train_x.shape[2])),
        train_indices=list(train_indices) if train_indices is not None else None,
        eval_indices=list(eval_indices) if eval_indices is not None else None,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate,
        hidden_channels=hidden_channels,
        device=str(resolved_device),
        num_threads=num_threads,
        loss_history=[float(value) for value in loss_history],
        train_accuracy=float(train_accuracy),
        eval_accuracy=float(eval_accuracy),
        warnings=warnings,
    )


def encode_labels(train_labels: Iterable[str], eval_labels: Iterable[str]) -> tuple[list[str], list[int], list[int], list[str]]:
    """Encode labels from train vocabulary, mapping missing eval labels to index 0."""

    train_rows = [str(value) for value in train_labels]
    eval_rows = [str(value) for value in eval_labels]
    if not train_rows:
        raise ValueError("tiny conv baseline requires at least one train label.")
    label_vocab = sorted(set(train_rows))
    label_to_index = {label: index for index, label in enumerate(label_vocab)}
    missing = sorted(set(eval_rows) - set(label_to_index))
    train_encoded = [label_to_index[label] for label in train_rows]
    eval_encoded = [label_to_index.get(label, 0) for label in eval_rows]
    return label_vocab, train_encoded, eval_encoded, missing


def _standardize_from_train(train_x, eval_x):
    mean = train_x.mean(dtype="float64")
    std = train_x.std(dtype="float64")
    if not std or std < 1e-8:
        std = 1.0
    return ((train_x - mean) / std).astype("float32"), ((eval_x - mean) / std).astype("float32")


def _accuracy(predicted: Iterable[object], targets: Iterable[object]) -> float:
    pred_rows = list(predicted)
    target_rows = list(targets)
    if not target_rows:
        return 0.0
    return sum(1 for pred, target in zip(pred_rows, target_rows) if str(pred) == str(target)) / len(target_rows)


def _labels_array(labels: Iterable[str]):
    np, _torch = _require_ml_dependencies()
    return np.asarray([str(value) for value in labels])


def _validate_windows_and_labels(windows, labels, *, role: str = "cache") -> None:
    if windows.ndim != 3:
        raise ValueError(f"Expected {role} windows [samples, channels, times], got {windows.shape}")
    if len(windows) != len(labels):
        raise ValueError(f"{role} windows and labels must have the same length")
    if len(labels) == 0:
        raise ValueError(f"tiny conv baseline requires at least one {role} row.")


def _validate_training_params(
    *,
    epochs: int,
    batch_size: int,
    learning_rate: float,
    hidden_channels: int,
    num_threads: int,
) -> None:
    if epochs < 1:
        raise ValueError("epochs must be >= 1.")
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1.")
    if learning_rate <= 0:
        raise ValueError("learning_rate must be > 0.")
    if hidden_channels < 1:
        raise ValueError("hidden_channels must be >= 1.")
    if num_threads < 1:
        raise ValueError("num_threads must be >= 1.")


def _count_labels(labels: Iterable[str]) -> dict[str, int]:
    counts = Counter(str(value) for value in labels)
    return {label: int(counts[label]) for label in sorted(counts)}


def _resolve_device(torch, requested: str):
    requested = str(requested or "cpu").lower()
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available; use --device cpu.")
        return torch.device("cuda")
    raise ValueError("device must be one of: cpu, cuda.")


def _require_ml_dependencies():
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - depends on local optional deps
        raise RuntimeError(
            f"Tiny Conv baseline requires optional ML dependencies: `{ML_INSTALL_HINT}`."
        ) from exc
    return np, torch


def _build_tiny_conv_net(
    torch,
    *,
    n_channels: int,
    n_timepoints: int,
    n_classes: int,
    hidden_channels: int,
):
    class TinyConvNet(torch.nn.Module):
        """Small temporal-then-spatial ConvNet for window classification."""

        def __init__(self) -> None:
            super().__init__()
            temporal_kernel = max(1, min(5, n_timepoints))
            spatial_kernel = max(1, min(3, n_channels))
            self.net = torch.nn.Sequential(
                torch.nn.Conv2d(
                    1,
                    hidden_channels,
                    kernel_size=(1, temporal_kernel),
                    padding=(0, temporal_kernel // 2),
                ),
                torch.nn.ReLU(),
                torch.nn.Conv2d(
                    hidden_channels,
                    hidden_channels,
                    kernel_size=(spatial_kernel, 1),
                    padding=(spatial_kernel // 2, 0),
                ),
                torch.nn.ReLU(),
                torch.nn.AdaptiveAvgPool2d((1, 1)),
                torch.nn.Flatten(),
                torch.nn.Linear(hidden_channels, n_classes),
            )

        def forward(self, x):
            return self.net(x)

    return TinyConvNet()
