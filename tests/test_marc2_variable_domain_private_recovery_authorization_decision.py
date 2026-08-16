import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc2_variable_domain_private_recovery_authorization_decision.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2VariableDomainPrivateRecoveryAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_variable_domain_private_recovery_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR3")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "328faa845d894459a658b6ad62d078a00f539e9e",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_proof_is_exact(self):
        proof = self.decision["green_request"]
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 31_947_928_896)
        self.assertEqual(proof["base_python_job_id"], 95_166_799_271)
        self.assertEqual(proof["optional_neuro_job_id"], 95_166_799_305)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["request_SHA256"],
            "f665d66f3b6c5e97c88d8302de0b87d63e0383f45bdab54d34a90f80f4ce248b",
        )
        self.assertEqual(
            proof["packet_SHA256"],
            "1f546f25372b6212d5e86518b30acd3d42fe664965394fa5a72d5b043b4a709a",
        )

    def test_bound_artifacts_are_current_and_byte_exact(self):
        for artifact in self.decision["bound_artifacts"]:
            path = ROOT / artifact["path"]
            with self.subTest(path=artifact["path"]):
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])

    def test_actual_message_is_preserved_without_future_scope_inference(self):
        user = self.decision["user_authorization"]
        expected = (
            "continue; Run one structural-manifest pass to freeze the real cohort.\n"
            "Preregister a bounded FW2 neural experiment with signal, derangement, "
            "timing, and no-signal controls.\n"
            "Train target-firewalled models, freeze predictions, then score once."
        )
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 240)
        self.assertEqual(
            hashlib.sha256(expected.encode()).hexdigest(),
            "b104fe21f692a84f6b9aef74f5d7b0f80f025ea2d5b103798efec4246eff618f",
        )
        self.assertEqual(user["actual_message_SHA256"], hashlib.sha256(expected.encode()).hexdigest())
        self.assertTrue(user["VR3_structural_sequence_authorized_by_reference"])
        self.assertTrue(user["future_FW2_preregistration_requested"])
        self.assertFalse(user["future_FW2_real_execution_authorized_by_this_record"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])

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
        self.assertTrue(authority["wrapper_implementation_after_decision_green"])
        self.assertTrue(authority["one_private_manifest_read_after_wrapper_green"])
        self.assertTrue(authority["one_target_free_private_selection_after_wrapper_green"])
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["archive_member_or_payload_access_authorized_now"])
        self.assertFalse(authority["neural_derivative_creation_authorized_now"])
        self.assertFalse(authority["training_prediction_freeze_or_scoring_authorized_now"])

    def test_required_execution_order_has_both_remote_green_barriers(self):
        self.assertEqual(
            self.decision["required_execution_order"],
            [
                "decision_commit_pushed_and_both_CI_jobs_green",
                "generated_and_mocked_wrapper_implementation_and_qualification",
                "exact_wrapper_commit_pushed_and_both_CI_jobs_green",
                "one_registered_private_structural_manifest_invocation",
                "one_aggregate_result_commit_pushed_and_both_CI_jobs_green",
                "bounded_FW2_preregistration_and_all_false_request",
                "stop_before_archive_payload_neural_training_freeze_target_delivery_or_score",
            ],
        )

    def test_certificate_and_native_registry_have_distinct_lanes(self):
        proof = self.decision["future_proof_certificate"]
        self.assertEqual(proof["certificate_schema_lane"], "MARC2-FW1B")
        self.assertEqual(proof["native_wrapper_registry_lane"], "MARC2-VR3")
        self.assertEqual(proof["shared_validator_symbol"], "validate_implementation_record")
        self.assertTrue(proof["expected_and_observed_proofs_bind_wrapper_HEAD"])
        self.assertFalse(proof["older_HEAD_substitution_allowed"])

    def test_wrapper_surface_is_additive_and_consumed_lanes_are_forbidden(self):
        wrapper = self.decision["wrapper_qualification"]
        self.assertEqual(
            wrapper["module"],
            "neurodecodekit.datasets.marc2_variable_domain_private_recovery",
        )
        self.assertEqual(wrapper["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(wrapper["standard_library_only"])
        self.assertTrue(wrapper["exact_VR2_adapter_import_required"])
        self.assertFalse(wrapper["consumed_executor_import_call_copy_or_edit_allowed"])
        self.assertFalse(wrapper["generic_source_or_output_override_available"])
        self.assertGreaterEqual(wrapper["proof_certificate_mutations"], 32)
        self.assertGreaterEqual(wrapper["wrapper_mutations"], 32)

    def test_private_source_is_bound_but_untouched(self):
        source = self.decision["registered_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["entries"], 1_227)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["content_opens_at_decision_recording"], 0)
        self.assertEqual(source["private_bytes_at_decision_recording"], 0)

    def test_new_output_root_is_exact_closed_and_distinct(self):
        output = self.decision["future_output_contract"]
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_live_domain_private_recovery/v0",
        )
        self.assertNotIn(output["root"], output["forbidden_consumed_roots"])
        self.assertFalse(output["root_operation_authorized_before_wrapper_green"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertFalse(output["overwrite_allowed"])

    def test_future_execution_is_one_shot_and_stops_before_payload(self):
        execution = self.decision["future_private_execution"]
        self.assertEqual(execution["execution_limit"], 1)
        self.assertEqual(execution["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertEqual(execution["content_opens"], 1)
        self.assertTrue(execution["consumed_marker_before_private_content_open"])
        self.assertEqual(execution["success_route"], "MARC2VDR-R1")
        self.assertFalse(execution["success_authorizes_archive_member_or_payload"])
        self.assertFalse(execution["success_authorizes_MARC2_FW2"])

    def test_resource_caps_are_bounded_and_payload_bytes_are_zero(self):
        caps = self.decision["resource_boundary"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["private_input_bytes"], 418_755)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_local_header_or_member_bytes"], 0)
        self.assertEqual(caps["selected_future_reservation_cap_bytes"], 8 * 1024**3)

    def test_decision_only_counters_are_zero_except_green_verification(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                self.assertEqual(value, 0, key)

    def test_next_gate_forbids_early_private_and_FW2_execution(self):
        gate = self.decision["next_gate"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertTrue(gate["decision_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["wrapper_implementation_may_begin_before_green"])
        self.assertFalse(gate["private_manifest_operation_may_begin_before_green_wrapper"])
        self.assertTrue(gate["FW2_preregistration_may_follow_successful_structural_freeze"])
        self.assertFalse(gate["FW2_real_execution_may_begin_from_this_decision"])

    def test_claim_boundary_is_explicit_and_not_a_pivot(self):
        claim = self.decision["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["structural_selection_is_scientific_or_language_evidence"])
        self.assertIn("not neural data", claim["scientific_claim_not_established"])
        self.assertFalse(claim["current_scientific_claim_upgrade"])


if __name__ == "__main__":
    unittest.main()
