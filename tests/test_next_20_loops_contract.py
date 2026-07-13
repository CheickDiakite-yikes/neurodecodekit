import json
import re
import unittest
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
LOOP24_PATH = REPO_ROOT / "registries" / "local_precision_runtime_contract.v0.json"
RW3_PATH = REPO_ROOT / "registries" / "replay_equivalence_contract.v0.json"
RW3_REQUEST_PATH = REPO_ROOT / "registries" / "rw3_stage_a_authorization_request.v0.json"
LOOP25_REQUEST_PATH = REPO_ROOT / "registries" / "loop25_authorization_request.v1.json"


class NextTwentyLoopsContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.loops = cls.roadmap["loops"]

    def test_identity_range_and_planning_boundary_are_exact(self):
        roadmap = self.roadmap
        self.assertEqual(roadmap["schema_name"], "neurodecodekit.next_twenty_loops_roadmap")
        self.assertEqual(roadmap["schema_version"], "0.14.0")
        self.assertEqual(roadmap["roadmap_id"], "loops-25-44")
        self.assertEqual(roadmap["status"], "planning_only_not_execution_authorization")
        self.assertEqual(
            roadmap["range"],
            {"first_loop": 25, "last_loop": 44, "loop_count": 20},
        )
        boundary = roadmap["current_boundary"]
        self.assertEqual(boundary["current_numbered_gate"], 25)
        self.assertEqual(
            boundary["current_gate_status"],
            "amended_preregistration_awaiting_explicit_authorization",
        )
        self.assertEqual(boundary["loop24_status"], "parked_resource_cap_exceeded")
        self.assertTrue(boundary["loop24_execution_was_authorized"])
        self.assertFalse(boundary["loop24_execution_authorized_now"])
        self.assertTrue(boundary["loop25_preregistration_ci_green"])
        self.assertTrue(boundary["loop25_amendment_ci_green"])
        self.assertTrue(boundary["loop25_original_request_superseded_before_authorization"])
        self.assertTrue(boundary["loop25_authorization_request_prepared"])
        self.assertFalse(boundary["loop25_execution_authorized"])
        self.assertFalse(boundary["loop25_development_seed_opened"])
        self.assertFalse(boundary["loop25_qualification_seed_opened"])
        self.assertTrue(boundary["loop26_research_packet_prepared"])
        self.assertFalse(boundary["loop26_preregistration_prepared"])
        self.assertFalse(boundary["loop26_execution_authorized"])
        self.assertFalse(boundary["loop26_dependency_loop25_satisfied"])
        self.assertTrue(boundary["loop27_research_packet_prepared"])
        self.assertEqual(
            boundary["loop27_selected_candidate"],
            "spanishbcbl-meg-s25-session2-block2-v0",
        )
        self.assertFalse(boundary["loop27_preregistration_prepared"])
        self.assertFalse(boundary["loop27_acquisition_request_prepared"])
        self.assertFalse(boundary["loop27_download_authorized"])
        self.assertTrue(boundary["loop28_research_packet_prepared"])
        self.assertEqual(
            boundary["loop28_selected_claim_level"],
            "T2_unseen_person_strict_zero_shot",
        )
        self.assertTrue(boundary["loop28_final_only_rule_research_ready"])
        self.assertFalse(boundary["loop28_preregistration_prepared"])
        self.assertFalse(boundary["loop28_execution_authorized"])
        self.assertFalse(boundary["loop28_dependency_loop25_satisfied"])
        self.assertFalse(boundary["loop28_dependency_loop26_satisfied"])
        self.assertFalse(boundary["loop28_dependency_loop27_satisfied"])
        self.assertTrue(boundary["loop29_research_packet_prepared"])
        self.assertEqual(
            boundary["loop29_selected_accessibility_lane"],
            "scalp_EEG_local_first",
        )
        self.assertEqual(boundary["loop29_selected_partner_lane"], "OPM_MEG_partner_lab")
        self.assertIsNone(boundary["loop29_selected_device"])
        self.assertFalse(boundary["loop29_preregistration_prepared"])
        self.assertFalse(boundary["loop29_execution_authorized"])
        self.assertFalse(boundary["loop29_real_data_download_authorized"])
        self.assertFalse(boundary["loop29_device_or_hardware_authorized"])
        self.assertTrue(boundary["loop30_research_packet_prepared"])
        self.assertEqual(boundary["loop30_future_source_mode"], "synthetic_replay")
        self.assertEqual(boundary["loop30_clock_domain_count"], 9)
        self.assertEqual(boundary["loop30_future_requirement_count"], 18)
        self.assertEqual(boundary["loop30_future_refusal_count"], 30)
        self.assertFalse(boundary["loop30_preregistration_prepared"])
        self.assertFalse(boundary["loop30_trace_fixture_exists"])
        self.assertFalse(boundary["loop30_execution_authorized"])
        self.assertFalse(boundary["loop30_server_or_browser_run_authorized"])
        self.assertTrue(boundary["loop31_research_packet_prepared"])
        self.assertEqual(boundary["loop31_encoder_condition_count"], 10)
        self.assertEqual(boundary["loop31_language_model_condition_count"], 5)
        self.assertEqual(boundary["loop31_future_requirement_count"], 18)
        self.assertEqual(boundary["loop31_future_refusal_count"], 24)
        self.assertEqual(
            boundary["loop31_maximum_future_local_claim"],
            "sensor_signal_dependence",
        )
        self.assertTrue(boundary["loop31_brain_specific_claim_requires_loop35"])
        self.assertFalse(boundary["loop31_preregistration_prepared"])
        self.assertFalse(boundary["loop31_authorization_request_prepared"])
        self.assertFalse(boundary["loop31_execution_authorized"])
        self.assertFalse(boundary["loop31_dependency_loop26_satisfied"])
        self.assertTrue(boundary["loop32_research_packet_prepared"])
        self.assertEqual(boundary["loop32_calibration_mode_count"], 4)
        self.assertEqual(boundary["loop32_budget_counts"], [0, 2, 4, 8, 16, 32])
        self.assertEqual(boundary["loop32_target_trainable_parameter_ceiling"], 32)
        self.assertEqual(boundary["loop32_future_requirement_count"], 20)
        self.assertEqual(boundary["loop32_future_refusal_count"], 26)
        self.assertFalse(boundary["loop32_candidate_selected"])
        self.assertFalse(boundary["loop32_preregistration_prepared"])
        self.assertFalse(boundary["loop32_authorization_request_prepared"])
        self.assertFalse(boundary["loop32_execution_authorized"])
        self.assertFalse(boundary["loop32_dependency_loop25_satisfied"])
        self.assertFalse(boundary["loop32_dependency_loop26_satisfied"])
        self.assertFalse(boundary["loop32_dependency_loop31_satisfied"])
        self.assertTrue(boundary["loop33_research_packet_prepared"])
        self.assertEqual(boundary["loop33_prefix_counts"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(boundary["loop33_maximum_optimization_seeds"], 3)
        self.assertEqual(boundary["loop33_maximum_candidate_training_runs"], 18)
        self.assertEqual(boundary["loop33_future_requirement_count"], 20)
        self.assertEqual(boundary["loop33_future_refusal_count"], 30)
        self.assertTrue(boundary["loop33_prospective_shared_validation_path_available"])
        self.assertFalse(boundary["loop33_physical_repetition_lane_available"])
        self.assertFalse(boundary["loop33_acquisition_recommended"])
        self.assertFalse(boundary["loop33_preregistration_prepared"])
        self.assertFalse(boundary["loop33_authorization_request_prepared"])
        self.assertFalse(boundary["loop33_execution_authorized"])
        self.assertFalse(boundary["loop33_dependency_loop25_satisfied"])
        self.assertFalse(boundary["loop33_dependency_loop26_satisfied"])
        self.assertFalse(boundary["loop33_dependency_loop31_satisfied"])
        self.assertTrue(boundary["loop34_research_packet_prepared"])
        self.assertEqual(boundary["loop34_confidence_semantics_count"], 7)
        self.assertEqual(boundary["loop34_candidate_score_count"], 8)
        self.assertEqual(boundary["loop34_recommended_partition_counts"], [128, 64, 256])
        self.assertEqual(boundary["loop34_future_requirement_count"], 20)
        self.assertEqual(boundary["loop34_future_refusal_count"], 30)
        self.assertFalse(boundary["loop34_existing_real_confidence_partition_available"])
        self.assertEqual(boundary["loop34_confidence_default"], "unavailable")
        self.assertFalse(boundary["loop34_preregistration_prepared"])
        self.assertFalse(boundary["loop34_authorization_request_prepared"])
        self.assertFalse(boundary["loop34_execution_authorized"])
        self.assertFalse(boundary["loop34_dependency_loop30_execution_satisfied"])
        self.assertFalse(boundary["loop34_dependency_loop31_execution_satisfied"])
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
        self.assertFalse(boundary["loop35_dependency_loop31_execution_satisfied"])
        self.assertTrue(boundary["loop36_research_packet_prepared"])
        self.assertEqual(boundary["loop36_representation_layer_count"], 6)
        self.assertEqual(boundary["loop36_modality_profile_count"], 5)
        self.assertEqual(boundary["loop36_channel_record_field_count"], 24)
        self.assertEqual(boundary["loop36_operation_class_count"], 12)
        self.assertEqual(boundary["loop36_future_fixture_family_count"], 16)
        self.assertEqual(boundary["loop36_future_requirement_count"], 22)
        self.assertEqual(boundary["loop36_future_refusal_count"], 30)
        self.assertFalse(boundary["loop36_current_complete_geometry_reference_evidence_available"])
        self.assertEqual(
            boundary["loop36_maximum_future_real_metadata_claim"],
            "declared_metadata_compatibility",
        )
        self.assertFalse(boundary["loop36_preregistration_prepared"])
        self.assertFalse(boundary["loop36_execution_authorized"])
        self.assertFalse(boundary["loop36_dependency_loop29_execution_satisfied"])
        self.assertTrue(boundary["loop37_research_packet_prepared"])
        self.assertEqual(boundary["loop37_export_layer_count"], 6)
        self.assertEqual(boundary["loop37_artifact_profile_count"], 5)
        self.assertEqual(boundary["loop37_standard_field_mapping_count"], 15)
        self.assertEqual(boundary["loop37_ndk_extension_field_count"], 16)
        self.assertEqual(boundary["loop37_future_fixture_family_count"], 20)
        self.assertEqual(boundary["loop37_future_requirement_count"], 24)
        self.assertEqual(boundary["loop37_future_refusal_count"], 32)
        self.assertEqual(boundary["loop37_tracked_neural_or_model_binary_candidate_files"], 0)
        self.assertEqual(
            boundary["loop37_maximum_future_stage_b_claim"],
            "validator_assessed_standard_envelope_with_nonstandard_payloads",
        )
        self.assertFalse(boundary["loop37_preregistration_prepared"])
        self.assertFalse(boundary["loop37_execution_authorized"])
        self.assertFalse(boundary["loop37_bids_validator_authorized"])
        self.assertFalse(boundary["loop37_public_release_authorized"])
        self.assertFalse(boundary["loop37_dependency_loop36_execution_satisfied"])
        self.assertEqual(boundary["user_preferred_incremental_storage_bytes"], 5_000_000_000)
        self.assertEqual(boundary["user_absolute_incremental_storage_bytes"], 10_000_000_000)
        self.assertEqual(boundary["selected_s20_plus_s25_future_bundle_bytes"], 1_106_030_247)
        self.assertFalse(boundary["storage_envelope_is_download_authorization"])
        self.assertFalse(boundary["rw3_stage_a_authorized"])
        self.assertFalse(boundary["general_continuation_is_authorization"])
        self.assertFalse(boundary["roadmap_approval_is_loop_execution_authorization"])

    def test_exactly_twenty_contiguous_loops_are_grouped_four_per_phase(self):
        self.assertEqual([row["loop_id"] for row in self.loops], list(range(25, 45)))
        phases = self.roadmap["phases"]
        self.assertEqual([row["phase_id"] for row in phases], ["P1", "P2", "P3", "P4", "P5"])
        self.assertTrue(all(len(row["loop_ids"]) == 4 for row in phases))
        self.assertEqual(
            [loop_id for phase in phases for loop_id in phase["loop_ids"]],
            list(range(25, 45)),
        )
        phase_counts = Counter(row["phase_id"] for row in self.loops)
        self.assertEqual(phase_counts, Counter({f"P{index}": 4 for index in range(1, 6)}))

    def test_loop25_is_preregistered_and_every_loop_is_unauthorized(self):
        required_text = {
            "title",
            "priority",
            "effort",
            "proof_posture",
            "core_question",
            "why_high_value",
            "build_deliverable",
            "research_deliverable",
            "data_scope",
            "acceptance_boundary",
            "stop_rule",
            "authorization_boundary",
            "resource_cap",
        }
        for row in self.loops:
            with self.subTest(loop=row["loop_id"]):
                self.assertFalse(row["execution_authorized"])
                if row["loop_id"] == 25:
                    self.assertEqual(row["status"], "Amended Preregistration")
                    self.assertEqual(
                        row["proof_posture"],
                        "amended_preregistered_no_implementation_or_execution",
                    )
                    registration = row["registration"]
                    self.assertEqual(registration["commit"][:7], "b6b92d8")
                    self.assertFalse(registration["authorized_now"])
                    self.assertFalse(registration["superseded_v0"]["was_authorized"])
                else:
                    self.assertEqual(row["status"], "Not Started")
                    if row["loop_id"] in {34, 35, 36, 37}:
                        expected = {
                            34: "planning_research_complete_no_confidence_fit_or_result_unauthorized",
                            35: "planning_research_complete_no_confound_fixture_acquisition_or_brain_specific_result_unauthorized",
                            36: "planning_research_complete_no_geometry_fixture_header_signal_transform_or_result_unauthorized",
                            37: "planning_research_complete_experiment_not_started",
                        }
                        self.assertEqual(row["proof_posture"], expected[row["loop_id"]])
                    else:
                        self.assertEqual(row["proof_posture"], "planned_not_authorized")
                    if row["loop_id"] in {26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37}:
                        self.assertEqual(row["research_status"], "planning_research_complete")
                        self.assertFalse(row["preregistration_prepared"])
                    if row["loop_id"] == 27:
                        self.assertFalse(row["acquisition_request_prepared"])
                self.assertTrue(
                    all(isinstance(row[key], str) and row[key].strip() for key in required_text)
                )
                self.assertGreaterEqual(len(row["controls"]), 3)
                self.assertGreaterEqual(len(row["primary_metrics"]), 4)
                self.assertIn(row["priority"], {"P0", "P1", "P2"})
                self.assertIn(row["effort"], {"S", "M", "L"})

    def test_loop_dependencies_are_unique_acyclic_and_point_backward(self):
        loop_ids = {row["loop_id"] for row in self.loops}
        for row in self.loops:
            dependencies = row["depends_on"]
            with self.subTest(loop=row["loop_id"]):
                self.assertEqual(len(dependencies), len(set(dependencies)))
                self.assertTrue(set(dependencies).issubset(loop_ids))
                self.assertTrue(all(dependency < row["loop_id"] for dependency in dependencies))
                self.assertEqual(len(row["external_gates"]), len(set(row["external_gates"])))

    def test_protected_real_evidence_and_consumed_seeds_remain_explicit(self):
        protected = self.roadmap["protected_evidence"]
        self.assertEqual(protected["synthetic_seeds"], [2203, 2303, 2353, 2401])
        self.assertEqual(protected["unopened_synthetic_seeds"], [2402, 2501, 2502])
        real_text = " ".join(protected["real_cohorts"])
        self.assertIn("S21 session-1", real_text)
        self.assertIn("S21 session-2", real_text)
        self.assertIn("S7 EEG", real_text)
        self.assertIn("consumed", real_text)
        self.assertTrue(any("target-free fixture" in rule for rule in protected["rules"]))
        loop_text = json.dumps(self.loops, sort_keys=True)
        self.assertIn("source-test", loop_text)
        self.assertIn("session-2", loop_text)
        self.assertIn("consumed", loop_text)

    def test_global_caps_controls_and_closeout_requirements_are_frozen(self):
        constraints = self.roadmap["global_constraints"]
        self.assertIn("one numerical thread", constraints["cpu"])
        self.assertIn("32 MiB", constraints["storage"])
        self.assertIn("No download", constraints["data"])
        self.assertIn("no-signal prior", constraints["evaluation"])
        self.assertIn("sensitive", constraints["privacy"])
        for term in ["bytes", "runtime", "peak RSS", "access counters", "proceed, park, or kill"]:
            self.assertIn(term, constraints["closeout"])
        self.assertTrue(
            all(
                "thread" in row["resource_cap"].lower() or row["loop_id"] in {27, 29, 35, 38, 44}
                for row in self.loops
            )
        )

    def test_primary_sources_are_unique_secure_and_cover_core_workstreams(self):
        sources = self.roadmap["primary_sources"]
        self.assertGreaterEqual(len(sources), 10)
        self.assertEqual(len({row["source_id"] for row in sources}), len(sources))
        self.assertEqual(len({row["url"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        source_ids = {row["source_id"] for row in sources}
        self.assertTrue(
            {
                "brain2qwerty_v2",
                "brain2qwerty_v2_code",
                "meg_cross_subject_transfer",
                "brain_decoder_cv_guidelines",
                "brain2qwerty_v1",
                "scipy_permutation_test",
                "scipy_bootstrap",
                "classifier_permutation_tests",
                "small_sample_cv_uncertainty",
                "time_series_permutation_dependence",
                "mne_resampling",
                "neuralset_v0_2_2",
                "scipy_iirdesign",
                "bids_derivatives",
                "opm_speech_tracking",
                "opm_lightly_shielded",
                "opm_field_control",
                "opm_interference",
                "mne_opm_processing",
                "home_dry_eeg",
                "bids_eeg",
                "bids_meg",
                "openbci_cyton_format",
                "brainflow_data_format",
                "gradio_blocks",
                "gradio_file_access",
                "python_perf_counter_ns",
                "w3c_high_resolution_time",
                "w3c_long_tasks",
                "w3c_event_timing",
                "wcag_status_messages",
                "playwright_network",
                "streaming_asr_stability",
                "incremental_asr_evaluation",
                "same_analysis_approach",
                "neuroimaging_confounds",
                "intersection_union_tests",
                "coral_domain_adaptation",
                "euclidean_alignment",
                "long_term_bci_calibration_reduction",
                "brain_decoding_image_scaling",
                "eeg_speech_scaling_175h",
                "classification_learning_curve_sample_size",
                "moabb_benchmark",
                "lsl_time_sync",
                "executorch",
                "eeg_identity_privacy",
                "nist_privacy_framework",
                "model_cards",
                "datasheets",
                "selective_prediction",
                "conformal_risk_control",
                "conformal_beyond_exchangeability",
                "neural_network_calibration",
                "calibration_measurement",
                "generalized_risk_coverage",
                "eye_movement_decoding_confounds",
                "eeg_bci_artifacts",
                "meg_movement_muscle_artifacts",
                "motion_muscle_phantom_validation",
                "bids_coordinate_systems",
                "bids_meg",
                "bids_eeg",
                "bids_units",
                "mne_coordinate_frames",
                "mne_transform",
                "mne_digmontage",
                "mne_eeg_reference",
                "mne_bad_interpolation",
                "bids_dataset_description",
                "bids_derivative_common_data",
                "bids_common_principles",
                "bids_extensions",
                "bids_validator",
                "bids_examples",
            }.issubset(source_ids)
        )
        source_map = self.roadmap["loop_source_map"]
        self.assertEqual(set(source_map), {str(loop_id) for loop_id in range(25, 45)})
        for loop_id, mapped_sources in source_map.items():
            with self.subTest(loop=loop_id):
                self.assertGreaterEqual(len(mapped_sources), 1)
                self.assertEqual(len(mapped_sources), len(set(mapped_sources)))
                self.assertTrue(set(mapped_sources).issubset(source_ids))

    def test_existing_loop24_and_rw3_execution_flags_remain_false(self):
        loop24 = json.loads(LOOP24_PATH.read_text(encoding="utf-8"))
        rw3 = json.loads(RW3_PATH.read_text(encoding="utf-8"))
        rw3_request = json.loads(RW3_REQUEST_PATH.read_text(encoding="utf-8"))
        loop25_request = json.loads(LOOP25_REQUEST_PATH.read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                value is False
                for key, value in loop24["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        self.assertTrue(
            all(
                value is False
                for key, value in rw3["authorization"].items()
                if key.endswith("_authorized_now")
            )
        )
        request_flags = []
        for key, value in rw3_request.items():
            if key.endswith("authorized_now"):
                request_flags.append(value)
        for section in rw3_request.values():
            if isinstance(section, dict):
                request_flags.extend(
                    value for key, value in section.items() if key.endswith("authorized_now")
                )
        self.assertTrue(request_flags)
        self.assertTrue(all(value is False for value in request_flags))
        loop25_flags = []
        for key, value in loop25_request.items():
            if key.endswith("authorized_now"):
                loop25_flags.append(value)
        for section in loop25_request.values():
            if isinstance(section, dict):
                loop25_flags.extend(
                    value for key, value in section.items() if key.endswith("authorized_now")
                )
        self.assertTrue(loop25_flags)
        self.assertTrue(all(value is False for value in loop25_flags))

    def test_human_roadmap_and_public_tracker_cover_all_twenty_loops(self):
        roadmap_doc = (REPO_ROOT / "docs" / "LOOPS_25_44_ROADMAP.md").read_text(encoding="utf-8")
        research_doc = (REPO_ROOT / "docs" / "NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md").read_text(
            encoding="utf-8"
        )
        tracker_doc = (REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md").read_text(encoding="utf-8")
        for row in self.loops:
            heading = rf"^## Loop {row['loop_id']} - {re.escape(row['title'])}$"
            with self.subTest(loop=row["loop_id"]):
                self.assertRegex(roadmap_doc, re.compile(heading, re.MULTILINE))
                self.assertIn(f"| {row['loop_id']} |", tracker_doc)
        self.assertIn("registries/next_20_loops.v0.json", roadmap_doc)
        self.assertIn("planning only", roadmap_doc.lower())
        self.assertIn("Brain2Qwerty v2", research_doc)
        self.assertIn("MNE", research_doc)
        self.assertIn("BIDS", research_doc)
        self.assertIn("MOABB", research_doc)


if __name__ == "__main__":
    unittest.main()
