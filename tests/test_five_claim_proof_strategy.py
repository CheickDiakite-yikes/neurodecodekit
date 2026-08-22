import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / "five_claim_proof_strategy.v0.json"


class FiveClaimProofStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_schema_and_zero_operation_status(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.five_claim_proof_strategy",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertIn("zero_dataset_operations", self.record["status"])

    def test_all_five_claims_remain_unestablished(self):
        claims = self.record["claims"]
        self.assertEqual([claim["claim_id"] for claim in claims], ["C1", "C2", "C3", "C4", "C5"])
        self.assertTrue(all(not claim["established"] for claim in claims))

    def test_language_claim_cannot_be_promoted_to_arbitrary_thought(self):
        claim = self.record["claims"][0]
        self.assertEqual(
            claim["maximum_near_term_claim"],
            "closed_set_inner_speech_command_information",
        )
        self.assertFalse(claim["arbitrary_thought_to_text_established_by_pass"])

    def test_motor_claim_requires_spatial_temporal_and_peripheral_controls(self):
        required = set(self.record["claims"][1]["required_comparators"])
        self.assertTrue(
            {
                "timing",
                "EOG",
                "acceleration",
                "frontal_EEG",
                "occipital_EEG",
                "onset_shift",
                "temporal_reversal",
                "deranged_EEG",
            }.issubset(required)
        )

    def test_unseen_person_means_zero_target_person_adaptation(self):
        claim = self.record["claims"][2]
        for field in (
            "held_out_person_signal_fit_rows",
            "held_out_person_target_fit_rows",
            "held_out_person_calibration_rows",
            "held_out_person_threshold_selection_rows",
        ):
            self.assertEqual(claim[field], 0)

    def test_live_requires_real_stream_and_latency(self):
        claim = self.record["claims"][3]
        self.assertEqual(claim["required_stages"], ["NDK_STREAM1", "NDK_LIVE1"])
        self.assertFalse(claim["offline_replay_is_live_evidence"])
        self.assertFalse(claim["known_event_timing_allowed"])
        self.assertTrue(claim["capture_to_output_latency_required"])

    def test_peripheral_adjusted_endpoint_is_primary(self):
        claim = self.record["claims"][4]
        self.assertEqual(
            claim["primary_endpoint"],
            "participant_macro_log_loss_P_minus_P_plus_E",
        )
        self.assertEqual(
            claim["required_ordering"],
            [
                "P_plus_E_beats_P",
                "P_plus_E_beats_P_plus_deranged_E",
                "P_plus_E_beats_timing",
                "P_plus_E_beats_no_signal",
            ],
        )

    def test_execution_order_keeps_live_and_language_after_core_controls(self):
        self.assertEqual(
            self.record["execution_order"],
            [
                "MARC2_VR20P",
                "MARC2_FW2",
                "MARC2_CIL1",
                "MARC2_ZP1",
                "NDK_LANG1",
                "NDK_STREAM1",
                "NDK_LIVE1",
            ],
        )

    def test_source_decisions_do_not_promote_new_reserves(self):
        sources = self.record["source_decisions"]
        self.assertEqual(sources["movement_primary"], "Freewill_23")
        self.assertEqual(sources["language_primary"], "OpenNeuro_ds003626")
        self.assertFalse(sources["Directional_Word_2026_first_claim_eligible"])
        self.assertTrue(sources["Directional_Word_2026_block_order_confound"])
        self.assertFalse(sources["TESSCCo_exact_payload_and_control_qualification_complete"])

    def test_primary_sources_are_first_party_records(self):
        sources = self.record["primary_sources"]
        self.assertEqual(set(sources), {
            "Brain2Qwerty_article",
            "Brain2Qwerty_code",
            "Freewill_23",
            "OpenNeuro_ds003626_descriptor",
            "TESSCCo_2026",
            "Directional_Word_2026",
            "Directional_Word_2026_data",
        })
        self.assertTrue(all(
            url.startswith(("https://www.nature.com/", "https://github.com/facebookresearch/", "https://zenodo.org/"))
            for url in sources.values()
        ))

    def test_resources_remain_local_and_bounded(self):
        resources = self.record["resource_policy"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["maximum_incremental_payload_bytes"], 10 << 30)
        self.assertEqual(resources["simultaneous_real_data_tracks"], 1)
        self.assertFalse(resources["whole_Freewill_archive_allowed"])
        self.assertEqual(resources["provider_calls_before_neural_prediction_freeze"], 0)

    def test_current_gate_is_proven_but_not_authorized(self):
        gate = self.record["current_gate"]
        self.assertEqual(gate["gate_id"], "MARC2-VR20P")
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertFalse(gate["fresh_packet_bound_decision_received"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_structural_read_authorized_now"])
        self.assertFalse(gate["FW2_authorized_now"])
        self.assertFalse(gate["neural_payload_authorized_now"])

    def test_every_authority_and_access_counter_is_zero(self):
        self.assertTrue(all(not value for value in self.record["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_claim_boundary_names_every_forbidden_current_claim(self):
        forbidden = set(self.record["claim_boundary"]["forbidden_current_claims"])
        self.assertEqual(
            forbidden,
            {
                "thought_to_text",
                "motor_cortex_specific_decoding",
                "unseen_person_generalization",
                "live_neural_decoding",
                "EEG_advantage_beyond_peripheral_controls",
            },
        )


if __name__ == "__main__":
    unittest.main()
