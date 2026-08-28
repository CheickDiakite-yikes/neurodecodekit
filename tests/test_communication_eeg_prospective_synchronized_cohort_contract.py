from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_synchronized_cohort_contract.v0.json"
)
DOCUMENT = (
    ROOT / "docs/COMMUNICATION_EEG_PROSPECTIVE_SYNCHRONIZED_COHORT_PREREGISTRATION.md"
)
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


class CommunicationEEGProspectiveSynchronizedCohortContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_two_independent_cohorts_and_participant_inference(self) -> None:
        cohorts = self.record["cohorts"]
        self.assertEqual(cohorts["discovery"]["planned_complete_participants"], 21)
        self.assertEqual(
            cohorts["independent_replication"]["planned_complete_participants"], 21
        )
        self.assertEqual(cohorts["discovery"]["minimum_complete_participants"], 21)
        self.assertEqual(
            cohorts["independent_replication"]["minimum_complete_participants"],
            21,
        )
        self.assertFalse(cohorts["performance_based_exclusion_or_reassignment_allowed"])
        self.assertFalse(cohorts["post_enrollment_performance_substitution_allowed"])
        self.assertEqual(cohorts["maximum_total_enrolled_participants"], 44)

        inference = self.record["participant_inference"]
        p_15_of_21 = sum(math.comb(21, k) for k in range(15, 22)) / 2**21
        self.assertEqual(
            inference["supporting_exact_sign_test"]["one_sided_p_at_15_of_21"],
            p_15_of_21,
        )
        self.assertLess(p_15_of_21, 0.05)
        self.assertEqual(inference["maximum_sign_assignments"], 2**22)
        self.assertTrue(inference["discovery_and_replication_must_pass_separately"])
        self.assertFalse(inference["pooled_success_may_rescue_a_failed_cohort"])

    def test_full_sensor_and_user_intention_contract(self) -> None:
        acquisition = self.record["acquisition"]
        self.assertEqual(acquisition["biosignal_channels"]["EEG"], 64)
        self.assertEqual(acquisition["biosignal_channels"]["EOG"], 4)
        self.assertEqual(acquisition["biosignal_channels"]["bilateral_oral_EMG"], 4)
        self.assertEqual(acquisition["biosignal_channels"]["photodiode_MISC"], 1)
        self.assertEqual(acquisition["biosignal_channels"]["total"], 73)
        self.assertTrue(acquisition["microphone_required"])
        self.assertTrue(acquisition["hardware_trigger_required"])
        self.assertTrue(acquisition["photodiode_display_onset_required"])
        self.assertTrue(acquisition["EEG_geometry_required"])
        self.assertEqual(acquisition["BIDS_version"], "1.11.1")
        self.assertFalse(acquisition["raw_irreversibly_cleaned_before_control_analysis_allowed"])

        task = self.record["task"]
        self.assertEqual(task["command_inventory_size"], 4)
        self.assertEqual(task["prompted_intend_trials_per_participant"], 64)
        self.assertEqual(task["prompted_no_intent_trials_per_participant"], 32)
        self.assertEqual(task["free_choice_intend_trials_per_participant"], 64)
        self.assertEqual(task["free_choice_no_intent_trials_per_participant"], 32)
        self.assertEqual(task["rest_trials_per_participant"], 32)
        self.assertEqual(task["peripheral_calibration_trials_per_participant"], 32)
        self.assertEqual(task["maximum_total_trials_per_participant"], 256)
        self.assertIn("encrypted_TargetVault", task["free_choice_target_rule"])
        self.assertFalse(task["continuous_decoder_receives_block_or_trial_identity"])
        self.assertFalse(
            task[
                "free_choice_target_or_vault_key_may_enter_model_preprocessing_or_operator_surface"
            ]
        )

    def test_storage_arithmetic_stays_inside_twenty_GiB(self) -> None:
        acquisition = self.record["acquisition"]
        storage = self.record["storage_budget"]
        participants = 44
        seconds = acquisition["maximum_recording_seconds_per_participant"]
        biosignal_bytes = (
            acquisition["biosignal_channels"]["total"]
            * acquisition["biosignal_sampling_rate_hz"]
            * acquisition["biosignal_storage_bytes_per_sample"]
            * seconds
            * participants
        )
        audio_bytes = (
            acquisition["audio_sampling_rate_hz"]
            * acquisition["audio_channels"]
            * acquisition["audio_storage_bytes_per_sample"]
            * seconds
            * participants
        )
        self.assertEqual(storage["raw_biosignal_worst_case_bytes"], biosignal_bytes)
        self.assertEqual(storage["raw_audio_worst_case_bytes"], audio_bytes)
        self.assertEqual(storage["raw_total_worst_case_bytes"], biosignal_bytes + audio_bytes)
        self.assertLessEqual(storage["raw_total_worst_case_bytes"], storage["raw_payload_cap_bytes"])
        self.assertEqual(
            storage["raw_cap_headroom_bytes"],
            storage["raw_payload_cap_bytes"] - storage["raw_total_worst_case_bytes"],
        )
        self.assertEqual(
            storage["sum_of_declared_caps_bytes"]
            + storage["unallocated_permission_headroom_bytes"],
            storage["permission_ceiling_bytes"],
        )
        self.assertTrue(storage["park_if_any_cap_or_free_space_floor_fails"])
        self.assertFalse(storage["full_float32_raw_copy_allowed"])

    def test_hardware_sync_and_voice_privacy_park_before_collection(self) -> None:
        qualification = self.record["precollection_hardware_qualification"]
        self.assertTrue(qualification["required_before_human_recording"])
        self.assertEqual(qualification["cold_start_bench_replays"], 3)
        self.assertEqual(qualification["duration_seconds_per_replay"], 1_800)
        self.assertTrue(qualification["wired_acquisition_network_required"])
        self.assertEqual(
            qualification["LSL_clock_uncertainty_p99_milliseconds_maximum"], 1.0
        )
        self.assertEqual(
            qualification["hardware_residual_p99_EEG_samples_maximum"], 2
        )
        self.assertEqual(
            qualification["hardware_residual_p99_milliseconds_maximum"],
            2 / self.record["acquisition"]["biosignal_sampling_rate_hz"] * 1_000,
        )
        self.assertEqual(
            qualification["bench_failure_action"],
            "park_before_recruitment_or_recording",
        )

        privacy = self.record["privacy_boundary"]
        self.assertTrue(privacy["pseudonymous_BIDS_root"])
        self.assertFalse(privacy["full_band_voice_in_shareable_BIDS_root"])
        self.assertEqual(privacy["audio_storage"], "separately_encrypted_protected_root")
        self.assertFalse(privacy["individual_neural_audio_or_target_hashes_public_by_default"])

    def test_controls_endpoint_and_live_metrics_are_claim_bearing(self) -> None:
        conditions = set(self.record["required_conditions"])
        for required in (
            "EOG_only",
            "oral_EMG_only",
            "microphone_only",
            "posterior_EEG_only",
            "P_plus_residual_central_EEG",
            "P_plus_class_destroyed_residual_central_EEG",
            "null_or_rest_endpoint",
            "language_only",
            "deranged_neural_plus_language",
        ):
            self.assertIn(required, conditions)

        endpoint = self.record["primary_endpoint"]
        self.assertEqual(endpoint["minimum_log_loss_gain_nats_per_item"], 0.03)
        self.assertEqual(
            endpoint[
                "balanced_accuracy_margin_over_strongest_prior_cue_timing_posterior_or_peripheral_control"
            ],
            0.05,
        )
        self.assertFalse(endpoint["positive_prompted_result_may_rescue_failed_free_choice_endpoint"])

        live = self.record["live_endpoint"]
        required_live_fields = [key for key, value in live.items() if key.endswith("_required")]
        self.assertGreaterEqual(len(required_live_fields), 9)
        self.assertTrue(all(live[key] for key in required_live_fields))
        self.assertEqual(live["stable_commit_coverage_fraction_minimum"], 0.70)
        self.assertEqual(live["false_commits_per_inactive_minute_maximum"], 0.10)
        self.assertEqual(live["dropped_or_invalid_chunk_fraction_maximum"], 0.01)
        self.assertEqual(live["frames_processed_before_next_deadline_fraction_minimum"], 0.99)
        self.assertEqual(live["stable_commit_latency_median_seconds_maximum"], 2.5)
        self.assertEqual(live["stable_commit_latency_p95_seconds_maximum"], 5.0)
        self.assertEqual(
            live["capture_to_presentation_processing_overhead_p95_seconds_maximum"],
            0.5,
        )
        self.assertFalse(live["accuracy_only_may_establish_live_claim"])

    def test_target_firewall_and_claim_ceiling_fail_closed(self) -> None:
        firewall = self.record["target_firewall"]
        self.assertTrue(
            firewall[
                "replication_protocol_model_threshold_and_code_hash_freeze_before_discovery_target_delivery"
            ]
        )
        self.assertTrue(firewall["replication_prediction_freeze_before_replication_target_delivery"])
        self.assertFalse(firewall["post_target_tuning_rerun_or_model_substitution"])

        router = self.record["claim_router"]
        self.assertFalse(router["E7_external_reproduction_possible_from_this_same_site_protocol"])
        self.assertFalse(
            router["thought_reading_sentence_decoding_semantic_reconstruction_or_clinical_claim_allowed"]
        )

    def test_authority_and_operation_counters_remain_zero(self) -> None:
        authority = self.record["authority"]
        self.assertTrue(authority["generated_contract_tests"])
        forbidden = {key: value for key, value in authority.items() if key != "generated_contract_tests"}
        self.assertTrue(all(value is False for value in forbidden.values()))
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        gate = self.record["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_remain_false"])

    def test_document_and_frontier_state_exact_boundary(self) -> None:
        document = " ".join(DOCUMENT.read_text(encoding="utf-8").split())
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no human, device, or real-data authority", document)

        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        prospective = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["prospective_synchronized_cohort_preregistration"]
        self.assertEqual(prospective["registration_id"], "COMM-P0-SYNC-v0")
        self.assertEqual(prospective["planned_complete_participants"], 42)
        self.assertEqual(prospective["maximum_enrolled_participants"], 44)
        self.assertEqual(prospective["raw_worst_case_bytes"], 10_463_692_800)
        self.assertFalse(prospective["human_or_device_authority"])
        self.assertFalse(prospective["scientific_claim_established"])


if __name__ == "__main__":
    unittest.main()
