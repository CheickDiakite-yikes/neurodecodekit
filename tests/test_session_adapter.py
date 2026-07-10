import importlib.util
import unittest

from neurodecodekit.preprocess.session_adapter import (
    apply_robust_channel_affine,
    apply_synthetic_channel_mixing_shift,
    apply_synthetic_channel_shift,
    apply_synthetic_time_varying_shift,
    fit_robust_channel_affine,
    make_synthetic_channel_mixing_shift,
    make_synthetic_channel_shift,
    make_synthetic_time_varying_shift,
    padding_is_zero,
    summarize_signal_reconstruction,
)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SessionAdapterTests(unittest.TestCase):
    def test_robust_affine_recovers_known_shift_without_touching_padding(self):
        import numpy as np

        rng = np.random.default_rng(7)
        signals = np.zeros((4, 3, 8), dtype="float32")
        lengths = np.asarray([8, 6, 5, 7], dtype="int32")
        for row, length in enumerate(lengths.tolist()):
            signals[row, :, :length] = rng.normal(size=(3, length))
        shift = make_synthetic_channel_shift(3, seed=11)
        shifted = apply_synthetic_channel_shift(signals, lengths, shift)
        state = fit_robust_channel_affine(
            source_signals=signals,
            source_input_lengths=lengths,
            target_calibration_signals=shifted,
            target_input_lengths=lengths,
        )
        adapted = apply_robust_channel_affine(shifted, lengths, state)
        error = summarize_signal_reconstruction(signals, adapted, lengths)

        self.assertLess(error["mae"], 1e-5)
        self.assertTrue(padding_is_zero(shifted, lengths))
        self.assertTrue(padding_is_zero(adapted, lengths))
        self.assertFalse(state.to_dict()["target_labels_used"])
        self.assertEqual(state.to_dict()["learned_parameter_count"], 0)

    def test_shift_is_deterministic_and_rejects_channel_mismatch(self):
        import numpy as np

        first = make_synthetic_channel_shift(3, seed=19)
        second = make_synthetic_channel_shift(3, seed=19)
        self.assertEqual(first, second)

        with self.assertRaisesRegex(ValueError, "channel count"):
            apply_synthetic_channel_shift(
                np.zeros((2, 2, 3), dtype="float32"),
                np.asarray([3, 3]),
                first,
            )

    def test_fit_rejects_invalid_lengths(self):
        import numpy as np

        signals = np.zeros((2, 2, 3), dtype="float32")
        with self.assertRaisesRegex(ValueError, "input_lengths"):
            fit_robust_channel_affine(
                source_signals=signals,
                source_input_lengths=np.asarray([3, 4]),
                target_calibration_signals=signals,
                target_input_lengths=np.asarray([3, 3]),
            )

    def test_non_diagonal_and_time_varying_shifts_are_deterministic_and_padded(self):
        import numpy as np

        rng = np.random.default_rng(29)
        signals = np.zeros((3, 4, 9), dtype="float32")
        lengths = np.asarray([9, 6, 7], dtype="int32")
        for row, length in enumerate(lengths.tolist()):
            signals[row, :, :length] = rng.normal(size=(4, length))

        mixing = make_synthetic_channel_mixing_shift(4, seed=41)
        time_varying = make_synthetic_time_varying_shift(4, seed=43)
        mixed_first = apply_synthetic_channel_mixing_shift(signals, lengths, mixing)
        mixed_second = apply_synthetic_channel_mixing_shift(signals, lengths, mixing)
        drifted_first = apply_synthetic_time_varying_shift(
            signals,
            lengths,
            time_varying,
        )
        drifted_second = apply_synthetic_time_varying_shift(
            signals,
            lengths,
            time_varying,
        )

        np.testing.assert_array_equal(mixed_first, mixed_second)
        np.testing.assert_array_equal(drifted_first, drifted_second)
        self.assertTrue(padding_is_zero(mixed_first, lengths))
        self.assertTrue(padding_is_zero(drifted_first, lengths))
        self.assertGreater(mixing.condition_number, 1.0)
        self.assertEqual(mixing.to_dict()["kind"], "synthetic_stationary_channel_mixing")
        self.assertEqual(
            time_varying.to_dict()["kind"],
            "synthetic_within_row_time_varying_diagonal",
        )


if __name__ == "__main__":
    unittest.main()
