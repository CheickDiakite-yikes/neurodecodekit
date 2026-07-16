"""Exact optional-Torch models for the Loop 48 Stage C synthetic gate."""

from __future__ import annotations

import hashlib
import json
import math
import resource
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from neurodecodekit.preprocess.ctc_text import CTC_VOCAB, greedy_decode_ctc_ids


CHECKPOINT_SCHEMA_NAME = "neurodecodekit.tiny_causal_temporal_ctc_checkpoint"
CHECKPOINT_SCHEMA_VERSION = 0
CANDIDATE_MODEL_ID = "TinyCausalTemporalCTC-v0"
ABLATION_MODEL_ID = "TinyCausalTemporalAblation-v0"
REGISTERED_RECIPE_IDS = (
    "L48C-SYN-OPT0",
    "L48C-SYN-OPT1",
    "L48C-SYN-OPT2",
)


@dataclass(frozen=True)
class TemporalCTCConfig:
    """Frozen architecture and optimizer configuration for one synthetic fit."""

    architecture: str
    recipe_id: str
    optimizer: str
    learning_rate: float
    weight_decay: float
    optimizer_steps: int
    input_channels: int = 102
    classes: int = 28
    batch_size: int = 8
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    num_threads: int = 1
    deterministic_algorithms: bool = True
    seed: int = 4850

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class TemporalCTCTrainingResult:
    """One final-step deterministic synthetic training result."""

    model: Any
    config: TemporalCTCConfig
    loss_history: tuple[float, ...]
    optimizer_steps: int
    example_presentations: int
    parameter_count: int
    parameter_bytes_float32: int
    runtime_sec: float
    peak_rss_bytes: int
    torch_version: str

    def summary(self) -> dict[str, Any]:
        payload = asdict(self)
        payload.pop("model")
        payload["config"] = self.config.to_dict()
        payload["config_sha256"] = self.config.config_sha256
        payload["loss_history"] = list(self.loss_history)
        return payload


def registered_temporal_ctc_config(
    recipe_id: str,
    *,
    architecture: str = "candidate",
) -> TemporalCTCConfig:
    """Return one exact Stage C optimizer recipe for either registered model."""

    recipes = {
        "L48C-SYN-OPT0": ("adam", 0.003, 0.0, 360),
        "L48C-SYN-OPT1": ("adamw", 0.001, 0.01, 480),
        "L48C-SYN-OPT2": ("adamw", 0.003, 0.01, 480),
    }
    if recipe_id not in recipes:
        raise ValueError(f"unknown Stage C optimizer recipe: {recipe_id}")
    optimizer, learning_rate, weight_decay, steps = recipes[recipe_id]
    config = TemporalCTCConfig(
        architecture=architecture,
        recipe_id=recipe_id,
        optimizer=optimizer,
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        optimizer_steps=steps,
    )
    _validate_config(config)
    return config


def temporal_output_lengths(input_lengths):
    """Map 100 Hz source lengths to the registered 25 Hz causal output grid."""

    np = _require_numpy()
    lengths = np.asarray(input_lengths, dtype="int64")
    if lengths.ndim != 1 or len(lengths) < 1 or (lengths < 1).any():
        raise ValueError("input_lengths must be a nonempty positive vector")
    return (lengths + 3) // 4


def build_tiny_causal_temporal_ctc(config: TemporalCTCConfig):
    """Build the exact 7,692-parameter candidate or 7,568-parameter ablation."""

    _np, torch = _require_ml_dependencies()
    _validate_config(config)

    class ResidualTemporalBlock(torch.nn.Module):
        def __init__(self, channels: int, kernel_size: int, dilation: int):
            super().__init__()
            self.left_padding = dilation * (kernel_size - 1)
            self.conv = torch.nn.Conv1d(
                channels,
                channels,
                kernel_size=kernel_size,
                dilation=dilation,
                padding=0,
                bias=True,
            )
            self.norm = torch.nn.LayerNorm(channels)
            self.activation = torch.nn.GELU(approximate="none")

        def forward(self, value):
            hidden = torch.nn.functional.pad(value, (self.left_padding, 0), value=0.0)
            hidden = self.conv(hidden).transpose(1, 2)
            hidden = self.activation(self.norm(hidden)).transpose(1, 2)
            return value + hidden * 0.1

    if config.architecture == "candidate":

        class TinyCausalTemporalCTC(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.input_conv = torch.nn.Conv1d(102, 16, kernel_size=1, bias=True)
                self.blocks = torch.nn.ModuleList(
                    ResidualTemporalBlock(16, 5, dilation) for dilation in (1, 2, 4, 1)
                )
                self.reducer = torch.nn.Conv1d(
                    16,
                    16,
                    kernel_size=16,
                    stride=4,
                    groups=16,
                    padding=0,
                    bias=False,
                )
                self.output_conv = torch.nn.Conv1d(16, 28, kernel_size=1, bias=True)

            def forward(self, value):
                hidden = self.input_conv(value)
                for block in self.blocks:
                    hidden = block(hidden)
                hidden = self.reducer(torch.nn.functional.pad(hidden, (15, 0), value=0.0))
                return self.output_conv(hidden).transpose(1, 2)

        model = TinyCausalTemporalCTC()
        expected_parameters = 7692
    else:

        class TinyCausalTemporalAblation(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.input_conv = torch.nn.Conv1d(102, 29, kernel_size=1, bias=True)
                self.blocks = torch.nn.ModuleList(ResidualTemporalBlock(29, 1, 1) for _ in range(4))
                self.reducer = torch.nn.Conv1d(
                    29,
                    29,
                    kernel_size=1,
                    stride=4,
                    groups=29,
                    padding=0,
                    bias=False,
                )
                self.output_conv = torch.nn.Conv1d(29, 28, kernel_size=1, bias=True)

            def forward(self, value):
                hidden = self.input_conv(value)
                for block in self.blocks:
                    hidden = block(hidden)
                hidden = self.reducer(hidden)
                return self.output_conv(hidden).transpose(1, 2)

        model = TinyCausalTemporalAblation()
        expected_parameters = 7568

    parameter_count = sum(int(value.numel()) for value in model.parameters())
    if parameter_count != expected_parameters:
        raise RuntimeError(
            f"{config.architecture} parameter count {parameter_count} != {expected_parameters}"
        )
    return model.to("cpu")


def train_tiny_causal_temporal_ctc(
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    config: TemporalCTCConfig,
) -> TemporalCTCTrainingResult:
    """Run one exact final-step-only deterministic synthetic fit."""

    np, torch = _require_ml_dependencies()
    _validate_config(config)
    arrays = _validate_training_arrays(
        np,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
    )
    _configure_torch(torch, config)
    torch.manual_seed(config.seed)
    np.random.seed(config.seed)
    model = build_tiny_causal_temporal_ctc(config)
    optimizer_class = torch.optim.Adam if config.optimizer == "adam" else torch.optim.AdamW
    optimizer = optimizer_class(
        model.parameters(),
        lr=config.learning_rate,
        betas=(config.beta1, config.beta2),
        eps=config.epsilon,
        weight_decay=config.weight_decay,
    )
    criterion = torch.nn.CTCLoss(blank=0, reduction="mean", zero_infinity=False)
    rng = np.random.Generator(np.random.PCG64(config.seed))
    started_at = time.perf_counter()
    losses: list[float] = []
    example_presentations = 0
    order = np.empty(0, dtype="int64")
    cursor = 0
    model.train()
    for _step in range(config.optimizer_steps):
        if cursor >= len(order):
            order = rng.permutation(len(arrays["signals"])).astype("int64", copy=False)
            cursor = 0
        batch_indices = order[cursor : cursor + config.batch_size]
        cursor += len(batch_indices)
        xb = torch.from_numpy(arrays["signals"][batch_indices])
        targets = torch.from_numpy(arrays["target_token_ids"][batch_indices])
        target_len = torch.from_numpy(arrays["target_lengths"][batch_indices])
        output_len = torch.from_numpy(arrays["output_lengths"][batch_indices])
        optimizer.zero_grad(set_to_none=True)
        logits = model(xb)
        loss = criterion(
            logits.log_softmax(dim=2).permute(1, 0, 2),
            targets,
            output_len,
            target_len,
        )
        if not bool(torch.isfinite(loss)):
            raise RuntimeError("Stage C temporal CTC produced non-finite loss")
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
        example_presentations += int(len(batch_indices))
    model.eval()
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    return TemporalCTCTrainingResult(
        model=model,
        config=config,
        loss_history=tuple(losses),
        optimizer_steps=len(losses),
        example_presentations=example_presentations,
        parameter_count=parameter_count,
        parameter_bytes_float32=parameter_count * 4,
        runtime_sec=round(time.perf_counter() - started_at, 6),
        peak_rss_bytes=_peak_rss_bytes(),
        torch_version=str(torch.__version__),
    )


def predict_tiny_causal_temporal_ctc(
    model,
    *,
    signals,
    input_lengths,
    batch_size: int = 8,
    include_logits: bool = False,
) -> dict[str, Any]:
    """Run target-blind greedy prediction on the causal 25 Hz output grid."""

    np, torch = _require_ml_dependencies()
    values, lengths = _validate_signal_arrays(np, signals, input_lengths)
    if batch_size < 1 or batch_size > 8:
        raise ValueError("batch_size must be between 1 and 8")
    output_lengths = temporal_output_lengths(lengths)
    predictions: list[str] = []
    token_rows_out: list[list[int]] = []
    logits_out: list[Any] = []
    blank_count = 0
    valid_steps = 0
    model.eval()
    started_at = time.perf_counter()
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            stop = min(len(values), start + batch_size)
            logits = model(torch.from_numpy(values[start:stop])).cpu().numpy()
            for row_logits, length in zip(
                logits,
                output_lengths[start:stop],
                strict=True,
            ):
                valid_logits = row_logits[: int(length)].copy()
                token_row = valid_logits.argmax(axis=1).astype("int64", copy=False)
                predictions.append(greedy_decode_ctc_ids(token_row))
                token_rows_out.append(token_row.tolist())
                blank_count += int((token_row == 0).sum())
                valid_steps += int(length)
                if include_logits:
                    logits_out.append(valid_logits)
    report = {
        "predictions": predictions,
        "token_rows": token_rows_out,
        "output_lengths": output_lengths.tolist(),
        "prediction_count": len(predictions),
        "blank_count": blank_count,
        "valid_steps": valid_steps,
        "blank_fraction": blank_count / valid_steps if valid_steps else 0.0,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "model_run_count": 1,
    }
    if include_logits:
        report["logits"] = logits_out
    return report


def save_tiny_causal_temporal_checkpoint(
    path: str | Path,
    *,
    model,
    config: TemporalCTCConfig,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Save one numeric-only model state with strict hash-bound metadata."""

    np, _torch = _require_ml_dependencies()
    _validate_config(config)
    output = Path(path)
    if output.exists():
        raise FileExistsError(f"Refusing to replace checkpoint: {output}")
    arrays = {
        name: value.detach().cpu().numpy().astype("float32", copy=True)
        for name, value in model.state_dict().items()
    }
    payload_hash = _checkpoint_payload_sha256(arrays)
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata.update(
        {
            "schema": {
                "name": CHECKPOINT_SCHEMA_NAME,
                "version": CHECKPOINT_SCHEMA_VERSION,
            },
            "model_id": (
                CANDIDATE_MODEL_ID if config.architecture == "candidate" else ABLATION_MODEL_ID
            ),
            "serialization": "numpy_npz_allow_pickle_false",
            "parameter_payload_sha256": payload_hash,
            "parameter_count": sum(int(value.size) for value in arrays.values()),
            "parameter_bytes_float32": sum(int(value.nbytes) for value in arrays.values()),
            "config": config.to_dict(),
            "config_sha256": config.config_sha256,
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output, **arrays, metadata=json.dumps(checkpoint_metadata, sort_keys=True))
    return {
        "path": str(output),
        "bytes": int(output.stat().st_size),
        "sha256": _file_sha256(output),
        "parameter_payload_sha256": payload_hash,
        "metadata": checkpoint_metadata,
    }


def load_tiny_causal_temporal_checkpoint(path: str | Path):
    """Load a safe numeric Stage C checkpoint and rebuild its exact model."""

    np, torch = _require_ml_dependencies()
    checkpoint = Path(path)
    with np.load(checkpoint, allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise ValueError("Stage C checkpoint lacks metadata")
        metadata = _decode_metadata(data["metadata"])
        arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
    if metadata.get("schema") != {
        "name": CHECKPOINT_SCHEMA_NAME,
        "version": CHECKPOINT_SCHEMA_VERSION,
    }:
        raise ValueError("unsupported Stage C checkpoint schema")
    if metadata.get("serialization") != "numpy_npz_allow_pickle_false":
        raise ValueError("Stage C checkpoint serialization is invalid")
    try:
        config = TemporalCTCConfig(**metadata["config"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Stage C checkpoint config is invalid") from exc
    _validate_config(config)
    if metadata.get("config_sha256") != config.config_sha256:
        raise ValueError("Stage C checkpoint config hash mismatch")
    if metadata.get("parameter_payload_sha256") != _checkpoint_payload_sha256(arrays):
        raise ValueError("Stage C checkpoint payload hash mismatch")
    model = build_tiny_causal_temporal_ctc(config)
    expected = model.state_dict()
    if set(arrays) != set(expected):
        raise ValueError("Stage C checkpoint parameter names are invalid")
    state = {}
    for name, expected_value in expected.items():
        if arrays[name].shape != tuple(expected_value.shape):
            raise ValueError(f"Stage C checkpoint shape mismatch for {name}")
        if arrays[name].dtype != np.dtype("float32"):
            raise ValueError(f"Stage C checkpoint dtype mismatch for {name}")
        state[name] = torch.from_numpy(arrays[name])
    model.load_state_dict(state, strict=True)
    model.eval()
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    if metadata.get("parameter_count") != parameter_count:
        raise ValueError("Stage C checkpoint parameter accounting mismatch")
    return model, config, metadata


def _validate_training_arrays(
    np,
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
) -> dict[str, Any]:
    values, lengths = _validate_signal_arrays(np, signals, input_lengths)
    target_ids = np.asarray(target_token_ids, dtype="int64")
    target_len = np.asarray(target_lengths, dtype="int64")
    if target_ids.ndim != 2 or target_ids.shape[0] != len(values):
        raise ValueError("target_token_ids must be [items, max_target_length]")
    if target_len.shape != (len(values),):
        raise ValueError("target_lengths must match signal rows")
    if (target_len < 1).any() or (target_len > target_ids.shape[1]).any():
        raise ValueError("target_lengths fall outside padded target width")
    output_lengths = temporal_output_lengths(lengths)
    for row, length, output_length in zip(
        target_ids,
        target_len,
        output_lengths,
        strict=True,
    ):
        valid = row[: int(length)]
        if (valid <= 0).any() or (valid >= len(CTC_VOCAB)).any():
            raise ValueError("valid target IDs must exclude blank and stay in vocabulary")
        if (row[int(length) :] != 0).any():
            raise ValueError("target padding must use blank zero")
        adjacent_repeats = int((valid[1:] == valid[:-1]).sum())
        if int(output_length) < int(length) + adjacent_repeats:
            raise ValueError("target is infeasible on the registered Stage C output grid")
    return {
        "signals": values,
        "input_lengths": lengths,
        "output_lengths": np.ascontiguousarray(output_lengths),
        "target_token_ids": np.ascontiguousarray(target_ids),
        "target_lengths": np.ascontiguousarray(target_len),
    }


def _validate_signal_arrays(np, signals, input_lengths):
    values = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or values.shape[0] < 1 or values.shape[1] != 102:
        raise ValueError(f"signals must be nonempty [items, 102, time], got {values.shape}")
    if not np.isfinite(values).all():
        raise ValueError("signals contain non-finite values")
    if lengths.shape != (len(values),):
        raise ValueError("input_lengths must match signal rows")
    if (lengths < 1).any() or (lengths > values.shape[2]).any():
        raise ValueError("input_lengths fall outside padded signal width")
    for row, length in zip(values, lengths, strict=True):
        if np.any(row[:, int(length) :] != 0.0):
            raise ValueError("signal padding must be exactly zero")
    return np.ascontiguousarray(values), np.ascontiguousarray(lengths)


def _validate_config(config: TemporalCTCConfig) -> None:
    if config.architecture not in {"candidate", "ablation"}:
        raise ValueError("architecture must be candidate or ablation")
    expected = {
        "L48C-SYN-OPT0": ("adam", 0.003, 0.0, 360),
        "L48C-SYN-OPT1": ("adamw", 0.001, 0.01, 480),
        "L48C-SYN-OPT2": ("adamw", 0.003, 0.01, 480),
    }
    if config.recipe_id not in expected:
        raise ValueError("unregistered Stage C optimizer recipe")
    if (config.optimizer, config.learning_rate, config.weight_decay, config.optimizer_steps) != (
        expected[config.recipe_id]
    ):
        raise ValueError("Stage C optimizer recipe values drifted")
    if (config.input_channels, config.classes, config.batch_size) != (102, 28, 8):
        raise ValueError(
            "registered Stage C geometry is fixed at 102 channels, 28 classes, batch 8"
        )
    if config.seed != 4850 or config.num_threads != 1:
        raise ValueError("registered Stage C fits require seed 4850 and one thread")
    for name, value, registered in (
        ("beta1", config.beta1, 0.9),
        ("beta2", config.beta2, 0.999),
        ("epsilon", config.epsilon, 1e-8),
    ):
        if not math.isfinite(value) or value != registered:
            raise ValueError(f"{name} must equal registered value {registered}")
    if not config.deterministic_algorithms:
        raise ValueError("Stage C requires deterministic algorithms")


def _configure_torch(torch, config: TemporalCTCConfig) -> None:
    torch.set_num_threads(config.num_threads)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass
    torch.use_deterministic_algorithms(True, warn_only=False)


def _checkpoint_payload_sha256(arrays: Mapping[str, Any]) -> str:
    digest = hashlib.sha256()
    for name in sorted(arrays):
        value = arrays[name]
        digest.update(name.encode("utf-8"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(json.dumps(list(value.shape), separators=(",", ":")).encode("ascii"))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _decode_metadata(value) -> dict[str, Any]:
    raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    if not isinstance(raw, str):
        raise ValueError("Stage C checkpoint metadata must be JSON text")
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise ValueError("Stage C checkpoint metadata must decode to an object")
    return decoded


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if value > 10_000_000 else value * 1024


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Stage C length utilities require NumPy: `pip install -e '.[array]'`."
        ) from exc
    return np


def _require_ml_dependencies():
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Stage C temporal CTC requires NumPy and Torch: `pip install -e '.[ml]'`."
        ) from exc
    return np, torch
