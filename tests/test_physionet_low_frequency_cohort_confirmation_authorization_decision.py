import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "physionet_low_frequency_cohort_confirmation_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT
    / "registries"
    / "physionet_low_frequency_cohort_confirmation_authorization_request.v0.json"
)
CONTRACT_PATH = (
    ROOT / "registries" / "physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
PACKET_PATH = (
    ROOT / "docs" / "PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md"
)
DOC_PATH = (
    ROOT / "docs" / "PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_DECISION.md"
)


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


class PhysioNetLowFrequencyCohortAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.physionet_low_frequency_cohort_confirmation_"
            "authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "580708fa1f24772a2f9d7cfd572a421b860a1f14",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"
            ]
        )
        self.assertEqual(decision["authorized_contract"]["sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(
            decision["authorized_contract"]["git_blob_sha1"],
            git_blob_sha1(CONTRACT_PATH),
        )
        self.assertEqual(decision["authorization_request"]["sha256"], sha256(REQUEST_PATH))
        self.assertEqual(
            decision["authorization_request"]["git_blob_sha1"],
            git_blob_sha1(REQUEST_PATH),
        )
        self.assertEqual(decision["authorization_packet"]["sha256"], sha256(PACKET_PATH))
        self.assertEqual(
            decision["authorization_packet"]["git_blob_sha1"],
            git_blob_sha1(PACKET_PATH),
        )

    def test_green_request_commit_and_both_jobs_are_exact(self):
        green = self.decision["green_request"]
        self.assertEqual(green["commit"], "580708fa1f24772a2f9d7cfd572a421b860a1f14")
        self.assertEqual(green["push_ci_run_id"], 31355270896)
        self.assertEqual(green["base_python_job_id"], 93353672957)
        self.assertEqual(green["optional_neuro_job_id"], 93353672996)
        self.assertEqual(green["push_ci_conclusion"], "success")
        self.assertEqual(green["base_python_job_conclusion"], "success")
        self.assertEqual(green["optional_neuro_job_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])

    def test_actual_user_words_are_preserved_without_fabricated_recital(self):
        user = self.decision["user_authorization"]
        actual = (
            "i dont want to type out exact auth sentences anymore -- keep going, "
            "move the needle, continue, you approved to go on"
        )
        self.assertEqual(user["actual_message_verbatim"], actual)
        self.assertEqual(user["actual_message_sha256"], hashlib.sha256(actual.encode()).hexdigest())
        self.assertEqual(self.doc.count(actual), 1)
        self.assertNotEqual(
            actual,
            self.request["authorization"]["exact_authorization_sentence"],
        )
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["procedural_recital_waived_for_this_decision"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_short_form_rule_keeps_separate_packet_bound_fail_closed_decisions(self):
        rule = self.decision["short_form_packet_rule"]
        for key in (
            "activated_by_this_maintainer_instruction",
            "separate_tier_c_permission_still_required",
            "exactly_one_active_packet_required",
            "packet_and_all_false_request_must_already_be_green",
            "assistant_must_have_just_named_packet_commit_ci_and_decision_gate",
            "maintainer_must_unambiguously_approve_continue_or_proceed",
            "decision_must_quote_actual_words_and_bind_immutable_scope",
            "decision_commit_must_be_remotely_green_before_implementation_or_access",
        ):
            self.assertTrue(rule[key], key)
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertEqual(
            rule["ambiguity_multiple_packets_changed_packet_or_missing_green_evidence_policy"],
            "fail_closed",
        )
        self.assertFalse(rule["release_destructive_hardware_or_claim_action_inferred_from_continue"])

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        self.assertEqual(
            self.contract["status"],
            "frozen_preregistration_exact_tier_c_authorization_pending",
        )
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(self.request["authorized_now"])
        self.assertFalse(self.request["authorization"]["exact_sentence_received_from_user"])
        self.assertTrue(
            self.decision["authorized_contract"][
                "remains_immutable_preregistration_snapshot"
            ]
        )
        self.assertTrue(
            self.decision["authorization_request"][
                "remains_immutable_and_pending_snapshot"
            ]
        )

    def test_authorized_actions_are_conditional_and_expansions_remain_false(self):
        authorization = self.decision["authorization"]
        expected_true = {
            "generated_fixture_and_mocked_transport_implementation_authorized_after_decision_green",
            "existing_exact_version_environment_reuse_authorized_after_decision_green",
            "metadata_reverification_authorized_after_implementation_green",
            "exact_72_edf_acquisition_authorized_after_implementation_green",
            "registered_72_edf_hash_and_semantic_parse_authorized_after_acquisition",
            "registered_header_annotation_signal_geometry_reads_authorized_after_acquisition",
            "target_firewalled_derivative_creation_authorized_after_acquisition",
            "bounded_participant_specific_training_and_inference_authorized_after_acquisition",
            "aggregate_hash_only_prediction_freeze_authorized_after_analysis",
            "one_combined_final_target_delivery_and_score_authorized_after_freeze_green",
            "invocation_created_temporary_cleanup_authorized_within_registered_stages",
        }
        flags = dict(authorization_flags(authorization))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 25)

    def test_registered_scope_matches_frozen_contract(self):
        run = self.decision["registered_sequence"]
        binding = self.contract["dataset_binding"]
        self.assertEqual(run["provider"], binding["provider"])
        self.assertEqual(run["dataset_id"], binding["dataset_id"])
        self.assertEqual(run["dataset_version"], binding["version"])
        self.assertEqual(run["subjects"], binding["participants"])
        self.assertEqual(run["execution_fit_runs"], binding["execution_fit_runs"])
        self.assertEqual(run["execution_final_run"], binding["execution_sealed_final_run"])
        self.assertEqual(run["imagery_fit_runs"], binding["imagery_fit_runs"])
        self.assertEqual(run["imagery_final_run"], binding["imagery_sealed_final_run"])
        self.assertEqual(run["file_count"], binding["file_count"])
        self.assertEqual(run["payload_bytes"], binding["exact_payload_bytes"])
        self.assertEqual(run["expected_fit_rows"], 720)
        self.assertEqual(run["expected_final_rows"], 360)
        self.assertEqual(run["condition_families"], 18)
        self.assertEqual(run["required_target_blind_inference_runs"], 216)
        self.assertEqual(run["maximum_verdict"], "WO9R-R4")

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.decision["required_execution_order"]
        decision_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_this_short_form_packet_bound_decision"
        )
        implementation = order.index(
            "implement_and_fixture_qualify_without_any_real_or_local_physionet_operation"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_exact_implementation"
        )
        acquisition = order.index(
            "metadata_reverify_and_acquire_only_the_registered_72_edf_bundle_once"
        )
        freeze_green = order.index("commit_push_and_obtain_green_ci_for_prediction_freeze")
        score = order.index(
            "deliver_the_same_360_final_targets_together_once_score_once_apply_router_and_stop"
        )
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, acquisition)
        self.assertLess(acquisition, freeze_green)
        self.assertLess(freeze_green, score)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_decision_commit_is_green"])
        self.assertFalse(rules["dependency_installation_may_occur"])
        self.assertFalse(
            rules[
                "edf_url_request_or_local_physionet_operation_may_begin_before_implementation_green"
            ]
        )
        self.assertFalse(rules["final_targets_may_open_before_prediction_freeze_commit_is_green"])
        self.assertFalse(rules["registered_acquisition_or_analysis_may_run_more_than_once"])

    def test_resource_caps_are_exact_contract_copies(self):
        decision_caps = self.decision["resource_boundary"]
        contract_caps = self.contract["resource_caps"]
        self.assertEqual(decision_caps["acquisition"], contract_caps["acquisition"])
        self.assertEqual(
            decision_caps["analysis_and_scoring"],
            contract_caps["analysis_and_scoring"],
        )

    def test_authorization_only_measurements_preserve_zero_real_operations(self):
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["github_ci_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "github_ci_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_remains_narrow(self):
        claim = self.decision["claim_boundary"]
        self.assertIn("twelve-person", claim["engineering_capability_authorized_for_testing"])
        self.assertIn("within EEGMMIDB", claim["maximum_after_clean_WO9R_R4"])
        unavailable = claim["scientific_claim_not_established"]
        for term in (
            "brain-specific",
            "independent-team",
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
