import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop33_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_33_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "docs" / "POST_20_ROADMAP.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
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


class Loop33ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_all_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop33_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_experiment_blocked_on_loop25_loop26_and_validation_access_order",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_protected_cache_signal_target_checkpoint_model_training_validation_or_acquisition",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 23)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_keeps_curve_exponent_seeds_and_acquisition_unavailable(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L33-C0_no_new_result")
        self.assertEqual(
            decision["recommended_unique_sentence_prefix_counts"], [8, 16, 24, 32, 44, 55]
        )
        self.assertFalse(decision["universal_scaling_law_available_now_or_from_this_design"])
        self.assertFalse(decision["brain2qwerty_v2_scaling_exponent_transferable_to_local_curve"])
        self.assertFalse(decision["physical_repetition_comparison_available_now"])
        self.assertFalse(decision["additional_acquisition_recommended_now"])
        self.assertEqual(decision["exact_optimization_seeds_selected_now"], [])
        self.assertFalse(decision["preregistration_prepared_now"])

    def test_dependencies_preserve_one_prospective_shared_validation_event(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop33_planning_research_complete"])
        self.assertFalse(dependencies["loop25_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop26_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop31_dependency_satisfied_now"])
        self.assertTrue(
            dependencies["loop33_may_be_copreregistered_with_loop26_before_validation_target_open"]
        )
        self.assertEqual(dependencies["source_validation_target_open_count_now"], 0)
        self.assertTrue(dependencies["prospective_shared_validation_path_available_now"])
        self.assertTrue(
            dependencies["prospective_path_is_lost_if_loop26_targets_open_before_loop33_freeze"]
        )
        self.assertTrue(
            dependencies["fresh_physical_validation_required_after_lost_prospective_path"]
        )

    def test_evidence_inventory_preserves_negative_planning_and_public_boundaries(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 7)
        self.assertIn("55 train, 6 reserved validation", evidence["loop14_source_split"]["finding"])
        self.assertIn("worse than its no-signal", evidence["loop15_s21_cross_session"]["finding"])
        self.assertIn("2,908-parameter", evidence["loop26_encoder_gate"]["finding"])
        self.assertIn("five-condition", evidence["brain2qwerty_v2_scaling"]["finding"])
        self.assertIn("audio supervision", evidence["eeg_speech_scaling"]["finding"])
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_scale_contract_varies_only_unique_sentence_prefixes(self):
        contract = self.boundary["local_scale_contract"]
        self.assertEqual(contract["fixed_person_count"], 1)
        self.assertEqual(contract["fixed_session_count"], 1)
        self.assertEqual(contract["fixed_modality"], "MEG")
        self.assertEqual(contract["fixed_model_parameter_count"], 2908)
        self.assertEqual(contract["varied_axis"], "nested_unique_source_train_sentence_instances")
        self.assertEqual(len(contract["required_report_axes"]), 5)
        self.assertEqual(
            contract["hours_label_allowed_only_when_valid_signal_seconds_at_least"], 3600
        )
        self.assertTrue(contract["otherwise_report_minutes"])
        self.assertFalse(contract["formal_power_law_fit_or_extrapolation_allowed"])
        self.assertFalse(contract["brain2qwerty_v2_90_hour_curve_is_a_local_reference_curve"])

    def test_prefix_schedule_is_nested_target_blind_and_bounded_to_eighteen_fits(self):
        schedule = self.boundary["nested_prefix_recommendation"]
        self.assertEqual(schedule["counts"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(schedule["maximum_sizes"], 6)
        self.assertEqual(schedule["maximum_optimization_seeds"], 3)
        self.assertEqual(schedule["maximum_candidate_training_runs"], 18)
        self.assertIsNone(schedule["exact_seed_values"])
        self.assertTrue(schedule["strictly_nested"])
        self.assertTrue(schedule["full_size_exactly_equals_all_55_source_train_rows"])
        self.assertFalse(schedule["validation_or_test_information_may_affect_membership_order"])
        self.assertTrue(
            schedule[
                "all_prefix_membership_ids_and_hashes_must_freeze_before_any_signal_or_target_open"
            ]
        )
        self.assertTrue(schedule["seeds_are_optimization_replicates_not_biological_replicates"])

    def test_repetition_contract_rejects_duplicate_arrays_as_new_acquisitions(self):
        contract = self.boundary["unique_vs_repetition_contract"]
        self.assertFalse(contract["current_physical_repetition_groups_available"])
        self.assertTrue(
            contract["current_source_train_rows_may_support_unique_sentence_curve_only"]
        )
        self.assertFalse(
            contract[
                "duplicating_reweighting_or_augmenting_one_recorded_row_counts_as_physical_repetition"
            ]
        )
        self.assertTrue(
            contract["future_physical_repetition_lane_requires_distinct_performed_row_ids"]
        )
        self.assertTrue(
            contract[
                "future_physical_repetition_lane_requires_same_normalized_prompt_hash_with_distinct_recordings"
            ]
        )
        self.assertTrue(
            contract["future_matched_comparison_requires_equal_total_physical_trial_count"]
        )
        self.assertFalse(contract["absence_of_repetition_lane_invalidates_unique_sentence_curve"])
        self.assertTrue(
            contract["absence_of_repetition_lane_invalidates_repetition_efficiency_claim"]
        )

    def test_access_sequence_freezes_all_predictions_before_one_target_open(self):
        contract = self.boundary["shared_validation_access_contract"]
        sequence = contract["required_sequence"]
        self.assertEqual(contract["validation_rows"], 6)
        self.assertEqual(len(sequence), 10)
        self.assertLess(
            sequence.index(
                "hash_freeze_all_models_configs_prefixes_predictions_access_ledgers_and_payloads"
            ),
            sequence.index(
                "open_all_six_validation_targets_once_and_score_every_condition_in_one_pass"
            ),
        )
        self.assertIn("mark_source_validation_targets_consumed", sequence[8])
        self.assertIn("without_restart", sequence[9])
        self.assertFalse(contract["exploratory_curve_may_authorize_acquisition_or_scaling_claim"])

    def test_condition_matrix_has_four_unique_unstarted_or_unavailable_conditions(self):
        matrix = self.boundary["future_condition_matrix"]
        condition_ids = [row["condition_id"] for row in matrix]
        self.assertEqual(len(condition_ids), 4)
        self.assertEqual(len(condition_ids), len(set(condition_ids)))
        self.assertEqual(matrix[0]["sizes"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(matrix[0]["maximum_seeds"], 3)
        self.assertIn("no_signal_prior", matrix[1]["condition_id"])
        self.assertIn("Loop 31", matrix[2]["role"])
        self.assertIn("unavailable", matrix[3]["execution_status"])

    def test_statistics_are_descriptive_bounded_and_not_population_inference(self):
        stats = self.boundary["statistical_decision_recommendation"]
        self.assertEqual(stats["registered_x_axis"], "log2_unique_train_sentence_count")
        self.assertEqual(stats["smallest_band_counts"], [8, 16])
        self.assertEqual(stats["upper_band_counts"], [44, 55])
        self.assertEqual(
            stats["minimum_practical_smallest_to_upper_band_macro_cer_gain_recommendation"], 0.05
        )
        self.assertEqual(
            stats["minimum_practical_upper_band_gain_over_size_matched_prior_recommendation"], 0.05
        )
        self.assertTrue(stats["all_seed_slopes_must_be_negative_for_stable_bounded_trend"])
        self.assertFalse(stats["every_adjacent_size_must_improve"])
        self.assertTrue(stats["all_adjacent_deltas_must_be_reported"])
        self.assertIsNone(stats["formal_p_value_for_slope"])
        self.assertEqual(stats["biological_replicates"], 1)
        self.assertFalse(stats["population_inference_supported"])
        self.assertFalse(stats["extrapolation_beyond_55_sentences_supported"])

    def test_outcome_and_claim_taxonomies_are_exact_and_conservative(self):
        outcomes = self.boundary["outcome_taxonomy"]
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(outcomes), 7)
        self.assertEqual(
            [row["outcome_id"].split("_", 1)[0] for row in outcomes],
            [f"L33-O{i}" for i in range(7)],
        )
        self.assertEqual(len(claims), 7)
        self.assertEqual(
            [row["claim_id"].split("_", 1)[0] for row in claims], [f"L33-C{i}" for i in range(7)]
        )
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        self.assertIn("separate metadata-only acquisition packet", outcomes[-1]["meaning"])
        self.assertIn("duplicated arrays are ineligible", claims[5]["boundary"])

    def test_future_gates_and_refusals_are_exact_unique_and_fail_closed(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 20)
        self.assertEqual(len({row["requirement_id"] for row in gates}), 20)
        self.assertEqual(
            [row["requirement_id"].split("_", 1)[0] for row in gates],
            [f"L33-G{i:02d}" for i in range(1, 21)],
        )
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(set(refusals)), 30)
        self.assertEqual(
            [value.split("_", 1)[0] for value in refusals], [f"L33-R{i:02d}" for i in range(1, 31)]
        )
        combined = " ".join(refusals)
        for phrase in (
            "target",
            "prior",
            "biological",
            "repetition",
            "90_hour",
            "energy",
            "acquisition",
            "clinical",
        ):
            self.assertIn(phrase, combined)

    def test_resources_and_protected_access_are_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_model_parameter_ceiling"], 2908)
        self.assertEqual(resources["future_maximum_candidate_training_runs"], 18)
        self.assertEqual(resources["future_total_training_runtime_cap_sec"], 1200)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 32 * 1024**2)
        self.assertEqual(
            resources["future_new_data_or_model_download_bytes_before_separate_authorization"], 0
        )
        self.assertFalse(resources["future_direct_energy_measurement_available"])
        self.assertFalse(resources["cpu_time_may_be_reported_as_energy"])
        self.assertFalse(
            resources["storage_envelope_is_data_access_acquisition_or_execution_authorization"]
        )
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 6)
        self.assertEqual(counters["protected_dataset_model_or_weight_download_bytes"], 0)
        self.assertIsNone(counters["public_network_response_bytes"])
        numeric = [
            value
            for key, value in counters.items()
            if key
            not in {
                "high_level_public_web_research_operations",
                "public_network_response_bytes",
                "public_network_response_bytes_unavailable_reason",
            }
            and isinstance(value, int)
        ]
        self.assertTrue(all(value == 0 for value in numeric))

    def test_sources_and_claim_boundary_are_explicit(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 7)
        source_ids = {row["source_id"] for row in sources}
        self.assertTrue(
            {
                "brain2qwerty_v2_paper",
                "brain_decoding_image_scaling",
                "eeg_speech_scaling_175h",
                "classification_learning_curve_sample_size",
                "small_sample_cv_uncertainty",
            }.issubset(source_ids)
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        claim_text = " ".join(self.boundary["claim_boundary"])
        for term in (
            "not a preregistration",
            "No protected cache",
            "duplicated arrays",
            "No universal scaling law",
        ):
            self.assertIn(term, claim_text)

    def test_human_note_contains_exact_engineering_and_scientific_boundaries(self):
        for text in (
            "experiment Not Started",
            "8, 16, 24, 32, 44, 55",
            "18 candidate fits",
            "1,200 seconds",
            "open all six validation targets once",
            "duplicating an array row",
            "No acquisition is recommended now",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.11.0")
        boundary = self.roadmap["current_boundary"]
        self.assertTrue(boundary["loop33_research_packet_prepared"])
        self.assertEqual(boundary["loop33_prefix_counts"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(boundary["loop33_maximum_candidate_training_runs"], 18)
        self.assertEqual(boundary["loop33_future_requirement_count"], 20)
        self.assertEqual(boundary["loop33_future_refusal_count"], 30)
        self.assertTrue(boundary["loop33_prospective_shared_validation_path_available"])
        self.assertFalse(boundary["loop33_physical_repetition_lane_available"])
        self.assertFalse(boundary["loop33_acquisition_recommended"])
        self.assertFalse(boundary["loop33_preregistration_prepared"])
        self.assertFalse(boundary["loop33_execution_authorized"])
        loop33 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 33)
        self.assertEqual(loop33["research_status"], "planning_research_complete")
        self.assertEqual(loop33["research_packet"], "docs/LOOP_33_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(loop33["research_registry"], "registries/loop33_research_boundary.v0.json")
        self.assertEqual(loop33["prefix_counts"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(loop33["future_requirement_count"], 20)
        self.assertEqual(loop33["future_refusal_count"], 30)
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 33", content)
                self.assertIn("planning research", content.lower())
                self.assertIn("Not Started", content)
                self.assertIn("8, 16, 24, 32, 44, 55", content)
                self.assertIn("unauthorized", content.lower())


if __name__ == "__main__":
    unittest.main()
