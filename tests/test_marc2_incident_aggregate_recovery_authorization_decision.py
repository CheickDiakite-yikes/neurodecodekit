import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries/marc2_incident_aggregate_recovery_authorization_decision.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_INCIDENT_AGGREGATE_RECOVERY_AUTHORIZATION_DECISION.md"


class Marc2IncidentAggregateRecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_identity_parent_and_delayed_effect_are_exact(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc2_incident_aggregate_recovery_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC2-VR14P")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "3274a728ccf25a2e7bb5a7c208d2e8d53f2db6fb",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_and_proof_are_exact(self):
        request = self.decision["green_request"]
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(request["commit"], "d920e8eeaf7a7e9c980232c5de59f0e390c374be")
        self.assertEqual(request["CI_run_id"], 32_443_248_466)
        self.assertEqual(request["base_python_job_id"], 96_657_974_654)
        self.assertEqual(request["optional_neuro_job_id"], 96_657_974_564)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(proof["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(proof["CI_run_id"], 32_443_804_353)
        self.assertEqual(proof["base_python_job_id"], 96_659_529_617)
        self.assertEqual(proof["optional_neuro_job_id"], 96_659_529_824)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_actual_message_is_preserved_without_continuous_scope_inference(self):
        user = self.decision["user_authorization"]
        expected = (
            "youre approve to keep going, continue, you have my continuous approval "
            "and pre-approved approval"
        )
        self.assertEqual(user["actual_message_verbatim"], expected)
        self.assertEqual(user["actual_message_UTF8_bytes"], 96)
        self.assertEqual(
            user["actual_message_SHA256"],
            hashlib.sha256(expected.encode()).hexdigest(),
        )
        self.assertTrue(user["one_registered_two_stage_sequence_only"])
        self.assertFalse(user["continuous_or_future_packet_authority_inferred"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])

    def test_request_artifacts_match_bound_bytes_hashes_and_blobs(self):
        rows = self.decision["immutable_request_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 13_334)
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

    def test_authority_is_delayed_and_aggregate_only(self):
        authority = self.decision["authorization"]
        self.assertTrue(authority["generated_wrapper_implementation_after_decision_green"])
        self.assertTrue(authority["one_aggregate_report_read_after_stage_1_green"])
        self.assertTrue(authority["one_aggregate_recovery_receipt"])
        self.assertFalse(authority["implementation_or_ignored_access_authorized_now"])
        self.assertFalse(authority["structural_source_or_private_manifest_access"])
        self.assertFalse(authority["archive_neural_target_model_or_score_access"])
        self.assertFalse(authority["FW2_or_CIL1_execution"])

    def test_order_paths_routes_and_caps_are_frozen(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[2], "exact_stage_1_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(order[3], "stage_1_proof_closeout_pushed_and_both_CI_jobs_green")
        self.assertTrue(order[-1].startswith("stop_before_structural_source_private_manifest"))
        self.assertEqual(
            self.decision["fixed_paths"]["aggregate_report"],
            ".codex_work/marc2_r4_private_discriminator/v0/report.aggregate.v0.json",
        )
        self.assertEqual(len(self.decision["route_contract"]), 8)
        caps = self.decision["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["aggregate_report_content_opens"], 1)
        self.assertEqual(caps["aggregate_report_bytes_maximum"], 65_536)
        self.assertEqual(caps["network_bytes"], 0)

    def test_decision_operations_and_current_forbidden_counters_are_zero(self):
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
        self.assertFalse(gate["aggregate_read_may_begin_before_stage_1_proof_green"])
        self.assertFalse(gate["FW2_or_CIL1_may_execute_from_this_decision"])
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_effect"])
        self.assertFalse(claims["decoding_accuracy"])

    def test_human_decision_states_delayed_effect_and_continuous_limit(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("actual 96 UTF-8 bytes", text)
        self.assertIn("do not expand authority to a future packet", text)
        self.assertIn("This decision does not become effective", text)
        self.assertIn("Engineering capability authorized after green decision", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
