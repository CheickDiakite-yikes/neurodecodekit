"""Exact synthetic Causal Motor Lattice v0 architecture.

NumPy and PyTorch remain lazy optional dependencies. The module-level import is
therefore safe in the zero-dependency base package.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


CONTRACT_RELATIVE_PATH = Path(
    "registries/causal_motor_lattice_synthetic_contract.v0.json"
)
REGISTERED_CONTRACT_SHA256 = (
    "4880c322d48611ed098182fe845e891150e8e53551c95c25c33a4914c7db0fd4"
)
REGISTERED_CONTRACT_BYTES = 27_658
MAX_CONTRACT_BYTES = 1024 * 1024
ML_INSTALL_HINT = "pip install -e '.[ml]'"
NEURO_INSTALL_HINT = "pip install -e '.[neuro]'"

INPUT_CHANNELS = 64
SOURCE_CHANNELS = 8
SPATIAL_RANK = 8
VIEW_COUNT = 3
TEMPORAL_CELLS = ((0, 21), (21, 42), (42, 64))
CONTEXT_SAMPLES = 32
ANALYSIS_SAMPLES = 64
CROP_SAMPLES = CONTEXT_SAMPLES + ANALYSIS_SAMPLES
BOTTLENECK_FEATURES = 24
PRIMITIVE_COUNT = 18
KEY_COUNT = 29
RESIDUAL_GAIN = 0.25
EXPECTED_PARAMETER_COUNT = 4_535
VIEW_NAMES = ("potential", "mu", "beta")


def load_registered_cml_synthetic_contract(
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate the exact frozen work-order-13 contract."""

    source = Path(path) if path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    with source.open("rb") as handle:
        payload = handle.read(MAX_CONTRACT_BYTES + 1)
    if len(payload) > MAX_CONTRACT_BYTES:
        raise ValueError("CML-v0 synthetic contract exceeds 1 MiB")
    if len(payload) != REGISTERED_CONTRACT_BYTES:
        raise ValueError("CML-v0 synthetic contract byte count mismatch")
    if hashlib.sha256(payload).hexdigest() != REGISTERED_CONTRACT_SHA256:
        raise ValueError("CML-v0 synthetic contract SHA-256 mismatch")
    contract = json.loads(payload.decode("utf-8"))
    if contract.get("schema_name") != (
        "neurodecodekit.causal_motor_lattice_synthetic_contract"
    ):
        raise ValueError("CML-v0 synthetic contract schema mismatch")
    if contract.get("schema_version") != "0.1.0":
        raise ValueError("CML-v0 synthetic contract version mismatch")
    if contract.get("status") != (
        "preregistered_tier_B_synthetic_only_not_implemented_not_executed"
    ):
        raise ValueError("CML-v0 synthetic contract status mismatch")
    _validate_contract_identity(contract)
    return contract


def build_synthetic_projection(
    *, contract: Mapping[str, Any] | None = None
) -> Any:
    """Build the exact target-free 64-by-8 float32 source projection."""

    np = _require_numpy()
    registered = dict(contract) if contract is not None else load_registered_cml_synthetic_contract()
    matrix64 = np.zeros((INPUT_CHANNELS, SOURCE_CHANNELS), dtype="float64")
    for output_index in range(INPUT_CHANNELS):
        group = output_index // SOURCE_CHANNELS
        base = output_index % SOURCE_CHANNELS
        matrix64[output_index, base] = 1.0
        matrix64[output_index, (base + 1) % SOURCE_CHANNELS] = (
            0.05 if group % 2 == 0 else -0.05
        )
        matrix64[output_index, (base + 4) % SOURCE_CHANNELS] = 0.01 * (group - 3.5)
        matrix64[output_index] /= np.linalg.norm(matrix64[output_index])
    matrix = matrix64.astype("float32")
    expected = registered["synthetic_projection"]
    _validate_array_bytes(
        matrix,
        dtype="<f4",
        expected_bytes=int(expected["matrix_bytes"]),
        expected_sha256=str(expected["matrix_sha256"]),
        name="CML-v0 synthetic projection",
    )
    if int(np.linalg.matrix_rank(matrix)) != int(expected["matrix_rank"]):
        raise ValueError("CML-v0 synthetic projection rank mismatch")
    return matrix


def build_lattice_incidence(
    *, contract: Mapping[str, Any] | None = None
) -> Any:
    """Build the exact fixed 29-key by 18-primitive incidence matrix."""

    np = _require_numpy()
    registered = dict(contract) if contract is not None else load_registered_cml_synthetic_contract()
    incidence = np.zeros((KEY_COUNT, PRIMITIVE_COUNT), dtype="uint8")
    for key_index in range(KEY_COUNT):
        if key_index == KEY_COUNT - 1:
            incidence[key_index, 17] = 1
            continue
        local = key_index % 14
        hand = 0 if key_index < 14 else 1
        incidence[key_index, hand] = 1
        incidence[key_index, 2 + local % 4] = 1
        incidence[key_index, 6 + (local // 4) % 4] = 1
        incidence[key_index, 10 + local % 7] = 1
    expected = registered["synthetic_lattice"]
    _validate_array_bytes(
        incidence,
        dtype="uint8",
        expected_bytes=int(expected["incidence_bytes"]),
        expected_sha256=str(expected["incidence_sha256"]),
        name="CML-v0 lattice incidence",
    )
    return incidence


def build_causal_filter_coefficients(
    *, contract: Mapping[str, Any] | None = None
) -> dict[str, Any]:
    """Load and byte-validate the two exact one-sided FIR filters."""

    np = _require_numpy()
    registered = dict(contract) if contract is not None else load_registered_cml_synthetic_contract()
    filters: dict[str, Any] = {}
    for name in ("mu", "beta"):
        specification = registered["causal_filter_bank"][name]
        coefficients = np.asarray(specification["coefficients_float64"], dtype="<f8")
        _validate_array_bytes(
            coefficients,
            dtype="<f8",
            expected_bytes=33 * 8,
            expected_sha256=str(specification["little_endian_float64_sha256"]),
            name=f"CML-v0 {name} FIR",
        )
        filters[name] = coefficients
    return filters


def build_causal_motor_lattice_model(
    *, contract: Mapping[str, Any] | None = None
) -> Any:
    """Create the exact 4,535-parameter CPU-compatible CML-v0 module."""

    torch, nn, functional = _require_torch()
    registered = dict(contract) if contract is not None else load_registered_cml_synthetic_contract()
    filters = build_causal_filter_coefficients(contract=registered)
    incidence = build_lattice_incidence(contract=registered)

    class CausalMotorLatticeV0(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.potential_spatial = nn.Linear(INPUT_CHANNELS, SPATIAL_RANK, bias=True)
            self.mu_spatial = nn.Linear(INPUT_CHANNELS, SPATIAL_RANK, bias=True)
            self.beta_spatial = nn.Linear(INPUT_CHANNELS, SPATIAL_RANK, bias=True)
            self.bottleneck = nn.Linear(72, BOTTLENECK_FEATURES, bias=True)
            self.layer_norm = nn.LayerNorm(BOTTLENECK_FEATURES)
            self.primitive_head = nn.Linear(
                BOTTLENECK_FEATURES,
                PRIMITIVE_COUNT,
                bias=True,
            )
            self.key_residual_head = nn.Linear(
                BOTTLENECK_FEATURES,
                KEY_COUNT,
                bias=True,
            )
            self.register_buffer(
                "mu_fir",
                torch.as_tensor(filters["mu"], dtype=torch.float32),
            )
            self.register_buffer(
                "beta_fir",
                torch.as_tensor(filters["beta"], dtype=torch.float32),
            )
            incidence_tensor = torch.as_tensor(incidence, dtype=torch.float32)
            incidence_count = incidence_tensor.sum(dim=1, keepdim=True).clamp_min(1.0)
            self.register_buffer("lattice_incidence", incidence_tensor)
            self.register_buffer(
                "lattice_average",
                incidence_tensor / incidence_count,
            )

        @staticmethod
        def _normalized_weight(layer: Any) -> Any:
            centered = layer.weight - layer.weight.mean(dim=1, keepdim=True)
            norm = centered.square().sum(dim=1, keepdim=True).sqrt().clamp_min(1e-8)
            return centered / norm

        def _spatial_mix(self, layer: Any, signal: Any, valid_mask: Any) -> Any:
            weight = self._normalized_weight(layer)
            mixed = torch.einsum("oc,bct->bot", weight, signal)
            mixed = mixed + layer.bias[None, :, None]
            return mixed * valid_mask[:, None, :].to(dtype=mixed.dtype)

        @staticmethod
        def _cell_features(values: Any, valid_mask: Any, *, energy: bool) -> Any:
            features = []
            source = values.square() if energy else values
            for start, stop in TEMPORAL_CELLS:
                cell_mask = valid_mask[:, start:stop].to(dtype=source.dtype)
                count = cell_mask.sum(dim=1, keepdim=True)
                numerator = (source[:, :, start:stop] * cell_mask[:, None, :]).sum(dim=2)
                feature = numerator / count.clamp_min(1.0)
                feature = feature * (count > 0).to(dtype=feature.dtype)
                if energy:
                    feature = torch.log1p(feature)
                features.append(feature)
            return torch.stack(features, dim=2).reshape(values.shape[0], -1)

        def extract_views(self, signal: Any, valid_mask: Any) -> dict[str, Any]:
            if signal.ndim != 3 or tuple(signal.shape[1:]) != (
                INPUT_CHANNELS,
                CROP_SAMPLES,
            ):
                raise ValueError("CML-v0 signal shape must be [items, 64, 96]")
            if valid_mask.shape != (signal.shape[0], CROP_SAMPLES):
                raise ValueError("CML-v0 valid-mask shape mismatch")
            finite = torch.isfinite(signal)
            if not bool(finite.all().item()):
                raise ValueError("CML-v0 signal contains nonfinite values")
            mask = valid_mask.to(dtype=torch.bool)
            masked_signal = signal * mask[:, None, :].to(dtype=signal.dtype)

            analysis_mask = mask[:, CONTEXT_SAMPLES:]
            potential_values = self._spatial_mix(
                self.potential_spatial,
                masked_signal[:, :, CONTEXT_SAMPLES:],
                analysis_mask,
            )
            potential = self._cell_features(
                potential_values,
                analysis_mask,
                energy=False,
            )

            mask_count = functional.conv1d(
                mask[:, None, :].to(dtype=signal.dtype),
                torch.ones((1, 1, 33), dtype=signal.dtype, device=signal.device),
            )
            filtered_mask = mask_count[:, 0, :] >= 32.5
            views = {"potential": potential}
            for name, coefficients, layer in (
                ("mu", self.mu_fir, self.mu_spatial),
                ("beta", self.beta_fir, self.beta_spatial),
            ):
                kernel = coefficients.flip(0).reshape(1, 1, 33).repeat(INPUT_CHANNELS, 1, 1)
                filtered = functional.conv1d(
                    masked_signal,
                    kernel,
                    groups=INPUT_CHANNELS,
                )
                mixed = self._spatial_mix(layer, filtered, filtered_mask)
                views[name] = self._cell_features(mixed, filtered_mask, energy=True)
            return views

        def forward_from_views(
            self,
            views: Mapping[str, Any],
            *,
            muted_views: tuple[str, ...] = (),
        ) -> dict[str, Any]:
            unknown = set(muted_views) - set(VIEW_NAMES)
            if unknown:
                raise ValueError(f"unknown CML-v0 muted view(s): {sorted(unknown)}")
            ordered = [
                torch.zeros_like(views[name]) if name in muted_views else views[name]
                for name in VIEW_NAMES
            ]
            fused = torch.cat(ordered, dim=1)
            bottleneck = torch.tanh(self.layer_norm(self.bottleneck(fused)))
            primitive_logits = self.primitive_head(bottleneck)
            residual_logits = self.key_residual_head(bottleneck)
            lattice_logits = primitive_logits @ self.lattice_average.transpose(0, 1)
            bounded_residual = RESIDUAL_GAIN * torch.tanh(residual_logits)
            key_logits = lattice_logits + bounded_residual
            key_probabilities = torch.softmax(key_logits, dim=1)
            left = key_probabilities[:, :14].sum(dim=1)
            right = key_probabilities[:, 14:28].sum(dim=1)
            eligible_mass = (left + right).clamp_min(1e-12)
            hand_probabilities = torch.stack(
                (left / eligible_mass, right / eligible_mass),
                dim=1,
            )
            return {
                "view_features": views,
                "fused_features": fused,
                "bottleneck": bottleneck,
                "primitive_logits": primitive_logits,
                "residual_logits": residual_logits,
                "bounded_residual": bounded_residual,
                "key_logits": key_logits,
                "key_probabilities": key_probabilities,
                "hand_probabilities": hand_probabilities,
            }

        def forward(
            self,
            signal: Any,
            valid_mask: Any,
            *,
            muted_views: tuple[str, ...] = (),
        ) -> dict[str, Any]:
            return self.forward_from_views(
                self.extract_views(signal, valid_mask),
                muted_views=muted_views,
            )

    model = CausalMotorLatticeV0()
    validate_causal_motor_lattice_model(model, contract=registered)
    return model


def count_trainable_parameters(model: Any) -> int:
    """Return the exact number of trainable scalar parameters."""

    return sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)


def validate_causal_motor_lattice_model(
    model: Any,
    *,
    contract: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Fail closed on architecture, buffer, and parameter-ledger drift."""

    np = _require_numpy()
    registered = dict(contract) if contract is not None else load_registered_cml_synthetic_contract()
    count = count_trainable_parameters(model)
    expected = int(registered["architecture"]["parameter_ledger"]["total_trainable_parameters"])
    if count != expected or count != EXPECTED_PARAMETER_COUNT:
        raise ValueError(f"CML-v0 parameter count mismatch: {count} != {expected}")
    filters = build_causal_filter_coefficients(contract=registered)
    incidence = build_lattice_incidence(contract=registered)
    for name in ("mu", "beta"):
        observed = getattr(model, f"{name}_fir").detach().cpu().numpy().astype("float64")
        if not np.array_equal(observed, filters[name].astype("float32").astype("float64")):
            raise ValueError(f"CML-v0 {name} model buffer mismatch")
    observed_incidence = model.lattice_incidence.detach().cpu().numpy().astype("uint8")
    if not np.array_equal(observed_incidence, incidence):
        raise ValueError("CML-v0 lattice model buffer mismatch")
    if float(registered["architecture"]["residual_gain_rho"]) != RESIDUAL_GAIN:
        raise ValueError("CML-v0 residual gain mismatch")
    return {
        "candidate_id": registered["architecture"]["candidate_id"],
        "trainable_parameters": count,
        "input_channels": INPUT_CHANNELS,
        "primitive_count": PRIMITIVE_COUNT,
        "key_count": KEY_COUNT,
        "producer_is_causal": True,
        "required_left_context_samples": CONTEXT_SAMPLES,
        "required_right_context_samples": 0,
    }


def _validate_contract_identity(contract: Mapping[str, Any]) -> None:
    architecture = contract["architecture"]
    ledger = architecture["parameter_ledger"]
    exact = {
        "input_channels": INPUT_CHANNELS,
        "primitive_count": PRIMITIVE_COUNT,
        "key_count": KEY_COUNT,
        "bottleneck_features": BOTTLENECK_FEATURES,
        "residual_gain_rho": RESIDUAL_GAIN,
        "maximum_trainable_parameters": EXPECTED_PARAMETER_COUNT,
    }
    for key, value in exact.items():
        if architecture.get(key) != value:
            raise ValueError(f"CML-v0 synthetic contract drifted at architecture.{key}")
    if ledger.get("total_trainable_parameters") != EXPECTED_PARAMETER_COUNT:
        raise ValueError("CML-v0 synthetic parameter ledger drifted")
    adapter = contract["pair_anchored_adapter"]
    for key, value in {
        "crop_samples": CROP_SAMPLES,
        "left_filter_context_samples": CONTEXT_SAMPLES,
        "analysis_samples": ANALYSIS_SAMPLES,
        "right_context_samples": 0,
    }.items():
        if adapter.get(key) != value:
            raise ValueError(f"CML-v0 synthetic contract drifted at adapter.{key}")
    if contract["training_recipe"].get("parameter_update_runs") != 1:
        raise ValueError("CML-v0 synthetic training-run count drifted")
    if contract["training_recipe"].get("optimizer_steps") != 600:
        raise ValueError("CML-v0 synthetic optimizer-step count drifted")
    caps = contract["resource_caps"]
    if caps.get("maximum_CPU_threads") != 1 or caps.get("maximum_workers") != 1:
        raise ValueError("CML-v0 synthetic thread or worker cap drifted")
    if caps.get("maximum_generated_output_bytes") != 4 * 1024 * 1024:
        raise ValueError("CML-v0 synthetic output cap drifted")


def _validate_array_bytes(
    value: Any,
    *,
    dtype: str,
    expected_bytes: int,
    expected_sha256: str,
    name: str,
) -> None:
    np = _require_numpy()
    payload = np.asarray(value, dtype=dtype, order="C").tobytes(order="C")
    if len(payload) != expected_bytes:
        raise ValueError(f"{name} byte count mismatch")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        raise ValueError(f"{name} SHA-256 mismatch")


def _require_numpy() -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError(f"NumPy is required. Install with: {NEURO_INSTALL_HINT}") from exc
    return np


def _require_torch() -> tuple[Any, Any, Any]:
    try:
        import torch
        from torch import nn
        from torch.nn import functional
    except ImportError as exc:  # pragma: no cover - optional dependency path
        raise RuntimeError(f"PyTorch is required. Install with: {ML_INSTALL_HINT}") from exc
    return torch, nn, functional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
