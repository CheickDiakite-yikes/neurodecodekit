"""Strict, dependency-free SourceChunk v0 validation and generated fixtures.

This module implements only the existing RW3 ``neurodecodekit.source_chunk``
envelope.  It performs no I/O and contains no adapter, device, model, target,
or real-data path.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
import struct
from types import MappingProxyType
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA_NAME = "neurodecodekit.source_chunk"
SCHEMA_VERSION = "0.1.0"
MAX_CHANNELS = 32
MAX_SAMPLES_PER_CHUNK = 4096

VALID_PAYLOAD_DOMAIN = b"NDK-SOURCE-VALID-PAYLOAD-v0\x00"
SEMANTIC_DOMAIN = b"NDK-SOURCE-SEMANTIC-v0\x00"
REPLAY_CONTRACT_SHA256 = "6e4ef54049d9a6f77f64e7b6cfd6b911bd97b5693386f16b62f9d466f66b0469"

RECORD_KINDS = frozenset(
    {"stream_start", "data", "gap", "reconnect", "stream_end", "source_error"}
)
PAYLOAD_DTYPES = frozenset({"float32", "float64"})
CLOCK_DOMAINS = frozenset(
    {
        "synthetic_relative_monotonic",
        "recording_relative",
        "brainflow_unix_source",
        "lsl_outlet_steady_clock",
        "lsl_inlet_steady_clock",
        "python_monotonic_ns_arrival",
        "device_clock_unmapped",
    }
)

TOP_LEVEL_KEYS = frozenset(
    {
        "schema",
        "record_kind",
        "identity",
        "sequence",
        "channels",
        "payload",
        "sample_axis",
        "timestamps",
        "packet_accounting",
        "anomalies",
        "causality",
        "provenance",
        "hashes",
        "warnings",
        "unavailable_fields",
    }
)
SCHEMA_KEYS = frozenset({"name", "version"})
IDENTITY_KEYS = frozenset(
    {
        "stream_id",
        "source_id",
        "source_item_id",
        "evidence_cohort_id",
        "modality",
        "device_type",
        "adapter_id",
        "adapter_version",
        "preset_or_stream_role",
    }
)
SEQUENCE_KEYS = frozenset(
    {
        "chunk_sequence_index",
        "correction_segment_index",
        "reconnect_generation",
        "first_record",
        "final_record",
    }
)
CHANNEL_KEYS = frozenset(
    {
        "names",
        "types",
        "units",
        "source_row_indices",
        "geometry_available_mask",
        "geometry_payload_sha256",
    }
)
PAYLOAD_KEYS = frozenset(
    {
        "layout",
        "dtype",
        "shape",
        "values",
        "valid_sample_count",
        "capacity_sample_count",
        "padding_mask",
    }
)
SAMPLE_AXIS_KEYS = frozenset(
    {
        "source_sample_indices",
        "first_source_sample_index",
        "stop_source_sample_index_exclusive",
        "nominal_sampling_rate_hz",
        "nominal_sample_period_sec",
    }
)
TIMESTAMP_KEYS = frozenset(
    {
        "source_clock_domain",
        "source_timestamps_sec",
        "corrected_clock_domain",
        "corrected_timestamps_sec",
        "correction_applied",
        "correction_method",
        "correction_ledger_sha256",
        "arrival_monotonic_start_ns",
        "arrival_monotonic_end_ns",
        "wall_clock_values_redacted",
    }
)
PACKET_KEYS = frozenset(
    {
        "raw_counter_available",
        "raw_counter_values",
        "unwrapped_counter_values",
        "counter_modulus",
        "gap_before_samples",
        "duplicate_sample_count",
        "out_of_order_sample_count",
        "counter_wrap_count",
    }
)
ANOMALY_KEYS = frozenset(
    {
        "timestamp_regression_count",
        "timestamp_duplicate_count",
        "clock_reset_before",
        "source_restarted_before",
        "inferred_gap_count",
        "proven_gap_count",
        "interpolation_performed",
    }
)
CAUSALITY_KEYS = frozenset(
    {
        "emits_only_received_samples",
        "producer_causal",
        "producer_right_context_samples",
        "internal_read_ahead_status",
        "required_left_context_samples",
        "required_right_context_samples",
        "end_to_end_latency_measured",
    }
)
PROVENANCE_KEYS = frozenset(
    {
        "source_manifest_sha256",
        "source_config_sha256",
        "contract_sha256",
        "device_registry_sha256",
        "split_protocol_sha256",
        "adapter_config_sha256",
    }
)
HASH_KEYS = frozenset(
    {"chunk_envelope_sha256", "valid_payload_sha256", "semantic_prefix_sha256"}
)
BINDING_KEYS = frozenset(
    {
        "schema",
        "identity",
        "channels",
        "payload_dtype",
        "nominal_sampling_rate_hz",
        "nominal_sample_period_sec",
        "source_clock_domain",
        "corrected_clock_domain",
        "correction_applied",
        "correction_method",
        "correction_ledger_sha256",
        "causality",
        "provenance",
    }
)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_NORMALIZED_KEYS = frozenset(
    {
        "target",
        "targets",
        "targettext",
        "targetlabel",
        "targetlabels",
        "label",
        "labels",
        "intendedtext",
        "referencetext",
        "groundtruth",
        "expectedoutput",
        "prediction",
        "predictions",
        "probability",
        "probabilities",
        "scorerstate",
        "scoringkey",
        "languagemodel",
        "languagemodelcontext",
        "prompttext",
    }
)


class SourceChunkRefusal(ValueError):
    """A fail-closed SourceChunk refusal with a stable machine identifier."""

    def __init__(self, refusal_id: str, detail: str) -> None:
        self.refusal_id = refusal_id
        self.detail = detail
        super().__init__(f"{refusal_id}: {detail}")


def _refuse(refusal_id: str, detail: str) -> None:
    raise SourceChunkRefusal(refusal_id, detail)


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _expect_int(value: Any, field: str, *, minimum: int = 0) -> int:
    if not _is_int(value) or value < minimum:
        _refuse("source_chunk_schema_invalid", f"{field} must be an integer >= {minimum}")
    return value


def _expect_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:
        _refuse("source_chunk_schema_invalid", f"{field} must be a boolean")
    return value


def _expect_string(value: Any, field: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        _refuse("source_chunk_schema_invalid", f"{field} must be a non-empty string")
    return value


def _expect_float(value: Any, field: str, refusal_id: str) -> float:
    if type(value) is not float or not math.isfinite(value):
        _refuse(refusal_id, f"{field} must be a finite float")
    return value


def _expect_hash(value: Any, field: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or _HEX64.fullmatch(value) is None:
        _refuse("source_config_or_contract_hash_mismatch", f"{field} must be lowercase SHA-256")
    return value


def _expect_mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        _refuse("source_chunk_schema_invalid", f"{field} must be an object")
    return value


def _expect_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        _refuse("source_chunk_schema_invalid", f"{field} must be an array")
    return value


def _expect_exact_keys(value: Mapping[str, Any], expected: frozenset[str], field: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        _refuse(
            "source_chunk_schema_invalid",
            f"{field} keys are not exact; missing={missing}, unknown={unknown}",
        )


def _scan_forbidden_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if not isinstance(key, str):
                _refuse("source_chunk_schema_invalid", f"{path} contains a non-string key")
            normalized = re.sub(r"[^a-z0-9]", "", key.lower())
            forbidden_prefix = normalized.startswith(
                ("target", "label", "prediction", "probability", "scorer")
            )
            forbidden_text = normalized.endswith("text") and not normalized.endswith("context")
            if normalized in _FORBIDDEN_NORMALIZED_KEYS or forbidden_prefix or forbidden_text:
                _refuse("forbidden_target_or_text_key", f"forbidden key at {path}.{key}")
            _scan_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _scan_forbidden_keys(child, f"{path}[{index}]")


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _thaw(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_thaw(child) for child in value]
    return value


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(child) for key, child in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(child) for child in value)
    if isinstance(value, tuple):
        return tuple(_freeze(child) for child in value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return the amended canonical UTF-8 JSON representation."""

    try:
        encoded = json.dumps(
            _thaw(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        _refuse("source_chunk_schema_invalid", f"canonical JSON encoding failed: {exc}")
    return encoded + b"\n"


def _hash_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _float_format(dtype: str) -> str:
    return "<f" if dtype == "float32" else "<d"


def _cast_generated_float(value: Any, dtype: str, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        _refuse("payload_shape_or_layout_invalid", f"{field} must be numeric")
    numeric = float(value)
    if not math.isfinite(numeric):
        _refuse("payload_contains_nonfinite_values", f"{field} is nonfinite")
    try:
        return struct.unpack(_float_format(dtype), struct.pack(_float_format(dtype), numeric))[0]
    except OverflowError:
        _refuse("payload_contains_nonfinite_values", f"{field} overflows {dtype}")


def _validate_exact_payload_float(value: Any, dtype: str, field: str) -> float:
    numeric = _expect_float(value, field, "payload_contains_nonfinite_values")
    try:
        cast = struct.unpack(_float_format(dtype), struct.pack(_float_format(dtype), numeric))[0]
    except OverflowError:
        _refuse("payload_contains_nonfinite_values", f"{field} overflows {dtype}")
    if struct.pack("<d", cast) != struct.pack("<d", numeric):
        _refuse("payload_dtype_not_allowed", f"{field} is not an exact declared {dtype} value")
    return numeric


def _is_positive_zero(value: float, dtype: str) -> bool:
    return struct.pack(_float_format(dtype), value) == (b"\x00" * (4 if dtype == "float32" else 8))


def _pack_valid_sample_major(payload: Mapping[str, Any]) -> bytes:
    dtype = payload["dtype"]
    valid = payload["valid_sample_count"]
    values = payload["values"]
    packed = bytearray()
    for sample_index in range(valid):
        for channel_row in values:
            packed.extend(struct.pack(_float_format(dtype), channel_row[sample_index]))
    return bytes(packed)


def compute_valid_payload_sha256(payload: Mapping[str, Any]) -> str:
    """Hash valid samples in amended little-endian sample-major order."""

    dtype = payload["dtype"]
    channel_count = len(payload["values"])
    valid_count = payload["valid_sample_count"]
    dtype_bytes = dtype.encode("ascii")
    preimage = (
        VALID_PAYLOAD_DOMAIN
        + struct.pack(">H", len(dtype_bytes))
        + dtype_bytes
        + struct.pack(">II", channel_count, valid_count)
        + _pack_valid_sample_major(payload)
    )
    return hashlib.sha256(preimage).hexdigest()


def compute_chunk_envelope_sha256(record: Mapping[str, Any]) -> str:
    """Hash a complete envelope while omitting only its own hash field."""

    envelope = _thaw(record)
    hashes = dict(envelope["hashes"])
    hashes.pop("chunk_envelope_sha256", None)
    envelope["hashes"] = hashes
    return _hash_json(envelope)


@dataclass(frozen=True, slots=True)
class SourceBindings:
    """Immutable SourceChunk fields that must not change within a stream."""

    _record: Mapping[str, Any]
    canonical_bytes: bytes
    sha256: str

    @classmethod
    def from_record(cls, record: Mapping[str, Any]) -> SourceBindings:
        binding = {
            "schema": _thaw(record["schema"]),
            "identity": _thaw(record["identity"]),
            "channels": _thaw(record["channels"]),
            "payload_dtype": record["payload"]["dtype"],
            "nominal_sampling_rate_hz": record["sample_axis"]["nominal_sampling_rate_hz"],
            "nominal_sample_period_sec": record["sample_axis"]["nominal_sample_period_sec"],
            "source_clock_domain": record["timestamps"]["source_clock_domain"],
            "corrected_clock_domain": record["timestamps"]["corrected_clock_domain"],
            "correction_applied": record["timestamps"]["correction_applied"],
            "correction_method": record["timestamps"]["correction_method"],
            "correction_ledger_sha256": record["timestamps"]["correction_ledger_sha256"],
            "causality": _thaw(record["causality"]),
            "provenance": _thaw(record["provenance"]),
        }
        _expect_exact_keys(binding, BINDING_KEYS, "bindings")
        encoded = canonical_json_bytes(binding)
        return cls(_freeze(binding), encoded, hashlib.sha256(encoded).hexdigest())

    @classmethod
    def generated(
        cls,
        *,
        channel_names: Sequence[str] = ("C3", "C4"),
        channel_types: Sequence[str] | None = None,
        channel_units: Sequence[str] | None = None,
        dtype: str = "float64",
        nominal_sampling_rate_hz: float = 128.0,
        seed: str = "fictional-stream-0",
        modality: str = "synthetic_eeg",
        device_type: str = "generated_fixture",
    ) -> SourceBindings:
        if not isinstance(dtype, str) or dtype not in PAYLOAD_DTYPES:
            _refuse("payload_dtype_not_allowed", f"unsupported generated dtype {dtype!r}")
        if isinstance(channel_names, (str, bytes)):
            _refuse("channel_contract_changed_midstream", "channel_names must be an array")
        if isinstance(channel_types, (str, bytes)) or isinstance(channel_units, (str, bytes)):
            _refuse("channel_contract_changed_midstream", "channel types and units must be arrays")
        names = list(channel_names)
        types = list(channel_types or ("EEG" for _ in names))
        units = list(channel_units or ("uV" for _ in names))
        if not names or len(names) > MAX_CHANNELS or len(types) != len(names) or len(units) != len(names):
            _refuse("resource_cap_exceeded", "generated channel contract is invalid or exceeds 32")
        if isinstance(nominal_sampling_rate_hz, bool) or not isinstance(
            nominal_sampling_rate_hz, (int, float)
        ):
            _refuse("source_chunk_schema_invalid", "generated sampling rate must be numeric")
        rate = float(nominal_sampling_rate_hz)
        if not math.isfinite(rate) or rate <= 0.0 or rate > 4096.0:
            _refuse("resource_cap_exceeded", "generated sampling rate is outside (0, 4096]")

        def digest(label: str) -> str:
            return hashlib.sha256(f"{seed}:{label}".encode("utf-8")).hexdigest()

        identity = {
            "stream_id": digest("stream")[:24],
            "source_id": digest("source")[:24],
            "source_item_id": digest("item")[:24],
            "evidence_cohort_id": "fictional-generated-only",
            "modality": modality,
            "device_type": device_type,
            "adapter_id": "pure_python_synthetic_replay",
            "adapter_version": "0.1.0",
            "preset_or_stream_role": "generated-primary",
        }
        channels = {
            "names": names,
            "types": types,
            "units": units,
            "source_row_indices": list(range(len(names))),
            "geometry_available_mask": [False] * len(names),
            "geometry_payload_sha256": None,
        }
        correction_ledger = digest("identity-clock-correction")
        provenance = {
            "source_manifest_sha256": digest("manifest"),
            "source_config_sha256": digest("source-config"),
            "contract_sha256": REPLAY_CONTRACT_SHA256,
            "device_registry_sha256": digest("device-registry"),
            "split_protocol_sha256": digest("split-protocol"),
            "adapter_config_sha256": digest("adapter-config"),
        }
        causality = {
            "emits_only_received_samples": True,
            "producer_causal": True,
            "producer_right_context_samples": 0,
            "internal_read_ahead_status": "none",
            "required_left_context_samples": 0,
            "required_right_context_samples": 0,
            "end_to_end_latency_measured": False,
        }
        record = {
            "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
            "identity": identity,
            "channels": channels,
            "payload": {"dtype": dtype},
            "sample_axis": {
                "nominal_sampling_rate_hz": rate,
                "nominal_sample_period_sec": 1.0 / rate,
            },
            "timestamps": {
                "source_clock_domain": "synthetic_relative_monotonic",
                "corrected_clock_domain": "synthetic_relative_monotonic",
                "correction_applied": True,
                "correction_method": "generated_identity_mapping",
                "correction_ledger_sha256": correction_ledger,
            },
            "causality": causality,
            "provenance": provenance,
        }
        # from_record reads only immutable fields and is intentionally I/O-free.
        return cls.from_record(record)

    @property
    def record(self) -> Mapping[str, Any]:
        return self._record

    def to_dict(self) -> dict[str, Any]:
        return _thaw(self._record)


@dataclass(frozen=True, slots=True)
class SemanticPrefixState:
    """Serializable semantic-chain state, without an implementation hash object."""

    bindings_sha256: str
    digest_sha256: str
    element_count: int

    @classmethod
    def initial(cls, bindings: SourceBindings) -> SemanticPrefixState:
        preimage = (
            SEMANTIC_DOMAIN
            + struct.pack(">Q", len(bindings.canonical_bytes))
            + bindings.canonical_bytes
        )
        return cls(bindings.sha256, hashlib.sha256(preimage).hexdigest(), 0)

    def advance(self, element: bytes) -> SemanticPrefixState:
        previous = bytes.fromhex(self.digest_sha256)
        digest = hashlib.sha256(
            SEMANTIC_DOMAIN + previous + struct.pack(">Q", len(element)) + element
        ).hexdigest()
        return SemanticPrefixState(self.bindings_sha256, digest, self.element_count + 1)


def _float64_bits_hex(value: float) -> str:
    return struct.pack("<d", value).hex()


def _semantic_elements(record: Mapping[str, Any]) -> Iterator[bytes]:
    kind = record["record_kind"]
    sequence = record["sequence"]
    sample_axis = record["sample_axis"]
    timestamps = record["timestamps"]
    packet = record["packet_accounting"]
    payload = record["payload"]
    if kind == "data":
        packed_width = 4 if payload["dtype"] == "float32" else 8
        sample_major = _pack_valid_sample_major(payload)
        channel_count = len(record["channels"]["names"])
        vector_width = channel_count * packed_width
        for position, source_index in enumerate(sample_axis["source_sample_indices"]):
            corrected = timestamps["corrected_timestamps_sec"][position]
            element = {
                "kind": "data",
                "reconnect_generation": sequence["reconnect_generation"],
                "correction_segment_index": sequence["correction_segment_index"],
                "source_sample_index": source_index,
                "source_timestamp_f64_le_hex": _float64_bits_hex(
                    timestamps["source_timestamps_sec"][position]
                ),
                "corrected_timestamp_f64_le_hex": (
                    None if corrected is None else _float64_bits_hex(corrected)
                ),
                "raw_counter": (
                    packet["raw_counter_values"][position]
                    if packet["raw_counter_available"]
                    else None
                ),
                "unwrapped_counter": (
                    packet["unwrapped_counter_values"][position]
                    if packet["raw_counter_available"]
                    else None
                ),
                "gap_before_samples": packet["gap_before_samples"] if position == 0 else 0,
                "anomalies": _thaw(record["anomalies"]),
                "channel_vector_le_hex": sample_major[
                    position * vector_width : (position + 1) * vector_width
                ].hex(),
            }
            yield canonical_json_bytes(element)
        return

    element = {
        "kind": kind,
        "reconnect_generation": sequence["reconnect_generation"],
        "correction_segment_index": sequence["correction_segment_index"],
        "first_source_sample_index": sample_axis["first_source_sample_index"],
        "stop_source_sample_index_exclusive": sample_axis[
            "stop_source_sample_index_exclusive"
        ],
        "first_record": sequence["first_record"],
        "final_record": sequence["final_record"],
        "packet_accounting": _thaw(packet),
        "anomalies": _thaw(record["anomalies"]),
        "source_clock_domain": timestamps["source_clock_domain"],
        "corrected_clock_domain": timestamps["corrected_clock_domain"],
        "correction_applied": timestamps["correction_applied"],
        "correction_method": timestamps["correction_method"],
        "correction_ledger_sha256": timestamps["correction_ledger_sha256"],
        "warnings": _thaw(record["warnings"]),
        "unavailable_fields": _thaw(record["unavailable_fields"]),
    }
    yield canonical_json_bytes(element)


def advance_semantic_prefix(
    record: Mapping[str, Any],
    bindings: SourceBindings,
    prior: SemanticPrefixState | None = None,
) -> SemanticPrefixState:
    """Advance a resumable semantic chain over sample or control elements."""

    state = prior or SemanticPrefixState.initial(bindings)
    if state.bindings_sha256 != bindings.sha256:
        _refuse("state_source_or_prefix_collision", "semantic prior belongs to other bindings")
    for element in _semantic_elements(record):
        state = state.advance(element)
    return state


@dataclass(frozen=True, slots=True)
class SourceChunk:
    """Deeply immutable validated SourceChunk envelope."""

    _record: Mapping[str, Any]
    bindings: SourceBindings
    semantic_state: SemanticPrefixState
    canonical_bytes: bytes

    @property
    def record(self) -> Mapping[str, Any]:
        return self._record

    @property
    def record_kind(self) -> str:
        return self._record["record_kind"]

    @property
    def semantic_prefix_sha256(self) -> str:
        return self.semantic_state.digest_sha256

    def __getitem__(self, key: str) -> Any:
        return self._record[key]

    def to_dict(self) -> dict[str, Any]:
        return _thaw(self._record)


def _validate_string_array(value: Any, field: str, expected_length: int | None = None) -> list[str]:
    items = _expect_list(value, field)
    if expected_length is not None and len(items) != expected_length:
        _refuse("channel_contract_changed_midstream", f"{field} length mismatch")
    for index, item in enumerate(items):
        _expect_string(item, f"{field}[{index}]")
    return items


def _validate_schema_and_identity(record: Mapping[str, Any]) -> None:
    schema = _expect_mapping(record["schema"], "schema")
    _expect_exact_keys(schema, SCHEMA_KEYS, "schema")
    if schema["name"] != SCHEMA_NAME or schema["version"] != SCHEMA_VERSION:
        _refuse("source_chunk_schema_invalid", "schema name or version mismatch")
    identity = _expect_mapping(record["identity"], "identity")
    _expect_exact_keys(identity, IDENTITY_KEYS, "identity")
    for key in sorted(IDENTITY_KEYS):
        _expect_string(identity[key], f"identity.{key}")


def _validate_sequence(record: Mapping[str, Any]) -> None:
    sequence = _expect_mapping(record["sequence"], "sequence")
    _expect_exact_keys(sequence, SEQUENCE_KEYS, "sequence")
    for key in ("chunk_sequence_index", "correction_segment_index", "reconnect_generation"):
        _expect_int(sequence[key], f"sequence.{key}")
    _expect_bool(sequence["first_record"], "sequence.first_record")
    _expect_bool(sequence["final_record"], "sequence.final_record")
    kind = record["record_kind"]
    if (kind == "stream_start") != sequence["first_record"]:
        _refuse("reconnect_generation_or_state_invalid", "first_record must identify stream_start only")
    if kind == "stream_start" and (
        sequence["chunk_sequence_index"] != 0
        or sequence["correction_segment_index"] != 0
        or sequence["reconnect_generation"] != 0
    ):
        _refuse("reconnect_generation_or_state_invalid", "stream_start must open generation zero")
    if (kind == "stream_end") != sequence["final_record"]:
        _refuse("reconnect_generation_or_state_invalid", "final_record must identify stream_end only")
    if kind == "reconnect" and sequence["chunk_sequence_index"] != 0:
        _refuse("reconnect_generation_or_state_invalid", "reconnect must start sequence zero")


def _validate_channels(record: Mapping[str, Any]) -> int:
    channels = _expect_mapping(record["channels"], "channels")
    _expect_exact_keys(channels, CHANNEL_KEYS, "channels")
    names = _validate_string_array(channels["names"], "channels.names")
    count = len(names)
    if count == 0 or count > MAX_CHANNELS:
        _refuse("resource_cap_exceeded", "channel count must be in [1, 32]")
    if len(set(names)) != count:
        _refuse("channel_contract_changed_midstream", "channel names must be unique")
    _validate_string_array(channels["types"], "channels.types", count)
    _validate_string_array(channels["units"], "channels.units", count)
    rows = _expect_list(channels["source_row_indices"], "channels.source_row_indices")
    if len(rows) != count:
        _refuse("channel_contract_changed_midstream", "source row count mismatch")
    for index, row in enumerate(rows):
        _expect_int(row, f"channels.source_row_indices[{index}]")
    if len(set(rows)) != count:
        _refuse("channel_contract_changed_midstream", "source rows must be unique")
    mask = _expect_list(channels["geometry_available_mask"], "channels.geometry_available_mask")
    if len(mask) != count or any(type(item) is not bool for item in mask):
        _refuse("channel_contract_changed_midstream", "geometry mask must align to channels")
    geometry_hash = _expect_hash(
        channels["geometry_payload_sha256"],
        "channels.geometry_payload_sha256",
        nullable=True,
    )
    if any(mask) != (geometry_hash is not None):
        _refuse("channel_contract_changed_midstream", "geometry availability and hash disagree")
    return count


def _validate_payload(record: Mapping[str, Any], channel_count: int) -> None:
    payload = _expect_mapping(record["payload"], "payload")
    _expect_exact_keys(payload, PAYLOAD_KEYS, "payload")
    if payload["layout"] != "channels,samples":
        _refuse("payload_shape_or_layout_invalid", "payload layout must be channels,samples")
    dtype = payload["dtype"]
    if not isinstance(dtype, str) or dtype not in PAYLOAD_DTYPES:
        _refuse("payload_dtype_not_allowed", f"unsupported payload dtype {dtype!r}")
    shape = _expect_list(payload["shape"], "payload.shape")
    if len(shape) != 2 or any(not _is_int(item) or item < 0 for item in shape):
        _refuse("payload_shape_or_layout_invalid", "payload shape must contain two nonnegative integers")
    valid = _expect_int(payload["valid_sample_count"], "payload.valid_sample_count")
    capacity = _expect_int(payload["capacity_sample_count"], "payload.capacity_sample_count")
    if capacity > MAX_SAMPLES_PER_CHUNK:
        _refuse("resource_cap_exceeded", "chunk sample capacity exceeds 4096")
    if valid > capacity or shape != [channel_count, capacity]:
        _refuse("payload_shape_or_layout_invalid", "shape, channel count, valid count, or capacity disagree")
    values = _expect_list(payload["values"], "payload.values")
    if len(values) != channel_count:
        _refuse("payload_shape_or_layout_invalid", "payload row count differs from channels")
    padding_mask = _expect_list(payload["padding_mask"], "payload.padding_mask")
    if len(padding_mask) != capacity or any(type(item) is not bool for item in padding_mask):
        _refuse("padding_mask_or_value_invalid", "padding mask must be a boolean per capacity sample")
    if padding_mask != ([True] * valid + [False] * (capacity - valid)):
        _refuse("padding_mask_or_value_invalid", "valid samples must precede padding exactly")
    for channel_index, row_value in enumerate(values):
        row = _expect_list(row_value, f"payload.values[{channel_index}]")
        if len(row) != capacity:
            _refuse("payload_shape_or_layout_invalid", "payload row capacity mismatch")
        for sample_index, value in enumerate(row):
            numeric = _validate_exact_payload_float(
                value, dtype, f"payload.values[{channel_index}][{sample_index}]"
            )
            if sample_index >= valid and not _is_positive_zero(numeric, dtype):
                _refuse(
                    "padding_mask_or_value_invalid",
                    "padding must use exact positive zero in the declared dtype",
                )
    if record["record_kind"] == "data" and valid == 0:
        _refuse("payload_shape_or_layout_invalid", "data records require at least one valid sample")
    if record["record_kind"] != "data" and (valid != 0 or capacity != 0):
        _refuse("payload_shape_or_layout_invalid", "control records cannot carry samples")


def _validate_sample_axis(record: Mapping[str, Any]) -> None:
    axis = _expect_mapping(record["sample_axis"], "sample_axis")
    _expect_exact_keys(axis, SAMPLE_AXIS_KEYS, "sample_axis")
    indices = _expect_list(axis["source_sample_indices"], "sample_axis.source_sample_indices")
    valid = record["payload"]["valid_sample_count"]
    first = _expect_int(axis["first_source_sample_index"], "sample_axis.first_source_sample_index")
    stop = _expect_int(
        axis["stop_source_sample_index_exclusive"],
        "sample_axis.stop_source_sample_index_exclusive",
    )
    for position, index in enumerate(indices):
        _expect_int(index, f"sample_axis.source_sample_indices[{position}]")
    if record["record_kind"] == "data":
        expected = list(range(first, first + valid))
        if indices != expected or stop != first + valid:
            _refuse("sample_index_gap_unrepresented", "source sample indices must be consecutive")
    elif indices:
        _refuse("payload_shape_or_layout_invalid", "control records cannot list source samples")
    elif record["record_kind"] == "gap":
        if stop - first != record["packet_accounting"]["gap_before_samples"]:
            _refuse("sample_index_gap_unrepresented", "gap span must equal gap_before_samples")
    elif stop != first:
        _refuse("sample_index_gap_unrepresented", "non-gap controls must have an empty boundary")
    rate = _expect_float(
        axis["nominal_sampling_rate_hz"],
        "sample_axis.nominal_sampling_rate_hz",
        "source_chunk_schema_invalid",
    )
    period = _expect_float(
        axis["nominal_sample_period_sec"],
        "sample_axis.nominal_sample_period_sec",
        "source_chunk_schema_invalid",
    )
    if rate <= 0.0 or rate > 4096.0 or struct.pack("<d", period) != struct.pack("<d", 1.0 / rate):
        _refuse("source_chunk_schema_invalid", "sampling rate and exact nominal period disagree")


def _strictly_increasing(values: Sequence[float]) -> bool:
    return all(left < right for left, right in zip(values, values[1:]))


def _validate_timestamps(record: Mapping[str, Any]) -> None:
    timestamps = _expect_mapping(record["timestamps"], "timestamps")
    _expect_exact_keys(timestamps, TIMESTAMP_KEYS, "timestamps")
    source_domain = timestamps["source_clock_domain"]
    if not isinstance(source_domain, str) or source_domain not in CLOCK_DOMAINS:
        _refuse("clock_domain_unknown_for_required_correction", "unknown source clock domain")
    source = _expect_list(timestamps["source_timestamps_sec"], "timestamps.source_timestamps_sec")
    valid = record["payload"]["valid_sample_count"]
    if len(source) != valid:
        _refuse("source_timestamp_nonfinite", "source timestamp count must equal valid samples")
    for index, value in enumerate(source):
        _expect_float(value, f"timestamps.source_timestamps_sec[{index}]", "source_timestamp_nonfinite")
    if not _strictly_increasing(source):
        _refuse("sample_order_regression_unrepresented", "source timestamps must be strictly increasing")
    corrected = _expect_list(
        timestamps["corrected_timestamps_sec"], "timestamps.corrected_timestamps_sec"
    )
    if len(corrected) != valid:
        _refuse("clock_correction_ledger_missing_or_tampered", "corrected timestamp count mismatch")
    correction_applied = _expect_bool(timestamps["correction_applied"], "timestamps.correction_applied")
    if correction_applied:
        corrected_domain = timestamps["corrected_clock_domain"]
        if not isinstance(corrected_domain, str) or corrected_domain not in CLOCK_DOMAINS:
            _refuse("clock_domain_unknown_for_required_correction", "unknown corrected clock domain")
        _expect_string(timestamps["correction_method"], "timestamps.correction_method")
        _expect_hash(
            timestamps["correction_ledger_sha256"], "timestamps.correction_ledger_sha256"
        )
        for index, value in enumerate(corrected):
            _expect_float(
                value,
                f"timestamps.corrected_timestamps_sec[{index}]",
                "clock_correction_ledger_missing_or_tampered",
            )
        if not _strictly_increasing(corrected):
            _refuse("clock_reset_unrepresented", "corrected timestamps must be strictly increasing")
    else:
        if (
            timestamps["corrected_clock_domain"] is not None
            or timestamps["correction_method"] is not None
            or timestamps["correction_ledger_sha256"] is not None
            or corrected != [None] * valid
        ):
            _refuse(
                "clock_correction_ledger_missing_or_tampered",
                "unavailable correction view must be explicitly null",
            )
    start = _expect_int(
        timestamps["arrival_monotonic_start_ns"], "timestamps.arrival_monotonic_start_ns"
    )
    end = _expect_int(
        timestamps["arrival_monotonic_end_ns"], "timestamps.arrival_monotonic_end_ns"
    )
    if end < start:
        _refuse("clock_reset_unrepresented", "arrival monotonic interval regressed")
    if timestamps["wall_clock_values_redacted"] is not True:
        _refuse("source_chunk_schema_invalid", "wall-clock values must be redacted")


def _validate_packet_and_anomalies(record: Mapping[str, Any]) -> None:
    packet = _expect_mapping(record["packet_accounting"], "packet_accounting")
    _expect_exact_keys(packet, PACKET_KEYS, "packet_accounting")
    available = _expect_bool(packet["raw_counter_available"], "packet_accounting.raw_counter_available")
    raw = _expect_list(packet["raw_counter_values"], "packet_accounting.raw_counter_values")
    unwrapped = _expect_list(
        packet["unwrapped_counter_values"], "packet_accounting.unwrapped_counter_values"
    )
    valid = record["payload"]["valid_sample_count"]
    if available:
        modulus = _expect_int(packet["counter_modulus"], "packet_accounting.counter_modulus", minimum=2)
        if len(raw) != valid or len(unwrapped) != valid:
            _refuse("packet_loss_measurement_unavailable_for_required_gate", "counter arrays must align")
        for index, value in enumerate(raw):
            _expect_int(value, f"packet_accounting.raw_counter_values[{index}]")
            if value >= modulus:
                _refuse("packet_counter_wrap_unrepresented", "raw counter exceeds modulus")
        for index, value in enumerate(unwrapped):
            _expect_int(value, f"packet_accounting.unwrapped_counter_values[{index}]")
        if not all(left < right for left, right in zip(unwrapped, unwrapped[1:])):
            _refuse("sample_order_regression_unrepresented", "unwrapped counters must increase")
        expected_raw = [value % modulus for value in unwrapped]
        if raw != expected_raw:
            _refuse("packet_counter_wrap_unrepresented", "raw and unwrapped counters disagree")
    elif raw or unwrapped or packet["counter_modulus"] is not None:
        _refuse(
            "packet_loss_measurement_unavailable_for_required_gate",
            "unavailable counters must use empty arrays and null modulus",
        )
    gap = _expect_int(packet["gap_before_samples"], "packet_accounting.gap_before_samples")
    for key in ("duplicate_sample_count", "out_of_order_sample_count", "counter_wrap_count"):
        _expect_int(packet[key], f"packet_accounting.{key}")

    anomalies = _expect_mapping(record["anomalies"], "anomalies")
    _expect_exact_keys(anomalies, ANOMALY_KEYS, "anomalies")
    for key in (
        "timestamp_regression_count",
        "timestamp_duplicate_count",
        "inferred_gap_count",
        "proven_gap_count",
    ):
        _expect_int(anomalies[key], f"anomalies.{key}")
    for key in ("clock_reset_before", "source_restarted_before", "interpolation_performed"):
        _expect_bool(anomalies[key], f"anomalies.{key}")
    if anomalies["interpolation_performed"]:
        _refuse("payload_shape_or_layout_invalid", "interpolation is forbidden")
    if record["record_kind"] == "data":
        if gap or any(packet[key] for key in ("duplicate_sample_count", "out_of_order_sample_count")):
            _refuse("sample_index_gap_unrepresented", "data anomalies require an explicit control record")
        if any(anomalies[key] for key in ANOMALY_KEYS if key != "interpolation_performed"):
            _refuse("clock_reset_unrepresented", "data anomaly facts require an explicit control record")
    elif record["record_kind"] == "gap":
        if gap <= 0 or anomalies["inferred_gap_count"] + anomalies["proven_gap_count"] <= 0:
            _refuse("sample_index_gap_unrepresented", "gap control must declare a positive represented gap")
    elif gap != 0:
        _refuse("sample_index_gap_unrepresented", "only gap controls may declare gap_before_samples")
    if record["record_kind"] == "reconnect" and not (
        anomalies["source_restarted_before"] or anomalies["clock_reset_before"]
    ):
        _refuse("reconnect_generation_or_state_invalid", "reconnect must declare restart or reset")


def _validate_causality_and_provenance(record: Mapping[str, Any]) -> None:
    causality = _expect_mapping(record["causality"], "causality")
    _expect_exact_keys(causality, CAUSALITY_KEYS, "causality")
    for key in ("emits_only_received_samples", "producer_causal", "end_to_end_latency_measured"):
        _expect_bool(causality[key], f"causality.{key}")
    for key in (
        "producer_right_context_samples",
        "required_left_context_samples",
        "required_right_context_samples",
    ):
        _expect_int(causality[key], f"causality.{key}")
    _expect_string(causality["internal_read_ahead_status"], "causality.internal_read_ahead_status")
    if (
        not causality["emits_only_received_samples"]
        or not causality["producer_causal"]
        or causality["producer_right_context_samples"] != 0
        or causality["required_right_context_samples"] != 0
        or causality["end_to_end_latency_measured"]
    ):
        _refuse("source_chunk_schema_invalid", "SourceChunk v0 generated path must remain causal and unmeasured")
    provenance = _expect_mapping(record["provenance"], "provenance")
    _expect_exact_keys(provenance, PROVENANCE_KEYS, "provenance")
    for key in sorted(PROVENANCE_KEYS):
        _expect_hash(provenance[key], f"provenance.{key}")


def _validate_hashes_and_lists(record: Mapping[str, Any]) -> None:
    hashes = _expect_mapping(record["hashes"], "hashes")
    _expect_exact_keys(hashes, HASH_KEYS, "hashes")
    for key in sorted(HASH_KEYS):
        _expect_hash(hashes[key], f"hashes.{key}")
    for field in ("warnings", "unavailable_fields"):
        values = _validate_string_array(record[field], field)
        if len(values) != len(set(values)) or values != sorted(values):
            _refuse("source_chunk_schema_invalid", f"{field} must be unique and sorted")


def validate_source_chunk(
    record: Mapping[str, Any] | SourceChunk,
    *,
    prior: SemanticPrefixState | None = None,
    expected_bindings: SourceBindings | None = None,
) -> SourceChunk:
    """Strictly validate and deeply freeze one existing SourceChunk v0 record."""

    if isinstance(record, SourceChunk):
        if prior is not None or expected_bindings is not None:
            _refuse("source_chunk_schema_invalid", "already validated chunks take no validation context")
        return record
    source = _expect_mapping(record, "SourceChunk")
    _scan_forbidden_keys(source)
    _expect_exact_keys(source, TOP_LEVEL_KEYS, "SourceChunk")
    if not isinstance(source["record_kind"], str) or source["record_kind"] not in RECORD_KINDS:
        _refuse("source_chunk_schema_invalid", "record_kind is not registered")
    _validate_schema_and_identity(source)
    _validate_sequence(source)
    channel_count = _validate_channels(source)
    _validate_payload(source, channel_count)
    _validate_sample_axis(source)
    _validate_timestamps(source)
    _validate_packet_and_anomalies(source)
    _validate_causality_and_provenance(source)
    _validate_hashes_and_lists(source)

    bindings = SourceBindings.from_record(source)
    if expected_bindings is not None and bindings.sha256 != expected_bindings.sha256:
        _refuse("source_identity_mismatch", "record immutable bindings changed")
    if prior is None and source["record_kind"] != "stream_start":
        _refuse("state_source_or_prefix_collision", "non-start record requires a semantic prior")
    if prior is not None and source["record_kind"] == "stream_start":
        _refuse("state_source_or_prefix_collision", "stream_start cannot follow a semantic prior")
    semantic = advance_semantic_prefix(source, bindings, prior)
    if source["hashes"]["valid_payload_sha256"] != compute_valid_payload_sha256(source["payload"]):
        _refuse("semantic_stream_hash_mismatch", "valid payload hash mismatch")
    if source["hashes"]["semantic_prefix_sha256"] != semantic.digest_sha256:
        _refuse("semantic_stream_hash_mismatch", "semantic prefix hash mismatch")
    if source["hashes"]["chunk_envelope_sha256"] != compute_chunk_envelope_sha256(source):
        _refuse("semantic_stream_hash_mismatch", "chunk envelope hash mismatch")
    frozen = _freeze(_thaw(source))
    return SourceChunk(frozen, bindings, semantic, canonical_json_bytes(source))


class GeneratedSourceChunkFactory:
    """Deterministic stateful factory for fictional SourceChunk control/data records."""

    def __init__(self, bindings: SourceBindings) -> None:
        if bindings.record["identity"]["adapter_id"] != "pure_python_synthetic_replay":
            _refuse("source_identity_mismatch", "generated factory requires the synthetic adapter")
        if bindings.record["source_clock_domain"] != "synthetic_relative_monotonic":
            _refuse("clock_domain_unknown_for_required_correction", "generated factory requires synthetic time")
        self._bindings = bindings
        self._prefix = SemanticPrefixState.initial(bindings)
        self._sequence = 0
        self._generation = 0
        self._correction_segment = 0
        self._next_sample = 0
        self._started = False
        self._degraded = False
        self._closed = False

    @classmethod
    def fictional(cls, **kwargs: Any) -> GeneratedSourceChunkFactory:
        return cls(SourceBindings.generated(**kwargs))

    @property
    def semantic_state(self) -> SemanticPrefixState:
        return self._prefix

    @property
    def bindings(self) -> SourceBindings:
        return self._bindings

    def _base_record(
        self,
        *,
        kind: str,
        first: int,
        stop: int,
        values: list[list[float]],
        valid: int,
        capacity: int,
        source_timestamps: list[float],
        corrected_timestamps: list[float],
        raw_counters: list[int],
        unwrapped_counters: list[int],
        gap_before: int = 0,
        anomalies: Mapping[str, Any] | None = None,
        warnings: Iterable[str] = (),
        unavailable_fields: Iterable[str] = (),
        first_record: bool = False,
        final_record: bool = False,
    ) -> SourceChunk:
        binding = self._bindings.record
        rate = binding["nominal_sampling_rate_hz"]
        arrival_start = round((first / rate) * 1_000_000_000)
        arrival_end = round((stop / rate) * 1_000_000_000)
        if arrival_end < arrival_start:
            arrival_end = arrival_start
        default_anomalies = {
            "timestamp_regression_count": 0,
            "timestamp_duplicate_count": 0,
            "clock_reset_before": False,
            "source_restarted_before": False,
            "inferred_gap_count": 0,
            "proven_gap_count": 0,
            "interpolation_performed": False,
        }
        if anomalies is not None:
            default_anomalies.update(anomalies)
        record = {
            "schema": _thaw(binding["schema"]),
            "record_kind": kind,
            "identity": _thaw(binding["identity"]),
            "sequence": {
                "chunk_sequence_index": self._sequence,
                "correction_segment_index": self._correction_segment,
                "reconnect_generation": self._generation,
                "first_record": first_record,
                "final_record": final_record,
            },
            "channels": _thaw(binding["channels"]),
            "payload": {
                "layout": "channels,samples",
                "dtype": binding["payload_dtype"],
                "shape": [len(binding["channels"]["names"]), capacity],
                "values": values,
                "valid_sample_count": valid,
                "capacity_sample_count": capacity,
                "padding_mask": [True] * valid + [False] * (capacity - valid),
            },
            "sample_axis": {
                "source_sample_indices": list(range(first, first + valid)),
                "first_source_sample_index": first,
                "stop_source_sample_index_exclusive": stop,
                "nominal_sampling_rate_hz": binding["nominal_sampling_rate_hz"],
                "nominal_sample_period_sec": binding["nominal_sample_period_sec"],
            },
            "timestamps": {
                "source_clock_domain": binding["source_clock_domain"],
                "source_timestamps_sec": source_timestamps,
                "corrected_clock_domain": binding["corrected_clock_domain"],
                "corrected_timestamps_sec": corrected_timestamps,
                "correction_applied": binding["correction_applied"],
                "correction_method": binding["correction_method"],
                "correction_ledger_sha256": binding["correction_ledger_sha256"],
                "arrival_monotonic_start_ns": arrival_start,
                "arrival_monotonic_end_ns": arrival_end,
                "wall_clock_values_redacted": True,
            },
            "packet_accounting": {
                "raw_counter_available": True,
                "raw_counter_values": raw_counters,
                "unwrapped_counter_values": unwrapped_counters,
                "counter_modulus": 65536,
                "gap_before_samples": gap_before,
                "duplicate_sample_count": 0,
                "out_of_order_sample_count": 0,
                "counter_wrap_count": 0,
            },
            "anomalies": default_anomalies,
            "causality": _thaw(binding["causality"]),
            "provenance": _thaw(binding["provenance"]),
            "hashes": {
                "chunk_envelope_sha256": "0" * 64,
                "valid_payload_sha256": "0" * 64,
                "semantic_prefix_sha256": "0" * 64,
            },
            "warnings": sorted(set(warnings)),
            "unavailable_fields": sorted(set(unavailable_fields)),
        }
        prior = self._prefix
        record["hashes"]["valid_payload_sha256"] = compute_valid_payload_sha256(record["payload"])
        semantic = advance_semantic_prefix(record, self._bindings, prior)
        record["hashes"]["semantic_prefix_sha256"] = semantic.digest_sha256
        record["hashes"]["chunk_envelope_sha256"] = compute_chunk_envelope_sha256(record)
        validated = validate_source_chunk(
            record,
            prior=None if kind == "stream_start" else prior,
            expected_bindings=self._bindings,
        )
        self._prefix = validated.semantic_state
        return validated

    def stream_start(self) -> SourceChunk:
        if self._started or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "stream_start is valid exactly once")
        validated = self._base_record(
            kind="stream_start",
            first=0,
            stop=0,
            values=[[] for _ in self._bindings.record["channels"]["names"]],
            valid=0,
            capacity=0,
            source_timestamps=[],
            corrected_timestamps=[],
            raw_counters=[],
            unwrapped_counters=[],
            first_record=True,
        )
        self._started = True
        self._sequence = 1
        return validated

    def data(self, values: Sequence[Sequence[Any]], *, capacity: int | None = None) -> SourceChunk:
        if not self._started or self._degraded or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "data requires an active generated stream")
        channel_count = len(self._bindings.record["channels"]["names"])
        if isinstance(values, (str, bytes)):
            _refuse("payload_shape_or_layout_invalid", "generated values must be an array")
        try:
            rows = [list(row) for row in values]
        except TypeError:
            _refuse("payload_shape_or_layout_invalid", "generated values must be channels,samples")
        if len(rows) != channel_count or not rows or len({len(row) for row in rows}) != 1:
            _refuse("payload_shape_or_layout_invalid", "generated values must be channels,samples")
        valid = len(rows[0])
        if valid == 0:
            _refuse("payload_shape_or_layout_invalid", "generated data cannot be empty")
        chosen_capacity = valid if capacity is None else capacity
        if not _is_int(chosen_capacity) or chosen_capacity < valid:
            _refuse("payload_shape_or_layout_invalid", "generated capacity is smaller than valid samples")
        if chosen_capacity > MAX_SAMPLES_PER_CHUNK:
            _refuse("resource_cap_exceeded", "generated chunk exceeds 4096 samples")
        dtype = self._bindings.record["payload_dtype"]
        cast_rows: list[list[float]] = []
        for channel_index, row in enumerate(rows):
            cast = [
                _cast_generated_float(value, dtype, f"values[{channel_index}][{sample_index}]")
                for sample_index, value in enumerate(row)
            ]
            cast.extend(0.0 for _ in range(chosen_capacity - valid))
            cast_rows.append(cast)
        first = self._next_sample
        stop = first + valid
        rate = self._bindings.record["nominal_sampling_rate_hz"]
        source_timestamps = [index / rate for index in range(first, stop)]
        corrected_timestamps = list(source_timestamps)
        unwrapped = list(range(first, stop))
        validated = self._base_record(
            kind="data",
            first=first,
            stop=stop,
            values=cast_rows,
            valid=valid,
            capacity=chosen_capacity,
            source_timestamps=source_timestamps,
            corrected_timestamps=corrected_timestamps,
            raw_counters=[value % 65536 for value in unwrapped],
            unwrapped_counters=unwrapped,
        )
        self._next_sample = stop
        self._sequence += 1
        return validated

    def gap(self, missing_samples: int, *, inferred: bool = False) -> SourceChunk:
        if not self._started or self._degraded or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "gap requires an active generated stream")
        _expect_bool(inferred, "inferred")
        missing = _expect_int(missing_samples, "missing_samples", minimum=1)
        first = self._next_sample
        stop = first + missing
        validated = self._base_record(
            kind="gap",
            first=first,
            stop=stop,
            values=[[] for _ in self._bindings.record["channels"]["names"]],
            valid=0,
            capacity=0,
            source_timestamps=[],
            corrected_timestamps=[],
            raw_counters=[],
            unwrapped_counters=[],
            gap_before=missing,
            anomalies={
                "inferred_gap_count": 1 if inferred else 0,
                "proven_gap_count": 0 if inferred else 1,
            },
            warnings=("timestamp_only_gap_inferred",) if inferred else (),
        )
        self._next_sample = stop
        self._sequence += 1
        self._degraded = True
        return validated

    def source_error(self, *, clock_reset: bool = False) -> SourceChunk:
        if not self._started or self._degraded or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "source_error requires an active stream")
        _expect_bool(clock_reset, "clock_reset")
        boundary = self._next_sample
        validated = self._base_record(
            kind="source_error",
            first=boundary,
            stop=boundary,
            values=[[] for _ in self._bindings.record["channels"]["names"]],
            valid=0,
            capacity=0,
            source_timestamps=[],
            corrected_timestamps=[],
            raw_counters=[],
            unwrapped_counters=[],
            anomalies={
                "clock_reset_before": clock_reset,
                "source_restarted_before": True,
            },
            warnings=("generated_source_error",),
        )
        self._sequence += 1
        self._degraded = True
        return validated

    def reconnect(self, *, clock_reset: bool = False) -> SourceChunk:
        if not self._started or not self._degraded or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "reconnect requires degraded state")
        _expect_bool(clock_reset, "clock_reset")
        self._generation += 1
        self._correction_segment += 1
        self._sequence = 0
        boundary = self._next_sample
        validated = self._base_record(
            kind="reconnect",
            first=boundary,
            stop=boundary,
            values=[[] for _ in self._bindings.record["channels"]["names"]],
            valid=0,
            capacity=0,
            source_timestamps=[],
            corrected_timestamps=[],
            raw_counters=[],
            unwrapped_counters=[],
            anomalies={
                "clock_reset_before": clock_reset,
                "source_restarted_before": True,
            },
        )
        self._sequence = 1
        self._degraded = False
        return validated

    def stream_end(self) -> SourceChunk:
        if not self._started or self._degraded or self._closed:
            _refuse("reconnect_generation_or_state_invalid", "stream_end requires an active stream")
        boundary = self._next_sample
        validated = self._base_record(
            kind="stream_end",
            first=boundary,
            stop=boundary,
            values=[[] for _ in self._bindings.record["channels"]["names"]],
            valid=0,
            capacity=0,
            source_timestamps=[],
            corrected_timestamps=[],
            raw_counters=[],
            unwrapped_counters=[],
            final_record=True,
        )
        self._sequence += 1
        self._closed = True
        return validated


__all__ = [
    "GeneratedSourceChunkFactory",
    "SemanticPrefixState",
    "SourceBindings",
    "SourceChunk",
    "SourceChunkRefusal",
    "advance_semantic_prefix",
    "canonical_json_bytes",
    "compute_chunk_envelope_sha256",
    "compute_valid_payload_sha256",
    "validate_source_chunk",
]
