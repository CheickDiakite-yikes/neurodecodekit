"""Generated-only nominal-slot split checks; no recordings or real model fits."""

import importlib.util
import json
import unittest
from unittest import mock

from neurodecodekit.experiments import inner_speech as inner


@unittest.skipUnless(importlib.util.find_spec("numpy"), "optional NumPy")
class ObservedAnchorSplitTests(unittest.TestCase):
    def test_intact_nominal_mode_has_identical_legacy_splits_and_null_permutations(self):
        import numpy as np
        for n in (40, 80, 120):
            original, labels = np.arange(n), np.arange(n) % 4
            strict = inner._nested_plan(labels, original, inner.SEED)
            observed = inner._nested_plan(labels, original, inner.SEED, original)
            for old, new in zip(strict[1], observed[1]):
                for index in (0, 1, 3):
                    np.testing.assert_array_equal(old[index], new[index])
                for old_inner, new_inner in zip(old[2], new[2]):
                    for left, right in zip(old_inner, new_inner):
                        np.testing.assert_array_equal(left, right)
            for old, new in zip(strict[2], observed[2]):
                self.assertEqual(old["original_split_sha256"], new["original_split_sha256"])
                self.assertEqual(new["nominal_split_sha256"], new["original_split_sha256"])
                self.assertEqual(new["excluded_validation_trials"], 0)
                self.assertEqual([r["original_split_sha256"] for r in old["inner_folds"]],
                                 [r["original_split_sha256"] for r in new["inner_folds"]])
            self.assertEqual(set(inner.preflight_condition(labels, original)),
                             {"n_trials", "seed_block", "folds"})

    def test_gaps_preserve_nominal_blocks_and_both_original_embargo_levels(self):
        import numpy as np
        nominal = np.arange(40, 120)
        original = nominal[~np.isin(nominal, [42, 58, 59, 78, 79, 98, 118])]
        labels = original % 4
        _, plans, records = inner._nested_plan(labels, original, inner.SEED, nominal)
        nominal_blocks = np.array_split(nominal, 4)
        coverage = np.zeros(len(original), dtype=int)

        def embargo(pool, held):
            return [slot for slot in pool if all(abs(slot - test) > 1 for test in held)]

        for fold, (train, validation, nested, null) in enumerate(plans):
            planned_train = embargo(nominal, nominal_blocks[fold])
            expected_train = sorted(set(planned_train) & set(original))
            expected_validation = sorted(set(nominal_blocks[fold]) & set(original))
            np.testing.assert_array_equal(original[train], expected_train)
            np.testing.assert_array_equal(original[validation], expected_validation)
            coverage[validation] += 1
            np.testing.assert_array_equal(np.sort(null[train]), np.sort(labels[train]))
            self.assertTrue((null[validation] == -1).all())
            inner_coverage = np.zeros(len(original), dtype=int)
            for other, (inner_train, inner_validation) in zip(
                    [index for index in range(4) if index != fold], nested):
                planned_validation = sorted(set(planned_train) & set(nominal_blocks[other]))
                expected = sorted(set(embargo(planned_train, planned_validation)) & set(original))
                np.testing.assert_array_equal(original[inner_train], expected)
                np.testing.assert_array_equal(original[inner_validation],
                                              sorted(set(planned_validation) & set(original)))
                inner_coverage[inner_validation] += 1
            np.testing.assert_array_equal(inner_coverage[train], np.ones(len(train)))
            self.assertEqual(inner_coverage[validation].sum(), 0)
        np.testing.assert_array_equal(coverage, np.ones(len(original)))
        self.assertNotIn(60, original[plans[0][0]])  # omitted validation59 does not reclaim neighbour60
        self.assertNotIn(80, original[plans[0][2][0][0]])  # likewise inner validation79 / neighbour80
        self.assertIn(81, original[plans[0][2][0][0]])
        self.assertEqual(records[0]["nominal_validation_trials"], 20)
        self.assertEqual(records[0]["validation_trials"], 17)
        self.assertEqual(records[0]["excluded_validation_trials"], 3)
        changed = inner._nested_plan((labels + 1) % 4, original, inner.SEED, nominal)[2]
        self.assertEqual([r["original_split_sha256"] for r in records],
                         [r["original_split_sha256"] for r in changed])

    def test_embargo_never_uses_compressed_condition_row_neighbours(self):
        import numpy as np
        nominal = np.arange(40) * 3
        original = nominal[nominal != 27]
        _, plans, _ = inner._nested_plan(original % 4, original, inner.SEED, nominal)
        np.testing.assert_array_equal(original[plans[0][1]], np.arange(9) * 3)
        self.assertIn(30, original[plans[0][0]])
        self.assertEqual(len(plans[0][0]), 30)

    def test_invalid_nominal_or_retained_metadata_refuses_without_a_fit(self):
        import numpy as np
        original = np.arange(40)
        nominal_cases = (original.astype(float), original.reshape(2, 20), original[:-1],
                         original[::-1], np.r_[original[:-1], 38], original - 1,
                         np.r_[original[:-1], 200])
        with mock.patch.object(inner, "_ridge_probabilities", new=lambda *args: self.fail("No fit")):
            for nominal in nominal_cases:
                with self.subTest(nominal_shape=nominal.shape), self.assertRaises(ValueError):
                    inner.preflight_condition(original % 4, original, nominal_trial_indices=nominal)
            for retained in (original[8:], np.arange(1, 41), np.r_[0, original[:-1]]):
                with self.subTest(retained=retained.shape), self.assertRaises(ValueError):
                    inner.preflight_condition(retained % 4, retained, nominal_trial_indices=original)
            with self.assertRaises(ValueError):
                inner.preflight_condition(original % 3, original, nominal_trial_indices=original)
            with self.assertRaises(ValueError):
                inner.preflight_condition(original[:-1] % 4, original[:-1])

    def test_retention_diagnostics_are_counts_and_hashes_not_slot_rows(self):
        import numpy as np
        nominal = np.arange(80)
        original = np.delete(nominal, [1, 19, 22, 39, 44, 60, 77])
        result = inner.preflight_condition(original % 4, original, nominal_trial_indices=nominal)
        self.assertEqual((result["nominal_trials"], result["retained_trials"], result["excluded_trials"]),
                         (80, 73, 7))
        self.assertEqual(result["n_trials"], 73)
        for name in ("nominal_indices_sha256", "retained_indices_sha256"):
            self.assertRegex(result[name], "^[0-9a-f]{64}$")
        for fold in result["folds"]:
            for record in (fold, *fold["inner_folds"]):
                self.assertNotIn("train", record)
                self.assertNotIn("validation", record)
                self.assertEqual(record["nominal_training_trials"] - record["training_trials"],
                                 record["excluded_training_trials"])
        json.dumps(result, allow_nan=False)

    def test_observed_mode_requires_p88_and_keeps_all_arms_and_fit_counts(self):
        import numpy as np
        nominal = np.arange(40)
        original = np.delete(nominal, [2, 9, 19])
        labels = original % 4
        features = {"P": np.zeros((len(labels), 88)),
                    **{name: np.zeros((len(labels), 640)) for name in ("E_action", "E_cue", "E_late")}}
        fits = 0

        def uniform(fit, fit_labels, evaluation):
            nonlocal fits
            fits += 1
            self.assertIn(fit.shape[1], (88, 728))
            self.assertEqual(len(fit), len(fit_labels))
            return np.full((len(evaluation), 4), .25)

        with mock.patch.object(inner, "_ridge_probabilities", new=uniform), \
                mock.patch.object(inner, "_metrics", new=lambda *args: self.fail("No outer scoring")):
            result = inner.run_condition(features, labels, original, observed_anchors=True,
                                         nominal_trial_indices=nominal)
        self.assertEqual(fits, 96)
        self.assertEqual(set(result["predictions"]), set(inner.ARMS))
        for values in result["predictions"].values():
            self.assertEqual(values.shape, (37, 4))
            self.assertTrue(np.isfinite(values).all())
            np.testing.assert_allclose(values.sum(axis=1), 1)
        diagnostics = result["fit_diagnostics"]
        self.assertEqual(diagnostics["temperature_fits"], 24)
        self.assertEqual(diagnostics["peripheral_timing_features"], 88)
        self.assertTrue(diagnostics["observed_anchor_amendment"])
        self.assertFalse(diagnostics["missing_timing_amendment"])
        self.assertEqual(diagnostics["excluded_trials"], 3)
        for options in ({"observed_anchors": True},
                        {"observed_anchors": True, "missing_timing": True, "nominal_trial_indices": nominal},
                        {"observed_anchors": 1, "nominal_trial_indices": nominal},
                        {"nominal_trial_indices": nominal}):
            with self.subTest(options=list(options)), self.assertRaises(ValueError):
                inner.run_condition(features, labels, original, **options)
        for width in (85, 87):
            with self.subTest(width=width), self.assertRaises(ValueError):
                inner.run_condition({**features, "P": np.zeros((37, width))}, labels, original,
                                    observed_anchors=True, nominal_trial_indices=nominal)


if __name__ == "__main__":
    unittest.main()
