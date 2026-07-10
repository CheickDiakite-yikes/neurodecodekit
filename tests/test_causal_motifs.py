import importlib.util
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CausalMotifFixtureTests(unittest.TestCase):
    def _protocol(self):
        from neurodecodekit.training.causal_motifs import (
            registered_causal_motif_protocol,
        )

        return replace(
            registered_causal_motif_protocol(),
            train_items=16,
            validation_items=4,
            test_items=4,
            train_seed=9901,
            validation_seed=9902,
            test_seed=9903,
        )

    def test_separate_partitions_are_deterministic_bounded_and_aligned(self):
        import numpy as np

        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_manifest,
            load_causal_motif_partition,
            prepare_causal_motif_fixture,
            resolve_manifest_partition_path,
        )

        protocol = self._protocol()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = prepare_causal_motif_fixture(
                root / "first", protocol=protocol, max_total_mb=1
            )
            second = prepare_causal_motif_fixture(
                root / "second", protocol=protocol, max_total_mb=1
            )
            manifest_path = root / "first" / "manifest.json"
            loaded_manifest = load_causal_motif_manifest(
                manifest_path, require_registered_protocol=False
            )
            partitions = {
                split: load_causal_motif_partition(
                    resolve_manifest_partition_path(manifest_path, loaded_manifest, split),
                    expected=loaded_manifest["partitions"][split],
                )
                for split in ("train", "validation", "test")
            }

        self.assertFalse(first["registered_protocol_match"])
        self.assertLessEqual(
            first["artifacts"]["total_fixture_bytes"],
            first["artifacts"]["max_total_bytes"],
        )
        for split in ("train", "validation", "test"):
            self.assertEqual(
                first["partitions"][split]["sha256"],
                second["partitions"][split]["sha256"],
            )
            partition = partitions[split]
            self.assertEqual(partition.signals.dtype, np.dtype("float32"))
            self.assertEqual(partition.signals.shape[1:], (5, 112))
            self.assertEqual(
                len(first["partitions"][split]["class_support"]),
                protocol.n_classes,
            )
            self.assertTrue(
                all(value > 0 for value in first["partitions"][split]["class_support"])
            )
        item_sets = [set(value.item_ids.tolist()) for value in partitions.values()]
        self.assertFalse(item_sets[0] & item_sets[1])
        self.assertFalse(item_sets[0] & item_sets[2])
        self.assertFalse(item_sets[1] & item_sets[2])

    def test_registered_requirement_collision_and_manifest_path_safety(self):
        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_manifest,
            prepare_causal_motif_fixture,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            protocol = self._protocol()
            prepare_causal_motif_fixture(root, protocol=protocol)
            with self.assertRaisesRegex(ValueError, "registered protocol"):
                load_causal_motif_manifest(root / "manifest.json")
            with self.assertRaisesRegex(FileExistsError, "Refusing to replace"):
                prepare_causal_motif_fixture(root, protocol=protocol)

            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            manifest["partitions"]["test"]["path"] = "../test.npz"
            unsafe = root / "unsafe.json"
            unsafe.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "local and relative"):
                load_causal_motif_manifest(
                    unsafe, require_registered_protocol=False
                )

    def test_partition_validation_rejects_fractional_lengths_and_bad_frame_labels(self):
        import numpy as np

        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_partition,
            make_causal_motif_partition,
            save_causal_motif_partition,
        )

        protocol = self._protocol()
        arrays, metadata = make_causal_motif_partition(
            split="validation", items=4, seed=9902, protocol=protocol
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fractional = dict(arrays)
            fractional["input_lengths"] = arrays["input_lengths"].astype("float32")
            with self.assertRaisesRegex(ValueError, "integer vector"):
                save_causal_motif_partition(
                    root / "fractional.npz", arrays=fractional, metadata=metadata
                )

            malformed = root / "bad-label.npz"
            bad_labels = arrays["frame_labels"].copy()
            bad_labels[0, 0] = (int(bad_labels[0, 0]) + 1) % protocol.n_classes
            np.savez_compressed(
                malformed,
                **{**arrays, "frame_labels": bad_labels},
                metadata=json.dumps(metadata, sort_keys=True),
            )
            with self.assertRaisesRegex(ValueError, "final-sample semantics"):
                load_causal_motif_partition(malformed)

    def test_manifest_and_partition_reject_unbound_contract_members(self):
        import numpy as np

        from neurodecodekit.training.causal_motifs import (
            load_causal_motif_manifest,
            load_causal_motif_partition,
            make_causal_motif_partition,
            prepare_causal_motif_fixture,
        )

        protocol = self._protocol()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare_causal_motif_fixture(root / "fixture", protocol=protocol)
            manifest = json.loads(
                (root / "fixture" / "manifest.json").read_text(encoding="utf-8")
            )
            manifest["partitions"]["validation"]["n_classes"] = 99
            tampered_manifest = root / "tampered-manifest.json"
            tampered_manifest.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "n_classes is inconsistent"):
                load_causal_motif_manifest(
                    tampered_manifest, require_registered_protocol=False
                )

            arrays, metadata = make_causal_motif_partition(
                split="validation", items=4, seed=9902, protocol=protocol
            )
            unexpected = root / "unexpected-member.npz"
            np.savez_compressed(
                unexpected,
                **arrays,
                target_texts=np.asarray(["forbidden"]),
                metadata=json.dumps(metadata, sort_keys=True),
            )
            with self.assertRaisesRegex(ValueError, "unexpected members"):
                load_causal_motif_partition(unexpected)


if __name__ == "__main__":
    unittest.main()
