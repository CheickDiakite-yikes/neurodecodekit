import importlib.util
import unittest

from neurodecodekit.models.tiny_conv_baseline import encode_labels


class TinyConvBaselineHelperTests(unittest.TestCase):
    def test_encode_labels_reports_eval_labels_missing_from_train(self):
        vocab, train_encoded, eval_encoded, missing = encode_labels(
            ["B", "A", "B"],
            ["A", "C", "B"],
        )

        self.assertEqual(vocab, ["A", "B"])
        self.assertEqual(train_encoded, [1, 0, 1])
        self.assertEqual(eval_encoded, [0, 0, 1])
        self.assertEqual(missing, ["C"])

    def test_training_param_validation_runs_before_optional_imports(self):
        from neurodecodekit.models.tiny_conv_baseline import run_tiny_conv_baseline

        with self.assertRaisesRegex(ValueError, "epochs"):
            run_tiny_conv_baseline(
                train_windows=[],
                train_labels=[],
                eval_windows=[],
                eval_labels=[],
                epochs=0,
            )


@unittest.skipIf(importlib.util.find_spec("torch"), "Torch installed; missing-dependency path not active")
class TinyConvMissingDependencyTests(unittest.TestCase):
    def test_missing_torch_error_points_to_ml_extra(self):
        import numpy as np

        from neurodecodekit.models.tiny_conv_baseline import run_tiny_conv_baseline

        with self.assertRaisesRegex(RuntimeError, r"pip install -e '.\[ml\]'"):
            run_tiny_conv_baseline(
                train_windows=np.zeros((2, 2, 3), dtype="float32"),
                train_labels=["A", "B"],
                eval_windows=np.zeros((1, 2, 3), dtype="float32"),
                eval_labels=["A"],
            )


@unittest.skipUnless(importlib.util.find_spec("torch"), "Torch not installed")
@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TinyConvTrainingSmokeTests(unittest.TestCase):
    def test_tiny_conv_learns_separable_synthetic_windows(self):
        from neurodecodekit.models.tiny_conv_baseline import run_tiny_conv_baseline_from_single_cache
        from neurodecodekit.training.synthetic import make_synthetic_windows

        windows, labels, _metadata = make_synthetic_windows(
            samples=96,
            channels=4,
            times=12,
            classes=2,
            seed=11,
        )

        result = run_tiny_conv_baseline_from_single_cache(
            windows=windows,
            labels=labels,
            train_fraction=0.75,
            seed=11,
            epochs=30,
            batch_size=16,
            learning_rate=0.02,
            hidden_channels=8,
            num_threads=1,
        )

        self.assertEqual(result.strategy, "tiny-conv")
        self.assertEqual(result.model_name, "TinyConvNet")
        self.assertEqual(result.split_mode, "single-cache-stratified-holdout")
        self.assertEqual(len(result.predictions), result.n_eval_rows)
        self.assertGreaterEqual(result.eval_accuracy, 0.5)
        self.assertIn("tiny_conv_baseline_uses_neural_windows", result.warnings)
        self.assertTrue(result.metadata()["uses_deep_learning"])


if __name__ == "__main__":
    unittest.main()
