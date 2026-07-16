import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries" / "loop48_train_only_discrimination_result.v0.json"
FREEZE_PATH = REPO_ROOT / "registries" / "loop48_stage_b_prediction_freeze.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_train_only_discrimination_contract.v0.json"
DECISION_PATH = REPO_ROOT / "registries" / "loop48_stage_b_authorization_decision.v0.json"
CLOSEOUT_PATH = REPO_ROOT / "docs" / "LOOP_48_STAGE_B_RESULT.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
RESULT_SHA256 = "ef8290eb45e755bedb2deed781e6e472aa3621c25d91a01d01626c17c96ce891"
FREEZE_SHA256 = "2c14d25d92dbd93677515136365f9b229fbbdfaf7086fe77a36469f43085e65f"


class Loop48StageBResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.freeze_bytes = FREEZE_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)
        cls.freeze = json.loads(cls.freeze_bytes)
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.closeout = CLOSEOUT_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))

    def test_result_and_freeze_identities_are_exact(self):
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), RESULT_SHA256)
        self.assertEqual(hashlib.sha256(self.freeze_bytes).hexdigest(), FREEZE_SHA256)
        self.assertEqual(len(self.result_bytes), 174849)
        self.assertEqual(len(self.freeze_bytes), 171971)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.loop48_stage_b_failure_discrimination_score",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["status"], "completed_registered_diagnostic_no_rerun")
        self.assertEqual(self.result["maximum_evidence_level"], "E2_pipeline_discriminative")

    def test_contract_authorization_and_remote_green_freeze_bindings_are_exact(self):
        self.assertEqual(
            self.result["contract_sha256"],
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(
            self.result["authorization_decision_sha256"],
            hashlib.sha256(DECISION_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(self.result["prediction_freeze_sha256"], FREEZE_SHA256)
        self.assertEqual(
            self.result["green_prediction_freeze"],
            {
                "commit": "00215b1f43183ff0c832bf7ba63bbd699d4a4c7b",
                "operator_confirmed_both_runs_green_before_target_delivery": True,
                "pr_ci_run_id": 29461935560,
                "push_ci_run_id": 29461934145,
            },
        )
        self.assertEqual(
            self.freeze["implementation_commit"],
            "1d840e3eb10a68f25381bde16595f7d62fd515bb",
        )
        self.assertEqual(self.result["contract_sha256"], self.freeze["contract_sha256"])
        self.assertEqual(
            self.result["authorization_decision_sha256"],
            self.freeze["authorization_decision_sha256"],
        )

    def test_access_order_and_one_shot_ledger_are_exact(self):
        counters = self.result["access_counters"]
        expected = {
            "candidate_training_runs": 15,
            "linear_training_runs": 3,
            "control_training_runs": 2,
            "optimizer_steps": 4800,
            "target_blind_model_inference_runs": 35,
            "no_signal_prior_fits": 5,
            "prediction_sets_frozen": 41,
            "check_scoring_runs": 1,
            "check_signal_rows_delivered": 11,
            "check_target_rows_delivered_before_green_freeze": 0,
            "check_target_rows_delivered_after_green_freeze": 11,
            "fit_signal_rows_delivered": 44,
            "fit_target_rows_delivered": 44,
            "source_cache_hash_passes": 1,
            "validation_signal_rows_delivered": 0,
            "validation_target_rows_delivered": 0,
            "source_test_signal_rows_delivered": 0,
            "source_test_target_rows_delivered": 0,
            "session2_rows_delivered": 0,
            "raw_fif_or_mat_reads": 0,
            "new_download_bytes": 0,
            "network_calls": 0,
            "post_check_configuration_changes": 0,
            "post_check_parameter_updates": 0,
            "reruns": 0,
        }
        for key, value in expected.items():
            self.assertEqual(counters[key], value, key)
        self.assertEqual(self.result["check_target_delivery_events"], 1)
        self.assertEqual(self.result["validation_rows_delivered_or_scored"], 0)
        self.assertEqual(self.result["source_test_rows_delivered_or_scored"], 0)
        self.assertEqual(self.result["session2_rows_delivered_or_scored"], 0)

    def test_primary_candidate_loses_to_the_train_only_prior(self):
        self.assertEqual(self.result["primary_candidate"], "candidate_size44_seed4801")
        self.assertEqual(self.result["primary_prior"], "prior_size44")
        candidate = self.result["condition_metrics"][self.result["primary_candidate"]]
        prior = self.result["condition_metrics"][self.result["primary_prior"]]
        self.assertAlmostEqual(candidate["macro_sentence_cer"], 0.9535663244239262)
        self.assertAlmostEqual(prior["macro_sentence_cer"], 0.8220446152037734)
        self.assertAlmostEqual(candidate["blank_fraction"], 0.9963163596966413)
        self.assertEqual(candidate["exact_sentence_count"], 0)
        comparison = self.result["primary_comparisons"]["prior_size44"]
        self.assertEqual((comparison["wins"], comparison["ties"], comparison["losses"]), (2, 0, 9))
        self.assertAlmostEqual(comparison["observed_mean_difference"], -0.13152170922015277)
        self.assertAlmostEqual(comparison["one_sided_greater_p"], 0.98095703125)
        self.assertEqual(comparison["null_assignments"], 2048)

    def test_h4_is_supported_h3_has_evidence_against_and_others_remain_open(self):
        support = {row["hypothesis_id"]: row for row in self.result["hypothesis_support_vector"]}
        self.assertEqual(set(support), {"H1", "H2", "H3", "H4", "H5", "H6"})
        self.assertEqual(support["H4"]["status"], "supported")
        self.assertTrue(support["H4"]["support_rule_passed"])
        self.assertTrue(
            support["H4"]["evidence"]["registered_probe_separability"][
                "all_six_fits_finite_and_stable"
            ]
        )
        self.assertTrue(
            support["H4"]["evidence"]["registered_probe_separability"]["none_of_six_clears_prior"]
        )
        self.assertEqual(support["H3"]["status"], "evidence_against")
        self.assertTrue(support["H3"]["against_rule_passed"])
        self.assertEqual(
            {support[key]["status"] for key in ("H1", "H5", "H6")},
            {"mixed_or_unresolved"},
        )
        self.assertEqual(support["H2"]["status"], "unresolved_evidence_against_unavailable")

    def test_control_components_do_not_rescue_the_failed_conjunction(self):
        self.assertFalse(self.result["intact_signal_conjunction_passed"])
        self.assertTrue(
            all(not value for value in self.result["intact_signal_conjunction_components"].values())
        )
        zero = self.result["primary_comparisons"]["zero_signal"]
        timing = self.result["primary_comparisons"]["timing_only_fit"]
        severe = self.result["primary_comparisons"]["severe_plus100_sample_displacement"]
        self.assertEqual((zero["wins"], zero["ties"], zero["losses"]), (11, 0, 0))
        self.assertAlmostEqual(zero["one_sided_greater_p"], 0.00048828125)
        self.assertEqual(zero, timing)
        self.assertEqual((severe["wins"], severe["ties"], severe["losses"]), (6, 5, 0))
        self.assertFalse(self.result["timing_sensitivity"]["support_rule_passed"])
        self.assertTrue(self.result["timing_sensitivity"]["against_rule_passed"])
        self.assertIsNone(self.result["timing_sensitivity"]["selected_shift"])

    def test_resource_caps_and_causal_claim_boundary_are_preserved(self):
        resources = self.result["resources"]
        freeze_resources = self.freeze["resources"]
        self.assertEqual(resources["training_runs"], 20)
        self.assertEqual(resources["model_runs"], 35)
        self.assertLessEqual(resources["parameter_update_runtime_sec"], 600)
        self.assertLessEqual(resources["cumulative_execution_runtime_sec"], 900)
        self.assertLessEqual(freeze_resources["peak_rss_bytes"], 1024**3)
        self.assertLessEqual(resources["total_generated_artifact_bytes"], 32 * 1024**2)
        self.assertEqual(resources["real_cache_hash_passes"], 1)
        self.assertEqual(resources["raw_data_reads"], 0)
        self.assertTrue(resources["producer_is_causal"])
        self.assertEqual(resources["producer_required_left_context_frames"], 2)
        self.assertEqual(resources["producer_right_context_frames"], 0)
        self.assertFalse(resources["upstream_cache_is_causal"])
        self.assertFalse(resources["end_to_end_latency_measured"])
        self.assertEqual(resources["direct_energy_measurement"], "unavailable")

    def test_no_plaintext_targets_predictions_or_private_payload_were_committed(self):
        self.assertFalse(self.result["plaintext_targets_or_predictions_present"])
        self.assertFalse(self.result["check_target_artifact"]["committed"])
        self.assertFalse(self.freeze["plaintext_predictions_committed"])
        self.assertFalse(self.freeze["plaintext_targets_committed"])
        serialized_result = json.dumps(self.result, sort_keys=True)
        serialized_freeze = json.dumps(self.freeze, sort_keys=True)
        for forbidden in ('"target_texts"', '"predictions"', '"prediction_text"'):
            self.assertNotIn(forbidden, serialized_result)
            self.assertNotIn(forbidden, serialized_freeze)

    def test_closeout_and_roadmap_apply_l50_r05_without_claim_promotion(self):
        normalized_closeout = " ".join(self.closeout.split())
        for phrase in (
            "stable but nonseparable representation",
            "0.953566",
            "0.822045",
            "L50-R05",
            "483,540,992",
            "9,623,773",
            RESULT_SHA256,
            "Scientific claim not established",
        ):
            self.assertIn(phrase, normalized_closeout)
        loop48 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 48)
        self.assertEqual(loop48["status"], "Complete A/B; Stage C Research Ready")
        self.assertFalse(loop48["execution_authorized"])
        self.assertIn("L50-R05", loop48["kill_or_park_rule"])
        self.assertIn("park S24 acquisition", loop48["kill_or_park_rule"])
        self.assertIn("no rerun", loop48["authorization_boundary"])


if __name__ == "__main__":
    unittest.main()
