import importlib.util
import unittest

from neurodecodekit.models.template_classifier import TemplateClassifier


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class TemplateBaselineTests(unittest.TestCase):
    def test_single_cache_holdout_learns_separable_windows(self):
        import numpy as np

        from neurodecodekit.models.template_baseline import run_template_baseline_from_single_cache

        windows, labels = _separable_windows()

        result = run_template_baseline_from_single_cache(
            windows=windows,
            labels=labels,
            train_fraction=0.5,
            seed=3,
        )

        self.assertEqual(result.strategy, "nearest-centroid")
        self.assertEqual(result.split_mode, "single-cache-stratified-holdout")
        self.assertEqual(result.n_train_rows, 4)
        self.assertEqual(result.n_eval_rows, 4)
        self.assertEqual(result.n_classes, 2)
        self.assertEqual(result.predictions, result.targets)
        self.assertEqual(result.feature_shape, (2, 3))
        self.assertTrue(np.array_equal(windows.shape, np.array([8, 2, 3])))
        self.assertIn("template_baseline_uses_neural_windows", result.warnings)
        self.assertIn("template_single_cache_holdout_split", result.warnings)
        self.assertTrue(result.metadata()["uses_neural_windows"])
        self.assertTrue(result.metadata()["no_deep_learning"])

    def test_separate_cache_warns_when_eval_label_missing_from_train(self):
        import numpy as np

        from neurodecodekit.models.template_baseline import run_template_baseline

        train_windows = np.zeros((2, 2, 3), dtype="float32")
        eval_windows = np.zeros((2, 2, 3), dtype="float32")

        result = run_template_baseline(
            train_windows=train_windows,
            train_labels=["A", "A"],
            eval_windows=eval_windows,
            eval_labels=["A", "B"],
        )

        self.assertEqual(result.missing_eval_labels_in_train, ["B"])
        self.assertIn("template_eval_labels_missing_from_train", result.warnings)
        self.assertEqual(result.n_eval_rows, 2)

    def test_holdout_rejects_invalid_fraction_and_tiny_eval(self):
        import numpy as np

        from neurodecodekit.models.template_baseline import stratified_holdout_indices

        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            stratified_holdout_indices(["A", "A"], train_fraction=1.0)

        with self.assertRaisesRegex(ValueError, "no eval rows"):
            stratified_holdout_indices(["A"], train_fraction=0.5)

        classifier = TemplateClassifier()
        with self.assertRaisesRegex(RuntimeError, "fitted"):
            classifier.predict(np.zeros((1, 2, 3), dtype="float32"))

    def test_template_classifier_rejects_shape_mismatch(self):
        import numpy as np

        classifier = TemplateClassifier().fit(
            np.zeros((2, 2, 3), dtype="float32"),
            np.array(["A", "B"]),
        )

        with self.assertRaisesRegex(ValueError, "match template"):
            classifier.predict(np.zeros((1, 2, 4), dtype="float32"))


def _separable_windows():
    import numpy as np

    labels = np.array(["A", "A", "A", "A", "B", "B", "B", "B"])
    windows = np.zeros((8, 2, 3), dtype="float32")
    windows[:4, 0, :] = 1.0
    windows[4:, 1, :] = 1.0
    return windows, labels


if __name__ == "__main__":
    unittest.main()
