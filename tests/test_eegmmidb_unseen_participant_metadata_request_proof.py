import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/eegmmidb_unseen_participant_metadata_request_proof.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_REQUEST_PROOF_CLOSEOUT.md"


class EEGMMIDBUnseenParticipantMetadataRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_request_commit_is_remotely_green(self):
        green = self.proof["green_request_commit"]
        self.assertEqual(
            green["commit"], "e2647d609a99997ac417dac5d8efb2dad61863a0"
        )
        self.assertEqual(green["CI_run_id"], 32709110804)
        self.assertEqual(green["base_python_job_id"], 97376524550)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97376524804)
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_request_artifacts_are_hash_size_and_git_bound(self):
        rows = self.proof["bound_request_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_request_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 20189)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_scope_is_unchanged_and_closeout_authorizes_nothing(self):
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["request_artifacts_unchanged"])
        self.assertTrue(scope["paths_participants_runs_dataset_and_order_unchanged"])
        self.assertTrue(scope["HEAD_only_zero_body_zero_redirect_zero_retry_contract_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])
        transition = self.proof["transition"]
        self.assertFalse(transition["implementation_authorized_by_closeout"])
        self.assertFalse(transition["network_or_real_operation_authorized_by_closeout"])
        self.assertTrue(transition["fresh_packet_bound_maintainer_words_required"])

    def test_only_tracked_and_git_proof_reads_occurred(self):
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 3)
        self.assertEqual(counters["Git_proof_reads"], 3)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_claim_and_next_gate_language_are_explicit(self):
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
