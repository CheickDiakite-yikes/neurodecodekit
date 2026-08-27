from __future__ import annotations

import copy
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.streaming.live_session import (  # noqa: E402
    LiveSession,
    LiveSessionRefusal,
    ProcessorEvent,
    make_session_bindings,
)
from neurodecodekit.streaming.source_chunk import (  # noqa: E402
    GeneratedSourceChunkFactory,
    SourceChunk,
    advance_semantic_prefix,
    canonical_json_bytes,
    compute_chunk_envelope_sha256,
    compute_valid_payload_sha256,
    validate_source_chunk,
)


class DeterministicProcessor:
    def __init__(self) -> None:
        self.processor_config_sha256 = self._digest("deterministic-processor-v0")
        self.model_sha256 = self._digest("fictional-no-model-v0")

    @staticmethod
    def _digest(value: str) -> str:
        import hashlib

        return hashlib.sha256(value.encode("ascii")).hexdigest()

    def __call__(self, frame, prior_state):
        first_value = frame.sample_major_values[-1][0]
        state = {"updates": int(prior_state.get("updates", 0)) + 1}
        arrival = frame.arrival_monotonic_ns[-1]
        if first_value == 0:
            symbol, active, quality, confidence = "", True, True, 0.95
        elif first_value == -1:
            symbol, active, quality, confidence = "A", True, False, 0.95
        elif first_value == -2:
            symbol, active, quality, confidence = "A", True, True, 0.2
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


class LeakyProcessor(DeterministicProcessor):
    def __call__(self, frame, prior_state):
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


class ReentrantProcessor(DeterministicProcessor):
    session = None
    nested_chunk = None

    def __call__(self, frame, prior_state):
        assert self.session is not None
        assert self.nested_chunk is not None
        self.session.push(self.nested_chunk)
        return super().__call__(frame, prior_state)


class WrongProcessor(DeterministicProcessor):
    def __init__(self) -> None:
        super().__init__()
        self.model_sha256 = self._digest("wrong-model")


class CommunicationLiveSessionTests(unittest.TestCase):
    def factory(self) -> GeneratedSourceChunkFactory:
        return GeneratedSourceChunkFactory.fictional(
            seed="live-session-tests",
            dtype="float64",
            channel_names=("SYN00", "SYN01", "SYN02", "SYN03"),
            channel_types=("synthetic",) * 4,
            channel_units=("arbitrary_unit",) * 4,
            nominal_sampling_rate_hz=256.0,
            modality="synthetic_eeg_interface",
        )

    def session(self, start: SourceChunk, processor=None) -> LiveSession:
        selected_processor = processor or DeterministicProcessor()
        return LiveSession(
            bindings=make_session_bindings(start, processor=selected_processor),
            processor=selected_processor,
        )

    @staticmethod
    def data(factory: GeneratedSourceChunkFactory, count: int, value: float = 1.0) -> SourceChunk:
        return factory.data([[value] * count for _ in range(4)])

    @staticmethod
    def resign(record, *, prior, bindings) -> SourceChunk:
        record["hashes"]["valid_payload_sha256"] = compute_valid_payload_sha256(
            record["payload"]
        )
        record["hashes"]["semantic_prefix_sha256"] = advance_semantic_prefix(
            record, bindings, prior
        ).digest_sha256
        record["hashes"]["chunk_envelope_sha256"] = compute_chunk_envelope_sha256(record)
        return validate_source_chunk(record, prior=prior, expected_bindings=bindings)

    def test_warmup_stable_commit_and_rearm_are_exact(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        session = self.session(start)
        session.push(start)
        update = session.push(self.data(factory, 80))
        self.assertEqual(len(update.frame_updates), 5)
        self.assertEqual(
            [frame.status for frame in update.frame_updates],
            ["abstained", "abstained", "eligible", "eligible", "committed"],
        )
        self.assertEqual(update.committed_delta, "A")
        self.assertEqual(session.push(self.data(factory, 48)).committed_delta, "")
        self.assertEqual(session.push(self.data(factory, 16, 0.0)).committed_delta, "")
        self.assertEqual(session.push(self.data(factory, 48)).committed_delta, "A")
        self.assertEqual(session.snapshot()["state"]["committed_output"], "AA")

    def test_partitioned_replay_has_identical_semantics_and_commits(self) -> None:
        schedules = ((80,), (5, 17, 13, 45), (16, 16, 16, 16, 16), (1,) * 80)
        surfaces = []
        for widths in schedules:
            factory = self.factory()
            start = factory.stream_start()
            session = self.session(start)
            session.push(start)
            commits = []
            frame_updates = []
            for width in widths:
                update = session.push(self.data(factory, width))
                commits.append(update.committed_delta)
                frame_updates.extend(frame.to_dict() for frame in update.frame_updates)
            state = session.snapshot()["state"]
            surfaces.append(
                (
                    state["semantic_prefix_sha256"],
                    state["semantic_element_count"],
                    state["event_count"],
                    state["processor_state"],
                    state["committed_output"],
                    "".join(commits),
                    frame_updates,
                )
            )
        self.assertEqual(len({repr(surface) for surface in surfaces}), 1)

    def test_snapshot_resume_matches_uninterrupted_execution(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        first = self.data(factory, 40)
        second = self.data(factory, 40)

        uninterrupted = self.session(start)
        uninterrupted.push(start)
        uninterrupted.push(first)
        uninterrupted.push(second)

        resumed = self.session(start)
        resumed.push(start)
        resumed.push(first)
        restored = LiveSession.restore(
            resumed.snapshot(),
            bindings=make_session_bindings(
                start, processor=DeterministicProcessor()
            ),
            processor=DeterministicProcessor(),
            expected_semantic_prefix_sha256=first.semantic_prefix_sha256,
            expected_semantic_element_count=first.semantic_state.element_count,
        )
        restored.push(second)
        self.assertEqual(restored.snapshot_bytes(), uninterrupted.snapshot_bytes())

    def test_gap_reconnect_discards_tail_and_prior_stability(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        session = self.session(start)
        session.push(start)
        session.push(self.data(factory, 48))
        self.assertEqual(session.snapshot()["state"]["stable_count"], 1)
        session.push(factory.gap(4))
        degraded = session.snapshot()["state"]
        self.assertEqual(degraded["status"], "degraded")
        self.assertEqual(degraded["frame_buffer"], [])
        self.assertEqual(degraded["processor_state"], {})
        self.assertEqual(degraded["stable_count"], 0)
        session.push(factory.reconnect())
        self.assertEqual(session.push(self.data(factory, 48)).committed_delta, "")

    def test_refusal_is_transactional_for_overlap_and_target_leak(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        session = self.session(start)
        session.push(start)
        first = self.data(factory, 16)
        session.push(first)
        second = self.data(factory, 16).to_dict()
        second["sample_axis"]["source_sample_indices"] = list(range(8, 24))
        second["sample_axis"]["first_source_sample_index"] = 8
        second["sample_axis"]["stop_source_sample_index_exclusive"] = 24
        source_times = [index / 256.0 for index in range(8, 24)]
        second["timestamps"]["source_timestamps_sec"] = source_times
        second["timestamps"]["corrected_timestamps_sec"] = list(source_times)
        second["packet_accounting"]["raw_counter_values"] = list(range(8, 24))
        second["packet_accounting"]["unwrapped_counter_values"] = list(range(8, 24))
        overlap = self.resign(second, prior=first.semantic_state, bindings=first.bindings)
        before = session.snapshot_bytes()
        with self.assertRaisesRegex(LiveSessionRefusal, "partial_source_sample_overlap"):
            session.push(overlap)
        self.assertEqual(session.snapshot_bytes(), before)

        leaky_factory = self.factory()
        leaky_start = leaky_factory.stream_start()
        leaky = self.session(leaky_start, processor=LeakyProcessor())
        leaky.push(leaky_start)
        leaky_before = leaky.snapshot_bytes()
        with self.assertRaisesRegex(LiveSessionRefusal, "target_label_or_text_leakage"):
            leaky.push(self.data(leaky_factory, 16))
        self.assertEqual(leaky.snapshot_bytes(), leaky_before)

    def test_quality_and_confidence_abstain_and_clear_stability(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        session = self.session(start)
        session.push(start)
        session.push(self.data(factory, 32))
        session.push(self.data(factory, 16))
        self.assertEqual(session.snapshot()["state"]["stable_count"], 1)
        quality_update = session.push(self.data(factory, 16, -1.0)).frame_updates[0]
        self.assertTrue(quality_update.invalid_output_mask)
        self.assertIn("quality_invalid", quality_update.abstention_and_anomaly_reasons)
        confidence_update = session.push(self.data(factory, 16, -2.0)).frame_updates[0]
        self.assertTrue(confidence_update.invalid_output_mask)
        self.assertIn(
            "confidence_below_threshold",
            confidence_update.abstention_and_anomaly_reasons,
        )
        self.assertEqual(session.snapshot()["state"]["stable_count"], 0)

    def test_duplicate_refusals_precede_semantic_replay_validation(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        session = self.session(start)
        session.push(start)
        first = self.data(factory, 16, 1.0)
        session.push(first)
        before = session.snapshot_bytes()
        with self.assertRaisesRegex(LiveSessionRefusal, "identical_duplicate_record"):
            session.push(first)
        self.assertEqual(session.snapshot_bytes(), before)

        alternate_factory = self.factory()
        alternate_factory.stream_start()
        alternate = self.data(alternate_factory, 16, 2.0)
        with self.assertRaisesRegex(LiveSessionRefusal, "conflicting_duplicate_payload"):
            session.push(alternate)
        self.assertEqual(session.snapshot_bytes(), before)

    def test_reentrant_processor_refuses_transactionally(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        processor = ReentrantProcessor()
        session = self.session(start, processor=processor)
        session.push(start)
        data = self.data(factory, 16)
        ReentrantProcessor.session = session
        ReentrantProcessor.nested_chunk = data
        before = session.snapshot_bytes()
        with self.assertRaisesRegex(LiveSessionRefusal, "reentrant push"):
            session.push(data)
        self.assertEqual(session.snapshot_bytes(), before)

    def test_rehashed_policy_tamper_and_processor_substitution_refuse(self) -> None:
        import hashlib

        factory = self.factory()
        start = factory.stream_start()
        processor = DeterministicProcessor()
        bindings = make_session_bindings(start, processor=processor)
        session = LiveSession(bindings=bindings, processor=processor)
        session.push(start)
        snapshot = session.snapshot()
        snapshot["policy"]["minimum_confidence"] = 0.0
        unsigned = {key: value for key, value in snapshot.items() if key != "snapshot_sha256"}
        snapshot["snapshot_sha256"] = hashlib.sha256(
            canonical_json_bytes(unsigned)
        ).hexdigest()
        with self.assertRaisesRegex(
            LiveSessionRefusal, "snapshot_source_config_model_or_prefix_collision"
        ):
            LiveSession.restore(
                snapshot,
                bindings=bindings,
                processor=processor,
                expected_semantic_prefix_sha256=start.semantic_prefix_sha256,
                expected_semantic_element_count=start.semantic_state.element_count,
            )
        with self.assertRaisesRegex(
            LiveSessionRefusal, "snapshot_source_config_model_or_prefix_collision"
        ):
            LiveSession(bindings=bindings, processor=WrongProcessor())

    def test_snapshot_tamper_raw_mapping_and_use_after_close_refuse(self) -> None:
        factory = self.factory()
        start = factory.stream_start()
        processor = DeterministicProcessor()
        bindings = make_session_bindings(start, processor=processor)
        session = LiveSession(bindings=bindings, processor=processor)
        with self.assertRaisesRegex(LiveSessionRefusal, "validated SourceChunk required"):
            session.push(start.to_dict())  # type: ignore[arg-type]
        session.push(start)
        snapshot = session.snapshot()
        tampered = copy.deepcopy(snapshot)
        tampered["state"]["committed_output"] = "X"
        with self.assertRaisesRegex(LiveSessionRefusal, "snapshot_tamper"):
            LiveSession.restore(
                tampered,
                bindings=bindings,
                processor=DeterministicProcessor(),
                expected_semantic_prefix_sha256=start.semantic_prefix_sha256,
                expected_semantic_element_count=start.semantic_state.element_count,
            )
        end = factory.stream_end()
        session.push(end)
        with self.assertRaisesRegex(LiveSessionRefusal, "use_after_close"):
            session.push(end)


if __name__ == "__main__":
    unittest.main()
