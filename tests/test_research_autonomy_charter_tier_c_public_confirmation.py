from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT_DOC = (
    ROOT / "docs/RESEARCH_AUTONOMY_CHARTER_TIER_C_PUBLIC_CONFIRMATION_AMENDMENT.md"
)
AMENDMENT_RECORD = (
    ROOT
    / "registries/research_autonomy_charter_tier_c_public_confirmation_amendment.v0.json"
)
DECISION_DOC = (
    ROOT / "docs/RESEARCH_AUTONOMY_CHARTER_TIER_C_PUBLIC_CONFIRMATION_DECISION.md"
)
DECISION_RECORD = (
    ROOT
    / "registries/research_autonomy_charter_tier_c_public_confirmation_decision.v0.json"
)
PACKET_RECORD = (
    ROOT / "registries/fresh_motor_end_to_end_real_experiment_authorization_request.v0.json"
)


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload,
        usedforsecurity=False,
    ).hexdigest()


def _assert_identity(test: unittest.TestCase, identity: dict[str, object]) -> None:
    payload = (ROOT / str(identity["path"])).read_bytes()
    test.assertEqual(len(payload), identity["bytes"])
    test.assertEqual(hashlib.sha256(payload).hexdigest(), identity["sha256"])
    test.assertEqual(_git_blob(payload), identity["git_blob"])


class TierCPublicConfirmationAmendmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.amendment_doc = AMENDMENT_DOC.read_text(encoding="utf-8")
        cls.decision_doc = DECISION_DOC.read_text(encoding="utf-8")
        cls.amendment = json.loads(AMENDMENT_RECORD.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_RECORD.read_text(encoding="utf-8"))
        cls.packet = json.loads(PACKET_RECORD.read_text(encoding="utf-8"))

    def test_historical_charter_records_remain_exact(self) -> None:
        historical = self.amendment["historical_governance_bindings"]
        for key in (
            "original_charter_snapshot",
            "original_activation_decision_document",
            "original_activation_decision_machine_record",
        ):
            with self.subTest(key=key):
                _assert_identity(self, historical[key])
                self.assertTrue(historical[key]["remains_byte_identical_historical_record"])
        self.assertFalse(
            historical["original_record_rewritten_or_reinterpreted_as_general_Tier_C_authority"]
        )

    def test_amendment_and_decision_bind_every_exact_record(self) -> None:
        _assert_identity(self, self.amendment["human_record"])
        for identity in self.decision["bound_records"].values():
            _assert_identity(self, identity)
        self.assertEqual(self.amendment["amendment_id"], "TIER-C-PUBLIC-CONFIRMATION-v1")
        self.assertEqual(self.decision["decision_id"], "TIER-C-PUBLIC-CONFIRMATION-v1-D0")

    def test_actual_user_words_are_verbatim_once_and_not_expanded(self) -> None:
        expected = [
            "by anymeans without breaking my computer or storage or other projects.",
            "i dont want it to require my auth to proceed, we need to remove that part",
            "yes Tier C charter amendment, all blocker amendments",
            "commit and push to main",
        ]
        self.assertEqual(self.decision["exact_user_instructions"], expected)
        for words in expected:
            with self.subTest(words=words):
                self.assertEqual(self.decision_doc.count(words), 1)
        self.assertFalse(self.decision["scope_resolution"]["maintainer_words_fabricated_rewritten_or_expanded"])

    def test_remote_green_delayed_effect_is_fail_closed(self) -> None:
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_and_all_bound_records_are_committed_to_GitHub_main_and_both_required_jobs_green"
            ]
        )
        self.assertFalse(self.decision["effective_now_before_remote_green"])
        remote = self.decision["remote_green_activation"]
        self.assertIsNone(remote["decision_commit"])
        self.assertIsNone(remote["CI_run_id"])
        self.assertTrue(remote["runtime_must_resolve_exact_commit_and_unique_successful_jobs"])
        self.assertFalse(remote["effect_before_all_checks_pass"])
        self.assertFalse(remote["another_maintainer_message_after_all_checks_pass"])
        self.assertTrue(
            all(value is False for value in self.decision["operation_authority_before_remote_green"].values())
        )
        self.assertTrue(
            all(value is False for value in self.amendment["operation_authority_now"].values())
        )

    def test_profile_is_not_open_ended_self_admission(self) -> None:
        scope = self.amendment["standing_profile_scope"]
        self.assertEqual(scope["claim_class"], "motor_central_increment_v1")
        self.assertFalse(scope["open_ended_self_admission"])
        self.assertEqual(
            scope["admitted_work_order_ids_exact"],
            ["FMSR1-E2E-v0"],
        )
        self.assertFalse(scope["later_work_order_self_opt_in"])
        self.assertTrue(scope["future_replication_or_new_work_requires_new_profile_revision_and_activation"])
        self.assertFalse(scope["new_hypothesis_weaker_controls_changed_endpoint_inference_or_wider_claim_may_opt_in"])
        self.assertEqual(scope["later_human_micro_gates_inside_admitted_route"], 0)

    def test_admission_has_three_ordered_scientific_gates(self) -> None:
        admission = self.amendment["machine_admission_requirements"]
        self.assertTrue(admission["staged_admission_required"])
        self.assertTrue(admission["gate_A_before_first_network_request"]["exclusive_global_active_work_order_lock_required"])
        self.assertTrue(
            admission["gate_B_after_bounded_discovery_before_bulk_acquisition"]
            ["candidate_values_only_frozen_deterministic_target_free"]
        )
        self.assertEqual(
            admission["gate_C_after_development_processing_before_confirmation_delivery"]
            ["confirmation_derived_pass_fail_bits_before_single_scorer"],
            0,
        )
        self.assertTrue(admission["failed_admission_consumes_under_narrower_contract"])
        self.assertFalse(
            admission[
                "failed_admission_may_become_new_source_relaxed_criterion_larger_model_wider_authority_retry_or_smaller_follow_on_request"
            ]
        )

    def test_comparator_capacity_common_mask_and_power_are_exact(self) -> None:
        science = self.amendment["scientific_integrity_invariants"]
        comparator = science["comparator_contract"]
        self.assertEqual(
            comparator["N_exact"],
            "byte_identical_EOG_plus_every_relevant_effector_EMG_plus_non_target_identical_cue_timing_ordinal_and_allowed_metadata",
        )
        self.assertEqual(len(comparator["required_edges"]), 6)
        self.assertEqual(
            comparator["decision_rule"],
            "conjunctive_intersection_union_every_edge_must_pass",
        )
        self.assertTrue(comparator["same_ordered_rows_and_byte_identical_N_every_neural_arm"])
        self.assertTrue(comparator["equal_neural_width_window_preprocessing_feature_missingness_estimator_and_fit_schedule"])
        self.assertTrue(comparator["one_target_blind_common_complete_case_mask_from_all_unshifted_blocks_before_control_mapping"])
        self.assertFalse(comparator["imputation_arm_specific_deletion_or_post_target_row_or_participant_dropping"])
        power = science["power_contract"]
        self.assertEqual(power["joint_all_edge_power_minimum"], 0.8)
        self.assertTrue(power["evaluated_at_exact_final_confirmation_participant_count"])
        self.assertFalse(power["participant_admission_floor_implies_power"])
        self.assertFalse(power["smaller_count_substitution_allowed"])
        self.assertTrue(power["underpowering_precedes_target_delivery_score_and_edge_interpretation"])

    def test_target_firewall_has_no_pre_score_confirmation_oracle(self) -> None:
        firewall = self.amendment["scientific_integrity_invariants"]["target_firewall_floor"]
        self.assertTrue(firewall["public_ledger_deny_by_default"])
        self.assertEqual(
            set(firewall["forbidden_public_fields"]),
            {
                "raw_participant_identity",
                "raw_session_identity",
                "raw_run_identity",
                "raw_trial_identity",
                "event_role",
                "trial_type",
                "effector",
                "class",
                "label",
                "target",
                "target_identical_metadata",
                "undeclared_field",
            },
        )
        self.assertFalse(firewall["continuous_derivatives_contain_annotations"])
        self.assertTrue(firewall["confirmation_vault_unlinked_and_bare_SHA_private"])
        self.assertFalse(firewall["prediction_worker_raw_member_marker_annotation_events_vault_path_and_network_access"])
        self.assertEqual(firewall["confirmation_dependent_public_bits_before_score"], 0)
        self.assertFalse(firewall["descriptive_checks_may_change_inclusion_prediction_score_metric_row_or_participant"])
        self.assertEqual(self.amendment["scientific_integrity_invariants"]["target_deliveries_maximum"], 1)
        self.assertEqual(self.amendment["scientific_integrity_invariants"]["scores_maximum"], 1)

    def test_lineage_and_claim_ceiling_prevent_outcome_shopping(self) -> None:
        science = self.amendment["scientific_integrity_invariants"]
        self.assertTrue(science["replication_identity_must_be_sealed_before_prior_target_open"])
        self.assertFalse(science["post_outcome_selected_successor_is_confirmation"])
        self.assertTrue(science["post_outcome_selected_successor_is_discovery_only"])
        self.assertEqual(
            science["successful_single_cohort_claim_ceiling"],
            "cohort_specific_participant_generalizing_predictive_increment_under_exact_recorded_comparators",
        )
        self.assertIn("language", science["single_cohort_forbidden_claims"])
        self.assertIn("clinical_value", science["single_cohort_forbidden_claims"])

    def test_network_storage_and_computer_caps_are_exact(self) -> None:
        resources = self.amendment["transport_resource_and_computer_safety_envelope"]
        self.assertEqual(resources["CPU_threads_maximum"], 1)
        self.assertEqual(resources["workers_maximum"], 1)
        self.assertEqual(resources["numerical_jobs_maximum"], 1)
        self.assertEqual(resources["wall_time_seconds_maximum"], 86_400)
        self.assertEqual(resources["peak_process_tree_RSS_bytes_maximum"], 4 * 1024**3)
        self.assertEqual(resources["GitHub_remote_green_verification_events_maximum"], 3)
        self.assertEqual(resources["GitHub_CI_read_requests_per_reached_event_exact"], 3)
        self.assertEqual(resources["GitHub_CI_read_requests_total_maximum"], 9)
        self.assertEqual(resources["GitHub_CI_response_body_bytes_total_maximum"], 24 * 1024**2)
        self.assertEqual(resources["discovery_requests_maximum"], 125)
        self.assertEqual(resources["candidate_metadata_manifest_license_and_header_requests_maximum"], 256)
        self.assertEqual(resources["header_body_bytes_total_maximum"], 1024**2)
        self.assertEqual(resources["payload_requests_maximum"], 2048)
        self.assertEqual(resources["network_retries"], 0)
        storage = resources["storage_budget"]
        components = (
            storage["selected_payload_bytes"],
            storage["invocation_temporary_bytes"],
            storage["derivatives_and_frozen_predictions_bytes"],
            storage["atomic_aggregate_publication_bytes"],
            storage["untouched_reserve_bytes"],
        )
        self.assertEqual(components, (12 * 1024**3, 2 * 1024**3, 2 * 1024**3, 1024**3, 3 * 1024**3))
        self.assertEqual(sum(components), storage["total_incremental_disk_cap_bytes"])
        self.assertEqual(storage["minimum_filesystem_free_bytes_after_every_allocation"], 20 * 1024**3)
        self.assertTrue(resources["cap_plus_one_refuses"])
        self.assertFalse(resources["unused_cap_may_be_reassigned"])
        self.assertFalse(resources["existing_or_external_state_may_be_deleted_overwritten_renamed_moved_or_modified"])
        source_network = resources["network_contract"]
        self.assertFalse(source_network["credentials_allowed_for_scientific_source_endpoints"])
        git = resources["GitHub_control_plane_contract"]
        self.assertEqual(git["repository_exact"], "CheickDiakite-yikes/neurodecodekit")
        self.assertEqual(git["branch_exact"], "main")
        self.assertEqual(git["post_activation_push_transactions_maximum"], 2)
        self.assertTrue(git["existing_host_authentication_may_be_used"])
        self.assertFalse(git["credential_read_print_copy_export_or_mutation_allowed"])
        self.assertTrue(git["fast_forward_non_force_push_required"])
        self.assertFalse(git["tag_release_branch_delete_history_rewrite_force_push_or_other_remote_mutation_allowed"])
        clean = resources["clean_worktree_contract"]
        self.assertTrue(clean["new_worktree_at_exact_remote_green_main_required"])
        self.assertTrue(clean["index_and_working_tree_clean_at_each_remote_green_check"])
        self.assertFalse(clean["primary_checkout_user_changes_are_cleanliness_exceptions"])
        self.assertFalse(clean["primary_checkout_user_changes_copied_imported_configured_or_used_as_inputs"])

    def test_single_use_arms_before_any_external_or_target_operation(self) -> None:
        single = self.amendment["durable_single_use_rule"]
        self.assertTrue(single["durable_arm_before_first_network_request_official_source_contact_raw_member_open_or_target_operation"])
        self.assertTrue(single["every_terminal_route_consumes_attempt"])
        self.assertTrue(all(value is False for value in single["after_arm_or_held_out_access"].values()))
        self.assertFalse(single["same_estimand_source_selected_after_prior_outcome_may_be_confirmatory"])

    def test_only_bounded_conditional_authority_is_true_and_retained_gates_are_false(self) -> None:
        standing = self.decision["standing_authority_after_remote_green_and_machine_admission"]
        expected_non_boolean = {
            "admitted_work_order_id_exact": "FMSR1-E2E-v0",
            "later_work_order_self_admission": False,
            "confirmation_target_deliveries_maximum": 1,
            "scores_maximum": 1,
            "additional_human_micro_gates": 0,
        }
        for key, value in standing.items():
            with self.subTest(key=key):
                if key in expected_non_boolean:
                    self.assertEqual(value, expected_non_boolean[key])
                else:
                    self.assertTrue(value)
        self.assertTrue(
            all(value is False for value in self.decision["authority_remaining_fresh_human_gated"].values())
        )

    def test_initial_FMSR_adoption_changes_human_gate_and_one_CI_read_cap(self) -> None:
        adopted = self.decision["initial_adopted_work_order"]
        self.assertEqual(adopted["packet_id"], "FMSR1-E2E-v0")
        self.assertEqual(adopted["packet_commit"], "b4e0689d5cb78706896eb0cc9566c1a707cddb50")
        self.assertEqual(adopted["packet_CI_run_id"], 33419678858)
        _assert_identity(self, adopted["human_packet"])
        _assert_identity(self, adopted["machine_packet"])
        self.assertFalse(adopted["adoption_effective_before_this_decision_remote_green"])
        self.assertTrue(
            adopted[
                "after_remote_green_replaces_fresh_words_separate_packet_decision_and_only_GitHub_CI_requests_exact_3_total"
            ]
        )
        self.assertTrue(
            adopted[
                "every_scientific_source_payload_storage_retry_firewall_single_use_terminal_and_claim_rule_preserved"
            ]
        )
        self.assertEqual(adopted["additional_human_micro_gates_after_adoption"], 0)
        self.assertFalse(adopted["source_substitution_or_criterion_relaxation"])
        request = self.packet["single_decision_contract"]
        self.assertTrue(request["fresh_short_form_words_required_after_packet_remote_green"])
        self.assertEqual(request["additional_human_micro_gates_after_green_decision"], 0)

    def test_only_packet_resource_delta_is_partitioned_CI_reads(self) -> None:
        packet = self.packet["resource_contract"]
        amended = self.amendment["transport_resource_and_computer_safety_envelope"]
        self.assertEqual(packet["GitHub_CI_requests_exact"], 3)
        self.assertTrue(
            amended[
                "explicitly_supersedes_FMSR1_E2E_v0_GitHub_CI_requests_exact_3_total_only"
            ]
        )
        self.assertEqual(amended["GitHub_CI_read_requests_per_reached_event_exact"], 3)
        self.assertEqual(amended["GitHub_CI_read_requests_total_maximum"], 9)
        unchanged_pairs = {
            "CPU_threads_maximum": "CPU_threads",
            "workers_maximum": "workers",
            "numerical_jobs_maximum": "numerical_jobs",
            "wall_time_seconds_maximum": "wall_time_seconds_maximum",
            "peak_process_tree_RSS_bytes_maximum": "peak_process_tree_RSS_bytes_maximum",
            "discovery_requests_maximum": "discovery_requests_maximum",
            "discovery_response_body_bytes_maximum": "discovery_response_body_bytes_maximum",
            "candidate_metadata_manifest_license_and_header_requests_maximum": "candidate_metadata_header_manifest_requests_maximum",
            "candidate_metadata_manifest_license_and_header_response_body_bytes_maximum": "candidate_metadata_header_body_bytes_maximum",
            "header_body_bytes_total_maximum": "header_body_bytes_total_maximum",
            "payload_requests_maximum": "payload_requests_maximum",
            "payload_members_maximum": "payload_member_count_maximum",
            "network_retries": "network_retries",
            "selected_payload_bytes_maximum": "selected_payload_body_bytes_maximum",
        }
        for amended_key, packet_key in unchanged_pairs.items():
            with self.subTest(amended_key=amended_key):
                self.assertEqual(amended[amended_key], packet[packet_key])
        storage = amended["storage_budget"]
        packet_storage = packet["storage_budget"]
        self.assertEqual(storage["selected_payload_bytes"], packet_storage["selected_source_payload_bytes"])
        self.assertEqual(storage["invocation_temporary_bytes"], packet_storage["invocation_temporary_bytes"])
        self.assertEqual(
            storage["derivatives_and_frozen_predictions_bytes"],
            packet_storage["derivative_and_frozen_prediction_bytes"],
        )
        self.assertEqual(storage["atomic_aggregate_publication_bytes"], packet_storage["atomic_result_publication_bytes"])
        self.assertEqual(storage["untouched_reserve_bytes"], packet_storage["untouched_reserve_bytes"])
        self.assertEqual(storage["total_incremental_disk_cap_bytes"], packet_storage["total_incremental_disk_cap_bytes"])

    def test_governance_records_produced_no_scientific_operation(self) -> None:
        self.assertTrue(all(value == 0 for value in self.amendment["authorization_only_measurements"].values()))
        self.assertTrue(all(value == 0 for value in self.decision["authorization_only_measurements"].values()))
        self.assertTrue(all(value is False for key, value in self.amendment["claim_boundary"].items() if key != "maximum_single_cohort_claim"))
        decision_claim = self.decision["claim_boundary"]
        self.assertFalse(decision_claim["governance_decision_is_scientific_evidence"])
        self.assertFalse(decision_claim["score_produced"])
        self.assertFalse(decision_claim["public_claim_promotion_authorized"])


if __name__ == "__main__":
    unittest.main()
