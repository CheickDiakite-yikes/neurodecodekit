import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CausalMockNeuroTokenStreamTests(unittest.TestCase):
    def test_chunk_schedules_match_offline_tokens_and_timestamps_exactly(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken import project_mock_temporal_embeddings
        from neurodecodekit.cache.neurotoken_stream import CausalMockNeuroTokenProducer

        signal = (
            np.arange(2 * 24, dtype="float32").reshape(2, 24) / 17.0
        )
        source_start = 1.25
        config = {
            "source_sampling_rate_hz": 100.0,
            "embedding_dim": 7,
            "kernel_size": 5,
            "stride": 2,
            "seed": 41,
            "token_dtype": "float32",
        }
        offline = project_mock_temporal_embeddings(
            signals=signal[None, :, :],
            input_lengths=np.asarray([24], dtype="int32"),
            source_start_sec=np.asarray([source_start]),
            max_tokens_per_item=64,
            max_output_mb=1,
            **config,
        )
        count = int(offline["token_lengths"][0])
        schedules = (
            [1] * 24,
            [5] + [2] * 9 + [1],
            [4, 1, 7, 3, 8, 1],
            [24],
        )
        producer = CausalMockNeuroTokenProducer(n_channels=2, **config)
        schedule_reference = None

        for chunks in schedules:
            with self.subTest(chunks=chunks):
                stream = producer.new_stream(
                    source_start_sec=source_start,
                    max_chunk_samples=24,
                    max_total_samples=24,
                    max_total_tokens=64,
                )
                offset = 0
                batches = []
                for size in chunks:
                    batches.append(stream.push(signal[:, offset : offset + size]))
                    offset += size
                flush = stream.flush()
                tokens = np.concatenate([batch.tokens for batch in batches], axis=0)
                starts = np.concatenate(
                    [batch.token_start_sec for batch in batches], axis=0
                )
                ends = np.concatenate(
                    [batch.token_end_sec for batch in batches], axis=0
                )
                delays = np.concatenate(
                    [batch.schedule_delay_samples for batch in batches], axis=0
                )

                self.assertEqual(offset, 24)
                self.assertEqual(len(tokens), count)
                np.testing.assert_allclose(
                    tokens, offline["tokens"][0, :count], rtol=0, atol=1e-6
                )
                if schedule_reference is None:
                    schedule_reference = tokens
                else:
                    np.testing.assert_array_equal(tokens, schedule_reference)
                np.testing.assert_array_equal(
                    starts, offline["token_start_sec"][0, :count]
                )
                np.testing.assert_array_equal(ends, offline["token_end_sec"][0, :count])
                self.assertTrue((delays >= 0).all())
                self.assertEqual(flush.unframed_tail_samples, 1)
                self.assertEqual(flush.mutable_state_bytes_after_flush, 0)
                self.assertTrue(stream.closed)

    def test_state_is_bounded_and_flush_drops_only_unframed_tail(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken_stream import CausalMockNeuroTokenProducer

        producer = CausalMockNeuroTokenProducer(
            n_channels=3,
            source_sampling_rate_hz=50.0,
            embedding_dim=5,
            kernel_size=4,
            stride=3,
            seed=5,
        )
        stream = producer.new_stream(
            max_chunk_samples=21,
            max_total_samples=21,
            max_total_tokens=16,
        )
        signal = np.arange(3 * 21, dtype="float32").reshape(3, 21)
        offset = 0
        for size in (2, 5, 14):
            stream.push(signal[:, offset : offset + size])
            offset += size
            self.assertLess(stream.buffered_samples, producer.kernel_size)
            self.assertLessEqual(
                stream.mutable_state_bytes, producer.mutable_state_bound_bytes
            )

        flush = stream.flush()
        self.assertEqual(stream.emitted_tokens, 6)
        self.assertEqual(flush.unframed_tail_samples, 2)
        self.assertLessEqual(
            stream.max_mutable_state_bytes, producer.mutable_state_bound_bytes
        )
        self.assertEqual(producer.producer_right_context_samples, 0)
        self.assertAlmostEqual(producer.minimum_frame_availability_sec, 0.08)

    def test_rejects_invalid_chunks_caps_and_use_after_flush(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken_stream import CausalMockNeuroTokenProducer

        with self.assertRaisesRegex(ValueError, "stride"):
            CausalMockNeuroTokenProducer(
                n_channels=2,
                source_sampling_rate_hz=100,
                kernel_size=4,
                stride=5,
            )
        producer = CausalMockNeuroTokenProducer(
            n_channels=2,
            source_sampling_rate_hz=100,
            kernel_size=4,
            stride=2,
        )
        stream = producer.new_stream(
            max_chunk_samples=4,
            max_total_samples=6,
            max_total_tokens=2,
        )
        with self.assertRaisesRegex(ValueError, "at least one"):
            stream.push(np.zeros((2, 0), dtype="float32"))
        with self.assertRaisesRegex(ValueError, "exactly 2 channels"):
            stream.push(np.zeros((3, 2), dtype="float32"))
        with self.assertRaisesRegex(ValueError, "finite floating"):
            stream.push(np.zeros((2, 2), dtype="int16"))
        stream.push(np.zeros((2, 4), dtype="float32"))
        with self.assertRaisesRegex(ValueError, "exceeding cap"):
            stream.push(np.zeros((2, 3), dtype="float32"))
        stream.flush()
        with self.assertRaisesRegex(RuntimeError, "already closed"):
            stream.push(np.zeros((2, 1), dtype="float32"))
        with self.assertRaisesRegex(RuntimeError, "already closed"):
            stream.flush()


if __name__ == "__main__":
    unittest.main()
