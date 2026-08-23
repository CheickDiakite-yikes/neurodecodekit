import ast
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT / "registries/marc2_task_aware_eligibility_repair_contract.v0.json"
)
DOC = ROOT / "docs/MARC_2_TASK_AWARE_ELIGIBILITY_REPAIR_PREREGISTRATION.md"
VR2 = ROOT / "src/neurodecodekit/datasets/marc2_live_domain_eligibility_adapter.py"


class Marc2TaskAwareEligibilityRepairRegistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_identity_and_green_VR34P_proof_are_exact(self):
        self.assertEqual(self.contract["lane_id"], "MARC2-VR35A")
        self.assertEqual(
            self.contract["status"],
            "preregistered_artifact_only_generated_only_no_private_access",
        )
        proof = self.contract["result_proof"]
        self.assertEqual(
            proof["VR34P_result_commit"],
            "22c428b4129244e3cc034d338d805a429316a646",
        )
        self.assertEqual(proof["VR34P_result_CI_run_id"], 32_642_196_932)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["observed_route"], "MARC2VR34P-R2")
        self.assertTrue(proof["protocol_conforming"])

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
        self.assertEqual(len(self.contract["fixed_inputs"]), 11)
        self.assertEqual(total, self.contract["fixed_input_bytes"])
        self.assertFalse(
            self.contract["result_proof"][
                "private_source_or_consumed_output_reinspected_by_registration"
            ]
        )

    def test_registration_artifacts_match(self):
        registration = self.contract["registration_artifacts"]
        for kind in ("document", "test"):
            payload = (ROOT / registration[f"{kind}_path"]).read_bytes()
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                registration[f"{kind}_sha256"],
            )

    def test_static_localization_is_bound_to_exact_code(self):
        source = VR2.read_text(encoding="utf-8")
        tree = ast.parse(source)
        functions = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_classify_key"
        ]
        self.assertEqual(len(functions), 1)
        segment = ast.get_source_segment(source, functions[0])
        self.assertIsNotNone(segment)
        self.assertIn("subject, session, _run = key", segment)
        self.assertNotIn("task", segment)
        localization = self.contract["static_localization"]
        self.assertFalse(localization["classifier_task_dimension_present"])
        self.assertFalse(localization["exact_task_checked_before_eligibility_count"])
        self.assertTrue(localization["compatible_with_R2_but_not_proven_private_cause"])
        self.assertFalse(localization["private_count_value_or_task_distribution_inferred"])

    def test_repair_order_and_selection_boundary_are_frozen(self):
        repair = self.contract["repair_contract"]
        self.assertEqual(repair["published_task_label"], "reachingandgrasping")
        self.assertLess(
            repair["projection_order"].index("project_exact_published_task_bundles"),
            repair["projection_order"].index(
                "classify_projected_bundles_by_frozen_participant_and_session_taxonomy"
            ),
        )
        self.assertEqual(repair["exact_projected_eligible_run_bundles"], 195)
        self.assertEqual(repair["eligible_subjects"], 19)
        self.assertEqual(repair["selected_subjects"], 16)
        self.assertEqual(repair["reservation_cap_bytes"], 8 * 1024**3)
        self.assertFalse(repair["non_target_task_bundle_may_enter_selection"])
        self.assertFalse(repair["source_mutation_allowed"])
        self.assertFalse(repair["count_threshold_task_or_rank_override_allowed"])

    def test_parallel_hypotheses_and_routes_are_exact(self):
        matrix = self.contract["generated_matrix"]
        self.assertEqual(len(matrix["cases"]), 5)
        self.assertEqual(matrix["orders"], ["canonical", "reversed"])
        self.assertEqual(matrix["replays"], 2)
        self.assertEqual(matrix["required_paths"], 20)
        self.assertEqual(
            matrix["expected_route_counts"],
            {
                "MARC2VR35A-G1": 4,
                "MARC2VR35A-G2": 4,
                "MARC2VR35A-R1": 4,
                "MARC2VR35A-R2": 4,
                "MARC2VR35A-R3": 4,
            },
        )
        self.assertEqual(matrix["successful_selection_calls"], 8)
        self.assertEqual(matrix["successful_selection_validation_calls"], 8)
        self.assertTrue(matrix["mixed_task_semantic_cohort_must_equal_baseline"])
        self.assertEqual(matrix["non_target_selected_rows"], 0)
        self.assertGreaterEqual(matrix["minimum_direct_refusals"], 80)
        self.assertEqual(matrix["retained_output_bytes"], 0)

    def test_implementation_surface_is_generated_only(self):
        implementation = self.contract["implementation_contract"]
        self.assertEqual(implementation["commands"], ["plan", "qualify"])
        self.assertEqual(implementation["dependency_policy"], "standard_library_only")
        self.assertEqual(implementation["base_dependency_additions"], 0)
        self.assertFalse(implementation["private_executor_allowed"])
        self.assertEqual(
            implementation[
                "generic_path_URL_output_count_threshold_task_rank_cap_route_retry_or_resource_arguments"
            ],
            0,
        )
        self.assertFalse(
            implementation["consumed_VR20P_VR34P_module_import_or_call_allowed"]
        )
        self.assertFalse(implementation["private_or_Git_ignored_source_access_allowed"])

    def test_resource_limits_are_small(self):
        limits = self.contract["resource_limits"]
        self.assertEqual(limits["CPU_threads"], 1)
        self.assertEqual(limits["workers"], 1)
        self.assertEqual(limits["numerical_jobs"], 1)
        self.assertLessEqual(limits["runtime_seconds"], 45)
        self.assertLess(limits["peak_RSS_bytes_exclusive"], 256 * 1024**2 + 1)
        self.assertLessEqual(limits["generated_input_bytes"], 16 * 1024**2)
        self.assertLessEqual(limits["aggregate_output_bytes"], 1024**2)
        self.assertEqual(limits["retained_output_bytes"], 0)
        self.assertEqual(limits["network_bytes"], 0)
        verification = self.contract["registration_verification"]
        self.assertEqual(verification["focused_registration_tests_passed"], 10)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 5425)
        self.assertEqual(verification["expected_skips"], 204)
        self.assertEqual(verification["test_delta"], 10)
        self.assertTrue(verification["repository_pinned_ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertEqual(verification["registry_JSON_files_parsed"], 413)
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertEqual(verification["private_operations_during_verification"], 0)

    def test_authorization_and_operation_counters_remain_closed(self):
        authorization = self.contract["authorization"]
        self.assertTrue(authorization["artifact_only_reads"])
        self.assertTrue(authorization["generated_in_memory_fixture_creation"])
        self.assertFalse(authorization["private_or_Git_ignored_path_access"])
        self.assertFalse(authorization["readiness_file_or_consumed_state_access"])
        self.assertFalse(authorization["archive_header_or_member_access"])
        self.assertFalse(authorization["signal_event_channel_geometry_target_or_label_access"])
        self.assertFalse(authorization["cohort_freeze"])
        self.assertFalse(authorization["model_training_inference_prediction_or_scoring"])
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
        self.assertFalse(next_gate["private_execution_or_consumed_lane_reinspection_authorized"])
        self.assertTrue(
            next_gate[
                "new_private_cohort_freeze_requires_separate_frozen_Tier_C_packet_and_decision"
            ]
        )
        claims = self.contract["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["real_cohort_established"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability proposed", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("future private wrapper", text)


if __name__ == "__main__":
    unittest.main()
