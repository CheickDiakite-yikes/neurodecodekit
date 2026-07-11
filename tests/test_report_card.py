import json
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.cli import main
from neurodecodekit.evaluation.report_card import (
    REPORT_CARD_SCHEMA,
    build_leaderboard,
    validate_report_card,
    validate_report_card_set,
)


def _source_report(*, name: str = "primary", cer: float = 0.25) -> dict:
    return {
        "schema": {"name": "neurodecodekit-report", "version": 1},
        "run": {
            "name": name,
            "created_at_utc": "2026-01-02T03:04:05+00:00",
            "runtime_sec": 1.25,
            "split": "fixture-holdout",
        },
        "summary": {
            "n_examples": 4,
            "corpus_cer": cer,
            "corpus_wer": 0.5,
            "exact_match_rate": 0.5,
            "mean_keyboard_distance": 1.0,
            "char_edits": 2,
            "word_edits": 2,
        },
        "baseline": {
            "kind": "tiny-fixture",
            "model_name": "FixtureNet",
            "causal": False,
            "uses_neural_windows": True,
            "uses_deep_learning": True,
            "parameter_count": 12,
            "runtime_sec": 0.5,
            "peak_rss_bytes": 1000,
        },
        "comparators": {
            "prior_only": {
                "summary": {
                    "n_examples": 4,
                    "corpus_cer": 0.75,
                    "corpus_wer": 1.0,
                    "exact_match_rate": 0.0,
                    "mean_keyboard_distance": 2.0,
                    "char_edits": 6,
                    "word_edits": 4,
                },
                "baseline": {
                    "kind": "prior-only",
                    "strategy": "most-frequent",
                    "uses_neural_windows": False,
                    "uses_deep_learning": False,
                    "fit_on_eval_targets": False,
                },
            }
        },
        "comparisons": {
            "primary_vs_prior": {
                "corpus_cer_delta_a_minus_b": cer - 0.75,
                "char_edit_delta_a_minus_b": -4,
                "paired_bootstrap_delta_ci95": [-0.6, -0.2],
                "bootstrap_probability_a_better": 1.0,
                "n_paired_sentences": 4,
                "interpretation_boundary": "fixture only",
            }
        },
        "cache": {
            "path": "cache/fixture.npz",
            "bytes": 1234,
            "schema_name": "fixture-cache",
            "schema_version": 1,
            "kind": "synthetic_fixture",
            "signals_shape": [4, 2, 8],
            "source_files": {},
        },
    }


def _spec() -> dict:
    shared = {
        "cohort_id": "fixture-holdout",
        "task": "sentence decoding",
        "unit": "sentence",
        "domain": "synthetic",
        "modality": "synthetic",
        "dataset": "unit fixture",
        "subject_scope": "none",
        "split": "held-out fixture rows",
        "comparison_authorized": True,
        "proof_posture": "fixture_backed",
        "allowed_claims": ["pipeline behavior"],
        "prohibited_claims": ["neural decoding performance"],
    }
    return {
        "schema": {"name": "neurodecodekit-leaderboard-spec", "version": 1},
        "leaderboard_id": "unit-fixture",
        "research_sources": [],
        "cohorts": [shared],
        "cards": [
            {
                "run_id": "fixture-net",
                "cohort_id": "fixture-holdout",
                "display_name": "Fixture neural method",
                "method_family": "tiny-ctc",
                "method_name": "FixtureNet",
                "source_report": "reports/source.json",
                "selector": {"kind": "report-primary"},
                "uses_neural_signal": True,
                "uses_deep_learning": True,
                "comparison": {
                    "source_key": "primary_vs_prior",
                    "comparator_run_id": "fixture-prior",
                },
            },
            {
                "run_id": "fixture-prior",
                "cohort_id": "fixture-holdout",
                "display_name": "Fixture prior",
                "method_family": "prior",
                "method_name": "most_frequent",
                "source_report": "reports/source.json",
                "selector": {"kind": "report-comparator", "name": "prior_only"},
                "uses_neural_signal": False,
                "uses_deep_learning": False,
            },
        ],
    }


class ReportCardTests(unittest.TestCase):
    def _write_fixture(self, root: Path) -> Path:
        reports = root / "reports"
        reports.mkdir()
        (reports / "source.json").write_text(
            json.dumps(_source_report(), indent=2) + "\n", encoding="utf-8"
        )
        spec_path = root / "spec.json"
        spec_path.write_text(json.dumps(_spec(), indent=2) + "\n", encoding="utf-8")
        return spec_path

    def test_build_is_deterministic_and_never_loads_signal_arrays(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self._write_fixture(root)
            first = build_leaderboard(
                spec_path=spec_path,
                out_dir=root / "out-a",
                project_root=root,
            )
            build_leaderboard(
                spec_path=spec_path,
                out_dir=root / "out-b",
                project_root=root,
            )
            first_files = {
                path.relative_to(root / "out-a"): path.read_bytes()
                for path in (root / "out-a").rglob("*")
                if path.is_file() and path.name != "audit.json"
            }
            second_files = {
                path.relative_to(root / "out-b"): path.read_bytes()
                for path in (root / "out-b").rglob("*")
                if path.is_file() and path.name != "audit.json"
            }

        self.assertEqual(first_files, second_files)
        self.assertFalse(first["audit"]["signal_array_members_loaded"])
        self.assertEqual(first["audit"]["raw_data_reads"], 0)
        self.assertEqual(first["audit"]["model_runs_triggered"], 0)
        self.assertEqual(first["audit"]["network_fetches"], 0)
        self.assertEqual(first["leaderboard"]["rows"][0]["rank"], 1)
        self.assertFalse(first["leaderboard"]["summary"]["cross_cohort_ranking_performed"])

    def test_malformed_card_and_mixed_versions_are_rejected(self):
        malformed = {
            "schema": dict(REPORT_CARD_SCHEMA),
            "run": {"run_id": "bad"},
        }
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_report_card(malformed)

        valid = self._built_card()
        other = json.loads(json.dumps(valid))
        other["schema"]["version"] = 2
        other["run"]["run_id"] = "other"
        with self.assertRaisesRegex(ValueError, "mixed report-card schema versions"):
            validate_report_card_set([valid, other])

    def test_duplicate_ids_card_cap_and_existing_output_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self._write_fixture(root)
            with self.assertRaisesRegex(ValueError, "cap is 1"):
                build_leaderboard(
                    spec_path=spec_path,
                    out_dir=root / "out",
                    project_root=root,
                    max_cards=1,
                )
            spec = _spec()
            spec["cards"][1]["run_id"] = "fixture-net"
            spec_path.write_text(json.dumps(spec), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate run_id"):
                build_leaderboard(
                    spec_path=spec_path,
                    out_dir=root / "out",
                    project_root=root,
                )

            spec_path.write_text(json.dumps(_spec()), encoding="utf-8")
            (root / "out").mkdir()
            with self.assertRaises(FileExistsError):
                build_leaderboard(
                    spec_path=spec_path,
                    out_dir=root / "out",
                    project_root=root,
                )

    def test_cli_smoke_prints_table_and_writes_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self._write_fixture(root)
            code = main(
                [
                    "build-leaderboard",
                    "--spec",
                    str(spec_path),
                    "--project-root",
                    str(root),
                    "--out-dir",
                    str(root / "out"),
                ]
            )
            audit = json.loads((root / "out" / "audit.json").read_text(encoding="utf-8"))

        self.assertEqual(code, 0)
        self.assertEqual(audit["holdouts_reopened"], 0)
        self.assertLessEqual(audit["total_artifact_bytes"], audit["max_output_bytes"])

    def test_output_must_stay_below_project_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self._write_fixture(root)
            with self.assertRaisesRegex(ValueError, "unsafe output directory"):
                build_leaderboard(
                    spec_path=spec_path,
                    out_dir=root,
                    project_root=root,
                    overwrite=True,
                )
            with self.assertRaisesRegex(ValueError, "escapes project root"):
                build_leaderboard(
                    spec_path=spec_path,
                    out_dir=root.parent / "outside",
                    project_root=root,
                )

    def _built_card(self) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec_path = self._write_fixture(root)
            build_leaderboard(
                spec_path=spec_path,
                out_dir=root / "out",
                project_root=root,
            )
            return json.loads(
                (root / "out" / "cards" / "fixture-net" / "card.json").read_text(
                    encoding="utf-8"
                )
            )


if __name__ == "__main__":
    unittest.main()
