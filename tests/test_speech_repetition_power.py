"""Generated-only contracts for matched repetition-power discovery."""

import importlib.util
import json
import unittest
from unittest import mock

from neurodecodekit.evaluation.speech_reproduction import _log_band_energies
from neurodecodekit.experiments import speech_auxiliary_discovery as auxiliary_discovery
from neurodecodekit.experiments import speech_repetition_power as discovery


class RepetitionPowerContractTests(unittest.TestCase):
    def test_fixed_roster_and_same_existing_split_contract(self):
        self.assertEqual(discovery.REPRESENTATIONS,
                         ("raw_evoked", "raw_repetition", "filtered_evoked", "filtered_repetition"))
        self.assertEqual(len(discovery.ARMS), 24)
        self.assertEqual(len(set(discovery.ARMS)), 24)
        self.assertEqual(discovery.PRIMARY_ARM, "N_filtered_repetition")
        self.assertEqual(discovery.PRIMARY_COMPARATORS, (
            "N", "N_filtered_evoked", "N_filtered_repetition_deranged",
            "N_filtered_repetition_shuffled", "uniform", "training_prior"))
        self.assertIs(discovery.preflight_calibration, auxiliary_discovery.preflight_calibration)
        self.assertEqual(discovery.SCHEMES, auxiliary_discovery.SCHEMES)
        self.assertEqual(discovery.SEED, auxiliary_discovery.SEED)
        self.assertEqual(discovery.N_EEG_FEATURES, 128 * 6)


@unittest.skipUnless(importlib.util.find_spec("numpy"), "Optional NumPy required")
class RepetitionPowerFeatureTests(unittest.TestCase):
    def setUp(self):
        import numpy as np

        self.np = np

    def test_identical_repetitions_match_evoked_and_existing_fft_definition(self):
        np = self.np
        waveform = np.random.default_rng(21).normal(size=(2, 128, 320)).astype(np.float32)
        trials = np.tile(waveform[:, :, None, :], (1, 1, 5, 1)).reshape(2, 128, 1600)
        result = discovery.paired_power_features(trials)
        expected = _log_band_energies(waveform.astype(np.float64), 256.0).reshape(2, 768)
        for name in ("evoked", "repetition"):
            self.assertEqual(result[name].shape, (2, 768))
            self.assertEqual(result[name].dtype, np.float64)
            np.testing.assert_allclose(result[name], expected, rtol=0, atol=1e-14)
        np.testing.assert_allclose(result["diagnostics"]["coherent_to_total_band_power_ratio"],
                                   np.ones(6), rtol=0, atol=1e-14)
        json.dumps(result["diagnostics"], allow_nan=False)

    def test_phase_cancellation_loses_evoked_but_retains_repetition_power(self):
        np = self.np
        time = np.arange(320) / 256.0
        waves = np.array([np.sin(2 * np.pi * 8 * time + 2 * np.pi * repeat / 5)
                          for repeat in range(5)], dtype=np.float32)
        trials = np.tile(waves.reshape(1, 1, 1600), (1, 128, 1))
        result = discovery.paired_power_features(trials)
        evoked = result["evoked"].reshape(1, 128, 6)
        repetition = result["repetition"].reshape(1, 128, 6)
        np.testing.assert_allclose(np.exp(repetition[:, :, 2]), 0.5, rtol=1e-6)
        self.assertTrue(np.all(repetition[:, :, 2] - evoked[:, :, 2] > 20))
        self.assertLess(result["diagnostics"]["coherent_to_total_band_power_ratio"][2], 1e-12)

    def test_repetition_uses_log_mean_power_not_mean_log_power(self):
        np = self.np
        time = np.arange(320) / 256.0
        waves = np.array([amplitude * np.sin(2 * np.pi * 8 * time)
                          for amplitude in range(1, 6)], dtype=np.float32)
        trials = np.tile(waves.reshape(1, 1, 1600), (1, 128, 1))
        result = discovery.paired_power_features(trials)
        repetition = result["repetition"].reshape(1, 128, 6)[0, 0, 2]
        per_repetition = _log_band_energies(waves.astype(np.float64), 256.0)[:, 2]
        self.assertAlmostEqual(repetition, float(np.log(np.exp(per_repetition).mean())), places=13)
        self.assertGreater(repetition - float(per_repetition.mean()), 0.4)

    def test_diagnostics_stream_by_summing_power_not_averaging_ratios(self):
        np = self.np
        trials = np.random.default_rng(19).normal(size=(3, 128, 1600)).astype(np.float32)
        trials[1] *= 20
        pooled = discovery.paired_power_features(trials)["diagnostics"]
        parts = [discovery.paired_power_features(trials[row:row + 1])["diagnostics"]
                 for row in range(3)]
        self.assertEqual(sum(part["n_trials"] for part in parts), pooled["n_trials"])
        for key in ("coherent_band_power_sum", "total_band_power_sum"):
            np.testing.assert_allclose(np.sum([part[key] for part in parts], axis=0),
                                       pooled[key], rtol=1e-14)
        ratios = np.asarray(pooled["coherent_band_power_sum"]) / pooled["total_band_power_sum"]
        np.testing.assert_allclose(pooled["coherent_to_total_band_power_ratio"], ratios)
        self.assertNotIn("trial_ratios", pooled)
        self.assertNotIn("labels", pooled)
        json.dumps(pooled, allow_nan=False)

    def test_zero_energy_has_finite_features_and_null_ratio_and_invalid_inputs_refuse(self):
        np = self.np
        result = discovery.paired_power_features(np.zeros((1, 128, 1600), dtype=np.float32))
        self.assertTrue(np.isfinite(result["evoked"]).all())
        self.assertTrue(np.isfinite(result["repetition"]).all())
        self.assertEqual(result["diagnostics"]["coherent_to_total_band_power_ratio"], [None] * 6)
        json.dumps(result["diagnostics"], allow_nan=False)
        for values in (np.zeros((0, 128, 1600)), np.zeros((1, 127, 1600)),
                       np.zeros((1, 128, 1599)), np.zeros((128, 1600)),
                       np.full((1, 128, 1600), np.nan)):
            with self.subTest(shape=values.shape), self.assertRaises(ValueError):
                discovery.paired_power_features(values)


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("sklearn"),
                     "Optional NumPy and sklearn required")
class RepetitionPowerComparisonTests(unittest.TestCase):
    def setUp(self):
        import numpy as np

        self.np = np
        self.labels = np.tile(np.arange(5), 20)
        rng = np.random.default_rng(37)
        self.auxiliary = rng.normal(size=(100, 392))
        self.eeg = {name: rng.normal(size=(100, 768)) for name in discovery.REPRESENTATIONS}

    def test_derangement_has_no_self_donors_or_train_validation_crossing(self):
        np = self.np
        _, plans, _ = auxiliary_discovery._split_plan(self.labels)
        for folds in plans.values():
            for train, validation in folds:
                donors = discovery.fold_derangement_indices(train, validation)
                for original, shuffled in zip((train, validation), donors):
                    np.testing.assert_array_equal(shuffled, np.roll(original, 1))
                    self.assertEqual(set(original), set(shuffled))
                    self.assertTrue(np.all(original != shuffled))
                self.assertFalse(set(donors[0]) & set(validation))
                self.assertFalse(set(donors[1]) & set(train))
        for train, validation in (([0], [1, 2]), ([0, 1], [1, 2]), ([0, 0], [2, 3]),
                                  ([0.0, 1.0], [2, 3]), ([-1, 0], [2, 3])):
            with self.subTest(train=train), self.assertRaises(ValueError):
                discovery.fold_derangement_indices(train, validation)

    def test_all_arms_train_only_scaling_shared_labels_and_fold_local_eeg_donors(self):
        np = self.np
        _, plans, metadata = auxiliary_discovery._split_plan(self.labels)
        fold_roster = [(scheme, fold, train, validation) for scheme, folds in plans.items()
                       for fold, (train, validation) in enumerate(folds)]
        calls = 0
        cache = {}

        def manual_block(values, train, validation):
            mean = values[train].mean(axis=0)
            scale = values[train].std(axis=0)
            denominator = np.where(scale > 0, scale, 1) * np.sqrt(values.shape[1])
            return (values[train] - mean) / denominator, (values[validation] - mean) / denominator

        def check_fit(actual_train, actual_labels, actual_test):
            nonlocal calls
            fold_index, call_in_fold = divmod(calls, 22)
            scheme, fold, train, validation = fold_roster[fold_index]
            if call_in_fold == 0:
                cache["auxiliary"] = manual_block(self.auxiliary, train, validation)
                cache["eeg"] = {name: manual_block(values, train, validation)
                                for name, values in self.eeg.items()}
            truth = self.labels[train]
            seed = metadata["schemes"][scheme]["folds"][fold]["shuffle_seed"]
            shuffled = truth[np.random.default_rng(seed).permutation(len(train))]
            aux_train, aux_test = cache["auxiliary"]
            if call_in_fold < 2:
                expected_train, expected_test = aux_train, aux_test
                expected_labels = truth if call_in_fold == 0 else shuffled
            else:
                representation, variant = divmod(call_in_fold - 2, 5)
                eeg_train, eeg_test = cache["eeg"][discovery.REPRESENTATIONS[representation]]
                if variant == 3:
                    eeg_train, eeg_test = np.roll(eeg_train, 1, axis=0), np.roll(eeg_test, 1, axis=0)
                if variant < 2:
                    expected_train, expected_test = eeg_train, eeg_test
                else:
                    expected_train = np.concatenate((aux_train, eeg_train), axis=1)
                    expected_test = np.concatenate((aux_test, eeg_test), axis=1)
                expected_labels = shuffled if variant in (1, 4) else truth
            np.testing.assert_allclose(actual_train, expected_train, rtol=0, atol=1e-14)
            np.testing.assert_allclose(actual_test, expected_test, rtol=0, atol=1e-14)
            np.testing.assert_array_equal(actual_labels, expected_labels)
            calls += 1
            return np.full((len(actual_test), 5), 0.2)

        # A direct replacement checks every call without retaining 220 large
        # argument tuples in a Mock's lifetime call history.
        with mock.patch.object(discovery, "ridge_probabilities", new=check_fit):
            report, outputs = discovery.run_pair_power_discovery(
                self.auxiliary, self.eeg, self.labels, pair_id="generated")
        self.assertEqual(calls, 220)
        self.assertFalse(report["confirmatory_result"])
        for scheme in discovery.SCHEMES:
            self.assertEqual(set(outputs[scheme]), set(discovery.ARMS))
            for actual, expected in zip(report["schemes"][scheme]["folds"],
                                        metadata["schemes"][scheme]["folds"]):
                self.assertEqual({key: value for key, value in actual.items()
                                  if key != "eeg_derangement_indices_sha256"}, expected)
                self.assertEqual(len(actual["eeg_derangement_indices_sha256"]), 64)
        json.dumps(report, allow_nan=False)

    def test_generated_signal_pools_original_trials_and_reports_exact_primary_gains(self):
        np = self.np
        labels = np.concatenate([np.tile([(block + k) % 5 for k in range(4)], 5)
                                 for block in range(5)])
        eeg = {name: np.eye(5)[labels][:, np.arange(768) % 5]
               for name in discovery.REPRESENTATIONS}
        progress = []
        with mock.patch.object(discovery, "_metrics", wraps=discovery._metrics) as metrics_call:
            report, outputs = discovery.run_pair_power_discovery(
                np.zeros((100, 392)), eeg, labels, pair_id="generated", progress=progress.append)
        self.assertEqual(metrics_call.call_count, 48)
        self.assertTrue(all(call.args[0].shape == (100, 5) for call in metrics_call.call_args_list))
        self.assertEqual(len(progress), 20)
        for scheme in discovery.SCHEMES:
            metrics = report["schemes"][scheme]["metrics"]
            self.assertEqual(metrics["filtered_repetition"]["balanced_accuracy"], 1.0)
            self.assertLess(metrics["filtered_repetition_shuffled"]["balanced_accuracy"], 0.5)
            for arm in discovery.ARMS:
                probabilities = outputs[scheme][arm]
                self.assertEqual(probabilities.shape, (100, 5))
                np.testing.assert_allclose(probabilities.sum(axis=1), 1, atol=1e-12)
                expected = float(np.mean([-np.log(probabilities[labels == label, label]).mean()
                                          for label in range(5)]))
                self.assertAlmostEqual(metrics[arm]["class_macro_log_loss"], expected)
                self.assertTrue(metrics[arm]["complete_five_class_endpoint"])
                self.assertEqual(metrics[arm]["class_counts"], [20] * 5)
            for comparator, gain in report["schemes"][scheme]["primary_log_loss_gains"].items():
                self.assertAlmostEqual(gain, metrics[comparator]["class_macro_log_loss"]
                                       - metrics[discovery.PRIMARY_ARM]["class_macro_log_loss"])
        self.assertTrue(all(0 in fold["validation_class_counts"]
                            for fold in report["schemes"]["blocked_embargo1"]["folds"]))
        json.dumps(report, allow_nan=False)

if __name__ == "__main__":
    unittest.main()
