import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_live_schema_adapter_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveSchemaAdapterResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_is_generated_only_consumed_and_pending_green(self):
        self.assertEqual(self.result["schema_name"], "neurodecodekit.marc2_live_schema_adapter_result")
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-LA1")
        self.assertEqual(self.result["route"], "MARC2LA-G1")
        self.assertEqual(self.result["status"], "generated_qualification_complete_consumed_remote_green_pending")
        self.assertFalse(self.result["proof_posture"]["scientific_value"])
        self.assertFalse(self.result["implementation_remote_proof"]["both_required_jobs_green"])

    def test_all_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_live_envelope_and_four_value_bridge_passed(self):
        result = self.result["composition_result"]
        self.assertTrue(result["live_envelope_validated_before_copy_or_bridge"])
        self.assertTrue(result["all_entries_validated_before_copy_or_bridge"])
        self.assertEqual(len(result["identity_values_changed"]), 4)
        self.assertFalse(result["source_mutated"])
        self.assertFalse(result["mutable_alias_detected"])
        self.assertEqual(result["green_public_adapter_calls_per_success_path"], 1)
        self.assertTrue(result["all_transport_values_preserved"])

    def test_generated_selector_identity_replayed_exactly(self):
        selection = self.result["selector_result"]
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertTrue(selection["existing_generated_identity_matched"])
        self.assertTrue(selection["canonical_and_reversed_orders_matched"])

    def test_all_mutations_and_acceptance_gates_passed(self):
        mutations = self.result["mutation_result"]
        self.assertEqual(mutations["required"], 30)
        self.assertEqual(mutations["passed"], 30)
        self.assertEqual(sum(mutations["route_counts"].values()), 30)
        self.assertEqual(self.result["acceptance_gates_passed"], 16)
        self.assertEqual(self.result["acceptance_gates_required"], 16)

    def test_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 846_696)
        self.assertEqual(measured["generated_output_bytes"], 5_366)
        self.assertEqual(measured["runtime_seconds"], 0.4889211250047083)
        self.assertEqual(measured["peak_RSS_bytes"], 38_387_712)
        self.assertEqual(measured["report_SHA256"], "8353c641634cc628663f40932140805bbb2f051fd83ba917695e9cf20a457df7")
        self.assertFalse(measured["temporary_output_retained"])

    def test_no_real_neural_or_model_operation_occurred(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))
        measured = self.result["measurements"]
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_live_boundary_remains_closed_until_remote_green(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["generated_qualification_consumed"])
        self.assertTrue(disposition["temporary_aggregate_removed"])
        self.assertFalse(disposition["implementation_remote_green"])
        self.assertFalse(disposition["all_false_Tier_C_request_eligible"])
        self.assertFalse(disposition["live_executor_or_private_read_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])

    def test_claim_boundary_is_exact(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("generated-only composition", boundary["engineering_capability_added"])
        self.assertIn("no neural payload", boundary["scientific_claim_not_established"].lower())


if __name__ == "__main__":
    unittest.main()
