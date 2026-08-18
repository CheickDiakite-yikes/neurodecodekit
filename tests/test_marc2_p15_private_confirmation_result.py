import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_p15_private_confirmation_result.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_P15_PRIVATE_CONFIRMATION_RESULT.md"


class Marc2P15PrivateConfirmationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_is_one_consumed_aggregate_R4_observation(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_p15_private_confirmation_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR12P")
        self.assertEqual(self.result["route"], "MARC2VR12P-R4")
        self.assertEqual(self.result["status"], "consumed_without_cohort_freeze")
        self.assertTrue(self.result["execution_state"]["consumed"])
        self.assertEqual(self.result["execution_state"]["registered_invocations"], 1)
        self.assertEqual(self.result["execution_state"]["retry_limit"], 0)

    def test_green_order_binds_exact_implementation_and_closeout(self):
        proof = self.result["green_execution_proof"]
        self.assertEqual(
            proof["implementation"],
            {
                "commit": "d98a0115d2fd113929d512dfc7fb372a38b8f5c8",
                "CI_run_id": 32197145780,
                "base_python_job_id": 95903371693,
                "optional_neuro_job_id": 95903371721,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            proof["proof_closeout"],
            {
                "commit": "4280aa603da58de4eac220496e09aa97bcce65cb",
                "CI_run_id": 32197772060,
                "base_python_job_id": 95905146777,
                "optional_neuro_job_id": 95905146692,
                "both_required_jobs_green_before_execution": True,
            },
        )

    def test_route_ceiling_withholds_private_failure_detail(self):
        meaning = self.result["route_meaning"]
        self.assertEqual(
            meaning["public_class_name"],
            "identity_task_or_companion_validation_refusal",
        )
        self.assertFalse(meaning["failed_private_value_retained"])
        self.assertFalse(meaning["source_row_or_identity_retained"])
        self.assertFalse(meaning["candidate_or_cohort_retained"])
        self.assertFalse(meaning["run_index_repair_sufficient"])

    def test_execution_counts_are_exact_and_forbidden_counts_are_zero(self):
        counters = self.result["operation_counters"]
        self.assertEqual(counters["private_structural_source_reads"], 1)
        self.assertEqual(counters["private_structural_source_bytes"], 418_755)
        self.assertEqual(counters["strict_structural_parses"], 1)
        self.assertEqual(counters["VR12A_calls"], 1)
        allowed = {
            "private_structural_source_reads",
            "private_structural_source_bytes",
            "strict_structural_parses",
            "VR12A_calls",
        }
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed)
        )

    def test_resources_and_output_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_bytes"], 418_755)
        self.assertLessEqual(measured["runtime_seconds"], 650)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_result_does_not_reopen_or_publish_private_output(self):
        closeout = self.result["closeout_operations"]
        self.assertEqual(closeout["post_result_private_source_reopens"], 0)
        self.assertEqual(closeout["post_result_private_manifest_reopens"], 0)
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
        self.assertTrue(gate["artifact_only_generated_decomposition_eligible"])
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
        self.assertIn("MARC2VR12P-R4", text)
        self.assertIn("no rerun is open", text)
        self.assertIn("FW2 and CIL1 remain ineligible", text)


if __name__ == "__main__":
    unittest.main()
