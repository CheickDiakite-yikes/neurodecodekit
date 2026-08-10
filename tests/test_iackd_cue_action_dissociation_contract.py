import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/iackd_cue_action_dissociation_contract.v0.json"
DOC_PATH = ROOT / "docs/IACKD_CUE_ACTION_DISSOCIATION_PREREGISTRATION.md"
INVENTORY_PATH = ROOT / "registries/iackd_openneuro_metadata_inventory.v0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDCueActionDissociationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_registration_is_frozen_but_authorizes_no_operation(self):
        self.assertEqual(
            self.contract["status"],
            "frozen_preregistration_exact_packet_bound_tier_c_decision_pending",
        )
        scope = self.contract["scope"]
        allowed_true = {
            "preregistration_frozen",
            "exact_metadata_inventory_frozen",
            "separate_all_false_request_required",
            "separate_packet_bound_tier_c_decision_required",
        }
        self.assertTrue(all(scope[key] for key in allowed_true))
        self.assertTrue(
            all(value is False for key, value in scope.items() if key not in allowed_true)
        )

    def test_green_research_anchor_and_artifact_hashes_are_exact(self):
        anchor = self.contract["green_research_anchor"]
        self.assertEqual(anchor["commit"], "d6f955e59e210a045d54e1fdb013e4bc7a9235d7")
        self.assertEqual(anchor["push_ci_run_id"], 31_399_402_403)
        self.assertEqual(anchor["base_python_job_id"], 93_490_301_532)
        self.assertEqual(anchor["optional_neuro_job_id"], 93_490_301_603)
        self.assertTrue(anchor["both_required_jobs_green"])
        for binding in self.contract["research_bindings"].values():
            self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_inventory_is_hash_bound_and_below_10_GiB(self):
        binding = self.contract["research_bindings"]["metadata_inventory"]
        self.assertEqual(binding["sha256"], sha256(INVENTORY_PATH))
        dataset = self.contract["dataset_binding"]
        self.assertEqual(dataset["participant_count"], 15)
        self.assertEqual(dataset["participant_hand_unit_count"], 30)
        self.assertEqual(dataset["bids_run_count"], 128)
        self.assertEqual(dataset["selected_object_count"], 1340)
        self.assertEqual(dataset["exact_selected_payload_bytes"], 7_249_113_684)
        self.assertLessEqual(dataset["exact_selected_payload_bytes"], 10 << 30)
        self.assertEqual(dataset["published_derivative_objects_allowed"], 0)
        self.assertEqual(dataset["substitution_objects_allowed"], 0)

    def test_acquisition_is_one_shot_sequential_opaque_and_atomic(self):
        acquisition = self.contract["acquisition_contract"]
        self.assertEqual(acquisition["invocations"], 1)
        self.assertEqual(acquisition["object_requests"], 1340)
        self.assertEqual(acquisition["request_order"], "selected_objects_sorted_by_path")
        self.assertTrue(acquisition["sha256_computed_while_streaming"])
        self.assertFalse(acquisition["content_parsed_during_acquisition"])
        self.assertTrue(acquisition["final_root_must_be_absent"])
        self.assertTrue(acquisition["atomic_complete_bundle_promotion"])
        self.assertFalse(acquisition["partial_bundle_promotion"])
        self.assertEqual(acquisition["MNE_imports"], 0)
        self.assertEqual(acquisition["retries"], 0)
        self.assertEqual(acquisition["reruns"], 0)

    def test_split_is_grouped_by_participant_hand_and_reverses_mapping(self):
        split = self.contract["split_contract"]
        self.assertEqual(split["model_unit"], "participant_by_moving_hand")
        self.assertEqual(split["model_unit_count"], 30)
        self.assertEqual(split["six_run_participants"], ["sub-04", "sub-05"])
        self.assertEqual(split["six_run_sealed_final_run"], "06")
        self.assertEqual(len(split["four_run_participants"]), 13)
        self.assertEqual(split["four_run_sealed_final_run"], "04")
        self.assertEqual(split["fit_condition"], "red_congruent_only")
        self.assertEqual(split["sealed_final_condition"], "yellow_incongruent_only")
        self.assertTrue(split["same_predictions_scored_against_both_target_views"])
        self.assertFalse(split["row_random_split"])
        self.assertFalse(split["cross_participant_fit"])
        self.assertFalse(split["cross_hand_fit"])
        self.assertFalse(split["final_condition_model_selection"])

    def test_reader_keeps_EEG_EOG_and_uses_no_post_hoc_cleaning(self):
        reader = self.contract["reader_contract"]
        self.assertEqual(reader["reader"], "mne.io.read_raw_brainvision")
        self.assertEqual(reader["mne_version"], "1.12.1")
        self.assertEqual(reader["eeg_sampling_rate_hz"], 1024)
        self.assertEqual(reader["required_EEG_channel_count"], 32)
        self.assertEqual(reader["required_non_EEG_channels"], ["M1", "M2", "HEOG", "VEOG"])
        self.assertTrue(reader["all_32_EEG_channels_retained"])
        self.assertTrue(reader["EOG_channels_retained"])
        self.assertFalse(reader["raw_window_persistence"])
        for forbidden in (
            "ICA",
            "interpolation",
            "bad_channel_deletion",
            "amplitude_rejection",
            "zero_phase_filtering",
            "resampling",
        ):
            self.assertFalse(reader[forbidden])

    def test_motion_guard_hides_direction_and_uses_no_post_motion_samples(self):
        guard = self.contract["kinematic_guard"]
        self.assertFalse(guard["signed_displacement_visible_to_predictive_preprocessing"])
        self.assertEqual(guard["minimum_speed_threshold_mm_per_second"], 20.0)
        self.assertEqual(guard["persistence_native_samples"], 3)
        self.assertEqual(guard["motion_guard_ms"], 30)
        self.assertEqual(guard["analysis_window_seconds"], [-1.0, 0.0])
        self.assertTrue(guard["window_half_open"])
        self.assertFalse(guard["event_14_more_than_30_ms_after_onset_allowed"])
        self.assertIn("not_real_time", guard["operational_claim"])

    def test_target_firewall_hides_both_opposite_final_views(self):
        firewall = self.contract["target_firewall"]
        self.assertFalse(firewall["final_actual_direction_available_to_predictive_code"])
        self.assertFalse(firewall["final_visual_direction_available_to_predictive_code"])
        self.assertFalse(firewall["final_signed_kinematics_available_to_predictive_code"])
        self.assertEqual(firewall["sealed_target_views"], ["actual_hand_direction", "visual_target_direction"])
        self.assertEqual(firewall["sealed_target_relation_required"], "exact_opposites")
        self.assertEqual(firewall["sealed_target_delivery_count"], 1)
        self.assertEqual(firewall["scoring_event_count"], 1)
        self.assertTrue(firewall["both_target_views_delivered_together"])
        self.assertFalse(firewall["delivery_before_remote_green_freeze"])

        builder = self.contract["isolated_target_builder"]
        self.assertEqual(builder["actual_hand_direction_source"], "signed_Leap_x_displacement")
        self.assertEqual(builder["visual_target_direction_source"], "signed_ball_x_displacement")
        self.assertEqual(builder["minimum_absolute_hand_displacement_mm"], 5.0)
        self.assertEqual(builder["minimum_absolute_ball_displacement_pixels"], 5.0)
        self.assertEqual(builder["congruent_fit_relation"], "equal_direction_signs")
        self.assertEqual(builder["incongruent_final_relation"], "opposite_direction_signs")
        self.assertTrue(builder["ball_move_direct_field_must_agree"])
        self.assertFalse(builder["ball_move_direct_field_is_sole_target_source"])
        self.assertFalse(builder["signed_values_visible_to_predictive_code"])

    def test_model_and_EOG_projection_are_fixed_and_fit_only(self):
        model = self.contract["primary_model"]
        self.assertEqual(model["family_id"], "fixed_low_frequency_shrinkage_lda")
        self.assertEqual(model["passband_hz"], [0.5, 4.0])
        self.assertEqual(model["feature_dimension"], 160)
        self.assertEqual(model["shrinkage"], 0.1)
        self.assertEqual(model["selection_candidate_count"], 1)
        self.assertEqual(model["hyperparameter_search_runs"], 0)
        self.assertEqual(model["right_context_seconds"], 0.0)
        self.assertFalse(model["end_to_end_latency_measured"])
        projection = self.contract["EOG_projection"]
        self.assertEqual(projection["ridge_lambda"], 0.001)
        self.assertTrue(projection["fit_partition_only"])
        self.assertEqual(projection["final_EOG_updates"], 0)

    def test_fit_and_prediction_counts_are_exact(self):
        fits = self.contract["fit_inventory"]
        self.assertEqual(fits["fits_per_participant_hand_unit"], 10)
        self.assertEqual(fits["maximum_parameter_update_fits"], 300)
        self.assertEqual(len(fits["families"]), 10)
        predictions = self.contract["prediction_inventory"]
        self.assertEqual(predictions["prediction_sets_per_participant_hand_unit"], 14)
        self.assertEqual(predictions["required_prediction_sets"], 420)
        self.assertEqual(predictions["maximum_target_blind_inference_calls"], 420)
        self.assertEqual(len(predictions["conditions"]), 14)
        self.assertTrue(predictions["primary_prediction_stored_once"])
        self.assertFalse(predictions["scoring_target_views_create_additional_prediction_sets"])

    def test_primary_gate_uses_participants_and_same_prediction_reversal(self):
        stats = self.contract["statistical_contract"]
        self.assertTrue(stats["hands_combined_within_participant_before_inference"])
        self.assertEqual(stats["participant_count"], 15)
        self.assertEqual(stats["exact_sign_assignments"], 32768)
        self.assertFalse(stats["pooled_trial_binomial_substitution_allowed"])
        h1 = self.contract["gates"]["H1_action_over_cue_reversal"]
        self.assertEqual(h1["minimum_macro_participant_action_balanced_accuracy"], 0.6)
        self.assertEqual(h1["minimum_macro_action_minus_visual_margin"], 0.2)
        self.assertEqual(h1["maximum_macro_visual_balanced_accuracy"], 0.4)
        self.assertLessEqual(h1["maximum_exact_participant_sign_flip_p"], 0.01)

    def test_router_separates_cue_bound_and_action_aligned_outcomes(self):
        router = self.contract["ordered_router"]
        self.assertEqual(
            [row["verdict"] for row in router],
            ["IACKD-R1", "IACKD-R0", "IACKD-R2", "IACKD-R3", "IACKD-R4"],
        )
        self.assertIn("cue_bound", router[0]["maximum_claim"])
        self.assertIn("source_unresolved", router[2]["maximum_claim"])
        self.assertIn("not_brain_specific", router[-1]["maximum_claim"])

    def test_resources_protect_CPU_memory_and_storage(self):
        acquisition = self.contract["resource_caps"]["acquisition"]
        self.assertEqual(acquisition["cpu_threads"], 1)
        self.assertEqual(acquisition["workers"], 1)
        self.assertEqual(acquisition["payload_requests"], 1340)
        self.assertEqual(acquisition["payload_bytes"], 7_249_113_684)
        self.assertLessEqual(acquisition["peak_incremental_disk_bytes"], 9 << 30)
        self.assertGreaterEqual(acquisition["minimum_free_disk_bytes"], 20 << 30)
        self.assertEqual(acquisition["retries"], 0)
        analysis = self.contract["resource_caps"]["analysis_and_scoring"]
        self.assertEqual(analysis["cpu_threads"], 1)
        self.assertLessEqual(analysis["peak_rss_bytes"], 2 << 30)
        self.assertLessEqual(analysis["private_generated_output_bytes"], 512 << 20)
        self.assertEqual(analysis["required_prediction_sets"], 420)
        self.assertEqual(analysis["final_target_deliveries"], 1)
        self.assertEqual(analysis["final_scoring_events"], 1)
        self.assertEqual(analysis["network_bytes"], 0)
        self.assertEqual(analysis["reruns"], 0)
        self.assertEqual(analysis["post_target_updates"], 0)

    def test_current_counters_preserve_metadata_only_history(self):
        counters = self.contract["current_access_counters"]
        allowed_nonzero = {
            "inherited_retained_S3_listing_bodies",
            "inherited_retained_openneuro_root_metadata_bodies",
            "inherited_retained_primary_article_bodies",
        }
        self.assertTrue(all(counters[key] > 0 for key in allowed_nonzero))
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)
        )

    def test_document_and_claim_boundary_are_explicit(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("same predictions", document)
        self.assertIn("7,249,113,684", document)
        self.assertIn("exactly 420", document)
        self.assertIn("IACKD-R1", document)
        self.assertIn("IACKD-R4", document)
        self.assertIn("Scientific claim not established", document)
        boundary = self.contract["claim_boundary"]
        self.assertIn("No IACKD payload", boundary["scientific_claim_not_established"])
        self.assertIn("without proof of brain-specific origin", boundary["maximum_future_IACKD_R4"])


if __name__ == "__main__":
    unittest.main()
