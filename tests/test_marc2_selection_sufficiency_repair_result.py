import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/marc2_selection_sufficiency_repair_result.v0.json"


class Marc2SelectionSufficiencyRepairResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_identity_and_registration_proof_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR38A")
        proof = self.result["registration_proof"]
        self.assertEqual(proof["commit"], "25205b1d2a1033cf3cefcab022c885025ac76928")
        self.assertEqual(proof["CI_run_id"], 32_670_514_251)
        self.assertEqual(proof["base_job_id"], 97_270_563_617)
        self.assertEqual(proof["optional_neuro_job_id"], 97_270_563_773)

    def test_frozen_matrix_passed_exactly_once(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 40)
        self.assertEqual(matrix["selector_calls"], 40)
        self.assertEqual(
            matrix["route_counts"],
            {
                "MARC2VR38A-G1": 4,
                "MARC2VR38A-G2": 16,
                "MARC2VR38A-R1": 8,
                "MARC2VR38A-R2": 8,
                "MARC2VR38A-R3": 4,
            },
        )
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(self.result["qualification_invocations"], 1)
        self.assertFalse(self.result["qualification_may_be_repeated"])

    def test_selection_sufficiency_gates_passed(self):
        proof = self.result["selection_proof"]
        self.assertEqual(proof["accepted_paths"], 20)
        self.assertEqual(proof["accepted_semantic_identities"], 1)
        self.assertEqual(proof["accepted_source_exact_name_identities"], 1)
        self.assertEqual(proof["generated_selected_subjects"], 16)
        self.assertEqual(proof["generated_selected_run_bundles"], 96)
        self.assertEqual(proof["generated_selected_core_members"], 384)
        self.assertEqual(proof["required_runs_per_session"], [1, 2, 3])
        self.assertEqual(proof["selected_optional_runs"], 0)
        self.assertEqual(proof["selected_non_target_rows"], 0)
        self.assertEqual(proof["selected_ineligible_rows"], 0)
        self.assertFalse(proof["global_exact_195_gate_used"])

    def test_resources_refusals_and_operations_are_bounded(self):
        measurements = self.result["measurements"]
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLess(measurements["aggregate_output_bytes"], 1024 * 1024)
        self.assertEqual(measurements["retained_output_bytes"], 0)
        self.assertGreaterEqual(self.result["refusals"]["direct_refusals"], 80)
        self.assertTrue(all(value == 0 for value in self.result["operation_counters"].values()))

    def test_claim_boundary_and_terminal_gate_remain_closed(self):
        boundary = self.result["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["private_source_accessed"])
        self.assertFalse(boundary["real_cohort_established"])
        self.assertFalse(boundary["neural_payload_accessed"])
        self.assertFalse(boundary["decoding_performance_established"])
        gate = self.result["terminal_next_gate"]
        self.assertTrue(
            gate["next_private_structural_request_must_freeze_a_cohort_or_park_Freewill"]
        )
        self.assertFalse(gate["topology_only_private_successor_allowed"])
        self.assertFalse(
            gate[
                "private_read_cohort_freeze_archive_neural_target_model_score_or_claim_authorized_now"
            ]
        )


if __name__ == "__main__":
    unittest.main()
