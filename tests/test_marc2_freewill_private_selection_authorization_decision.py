import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_private_selection_authorization_decision.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrivateSelectionAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_freewill_private_selection_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "MARC2-FW1A")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "d0a6eaa391b12f04da35bf277f6409f2750d40df",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_proof_is_exact(self):
        proof = self.decision["green_request"]
        self.assertEqual(proof["CI_run_id"], 31_679_428_199)
        self.assertEqual(proof["base_python_job_id"], 94_381_244_828)
        self.assertEqual(proof["optional_neuro_job_id"], 94_381_244_902)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["request_SHA256"],
            "2795818b0517bdd66a69e4039c98d3359c0115ef78d5f0be7ff8869511e5987d",
        )

    def test_bound_artifacts_are_current_and_byte_exact(self):
        for artifact in self.decision["bound_artifacts"]:
            path = ROOT / artifact["path"]
            with self.subTest(path=artifact["path"]):
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])

    def test_actual_message_is_preserved_without_fabricated_recital(self):
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            hashlib.sha256(user["actual_message_verbatim"].encode()).hexdigest(),
            user["actual_message_SHA256"],
        )
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_short_form_rule_is_packet_bound_and_no_scope_expands(self):
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["exactly_one_active_packet_required"])
        self.assertTrue(rule["packet_and_request_green_before_message"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(
            rule[
                "future_payload_neural_experiment_score_replication_or_language_authority_inferred"
            ]
        )

    def test_authority_is_conditional_and_payload_remains_closed(self):
        authority = self.decision["authorization"]
        self.assertTrue(authority["wrapper_implementation_after_decision_green"])
        self.assertTrue(authority["one_private_manifest_read_after_wrapper_green"])
        self.assertTrue(authority["one_target_free_private_selection_after_wrapper_green"])
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["payload_acquisition_or_download_authorized_now"])
        self.assertFalse(
            authority["archive_local_header_member_or_payload_access_authorized_now"]
        )
        self.assertFalse(
            authority["derivative_model_training_inference_prediction_freeze_or_score_authorized_now"]
        )

    def test_required_execution_order_has_both_remote_green_barriers(self):
        self.assertEqual(
            self.decision["required_execution_order"],
            [
                "decision_commit_pushed_and_both_CI_jobs_green",
                "generated_and_mocked_wrapper_implementation_and_qualification",
                "exact_wrapper_commit_pushed_and_both_CI_jobs_green",
                "one_registered_private_manifest_selection_invocation",
                "one_aggregate_result_commit_pushed_and_both_CI_jobs_green",
                "stop_before_archive_payload_and_prepare_only_MARC2_FW2_packet",
            ],
        )

    def test_private_source_is_bound_but_untouched(self):
        source = self.decision["registered_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["entries"], 1_227)
        self.assertEqual(source["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["content_opens_at_decision_recording"], 0)
        self.assertEqual(source["private_bytes_at_decision_recording"], 0)

    def test_wrapper_qualification_requires_all_fifty_eight_refusals(self):
        qualification = self.decision["wrapper_qualification"]
        self.assertEqual(qualification["inherited_selector_mutations"], 40)
        self.assertEqual(qualification["wrapper_specific_mutations"], 18)
        self.assertEqual(qualification["total_mutations"], 58)
        self.assertTrue(qualification["execute_proof_disabled_until_green"])
        self.assertFalse(
            qualification["generic_source_output_subject_seed_cap_split_member_URL_or_credential_override"]
        )

    def test_future_execution_is_one_shot_and_stops_before_payload(self):
        execution = self.decision["future_private_execution"]
        self.assertEqual(execution["execution_limit"], 1)
        self.assertEqual(execution["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertEqual(execution["content_opens"], 1)
        self.assertTrue(execution["consumed_marker_before_private_content_open"])
        self.assertFalse(execution["success_authorizes_archive_member_or_payload"])
        self.assertFalse(execution["success_authorizes_MARC2_FW2"])
        self.assertFalse(execution["success_is_scientific_result"])

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

    def test_next_gate_forbids_early_implementation_and_private_access(self):
        verification = self.decision["local_verification"]
        self.assertEqual(verification["dependency_light_unittest_tests"], 3_031)
        self.assertEqual(verification["optional_neuro_unittest_tests"], 3_102)
        self.assertEqual(
            verification["optional_neuro_shard_a_m_tests"]
            + verification["optional_neuro_shard_n_z_tests"],
            verification["optional_neuro_unittest_tests"],
        )
        self.assertTrue(
            verification[
                "optional_neuro_complete_inventory_passed_across_fresh_process_shards"
            ]
        )
        self.assertFalse(verification["historical_test_or_resource_cap_modified"])

        gate = self.decision["next_gate"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertTrue(gate["decision_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["wrapper_implementation_may_begin_before_green"])
        self.assertFalse(gate["private_manifest_operation_may_begin_before_green_wrapper"])
        self.assertFalse(gate["payload_acquisition_or_MARC2_FW2_may_begin"])

    def test_claim_boundary_is_explicit_and_not_a_pivot(self):
        claim = self.decision["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["private_selection_is_scientific_or_language_evidence"])
        self.assertIn("not neural data", claim["scientific_claim_not_established"])
        self.assertFalse(claim["current_scientific_claim_upgrade"])


if __name__ == "__main__":
    unittest.main()
