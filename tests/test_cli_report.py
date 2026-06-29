import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


class ReportCliTests(unittest.TestCase):
    def test_report_from_target_prediction_text_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets = Path(tmp) / "targets.txt"
            predictions = Path(tmp) / "predictions.txt"
            out_json = Path(tmp) / "report.json"
            out_md = Path(tmp) / "report.md"
            targets.write_text("HOLA MUNDO\nCASA\n", encoding="utf-8")
            predictions.write_text("HOLA MUNCO\nCASA\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                code = main([
                    "report",
                    "--targets",
                    str(targets),
                    "--predictions",
                    str(predictions),
                    "--out-json",
                    str(out_json),
                    "--out-md",
                    str(out_md),
                    "--run-name",
                    "text-files",
                    "--split",
                    "unit",
                ])

            report = json.loads(out_json.read_text(encoding="utf-8"))
            markdown_exists = out_md.exists()

        self.assertEqual(code, 0)
        self.assertTrue(markdown_exists)
        self.assertEqual(report["summary"]["n_examples"], 2)
        self.assertEqual(report["run"]["name"], "text-files")
        self.assertAlmostEqual(report["summary"]["exact_match_rate"], 0.5)

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_report_from_synthetic_cache_identity_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "synthetic.npz"
            out_json = Path(tmp) / "report.json"
            out_md = Path(tmp) / "report.md"
            with redirect_stdout(io.StringIO()):
                make_code = main([
                    "make-synthetic-shard",
                    "--out",
                    str(cache_path),
                    "--samples",
                    "5",
                    "--channels",
                    "2",
                    "--times",
                    "4",
                    "--classes",
                    "3",
                ])
                report_code = main([
                    "report",
                    "--cache",
                    str(cache_path),
                    "--identity-smoke",
                    "--out-json",
                    str(out_json),
                    "--out-md",
                    str(out_md),
                    "--run-name",
                    "identity-smoke",
                    "--split",
                    "synthetic-smoke",
                    "--max-examples",
                    "3",
                ])

            report = json.loads(out_json.read_text(encoding="utf-8"))
            markdown = out_md.read_text(encoding="utf-8")

        self.assertEqual(make_code, 0)
        self.assertEqual(report_code, 0)
        self.assertEqual(report["summary"]["n_examples"], 5)
        self.assertEqual(report["summary"]["exact_match_rate"], 1.0)
        self.assertEqual(report["cache"]["schema_name"], "b2q-mini-cache")
        self.assertIn("identity_smoke_predictions_equal_targets_not_model_result", report["warnings"])
        self.assertIn("identity-smoke", markdown)

    def test_report_requires_predictions_without_identity_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            targets = Path(tmp) / "targets.txt"
            targets.write_text("A\n", encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(["report", "--targets", str(targets)])

        self.assertEqual(code, 2)
        self.assertIn("--predictions is required", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
