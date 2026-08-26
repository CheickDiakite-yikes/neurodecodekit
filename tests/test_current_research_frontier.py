import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/current_research_frontier.v0.json"


class CurrentResearchFrontierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frontier = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_active_lane_are_exact(self):
        self.assertEqual(
            self.frontier["schema_name"],
            "neurodecodekit.current_research_frontier",
        )
        self.assertEqual(self.frontier["schema_version"], "0.1.0")
        self.assertEqual(self.frontier["active_lane_id"], "DREYER-C5R-1-HL")
        self.assertEqual(
            self.frontier["status"],
            "all_false_request_and_proof_remotely_green_awaiting_exact_Tier_C_decision",
        )

    def test_proof_chain_records_green_recovery_activation(self):
        proof = self.frontier["completed_proof"]
        self.assertEqual(
            proof["G1_proof_closeout_commit"],
            "cf476982d70cbd6c710b7d0a67352765155c6bc1",
        )
        self.assertEqual(
            proof["redirect_recovery_implementation_commit"],
            "09a19d1c1c498bdd6e0ece2fbecb6d15917bdefa",
        )
        self.assertEqual(
            proof["redirect_recovery_activation_commit"],
            "492a36a818bb00ca6bb86de6592c6cd0d5134f90",
        )
        self.assertEqual(proof["redirect_recovery_activation_CI_run_id"], 32_807_676_008)
        self.assertTrue(proof["both_activation_jobs_green"])
        self.assertEqual(
            proof["Stage_A_result_commit"],
            "96d7f0569a54b05f8031d2e3943658ef598e38a5",
        )
        self.assertTrue(proof["both_Stage_A_result_jobs_green"])
        self.assertEqual(
            proof["Stage_Q_implementation_commit"],
            "e5ca6a24f65beab12b89eddad938c96fe4ecaf00",
        )
        self.assertTrue(proof["both_Stage_Q_implementation_jobs_green"])
        self.assertEqual(
            proof["first_Stage_Q_activation_commit"],
            "e67809593de548bf8dd2afb1f1298b7a2c9b26eb",
        )
        self.assertFalse(proof["first_Stage_Q_activation_green"])
        self.assertEqual(proof["first_Stage_Q_activation_private_operations"], 0)
        self.assertEqual(
            proof["Stage_Q_compatibility_commit"],
            "52b681ed7ec3991527f04f2fc555452d2246c481",
        )
        self.assertTrue(proof["both_Stage_Q_compatibility_jobs_green"])
        self.assertEqual(
            proof["Stage_Q_activation_commit"],
            "0e36993fb3b4e0651d53d62818df672c5ed5f04b",
        )
        self.assertTrue(proof["both_Stage_Q_activation_jobs_green"])
        self.assertEqual(
            proof["Stage_Q_result_commit"],
            "9832ae5e60c42bf975ccfdd22740267ef802d191",
        )
        self.assertTrue(proof["both_Stage_Q_result_jobs_green"])
        self.assertEqual(
            proof["Stage_P_T_implementation_commit"],
            "7ba4f7c30f260bc7603e8928ad8d9ff010e54872",
        )
        self.assertEqual(proof["Stage_P_T_implementation_CI_run_id"], 32_906_104_408)
        self.assertTrue(proof["both_Stage_P_T_implementation_jobs_green"])
        self.assertEqual(
            proof["Stage_P_activation_commit"],
            "a49609b77fb9407f7c8ea8368c72b84c03fc446c",
        )
        self.assertEqual(proof["Stage_P_activation_CI_run_id"], 32_906_928_931)
        self.assertTrue(proof["both_Stage_P_activation_jobs_green"])
        self.assertEqual(
            proof["Stage_P_prediction_freeze_commit"],
            "2517fd16e7bf4cca077c46686320fe26c992ed69",
        )
        self.assertEqual(proof["Stage_P_prediction_freeze_CI_run_id"], 32_908_059_166)
        self.assertTrue(proof["both_Stage_P_prediction_freeze_jobs_green"])
        self.assertEqual(
            proof["Stage_T_activation_commit"],
            "06e29cb094e67e9c946012f2aa716ea510501251",
        )
        self.assertEqual(proof["Stage_T_activation_CI_run_id"], 32_908_763_353)
        self.assertTrue(proof["both_Stage_T_activation_jobs_green"])
        self.assertEqual(
            proof["Stage_T_result_commit"],
            "af8dcc998b5b5eb6bda3ecae1c9e6c787fabc0f2",
        )
        self.assertEqual(proof["Stage_T_result_CI_run_id"], 32_909_763_799)
        self.assertTrue(proof["both_Stage_T_result_jobs_green"])

    def test_prelaunch_rejection_did_not_consume_recovery(self):
        rejection = self.frontier["prelaunch_rejection"]
        self.assertFalse(rejection["process_created"])
        self.assertFalse(rejection["replacement_recovery_invocation_consumed"])
        for key in (
            "manifest_requests",
            "payload_requests",
            "network_body_bytes",
            "accepted_payload_bytes",
            "recovery_marker_writes",
            "ignored_path_operations",
            "MAT_semantic_opens",
            "model_runs",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(rejection[key], 0, key)

    def test_recovery_resources_and_stage_order_are_frozen(self):
        envelope = self.frontier["active_Stage_Q_envelope"]
        self.assertEqual(envelope["registered_invocations_remaining_after_activation"], 0)
        self.assertEqual(envelope["MAT_content_opens_maximum"], 18)
        self.assertEqual(envelope["CPU_threads"], 1)
        self.assertEqual(envelope["workers"], 1)
        self.assertEqual(envelope["reruns"], 0)
        self.assertEqual(
            self.frontier["historical_BNCI_evidence_sequence"],
            [
                "G1_generated_proof",
                "A_opaque_acquisition",
                "Q_target_blind_validation",
                "P_target_firewalled_prediction_freeze",
                "T_one_frozen_score",
            ],
        )
        result = self.frontier["Stage_A_recovery_result"]
        self.assertEqual(result["payload_files"], 18)
        self.assertEqual(result["accepted_payload_bytes"], 779_873_919)
        self.assertEqual(result["MAT_semantic_opens"], 0)
        self.assertEqual(result["model_runs"], 0)
        self.assertEqual(result["scores"], 0)
        generated = self.frontier["Stage_Q_generated_qualification_result"]
        self.assertEqual(generated["generated_trials"], 288)
        self.assertEqual(generated["real_or_private_path_opens"], 0)
        self.assertEqual(generated["model_runs"], 0)
        live_result = self.frontier["Stage_Q_live_result"]
        self.assertEqual(live_result["MAT_files"], 18)
        self.assertEqual(live_result["task_runs"], 108)
        self.assertEqual(live_result["trials"], 5_184)
        self.assertEqual(live_result["scores"], 0)
        stage_p_result = self.frontier["Stage_P_live_result"]
        self.assertEqual(stage_p_result["parameter_update_fits"], 468)
        self.assertEqual(stage_p_result["prediction_sets"], 495)
        self.assertEqual(stage_p_result["private_prediction_rows"], 41_472)
        self.assertEqual(stage_p_result["target_deliveries"], 0)
        self.assertEqual(stage_p_result["scores"], 0)
        stage_t_result = self.frontier["Stage_T_live_result"]
        self.assertEqual(stage_t_result["route"], "BNCIC3C5-R2")
        self.assertFalse(stage_t_result["C3_passed"])
        self.assertFalse(stage_t_result["C5_partial_passed"])
        self.assertEqual(stage_t_result["target_deliveries"], 1)
        self.assertEqual(stage_t_result["scores"], 1)
        self.assertEqual(stage_t_result["reruns"], 0)

    def test_fresh_replication_and_active_preflight_are_exact(self):
        self.assertEqual(
            self.frontier["evidence_sequence"],
            [
                "D_aggregate_only_BNCI_failure_localization",
                "R_fresh_cohort_primary_source_selection",
                "C_stronger_control_preregistration",
                "G_generated_model_firewall_and_scorer_qualification",
                "H_generated_one_file_sensor_preflight_qualification",
                "HL_packet_bound_authorization_decision",
                "HL1_generated_live_wrapper_qualification_and_activation",
                "HL2_one_real_EDF_header_preflight",
            ],
        )
        fresh = self.frontier["fresh_replication"]
        self.assertEqual(fresh["cohort"]["participants"], 60)
        self.assertEqual(fresh["cohort"]["files"], 120)
        self.assertEqual(fresh["cohort"]["declared_payload_bytes"], 1_779_763_388)
        self.assertFalse(fresh["cohort"]["source_EDF_sensor_roster_verified"])
        self.assertEqual(fresh["frozen_protocol"]["outer_folds"], 60)
        self.assertEqual(
            fresh["frozen_protocol"]["real_parameter_update_fits_planned"], 4740
        )
        self.assertTrue(fresh["frozen_protocol"]["producer_causal"])
        packet = fresh["active_Tier_C_packet"]
        self.assertEqual(packet["packet_id"], "DREYER-C5R-1-HL")
        self.assertEqual(
            packet["proof_closeout_commit"],
            "821fad17e06914375c50a7d0dd7017458b2df838",
        )
        self.assertEqual(packet["proof_closeout_CI_run_id"], 32_936_247_679)
        self.assertTrue(packet["both_request_and_proof_required_jobs_green"])
        self.assertTrue(packet["all_authority_flags_false"])
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
            self.assertEqual(packet[key], 0, key)

    def test_all_five_scientific_goals_and_claims_remain_unestablished(self):
        self.assertEqual(
            set(self.frontier["five_scientific_goals"].values()),
            {"not_established"},
        )
        claims = self.frontier["claim_boundary"]
        for key, value in claims.items():
            if key not in {
                "engineering_capability_established",
                "verified_recovery_bundle_acquired",
                "real_MAT_semantics_validated",
                "real_neural_model_run",
                "scientific_score_produced",
                "real_held_out_scoring_completed",
                "candidate_EEG_beats_no_signal_and_timing_macro",
                "fresh_replication_design_frozen",
                "generated_model_and_firewall_qualified",
                "generated_sensor_preflight_qualified",
            }:
                self.assertFalse(value, key)
        self.assertTrue(claims["verified_recovery_bundle_acquired"])
        self.assertTrue(claims["real_MAT_semantics_validated"])
        self.assertTrue(claims["real_neural_model_run"])
        self.assertTrue(claims["scientific_score_produced"])
        self.assertTrue(claims["real_held_out_scoring_completed"])
        self.assertTrue(claims["candidate_EEG_beats_no_signal_and_timing_macro"])
        self.assertTrue(claims["fresh_replication_design_frozen"])
        self.assertTrue(claims["generated_model_and_firewall_qualified"])
        self.assertTrue(claims["generated_sensor_preflight_qualified"])
        self.assertFalse(claims["registered_C3_passed"])
        self.assertFalse(claims["registered_C5_partial_passed"])
        self.assertFalse(claims["real_Dreyer_EEG_accessed"])

    def test_control_plane_entrypoints_name_the_current_gate(self):
        expected = {
            "AGENTS.md": "DREYER-C5R-1-HL",
            "START_HERE.md": "Current Gate: DREYER-C5R-1-HL One-File Sensor Preflight",
            "README.md": "DREYER-C5R-1",
            "docs/CODEX_HANDOFF.md": "Current gate, 2026-08-26",
            "docs/NEXT_20_LOOPS_TRACKER.md": "DREYER-C5R-1 frontier",
        }
        for path, phrase in expected.items():
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn(phrase, text, path)
        start = (ROOT / "START_HERE.md").read_text(encoding="utf-8")[:8_000]
        self.assertNotIn("Current Gate: BNCI-C3C5-1", start)


if __name__ == "__main__":
    unittest.main()
