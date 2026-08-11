import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries" / "iackd_source_semantics_implementation.v0.json"
DOCUMENT_PATH = ROOT / "docs" / "IACKD_SOURCE_SEMANTICS_IMPLEMENTATION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSourceSemanticsImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_schema_status_and_proof_posture_are_synthetic_only(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_source_semantics_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertIn("pending_exact_implementation_remote_green", self.record["status"])
        self.assertIn("zero_real_public_local_bundle", self.record["proof_posture"])

    def test_green_research_gate_is_exact(self):
        green = self.record["green_research"]
        self.assertEqual(green["commit"], "ed5ce8292c2c1dc842898023cfe8cb608e9d4476")
        self.assertEqual(green["push_CI_run_id"], 31_445_790_741)
        self.assertEqual(green["base_python_job_id"], 93_639_606_343)
        self.assertEqual(green["optional_neuro_job_id"], 93_639_606_403)
        self.assertTrue(green["both_required_jobs_green"])

    def test_policy_binding_is_exact_and_version_aware(self):
        binding = self.record["policy_binding"]
        self.assertEqual(
            binding["policy_sha256"],
            "1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4",
        )
        self.assertEqual(binding["dataset_BIDS_version"], "1.7.0")
        self.assertEqual(binding["dataset_misc_count_field"], "MiscChannelCount")
        self.assertEqual(binding["current_BIDS_migration_field"], "MISCChannelCount")

    def test_every_tracked_implementation_hash_matches(self):
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256(ROOT / binding["path"]), binding["sha256"])

    def test_interface_is_dependency_free_and_has_no_real_execute_surface(self):
        interface = self.record["implemented_interface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["dry_run_default"])
        self.assertTrue(interface["generated_fixture_mode"])
        self.assertTrue(interface["bounded_inspection_mode"])
        self.assertFalse(interface["real_execute_mode_exists"])
        self.assertFalse(interface["top_level_CLI_integration_added"])
        self.assertEqual(interface["fixture_row_counts"], [29, 31])
        self.assertEqual(interface["predictive_EEG_count_per_fixture"], 26)
        self.assertFalse(interface["raw_fixture_rows_in_report"])
        self.assertFalse(interface["generated_coordinates_in_report"])

    def test_mutations_cover_twelve_distinct_fail_closed_classes(self):
        coverage = self.record["adversarial_coverage"]
        self.assertEqual(coverage["generated_mutation_attempts"], 13)
        self.assertEqual(coverage["distinct_refusal_classes"], 12)
        self.assertIn("count_spelling", coverage["mutation_names"])
        self.assertIn("target_firewall", coverage["mutation_names"])
        self.assertIn("functional_role_overlap", coverage["mutation_names"])
        self.assertIn("new_heavy_import", coverage["additional_qualified_conditions"])

    def test_resources_verification_and_all_access_counters_are_bounded(self):
        resources = self.record["resource_caps"]
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["concurrent_numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["generated_output_bytes"], 2 * 1024 * 1024)
        verification = self.record["verification"]
        self.assertEqual(verification["focused_research_and_implementation_tests"], 43)
        self.assertEqual(verification["complete_base_tests"], 1824)
        self.assertEqual(verification["complete_optional_tests"], 1895)
        self.assertEqual(verification["registry_JSON_files_valid"], 135)
        self.assertTrue(
            all(
                verification[field]
                for field in (
                    "focused_passed",
                    "complete_base_suite_passed",
                    "complete_optional_suite_passed",
                    "ruff_passed",
                    "compileall_passed",
                    "module_CLI_help_default_fixture_inspect_passed",
                    "git_diff_check_passed",
                )
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.record["implementation_access_counters"].values())
        )

    def test_execution_state_holds_measured_closeout_and_real_data_closed(self):
        state = self.record["execution_state"]
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["measured_generated_closeout_executed"])
        self.assertFalse(state["real_reader_authorized"])
        self.assertFalse(state["public_or_local_source_body_access_authorized"])
        self.assertFalse(state["IACKD2_authorized"])

    def test_document_separates_engineering_and_scientific_boundaries(self):
        self.assertIn("Engineering capability added:", self.document)
        self.assertIn("Scientific claim not established:", self.document)
        self.assertIn("There is no real-data or `--execute` mode", self.document)
        claim = self.record["claim_boundary"]
        self.assertIn("version-aware", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
