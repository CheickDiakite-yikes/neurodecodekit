import math
import unittest


class BlankCalibrationTests(unittest.TestCase):
    def test_intercept_matches_analytic_constant_margin_solution_and_dense_oracle(self):
        from neurodecodekit.evaluation.blank_calibration import (
            fit_blank_intercept,
        )

        margins = [0.0] * 10
        labels = [1, 1, 1, 1, 0, 0, 0, 0, 0, 0]
        fit = fit_blank_intercept(margins, labels)
        analytic = math.log(0.4 / 0.6)

        def independent_nll(intercept):
            losses = [
                math.log1p(math.exp(-intercept)) if label else math.log1p(math.exp(intercept))
                for label in labels
            ]
            return sum(losses) / len(losses)

        dense = min(
            (index / 10000 for index in range(-80000, 80001)),
            key=independent_nll,
        )

        self.assertAlmostEqual(fit.intercept, analytic, places=12)
        self.assertAlmostEqual(fit.intercept, dense, delta=0.0001)
        self.assertEqual(fit.iterations, 80)
        self.assertLess(abs(fit.final_gradient), 1e-14)
        self.assertLess(
            fit.train_metrics_after["negative_log_likelihood"],
            fit.train_metrics_before["negative_log_likelihood"],
        )

    def test_logits_margin_application_and_metrics_are_explicit(self):
        from neurodecodekit.evaluation.blank_calibration import (
            apply_blank_intercept,
            blank_binary_metrics,
            blank_margins_from_logits,
            registered_blank_intercept_config,
        )

        logits = [(1.0, 0.0, -1.0), (-1.0, 1.0, 0.0)]
        margins = blank_margins_from_logits(logits)
        adjusted = apply_blank_intercept(logits[0], intercept=0.75)
        metrics = blank_binary_metrics(margins, [1, 0], intercept=0.0)

        self.assertEqual(adjusted, (1.75, 0.0, -1.0))
        self.assertEqual(metrics["frames"], 2)
        self.assertEqual(metrics["blank_frames"], 1)
        self.assertEqual(len(metrics["calibration_bins"]), 10)
        self.assertEqual(
            registered_blank_intercept_config().config_sha256,
            "43de56b1d275c0fd5b08a92d9dabc6893f7fe7ee49e02195623f6d61caa57e47",
        )

    def test_malformed_inputs_and_unbracketed_root_fail_closed(self):
        from neurodecodekit.evaluation.blank_calibration import (
            BlankInterceptConfig,
            apply_blank_intercept,
            blank_margins_from_logits,
            fit_blank_intercept,
        )

        with self.assertRaisesRegex(ValueError, "finite"):
            blank_margins_from_logits([(0.0, float("nan"))])
        with self.assertRaisesRegex(ValueError, "both blank and nonblank"):
            fit_blank_intercept([0.0, 1.0], [1, 1])
        with self.assertRaisesRegex(ValueError, "not bracketed"):
            fit_blank_intercept([100.0, 100.0], [1, 0])
        with self.assertRaisesRegex(ValueError, "preregistration"):
            fit_blank_intercept(
                [0.0, 0.0],
                [1, 0],
                config=BlankInterceptConfig(fit_iterations=79),
            )
        with self.assertRaisesRegex(ValueError, "finite"):
            apply_blank_intercept([0.0, 1.0], intercept=float("inf"))

    def test_paired_sequence_audit_and_bootstrap_are_deterministic(self):
        from neurodecodekit.evaluation.blank_calibration import (
            paired_metric_bootstrap,
            paired_sequence_change_metrics,
        )

        targets = [(1, 2), (2, 2, 1), (3, 1)]
        unmodified = [(1, 2, 4), (2, 2, 1, 3), (3, 1)]
        calibrated = [(1, 2), (2, 2, 1), (3, 1)]
        audit = paired_sequence_change_metrics(targets, unmodified, calibrated)
        first = paired_metric_bootstrap(
            targets, unmodified, calibrated, resamples=200, seed=2354
        )
        second = paired_metric_bootstrap(
            targets, unmodified, calibrated, resamples=200, seed=2354
        )

        self.assertEqual(audit["corrected_items"], 2)
        self.assertEqual(audit["new_error_items"], 0)
        self.assertEqual(audit["items_with_worse_cer"], 0)
        self.assertEqual(audit["tail_inserted_token_reduction"], 2)
        self.assertEqual(first, second)
        self.assertGreaterEqual(first["exact_accuracy_gain_interval_95"][0], 0)
        self.assertGreaterEqual(first["cer_reduction_interval_95"][0], 0)


if __name__ == "__main__":
    unittest.main()
