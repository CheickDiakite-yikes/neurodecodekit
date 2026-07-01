import unittest

from neurodecodekit.models.prior_baseline import run_prior_baseline


class PriorBaselineTests(unittest.TestCase):
    def test_most_frequent_uses_training_distribution_with_first_seen_tie_break(self):
        result = run_prior_baseline(
            eval_targets=["A", "B", "C"],
            train_targets=["B", "A", "B", "A"],
        )

        self.assertEqual(result.predictions, ["B", "B", "B"])
        self.assertEqual(result.top_target, "B")
        self.assertEqual(result.top_count, 2)
        self.assertFalse(result.fit_on_eval_targets)
        self.assertEqual(result.counts, {"B": 2, "A": 2})
        self.assertIn("prior_baseline_no_neural_signal", result.warnings)

    def test_missing_train_targets_fits_eval_targets_with_warning(self):
        result = run_prior_baseline(eval_targets=["C", "C", "A"])

        self.assertEqual(result.predictions, ["C", "C", "C"])
        self.assertTrue(result.fit_on_eval_targets)
        self.assertIn("prior_fit_on_eval_targets_for_smoke_only", result.warnings)

    def test_sampling_strategies_are_deterministic_with_seed(self):
        first = run_prior_baseline(
            eval_targets=["A", "A", "A", "A", "A"],
            train_targets=["A", "B", "B"],
            strategy="frequency-sample",
            seed=13,
        )
        second = run_prior_baseline(
            eval_targets=["A", "A", "A", "A", "A"],
            train_targets=["A", "B", "B"],
            strategy="frequency-sample",
            seed=13,
        )
        uniform = run_prior_baseline(
            eval_targets=["A", "A", "A", "A", "A"],
            train_targets=["A", "B", "B"],
            strategy="uniform-random",
            seed=13,
        )

        self.assertEqual(first.predictions, second.predictions)
        self.assertEqual(len(first.predictions), 5)
        self.assertEqual(len(uniform.predictions), 5)
        self.assertTrue(set(first.predictions).issubset({"A", "B"}))
        self.assertTrue(set(uniform.predictions).issubset({"A", "B"}))

    def test_rejects_empty_eval_and_train_rows(self):
        with self.assertRaisesRegex(ValueError, "eval target"):
            run_prior_baseline(eval_targets=[])
        with self.assertRaisesRegex(ValueError, "train target"):
            run_prior_baseline(eval_targets=["A"], train_targets=[])

    def test_rejects_unknown_strategy(self):
        with self.assertRaisesRegex(ValueError, "unknown prior strategy"):
            run_prior_baseline(eval_targets=["A"], strategy="mystery")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
