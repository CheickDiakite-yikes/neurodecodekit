import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
DOC_PATH = (
    ROOT / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PREREGISTRATION.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyCohortConfirmationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_registration_freezes_metadata_but_authorizes_no_tier_c_operation(self):
        self.assertEqual(
            self.contract["status"],
            "frozen_preregistration_exact_tier_c_authorization_pending",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["preregistration_frozen"])
        self.assertTrue(scope["exact_metadata_inventory_frozen"])
        self.assertTrue(scope["separate_exact_tier_c_decision_required"])
        allowed_true = {
            "preregistration_frozen",
            "exact_metadata_inventory_frozen",
            "separate_exact_tier_c_decision_required",
        }
        self.assertTrue(
            all(value is False for key, value in scope.items() if key not in allowed_true)
        )

        counters = self.contract["current_access_counters"]
        self.assertEqual(counters["retained_public_metadata_get_requests"], 13)
        self.assertEqual(counters["retained_public_metadata_body_bytes"], 340_703)
        self.assertFalse(
            counters["total_public_research_metadata_requests_or_bytes_exactly_measured"]
        )
        nonzero_metadata = {
            "retained_public_metadata_get_requests",
            "retained_public_metadata_body_bytes",
        }
        self.assertTrue(
            all(value in (0, False) for key, value in counters.items() if key not in nonzero_metadata)
        )

    def test_local_source_bindings_match_exact_files(self):
        for binding in self.contract["source_bindings"].values():
            path = ROOT / binding["path"]
            self.assertTrue(path.is_file(), binding["path"])
            self.assertEqual(binding["sha256"], sha256(path), binding["path"])

    def test_metadata_sources_are_exact_and_no_edf_url_was_requested(self):
        metadata = self.contract["metadata_registration"]
        documents = metadata["retained_documents"]
        self.assertEqual(len(documents), 13)
        self.assertEqual(sum(row["body_bytes"] for row in documents), 340_703)
        self.assertEqual(len({row["source_id"] for row in documents}), 13)
        self.assertEqual(len({row["url"] for row in documents}), 13)
        self.assertEqual(sum(row["source_id"].startswith("official_s3_listing_") for row in documents), 12)
        self.assertEqual(
            next(row for row in documents if row["source_id"] == "official_sha256_manifest")["body_sha256"],
            "7f5d16957d8ee7bce86cc7ccba0e5994f63f33781607eb3f838392d49311a208",
        )
        self.assertTrue(all(len(row["body_sha256"]) == 64 for row in documents))
        self.assertEqual(metadata["edf_url_head_requests"], 0)
        self.assertEqual(metadata["edf_url_get_requests"], 0)
        self.assertEqual(metadata["edf_payload_body_bytes"], 0)

    def test_inventory_expands_to_exact_unique_72_file_identity(self):
        files = self.contract["selected_files"]
        subjects = [f"S{index:03d}" for index in range(4, 16)]
        runs = ["03", "04", "07", "08", "11", "12"]
        expected_paths = [
            f"{subject}/{subject}R{run}.edf"
            for subject in subjects
            for run in runs
        ]
        self.assertEqual([row["path"] for row in files], expected_paths)
        self.assertEqual(len(files), 72)
        self.assertEqual(len({row["path"] for row in files}), 72)
        self.assertEqual(len({row["sha256"] for row in files}), 72)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in files))
        self.assertTrue(all(row["subject"] in subjects for row in files))
        self.assertFalse(any(row["path"].endswith(".event") for row in files))

        canonical = json.dumps(
            files,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            "41906e8c74cafdcaa99354baab8acd4927127a73e7454939429dbca2a8c03dad",
        )
        self.assertEqual(
            self.contract["dataset_binding"]["canonical_expanded_inventory_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_inventory_roles_tasks_and_bytes_are_exact(self):
        files = self.contract["selected_files"]
        self.assertEqual(sum(row["size_bytes"] for row in files), 184_252_032)
        self.assertEqual(sum(row["role"] == "fit" for row in files), 48)
        self.assertEqual(sum(row["role"] == "sealed_final" for row in files), 24)
        self.assertEqual(
            sum(row["size_bytes"] for row in files if row["role"] == "fit"),
            122_834_688,
        )
        self.assertEqual(
            sum(row["size_bytes"] for row in files if row["role"] == "sealed_final"),
            61_417_344,
        )
        self.assertEqual(sum(row["task"] == "execution" for row in files), 36)
        self.assertEqual(sum(row["task"] == "imagery" for row in files), 36)
        for row in files:
            expected_task = "execution" if row["run"] in {"03", "07", "11"} else "imagery"
            expected_role = "sealed_final" if row["run"] in {"11", "12"} else "fit"
            self.assertEqual(row["task"], expected_task)
            self.assertEqual(row["role"], expected_role)

    def test_cohort_and_target_firewall_are_strict(self):
        dataset = self.contract["dataset_binding"]
        self.assertEqual(dataset["participants"], [f"S{index:03d}" for index in range(4, 16)])
        self.assertEqual(dataset["overlap_with_consumed_participants"], [])
        self.assertEqual(dataset["execution_fit_runs"], ["03", "07"])
        self.assertEqual(dataset["execution_sealed_final_run"], "11")
        self.assertEqual(dataset["imagery_fit_runs"], ["04", "08"])
        self.assertEqual(dataset["imagery_sealed_final_run"], "12")
        self.assertFalse(dataset["substitution_allowed"])

        firewall = self.contract["target_firewall_and_split"]
        self.assertFalse(firewall["row_random_split"])
        self.assertFalse(firewall["cross_participant_fit"])
        self.assertEqual(firewall["expected_total_fit_rows"], 720)
        self.assertEqual(firewall["expected_total_final_rows"], 360)
        self.assertTrue(firewall["final_annotations_may_be_materialized_only_by_target_firewall"])
        self.assertFalse(firewall["physical_never_opened_target_claim"])
        self.assertFalse(firewall["final_targets_exposed_to_predictive_code"])
        self.assertTrue(firewall["both_final_target_sets_delivered_together"])
        self.assertEqual(firewall["final_target_deliveries"], 1)
        self.assertEqual(firewall["final_scoring_events"], 1)

    def test_reader_requires_exact_channels_geometry_sampling_and_events(self):
        reader = self.contract["reader_and_derivative_contract"]
        self.assertEqual(reader["reader"], "mne.io.read_raw_edf")
        self.assertEqual(reader["channel_count"], 64)
        self.assertEqual(len(reader["standardized_channel_names"]), 64)
        self.assertEqual(len(set(reader["standardized_channel_names"])), 64)
        self.assertEqual(reader["require_sampling_rate_hz"], 160)
        self.assertEqual(reader["allowed_annotations"], ["T0", "T1", "T2"])
        self.assertTrue(reader["retain_all_source_eeg_channels"])
        self.assertTrue(reader["require_available_geometry"])
        self.assertFalse(reader["resampling"])
        self.assertFalse(reader["bad_channel_deletion_or_interpolation"])
        self.assertFalse(reader["ica_or_artifact_component_removal"])
        self.assertFalse(reader["raw_window_persistence"])
        self.assertFalse(reader["target_blind_prediction_derivative_contains_targets"])

    def test_primary_model_is_exact_low_frequency_prespecified_comparator(self):
        preprocessing = self.contract["causal_preprocessing"]
        model = self.contract["primary_model_template"]
        self.assertEqual(preprocessing["passband_hz"], [0.5, 4.0])
        self.assertEqual(preprocessing["primary_window_seconds_from_cue"], [1.0, 3.0])
        self.assertEqual(preprocessing["whole_head_feature_dimension"], 320)
        self.assertEqual(preprocessing["right_context_seconds_relative_to_decision"], 0.0)
        self.assertIn("cue_causal_only", preprocessing["causal_claim"])
        self.assertEqual(model["family_id"], "fixed_low_frequency_shrinkage_lda")
        self.assertEqual(model["selection_candidate_count"], 1)
        self.assertEqual(model["hyperparameter_search_runs"], 0)
        self.assertEqual(model["solver"], "lsqr")
        self.assertEqual(model["shrinkage"], 0.1)
        self.assertFalse(model["deep_network"])
        self.assertFalse(model["language_or_foundation_model"])

    def test_channel_views_are_literal_and_proxy_claims_remain_bounded(self):
        channels = self.contract["channel_sets"]
        source_names = set(self.contract["reader_and_derivative_contract"]["standardized_channel_names"])
        named_sets = [
            "sensorimotor_left",
            "sensorimotor_right",
            "frontal_ocular_sensitive",
            "occipital_visual_sensitive",
            "frontal_asymmetry_left",
            "frontal_asymmetry_right",
        ]
        self.assertTrue(all(set(channels[key]).issubset(source_names) for key in named_sets))
        self.assertTrue(set(channels["sensorimotor_left"]).isdisjoint(channels["sensorimotor_right"]))
        self.assertEqual(len(channels["hemisphere_swap_pairs"]), 9)
        self.assertTrue(channels["proxy_models_are_not_measured_EOG_source_localization_or_confound_removal"])

    def test_exact_fit_inference_and_prediction_counts_are_closed(self):
        fits = self.contract["parameter_update_contract"]
        predictions = self.contract["prediction_contract"]
        self.assertEqual(len(fits["model_ids_per_participant"]), 12)
        self.assertEqual(fits["parameter_update_fits_per_participant"], 12)
        self.assertEqual(fits["exact_parameter_update_fits"], 144)
        self.assertTrue(fits["cross_task_predictions_reuse_native_models_without_update"])
        self.assertEqual(predictions["condition_family_count"], 18)
        self.assertEqual(len(predictions["conditions"]), 18)
        self.assertEqual(predictions["exact_participant_condition_prediction_sets"], 216)
        self.assertEqual(predictions["exact_target_blind_model_inference_runs"], 216)
        self.assertEqual(predictions["expected_individual_predictions"], 3_240)
        self.assertTrue(all(not row["final_targets_available_to_predictor"] for row in predictions["conditions"]))
        self.assertEqual(
            {row["condition_id"] for row in predictions["conditions"]},
            {
                "execution_native_primary",
                "imagery_native",
                "execution_to_imagery",
                "imagery_to_execution",
                "execution_central_sensorimotor",
                "execution_frontal_proxy",
                "execution_occipital_proxy",
                "execution_frontal_asymmetry",
                "execution_early_cue",
                "execution_pre_cue",
                "execution_timing_only",
                "execution_no_signal_prior",
                "imagery_no_signal_prior",
                "execution_all_zero_final_signal",
                "execution_train_label_derangement",
                "execution_one_trial_final_signal_displacement",
                "execution_channel_derangement",
                "execution_central_hemisphere_swap",
            },
        )

    def test_control_permutations_are_literal_nonidentity_and_target_free(self):
        controls = self.contract["control_contract"]
        label_permutation = controls["train_label_derangement_indices"]
        channel_permutation = controls["channel_derangement_indices"]
        self.assertEqual(sorted(label_permutation), list(range(15)))
        self.assertNotEqual(label_permutation, list(range(15)))
        self.assertEqual(sorted(channel_permutation), list(range(64)))
        self.assertNotEqual(channel_permutation, list(range(64)))
        self.assertEqual(controls["seed_provenance_label"], 5909)
        self.assertFalse(controls["future_event_timing_used"])
        self.assertFalse(controls["final_target_used_to_construct_control"])

    def test_gates_use_participants_and_keep_localization_conjunctive(self):
        gates = self.contract["frozen_gates"]
        h1 = gates["H1_execution_native_cohort_confirmation"]
        self.assertEqual(h1["final_event_count"], 180)
        self.assertEqual(h1["minimum_correct_count"], 117)
        self.assertEqual(h1["minimum_pooled_balanced_accuracy"], 0.65)
        self.assertEqual(h1["minimum_macro_participant_balanced_accuracy"], 0.625)
        self.assertEqual(h1["minimum_participants_strictly_above_0_5_balanced_accuracy"], 9)
        self.assertLessEqual(h1["maximum_exact_one_sided_participant_sign_flip_p"], 0.01)
        h2 = gates["H2_imagery_native_task_mode_robustness"]
        self.assertEqual(h2["minimum_pooled_balanced_accuracy"], 0.6)
        self.assertTrue(h2["cross_task_transfer_is_diagnostic_not_rescue"])
        h3 = gates["H3_motor_compatible_localization"]
        self.assertEqual(h3["minimum_central_minus_strongest_proxy_pooled_margin"], 0.05)
        self.assertEqual(h3["minimum_lateralization_participants_in_registered_direction"], 8)
        controls = gates["mandatory_control_ceilings"]
        self.assertEqual(controls["maximum_pooled_and_macro_balanced_accuracy"], 0.6)
        self.assertFalse(controls["proxy_pass_proves_brain_specific_origin"])

    def test_prediction_freeze_precedes_combined_target_delivery(self):
        freeze = self.contract["prediction_freeze"]
        self.assertTrue(freeze["aggregate_hash_only_ledger_required"])
        self.assertTrue(freeze["ledger_binds_all_216_participant_condition_payload_hashes"])
        self.assertFalse(freeze["private_prediction_payloads_committed"])
        self.assertFalse(freeze["individual_prediction_probability_target_or_participant_outcome_in_ledger"])
        self.assertTrue(freeze["run11_and_run12_predictions_freeze_together"])
        self.assertTrue(freeze["freeze_commit_must_be_pushed"])
        self.assertTrue(freeze["base_python_and_optional_neuro_jobs_must_be_green"])
        self.assertFalse(freeze["final_targets_may_be_delivered_to_scorer_before_remote_green_freeze"])
        self.assertEqual(freeze["final_target_deliveries"], 1)
        self.assertEqual(freeze["final_scoring_events"], 1)

    def test_resources_are_small_one_shot_and_storage_cognizant(self):
        acquisition = self.contract["resource_caps"]["acquisition"]
        self.assertEqual(acquisition["invocations"], 1)
        self.assertEqual(acquisition["cpu_threads"], 1)
        self.assertEqual(acquisition["workers"], 1)
        self.assertEqual(acquisition["edf_payload_requests"], 72)
        self.assertEqual(acquisition["edf_payload_bytes"], 184_252_032)
        self.assertLessEqual(acquisition["peak_incremental_disk_bytes"], 384 << 20)
        self.assertGreaterEqual(acquisition["minimum_free_disk_bytes_before"], 20 << 30)
        self.assertEqual(acquisition["retries"], 0)
        self.assertEqual(acquisition["reruns"], 0)

        analysis = self.contract["resource_caps"]["analysis_and_scoring"]
        self.assertEqual(analysis["cpu_threads"], 1)
        self.assertEqual(analysis["workers"], 1)
        self.assertLessEqual(analysis["peak_rss_bytes"], 1 << 30)
        self.assertLessEqual(analysis["private_generated_bytes"], 64 << 20)
        self.assertEqual(analysis["network_bytes"], 0)
        self.assertEqual(analysis["new_payload_bytes"], 0)
        self.assertEqual(analysis["post_target_updates"], 0)

    def test_access_order_router_and_claim_ceiling_are_explicit(self):
        order = self.contract["registered_access_order"]
        self.assertLess(
            order.index("commit_push_and_remote_green_exact_preregistration_contract_and_invariant_tests"),
            order.index("commit_push_and_remote_green_all_false_authorization_request"),
        )
        self.assertLess(
            order.index("commit_push_and_remote_green_aggregate_hash_only_prediction_freeze"),
            order.index("deliver_both_final_target_sets_together_once_score_once_apply_frozen_router_and_stop"),
        )
        router = self.contract["ordered_verdict_router"]
        self.assertEqual(
            [row["verdict"] for row in router],
            ["WO9R-R0", "WO9R-R1", "WO9R-R2", "WO9R-R3", "WO9R-R4"],
        )
        self.assertIn("not_brain_specific", router[-1]["maximum_claim"])
        boundary = self.contract["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established_now"])
        self.assertIn("Brain-specific origin", boundary["not_established_even_if_WO9R_R4"])
        self.assertGreaterEqual(len(self.contract["forbidden_operations"]), 15)

    def test_document_states_metadata_method_target_reality_and_claim_boundary(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("without requesting an EDF URL", document)
        self.assertIn("184,252,032", document)
        self.assertIn("claim that target bytes remain physically unopened", document)
        self.assertIn("exactly 144 total", document)
        self.assertIn("exactly 18 prediction-condition families", document)
        self.assertIn("WO9R-R4", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
