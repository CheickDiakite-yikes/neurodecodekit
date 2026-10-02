"""Generated-only successor orchestration; no acquired recordings are opened."""

import contextlib
from dataclasses import replace
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.test_inner_speech_reader import generated_events

SPEC = importlib.util.spec_from_file_location("observed_wrapper_tested",
    Path(__file__).resolve().parents[1] / "scripts/test_inner_speech_observed.py")
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
try:
    import numpy as np
except ImportError:
    np = None


class ObservedRunnerTests(unittest.TestCase):
    def setUp(self):
        self.runner = WRAPPER.configured_runner()

    def test_dry_run_and_score_identity_refusal_need_no_numpy_or_data(self):
        r = self.runner
        with mock.patch.object(Path, "open", side_effect=AssertionError("No files")), \
                mock.patch.object(r, "git", side_effect=AssertionError("No Git")), \
                mock.patch.dict("sys.modules", {"numpy": None}), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(r.main([]), 0)
            with self.assertRaisesRegex(RuntimeError, "attempt_identity"):
                r.score("a" * 40, None, {"experiment_id": "INNER-SPEECH-TEST-1-MR1"})

    def test_exact_roster_and_global_exclusion_cap(self):
        r = self.runner
        pairs = [{"participant": f"sub-{i:02d}", "condition": condition,
                  "trials": r.expected_trials(f"sub-{i:02d}", condition)}
                 for i in range(1, 11) for condition, _ in r.CONDITIONS]
        r.validate_pairs(pairs)
        for pair in pairs[:7]:
            pair["trials"] -= 1
        r.validate_pairs(pairs)
        pairs[7]["trials"] -= 1
        with self.assertRaisesRegex(RuntimeError, "cohort_exclusion_cap"):
            r.validate_pairs(pairs)
        pairs[7]["trials"] += 1
        pairs[0] = dict(pairs[1])
        with self.assertRaisesRegex(RuntimeError, "exact_thirty_pair_roster"):
            r.validate_pairs(pairs)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_timing_uses_original_excluded_predecessor_and_explicit_flags(self):
        from neurodecodekit.datasets.inner_speech_observed import parse_observed_slots
        slots = parse_observed_slots(generated_events(), participant="sub-01")
        r = self.runner
        intact = r.timing_features(slots, 2)
        self.assertEqual(intact.shape, (11,))
        slots[1] = replace(slots[1], cue=None, label=None)  # excluded, but observed rest stays
        self.assertFalse(slots[1].eligible)
        np.testing.assert_array_equal(r.timing_features(slots, 2), intact)
        slots[1] = replace(slots[1], rest=None)
        changed = r.timing_features(slots, 2)
        self.assertEqual((changed[7], changed[9]), (0, 0))
        slots[2] = replace(slots[2], start=None, rest=None)
        changed = r.timing_features(slots, 2)
        self.assertTrue(all(changed[i] == 0 for i in (0, 3, 6, 7, 8, 9, 10)))

    @unittest.skipIf(np is None, "NumPy optional")
    def test_last_person_disagreement_stops_before_any_physiology_or_fit(self):
        r, reports = self.runner, {}
        inventory = [(f"sub-{i:02d}", Path(f"generated-{i}.bdf"), "generated") for i in range(1, 11)]
        events = generated_events()
        reader = SimpleNamespace(iter_status_events=lambda *args, **kwargs: events)
        budget = SimpleNamespace(check=lambda: None, storage=lambda: None, stage=None,
                                 participant=None, gate_active=False)
        calls = []

        def reference(*args, participant, **kwargs):
            calls.append(participant)
            # Count-identical, different observed cue identity MUST refuse.
            return [(sample, 32 if code == 31 else code) for sample, code in events] if (
                participant == "sub-10") else events

        with mock.patch.object(r, "source_inventory", return_value=inventory), \
                mock.patch.object(r, "sha256", return_value="generated"), \
                mock.patch.object(r, "write_json", side_effect=lambda p, value: reports.update({p.name: value})), \
                mock.patch("neurodecodekit.datasets.inner_speech.BDFReader", return_value=reader), \
                mock.patch("neurodecodekit.datasets.inner_speech_reference_status.reference_status_events", side_effect=reference), \
                mock.patch("neurodecodekit.experiments.inner_speech.preflight_condition", return_value={}), \
                mock.patch.object(r, "participant_features", side_effect=AssertionError("No physiology")), \
                mock.patch("neurodecodekit.experiments.inner_speech.run_condition", side_effect=AssertionError("No fit")):
            with self.assertRaisesRegex(RuntimeError, "decoder_disagreement"):
                r.predict(budget, {})
        self.assertEqual(calls, [p for p, _, _ in inventory])
        self.assertFalse(reports["decoder_gate.json"]["participants_checked"][-1]["core_agreement"])
        self.assertNotIn("qualification.json", reports)
        self.assertTrue(budget.gate_active)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_completed_gate_preserves_all_slots_and_zero_physiology(self):
        r, reports = self.runner, {}
        inventory = [(f"sub-{i:02d}", Path(f"generated-{i}.bdf"), "generated") for i in range(1, 11)]
        events = generated_events()
        # One unambiguously incomplete cue slot, identically seen by both decoders.
        events.pop(next(i for i, (_, code) in enumerate(events) if code == 31))
        reader = SimpleNamespace(iter_status_events=lambda *args, **kwargs: events)
        with mock.patch("neurodecodekit.datasets.inner_speech.BDFReader", return_value=reader), \
                mock.patch("neurodecodekit.datasets.inner_speech_reference_status.reference_status_events", return_value=events), \
                mock.patch("neurodecodekit.experiments.inner_speech.preflight_condition", return_value={}), \
                mock.patch.object(r, "write_json", side_effect=lambda p, value: reports.update({p.name: value})), \
                mock.patch.object(r, "sha256", return_value="generated"):
            # Ten people each losing one core exceeds the COHORT limit, despite every local parse passing.
            with self.assertRaisesRegex(RuntimeError, "cohort_exclusion_cap"):
                r.qualify_all(inventory, SimpleNamespace(check=lambda: None))
        self.assertNotIn("qualification.json", reports)

    @unittest.skipIf(np is None, "NumPy optional")
    def test_reused_one_shot_scorer_with_successor_metadata(self):
        from tests import test_inner_speech_runner as original_test
        r = self.runner
        write = r.write_json

        def generated_write(path, payload):
            if path.name == "qualification.json":
                gate = path.parent / "decoder_gate.json"
                write(gate, {"status": "passed", "generated_only": True})
                payload = {"nominal_trials": 2000, "trials": 2000, "trials_excluded": 0,
                           "decoder_gate_sha256": r.sha256(gate), "participants": [
                               {"participant": f"sub-{i:02d}", "condition_counts_eligible": {
                                   str(code): r.expected_trials(f"sub-{i:02d}", condition)
                                   for condition, code in r.CONDITIONS}} for i in range(1, 11)]}
            write(path, payload)

        with mock.patch.object(original_test, "runner", r), \
                mock.patch.object(r, "write_json", side_effect=generated_write):
            original_test.RunnerTests.test_synthetic_one_shot_score_consumes_before_loading_targets(self)


if __name__ == "__main__":
    unittest.main()
