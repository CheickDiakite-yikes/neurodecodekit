import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/contact_aware_ear_channel_result.v0.json"
DOC_PATH = ROOT / "docs/CONTACT_AWARE_EAR_CHANNEL_RESULT.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContactAwareEarChannelResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_remote_green_order_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["status"],
            "complete_consumed_one_measured_synthetic_roundtrip",
        )
        contract = self.result["contract_binding"]
        self.assertEqual(contract["registration_push_CI_run_id"], 31281290300)
        self.assertEqual(contract["registration_push_CI_conclusion"], "success")
        implementation = self.result["implementation_binding"]
        self.assertEqual(
            implementation["commit"],
            "76ccc63bdb62b7695dd12ead6ae629c3ab73bb53",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31282344300)
        self.assertEqual(implementation["push_CI_conclusion"], "success")
        registry = implementation["implementation_registry"]
        self.assertEqual(registry["sha256"], sha256(ROOT / registry["path"]))

    def test_measured_shape_masks_hashes_and_resource_caps_pass(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["signal_shape"], [48, 16, 256])
        self.assertEqual(measurements["observed_source_sample_count"], 168192)
        self.assertEqual(measurements["adapted_observed_sample_count"], 76800)
        self.assertEqual(measurements["selected_channel_count"], 300)
        self.assertEqual(measurements["selected_left_channel_count"], 150)
        self.assertEqual(measurements["selected_right_channel_count"], 150)
        self.assertEqual(
            measurements["selection_status_counts"],
            {"insufficient_bilateral_contact": 6, "ok": 42},
        )
        self.assertLessEqual(measurements["runtime_seconds"], 60.0)
        self.assertLessEqual(measurements["peak_RSS_bytes"], 268435456)
        self.assertGreaterEqual(measurements["free_disk_bytes_before_execution"], 1024**3)
        self.assertLessEqual(measurements["total_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(
            measurements["total_output_bytes"],
            measurements["payload_bytes"] + measurements["metadata_sidecar_bytes"],
        )
        for key in (
            "payload_sha256",
            "metadata_sidecar_sha256",
            "fixture_metadata_sha256",
            "configuration_sha256",
            "source_order_sha256",
            "selected_subset_and_weight_sha256",
        ):
            self.assertRegex(measurements[key], r"^[0-9a-f]{64}$")

    def test_execution_was_one_bounded_ephemeral_roundtrip(self):
        execution = self.result["execution_identity"]
        self.assertEqual(execution["execution_count"], 1)
        self.assertFalse(execution["rerun_after_measured_closeout"])
        self.assertEqual(execution["configured_numerical_threads"], 1)
        self.assertEqual(execution["worker_count"], 1)
        self.assertEqual(execution["create_return_code"], 0)
        self.assertEqual(execution["inspect_return_code"], 0)
        self.assertTrue(execution["create_and_inspect_summaries_equal"])
        self.assertEqual(execution["temporary_fixture_files_created_then_removed"], 2)
        self.assertEqual(execution["retained_generated_fixture_files"], 0)
        self.assertEqual(
            self.result["measurements"]["array_members_opened_by_metadata_inspector"],
            0,
        )

    def test_only_registered_synthetic_operations_are_nonzero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["synthetic_payload_generations"], 1)
        self.assertEqual(counters["target_blind_contact_policy_item_runs"], 48)
        self.assertEqual(counters["metadata_only_inspections"], 1)
        allowed = {
            "synthetic_payload_generations",
            "target_blind_contact_policy_item_runs",
            "metadata_only_inspections",
        }
        for field, value in counters.items():
            if field not in allowed:
                self.assertEqual(value, 0, field)

    def test_every_gate_passed_without_scientific_upgrade(self):
        gates = self.result["acceptance_gates"]
        self.assertEqual(len(gates), 18)
        self.assertTrue(all(gates.values()))
        measurements = self.result["measurements"]
        self.assertTrue(measurements["producer_is_causal"])
        self.assertEqual(measurements["required_left_context_samples"], 256)
        self.assertEqual(measurements["required_right_context_samples"], 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])
        self.assertIn("brain_specific_origin", self.result["unavailable_fields"])
        self.assertEqual(len(self.result["warnings"]), 6)
        verification = self.result["verification"]
        self.assertEqual(verification["result_receipt_tests_passed"], 6)
        self.assertEqual(verification["complete_closeout_tests_passed"], 1309)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertGreater(verification["complete_closeout_wall_seconds"], 0.0)
        self.assertGreater(verification["complete_closeout_peak_RSS_bytes"], 0)

    def test_docs_close_work_order_five_and_gate_real_work_order_six(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        work_order_five = next(line for line in queue.splitlines() if line.startswith("| 5 |"))
        work_order_six = next(line for line in queue.splitlines() if line.startswith("| 6 |"))
        self.assertIn("| Complete |", work_order_five)
        self.assertIn("| In Progress", work_order_six)
        self.assertEqual(queue.count("| Complete |"), 5)
        self.assertEqual(sum("| In Progress" in line for line in queue.splitlines()), 1)
        route = self.result["next_route"]
        self.assertFalse(route["real_Loop_54_A_execution_authorized_by_this_result"])
        self.assertFalse(route["S20_path_stat_or_content_access_authorized_by_this_result"])
        self.assertFalse(route["hardware_action_authorized_by_this_result"])


if __name__ == "__main__":
    unittest.main()
