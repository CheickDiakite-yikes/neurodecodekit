"""Generated event structure only; no BDF, participant or private artifact reads."""

from dataclasses import FrozenInstanceError, asdict, replace
import json
import unittest

from neurodecodekit.datasets.inner_speech import InnerSpeechRefusal, parse_trials
from neurodecodekit.datasets.inner_speech_observed import (
    ObservedSlot, PHASE_NAMES, PHASE_RANK, parse_observed_slots,
)


def generated_events(*, conditions=(21, 22, 22, 23, 23), trials_per_run=40,
                     intervals=(512, 512, 2560, 1024)):
    events, sample = [], 0

    def add(code, delta=4):
        nonlocal sample
        sample += delta
        events.append((sample, code))

    add(11)
    add(13)
    add(14, 15 * 1024)
    for run, condition in enumerate(conditions):
        add(15)
        add(condition)
        for trial in range(trials_per_run):
            add(42, 2048)
            for code, delta in zip((31 + trial % 4, 44, 45, 46), intervals):
                add(code, delta)
        add(16)
        if run < 4:
            add(51)
    add(12)
    return events


def without_phases(events, missing):
    phase_positions = [index for index, (_, code) in enumerate(events) if code in PHASE_RANK]
    removed = {phase_positions[slot * 5 + phase] for slot, phase in missing}
    return [event for index, event in enumerate(events) if index not in removed]


class ObservedSlotTests(unittest.TestCase):
    def test_intact_slots_match_strict_parser_exactly_and_are_frozen(self):
        events, summary = generated_events(), {}
        slots = parse_observed_slots(events, participant="sub-01", summary=summary)
        expected = [ObservedSlot(**asdict(trial), original_index=index)
                    for index, trial in enumerate(parse_trials(events, participant="sub-01"))]
        self.assertEqual(slots, expected)
        self.assertEqual([slot.original_index for slot in slots], list(range(200)))
        self.assertTrue(all(slot.eligible for slot in slots))
        self.assertEqual((summary["slots"], summary["eligible"], summary["excluded"]), (200, 200, 0))
        self.assertEqual(summary["condition_counts_nominal"], {"21": 40, "22": 80, "23": 80})
        with self.assertRaises(FrozenInstanceError):
            slots[0].label = 99

    def test_each_single_missing_phase_preserves_every_other_observation_and_index(self):
        original = generated_events()
        complete = parse_observed_slots(original, participant="sub-01")
        for slot_index in (0, 3, 39, 40, 199):
            for phase, name in enumerate(PHASE_NAMES):
                events = without_phases(original, [(slot_index, phase)])
                before, summary = events.copy(), {}
                slots = parse_observed_slots(events, participant="sub-01", summary=summary)
                updates = {name: None}
                if name == "cue":
                    updates["label"] = None
                expected = complete.copy()
                expected[slot_index] = replace(expected[slot_index], **updates)
                with self.subTest(slot=slot_index, missing=name):
                    self.assertEqual(slots, expected)
                    self.assertEqual(events, before)
                    excluded = int(name in ("cue", "action", "relax"))
                    self.assertEqual(summary["excluded"], excluded)
                    self.assertEqual(summary["eligible"], 200 - excluded)
                    self.assertEqual(slots[slot_index].eligible, not excluded)
                    self.assertEqual(summary["inferred_target_count"], 0)
                    self.assertEqual(summary["synthesized_event_count"], 0)

    def test_seven_core_exclusions_are_not_reindexed_and_eight_refuse(self):
        original = generated_events()
        missing = [(index, 1 + index % 3) for index in range(1, 8)]
        summary = {}
        slots = parse_observed_slots(without_phases(original, missing), participant="sub-01", summary=summary)
        self.assertEqual(summary["excluded"], 7)
        self.assertEqual(sum(summary["exclusion_reasons"].values()), 7)
        self.assertEqual([slot.original_index for slot in slots if slot.eligible], [0, *range(8, 200)])
        self.assertEqual(summary["condition_counts_eligible"], {"21": 33, "22": 80, "23": 80})
        summary_text = json.dumps(summary, allow_nan=False)
        for forbidden in ("original_index", "excluded_indices", "timestamp", '"label"', '"events"'):
            self.assertNotIn(forbidden, summary_text)
        unchanged = {"sentinel": True}
        with self.assertRaisesRegex(InnerSpeechRefusal, "exclusion_cap"):
            parse_observed_slots(without_phases(original, missing + [(8, 1)]),
                                 participant="sub-01", summary=unchanged)
        self.assertEqual(unchanged, {"sentinel": True})

    def test_missing_start_and_rest_are_retained_but_never_two_missing_phases_in_one_slot(self):
        original = generated_events()
        missing = [(index, 0 if index % 2 else 4) for index in range(200)]
        summary = {}
        slots = parse_observed_slots(without_phases(original, missing), participant="sub-01", summary=summary)
        self.assertTrue(all(slot.eligible for slot in slots))
        self.assertEqual(summary["missing_start_events"], 100)
        self.assertEqual(summary["missing_rest_events"], 100)
        for missing in ([(3, 0), (3, 4)], [(3, 1), (3, 2)], [(3, rank) for rank in range(5)]):
            with self.subTest(missing=missing), self.assertRaises(InnerSpeechRefusal):
                parse_observed_slots(without_phases(original, missing), participant="sub-01")

    def test_duplicate_rank_reordering_and_nonunique_slot_counts_refuse(self):
        original = generated_events()
        cue = next(index for index, (_, code) in enumerate(original) if code == 31)
        duplicate = original[:cue + 1] + [(original[cue][0] + 1, 32)] + original[cue + 1:]
        with self.assertRaisesRegex(InnerSpeechRefusal, "duplicate_phase_rank"):
            parse_observed_slots(duplicate, participant="sub-01")
        swapped = original.copy()
        swapped[cue] = (original[cue][0], 44)
        swapped[cue + 1] = (original[cue + 1][0], 31)
        doubled_start = original[:cue] + [(original[cue - 1][0] + 1, 42)] + original[cue:]
        for events in (swapped, doubled_start, generated_events(trials_per_run=39),
                       generated_events(trials_per_run=41), original[:-1],
                       original + [(original[-1][0] + 4, 42)]):
            with self.subTest(length=len(events)), self.assertRaises(InnerSpeechRefusal):
                parse_observed_slots(events, participant="sub-01")

    def test_all_available_timing_bounds_apply_even_to_excluded_slots(self):
        for bounds in ((1, 384, 2048, 1), (5120, 3072, 4096, 3072)):
            self.assertEqual(len(parse_observed_slots(generated_events(intervals=bounds), participant="sub-01")), 200)
        for bounds in ((0, 512, 2560, 1024), (5121, 512, 2560, 1024),
                       (512, 383, 2560, 1024), (512, 3073, 2560, 1024),
                       (512, 512, 2047, 1024), (512, 512, 4097, 1024),
                       (512, 512, 2560, 0), (512, 512, 2560, 3073)):
            with self.subTest(bounds=bounds), self.assertRaises(InnerSpeechRefusal):
                parse_observed_slots(generated_events(intervals=bounds), participant="sub-01")
        invalid_action = without_phases(generated_events(intervals=(512, 512, 2047, 1024)), [(3, 1)])
        with self.assertRaisesRegex(InnerSpeechRefusal, "trial_timing"):
            parse_observed_slots(invalid_action, participant="sub-01")
        # This excluded cue-missing slot still has an observed, invalid action interval.
        valid = generated_events()
        phase_positions = [i for i, (_, code) in enumerate(valid) if code in PHASE_RANK]
        relax = phase_positions[3 * 5 + 3]
        invalid_one = valid.copy()
        invalid_one[relax] = (valid[relax - 1][0] + 2047, 45)
        with self.assertRaisesRegex(InnerSpeechRefusal, "trial_timing"):
            parse_observed_slots(without_phases(invalid_one, [(3, 1)]), participant="sub-01")

    def test_attention_is_only_after_observed_rest_and_counts_match_old_parser(self):
        original = generated_events()
        rest = next(index for index, (_, code) in enumerate(original) if code == 46)
        extras = [(original[rest][0] + offset, code)
                  for offset, code in enumerate((62, 17, 17, 61, 64, 17), 1)]
        events = original[:rest + 1] + extras + original[rest + 1:]
        old_summary, summary = {}, {}
        parse_trials(events, participant="sub-01", summary=old_summary)
        parse_observed_slots(events, participant="sub-01", summary=summary)
        for key in ("attention_question_events", "attention_answer_events",
                    "unpaired_attention_questions", "unpaired_attention_answers"):
            self.assertEqual(summary[key], old_summary[key])
        self.assertEqual(summary["unpaired_attention_questions"], 2)
        self.assertEqual(summary["unpaired_attention_answers"], 2)
        with self.assertRaisesRegex(InnerSpeechRefusal, "attention_requires_observed_rest"):
            parse_observed_slots(without_phases(events, [(0, 4)]), participant="sub-01")
        cue = next(index for index, (_, code) in enumerate(original) if code == 31)
        premature = original[:cue + 1] + [(original[cue][0] + 1, 17)] + original[cue + 1:]
        with self.assertRaises(InnerSpeechRefusal):
            parse_observed_slots(premature, participant="sub-01")

    def test_sub03_sub10_optional_interrun_and_input_refusals(self):
        original = generated_events()
        summary = {}
        corrected = parse_observed_slots(original, participant="sub-03", summary=summary)
        self.assertTrue(summary["condition_correction_applied"])
        self.assertEqual(summary["condition_counts_nominal"], {"21": 40, "22": 40, "23": 120})
        already = generated_events(conditions=(21, 22, 23, 23, 23))
        self.assertEqual(corrected, parse_observed_slots(already, participant="sub-03", summary=summary))
        self.assertTrue(summary["condition_correction_already_present"])
        with self.assertRaisesRegex(InnerSpeechRefusal, "condition_layout"):
            parse_observed_slots(already, participant="sub-01")
        no_baseline_end = [event for event in original if event[1] != 14]
        parse_observed_slots(no_baseline_end, participant="sub-10", summary=summary)
        self.assertTrue(summary["baseline_end_missing"])
        with self.assertRaisesRegex(InnerSpeechRefusal, "baseline_end_missing"):
            parse_observed_slots(no_baseline_end, participant="sub-01")
        no_interrun = [event for event in original if event[1] != 51]
        parse_observed_slots(no_interrun, participant="sub-01", summary=summary)
        self.assertEqual(summary["missing_inter_run_rest_tags"], 4)
        for participant, session in (("sub-11", "ses-01"), ("sub-01", "ses-02")):
            with self.assertRaises(InnerSpeechRefusal):
                parse_observed_slots(original, participant=participant, session=session)
        for events in (None, [], [(None, 11)], [(True, 11)], [(0, True)],
                       [original[0], original[0], *original[1:]], original[::-1]):
            with self.subTest(events_type=type(events).__name__), self.assertRaises(InnerSpeechRefusal):
                parse_observed_slots(events, participant="sub-01")


if __name__ == "__main__":
    unittest.main()
