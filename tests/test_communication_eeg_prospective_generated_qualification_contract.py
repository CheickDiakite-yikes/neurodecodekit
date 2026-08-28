from __future__ import annotations

import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_qualification_contract.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_PREREGISTRATION.md"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"
PARENT = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_synchronized_cohort_contract.v0.json"
)

EXPECTED_REFUSAL_FAMILIES = [
    "recursive_target_label_reference_key_leakage",
    "free_choice_target_before_precommit",
    "target_vault_key_capability_escape",
    "target_exposed_to_decoder_operator_freezer_or_language_context",
    "prediction_visible_before_target_precommit",
    "pre_freeze_target_delivery",
    "post_target_update_rerun_or_model_substitution",
    "future_sample_or_right_context_use",
    "noncausal_filter_or_centered_window",
    "trial_or_block_boundary_oracle_use",
    "source_endpointer_bypass",
    "state_bridge_across_gap_reconnect_session_or_participant",
    "offline_incremental_partition_mismatch",
    "post_washout_context_limit_breach",
    "modality_or_device_identity_drift",
    "channel_count_name_or_order_drift",
    "EEG_geometry_missing_or_changed",
    "EOG_role_inventory_mismatch",
    "oral_EMG_role_or_laterality_mismatch",
    "microphone_trigger_or_photodiode_binding_missing",
    "required_control_condition_missing_duplicated_or_substituted",
    "participant_identity_collision",
    "discovery_replication_identity_overlap",
    "held_out_participant_fit_threshold_or_adaptation",
    "performance_based_exclusion_reassignment_or_substitution",
    "cohort_cardinality_or_replacement_rule_violation",
    "pooled_result_or_other_cohort_rescues_failed_cohort",
    "calibration_source_method_or_row_violation",
    "source_sample_overlap_reorder_or_hidden_gap",
    "source_timestamp_nonfinite_regression_or_clock_reset",
    "correction_ledger_tamper",
    "cross_clock_mapping_missing_or_unverified",
    "LSL_clock_uncertainty_cap_breach",
    "hardware_residual_cap_breach",
    "capture_arrival_processing_commit_presentation_order_violation",
    "raw_payload_cap_breach",
    "private_derivative_cap_breach",
    "temporary_output_cap_breach",
    "public_output_cap_breach",
    "total_permission_or_free_space_floor_breach",
    "forbidden_raw_backup_or_full_float32_copy",
    "filesystem_capability_publication_or_cleanup_escape",
    "full_band_voice_in_shareable_BIDS_root",
    "identity_consent_or_date_mapping_in_BIDS_root",
    "individual_neural_audio_or_target_hash_publication",
    "private_path_or_secret_in_public_artifact",
    "protected_audio_root_not_encrypted_or_separated",
    "release_without_consent_privacy_or_Tier_C_binding",
    "target_vault_ciphertext_timing_path_or_metadata_side_channel",
    "protocol_model_threshold_vocabulary_prior_or_code_hash_drift",
    "prediction_inventory_missing_or_duplicate",
    "prediction_probability_nonfinite_or_sum_mismatch",
    "prediction_row_or_probability_tamper_after_freeze",
    "replication_freeze_before_discovery_delivery_missing",
    "replication_prediction_freeze_not_green_before_delivery",
    "nondeterministic_fixture_prediction_or_freeze_replay",
    "scorer_prediction_target_row_mismatch",
    "scorer_fit_update_transform_or_model_capability",
    "score_before_exact_green_freeze",
    "repeated_score_or_target_delivery",
    "individual_protected_output_in_aggregate_score",
    "missing_invalid_or_nonfinite_prediction_dropped",
    "post_score_mutation_repeat_or_output_replacement",
    "live_required_metric_missing",
    "stable_commit_or_per_command_coverage_below_minimum",
    "false_commit_or_chatter_rate_above_maximum",
    "dropped_invalid_or_deadline_gate_failure",
    "stable_commit_latency_median_or_p95_above_maximum",
    "capture_to_presentation_overhead_or_clock_map_failure",
    "live_update_or_accuracy_only_claim_upgrade",
]


class CommunicationEEGProspectiveGeneratedQualificationContractTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.parent = json.loads(PARENT.read_text(encoding="utf-8"))

    def test_parent_proofs_and_order_are_exact(self) -> None:
        parents = self.contract["parents"]
        self.assertEqual(
            parents["green_registration_commit"],
            "df3266ed09132017cc8a9dcc10e8a7d61ea92f61",
        )
        self.assertEqual(
            parents["proof_and_amendment_commit"],
            "478d31ed8908e29439db215f3aed01a3bcbc16fc",
        )
        self.assertEqual(parents["proof_and_amendment_CI_run_id"], 33_135_742_217)
        self.assertEqual(
            parents["authoritative_stable_commit_coverage_fraction_minimum"],
            0.70,
        )
        order = self.contract["proof_order"]
        self.assertTrue(
            order[
                "generated_implementation_may_begin_after_this_registration_is_remotely_green"
            ]
        )
        self.assertEqual(order["official_qualification_invocations_maximum"], 1)
        self.assertFalse(order["rerun_repair_overwrite_or_substitution_allowed"])

    def test_fictional_cohorts_and_full_trial_grammar_are_exact(self) -> None:
        cohorts = self.contract["fictional_cohorts"]
        self.assertEqual(cohorts["complete_participants_total"], 42)
        self.assertEqual(cohorts["enrolled_participants_total"], 44)
        self.assertTrue(cohorts["participant_identities_disjoint"])
        grammar = self.contract["trial_grammar"]
        roles = (
            grammar["prompted_intend_rows"],
            grammar["prompted_no_intent_rows"],
            grammar["free_choice_intend_rows"],
            grammar["free_choice_no_intent_rows"],
            grammar["rest_rows"],
            grammar["peripheral_calibration_rows"],
        )
        self.assertEqual(sum(roles), 256)
        self.assertEqual(grammar["complete_structural_rows_per_replay"], 42 * 256)
        self.assertEqual(grammar["free_choice_target_precommits_per_replay"], 42 * 96)
        self.assertTrue(grammar["confirmatory_replication_endpoint_uses_shadow_only"])
        self.assertFalse(grammar["shadow_and_live_may_rescue_each_other"])
        timing = grammar["timing_schedule"]
        washout = timing["free_choice_washout_seconds_counts"]
        self.assertEqual(sum(washout.values()), 96)
        washout_seconds = sum(int(seconds) * count for seconds, count in washout.items())
        total = (
            washout_seconds
            + 96 * timing["free_choice_post_washout_intention_and_ITI_seconds"]
            + 96 * timing["prompted_row_seconds"]
            + 32 * timing["rest_row_seconds"]
            + 32 * timing["peripheral_calibration_row_seconds"]
            + timing["fixed_sync_warmup_and_segment_padding_seconds"]
        )
        self.assertEqual(total, timing["total_session_seconds"])

    def test_target_firewall_blocks_context_and_side_channels(self) -> None:
        firewall = self.contract["target_firewall"]
        self.assertTrue(firewall["fixed_size_authenticated_generated_record_required"])
        self.assertLess(
            firewall["maximum_signal_context_seconds"],
            firewall["minimum_washout_seconds"],
        )
        self.assertFalse(firewall["pre_washout_signal_or_state_allowed"])
        self.assertFalse(firewall["trial_or_block_identity_allowed"])
        self.assertTrue(
            firewall[
                "complete_replication_artifact_set_freeze_before_replication_enrollment_or_access"
            ]
        )
        self.assertFalse(firewall["post_target_update_rerun_or_substitution_allowed"])
        self.assertEqual(len(self.contract["replication_artifact_freeze_fields"]), 13)

    def test_all_73_roles_are_synchronized_without_dense_materialization(self) -> None:
        adapter = self.contract["synchronized_sensor_adapter"]
        shards = adapter["source_chunk_shards"]
        self.assertEqual(sum(row["channel_count"] for row in shards), 73)
        self.assertEqual([row["channel_count"] for row in shards], [32, 32, 9])
        self.assertEqual(adapter["segments_per_participant"], 14)
        self.assertEqual(
            adapter["full_segments"] * adapter["full_segment_seconds"]
            + adapter["final_segment_seconds"],
            1650,
        )
        self.assertFalse(adapter["active_trial_may_cross_segment_boundary"])
        self.assertFalse(adapter["dense_full_recording_materialization_allowed"])
        self.assertFalse(adapter["full_float32_backup_allowed"])
        bundle = adapter["atomic_bundle"]
        self.assertEqual(bundle["integer_sample_axis_skew_maximum_samples"], 0)
        self.assertEqual(bundle["hardware_residual_p99_samples_maximum"], 2)
        self.assertEqual(len(bundle["join_order"]), 5)
        self.assertTrue(
            bundle[
                "cross_shard_generation_segment_axis_ledger_geometry_or_clock_mismatch_refuses"
            ]
        )
        self.assertTrue(set(adapter["central_EEG_roles"]).isdisjoint(adapter["posterior_EEG_roles"]))

    def test_conditions_schedule_and_shortcut_fixtures_are_complete(self) -> None:
        self.assertEqual(self.contract["conditions"], self.parent["required_conditions"])
        schedule = self.contract["numerical_schedule_per_replay"]
        self.assertEqual(schedule["prediction_sets"], 42 * 17 * 2)
        self.assertEqual(schedule["prediction_rows"], 42 * 17 * 128)
        self.assertEqual(len(schedule["shortcut_fixtures"]), 7)
        self.assertFalse(
            schedule[
                "same_row_held_out_replication_shadow_live_or_post_target_calibration_allowed"
            ]
        )
        self.assertEqual(schedule["classifier_fits"], 42 * 15)
        self.assertEqual(schedule["temperature_calibration_fits"], 42 * 15)
        self.assertEqual(schedule["sign_flip_assignments_evaluated"], 2 * 2**21)
        self.assertTrue(schedule["prediction_rows_streamed"])
        self.assertFalse(schedule["model_fitting_during_adversarial_mutations_allowed"])

    def test_participant_first_scoring_cannot_be_rescued_by_pooling(self) -> None:
        scoring = self.contract["participant_first_scoring"]
        self.assertEqual(scoring["positive_participants_minimum"], 15)
        self.assertEqual(scoring["complete_participants_denominator"], 21)
        self.assertEqual(scoring["mean_margin_nats_per_item_minimum"], 0.03)
        self.assertTrue(scoring["ties_included_conservatively"])
        self.assertFalse(scoring["pooled_rows_may_rescue_participant_macro_failure"])
        self.assertFalse(scoring["cohorts_may_rescue_each_other"])
        self.assertFalse(scoring["invalid_rows_may_be_dropped"])
        self.assertEqual(scoring["population"], "independent_replication_free_choice_shadow_rows")
        self.assertEqual(scoring["probability_floor"], 1e-6)
        self.assertAlmostEqual(
            scoring["maximum_frozen_log_loss"], -math.log(1e-6)
        )
        self.assertFalse(
            scoring["positive_prompted_result_may_rescue_failed_free_choice_endpoint"]
        )

    def test_live_coverage_false_commit_and_latency_semantics_are_strict(self) -> None:
        live = self.contract["live_metrics"]
        self.assertEqual(live["stable_commit_coverage_fraction_minimum"], 0.70)
        self.assertEqual(live["per_command_coverage_fraction_minimum"], 0.50)
        self.assertTrue(live["invalid_trials_count_uncovered"])
        self.assertEqual(len(live["inactive_false_commit_surfaces"]), 5)
        self.assertTrue(live["repeated_commit_after_first_counts_as_false_chatter"])
        self.assertTrue(live["missing_clock_map_fails"])
        self.assertFalse(live["accuracy_only_may_establish_live_claim"])
        for key, value in self.parent["live_endpoint"].items():
            self.assertEqual(live[key], value, key)

    def test_adversarial_matrix_counts_and_resources_are_bounded(self) -> None:
        adversarial = self.contract["adversarial_qualification"]
        categories = adversarial["categories"]
        self.assertEqual(len(categories), 10)
        self.assertEqual(sum(categories.values()), 70)
        families = adversarial["refusal_families"]
        self.assertEqual(set(families), set(categories))
        flat = [family for rows in families.values() for family in rows]
        self.assertEqual(flat, EXPECTED_REFUSAL_FAMILIES)
        self.assertEqual(len(set(flat)), 70)
        for category, rows in families.items():
            self.assertEqual(len(rows), categories[category])
        self.assertEqual(adversarial["refusal_observations"], 140)
        semantics = adversarial["family_semantics"]
        self.assertEqual(semantics["executions_per_family_per_replay"], 1)
        self.assertTrue(semantics["pre_and_post_transaction_state_sha256_must_match"])
        replay = adversarial["canonical_replay_equivalence"]
        self.assertEqual(
            replay["volatile_fields_excluded_exactly"],
            [
                "runtime_seconds",
                "peak_process_tree_RSS_bytes",
                "observed_free_disk_bytes",
            ],
        )
        self.assertEqual(len(replay["digest_fields"]), 15)
        self.assertEqual(adversarial["isolated_child_process_replays"], 2)
        self.assertEqual(adversarial["malformed_accepts_maximum"], 0)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 512 * 1024**2)
        self.assertLessEqual(caps["public_aggregate_output_bytes"], 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["retained_generated_payload_bytes_after_proof"], 0)
        self.assertEqual(
            caps["aggregate_incremental_disk_bytes"],
            caps["generated_input_bytes"]
            + caps["private_generated_output_bytes"]
            + caps["temporary_disk_bytes"]
            + caps["public_aggregate_output_bytes"],
        )

    def test_authority_operations_and_claims_remain_closed(self) -> None:
        self.assertTrue(
            all(value is False for value in self.contract["authority"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        self.assertTrue(
            all(value is False for value in self.contract["claim_boundary"].values())
        )
        self.assertTrue(self.contract["active_gate"]["all_authority_flags_false"])

    def test_document_and_frontier_state_exact_boundary(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("engineering qualification over fictional", document)
        self.assertIn("This is an engineering qualification", document)
        self.assertIn("It would not establish real synchronization", document)
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        registration = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["prospective_synchronized_cohort_preregistration"]
        generated = registration["generated_qualification_registration"]
        self.assertEqual(generated["gate_id"], "COMM-P0-G-v0")
        self.assertEqual(generated["status"], "registration_pending_own_remote_CI")
        self.assertFalse(generated["implementation_authorized_now"])
        self.assertFalse(generated["execution_authorized_now"])


if __name__ == "__main__":
    unittest.main()
