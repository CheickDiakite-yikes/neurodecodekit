from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v5.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v4.json"
LEDGER = ROOT / "registries/scientific_knowledge_ledger.v0.json"


class CurrentResearchFrontierV5Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.ledger = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_additive_successor_and_green_chain_are_exact(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.6.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        chain = self.frontier["green_packet_chain"]
        self.assertEqual(
            chain["request_commit"], "af9d0247bb816c3432a9eb407fadcd286f84d87c"
        )
        self.assertEqual(
            chain["proof_commit"], "2c313d57ca3acebeea985fb788593be88877f68e"
        )
        self.assertEqual(chain["proof_CI_run_id"], 33_273_777_182)
        self.assertTrue(chain["all_named_jobs_green"])

    def test_packet_is_active_only_for_a_fresh_decision(self) -> None:
        self.assertEqual(self.frontier["active_lane_id"], "OFNER-C6R-1-HL")
        boundary = self.frontier["operation_boundary"]
        self.assertEqual(boundary["active_tier_c_packet"], "OFNER-C6R-1-HL")
        self.assertTrue(boundary["all_operation_authority_flags_false"])
        self.assertTrue(
            all(
                value is False
                for value in self.frontier["operation_authority"].values()
            )
        )
        scope = self.frontier["active_packet_scope"]
        self.assertFalse(scope["decision_record_exists"])
        self.assertFalse(scope["implementation_exists"])
        self.assertFalse(scope["real_operation_authorized"])
        next_gate = self.frontier["next_gate"]
        self.assertFalse(next_gate["earlier_continue_or_general_approval_retroactive"])
        self.assertFalse(next_gate["real_data_authority_created_by_this_transition"])

    def test_claim_boundary_remains_negative(self) -> None:
        claims = self.frontier["claim_boundary"]
        proven_engineering = {
            "source_selection_complete",
            "generated_acquisition_engineering_proven",
            "generated_header_engineering_proven",
        }
        for key, value in claims.items():
            self.assertEqual(value, key in proven_engineering, key)

    def test_knowledge_ledger_matches_current_packet(self) -> None:
        boundary = self.ledger["operation_boundary"]
        self.assertEqual(boundary["active_tier_c_packet"], "OFNER-C6R-1-HL")
        self.assertTrue(boundary["all_authority_flags_false"])

    def test_current_control_plane_names_v5_and_fresh_decision(self) -> None:
        expected = {
            "AGENTS.md": "registries/current_research_frontier.v5.json",
            "README.md": "registries/current_research_frontier.v5.json",
            "START_HERE.md": "registries/current_research_frontier.v5.json",
            "docs/CODEX_HANDOFF.md": "registries/current_research_frontier.v5.json",
        }
        for path, phrase in expected.items():
            text = (ROOT / path).read_text(encoding="utf-8")[:12_000]
            self.assertIn(phrase, text, path)
            normalized = text.replace("\n> ", " ").replace("\n", " ")
            self.assertIn("fresh packet-bound", normalized, path)


if __name__ == "__main__":
    unittest.main()
