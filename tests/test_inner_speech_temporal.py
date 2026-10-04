"""Generated-array checks only; no recording, source path or real experiment access."""

import importlib.util
import json
import unittest
from unittest import mock

from neurodecodekit.experiments import inner_speech as old
from neurodecodekit.experiments import inner_speech_temporal as temporal


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
class InnerSpeechTemporalTests(unittest.TestCase):
    def features(self, n=40):
        import numpy as np
        return {key: np.zeros((n, width)) for key, width in temporal.FEATURE_WIDTHS.items()}

    def test_signed_bins_reference_demean_dimensions_and_input_isolation(self):
        import numpy as np
        rng = np.random.default_rng(40)
        for samples in (384, 2048):
            eeg, exg = rng.normal(size=(128, samples)), rng.normal(size=(8, samples))
            before_eeg, before_exg = eeg.copy(), exg.copy()
            actual = temporal.temporal_window_features(eeg, exg)
            referenced_eeg = eeg - eeg.mean(axis=0)
            referenced_exg = exg - (exg[0] + exg[1]) / 2
            expected_exg = np.vstack((referenced_exg, exg[2] - exg[3],
                                      exg[4] - exg[5], exg[6] - exg[7]))
            for name, values, width in (("E", referenced_eeg, 4096),
                                        ("P_temporal", expected_exg, 352)):
                expected = np.array([[part.mean() - row.mean() for part in np.split(row, 32)]
                                     for row in values]).reshape(-1)
                self.assertEqual(actual[name].shape, (width,))
                np.testing.assert_allclose(actual[name], expected, atol=1e-14)
            flipped = temporal.temporal_window_features(-eeg, -exg)
            np.testing.assert_array_equal(flipped["E"], -actual["E"])
            np.testing.assert_array_equal(flipped["P_temporal"], -actual["P_temporal"])
            np.testing.assert_array_equal(temporal.temporal_window_features(eeg, exg * 9)["E"], actual["E"])
            np.testing.assert_array_equal(temporal.temporal_window_features(eeg * 9, exg)["P_temporal"],
                                          actual["P_temporal"])
            np.testing.assert_array_equal(eeg, before_eeg)
            np.testing.assert_array_equal(exg, before_exg)
            common = np.tile(np.linspace(-2, 2, samples), (128, 1))
            np.testing.assert_allclose(temporal.temporal_window_features(common, exg)["E"], 0, atol=1e-14)

    def test_invalid_windows_and_dimensions_refuse(self):
        import numpy as np
        eeg, exg = np.zeros((128, 2048)), np.zeros((8, 2048))
        for bad_eeg, bad_exg, sfreq in ((eeg[:127], exg, 1024), (eeg, exg[:7], 1024),
                                      (eeg[:, :384], exg, 1024), (eeg[:, :-1], exg[:, :-1], 1024),
                                      (eeg, exg, 256), (eeg + np.nan, exg, 1024)):
            with self.subTest(shapes=(bad_eeg.shape, bad_exg.shape), sfreq=sfreq), self.assertRaises(ValueError):
                temporal.temporal_window_features(bad_eeg, bad_exg, sfreq=sfreq)

    def test_training_only_scaling_shared_p_and_fold_local_derangement(self):
        import numpy as np
        features = self.features(8)
        for offset, values in enumerate(features.values()):
            values[:] = (np.arange(8, dtype=float) ** (offset + 1))[:, None]
            values[4:] += 100000  # cannot affect any fitted scale
        train, validation = np.array([0, 1, 2, 3]), np.array([5, 6, 7])
        labels, null = np.arange(8) % 4, (np.arange(8) + 1) % 4
        expected = {}
        for key, values in features.items():
            fit = values[train]
            denominator = fit.std(axis=0) * np.sqrt(fit.shape[1])
            expected[key] = ((fit - fit.mean(axis=0)) / denominator,
                             (values[validation] - fit.mean(axis=0)) / denominator)
        calls = 0

        def inspect_fit(fit, fit_labels, evaluation):
            nonlocal calls
            arm = temporal.LEARNED_ARMS[calls]
            calls += 1
            np.testing.assert_array_equal(fit_labels, (null if arm in temporal.SHUFFLED_ARMS else labels)[train])
            if arm == "P":
                wanted = expected["P"]
            elif arm.startswith("action_eeg"):
                wanted = expected["E_action"]
            elif arm.startswith("cue_eeg"):
                wanted = expected["E_cue"]
            else:
                key = {"cue_joint": "E_cue", "late_joint": "E_late",
                       "spectral_joint": "E_spectral"}.get(arm, "E_action")
                block = expected[key]
                if arm == "deranged_joint":
                    block = tuple(value[[-1, *range(len(value) - 1)]] for value in block)
                wanted = tuple(np.concatenate((p, e), axis=1) for p, e in zip(expected["P"], block))
            np.testing.assert_allclose(fit, wanted[0])
            np.testing.assert_allclose(evaluation, wanted[1])
            return np.full((len(evaluation), 4), .25)

        with mock.patch.object(temporal, "_ridge_probabilities", new=inspect_fit):
            result = temporal._predict_arms(features, labels, null, train, validation, None)
        self.assertEqual(calls, 11)
        self.assertEqual(set(result), set(temporal.LEARNED_ARMS))

    def test_complete_nested_null_isolation_counts_coverage_and_no_prediction_scoring(self):
        import numpy as np
        nominal = np.arange(40)
        original = np.delete(nominal, [9, 20])
        labels = original % 4
        _, plans, _ = old._nested_plan(labels, original, old.SEED, nominal)
        fit_calls = temperature_calls = checks = 0
        original_temperature = temporal.fit_inverse_temperature

        def fit(fit_features, fit_labels, evaluation):
            nonlocal fit_calls
            fold, within_fold = divmod(fit_calls, 44)
            fit_index, arm_index = divmod(within_fold, 11)
            train, validation, inner, null = plans[fold]
            current_train, current_validation = inner[fit_index] if fit_index < 3 else (train, validation)
            arm = temporal.LEARNED_ARMS[arm_index]
            expected = null if arm in temporal.SHUFFLED_ARMS else labels
            np.testing.assert_array_equal(fit_labels, expected[current_train])
            self.assertEqual(len(fit_features), len(current_train))
            self.assertEqual(len(evaluation), len(current_validation))
            self.assertFalse(np.intersect1d(train if fit_index == 3 else current_train, validation).size)
            fit_calls += 1
            return np.full((len(evaluation), 4), .25)

        def calibrate(probabilities, calibration_labels):
            nonlocal temperature_calls
            fold, arm_index = divmod(temperature_calls, 11)
            train, _, _, null = plans[fold]
            arm = temporal.LEARNED_ARMS[arm_index]
            np.testing.assert_array_equal(calibration_labels,
                                          (null if arm in temporal.SHUFFLED_ARMS else labels)[train])
            self.assertTrue(np.isfinite(probabilities).all())
            temperature_calls += 1
            return original_temperature(probabilities, calibration_labels)

        def check():
            nonlocal checks
            checks += 1

        with mock.patch.object(temporal, "_ridge_probabilities", new=fit), \
                mock.patch.object(temporal, "fit_inverse_temperature", new=calibrate), \
                mock.patch.object(temporal, "_metrics", new=lambda *args: self.fail("No outer scoring")):
            result = temporal.run_condition(self.features(len(labels)), labels, original,
                                            nominal_trial_indices=nominal, check=check)
        self.assertEqual((fit_calls, temperature_calls, checks), (176, 44, 220))
        self.assertEqual(set(result["predictions"]), set(temporal.ARMS))
        self.assertEqual(set(result["uncalibrated"]), set(temporal.LEARNED_ARMS))
        for values in (*result["predictions"].values(), *result["uncalibrated"].values()):
            self.assertEqual(values.shape, (38, 4))
            np.testing.assert_allclose(values.sum(axis=1), 1)
        diagnostics = result["fit_diagnostics"]
        self.assertEqual((diagnostics["ridge_fits"], diagnostics["temperature_fits"]), (176, 44))
        self.assertEqual(diagnostics["excluded_trials"], 2)
        self.assertEqual(diagnostics["peripheral_timing_features"], 440)
        self.assertFalse(diagnostics["outer_scores_computed"])
        self.assertEqual(diagnostics["argmax_changes"], 0)
        json.dumps(diagnostics, allow_nan=False)

    def test_nominal_split_reuse_and_previous_defaults_unchanged(self):
        import numpy as np
        nominal = np.arange(40, 120)
        original = np.delete(nominal, [19, 39])
        labels = original % 4
        preflight = temporal.preflight_condition(labels, original, nominal_trial_indices=nominal)
        self.assertEqual(preflight, old.preflight_condition(labels, original, nominal_trial_indices=nominal))
        self.assertEqual((len(old.ARMS), len(old.LEARNED_ARMS)), (8, 6))
        self.assertEqual(set(old.preflight_condition(nominal % 4, nominal)), {"n_trials", "seed_block", "folds"})
        self.assertEqual(old.window_features(np.zeros((128, 384)), np.zeros((8, 384)))["E"].shape, (640,))

    def test_invalid_feature_roster_and_missing_nominal_indices_fail_before_fit(self):
        import numpy as np
        original = np.arange(40)
        labels = original % 4
        features = self.features()
        malformed = ({**features, "extra": features["P"]},
                     {key: value for key, value in features.items() if key != "E_spectral"},
                     {**features, "P": np.zeros((40, 88))},
                     {**features, "E_action": np.zeros((40, 640))},
                     {**features, "E_spectral": np.full((40, 640), np.nan)})
        with mock.patch.object(temporal, "_ridge_probabilities", new=lambda *args: self.fail("No fit")):
            for wrong in malformed:
                with self.subTest(keys=list(wrong)), self.assertRaises(ValueError):
                    temporal.run_condition(wrong, labels, original, nominal_trial_indices=original)
            with self.assertRaises(ValueError):
                temporal.run_condition(features, labels, original)
            with self.assertRaises(ValueError):
                temporal.preflight_condition(labels, original)

    def test_all_aggregate_metrics_and_gain_directions(self):
        import numpy as np
        labels = np.arange(40) % 4
        predictions = {}
        confidence = {"joint": .6, "P": .5, "spectral_joint": .55, "action_eeg": .65, "cue_eeg": .7}
        for arm in temporal.ARMS:
            target = confidence.get(arm, .25)
            values = np.full((len(labels), 4), (1 - target) / 3)
            values[np.arange(len(labels)), labels] = target
            predictions[arm] = values
        raw = {arm: predictions[arm].copy() for arm in temporal.LEARNED_ARMS}
        score = temporal.score_condition({"predictions": predictions, "uncalibrated": raw}, labels)
        self.assertEqual((len(score["metrics"]), len(score["uncalibrated_diagnostic"])), (13, 11))
        for arm in temporal.ARMS:
            self.assertEqual(score["metrics"][arm], old._metrics(predictions[arm], labels))
        self.assertEqual(set(score["primary_joint_nll_gains"]), set(temporal.PRIMARY_COMPARATORS))
        for arm, gain in score["primary_joint_nll_gains"].items():
            self.assertAlmostEqual(gain, np.log(.6 / confidence.get(arm, .25)))
        for arm in ("action_eeg", "cue_eeg"):
            self.assertEqual(set(score["eeg_sensitivity_nll_gains"][arm]),
                             {f"{arm}_shuffled", "uniform", "training_prior"})
            for gain in score["eeg_sensitivity_nll_gains"][arm].values():
                self.assertAlmostEqual(gain, np.log(confidence[arm] / .25))
        self.assertFalse(score["eeg_sensitivity_establishes_neural_origin"])
        json.dumps(score, allow_nan=False)
        with self.assertRaises(ValueError):
            temporal.score_condition({"predictions": {k: v for k, v in predictions.items() if k != "cue_eeg"},
                                      "uncalibrated": raw}, labels)
        with self.assertRaises(ValueError):
            temporal.score_condition({"predictions": predictions,
                                      "uncalibrated": {**raw, "joint": np.roll(raw["joint"], 1, axis=1)}}, labels)

    def test_real_ridge_and_temperature_on_generated_4096_column_arrays(self):
        import numpy as np
        rng = np.random.default_rng(8)
        labels = np.arange(16) % 4
        features = rng.normal(size=(16, 4096))
        train, evaluation = old._standardized_block(features[:12], features[12:])
        raw = temporal._ridge_probabilities(train, labels[:12], evaluation)
        self.assertEqual(raw.shape, (4, 4))
        calibration = temporal.fit_inverse_temperature(raw, labels[12:])
        calibrated = temporal.temperature_probabilities(raw, calibration["inverse_temperature"])
        np.testing.assert_array_equal(calibrated.argmax(axis=1), raw.argmax(axis=1))
        self.assertLessEqual(calibration["class_macro_nll_after"], calibration["class_macro_nll_before"] + 1e-12)


if __name__ == "__main__":
    unittest.main()
