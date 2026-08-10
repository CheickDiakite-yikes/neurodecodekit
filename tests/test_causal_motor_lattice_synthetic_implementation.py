import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/causal_motor_lattice_synthetic_implementation.v0.json"
DOC_PATH = ROOT / "docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_IMPLEMENTATION.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "CLI_module": "808fbc930db504e80cc7ecb0117e11115dc039b28505090abe545737b74bfc9e",
    "implementation_registry_tests": (
        "8295a47e4e4ab18f4603c517805aed4653a574e6ea34772e354565e112e97e42"
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CausalMotorLatticeSyntheticImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_is_qualified_but_registered_execution_is_zero(self):
        self.assertEqual(self.registry["status"], "implementation_qualified_not_executed")
        self.assertFalse(self.registry["registered_execution"]["started"])
        self.assertTrue(
            all(
                value == 0
                for value in self.registry["registered_execution"]["access_counters"].values()
            )
        )

    def test_contract_and_owned_sources_are_current_or_historically_hash_bound(self):
        contract = self.registry["contract_binding"]
        self.assertEqual(contract["sha256"], sha256(ROOT / contract["path"]))
        for name, source in self.registry["source_bindings"].items():
            if name in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(source["sha256"], HISTORICAL_MUTABLE_BINDINGS[name])
            else:
                self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])
        current_cli = (ROOT / self.registry["source_bindings"]["CLI_module"]["path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("_cmd_cml_v0_synthetic", current_cli)
        self.assertIn('"cml-v0-synthetic"', current_cli)

    def test_architecture_adapter_and_training_shell_are_exact(self):
        architecture = self.registry["architecture_qualification"]
        self.assertEqual(architecture["input_shape"], [96, 64, 96])
        self.assertEqual(architecture["projection_rank"], 8)
        self.assertEqual(architecture["trainable_parameters"], 4535)
        self.assertEqual(architecture["primitive_count"], 18)
        self.assertEqual(architecture["key_count"], 29)
        self.assertTrue(architecture["exact_hand_marginal"])
        shell = self.registry["execution_shell"]
        self.assertEqual(shell["parameter_update_runs"], 1)
        self.assertEqual(shell["optimizer_steps"], 600)
        self.assertEqual(shell["parameter_update_rows"], 24)
        self.assertTrue(shell["check_before_conditional_final"])
        self.assertFalse(shell["rerun_allowed"])

    def test_import_resources_output_and_proof_gates_fail_closed(self):
        dependency = self.registry["dependency_boundary"]
        self.assertTrue(dependency["module_import_is_scientific_dependency_free"])
        self.assertFalse(dependency["dependency_install_performed_or_allowed"])
        resources = self.registry["resource_caps"]
        self.assertEqual(resources["maximum_CPU_threads"], 1)
        self.assertEqual(resources["maximum_peak_RSS_bytes"], 512 * 1024 * 1024)
        self.assertEqual(resources["maximum_generated_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(resources["minimum_free_disk_bytes_before"], 20 * 1024 * 1024 * 1024)
        proof = self.registry["next_gate"]
        self.assertTrue(proof["exact_implementation_commit_remote_green_required"])
        self.assertFalse(proof["registered_execution_allowed_before_remote_green"])

    def test_qualification_and_claim_boundary_are_explicit(self):
        qualification = self.registry["local_qualification"]
        self.assertEqual(qualification["focused_tests_passed"], 24)
        self.assertEqual(qualification["optimizer_steps"], 0)
        self.assertEqual(qualification["scoring_events"], 0)
        self.assertEqual(qualification["retained_generated_files"], 0)
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)

    def test_tracker_preserves_implementation_before_execution_order(self):
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        row = next(line for line in queue.splitlines() if line.startswith("| 13 |"))
        self.assertIn("Implementation Qualified Locally", row)
        self.assertIn("Execution Pending Remote Green", row)


if __name__ == "__main__":
    unittest.main()
