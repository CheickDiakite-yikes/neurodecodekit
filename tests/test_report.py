import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.evaluation.report import (
    build_text_report,
    compare_paired_label_predictions,
    compare_paired_predictions,
    read_text_rows,
    render_report_markdown,
    write_report_json,
    write_report_markdown,
)


class ReportTests(unittest.TestCase):
    def test_build_text_report_aggregates_metrics_and_examples(self):
        report = build_text_report(
            targets=["HOLA MUNDO", "CASA"],
            predictions=["HOLA MUNCO", "CASA"],
            run_name="unit",
            split="synthetic",
            max_examples=2,
        )

        self.assertEqual(report["summary"]["n_examples"], 2)
        self.assertEqual(report["summary"]["exact_match_count"], 1)
        self.assertAlmostEqual(report["summary"]["exact_match_rate"], 0.5)
        self.assertAlmostEqual(report["summary"]["corpus_cer"], 1 / 14)
        self.assertEqual(report["summary"]["char_edits"], 1)
        self.assertEqual(report["examples"][0]["target"], "HOLA MUNDO")
        self.assertGreater(report["examples"][0]["keyboard_distance"], 0)

    def test_report_rejects_mismatched_rows(self):
        with self.assertRaisesRegex(ValueError, "same number of rows"):
            build_text_report(targets=["A", "B"], predictions=["A"])

    def test_report_writers_create_json_and_markdown(self):
        report = build_text_report(
            targets=["ABC"],
            predictions=["AXC"],
            warnings=["unit_warning"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            json_path = Path(tmp) / "report.json"
            md_path = Path(tmp) / "report.md"
            write_report_json(report, json_path)
            write_report_markdown(report, md_path)

            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            markdown = md_path.read_text(encoding="utf-8")

        self.assertEqual(loaded["schema"]["name"], "neurodecodekit-report")
        self.assertIn("# NeuroDecodeKit Report", markdown)
        self.assertIn("unit_warning", markdown)
        self.assertIn("ABC", markdown)

    def test_read_text_rows_preserves_blank_lines(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "targets.txt"
            path.write_text("A\n\nB\n", encoding="utf-8")

            rows = read_text_rows(path)

        self.assertEqual(rows, ["A", "", "B"])

    def test_render_report_markdown_escapes_table_pipes(self):
        report = build_text_report(targets=["A|B"], predictions=["A B"])
        markdown = render_report_markdown(report)

        self.assertIn("A\\|B", markdown)

    def test_render_report_markdown_includes_baseline_metadata(self):
        report = build_text_report(targets=["A", "B"], predictions=["A", "A"])
        report["baseline"] = {
            "kind": "prior-only",
            "strategy": "most-frequent",
            "n_train_rows": 3,
            "n_eval_rows": 2,
            "vocab_size": 2,
            "top_target": "A",
            "top_count": 2,
        }

        markdown = render_report_markdown(report)

        self.assertIn("## Baseline", markdown)
        self.assertIn("most-frequent", markdown)
        self.assertIn("No neural signal", markdown)

    def test_render_report_markdown_includes_neural_baseline_metadata(self):
        report = build_text_report(targets=["A", "B"], predictions=["A", "A"])
        report["baseline"] = {
            "kind": "tiny-conv-window",
            "strategy": "tiny-conv",
            "model_name": "TinyConvNet",
            "uses_neural_windows": True,
            "uses_deep_learning": True,
            "split_mode": "single-cache-stratified-holdout",
            "n_train_rows": 10,
            "n_eval_rows": 2,
            "n_classes": 2,
            "epochs": 3,
            "learning_rate": 0.01,
            "device": "cpu",
            "train_accuracy": 0.8,
            "eval_accuracy": 0.5,
        }

        markdown = render_report_markdown(report)

        self.assertIn("TinyConvNet", markdown)
        self.assertIn("Uses deep learning: `yes`", markdown)
        self.assertIn("Eval accuracy: `0.5`", markdown)

    def test_paired_comparison_reports_edit_delta_and_uncertainty(self):
        comparison = compare_paired_predictions(
            targets=["AAAA", "BBBB", "CCCC"],
            predictions_a=["AAAA", "BBBX", ""],
            predictions_b=["AAAX", "BBBB", "CCCC"],
            label_a="a",
            label_b="b",
            bootstrap_iterations=500,
            seed=3,
        )

        self.assertEqual(comparison["char_edits_a"], 5)
        self.assertEqual(comparison["char_edits_b"], 1)
        self.assertEqual(comparison["char_edit_delta_a_minus_b"], 4)
        self.assertEqual(comparison["sentence_wins_a"], 1)
        self.assertEqual(comparison["sentence_losses_a"], 2)
        self.assertEqual(len(comparison["paired_bootstrap_delta_ci95"]), 2)

        report = build_text_report(targets=["A"], predictions=["A"])
        report["comparisons"] = {"a_vs_b": comparison}
        markdown = render_report_markdown(report)
        self.assertIn("## Paired Comparisons", markdown)
        self.assertIn("Character-edit delta", markdown)

    def test_paired_label_comparison_uses_exact_class_correctness(self):
        comparison = compare_paired_label_predictions(
            targets=["SPACE", "A", "B", "ENTER"],
            predictions_a=["A", "A", "B", "A"],
            predictions_b=["SPACE", "SPACE", "SPACE", "SPACE"],
            label_a="template",
            label_b="prior",
            bootstrap_iterations=500,
            seed=3,
        )

        self.assertEqual(comparison["metric_kind"], "label_accuracy")
        self.assertEqual(comparison["label_accuracy_a"], 0.5)
        self.assertEqual(comparison["label_accuracy_b"], 0.25)
        self.assertEqual(comparison["paired_label_wins_a"], 2)
        self.assertEqual(comparison["paired_label_losses_a"], 1)

        report = build_text_report(targets=["A"], predictions=["A"])
        report["comparisons"] = {"template_vs_prior": comparison}
        markdown = render_report_markdown(report)
        self.assertIn("Label accuracy delta", markdown)
        self.assertNotIn("Character-edit delta", markdown)


if __name__ == "__main__":
    unittest.main()
