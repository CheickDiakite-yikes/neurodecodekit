import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc2_confound_triangulation_research.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2ConfoundTriangulationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_schema_identity_and_tier_a_status(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_confound_triangulation_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["research_id"],
            "MARC-2-confound-triangulation-and-language-bridge-research-v0",
        )
        self.assertEqual(
            self.record["status"],
            "tier_A_primary_source_research_complete_zero_dataset_operations",
        )

    def test_artifact_bindings_are_current(self):
        for binding in self.record["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_wrist_predecessor_is_consumed_and_cannot_be_repaired(self):
        predecessor = self.record["blocked_predecessor"]
        self.assertEqual(predecessor["route"], "MARC1SAL-R2")
        self.assertTrue(predecessor["consumed"])
        self.assertFalse(predecessor["selected_cohort_available"])
        self.assertEqual(predecessor["payload_bytes"], 0)
        for operation in ("retry", "rerun", "resume", "repair", "route_around"):
            self.assertFalse(predecessor["allowed_operations"][operation])

    def test_five_work_orders_are_exact_and_ordered(self):
        work_orders = self.record["five_work_orders"]
        self.assertEqual(
            [item["work_order_id"] for item in work_orders],
            ["MARC2-FW1", "MARC2-FW2", "MARC2-CIL1", "MARC2-ORTH1", "NDK-LANG1"],
        )
        self.assertEqual([item["ordinal"] for item in work_orders], [1, 2, 3, 4, 5])
        self.assertEqual(work_orders[0]["current_eligibility"], "contract_design_only")
        for item in work_orders[1:]:
            self.assertEqual(item["current_eligibility"], "closed")

    def test_freewill_is_primary_and_whole_archive_is_forbidden(self):
        freewill = self.record["source_matrix"]["freewill_23"]
        self.assertEqual(freewill["role"], "primary_cue_reduced_axis")
        self.assertEqual(freewill["license"], "CC BY 4.0")
        self.assertEqual(freewill["participants"], 23)
        self.assertEqual(freewill["trials"], 6808)
        self.assertEqual(freewill["EOG_channels"], 4)
        self.assertEqual(freewill["accelerometer_axes"], 3)
        self.assertFalse(freewill["target_specific_cue"])
        self.assertFalse(freewill["whole_archive_eligible"])
        self.assertEqual(freewill["archive_bytes"], 13_591_548_048)

    def test_orthogonal_candidates_have_distinct_roles(self):
        sources = self.record["source_matrix"]
        biomed = sources["biomed_spc_9"]
        gait = sources["physionet_gait_59"]
        self.assertEqual(biomed["role"], "complete_peripheral_control_candidate")
        self.assertTrue(biomed["EOG_available"])
        self.assertTrue(biomed["EMG_available"])
        self.assertTrue(biomed["kinematics_available"])
        self.assertTrue(biomed["target_specific_cue"])
        self.assertEqual(gait["role"], "held_out_person_scale_reserve")
        self.assertEqual(gait["participants"], 59)
        self.assertFalse(gait["EOG_available"])
        self.assertTrue(gait["EMG_available"])
        self.assertTrue(gait["kinematics_available"])
        self.assertTrue(gait["force_available"])

    def test_way_reference_warns_against_fused_model_attribution(self):
        way = self.record["source_matrix"]["way_eeg_gal_reference"]
        self.assertFalse(way["execution_candidate"])
        self.assertEqual(way["reported_EEG_only_result"], "near_chance")
        self.assertEqual(way["reported_dominant_modality"], "EMG")
        self.assertEqual(way["payload_authorized"], False)

    def test_inner_speech_source_has_required_control_channels(self):
        source = self.record["source_matrix"]["inner_speech_10"]
        self.assertEqual(source["role"], "future_language_control_source")
        self.assertEqual(source["participants"], 10)
        self.assertEqual(source["EEG_channels"], 128)
        self.assertEqual(source["EOG_channels"], 4)
        self.assertEqual(source["oral_EMG_channels"], 2)
        self.assertEqual(source["command_classes"], 4)
        self.assertEqual(
            source["conditions"],
            ["inner_speech", "pronounced_speech", "visualized_direction"],
        )
        self.assertFalse(source["payload_authorized"])

    def test_conditional_information_ladder_is_complete(self):
        ladder = self.record["conditional_information_ladder"]
        self.assertEqual(
            ladder["ordered_conditions"],
            ["B0", "B1", "P", "E", "P_plus_E", "P_plus_deranged_E"],
        )
        self.assertEqual(
            ladder["primary_endpoint"],
            "participant_macro_log_loss_P_minus_P_plus_E",
        )
        self.assertFalse(ladder["pooled_trial_accuracy_primary"])
        self.assertTrue(ladder["positive_conditional_gain_required"])
        self.assertTrue(ladder["participant_level_paired_inference_required"])

    def test_candidate_families_are_compact_and_not_final_selected(self):
        families = self.record["candidate_families"]
        self.assertEqual(set(families), {"H_LF", "H_SMR", "H_CML"})
        self.assertEqual(families["H_LF"]["frequency_band_hz"], [0.5, 4.0])
        self.assertTrue(families["H_LF"]["causal"])
        self.assertTrue(families["H_SMR"]["causal"])
        self.assertLessEqual(families["H_CML"]["parameter_ceiling"], 10_000)
        for family in families.values():
            self.assertFalse(family["final_target_family_selection_allowed"])
            self.assertFalse(family["pretrained_model_allowed"])

    def test_target_firewall_requires_remote_green_freeze(self):
        firewall = self.record["target_firewall"]
        self.assertEqual(
            firewall["physical_deliveries"],
            [
                "fit_signals_controls_onsets_and_targets",
                "held_out_target_blind_signals",
                "held_out_target_blind_timing_and_controls",
                "one_final_held_out_target_delivery",
            ],
        )
        self.assertTrue(firewall["remote_green_prediction_freeze_required"])
        self.assertEqual(firewall["post_target_updates"], 0)
        self.assertEqual(firewall["reruns_after_scoring"], 0)

    def test_language_model_is_downstream_and_must_beat_controls(self):
        language = self.record["language_bridge_policy"]
        self.assertFalse(language["eligible_now"])
        self.assertTrue(language["neural_prediction_freeze_first"])
        self.assertEqual(
            language["matched_conditions"],
            [
                "neural_only",
                "language_model_only",
                "language_model_plus_neural",
                "language_model_plus_item_deranged_neural",
            ],
        )
        self.assertTrue(language["must_beat_language_model_only"])
        self.assertTrue(language["must_beat_deranged_neural"])
        self.assertFalse(language["four_command_result_is_thought_to_text"])

    def test_storage_and_compute_caps_are_small(self):
        resources = self.record["resource_policy"]
        self.assertEqual(resources["maximum_incremental_payload_bytes"], 8 << 30)
        self.assertEqual(resources["minimum_free_disk_bytes"], 15 << 30)
        self.assertEqual(resources["private_derivative_cap_bytes"], 64 << 20)
        self.assertEqual(resources["aggregate_output_cap_bytes"], 1 << 20)
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["provider_budget_USD"], 0.0)

    def test_current_authority_and_access_are_all_zero(self):
        for value in self.record["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.record["access_counters"].values():
            self.assertEqual(value, 0)

    def test_claim_boundary_is_explicit(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("conditional contribution", boundary["engineering_capability_added"])
        self.assertIn("no new neural", boundary["scientific_claim_not_established"])
        self.assertIn("scalp-sensor", boundary["future_movement_ceiling"])
        self.assertFalse(boundary["free_form_thought_to_text_established"])
        for forbidden in ("brain-specific", "thought-to-text", "clinical"):
            self.assertIn(forbidden, boundary["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
