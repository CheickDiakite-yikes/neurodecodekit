import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_contract.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_R1_ELIGIBLE_TOTAL_DIRECTION_DISCRIMINATOR_PREREGISTRATION.md"
)


class Marc2R1EligibleTotalDirectionDiscriminatorRegistrationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_result_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR31A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR30P_result_commit"],
            "a6e1ac5c17c2cffd4d07222c1f3eebcd05fb6a22",
        )
        self.assertEqual(proof["VR30P_result_CI_run_id"], 32_626_086_478)
        self.assertEqual(proof["observed_route"], "MARC2VR30P-R1")
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["private_source_or_consumed_output_reinspected_by_registration"])

    def test_all_fixed_inputs_match(self):
        total = 0
        for item in self.contract["fixed_inputs"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                item["sha256"],
                item["path"],
            )
            total += len(payload)
        self.assertEqual(len(self.contract["fixed_inputs"]), 8)
        self.assertEqual(total, self.contract["fixed_input_bytes"])

    def test_threshold_is_immutable_and_non_disclosing(self):
        predicate = self.contract["immutable_threshold_predicate"]
        self.assertEqual(predicate["function_name"], "_filter_and_validate_eligible")
        self.assertEqual(predicate["expression"], "len(filtered) != 195")
        self.assertEqual(predicate["expected_total"], 195)
        self.assertEqual(predicate["exact_AST_match_count"], 1)
        self.assertFalse(predicate["threshold_override_allowed"])
        self.assertFalse(predicate["observed_total_or_difference_output_allowed"])

    def test_direction_routes_are_exact(self):
        inventory = self.contract["ordered_R1_direction_inventory"]
        self.assertEqual(inventory["below_expected"]["VR31A_route"], "MARC2VR31A-R1")
        self.assertEqual(inventory["above_expected"]["VR31A_route"], "MARC2VR31A-R2")
        self.assertEqual(inventory["non_R1_upstream"]["VR31A_route"], "MARC2VR31A-R3")
        self.assertTrue(
            all(
                not row.get("observed_total_or_difference_allowed", False)
                for row in inventory.values()
            )
        )

    def test_generated_matrix_and_call_counts_are_frozen(self):
        matrix = self.contract["generated_witness_matrix"]
        self.assertEqual(len(matrix["cases"]), 8)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 32)
        self.assertEqual(matrix["required_VR29A_calls"], 32)
        self.assertEqual(matrix["required_R1_direction_comparisons"], 8)
        self.assertEqual(
            matrix["expected_VR31A_route_counts"],
            {
                "MARC2VR31A-G1": 4,
                "MARC2VR31A-G2": 4,
                "MARC2VR31A-R1": 4,
                "MARC2VR31A-R2": 4,
                "MARC2VR31A-R3": 16,
            },
        )
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 70)
        self.assertFalse(
            matrix[
                "observed_total_difference_distribution_participant_or_source_detail_retention_allowed"
            ]
        )

    def test_implementation_has_no_private_executor_or_override(self):
        implementation = self.contract["implementation_contract"]
        self.assertEqual(implementation["commands"], ["plan", "qualify"])
        self.assertEqual(implementation["dependency_policy"], "standard_library_only")
        self.assertTrue(implementation["one_VR29A_call_per_generated_path"])
        self.assertTrue(implementation["one_direction_comparison_per_R1_path"])
        self.assertFalse(implementation["private_executor_allowed"])
        self.assertEqual(implementation["retained_generated_source_bytes"], 0)

    def test_resource_limits_are_small(self):
        limits = self.contract["resource_limits"]
        self.assertEqual(limits["CPU_threads"], 1)
        self.assertEqual(limits["workers"], 1)
        self.assertEqual(limits["numerical_jobs"], 1)
        self.assertLessEqual(limits["runtime_seconds"], 30)
        self.assertLessEqual(limits["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(limits["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(limits["aggregate_output_bytes"], 1024**2)
        self.assertEqual(limits["retained_output_bytes"], 0)
        self.assertEqual(limits["network_bytes"], 0)
        self.assertEqual(limits["new_payload_bytes"], 0)

    def test_authorization_and_operation_counters_remain_closed(self):
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["artifact_only_reads"])
        self.assertTrue(authorization["generated_fixture_creation"])
        self.assertFalse(authorization["private_or_Git_ignored_path_access"])
        self.assertFalse(authorization["readiness_or_consumed_state_access"])
        self.assertFalse(authorization["archive_header_or_member_access"])
        self.assertFalse(authorization["signal_event_target_or_label_access"])
        self.assertFalse(
            authorization["model_training_inference_prediction_or_scoring"]
        )
        self.assertFalse(authorization["network_or_provider_calls"])
        self.assertFalse(authorization["FW2_or_CIL1_execution"])
        self.assertFalse(authorization["scientific_claim_upgrade"])
        self.assertTrue(
            all(
                value == 0
                for value in self.contract["registration_operation_counters"].values()
            )
        )

    def test_claim_boundary_is_explicit(self):
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["real_cohort_established"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("Another private read", text)


if __name__ == "__main__":
    unittest.main()
