"""Generated-only execution boundary checks; never read participant payloads."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("auxiliary_driver", REPO / "scripts/discover_speech_auxiliary.py")
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)


class AuxiliaryDriverTests(unittest.TestCase):
    def test_exact_plan_selects_only_six_calibrations_from_public_manifest(self):
        manifest = json.loads((REPO / "registries/speech_reproduction_source_manifest.v0.json").read_text())
        plan = json.loads(driver.PLAN.read_text())
        selected = driver.calibration_selection(manifest)
        self.assertEqual([item["path"] for item in selected], plan["calibration_source_paths"])
        self.assertEqual(len(selected), 6)
        self.assertTrue(all("_acq-online_" not in item["path"] for item in selected))
        for item in selected:
            original_path = item["events_path"]
            item["events_path"] = original_path.replace("_acq-calibration_", "_acq-online_")
            with self.assertRaises(ValueError):
                driver.calibration_selection(manifest)
            item["events_path"] = original_path

    def test_single_invocation_refuses_existing_root_before_any_data_access(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(driver, "LOCAL", Path(temporary)), \
                    mock.patch.object(driver, "run") as run:
                with self.assertRaises(FileExistsError):
                    driver.main()
                run.assert_not_called()

    def test_dirty_implementation_refused_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            local = Path(temporary) / "not-created"
            with mock.patch.object(driver, "LOCAL", local), \
                    mock.patch.object(driver, "RESULT", Path(temporary) / "absent.json"), \
                    mock.patch.object(driver.original, "git", return_value=" M changed.py"), \
                    mock.patch.object(driver, "run") as run:
                with self.assertRaises(RuntimeError):
                    driver.main()
                self.assertFalse(local.exists())
                run.assert_not_called()

    def test_failure_marker_is_preserved_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temporary:
            with mock.patch.object(driver, "LOCAL", Path(temporary)):
                budget = mock.Mock(started=driver.time.monotonic())
                driver.failure(ValueError("generated failure"), budget)
                first = (Path(temporary) / "execution_failed.json").read_bytes()
                driver.failure(RuntimeError("later failure"), budget)
                self.assertEqual(first, (Path(temporary) / "execution_failed.json").read_bytes())
                self.assertFalse(json.loads(first)["confirmation_reopened"])

    def test_budget_enforces_time_and_rss_without_numerical_dependencies(self):
        budget = driver.Budget.__new__(driver.Budget)
        budget.started = driver.time.monotonic() - 601
        budget.process = mock.Mock()
        budget.process.memory_info.return_value.rss = 100
        budget.peak_rss = 0
        with self.assertRaisesRegex(RuntimeError, "Ten-minute"):
            budget.check()
        budget.started = driver.time.monotonic()
        budget.process.memory_info.return_value.rss = driver.MAX_RSS + 1
        with self.assertRaisesRegex(RuntimeError, "One-GiB"):
            budget.check()

    def test_bound_metadata_change_refused_without_source_reads(self):
        started = {"plan_sha256": "plan", "source_manifest_sha256": "manifest",
                   "prediction_freeze_sha256": "freeze"}
        with mock.patch.object(driver.original, "sha256", side_effect=["changed"]):
            with self.assertRaisesRegex(ValueError, "plan_sha256"):
                driver.verify_bound_metadata(started)
        with mock.patch.object(driver.original, "sha256", side_effect=[
                "plan", "manifest", "freeze", driver.PRIOR_RESULT_SHA]):
            driver.verify_bound_metadata(started)
