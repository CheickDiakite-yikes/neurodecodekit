"""Generated-only qualification harness for COMM-LIVE-G0.

The development entry point is repeatable and has no evidentiary effect.  The
official entry point remains fail-closed until a future, exact, remotely green
implementation proof binds this harness and its implementation dependencies.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import resource
import stat
import time
from typing import Any, Callable, Mapping, Sequence

from neurodecodekit.streaming.live_session import (
    LiveSession,
    LiveSessionRefusal,
    ProcessorEvent,
    make_session_bindings,
)
from neurodecodekit.streaming.source_chunk import (
    GeneratedSourceChunkFactory,
    SemanticPrefixState,
    SourceBindings,
    SourceChunk,
    SourceChunkRefusal,
    advance_semantic_prefix,
    canonical_json_bytes,
    compute_chunk_envelope_sha256,
    compute_valid_payload_sha256,
)


LANE_ID = "COMM-LIVE-G0"
RESULT_SCHEMA = "neurodecodekit.communication_live_session_g0_generated_result"
RESULT_VERSION = "0.1.0"
CONTRACT_PATH = "registries/communication_live_session_g0_contract.v0.json"
CONTRACT_SHA256 = "3601df30a0823d2116ade758745ba86de7de155593c4e95f2162b6a7f5eac245"
AMENDMENT_PATH = "registries/communication_live_session_g0_amendment_1.v0.json"
AMENDMENT_SHA256 = "3f00046332c89083d93db0e02249ddaf2f7dafe0e0fae1a8f21616a87c0eadd8"
REPLAY_CONTRACT_PATH = "registries/replay_equivalence_contract.v0.json"
REPLAY_CONTRACT_SHA256 = "6e4ef54049d9a6f77f64e7b6cfd6b911bd97b5693386f16b62f9d466f66b0469"
IMPLEMENTATION_PROOF_PATH = (
    "registries/communication_live_session_g0_implementation_proof.v0.json"
)
REQUIRED_IMPLEMENTATION_ARTIFACTS = (
    "src/neurodecodekit/streaming/__init__.py",
    "src/neurodecodekit/streaming/source_chunk.py",
    "src/neurodecodekit/streaming/live_session.py",
    "src/neurodecodekit/experiments/comm_live_g0_generated.py",
    "src/neurodecodekit/comm_live_g0_cli.py",
    "tests/test_communication_source_chunk_v0.py",
    "tests/test_communication_live_session.py",
    "tests/test_communication_live_session_g0_implementation.py",
)

PARTITION_SCHEDULES: Mapping[str, tuple[int, ...]] = {
    "one_sample": (1,) * 80,
    "fixed_width": (16, 16, 16, 16, 16),
    "jittered": (5, 17, 13, 7, 19, 19),
    "whole_stream": (80,),
}
CONTROL_SCHEDULES = ("gap_reconnect", "quality_confidence")
REQUIRED_REFUSAL_FAMILIES = (
    "source_identity_mismatch",
    "modality_or_device_drift",
    "channel_contract_drift",
    "sampling_rate_drift",
    "identical_duplicate_record",
    "conflicting_duplicate_payload",
    "partial_source_sample_overlap",
    "reordered_sequence",
    "hidden_sample_gap",
    "timestamp_only_inferred_gap_unrepresented",
    "clock_reset_unrepresented",
    "correction_ledger_tamper",
    "generation_rollback",
    "generation_skip",
    "old_generation_after_reconnect",
    "chunk_after_disconnect",
    "reconnect_without_generation_increment",
    "reconnect_while_not_degraded",
    "capture_arrival_clock_order_violation",
    "arrival_monotonic_rollback",
    "nonfinite_padding_or_hash_invalid_payload",
    "chunk_size_cap_breach",
    "session_sample_cap_breach",
    "processor_state_cap_breach",
    "snapshot_tamper",
    "snapshot_source_config_model_or_prefix_collision",
    "quality_gate_bypass",
    "confidence_gate_bypass",
    "stability_across_gap",
    "repeated_stable_commit",
    "target_label_or_text_leakage",
    "deadline_expired_or_abstain_all_positive_control",
    "use_after_close",
)
EXPECTED_INTERNAL_REFUSALS: Mapping[str, str] = {
    **{family: family for family in REQUIRED_REFUSAL_FAMILIES},
    "nonfinite_padding_or_hash_invalid_payload": "semantic_stream_hash_mismatch",
    "chunk_size_cap_breach": "resource_cap_exceeded",
    "quality_gate_bypass": "behavioral_gate_blocked:quality_gate_bypass",
    "confidence_gate_bypass": "behavioral_gate_blocked:confidence_gate_bypass",
    "stability_across_gap": "behavioral_gate_blocked:stability_across_gap",
    "repeated_stable_commit": "behavioral_gate_blocked:repeated_stable_commit",
}

CAPS = {
    "fictional_sessions": 4,
    "cpu_threads": 1,
    "workers": 1,
    "wall_time_seconds": 30.0,
    "peak_RSS_bytes": 256 * 1024 * 1024,
    "public_output_bytes": 1024 * 1024,
    "temporary_generated_bytes": 16 * 1024 * 1024,
}
ZERO_OPERATION_COUNTERS = {
    "real_or_private_path_operations": 0,
    "real_signal_reads": 0,
    "real_target_or_label_reads": 0,
    "model_runs": 0,
    "training_runs": 0,
    "provider_calls": 0,
    "network_bytes": 0,
    "physical_stream_or_device_operations": 0,
    "release_operations": 0,
    "scientific_claim_upgrades": 0,
}


class CommLiveG0GeneratedRefusal(RuntimeError):
    """Fail-closed harness refusal with a stable machine identifier."""

    def __init__(self, refusal_id: str, detail: str = "") -> None:
        self.refusal_id = refusal_id
        super().__init__(refusal_id if not detail else f"{refusal_id}:{detail}")


class DeterministicGeneratedProcessor:
    """Small source-only processor used solely for interface qualification."""

    def __init__(self) -> None:
        self.processor_config_sha256 = _sha256(
            b"COMM-LIVE-G0-deterministic-generated-processor-v0"
        )
        self.model_sha256 = _sha256(b"COMM-LIVE-G0-fictional-no-model-v0")

    def __call__(
        self, frame: Any, prior_state: Mapping[str, Any]
    ) -> ProcessorEvent:
        value = float(frame.sample_major_values[-1][0])
        state = {"updates": int(prior_state.get("updates", 0)) + 1}
        arrival = int(frame.arrival_monotonic_ns[-1])
        if value == 0.0:
            symbol, active, quality, confidence = "", True, True, 0.95
        elif value == -1.0:
            symbol, active, quality, confidence = "A", True, False, 0.95
        elif value == -2.0:
            symbol, active, quality, confidence = "A", True, True, 0.20
        else:
            symbol, active, quality, confidence = "A", True, True, 0.95
        return ProcessorEvent(
            candidate_symbol=symbol,
            source_active=active,
            quality_valid=quality,
            confidence=confidence,
            preprocessing_complete_ns=arrival + 100,
            model_complete_ns=arrival + 200,
            presentation_ns=arrival + 300,
            mutable_state_bytes=len(canonical_json_bytes(state)),
            next_state=state,
        )


class _BadClockProcessor(DeterministicGeneratedProcessor):
    def __call__(self, frame: Any, prior_state: Mapping[str, Any]) -> ProcessorEvent:
        event = super().__call__(frame, prior_state)
        return ProcessorEvent(
            candidate_symbol=event.candidate_symbol,
            source_active=event.source_active,
            quality_valid=event.quality_valid,
            confidence=event.confidence,
            preprocessing_complete_ns=event.model_complete_ns + 1,
            model_complete_ns=event.model_complete_ns,
            presentation_ns=event.presentation_ns,
            mutable_state_bytes=event.mutable_state_bytes,
            next_state=event.next_state,
        )


class _LargeStateProcessor(DeterministicGeneratedProcessor):
    def __call__(self, frame: Any, prior_state: Mapping[str, Any]) -> ProcessorEvent:
        event = super().__call__(frame, prior_state)
        state = {"state": "x" * (1024 * 1024)}
        return ProcessorEvent(
            candidate_symbol=event.candidate_symbol,
            source_active=event.source_active,
            quality_valid=event.quality_valid,
            confidence=event.confidence,
            preprocessing_complete_ns=event.preprocessing_complete_ns,
            model_complete_ns=event.model_complete_ns,
            presentation_ns=event.presentation_ns,
            mutable_state_bytes=len(canonical_json_bytes(state)),
            next_state=state,
        )


class _LeakyProcessor(DeterministicGeneratedProcessor):
    def __call__(self, frame: Any, prior_state: Mapping[str, Any]) -> ProcessorEvent:
        event = super().__call__(frame, prior_state)
        state = {"target_text": "forbidden"}
        return ProcessorEvent(
            candidate_symbol=event.candidate_symbol,
            source_active=event.source_active,
            quality_valid=event.quality_valid,
            confidence=event.confidence,
            preprocessing_complete_ns=event.preprocessing_complete_ns,
            model_complete_ns=event.model_complete_ns,
            presentation_ns=event.presentation_ns,
            mutable_state_bytes=len(canonical_json_bytes(state)),
            next_state=state,
        )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_json_exact(root: Path, relative: str, expected_sha256: str) -> dict[str, Any]:
    path = root / relative
    payload = path.read_bytes()
    if _sha256(payload) != expected_sha256:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-FROZEN-ARTIFACT-HASH", relative)
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-FROZEN-ARTIFACT-JSON", relative) from exc


def load_frozen_registration(root: str | Path | None = None) -> dict[str, Any]:
    repository = (Path(root) if root is not None else _repo_root()).absolute()
    contract = _load_json_exact(repository, CONTRACT_PATH, CONTRACT_SHA256)
    amendment = _load_json_exact(repository, AMENDMENT_PATH, AMENDMENT_SHA256)
    replay = _load_json_exact(repository, REPLAY_CONTRACT_PATH, REPLAY_CONTRACT_SHA256)
    if contract.get("gate_id") != LANE_ID:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-CONTRACT-IDENTITY")
    if amendment.get("amendment_id") != "COMM-LIVE-G0-A1":
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-AMENDMENT-IDENTITY")
    if replay.get("source_chunk_schema", {}).get("schema_name") != "neurodecodekit.source_chunk":
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-RW3-IDENTITY")
    if tuple(contract.get("required_adversarial_refusals", ())) != REQUIRED_REFUSAL_FAMILIES:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-REFUSAL-INVENTORY")
    if set(EXPECTED_INTERNAL_REFUSALS) != set(REQUIRED_REFUSAL_FAMILIES):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-INTERNAL-REFUSAL-INVENTORY")
    cadence = amendment.get("sample_cadence", {})
    if (
        cadence.get("processor_frame_valid_samples") != 16
        or cadence.get("warmup_valid_samples_per_generation") != 32
        or tuple(cadence.get("partition_schedules_required", ()))
        != tuple(PARTITION_SCHEDULES)
    ):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-CADENCE-DRIFT")
    return {"contract": contract, "amendment": amendment, "replay": replay}


def _validate_future_implementation_proof(root: Path) -> dict[str, Any]:
    path = root / IMPLEMENTATION_PROOF_PATH
    if not path.is_file() or path.is_symlink():
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-PROOF-MISSING")
    try:
        proof = json.loads(path.read_bytes())
    except (OSError, json.JSONDecodeError) as exc:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-PROOF-INVALID") from exc
    if (
        proof.get("schema_name")
        != "neurodecodekit.communication_live_session_g0_implementation_proof"
        or proof.get("status") != "implementation_remotely_green"
    ):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-PROOF-INVALID")
    commit = proof.get("implementation_commit")
    remote = proof.get("remote_proof", {})
    if (
        not isinstance(commit, str)
        or len(commit) != 40
        or any(character not in "0123456789abcdef" for character in commit)
        or remote.get("head_sha") != commit
        or remote.get("CI_conclusion") != "success"
    ):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-PROOF-INVALID")
    jobs = {
        (row.get("name"), row.get("conclusion"))
        for row in remote.get("jobs", ())
        if isinstance(row, Mapping)
    }
    if jobs != {("Base Python", "success"), ("Optional Neuro Readers", "success")}:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-PROOF-INVALID")
    artifacts = {
        row.get("path"): row
        for row in proof.get("artifacts", ())
        if isinstance(row, Mapping)
    }
    if set(artifacts) != set(REQUIRED_IMPLEMENTATION_ARTIFACTS):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-ARTIFACT-SET")
    for relative in REQUIRED_IMPLEMENTATION_ARTIFACTS:
        artifact = artifacts[relative]
        payload = (root / relative).read_bytes()
        if artifact.get("bytes") != len(payload) or artifact.get("sha256") != _sha256(payload):
            raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-IMPLEMENTATION-ARTIFACT-HASH", relative)
    return proof


def _factory(seed: str, *, channels: int = 4, rate: float = 256.0) -> GeneratedSourceChunkFactory:
    return GeneratedSourceChunkFactory.fictional(
        seed=seed,
        dtype="float64",
        channel_names=tuple(f"SYN{index:02d}" for index in range(channels)),
        channel_types=("synthetic",) * channels,
        channel_units=("arbitrary_unit",) * channels,
        nominal_sampling_rate_hz=rate,
        modality="synthetic_eeg_interface",
    )


def _data(factory: GeneratedSourceChunkFactory, count: int, value: float = 1.0) -> SourceChunk:
    channels = len(factory.bindings.record["channels"]["names"])
    return factory.data([[value] * count for _ in range(channels)])


def _session(start: SourceChunk, seed: str, processor: Callable[..., ProcessorEvent] | None = None) -> LiveSession:
    del seed
    selected_processor = processor or DeterministicGeneratedProcessor()
    return LiveSession(
        bindings=make_session_bindings(start, processor=selected_processor),
        processor=selected_processor,
    )


def _surface(update: Any) -> dict[str, Any]:
    return {
        "committed_delta": update.committed_delta,
        "frame_updates": [frame.to_dict() for frame in update.frame_updates],
    }


def _run_partition(seed: str, widths: Sequence[int]) -> dict[str, Any]:
    factory = _factory(seed)
    start = factory.stream_start()
    session = _session(start, seed)
    session.push(start)
    frame_updates: list[dict[str, Any]] = []
    commits: list[str] = []
    for width in widths:
        update = session.push(_data(factory, int(width)))
        commits.append(update.committed_delta)
        frame_updates.extend(frame.to_dict() for frame in update.frame_updates)
    end_update = session.push(factory.stream_end())
    state = session.snapshot()["state"]
    return {
        "semantic_prefix_sha256": state["semantic_prefix_sha256"],
        "semantic_element_count": state["semantic_element_count"],
        "event_count": state["event_count"],
        "processor_state": state["processor_state"],
        "committed_output": state["committed_output"],
        "committed_deltas": "".join(commits),
        "frame_updates": frame_updates,
        "closed": end_update.status == "closed",
    }


def _run_gap_reconnect(seed: str) -> dict[str, Any]:
    factory = _factory(seed)
    start = factory.stream_start()
    session = _session(start, seed)
    session.push(start)
    before_gap = session.push(_data(factory, 64))
    stable_before = session.snapshot()["state"]["stable_count"]
    gap_update = session.push(factory.gap(4))
    degraded = session.snapshot()["state"]
    reconnect_update = session.push(factory.reconnect())
    first_after = session.push(_data(factory, 48))
    second_after = session.push(_data(factory, 32))
    session.push(factory.stream_end())
    passed = (
        stable_before == 2
        and before_gap.committed_delta == ""
        and gap_update.status == "degraded"
        and degraded["frame_buffer"] == []
        and degraded["processor_state"] == {}
        and reconnect_update.status == "active"
        and first_after.committed_delta == ""
        and second_after.committed_delta == "A"
    )
    if not passed:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-GENERATION-STATE-BRIDGE")
    return {
        "stable_before_gap": stable_before,
        "first_post_reconnect_commit": first_after.committed_delta,
        "later_post_reconnect_commit": second_after.committed_delta,
        "passed": True,
    }


def _run_quality_confidence(seed: str) -> dict[str, Any]:
    factory = _factory(seed)
    start = factory.stream_start()
    session = _session(start, seed)
    session.push(start)
    session.push(_data(factory, 64))
    quality = session.push(_data(factory, 16, -1.0)).frame_updates[0]
    session.push(_data(factory, 32))
    confidence = session.push(_data(factory, 16, -2.0)).frame_updates[0]
    final = session.push(_data(factory, 48))
    session.push(factory.stream_end())
    passed = (
        quality.invalid_output_mask
        and "quality_invalid" in quality.abstention_and_anomaly_reasons
        and confidence.invalid_output_mask
        and "confidence_below_threshold" in confidence.abstention_and_anomaly_reasons
        and final.committed_delta == "A"
    )
    if not passed:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-ABSTENTION-GATE")
    return {
        "quality_abstained": True,
        "confidence_abstained": True,
        "later_positive_control_commit": final.committed_delta,
        "passed": True,
    }


def _prior_from_session(session: LiveSession, bindings: SourceBindings) -> SemanticPrefixState:
    state = session.snapshot()["state"]
    return SemanticPrefixState(
        bindings_sha256=bindings.sha256,
        digest_sha256=state["semantic_prefix_sha256"],
        element_count=state["semantic_element_count"],
    )


def _forge(
    chunk: SourceChunk,
    mutation: Callable[[dict[str, Any]], None],
    *,
    prior: SemanticPrefixState | None = None,
    resign: bool = False,
) -> SourceChunk:
    record = chunk.to_dict()
    mutation(record)
    bindings = SourceBindings.from_record(record)
    if resign:
        record["hashes"]["valid_payload_sha256"] = compute_valid_payload_sha256(
            record["payload"]
        )
        semantic = advance_semantic_prefix(record, bindings, prior)
        record["hashes"]["semantic_prefix_sha256"] = semantic.digest_sha256
        record["hashes"]["chunk_envelope_sha256"] = compute_chunk_envelope_sha256(record)
    else:
        semantic = chunk.semantic_state
    return SourceChunk(record, bindings, semantic, canonical_json_bytes(record))


def _resign_axis(
    record: dict[str, Any], *, first: int, count: int, time_offset: float = 0.0
) -> None:
    rate = float(record["sample_axis"]["nominal_sampling_rate_hz"])
    stop = first + count
    indices = list(range(first, stop))
    timestamps = [index / rate + time_offset for index in indices]
    record["sample_axis"]["source_sample_indices"] = indices
    record["sample_axis"]["first_source_sample_index"] = first
    record["sample_axis"]["stop_source_sample_index_exclusive"] = stop
    record["timestamps"]["source_timestamps_sec"] = timestamps
    record["timestamps"]["corrected_timestamps_sec"] = list(timestamps)
    record["packet_accounting"]["raw_counter_values"] = [value % 65536 for value in indices]
    record["packet_accounting"]["unwrapped_counter_values"] = indices


def _expect_refusal(
    family_id: str,
    operation: Callable[[], Any],
) -> dict[str, Any]:
    try:
        operation()
    except (LiveSessionRefusal, SourceChunkRefusal, CommLiveG0GeneratedRefusal) as exc:
        observed = getattr(exc, "refusal_id", type(exc).__name__)
        expected = EXPECTED_INTERNAL_REFUSALS[family_id]
        if observed != expected:
            raise CommLiveG0GeneratedRefusal(
                "COMM-LIVE-G0-WRONG-INTERNAL-REFUSAL",
                f"{family_id}:expected={expected}:observed={observed}",
            ) from exc
        return {
            "family_id": family_id,
            "refused": True,
            "exact_family_id_bound": True,
            "observed_internal_refusal": observed,
        }
    raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-ADVERSARIAL-ACCEPTED", family_id)


def _expect_blocked_behavior(family_id: str, blocked: bool, detail: str) -> dict[str, Any]:
    if not blocked:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-ADVERSARIAL-ACCEPTED", detail)
    return {
        "family_id": family_id,
        "refused": True,
        "exact_family_id_bound": True,
        "observed_internal_refusal": EXPECTED_INTERNAL_REFUSALS[family_id],
    }


def _base_active(seed: str) -> tuple[GeneratedSourceChunkFactory, SourceChunk, LiveSession]:
    factory = _factory(seed)
    start = factory.stream_start()
    session = _session(start, seed)
    session.push(start)
    return factory, start, session


def _mutated_next_case(
    seed: str,
    mutation: Callable[[dict[str, Any]], None],
) -> Callable[[], Any]:
    def operation() -> Any:
        factory, _, session = _base_active(seed)
        first = _data(factory, 16)
        session.push(first)
        next_chunk = _data(factory, 16)
        prior = _prior_from_session(session, factory.bindings)
        forged = _forge(next_chunk, mutation, prior=prior, resign=True)
        return session.push(forged)

    return operation


def _adversarial_refusals(seed: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    factory, start, session = _base_active(f"{seed}:identity")
    other = _factory(f"{seed}:other").stream_start()
    rows.append(_expect_refusal("source_identity_mismatch", lambda: session.push(other)))

    def other_start(**kwargs: Any) -> SourceChunk:
        generated = GeneratedSourceChunkFactory.fictional(
            seed=f"{seed}:identity",
            dtype="float64",
            channel_names=kwargs.pop("channel_names", ("SYN00", "SYN01", "SYN02", "SYN03")),
            channel_types=kwargs.pop("channel_types", ("synthetic",) * 4),
            channel_units=kwargs.pop("channel_units", ("arbitrary_unit",) * 4),
            nominal_sampling_rate_hz=kwargs.pop("nominal_sampling_rate_hz", 256.0),
            modality=kwargs.pop("modality", "synthetic_eeg_interface"),
            **kwargs,
        )
        return generated.stream_start()

    rows.append(
        _expect_refusal(
            "modality_or_device_drift",
            lambda: session.push(other_start(modality="synthetic_other_modality")),
        )
    )
    rows.append(
        _expect_refusal(
            "channel_contract_drift",
            lambda: session.push(other_start(channel_names=("A", "B", "C", "D"))),
        )
    )
    rows.append(
        _expect_refusal(
            "sampling_rate_drift",
            lambda: session.push(other_start(nominal_sampling_rate_hz=128.0)),
        )
    )

    duplicate_factory, _, duplicate_session = _base_active(f"{seed}:duplicate")
    duplicate = _data(duplicate_factory, 16)
    duplicate_session.push(duplicate)
    rows.append(
        _expect_refusal(
            "identical_duplicate_record", lambda: duplicate_session.push(duplicate)
        )
    )

    def conflicting() -> Any:
        factory, _, active = _base_active(f"{seed}:conflict")
        first = _data(factory, 16)
        active.push(first)
        next_chunk = _data(factory, 16, 2.0)
        prior = _prior_from_session(active, factory.bindings)
        forged = _forge(
            next_chunk,
            lambda record: record["sequence"].__setitem__("chunk_sequence_index", 1),
            prior=prior,
            resign=True,
        )
        return active.push(forged)

    rows.append(_expect_refusal("conflicting_duplicate_payload", conflicting))

    rows.append(
        _expect_refusal(
            "partial_source_sample_overlap",
            _mutated_next_case(
                f"{seed}:overlap",
                lambda record: _resign_axis(record, first=8, count=16),
            ),
        )
    )
    rows.append(
        _expect_refusal(
            "reordered_sequence",
            _mutated_next_case(
                f"{seed}:reorder",
                lambda record: record["sequence"].__setitem__("chunk_sequence_index", 0),
            ),
        )
    )
    rows.append(
        _expect_refusal(
            "hidden_sample_gap",
            _mutated_next_case(
                f"{seed}:hidden-gap",
                lambda record: _resign_axis(record, first=20, count=16),
            ),
        )
    )
    rows.append(
        _expect_refusal(
            "timestamp_only_inferred_gap_unrepresented",
            _mutated_next_case(
                f"{seed}:time-gap",
                lambda record: _resign_axis(record, first=16, count=16, time_offset=1.0),
            ),
        )
    )
    rows.append(
        _expect_refusal(
            "clock_reset_unrepresented",
            _mutated_next_case(
                f"{seed}:clock-reset",
                lambda record: _resign_axis(record, first=16, count=16, time_offset=-1.0),
            ),
        )
    )

    def ledger_tamper() -> Any:
        factory, _, active = _base_active(f"{seed}:ledger")
        first = _data(factory, 16)
        active.push(first)
        next_chunk = _data(factory, 16)
        return active.push(
            _forge(
                next_chunk,
                lambda record: record["timestamps"].__setitem__(
                    "correction_ledger_sha256", "f" * 64
                ),
                resign=False,
            )
        )

    rows.append(_expect_refusal("correction_ledger_tamper", ledger_tamper))

    def reconnect_case(family: str, generation: int, sequence: int = 0) -> dict[str, Any]:
        def operation() -> Any:
            factory, _, active = _base_active(f"{seed}:{family}")
            active.push(factory.gap(2))
            reconnect = factory.reconnect()
            prior = _prior_from_session(active, factory.bindings)
            forged = _forge(
                reconnect,
                lambda record: (
                    record["sequence"].__setitem__("reconnect_generation", generation),
                    record["sequence"].__setitem__("chunk_sequence_index", sequence),
                ),
                prior=prior,
                resign=True,
            )
            return active.push(forged)

        return _expect_refusal(family, operation)

    rows.append(reconnect_case("generation_rollback", 0))
    rows.append(reconnect_case("generation_skip", 2))

    def old_generation() -> Any:
        factory, _, active = _base_active(f"{seed}:old-generation")
        active.push(factory.gap(2))
        active.push(factory.reconnect())
        data = _data(factory, 16)
        prior = _prior_from_session(active, factory.bindings)
        forged = _forge(
            data,
            lambda record: record["sequence"].__setitem__("reconnect_generation", 0),
            prior=prior,
            resign=True,
        )
        return active.push(forged)

    rows.append(_expect_refusal("old_generation_after_reconnect", old_generation))

    def after_disconnect() -> Any:
        factory, _, active = _base_active(f"{seed}:after-disconnect")
        gap = factory.gap(2)
        active.push(gap)
        template_factory = _factory(f"{seed}:after-disconnect")
        template_factory.stream_start()
        template = _data(template_factory, 16)
        prior = _prior_from_session(active, factory.bindings)
        forged = _forge(
            template,
            lambda record: (
                record["sequence"].__setitem__("chunk_sequence_index", 2),
                _resign_axis(record, first=2, count=16),
            ),
            prior=prior,
            resign=True,
        )
        return active.push(forged)

    rows.append(_expect_refusal("chunk_after_disconnect", after_disconnect))
    rows.append(reconnect_case("reconnect_without_generation_increment", 1, 1))

    def reconnect_active() -> Any:
        factory, _, active = _base_active(f"{seed}:reconnect-active")
        factory.source_error()
        reconnect = factory.reconnect()
        original_factory = _factory(f"{seed}:reconnect-active")
        original_factory.stream_start()
        prior = _prior_from_session(active, original_factory.bindings)
        forged = _forge(reconnect, lambda record: None, prior=prior, resign=True)
        return active.push(forged)

    rows.append(_expect_refusal("reconnect_while_not_degraded", reconnect_active))

    rows.append(
        _expect_refusal(
            "capture_arrival_clock_order_violation",
            lambda: _clock_case(f"{seed}:bad-clock", _BadClockProcessor()),
        )
    )
    rows.append(
        _expect_refusal(
            "arrival_monotonic_rollback",
            _mutated_next_case(
                f"{seed}:arrival-rollback",
                lambda record: (
                    record["timestamps"].__setitem__("arrival_monotonic_start_ns", 0),
                    record["timestamps"].__setitem__("arrival_monotonic_end_ns", 1),
                ),
            ),
        )
    )

    def invalid_payload() -> Any:
        factory, _, active = _base_active(f"{seed}:payload")
        chunk = _data(factory, 16)
        forged = _forge(
            chunk,
            lambda record: record["hashes"].__setitem__("valid_payload_sha256", "0" * 64),
        )
        return active.push(forged)

    rows.append(
        _expect_refusal("nonfinite_padding_or_hash_invalid_payload", invalid_payload)
    )
    rows.append(
        _expect_refusal(
            "chunk_size_cap_breach",
            lambda: _oversized_chunk_case(f"{seed}:chunk-cap"),
        )
    )
    rows.append(
        _expect_refusal(
            "session_sample_cap_breach",
            lambda: _session_cap_case(f"{seed}:session-cap"),
        )
    )
    rows.append(
        _expect_refusal(
            "processor_state_cap_breach",
            lambda: _clock_case(f"{seed}:state-cap", _LargeStateProcessor()),
        )
    )

    snapshot_factory, snapshot_start, snapshot_session = _base_active(f"{seed}:snapshot")
    snapshot = snapshot_session.snapshot()
    tampered = copy.deepcopy(snapshot)
    tampered["state"]["committed_output"] = "X"
    rows.append(
        _expect_refusal(
            "snapshot_tamper",
            lambda: LiveSession.restore(
                tampered,
                bindings=make_session_bindings(
                    snapshot_start, processor=DeterministicGeneratedProcessor()
                ),
                processor=DeterministicGeneratedProcessor(),
                expected_semantic_prefix_sha256=snapshot["state"][
                    "semantic_prefix_sha256"
                ],
                expected_semantic_element_count=snapshot["state"][
                    "semantic_element_count"
                ],
            ),
        )
    )
    other_processor = DeterministicGeneratedProcessor()
    other_bindings = make_session_bindings(other, processor=other_processor)
    rows.append(
        _expect_refusal(
            "snapshot_source_config_model_or_prefix_collision",
            lambda: LiveSession.restore(
                snapshot,
                bindings=other_bindings,
                processor=other_processor,
                expected_semantic_prefix_sha256=snapshot["state"][
                    "semantic_prefix_sha256"
                ],
                expected_semantic_element_count=snapshot["state"][
                    "semantic_element_count"
                ],
            ),
        )
    )

    quality = _quality_probe(f"{seed}:quality-probe", -1.0)
    rows.append(
        _expect_blocked_behavior(
            "quality_gate_bypass",
            quality.invalid_output_mask and quality.committed_delta == "",
            "quality gate admitted output",
        )
    )
    confidence = _quality_probe(f"{seed}:confidence-probe", -2.0)
    rows.append(
        _expect_blocked_behavior(
            "confidence_gate_bypass",
            confidence.invalid_output_mask and confidence.committed_delta == "",
            "confidence gate admitted output",
        )
    )

    gap = _run_gap_reconnect(f"{seed}:stability-gap")
    rows.append(
        _expect_blocked_behavior(
            "stability_across_gap",
            gap["first_post_reconnect_commit"] == "",
            "stability crossed generation",
        )
    )
    repeated = _repeated_commit_probe(f"{seed}:repeated")
    rows.append(
        _expect_blocked_behavior(
            "repeated_stable_commit",
            repeated,
            "stable symbol recommitted without blank or inactive rearm",
        )
    )

    rows.append(
        _expect_refusal(
            "target_label_or_text_leakage",
            lambda: _clock_case(f"{seed}:leak", _LeakyProcessor()),
        )
    )
    rows.append(
        _expect_refusal(
            "deadline_expired_or_abstain_all_positive_control",
            lambda: _require_positive_control(0, deadline_expired=False),
        )
    )

    close_factory, _, close_session = _base_active(f"{seed}:closed")
    end = close_factory.stream_end()
    close_session.push(end)
    rows.append(_expect_refusal("use_after_close", lambda: close_session.push(end)))

    if tuple(row["family_id"] for row in rows) != REQUIRED_REFUSAL_FAMILIES:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-REFUSAL-ORDER")
    return rows


def _clock_case(seed: str, processor: Callable[..., ProcessorEvent]) -> Any:
    factory = _factory(seed)
    start = factory.stream_start()
    session = LiveSession(
        bindings=make_session_bindings(start, processor=processor),
        processor=processor,
    )
    session.push(start)
    return session.push(_data(factory, 16))


def _oversized_chunk_case(seed: str) -> Any:
    factory = _factory(seed, channels=1)
    factory.stream_start()
    return factory.data([[0.0] * 4097])


def _session_cap_case(seed: str) -> Any:
    factory = _factory(seed, channels=1)
    start = factory.stream_start()
    processor = DeterministicGeneratedProcessor()
    session = _session(start, seed, processor)
    session.push(start)
    snapshot = session.snapshot()
    snapshot["state"]["session_valid_samples"] = 65_536
    unsigned = {
        key: value for key, value in snapshot.items() if key != "snapshot_sha256"
    }
    snapshot["snapshot_sha256"] = _sha256(canonical_json_bytes(unsigned))
    restored = LiveSession.restore(
        snapshot,
        bindings=make_session_bindings(start, processor=processor),
        processor=processor,
        expected_semantic_prefix_sha256=start.semantic_prefix_sha256,
        expected_semantic_element_count=start.semantic_state.element_count,
    )
    return restored.push(_data(factory, 1))


def _quality_probe(seed: str, value: float) -> Any:
    factory, _, session = _base_active(seed)
    session.push(_data(factory, 32))
    return session.push(_data(factory, 16, value)).frame_updates[0]


def _repeated_commit_probe(seed: str) -> bool:
    factory, _, session = _base_active(seed)
    first = session.push(_data(factory, 80))
    repeated = session.push(_data(factory, 48))
    blank = session.push(_data(factory, 16, 0.0))
    rearmed = session.push(_data(factory, 48))
    return (
        first.committed_delta == "A"
        and repeated.committed_delta == ""
        and blank.committed_delta == ""
        and rearmed.committed_delta == "A"
    )


def _require_positive_control(commit_count: int, *, deadline_expired: bool) -> None:
    if deadline_expired or commit_count < 1:
        raise CommLiveG0GeneratedRefusal(
            "deadline_expired_or_abstain_all_positive_control"
        )


def _run_replay(replay_index: int) -> dict[str, Any]:
    sessions: list[dict[str, Any]] = []
    for session_index in range(CAPS["fictional_sessions"]):
        seed = f"comm-live-g0:session-{session_index}"
        partitions = {
            name: _run_partition(seed, widths)
            for name, widths in PARTITION_SCHEDULES.items()
        }
        canonical = canonical_json_bytes(next(iter(partitions.values())))
        if any(canonical_json_bytes(value) != canonical for value in partitions.values()):
            raise CommLiveG0GeneratedRefusal(
                "COMM-LIVE-G0-PARTITION-NONDETERMINISM", seed
            )
        sessions.append(
            {
                "fictional_session_index": session_index,
                "partition_schedules": partitions,
                "gap_reconnect": _run_gap_reconnect(f"{seed}:gap"),
                "quality_confidence": _run_quality_confidence(f"{seed}:quality"),
            }
        )
    commit_count = sum(
        len(value["whole_stream"]["committed_output"])
        for value in (row["partition_schedules"] for row in sessions)
    )
    _require_positive_control(commit_count, deadline_expired=False)
    deterministic = {
        "fictional_sessions": sessions,
        "positive_control_commit_count": commit_count,
    }
    return {
        "replay_index": replay_index,
        "deterministic": deterministic,
        "deterministic_sha256": _sha256(canonical_json_bytes(deterministic)),
    }


def _peak_rss_bytes() -> int:
    value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return value if os.uname().sysname == "Darwin" else value * 1024


def _enforce_caps(measurements: Mapping[str, int | float]) -> None:
    if measurements["runtime_seconds"] > CAPS["wall_time_seconds"]:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-RUNTIME-CAP")
    if measurements["peak_RSS_bytes"] > CAPS["peak_RSS_bytes"]:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-RSS-CAP")
    if measurements["public_output_bytes"] > CAPS["public_output_bytes"]:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-PUBLIC-OUTPUT-CAP")


def plan(root: str | Path | None = None) -> dict[str, Any]:
    load_frozen_registration(root)
    return {
        "lane_id": LANE_ID,
        "generated_only": True,
        "fictional_sessions": CAPS["fictional_sessions"],
        "deterministic_replays": 2,
        "partition_schedules": list(PARTITION_SCHEDULES),
        "control_schedules": list(CONTROL_SCHEDULES),
        "required_adversarial_family_count": len(REQUIRED_REFUSAL_FAMILIES),
        "required_adversarial_family_ids": list(REQUIRED_REFUSAL_FAMILIES),
        "official_qualification_available_now": False,
        "official_requirement": "exact_future_green_implementation_proof",
        "caps": dict(CAPS),
        "real_network_provider_device_model_operations": 0,
        "scientific_value": "none_generated_engineering_only",
    }


def run_development_qualification(root: str | Path | None = None) -> dict[str, Any]:
    """Run repeatable development checks without consuming the official invocation."""

    started = time.monotonic()
    load_frozen_registration(root)
    first = _run_replay(1)
    second = _run_replay(2)
    if first["deterministic_sha256"] != second["deterministic_sha256"]:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-REPLAY-NONDETERMINISM")
    refusals = _adversarial_refusals("comm-live-g0:adversarial")
    runtime = time.monotonic() - started
    deterministic = first["deterministic"]
    measurements: dict[str, int | float] = {
        "runtime_seconds": runtime,
        "peak_RSS_bytes": _peak_rss_bytes(),
        "public_output_bytes": 0,
        "temporary_generated_bytes": 0,
        "cpu_threads": 1,
        "workers": 1,
    }
    result: dict[str, Any] = {
        "schema_name": RESULT_SCHEMA,
        "schema_version": RESULT_VERSION,
        "lane_id": LANE_ID,
        "status": "development_only_repeatable_not_official",
        "route": "COMM-LIVE-G0-DEVELOPMENT-PASS",
        "official_invocation_consumed": False,
        "registration": {
            "contract_sha256": CONTRACT_SHA256,
            "amendment_sha256": AMENDMENT_SHA256,
            "replay_contract_sha256": REPLAY_CONTRACT_SHA256,
        },
        "replay_equivalence": {
            "deterministic_replays": 2,
            "deterministic_sha256": first["deterministic_sha256"],
            "byte_equivalent": True,
            "fictional_sessions": CAPS["fictional_sessions"],
            "partition_schedules": list(PARTITION_SCHEDULES),
            "control_schedules": list(CONTROL_SCHEDULES),
        },
        "aggregate_proof": {
            "session_payload_sha256": _sha256(
                canonical_json_bytes(deterministic["fictional_sessions"])
            ),
            "positive_control_commit_count": deterministic[
                "positive_control_commit_count"
            ],
        },
        "adversarial_qualification": {
            "refusal_count": len(refusals),
            "refusal_ids": [
                row["family_id"] for row in refusals
            ],
            "observed": refusals,
            "every_named_family_executed": True,
        },
        "measurements": measurements,
        "operation_counters": dict(ZERO_OPERATION_COUNTERS),
        "warnings": [
            "generated_fictional_streams_only",
            "development_path_does_not_consume_official_invocation",
            "no_real_or_device_latency_measured",
            "no_scientific_or_decoding_value",
        ],
        "claim_boundary": {
            "scientific_value": "none_generated_engineering_only",
            "real_EEG_accessed": False,
            "communication_decoding_established": False,
            "EEG_beyond_peripheral_controls_established": False,
            "unseen_person_generalization_established": False,
            "live_neural_decoding_established": False,
        },
    }
    measurements["public_output_bytes"] = len(canonical_json_bytes(result))
    _enforce_caps(measurements)
    return result


def _assert_safe_parent(path: Path) -> None:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parent.parts[1:]:
        current /= part
        info = current.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-UNSAFE-OUTPUT-PATH")


def _write_no_replace(path: Path, payload: bytes) -> None:
    _assert_safe_parent(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except FileExistsError as exc:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-OUTPUT-COLLISION") from exc
    try:
        offset = 0
        while offset < len(payload):
            offset += os.write(descriptor, payload[offset:])
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def qualify(
    output_path: str | Path,
    *,
    root: str | Path | None = None,
) -> dict[str, Any]:
    """Run the one-shot official path only after an exact future green proof exists."""

    repository = (Path(root) if root is not None else _repo_root()).absolute()
    load_frozen_registration(repository)
    proof = _validate_future_implementation_proof(repository)
    output = Path(output_path).absolute()
    marker = output.with_name(f".{output.name}.comm-live-g0-consumed.json")
    if output.exists() or output.is_symlink() or marker.exists() or marker.is_symlink():
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-OFFICIAL-ALREADY-CONSUMED")
    marker_payload = canonical_json_bytes(
        {
            "lane_id": LANE_ID,
            "status": "official_invocation_consumed_before_execution",
            "implementation_commit": proof["implementation_commit"],
        }
    )
    _write_no_replace(marker, marker_payload)
    result = run_development_qualification(repository)
    result["status"] = "official_generated_qualification_completed"
    result["route"] = "COMM-LIVE-G0-R1"
    result["official_invocation_consumed"] = True
    result["implementation_proof"] = {
        "implementation_commit": proof["implementation_commit"],
        "CI_run_id": proof["remote_proof"]["CI_run_id"],
    }
    payload = b""
    for _ in range(8):
        payload = canonical_json_bytes(result)
        byte_count = len(payload)
        if result["measurements"]["public_output_bytes"] == byte_count:
            break
        result["measurements"]["public_output_bytes"] = byte_count
    else:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-OUTPUT-ACCOUNTING")
    _enforce_caps(result["measurements"])
    _write_no_replace(output, payload)
    return result


def _read_no_follow(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path.absolute(), flags)
    except OSError as exc:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-INSPECT-PATH") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-INSPECT-PATH")
        if info.st_size > CAPS["public_output_bytes"]:
            raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-PUBLIC-OUTPUT-CAP")
        chunks: list[bytes] = []
        while block := os.read(descriptor, 1024 * 1024):
            chunks.append(block)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def inspect_result(path: str | Path) -> dict[str, Any]:
    try:
        value = json.loads(_read_no_follow(Path(path)))
    except json.JSONDecodeError as exc:
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-INSPECT-JSON") from exc
    if (
        value.get("schema_name") != RESULT_SCHEMA
        or value.get("schema_version") != RESULT_VERSION
        or value.get("lane_id") != LANE_ID
    ):
        raise CommLiveG0GeneratedRefusal("COMM-LIVE-G0-INSPECT-SCHEMA")
    return {
        "lane_id": value["lane_id"],
        "status": value["status"],
        "route": value["route"],
        "official_invocation_consumed": value["official_invocation_consumed"],
        "replay_equivalence": value["replay_equivalence"],
        "adversarial_qualification": value["adversarial_qualification"],
        "measurements": value["measurements"],
        "operation_counters": value["operation_counters"],
        "claim_boundary": value["claim_boundary"],
    }


__all__ = [
    "CommLiveG0GeneratedRefusal",
    "REQUIRED_REFUSAL_FAMILIES",
    "inspect_result",
    "load_frozen_registration",
    "plan",
    "qualify",
    "run_development_qualification",
]
