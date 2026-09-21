"""Numerical and scientific-contract checks for the fixed speech comparison."""

import importlib.util
import unittest

from neurodecodekit.evaluation.speech_reproduction import (
    COMPACT_ARMS,
    PRIMARY_ARM,
    cyclic_derangement_indices,
    fixed_channel_features,
    predict_compact_arms,
    ridge_probabilities,
    score_speech_predictions,
    shuffled_calibration_labels,
)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
class SpeechReproductionTests(unittest.TestCase):
    def test_dual_ridge_matches_independent_primal_solution_with_intercept(self):
        import numpy as np

        rng = np.random.default_rng(14)
        train = rng.normal(size=(30, 8)) + 4
        evaluation = rng.normal(size=(6, 8)) + 3
        labels = np.tile(np.arange(5), 6)
        x_mean = train.mean(0)
        y_mean = np.eye(5)[labels].mean(0)
        xc = train - x_mean
        weights = np.linalg.solve(xc.T @ xc + np.eye(8), xc.T @ (np.eye(5)[labels] - y_mean))
        expected_scores = (evaluation - x_mean) @ weights + y_mean
        expected = np.exp(expected_scores - expected_scores.max(axis=1, keepdims=True))
        expected /= expected.sum(axis=1, keepdims=True)
        np.testing.assert_allclose(ridge_probabilities(train, labels, evaluation), expected, atol=1e-12)

    def test_prediction_is_independent_of_other_evaluation_values(self):
        import numpy as np

        rng = np.random.default_rng(3)
        train = rng.normal(size=(25, 7))
        evaluation = rng.normal(size=(6, 7))
        eeg = {name: train.copy() for name in ("raw", "filtered", "preaction")}
        eeg_eval = {name: evaluation.copy() for name in eeg}
        original = predict_compact_arms(np.tile(np.arange(5), 5), train, evaluation, eeg, eeg_eval)
        expanded = predict_compact_arms(
            np.tile(np.arange(5), 5),
            train,
            np.concatenate((evaluation, np.full((2, 7), 1e9))),
            eeg,
            {name: np.concatenate((value, np.full((2, 7), 1e9))) for name, value in eeg_eval.items()},
            eval_recordings=["a"] * 6 + ["b"] * 2,
        )
        self.assertEqual(set(original), set(COMPACT_ARMS))
        for arm in COMPACT_ARMS:
            np.testing.assert_allclose(original[arm], expanded[arm][:6], atol=1e-12)

    def test_derangement_and_shuffle_preserve_recording_membership(self):
        import numpy as np

        records = ["a", "a", "a", "b", "b", "b", "b"]
        indices = cyclic_derangement_indices(records, 7)
        self.assertTrue(np.all(indices != np.arange(7)))
        np.testing.assert_array_equal(np.asarray(records)[indices], records)
        labels = np.array([0, 1, 2, 1, 2, 3, 4])
        shuffled = shuffled_calibration_labels(labels, records)
        np.testing.assert_array_equal(np.sort(shuffled[:3]), np.sort(labels[:3]))
        np.testing.assert_array_equal(np.sort(shuffled[3:]), np.sort(labels[3:]))
        np.testing.assert_array_equal(shuffled, shuffled_calibration_labels(labels, records))
        with self.assertRaisesRegex(ValueError, "at least two"):
            cyclic_derangement_indices(["a", "b"], 2)

    def test_features_preserve_expected_temporal_and_spectral_quantities(self):
        import numpy as np

        time = np.arange(320) / 256
        signal = np.sin(2 * np.pi * 16 * time)[None, None, :]
        features = fixed_channel_features(signal)
        self.assertEqual(features.shape, (1, 70))
        np.testing.assert_allclose(features[0, :64], signal.reshape(64, 5).mean(1))
        self.assertEqual(int(np.argmax(features[0, 64:])), 3)
        self.assertAlmostEqual(float(np.exp(features[0, 67])), 0.5)
        aux = fixed_channel_features(signal, full_trial=np.tile(signal, (1, 1, 5)))
        self.assertEqual(aux.shape, (1, 78))
        self.assertAlmostEqual(float(aux[0, -2]), 2**-0.5)
        self.assertAlmostEqual(float(aux[0, -1]), 2.0)

    def test_scorer_weights_people_equally_and_keeps_reference_separate(self):
        import numpy as np

        labels, people, tasks = [], [], []
        for task in ("minimallyovert", "covert"):
            for person, repeats in zip(("sub-1", "sub-2", "sub-3"), (1, 2, 10)):
                labels.extend(list(range(5)) * repeats)
                people.extend([person] * (5 * repeats))
                tasks.extend([task] * (5 * repeats))
        labels = np.array(labels)
        predictions = {arm: np.full((len(labels), 5), 0.2) for arm in COMPACT_ARMS}
        predictions["eegnet_reference"] = np.eye(5)[labels] * 0.8 + 0.04
        for index, person in enumerate(people):
            correct_probability = {"sub-1": 0.8, "sub-2": 0.6, "sub-3": 0.1}[person]
            predictions[PRIMARY_ARM][index] = (1 - correct_probability) / 4
            predictions[PRIMARY_ARM][index, labels[index]] = correct_probability
        result = score_speech_predictions(predictions, labels, people, tasks)
        overt = result["conditions"]["minimallyovert"]
        self.assertFalse(overt["conditional_descriptive_success"])
        self.assertTrue(overt["reference_all_three_above_chance"])
        expected_loss = -np.log([0.8, 0.6, 0.1]).mean()
        self.assertAlmostEqual(
            overt["equal_person_metrics"][PRIMARY_ARM]["equal_person_class_macro_log_loss"],
            expected_loss,
        )
        self.assertEqual(overt["primary_edges"]["uniform"]["positive_people"], 2)

    def test_missing_class_is_incomplete_instead_of_changing_denominator(self):
        import numpy as np

        labels = np.tile(np.arange(4), 3)
        predictions = {arm: np.full((12, 5), 0.2) for arm in COMPACT_ARMS}
        predictions["eegnet_reference"] = predictions["uniform"].copy()
        result = score_speech_predictions(
            predictions,
            labels,
            ["sub-1"] * 4 + ["sub-2"] * 4 + ["sub-3"] * 4,
            ["minimallyovert"] * 12,
        )
        overt = result["conditions"]["minimallyovert"]
        self.assertEqual(overt["status"], "incomplete")
        self.assertIsNone(overt["equal_person_metrics"][PRIMARY_ARM]["equal_person_class_macro_log_loss"])
        self.assertFalse(overt["conditional_descriptive_success"])
        self.assertEqual(len(overt["notes"]), 3)
        self.assertEqual(result["conditions"]["covert"]["status"], "incomplete")

    def test_all_controls_must_be_beaten_in_every_person(self):
        import numpy as np

        labels = np.tile(np.arange(5), 6)
        people = (["sub-1"] * 5 + ["sub-2"] * 5 + ["sub-3"] * 5) * 2
        tasks = ["minimallyovert"] * 15 + ["covert"] * 15
        predictions = {arm: np.full((30, 5), 0.2) for arm in COMPACT_ARMS}
        predictions["eegnet_reference"] = predictions["uniform"].copy()
        predictions[PRIMARY_ARM] = np.eye(5)[labels] * 0.8 + 0.04
        result = score_speech_predictions(predictions, labels, people, tasks)
        self.assertTrue(result["conditions"]["minimallyovert"]["conditional_descriptive_success"])
        self.assertFalse(result["conditions"]["minimallyovert"]["reference_all_three_above_chance"])
        predictions["auxiliary_deranged_eeg"][:5] = predictions[PRIMARY_ARM][:5]
        result = score_speech_predictions(predictions, labels, people, tasks)
        self.assertFalse(result["conditions"]["minimallyovert"]["conditional_descriptive_success"])
        self.assertTrue(result["conditions"]["covert"]["conditional_descriptive_success"])

    def test_invalid_probability_and_mismatched_eeg_capacity_refuse(self):
        import numpy as np

        labels = np.tile(np.arange(5), 3)
        predictions = {arm: np.full((15, 5), 0.3) for arm in COMPACT_ARMS}
        predictions["eegnet_reference"] = predictions["uniform"].copy()
        with self.assertRaisesRegex(ValueError, "sum to one"):
            score_speech_predictions(
                predictions, labels, ["sub-1"] * 15, ["minimallyovert"] * 15
            )
        with self.assertRaisesRegex(ValueError, "identical feature dimensions"):
            predict_compact_arms(
                labels, np.zeros((15, 2)), np.zeros((3, 2)),
                {"raw": np.zeros((15, 2)), "filtered": np.zeros((15, 3)), "preaction": np.zeros((15, 2))},
                {"raw": np.zeros((3, 2)), "filtered": np.zeros((3, 3)), "preaction": np.zeros((3, 2))},
            )


if __name__ == "__main__":
    unittest.main()
