from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_implementation_safety_review.v0.json"
)
DOC_PATH = ROOT / "docs/DREYER_C5R_1_STAGE_H_LIVE_IMPLEMENTATION_SAFETY_REVIEW.md"
FRONTIER_PATH = ROOT / "registries/current_research_frontier.v0.json"


class DreyerStageHLiveImplementationSafetyReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.review = json.loads(REGISTRY_PATH.read_bytes())
        cls.document = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_and_static_only_status_are_exact(self) -> None:
        self.assertEqual(
            self.review["schema_name"],
            "neurodecodekit.dreyer_c5r_1_stage_h_live_implementation_safety_review",
        )
        self.assertEqual(self.review["lane_id"], "DREYER-C5R-1-HL")
        self.assertEqual(
            self.review["status"], "pre_decision_static_review_no_authority_change"
        )

    def test_qualified_artifacts_remain_byte_identical(self) -> None:
        for artifact in self.review["reviewed_artifacts"]:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            with self.subTest(path=artifact["path"]):
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_only_static_review_authority_is_true(self) -> None:
        authority = dict(self.review["authority"])
        self.assertTrue(authority.pop("record_static_review"))
        self.assertTrue(all(value is False for value in authority.values()))
        self.assertTrue(all(value == 0 for value in self.review["operation_counters"].values()))

    def test_additive_wrapper_controls_close_identified_hazards(self) -> None:
        controls = set(self.review["required_wrapper_controls"])
        self.assertEqual(len(controls), 9)
        for expected in (
            "durable_exclusive_nofollow_consumed_marker_before_opener",
            "capability_safe_non_symlink_path_chain",
            "private_staging_and_atomic_no_replace_promotion",
            "bounded_deterministically_closed_response",
            "continuous_resource_and_operation_ledger_enforcement",
            "fixed_header_record_geometry_matches_exact_payload_bytes",
        ):
            self.assertIn(expected, controls)

    def test_scientific_ladder_reaches_score_replication_then_streaming(self) -> None:
        ladder = self.review["evidence_ladder"]
        self.assertEqual(ladder[0], "HL1_generated_live_wrapper_qualification_and_green_activation")
        self.assertIn("T_one_frozen_score", ladder)
        self.assertEqual(ladder[-1], "prospective_streaming_only_after_replication")

    def test_current_frontier_binds_the_exact_review(self) -> None:
        frontier = json.loads(FRONTIER_PATH.read_bytes())
        binding = frontier["fresh_replication"]["active_Tier_C_packet"][
            "pre_implementation_safety_review"
        ]
        for path, prefix in ((DOC_PATH, "document"), (REGISTRY_PATH, "registry")):
            payload = path.read_bytes()
            self.assertEqual(binding[f"{prefix}_bytes"], len(payload))
            self.assertEqual(binding[f"{prefix}_sha256"], hashlib.sha256(payload).hexdigest())
        self.assertFalse(binding["authority_change"])
        self.assertEqual(binding["real_or_private_operations"], 0)

    def test_document_is_explicit_about_value_and_claim_boundary(self) -> None:
        for statement in (
            "14,805,604 bytes",
            "Q -> P -> T is the scientific center",
            "This review does not authorize H-L1 implementation",
            "It would not establish spontaneous intention",
        ):
            self.assertIn(statement, self.document)


if __name__ == "__main__":
    unittest.main()
