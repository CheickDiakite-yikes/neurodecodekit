import copy
import json
import unittest
from pathlib import Path

from neurodecodekit.research.task_identifiability import (
    TaskIdentifiabilityError,
    build_endpoint_schedule,
    exact_binomial_tail,
    run_task_identifiability_audit,
    sign_test_sensitivity,
    summarize_endpoint,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/communication_eeg_prospective_synchronized_cohort_contract.v0.json"
RESULT = ROOT / "registries/communication_task_identifiability_result.v0.json"


class CommunicationTaskIdentifiabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.result = run_task_identifiability_audit(cls.contract)
        cls.committed = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_committed_result_replays_exactly(self):
        self.assertEqual(self.committed["result"], self.result)

    def test_endpoint_schedules_are_exact_and_deterministic(self):
        for endpoint in ("prompted", "free_choice"):
            first = build_endpoint_schedule(endpoint)
            second = build_endpoint_schedule(endpoint)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 64)
            self.assertEqual({row.target for row in first}, {"yes", "no", "help", "stop"})

    def test_prompted_target_is_not_separable_from_cue_content(self):
        result = self.result["endpoint_results"]["prompted"]
        self.assertEqual(result["nuisance_bayes_accuracy"], 1.0)
        self.assertEqual(result["target_incremental_degrees_of_freedom"], 0)
        self.assertFalse(result["target_separable_from_scheduled_nuisance"])

    def test_free_choice_target_is_orthogonal_to_joint_scheduled_nuisance(self):
        result = self.result["endpoint_results"]["free_choice"]
        self.assertAlmostEqual(result["nuisance_mutual_information_nats"], 0.0)
        self.assertEqual(result["nuisance_bayes_accuracy"], 0.25)
        self.assertEqual(result["target_incremental_degrees_of_freedom"], 3)
        self.assertTrue(result["target_separable_from_scheduled_nuisance"])
        for information in result["pairwise_target_information_nats"].values():
            self.assertAlmostEqual(information, 0.0)

    def test_cue_leakage_mutation_is_detected(self):
        rows = [
            row.__class__(
                target=row.target,
                cue_content=row.target,
                cue_side=row.cue_side,
                eog_profile=row.eog_profile,
                oral_emg_profile=row.oral_emg_profile,
                timing_phase=row.timing_phase,
            )
            for row in build_endpoint_schedule("free_choice")
        ]
        result = summarize_endpoint(rows)
        self.assertEqual(result["nuisance_bayes_accuracy"], 1.0)
        self.assertEqual(result["target_incremental_degrees_of_freedom"], 0)
        self.assertFalse(result["target_separable_from_scheduled_nuisance"])

    def test_exact_sign_test_matches_frozen_twenty_one_person_gate(self):
        result = sign_test_sensitivity(21)
        self.assertEqual(result["minimum_positive_participants"], 15)
        self.assertAlmostEqual(result["null_tail_probability"], 0.03917694091796875)
        by_probability = {
            row["true_positive_participant_probability"]: row
            for row in result["power_curve"]
        }
        self.assertAlmostEqual(by_probability[0.7]["one_cohort_power"], 0.550518117374891)
        self.assertAlmostEqual(
            by_probability[0.8]["two_independent_cohorts_joint_power"],
            0.794750045097432,
        )
        self.assertAlmostEqual(exact_binomial_tail(21, 15, 0.5), 0.03917694091796875)

    def test_storage_recomputation_matches_frozen_contract(self):
        result = self.result["storage_and_device"]
        frozen = self.contract["storage_budget"]
        self.assertEqual(
            result["raw_total_worst_case_bytes"],
            frozen["raw_total_worst_case_bytes"],
        )
        self.assertEqual(result["raw_cap_headroom_bytes"], frozen["raw_cap_headroom_bytes"])
        self.assertTrue(result["fits_frozen_raw_cap"])

    def test_contract_drift_fails_closed(self):
        malformed = copy.deepcopy(self.contract)
        malformed["task"]["free_choice_intend_trials_per_participant"] = 63
        with self.assertRaisesRegex(TaskIdentifiabilityError, "free-choice trial count"):
            run_task_identifiability_audit(malformed)

        malformed = copy.deepcopy(self.contract)
        malformed["storage_budget"]["raw_total_worst_case_bytes"] += 1
        with self.assertRaisesRegex(TaskIdentifiabilityError, "recomputed raw storage"):
            run_task_identifiability_audit(malformed)

    def test_output_is_small_and_keeps_claim_boundary_closed(self):
        encoded = json.dumps(self.result, sort_keys=True, separators=(",", ":")).encode()
        self.assertLess(len(encoded), 1 << 20)
        self.assertEqual(set(self.result["operation_counters"].values()), {0})
        boundary = self.result["claim_boundary"]
        self.assertTrue(boundary["task_schedule_identifiability_checked"])
        for key, value in boundary.items():
            if key != "task_schedule_identifiability_checked":
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
