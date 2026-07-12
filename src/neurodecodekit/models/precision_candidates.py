"""Exact Loop 24 CPU precision candidates around the frozen tiny producer."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
import time
import warnings
from dataclasses import asdict, dataclass
from typing import Any

from neurodecodekit.models.tiny_causal_encoder import (
    CHECKPOINT_PARAMETER_NAMES,
    _build_model,
)


FLOAT32_REFERENCE = "float32_eager_reference"
FLOAT16_EAGER_CPU = "float16_eager_cpu"
DYNAMIC_QINT8_QNNPACK = "dynamic_qint8_qnnpack"
CANDIDATE_IDS = (
    FLOAT32_REFERENCE,
    FLOAT16_EAGER_CPU,
    DYNAMIC_QINT8_QNNPACK,
)
LINEAR_MODULE_NAMES = ("encoder_input", "encoder_output", "motif_probe")
REQUIRED_QINT8_OPERATOR = "quantized::linear_dynamic"
API_MIGRATION_WARNING = (
    "Legacy torch.ao eager quantization is version-bound and is migrating to torchao; "
    "this gate does not substitute torchao or another backend."
)
PAYLOAD_MAGIC = b"NEURODECODEKIT_LOOP24_NUMERIC_PAYLOAD_V0\n"


class CandidateUnavailableError(RuntimeError):
    """One registered candidate is unavailable and may not silently fall back."""

    def __init__(self, refusal_id: str, message: str) -> None:
        super().__init__(message)
        self.refusal_id = refusal_id


@dataclass(frozen=True)
class PrecisionCandidateProvenance:
    """Inspectable conversion identity without exposing numeric weights."""

    candidate_id: str
    status: str
    device: str
    framework: str
    normalization_dtype: str
    module_input_dtype: str
    module_output_dtype: str
    decoder_cast: str
    module_classes: dict[str, str]
    weight_dtypes: dict[str, str]
    bias_dtypes: dict[str, str]
    quantized_engine: str | None
    packed_weight_scheme: dict[str, dict[str, object]]
    fallback_used: bool
    autocast_used: bool
    compile_used: bool
    architecture_changed: bool
    training_runs: int
    parameter_updates: int
    conversion_runtime_sec: float
    warnings: tuple[str, ...]
    unavailable_fields: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["warnings"] = list(self.warnings)
        value["unavailable_fields"] = list(self.unavailable_fields)
        return value


@dataclass(frozen=True)
class FrozenProducerPayload:
    """Small in-memory float32 source state used by isolated timing workers."""

    parameter_arrays: dict[str, Any]
    normalization_mean: Any
    normalization_std: Any
    n_channels: int
    source_sampling_rate_hz: float
    embedding_dim: int
    kernel_size: int
    stride: int
    n_classes: int
    hidden_dim: int
    logical_parameter_count: int
    parameter_payload_sha256: str


class PrecisionCandidateProducer:
    """Producer-compatible wrapper with explicit normalization and compute dtype."""

    def __init__(
        self,
        *,
        torch,
        model,
        normalization_mean,
        normalization_std,
        candidate_id: str,
        compute_dtype,
        n_channels: int,
        source_sampling_rate_hz: float,
        embedding_dim: int,
        kernel_size: int,
        stride: int,
        n_classes: int,
        logical_parameter_count: int,
        provenance: PrecisionCandidateProvenance,
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
        self.candidate_id = candidate_id
        self.compute_dtype = compute_dtype
        self.n_channels = int(n_channels)
        self.source_sampling_rate_hz = float(source_sampling_rate_hz)
        self.embedding_dim = int(embedding_dim)
        self.kernel_size = int(kernel_size)
        self.stride = int(stride)
        self.n_classes = int(n_classes)
        self.logical_parameter_count = int(logical_parameter_count)
        self.provenance = provenance
        self.token_dtype = "float32"
        self.model.eval()
        _validate_candidate_geometry(self)

    @property
    def mutable_state_bound_bytes(self) -> int:
        return self.n_channels * max(0, self.kernel_size - 1) * 4

    @property
    def producer_right_context_samples(self) -> int:
        return 0

    def project_frame(self, frame):
        """Normalize in float32, then run the exact candidate encoder path."""

        np = _require_numpy()
        value = np.asarray(frame, dtype="float32")
        expected = self.n_channels * self.kernel_size
        if value.shape != (expected,):
            raise ValueError(f"frame must be flattened with {expected} values")
        if not np.isfinite(value).all():
            raise ValueError("candidate frame contains non-finite values")
        matrix = value.reshape(self.n_channels, self.kernel_size)
        normalized = (
            (matrix - self.normalization_mean[:, None])
            / self.normalization_std[:, None]
        ).reshape(1, -1)
        tensor = self.torch.from_numpy(normalized)
        if self.candidate_id == FLOAT16_EAGER_CPU:
            tensor = tensor.to(dtype=self.compute_dtype)
        with self.torch.inference_mode():
            embedding = self.model.encode(tensor)
        return embedding.detach().cpu().to(dtype=self.torch.float32).numpy().copy()

    def probe_embedding(self, embedding):
        """Run the exact candidate probe and return float32 for the decoder cast."""

        np = _require_numpy()
        value = np.asarray(embedding, dtype="float32")
        if value.shape != (self.embedding_dim,):
            raise ValueError("embedding has the wrong shape for the candidate probe")
        if not np.isfinite(value).all():
            raise ValueError("candidate embedding contains non-finite values")
        tensor = self.torch.from_numpy(value[None, :])
        if self.candidate_id == FLOAT16_EAGER_CPU:
            tensor = tensor.to(dtype=self.compute_dtype)
        with self.torch.inference_mode():
            logits = self.model.probe(tensor)
        return logits.detach().cpu().to(dtype=self.torch.float32).numpy().copy()

    def run_frame(self, frame) -> tuple[Any, Any]:
        embedding = self.project_frame(frame)[0]
        logits = self.probe_embedding(embedding)[0]
        return embedding, logits


def extract_frozen_producer_payload(producer) -> FrozenProducerPayload:
    """Copy the already loaded source state without reopening its checkpoint."""

    np = _require_numpy()
    state = producer.model.state_dict()
    arrays = {
        name: state[name].detach().cpu().numpy().astype("float32", copy=True)
        for name in CHECKPOINT_PARAMETER_NAMES
    }
    hidden_dim = int(arrays["encoder_input.weight"].shape[0])
    logical_count = sum(int(value.size) for value in arrays.values())
    if logical_count != int(producer.trainable_parameter_count):
        raise ValueError("frozen producer parameter accounting drifted")
    return FrozenProducerPayload(
        parameter_arrays=arrays,
        normalization_mean=np.asarray(
            producer.normalization_mean, dtype="float32"
        ).copy(),
        normalization_std=np.asarray(
            producer.normalization_std, dtype="float32"
        ).copy(),
        n_channels=int(producer.n_channels),
        source_sampling_rate_hz=float(producer.source_sampling_rate_hz),
        embedding_dim=int(producer.embedding_dim),
        kernel_size=int(producer.kernel_size),
        stride=int(producer.stride),
        n_classes=int(producer.n_classes),
        hidden_dim=hidden_dim,
        logical_parameter_count=logical_count,
        parameter_payload_sha256=str(producer.parameter_payload_sha256),
    )


def build_precision_candidate_from_payload(
    payload: FrozenProducerPayload,
    candidate_id: str,
) -> PrecisionCandidateProducer:
    """Materialize one candidate in an isolated worker without checkpoint I/O."""

    np, torch = _require_ml_dependencies()
    model = _build_model(
        torch,
        input_dim=payload.n_channels * payload.kernel_size,
        hidden_dim=payload.hidden_dim,
        embedding_dim=payload.embedding_dim,
        n_classes=payload.n_classes,
    ).to("cpu")
    model.load_state_dict(
        {
            name: torch.from_numpy(np.asarray(value, dtype="float32"))
            for name, value in payload.parameter_arrays.items()
        },
        strict=True,
    )
    model.eval()
    source = _ProducerView(
        torch=torch,
        model=model,
        normalization_mean=payload.normalization_mean,
        normalization_std=payload.normalization_std,
        n_channels=payload.n_channels,
        source_sampling_rate_hz=payload.source_sampling_rate_hz,
        embedding_dim=payload.embedding_dim,
        kernel_size=payload.kernel_size,
        stride=payload.stride,
        n_classes=payload.n_classes,
        trainable_parameter_count=payload.logical_parameter_count,
    )
    return build_precision_candidate(source, candidate_id)


def build_precision_candidate(producer, candidate_id: str) -> PrecisionCandidateProducer:
    """Clone and validate one exact registered candidate with no fallback."""

    if candidate_id not in CANDIDATE_IDS:
        raise ValueError(f"unknown Loop 24 candidate: {candidate_id}")
    np, torch = _require_ml_dependencies()
    _configure_single_thread_torch(torch)
    _validate_source_producer(producer)
    started_at = time.perf_counter()
    model = copy.deepcopy(producer.model).to("cpu").eval()
    captured_warnings: list[str] = []
    quantized_engine: str | None = None
    compute_dtype = torch.float32

    if candidate_id == FLOAT32_REFERENCE:
        model = model.to(dtype=torch.float32)
        framework = "torch_eager"
        module_input_dtype = "float32"
        module_output_dtype = "float32"
        decoder_cast = "float32_to_float64_once"
    elif candidate_id == FLOAT16_EAGER_CPU:
        model = model.to(dtype=torch.float16)
        compute_dtype = torch.float16
        framework = "torch_eager"
        module_input_dtype = "float16_after_float32_normalization"
        module_output_dtype = "float16_then_float32_once"
        decoder_cast = "float32_to_float64_once"
    else:
        engines = tuple(str(value) for value in torch.backends.quantized.supported_engines)
        if "qnnpack" not in engines:
            raise CandidateUnavailableError(
                "dynamic_int8_qnnpack_unavailable",
                "QNNPACK is unavailable; no alternate backend or fallback is allowed",
            )
        quantize_dynamic = getattr(
            getattr(torch, "ao", None), "quantization", None
        )
        quantize_dynamic = getattr(quantize_dynamic, "quantize_dynamic", None)
        if quantize_dynamic is None:
            raise CandidateUnavailableError(
                "dynamic_int8_qnnpack_unavailable",
                "legacy torch.ao dynamic quantization API is unavailable",
            )
        torch.backends.quantized.engine = "qnnpack"
        quantized_engine = str(torch.backends.quantized.engine)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                model = quantize_dynamic(
                    model,
                    qconfig_spec={torch.nn.Linear},
                    dtype=torch.qint8,
                    inplace=False,
                )
            except Exception as exc:  # noqa: BLE001 - backend availability varies
                raise CandidateUnavailableError(
                    "dynamic_int8_qnnpack_unavailable",
                    f"QNNPACK dynamic conversion failed: {exc}",
                ) from exc
        captured_warnings.extend(_sanitize_warning(str(row.message)) for row in caught)
        captured_warnings.append(API_MIGRATION_WARNING)
        framework = "torch_ao_legacy_eager_dynamic_quantization"
        module_input_dtype = "float32_dynamic_activation_quantization"
        module_output_dtype = "float32"
        decoder_cast = "float32_to_float64_once"

    module_classes, weight_dtypes, bias_dtypes, packed = _module_provenance(
        torch,
        model,
        candidate_id=candidate_id,
    )
    unavailable_fields = (
        ("hardware_accumulation_dtype",)
        if candidate_id == FLOAT16_EAGER_CPU
        else ()
    )
    provenance = PrecisionCandidateProvenance(
        candidate_id=candidate_id,
        status="available",
        device="cpu",
        framework=framework,
        normalization_dtype="float32",
        module_input_dtype=module_input_dtype,
        module_output_dtype=module_output_dtype,
        decoder_cast=decoder_cast,
        module_classes=module_classes,
        weight_dtypes=weight_dtypes,
        bias_dtypes=bias_dtypes,
        quantized_engine=quantized_engine,
        packed_weight_scheme=packed,
        fallback_used=False,
        autocast_used=False,
        compile_used=False,
        architecture_changed=False,
        training_runs=0,
        parameter_updates=0,
        conversion_runtime_sec=round(time.perf_counter() - started_at, 9),
        warnings=tuple(dict.fromkeys(captured_warnings)),
        unavailable_fields=unavailable_fields,
    )
    candidate = PrecisionCandidateProducer(
        torch=torch,
        model=model,
        normalization_mean=np.asarray(producer.normalization_mean, dtype="float32"),
        normalization_std=np.asarray(producer.normalization_std, dtype="float32"),
        candidate_id=candidate_id,
        compute_dtype=compute_dtype,
        n_channels=int(producer.n_channels),
        source_sampling_rate_hz=float(producer.source_sampling_rate_hz),
        embedding_dim=int(producer.embedding_dim),
        kernel_size=int(producer.kernel_size),
        stride=int(producer.stride),
        n_classes=int(producer.n_classes),
        logical_parameter_count=int(producer.trainable_parameter_count),
        provenance=provenance,
    )
    _validate_runtime_dtypes(candidate)
    return candidate


def candidate_storage_summary(candidate: PrecisionCandidateProducer) -> dict[str, Any]:
    """Return deterministic numeric payload accounting without exposing values."""

    arrays = candidate_numeric_arrays(candidate)
    payload = serialize_candidate_numeric_payload(candidate)
    raw_by_dtype: dict[str, int] = {}
    for value in arrays.values():
        dtype = str(value.dtype)
        raw_by_dtype[dtype] = raw_by_dtype.get(dtype, 0) + int(value.nbytes)
    return {
        "logical_parameter_count": candidate.logical_parameter_count,
        "raw_tensor_payload_bytes_by_dtype": dict(sorted(raw_by_dtype.items())),
        "raw_tensor_payload_bytes_total": sum(raw_by_dtype.values()),
        "deterministic_serialized_numeric_payload_bytes": len(payload),
        "deterministic_serialized_numeric_payload_sha256": hashlib.sha256(
            payload
        ).hexdigest(),
        "serialized_numeric_payload_is_deployable_package": False,
        "mutable_encoder_state_bytes": candidate.mutable_state_bound_bytes,
    }


def candidate_numeric_arrays(candidate: PrecisionCandidateProducer) -> dict[str, Any]:
    """Extract canonical numeric arrays for storage accounting only."""

    np = _require_numpy()
    arrays: dict[str, Any] = {
        "normalization_mean": np.asarray(candidate.normalization_mean, dtype="float32"),
        "normalization_std": np.asarray(candidate.normalization_std, dtype="float32"),
    }
    if candidate.candidate_id != DYNAMIC_QINT8_QNNPACK:
        state = candidate.model.state_dict()
        for name in CHECKPOINT_PARAMETER_NAMES:
            arrays[name] = state[name].detach().cpu().numpy().copy()
        return arrays
    for module_name in LINEAR_MODULE_NAMES:
        module = getattr(candidate.model, module_name)
        weight = module.weight()
        arrays[f"{module_name}.weight.int_repr"] = (
            weight.int_repr().detach().cpu().numpy().copy()
        )
        qscheme = str(weight.qscheme())
        if "per_channel" in qscheme:
            arrays[f"{module_name}.weight.scales"] = (
                weight.q_per_channel_scales().detach().cpu().numpy().astype("float64")
            )
            arrays[f"{module_name}.weight.zero_points"] = (
                weight.q_per_channel_zero_points()
                .detach()
                .cpu()
                .numpy()
                .astype("int64")
            )
            arrays[f"{module_name}.weight.axis"] = np.asarray(
                [weight.q_per_channel_axis()], dtype="int64"
            )
        else:
            arrays[f"{module_name}.weight.scale"] = np.asarray(
                [weight.q_scale()], dtype="float64"
            )
            arrays[f"{module_name}.weight.zero_point"] = np.asarray(
                [weight.q_zero_point()], dtype="int64"
            )
        bias = module.bias()
        arrays[f"{module_name}.bias"] = (
            bias.detach().cpu().numpy().astype("float32", copy=True)
        )
    return arrays


def serialize_candidate_numeric_payload(candidate: PrecisionCandidateProducer) -> bytes:
    """Serialize sorted arrays with explicit dtype/shape headers and no pickle."""

    np = _require_numpy()
    output = bytearray(PAYLOAD_MAGIC)
    for name, raw_value in sorted(candidate_numeric_arrays(candidate).items()):
        value = np.ascontiguousarray(raw_value)
        header = json.dumps(
            {
                "bytes": int(value.nbytes),
                "dtype": str(value.dtype),
                "name": name,
                "shape": [int(item) for item in value.shape],
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        output.extend(len(header).to_bytes(4, "big"))
        output.extend(header)
        output.extend(value.tobytes(order="C"))
    return bytes(output)


def profile_candidate_operator(
    candidate: PrecisionCandidateProducer,
    frame,
) -> dict[str, Any]:
    """Run one untimed CPU trace and retain only aggregate operator names."""

    if candidate.candidate_id != DYNAMIC_QINT8_QNNPACK:
        return {
            "required": False,
            "passed": True,
            "required_operator_contains": None,
            "operator_names": [],
            "raw_trace_saved": False,
        }
    torch = candidate.torch
    profiler = getattr(torch, "profiler", None)
    if profiler is None:
        raise CandidateUnavailableError(
            "dynamic_int8_profiler_operator_unproven",
            "torch CPU profiler is unavailable for QNNPACK provenance",
        )
    try:
        with profiler.profile(activities=[profiler.ProfilerActivity.CPU]) as trace:
            candidate.run_frame(frame)
    except Exception as exc:  # noqa: BLE001 - backend profiler varies
        raise CandidateUnavailableError(
            "dynamic_int8_profiler_operator_unproven",
            f"QNNPACK profiler provenance failed: {exc}",
        ) from exc
    operator_names = sorted({str(event.key) for event in trace.key_averages()})
    passed = any(REQUIRED_QINT8_OPERATOR in name for name in operator_names)
    if not passed:
        raise CandidateUnavailableError(
            "dynamic_int8_profiler_operator_unproven",
            "QNNPACK candidate did not expose quantized::linear_dynamic",
        )
    return {
        "required": True,
        "passed": True,
        "required_operator_contains": REQUIRED_QINT8_OPERATOR,
        "operator_names": operator_names,
        "raw_trace_saved": False,
    }


@dataclass
class _ProducerView:
    torch: Any
    model: Any
    normalization_mean: Any
    normalization_std: Any
    n_channels: int
    source_sampling_rate_hz: float
    embedding_dim: int
    kernel_size: int
    stride: int
    n_classes: int
    trainable_parameter_count: int


def _module_provenance(torch, model, *, candidate_id: str):
    module_classes: dict[str, str] = {}
    weight_dtypes: dict[str, str] = {}
    bias_dtypes: dict[str, str] = {}
    packed: dict[str, dict[str, object]] = {}
    expected_quantized = getattr(
        getattr(getattr(torch, "ao", None), "nn", None), "quantized", None
    )
    expected_quantized = getattr(expected_quantized, "dynamic", None)
    expected_quantized = getattr(expected_quantized, "Linear", None)
    for name in LINEAR_MODULE_NAMES:
        module = getattr(model, name, None)
        if module is None:
            raise CandidateUnavailableError(
                "candidate_dtype_or_module_contract_mismatch",
                f"candidate is missing registered Linear module {name}",
            )
        module_classes[name] = f"{type(module).__module__}.{type(module).__qualname__}"
        if candidate_id == DYNAMIC_QINT8_QNNPACK:
            if expected_quantized is None or not isinstance(module, expected_quantized):
                raise CandidateUnavailableError(
                    "candidate_dtype_or_module_contract_mismatch",
                    f"{name} is not torch.ao.nn.quantized.dynamic.Linear",
                )
            weight = module.weight()
            bias = module.bias()
            if weight.dtype != torch.qint8:
                raise CandidateUnavailableError(
                    "candidate_dtype_or_module_contract_mismatch",
                    f"{name} packed weight is not qint8",
                )
            weight_dtypes[name] = str(weight.dtype).replace("torch.", "")
            bias_dtypes[name] = str(bias.dtype).replace("torch.", "")
            scheme: dict[str, object] = {"qscheme": str(weight.qscheme())}
            if "per_channel" in str(weight.qscheme()):
                scheme.update(
                    {
                        "axis": int(weight.q_per_channel_axis()),
                        "scales": int(weight.q_per_channel_scales().numel()),
                        "zero_points": int(weight.q_per_channel_zero_points().numel()),
                    }
                )
            else:
                scheme.update(
                    {
                        "scale": float(weight.q_scale()),
                        "zero_point": int(weight.q_zero_point()),
                    }
                )
            packed[name] = scheme
        else:
            if not isinstance(module, torch.nn.Linear):
                raise CandidateUnavailableError(
                    "candidate_dtype_or_module_contract_mismatch",
                    f"{name} is not torch.nn.Linear",
                )
            weight_dtypes[name] = str(module.weight.dtype).replace("torch.", "")
            bias_dtypes[name] = str(module.bias.dtype).replace("torch.", "")
    return module_classes, weight_dtypes, bias_dtypes, packed


def _validate_source_producer(producer) -> None:
    np = _require_numpy()
    required = (
        "model",
        "normalization_mean",
        "normalization_std",
        "n_channels",
        "source_sampling_rate_hz",
        "embedding_dim",
        "kernel_size",
        "stride",
        "n_classes",
        "trainable_parameter_count",
    )
    missing = [name for name in required if not hasattr(producer, name)]
    if missing:
        raise ValueError(f"frozen producer is missing fields: {missing}")
    mean = np.asarray(producer.normalization_mean)
    std = np.asarray(producer.normalization_std)
    if mean.dtype != np.dtype("float32") or std.dtype != np.dtype("float32"):
        raise ValueError("frozen normalization must remain float32")
    if mean.shape != (int(producer.n_channels),) or std.shape != mean.shape:
        raise ValueError("frozen normalization shape is invalid")
    if not np.isfinite(mean).all() or not np.isfinite(std).all() or (std <= 0).any():
        raise ValueError("frozen normalization values are invalid")
    if int(producer.trainable_parameter_count) < 1:
        raise ValueError("frozen producer parameter count is invalid")


def _validate_runtime_dtypes(candidate: PrecisionCandidateProducer) -> None:
    torch = candidate.torch
    expected = {
        FLOAT32_REFERENCE: "float32",
        FLOAT16_EAGER_CPU: "float16",
        DYNAMIC_QINT8_QNNPACK: "qint8",
    }[candidate.candidate_id]
    if any(value != expected for value in candidate.provenance.weight_dtypes.values()):
        raise CandidateUnavailableError(
            "candidate_silent_float32_or_backend_fallback",
            f"candidate weights do not all use registered {expected}",
        )
    if candidate.candidate_id == FLOAT16_EAGER_CPU:
        if any(
            parameter.device.type != "cpu" or parameter.dtype != torch.float16
            for parameter in candidate.model.parameters()
        ):
            raise CandidateUnavailableError(
                "candidate_silent_float32_or_backend_fallback",
                "float16 candidate silently changed device or dtype",
            )
    if candidate.candidate_id == DYNAMIC_QINT8_QNNPACK:
        if str(torch.backends.quantized.engine) != "qnnpack":
            raise CandidateUnavailableError(
                "candidate_silent_float32_or_backend_fallback",
                "dynamic qint8 candidate did not retain QNNPACK",
            )


def _validate_candidate_geometry(candidate: PrecisionCandidateProducer) -> None:
    if (
        candidate.n_channels < 1
        or candidate.embedding_dim < 1
        or candidate.kernel_size < 1
        or candidate.stride < 1
        or candidate.stride > candidate.kernel_size
        or candidate.n_classes < 2
        or not math.isfinite(candidate.source_sampling_rate_hz)
        or candidate.source_sampling_rate_hz <= 0
    ):
        raise ValueError("precision candidate geometry is invalid")
    if candidate.normalization_mean.shape != (candidate.n_channels,):
        raise ValueError("precision candidate normalization mean shape is invalid")
    if candidate.normalization_std.shape != (candidate.n_channels,):
        raise ValueError("precision candidate normalization std shape is invalid")


def _configure_single_thread_torch(torch) -> None:
    torch.set_num_threads(1)
    if hasattr(torch, "set_num_interop_threads"):
        try:
            torch.set_num_interop_threads(1)
        except RuntimeError:
            pass


def _sanitize_warning(value: str) -> str:
    """Keep the warning meaning while removing build-machine absolute paths."""

    return re.sub(r"\s*\(Triggered internally at [^)]*\)", "", value).strip()


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Loop 24 precision candidates require NumPy") from exc
    return np


def _require_ml_dependencies():
    np = _require_numpy()
    try:
        import torch
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Loop 24 precision candidates require PyTorch: `pip install -e '.[ml]'`."
        ) from exc
    return np, torch
