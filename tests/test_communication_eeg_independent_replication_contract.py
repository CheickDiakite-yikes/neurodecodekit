from __future__ import annotations

import hashlib
import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_contract.v0.json"
)
DOCUMENT = ROOT / "docs" / "COMMUNICATION_EEG_INDEPENDENT_REPLICATION_PREREGISTRATION.md"
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationEEGIndependentReplicationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_schema_parent_proof_and_active_gate(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_independent_replication_contract",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        parent = self.record["parent_evidence_decision"]
        self.assertEqual(
            parent["proof_closeout_commit"],
            "441c4e36d1472298b543feef524ff9b4978e06ea",
        )
        self.assertTrue(parent["both_required_jobs_green"])
        for artifact in parent["bound_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

        gate = self.record["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_remain_false"])
        self.assertFalse(gate["authority_changed"])
        authoritative = self.frontier["fresh_replication"]["active_Tier_C_packet"]
        self.assertEqual(authoritative["packet_id"], gate["gate_id"])
        self.assertTrue(authoritative["all_authority_flags_false"])
        self.assertTrue(authoritative["fresh_packet_bound_maintainer_decision_required"])
        for key in (
            "real_requests",
            "real_network_bytes",
            "real_EDF_bytes",
            "real_EDF_header_reads",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(authoritative[key], 0, key)
        routing = self.frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["independent_replication_preregistration"]
        self.assertEqual(routing["registration_id"], self.record["registration_id"])
        self.assertTrue(routing["protocol_frozen_before_discovery_score"])
        self.assertIn("offline_event_locked", routing["analysis_mode"])
        self.assertFalse(routing["continuous_or_live_claim_allowed"])
        self.assertTrue(routing["source_router_deterministic"])
        self.assertFalse(routing["external_or_generative_language_model_allowed"])
        self.assertFalse(routing["both_required_jobs_green"])
        self.assertEqual(routing["payload_or_private_operations"], 0)
        self.assertFalse(routing["active_Tier_C_gate_changed"])

    def test_replication_is_locked_before_discovery_targets(self) -> None:
        lock = self.record["discovery_score_lock"]
        self.assertTrue(lock["replication_protocol_frozen_now"])
        self.assertTrue(
            lock[
                "exact_replication_source_identity_and_claim_ceiling_must_be_frozen_before_discovery_target_delivery"
            ]
        )
        self.assertTrue(lock["source_lock_must_be_committed_pushed_and_remotely_green"])
        self.assertEqual(lock["discovery_target_delivery_when_source_lock_absent"], "refuse")
        self.assertFalse(
            lock[
                "discovery_outcomes_may_select_source_participants_preprocessing_features_controls_model_thresholds_or_exclusions"
            ]
        )

    def test_source_routes_preserve_full_and_partial_claim_ceilings(self) -> None:
        routes = self.record["source_routes"]
        router = routes["deterministic_router"]
        self.assertIn("SilentSpeech", router["step_1"])
        self.assertIn("TESSCCo", router["step_2"])
        self.assertTrue(router["all_frozen_routes_reported_regardless_of_outcome"])
        self.assertFalse(
            router[
                "route_or_subset_selection_from_discovery_or_published_participant_performance"
            ]
        )
        self.assertEqual(
            router["over_cap_or_unsplittable_action"],
            "park_without_participant_dropping",
        )
        full = routes["full_control"]
        self.assertEqual(full["source_id"], "SilentSpeech_EEG_2026")
        self.assertEqual(full["status_now"], "watchlist_not_operationally_qualified")
        self.assertEqual(len(full["required_public_target_free_gates"]), 9)
        self.assertEqual(full["failure_of_any_gate"], "route_closed")

        for route_name in ("partial_prompted_command", "partial_eye_face"):
            self.assertFalse(routes[route_name]["may_upgrade_full_peripheral_adjusted_claim"])
        self.assertFalse(routes["partial_prompted_command"]["separate_EOG_verified_now"])
        self.assertEqual(
            routes["partial_prompted_command"]["minimum_complete_participants"],
            12,
        )
        self.assertTrue(routes["partial_eye_face"]["recorded_EOG_verified_now"])
        self.assertEqual(routes["partial_eye_face"]["minimum_complete_participants"], 12)
        self.assertFalse(routes["partial_eye_face"]["separate_oral_EMG_verified_now"])

    def test_zero_calibration_participant_firewall_is_exact(self) -> None:
        required = self.record["exact_source_lock_required_fields"]
        self.assertIn("ordered_command_class_inventory_with_raw_UTF8_IDs", required)
        self.assertIn("canonical_item_ID_construction_and_uniqueness_proof", required)

        split = self.record["cohort_and_splits"]
        self.assertEqual(split["outer_split"], "leave_one_participant_out")
        self.assertFalse(split["row_random_split_allowed"])
        for key in (
            "held_out_signal_fit_rows",
            "held_out_target_fit_rows",
            "held_out_normalization_rows",
            "held_out_residualizer_rows",
            "held_out_calibration_rows",
            "held_out_threshold_selection_rows",
            "held_out_adaptation_rows",
        ):
            self.assertEqual(split[key], 0, key)
        self.assertFalse(split["post_lock_participant_exclusion_allowed"])

    def test_causal_features_model_controls_and_derangement_are_frozen(self) -> None:
        features = self.record["causal_features"]
        self.assertTrue(features["sample_window_causal"])
        self.assertEqual(features["analysis_mode"], "offline_event_locked")
        self.assertTrue(features["trial_boundary_oracle_used"])
        self.assertFalse(features["continuous_self_endpointed_claim_allowed"])
        self.assertFalse(features["real_time_or_live_claim_allowed"])
        self.assertTrue(
            features["event_onset_offset_and_feature_availability_timestamp_recorded"]
        )
        self.assertEqual(features["required_left_context_seconds"], 1.0)
        self.assertEqual(features["right_context_seconds"], 0.0)
        self.assertEqual(features["bands_hz"], [[4.0, 8.0], [8.0, 13.0], [13.0, 20.0], [20.0, 30.0]])
        self.assertIn("future_samples", features["forbidden"])
        self.assertIn("target_derived_rejection", features["forbidden"])

        model = self.record["classifier"]
        self.assertEqual(model["C"], 0.1)
        self.assertEqual(model["max_iter"], 1000)
        self.assertFalse(model["hyperparameter_selection"])
        self.assertEqual(model["nonconvergence_action"], "park")

        derangement = self.record["derangement"]
        self.assertEqual(derangement["data_scope"], "source_rows_only")
        self.assertEqual(derangement["class_count_K"], "exact_frozen_source_command_inventory_size")
        self.assertEqual(derangement["control_fits_per_fold"], "K_minus_1")
        self.assertIn("K_minus_1", derangement["permutation_ensemble"])
        self.assertTrue(derangement["held_out_probabilities_averaged_across_derangements"])
        self.assertTrue(
            derangement[
                "every_class_receives_every_other_class_equally_across_ensemble"
            ]
        )
        self.assertFalse(derangement["single_invertible_rotation_used"])
        self.assertFalse(derangement["held_out_rows_permuted"])
        self.assertFalse(derangement["held_out_targets_read"])

    def test_primary_estimand_and_full_router_are_conjunctive(self) -> None:
        estimand = self.record["primary_estimand"]
        self.assertEqual(
            estimand["comparators"],
            ["P", "P_plus_class_destroyed_residual_EEG"],
        )
        self.assertTrue(estimand["both_component_margins_must_be_positive"])
        self.assertFalse(estimand["gain_against_no_signal_alone_is_sufficient"])

        router = self.record["full_control_router"]
        self.assertEqual(router["primary_minimum_margin_nats_per_item"], 0.03)
        self.assertEqual(
            router["both_component_margins_positive_participant_fraction_minimum"],
            0.70,
        )
        self.assertEqual(router["exact_one_sided_participant_sign_flip_p_maximum"], 0.05)
        self.assertEqual(
            router[
                "balanced_accuracy_margin_over_max_equal_prior_source_prior_cue_timing_and_posterior_minimum"
            ],
            0.05,
        )
        self.assertTrue(router["discovery_and_replication_must_each_pass_independently"])
        self.assertFalse(router["partial_route_may_pass_full_control_router"])
        self.assertEqual(router["post_target_updates"], 0)
        self.assertEqual(router["reruns"], 0)
        self.assertEqual(math.ceil(0.70 * 10), 7)
        partial = self.record["partial_router"]
        self.assertFalse(partial["full_control_claim_allowed"])
        self.assertTrue(partial["all_qualified_partial_routes_must_run_and_report"])
        self.assertIn("Holm", partial["multiple_testing_when_two_partial_routes_qualify"])
        self.assertFalse(partial["route_may_be_omitted_after_scoring"])

        sign_flip = self.record["sign_flip_schedule"]
        self.assertEqual(sign_flip["n_above_20_draws"], 1_000_000)
        self.assertTrue(sign_flip["Monte_Carlo_plus_one_correction"])
        self.assertEqual(sign_flip["n_above_20_sampling"], "with_replacement")
        self.assertIn("decimal_draw_i", sign_flip["n_above_20_digest_input"])
        self.assertIn("least_significant_bit", sign_flip["n_above_20_sign_bit"])
        self.assertFalse(sign_flip["library_PRNG_used"])
        self.assertFalse(sign_flip["schedule_may_change_after_target_delivery"])

    def test_language_arms_cannot_create_neural_evidence(self) -> None:
        self.assertEqual(
            self.record["language_control_arms"],
            [
                "language_only",
                "neural_only",
                "neural_plus_language",
                "item_deranged_neural_plus_language",
            ],
        )
        firewall = self.record["language_firewall"]
        self.assertTrue(firewall["neural_prediction_freeze_precedes_language_evaluation"])
        self.assertFalse(firewall["external_or_generative_language_model_allowed"])
        self.assertEqual(firewall["provider_calls"], 0)
        self.assertEqual(firewall["language_only_definition"], "source_class_prior")
        self.assertIn("item-derangement", firewall["item_derangement_digest_input"])
        self.assertEqual(
            firewall["item_derangement_permutation"],
            "rotate_sorted_prediction_vectors_by_plus_one",
        )
        self.assertEqual(
            firewall["item_derangement_group_below_two_items_action"],
            "refuse",
        )
        self.assertTrue(
            firewall["participant_identity_used_only_for_isolation_not_hash_model_or_provider"]
        )
        self.assertFalse(firewall["language_gain_without_neural_gain_passes_neural_router"])
        self.assertIn("held_out_labels", firewall["forbidden_inputs"])
        self.assertIn("raw_EEG", firewall["forbidden_inputs"])

    def test_resources_authority_operations_and_claims_remain_closed(self) -> None:
        resources = self.record["resource_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["maximum_total_incremental_research_storage_bytes"], 20 << 30)
        self.assertEqual(resources["maximum_selected_raw_communication_bytes"], 10 << 30)
        self.assertEqual(resources["incremental_payload_bytes_this_registration"], 0)
        self.assertEqual(resources["generated_qualification_wall_time_seconds"], 300)
        self.assertEqual(
            resources["generated_qualification_peak_process_tree_RSS_bytes"],
            768 << 20,
        )
        self.assertEqual(resources["generated_qualification_public_output_bytes"], 1 << 20)
        self.assertEqual(resources["future_real_execution_wall_time_seconds"], 3600)
        self.assertEqual(
            resources["future_real_execution_peak_process_tree_RSS_bytes"],
            1 << 30,
        )
        self.assertEqual(resources["future_real_parameter_update_fits"], 768)
        self.assertEqual(resources["future_real_inference_and_prediction_sets"], 768)
        self.assertEqual(resources["analysis_network_bytes"], 0)
        self.assertEqual(resources["provider_bytes"], 0)
        self.assertFalse(resources["write_outside_NeuroDecodeKit"])
        self.assertFalse(resources["cleanup_or_deletion_this_registration"])
        self.assertEqual(
            resources["future_cleanup_authority"],
            "inode_verified_invocation_created_temporary_files_only",
        )

        self.assertTrue(all(not value for value in self.record["authorization_state"].values()))
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        claims = self.record["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)

    def test_document_states_engineering_and_scientific_boundaries(self) -> None:
        self.assertIn("Engineering capability added:", self.document)
        self.assertIn("Scientific claim not established:", self.document)
        self.assertIn("If that proof does not exist, discovery scoring stays closed", self.document)
        self.assertIn("partial route may", self.document.lower())


if __name__ == "__main__":
    unittest.main()
