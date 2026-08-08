import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.evaluation.local_eeg_tooling import (
    validate_local_eeg_tooling_report,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/local_eeg_tooling_audit_result.v0.json"
RECEIPT_PATH = ROOT / "registries/local_eeg_tooling_audit_receipt.v0.json"
DOC_PATH = ROOT / "docs/LOCAL_EEG_TOOLING_AUDIT_2026-08-08.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "CLI": "a095a18b62d2aa21408ce7dc7be7eb52f019f3ed4c92f69e604f73b91a388138",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class LocalEegToolingResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.receipt = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

    def test_raw_result_is_strict_valid_and_hash_bound(self):
        validate_local_eeg_tooling_report(self.result)
        binding = self.receipt["result_binding"]
        self.assertEqual(binding["path"], str(RESULT_PATH.relative_to(ROOT)))
        self.assertEqual(binding["bytes"], RESULT_PATH.stat().st_size)
        self.assertEqual(binding["sha256"], sha256(RESULT_PATH))

    def test_execution_followed_remote_green_implementation(self):
        binding = self.receipt["implementation_binding"]
        self.assertEqual(
            binding["commit"],
            "e1de855f8767840c04e719bade616ba7a22514ed",
        )
        self.assertEqual(binding["push_CI_run_id"], 31277731869)
        self.assertEqual(binding["push_CI_conclusion"], "success")
        for name, source in binding["source_bindings"].items():
            if name in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(source["sha256"], HISTORICAL_MUTABLE_BINDINGS[name])
                current_source = (ROOT / source["path"]).read_text(encoding="utf-8")
                self.assertIn("_cmd_inspect_local_eeg_tooling", current_source)
                self.assertIn('"inspect-local-eeg-tooling"', current_source)
            else:
                self.assertEqual(source["sha256"], sha256(ROOT / source["path"]))

    def test_capability_summary_is_exact_and_does_not_infer_installs(self):
        summary = self.result["summary"]
        self.assertTrue(summary["array_signal_core_ready"])
        self.assertTrue(summary["brainvision_reader_ready"])
        self.assertTrue(summary["ocular_ica_substrate_ready"])
        self.assertFalse(summary["mne_csp_substrate_ready"])
        self.assertFalse(summary["classical_ml_substrate_ready"])
        self.assertEqual(
            summary["missing_tool_ids"],
            ["scikit_learn", "pyriemann", "moabb", "braindecode"],
        )
        self.assertFalse(self.receipt["next_route"]["install_new_dependencies_now"])

    def test_all_irreversible_or_scientific_counters_remain_zero(self):
        allowed_nonzero = {"distribution_metadata_reads", "isolated_import_probes"}
        for field, value in self.receipt["access_counters"].items():
            if field not in allowed_nonzero:
                self.assertEqual(value, 0, field)
        self.assertEqual(self.receipt["access_counters"]["distribution_metadata_reads"], 7)
        self.assertEqual(self.receipt["access_counters"]["isolated_import_probes"], 3)

    def test_resources_and_temporary_cache_are_bounded(self):
        resources = self.receipt["resource_measurements"]
        self.assertLessEqual(resources["runtime_seconds"], 30.0)
        self.assertLessEqual(resources["maximum_child_peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLessEqual(resources["retained_output_bytes"], resources["maximum_output_bytes"])
        self.assertEqual(resources["worker_count"], 1)
        self.assertEqual(resources["configured_numerical_threads"], 1)
        self.assertEqual(resources["temporary_files_created_then_removed"], 1)
        self.assertLess(resources["temporary_bytes_created_then_removed"], 1024 * 1024)

    def test_warnings_and_unavailable_fields_are_not_hidden(self):
        self.assertEqual(self.receipt["warnings"], self.result["warnings"])
        self.assertIn("stable_input_byte_count", self.receipt["unavailable_fields"])
        self.assertIn("neural_advantage", self.receipt["unavailable_fields"])
        self.assertIn("optional_tool_emitted_sanitized_output:mne:63_bytes", self.result["warnings"])

    def test_docs_preserve_the_route_and_claim_boundary(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Do not install a broad EEG stack yet", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("Work orders 1 and 2 are complete", queue)
        self.assertEqual(queue.count("| Complete |"), 2)
        work_order_three = next(
            line for line in queue.splitlines() if line.startswith("| 3 |")
        )
        self.assertIn("| In Progress:", work_order_three)
        self.assertEqual(sum(line.startswith("| ") for line in queue.splitlines()), 21)


if __name__ == "__main__":
    unittest.main()
