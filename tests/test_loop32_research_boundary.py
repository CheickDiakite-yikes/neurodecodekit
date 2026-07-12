import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop32_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_32_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop32ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_all_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop32_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_experiment_blocked_on_dependencies_and_fresh_person_protocol",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_candidate_participant_cache_signal_target_checkpoint_adapter_training_or_evaluation",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 22)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_keeps_candidate_mode_and_experiment_unselected(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L32-C0_no_new_result")
        self.assertEqual(decision["recommended_target_trainable_parameter_count"], 32)
        self.assertFalse(decision["adapter_family_frozen_now"])
        self.assertIsNone(decision["calibration_mode_selected_now"])
        self.assertIsNone(decision["fresh_person_candidate_selected_now"])
        self.assertFalse(decision["preregistration_prepared_now"])
        self.assertFalse(decision["authorization_request_prepared_now"])
        self.assertFalse(decision["s25_session2_block2_eligible_for_loop32"])

    def test_dependencies_do_not_turn_research_packets_into_execution_results(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop32_planning_research_complete"])
        self.assertTrue(dependencies["loop25_compatible_result_required"])
        self.assertFalse(dependencies["loop25_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop26_frozen_source_model_result_required"])
        self.assertFalse(dependencies["loop26_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop28_transfer_taxonomy_research_satisfied"])
        self.assertFalse(dependencies["loop31_dependency_satisfied_now"])
        self.assertFalse(dependencies["approved_fresh_person_protocol_exists_now"])
        self.assertFalse(dependencies["physically_separated_candidate_exists_now"])
        self.assertFalse(dependencies["loop32_runtime_or_fixture_exists"])

    def test_evidence_inventory_preserves_negative_synthetic_and_planning_boundaries(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 5)
        self.assertIn(
            "worse than the no-signal prior",
            evidence["loop15_s21_same_subject_cross_session"]["finding"],
        )
        self.assertIn(
            "harmed channel-mixing", evidence["loop16_synthetic_calibration_curve"]["finding"]
        )
        self.assertFalse(
            evidence["loop16_synthetic_calibration_curve"]["eligible_for_human_calibration_claim"]
        )
        self.assertFalse(
            evidence["brain2qwerty_v2_leave_one_out_finetune"][
                "local_dataset_or_embedding_available"
            ]
        )
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_four_modes_keep_zero_shot_unlabeled_label_light_and_supervised_distinct(self):
        modes = self.boundary["calibration_mode_taxonomy"]
        mode_ids = [row["mode_id"] for row in modes]
        self.assertEqual(
            mode_ids,
            [
                "L32-M0_strict_zero_shot",
                "L32-M1_unlabeled_transductive_calibration",
                "L32-M2_label_light_calibration",
                "L32-M3_supervised_calibration",
            ],
        )
        self.assertFalse(modes[0]["target_calibration_signal_before_final_prediction"])
        self.assertEqual(modes[0]["target_parameter_updates"], 0)
        self.assertEqual(modes[1]["target_labels_before_final_target_open"], 0)
        self.assertIn("target-label-free", modes[1]["selection_rule"])
        self.assertEqual(modes[2]["maximum_labeled_calibration_sentences"], 8)
        self.assertEqual(modes[3]["maximum_labeled_calibration_sentences"], 32)
        self.assertTrue(all("not_zero_shot" in row["allowed_claim"] for row in modes[1:]))

    def test_adapter_is_exactly_32_target_parameters_and_remains_causal_pointwise(self):
        adapter = self.boundary["adapter_family_recommendation"]
        self.assertIn("not_frozen_or_authorized", adapter["status"])
        self.assertEqual(adapter["base_model_parameter_count"], 2908)
        self.assertEqual(adapter["hidden_width"], 16)
        self.assertEqual(adapter["scale_parameter_count"], 16)
        self.assertEqual(adapter["bias_parameter_count"], 16)
        self.assertEqual(adapter["target_trainable_parameter_count"], 32)
        self.assertEqual(adapter["total_parameter_count_with_adapter"], 2940)
        self.assertEqual(adapter["identity_initialization"], {"scale": 1.0, "bias": 0.0})
        self.assertTrue(adapter["causal"])
        self.assertEqual(adapter["extra_right_context_samples"], 0)
        self.assertEqual(adapter["extra_history_samples"], 0)
        self.assertEqual(len(adapter["forbidden"]), 6)
        for term in ["channel rotation", "missing channels", "nonstationary drift"]:
            self.assertIn(term, adapter["known_failure_boundary"])

    def test_budget_schedule_is_nested_and_does_not_invent_human_minutes(self):
        schedule = self.boundary["calibration_budget_schedule"]
        self.assertEqual(schedule["nested_budget_counts"], [0, 2, 4, 8, 16, 32])
        self.assertEqual(schedule["label_light_allowed_counts"], [2, 4, 8])
        self.assertEqual(schedule["supervised_allowed_counts"], [2, 4, 8, 16, 32])
        self.assertTrue(schedule["unlabeled_budget_must_be_fixed_without_target_labels"])
        self.assertTrue(schedule["repeated_attempts_count_as_additional_human_burden"])
        self.assertFalse(schedule["synthetic_seconds_may_be_translated_to_human_minutes"])
        self.assertIsNone(schedule["maximum_real_calibration_minutes"])

    def test_physical_partition_contract_keeps_fit_selection_and_final_disjoint(self):
        contract = self.boundary["fresh_person_partition_contract"]
        self.assertEqual(
            contract["calibration_partition"]["minimum_unique_completed_sentences_for_full_curve"],
            32,
        )
        self.assertEqual(contract["selection_partition"]["minimum_unique_completed_sentences"], 16)
        self.assertEqual(contract["final_partition"]["minimum_unique_completed_sentences"], 48)
        self.assertFalse(contract["final_partition"]["may_fit_or_select_any_value"])
        self.assertEqual(contract["final_partition"]["target_open_count"], 1)
        self.assertTrue(contract["all_three_partition_ids_must_be_distinct"])
        self.assertTrue(contract["semantic_text_hash_groups_must_be_disjoint"])
        self.assertTrue(contract["performed_row_ids_must_be_disjoint"])
        self.assertFalse(contract["normalization_statistics_may_cross_partitions"])
        self.assertFalse(contract["s25_session2_block2_may_be_repurposed"])

    def test_condition_matrix_has_exact_controls_and_mode_applicability(self):
        conditions = self.boundary["future_condition_matrix"]
        ids = [row["condition_id"] for row in conditions]
        self.assertEqual(len(ids), 6)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            ids,
            [
                "L32-A00_frozen_strict_zero_shot",
                "L32-A01_identity_adapter",
                "L32-A02_selected_mode_adapter",
                "L32-A03_source_train_only_no_signal_prior",
                "L32-A04_unlabeled_robust_normalization_only",
                "L32-A05_calibration_label_derangement",
            ],
        )
        self.assertTrue(conditions[1]["must_match_zero_shot_predictions_exactly"])
        self.assertEqual(
            conditions[5]["required_modes"],
            ["L32-M2_label_light_calibration", "L32-M3_supervised_calibration"],
        )
        self.assertTrue(conditions[5]["same_32_parameters_budget_optimizer_and_updates_required"])

    def test_access_order_freezes_zero_shot_before_calibration_and_targets_last(self):
        order = self.boundary["access_and_freeze_order"]
        self.assertEqual(len(order), 11)
        zero_shot_index = next(i for i, step in enumerate(order) if "zero_shot" in step)
        calibration_index = next(
            i for i, step in enumerate(order) if "open_only_the_authorized_calibration" in step
        )
        target_index = next(i for i, step in enumerate(order) if "open_final_targets_once" in step)
        self.assertLess(zero_shot_index, calibration_index)
        self.assertLess(calibration_index, target_index)
        self.assertIn("without_restart", order[-1])

    def test_statistical_recommendation_is_conjunctive_and_one_person_only(self):
        stats = self.boundary["statistical_decision_recommendation"]
        self.assertIn("not_frozen", stats["status"])
        self.assertEqual(stats["minimum_final_unique_sentences"], 48)
        self.assertEqual(stats["random_sign_assignments"], 65535)
        self.assertEqual(stats["reference_statistics_total"], 65536)
        self.assertEqual(stats["one_sided_alpha"], 0.05)
        self.assertEqual(
            stats["minimum_practical_macro_cer_gain_vs_zero_shot_recommendation"], 0.05
        )
        self.assertEqual(stats["minimum_practical_macro_cer_gain_vs_prior_recommendation"], 0.05)
        self.assertFalse(stats["practical_margins_frozen_now"])
        self.assertIn("intersection_union", stats["overall_decision"])
        self.assertFalse(stats["control_tie_passes"])
        self.assertFalse(stats["selection_improvement_can_override_final_harm"])
        self.assertFalse(stats["population_inference_supported"])

    def test_human_burden_claims_gates_and_refusals_are_exact(self):
        burden = self.boundary["human_burden_ledger"]
        self.assertEqual(len(burden), 12)
        self.assertIn("label_verification_and_correction_minutes", burden)
        self.assertIn("selection_sentences_and_labels_exposed", burden)
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(claims), 7)
        self.assertEqual(claims[0]["claim_id"], "L32-C0_no_new_result")
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        gates = self.boundary["future_promotion_requirements"]
        self.assertEqual(len(gates), 20)
        self.assertEqual(
            [row["requirement_id"] for row in gates], [f"L32-G{i:02d}" for i in range(1, 21)]
        )
        refusals = self.boundary["refusal_matrix"]
        self.assertEqual(len(refusals), 26)
        self.assertEqual(len(refusals), len(set(refusals)))
        self.assertTrue(all(value.startswith("L32-R") for value in refusals))

    def test_resources_and_protected_operations_remain_bounded_and_zero(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_research_cpu_threads"], 1)
        self.assertEqual(resources["current_research_workers"], 1)
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_target_trainable_parameter_ceiling"], 32)
        self.assertEqual(resources["future_total_parameter_count_ceiling"], 2940)
        self.assertEqual(resources["future_total_adapter_fit_runtime_cap_sec"], 1200)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1_073_741_824)
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 33_554_432)
        self.assertEqual(
            resources["future_new_data_or_model_download_bytes_before_separate_authorization"], 0
        )
        self.assertFalse(resources["storage_envelope_is_data_access_or_execution_authorization"])
        ledger = self.boundary["protected_operation_ledger"]
        self.assertEqual(ledger["public_network_operations_total"], 6)
        for key, value in ledger.items():
            if key.endswith(
                ("reads", "runs", "updates", "evaluations", "operations")
            ) and not key.startswith("public_"):
                self.assertEqual(value, 0, key)
        self.assertEqual(ledger["protected_dataset_or_model_download_bytes"], 0)
        self.assertEqual(len(ledger["unavailable_fields"]), 4)

    def test_sources_are_primary_local_or_pinned_and_claim_boundary_is_explicit(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 9)
        source_ids = {row["source_id"] for row in sources}
        self.assertEqual(len(source_ids), len(sources))
        self.assertTrue(
            {
                "brain2qwerty_v2_paper",
                "brain2qwerty_v2_code_pinned",
                "coral_domain_adaptation",
                "euclidean_alignment",
                "long_term_bci_calibration_reduction",
                "loop16_local_synthetic_curve",
                "loop28_local_transfer_taxonomy",
                "loop31_local_attribution_firewall",
            }.issubset(source_ids)
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 5)
        claim_text = " ".join(self.boundary["claim_boundary"])
        for term in ["not a preregistration", "No protected participant data", "No zero-shot"]:
            self.assertIn(term, claim_text)

    def test_human_research_note_contains_exact_proof_and_scientific_boundaries(self):
        for text in [
            "experiment Not Started",
            "32-parameter",
            "0, 2, 4, 8, 16, 32",
            "32 calibration, 16 selection, and 48 final",
            "65,535",
            "1,200 seconds",
            "Engineering capability added:",
            "Scientific claim not established:",
        ]:
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.11.0")
        boundary = self.roadmap["current_boundary"]
        self.assertTrue(boundary["loop32_research_packet_prepared"])
        self.assertEqual(boundary["loop32_calibration_mode_count"], 4)
        self.assertEqual(boundary["loop32_budget_counts"], [0, 2, 4, 8, 16, 32])
        self.assertEqual(boundary["loop32_target_trainable_parameter_ceiling"], 32)
        self.assertEqual(boundary["loop32_future_requirement_count"], 20)
        self.assertEqual(boundary["loop32_future_refusal_count"], 26)
        self.assertFalse(boundary["loop32_candidate_selected"])
        self.assertFalse(boundary["loop32_preregistration_prepared"])
        self.assertFalse(boundary["loop32_execution_authorized"])
        loop32 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 32)
        self.assertEqual(loop32["research_status"], "planning_research_complete")
        self.assertEqual(loop32["research_packet"], "docs/LOOP_32_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(loop32["research_registry"], "registries/loop32_research_boundary.v0.json")
        self.assertEqual(loop32["calibration_mode_count"], 4)
        self.assertEqual(loop32["future_requirement_count"], 20)
        self.assertEqual(loop32["future_refusal_count"], 26)
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 32", content)
                self.assertIn("planning research", content.lower())
                self.assertIn("Not Started", content)
                self.assertTrue("32-parameter" in content or "32 parameter" in content)
                self.assertIn("unauthorized", content.lower())


if __name__ == "__main__":
    unittest.main()
