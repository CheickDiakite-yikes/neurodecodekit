import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/physionet_low_frequency_cohort_confirmation_result.v0.json"
)
CONTRACT_PATH = (
    ROOT / "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
FREEZE_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_prediction_freeze.v0.json"
)
DOC_PATH = ROOT / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_RESULT.md"
EXPECTED_RESULT_SHA256 = "d6cda8b4ce5f6da7add4a78ac8b1e74587cd8ab8eacf0dce8b806c076e85699a"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def metric(self, condition_id):
        return self.result["condition_metrics"][condition_id]

    def test_result_is_hash_locked_to_green_freeze(self):
        self.assertEqual(sha256(RESULT_PATH), EXPECTED_RESULT_SHA256)
        self.assertEqual(
            self.result["freeze_commit"],
            "8cd45d74dfa3517ae53c1427a0eb06e27ad3c870",
        )
        self.assertEqual(self.result["freeze_ci_run_id"], 31360781199)
        self.assertEqual(self.result["base_python_job_id"], 93369101655)
        self.assertEqual(self.result["optional_neuro_job_id"], 93369101696)
        self.assertEqual(sha256(FREEZE_PATH), "6a546ca32a92b35c9c3448cecb5831f926d02f519a563d2ad803944c8d1f487a")

    def test_one_shot_scoring_is_consumed_without_post_target_update(self):
        self.assertEqual(self.result["status"], "scored_once_frozen_router_applied")
        self.assertEqual(self.result["final_target_deliveries"], 1)
        self.assertEqual(self.result["scoring_events"], 1)
        self.assertEqual(self.result["post_target_updates"], 0)
        self.assertFalse(self.result["individual_participant_metrics_published"])
        self.assertEqual(self.result["public_result_bytes"], RESULT_PATH.stat().st_size)

    def test_H1_execution_confirmation_passes_every_frozen_gate(self):
        metric = self.metric("execution_native_primary")
        prior = self.metric("execution_no_signal_prior")
        gate = self.contract["frozen_gates"]["H1_execution_native_cohort_confirmation"]
        self.assertTrue(self.result["H1_execution_native_passed"])
        self.assertEqual(metric["correct_count"], 123)
        self.assertGreaterEqual(metric["correct_count"], gate["minimum_correct_count"])
        self.assertGreaterEqual(metric["pooled_balanced_accuracy"], gate["minimum_pooled_balanced_accuracy"])
        self.assertGreaterEqual(metric["macro_participant_balanced_accuracy"], gate["minimum_macro_participant_balanced_accuracy"])
        self.assertGreaterEqual(metric["participants_strictly_above_chance"], gate["minimum_participants_strictly_above_0_5_balanced_accuracy"])
        self.assertLessEqual(metric["exact_one_sided_participant_sign_flip_p"], gate["maximum_exact_one_sided_participant_sign_flip_p"])
        self.assertGreaterEqual(metric["pooled_balanced_accuracy"] - prior["pooled_balanced_accuracy"], gate["minimum_pooled_margin_over_execution_no_signal"])
        self.assertGreaterEqual(metric["macro_participant_balanced_accuracy"] - prior["macro_participant_balanced_accuracy"], gate["minimum_macro_margin_over_execution_no_signal"])

    def test_H2_imagery_and_bidirectional_transfer_are_positive(self):
        metric = self.metric("imagery_native")
        gate = self.contract["frozen_gates"]["H2_imagery_native_task_mode_robustness"]
        self.assertTrue(self.result["H2_imagery_native_passed"])
        self.assertEqual(metric["correct_count"], 131)
        self.assertGreaterEqual(metric["pooled_balanced_accuracy"], gate["minimum_pooled_balanced_accuracy"])
        self.assertGreaterEqual(metric["macro_participant_balanced_accuracy"], gate["minimum_macro_participant_balanced_accuracy"])
        self.assertEqual(metric["participants_strictly_above_chance"], 12)
        self.assertLessEqual(metric["exact_one_sided_participant_sign_flip_p"], gate["maximum_exact_one_sided_participant_sign_flip_p"])
        self.assertGreater(self.metric("execution_to_imagery")["pooled_balanced_accuracy"], 0.69)
        self.assertGreater(self.metric("imagery_to_execution")["pooled_balanced_accuracy"], 0.69)

    def test_H3_and_motor_physiology_fail_without_route_inflation(self):
        self.assertFalse(self.result["H3_motor_compatible_localization_passed"])
        self.assertLess(
            self.result["localization"]["central_minus_strongest_proxy_pooled_margin"],
            0.0,
        )
        self.assertGreater(
            self.result["localization"]["exact_paired_participant_sign_flip_p"],
            0.05,
        )
        self.assertFalse(self.result["physiology"]["passed"])
        self.assertEqual(self.result["physiology"]["participants_in_registered_direction"], 5)
        self.assertEqual(self.result["verdict"], "WO9R-R3")

    def test_cue_and_frontal_controls_prevent_brain_specific_claim(self):
        self.assertFalse(self.result["mandatory_controls_passed"])
        controls = self.result["control_components"]
        for condition_id in (
            "execution_early_cue",
            "execution_frontal_proxy",
            "execution_frontal_asymmetry",
        ):
            self.assertFalse(controls[condition_id])
            self.assertGreater(self.metric(condition_id)["pooled_balanced_accuracy"], 0.6)
        self.assertTrue(controls["execution_pre_cue"])
        self.assertTrue(controls["execution_timing_only"])
        self.assertIn("Brain-specific origin", self.result["claim_boundary"]["not_established"])

    def test_closeout_states_positive_result_and_limit_separately(self):
        document = " ".join(DOC_PATH.read_text(encoding="utf-8").split())
        self.assertIn("Scientific result established", document)
        self.assertIn("held-out left/right task information", document)
        self.assertIn("motor-compatible localization", document)
        self.assertIn("were not established", document)
        self.assertIn("Do not rerun it", document)


if __name__ == "__main__":
    unittest.main()
