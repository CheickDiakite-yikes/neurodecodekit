import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = json.loads(
    (
        ROOT
        / "registries/marc2_selection_sufficiency_private_cohort_freeze_private_result.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_RESULT.md"
).read_text(encoding="utf-8")


class SelectionSufficiencyPrivateCohortFreezePrivateResultTests(unittest.TestCase):
    def test_exact_consumed_route_and_proof_chain_are_bound(self):
        self.assertEqual(REGISTRY["lane_id"], "MARC2-VR39P")
        self.assertEqual(REGISTRY["route"], "MARC2VR39P-R2")
        self.assertEqual(
            REGISTRY["execution_proof_chain"]["activation_commit"],
            "c74255526a9265e52919672e8c6088022b77ef1d",
        )
        self.assertEqual(
            REGISTRY["execution_proof_chain"]["activation_CI_run_id"],
            32_687_368_688,
        )
        self.assertTrue(
            REGISTRY["execution_proof_chain"][
                "every_required_barrier_green_before_execution"
            ]
        )

    def test_returned_report_has_exact_public_allowlist(self):
        report = REGISTRY["returned_aggregate_report"]
        self.assertEqual(
            set(report),
            {
                "claim_boundary",
                "cohort_commitment_sha256",
                "commitment_scheme",
                "lane_id",
                "proof_anchors",
                "route",
                "schema_name",
                "schema_version",
                "status",
                "unavailable_fields",
                "warnings",
            },
        )
        self.assertEqual(report["route"], "MARC2VR39P-R2")
        self.assertEqual(report["commitment_scheme"], "HMAC-SHA256-v0")
        self.assertIsNone(report["cohort_commitment_sha256"])
        self.assertEqual(report["claim_boundary"]["scientific"], "none")

    def test_no_private_reinspection_or_rerun_was_recorded(self):
        capture = REGISTRY["capture_boundary"]
        self.assertEqual(capture["registered_execution_invocations"], 1)
        self.assertTrue(capture["returned_aggregate_JSON_captured"])
        for key, value in capture.items():
            if key not in {
                "registered_execution_invocations",
                "returned_aggregate_JSON_captured",
            }:
                self.assertEqual(value, 0, key)
        self.assertFalse(REGISTRY["route_interpretation"]["cohort_frozen"])
        self.assertFalse(
            REGISTRY["next_gate"][
                "VR39P_retry_rerun_resume_repair_or_reinspection_allowed"
            ]
        )

    def test_withheld_execution_details_remain_unavailable(self):
        unavailable = set(REGISTRY["unavailable_measurements_by_public_contract"])
        self.assertIn("readiness_samples_or_values", unavailable)
        self.assertIn("source_preflight_open_parse_or_byte_counts", unavailable)
        self.assertIn("failure_stage_or_exception", unavailable)
        self.assertIn("runtime_seconds", unavailable)
        self.assertIn("peak_RSS_bytes", unavailable)
        self.assertIn("private_count_identity_topology_rows_or_sizes", unavailable)

    def test_human_result_preserves_engineering_and_scientific_boundary(self):
        self.assertIn("Consumed at aggregate R2", DOC)
        self.assertIn("does not reveal whether readiness", DOC)
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)


if __name__ == "__main__":
    unittest.main()
