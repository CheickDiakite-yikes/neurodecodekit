import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/contact_aware_ear_channel_implementation.v0.json"
HISTORICAL_CLI_SHA256 = "16219ba1927513663f06bdb78a3dd0ab1d87f7f346ee1c6bbe5d487795ff5be7"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ContactAwareEarChannelImplementationTests(unittest.TestCase):
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
            "c6e216f68a450ac78f7f67501beaf528999626a6",
        )
        self.assertEqual(binding["registration_push_CI_run_id"], 31281290300)
        self.assertEqual(binding["registration_push_CI_conclusion"], "success")

    def test_implementation_sources_are_hash_bound(self):
        for name, source in self.registry["implementation_binding"].items():
            if name == "CLI":
                self.assertEqual(source["sha256"], HISTORICAL_CLI_SHA256)
                current = (ROOT / source["path"]).read_text(encoding="utf-8")
                self.assertIn('"make-contact-aware-ear-fixture"', current)
                self.assertIn('"inspect-contact-aware-ear-fixture"', current)
            else:
                self.assertEqual(
                    source["sha256"],
                    sha256(ROOT / source["path"]),
                    source["path"],
                )

    def test_surfaces_are_complete_but_measured_execution_is_pending(self):
        surfaces = self.registry["implemented_surfaces"]
        for key, value in surfaces.items():
            if key.endswith("_command"):
                self.assertIsInstance(value, str)
            elif key in {
                "generated_payload_committed",
                "hardware_or_physical_switching_implementation",
            }:
                self.assertFalse(value, key)
            else:
                self.assertTrue(value, key)
        self.assertTrue(all(not value for value in self.registry["execution_gate"].values()))

    def test_local_verification_and_resources_are_explicit(self):
        verification = self.registry["local_verification"]
        self.assertEqual(verification["preimplementation_complete_tests_passed"], 1286)
        self.assertEqual(verification["focused_implementation_tests_passed"], 12)
        self.assertEqual(verification["combined_focused_tests_passed"], 29)
        self.assertEqual(verification["complete_tests_passed"], 1303)
        self.assertEqual(verification["complete_tests_skipped"], 3)
        self.assertGreater(verification["complete_test_wall_seconds"], 0.0)
        self.assertGreater(verification["complete_test_peak_RSS_bytes"], 0)
        self.assertFalse(verification["measured_fixture_execution_completed"])
        resources = self.registry["resource_contract"]
        self.assertEqual(resources["maximum_CPU_threads"], 1)
        self.assertEqual(resources["maximum_workers"], 1)
        self.assertEqual(resources["maximum_generated_output_bytes"], 4 * 1024 * 1024)
        self.assertEqual(resources["minimum_free_disk_bytes_before_execution"], 1024**3)

    def test_no_irreversible_access_or_scientific_claim_occurred(self):
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        document = (
            ROOT / self.registry["implementation_binding"]["documentation"]["path"]
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("No probe file was retained", " ".join(document.split()))


if __name__ == "__main__":
    unittest.main()
