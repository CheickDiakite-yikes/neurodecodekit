import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/marc2_dynamic_live_selection_contract.v0.json"


class Marc2DynamicLiveSelectionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_upstream_green_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR6")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_dynamic_selection_repair_implementation_pending",
        )
        proof = self.contract["upstream_green_proof"]
        self.assertEqual(
            proof["closeout_commit"],
            "0c347adea910e42ef479e4f95e22603e3366683c",
        )
        self.assertEqual(proof["closeout_CI_run_id"], 31973927757)
        self.assertTrue(proof["both_closeout_jobs_green"])
        self.assertFalse(proof["observed_private_nested_route_available"])

    def test_every_fixed_input_is_committed_scoped_and_hash_bound(self):
        bindings = self.contract["fixed_inputs"]
        self.assertEqual(len(bindings), 7)
        self.assertEqual(len({row["role"] for row in bindings}), 7)
        for binding in bindings:
            with self.subTest(role=binding["role"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_policy_uses_dynamic_outputs_not_fixture_identity(self):
        policy = self.contract["dynamic_selection_policy"]
        self.assertEqual(policy["minimum_selected_subjects"], 12)
        self.assertEqual(policy["maximum_selected_subjects"], 19)
        self.assertEqual(policy["reservation_cap_bytes"], 8 * 1024**3)
        self.assertTrue(policy["selected_subjects_is_measured_output"])
        self.assertTrue(policy["selected_reservation_bytes_is_measured_output"])
        self.assertTrue(policy["selection_identity_sha256_is_measured_output"])
        self.assertFalse(policy["generated_expected_selection_object_allowed"])
        self.assertFalse(
            policy["real_value_may_be_compared_with_generated_subject_count"]
        )
        self.assertFalse(
            policy["real_value_may_be_compared_with_generated_reservation_bytes"]
        )
        self.assertFalse(
            policy["real_value_may_be_compared_with_generated_selection_hash"]
        )

    def test_split_arithmetic_and_maximality_are_frozen(self):
        policy = self.contract["dynamic_selection_policy"]
        self.assertTrue(policy["source_validation_precedes_selection"])
        self.assertEqual(policy["run_bundles_per_subject_total"], 6)
        self.assertEqual(policy["core_members_per_subject"], 24)
        self.assertEqual(policy["fit_heldout_overlap"], 0)
        self.assertTrue(
            policy["all_19_fit_or_exact_next_ranked_subject_does_not_fit"]
        )
        self.assertFalse(policy["target_label_quality_outcome_or_neural_field_allowed"])
        self.assertFalse(policy["row_random_split_allowed"])

    def test_generated_matrix_spans_minimum_middle_upper_and_all(self):
        profiles = self.contract["generated_success_profiles"]
        self.assertEqual(
            [row["expected_selected_subjects"] for row in profiles],
            [12, 14, 16, 18, 19],
        )
        replay = self.contract["generated_replay_policy"]
        self.assertEqual(replay["row_orders"], ["canonical", "reversed"])
        self.assertEqual(replay["success_paths"], 10)
        self.assertGreaterEqual(replay["minimum_direct_mutations"], 24)
        self.assertFalse(replay["profile_values_become_live_expected_values"])

    def test_upstream_route_preserves_code_only(self):
        policy = self.contract["upstream_route_policy"]
        self.assertEqual(
            policy["allowlisted_upstream_routes"],
            [f"MARC2VR2-F{index:02d}" for index in range(1, 9)],
        )
        self.assertTrue(policy["aggregate_route_code_preserved"])
        self.assertFalse(policy["upstream_reason_preserved"])
        self.assertFalse(policy["private_predicate_or_value_preserved"])
        self.assertTrue(policy["unknown_upstream_route_fails_closed"])
        self.assertFalse(policy["consumed_private_route_inferred"])

    def test_source_semantics_are_live_and_target_free(self):
        semantics = self.contract["source_semantics_policy"]
        self.assertEqual(
            semantics["live_row_source_id"],
            "freewill_23_live_central_directory",
        )
        self.assertFalse(semantics["generated_row_source_id_for_live_rows_allowed"])
        self.assertFalse(semantics["generated_proof_posture_for_live_rows_allowed"])
        self.assertFalse(
            semantics["generated_inventory_hash_key_for_live_rows_allowed"]
        )

    def test_authority_resources_and_claims_remain_generated_only(self):
        authority = self.contract["authorization_state"]
        allowed = {
            "generated_fixture_implementation_and_qualification",
            "fixed_committed_artifact_reads",
        }
        self.assertTrue(all(authority[name] for name in allowed))
        self.assertFalse(
            any(value for name, value in authority.items() if name not in allowed)
        )
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["private_or_Git_ignored_bytes"], 0)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["retained_generated_output_bytes"], 0)
        gate = self.contract["implementation_gate"]
        self.assertFalse(gate["execute_command_allowed"])
        self.assertTrue(
            gate["future_private_read_requires_new_Tier_C_packet_and_decision"]
        )
        claim = self.contract["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["real_cohort_frozen"])
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
