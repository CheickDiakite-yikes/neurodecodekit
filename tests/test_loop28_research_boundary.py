import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop28_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_28_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop28ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_research_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(
            boundary["schema_name"], "neurodecodekit.loop28_research_boundary"
        )
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"], "planning_research_complete_preregistration_blocked"
        )
        self.assertEqual(
            boundary["proof_posture"],
            "primary_source_and_public_code_research_no_data_model_or_target_access",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 21)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_v2_reference_separates_asynchronous_from_causal_and_zero_shot(self):
        reference = self.boundary["brain2qwerty_v2_reference_boundary"]
        self.assertEqual(
            reference["reviewed_code_commit"],
            "3bf5a4099ca0d23bbe994b2287905760236e56e0",
        )
        self.assertEqual(reference["participants"], 9)
        self.assertEqual(reference["sessions_per_participant"], 10)
        self.assertEqual(reference["aggregate_recording_hours"], 90)
        self.assertTrue(reference["model_input_is_continuous_sentence_recording"])
        self.assertFalse(reference["keypress_timing_required_at_inference"])
        self.assertFalse(reference["model_is_causal"])
        self.assertTrue(reference["model_consumes_entire_sentence"])
        self.assertFalse(reference["incremental_word_display_supported"])
        self.assertFalse(reference["end_to_end_low_latency_measured"])
        self.assertTrue(reference["participant_index_conditioned_affine_layer"])
        self.assertTrue(reference["joint_training_includes_target_participant_data"])
        self.assertTrue(
            reference["leave_one_out_regime_finetunes_on_target_participant"]
        )
        self.assertFalse(reference["strict_unseen_person_zero_shot_result_reported"])
        self.assertFalse(reference["englishbcbl_data_public"])

    def test_transfer_taxonomy_has_four_noninterchangeable_levels(self):
        taxonomy = self.boundary["transfer_taxonomy"]
        self.assertEqual([row["level_id"] for row in taxonomy], ["T0", "T1", "T2", "T3"])
        strict = taxonomy[2]
        calibrated = taxonomy[3]
        self.assertFalse(strict["target_person_fit_allowed"])
        self.assertFalse(strict["target_corpus_signal_statistics_allowed"])
        self.assertTrue(strict["deterministic_header_geometry_compatibility_allowed"])
        self.assertTrue(calibrated["target_person_fit_allowed"])
        self.assertTrue(
            calibrated["requires_physically_separate_calibration_and_final_partitions"]
        )
        transductive = self.boundary["transductive_boundary"]
        self.assertTrue(transductive["uses_target_corpus_signal_distribution"])
        self.assertFalse(transductive["counts_as_strict_zero_shot_T2"])

    def test_selected_s25_question_is_strict_zero_fit_final_only(self):
        selected = self.boundary["selected_future_question"]
        self.assertEqual(selected["claim_level"], "T2")
        self.assertEqual(
            selected["candidate_id"], "spanishbcbl-meg-s25-session2-block2-v0"
        )
        self.assertEqual((selected["subject"], selected["session"], selected["block"]), ("S25", 2, 2))
        for key in (
            "candidate_train_rows",
            "candidate_validation_rows",
            "candidate_calibration_rows",
            "candidate_target_wide_fit_rows",
        ):
            self.assertEqual(selected[key], 0, key)
        for key in (
            "candidate_side_model_selection",
            "candidate_side_threshold_selection",
            "candidate_side_normalization_fit",
            "candidate_side_subject_embedding_fit",
            "candidate_side_adapter_fit",
            "candidate_side_unlabeled_corpus_adaptation",
            "candidate_eligible_for_T3_calibrated_claim",
        ):
            self.assertFalse(selected[key], key)
        self.assertEqual(selected["minimum_final_unique_rows"], 48)
        self.assertIn("not a power claim", selected["minimum_row_reason"])

    def test_final_rule_freezes_effect_randomization_and_one_time_order(self):
        rule = self.boundary["future_final_only_decision_rule"]
        self.assertEqual(
            rule["primary_estimand"],
            "macro_mean_sentence_cer_prior_minus_frozen_zero_shot_model",
        )
        self.assertEqual(rule["minimum_absolute_macro_cer_improvement"], 0.05)
        self.assertEqual(rule["minimum_final_unique_rows"], 48)
        randomization = rule["randomization_test"]
        self.assertEqual(randomization["random_sign_assignments"], 65535)
        self.assertTrue(randomization["observed_assignment_included"])
        self.assertEqual(randomization["total_reference_statistics"], 65536)
        self.assertEqual(randomization["maximum_p_value"], 0.05)
        self.assertFalse(randomization["population_inference_supported"])
        order = rule["required_prediction_freeze_order"]
        self.assertLess(
            order.index(
                "produce_and_hash_model_prior_and_control_predictions_without_final_target_text"
            ),
            order.index("open_all_eligible_final_targets_once"),
        )

    def test_control_gate_is_conjunctive_and_ties_fail(self):
        rule = self.boundary["future_final_only_decision_rule"]
        controls = rule["required_controls"]
        self.assertEqual(
            [row["control_id"] for row in controls],
            [
                "source_train_only_no_signal_sentence_prior",
                "same_checkpoint_zero_candidate_signal",
                "channel_name_hash_derangement",
                "nonwrapping_zero_filled_time_displacement",
            ],
        )
        self.assertTrue(rule["conjunctive_control_gate"])
        self.assertFalse(rule["control_tie_passes"])
        self.assertFalse(rule["failure_allows_restart"])
        self.assertFalse(rule["failure_allows_threshold_change"])
        self.assertFalse(rule["failure_allows_calibration"])
        self.assertFalse(rule["failure_allows_automatic_backup"])
        self.assertFalse(rule["all_gates_pass_authorizes_next_loop_execution"])

    def test_identity_text_and_population_claims_cannot_collapse(self):
        boundary = self.boundary["identity_and_text_claim_boundary"]
        self.assertTrue(boundary["unseen_canonical_person_candidate"])
        self.assertFalse(boundary["unseen_text_currently_verified"])
        self.assertIn("sentence_plaintext", boundary["forbidden_overlap_outputs"])
        self.assertIn("typed_response_plaintext", boundary["forbidden_overlap_outputs"])
        self.assertFalse(
            boundary["overlap_may_change_final_membership_after_preregistered_eligibility"]
        )
        self.assertFalse(boundary["single_person_population_generalization"])

    def test_calibrated_transfer_requires_a_different_physical_design(self):
        calibrated = self.boundary["calibrated_transfer_boundary"]
        self.assertFalse(calibrated["s25_block2_may_be_repurposed_for_calibration"])
        self.assertTrue(calibrated["requires_new_metadata_selection"])
        self.assertTrue(
            calibrated["requires_physically_separate_calibration_and_final_recordings"]
        )
        self.assertTrue(calibrated["requires_nested_predeclared_calibration_budgets"])
        self.assertFalse(calibrated["calibrated_result_may_be_labeled_zero_shot"])
        self.assertEqual(calibrated["future_roadmap_loop"], 32)

    def test_dependencies_keep_experiment_blocked_but_resolve_loop27_rule_research(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop28_planning_research_complete"])
        self.assertFalse(dependencies["loop28_preregistration_prepared"])
        self.assertFalse(dependencies["loop28_authorization_request_prepared"])
        self.assertFalse(dependencies["loop25_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop26_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop27_dependency_satisfied_now"])
        self.assertTrue(
            dependencies["loop27_final_only_decision_rule_research_dependency_satisfied"]
        )
        self.assertTrue(dependencies["loop27_other_preregistration_blockers_remain"])

    def test_resources_and_protected_access_are_zero_or_explicitly_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_workers"], 1)
        self.assertEqual(resources["current_downloaded_payload_bytes"], 0)
        self.assertEqual(resources["current_generated_planning_artifact_cap_bytes"], 8 * 1024**2)
        self.assertIsNone(resources["external_browser_peak_rss_bytes"])
        self.assertIsNone(resources["end_to_end_research_runtime_sec"])
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 32 * 1024**2)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_candidate_parameter_updates"], 0)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 10)
        self.assertEqual(counters["github_metadata_api_operations"], 1)
        protected = {
            key: value
            for key, value in counters.items()
            if key
            not in {
                "high_level_public_web_research_operations",
                "github_metadata_api_operations",
            }
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_and_human_note_cover_v2_and_decision_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        self.assertEqual(len({row["source_id"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        for phrase in (
            "Asynchronous Is Not Yet Causal",
            "Does Not Establish Strict Unseen-Person Zero-Shot",
            "0.05 absolute macro sentence-CER",
            "65,535",
            "S25 block 2 remains T2",
            "does not establish",
        ):
            self.assertIn(phrase, self.research)

    def test_roadmap_keeps_loop28_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 28)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(
            row["research_registry"],
            "registries/loop28_research_boundary.v0.json",
        )
        self.assertFalse(row["preregistration_prepared"])
        self.assertEqual(row["selected_claim_level"], "T2")

    def test_no_loop28_preregistration_request_runtime_or_payload_exists(self):
        forbidden = (
            "docs/LOOP_28_TRANSFER_PREREGISTRATION.md",
            "docs/LOOP_28_AUTHORIZATION_PACKET.md",
            "registries/loop28_transfer_contract.v0.json",
            "registries/loop28_authorization_request.v0.json",
            "selections/loop28_s25_final.json",
            "src/neurodecodekit/experiments/session_person_transfer.py",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))

    def test_public_status_keeps_research_separate_from_execution(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                lowered = contents.lower()
                self.assertIn("loop 28", lowered)
                self.assertIn("planning research", lowered)
                self.assertIn("zero-shot", lowered)
                self.assertIn("not started", lowered)
        combined = "\n".join(self.public_status.values())
        self.assertIn("65,535", combined)
        self.assertIn("0.05", combined)
        self.assertNotIn("Loop 28 is complete", combined)


if __name__ == "__main__":
    unittest.main()
