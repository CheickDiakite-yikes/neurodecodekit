import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/marc2_exact_task_surplus_decomposition_result.v0.json"


class ExactTaskSurplusDecompositionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_identity_and_registration_proof_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR37A")
        proof = self.result["registration_proof"]
        self.assertEqual(proof["commit"], "a677e7abd2b89e92bb7bcc3f823a3493c6a32ad0")
        self.assertEqual(proof["CI_run_id"], 32_652_807_264)
        self.assertEqual(proof["base_job_id"], 97_226_913_287)
        self.assertEqual(proof["optional_neuro_job_id"], 97_226_913_421)

    def test_frozen_matrix_passed_exactly_once(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 24)
        self.assertEqual(matrix["VR35A_calls"], 24)
        self.assertEqual(set(matrix["route_counts"].values()), {4})
        self.assertEqual(
            set(matrix["route_counts"]),
            {
                "MARC2VR37A-G1",
                "MARC2VR37A-R1",
                "MARC2VR37A-R2",
                "MARC2VR37A-R3",
                "MARC2VR37A-R4",
                "MARC2VR37A-R5",
            },
        )
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(self.result["qualification_invocations"], 1)
        self.assertFalse(self.result["qualification_may_be_repeated"])

    def test_all_frozen_topology_classes_are_distinguished(self):
        decomposition = self.result["decomposition"]
        self.assertEqual(decomposition["published_subject_session_cells"], 38)
        self.assertEqual(decomposition["published_cell_total"], 195)
        for key, value in decomposition.items():
            if key.endswith("_distinguished"):
                self.assertTrue(value, key)

    def test_resources_and_forbidden_operations_stayed_within_bounds(self):
        measurements = self.result["measurements"]
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLess(measurements["aggregate_output_bytes"], 1024 * 1024)
        self.assertEqual(measurements["retained_output_bytes"], 0)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertTrue(all(value == 0 for value in self.result["operation_counters"].values()))

    def test_claim_boundary_and_next_gate_remain_closed(self):
        boundary = self.result["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["private_source_accessed"])
        self.assertFalse(boundary["real_cohort_established"])
        self.assertFalse(boundary["neural_payload_accessed"])
        self.assertFalse(boundary["decoding_performance_established"])
        self.assertIsNone(self.result["remote_implementation_proof"])
        gate = self.result["next_gate"]
        self.assertTrue(gate["implementation_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["private_discriminator_or_read_authorized"])


if __name__ == "__main__":
    unittest.main()
