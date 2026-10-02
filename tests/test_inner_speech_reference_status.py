"""Generated Status only; never open acquired participant recordings."""

import importlib.util
from pathlib import Path
import random
import tempfile
import unittest
from unittest import mock

from neurodecodekit.datasets.inner_speech import BDFReader, InnerSpeechRefusal
from neurodecodekit.datasets.inner_speech_reference_status import (
    OVERFLOW_ONLY,
    STATUS_MASK,
    _onsets,
    _status_steps,
    reference_status_events,
    status_agreement,
)
from tests.test_inner_speech_reader import generated_bdf


def reference_generated(values, *, short_filter=False, record_samples=None):
    record_samples = record_samples or len(values)
    payload = b"".join((value & 0xffffff).to_bytes(3, "little") for value in values)
    records = [payload[i:i + 3 * record_samples] for i in range(0, len(payload), 3 * record_samples)]
    steps, initial, total = _status_steps(records, record_samples, None)
    return _onsets(steps, initial, total, minimum_duration=short_filter)


class ReferenceStatusTests(unittest.TestCase):
    def test_initial_final_and_direct_nonzero_transitions(self):
        self.assertEqual(reference_generated([31]*4 + [44]*4 + [45]*4),
                         [(0, 31), (4, 44), (8, 45)])
        self.assertEqual(reference_generated([0]*4 + [31]*4), [(4, 31)])
        self.assertEqual(reference_generated([31]*4 + [0]*4), [(0, 31)])
        self.assertEqual(reference_generated([0]*8), [])
        # Source's no-transition early return, not a made-up final offset.
        self.assertEqual(reference_generated([31]*8), [])

    def test_seventeenth_bit_preserved_overflow_dropped_after_edges(self):
        values = [0]*4 + [OVERFLOW_ONLY]*4 + [OVERFLOW_ONLY+31]*4 + [31]*4 + [0]*4
        self.assertEqual(reference_generated(values), [(8, OVERFLOW_ONLY+31), (12, 31)])
        higher_bits = [(0x800000 | value) for value in values]
        self.assertEqual(reference_generated(higher_bits), reference_generated(values))
        self.assertFalse(status_agreement([(8, 31)], reference_generated(values))["core_events_match"])

    def test_duration_filter_is_simultaneous_step_merge_not_pulse_discard(self):
        values = [0]*4 + [31]*2 + [44]*4 + [0]*4
        self.assertEqual(reference_generated(values), [(4, 31), (6, 44)])
        self.assertEqual(reference_generated(values, short_filter=True), [(6, 44)])
        # A short zero gap merges towards the later step; initial marker stays.
        values = [31]*4 + [0] + [44]*4 + [0]*4
        self.assertEqual(reference_generated(values, short_filter=True), [(0, 31), (5, 44)])
        # Simultaneous, not recursive: the last step inherits the immediately
        # previous ORIGINAL pre-value, even across multiple close transitions.
        values = [0]*4 + [31] + [44] + [45]*4 + [0]*4
        self.assertEqual(reference_generated(values, short_filter=True), [(6, 45)])

    def test_initial_event_is_inserted_after_duration_filter(self):
        self.assertEqual(reference_generated([31] + [0]*7, short_filter=True), [(0, 31)])
        self.assertEqual(reference_generated([0]*7 + [31], short_filter=True), [])

    def test_shortest_event_default_before_overflow_exclusion(self):
        with self.assertRaisesRegex(InnerSpeechRefusal, "reference_shortest_event"):
            reference_generated([0]*4 + [31] + [44]*4 + [0]*4)
        with self.assertRaisesRegex(InnerSpeechRefusal, "reference_shortest_event"):
            reference_generated([0]*4 + [OVERFLOW_ONLY] + [31]*4 + [0]*4)
        self.assertEqual(reference_generated([0]*4 + [31] + [0]*4), [(4, 31)])

    def test_record_boundaries_do_not_change_semantics(self):
        values = [0]*6 + [31]*6 + [44]*8 + [45]*4 + [0]*8
        for short in (False, True):
            expected = reference_generated(values, short_filter=short)
            for size in (1, 2, 4, 8, 16):
                self.assertEqual(reference_generated(values, short_filter=short, record_samples=size), expected)

    def test_bounds_and_callback(self):
        with self.assertRaisesRegex(InnerSpeechRefusal, "reference_status_truncated"):
            _status_steps([b"\x00\x00"], 1, None)
        with self.assertRaisesRegex(InnerSpeechRefusal, "reference_empty_status"):
            _status_steps([], 1, None)
        with mock.patch("neurodecodekit.datasets.inner_speech_reference_status.MAX_STEPS", 1):
            with self.assertRaisesRegex(InnerSpeechRefusal, "reference_transition_limit"):
                reference_generated([0, 31, 0])
        check = mock.Mock(side_effect=RuntimeError("generated deadline"))
        with self.assertRaisesRegex(RuntimeError, "generated deadline"):
            _status_steps([b"\x00\x00\x00"], 1, check)

    def test_private_exact_agreement_includes_context_not_nonanchor_repair(self):
        original = [(0, 11), (4, 15), (8, 22), (12, 31), (16, 44), (20, 45), (24, 46)]
        self.assertEqual(status_agreement(original, original[:-1]),
                         {"core_events_match": True, "context_events_match": True})
        changed = list(original)
        changed[3] = (12, 32)
        self.assertFalse(status_agreement(original, changed)["core_events_match"])
        changed[3] = (13, 31)
        self.assertFalse(status_agreement(original, changed)["core_events_match"])
        changed[3], changed[4] = original[4], original[3]
        self.assertFalse(status_agreement(original, changed)["core_events_match"])
        changed = [(sample, 23 if code == 22 else code) for sample, code in original]
        self.assertFalse(status_agreement(original, changed)["context_events_match"])

    def test_bdf_record_only_reads_and_independent_decoder(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            words = {i: code for start, stop, code in ((0, 4, 11), (1022, 1026, 31),
                (1030, 1034, 44), (2044, 2048, 45)) for i in range(start, stop)}
            generated_bdf(path, records=2, replacements={"Status": words})
            reader = BDFReader(path)
            check = mock.Mock()
            with mock.patch.object(reader, "iter_status_events", side_effect=AssertionError("not independent")), \
                    mock.patch.object(reader, "read_window", side_effect=AssertionError("no physiology")), \
                    mock.patch.object(reader, "_read_channel", side_effect=AssertionError("independent offsets")):
                self.assertEqual(reference_status_events(reader, participant="sub-01", check=check),
                                 [(0, 11), (1022, 31), (1030, 44), (2044, 45)])
            self.assertEqual(check.call_count, 3)
            with self.assertRaisesRegex(InnerSpeechRefusal, "reference_participant"):
                reference_status_events(reader, participant="sub-11")

    def test_sub10_short_pulse_exception_is_session1_only_and_defaults_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.bdf"
            words = {i: code for start, stop, code in ((4, 5, 31), (10, 12, 44), (20, 24, 45))
                     for i in range(start, stop)}
            generated_bdf(path, records=1, replacements={"Status": words})
            reader = BDFReader(path)
            self.assertEqual(reference_status_events(reader, participant="sub-10"), [(20, 45)])
            self.assertEqual(reference_status_events(reader, participant="sub-10", session="ses-01"), [(20, 45)])
            expected = [(4, 31), (10, 44), (20, 45)]
            self.assertEqual(reference_status_events(reader, participant="sub-10", session="ses-02"), expected)
            if importlib.util.find_spec("numpy"):
                self.assertEqual(reader.iter_status_events(participant="sub-10", session="ses-02"), expected)
            for participant in ("sub-01", "sub-03"):
                self.assertEqual(reference_status_events(reader, participant=participant), expected)
                self.assertEqual(reference_status_events(reader, participant=participant, session="ses-02"), expected)
            with mock.patch.object(reader, "_open", side_effect=AssertionError("must refuse before reading")):
                with self.assertRaisesRegex(InnerSpeechRefusal, "reference_session"):
                    reference_status_events(reader, participant="sub-10", session="ses-03")

    @unittest.skipUnless(importlib.util.find_spec("mne") and importlib.util.find_spec("numpy"),
                         "Optional MNE/NumPy comparison")
    def test_optional_mne_generated_rawarray_matches_source_semantics(self):
        import mne
        import numpy as np
        cases = [[0]*8, [31]*8, [31]+[0]*7, [0]*7+[31],
            [0]*4+[31]+[44]*4+[0]*4, [0]*4+[31]*2+[44]*4+[0]*4,
            [0]*4+[31]+[44]+[45]*4+[0]*4,
            [0]*4+[OVERFLOW_ONLY]*4+[OVERFLOW_ONLY+31]*4+[31]*4+[0]*4]
        generator = random.Random(20261002)
        for _ in range(32):
            cases.append([value for _ in range(12) for value in
                [generator.choice((0, 31, 44, 45, OVERFLOW_ONLY, OVERFLOW_ONLY+31))] *
                generator.randint(1, 5)])
        for values in cases:
            for short in (False, True):
                with self.subTest(values=values, short=short):
                    raw = mne.io.RawArray(np.asarray(values, dtype=np.int64)[None, :] & STATUS_MASK,
                        mne.create_info(["Status"], 1024, ["stim"]), verbose="ERROR")
                    try:
                        expected = mne.find_events(raw, initial_event=True, consecutive=True,
                            min_duration=.002 if short else 0, verbose="ERROR")
                    except ValueError:
                        with self.assertRaises(InnerSpeechRefusal):
                            reference_generated(values, short_filter=short)
                    else:
                        expected = [(int(s), int(c)) for s, _, c in expected if c != OVERFLOW_ONLY]
                        self.assertEqual(reference_generated(values, short_filter=short), expected)


if __name__ == "__main__":
    unittest.main()
