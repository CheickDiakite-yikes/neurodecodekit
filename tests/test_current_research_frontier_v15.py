from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v15.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v14.json"
CORRECTION = (
    ROOT
    / "registries/fresh_motor_source_discovery_admission_correction.v0.json"
)


class CurrentResearchFrontierV15Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
        cls.correction = json.loads(CORRECTION.read_text(encoding="utf-8"))

    def test_predecessor_is_exactly_bound(self) -> None:
        payload = PREDECESSOR.read_bytes()
        self.assertEqual(
            hashlib.sha256(payload).hexdigest(),
            self.frontier["superseded_registry_sha256"],
        )
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v14.json",
        )

    def test_proof_closeout_is_exact_green(self) -> None:
        proof = self.frontier["green_proof_only_closeout"]
        self.assertEqual(
            proof["commit"], "fac60bfafaa6414da82b075fa677e2aa31c80e22"
        )
        self.assertEqual(proof["CI_run_id"], 33_338_847_448)
        self.assertEqual(proof["base_python_job_id"], 99_330_615_390)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99_330_615_564)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertTrue(proof["on_GitHub_main"])
        self.assertFalse(proof["contacts_public_source"])
        self.assertFalse(proof["creates_live_execution_authority"])

    def test_evidence_architecture_and_coordinate_are_unchanged(self) -> None:
        self.assertEqual(
            self.frontier["scientific_evidence_architecture"],
            self.predecessor["scientific_evidence_architecture"],
        )
        self.assertEqual(
            self.frontier["current_evidence_coordinate"],
            self.predecessor["current_evidence_coordinate"],
        )

    def test_correction_is_all_false_and_not_an_active_packet(self) -> None:
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        correction = self.frontier["all_false_admission_correction"]
        self.assertEqual(correction["correction_id"], self.correction["correction_id"])
        self.assertFalse(correction["current_M0_rearmed"])
        self.assertFalse(correction["all_five_revision_or_snapshot_profiles_bound"])
        self.assertFalse(correction["external_CI_witness_profile_bound"])
        self.assertFalse(correction["network_or_protected_authority_created"])

    def test_only_strategy_correction_commit_and_CI_are_open(self) -> None:
        authority = self.frontier["operation_authority_now"]
        self.assertTrue(authority["strategy_correction_commit_and_CI"])
        for key, value in authority.items():
            if key != "strategy_correction_commit_and_CI":
                self.assertFalse(value, key)

    def test_claims_and_real_operations_remain_false(self) -> None:
        for key, value in self.frontier["claim_boundary"].items():
            self.assertFalse(value, key)
        park = self.frontier["park_reason"]
        self.assertTrue(park["execute_refuses_before_DNS_or_HTTP"])
        self.assertEqual(park["metadata_execution_attempts"], 0)
        self.assertEqual(park["public_metadata_requests"], 0)


if __name__ == "__main__":
    unittest.main()
