import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc2_f03_private_discriminator_authorization_decision.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_F03_PRIVATE_DISCRIMINATOR_AUTHORIZATION_DECISION.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2F03PrivateDiscriminatorAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_f03_private_discriminator_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR11P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "136f7b999d3514bd8d62f8dc9e7d7c01b89662f7",
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
            request["commit"], "6e72c8f797201359777454a750b1dea9704665c0"
        )
        self.assertEqual(request["CI_run_id"], 32_009_557_248)
        self.assertEqual(request["base_python_job_id"], 95_326_004_060)
        self.assertEqual(request["optional_neuro_job_id"], 95_326_004_145)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 32_011_020_786)
        self.assertEqual(proof["base_python_job_id"], 95_330_380_822)
        self.assertEqual(proof["optional_neuro_job_id"], 95_330_380_918)
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
        expected = "okay lets continue"
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 18)
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
        self.assertTrue(authority["one_VR6_and_one_VR10B_call_after_wrapper_green"])
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["cohort_freeze_authorized_by_this_decision"])
        self.assertFalse(authority["archive_member_or_payload_access_authorized_now"])
        self.assertFalse(authority["neural_derivative_creation_authorized_now"])
        self.assertFalse(
            authority[
                "training_prediction_freeze_target_delivery_or_scoring_authorized_now"
            ]
        )

    def test_execution_order_has_both_remote_green_barriers(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[2], "exact_wrapper_commit_pushed_and_both_CI_jobs_green")
        self.assertIn(
            "new_root_preflight_and_marker_immediately_before_private_open", order
        )
        self.assertIn("one_aggregate_R1_to_R5_report_without_cohort", order)
        self.assertTrue(order[-1].startswith("stop_before_archive_payload_neural"))

    def test_paths_source_and_outputs_are_fixed_but_untouched(self):
        paths = self.decision["fixed_paths"]
        source = self.decision["registered_private_source"]
        output = self.decision["future_output_contract"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr11p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_f03_private_discriminator/v0",
        )
        self.assertEqual(paths["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["path_operations_at_decision_recording"], 0)
        self.assertEqual(source["content_opens_at_decision_recording"], 0)
        self.assertTrue(output["marker_immediately_before_private_content_open"])
        self.assertFalse(output["private_manifest_or_cohort_output_allowed"])
        self.assertEqual(output["output_operations_at_decision_recording"], 0)

    def test_five_route_firewall_is_exact(self):
        route = self.decision["five_route_contract"]
        self.assertEqual(route["expected_outer_VR6_route"], "MARC2VR6-F02")
        self.assertEqual(route["expected_nested_VR2_route"], "MARC2VR2-F03")
        self.assertEqual(
            list(route["VR10B_to_private_route_map"].values()),
            [
                "MARC2VR11P-R1",
                "MARC2VR11P-R2",
                "MARC2VR11P-R3",
                "MARC2VR11P-R4",
                "MARC2VR11P-R5",
            ],
        )
        self.assertFalse(route["VR10B_G1_allowed_as_private_result"])
        self.assertFalse(route["candidate_selection_or_cohort_retained"])

    def test_generated_matrix_and_resources_are_bounded(self):
        generated = self.decision["generated_qualification"]
        caps = self.decision["resource_boundary"]
        self.assertEqual(generated["generated_cases"], 6)
        self.assertEqual(generated["source_orders"], 2)
        self.assertEqual(generated["exact_replays"], 2)
        self.assertEqual(generated["exact_paths"], 24)
        self.assertGreaterEqual(generated["minimum_direct_mutations"], 70)
        self.assertFalse(generated["real_or_consumed_path_operation"])
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_signal_or_target_bytes"], 0)

    def test_decision_only_counters_are_zero_except_green_verification(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 2)
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                self.assertEqual(value, 0, key)

    def test_next_gate_and_claim_boundary_fail_closed(self):
        gate = self.decision["next_gate"]
        claim = self.decision["claim_boundary"]
        self.assertTrue(gate["decision_commit_required"])
        self.assertFalse(gate["wrapper_implementation_may_begin_before_green"])
        self.assertFalse(
            gate["readiness_or_private_operation_may_begin_before_green_wrapper"]
        )
        self.assertFalse(gate["FW2_or_CIL1_real_execution_may_begin_from_this_decision"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["structural_route_is_scientific_or_language_evidence"])
        self.assertIn("not neural data", claim["scientific_claim_not_established"])

    def test_human_decision_states_delayed_effect_and_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("actual 18 UTF-8 bytes", text)
        self.assertIn("This decision is not effective merely because", text)
        self.assertIn("one exact VR10B discriminator call", text)
        self.assertIn("FW2 and CIL1 remain closed", text)
        self.assertIn("Engineering capability authorized after green decision", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
