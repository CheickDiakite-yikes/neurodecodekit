import importlib.util
import unittest

from neurodecodekit.preprocess.sequence_alignment import KeySequence, TargetSequence


class SentenceRecordTests(unittest.TestCase):
    def test_channel_descriptions_preserve_geometry_and_type(self):
        from neurodecodekit.preprocess.sentence_extraction import describe_raw_channels

        class FakeRaw:
            ch_names = ["MEG0011", "MEG0012"]
            info = {
                "chs": [
                    {
                        "loc": [0.1, -0.2, 0.3],
                        "coord_frame": 1,
                        "coil_type": 3024,
                        "unit": 112,
                    },
                    {
                        "loc": [float("nan"), 0.0, 0.0],
                        "coord_frame": 1,
                        "coil_type": 3012,
                        "unit": 201,
                    },
                ]
            }

            @staticmethod
            def get_channel_types():
                return ["mag", "grad"]

        rows = describe_raw_channels(FakeRaw())

        self.assertEqual(rows[0]["name"], "MEG0011")
        self.assertEqual(rows[0]["type"], "mag")
        self.assertEqual(rows[0]["position_m"], [0.1, -0.2, 0.3])
        self.assertEqual(rows[0]["coord_frame"], 1)
        self.assertIsNone(rows[1]["position_m"])

    def test_trial_aligned_target_source_preserves_duplicate_rows(self):
        from neurodecodekit.preprocess.sequence_alignment import (
            extract_target_sequences_from_payload,
        )

        targets, _warnings = extract_target_sequences_from_payload(
            {"pr_trials": {"sequence": ["SAME TEXT", "SAME TEXT"]}}
        )

        self.assertEqual([target.index for target in targets], [0, 1])
        self.assertEqual([target.text for target in targets], ["SAME TEXT", "SAME TEXT"])

    def test_records_use_strict_trial_index_and_context(self):
        from neurodecodekit.preprocess.sentence_extraction import build_sentence_records

        keys = [
            KeySequence(0, "AB", "AB", 0, 2, 1.0, 2.0, 3, "ENTER"),
            KeySequence(1, "BA", "BA", 3, 5, 4.0, 5.0, 3, "ENTER"),
        ]
        targets = [
            TargetSequence(0, "PROMPT AB", "PROMPT AB", "mat.pr_trials.sequence"),
            TargetSequence(1, "PROMPT BA", "PROMPT BA", "mat.pr_trials.sequence"),
        ]
        responses = [
            TargetSequence(0, "AB", "AB", "mat.pr_trials.key"),
            TargetSequence(1, "BA", "BA", "mat.pr_trials.key"),
        ]

        records = build_sentence_records(
            keys,
            targets,
            responses,
            pre_context_sec=0.4,
            post_context_sec=0.5,
            raw_duration_sec=10.0,
        )

        self.assertEqual(records[0].start_sec, 0.6)
        self.assertEqual(records[0].end_sec, 2.5)
        self.assertEqual(records[1].reference_text, "PROMPT BA")

    def test_records_preserve_gapped_mat_trial_indices(self):
        from neurodecodekit.preprocess.sentence_extraction import build_sentence_records

        keys = [
            KeySequence(0, "AA", "AA", 0, 2, 1.0, 2.0, 3, "ENTER"),
            KeySequence(1, "CC", "CC", 3, 5, 3.0, 4.0, 3, "ENTER"),
        ]
        targets = [
            TargetSequence(
                index,
                f"PROMPT {index}",
                f"PROMPT {index}",
                "mat.pr_trials.sequence",
            )
            for index in range(3)
        ]
        responses = [
            TargetSequence(0, "AA", "AA", "mat.pr_trials.key"),
            TargetSequence(2, "CC", "CC", "mat.pr_trials.key"),
        ]

        records = build_sentence_records(
            keys,
            targets,
            responses,
            pre_context_sec=0.0,
            post_context_sec=0.0,
            raw_duration_sec=10.0,
            trial_index_map=[0, 2],
        )

        self.assertEqual([record.trial_index for record in records], [0, 2])
        self.assertEqual(records[1].reference_text, "PROMPT 2")
        self.assertEqual(records[1].mat_response_text, "CC")


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SentenceArrayTests(unittest.TestCase):
    def test_extracts_variable_segments_and_zero_pads(self):
        import numpy as np

        from neurodecodekit.preprocess.sentence_extraction import (
            SentenceRecord,
            extract_padded_sentence_arrays,
        )

        signal = np.arange(40, dtype="float32").reshape(2, 20)
        records = [
            SentenceRecord(0, "AB", "AB", "AB", 0.2, 0.8),
            SentenceRecord(1, "AA", "AA", "AA", 1.0, 1.4),
        ]
        arrays = extract_padded_sentence_arrays(signal, sfreq=10.0, records=records)

        self.assertEqual(arrays["signals"].shape, (2, 2, 6))
        self.assertEqual(arrays["input_lengths"].tolist(), [6, 4])
        self.assertTrue((arrays["signals"][1, :, 4:] == 0).all())
        self.assertEqual(arrays["target_lengths"].tolist(), [2, 2])

    def test_robust_scaling_clamps_and_reports_flat_channels(self):
        import numpy as np

        from neurodecodekit.preprocess.sentence_extraction import robust_scale_channels

        signal = np.array([[0, 1, 2, 100], [3, 3, 3, 3]], dtype="float32")
        scaled, zero_iqr = robust_scale_channels(signal, clamp=2.0)

        self.assertLessEqual(float(abs(scaled).max()), 2.0)
        self.assertEqual(zero_iqr, 1)

    def test_train_fit_scaler_ignores_eval_rows_and_preserves_padding(self):
        import numpy as np

        from neurodecodekit.preprocess.sentence_extraction import (
            apply_robust_scaler_to_padded,
            fit_robust_scaler_from_padded,
        )

        signals = np.zeros((3, 2, 5), dtype="float32")
        signals[0, :, :4] = [[0, 1, 2, 3], [10, 10, 10, 10]]
        signals[1, :, :3] = [[4, 5, 6], [10, 11, 12]]
        signals[2, :, :2] = [[1000, 2000], [-1000, -2000]]
        lengths = np.asarray([4, 3, 2], dtype="int32")

        center, scale, stats = fit_robust_scaler_from_padded(
            signals,
            lengths,
            fit_indices=[0, 1],
        )
        changed_eval = signals.copy()
        changed_eval[2, :, :2] *= -100
        changed_center, changed_scale, _ = fit_robust_scaler_from_padded(
            changed_eval,
            lengths,
            fit_indices=[0, 1],
        )
        scaled = apply_robust_scaler_to_padded(
            signals,
            lengths,
            center=center,
            scale=scale,
            clamp=5.0,
        )

        np.testing.assert_array_equal(center, changed_center)
        np.testing.assert_array_equal(scale, changed_scale)
        self.assertEqual(stats["n_fit_rows"], 2)
        self.assertEqual(stats["n_fit_valid_timepoints"], 7)
        self.assertLessEqual(float(abs(scaled).max()), 5.0)
        for row_index, length in enumerate(lengths.tolist()):
            self.assertTrue((scaled[row_index, :, length:] == 0).all())


if __name__ == "__main__":
    unittest.main()
