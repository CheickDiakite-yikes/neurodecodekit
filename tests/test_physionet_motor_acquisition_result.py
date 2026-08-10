import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/physionet_motor_acquisition_result.v0.json"
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_ACQUISITION_RESULT.md"
TRACKER_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


class PhysioNetMotorAcquisitionResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_is_passed_consumed_and_ordered_after_green_gates(self):
        self.assertEqual(self.result["status"], "passed_consumed_no_retry_no_rerun")
        evidence = self.result["ordered_evidence"]
        self.assertEqual(
            evidence["implementation_commit"],
            "92760ce7e3123058f15127b9afd8d5e4bae75321",
        )
        self.assertEqual(evidence["implementation_ci_run_id"], 31345401581)
        self.assertEqual(evidence["implementation_base_python_job_id"], 93326279510)
        self.assertEqual(evidence["implementation_optional_neuro_job_id"], 93326279396)
        self.assertTrue(evidence["all_prior_gates_green_before_execution"])

    def test_exact_nine_file_identity_and_byte_total_pass(self):
        rows = self.result["file_identity_results"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(sum(row["size_bytes"] for row in rows), 23_248_224)
        self.assertEqual(len({row["path"] for row in rows}), 9)
        self.assertTrue(all(row["official_and_observed_sha256_equal"] for row in rows))
        self.assertEqual({row["opaque_local_hash_pass_count"] for row in rows}, {1})

    def test_measurements_are_bounded_and_end_to_end_latency_is_unavailable(self):
        metrics = self.result["measurements"]
        caps = self.result["registered_caps"]
        self.assertEqual(metrics["final_output_payload_bytes"], 23_248_224)
        self.assertEqual(metrics["metadata_request_count"], 12)
        self.assertEqual(metrics["edf_payload_request_count"], 9)
        self.assertLessEqual(metrics["runtime_seconds"], caps["wall_time_seconds"])
        self.assertLessEqual(metrics["peak_rss_bytes"], caps["peak_rss_bytes"])
        self.assertLessEqual(
            metrics["metadata_response_body_bytes"],
            caps["maximum_metadata_network_bytes"],
        )
        self.assertLessEqual(
            metrics["edf_payload_network_bytes"],
            caps["maximum_edf_payload_network_bytes"],
        )
        self.assertLessEqual(
            metrics["incremental_disk_peak_bytes"],
            caps["maximum_incremental_disk_bytes"],
        )
        self.assertFalse(metrics["end_to_end_latency_measured"])
        verification = self.result["post_result_verification"]
        self.assertEqual(verification["complete_suite_passed_tests"], 1455)
        self.assertEqual(verification["complete_suite_expected_skips"], 3)
        self.assertEqual(verification["complete_suite_subtests_passed"], 493)
        self.assertFalse(verification["complete_suite_rss_is_acquisition_metric"])

    def test_all_twelve_gates_pass_and_all_forbidden_counters_are_zero(self):
        gates = self.result["acceptance_gate_results"]
        self.assertEqual(len(gates), 12)
        self.assertTrue(all(gates.values()))
        counters = self.result["access_and_operation_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_private_receipts_are_hash_bound_but_not_committed_or_uploaded(self):
        bindings = self.result["locked_bindings"]
        self.assertRegex(bindings["private_machine_manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(bindings["private_human_receipt_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(bindings["private_receipts_committed_or_uploaded"])
        self.assertFalse(bindings["payload_committed_or_uploaded"])
        self.assertEqual(self.result["measurements"]["combined_private_receipt_bytes"], 16_083)

    def test_work_order_9_and_claim_upgrade_remain_closed(self):
        next_gate = self.result["next_gate"]
        self.assertTrue(next_gate["work_order_8_complete"])
        self.assertTrue(next_gate["work_order_8_consumed"])
        self.assertFalse(next_gate["work_order_8_rerun_allowed"])
        self.assertFalse(next_gate["work_order_9_authorized"])
        self.assertFalse(next_gate["edf_parse_or_annotation_read_authorized"])
        self.assertFalse(next_gate["split_model_training_inference_or_scoring_authorized"])

    def test_closeout_document_and_tracker_state_the_scientific_ceiling(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("No EDF content was decoded", document)
        tracker = TRACKER_PATH.read_text(encoding="utf-8")
        row = next(line for line in tracker.splitlines() if line.startswith("| 8 |"))
        self.assertIn("Complete", row)
        self.assertIn("Consumed", row)
        self.assertIn("No Rerun", row)
        work_order_9 = next(line for line in tracker.splitlines() if line.startswith("| 9 |"))
        self.assertIn("Gated", work_order_9)


if __name__ == "__main__":
    unittest.main()
