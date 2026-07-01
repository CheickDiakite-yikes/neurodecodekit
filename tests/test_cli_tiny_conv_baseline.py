import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


class TinyConvBaselineCliValidationTests(unittest.TestCase):
    def test_tiny_conv_baseline_requires_cache_source(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["tiny-conv-baseline"])

        self.assertEqual(code, 2)
        self.assertIn("--cache is required", stderr.getvalue())

    def test_tiny_conv_baseline_rejects_mixed_cache_modes(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(
                [
                    "tiny-conv-baseline",
                    "--cache",
                    "one.npz",
                    "--train-cache",
                    "train.npz",
                    "--eval-cache",
                    "eval.npz",
                ]
            )

        self.assertEqual(code, 2)
        self.assertIn("single-cache holdout", stderr.getvalue())


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
@unittest.skipIf(importlib.util.find_spec("torch"), "Torch installed; missing-dependency path not active")
class TinyConvBaselineCliMissingDependencyTests(unittest.TestCase):
    def test_tiny_conv_baseline_missing_ml_dependency_is_helpful(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "synthetic.npz"

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
                        "2",
                    ]
                )

            stderr = io.StringIO()
            with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                baseline_code = main(["tiny-conv-baseline", "--cache", str(cache_path)])

        self.assertEqual(make_code, 0)
        self.assertEqual(baseline_code, 2)
        self.assertIn("pip install -e '.[ml]'", stderr.getvalue())


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TinyConvBaselineCliTrainingTests(unittest.TestCase):
    def test_tiny_conv_baseline_from_synthetic_cache_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache_path = tmp_path / "synthetic.npz"
            predictions = tmp_path / "tiny_conv_predictions.txt"
            out_json = tmp_path / "tiny_conv_report.json"
            out_md = tmp_path / "tiny_conv_report.md"

            with redirect_stdout(io.StringIO()):
                make_code = main(
                    [
                        "make-synthetic-shard",
                        "--out",
                        str(cache_path),
                        "--samples",
                        "96",
                        "--channels",
                        "4",
                        "--times",
                        "12",
                        "--classes",
                        "2",
                    ]
                )
                baseline_code = main(
                    [
                        "tiny-conv-baseline",
                        "--cache",
                        str(cache_path),
                        "--train-fraction",
                        "0.75",
                        "--epochs",
                        "30",
                        "--learning-rate",
                        "0.02",
                        "--out-predictions",
                        str(predictions),
                        "--out-json",
                        str(out_json),
                        "--out-md",
                        str(out_md),
                        "--run-name",
                        "tiny-conv-smoke",
                        "--split",
                        "synthetic-holdout",
                    ]
                )

            report = json.loads(out_json.read_text(encoding="utf-8"))
            prediction_rows = predictions.read_text(encoding="utf-8").splitlines()
            markdown = out_md.read_text(encoding="utf-8")

        self.assertEqual(make_code, 0)
        self.assertEqual(baseline_code, 0)
        self.assertEqual(len(prediction_rows), report["summary"]["n_examples"])
        self.assertEqual(report["baseline"]["kind"], "tiny-conv-window")
        self.assertTrue(report["baseline"]["uses_deep_learning"])
        self.assertGreaterEqual(report["baseline"]["eval_accuracy"], 0.5)
        self.assertIn("tiny_conv_baseline_uses_neural_windows", report["warnings"])
        self.assertIn("Uses deep learning: `yes`", markdown)


if __name__ == "__main__":
    unittest.main()
