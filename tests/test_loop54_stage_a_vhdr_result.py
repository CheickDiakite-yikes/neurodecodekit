import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/loop54_stage_a_vhdr_result.v0.json"
DOCUMENT_PATH = ROOT / "docs/LOOP_54_STAGE_A_VHDR_RESULT.md"
CONTRACT_PATH = ROOT / "registries/loop54_stage_a_vhdr_contract.v0.json"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Loop54StageAVHDRResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_identity_bindings_and_green_implementation_precede_execution(self):
        result = self.result
        self.assertEqual(
            result["schema_name"],
            "neurodecodekit.loop54_stage_a_vhdr_result",
        )
        self.assertEqual(result["schema_version"], "0.1.0")
        self.assertEqual(result["status"], "consumed_parked_F11_no_rerun")
        bindings = result["bindings"]
        for binding in (
            bindings["contract"],
            bindings["authorization_decision"],
            bindings["implementation"],
            bindings["human_result"],
        ):
            self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))
        self.assertEqual(bindings["authorization_decision"]["push_CI_run_id"], 31286428489)
        implementation = bindings["implementation"]
        self.assertEqual(
            implementation["commit"],
            "b486fdf13d8a2293432f9dca5f3fb8ba97527be0",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31287819503)
        self.assertEqual(implementation["base_python_job_id"], 93179736029)
        self.assertEqual(implementation["optional_neuro_readers_job_id"], 93179736035)
        self.assertTrue(implementation["all_required_jobs_green_before_execution"])

    def test_one_execution_passed_source_identity_and_parked_at_F11(self):
        execution = self.result["execution"]
        source = self.result["source_verification"]
        self.assertEqual(execution["registered_execution_ordinal"], 1)
        self.assertTrue(execution["registered_execution_consumed"])
        self.assertEqual(execution["command_return_code"], 2)
        self.assertEqual(
            execution["primary_refusal_id"],
            "L54A-F11_missing_duplicate_or_malformed_required_section_or_key",
        )
        self.assertEqual(execution["safe_diagnostic"], "VHDR format preamble is missing")
        self.assertFalse(execution["raw_first_line_recorded"])
        self.assertFalse(execution["rerun_available"])
        self.assertEqual(source["observed_input_bytes"], 11705)
        self.assertEqual(source["content_opens"], 1)
        self.assertEqual(source["observed_source_identity"], source["expected_source_identity"])
        self.assertTrue(source["strict_codepage_detection_and_decode_completed"])
        self.assertIsNone(source["strict_codepage_value"])
        self.assertFalse(source["format_preamble_check_passed"])
        self.assertEqual(source["declared_header_fields_emitted"], 0)

    def test_gate_map_matches_contract_and_fails_exactly_one_gate(self):
        gates = self.result["acceptance_gate_results"]
        self.assertEqual(list(gates), self.contract["acceptance_gates"])
        self.assertEqual(
            gates["all_required_sections_and_keys_unique_and_internally_consistent"],
            "failed_F11_format_preamble",
        )
        summary = self.result["gate_summary"]
        self.assertEqual(summary["total_gates"], 18)
        self.assertEqual(summary["passed_or_passed_in_closeout"], 12)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["not_reached"], 5)
        self.assertFalse(summary["all_gates_passed"])
        self.assertFalse(summary["L54_Q2_declared_header_compatibility_established"])
        self.assertEqual(summary["retained_claim_level"], "L54-Q1_acquisition_identity")

    def test_resources_outputs_and_every_forbidden_counter_are_bounded(self):
        measurements = self.result["measurements"]
        self.assertLess(measurements["external_wall_seconds"], 30)
        self.assertLess(measurements["external_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measurements["input_bytes"], 11705)
        self.assertEqual(measurements["registered_generated_output_bytes"], 0)
        self.assertEqual(measurements["registered_generated_output_files"], 0)
        self.assertLessEqual(measurements["registered_generated_output_bytes"], 1024**2)
        self.assertGreaterEqual(measurements["free_disk_bytes_before_execution"], 2 * 1024**3)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertFalse(measurements["end_to_end_decoding_latency_measured"])
        counters = self.result["access_counters"]
        self.assertEqual(counters["registered_real_executions"], 1)
        self.assertEqual(counters["registered_VHDR_content_opens"], 1)
        self.assertEqual(counters["registered_VHDR_bytes_read"], 11705)
        allowed_nonzero = {
            "registered_real_executions",
            "registered_path_validation_passes",
            "registered_VHDR_content_opens",
            "registered_VHDR_bytes_read",
            "registered_VHDR_size_checks",
            "registered_VHDR_git_blob_checks",
            "strict_decode_attempts",
            "strict_parse_attempts",
        }
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)
        )
        verification = self.result["verification"]
        self.assertEqual(verification["pre_change_implementation_pytest_passed"], 1351)
        self.assertEqual(verification["complete_pytest_passed"], 1356)
        self.assertEqual(verification["complete_pytest_skipped"], 3)
        self.assertEqual(verification["complete_pytest_subtests_passed"], 493)
        self.assertEqual(verification["pytest_pass_delta_vs_pre_change"], 5)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertEqual(verification["registry_JSON_files_validated"], 93)
        self.assertEqual(verification["real_execute_commands_during_closeout_verification"], 0)

    def test_unavailable_fields_route_and_public_result_preserve_claim_boundary(self):
        unavailable = set(self.result["unavailable_fields"])
        for field in (
            "format preamble content",
            "data basename",
            "source channel names",
            "sampling rate",
            "target text",
            "neural advantage",
            "decoding accuracy",
        ):
            self.assertIn(field, unavailable)
        route = self.result["route"]
        self.assertEqual(route["decision"], "park_L54_A_consumed_no_rerun")
        self.assertFalse(route["Loop_54_B_eligible"])
        self.assertFalse(route["Loop_54_C_eligible"])
        self.assertFalse(route["Loop_55_protected_experiment_eligible"])
        normalized = " ".join(self.document.split()).lower()
        for phrase in (
            "consumed; parked at l54a-f11; no rerun",
            "the raw first line is deliberately not reported",
            "registered ledger and summary bytes are both zero",
            "engineering capability added:",
            "scientific claim not established:",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
