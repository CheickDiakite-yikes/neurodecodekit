import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/bnci_2014_001_stage_q_result.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_Q_RESULT.md"


class BNCIStageQResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_passed_consumed_and_proof_ordered(self):
        self.assertEqual(
            self.result["status"],
            "passed_consumed_target_firewalled_semantic_qualification_no_rerun",
        )
        evidence = self.result["ordered_evidence"]
        self.assertEqual(
            evidence["Stage_Q_activation_commit"],
            "0e36993fb3b4e0651d53d62818df672c5ed5f04b",
        )
        self.assertEqual(evidence["Stage_Q_activation_CI_run_id"], 32_825_946_085)
        self.assertTrue(evidence["all_prior_gates_green_before_execution"])
        execution = self.result["execution"]
        self.assertTrue(execution["consumed"])
        self.assertFalse(execution["retry_allowed"])
        self.assertFalse(execution["rerun_allowed"])
        self.assertEqual(execution["registered_invocations_remaining"], 0)

    def test_exact_real_semantic_inventory_is_aggregate_only(self):
        inventory = self.result["inventory"]
        self.assertEqual(inventory["MAT_files"], 18)
        self.assertEqual(inventory["task_runs"], 108)
        self.assertEqual(inventory["trials"], 5_184)
        self.assertEqual(inventory["channels"], 25)
        self.assertEqual(inventory["EEG_channels"], 22)
        self.assertEqual(inventory["EOG_channels"], 3)
        self.assertEqual(inventory["sampling_rate_hz"], 250.0)
        self.assertEqual(inventory["folds"], 9)
        self.assertEqual(inventory["held_out_T_rows_exposed_per_fold"], 0)
        self.assertFalse(inventory["geometry_available_from_payload"])
        payload = RESULT.read_text(encoding="utf-8")
        for forbidden in ("participant_id", ".codex_work", "/Users/", "derivative_sha256"):
            self.assertNotIn(forbidden, payload)

    def test_resources_and_registered_limits_pass(self):
        metrics = self.result["measurements"]
        caps = self.result["registered_caps"]
        self.assertEqual(metrics["input_payload_bytes"], 779_873_919)
        self.assertEqual(metrics["private_derivative_bytes"], 72_666_213)
        self.assertLessEqual(metrics["runtime_seconds"], caps["runtime_seconds_maximum"])
        self.assertLessEqual(
            metrics["peak_process_RSS_bytes"], caps["peak_RSS_bytes_maximum"]
        )
        self.assertLessEqual(
            metrics["private_derivative_bytes"],
            caps["private_derivative_bytes_maximum"],
        )
        self.assertFalse(metrics["end_to_end_decoding_latency_measured"])
        self.assertTrue(caps["all_resource_caps_passed"])

    def test_target_firewall_and_forbidden_counters_pass(self):
        firewall = self.result["target_firewall"]
        self.assertTrue(firewall["one_copy_target_free_signal_derivatives"])
        self.assertTrue(firewall["held_out_E_targets_sealed"])
        self.assertTrue(firewall["scoring_keys_outside_every_fold_capability"])
        self.assertFalse(firewall["held_out_T_delivered_to_fold_capabilities"])
        counters = self.result["operation_counters"]
        self.assertEqual(counters["MAT_content_opens"], 18)
        self.assertEqual(counters["MAT_semantic_parses"], 18)
        self.assertEqual(counters["task_signal_runs_read"], 108)
        self.assertEqual(counters["target_vectors_isolated"], 108)
        for key in (
            "calibration_signal_runs_read",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
            "analysis_network_bytes",
        ):
            self.assertEqual(counters[key], 0, key)

    def test_acceptance_claim_and_next_gate_remain_narrow(self):
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        self.assertEqual(
            set(self.result["five_scientific_goals"].values()),
            {"not_established"},
        )
        next_gate = self.result["next_gate"]
        self.assertTrue(next_gate["Stage_Q_complete"])
        self.assertFalse(next_gate["Stage_Q_rerun_allowed"])
        self.assertFalse(next_gate["Stage_P_allowed_before_green_result"])
        self.assertFalse(next_gate["Stage_P_started"])
        self.assertFalse(next_gate["Stage_T_started"])

    def test_verification_reports_aggregate_and_isolated_processes_honestly(self):
        verification = self.result["post_result_verification"]
        self.assertEqual(verification["focused_Stage_Q_tests_passed"], 52)
        self.assertEqual(verification["complete_suite_discovered_tests"], 6_166)
        self.assertEqual(verification["complete_suite_first_process_passed_tests"], 6_144)
        self.assertEqual(verification["environment_sensitive_modules"], 5)
        self.assertEqual(verification["isolated_module_tests_passed"], 62)
        self.assertTrue(verification["process_isolated_complete_verification_passed"])
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["CLI_help_passed"])
        self.assertTrue(verification["git_diff_check_passed"])

    def test_document_states_engineering_and_scientific_boundaries(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("Stage Q is complete and consumed", document)
        self.assertIn("Stage P remains closed", document)
        self.assertIn("5,184 trials", document)
        self.assertIn("6,166 tests", document)


if __name__ == "__main__":
    unittest.main()
