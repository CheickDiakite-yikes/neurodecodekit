import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_task_aware_private_cohort_confirmation_private_result.v0.json"
)
DOC = ROOT / "docs/MARC_2_TASK_AWARE_PRIVATE_COHORT_CONFIRMATION_RESULT.md"


class TaskAwarePrivateCohortConfirmationPrivateResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["decision_commit"],
            "fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5",
        )
        self.assertEqual(
            proof["exact_implementation_commit"],
            "8179f6fd4acb721ef25b023e02ac9160789f9d49",
        )
        self.assertEqual(
            proof["proof_closeout_commit"],
            "d4074081b86e6b6247f91150daa1e3253f6e2bd9",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_651_006_809)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_one_shot_result_is_exact_and_bounded(self):
        report = self.result["returned_aggregate_report"]
        measured = report["measurements"]
        self.assertEqual(self.result["route"], "MARC2VR36P-R3")
        self.assertEqual(measured["input_bytes"], 418_755)
        self.assertEqual(measured["readiness_samples"], 3)
        self.assertEqual(measured["readiness_sleeps"], 2)
        self.assertEqual(measured["source_content_opens"], 1)
        self.assertEqual(measured["strict_JSON_parses"], 1)
        self.assertEqual(measured["VR33A_calls"], 1)
        self.assertEqual(measured["VR35A_calls"], 1)
        self.assertFalse(measured["cohort_file_written"])
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["runtime_seconds"], 120)

    def test_R3_ceiling_is_exact_without_exposing_private_values(self):
        route = self.result["route_interpretation"]
        self.assertEqual(route["compatible_VR35A_routes"], ["MARC2VR35A-R1"])
        self.assertTrue(route["exact_task_projected_eligible_total_above_195"])
        self.assertTrue(route["mixed_task_surplus_as_sole_explanation_excluded"])
        self.assertFalse(route["observed_exact_task_eligible_total_known"])
        self.assertFalse(route["difference_magnitude_known"])
        self.assertFalse(route["private_task_distribution_known"])
        self.assertFalse(route["real_cohort_frozen"])

    def test_readiness_and_execution_protocol_conform_without_claim_upgrade(self):
        fidelity = self.result["protocol_fidelity"]
        self.assertEqual(fidelity["registered_readiness_samples"], 3)
        self.assertEqual(fidelity["returned_readiness_samples"], 3)
        self.assertEqual(fidelity["registered_readiness_sleeps"], 2)
        self.assertEqual(fidelity["returned_readiness_sleeps"], 2)
        self.assertTrue(fidelity["fully_protocol_conforming"])
        self.assertFalse(fidelity["claim_upgrade_allowed"])
        self.assertFalse(fidelity["rerun_or_repair_allowed"])

    def test_output_gap_and_no_private_reinspection_are_explicit(self):
        output = self.result["output_measurement"]
        post = self.result["post_execution_handling"]
        canonical_report = (
            json.dumps(
                self.result["returned_aggregate_report"],
                allow_nan=False,
                ensure_ascii=True,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        ).encode("ascii")
        self.assertEqual(
            len(canonical_report), output["aggregate_return_JSON_canonical_bytes"]
        )
        self.assertIsNone(output["combined_incremental_output_bytes"])
        self.assertFalse(output["exact_combined_output_measured"])
        self.assertFalse(output["private_output_reinspection_used_to_recover_bytes"])
        self.assertEqual(post["aggregate_report_inspections_after_execution"], 1)
        self.assertEqual(post["private_output_listing_or_stat_operations"], 0)
        self.assertEqual(post["private_reinspection_operations"], 0)
        self.assertFalse(post["retry_rerun_resume_allowed"])

    def test_consumption_and_forbidden_boundaries_are_closed(self):
        operations = self.result["execution_operation_counts"]
        forbidden = self.result["recorded_forbidden_counters"]
        self.assertEqual(operations["registered_invocations"], 1)
        self.assertEqual(operations["private_cohort_freezes"], 0)
        self.assertTrue(all(value == 0 for value in forbidden.values()))
        self.assertFalse(self.result["next_gate"]["VR36P_rerun_or_repair_authorized"])

    def test_human_result_states_route_protocol_and_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("R3 maps only to VR35A R1", text)
        self.assertIn("exactly three readiness samples", text)
        self.assertIn("no real cohort was frozen", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
