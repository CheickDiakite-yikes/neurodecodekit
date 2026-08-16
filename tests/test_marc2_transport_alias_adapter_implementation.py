import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc2_transport_alias_adapter_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2TransportAliasAdapterImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc2_transport_alias_adapter_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC2-TA1")
        self.assertEqual(
            self.registry["status"],
            "generated_implementation_and_qualification_complete_remote_green_required",
        )

    def test_green_registration_proof_is_exact(self):
        proof = self.registry["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "0c0e1c8a08ff7e68d0e4432a64dde8a85fb0274f"
        )
        self.assertEqual(proof["CI_run_id"], 31_932_701_989)
        self.assertEqual(proof["base_python_job_id"], 95_129_832_134)
        self.assertEqual(proof["optional_neuro_job_id"], 95_129_832_169)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_every_tracked_file_hash_is_current(self):
        for binding in self.registry["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_surface_is_generated_only(self):
        surface = self.registry["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_available"])
        self.assertFalse(surface["generic_source_path_or_URL_available"])
        self.assertFalse(surface["private_or_consumed_root_interface_available"])
        self.assertFalse(surface["network_or_archive_reader_available"])
        self.assertFalse(surface["neural_target_model_or_score_interface_available"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_adapter_preserves_the_single_registered_alias(self):
        adapter = self.registry["adapter_result"]
        self.assertEqual(
            adapter["source_transport_keys"], ["directory", "metadata", "tail"]
        )
        self.assertEqual(
            adapter["selector_transport_keys"],
            ["central_directory", "metadata", "tail"],
        )
        self.assertTrue(adapter["source_validated_before_copy_or_mapping"])
        self.assertFalse(adapter["source_mutated"])
        self.assertFalse(adapter["mutable_alias_detected"])
        self.assertTrue(adapter["transport_values_preserved"])

    def test_selector_identity_and_mutations_passed(self):
        result = self.registry["generated_qualification"]
        self.assertEqual(result["route"], "MARC2TA-G1")
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["required_mutations"], 26)
        self.assertEqual(result["passed_mutations"], 26)

    def test_measurements_are_bounded_and_output_was_removed(self):
        measured = self.registry["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 846_708)
        self.assertEqual(measured["generated_output_bytes"], 4_931)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measured["report_mode"], "0600")
        self.assertFalse(measured["temporary_output_retained"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_every_forbidden_counter_and_authorization_is_zero_or_false(self):
        self.assertTrue(
            all(value == 0 for value in self.registry["access_counters"].values())
        )
        self.assertTrue(
            all(not value for value in self.registry["authorization_state"].values())
        )

    def test_claim_boundary_remains_scientifically_empty(self):
        boundary = self.registry["claim_boundary"]
        self.assertIn("generated producer-native manifest", boundary["engineering"])
        self.assertIn("no neural payload", boundary["scientific_not_established"])


if __name__ == "__main__":
    unittest.main()
