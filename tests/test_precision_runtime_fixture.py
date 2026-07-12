import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class PrecisionRuntimeFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
        except ImportError:
            raise unittest.SkipTest("NumPy is optional") from None
        cls.np = np

    def _protocol(self):
        from neurodecodekit.training.precision_runtime_fixture import (
            PrecisionRuntimeFixtureProtocol,
        )

        return PrecisionRuntimeFixtureProtocol(
            selection_seed=9401,
            qualification_seed=9402,
            items_per_partition=12,
            items_per_family=2,
            channels=5,
            sampling_rate_hz=100.0,
            minimum_samples=16,
            maximum_samples=32,
            length_multiple_samples=4,
            value_min=-4.0,
            value_max=4.0,
        )

    def _prepare(self, root: Path, name: str = "fixture"):
        from neurodecodekit.training.precision_runtime_fixture import (
            prepare_precision_runtime_fixture,
        )

        output = root / name
        manifest = prepare_precision_runtime_fixture(
            output,
            max_total_bytes=128 * 1024,
            protocol=self._protocol(),
            require_registered_protocol=False,
        )
        return output, manifest

    def _rewrite_manifest(self, manifest_path: Path, manifest: dict):
        import neurodecodekit.training.precision_runtime_fixture as fixture_module

        partition_bytes = sum(
            int((manifest_path.parent / f"{split}.npz").stat().st_size)
            for split in ("selection", "qualification")
        )
        manifest["artifacts"]["partition_bytes"] = partition_bytes
        manifest_path.write_bytes(fixture_module._manifest_payload_with_sizes(manifest))

    def test_deterministic_replay_and_metadata_only_inspection(self):
        import neurodecodekit.training.precision_runtime_fixture as fixture_module

        from neurodecodekit.training.precision_runtime_fixture import (
            load_precision_runtime_manifest,
            summarize_precision_runtime_manifest,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, _ = self._prepare(root, "first")
            second, _ = self._prepare(root, "second")
            for name in ("manifest.json", "selection.npz", "qualification.npz"):
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            original_hash = fixture_module._file_sha256

            def metadata_hash(path):
                if Path(path).suffix == ".npz":
                    raise AssertionError("partition bytes opened during metadata inspection")
                return original_hash(path)

            with (
                mock.patch("numpy.load", side_effect=AssertionError("array opened")),
                mock.patch.object(fixture_module, "_file_sha256", metadata_hash),
            ):
                manifest = load_precision_runtime_manifest(
                    first / "manifest.json",
                    max_total_bytes=128 * 1024,
                    require_registered_protocol=False,
                )
            summary = summarize_precision_runtime_manifest(manifest)
            self.assertTrue(summary["metadata_only_no_partition_arrays_opened"])
            self.assertFalse(summary["registered_protocol_match"])
            self.assertEqual(summary["artifacts"]["files"], 3)
            self.assertLessEqual(summary["artifacts"]["total_bytes"], 128 * 1024)

    def test_partitions_are_target_free_bounded_padded_and_disjoint(self):
        from neurodecodekit.training.precision_runtime_fixture import (
            ARRAY_MEMBERS,
            FORBIDDEN_MEMBERS,
            WAVEFORM_FAMILIES,
            load_precision_runtime_partition,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output, manifest = self._prepare(Path(tmp))
            selection = load_precision_runtime_partition(
                output / "manifest.json",
                "selection",
                max_total_bytes=128 * 1024,
                require_registered_protocol=False,
            )
            qualification = load_precision_runtime_partition(
                output / "manifest.json",
                "qualification",
                max_total_bytes=128 * 1024,
                require_registered_protocol=False,
            )
            self.assertEqual(set(selection.opened_members), set(ARRAY_MEMBERS))
            self.assertFalse(set(selection.opened_members).intersection(FORBIDDEN_MEMBERS))
            self.assertFalse(
                set(selection.item_ids.tolist()).intersection(qualification.item_ids.tolist())
            )
            self.assertEqual(selection.signals.dtype, self.np.dtype("float32"))
            self.assertTrue(self.np.isfinite(selection.signals).all())
            self.assertGreaterEqual(float(selection.signals.min()), -4.0)
            self.assertLessEqual(float(selection.signals.max()), 4.0)
            for index, length in enumerate(selection.input_lengths.tolist()):
                self.assertTrue(
                    self.np.equal(selection.signals[index, :, int(length) :], 0.0).all()
                )
            self.assertEqual(
                selection.metadata["family_counts"],
                {family: 2 for family in WAVEFORM_FAMILIES},
            )
            self.assertEqual(selection.metadata["generator"]["model_outputs_read"], 0)
            self.assertEqual(selection.metadata["generator"]["target_label_text_reads"], 0)
            self.assertFalse(manifest["generation"]["uses_target_label_or_text"])

    def test_forbidden_target_member_is_rejected_even_with_matching_file_hash(self):
        from neurodecodekit.training.precision_runtime_fixture import (
            load_precision_runtime_partition,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output, _ = self._prepare(Path(tmp))
            manifest_path = output / "manifest.json"
            selection_path = output / "selection.npz"
            with self.np.load(selection_path, allow_pickle=False) as data:
                arrays = {name: data[name].copy() for name in data.files}
            self.np.savez_compressed(
                selection_path,
                **arrays,
                targets=self.np.zeros(12, dtype="int64"),
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["partitions"]["selection"]["bytes"] = selection_path.stat().st_size
            manifest["partitions"]["selection"]["sha256"] = hashlib.sha256(
                selection_path.read_bytes()
            ).hexdigest()
            self._rewrite_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(ValueError, "forbidden members"):
                load_precision_runtime_partition(
                    manifest_path,
                    "selection",
                    max_total_bytes=128 * 1024,
                    require_registered_protocol=False,
                )

    def test_strict_split_binding_rejects_overlap_and_seed_drift(self):
        from neurodecodekit.training.precision_runtime_fixture import (
            load_precision_runtime_manifest,
        )

        with tempfile.TemporaryDirectory() as tmp:
            output, _ = self._prepare(Path(tmp))
            manifest_path = output / "manifest.json"
            original = json.loads(manifest_path.read_text(encoding="utf-8"))
            overlap = json.loads(json.dumps(original))
            overlap["partitions"]["qualification"]["item_ids"][0] = overlap[
                "partitions"
            ]["selection"]["item_ids"][0]
            self._rewrite_manifest(manifest_path, overlap)
            with self.assertRaisesRegex(ValueError, "item IDs overlap"):
                load_precision_runtime_manifest(
                    manifest_path,
                    max_total_bytes=128 * 1024,
                    require_registered_protocol=False,
                )

            self._rewrite_manifest(manifest_path, original)
            drifted = json.loads(manifest_path.read_text(encoding="utf-8"))
            drifted["partitions"]["selection"]["seed"] += 1
            self._rewrite_manifest(manifest_path, drifted)
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                load_precision_runtime_manifest(
                    manifest_path,
                    max_total_bytes=128 * 1024,
                    require_registered_protocol=False,
                )

    def test_caps_collisions_and_wrong_seed_fail_closed(self):
        from neurodecodekit.training.precision_runtime_fixture import (
            make_precision_runtime_partition,
            prepare_precision_runtime_fixture,
        )

        protocol = self._protocol()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "exceeding cap"):
                prepare_precision_runtime_fixture(
                    root / "too-small",
                    max_total_bytes=64,
                    protocol=protocol,
                    require_registered_protocol=False,
                )
            self.assertFalse((root / "too-small").exists())
            existing = root / "existing"
            existing.mkdir()
            with self.assertRaises(FileExistsError):
                prepare_precision_runtime_fixture(
                    existing,
                    max_total_bytes=128 * 1024,
                    protocol=protocol,
                    require_registered_protocol=False,
                )
            with self.assertRaisesRegex(ValueError, "cannot exceed"):
                prepare_precision_runtime_fixture(
                    root / "raised-cap",
                    max_total_bytes=512 * 1024 + 1,
                    protocol=protocol,
                    require_registered_protocol=False,
                )
            with self.assertRaisesRegex(ValueError, "seed must be"):
                make_precision_runtime_partition(
                    split="selection",
                    seed=protocol.selection_seed + 1,
                    protocol=protocol,
                )


if __name__ == "__main__":
    unittest.main()
