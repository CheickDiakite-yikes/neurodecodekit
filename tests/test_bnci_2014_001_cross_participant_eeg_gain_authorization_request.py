import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_authorization_request.v0.json"
RESEARCH = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_research.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_AUTHORIZATION_PACKET.md"


class BNCI2014001CrossParticipantEEGGainAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.research = json.loads(RESEARCH.read_text(encoding="utf-8"))

    def test_identity_and_green_research_predecessor_are_exact(self):
        self.assertEqual(self.request["lane_id"], "BNCI-C3C5-1")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_local_remote_proof_pending",
        )
        proof = self.request["green_research_predecessor"]
        self.assertEqual(proof["commit"], "f435296be49f51aa1573f483cb29b4dde888bea2")
        self.assertEqual(proof["CI_run_id"], 32_745_853_616)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["real_data_or_scientific_operation"])

    def test_fixed_artifacts_match_exact_bytes_and_hashes(self):
        total = 0
        for binding in self.request["fixed_artifacts"]:
            payload = (ROOT / binding["path"]).read_bytes()
            self.assertEqual(len(payload), binding["bytes"], binding["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                binding["sha256"],
                binding["path"],
            )
            total += len(payload)
        summary = self.request["fixed_artifact_summary"]
        self.assertEqual((len(self.request["fixed_artifacts"]), total), (summary["count"], summary["bytes"]))
        self.assertTrue(summary["all_paths_tracked_and_not_Git_ignored"])

    def test_stages_are_strict_and_one_shot(self):
        stages = self.request["requested_stages"]
        self.assertEqual(stages["strict_order_required"], ["G1", "A", "Q", "P", "T"])
        self.assertTrue(stages["each_prior_stage_commit_push_and_both_CI_jobs_green"])
        self.assertTrue(stages["prediction_freeze_green_before_target_delivery"])
        self.assertTrue(stages["scientific_execution_is_one_shot"])

    def test_acquisition_is_exact_opaque_and_bounded(self):
        acquisition = self.request["future_acquisition_stage"]
        members = self.research["selected_original_payload"]["members"]
        self.assertEqual(acquisition["file_count"], len(members))
        self.assertEqual(acquisition["accepted_payload_bytes_exact"], sum(row["bytes"] for row in members))
        self.assertEqual(acquisition["attempts_per_file_maximum"], 3)
        self.assertEqual(acquisition["payload_requests_maximum"], 54)
        self.assertTrue(acquisition["resume_only_invocation_created_partial_file"])
        self.assertFalse(acquisition["completed_file_second_request_allowed"])
        self.assertFalse(
            acquisition["MAT_header_key_structure_signal_event_trial_artifact_label_or_target_parse_allowed"]
        )

    def test_fold_scoped_target_firewall_is_explicit(self):
        qualification = self.request["future_qualification_stage"]
        self.assertEqual(qualification["expected_task_runs"], 108)
        self.assertEqual(qualification["expected_nominal_trials"], 5_184)
        self.assertTrue(qualification["target_free_signal_and_timing_capabilities"])
        self.assertTrue(qualification["fold_scoped_source_label_capabilities"])
        self.assertEqual(qualification["sealed_held_out_E_target_sets"], 9)
        self.assertFalse(
            qualification["held_out_target_identity_visible_to_corresponding_predictive_capability"]
        )
        self.assertFalse(qualification["target_or_artifact_derived_primary_exclusion"])

        model = self.request["future_model_stage"]
        self.assertEqual((model["outer_folds"], model["inner_source_participant_folds"]), (9, 8))
        self.assertEqual(model["held_out_T_session_use"], "forbidden")
        self.assertEqual(model["participant_calibration_rows"], 0)
        self.assertEqual(model["test_time_adaptation_updates"], 0)
        self.assertEqual(model["hyperparameter_searches"], 0)

    def test_controls_and_score_cannot_expand(self):
        conditions = set(self.request["frozen_conditions"])
        self.assertTrue(
            {
                "equal_prior_no_signal",
                "timing_and_trial_order_only",
                "recorded_EOG_P",
                "P_plus_E",
                "P_plus_D_E",
                "test_only_EEG_channel_rotation_by_seven",
                "early_cue_EEG",
            }.issubset(conditions)
        )
        score = self.request["future_target_and_score_stage"]
        self.assertEqual(score["aggregate_target_deliveries"], 1)
        self.assertEqual(score["scoring_events"], 1)
        self.assertEqual(score["post_target_updates"], 0)
        self.assertEqual(score["scientific_reruns"], 0)
        self.assertFalse(score["individual_protected_outputs_public"])

    def test_resource_caps_respect_computer_and_storage(self):
        caps = self.request["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["payload_bytes_exact"], 779_873_919)
        self.assertLessEqual(caps["payload_network_bytes_maximum"], 2_684_354_560)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 2 << 30)
        self.assertGreaterEqual(caps["free_disk_bytes_minimum_before_acquisition"], 5 << 30)
        self.assertLessEqual(caps["peak_RSS_bytes_maximum"], 1 << 30)
        self.assertEqual(caps["cleanup_scope"], "invocation_created_temporary_files_only")

    def test_every_current_authority_and_protected_operation_is_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.request["current_operation_counters"].values()))
        research = self.request["public_preregistration_research_operations"]
        self.assertGreater(research["public_source_code_GETs"], 0)
        self.assertEqual(research["neural_or_dataset_payload_GETs"], 0)
        self.assertEqual(research["retained_response_body_bytes"], 0)
        self.assertFalse(research["authority_granted"])

    def test_short_form_cannot_be_retroactive(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["non_scope_changing_request_proof_closeout_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_approve_or_similar_message_is_retroactive"])
        self.assertFalse(protocol["packet_registration_or_research_alone_authorizes_any_stage"])

    def test_claim_boundary_and_document_are_honest(self):
        boundary = self.request["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling_now"], "none")
        self.assertFalse(boundary["neural_payload_accessed"])
        self.assertFalse(boundary["decoding_performance_established"])
        self.assertFalse(boundary["thought_or_language_decoding"])
        self.assertFalse(boundary["exclusive_motor_cortex_origin"])
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("All-false Tier C request", text)
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("not retroactive", text)


if __name__ == "__main__":
    unittest.main()
