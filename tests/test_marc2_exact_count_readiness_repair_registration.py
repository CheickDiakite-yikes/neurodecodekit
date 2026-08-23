import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/marc2_exact_count_readiness_repair_contract.v0.json"
DOC = ROOT / "docs/MARC_2_EXACT_COUNT_READINESS_REPAIR_PREREGISTRATION.md"


class Marc2ExactCountReadinessRepairRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_consumed_result_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR33A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR32P_result_commit"],
            "2c3b901b5536191d181c12d54106e45d9574b309",
        )
        self.assertEqual(proof["VR32P_result_CI_run_id"], 32_633_522_416)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR32P-R2")
        self.assertEqual(proof["registered_readiness_samples"], 3)
        self.assertEqual(proof["returned_readiness_samples"], 5)
        self.assertFalse(proof["fully_protocol_conforming"])

    def test_all_fixed_inputs_match_without_private_reinspection(self):
        total = 0
        for item in self.contract["fixed_inputs"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                item["sha256"],
                item["path"],
            )
            total += len(payload)
        self.assertEqual(len(self.contract["fixed_inputs"]), 5)
        self.assertEqual(total, self.contract["fixed_input_bytes"])
        self.assertFalse(
            self.contract["result_proof"][
                "private_source_or_consumed_output_reinspected_by_registration"
            ]
        )

    def test_failure_mechanism_and_no_repair_boundary_are_frozen(self):
        failure = self.contract["failure_localization"]
        self.assertEqual(failure["function_name"], "_collect_private_readiness")
        self.assertIn("while time.monotonic()", failure["open_ended_loop_expression"])
        self.assertEqual(failure["break_expression"], "passing_tail == 3")
        self.assertFalse(failure["VR32P_repair_or_rerun_allowed"])

    def test_exact_count_contract_has_no_dynamic_escape_hatch(self):
        exact = self.contract["exact_count_contract"]
        self.assertEqual(exact["sample_count"], 3)
        self.assertEqual(exact["interval_seconds"], 5.0)
        self.assertEqual(exact["provider_calls_per_collection"], 3)
        self.assertEqual(exact["sleeper_calls_per_collection"], 2)
        self.assertEqual(exact["sequence_values"], [1, 2, 3])
        self.assertFalse(exact["while_loop_allowed"])
        self.assertFalse(exact["sample_count_override_allowed"])
        self.assertFalse(exact["interval_override_allowed"])
        self.assertFalse(exact["timeout_or_retry_allowed"])

    def test_generated_matrix_and_call_counts_are_exact(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["patterns"]), 8)
        self.assertEqual(matrix["ready_patterns"], ["PPP"])
        self.assertEqual(len(matrix["not_ready_patterns"]), 7)
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 16)
        self.assertEqual(matrix["required_provider_calls"], 48)
        self.assertEqual(matrix["required_sleeper_calls"], 32)
        self.assertEqual(matrix["required_returned_samples"], 48)
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 40)
        self.assertEqual(matrix["retained_output_bytes"], 0)

    def test_implementation_surface_is_generated_only(self):
        implementation = self.contract["implementation_contract"]
        self.assertEqual(implementation["commands"], ["plan", "qualify"])
        self.assertEqual(implementation["dependency_policy"], "standard_library_only")
        self.assertEqual(implementation["base_dependency_additions"], 0)
        self.assertFalse(implementation["private_executor_allowed"])
        self.assertEqual(
            implementation[
                "generic_path_URL_timeout_count_interval_route_output_retry_or_resource_arguments"
            ],
            0,
        )
        self.assertFalse(implementation["VR32P_sampler_import_or_call_allowed"])
        self.assertFalse(implementation["consumed_wrapper_modification_allowed"])

    def test_resource_limits_are_small(self):
        limits = self.contract["resource_limits"]
        self.assertEqual(limits["CPU_threads"], 1)
        self.assertEqual(limits["workers"], 1)
        self.assertEqual(limits["numerical_jobs"], 1)
        self.assertLessEqual(limits["runtime_seconds"], 15)
        self.assertLess(limits["peak_RSS_bytes_exclusive"], 256 * 1024**2)
        self.assertLessEqual(limits["generated_input_bytes"], 1024**2)
        self.assertLessEqual(limits["aggregate_output_bytes"], 1024**2)
        self.assertEqual(limits["retained_output_bytes"], 0)
        self.assertEqual(limits["network_bytes"], 0)

    def test_authorization_and_operation_counters_remain_closed(self):
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["artifact_only_reads"])
        self.assertTrue(authorization["generated_in_memory_fixture_creation"])
        self.assertFalse(authorization["private_or_Git_ignored_path_access"])
        self.assertFalse(authorization["readiness_file_or_consumed_state_access"])
        self.assertFalse(authorization["archive_header_or_member_access"])
        self.assertFalse(authorization["signal_event_target_or_label_access"])
        self.assertFalse(
            authorization["model_training_inference_prediction_or_scoring"]
        )
        self.assertFalse(authorization["network_or_provider_calls"])
        self.assertFalse(authorization["FW2_or_CIL1_execution"])
        self.assertFalse(authorization["scientific_claim_upgrade"])
        self.assertTrue(
            all(
                value == 0
                for value in self.contract["registration_operation_counters"].values()
            )
        )

    def test_claim_boundary_and_next_gate_are_explicit(self):
        next_gate = self.contract["next_gate"]
        self.assertTrue(
            next_gate[
                "registration_must_be_committed_pushed_and_both_CI_jobs_green_before_implementation"
            ]
        )
        self.assertFalse(next_gate["private_execution_or_VR32P_repair_authorized"])
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("future private wrapper", text)


if __name__ == "__main__":
    unittest.main()
