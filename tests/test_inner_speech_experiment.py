"""Generated signals/labels only; no participant source or frozen outcomes."""

import importlib.util
import json
import subprocess
import sys
import unittest
from unittest import mock

from neurodecodekit.experiments import inner_speech as inner


class OptionalDependencyTests(unittest.TestCase):
    def test_import_keeps_numerical_dependencies_optional(self):
        result = subprocess.run([sys.executable, "-c",
            "import sys; from neurodecodekit.experiments import inner_speech; "
            "assert not {'numpy','scipy','sklearn','mne','torch'} & set(sys.modules)"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
class InnerSpeechExperimentTests(unittest.TestCase):
    def _features(self, n=40):
        import numpy as np
        labels = np.arange(n) % 4
        signal = np.tile(np.eye(4)[labels], (1, 160))
        return {"P": np.zeros((n, 85)), "E_action": signal,
                "E_cue": signal.copy(), "E_late": signal.copy()}, labels, np.arange(n)

    def test_fixed_windows_four_class_bands_and_modality_independence(self):
        import numpy as np
        rng = np.random.default_rng(4)
        for length in (384, 2048):
            eeg, exg = rng.normal(size=(128, length)), rng.normal(size=(8, length))
            result = inner.window_features(eeg, exg)
            self.assertEqual(result["E"].shape, (640,))
            self.assertEqual(result["P"].shape, (77,))
            np.testing.assert_array_equal(result["E"], inner.window_features(eeg, exg * 50)["E"])
            np.testing.assert_array_equal(result["P"], inner.window_features(eeg * 50, exg)["P"])
            rereferenced = exg - exg[:2].mean(axis=0, keepdims=True)
            rereferenced = np.concatenate((rereferenced, rereferenced[2:8:2] - rereferenced[3:8:2]))
            np.testing.assert_allclose(result["P"].reshape(11, 7)[:, -1], np.log(rereferenced.var(axis=1)))
            np.testing.assert_allclose(result["P"].reshape(11, 7)[0], result["P"].reshape(11, 7)[1])
            common = rng.normal(size=(1, length))
            np.testing.assert_allclose(result["E"], inner.window_features(eeg + common, exg)["E"], atol=1e-12)
        time = np.arange(2048) / 1024
        for label, frequency in enumerate((2, 6, 10, 20)):
            eeg = np.zeros((128, 2048))
            eeg[0] = 10 * np.sin(2 * np.pi * frequency * time)
            eeg[1] = -eeg[0]
            features = inner.window_features(eeg, np.zeros((8, 2048)))
            self.assertEqual(features["E"].reshape(128, 5)[0].argmax(), label)
        for length in (383, 512, 1024, 2049):
            with self.assertRaises(ValueError):
                inner.window_features(np.zeros((128, length)), np.zeros((8, length)))

    def test_original_index_embargo_and_nested_coverage_are_label_independent(self):
        import numpy as np
        for n in (40, 80, 120):
            labels, original = np.arange(n) % 4, np.arange(n)
            _, plans, records = inner._nested_plan(labels, original, inner.SEED)
            outer_coverage = np.zeros(n, dtype=int)
            for train, validation, nested, _ in plans:
                self.assertTrue(np.all(np.abs(original[train, None] - original[validation]) > 1))
                outer_coverage[validation] += 1
                inner_coverage = np.zeros(n, dtype=int)
                for inner_train, inner_validation in nested:
                    self.assertTrue(np.isin(inner_train, train).all())
                    self.assertTrue(np.isin(inner_validation, train).all())
                    self.assertTrue(np.all(np.abs(original[inner_train, None] - original[inner_validation]) > 1))
                    inner_coverage[inner_validation] += 1
                np.testing.assert_array_equal(inner_coverage[train], np.ones(len(train)))
                self.assertEqual(inner_coverage[validation].sum(), 0)
            np.testing.assert_array_equal(outer_coverage, np.ones(n))
            permuted = inner._nested_plan((labels + 1) % 4, original, inner.SEED)[2]
            self.assertEqual([r["original_split_sha256"] for r in records],
                             [r["original_split_sha256"] for r in permuted])
        spaced = np.arange(40) * 3
        _, plans, _ = inner._nested_plan(np.arange(40) % 4, spaced, inner.SEED)
        self.assertIn(10, plans[0][0])  # compressed neighbour is not an original-index neighbour

    def test_block_scaling_fold_local_derangement_and_fixed_null_labels(self):
        import numpy as np
        rng = np.random.default_rng(8)
        features = {name: rng.normal(size=(40, width)) for name, width in
                    (("P", 80), ("E_action", 640), ("E_cue", 640), ("E_late", 640))}
        labels = np.arange(40) % 4
        null = np.roll(labels, 1)
        train, test = np.arange(20), np.arange(21, 40)
        expected = {name: inner._standardized_block(values[train], values[test])
                    for name, values in features.items()}
        count = 0

        def inspect(fit, fit_labels, evaluation):
            nonlocal count
            arm = inner.LEARNED_ARMS[count]
            count += 1
            np.testing.assert_array_equal(fit_labels, null[train] if arm == "joint_shuffled" else labels[train])
            np.testing.assert_array_equal(fit[:, :80], expected["P"][0])
            np.testing.assert_array_equal(evaluation[:, :80], expected["P"][1])
            if arm != "P":
                name = {"cue_joint": "E_cue", "late_joint": "E_late"}.get(arm, "E_action")
                eeg_train, eeg_test = expected[name]
                if arm == "deranged_joint":
                    eeg_train, eeg_test = np.roll(eeg_train, 1, axis=0), np.roll(eeg_test, 1, axis=0)
                np.testing.assert_array_equal(fit[:, 80:], eeg_train)
                np.testing.assert_array_equal(evaluation[:, 80:], eeg_test)
            return np.full((len(test), 4), .25)

        with mock.patch.object(inner, "_ridge_probabilities", new=inspect):
            inner._predict_arms(features, labels, null, train, test, None)
        self.assertEqual(count, 6)
        altered = features["P"].copy()
        altered[test] *= 100000
        np.testing.assert_array_equal(inner._standardized_block(altered[train], altered[test])[0], expected["P"][0])

    def test_temperature_math_argmax_and_missing_training_classes(self):
        import numpy as np
        labels = np.arange(40) % 4
        predicted = labels.copy()
        predicted[:10] = (predicted[:10] + 1) % 4
        probabilities = np.full((40, 4), 1 / 30)
        probabilities[np.arange(40), predicted] = .9
        fit = inner.fit_inverse_temperature(probabilities, labels)
        self.assertAlmostEqual(fit["inverse_temperature"], 2 / 3, places=12)
        self.assertEqual(fit["bisection_steps"], 60)
        calibrated = inner.temperature_probabilities(probabilities, fit["inverse_temperature"])
        np.testing.assert_array_equal(calibrated.argmax(axis=1), probabilities.argmax(axis=1))
        self.assertLessEqual(fit["class_macro_nll_after"], fit["class_macro_nll_before"])
        train = np.arange(12, dtype=float).reshape(6, 2)
        missing = inner._ridge_probabilities(train, np.zeros(6, dtype=int), train[:2])
        self.assertEqual(missing.shape, (2, 4))
        np.testing.assert_allclose(missing.sum(axis=1), 1)
        fit_missing = inner.fit_inverse_temperature(missing, np.zeros(2, dtype=int))
        self.assertEqual(fit_missing["observed_calibration_classes"], 1)
        self.assertEqual(fit_missing["calibration_class_counts"], [2, 0, 0, 0])
        # Whole-condition class presence remains required; splits are never repaired.
        with self.assertRaises(ValueError):
            inner.preflight_condition(np.arange(40) % 3, np.arange(40))
        sparse_labels = np.concatenate((np.arange(3), np.full(37, 3)))
        metadata = inner.preflight_condition(sparse_labels, np.arange(40))
        self.assertIn(0, metadata["folds"][0]["training_class_counts"])

    def test_generated_signal_prediction_is_separate_from_scoring_and_preserves_null_calibration(self):
        import numpy as np
        features, labels, original = self._features()
        plans = inner._nested_plan(labels, original, inner.SEED)[1]
        calibrations = 0
        original_calibrate = inner.fit_inverse_temperature

        def calibrate(probabilities, calibration_labels):
            nonlocal calibrations
            fold, arm_index = divmod(calibrations, len(inner.LEARNED_ARMS))
            calibrations += 1
            train, _, _, null = plans[fold]
            expected = null[train] if inner.LEARNED_ARMS[arm_index] == "joint_shuffled" else labels[train]
            np.testing.assert_array_equal(calibration_labels, expected)
            return original_calibrate(probabilities, calibration_labels)

        with mock.patch.object(inner, "fit_inverse_temperature", new=calibrate), \
                mock.patch.object(inner, "_metrics", side_effect=AssertionError("No scoring during prediction")):
            result = inner.run_condition(features, labels, original)
        self.assertEqual(calibrations, 24)
        self.assertEqual(result["fit_diagnostics"]["ridge_fits"], 96)
        self.assertFalse(result["fit_diagnostics"]["outer_scores_computed"])
        self.assertGreaterEqual(result["fit_diagnostics"]["argmax_rounding_tie_corrections"], 2)
        self.assertEqual(set(result["predictions"]), set(inner.ARMS))
        for arm, values in result["predictions"].items():
            self.assertEqual(values.shape, (40, 4))
            np.testing.assert_allclose(values.sum(axis=1), 1)
            if arm in inner.LEARNED_ARMS:
                np.testing.assert_array_equal(values.argmax(axis=1), result["uncalibrated"][arm].argmax(axis=1))
        score = inner.score_condition(result, labels)
        self.assertGreater(score["metrics"]["joint"]["balanced_accuracy"], .95)
        self.assertEqual(set(score["primary_joint_nll_gains"]), set(inner.PRIMARY_COMPARATORS))
        json.dumps(score, allow_nan=False)
        json.dumps(result["fit_diagnostics"], allow_nan=False)
        first_train = plans[0][0]
        expected_prior = (np.bincount(labels[first_train], minlength=4) + 1) / (len(first_train) + 4)
        np.testing.assert_array_equal(result["predictions"]["training_prior"][0], expected_prior)
        changed = labels.copy()
        changed[:10] = (changed[:10] + 1) % 4
        held_out_changed = inner.run_condition(features, changed, original)
        for arm in inner.ARMS:
            np.testing.assert_array_equal(result["predictions"][arm][:10], held_out_changed["predictions"][arm][:10])

    def test_temperature_rounding_tie_regression_refuses_true_reversal_or_large_gap(self):
        import numpy as np
        probabilities = np.array([[.25780201632766936, .22659395101699173,
                                   .25780201632766947, .2578020163276694]])
        before = probabilities.copy()
        diagnostics = {}
        calibrated = inner.temperature_probabilities(probabilities, .05, diagnostics=diagnostics)
        self.assertEqual(calibrated.argmax(axis=1).tolist(), [2])
        self.assertEqual(diagnostics["argmax_rounding_tie_corrections"], 1)
        self.assertEqual(calibrated[0, 2], np.nextafter(calibrated[0, 0], np.inf))
        np.testing.assert_array_equal(probabilities, before)
        np.testing.assert_allclose(calibrated.sum(axis=1), 1, rtol=0, atol=4 * np.finfo(float).eps)
        flat_diagnostics = {}
        np.testing.assert_array_equal(inner.temperature_probabilities(np.full((1, 4), .25), .05,
            diagnostics=flat_diagnostics), np.full((1, 4), .25))
        self.assertEqual(flat_diagnostics["argmax_rounding_tie_corrections"], 0)
        with mock.patch.object(inner, "_temperature_log_softmax", return_value=np.log([[.7, .1, .1, .1]])), \
                self.assertRaisesRegex(ValueError, "strict numerical order reversal"):
            inner.temperature_probabilities(probabilities, .05)
        with mock.patch.object(inner, "_temperature_log_softmax", return_value=np.log([[.25] * 4])), \
                self.assertRaisesRegex(ValueError, "rounding-only"):
            inner.temperature_probabilities(np.array([[.1, .1, .1, .7]]), .05)

    def test_class_macro_nll_balanced_accuracy_and_confusion_arithmetic(self):
        import numpy as np
        labels = np.array([0, 0, 1, 2, 3])
        probabilities = np.full((5, 4), .1)
        probabilities[np.arange(5), labels] = .7
        metrics = inner._metrics(probabilities, labels)
        self.assertAlmostEqual(metrics["class_macro_nll"], -np.log(.7))
        self.assertEqual(metrics["balanced_accuracy"], 1)
        self.assertEqual(metrics["confusion_matrix_actual_by_predicted"], np.diag([2, 1, 1, 1]).tolist())
        uniform = inner._metrics(np.full((5, 4), .25), labels)
        self.assertAlmostEqual(uniform["class_macro_nll"], np.log(4))
        self.assertEqual(uniform["balanced_accuracy"], .25)


if __name__ == "__main__":
    unittest.main()
