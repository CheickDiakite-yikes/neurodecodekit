import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/bnci_2014_001_stage_a_redirect_recovery_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_AUTHORIZATION_PACKET.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageARedirectRecoveryRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_consumed_failure_is_exact(self):
        green = self.request["green_failure_closeout"]
        self.assertEqual(green["commit"], "162fddcfa2f399f4e5919a2daa0de4d7d33bf1f4")
        self.assertEqual(green["CI_run_id"], 32_782_670_936)
        self.assertEqual(green["base_python_job_id"], 97_607_889_466)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97_607_889_659)
        self.assertTrue(green["both_required_jobs_green"])

    def test_bound_artifacts_are_exact(self):
        self.assertEqual(len(self.request["bound_artifacts"]), 8)
        for row in self.request["bound_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_recovery_is_narrow_and_identity_derived(self):
        proposed = self.request["proposed_recovery_invocation"]
        self.assertEqual(proposed["invocations_maximum"], 1)
        self.assertEqual(proposed["manifest_GETs_exact"], 1)
        self.assertEqual(proposed["payload_files_exact"], 18)
        self.assertEqual(proposed["accepted_payload_bytes_exact"], 779_873_919)
        self.assertEqual(
            proposed["payload_host_allowlist"],
            ["nemar.s3.us-east-2.amazonaws.com"],
        )
        self.assertTrue(proposed["payload_object_key_bound_to_registered_size_and_sha256"])
        self.assertEqual(proposed["payload_redirects"], 0)
        self.assertTrue(proposed["old_consumed_marker_must_remain_byte_identical"])

    def test_all_authority_is_false_and_science_is_closed(self):
        self.assertTrue(all(value is False for value in self.request["authority_now"].values()))
        claims = self.request["claim_boundary"]
        self.assertFalse(claims["scientific_claim_established"])
        self.assertFalse(claims["unseen_person_generalization"])
        self.assertFalse(claims["EEG_beyond_EOG"])
        self.assertFalse(claims["decoding_performance"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
