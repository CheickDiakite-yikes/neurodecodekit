import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries/marc2_published_task_private_confirmation_authorization_decision.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs/MARC_2_PUBLISHED_TASK_PRIVATE_CONFIRMATION_AUTHORIZATION_DECISION.md"
)


class Marc2PublishedTaskPrivateConfirmationAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_published_task_private_confirmation_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR20P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "88b3b4aaa4436655ce6f4de65215982e2b8ff9de",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_and_proof_are_exact(self):
        request = self.decision["green_request"]
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(request["commit"], "bef2391d8edf92c5edf8a3624831e50430636626")
        self.assertEqual(request["CI_run_id"], 32_489_589_922)
        self.assertEqual(request["base_python_job_id"], 96_793_861_959)
        self.assertEqual(request["optional_neuro_job_id"], 96_793_861_717)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 32_490_587_975)
        self.assertEqual(proof["base_python_job_id"], 96_797_011_698)
        self.assertEqual(proof["optional_neuro_job_id"], 96_797_011_783)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_actual_message_is_preserved_without_scope_inference(self):
        user = self.decision["user_authorization"]
        expected = "conitnue"
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"], hashlib.sha256(expected.encode()).hexdigest()
        )
        self.assertTrue(user["unambiguous_transposition_typo_of_continue"])
        self.assertEqual(user["sole_active_Tier_C_packet"], "MARC2-VR20P")
        self.assertTrue(user["one_registered_two_stage_sequence_only"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_bound_request_and_proof_artifacts_are_exact(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 46_756)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_decision_artifacts_are_byte_exact(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_authority_is_delayed_and_payload_work_remains_closed(self):
        authority = self.decision["authorization"]
        self.assertTrue(authority["generated_wrapper_implementation_after_decision_green"])
        self.assertTrue(authority["one_private_structural_read_after_stage_1_proof_green"])
        self.assertTrue(authority["one_VR20A_call_after_stage_1_proof_green"])
        self.assertTrue(authority["one_private_cohort_freeze_on_R1"])
        self.assertFalse(authority["implementation_or_private_access_authorized_now"])
        self.assertFalse(authority["archive_member_or_payload_access_authorized_now"])
        self.assertFalse(authority["neural_derivative_creation_authorized_now"])
        self.assertFalse(authority["MARC2_FW2_or_CIL1_real_execution_authorized_now"])

    def test_execution_order_preserves_both_remote_barriers(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[2], "exact_stage_1_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[3], "stage_1_proof_closeout_pushed_and_both_CI_jobs_green")
        self.assertIn("one_exact_private_structural_read_hash_parse_and_VR20A_call", order)
        self.assertTrue(order[-1].startswith("stop_before_archive_payload_neural"))

    def test_routes_resources_and_output_firewall_are_frozen(self):
        self.assertEqual(
            [row["route"] for row in self.decision["private_route_contract"]],
            [f"MARC2VR20P-R{i}" for i in range(1, 7)],
        )
        self.assertTrue(
            self.decision["private_route_contract"][0]["private_cohort_manifest_allowed"]
        )
        self.assertTrue(
            all(
                not row["private_cohort_manifest_allowed"]
                for row in self.decision["private_route_contract"][1:]
            )
        )
        generated = self.decision["generated_stage_requirements"]
        self.assertEqual(
            (generated["cases"], generated["orders"], generated["replays"]),
            (6, 2, 2),
        )
        self.assertEqual(generated["required_paths"], 24)
        self.assertGreaterEqual(generated["direct_refusal_minimum"], 90)
        caps = self.decision["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["private_source_content_opens"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["signal_bytes"], 0)
        self.assertEqual(caps["target_bytes"], 0)

    def test_decision_only_counters_are_zero(self):
        counters = self.decision["decision_only_counters"]
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
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
        self.assertIn("unambiguous transposition typo", text)
        self.assertIn("This decision does not become effective", text)
        self.assertIn("All 24 paths and at least 90", text)
        self.assertIn("R1 alone may freeze", text)
        self.assertIn("Engineering capability authorized after green decision", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
