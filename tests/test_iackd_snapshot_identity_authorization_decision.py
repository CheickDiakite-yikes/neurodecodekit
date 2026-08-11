import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT / "registries" / "iackd_snapshot_identity_authorization_decision.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSnapshotIdentityAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_decision_is_packet_bound_and_not_yet_effective(self) -> None:
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "IACKD-M1A")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "ce847383ab1e327523cbc172bb6d3be417b46a11",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_proof_is_exact(self) -> None:
        proof = self.decision["green_request"]
        self.assertEqual(proof["commit"], "ce847383ab1e327523cbc172bb6d3be417b46a11")
        self.assertEqual(proof["push_CI_run_id"], 31484273623)
        self.assertEqual(proof["base_python_job_id"], 93755977352)
        self.assertEqual(proof["optional_neuro_job_id"], 93755977235)
        self.assertEqual(proof["base_python_job_conclusion"], "success")
        self.assertEqual(proof["optional_neuro_job_conclusion"], "success")
        self.assertTrue(proof["both_required_jobs_green"])

    def test_actual_user_message_is_preserved_exactly(self) -> None:
        user = self.decision["user_authorization"]
        message = "keep going, move the needle, continue, you approved to go on"
        self.assertEqual(user["actual_message_verbatim"], message)
        self.assertEqual(user["actual_message_UTF8_bytes"], 60)
        self.assertEqual(
            user["actual_message_SHA256"],
            hashlib.sha256(message.encode("utf-8")).hexdigest(),
        )
        self.assertEqual(user["communication_mode"], "short_form_packet_reference")
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_every_bound_artifact_hash_and_git_blob_match(self) -> None:
        for binding in self.decision["bound_artifacts"].values():
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(_sha256(path), binding["sha256"])
                self.assertEqual(
                    hashlib.sha1(b"blob " + str(path.stat().st_size).encode() + b"\0" + path.read_bytes()).hexdigest(),
                    binding["git_blob_sha1"],
                )

    def test_short_form_rule_was_satisfied_without_scope_expansion(self) -> None:
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["exactly_one_active_packet_required"])
        self.assertTrue(rule["packet_and_all_false_request_were_green_before_message"])
        self.assertTrue(rule["assistant_named_packet_commit_CI_scope_and_decision_gate"])
        self.assertTrue(rule["maintainer_unambiguously_directed_continue"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_immutable_scope"])
        self.assertTrue(rule["decision_commit_must_be_remotely_green_before_implementation_or_access"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])

    def test_authorization_is_conditional_and_metadata_only(self) -> None:
        authorization = self.decision["authorization"]
        self.assertTrue(authorization["wrapper_implementation_authorized_after_decision_green"])
        self.assertTrue(authorization["generated_and_mocked_qualification_authorized_after_decision_green"])
        self.assertTrue(authorization["machine_gate_authorized_after_wrapper_green"])
        self.assertTrue(authorization["one_public_GraphQL_request_authorized_after_wrapper_green"])
        self.assertTrue(authorization["one_bounded_response_read_hash_and_parse_authorized_after_wrapper_green"])
        self.assertTrue(authorization["one_private_manifest_and_public_report_authorized_after_wrapper_green"])
        for key in (
            "S3_payload_request_or_download_authorized_now",
            "local_IACKD_path_operation_authorized_now",
            "consumed_root_bundle_marker_executor_or_result_operation_authorized_now",
            "EEG_EOG_event_signal_trajectory_target_or_label_read_authorized_now",
            "derivative_model_training_inference_prediction_freeze_or_score_authorized_now",
            "dependency_installation_authorized_now",
            "retry_rerun_resume_restart_substitution_or_post_result_update_authorized_now",
            "release_hardware_destructive_or_scientific_claim_upgrade_authorized_now",
        ):
            with self.subTest(key=key):
                self.assertFalse(authorization[key])

    def test_registered_sequence_and_resources_match_request(self) -> None:
        sequence = self.decision["registered_sequence"]
        self.assertEqual(sequence["GraphQL_requests"], 1)
        self.assertEqual(sequence["request_body_bytes"], 355)
        self.assertEqual(sequence["response_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(sequence["S3_payload_requests"], 0)
        self.assertEqual(sequence["tree_rows"], 1679)
        self.assertEqual(sequence["selected_rows"], 1340)
        self.assertEqual((sequence["retries"], sequence["reruns"]), (0, 0))
        resources = self.decision["resource_boundary"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 2 * 1024 * 1024 * 1024)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["public_execution_wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)

    def test_execution_order_requires_both_green_milestones(self) -> None:
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "test_commit_push_and_obtain_green_CI_for_this_packet_bound_decision")
        self.assertLess(
            order.index("generated_and_mocked_transport_wrapper_implementation"),
            order.index("test_commit_push_and_obtain_green_CI_for_exact_wrapper"),
        )
        self.assertLess(
            order.index("test_commit_push_and_obtain_green_CI_for_exact_wrapper"),
            order.index("pre_consumption_machine_gate_and_private_marker"),
        )
        self.assertLess(
            order.index("pre_consumption_machine_gate_and_private_marker"),
            order.index("one_exact_public_GraphQL_request_response_canonicalization_and_stop"),
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
        self.assertTrue(gate["decision_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["wrapper_implementation_may_begin_before_green"])
        self.assertFalse(gate["public_operation_may_begin_before_green_wrapper"])
        self.assertFalse(gate["EEG_payload_access_may_begin"])
        claim = self.decision["claim_boundary"]
        self.assertIn("wrapper", claim["engineering_capability_authorized_for_testing"])
        self.assertIn("not EEG data", claim["scientific_claim_not_established"])

    def test_human_decision_quotes_message_and_boundaries(self) -> None:
        document = (
            ROOT / "docs" / "IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_DECISION.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "> keep going, move the needle, continue, you approved to go on",
            document,
        )
        self.assertIn("Engineering capability authorized for testing:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("authorizes no transfer of those payload bytes", document)


if __name__ == "__main__":
    unittest.main()
