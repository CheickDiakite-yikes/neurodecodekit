"""Deterministic target-free fixture for the Loop 25 causal preprocessing gate."""

from __future__ import annotations

import hashlib
import io
import json
import math
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from neurodecodekit.preprocess.causal_preprocessing import (
    REGISTERED_CONTRACT_SHA256,
    load_filter_bundle,
    load_registered_contract,
    validate_loop25_authorization,
)


SCHEMA_NAME = "b2q-causal-preprocessing-fixture"
SCHEMA_VERSION = 0
MANIFEST_SCHEMA_NAME = "b2q-causal-preprocessing-fixture-manifest"
MANIFEST_SCHEMA_VERSION = 0
PROOF_POSTURE = "target_free_synthetic_causal_preprocessing_mechanics_only"
PARTITION_NAMES = ("development", "qualification")
ARRAY_MEMBERS = (
    "signals",
    "input_lengths",
    "item_ids",
    "source_start_samples",
    "metadata",
)
FORBIDDEN_MEMBERS = (
    "targets",
    "target_token_ids",
    "target_lengths",
    "labels",
    "frame_labels",
    "sample_labels",
    "text",
    "predictions",
    "participant_id",
    "subject_id",
    "session_id",
    "recording_path",
    "model_output",
    "checkpoint",
)
SIGNAL_FAMILIES = (
    "bounded_multisine_passband_and_stopband",
    "bounded_linear_chirp",
    "bounded_impulse_interior_and_boundary",
    "bounded_step_and_plateau",
    "bounded_drift_and_piecewise_ramp",
    "bounded_seeded_noise_with_outlier",
)
DEFAULT_MAX_FIXTURE_BYTES = 4 * 1024 * 1024
CONTRACT_RELATIVE_PATH = Path("registries/causal_preprocessing_contract.v1.json")


@dataclass(frozen=True)
class CausalPreprocessingFixtureProtocol:
    """Frozen fixture constants copied from the v1 contract."""

    development_seed: int = 2501
    qualification_seed: int = 2502
    items_per_partition: int = 12
    items_per_family: int = 2
    channels: int = 5
    sampling_rate_hz: float = 1000.0
    item_lengths: tuple[int, ...] = (
        1024,
        1280,
        1536,
        1792,
        2048,
        2304,
        2560,
        2816,
        3072,
        3328,
        3584,
        4096,
    )
    value_min: float = -4.0
    value_max: float = 4.0

    @property
    def maximum_samples(self) -> int:
        return max(self.item_lengths)

    @property
    def minimum_samples(self) -> int:
        return min(self.item_lengths)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["item_lengths"] = list(self.item_lengths)
        value["signal_families"] = list(SIGNAL_FAMILIES)
        value["schema_name"] = SCHEMA_NAME
        value["schema_version"] = SCHEMA_VERSION
        return value

    @property
    def protocol_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class LoadedCausalPreprocessingPartition:
    """One validated physical target-free partition."""

    split: str
    signals: Any
    input_lengths: Any
    item_ids: Any
    source_start_samples: Any
    metadata: dict[str, Any]
    opened_members: tuple[str, ...]

    @property
    def array_bytes(self) -> int:
        return int(
            self.signals.nbytes
            + self.input_lengths.nbytes
            + self.item_ids.nbytes
            + self.source_start_samples.nbytes
        )


def registered_causal_preprocessing_fixture_protocol() -> CausalPreprocessingFixtureProtocol:
    """Return and verify the exact fixture constants in the v1 contract."""

    protocol = CausalPreprocessingFixtureProtocol()
    fixture = load_registered_contract()["fixture_contract"]
    expected = {
        "development_seed": fixture["development"]["seed"],
        "qualification_seed": fixture["qualification"]["seed"],
        "items_per_partition": fixture["development"]["items"],
        "items_per_family": fixture["items_per_family_per_partition"],
        "channels": fixture["channels"],
        "sampling_rate_hz": fixture["sampling_rate_hz"],
        "item_lengths": tuple(fixture["item_lengths_exact"]),
        "value_min": fixture["value_bounds_inclusive"][0],
        "value_max": fixture["value_bounds_inclusive"][1],
    }
    for name, value in expected.items():
        if getattr(protocol, name) != value:
            raise RuntimeError(f"Loop 25 fixture protocol drifted at {name}")
    if tuple(fixture["members"]) != ARRAY_MEMBERS:
        raise RuntimeError("Loop 25 fixture member contract drifted")
    if tuple(fixture["forbidden_members"]) != FORBIDDEN_MEMBERS:
        raise RuntimeError("Loop 25 fixture forbidden-member contract drifted")
    if tuple(fixture["signal_families"]) != SIGNAL_FAMILIES:
        raise RuntimeError("Loop 25 signal-family contract drifted")
    return protocol


def prepare_causal_preprocessing_fixture(
    out_dir: str | Path,
    *,
    static_filter_bundle_path: str | Path | None = None,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    protocol: CausalPreprocessingFixtureProtocol | None = None,
    require_registered_protocol: bool = True,
    require_static_gate: bool = True,
    enforce_authorized_output_root: bool | None = None,
) -> dict[str, Any]:
    """Create deterministic development and qualification NPZ files plus manifest."""

    registered = registered_causal_preprocessing_fixture_protocol()
    selected = protocol or registered
    _validate_protocol(selected)
    registered_match = selected == registered
    if require_registered_protocol and not registered_match:
        raise ValueError("causal preprocessing fixture override is not registered")
    if max_total_bytes <= 0 or max_total_bytes > DEFAULT_MAX_FIXTURE_BYTES:
        raise ValueError("fixture byte cap must be positive and cannot exceed 4 MiB")
    if require_static_gate:
        if static_filter_bundle_path is None:
            raise ValueError("a passing static filter bundle is required before fixture generation")
        _, audit = load_filter_bundle(
            static_filter_bundle_path,
            require_registered=require_registered_protocol,
        )
        if not audit["passed"]:
            raise ValueError("static filter gate failed; both fixture seeds must remain unopened")
        static_bundle_sha256 = _file_sha256(Path(static_filter_bundle_path))
    else:
        if require_registered_protocol:
            raise ValueError("registered fixture generation cannot bypass the static gate")
        static_bundle_sha256 = "nonregistered-test-bypass"

    if require_registered_protocol:
        validate_loop25_authorization()
    output = Path(out_dir)
    enforce_root = (
        require_registered_protocol
        if enforce_authorized_output_root is None
        else enforce_authorized_output_root
    )
    if enforce_root:
        _validate_authorized_output_path(output)
    if output.exists():
        raise FileExistsError(f"refusing to replace fixture directory: {output}")

    partition_payloads: dict[str, bytes] = {}
    partition_rows: dict[str, dict[str, Any]] = {}
    for split in PARTITION_NAMES:
        seed = _partition_seed(selected, split)
        arrays, metadata = make_causal_preprocessing_partition(
            split=split,
            seed=seed,
            protocol=selected,
        )
        payload = _deterministic_npz_bytes({**arrays, "metadata": _metadata_array(metadata)})
        partition_payloads[split] = payload
        partition_rows[split] = _partition_manifest_row(
            split=split,
            seed=seed,
            payload=payload,
            arrays=arrays,
            metadata=metadata,
        )

    manifest: dict[str, Any] = {
        "schema": {"name": MANIFEST_SCHEMA_NAME, "version": MANIFEST_SCHEMA_VERSION},
        "fixture_schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "registered_protocol_match": registered_match,
        "protocol": selected.to_dict(),
        "protocol_sha256": selected.protocol_sha256,
        "contract": {
            "path": CONTRACT_RELATIVE_PATH.as_posix(),
            "sha256": REGISTERED_CONTRACT_SHA256 if registered_match else "nonregistered-test",
        },
        "static_filter_bundle_sha256": static_bundle_sha256,
        "array_members": list(ARRAY_MEMBERS),
        "forbidden_members": list(FORBIDDEN_MEMBERS),
        "partitions": partition_rows,
        "access_contract": {
            "manifest_inspection_opens_signal_arrays": False,
            "physical_partition_files_required": True,
            "partition_item_ids_must_be_disjoint": True,
            "development_must_pass_before_qualification_open": True,
        },
        "generation": {
            "generated_from_model_outputs": False,
            "generated_from_targets_labels_text_or_predictions": False,
            "contains_brainlike_or_neural_claim": False,
            "real_data_reads": 0,
            "real_cache_reads": 0,
            "consumed_evidence_reads": 0,
            "target_label_text_prediction_reads": 0,
            "model_runs": 0,
            "training_runs": 0,
            "network_calls": 0,
        },
        "artifacts": {
            "files": 3,
            "partition_bytes": sum(len(value) for value in partition_payloads.values()),
            "manifest_bytes": 0,
            "total_bytes": 0,
            "maximum_total_bytes": int(max_total_bytes),
        },
        "warnings": [
            "Synthetic numerical stress signals are not neural recordings.",
            "The fixture contains no targets, labels, text, predictions, or participant identity.",
            "Qualification is physically separate and may open only after a frozen development pass.",
        ],
        "claim_boundaries": [
            "This fixture validates target-free mechanics only.",
            "It does not establish neural information, decoding, latency, or device behavior.",
        ],
    }
    manifest_payload = _manifest_payload_with_sizes(manifest)
    total = sum(len(value) for value in partition_payloads.values()) + len(manifest_payload)
    if total > max_total_bytes:
        raise ValueError(f"fixture would write {total} bytes, exceeding cap {max_total_bytes}")

    output.mkdir(parents=True, exist_ok=False)
    for split, payload in partition_payloads.items():
        (output / f"{split}.npz").write_bytes(payload)
    manifest_path = output / "manifest.json"
    manifest_path.write_bytes(manifest_payload)
    return load_causal_preprocessing_manifest(
        manifest_path,
        max_total_bytes=max_total_bytes,
        require_registered_protocol=require_registered_protocol,
    )


def make_causal_preprocessing_partition(
    *,
    split: str,
    seed: int,
    protocol: CausalPreprocessingFixtureProtocol | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate one target-free partition without consulting a model or target."""

    np = _require_numpy()
    selected = protocol or registered_causal_preprocessing_fixture_protocol()
    _validate_protocol(selected)
    _validate_split_seed(selected, split, seed)
    rng = np.random.default_rng(seed)
    signals = np.zeros(
        (selected.items_per_partition, selected.channels, selected.maximum_samples),
        dtype="float32",
    )
    input_lengths = np.asarray(selected.item_lengths, dtype="int32")
    item_ids: list[str] = []
    family_by_item: list[str] = []
    for item_index, length in enumerate(selected.item_lengths):
        family = SIGNAL_FAMILIES[item_index // selected.items_per_family]
        local_index = item_index % selected.items_per_family
        row = _make_signal_family(
            np,
            rng,
            family=family,
            local_index=local_index,
            channels=selected.channels,
            length=length,
            sampling_rate_hz=selected.sampling_rate_hz,
        )
        signals[item_index, :, :length] = row
        item_ids.append(f"loop25-{split}-{item_index:02d}-{family[:12]}")
        family_by_item.append(family)
    source_start_samples = (
        np.arange(selected.items_per_partition, dtype="int64") * 10_000
        + (0 if split == "development" else 1_000_000)
    )
    arrays = {
        "signals": signals,
        "input_lengths": input_lengths,
        "item_ids": np.asarray(item_ids, dtype="U56"),
        "source_start_samples": source_start_samples,
    }
    metadata = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "split": split,
        "seed": int(seed),
        "protocol_sha256": selected.protocol_sha256,
        "signal_layout": "items,channels,time",
        "signal_dtype": "float32",
        "family_by_item": family_by_item,
        "family_counts": {family: family_by_item.count(family) for family in SIGNAL_FAMILIES},
        "generator": {
            "model_outputs_read": 0,
            "target_label_text_prediction_reads": 0,
            "real_or_consumed_data_reads": 0,
            "network_calls": 0,
        },
    }
    _validate_partition_arrays(
        arrays,
        metadata=metadata,
        split=split,
        seed=seed,
        protocol=selected,
    )
    return arrays, metadata


def load_causal_preprocessing_manifest(
    path: str | Path,
    *,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    require_registered_protocol: bool = True,
) -> dict[str, Any]:
    """Validate manifest identities and file hashes without opening NPZ members."""

    source = Path(path)
    if source.stat().st_size > 1024 * 1024:
        raise ValueError("fixture manifest exceeds 1 MiB")
    manifest = json.loads(source.read_text(encoding="utf-8"))
    if manifest.get("schema") != {
        "name": MANIFEST_SCHEMA_NAME,
        "version": MANIFEST_SCHEMA_VERSION,
    }:
        raise ValueError("fixture manifest schema mismatch")
    if not manifest.get("target_free"):
        raise ValueError("fixture manifest must be target-free")
    if tuple(manifest.get("array_members", ())) != ARRAY_MEMBERS:
        raise ValueError("fixture array-member contract mismatch")
    if tuple(manifest.get("forbidden_members", ())) != FORBIDDEN_MEMBERS:
        raise ValueError("fixture forbidden-member contract mismatch")
    protocol = _protocol_from_dict(manifest["protocol"])
    _validate_protocol(protocol)
    if manifest["protocol_sha256"] != protocol.protocol_sha256:
        raise ValueError("fixture protocol hash mismatch")
    if require_registered_protocol:
        registered = registered_causal_preprocessing_fixture_protocol()
        if protocol != registered or not manifest.get("registered_protocol_match"):
            raise ValueError("fixture protocol is not the registered protocol")
        if manifest["contract"]["sha256"] != REGISTERED_CONTRACT_SHA256:
            raise ValueError("fixture contract hash mismatch")
    partitions = manifest.get("partitions", {})
    if set(partitions) != set(PARTITION_NAMES):
        raise ValueError("fixture must contain development and qualification metadata")
    all_ids: set[str] = set()
    referenced_paths: set[PurePosixPath] = set()
    total = source.stat().st_size
    for split in PARTITION_NAMES:
        row = partitions[split]
        _validate_manifest_partition_identity(row, split=split, protocol=protocol)
        ids = set(row["item_ids"])
        if all_ids.intersection(ids):
            raise ValueError("fixture partition item IDs overlap")
        all_ids.update(ids)
        relative = PurePosixPath(row["path"])
        if relative.is_absolute() or ".." in relative.parts or len(relative.parts) != 1:
            raise ValueError("fixture partition path is unsafe")
        if relative in referenced_paths:
            raise ValueError("fixture partitions must use separate physical files")
        referenced_paths.add(relative)
        partition_path = source.parent / relative.as_posix()
        if partition_path.stat().st_size != row["bytes"]:
            raise ValueError(f"{split} fixture byte count mismatch")
        if _file_sha256(partition_path) != row["sha256"]:
            raise ValueError(f"{split} fixture SHA-256 mismatch")
        archive_members = _npz_array_members(partition_path)
        forbidden = set(archive_members).intersection(FORBIDDEN_MEMBERS)
        if forbidden:
            raise ValueError(f"fixture contains forbidden members: {sorted(forbidden)}")
        if set(archive_members) != set(ARRAY_MEMBERS):
            raise ValueError(f"{split} fixture NPZ member set mismatch")
        total += partition_path.stat().st_size
    if total > max_total_bytes or total != manifest["artifacts"]["total_bytes"]:
        raise ValueError("fixture total bytes violate manifest or cap")
    return manifest


def load_causal_preprocessing_partition(
    manifest_path: str | Path,
    split: str,
    *,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    require_registered_protocol: bool = True,
) -> LoadedCausalPreprocessingPartition:
    """Open exactly one validated physical partition."""

    np = _require_numpy()
    manifest = load_causal_preprocessing_manifest(
        manifest_path,
        max_total_bytes=max_total_bytes,
        require_registered_protocol=require_registered_protocol,
    )
    if split not in PARTITION_NAMES:
        raise ValueError(f"unsupported fixture partition: {split}")
    protocol = _protocol_from_dict(manifest["protocol"])
    row = manifest["partitions"][split]
    source = Path(manifest_path).parent / row["path"]
    with np.load(source, allow_pickle=False) as data:
        members = tuple(data.files)
        forbidden = set(members).intersection(FORBIDDEN_MEMBERS)
        if forbidden:
            raise ValueError(f"fixture contains forbidden members: {sorted(forbidden)}")
        if set(members) != set(ARRAY_MEMBERS):
            raise ValueError("fixture NPZ member set mismatch")
        arrays = {
            "signals": data["signals"].copy(),
            "input_lengths": data["input_lengths"].copy(),
            "item_ids": data["item_ids"].copy(),
            "source_start_samples": data["source_start_samples"].copy(),
        }
        metadata = json.loads(str(data["metadata"].item()))
    _validate_partition_arrays(
        arrays,
        metadata=metadata,
        split=split,
        seed=_partition_seed(protocol, split),
        protocol=protocol,
    )
    return LoadedCausalPreprocessingPartition(
        split=split,
        signals=arrays["signals"],
        input_lengths=arrays["input_lengths"],
        item_ids=arrays["item_ids"],
        source_start_samples=arrays["source_start_samples"],
        metadata=metadata,
        opened_members=members,
    )


def summarize_causal_preprocessing_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return a compact metadata-only fixture summary."""

    return {
        "schema": manifest["schema"],
        "proof_posture": manifest["proof_posture"],
        "target_free": manifest["target_free"],
        "registered_protocol_match": manifest["registered_protocol_match"],
        "protocol_sha256": manifest["protocol_sha256"],
        "static_filter_bundle_sha256": manifest["static_filter_bundle_sha256"],
        "partitions": {
            split: {
                "seed": manifest["partitions"][split]["seed"],
                "items": manifest["partitions"][split]["items"],
                "bytes": manifest["partitions"][split]["bytes"],
                "sha256": manifest["partitions"][split]["sha256"],
                "array_members_opened": 0,
            }
            for split in PARTITION_NAMES
        },
        "artifacts": manifest["artifacts"],
        "warnings": manifest["warnings"],
        "claim_boundaries": manifest["claim_boundaries"],
    }


def _make_signal_family(
    np: Any,
    rng: Any,
    *,
    family: str,
    local_index: int,
    channels: int,
    length: int,
    sampling_rate_hz: float,
) -> Any:
    time = np.arange(length, dtype="float64") / sampling_rate_hz
    rows = []
    for channel in range(channels):
        phase = float(rng.uniform(-math.pi, math.pi))
        scale = 0.72 + 0.06 * channel
        if family == SIGNAL_FAMILIES[0]:
            frequencies = (5.0, 20.0, 35.0, 55.0, 99.0, 149.0, 250.0)
            row = sum(
                (0.42 / (1.0 + index * 0.25))
                * np.sin(2.0 * math.pi * frequency * time + phase + index * 0.17)
                for index, frequency in enumerate(frequencies)
            )
        elif family == SIGNAL_FAMILIES[1]:
            f0, f1 = ((2.0, 480.0) if local_index == 0 else (480.0, 2.0))
            duration = max(time[-1], 1.0 / sampling_rate_hz)
            slope = (f1 - f0) / duration
            row = 1.4 * np.sin(2.0 * math.pi * (f0 * time + 0.5 * slope * time**2) + phase)
        elif family == SIGNAL_FAMILIES[2]:
            row = np.zeros(length, dtype="float64")
            positions = [0, 1, length // 2, length - 2, length - 1]
            for index, position in enumerate(positions):
                row[position] = (2.8 - 0.3 * index) * (-1.0 if index % 2 else 1.0)
        elif family == SIGNAL_FAMILIES[3]:
            row = np.zeros(length, dtype="float64")
            first = length // 5
            second = 3 * length // 5
            row[first:second] = 2.1 if local_index == 0 else -2.1
            row[second:] = -0.8 if local_index == 0 else 0.8
        elif family == SIGNAL_FAMILIES[4]:
            ramp = np.linspace(-1.8, 1.8, length, dtype="float64")
            row = ramp + 0.35 * np.sign(np.sin(2.0 * math.pi * 3.0 * time + phase))
            if local_index:
                row = row[::-1].copy()
        elif family == SIGNAL_FAMILIES[5]:
            row = rng.normal(0.0, 0.62, length)
            row += 0.22 * np.sin(2.0 * math.pi * 17.0 * time + phase)
            row[min(length - 1, 13 + channel * 17)] = 3.8 * (-1.0 if local_index else 1.0)
        else:  # pragma: no cover - guarded by protocol validation
            raise ValueError(f"unknown signal family: {family}")
        rows.append(np.clip(scale * row, -4.0, 4.0))
    return np.asarray(rows, dtype="float32")


def _validate_protocol(protocol: CausalPreprocessingFixtureProtocol) -> None:
    if protocol.items_per_partition != len(protocol.item_lengths):
        raise ValueError("fixture item count must match exact lengths")
    if protocol.items_per_partition != len(SIGNAL_FAMILIES) * protocol.items_per_family:
        raise ValueError("fixture family count must cover every item")
    if protocol.channels != 5 or protocol.sampling_rate_hz != 1000.0:
        raise ValueError("fixture geometry must remain 5 channels at 1,000 Hz")
    if any(length <= 0 or length > 4096 for length in protocol.item_lengths):
        raise ValueError("fixture item length exceeds registered cap")
    if protocol.value_min != -4.0 or protocol.value_max != 4.0:
        raise ValueError("fixture value bounds must remain [-4, 4]")


def _validate_split_seed(
    protocol: CausalPreprocessingFixtureProtocol, split: str, seed: int
) -> None:
    if split not in PARTITION_NAMES:
        raise ValueError(f"unsupported fixture partition: {split}")
    expected = _partition_seed(protocol, split)
    if seed != expected:
        raise ValueError(f"{split} seed must be {expected}")


def _partition_seed(protocol: CausalPreprocessingFixtureProtocol, split: str) -> int:
    return protocol.development_seed if split == "development" else protocol.qualification_seed


def _validate_partition_arrays(
    arrays: Mapping[str, Any],
    *,
    metadata: Mapping[str, Any],
    split: str,
    seed: int,
    protocol: CausalPreprocessingFixtureProtocol,
) -> None:
    np = _require_numpy()
    _validate_split_seed(protocol, split, seed)
    signals = arrays["signals"]
    lengths = arrays["input_lengths"]
    item_ids = arrays["item_ids"]
    starts = arrays["source_start_samples"]
    expected_shape = (protocol.items_per_partition, protocol.channels, protocol.maximum_samples)
    if signals.shape != expected_shape or signals.dtype != np.dtype("float32"):
        raise ValueError("fixture signal shape or dtype mismatch")
    if lengths.dtype != np.dtype("int32") or tuple(lengths.tolist()) != protocol.item_lengths:
        raise ValueError("fixture input-length identity mismatch")
    if item_ids.ndim != 1 or len(set(item_ids.tolist())) != protocol.items_per_partition:
        raise ValueError("fixture item IDs must be unique")
    if starts.shape != (protocol.items_per_partition,) or starts.dtype != np.dtype("int64"):
        raise ValueError("fixture source starts must be int64 per item")
    if not np.equal(starts % 10, 0).all():
        raise ValueError("fixture source starts must preserve decimation phase")
    if not np.isfinite(signals).all():
        raise ValueError("fixture signals contain nonfinite values")
    if float(signals.min()) < protocol.value_min or float(signals.max()) > protocol.value_max:
        raise ValueError("fixture signals exceed registered bounds")
    for index, length in enumerate(lengths.tolist()):
        if not np.equal(signals[index, :, int(length) :], 0.0).all():
            raise ValueError("fixture padding must be exact zero")
    if metadata.get("split") != split or metadata.get("seed") != seed:
        raise ValueError("fixture metadata identity mismatch")
    if not metadata.get("target_free") or metadata.get("protocol_sha256") != protocol.protocol_sha256:
        raise ValueError("fixture metadata protocol mismatch")


def _partition_manifest_row(
    *,
    split: str,
    seed: int,
    payload: bytes,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "split": split,
        "seed": int(seed),
        "path": f"{split}.npz",
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "items": int(arrays["signals"].shape[0]),
        "channels": int(arrays["signals"].shape[1]),
        "maximum_samples": int(arrays["signals"].shape[2]),
        "input_lengths": arrays["input_lengths"].tolist(),
        "item_ids": arrays["item_ids"].tolist(),
        "source_start_samples": arrays["source_start_samples"].tolist(),
        "array_members": list(ARRAY_MEMBERS),
        "family_counts": metadata["family_counts"],
    }


def _validate_manifest_partition_identity(
    row: Mapping[str, Any],
    *,
    split: str,
    protocol: CausalPreprocessingFixtureProtocol,
) -> None:
    if row.get("split") != split or row.get("seed") != _partition_seed(protocol, split):
        raise ValueError(f"{split} fixture identity mismatch")
    if row.get("items") != protocol.items_per_partition or row.get("channels") != 5:
        raise ValueError(f"{split} fixture count or channel mismatch")
    if tuple(row.get("input_lengths", ())) != protocol.item_lengths:
        raise ValueError(f"{split} fixture lengths mismatch")
    if tuple(row.get("array_members", ())) != ARRAY_MEMBERS:
        raise ValueError(f"{split} fixture array-member mismatch")
    if len(set(row.get("item_ids", ()))) != protocol.items_per_partition:
        raise ValueError(f"{split} fixture item IDs are malformed")


def _protocol_from_dict(value: Mapping[str, Any]) -> CausalPreprocessingFixtureProtocol:
    return CausalPreprocessingFixtureProtocol(
        development_seed=int(value["development_seed"]),
        qualification_seed=int(value["qualification_seed"]),
        items_per_partition=int(value["items_per_partition"]),
        items_per_family=int(value["items_per_family"]),
        channels=int(value["channels"]),
        sampling_rate_hz=float(value["sampling_rate_hz"]),
        item_lengths=tuple(int(item) for item in value["item_lengths"]),
        value_min=float(value["value_min"]),
        value_max=float(value["value_max"]),
    )


def _deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    np = _require_numpy()
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


def _npz_array_members(path: Path) -> tuple[str, ...]:
    try:
        with zipfile.ZipFile(path, mode="r") as archive:
            names = archive.namelist()
    except zipfile.BadZipFile as exc:
        raise ValueError(f"fixture partition is not a valid NPZ archive: {path.name}") from exc
    members: list[str] = []
    for name in names:
        member = PurePosixPath(name)
        if member.is_absolute() or len(member.parts) != 1 or member.suffix != ".npy":
            raise ValueError(f"fixture partition contains an unsafe member: {name}")
        members.append(member.stem)
    if len(members) != len(set(members)):
        raise ValueError("fixture partition contains duplicate array members")
    return tuple(members)


def _metadata_array(metadata: Mapping[str, Any]):
    np = _require_numpy()
    return np.asarray(_canonical_json(metadata))


def _manifest_payload_with_sizes(manifest: dict[str, Any]) -> bytes:
    for _ in range(5):
        payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
        manifest["artifacts"]["manifest_bytes"] = len(payload)
        manifest["artifacts"]["total_bytes"] = (
            manifest["artifacts"]["partition_bytes"] + len(payload)
        )
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _validate_authorized_output_path(output: Path) -> None:
    resolved = output.resolve(strict=False)
    roots = [
        (_repo_root() / "cache" / "loop25").resolve(strict=False),
        (_repo_root() / "outputs" / "loop25").resolve(strict=False),
        (_repo_root() / ".codex_work" / "loop25").resolve(strict=False),
    ]
    if not any(resolved != root and root in resolved.parents for root in roots):
        raise ValueError(
            "registered Loop 25 output must be nested under cache/loop25, "
            "outputs/loop25, or .codex_work/loop25"
        )


def _sha256_json(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - optional dependency boundary
        raise RuntimeError("Loop 25 fixture requires NumPy. Install neurodecodekit[neuro].") from exc
    return np
