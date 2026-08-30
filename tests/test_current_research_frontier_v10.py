from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v10.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v9.json"
CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v1.json"


class CurrentResearchFrontierV10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_v10_is_exact_additive_successor(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.11.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        self.assertTrue(CONTRACT.is_file())
        self.assertIsNone(self.frontier["active_lane_id"])

    def test_v0_is_unaccepted_and_v1_is_current(self) -> None:
        draft = self.frontier["unaccepted_v0_draft"]
        self.assertFalse(draft["accepted_as_scientific_registration"])
        self.assertEqual(draft["protected_operations"], 0)
        current = self.frontier["current_registration"]
        self.assertEqual(current["protocol_id"], "FMSR1-v1")
        self.assertIsNone(current["candidate_selected"])
        self.assertTrue(current["joint_nuisance_comparators_required"])
        self.assertTrue(current["EMG_for_every_relevant_effector_required"])
        self.assertTrue(current["exact_metadata_eligibility_predicate_required"])
        self.assertTrue(current["deterministic_total_candidate_order_required"])
        self.assertFalse(current["partial_or_truncated_discovery_may_select_candidate"])
        self.assertEqual(current["storage_component_sum_bytes"], 20 * 2**30)
        self.assertEqual(current["future_discovery_packet_maximum_requests"], 128)
        self.assertEqual(
            current["future_discovery_packet_maximum_response_body_bytes"],
            32 * 2**20,
        )
        self.assertEqual(current["future_discovery_packet_retry_count"], 0)

    def test_every_current_operation_authority_is_false(self) -> None:
        for key, value in self.frontier["operation_authority"].items():
            self.assertFalse(value, key)
        next_gate = self.frontier["conditional_next_gate"]
        self.assertFalse(next_gate["describes_present_authority"])
        self.assertFalse(next_gate["network_request_authorized"])

    def test_claim_boundary_separates_rules_from_evidence(self) -> None:
        boundary = self.frontier["claim_boundary"]
        self.assertTrue(boundary["generated_transport_admission_proven"])
        self.assertTrue(boundary["FMSR1_v1_rules_frozen_after_exact_remote_green"])
        for key, value in boundary.items():
            if key not in {
                "generated_transport_admission_proven",
                "FMSR1_v1_rules_frozen_after_exact_remote_green",
            }:
                self.assertFalse(value, key)

    def test_current_control_plane_names_v10_and_v1_without_stale_Ofner_next(self) -> None:
        paths = (
            "AGENTS.md",
            "README.md",
            "START_HERE.md",
            "docs/CODEX_HANDOFF.md",
            "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md",
        )
        for relative in paths:
            text = (ROOT / relative).read_text(encoding="utf-8")[:20_000]
            self.assertIn("current_research_frontier.v10.json", text, relative)
            self.assertIn("FMSR1-v1", text, relative)
        readme = (ROOT / "README.md").read_text(encoding="utf-8")[:20_000]
        plan = (
            ROOT / "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md"
        ).read_text(encoding="utf-8")[:20_000]
        self.assertNotIn("The next real checkpoint is", readme)
        self.assertNotIn("The next prospective flagship is `OFNER-C6R-1`", plan)


if __name__ == "__main__":
    unittest.main()
