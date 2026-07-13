import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop35_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_35_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop35ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop35_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_experiment_blocked_on_loop31_and_fresh_synchronized_multimodal_evidence",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_protected_signal_target_model_confounds_fixture_acquisition_device_or_brain_specific_claim",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 31)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_future_claim_beyond_recorded_controls(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L35-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_local_claim_with_fresh_complete_multimodal_evidence"],
            "L35-C4_incremental_brain_sensor_information_beyond_recorded_controls",
        )
        self.assertFalse(
            decision["absolute_brain_specific_origin_claim_available_from_this_design"]
        )
        self.assertFalse(decision["patient_no_keypress_transfer_available_from_this_design"])
        self.assertFalse(decision["brain_sensor_channel_label_proves_brain_origin"])
        self.assertFalse(decision["artifact_rejection_proves_artifact_absence"])
        self.assertTrue(decision["negative_or_peripheral_explanation_is_publishable_result"])
        self.assertEqual(decision["missing_control_default"], "claim_unavailable")

    def test_dependencies_require_loop31_and_fresh_multimodal_evidence(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop31_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop31_execution_result_available_now"])
        self.assertTrue(
            dependencies["loop31_sensor_signal_dependence_required_before_loop35_increment"]
        )
        self.assertTrue(dependencies["loop30_clock_domain_contract_required_for_synchronization"])
        self.assertFalse(dependencies["current_s21_cache_is_complete_loop35_multimodal_evidence"])
        self.assertFalse(dependencies["consumed_s7_eeg_is_fresh_loop35_evidence"])
        self.assertFalse(dependencies["fresh_synchronized_multimodal_protocol_exists_now"])
        self.assertFalse(dependencies["fresh_multimodal_consent_and_retention_packet_exists_now"])

    def test_existing_evidence_preserves_overt_task_missing_controls_and_negative_results(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 8)
        self.assertIn("known keypresses", evidence["brain2qwerty_v1_task"]["finding"])
        self.assertIn("physically typing", evidence["brain2qwerty_v2_task"]["finding"])
        self.assertIn("102 magnetometers", evidence["s21_local_meg_cache"]["finding"])
        self.assertIn("three ocular channels", evidence["s7_local_eeg_bridge"]["finding"])
        self.assertIn(
            "worse than no-signal", evidence["local_negative_predictive_results"]["finding"]
        )
        self.assertIn("more informative", evidence["movement_artifact_bci_and_meg"]["finding"])
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_confound_taxonomy_has_ten_unique_classes_and_hard_leakage_rules(self):
        taxonomy = self.boundary["confound_taxonomy"]
        self.assertEqual(len(taxonomy), 10)
        ids = [row["confound_id"] for row in taxonomy]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            [value.split("_", 1)[0] for value in ids], [f"L35-T{i:02d}" for i in range(10)]
        )
        self.assertFalse(taxonomy[0]["may_enter_predictive_features"])
        self.assertFalse(taxonomy[1]["may_enter_predictive_features"])
        self.assertTrue(taxonomy[2]["may_enter_timing_control_only"])
        self.assertTrue(taxonomy[3]["requires_eog_or_eye_tracking"])
        self.assertTrue(taxonomy[4]["requires_emg_or_kinematics"])
        self.assertTrue(taxonomy[5]["requires_emg_or_kinematics"])

    def test_current_data_can_audit_timing_but_not_close_peripheral_firewall(self):
        availability = self.boundary["current_data_availability"]
        self.assertEqual(availability["s21_meg_brain_sensor_channels"], 102)
        self.assertTrue(availability["s21_stim_timing_available_in_committed_cache_path"])
        self.assertTrue(
            availability["s21_key_identity_available_but_forbidden_as_predictive_input"]
        )
        for key in (
            "s21_synchronized_eog_available_in_committed_cache_path",
            "s21_synchronized_emg_available_in_committed_cache_path",
            "s21_synchronized_gaze_available_in_committed_cache_path",
            "s21_synchronized_motion_available_in_committed_cache_path",
            "s21_synchronized_audio_available_in_committed_cache_path",
        ):
            self.assertFalse(availability[key])
        self.assertEqual(availability["s7_source_named_eog_channels"], 3)
        self.assertEqual(availability["s7_eog_channels_in_eeg_cache"], 0)
        self.assertTrue(availability["s7_evidence_consumed"])
        self.assertTrue(
            availability[
                "current_data_can_support_timing_shortcut_audit_after_separate_authorization"
            ]
        )
        self.assertFalse(availability["current_data_can_support_complete_peripheral_firewall"])
        self.assertFalse(availability["current_data_can_support_brain_specific_claim"])

    def test_three_stages_are_separate_and_never_self_authorizing(self):
        stages = self.boundary["staged_future_program"]
        self.assertEqual(len(stages), 3)
        self.assertEqual(
            [row["stage_id"].split("_", 1)[0] for row in stages], ["L35-A", "L35-B", "L35-C"]
        )
        self.assertTrue(all(row["authorizes_next_stage"] is False for row in stages))
        self.assertIn("synthetic", stages[0]["maximum_claim"])
        self.assertIn("recorded_controls", stages[1]["maximum_claim"])
        self.assertIn("patient", stages[2]["maximum_claim"])

    def test_stream_registry_has_nine_typed_streams_and_no_peripheral_brain_labels(self):
        streams = self.boundary["future_stream_registry"]
        self.assertEqual(len(streams), 9)
        ids = [row["stream_id"] for row in streams]
        self.assertEqual(
            [value.split("_", 1)[0] for value in ids], [f"L35-M{i:02d}" for i in range(9)]
        )
        self.assertFalse(streams[0]["brain_origin_guaranteed_by_channel_type"])
        self.assertTrue(all(row["brain_signal"] is False for row in streams[1:]))

    def test_condition_matrix_has_thirteen_unique_conditions_and_unavailable_controls(self):
        matrix = self.boundary["future_condition_matrix"]
        self.assertEqual(len(matrix), 13)
        ids = [row["condition_id"] for row in matrix]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            [value.split("_", 1)[0] for value in ids], [f"L35-E{i:02d}" for i in range(13)]
        )
        self.assertIn("never eligible", matrix[2]["role"])
        self.assertIn("never eligible", matrix[3]["role"])
        self.assertEqual(matrix[9]["role"], "strongest combined nonbrain comparator")
        self.assertEqual(matrix[10]["status"], "not_started")
        self.assertEqual(matrix[11]["status"], "unavailable_until_recorded")
        self.assertEqual(matrix[12]["status"], "unavailable_until_recorded")

    def test_partition_rule_is_physical_disjoint_and_missing_controls_are_not_imputed(self):
        partition = self.boundary["partition_and_selection_recommendation"]
        self.assertEqual(
            [
                partition["calibration_sentence_floor"],
                partition["selection_sentence_floor"],
                partition["final_sentence_floor"],
            ],
            [32, 16, 48],
        )
        self.assertTrue(partition["performed_row_ids_disjoint"])
        self.assertTrue(partition["semantic_text_hashes_disjoint"])
        self.assertTrue(partition["strongest_peripheral_condition_selected_on_selection_only"])
        self.assertTrue(
            partition["all_conditions_predictions_and_hashes_freeze_before_final_targets"]
        )
        self.assertTrue(partition["final_targets_open_once"])
        self.assertFalse(partition["unrecorded_stream_may_be_imputed_as_clean_or_zero_control"])
        self.assertFalse(partition["synthetic_streams_may_replace_missing_real_controls"])
        self.assertFalse(partition["one_person_supports_population_inference"])

    def test_estimands_require_increment_over_peripheral_controls(self):
        stats = self.boundary["estimands_and_statistics_recommendation"]
        self.assertIn("strongest_peripheral", stats["primary_estimand"])
        self.assertIn("all_synchronized", stats["primary_estimand"])
        self.assertIn("strongest_nonbrain", stats["secondary_brain_sensor_estimand"])
        self.assertEqual(stats["primary_practical_margin_recommendation"], 0.05)
        self.assertEqual(stats["secondary_practical_margin_recommendation"], 0.05)
        self.assertFalse(stats["practical_margins_frozen_now"])
        self.assertEqual(stats["paired_random_sign_assignments_plus_observed"], 65536)
        self.assertEqual(
            stats["familywise_decision"],
            "intersection_union_all_registered_required_components_pass",
        )
        self.assertFalse(stats["control_tie_passes"])
        self.assertFalse(stats["population_inference_supported"])
        self.assertFalse(stats["neural_origin_proven_by_performance_only"])

    def test_sync_and_residualization_are_train_only_and_report_raw_results(self):
        sync = self.boundary["synchronization_and_residualization_boundary"]
        self.assertTrue(sync["all_streams_require_source_and_host_clock_identity"])
        self.assertTrue(sync["clock_conversion_must_follow_loop30"])
        self.assertTrue(sync["dropped_packet_missing_interval_and_clock_reset_counts_required"])
        self.assertTrue(sync["alignment_residual_distribution_required"])
        self.assertTrue(sync["residualization_statistics_fit_on_train_only"])
        self.assertFalse(sync["residualization_may_use_selection_or_final_targets"])
        self.assertTrue(sync["raw_and_residualized_results_both_reported"])
        self.assertFalse(sync["artifact_correction_may_be_selected_for_best_final_result"])
        self.assertTrue(
            sync["source_localization_or_topography_is_supporting_not_decisive_evidence"]
        )

    def test_access_sequence_preserves_stage_and_target_order(self):
        sequence = self.boundary["future_access_sequence"]
        self.assertEqual(len(sequence), 12)
        self.assertLess(
            sequence.index(
                "commit_push_and_separately_authorize_only_the_synthetic_interface_stage"
            ),
            sequence.index(
                "run_target_free_synthetic_interface_gate_and_close_without_claiming_biology"
            ),
        )
        self.assertLess(
            sequence.index("commit_push_and_obtain_a_new_exact_real_multimodal_authorization"),
            sequence.index(
                "acquire_or_access_calibration_selection_and_final recordings without opening final targets"
            ),
        )
        self.assertLess(
            sequence.index(
                "generate_and_hash_freeze_every_final prediction condition config access ledger and payload before final targets"
            ),
            sequence.index(
                "open_final_targets_once and score the complete condition matrix in one pass"
            ),
        )
        self.assertIn("without restart", sequence[-1])

    def test_outcomes_and_claims_are_exact_and_fail_closed(self):
        outcomes = self.boundary["outcome_taxonomy"]
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(outcomes), 8)
        self.assertEqual(
            [row["outcome_id"].split("_", 1)[0] for row in outcomes],
            [f"L35-O{i}" for i in range(8)],
        )
        self.assertEqual(len(claims), 7)
        self.assertEqual(
            [row["claim_id"].split("_", 1)[0] for row in claims], [f"L35-C{i}" for i in range(7)]
        )
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        self.assertIn("peripheral", outcomes[4]["meaning"])
        self.assertIn("recorded controls", claims[4]["boundary"])
        self.assertIn("separately authorized", claims[5]["boundary"])

    def test_future_gates_and_refusals_are_exact_unique_and_comprehensive(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 24)
        self.assertEqual(len({row["requirement_id"] for row in gates}), 24)
        self.assertEqual(
            [row["requirement_id"].split("_", 1)[0] for row in gates],
            [f"L35-G{i:02d}" for i in range(1, 25)],
        )
        self.assertEqual(len(refusals), 32)
        self.assertEqual(len(set(refusals)), 32)
        self.assertEqual(
            [value.split("_", 1)[0] for value in refusals], [f"L35-R{i:02d}" for i in range(1, 33)]
        )
        combined = " ".join(refusals)
        for phrase in (
            "consent",
            "target",
            "key_identity",
            "missing_required_peripheral",
            "brain_origin",
            "artifact",
            "sync",
            "final",
            "peripheral",
            "patient",
            "clinical",
        ):
            self.assertIn(phrase, combined)

    def test_resources_and_protected_access_are_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_stage_a_cpu_threads"], 1)
        self.assertEqual(resources["future_stage_a_runtime_cap_sec"], 120)
        self.assertEqual(resources["future_stage_a_generated_artifact_cap_bytes"], 16 * 1024**2)
        self.assertEqual(resources["future_stage_b_analysis_runtime_cap_sec"], 1200)
        self.assertEqual(resources["future_stage_b_generated_artifact_cap_bytes"], 32 * 1024**2)
        self.assertIsNone(resources["future_stage_b_acquisition_byte_cap"])
        self.assertEqual(
            resources["future_new_data_or_model_download_bytes_before_separate_authorization"], 0
        )
        self.assertFalse(resources["future_direct_energy_measurement_available"])
        self.assertFalse(resources["cpu_time_may_be_reported_as_energy"])
        self.assertFalse(
            resources[
                "storage_envelope_is_multimodal_acquisition_data_access_or_execution_authorization"
            ]
        )
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 6)
        self.assertEqual(counters["protected_dataset_model_or_weight_download_bytes"], 0)
        self.assertIsNone(counters["public_network_response_bytes"])
        excluded = {
            "high_level_public_web_research_operations",
            "public_network_response_bytes",
            "public_network_response_bytes_unavailable_reason",
        }
        numeric = [
            value
            for key, value in counters.items()
            if key not in excluded and isinstance(value, int)
        ]
        self.assertTrue(all(value == 0 for value in numeric))

    def test_sources_claim_boundary_and_human_note_are_explicit(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        source_ids = {row["source_id"] for row in sources}
        self.assertTrue(
            {
                "brain2qwerty_v1_paper",
                "brain2qwerty_v2_paper",
                "eye_movement_decoding_confounds",
                "eeg_bci_artifacts_friend_or_foe",
                "meg_speech_artifact_correction",
                "motion_muscle_phantom_validation",
            }.issubset(source_ids)
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        claim_text = " ".join(self.boundary["claim_boundary"])
        for term in (
            "not a preregistration",
            "No protected signal",
            "cannot provide a fresh complete",
            "do not by themselves prove",
            "beyond every recorded",
            "No absolute brain origin",
        ):
            self.assertIn(term, claim_text)
        for text in (
            "experiment Not Started",
            "ten confound classes",
            "nine future synchronized stream classes",
            "13-condition matrix",
            "32 unique",
            "16 unique",
            "48 unique",
            "65,535",
            "24 gates",
            "32 refusals",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.20.0")
        boundary = self.roadmap["current_boundary"]
        self.assertTrue(boundary["loop35_research_packet_prepared"])
        self.assertEqual(boundary["loop35_confound_class_count"], 10)
        self.assertEqual(boundary["loop35_future_stream_count"], 9)
        self.assertEqual(boundary["loop35_future_condition_count"], 13)
        self.assertEqual(boundary["loop35_staged_program_count"], 3)
        self.assertEqual(boundary["loop35_future_requirement_count"], 24)
        self.assertEqual(boundary["loop35_future_refusal_count"], 32)
        self.assertFalse(boundary["loop35_current_complete_multimodal_evidence_available"])
        self.assertEqual(
            boundary["loop35_maximum_future_local_claim"],
            "incremental_brain_sensor_information_beyond_recorded_controls",
        )
        self.assertFalse(boundary["loop35_absolute_brain_origin_claim_available"])
        self.assertFalse(boundary["loop35_preregistration_prepared"])
        self.assertFalse(boundary["loop35_execution_authorized"])
        loop35 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 35)
        self.assertEqual(loop35["research_status"], "planning_research_complete")
        self.assertEqual(loop35["research_packet"], "docs/LOOP_35_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(loop35["research_registry"], "registries/loop35_research_boundary.v0.json")
        self.assertEqual(loop35["confound_class_count"], 10)
        self.assertEqual(loop35["future_condition_count"], 13)
        self.assertEqual(loop35["future_requirement_count"], 24)
        self.assertEqual(loop35["future_refusal_count"], 32)
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 35", content)
                self.assertIn("planning research", content.lower())
                self.assertIn("Not Started", content)
                self.assertIn("incremental brain-sensor", content)
                self.assertIn("unauthorized", content.lower())


if __name__ == "__main__":
    unittest.main()
