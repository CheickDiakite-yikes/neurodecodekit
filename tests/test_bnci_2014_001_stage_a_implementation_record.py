import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/bnci_2014_001_stage_a_implementation.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_IMPLEMENTATION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageAImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_g1_proof_is_exact(self):
        proof = self.record["green_G1_proof"]
        self.assertEqual(proof["commit"], "cf476982d70cbd6c710b7d0a67352765155c6bc1")
        self.assertEqual(proof["CI_run_id"], 32_767_245_101)
        self.assertEqual(proof["base_python_job_id"], 97_559_394_298)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 97_559_394_437)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_implementation_artifacts_are_bound(self):
        for row in self.record["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_one_shot_and_resource_bounds_are_closed(self):
        boundary = self.record["one_shot_boundary"]
        self.assertTrue(boundary["consumed_marker_before_live_transport_construction"])
        self.assertEqual(boundary["live_invocations_now"], 0)
        self.assertEqual(boundary["reruns_allowed"], 0)
        caps = self.record["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["payload_files_exact"], 18)
        self.assertEqual(caps["payload_bytes_exact"], 779_873_919)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 2 << 30)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)

    def test_no_real_or_scientific_operation_is_claimed(self):
        verification = self.record["verification"]
        self.assertEqual(verification["network_requests"], 0)
        self.assertEqual(verification["real_payload_reads"], 0)
        self.assertEqual(verification["scientific_scores"], 0)
        claims = self.record["claim_boundary"]
        self.assertFalse(claims["scientific_claim_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
