import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT / "registries/eegmmidb_unseen_participant_generalization_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_AUTHORIZATION_PACKET.md"


class EEGMMIDBUnseenParticipantGeneralizationAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_fixed_artifacts_are_exact(self):
        for binding in self.request["fixed_artifacts"]:
            path = ROOT / binding["path"]
            self.assertEqual(path.stat().st_size, binding["bytes"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), binding["sha256"])

    def test_stages_are_conditional_and_strictly_ordered(self):
        stages = self.request["requested_stages"]
        self.assertEqual(stages["strict_order_required"], ["G", "M", "S", "F", "T"])
        self.assertTrue(stages["each_prior_stage_commit_push_and_both_CI_jobs_green"])
        self.assertTrue(stages["source_failure_stops_before_fresh_payload"])
        self.assertTrue(stages["prediction_freeze_green_before_target_delivery"])

    def test_existing_source_access_excludes_consumed_final_runs(self):
        source = self.request["future_source_stage"]
        self.assertEqual(source["existing_source_EDFs"], 54)
        self.assertEqual(source["existing_source_bytes"], 138_333_504)
        self.assertEqual(source["new_source_EDFs"], 6)
        self.assertEqual(source["forbidden_existing_runs"], ["11", "12"])
        self.assertEqual(sum(row["allowed_EDFs"] for row in source["existing_roots"]), 54)
        self.assertEqual(sum(row["allowed_bytes"] for row in source["existing_roots"]), 138_333_504)
        self.assertEqual(source["fresh_payload_requests_if_execution_gate_fails"], 0)

    def test_fresh_targets_are_firewalled_from_prediction(self):
        fresh = self.request["future_fresh_stage"]
        self.assertEqual(fresh["participants"], [f"S{i:03d}" for i in range(16, 31)])
        self.assertEqual(fresh["sealed_targets_maximum"], 450)
        self.assertEqual(fresh["participant_calibration_rows"], 0)
        self.assertEqual(fresh["test_normalization_fit_rows"], 0)
        self.assertEqual(fresh["test_threshold_or_selection_rows"], 0)
        self.assertEqual(fresh["test_time_adaptation_updates"], 0)
        self.assertFalse(
            fresh["individual_prediction_probability_target_or_participant_outcome_publication"]
        )

    def test_model_and_controls_cannot_expand(self):
        model = self.request["frozen_model"]
        self.assertEqual(model["candidate_count"], 1)
        self.assertEqual(model["hyperparameter_searches"], 0)
        self.assertEqual(model["larger_deep_or_pretrained_models"], 0)
        self.assertEqual(len(self.request["frozen_conditions"]), 12)
        self.assertIn("equal_prior_no_signal", self.request["frozen_conditions"])
        self.assertIn("timing_only", self.request["frozen_conditions"])

    def test_resource_caps_are_storage_and_cpu_cautious(self):
        caps = self.request["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertLessEqual(caps["payload_network_bytes_maximum"], 256 << 20)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 512 << 20)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)
        self.assertGreaterEqual(caps["free_disk_bytes_minimum_before_payload"], 2 << 30)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)

    def test_all_current_authority_and_operations_are_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )

    def test_short_form_cannot_be_retroactive(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["non_scope_changing_request_proof_closeout_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_approve_or_lets_go_is_retroactive"])
        self.assertFalse(protocol["packet_or_registration_alone_authorizes_any_stage"])

    def test_claim_ceiling_does_not_overstate_neural_origin(self):
        boundary = self.request["claim_boundary"]
        self.assertEqual(boundary["maximum_route"], "EEGMMIDBUG1-R4")
        self.assertFalse(boundary["neural_source_or_motor_cortex_origin"])
        self.assertFalse(boundary["movement_intention"])
        self.assertFalse(boundary["EEG_beyond_eye_visual_or_peripheral_signals"])
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("All-false Tier C request", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
