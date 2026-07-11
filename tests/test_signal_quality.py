from __future__ import annotations

import copy
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from neurodecodekit.cli import main
from neurodecodekit.preprocess.signal_quality import (
    ARTIFACT_JSON,
    ARTIFACT_MARKDOWN,
    SignalQualityLimits,
    inspect_signal_quality,
    load_signal_quality_report,
    validate_signal_quality_report,
    write_signal_quality_artifacts,
)
from neurodecodekit.training.synthetic_signal_quality import (
    FIXTURE_SET_CAP_BYTES,
    SAFE_ANNOTATION_SENTINEL,
    load_signal_quality_fixture_manifest,
    make_signal_quality_fixtures,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "registries" / "signal_quality_contract.v0.json"
_TEMP: tempfile.TemporaryDirectory[str] | None = None
FIXTURE_ROOT: Path
MANIFEST_PATH: Path
MANIFEST: dict
GENERATION_SUMMARY: dict


def setUpModule() -> None:
    global _TEMP, FIXTURE_ROOT, MANIFEST_PATH, MANIFEST, GENERATION_SUMMARY
    missing = [
        name for name in ("mne", "numpy", "scipy") if importlib.util.find_spec(name) is None
    ]
    if missing:
        raise unittest.SkipTest(
            "RW2 signal-quality tests require the optional neuro dependencies: "
            + ", ".join(missing)
        )
    _TEMP = tempfile.TemporaryDirectory()
    FIXTURE_ROOT = Path(_TEMP.name) / "rw2-fixtures"
    GENERATION_SUMMARY = make_signal_quality_fixtures(
        FIXTURE_ROOT,
        contract_path=CONTRACT,
    )
    MANIFEST_PATH = FIXTURE_ROOT / "signal_quality_fixtures.json"
    MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def tearDownModule() -> None:
    if _TEMP is not None:
        _TEMP.cleanup()


def fixture_row(fixture_id: str) -> dict:
    return next(row for row in MANIFEST["fixtures"] if row["fixture_id"] == fixture_id)


def inspect_fixture(fixture_id: str, *, limits: SignalQualityLimits | None = None):
    row = fixture_row(fixture_id)
    return inspect_signal_quality(
        FIXTURE_ROOT / row["source_path"],
        intake_report_path=FIXTURE_ROOT / row["intake_report_path"],
        fixture_manifest_path=MANIFEST_PATH,
        contract_path=CONTRACT,
        limits=limits,
    )


class SignalQualityTests(unittest.TestCase):
    def test_fixture_manifest_is_deterministic_complete_and_bounded(self):
        summary = load_signal_quality_fixture_manifest(MANIFEST_PATH)

        self.assertEqual(summary["fixture_count"], 40)
        self.assertEqual(summary["readable_fixture_count"], 38)
        self.assertEqual(summary["refusal_fixture_count"], 2)
        self.assertEqual(summary["skipped_export_count"], 4)
        self.assertEqual(
            set(summary["format_families"]),
            {"brainvision", "edf_or_edf_plus", "bdf", "eeglab", "fif", "bids"},
        )
        self.assertLess(GENERATION_SUMMARY["total_bytes"], FIXTURE_SET_CAP_BYTES)
        self.assertTrue(GENERATION_SUMMARY["output_cap_passed"])
        self.assertEqual(GENERATION_SUMMARY["real_data_reads"], 0)
        self.assertEqual(GENERATION_SUMMARY["target_label_values_emitted_or_used"], 0)
        self.assertEqual(GENERATION_SUMMARY["model_runs"], 0)
        self.assertEqual(GENERATION_SUMMARY["training_runs"], 0)
        self.assertEqual(GENERATION_SUMMARY["network_calls"], 0)

        with tempfile.TemporaryDirectory() as tmp:
            replay_root = Path(tmp) / "replay"
            make_signal_quality_fixtures(replay_root, contract_path=CONTRACT)
            replay_manifest = (replay_root / MANIFEST_PATH.name).read_bytes()
        self.assertEqual(MANIFEST_PATH.read_bytes(), replay_manifest)

    def test_all_registered_readers_and_refusals_match_the_frozen_contract(self):
        passed = 0
        refused = 0
        families: set[str] = set()
        for row in MANIFEST["fixtures"]:
            if row["expected_refusal"] is not None:
                with self.assertRaisesRegex(ValueError, f"^{row['expected_refusal']}$"):
                    inspect_fixture(row["fixture_id"])
                refused += 1
                continue
            result = inspect_fixture(row["fixture_id"])
            report = result.report
            validate_signal_quality_report(report)
            passed += 1
            families.add(row["format_family"])
            self.assertFalse(report["reader"]["preloaded_after_open"])
            self.assertTrue(report["no_mutation"]["passed"])
            self.assertEqual(report["compatibility"]["current_level"], 2)
            self.assertEqual(report["access_counts"]["real_data_reads"], 0)
            self.assertEqual(report["access_counts"]["consumed_cache_reads"], 0)
            self.assertEqual(
                report["access_counts"]["target_label_values_emitted_or_used"], 0
            )
            self.assertEqual(report["access_counts"]["model_runs"], 0)
            self.assertEqual(report["access_counts"]["training_runs"], 0)
            self.assertEqual(report["access_counts"]["network_calls"], 0)
            self.assertFalse(report["quality"]["automatic_cleaning_performed"])
        self.assertEqual(passed, 38)
        self.assertEqual(refused, 2)
        self.assertEqual(families, set(MANIFEST["generation"]["format_families"]))

    def test_deterministic_report_artifacts_and_strict_roundtrip(self):
        first = inspect_fixture("clean_multitype_continuous__fif")
        second = inspect_fixture("clean_multitype_continuous__fif")
        self.assertEqual(first.report, second.report)
        self.assertEqual(first.report["quality"]["structural_warnings"], [])

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first_summary = write_signal_quality_artifacts(first, root / "a")
            second_summary = write_signal_quality_artifacts(second, root / "b")
            first_json = (root / "a" / ARTIFACT_JSON).read_bytes()
            first_markdown = (root / "a" / ARTIFACT_MARKDOWN).read_bytes()
            self.assertEqual(first_json, (root / "b" / ARTIFACT_JSON).read_bytes())
            self.assertEqual(first_markdown, (root / "b" / ARTIFACT_MARKDOWN).read_bytes())
            loaded = load_signal_quality_report(root / "a" / ARTIFACT_JSON)

        self.assertTrue(loaded["audit_validated"])
        self.assertEqual(loaded["compatibility_level"], 2)
        self.assertLess(first_summary["total_output_bytes"], 4 * 1024 * 1024)
        self.assertLess(second_summary["total_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(first_summary["real_data_reads"], 0)
        self.assertEqual(first_summary["target_label_values_emitted_or_used"], 0)
        self.assertFalse(first_summary["producer_causal"])
        self.assertFalse(first_summary["end_to_end_latency_measured"])

    def test_injected_psd_peaks_and_line_ratios_are_descriptive_only(self):
        report = inspect_fixture("line_components_50_60_hz__fif").report
        rows = report["quality"]["welch_psd"]["per_channel_window"]
        fp1 = [row for row in rows if row["channel_name"] == "Fp1"]
        fp2 = [row for row in rows if row["channel_name"] == "Fp2"]

        self.assertTrue(all(row["peak_frequency_hz"] == 50.0 for row in fp1))
        self.assertTrue(all(row["peak_frequency_hz"] == 60.0 for row in fp2))
        self.assertTrue(
            all(row["line_to_sideband_ratio"]["50_hz"] is not None for row in fp1)
        )
        self.assertTrue(
            all(row["line_to_sideband_ratio"]["60_hz"] is not None for row in fp2)
        )
        self.assertIsNone(
            report["quality"]["welch_psd"]["method"]["generic_pass_fail_threshold"]
        )
        self.assertEqual(report["quality"]["structural_warnings"], [])
        self.assertFalse(report["quality"]["annotate_amplitude_used"])

    def test_flat_nonfinite_outlier_and_annotation_semantics(self):
        flat = inspect_fixture("exact_flat_channel__fif").report
        self.assertEqual(
            flat["quality"]["structural_warnings"],
            ["exact_constant_channel_window"],
        )
        self.assertEqual(flat["recording"]["source_bads"], [])

        nonfinite = inspect_fixture("nonfinite_samples__fif").report
        self.assertEqual(
            nonfinite["quality"]["structural_warnings"],
            ["nonfinite_samples_present"],
        )
        affected = [
            row
            for row in nonfinite["quality"]["time_domain"]["per_channel_window"]
            if row["channel_name"] == "Fp2" and row["window_id"] == 0
        ][0]
        self.assertLess(affected["metrics"]["finite_fraction"], 1.0)
        self.assertIsNone(affected["metrics"]["centered_rms"])

        outlier = inspect_fixture("relative_rms_outlier__fif").report
        self.assertEqual(
            [row["channel_name"] for row in outlier["quality"]["advisory_candidates"]],
            ["P4"],
        )
        self.assertFalse(
            outlier["quality"]["advisory_candidates"][0]["declares_bad_channel"]
        )
        self.assertEqual(outlier["recording"]["source_bads"], [])

        annotated = inspect_fixture("safe_nonsemantic_annotations__fif").report
        encoded = json.dumps(annotated, sort_keys=True)
        self.assertEqual(annotated["recording"]["events"]["status"], "present_aggregate_only")
        self.assertEqual(annotated["recording"]["events"]["count"], 1)
        self.assertEqual(annotated["recording"]["events"]["unique_description_count"], 1)
        self.assertNotIn(SAFE_ANNOTATION_SENTINEL, encoded)
        self.assertNotIn(str(FIXTURE_ROOT), encoded)

    def test_strict_binding_and_resource_caps_refuse_before_overclaiming(self):
        source_row = fixture_row("clean_multitype_continuous__fif")
        wrong_intake = fixture_row("clean_multitype_continuous__brainvision")
        with self.assertRaisesRegex(ValueError, "strict_synthetic_fixture_binding_failed"):
            inspect_signal_quality(
                FIXTURE_ROOT / source_row["source_path"],
                intake_report_path=FIXTURE_ROOT / wrong_intake["intake_report_path"],
                fixture_manifest_path=MANIFEST_PATH,
                contract_path=CONTRACT,
            )

        with self.assertRaisesRegex(ValueError, "channel_count_exceeds_registered_cap"):
            inspect_fixture(
                "clean_multitype_continuous__fif",
                limits=SignalQualityLimits(max_channels=4),
            )
        with self.assertRaisesRegex(
            ValueError,
            "bounded_windows_below_registered_minimum_samples",
        ):
            inspect_fixture(
                "clean_multitype_continuous__fif",
                limits=SignalQualityLimits(max_channel_sample_values=3000),
            )

        small_output = inspect_fixture(
            "clean_multitype_continuous__fif",
            limits=SignalQualityLimits(max_output_bytes=1024),
        )
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "too-small"
            with self.assertRaisesRegex(ValueError, "exceed output cap"):
                write_signal_quality_artifacts(small_output, output)
            self.assertFalse(output.exists())

        with self.assertRaisesRegex(ValueError, "configured limit exceeds frozen contract"):
            inspect_fixture(
                "clean_multitype_continuous__fif",
                limits=SignalQualityLimits(max_channels=513),
            )

    def test_malformed_reports_tampering_collision_and_privacy_are_refused(self):
        result = inspect_fixture("clean_multitype_continuous__fif")
        report = result.report

        tampered = copy.deepcopy(report)
        tampered["target_text"] = "forbidden"
        with self.assertRaisesRegex(ValueError, "forbidden fields"):
            validate_signal_quality_report(tampered)

        tampered = copy.deepcopy(report)
        tampered["access_counts"]["model_runs"] = 1
        with self.assertRaisesRegex(ValueError, "forbidden access count"):
            validate_signal_quality_report(tampered)

        tampered = copy.deepcopy(report)
        tampered["source"]["selected_path"] = "/private/source.fif"
        with self.assertRaisesRegex(ValueError, "absolute path"):
            validate_signal_quality_report(tampered)

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            write_signal_quality_artifacts(result, output)
            unrelated = output / "keep.txt"
            unrelated.write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "nonempty output directory"):
                write_signal_quality_artifacts(result, output)
            write_signal_quality_artifacts(result, output, overwrite=True)
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep")

            markdown = output / ARTIFACT_MARKDOWN
            payload = bytearray(markdown.read_bytes())
            payload[0] = ord("!")
            markdown.write_bytes(payload)
            with self.assertRaisesRegex(ValueError, "Markdown artifact hash mismatch"):
                load_signal_quality_report(output / ARTIFACT_JSON)

    def test_base_module_imports_without_heavy_dependencies(self):
        script = """
import sys
import neurodecodekit.preprocess.signal_quality
for name in ('mne', 'numpy', 'scipy', 'mne_bids', 'torch'):
    assert name not in sys.modules, name
"""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT / "src")
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_cli_fixture_inspect_signal_roundtrip_and_collision(self):
        fixture = fixture_row("clean_multitype_continuous__fif")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "quality"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                fixture_code = main(
                    [
                        "inspect-signal-quality-fixtures",
                        "--manifest",
                        str(MANIFEST_PATH),
                    ]
                )
            fixture_summary = json.loads(stdout.getvalue())

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                create_code = main(
                    [
                        "inspect-signal-quality",
                        "--path",
                        str(FIXTURE_ROOT / fixture["source_path"]),
                        "--intake-report",
                        str(FIXTURE_ROOT / fixture["intake_report_path"]),
                        "--fixture-manifest",
                        str(MANIFEST_PATH),
                        "--contract",
                        str(CONTRACT),
                        "--out-dir",
                        str(output),
                    ]
                )
            create_summary = json.loads(stdout.getvalue())

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                inspect_code = main(
                    [
                        "inspect-signal-quality-report",
                        "--report",
                        str(output / ARTIFACT_JSON),
                    ]
                )
            inspect_summary = json.loads(stdout.getvalue())

            stderr = io.StringIO()
            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                collision_code = main(
                    [
                        "inspect-signal-quality",
                        "--path",
                        str(FIXTURE_ROOT / fixture["source_path"]),
                        "--intake-report",
                        str(FIXTURE_ROOT / fixture["intake_report_path"]),
                        "--fixture-manifest",
                        str(MANIFEST_PATH),
                        "--contract",
                        str(CONTRACT),
                        "--out-dir",
                        str(output),
                    ]
                )

        self.assertEqual(fixture_code, 0)
        self.assertEqual(create_code, 0)
        self.assertEqual(inspect_code, 0)
        self.assertEqual(collision_code, 2)
        self.assertEqual(fixture_summary["fixture_count"], 40)
        self.assertEqual(create_summary["compatibility_level"], 2)
        self.assertTrue(create_summary["output_cap_passed"])
        self.assertTrue(inspect_summary["audit_validated"])
        self.assertIn("nonempty output directory", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
