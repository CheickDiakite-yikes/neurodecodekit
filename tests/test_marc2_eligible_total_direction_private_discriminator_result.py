import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/marc2_eligible_total_direction_private_discriminator_result.v0.json"
)


class Marc2EligibleTotalDirectionPrivateDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_generated_stage_1_only(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_eligible_total_direction_private_discriminator_result",
        )
        self.assertEqual(self.result["lane_id"], "MARC2-VR32P")
        self.assertEqual(self.result["route"], "MARC2VR32P-G1")
        self.assertEqual(
            self.result["status"], "generated_fixed_path_wrapper_qualified"
        )

    def test_matrix_is_exact_and_deterministic(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["source_content_opens"], 32)
        self.assertEqual(matrix["VR31A_calls"], 32)
        self.assertEqual(matrix["nested_VR29A_calls"], 32)
        self.assertEqual(matrix["nested_VR25A_calls"], 32)
        self.assertEqual(matrix["nested_R1_direction_comparisons"], 8)
        self.assertEqual(
            matrix["VR32P_route_counts"],
            {
                "MARC2VR32P-G1": 4,
                "MARC2VR32P-G2": 4,
                "MARC2VR32P-R1": 4,
                "MARC2VR32P-R2": 4,
                "MARC2VR32P-R3": 16,
            },
        )
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["marker_preceded_every_source_open"])
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 90)

    def test_measurements_are_under_registered_caps(self):
        measured = self.result["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 60)
        self.assertLess(measured["peak_RSS_bytes"], 268_435_456)
        self.assertLessEqual(measured["peak_incremental_output_bytes"], 1_048_576)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)

    def test_every_forbidden_operation_counter_is_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_claim_boundary_is_explicit(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("generated fixed-path", boundary["engineering_capability"])
        self.assertIn(
            "No private structural source",
            boundary["scientific_claim_not_established"],
        )


if __name__ == "__main__":
    unittest.main()
