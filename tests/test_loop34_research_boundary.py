import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop34_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_34_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop34ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop34_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_experiment_blocked_on_loop30_loop31_and_fresh_confidence_partitions",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_protected_cache_signal_target_checkpoint_model_confidence_fit_validation_or_product_claim",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 26)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_keeps_confidence_unavailable_and_semantics_separate(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L34-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_synthetic_claim_class"],
            "L34-C5_bounded_synthetic_selective_risk_control",
        )
        self.assertFalse(
            decision["real_confidence_claim_available_from_existing_six_validation_rows"]
        )
        self.assertTrue(
            decision["fresh_physically_separate_confidence_partitions_required_for_real_claim"]
        )
        self.assertFalse(decision["stability_is_confidence"])
        self.assertFalse(decision["ranking_score_is_probability"])
        self.assertEqual(decision["confidence_exposure_default"], "unavailable")

    def test_dependencies_preserve_shared_validation_and_consumed_evidence(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop30_planning_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop31_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop30_execution_result_available_now"])
        self.assertFalse(dependencies["loop31_execution_result_available_now"])
        self.assertTrue(
            dependencies["loop26_loop31_loop33_shared_source_validation_event_reserved"]
        )
        self.assertFalse(
            dependencies["source_validation_rows_available_for_loop34_confidence_fitting"]
        )
        self.assertFalse(
            dependencies["source_validation_rows_available_for_independent_loop34_qualification"]
        )
        self.assertTrue(dependencies["source_test_and_session2_consumed_and_frozen"])
        self.assertFalse(
            dependencies["fresh_synthetic_calibration_selection_and_final_partitions_exist_now"]
        )

    def test_existing_evidence_is_negative_planning_only_or_exact_design_math(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 6)
        self.assertIn("55 train, 6 reserved validation", evidence["loop14_source_split"]["finding"])
        self.assertIn(
            "worse than their no-signal", evidence["loop15_and_loop19_negative_results"]["finding"]
        )
        self.assertIn(
            "stabilize and still be wrong", evidence["loop23_stability_result"]["finding"]
        )
        self.assertIn("0.393", evidence["six_row_zero_error_bound"]["finding"])
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_confidence_ladder_has_seven_noninterchangeable_levels(self):
        semantics = self.boundary["confidence_semantics"]
        self.assertEqual(len(semantics), 7)
        self.assertEqual(
            [row["level_id"].split("_", 1)[0] for row in semantics],
            [f"L34-S{i}" for i in range(7)],
        )
        self.assertTrue(semantics[2]["probability_semantics"])
        self.assertTrue(all(row["probability_semantics"] is False for row in semantics[:2]))
        self.assertTrue(all(row["probability_semantics"] is False for row in semantics[3:6]))
        self.assertIsNone(semantics[6]["probability_semantics"])

    def test_partition_recommendation_is_fresh_disjoint_and_three_way(self):
        partition = self.boundary["partition_recommendation"]
        self.assertEqual(partition["calibration_sequence_count"], 128)
        self.assertEqual(partition["selection_sequence_count"], 64)
        self.assertEqual(partition["final_sequence_count"], 256)
        self.assertEqual(partition["total_sequence_count"], 448)
        self.assertFalse(partition["counts_frozen_now"])
        self.assertIsNone(partition["exact_seed_value"])
        self.assertTrue(partition["group_membership_must_be_disjoint"])
        self.assertFalse(partition["final_targets_may_fit_scale_threshold_bins_or_policy"])
        self.assertFalse(partition["synthetic_rows_are_biological_replication"])
        self.assertFalse(partition["synthetic_pass_implies_real_confidence"])

    def test_candidate_matrix_has_controls_and_non_deployable_oracle(self):
        matrix = self.boundary["candidate_score_matrix"]
        self.assertEqual(len(matrix), 8)
        ids = [row["candidate_id"] for row in matrix]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(row["probability_without_calibration"] is False for row in matrix))
        self.assertIn("prior", matrix[4]["candidate_id"])
        self.assertIn("random", matrix[5]["candidate_id"])
        self.assertIn("always_predict", matrix[6]["candidate_id"])
        self.assertFalse(matrix[7]["target_blind_at_inference"])
        self.assertFalse(matrix[7]["eligible_for_selection_or_deployment"])

    def test_target_firewall_forbids_real_consumed_final_and_oracle_leakage(self):
        firewall = self.boundary["target_and_leakage_firewall"]
        self.assertFalse(
            firewall["synthetic_generation_may_use_real_target_text_labels_prompts_or_predictions"]
        )
        self.assertFalse(
            firewall["score_generation_may_use_current_item_target_correctness_cer_or_wer"]
        )
        self.assertFalse(
            firewall[
                "final_targets_may_change_candidate_mapping_threshold_coverage_bin_or_latency_rule"
            ]
        )
        self.assertTrue(firewall["oracle_ranking_may_be_reported_only_after_final_scoring"])
        self.assertFalse(firewall["oracle_ranking_may_be_presented_as_deployable"])
        self.assertFalse(
            firewall[
                "consumed_source_test_session2_s7_or_loop23_payload_may_seed_or_tune_confidence"
            ]
        )

    def test_metrics_use_bounded_primary_loss_and_do_not_overclaim_ece_or_aurc(self):
        metrics = self.boundary["metric_and_loss_recommendation"]
        self.assertEqual(metrics["primary_bounded_loss"], "exact_sequence_error_0_or_1")
        self.assertEqual(metrics["secondary_raw_loss"], "raw_character_error_rate_unclipped")
        self.assertIn("min_raw_CER_1", metrics["optional_bounded_cer_loss"])
        self.assertFalse(metrics["raw_cer_may_be_silently_clipped"])
        self.assertEqual(metrics["recommended_coverage_grid"], [1.0, 0.9, 0.8, 0.6])
        self.assertEqual(metrics["recommended_primary_coverage"], 0.8)
        self.assertEqual(metrics["recommended_minimum_coverage"], 0.5)
        self.assertIn(
            "AUGRC_or_equivalent_generalized_risk_area", metrics["multi_threshold_metrics"]
        )
        self.assertFalse(metrics["ece_available_for_raw_ranking_scores"])
        self.assertFalse(metrics["abstain_all_passes"])

    def test_six_row_and_conformal_boundary_is_exact_and_conservative(self):
        boundary = self.boundary["small_sample_and_conformal_boundary"]
        self.assertEqual(boundary["existing_real_sequence_count"], 6)
        self.assertAlmostEqual(
            boundary["zero_observed_error_exact_upper_bound"], 0.39303776899708276
        )
        self.assertFalse(boundary["existing_rows_independent_exchangeable_evidence"])
        self.assertFalse(boundary["existing_rows_can_certify_useful_error_risk"])
        self.assertTrue(boundary["conformal_loss_must_be_bounded"])
        self.assertTrue(
            boundary[
                "conformal_guarantee_requires_registered_exchangeability_or_weighted_group_protocol"
            ]
        )
        self.assertFalse(boundary["conformal_result_may_be_transferred_from_synthetic_to_real"])
        self.assertFalse(boundary["population_person_or_device_inference_supported"])

    def test_revision_contract_separates_stability_and_reports_added_delay(self):
        revision = self.boundary["revision_and_latency_boundary"]
        self.assertFalse(revision["stability_is_correctness"])
        self.assertTrue(revision["stable_prefix_may_still_be_wrong"])
        self.assertTrue(revision["revision_policy_must_freeze_before_final_targets"])
        self.assertTrue(revision["report_revision_count"])
        self.assertTrue(revision["report_abstention_or_delay_added_latency"])
        self.assertTrue(revision["clock_domains_must_follow_loop30"])
        self.assertFalse(revision["end_to_end_latency_measured_now"])
        self.assertFalse(revision["real_time_claim_available_now"])

    def test_access_sequence_freezes_before_one_final_open(self):
        sequence = self.boundary["future_access_sequence"]
        self.assertEqual(len(sequence), 10)
        self.assertLess(
            sequence.index(
                "freeze_all_code_config_feature_mapping_threshold_policy_prediction_and_access hashes before final targets"
            ),
            sequence.index(
                "open_final_targets_once and score every frozen condition without restart"
            ),
        )
        self.assertIn("calibration only", sequence[5])
        self.assertIn("selection only", sequence[6])
        self.assertIn("without restart", sequence[9])

    def test_outcome_and_claim_taxonomies_are_exact_and_fail_closed(self):
        outcomes = self.boundary["outcome_taxonomy"]
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(outcomes), 8)
        self.assertEqual(
            [row["outcome_id"].split("_", 1)[0] for row in outcomes],
            [f"L34-O{i}" for i in range(8)],
        )
        self.assertEqual(len(claims), 7)
        self.assertEqual(
            [row["claim_id"].split("_", 1)[0] for row in claims],
            [f"L34-C{i}" for i in range(7)],
        )
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        self.assertIn("synthetic", outcomes[-1]["meaning"])
        self.assertIn("physically separate real", claims[-1]["boundary"])

    def test_future_gates_and_refusals_are_exact_unique_and_comprehensive(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 20)
        self.assertEqual(len({row["requirement_id"] for row in gates}), 20)
        self.assertEqual(
            [row["requirement_id"].split("_", 1)[0] for row in gates],
            [f"L34-G{i:02d}" for i in range(1, 21)],
        )
        self.assertEqual(len(refusals), 30)
        self.assertEqual(len(set(refusals)), 30)
        self.assertEqual(
            [value.split("_", 1)[0] for value in refusals],
            [f"L34-R{i:02d}" for i in range(1, 31)],
        )
        combined = " ".join(refusals)
        for phrase in (
            "target",
            "probability",
            "stability",
            "oracle",
            "AURC",
            "ECE",
            "conformal",
            "six_real_rows",
            "synthetic",
            "clinical",
        ):
            self.assertIn(phrase, combined)

    def test_resources_and_protected_access_are_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_model_training_runs"], 0)
        self.assertEqual(resources["future_parameter_updates_for_decoder"], 0)
        self.assertEqual(resources["future_confidence_mapping_fits_ceiling"], 6)
        self.assertEqual(resources["future_total_runtime_cap_sec"], 120)
        self.assertEqual(resources["future_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 16 * 1024**2)
        self.assertEqual(
            resources["future_new_data_or_model_download_bytes_before_separate_authorization"], 0
        )
        self.assertFalse(resources["future_direct_energy_measurement_available"])
        self.assertFalse(resources["cpu_time_may_be_reported_as_energy"])
        self.assertFalse(
            resources["storage_envelope_is_data_access_model_target_or_execution_authorization"]
        )
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 5)
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
                "selective_classification_deep_networks",
                "conformal_risk_control",
                "conformal_beyond_exchangeability",
                "modern_neural_network_calibration",
                "measuring_calibration",
                "generalized_risk_coverage",
            }.issubset(source_ids)
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        claim_text = " ".join(self.boundary["claim_boundary"])
        for term in (
            "not a preregistration",
            "No protected cache",
            "not a correctness probability",
            "existing six source-validation sentences",
            "No real confidence",
        ):
            self.assertIn(term, claim_text)
        for text in (
            "experiment Not Started",
            "confidence unavailable",
            "0.39303776899708276",
            "128",
            "64",
            "256",
            "AUGRC",
            "16 MiB",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.20.0")
        boundary = self.roadmap["current_boundary"]
        self.assertTrue(boundary["loop34_research_packet_prepared"])
        self.assertEqual(boundary["loop34_confidence_semantics_count"], 7)
        self.assertEqual(boundary["loop34_candidate_score_count"], 8)
        self.assertEqual(boundary["loop34_recommended_partition_counts"], [128, 64, 256])
        self.assertEqual(boundary["loop34_future_requirement_count"], 20)
        self.assertEqual(boundary["loop34_future_refusal_count"], 30)
        self.assertFalse(boundary["loop34_existing_real_confidence_partition_available"])
        self.assertFalse(boundary["loop34_preregistration_prepared"])
        self.assertFalse(boundary["loop34_execution_authorized"])
        loop34 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 34)
        self.assertEqual(loop34["research_status"], "planning_research_complete")
        self.assertEqual(loop34["research_packet"], "docs/LOOP_34_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(loop34["research_registry"], "registries/loop34_research_boundary.v0.json")
        self.assertEqual(loop34["recommended_partition_counts"], [128, 64, 256])
        self.assertEqual(loop34["future_requirement_count"], 20)
        self.assertEqual(loop34["future_refusal_count"], 30)
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 34", content)
                self.assertIn("planning research", content.lower())
                self.assertIn("Not Started", content)
                self.assertIn("confidence", content.lower())
                self.assertIn("unavailable", content.lower())
                self.assertIn("unauthorized", content.lower())


if __name__ == "__main__":
    unittest.main()
