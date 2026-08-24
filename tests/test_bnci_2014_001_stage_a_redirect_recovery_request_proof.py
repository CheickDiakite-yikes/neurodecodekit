import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/bnci_2014_001_stage_a_redirect_recovery_request_proof.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_REQUEST_PROOF_CLOSEOUT.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageARedirectRecoveryRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_green_request_is_exact(self):
        green = self.proof["green_request"]
        self.assertEqual(green["commit"], "69527929cbe590cf4d8a83cfc68bbff9867c28c9")
        self.assertEqual(green["CI_run_id"], 32_783_593_146)
        self.assertEqual(green["base_python_job_id"], 97_610_714_226)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97_610_714_567)
        self.assertTrue(green["both_required_jobs_green"])

    def test_request_artifacts_are_exact(self):
        rows = self.proof["bound_request_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 12_562)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_proof_is_nonoperative_and_authority_remains_false(self):
        operations = self.proof["proof_operations"]
        for key, value in operations.items():
            if key == "committed_artifact_reads":
                self.assertEqual(value, 3)
            elif key == "GitHub_CI_verification_calls":
                self.assertEqual(value, 1)
            else:
                self.assertEqual(value, 0, key)
        authority = self.proof["authority"]
        self.assertFalse(authority["recovery_authorized"])
        self.assertFalse(authority["manifest_or_payload_network"])
        self.assertTrue(authority["decision_required_after_this_proof_is_remotely_green"])

    def test_claim_boundary_and_document_are_explicit(self):
        self.assertFalse(self.proof["claim_boundary"]["scientific_claim_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
