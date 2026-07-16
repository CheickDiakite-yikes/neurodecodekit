"""Deterministic synthetic sentence motifs for Loop 48 Stage C."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from neurodecodekit.preprocess.ctc_text import CTC_VOCAB


FIXTURE_SCHEMA_NAME = "neurodecodekit.loop48_stage_c_temporal_motif_fixture"
FIXTURE_SCHEMA_VERSION = 0
REGISTERED_SEED = 4850
REGISTERED_PARTITIONS = {"train": 24, "selection": 8, "final": 8}
REGISTERED_CHANNELS = 102
REGISTERED_SAMPLING_RATE_HZ = 100
REGISTERED_TOKEN_IDS = (1, 2, 3, 4)


@dataclass(frozen=True)
class TemporalMotifPartition:
    """One physically separate synthetic split with explicit padding and identity."""

    name: str
    signals: Any
    input_lengths: Any
    target_token_ids: Any
    target_lengths: Any
    item_ids: Any

    @property
    def target_texts(self) -> tuple[str, ...]:
        return tuple(
            "".join(CTC_VOCAB[int(value)] for value in row[: int(length)])
            for row, length in zip(
                self.target_token_ids,
                self.target_lengths,
                strict=True,
            )
        )

    @property
    def array_bytes(self) -> int:
        return sum(
            int(value.nbytes)
            for value in (
                self.signals,
                self.input_lengths,
                self.target_token_ids,
                self.target_lengths,
                self.item_ids,
            )
        )


@dataclass(frozen=True)
class TemporalMotifFixture:
    """Frozen 24/8/8 synthetic fixture generated without any input file."""

    train: TemporalMotifPartition
    selection: TemporalMotifPartition
    final: TemporalMotifPartition
    metadata: dict[str, Any]

    def partition(self, name: str) -> TemporalMotifPartition:
        if name not in REGISTERED_PARTITIONS:
            raise ValueError(f"unknown Stage C fixture partition: {name}")
        return getattr(self, name)

    @property
    def array_bytes(self) -> int:
        return sum(self.partition(name).array_bytes for name in REGISTERED_PARTITIONS)


def generate_registered_temporal_motif_fixture() -> TemporalMotifFixture:
    """Generate the exact target-free-from-real-data Stage C fixture in memory."""

    np = _require_numpy()
    rng = np.random.Generator(np.random.PCG64(REGISTERED_SEED))
    item_count = sum(REGISTERED_PARTITIONS.values())
    output_lengths = np.asarray([24 + (index % 3) for index in range(item_count)])
    input_lengths = output_lengths * 4
    max_input_length = int(input_lengths.max())
    max_target_length = 6
    signals = np.zeros(
        (item_count, REGISTERED_CHANNELS, max_input_length),
        dtype="float32",
    )
    target_ids = np.zeros((item_count, max_target_length), dtype="int16")
    target_lengths = np.asarray(
        [4 + (index % 3) for index in range(item_count)],
        dtype="int16",
    )
    item_ids = np.asarray(
        [f"L48C-SYN-{index:03d}" for index in range(item_count)],
        dtype="<U12",
    )
    shared_pattern = np.asarray([3.0, 1.0, -2.0, -3.0, -1.0, 2.0], dtype="float32")
    motif_offsets = np.asarray([-7, -6, -5, -3, -2, -1], dtype="int64")

    for item_index in range(item_count):
        valid_length = int(input_lengths[item_index])
        noise = rng.normal(
            loc=0.0,
            scale=0.015,
            size=(REGISTERED_CHANNELS, valid_length),
        ).astype("float32")
        noise[:, ::4] = 0.0
        signals[item_index, :, :valid_length] = noise
        target_length = int(target_lengths[item_index])
        step = 1 + ((item_index // 4) % 3)
        token_row = np.asarray(
            [((item_index + position * step) % 4) + 1 for position in range(target_length)],
            dtype="int16",
        )
        target_ids[item_index, :target_length] = token_row
        for position, token_id in enumerate(token_row.tolist()):
            output_index = 3 + position * 4
            endpoint = output_index * 4
            shifted = np.roll(shared_pattern, int(token_id) - 1)
            indices = endpoint + motif_offsets
            signals[item_index, 0, indices] += shifted * 2.5
            signals[item_index, 1, indices] += shifted[::-1] * 1.5
            signals[item_index, 2, indices] += np.sign(shifted) * 0.75
        signals[item_index, :, :valid_length:4] = 0.0

    boundaries = (0, 24, 32, 40)
    partitions = {}
    for name, start, stop in zip(
        REGISTERED_PARTITIONS,
        boundaries[:-1],
        boundaries[1:],
        strict=True,
    ):
        partitions[name] = TemporalMotifPartition(
            name=name,
            signals=np.ascontiguousarray(signals[start:stop]),
            input_lengths=np.ascontiguousarray(input_lengths[start:stop].astype("int32")),
            target_token_ids=np.ascontiguousarray(target_ids[start:stop]),
            target_lengths=np.ascontiguousarray(target_lengths[start:stop]),
            item_ids=np.ascontiguousarray(item_ids[start:stop]),
        )
    metadata = {
        "schema": {"name": FIXTURE_SCHEMA_NAME, "version": FIXTURE_SCHEMA_VERSION},
        "seed": REGISTERED_SEED,
        "partitions": dict(REGISTERED_PARTITIONS),
        "sampling_rate_hz": REGISTERED_SAMPLING_RATE_HZ,
        "channels": REGISTERED_CHANNELS,
        "token_ids": list(REGISTERED_TOKEN_IDS),
        "source_kind": "synthetic_ordered_temporal_motifs",
        "source_files_read": 0,
        "real_cache_reads": 0,
        "real_signal_rows_read": 0,
        "real_target_rows_read": 0,
        "new_real_data_download_bytes": 0,
        "sampled_source_frames_are_zero": True,
        "motif_offsets_from_output_timestamp": motif_offsets.tolist(),
        "motif_identity": "cyclic_order_of_one_shared_six_value_history_pattern",
        "warning": "synthetic labels define fixture motifs and are not real neural targets",
    }
    fixture = TemporalMotifFixture(metadata=metadata, **partitions)
    validate_temporal_motif_fixture(fixture)
    return fixture


def validate_temporal_motif_fixture(fixture: TemporalMotifFixture) -> dict[str, Any]:
    """Validate identity, masks, padding, CTC geometry, and leakage boundaries."""

    np = _require_numpy()
    if fixture.metadata.get("schema") != {
        "name": FIXTURE_SCHEMA_NAME,
        "version": FIXTURE_SCHEMA_VERSION,
    }:
        raise ValueError("unsupported Stage C fixture schema")
    if fixture.metadata.get("seed") != REGISTERED_SEED:
        raise ValueError("Stage C fixture seed drifted")
    if fixture.metadata.get("partitions") != REGISTERED_PARTITIONS:
        raise ValueError("Stage C fixture partition counts drifted")
    forbidden_metadata = {
        "source_path",
        "cache_path",
        "subject_id",
        "session_id",
        "trial_id",
        "real_target_text",
        "real_prediction",
    }
    if forbidden_metadata.intersection(fixture.metadata):
        raise ValueError("Stage C fixture metadata contains a forbidden real-data field")

    seen_ids: set[str] = set()
    partition_hashes: dict[str, str] = {}
    total_valid_source_samples = 0
    total_valid_output_steps = 0
    for name, expected_items in REGISTERED_PARTITIONS.items():
        partition = fixture.partition(name)
        if partition.name != name or len(partition.signals) != expected_items:
            raise ValueError(f"Stage C {name} partition identity or item count drifted")
        if partition.signals.ndim != 3 or partition.signals.shape[1] != REGISTERED_CHANNELS:
            raise ValueError(f"Stage C {name} signal geometry is invalid")
        if partition.input_lengths.shape != (expected_items,):
            raise ValueError(f"Stage C {name} input lengths are invalid")
        if partition.target_token_ids.shape != (expected_items, 6):
            raise ValueError(f"Stage C {name} target geometry is invalid")
        if partition.target_lengths.shape != (expected_items,):
            raise ValueError(f"Stage C {name} target lengths are invalid")
        if partition.item_ids.shape != (expected_items,):
            raise ValueError(f"Stage C {name} item IDs are invalid")
        if not np.isfinite(partition.signals).all():
            raise ValueError(f"Stage C {name} signals contain non-finite values")
        for row, input_length, target_row, target_length, item_id in zip(
            partition.signals,
            partition.input_lengths,
            partition.target_token_ids,
            partition.target_lengths,
            partition.item_ids,
            strict=True,
        ):
            item = str(item_id)
            if item in seen_ids:
                raise ValueError("Stage C fixture item IDs overlap across partitions")
            seen_ids.add(item)
            length = int(input_length)
            target_len = int(target_length)
            if length < 1 or length > row.shape[1] or length % 4:
                raise ValueError("Stage C input length is invalid")
            if np.any(row[:, length:] != 0.0):
                raise ValueError("Stage C signal padding must be exactly zero")
            if np.any(row[:, :length:4] != 0.0):
                raise ValueError("Stage C sampled source frames must contain no motif signal")
            valid_targets = target_row[:target_len]
            if target_len < 1 or (valid_targets < 1).any() or (valid_targets > 4).any():
                raise ValueError("Stage C synthetic targets are invalid")
            if np.any(target_row[target_len:] != 0):
                raise ValueError("Stage C target padding must use blank zero")
            if np.any(valid_targets[1:] == valid_targets[:-1]):
                raise ValueError("Stage C synthetic targets may not contain adjacent repeats")
            if length // 4 < target_len:
                raise ValueError("Stage C synthetic target is infeasible after downsampling")
            total_valid_source_samples += length
            total_valid_output_steps += length // 4
        partition_hashes[name] = _partition_sha256(partition)
    if len(seen_ids) != 40:
        raise ValueError("Stage C fixture must contain exactly 40 unique item IDs")
    return {
        "valid": True,
        "schema": fixture.metadata["schema"],
        "seed": REGISTERED_SEED,
        "partitions": dict(REGISTERED_PARTITIONS),
        "item_count": len(seen_ids),
        "channels": REGISTERED_CHANNELS,
        "sampling_rate_hz": REGISTERED_SAMPLING_RATE_HZ,
        "array_bytes": fixture.array_bytes,
        "total_valid_source_samples": total_valid_source_samples,
        "total_valid_output_steps": total_valid_output_steps,
        "partition_sha256": partition_hashes,
        "fixture_sha256": _sha256_json(
            {
                "metadata": fixture.metadata,
                "partition_sha256": partition_hashes,
            }
        ),
        "source_files_read": 0,
        "real_cache_reads": 0,
        "real_signal_rows_read": 0,
        "real_target_rows_read": 0,
        "new_real_data_download_bytes": 0,
    }


def _partition_sha256(partition: TemporalMotifPartition) -> str:
    digest = hashlib.sha256()
    for name, value in (
        ("signals", partition.signals),
        ("input_lengths", partition.input_lengths),
        ("target_token_ids", partition.target_token_ids),
        ("target_lengths", partition.target_lengths),
        ("item_ids", partition.item_ids),
    ):
        digest.update(name.encode("utf-8"))
        digest.update(str(value.dtype).encode("ascii"))
        digest.update(json.dumps(list(value.shape), separators=(",", ":")).encode("ascii"))
        digest.update(value.tobytes(order="C"))
    return digest.hexdigest()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "Stage C synthetic fixtures require NumPy: `pip install -e '.[array]'`."
        ) from exc
    return np
