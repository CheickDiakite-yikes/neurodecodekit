from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v22.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v21.json"


class CurrentResearchFrontierV22Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_predecessor_identity_is_exact(self) -> None:
        self.assertEqual(self.frontier["supersedes"], PREDECESSOR.relative_to(ROOT).as_posix())
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )

    def test_green_packet_and_pending_decision_are_distinct(self) -> None:
        packet = self.frontier["green_packet"]
        self.assertEqual(packet["packet_id"], "FMSR1-R1-W-v0")
        self.assertTrue(packet["both_required_jobs_green"])
        self.assertEqual(packet["official_index_profiles"], 5)
        self.assertEqual(packet["root_request_identities"], 17)
        decision = self.frontier["implementation_decision"]
        self.assertEqual(decision["decision_id"], "FMSR1-R1-W-I0-D0")
        self.assertEqual(decision["status"], "pending_this_exact_commit_and_remote_proof")
        self.assertTrue(decision["generated_implementation_after_decision_green"])
        self.assertFalse(decision["live_network_or_witness"])

    def test_live_and_scientific_authority_remain_false(self) -> None:
        authority = self.frontier["operation_authority_now"]
        self.assertFalse(authority["generated_implementation_before_decision_green"])
        self.assertFalse(authority["GitHub_API_or_official_index_network"])
        self.assertFalse(authority["candidate_parsing_ranking_or_selection"])
        self.assertFalse(authority["real_payload_header_signal_event_annotation_target_or_label"])
        self.assertFalse(authority["model_training_inference_prediction_or_score"])
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))

    def test_next_gate_is_generated_implementation_not_live_contact(self) -> None:
        gate = self.frontier["next_gate"]
        self.assertIn("generated_witness", gate["action"])
        self.assertTrue(gate["fresh_second_execution_bound_words_required_after_implementation_green"])
        self.assertFalse(gate["network_request_authorized_now"])
        self.assertFalse(gate["real_data_transaction_authorized"])
        self.assertFalse(gate["model_or_scoring_authorized"])


if __name__ == "__main__":
    unittest.main()
