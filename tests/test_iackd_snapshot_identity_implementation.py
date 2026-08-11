import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "registries" / "iackd_snapshot_identity_implementation.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSnapshotIdentityImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_schema_and_status_are_generated_only(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["implementation_id"],
            "IACKD-M1-generated-snapshot-canonicalizer-v0",
        )
        self.assertIn("generated_fixture_qualified", self.record["status"])
        self.assertIn("zero_network", self.record["proof_posture"])

    def test_green_registration_is_exact(self) -> None:
        green = self.record["green_registration"]
        self.assertEqual(green["commit"], "1667e302e262ad23695f204a88d5a0997ac38270")
        self.assertEqual(green["push_CI_run_id"], 31481270697)
        self.assertEqual(green["base_python_job_id"], 93746523491)
        self.assertEqual(green["optional_neuro_job_id"], 93746523322)
        self.assertTrue(green["both_required_jobs_green"])

    def test_all_tracked_file_hashes_match(self) -> None:
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_interface_is_dependency_free_and_has_no_real_executor(self) -> None:
        interface = self.record["implemented_interface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["generated_fixture_mode"])
        self.assertTrue(interface["aggregate_inspection_mode"])
        self.assertEqual(interface["registered_tree_rows"], 1679)
        self.assertEqual(interface["registered_selected_rows"], 1340)
        self.assertEqual(interface["registered_refusal_mutations"], 37)
        self.assertFalse(interface["network_opener_exists"])
        self.assertFalse(interface["execute_CLI_exists"])
        self.assertFalse(interface["local_IACKD_path_interface_exists"])
        self.assertFalse(interface["heavy_dependency_imported"])

    def test_measured_generated_qualification_is_exact_and_bounded(self) -> None:
        result = self.record["generated_qualification"]
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["generated_input_bytes"], 531067)
        self.assertEqual(result["generated_output_bytes"], 426792)
        self.assertEqual(result["report_bytes"], 3664)
        self.assertEqual(result["private_manifest_bytes"], 423128)
        self.assertEqual(result["deterministic_replays"], 2)
        self.assertEqual(result["refusal_mutations"], 37)
        self.assertEqual(result["tree_rows"], 1679)
        self.assertEqual(result["selected_rows"], 1340)
        self.assertEqual(result["selected_payload_bytes"], 7249113684)
        self.assertLess(result["runtime_seconds"], 30)
        self.assertLess(result["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(result["network_bytes"], 0)
        self.assertEqual(result["real_or_public_operation_sum"], 0)
        self.assertFalse(result["scientific_claim_upgrade"])

    def test_adversarial_and_resource_contracts_are_preserved(self) -> None:
        coverage = self.record["adversarial_coverage"]
        self.assertEqual(coverage["required_refusal_mutations"], 37)
        self.assertEqual(coverage["deterministic_replays"], 2)
        self.assertTrue(coverage["overflowed_JSON_float_refused"])
        self.assertTrue(coverage["historical_selected_path_set_exact"])
        self.assertTrue(coverage["public_row_path_URL_and_version_ID_leak_refused"])
        resources = self.record["resource_caps"]
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["network_bytes"], 0)

    def test_verification_and_access_boundaries_are_explicit(self) -> None:
        verification = self.record["verification"]
        self.assertEqual(verification["core_implementation_tests"], 16)
        self.assertEqual(verification["implementation_record_tests"], 9)
        self.assertEqual(verification["research_and_contract_tests"], 24)
        self.assertTrue(verification["focused_passed"])
        self.assertTrue(verification["complete_base_suite_passed"])
        self.assertTrue(verification["complete_optional_suite_passed"])
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["CLI_roundtrip_passed"])
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_execution_state_keeps_public_access_closed(self) -> None:
        state = self.record["execution_state"]
        self.assertTrue(state["generated_qualification_consumed"])
        self.assertFalse(state["generated_qualification_rerun_available"])
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["Tier_C_request_exists"])
        self.assertFalse(state["real_transport_wrapper_exists"])
        self.assertFalse(state["public_GraphQL_request_authorized"])
        self.assertFalse(state["public_execution_consumed"])
        self.assertFalse(state["current_continue_is_retroactive_permission"])

    def test_document_separates_engineering_and_scientific_boundaries(self) -> None:
        document = (
            ROOT / "docs" / "IACKD_SNAPSHOT_IDENTITY_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No dataset-specific OpenNeuro response", document)
        claim = self.record["claim_boundary"]
        self.assertIn("snapshot", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
