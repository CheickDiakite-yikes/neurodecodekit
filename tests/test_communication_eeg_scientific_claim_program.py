import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / "communication_eeg_scientific_claim_program.v0.json"
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"
DOCUMENT = ROOT / "docs" / "COMMUNICATION_EEG_SCIENTIFIC_CLAIM_PROGRAM.md"


class CommunicationEEGScientificClaimProgramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.program = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")

    def test_schema_status_and_document(self):
        self.assertEqual(
            self.program["schema_name"],
            "neurodecodekit.communication_eeg_scientific_claim_program",
        )
        self.assertEqual(self.program["schema_version"], "0.1.0")
        self.assertIn("zero_real_or_private_operations", self.program["status"])
        self.assertIn("## End Goal", self.document)
        self.assertIn("## Frozen Program Sequence", self.document)

    def test_active_dreyer_gate_is_preserved_and_unapproved(self):
        gate = self.program["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertFalse(gate["fresh_packet_bound_maintainer_decision_received"])
        self.assertFalse(gate["H_L1_authorized_now"])
        self.assertFalse(gate["H_L2_authorized_now"])
        self.assertFalse(gate["authority_changed_by_this_record"])
        parallel = self.frontier["parallel_tier_A_communication_program"]
        self.assertEqual(parallel["program_id"], self.program["program_id"])
        self.assertFalse(parallel["active_Tier_C_gate_changed"])
        self.assertEqual(parallel["real_or_private_operations"], 0)

    def test_claim_ladder_is_cumulative_and_all_false(self):
        levels = self.program["claim_levels"]
        self.assertEqual(
            [row["level"] for row in levels],
            ["CL1", "CL2", "CL3", "CL4"],
        )
        self.assertTrue(all(not row["established"] for row in levels))
        self.assertEqual(
            levels[0]["maximum_claim_if_passed"],
            "prompted_closed_set_inner_speech_command_information_beyond_recorded_controls",
        )
        self.assertFalse(levels[2]["partial_control_replication_may_upgrade_full_claim"])
        self.assertFalse(levels[3]["known_event_onset_allowed"])
        self.assertFalse(levels[3]["known_trial_end_allowed"])

    def test_unseen_person_has_zero_adaptation_surface(self):
        level = self.program["claim_levels"][1]
        for key in (
            "held_out_person_signal_fit_rows",
            "held_out_person_target_fit_rows",
            "held_out_person_calibration_rows",
            "held_out_person_threshold_selection_rows",
            "held_out_person_adaptation_rows",
        ):
            self.assertEqual(level[key], 0)

    def test_discovery_source_has_required_recorded_controls(self):
        source = self.program["source_decision"]["discovery"]
        self.assertEqual(source["source_id"], "OpenNeuro_ds003626_v2.1.2")
        self.assertEqual(source["participants"], 10)
        self.assertEqual(source["commands"], 4)
        self.assertEqual(source["EEG_channels"], 128)
        self.assertEqual(source["horizontal_vertical_EOG_channels"], 4)
        self.assertEqual(source["oral_EMG_channels"], 2)
        self.assertTrue(source["trial_class_order_randomized"])
        self.assertTrue(source["participant_held_out_evaluation_feasible"])
        self.assertTrue(source["full_peripheral_adjusted_candidate"])
        self.assertFalse(source["payload_manifest_qualified"])
        self.assertFalse(source["payload_downloaded_by_this_record"])

    def test_no_replication_source_is_silently_promoted(self):
        decision = self.program["source_decision"]
        self.assertTrue(decision["no_full_independent_replication_source_verified_now"])
        rows = decision["replication_ranking"]
        self.assertEqual([row["rank"] for row in rows], [1, 2, 3, 4])
        self.assertTrue(
            all(not row["full_peripheral_adjusted_replication_ready"] for row in rows)
        )
        kara = rows[0]
        self.assertTrue(kara["verified_EOG"])
        self.assertTrue(kara["verified_face_tracking"])
        self.assertFalse(kara["verified_oral_EMG"])
        silent = rows[1]
        self.assertFalse(silent["public_payload_identity_and_license_verified"])
        self.assertFalse(silent["exact_peripheral_roles_verified"])

    def test_sequence_reaches_score_replication_and_live_in_order(self):
        sequence = self.program["program_sequence"]
        self.assertEqual([row["order"] for row in sequence], list(range(1, 13)))
        ids = [row["gate_id"] for row in sequence]
        self.assertEqual(ids[0], "DREYER_HL1_HL2")
        self.assertLess(
            ids.index("COMM_P1_PREDICTION_FREEZE"),
            ids.index("COMM_T1_ONE_SCORE"),
        )
        self.assertLess(
            ids.index("COMM_T1_ONE_SCORE"),
            ids.index("COMM_R0_REPLICATION_SOURCE"),
        )
        self.assertLess(
            ids.index("COMM_R1_REPLICATION_FREEZE_SCORE"),
            ids.index("NDK_STREAM1"),
        )
        self.assertEqual(ids[-1], "NDK_LIVE1")
        self.assertTrue(sequence[-1]["claim_producing"])

    def test_language_comparison_has_matched_derangement_arm(self):
        self.assertEqual(
            self.program["language_control_arms"],
            [
                "language_only",
                "neural_only",
                "neural_plus_language",
                "item_deranged_neural_plus_language",
            ],
        )

    def test_architecture_readiness_separates_reusable_and_missing(self):
        readiness = self.program["architecture_readiness"]
        self.assertIn("forward_only_stateful_preprocessing", readiness["reusable_now"])
        self.assertIn("incremental_CTC_decoding", readiness["reusable_now"])
        self.assertIn("real_device_source_adapter", readiness["missing"])
        self.assertIn("source_only_onset_and_endpointer", readiness["missing"])
        self.assertFalse(readiness["larger_or_pretrained_model_eligible_now"])

    def test_resource_policy_stays_bounded(self):
        policy = self.program["resource_policy"]
        self.assertEqual(policy["CPU_threads"], 1)
        self.assertEqual(policy["workers"], 1)
        self.assertEqual(policy["numerical_jobs"], 1)
        self.assertEqual(policy["maximum_incremental_payload_bytes"], 10 << 30)
        self.assertEqual(policy["simultaneous_real_data_lanes"], 1)
        self.assertEqual(policy["provider_calls_before_neural_prediction_freeze"], 0)
        self.assertFalse(policy["operation_outside_declared_NeuroDecodeKit_roots"])
        self.assertFalse(policy["unrelated_cleanup_or_deletion"])

    def test_every_authority_and_counter_is_zero(self):
        self.assertTrue(
            all(not value for value in self.program["authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.program["operation_counters"].values())
        )

    def test_claim_boundary_forbids_requested_upgrades_now(self):
        forbidden = set(self.program["claim_boundary"]["forbidden_current_claims"])
        self.assertTrue(
            {
                "unrestricted_thought_reading",
                "open_vocabulary_thought_to_text",
                "inner_speech_decoding",
                "EEG_beyond_EOG_or_oral_EMG",
                "unseen_person_communication_generalization",
                "independent_replication",
                "live_neural_decoding",
            }.issubset(forbidden)
        )

    def test_primary_sources_are_explicit_public_records(self):
        sources = self.program["primary_sources"]
        self.assertEqual(len(sources), 7)
        self.assertTrue(all(value.startswith("https://") for value in sources.values()))


if __name__ == "__main__":
    unittest.main()
