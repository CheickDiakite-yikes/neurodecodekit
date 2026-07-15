"""Exact bounded causal sentence CTC models for the shared S21 gate."""

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


MODEL_SCHEMA_NAME = "neurodecodekit.tiny_causal_sentence_ctc_checkpoint"
MODEL_SCHEMA_VERSION = 0
CANDIDATE_MODEL_ID = "TinyCausalSentenceCTC-v0"
LINEAR_MODEL_ID = "LinearSignalCTC-v0"


@dataclass(frozen=True)
class CausalSentenceCTCConfig:
    """Frozen optimizer, architecture, and determinism settings."""

    architecture: str = "candidate"
    input_channels: int = 102
    hidden_channels: int = 16
    classes: int = 28
    optimizer_steps: int = 240
    batch_size: int = 16
    learning_rate: float = 0.02
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    weight_decay: float = 0.0
    amsgrad: bool = False
    num_threads: int = 1
    deterministic_algorithms: bool = True
    seed: int = 2601

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def config_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class CausalSentenceCTCTrainingResult:
    """One exact fixed-step training result with no validation selection."""

    model: Any
    config: CausalSentenceCTCConfig
    loss_history: tuple[float, ...]
    optimizer_steps: int
    example_presentations: int
    completed_epochs: int
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


def registered_candidate_config(*, seed: int = 2601) -> CausalSentenceCTCConfig:
    return CausalSentenceCTCConfig(architecture="candidate", seed=int(seed))


def registered_linear_config(*, seed: int = 2601) -> CausalSentenceCTCConfig:
    return CausalSentenceCTCConfig(architecture="linear", seed=int(seed))


def build_causal_sentence_ctc(config: CausalSentenceCTCConfig):
    """Build the exact candidate or linear CPU architecture."""

    _np, torch = _require_ml_dependencies()
    _validate_config(config)

    if config.architecture == "candidate":

        class TinyCausalSentenceCTC(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.input_conv = torch.nn.Conv1d(
                    config.input_channels,
                    config.hidden_channels,
                    kernel_size=1,
                    bias=True,
                )
                self.hidden_conv = torch.nn.Conv1d(
                    config.hidden_channels,
                    config.hidden_channels,
                    kernel_size=3,
                    padding=0,
                    bias=True,
                )
                self.output_conv = torch.nn.Conv1d(
                    config.hidden_channels,
                    config.classes,
                    kernel_size=1,
                    bias=True,
                )
                self.activation = torch.nn.GELU(approximate="none")

            def forward(self, value):
                hidden = self.activation(self.input_conv(value))
                hidden = torch.nn.functional.pad(hidden, (2, 0), value=0.0)
                hidden = self.activation(self.hidden_conv(hidden))
                return self.output_conv(hidden).transpose(1, 2)

        model = TinyCausalSentenceCTC()
    else:

        class LinearSignalCTC(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.output_conv = torch.nn.Conv1d(
                    config.input_channels,
                    config.classes,
                    kernel_size=1,
                    bias=True,
                )

            def forward(self, value):
                return self.output_conv(value).transpose(1, 2)

        model = LinearSignalCTC()

    parameter_count = sum(int(value.numel()) for value in model.parameters())
    expected = 2908 if config.architecture == "candidate" else 2884
    if parameter_count != expected:
        raise RuntimeError(f"{config.architecture} parameter count {parameter_count} != {expected}")
    return model.to("cpu")


def train_causal_sentence_ctc(
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    config: CausalSentenceCTCConfig,
) -> CausalSentenceCTCTrainingResult:
    """Train one exact 240-step CPU fit and retain only the final state."""

    np, torch = _require_ml_dependencies()
    _validate_config(config)
    arrays = _validate_training_arrays(
        np,
        signals=signals,
        input_lengths=input_lengths,
        target_token_ids=target_token_ids,
        target_lengths=target_lengths,
        input_channels=config.input_channels,
    )
    _configure_torch(torch, config)
    torch.manual_seed(config.seed)
    model = build_causal_sentence_ctc(config)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=config.learning_rate,
        betas=(config.beta1, config.beta2),
        eps=config.epsilon,
        weight_decay=config.weight_decay,
        amsgrad=config.amsgrad,
        maximize=False,
    )
    criterion = torch.nn.CTCLoss(
        blank=0,
        reduction="mean",
        zero_infinity=False,
    )
    rng = np.random.default_rng(config.seed)
    started_at = time.perf_counter()
    losses: list[float] = []
    example_presentations = 0
    completed_epochs = 0
    order = np.empty(0, dtype="int64")
    cursor = 0
    model.train()
    for _step in range(config.optimizer_steps):
        if cursor >= len(order):
            order = rng.permutation(len(arrays["signals"])).astype("int64", copy=False)
            cursor = 0
            completed_epochs += 1
        batch_indices = order[cursor : cursor + config.batch_size]
        cursor += len(batch_indices)
        xb = torch.from_numpy(arrays["signals"][batch_indices])
        input_len = torch.from_numpy(arrays["input_lengths"][batch_indices])
        targets = torch.from_numpy(arrays["target_token_ids"][batch_indices])
        target_len = torch.from_numpy(arrays["target_lengths"][batch_indices])
        optimizer.zero_grad(set_to_none=True)
        logits = model(xb)
        if logits.shape[:2] != (len(batch_indices), arrays["signals"].shape[2]):
            raise RuntimeError("causal CTC output length does not equal input length")
        loss = criterion(logits.log_softmax(dim=2).permute(1, 0, 2), targets, input_len, target_len)
        if not bool(torch.isfinite(loss)):
            raise RuntimeError("causal sentence CTC produced non-finite loss")
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach().cpu()))
        example_presentations += int(len(batch_indices))
    model.eval()
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    return CausalSentenceCTCTrainingResult(
        model=model,
        config=config,
        loss_history=tuple(losses),
        optimizer_steps=len(losses),
        example_presentations=example_presentations,
        completed_epochs=completed_epochs,
        parameter_count=parameter_count,
        parameter_bytes_float32=parameter_count * 4,
        runtime_sec=round(time.perf_counter() - started_at, 6),
        peak_rss_bytes=_peak_rss_bytes(),
        torch_version=str(torch.__version__),
    )


def predict_causal_sentence_ctc(
    model,
    *,
    signals,
    input_lengths,
    batch_size: int = 16,
) -> dict[str, Any]:
    """Run target-blind greedy CTC inference on one frozen model."""

    np, torch = _require_ml_dependencies()
    values = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    if values.ndim != 3 or len(values) < 1:
        raise ValueError("signals must be nonempty [items, channels, time]")
    if lengths.shape != (len(values),):
        raise ValueError("input_lengths must match signal rows")
    if batch_size < 1 or batch_size > 16:
        raise ValueError("batch_size must be between 1 and 16")
    if (lengths < 1).any() or (lengths > values.shape[2]).any():
        raise ValueError("input_lengths fall outside padded signal width")
    predictions: list[str] = []
    blank_count = 0
    valid_steps = 0
    model.eval()
    started_at = time.perf_counter()
    with torch.no_grad():
        for start in range(0, len(values), batch_size):
            stop = min(len(values), start + batch_size)
            logits = model(torch.from_numpy(values[start:stop]))
            token_rows = logits.argmax(dim=2).cpu().numpy()
            for token_row, length in zip(token_rows, lengths[start:stop], strict=True):
                valid = token_row[: int(length)]
                predictions.append(greedy_decode_ctc_ids(valid))
                blank_count += int((valid == 0).sum())
                valid_steps += int(length)
    return {
        "predictions": predictions,
        "prediction_count": len(predictions),
        "blank_count": blank_count,
        "valid_steps": valid_steps,
        "blank_fraction": blank_count / valid_steps if valid_steps else 0.0,
        "runtime_sec": round(time.perf_counter() - started_at, 6),
        "peak_rss_bytes": _peak_rss_bytes(),
        "model_run_count": 1,
    }


def save_causal_sentence_ctc_checkpoint(
    path: str | Path,
    *,
    training: CausalSentenceCTCTrainingResult,
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    """Save numeric-only final-step weights and hash-bound metadata."""

    np, _torch = _require_ml_dependencies()
    output = Path(path)
    if output.exists():
        raise FileExistsError(f"Refusing to replace checkpoint: {output}")
    arrays = {
        name: value.detach().cpu().numpy().astype("float32", copy=True)
        for name, value in training.model.state_dict().items()
    }
    payload_hash = _checkpoint_payload_sha256(arrays)
    checkpoint_metadata = dict(metadata)
    checkpoint_metadata.update(
        {
            "schema": {"name": MODEL_SCHEMA_NAME, "version": MODEL_SCHEMA_VERSION},
            "model_id": (
                CANDIDATE_MODEL_ID
                if training.config.architecture == "candidate"
                else LINEAR_MODEL_ID
            ),
            "serialization": "numpy_npz_allow_pickle_false",
            "parameter_payload_sha256": payload_hash,
            "parameter_count": training.parameter_count,
            "parameter_bytes_float32": training.parameter_bytes_float32,
            "checkpoint_selection": "state_after_optimizer_step_240_only",
            "optimizer_steps": training.optimizer_steps,
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
        "parameter_payload_sha256": payload_hash,
        "metadata": checkpoint_metadata,
    }


def load_causal_sentence_ctc_checkpoint(path: str | Path):
    """Load a numeric checkpoint and rebuild the exact CPU model."""

    np, torch = _require_ml_dependencies()
    checkpoint = Path(path)
    with np.load(checkpoint, allow_pickle=False) as data:
        if "metadata" not in data.files:
            raise ValueError("causal sentence checkpoint lacks metadata")
        metadata = _decode_metadata(data["metadata"])
        arrays = {name: data[name].copy() for name in data.files if name != "metadata"}
    schema = metadata.get("schema") or {}
    if schema != {"name": MODEL_SCHEMA_NAME, "version": MODEL_SCHEMA_VERSION}:
        raise ValueError("unsupported causal sentence checkpoint schema")
    if metadata.get("serialization") != "numpy_npz_allow_pickle_false":
        raise ValueError("causal sentence checkpoint serialization is invalid")
    try:
        config = CausalSentenceCTCConfig(**metadata["config"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("causal sentence checkpoint config is invalid") from exc
    _validate_config(config)
    if metadata.get("config_sha256") != config.config_sha256:
        raise ValueError("causal sentence checkpoint config hash mismatch")
    if metadata.get("parameter_payload_sha256") != _checkpoint_payload_sha256(arrays):
        raise ValueError("causal sentence checkpoint payload hash mismatch")
    model = build_causal_sentence_ctc(config)
    expected = model.state_dict()
    if set(arrays) != set(expected):
        raise ValueError("causal sentence checkpoint parameter names are invalid")
    state = {}
    for name, expected_value in expected.items():
        if arrays[name].shape != tuple(expected_value.shape):
            raise ValueError(f"causal sentence checkpoint shape mismatch for {name}")
        if arrays[name].dtype != np.dtype("float32"):
            raise ValueError(f"causal sentence checkpoint dtype mismatch for {name}")
        state[name] = torch.from_numpy(arrays[name])
    model.load_state_dict(state, strict=True)
    model.eval()
    parameter_count = sum(int(value.numel()) for value in model.parameters())
    if metadata.get("parameter_count") != parameter_count:
        raise ValueError("causal sentence checkpoint parameter accounting mismatch")
    if metadata.get("optimizer_steps") != 240:
        raise ValueError("causal sentence checkpoint is not the registered final step")
    return model, metadata


def _validate_training_arrays(
    np,
    *,
    signals,
    input_lengths,
    target_token_ids,
    target_lengths,
    input_channels: int,
) -> dict[str, Any]:
    values = np.asarray(signals, dtype="float32")
    lengths = np.asarray(input_lengths, dtype="int64")
    target_ids = np.asarray(target_token_ids, dtype="int64")
    target_len = np.asarray(target_lengths, dtype="int64")
    if values.ndim != 3 or values.shape[0] < 1 or values.shape[1] != input_channels:
        raise ValueError(
            f"signals must be nonempty [items, {input_channels}, time], got {values.shape}"
        )
    if not np.isfinite(values).all():
        raise ValueError("signals contain non-finite values")
    if lengths.shape != (len(values),) or target_len.shape != (len(values),):
        raise ValueError("input_lengths and target_lengths must match signal rows")
    if target_ids.ndim != 2 or target_ids.shape[0] != len(values):
        raise ValueError("target_token_ids must be [items, max_target_length]")
    if (lengths < 1).any() or (lengths > values.shape[2]).any():
        raise ValueError("input_lengths fall outside the padded signal width")
    if (target_len < 1).any() or (target_len > target_ids.shape[1]).any():
        raise ValueError("target_lengths fall outside the padded target width")
    for row, length in zip(target_ids, target_len, strict=True):
        valid = row[: int(length)]
        if (valid <= 0).any() or (valid >= len(CTC_VOCAB)).any():
            raise ValueError("valid target IDs must exclude blank and stay in vocabulary")
        if (row[int(length) :] != 0).any():
            raise ValueError("target padding must use blank zero")
    return {
        "signals": np.ascontiguousarray(values),
        "input_lengths": np.ascontiguousarray(lengths),
        "target_token_ids": np.ascontiguousarray(target_ids),
        "target_lengths": np.ascontiguousarray(target_len),
    }


def _validate_config(config: CausalSentenceCTCConfig) -> None:
    if config.architecture not in {"candidate", "linear"}:
        raise ValueError("architecture must be candidate or linear")
    if (config.input_channels, config.hidden_channels, config.classes) != (102, 16, 28):
        raise ValueError("registered causal sentence geometry is fixed at 102/16/28")
    if config.optimizer_steps != 240:
        raise ValueError("registered fits require exactly 240 optimizer steps")
    if config.batch_size < 1 or config.batch_size > 16:
        raise ValueError("batch_size must be between 1 and 16")
    if config.num_threads != 1:
        raise ValueError("registered fits require exactly one CPU thread")
    if config.seed not in {2601, 2602, 2603}:
        raise ValueError("registered fits require seed 2601, 2602, or 2603")
    exact = {
        "learning_rate": (config.learning_rate, 0.02),
        "beta1": (config.beta1, 0.9),
        "beta2": (config.beta2, 0.999),
        "epsilon": (config.epsilon, 1e-8),
        "weight_decay": (config.weight_decay, 0.0),
    }
    for name, (value, expected) in exact.items():
        if not math.isfinite(value) or value != expected:
            raise ValueError(f"{name} must equal registered value {expected}")
    if config.amsgrad or not config.deterministic_algorithms:
        raise ValueError("AMSGrad must be false and deterministic algorithms true")


def _configure_torch(torch, config: CausalSentenceCTCConfig) -> None:
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
        raise ValueError("causal sentence checkpoint metadata must be JSON text")
    decoded = json.loads(raw)
    if not isinstance(decoded, dict):
        raise ValueError("causal sentence checkpoint metadata must decode to an object")
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


def _require_ml_dependencies():
    try:
        import numpy as np
        import torch
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Causal sentence CTC requires NumPy and Torch: `pip install -e '.[ml]'`."
        ) from exc
    return np, torch
