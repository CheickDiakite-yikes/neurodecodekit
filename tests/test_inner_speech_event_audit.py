"""Generated event lists only; this module never executes the private audit."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tests.test_inner_speech_reader import generated_events

SPEC = importlib.util.spec_from_file_location(
    "event_audit", Path(__file__).resolve().parents[1] / "scripts/audit_inner_speech_events.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class EventAuditTests(unittest.TestCase):
    def test_existing_traceback_projection_neither_reparses_nor_reads_files(self):
        events = generated_events()
        index = next(i for i, (_, code) in enumerate(events) if code == 31)
        events[index] = (events[index][0], 64)
        try:
            AUDIT.parse_trials(events, participant="sub-01", allow_missing_rest=True)
        except AUDIT.InnerSpeechRefusal as error:
            with patch.object(AUDIT, "parse_trials", side_effect=AssertionError("No reparse")), \
                    patch.object(Path, "open", side_effect=AssertionError("No source read")):
                result = AUDIT.project_parser_refusal(error)
        else:
            self.fail("Generated missing direction must refuse")
        self.assertEqual(result, {
            "parser_status": "refused", "error_code": "event_grammar", "completed_trials": 0,
            "first_mismatch": {"expected_families": ["direction_cue"],
                               "observed_family": "attention_answer"}})

    def test_initial_unknown_is_projected_without_numeric_value_or_repair(self):
        events = [(0, 987654321), *generated_events()]
        before = list(events)
        with patch.object(AUDIT, "parse_trials", wraps=AUDIT.parse_trials) as parser:
            # Preserve the frozen code identity used only to find its traceback frame.
            parser.__code__ = AUDIT.parse_trials._mock_wraps.__code__
            result = AUDIT.diagnose(events)
            self.assertEqual(parser.call_count, 1)
        self.assertEqual(events, before)
        self.assertEqual(result["completed_trials"], 0)
        self.assertEqual(result["first_mismatch"], {
            "expected_families": ["experiment_start"],
            "observed_family": "unrecognized_status_word",
            "is_first_retained_event": True, "is_recording_initial_sample": True,
            "completed_run_end_markers": 0})
        self.assertNotIn("987654321", json.dumps(result))

    def test_missing_direction_and_answer_are_collapsed(self):
        events = generated_events()
        index = next(i for i, (_, code) in enumerate(events) if code == 31)
        events[index] = (events[index][0], 64)
        result = AUDIT.diagnose(events)
        self.assertEqual(result["first_mismatch"]["expected_families"], ["direction_cue"])
        self.assertEqual(result["first_mismatch"]["observed_family"], "attention_answer")
        self.assertEqual({AUDIT.family(c) for c in (31, 32, 33, 34)}, {"direction_cue"})
        self.assertEqual({AUDIT.family(c) for c in (21, 22, 23)}, {"condition_marker"})

    def test_eof_and_non_grammar_refusals_remain_explicit(self):
        result = AUDIT.diagnose(generated_events()[:-1])
        self.assertEqual(result["first_mismatch"]["observed_family"], "end_of_events")
        self.assertEqual(result["completed_trials"], 200)
        self.assertEqual(result["first_mismatch"]["completed_run_end_markers"], 5)
        events = [e for e in generated_events() if e[1] != 14]
        result = AUDIT.diagnose(events)
        self.assertEqual(result["error_code"], "baseline_end_missing")
        self.assertIsNone(result["first_mismatch"])

    def test_intact_events_pass_without_exporting_trials(self):
        result = AUDIT.diagnose(generated_events())
        self.assertEqual(result["parser_status"], "passed")
        self.assertEqual(result["completed_trials"], 200)
        self.assertEqual(set(result), {"parser_status", "completed_trials", "first_mismatch",
                                       "event_family_counts"})
        self.assertEqual(result["event_family_counts"]["direction_cue"], 200)


if __name__ == "__main__":
    unittest.main()
