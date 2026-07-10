"""Fresh bounded synthetic symbol streams for the preregistered Loop 23 gate."""

from __future__ import annotations

import hashlib
import io
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


CTC_SYMBOL_SCHEMA_NAME = "b2q-ctc-symbol-stream-fixture"
CTC_SYMBOL_SCHEMA_VERSION = 0
CTC_SYMBOL_MANIFEST_SCHEMA_NAME = "b2q-ctc-symbol-stream-manifest"
CTC_SYMBOL_MANIFEST_SCHEMA_VERSION = 0
CTC_SYMBOL_PROOF_POSTURE = "synthetic_ctc_symbol_stream_only"
CTC_SYMBOL_NAMES = ("A", "B", "C", "D", "E")
PARTITION_NAMES = ("train", "validation", "test")
TARGET_ONLY_MEMBERS = (
    "metadata",
    "target_token_ids",
    "target_lengths",
    "item_ids",
)
FULL_ARRAY_MEMBERS = (
    "signals",
    "input_lengths",
    "sample_labels",
    "frame_labels",
    "frame_lengths",
    "target_token_ids",
    "target_lengths",
    "motif_start_samples",
    "motif_end_samples",
    "item_ids",
)


@dataclass(frozen=True)
class CTCSymbolStreamProtocol:
    """Complete generation protocol frozen before the registered test exists."""

    train_items: int = 48
    validation_items: int = 8
    test_items: int = 8
    n_channels: int = 5
    n_symbols: int = 5
    sampling_rate_hz: float = 100.0
    kernel_size: int = 16
    stride: int = 4
    min_target_length: int = 6
    max_target_length: int = 8
    motif_width: int = 8
    gap_width: int = 4
    lead_width: int = 16
    tail_width: int = 8
    motif_amplitude: float = 1.5
    adjacent_amplitude: float = 0.25
    noise_std: float = 0.10
    gain_min: float = 0.85
    gain_max: float = 1.15
    offset_std: float = 0.03
    train_seed: int = 2301
    validation_seed: int = 2302
    test_seed: int = 2303

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

    @property
    def total_items(self) -> int:
        return self.train_items + self.validation_items + self.test_items

    @property
    def n_classes(self) -> int:
        return self.n_symbols + 1

    @property
    def max_timepoints(self) -> int:
        return (
            self.lead_width
            + self.max_target_length * self.motif_width
            + (self.max_target_length - 1) * self.gap_width
            + self.tail_width
        )

    @property
    def max_frames(self) -> int:
        return 1 + (self.max_timepoints - self.kernel_size) // self.stride

    @property
    def protocol_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class LoadedCTCSymbolPartition:
    """Validated target-only or full partition with explicit opened members."""

    path: str
    split: str
    target_token_ids: Any
    target_lengths: Any
    item_ids: Any
    metadata: dict[str, Any]
    opened_members: tuple[str, ...]
    signals: Any | None = None
    input_lengths: Any | None = None
    sample_labels: Any | None = None
    frame_labels: Any | None = None
    frame_lengths: Any | None = None
    motif_start_samples: Any | None = None
    motif_end_samples: Any | None = None


def registered_ctc_symbol_stream_protocol() -> CTCSymbolStreamProtocol:
    return CTCSymbolStreamProtocol()


def prepare_ctc_symbol_stream_fixture(
    out_dir: str | Path,
    *,
    protocol: CTCSymbolStreamProtocol | None = None,
    max_total_mb: float = 1.0,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create three physical partitions and one compact hash-bound manifest."""

    selected = protocol or registered_ctc_symbol_stream_protocol()
    _validate_protocol(selected)
    output_dir = Path(out_dir)
    max_total_bytes = _mb_to_bytes(max_total_mb, "max_total_mb")
    manifest_path = output_dir / "manifest.json"
    partition_paths = {
        split: output_dir / f"{split}.npz" for split in PARTITION_NAMES
    }
    for path in (manifest_path, *partition_paths.values()):
        if path.exists() and not overwrite:
            raise FileExistsError(f"Refusing to replace Loop 23 fixture artifact: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)

    specs = {
        "train": (selected.train_items, selected.train_seed),
        "validation": (selected.validation_items, selected.validation_seed),
        "test": (selected.test_items, selected.test_seed),
    }
    summaries: dict[str, dict[str, Any]] = {}
    all_item_ids: set[str] = set()
    for split in PARTITION_NAMES:
        items, seed = specs[split]
        arrays, metadata = make_ctc_symbol_stream_partition(
            split=split,
            items=items,
            seed=seed,
            protocol=selected,
        )
        item_ids = {str(value) for value in arrays["item_ids"].tolist()}
        if all_item_ids.intersection(item_ids):
            raise RuntimeError("Loop 23 item IDs overlap across partitions")
        all_item_ids.update(item_ids)
        save_ctc_symbol_stream_partition(
            partition_paths[split], arrays=arrays, metadata=metadata
        )
        summaries[split] = _partition_report(
            partition_paths[split], arrays=arrays, metadata=metadata
        )

    partition_bytes = sum(int(summary["bytes"]) for summary in summaries.values())
    registered = registered_ctc_symbol_stream_protocol()
    manifest: dict[str, Any] = {
        "schema": {
            "name": CTC_SYMBOL_MANIFEST_SCHEMA_NAME,
            "version": CTC_SYMBOL_MANIFEST_SCHEMA_VERSION,
        },
        "proof_posture": CTC_SYMBOL_PROOF_POSTURE,
        "registered_protocol_match": selected == registered,
        "protocol": selected.to_dict(),
        "protocol_sha256": selected.protocol_sha256,
        "symbols": {str(index + 1): value for index, value in enumerate(CTC_SYMBOL_NAMES)},
        "blank_id": 0,
        "partitions": summaries,
        "access_contract": {
            "train_open_mode": "targets_only",
            "validation_open_mode": "full_once",
            "test_open_after_validation_only": True,
            "test_semantic_open_count_allowed": 1,
        },
        "warnings": [
            "synthetic_symbols_are_not_natural_text",
            "frozen_probe_was_not_trained_with_ctc_loss",
            "fixture_does_not_establish_brain_decoding",
        ],
        "claim_boundaries": [
            "No real neural signal or observed holdout is stored.",
            "Synthetic CER is not natural-language CER or WER.",
            "Known item ends are not a live endpoint detector.",
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
    if int(manifest["artifacts"]["total_fixture_bytes"]) > max_total_bytes:
        raise ValueError("Loop 23 fixture exceeds the declared byte cap")
    manifest_path.write_text(manifest_text, encoding="utf-8")
    return manifest


def make_ctc_symbol_stream_partition(
    *,
    split: str,
    items: int,
    seed: int,
    protocol: CTCSymbolStreamProtocol,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate one partition with a guaranteed adjacent repeated target."""

    _validate_protocol(protocol)
    if split not in PARTITION_NAMES:
        raise ValueError(f"split must be one of: {', '.join(PARTITION_NAMES)}")
    if int(seed) != int(getattr(protocol, f"{split}_seed")):
        raise ValueError("partition seed must match the selected protocol")
    if items != int(getattr(protocol, f"{split}_items")):
        raise ValueError("partition item count must match the selected protocol")
    np = _require_numpy()
    rng = np.random.Generator(np.random.PCG64(seed))
    signals = np.zeros(
        (items, protocol.n_channels, protocol.max_timepoints), dtype="float32"
    )
    input_lengths = np.zeros(items, dtype="int32")
    sample_labels = np.full((items, protocol.max_timepoints), -1, dtype="int16")
    frame_labels = np.full((items, protocol.max_frames), -1, dtype="int16")
    frame_lengths = np.zeros(items, dtype="int32")
    target_token_ids = np.full(
        (items, protocol.max_target_length), -1, dtype="int16"
    )
    target_lengths = np.zeros(items, dtype="int32")
    motif_start_samples = np.full(
        (items, protocol.max_target_length), -1, dtype="int32"
    )
    motif_end_samples = np.full(
        (items, protocol.max_target_length), -1, dtype="int32"
    )
    item_ids = np.asarray(
        [f"{split}-{seed}-{index:04d}" for index in range(items)], dtype="U"
    )

    base_symbols = np.arange(1, protocol.n_symbols + 1, dtype="int16")
    for item_index in range(items):
        base = base_symbols.copy()
        rng.shuffle(base)
        duplicate_index = int(rng.integers(0, len(base)))
        sequence = np.insert(base, duplicate_index + 1, base[duplicate_index])
        target_length = int(
            rng.integers(protocol.min_target_length, protocol.max_target_length + 1)
        )
        extras = rng.integers(
            1,
            protocol.n_symbols + 1,
            size=target_length - len(sequence),
            dtype="int16",
        )
        sequence = np.concatenate([sequence, extras])
        length = (
            protocol.lead_width
            + target_length * protocol.motif_width
            + (target_length - 1) * protocol.gap_width
            + protocol.tail_width
        )
        row = rng.normal(
            0.0, protocol.noise_std, size=(protocol.n_channels, length)
        ).astype("float32")
        labels = np.zeros(length, dtype="int16")
        cursor = protocol.lead_width
        for target_index, symbol_value in enumerate(sequence.tolist()):
            symbol = int(symbol_value)
            channel = symbol - 1
            start = cursor
            end = start + protocol.motif_width
            row[channel, start:end] += protocol.motif_amplitude
            row[(channel + 1) % protocol.n_channels, start:end] += (
                protocol.adjacent_amplitude
            )
            labels[start:end] = symbol
            motif_start_samples[item_index, target_index] = start
            motif_end_samples[item_index, target_index] = end
            cursor = end
            if target_index < target_length - 1:
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

        signals[item_index, :, :length] = row
        input_lengths[item_index] = length
        sample_labels[item_index, :length] = labels
        frame_labels[item_index, : len(starts)] = labels[
            starts + protocol.kernel_size - 1
        ]
        frame_lengths[item_index] = len(starts)
        target_token_ids[item_index, :target_length] = sequence
        target_lengths[item_index] = target_length

    arrays = {
        "signals": signals,
        "input_lengths": input_lengths,
        "sample_labels": sample_labels,
        "frame_labels": frame_labels,
        "frame_lengths": frame_lengths,
        "target_token_ids": target_token_ids,
        "target_lengths": target_lengths,
        "motif_start_samples": motif_start_samples,
        "motif_end_samples": motif_end_samples,
        "item_ids": item_ids,
    }
    metadata = {
        "schema": {
            "name": CTC_SYMBOL_SCHEMA_NAME,
            "version": CTC_SYMBOL_SCHEMA_VERSION,
        },
        "kind": "synthetic_ctc_symbol_stream",
        "proof_posture": CTC_SYMBOL_PROOF_POSTURE,
        "split": split,
        "seed": seed,
        "protocol": protocol.to_dict(),
        "protocol_sha256": protocol.protocol_sha256,
        "blank_id": 0,
        "symbols": {str(index + 1): value for index, value in enumerate(CTC_SYMBOL_NAMES)},
        "target_semantics": "generated_symbol_sequence_not_natural_text",
        "warnings": [
            "synthetic_symbols_are_not_natural_text",
            "adjacent_repeat_requires_blank_separation",
            "no_real_neural_or_language_target",
        ],
    }
    _validate_full_arrays(arrays, metadata)
    return arrays, metadata


def save_ctc_symbol_stream_partition(
    path: str | Path,
    *,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> None:
    np = _require_numpy()
    normalized = {name: np.asarray(value) for name, value in arrays.items()}
    normalized_metadata = dict(metadata)
    _validate_full_arrays(normalized, normalized_metadata)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        output,
        **normalized,
        metadata=json.dumps(normalized_metadata, sort_keys=True),
    )


def load_ctc_symbol_stream_partition(
    path: str | Path,
    *,
    expected: Mapping[str, Any] | None = None,
    access_mode: str = "full",
) -> LoadedCTCSymbolPartition:
    """Read one file once and open either target-only or all array members."""

    if access_mode not in {"targets-only", "full"}:
        raise ValueError("access_mode must be targets-only or full")
    np = _require_numpy()
    partition_path = Path(path)
    payload = partition_path.read_bytes()
    if expected is not None:
        if int(expected.get("bytes", -1)) != len(payload):
            raise ValueError("Loop 23 partition byte count does not match manifest")
        if str(expected.get("sha256")) != _sha256_bytes(payload):
            raise ValueError("Loop 23 partition hash does not match manifest")
    required_members = set(FULL_ARRAY_MEMBERS) | {"metadata"}
    opened_names = TARGET_ONLY_MEMBERS if access_mode == "targets-only" else (
        "metadata",
        *FULL_ARRAY_MEMBERS,
    )
    with np.load(io.BytesIO(payload), allow_pickle=False) as data:
        members = set(data.files)
        missing = sorted(required_members - members)
        unexpected = sorted(members - required_members)
        if missing:
            raise ValueError(f"Loop 23 partition is missing members: {missing}")
        if unexpected:
            raise ValueError(f"Loop 23 partition has unexpected members: {unexpected}")
        opened = {
            name: (_decode_metadata(data[name]) if name == "metadata" else data[name].copy())
            for name in opened_names
        }
    metadata = opened.pop("metadata")
    target_arrays = {
        name: opened[name]
        for name in ("target_token_ids", "target_lengths", "item_ids")
    }
    _validate_target_arrays(target_arrays, metadata)
    if access_mode == "full":
        _validate_full_arrays(opened, metadata)
    actual = _partition_content_summary(opened, metadata, full=access_mode == "full")
    if expected is not None:
        fields = (
            "schema",
            "split",
            "items",
            "target_tokens",
            "target_length_range",
            "repeated_pair_count",
            "target_symbol_support",
            "item_ids_sha256",
            "target_ids_sha256",
            "seed",
            "protocol_sha256",
        )
        if access_mode == "full":
            fields += (
                "signals_shape",
                "signals_dtype",
                "valid_samples",
                "valid_frames",
                "frame_class_support",
            )
        for name in fields:
            if expected.get(name) != actual[name]:
                raise ValueError(f"Loop 23 partition {name} does not match manifest")
        if Path(str(expected.get("path"))).name != partition_path.name:
            raise ValueError("Loop 23 partition path does not match manifest")
    return LoadedCTCSymbolPartition(
        path=str(partition_path),
        split=str(metadata["split"]),
        target_token_ids=target_arrays["target_token_ids"],
        target_lengths=target_arrays["target_lengths"],
        item_ids=target_arrays["item_ids"],
        metadata=metadata,
        opened_members=tuple(opened_names),
        signals=opened.get("signals"),
        input_lengths=opened.get("input_lengths"),
        sample_labels=opened.get("sample_labels"),
        frame_labels=opened.get("frame_labels"),
        frame_lengths=opened.get("frame_lengths"),
        motif_start_samples=opened.get("motif_start_samples"),
        motif_end_samples=opened.get("motif_end_samples"),
    )


def load_ctc_symbol_stream_manifest(
    path: str | Path,
    *,
    require_registered_protocol: bool = True,
) -> dict[str, Any]:
    """Validate only the compact manifest; do not touch partition files."""

    manifest_path = Path(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Loop 23 manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("Loop 23 manifest must be an object")
    schema = manifest.get("schema") or {}
    if schema != {
        "name": CTC_SYMBOL_MANIFEST_SCHEMA_NAME,
        "version": CTC_SYMBOL_MANIFEST_SCHEMA_VERSION,
    }:
        raise ValueError("unsupported Loop 23 manifest schema")
    if manifest.get("proof_posture") != CTC_SYMBOL_PROOF_POSTURE:
        raise ValueError("Loop 23 manifest proof posture is invalid")
    protocol_values = manifest.get("protocol")
    if not isinstance(protocol_values, dict):
        raise ValueError("Loop 23 manifest protocol must be an object")
    try:
        protocol = CTCSymbolStreamProtocol(**protocol_values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Loop 23 manifest protocol fields are invalid") from exc
    _validate_protocol(protocol)
    if manifest.get("protocol_sha256") != protocol.protocol_sha256:
        raise ValueError("Loop 23 manifest protocol hash mismatch")
    registered_match = protocol == registered_ctc_symbol_stream_protocol()
    if manifest.get("registered_protocol_match") is not registered_match:
        raise ValueError("Loop 23 registered-protocol flag is inconsistent")
    if require_registered_protocol and not registered_match:
        raise ValueError("Loop 23 manifest does not match the registered protocol")
    if manifest.get("blank_id") != 0 or manifest.get("symbols") != {
        str(index + 1): value for index, value in enumerate(CTC_SYMBOL_NAMES)
    }:
        raise ValueError("Loop 23 manifest symbol vocabulary is invalid")
    partitions = manifest.get("partitions")
    if not isinstance(partitions, dict) or set(partitions) != set(PARTITION_NAMES):
        raise ValueError("Loop 23 manifest must bind all physical partitions")
    specs = {
        "train": (protocol.train_items, protocol.train_seed),
        "validation": (protocol.validation_items, protocol.validation_seed),
        "test": (protocol.test_items, protocol.test_seed),
    }
    paths: set[Path] = set()
    for split in PARTITION_NAMES:
        summary = partitions[split]
        if not isinstance(summary, dict) or summary.get("split") != split:
            raise ValueError(f"invalid Loop 23 manifest summary for {split}")
        relative = Path(str(summary.get("path") or ""))
        if relative.is_absolute() or ".." in relative.parts or relative in paths:
            raise ValueError("Loop 23 partition paths must be safe, relative, and unique")
        paths.add(relative)
        items, seed = specs[split]
        expected = {
            "schema": {"name": CTC_SYMBOL_SCHEMA_NAME, "version": 0},
            "items": items,
            "signals_shape": [items, protocol.n_channels, protocol.max_timepoints],
            "signals_dtype": "float32",
            "seed": seed,
            "protocol_sha256": protocol.protocol_sha256,
        }
        for name, value in expected.items():
            if summary.get(name) != value:
                raise ValueError(f"Loop 23 manifest {split} {name} is inconsistent")
        for name in (
            "bytes",
            "valid_samples",
            "valid_frames",
            "target_tokens",
            "repeated_pair_count",
        ):
            value = summary.get(name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"Loop 23 manifest {split} {name} is invalid")
        if int(summary["repeated_pair_count"]) < items:
            raise ValueError(f"Loop 23 manifest {split} lacks guaranteed repeats")
        observed_target_range = summary.get("target_length_range")
        if (
            not isinstance(observed_target_range, list)
            or len(observed_target_range) != 2
            or any(
                not isinstance(value, int) or isinstance(value, bool)
                for value in observed_target_range
            )
            or observed_target_range[0] < protocol.min_target_length
            or observed_target_range[1] > protocol.max_target_length
            or observed_target_range[0] > observed_target_range[1]
        ):
            raise ValueError(f"Loop 23 manifest {split} target lengths are invalid")
        for name, expected_length in (
            ("target_symbol_support", protocol.n_symbols),
            ("frame_class_support", protocol.n_classes),
        ):
            values = summary.get(name)
            if (
                not isinstance(values, list)
                or len(values) != expected_length
                or any(not isinstance(value, int) or value < 1 for value in values)
            ):
                raise ValueError(f"Loop 23 manifest {split} {name} is invalid")
        for name in ("sha256", "item_ids_sha256", "target_ids_sha256"):
            if not _is_sha256(summary.get(name)):
                raise ValueError(f"Loop 23 manifest {split} {name} is invalid")
    expected_access = {
        "train_open_mode": "targets_only",
        "validation_open_mode": "full_once",
        "test_open_after_validation_only": True,
        "test_semantic_open_count_allowed": 1,
    }
    if manifest.get("access_contract") != expected_access:
        raise ValueError("Loop 23 manifest access contract is invalid")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, dict):
        raise ValueError("Loop 23 manifest artifact accounting is missing")
    manifest_bytes = manifest_path.stat().st_size
    partition_bytes = sum(int(partitions[split]["bytes"]) for split in PARTITION_NAMES)
    total_bytes = manifest_bytes + partition_bytes
    if (
        artifacts.get("manifest_bytes") != manifest_bytes
        or artifacts.get("partition_bytes") != partition_bytes
        or artifacts.get("total_fixture_bytes") != total_bytes
        or not isinstance(artifacts.get("max_total_bytes"), int)
        or int(artifacts["max_total_bytes"]) < total_bytes
    ):
        raise ValueError("Loop 23 manifest artifact byte accounting is invalid")
    return manifest


def resolve_ctc_symbol_partition_path(
    manifest_path: str | Path,
    manifest: Mapping[str, Any],
    split: str,
) -> Path:
    if split not in PARTITION_NAMES:
        raise ValueError(f"unknown Loop 23 partition: {split}")
    root = Path(manifest_path).parent.resolve()
    resolved = (root / str(manifest["partitions"][split]["path"])).resolve(
        strict=False
    )
    if not resolved.is_relative_to(root):
        raise ValueError("Loop 23 partition resolves outside its fixture directory")
    return resolved


def _partition_report(
    path: Path, *, arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": _file_sha256(path),
        "bytes": path.stat().st_size,
        **_partition_content_summary(arrays, metadata, full=True),
    }


def _partition_content_summary(
    arrays: Mapping[str, Any], metadata: Mapping[str, Any], *, full: bool
) -> dict[str, Any]:
    np = _require_numpy()
    target_lengths = arrays["target_lengths"]
    targets = arrays["target_token_ids"]
    valid_targets = [
        targets[index, : int(length)].astype("int64", copy=False)
        for index, length in enumerate(target_lengths.tolist())
    ]
    target_support = np.bincount(
        np.concatenate(valid_targets), minlength=int(metadata["protocol"]["n_symbols"]) + 1
    )[1:]
    repeated_pairs = sum(
        sum(left == right for left, right in zip(row[:-1], row[1:]))
        for row in (value.tolist() for value in valid_targets)
    )
    summary = {
        "schema": dict(metadata["schema"]),
        "split": str(metadata["split"]),
        "items": int(len(target_lengths)),
        "target_tokens": int(target_lengths.sum()),
        "target_length_range": [int(target_lengths.min()), int(target_lengths.max())],
        "repeated_pair_count": int(repeated_pairs),
        "target_symbol_support": [int(value) for value in target_support.tolist()],
        "item_ids_sha256": _sha256_json(arrays["item_ids"].tolist()),
        "target_ids_sha256": _ragged_targets_sha256(targets, target_lengths),
        "seed": int(metadata["seed"]),
        "protocol_sha256": str(metadata["protocol_sha256"]),
    }
    if full:
        frame_labels = arrays["frame_labels"]
        frame_lengths = arrays["frame_lengths"]
        valid_frames = np.concatenate(
            [
                frame_labels[index, : int(length)]
                for index, length in enumerate(frame_lengths.tolist())
            ]
        )
        frame_support = np.bincount(
            valid_frames.astype("int64"),
            minlength=int(metadata["protocol"]["n_symbols"]) + 1,
        )
        summary.update(
            {
                "signals_shape": [int(value) for value in arrays["signals"].shape],
                "signals_dtype": str(arrays["signals"].dtype),
                "valid_samples": int(arrays["input_lengths"].sum()),
                "valid_frames": int(frame_lengths.sum()),
                "frame_class_support": [
                    int(value) for value in frame_support.tolist()
                ],
            }
        )
    return summary


def _validate_target_arrays(
    arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> None:
    np = _require_numpy()
    protocol = _protocol_from_metadata(metadata)
    split = str(metadata["split"])
    targets = np.asarray(arrays["target_token_ids"])
    lengths = np.asarray(arrays["target_lengths"])
    item_ids = np.asarray(arrays["item_ids"])
    n_items = int(getattr(protocol, f"{split}_items"))
    if targets.shape != (n_items, protocol.max_target_length):
        raise ValueError("Loop 23 target array shape is invalid")
    if not np.issubdtype(targets.dtype, np.integer):
        raise ValueError("Loop 23 target IDs must use an integer dtype")
    if lengths.shape != (n_items,) or not np.issubdtype(lengths.dtype, np.integer):
        raise ValueError("Loop 23 target lengths must be an integer item vector")
    if (
        item_ids.shape != (n_items,)
        or item_ids.dtype.kind != "U"
        or item_ids.tolist()
        != [f"{split}-{metadata['seed']}-{index:04d}" for index in range(n_items)]
    ):
        raise ValueError("Loop 23 item IDs do not match split, seed, and row order")
    for index, length_value in enumerate(lengths.tolist()):
        length = int(length_value)
        if length < protocol.min_target_length or length > protocol.max_target_length:
            raise ValueError("Loop 23 target length falls outside the protocol")
        row = targets[index, :length]
        if set(row.tolist()) != set(range(1, protocol.n_symbols + 1)):
            raise ValueError("Loop 23 target must contain every synthetic symbol")
        if not any(left == right for left, right in zip(row[:-1], row[1:])):
            raise ValueError("Loop 23 target lacks an adjacent repeated symbol")
        if not (targets[index, length:] == -1).all():
            raise ValueError("Loop 23 target padding must be -1")


def _validate_full_arrays(
    arrays: Mapping[str, Any], metadata: Mapping[str, Any]
) -> None:
    np = _require_numpy()
    missing = sorted(set(FULL_ARRAY_MEMBERS) - set(arrays))
    if missing:
        raise ValueError(f"Loop 23 arrays are missing: {missing}")
    _validate_target_arrays(arrays, metadata)
    protocol = _protocol_from_metadata(metadata)
    n_items = int(arrays["target_lengths"].shape[0])
    signals = np.asarray(arrays["signals"])
    if (
        signals.shape != (n_items, protocol.n_channels, protocol.max_timepoints)
        or signals.dtype != np.dtype("float32")
        or not np.isfinite(signals).all()
    ):
        raise ValueError("Loop 23 signals violate shape, dtype, or finite contract")
    input_lengths = np.asarray(arrays["input_lengths"])
    frame_lengths = np.asarray(arrays["frame_lengths"])
    for name, values in (
        ("input_lengths", input_lengths),
        ("frame_lengths", frame_lengths),
    ):
        if values.shape != (n_items,) or not np.issubdtype(values.dtype, np.integer):
            raise ValueError(f"Loop 23 {name} must be an integer item vector")
    sample_labels = np.asarray(arrays["sample_labels"])
    frame_labels = np.asarray(arrays["frame_labels"])
    starts = np.asarray(arrays["motif_start_samples"])
    ends = np.asarray(arrays["motif_end_samples"])
    if sample_labels.shape != (n_items, protocol.max_timepoints):
        raise ValueError("Loop 23 sample labels do not match signal time")
    if frame_labels.shape != (n_items, protocol.max_frames):
        raise ValueError("Loop 23 frame labels do not match protocol geometry")
    if starts.shape != arrays["target_token_ids"].shape or ends.shape != starts.shape:
        raise ValueError("Loop 23 motif boundaries do not match target shape")
    for index in range(n_items):
        target_length = int(arrays["target_lengths"][index])
        target = arrays["target_token_ids"][index, :target_length]
        length = int(input_lengths[index])
        expected_length = (
            protocol.lead_width
            + target_length * protocol.motif_width
            + (target_length - 1) * protocol.gap_width
            + protocol.tail_width
        )
        if length != expected_length:
            raise ValueError("Loop 23 input length does not match its target")
        expected_frames = 1 + (length - protocol.kernel_size) // protocol.stride
        if int(frame_lengths[index]) != expected_frames:
            raise ValueError("Loop 23 frame length does not match kernel/stride")
        expected_labels = np.zeros(length, dtype=sample_labels.dtype)
        cursor = protocol.lead_width
        for target_index, symbol_value in enumerate(target.tolist()):
            end = cursor + protocol.motif_width
            if int(starts[index, target_index]) != cursor or int(
                ends[index, target_index]
            ) != end:
                raise ValueError("Loop 23 motif boundaries are inconsistent")
            expected_labels[cursor:end] = int(symbol_value)
            cursor = end
            if target_index < target_length - 1:
                cursor += protocol.gap_width
        if not np.array_equal(sample_labels[index, :length], expected_labels):
            raise ValueError("Loop 23 sample labels do not match targets/boundaries")
        frame_starts = np.arange(expected_frames, dtype="int64") * protocol.stride
        expected_frame_labels = expected_labels[
            frame_starts + protocol.kernel_size - 1
        ]
        if not np.array_equal(
            frame_labels[index, :expected_frames], expected_frame_labels
        ):
            raise ValueError("Loop 23 frame labels violate final-sample semantics")
        if not (sample_labels[index, length:] == -1).all():
            raise ValueError("Loop 23 sample-label padding must be -1")
        if not (frame_labels[index, expected_frames:] == -1).all():
            raise ValueError("Loop 23 frame-label padding must be -1")
        if not np.array_equal(
            signals[index, :, length:], np.zeros_like(signals[index, :, length:])
        ):
            raise ValueError("Loop 23 signal padding must be exactly zero")
        if not (starts[index, target_length:] == -1).all() or not (
            ends[index, target_length:] == -1
        ).all():
            raise ValueError("Loop 23 motif-boundary padding must be -1")


def _protocol_from_metadata(metadata: Mapping[str, Any]) -> CTCSymbolStreamProtocol:
    schema = metadata.get("schema") or {}
    if schema != {"name": CTC_SYMBOL_SCHEMA_NAME, "version": CTC_SYMBOL_SCHEMA_VERSION}:
        raise ValueError("unsupported Loop 23 partition schema")
    if metadata.get("kind") != "synthetic_ctc_symbol_stream":
        raise ValueError("Loop 23 partition kind is invalid")
    if metadata.get("proof_posture") != CTC_SYMBOL_PROOF_POSTURE:
        raise ValueError("Loop 23 partition proof posture is invalid")
    split = str(metadata.get("split") or "")
    if split not in PARTITION_NAMES:
        raise ValueError("Loop 23 partition split is invalid")
    values = metadata.get("protocol")
    if not isinstance(values, dict):
        raise ValueError("Loop 23 partition protocol is missing")
    try:
        protocol = CTCSymbolStreamProtocol(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Loop 23 partition protocol fields are invalid") from exc
    _validate_protocol(protocol)
    if metadata.get("protocol_sha256") != protocol.protocol_sha256:
        raise ValueError("Loop 23 partition protocol hash mismatch")
    if metadata.get("seed") != int(getattr(protocol, f"{split}_seed")):
        raise ValueError("Loop 23 partition seed does not match protocol")
    if metadata.get("blank_id") != 0:
        raise ValueError("Loop 23 partition blank ID is invalid")
    return protocol


def _validate_protocol(protocol: CTCSymbolStreamProtocol) -> None:
    integers = {
        name: int(value)
        for name, value in protocol.to_dict().items()
        if name.endswith("_items")
        or name.endswith("_seed")
        or name
        in {
            "n_channels",
            "n_symbols",
            "kernel_size",
            "stride",
            "min_target_length",
            "max_target_length",
            "motif_width",
            "gap_width",
            "lead_width",
            "tail_width",
        }
    }
    if any(value < 1 for value in integers.values()):
        raise ValueError("Loop 23 integer protocol values must be positive")
    if protocol.n_channels != protocol.n_symbols or protocol.n_symbols != 5:
        raise ValueError("Loop 23 requires exactly one channel per five symbols")
    if protocol.min_target_length != protocol.n_symbols + 1:
        raise ValueError("Loop 23 minimum target must include all symbols plus a repeat")
    if protocol.max_target_length < protocol.min_target_length:
        raise ValueError("Loop 23 maximum target length is invalid")
    if protocol.stride > protocol.kernel_size:
        raise ValueError("Loop 23 stride cannot exceed kernel size")
    if protocol.total_items > 4096 or protocol.max_timepoints > 65536:
        raise ValueError("Loop 23 protocol exceeds fixture safety bounds")
    floats = (
        protocol.sampling_rate_hz,
        protocol.motif_amplitude,
        protocol.adjacent_amplitude,
        protocol.noise_std,
        protocol.gain_min,
        protocol.gain_max,
        protocol.offset_std,
    )
    if any(not math.isfinite(value) or value <= 0 for value in floats):
        raise ValueError("Loop 23 floating protocol values must be finite and positive")
    if protocol.gain_max < protocol.gain_min:
        raise ValueError("Loop 23 gain range is invalid")


def _stable_manifest_json(manifest: dict[str, Any]) -> str:
    for _ in range(16):
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
    raise RuntimeError("Loop 23 manifest byte accounting did not converge")


def _ragged_targets_sha256(targets, lengths) -> str:
    digest = hashlib.sha256()
    for index, length_value in enumerate(lengths.tolist()):
        values = _require_numpy().ascontiguousarray(
            targets[index, : int(length_value)].astype("int16", copy=False)
        )
        digest.update(int(length_value).to_bytes(4, "little", signed=False))
        digest.update(values.tobytes())
    return digest.hexdigest()


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        metadata = json.loads(str(raw))
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Loop 23 partition metadata is not valid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("Loop 23 partition metadata must decode to an object")
    return metadata


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
        raise RuntimeError(
            "Loop 23 symbol fixtures require NumPy: `pip install numpy`."
        ) from exc
    return np
