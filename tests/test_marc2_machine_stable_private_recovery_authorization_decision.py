import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc2_machine_stable_private_recovery_authorization_decision.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_MACHINE_STABLE_PRIVATE_RECOVERY_AUTHORIZATION_DECISION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2MachineStablePrivateRecoveryAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_machine_stable_private_recovery_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR4P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "a5b73d6859c71054a1f20ab6c1c500341539efea",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_proof_is_exact(self):
        proof = self.decision["green_request"]
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 31_967_933_217)
        self.assertEqual(proof["base_python_job_id"], 95_215_825_208)
        self.assertEqual(proof["optional_neuro_job_id"], 95_215_825_263)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["request_SHA256"],
            "cf10a7bcd40baa941c81f3966694aa63e80a173c1fc0c4e6e5c2d6c2bcce34a1",
        )
        self.assertEqual(
            proof["packet_SHA256"],
            "56458e19991e468f501731d555e144f9ee0d31b19f70b6e666f7c950c3a796e8",
        )

    def test_bound_request_artifacts_are_byte_exact(self):
        for artifact in self.decision["bound_request_artifacts"]:
            path = ROOT / artifact["path"]
            with self.subTest(path=artifact["path"]):
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])

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
        self.assertTrue(rule["packet_and_request_green_before_message"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(rule["future_FW2_packet_existed_when_message_was_sent"])

    def test_authority_is_conditional_and_payload_remains_closed(self):
        authority = self.decision["authorization"]
        self.assertTrue(
            authority["generated_mock_executor_implementation_after_decision_green"]
        )
        self.assertTrue(
            authority["one_private_structural_manifest_read_after_executor_green"]
        )
        self.assertTrue(
            authority[
                "one_VR2_adapter_call_and_real_target_free_cohort_freeze_after_executor_green"
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
        self.assertEqual(
            order[2], "exact_executor_commit_pushed_and_both_CI_jobs_green"
        )
        self.assertIn(
            "new_root_preflight_and_marker_immediately_before_private_open", order
        )
        self.assertTrue(order[-1].startswith("stop_before_archive_payload_neural"))

    def test_expired_certificate_cleanup_is_exactly_one_artifact(self):
        artifact = self.decision["expired_certificate_identity"]
        self.assertEqual(
            artifact["path"],
            ".codex_work/marc2_machine_readiness/vr4/readiness.v0.json",
        )
        self.assertEqual(artifact["mode"], "0600")
        self.assertEqual(artifact["bytes"], 4551)
        self.assertEqual(artifact["unlink_limit_after_executor_green"], 1)
        self.assertEqual(artifact["other_path_or_project_deletion_limit"], 0)
        self.assertEqual(artifact["operations_at_decision_recording"], 0)

    def test_fresh_readiness_precedes_private_operations(self):
        readiness = self.decision["fresh_readiness_contract"]
        self.assertEqual(readiness["consecutive_passing_samples"], 3)
        self.assertEqual(readiness["maximum_wait_seconds"], 600)
        self.assertTrue(
            readiness["bind_future_exact_executor_commit_from_proof_record"]
        )
        self.assertFalse(readiness["ambient_HEAD_binding_allowed"])
        self.assertFalse(readiness["output_or_private_path_operation_before_ready"])

    def test_private_source_and_output_are_fixed_but_untouched(self):
        source = self.decision["registered_private_source"]
        output = self.decision["future_output_contract"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["expected_eligible_run_bundles"], 195)
        self.assertEqual(source["expected_valid_ineligible_run_bundles"], 43)
        self.assertEqual(source["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["content_opens_at_decision_recording"], 0)
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_machine_stable_private_recovery/v0",
        )
        self.assertTrue(output["marker_written_immediately_before_private_content_open"])
        self.assertEqual(output["output_operations_at_decision_recording"], 0)

    def test_cohort_and_resource_caps_are_structural_only(self):
        cohort = self.decision["frozen_cohort_invariants"]
        caps = self.decision["resource_boundary"]
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(cohort["selected_bundles"], 96)
        self.assertEqual(cohort["selected_members"], 384)
        self.assertTrue(cohort["selected_declared_bytes_are_metadata_only"])
        self.assertEqual(cohort["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)

    def test_decision_only_counters_are_zero_except_green_verification(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                self.assertEqual(value, 0, key)

    def test_next_gate_and_claim_boundary_fail_closed(self):
        gate = self.decision["next_gate"]
        claim = self.decision["claim_boundary"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertFalse(gate["executor_implementation_may_begin_before_green"])
        self.assertFalse(
            gate[
                "expired_certificate_or_private_manifest_operation_may_begin_before_green_executor"
            ]
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
