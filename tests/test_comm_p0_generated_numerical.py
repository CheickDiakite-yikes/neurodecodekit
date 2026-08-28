from __future__ import annotations

import os
import unittest
from dataclasses import replace
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_numerical as numerical


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    numerical.numerical_dependencies_available(),
    "optional COMM-P0-G numerical dependencies are unavailable",
)
class CommP0GeneratedNumericalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for name in numerical.THREAD_ENVIRONMENT:
            os.environ[name] = "1"
        cls.contract = core.load_contract(ROOT)
        vault = core.GeneratedTargetVault(b"n" * 32)
        all_rows = core.generate_trial_plan(cls.contract, vault)
        keep = {
            "P0-1-01",
            "P0-1-02",
            "P0-1-03",
            "P0-1-04",
            "P0-2-01",
            "P0-2-02",
            "P0-2-03",
            "P0-2-04",
        }
        # Four participants per cohort is the smallest useful development schedule.
        cls.rows = tuple(row for row in all_rows if row.participant_id in keep)

    def test_feature_fixture_is_deterministic_target_free_and_positive_only_in_central(
        self,
    ) -> None:
        first = numerical.generate_feature_rows(self.rows)
        second = numerical.generate_feature_rows(self.rows)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 8 * 128)
        for row in first:
            core.assert_target_free(
                {
                    "item_id": row.item_id,
                    "participant_id": row.participant_id,
                    "endpoint": row.endpoint,
                    "phase": row.phase,
                    "central": row.central,
                    "posterior": row.posterior,
                    "eog": row.eog,
                    "oral_emg": row.oral_emg,
                    "microphone": row.microphone,
                }
            )

    def test_reduced_schedule_has_exact_formula_and_deterministic_predictions(self) -> None:
        first, first_ledger = numerical.run_target_blind_schedule(
            self.rows, self.contract, exact_registered_schedule=False
        )
        second, second_ledger = numerical.run_target_blind_schedule(
            self.rows, self.contract, exact_registered_schedule=False
        )
        folds = 8
        self.assertEqual(first_ledger.prior_fits, folds)
        self.assertEqual(first_ledger.residualizer_fits, folds * 2)
        self.assertEqual(first_ledger.classifier_fits, folds * 15)
        self.assertEqual(first_ledger.temperature_calibration_fits, folds * 15)
        self.assertEqual(first_ledger.prediction_sets, folds * 17 * 2)
        self.assertEqual(first_ledger.prediction_rows, folds * 17 * 128)
        self.assertEqual(first_ledger, second_ledger)
        self.assertEqual(
            numerical.prediction_stream_sha256(first),
            numerical.prediction_stream_sha256(second),
        )
        self.assertEqual(len(first), folds * 17 * 128)
        self.assertEqual(first, second)
        self.assertEqual(first_ledger.target_deliveries, 0)
        self.assertEqual(first_ledger.scores, 0)

    def test_prediction_records_are_target_free_finite_and_normalized(self) -> None:
        predictions, _ = numerical.run_target_blind_schedule(
            self.rows, self.contract, exact_registered_schedule=False
        )
        for prediction in predictions:
            record = prediction.public_record()
            core.assert_target_free(record)
            self.assertIn(record["phase"], {"shadow", "live"})
            self.assertAlmostEqual(sum(record["probabilities"]), 1.0, places=12)
            self.assertEqual(len(record["probabilities"]), 4)

    def test_thread_environment_is_required(self) -> None:
        previous = os.environ.pop("OMP_NUM_THREADS", None)
        try:
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "total_permission_or_free_space_floor_breach",
            ):
                numerical.assert_single_thread_environment()
        finally:
            if previous is not None:
                os.environ["OMP_NUM_THREADS"] = previous

    def test_schedule_rejects_condition_drift(self) -> None:
        drifted = dict(self.contract)
        drifted["conditions"] = list(self.contract["conditions"][:-1])
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "required_control_condition_missing_duplicated_or_substituted",
        ):
            numerical.run_target_blind_schedule(self.rows, drifted, exact_registered_schedule=False)

    def test_feature_rows_do_not_accept_target_bearing_extension(self) -> None:
        active_trial = next(row for row in self.rows if row.endpoint in core.ENDPOINTS)
        row = numerical.generate_feature_rows((active_trial,))[0]
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "recursive_target_label_reference_key_leakage",
        ):
            core.assert_target_free({"row": replace(row), "target": 1})


if __name__ == "__main__":
    unittest.main()
