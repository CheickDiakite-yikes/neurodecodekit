import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_authorization_decision.v0.json"
REQUEST = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_authorization_request.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_STAGE_G1_RECOVERY_AUTHORIZATION_DECISION.md"


class BNCIStageG1RecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_proof_and_delayed_effect_are_exact(self):
        green = self.decision["green_recovery_proof"]
        self.assertEqual(
            green["commit"],
            "e1ad1eae373e0175eb05b2bb42f2f4a567a0fd49",
        )
        self.assertEqual(green["CI_run_id"], 32_761_632_135)
        self.assertEqual(green["base_python_job_id"], 97_541_580_862)
        self.assertEqual(green["optional_neuro_job_id"], 97_541_580_606)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_actual_maintainer_message_is_preserved_without_recital(self):
        user = self.decision["user_authorization"]
        actual = "continue"
        self.assertEqual(user["actual_message_verbatim"], actual)
        self.assertEqual(user["actual_message_utf8_bytes"], len(actual.encode()))
        self.assertEqual(
            user["actual_message_sha256"],
            hashlib.sha256(actual.encode()).hexdigest(),
        )
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertEqual(document.count("> continue"), 1)
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertEqual(
            user["sole_active_Tier_C_packet"],
            "BNCI-C3C5-1-G1-recovery",
        )

    def test_bound_artifacts_match_size_hash_blob_and_canonical_set(self):
        rows = self.decision["bound_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.decision["bound_artifact_summary"]
        self.assertEqual(summary["count"], 6)
        self.assertEqual(summary["bytes"], sum(row["bytes"] for row in rows))
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_request_remains_all_false_and_immutable(self):
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertTrue(
            all(value is False for value in self.request["recovery_authority_now"].values())
        )

    def test_only_one_generated_recovery_is_conditionally_authorized(self):
        authorization = self.decision["authorization_after_decision_green"]
        allowed_true = {
            "replacement_generated_qualification",
            "generated_MAT_fixture_write_and_parse",
            "mock_transport",
            "synthetic_feature_and_target_creation",
            "synthetic_parameter_update_and_inference",
            "synthetic_prediction_freeze",
            "synthetic_target_delivery_and_score",
            "aggregate_result_publication",
            "invocation_created_generated_cleanup",
            "existing_exact_optional_environment_reuse",
        }
        self.assertEqual(
            {key for key, value in authorization.items() if value},
            allowed_true,
        )
        recovery = self.decision["registered_recovery"]
        self.assertEqual(recovery["replacement_generated_qualification_invocations"], 1)
        self.assertEqual(recovery["synthetic_parameter_update_fits_exact"], 468)
        self.assertEqual(recovery["synthetic_prediction_sets_exact"], 495)
        self.assertFalse(recovery["retry_after_replacement"])
        self.assertTrue(recovery["stop_before_Stage_A"])

    def test_resources_and_execution_order_copy_the_request(self):
        self.assertEqual(self.decision["resource_caps"], self.request["resource_caps"])
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "test_commit_push_and_obtain_green_CI_for_this_decision")
        self.assertEqual(order[-1], "stop_before_Stage_A")
        gate = self.decision["next_gate"]
        self.assertFalse(gate["replacement_qualification_may_begin_before_green"])
        self.assertFalse(gate["real_or_Stage_A_operation_may_begin_after_green_decision"])
        self.assertFalse(gate["retry_or_rerun_available"])

    def test_decision_record_performed_no_recovery_or_real_operation(self):
        measurements = self.decision["authorization_only_measurements"]
        self.assertEqual(measurements["GitHub_CI_verification_calls"], 1)
        for key, value in measurements.items():
            if key == "GitHub_CI_verification_calls":
                continue
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_claim_boundary_remains_engineering_only(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability authorized for testing", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("this decision is not neural data", document)
        self.assertIn("does not authorize Stage A", document)


if __name__ == "__main__":
    unittest.main()
