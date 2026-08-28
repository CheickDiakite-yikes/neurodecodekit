from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/communication_eeg_triangulated_replication_refresh_proof.v0.json"
)
DOCUMENT = (
    ROOT / "docs/COMMUNICATION_EEG_TRIANGULATED_REPLICATION_REFRESH_PROOF_CLOSEOUT.md"
)


class CommunicationEEGTriangulatedReplicationRefreshProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_refresh_commit_is_remotely_green_and_on_main(self) -> None:
        green = self.proof["green_refresh_commit"]
        self.assertEqual(
            green["commit"], "85400fe13a87d82916a8338709239764b621c5c1"
        )
        self.assertEqual(green["CI_run_id"], 33_128_665_324)
        self.assertEqual(green["base_python_job_id"], 98_712_772_971)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_712_773_150)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["working_branch_matches_exact_commit"])
        self.assertTrue(green["GitHub_main_matches_exact_commit"])

    def test_exact_refresh_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_refresh_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_refresh_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 23_934)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_changes_no_authority_or_claim(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["source_refresh_artifacts_unchanged"])
        self.assertTrue(scope["parent_replication_contract_unchanged"])
        self.assertTrue(scope["original_source_refresh_unchanged"])
        self.assertTrue(scope["objective_evidence_decision_unchanged"])
        self.assertTrue(scope["consumed_generated_lanes_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["active_Tier_C_gate_changed"])
        self.assertFalse(scope["claim_boundary_changed"])

        transition = self.proof["transition"]
        self.assertFalse(transition["metadata_operation_authorized_by_closeout"])
        self.assertFalse(transition["payload_operation_authorized_by_closeout"])
        self.assertTrue(transition["fresh_Tier_C_packet_and_decision_required"])
        self.assertTrue(transition["DREYER_C5R_1_HL_remains_sole_active_Tier_C_packet"])
        self.assertTrue(
            transition["all_DREYER_C5R_1_HL_authority_flags_remain_false"]
        )

    def test_only_proof_metadata_reads_are_nonzero(self) -> None:
        counters = self.proof["operation_counters"]
        allowed = {
            "tracked_artifact_reads": 3,
            "Git_proof_reads": 3,
            "GitHub_CI_metadata_reads": 1,
            "GitHub_ref_reads": 1,
        }
        for key, value in counters.items():
            self.assertEqual(value, allowed.get(key, 0), key)

    def test_document_states_capability_nonclaim_and_next_gate(self) -> None:
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["independent_replication_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
