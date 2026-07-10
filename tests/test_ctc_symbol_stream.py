import importlib.util
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CTCSymbolStreamFixtureTests(unittest.TestCase):
    def _protocol(self):
        from neurodecodekit.training.ctc_symbol_stream import (
            registered_ctc_symbol_stream_protocol,
        )

        return replace(
            registered_ctc_symbol_stream_protocol(),
            train_items=16,
            validation_items=4,
            test_items=4,
            train_seed=9301,
            validation_seed=9302,
            test_seed=9303,
        )

    def test_fresh_partitions_are_deterministic_bounded_and_repeat_complete(self):
        from neurodecodekit.training.ctc_symbol_stream import (
            load_ctc_symbol_stream_manifest,
            load_ctc_symbol_stream_partition,
            prepare_ctc_symbol_stream_fixture,
            resolve_ctc_symbol_partition_path,
        )

        protocol = self._protocol()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = prepare_ctc_symbol_stream_fixture(
                root / "first", protocol=protocol
            )
            second = prepare_ctc_symbol_stream_fixture(
                root / "second", protocol=protocol
            )
            manifest_path = root / "first" / "manifest.json"
            manifest = load_ctc_symbol_stream_manifest(
                manifest_path, require_registered_protocol=False
            )
            loaded = {
                split: load_ctc_symbol_stream_partition(
                    resolve_ctc_symbol_partition_path(manifest_path, manifest, split),
                    expected=manifest["partitions"][split],
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
            self.assertGreaterEqual(first["partitions"][split]["repeated_pair_count"], 1)
            partition = loaded[split]
            for index, length_value in enumerate(partition.target_lengths.tolist()):
                row = partition.target_token_ids[index, : int(length_value)].tolist()
                self.assertEqual(set(row), {1, 2, 3, 4, 5})
                self.assertTrue(any(left == right for left, right in zip(row[:-1], row[1:])))

    def test_target_only_access_never_indexes_signal_members(self):
        import numpy as np

        from neurodecodekit.training.ctc_symbol_stream import (
            TARGET_ONLY_MEMBERS,
            load_ctc_symbol_stream_manifest,
            load_ctc_symbol_stream_partition,
            prepare_ctc_symbol_stream_fixture,
            resolve_ctc_symbol_partition_path,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare_ctc_symbol_stream_fixture(root, protocol=self._protocol())
            manifest_path = root / "manifest.json"
            manifest = load_ctc_symbol_stream_manifest(
                manifest_path, require_registered_protocol=False
            )
            train_path = resolve_ctc_symbol_partition_path(
                manifest_path, manifest, "train"
            )
            real_load = np.load
            accessed = []

            class TrackingNpz:
                def __init__(self, wrapped):
                    self.wrapped = wrapped
                    self.files = wrapped.files

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, traceback):
                    self.wrapped.close()

                def __getitem__(self, name):
                    accessed.append(name)
                    return self.wrapped[name]

            def tracking_load(*args, **kwargs):
                return TrackingNpz(real_load(*args, **kwargs))

            with patch("numpy.load", side_effect=tracking_load):
                loaded = load_ctc_symbol_stream_partition(
                    train_path,
                    expected=manifest["partitions"]["train"],
                    access_mode="targets-only",
                )

        self.assertEqual(tuple(accessed), TARGET_ONLY_MEMBERS)
        self.assertEqual(loaded.opened_members, TARGET_ONLY_MEMBERS)
        self.assertIsNone(loaded.signals)
        self.assertIsNone(loaded.frame_labels)

    def test_manifest_and_partition_reject_tampering_and_extra_members(self):
        import numpy as np

        from neurodecodekit.training.ctc_symbol_stream import (
            load_ctc_symbol_stream_manifest,
            load_ctc_symbol_stream_partition,
            make_ctc_symbol_stream_partition,
            prepare_ctc_symbol_stream_fixture,
        )

        protocol = self._protocol()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare_ctc_symbol_stream_fixture(root / "fixture", protocol=protocol)
            manifest = json.loads(
                (root / "fixture" / "manifest.json").read_text(encoding="utf-8")
            )
            manifest["partitions"]["test"]["repeated_pair_count"] = 0
            tampered = root / "tampered.json"
            tampered.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "repeated_pair_count is invalid"):
                load_ctc_symbol_stream_manifest(
                    tampered, require_registered_protocol=False
                )

            arrays, metadata = make_ctc_symbol_stream_partition(
                split="validation", items=4, seed=9302, protocol=protocol
            )
            unexpected = root / "unexpected.npz"
            np.savez_compressed(
                unexpected,
                **arrays,
                reference_texts=np.asarray(["forbidden"]),
                metadata=json.dumps(metadata, sort_keys=True),
            )
            with self.assertRaisesRegex(ValueError, "unexpected members"):
                load_ctc_symbol_stream_partition(unexpected)

    def test_registered_requirement_and_collision_refusal(self):
        from neurodecodekit.training.ctc_symbol_stream import (
            load_ctc_symbol_stream_manifest,
            prepare_ctc_symbol_stream_fixture,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            prepare_ctc_symbol_stream_fixture(root, protocol=self._protocol())
            with self.assertRaisesRegex(ValueError, "registered protocol"):
                load_ctc_symbol_stream_manifest(root / "manifest.json")
            with self.assertRaisesRegex(FileExistsError, "Refusing to replace"):
                prepare_ctc_symbol_stream_fixture(root, protocol=self._protocol())


if __name__ == "__main__":
    unittest.main()
