import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/classical_eeg_adapter_result.v0.json"
DOC_PATH = ROOT / "docs/CLASSICAL_EEG_ADAPTER_RESULT.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ClassicalEegAdapterResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_remote_green_order_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["status"],
            "complete_consumed_one_measured_symbolic_roundtrip",
        )
        contract = self.result["contract_binding"]
        self.assertEqual(contract["registration_push_CI_run_id"], 31279856066)
        self.assertEqual(contract["registration_push_CI_conclusion"], "success")
        implementation = self.result["implementation_binding"]
        self.assertEqual(
            implementation["commit"],
            "eefb7b066810c2a6b87417b105bdb746218e87dc",
        )
        self.assertEqual(implementation["push_CI_run_id"], 31280581308)
        self.assertEqual(implementation["push_CI_conclusion"], "success")
        registry = implementation["implementation_registry"]
        self.assertEqual(registry["sha256"], sha256(ROOT / registry["path"]))

    def test_measured_identity_counts_and_resource_caps_pass(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["item_count"], 96)
        self.assertEqual(measurements["group_count"], 48)
        self.assertEqual(
            measurements["partition_item_counts"],
            {"train": 48, "check": 32, "final": 16},
        )
        self.assertEqual(
            measurements["partition_group_counts"],
            {"train": 24, "check": 16, "final": 8},
        )
        self.assertLessEqual(measurements["runtime_seconds"], 15.0)
        self.assertLessEqual(measurements["peak_RSS_bytes"], 268435456)
        self.assertLessEqual(measurements["plan_bytes"], 1024 * 1024)
        self.assertIsNone(measurements["winner_adapter_id"])

    def test_execution_was_one_bounded_ephemeral_roundtrip(self):
        execution = self.result["execution_identity"]
        self.assertEqual(execution["execution_count"], 1)
        self.assertFalse(execution["rerun_after_measured_closeout"])
        self.assertEqual(execution["configured_numerical_threads"], 1)
        self.assertEqual(execution["worker_count"], 1)
        self.assertEqual(execution["create_return_code"], 0)
        self.assertEqual(execution["inspect_return_code"], 0)
        self.assertTrue(execution["create_and_inspect_summaries_equal"])
        self.assertEqual(execution["temporary_plan_files_created_then_removed"], 1)
        self.assertEqual(execution["retained_generated_plan_files"], 0)

    def test_only_symbolic_plan_operations_are_nonzero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["synthetic_plan_builds"], 1)
        self.assertEqual(counters["symbolic_plan_inspections"], 1)
        for field, value in counters.items():
            if field not in {"synthetic_plan_builds", "symbolic_plan_inspections"}:
                self.assertEqual(value, 0, field)

    def test_every_gate_passed_without_scientific_upgrade(self):
        gates = self.result["acceptance_gates"]
        self.assertEqual(len(gates), 18)
        self.assertTrue(all(gates.values()))
        measurements = self.result["measurements"]
        self.assertTrue(measurements["planned_producer_is_causal"])
        self.assertFalse(measurements["producer_executed"])
        self.assertEqual(measurements["required_right_context_samples"], 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])
        self.assertIn("decoding_accuracy", self.result["unavailable_fields"])
        self.assertEqual(len(self.result["warnings"]), 5)
        verification = self.result["verification"]
        self.assertEqual(verification["result_receipt_tests_passed"], 6)
        self.assertEqual(verification["complete_closeout_tests_passed"], 1279)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertGreater(verification["complete_closeout_wall_seconds"], 0.0)
        self.assertGreater(verification["complete_closeout_peak_RSS_bytes"], 0)

    def test_docs_preserve_work_order_four_as_queue_advances(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        work_order_four = next(line for line in queue.splitlines() if line.startswith("| 4 |"))
        work_order_five = next(line for line in queue.splitlines() if line.startswith("| 5 |"))
        self.assertIn("| Complete |", work_order_four)
        work_order_six = next(line for line in queue.splitlines() if line.startswith("| 6 |"))
        work_order_seven = next(line for line in queue.splitlines() if line.startswith("| 7 |"))
        self.assertIn("| Complete |", work_order_five)
        self.assertIn("| Complete |", work_order_six)
        self.assertIn("Consumed; Parked F11; No Rerun", work_order_seven)
        self.assertEqual(queue.count("| Complete |"), 6)
        self.assertEqual(sum("| In Progress" in line for line in queue.splitlines()), 0)
        self.assertFalse(self.result["next_route"]["install_new_dependencies_now"])
        self.assertFalse(self.result["next_route"]["real_data_action_authorized_by_this_result"])
        self.assertFalse(self.result["next_route"]["hardware_action_authorized_by_this_result"])


if __name__ == "__main__":
    unittest.main()
