import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc2_dynamic_private_selection_recovery_authorization_decision.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_AUTHORIZATION_DECISION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2DynamicPrivateSelectionRecoveryAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_dynamic_private_selection_recovery_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR7P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "ecaa2aba82726b6c428facf917868b78e0340969",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_and_proof_are_exact(self):
        request = self.decision["green_request"]
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(
            request["commit"], "9d42bac29b695a97639c4a197812865f0ac4f7d5"
        )
        self.assertEqual(request["CI_run_id"], 31_976_595_268)
        self.assertEqual(request["base_python_job_id"], 95_236_917_861)
        self.assertEqual(request["optional_neuro_job_id"], 95_236_917_836)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 31_976_872_160)
        self.assertEqual(proof["base_python_job_id"], 95_237_574_426)
        self.assertEqual(proof["optional_neuro_job_id"], 95_237_574_453)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_green_proof_snapshot_artifacts_are_byte_exact(self):
        for artifact in self.decision["green_proof_snapshot_artifacts"]:
            path = ROOT / artifact["path"]
            with self.subTest(path=artifact["path"]):
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])

    def test_immutable_request_bindings_are_distinct_and_complete(self):
        request_rows = self.decision["immutable_request_artifacts"]
        proof_rows = self.decision["green_proof_snapshot_artifacts"]
        self.assertEqual(len(request_rows), 3)
        self.assertEqual(len(proof_rows), 3)
        self.assertEqual(
            {row["path"] for row in request_rows},
            {row["path"] for row in proof_rows},
        )
        self.assertNotEqual(
            {row["sha256"] for row in request_rows},
            {row["sha256"] for row in proof_rows},
        )

    def test_actual_message_is_preserved_without_scope_inference(self):
        user = self.decision["user_authorization"]
        expected = "continue"
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"],
            hashlib.sha256(expected.encode()).hexdigest(),
        )
        self.assertTrue(user["one_registered_two_stage_sequence_only"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_short_form_rule_is_packet_bound_and_scope_preserving(self):
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["exactly_one_active_packet_required"])
        self.assertTrue(rule["packet_request_and_proof_green_before_message"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(rule["future_FW2_packet_existed_when_message_was_sent"])

    def test_authority_is_conditional_and_neural_payload_remains_closed(self):
        authority = self.decision["authorization"]
        self.assertTrue(
            authority["generated_mock_wrapper_implementation_after_decision_green"]
        )
        self.assertTrue(
            authority["one_private_structural_manifest_read_after_wrapper_green"]
        )
        self.assertTrue(
            authority[
                "one_VR6_adapter_call_and_real_target_free_cohort_freeze_after_wrapper_green"
            ]
        )
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["archive_member_or_payload_access_authorized_now"])
        self.assertFalse(authority["neural_derivative_creation_authorized_now"])
        self.assertFalse(
            authority["training_prediction_freeze_target_delivery_or_scoring_authorized_now"]
        )

    def test_execution_order_has_both_remote_green_barriers(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[2], "exact_wrapper_commit_pushed_and_both_CI_jobs_green")
        self.assertIn(
            "new_root_preflight_and_marker_immediately_before_private_open", order
        )
        self.assertTrue(order[-1].startswith("stop_before_archive_payload_neural"))

    def test_paths_source_and_outputs_are_fixed_but_untouched(self):
        paths = self.decision["fixed_paths"]
        source = self.decision["registered_private_source"]
        output = self.decision["future_output_contract"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr7p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_dynamic_private_selection_recovery/v0",
        )
        self.assertEqual(paths["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["content_opens_at_decision_recording"], 0)
        self.assertTrue(output["marker_immediately_before_private_content_open"])
        self.assertEqual(output["output_operations_at_decision_recording"], 0)

    def test_dynamic_selection_has_no_generated_live_outcome(self):
        policy = self.decision["dynamic_selection_invariants"]
        self.assertEqual(policy["minimum_selected_subjects"], 12)
        self.assertEqual(policy["maximum_selected_subjects"], 19)
        self.assertTrue(policy["selected_subjects_is_measured_output"])
        self.assertTrue(policy["selected_reservation_bytes_is_measured_output"])
        self.assertTrue(policy["selection_identity_sha256_is_measured_output"])
        self.assertFalse(policy["generated_expected_subject_count_allowed"])
        self.assertFalse(policy["generated_expected_reservation_bytes_allowed"])
        self.assertFalse(policy["generated_expected_selection_hash_allowed"])
        self.assertFalse(policy["target_label_quality_outcome_or_neural_field_allowed"])

    def test_generated_matrix_and_resources_are_bounded(self):
        generated = self.decision["generated_qualification"]
        caps = self.decision["resource_boundary"]
        self.assertEqual(generated["profile_subject_counts"], [12, 14, 16, 18, 19])
        self.assertEqual(generated["minimum_success_paths"], 10)
        self.assertGreaterEqual(generated["minimum_direct_mutations"], 72)
        self.assertFalse(generated["real_or_consumed_path_operation"])
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)

    def test_decision_only_counters_are_zero_except_green_verification(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 2)
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                self.assertEqual(value, 0, key)

    def test_next_gate_and_claim_boundary_fail_closed(self):
        verification = self.decision["local_verification"]
        self.assertEqual(verification["focused_request_and_decision_tests_passed"], 25)
        self.assertEqual(verification["new_decision_tests_added"], 14)
        self.assertEqual(verification["complete_suite_tests_run"], 3932)
        self.assertEqual(verification["complete_suite_passes"], 3896)
        self.assertEqual(verification["complete_suite_skips"], 35)
        self.assertEqual(
            verification["complete_suite_known_sandbox_forkserver_errors"], 1
        )
        self.assertTrue(verification["forkserver_test_passed_outside_sandbox"])
        self.assertEqual(verification["new_decision_test_failures"], 0)
        gate = self.decision["next_gate"]
        claim = self.decision["claim_boundary"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertFalse(gate["wrapper_implementation_may_begin_before_green"])
        self.assertFalse(
            gate["readiness_or_private_operation_may_begin_before_green_wrapper"]
        )
        self.assertFalse(gate["FW2_or_CIL1_real_execution_may_begin_from_this_decision"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["structural_selection_is_scientific_or_language_evidence"])
        self.assertIn("not neural data", claim["scientific_claim_not_established"])

    def test_human_decision_states_delayed_effect_and_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("The machine record preserves those actual eight UTF-8 bytes", text)
        self.assertIn("This decision is not effective merely because", text)
        self.assertIn("Engineering capability authorized after green decision", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
