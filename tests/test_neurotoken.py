import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class NeuroTokenCacheTests(unittest.TestCase):
    def _arrays(self):
        import numpy as np

        tokens = np.zeros((2, 3, 4), dtype="float32")
        tokens[0] = np.arange(12, dtype="float32").reshape(3, 4)
        tokens[1, :2] = np.arange(8, dtype="float32").reshape(2, 4)
        return {
            "tokens": tokens,
            "token_lengths": np.asarray([3, 2], dtype="int32"),
            "token_mask": np.asarray([[True, True, True], [True, True, False]]),
            "token_start_sec": np.asarray([[0.0, 0.1, 0.2], [1.0, 1.1, -1.0]]),
            "token_end_sec": np.asarray([[0.1, 0.2, 0.3], [1.1, 1.2, -1.0]]),
            "item_ids": np.asarray(["item-a", "item-b"]),
            "split_labels": np.asarray(["train", "test"]),
            "source_row_indices": np.asarray([0, 1], dtype="int32"),
            "source_trial_indices": np.asarray([7, 8], dtype="int32"),
            "source_input_lengths": np.asarray([20, 18], dtype="int32"),
            "source_start_sec": np.asarray([0.0, 1.0]),
            "source_end_sec": np.asarray([0.3, 1.2]),
            "subject_ids": np.asarray(["SYN-1", "SYN-1"]),
            "session_ids": np.asarray(["SESSION-1", "SESSION-1"]),
            "source_channel_names": np.asarray(["C1", "C2"]),
            "source_channel_positions": np.asarray(
                [[0.1, 0.2, 0.3], [0.0, 0.0, 0.0]], dtype="float32"
            ),
            "source_channel_position_mask": np.asarray([True, False]),
        }

    def _metadata(self):
        source_sha = "a" * 64
        return {
            "kind": "unit_continuous_tokens",
            "modality": "synthetic",
            "device_type": "synthetic-array",
            "representation": {
                "name": "unit",
                "continuous": True,
                "discrete": False,
                "learned": False,
                "uses_target_labels": False,
            },
            "source": {
                "cache_sha256": source_sha,
                "split_report_sha256": "b" * 64,
            },
            "split_protocol": {
                "protocol_config_sha256": "c" * 64,
                "group_assignment_sha256": "d" * 64,
                "semantic_membership_sha256": "e" * 64,
                "source_cache_sha256": source_sha,
            },
            "source_timebase": {"sampling_rate_hz": 100.0},
            "streaming_contract": {
                "producer_causal": True,
                "producer_right_context_samples": 0,
                "minimum_producer_latency_sec": 0.16,
                "downstream_decoder_causality": "unspecified",
                "end_to_end_latency_measured": False,
            },
            "source_geometry": {"position_units": "m"},
            "official_v2_compatibility": {"maps_to_public_tensor": "z_final"},
            "resources": {"model_runs": 0},
            "claim_boundaries": ["unit-test only"],
            "warnings": ["unit_test"],
        }

    def test_roundtrip_preserves_time_major_contract_and_hashes(self):
        from neurodecodekit.cache.neurotoken import (
            load_neurotoken_cache,
            save_neurotoken_cache,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "tokens.npz"
            save_neurotoken_cache(path, **self._arrays(), metadata=self._metadata())
            loaded = load_neurotoken_cache(path)

        self.assertEqual(loaded.summary.tokens_shape, (2, 3, 4))
        self.assertEqual(loaded.summary.total_valid_tokens, 5)
        self.assertAlmostEqual(loaded.summary.padding_fraction, 1 / 6)
        self.assertEqual(loaded.summary.positioned_source_channel_count, 1)
        self.assertEqual(loaded.summary.split_counts, {"test": 1, "train": 1})
        self.assertTrue(loaded.summary.continuous_tokens)
        self.assertFalse(loaded.summary.learned_representation)
        self.assertEqual(len(loaded.summary.token_payload_sha256), 64)
        self.assertEqual(loaded.metadata["dimensions"]["embedding_dim"], 4)

    def test_rejects_mask_timestamp_and_vector_padding_disagreement(self):
        from neurodecodekit.cache.neurotoken import (
            NeuroTokenCacheSchemaError,
            save_neurotoken_cache,
        )

        arrays = self._arrays()
        arrays["token_mask"][1, 2] = True
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(
            NeuroTokenCacheSchemaError, "token_mask"
        ):
            save_neurotoken_cache(
                Path(tmp) / "bad-mask.npz", **arrays, metadata=self._metadata()
            )

        arrays = self._arrays()
        arrays["tokens"][1, 2, 0] = 1.0
        with tempfile.TemporaryDirectory() as tmp, self.assertRaisesRegex(
            NeuroTokenCacheSchemaError, "padded token vectors"
        ):
            save_neurotoken_cache(
                Path(tmp) / "bad-padding.npz", **arrays, metadata=self._metadata()
            )

    def test_mock_projection_is_deterministic_and_bounded(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken import project_mock_temporal_embeddings

        signals = np.arange(2 * 3 * 20, dtype="float32").reshape(2, 3, 20) / 100
        kwargs = {
            "signals": signals,
            "input_lengths": np.asarray([20, 18], dtype="int32"),
            "source_start_sec": np.asarray([0.0, 1.0]),
            "source_sampling_rate_hz": 100.0,
            "embedding_dim": 5,
            "kernel_size": 4,
            "stride": 2,
            "seed": 11,
            "max_tokens_per_item": 16,
            "max_output_mb": 1.0,
        }
        first = project_mock_temporal_embeddings(**kwargs)
        second = project_mock_temporal_embeddings(**kwargs)

        np.testing.assert_array_equal(first["tokens"], second["tokens"])
        np.testing.assert_array_equal(first["token_start_sec"], second["token_start_sec"])
        self.assertEqual(first["weights_sha256"], second["weights_sha256"])
        self.assertEqual(first["token_lengths"].tolist(), [9, 8])
        self.assertEqual(first["tokens"].shape, (2, 9, 5))
        self.assertAlmostEqual(first["token_end_sec"][0, 0], 0.04)

        with self.assertRaisesRegex(ValueError, "exceeding cap"):
            project_mock_temporal_embeddings(**{**kwargs, "max_output_mb": 0.00001})

    def test_sentence_projection_binds_strict_split_without_target_arrays(self):
        import numpy as np

        from neurodecodekit.cache.neurotoken import (
            SENTENCE_SIGNAL_MEMBERS_OPENED,
            SENTENCE_TARGET_MEMBERS_NOT_OPENED,
            load_neurotoken_cache,
            project_sentence_cache_to_neurotokens,
        )
        from neurodecodekit.evaluation.split_protocol import run_split_protocol
        from neurodecodekit.training.synthetic_sentences import save_synthetic_sentence_npz

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source.npz"
            split_dir = root / "split"
            output_a = root / "tokens-a.npz"
            output_b = root / "tokens-b.npz"
            sidecar = root / "tokens-a.json"
            save_synthetic_sentence_npz(
                source,
                sentences=48,
                channels=5,
                letter_classes=4,
                sfreq=100.0,
                seed=31,
            )
            split = run_split_protocol(
                cache_paths=[source],
                out_dir=split_dir,
                text_normalization="official-exact",
            )
            self.assertTrue(split["membership"]["strict_training_ready"])
            kwargs = {
                "source_cache_path": source,
                "split_report_path": split_dir / "split.json",
                "modality": "synthetic",
                "device_type": "synthetic-array",
                "subject_id": "SYN-1",
                "session_id": "SESSION-1",
                "embedding_dim": 12,
                "kernel_size": 16,
                "stride": 4,
                "seed": 23,
                "max_items": 64,
                "max_output_mb": 4.0,
            }
            accessed = []
            real_load = np.load

            class TrackingNpz:
                def __init__(self, wrapped, *, track):
                    self.wrapped = wrapped
                    self.files = wrapped.files
                    self.track = track

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, traceback):
                    self.wrapped.close()

                def __getitem__(self, name):
                    if self.track:
                        accessed.append(name)
                    return self.wrapped[name]

            def tracking_load(*args, **load_kwargs):
                loaded_path = Path(args[0]) if args else Path(load_kwargs["file"])
                return TrackingNpz(
                    real_load(*args, **load_kwargs),
                    track=loaded_path.resolve() == source.resolve(),
                )

            with patch("numpy.load", side_effect=tracking_load):
                result_a = project_sentence_cache_to_neurotokens(
                    out_path=output_a,
                    metadata_sidecar=sidecar,
                    **kwargs,
                )
                project_sentence_cache_to_neurotokens(out_path=output_b, **kwargs)
            loaded_a = load_neurotoken_cache(output_a)
            loaded_b = load_neurotoken_cache(output_b)
            with np.load(output_a, allow_pickle=False) as data:
                members = set(data.files)
            sidecar_exists = sidecar.exists()

        self.assertEqual(
            result_a["proof_posture"], "synthetic_neurotoken_interface_roundtrip_only"
        )
        self.assertEqual(result_a["model_runs"], 0)
        self.assertEqual(result_a["training_runs"], 0)
        self.assertEqual(result_a["real_data_reads"], 0)
        self.assertEqual(
            loaded_a.summary.token_payload_sha256,
            loaded_b.summary.token_payload_sha256,
        )
        self.assertEqual(loaded_a.metadata["source"]["cache_sha256"], split["sources"][0]["sha256"])
        self.assertEqual(loaded_a.metadata["source_geometry"]["position_source"], "unavailable")
        self.assertEqual(int(loaded_a.source_channel_position_mask.sum()), 0)
        self.assertEqual(set(accessed), set(SENTENCE_SIGNAL_MEMBERS_OPENED))
        self.assertTrue(set(SENTENCE_TARGET_MEMBERS_NOT_OPENED).isdisjoint(accessed))
        self.assertTrue(
            all(accessed.count(name) == 2 for name in SENTENCE_SIGNAL_MEMBERS_OPENED)
        )
        self.assertFalse(loaded_a.metadata["source"]["target_text_array_opened"])
        self.assertFalse(loaded_a.metadata["source"]["target_token_array_opened"])
        self.assertEqual(
            set(loaded_a.metadata["source"]["target_members_present_but_not_opened"]),
            set(SENTENCE_TARGET_MEMBERS_NOT_OPENED),
        )
        self.assertNotIn("target_texts", members)
        self.assertNotIn("target_token_ids", members)
        self.assertTrue(sidecar_exists)


if __name__ == "__main__":
    unittest.main()
