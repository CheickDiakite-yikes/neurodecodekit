"""Immediate numerical checks for the real SPEECH-REPRO-1 reference, not evidence."""

import importlib.util
import inspect
import subprocess
import sys
import unittest

from neurodecodekit.models import speech_reference as reference


class ImportContractTests(unittest.TestCase):
    def test_import_has_no_heavy_dependency_side_effect(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys; from neurodecodekit.models import speech_reference; "
             "assert not {'numpy','torch','sklearn','mne'} & set(sys.modules)"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_online_target_and_reduced_schedule_not_in_api(self):
        parameters = inspect.signature(reference.train_predict).parameters
        self.assertEqual(list(parameters), ["cal_windows", "cal_labels", "online_windows",
                                           "deadline", "progress", "checkpoint_dir"])
        self.assertEqual((reference.N_FOLDS, reference.N_EPOCHS, reference.SEED),
                         (10, 100, 20260906))


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
class NumericTests(unittest.TestCase):
    def test_center_average_and_training_jitter_boundaries(self):
        import numpy as np

        samples = np.broadcast_to(np.arange(1626, dtype=np.float32), (2, 128, 1626))
        actual = reference.average_repetitions(samples)
        np.testing.assert_array_equal(actual[0, 0], np.arange(320) + 665)

        class Fixed:
            def randint(self, low, high, size):
                self.bounds = (low, high, size)
                return np.array([-25, 24, -25, 24])

        rng = Fixed()
        jittered = reference.average_repetitions(samples, rng=rng)
        self.assertEqual(rng.bounds, (-25, 25, 4))
        np.testing.assert_allclose(jittered, actual - 0.4, atol=1e-4)
        np.testing.assert_array_equal(reference.average_repetitions(samples), actual)

    def test_no_jitter_on_already_averaged_or_nonfinite_input(self):
        import numpy as np

        averaged = np.zeros((2, 128, 320), dtype=np.float32)
        with self.assertRaises(ValueError):
            reference.average_repetitions(averaged, rng=np.random.RandomState(0))
        with self.assertRaises(ValueError):
            reference.average_repetitions(np.full((2, 128, 1626), np.nan))

    def test_ensemble_is_per_trial_class_zscore_without_cross_trial_fitting(self):
        import numpy as np

        logits = np.random.RandomState(3).normal(size=(4, 2, 5))
        actual = reference.zscore_mean_probabilities(logits)
        z = ((logits - logits.mean(-1, keepdims=True)) / logits.std(-1, keepdims=True)).mean(0)
        np.testing.assert_array_equal(actual.argmax(-1), z.argmax(-1))
        np.testing.assert_allclose(actual.sum(-1), 1)
        logits[:, 1] *= -100
        changed = reference.zscore_mean_probabilities(logits)
        np.testing.assert_array_equal(changed[0], actual[0])
        with self.assertRaises(ValueError):
            reference.zscore_mean_probabilities(np.zeros((4, 2, 5)))

    @unittest.skipUnless(importlib.util.find_spec("sklearn"), "optional sklearn")
    def test_ten_stratified_original_trial_folds(self):
        import numpy as np

        labels, folds = reference.calibration_folds(np.tile(np.arange(5), 20))
        observed = []
        for train, validation in folds:
            self.assertFalse(set(train) & set(validation))
            np.testing.assert_array_equal(np.bincount(labels[validation]), [2] * 5)
            observed.extend(validation.tolist())
        self.assertEqual(sorted(observed), list(range(100)))
        with self.assertRaises(ValueError):
            reference.calibration_folds(np.tile(np.arange(5), 9))


@unittest.skipUnless(importlib.util.find_spec("torch"), "optional Torch")
class NetworkTests(unittest.TestCase):
    def test_channels_last_matches_source_contiguous_evaluation(self):
        import copy
        import torch

        torch.set_num_threads(1)
        torch.manual_seed(7)
        model = reference.build_reference_eegnet().eval()
        contiguous = copy.deepcopy(model).to(memory_format=torch.contiguous_format)
        inputs = torch.randn(3, 1, 128, 320)
        with torch.inference_mode():
            actual = model(inputs.contiguous(memory_format=torch.channels_last))
            expected = contiguous(inputs)
        torch.testing.assert_close(actual, expected, atol=1e-6, rtol=1e-5)

    def test_exact_parameter_count_shape_and_source_initial_state(self):
        import torch

        torch.set_num_threads(1)
        model = reference.build_reference_eegnet()
        self.assertEqual(sum(p.numel() for p in model.parameters()), 12293)
        self.assertEqual(model.n_dim, 1280)
        self.assertEqual(model.conv1[1].num_batches_tracked.item(), 1)
        model.eval()
        with torch.inference_mode():
            result = model(torch.zeros(2, 1, 128, 320))
        self.assertEqual(tuple(result.shape), (2, 5))

    def test_one_training_step_and_validation_checkpoint(self):
        import numpy as np
        import torch

        torch.set_num_threads(1)
        windows = np.random.RandomState(4).normal(size=(10, 128, 1626)).astype(np.float32)
        labels = np.tile(np.arange(5), 2)
        state, record = reference._fit_fold(
            windows, labels, reference.average_repetitions(windows),
            np.arange(5), np.arange(5, 10), fold=0, deadline=None, progress=None, epochs=1,
        )
        self.assertEqual(record["best_epoch"], 1)
        self.assertTrue(np.isfinite(record["best_validation_loss"]))
        model = reference.build_reference_eegnet()
        model.load_state_dict(state, strict=True)
        self.assertEqual(len(record["state_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
