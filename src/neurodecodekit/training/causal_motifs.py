"""Bounded synthetic motif fixtures for the tiny causal encoder gate."""

from __future__ import annotations

import hashlib
import io
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


CAUSAL_MOTIF_SCHEMA_NAME = "b2q-causal-motif-fixture"
CAUSAL_MOTIF_SCHEMA_VERSION = 0
CAUSAL_MOTIF_MANIFEST_SCHEMA_NAME = "b2q-causal-motif-manifest"
CAUSAL_MOTIF_MANIFEST_SCHEMA_VERSION = 0
CAUSAL_MOTIF_PROOF_POSTURE = "synthetic_causal_motif_fixture_only"
PARTITION_NAMES = ("train", "validation", "test")


@dataclass(frozen=True)
class CausalMotifProtocol:
    """Complete deterministic generation protocol for three physical partitions."""

    train_items: int = 64
    validation_items: int = 8
    test_items: int = 8
    n_channels: int = 5
    n_motif_classes: int = 5
    sampling_rate_hz: float = 100.0
    kernel_size: int = 16
    stride: int = 4
    min_motifs: int = 5
    max_motifs: int = 8
    motif_width: int = 8
    gap_width: int = 4
    lead_width: int = 16
    tail_width: int = 4
    motif_amplitude: float = 1.5
    adjacent_amplitude: float = 0.25
    noise_std: float = 0.10
    gain_min: float = 0.85
    gain_max: float = 1.15
    offset_std: float = 0.03
    train_seed: int = 2201
    validation_seed: int = 2202
    test_seed: int = 2203

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def total_items(self) -> int:
        return self.train_items + self.validation_items + self.test_items

    @property
    def n_classes(self) -> int:
        return self.n_motif_classes + 1

    @property
    def max_timepoints(self) -> int:
        return (
            self.lead_width
            + self.max_motifs * self.motif_width
            + (self.max_motifs - 1) * self.gap_width
            + self.tail_width
        )

    @property
    def max_frames(self) -> int:
        return 1 + (self.max_timepoints - self.kernel_size) // self.stride

    @property
    def protocol_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class LoadedCausalMotifPartition:
    """Validated arrays for one synthetic physical partition."""

    path: str
    split: str
    signals: Any
    input_lengths: Any
    sample_labels: Any
    frame_labels: Any
    frame_lengths: Any
    item_ids: Any
    motif_sequences: Any
    motif_lengths: Any
    metadata: dict[str, Any]

    @property
    def bytes(self) -> int:
        return int(Path(self.path).stat().st_size)

    @property
    def sha256(self) -> str:
        return _file_sha256(Path(self.path))


def registered_causal_motif_protocol() -> CausalMotifProtocol:
    return CausalMotifProtocol()


def prepare_causal_motif_fixture(
    out_dir: str | Path,
    *,
    protocol: CausalMotifProtocol | None = None,
    max_total_mb: float = 1.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Write separate train/validation/test fixtures and a compact manifest."""

    selected = protocol or registered_causal_motif_protocol()
    _validate_protocol(selected)
    output_dir = Path(out_dir)
    max_total_bytes = _mb_to_bytes(max_total_mb, "max_total_mb")
    manifest_path = output_dir / "manifest.json"
    partition_paths = {
        name: output_dir / f"{name}.npz" for name in PARTITION_NAMES
    }
    planned = [manifest_path, *partition_paths.values()]
    for path in planned:
        if path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to replace existing fixture artifact: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    partition_specs = {
        "train": (selected.train_items, selected.train_seed),
        "validation": (selected.validation_items, selected.validation_seed),
        "test": (selected.test_items, selected.test_seed),
    }
    partition_reports: dict[str, dict[str, Any]] = {}
    all_item_ids: set[str] = set()
    for split in PARTITION_NAMES:
        items, seed = partition_specs[split]
        arrays, metadata = make_causal_motif_partition(
            split=split,
            items=items,
            seed=seed,
            protocol=selected,
        )
        item_ids = {str(value) for value in arrays["item_ids"].tolist()}
        if all_item_ids.intersection(item_ids):
            raise RuntimeError("causal motif item IDs overlap across partitions")
        all_item_ids.update(item_ids)
        save_causal_motif_partition(
            partition_paths[split], arrays=arrays, metadata=metadata
        )
        partition_reports[split] = _partition_report(
            partition_paths[split], arrays=arrays, metadata=metadata
        )

    partition_bytes = sum(
        int(report["bytes"]) for report in partition_reports.values()
    )
    registered = registered_causal_motif_protocol()
    manifest: dict[str, Any] = {
        "schema": {
            "name": CAUSAL_MOTIF_MANIFEST_SCHEMA_NAME,
            "version": CAUSAL_MOTIF_MANIFEST_SCHEMA_VERSION,
        },
        "proof_posture": CAUSAL_MOTIF_PROOF_POSTURE,
        "registered_protocol_match": selected == registered,
        "protocol": selected.to_dict(),
        "protocol_sha256": selected.protocol_sha256,
        "partitions": partition_reports,
        "access_contract": {
            "physical_partition_files": True,
            "model_selection_partitions": ["train", "validation"],
            "test_open_after_checkpoint_freeze_only": True,
            "test_semantic_open_count_allowed": 1,
        },
        "claim_boundaries": [
            "Synthetic motif states are not neural or text labels.",
            "Fixture separation enables an auditable test-access boundary.",
            "No MEG, EEG, raw recording, decoder, or network access occurs.",
        ],
        "warnings": [
            "synthetic_motif_fixture_not_real_neural_data",
            "motif_task_is_intentionally_small_and_supervised",
            "no_text_decoder_or_end_to_end_latency_claim",
        ],
        "artifacts": {
            "manifest_path": str(manifest_path),
            "partition_bytes": partition_bytes,
            "manifest_bytes": 0,
            "total_fixture_bytes": partition_bytes,
            "max_total_bytes": max_total_bytes,
        },
    }
    manifest_text = _stable_manifest_json(manifest)
    total_bytes = partition_bytes + len(manifest_text.encode("utf-8"))
    if total_bytes > max_total_bytes:
        raise ValueError(
            f"fixture artifacts need {total_bytes} bytes, exceeding cap {max_total_bytes}"
        )
    manifest_path.write_text(manifest_text, encoding="utf-8")
    return manifest


def make_causal_motif_partition(
    *,
    split: str,
    items: int,
    seed: int,
    protocol: CausalMotifProtocol,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate one deterministic physical partition with aligned frame labels."""

    _validate_protocol(protocol)
    if split not in PARTITION_NAMES:
        raise ValueError(f"split must be one of: {', '.join(PARTITION_NAMES)}")
    if items < 1 or items > 4096:
        raise ValueError("items must be between 1 and 4096")
    np = _require_numpy()
    rng = np.random.Generator(np.random.PCG64(int(seed)))
    signals = np.zeros(
        (items, protocol.n_channels, protocol.max_timepoints), dtype="float32"
    )
    input_lengths = np.zeros(items, dtype="int32")
    sample_labels = np.full(
        (items, protocol.max_timepoints), -1, dtype="int16"
    )
    frame_labels = np.full((items, protocol.max_frames), -1, dtype="int16")
    frame_lengths = np.zeros(items, dtype="int32")
    motif_sequences = np.full(
        (items, protocol.max_motifs), -1, dtype="int16"
    )
    motif_lengths = np.zeros(items, dtype="int32")
    item_ids = np.asarray(
        [f"{split}-{seed}-{index:04d}" for index in range(items)], dtype="U"
    )

    base_classes = np.arange(1, protocol.n_classes, dtype="int16")
    for item_index in range(items):
        motif_count = int(
            rng.integers(protocol.min_motifs, protocol.max_motifs + 1)
        )
        base = base_classes.copy()
        rng.shuffle(base)
        extras = rng.integers(
            1,
            protocol.n_classes,
            size=motif_count - protocol.n_motif_classes,
            dtype="int16",
        )
        sequence = np.concatenate([base, extras])
        rng.shuffle(sequence)
        length = (
            protocol.lead_width
            + motif_count * protocol.motif_width
            + (motif_count - 1) * protocol.gap_width
            + protocol.tail_width
        )
        row = rng.normal(
            0.0, protocol.noise_std, size=(protocol.n_channels, length)
        ).astype("float32")
        labels = np.zeros(length, dtype="int16")
        cursor = protocol.lead_width
        for motif_index, motif_value in enumerate(sequence.tolist()):
            motif = int(motif_value)
            channel = motif - 1
            row[channel, cursor : cursor + protocol.motif_width] += (
                protocol.motif_amplitude
            )
            adjacent = (channel + 1) % protocol.n_channels
            row[adjacent, cursor : cursor + protocol.motif_width] += (
                protocol.adjacent_amplitude
            )
            labels[cursor : cursor + protocol.motif_width] = motif
            cursor += protocol.motif_width
            if motif_index < motif_count - 1:
                cursor += protocol.gap_width
        gains = rng.uniform(
            protocol.gain_min, protocol.gain_max, size=(protocol.n_channels, 1)
        ).astype("float32")
        offsets = rng.normal(
            0.0, protocol.offset_std, size=(protocol.n_channels, 1)
        ).astype("float32")
        row = row * gains + offsets

        starts = np.arange(
            0,
            length - protocol.kernel_size + 1,
            protocol.stride,
            dtype="int32",
        )
        labels_at_frame_end = labels[starts + protocol.kernel_size - 1]
        signals[item_index, :, :length] = row
        input_lengths[item_index] = length
        sample_labels[item_index, :length] = labels
        frame_labels[item_index, : len(starts)] = labels_at_frame_end
        frame_lengths[item_index] = len(starts)
        motif_sequences[item_index, :motif_count] = sequence
        motif_lengths[item_index] = motif_count

    arrays = {
        "signals": signals,
        "input_lengths": input_lengths,
        "sample_labels": sample_labels,
        "frame_labels": frame_labels,
        "frame_lengths": frame_lengths,
        "item_ids": item_ids,
        "motif_sequences": motif_sequences,
        "motif_lengths": motif_lengths,
    }
    metadata = {
        "schema": {
            "name": CAUSAL_MOTIF_SCHEMA_NAME,
            "version": CAUSAL_MOTIF_SCHEMA_VERSION,
        },
        "kind": "synthetic_causal_motif_frames",
        "proof_posture": CAUSAL_MOTIF_PROOF_POSTURE,
        "split": split,
        "seed": int(seed),
        "protocol": protocol.to_dict(),
        "protocol_sha256": protocol.protocol_sha256,
        "label_semantics": {
            "background": 0,
            "motifs": list(range(1, protocol.n_classes)),
            "padding": -1,
            "frame_reference": "final_sample_of_complete_causal_frame",
        },
        "warnings": [
            "synthetic_motif_fixture_not_real_neural_data",
            "frame_labels_are_generation_ground_truth",
            "no_text_or_language_target_stored",
        ],
    }
    _validate_partition_arrays(arrays, metadata)
    return arrays, metadata


def save_causal_motif_partition(
    path: str | Path,
    *,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> None:
    """Validate and save one inspectable compressed partition."""

    np = _require_numpy()
    normalized_arrays = {name: np.asarray(value) for name, value in arrays.items()}
    normalized_metadata = dict(metadata)
    _validate_partition_arrays(normalized_arrays, normalized_metadata)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        **normalized_arrays,
        metadata=json.dumps(normalized_metadata, sort_keys=True),
    )


def load_causal_motif_partition(
    path: str | Path,
    *,
    expected: Mapping[str, Any] | None = None,
) -> LoadedCausalMotifPartition:
    """Read one partition file once, then validate arrays and manifest binding."""

    np = _require_numpy()
    partition_path = Path(path)
    payload = partition_path.read_bytes()
    if expected is not None:
        expected_bytes = int(expected.get("bytes", -1))
        if expected_bytes != len(payload):
            raise ValueError("causal motif partition byte count does not match manifest")
        if str(expected.get("sha256")) != _sha256_bytes(payload):
            raise ValueError("causal motif partition hash does not match manifest")
    required = _required_array_names()
    expected_members = required | {"metadata"}
    with np.load(io.BytesIO(payload), allow_pickle=False) as data:
        members = set(data.files)
        missing = sorted(expected_members - members)
        if missing:
            raise ValueError(f"causal motif partition is missing members: {missing}")
        unexpected = sorted(members - expected_members)
        if unexpected:
            raise ValueError(f"causal motif partition has unexpected members: {unexpected}")
        arrays = {name: data[name].copy() for name in required}
        metadata = _decode_metadata(data["metadata"])
    _validate_partition_arrays(arrays, metadata)
    if expected is not None:
        actual = _partition_content_summary(arrays=arrays, metadata=metadata)
        for name in (
            "schema",
            "split",
            "items",
            "signals_shape",
            "signals_dtype",
            "valid_samples",
            "valid_frames",
            "n_classes",
            "class_support",
            "item_ids_sha256",
            "seed",
            "protocol_sha256",
        ):
            if expected.get(name) != actual[name]:
                raise ValueError(
                    f"causal motif partition {name} does not match manifest"
                )
        if Path(str(expected.get("path"))).name != partition_path.name:
            raise ValueError("causal motif partition path does not match manifest")
    return LoadedCausalMotifPartition(
        path=str(partition_path),
        split=str(metadata["split"]),
        metadata=metadata,
        **arrays,
    )


def load_causal_motif_manifest(
    path: str | Path,
    *,
    require_registered_protocol: bool = True,
) -> dict[str, Any]:
    """Validate the compact manifest without opening any partition NPZ."""

    manifest_path = Path(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("causal motif manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("causal motif manifest must be an object")
    schema = manifest.get("schema") or {}
    if schema.get("name") != CAUSAL_MOTIF_MANIFEST_SCHEMA_NAME:
        raise ValueError("unsupported causal motif manifest schema")
    if schema.get("version") != CAUSAL_MOTIF_MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported causal motif manifest version")
    if manifest.get("proof_posture") != CAUSAL_MOTIF_PROOF_POSTURE:
        raise ValueError("causal motif manifest proof posture is invalid")
    protocol = manifest.get("protocol")
    if not isinstance(protocol, dict):
        raise ValueError("causal motif manifest protocol must be an object")
    if manifest.get("protocol_sha256") != _sha256_json(protocol):
        raise ValueError("causal motif manifest protocol hash mismatch")
    try:
        parsed_protocol = CausalMotifProtocol(**protocol)
    except (TypeError, ValueError) as exc:
        raise ValueError("causal motif manifest protocol fields are invalid") from exc
    _validate_protocol(parsed_protocol)
    registered = registered_causal_motif_protocol()
    registered_match = parsed_protocol == registered
    if manifest.get("registered_protocol_match") is not registered_match:
        raise ValueError("causal motif registered-protocol flag is inconsistent")
    if require_registered_protocol and not registered_match:
        raise ValueError("causal motif manifest does not match the registered protocol")
    partitions = manifest.get("partitions")
    if not isinstance(partitions, dict) or set(partitions) != set(PARTITION_NAMES):
        raise ValueError("causal motif manifest must bind train, validation, and test")
    partition_specs = {
        "train": (parsed_protocol.train_items, parsed_protocol.train_seed),
        "validation": (
            parsed_protocol.validation_items,
            parsed_protocol.validation_seed,
        ),
        "test": (parsed_protocol.test_items, parsed_protocol.test_seed),
    }
    paths: set[Path] = set()
    for split in PARTITION_NAMES:
        summary = partitions[split]
        if not isinstance(summary, dict) or summary.get("split") != split:
            raise ValueError(f"invalid causal motif manifest summary for {split}")
        relative = Path(str(summary.get("path") or ""))
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("causal motif manifest partition paths must be local and relative")
        if relative in paths:
            raise ValueError("causal motif manifest partition paths must be unique")
        paths.add(relative)
        items, seed = partition_specs[split]
        expected_values = {
            "schema": {
                "name": CAUSAL_MOTIF_SCHEMA_NAME,
                "version": CAUSAL_MOTIF_SCHEMA_VERSION,
            },
            "items": items,
            "signals_shape": [
                items,
                parsed_protocol.n_channels,
                parsed_protocol.max_timepoints,
            ],
            "signals_dtype": "float32",
            "n_classes": parsed_protocol.n_classes,
            "seed": seed,
            "protocol_sha256": parsed_protocol.protocol_sha256,
        }
        for name, expected_value in expected_values.items():
            if summary.get(name) != expected_value:
                raise ValueError(
                    f"causal motif manifest {split} {name} is inconsistent"
                )
        for name in ("bytes", "valid_samples", "valid_frames"):
            value = summary.get(name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"causal motif manifest {split} {name} is invalid")
        if int(summary["valid_samples"]) > items * parsed_protocol.max_timepoints:
            raise ValueError(f"causal motif manifest {split} sample count is invalid")
        if int(summary["valid_frames"]) > items * parsed_protocol.max_frames:
            raise ValueError(f"causal motif manifest {split} frame count is invalid")
        support = summary.get("class_support")
        if (
            not isinstance(support, list)
            or len(support) != parsed_protocol.n_classes
            or any(not isinstance(value, int) or value < 1 for value in support)
            or sum(support) != int(summary["valid_frames"])
        ):
            raise ValueError(f"causal motif manifest {split} class support is invalid")
        for name in ("sha256", "item_ids_sha256"):
            if not _is_sha256(summary.get(name)):
                raise ValueError(f"causal motif manifest {split} {name} is invalid")
    access_contract = manifest.get("access_contract")
    expected_access_contract = {
        "physical_partition_files": True,
        "model_selection_partitions": ["train", "validation"],
        "test_open_after_checkpoint_freeze_only": True,
        "test_semantic_open_count_allowed": 1,
    }
    if access_contract != expected_access_contract:
        raise ValueError("causal motif manifest access contract is invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("causal motif manifest artifact accounting is missing")
    manifest_bytes = int(manifest_path.stat().st_size)
    partition_bytes = sum(int(partitions[name]["bytes"]) for name in PARTITION_NAMES)
    total_bytes = partition_bytes + manifest_bytes
    if (
        artifacts.get("manifest_bytes") != manifest_bytes
        or artifacts.get("partition_bytes") != partition_bytes
        or artifacts.get("total_fixture_bytes") != total_bytes
        or not isinstance(artifacts.get("max_total_bytes"), int)
        or int(artifacts["max_total_bytes"]) < total_bytes
    ):
        raise ValueError("causal motif manifest artifact byte accounting is invalid")
    return manifest


def resolve_manifest_partition_path(
    manifest_path: str | Path, manifest: Mapping[str, Any], split: str
) -> Path:
    if split not in PARTITION_NAMES:
        raise ValueError(f"unknown causal motif partition: {split}")
    relative = Path(str(manifest["partitions"][split]["path"]))
    root = Path(manifest_path).parent.resolve()
    resolved = (root / relative).resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError("causal motif partition resolves outside the fixture directory")
    return resolved


def _partition_report(
    path: Path, *, arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": _file_sha256(path),
        "bytes": int(path.stat().st_size),
        **_partition_content_summary(arrays=arrays, metadata=metadata),
    }


def _partition_content_summary(
    *, arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> dict[str, Any]:
    np = _require_numpy()
    valid_frame_labels = np.concatenate(
        [
            arrays["frame_labels"][index, : int(length)]
            for index, length in enumerate(arrays["frame_lengths"].tolist())
        ]
    )
    supports = np.bincount(
        valid_frame_labels.astype("int64"),
        minlength=int(metadata["protocol"]["n_motif_classes"]) + 1,
    )
    return {
        "schema": dict(metadata["schema"]),
        "split": str(metadata["split"]),
        "items": int(arrays["signals"].shape[0]),
        "signals_shape": [int(value) for value in arrays["signals"].shape],
        "signals_dtype": str(arrays["signals"].dtype),
        "valid_samples": int(arrays["input_lengths"].sum()),
        "valid_frames": int(arrays["frame_lengths"].sum()),
        "n_classes": int(metadata["protocol"]["n_motif_classes"]) + 1,
        "class_support": [int(value) for value in supports.tolist()],
        "item_ids_sha256": _sha256_json(arrays["item_ids"].tolist()),
        "seed": int(metadata["seed"]),
        "protocol_sha256": str(metadata["protocol_sha256"]),
    }


def _validate_protocol(protocol: CausalMotifProtocol) -> None:
    integer_values = {
        "train_items": protocol.train_items,
        "validation_items": protocol.validation_items,
        "test_items": protocol.test_items,
        "n_channels": protocol.n_channels,
        "n_motif_classes": protocol.n_motif_classes,
        "kernel_size": protocol.kernel_size,
        "stride": protocol.stride,
        "min_motifs": protocol.min_motifs,
        "max_motifs": protocol.max_motifs,
        "motif_width": protocol.motif_width,
        "gap_width": protocol.gap_width,
        "lead_width": protocol.lead_width,
        "tail_width": protocol.tail_width,
    }
    if any(int(value) < 1 for value in integer_values.values()):
        raise ValueError("causal motif integer protocol values must be positive")
    if protocol.n_channels != protocol.n_motif_classes:
        raise ValueError("causal motif protocol requires one channel per motif class")
    if protocol.min_motifs < protocol.n_motif_classes:
        raise ValueError("every item must contain every motif class")
    if protocol.max_motifs < protocol.min_motifs:
        raise ValueError("max_motifs must be at least min_motifs")
    if protocol.stride > protocol.kernel_size:
        raise ValueError("stride must not exceed kernel_size")
    if protocol.max_timepoints > 65536 or protocol.total_items > 4096:
        raise ValueError("causal motif protocol exceeds fixture safety bounds")
    finite_values = {
        "sampling_rate_hz": protocol.sampling_rate_hz,
        "motif_amplitude": protocol.motif_amplitude,
        "adjacent_amplitude": protocol.adjacent_amplitude,
        "noise_std": protocol.noise_std,
        "gain_min": protocol.gain_min,
        "gain_max": protocol.gain_max,
        "offset_std": protocol.offset_std,
    }
    if any(not math.isfinite(value) or value <= 0 for value in finite_values.values()):
        raise ValueError("causal motif floating protocol values must be finite and positive")
    if protocol.gain_max < protocol.gain_min:
        raise ValueError("gain_max must be at least gain_min")


def _validate_partition_arrays(
    arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> None:
    np = _require_numpy()
    missing = sorted(_required_array_names() - set(arrays))
    if missing:
        raise ValueError(f"causal motif arrays are missing: {missing}")
    schema = metadata.get("schema") or {}
    if schema.get("name") != CAUSAL_MOTIF_SCHEMA_NAME:
        raise ValueError("unsupported causal motif partition schema")
    if schema.get("version") != CAUSAL_MOTIF_SCHEMA_VERSION:
        raise ValueError("unsupported causal motif partition version")
    if metadata.get("kind") != "synthetic_causal_motif_frames":
        raise ValueError("causal motif partition kind is invalid")
    if metadata.get("proof_posture") != CAUSAL_MOTIF_PROOF_POSTURE:
        raise ValueError("causal motif partition proof posture is invalid")
    split = str(metadata.get("split") or "")
    if split not in PARTITION_NAMES:
        raise ValueError("causal motif metadata split is invalid")
    protocol_values = metadata.get("protocol")
    if not isinstance(protocol_values, dict):
        raise ValueError("causal motif metadata protocol must be an object")
    if metadata.get("protocol_sha256") != _sha256_json(protocol_values):
        raise ValueError("causal motif metadata protocol hash mismatch")
    try:
        protocol = CausalMotifProtocol(**protocol_values)
    except (TypeError, ValueError) as exc:
        raise ValueError("causal motif metadata protocol fields are invalid") from exc
    _validate_protocol(protocol)
    expected_seed = int(getattr(protocol, f"{split}_seed"))
    if metadata.get("seed") != expected_seed:
        raise ValueError("causal motif partition seed does not match its protocol")
    signals = np.asarray(arrays["signals"])
    if (
        signals.ndim != 3
        or min(signals.shape) < 1
        or signals.dtype != np.dtype("float32")
        or not np.isfinite(signals).all()
    ):
        raise ValueError("signals must be finite nonempty float32 [items,channels,time]")
    n_items, n_channels, max_timepoints = signals.shape
    if n_channels != protocol.n_channels or max_timepoints != protocol.max_timepoints:
        raise ValueError("signal geometry does not match the causal motif protocol")
    input_lengths = np.asarray(arrays["input_lengths"])
    frame_lengths = np.asarray(arrays["frame_lengths"])
    motif_lengths = np.asarray(arrays["motif_lengths"])
    for name, value in (
        ("input_lengths", input_lengths),
        ("frame_lengths", frame_lengths),
        ("motif_lengths", motif_lengths),
    ):
        if value.shape != (n_items,) or not np.issubdtype(value.dtype, np.integer):
            raise ValueError(f"{name} must be an integer vector with one row per item")
    sample_labels = np.asarray(arrays["sample_labels"])
    frame_labels = np.asarray(arrays["frame_labels"])
    motif_sequences = np.asarray(arrays["motif_sequences"])
    item_ids = np.asarray(arrays["item_ids"])
    for name, value in (
        ("sample_labels", sample_labels),
        ("frame_labels", frame_labels),
        ("motif_sequences", motif_sequences),
    ):
        if not np.issubdtype(value.dtype, np.integer):
            raise ValueError(f"{name} must use an integer dtype")
    if sample_labels.shape != (n_items, max_timepoints):
        raise ValueError("sample_labels shape must match item/time dimensions")
    if frame_labels.shape != (n_items, protocol.max_frames):
        raise ValueError("frame_labels must match the protocol frame grid")
    if motif_sequences.shape != (n_items, protocol.max_motifs):
        raise ValueError("motif_sequences must match the protocol motif bound")
    if (
        item_ids.shape != (n_items,)
        or item_ids.dtype.kind != "U"
        or len(set(item_ids.tolist())) != n_items
    ):
        raise ValueError("item_ids must be a unique vector with one row per item")
    n_classes = int(protocol_values["n_motif_classes"]) + 1
    kernel_size = int(protocol_values["kernel_size"])
    stride = int(protocol_values["stride"])
    expected_item_ids = [
        f"{split}-{expected_seed}-{index:04d}" for index in range(n_items)
    ]
    if item_ids.tolist() != expected_item_ids:
        raise ValueError("item IDs do not match split, seed, and row order")
    for index in range(n_items):
        length = int(input_lengths[index])
        if length < kernel_size or length > max_timepoints:
            raise ValueError("input_lengths fall outside the signal array")
        expected_frames = 1 + (length - kernel_size) // stride
        if int(frame_lengths[index]) != expected_frames:
            raise ValueError("frame_lengths do not match kernel/stride geometry")
        labels = sample_labels[index, :length]
        if (labels < 0).any() or (labels >= n_classes).any():
            raise ValueError("valid sample labels fall outside the class vocabulary")
        starts = np.arange(expected_frames, dtype="int64") * stride
        expected = labels[starts + kernel_size - 1]
        if not np.array_equal(frame_labels[index, :expected_frames], expected):
            raise ValueError("frame labels do not match final-sample semantics")
        if not (frame_labels[index, expected_frames:] == -1).all():
            raise ValueError("frame-label padding must be -1")
        if not (sample_labels[index, length:] == -1).all():
            raise ValueError("sample-label padding must be -1")
        if not np.array_equal(
            signals[index, :, length:], np.zeros_like(signals[index, :, length:])
        ):
            raise ValueError("signal padding must be exactly zero")
        motif_count = int(motif_lengths[index])
        if motif_count < protocol.min_motifs or motif_count > protocol.max_motifs:
            raise ValueError("motif count falls outside the protocol")
        valid_motifs = motif_sequences[index, :motif_count]
        if set(valid_motifs.tolist()) != set(range(1, n_classes)):
            raise ValueError("every item must contain every motif class")
        if not (motif_sequences[index, motif_count:] == -1).all():
            raise ValueError("motif sequence padding must be -1")
        expected_length = (
            protocol.lead_width
            + motif_count * protocol.motif_width
            + (motif_count - 1) * protocol.gap_width
            + protocol.tail_width
        )
        if length != expected_length:
            raise ValueError("input length does not match the motif sequence")
        expected_sample_labels = np.zeros(length, dtype=sample_labels.dtype)
        cursor = protocol.lead_width
        for motif_index, motif_value in enumerate(valid_motifs.tolist()):
            expected_sample_labels[
                cursor : cursor + protocol.motif_width
            ] = int(motif_value)
            cursor += protocol.motif_width
            if motif_index < motif_count - 1:
                cursor += protocol.gap_width
        if not np.array_equal(labels, expected_sample_labels):
            raise ValueError("sample labels do not match the registered motif sequence")
        if not str(item_ids[index]).startswith(f"{split}-"):
            raise ValueError("item ID does not preserve physical partition identity")


def _required_array_names() -> set[str]:
    return {
        "signals",
        "input_lengths",
        "sample_labels",
        "frame_labels",
        "frame_lengths",
        "item_ids",
        "motif_sequences",
        "motif_lengths",
    }


def _stable_manifest_json(manifest: dict[str, Any]) -> str:
    for _ in range(12):
        text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        size = len(text.encode("utf-8"))
        total = int(manifest["artifacts"]["partition_bytes"]) + size
        if (
            manifest["artifacts"]["manifest_bytes"] == size
            and manifest["artifacts"]["total_fixture_bytes"] == total
        ):
            return text
        manifest["artifacts"]["manifest_bytes"] = size
        manifest["artifacts"]["total_fixture_bytes"] = total
    raise RuntimeError("causal motif manifest byte count did not converge")


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        metadata = json.loads(str(raw))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("causal motif metadata is not valid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("causal motif metadata must decode to an object")
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


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: object) -> bool:
    text = str(value)
    return len(text) == 64 and all(character in "0123456789abcdef" for character in text)


def _mb_to_bytes(value: float, name: str) -> int:
    try:
        normalized = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be finite and positive") from exc
    if not math.isfinite(normalized) or normalized <= 0:
        raise ValueError(f"{name} must be finite and positive")
    return int(normalized * 1024 * 1024)


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Causal motif fixtures require NumPy: `pip install numpy`.") from exc
    return np
