import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/synthetic_motor_fixture_implementation.v0.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class SyntheticMotorFixtureImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_contract_commit_was_remote_green_before_implementation(self):
        self.assertEqual(
            self.registry["status"],
            "implemented_locally_qualified_not_measured_pending_remote_green",
        )
        binding = self.registry["contract_binding"]
        self.assertEqual(
            binding["sha256"],
            sha256(ROOT / binding["path"]),
        )
        self.assertEqual(
            binding["registration_commit"],
            "9238fd79433e849054f453c47f2aff9470ba6947",
        )
        self.assertEqual(binding["registration_push_CI_run_id"], 31278502496)
        self.assertEqual(binding["registration_push_CI_conclusion"], "success")

    def test_implementation_sources_are_hash_bound(self):
        for source in self.registry["implementation_binding"].values():
            self.assertEqual(source["sha256"], sha256(ROOT / source["path"]), source["path"])

    def test_surfaces_are_complete_but_measured_execution_is_pending(self):
        surfaces = self.registry["implemented_surfaces"]
        for key, value in surfaces.items():
            if key.endswith("_command"):
                self.assertIsInstance(value, str)
            else:
                self.assertEqual(value, key != "generated_payload_committed")
        self.assertTrue(all(not value for value in self.registry["execution_gate"].values()))

    def test_local_verification_and_resources_are_explicit(self):
        verification = self.registry["local_verification"]
        self.assertEqual(verification["preimplementation_complete_tests_passed"], 1225)
        self.assertEqual(verification["complete_tests_passed"], 1242)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["diff_check_passed"])
        self.assertFalse(verification["measured_fixture_execution_completed"])
        resources = self.registry["resource_contract"]
        self.assertEqual(resources["maximum_CPU_threads"], 1)
        self.assertEqual(resources["maximum_workers"], 1)
        self.assertEqual(resources["maximum_generated_output_bytes"], 4 * 1024 * 1024)

    def test_no_irreversible_access_or_scientific_claim_occurred(self):
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        document = (
            ROOT / self.registry["implementation_binding"]["documentation"]["path"]
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("No generated NPZ or metadata sidecar is retained in Git", document)


if __name__ == "__main__":
    unittest.main()
