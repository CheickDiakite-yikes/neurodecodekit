import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/"
    "marc2_eligible_total_direction_private_discriminator_private_result.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_ELIGIBLE_TOTAL_DIRECTION_PRIVATE_DISCRIMINATOR_RESULT.md"
)


class Marc2EligibleTotalDirectionPrivateDiscriminatorPrivateResultTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["decision_commit"],
            "cb80d07b0e83c3d02d0bb3f7afae08b4ee6ba528",
        )
        self.assertEqual(
            proof["exact_implementation_commit"],
            "bae648e269e56dde45eb15295224fbafcc3c8706",
        )
        self.assertEqual(
            proof["proof_closeout_commit"],
            "5aec8a15f5ee6fa3c6ca9cefcfb4fbfead9dd72f",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_632_497_701)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_one_shot_result_is_exact_and_bounded(self):
        report = self.result["returned_aggregate_report"]
        measurements = report["measurements"]
        self.assertEqual(self.result["route"], "MARC2VR32P-R2")
        self.assertEqual(measurements["input_bytes"], 418_755)
        self.assertEqual(measurements["source_content_opens"], 1)
        self.assertEqual(measurements["strict_JSON_parses"], 1)
        self.assertEqual(measurements["VR31A_calls"], 1)
        self.assertEqual(measurements["nested_VR29A_calls"], 1)
        self.assertEqual(measurements["nested_VR25A_calls"], 1)
        self.assertEqual(measurements["nested_R1_direction_comparisons"], 1)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measurements["runtime_seconds"], 650)

    def test_R2_ceiling_is_exact_without_exposing_count(self):
        route = self.result["route_interpretation"]
        self.assertEqual(route["compatible_VR31A_routes"], ["MARC2VR31A-R2"])
        self.assertEqual(route["excluded_VR31A_routes"], ["MARC2VR31A-R1"])
        self.assertTrue(route["filtered_eligible_total_above_195"])
        self.assertFalse(route["observed_filtered_eligible_total_known"])
        self.assertFalse(route["difference_magnitude_known"])
        self.assertFalse(route["real_cohort_frozen"])

    def test_readiness_sample_overrun_is_explicit_and_blocks_upgrade(self):
        fidelity = self.result["protocol_fidelity"]
        self.assertEqual(fidelity["registered_readiness_samples"], 3)
        self.assertEqual(fidelity["returned_readiness_samples"], 5)
        self.assertEqual(fidelity["readiness_sample_count_excess"], 2)
        self.assertFalse(fidelity["fully_protocol_conforming"])
        self.assertFalse(fidelity["claim_upgrade_allowed"])
        self.assertFalse(fidelity["rerun_or_repair_allowed"])

    def test_output_gap_and_no_reinspection_are_explicit(self):
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
        self.assertEqual(post["private_output_listing_or_stat_operations"], 0)
        self.assertEqual(post["private_reinspection_operations"], 0)
        self.assertFalse(post["retry_rerun_resume_allowed"])

    def test_human_result_states_observation_deviation_and_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("R2 means the filtered eligible total is above", text)
        self.assertIn("five readiness samples", text)
        self.assertIn("not described as a fully protocol-", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
