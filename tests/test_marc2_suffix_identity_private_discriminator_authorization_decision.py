import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_authorization_decision.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_AUTHORIZATION_DECISION.md"
)


class Marc2SuffixIdentityPrivateDiscriminatorAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_suffix_identity_private_discriminator_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR15P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "8873796f772d7c2352d27aa9c0ad2be5278b67fe",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_and_proof_are_exact(self):
        request = self.decision["green_request"]
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(request["commit"], "08cef4bfacb126770c1a3a4be2fab58d1f7a276f")
        self.assertEqual(request["CI_run_id"], 32_450_174_692)
        self.assertEqual(request["base_python_job_id"], 96_677_085_658)
        self.assertEqual(request["optional_neuro_job_id"], 96_677_085_404)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 32_450_773_951)
        self.assertEqual(proof["base_python_job_id"], 96_678_759_155)
        self.assertEqual(proof["optional_neuro_job_id"], 96_678_759_451)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_actual_message_is_preserved_without_scope_inference(self):
        user = self.decision["user_authorization"]
        expected = "continue"
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"], hashlib.sha256(expected.encode()).hexdigest()
        )
        self.assertTrue(user["one_registered_two_stage_sequence_only"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_request_artifacts_match_bound_bytes_hashes_and_blobs(self):
        rows = self.decision["immutable_request_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 29_112)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_decision_artifacts_are_byte_exact(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

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
        self.assertTrue(authority["generated_wrapper_implementation_after_decision_green"])
        self.assertTrue(authority["one_private_structural_read_after_stage_1_green"])
        self.assertTrue(authority["one_VR15A_classifier_call_after_stage_1_green"])
        self.assertTrue(authority["one_nested_VR12A_call_after_stage_1_green"])
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["archive_member_or_payload_access_authorized_now"])
        self.assertFalse(authority["neural_derivative_creation_authorized_now"])
        self.assertFalse(authority["FW2_or_CIL1_execution_authorized_now"])

    def test_execution_order_preserves_all_remote_green_barriers(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[2], "exact_stage_1_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[3], "stage_1_proof_closeout_pushed_and_both_CI_jobs_green")
        self.assertIn("one_exact_private_structural_read_and_VR15A_call", order)
        self.assertIn("one_exact_nested_VR12A_call", order)
        self.assertTrue(order[-1].startswith("stop_before_archive_payload_neural"))

    def test_routes_resources_and_outputs_are_frozen(self):
        self.assertEqual(len(self.decision["private_route_contract"]), 16)
        self.assertEqual(
            [row["route"] for row in self.decision["private_route_contract"]],
            [f"MARC2VR15P-R{i}" for i in range(1, 17)],
        )
        self.assertTrue(
            all(
                not row["private_cohort_manifest_allowed"]
                for row in self.decision["private_route_contract"]
            )
        )
        generated = self.decision["generated_stage_requirements"]
        self.assertEqual(
            (generated["cases"], generated["orders"], generated["replays"]),
            (17, 2, 2),
        )
        self.assertEqual(generated["required_paths"], 68)
        self.assertGreaterEqual(generated["direct_refusal_minimum"], 100)
        caps = self.decision["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["signal_bytes"], 0)
        self.assertEqual(caps["target_bytes"], 0)

    def test_decision_only_counters_and_current_operations_are_zero(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 2)
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                self.assertEqual(value, 0, key)

    def test_next_gate_and_claim_boundary_fail_closed(self):
        gate = self.decision["next_gate"]
        claims = self.decision["claim_boundary"]
        self.assertTrue(gate["decision_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["stage_1_may_begin_before_decision_green"])
        self.assertFalse(gate["private_stage_may_begin_before_stage_1_proof_green"])
        self.assertFalse(gate["FW2_or_CIL1_may_execute_from_this_decision"])
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])

    def test_human_decision_states_delayed_effect_and_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("actual eight UTF-8 bytes", text)
        self.assertIn("This decision does not become effective", text)
        self.assertIn("all 17 VR15A cases", text)
        self.assertIn("creates no cohort manifest", text)
        self.assertIn("Engineering capability authorized after green decision", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
