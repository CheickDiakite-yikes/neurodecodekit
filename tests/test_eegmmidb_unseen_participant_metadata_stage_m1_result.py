import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = (
    ROOT / "registries/eegmmidb_unseen_participant_metadata_implementation.v0.json"
)
RESULT = (
    ROOT / "registries/eegmmidb_unseen_participant_metadata_stage_m1_result.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_STAGE_M1_RESULT.md"


class EEGMMIDBUnseenParticipantMetadataStageM1ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(IMPLEMENTATION.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_corrected_implementation_was_green_before_execution(self):
        execution = self.result["execution_binding"]
        self.assertEqual(
            execution["implementation_commit"],
            "1c68a775294e08013f6ef0780eb8901917699db0",
        )
        self.assertEqual(execution["implementation_CI_run_id"], 32715529168)
        self.assertEqual(execution["base_python_job_id"], 97395810059)
        self.assertEqual(execution["optional_neuro_readers_job_id"], 97395810337)
        self.assertTrue(execution["both_required_jobs_green_before_execution"])

    def test_preexecution_implementation_artifacts_remain_exact(self):
        for row in self.implementation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_registered_qualification_is_consumed_once(self):
        execution = self.result["execution_binding"]
        self.assertEqual(execution["qualification_invocations"], 1)
        self.assertFalse(execution["qualification_may_be_repeated"])
        self.assertEqual(execution["aggregate_output_bytes"], 1416)
        self.assertEqual(
            execution["aggregate_output_sha256"],
            "9f91843e6a20f8794cf19105116b3bcf13a2a3deff496a3c44ff30ecbcfeafe3",
        )
        self.assertFalse(execution["aggregate_output_committed"])

    def test_all_twenty_cases_passed_in_frozen_order(self):
        expected = self.implementation["generated_qualification"]["cases"]
        qualification = self.result["qualification"]
        self.assertEqual(qualification["case_count"], 20)
        self.assertEqual(qualification["cases"], expected)
        self.assertTrue(qualification["deterministic_replay"])
        self.assertEqual(qualification["source_immutability_checks"], 1)
        self.assertEqual(qualification["source_fixture_bytes"], 8354)

    def test_resources_and_operation_counters_are_bounded(self):
        measured = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertLessEqual(measured["runtime_seconds"], caps["wall_time_seconds"])
        self.assertLessEqual(
            measured["peak_process_tree_RSS_bytes"],
            caps["peak_process_tree_RSS_bytes"],
        )
        self.assertLessEqual(measured["output_bytes"], caps["generated_output_bytes"])
        self.assertGreaterEqual(
            measured["initial_free_disk_bytes"], caps["minimum_free_disk_bytes"]
        )
        self.assertEqual(measured["mock_HEAD_requests"], 297)
        for key in (
            "real_HEAD_requests",
            "response_body_reads",
            "response_body_bytes",
            "real_URL_or_local_data_path_operations",
            "EDF_content_reads",
            "payload_download_bytes",
            "target_or_label_reads",
            "parameter_update_fits",
            "model_inference_runs",
            "model_runs",
            "training_runs",
            "scoring_events",
            "network_bytes",
            "new_payload_bytes",
        ):
            self.assertEqual(measured[key], 0)

    def test_stage_m2_and_scientific_claims_remain_closed(self):
        gate = self.result["next_gate"]
        self.assertFalse(gate["stage_M2_authorized_now"])
        self.assertFalse(gate["payload_download_authorized_now"])
        self.assertFalse(gate["EDF_content_access_authorized_now"])
        boundary = self.result["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
