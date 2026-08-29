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
            "HL2_packet_bound_decision_recorded_pending_own_remote_green",
        )

    def test_scientific_strategy_converges_on_one_empirical_checkpoint(self):
        strategy = self.frontier["scientific_strategy"]
        self.assertEqual(strategy["flagship_experiment"], "EXP-DREYER-C5R-1")
        self.assertEqual(
            strategy["first_empirical_checkpoint"],
            "one_exact_sub_01_R1_EDF_fixed_header_sensor_and_sampling_observation",
        )
        self.assertEqual(
            strategy["portfolio_allocation_percent"],
            {"flagship": 70, "adjacent_diagnostic": 20, "moonshot": 10},
        )
        self.assertEqual(
            strategy["COMM_P0_G_FS3_status"],
            "paused_adjacent_engineering_diagnostic",
        )
        self.assertFalse(strategy["authority_changed"])
        self.assertEqual(strategy["new_real_or_private_operations"], 0)
        self.assertEqual(strategy["new_model_or_score_operations"], 0)
        for path_key in ("constitution", "convergence_plan", "knowledge_ledger"):
            self.assertTrue((ROOT / strategy[path_key]).is_file(), path_key)

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
        self.assertTrue(packet["request_all_authority_flags_false"])
        self.assertTrue(packet["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(packet["current_HL2_authority"])
        decision = packet["packet_bound_decision"]
        self.assertEqual(decision["maintainer_words"], "continue, make a deep push")
        self.assertEqual(
            decision["commit"],
            "de6cf80f4bd243e7e60a6933445d0a65291abb90",
        )
        self.assertEqual(decision["CI_run_id"], 33_230_243_142)
        self.assertTrue(decision["both_required_jobs_green"])
        self.assertTrue(decision["decision_effective_now"])
        self.assertEqual(decision["decision_only_real_or_private_operations"], 0)
        qualification = packet["HL1_generated_qualification"]
        self.assertEqual(
            qualification["status"],
            "consumed_rejected_post_run_failure_cleanup_gate",
        )
        self.assertFalse(qualification["all_acceptance_gates_passed"])
        self.assertFalse(qualification["rerun_allowed"])
        self.assertEqual(qualification["real_or_private_operations"], 0)
        proof = packet["HL1_generated_qualification_proof"]
        self.assertEqual(
            proof["commit"], "a70fda0a808751c6057ed07117b7d22ee715a273"
        )
        self.assertEqual(proof["CI_run_id"], 33_233_017_769)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["qualification_reruns"], 0)
        recovery = packet["queued_HL1R1_recovery_request"]
        self.assertEqual(recovery["packet_id"], "DREYER-C5R-1-HL1R1")
        self.assertEqual(
            recovery["request_commit"],
            "0152fa5417f85c54d8c022634e73bee69bc8ef70",
        )
        self.assertEqual(recovery["request_CI_run_id"], 33_233_829_570)
        self.assertTrue(recovery["request_both_required_jobs_green"])
        self.assertTrue(recovery["request_on_GitHub_main"])
        self.assertTrue(recovery["all_authority_flags_false"])
        self.assertFalse(recovery["fresh_packet_bound_maintainer_decision_required"])
        self.assertTrue(recovery["fresh_packet_bound_maintainer_decision_recorded"])
        self.assertFalse(recovery["predating_short_form_may_activate"])
        self.assertEqual(recovery["requested_successor_refusal_cases"], 43)
        self.assertEqual(recovery["real_or_private_operations"], 0)
        request_proof = recovery["proof_only_closeout"]
        self.assertEqual(request_proof["proof_id"], "DREYER-C5R-1-HL1R1-P0")
        self.assertEqual(
            request_proof["commit"],
            "8868a0866fd8f31bf7ba435e94b1b619314910ec",
        )
        self.assertEqual(request_proof["CI_run_id"], 33_234_406_143)
        self.assertTrue(request_proof["both_required_jobs_green"])
        self.assertEqual(request_proof["implementation_or_execution_operations"], 0)
        self.assertFalse(request_proof["authority_expanded"])
        recovery_decision = recovery["packet_bound_decision"]
        self.assertEqual(recovery_decision["maintainer_words"], "continue")
        self.assertEqual(
            recovery_decision["status"],
            "remotely_green_implementation_authority_active",
        )
        self.assertEqual(
            recovery_decision["commit"],
            "eaff077fc14b10886a6c26f45318ae649765e76d",
        )
        self.assertEqual(recovery_decision["CI_run_id"], 33_247_816_266)
        self.assertTrue(recovery_decision["both_required_jobs_green"])
        self.assertTrue(recovery_decision["decision_effective_now"])
        self.assertTrue(
            recovery_decision["implementation_authority_after_remote_green"]
        )
        self.assertFalse(recovery_decision["registered_qualification_authority"])
        self.assertFalse(recovery_decision["HL2_authority"])
        self.assertEqual(recovery_decision["real_or_private_operations"], 0)
        implementation = recovery["generated_recovery_implementation"]
        self.assertEqual(implementation["implementation_id"], "DREYER-C5R-1-HL1R1-I0")
        self.assertEqual(
            implementation["status"],
            "remotely_green_generated_only_qualification_inactive",
        )
        self.assertEqual(
            implementation["commit"],
            "6a0bc7749dd6c36b4d8db019cc6e78acf653c83d",
        )
        self.assertEqual(implementation["CI_run_id"], 33_249_178_006)
        self.assertTrue(implementation["both_required_jobs_green"])
        self.assertTrue(implementation["on_GitHub_main"])
        self.assertEqual(implementation["focused_tests"], 9)
        self.assertEqual(implementation["focused_subtests"], 43)
        self.assertEqual(implementation["ordered_failure_identities_passed"], 43)
        self.assertEqual(implementation["registered_qualification_runs"], 0)
        self.assertFalse(implementation["qualification_command_exposed"])
        self.assertFalse(implementation["real_command_exposed"])
        self.assertEqual(implementation["real_or_private_operations"], 0)
        implementation_proof = recovery["generated_recovery_implementation_proof"]
        self.assertEqual(
            implementation_proof["proof_id"],
            "DREYER-C5R-1-HL1R1-I0-P0",
        )
        self.assertEqual(implementation_proof["bound_artifacts"], 6)
        self.assertEqual(implementation_proof["bound_bytes"], 69_368)
        self.assertEqual(
            implementation_proof["canonical_artifact_set_sha256"],
            "b70a95b12bd80e7703e0a1c109c5be734ad278892653ba7336aee472ab4708ed",
        )
        self.assertEqual(
            implementation_proof["commit"],
            "41644a55ada938b0d1d3a042264e8c0b7a48384b",
        )
        self.assertEqual(implementation_proof["CI_run_id"], 33_249_903_090)
        self.assertTrue(implementation_proof["both_required_jobs_green"])
        self.assertEqual(implementation_proof["registered_qualification_runs"], 0)
        self.assertEqual(implementation_proof["real_or_private_operations"], 0)
        self.assertFalse(implementation_proof["authority_expanded"])
        activation_request = recovery["queued_qualification_authorization_request"]
        self.assertEqual(
            activation_request["request_id"],
            "DREYER-C5R-1-HL1R1-QA0",
        )
        self.assertEqual(
            activation_request["status"],
            "qualification_passed_consumed_result_closeout_pending_remote_green",
        )
        self.assertEqual(
            activation_request["bound_green_implementation_proof_commit"],
            "41644a55ada938b0d1d3a042264e8c0b7a48384b",
        )
        self.assertTrue(activation_request["all_authority_flags_false"])
        self.assertEqual(
            activation_request["commit"],
            "0213e7050dd845de16b5f1abac4573f30b534452",
        )
        self.assertEqual(activation_request["CI_run_id"], 33_250_382_778)
        self.assertTrue(activation_request["both_required_jobs_green"])
        self.assertTrue(activation_request["on_GitHub_main"])
        self.assertTrue(
            activation_request["fresh_packet_bound_maintainer_decision_required"]
        )
        self.assertFalse(activation_request["predating_short_form_may_activate"])
        self.assertEqual(activation_request["registered_qualification_runs"], 0)
        self.assertEqual(activation_request["real_or_private_operations"], 0)
        self.assertFalse(activation_request["authority_expanded"])
        activation_proof = activation_request["proof_only_closeout"]
        self.assertEqual(
            activation_proof["proof_id"],
            "DREYER-C5R-1-HL1R1-QA0-P0",
        )
        self.assertEqual(activation_proof["bound_artifacts"], 3)
        self.assertEqual(activation_proof["bound_bytes"], 13_443)
        self.assertEqual(
            activation_proof["commit"],
            "d1c003f303083d23685da858bca069397b1f9c58",
        )
        self.assertEqual(activation_proof["CI_run_id"], 33_250_971_717)
        self.assertTrue(activation_proof["both_required_jobs_green"])
        self.assertEqual(activation_proof["registered_qualification_runs"], 0)
        self.assertEqual(activation_proof["real_or_private_operations"], 0)
        self.assertFalse(activation_proof["authority_expanded"])
        qualification_decision = activation_request["packet_bound_decision"]
        self.assertEqual(
            qualification_decision["decision_id"],
            "DREYER-C5R-1-HL1R1-QA0-D0",
        )
        self.assertEqual(qualification_decision["maintainer_words"], "continue")
        self.assertEqual(
            qualification_decision["status"],
            "remotely_green_coordinator_and_one_post_green_qualification_authorized",
        )
        self.assertEqual(
            qualification_decision["commit"],
            "749fd5695441350d8cc949af19b6ad4bb5863dba",
        )
        self.assertEqual(qualification_decision["CI_run_id"], 33_251_731_156)
        self.assertTrue(qualification_decision["both_required_jobs_green"])
        self.assertTrue(qualification_decision["decision_effective_now"])
        self.assertTrue(
            qualification_decision["coordinator_authority_after_remote_green"]
        )
        self.assertTrue(
            qualification_decision[
                "one_registered_qualification_after_coordinator_green"
            ]
        )
        self.assertFalse(qualification_decision["HL2_authority"])
        self.assertEqual(qualification_decision["real_or_private_operations"], 0)
        coordinator = qualification_decision["generated_qualification_coordinator"]
        self.assertEqual(coordinator["implementation_id"], "DREYER-C5R-1-HL1R1-QI0")
        self.assertEqual(
            coordinator["commit"],
            "0ef634e4852d9f8a18d4b8a1f50e6a1331bd020a",
        )
        self.assertEqual(coordinator["CI_run_id"], 33_253_657_120)
        self.assertEqual(coordinator["development_matrix_cases_passed"], 65)
        self.assertEqual(coordinator["registered_qualification_attempts"], 0)
        self.assertEqual(coordinator["real_or_private_operations"], 0)
        self.assertFalse(coordinator["HL2_authority"])
        result = coordinator["registered_qualification_result"]
        self.assertEqual(result["result_id"], "DREYER-C5R-1-HL1R1-Q0-R0")
        self.assertEqual(result["matrix_cases_passed"], 65)
        self.assertEqual(result["registered_attempts_consumed"], 1)
        self.assertFalse(result["rerun_allowed"])
        self.assertEqual(result["real_or_private_operations"], 0)
        green = result["result_closeout_green"]
        self.assertEqual(
            green["commit"], "cb7e7f831a1056dfcf878ca23ed53aa6fd4738dc"
        )
        self.assertEqual(green["CI_run_id"], 33_254_474_440)
        self.assertTrue(green["both_required_jobs_green"])
        proof = result["result_proof"]
        self.assertEqual(proof["proof_id"], "DREYER-C5R-1-HL1R1-Q0-R0-P0")
        self.assertEqual(proof["bound_artifact_count"], 3)
        self.assertEqual(proof["bound_artifact_bytes"], 13_827)
        self.assertEqual(
            proof["commit"], "1ae340354352d544d6d99fe5af6f354ab668bf9c"
        )
        self.assertEqual(proof["CI_run_id"], 33_255_170_805)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["qualification_repeated"])
        self.assertFalse(proof["ignored_evidence_reopened"])
        self.assertEqual(proof["real_or_private_operations"], 0)
        self.assertFalse(proof["HL2_authority"])
        request = packet["queued_HL2_activation_request"]
        self.assertEqual(request["request_id"], "DREYER-C5R-1-HL2-A0")
        self.assertEqual(
            request["status"],
            "request_only_all_authority_false_remotely_green_proof_pending_own_remote_green",
        )
        self.assertEqual(
            request["commit"], "a97fc191106e5fe42859d871d78e59930bef79ac"
        )
        self.assertEqual(request["CI_run_id"], 33_255_920_346)
        self.assertEqual(request["base_python_job_id"], 99_109_482_999)
        self.assertEqual(
            request["optional_neuro_readers_job_id"], 99_109_482_995
        )
        self.assertTrue(request["both_required_jobs_green"])
        self.assertTrue(request["on_GitHub_main"])
        self.assertTrue(request["all_authority_flags_false"])
        self.assertTrue(request["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(request["predating_short_form_may_activate"])
        self.assertEqual(request["requested_member_bytes"], 14_805_604)
        self.assertEqual(request["requested_real_HTTP_GET_requests"], 1)
        self.assertEqual(request["requested_fixed_header_parses"], 1)
        self.assertEqual(request["requested_remaining_payloads"], 0)
        self.assertEqual(request["real_or_private_operations"], 0)
        self.assertFalse(request["authority_expanded"])
        proof = request["request_proof"]
        self.assertEqual(proof["proof_id"], "DREYER-C5R-1-HL2-A0-P0")
        self.assertEqual(
            proof["commit"], "036a9ec7e78b460d464c3349151ddb0e35914d87"
        )
        self.assertEqual(proof["CI_run_id"], 33_257_159_816)
        self.assertEqual(proof["base_python_job_id"], 99_112_795_545)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 99_112_795_525)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertTrue(proof["on_GitHub_main"])
        self.assertEqual(proof["bound_artifact_count"], 3)
        self.assertEqual(proof["bound_artifact_bytes"], 18_035)
        self.assertEqual(
            proof["canonical_artifact_set_sha256"],
            "d0d0de3cbd7c448852ebdfcb28dc7e3dc2c561307cba164d2be3629f2756382e",
        )
        self.assertFalse(proof["decision_recorded"])
        self.assertTrue(
            proof["fresh_packet_bound_maintainer_words_required_after_proof_green"]
        )
        self.assertFalse(proof["predating_maintainer_words_may_activate"])
        self.assertFalse(proof["HL2_authority"])
        self.assertFalse(proof["real_EDF_access_allowed"])
        decision = request["packet_bound_decision"]
        self.assertEqual(decision["decision_id"], "DREYER-C5R-1-HL2-A0-D0")
        self.assertEqual(decision["maintainer_words"], "continue")
        self.assertEqual(decision["bound_artifact_count"], 6)
        self.assertEqual(decision["bound_artifact_bytes"], 27_477)
        self.assertEqual(decision["fresh_CI_verification_calls"], 1)
        self.assertFalse(decision["effective_before_own_remote_green"])
        self.assertFalse(decision["HL2_authority_before_all_barriers"])
        self.assertFalse(decision["real_EDF_access_allowed_before_all_barriers"])
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
