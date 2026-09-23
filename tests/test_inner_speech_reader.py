"""Generated BDFs/events only; never read acquired participant files."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

from neurodecodekit.datasets.inner_speech import (
    BDFReader,
    EEG_CHANNELS,
    EXG_CHANNELS,
    InnerSpeechRefusal,
    parse_trials,
)


def generated_events(conditions=(21, 22, 22, 23, 23), questions=True):
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
        for trial in range(40):
            add(42, 2048)
            add(31 + trial % 4, 512)
            add(44, 512)
            add(45, 2560)
            add(46, 1024)
            if questions and condition != 21 and trial % 7 == 0:
                add(17)
                add(61 + trial % 4, 2000)
        add(16)
        if run < 4:
            add(51)
    add(12)
    return events


def generated_bdf(path, *, records=3, replacements=None):
    labels = EEG_CHANNELS + EXG_CHANNELS + ("Status",)
    count = len(labels)

    def field(value, width):
        return str(value).encode("ascii").ljust(width, b" ")

    header = (b"\xffBIOSEMI" + field("UNREPORTED PATIENT", 80) +
              field("UNREPORTED RECORDING", 80) + field("01.01.00", 8) +
              field("01.02.03", 8) + field(256 * (count + 1), 8) +
              field("24BIT", 44) + field(records, 8) + field(1, 8) + field(count, 4))
    header += b"".join(field(name, 16) for name in labels)
    # pmin=10, pmax=25 and digital -8..7 imply microvolts=digital+18.
    for width, value in ((80, ""), (8, "uV"), (8, 10), (8, 25),
                         (8, -8), (8, 7), (80, ""), (8, 1024), (32, "")):
        header += field(value, width) * count
    replacements = replacements or {}
    with path.open("wb") as stream:
        stream.write(header)
        for record in range(records):
            for channel in labels:
                values = replacements.get(channel, {})
                data = bytearray()
                for index in range(1024):
                    value = values.get(record * 1024 + index, 0)
                    data.extend((value & 0xFFFFFF).to_bytes(3, "little"))
                stream.write(data)
    return len(header)


class TrialParserTests(unittest.TestCase):
    def test_complete_trials_and_event_relative_windows(self):
        summary = {}
        trials = parse_trials(generated_events(), participant="sub-01", summary=summary)
        self.assertEqual(len(trials), 200)
        self.assertEqual([trials[i].condition for i in (0, 40, 80, 120, 160)],
                         [21, 22, 22, 23, 23])
        self.assertEqual([trial.label for trial in trials[:4]], [0, 1, 2, 3])
        self.assertEqual(trials[-1].run_ordinal, 5)
        self.assertEqual(summary["inferred_target_count"], 0)
        self.assertEqual(summary["synthesized_event_count"], 0)
        for trial in trials:
            self.assertGreaterEqual(trial.relax - 2048, trial.action)
            self.assertLessEqual(trial.cue + 384, trial.action)
            self.assertGreaterEqual(trial.relax - 384, trial.action)

    def test_sub03_correction_is_exact_and_idempotent(self):
        summary = {}
        trials = parse_trials(generated_events(), participant="sub-03", summary=summary)
        self.assertTrue(summary["condition_correction_applied"])
        self.assertEqual(sum(trial.condition == 22 for trial in trials), 40)
        self.assertEqual(sum(trial.condition == 23 for trial in trials), 120)
        corrected = generated_events((21, 22, 23, 23, 23))
        self.assertEqual(trials, parse_trials(corrected, participant="sub-03", summary=summary))
        self.assertFalse(summary["condition_correction_applied"])
        self.assertTrue(summary["condition_correction_already_present"])
        with self.assertRaisesRegex(InnerSpeechRefusal, "condition_layout"):
            parse_trials(corrected, participant="sub-02")

    def test_missing_baseline_end_only_sub10_and_never_synthesized(self):
        events = [item for item in generated_events() if item[1] != 14]
        summary = {}
        self.assertEqual(len(parse_trials(events, participant="sub-10", summary=summary)), 200)
        self.assertTrue(summary["baseline_end_missing"])
        self.assertEqual(summary["synthesized_event_count"], 0)
        with self.assertRaisesRegex(InnerSpeechRefusal, "baseline_end_missing"):
            parse_trials(events, participant="sub-01")

    def test_unused_attention_and_inter_run_rest_do_not_change_trials(self):
        events = generated_events()
        expected = parse_trials(events, participant="sub-01")
        # Drop one question and a different answer, preserving two unpaired events.
        first_question = next(i for i, item in enumerate(events) if item[1] == 17)
        later_answer = next(i for i, item in enumerate(events)
                            if i > first_question + 1 and item[1] in (61, 62, 63, 64))
        changed = [item for i, item in enumerate(events)
                   if i not in (first_question, later_answer) and item[1] != 51]
        summary = {}
        self.assertEqual(parse_trials(changed, participant="sub-01", summary=summary), expected)
        self.assertEqual(summary["unpaired_attention_questions"], 1)
        self.assertEqual(summary["unpaired_attention_answers"], 1)
        self.assertEqual(summary["missing_inter_run_rest_tags"], 4)
        self.assertEqual(summary["trials"], 200)
        self.assertEqual(summary["synthesized_event_count"], 0)

    def test_attention_inside_trial_and_missing_run_markers_still_refuse(self):
        events = generated_events()
        action = next(i for i, item in enumerate(events) if item[1] == 44)
        for code in (17, 61, 65):
            interrupted = events[:action + 1] + [(events[action][0] + 1, code)] + events[action + 1:]
            with self.subTest(code=code), self.assertRaisesRegex(InnerSpeechRefusal, "event_grammar"):
                parse_trials(interrupted, participant="sub-01")
        for missing_code in (15, 16, 42, 44, 45, 46):
            index = next(i for i, item in enumerate(events) if item[1] == missing_code)
            incomplete = events[:index] + events[index + 1:]
            with self.subTest(missing_code=missing_code), self.assertRaises(InnerSpeechRefusal):
                parse_trials(incomplete, participant="sub-01")

    def test_no_missing_target_repair_no_drop_and_no_extra_codes(self):
        original = generated_events()
        first_cue = next(i for i, item in enumerate(original) if item[1] == 31)
        missing = original[:first_cue] + original[first_cue + 1:]
        wrong_target = original.copy()
        wrong_target[first_cue] = (original[first_cue][0], 35)
        wrong_timing = original.copy()
        wrong_timing[first_cue] = (original[first_cue][0] + 129, 31)  # cue below384samples
        for events in (missing, wrong_target, wrong_timing, original[:-1],
                       original + [(original[-1][0] + 4, 42)],
                       generated_events((21, 23, 22, 23, 23)),
                       original[:first_cue] + [(original[first_cue][0], 65536)] +
                       original[first_cue:]):
            with self.subTest(events=len(events)), self.assertRaises(InnerSpeechRefusal):
                parse_trials(events, participant="sub-01")

    def test_timing_bounds_diagnostics_and_identity_are_fixed(self):
        events = generated_events()
        cue = next(i for i, item in enumerate(events) if item[1] == 31)
        events[cue] = (events[cue][0] + 103, 31)
        summary = {}
        self.assertEqual(len(parse_trials(events, participant="sub-01", summary=summary)), 200)
        self.assertEqual(summary["interval_timing"]["cue"]["deviation_over_0_1s_count"], 1)
        self.assertEqual(summary["interval_timing"]["concentration"]["deviation_over_0_1s_count"], 1)
        self.assertEqual(summary["interval_timing"]["action"]["deviation_over_0_1s_count"], 0)
        for participant, session in (("sub-11", "ses-01"), ("sub-01", "ses-02")):
            with self.assertRaisesRegex(InnerSpeechRefusal, "participant_session"):
                parse_trials(events, participant=participant, session=session)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional numpy unavailable")
class BDFReaderTests(unittest.TestCase):
    def test_signed_24bit_scaling_and_record_crossing(self):
        import numpy as np
        values = {1022: -8, 1023: -1, 1024: 0, 1025: 7}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            generated_bdf(path, replacements={"A1": values, "EXG8": {1024: -2}})
            reader = BDFReader(path)
            self.assertEqual((reader.sfreq, reader.n_samples), (1024, 3072))
            result = reader.read_window(1022, 1026, ["A1", "EXG8"])
            np.testing.assert_array_equal(result, [[10, 17, 18, 25], [18, 18, 16, 18]])
            self.assertEqual(result.dtype, np.float64)

    def test_signed_24bit_extremes(self):
        from neurodecodekit.datasets.inner_speech import _decode24
        import numpy as np
        values = [-8388608, -1, 0, 1, 8388607]
        data = b"".join((value & 0xFFFFFF).to_bytes(3, "little") for value in values)
        np.testing.assert_array_equal(_decode24(data, signed=True), values)

    def test_status_edges_mask_initial_crossrecord_and_source_exception(self):
        status = {index: 65536 for index in range(3072)}
        for index, value in {0: 11, 1: 11, 2: 11, 20: 14, 21: 14,
                             1023: 31, 1024: 31, 1025: 31,
                             1026: 44, 1027: 44, 1028: 44, 2000: 45}.items():
            status[index] |= value
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            generated_bdf(path, replacements={"Status": status})
            reader, calls = BDFReader(path), []
            events = reader.iter_status_events(lambda: calls.append(1), participant="sub-01")
            self.assertEqual(events, [(0, 11), (20, 14), (1023, 31), (1026, 44), (2000, 45)])
            self.assertEqual(len(calls), 3)
            self.assertEqual(reader.status_summary["short_pulses_below_three"], 2)
            self.assertEqual(reader.status_summary["nonzero_highbit_samples"], 3072)
            self.assertEqual(reader.status_summary["ignored_short_pulses"], 0)
            events = reader.iter_status_events(participant="sub-10")
            self.assertEqual(events, [(0, 11), (1023, 31), (1026, 44)])
            self.assertEqual(reader.status_summary["ignored_short_pulses"], 2)

    def test_window_refuses_status_bounds_duplicates_and_file_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            generated_bdf(path, records=5)
            reader = BDFReader(path)
            for start, stop, picks in ((0, 4097, ["A1"]), (-1, 2, ["A1"]),
                                       (0, 1, ["Status"]), (0, 1, [136]),
                                       (0, 1, ["A1", "A1"]), (0, 1, [True])):
                with self.assertRaises(InnerSpeechRefusal):
                    reader.read_window(start, stop, picks)
            with path.open("ab") as stream:
                stream.write(b"x")
            with self.assertRaisesRegex(InnerSpeechRefusal, "file_changed"):
                reader.read_window(0, 2, ["A1"])

    def test_header_geometry_calibration_and_channel_refusals(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            generated_bdf(path, records=1)
            original = path.read_bytes()
            count = 137
            mutations = [
                (0, b"0       "),
                (256 + 135 * 16, b"Missing         "),
                (256 + 96 * count, b"mV      "),
                (256 + 120 * count, b"7       "),
                (256 + 216 * count, b"512     "),
            ]
            for offset, value in mutations:
                path.write_bytes(original[:offset] + value + original[offset + len(value):])
                with self.subTest(offset=offset), self.assertRaises(InnerSpeechRefusal):
                    BDFReader(path)
            path.write_bytes(original[:-1])
            with self.assertRaisesRegex(InnerSpeechRefusal, "file_geometry"):
                BDFReader(path)


if __name__ == "__main__":
    unittest.main()
