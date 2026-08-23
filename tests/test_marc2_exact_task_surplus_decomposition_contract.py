import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT / "registries/marc2_exact_task_surplus_decomposition_contract.v0.json"
)
DOC = ROOT / "docs/MARC_2_EXACT_TASK_SURPLUS_DECOMPOSITION_PREREGISTRATION.md"


class ExactTaskSurplusDecompositionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_green_predecessor_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR37A")
        proof = self.contract["green_predecessor_proof"]
        self.assertEqual(
            proof["commit"], "d55142ac52b862fba94958ad38638d47975c9969"
        )
        self.assertEqual(proof["CI_run_id"], 32_651_904_520)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_fixed_inputs_are_byte_exact(self):
        total = 0
        for row in self.contract["fixed_inputs"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            total += len(payload)
        self.assertEqual(total, self.contract["fixed_input_bytes"])
        self.assertEqual(len(self.contract["fixed_inputs"]), 8)

    def test_artifact_only_findings_preserve_private_ceiling(self):
        findings = self.contract["artifact_only_findings"]
        self.assertEqual(findings["consumed_VR36P_route"], "MARC2VR36P-R3")
        self.assertEqual(findings["compatible_VR35A_route"], "MARC2VR35A-R1")
        self.assertEqual(findings["published_cell_total"], 195)
        self.assertTrue(findings["global_surplus_requires_at_least_one_positive_cell_delta"])
        self.assertFalse(findings["consumed_route_distinguishes_delta_topology"])
        self.assertFalse(findings["private_count_difference_distribution_identity_or_row_known"])

    def test_routes_and_generated_matrix_are_frozen(self):
        self.assertEqual(
            [row["route"] for row in self.contract["ordered_routes"]],
            [
                "MARC2VR37A-G1",
                "MARC2VR37A-R1",
                "MARC2VR37A-R2",
                "MARC2VR37A-R3",
                "MARC2VR37A-R4",
                "MARC2VR37A-R5",
            ],
        )
        matrix = self.contract["generated_matrix"]
        self.assertEqual(matrix["required_paths"], 24)
        self.assertEqual(matrix["VR35A_calls"], 24)
        self.assertEqual(set(matrix["expected_route_counts"].values()), {4})
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 60)

    def test_implementation_and_private_boundaries_are_closed(self):
        implementation = self.contract["implementation_contract"]
        self.assertEqual(implementation["commands"], ["plan", "qualify"])
        self.assertFalse(implementation["private_executor_allowed"])
        self.assertFalse(implementation["private_or_Git_ignored_path_constants_allowed"])
        self.assertTrue(all(value == 0 for value in self.contract["forbidden_operations"].values()))
        self.assertFalse(self.contract["next_gate"]["private_read_or_discriminator_authorized"])

    def test_human_registration_states_proposal_and_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("implementation blocked until", text)
        self.assertIn("generated diagnostic mechanisms", text)
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
