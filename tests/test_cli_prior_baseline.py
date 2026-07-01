import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


class PriorBaselineCliTests(unittest.TestCase):
    def test_prior_baseline_writes_predictions_and_report_from_text_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            train = tmp_path / "train.txt"
            targets = tmp_path / "targets.txt"
            predictions = tmp_path / "predictions.txt"
            out_json = tmp_path / "prior_report.json"
            out_md = tmp_path / "prior_report.md"
            train.write_text("B\nB\nA\n", encoding="utf-8")
            targets.write_text("A\nB\nB\nC\n", encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                code = main(
                    [
                        "prior-baseline",
                        "--targets",
                        str(targets),
                        "--train-targets",
                        str(train),
                        "--out-predictions",
                        str(predictions),
                        "--out-json",
                        str(out_json),
                        "--out-md",
                        str(out_md),
                        "--run-name",
                        "unit-prior",
                        "--split",
                        "unit",
                    ]
                )

            report = json.loads(out_json.read_text(encoding="utf-8"))
            prediction_rows = predictions.read_text(encoding="utf-8").splitlines()
            markdown = out_md.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(prediction_rows, ["B", "B", "B", "B"])
        self.assertEqual(report["run"]["name"], "unit-prior")
        self.assertEqual(report["baseline"]["kind"], "prior-only")
        self.assertEqual(report["baseline"]["strategy"], "most-frequent")
        self.assertEqual(report["baseline"]["top_target"], "B")
        self.assertAlmostEqual(report["summary"]["exact_match_rate"], 0.5)
        self.assertIn("prior_baseline_no_neural_signal", report["warnings"])
        self.assertIn("unit-prior", markdown)

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_prior_baseline_reads_synthetic_cache_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache_path = tmp_path / "synthetic.npz"
            out_json = tmp_path / "prior_report.json"
            out_md = tmp_path / "prior_report.md"

            with redirect_stdout(io.StringIO()):
                make_code = main(
                    [
                        "make-synthetic-shard",
                        "--out",
                        str(cache_path),
                        "--samples",
                        "8",
                        "--channels",
                        "2",
                        "--times",
                        "4",
                        "--classes",
                        "3",
                    ]
                )
                baseline_code = main(
                    [
                        "prior-baseline",
                        "--cache",
                        str(cache_path),
                        "--out-json",
                        str(out_json),
                        "--out-md",
                        str(out_md),
                        "--run-name",
                        "cache-prior",
                        "--split",
                        "synthetic-smoke",
                        "--max-examples",
                        "4",
                    ]
                )

            report = json.loads(out_json.read_text(encoding="utf-8"))

        self.assertEqual(make_code, 0)
        self.assertEqual(baseline_code, 0)
        self.assertEqual(report["summary"]["n_examples"], 8)
        self.assertEqual(report["cache"]["schema_name"], "b2q-mini-cache")
        self.assertEqual(report["baseline"]["kind"], "prior-only")
        self.assertTrue(report["baseline"]["fit_on_eval_targets"])
        self.assertIn("prior_fit_on_eval_targets_for_smoke_only", report["warnings"])
        self.assertIn("cache:synthetic_cache_not_real_neural_data", report["warnings"])

    def test_prior_baseline_requires_predictions_source(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["prior-baseline"])

        self.assertEqual(code, 2)
        self.assertIn("--targets is required", stderr.getvalue())

    def test_prior_baseline_rejects_multiple_training_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            targets = tmp_path / "targets.txt"
            train = tmp_path / "train.txt"
            fake_cache = tmp_path / "train.npz"
            targets.write_text("A\n", encoding="utf-8")
            train.write_text("A\n", encoding="utf-8")
            fake_cache.write_text("not a cache", encoding="utf-8")

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = main(
                    [
                        "prior-baseline",
                        "--targets",
                        str(targets),
                        "--train-targets",
                        str(train),
                        "--train-cache",
                        str(fake_cache),
                    ]
                )

        self.assertEqual(code, 2)
        self.assertIn("use only one", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
