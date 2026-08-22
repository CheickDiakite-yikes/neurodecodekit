import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_f06_five_route_decomposition_result.v0.json"


class Marc2F06FiveRouteDecompositionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_route_table_and_matrix_are_exact(self):
        self.assertEqual(self.result["route"], "MARC2VR23A-G1")
        self.assertEqual(len(self.result["route_table"]), 6)
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 24)
        self.assertEqual(matrix["VR20A_calls"], 24)
        self.assertEqual(matrix["diagnostic_and_VR20A_route_disagreements"], 0)
        self.assertEqual(matrix["source_mutations_after_call"], 0)

    def test_every_generated_route_appears_four_times(self):
        self.assertEqual(
            self.result["matrix"]["VR23A_route_counts"],
            {"MARC2VR23A-G1": 4}
            | {f"MARC2VR23A-R{index}": 4 for index in range(1, 6)},
        )

    def test_measured_resources_are_bounded(self):
        resources = self.result["resources"]
        self.assertEqual(resources["generated_input_bytes"], 10_603_766)
        self.assertEqual(resources["aggregate_output_bytes"], 6_458)
        self.assertEqual(resources["runtime_seconds"], 2.4120343329850584)
        self.assertEqual(resources["peak_RSS_bytes"], 39_944_192)
        self.assertFalse(resources["end_to_end_latency_measured"])

    def test_all_real_private_and_scientific_counters_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_real_class_remains_unavailable_and_private_gate_closed(self):
        self.assertIn("real_failed_F06_class", self.result["unavailable_fields"])
        gate = self.result["next_gate"]
        self.assertTrue(
            gate["future_private_discriminator_requires_new_Tier_C_packet_and_decision"]
        )
        self.assertFalse(
            gate["private_neural_target_model_score_FW2_or_CIL1_authorized"]
        )


if __name__ == "__main__":
    unittest.main()
