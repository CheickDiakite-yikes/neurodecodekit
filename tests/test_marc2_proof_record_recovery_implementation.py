import hashlib
import json
import unittest
from pathlib import Path, PurePosixPath

from neurodecodekit.datasets import marc2_proof_record_recovery as recovery


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc2_proof_record_recovery_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2ProofRecordRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.payload.decode("utf-8"))

    def test_registry_is_accepted_by_the_exact_shared_validator(self):
        proof = recovery._generated_proof(self.payload)
        summary = recovery.validate_implementation_record(
            self.payload,
            repo_root=ROOT,
            expected_proof=proof,
            observed_proof=proof,
        )
        self.assertEqual(summary.lane_id, "MARC2-FW1B")
        self.assertEqual(summary.top_level_field_count, 15)
        self.assertEqual(summary.tracked_binding_count, 6)
        self.assertEqual(summary.validator_module, recovery.MODULE_NAME)
        self.assertEqual(
            summary.validator_symbol,
            recovery.validate_implementation_record.__name__,
        )
        self.assertEqual(summary.record_sha256, hashlib.sha256(self.payload).hexdigest())

    def test_top_level_identity_and_lane_id_are_exact(self):
        self.assertEqual(tuple(self.record), recovery.EXPECTED_TOP_LEVEL_FIELDS)
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_proof_record_recovery_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-FW1B")
        self.assertEqual(
            self.record["status"],
            "generated_shared_proof_validator_qualified_no_private_authority",
        )

    def test_green_contract_and_consumed_result_are_bound(self):
        proof = self.record["predecessor_proof"]
        self.assertEqual(proof["green_contract"]["commit"], (
            "b86aa940d47a232535ee1e72fb22ad58ea5c2729"
        ))
        self.assertEqual(proof["green_contract"]["CI_run_id"], 31_767_373_647)
        self.assertTrue(proof["green_contract"]["both_required_jobs_green"])
        self.assertEqual(proof["consumed_result"]["commit"], (
            "4f08553eaa27c83e3f9ace9226dce64d933be1d4"
        ))
        self.assertEqual(
            proof["consumed_result"]["result_registry_sha256"],
            "56ccc534ce682b45a3dcea6f4e301261a060ccf0ebd6f8f34a7dbed9071899c5",
        )

    def test_all_tracked_artifacts_are_unique_safe_and_exact(self):
        seen: set[str] = set()
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                pure = PurePosixPath(binding["path"])
                self.assertFalse(pure.is_absolute())
                self.assertNotIn("..", pure.parts)
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )
        self.assertNotIn(
            recovery.IMPLEMENTATION_REGISTRY_RELATIVE_PATH.as_posix(),
            seen,
        )

    def test_surface_uses_one_canonical_shared_validator(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["module"], recovery.MODULE_NAME)
        self.assertEqual(
            surface["shared_validator_symbol"],
            recovery.validate_implementation_record.__name__,
        )
        self.assertEqual(
            surface["generated_closure_symbol"],
            recovery.validate_implementation_record.__name__,
        )
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["heavy_dependency_imports"], 0)

    def test_measured_generated_qualification_is_exact_and_bounded(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["route"], "MARC2FWR-G1")
        self.assertTrue(measured["all_gates_passed"])
        self.assertEqual(measured["shared_validator_call_count"], 34)
        self.assertEqual(measured["canonical_replays"], 2)
        self.assertTrue(measured["canonical_summary_byte_identical"])
        self.assertEqual(measured["generated_input_bytes"], 84_701)
        self.assertEqual(measured["combined_output_bytes"], 6_711)
        self.assertEqual(measured["peak_RSS_bytes"], 27_099_136)
        self.assertAlmostEqual(
            measured["runtime_seconds"],
            0.01692712500516791,
        )
        self.assertTrue(measured["temporary_output_removed"])

    def test_all_32_mutations_and_route_counts_are_exact(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["proof_record_mutations_passed"], 32)
        self.assertEqual(
            tuple(measured["proof_record_mutation_order"]),
            recovery.ORDERED_MUTATIONS,
        )
        self.assertEqual(measured["mutation_route_counts"], {
            "MARC2FWR-F00": 7,
            "MARC2FWR-F01": 7,
            "MARC2FWR-F02": 5,
            "MARC2FWR-F03": 4,
            "MARC2FWR-F04": 7,
            "MARC2FWR-F05": 2,
        })
        self.assertEqual(sum(measured["mutation_route_counts"].values()), 32)

    def test_measurement_metadata_preserves_zero_context_and_no_latency_claim(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertTrue(
            measured[
                "private_real_network_payload_neural_target_model_score_counters_zero"
            ]
        )
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertEqual(measured["producer_is_causal"], "not_applicable_metadata_only")

    def test_private_execution_state_remains_zero_and_ineligible(self):
        state = self.record["execution_state"]
        self.assertFalse(state["registered_private_execution_consumed"])
        self.assertEqual(state["registered_private_execution_limit"], 0)
        self.assertEqual(state["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertFalse(state["private_selection_result_available"])
        self.assertFalse(state["MARC2_FW2_eligible"])

    def test_every_authority_flag_and_access_counter_is_zero(self):
        self.assertTrue(
            all(value is False for value in self.record["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_next_gate_requires_green_implementation_and_new_tier_c_packet(self):
        gate = self.record["next_gate"]
        self.assertTrue(
            gate["implementation_commit_push_and_both_remote_jobs_green_required"]
        )
        self.assertFalse(gate["private_access_authorized_now"])
        self.assertTrue(gate["all_false_Tier_C_request_only_after_green_implementation"])
        self.assertTrue(gate["fresh_packet_bound_decision_required_before_live_wrapper"])
        self.assertTrue(gate["live_wrapper_remote_green_required_before_private_path"])
        self.assertFalse(gate["MARC2_FW2_eligible_now"])
        self.assertFalse(gate["earlier_continue_is_retroactive_authority"])

    def test_report_hash_and_verification_state_are_explicit(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(
            measured["report_sha256"],
            "80ee6a1222c53a5545504421eaec0216d14e724d1b3dec2d8e6023c81456634f",
        )
        self.assertEqual(measured["focused_behavior_tests"], 23)
        self.assertEqual(measured["focused_contract_tests"], 15)
        self.assertEqual(measured["focused_implementation_tests"], 13)
        self.assertEqual(measured["complete_base_tests"], 3_134)
        self.assertEqual(measured["complete_base_skips"], 204)
        self.assertEqual(measured["complete_optional_tests"], 3_205)
        self.assertEqual(measured["complete_optional_skips"], 35)
        self.assertFalse(measured["complete_suite_verification_pending"])
        self.assertTrue(measured["remote_CI_pending"])

    def test_claim_boundary_reports_engineering_not_science(self):
        boundary = self.record["claim_boundary"]
        self.assertIn(
            "shared implementation-record validator",
            boundary["engineering_capability_added"],
        )
        self.assertIn("no human neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
