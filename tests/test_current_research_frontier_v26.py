from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v26.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v25.json"


class CurrentResearchFrontierV26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_predecessor_identity_is_exact(self) -> None:
        self.assertEqual(self.frontier["supersedes"], PREDECESSOR.relative_to(ROOT).as_posix())
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )

    def test_exact_green_implementation_is_recorded(self) -> None:
        implementation = self.frontier["green_live_implementation"]
        self.assertEqual(
            implementation["commit"], "a2af6c4c016a81652b3c1bae13d8c8e5e56ef4e9"
        )
        self.assertTrue(implementation["both_required_jobs_green"])
        self.assertTrue(implementation["on_GitHub_main"])
        self.assertTrue(implementation["qualification_consumed"])
        self.assertFalse(implementation["qualification_replay_allowed"])
        self.assertFalse(implementation["real_source_access"])

    def test_proof_is_pending_its_own_remote_gate(self) -> None:
        proof = self.frontier["implementation_proof_closeout"]
        self.assertEqual(proof["proof_id"], "FMSR1-R1-W-I1-P0")
        self.assertEqual(proof["bound_artifact_count"], 16)
        self.assertEqual(proof["bound_artifact_bytes"], 314_356)
        self.assertIn("pending", proof["status"])

    def test_next_gate_requires_fresh_words_after_proof(self) -> None:
        authority = self.frontier["operation_authority_now"]
        self.assertFalse(authority["fresh_execution_bound_maintainer_words_present"])
        self.assertFalse(authority["create_execution_decision_now"])
        self.assertFalse(authority["GitHub_CI_W0_or_official_index_network"])
        self.assertFalse(authority["live_source_identity_witness"])
        gate = self.frontier["next_gate"]
        self.assertTrue(gate["fresh_execution_bound_words_required_after_proof_green"])
        self.assertFalse(gate["network_request_authorized_now"])
        self.assertFalse(gate["real_data_transaction_authorized"])

    def test_no_scientific_claim_is_upgraded(self) -> None:
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
