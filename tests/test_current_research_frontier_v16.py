from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v16.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v15.json"
CONTRACT = (
    ROOT
    / "registries/fresh_motor_source_admission_generated_qualification_contract.v0.json"
)


class CurrentResearchFrontierV16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_predecessor_is_exactly_bound(self) -> None:
        self.assertEqual(
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
            self.frontier["superseded_registry_sha256"],
        )
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v15.json",
        )

    def test_evidence_architecture_and_coordinate_are_unchanged(self) -> None:
        self.assertEqual(
            self.frontier["scientific_evidence_architecture"],
            self.predecessor["scientific_evidence_architecture"],
        )
        self.assertEqual(
            self.frontier["current_evidence_coordinate"],
            self.predecessor["current_evidence_coordinate"],
        )

    def test_correction_is_exact_green_without_rearming_M0(self) -> None:
        correction = self.frontier["green_admission_correction"]
        self.assertEqual(
            correction["exact_green_state_commit"],
            "8fe98df7e08e7e1e40860e6023832c3b092d78d2",
        )
        self.assertEqual(correction["main_CI_run_id"], 33_340_527_773)
        self.assertTrue(correction["both_required_main_jobs_green"])
        self.assertFalse(correction["current_M0_rearmed"])
        self.assertFalse(correction["network_or_protected_authority_created"])

    def test_R1_G_is_registered_but_not_implemented_or_run(self) -> None:
        registration = self.frontier["R1_G_generated_only_preregistration"]
        self.assertEqual(registration["protocol_id"], self.contract["protocol_id"])
        self.assertEqual(registration["named_refusal_mutations"], 82)
        self.assertFalse(registration["network_client_present"])
        self.assertFalse(registration["live_command_present"])
        self.assertFalse(registration["implementation_started"])
        self.assertEqual(registration["qualification_runs"], 0)

    def test_only_registration_commit_and_CI_are_open_now(self) -> None:
        authority = self.frontier["operation_authority_now"]
        self.assertTrue(authority["R1_G_registration_commit_push_and_CI"])
        for key, value in authority.items():
            if key != "R1_G_registration_commit_push_and_CI":
                self.assertFalse(value, key)

    def test_no_Tier_C_packet_or_scientific_claim_is_active(self) -> None:
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        for key, value in self.frontier["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.frontier["next_gate"]["network_request_authorized_now"])
        self.assertTrue(
            self.frontier["next_gate"][
                "fresh_exact_Tier_C_decision_required_before_any_GitHub_or_source_contact"
            ]
        )


if __name__ == "__main__":
    unittest.main()
