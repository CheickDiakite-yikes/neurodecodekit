import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT / "registries/marc2_selection_boundary_private_confirmation_result.v0.json"
)
DOC = ROOT / "docs/MARC_2_SELECTION_BOUNDARY_PRIVATE_CONFIRMATION_RESULT.md"


class Marc2SelectionBoundaryPrivateConfirmationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(proof["decision_commit"], "8b9ce248f6cbce1205addf113f97325a98c1992e")
        self.assertEqual(proof["implementation_commit"], "d5c5abd8fde15f0557101fa2aa1135382819ea4e")
        self.assertEqual(proof["proof_closeout_commit"], "bb6c52bb7217edb79eec5c3f09c14ba50776c2c6")
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_609_855_945)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_one_shot_result_is_exact_and_bounded(self):
        self.assertEqual(self.result["route"], "MARC2VR26P-R5")
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertEqual(self.result["resources"]["input_bytes"], 418_755)
        self.assertEqual(self.result["resources"]["output_bytes"], 2_923)
        self.assertLess(self.result["resources"]["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(self.result["resources"]["executor_runtime_seconds"], 650)

    def test_operation_boundary_is_exact(self):
        allowed = self.result["authorized_operations"]
        self.assertEqual(allowed["fresh_readiness_samples"], 3)
        self.assertEqual(allowed["private_structural_content_opens"], 1)
        self.assertEqual(allowed["strict_JSON_parses"], 1)
        self.assertEqual(allowed["VR25A_calls"], 1)
        self.assertEqual(allowed["private_cohort_freezes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.result["returned_forbidden_counters"].values())
        )

    def test_route_ceiling_and_post_execution_boundary_are_preserved(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["compatible_VR25A_routes"], ["MARC2VR25A-R1", "MARC2VR25A-R2"]
        )
        self.assertFalse(route["eligible_inventory_or_distribution_drift_known"])
        self.assertFalse(route["unknown_recognized_participant_known"])
        self.assertFalse(route["real_cohort_frozen"])
        post = self.result["post_execution_handling"]
        self.assertEqual(post["aggregate_report_inspections_after_execution"], 0)
        self.assertEqual(post["private_reinspection_operations"], 0)
        self.assertFalse(post["retry_rerun_resume_allowed"])

    def test_human_result_states_engineering_and_scientific_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("R5 means participant taxonomy or the exact", text)
        self.assertIn("eligible inventory refused", text)
        self.assertIn("aggregate JSON returned by `execute`", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
