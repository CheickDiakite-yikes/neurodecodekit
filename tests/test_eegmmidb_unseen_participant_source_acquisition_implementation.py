import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_IMPLEMENTATION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class EEGMMIDBUnseenParticipantSourceAcquisitionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_decision_and_no_registered_execution_are_exact(self):
        green = self.registry["green_authorization_decision"]
        self.assertEqual(green["commit"], "1b5c9195f384e5867f18131aa7d669f7c9cd0e2b")
        self.assertEqual(green["CI_run_id"], 32_725_633_524)
        self.assertEqual(green["base_python_job_id"], 97_426_157_639)
        self.assertEqual(green["optional_neuro_job_id"], 97_426_157_381)
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
        self.assertEqual(transport["method"], "GET")
        self.assertEqual(transport["checksum_manifest_requests"], 1)
        self.assertEqual(transport["EDF_requests"], 6)
        self.assertEqual(transport["requests_total"], 7)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertTrue(transport["checksum_freeze_before_first_EDF_request"])
        self.assertEqual(transport["maximum_stream_chunk_bytes"], 1 << 20)
        qualification = self.registry["generated_qualification"]
        self.assertEqual(qualification["case_count"], 27)
        self.assertEqual(len(qualification["cases"]), 27)
        self.assertEqual(qualification["registered_execution_count_now"], 0)

    def test_cli_and_live_proof_gate_are_closed(self):
        cli = self.registry["CLI"]
        self.assertEqual(cli["commands"], ["plan", "qualify"])
        self.assertFalse(cli["execute_command_present"])
        self.assertFalse(cli["live_network_command_present"])
        gate = self.registry["stage_SA2_boundary"]
        self.assertTrue(gate["exact_green_SA1_proof_required_before_live_opener"])
        self.assertEqual(gate["real_invocation_count_now"], 0)
        self.assertFalse(gate["available_before_exact_SA1_result_remote_green"])
        self.assertFalse(gate["available_before_separate_proof_closeout_remote_green"])

    def test_resources_and_current_counters_are_closed(self):
        caps = self.registry["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["successful_payload_body_bytes_exact"], 15_498_816)
        self.assertEqual(caps["payload_network_body_bytes_maximum"], 16 << 20)
        self.assertEqual(caps["incremental_disk_bytes_maximum"], 64 << 20)
        self.assertEqual(caps["stream_chunk_bytes_maximum"], 1 << 20)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 256 << 20)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertTrue(all(value == 0 for value in self.registry["operation_counters"].values()))

    def test_isolation_and_claim_boundary_are_explicit(self):
        isolation = self.registry["isolation"]
        self.assertFalse(isolation["proof_bound_stage_G_or_M_artifact_modified"])
        self.assertFalse(isolation["central_neurodecode_CLI_modified"])
        self.assertFalse(isolation["heavy_base_dependency_added"])
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
