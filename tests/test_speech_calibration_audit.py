"""Generated calibration fixtures only; online paths are intentionally absent."""

from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


def load_audit():
    path = Path(__file__).resolve().parents[1] / "scripts/audit_speech_calibration.py"
    spec = importlib.util.spec_from_file_location("speech_calibration_audit_test", path)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(os.environ), mock.patch.object(sys, "path", list(sys.path)):
        spec.loader.exec_module(module)
    return module


audit = load_audit()


class CalibrationAuditTests(unittest.TestCase):
    def setUp(self):
        if not all(importlib.util.find_spec(name) for name in ("numpy", "sklearn")):
            self.skipTest("optional numerical dependencies unavailable")
        try:
            import numpy as np
            from neurodecodekit.models.speech_reference import calibration_folds
        except ImportError:
            self.skipTest("optional numerical dependencies unavailable")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source, self.reports = self.root / "source", self.root / "reports"
        self.source.mkdir()
        self.reports.mkdir()
        self.manifest = {"source_commit": audit.original.SOURCE_COMMIT, "files": []}
        for index, (person, condition) in enumerate(
            (p, c) for p in ("sub-1", "sub-2", "sub-3") for c in ("minimallyovert", "covert")
        ):
            counts = [20] * 5 if index < 5 else [37, 28, 13, 8, 14]
            labels = np.repeat(np.arange(5), counts)
            stem = f"{person}_ses-generated_task-{condition}_acq-calibration_run-01"
            name = f"{person}/ses-generated/eeg/{stem}_events.tsv"
            header = "onset\tduration\ttrial_type\tvalue\tsession_type\n"
            words = ("green", "magenta", "orange", "violet", "yellow")
            rows = [f"{i * 11.25}\t6.25\t{words[y]}\t{y}\tcalibration\n" for i, y in enumerate(labels)]
            payload = (header + "".join(rows)).encode()
            (self.source / name).parent.mkdir(parents=True, exist_ok=True)
            (self.source / name).write_bytes(payload)
            self.manifest["files"].append({
                "path": f"{person}/ses-generated/eeg/{stem}_eeg.edf", "events_path": name,
                "events_bytes": len(payload),
                "events_git_blob_sha": hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest(),
            })
            self.manifest["files"].append({"path": f"{person}/ses-generated/eeg/"
                f"{person}_ses-generated_task-{condition}_acq-online_run-01_eeg.edf",
                "events_path": "FORBIDDEN_DO_NOT_OPEN"})
            if index < 5:
                _, splits = calibration_folds(labels)
                report = {"model": {"folds": [{"validation_indices": v.tolist()} for _, v in splits]}}
                (self.reports / f"{person}_ses-generated_{condition}.json").write_text(json.dumps(report))

    def test_all_six_sparse_folds_and_prior_indices_without_online_reads(self):
        result = audit.audit_calibrations(self.manifest, self.source, self.reports)
        self.assertTrue(result["all_six_eligible"])
        self.assertEqual(result["online_event_rows_read"], 0)
        self.assertEqual(result["pairs"][-1]["class_counts"], [37, 28, 13, 8, 14])
        self.assertEqual(len(result["pairs"][-1]["split_warnings"]), 1)
        self.assertEqual(sum(p["previous_fold_indices_match"] is True for p in result["pairs"]), 5)
        # Receipt is aggregate only: never disclose row labels or fold index assignments.
        self.assertNotIn("validation_indices", json.dumps(result))
        self.assertNotIn("calibration_labels", json.dumps(result))

    def test_source_identity_change_refused(self):
        self.manifest["files"][0]["events_git_blob_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "source identity"):
            audit.audit_calibrations(self.manifest, self.source, self.reports)

    def test_online_sidecar_substitution_refused_before_open(self):
        for name in ("missing_acq-online_events.tsv", "folder_acq-calibration_/record_acq-online_events.tsv",
                     "wrong_acq-calibration_events.tsv"):
            with self.subTest(path=name):
                self.manifest["files"][0]["events_path"] = name
                with self.assertRaisesRegex(ValueError, "Only calibration"):
                    audit.audit_calibrations(self.manifest, self.source, self.reports)

    def test_missing_pair_and_wrong_source_refused(self):
        changed = deepcopy(self.manifest)
        changed["files"] = changed["files"][:-2]
        with self.assertRaisesRegex(ValueError, "six original"):
            audit.audit_calibrations(changed, self.source, self.reports)
        changed = deepcopy(self.manifest)
        changed["source_commit"] = "unapproved"
        with self.assertRaisesRegex(ValueError, "source commit"):
            audit.audit_calibrations(changed, self.source, self.reports)

    def test_changed_previous_indices_refused(self):
        path = self.reports / "sub-1_ses-generated_minimallyovert.json"
        data = json.loads(path.read_text())
        data["model"]["folds"][0]["validation_indices"] = [99]
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "previously trained"):
            audit.audit_calibrations(self.manifest, self.source, self.reports)


if __name__ == "__main__":
    unittest.main()
