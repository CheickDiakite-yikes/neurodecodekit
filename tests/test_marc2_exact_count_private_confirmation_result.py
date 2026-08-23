import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/marc2_exact_count_private_confirmation_result.v0.json"
)


class Marc2ExactCountPrivateConfirmationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_the_single_generated_qualification(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_exact_count_private_confirmation_result",
        )
        self.assertEqual(self.result["lane_id"], "MARC2-VR34P")
        self.assertEqual(self.result["route"], "MARC2VR34P-G1")
        self.assertEqual(
            self.result["status"],
            "generated_exact_readiness_fixed_path_wrapper_qualified",
        )

    def test_matrix_matches_every_registered_count(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 60)
        self.assertEqual(matrix["VR33A_calls"], 60)
        self.assertEqual(matrix["readiness_provider_calls"], 180)
        self.assertEqual(matrix["readiness_sleeper_calls"], 120)
        self.assertEqual(matrix["source_constructions"], 32)
        self.assertEqual(matrix["source_content_opens"], 32)
        self.assertEqual(matrix["VR31A_calls"], 32)
        self.assertEqual(matrix["nested_VR29A_calls"], 32)
        self.assertEqual(matrix["nested_VR25A_calls"], 32)
        self.assertEqual(matrix["nested_R1_direction_comparisons"], 8)
        self.assertEqual(matrix["nonpassing_readiness_source_constructions"], 0)
        self.assertEqual(matrix["nonpassing_readiness_VR31A_calls"], 0)
        self.assertEqual(
            matrix["VR34P_route_counts"],
            {
                "MARC2VR34P-G1": 4,
                "MARC2VR34P-G2": 4,
                "MARC2VR34P-R1": 4,
                "MARC2VR34P-R2": 4,
                "MARC2VR34P-R3": 44,
            },
        )
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 110)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["fixed_path_state_machine_qualified"])

    def test_measurements_pass_every_registered_cap(self):
        measured = self.result["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 90)
        self.assertLess(measured["peak_RSS_bytes"], 268_435_456)
        self.assertLessEqual(measured["peak_incremental_output_bytes"], 1_048_576)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1_048_576)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["new_payload_bytes"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_every_forbidden_operation_counter_is_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_result_preserves_the_scientific_ceiling(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("generated", boundary["engineering_capability"])
        self.assertIn(
            "No private structural source", boundary["scientific_claim_not_established"]
        )


if __name__ == "__main__":
    unittest.main()
