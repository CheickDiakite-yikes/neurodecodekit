import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc1_http_identity_live_recovery_authorization_decision.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha1(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(body)).encode("ascii") + b"\0" + body
    ).hexdigest()


class Marc1HttpIdentityLiveRecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_decision_is_packet_bound_and_not_yet_effective(self) -> None:
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc1_http_identity_live_recovery_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC1-HT1A")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "27f39aee5f056eafc81b615cec4a178a41a6c5d2",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_proof_is_exact(self) -> None:
        proof = self.decision["green_request"]
        self.assertEqual(proof["commit"], "27f39aee5f056eafc81b615cec4a178a41a6c5d2")
        self.assertEqual(proof["push_CI_run_id"], 31_586_256_906)
        self.assertEqual(proof["base_python_job_id"], 94_080_678_529)
        self.assertEqual(proof["optional_neuro_job_id"], 94_080_678_738)
        self.assertEqual(proof["base_python_job_conclusion"], "success")
        self.assertEqual(proof["optional_neuro_job_conclusion"], "success")
        self.assertTrue(proof["both_required_jobs_green"])

    def test_actual_user_message_is_preserved_exactly(self) -> None:
        user = self.decision["user_authorization"]
        message = "approved, continue, achieve a scientific claim, achieve thought to text 😎"
        self.assertEqual(user["actual_message_verbatim"], message)
        self.assertEqual(user["actual_message_UTF8_bytes"], 76)
        self.assertEqual(
            user["actual_message_SHA256"],
            hashlib.sha256(message.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(user["communication_mode"], "short_form_packet_reference")
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])
        self.assertTrue(user["research_objective_preserved"])
        self.assertFalse(user["positive_result_predeclared"])

    def test_every_bound_artifact_hash_and_git_blob_match(self) -> None:
        for binding in self.decision["bound_artifacts"].values():
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(_sha256(path), binding["sha256"])
                self.assertEqual(_git_blob_sha1(path), binding["git_blob_sha1"])

    def test_short_form_rule_was_satisfied_without_scope_expansion(self) -> None:
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["exactly_one_active_packet_required"])
        self.assertTrue(rule["packet_and_all_false_request_were_green_before_message"])
        self.assertTrue(rule["assistant_named_packet_commit_CI_scope_and_decision_gate"])
        self.assertTrue(rule["maintainer_unambiguously_approved_and_directed_continue"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_immutable_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(rule["aspirational_goal_predeclares_scientific_outcome"])

    def test_authorization_is_conditional_and_metadata_only(self) -> None:
        authorization = self.decision["authorization"]
        self.assertTrue(
            authorization["additive_wrapper_implementation_authorized_after_decision_green"]
        )
        self.assertTrue(
            authorization[
                "generated_and_mocked_wrapper_qualification_authorized_after_decision_green"
            ]
        )
        self.assertTrue(authorization["machine_gate_authorized_after_wrapper_green"])
        self.assertTrue(
            authorization[
                "one_private_and_one_public_metadata_selection_authorized_after_wrapper_green"
            ]
        )
        for key in (
            "consumed_executor_or_old_root_access_authorized_now",
            "local_header_member_or_archive_payload_access_authorized_now",
            "payload_acquisition_or_download_authorized_now",
            "signal_channel_geometry_event_onset_quality_or_target_read_authorized_now",
            "derivative_model_training_inference_prediction_freeze_or_score_authorized_now",
            "dependency_installation_authorized_now",
            "retry_rerun_resume_restart_substitution_or_post_result_update_authorized_now",
            "release_hardware_destructive_or_scientific_claim_upgrade_authorized_now",
        ):
            with self.subTest(key=key):
                self.assertFalse(authorization[key])

    def test_registered_sequence_is_exact_and_bounded(self) -> None:
        sequence = self.decision["registered_sequence"]
        freewill = sequence["Freewill_private_inventory"]
        wrist = sequence["Wrist_public_metadata"]
        self.assertEqual(freewill["bytes"], 418_755)
        self.assertEqual(freewill["mode"], "0600")
        self.assertEqual(freewill["content_opens"], 1)
        self.assertEqual(freewill["payload_opens"], 0)
        self.assertEqual((wrist["record_id"], wrist["version"]), (29_666_735, 3))
        self.assertEqual(wrist["accepted_body_count"], 1)
        self.assertEqual(wrist["accepted_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(wrist["HTTP_request_attempt_cap"], 3)
        self.assertEqual(wrist["payload_requests"], 0)
        self.assertEqual((sequence["retries"], sequence["reruns"]), (0, 0))

    def test_semantics_selection_and_resources_match_request(self) -> None:
        transport = self.decision["transport_contract"]
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_case_insensitive_identity_accepted"])
        self.assertTrue(transport["all_actual_codings_refused"])
        self.assertTrue(transport["duplicate_list_and_transfer_coding_refused"])
        self.assertEqual(transport["decoding_or_decompression_operations"], 0)
        selection = self.decision["selection_contract"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_selected_run_bundles"], 72)
        self.assertEqual(selection["Freewill_selected_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertFalse(selection["size_CRC_quality_target_or_outcome_may_affect_selection"])
        resources = self.decision["resource_boundary"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 12 * 1024 * 1024 * 1024)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["real_selection_wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)

    def test_execution_order_requires_both_green_milestones_and_new_root(self) -> None:
        order = self.decision["required_execution_order"]
        self.assertEqual(
            order[0],
            "test_commit_push_and_obtain_green_CI_for_this_packet_bound_decision",
        )
        self.assertLess(
            order.index("generated_and_mocked_additive_wrapper_implementation"),
            order.index("test_commit_push_and_obtain_green_CI_for_exact_additive_wrapper"),
        )
        self.assertLess(
            order.index("test_commit_push_and_obtain_green_CI_for_exact_additive_wrapper"),
            order.index("pre_consumption_machine_gate_and_new_private_marker"),
        )
        wrapper = self.decision["wrapper_isolation"]
        self.assertTrue(wrapper["old_private_invocation_root_forbidden"])
        self.assertFalse(wrapper["consumed_live_executor_import_call_or_modification_allowed"])
        self.assertNotEqual(
            wrapper["new_private_invocation_root_relative_path"],
            wrapper["old_private_invocation_root_relative_path"],
        )

    def test_all_decision_only_operation_counters_are_zero(self) -> None:
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["GitHub_CI_verification_calls"], 1)
        for key, value in measurements.items():
            if key not in {"GitHub_CI_verification_calls", "end_to_end_latency_measured"}:
                with self.subTest(key=key):
                    self.assertEqual(value, 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_next_gate_and_claim_boundary_are_explicit(self) -> None:
        gate = self.decision["next_gate"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["additive_wrapper_implementation_may_begin_before_green"])
        self.assertFalse(gate["real_metadata_selection_may_begin_before_green_wrapper"])
        self.assertFalse(gate["payload_acquisition_may_begin"])
        claim = self.decision["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["positive_scientific_result_predeclared"])
        self.assertIn("not neural data", claim["scientific_claim_not_established"])

    def test_human_decision_quotes_message_and_boundaries(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_DECISION.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "> approved, continue, achieve a scientific claim, achieve thought to text 😎",
            document,
        )
        self.assertIn("Engineering capability authorized for testing:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("same path", document)
        self.assertIn("authorizes moving zero payload bytes", document)


if __name__ == "__main__":
    unittest.main()
