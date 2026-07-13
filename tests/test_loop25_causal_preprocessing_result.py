import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries" / "loop25_causal_preprocessing_result.v1.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "causal_preprocessing_contract.v1.json"
AUTHORIZATION_PATH = REPO_ROOT / "registries" / "loop25_authorization_decision.v1.json"
CLOSEOUT_PATH = REPO_ROOT / "docs" / "LOOP_25_CAUSAL_PREPROCESSING_RESULT.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Loop25CausalPreprocessingResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.closeout = CLOSEOUT_PATH.read_text(encoding="utf-8")

    def test_identity_and_green_commit_sequence_are_exact(self):
        result = self.result
        self.assertEqual(
            result["schema_name"],
            "neurodecodekit.loop25_causal_preprocessing_result",
        )
        self.assertEqual(result["schema_version"], "0.1.0")
        self.assertEqual(result["status"], "complete_passed_no_rerun_authorized")
        bindings = result["bindings"]
        self.assertEqual(bindings["contract_sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(bindings["authorization_sha256"], sha256(AUTHORIZATION_PATH))
        self.assertEqual(bindings["authorization_commit"][:7], "1e7296a")
        self.assertEqual(bindings["authorization_ci_run_id"], 29275552886)
        self.assertEqual(bindings["implementation_commit"][:7], "439f151")
        self.assertEqual(bindings["implementation_ci_run_id"], 29277702513)
        self.assertEqual(bindings["authorization_ci_conclusion"], "success")
        self.assertEqual(bindings["implementation_ci_conclusion"], "success")

    def test_static_gate_preceded_all_partition_access_and_passed(self):
        order = self.result["execution_order"]
        self.assertEqual(order["registered_filter_design_runs"], 1)
        self.assertEqual(order["static_gate_runs"], 1)
        self.assertEqual(order["fixture_generation_runs"], 1)
        self.assertEqual(order["development_partition_opens"], 1)
        self.assertTrue(order["development_report_frozen_before_qualification"])
        self.assertEqual(order["qualification_partition_opens"], 1)
        self.assertEqual(order["complete_gate_runs"], 1)
        self.assertEqual(order["post_result_tuning_runs"], 0)
        self.assertFalse(order["reruns_authorized_now"])
        static = self.result["static_gate"]
        self.assertTrue(static["passed"])
        self.assertEqual(static["dense_response_points"], 65537)
        self.assertEqual(static["alias_probe_count"], 23)
        self.assertEqual(static["partition_arrays_opened"], 0)
        self.assertLessEqual(static["combined_folding_band_max_db"], -59.5)
        self.assertLessEqual(static["maximum_pole_magnitude"], 0.999999)

    def test_fixture_is_target_free_separate_and_bounded(self):
        fixture = self.result["fixture"]
        self.assertTrue(fixture["target_free"])
        self.assertFalse(fixture["forbidden_target_or_identity_members_present"])
        self.assertEqual(fixture["development"]["seed"], 2501)
        self.assertEqual(fixture["qualification"]["seed"], 2502)
        self.assertNotEqual(
            fixture["development"]["sha256"],
            fixture["qualification"]["sha256"],
        )
        self.assertEqual(fixture["total_bytes"], 728596)
        self.assertLessEqual(fixture["total_bytes"], 4 * 1024 * 1024)
        self.assertIsNone(fixture["fixture_generation_peak_rss_bytes"])
        self.assertTrue(fixture["fixture_generation_peak_rss_unavailable_reason"])

    def test_development_and_one_time_qualification_pass_every_replay_gate(self):
        development = self.result["development_gate"]
        qualification = self.result["qualification_gate"]
        self.assertTrue(development["passed"])
        self.assertTrue(qualification["opened_only_after_development_pass_and_report_freeze"])
        self.assertTrue(qualification["passed"])
        for row in (development, qualification):
            self.assertEqual(row["items_passed"], 12)
            self.assertEqual(row["chunk_schedule_checks"], 84)
            self.assertEqual(row["resume_checks"], 120)
            self.assertEqual(row["future_mutation_checks"], 36)
            self.assertEqual(row["valid_source_samples"], 29440)
            self.assertEqual(row["valid_output_samples"], 2949)
        combined = self.result["combined_measurements"]
        self.assertEqual(combined["items_passed"], 24)
        self.assertEqual(combined["chunk_schedule_runs"], 168)
        self.assertEqual(combined["resume_runs"], 240)
        self.assertEqual(combined["future_mutation_control_runs"], 72)

    def test_resources_access_and_causal_claim_are_exact(self):
        gate = self.result["complete_gate"]
        self.assertTrue(gate["passed"])
        self.assertTrue(gate["all_resource_caps_passed"])
        self.assertTrue(gate["exact_access_counter_match"])
        self.assertTrue(gate["producer_causal"])
        self.assertEqual(gate["right_context_source_samples"], 0)
        self.assertFalse(gate["end_to_end_latency_measured"])
        combined = self.result["combined_measurements"]
        self.assertLessEqual(combined["total_generated_bytes"], combined["generated_cap_bytes"])
        self.assertLessEqual(combined["maximum_observed_peak_rss_bytes"], 1024**3)
        self.assertEqual(combined["cpu_threads"], 1)
        counters = self.result["access_counters"]
        for name in (
            "normalization_fit_runs",
            "real_data_reads",
            "real_cache_reads",
            "consumed_evidence_reads",
            "target_label_text_prediction_reads",
            "checkpoint_reads",
            "model_runs",
            "training_runs",
            "parameter_updates",
            "external_network_calls",
            "rw3_operations",
            "stream_socket_board_device_hardware_operations",
        ):
            self.assertEqual(counters[name], 0, name)

    def test_closeout_keeps_engineering_and_science_in_separate_sentences(self):
        normalized_closeout = " ".join(self.closeout.split())
        for phrase in (
            "What Was Proven",
            "What Was Not Proven",
            "No neural recording was used",
            "End-to-end latency was not measured",
            "This closeout does not authorize that experiment",
        ):
            self.assertIn(phrase, normalized_closeout)
        boundary = self.result["claim_boundary"]
        self.assertFalse(boundary["loop46_execution_authorized_now"])
        self.assertEqual(boundary["S21_source_validation_targets_opened"], 0)
        self.assertEqual(boundary["S25_reads"], 0)


if __name__ == "__main__":
    unittest.main()
