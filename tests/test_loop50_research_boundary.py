import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop50_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_50_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
)


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop50ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_boundary_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop50_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertEqual(
            boundary["proof_posture"],
            "primary_source_design_only_no_protected_payload_or_model_execution",
        )
        flags = authorization_flags(boundary)
        self.assertGreaterEqual(len(flags), 31)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])
        self.assertFalse(boundary["authorization"]["general_continuation_is_authorization"])

    def test_dependencies_keep_stage_b_s24_s25_and_closed_s21_partitions_closed(self):
        dependencies = self.boundary["dependencies"]
        self.assertFalse(dependencies["loop48_stage_b_result_available"])
        self.assertTrue(
            dependencies["decision_0083_requires_stage_b_close_or_park_before_s24_acquisition"]
        )
        self.assertFalse(dependencies["loop49_s24_payload_opened"])
        self.assertFalse(dependencies["loop49_s24_minimum_row_gate_proven"])
        self.assertFalse(dependencies["loop50_experiment_started"])
        self.assertEqual(dependencies["s25_status"], "final_only_unopened")
        self.assertFalse(dependencies["s25_may_be_used_by_loop50"])
        self.assertFalse(
            dependencies["source_validation_source_test_session2_may_be_used_by_loop50"]
        )

    def test_primary_sources_cover_joint_training_leakage_robustness_and_uncertainty(self):
        sources = {row["source_id"]: row for row in self.boundary["primary_source_bindings"]}
        self.assertEqual(
            set(sources),
            {
                "brain2qwerty-v2-2026",
                "spanishbcbl-official-card",
                "brookshire-2024-eeg-leakage",
                "sagawa-2020-group-dro",
                "varoquaux-2018-small-sample-cv",
                "varma-simon-2006-selection-bias",
            },
        )
        self.assertTrue(sources["brain2qwerty-v2-2026"]["url"].endswith(".pdf"))
        self.assertIn("participant-specific leakage", sources["brookshire-2024-eeg-leakage"]["use"])
        self.assertIn("worst-group", sources["sagawa-2020-group-dro"]["use"])
        self.assertIn("small-neuroimaging-sample", sources["varoquaux-2018-small-sample-cv"]["use"])

    def test_evidence_roles_preserve_development_and_final_people(self):
        roles = self.boundary["evidence_roles"]
        self.assertFalse(roles["s21_session1_source_train"]["fresh_or_independent"])
        self.assertEqual(
            roles["s24_session2_block2"]["current_state"],
            "metadata_only_unopened_unqualified",
        )
        self.assertEqual(roles["s24_session2_block2"]["future_selection_groups"], 16)
        self.assertEqual(roles["s24_session2_block2"]["future_minimum_fit_groups"], 32)
        self.assertFalse(roles["s24_session2_block2"]["may_become_final_or_independent_evidence"])
        self.assertEqual(
            roles["s25_session2_block2"]["loop50_fit_selection_normalization_or_scoring_rows"],
            0,
        )
        self.assertFalse(roles["s25_session2_block2"]["may_influence_loop50_model_or_protocol"])

    def test_stage_b_router_has_no_automatic_acquisition_or_backup(self):
        router = self.boundary["stage_b_outcome_router"]
        self.assertFalse(router["automatic_s24_acquisition_after_any_result"])
        routes = {row["route_id"]: row for row in router["routes"]}
        self.assertEqual(set(routes), {f"L50-R0{index}" for index in range(1, 7)})
        self.assertIn("repair", routes["L50-R01"]["action"])
        self.assertIn("timing", routes["L50-R02"]["action"])
        self.assertIn("prepare", routes["L50-R03"]["action"])
        self.assertIn("data_regime", routes["L50-R04"]["action"])
        self.assertIn("park", routes["L50-R05"]["action"])
        self.assertIn("without_automatic_backup", routes["L50-R06"]["action"])
        self.assertFalse(router["route_application_is_acquisition_authorization"])

    def test_global_text_firewall_prevents_cross_person_target_leakage(self):
        firewall = self.boundary["future_global_text_firewall"]
        self.assertEqual(firewall["digest"], "SHA-256")
        self.assertIn("across_all_people", firewall["assignment_unit"])
        self.assertTrue(firewall["same_text_must_never_cross_fit_and_evaluation_roles"])
        self.assertEqual(firewall["s24_selection_groups"], 16)
        self.assertEqual(firewall["s24_minimum_fit_groups"], 32)
        self.assertEqual(firewall["s24_minimum_total_usable_groups"], 48)
        self.assertTrue(
            firewall[
                "s21_rows_matching_s24_selection_text_excluded_from_every_loop50_fit_normalizer_prior_and_diagnostic"
            ]
        )
        self.assertTrue(
            firewall["s24_rows_matching_current_s21_oof_fold_excluded_from_that_fold_training"]
        )
        self.assertTrue(firewall["sentence_plaintext_may_not_be_emitted"])
        self.assertTrue(firewall["raw_canonical_sentence_hashes_may_not_be_persisted"])

    def test_s21_diagnostic_is_out_of_fold_but_never_relabelled_fresh(self):
        oof = self.boundary["future_s21_oof_diagnostic"]
        self.assertEqual(oof["fold_count"], 5)
        self.assertTrue(oof["same_text_group_stays_in_one_fold"])
        self.assertTrue(oof["fold_train_scaler_must_exclude_held_out_fold"])
        self.assertTrue(oof["fold_train_candidate_must_exclude_held_out_fold"])
        self.assertFalse(oof["direct_in_sample_scoring_allowed"])
        self.assertFalse(oof["historical_freshness_restored_by_oof"])
        self.assertEqual(oof["allowed_label"], "historical_development_oof")

    def test_compatibility_and_normalization_preserve_future_strict_zero_shot(self):
        compatibility = self.boundary["future_compatibility_gate"]
        self.assertEqual(compatibility["required_input_channels"], 102)
        self.assertTrue(compatibility["exact_same_ordered_channel_names_required"])
        self.assertFalse(
            compatibility["silent_channel_interpolation_substitution_or_reordering_allowed"]
        )
        self.assertFalse(compatibility["nominal_same_megin_system_is_sufficient"])
        self.assertFalse(compatibility["compatibility_proven_now"])

        normalization = self.boundary["future_normalization_policy"]
        self.assertEqual(normalization["fit_scope"], "current_fit_rows_only")
        self.assertFalse(normalization["participant_specific_scalers_allowed"])
        self.assertFalse(normalization["s24_selection_signal_statistics_allowed"])
        self.assertFalse(normalization["s25_target_corpus_signal_statistics_allowed"])

    def test_single_shared_candidate_has_no_participant_or_language_shortcut(self):
        policy = self.boundary["future_candidate_policy"]
        self.assertFalse(policy["exact_candidate_selected_now"])
        self.assertEqual(policy["candidate_configurations_allowed_after_preregistration"], 1)
        self.assertEqual(policy["trainable_parameter_ceiling"], 10000)
        self.assertEqual(policy["right_context_samples"], 0)
        self.assertFalse(policy["whole_sentence_or_bidirectional_layer_allowed"])
        self.assertEqual(policy["primary_shared_checkpoint_count"], 1)
        self.assertEqual(policy["nonselectable_shared_stability_checkpoint_count"], 2)
        self.assertEqual(policy["final_candidate_checkpoint_count"], 1)
        self.assertEqual(policy["participant_specific_checkpoint_count"], 0)
        self.assertFalse(policy["participant_id_as_model_input"])
        self.assertFalse(policy["participant_embedding"])
        self.assertFalse(policy["participant_conditioned_affine"])
        self.assertFalse(policy["participant_specific_adapter_checkpoint_or_finetuning"])
        self.assertFalse(policy["language_model_or_ngram"])
        self.assertFalse(policy["target_text_derived_model_input"])
        self.assertEqual(policy["primary_seed"], 5001)
        self.assertEqual(policy["stability_seeds"], [5002, 5003])
        self.assertFalse(policy["best_seed_selection"])
        self.assertEqual(policy["restarts"], 0)

    def test_training_objective_balances_people_without_group_dro(self):
        objective = self.boundary["future_training_objective"]
        self.assertEqual(objective["applies_to"], "primary_multi_source_candidate")
        self.assertEqual(objective["participant_weights"], {"S21": 0.5, "S24": 0.5})
        self.assertTrue(objective["every_optimizer_update_requires_both_people"])
        self.assertTrue(
            objective["replacement_or_cycling_rule_must_be_deterministic_and_preregistered"]
        )
        self.assertTrue(
            objective["participant_id_use_allowed_only_for_sampler_metric_and_access_ledgers"]
        )
        self.assertFalse(objective["learned_group_dro_selected"])

        inventory = self.boundary["future_parameter_update_inventory_recommendation"]
        self.assertEqual(inventory["pooled_candidate_primary_seed_s21_oof_fits"], 5)
        self.assertEqual(inventory["pooled_candidate_final_fit_seeds_5001_5002_5003"], 3)
        self.assertEqual(inventory["shared_linear_primary_seed_s21_oof_plus_final_fits"], 6)
        self.assertEqual(inventory["s21_only_causal_primary_seed_s21_oof_plus_final_fits"], 6)
        self.assertEqual(inventory["total_parameter_update_runs"], 20)
        self.assertEqual(inventory["absolute_parameter_update_run_cap"], 24)
        self.assertTrue(inventory["exact_zero_channel_and_time_controls_reuse_frozen_checkpoints"])
        self.assertTrue(
            inventory["timing_length_only_control_must_be_deterministic_or_closed_form"]
        )
        self.assertFalse(inventory["unused_cap_margin_is_rerun_permission"])

    def test_condition_inventory_is_exact_and_contains_identity_controls(self):
        inventory = self.boundary["future_condition_inventory"]
        self.assertEqual(len(inventory), 10)
        self.assertEqual(
            [row["condition_id"] for row in inventory],
            [f"L50-C{index:02d}" for index in range(10)],
        )
        by_id = {row["condition_id"]: row for row in inventory}
        self.assertEqual(by_id["L50-C02"]["role"], "participant_id_only_shortcut")
        self.assertEqual(by_id["L50-C04"]["role"], "signal_use_control")
        self.assertEqual(by_id["L50-C08"]["role"], "architecture_complexity_control")
        self.assertEqual(by_id["L50-C09"]["role"], "descriptive_added_s24_fit_value")

    def test_prediction_firewall_consumes_selection_once_without_restoring_s21(self):
        firewall = self.boundary["future_prediction_firewall"]
        self.assertFalse(firewall["s24_selection_targets_available_to_fit_or_prediction_process"])
        self.assertTrue(
            firewall[
                "all_candidate_and_control_predictions_hash_frozen_before_s24_selection_targets"
            ]
        )
        self.assertTrue(
            firewall["prediction_freeze_record_must_be_tested_committed_pushed_and_remotely_green"]
        )
        self.assertTrue(firewall["s24_selection_target_delivery_exactly_once"])
        self.assertTrue(firewall["s24_selection_scoring_exactly_once"])
        self.assertEqual(firewall["post_selection_parameter_or_configuration_updates"], 0)
        self.assertEqual(firewall["reruns_after_selection_scoring"], 0)
        self.assertFalse(firewall["prediction_freeze_restores_s21_historical_freshness"])

    def test_acceptance_requires_both_people_and_never_uses_pooled_rescue(self):
        metrics = self.boundary["future_metrics"]
        self.assertTrue(metrics["worst_person_primary_over_pooled"])
        self.assertFalse(metrics["pooled_metric_may_rescue_failed_person"])

        gate = self.boundary["future_acceptance_recommendation"]
        self.assertEqual(gate["primary_seed"], 5001)
        self.assertEqual(gate["strongest_no_signal_macro_CER_margin_min_each_person"], 0.05)
        self.assertTrue(gate["strictly_beat_exact_zero_channel_time_timing_and_linear_each_person"])
        self.assertTrue(gate["strictly_improve_s24_over_s21_only_neural_comparator"])
        self.assertEqual(
            gate["maximum_allowed_s21_oof_macro_CER_degradation_vs_s21_only_neural"],
            0.02,
        )
        self.assertTrue(
            gate["stability_seeds_must_preserve_s24_primary_no_signal_margin_direction"]
        )
        self.assertFalse(gate["stability_seed_may_replace_primary"])
        self.assertTrue(gate["both_people_must_pass"])
        self.assertTrue(gate["worst_person_must_pass"])
        self.assertFalse(gate["pooled_only_pass_allowed"])
        self.assertFalse(gate["s24_selection_p_value_is_confirmatory"])
        self.assertIn("no_rerun", gate["failure_action"])

    def test_resources_access_counters_and_refusals_are_bounded(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_trainable_parameter_ceiling"], 10000)
        self.assertEqual(resources["future_parameter_update_run_ceiling"], 24)
        self.assertEqual(resources["future_parameter_update_runtime_cap_sec"], 3600)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 2 * 1024**3)
        self.assertEqual(resources["future_generated_output_cap_bytes"], 64 * 1024**2)
        self.assertEqual(resources["future_minimum_free_disk_bytes"], 20 * 1024**3)
        self.assertEqual(resources["current_new_download_bytes"], 0)
        self.assertEqual(resources["current_protected_payload_read_bytes"], 0)
        self.assertFalse(resources["tracked_workbook_reopened_this_pass"])
        self.assertFalse(resources["user_owned_inspection_sidecar_touched"])

        counters = self.boundary["planning_access_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()), counters)
        self.assertEqual(len(self.boundary["refusal_ids"]), 30)
        self.assertEqual(len(set(self.boundary["refusal_ids"])), 30)

    def test_claim_boundary_stays_below_science_and_realtime(self):
        claim = self.boundary["claim_boundary"]
        self.assertIn(
            "development evidence",
            claim["maximum_future_claim_if_every_separate_loop50_gate_passes"],
        )
        unavailable = " ".join(claim["not_established"])
        for term in (
            "neural advantage",
            "brain-specific",
            "independent validation",
            "unseen-person",
            "real-time",
            "EEG",
            "home-device",
            "clinical",
        ):
            self.assertIn(term, unavailable)
        self.assertTrue(claim["s25_is_required_for_future_strict_zero_shot_verdict"])
        self.assertTrue(claim["loop35_is_required_for_brain_specific_origin"])

    def test_roadmap_and_public_status_keep_loop50_not_started(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 50)
        self.assertEqual(row["status"], "Not Started")
        self.assertFalse(row["execution_authorized"])
        self.assertIn("five-fold", row["build_deliverable"])
        self.assertIn("20-parameter-update", row["build_deliverable"])
        self.assertIn("20 planned", row["future_resource_cap"])
        self.assertIn("both development people", row["acceptance_gate"])
        self.assertIn("S25 remains unopened", row["data_scope"])

        for path, content in self.public_status.items():
            with self.subTest(path=path):
                self.assertIn("LOOP_50_PRIMARY_SOURCE_RESEARCH.md", content)
                self.assertIn("loop50_research_boundary.v0.json", content)
                self.assertIn("Not Started", content)

    def test_research_document_states_both_closeout_sentences(self):
        normalized = " ".join(self.research.split())
        for phrase in (
            "Engineering capability added:",
            "Scientific claim not established:",
            "Loop 48 Stage B remains the next protected decision",
            "S25 remains the future one-time final test",
            "no pooled-only pass",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
