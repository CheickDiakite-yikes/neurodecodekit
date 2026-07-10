import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class NeuroTokenCliTests(unittest.TestCase):
    def _source_and_split(self, root: Path) -> tuple[Path, Path]:
        source = root / "source.npz"
        split_dir = root / "split"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                main(
                    [
                        "make-synthetic-sentence-cache",
                        "--out",
                        str(source),
                        "--sentences",
                        "48",
                        "--channels",
                        "5",
                        "--sfreq",
                        "100",
                        "--seed",
                        "31",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "split-protocol",
                        "--cache",
                        str(source),
                        "--out-dir",
                        str(split_dir),
                        "--text-normalization",
                        "official-exact",
                    ]
                ),
                0,
            )
        return source, split_dir / "split.json"

    def _make_args(self, source: Path, split: Path, root: Path) -> list[str]:
        return [
            "make-neurotoken-cache",
            "--source-cache",
            str(source),
            "--split-report",
            str(split),
            "--out",
            str(root / "tokens.npz"),
            "--metadata-out",
            str(root / "tokens.metadata.json"),
            "--summary-json",
            str(root / "tokens.summary.json"),
            "--modality",
            "synthetic",
            "--device-type",
            "synthetic-array",
            "--subject-id",
            "SYN-1",
            "--session-id",
            "SESSION-1",
            "--embedding-dim",
            "12",
            "--max-items",
            "64",
            "--max-output-mb",
            "4",
        ]

    def test_make_and_inspect_neurotoken_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, split = self._source_and_split(root)
            with redirect_stdout(io.StringIO()):
                make_code = main(self._make_args(source, split, root))
                inspect_code = main(
                    [
                        "inspect-neurotoken-cache",
                        "--cache",
                        str(root / "tokens.npz"),
                        "--metadata-out",
                        str(root / "tokens.inspection.json"),
                    ]
                )
            run_summary = json.loads(
                (root / "tokens.summary.json").read_text(encoding="utf-8")
            )
            inspection = json.loads(
                (root / "tokens.inspection.json").read_text(encoding="utf-8")
            )

        self.assertEqual(make_code, 0)
        self.assertEqual(inspect_code, 0)
        self.assertEqual(run_summary["model_runs"], 0)
        self.assertEqual(run_summary["training_runs"], 0)
        self.assertEqual(run_summary["real_data_reads"], 0)
        self.assertEqual(inspection["summary"]["schema_name"], "neurotoken-cache")
        self.assertEqual(inspection["summary"]["tokens_shape"][0], 48)
        self.assertFalse(inspection["metadata"]["representation"]["uses_target_labels"])
        self.assertFalse(
            inspection["metadata"]["streaming_contract"]["end_to_end_latency_measured"]
        )

    def test_make_refuses_to_replace_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, split = self._source_and_split(root)
            args = self._make_args(source, split, root)
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 0)
            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                second_code = main(args)

        self.assertEqual(second_code, 2)
        self.assertIn("Refusing to replace summary JSON", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
