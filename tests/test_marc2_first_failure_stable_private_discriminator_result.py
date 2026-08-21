import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_result.v0.json"
)
RESULT_DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_FIRST_FAILURE_STABLE_PRIVATE_DISCRIMINATOR_RESULT.md"
)


class Marc2FirstFailureStablePrivateDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_consumed_route_and_proof_chain_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR18P")
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertEqual(self.result["route"], "MARC2VR18P-R4")
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["proof_closeout_commit"],
            "535bd9bf8cb8cc48dd8369be7c2d5c51af1a7d63",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_478_506_443)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_resources_and_authorized_operations_are_exact(self):
        resources = self.result["resources"]
        self.assertEqual(resources["input_bytes"], 418_755)
        self.assertEqual(resources["output_bytes"], 2_063)
        self.assertEqual(resources["peak_RSS_bytes"], 27_443_200)
        self.assertLess(resources["runtime_seconds"], 650)
        self.assertEqual(resources["network_bytes"], 0)
        operations = self.result["authorized_operations"]
        self.assertEqual(operations["private_structural_content_opens"], 1)
        self.assertEqual(operations["strict_JSON_parses"], 1)
        self.assertEqual(operations["VR16A_calls"], 1)
        self.assertEqual(operations["VR17C_map_calls"], 1)
        self.assertEqual(operations["private_cohort_freezes"], 0)

    def test_every_returned_forbidden_counter_is_zero(self):
        self.assertTrue(
            all(
                value == 0
                for value in self.result["returned_forbidden_counters"].values()
            )
        )
        handling = self.result["post_execution_handling"]
        self.assertEqual(handling["aggregate_report_inspections_after_execution"], 0)
        self.assertEqual(handling["private_source_reopens"], 0)
        self.assertEqual(handling["private_reinspection_operations"], 0)
        self.assertFalse(handling["retry_rerun_resume_allowed"])

    def test_route_ceiling_is_narrow_and_does_not_claim_a_cohort(self):
        route = self.result["route_interpretation"]
        self.assertEqual(
            route["frozen_class"], "generated_qualified_core_task_or_identity_class"
        )
        self.assertFalse(route["task_versus_identity_known"])
        self.assertFalse(route["failed_predicate_known"])
        self.assertFalse(route["real_cohort_frozen"])
        self.assertFalse(route["FW2_or_CIL1_eligible"])

    def test_document_preserves_structural_not_scientific_boundary(self):
        text = RESULT_DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("MARC2VR18P-R4", text)
        self.assertIn("target-free structural", text)
        self.assertIn("no neural payload", text)
        self.assertIn("no retry", text)
        boundary = self.result["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["neural_effect"])
        self.assertFalse(boundary["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
