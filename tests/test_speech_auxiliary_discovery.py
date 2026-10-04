"""Generated-only checks of the fixed calibration modality experiment."""

import importlib.util
import json
import unittest
from unittest import mock

from neurodecodekit.experiments import speech_auxiliary_discovery as discovery


class AuxiliaryDiscoveryContractTests(unittest.TestCase):
    def test_fixed_modality_map_has_no_eeg_or_online_inputs(self):
        self.assertEqual(discovery.MODALITY_ARMS, ("T", "D", "DT", "M", "E", "L", "P", "N"))
        self.assertEqual(len(discovery.ARMS), 18)
        self.assertEqual([len(columns) for columns in discovery.MODALITY_COLUMNS.values()],
                         [2, 78, 80, 78, 78, 156, 312, 392])
        columns = discovery.MODALITY_COLUMNS
        self.assertEqual(set(columns["P"]), set(columns["M"]) | set(columns["E"]) | set(columns["L"]))
        self.assertFalse(set(columns["P"]) & set(columns["DT"]))
        self.assertEqual(set(columns["N"]), set(range(392)))


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("sklearn"),
                     "Optional NumPy and sklearn required")
class AuxiliaryDiscoveryNumericalTests(unittest.TestCase):
    def setUp(self):
        import numpy as np

        self.np = np
        self.labels = np.tile(np.arange(5), 20)
        self.features = np.random.default_rng(12).normal(size=(100, 392))

    def test_blocked_folds_are_contiguous_purged_and_exactly_cover_original_trials(self):
        np = self.np
        _, plans, metadata = discovery._split_plan(self.labels)
        seen = []
        for fold, (train, validation) in enumerate(plans["blocked_embargo1"]):
            np.testing.assert_array_equal(validation, np.arange(fold * 20, (fold + 1) * 20))
            self.assertFalse(set(train) & set(validation))
            self.assertFalse(set(train) & {int(validation[0]) - 1, int(validation[-1]) + 1})
            seen.extend(validation.tolist())
        self.assertEqual(seen, list(range(100)))
        folds = metadata["schemes"]["blocked_embargo1"]["folds"]
        self.assertEqual([fold["training_trials"] for fold in folds], [79, 78, 78, 78, 79])
        self.assertEqual([fold["embargoed_trials"] for fold in folds], [1, 2, 2, 2, 1])

    def test_stratification_matches_frozen_library_call_and_metadata_is_deterministic(self):
        from sklearn.model_selection import StratifiedKFold

        np = self.np
        _, plans, metadata = discovery._split_plan(self.labels)
        expected = StratifiedKFold(5, shuffle=True, random_state=20260921).split(
            np.zeros(100), self.labels)
        for actual, target in zip(plans["stratified_shuffled"], expected):
            np.testing.assert_array_equal(actual[0], target[0])
            np.testing.assert_array_equal(actual[1], target[1])
        self.assertEqual(metadata, discovery.preflight_calibration(self.labels))
        for fold in metadata["schemes"]["stratified_shuffled"]["folds"]:
            self.assertEqual(fold["training_class_counts"], [16] * 5)
            self.assertEqual(fold["validation_class_counts"], [4] * 5)
            self.assertEqual(len(fold["split_indices_sha256"]), 64)
            self.assertNotIn("validation_indices", fold)
        json.dumps(metadata, allow_nan=False)

    def test_missing_training_class_refuses_before_any_fit_without_dropping_folds(self):
        np = self.np
        concentrated = np.concatenate((np.full(8, 4), np.tile(np.arange(4), 23)))
        with mock.patch.object(discovery, "ridge_probabilities") as fit:
            with self.assertRaisesRegex(ValueError, "training class is absent"):
                discovery.run_pair_discovery(self.features, concentrated, pair_id="generated")
        fit.assert_not_called()

    def test_wrong_trial_count_classes_shape_or_nonfinite_values_refuse(self):
        np = self.np
        for labels in (self.labels[:-1], np.tile(np.arange(4), 25), self.labels.astype(float)):
            with self.subTest(labels_shape=labels.shape), self.assertRaises(ValueError):
                discovery.preflight_calibration(labels)
        for matrix in (self.features[:, :-1], self.features[:-1], np.full((100, 392), np.nan)):
            with self.subTest(shape=matrix.shape), self.assertRaises(ValueError):
                discovery.run_pair_discovery(matrix, self.labels, pair_id="generated")

    def test_every_arm_uses_training_only_scaling_and_the_same_training_shuffle(self):
        np = self.np
        calls = []

        def fake_fit(train, labels, evaluation):
            calls.append((train.copy(), labels.copy(), evaluation.copy()))
            return np.full((len(evaluation), 5), 0.2)

        with mock.patch.object(discovery, "ridge_probabilities", side_effect=fake_fit):
            report, predictions = discovery.run_pair_discovery(
                self.features, self.labels, pair_id="generated")
        self.assertEqual(len(calls), 2 * 5 * 8 * 2)
        _, plans, _ = discovery._split_plan(self.labels)
        for scheme_index, scheme in enumerate(discovery.SCHEMES):
            for fold, (train_indices, _) in enumerate(plans[scheme]):
                offset = (scheme_index * 5 + fold) * 16
                truth = self.labels[train_indices]
                expected_shuffle = truth[np.random.default_rng(
                    20260921 + 100 * scheme_index + fold).permutation(len(truth))]
                for arm_index, columns in enumerate(discovery.MODALITY_COLUMNS.values()):
                    train, actual_labels, _ = calls[offset + 2 * arm_index]
                    np.testing.assert_array_equal(actual_labels, truth)
                    np.testing.assert_array_equal(calls[offset + 2 * arm_index + 1][1], expected_shuffle)
                    np.testing.assert_allclose(train.mean(axis=0), 0, atol=1e-14)
                    np.testing.assert_allclose(train.std(axis=0), 1 / np.sqrt(len(columns)), atol=1e-14)
                np.testing.assert_array_equal(np.bincount(expected_shuffle, minlength=5),
                                              np.bincount(truth, minlength=5))
        self.assertFalse(report["confirmatory_result"])
        self.assertEqual(set(predictions), set(discovery.SCHEMES))
        json.dumps(report, allow_nan=False)

    def test_held_out_and_embargo_values_do_not_change_first_fold_scaling(self):
        np = self.np
        original_standardize = discovery._standardized_block
        first_training = []

        def capture(train, validation):
            standardized = original_standardize(train, validation)
            if not first_training:
                first_training.append(standardized[0].copy())
            return standardized

        def fake_fit(train, labels, evaluation):
            return np.full((len(evaluation), 5), 0.2)

        with mock.patch.object(discovery, "_standardized_block", side_effect=capture), \
                mock.patch.object(discovery, "ridge_probabilities", side_effect=fake_fit):
            discovery.run_pair_discovery(self.features, self.labels, pair_id="generated")
            baseline = first_training.pop()
            changed = self.features.copy()
            changed[:21] = 1e9
            discovery.run_pair_discovery(changed, self.labels, pair_id="generated")
        np.testing.assert_array_equal(first_training[0], baseline)

    def test_generated_modality_signal_and_pooled_metrics_with_missing_validation_classes(self):
        np = self.np
        # Every block lacks a different validation class; training retains all
        # five. The M columns alone encode a generated categorical signal.
        labels = np.concatenate([np.tile([(block + k) % 5 for k in range(4)], 5)
                                 for block in range(5)])
        features = np.random.default_rng(44).normal(size=(100, 392))
        features[:, 78:156] = np.eye(5)[labels][:, np.arange(78) % 5]
        progress = []
        report, outputs = discovery.run_pair_discovery(
            features, labels, pair_id="generated", progress=progress.append)
        self.assertEqual(len(progress), 20)
        for scheme in discovery.SCHEMES:
            metrics = report["schemes"][scheme]["metrics"]
            self.assertEqual(metrics["M"]["balanced_accuracy"], 1.0)
            self.assertLess(metrics["M_shuffled"]["balanced_accuracy"], 0.5)
            self.assertTrue(metrics["M"]["complete_five_class_endpoint"])
            self.assertEqual(metrics["M"]["class_counts"], [20] * 5)
            self.assertAlmostEqual(metrics["uniform"]["class_macro_log_loss"], float(np.log(5)))
            probabilities = outputs[scheme]["M"]
            independent_macro_loss = float(np.mean([
                -np.log(probabilities[labels == label, label]).mean() for label in range(5)]))
            self.assertAlmostEqual(metrics["M"]["class_macro_log_loss"], independent_macro_loss)
            for arm in discovery.ARMS:
                self.assertEqual(outputs[scheme][arm].shape, (100, 5))
                np.testing.assert_allclose(outputs[scheme][arm].sum(axis=1), 1, atol=1e-12)
        self.assertTrue(all(0 in fold["validation_class_counts"]
                            for fold in report["schemes"]["blocked_embargo1"]["folds"]))
        json.dumps(report, allow_nan=False)


if __name__ == "__main__":
    unittest.main()
