import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_implementation.v0.json"
)
RESULT = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_result.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_STAGE_SA1_RESULT.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionStageSA1ResultTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(IMPLEMENTATION.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_exact_corrected_implementation_was_green_before_execution(self):
        execution = self.result["execution_binding"]
        self.assertEqual(
            execution["implementation_commit"],
            "37808bef8c59bc862345f342fd932aa04373b3fd",
        )
        self.assertEqual(execution["implementation_CI_run_id"], 32730673153)
        self.assertEqual(execution["base_python_job_id"], 97441967842)
        self.assertEqual(execution["optional_neuro_readers_job_id"], 97441968304)
        self.assertTrue(execution["both_required_jobs_green_before_execution"])

    def test_preexecution_implementation_artifacts_remain_exact(self):
        for row in self.implementation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        module = self.result["preexecution_implementation"]
        self.assertEqual(module["qualified_module_bytes"], 75810)
        self.assertEqual(
            module["qualified_module_sha256"],
            "3e6d7c8ee9b52286860d59c26061f3f52521905d91bfad166c7618feaacc7e62",
        )
        self.assertFalse(module["qualified_module_modified_after_execution"])

    def test_registered_qualification_is_consumed_once(self):
        execution = self.result["execution_binding"]
        self.assertEqual(execution["qualification_invocations"], 1)
        self.assertFalse(execution["qualification_may_be_repeated"])
        self.assertEqual(execution["aggregate_output_bytes"], 1901)
        self.assertEqual(
            execution["aggregate_output_sha256"],
            "f2fbba2e102858d3e4328960b7772b3f5b6b83c3907266e99de45f19b7e7239e",
        )
        self.assertFalse(execution["aggregate_output_committed"])

    def test_all_twenty_seven_cases_passed_in_frozen_order(self):
        expected = self.implementation["generated_qualification"]["cases"]
        qualification = self.result["qualification"]
        self.assertEqual(qualification["case_count"], 27)
        self.assertEqual(qualification["cases"], expected)
        self.assertTrue(qualification["deterministic_replay"])
        self.assertEqual(qualification["successful_generated_bundle_count"], 3)
        self.assertEqual(qualification["direct_refusals"], 1)

    def test_mock_counter_discrepancy_is_explicit_and_exactly_reconciled(self):
        correction = self.result["counter_schema_discrepancy"]
        self.assertEqual(correction["raw_top_level_mock_requests"], 56)
        self.assertEqual(correction["raw_nested_mock_checksum_requests"], 0)
        self.assertEqual(correction["raw_nested_mock_EDF_requests"], 0)
        self.assertFalse(correction["raw_nested_subtype_fields_authoritative"])
        self.assertEqual(
            correction["deterministically_recovered_mock_checksum_requests"], 21
        )
        self.assertEqual(
            correction["deterministically_recovered_mock_EDF_requests"], 35
        )
        self.assertEqual(correction["recovered_total"], 21 + 35)
        self.assertEqual(correction["authoritative_mock_request_total"], 56)
        self.assertFalse(correction["qualification_rerun_for_correction"])
        self.assertFalse(correction["real_or_scientific_counter_affected"])

    def test_resources_and_real_operation_counters_are_bounded(self):
        measured = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertLessEqual(measured["runtime_seconds"], caps["wall_time_seconds"])
        self.assertLessEqual(
            measured["peak_process_tree_RSS_bytes"],
            caps["peak_process_tree_RSS_bytes"],
        )
        self.assertLessEqual(
            measured["maximum_stream_chunk_bytes"],
            caps["stream_chunk_bytes_maximum"],
        )
        self.assertLessEqual(
            measured["peak_incremental_disk_bytes"],
            caps["incremental_disk_bytes_maximum"],
        )
        self.assertGreaterEqual(
            measured["initial_free_disk_bytes"], caps["minimum_free_disk_bytes"]
        )
        self.assertEqual(measured["mock_requests"], 56)
        self.assertEqual(measured["opaque_post_write_passes"], 18)
        for key in (
            "real_requests",
            "real_URL_or_local_payload_path_operations",
            "real_payload_bytes",
            "new_real_payload_disk_bytes",
            "EDF_semantic_reads",
            "target_or_label_reads",
            "parameter_update_fits",
            "model_inference_runs",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "network_bytes",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(measured[key], 0)

    def test_stage_sa2_and_scientific_claims_remain_closed(self):
        gate = self.result["next_gate"]
        self.assertFalse(gate["stage_SA2_authorized_now"])
        self.assertFalse(gate["network_or_real_payload_access_authorized_now"])
        self.assertFalse(gate["EDF_semantic_access_authorized_now"])
        boundary = self.result["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("21 checksum-manifest mock requests plus 35 EDF", document)


if __name__ == "__main__":
    unittest.main()
