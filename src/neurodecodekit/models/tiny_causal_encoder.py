"""Tiny optional-Torch causal encoder with safe NPZ checkpointing."""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping

from neurodecodekit.cache.neurotoken_stream import CausalWindowTokenStream

if TYPE_CHECKING:
    from neurodecodekit.training.causal_motifs import LoadedCausalMotifPartition


TINY_CAUSAL_CHECKPOINT_SCHEMA_NAME = "tiny-causal-encoder-checkpoint"
TINY_CAUSAL_CHECKPOINT_SCHEMA_VERSION = 0
TINY_CAUSAL_MODEL_NAME = "TinyCausalWindowEncoder"
CHECKPOINT_PARAMETER_NAMES = (
    "encoder_input.weight",
    "encoder_input.bias",
    "encoder_output.weight",
    "encoder_output.bias",
    "motif_probe.weight",
    "motif_probe.bias",
)


@dataclass(frozen=True)
class TinyCausalEncoderConfig:
    """Registered train and architecture constants, excluding fixture geometry."""

    hidden_dim: int = 12
    embedding_dim: int = 8
    model_seed: int = 2221
    learning_rate: float = 0.01
    weight_decay: float = 0.0001
    batch_size: int = 64
    max_epochs: int = 60
    patience: int = 8
    num_threads: int = 1
    deterministic_algorithms: bool = True

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def config_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class CausalFrameDataset:
    """Flattened complete causal frames and inspectable row/grid identity."""

    windows: Any
    labels: Any
    item_indices: Any
    frame_start_samples: Any
    frame_end_samples: Any

    @property
    def n_frames(self) -> int:
        return int(self.windows.shape[0])

    @property
    def array_bytes(self) -> int:
        return int(
            self.windows.nbytes
            + self.labels.nbytes
            + self.item_indices.nbytes
            + self.frame_start_samples.nbytes
            + self.frame_end_samples.nbytes
        )


@dataclass(frozen=True)
class TinyCausalTrainingResult:
    """Selected validation checkpoint and train-only fit records."""

    model: Any
    normalization_mean: Any
    normalization_std: Any
    class_weights: Any
    training_history: list[dict[str, object]]
    best_epoch: int
    epochs_ran: int
    stopped_early: bool
    train_metrics: dict[str, object]
    validation_metrics: dict[str, object]
    parameter_count: int
    encoder_parameter_count: int
    probe_parameter_count: int
    parameter_bytes_float32: int
    runtime_sec: float
    torch_version: str
    config: TinyCausalEncoderConfig


def registered_tiny_causal_encoder_config() -> TinyCausalEncoderConfig:
    return TinyCausalEncoderConfig()


def fit_train_channel_standardizer(
    partition: LoadedCausalMotifPartition,
) -> tuple[Any, Any, dict[str, object]]:
    """Fit per-channel mean/std using valid train samples only."""

    np = _require_numpy()
    signals = np.asarray(partition.signals, dtype="float32")
    sums = np.zeros(signals.shape[1], dtype="float64")
    squared_sums = np.zeros(signals.shape[1], dtype="float64")
    valid_count = 0
    for index, length_value in enumerate(partition.input_lengths.tolist()):
        length = int(length_value)
        row = signals[index, :, :length].astype("float64", copy=False)
        sums += row.sum(axis=1)
        squared_sums += np.square(row).sum(axis=1)
        valid_count += length
    if valid_count < 1:
        raise ValueError("train partition has no valid samples")
    mean = (sums / valid_count).astype("float32")
    variance = squared_sums / valid_count - np.square(mean.astype("float64"))
    std = np.sqrt(np.maximum(variance, 1e-8)).astype("float32")
    if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std <= 0).any():
        raise RuntimeError("train-only standardizer produced invalid statistics")
    return mean, std, {
        "fit_split": "train",
        "valid_samples": valid_count,
        "mean_sha256": _array_sha256(mean),
        "std_sha256": _array_sha256(std),
        "minimum_std": float(std.min()),
        "maximum_std": float(std.max()),
    }


def extract_causal_frame_dataset(
    partition: LoadedCausalMotifPartition,
    *,
    normalization_mean=None,
    normalization_std=None,
) -> CausalFrameDataset:
    """Extract complete kernel/stride frames without padding or future context."""

    np = _require_numpy()
    protocol = partition.metadata["protocol"]
    kernel_size = int(protocol["kernel_size"])
    stride = int(protocol["stride"])
    n_channels = int(partition.signals.shape[1])
    total_frames = int(partition.frame_lengths.sum())
    windows = np.empty((total_frames, n_channels * kernel_size), dtype="float32")
    labels = np.empty(total_frames, dtype="int64")
    item_indices = np.empty(total_frames, dtype="int32")
    starts_out = np.empty(total_frames, dtype="int32")
    ends_out = np.empty(total_frames, dtype="int32")
    if (normalization_mean is None) != (normalization_std is None):
        raise ValueError("normalization mean and std must be supplied together")
    mean = (
        np.asarray(normalization_mean, dtype="float32")
        if normalization_mean is not None
        else None
    )
    std = (
        np.asarray(normalization_std, dtype="float32")
        if normalization_std is not None
        else None
    )
    if mean is not None and (mean.shape != (n_channels,) or std.shape != (n_channels,)):
        raise ValueError("normalization vectors must contain one value per channel")

    cursor = 0
    for item_index, frame_count_value in enumerate(partition.frame_lengths.tolist()):
        frame_count = int(frame_count_value)
        starts = np.arange(frame_count, dtype="int32") * stride
        for local_index, start_value in enumerate(starts.tolist()):
            start = int(start_value)
            frame = partition.signals[
                item_index, :, start : start + kernel_size
            ].astype("float32", copy=False)
            if mean is not None:
                frame = (frame - mean[:, None]) / std[:, None]
            windows[cursor] = frame.reshape(-1)
            labels[cursor] = int(partition.frame_labels[item_index, local_index])
            item_indices[cursor] = item_index
            starts_out[cursor] = start
            ends_out[cursor] = start + kernel_size
            cursor += 1
    if cursor != total_frames:
        raise RuntimeError("causal frame extraction count drifted")
    return CausalFrameDataset(
        windows=windows,
        labels=labels,
        item_indices=item_indices,
        frame_start_samples=starts_out,
        frame_end_samples=ends_out,
    )


def train_tiny_causal_encoder(
    train_partition: LoadedCausalMotifPartition,
    validation_partition: LoadedCausalMotifPartition,
    *,
    config: TinyCausalEncoderConfig | None = None,
) -> tuple[TinyCausalTrainingResult, dict[str, object]]:
    """Fit one deterministic CPU model and select one epoch on validation only."""

    selected = config or registered_tiny_causal_encoder_config()
    _validate_config(selected)
    _validate_partition_pair(train_partition, validation_partition)
    np, torch = _require_ml_dependencies()
    started_at = time.perf_counter()
    _configure_torch(torch, selected)
    mean, std, standardizer_report = fit_train_channel_standardizer(train_partition)
    train_frames = extract_causal_frame_dataset(
        train_partition, normalization_mean=mean, normalization_std=std
    )
    validation_frames = extract_causal_frame_dataset(
        validation_partition, normalization_mean=mean, normalization_std=std
    )
    n_classes = int(train_partition.metadata["protocol"]["n_motif_classes"]) + 1
    class_counts = np.bincount(train_frames.labels, minlength=n_classes)
    if (class_counts < 1).any():
        raise ValueError("every motif class must occur in the train partition")
    class_weights = (
        train_frames.n_frames / (n_classes * class_counts.astype("float64"))
    ).astype("float32")

    torch.manual_seed(selected.model_seed)
    np.random.seed(selected.model_seed)
    model = _build_model(
        torch,
        input_dim=int(train_frames.windows.shape[1]),
        hidden_dim=selected.hidden_dim,
        embedding_dim=selected.embedding_dim,
        n_classes=n_classes,
    ).to("cpu")
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=selected.learning_rate,
        weight_decay=selected.weight_decay,
    )
    criterion = torch.nn.CrossEntropyLoss(weight=torch.from_numpy(class_weights))
    rng = np.random.Generator(np.random.PCG64(selected.model_seed))
    history: list[dict[str, object]] = []
    best_key: tuple[float, float, int] | None = None
    best_state: dict[str, Any] | None = None
    best_epoch = -1
    epochs_without_improvement = 0

    for epoch in range(selected.max_epochs):
        model.train()
        order = rng.permutation(train_frames.n_frames)
        epoch_loss = 0.0
        seen = 0
        for start in range(0, len(order), selected.batch_size):
            indices = order[start : start + selected.batch_size]
            xb = torch.from_numpy(train_frames.windows[indices])
            yb = torch.from_numpy(train_frames.labels[indices])
            optimizer.zero_grad(set_to_none=True)
            logits = model(xb)
            loss = criterion(logits, yb)
            if not bool(torch.isfinite(loss)):
                raise RuntimeError("tiny causal encoder produced non-finite loss")
            loss.backward()
            optimizer.step()
            count = int(len(indices))
            epoch_loss += float(loss.detach()) * count
            seen += count
        validation_logits = _predict_logits_batch(
            torch, model, validation_frames.windows, batch_size=selected.batch_size
        )
        validation_predictions = validation_logits.argmax(axis=1)
        validation_metrics = classification_metrics(
            validation_frames.labels,
            validation_predictions,
            n_classes=n_classes,
        )
        validation_loss = _cross_entropy_from_logits(
            np,
            validation_logits,
            validation_frames.labels,
            class_weights,
        )
        row = {
            "epoch": epoch + 1,
            "train_loss": epoch_loss / max(1, seen),
            "validation_loss": validation_loss,
            "validation_accuracy": validation_metrics["accuracy"],
            "validation_balanced_accuracy": validation_metrics["balanced_accuracy"],
        }
        history.append(row)
        key = (
            -float(validation_metrics["balanced_accuracy"]),
            float(validation_loss),
            epoch,
        )
        if best_key is None or key < best_key:
            best_key = key
            best_state = {
                name: value.detach().cpu().clone()
                for name, value in model.state_dict().items()
            }
            best_epoch = epoch + 1
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
        if epochs_without_improvement >= selected.patience:
            break
    if best_state is None or best_epoch < 1:
        raise RuntimeError("tiny causal encoder did not select a validation checkpoint")
    model.load_state_dict(best_state, strict=True)
    model.eval()
    train_predictions = _predict_logits_batch(
        torch, model, train_frames.windows, batch_size=selected.batch_size
    ).argmax(axis=1)
    validation_predictions = _predict_logits_batch(
        torch, model, validation_frames.windows, batch_size=selected.batch_size
    ).argmax(axis=1)
    train_metrics = classification_metrics(
        train_frames.labels, train_predictions, n_classes=n_classes
    )
    validation_metrics = classification_metrics(
        validation_frames.labels, validation_predictions, n_classes=n_classes
    )
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    encoder_parameter_count = sum(
        int(value.numel())
        for name, value in model.named_parameters()
        if name.startswith("encoder_")
    )
    probe_parameter_count = parameter_count - encoder_parameter_count
    result = TinyCausalTrainingResult(
        model=model,
        normalization_mean=mean,
        normalization_std=std,
        class_weights=class_weights,
        training_history=history,
        best_epoch=best_epoch,
        epochs_ran=len(history),
        stopped_early=len(history) < selected.max_epochs,
        train_metrics=train_metrics,
        validation_metrics=validation_metrics,
        parameter_count=parameter_count,
        encoder_parameter_count=encoder_parameter_count,
        probe_parameter_count=probe_parameter_count,
        parameter_bytes_float32=parameter_count * 4,
        runtime_sec=round(time.perf_counter() - started_at, 6),
        torch_version=str(torch.__version__),
        config=selected,
    )
    fit_report = {
        "standardizer": standardizer_report,
        "class_weight_fit_split": "train",
        "class_counts": [int(value) for value in class_counts.tolist()],
        "class_weights": [float(value) for value in class_weights.tolist()],
        "class_weights_sha256": _array_sha256(class_weights),
        "train_frames": train_frames.n_frames,
        "validation_frames": validation_frames.n_frames,
        "train_frame_array_bytes": train_frames.array_bytes,
        "validation_frame_array_bytes": validation_frames.array_bytes,
    }
    return result, fit_report


def save_tiny_causal_encoder_checkpoint(
    path: str | Path,
    *,
    training: TinyCausalTrainingResult,
    metadata: Mapping[str, Any],
) -> dict[str, object]:
    """Save plain numeric weights and metadata without a pickle payload."""

    np, _torch = _require_ml_dependencies()
    output = Path(path)
    if output.exists():
        raise FileExistsError(f"Refusing to replace existing checkpoint: {output}")
    state = training.model.state_dict()
    arrays = {
        name: state[name].detach().cpu().numpy().astype("float32", copy=True)
        for name in CHECKPOINT_PARAMETER_NAMES
    }
    arrays["normalization_mean"] = np.asarray(
        training.normalization_mean, dtype="float32"
    )
    arrays["normalization_std"] = np.asarray(
        training.normalization_std, dtype="float32"
    )
    payload_sha256 = _checkpoint_payload_sha256(arrays)
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata.update(
        {
            "schema": {
                "name": TINY_CAUSAL_CHECKPOINT_SCHEMA_NAME,
                "version": TINY_CAUSAL_CHECKPOINT_SCHEMA_VERSION,
            },
            "model_name": TINY_CAUSAL_MODEL_NAME,
            "parameter_payload_sha256": payload_sha256,
            "serialization": "numpy_npz_allow_pickle_false",
            "trainable_parameters": training.parameter_count,
            "encoder_parameters": training.encoder_parameter_count,
            "probe_parameters": training.probe_parameter_count,
            "parameter_bytes_float32": training.parameter_bytes_float32,
            "normalization_fit_split": "train",
            "selected_epoch": training.best_epoch,
            "config": training.config.to_dict(),
            "config_sha256": training.config.config_sha256,
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        **arrays,
        metadata=json.dumps(checkpoint_metadata, sort_keys=True),
    )
    return {
        "path": str(output),
        "bytes": int(output.stat().st_size),
        "sha256": _file_sha256(output),
        "parameter_payload_sha256": payload_sha256,
        "metadata": checkpoint_metadata,
    }


def load_tiny_causal_encoder_checkpoint(
    path: str | Path,
) -> tuple[FrozenTinyCausalEncoderProducer, dict[str, Any]]:
    """Load the safe numeric checkpoint and rebuild one CPU producer."""

    np, torch = _require_ml_dependencies()
    checkpoint_path = Path(path)
    required = {*CHECKPOINT_PARAMETER_NAMES, "normalization_mean", "normalization_std"}
    with np.load(checkpoint_path, allow_pickle=False) as data:
        members = set(data.files)
        expected_members = required | {"metadata"}
        missing = sorted(expected_members - members)
        if missing:
            raise ValueError(f"tiny causal checkpoint is missing arrays: {missing}")
        unexpected = sorted(members - expected_members)
        if unexpected:
            raise ValueError(f"tiny causal checkpoint has unexpected arrays: {unexpected}")
        arrays = {name: data[name].copy() for name in required}
        metadata = _decode_metadata(data["metadata"])
    schema = metadata.get("schema") or {}
    if schema.get("name") != TINY_CAUSAL_CHECKPOINT_SCHEMA_NAME:
        raise ValueError("unsupported tiny causal checkpoint schema")
    if schema.get("version") != TINY_CAUSAL_CHECKPOINT_SCHEMA_VERSION:
        raise ValueError("unsupported tiny causal checkpoint version")
    if metadata.get("model_name") != TINY_CAUSAL_MODEL_NAME:
        raise ValueError("tiny causal checkpoint model name is invalid")
    if metadata.get("serialization") != "numpy_npz_allow_pickle_false":
        raise ValueError("tiny causal checkpoint serialization contract is invalid")
    if metadata.get("normalization_fit_split") != "train":
        raise ValueError("tiny causal checkpoint normalization was not fit on train")
    if metadata.get("parameter_payload_sha256") != _checkpoint_payload_sha256(arrays):
        raise ValueError("tiny causal checkpoint payload hash mismatch")
    geometry = metadata.get("geometry") or {}
    n_channels = int(geometry.get("n_channels", 0))
    kernel_size = int(geometry.get("kernel_size", 0))
    stride = int(geometry.get("stride", 0))
    n_classes = int(geometry.get("n_classes", 0))
    sampling_rate_hz = float(geometry.get("sampling_rate_hz", 0))
    if (
        n_channels < 1
        or kernel_size < 1
        or stride < 1
        or stride > kernel_size
        or n_classes < 2
        or not math.isfinite(sampling_rate_hz)
        or sampling_rate_hz <= 0
    ):
        raise ValueError("tiny causal checkpoint geometry is invalid")
    config_values = metadata.get("config") or {}
    try:
        config = TinyCausalEncoderConfig(**config_values)
    except (TypeError, ValueError) as exc:
        raise ValueError("tiny causal checkpoint config fields are invalid") from exc
    _validate_config(config)
    if metadata.get("config_sha256") != config.config_sha256:
        raise ValueError("tiny causal checkpoint config hash mismatch")
    _validate_checkpoint_shapes(
        arrays,
        n_channels=n_channels,
        kernel_size=kernel_size,
        hidden_dim=config.hidden_dim,
        embedding_dim=config.embedding_dim,
        n_classes=n_classes,
    )
    parameter_count = sum(int(arrays[name].size) for name in CHECKPOINT_PARAMETER_NAMES)
    encoder_count = sum(
        int(arrays[name].size)
        for name in CHECKPOINT_PARAMETER_NAMES
        if name.startswith("encoder_")
    )
    probe_count = parameter_count - encoder_count
    if (
        metadata.get("trainable_parameters") != parameter_count
        or metadata.get("encoder_parameters") != encoder_count
        or metadata.get("probe_parameters") != probe_count
        or metadata.get("parameter_bytes_float32") != parameter_count * 4
    ):
        raise ValueError("tiny causal checkpoint parameter accounting is invalid")
    if not isinstance(metadata.get("selected_epoch"), int) or int(
        metadata["selected_epoch"]
    ) < 1:
        raise ValueError("tiny causal checkpoint selected epoch is invalid")
    model = _build_model(
        torch,
        input_dim=n_channels * kernel_size,
        hidden_dim=config.hidden_dim,
        embedding_dim=config.embedding_dim,
        n_classes=n_classes,
    ).to("cpu")
    state = {
        name: torch.from_numpy(arrays[name].astype("float32", copy=False))
        for name in CHECKPOINT_PARAMETER_NAMES
    }
    model.load_state_dict(state, strict=True)
    model.eval()
    producer = FrozenTinyCausalEncoderProducer(
        torch=torch,
        model=model,
        normalization_mean=arrays["normalization_mean"],
        normalization_std=arrays["normalization_std"],
        n_channels=n_channels,
        source_sampling_rate_hz=sampling_rate_hz,
        embedding_dim=config.embedding_dim,
        kernel_size=kernel_size,
        stride=stride,
        n_classes=n_classes,
        parameter_payload_sha256=str(metadata["parameter_payload_sha256"]),
    )
    return producer, metadata


class FrozenTinyCausalEncoderProducer:
    """Frozen one-frame Torch encoder implementing the Loop 21 stream protocol."""

    def __init__(
        self,
        *,
        torch,
        model,
        normalization_mean,
        normalization_std,
        n_channels: int,
        source_sampling_rate_hz: float,
        embedding_dim: int,
        kernel_size: int,
        stride: int,
        n_classes: int,
        parameter_payload_sha256: str,
    ) -> None:
        np = _require_numpy()
        self.torch = torch
        self.model = model
        self.normalization_mean = np.asarray(
            normalization_mean, dtype="float32"
        ).copy()
        self.normalization_std = np.asarray(
            normalization_std, dtype="float32"
        ).copy()
        self.n_channels = int(n_channels)
        self.source_sampling_rate_hz = float(source_sampling_rate_hz)
        self.embedding_dim = int(embedding_dim)
        self.kernel_size = int(kernel_size)
        self.stride = int(stride)
        self.n_classes = int(n_classes)
        self.token_dtype = "float32"
        self.parameter_payload_sha256 = str(parameter_payload_sha256)
        if (
            self.n_channels < 1
            or self.embedding_dim < 1
            or self.kernel_size < 1
            or self.stride < 1
            or self.stride > self.kernel_size
            or self.n_classes < 2
            or not math.isfinite(self.source_sampling_rate_hz)
            or self.source_sampling_rate_hz <= 0
        ):
            raise ValueError("checkpoint producer geometry is invalid")
        if self.normalization_mean.shape != (self.n_channels,):
            raise ValueError("checkpoint normalization mean shape is invalid")
        if self.normalization_std.shape != (self.n_channels,):
            raise ValueError("checkpoint normalization std shape is invalid")
        if (self.normalization_std <= 0).any():
            raise ValueError("checkpoint normalization std must be positive")

    @property
    def mutable_state_bound_bytes(self) -> int:
        return self.n_channels * max(0, self.kernel_size - 1) * 4

    @property
    def producer_right_context_samples(self) -> int:
        return 0

    @property
    def trainable_parameter_count(self) -> int:
        return sum(int(value.numel()) for value in self.model.parameters())

    @property
    def fixed_parameter_bytes(self) -> int:
        return int(
            self.trainable_parameter_count * 4
            + self.normalization_mean.nbytes
            + self.normalization_std.nbytes
        )

    def new_stream(
        self,
        *,
        source_start_sec: float = 0.0,
        max_chunk_samples: int = 4096,
        max_total_samples: int = 65536,
        max_total_tokens: int = 4096,
    ) -> CausalWindowTokenStream:
        return CausalWindowTokenStream(
            self,
            source_start_sec=source_start_sec,
            max_chunk_samples=max_chunk_samples,
            max_total_samples=max_total_samples,
            max_total_tokens=max_total_tokens,
        )

    def project_frame(self, frame):
        """Encode one raw complete frame using canonical batch-size-one arithmetic."""

        np = _require_numpy()
        value = np.asarray(frame, dtype="float32")
        expected = self.n_channels * self.kernel_size
        if value.shape != (expected,):
            raise ValueError(f"frame must be flattened with {expected} values")
        matrix = value.reshape(self.n_channels, self.kernel_size)
        normalized = (
            (matrix - self.normalization_mean[:, None])
            / self.normalization_std[:, None]
        ).reshape(1, -1)
        with self.torch.no_grad():
            embedding = self.model.encode(self.torch.from_numpy(normalized))
        return embedding.detach().cpu().numpy().astype("float32", copy=True)

    def probe_embedding(self, embedding):
        """Apply the diagnostic motif probe to one embedding."""

        np = _require_numpy()
        value = np.asarray(embedding, dtype="float32")
        if value.shape != (self.embedding_dim,):
            raise ValueError("embedding has the wrong shape for the motif probe")
        with self.torch.no_grad():
            logits = self.model.probe(self.torch.from_numpy(value[None, :]))
        return logits.detach().cpu().numpy().astype("float32", copy=True)


def canonical_partition_outputs(
    producer: FrozenTinyCausalEncoderProducer,
    partition: LoadedCausalMotifPartition,
) -> dict[str, Any]:
    """Run one canonical frame at a time for schedule-independent evaluation."""

    np = _require_numpy()
    raw = extract_causal_frame_dataset(partition)
    embeddings = []
    logits = []
    for window in raw.windows:
        embedding = producer.project_frame(window)
        embeddings.append(embedding)
        logits.append(producer.probe_embedding(embedding[0]))
    embedding_array = np.concatenate(embeddings, axis=0)
    logit_array = np.concatenate(logits, axis=0)
    predictions = logit_array.argmax(axis=1).astype("int64")
    return {
        "embeddings": embedding_array,
        "logits": logit_array,
        "predictions": predictions,
        "labels": raw.labels,
        "item_indices": raw.item_indices,
        "frame_start_samples": raw.frame_start_samples,
        "frame_end_samples": raw.frame_end_samples,
        "embedding_payload_sha256": _array_sha256(embedding_array),
    }


def batched_partition_outputs(
    producer: FrozenTinyCausalEncoderProducer,
    partition: LoadedCausalMotifPartition,
) -> dict[str, Any]:
    """Run all frames as one batch for a declared numerical compatibility check."""

    normalized = extract_causal_frame_dataset(
        partition,
        normalization_mean=producer.normalization_mean,
        normalization_std=producer.normalization_std,
    )
    with producer.torch.no_grad():
        value = producer.torch.from_numpy(normalized.windows)
        embeddings = producer.model.encode(value)
        logits = producer.model.probe(embeddings)
    return {
        "embeddings": embeddings.detach().cpu().numpy().astype("float32", copy=True),
        "logits": logits.detach().cpu().numpy().astype("float32", copy=True),
        "predictions": logits.argmax(dim=1).detach().cpu().numpy().astype("int64"),
        "labels": normalized.labels,
    }


def classification_metrics(
    targets, predictions, *, n_classes: int
) -> dict[str, object]:
    """Compute accuracy, balanced accuracy, macro-F1, and confusion without sklearn."""

    np = _require_numpy()
    y_true = np.asarray(targets, dtype="int64")
    y_pred = np.asarray(predictions, dtype="int64")
    if y_true.ndim != 1 or y_pred.shape != y_true.shape or len(y_true) < 1:
        raise ValueError("classification targets/predictions must be nonempty equal vectors")
    if (y_true < 0).any() or (y_true >= n_classes).any():
        raise ValueError("classification targets fall outside the vocabulary")
    if (y_pred < 0).any() or (y_pred >= n_classes).any():
        raise ValueError("classification predictions fall outside the vocabulary")
    confusion = np.zeros((n_classes, n_classes), dtype="int64")
    np.add.at(confusion, (y_true, y_pred), 1)
    support = confusion.sum(axis=1)
    if (support < 1).any():
        raise ValueError("balanced accuracy requires every class in the target partition")
    recall = confusion.diagonal() / support
    precision_denominator = confusion.sum(axis=0)
    precision = np.divide(
        confusion.diagonal(),
        precision_denominator,
        out=np.zeros(n_classes, dtype="float64"),
        where=precision_denominator > 0,
    )
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros(n_classes, dtype="float64"),
        where=(precision + recall) > 0,
    )
    return {
        "frames": int(len(y_true)),
        "correct": int((y_true == y_pred).sum()),
        "accuracy": float((y_true == y_pred).mean()),
        "balanced_accuracy": float(recall.mean()),
        "macro_f1": float(f1.mean()),
        "per_class_recall": [float(value) for value in recall.tolist()],
        "per_class_precision": [float(value) for value in precision.tolist()],
        "class_support": [int(value) for value in support.tolist()],
        "confusion_matrix": [
            [int(value) for value in row] for row in confusion.tolist()
        ],
    }


def train_only_prior_class(labels, *, n_classes: int) -> int:
    np = _require_numpy()
    values = np.asarray(labels, dtype="int64")
    counts = np.bincount(values, minlength=n_classes)
    return int(counts.argmax())


def _build_model(torch, *, input_dim: int, hidden_dim: int, embedding_dim: int, n_classes: int):
    class TinyCausalWindowEncoder(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder_input = torch.nn.Linear(input_dim, hidden_dim)
            self.encoder_output = torch.nn.Linear(hidden_dim, embedding_dim)
            self.motif_probe = torch.nn.Linear(embedding_dim, n_classes)

        def encode(self, value):
            rows = []
            for index in range(int(value.shape[0])):
                row = torch.nn.functional.gelu(
                    self.encoder_input(value[index : index + 1])
                )
                rows.append(
                    torch.nn.functional.gelu(self.encoder_output(row))
                )
            return torch.cat(rows, dim=0)

        def probe(self, embedding):
            return torch.cat(
                [
                    self.motif_probe(embedding[index : index + 1])
                    for index in range(int(embedding.shape[0]))
                ],
                dim=0,
            )

        def forward(self, value):
            return self.probe(self.encode(value))

    return TinyCausalWindowEncoder()


def _predict_logits_batch(torch, model, windows, *, batch_size: int):
    np = _require_numpy()
    model.eval()
    rows = []
    with torch.no_grad():
        for start in range(0, len(windows), batch_size):
            logits = model(torch.from_numpy(windows[start : start + batch_size]))
            rows.append(logits.detach().cpu().numpy().astype("float32", copy=True))
    return np.concatenate(rows, axis=0)


def _cross_entropy_from_logits(np, logits, labels, class_weights) -> float:
    shifted = logits.astype("float64") - logits.max(axis=1, keepdims=True)
    log_probabilities = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    rows = np.arange(len(labels))
    losses = -log_probabilities[rows, labels]
    weights = class_weights[labels].astype("float64")
    return float((losses * weights).sum() / weights.sum())


def _validate_partition_pair(train, validation) -> None:
    if train.split != "train" or validation.split != "validation":
        raise ValueError("training requires physical train and validation partitions")
    train_protocol = train.metadata.get("protocol_sha256")
    validation_protocol = validation.metadata.get("protocol_sha256")
    if train_protocol != validation_protocol:
        raise ValueError("train and validation fixture protocols do not match")
    if set(train.item_ids.tolist()).intersection(validation.item_ids.tolist()):
        raise ValueError("train and validation item IDs overlap")


def _validate_config(config: TinyCausalEncoderConfig) -> None:
    integer_values = {
        "hidden_dim": config.hidden_dim,
        "embedding_dim": config.embedding_dim,
        "batch_size": config.batch_size,
        "max_epochs": config.max_epochs,
        "patience": config.patience,
        "num_threads": config.num_threads,
    }
    if any(int(value) < 1 for value in integer_values.values()):
        raise ValueError("tiny causal encoder integer config values must be positive")
    if config.hidden_dim > 4096 or config.embedding_dim > 4096:
        raise ValueError("tiny causal encoder dimensions exceed safety bounds")
    if config.num_threads != 1:
        raise ValueError("tiny causal encoder gate requires exactly one CPU thread")
    for name, value in (
        ("learning_rate", config.learning_rate),
        ("weight_decay", config.weight_decay),
    ):
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be finite and positive")


def _configure_torch(torch, config: TinyCausalEncoderConfig) -> None:
    torch.set_num_threads(config.num_threads)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    torch.use_deterministic_algorithms(config.deterministic_algorithms)


def _validate_checkpoint_shapes(
    arrays: Mapping[str, Any],
    *,
    n_channels: int,
    kernel_size: int,
    hidden_dim: int,
    embedding_dim: int,
    n_classes: int,
) -> None:
    expected = {
        "encoder_input.weight": (hidden_dim, n_channels * kernel_size),
        "encoder_input.bias": (hidden_dim,),
        "encoder_output.weight": (embedding_dim, hidden_dim),
        "encoder_output.bias": (embedding_dim,),
        "motif_probe.weight": (n_classes, embedding_dim),
        "motif_probe.bias": (n_classes,),
        "normalization_mean": (n_channels,),
        "normalization_std": (n_channels,),
    }
    np = _require_numpy()
    for name, shape in expected.items():
        value = np.asarray(arrays[name])
        if value.shape != shape or value.dtype != np.dtype("float32"):
            raise ValueError(f"checkpoint {name} must be float32 with shape {shape}")
        if not np.isfinite(value).all():
            raise ValueError(f"checkpoint {name} contains non-finite values")


def _checkpoint_payload_sha256(arrays: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in sorted(arrays):
        value = _require_numpy().ascontiguousarray(arrays[name])
        digest.update(name.encode("utf-8"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(json.dumps(list(value.shape)).encode("ascii"))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _array_sha256(value) -> str:
    array = _require_numpy().ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        metadata = json.loads(str(raw))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("tiny causal checkpoint metadata is not valid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("tiny causal checkpoint metadata must decode to an object")
    return metadata


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Tiny causal encoding requires NumPy: `pip install numpy`.") from exc
    return np


def _require_ml_dependencies():
    np = _require_numpy()
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Tiny causal encoding requires the optional ML dependencies: "
            "`pip install -e '.[ml]'`."
        ) from exc
    return np, torch
