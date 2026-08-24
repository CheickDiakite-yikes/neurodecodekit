import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/eegmmidb_unseen_participant_generalization_request_proof.v0.json"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_REQUEST_PROOF_CLOSEOUT.md"


class EEGMMIDBUnseenParticipantGeneralizationRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_green_request_is_bound(self):
        green = self.proof["request_green_proof"]
        self.assertEqual(green["commit"], "c642d90b646ff32c6d83e648f7d7779810605e11")
        self.assertEqual(green["CI_run_id"], 32690289547)
        self.assertEqual(green["base_python_job_id"], 97322606634)
        self.assertEqual(green["optional_neuro_job_id"], 97322606501)
        self.assertTrue(green["both_required_jobs_green"])

    def test_artifact_hashes_sizes_and_git_blobs_are_exact(self):
        rows = self.proof["artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["artifact_summary"]
        self.assertEqual(summary["count"], 9)
        self.assertEqual(summary["bytes"], sum(row["bytes"] for row in rows))
        self.assertEqual(
            summary["canonical_artifact_set_sha256"], hashlib.sha256(canonical).hexdigest()
        )

    def test_proof_changes_no_scope_and_grants_no_authority(self):
        self.assertTrue(all(self.proof["scope_unchanged"].values()))
        self.assertTrue(
            all(value is False for value in self.proof["current_authorization_flags"].values())
        )
        counters = self.proof["proof_operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 9)
        self.assertEqual(counters["Git_proof_reads"], 9)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_next_gate_requires_closeout_green_then_fresh_message(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["closeout_commit_push_and_both_CI_jobs_green_required"])
        self.assertFalse(
            gate["sole_active_Tier_C_packet_identification_allowed_before_closeout_green"]
        )
        self.assertTrue(gate["fresh_packet_bound_maintainer_message_required_after_identification"])
        self.assertFalse(gate["current_or_earlier_continue_is_retroactive"])
        self.assertFalse(gate["any_real_or_generated_stage_authorized_now"])

    def test_document_preserves_scientific_boundary(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Proof-only closeout", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("no real-data access", document)


if __name__ == "__main__":
    unittest.main()
