import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_inventory_taxonomy_private_discriminator_private_result.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_INVENTORY_TAXONOMY_PRIVATE_DISCRIMINATOR_RESULT.md"
)


class Marc2InventoryTaxonomyPrivateDiscriminatorPrivateResultTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_precedes_execution(self):
        proof = self.result["execution_proof_chain"]
        self.assertEqual(
            proof["decision_commit"],
            "718c3de6ddb0030b1ba39fa0e42250e97db01072",
        )
        self.assertEqual(
            proof["exact_implementation_commit"],
            "6d3b770d0e67c8b394c6a1a7581c21ae7b202909",
        )
        self.assertEqual(
            proof["proof_closeout_commit"],
            "96bff687013dcbfb507455b5f8c045977bc84fe8",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 32_617_240_661)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_one_shot_result_is_exact_and_bounded(self):
        report = self.result["returned_aggregate_report"]
        measurements = report["measurements"]
        self.assertEqual(self.result["route"], "MARC2VR28P-R1")
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertEqual(measurements["input_bytes"], 418_755)
        self.assertEqual(measurements["source_content_opens"], 1)
        self.assertEqual(measurements["strict_JSON_parses"], 1)
        self.assertEqual(measurements["VR25A_calls"], 1)
        self.assertEqual(measurements["VR27A_map_calls"], 1)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measurements["runtime_seconds"], 650)

    def test_operation_boundary_is_exact(self):
        allowed = self.result["authorized_operations"]
        self.assertEqual(allowed["registered_invocations"], 1)
        self.assertEqual(allowed["fresh_readiness_samples"], 3)
        self.assertEqual(allowed["private_structural_content_opens"], 1)
        self.assertEqual(allowed["strict_JSON_parses"], 1)
        self.assertEqual(allowed["VR25A_calls"], 1)
        self.assertEqual(allowed["VR27A_map_calls"], 1)
        self.assertEqual(allowed["private_cohort_freezes"], 0)
        self.assertTrue(
            all(
                value == 0
                for value in self.result["returned_forbidden_counters"].values()
            )
        )

    def test_route_ceiling_excludes_taxonomy_without_exposing_detail(self):
        route = self.result["route_interpretation"]
        self.assertEqual(route["compatible_VR25A_routes"], ["MARC2VR25A-R1"])
        self.assertEqual(route["excluded_VR25A_routes"], ["MARC2VR25A-R2"])
        self.assertTrue(route["unknown_recognized_participant_taxonomy_excluded"])
        self.assertFalse(route["eligible_inventory_arithmetic_known"])
        self.assertFalse(route["participant_session_distribution_arithmetic_known"])
        self.assertFalse(route["real_cohort_frozen"])

    def test_output_telemetry_gap_and_no_reinspection_are_explicit(self):
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
        self.assertIsNone(output["readiness_certificate_bytes"])
        self.assertIsNone(output["consumed_marker_bytes"])
        self.assertIsNone(output["combined_incremental_output_bytes"])
        self.assertFalse(output["exact_combined_output_measured"])
        self.assertFalse(output["private_output_reinspection_used_to_recover_bytes"])
        self.assertEqual(post["private_output_listing_or_stat_operations"], 0)
        self.assertEqual(post["private_reinspection_operations"], 0)
        self.assertFalse(post["retry_rerun_resume_allowed"])

    def test_human_result_states_engineering_and_scientific_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("R1 means the remaining blocker", text)
        self.assertIn("unknown-participant taxonomy route", text)
        self.assertIn("combined incremental output bytes are unavailable", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
