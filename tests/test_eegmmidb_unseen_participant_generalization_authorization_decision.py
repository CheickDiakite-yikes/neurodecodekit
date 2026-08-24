import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT / "registries/eegmmidb_unseen_participant_generalization_authorization_decision.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_AUTHORIZATION_DECISION.md"


class EEGMMIDBUnseenParticipantGeneralizationAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_exact_short_form_message_and_green_packet_are_bound(self):
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"],
            hashlib.sha256(b"continue").hexdigest(),
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "EEGMMIDB-UG1")
        self.assertFalse(user["message_silently_corrected"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])

        request = self.decision["green_request"]
        self.assertEqual(request["commit"], "c642d90b646ff32c6d83e648f7d7779810605e11")
        self.assertEqual(request["CI_run_id"], 32690289547)
        self.assertEqual(request["base_python_job_id"], 97322606634)
        self.assertEqual(request["optional_neuro_job_id"], 97322606501)
        self.assertTrue(request["both_required_jobs_green"])

        proof = self.decision["green_proof_closeout"]
        self.assertEqual(proof["commit"], "9117b1db343be38248944c24e3d93cafc4058d98")
        self.assertEqual(proof["CI_run_id"], 32690987778)
        self.assertEqual(proof["base_python_job_id"], 97324487895)
        self.assertEqual(proof["optional_neuro_job_id"], 97324488042)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_decision_has_delayed_effect_and_strict_order(self):
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )
        self.assertEqual(
            self.decision["required_order"][0], "decision_commit_push_and_both_CI_jobs_green"
        )
        self.assertEqual(
            self.decision["required_order"][-1], "stop_without_rerun_or_post_target_update"
        )
        auth = self.decision["authorization"]
        self.assertFalse(
            auth["G_generated_mocked_implementation_after_decision_green_without_amendment"]
        )
        self.assertTrue(
            auth["G_generated_mocked_implementation_after_decision_and_narrowing_amendment_green"]
        )
        self.assertTrue(auth["M_metadata_only_inventory_after_G_green"])
        self.assertTrue(auth["T_one_target_delivery_and_score_after_F_prediction_freeze_green"])
        self.assertFalse(auth["implementation_or_any_stage_authorized_at_decision_recording"])
        self.assertFalse(auth["network_or_payload_operation_authorized_before_G_green"])
        self.assertEqual(
            self.decision["required_order"][1],
            "pre_execution_narrowing_amendment_commit_push_and_both_CI_jobs_green",
        )

    def test_pre_execution_audit_fails_closed_before_stage_g(self):
        audit = self.decision["pre_execution_audit"]
        self.assertTrue(audit["completed_before_decision_commit"])
        self.assertFalse(audit["real_or_retained_data_accessed"])
        self.assertFalse(audit["result_or_target_observed"])
        self.assertFalse(audit["original_green_packet_modified"])
        self.assertTrue(audit["stage_G_blocked_pending_hash_changing_narrowing_amendment"])
        self.assertTrue(audit["amendment_may_only_narrow_or_clarify"])
        self.assertGreaterEqual(len(audit["required_clarifications"]), 8)

    def test_cohorts_model_and_controls_are_unchanged(self):
        cohorts = self.decision["cohorts"]
        self.assertEqual(cohorts["source_participants"], "S001-S015")
        self.assertEqual(cohorts["fresh_participants"], "S016-S030")
        self.assertEqual(cohorts["source_execution_runs"], [3, 7])
        self.assertEqual(cohorts["source_imagery_runs"], [4, 8])
        self.assertFalse(cohorts["source_run_11_or_12_allowed"])
        self.assertEqual(
            cohorts["fresh_calibration_normalization_threshold_selection_or_update_rows"], 0
        )
        self.assertEqual(cohorts["fresh_execution_rows_exact"], 225)
        self.assertEqual(cohorts["fresh_imagery_rows_exact"], 225)
        self.assertEqual(cohorts["sealed_target_rows_exact"], 450)
        self.assertFalse(
            cohorts[
                "participant_identity_available_to_predictor_feature_normalization_model_threshold_or_condition_transform"
            ]
        )
        model = self.decision["model"]
        self.assertEqual(model["feature_dimension"], 320)
        self.assertEqual(model["candidate_count"], 1)
        self.assertEqual(model["hyperparameter_searches"], 0)
        self.assertEqual(model["larger_deep_pretrained_or_foundation_models"], 0)
        self.assertEqual(len(self.decision["frozen_conditions"]), 12)

    def test_source_and_fresh_gates_remain_conjunctive(self):
        source = self.decision["source_gate"]
        self.assertEqual(source["folds"], 15)
        self.assertEqual(source["macro_balanced_accuracy_minimum"], 0.57)
        self.assertEqual(source["margin_over_max_no_signal_timing_minimum"], 0.07)
        self.assertEqual(source["failure_fresh_payload_requests"], 0)
        fresh = self.decision["fresh_execution_gate"]
        self.assertEqual(fresh["participants"], 15)
        self.assertEqual(fresh["events"], 225)
        self.assertEqual(fresh["pooled_and_macro_balanced_accuracy_minimum"], 0.60)
        self.assertEqual(fresh["margin_over_max_no_signal_timing_minimum"], 0.10)
        self.assertEqual(fresh["participants_above_chance_minimum"], 11)

    def test_resources_are_bounded_and_one_shot(self):
        caps = self.decision["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertLessEqual(caps["payload_network_bytes_maximum"], 256 << 20)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 512 << 20)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)
        self.assertEqual(caps["target_deliveries"], 1)
        self.assertEqual(caps["scoring_events"], 1)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertEqual(caps["post_target_updates"], 0)

    def test_recording_performed_no_operation_or_claim(self):
        self.assertTrue(
            all(value == 0 for value in self.decision["decision_only_counters"].values())
        )
        boundary = self.decision["claim_boundary"]
        self.assertEqual(boundary["maximum_route"], "EEGMMIDBUG1-R4")
        self.assertFalse(boundary["movement_intention_or_motor_cortex_origin"])
        self.assertFalse(boundary["EEG_beyond_eye_visual_or_peripheral_signals"])
        self.assertFalse(boundary["scientific_claim_established_by_decision"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Scientific claim not established", document)
        self.assertIn("generated/mock Stage G qualification", document)


if __name__ == "__main__":
    unittest.main()
