"""Generated-only successor tests; never open participant files or use network."""

from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from tests import test_inner_speech_runner as lifecycle
from tests.test_inner_speech_reader import generated_events
from neurodecodekit.datasets.inner_speech import InnerSpeechRefusal, parse_trials

SPEC = importlib.util.spec_from_file_location("missing_rest_wrapper",
    Path(__file__).resolve().parents[1] / "scripts/test_inner_speech_missing_rest.py")
wrapper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wrapper)


class SuccessorLifecycleTests(lifecycle.RunnerTests):
    """Reuse all eight existing lifecycle safeguards under the new fixed route."""

    def setUp(self):
        patched = mock.patch.object(lifecycle, "runner", wrapper.configured_runner())
        patched.start()
        self.addCleanup(patched.stop)


class MissingRestRunnerTests(unittest.TestCase):
    def test_failure_projects_existing_exception_without_reopening_data(self):
        amended = wrapper.configured_runner()
        events = generated_events()
        events = [event for event in events if event[1] != 44]
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(amended, "LOCAL", Path(directory)):
            try:
                parse_trials(events, participant="sub-01", allow_missing_rest=True)
            except InnerSpeechRefusal as error:
                amended.failure(error, mock.Mock(stage="all_participant_event_qualification",
                    participant="sub-01", started=time.time(), peak_rss=1000))
            report = json.loads((Path(directory) / "execution_failed.json").read_text())
        self.assertEqual(report["experiment_id"], amended.EXPERIMENT_ID)
        self.assertEqual(report["structural_diagnostic"]["first_mismatch"], {
            "expected_families": ["action"], "observed_family": "relax"})
        self.assertEqual(report["structural_diagnostic"]["completed_trials"], 0)

    def test_fixed_route_keeps_original_and_successor_artifacts_separate(self):
        amended, original = wrapper.configured_runner(), lifecycle.runner
        self.assertTrue(amended.ALLOW_MISSING_REST)
        self.assertFalse(original.ALLOW_MISSING_REST)
        for name in ("EXPERIMENT_ID", "LOCAL", "PLAN", "FREEZE", "RESULT"):
            self.assertNotEqual(getattr(amended, name), getattr(original, name))
        self.assertEqual(amended.SOURCE, original.SOURCE)
        self.assertEqual(amended.MAX_SECONDS, 1200)
        self.assertTrue(set(original.CODE_PATHS).issubset(amended.CODE_PATHS))
        self.assertIn("scripts/test_inner_speech_missing_rest.py", amended.CODE_PATHS)
        self.assertIn(amended.PLAN.relative_to(amended.REPO).as_posix(), amended.CODE_PATHS)
        with mock.patch.object(amended, "git", side_effect=AssertionError("No Git")), \
                mock.patch.dict("sys.modules", {"numpy": None}):
            with self.assertRaisesRegex(RuntimeError, "attempt_identity"):
                amended.score("a" * 40, mock.Mock(), {"experiment_id": original.EXPERIMENT_ID})

    @unittest.skipIf(lifecycle.np is None, "optional NumPy")
    def test_both_timing_values_flags_and_observed_columns(self):
        np = lifecycle.np
        amended, original = wrapper.configured_runner(), lifecycle.runner
        trials = parse_trials(generated_events(), participant="sub-01")
        for index in (0, 3, 4, 40):
            new = amended.timing_features(trials, index)
            np.testing.assert_array_equal(new[:8], original.timing_features(trials, index))
            np.testing.assert_array_equal(new[8:], [1, int(index > 0)])
        missing = [replace(trial, rest=None) if i == 3 else trial for i, trial in enumerate(trials)]
        for index, column, flags in ((3, 6, [0, 1]), (4, 7, [1, 0])):
            new = amended.timing_features(missing, index)
            expected = original.timing_features(trials, index)
            expected[column] = 0
            np.testing.assert_array_equal(new[:8], expected)
            np.testing.assert_array_equal(new[8:], flags)
            with self.assertRaisesRegex(RuntimeError, "missing_rest_requires_amendment"):
                original.timing_features(missing, index)
        # Direction identity never changes predictors or the availability pattern.
        relabeled = [replace(trial, label=(trial.label + 1) % 4) for trial in missing]
        np.testing.assert_array_equal(amended.timing_features(missing, 3),
                                      amended.timing_features(relabeled, 3))

    @unittest.skipIf(lifecycle.np is None, "optional NumPy")
    def test_windows_and_physiological_features_unchanged(self):
        import numpy as np
        from neurodecodekit.experiments import inner_speech as model
        amended = wrapper.configured_runner()
        trials = parse_trials(generated_events(), participant="sub-01")[:5]
        trials[3] = replace(trials[3], rest=None)
        reader = mock.Mock()
        reader.read_window.side_effect = lambda start, stop, picks: np.zeros((136, stop-start))
        with mock.patch.object(model, "window_features", return_value={"P": np.zeros(77),
                                                                      "E": np.ones(640)}):
            features = amended.participant_features(reader, trials, mock.Mock())
        self.assertEqual(features["P"].shape, (5, 87))
        self.assertEqual(features["E_action"].shape, (5, 640))
        calls = reader.read_window.call_args_list
        for i, trial in enumerate(trials):
            self.assertEqual(calls[2*i].args[:2], (trial.relax-2048, trial.relax))
            self.assertEqual(calls[2*i+1].args[:2], (trial.cue, trial.cue+384))

    @unittest.skipIf(lifecycle.np is None, "optional NumPy")
    def test_last_participant_failure_prevents_any_physiology_or_fit(self):
        from neurodecodekit.datasets import inner_speech as reader_module
        from neurodecodekit.experiments import inner_speech as model
        amended = wrapper.configured_runner()
        inventory = [(f"sub-{i:02d}", Path(f"generated-{i}"), "generated") for i in range(1, 11)]
        readers = []
        for i in range(10):
            events = generated_events()
            if i == 9:
                events = [event for index, event in enumerate(events)
                          if index != next(k for k, (_, c) in enumerate(events) if c == 44)]
            readers.append(mock.Mock(status_summary={}, iter_status_events=mock.Mock(return_value=events)))
        with mock.patch.object(amended, "source_inventory", return_value=inventory), \
                mock.patch.object(reader_module, "BDFReader", side_effect=readers) as constructors, \
                mock.patch.object(amended, "participant_features") as features, \
                mock.patch.object(model, "run_condition") as fits, \
                mock.patch.object(amended, "write_json") as writes:
            with self.assertRaises(InnerSpeechRefusal):
                amended.predict(mock.Mock(), {})
        self.assertEqual(constructors.call_count, 10)
        features.assert_not_called()
        fits.assert_not_called()
        writes.assert_not_called()

    @unittest.skipIf(lifecycle.np is None, "optional NumPy")
    def test_dimension_mode_is_explicit_and_scoring_stays_separate(self):
        import numpy as np
        from neurodecodekit.experiments import inner_speech as model
        labels, original = np.arange(40) % 4, np.arange(40)
        features = {"P": np.zeros((40, 87)), **{name: np.zeros((40, 640))
                    for name in ("E_action", "E_cue", "E_late")}}
        with self.assertRaises(ValueError):
            model.run_condition(features, labels, original)
        with mock.patch.object(model, "_metrics", side_effect=AssertionError("No scoring")):
            result = model.run_condition(features, labels, original, missing_timing=True)
        self.assertEqual(set(result["predictions"]), set(model.ARMS))
        self.assertEqual(result["fit_diagnostics"]["peripheral_timing_features"], 87)
        self.assertTrue(result["fit_diagnostics"]["missing_timing_amendment"])
        self.assertEqual(result["fit_diagnostics"]["ridge_fits"], 96)
        features["P"] = np.zeros((40, 85))
        with self.assertRaises(ValueError):
            model.run_condition(features, labels, original, missing_timing=True)


if __name__ == "__main__":
    unittest.main()
