import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/marc2_task_aware_private_cohort_confirmation_authorization_request.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_TASK_AWARE_PRIVATE_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md"
)


class Marc2TaskAwarePrivateCohortConfirmationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR36P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_local_remote_proof_pending",
        )
        self.assertEqual(
            self.request["proof_posture"],
            "request_only_no_private_real_or_scientific_operation_authorized",
        )

    def test_green_VR35A_closeout_is_bound(self):
        proof = self.request["green_predecessor_proof"]["VR35A_proof_closeout"]
        self.assertEqual(
            proof["commit"], "6744568115f1f4871b68f4605d14732bf3af38f8"
        )
        self.assertEqual(proof["CI_run_id"], 32_645_704_669)
        self.assertEqual(proof["base_python_job_id"], 97_209_528_132)
        self.assertEqual(proof["optional_neuro_job_id"], 97_209_528_186)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["qualification_repeated"])

    def test_fixed_artifacts_match_without_private_access(self):
        total = 0
        for row in self.request["fixed_committed_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            total += len(payload)
        summary = self.request["fixed_artifact_summary"]
        self.assertEqual(total, summary["bytes"])
        self.assertEqual(len(self.request["fixed_committed_artifacts"]), summary["count"])
        self.assertTrue(summary["all_paths_tracked_and_not_Git_ignored"])

    def test_request_artifacts_match(self):
        artifacts = self.request["request_artifacts"]
        for role in ("document", "test"):
            payload = (ROOT / artifacts[f"{role}_path"]).read_bytes()
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), artifacts[f"{role}_sha256"]
            )

    def test_future_source_identity_is_copied_only(self):
        source = self.request["future_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["regular_file_rows"], 1_025)
        self.assertEqual(source["directory_rows"], 202)
        self.assertTrue(source["identity_copied_from_committed_records_only"])
        self.assertFalse(source["path_checked_during_packet_preparation"])
        self.assertFalse(source["content_opened_during_packet_preparation"])
        self.assertEqual(source["bytes_read_during_packet_preparation"], 0)

    def test_requested_sequence_is_two_stage_and_one_shot(self):
        sequence = self.request["requested_future_sequence"]
        self.assertTrue(sequence["stage_1_generated_mock_wrapper_after_separate_decision_green"])
        self.assertTrue(
            sequence["stage_2_one_private_confirmation_after_implementation_and_closeout_green"]
        )
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["strict_JSON_parse_limit"], 1)
        self.assertEqual(sequence["VR35A_call_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)

    def test_exact_finite_readiness_is_required(self):
        readiness = self.request["future_readiness_contract"]
        self.assertEqual(readiness["exact_VR33A_calls"], 1)
        self.assertEqual(readiness["sample_provider_calls"], 3)
        self.assertEqual(readiness["sleeper_calls"], 2)
        self.assertEqual(readiness["interval_seconds"], 5.0)
        self.assertTrue(readiness["all_three_samples_must_pass"])
        self.assertEqual(readiness["not_ready_source_content_opens"], 0)
        self.assertFalse(readiness["dynamic_loop_allowed"])

    def test_route_map_separates_parallel_hypotheses(self):
        route_map = self.request["future_task_aware_route_contract"]
        self.assertEqual(
            route_map["frozen_map"],
            [
                {"VR35A_route": "MARC2VR35A-G1", "VR36P_route": "MARC2VR36P-R1", "cohort_frozen": True},
                {"VR35A_route": "MARC2VR35A-G2", "VR36P_route": "MARC2VR36P-R2", "cohort_frozen": True},
                {"VR35A_route": "MARC2VR35A-R1", "VR36P_route": "MARC2VR36P-R3", "cohort_frozen": False},
                {"VR35A_route": "MARC2VR35A-R2", "VR36P_route": "MARC2VR36P-R4", "cohort_frozen": False},
                {"VR35A_route": "MARC2VR35A-R3", "VR36P_route": "MARC2VR36P-R5", "cohort_frozen": False},
            ],
        )
        self.assertFalse(route_map["observed_count_difference_or_task_distribution_allowed"])
        self.assertFalse(route_map["non_target_selected_row_allowed"])

    def test_success_freezes_only_target_free_structural_cohort(self):
        cohort = self.request["future_cohort_freeze_contract"]
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(cohort["selected_run_bundles"], 96)
        self.assertEqual(cohort["selected_core_members"], 384)
        self.assertEqual(cohort["fit_session"], "ses-01")
        self.assertEqual(cohort["heldout_session"], "ses-02")
        self.assertTrue(cohort["source_exact_target_task_rows_required"])
        self.assertFalse(cohort["archive_member_or_payload_opened"])
        self.assertFalse(cohort["FW2_authorized_by_success"])

    def test_generated_stage_is_bounded_and_private_free(self):
        stage = self.request["future_generated_qualification"]
        self.assertEqual(stage["required_paths"], 40)
        self.assertEqual(stage["required_VR33A_calls"], 40)
        self.assertEqual(stage["required_VR35A_calls"], 20)
        self.assertGreaterEqual(stage["minimum_direct_refusals"], 100)
        self.assertEqual(stage["private_or_Git_ignored_path_operation_limit"], 0)
        self.assertEqual(stage["retained_generated_output_bytes"], 0)

    def test_resource_caps_are_small_and_payload_free(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLess(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2 + 1)
        self.assertEqual(caps["private_source_input_bytes"], 418_755)
        self.assertLessEqual(caps["combined_incremental_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["signal_sample_bytes"], 0)
        self.assertEqual(caps["target_or_label_bytes"], 0)

    def test_every_current_authority_and_operation_is_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )

    def test_decision_protocol_rejects_retroactive_continue(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["proof_closeout_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_is_retroactive_authority"])
        self.assertFalse(protocol["packet_or_decision_alone_authorizes_private_open"])

    def test_next_gate_and_claim_boundary_remain_closed(self):
        gate = self.request["next_gate"]
        self.assertFalse(gate["packet_identification_or_fresh_decision_allowed_now"])
        self.assertFalse(gate["generated_wrapper_implementation_allowed_now"])
        self.assertFalse(gate["private_structural_confirmation_allowed_now"])
        self.assertFalse(gate["private_cohort_freeze_allowed_now"])
        self.assertFalse(gate["FW2_or_CIL1_allowed_now"])
        claims = self.request["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["real_or_private_data_accessed_by_request"])
        self.assertFalse(claims["real_cohort_established"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("not retroactive authority", text)


if __name__ == "__main__":
    unittest.main()
