import json
import tempfile
import unittest
import zipfile
from pathlib import Path


try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError:  # pragma: no cover
    NUMPY_AVAILABLE = False


@unittest.skipUnless(NUMPY_AVAILABLE, "NumPy not installed")
class RowStreamingNPZTests(unittest.TestCase):
    def test_streams_only_selected_rows_and_reports_opaque_traversal(self):
        from neurodecodekit.cache.row_streaming_npz import (
            inspect_npz_members,
            read_npz_json_scalar,
            stream_npz_rows,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.npz"
            values = np.arange(30, dtype="float32").reshape(5, 2, 3)
            np.savez_compressed(
                path,
                signals=values,
                labels=np.asarray(["A", "B", "C", "D", "E"]),
                metadata=json.dumps({"kind": "synthetic"}),
            )
            headers = inspect_npz_members(path)
            self.assertEqual(headers["signals.npy"].shape, (5, 2, 3))
            self.assertEqual(headers["metadata.npy"].shape, ())
            self.assertEqual(read_npz_json_scalar(path), {"kind": "synthetic"})
            selected = stream_npz_rows(
                path,
                "signals",
                [4, 1],
                expected_shape=(5, 2, 3),
                expected_dtype="float32",
                maximum_row_bytes=24,
            )
            np.testing.assert_array_equal(selected.values, values[[4, 1]])
            self.assertEqual(selected.physical_rows_traversed, 5)
            self.assertEqual(selected.opaque_excluded_rows_traversed, 3)
            self.assertEqual(selected.delivered_rows, 2)
            self.assertEqual(selected.reusable_buffer_bytes, 24)
            self.assertEqual(selected.reusable_buffer_overwrites, 5)

    def test_refuses_object_dtype_scalar_rows_and_oversized_rows(self):
        from neurodecodekit.cache.row_streaming_npz import (
            RowStreamingNPZError,
            stream_npz_rows,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            object_path = root / "object.npz"
            np.savez_compressed(object_path, bad=np.asarray([{"secret": "x"}], dtype=object))
            with self.assertRaisesRegex(RowStreamingNPZError, "object dtype"):
                stream_npz_rows(object_path, "bad", [0])

            scalar_path = root / "scalar.npz"
            np.savez_compressed(scalar_path, metadata=json.dumps({"ok": True}))
            with self.assertRaisesRegex(RowStreamingNPZError, "scalar"):
                stream_npz_rows(scalar_path, "metadata", [0])

            large_path = root / "large.npz"
            np.savez_compressed(large_path, rows=np.zeros((2, 100), dtype="float32"))
            with self.assertRaisesRegex(RowStreamingNPZError, "above cap"):
                stream_npz_rows(large_path, "rows", [0], maximum_row_bytes=399)

    def test_refuses_malformed_headers_duplicates_and_out_of_range_rows(self):
        from neurodecodekit.cache.row_streaming_npz import (
            RowStreamingNPZError,
            inspect_npz_members,
            stream_npz_rows,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            malformed = root / "malformed.npz"
            with zipfile.ZipFile(malformed, "w") as bundle:
                bundle.writestr("bad.npy", b"not-an-npy")
            with self.assertRaisesRegex(RowStreamingNPZError, "invalid NPY header"):
                inspect_npz_members(malformed)

            valid = root / "valid.npz"
            np.savez_compressed(valid, rows=np.arange(6, dtype="int16").reshape(3, 2))
            with self.assertRaisesRegex(RowStreamingNPZError, "repeat"):
                stream_npz_rows(valid, "rows", [1, 1])
            with self.assertRaisesRegex(RowStreamingNPZError, "exceeds row count"):
                stream_npz_rows(valid, "rows", [3])

    def test_hash_pass_is_single_forward_and_fail_closed(self):
        from neurodecodekit.cache.row_streaming_npz import (
            RowStreamingNPZError,
            sha256_file_once,
        )

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.bin"
            path.write_bytes(b"bounded-payload" * 100)
            first = sha256_file_once(path, expected_bytes=1500, chunk_bytes=17)
            self.assertEqual(first["hash_passes"], 1)
            self.assertEqual(first["bytes_read"], 1500)
            second = sha256_file_once(path, expected_sha256=first["sha256"])
            self.assertEqual(second["sha256"], first["sha256"])
            with self.assertRaisesRegex(RowStreamingNPZError, "SHA-256 mismatch"):
                sha256_file_once(path, expected_sha256="0" * 64)


if __name__ == "__main__":
    unittest.main()
