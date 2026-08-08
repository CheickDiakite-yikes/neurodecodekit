import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/classical_eeg_adapter_implementation.v0.json"
HISTORICAL_MUTABLE_BINDINGS = {
    "CLI": "6506aa364dbe753c55eff0842574d2c2cb5e80ed76e3f077c3fbc70272adbd67",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ClassicalEegAdapterImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_contract_was_remote_green_before_implementation(self):
        self.assertEqual(
            self.registry["status"],
            "implemented_locally_qualified_not_measured_pending_remote_green",
        )
        binding = self.registry["contract_binding"]
        self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))
        self.assertEqual(
            binding["registration_commit"],
            "ea5fafda3e408972797e579f00d786ab6c8ee6bc",
        )
        self.assertEqual(binding["registration_push_CI_run_id"], 31279856066)
        self.assertEqual(binding["registration_push_CI_conclusion"], "success")

    def test_implementation_sources_are_hash_bound(self):
        for name, source in self.registry["implementation_binding"].items():
            if name in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(source["sha256"], HISTORICAL_MUTABLE_BINDINGS[name])
                current_source = (ROOT / source["path"]).read_text(encoding="utf-8")
                self.assertIn("_cmd_make_classical_eeg_adapter_plan", current_source)
                self.assertIn('"make-classical-eeg-adapter-plan"', current_source)
            else:
                self.assertEqual(
                    source["sha256"],
                    sha256(ROOT / source["path"]),
                    source["path"],
                )

    def test_symbolic_surfaces_are_complete_and_execution_is_pending(self):
        surfaces = self.registry["implemented_surfaces"]
        for key in (
            "registered_contract_loader",
            "adapter_specification_loader",
            "deterministic_symbolic_plan_builder",
            "strict_plan_validator",
            "canonical_plan_hash",
            "bounded_save_load_and_summary",
            "twelve_refusal_mutation_builders",
        ):
            self.assertTrue(surfaces[key], key)
        self.assertFalse(surfaces["adapter_backend_or_feature_implementation"])
        self.assertFalse(surfaces["generated_plan_committed"])
        self.assertTrue(all(not value for value in self.registry["execution_gate"].values()))

    def test_local_verification_and_resource_boundary_are_explicit(self):
        verification = self.registry["local_verification"]
        self.assertEqual(verification["preimplementation_complete_tests_passed"], 1255)
        self.assertEqual(verification["focused_implementation_tests_passed"], 10)
        self.assertEqual(verification["complete_tests_passed"], 1273)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertFalse(verification["measured_plan_execution_completed"])
        resources = self.registry["resource_contract"]
        self.assertEqual(resources["maximum_CPU_threads"], 1)
        self.assertEqual(resources["maximum_workers"], 1)
        self.assertEqual(resources["maximum_generated_output_bytes"], 1024 * 1024)

    def test_no_adapter_or_irreversible_action_occurred(self):
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        document = (
            ROOT / self.registry["implementation_binding"]["documentation"]["path"]
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("No plan file was retained", " ".join(document.split()))


if __name__ == "__main__":
    unittest.main()
