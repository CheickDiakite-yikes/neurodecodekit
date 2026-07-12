"""Deterministic target-free fixture for the Loop 24 precision/runtime gate."""

from __future__ import annotations

import hashlib
import io
import json
import math
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


SCHEMA_NAME = "b2q-local-precision-runtime-fixture"
SCHEMA_VERSION = 0
MANIFEST_SCHEMA_NAME = "b2q-local-precision-runtime-fixture-manifest"
MANIFEST_SCHEMA_VERSION = 0
PROOF_POSTURE = "target_free_synthetic_numeric_stress_fixture_only"
PARTITION_NAMES = ("selection", "qualification")
ARRAY_MEMBERS = ("signals", "input_lengths", "item_ids", "metadata")
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
    "recording_path",
)
WAVEFORM_FAMILIES = (
    "bounded_sinusoid_mixture",
    "bounded_linear_chirp",
    "bounded_impulse_train",
    "bounded_piecewise_ramp",
    "bounded_piecewise_constant",
    "bounded_seeded_gaussian_mixture",
)
DEFAULT_MAX_FIXTURE_BYTES = 512 * 1024
CONTRACT_RELATIVE_PATH = Path("registries/local_precision_runtime_contract.v0.json")


@dataclass(frozen=True)
class PrecisionRuntimeFixtureProtocol:
    """Frozen generator constants copied from the preregistered contract."""

    selection_seed: int = 2401
    qualification_seed: int = 2402
    items_per_partition: int = 48
    items_per_family: int = 8
    channels: int = 5
    sampling_rate_hz: float = 100.0
    minimum_samples: int = 64
    maximum_samples: int = 128
    length_multiple_samples: int = 4
    value_min: float = -4.0
    value_max: float = 4.0

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["waveform_families"] = list(WAVEFORM_FAMILIES)
        value["schema_name"] = SCHEMA_NAME
        value["schema_version"] = SCHEMA_VERSION
        return value

    @property
    def protocol_sha256(self) -> str:
        return _sha256_json(self.to_dict())


@dataclass(frozen=True)
class LoadedPrecisionRuntimePartition:
    """One validated physical input-only partition."""

    split: str
    signals: Any
    input_lengths: Any
    item_ids: Any
    metadata: dict[str, Any]
    opened_members: tuple[str, ...]

    @property
    def array_bytes(self) -> int:
        return int(
            self.signals.nbytes + self.input_lengths.nbytes + self.item_ids.nbytes
        )

    @property
    def valid_samples(self) -> int:
        return int(self.input_lengths.sum())


def registered_precision_runtime_fixture_protocol() -> PrecisionRuntimeFixtureProtocol:
    """Return and verify the exact fixture constants in the machine contract."""

    protocol = PrecisionRuntimeFixtureProtocol()
    contract = _load_contract()
    fixture = contract["fixture_contract"]
    if fixture["schema_name"] != SCHEMA_NAME or fixture["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError("Loop 24 fixture schema drifted from the frozen contract")
    expected = {
        "selection_seed": fixture["selection"]["seed"],
        "qualification_seed": fixture["qualification"]["seed"],
        "items_per_partition": fixture["selection"]["items"],
        "items_per_family": fixture["items_per_waveform_family_per_partition"],
        "channels": fixture["channels"],
        "sampling_rate_hz": fixture["sampling_rate_hz"],
        "minimum_samples": fixture["minimum_samples_per_item"],
        "maximum_samples": fixture["maximum_samples_per_item"],
        "length_multiple_samples": fixture["length_multiple_samples"],
        "value_min": fixture["value_bounds_inclusive"][0],
        "value_max": fixture["value_bounds_inclusive"][1],
    }
    for name, expected_value in expected.items():
        if getattr(protocol, name) != expected_value:
            raise RuntimeError(f"Loop 24 fixture protocol drifted at {name}")
    if tuple(fixture["members"]) != ARRAY_MEMBERS:
        raise RuntimeError("Loop 24 fixture member contract drifted")
    if tuple(fixture["forbidden_members"]) != FORBIDDEN_MEMBERS:
        raise RuntimeError("Loop 24 forbidden member contract drifted")
    if tuple(fixture["waveform_families"]) != WAVEFORM_FAMILIES:
        raise RuntimeError("Loop 24 waveform family contract drifted")
    return protocol


def prepare_precision_runtime_fixture(
    out_dir: str | Path,
    *,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    protocol: PrecisionRuntimeFixtureProtocol | None = None,
    require_registered_protocol: bool = True,
    enforce_authorized_output_root: bool | None = None,
) -> dict[str, Any]:
    """Create two deterministic physical NPZ partitions plus one JSON manifest."""

    registered = registered_precision_runtime_fixture_protocol()
    selected = protocol or registered
    _validate_protocol(selected)
    registered_match = selected == registered
    if require_registered_protocol and not registered_match:
        raise ValueError("precision/runtime fixture override is not the registered protocol")
    _validate_output_cap(max_total_bytes)
    output_dir = Path(out_dir)
    enforce_output_root = (
        require_registered_protocol
        if enforce_authorized_output_root is None
        else enforce_authorized_output_root
    )
    if enforce_output_root:
        _validate_authorized_output_path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Refusing to replace existing fixture directory: {output_dir}")

    partition_payloads: dict[str, bytes] = {}
    partition_rows: dict[str, dict[str, Any]] = {}
    for split in PARTITION_NAMES:
        seed = _partition_seed(selected, split)
        arrays, metadata = make_precision_runtime_partition(
            split=split,
            seed=seed,
            protocol=selected,
        )
        payload = _deterministic_npz_bytes({**arrays, "metadata": _metadata_array(metadata)})
        file_name = f"{split}.npz"
        partition_payloads[split] = payload
        partition_rows[split] = _partition_manifest_row(
            split=split,
            path=file_name,
            payload=payload,
            arrays=arrays,
            metadata=metadata,
        )

    contract_path = _repo_root() / CONTRACT_RELATIVE_PATH
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
            "sha256": _file_sha256(contract_path),
        },
        "array_members": list(ARRAY_MEMBERS),
        "forbidden_members": list(FORBIDDEN_MEMBERS),
        "partitions": partition_rows,
        "access_contract": {
            "manifest_inspection_opens_array_members": False,
            "physical_partition_files_required": True,
            "partition_item_ids_must_be_disjoint": True,
        },
        "generation": {
            "generated_from_model_outputs": False,
            "contains_brainlike_or_neural_claim": False,
            "uses_target_label_or_text": False,
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
            "Qualification is physically present but may be opened only after a replacement candidate is frozen.",
        ],
        "claim_boundaries": [
            "This fixture validates only bounded input and split mechanics.",
            "It does not establish neural information, decoding, latency, EEG usefulness, or hardware behavior.",
        ],
    }
    manifest_payload = _manifest_payload_with_sizes(manifest)
    total_bytes = sum(len(value) for value in partition_payloads.values()) + len(
        manifest_payload
    )
    if total_bytes > max_total_bytes:
        raise ValueError(
            f"precision/runtime fixture would write {total_bytes} bytes, exceeding cap "
            f"{max_total_bytes}"
        )

    output_dir.mkdir(parents=True, exist_ok=False)
    for split, payload in partition_payloads.items():
        (output_dir / f"{split}.npz").write_bytes(payload)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_bytes(manifest_payload)
    loaded = load_precision_runtime_manifest(
        manifest_path,
        max_total_bytes=max_total_bytes,
        require_registered_protocol=require_registered_protocol,
    )
    loaded["artifacts"]["output_directory"] = output_dir.name
    return loaded


def make_precision_runtime_partition(
    *,
    split: str,
    seed: int,
    protocol: PrecisionRuntimeFixtureProtocol | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate one input-only partition without consulting a model or decoder."""

    np = _require_numpy()
    selected = protocol or registered_precision_runtime_fixture_protocol()
    _validate_split_seed(selected, split, seed)
    rng = np.random.default_rng(seed)
    shape = (
        selected.items_per_partition,
        selected.channels,
        selected.maximum_samples,
    )
    signals = np.zeros(shape, dtype="float32")
    input_lengths = np.empty(selected.items_per_partition, dtype="int32")
    item_ids: list[str] = []
    family_by_item: list[str] = []
    length_values = np.linspace(
        selected.minimum_samples,
        selected.maximum_samples,
        selected.items_per_family,
        dtype="int32",
    )
    length_values = (
        length_values // selected.length_multiple_samples
        * selected.length_multiple_samples
    )
    length_values[-1] = selected.maximum_samples

    cursor = 0
    for family_index, family in enumerate(WAVEFORM_FAMILIES):
        order = rng.permutation(selected.items_per_family)
        for local_index, length_index in enumerate(order.tolist()):
            length = int(length_values[length_index])
            row = _make_waveform_family(
                np,
                rng,
                family=family,
                channels=selected.channels,
                length=length,
                sampling_rate_hz=selected.sampling_rate_hz,
            )
            signals[cursor, :, :length] = row
            input_lengths[cursor] = length
            item_ids.append(
                f"loop24-{split}-{family_index:02d}-{local_index:02d}"
            )
            family_by_item.append(family)
            cursor += 1
    if cursor != selected.items_per_partition:
        raise RuntimeError("Loop 24 fixture item count drifted")
    item_id_array = np.asarray(item_ids, dtype="U40")
    arrays = {
        "signals": signals,
        "input_lengths": input_lengths,
        "item_ids": item_id_array,
    }
    _validate_partition_arrays(
        arrays,
        split=split,
        seed=seed,
        protocol=selected,
        metadata=None,
    )
    metadata = {
        "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
        "proof_posture": PROOF_POSTURE,
        "target_free": True,
        "split": split,
        "seed": int(seed),
        "protocol_sha256": selected.protocol_sha256,
        "signal_layout": "items,channels,time",
        "signal_dtype": "float32",
        "padding_value": 0.0,
        "family_by_item": family_by_item,
        "family_counts": {
            family: family_by_item.count(family) for family in WAVEFORM_FAMILIES
        },
        "item_ids_sha256": _array_sha256(item_id_array),
        "signals_sha256": _array_sha256(signals),
        "input_lengths_sha256": _array_sha256(input_lengths),
        "generator": {
            "model_outputs_read": 0,
            "target_label_text_reads": 0,
            "real_or_consumed_data_reads": 0,
            "training_runs": 0,
        },
    }
    return arrays, metadata


def load_precision_runtime_manifest(
    path: str | Path,
    *,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    require_registered_protocol: bool = True,
) -> dict[str, Any]:
    """Validate manifest identity and partition files without opening NPZ members."""

    _validate_output_cap(max_total_bytes)
    manifest_path = Path(path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("precision/runtime fixture manifest is not valid JSON") from exc
    if not isinstance(manifest, dict):
        raise ValueError("precision/runtime fixture manifest must be an object")
    schema = manifest.get("schema") or {}
    if schema != {"name": MANIFEST_SCHEMA_NAME, "version": MANIFEST_SCHEMA_VERSION}:
        raise ValueError("unsupported precision/runtime fixture manifest schema")
    if manifest.get("fixture_schema") != {
        "name": SCHEMA_NAME,
        "version": SCHEMA_VERSION,
    }:
        raise ValueError("precision/runtime fixture schema identity is invalid")
    if manifest.get("proof_posture") != PROOF_POSTURE or manifest.get("target_free") is not True:
        raise ValueError("precision/runtime fixture proof posture is invalid")
    protocol = _protocol_from_dict(manifest.get("protocol"))
    registered = registered_precision_runtime_fixture_protocol()
    registered_match = protocol == registered
    if manifest.get("registered_protocol_match") is not registered_match:
        raise ValueError("precision/runtime registered protocol declaration is invalid")
    if require_registered_protocol and not registered_match:
        raise ValueError("precision/runtime fixture is not the registered protocol")
    if manifest.get("protocol_sha256") != protocol.protocol_sha256:
        raise ValueError("precision/runtime fixture protocol hash mismatch")
    contract = manifest.get("contract") or {}
    contract_path = _repo_root() / CONTRACT_RELATIVE_PATH
    if contract.get("path") != CONTRACT_RELATIVE_PATH.as_posix():
        raise ValueError("precision/runtime fixture contract path is invalid")
    if contract.get("sha256") != _file_sha256(contract_path):
        raise ValueError("precision/runtime fixture contract hash mismatch")
    if tuple(manifest.get("array_members") or ()) != ARRAY_MEMBERS:
        raise ValueError("precision/runtime fixture array member declaration drifted")
    if tuple(manifest.get("forbidden_members") or ()) != FORBIDDEN_MEMBERS:
        raise ValueError("precision/runtime fixture forbidden member declaration drifted")

    partitions = manifest.get("partitions")
    if (
        not isinstance(partitions, dict)
        or len(partitions) != len(PARTITION_NAMES)
        or set(partitions) != set(PARTITION_NAMES)
    ):
        raise ValueError("precision/runtime fixture must declare exact physical partitions")
    ids_by_split: dict[str, set[str]] = {}
    total_partition_bytes = 0
    for split in PARTITION_NAMES:
        row = partitions[split]
        if not isinstance(row, dict):
            raise ValueError(f"precision/runtime {split} manifest row is invalid")
        _validate_manifest_partition_row(row, split=split, protocol=protocol)
        relative = _safe_relative_path(row["path"], expected=f"{split}.npz")
        partition_path = manifest_path.parent / relative
        if not partition_path.is_file():
            raise ValueError(f"precision/runtime {split} partition file is missing")
        file_bytes = int(partition_path.stat().st_size)
        if row.get("bytes") != file_bytes:
            raise ValueError(f"precision/runtime {split} partition byte count mismatch")
        if not _is_sha256(row.get("sha256")):
            raise ValueError(f"precision/runtime {split} partition hash is invalid")
        total_partition_bytes += file_bytes
        ids_by_split[split] = set(str(value) for value in row["item_ids"])
    if ids_by_split["selection"].intersection(ids_by_split["qualification"]):
        raise ValueError("precision/runtime fixture partition item IDs overlap")

    artifacts = manifest.get("artifacts") or {}
    total_bytes = total_partition_bytes + int(manifest_path.stat().st_size)
    recorded_cap = artifacts.get("maximum_total_bytes")
    _validate_output_cap(recorded_cap)
    expected_artifacts = {
        "files": 3,
        "partition_bytes": total_partition_bytes,
        "manifest_bytes": int(manifest_path.stat().st_size),
        "total_bytes": total_bytes,
        "maximum_total_bytes": int(recorded_cap),
    }
    if artifacts != expected_artifacts:
        raise ValueError("precision/runtime fixture artifact accounting mismatch")
    if total_bytes > int(recorded_cap) or total_bytes > max_total_bytes:
        raise ValueError("precision/runtime fixture exceeds the configured byte cap")
    access = manifest.get("access_contract") or {}
    if access.get("manifest_inspection_opens_array_members") is not False:
        raise ValueError("precision/runtime manifest access declaration is invalid")
    generation = manifest.get("generation") or {}
    if generation != {
        "generated_from_model_outputs": False,
        "contains_brainlike_or_neural_claim": False,
        "uses_target_label_or_text": False,
    }:
        raise ValueError("precision/runtime fixture generation boundary is invalid")
    return manifest


def load_precision_runtime_partition(
    manifest_path: str | Path,
    split: str,
    *,
    max_total_bytes: int = DEFAULT_MAX_FIXTURE_BYTES,
    require_registered_protocol: bool = True,
) -> LoadedPrecisionRuntimePartition:
    """Open and strictly validate one authorized partition exactly once."""

    if split not in PARTITION_NAMES:
        raise ValueError(f"split must be one of: {', '.join(PARTITION_NAMES)}")
    manifest_file = Path(manifest_path)
    manifest = load_precision_runtime_manifest(
        manifest_file,
        max_total_bytes=max_total_bytes,
        require_registered_protocol=require_registered_protocol,
    )
    protocol = _protocol_from_dict(manifest["protocol"])
    row = manifest["partitions"][split]
    partition_path = manifest_file.parent / _safe_relative_path(
        row["path"], expected=f"{split}.npz"
    )
    if row.get("sha256") != _file_sha256(partition_path):
        raise ValueError(f"precision/runtime {split} partition hash mismatch")
    np = _require_numpy()
    try:
        with np.load(partition_path, allow_pickle=False) as data:
            members = tuple(data.files)
            member_set = set(members)
            forbidden = sorted(member_set.intersection(FORBIDDEN_MEMBERS))
            if forbidden:
                raise ValueError(
                    f"precision/runtime fixture contains forbidden members: {forbidden}"
                )
            if member_set != set(ARRAY_MEMBERS):
                missing = sorted(set(ARRAY_MEMBERS) - member_set)
                unexpected = sorted(member_set - set(ARRAY_MEMBERS))
                raise ValueError(
                    "precision/runtime partition member mismatch: "
                    f"missing={missing}, unexpected={unexpected}"
                )
            arrays = {
                "signals": data["signals"].copy(),
                "input_lengths": data["input_lengths"].copy(),
                "item_ids": data["item_ids"].copy(),
            }
            metadata = _decode_metadata(data["metadata"])
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        if isinstance(exc, ValueError) and str(exc).startswith("precision/runtime"):
            raise
        raise ValueError("precision/runtime partition cannot be read safely") from exc
    _validate_partition_arrays(
        arrays,
        split=split,
        seed=_partition_seed(protocol, split),
        protocol=protocol,
        metadata=metadata,
    )
    if arrays["item_ids"].tolist() != row["item_ids"]:
        raise ValueError("precision/runtime partition item IDs differ from manifest")
    for key, array_name in (
        ("signals_sha256", "signals"),
        ("input_lengths_sha256", "input_lengths"),
        ("item_ids_sha256", "item_ids"),
    ):
        if row.get(key) != _array_sha256(arrays[array_name]):
            raise ValueError(f"precision/runtime partition {array_name} hash mismatch")
        if metadata.get(key) != row.get(key):
            raise ValueError(f"precision/runtime partition metadata {key} mismatch")
    return LoadedPrecisionRuntimePartition(
        split=split,
        signals=arrays["signals"],
        input_lengths=arrays["input_lengths"],
        item_ids=arrays["item_ids"],
        metadata=metadata,
        opened_members=members,
    )


def summarize_precision_runtime_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Return the small metadata-only inspection surface used by the CLI."""

    return {
        "schema": manifest["schema"],
        "fixture_schema": manifest["fixture_schema"],
        "proof_posture": manifest["proof_posture"],
        "target_free": manifest["target_free"],
        "registered_protocol_match": manifest["registered_protocol_match"],
        "protocol_sha256": manifest["protocol_sha256"],
        "metadata_only_no_partition_arrays_opened": True,
        "partitions": {
            split: {
                key: manifest["partitions"][split][key]
                for key in (
                    "path",
                    "sha256",
                    "bytes",
                    "seed",
                    "items",
                    "signals_shape",
                    "minimum_length",
                    "maximum_length",
                    "valid_samples",
                    "family_counts",
                    "item_ids_sha256",
                )
            }
            for split in PARTITION_NAMES
        },
        "artifacts": manifest["artifacts"],
        "warnings": manifest["warnings"],
        "claim_boundaries": manifest["claim_boundaries"],
    }


def _partition_manifest_row(
    *,
    split: str,
    path: str,
    payload: bytes,
    arrays: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    lengths = arrays["input_lengths"]
    return {
        "path": path,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "bytes": len(payload),
        "seed": int(metadata["seed"]),
        "items": int(arrays["signals"].shape[0]),
        "signals_shape": [int(value) for value in arrays["signals"].shape],
        "signal_dtype": str(arrays["signals"].dtype),
        "minimum_length": int(lengths.min()),
        "maximum_length": int(lengths.max()),
        "valid_samples": int(lengths.sum()),
        "family_counts": dict(metadata["family_counts"]),
        "item_ids": [str(value) for value in arrays["item_ids"].tolist()],
        "item_ids_sha256": str(metadata["item_ids_sha256"]),
        "signals_sha256": str(metadata["signals_sha256"]),
        "input_lengths_sha256": str(metadata["input_lengths_sha256"]),
        "array_members": list(ARRAY_MEMBERS),
        "split": split,
    }


def _validate_manifest_partition_row(
    row: Mapping[str, Any],
    *,
    split: str,
    protocol: PrecisionRuntimeFixtureProtocol,
) -> None:
    expected_seed = _partition_seed(protocol, split)
    if row.get("split") != split or row.get("seed") != expected_seed:
        raise ValueError(f"precision/runtime {split} partition identity mismatch")
    if row.get("items") != protocol.items_per_partition:
        raise ValueError(f"precision/runtime {split} item count mismatch")
    if row.get("signals_shape") != [
        protocol.items_per_partition,
        protocol.channels,
        protocol.maximum_samples,
    ]:
        raise ValueError(f"precision/runtime {split} signal shape mismatch")
    if row.get("signal_dtype") != "float32":
        raise ValueError(f"precision/runtime {split} signal dtype mismatch")
    if row.get("minimum_length") < protocol.minimum_samples:
        raise ValueError(f"precision/runtime {split} minimum length is invalid")
    if row.get("maximum_length") > protocol.maximum_samples:
        raise ValueError(f"precision/runtime {split} maximum length is invalid")
    if row.get("array_members") != list(ARRAY_MEMBERS):
        raise ValueError(f"precision/runtime {split} member declaration mismatch")
    item_ids = row.get("item_ids")
    if not isinstance(item_ids, list) or len(item_ids) != protocol.items_per_partition:
        raise ValueError(f"precision/runtime {split} item IDs are invalid")
    if len(set(item_ids)) != len(item_ids):
        raise ValueError(f"precision/runtime {split} item IDs are not unique")
    expected_counts = {family: protocol.items_per_family for family in WAVEFORM_FAMILIES}
    if row.get("family_counts") != expected_counts:
        raise ValueError(f"precision/runtime {split} family counts mismatch")
    for name in ("sha256", "item_ids_sha256", "signals_sha256", "input_lengths_sha256"):
        if not _is_sha256(row.get(name)):
            raise ValueError(f"precision/runtime {split} {name} is invalid")
    if not isinstance(row.get("bytes"), int) or row["bytes"] < 1:
        raise ValueError(f"precision/runtime {split} byte count is invalid")


def _validate_partition_arrays(
    arrays: Mapping[str, Any],
    *,
    split: str,
    seed: int,
    protocol: PrecisionRuntimeFixtureProtocol,
    metadata: Mapping[str, Any] | None,
) -> None:
    np = _require_numpy()
    signals = np.asarray(arrays["signals"])
    lengths = np.asarray(arrays["input_lengths"])
    item_ids = np.asarray(arrays["item_ids"])
    expected_shape = (
        protocol.items_per_partition,
        protocol.channels,
        protocol.maximum_samples,
    )
    if signals.shape != expected_shape or signals.dtype != np.dtype("float32"):
        raise ValueError("precision/runtime signals must be registered float32 shape")
    if lengths.shape != (protocol.items_per_partition,) or not np.issubdtype(
        lengths.dtype, np.integer
    ):
        raise ValueError("precision/runtime input lengths must be one integer per item")
    if item_ids.shape != (protocol.items_per_partition,) or item_ids.dtype.kind not in {
        "U",
        "S",
    }:
        raise ValueError("precision/runtime item IDs must be a fixed string vector")
    if not np.isfinite(signals).all():
        raise ValueError("precision/runtime signals contain non-finite values")
    if float(signals.min()) < protocol.value_min or float(signals.max()) > protocol.value_max:
        raise ValueError("precision/runtime signals exceed frozen value bounds")
    if (lengths < protocol.minimum_samples).any() or (
        lengths > protocol.maximum_samples
    ).any():
        raise ValueError("precision/runtime input lengths exceed frozen bounds")
    if (lengths % protocol.length_multiple_samples).any():
        raise ValueError("precision/runtime input lengths violate the multiple rule")
    for index, raw_length in enumerate(lengths.tolist()):
        length = int(raw_length)
        if not np.equal(signals[index, :, length:], 0.0).all():
            raise ValueError("precision/runtime signal padding must be exactly zero")
    ids = [str(value) for value in item_ids.tolist()]
    if len(ids) != len(set(ids)):
        raise ValueError("precision/runtime item IDs must be unique")
    if any(not value.startswith(f"loop24-{split}-") for value in ids):
        raise ValueError("precision/runtime item ID split prefix is invalid")
    _validate_split_seed(protocol, split, seed)
    if metadata is None:
        return
    if metadata.get("schema") != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
        raise ValueError("precision/runtime partition metadata schema is invalid")
    if metadata.get("proof_posture") != PROOF_POSTURE:
        raise ValueError("precision/runtime partition proof posture is invalid")
    if metadata.get("target_free") is not True:
        raise ValueError("precision/runtime partition must declare target-free content")
    if metadata.get("split") != split or metadata.get("seed") != seed:
        raise ValueError("precision/runtime partition metadata identity mismatch")
    if metadata.get("protocol_sha256") != protocol.protocol_sha256:
        raise ValueError("precision/runtime partition protocol hash mismatch")
    families = metadata.get("family_by_item")
    if not isinstance(families, list) or len(families) != protocol.items_per_partition:
        raise ValueError("precision/runtime waveform family metadata is invalid")
    if set(families) != set(WAVEFORM_FAMILIES):
        raise ValueError("precision/runtime waveform family set is invalid")
    expected_counts = {family: protocol.items_per_family for family in WAVEFORM_FAMILIES}
    if metadata.get("family_counts") != expected_counts:
        raise ValueError("precision/runtime waveform family counts are invalid")
    generator = metadata.get("generator") or {}
    if generator != {
        "model_outputs_read": 0,
        "target_label_text_reads": 0,
        "real_or_consumed_data_reads": 0,
        "training_runs": 0,
    }:
        raise ValueError("precision/runtime fixture generator access boundary is invalid")


def _make_waveform_family(
    np,
    rng,
    *,
    family: str,
    channels: int,
    length: int,
    sampling_rate_hz: float,
):
    time_axis = np.arange(length, dtype="float64") / sampling_rate_hz
    rows = np.zeros((channels, length), dtype="float64")
    for channel in range(channels):
        if family == "bounded_sinusoid_mixture":
            frequencies = rng.uniform(0.8, 18.0, size=3)
            amplitudes = rng.uniform(0.2, 1.1, size=3)
            phases = rng.uniform(-math.pi, math.pi, size=3)
            rows[channel] = sum(
                amplitude * np.sin(2.0 * math.pi * frequency * time_axis + phase)
                for amplitude, frequency, phase in zip(
                    amplitudes, frequencies, phases, strict=True
                )
            )
        elif family == "bounded_linear_chirp":
            start_hz = float(rng.uniform(0.5, 5.0))
            end_hz = float(rng.uniform(12.0, 35.0))
            duration = max(float(time_axis[-1]), 1.0 / sampling_rate_hz)
            slope = (end_hz - start_hz) / duration
            phase = 2.0 * math.pi * (
                start_hz * time_axis + 0.5 * slope * np.square(time_axis)
            )
            rows[channel] = float(rng.uniform(0.8, 2.6)) * np.sin(
                phase + float(rng.uniform(-math.pi, math.pi))
            )
        elif family == "bounded_impulse_train":
            interval = int(rng.integers(5, 17))
            start = int(rng.integers(0, interval))
            positions = np.arange(start, length, interval)
            rows[channel, positions] = rng.uniform(-3.5, 3.5, size=len(positions))
            if len(positions):
                next_positions = positions + 1
                next_positions = next_positions[next_positions < length]
                rows[channel, next_positions] += rows[channel, positions[: len(next_positions)]] * 0.35
        elif family == "bounded_piecewise_ramp":
            knots = np.unique(
                np.concatenate(
                    ([0], rng.integers(1, max(2, length - 1), size=4), [length - 1])
                )
            )
            values = rng.uniform(-3.2, 3.2, size=len(knots))
            rows[channel] = np.interp(np.arange(length), knots, values)
        elif family == "bounded_piecewise_constant":
            boundaries = sorted(
                set([0, length, *rng.integers(1, length, size=5).tolist()])
            )
            for start, end in zip(boundaries[:-1], boundaries[1:], strict=True):
                rows[channel, start:end] = float(rng.uniform(-3.3, 3.3))
        elif family == "bounded_seeded_gaussian_mixture":
            sample_axis = np.arange(length, dtype="float64")
            for _ in range(4):
                center = float(rng.uniform(0, length - 1))
                width = float(rng.uniform(1.5, 12.0))
                amplitude = float(rng.uniform(-3.0, 3.0))
                rows[channel] += amplitude * np.exp(
                    -0.5 * np.square((sample_axis - center) / width)
                )
        else:  # pragma: no cover - protected by frozen family tuple
            raise ValueError(f"unsupported precision/runtime waveform family: {family}")
    maximum = float(np.max(np.abs(rows)))
    if maximum > 3.75:
        rows *= 3.75 / maximum
    rows = np.clip(rows, -4.0, 4.0).astype("float32")
    if not np.isfinite(rows).all():
        raise RuntimeError("precision/runtime waveform generation became non-finite")
    return rows


def _deterministic_npz_bytes(arrays: Mapping[str, Any]) -> bytes:
    """Write NumPy members into a fixed-timestamp ZIP container."""

    np = _require_numpy()
    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w") as archive:
        for name in ARRAY_MEMBERS:
            if name not in arrays:
                raise ValueError(f"missing deterministic NPZ member: {name}")
            value = np.asarray(arrays[name])
            member = io.BytesIO()
            np.lib.format.write_array(member, value, allow_pickle=False)
            info = zipfile.ZipInfo(
                filename=f"{name}.npy",
                date_time=(1980, 1, 1, 0, 0, 0),
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, member.getvalue(), compress_type=zipfile.ZIP_DEFLATED)
    return output.getvalue()


def _manifest_payload_with_sizes(manifest: dict[str, Any]) -> bytes:
    partition_bytes = int(manifest["artifacts"]["partition_bytes"])
    payload = b""
    for _ in range(10):
        manifest["artifacts"]["manifest_bytes"] = len(payload)
        manifest["artifacts"]["total_bytes"] = partition_bytes + len(payload)
        next_payload = _stable_json_bytes(manifest)
        if len(next_payload) == len(payload):
            manifest["artifacts"]["manifest_bytes"] = len(next_payload)
            manifest["artifacts"]["total_bytes"] = partition_bytes + len(next_payload)
            final_payload = _stable_json_bytes(manifest)
            if len(final_payload) == len(next_payload):
                return final_payload
        payload = next_payload
    raise RuntimeError("precision/runtime manifest byte accounting did not converge")


def _validate_output_cap(value: int) -> None:
    if not isinstance(value, int) or value < 1:
        raise ValueError("max_total_bytes must be a positive integer")
    if value > DEFAULT_MAX_FIXTURE_BYTES:
        raise ValueError("max_total_bytes cannot exceed the frozen 512 KiB cap")


def _protocol_from_dict(value: object) -> PrecisionRuntimeFixtureProtocol:
    if not isinstance(value, dict):
        raise ValueError("precision/runtime fixture protocol must be an object")
    if value.get("schema_name") != SCHEMA_NAME or value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("precision/runtime fixture protocol schema is invalid")
    if tuple(value.get("waveform_families") or ()) != WAVEFORM_FAMILIES:
        raise ValueError("precision/runtime fixture waveform families are invalid")
    fields = {
        name: value.get(name)
        for name in PrecisionRuntimeFixtureProtocol.__dataclass_fields__
    }
    try:
        protocol = PrecisionRuntimeFixtureProtocol(**fields)
    except (TypeError, ValueError) as exc:
        raise ValueError("precision/runtime fixture protocol fields are invalid") from exc
    _validate_protocol(protocol)
    if protocol.to_dict() != value:
        raise ValueError("precision/runtime fixture protocol contains unexpected fields")
    return protocol


def _validate_protocol(protocol: PrecisionRuntimeFixtureProtocol) -> None:
    integer_values = {
        "selection_seed": protocol.selection_seed,
        "qualification_seed": protocol.qualification_seed,
        "items_per_partition": protocol.items_per_partition,
        "items_per_family": protocol.items_per_family,
        "channels": protocol.channels,
        "minimum_samples": protocol.minimum_samples,
        "maximum_samples": protocol.maximum_samples,
        "length_multiple_samples": protocol.length_multiple_samples,
    }
    if any(not isinstance(value, int) or value < 1 for value in integer_values.values()):
        raise ValueError("precision/runtime fixture integer protocol values must be positive")
    if protocol.selection_seed == protocol.qualification_seed:
        raise ValueError("precision/runtime fixture partition seeds must differ")
    if protocol.items_per_partition != len(WAVEFORM_FAMILIES) * protocol.items_per_family:
        raise ValueError("precision/runtime fixture items must balance waveform families")
    if protocol.minimum_samples > protocol.maximum_samples:
        raise ValueError("precision/runtime fixture sample bounds are inverted")
    if protocol.minimum_samples % protocol.length_multiple_samples:
        raise ValueError("precision/runtime minimum length violates its multiple")
    if protocol.maximum_samples % protocol.length_multiple_samples:
        raise ValueError("precision/runtime maximum length violates its multiple")
    if not math.isfinite(protocol.sampling_rate_hz) or protocol.sampling_rate_hz <= 0:
        raise ValueError("precision/runtime sampling rate must be finite and positive")
    if (
        not math.isfinite(protocol.value_min)
        or not math.isfinite(protocol.value_max)
        or protocol.value_min >= protocol.value_max
    ):
        raise ValueError("precision/runtime signal bounds are invalid")


def _validate_split_seed(
    protocol: PrecisionRuntimeFixtureProtocol,
    split: str,
    seed: int,
) -> None:
    if split not in PARTITION_NAMES:
        raise ValueError(f"split must be one of: {', '.join(PARTITION_NAMES)}")
    expected = _partition_seed(protocol, split)
    if int(seed) != expected:
        raise ValueError(f"precision/runtime {split} seed must be {expected}")


def _partition_seed(protocol: PrecisionRuntimeFixtureProtocol, split: str) -> int:
    if split == "selection":
        return protocol.selection_seed
    if split == "qualification":
        return protocol.qualification_seed
    raise ValueError(f"unsupported precision/runtime split: {split}")


def _safe_relative_path(value: object, *, expected: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("precision/runtime partition path must be a nonempty string")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or value != expected:
        raise ValueError("precision/runtime partition path is unsafe or unexpected")
    return Path(*pure.parts)


def _validate_authorized_output_path(output_dir: Path) -> None:
    resolved = output_dir.expanduser().resolve(strict=False)
    root = _repo_root().resolve()
    allowed_roots = (
        root / "cache" / "loop24",
        root / "outputs" / "loop24",
        root / ".codex_work" / "loop24",
    )
    if not any(
        resolved != allowed.resolve(strict=False)
        and resolved.is_relative_to(allowed.resolve(strict=False))
        for allowed in allowed_roots
    ):
        raise ValueError(
            "registered Loop 24 fixture output must be nested under an authorized ignored root"
        )


def _metadata_array(metadata: Mapping[str, Any]):
    np = _require_numpy()
    return np.asarray(json.dumps(metadata, sort_keys=True, separators=(",", ":")))


def _decode_metadata(value: Any) -> dict[str, Any]:
    try:
        raw = value.item() if getattr(value, "shape", None) == () else value.tolist()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        metadata = json.loads(str(raw))
    except (AttributeError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("precision/runtime partition metadata is not valid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("precision/runtime partition metadata must be an object")
    return metadata


def _load_contract() -> dict[str, Any]:
    path = _repo_root() / CONTRACT_RELATIVE_PATH
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Loop 24 machine contract cannot be read") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Loop 24 machine contract must be an object")
    return value


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _array_sha256(value: Any) -> str:
    np = _require_numpy()
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(json.dumps(list(array.shape)).encode("ascii"))
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _sha256_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _stable_json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _require_numpy():
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "Loop 24 fixture generation requires NumPy: `pip install -e '.[ml]'`."
        ) from exc
    return np
