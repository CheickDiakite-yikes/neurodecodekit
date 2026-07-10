import unittest

from neurodecodekit.preprocess.brainvision_extraction import (
    MatTriggerEvent,
    RawTriggerEvent,
    align_trigger_sequences,
    label_for_keycode,
)


class BrainVisionExtractionTests(unittest.TestCase):
    def test_aligns_mat_as_exact_raw_subsequence_and_audits_clock(self):
        raw = [
            RawTriggerEvent(0, 0.5, 20),
            RawTriggerEvent(1, 1.0, 10),
            RawTriggerEvent(2, 1.5, 65),
            RawTriggerEvent(3, 1.7, 30),
            RawTriggerEvent(4, 2.0, 13),
        ]
        mat = [
            MatTriggerEvent(0, 101.0, 10, "rsvp", 0, None),
            MatTriggerEvent(1, 101.5, 65, "key", 0, "A"),
            MatTriggerEvent(2, 102.0, 13, "key", 0, "ENTER"),
        ]

        aligned = align_trigger_sequences(raw, mat, max_abs_residual_sec=0.001)

        self.assertEqual([(m.raw_index, m.mat_index) for m in aligned.matches], [(1, 0), (2, 1), (4, 2)])
        self.assertEqual(aligned.unmatched_raw_indices, (0, 3))
        self.assertAlmostEqual(aligned.clock_offset_sec, -100.0)
        self.assertAlmostEqual(aligned.max_abs_residual_sec, 0.0)

    def test_alignment_fails_when_trigger_or_timing_contract_breaks(self):
        raw = [RawTriggerEvent(0, 1.0, 65)]
        mat_missing = [MatTriggerEvent(0, 101.0, 66, "key", 0, "B")]
        with self.assertRaisesRegex(ValueError, "cannot cover MAT trigger"):
            align_trigger_sequences(raw, mat_missing)

        mat_drift = [MatTriggerEvent(0, 100.0, 65, "key", 0, "A")]
        raw_drift = [
            RawTriggerEvent(0, 1.0, 65),
            RawTriggerEvent(1, 2.0, 66),
        ]
        mat_drift.append(MatTriggerEvent(1, 100.5, 66, "key", 0, "B"))
        with self.assertRaisesRegex(ValueError, "timing residual"):
            align_trigger_sequences(raw_drift, mat_drift, max_abs_residual_sec=0.1)

    def test_keycode_labels_match_existing_cache_contract(self):
        self.assertEqual(label_for_keycode(65), "A")
        self.assertEqual(label_for_keycode(122), "Z")
        self.assertEqual(label_for_keycode(32), "SPACE")
        self.assertEqual(label_for_keycode(13), "ENTER")
        self.assertIsNone(label_for_keycode(8))


if __name__ == "__main__":
    unittest.main()
