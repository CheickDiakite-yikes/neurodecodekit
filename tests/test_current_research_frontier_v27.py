from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v27.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v26.json"
PACKET = ROOT / "registries/fresh_motor_end_to_end_real_experiment_authorization_request.v0.json"


def _git_blob(payload: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload,
        usedforsecurity=False,
    ).hexdigest()


class CurrentResearchFrontierV27Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.packet = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_predecessor_is_superseded_without_rewriting_it(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"], PREDECESSOR.relative_to(ROOT).as_posix()
        )
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        self.assertFalse(self.frontier["preserved_history"]["predecessor_frontier_modified"])

    def test_every_existing_identity_is_exact(self) -> None:
        roles = set()
        for identity in self.frontier["bound_existing_identities"]:
            roles.add(identity["role"])
            payload = (ROOT / identity["path"]).read_bytes()
            with self.subTest(role=identity["role"]):
                self.assertEqual(len(payload), identity["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), identity["sha256"])
                self.assertEqual(_git_blob(payload), identity["git_blob"])
        self.assertEqual(
            roles,
            {
                "approved_charter_historical_snapshot",
                "approved_charter_activation_decision_human_record",
                "approved_charter_activation_decision_machine_record",
                "public_confirmation_v1_amendment_human_record",
                "public_confirmation_v1_amendment_machine_record",
                "public_confirmation_v1_activation_decision_human_record",
                "public_confirmation_v1_activation_decision_machine_record",
                "initial_adopted_work_order_human_record",
                "initial_adopted_work_order_machine_record",
            },
        )

    def test_pending_decision_paths_and_delayed_effect_are_exact(self) -> None:
        pending = self.frontier["same_commit_activation_records"]
        self.assertEqual(
            pending["amendment_machine_record_path"],
            "registries/research_autonomy_charter_tier_c_public_confirmation_amendment.v0.json",
        )
        self.assertEqual(
            pending["activation_decision_human_record_path"],
            "docs/RESEARCH_AUTONOMY_CHARTER_TIER_C_PUBLIC_CONFIRMATION_DECISION.md",
        )
        self.assertEqual(
            pending["activation_decision_machine_record_path"],
            "registries/research_autonomy_charter_tier_c_public_confirmation_decision.v0.json",
        )
        self.assertTrue(pending["exact_identities_bound"])
        self.assertFalse(pending["effective_before_same_commit_remote_green"])
        delegation = self.frontier["standing_delegation"]
        self.assertEqual(delegation["profile"], "public_confirmation_v1")
        self.assertEqual(delegation["claim_class"], "motor_central_increment_v1")
        self.assertFalse(delegation["effective_now"])
        self.assertIn("Base_Python_and_Optional_Neuro_Readers_green", delegation["effect_condition"])
        self.assertEqual(self.frontier["active_Tier_C_packet"], "FMSR1-E2E-v0")
        self.assertFalse(
            self.frontier[
                "active_Tier_C_packet_runtime_authority_before_activation_decision_remote_green"
            ]
        )

    def test_initial_work_order_identity_and_conditional_adoption_are_exact(self) -> None:
        adopted = self.frontier["initial_adopted_work_order"]
        self.assertEqual(adopted["packet_id"], "FMSR1-E2E-v0")
        self.assertEqual(
            adopted["packet_commit"], "b4e0689d5cb78706896eb0cc9566c1a707cddb50"
        )
        self.assertEqual(adopted["packet_CI_run_id"], 33419678858)
        self.assertEqual(adopted["packet_base_python_job_id"], 99578715549)
        self.assertEqual(adopted["packet_optional_neuro_readers_job_id"], 99578715620)
        self.assertTrue(adopted["packet_both_required_jobs_green"])
        self.assertTrue(adopted["packet_on_GitHub_main"])
        self.assertFalse(adopted["adoption_effective_now"])
        self.assertTrue(adopted["adoption_effective_only_after_activation_decision_remote_green"])
        self.assertEqual(adopted["additional_human_micro_gates_after_effective_adoption"], 0)
        self.assertEqual(self.packet["packet_id"], adopted["packet_id"])
        self.assertTrue(
            self.packet["single_decision_contract"][
                "fresh_short_form_words_required_after_packet_remote_green"
            ]
        )
        self.assertEqual(
            self.packet["single_decision_contract"][
                "additional_human_micro_gates_after_green_decision"
            ],
            0,
        )

    def test_no_runtime_authority_is_active_before_remote_green(self) -> None:
        self.assertTrue(
            all(
                value is False
                for value in self.frontier["runtime_operation_authority_now"].values()
            )
        )
        gate = self.frontier["next_gate"]
        self.assertTrue(gate["activation_decision_present_and_exactly_bound_now"])
        self.assertTrue(
            all(
                value is False
                for key, value in gate.items()
                if key not in {"action", "activation_decision_present_and_exactly_bound_now"}
            )
        )

    def test_target_firewall_and_single_use_rules_remain_closed(self) -> None:
        gates = self.frontier["preserved_target_and_single_use_gates"]
        self.assertFalse(
            gates[
                "confirmation_labels_or_outcomes_may_influence_fit_calibration_selection_exclusion_power_threshold_seed_model_protocol_or_source"
            ]
        )
        self.assertTrue(gates["all_scientifically_material_choices_frozen_before_confirmation_delivery"])
        self.assertFalse(gates["prediction_workers_receive_confirmation_targets"])
        self.assertFalse(gates["prediction_aggregator_receives_confirmation_targets"])
        self.assertEqual(gates["confirmation_target_deliveries_maximum"], 1)
        self.assertEqual(gates["scores_maximum"], 1)
        self.assertEqual(gates["post_target_updates"], 0)
        self.assertTrue(
            gates[
                "central_must_beat_N_posterior_pre_cue_cue_shift_and_derangement_conjunctively"
            ]
        )
        self.assertTrue(gates["one_target_blind_common_mask_before_control_mapping"])
        self.assertFalse(gates["imputation_arm_specific_deletion_or_post_target_dropping"])
        self.assertEqual(gates["joint_all_edge_power_minimum"], 0.8)
        self.assertEqual(gates["confirmation_dependent_public_bits_before_single_scorer"], 0)
        self.assertTrue(gates["every_terminal_route_consumes_attempt"])
        self.assertFalse(gates["retry_rerun_resume_repair_reseed_refreeze_substitute_or_reuse"])
        self.assertFalse(gates["failed_scientific_result_may_select_another_source"])

    def test_resource_and_human_gated_boundaries_are_preserved(self) -> None:
        resources = self.frontier["preserved_resource_envelope"]
        self.assertEqual(resources["CPU_threads_maximum"], 1)
        self.assertEqual(resources["workers_maximum"], 1)
        self.assertEqual(resources["numerical_jobs_maximum"], 1)
        self.assertEqual(resources["wall_time_seconds_maximum"], 86_400)
        self.assertEqual(resources["peak_process_tree_RSS_bytes_maximum"], 4 * 1024**3)
        self.assertEqual(resources["GitHub_remote_green_verification_events_maximum"], 3)
        self.assertEqual(resources["GitHub_CI_read_requests_per_reached_event_exact"], 3)
        self.assertEqual(resources["GitHub_CI_read_requests_total_maximum"], 9)
        self.assertEqual(resources["discovery_requests_maximum"], 125)
        self.assertEqual(resources["candidate_metadata_manifest_license_and_header_requests_maximum"], 256)
        self.assertEqual(resources["header_body_bytes_total_maximum"], 1024**2)
        self.assertEqual(resources["selected_payload_bytes_maximum"], 12 * 1024**3)
        self.assertEqual(resources["total_incremental_disk_bytes_maximum"], 20 * 1024**3)
        self.assertEqual(
            resources["filesystem_free_bytes_minimum_after_every_allocation"],
            20 * 1024**3,
        )
        self.assertFalse(resources["automated_resource_increase_allowed"])
        self.assertFalse(resources["scientific_source_credentials_allowed"])
        git = resources["GitHub_control_plane"]
        self.assertEqual(git["post_activation_push_transactions_maximum"], 2)
        self.assertTrue(git["existing_host_authentication_may_be_used"])
        self.assertFalse(git["credential_read_print_copy_export_or_mutation_allowed"])
        clean = resources["clean_worktree"]
        self.assertTrue(clean["new_worktree_at_exact_remote_green_main_required"])
        self.assertFalse(clean["primary_checkout_user_changes_are_cleanliness_exceptions"])
        self.assertFalse(clean["primary_checkout_user_changes_copied_imported_configured_or_used_as_inputs"])
        self.assertTrue(
            all(
                value is False
                for value in self.frontier[
                    "authority_remaining_fresh_human_gated_after_delegation"
                ].values()
            )
        )

    def test_history_and_claims_remain_closed(self) -> None:
        history = self.frontier["preserved_history"]
        self.assertTrue(all(value is False for value in history.values()))
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))
        coordinate = self.frontier["current_evidence_coordinate"]
        self.assertFalse(coordinate["scientific_claim_upgrade"])
        self.assertEqual(coordinate["dimension_4_task_autonomy"], "source_not_selected")


if __name__ == "__main__":
    unittest.main()
