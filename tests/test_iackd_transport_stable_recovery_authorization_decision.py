import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "iackd_transport_stable_recovery_authorization_decision.v0.json"
)
REQUEST_PATH = (
    ROOT
    / "registries"
    / "iackd_transport_stable_recovery_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT / "docs" / "IACKD_TRANSPORT_STABLE_RECOVERY_AUTHORIZATION_DECISION.md"
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


class IACKDTransportStableRecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_bound_hashes_are_exact(self) -> None:
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.iackd_transport_stable_recovery_authorization_decision",
        )
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "525e97e64d04c64aa3243f94790dd70db5fd30e7",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_both_CI_jobs_green"
            ]
        )
        for binding in self.decision["bound_artifacts"].values():
            path = ROOT / binding["path"]
            self.assertEqual(binding["sha256"], sha256(path), binding["path"])
            self.assertEqual(binding["git_blob_sha1"], git_blob_sha1(path))

    def test_green_request_and_both_jobs_are_exact(self) -> None:
        green = self.decision["green_request"]
        self.assertEqual(green["commit"], "525e97e64d04c64aa3243f94790dd70db5fd30e7")
        self.assertEqual(green["push_CI_run_id"], 31475356506)
        self.assertEqual(green["base_python_job_id"], 93727674791)
        self.assertEqual(green["optional_neuro_job_id"], 93727674875)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(green["verification_calls"], 1)

    def test_actual_maintainer_word_is_preserved_without_recital(self) -> None:
        user = self.decision["user_authorization"]
        actual = "continue"
        self.assertEqual(user["actual_message_verbatim"], actual)
        self.assertEqual(
            user["actual_message_sha256"],
            hashlib.sha256(actual.encode()).hexdigest(),
        )
        self.assertEqual(self.doc.count("> continue"), 1)
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["procedural_recital_waived_for_this_decision"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertEqual(user["sole_active_Tier_C_packet"], "IACKD-2R")

    def test_request_remains_an_immutable_all_false_snapshot(self) -> None:
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_authorized_actions_are_conditional_and_expansions_false(self) -> None:
        expected_true = {
            "additive_executor_implementation_authorized_after_decision_green",
            "generated_fixture_and_mock_transport_qualification_authorized_after_decision_green",
            "existing_exact_optional_environment_reuse_authorized_after_decision_green",
            "pre_consumption_machine_safety_check_authorized_after_implementation_green",
            "four_body_metadata_reverification_authorized_after_implementation_green",
            "exact_1340_object_fresh_stream_authorized_after_implementation_green",
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

    def test_only_transport_delta_and_resource_strengthening_are_allowed(self) -> None:
        delta = self.decision["allowed_protocol_delta"]
        self.assertEqual(delta["changed_fields"], ["small_metadata_response_framing_policy"])
        self.assertTrue(delta["scientific_parent_inherited_unchanged"])
        self.assertTrue(delta["large_payload_integrity_inherited_unchanged"])
        self.assertTrue(delta["resource_safety_may_only_strengthen"])
        self.assertFalse(delta["post_result_tuning_or_update_allowed"])

    def test_registered_scope_matches_the_request(self) -> None:
        run = self.decision["registered_sequence"]
        requested = self.request["requested_scope"]
        self.assertEqual(run["provider"], requested["provider"])
        self.assertEqual(run["dataset_id"], requested["dataset_id"])
        self.assertEqual(run["participant_count"], requested["participant_count"])
        self.assertEqual(run["participant_hand_units"], requested["participant_hand_units"])
        self.assertEqual(run["object_count"], requested["payload_requests"])
        self.assertEqual(run["payload_bytes"], requested["payload_bytes"])
        self.assertEqual(run["required_parameter_update_fits"], requested["parameter_update_fits"])
        self.assertEqual(run["required_prediction_sets"], requested["prediction_sets"])
        self.assertEqual(run["maximum_verdict"], requested["maximum_verdict"])

    def test_order_requires_green_decision_executor_and_freeze(self) -> None:
        order = self.decision["required_execution_order"]
        decision_green = order.index(
            "test_commit_push_and_obtain_green_CI_for_this_packet_bound_decision"
        )
        implementation = order.index(
            "implement_and_fixture_qualify_new_additive_executor_without_real_public_or_local_IACKD_operation"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_CI_for_exact_additive_executor"
        )
        safety = order.index("pre_consumption_disk_thread_and_machine_load_gate")
        consumed = order.index(
            "write_new_private_consumed_marker_before_first_real_request"
        )
        freeze_green = order.index(
            "commit_push_and_obtain_green_CI_for_prediction_freeze"
        )
        score = order.index(
            "deliver_both_final_target_views_together_once_score_once_apply_router_and_stop"
        )
        self.assertLess(decision_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, safety)
        self.assertLess(safety, consumed)
        self.assertLess(consumed, freeze_green)
        self.assertLess(freeze_green, score)

    def test_resource_caps_are_exact_request_copies(self) -> None:
        self.assertEqual(
            self.decision["resource_boundary"],
            self.request["resource_caps"],
        )
        safety = self.decision["resource_boundary"]["pre_consumption_machine_safety"]
        self.assertEqual(safety["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(safety["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertTrue(safety["failure_occurs_before_consumed_marker"])

    def test_authorization_only_measurements_are_zero(self) -> None:
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["GitHub_CI_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "GitHub_CI_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_ceiling_remains_narrow(self) -> None:
        claim = self.decision["claim_boundary"]
        self.assertIn(
            "target-firewalled public IACKD dual reversal",
            claim["engineering_capability_authorized_for_testing"],
        )
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
