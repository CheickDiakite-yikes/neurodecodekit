import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TemplateBaselineCliTests(unittest.TestCase):
    def test_template_baseline_from_synthetic_cache_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            cache_path = tmp_path / "synthetic.npz"
            predictions = tmp_path / "template_predictions.txt"
            out_json = tmp_path / "template_report.json"
            out_md = tmp_path / "template_report.md"

            with redirect_stdout(io.StringIO()):
                make_code = main(
                    [
                        "make-synthetic-shard",
                        "--out",
                        str(cache_path),
                        "--samples",
                        "64",
                        "--channels",
                        "4",
                        "--times",
                        "12",
                        "--classes",
                        "4",
                    ]
                )
                baseline_code = main(
                    [
                        "template-baseline",
                        "--cache",
                        str(cache_path),
                        "--train-fraction",
                        "0.5",
                        "--out-predictions",
                        str(predictions),
                        "--out-json",
                        str(out_json),
                        "--out-md",
                        str(out_md),
                        "--run-name",
                        "template-smoke",
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
        self.assertEqual(report["baseline"]["kind"], "template-window")
        self.assertEqual(report["baseline"]["strategy"], "nearest-centroid")
        self.assertEqual(report["baseline"]["split_mode"], "single-cache-stratified-holdout")
        self.assertTrue(report["baseline"]["uses_neural_windows"])
        self.assertTrue(report["baseline"]["no_deep_learning"])
        self.assertEqual(report["comparators"]["prior_only"]["baseline"]["kind"], "prior-only")
        self.assertFalse(
            report["comparators"]["prior_only"]["baseline"]["fit_on_eval_targets"]
        )
        self.assertEqual(
            report["comparators"]["prior_only"]["baseline"]["n_train_rows"],
            report["baseline"]["n_train_rows"],
        )
        self.assertEqual(
            report["comparisons"]["template_vs_prior_only"]["n_paired_labels"],
            report["baseline"]["n_eval_rows"],
        )
        self.assertEqual(report["summary"]["primary_metric"], "label_accuracy")
        self.assertEqual(report["summary"]["label_accuracy"], report["baseline"]["eval_accuracy"])
        self.assertIn("template_baseline_uses_neural_windows", report["warnings"])
        self.assertIn("cache:synthetic_cache_not_real_neural_data", report["warnings"])
        self.assertIn("Uses neural windows: `yes`", markdown)
        self.assertIn("## Comparators", markdown)
        self.assertIn("## Paired Comparisons", markdown)

    def test_template_baseline_requires_cache_source(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(["template-baseline"])

        self.assertEqual(code, 2)
        self.assertIn("--cache is required", stderr.getvalue())

    def test_template_baseline_rejects_mixed_cache_modes(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            code = main(
                [
                    "template-baseline",
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


if __name__ == "__main__":
    unittest.main()
