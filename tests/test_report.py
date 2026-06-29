import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.evaluation.report import (
    build_text_report,
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


if __name__ == "__main__":
    unittest.main()
