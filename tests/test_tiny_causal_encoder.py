import importlib.util
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


HAS_ML = bool(
    importlib.util.find_spec("numpy") and importlib.util.find_spec("torch")
)


@unittest.skipUnless(HAS_ML, "NumPy/Torch not installed")
class TinyCausalEncoderTests(unittest.TestCase):
    def _fixture(self, root: Path):
        from neurodecodekit.training.causal_motifs import (
            prepare_causal_motif_fixture,
            registered_causal_motif_protocol,
        )

        protocol = replace(
            registered_causal_motif_protocol(),
            train_items=16,
            validation_items=4,
            test_items=4,
            train_seed=9911,
            validation_seed=9912,
            test_seed=9913,
        )
        prepare_causal_motif_fixture(root, protocol=protocol)
        return root / "manifest.json"

    def _partitions(self, manifest_path: Path):
        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_manifest,
            load_causal_motif_partition,
            resolve_manifest_partition_path,
        )

        manifest = load_causal_motif_manifest(
            manifest_path, require_registered_protocol=False
        )
        loaded = {
            split: load_causal_motif_partition(
                resolve_manifest_partition_path(manifest_path, manifest, split),
                expected=manifest["partitions"][split],
            )
            for split in ("train", "validation")
        }
        return manifest, loaded

    def test_train_checkpoint_and_canonical_stream_replay(self):
        import numpy as np

        from neurodecodekit.experiments.causal_replay_gate import (
            REGISTERED_SCHEDULES,
            registered_chunk_sizes,
        )
        from neurodecodekit.models.tiny_causal_encoder import (
            batched_partition_outputs,
            canonical_partition_outputs,
            load_tiny_causal_encoder_checkpoint,
            save_tiny_causal_encoder_checkpoint,
            train_tiny_causal_encoder,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = self._fixture(root / "fixture")
            manifest, partitions = self._partitions(manifest_path)
            training, fit_report = train_tiny_causal_encoder(
                partitions["train"], partitions["validation"]
            )
            checkpoint = root / "encoder.npz"
            summary = save_tiny_causal_encoder_checkpoint(
                checkpoint,
                training=training,
                metadata={
                    "proof_posture": "nonregistered_test_fixture_only",
                    "fixture_protocol_sha256": manifest["protocol_sha256"],
                    "geometry": {
                        "n_channels": 5,
                        "kernel_size": 16,
                        "stride": 4,
                        "n_classes": 6,
                        "sampling_rate_hz": 100.0,
                    },
                    "selection_frozen_before_test": True,
                },
            )
            producer, metadata = load_tiny_causal_encoder_checkpoint(checkpoint)
            canonical = canonical_partition_outputs(
                producer, partitions["validation"]
            )
            batched = batched_partition_outputs(producer, partitions["validation"])

            schedule_payloads = {}
            max_state = 0
            for schedule in REGISTERED_SCHEDULES:
                rows = []
                for item_index, length_value in enumerate(
                    partitions["validation"].input_lengths.tolist()
                ):
                    length = int(length_value)
                    stream = producer.new_stream(
                        max_chunk_samples=128,
                        max_total_samples=128,
                        max_total_tokens=32,
                    )
                    offset = 0
                    batches = []
                    for size in registered_chunk_sizes(
                        length,
                        name=schedule,
                        kernel_size=producer.kernel_size,
                        stride=producer.stride,
                    ):
                        batches.append(
                            stream.push(
                                partitions["validation"].signals[
                                    item_index, :, offset : offset + size
                                ]
                            )
                        )
                        offset += size
                    flush = stream.flush()
                    self.assertTrue(flush.stream_closed)
                    max_state = max(max_state, stream.max_mutable_state_bytes)
                    rows.append(np.concatenate([batch.tokens for batch in batches]))
                schedule_payloads[schedule] = np.concatenate(rows)

            with self.assertRaisesRegex(FileExistsError, "Refusing to replace"):
                save_tiny_causal_encoder_checkpoint(
                    checkpoint,
                    training=training,
                    metadata=summary["metadata"],
                )

        self.assertEqual(training.parameter_count, 1130)
        self.assertEqual(training.encoder_parameter_count, 1076)
        self.assertEqual(training.probe_parameter_count, 54)
        self.assertEqual(fit_report["standardizer"]["fit_split"], "train")
        self.assertEqual(metadata["serialization"], "numpy_npz_allow_pickle_false")
        self.assertEqual(producer.mutable_state_bound_bytes, 300)
        self.assertLessEqual(max_state, 300)
        self.assertLessEqual(
            float(
                np.abs(canonical["embeddings"] - batched["embeddings"]).max()
            ),
            1e-6,
        )
        for payload in schedule_payloads.values():
            self.assertTrue(np.array_equal(payload, canonical["embeddings"]))

    def test_metrics_make_background_prior_explicit(self):
        import numpy as np

        from neurodecodekit.models.tiny_causal_encoder import (
            classification_metrics,
            train_only_prior_class,
        )

        targets = np.asarray([0, 0, 0, 1, 1, 2], dtype="int64")
        prior = train_only_prior_class(targets, n_classes=3)
        predictions = np.full_like(targets, prior)
        metrics = classification_metrics(targets, predictions, n_classes=3)

        self.assertEqual(prior, 0)
        self.assertEqual(metrics["accuracy"], 0.5)
        self.assertAlmostEqual(metrics["balanced_accuracy"], 1 / 3)
        self.assertEqual(metrics["class_support"], [3, 2, 1])


if __name__ == "__main__":
    unittest.main()
