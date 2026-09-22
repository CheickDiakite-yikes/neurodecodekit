"""Generated-only nested temperature calibration checks, with bounded memory."""

import importlib.util
import json
import unittest
import warnings
from unittest import mock

from neurodecodekit.experiments import speech_probability_calibration as calibration
from neurodecodekit.experiments import speech_repetition_power as previous


class ProbabilityCalibrationContractTests(unittest.TestCase):
    def test_fixed_roster_and_resource_counts(self):
        self.assertEqual(len(calibration.LEARNED_ARMS), 9)
        self.assertEqual(len(calibration.ARMS), 20)
        self.assertEqual(len(set(calibration.ARMS)), 20)
        self.assertEqual(calibration.BETA_BOUNDS, (0.05, 20.0))
        self.assertEqual(calibration.BISECTION_STEPS, 60)
        self.assertEqual(calibration.PRIMARY_ARM, "A_full_all_calibrated")
        self.assertEqual(calibration.PRIMARY_COMPARATORS, (
            "A_calibrated", "N_calibrated", "A_full_all_deranged_calibrated",
            "A_full_all_shuffled_calibrated", "uniform", "training_prior"))
        self.assertEqual(9 * 5 * 10 * 6, 2700)
        self.assertEqual(9 * 10 * 6, 540)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "Optional NumPy required")
class TemperatureTests(unittest.TestCase):
    def setUp(self):
        import numpy as np

        self.np = np

    def test_known_class_balanced_logits_have_inverse_temperature_two(self):
        np = self.np
        probabilities, labels = [], []
        for predicted_class in range(5):
            distribution = np.full(5, 0.05)
            distribution[predicted_class] = 0.8
            underconfident = np.sqrt(distribution)
            underconfident /= underconfident.sum()
            probabilities.extend([underconfident] * 20)
            labels.extend([predicted_class] * 16 + [label for label in range(5) if label != predicted_class])
        result = calibration.fit_inverse_temperature(np.asarray(probabilities), np.asarray(labels))
        self.assertAlmostEqual(result["inverse_temperature"], 2.0, places=10)
        self.assertEqual(result["boundary"], "interior")
        self.assertEqual(result["bisection_steps"], 60)
        self.assertAlmostEqual(result["class_macro_nll_after"],
                               float(-0.8 * np.log(0.8) - 0.2 * np.log(0.05)), places=12)
        self.assertLess(result["class_macro_nll_after"], result["class_macro_nll_before"])
        self.assertAlmostEqual(result["derivative_at_solution"], 0.0, places=12)
        json.dumps(result, allow_nan=False)

    def test_boundaries_flat_case_and_argmax_identity(self):
        np = self.np
        labels = np.tile(np.arange(5), 4)
        confident = np.full((20, 5), 0.1)
        confident[np.arange(20), labels] = 0.6
        upper = calibration.fit_inverse_temperature(confident, labels)
        lower = calibration.fit_inverse_temperature(confident, (labels + 1) % 5)
        flat = calibration.fit_inverse_temperature(np.full((20, 5), 0.2), labels)
        self.assertEqual((upper["inverse_temperature"], upper["boundary"]), (20.0, "upper"))
        self.assertEqual((lower["inverse_temperature"], lower["boundary"]), (0.05, "lower"))
        self.assertEqual((flat["inverse_temperature"], flat["boundary"]), (1.0, "flat"))
        self.assertFalse(flat["boundary_hit"])
        for beta in (0.05, 1.0, 2.0, 20.0):
            transformed = calibration.temperature_probabilities(confident, beta)
            np.testing.assert_array_equal(transformed.argmax(axis=1), confident.argmax(axis=1))
            np.testing.assert_allclose(transformed.sum(axis=1), 1, atol=1e-12)
        for beta in (0.0, -1.0, 21.0, float("nan")):
            with self.subTest(beta=beta), self.assertRaises(ValueError):
                calibration.temperature_probabilities(confident, beta)
        with self.assertRaisesRegex(ValueError, "all five classes"):
            calibration.fit_inverse_temperature(confident[:2], labels[:2])


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("sklearn"),
                     "Optional NumPy and sklearn required")
class NestedProbabilityCalibrationTests(unittest.TestCase):
    def setUp(self):
        import numpy as np

        self.np = np
        self.labels = np.tile(np.arange(5), 20)
        rng = np.random.default_rng(39)
        self.auxiliary = rng.normal(size=(100, 692))
        self.eeg = rng.normal(size=(100, 768))

    def test_nested_splits_cover_outer_training_only_and_use_original_index_embargo(self):
        from sklearn.model_selection import KFold

        np = self.np
        _, outer, inner, null_labels, metadata = calibration._nested_plan(self.labels)
        self.assertEqual(metadata, calibration.preflight_probability_calibration(self.labels))
        for scheme_index, (scheme, folds) in enumerate(outer.items()):
            outer_coverage = np.zeros(100, dtype=int)
            for fold, (outer_train, outer_validation) in enumerate(folds):
                outer_coverage[outer_validation] += 1
                coverage = np.zeros(100, dtype=int)
                expected_random = list(KFold(4, shuffle=True,
                    random_state=20260922 + 100 * scheme_index + fold).split(outer_train))
                original_blocks = [block for block in range(5) if block != fold]
                for inner_index, (train, validation) in enumerate(inner[scheme][fold]):
                    self.assertFalse(set(train) & set(validation))
                    self.assertFalse((set(train) | set(validation)) & set(outer_validation))
                    self.assertTrue(set(train).issubset(set(outer_train)))
                    self.assertTrue(set(validation).issubset(set(outer_train)))
                    coverage[validation] += 1
                    if scheme == "blocked_embargo1":
                        start = original_blocks[inner_index] * 20
                        stop = start + 20
                        np.testing.assert_array_equal(validation,
                            outer_train[(outer_train >= start) & (outer_train < stop)])
                        self.assertFalse(set(train) & set(range(max(0, start - 1), min(100, stop + 1))))
                    else:
                        np.testing.assert_array_equal(train, outer_train[expected_random[inner_index][0]])
                        np.testing.assert_array_equal(validation, outer_train[expected_random[inner_index][1]])
                    self.assertTrue((np.bincount(self.labels[train], minlength=5) > 0).all())
                    self.assertTrue((np.bincount(null_labels[scheme][fold][train], minlength=5) > 0).all())
                np.testing.assert_array_equal(coverage[outer_train], np.ones(len(outer_train)))
                self.assertEqual(coverage.sum(), len(outer_train))
                self.assertTrue((null_labels[scheme][fold][outer_validation] == -1).all())
                for record in metadata["schemes"][scheme]["folds"][fold]["inner_folds"]:
                    self.assertNotIn("labels", record)
                    self.assertNotIn("training_indices", record)
                    self.assertEqual(len(record["split_indices_sha256"]), 64)
            np.testing.assert_array_equal(outer_coverage, np.ones(100))
        json.dumps(metadata, allow_nan=False)

    def test_missing_true_or_shuffled_inner_class_refuses_before_any_fit(self):
        np = self.np
        rare = np.tile(np.arange(4), 25)
        rare[[0, 60]] = 4

        def must_not_fit(*args):
            self.fail("Failed nested preflight reached a model fit")

        with warnings.catch_warnings(), mock.patch.object(calibration, "ridge_probabilities", new=must_not_fit):
            warnings.simplefilter("ignore", UserWarning)
            with self.assertRaisesRegex(ValueError, "inner-training class is absent"):
                calibration.run_pair_probability_calibration(
                    self.auxiliary, self.eeg, rare, pair_id="generated")
            # The original round-robin labels retain every class in all inner
            # training sets; this deliberately fixed permutation alone removes
            # a class when its contiguous validation block is withheld.
            first_outer_train = np.arange(21, 100)
            order = np.argsort(self.labels[first_outer_train], kind="stable")

            class FixedPermutation:
                def permutation(self, size):
                    self_size = len(order)
                    if size != self_size:
                        raise AssertionError("Unexpected permutation before first-fold refusal")
                    return order

            with mock.patch.object(np.random, "default_rng", new=lambda seed: FixedPermutation()):
                with self.assertRaisesRegex(ValueError, "inner-training class is absent"):
                    calibration.run_pair_probability_calibration(
                        self.auxiliary, self.eeg, self.labels, pair_id="generated")

    def test_every_nested_fit_and_calibrator_excludes_outer_labels_and_reuses_one_null(self):
        np = self.np
        _, outer, inner, _, metadata = calibration._nested_plan(self.labels)
        roster = [(scheme, fold, train, validation) for scheme, folds in outer.items()
                  for fold, (train, validation) in enumerate(folds)]
        fit_count, temperature_count = 0, 0
        cache = {}

        def manual_block(matrix, train, validation):
            mean = matrix[train].mean(axis=0)
            scale = matrix[train].std(axis=0)
            denominator = np.where(scale > 0, scale, 1) * np.sqrt(matrix.shape[1])
            return (matrix[train] - mean) / denominator, (matrix[validation] - mean) / denominator

        def synthetic_probabilities(arm_index, stage, rows):
            weights = np.arange(1.0, 6.0) + arm_index / 10 + stage / 100
            if arm_index == 0 and stage == 4:
                weights[0] = 1e-30
            return np.tile(weights / weights.sum(), (rows, 1))

        def check_fit(train_matrix, supplied_labels, validation_matrix):
            nonlocal fit_count
            outer_index, within_outer = divmod(fit_count, 45)
            stage, arm_index = divmod(within_outer, 9)
            scheme, fold, outer_train, outer_validation = roster[outer_index]
            train, validation = inner[scheme][fold][stage] if stage < 4 else (outer_train, outer_validation)
            if arm_index == 0:
                cache["N"] = manual_block(self.auxiliary[:, :392], train, validation)
                cache["A"] = manual_block(self.auxiliary, train, validation)
                cache["E"] = manual_block(self.eeg, train, validation)
            a_train, a_test = cache["A"]
            e_train, e_test = cache["E"]
            if arm_index < 2:
                expected_train, expected_test = cache["N"]
            elif arm_index < 4:
                expected_train, expected_test = cache["A"]
            elif arm_index < 6:
                expected_train, expected_test = cache["E"]
            else:
                if arm_index == 7:
                    e_train, e_test = np.roll(e_train, 1, axis=0), np.roll(e_test, 1, axis=0)
                expected_train = np.concatenate((a_train, e_train), axis=1)
                expected_test = np.concatenate((a_test, e_test), axis=1)
            expected_labels = self.labels[train]
            if calibration.LEARNED_ARMS[arm_index].endswith("_shuffled"):
                seed = metadata["schemes"][scheme]["folds"][fold]["shuffle_seed"]
                fixed = self.labels[outer_train][np.random.default_rng(seed).permutation(len(outer_train))]
                expected_labels = fixed[np.searchsorted(outer_train, train)]
            np.testing.assert_array_equal(supplied_labels, expected_labels)
            np.testing.assert_allclose(train_matrix, expected_train, atol=1e-14, rtol=0)
            np.testing.assert_allclose(validation_matrix, expected_test, atol=1e-14, rtol=0)
            fit_count += 1
            return synthetic_probabilities(arm_index, stage, len(validation))

        def check_temperature(probabilities, supplied_labels):
            nonlocal temperature_count
            outer_index, arm_index = divmod(temperature_count, 9)
            scheme, fold, outer_train, _ = roster[outer_index]
            self.assertEqual(fit_count, outer_index * 45 + 36)
            expected = np.full((len(outer_train), 5), np.nan)
            for stage, (_, validation) in enumerate(inner[scheme][fold]):
                expected[np.searchsorted(outer_train, validation)] = synthetic_probabilities(
                    arm_index, stage, len(validation))
            np.testing.assert_array_equal(probabilities, expected)
            expected_labels = self.labels[outer_train]
            if calibration.LEARNED_ARMS[arm_index].endswith("_shuffled"):
                seed = metadata["schemes"][scheme]["folds"][fold]["shuffle_seed"]
                expected_labels = expected_labels[np.random.default_rng(seed).permutation(len(outer_train))]
            np.testing.assert_array_equal(supplied_labels, expected_labels)
            temperature_count += 1
            return {"inverse_temperature": 1.0, "boundary_hit": False}

        progress = []
        with mock.patch.object(calibration, "ridge_probabilities", new=check_fit), \
                mock.patch.object(calibration, "fit_inverse_temperature", new=check_temperature):
            report, outputs = calibration.run_pair_probability_calibration(
                self.auxiliary, self.eeg, self.labels, pair_id="generated", progress=progress.append)
        self.assertEqual((fit_count, temperature_count), (450, 90))
        self.assertEqual(len(progress), 60)
        for scheme in calibration.SCHEMES:
            self.assertEqual(set(outputs[scheme]), set(calibration.ARMS))
            metrics = report["schemes"][scheme]["metrics"]
            for arm, probabilities in outputs[scheme].items():
                self.assertEqual(probabilities.shape, (100, 5))
                self.assertTrue(np.isfinite(probabilities).all())
                expected_loss = float(np.mean([
                    -np.log(np.maximum(probabilities[self.labels == label, label], 1e-15)).mean()
                    for label in range(5)]))
                self.assertAlmostEqual(metrics[arm]["class_macro_log_loss"], expected_loss)
                self.assertEqual(report["schemes"][scheme]["true_class_probabilities_below_scoring_floor"][arm],
                                 int(np.count_nonzero(probabilities[np.arange(100), self.labels] < 1e-15)))
            self.assertEqual(report["schemes"][scheme]["true_class_probabilities_below_scoring_floor"]["N"], 20)
            self.assertTrue(report["schemes"][scheme]["all_argmax_predictions_preserved"])
            for comparator, gain in report["schemes"][scheme]["primary_log_loss_gains"].items():
                self.assertAlmostEqual(gain, metrics[comparator]["class_macro_log_loss"]
                                       - metrics[calibration.PRIMARY_ARM]["class_macro_log_loss"])
            for arm, gain in report["schemes"][scheme]["paired_calibration_log_loss_gains"].items():
                self.assertAlmostEqual(gain, metrics[arm]["class_macro_log_loss"]
                                       - metrics[arm + "_calibrated"]["class_macro_log_loss"])
        json.dumps(report, allow_nan=False)

    def test_outer_validation_label_changes_cannot_change_first_block_temperatures(self):
        np = self.np

        def fixed_generated_predictions(auxiliary, eeg, labels, null_labels, train, validation):
            # A fixed synthetic trial-index signal, never reading supplied
            # labels; all model variants are stubbed solely for this boundary.
            values = np.full((len(validation), 5), 0.1)
            values[np.arange(len(validation)), validation % 5] = 0.6
            return {arm: values.copy() for arm in calibration.LEARNED_ARMS}

        changed = self.labels.copy()
        changed[:20] = (changed[:20] + 1) % 5
        with mock.patch.object(calibration, "_predict_arms", new=fixed_generated_predictions):
            baseline, _ = calibration.run_pair_probability_calibration(
                self.auxiliary, self.eeg, self.labels, pair_id="generated")
            altered, _ = calibration.run_pair_probability_calibration(
                self.auxiliary, self.eeg, changed, pair_id="generated")
        original_fits = baseline["schemes"]["blocked_embargo1"]["folds"][0]["temperature_fits"]
        changed_fits = altered["schemes"]["blocked_embargo1"]["folds"][0]["temperature_fits"]
        self.assertEqual(original_fits, changed_fits)
        self.assertEqual(original_fits["A_full_all"]["inverse_temperature"], 20.0)

    def test_uncalibrated_outputs_exactly_match_existing_readout_and_calibration_preserves_ba(self):
        np = self.np
        views = {name: self.eeg[:, :count] for name, count in previous.TIME_FREQUENCY_FEATURE_COUNTS.items()}
        original, original_probabilities = previous.run_pair_power_discovery(
            self.auxiliary, views, self.labels, pair_id="generated", mode="time_frequency")
        report, probabilities = calibration.run_pair_probability_calibration(
            self.auxiliary, self.eeg, self.labels, pair_id="generated")
        for scheme in calibration.SCHEMES:
            metrics = report["schemes"][scheme]["metrics"]
            for arm in (*calibration.LEARNED_ARMS, "uniform", "training_prior"):
                np.testing.assert_array_equal(probabilities[scheme][arm], original_probabilities[scheme][arm])
                self.assertEqual(metrics[arm], original["schemes"][scheme]["metrics"][arm])
            for arm in calibration.LEARNED_ARMS:
                self.assertEqual(metrics[arm]["balanced_accuracy"], metrics[arm + "_calibrated"]["balanced_accuracy"])
                self.assertEqual(metrics[arm]["accuracy"], metrics[arm + "_calibrated"]["accuracy"])
            self.assertTrue(report["schemes"][scheme]["all_argmax_predictions_preserved"])
            self.assertEqual(len(report["schemes"][scheme]["folds"]), 5)
        json.dumps(report, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
