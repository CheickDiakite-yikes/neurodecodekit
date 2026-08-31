from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path

from neurodecodekit.evaluation.public_motor_cross_cohort_synthesis import build_result


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/public_motor_cross_cohort_synthesis_result.v0.json"
DOCUMENT = ROOT / "docs/PUBLIC_MOTOR_CROSS_COHORT_SYNTHESIS_RESULT.md"


class PublicMotorCrossCohortSynthesisResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_registry_exactly_replays_from_hash_bound_public_aggregates(self) -> None:
        self.assertEqual(build_result(ROOT), self.result)
        for identity in self.result["source_identities"].values():
            payload = (ROOT / identity["path"]).read_bytes()
            self.assertEqual(len(payload), identity["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), identity["sha256"])

    def test_low_frequency_task_information_replication_arithmetic(self) -> None:
        result = self.result["replicated_low_frequency_task_information"]
        self.assertEqual(result["participants"], 15)
        self.assertEqual(result["correct_events"], 159)
        self.assertEqual(result["held_out_execution_events"], 225)
        self.assertAlmostEqual(result["descriptive_event_accuracy"], 159 / 225)
        self.assertAlmostEqual(
            result["participant_count_weighted_mean_macro_balanced_accuracy"],
            (3 * 0.8005952380952381 + 12 * 0.6822916666666666) / 15,
        )
        product = 0.00018310546875 * 0.0029296875
        self.assertAlmostEqual(result["retrospective_Fisher_statistic"], -2 * math.log(product))
        self.assertAlmostEqual(
            result["retrospective_Fisher_nominal_p"],
            product * (1 - math.log(product)),
        )
        self.assertFalse(result["Fisher_value_is_confirmatory"])
        self.assertEqual(result["confirmatory_p_value"], 0.0029296875)

    def test_spatial_result_is_unanimously_negative_but_not_pooled(self) -> None:
        result = self.result["cross_cohort_spatial_control_convergence"]
        self.assertEqual(
            [cohort["candidate_id"] for cohort in result["cohorts"]],
            [
                "central_sensorimotor_channel_model",
                "execution_central_sensorimotor",
                "selected_E",
            ],
        )
        margins = [
            cohort["candidate_minus_control_macro_balanced_accuracy"]
            for cohort in result["cohorts"]
        ]
        self.assertEqual(len(margins), 3)
        self.assertTrue(all(margin < 0 for margin in margins))
        self.assertEqual(result["cohorts_with_negative_candidate_minus_control_margin"], 3)
        self.assertAlmostEqual(
            result["nominal_all_negative_probability_under_independent_fair_signs"],
            0.125,
        )
        self.assertFalse(result["sign_test_valid"])
        self.assertAlmostEqual(
            result["participant_count_weighted_descriptive_margin"],
            sum(
                cohort["participants"]
                * cohort["candidate_minus_control_macro_balanced_accuracy"]
                for cohort in result["cohorts"]
            )
            / 24,
        )
        self.assertFalse(result["formal_pooled_effect_valid"])

    def test_independence_and_active_claim_limits_are_explicit(self) -> None:
        independence = self.result["cohort_independence"]
        self.assertEqual(independence["EEGMMIDB_participant_overlap"], [])
        self.assertTrue(independence["EEGMMIDB_participant_disjoint_recordings"])
        self.assertTrue(independence["BNCI_is_distinct_dataset"])
        self.assertEqual(independence["EEGMMIDB_dataset_id"], "eegmmidb")
        self.assertEqual(independence["EEGMMIDB_version"], "1.0.0")
        self.assertEqual(independence["BNCI_official_dataset_id"], "BNCI_001_2014")
        self.assertEqual(independence["BNCI_NEMAR_dataset_id"], "nm000139")
        self.assertFalse(
            independence["BNCI_biological_person_overlap_with_EEGMMIDB_known"]
        )
        self.assertFalse(independence["independent_team_replication"])
        self.assertFalse(independence["method_selection_independent_of_pilot_outcome"])
        peripheral = self.result["peripheral_attribution"]
        self.assertEqual(peripheral["cohorts_with_recorded_task_relevant_EMG"], 0)
        self.assertFalse(peripheral["joint_EOG_EMG_attribution_tested"])
        conclusion = self.result["scientific_conclusion"]
        self.assertFalse(conclusion["active_FMSR1_conjunction_established"])
        self.assertFalse(conclusion["brain_specific_motor_signal_established"])

    def test_synthesis_did_not_reopen_or_rescore_consumed_data(self) -> None:
        counters = self.result["operation_counters"]
        self.assertEqual(counters["tracked_public_JSON_files_read"], 6)
        self.assertEqual(counters["tracked_public_JSON_content_open_events"], 6)
        self.assertEqual(counters["tracked_public_result_JSON_files_read"], 3)
        self.assertEqual(
            counters["tracked_public_contract_or_identity_JSON_files_read"],
            3,
        )
        self.assertEqual(
            counters["tracked_public_JSON_bytes_read"],
            counters["tracked_public_result_JSON_bytes_read"]
            + counters["tracked_public_contract_or_identity_JSON_bytes_read"],
        )
        for key in (
            "raw_neural_payload_reads",
            "private_or_ignored_reads",
            "target_deliveries",
            "model_fits",
            "prediction_sets",
            "scores",
            "network_requests",
        ):
            self.assertEqual(counters[key], 0)

    def test_document_reports_result_and_limit_separately(self) -> None:
        document = " ".join(DOCUMENT.read_text(encoding="utf-8").split())
        self.assertIn("159 correct events", document)
        self.assertIn("p=0.00000828175", document)
        self.assertIn("not a new confirmatory p-value", document)
        self.assertIn("-0.025649", document)
        self.assertIn("remains untested", document)
        self.assertIn("unseen-person generalization", document)
        self.assertIn("biological-person overlap", document.lower())


if __name__ == "__main__":
    unittest.main()
