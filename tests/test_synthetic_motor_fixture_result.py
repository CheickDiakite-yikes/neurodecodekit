import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/synthetic_motor_fixture_result.v0.json"
DOC_PATH = ROOT / "docs/SYNTHETIC_MOTOR_FIXTURE_RESULT.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyntheticMotorFixtureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_remote_green_order_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["status"],
            "complete_consumed_one_measured_synthetic_closeout",
        )
        contract = self.result["contract_binding"]
        self.assertEqual(contract["registration_push_CI_run_id"], 31278502496)
        self.assertEqual(contract["registration_push_CI_conclusion"], "success")
        implementation = self.result["implementation_binding"]
        self.assertEqual(
            implementation["commit"],
            "ad361c89d480d697d79c10733eeaea3855716424",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31279302969)
        self.assertEqual(implementation["push_CI_conclusion"], "success")
        registry = implementation["implementation_registry"]
        self.assertEqual(registry["sha256"], sha256(ROOT / registry["path"]))

    def test_measured_shape_counts_and_resource_caps_pass(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["signal_shape"], [96, 8, 256])
        self.assertEqual(measurements["valid_sample_count"], 20448)
        self.assertEqual(measurements["padding_fraction"], 0.16796875)
        self.assertLessEqual(measurements["runtime_seconds"], 60.0)
        self.assertLessEqual(measurements["peak_RSS_bytes"], 536870912)
        self.assertLessEqual(measurements["total_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(
            measurements["total_output_bytes"],
            measurements["payload_bytes"] + measurements["metadata_sidecar_bytes"],
        )
        self.assertEqual(self.result["partition_counts"], {"train": 48, "check": 32, "final": 16})
        self.assertTrue(all(value == 12 for value in self.result["factor_counts"].values()))

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
        self.assertEqual(self.result["measurements"]["array_members_opened_by_metadata_inspector"], 0)

    def test_only_the_synthetic_generation_counter_is_nonzero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["synthetic_fixture_payload_generations"], 1)
        for field, value in counters.items():
            if field != "synthetic_fixture_payload_generations":
                self.assertEqual(value, 0, field)

    def test_every_acceptance_gate_passed_without_claim_upgrade(self):
        gates = self.result["acceptance_gates"]
        self.assertEqual(len(gates), 18)
        self.assertTrue(all(gates.values()))
        self.assertTrue(self.result["measurements"]["producer_is_causal"])
        self.assertEqual(self.result["measurements"]["required_right_context_samples"], 0)
        self.assertFalse(self.result["measurements"]["end_to_end_latency_measured"])
        self.assertIn("decoding_accuracy", self.result["unavailable_fields"])
        self.assertEqual(len(self.result["warnings"]), 5)
        verification = self.result["verification"]
        self.assertEqual(verification["result_receipt_tests_passed"], 6)
        self.assertEqual(verification["complete_closeout_tests_passed"], 1248)
        self.assertEqual(verification["complete_tests_skipped"], 3)

    def test_docs_keep_work_order_three_complete_as_queue_advances(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        work_order_three = next(line for line in queue.splitlines() if line.startswith("| 3 |"))
        work_order_four = next(line for line in queue.splitlines() if line.startswith("| 4 |"))
        work_order_five = next(line for line in queue.splitlines() if line.startswith("| 5 |"))
        self.assertIn("| Complete |", work_order_three)
        self.assertIn("| Complete |", work_order_four)
        work_order_six = next(line for line in queue.splitlines() if line.startswith("| 6 |"))
        self.assertIn("| Complete |", work_order_five)
        self.assertIn("| In Progress", work_order_six)
        self.assertEqual(queue.count("| Complete |"), 5)
        self.assertEqual(sum("| In Progress" in line for line in queue.splitlines()), 1)
        self.assertFalse(self.result["next_route"]["install_new_dependencies_now"])
        self.assertFalse(self.result["next_route"]["real_data_action_authorized_by_this_result"])


if __name__ == "__main__":
    unittest.main()
