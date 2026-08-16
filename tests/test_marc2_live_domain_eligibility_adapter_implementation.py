import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_live_domain_eligibility_adapter_implementation.v0.json"
)
DOC_PATH = (
    ROOT / "docs" / "MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_IMPLEMENTATION.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveDomainEligibilityAdapterImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_is_generated_implementation_remote_proof_pending(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_live_domain_eligibility_adapter_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR2")
        self.assertEqual(
            self.record["status"],
            "generated_implementation_ready_remote_proof_pending",
        )
        self.assertTrue(self.record["implementation_remote_proof"]["pending"])

    def test_green_registration_proof_is_exact(self):
        proof = self.record["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "384373e0ffcfe999ae0ae188087f7e84f09720ca"
        )
        self.assertEqual(proof["CI_run_id"], 31_945_086_852)
        self.assertEqual(proof["base_python_job_id"], 95_159_734_989)
        self.assertEqual(proof["optional_neuro_job_id"], 95_159_734_967)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_every_tracked_implementation_hash_matches(self):
        paths = set()
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], paths)
                paths.add(binding["path"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertEqual(len(paths), 9)

    def test_surface_is_standard_library_in_memory_and_nonexecuting(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertEqual(
            surface["public_in_memory_adapter"], "adapt_live_domain_source"
        )
        self.assertFalse(surface["execute_command_available"])
        self.assertFalse(surface["generic_source_path_or_URL_available"])
        self.assertFalse(
            surface["private_root_output_root_or_consumed_executor_available"]
        )
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_all_four_profiles_are_distinct_and_preserve_one_selection(self):
        profiles = self.record["generated_profiles"]
        self.assertEqual(set(profiles), {"A", "B", "C", "D"})
        self.assertEqual(
            {name: row["predicate_counts"] for name, row in profiles.items()},
            {
                "A": [12, 24, 7],
                "B": [8, 20, 15],
                "C": [16, 12, 15],
                "D": [4, 4, 35],
            },
        )
        self.assertEqual(
            len({row["canonical_source_sha256"] for row in profiles.values()}),
            4,
        )
        selection = self.record["validation_and_selection"]
        self.assertFalse(selection["exact_ineligible_breakdown_required"])
        self.assertFalse(selection["generated_profile_identity_passed_to_adapter"])
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["ineligible_selected_bundles"], 0)

    def test_preflight_measurements_and_refusal_matrix_are_bounded(self):
        preflight = self.record["generated_adversarial_preflight"]
        self.assertEqual(preflight["registered_mutations"], 58)
        self.assertEqual(preflight["refused_mutations"], 58)
        self.assertTrue(preflight["all_eight_refusal_routes_exercised"])
        self.assertEqual(
            set(preflight["route_counts"]),
            {f"MARC2VR2-F{index:02d}" for index in range(1, 9)},
        )
        self.assertLess(preflight["runtime_seconds"], 30)
        self.assertLess(preflight["peak_RSS_bytes"], 256 * 1024**2)
        self.assertFalse(preflight["registered_measured_closeout_executed"])

    def test_local_verification_is_complete_and_remote_proof_is_pending(self):
        verification = self.record["local_verification"]
        self.assertEqual(verification["focused_registration_tests"], 10)
        self.assertEqual(verification["focused_behavior_tests"], 13)
        self.assertEqual(verification["focused_implementation_record_tests"], 9)
        self.assertEqual(verification["focused_tests"], 32)
        self.assertEqual(verification["complete_base_tests"], 3_575)
        self.assertEqual(verification["complete_base_skips"], 204)
        self.assertEqual(verification["complete_optional_tests"], 3_646)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertFalse(verification["implementation_record_tests_pending"])
        self.assertFalse(verification["complete_repository_verification_pending"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_all_forbidden_operation_and_authorization_fields_are_false(self):
        self.assertTrue(
            all(value == 0 for value in self.record["access_counters"].values())
        )
        self.assertTrue(
            all(not value for value in self.record["authorization_state"].values())
        )
        gate = self.record["next_gate"]
        self.assertTrue(gate["commit_push_and_both_remote_jobs_green_required"])
        self.assertFalse(
            gate["registered_measured_generated_closeout_allowed_before_remote_green"]
        )
        self.assertFalse(gate["private_read_or_real_executor_allowed"])
        self.assertFalse(gate["MARC2_FW2_allowed"])

    def test_document_separates_engineering_and_scientific_boundaries(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("This is not the registered measured closeout", text)
        self.assertIn("No private path", text)


if __name__ == "__main__":
    unittest.main()
