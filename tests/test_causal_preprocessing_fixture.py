import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class CausalPreprocessingFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            import numpy as np
        except ImportError:
            raise unittest.SkipTest("NumPy is optional") from None
        cls.np = np

    @staticmethod
    def _protocol():
        from neurodecodekit.training.causal_preprocessing_fixture import (
            CausalPreprocessingFixtureProtocol,
        )

        return CausalPreprocessingFixtureProtocol(
            development_seed=9501,
            qualification_seed=9502,
            item_lengths=tuple(range(1001, 1013)),
        )

    def _fixture(self, root: Path, name: str = "fixture") -> Path:
        from neurodecodekit.training.causal_preprocessing_fixture import (
            prepare_causal_preprocessing_fixture,
        )

        output = root / name
        prepare_causal_preprocessing_fixture(
            output,
            protocol=self._protocol(),
            require_registered_protocol=False,
            require_static_gate=False,
            enforce_authorized_output_root=False,
        )
        return output / "manifest.json"

    @staticmethod
    def _write_sized_manifest(path: Path, manifest: dict) -> None:
        for _ in range(10):
            payload = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
            manifest["artifacts"]["manifest_bytes"] = len(payload)
            manifest["artifacts"]["total_bytes"] = (
                manifest["artifacts"]["partition_bytes"] + len(payload)
            )
        path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def test_replay_is_byte_deterministic_and_partitions_are_disjoint(self):
        from neurodecodekit.training.causal_preprocessing_fixture import (
            load_causal_preprocessing_manifest,
            load_causal_preprocessing_partition,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = self._fixture(root, "first")
            second = self._fixture(root, "second")
            for name in ("development.npz", "qualification.npz", "manifest.json"):
                self.assertEqual((first.parent / name).read_bytes(), (second.parent / name).read_bytes())
            manifest = load_causal_preprocessing_manifest(
                first,
                require_registered_protocol=False,
            )
            development = load_causal_preprocessing_partition(
                first, "development", require_registered_protocol=False
            )
            qualification = load_causal_preprocessing_partition(
                first, "qualification", require_registered_protocol=False
            )
            self.assertTrue(set(development.item_ids.tolist()).isdisjoint(qualification.item_ids.tolist()))
            self.assertLessEqual(manifest["artifacts"]["total_bytes"], 4 * 1024 * 1024)
            for index, length in enumerate(development.input_lengths.tolist()):
                self.assertTrue(self.np.equal(development.signals[index, :, length:], 0.0).all())

    def test_manifest_inspection_does_not_open_arrays(self):
        from neurodecodekit.training.causal_preprocessing_fixture import (
            load_causal_preprocessing_manifest,
        )

        with tempfile.TemporaryDirectory() as temporary:
            manifest = self._fixture(Path(temporary))
            with mock.patch("numpy.load", side_effect=AssertionError("array opened")) as loader:
                load_causal_preprocessing_manifest(
                    manifest,
                    require_registered_protocol=False,
                )
            loader.assert_not_called()

    def test_hidden_target_member_is_refused_from_zip_metadata(self):
        from neurodecodekit.training.causal_preprocessing_fixture import (
            load_causal_preprocessing_manifest,
        )

        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = self._fixture(Path(temporary))
            partition_path = manifest_path.parent / "development.npz"
            with self.np.load(partition_path, allow_pickle=False) as source:
                arrays = {name: source[name].copy() for name in source.files}
            arrays["targets"] = self.np.zeros(12, dtype="int32")
            self.np.savez_compressed(partition_path, **arrays)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            row = manifest["partitions"]["development"]
            row["bytes"] = partition_path.stat().st_size
            row["sha256"] = hashlib.sha256(partition_path.read_bytes()).hexdigest()
            manifest["artifacts"]["partition_bytes"] = sum(
                (manifest_path.parent / manifest["partitions"][split]["path"]).stat().st_size
                for split in ("development", "qualification")
            )
            self._write_sized_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(ValueError, "forbidden members"):
                load_causal_preprocessing_manifest(
                    manifest_path,
                    require_registered_protocol=False,
                )

    def test_strict_split_binding_rejects_qualification_payload_as_development(self):
        from neurodecodekit.training.causal_preprocessing_fixture import (
            load_causal_preprocessing_partition,
        )

        with tempfile.TemporaryDirectory() as temporary:
            manifest_path = self._fixture(Path(temporary))
            qualification = manifest_path.parent / "qualification.npz"
            rebound = manifest_path.parent / "development-rebound.npz"
            rebound.write_bytes(qualification.read_bytes())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            row = manifest["partitions"]["development"]
            row["path"] = rebound.name
            row["bytes"] = rebound.stat().st_size
            row["sha256"] = hashlib.sha256(rebound.read_bytes()).hexdigest()
            manifest["artifacts"]["partition_bytes"] = row["bytes"] + qualification.stat().st_size
            self._write_sized_manifest(manifest_path, manifest)
            with self.assertRaisesRegex(ValueError, "metadata identity mismatch"):
                load_causal_preprocessing_partition(
                    manifest_path,
                    "development",
                    require_registered_protocol=False,
                )

    def test_output_cap_and_collision_fail_before_overwrite(self):
        from neurodecodekit.training.causal_preprocessing_fixture import (
            prepare_causal_preprocessing_fixture,
        )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            capped = root / "capped"
            with self.assertRaisesRegex(ValueError, "exceeding cap"):
                prepare_causal_preprocessing_fixture(
                    capped,
                    max_total_bytes=128,
                    protocol=self._protocol(),
                    require_registered_protocol=False,
                    require_static_gate=False,
                    enforce_authorized_output_root=False,
                )
            self.assertFalse(capped.exists())
            existing = root / "existing"
            existing.mkdir()
            marker = existing / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                prepare_causal_preprocessing_fixture(
                    existing,
                    protocol=self._protocol(),
                    require_registered_protocol=False,
                    require_static_gate=False,
                    enforce_authorized_output_root=False,
                )
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
