from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v11.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v10.json"


class CurrentResearchFrontierV11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_v11_exactly_supersedes_v10(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.12.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )

    def test_registration_is_green_and_request_is_all_false(self) -> None:
        green = self.frontier["green_registration"]
        self.assertEqual(green["commit"], "e09f6cc014744485940713c148dacad9dbbe59e3")
        self.assertTrue(green["both_required_jobs_green"])
        request = self.frontier["queued_all_false_request"]
        self.assertEqual(request["packet_id"], "FMSR1-DISCOVERY-M0")
        self.assertFalse(request["request_grants_authority"])
        self.assertTrue(request["fresh_packet_bound_maintainer_words_required_after_remote_green"])
        self.assertIsNone(self.frontier["active_lane_id"])

    def test_every_current_operation_authority_is_false(self) -> None:
        for key, value in self.frontier["operation_authority"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.frontier["next_gate"]["describes_present_authority"])

    def test_current_documents_name_v11_and_packet(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "START_HERE.md",
            "docs/CODEX_HANDOFF.md",
            "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")[:22_000]
            self.assertIn("current_research_frontier.v11.json", text, relative)
            self.assertIn("FMSR1-DISCOVERY-M0", text, relative)

    def test_current_strategy_cannot_reactivate_consumed_dreyer_or_ofner(self) -> None:
        plan = (
            ROOT / "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("**Current gate:** `DREYER", plan)
        self.assertNotIn("**Current gate:** `OFNER", plan)
        self.assertNotIn("may bind only its unchanged H-L1", plan)
        self.assertIn("historical and inert", plan)
        self.assertIn("No Dreyer or Ofner Tier C gate is active", plan)
        self.assertNotIn("separately decided `FMSR1-DISCOVERY-M0`", plan)
        self.assertIn("pending-decision `FMSR1-DISCOVERY-M0`", plan)


if __name__ == "__main__":
    unittest.main()
