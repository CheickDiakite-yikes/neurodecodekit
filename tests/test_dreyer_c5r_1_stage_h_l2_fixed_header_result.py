import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h_l2 as hl2


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / hl2.PUBLIC_RESULT_RELATIVE_PATH
CLOSEOUT = ROOT / (
    "registries/dreyer_c5r_1_stage_h_l2_fixed_header_result_closeout.v0.json"
)
DOCUMENT = ROOT / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_RESULT_CLOSEOUT.md"
FRONTIER = ROOT / "registries/current_research_frontier.v1.json"


class DreyerStageHL2FixedHeaderResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = hl2.inspect_public_result(RESULT)
        cls.closeout = json.loads(CLOSEOUT.read_text(encoding="utf-8"))

    def test_exact_consumed_H0_result_is_bound(self):
        bound = self.closeout["bound_public_result"]
        self.assertEqual(RESULT.stat().st_size, 2_624)
        self.assertEqual(
            hashlib.sha256(RESULT.read_bytes()).hexdigest(), bound["sha256"]
        )
        self.assertEqual(self.result["route"], "DREYER-H0")
        self.assertEqual(self.result["refusal_code"], "HL2-TRANSPORT")
        self.assertTrue(self.closeout["result"]["invocation_consumed"])
        self.assertFalse(self.closeout["result"]["retry_allowed"])
        self.assertFalse(self.closeout["result"]["rerun_allowed"])

    def test_additive_current_frontier_preserves_v0_proof_surface(self):
        binding = self.closeout["current_frontier"]
        self.assertEqual(FRONTIER.stat().st_size, binding["bytes"])
        self.assertEqual(
            hashlib.sha256(FRONTIER.read_bytes()).hexdigest(),
            binding["sha256"],
        )
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        self.assertEqual(frontier["active_lane_id"], "NO_ACTIVE_TIER_C_GATE")
        self.assertEqual(frontier["supersedes"], binding["supersedes"])
        self.assertEqual(
            frontier["superseded_registry_sha256"],
            binding["superseded_registry_sha256"],
        )

    def test_transport_refused_before_any_EDF_body_or_header_read(self):
        counters = self.result["operation_counters"]
        self.assertEqual(counters["real_HTTP_GET_requests"], 1)
        self.assertEqual(counters["real_response_opens"], 1)
        for key in (
            "real_network_body_bytes",
            "real_payload_SHA256_passes",
            "real_fixed_header_reads",
            "real_fixed_header_semantic_parses",
            "annotation_semantic_reads",
            "signal_sample_semantic_reads",
            "target_or_label_reads",
            "model_runs",
            "training_runs",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertIsNone(self.result["sensor_contract"])
        self.assertFalse(self.result["geometry_available"])
        self.assertFalse(self.result["teardown"]["payload_retained"])
        self.assertTrue(self.result["teardown"]["cleanup_complete"])

    def test_resources_claims_and_closeout_boundary_are_exact(self):
        resources = self.result["resources"]
        self.assertLessEqual(resources["peak_process_tree_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(resources["runtime_seconds"], 300)
        self.assertEqual(set(self.result["claim_boundary"].values()), {False})
        self.assertEqual(
            set(self.closeout["closeout_operation_counters"].values()), {0}
        )
        self.assertEqual(set(self.closeout["claim_boundary"].values()), {False})
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("Claiming a more specific cause would invent evidence.", text)


if __name__ == "__main__":
    unittest.main()
