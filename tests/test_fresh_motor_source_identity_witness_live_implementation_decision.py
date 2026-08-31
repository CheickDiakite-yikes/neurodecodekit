from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = ROOT / "registries/fresh_motor_source_identity_witness_live_implementation_decision.v0.json"
FRONTIER_PATH = ROOT / "registries/current_research_frontier.v24.json"


class FreshMotorSourceIdentityWitnessLiveImplementationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))

    def test_actual_words_and_boundary_are_exact(self) -> None:
        words = self.decision["maintainer_words"].encode("utf-8")
        self.assertEqual(words, b"get needle moving, eureka results")
        self.assertEqual(self.decision["maintainer_words_utf8_bytes"], len(words))
        self.assertEqual(
            self.decision["maintainer_words_sha256"], hashlib.sha256(words).hexdigest()
        )
        authority = self.decision["authorization_after_decision_green"]
        self.assertTrue(authority["additive_standard_library_live_executor"])
        self.assertTrue(authority["generated_transport_and_refusal_fixtures"])
        self.assertTrue(authority["generated_qualification_once"])
        self.assertFalse(authority["GitHub_API_or_official_index_contact"])
        self.assertFalse(authority["live_source_identity_witness"])
        self.assertFalse(authority["release_or_scientific_claim_upgrade"])

    def test_bound_artifacts_match_bytes_hashes_and_git_blobs(self) -> None:
        for row in self.decision["bound_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(row["bytes"], len(payload))
            self.assertEqual(row["sha256"], hashlib.sha256(payload).hexdigest())
            blob = subprocess.run(
                ["git", "hash-object", "--stdin"],
                cwd=ROOT,
                input=payload,
                check=True,
                capture_output=True,
            ).stdout.decode("ascii").strip()
            self.assertEqual(row["git_blob"], blob)

    def test_frontier_preserves_zero_evidence_and_orders_the_barrier(self) -> None:
        self.assertEqual(self.frontier["active_lane_id"], "FMSR1-R1-W-I1-D0")
        self.assertFalse(
            self.frontier["operation_authority_now"]["GitHub_API_or_official_index_network"]
        )
        self.assertTrue(
            self.frontier["next_gate"]["fresh_execution_bound_words_required_after_live_implementation_green"]
        )
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
