import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_contract.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_PREREGISTRATION.md"


class BNCI2014001CrossParticipantEEGGainContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_source_and_loader_semantics_are_exact(self):
        dataset = self.contract["dataset"]
        self.assertEqual(dataset["participants"], 9)
        self.assertEqual(dataset["nominal_trials_total"], 5_184)
        self.assertEqual(dataset["sampling_rate_hz"], 250)
        self.assertEqual((dataset["EEG_channels"], dataset["EOG_channels"]), (22, 3))

        payload = self.contract["payload"]
        self.assertEqual((payload["file_count"], payload["bytes"]), (18, 779_873_919))
        self.assertFalse(payload["BDF_conversion_allowed"])
        loader = self.contract["loader_semantics"]
        self.assertTrue(loader["source_trial_indices_are_one_based"])
        self.assertFalse(loader["MOABB_is_required_base_dependency"])

    def test_channel_order_and_views_are_frozen(self):
        channels = self.contract["channels"]
        self.assertEqual(len(channels["all_order"]), 25)
        self.assertEqual(len(channels["EEG_order"]), 22)
        self.assertEqual(channels["EOG_order"], ["EOG1", "EOG2", "EOG3"])
        self.assertEqual(channels["all_order"][:22], channels["EEG_order"])
        self.assertEqual(channels["all_order"][22:], channels["EOG_order"])
        self.assertEqual(len(channels["central_view"]), 17)
        self.assertEqual(len(channels["frontal_view"]), 6)
        self.assertEqual(len(channels["posterior_view"]), 9)

    def test_timing_is_causal_and_completed_trial_only(self):
        timing = self.contract["timing"]
        self.assertEqual(timing["primary_late_EEG_seconds"], [3.5, 6.0])
        self.assertEqual(timing["primary_late_EEG_samples"], [875, 1500])
        self.assertEqual(timing["EOG_comparator_samples"], [500, 1500])
        self.assertTrue(timing["window_stop_exclusive"])
        self.assertTrue(timing["one_decision_per_completed_trial"])

        causal = self.contract["causal_preprocessing"]
        self.assertEqual(causal["filter_direction"], "forward_causal_only")
        self.assertEqual(causal["state_reset_boundary"], "run_only")
        self.assertFalse(causal["trial_boundary_reset"])
        self.assertFalse(causal["forward_backward_or_centered_filter"])
        self.assertFalse(causal["future_sample_access"])

    def test_outer_protocol_is_strictly_unseen_person(self):
        protocol = self.contract["outer_protocol"]
        self.assertEqual(protocol["folds"], 9)
        self.assertEqual(protocol["participants"], [f"A{i:02d}" for i in range(1, 10)])
        self.assertEqual(protocol["source_participants_per_fold"], 8)
        self.assertEqual(protocol["held_out_evaluation_session"], "E")
        self.assertEqual(protocol["held_out_T_session_use"], "forbidden")
        self.assertTrue(protocol["fold_process_isolation_required"])
        self.assertTrue(protocol["fold_scoped_target_capability_manifest_required"])
        forbidden_fit_keys = (
            "held_out_person_signal_for_fit",
            "held_out_person_target_for_fit",
            "held_out_person_calibration",
            "held_out_person_normalization_fit",
            "held_out_person_alignment_fit",
            "held_out_person_rejection_threshold_fit",
            "held_out_person_abstention_threshold_fit",
            "test_time_adaptation",
        )
        self.assertTrue(all(protocol[key] is False for key in forbidden_fit_keys))

    def test_models_and_selection_are_small_and_fixed(self):
        candidates = self.contract["EEG_candidates"]
        self.assertEqual([(row["id"], row["feature_dimension"]) for row in candidates], [("E1", 88), ("E2", 1_012)])
        selection = self.contract["EEG_selection"]
        self.assertEqual(selection["inner_folds"], 8)
        self.assertEqual(selection["tie_winner"], "E1")
        self.assertEqual(selection["hyperparameter_searches"], 0)
        self.assertFalse(selection["global_post_score_winner_selection"])

        eog = self.contract["EOG_model_P"]
        self.assertEqual(eog["feature_dimension"], 102)
        self.assertEqual(eog["candidate_count"], 1)
        fusion = self.contract["fusion"]
        self.assertEqual(fusion["feature_dimension"], 6)
        self.assertTrue(fusion["P_plus_D_E_is_separately_fitted_size_matched_fusion"])
        self.assertFalse(fusion["held_out_person_data_for_fusion_fit"])

    def test_controls_and_gates_test_both_questions(self):
        conditions = self.contract["conditions"]
        self.assertEqual(conditions["equal_prior_no_signal"], 0.25)
        self.assertEqual(conditions["test_only_channel_rotation_positions"], 7)
        self.assertEqual(conditions["nonwrapping_within_run_EEG_trial_displacement"], 1)
        self.assertEqual(conditions["source_label_rotation_within_run"], 1)

        c3 = self.contract["C3_gate"]
        self.assertEqual(c3["primary_model"], "selected_E")
        self.assertEqual(c3["macro_balanced_accuracy_minimum"], 0.35)
        self.assertEqual(c3["positive_participant_margins_over_max_equal_prior_timing_minimum"], 8)
        self.assertFalse(c3["pooled_trial_p_value_allowed"])

        c5 = self.contract["C5_partial_gate"]
        self.assertEqual(c5["P_minus_P_plus_E_nats_per_trial_minimum"], 0.03)
        self.assertEqual(c5["P_plus_D_E_minus_P_plus_E_nats_per_trial_minimum"], 0.03)
        self.assertEqual(c5["positive_participant_deltas_each_comparison_minimum"], 8)
        self.assertFalse(c5["pooled_trial_p_value_allowed"])

    def test_resource_and_claim_boundaries_are_honest(self):
        caps = self.contract["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["payload_bytes"], 779_873_919)
        self.assertLessEqual(caps["incremental_disk_bytes_maximum"], 2 << 30)
        self.assertGreaterEqual(caps["free_disk_bytes_minimum_before_acquisition"], 5 << 30)
        self.assertEqual(caps["scientific_reruns"], 0)
        self.assertEqual(caps["post_target_updates"], 0)
        self.assertTrue(all(value is False for value in self.contract["authority_now"].values()))

        claims = self.contract["claim_boundary"]
        self.assertFalse(claims["thought_or_language_decoding"])
        self.assertFalse(claims["exclusive_motor_cortex_origin"])
        self.assertFalse(claims["beyond_all_peripheral_or_unrecorded_artifacts"])
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("## Participant Firewall", text)
        self.assertIn("## Recorded-EOG Comparator And Conditional Fusion", text)
        self.assertIn("This preregistration authorizes nothing", text)


if __name__ == "__main__":
    unittest.main()
