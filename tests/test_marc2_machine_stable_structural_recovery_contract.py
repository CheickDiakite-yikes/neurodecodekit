import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc2_machine_stable_structural_recovery_contract.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_MACHINE_STABLE_STRUCTURAL_RECOVERY_PREREGISTRATION.md"


class Marc2MachineStableStructuralRecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_is_frozen_generated_only(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_machine_stable_structural_recovery_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-VR4")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_implementation_pending",
        )

    def test_both_predecessors_are_remotely_green(self):
        proof = self.contract["green_predecessor_proof"]
        self.assertEqual(proof["VR3_result"]["CI_run_id"], 31964995980)
        self.assertEqual(proof["VR3_result"]["route"], "MARC2VDR-F01")
        self.assertEqual(proof["VR3_result"]["private_input_bytes"], 0)
        self.assertEqual(
            proof["machine_stable_research"]["CI_run_id"], 31965424149
        )
        self.assertTrue(
            proof["machine_stable_research"]["both_required_jobs_green"]
        )

    def test_surface_has_no_execute_or_private_interface(self):
        surface = self.contract["implementation_surface"]
        self.assertEqual(
            surface["commands"], ["plan", "qualify", "inspect", "readiness"]
        )
        self.assertFalse(surface["execute_command"])
        self.assertFalse(surface["private_source_or_private_output_root_constant"])
        self.assertFalse(
            surface["network_archive_neural_target_model_prediction_or_score_interface"]
        )
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_dependency_delta"], 0)

    def test_readiness_wait_and_thresholds_are_exact(self):
        readiness = self.contract["readiness_contract"]
        self.assertEqual(readiness["maximum_wait_seconds"], 600)
        self.assertEqual(readiness["minimum_sample_interval_seconds"], 5)
        self.assertEqual(readiness["maximum_samples"], 121)
        self.assertEqual(readiness["consecutive_passing_samples"], 3)
        self.assertEqual(readiness["normalized_one_minute_load_maximum"], 1.0)
        self.assertEqual(
            readiness["process_peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2
        )
        self.assertEqual(readiness["free_disk_bytes_minimum"], 15 * 1024**3)

    def test_machine_timeout_is_nonconsuming_and_diagnostic(self):
        readiness = self.contract["readiness_contract"]
        self.assertTrue(readiness["specific_refusal_code_and_exact_safe_value_emitted"])
        self.assertFalse(readiness["machine_only_refusal_consumes_future_private_content_open"])
        self.assertFalse(readiness["output_root_or_private_path_operation"])

    def test_certificate_is_fixed_bounded_and_nonauthoritative(self):
        schema = self.contract["certificate_schema"]
        self.assertEqual(schema["mode"], "0600")
        self.assertEqual(schema["maximum_bytes"], 64 * 1024)
        self.assertTrue(schema["ready_false_certificate_allowed"])
        self.assertFalse(schema["generated_ready_true_grants_private_authority"])
        self.assertFalse(schema["symlink_overwrite_or_alternate_path_allowed"])

    def test_future_private_boundary_remains_separate(self):
        future = self.contract["future_private_executor_constraints"]
        self.assertFalse(future["implemented_by_this_contract"])
        self.assertTrue(future["separate_all_false_Tier_C_packet_required"])
        self.assertTrue(future["fresh_packet_bound_decision_required"])
        self.assertFalse(future["second_normalized_load_consuming_gate_allowed"])
        self.assertEqual(future["private_content_opens"], 1)
        self.assertEqual(future["post_marker_retry_rerun_resume_repair_or_fallback_limit"], 0)

    def test_structural_invariants_are_unchanged(self):
        future = self.contract["future_private_executor_constraints"]
        self.assertEqual(future["private_source_bytes"], 418755)
        self.assertEqual(future["source_rows"], 1227)
        self.assertEqual(future["source_bundles"], 238)
        self.assertEqual(future["eligible_bundles"], 195)
        self.assertEqual(future["valid_ineligible_bundles"], 43)
        self.assertEqual(future["VR2_adapter_calls"], 1)
        self.assertEqual(future["archive_member_or_payload_bytes"], 0)

    def test_generated_matrix_has_36_ordered_mutations_and_six_routes(self):
        qualification = self.contract["generated_qualification"]
        self.assertEqual(len(qualification["ordered_mutations"]), 36)
        self.assertEqual(qualification["mutation_count"], 36)
        self.assertEqual(len(set(qualification["ordered_mutations"])), 36)
        self.assertEqual(
            qualification["routes"],
            [
                "MARC2RDY-F00",
                "MARC2RDY-F01",
                "MARC2RDY-F02",
                "MARC2RDY-F03",
                "MARC2RDY-F04",
                "MARC2RDY-F05",
            ],
        )
        self.assertEqual(qualification["success_route"], "MARC2RDY-G1")

    def test_resource_caps_are_small_and_private_free(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["generated_qualification_runtime_seconds"], 30)
        self.assertEqual(caps["certificate_bytes"], 64 * 1024)
        self.assertEqual(caps["incremental_disk_bytes"], 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["private_bytes"], 0)

    def test_every_authority_and_access_counter_is_zero(self):
        self.assertTrue(all(not value for value in self.contract["authorization_state"].values()))
        self.assertTrue(all(value == 0 for value in self.contract["access_counters"].values()))

    def test_next_gate_stops_before_private_FW2_and_CIL1(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["exact_registration_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["generated_only_implementation_after_green"])
        self.assertFalse(gate["private_executor_implementation_from_this_contract"])
        self.assertTrue(gate["fresh_Tier_C_packet_and_decision_for_private_open"])
        self.assertFalse(gate["FW2_or_CIL1_eligible"])

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("This contract does not implement or authorize it", text)
        self.assertIn("Engineering capability specified", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
