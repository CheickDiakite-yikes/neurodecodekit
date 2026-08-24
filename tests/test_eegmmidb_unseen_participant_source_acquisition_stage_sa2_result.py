import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa2_result.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_STAGE_SA2_RESULT.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionStageSA2ResultTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_result_is_failed_consumed_and_not_rerunnable(self):
        self.assertEqual(
            self.result["status"],
            "failed_before_HTTP_response_consumed_permanently_parked",
        )
        binding = self.result["execution_binding"]
        self.assertEqual(binding["registered_invocations"], 1)
        self.assertFalse(binding["retry_allowed"])
        self.assertFalse(binding["rerun_allowed"])
        self.assertFalse(binding["repair_resume_fallback_or_substitution_allowed"])

    def test_execution_waited_for_both_green_jobs(self):
        binding = self.result["execution_binding"]
        self.assertEqual(
            binding["execution_HEAD"],
            "9cc2688d90dc9bf75bd64751a63a7e318b4276ce",
        )
        self.assertEqual(binding["activation_CI_run_id"], 32738530528)
        self.assertEqual(binding["activation_base_python_job_id"], 97467118679)
        self.assertEqual(
            binding["activation_optional_neuro_readers_job_id"], 97467118486
        )
        self.assertTrue(binding["both_required_jobs_green_before_execution"])

    def test_failed_activation_commit_never_opened_live_boundary(self):
        history = self.result["activation_CI_history"]
        self.assertFalse(history["initial_activation_CI_green"])
        self.assertFalse(history["live_operation_from_failed_activation_commit"])
        self.assertTrue(history["repair_CI_green"])
        self.assertFalse(history["qualified_module_or_proof_registry_changed_by_repair"])

    def test_failure_is_verified_TLS_without_bypass_or_response(self):
        failure = self.result["failure"]
        self.assertEqual(failure["stage"], "checksum_manifest_TLS_handshake")
        self.assertEqual(failure["cause_exception_type"], "ssl.SSLCertVerificationError")
        self.assertTrue(failure["TLS_verification_enabled"])
        self.assertFalse(failure["certificate_verification_bypassed"])
        self.assertFalse(failure["alternate_client_or_certificate_bundle_used"])
        self.assertFalse(failure["HTTP_response_received"])
        self.assertTrue(failure["failure_consumes_invocation"])

    def test_postfailure_state_retains_only_consumed_marker(self):
        state = self.result["postfailure_state"]
        self.assertFalse(state["payload_bundle_exists"])
        self.assertFalse(state["temporary_directory_exists"])
        self.assertTrue(state["consumed_marker_exists"])
        self.assertFalse(state["consumed_marker_opened_after_failure"])
        self.assertEqual(state["consumed_marker_logical_bytes_from_frozen_serializer"], 212)
        self.assertEqual(state["repository_tracked_files_modified_by_execution"], 0)

    def test_all_data_model_score_and_claim_counters_are_zero(self):
        measured = self.result["measurements"]
        zero_fields = (
            "input_bytes",
            "successful_HTTP_responses",
            "checksum_manifest_body_bytes",
            "EDF_requests",
            "payload_network_bytes",
            "new_payload_disk_bytes",
            "maximum_stream_read_bytes",
            "opaque_post_write_passes",
            "EDF_semantic_reads",
            "target_or_label_reads",
            "parameter_update_fits",
            "model_inference_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "scientific_claim_upgrades",
        )
        self.assertTrue(all(measured[field] == 0 for field in zero_fields))
        self.assertEqual(measured["checksum_manifest_transport_attempts"], 1)
        self.assertEqual(
            measured["input_bytes_definition"],
            "application_visible_HTTP_response_body_bytes",
        )
        self.assertIsNone(measured["peak_process_tree_RSS_bytes"])
        self.assertFalse(measured["end_to_end_decoding_latency_measured"])
        verification = self.result["verification"]
        self.assertEqual(verification["focused_tests_passed"], 16)
        self.assertEqual(verification["result_base_tests_passed"], 5913)
        self.assertEqual(verification["net_new_tests_passed"], 9)
        self.assertEqual(verification["ruff_scope"], "changed_Python_files")
        self.assertFalse(verification["latest_unpinned_repository_wide_ruff_passed"])

    def test_proof_artifacts_remain_exact_in_current_tree(self):
        for row in self.result["proof_bindings"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_next_gate_parks_dependent_source_LOSO(self):
        gate = self.result["next_gate"]
        self.assertTrue(gate["stage_SA2_consumed"])
        self.assertTrue(gate["stage_SA2_permanently_parked"])
        self.assertFalse(gate["dependent_UG1_source_LOSO_executable"])
        self.assertTrue(
            gate["separate_new_lane_requires_new_preregistration_and_Tier_C_decision"]
        )

    def test_human_result_preserves_engineering_and_science_boundary(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Failed before any HTTP response", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("will not retry", document)
        boundary = self.result["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])


if __name__ == "__main__":
    unittest.main()
