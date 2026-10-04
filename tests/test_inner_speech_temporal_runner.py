"""Generated, in-memory lifecycle checks; never open any participant/source file."""

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import threading
import time
from types import SimpleNamespace
import unittest
from unittest import mock


SPEC = importlib.util.spec_from_file_location("temporal_wrapper_tested",
    Path(__file__).resolve().parents[1] / "scripts/test_inner_speech_temporal.py")
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
try:
    import numpy as np
except ImportError:
    np = None


class TemporalRunnerTests(unittest.TestCase):
    def setUp(self):
        self.runner = WRAPPER.configured_runner()

    def roster(self):
        return [{"participant": f"sub-{i:02d}", "condition": condition,
                 "trials": 40 if condition == "pronounced" else 80}
                for i in range(1, 11) for condition, _ in self.runner.CONDITIONS]

    def gains(self):
        return [{"participant": f"sub-{i:02d}", "condition": "inner",
                 "primary_joint_nll_gains": {key: .05 for key in (
                     "P", "deranged_joint", "joint_shuffled", "uniform", "training_prior", "spectral_joint")},
                 "eeg_sensitivity_nll_gains": {"cue_eeg": {
                     "cue_eeg_shuffled": .05, "uniform": .05, "training_prior": .05}}}
                for i in range(1, 11)]

    def test_dry_run_requires_no_file_git_or_numpy_and_uses_only_new_paths(self):
        r = self.runner
        with mock.patch.object(Path, "open", new=lambda *a, **k: self.fail("No files")), \
                mock.patch.object(r, "git", new=lambda *a: self.fail("No Git")), \
                mock.patch.dict("sys.modules", {"numpy": None}), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(r.main([]), 0)
            with self.assertRaisesRegex(RuntimeError, "attempt_identity"):
                r.score("a" * 40, None, {"experiment_id": "INNER-SPEECH-OBSERVED-1"})
        self.assertEqual(json.loads(output.getvalue())["participant_files_opened"], 0)
        self.assertEqual(r.SOURCE_SESSION, "ses-02")
        self.assertIn("ses02", r.SOURCE.name)
        self.assertEqual(r.MAX_EXCLUSIONS, 20)
        self.assertEqual(r.EXPERIMENT_KWARGS, {})
        self.assertEqual(r.MODEL_MODULE, "neurodecodekit.experiments.inner_speech_temporal")
        self.assertEqual((r.MAX_SECONDS, r.MAX_RSS, r.MAX_OUTPUT), (1200, 1024**3, 32 * 1024**2))
        self.assertIn("inner_speech_observed_1_20261002", r.PRIOR_EVIDENCE)
        self.assertNotIn("registries/inner_speech_acquisition_result.v0.json", r.CODE_PATHS)

    def test_exact_thirty_roster_and_two_exclusions_per_person(self):
        r, pairs = self.runner, self.roster()
        r.validate_pairs(pairs)
        for pair in pairs[::3]:
            pair["trials"] -= 2
        r.validate_pairs(pairs)  # exactly1980, twenty exclusions but no person loses more than two
        for change, message in ((lambda rows: rows.__setitem__(0, dict(rows[1])), "exact_thirty_pair_roster"),
                                (lambda rows: rows.pop(), "exact_thirty_pair_roster"),
                                (lambda rows: rows[0].update(trials=37), "temporal_pair_trial_count"),
                                (lambda rows: rows[1].update(trials=79), "person_exclusion_cap"),
                                (lambda rows: rows[0].update(trials=True), "temporal_pair_trial_count"),
                                (lambda rows: rows[7].update(trials=120), "temporal_pair_trial_count")):
            changed = copy.deepcopy(pairs)
            change(changed)
            with self.subTest(message=message), self.assertRaisesRegex(RuntimeError, message):
                r.validate_pairs(changed)
        self.assertEqual(r.expected_trials("sub-03", "inner"), 80)
        self.assertEqual(r.expected_trials("sub-03", "visualization"), 80)

    def test_primary_same_nine_six_controls_effect_and_separate_cue_gate(self):
        r, pairs = self.runner, self.gains()
        result = r.primary_decision(pairs)
        self.assertTrue(result["primary_pass"] and result["cue_sensitivity"]["pass"])
        self.assertTrue(result["progression_pass"])
        pairs[0]["primary_joint_nll_gains"]["P"] = 0
        result = r.primary_decision(pairs)
        self.assertTrue(result["primary_pass"])
        self.assertEqual(result["contrasts"]["P"]["one_sided_sign_p"], 11 / 1024)
        pairs[1]["primary_joint_nll_gains"]["spectral_joint"] = 0
        result = r.primary_decision(pairs)
        self.assertFalse(result["primary_pass"])  # each comparator has nine, but intersection has eight
        self.assertTrue(result["cue_sensitivity"]["pass"])
        self.assertFalse(result["progression_pass"])
        for control, value in (("P", .019), ("spectral_joint", -.5)):
            pairs = self.gains()
            if control == "P":
                for pair in pairs:
                    pair["primary_joint_nll_gains"][control] = value
            else:
                pairs[0]["primary_joint_nll_gains"][control] = value
            self.assertFalse(r.primary_decision(pairs)["primary_pass"])
        pairs = self.gains()
        pairs[0]["eeg_sensitivity_nll_gains"]["cue_eeg"]["uniform"] = 0
        pairs[1]["eeg_sensitivity_nll_gains"]["cue_eeg"]["cue_eeg_shuffled"] = 0
        result = r.primary_decision(pairs)
        self.assertTrue(result["primary_pass"])
        self.assertFalse(result["cue_sensitivity"]["pass"] or result["progression_pass"])
        pairs = self.gains()
        for pair in pairs:
            pair["eeg_sensitivity_nll_gains"]["cue_eeg"]["uniform"] = .019
        self.assertFalse(r.primary_decision(pairs)["cue_sensitivity"]["pass"])
        with self.assertRaisesRegex(RuntimeError, "primary_population"):
            r.primary_decision(pairs[:-1])

    @contextlib.contextmanager
    def source_fixture(self):
        r = self.runner
        source = Path(r.REPO.anchor) / "generated-temporal-source"
        files = []
        for i in range(1, 11):
            participant = f"sub-{i:02d}"
            size = 600000000 if i < 10 else 1470116352
            files.append({"path": f"{participant}/ses-02/eeg/{participant}_ses-02_task-innerspeech_eeg.bdf",
                          "md5": f"{i:032x}", "size_bytes": size, "s3_version_id": f"generated-{i}",
                          "metadata_head_verified": {"status": 200, "content_length": size, "etag": f"{i:032x}"}})
        manifest = {"files": files}
        acquisition = {"acquisition_id": "INNER-SPEECH-ACQ-S2", "status": "complete",
                       "payload_bytes": 6870116352, "manifest_sha256": "generated-manifest-hash",
                       "sample_or_status_values_parsed": False, "targets_or_performance_outcomes_computed": False,
                       "files": [{"path": f["path"], "md5": f["md5"], "bytes": f["size_bytes"],
                                  "sha256": "generated-source-hash"} for f in files]}
        committed = copy.deepcopy(acquisition)
        state = SimpleNamespace(manifest=manifest, acquisition=acquisition, committed=committed,
                                failure=False, hash_value="generated-source-hash", hash_calls=[])

        def read(path, *args, **kwargs):
            self.assertIn(path, (r.MANIFEST, r.ACQUISITION))
            return json.dumps(manifest if path == r.MANIFEST else acquisition)

        def git(*args):
            self.assertEqual(args, ("show", "HEAD:" + r.ACQUISITION.relative_to(r.REPO).as_posix()))
            return json.dumps(state.committed)

        def digest(path, check=None):
            if path == r.MANIFEST:
                return "generated-manifest-hash"
            self.assertTrue(path.is_relative_to(source))
            state.hash_calls.append(path)
            if check:
                check()
            return state.hash_value

        sizes = {source / f["path"]: f["size_bytes"] for f in files}
        with mock.patch.object(r, "SOURCE", source), \
                mock.patch.object(Path, "open", new=lambda *a, **k: self.fail("No files")), \
                mock.patch.object(Path, "read_text", new=read), \
                mock.patch.object(Path, "resolve", new=lambda path, *a, **k: path.absolute()), \
                mock.patch.object(Path, "exists", new=lambda path: state.failure if path.name == "acquisition_failure.json" else False), \
                mock.patch.object(Path, "stat", new=lambda path, *a, **k: SimpleNamespace(st_size=sizes[path])), \
                mock.patch.object(r, "sha256", new=digest), mock.patch.object(r, "git", new=git):
            yield state

    def test_source_inventory_binds_committed_new_receipt_manifest_and_ten_session_two_files(self):
        with self.source_fixture() as state:
            inventory = self.runner.source_inventory(SimpleNamespace(check=lambda: None))
            self.assertEqual([p for p, _, _ in inventory], [f"sub-{i:02d}" for i in range(1, 11)])
            self.assertEqual(len(state.hash_calls), 10)
            self.assertTrue(all("ses-02" in path.parts for _, path, _ in inventory))
        mutations = (
            (lambda s: s.acquisition.update(status="partial"), "acquisition_not_committed"),
            (lambda s: (s.acquisition.update(acquisition_id="INNER-SPEECH-ACQ-1"),
                        s.committed.update(acquisition_id="INNER-SPEECH-ACQ-1")), "session_two_acquisition_identity"),
            (lambda s: (s.acquisition.update(manifest_sha256="wrong"),
                        s.committed.update(manifest_sha256="wrong")), "session_two_acquisition_identity"),
            (lambda s: s.manifest["files"][0].update(path="sub-01/ses-01/old.bdf"), "source_identity"),
            (lambda s: s.manifest["files"].pop(), "complete_source_required"),
            (lambda s: setattr(s, "failure", True), "failed_acquisition"),
            (lambda s: setattr(s, "hash_value", "changed"), "source_hash"),
        )
        for mutate, message in mutations:
            with self.subTest(message=message), self.source_fixture() as state:
                mutate(state)
                with self.assertRaisesRegex(RuntimeError, message):
                    self.runner.source_inventory(SimpleNamespace(check=lambda: None))

    @unittest.skipIf(np is None, "NumPy optional")
    def test_qualification_passes_session_two_to_both_decoders_and_parser_without_physiology(self):
        from tests.test_inner_speech_reader import generated_events
        events = generated_events()
        calls, reports = [], {}

        def decode(*args, participant, session, **kwargs):
            self.assertEqual(session, "ses-02")
            calls.append(participant)
            return events

        reader = SimpleNamespace(iter_status_events=decode,
                                 read_window=lambda *a: self.fail("No physiological windows"))
        r = self.runner
        inventory = [(f"sub-{i:02d}", Path(f"generated-{i}.bdf"), "generated") for i in range(1, 11)]
        with mock.patch.object(Path, "open", new=lambda *a, **k: self.fail("No source files")), \
                mock.patch("neurodecodekit.datasets.inner_speech.BDFReader", new=lambda *a: reader), \
                mock.patch("neurodecodekit.datasets.inner_speech_reference_status.reference_status_events", new=decode), \
                mock.patch.object(r, "write_json", new=lambda path, value: reports.update({path.name: value})), \
                mock.patch.object(r, "sha256", new=lambda *a: "generated"), \
                mock.patch("neurodecodekit.experiments.inner_speech_temporal._ridge_probabilities",
                           new=lambda *a: self.fail("No fits")):
            qualified = r.qualify_all(inventory, SimpleNamespace(check=lambda: None))
        self.assertEqual(len(qualified), 10)
        self.assertEqual(len(calls), 20)
        self.assertEqual(reports["qualification.json"]["trials"], 2000)
        self.assertFalse(reports["qualification.json"]["participants"][2]["condition_correction_applied"])
        self.assertEqual(reports["decoder_gate.json"]["physiological_windows_read"], 0)

    @contextlib.contextmanager
    def score_fixture(self, *, missing_arm=False):
        from neurodecodekit.experiments import inner_speech_temporal as model
        r = self.runner
        repo = Path(r.REPO.anchor) / "generated-temporal-score"
        local, registries = repo / "local", repo / "registries"
        freeze_path, result_path, plan_path = (registries / name for name in ("freeze.json", "result.json", "plan.json"))
        records = {local / "decoder_gate.json": {"status": "passed", "generated_only": True},
                   plan_path: {"interpretation": "Generated fixture only"}}
        arrays, loads = {}, []

        def digest(path, *args):
            self.assertTrue(path.is_relative_to(repo))
            return hashlib.sha256(str(path).encode()).hexdigest()

        qualification = {"nominal_trials": 2000, "trials": 2000, "trials_excluded": 0,
                         "decoder_gate_sha256": digest(local / "decoder_gate.json"), "participants": [
                             {"participant": f"sub-{i:02d}", "condition_counts_eligible": {
                                 str(code): 40 if condition == "pronounced" else 80
                                 for condition, code in r.CONDITIONS}} for i in range(1, 11)]}
        records[local / "qualification.json"] = qualification
        pairs = self.roster()
        for pair in pairs:
            stem = pair["participant"] + "_" + pair["condition"]
            for kind, suffix in (("predictions", ".npz"), ("targets", ".npy"), ("diagnostics", ".json")):
                path = local / (stem + suffix)
                pair[kind], pair[kind + "_sha256"] = path.name, digest(path)
                if kind == "diagnostics":
                    records[path] = {"generated_only": True}
                else:
                    arrays[path] = (kind, pair["trials"])
        frozen = {"experiment_id": r.EXPERIMENT_ID, "pairs": pairs, "fingerprints": {"fixture": "generated"},
                  "qualification_sha256": digest(local / "qualification.json"), "peak_rss_bytes": 1000}
        records[freeze_path] = frozen
        commit = "a" * 40

        def git(*args):
            return {("rev-parse", "HEAD"): commit, ("status", "--porcelain", "--untracked-files=no"): "",
                    ("diff", "--name-only", "b" * 40, "HEAD"): "registries/freeze.json",
                    ("ls-remote", "origin", "refs/heads/main"): commit + "\trefs/heads/main",
                    ("show", commit + ":registries/freeze.json"): json.dumps(frozen)}[args]

        def write(path, payload):
            self.assertTrue(path.is_relative_to(repo))
            if path in records:
                raise FileExistsError(path.name)
            records[path] = payload

        def load(path, *, allow_pickle):
            self.assertFalse(allow_pickle)
            self.assertIn(local / "scoring_consumed.json", records)
            loads.append(path)
            kind, n = arrays[path]
            if kind == "targets":
                return np.arange(n) % 4
            values = np.full((n, 4), .25)
            output = {arm: values for arm in model.ARMS}
            output.update({"raw_" + arm: values for arm in model.LEARNED_ARMS})
            if missing_arm:
                output.pop("spectral_joint")
            return contextlib.nullcontext(output)

        budget = SimpleNamespace(started=time.time(), peak_rss=1000, publication_lock=threading.Lock(),
                                 completed=False, storage=lambda **k: None, check=lambda: None)
        with mock.patch.multiple(r, REPO=repo, LOCAL=local, FREEZE=freeze_path, RESULT=result_path, PLAN=plan_path), \
                mock.patch.object(Path, "open", new=lambda *a, **k: self.fail("No real files")), \
                mock.patch.object(Path, "read_text", new=lambda path, *a, **k: json.dumps(records[path])), \
                mock.patch.object(Path, "exists", new=lambda path: path in records), \
                mock.patch.object(Path, "stat", new=lambda path, *a, **k: SimpleNamespace(st_size=len(json.dumps(records[path])))), \
                mock.patch.object(r, "write_json", new=write), mock.patch.object(r, "sha256", new=digest), \
                mock.patch.object(r, "fingerprints", new=lambda: {"fixture": "generated"}), \
                mock.patch.object(r, "git", new=git), mock.patch.object(np, "load", new=load), \
                mock.patch.object(r.os, "link", new=lambda source, target: write(target, records[source])), \
                contextlib.redirect_stdout(io.StringIO()):
            yield SimpleNamespace(records=records, loads=loads, result=result_path, local=local, budget=budget,
                                  commit=commit, frozen=frozen,
                                  started={"code_commit": "b" * 40, "experiment_id": r.EXPERIMENT_ID})

    @unittest.skipIf(np is None, "NumPy optional")
    def test_complete_thirteen_arm_one_shot_score_consumes_before_load_and_integrates_primary(self):
        with self.score_fixture() as f:
            self.runner.score(f.commit, f.budget, f.started)
            result = f.records[f.result]
            self.assertEqual(len(result["pairs"]), 30)
            self.assertEqual(result["scoring_invocations"], 1)
            self.assertEqual(result["eligible_trials"], 2000)
            self.assertEqual(result["trials_excluded"], 0)
            self.assertTrue(f.budget.completed)
            self.assertFalse(result["primary"]["primary_pass"])
            self.assertFalse(result["primary"]["cue_sensitivity"]["pass"])
            self.assertFalse(result["primary"]["progression_pass"])
            for pair in result["pairs"]:
                self.assertEqual((len(pair["metrics"]), len(pair["uncalibrated_diagnostic"])), (13, 11))
            self.assertEqual(len(f.loads), 60)
            with self.assertRaises(FileExistsError):
                self.runner.score(f.commit, f.budget, f.started)
            self.assertEqual(len(f.loads), 60)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_missing_arm_consumes_attempt_without_publication_or_second_load(self):
        with self.score_fixture(missing_arm=True) as f:
            with self.assertRaises(KeyError):
                self.runner.score(f.commit, f.budget, f.started)
            self.assertIn(f.local / "scoring_consumed.json", f.records)
            self.assertNotIn(f.result, f.records)
            self.assertFalse(f.budget.completed)
            with self.assertRaises(FileExistsError):
                self.runner.score(f.commit, f.budget, f.started)
            self.assertEqual(len(f.loads), 1)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_bad_frozen_roster_refuses_before_marker_or_any_array_load(self):
        with self.score_fixture() as f:
            f.frozen["pairs"][0] = dict(f.frozen["pairs"][1])
            with self.assertRaisesRegex(RuntimeError, "exact_thirty_pair_roster"):
                self.runner.score(f.commit, f.budget, f.started)
            self.assertNotIn(f.local / "scoring_consumed.json", f.records)
            self.assertEqual(f.loads, [])


if __name__ == "__main__":
    unittest.main()
