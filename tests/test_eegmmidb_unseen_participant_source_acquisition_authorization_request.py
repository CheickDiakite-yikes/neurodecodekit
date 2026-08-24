import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_authorization_request.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_AUTHORIZATION_PACKET.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionAuthorizationRequestTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_stage_m_closeout_is_exactly_bound(self):
        green = self.request["green_stage_M_closeout"]
        self.assertEqual(
            green["commit"], "00f795f860762a6e828b210cee52808e69571d53"
        )
        self.assertEqual(green["CI_run_id"], 32720013549)
        self.assertEqual(green["base_python_job_id"], 97409224259)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97409224710)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["stage_M_consumed"])
        self.assertFalse(green["stage_M_rerun_allowed"])

    def test_bound_artifacts_hash_size_blob_and_set_hash_are_exact(self):
        rows = self.request["bound_pre_request_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.request["bound_pre_request_artifact_summary"]
        self.assertEqual(summary["count"], 11)
        self.assertEqual(summary["bytes"], 116444)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_exact_source_boundary_is_complete_distinct_and_six_only(self):
        controlling = self.request["controlling_scope"]
        self.assertTrue(controlling["amendment_1_controls_conflicts_with_older_packet_language"])
        self.assertFalse(
            controlling[
                "participant_or_file_identity_allowed_in_predictive_features_normalization_models_controls_or_thresholds"
            ]
        )
        source = self.request["source_boundary"]
        rows = source["exact_files_in_request_order"]
        self.assertEqual(source["participants"], ["S001", "S002", "S003"])
        self.assertEqual(source["runs"], ["04", "08"])
        self.assertEqual(len(rows), source["file_count"])
        self.assertEqual(len({row["repository_path"] for row in rows}), 6)
        self.assertEqual(sum(row["size_bytes"] for row in rows), 15498816)
        self.assertEqual(source["declared_payload_bytes_exact"], 15498816)
        self.assertTrue(all(row["partition"] == "source_fit_missing" for row in rows))
        self.assertEqual(
            [(row["participant"], row["run"]) for row in rows],
            [
                ("S001", "04"),
                ("S001", "08"),
                ("S002", "04"),
                ("S002", "08"),
                ("S003", "04"),
                ("S003", "08"),
            ],
        )
        self.assertTrue(all(row["repository_path"].endswith(".edf") for row in rows))
        self.assertTrue(all(".event" not in row["repository_path"] for row in rows))

    def test_fresh_final_files_are_a_zero_operation_firewall(self):
        firewall = self.request["fresh_final_firewall"]
        self.assertEqual(firewall["participants"], "S016-S030")
        self.assertEqual(firewall["file_count"], 30)
        self.assertEqual(firewall["declared_payload_bytes"], 76916160)
        self.assertEqual(firewall["network_requests_allowed"], 0)
        self.assertEqual(firewall["local_path_operations_allowed"], 0)
        self.assertFalse(firewall["payload_or_content_access_allowed"])
        self.assertFalse(firewall["acquisition_allowed"])
        retained = self.request["retained_source_firewall"]
        self.assertIn("54 already-retained", retained["description"])
        self.assertEqual(retained["network_requests_allowed"], 0)
        self.assertEqual(retained["local_path_operations_allowed"], 0)
        self.assertFalse(retained["payload_or_content_access_allowed"])

    def test_stages_are_generated_first_remote_green_and_one_shot(self):
        generated, real = self.request["requested_ordered_stages"]
        self.assertEqual(generated["network_requests"], 0)
        self.assertEqual(generated["real_URL_or_path_access"], 0)
        self.assertEqual(generated["generated_qualification_invocations"], 1)
        self.assertFalse(generated["proof_bound_existing_module_modification_allowed"])
        self.assertTrue(generated["must_be_recorded_committed_pushed_and_both_jobs_green"])
        self.assertTrue(
            generated["proof_closeout_must_then_be_committed_pushed_and_both_jobs_green"]
        )
        self.assertEqual(real["HTTP_method"], "GET")
        self.assertEqual(real["checksum_manifest_requests_exact"], 1)
        self.assertEqual(real["EDF_payload_requests_exact"], 6)
        self.assertEqual(real["total_requests_exact"], 7)
        self.assertEqual(real["redirects"], 0)
        self.assertEqual(real["retries"], 0)
        self.assertEqual(real["reruns"], 0)
        self.assertEqual(real["successful_response_body_bytes_exact"], 15498816)
        self.assertEqual(real["opaque_local_size_and_sha256_passes_exact"], 6)
        self.assertTrue(real["consumed_on_pass_or_failure"])

    def test_transport_is_exact_conditional_and_opaque(self):
        contract = self.request["transport_contract"]
        self.assertTrue(contract["TLS_certificate_verification_required"])
        self.assertEqual(contract["direct_status_exact"], 200)
        self.assertEqual(contract["checksum_manifest"]["requests_exact"], 1)
        self.assertEqual(
            contract["checksum_manifest"]["allowlisted_entries_required_exact"], 6
        )
        self.assertTrue(contract["checksum_manifest"]["must_freeze_before_first_EDF_request"])
        self.assertEqual(contract["request_headers"]["Accept-Encoding"], "identity")
        self.assertEqual(contract["request_headers"]["If-Match"], "exact_frozen_file_etag")
        self.assertTrue(contract["response_final_URL_must_equal_requested_URL"])
        self.assertTrue(contract["content_length_must_equal_frozen_size_before_body_read"])
        self.assertTrue(contract["etag_must_equal_frozen_value_before_body_read"])
        self.assertFalse(contract["content_encoding_allowed"])
        self.assertFalse(contract["content_range_allowed"])
        self.assertEqual(contract["maximum_chunk_bytes"], 1048576)
        self.assertFalse(contract["fallback_HEAD_GET_or_Range_allowed"])
        self.assertFalse(contract["partial_bundle_is_success"])

    def test_output_and_resource_caps_are_storage_cautious(self):
        output = self.request["integrity_and_output_contract"]
        self.assertTrue(output["payload_root"].startswith(".codex_work/eegmmidb_ug1/"))
        self.assertTrue(output["payload_root_must_be_absent_before_execution"])
        self.assertTrue(output["temporary_root_must_be_absent_before_execution"])
        self.assertTrue(output["consumed_marker_must_be_absent_before_execution"])
        self.assertTrue(output["consumed_marker_persisted_and_fsynced_before_first_network_request"])
        self.assertEqual(output["opaque_post_write_size_and_SHA256_passes_per_file"], 1)
        self.assertFalse(output["partial_bundle_publication_allowed"])
        self.assertFalse(output["preexisting_path_overwrite_delete_rename_or_cleanup_allowed"])
        self.assertFalse(output["payload_or_private_manifest_commit_upload_or_publication_allowed"])
        self.assertFalse(output["live_execution_CLI_command_allowed"])

        caps = self.request["resource_caps"]
        self.assertEqual(
            [caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]],
            [1, 1, 1],
        )
        self.assertEqual(caps["payload_requests"], 6)
        self.assertEqual(caps["checksum_manifest_requests"], 1)
        self.assertEqual(caps["successful_payload_body_bytes_exact"], 15498816)
        self.assertLessEqual(caps["payload_network_body_bytes_maximum"], 16777216)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 67108864)
        self.assertEqual(caps["minimum_free_disk_bytes"], 2147483648)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)

    def test_request_authorizes_nothing_and_performs_no_operation(self):
        self.assertTrue(all(value is False for value in self.request["authority_now"].values()))
        counters = self.request["request_operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 11)
        self.assertEqual(counters["Git_proof_reads"], 11)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_claim_boundary_and_packet_language_are_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established_by_request"])
        self.assertFalse(boundary["real_EEG_accessed_by_request"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        self.assertFalse(boundary["movement_intention_or_motor_cortex_origin_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Status: **All authority false; request only**", document)
        self.assertIn("The 30 S016-S030", document)
        self.assertIn("Engineering capability proposed:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
