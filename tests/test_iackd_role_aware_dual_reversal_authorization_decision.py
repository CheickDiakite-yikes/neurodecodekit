import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_authorization_request.v0.json"
)
CONTRACT_PATH = (
    ROOT / "registries" / "iackd_role_aware_dual_reversal_contract.v0.json"
)
DOC_PATH = (
    ROOT / "docs" / "IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_DECISION.md"
)
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_role_aware_dual_reversal_implementation.py": (
        "0721e83517069bed52127df2ae75234e1167233bf7c14f5d27091b22e748649b",
        "ccde4da03f989909da36d7ddaa26a40ef1f71ff7",
    ),
    "tests/test_iackd_role_aware_dual_reversal_synthetic_result.py": (
        "9145e431652f7aae86e1e9a9f501631ffc45dfece78658abe4a3d3cb2a96ba30",
        "f923a4c223d5a46bc2bf549557d090da5874e5a2",
    ),
    "tests/test_iackd_role_aware_dual_reversal_authorization_request.py": (
        "caa60905d45cdb62d2a16ead5355d19df8186be2f22d573bbf145abad797baa3",
        "ba00d1b089224631cefb652bd4b3cb967b75521b",
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if "authorized_" in key:
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class IACKDRoleAwareDualReversalAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_all_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "862141f6729182f36accce38ce42a3631feb7232",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_both_CI_jobs_green"
            ]
        )
        for binding in decision["bound_artifacts"].values():
            path = ROOT / binding["path"]
            if binding["path"] in HISTORICAL_MUTABLE_BINDINGS:
                expected_sha256, expected_blob = HISTORICAL_MUTABLE_BINDINGS[
                    binding["path"]
                ]
                self.assertEqual(binding["sha256"], expected_sha256, binding["path"])
                self.assertEqual(
                    binding["git_blob_sha1"], expected_blob, binding["path"]
                )
            else:
                self.assertEqual(binding["sha256"], sha256(path), binding["path"])
                self.assertEqual(
                    binding["git_blob_sha1"], git_blob_sha1(path), binding["path"]
                )

    def test_green_request_commit_and_both_jobs_are_exact(self):
        green = self.decision["green_request"]
        self.assertEqual(
            green["commit"], "862141f6729182f36accce38ce42a3631feb7232"
        )
        self.assertEqual(green["push_CI_run_id"], 31_454_131_606)
        self.assertEqual(green["base_python_job_id"], 93_664_349_787)
        self.assertEqual(green["optional_neuro_job_id"], 93_664_349_786)
        self.assertEqual(green["base_python_job_conclusion"], "success")
        self.assertEqual(green["optional_neuro_job_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(green["verification_calls"], 1)

    def test_actual_maintainer_word_is_preserved_without_fabricated_recital(self):
        user = self.decision["user_authorization"]
        actual = "continue"
        self.assertEqual(user["actual_message_verbatim"], actual)
        self.assertEqual(
            user["actual_message_sha256"], hashlib.sha256(actual.encode()).hexdigest()
        )
        self.assertEqual(self.doc.count("> continue"), 1)
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["procedural_recital_waived_for_this_decision"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])
        self.assertEqual(user["sole_active_Tier_C_packet"], "IACKD-2")

    def test_short_form_rule_is_packet_bound_and_fail_closed(self):
        rule = self.decision["short_form_packet_rule"]
        for key in (
            "separate_Tier_C_permission_satisfied_for_this_packet",
            "exactly_one_active_packet_required",
            "packet_and_all_false_request_were_green_before_message",
            "assistant_named_packet_commit_CI_scope_and_decision_gate",
            "maintainer_unambiguously_said_continue",
            "decision_quotes_actual_words_and_binds_immutable_scope",
            "decision_commit_must_be_remotely_green_before_implementation_or_access",
        ):
            self.assertTrue(rule[key], key)
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertEqual(
            rule[
                "ambiguity_multiple_packets_changed_packet_or_missing_green_evidence_policy"
            ],
            "fail_closed",
        )

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        self.assertEqual(
            self.contract["status"],
            "prospective_registration_frozen_real_execution_unauthorized",
        )
        self.assertEqual(
            self.request["status"], "awaiting_new_packet_bound_maintainer_decision"
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_authorized_actions_are_conditional_and_expansions_remain_false(self):
        expected_true = {
            "generated_real_executor_implementation_authorized_after_decision_green",
            "generated_fixture_and_mock_transport_qualification_authorized_after_decision_green",
            "existing_exact_version_environment_reuse_authorized_after_decision_green",
            "metadata_reverification_authorized_after_implementation_green",
            "exact_1340_object_fresh_streaming_acquisition_authorized_after_implementation_green",
            "registered_payload_hash_and_semantic_parse_authorized_within_stream",
            "registered_EEG_EOG_marker_event_ball_Leap_channel_geometry_and_sampling_reads_authorized_within_stream",
            "target_firewalled_derivative_and_split_creation_authorized_within_stream",
            "exact_660_parameter_update_fits_authorized_after_complete_derivatives",
            "exact_900_target_blind_prediction_sets_authorized_after_complete_derivatives",
            "aggregate_hash_only_prediction_freeze_authorized_after_analysis",
            "one_combined_dual_target_delivery_and_score_authorized_after_freeze_green",
            "invocation_created_temporary_raw_group_cleanup_authorized_after_derivative_promotion",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 29)

    def test_registered_scope_matches_request_and_required_decision_shape(self):
        run = self.decision["registered_sequence"]
        requested = self.request["requested_scope"]
        required = self.request["required_decision_shape"]
        self.assertEqual(run["provider"], requested["provider"])
        self.assertEqual(run["dataset_id"], requested["dataset_id"])
        self.assertEqual(run["dataset_version"], requested["version"])
        self.assertEqual(run["participant_count"], requested["participant_count"])
        self.assertEqual(run["participant_hand_units"], requested["participant_hand_units"])
        self.assertEqual(run["arms"], requested["arms"])
        self.assertEqual(run["BIDS_run_count"], requested["BIDS_run_count"])
        self.assertEqual(run["object_count"], required["real_payload_requests"])
        self.assertEqual(run["payload_bytes"], required["real_payload_bytes"])
        self.assertEqual(
            run["required_parameter_update_fits"], required["parameter_update_fits"]
        )
        self.assertEqual(run["required_prediction_sets"], required["prediction_sets"])
        self.assertEqual(
            run["prediction_freeze_commits"], required["prediction_freeze_commits"]
        )
        self.assertEqual(run["final_target_deliveries"], required["target_deliveries"])
        self.assertEqual(run["final_scoring_events"], required["scoring_events"])
        self.assertEqual(run["maximum_verdict"], required["maximum_verdict"])
        self.assertEqual(run["retries"], 0)
        self.assertEqual(run["reruns"], 0)
        self.assertEqual(run["post_target_updates"], 0)

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.decision["required_execution_order"]
        decision_green = order.index(
            "test_commit_push_and_obtain_green_CI_for_this_packet_bound_decision"
        )
        implementation = order.index(
            "implement_and_fixture_qualify_separate_real_executor_without_any_real_public_or_local_IACKD_operation"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_CI_for_exact_real_executor_implementation"
        )
        consumed = order.index("write_private_consumed_marker_before_first_real_request")
        acquisition = order.index(
            "metadata_reverify_and_stream_only_the_registered_1340_objects_once"
        )
        freeze_green = order.index(
            "commit_push_and_obtain_green_CI_for_prediction_freeze"
        )
        score = order.index(
            "deliver_both_final_target_views_together_once_score_once_apply_router_and_stop"
        )
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, consumed)
        self.assertLess(consumed, acquisition)
        self.assertLess(acquisition, freeze_green)
        self.assertLess(freeze_green, score)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_decision_commit_is_green"])
        self.assertFalse(
            rules[
                "dependency_installation_version_substitution_or_tooling_network_may_occur"
            ]
        )
        self.assertFalse(
            rules[
                "metadata_payload_or_local_IACKD_operation_may_begin_before_implementation_green"
            ]
        )
        self.assertFalse(rules["old_retained_IACKD_bundle_may_be_used"])
        self.assertFalse(
            rules["final_targets_may_open_before_prediction_freeze_commit_is_green"]
        )
        self.assertFalse(
            rules["registered_acquisition_analysis_or_score_may_run_more_than_once"]
        )

    def test_resource_caps_are_exact_request_copies(self):
        self.assertEqual(self.decision["resource_boundary"], self.request["resource_caps"])

    def test_authorization_only_measurements_preserve_zero_real_operations(self):
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["GitHub_CI_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "GitHub_CI_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_remains_narrow(self):
        claim = self.decision["claim_boundary"]
        self.assertIn(
            "target-firewalled public IACKD dual reversal",
            claim["engineering_capability_authorized_for_testing"],
        )
        self.assertIn("Within IACKD", claim["maximum_after_clean_IACKD2_R5"])
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "brain-specific",
            "independent replication",
            "unseen-person",
            "typing",
            "thought decoding",
            "real-time",
            "portable hardware",
            "clinical",
        ):
            self.assertIn(term, unavailable)


if __name__ == "__main__":
    unittest.main()
