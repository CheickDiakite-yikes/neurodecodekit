"""Recovery gates using generated metadata and temporary files only.

No real source, checkpoint, prediction or target file is opened. Network and
Git access are mocked, and neither training nor scientific scoring is invoked.
"""

from copy import deepcopy
from contextlib import ExitStack
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from neurodecodekit.evaluation.speech_reproduction import COMPACT_ARMS


def _load_recovery():
    script = Path(__file__).resolve().parents[1] / "scripts/recover_speech_reproduction.py"
    spec = importlib.util.spec_from_file_location("speech_recovery_test_driver", script)
    module = importlib.util.module_from_spec(spec)
    # The executable imports its sibling and sets numerical thread variables.
    # Preserve the test process's environment and import search order.
    with mock.patch.dict(os.environ), mock.patch.object(sys, "path", list(sys.path)):
        spec.loader.exec_module(module)
    return module


recovery = _load_recovery()


def _complete_selection():
    """Invent a 13-recording, six-pair roster with no scientific values."""
    files, reports = [], []
    for index, (person, condition) in enumerate(
        (person, condition)
        for person in ("sub-1", "sub-2", "sub-3")
        for condition in ("minimallyovert", "covert")
    ):
        session = "ses-generated"
        extraction = []
        roles = ["calibration", "online"] + (["online"] if index == 0 else [])
        for run, role in enumerate(roles):
            stem = f"{person}_{session}_task-{condition}_acq-{role}_run-{run}"
            files.append({"path": f"{person}/{session}/eeg/{stem}_eeg.edf",
                          "events_path": f"{person}/{session}/eeg/{stem}_events.tsv"})
            extraction.append({"recording_id": stem,
                               "private_targets_sha256": None if run == 0 else "a" * 64})
        reports.append({
            "pair_id": f"{person}_{session}_{condition}",
            "calibration_trials": 100,
            "evaluation_trials": 91 if index == 0 else 50,
            "extraction": extraction,
            "model": {"folds": [{"fold": fold, "epochs": 100} for fold in range(10)]},
            "checkpoint_reuse": {"reused_fits": 10 if index < 5 else 0},
            "new_reference_fits": 0 if index < 5 else 10,
        })
    manifest = {"source_commit": recovery.original.SOURCE_COMMIT, "files": files}
    freeze = {"pairs": reports, "n_evaluation_trials": 341,
              "arms": [*COMPACT_ARMS, "eegnet_reference"]}
    return manifest, freeze


class RecoveryCompletenessTests(unittest.TestCase):
    def setUp(self):
        self.manifest, self.freeze = _complete_selection()

    def test_complete_original_selection_is_accepted(self):
        recovery.validate_complete(self.freeze, self.manifest)
        self.assertEqual(len(self.manifest["files"]), 13)
        self.assertEqual(len(recovery.expected_pairs(self.manifest)), 6)

    def test_missing_person_or_condition_is_refused(self):
        self.manifest["files"] = self.manifest["files"][:-2]
        with self.assertRaisesRegex(ValueError, "all three people and both conditions"):
            recovery.expected_pairs(self.manifest)

    def test_partial_duplicate_and_reordered_pairs_are_refused(self):
        for mutation in ("missing", "duplicate", "reordered"):
            with self.subTest(mutation=mutation):
                freeze = deepcopy(self.freeze)
                if mutation == "missing":
                    freeze["pairs"].pop()
                elif mutation == "duplicate":
                    freeze["pairs"][-1] = deepcopy(freeze["pairs"][0])
                else:
                    freeze["pairs"].reverse()
                with self.assertRaisesRegex(ValueError, "pair freeze"):
                    recovery.validate_complete(freeze, self.manifest)

    def test_missing_duplicate_and_reordered_recordings_are_refused(self):
        for mutation in ("missing", "duplicate", "reordered"):
            with self.subTest(mutation=mutation):
                freeze = deepcopy(self.freeze)
                records = freeze["pairs"][0]["extraction"]
                if mutation == "missing":
                    records.pop()
                elif mutation == "duplicate":
                    records[-1] = deepcopy(records[0])
                else:
                    records.reverse()
                with self.assertRaisesRegex(ValueError, "recording freeze"):
                    recovery.validate_complete(freeze, self.manifest)

    def test_each_registered_arm_is_required(self):
        for arm in self.freeze["arms"]:
            with self.subTest(arm=arm):
                freeze = deepcopy(self.freeze)
                freeze["arms"].remove(arm)
                with self.assertRaisesRegex(ValueError, "comparator"):
                    recovery.validate_complete(freeze, self.manifest)

    def test_calibration_and_evaluation_totals_must_be_complete(self):
        for field in ("n_evaluation_trials", "calibration_trials", "evaluation_trials"):
            with self.subTest(field=field):
                freeze = deepcopy(self.freeze)
                container = freeze if field == "n_evaluation_trials" else freeze["pairs"][-1]
                container[field] -= 1
                with self.assertRaisesRegex(ValueError, "trial selection"):
                    recovery.validate_complete(freeze, self.manifest)

    def test_all_ten_full_training_folds_are_required(self):
        for mutation in ("missing_fold", "shortened_epoch"):
            with self.subTest(mutation=mutation):
                freeze = deepcopy(self.freeze)
                folds = freeze["pairs"][-1]["model"]["folds"]
                if mutation == "missing_fold":
                    folds.pop()
                else:
                    folds[-1]["epochs"] = 99
                with self.assertRaisesRegex(ValueError, "reference training"):
                    recovery.validate_complete(freeze, self.manifest)

    def test_fifty_reused_and_ten_new_fits_are_required(self):
        for mutation in ("missing_reuse", "extra_new_fit"):
            with self.subTest(mutation=mutation):
                freeze = deepcopy(self.freeze)
                if mutation == "missing_reuse":
                    freeze["pairs"][0]["checkpoint_reuse"]["reused_fits"] = 9
                else:
                    freeze["pairs"][-1]["new_reference_fits"] = 11
                with self.assertRaisesRegex(ValueError, "fifty-plus-ten"):
                    recovery.validate_complete(freeze, self.manifest)


class RecoveryTemporaryStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="speech-recovery-generated-")
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.local, self.old = self.repo / "recovery", self.repo / "original"
        self.failed = self.repo / "failed-recovery"
        self.local.mkdir()
        self.old.mkdir()
        self.failed.mkdir()
        self.manifest_path = self.repo / "manifest.json"
        self.freeze_path = self.repo / "freeze.json"
        self.result_path = self.repo / "result.json"
        self.audit_path = self.repo / "calibration-audit.json"
        paths = {"REPO": self.repo, "LOCAL": self.local, "OLD": self.old,
                 "FAILED_RECOVERY": self.failed, "CALIBRATION_AUDIT": self.audit_path,
                 "MANIFEST": self.manifest_path, "FREEZE": self.freeze_path,
                 "RESULT": self.result_path}
        for name, path in paths.items():
            patcher = mock.patch.object(recovery, name, path)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.network = mock.patch.object(recovery.original, "request",
                                         side_effect=AssertionError("No network in generated tests"))
        self.network.start()
        self.addCleanup(self.network.stop)
        self.git = mock.patch.object(recovery, "git",
                                     side_effect=AssertionError("No real Git in generated tests"))
        self.git.start()
        self.addCleanup(self.git.stop)
        self.failed_guard = mock.patch.object(recovery, "verify_failed_recovery")
        self.failed_guard.start()
        self.addCleanup(self.failed_guard.stop)
        self.manifest, self.freeze = _complete_selection()
        self.started = {"started_unix": 1000.0, "deadline_seconds": 7200,
                        "code_commit": "generated-code", "original_failure_sha256": recovery.FAILURE_SHA,
                        "failed_recovery_failure_sha256": recovery.FAILED_RECOVERY_SHA}
        recovery.write_json(self.audit_path, {"generated_only": True})
        self.started["calibration_audit_sha256"] = recovery.sha256(self.audit_path)
        recovery.write_json(self.manifest_path, self.manifest)
        recovery.write_json(self.local / "started.json", self.started)
        recovery.write_json(self.local / "preflight.json", {"generated_only": True})
        self.freeze.update({
            "execution_root": "recovery", "predictions_relative_path": "recovery/predictions.npz",
            "original_failure_sha256": recovery.FAILURE_SHA,
            "failed_recovery_failure_sha256": recovery.FAILED_RECOVERY_SHA,
            "failed_recovery_artifacts_sha256": {"fake-previous": "hash"},
            "calibration_audit_sha256": recovery.sha256(self.audit_path),
            "maximum_total_seconds": 7200, "code_commit": self.started["code_commit"],
            "started_sha256": recovery.sha256(self.local / "started.json"),
            "source_manifest_sha256": recovery.sha256(self.manifest_path),
            "preflight_sha256": recovery.sha256(self.local / "preflight.json"),
            "status": "predictions_locked_unscored", "original_artifacts_sha256": {"fake": "hash"},
        })

    def ready(self):
        with mock.patch.object(recovery, "verify_original") as original_check, \
                mock.patch.object(recovery, "verify_inventory") as inventory_check, \
                mock.patch.object(recovery, "verify_failed_inventory") as failed_inventory_check, \
                mock.patch.object(recovery.time, "time", return_value=1001.0):
            recovery.validate_score_ready(self.freeze, self.started)
        original_check.assert_called_once_with()
        inventory_check.assert_called_once_with(self.freeze["original_artifacts_sha256"])
        failed_inventory_check.assert_called_once_with(self.freeze["failed_recovery_artifacts_sha256"])

    def test_ready_gate_accepts_only_complete_bound_generated_state(self):
        self.ready()
        self.assertFalse((self.local / "scoring_consumed.json").exists())
        self.assertFalse((self.local / "private_targets").exists())

    def test_failed_or_consumed_state_refuses_before_original_access(self):
        for marker in ("execution_failed.json", "scoring_consumed.json"):
            with self.subTest(marker=marker):
                path = self.local / marker
                path.write_text("generated only", encoding="utf-8")
                with mock.patch.object(recovery, "verify_original") as original_check:
                    with self.assertRaisesRegex(RuntimeError, "failed or scoring already consumed"):
                        recovery.validate_score_ready(self.freeze, self.started)
                original_check.assert_not_called()
                path.unlink()

    def test_wrong_root_prediction_path_or_lineage_refuses(self):
        for field in ("execution_root", "predictions_relative_path", "original_failure_sha256",
                      "failed_recovery_failure_sha256"):
            with self.subTest(field=field):
                freeze = deepcopy(self.freeze)
                freeze[field] = "different"
                with mock.patch.object(recovery, "verify_original"), \
                        mock.patch.object(recovery, "sha256") as hash_read:
                    with self.assertRaisesRegex(ValueError, "root or failed-run lineage"):
                        recovery.validate_score_ready(freeze, self.started)
                hash_read.assert_not_called()

    def test_wall_deadline_includes_gap_between_predict_and_score(self):
        with mock.patch.object(recovery, "verify_original"), \
                mock.patch.object(recovery, "sha256") as hash_read, \
                mock.patch.object(recovery.time, "time", return_value=8200.0):
            with self.assertRaisesRegex(RuntimeError, "deadline expired or changed"):
                recovery.validate_score_ready(self.freeze, self.started)
        hash_read.assert_not_called()

    def test_no_larger_deadline_can_be_smuggled_into_started_or_freeze(self):
        for target, field in (("started", "deadline_seconds"), ("freeze", "maximum_total_seconds")):
            with self.subTest(target=target):
                started, freeze = deepcopy(self.started), deepcopy(self.freeze)
                (started if target == "started" else freeze)[field] = 21600
                with mock.patch.object(recovery, "verify_original"), \
                        mock.patch.object(recovery.time, "time", return_value=1001.0):
                    with self.assertRaisesRegex(RuntimeError, "deadline expired or changed"):
                        recovery.validate_score_ready(freeze, started)

    def test_changed_start_manifest_preflight_or_code_refuses_before_inventory(self):
        for field in ("started_sha256", "source_manifest_sha256", "preflight_sha256", "code_commit",
                      "calibration_audit_sha256"):
            with self.subTest(field=field):
                freeze = deepcopy(self.freeze)
                freeze[field] = "different"
                with mock.patch.object(recovery, "verify_original"), \
                        mock.patch.object(recovery, "verify_inventory") as inventory_check, \
                        mock.patch.object(recovery.time, "time", return_value=1001.0):
                    with self.assertRaisesRegex(ValueError, "provenance changed"):
                        recovery.validate_score_ready(freeze, self.started)
                inventory_check.assert_not_called()

    def test_existing_result_or_nonfresh_status_refuses(self):
        self.freeze["status"] = "already_scored"
        with self.assertRaisesRegex(ValueError, "not fresh"):
            self.ready()
        self.freeze["status"] = "predictions_locked_unscored"
        self.result_path.write_text("generated only", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not fresh"):
            self.ready()

    def test_old_inventory_is_opaque_and_detects_changed_bytes(self):
        for name in ("started.json", "execution_failed.json"):
            (self.old / name).write_bytes(b"generated opaque non-JSON bytes")
        for pair in range(5):
            report = self.old / "pair_reports" / f"pair-{pair}.json"
            report.parent.mkdir(exist_ok=True)
            report.write_bytes(b"not JSON; inventory must not parse")
            checkpoint = self.old / "checkpoints" / f"pair-{pair}"
            checkpoint.mkdir(parents=True)
            for fold in range(10):
                (checkpoint / f"fold-{fold:02d}.pt").write_bytes(b"not a model")
        targets = self.old / "private_targets"
        targets.mkdir()
        for index in range(6):
            (targets / f"generated-{index}.json").write_bytes(b"not labels or JSON")
        with mock.patch.object(recovery, "verify_original"):
            inventory = recovery.original_inventory()
            self.assertEqual(len(inventory), 63)
            recovery.verify_inventory(inventory)
            (targets / "generated-0.json").write_bytes(b"changed generated bytes")
            with self.assertRaisesRegex(ValueError, "artifacts changed"):
                recovery.verify_inventory(inventory)
            (targets / "generated-0.json").unlink()
            with self.assertRaisesRegex(ValueError, "five pairs, fifty checkpoints and six"):
                recovery.original_inventory()

    def test_failed_recovery_inventory_seals_seven_targets_and_zero_new_weights(self):
        for name in ("started.json", "execution_failed.json", "preflight.json"):
            (self.failed / name).write_bytes(b"opaque generated bytes")
        reports, targets = self.failed / "pair_reports", self.failed / "private_targets"
        reports.mkdir()
        targets.mkdir()
        for index in range(5):
            (reports / f"pair-{index}.json").write_bytes(b"not JSON")
        for index in range(7):
            (targets / f"target-{index}.json").write_bytes(b"not labels")
        inventory = recovery.failed_recovery_inventory()
        self.assertEqual(len(inventory), 15)
        recovery.verify_failed_inventory(inventory)
        (targets / "target-0.json").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "failed recovery artifacts changed"):
            recovery.verify_failed_inventory(inventory)
        checkpoint = self.failed / "checkpoints" / "unexpected"
        checkpoint.mkdir(parents=True)
        (checkpoint / "fold-00.pt").write_bytes(b"not a checkpoint")
        with self.assertRaisesRegex(ValueError, "zero checkpoints and seven sealed"):
            recovery.failed_recovery_inventory()

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_score_gate_failure_cannot_open_predictions_or_consume_scoring(self):
        import numpy as np

        with mock.patch.object(recovery, "git", return_value=json.dumps(self.freeze)), \
                mock.patch.object(recovery, "validate_score_ready", side_effect=RuntimeError("stop")), \
                mock.patch.object(np, "load") as load:
            with self.assertRaisesRegex(RuntimeError, "stop"):
                recovery.score_body("generated-commit", mock.Mock(), self.started)
        load.assert_not_called()
        self.assertFalse((self.local / "scoring_consumed.json").exists())

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_calibration_audit_mismatch_stops_before_signal_preflight_or_models(self):
        __import__("numpy")
        from neurodecodekit.models import speech_reference
        from neurodecodekit.preprocess import speech_reproduction

        audit = SimpleNamespace(audit_calibrations=mock.Mock(return_value={"different": True}))
        with mock.patch.dict(sys.modules, {"audit_speech_calibration": audit}), \
                mock.patch.object(recovery, "original_inventory", return_value={}), \
                mock.patch.object(recovery, "failed_recovery_inventory", return_value={}), \
                mock.patch.object(recovery, "verify_sources", return_value=[]), \
                mock.patch.object(speech_reproduction, "preflight_recording_timing") as preflight, \
                mock.patch.object(speech_reference, "predict_from_checkpoints") as predict, \
                mock.patch.object(speech_reference, "train_predict") as train:
            with self.assertRaisesRegex(ValueError, "committed six-pair audit"):
                recovery.predict_body(self.manifest, mock.Mock(), self.started)
        preflight.assert_not_called()
        predict.assert_not_called()
        train.assert_not_called()

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_generated_six_pair_predict_freeze_and_one_score_smoke(self):
        """Exercise the transaction with fabricated arrays and mocked model work."""
        import numpy as np
        from neurodecodekit.evaluation import speech_reproduction as evaluation
        from neurodecodekit.models import speech_reference
        from neurodecodekit.preprocess import speech_reproduction as preprocessing

        self.local.joinpath("preflight.json").unlink()
        extracts = {}
        for pair_index, report in enumerate(self.freeze["pairs"]):
            for record_index, record in enumerate(report["extraction"]):
                recording = record["recording_id"]
                calibration = record_index == 0
                count = 100 if calibration else 41 if pair_index == 0 and record_index == 1 else 50
                ids = [f"{recording}:trial-{index:04d}" for index in range(count)]
                labels = np.arange(count) % 5
                extract = {"trial_ids": ids, "timing_summary": {},
                           "eeg_adaptive": np.zeros((count, 1, 1)),
                           "adaptive_trials": np.zeros((count, 1, 1))}
                if calibration:
                    extract["calibration_labels"] = labels
                else:
                    payload = json.dumps({"recording_id": recording, "trial_ids": ids,
                                          "labels": labels.tolist()}, sort_keys=True).encode()
                    destination = self.failed / "private_targets" / f"{recording}.json"
                    destination.parent.mkdir(exist_ok=True)
                    destination.write_bytes(payload)
                    if pair_index < 5:
                        old_target = self.old / "private_targets" / destination.name
                        old_target.parent.mkdir(exist_ok=True)
                        old_target.write_bytes(payload)
                    record["private_targets_sha256"] = recovery.sha256(destination)
                    extract["private_targets_sha256"] = record["private_targets_sha256"]
                extracts[recording] = extract
            if pair_index < 5:
                recovery.write_json(self.old / "pair_reports" / f"{report['pair_id']}.json", report)

        audit = mock.Mock(return_value={"generated_only": True})

        def extract_recording(*args, recording_id, role, private_target_path, **kwargs):
            audit.assert_called_once_with(self.manifest, self.old / "source", self.old / "pair_reports")
            if role == "online":
                private_target_path.parent.mkdir(exist_ok=True)
                private_target_path.write_bytes(
                    (self.failed / "private_targets" / f"{recording_id}.json").read_bytes())
            return extracts[recording_id]

        def compact_features(extracted):
            count = len(extracted["trial_ids"])
            return np.zeros((count, 2)), {
                name: np.zeros((count, 2)) for name in ("raw", "filtered", "preaction")}

        def compact_predict(labels, train_aux, eval_aux, train_eeg, eval_eeg, **kwargs):
            return {arm: np.full((len(eval_aux), 5), 0.2) for arm in COMPACT_ARMS}

        def checkpoint_predict(values, *args, **kwargs):
            return np.full((len(values), 5), 0.2), {"reused_fits": 10}

        def train_predict(calibration, labels, values, **kwargs):
            return np.full((len(values), 5), 0.2), deepcopy(self.freeze["pairs"][-1]["model"])

        def git(*args):
            if args[0] == "show":
                return self.freeze_path.read_text()
            if args[0] == "diff":
                return self.freeze_path.relative_to(self.repo).as_posix()
            if args[0] == "status":
                return ""
            raise AssertionError(f"Unexpected generated Git operation: {args}")

        budget = SimpleNamespace(started_unix=1000.0, stage_started=None, deadline=8200.0,
                                 peak_rss=0, check=mock.Mock(), storage=mock.Mock(return_value=0))
        with ExitStack() as stack:
            stack.enter_context(mock.patch.dict(sys.modules, {
                "audit_speech_calibration": SimpleNamespace(audit_calibrations=audit)}))
            for module, name, value in (
                (recovery, "original_inventory", mock.Mock(return_value={"original": "hash"})),
                (recovery, "failed_recovery_inventory", mock.Mock(return_value={"failed": "hash"})),
                (recovery, "verify_sources", mock.Mock(return_value=[])),
                (recovery, "verify_original", mock.Mock()),
                (recovery, "verify_inventory", mock.Mock()),
                (recovery, "verify_failed_inventory", mock.Mock()),
                (recovery, "git", git),
                (recovery.subprocess, "run", mock.Mock()),
                (recovery.time, "time", lambda: 1001.0),
                (recovery.importlib.metadata, "version", lambda name: "generated-version"),
                (recovery.original, "compact_features", compact_features),
                (preprocessing, "preflight_recording_timing", mock.Mock(return_value={})),
                (preprocessing, "validate_source_geometry", mock.Mock()),
                (preprocessing, "extract_recording", extract_recording),
                (evaluation, "predict_compact_arms", compact_predict),
                (speech_reference, "predict_from_checkpoints", mock.Mock(side_effect=checkpoint_predict)),
                (speech_reference, "train_predict", mock.Mock(side_effect=train_predict)),
            ):
                stack.enter_context(mock.patch.object(module, name, value))
            stack.enter_context(mock.patch("builtins.print"))
            recovery.predict_body(self.manifest, budget, self.started)
            self.assertEqual(speech_reference.predict_from_checkpoints.call_count, 5)
            self.assertEqual(speech_reference.train_predict.call_count, 1)
            frozen = json.loads(self.freeze_path.read_text())
            self.assertEqual(frozen["n_evaluation_trials"], 341)
            self.assertEqual(frozen["calibration_audit_sha256"], recovery.sha256(self.audit_path))
            self.assertFalse((self.local / "scoring_consumed.json").exists())
            recovery.score_body("generated-freeze-commit", budget, self.started)
            result = json.loads(self.result_path.read_text())
            self.assertEqual((result["n_trials"], result["scoring_invocations"]), (341, 1))
            self.assertEqual(result["failed_recovery_failure_sha256"], recovery.FAILED_RECOVERY_SHA)
            with self.assertRaisesRegex(RuntimeError, "failed or scoring already consumed"):
                recovery.score_body("generated-freeze-commit", budget, self.started)


class RecoveryBudgetTests(unittest.TestCase):
    def budget(self):
        budget = object.__new__(recovery.RecoveryBudget)
        budget.started = 100.0
        budget.started_unix = 1000.0
        budget.deadline = 7300.0
        budget.stage_started = None
        budget.process = mock.Mock()
        budget.process.memory_info.return_value = SimpleNamespace(rss=1024)
        budget.peak_rss = 0
        return budget

    def test_resuming_for_score_deducts_elapsed_wall_time(self):
        def initialize_base(budget):
            budget.started = 500.0

        with mock.patch.object(recovery.original.Budget, "__init__", initialize_base), \
                mock.patch.object(recovery.time, "time", return_value=1400.0):
            budget = recovery.RecoveryBudget(started_unix=1000.0)
        self.assertEqual(budget.deadline, 500.0 + 7200.0 - 400.0)

    def test_monotonic_or_wall_deadline_each_refuses_at_exact_limit(self):
        for wall, monotonic in ((1001.0, 7300.0), (8200.0, 101.0)):
            with self.subTest(wall=wall, monotonic=monotonic), \
                    mock.patch.object(recovery.time, "time", return_value=wall), \
                    mock.patch.object(recovery.time, "monotonic", return_value=monotonic), \
                    mock.patch.object(recovery.original.Budget, "check") as base_check:
                with self.assertRaisesRegex(RuntimeError, "Two-hour"):
                    self.budget().check()
                base_check.assert_not_called()

    def test_watchdog_checks_current_stage_and_rss_without_numerical_callbacks(self):
        budget = self.budget()
        budget.stage_started = 100.0
        with mock.patch.object(recovery.time, "time", return_value=1901.0), \
                mock.patch.object(recovery.time, "monotonic", return_value=1001.0):
            with self.assertRaisesRegex(RuntimeError, "Fifteen-minute"):
                budget.check()
        budget.stage_started = None
        budget.process.memory_info.return_value = SimpleNamespace(rss=4 * recovery.GIB + 1)
        with mock.patch.object(recovery.time, "time", return_value=1001.0), \
                mock.patch.object(recovery.time, "monotonic", return_value=101.0):
            with self.assertRaisesRegex(RuntimeError, "Four-GiB"):
                budget.check()

    def test_storage_combines_original_and_recovery_without_double_budget(self):
        with tempfile.TemporaryDirectory(prefix="speech-recovery-storage-generated-") as directory:
            root = Path(directory)
            old, failed, local = root / "old", root / "failed", root / "recovery"
            old.mkdir()
            failed.mkdir()
            local.mkdir()
            (old / "generated.bin").write_bytes(b"a" * 60)
            (failed / "generated.bin").write_bytes(b"b" * 60)
            (local / "generated.bin").write_bytes(b"c" * 60)
            with mock.patch.object(recovery, "OLD", old), \
                    mock.patch.object(recovery, "FAILED_RECOVERY", failed), \
                    mock.patch.object(recovery, "LOCAL", local), \
                    mock.patch.object(recovery, "REPO", root), \
                    mock.patch.object(recovery, "GIB", 100), \
                    mock.patch.object(recovery.shutil, "disk_usage",
                                      return_value=SimpleNamespace(free=10000)):
                with self.assertRaisesRegex(RuntimeError, "Combined original/recovery storage"):
                    self.budget().storage()


if __name__ == "__main__":
    unittest.main()
