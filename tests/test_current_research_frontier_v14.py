from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "registries/current_research_frontier.v14.json"
PREVIOUS = ROOT / "registries/current_research_frontier.v13.json"


class CurrentResearchFrontierV14Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(CURRENT.read_text(encoding="utf-8"))

    def test_exactly_supersedes_immutable_v13(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v13.json",
        )
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
        )

    def test_generated_implementation_is_exact_green(self) -> None:
        implementation = self.frontier["green_generated_implementation"]
        self.assertEqual(
            implementation["commit"],
            "e92e9c21a044b05a187a04812f21e7e7bd5a76b6",
        )
        self.assertEqual(implementation["CI_run_id"], 33_337_741_165)
        self.assertEqual(implementation["bound_artifact_count"], 6)
        self.assertEqual(implementation["bound_artifact_bytes"], 162_295)
        self.assertEqual(implementation["real_network_requests"], 0)
        self.assertFalse(implementation["scientific_value"])

    def test_architecture_keeps_attribution_evidence_and_translation_distinct(self) -> None:
        architecture = self.frontier["scientific_evidence_architecture"]
        self.assertEqual(len(architecture["attribution_cube_dimensions_1_to_3"]), 3)
        self.assertEqual(len(architecture["outer_evidence_dimensions_4_to_5"]), 2)
        self.assertEqual(
            architecture["translation_dimension_6"],
            ["offline_evaluation", "causal_replay", "shadow_stream", "prospective_live"],
        )
        self.assertFalse(architecture["no_signal_win_alone_establishes_attribution"])
        self.assertFalse(
            architecture["translation_can_rescue_failed_attribution_or_evidence_dimension"]
        )
        self.assertFalse(architecture["live_motor_success_validates_language_decoding"])

    def test_closeout_is_proof_only_and_live_route_remains_parked(self) -> None:
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        closeout = self.frontier["proof_only_closeout"]
        self.assertFalse(closeout["repeats_generated_qualification"])
        self.assertFalse(closeout["contacts_public_source"])
        self.assertFalse(closeout["creates_live_execution_authority"])
        park = self.frontier["park_reason"]
        self.assertFalse(park["live_execution_armable_under_current_packet"])
        self.assertTrue(park["execute_refuses_before_DNS_or_HTTP"])
        self.assertEqual(park["metadata_execution_attempts"], 0)

    def test_only_proof_commit_and_CI_are_currently_open(self) -> None:
        authority = self.frontier["operation_authority_now"]
        self.assertTrue(authority["proof_only_closeout_commit_and_CI"])
        for key, value in authority.items():
            if key != "proof_only_closeout_commit_and_CI":
                self.assertFalse(value, key)
        self.assertFalse(any(self.frontier["claim_boundary"].values()))
        next_gate = self.frontier["next_gate"]
        self.assertFalse(next_gate["network_request_authorized_now"])
        self.assertTrue(next_gate["fresh_exact_decision_required_before_public_contact"])


if __name__ == "__main__":
    unittest.main()
