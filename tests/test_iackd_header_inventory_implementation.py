import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/iackd_channel_inventory_implementation.v0.json"
DOCUMENT_PATH = ROOT / "docs/IACKD_CHANNEL_INVENTORY_IMPLEMENTATION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDHeaderInventoryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_keeps_real_stage_closed_until_new_green_decision(self):
        self.assertEqual(
            self.registry["status"],
            "fixture_qualified_exact_implementation_requires_remote_green_before_real_access",
        )
        state = self.registry["execution_state"]
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["real_authorization_decision_exists"])
        self.assertFalse(state["real_execution_consumed"])
        self.assertFalse(state["rerun_available"])

    def test_green_registration_proof_is_exact(self):
        self.assertEqual(
            self.registry["green_registration"],
            {
                "commit": "0e52278aaa1d15e70f4baab7b21ab1c96eb37f67",
                "push_CI_run_id": 31412667060,
                "base_python_job_id": 93534203368,
                "optional_neuro_job_id": 93534203385,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            self.registry["contract_sha256"],
            sha256(ROOT / "registries/iackd_channel_inventory_contract.v0.json"),
        )

    def test_every_owned_implementation_hash_is_current(self):
        paths = set()
        for row in self.registry["tracked_file_hashes"]:
            self.assertNotIn(row["path"], paths)
            paths.add(row["path"])
            self.assertEqual(row["sha256"], sha256(ROOT / row["path"]), row["path"])
        for required in (
            "src/neurodecodekit/preprocess/iackd_header_inventory.py",
            "tests/test_iackd_header_inventory.py",
            "tests/test_iackd_header_inventory_implementation.py",
            "docs/IACKD_CHANNEL_INVENTORY_IMPLEMENTATION.md",
            ".github/workflows/ci.yml",
        ):
            self.assertIn(required, paths)

    def test_fixture_qualification_is_measured_and_target_free(self):
        qualification = self.registry["fixture_qualification"]
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["generated_VHDR_bodies"], 128)
        self.assertEqual(qualification["generated_input_bytes"], 161_792)
        self.assertEqual(qualification["body_SHA256_passes"], 128)
        self.assertEqual(qualification["semantic_parse_passes"], 128)
        self.assertEqual(qualification["generated_output_bytes"], 4_465)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertEqual(qualification["real_or_protected_operation_sum"], 0)
        self.assertEqual(qualification["real_only_gates_false"], 3)

    def test_interface_is_dependency_light_and_preserves_consumed_cli_hash(self):
        interface = self.registry["implemented_interface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["dry_run_default"])
        self.assertEqual(interface["registered_objects"], 128)
        self.assertEqual(interface["registered_body_bytes"], 161_792)
        self.assertEqual(interface["public_name_allowlist"], 7)
        self.assertEqual(interface["diagnostic_routes"], 6)
        self.assertEqual(
            interface["preserved_central_cli_sha256"],
            sha256(ROOT / "src/neurodecodekit/cli.py"),
        )

    def test_real_and_forbidden_access_counters_are_all_zero(self):
        for name, value in self.registry["implementation_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_verification_and_resource_bounds_are_explicit(self):
        verification = self.registry["verification"]
        self.assertEqual(verification["focused_tests"], 32)
        self.assertTrue(verification["focused_passed"])
        self.assertTrue(verification["complete_base_suite_passed"])
        self.assertTrue(verification["complete_optional_suite_passed"])
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["module_CLI_help_dry_run_fixture_inspect_passed"])
        resources = self.registry["real_execution_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["public_generated_output_bytes"], 1024 * 1024)
        self.assertEqual(resources["retries"], 0)
        self.assertEqual(resources["reruns"], 0)

    def test_document_preserves_engineering_and_scientific_boundaries(self):
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("There is currently no decision file", document)
        self.assertIn("no real IACKD header", document)


if __name__ == "__main__":
    unittest.main()
