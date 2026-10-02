"""Generated structural fixtures only: no source reads or scientific parsing."""

import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts/inner_speech_session2_structure.py"


def load_module():
    spec = importlib.util.spec_from_file_location("session2_structure_tested", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STRUCTURE = load_module()


def observed(codes):
    sample, events = 123456789, []
    for code in codes:
        sample += {31: 512, 32: 512, 33: 512, 34: 512,
                   44: 1024, 45: 2560, 46: 1024}.get(code, 100)
        events.append((sample, code))
    return events


class Session2StructureTests(unittest.TestCase):
    def assert_accounting(self, result):
        self.assertEqual(sum(result["event_family_counts"].values()), result["events"])
        self.assertEqual(result["events_inside_intact_run_boundaries"] +
                         result["events_outside_or_ambiguous_run_boundaries"], result["events"])
        self.assertEqual(sum(p["segments"] for p in result["structural_segment_patterns"]),
                         result["structural_segments"])
        self.assertEqual(sum(p["runs"] for p in result["per_run_segment_count_histogram"]),
                         result["intact_run_boundary_pairs"])
        self.assertEqual(sum(p["runs"] * p["structural_segments"]
                             for p in result["per_run_segment_count_histogram"]),
                         result["structural_segments"])
        self.assertEqual(sum(result["per_run_condition_marker_multiplicity_histogram"].values()),
                         result["intact_run_boundary_pairs"])
        self.assertEqual(sum(p["groups"] for p in result["attention_context_patterns"]),
                         result["attention_groups"])
        self.assertEqual(result["attention_events"], sum(result["event_family_counts"].get(f, 0)
                         for f in STRUCTURE.ATTENTION))
        self.assertEqual(result["parser_calls"], 0)
        self.assertEqual(result["events_changed"], 0)
        self.assertEqual(result["labels_inferred"], 0)
        self.assertFalse(result["alignment_or_scientific_qualification_established"])

    def test_complete_and_empty_accounting_input_unchanged(self):
        events = observed([15, 21, 42, 31, 44, 45, 46, 17, 61,
                           42, 32, 44, 45, 46, 16])
        before = events.copy()
        for fixture in ([], events):
            result = STRUCTURE.analyze_structure(fixture)
            self.assert_accounting(result)
        self.assertEqual(events, before)
        self.assertEqual(result["intact_run_boundary_pairs"], 1)
        self.assertEqual(result["structural_segments"], 2)
        self.assertEqual(result["per_run_segment_count_histogram"], [{"structural_segments": 2, "runs": 1}])
        self.assertEqual(result["per_run_condition_marker_multiplicity_histogram"],
                         {"zero": 0, "one": 1, "multiple": 0})
        context = result["attention_context_patterns"][0]
        self.assertEqual(context["preceding_family"], "rest")
        self.assertEqual(context["next_family"], "trial_start")
        self.assertEqual(context["previous_observed_core_phase"], "rest")
        self.assertEqual(set(context["segment_signature"]["phase_counts"].values()), {"one"})
        self.assertFalse(context["segment_signature"]["ambiguous_structure"])

    def test_absent_rest_after_intact_core_distinct_from_attention_interruption(self):
        after = STRUCTURE.analyze_structure(observed(
            [15, 42, 31, 44, 45, 17, 61, 42, 32, 44, 45, 46, 16]))
        interrupted = STRUCTURE.analyze_structure(observed(
            [15, 42, 31, 44, 17, 61, 45, 42, 32, 44, 45, 46, 16]))
        a, b = (r["attention_context_patterns"][0] for r in (after, interrupted))
        self.assertEqual(a["previous_observed_core_phase"], "relax")
        self.assertEqual(b["previous_observed_core_phase"], "action")
        self.assertEqual(a["next_family"], "trial_start")
        self.assertEqual(b["next_family"], "relax")
        for context in (a, b):
            self.assertEqual(context["segment_signature"]["phase_counts"]["rest"], "zero")
        self.assertTrue(a["segment_signature"]["contiguous_cue_action_relax"])
        self.assertFalse(a["segment_signature"]["attention_between_observed_phases"])
        self.assertFalse(b["segment_signature"]["contiguous_cue_action_relax"])
        self.assertTrue(b["segment_signature"]["attention_between_observed_phases"])
        self.assertEqual(set(a["segment_signature"]["observed_core_window_checks"].values()),
                         {"within_range"})
        self.assertEqual(a["segment_signature"]["observed_phase_interval_checks"]["relax_to_rest"],
                         "unavailable_missing_or_duplicate")

    def test_missing_start_and_run_end_attention_remain_observed_not_imputed(self):
        result = STRUCTURE.analyze_structure(observed([15, 31, 44, 45, 17, 61, 16]))
        pattern = result["structural_segment_patterns"][0]
        self.assertEqual(pattern["phase_counts"]["trial_start"], "zero")
        self.assertEqual(pattern["phase_counts"]["rest"], "zero")
        self.assertEqual(pattern["ending_boundary_family"], "run_end")
        self.assertFalse(pattern["ambiguous_structure"])
        self.assertEqual(result["attention_context_patterns"][0]["next_family"], "run_end")
        self.assert_accounting(result)

    def test_all_duplicates_out_of_order_unknown_and_early_resets_retained(self):
        result = STRUCTURE.analyze_structure(observed(
            [15, 42, 31, 44, 44, 45, 46,
             42, 31, 44, 45, 44, 46,
             42, 31, 987654321, 44, 45, 46,
             42, 31, 42, 31, 44, 45, 46, 16]))
        self.assertEqual(result["structural_segments"], 5)
        patterns = result["structural_segment_patterns"]
        self.assertEqual(sum(p["segments"] for p in patterns if p["duplicate_phase"]), 2)
        self.assertEqual(sum(p["segments"] for p in patterns if p["noncore_nonattention_marker"]), 1)
        self.assertTrue(all(p["ambiguous_structure"] for p in patterns))
        self.assert_accounting(result)

    def test_nested_and_unmatched_runs_never_salvage_inner_segments(self):
        result = STRUCTURE.analyze_structure(observed(
            [16, 17, 61, 15, 15, 42, 31, 44, 45, 17, 61, 16, 16,
             15, 42, 31, 44, 45, 46, 16, 15, 42, 17, 61]))
        self.assertEqual(result["intact_run_boundary_pairs"], 1)
        self.assertEqual(result["structural_segments"], 1)
        self.assertEqual(result["unassigned_run_boundary_markers"], 6)
        self.assertEqual(result["malformed_run_boundary_counts"],
                         {"unmatched_run_ends": 1, "nested_run_starts": 1, "unclosed_run_starts": 1})
        self.assertEqual(result["attention_groups_outside_or_ambiguous_runs"], 3)
        self.assertTrue(all(p["segment_signature"] is None
                            for p in result["attention_context_patterns"]))
        self.assert_accounting(result)

    def test_direction_answer_condition_unknown_and_time_offset_invariance(self):
        events = observed([987654321, 15, 21, 42, 31, 44, 45, 17, 61, 16])
        changed = [(sample + 876543210000, {987654321: 987654322, 21: 23, 31: 34, 61: 64}.get(code, code))
                   for sample, code in events]
        result = STRUCTURE.analyze_structure(events)
        self.assertEqual(result, STRUCTURE.analyze_structure(changed))
        encoded = json.dumps(result)
        self.assertNotIn("987654321", encoded)
        self.assertNotIn("876543210000", encoded)
        self.assertNotIn("123456789", encoded)

    def test_per_run_histograms_do_not_hide_unequal_segment_counts(self):
        core = [42, 31, 44, 45, 46]
        result = STRUCTURE.analyze_structure(observed([15] + core + [16, 15, 21, 23] + core * 3 + [16]))
        self.assertEqual(result["per_run_segment_count_histogram"],
                         [{"structural_segments": 1, "runs": 1}, {"structural_segments": 3, "runs": 1}])
        self.assertEqual(result["per_run_condition_marker_multiplicity_histogram"],
                         {"zero": 1, "one": 0, "multiple": 1})
        self.assert_accounting(result)

    def test_interval_edges_core_windows_and_unavailable_categories(self):
        for name, (left, right, lower, upper) in STRUCTURE.INTERVALS.items():
            for delta in (lower - 1, lower, upper, upper + 1):
                gaps = [512, 1024, 2560, 1024]
                gaps[left] = delta
                sample, events = 1000000, [(0, 15), (1000000, 42)]
                for gap, code in zip(gaps, (31, 44, 45, 46)):
                    sample += gap
                    events.append((sample, code))
                events.append((sample + 100, 16))
                result = STRUCTURE.analyze_structure(events)
                signature = result["structural_segment_patterns"][0]
                expected = "within_range" if lower <= delta <= upper else "outside_range"
                if delta == 0:
                    expected = "unavailable_ambiguous_structure"
                    self.assertTrue(signature["nonincreasing_sample_gap"])
                    self.assertEqual(result["nonincreasing_sample_pairs"], 1)
                self.assertEqual(signature["observed_phase_interval_checks"][name], expected)
                if name in ("cue_to_action", "action_to_relax"):
                    window = "cue_384_before_action" if left == 1 else "action_2048_before_relax"
                    self.assertEqual(signature["observed_core_window_checks"][window],
                                     "within_range" if delta >= lower else "outside_range")
        absent = STRUCTURE.analyze_structure(observed([15, 42, 45, 46, 16]))
        self.assertEqual(set(absent["structural_segment_patterns"][0]["observed_core_window_checks"].values()),
                         {"unavailable_missing_or_duplicate"})

    def test_numpy_unavailable_and_parser_or_reader_calls_forbidden(self):
        import neurodecodekit.datasets.inner_speech as reader

        with patch.dict(sys.modules, {"numpy": None}), \
                patch.object(reader, "parse_trials", side_effect=AssertionError("No parser")), \
                patch.object(reader.BDFReader, "__init__", side_effect=AssertionError("No reader")):
            # The already-loaded analyzer calls neither the parser nor a reader.
            result = STRUCTURE.analyze_structure(observed([15, 42, 31, 44, 45, 46, 16]))
            self.assert_accounting(result)
        with patch.dict(sys.modules, {"numpy": None}):
            reloaded = load_module()
            self.assertEqual(reloaded.analyze_structure([])["events"], 0)

    def test_callback_refusal_propagates_and_format_error_is_sanitized(self):
        calls = []

        def refuse():
            calls.append(1)
            if len(calls) == 3:
                raise RuntimeError("resource_limit")

        with self.assertRaisesRegex(RuntimeError, "resource_limit"):
            STRUCTURE.analyze_structure(observed([15, 42, 31, 44, 45, 46, 16]), check=refuse)
        with self.assertRaisesRegex(ValueError, "^event_format$"):
            STRUCTURE.analyze_structure([(123456789, "private_invalid_status")])


if __name__ == "__main__":
    unittest.main()
