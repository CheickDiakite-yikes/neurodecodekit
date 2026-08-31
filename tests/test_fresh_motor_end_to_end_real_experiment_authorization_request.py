from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    REPO_ROOT
    / "registries/fresh_motor_end_to_end_real_experiment_authorization_request.v0.json"
)


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload,
        usedforsecurity=False,
    ).hexdigest()


class FreshMotorEndToEndAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_packet_is_one_all_false_request(self) -> None:
        request = self.request
        self.assertEqual(request["packet_id"], "FMSR1-E2E-v0")
        self.assertEqual(
            request["status"],
            "all_authorities_false_one_end_to_end_Tier_C_decision_requested",
        )
        self.assertFalse(request["single_decision_contract"]["packet_grants_authority_now"])
        self.assertEqual(
            request["single_decision_contract"][
                "additional_human_micro_gates_after_green_decision"
            ],
            0,
        )
        self.assertTrue(
            all(value is False for value in request["operation_authority_now"].values())
        )
        self.assertEqual(
            request["requested_authority_after_packet_bound_decision_remote_green"]
            ["one_confirmation_target_delivery"],
            True,
        )
        self.assertEqual(
            request["requested_authority_after_packet_bound_decision_remote_green"]
            ["one_score"],
            True,
        )
        self.assertFalse(
            request["requested_authority_after_packet_bound_decision_remote_green"]
            ["source_substitution_or_rerun"]
        )

    def test_human_record_and_bound_artifacts_match_exact_bytes(self) -> None:
        identities = [self.request["human_record"]]
        identities.extend(self.request["bound_predecessor_artifacts"])
        for identity in identities:
            path = REPO_ROOT / identity["path"]
            payload = path.read_bytes()
            with self.subTest(path=identity["path"]):
                self.assertEqual(len(payload), identity["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), identity["sha256"])
                self.assertEqual(_git_blob(payload), identity["git_blob"])

    def test_nuisance_and_comparator_roles_are_exact(self) -> None:
        nuisance = self.request["nuisance_contract"]
        self.assertEqual(
            nuisance["N_components"],
            [
                "EOG",
                "task_relevant_EMG_for_every_relevant_effector",
                "canonical_non_target_identical_cue_type_one_hot",
                "cue_duration",
                "cue_to_motor_interval",
                "within_run_trial_ordinal",
            ],
        )
        self.assertFalse(nuisance["posterior_EEG_in_N"])
        self.assertFalse(
            nuisance["raw_participant_session_acquisition_or_run_identity_in_model_features"]
        )
        self.assertIn(
            "development_labels_only",
            nuisance["development_cue_type_validity_rule_before_freeze"],
        )
        self.assertIn(
            "after_primary_score",
            nuisance["confirmation_cue_type_validity_timing"],
        )
        self.assertIn(
            "no_row_participant_model_prediction_score_or_metric_change",
            nuisance["confirmation_cue_type_validity_failure_effect"],
        )
        self.assertTrue(nuisance["N_byte_identical_across_every_neural_arm"])
        conditions = self.request["condition_contract"]
        self.assertEqual(
            conditions["conditions"],
            [
                "N_plus_central_EEG_correct_motor_window",
                "N_only",
                "N_plus_geometry_matched_posterior_EEG_correct_motor_window",
                "N_plus_central_EEG_pre_cue_window",
                "N_plus_central_EEG_cue_window",
                "N_plus_one_registered_structure_preserving_shifted_central_EEG",
                "N_plus_one_registered_target_blind_deranged_central_EEG",
            ],
        )
        self.assertTrue(conditions["every_edge_must_pass"])
        self.assertFalse(conditions["edges_or_offsets_may_be_averaged"])
        self.assertFalse(conditions["winner_selection_allowed"])

    def test_model_and_target_firewall_are_frozen(self) -> None:
        model = self.request["model_contract"]
        self.assertEqual(model["family"], "multinomial_L2_logistic_regression")
        self.assertEqual(model["C"], 0.1)
        self.assertEqual(model["solver"], "lbfgs")
        self.assertEqual(model["max_iter"], 1000)
        self.assertEqual(model["tol"], 0.000001)
        self.assertIsNone(model["class_weight"])
        self.assertEqual(model["random_state"], 0)
        firewall = self.request["target_firewall"]
        self.assertFalse(
            firewall[
                "confirmation_target_values_delivered_to_model_or_prediction_aggregator_before_freeze"
            ]
        )
        self.assertEqual(firewall["isolated_target_broker_semantic_reads_maximum"], 1)
        self.assertIn(
            "unlinked_descriptor_only_development_label_bundle_for_development_label_worker",
            firewall["broker_outputs"],
        )
        self.assertTrue(
            firewall["worker_capability_contract"][
                "generated_tests_prove_forbidden_opens_fail"
            ]
        )
        self.assertFalse(
            firewall["participant_scoped_prediction_worker_receives_confirmation_targets"]
        )
        self.assertFalse(firewall["prediction_aggregator_receives_targets"])
        self.assertEqual(firewall["target_deliveries_maximum"], 1)
        self.assertEqual(firewall["score_events_maximum"], 1)
        class_contract = firewall["class_assignment_contract"]
        self.assertEqual(
            class_contract["vocabulary_source"],
            "events_json_trial_type_Levels_motor_role_keys_only_before_any_per_row_target_read",
        )
        self.assertFalse(
            class_contract["vocabulary_uses_development_or_confirmation_row_values"]
        )
        domain = firewall["scorer_score_domain_check"]
        self.assertEqual(
            domain["timing"],
            "after_durable_prediction_freeze_and_single_target_delivery_before_any_score",
        )
        self.assertEqual(
            domain["requirements"],
            [
                "every_confirmation_target_maps_to_frozen_source_declared_vocabulary",
                "every_confirmation_participant_by_frozen_class_cell_has_at_least_one_row",
            ],
        )
        self.assertFalse(domain["may_drop_or_select_rows_or_participants"])
        self.assertFalse(
            domain["may_change_model_predictions_metrics_protocol_or_class_order"]
        )
        self.assertIn("zero_scores", domain["failure_route"])
        ledger = firewall["public_target_free_ledger_schema"]
        self.assertEqual(
            ledger["allowed_columns_exact"],
            [
                "opaque_row_id",
                "cue_onset_sample",
                "motor_onset_sample",
                "cue_duration_samples",
                "cue_to_motor_interval_samples",
                "cue_type",
                "within_run_trial_ordinal",
            ],
        )
        self.assertTrue(ledger["every_undeclared_column_forbidden"])
        for forbidden in ("trial_type", "effector", "trial_id", "event_role"):
            self.assertIn(forbidden, ledger["forbidden_columns"])
        self.assertEqual(
            firewall["post_target_parameter_threshold_exclusion_seed_or_protocol_updates"],
            0,
        )
        self.assertFalse(self.request["feature_contract"]["hyperparameter_search"])
        freeze = self.request["prediction_freeze"]
        self.assertEqual(freeze["prediction_file_creation"]["mode"], "0400")
        self.assertTrue(
            freeze["hash_only_freeze_record"][
                "base_and_optional_remote_CI_green_required"
            ]
        )
        self.assertFalse(freeze["bare_target_vault_SHA256_in_public_record"])

    def test_candidate_adapter_shift_and_positive_controls_are_deterministic(
        self,
    ) -> None:
        candidate = self.request["candidate_contract"]
        self.assertEqual(candidate["FMSR1_source_admission_floor_participants"], 10)
        self.assertEqual(
            candidate["minimum_complete_participants_for_this_end_to_end_experiment"],
            15,
        )
        self.assertEqual(candidate["maximum_complete_participants"], 256)
        self.assertTrue(
            candidate[
                "source_issued_exact_size_and_cryptographic_hash_required_for_every_member_before_payload_read"
            ]
        )
        split = self.request["participant_split_contract"]
        self.assertEqual(split["minimum_development_participants"], 5)
        self.assertEqual(split["minimum_confirmation_participants"], 10)
        shift = self.request["shift_and_derangement_contract"]
        self.assertTrue(shift["mask_precedes_control_mapping"])
        self.assertEqual(
            shift["shift"]["offset_rule"],
            "1_plus_int_SHA256_preimage_modulo_m_minus_1",
        )
        self.assertFalse(shift["derangement"]["fixed_points_allowed"])
        self.assertEqual(shift["minimum_rows_per_stratum"], 2)
        self.assertIn(
            "after_primary_score",
            shift["confirmation_stratum_check_timing"],
        )
        self.assertIn(
            "no_inclusion_prediction_score_or_metric_change",
            shift["confirmation_stratum_check_failure_effect"],
        )
        controls = self.request["positive_control_contract"]
        self.assertEqual(
            controls["gates"]["peripheral_recoverability"][
                "minimum_finite_sample_fraction"
            ],
            0.99,
        )
        self.assertEqual(
            controls["gates"]["injected_effect_pipeline_sensitivity"][
                "minimum_equal_class_log_loss_improvement_nats"
            ],
            0.02,
        )

    def test_inference_power_and_missingness_are_participant_first(self) -> None:
        primary = self.request["primary_inference"]
        self.assertEqual(
            primary["primary_metric"],
            "equal_class_within_participant_then_equal_participant_natural_log_loss",
        )
        self.assertEqual(primary["minimum_mean_delta_nats_per_trial_each_edge"], 0.02)
        self.assertEqual(primary["test"], "exact_one_sided_participant_sign_test")
        self.assertEqual(primary["alpha_each_edge"], 0.05)
        self.assertEqual(primary["global_rule"], "intersection_union_all_edges_pass")
        self.assertFalse(primary["Bonferroni_for_global_IUT"])
        self.assertTrue(primary["participant_is_inferential_unit"])
        self.assertFalse(primary["trial_level_inference"])
        self.assertFalse(primary["secondary_metrics_may_rescue_primary_failure"])
        power = self.request["power_contract"]
        self.assertEqual(power["minimum_joint_power"], 0.8)
        self.assertEqual(power["minimum_mean_effect_gate_nats_per_trial"], 0.02)
        self.assertEqual(power["design_alternative_mean_nats_per_trial"], 0.03)
        self.assertFalse(power["positive_point_estimate_may_override_underpowered_route"])
        self.assertEqual(
            power["development_margin_source"],
            "leave_one_development_participant_out_predictions",
        )
        self.assertEqual(
            power["evaluated_confirmation_count"],
            "exact_all_remaining_confirmation_participants",
        )
        self.assertTrue(
            power["underpowering_precedes_target_delivery_scoring_and_edge_interpretation"]
        )
        missingness = self.request["missingness_contract"]
        self.assertTrue(missingness["common_target_blind_row_mask_across_all_arms"])
        self.assertFalse(missingness["imputation_allowed"])
        self.assertEqual(
            missingness[
                "minimum_target_free_declared_motor_row_fraction_retained_per_participant"
            ],
            0.8,
        )
        self.assertFalse(missingness["arm_specific_row_deletion"])
        self.assertFalse(missingness["post_target_participant_exclusion"])
        self.assertTrue(
            missingness["confirmation_class_floor_checked_only_by_scorer_after_primary_score"]
        )
        self.assertIn(
            "claim_ceiling_only",
            missingness["confirmation_class_floor_failure_effect"],
        )

    def test_resource_arithmetic_and_single_use_are_exact(self) -> None:
        resources = self.request["resource_contract"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["network_retries"], 0)
        self.assertEqual(resources["payload_requests_maximum"], 2048)
        self.assertEqual(resources["payload_member_count_maximum"], 2048)
        self.assertEqual(resources["complete_participants_maximum"], 256)
        self.assertEqual(
            resources["model_fit_count_maximum"],
            "10_times_development_participant_count_plus_7",
        )
        self.assertFalse(resources["network_request_contract"]["proxy_allowed"])
        storage = resources["storage_budget"]
        component_sum = sum(
            storage[key]
            for key in (
                "selected_source_payload_bytes",
                "invocation_temporary_bytes",
                "derivative_and_frozen_prediction_bytes",
                "atomic_result_publication_bytes",
                "untouched_reserve_bytes",
            )
        )
        self.assertEqual(component_sum, 21474836480)
        self.assertEqual(component_sum, storage["total_incremental_disk_cap_bytes"])
        self.assertTrue(storage["component_sum_must_equal_total"])
        self.assertEqual(
            storage["minimum_filesystem_free_bytes_after_every_allocation"],
            21474836480,
        )
        self.assertFalse(storage["participant_dropping_to_fit_budget"])
        single_use = self.request["single_use_and_terminal_routes"]
        self.assertEqual(single_use["official_work_order_invocations_maximum"], 1)
        self.assertIn("TARGET_SCORE_DOMAIN_BLOCKER", single_use["consumed_on"])
        self.assertFalse(single_use["retry_rerun_resume_repair_substitution_or_post_target_tuning"])

    def test_packet_claim_ceiling_is_preliminary_only(self) -> None:
        claim = self.request["claim_boundary_now"]
        self.assertTrue(all(value is False for value in claim.values()))
        self.assertEqual(
            self.request["maximum_claim_after_successful_adequately_powered_single_score"],
            "preliminary_cohort_specific_nuisance_resistant_unseen_participant_central_scalp_EEG_increment_under_the_frozen_method",
        )
        self.assertIn("independent_replication", self.request["explicitly_out_of_scope"])
        self.assertIn(
            "release_publication_or_public_scientific_claim_promotion",
            self.request["explicitly_out_of_scope"],
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
