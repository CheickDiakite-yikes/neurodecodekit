import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = (
    ROOT / "registries" / "iackd_transport_stable_recovery_implementation.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDTransportStableRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD_PATH.read_text(encoding="utf-8"))

    def test_schema_and_status_are_generated_only(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.iackd_transport_stable_recovery_implementation",
        )
        self.assertEqual(self.record["implementation_id"], "IACKD-T1-generated-transport-validator-v0")
        self.assertIn("generated_fixture_qualified", self.record["status"])
        self.assertIn("zero_network", self.record["proof_posture"])

    def test_green_registration_is_exact(self) -> None:
        green = self.record["green_registration"]
        self.assertEqual(green["commit"], "ee0f62adf74afd390052694142090ccc0395c539")
        self.assertEqual(green["push_CI_run_id"], 31472269070)
        self.assertEqual(green["base_python_job_id"], 93717995481)
        self.assertEqual(green["optional_neuro_job_id"], 93717995427)
        self.assertTrue(green["both_required_jobs_green"])

    def test_all_tracked_file_hashes_match(self) -> None:
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_interface_is_dependency_free_and_has_no_real_executor(self) -> None:
        interface = self.record["implemented_interface"]
        self.assertTrue(interface["standard_library_only"])
        self.assertTrue(interface["dry_run_default"])
        self.assertEqual(interface["metadata_framing_profiles"], ["fixed_length", "chunked", "close_delimited"])
        self.assertTrue(interface["metadata_exact_observed_bytes_and_SHA256_required"])
        self.assertTrue(interface["payload_exact_Content_Length_and_ETag_required"])
        self.assertEqual(interface["registered_refusal_mutations"], 22)
        self.assertFalse(interface["network_opener_exists"])
        self.assertFalse(interface["execute_CLI_exists"])
        self.assertFalse(interface["local_IACKD_path_interface_exists"])
        self.assertFalse(interface["heavy_dependency_imported"])

    def test_final_fixture_measurements_are_exact_and_bounded(self) -> None:
        fixture = self.record["final_fixture_qualification"]
        self.assertTrue(fixture["all_gates_passed"])
        self.assertEqual(fixture["accepted_validations"], 10)
        self.assertEqual(fixture["deterministic_replays"], 2)
        self.assertEqual(fixture["refusal_mutations"], 22)
        self.assertEqual(fixture["generated_input_bytes"], 848)
        self.assertEqual(fixture["generated_output_bytes"], 5540)
        self.assertEqual(fixture["peak_RSS_bytes"], 20332544)
        self.assertLess(fixture["runtime_seconds"], 30)
        self.assertTrue(fixture["report_SHA256"].isalnum())
        self.assertEqual(len(fixture["report_SHA256"]), 64)
        self.assertEqual(fixture["network_bytes"], 0)
        self.assertEqual(fixture["real_or_public_operation_sum"], 0)
        self.assertFalse(fixture["scientific_claim_upgrade"])

    def test_coverage_and_verification_match_the_contract(self) -> None:
        coverage = self.record["adversarial_coverage"]
        self.assertEqual(coverage["acceptance_cases"], 5)
        self.assertEqual(coverage["refusal_mutations"], 22)
        self.assertEqual(coverage["deterministic_replays"], 2)
        self.assertTrue(coverage["read_hash_parse_order_enforced"])
        self.assertTrue(coverage["network_constructor_absent"])
        verification = self.record["verification"]
        self.assertEqual(verification["implementation_tests"], 17)
        self.assertEqual(verification["registration_and_research_tests"], 16)
        self.assertTrue(verification["focused_passed"])
        self.assertTrue(verification["ruff_0_15_20_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertTrue(verification["CLI_roundtrip_passed"])
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertFalse(verification["complete_local_suite_run_due_to_external_machine_load"])

    def test_all_access_counters_and_authorizations_remain_zero_or_false(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))
        state = self.record["execution_state"]
        self.assertFalse(state["implementation_commit_remote_green"])
        self.assertFalse(state["Tier_C_request_exists"])
        self.assertFalse(state["real_executor_integration_authorized"])
        self.assertFalse(state["public_execution_authorized"])
        self.assertFalse(state["real_execution_consumed"])

    def test_claim_boundary_is_explicit(self) -> None:
        claim = self.record["claim_boundary"]
        self.assertIn("framing", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])
        document = (
            ROOT / "docs" / "IACKD_TRANSPORT_STABLE_RECOVERY_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No current message authorizes", document)


if __name__ == "__main__":
    unittest.main()
