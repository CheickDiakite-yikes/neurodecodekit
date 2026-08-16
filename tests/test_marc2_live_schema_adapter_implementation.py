import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc2_live_schema_adapter_implementation.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveSchemaAdapterImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_remote_status_are_exact(self):
        self.assertEqual(self.registry["schema_name"], "neurodecodekit.marc2_live_schema_adapter_implementation")
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC2-LA1")
        self.assertEqual(self.registry["status"], "generated_implementation_and_qualification_complete_remote_green")

    def test_green_registration_proof_is_exact(self):
        proof = self.registry["green_registration_proof"]
        self.assertEqual(proof["commit"], "62e465e0600622444b0868d5dcf19678504d20c4")
        self.assertEqual(proof["CI_run_id"], 31_934_737_967)
        self.assertEqual(proof["base_python_job_id"], 95_134_785_476)
        self.assertEqual(proof["optional_neuro_job_id"], 95_134_785_489)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])
        remote = self.registry["implementation_remote_proof"]
        self.assertEqual(remote["commit"], "3e3f8b86cfb8ac6f23730fb2fcc9fc5da549aac7")
        self.assertEqual(remote["CI_run_id"], 31_935_754_822)
        self.assertEqual(remote["base_python_job_id"], 95_137_289_730)
        self.assertEqual(remote["optional_neuro_job_id"], 95_137_289_704)
        self.assertTrue(remote["both_required_jobs_green"])

    def test_every_tracked_file_hash_is_current(self):
        for binding in self.registry["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_surface_is_generated_mock_only(self):
        surface = self.registry["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_available"])
        self.assertFalse(surface["generic_source_path_or_URL_available"])
        self.assertFalse(surface["private_or_consumed_root_interface_available"])
        self.assertFalse(surface["network_or_archive_reader_available"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_composition_validates_then_calls_green_adapter_once(self):
        composition = self.registry["composition_result"]
        self.assertTrue(composition["live_source_validated_before_copy_or_bridge"])
        self.assertTrue(composition["all_1227_entries_validated_before_copy_or_bridge"])
        self.assertEqual(composition["green_public_adapter_function"], "adapt_generated_source")
        self.assertEqual(composition["green_public_adapter_calls_per_success_path"], 1)
        self.assertFalse(composition["source_mutated"])
        self.assertTrue(composition["transport_values_preserved"])

    def test_selector_identity_and_mutations_passed(self):
        result = self.registry["generated_qualification"]
        self.assertEqual(result["route"], "MARC2LA-G1")
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["required_mutations"], 30)
        self.assertEqual(result["passed_mutations"], 30)

    def test_measurements_are_exact_bounded_and_removed(self):
        measured = self.registry["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 846_696)
        self.assertEqual(measured["generated_output_bytes"], 5_366)
        self.assertEqual(measured["runtime_seconds"], 0.4889211250047083)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measured["report_mode"], "0600")
        self.assertFalse(measured["temporary_output_retained"])

    def test_every_forbidden_counter_and_authorization_is_zero_or_false(self):
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))
        self.assertTrue(all(not value for value in self.registry["authorization_state"].values()))
        gate = self.registry["next_gate"]
        self.assertFalse(gate["commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(gate["all_false_Tier_C_request_allowed_after_green_implementation"])
        self.assertTrue(gate["proof_record_closeout_must_be_remote_green_before_request"])
        self.assertFalse(gate["live_executor_or_private_read_allowed"])

    def test_claim_boundary_remains_scientifically_empty(self):
        boundary = self.registry["claim_boundary"]
        self.assertIn("live-shaped source envelope", boundary["engineering"])
        self.assertIn("no neural payload", boundary["scientific_not_established"])


if __name__ == "__main__":
    unittest.main()
