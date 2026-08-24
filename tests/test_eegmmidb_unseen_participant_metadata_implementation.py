import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/eegmmidb_unseen_participant_metadata_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_IMPLEMENTATION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class EEGMMIDBUnseenParticipantMetadataImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_decision_and_no_registered_execution_are_exact(self):
        green = self.registry["green_authorization_decision"]
        self.assertEqual(green["commit"], "021bf8a1f2f12a8e7388a561535328cd0dc0dba2")
        self.assertEqual(green["CI_run_id"], 32_712_235_191)
        self.assertEqual(green["base_python_job_id"], 97_385_926_125)
        self.assertEqual(green["optional_neuro_job_id"], 97_385_926_444)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(self.registry["status"], "implementation_ready_qualification_not_run")
        self.assertEqual(self.registry["operation_counters"]["registered_qualifications"], 0)

    def test_exact_implementation_artifacts_are_bound(self):
        for row in self.registry["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_transport_and_case_matrix_are_frozen(self):
        transport = self.registry["transport_contract"]
        self.assertEqual(transport["method"], "HEAD")
        self.assertEqual(transport["scheme"], "https")
        self.assertEqual(transport["host"], "physionet.org")
        self.assertEqual(transport["requests_exact"], 36)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["response_body_reads"], 0)
        self.assertEqual(transport["response_body_bytes"], 0)
        qualification = self.registry["generated_qualification"]
        self.assertEqual(qualification["case_count"], 20)
        self.assertEqual(len(qualification["cases"]), 20)
        self.assertEqual(qualification["registered_execution_count_now"], 0)

    def test_cli_has_no_live_execution_surface(self):
        cli = self.registry["CLI"]
        self.assertEqual(cli["commands"], ["plan", "qualify"])
        self.assertFalse(cli["execute_command_present"])
        self.assertFalse(cli["live_network_command_present"])

    def test_resources_and_current_counters_are_closed(self):
        caps = self.registry["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["metadata_requests"], 36)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 256 << 20)
        self.assertEqual(caps["network_payload_body_bytes"], 0)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertTrue(all(value == 0 for value in self.registry["operation_counters"].values()))

    def test_claim_boundary_and_human_record_are_explicit(self):
        claims = self.registry["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_added", "scientific_ceiling"}:
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("qualification has not run", document)


if __name__ == "__main__":
    unittest.main()
