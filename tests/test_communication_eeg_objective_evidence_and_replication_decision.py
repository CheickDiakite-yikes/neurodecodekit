from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_objective_evidence_and_replication_decision.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_OBJECTIVE_EVIDENCE_AND_REPLICATION_DECISION_2026_08_27.md"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationEEGObjectiveEvidenceAndReplicationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_schema_and_active_gate_are_preserved(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_objective_evidence_and_replication_decision",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        gate = self.record["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertFalse(gate["authority_changed"])
        self.assertTrue(gate["all_authority_flags_remain_false"])
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
        ]["objective_evidence_and_replication_decision"]
        self.assertEqual(
            routing["green_decision_commit"],
            "9c3489c83dc2584a4fa454714ea2bc6166336234",
        )
        self.assertEqual(routing["green_decision_CI_run_id"], 33_069_830_931)
        self.assertEqual(routing["green_decision_base_python_job_id"], 98_508_922_485)
        self.assertEqual(
            routing["green_decision_optional_neuro_readers_job_id"],
            98_508_922_088,
        )
        self.assertTrue(routing["both_required_jobs_green"])
        self.assertFalse(routing["real_data_packet_created"])
        self.assertEqual(routing["payload_or_private_operations"], 0)
        self.assertFalse(routing["active_Tier_C_gate_changed"])

    def test_only_narrow_prior_evidence_is_established(self) -> None:
        ledger = self.record["evidence_ledger"]
        self.assertEqual(
            [row["requirement_id"] for row in ledger],
            [
                "E0_REAL_HELD_OUT_TASK_INFORMATION",
                "E1_PROMPTED_COMMUNICATION_INFORMATION",
                "E2_EEG_BEYOND_EYE_MOUTH_TIMING_CUE_AND_PRIOR",
                "E3_UNSEEN_PERSON_COMMUNICATION",
                "E4_INDEPENDENT_COMMUNICATION_REPLICATION",
                "E5_CAUSAL_CONTINUOUS_DECODING",
                "E6_LIVE_ACTUAL_DEVICE_DECODING",
                "E7_EXTERNAL_REPRODUCTION",
            ],
        )
        self.assertTrue(ledger[0]["established"])
        self.assertEqual(
            ledger[0]["claim_class"],
            "directional_protocol_information_only",
        )
        self.assertTrue(all(not row["established"] for row in ledger[1:]))

    def test_source_roles_cannot_be_silently_upgraded(self) -> None:
        rows = {row["source_id"]: row for row in self.record["source_roles"]}
        discovery = rows["OpenNeuro_ds003626_v2.1.2"]
        self.assertEqual(discovery["role"], "discovery")
        self.assertFalse(discovery["independent_replication_source"])
        self.assertFalse(discovery["operationally_qualified"])
        self.assertFalse(discovery["acquisition_authorized"])

        silent = rows["SilentSpeech_EEG_2026"]
        self.assertEqual(silent["role"], "full_control_replication_watchlist")
        self.assertEqual(
            silent["public_repository_commit"],
            "16ac8686627a74820e59cb02e6b8506a7abc24b2",
        )
        self.assertTrue(silent["repository_load_data_module_observed"])
        self.assertTrue(silent["open_missing_dataset_module_issue_observed"])
        for key in (
            "reproducible_public_loader_verified",
            "stable_dataset_DOI_or_immutable_release_verified",
            "complete_payload_manifest_and_hashes_verified",
            "dataset_license_verified",
            "exact_public_EOG_and_oral_EMG_roles_verified",
            "operationally_qualified",
            "acquisition_authorized",
        ):
            self.assertFalse(silent[key], key)

        tesscco = rows["TESSCCo_2026"]
        self.assertEqual(tesscco["reported_participants"], 24)
        self.assertEqual(tesscco["reported_commands"], 5)
        self.assertFalse(tesscco["separate_EOG_channels_verified"])
        self.assertFalse(tesscco["separate_oral_EMG_channels_verified"])
        self.assertFalse(tesscco["full_peripheral_adjusted_replication_ready"])

        kara = rows["Kara_One"]
        self.assertEqual(kara["reported_EOG_channels"], 4)
        self.assertTrue(kara["reported_face_tracking"])
        self.assertFalse(kara["separate_oral_EMG_verified"])
        self.assertFalse(kara["complete_archive_within_selected_raw_cap"])

        dreyer = rows["Dreyer_Dataset_A"]
        self.assertIn("motor", dreyer["role"])
        self.assertFalse(dreyer["may_establish_language_or_communication"])
        self.assertFalse(dreyer["may_establish_live_decoding"])

    def test_routing_keeps_discovery_replication_and_method_precursor_separate(self) -> None:
        routing = self.record["routing_decision"]
        self.assertEqual(routing["discovery_source"], "OpenNeuro_ds003626_v2.1.2")
        self.assertEqual(
            routing["full_control_replication_watchlist_source"],
            "SilentSpeech_EEG_2026",
        )
        self.assertEqual(routing["partial_independent_command_source"], "TESSCCo_2026")
        self.assertEqual(routing["method_precursor"], "Dreyer_Dataset_A")
        self.assertFalse(
            routing[
                "discovery_outcomes_may_select_replication_people_preprocessing_thresholds_or_capacity"
            ]
        )
        self.assertFalse(routing["partial_replication_may_upgrade_full_control_claim"])
        self.assertTrue(
            routing[
                "replication_source_hypothesis_features_controls_model_thresholds_and_exclusions_frozen_before_discovery_target_delivery"
            ]
        )

    def test_language_controls_are_machine_bound(self) -> None:
        self.assertEqual(
            self.record["language_control_arms_required_before_final_language_claim"],
            [
                "language_only",
                "neural_only",
                "neural_plus_language",
                "item_deranged_neural_plus_language",
            ],
        )

    def test_evidence_sequence_freezes_before_scores_and_live(self) -> None:
        sequence = self.record["next_evidence_sequence"]
        self.assertEqual(len(sequence), 9)
        self.assertLess(
            sequence.index("COMM_P_prediction_freeze"),
            sequence.index(
                "COMM_R0_replication_preregistration_freeze_before_discovery_targets"
            ),
        )
        self.assertLess(
            sequence.index(
                "COMM_R0_replication_preregistration_freeze_before_discovery_targets"
            ),
            sequence.index("COMM_T_one_discovery_score"),
        )
        self.assertLess(
            sequence.index("COMM_T_one_discovery_score"),
            sequence.index(
                "COMM_R1_independently_frozen_full_or_explicitly_partial_replication_execution"
            ),
        )
        self.assertLess(
            sequence.index(
                "COMM_R1_independently_frozen_full_or_explicitly_partial_replication_execution"
            ),
            sequence.index("NDK_STREAM_causal_source_only_endpointing_and_latency"),
        )
        self.assertEqual(sequence[-1], "NDK_LIVE_one_prospective_actual_device_run")

    def test_resources_and_operation_counts_remain_bounded_and_zero(self) -> None:
        policy = self.record["resource_policy"]
        self.assertEqual(policy["CPU_threads_default"], 1)
        self.assertEqual(policy["workers_default"], 1)
        self.assertEqual(policy["numerical_jobs_default"], 1)
        self.assertEqual(
            policy["maximum_total_incremental_research_storage_bytes"],
            20 << 30,
        )
        self.assertEqual(
            policy["maximum_communication_selected_raw_bytes"],
            10 << 30,
        )
        self.assertEqual(policy["incremental_payload_bytes_this_record"], 0)
        self.assertFalse(policy["write_outside_NeuroDecodeKit"])
        self.assertFalse(policy["cleanup_or_deletion"])
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_scientific_claims_stay_false(self) -> None:
        claims = self.record["claim_boundary"]
        self.assertEqual(
            claims["engineering_capability_added"],
            "machine_tested_objective_evidence_ledger_and_source_role_router",
        )
        for key, value in claims.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("An LLM cannot repair this evidence gap", self.document)

    def test_primary_sources_are_explicit(self) -> None:
        sources = self.record["primary_sources"]
        self.assertEqual(len(sources), 10)
        self.assertTrue(all(url.startswith("https://") for url in sources.values()))


if __name__ == "__main__":
    unittest.main()
