import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_f03_private_discriminator_result.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_F03_PRIVATE_DISCRIMINATOR_RESULT.md"


class Marc2F03PrivateDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_is_one_consumed_aggregate_R2_observation(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_f03_private_discriminator_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR11P")
        self.assertEqual(self.result["route"], "MARC2VR11P-R2")
        self.assertEqual(self.result["status"], "consumed_once_no_rerun")
        self.assertTrue(self.result["execution_state"]["consumed"])
        self.assertEqual(self.result["execution_state"]["registered_invocations"], 1)
        self.assertEqual(self.result["execution_state"]["retry_limit"], 0)

    def test_green_order_binds_exact_implementation_and_closeout(self):
        proof = self.result["green_execution_proof"]
        self.assertEqual(
            proof["implementation"],
            {
                "commit": "2093ad542d5043c97e2a3b0cabb605009e66600e",
                "CI_run_id": 32041540553,
                "base_python_job_id": 95421634020,
                "optional_neuro_job_id": 95421633971,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            proof["proof_closeout"],
            {
                "commit": "e569bcccfde9bcf5e1116de1b892fed79373c137",
                "CI_run_id": 32041863346,
                "base_python_job_id": 95422480212,
                "optional_neuro_job_id": 95422480363,
                "both_required_jobs_green_before_execution": True,
            },
        )

    def test_route_ceiling_is_P15_without_private_value(self):
        meaning = self.result["route_meaning"]
        self.assertEqual(meaning["frozen_class"], "P15")
        self.assertEqual(meaning["public_class_name"], "suffix_bearing_BIDS_identity")
        self.assertFalse(meaning["failed_private_value_retained"])
        self.assertFalse(meaning["source_row_or_identity_retained"])
        self.assertFalse(meaning["candidate_or_cohort_retained"])

    def test_execution_counts_are_exact_and_every_forbidden_count_is_zero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["real_readiness_operations"], 1)
        self.assertEqual(counters["private_or_Git_ignored_path_operations"], 1)
        self.assertEqual(counters["private_structural_source_opens"], 1)
        self.assertEqual(counters["private_structural_bytes_read"], 418_755)
        self.assertEqual(counters["VR6_real_calls"], 1)
        self.assertEqual(counters["VR10B_real_calls"], 1)
        allowed = {
            "real_readiness_operations",
            "private_or_Git_ignored_path_operations",
            "private_structural_source_opens",
            "private_structural_bytes_read",
            "VR6_real_calls",
            "VR10B_real_calls",
        }
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed)
        )

    def test_resources_and_output_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_bytes"], 418_755)
        self.assertLessEqual(measured["runtime_seconds"], 650)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["combined_output_bytes"], 1024**2)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_result_does_not_reopen_or_publish_private_report(self):
        closeout = self.result["closeout_operations"]
        self.assertEqual(closeout["post_result_private_source_reopens"], 0)
        self.assertEqual(closeout["post_result_aggregate_report_reopens"], 0)
        self.assertEqual(closeout["ignored_output_files_committed"], 0)
        self.assertEqual(closeout["raw_private_hashes_published"], 0)
        self.assertEqual(closeout["per_item_outcomes_published"], 0)

    def test_claims_and_next_gate_remain_closed(self):
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_ceiling", "scientific_ceiling"}:
                self.assertFalse(value)
        gate = self.result["next_gate"]
        self.assertTrue(gate["prospective_generated_P15_repair_contract_required"])
        self.assertFalse(gate["repair_implementation_authorized"])
        self.assertFalse(gate["another_private_read_authorized"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_result_artifacts_are_hash_bound(self):
        for row in self.result["result_artifacts"]:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_human_result_separates_engineering_and_scientific_sentences(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("MARC2VR11P-R2", text)
        self.assertIn("no rerun is open", text)
        self.assertIn("FW2 and CIL1 remain ineligible", text)


if __name__ == "__main__":
    unittest.main()
