import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT / "registries/marc2_r1_inventory_distribution_discriminator_result.v0.json"
)


class Marc2R1InventoryDistributionDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_result_is_generated_only_and_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR29A")
        self.assertEqual(self.result["route"], "MARC2VR29A-G1")
        self.assertEqual(
            self.result["status"],
            "generated_inventory_distribution_discriminator_qualified_remote_proof_pending",
        )

    def test_matrix_routes_and_replay_are_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR25A_calls"], 32)
        self.assertEqual(matrix["R1_filter_discriminator_calls"], 16)
        self.assertEqual(matrix["VR2_filter_refusal_sites"], 2)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["order_invariant_route_distribution"])
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertFalse(matrix["private_reason_or_value_retained"])

    def test_measured_resources_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 14_137_216)
        self.assertEqual(measured["aggregate_output_bytes"], 2_880)
        self.assertEqual(measured["peak_RSS_bytes"], 37_371_904)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertEqual(measured["retained_output_bytes"], 0)

    def test_forbidden_operations_and_claims_remain_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        claims = self.result["claim_boundary"]
        self.assertFalse(claims["consumed_private_subclass_identified"])
        self.assertFalse(claims["real_cohort_established"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])

    def test_remote_proof_transition_preserves_private_boundary(self):
        proof = self.result["remote_implementation_proof"]
        if proof is not None:
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
        gate = self.result["next_gate"]
        self.assertFalse(gate["private_or_neural_access_authorized"])
        self.assertFalse(gate["FW2_or_CIL1_authorized"])


if __name__ == "__main__":
    unittest.main()
