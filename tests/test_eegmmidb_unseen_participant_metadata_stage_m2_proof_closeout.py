import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/eegmmidb_unseen_participant_metadata_stage_m2_proof_closeout.v0.json"
)
DOCUMENT = (
    ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_STAGE_M2_PROOF_CLOSEOUT.md"
)


class EEGMMIDBUnseenParticipantMetadataStageM2ProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_m2_result_commit_was_remotely_green(self):
        green = self.proof["green_result_commit"]
        self.assertEqual(
            green["commit"], "818ef1f6384a03c3681d9d4ec01d6f88db4d2749"
        )
        self.assertEqual(green["CI_run_id"], 32718796222)
        self.assertEqual(green["base_python_job_id"], 97405609600)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97405609428)
        self.assertTrue(green["both_required_jobs_green"])

    def test_eight_artifacts_are_byte_hash_and_git_bound(self):
        rows = self.proof["bound_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["artifact_summary"]
        self.assertEqual(summary["count"], 8)
        self.assertEqual(summary["bytes"], 37723)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_repeats_no_network_or_real_operation(self):
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 8)
        self.assertEqual(counters["Git_proof_reads"], 8)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )
        scope = self.proof["scope_preservation"]
        self.assertFalse(scope["real_metadata_invocation_repeated"])
        self.assertFalse(scope["inventory_reconstructed_amended_or_replaced"])
        self.assertFalse(scope["authority_expanded"])

    def test_stage_m_closes_and_source_payload_remains_unapproved(self):
        transition = self.proof["transition"]
        self.assertFalse(transition["effective_before_this_closeout_commit_remote_green"])
        self.assertTrue(
            transition["stage_M_fully_closed_after_exact_closeout_remote_green"]
        )
        self.assertEqual(transition["source_fit_missing_file_count"], 6)
        self.assertEqual(transition["source_fit_missing_declared_bytes"], 15498816)
        self.assertFalse(transition["payload_acquisition_authorized_by_closeout"])
        self.assertFalse(transition["fresh_final_acquisition_authorized_by_closeout"])
        self.assertFalse(transition["EDF_content_access_authorized_by_closeout"])

    def test_human_closeout_separates_engineering_and_science(self):
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("six missing S001-S003 run-04/run-08 files", document)


if __name__ == "__main__":
    unittest.main()
