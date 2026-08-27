"""Transactional generated-only live-session state over validated SourceChunk records."""

from __future__ import annotations

import copy
import hashlib
import math
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from typing import Any

from neurodecodekit.streaming.source_chunk import (
    SemanticPrefixState,
    SourceChunk,
    canonical_json_bytes,
    validate_source_chunk,
)


SCHEMA_NAME = "neurodecodekit.live_session_state"
SCHEMA_VERSION = "0.1.0"
FRAME_SAMPLES = 16
WARMUP_SAMPLES = 32
MINIMUM_CONFIDENCE = 0.8
STABLE_UPDATES_REQUIRED = 3
MAX_SESSION_SAMPLES = 65_536
MAX_EVENTS = 4_096
MAX_GAPS = 64
MAX_SOURCE_STATE_BYTES = 4_096
MAX_MUTABLE_STATE_BYTES = 1_048_576
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_NORMALIZED_KEYS = frozenset(
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
        "scorerstate",
        "scoringkey",
        "languagemodel",
        "languagemodelcontext",
        "prompttext",
        "probability",
        "probabilities",
    }
)


class LiveSessionRefusal(RuntimeError):
    """Fail-closed live-session refusal with a stable refusal identifier."""

    def __init__(self, refusal_id: str, detail: str = "") -> None:
        self.refusal_id = refusal_id
        message = refusal_id if not detail else f"{refusal_id}:{detail}"
        super().__init__(message)


@dataclass(frozen=True)
class SessionBindings:
    """Immutable source and producer bindings for one session."""

    source_bindings_sha256: str
    source_identity_sha256: str
    modality_sha256: str
    device_type_sha256: str
    channel_contract_sha256: str
    sampling_rate_sha256: str
    correction_ledger_sha256: str
    clock_mapping_sha256: str
    source_config_sha256: str
    split_protocol_sha256: str
    adapter_config_sha256: str
    processor_config_sha256: str
    model_sha256: str
    decoder_sha256: str
    policy_sha256: str

    def __post_init__(self) -> None:
        for name, value in self.to_dict().items():
            if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
                raise LiveSessionRefusal("snapshot_source_config_model_or_prefix_collision", name)

    def to_dict(self) -> dict[str, str]:
        return {
            "source_bindings_sha256": self.source_bindings_sha256,
            "source_identity_sha256": self.source_identity_sha256,
            "modality_sha256": self.modality_sha256,
            "device_type_sha256": self.device_type_sha256,
            "channel_contract_sha256": self.channel_contract_sha256,
            "sampling_rate_sha256": self.sampling_rate_sha256,
            "correction_ledger_sha256": self.correction_ledger_sha256,
            "clock_mapping_sha256": self.clock_mapping_sha256,
            "source_config_sha256": self.source_config_sha256,
            "split_protocol_sha256": self.split_protocol_sha256,
            "adapter_config_sha256": self.adapter_config_sha256,
            "processor_config_sha256": self.processor_config_sha256,
            "model_sha256": self.model_sha256,
            "decoder_sha256": self.decoder_sha256,
            "policy_sha256": self.policy_sha256,
        }


@dataclass(frozen=True)
class ProcessorFrame:
    """One fixed logical frame, independent of transport chunk partition."""

    reconnect_generation: int
    correction_segment_index: int
    frame_index: int
    source_sample_indices: tuple[int, ...]
    sample_major_values: tuple[tuple[float, ...], ...]
    source_timestamps_sec: tuple[float, ...]
    corrected_timestamps_sec: tuple[float | None, ...]
    source_clock_domain: str
    corrected_clock_domain: str | None
    arrival_monotonic_ns: tuple[int, ...]


@dataclass(frozen=True)
class ProcessorEvent:
    """Strict target-free output from one deterministic causal processor step."""

    candidate_symbol: str
    source_active: bool
    quality_valid: bool
    confidence: float
    preprocessing_complete_ns: int
    model_complete_ns: int
    presentation_ns: int
    mutable_state_bytes: int
    next_state: Mapping[str, Any]


@dataclass(frozen=True)
class FrameUpdate:
    frame_index: int
    provisional_hypothesis: str
    committed_delta: str
    status: str
    abstention_and_anomaly_reasons: tuple[str, ...]
    invalid_output_mask: bool
    warmup_boundary: Mapping[str, Any]
    clocks: Mapping[str, int | None]
    latency: Mapping[str, int | bool | str | None]

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "provisional_hypothesis": self.provisional_hypothesis,
            "committed_delta": self.committed_delta,
            "status": self.status,
            "abstention_and_anomaly_reasons": list(
                self.abstention_and_anomaly_reasons
            ),
            "invalid_output_mask": self.invalid_output_mask,
            "warmup_boundary": dict(self.warmup_boundary),
            "clocks": dict(self.clocks),
            "latency": dict(self.latency),
        }


@dataclass(frozen=True)
class LiveUpdate:
    reconnect_generation: int
    correction_segment_index: int
    accepted_source_sample_interval: tuple[int, int]
    semantic_prefix_sha256: str
    provisional_hypothesis: str
    committed_delta: str
    status: str
    abstention_and_anomaly_reasons: tuple[str, ...]
    invalid_output_mask: bool
    warmup_boundary: Mapping[str, Any]
    clocks: Mapping[str, int | None]
    binding_hashes: Mapping[str, str]
    bounded_counters: Mapping[str, int]
    frame_updates: tuple[FrameUpdate, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "reconnect_generation": self.reconnect_generation,
            "correction_segment_index": self.correction_segment_index,
            "accepted_source_sample_interval": list(
                self.accepted_source_sample_interval
            ),
            "semantic_prefix_sha256": self.semantic_prefix_sha256,
            "provisional_hypothesis": self.provisional_hypothesis,
            "committed_delta": self.committed_delta,
            "status": self.status,
            "abstention_and_anomaly_reasons": list(
                self.abstention_and_anomaly_reasons
            ),
            "invalid_output_mask": self.invalid_output_mask,
            "warmup_boundary": dict(self.warmup_boundary),
            "clocks": dict(self.clocks),
            "binding_hashes": dict(self.binding_hashes),
            "bounded_counters": dict(self.bounded_counters),
            "frame_updates": [value.to_dict() for value in self.frame_updates],
        }


@dataclass(frozen=True)
class _Sample:
    source_index: int
    values: tuple[float, ...]
    source_timestamp_sec: float
    corrected_timestamp_sec: float | None
    arrival_monotonic_ns: int


@dataclass(frozen=True)
class _SessionState:
    status: str = "created"
    reconnect_generation: int = -1
    correction_segment_index: int = -1
    expected_sequence_index: int = 0
    next_source_sample: int | None = None
    semantic_prefix_sha256: str | None = None
    semantic_element_count: int = 0
    last_arrival_monotonic_end_ns: int | None = None
    last_source_timestamp_sec: float | None = None
    last_corrected_timestamp_sec: float | None = None
    nominal_sampling_rate_hz: float | None = None
    source_clock_domain: str | None = None
    corrected_clock_domain: str | None = None
    last_chunk_envelope_sha256: str | None = None
    last_chunk_sequence_index: int | None = None
    frame_buffer: tuple[_Sample, ...] = ()
    next_frame_index: int = 0
    generation_valid_samples: int = 0
    session_valid_samples: int = 0
    event_count: int = 0
    gap_count: int = 0
    processor_state: Mapping[str, Any] = None  # type: ignore[assignment]
    provisional_hypothesis: str = ""
    committed_output: str = ""
    stable_symbol: str = ""
    stable_count: int = 0
    rearmed: bool = True
    first_eligible_output_ns: int | None = None

    def __post_init__(self) -> None:
        if self.processor_state is None:
            object.__setattr__(self, "processor_state", {})


Processor = Callable[[ProcessorFrame, Mapping[str, Any]], ProcessorEvent]


def _hash(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _decoder_sha256() -> str:
    return _hash({"decoder": "stable_symbol_commit", "version": SCHEMA_VERSION})


def _processor_binding(processor: Processor, field: str) -> str:
    value = getattr(processor, field, None)
    if not isinstance(value, str) or HASH_RE.fullmatch(value) is None:
        raise LiveSessionRefusal(
            "snapshot_source_config_model_or_prefix_collision", field
        )
    return value


def _clock_mapping_payload(chunk: SourceChunk) -> dict[str, Any]:
    binding = chunk.bindings.record
    return {
        "source_clock_domain": binding["source_clock_domain"],
        "corrected_clock_domain": binding["corrected_clock_domain"],
        "correction_applied": binding["correction_applied"],
        "correction_method": binding["correction_method"],
        "correction_ledger_sha256": binding["correction_ledger_sha256"],
    }


def _source_state_bytes(chunk: SourceChunk) -> int:
    payload = {
        "bindings": chunk.bindings.to_dict(),
        "semantic_state": {
            "bindings_sha256": chunk.semantic_state.bindings_sha256,
            "digest_sha256": chunk.semantic_state.digest_sha256,
            "element_count": chunk.semantic_state.element_count,
        },
    }
    size = len(canonical_json_bytes(payload))
    if size > MAX_SOURCE_STATE_BYTES:
        raise LiveSessionRefusal("processor_state_cap_breach", "source state cap")
    return size


def _processor_object_state(processor: Processor) -> dict[str, Any]:
    value = getattr(processor, "__dict__", {})
    if not isinstance(value, Mapping):
        raise LiveSessionRefusal("processor_state_cap_breach", "processor object")
    try:
        result = copy.deepcopy(dict(value))
        _state_bytes(result)
    except (TypeError, ValueError, copy.Error) as exc:
        raise LiveSessionRefusal(
            "processor_state_cap_breach", "processor object"
        ) from exc
    return result


def _restore_processor_object_state(
    processor: Processor, state: Mapping[str, Any]
) -> None:
    value = getattr(processor, "__dict__", None)
    if isinstance(value, dict):
        value.clear()
        value.update(copy.deepcopy(dict(state)))


def assert_target_free(value: Any) -> None:
    """Recursively reject target, scoring, and language-context capability keys."""

    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
            if (
                normalized in FORBIDDEN_NORMALIZED_KEYS
                or normalized.endswith(("target", "targets", "label", "labels"))
                or normalized.endswith(("intendedtext", "referencetext", "targettext"))
                or normalized.endswith(("probability", "probabilities"))
            ):
                raise LiveSessionRefusal("target_label_or_text_leakage", str(key))
            assert_target_free(nested)
    elif isinstance(value, (list, tuple)):
        for nested in value:
            assert_target_free(nested)


def _strict_int(value: Any, *, refusal_id: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise LiveSessionRefusal(refusal_id)
    return value


def _snapshot_float(value: Any, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LiveSessionRefusal("snapshot_tamper")
    result = float(value)
    if not math.isfinite(result):
        raise LiveSessionRefusal("snapshot_tamper")
    return result


def _snapshot_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    return _strict_int(value, refusal_id="snapshot_tamper")


def _snapshot_optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise LiveSessionRefusal("snapshot_tamper")
    return value


def _state_bytes(value: Mapping[str, Any]) -> int:
    assert_target_free(value)
    try:
        payload = canonical_json_bytes(value)
    except (TypeError, ValueError) as exc:
        raise LiveSessionRefusal("processor_state_cap_breach", "not canonical") from exc
    if len(payload) > MAX_MUTABLE_STATE_BYTES:
        raise LiveSessionRefusal("processor_state_cap_breach")
    return len(payload)


def _identity_hash(chunk: SourceChunk) -> str:
    return _hash(chunk["identity"])


def _channel_hash(chunk: SourceChunk) -> str:
    return _hash(chunk["channels"])


def _valid_sample_count(chunk: SourceChunk) -> int:
    return int(chunk["payload"]["valid_sample_count"])


def _sample_major_values(chunk: SourceChunk) -> tuple[tuple[float, ...], ...]:
    payload = chunk["payload"]
    count = int(payload["valid_sample_count"])
    channel_rows = payload["values"]
    return tuple(
        tuple(float(channel_rows[channel][sample]) for channel in range(len(channel_rows)))
        for sample in range(count)
    )


def _logical_arrivals(chunk: SourceChunk) -> tuple[int, ...]:
    """Return partition-independent generated host-arrival boundaries."""

    count = _valid_sample_count(chunk)
    if count == 0:
        return ()
    timestamps = chunk["timestamps"]
    start = _strict_int(
        timestamps["arrival_monotonic_start_ns"],
        refusal_id="capture_arrival_clock_order_violation",
    )
    stop = _strict_int(
        timestamps["arrival_monotonic_end_ns"],
        refusal_id="capture_arrival_clock_order_violation",
    )
    if stop < start:
        raise LiveSessionRefusal("capture_arrival_clock_order_violation")
    axis = chunk["sample_axis"]
    rate = float(axis["nominal_sampling_rate_hz"])
    return tuple(
        round(((int(index) + 1) / rate) * 1_000_000_000)
        for index in axis["source_sample_indices"]
    )


def _reset_generation_state(state: _SessionState) -> _SessionState:
    return replace(
        state,
        frame_buffer=(),
        next_frame_index=0,
        generation_valid_samples=0,
        processor_state={},
        provisional_hypothesis="",
        stable_symbol="",
        stable_count=0,
        rearmed=True,
        first_eligible_output_ns=None,
        last_source_timestamp_sec=None,
        last_corrected_timestamp_sec=None,
    )


class LiveSession:
    """One fail-closed source-clocked session with persistent causal state."""

    def __init__(
        self,
        *,
        bindings: SessionBindings,
        processor: Processor,
        minimum_confidence: float = MINIMUM_CONFIDENCE,
        stable_updates_required: int = STABLE_UPDATES_REQUIRED,
    ) -> None:
        if not callable(processor):
            raise TypeError("processor must be callable")
        if not math.isfinite(minimum_confidence) or not 0 <= minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be finite and in [0, 1]")
        if stable_updates_required < 1:
            raise ValueError("stable_updates_required must be positive")
        if (
            _processor_binding(processor, "processor_config_sha256")
            != bindings.processor_config_sha256
            or _processor_binding(processor, "model_sha256") != bindings.model_sha256
            or bindings.decoder_sha256 != _decoder_sha256()
        ):
            raise LiveSessionRefusal(
                "snapshot_source_config_model_or_prefix_collision", "processor"
            )
        policy_sha256 = _hash(
            {
                "frame_samples": FRAME_SAMPLES,
                "warmup_valid_samples": WARMUP_SAMPLES,
                "minimum_confidence": float(minimum_confidence),
                "stable_updates_required": int(stable_updates_required),
            }
        )
        if policy_sha256 != bindings.policy_sha256:
            raise LiveSessionRefusal(
                "snapshot_source_config_model_or_prefix_collision", "policy"
            )
        self._bindings = bindings
        self._processor = processor
        self._minimum_confidence = float(minimum_confidence)
        self._stable_updates_required = int(stable_updates_required)
        self._state = _SessionState()
        self._push_in_progress = False

    @property
    def status(self) -> str:
        return self._state.status

    def push(self, source_chunk: SourceChunk) -> LiveUpdate:
        """Validate and apply one SourceChunk atomically."""

        if self._push_in_progress:
            raise LiveSessionRefusal("processor_state_cap_breach", "reentrant push")
        before = self.snapshot_bytes()
        processor_before = _processor_object_state(self._processor)
        if self._state.status == "closed":
            raise LiveSessionRefusal("use_after_close")
        self._push_in_progress = True
        try:
            if not isinstance(source_chunk, SourceChunk):
                raise LiveSessionRefusal("source_identity_mismatch", "validated SourceChunk required")
            self._preflight_bindings(source_chunk)
            self._preflight_order(source_chunk)
            _source_state_bytes(source_chunk)
            prior = (
                None
                if self._state.semantic_prefix_sha256 is None
                else SemanticPrefixState(
                    bindings_sha256=self._bindings.source_bindings_sha256,
                    digest_sha256=self._state.semantic_prefix_sha256,
                    element_count=self._state.semantic_element_count,
                )
            )
            chunk = validate_source_chunk(
                source_chunk.to_dict(),
                prior=prior,
                expected_bindings=source_chunk.bindings,
            )
            candidate, update = self._apply_chunk(self._state, chunk)
            if canonical_json_bytes(_processor_object_state(self._processor)) != canonical_json_bytes(
                processor_before
            ):
                raise LiveSessionRefusal(
                    "processor_state_cap_breach", "processor object mutated"
                )
            assert_target_free(update.to_dict())
            if len(canonical_json_bytes(update.to_dict())) > MAX_MUTABLE_STATE_BYTES:
                raise LiveSessionRefusal("processor_state_cap_breach", "update bytes")
            self._state = candidate
            return update
        except BaseException:
            _restore_processor_object_state(self._processor, processor_before)
            if self.snapshot_bytes() != before:
                raise AssertionError("LiveSession refusal mutated committed state")
            raise
        finally:
            self._push_in_progress = False

    def _preflight_bindings(self, chunk: SourceChunk) -> None:
        identity = chunk["identity"]
        if _hash(identity["modality"]) != self._bindings.modality_sha256:
            raise LiveSessionRefusal("modality_or_device_drift", "modality")
        if _hash(identity["device_type"]) != self._bindings.device_type_sha256:
            raise LiveSessionRefusal("modality_or_device_drift", "device_type")
        if _identity_hash(chunk) != self._bindings.source_identity_sha256:
            raise LiveSessionRefusal("source_identity_mismatch")
        if _channel_hash(chunk) != self._bindings.channel_contract_sha256:
            raise LiveSessionRefusal("channel_contract_drift")
        if _hash(chunk["sample_axis"]["nominal_sampling_rate_hz"]) != self._bindings.sampling_rate_sha256:
            raise LiveSessionRefusal("sampling_rate_drift")
        if _hash(chunk["timestamps"]["correction_ledger_sha256"]) != self._bindings.correction_ledger_sha256:
            raise LiveSessionRefusal("correction_ledger_tamper")
        if _hash(_clock_mapping_payload(chunk)) != self._bindings.clock_mapping_sha256:
            raise LiveSessionRefusal("correction_ledger_tamper", "clock mapping")
        provenance = chunk["provenance"]
        for key, expected in (
            ("source_config_sha256", self._bindings.source_config_sha256),
            ("split_protocol_sha256", self._bindings.split_protocol_sha256),
            ("adapter_config_sha256", self._bindings.adapter_config_sha256),
        ):
            if provenance[key] != expected:
                raise LiveSessionRefusal(
                    "snapshot_source_config_model_or_prefix_collision", key
                )
        if chunk.bindings.sha256 != self._bindings.source_bindings_sha256:
            raise LiveSessionRefusal(
                "snapshot_source_config_model_or_prefix_collision", "source bindings"
            )

    def _preflight_order(self, chunk: SourceChunk) -> None:
        state = self._state
        sequence = chunk["sequence"]
        generation = sequence["reconnect_generation"]
        sequence_index = sequence["chunk_sequence_index"]
        envelope_hash = chunk["hashes"]["chunk_envelope_sha256"]
        if (
            state.last_chunk_sequence_index is not None
            and generation == state.reconnect_generation
            and sequence_index == state.last_chunk_sequence_index
        ):
            refusal = (
                "identical_duplicate_record"
                if envelope_hash == state.last_chunk_envelope_sha256
                else "conflicting_duplicate_payload"
            )
            raise LiveSessionRefusal(refusal)
        if state.status == "created":
            return
        if state.status == "degraded":
            if chunk.record_kind != "reconnect":
                raise LiveSessionRefusal("chunk_after_disconnect")
            expected_generation = state.reconnect_generation + 1
            if generation < expected_generation:
                raise LiveSessionRefusal("generation_rollback")
            if generation > expected_generation:
                raise LiveSessionRefusal("generation_skip")
            if sequence_index != 0:
                raise LiveSessionRefusal("reconnect_without_generation_increment")
            return
        if chunk.record_kind == "reconnect":
            raise LiveSessionRefusal("reconnect_while_not_degraded")
        if generation < state.reconnect_generation:
            raise LiveSessionRefusal("old_generation_after_reconnect")
        if generation > state.reconnect_generation:
            raise LiveSessionRefusal("generation_skip")
        if sequence_index < state.expected_sequence_index:
            raise LiveSessionRefusal("reordered_sequence")
        if sequence_index > state.expected_sequence_index:
            raise LiveSessionRefusal("hidden_sample_gap")
        first = chunk["sample_axis"]["first_source_sample_index"]
        if state.next_source_sample is not None and first < state.next_source_sample:
            raise LiveSessionRefusal("partial_source_sample_overlap")
        if state.next_source_sample is not None and first > state.next_source_sample:
            raise LiveSessionRefusal("hidden_sample_gap")

    def _apply_chunk(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, LiveUpdate]:
        assert_target_free(chunk.record)
        if chunk.bindings.sha256 != self._bindings.source_bindings_sha256:
            raise LiveSessionRefusal("source_identity_mismatch", "source bindings")
        if _identity_hash(chunk) != self._bindings.source_identity_sha256:
            raise LiveSessionRefusal("source_identity_mismatch")
        if _channel_hash(chunk) != self._bindings.channel_contract_sha256:
            raise LiveSessionRefusal("channel_contract_drift")
        provenance = chunk["provenance"]
        expected_provenance = {
            "source_config_sha256": self._bindings.source_config_sha256,
            "split_protocol_sha256": self._bindings.split_protocol_sha256,
            "adapter_config_sha256": self._bindings.adapter_config_sha256,
        }
        for key, expected in expected_provenance.items():
            if provenance[key] != expected:
                raise LiveSessionRefusal(
                    "snapshot_source_config_model_or_prefix_collision", key
                )

        sequence = chunk["sequence"]
        generation = sequence["reconnect_generation"]
        sequence_index = sequence["chunk_sequence_index"]
        correction_segment = sequence["correction_segment_index"]
        record_kind = chunk.record_kind
        envelope_hash = chunk["hashes"]["chunk_envelope_sha256"]

        if state.last_chunk_sequence_index is not None:
            if (
                generation == state.reconnect_generation
                and sequence_index == state.last_chunk_sequence_index
            ):
                refusal = (
                    "identical_duplicate_record"
                    if envelope_hash == state.last_chunk_envelope_sha256
                    else "conflicting_duplicate_payload"
                )
                raise LiveSessionRefusal(refusal)

        if record_kind == "stream_start":
            candidate, frames, reasons = self._start(state, chunk)
        elif record_kind == "data":
            candidate, frames, reasons = self._data(state, chunk)
        elif record_kind in {"gap", "source_error"}:
            candidate, frames, reasons = self._degrade(state, chunk)
        elif record_kind == "reconnect":
            candidate, frames, reasons = self._reconnect(state, chunk)
        elif record_kind == "stream_end":
            candidate, frames, reasons = self._end(state, chunk)
        else:
            raise LiveSessionRefusal("source_identity_mismatch", "record kind")

        candidate = replace(
            candidate,
            semantic_prefix_sha256=chunk.semantic_prefix_sha256,
            semantic_element_count=chunk.semantic_state.element_count,
            last_arrival_monotonic_end_ns=chunk["timestamps"][
                "arrival_monotonic_end_ns"
            ],
            last_chunk_envelope_sha256=envelope_hash,
            last_chunk_sequence_index=sequence_index,
        )
        if candidate.reconnect_generation != generation:
            raise LiveSessionRefusal("generation_rollback")
        if candidate.correction_segment_index != correction_segment:
            raise LiveSessionRefusal("correction_ledger_tamper")
        _state_bytes(self._state_payload(candidate))
        return candidate, self._update(candidate, chunk, frames, reasons)

    def _start(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...], tuple[str, ...]]:
        sequence = chunk["sequence"]
        if state.status != "created":
            raise LiveSessionRefusal("reordered_sequence")
        if (
            sequence["reconnect_generation"] != 0
            or sequence["chunk_sequence_index"] != 0
            or sequence["correction_segment_index"] != 0
            or sequence["first_record"] is not True
            or _valid_sample_count(chunk) != 0
        ):
            raise LiveSessionRefusal("generation_skip")
        sample_axis = chunk["sample_axis"]
        candidate = replace(
            state,
            status="active",
            reconnect_generation=0,
            correction_segment_index=0,
            expected_sequence_index=1,
            next_source_sample=sample_axis["stop_source_sample_index_exclusive"],
            nominal_sampling_rate_hz=sample_axis["nominal_sampling_rate_hz"],
            source_clock_domain=chunk["timestamps"]["source_clock_domain"],
            corrected_clock_domain=chunk["timestamps"][
                "corrected_clock_domain"
            ],
        )
        return candidate, (), ("stream_started",)

    def _require_active_continuity(
        self, state: _SessionState, chunk: SourceChunk
    ) -> None:
        sequence = chunk["sequence"]
        if state.status == "degraded":
            raise LiveSessionRefusal("chunk_after_disconnect")
        if state.status != "active":
            raise LiveSessionRefusal("reordered_sequence")
        if sequence["reconnect_generation"] < state.reconnect_generation:
            raise LiveSessionRefusal("old_generation_after_reconnect")
        if sequence["reconnect_generation"] > state.reconnect_generation:
            raise LiveSessionRefusal("generation_skip")
        if sequence["chunk_sequence_index"] < state.expected_sequence_index:
            raise LiveSessionRefusal("reordered_sequence")
        if sequence["chunk_sequence_index"] > state.expected_sequence_index:
            raise LiveSessionRefusal("hidden_sample_gap")
        if sequence["correction_segment_index"] != state.correction_segment_index:
            raise LiveSessionRefusal("correction_ledger_tamper")
        sample_axis = chunk["sample_axis"]
        if sample_axis["nominal_sampling_rate_hz"] != state.nominal_sampling_rate_hz:
            raise LiveSessionRefusal("sampling_rate_drift")
        timestamps = chunk["timestamps"]
        if (
            timestamps["source_clock_domain"] != state.source_clock_domain
            or timestamps["corrected_clock_domain"] != state.corrected_clock_domain
        ):
            raise LiveSessionRefusal("clock_reset_unrepresented")
        first = sample_axis["first_source_sample_index"]
        if state.next_source_sample is not None and first < state.next_source_sample:
            raise LiveSessionRefusal("partial_source_sample_overlap")
        if state.next_source_sample is not None and first > state.next_source_sample:
            raise LiveSessionRefusal("hidden_sample_gap")
        arrival_start = chunk["timestamps"]["arrival_monotonic_start_ns"]
        if (
            state.last_arrival_monotonic_end_ns is not None
            and arrival_start < state.last_arrival_monotonic_end_ns
        ):
            raise LiveSessionRefusal("arrival_monotonic_rollback")

    def _data(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...], tuple[str, ...]]:
        self._require_active_continuity(state, chunk)
        valid_sample_count = _valid_sample_count(chunk)
        if valid_sample_count < 1:
            raise LiveSessionRefusal("nonfinite_padding_or_hash_invalid_payload")
        if state.session_valid_samples + valid_sample_count > MAX_SESSION_SAMPLES:
            raise LiveSessionRefusal("session_sample_cap_breach")
        sample_axis = chunk["sample_axis"]
        timestamps = chunk["timestamps"]
        source_times = tuple(timestamps["source_timestamps_sec"])
        corrected_values = timestamps["corrected_timestamps_sec"]
        corrected_times = tuple(
            None if value is None else float(value) for value in corrected_values
        )
        if state.last_source_timestamp_sec is not None and source_times[0] <= state.last_source_timestamp_sec:
            raise LiveSessionRefusal("clock_reset_unrepresented")
        if any(right <= left for left, right in zip(source_times, source_times[1:])):
            raise LiveSessionRefusal("clock_reset_unrepresented")
        period = float(sample_axis["nominal_sample_period_sec"])
        source_steps = [right - left for left, right in zip(source_times, source_times[1:])]
        if state.last_source_timestamp_sec is not None:
            source_steps.insert(0, source_times[0] - state.last_source_timestamp_sec)
        if any(step > period * 1.5 for step in source_steps):
            raise LiveSessionRefusal("timestamp_only_inferred_gap_unrepresented")
        finite_corrected = [value for value in corrected_times if value is not None]
        if finite_corrected and (
            len(finite_corrected) != len(corrected_times)
            or any(right <= left for left, right in zip(finite_corrected, finite_corrected[1:]))
        ):
            raise LiveSessionRefusal("clock_reset_unrepresented")
        if (
            state.last_corrected_timestamp_sec is not None
            and finite_corrected
            and finite_corrected[0] <= state.last_corrected_timestamp_sec
        ):
            raise LiveSessionRefusal("clock_reset_unrepresented")
        arrivals = _logical_arrivals(chunk)
        indices = tuple(sample_axis["source_sample_indices"])
        sample_major = _sample_major_values(chunk)
        added = tuple(
            _Sample(
                source_index=indices[index],
                values=sample_major[index],
                source_timestamp_sec=source_times[index],
                corrected_timestamp_sec=corrected_times[index],
                arrival_monotonic_ns=arrivals[index],
            )
            for index in range(valid_sample_count)
        )
        candidate = replace(
            state,
            expected_sequence_index=state.expected_sequence_index + 1,
            next_source_sample=sample_axis["stop_source_sample_index_exclusive"],
            frame_buffer=state.frame_buffer + added,
            generation_valid_samples=state.generation_valid_samples
            + valid_sample_count,
            session_valid_samples=state.session_valid_samples + valid_sample_count,
            last_source_timestamp_sec=source_times[-1],
            last_corrected_timestamp_sec=(finite_corrected[-1] if finite_corrected else None),
        )
        candidate, frame_updates = self._drain_frames(candidate, chunk)
        return candidate, frame_updates, ()

    def _drain_frames(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...]]:
        updates: list[FrameUpdate] = []
        candidate = state
        while len(candidate.frame_buffer) >= FRAME_SAMPLES:
            if candidate.event_count >= MAX_EVENTS:
                raise LiveSessionRefusal("processor_state_cap_breach", "event cap")
            values = candidate.frame_buffer[:FRAME_SAMPLES]
            frame = ProcessorFrame(
                reconnect_generation=candidate.reconnect_generation,
                correction_segment_index=candidate.correction_segment_index,
                frame_index=candidate.next_frame_index,
                source_sample_indices=tuple(value.source_index for value in values),
                sample_major_values=tuple(value.values for value in values),
                source_timestamps_sec=tuple(
                    value.source_timestamp_sec for value in values
                ),
                corrected_timestamps_sec=tuple(
                    value.corrected_timestamp_sec for value in values
                ),
                source_clock_domain=chunk["timestamps"]["source_clock_domain"],
                corrected_clock_domain=chunk["timestamps"][
                    "corrected_clock_domain"
                ],
                arrival_monotonic_ns=tuple(
                    value.arrival_monotonic_ns for value in values
                ),
            )
            prior_processor_state = copy.deepcopy(dict(candidate.processor_state))
            try:
                event = self._processor(frame, prior_processor_state)
            except LiveSessionRefusal:
                raise
            except BaseException as exc:
                raise LiveSessionRefusal("processor_state_cap_breach", "processor") from exc
            candidate, update = self._apply_processor_event(candidate, frame, event)
            updates.append(update)
            candidate = replace(
                candidate,
                frame_buffer=candidate.frame_buffer[FRAME_SAMPLES:],
                next_frame_index=candidate.next_frame_index + 1,
                event_count=candidate.event_count + 1,
            )
        return candidate, tuple(updates)

    def _apply_processor_event(
        self, state: _SessionState, frame: ProcessorFrame, event: ProcessorEvent
    ) -> tuple[_SessionState, FrameUpdate]:
        if not isinstance(event, ProcessorEvent):
            raise LiveSessionRefusal("processor_state_cap_breach", "event type")
        assert_target_free(
            {
                "candidate_symbol": event.candidate_symbol,
                "next_state": event.next_state,
            }
        )
        if not isinstance(event.candidate_symbol, str) or len(event.candidate_symbol) > 8:
            raise LiveSessionRefusal("processor_state_cap_breach", "symbol")
        if not isinstance(event.source_active, bool) or not isinstance(event.quality_valid, bool):
            raise LiveSessionRefusal("processor_state_cap_breach", "gate type")
        if not isinstance(event.confidence, (int, float)) or isinstance(event.confidence, bool):
            raise LiveSessionRefusal("processor_state_cap_breach", "confidence")
        confidence = float(event.confidence)
        if not math.isfinite(confidence) or not 0 <= confidence <= 1:
            raise LiveSessionRefusal("processor_state_cap_breach", "confidence")
        if not isinstance(event.next_state, Mapping):
            raise LiveSessionRefusal("processor_state_cap_breach", "state type")
        next_state = copy.deepcopy(dict(event.next_state))
        observed_state_bytes = _state_bytes(next_state)
        declared_state_bytes = _strict_int(
            event.mutable_state_bytes, refusal_id="processor_state_cap_breach"
        )
        if declared_state_bytes < 0 or declared_state_bytes != observed_state_bytes:
            raise LiveSessionRefusal("processor_state_cap_breach", "declared bytes")
        for value in (
            event.preprocessing_complete_ns,
            event.model_complete_ns,
            event.presentation_ns,
        ):
            _strict_int(value, refusal_id="capture_arrival_clock_order_violation")
        arrival_ns = frame.arrival_monotonic_ns[-1]
        if not (
            arrival_ns
            <= event.preprocessing_complete_ns
            <= event.model_complete_ns
            <= event.presentation_ns
        ):
            raise LiveSessionRefusal("capture_arrival_clock_order_violation")

        first_output_eligible_frame = WARMUP_SAMPLES // FRAME_SAMPLES
        output_eligible_by_warmup = frame.frame_index >= first_output_eligible_frame
        warmup_complete_after_frame = (
            (frame.frame_index + 1) * FRAME_SAMPLES >= WARMUP_SAMPLES
        )
        reasons: list[str] = []
        eligible = True
        if not output_eligible_by_warmup:
            reasons.append("warmup")
            eligible = False
        if not event.source_active:
            reasons.append("source_inactive")
            eligible = False
        if not event.quality_valid:
            reasons.append("quality_invalid")
            eligible = False
        if confidence < self._minimum_confidence:
            reasons.append("confidence_below_threshold")
            eligible = False
        if not event.candidate_symbol:
            reasons.append("blank")
            eligible = False

        first_eligible_this_frame = eligible and state.first_eligible_output_ns is None
        first_eligible_output_ns = state.first_eligible_output_ns
        if first_eligible_this_frame:
            first_eligible_output_ns = event.model_complete_ns
        candidate = replace(
            state,
            processor_state=next_state,
            first_eligible_output_ns=first_eligible_output_ns,
        )
        committed_delta = ""
        if not eligible:
            rearmed = candidate.rearmed or not event.source_active or not event.candidate_symbol
            candidate = replace(
                candidate,
                provisional_hypothesis="",
                stable_symbol="",
                stable_count=0,
                rearmed=rearmed,
            )
        else:
            symbol = event.candidate_symbol
            stable_count = candidate.stable_count + 1 if candidate.stable_symbol == symbol else 1
            candidate = replace(
                candidate,
                provisional_hypothesis=symbol,
                stable_symbol=symbol,
                stable_count=stable_count,
            )
            if not candidate.rearmed:
                reasons.append("commit_not_rearmed")
            elif stable_count >= self._stable_updates_required:
                committed_delta = symbol
                candidate = replace(
                    candidate,
                    committed_output=candidate.committed_output + symbol,
                    stable_symbol="",
                    stable_count=0,
                    rearmed=False,
                )

        clocks, latency = self._clock_payload(
            frame,
            event,
            bool(committed_delta),
            first_eligible_output_ns,
            first_eligible_this_frame,
        )
        update = FrameUpdate(
            frame_index=frame.frame_index,
            provisional_hypothesis=candidate.provisional_hypothesis,
            committed_delta=committed_delta,
            status="committed" if committed_delta else ("eligible" if eligible else "abstained"),
            abstention_and_anomaly_reasons=tuple(reasons),
            invalid_output_mask=not eligible,
            warmup_boundary={
                "frame_samples": FRAME_SAMPLES,
                "warmup_valid_samples": WARMUP_SAMPLES,
                "frame_index_origin": 0,
                "frame_index": frame.frame_index,
                "complete_after_frame": warmup_complete_after_frame,
                "first_output_eligible_frame_index": first_output_eligible_frame,
                "output_eligible_by_warmup": output_eligible_by_warmup,
            },
            clocks=clocks,
            latency=latency,
        )
        return candidate, update

    def _clock_payload(
        self,
        frame: ProcessorFrame,
        event: ProcessorEvent,
        committed: bool,
        first_eligible_output_ns: int | None,
        first_eligible_this_frame: bool,
    ) -> tuple[dict[str, int | None], dict[str, int | bool | str | None]]:
        capture_start_ns: int | None = None
        capture_end_ns: int | None = None
        comparable = (
            frame.source_clock_domain == "synthetic_relative_monotonic"
            and frame.corrected_clock_domain == frame.source_clock_domain
            and all(value is not None for value in frame.corrected_timestamps_sec)
        )
        if comparable:
            corrected = [float(value) for value in frame.corrected_timestamps_sec]
            capture_start_ns = round(corrected[0] * 1_000_000_000)
            capture_end_ns = round(corrected[-1] * 1_000_000_000)
            if capture_end_ns > frame.arrival_monotonic_ns[-1]:
                raise LiveSessionRefusal("capture_arrival_clock_order_violation")
        stable_commit = event.model_complete_ns if committed else None
        clocks = {
            "capture_start_ns": capture_start_ns,
            "capture_end_ns": capture_end_ns,
            "host_arrival_ns": frame.arrival_monotonic_ns[-1],
            "preprocessing_complete_ns": event.preprocessing_complete_ns,
            "model_complete_ns": event.model_complete_ns,
            "first_eligible_output_ns": first_eligible_output_ns,
            "stable_commit_ns": stable_commit,
            "presentation_ns": event.presentation_ns,
        }
        latency: dict[str, int | bool | str | None] = {
            "cross_domain_available": comparable,
            "unavailable_reason": None if comparable else "clock_domains_not_verified_comparable",
            "transport_ns": None,
            "preprocessing_ns": event.preprocessing_complete_ns
            - frame.arrival_monotonic_ns[-1],
            "model_ns": event.model_complete_ns - event.preprocessing_complete_ns,
            "capture_to_first_eligible_output_ns": None,
            "capture_to_stable_commit_ns": None,
            "capture_to_presentation_ns": None,
            "presentation_delay_ns": event.presentation_ns - event.model_complete_ns,
        }
        if comparable and capture_end_ns is not None:
            latency["transport_ns"] = frame.arrival_monotonic_ns[-1] - capture_end_ns
            if first_eligible_this_frame and first_eligible_output_ns is not None:
                latency["capture_to_first_eligible_output_ns"] = (
                    first_eligible_output_ns - capture_end_ns
                )
            latency["capture_to_stable_commit_ns"] = (
                None if stable_commit is None else stable_commit - capture_end_ns
            )
            latency["capture_to_presentation_ns"] = event.presentation_ns - capture_end_ns
        return clocks, latency

    def _degrade(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...], tuple[str, ...]]:
        self._require_active_continuity(state, chunk)
        if state.gap_count >= MAX_GAPS:
            raise LiveSessionRefusal("processor_state_cap_breach", "gap cap")
        sample_axis = chunk["sample_axis"]
        candidate = replace(
            state,
            status="degraded",
            expected_sequence_index=state.expected_sequence_index + 1,
            next_source_sample=sample_axis["stop_source_sample_index_exclusive"],
            gap_count=state.gap_count + 1,
        )
        candidate = _reset_generation_state(candidate)
        return candidate, (), ("explicit_gap_or_disconnect",)

    def _reconnect(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...], tuple[str, ...]]:
        sequence = chunk["sequence"]
        if state.status != "degraded":
            raise LiveSessionRefusal("reconnect_while_not_degraded")
        generation = sequence["reconnect_generation"]
        if generation < state.reconnect_generation + 1:
            raise LiveSessionRefusal("generation_rollback")
        if generation > state.reconnect_generation + 1:
            raise LiveSessionRefusal("generation_skip")
        if sequence["chunk_sequence_index"] != 0:
            raise LiveSessionRefusal("reconnect_without_generation_increment")
        if sequence["correction_segment_index"] != state.correction_segment_index + 1:
            raise LiveSessionRefusal("correction_ledger_tamper")
        first = chunk["sample_axis"]["first_source_sample_index"]
        if state.next_source_sample is not None and first != state.next_source_sample:
            raise LiveSessionRefusal("hidden_sample_gap")
        arrival_start = chunk["timestamps"]["arrival_monotonic_start_ns"]
        if (
            state.last_arrival_monotonic_end_ns is not None
            and arrival_start < state.last_arrival_monotonic_end_ns
        ):
            raise LiveSessionRefusal("arrival_monotonic_rollback")
        candidate = _reset_generation_state(state)
        candidate = replace(
            candidate,
            status="active",
            reconnect_generation=generation,
            correction_segment_index=sequence["correction_segment_index"],
            expected_sequence_index=1,
            next_source_sample=chunk["sample_axis"][
                "stop_source_sample_index_exclusive"
            ],
        )
        return candidate, (), ("reconnected_with_fresh_state",)

    def _end(
        self, state: _SessionState, chunk: SourceChunk
    ) -> tuple[_SessionState, tuple[FrameUpdate, ...], tuple[str, ...]]:
        self._require_active_continuity(state, chunk)
        if chunk["sequence"]["final_record"] is not True:
            raise LiveSessionRefusal("reordered_sequence")
        candidate = replace(
            state,
            status="closed",
            expected_sequence_index=state.expected_sequence_index + 1,
            frame_buffer=(),
            processor_state={},
            stable_symbol="",
            stable_count=0,
            provisional_hypothesis="",
        )
        return candidate, (), ("stream_closed",)

    def _update(
        self,
        state: _SessionState,
        chunk: SourceChunk,
        frames: tuple[FrameUpdate, ...],
        reasons: tuple[str, ...],
    ) -> LiveUpdate:
        sample_axis = chunk["sample_axis"]
        frame_reasons = tuple(
            reason for frame in frames for reason in frame.abstention_and_anomaly_reasons
        )
        clocks = frames[-1].clocks if frames else {
            "capture_start_ns": None,
            "capture_end_ns": None,
            "host_arrival_ns": chunk["timestamps"]["arrival_monotonic_end_ns"],
            "preprocessing_complete_ns": None,
            "model_complete_ns": None,
            "first_eligible_output_ns": None,
            "stable_commit_ns": None,
            "presentation_ns": None,
        }
        return LiveUpdate(
            reconnect_generation=state.reconnect_generation,
            correction_segment_index=state.correction_segment_index,
            accepted_source_sample_interval=(
                sample_axis["first_source_sample_index"],
                sample_axis["stop_source_sample_index_exclusive"],
            ),
            semantic_prefix_sha256=chunk.semantic_prefix_sha256,
            provisional_hypothesis=state.provisional_hypothesis,
            committed_delta="".join(frame.committed_delta for frame in frames),
            status=state.status,
            abstention_and_anomaly_reasons=reasons + frame_reasons,
            invalid_output_mask=(not frames or all(frame.invalid_output_mask for frame in frames)),
            warmup_boundary={
                "frame_samples": FRAME_SAMPLES,
                "warmup_valid_samples": WARMUP_SAMPLES,
                "generation_valid_samples": state.generation_valid_samples,
                "complete": state.generation_valid_samples >= WARMUP_SAMPLES,
                "first_output_eligible_frame_index": WARMUP_SAMPLES
                // FRAME_SAMPLES,
                "next_frame_output_eligible": state.next_frame_index
                >= WARMUP_SAMPLES // FRAME_SAMPLES,
            },
            clocks=clocks,
            binding_hashes=self._bindings.to_dict(),
            bounded_counters={
                "session_valid_samples": state.session_valid_samples,
                "generation_valid_samples": state.generation_valid_samples,
                "processor_events": state.event_count,
                "explicit_gaps": state.gap_count,
                "buffered_tail_samples": len(state.frame_buffer),
                "processor_state_bytes": _state_bytes(state.processor_state),
            },
            frame_updates=frames,
        )

    def _state_payload(self, state: _SessionState | None = None) -> dict[str, Any]:
        value = state if state is not None else self._state
        return {
            "status": value.status,
            "reconnect_generation": value.reconnect_generation,
            "correction_segment_index": value.correction_segment_index,
            "expected_sequence_index": value.expected_sequence_index,
            "next_source_sample": value.next_source_sample,
            "semantic_prefix_sha256": value.semantic_prefix_sha256,
            "semantic_element_count": value.semantic_element_count,
            "last_arrival_monotonic_end_ns": value.last_arrival_monotonic_end_ns,
            "last_source_timestamp_sec": value.last_source_timestamp_sec,
            "last_corrected_timestamp_sec": value.last_corrected_timestamp_sec,
            "nominal_sampling_rate_hz": value.nominal_sampling_rate_hz,
            "source_clock_domain": value.source_clock_domain,
            "corrected_clock_domain": value.corrected_clock_domain,
            "last_chunk_envelope_sha256": value.last_chunk_envelope_sha256,
            "last_chunk_sequence_index": value.last_chunk_sequence_index,
            "frame_buffer": [
                {
                    "source_index": sample.source_index,
                    "values": list(sample.values),
                    "source_timestamp_sec": sample.source_timestamp_sec,
                    "corrected_timestamp_sec": sample.corrected_timestamp_sec,
                    "arrival_monotonic_ns": sample.arrival_monotonic_ns,
                }
                for sample in value.frame_buffer
            ],
            "next_frame_index": value.next_frame_index,
            "generation_valid_samples": value.generation_valid_samples,
            "session_valid_samples": value.session_valid_samples,
            "event_count": value.event_count,
            "gap_count": value.gap_count,
            "processor_state": copy.deepcopy(dict(value.processor_state)),
            "provisional_hypothesis": value.provisional_hypothesis,
            "committed_output": value.committed_output,
            "stable_symbol": value.stable_symbol,
            "stable_count": value.stable_count,
            "rearmed": value.rearmed,
            "first_eligible_output_ns": value.first_eligible_output_ns,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return one canonical, self-hashed, target-free session snapshot."""

        payload = {
            "schema": {"name": SCHEMA_NAME, "version": SCHEMA_VERSION},
            "bindings": self._bindings.to_dict(),
            "policy": {
                "frame_samples": FRAME_SAMPLES,
                "warmup_valid_samples": WARMUP_SAMPLES,
                "minimum_confidence": self._minimum_confidence,
                "stable_updates_required": self._stable_updates_required,
            },
            "state": self._state_payload(),
        }
        assert_target_free(payload)
        snapshot_hash = _hash(payload)
        result = {**payload, "snapshot_sha256": snapshot_hash}
        if len(canonical_json_bytes(result)) > MAX_MUTABLE_STATE_BYTES:
            raise LiveSessionRefusal("processor_state_cap_breach", "snapshot bytes")
        return result

    def snapshot_bytes(self) -> bytes:
        return canonical_json_bytes(self.snapshot())

    @classmethod
    def restore(
        cls,
        snapshot: Mapping[str, Any],
        *,
        bindings: SessionBindings,
        processor: Processor,
        expected_semantic_prefix_sha256: str | None,
        expected_semantic_element_count: int,
    ) -> LiveSession:
        """Restore only a strictly bound and self-hashed snapshot."""

        expected_fields = {"schema", "bindings", "policy", "state", "snapshot_sha256"}
        if set(snapshot) != expected_fields:
            raise LiveSessionRefusal("snapshot_tamper")
        assert_target_free(snapshot)
        if snapshot["schema"] != {"name": SCHEMA_NAME, "version": SCHEMA_VERSION}:
            raise LiveSessionRefusal("snapshot_tamper")
        payload = {key: copy.deepcopy(value) for key, value in snapshot.items() if key != "snapshot_sha256"}
        if snapshot["snapshot_sha256"] != _hash(payload):
            raise LiveSessionRefusal("snapshot_tamper")
        if snapshot["bindings"] != bindings.to_dict():
            raise LiveSessionRefusal("snapshot_source_config_model_or_prefix_collision")
        policy = snapshot["policy"]
        if set(policy) != {
            "frame_samples",
            "warmup_valid_samples",
            "minimum_confidence",
            "stable_updates_required",
        }:
            raise LiveSessionRefusal("snapshot_tamper")
        if policy["frame_samples"] != FRAME_SAMPLES or policy["warmup_valid_samples"] != WARMUP_SAMPLES:
            raise LiveSessionRefusal("snapshot_tamper")
        session = cls(
            bindings=bindings,
            processor=processor,
            minimum_confidence=float(policy["minimum_confidence"]),
            stable_updates_required=_strict_int(
                policy["stable_updates_required"], refusal_id="snapshot_tamper"
            ),
        )
        session._state = session._state_from_payload(snapshot["state"])
        if (
            session._state.semantic_prefix_sha256
            != expected_semantic_prefix_sha256
            or session._state.semantic_element_count
            != expected_semantic_element_count
        ):
            raise LiveSessionRefusal(
                "snapshot_source_config_model_or_prefix_collision", "semantic prefix"
            )
        if session.snapshot_bytes() != canonical_json_bytes(snapshot):
            raise LiveSessionRefusal("snapshot_tamper")
        return session

    def _state_from_payload(self, payload: Any) -> _SessionState:
        if not isinstance(payload, Mapping):
            raise LiveSessionRefusal("snapshot_tamper")
        expected = set(self._state_payload())
        if set(payload) != expected:
            raise LiveSessionRefusal("snapshot_tamper")
        buffer_value = payload["frame_buffer"]
        if not isinstance(buffer_value, list):
            raise LiveSessionRefusal("snapshot_tamper")
        frame_buffer: list[_Sample] = []
        for row in buffer_value:
            if not isinstance(row, Mapping) or set(row) != {
                "source_index",
                "values",
                "source_timestamp_sec",
                "corrected_timestamp_sec",
                "arrival_monotonic_ns",
            }:
                raise LiveSessionRefusal("snapshot_tamper")
            values = row["values"]
            if not isinstance(values, list) or not values:
                raise LiveSessionRefusal("snapshot_tamper")
            source_index = _strict_int(
                row["source_index"], refusal_id="snapshot_tamper"
            )
            arrival_ns = _strict_int(
                row["arrival_monotonic_ns"], refusal_id="snapshot_tamper"
            )
            if source_index < 0 or arrival_ns < 0:
                raise LiveSessionRefusal("snapshot_tamper")
            frame_buffer.append(
                _Sample(
                    source_index=source_index,
                    values=tuple(
                        float(_snapshot_float(value)) for value in values
                    ),
                    source_timestamp_sec=float(
                        _snapshot_float(row["source_timestamp_sec"])
                    ),
                    corrected_timestamp_sec=_snapshot_float(
                        row["corrected_timestamp_sec"], nullable=True
                    ),
                    arrival_monotonic_ns=arrival_ns,
                )
            )
        if len(frame_buffer) >= FRAME_SAMPLES:
            raise LiveSessionRefusal("snapshot_tamper")
        if any(
            right.source_index != left.source_index + 1
            for left, right in zip(frame_buffer, frame_buffer[1:])
        ):
            raise LiveSessionRefusal("snapshot_tamper")
        processor_state = payload["processor_state"]
        if not isinstance(processor_state, Mapping):
            raise LiveSessionRefusal("snapshot_tamper")
        for field in (
            "status",
            "provisional_hypothesis",
            "committed_output",
            "stable_symbol",
        ):
            if not isinstance(payload[field], str):
                raise LiveSessionRefusal("snapshot_tamper")
        state = _SessionState(
            status=payload["status"],
            reconnect_generation=_strict_int(payload["reconnect_generation"], refusal_id="snapshot_tamper"),
            correction_segment_index=_strict_int(payload["correction_segment_index"], refusal_id="snapshot_tamper"),
            expected_sequence_index=_strict_int(payload["expected_sequence_index"], refusal_id="snapshot_tamper"),
            next_source_sample=_snapshot_optional_int(payload["next_source_sample"]),
            semantic_prefix_sha256=payload["semantic_prefix_sha256"],
            semantic_element_count=_strict_int(payload["semantic_element_count"], refusal_id="snapshot_tamper"),
            last_arrival_monotonic_end_ns=_snapshot_optional_int(
                payload["last_arrival_monotonic_end_ns"]
            ),
            last_source_timestamp_sec=_snapshot_float(
                payload["last_source_timestamp_sec"], nullable=True
            ),
            last_corrected_timestamp_sec=_snapshot_float(
                payload["last_corrected_timestamp_sec"], nullable=True
            ),
            nominal_sampling_rate_hz=_snapshot_float(
                payload["nominal_sampling_rate_hz"], nullable=True
            ),
            source_clock_domain=_snapshot_optional_string(payload["source_clock_domain"]),
            corrected_clock_domain=_snapshot_optional_string(
                payload["corrected_clock_domain"]
            ),
            last_chunk_envelope_sha256=_snapshot_optional_string(
                payload["last_chunk_envelope_sha256"]
            ),
            last_chunk_sequence_index=_snapshot_optional_int(
                payload["last_chunk_sequence_index"]
            ),
            frame_buffer=tuple(frame_buffer),
            next_frame_index=_strict_int(payload["next_frame_index"], refusal_id="snapshot_tamper"),
            generation_valid_samples=_strict_int(payload["generation_valid_samples"], refusal_id="snapshot_tamper"),
            session_valid_samples=_strict_int(payload["session_valid_samples"], refusal_id="snapshot_tamper"),
            event_count=_strict_int(payload["event_count"], refusal_id="snapshot_tamper"),
            gap_count=_strict_int(payload["gap_count"], refusal_id="snapshot_tamper"),
            processor_state=copy.deepcopy(dict(processor_state)),
            provisional_hypothesis=payload["provisional_hypothesis"],
            committed_output=payload["committed_output"],
            stable_symbol=payload["stable_symbol"],
            stable_count=_strict_int(payload["stable_count"], refusal_id="snapshot_tamper"),
            rearmed=payload["rearmed"],
            first_eligible_output_ns=_snapshot_optional_int(
                payload["first_eligible_output_ns"]
            ),
        )
        if state.status not in {"created", "active", "degraded", "closed"} or not isinstance(state.rearmed, bool):
            raise LiveSessionRefusal("snapshot_tamper")
        if (
            state.expected_sequence_index < 0
            or state.semantic_element_count < 0
            or state.next_frame_index < 0
            or state.generation_valid_samples < 0
            or not 0 <= state.session_valid_samples <= MAX_SESSION_SAMPLES
            or not 0 <= state.event_count <= MAX_EVENTS
            or not 0 <= state.gap_count <= MAX_GAPS
            or state.stable_count < 0
            or (
                state.first_eligible_output_ns is not None
                and state.first_eligible_output_ns < 0
            )
        ):
            raise LiveSessionRefusal("snapshot_tamper")
        if state.generation_valid_samples % FRAME_SAMPLES != len(state.frame_buffer):
            raise LiveSessionRefusal("snapshot_tamper")
        if state.next_frame_index != state.generation_valid_samples // FRAME_SAMPLES:
            raise LiveSessionRefusal("snapshot_tamper")
        if state.frame_buffer and (
            state.next_source_sample != state.frame_buffer[-1].source_index + 1
        ):
            raise LiveSessionRefusal("snapshot_tamper")
        if state.stable_count == 0 and state.stable_symbol:
            raise LiveSessionRefusal("snapshot_tamper")
        if state.stable_count > 0 and not state.stable_symbol:
            raise LiveSessionRefusal("snapshot_tamper")
        if state.status == "created":
            if state != _SessionState():
                raise LiveSessionRefusal("snapshot_tamper")
        else:
            if (
                state.reconnect_generation < 0
                or state.correction_segment_index < 0
                or state.next_source_sample is None
                or state.semantic_prefix_sha256 is None
                or HASH_RE.fullmatch(state.semantic_prefix_sha256) is None
                or state.semantic_element_count < 1
                or state.nominal_sampling_rate_hz is None
                or not 0 < state.nominal_sampling_rate_hz <= 4096
                or state.source_clock_domain is None
                or state.last_chunk_envelope_sha256 is None
                or HASH_RE.fullmatch(state.last_chunk_envelope_sha256) is None
                or state.last_chunk_sequence_index is None
            ):
                raise LiveSessionRefusal("snapshot_tamper")
        if state.status in {"degraded", "closed"} and (
            state.frame_buffer
            or state.processor_state
            or state.stable_symbol
            or state.stable_count
        ):
            raise LiveSessionRefusal("snapshot_tamper")
        _state_bytes(self._state_payload(state))
        return state


def make_session_bindings(
    chunk: SourceChunk,
    *,
    processor: Processor,
    minimum_confidence: float = MINIMUM_CONFIDENCE,
    stable_updates_required: int = STABLE_UPDATES_REQUIRED,
) -> SessionBindings:
    """Create deterministic generated-only bindings from one validated start chunk."""

    provenance = chunk["provenance"]
    mapping = _clock_mapping_payload(chunk)
    if (
        mapping["source_clock_domain"] != "synthetic_relative_monotonic"
        or mapping["corrected_clock_domain"] != mapping["source_clock_domain"]
        or mapping["correction_applied"] is not True
        or not isinstance(mapping["correction_method"], str)
        or not mapping["correction_method"]
        or not isinstance(mapping["correction_ledger_sha256"], str)
        or HASH_RE.fullmatch(mapping["correction_ledger_sha256"]) is None
    ):
        raise LiveSessionRefusal(
            "capture_arrival_clock_order_violation", "unverified generated mapping"
        )
    return SessionBindings(
        source_bindings_sha256=chunk.bindings.sha256,
        source_identity_sha256=_identity_hash(chunk),
        modality_sha256=_hash(chunk["identity"]["modality"]),
        device_type_sha256=_hash(chunk["identity"]["device_type"]),
        channel_contract_sha256=_channel_hash(chunk),
        sampling_rate_sha256=_hash(chunk["sample_axis"]["nominal_sampling_rate_hz"]),
        correction_ledger_sha256=_hash(
            chunk["timestamps"]["correction_ledger_sha256"]
        ),
        clock_mapping_sha256=_hash(mapping),
        source_config_sha256=provenance["source_config_sha256"],
        split_protocol_sha256=provenance["split_protocol_sha256"],
        adapter_config_sha256=provenance["adapter_config_sha256"],
        processor_config_sha256=_processor_binding(
            processor, "processor_config_sha256"
        ),
        model_sha256=_processor_binding(processor, "model_sha256"),
        decoder_sha256=_decoder_sha256(),
        policy_sha256=_hash(
            {
                "frame_samples": FRAME_SAMPLES,
                "warmup_valid_samples": WARMUP_SAMPLES,
                "minimum_confidence": float(minimum_confidence),
                "stable_updates_required": int(stable_updates_required),
            }
        ),
    )
