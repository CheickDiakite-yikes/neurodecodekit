from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v23.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v22.json"


class CurrentResearchFrontierV23Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_predecessor_identity_is_exact(self) -> None:
        self.assertEqual(self.frontier["supersedes"], PREDECESSOR.relative_to(ROOT).as_posix())
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )

    def test_green_decision_and_pending_implementation_are_distinct(self) -> None:
        decision = self.frontier["green_implementation_decision"]
        self.assertEqual(decision["decision_id"], "FMSR1-R1-W-I0-D0")
        self.assertTrue(decision["both_required_jobs_green"])
        implementation = self.frontier["generated_implementation"]
        self.assertEqual(implementation["implementation_id"], "FMSR1-R1-W-I0")
        self.assertTrue(implementation["qualification_passed"])
        self.assertTrue(implementation["qualification_consumed"])
        self.assertEqual(implementation["status"], "pending_this_exact_commit_and_remote_proof")
        self.assertFalse(implementation["live_network_or_witness"])

    def test_next_gate_is_remote_proof_then_fresh_execution_words(self) -> None:
        gate = self.frontier["next_gate"]
        self.assertIn("green_exact_generated_witness", gate["action"])
        self.assertFalse(gate["fresh_maintainer_words_required_before_commit_and_CI"])
        self.assertTrue(gate["fresh_second_execution_bound_words_required_after_implementation_green"])
        self.assertFalse(gate["network_request_authorized_now"])
        self.assertFalse(gate["real_data_transaction_authorized"])
        self.assertFalse(gate["model_or_scoring_authorized"])

    def test_no_scientific_claim_is_upgraded(self) -> None:
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))
        authority = self.frontier["operation_authority_now"]
        self.assertFalse(authority["repeat_generated_qualification"])
        self.assertFalse(authority["GitHub_API_or_official_index_network"])
        self.assertFalse(authority["real_payload_header_signal_event_annotation_target_or_label"])
        self.assertFalse(authority["model_training_inference_prediction_or_score"])


if __name__ == "__main__":
    unittest.main()
