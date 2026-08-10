import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT / "registries" / "iackd_cue_action_dissociation_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT / "registries" / "iackd_cue_action_dissociation_authorization_request.v0.json"
)
CONTRACT_PATH = ROOT / "registries" / "iackd_cue_action_dissociation_contract.v0.json"
PACKET_PATH = ROOT / "docs" / "IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_PACKET.md"
DOC_PATH = ROOT / "docs" / "IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_DECISION.md"


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


class IACKDCueActionDissociationAuthorizationDecisionTests(unittest.TestCase):
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
            "neurodecodekit.iackd_cue_action_dissociation_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "ef78c061682781d9decd3ecc9dca55e99ea86e5d",
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
        self.assertEqual(green["commit"], "ef78c061682781d9decd3ecc9dca55e99ea86e5d")
        self.assertEqual(green["push_ci_run_id"], 31_401_738_032)
        self.assertEqual(green["base_python_job_id"], 93_498_128_228)
        self.assertEqual(green["optional_neuro_job_id"], 93_498_128_143)
        self.assertEqual(green["push_ci_conclusion"], "success")
        self.assertEqual(green["base_python_job_conclusion"], "success")
        self.assertEqual(green["optional_neuro_job_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(green["current_verification_calls"], 1)

    def test_actual_user_words_are_preserved_without_fabricated_recital(self):
        user = self.decision["user_authorization"]
        actual = "keep going, move the needle, continue, you approved to go on"
        self.assertEqual(user["actual_message_verbatim"], actual)
        self.assertEqual(user["actual_message_sha256"], hashlib.sha256(actual.encode()).hexdigest())
        self.assertEqual(self.doc.count(actual), 1)
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["procedural_recital_waived_for_this_decision"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_short_form_rule_is_packet_bound_and_fail_closed(self):
        rule = self.decision["short_form_packet_rule"]
        for key in (
            "separate_tier_c_permission_satisfied_for_this_packet",
            "exactly_one_active_packet_required",
            "packet_and_all_false_request_were_green_before_message",
            "assistant_named_packet_commit_ci_scope_and_decision_gate",
            "maintainer_unambiguously_said_continue",
            "decision_quotes_actual_words_and_binds_immutable_scope",
            "decision_commit_must_be_remotely_green_before_implementation_or_access",
        ):
            self.assertTrue(rule[key], key)
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertEqual(
            rule["ambiguity_multiple_packets_changed_packet_or_missing_green_evidence_policy"],
            "fail_closed",
        )

    def test_contract_and_request_remain_immutable_pending_snapshots(self):
        self.assertEqual(
            self.contract["status"],
            "frozen_preregistration_exact_packet_bound_tier_c_decision_pending",
        )
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertTrue(
            self.decision["authorized_contract"]["remains_immutable_preregistration_snapshot"]
        )
        self.assertTrue(
            self.decision["authorization_request"]["remains_immutable_and_pending_snapshot"]
        )

    def test_authorized_actions_are_conditional_and_expansions_remain_false(self):
        expected_true = {
            "generated_fixture_and_mocked_transport_implementation_authorized_after_decision_green",
            "existing_exact_version_environment_reuse_authorized_after_decision_green",
            "metadata_reverification_authorized_after_implementation_green",
            "exact_1340_object_acquisition_authorized_after_implementation_green",
            "registered_object_hash_and_semantic_parse_authorized_after_acquisition",
            "registered_EEG_EOG_marker_event_ball_kinematic_geometry_and_sampling_reads_authorized_after_acquisition",
            "target_firewalled_derivative_creation_authorized_after_acquisition",
            "bounded_participant_hand_training_and_inference_authorized_after_acquisition",
            "aggregate_hash_only_prediction_freeze_authorized_after_analysis",
            "one_combined_dual_target_delivery_and_score_authorized_after_freeze_green",
            "invocation_created_temporary_cleanup_authorized_within_registered_stages",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 25)

    def test_registered_scope_matches_frozen_contract_and_request(self):
        run = self.decision["registered_sequence"]
        binding = self.contract["dataset_binding"]
        requested = self.request["requested_scope"]
        self.assertEqual(run["provider"], binding["provider"])
        self.assertEqual(run["dataset_id"], binding["accession"])
        self.assertEqual(run["dataset_version"], binding["version"])
        self.assertEqual(run["participants"], binding["participant_ids"])
        self.assertEqual(run["participant_hand_units"], binding["participant_hand_unit_count"])
        self.assertEqual(run["BIDS_runs"], binding["bids_run_count"])
        self.assertEqual(run["object_count"], requested["object_count"])
        self.assertEqual(run["payload_bytes"], requested["payload_bytes"])
        self.assertEqual(run["maximum_parameter_update_fits"], 300)
        self.assertEqual(run["required_prediction_sets"], 420)
        self.assertEqual(run["maximum_verdict"], "IACKD-R4")

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.decision["required_execution_order"]
        decision_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_this_packet_bound_decision"
        )
        implementation = order.index(
            "implement_and_fixture_qualify_without_any_real_or_local_IACKD_operation"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_exact_implementation"
        )
        acquisition = order.index(
            "metadata_reverify_and_acquire_only_the_registered_1340_object_bundle_once"
        )
        freeze_green = order.index("commit_push_and_obtain_green_ci_for_prediction_freeze")
        score = order.index(
            "deliver_both_target_views_together_once_score_once_apply_router_and_stop"
        )
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, acquisition)
        self.assertLess(acquisition, freeze_green)
        self.assertLess(freeze_green, score)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["implementation_may_begin_before_decision_commit_is_green"])
        self.assertFalse(rules["dependency_installation_or_version_substitution_may_occur"])
        self.assertFalse(
            rules[
                "metadata_payload_or_local_IACKD_operation_may_begin_before_implementation_green"
            ]
        )
        self.assertFalse(rules["final_targets_may_open_before_prediction_freeze_commit_is_green"])
        self.assertFalse(rules["registered_acquisition_or_analysis_may_run_more_than_once"])

    def test_resource_caps_are_exact_request_copies(self):
        self.assertEqual(self.decision["resource_boundary"], self.request["resource_caps"])

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
        self.assertIn("IACKD cue-to-action reversal", claim["engineering_capability_authorized_for_testing"])
        self.assertIn("within-IACKD", claim["maximum_after_clean_IACKD_R4"])
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
