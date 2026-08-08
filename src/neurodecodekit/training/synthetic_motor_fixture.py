"""Deterministic synthetic motor-factor and shortcut fixtures.

The module keeps NumPy and SciPy imports inside callable boundaries so the base
package remains dependency-free. All identities and geometry are synthetic.
"""

from __future__ import annotations

import hashlib
import io
import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


SCHEMA_NAME = "neurodecodekit.synthetic_motor_fixture"
SCHEMA_VERSION = "0.1.0"
SIDECAR_SCHEMA_NAME = "neurodecodekit.synthetic_motor_fixture_sidecar"
SIDECAR_SCHEMA_VERSION = "0.1.0"
PROOF_POSTURE = "synthetic_fixture_mechanics_only_no_model_or_scientific_evidence"
CONTRACT_RELATIVE_PATH = Path("registries/synthetic_motor_fixture_contract.v0.json")
REGISTERED_CONTRACT_SHA256 = "0613f2d5df4b4b58b3e49d49cebe159550da7c1cb244f19a2de114cccc0bde27"
DEFAULT_MAX_OUTPUT_BYTES = 4 * 1024 * 1024
MAX_SIDECAR_BYTES = 1024 * 1024
PAYLOAD_NAME = "fixture.npz"
SIDECAR_NAME = "metadata.json"

FACTOR_IDS = (
    "potential_shape_signal",
    "mu_energy_signal",
    "beta_energy_signal",
    "mixed_potential_mu_beta_signal",
    "left_right_spatial_reversal",
    "timing_only_labels_without_signal_relation",
    "peripheral_like_common_mode_artifact",
    "pure_noise",
)
PARTITION_BY_PAIR = ("train", "train", "train", "check", "check", "final")
PARTITION_COUNTS = {"train": 48, "check": 32, "final": 16}
CHANNEL_NAMES = tuple(f"SYN{index:02d}" for index in range(8))
MUTATION_IDS = (
    "line_noise_50_hz",
    "line_noise_60_hz",
    "single_channel_dropout",
    "frozen_channel_derangement",
    "nonwrapping_time_displacement",
    "peripheral_proxy_only",
    "zero_signal",
    "future_tail_mutation",
)
ARRAY_MEMBERS = (
    "channel_names",
    "factor_ids",
    "geometry_xyz",
    "item_ids",
    "metadata",
    "pair_ids",
    "partition_ids",
    "peripheral_proxy",
    "signals",
    "synthetic_hand_class",
    "timestamps_sec",
    "valid_lengths",
    "valid_mask",
)
HASHED_ARRAY_MEMBERS = tuple(name for name in ARRAY_MEMBERS if name != "metadata")
FORBIDDEN_KEY_FRAGMENTS = (
    "target_text",
    "reference_text",
    "intended_text",
    "participant_id",
    "subject_id",
    "protected_path",
)
ACCESS_COUNTERS = {
    "synthetic_fixture_payload_generations": 1,
    "real_or_protected_data_reads": 0,
    "public_EEG_payload_reads": 0,
    "target_or_label_reads": 0,
    "model_or_checkpoint_loads": 0,
    "parameter_update_runs": 0,
    "model_inference_runs": 0,
    "scoring_or_selection_runs": 0,
    "network_calls": 0,
    "provider_calls": 0,
    "stream_device_or_hardware_operations": 0,
    "scientific_claim_upgrades": 0,
}
WARNINGS = (
    "Generated motor-like factors are deliberately constructed and are not biological observations.",
    "Synthetic left/right geometry is not an anatomical montage.",
    "The timing-only family intentionally exposes a metadata shortcut for control testing.",
    "The peripheral family is an ocular-like shortcut proxy, not a validated EOG model.",
    "Passing fixture mechanics cannot qualify CML-v0 or any real EEG pipeline.",
)


@dataclass(frozen=True)
class LoadedSyntheticMotorFixture:
    """One fully validated synthetic fixture payload."""

    arrays: Mapping[str, Any]
    metadata: Mapping[str, Any]
    sidecar: Mapping[str, Any]
    opened_members: tuple[str, ...]

    @property
    def signals(self) -> Any:
        return self.arrays["signals"]

    @property
    def valid_mask(self) -> Any:
        return self.arrays["valid_mask"]

    @property
    def valid_lengths(self) -> Any:
        return self.arrays["valid_lengths"]

    @property
    def timestamps_sec(self) -> Any:
        return self.arrays["timestamps_sec"]

    @property
    def peripheral_proxy(self) -> Any:
        return self.arrays["peripheral_proxy"]


def load_registered_synthetic_motor_contract(
    path: str | Path | None = None,
) -> dict[str, Any]:
    """Load the exact committed fixture contract and reject substitutions."""

    source = Path(path) if path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    payload = source.read_bytes()
    if hashlib.sha256(payload).hexdigest() != REGISTERED_CONTRACT_SHA256:
        raise ValueError("synthetic motor fixture contract SHA-256 mismatch")
    if len(payload) > MAX_SIDECAR_BYTES:
        raise ValueError("synthetic motor fixture contract exceeds 1 MiB")
    contract = json.loads(payload.decode("utf-8"))
    if contract.get("schema_name") != "neurodecodekit.synthetic_motor_fixture_contract":
        raise ValueError("synthetic motor fixture contract schema mismatch")
    if contract.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("synthetic motor fixture contract version mismatch")
    if contract.get("status") != ("preregistered_tier_B_fixture_only_not_implemented_not_executed"):
        raise ValueError("synthetic motor fixture contract status mismatch")
    _validate_contract_identity(contract)
    return contract


def make_synthetic_motor_arrays(
    *,
    contract_path: str | Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Create the registered arrays without consulting data, targets, or models."""

    contract = load_registered_synthetic_motor_contract(contract_path)
    np, scipy_signal = _require_scientific_stack()
    identity = contract["fixture_identity"]
    seed = int(identity["seed"])
    sampling_rate_hz = float(identity["sampling_rate_hz"])
    maximum_samples = int(identity["maximum_samples"])
    channel_count = int(identity["channel_count"])
    item_count = int(identity["item_count"])
    rng = np.random.default_rng(seed)

    signals = np.zeros((item_count, channel_count, maximum_samples), dtype="float32")
    peripheral_proxy = np.zeros((item_count, maximum_samples), dtype="float32")
    valid_mask = np.zeros((item_count, maximum_samples), dtype="bool")
    timestamps_sec = np.zeros((item_count, maximum_samples), dtype="float64")
    valid_lengths = np.zeros(item_count, dtype="int32")
    synthetic_hand_class = np.zeros(item_count, dtype="int8")
    item_ids: list[str] = []
    pair_ids: list[str] = []
    factor_ids: list[str] = []
    partition_ids: list[str] = []

    row_index = 0
    for factor_index, factor_id in enumerate(FACTOR_IDS):
        for pair_index, partition in enumerate(PARTITION_BY_PAIR):
            base_signal = rng.normal(
                0.0,
                0.025,
                size=(channel_count, maximum_samples),
            )
            base_proxy = rng.normal(0.0, 0.01, size=maximum_samples)
            mu_phase = float(rng.uniform(-math.pi, math.pi))
            beta_phase = float(rng.uniform(-math.pi, math.pi))
            for hand_class in (0, 1):
                length = 192 + 8 * pair_index
                if factor_id == "timing_only_labels_without_signal_relation":
                    length += 16 * hand_class
                row, proxy = _make_factor_row(
                    np,
                    factor_id=factor_id,
                    hand_class=hand_class,
                    base_signal=base_signal,
                    base_proxy=base_proxy,
                    sampling_rate_hz=sampling_rate_hz,
                    mu_phase=mu_phase,
                    beta_phase=beta_phase,
                )
                signals[row_index, :, :length] = row[:, :length]
                peripheral_proxy[row_index, :length] = proxy[:length]
                valid_mask[row_index, :length] = True
                timestamps_sec[row_index, :length] = (
                    np.arange(length, dtype="float64") - length
                ) / sampling_rate_hz
                valid_lengths[row_index] = length
                synthetic_hand_class[row_index] = hand_class
                pair_id = f"syn-f{factor_index:02d}-p{pair_index:02d}"
                item_ids.append(f"{pair_id}-h{hand_class}")
                pair_ids.append(pair_id)
                factor_ids.append(factor_id)
                partition_ids.append(partition)
                row_index += 1

    geometry_xyz = _synthetic_geometry(np)
    arrays: dict[str, Any] = {
        "signals": signals,
        "peripheral_proxy": peripheral_proxy,
        "valid_mask": valid_mask,
        "timestamps_sec": timestamps_sec,
        "valid_lengths": valid_lengths,
        "synthetic_hand_class": synthetic_hand_class,
        "item_ids": np.asarray(item_ids, dtype="U24"),
        "pair_ids": np.asarray(pair_ids, dtype="U20"),
        "factor_ids": np.asarray(factor_ids, dtype="U48"),
        "partition_ids": np.asarray(partition_ids, dtype="U8"),
        "channel_names": np.asarray(CHANNEL_NAMES, dtype="U8"),
        "geometry_xyz": geometry_xyz,
    }
    metadata = _build_fixture_metadata(
        np,
        scipy_signal,
        arrays=arrays,
        contract=contract,
    )
    arrays["metadata"] = np.asarray(_canonical_json(metadata))
    validate_synthetic_motor_arrays(arrays, expected_metadata=metadata)
    return arrays, metadata


def prepare_synthetic_motor_fixture(
    out_dir: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Write one deterministic NPZ and one inspectable JSON sidecar."""

    if max_output_bytes <= 0 or max_output_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("fixture output cap must be positive and cannot exceed 4 MiB")
    output = Path(out_dir)
    if output.exists():
        raise FileExistsError(f"refusing to replace fixture directory: {output}")
    contract_source = (
        Path(contract_path) if contract_path is not None else _repo_root() / CONTRACT_RELATIVE_PATH
    )
    contract = load_registered_synthetic_motor_contract(contract_source)
    arrays, metadata = make_synthetic_motor_arrays(contract_path=contract_source)
    payload = _deterministic_npz_bytes(arrays)
    sidecar = _build_sidecar(
        metadata=metadata,
        payload=payload,
        contract_bytes=contract_source.stat().st_size,
        contract=contract,
        max_output_bytes=max_output_bytes,
    )
    sidecar_payload = _sidecar_payload_with_sizes(sidecar)
    total_bytes = len(payload) + len(sidecar_payload)
    if total_bytes > max_output_bytes:
        raise ValueError(
            f"fixture would write {total_bytes} bytes, exceeding cap {max_output_bytes}"
        )

    output.mkdir(parents=True, exist_ok=False)
    (output / PAYLOAD_NAME).write_bytes(payload)
    sidecar_path = output / SIDECAR_NAME
    sidecar_path.write_bytes(sidecar_payload)
    return load_synthetic_motor_metadata(
        sidecar_path,
        contract_path=contract_source,
        max_output_bytes=max_output_bytes,
    )


def load_synthetic_motor_metadata(
    path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> dict[str, Any]:
    """Validate the sidecar, payload hash, and ZIP members without opening arrays."""

    if max_output_bytes <= 0 or max_output_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("fixture validation cap must be positive and cannot exceed 4 MiB")
    source = Path(path)
    sidecar_bytes = source.stat().st_size
    if sidecar_bytes > MAX_SIDECAR_BYTES:
        raise ValueError("synthetic motor fixture sidecar exceeds 1 MiB")
    sidecar = json.loads(source.read_text(encoding="utf-8"))
    _validate_forbidden_keys(sidecar)
    if sidecar.get("schema") != {
        "name": SIDECAR_SCHEMA_NAME,
        "version": SIDECAR_SCHEMA_VERSION,
    }:
        raise ValueError("synthetic motor fixture sidecar schema mismatch")
    contract = load_registered_synthetic_motor_contract(contract_path)
    contract_binding = sidecar.get("contract", {})
    if contract_binding != {
        "path": CONTRACT_RELATIVE_PATH.as_posix(),
        "bytes": int(sidecar["artifacts"]["input_contract_bytes"]),
        "sha256": REGISTERED_CONTRACT_SHA256,
    }:
        raise ValueError("synthetic motor fixture contract binding mismatch")
    if contract_binding["bytes"] != int(
        (Path(contract_path) if contract_path else _repo_root() / CONTRACT_RELATIVE_PATH)
        .stat()
        .st_size
    ):
        raise ValueError("synthetic motor fixture contract byte count mismatch")
    _validate_sidecar_identity(sidecar, contract=contract)

    payload_binding = sidecar.get("payload", {})
    relative = PurePosixPath(str(payload_binding.get("path", "")))
    if relative.is_absolute() or len(relative.parts) != 1 or ".." in relative.parts:
        raise ValueError("synthetic motor fixture payload path is unsafe")
    if relative.as_posix() != PAYLOAD_NAME:
        raise ValueError("synthetic motor fixture payload filename mismatch")
    if payload_binding.get("array_members") != list(ARRAY_MEMBERS):
        raise ValueError("synthetic motor fixture payload member binding mismatch")
    payload_path = source.parent / relative.as_posix()
    if payload_path.stat().st_size != payload_binding.get("bytes"):
        raise ValueError("synthetic motor fixture payload byte count mismatch")
    if _file_sha256(payload_path) != payload_binding.get("sha256"):
        raise ValueError("synthetic motor fixture payload SHA-256 mismatch")
    members, uncompressed_bytes = _npz_member_inventory(payload_path)
    if set(members) != set(ARRAY_MEMBERS) or len(members) != len(ARRAY_MEMBERS):
        raise ValueError("synthetic motor fixture NPZ member set mismatch")
    if uncompressed_bytes > DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("synthetic motor fixture uncompressed arrays exceed cap")

    artifacts = sidecar.get("artifacts", {})
    total_bytes = payload_path.stat().st_size + sidecar_bytes
    if artifacts.get("output_files") != 2:
        raise ValueError("synthetic motor fixture must retain exactly two files")
    if artifacts.get("payload_bytes") != payload_path.stat().st_size:
        raise ValueError("synthetic motor fixture payload accounting mismatch")
    if artifacts.get("metadata_sidecar_bytes") != sidecar_bytes:
        raise ValueError("synthetic motor fixture sidecar accounting mismatch")
    if artifacts.get("total_output_bytes") != total_bytes:
        raise ValueError("synthetic motor fixture total-byte accounting mismatch")
    if total_bytes > max_output_bytes or total_bytes > artifacts.get("maximum_output_bytes", -1):
        raise ValueError("synthetic motor fixture output exceeds cap")
    return sidecar


def load_synthetic_motor_fixture(
    sidecar_path: str | Path,
    *,
    contract_path: str | Path | None = None,
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES,
) -> LoadedSyntheticMotorFixture:
    """Open and strictly validate every registered array."""

    np, _ = _require_scientific_stack()
    sidecar = load_synthetic_motor_metadata(
        sidecar_path,
        contract_path=contract_path,
        max_output_bytes=max_output_bytes,
    )
    source = Path(sidecar_path).parent / sidecar["payload"]["path"]
    with np.load(source, allow_pickle=False) as data:
        opened_members = tuple(data.files)
        if set(opened_members) != set(ARRAY_MEMBERS):
            raise ValueError("synthetic motor fixture NPZ member set mismatch")
        arrays = {name: data[name].copy() for name in opened_members}
    metadata = json.loads(str(arrays["metadata"].item()))
    validate_synthetic_motor_arrays(
        arrays,
        expected_metadata=sidecar["fixture_metadata"],
    )
    if metadata != sidecar["fixture_metadata"]:
        raise ValueError("embedded fixture metadata does not match sidecar")
    return LoadedSyntheticMotorFixture(
        arrays=arrays,
        metadata=metadata,
        sidecar=sidecar,
        opened_members=opened_members,
    )


def validate_synthetic_motor_arrays(
    arrays: Mapping[str, Any],
    *,
    expected_metadata: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate dimensions, identities, timing, padding, hashes, and factors."""

    np, scipy_signal = _require_scientific_stack()
    if set(arrays) != set(ARRAY_MEMBERS):
        raise ValueError("synthetic motor fixture array-member mismatch")
    expected_specs = {
        "signals": ((96, 8, 256), np.dtype("float32")),
        "peripheral_proxy": ((96, 256), np.dtype("float32")),
        "valid_mask": ((96, 256), np.dtype("bool")),
        "timestamps_sec": ((96, 256), np.dtype("float64")),
        "valid_lengths": ((96,), np.dtype("int32")),
        "synthetic_hand_class": ((96,), np.dtype("int8")),
        "geometry_xyz": ((8, 3), np.dtype("float32")),
    }
    for name, (shape, dtype) in expected_specs.items():
        if arrays[name].shape != shape or arrays[name].dtype != dtype:
            raise ValueError(f"synthetic motor fixture {name} shape or dtype mismatch")
    for name, shape in (
        ("item_ids", (96,)),
        ("pair_ids", (96,)),
        ("factor_ids", (96,)),
        ("partition_ids", (96,)),
        ("channel_names", (8,)),
    ):
        if arrays[name].shape != shape or arrays[name].dtype.kind != "U":
            raise ValueError(f"synthetic motor fixture {name} must be Unicode {shape}")
    if arrays["metadata"].shape != () or arrays["metadata"].dtype.kind != "U":
        raise ValueError("synthetic motor fixture metadata must be a Unicode scalar")

    metadata = json.loads(str(arrays["metadata"].item()))
    _validate_forbidden_keys(metadata)
    if expected_metadata is not None and metadata != dict(expected_metadata):
        raise ValueError("synthetic motor fixture metadata identity mismatch")
    if metadata.get("schema") != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("synthetic motor fixture embedded schema mismatch")
    if metadata.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("synthetic motor fixture proof posture mismatch")

    lengths = arrays["valid_lengths"]
    mask = arrays["valid_mask"]
    timestamps = arrays["timestamps_sec"]
    signals = arrays["signals"]
    proxy = arrays["peripheral_proxy"]
    if not np.isfinite(signals).all() or not np.isfinite(proxy).all():
        raise ValueError("synthetic motor fixture contains nonfinite signal values")
    if not np.isfinite(timestamps).all():
        raise ValueError("synthetic motor fixture contains nonfinite timestamps")
    for index, length_value in enumerate(lengths.tolist()):
        length = int(length_value)
        if length <= 0 or length > 256:
            raise ValueError("synthetic motor fixture valid length is outside bounds")
        if not mask[index, :length].all() or mask[index, length:].any():
            raise ValueError("synthetic motor fixture mask must be one contiguous prefix")
        if not (timestamps[index, :length] < 0.0).all():
            raise ValueError("synthetic motor fixture valid timestamps must be pre-event")
        if length > 1 and not np.allclose(
            np.diff(timestamps[index, :length]),
            1.0 / 128.0,
            rtol=0.0,
            atol=1e-12,
        ):
            raise ValueError("synthetic motor fixture timestamp spacing mismatch")
        if not np.equal(signals[index, :, length:], 0.0).all():
            raise ValueError("synthetic motor fixture signal padding must be exact zero")
        if not np.equal(proxy[index, length:], 0.0).all():
            raise ValueError("synthetic motor fixture proxy padding must be exact zero")
        if not np.equal(timestamps[index, length:], 0.0).all():
            raise ValueError("synthetic motor fixture timestamp padding must be exact zero")

    if arrays["channel_names"].tolist() != list(CHANNEL_NAMES):
        raise ValueError("synthetic motor fixture channel identity mismatch")
    if not np.array_equal(arrays["geometry_xyz"], _synthetic_geometry(np)):
        raise ValueError("synthetic motor fixture geometry mismatch")
    _validate_row_identities(arrays)
    expected_hashes = metadata.get("array_sha256", {})
    if set(expected_hashes) != set(HASHED_ARRAY_MEMBERS):
        raise ValueError("synthetic motor fixture array-hash inventory mismatch")
    for name in HASHED_ARRAY_MEMBERS:
        if expected_hashes[name] != _array_sha256(arrays[name]):
            raise ValueError(f"synthetic motor fixture {name} hash mismatch")

    diagnostics = _factor_diagnostics(np, scipy_signal, arrays)
    if not all(row["passed"] for row in diagnostics.values()):
        failed = sorted(name for name, row in diagnostics.items() if not row["passed"])
        raise ValueError(f"synthetic motor fixture analytic factor gate failed: {failed}")
    if metadata.get("factor_diagnostics") != diagnostics:
        raise ValueError("synthetic motor fixture factor diagnostics mismatch")
    return diagnostics


def summarize_synthetic_motor_metadata(sidecar: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact metadata-only summary."""

    fixture = sidecar["fixture_metadata"]
    return {
        "schema": sidecar["schema"],
        "proof_posture": sidecar["proof_posture"],
        "contract": sidecar["contract"],
        "payload": sidecar["payload"],
        "item_count": fixture["identity"]["item_count"],
        "signal_shape": fixture["array_shapes"]["signals"],
        "valid_sample_count": fixture["valid_sample_count"],
        "padding_fraction": fixture["padding_fraction"],
        "factor_counts": fixture["factor_counts"],
        "partition_counts": fixture["partition_counts"],
        "producer_is_causal": sidecar["causality"]["producer_is_causal"],
        "required_right_context_samples": 0,
        "end_to_end_latency_measured": False,
        "array_members_opened": 0,
        "artifacts": sidecar["artifacts"],
        "access_counters": sidecar["access_counters"],
        "warnings": sidecar["warnings"],
        "unavailable_fields": sidecar["unavailable_fields"],
        "claim_boundary": sidecar["claim_boundary"],
    }


def apply_synthetic_motor_mutation(
    fixture: LoadedSyntheticMotorFixture,
    mutation_id: str,
    *,
    cutoff_sample: int = 128,
) -> Any:
    """Apply one registered deterministic mutation and preserve exact padding."""

    np, _ = _require_scientific_stack()
    if mutation_id not in MUTATION_IDS:
        raise ValueError(f"unsupported synthetic motor mutation: {mutation_id}")
    source = fixture.signals
    output = source.copy()
    mask = fixture.valid_mask
    if mutation_id in {"line_noise_50_hz", "line_noise_60_hz"}:
        frequency = 50.0 if mutation_id == "line_noise_50_hz" else 60.0
        component = 0.05 * np.sin(2.0 * math.pi * frequency * fixture.timestamps_sec)
        output += component[:, None, :].astype("float32") * mask[:, None, :]
    elif mutation_id == "single_channel_dropout":
        output[:, 2, :] = 0.0
    elif mutation_id == "frozen_channel_derangement":
        output = output[:, [4, 5, 6, 7, 0, 1, 2, 3], :].copy()
    elif mutation_id == "nonwrapping_time_displacement":
        output.fill(0.0)
        for row, length_value in enumerate(fixture.valid_lengths.tolist()):
            length = int(length_value)
            if length > 16:
                output[row, :, : length - 16] = source[row, :, 16:length]
    elif mutation_id == "peripheral_proxy_only":
        weights = np.asarray([0.80, 0.88, 0.96, 1.04, 1.04, 0.96, 0.88, 0.80])
        output = (weights[None, :, None] * fixture.peripheral_proxy[:, None, :]).astype("float32")
    elif mutation_id == "zero_signal":
        output.fill(0.0)
    elif mutation_id == "future_tail_mutation":
        if cutoff_sample < 0 or cutoff_sample >= source.shape[2] - 1:
            raise ValueError("future-tail cutoff must leave at least one later sample")
        channel_offsets = np.linspace(0.01, 0.08, source.shape[1], dtype="float32")
        tail_mask = mask.copy()
        tail_mask[:, : cutoff_sample + 1] = False
        output += channel_offsets[None, :, None] * tail_mask[:, None, :]
    output *= mask[:, None, :]
    if output.shape != source.shape or output.dtype != np.dtype("float32"):
        raise RuntimeError("synthetic motor mutation changed shape or dtype")
    if not np.isfinite(output).all():
        raise RuntimeError("synthetic motor mutation produced nonfinite values")
    for row, length_value in enumerate(fixture.valid_lengths.tolist()):
        if not np.equal(output[row, :, int(length_value) :], 0.0).all():
            raise RuntimeError("synthetic motor mutation changed exact padding")
    return output


def _make_factor_row(
    np: Any,
    *,
    factor_id: str,
    hand_class: int,
    base_signal: Any,
    base_proxy: Any,
    sampling_rate_hz: float,
    mu_phase: float,
    beta_phase: float,
) -> tuple[Any, Any]:
    samples = base_signal.shape[1]
    time = np.arange(samples, dtype="float64") / sampling_rate_hz
    envelope = np.linspace(0.05, 1.0, samples, dtype="float64")
    lateral = np.asarray([1.0, 0.9, 0.8, 0.7, -0.7, -0.8, -0.9, -1.0])
    hand_sign = 1.0 if hand_class == 0 else -1.0
    row = base_signal.copy()
    proxy = base_proxy.copy()

    def add_potential(scale: float) -> None:
        nonlocal row
        row += hand_sign * scale * lateral[:, None] * envelope[None, :]

    def add_energy(frequency: float, high: float, low: float, phase: float) -> None:
        nonlocal row
        left_high = hand_class == 0
        amplitudes = np.asarray([high] * 4 + [low] * 4 if left_high else [low] * 4 + [high] * 4)
        row += amplitudes[:, None] * np.sin(2.0 * math.pi * frequency * time[None, :] + phase)

    if factor_id == "potential_shape_signal":
        add_potential(0.55)
    elif factor_id == "mu_energy_signal":
        add_energy(10.0, 0.60, 0.12, mu_phase)
    elif factor_id == "beta_energy_signal":
        add_energy(20.0, 0.52, 0.10, beta_phase)
    elif factor_id in (
        "mixed_potential_mu_beta_signal",
        "left_right_spatial_reversal",
    ):
        add_potential(0.35)
        add_energy(10.0, 0.42, 0.09, mu_phase)
        add_energy(20.0, 0.36, 0.08, beta_phase)
        if factor_id == "left_right_spatial_reversal":
            row = row[::-1].copy()
    elif factor_id == "peripheral_like_common_mode_artifact":
        center = samples - 96
        blink = hand_sign * 0.85 * np.exp(-0.5 * ((np.arange(samples) - center) / 11.0) ** 2)
        proxy = proxy + blink
        weights = np.asarray([0.80, 0.88, 0.96, 1.04, 1.04, 0.96, 0.88, 0.80])
        row += weights[:, None] * proxy[None, :]
    elif factor_id not in (
        "timing_only_labels_without_signal_relation",
        "pure_noise",
    ):
        raise ValueError(f"unknown synthetic motor factor: {factor_id}")
    return np.asarray(row, dtype="float32"), np.asarray(proxy, dtype="float32")


def _build_fixture_metadata(
    np: Any,
    scipy_signal: Any,
    *,
    arrays: Mapping[str, Any],
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    valid_samples = int(arrays["valid_lengths"].sum())
    total_samples = int(arrays["valid_mask"].size)
    factor_counts = {factor: int(np.sum(arrays["factor_ids"] == factor)) for factor in FACTOR_IDS}
    partition_counts = {
        split: int(np.sum(arrays["partition_ids"] == split)) for split in PARTITION_COUNTS
    }
    metadata: dict[str, Any] = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "identity": {
            "seed": int(contract["fixture_identity"]["seed"]),
            "item_count": 96,
            "channel_count": 8,
            "sampling_rate_hz": 128,
            "maximum_samples": 256,
            "right_context_samples": 0,
            "channel_identity": "synthetic_not_anatomical",
            "geometry_units": "synthetic_arbitrary_unit",
            "signal_units": "synthetic_arbitrary_unit",
        },
        "array_shapes": {name: list(arrays[name].shape) for name in HASHED_ARRAY_MEMBERS},
        "array_dtypes": {name: str(arrays[name].dtype) for name in HASHED_ARRAY_MEMBERS},
        "array_sha256": {name: _array_sha256(arrays[name]) for name in HASHED_ARRAY_MEMBERS},
        "factor_counts": factor_counts,
        "partition_counts": partition_counts,
        "valid_sample_count": valid_samples,
        "padding_fraction": round(1.0 - valid_samples / total_samples, 9),
        "pair_count": int(len(set(arrays["pair_ids"].tolist()))),
        "mutation_ids": list(MUTATION_IDS),
        "factor_diagnostics": _factor_diagnostics(np, scipy_signal, arrays),
        "causality": {
            "producer_is_causal": True,
            "strictly_pre_event": True,
            "required_right_context_samples": 0,
        },
        "access_counters": dict(ACCESS_COUNTERS),
        "warnings": list(WARNINGS),
        "claim_boundary": dict(contract["claim_boundary"]),
    }
    _validate_forbidden_keys(metadata)
    return metadata


def _build_sidecar(
    *,
    metadata: Mapping[str, Any],
    payload: bytes,
    contract_bytes: int,
    contract: Mapping[str, Any],
    max_output_bytes: int,
) -> dict[str, Any]:
    return {
        "schema": {"name": SIDECAR_SCHEMA_NAME, "version": SIDECAR_SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "bytes": int(contract_bytes),
            "sha256": REGISTERED_CONTRACT_SHA256,
        },
        "payload": {
            "path": PAYLOAD_NAME,
            "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest(),
            "array_members": list(ARRAY_MEMBERS),
        },
        "fixture_metadata": dict(metadata),
        "causality": dict(metadata["causality"]),
        "access_counters": dict(ACCESS_COUNTERS),
        "artifacts": {
            "input_contract_bytes": int(contract_bytes),
            "payload_bytes": len(payload),
            "metadata_sidecar_bytes": 0,
            "total_output_bytes": 0,
            "maximum_output_bytes": int(max_output_bytes),
            "output_files": 2,
        },
        "measurements": {
            "runtime_seconds": "unavailable_until_measured_closeout",
            "peak_RSS_bytes": "unavailable_until_measured_closeout",
            "configured_numerical_threads": 1,
            "worker_count": 1,
            "end_to_end_latency_measured": False,
        },
        "warnings": list(WARNINGS),
        "unavailable_fields": [
            "real_EEG_or_MEG_quality",
            "biological_neural_origin",
            "decoding_accuracy",
            "unseen_person_generalization",
            "end_to_end_latency",
            "device_or_home_performance",
            "clinical_utility",
        ],
        "claim_boundary": dict(contract["claim_boundary"]),
    }


def _validate_contract_identity(contract: Mapping[str, Any]) -> None:
    identity = contract["fixture_identity"]
    exact = {
        "seed": 5503,
        "sampling_rate_hz": 128,
        "maximum_samples": 256,
        "right_context_samples": 0,
        "channel_count": 8,
        "item_count": 96,
        "factor_family_count": 8,
        "items_per_factor_family": 12,
        "paired_design_classes_per_factor_family": 6,
    }
    for key, value in exact.items():
        if identity.get(key) != value:
            raise ValueError(f"synthetic motor fixture contract drifted at {key}")
    if tuple(identity.get("channel_names", ())) != CHANNEL_NAMES:
        raise ValueError("synthetic motor fixture channel contract drifted")
    if identity.get("partition_counts") != PARTITION_COUNTS:
        raise ValueError("synthetic motor fixture partition contract drifted")
    if tuple(row["factor_id"] for row in contract["factor_families"]) != FACTOR_IDS:
        raise ValueError("synthetic motor fixture factor contract drifted")
    if tuple(row["mutation_id"] for row in contract["mutation_contract"]) != MUTATION_IDS:
        raise ValueError("synthetic motor fixture mutation contract drifted")
    if contract["resource_caps"]["maximum_generated_output_bytes"] != DEFAULT_MAX_OUTPUT_BYTES:
        raise ValueError("synthetic motor fixture output cap drifted")


def _validate_sidecar_identity(
    sidecar: Mapping[str, Any],
    *,
    contract: Mapping[str, Any],
) -> None:
    expected_top_level = {
        "schema",
        "proof_posture",
        "target_free",
        "contract",
        "payload",
        "fixture_metadata",
        "causality",
        "access_counters",
        "artifacts",
        "measurements",
        "warnings",
        "unavailable_fields",
        "claim_boundary",
    }
    if set(sidecar) != expected_top_level:
        raise ValueError("synthetic motor fixture sidecar fields mismatch")
    if sidecar.get("proof_posture") != PROOF_POSTURE or not sidecar.get("target_free"):
        raise ValueError("synthetic motor fixture sidecar proof posture mismatch")
    fixture = sidecar.get("fixture_metadata", {})
    identity = fixture.get("identity", {})
    if identity.get("seed") != contract["fixture_identity"]["seed"]:
        raise ValueError("synthetic motor fixture seed mismatch")
    if identity.get("item_count") != 96 or identity.get("right_context_samples") != 0:
        raise ValueError("synthetic motor fixture identity mismatch")
    if fixture.get("factor_counts") != {name: 12 for name in FACTOR_IDS}:
        raise ValueError("synthetic motor fixture factor counts mismatch")
    if fixture.get("partition_counts") != PARTITION_COUNTS:
        raise ValueError("synthetic motor fixture partition counts mismatch")
    if fixture.get("mutation_ids") != list(MUTATION_IDS):
        raise ValueError("synthetic motor fixture mutation inventory mismatch")
    if fixture.get("access_counters") != ACCESS_COUNTERS:
        raise ValueError("embedded synthetic motor access counters mismatch")
    if fixture.get("causality") != sidecar.get("causality"):
        raise ValueError("synthetic motor fixture causality binding mismatch")
    if sidecar.get("access_counters") != ACCESS_COUNTERS:
        raise ValueError("synthetic motor fixture access counters mismatch")
    if sidecar.get("warnings") != list(WARNINGS):
        raise ValueError("synthetic motor fixture warnings mismatch")
    if fixture.get("warnings") != list(WARNINGS):
        raise ValueError("embedded synthetic motor fixture warnings mismatch")
    if sidecar.get("claim_boundary") != contract.get("claim_boundary"):
        raise ValueError("synthetic motor fixture claim boundary mismatch")
    if fixture.get("claim_boundary") != contract.get("claim_boundary"):
        raise ValueError("embedded synthetic motor fixture claim boundary mismatch")
    measurements = sidecar.get("measurements", {})
    if measurements.get("configured_numerical_threads") != 1:
        raise ValueError("synthetic motor fixture thread count mismatch")
    if measurements.get("worker_count") != 1:
        raise ValueError("synthetic motor fixture worker count mismatch")
    if measurements.get("end_to_end_latency_measured") is not False:
        raise ValueError("synthetic motor fixture latency status mismatch")


def _validate_row_identities(arrays: Mapping[str, Any]) -> None:
    factors = arrays["factor_ids"].tolist()
    partitions = arrays["partition_ids"].tolist()
    pairs = arrays["pair_ids"].tolist()
    items = arrays["item_ids"].tolist()
    classes = arrays["synthetic_hand_class"].tolist()
    if len(set(items)) != 96:
        raise ValueError("synthetic motor fixture item IDs must be unique")
    expected_row = 0
    pair_partitions: dict[str, str] = {}
    for factor_index, factor in enumerate(FACTOR_IDS):
        for pair_index, partition in enumerate(PARTITION_BY_PAIR):
            pair = f"syn-f{factor_index:02d}-p{pair_index:02d}"
            for hand_class in (0, 1):
                if factors[expected_row] != factor:
                    raise ValueError("synthetic motor fixture factor ordering mismatch")
                if pairs[expected_row] != pair:
                    raise ValueError("synthetic motor fixture pair identity mismatch")
                if items[expected_row] != f"{pair}-h{hand_class}":
                    raise ValueError("synthetic motor fixture item identity mismatch")
                if int(classes[expected_row]) != hand_class:
                    raise ValueError("synthetic motor fixture design-class mismatch")
                if partitions[expected_row] != partition:
                    raise ValueError("synthetic motor fixture partition identity mismatch")
                pair_partitions.setdefault(pair, partition)
                if pair_partitions[pair] != partition:
                    raise ValueError("synthetic motor fixture pair crosses partitions")
                expected_row += 1
    counts = {name: partitions.count(name) for name in PARTITION_COUNTS}
    if counts != PARTITION_COUNTS:
        raise ValueError("synthetic motor fixture partition inventory mismatch")


def _factor_diagnostics(np: Any, scipy_signal: Any, arrays: Mapping[str, Any]) -> dict[str, Any]:
    factors = arrays["factor_ids"]
    classes = arrays["synthetic_hand_class"]
    lengths = arrays["valid_lengths"]
    signals = arrays["signals"]
    timestamps = arrays["timestamps_sec"]
    proxy = arrays["peripheral_proxy"]
    diagnostics: dict[str, Any] = {}
    for factor in FACTOR_IDS:
        indices = np.flatnonzero(factors == factor).tolist()
        potential_scores: list[float] = []
        mu_scores: list[float] = []
        beta_scores: list[float] = []
        proxy_correlations: list[float] = []
        pair_signal_diffs: list[float] = []
        pair_timing_equal: list[bool] = []
        pair_length_diffs: list[int] = []
        for index in indices:
            length = int(lengths[index])
            hand_sign = 1.0 if int(classes[index]) == 0 else -1.0
            row = signals[index, :, :length].astype("float64")
            late = row[:, max(0, length - 48) :]
            potential_scores.append(hand_sign * float(late[:4].mean() - late[4:].mean()))
            mu_scores.append(
                hand_sign
                * _band_lateralization(
                    np,
                    scipy_signal,
                    row,
                    sampling_rate_hz=128.0,
                    low_hz=8.0,
                    high_hz=13.0,
                )
            )
            beta_scores.append(
                hand_sign
                * _band_lateralization(
                    np,
                    scipy_signal,
                    row,
                    sampling_rate_hz=128.0,
                    low_hz=13.0,
                    high_hz=30.0,
                )
            )
            proxy_row = proxy[index, :length].astype("float64")
            proxy_std = float(proxy_row.std())
            global_row = row.mean(axis=0)
            correlation = (
                float(np.corrcoef(global_row, proxy_row)[0, 1])
                if proxy_std > 0.0 and float(global_row.std()) > 0.0
                else 0.0
            )
            proxy_correlations.append(correlation)
        for offset in range(0, len(indices), 2):
            left_index, right_index = indices[offset : offset + 2]
            shared = min(int(lengths[left_index]), int(lengths[right_index]))
            pair_signal_diffs.append(
                float(
                    np.max(
                        np.abs(signals[left_index, :, :shared] - signals[right_index, :, :shared])
                    )
                )
            )
            pair_timing_equal.append(
                bool(
                    int(lengths[left_index]) == int(lengths[right_index])
                    and np.array_equal(
                        timestamps[left_index, : int(lengths[left_index])],
                        timestamps[right_index, : int(lengths[right_index])],
                    )
                )
            )
            pair_length_diffs.append(abs(int(lengths[left_index]) - int(lengths[right_index])))
        row = {
            "mean_potential_lateralization": round(float(np.mean(potential_scores)), 9),
            "mean_mu_lateralization": round(float(np.mean(mu_scores)), 9),
            "mean_beta_lateralization": round(float(np.mean(beta_scores)), 9),
            "mean_proxy_correlation": round(float(np.mean(proxy_correlations)), 9),
            "maximum_pair_shared_signal_difference": round(max(pair_signal_diffs), 9),
            "all_pair_timing_equal": all(pair_timing_equal),
            "pair_length_differences": pair_length_diffs,
        }
        if factor == "potential_shape_signal":
            passed = row["mean_potential_lateralization"] > 0.30
        elif factor == "mu_energy_signal":
            passed = row["mean_mu_lateralization"] > 0.08
        elif factor == "beta_energy_signal":
            passed = row["mean_beta_lateralization"] > 0.05
        elif factor == "mixed_potential_mu_beta_signal":
            passed = (
                row["mean_potential_lateralization"] > 0.18
                and row["mean_mu_lateralization"] > 0.03
                and row["mean_beta_lateralization"] > 0.02
            )
        elif factor == "left_right_spatial_reversal":
            passed = (
                row["mean_potential_lateralization"] < -0.18
                and row["mean_mu_lateralization"] < -0.03
                and row["mean_beta_lateralization"] < -0.02
            )
        elif factor == "timing_only_labels_without_signal_relation":
            passed = (
                row["maximum_pair_shared_signal_difference"] == 0.0
                and row["pair_length_differences"] == [16] * 6
                and not row["all_pair_timing_equal"]
            )
        elif factor == "peripheral_like_common_mode_artifact":
            passed = row["mean_proxy_correlation"] > 0.95
        else:
            passed = (
                row["maximum_pair_shared_signal_difference"] == 0.0
                and row["pair_length_differences"] == [0] * 6
                and row["all_pair_timing_equal"]
            )
        row["passed"] = bool(passed)
        diagnostics[factor] = row
    return diagnostics


def _band_lateralization(
    np: Any,
    scipy_signal: Any,
    row: Any,
    *,
    sampling_rate_hz: float,
    low_hz: float,
    high_hz: float,
) -> float:
    frequencies, power = scipy_signal.periodogram(
        row,
        fs=sampling_rate_hz,
        axis=-1,
        detrend="constant",
        scaling="spectrum",
    )
    selected = (frequencies >= low_hz) & (frequencies <= high_hz)
    band = power[:, selected].sum(axis=1)
    return float(np.mean(band[:4]) - np.mean(band[4:]))


def _synthetic_geometry(np: Any) -> Any:
    return np.asarray(
        [
            [-1.50, 0.00, 0.00],
            [-1.00, 0.55, 0.00],
            [-0.60, 1.00, 0.00],
            [-0.25, 1.35, 0.00],
            [0.25, 1.35, 0.00],
            [0.60, 1.00, 0.00],
            [1.00, 0.55, 0.00],
            [1.50, 0.00, 0.00],
        ],
        dtype="float32",
    )


def _deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    np, _ = _require_scientific_stack()
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(arrays):
            member = io.BytesIO()
            np.save(member, np.asarray(arrays[name]), allow_pickle=False)
            info = zipfile.ZipInfo(f"{name}.npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, member.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return output.getvalue()


def _npz_member_inventory(path: Path) -> tuple[tuple[str, ...], int]:
    try:
        with zipfile.ZipFile(path, mode="r") as archive:
            entries = archive.infolist()
    except zipfile.BadZipFile as exc:
        raise ValueError("synthetic motor fixture payload is not a valid NPZ") from exc
    names: list[str] = []
    uncompressed_bytes = 0
    for entry in entries:
        member = PurePosixPath(entry.filename)
        if member.is_absolute() or len(member.parts) != 1 or member.suffix != ".npy":
            raise ValueError(f"synthetic motor fixture contains unsafe member: {entry.filename}")
        names.append(member.stem)
        uncompressed_bytes += int(entry.file_size)
    if len(names) != len(set(names)):
        raise ValueError("synthetic motor fixture contains duplicate members")
    return tuple(names), uncompressed_bytes


def _sidecar_payload_with_sizes(sidecar: dict[str, Any]) -> bytes:
    for _ in range(10):
        payload = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode("utf-8")
        sidecar["artifacts"]["metadata_sidecar_bytes"] = len(payload)
        sidecar["artifacts"]["total_output_bytes"] = sidecar["artifacts"]["payload_bytes"] + len(
            payload
        )
    return (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _array_sha256(value: Any) -> str:
    np, _ = _require_scientific_stack()
    payload = io.BytesIO()
    np.save(payload, np.asarray(value), allow_pickle=False)
    return hashlib.sha256(payload.getvalue()).hexdigest()


def _validate_forbidden_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            lowered = str(key).lower()
            if any(fragment in lowered for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError(f"synthetic motor fixture contains forbidden field: {key}")
            _validate_forbidden_keys(nested)
    elif isinstance(value, list):
        for item in value:
            _validate_forbidden_keys(item)


def _require_scientific_stack() -> tuple[Any, Any]:
    try:
        import numpy as np
        import scipy
        from scipy import signal as scipy_signal
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError(
            "Synthetic motor fixtures require NumPy and SciPy. Install neurodecodekit[neuro]."
        ) from exc
    if _major_minor(np.__version__) < (1, 26):
        raise RuntimeError("Synthetic motor fixtures require NumPy >=1.26.")
    if _major_minor(scipy.__version__) < (1, 11):
        raise RuntimeError("Synthetic motor fixtures require SciPy >=1.11.")
    return np, scipy_signal


def _major_minor(version: str) -> tuple[int, int]:
    values: list[int] = []
    for part in version.split(".")[:2]:
        digits = "".join(character for character in part if character.isdigit())
        values.append(int(digits or 0))
    while len(values) < 2:
        values.append(0)
    return values[0], values[1]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]
