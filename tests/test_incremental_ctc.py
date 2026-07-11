import importlib.util
import unittest


class IncrementalCTCMetricsTests(unittest.TestCase):
    def test_sequence_prior_metrics_and_repeated_pair_reconstruction(self):
        from neurodecodekit.evaluation.incremental_ctc import (
            fit_most_frequent_sequence_prior,
            sequence_metrics,
        )

        targets = [(1, 1, 2), (1, 1, 2), (2, 2, 1)]
        prior = fit_most_frequent_sequence_prior(targets)
        metrics = sequence_metrics(targets, [(1, 1, 2), (1, 2), (2, 2, 1)])

        self.assertEqual(prior, (1, 1, 2))
        self.assertEqual(metrics["edit_distance"], 1)
        self.assertAlmostEqual(metrics["corpus_cer"], 1 / 9)
        self.assertAlmostEqual(metrics["exact_sequence_accuracy"], 2 / 3)
        self.assertEqual(metrics["repeated_pair_count"], 3)
        self.assertEqual(metrics["repeated_pair_reconstructed"], 2)

    def test_partial_metrics_separate_first_correct_stable_and_final(self):
        from neurodecodekit.evaluation.incremental_ctc import partial_hypothesis_metrics

        trace = [(), (1,), (2,), (1,), (1, 2), (1, 2)]
        metrics = partial_hypothesis_metrics(
            trace,
            final_hypothesis=(1, 2),
            frame_end_samples=(16, 20, 24, 28, 32, 36),
            availability_samples=(16, 20, 24, 28, 36, 40),
            sampling_rate_hz=100.0,
            motif_end_samples=(24, 36),
            target=(1, 2),
        )

        first = metrics["symbol_timing"][0]
        second = metrics["symbol_timing"][1]
        self.assertEqual(first["first_correct_frame"], 1)
        self.assertEqual(first["stable_correct_frame"], 3)
        self.assertAlmostEqual(first["correction_delay_sec"], 0.08)
        self.assertEqual(second["stable_correct_frame"], 4)
        self.assertEqual(metrics["revision_events"], 2)
        self.assertEqual(metrics["finalization_frame"], 5)
        self.assertTrue(metrics["motif_timing_available"])

    @unittest.skipUnless(importlib.util.find_spec("numpy"), "NumPy not installed")
    def test_paired_bootstrap_reports_positive_cer_reduction(self):
        from neurodecodekit.evaluation.incremental_ctc import (
            paired_cer_reduction_bootstrap,
        )

        targets = [(1, 1, 2), (2, 3, 3), (3, 1, 1), (1, 2, 2)]
        learned = list(targets)
        control = [(1,), (1,), (1,), (1,)]
        report = paired_cer_reduction_bootstrap(
            targets, learned, control, resamples=200, seed=2322
        )

        self.assertGreater(report["confidence_interval_95"][0], 0)
        self.assertEqual(report["items"], 4)


if __name__ == "__main__":
    unittest.main()
