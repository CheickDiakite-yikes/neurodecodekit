import hashlib
import json
import unittest
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "marc2_proof_record_recovery_contract.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2ProofRecordRecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_status_and_posture_are_exact(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_proof_record_recovery_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC2-FW1B")
        self.assertEqual(
            self.contract["contract_id"],
            "MARC-2-FW1B-proof-record-recovery-contract-v0",
        )
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_no_implementation_or_private_execution",
        )
        self.assertEqual(
            self.contract["proof_posture"],
            "prospective_generated_proof_record_recovery_only",
        )

    def test_all_bound_artifacts_are_exact(self):
        bindings = self.contract["artifact_bindings"]
        self.assertEqual(len(bindings), 4)
        for binding in bindings:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_green_consumed_predecessor_is_fully_bound(self):
        proof = self.contract["green_predecessor_result"]
        self.assertEqual(
            proof["commit"],
            "4f08553eaa27c83e3f9ace9226dce64d933be1d4",
        )
        self.assertEqual(proof["CI_run_id"], 31_766_526_262)
        self.assertEqual(proof["base_python_job_id"], 94_663_482_811)
        self.assertEqual(proof["optional_neuro_job_id"], 94_663_482_786)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["result_registry_sha256"],
            sha256_file(
                ROOT
                / "registries"
                / "marc2_freewill_private_selection_failure_result.v0.json"
            ),
        )

    def test_old_lane_is_consumed_and_cannot_be_reused(self):
        boundary = self.contract["consumed_predecessor_boundary"]
        self.assertTrue(boundary["MARC2_FW1A_consumed"])
        for key, value in boundary.items():
            if key == "MARC2_FW1A_consumed":
                continue
            self.assertFalse(value, key)

    def test_candidate_record_requires_lane_id_and_exact_fields(self):
        identity = self.contract["candidate_record_identity"]
        self.assertEqual(identity["lane_id"], "MARC2-FW1B")
        self.assertEqual(
            identity["schema_name"],
            "neurodecodekit.marc2_proof_record_recovery_implementation",
        )
        fields = identity["required_top_level_fields_in_order"]
        self.assertEqual(len(fields), 15)
        self.assertEqual(fields[2], "lane_id")
        self.assertEqual(len(fields), len(set(fields)))
        for key, value in identity.items():
            if key in {
                "schema_name",
                "schema_version",
                "lane_id",
                "implementation_id",
                "status",
                "required_top_level_fields_in_order",
            }:
                continue
            self.assertFalse(value, key)

    def test_tracked_artifact_policy_is_strict_and_non_circular(self):
        policy = self.contract["tracked_artifact_policy"]
        self.assertGreaterEqual(policy["minimum_bindings"], 3)
        self.assertTrue(policy["paths_must_be_unique"])
        self.assertTrue(policy["paths_must_be_normalized_repository_relative"])
        self.assertFalse(policy["absolute_tilde_dot_or_dotdot_paths_allowed"])
        self.assertFalse(policy["symlink_or_nonregular_artifacts_allowed"])
        self.assertFalse(policy["candidate_registry_may_bind_itself"])
        self.assertTrue(
            policy["candidate_registry_supplied_as_separately_hashed_validator_input"]
        )
        for binding in self.contract["artifact_bindings"]:
            path = PurePosixPath(binding["path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)

    def test_surface_is_generated_only_and_dependency_free(self):
        surface = self.contract["implementation_surface"]
        self.assertEqual(
            surface["module"],
            "neurodecodekit.datasets.marc2_proof_record_recovery",
        )
        self.assertEqual(
            surface["shared_validator_symbol"],
            "validate_implementation_record",
        )
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["heavy_dependency_imports"], 0)
        for key, value in surface.items():
            if key in {
                "module",
                "shared_validator_symbol",
                "commands",
                "standard_library_only",
                "heavy_dependency_imports",
            }:
                continue
            self.assertFalse(value, key)

    def test_one_shared_validator_path_is_required(self):
        shared = self.contract["shared_validator_contract"]
        self.assertTrue(shared["generated_qualification_calls_exact_public_symbol"])
        self.assertTrue(shared["future_additive_live_wrapper_must_call_exact_public_symbol"])
        self.assertFalse(
            shared["copy_fork_alias_weakening_or_reimplementation_allowed"]
        )
        self.assertTrue(shared["canonical_record_passes_twice"])
        self.assertTrue(shared["canonical_summary_bytes_identical_on_replay"])
        self.assertEqual(len(shared["proof_envelope_fields"]), 8)
        self.assertIn("implementation_registry_sha256", shared["proof_envelope_fields"])

    def test_all_32_ordered_mutations_have_registered_routes(self):
        mutations = self.contract["ordered_mutations"]
        routes = self.contract["mutation_routes"]
        self.assertEqual(len(mutations), 32)
        self.assertEqual(len(mutations), len(set(mutations)))
        self.assertEqual(tuple(routes), tuple(mutations))
        self.assertEqual(set(routes.values()), {
            "MARC2FWR-F00",
            "MARC2FWR-F01",
            "MARC2FWR-F02",
            "MARC2FWR-F03",
            "MARC2FWR-F04",
            "MARC2FWR-F05",
        })
        self.assertEqual(routes["lane_id_missing"], "MARC2FWR-F00")
        self.assertEqual(
            routes["generated_closure_uses_different_validator"],
            "MARC2FWR-F05",
        )

    def test_routes_have_no_private_or_live_success(self):
        routes = self.contract["routes"]
        self.assertEqual(len(routes), 7)
        self.assertEqual(routes["MARC2FWR-G1"], (
            "generated_candidate_refusal_matrix_and_shared_validator_identity_pass"
        ))
        self.assertFalse(any("private" in value or "live" in value for value in routes.values()))

    def test_all_18_acceptance_gates_and_resource_caps_are_frozen(self):
        self.assertEqual(len(self.contract["acceptance_gates"]), 18)
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["generated_input_bytes"], 1024**2)
        self.assertEqual(caps["combined_output_bytes"], 1024**2)
        self.assertEqual(caps["incremental_disk_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["private_or_real_input_bytes"], 0)

    def test_execution_state_has_zero_private_limit(self):
        state = self.contract["execution_state"]
        self.assertFalse(state["contract_execution_consumed"])
        self.assertTrue(state["generated_implementation_may_start_after_contract_remote_green"])
        self.assertEqual(state["registered_private_execution_limit"], 0)
        self.assertEqual(state["retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertFalse(state["private_selection_result_available"])
        self.assertFalse(state["MARC2_FW2_eligible"])

    def test_every_authority_flag_and_access_counter_is_zero(self):
        self.assertGreaterEqual(len(self.contract["authorization_flags"]), 16)
        self.assertTrue(
            all(value is False for value in self.contract["authorization_flags"].values())
        )
        self.assertGreaterEqual(len(self.contract["access_counters"]), 20)
        self.assertTrue(all(value == 0 for value in self.contract["access_counters"].values()))

    def test_next_gate_requires_new_packet_and_fresh_decision(self):
        gate = self.contract["next_gate"]
        self.assertTrue(gate["contract_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(gate["generated_only_implementation_after_green_contract"])
        self.assertFalse(gate["private_access_authorized_now"])
        self.assertTrue(gate["all_false_Tier_C_request_only_after_green_implementation"])
        self.assertTrue(gate["fresh_packet_bound_decision_required_before_live_wrapper"])
        self.assertTrue(gate["live_wrapper_remote_green_required_before_private_path"])
        self.assertFalse(gate["MARC2_FW2_eligible_now"])
        self.assertFalse(gate["earlier_continue_is_retroactive_authority"])

    def test_claim_boundary_is_engineering_only(self):
        boundary = self.contract["claim_boundary"]
        self.assertIn("reusable implementation-record validator", boundary["engineering_capability_sought"])
        self.assertIn("no human neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])
        self.assertGreaterEqual(len(self.contract["warnings"]), 4)
        self.assertGreaterEqual(len(self.contract["unavailable_fields"]), 6)


if __name__ == "__main__":
    unittest.main()
