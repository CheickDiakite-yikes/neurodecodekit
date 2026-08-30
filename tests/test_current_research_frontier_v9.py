from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v9.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v8.json"
CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v0.json"


class CurrentResearchFrontierV9Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_frontier_is_exact_additive_successor(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.10.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        self.assertTrue(CONTRACT.is_file())
        self.assertIsNone(self.frontier["active_lane_id"])

    def test_NPA1_proof_closeout_is_exact_green(self) -> None:
        proof = self.frontier["NPA1_G_proof_closeout"]
        self.assertEqual(
            proof["commit"], "2ec3d4b2b7b8c51f246e948ce9cbc9d667cecfb5"
        )
        self.assertEqual(proof["CI_run_id"], 33_285_776_358)
        self.assertEqual(proof["base_python_job_id"], 99_188_620_896)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99_188_621_003)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_registration_is_strict_and_no_source_is_selected(self) -> None:
        registration = self.frontier["fresh_source_registration"]
        self.assertEqual(registration["protocol_id"], "FMSR1-v0")
        self.assertIsNone(registration["candidate_selected"])
        self.assertEqual(registration["minimum_complete_participants"], 10)
        self.assertTrue(registration["recorded_EOG_required"])
        self.assertTrue(registration["task_relevant_EMG_required"])
        self.assertFalse(registration["kinematics_substitutes_for_EMG"])
        self.assertEqual(registration["selected_payload_cap_bytes"], 16 * 2**30)
        self.assertEqual(registration["total_incremental_disk_cap_bytes"], 20 * 2**30)

    def test_only_next_artifact_packet_is_authorized(self) -> None:
        authority = self.frontier["operation_authority"]
        self.assertTrue(authority["artifact_only_source_research_authorization_packet"])
        for key, value in authority.items():
            if key != "artifact_only_source_research_authorization_packet":
                self.assertFalse(value, key)
        self.assertFalse(
            self.frontier["next_gate"]["source_specific_network_request_authorized"]
        )

    def test_claim_boundary_separates_rules_from_evidence(self) -> None:
        boundary = self.frontier["claim_boundary"]
        self.assertTrue(boundary["generated_transport_admission_proven"])
        self.assertTrue(boundary["fresh_source_admission_rules_frozen_after_remote_green"])
        for key, value in boundary.items():
            if key not in {
                "generated_transport_admission_proven",
                "fresh_source_admission_rules_frozen_after_remote_green",
            }:
                self.assertFalse(value, key)

    def test_v9_is_preserved_as_the_unaccepted_predecessor(self) -> None:
        successor = ROOT / "registries/current_research_frontier.v10.json"
        self.assertTrue(successor.is_file())
        self.assertIn("pending_remote_green", self.frontier["status"])
        self.assertEqual(self.frontier["fresh_source_registration"]["protocol_id"], "FMSR1-v0")


if __name__ == "__main__":
    unittest.main()
