import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT / "registries" / "iackd_channel_role_geometry_implementation.v0.json"
)
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_channel_role_geometry_implementation.py": (
        "d5f7c40dd30050d6067adefc5afd6c7f3e19a756d313999a2afbe053e91a2491"
    ),
    ".github/workflows/ci.yml": (
        "b2dfcf8214b3b5d975e7a432e7c8ff0b6da9b0f1108fcef681cc22310ba50bba"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDChannelRoleGeometryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_schema_and_status_are_fixture_only(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_channel_role_geometry_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertIn("fixture_qualified", self.record["status"])
        self.assertIn("zero_real_metadata", self.record["proof_posture"])

    def test_green_registration_is_exact(self):
        green = self.record["green_registration"]
        self.assertEqual(green["commit"], "228ccd03f5e0b5d02ba104e13b77b04f2032df78")
        self.assertEqual(green["push_CI_run_id"], 31427931578)
        self.assertEqual(green["base_python_job_id"], 93583989913)
        self.assertEqual(green["optional_neuro_job_id"], 93583989996)
        self.assertTrue(green["both_required_jobs_green"])

    def test_every_tracked_implementation_file_hash_matches(self):
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                if binding["path"] in HISTORICAL_MUTABLE_BINDINGS:
                    self.assertEqual(
                        binding["sha256"], HISTORICAL_MUTABLE_BINDINGS[binding["path"]]
                    )
                else:
                    self.assertEqual(sha256(ROOT / binding["path"]), binding["sha256"])

    def test_interface_is_dependency_free_dry_run_first_and_aggregate(self):
        interface = self.record["implemented_interface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["dry_run_default"])
        self.assertTrue(interface["generated_fixture_mode"])
        self.assertTrue(interface["bounded_inspection_mode"])
        self.assertTrue(interface["future_real_execute_mode_requires_separate_decision"])
        self.assertEqual(interface["registered_objects"], 316)
        self.assertEqual(interface["registered_body_bytes"], 457602)
        self.assertEqual(interface["diagnostic_routes"], 5)
        self.assertFalse(interface["raw_body_persistence"])
        self.assertFalse(interface["local_bundle_access"])
        self.assertFalse(interface["per_object_public_output"])

    def test_fixture_measurements_and_constructed_route_are_exact(self):
        fixture = self.record["fixture_qualification"]
        self.assertTrue(fixture["all_gates_passed"])
        self.assertEqual(fixture["generated_metadata_bodies"], 316)
        self.assertEqual(fixture["generated_input_bytes"], 457602)
        self.assertEqual(fixture["body_SHA256_passes"], 316)
        self.assertEqual(fixture["semantic_parse_passes"], 316)
        self.assertEqual(fixture["synthetic_diagnostic_route"], "IACKDR-R4")
        self.assertEqual(fixture["channel_schema_groups"], 2)
        self.assertEqual(fixture["core_schema_groups"], 1)
        self.assertEqual(fixture["geometry_groups"], 30)
        self.assertEqual(fixture["network_bytes"], 0)
        self.assertEqual(fixture["real_or_protected_operation_sum"], 0)
        self.assertFalse(fixture["scientific_claim_upgrade"])

    def test_resources_and_adversarial_coverage_match_contract(self):
        resources = self.record["real_execution_caps"]
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["concurrent_numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["wall_time_seconds"], 180)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["requests"], 316)
        self.assertEqual(resources["expected_body_bytes"], 457602)
        self.assertEqual((resources["retries"], resources["reruns"]), (0, 0))
        coverage = self.record["adversarial_coverage"]
        self.assertEqual(
            coverage["router_outcomes_covered"],
            ["IACKDR-R0", "IACKDR-R1", "IACKDR-R2", "IACKDR-R3", "IACKDR-R4"],
        )
        self.assertEqual(coverage["deterministic_full_surface_replays"], 2)
        self.assertTrue(coverage["network_constructor_patched_closed_in_default_CLI_test"])
        verification = self.record["verification"]
        self.assertEqual(verification["focused_tests"], 47)
        self.assertEqual(verification["complete_base_tests"], 1751)
        self.assertEqual(verification["complete_optional_tests"], 1822)
        self.assertEqual(verification["registry_JSON_files_valid"], 130)
        self.assertTrue(
            all(
                verification[field]
                for field in (
                    "focused_passed",
                    "complete_base_suite_passed",
                    "complete_optional_suite_passed",
                    "ruff_passed",
                    "compileall_passed",
                    "module_CLI_help_default_fixture_inspect_missing_execute_passed",
                    "git_diff_check_passed",
                )
            )
        )

    def test_all_implementation_access_counters_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.record["implementation_access_counters"].values())
        )
        state = self.record["execution_state"]
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["real_authorization_decision_exists"])
        self.assertFalse(state["real_execution_consumed"])
        self.assertFalse(state["real_output_created"])
        self.assertFalse(state["rerun_available"])

    def test_document_states_separate_engineering_and_scientific_boundaries(self):
        document = (
            ROOT / "docs" / "IACKD_CHANNEL_ROLE_GEOMETRY_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("generated fixture", document)
        self.assertIn("No decision artifact exists", document)
        claim = self.record["claim_boundary"]
        self.assertIn("count-agnostic", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
