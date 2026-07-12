import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop31_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_31_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop31ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_all_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop31_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_experiment_blocked_on_loop26",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_cache_target_checkpoint_model_training_or_evaluation",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 19)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_local_claim_below_brain_specific_origin(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L31-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_local_encoder_claim_class"],
            "L31-C2_sensor_signal_dependence",
        )
        self.assertTrue(decision["brain_specific_claim_requires_loop35"])
        self.assertTrue(decision["language_model_extension_is_contingent"])
        self.assertFalse(decision["unreleased_brain2qwerty_v2_embeddings_assumed_available"])
        self.assertFalse(decision["execution_matrix_frozen_now"])
        self.assertFalse(decision["preregistration_prepared_now"])

    def test_dependencies_keep_loop26_and_loop35_roles_distinct(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop31_planning_research_complete"])
        self.assertFalse(dependencies["loop31_preregistration_prepared"])
        self.assertFalse(dependencies["loop31_authorization_request_prepared"])
        self.assertFalse(dependencies["loop31_runtime_or_fixture_exists"])
        self.assertTrue(dependencies["loop26_result_required"])
        self.assertFalse(dependencies["loop26_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop25_underlying_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop35_required_for_brain_specific_claim"])
        self.assertFalse(dependencies["authorized_language_model_system_exists_now"])

    def test_existing_real_comparisons_are_exact_negative_and_consumed(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 6)
        meg = evidence["loop15_s21_cross_session"]
        self.assertEqual(meg["rows"], 63)
        self.assertAlmostEqual(meg["neural_corpus_cer"], 0.917949)
        self.assertAlmostEqual(meg["no_signal_prior_corpus_cer"], 0.775458)
        self.assertEqual(meg["neural_wins_ties_losses"], [3, 2, 58])
        self.assertFalse(meg["neural_advantage"])
        eeg = evidence["loop19_s7_eeg_event_holdout"]
        self.assertEqual(eeg["rows"], 1100)
        self.assertAlmostEqual(eeg["neural_label_accuracy"], 0.009091)
        self.assertAlmostEqual(eeg["no_signal_prior_label_accuracy"], 0.122727)
        self.assertEqual(eeg["neural_wins_ties_losses"], [9, 957, 134])
        self.assertFalse(eeg["neural_advantage"])
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_encoder_matrix_has_ten_unique_conditions_and_exact_roles(self):
        matrix = self.boundary["encoder_condition_matrix"]
        condition_ids = [row["condition_id"] for row in matrix]
        self.assertEqual(len(condition_ids), 10)
        self.assertEqual(len(condition_ids), len(set(condition_ids)))
        self.assertEqual(
            condition_ids,
            [
                "L31-E00_full_signal_encoder",
                "L31-E01_train_only_no_signal_prior",
                "L31-E02_same_checkpoint_zero_signal",
                "L31-E03_same_checkpoint_item_derangement",
                "L31-E04_same_checkpoint_channel_derangement",
                "L31-E05_same_checkpoint_time_displacement",
                "L31-E06_timing_only_baseline",
                "L31-E07_declared_context_only_baseline",
                "L31-E08_train_pairing_derangement",
                "L31-E09_parameter_matched_linear_signal_ctc",
            ],
        )
        unconditional = [
            row["condition_id"]
            for row in matrix
            if row["required_for_sensor_signal_claim"] is True
            and row["condition_id"] != "L31-E00_full_signal_encoder"
        ]
        self.assertEqual(len(unconditional), 7)
        context = matrix[7]
        self.assertIn("if_any_prompt", context["required_for_sensor_signal_claim"])
        linear = matrix[9]
        self.assertFalse(linear["required_for_sensor_signal_claim"])
        self.assertIn("2884", linear["model_relation"])
        self.assertTrue(all(row["execution_status"] == "not_started" for row in matrix))

    def test_language_model_matrix_is_contingent_and_separates_effects(self):
        matrix = self.boundary["language_model_condition_matrix"]
        self.assertIn("unavailable", matrix["status"])
        condition_ids = [row["condition_id"] for row in matrix["conditions"]]
        self.assertEqual(len(condition_ids), 5)
        self.assertEqual(len(condition_ids), len(set(condition_ids)))
        self.assertEqual(
            condition_ids,
            [
                "L31-L00_encoder_ctc_text_only",
                "L31-L01_ctc_text_plus_neurotokens_llm",
                "L31-L02_ctc_text_only_same_llm",
                "L31-L03_ctc_text_plus_item_deranged_neurotokens_same_llm",
                "L31-L04_text_prior_only_same_llm",
            ],
        )
        self.assertEqual(len(matrix["incremental_neurotoken_claim_requires"]), 5)
        self.assertIn(
            "total_neural_contribution_from_neurotoken_drop_alone",
            matrix["cannot_establish"],
        )

    def test_estimands_keep_language_neurotoken_and_neural_origin_separate(self):
        estimands = self.boundary["estimands"]
        self.assertEqual(estimands["encoder_primary"]["positive_direction"], "full_signal_better")
        self.assertEqual(
            estimands["encoder_primary"]["primary_comparator"],
            "L31-E01_train_only_no_signal_prior",
        )
        self.assertFalse(estimands["encoder_primary"]["minimum_practical_margin_frozen_now"])
        self.assertFalse(estimands["language_prior_gain"]["may_be_credited_to_neural_signal"])
        self.assertTrue(
            estimands["incremental_neurotoken_gain"]["claim_is_conditional_on_ctc_text"]
        )
        self.assertFalse(
            estimands["incremental_neurotoken_gain"]["claim_is_total_neural_contribution"]
        )
        self.assertEqual(
            estimands["brain_specific_increment"]["status"], "unavailable_until_loop35"
        )

    def test_timing_context_and_transform_contracts_fail_closed(self):
        timing = self.boundary["timing_and_context_contract"]
        self.assertEqual(len(timing["timing_only_allowlist"]), 4)
        self.assertIn("keypress_identity", timing["timing_only_forbidden"])
        self.assertIn("target_text", timing["timing_only_forbidden"])
        self.assertFalse(timing["closed_candidate_sentence_list_allowed"])
        self.assertFalse(timing["prompt_text_allowed_as_candidate_input"])
        self.assertTrue(timing["context_absence_requires_machine_evidence"])
        self.assertFalse(timing["unavailable_context_control_may_be_reported_as_zero"])
        transforms = self.boundary["transform_freeze_contract"]
        self.assertTrue(transforms["all_transforms_frozen_before_validation_target_open"])
        self.assertTrue(transforms["item_derangement_must_have_no_fixed_points"])
        self.assertFalse(transforms["validation_targets_may_select_transform"])
        self.assertFalse(transforms["transform_search_or_best_of_many_allowed"])
        self.assertTrue(transforms["every_transform_configuration_and_payload_sha256_required"])

    def test_exact_six_item_intersection_union_math_is_machine_checkable(self):
        stats = self.boundary["statistical_decision_recommendation"]
        self.assertEqual(
            stats["status"], "research_recommendation_not_frozen_until_preregistration"
        )
        self.assertEqual(stats["validation_items"], 6)
        self.assertEqual(stats["assignments_with_six_nonzero_pairs"], 2**6)
        self.assertEqual(stats["minimum_one_sided_p_with_six_nonzero_pairs"], 1 / 2**6)
        self.assertEqual(stats["minimum_two_sided_p_with_six_nonzero_pairs"], 2 / 2**6)
        self.assertEqual(stats["assignments_with_five_nonzero_pairs"], 2**5)
        self.assertEqual(stats["minimum_one_sided_p_with_five_nonzero_pairs"], 1 / 2**5)
        self.assertEqual(stats["assignments_with_four_nonzero_pairs"], 2**4)
        self.assertEqual(stats["minimum_one_sided_p_with_four_nonzero_pairs"], 1 / 2**4)
        self.assertEqual(stats["maximum_zero_differences_that_can_still_reach_one_sided_alpha"], 1)
        self.assertEqual(
            stats["overall_claim_test"],
            "intersection_union_all_applicable_required_controls",
        )
        self.assertTrue(stats["overall_claim_requires_every_component_pass"])
        self.assertIn(
            "intersection_union", stats["multiplicity_adjustment_for_the_conjunctive_overall_claim"]
        )
        self.assertFalse(stats["independent_component_claims_allowed"])
        self.assertFalse(stats["control_tie_passes"])
        self.assertEqual(stats["biological_replicates"], 1)
        self.assertFalse(stats["population_inference_supported"])

    def test_claim_taxonomy_has_six_unique_classes_and_loop35_ceiling(self):
        taxonomy = self.boundary["claim_taxonomy"]
        claim_ids = [row["claim_id"] for row in taxonomy]
        self.assertEqual(len(claim_ids), 6)
        self.assertEqual(len(claim_ids), len(set(claim_ids)))
        self.assertTrue(taxonomy[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in taxonomy[1:]))
        brain_specific = next(row for row in taxonomy if row["claim_id"].startswith("L31-C3"))
        self.assertIn("Loop 35", brain_specific["requirements"])
        neurotoken = next(row for row in taxonomy if row["claim_id"].startswith("L31-C4"))
        self.assertIn("drop", neurotoken["requirements"])

    def test_future_access_sequence_is_target_blind_and_one_time(self):
        sequence = self.boundary["future_access_sequence"]
        self.assertEqual(len(sequence), 10)
        self.assertLess(
            sequence.index("produce_every_validation_prediction_target_blind_and_hash_freeze_them"),
            sequence.index(
                "open_all_six_validation_targets_once_and_score_every_condition_in_one_pass"
            ),
        )
        self.assertIn("mark_validation_consumed", sequence[8])
        self.assertIn("without_restart", sequence[9])

    def test_future_requirements_and_refusals_are_exact_and_unique(self):
        gates = self.boundary["future_requirements"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 18)
        self.assertEqual(len({row["requirement_id"] for row in gates}), 18)
        self.assertEqual(
            [row["requirement_id"].split("_", 1)[0] for row in gates],
            [f"L31-G{index:02d}" for index in range(1, 19)],
        )
        self.assertEqual(len(refusals), 24)
        self.assertEqual(len(set(refusals)), 24)
        self.assertEqual(
            [value.split("_", 1)[0] for value in refusals],
            [f"L31-R{index:02d}" for index in range(1, 25)],
        )
        combined = " ".join(refusals)
        for phrase in (
            "target_informed",
            "hidden_prompt",
            "language_gain",
            "brain_specific",
            "resource",
            "clinical",
        ):
            self.assertIn(phrase, combined)

    def test_resources_and_protected_access_are_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_workers"], 1)
        self.assertEqual(resources["current_generated_planning_artifact_cap_bytes"], 8 * 1024**2)
        self.assertEqual(resources["current_downloaded_data_model_or_weight_bytes"], 0)
        self.assertIsNone(resources["external_research_network_bytes"])
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_model_parameter_ceiling"], 2908)
        self.assertEqual(resources["future_total_training_runtime_cap_sec"], 1200)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 32 * 1024**2)
        self.assertEqual(resources["future_new_real_data_download_bytes"], 0)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_network_research_operations"], 16)
        self.assertEqual(counters["public_github_api_requests"], 8)
        protected = {
            key: value
            for key, value in counters.items()
            if key
            not in {
                "high_level_public_network_research_operations",
                "public_github_api_requests",
            }
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_and_human_note_cover_attribution_boundaries(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 14)
        self.assertEqual(len({row["source_id"] for row in sources}), 14)
        self.assertTrue(
            all(
                row["url"].startswith("https://") or row["url"].startswith("docs/")
                for row in sources
            )
        )
        for phrase in (
            "Prediction Is Not Attribution",
            "The Encoder Matrix Needs Ten Named Conditions",
            "Six Rows Make The Gate Exact And Severe",
            "sensor-signal dependence",
            "18 future requirements and 24 refusal IDs",
            "does not prove total neural contribution",
        ):
            self.assertIn(phrase, self.research)

    def test_no_loop31_runtime_preregistration_or_fixture_exists(self):
        forbidden = (
            "docs/LOOP_31_PREREGISTRATION.md",
            "docs/LOOP_31_AUTHORIZATION_PACKET.md",
            "registries/loop31_experiment_contract.v0.json",
            "registries/loop31_authorization_request.v0.json",
            "src/neurodecodekit/experiments/neural_contribution_ablation.py",
            "cache/loop31",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))

    def test_roadmap_keeps_loop31_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 31)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["research_registry"], "registries/loop31_research_boundary.v0.json")
        self.assertEqual(row["encoder_condition_count"], 10)
        self.assertEqual(row["language_model_condition_count"], 5)
        self.assertEqual(row["future_requirement_count"], 18)
        self.assertEqual(row["future_refusal_count"], 24)
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["authorization_request_prepared"])
        self.assertFalse(row["brain_specific_claim_available"])

    def test_public_status_keeps_research_separate_from_execution(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                lowered = contents.lower()
                self.assertIn("loop 31", lowered)
                self.assertIn("planning research", lowered)
                self.assertIn("not started", lowered)
                self.assertIn("sensor-signal", lowered)
        combined = "\n".join(self.public_status.values())
        self.assertIn("10-condition", combined)
        self.assertIn("5-condition", combined)
        self.assertIn("Loop 35", combined)
        self.assertNotIn("Loop 31 is complete", combined)


if __name__ == "__main__":
    unittest.main()
