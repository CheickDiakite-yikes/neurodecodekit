"""Generated-only orchestration tests: no real source access or Git/network calls."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/test_inner_speech.py"
SPEC = importlib.util.spec_from_file_location("inner_speech_runner_tested", SCRIPT)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)
try:
    import numpy as np
except ImportError:
    np = None


class RunnerTests(unittest.TestCase):
    def test_dry_run_does_not_open_any_file_or_call_git(self):
        with mock.patch.object(Path, "open", side_effect=AssertionError("No files")), \
                mock.patch.object(runner, "git", side_effect=AssertionError("No Git")), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(runner.main([]), 0)
        self.assertEqual(json.loads(output.getvalue())["participant_files_opened"], 0)

    def test_same_nine_people_and_effect_size_are_both_required(self):
        def pairs():
            return [{"condition": "inner", "participant": f"sub-{i+1:02d}",
                     "primary_joint_nll_gains": {key: .05 for key in
                      ("P", "deranged_joint", "joint_shuffled", "uniform", "training_prior")}}
                    for i in range(10)]
        values = pairs()
        self.assertTrue(runner.primary_decision(values)["primary_pass"])
        values[0]["primary_joint_nll_gains"]["P"] = 0
        result = runner.primary_decision(values)
        self.assertTrue(result["primary_pass"])
        self.assertEqual(result["contrasts"]["P"]["one_sided_sign_p"], 11/1024)
        values[1]["primary_joint_nll_gains"]["uniform"] = 0
        self.assertFalse(runner.primary_decision(values)["primary_pass"])
        values = pairs()
        for value in values:
            value["primary_joint_nll_gains"]["P"] = .019
        self.assertFalse(runner.primary_decision(values)["primary_pass"])
        with self.assertRaisesRegex(RuntimeError, "primary_population"):
            runner.primary_decision(values[:-1])

    def test_failure_does_not_emit_private_error_text(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(runner, "LOCAL", Path(directory)):
            budget = mock.Mock(stage="qualification", participant="sub-01",
                               started=time.time(), peak_rss=1000)
            runner.failure(ValueError("PRIVATE EVENT ROW 12345"), budget)
            result = json.loads((Path(directory) / "execution_failed.json").read_text())
            self.assertEqual(result["error_code"], "ValueError")
            self.assertNotIn("PRIVATE", json.dumps(result))

    def test_exact_roster_not_just_total_count(self):
        pairs = [{"participant": f"sub-{i:02d}", "condition": condition,
                  "trials": runner.expected_trials(f"sub-{i:02d}", condition)}
                 for i in range(1, 11) for condition, _ in runner.CONDITIONS]
        runner.validate_pairs(pairs)
        pairs[0], pairs[1] = pairs[1], pairs[0]
        runner.validate_pairs(pairs)
        pairs[0] = dict(pairs[1])
        with self.assertRaisesRegex(RuntimeError, "exact_thirty_pair_roster"):
            runner.validate_pairs(pairs)

    def test_resource_failure_before_publication_leaves_no_public_result(self):
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory)
            result_path = local / "public.json"
            budget = mock.Mock(publication_lock=threading.Lock(), completed=False)
            budget.storage.side_effect = RuntimeError("generated_output_budget")
            with mock.patch.multiple(runner, LOCAL=local, RESULT=result_path):
                with self.assertRaisesRegex(RuntimeError, "generated_output_budget"):
                    runner.publish_result({"generated_only": True}, budget)
            self.assertFalse(result_path.exists())
            self.assertFalse(budget.completed)
            self.assertTrue((local / "completed_aggregate.json").exists())
            budget.storage.assert_called_once_with(
                additional=(local / "completed_aggregate.json").stat().st_size)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_synthetic_one_shot_score_consumes_before_loading_targets(self):
        from neurodecodekit.experiments.inner_speech import ARMS, LEARNED_ARMS
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            local = repo / "private"
            local.mkdir()
            registries = repo / "registries"
            registries.mkdir()
            freeze_path, result_path = registries / "freeze.json", registries / "result.json"
            plan_path = registries / "plan.json"
            runner.write_json(plan_path, {"interpretation": "Generated fixture only"})
            runner.write_json(local / "qualification.json", {"generated_only": True})
            pairs = []
            for person in range(1, 11):
                for condition, _ in runner.CONDITIONS:
                    n = 40 if condition == "pronounced" or (person == 3 and condition == "inner") else (
                        120 if person == 3 else 80)
                    stem = f"sub-{person:02d}_{condition}"
                    prediction, target, diagnostic = (local / (stem + suffix) for suffix in
                                                     (".npz", ".npy", ".json"))
                    values = np.full((n, 4), .25)
                    np.savez_compressed(prediction, **{key: values for key in ARMS},
                                        **{"raw_" + key: values for key in LEARNED_ARMS})
                    np.save(target, np.arange(n) % 4, allow_pickle=False)
                    runner.write_json(diagnostic, {"generated_only": True})
                    pairs.append({"participant": f"sub-{person:02d}", "condition": condition, "trials": n,
                        **{key: path.name for key, path in zip(
                            ("predictions", "targets", "diagnostics"), (prediction, target, diagnostic))},
                        **{key + "_sha256": runner.sha256(path) for key, path in zip(
                            ("predictions", "targets", "diagnostics"), (prediction, target, diagnostic))}})
            frozen = {"pairs": pairs, "fingerprints": {"fixture": "generated"},
                      "qualification_sha256": runner.sha256(local / "qualification.json"),
                      "peak_rss_bytes": 1000}
            runner.write_json(freeze_path, frozen)
            commit = "a" * 40

            def fake_git(*args):
                return {("rev-parse", "HEAD"): commit,
                        ("status", "--porcelain", "--untracked-files=no"): "",
                        ("diff", "--name-only", "b" * 40, "HEAD"): "registries/freeze.json",
                        ("ls-remote", "origin", "refs/heads/main"): commit + "\trefs/heads/main",
                        ("show", commit + ":registries/freeze.json"): json.dumps(frozen)}[args]

            original_load = np.load
            load_calls = []

            def guarded_load(*args, **kwargs):
                self.assertTrue((local / "scoring_consumed.json").exists())
                load_calls.append(str(args[0]))
                return original_load(*args, **kwargs)

            budget = mock.Mock(started=time.time(), peak_rss=1000,
                               publication_lock=threading.Lock(), completed=False)
            started = {"code_commit": "b" * 40}
            with mock.patch.multiple(runner, REPO=repo, LOCAL=local, FREEZE=freeze_path,
                                     RESULT=result_path, PLAN=plan_path), \
                    mock.patch.object(runner, "fingerprints", return_value={"fixture": "generated"}), \
                    mock.patch.object(runner, "git", side_effect=fake_git), \
                    mock.patch.object(np, "load", side_effect=guarded_load), \
                    contextlib.redirect_stdout(io.StringIO()):
                runner.score(commit, budget, started)
                result = json.loads(result_path.read_text())
                self.assertEqual(len(result["pairs"]), 30)
                self.assertEqual(result["scoring_invocations"], 1)
                self.assertTrue(budget.completed)
                self.assertFalse(result["primary"]["primary_pass"])
                self.assertEqual(len(load_calls), 60)
                with self.assertRaises(FileExistsError):
                    runner.score(commit, budget, started)
                self.assertEqual(len(load_calls), 60)


if __name__ == "__main__":
    unittest.main()
