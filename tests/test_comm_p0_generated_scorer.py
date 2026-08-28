from __future__ import annotations

import os
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical
from neurodecodekit.experiments import comm_p0_generated_scorer as scorer


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    numerical.numerical_dependencies_available(),
    "optional COMM-P0-G numerical dependencies are unavailable",
)
class CommP0GeneratedScorerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for name in numerical.THREAD_ENVIRONMENT:
            os.environ[name] = "1"
        cls.contract = core.load_contract(ROOT)
        vault = core.GeneratedTargetVault(b"s" * 32)
        all_rows = core.generate_trial_plan(cls.contract, vault)
        keep = {f"P0-{cohort}-{index:02d}" for cohort in (1, 2) for index in range(1, 5)}
        cls.rows = tuple(row for row in all_rows if row.participant_id in keep)
        cls.predictions, cls.ledger = numerical.run_target_blind_schedule(
            cls.rows, cls.contract, exact_registered_schedule=False
        )
        cls.freeze = core.build_prediction_freeze(
            (prediction.public_record() for prediction in cls.predictions),
            expected_rows=len(cls.predictions),
            expected_sets=8 * 17 * 2,
        )

    def test_reduced_score_is_aggregate_target_free_and_keeps_cohorts_separate(self) -> None:
        result, live_digest = scorer.score_after_freeze(
            self.predictions,
            self.rows,
            self.freeze,
            self.contract,
            prediction_freeze_green=True,
            replication_artifact_freeze_green=True,
            exact_registered_cohort=False,
        )
        public = result.public_record()
        core.assert_target_free(public)
        self.assertEqual(result.target_deliveries, 2)
        self.assertEqual(result.scores, 2)
        self.assertEqual(result.post_target_updates, 0)
        self.assertEqual({row.cohort_id for row in result.cohorts}, set(core.COHORTS))
        self.assertEqual(len(live_digest), 64)
        for cohort in result.cohorts:
            free_choice = cohort.free_choice_shadow
            self.assertGreater(free_choice["mean_margin_nats_per_item"], 0.03)
            self.assertGreater(free_choice["mean_balanced_accuracy_margin"], 0.05)
            self.assertFalse(free_choice["passes"])
            self.assertTrue(free_choice["development_only_small_cohort"])
            prompted = cohort.prompted_shadow_directional
            self.assertIn("mean_balanced_accuracy_margin_over_noncue_controls", prompted)
            self.assertTrue(prompted["cue_only_reported_as_leakage_ceiling"])

    def test_live_score_reports_required_metrics_without_claiming_real_latency(self) -> None:
        result, _ = scorer.score_after_freeze(
            self.predictions,
            self.rows,
            self.freeze,
            self.contract,
            prediction_freeze_green=True,
            replication_artifact_freeze_green=True,
            exact_registered_cohort=False,
        )
        replication = next(
            row for row in result.cohorts if row.cohort_id == "independent_replication"
        )
        live = replication.live
        assert live is not None
        for field in (
            "balanced_accuracy",
            "log_loss",
            "false_activation_rate_on_null_trials",
            "missed_activation_rate",
            "abstention_fraction",
            "first_output_latency_median_seconds",
            "stable_commit_latency_median_seconds",
            "stable_commit_latency_p95_seconds",
            "capture_to_presentation_processing_overhead_p95_seconds",
            "dropped_or_invalid_chunk_fraction",
        ):
            self.assertIn(field, live)
        self.assertFalse(live["end_to_end_latency_measured"])
        self.assertTrue(live["generated_clock_latency_only"])

    def test_score_refuses_before_freeze_and_before_replication_binding(self) -> None:
        with self.assertRaisesRegex(core.CommP0GeneratedRefusal, "score_before_exact_green"):
            scorer.score_after_freeze(
                self.predictions,
                self.rows,
                self.freeze,
                self.contract,
                prediction_freeze_green=False,
                replication_artifact_freeze_green=True,
                exact_registered_cohort=False,
            )
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "replication_prediction_freeze_not_green_before_delivery",
        ):
            scorer.score_after_freeze(
                self.predictions,
                self.rows,
                self.freeze,
                self.contract,
                prediction_freeze_green=True,
                replication_artifact_freeze_green=False,
                exact_registered_cohort=False,
            )

    def test_prediction_tamper_or_duplicate_is_rejected(self) -> None:
        duplicate = self.predictions + (self.predictions[0],)
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal, "prediction_inventory_missing_or_duplicate"
        ):
            scorer.score_after_freeze(
                duplicate,
                self.rows,
                self.freeze,
                self.contract,
                prediction_freeze_green=True,
                replication_artifact_freeze_green=True,
                exact_registered_cohort=False,
            )


if __name__ == "__main__":
    unittest.main()
