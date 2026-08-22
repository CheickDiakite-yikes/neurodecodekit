import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries/marc2_f06_private_five_route_discriminator_result.v0.json"
)


class Marc2F06PrivateFiveRouteResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["implementation_commit"],
            "a2e19ba59d989ca27cada275ac460085cb07536c",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 32_601_257_065)
        self.assertEqual(
            proof["proof_closeout_commit"],
            "589b0f51db9a1bd157d90b0f4260fbb9c6475045",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_602_001_717)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_consumed_route_and_measured_resources_are_exact(self):
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertEqual(self.result["route"], "MARC2VR24P-R2")
        resources = self.result["resources"]
        self.assertEqual(resources["input_bytes"], 418_755)
        self.assertEqual(resources["output_bytes"], 3_068)
        self.assertEqual(resources["executor_runtime_seconds"], 0.1008453750400804)
        self.assertEqual(resources["observed_command_wall_seconds"], 10.096999959)
        self.assertEqual(resources["peak_RSS_bytes"], 27_656_192)
        self.assertLessEqual(resources["observed_command_wall_seconds"], 650)
        self.assertLess(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["output_bytes"], 1024**2)
        for key in ("CPU_threads", "workers", "numerical_jobs"):
            self.assertEqual(resources[key], 1)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)
        self.assertFalse(resources["end_to_end_latency_measured"])

    def test_one_shot_operation_counts_and_forbidden_counters_are_exact(self):
        operations = self.result["authorized_operations"]
        self.assertEqual(operations["fresh_readiness_samples"], 3)
        self.assertEqual(operations["private_structural_content_opens"], 1)
        self.assertEqual(operations["private_structural_source_bytes"], 418_755)
        self.assertEqual(operations["strict_JSON_parses"], 1)
        self.assertEqual(operations["VR23A_calls"], 1)
        self.assertEqual(operations["nested_VR20A_calls"], 1)
        self.assertEqual(operations["private_cohort_freezes"], 0)
        self.assertTrue(
            all(
                value == 0
                for value in self.result["returned_forbidden_counters"].values()
            )
        )

    def test_route_ceiling_preserves_private_count_uncertainty(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["frozen_class"],
            "VR20A_F06_complete_bundle_count_arithmetic_refused",
        )
        self.assertEqual(route["compatible_VR23A_routes"], ["MARC2VR23A-R2"])
        self.assertEqual(route["public_expected_complete_bundle_count"], 238)
        for key in (
            "observed_complete_bundle_count_known",
            "difference_direction_or_magnitude_known",
            "failed_predicate_known",
            "failed_private_value_known",
            "private_filename_path_row_or_identity_known",
            "participant_selection_reservation_or_cohort_known",
            "real_cohort_frozen",
            "FW2_or_CIL1_eligible",
        ):
            self.assertFalse(route[key], key)

    def test_no_private_reinspection_or_scientific_claim(self):
        handling = self.result["post_execution_handling"]
        self.assertEqual(handling["aggregate_report_inspections_after_execution"], 0)
        for key, value in handling.items():
            if key != "result_source":
                self.assertIn(value, (0, False), key)
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
