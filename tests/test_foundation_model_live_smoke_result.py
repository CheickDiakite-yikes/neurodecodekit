import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/foundation_model_live_smoke_result.v0.json"
CONTRACT_PATH = ROOT / "registries/foundation_model_live_smoke_contract.v0.json"


class FoundationModelLiveSmokeResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_result_is_consumed_parked_and_bound_to_green_implementation(self):
        self.assertEqual(
            self.result["status"],
            "consumed_parked_partial_provider_response",
        )
        self.assertTrue(self.result["consumed"])
        self.assertFalse(self.result["rerun_authorized"])
        implementation = self.result["implementation_binding"]
        self.assertEqual(
            implementation["commit"],
            "a1d7ccca514223cfc49bd37ef80c58c9cbc4596f",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31269398670)
        self.assertTrue(implementation["base_Python_job_passed"])
        self.assertTrue(implementation["optional_neuro_readers_job_passed"])

    def test_partial_call_and_failure_accounting_is_exact(self):
        execution = self.result["provider_execution"]
        self.assertEqual(execution["planned_request_count"], 12)
        self.assertEqual(execution["attempted_request_count"], 3)
        self.assertEqual(execution["completed_response_count"], 2)
        self.assertEqual(execution["schema_valid_response_count"], 2)
        self.assertEqual(execution["retry_count"], 0)
        failure = self.result["terminal_failure"]
        self.assertEqual(failure["request_index"], 2)
        self.assertEqual(failure["condition_id"], "FM-A02")
        self.assertEqual(failure["category"], "provider_response_not_completed")
        self.assertFalse(failure["root_cause_available"])
        self.assertEqual(
            [row["condition_id"] for row in self.result["completed_response_summaries"]],
            ["FM-A00", "FM-A01"],
        )

    def test_resources_and_forbidden_access_stayed_bounded(self):
        caps = self.contract["resource_caps"]
        measured = self.result["usage_and_resources"]
        self.assertLessEqual(
            self.result["provider_execution"]["attempted_request_count"],
            caps["maximum_provider_requests"],
        )
        self.assertLessEqual(
            measured["output_tokens_completed_responses"],
            caps["maximum_total_output_tokens"],
        )
        self.assertLessEqual(
            measured["estimated_standard_cost_USD_completed_responses"],
            caps["maximum_standard_provider_charge_usd"],
        )
        self.assertLessEqual(measured["runtime_seconds"], caps["maximum_wall_seconds"])
        self.assertLessEqual(measured["peak_RSS_bytes"], caps["maximum_peak_rss_bytes"])
        self.assertLessEqual(
            measured["generated_result_bytes"],
            caps["maximum_generated_result_bytes"],
        )
        counters = self.result["access_counters"]
        for field in (
            "real_or_protected_data_reads",
            "target_or_reference_reads",
            "raw_or_dense_neural_uploads",
            "training_runs",
            "fine_tuning_runs",
            "scoring_runs",
        ):
            self.assertEqual(counters[field], 0)

    def test_closeout_document_and_claim_boundary_are_exact(self):
        binding = self.result["result_document_binding"]
        document_path = ROOT / binding["path"]
        self.assertEqual(
            hashlib.sha256(document_path.read_bytes()).hexdigest(),
            binding["sha256"],
        )
        document = document_path.read_text(encoding="utf-8")
        self.assertIn("Consumed and parked", document)
        self.assertIn("no rerun", document.lower())
        self.assertIn("provider_response_not_completed", document)
        self.assertIn("Scientific claim not established", document)
        self.assertFalse(self.result["gate_results"]["behavioral_pairing_available"])
        self.assertFalse(self.result["gate_results"]["scientific_claim_available"])


if __name__ == "__main__":
    unittest.main()
