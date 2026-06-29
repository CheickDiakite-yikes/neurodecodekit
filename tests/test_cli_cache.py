import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class CacheCliTests(unittest.TestCase):
    def test_make_synthetic_then_load_cache_with_sidecar(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "synthetic.npz"
            sidecar_path = Path(tmp) / "synthetic.metadata.json"

            with redirect_stdout(io.StringIO()):
                make_code = main([
                    "make-synthetic-shard",
                    "--out",
                    str(cache_path),
                    "--samples",
                    "6",
                    "--channels",
                    "2",
                    "--times",
                    "5",
                    "--classes",
                    "3",
                ])
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                load_code = main([
                    "load-cache",
                    "--cache",
                    str(cache_path),
                    "--metadata-out",
                    str(sidecar_path),
                ])

            output_lines = stdout.getvalue().splitlines()
            summary = json.loads("\n".join(output_lines[:-1]))
            sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))

        self.assertEqual(make_code, 0)
        self.assertEqual(load_code, 0)
        self.assertEqual(summary["windows_shape"], [6, 2, 5])
        self.assertEqual(summary["schema_name"], "b2q-mini-cache")
        self.assertIn("synthetic_cache_not_real_neural_data", summary["warnings"])
        self.assertEqual(sidecar["summary"]["n_events"], 6)
        self.assertEqual(sidecar["metadata"]["kind"], "synthetic")


if __name__ == "__main__":
    unittest.main()
