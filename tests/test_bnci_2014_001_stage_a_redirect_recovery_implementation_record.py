import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/bnci_2014_001_stage_a_redirect_recovery_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_IMPLEMENTATION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageARedirectRecoveryImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_decision_is_exact(self):
        green = self.registry["green_authorization_decision"]
        self.assertEqual(green["commit"], "588dd70c62a6f7041d677f9baf35e476ef739627")
        self.assertEqual(green["CI_run_id"], 32_803_138_246)
        self.assertTrue(green["both_required_jobs_green"])

    def test_three_implementation_artifacts_are_exact(self):
        rows = self.registry["implementation_artifacts"]
        self.assertEqual(len(rows), 3)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_live_gate_is_closed_and_filesystem_is_anchored(self):
        gate = self.registry["live_proof_gate"]
        self.assertFalse(gate["activation_exists_now"])
        self.assertFalse(gate["live_recovery_open_now"])
        filesystem = self.registry["filesystem_contract"]
        self.assertTrue(filesystem["directory_descriptor_anchored"])
        self.assertTrue(filesystem["O_NOFOLLOW"])

    def test_document_has_separate_engineering_and_scientific_sentences(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
