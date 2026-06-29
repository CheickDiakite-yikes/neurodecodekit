import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cache.npz_cache import (
    CACHE_SCHEMA_NAME,
    CACHE_SCHEMA_VERSION,
    CacheSchemaError,
    load_npz_cache,
    save_npz_cache,
    write_cache_metadata_sidecar,
)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class NpzCacheSchemaTests(unittest.TestCase):
    def test_save_and_load_cache_schema_v0(self):
        import numpy as np

        windows = np.zeros((3, 2, 4), dtype="float32")
        labels = np.array(["A", "B", "A"], dtype="U1")
        channel_names = np.array(["left", "right"], dtype="U")
        metadata = {
            "kind": "unit_test",
            "source_files": {"raw": "synthetic"},
            "transformations": [{"name": "unit_test_generation"}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cache.npz"
            save_npz_cache(
                path,
                windows=windows,
                labels=labels,
                metadata=metadata,
                extra_arrays={"channel_names": channel_names},
            )

            loaded = load_npz_cache(path)

        self.assertEqual(loaded.windows.shape, (3, 2, 4))
        self.assertEqual(loaded.summary.schema_name, CACHE_SCHEMA_NAME)
        self.assertEqual(loaded.summary.schema_version, CACHE_SCHEMA_VERSION)
        self.assertEqual(loaded.summary.n_events, 3)
        self.assertEqual(loaded.summary.n_channels, 2)
        self.assertEqual(loaded.summary.n_timepoints, 4)
        self.assertEqual(loaded.summary.n_unique_labels, 2)
        self.assertIn("channel_names", loaded.arrays)
        self.assertEqual(loaded.metadata["schema"]["name"], CACHE_SCHEMA_NAME)
        self.assertEqual(loaded.metadata["dimensions"]["n_channels"], 2)
        self.assertIn("npz_compressed_write", [t["name"] for t in loaded.metadata["transformations"]])

    def test_rejects_bad_window_rank(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(CacheSchemaError, "Expected `windows`"):
                save_npz_cache(
                    Path(tmp) / "bad.npz",
                    windows=np.zeros((3, 4), dtype="float32"),
                    labels=np.array(["A", "B", "C"], dtype="U1"),
                    metadata={"kind": "bad"},
                )

    def test_rejects_label_length_mismatch(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(CacheSchemaError, "`labels` length"):
                save_npz_cache(
                    Path(tmp) / "bad.npz",
                    windows=np.zeros((3, 2, 4), dtype="float32"),
                    labels=np.array(["A", "B"], dtype="U1"),
                    metadata={"kind": "bad"},
                )

    def test_rejects_channel_name_mismatch(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(CacheSchemaError, "channel_names"):
                save_npz_cache(
                    Path(tmp) / "bad.npz",
                    windows=np.zeros((3, 2, 4), dtype="float32"),
                    labels=np.array(["A", "B", "C"], dtype="U1"),
                    metadata={"kind": "bad"},
                    extra_arrays={"channel_names": np.array(["only_one"], dtype="U")},
                )

    def test_metadata_sidecar_contains_summary_and_metadata(self):
        import numpy as np

        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "cache.npz"
            sidecar_path = Path(tmp) / "cache.metadata.json"
            save_npz_cache(
                cache_path,
                windows=np.zeros((1, 1, 2), dtype="float32"),
                labels=np.array(["A"], dtype="U1"),
                metadata={"kind": "sidecar_test"},
            )
            write_cache_metadata_sidecar(cache_path, sidecar_path)

            payload = json.loads(sidecar_path.read_text(encoding="utf-8"))

        self.assertEqual(payload["summary"]["schema_name"], CACHE_SCHEMA_NAME)
        self.assertEqual(payload["metadata"]["kind"], "sidecar_test")


if __name__ == "__main__":
    unittest.main()
