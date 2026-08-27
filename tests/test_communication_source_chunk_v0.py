from __future__ import annotations

import copy
import math
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.streaming.source_chunk import (  # noqa: E402
    GeneratedSourceChunkFactory,
    SourceBindings,
    SourceChunkRefusal,
    compute_chunk_envelope_sha256,
    compute_valid_payload_sha256,
    validate_source_chunk,
)


class CommunicationSourceChunkV0Tests(unittest.TestCase):
    def assert_refusal(self, refusal_id: str, callback) -> None:
        with self.assertRaises(SourceChunkRefusal) as caught:
            callback()
        self.assertEqual(caught.exception.refusal_id, refusal_id)

    def golden_stream(self):
        factory = GeneratedSourceChunkFactory.fictional(
            seed="golden-v0",
            dtype="float32",
            channel_names=("C3", "C4"),
            nominal_sampling_rate_hz=128.0,
        )
        return (
            factory,
            factory.stream_start(),
            factory.data([[1.0, 2.0], [3.0, 4.0]], capacity=3),
            factory.stream_end(),
        )

    def test_golden_replay_and_exact_hashes(self) -> None:
        factory, start, data, end = self.golden_stream()
        self.assertEqual(
            factory.bindings.sha256,
            "ef3ec3a90952c2ca7c674e1a16a9b57c2d12d8efab7807ffeeb2a1f2b15b8cdf",
        )
        expected = {
            "stream_start": (
                "a59349fbbb779113f9ce7ef4de3a134ba75585586d5d38f787973c946f21416f",
                "8e79d311e628eb3d7651d9a17e8e3b0b7ef679e9278b5882543276e957aab008",
                "cacfa08ddb10f6078d2e65dab5a48be3fa78af90b29f26c637f4e869bb1d2939",
            ),
            "data": (
                "092fa3abd724ea87c1a08b5e63fa48a93db3d3685d05e822f1677184c2126e29",
                "eda7e7f468121f25a7abd4778493025feacabc639a394b9e7df150cb593d987c",
                "2116c63bf5a17a557c7a693eaa42722c50dbb3d7779b2114a5d4598d59db95a8",
            ),
            "stream_end": (
                "a59349fbbb779113f9ce7ef4de3a134ba75585586d5d38f787973c946f21416f",
                "a50e4ba5339a01be98d02ff2a4b5bcd09e4b5bc77b71109a0158c32a0dd0f9b1",
                "edc33d384d54a4e0ef7961425082e5d9053e854a9008d74724e96204c1a6ec0e",
            ),
        }
        prior = None
        for chunk in (start, data, end):
            hashes = chunk["hashes"]
            self.assertEqual(
                (
                    hashes["valid_payload_sha256"],
                    hashes["semantic_prefix_sha256"],
                    hashes["chunk_envelope_sha256"],
                ),
                expected[chunk.record_kind],
            )
            replay = validate_source_chunk(
                chunk.to_dict(), prior=prior, expected_bindings=factory.bindings
            )
            self.assertEqual(replay.canonical_bytes, chunk.canonical_bytes)
            prior = replay.semantic_state

    def test_semantic_digest_is_partition_independent(self) -> None:
        samples = [float(value) for value in range(1, 9)]

        def run(widths: tuple[int, ...]):
            factory = GeneratedSourceChunkFactory.fictional(
                seed="partition-v0", channel_names=("A", "B"), dtype="float64"
            )
            factory.stream_start()
            offset = 0
            for width in widths:
                row = samples[offset : offset + width]
                factory.data([row, [value + 100.0 for value in row]])
                offset += width
            self.assertEqual(offset, len(samples))
            end = factory.stream_end()
            return end.semantic_prefix_sha256, end.semantic_state.element_count

        expected = run((8,))
        self.assertEqual(run((1, 1, 1, 1, 1, 1, 1, 1)), expected)
        self.assertEqual(run((1, 3, 2, 2)), expected)
        self.assertEqual(run((2, 2, 2, 2)), expected)

    def test_envelope_hash_omits_only_its_own_field(self) -> None:
        _, _, data, _ = self.golden_stream()
        original = data.to_dict()
        expected = compute_chunk_envelope_sha256(original)
        self.assertEqual(expected, original["hashes"]["chunk_envelope_sha256"])
        changed_self = copy.deepcopy(original)
        changed_self["hashes"]["chunk_envelope_sha256"] = "f" * 64
        self.assertEqual(compute_chunk_envelope_sha256(changed_self), expected)
        changed_other_hash = copy.deepcopy(original)
        changed_other_hash["hashes"]["valid_payload_sha256"] = "e" * 64
        self.assertNotEqual(compute_chunk_envelope_sha256(changed_other_hash), expected)
        self.assert_refusal(
            "semantic_stream_hash_mismatch",
            lambda: validate_source_chunk(
                changed_self,
                prior=self.golden_stream()[1].semantic_state,
                expected_bindings=data.bindings,
            ),
        )

    def test_valid_payload_hash_is_sample_major_and_ignores_padding(self) -> None:
        _, _, data, _ = self.golden_stream()
        payload = data.to_dict()["payload"]
        expected = compute_valid_payload_sha256(payload)
        payload["values"][0][2] = 0.0
        payload["values"][1][2] = 0.0
        self.assertEqual(compute_valid_payload_sha256(payload), expected)
        channel_major = copy.deepcopy(payload)
        channel_major["values"] = [payload["values"][1], payload["values"][0]]
        self.assertNotEqual(compute_valid_payload_sha256(channel_major), expected)

    def test_representation_is_deeply_immutable_and_roundtrippable(self) -> None:
        _, _, data, _ = self.golden_stream()
        with self.assertRaises(TypeError):
            data.record["record_kind"] = "gap"
        with self.assertRaises(TypeError):
            data.record["payload"]["values"][0][0] = 99.0
        mutable = data.to_dict()
        mutable["payload"]["values"][0][0] = 99.0
        self.assertEqual(data["payload"]["values"][0][0], 1.0)

    def test_unknown_and_recursive_forbidden_keys_fail_closed(self) -> None:
        _, start, _, _ = self.golden_stream()
        unknown = start.to_dict()
        unknown["mystery"] = 1
        self.assert_refusal(
            "source_chunk_schema_invalid", lambda: validate_source_chunk(unknown)
        )
        leaked = start.to_dict()
        leaked["identity"]["target_text"] = "do not admit"
        self.assert_refusal(
            "forbidden_target_or_text_key", lambda: validate_source_chunk(leaked)
        )
        nested_leak = start.to_dict()
        nested_leak["warnings"] = [{"reference_text": "still forbidden"}]
        self.assert_refusal(
            "forbidden_target_or_text_key", lambda: validate_source_chunk(nested_leak)
        )

    def test_float32_requires_exact_cast_and_finite_values(self) -> None:
        _, start, data, _ = self.golden_stream()
        inexact = data.to_dict()
        inexact["payload"]["values"][0][0] = 0.1
        self.assert_refusal(
            "payload_dtype_not_allowed",
            lambda: validate_source_chunk(inexact, prior=start.semantic_state),
        )
        nonfinite = data.to_dict()
        nonfinite["payload"]["values"][0][0] = math.inf
        self.assert_refusal(
            "payload_contains_nonfinite_values",
            lambda: validate_source_chunk(nonfinite, prior=start.semantic_state),
        )
        source_nonfinite = data.to_dict()
        source_nonfinite["timestamps"]["source_timestamps_sec"][0] = math.nan
        self.assert_refusal(
            "source_timestamp_nonfinite",
            lambda: validate_source_chunk(source_nonfinite, prior=start.semantic_state),
        )

    def test_padding_shape_and_sample_axis_are_strict(self) -> None:
        _, start, data, _ = self.golden_stream()
        negative_zero = data.to_dict()
        negative_zero["payload"]["values"][0][2] = -0.0
        self.assert_refusal(
            "padding_mask_or_value_invalid",
            lambda: validate_source_chunk(negative_zero, prior=start.semantic_state),
        )
        bad_shape = data.to_dict()
        bad_shape["payload"]["shape"] = [2, 2]
        self.assert_refusal(
            "payload_shape_or_layout_invalid",
            lambda: validate_source_chunk(bad_shape, prior=start.semantic_state),
        )
        gap = data.to_dict()
        gap["sample_axis"]["source_sample_indices"] = [0, 2]
        self.assert_refusal(
            "sample_index_gap_unrepresented",
            lambda: validate_source_chunk(gap, prior=start.semantic_state),
        )

    def test_payload_semantic_and_envelope_hash_tampering_refuses(self) -> None:
        _, start, data, _ = self.golden_stream()
        payload_hash = data.to_dict()
        payload_hash["hashes"]["valid_payload_sha256"] = "0" * 64
        self.assert_refusal(
            "semantic_stream_hash_mismatch",
            lambda: validate_source_chunk(payload_hash, prior=start.semantic_state),
        )
        semantic_hash = data.to_dict()
        semantic_hash["hashes"]["semantic_prefix_sha256"] = "0" * 64
        self.assert_refusal(
            "semantic_stream_hash_mismatch",
            lambda: validate_source_chunk(semantic_hash, prior=start.semantic_state),
        )
        envelope_hash = data.to_dict()
        envelope_hash["hashes"]["chunk_envelope_sha256"] = "0" * 64
        self.assert_refusal(
            "semantic_stream_hash_mismatch",
            lambda: validate_source_chunk(envelope_hash, prior=start.semantic_state),
        )

    def test_timestamp_packet_and_binding_failures_are_precise(self) -> None:
        _, start, data, _ = self.golden_stream()
        timestamp = data.to_dict()
        timestamp["timestamps"]["source_timestamps_sec"][1] = timestamp["timestamps"][
            "source_timestamps_sec"
        ][0]
        self.assert_refusal(
            "sample_order_regression_unrepresented",
            lambda: validate_source_chunk(timestamp, prior=start.semantic_state),
        )
        counters = data.to_dict()
        counters["packet_accounting"]["raw_counter_values"] = [0]
        self.assert_refusal(
            "packet_loss_measurement_unavailable_for_required_gate",
            lambda: validate_source_chunk(counters, prior=start.semantic_state),
        )
        other = GeneratedSourceChunkFactory.fictional(seed="other-binding")
        other_start = other.stream_start()
        self.assert_refusal(
            "state_source_or_prefix_collision",
            lambda: validate_source_chunk(
                data.to_dict(), prior=other_start.semantic_state, expected_bindings=data.bindings
            ),
        )

    def test_caps_are_enforced(self) -> None:
        self.assert_refusal(
            "resource_cap_exceeded",
            lambda: SourceBindings.generated(
                channel_names=tuple(f"C{index}" for index in range(33))
            ),
        )
        factory = GeneratedSourceChunkFactory.fictional(channel_names=("C",))
        factory.stream_start()
        self.assert_refusal(
            "resource_cap_exceeded",
            lambda: factory.data([[0.0] * 4097]),
        )

    def test_all_control_records_validate_in_one_deterministic_replay(self) -> None:
        factory = GeneratedSourceChunkFactory.fictional(seed="controls", dtype="float64")
        chunks = [factory.stream_start()]
        chunks.append(factory.data([[1.0], [2.0]]))
        chunks.append(factory.gap(3))
        chunks.append(factory.reconnect())
        chunks.append(factory.data([[3.0], [4.0]]))
        chunks.append(factory.source_error(clock_reset=True))
        chunks.append(factory.reconnect(clock_reset=True))
        chunks.append(factory.stream_end())
        self.assertEqual(
            [chunk.record_kind for chunk in chunks],
            [
                "stream_start",
                "data",
                "gap",
                "reconnect",
                "data",
                "source_error",
                "reconnect",
                "stream_end",
            ],
        )
        prior = None
        for chunk in chunks:
            replay = validate_source_chunk(
                chunk.to_dict(), prior=prior, expected_bindings=factory.bindings
            )
            prior = replay.semantic_state
        self.assertEqual(prior, chunks[-1].semantic_state)
        self.assertEqual(chunks[2]["packet_accounting"]["gap_before_samples"], 3)
        self.assertEqual(chunks[3]["sequence"]["reconnect_generation"], 1)
        self.assertEqual(chunks[6]["sequence"]["reconnect_generation"], 2)

    def test_factory_replay_is_deterministic(self) -> None:
        def run():
            factory = GeneratedSourceChunkFactory.fictional(seed="deterministic-v0")
            chunks = [
                factory.stream_start(),
                factory.data([[1.0, 2.0], [3.0, 4.0]], capacity=4),
                factory.gap(2),
                factory.reconnect(),
                factory.stream_end(),
            ]
            return [chunk.canonical_bytes for chunk in chunks]

        self.assertEqual(run(), run())


if __name__ == "__main__":
    unittest.main()
