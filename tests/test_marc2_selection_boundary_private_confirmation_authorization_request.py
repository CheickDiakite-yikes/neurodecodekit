import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_selection_boundary_private_confirmation_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs/MARC_2_SELECTION_BOUNDARY_PRIVATE_CONFIRMATION_AUTHORIZATION_PACKET.md"
)


class Marc2SelectionBoundaryPrivateConfirmationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request_bytes = REQUEST_PATH.read_bytes()
        cls.request = json.loads(cls.request_bytes)

    def test_identity_is_local_all_false_request(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_selection_boundary_private_confirmation_authorization_request",
        )
        self.assertEqual(self.request["lane_id"], "MARC2-VR26P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_local_remote_proof_pending",
        )
        self.assertEqual(
            self.request["proof_posture"],
            "request_only_no_private_real_or_scientific_operation_authorized",
        )

    def test_green_predecessor_order_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["VR24P_consumed_result"]["commit"],
            "a873f1a2ac796d5616339c7827b11af2a02bc63c",
        )
        self.assertEqual(proof["VR24P_consumed_result"]["route"], "MARC2VR24P-R2")
        self.assertFalse(proof["VR24P_consumed_result"]["private_source_reopened"])
        self.assertEqual(
            proof["VR25A_registration"]["commit"],
            "ad8be2197e58d4d3e0e1fe4f344de1c608930f73",
        )
        self.assertEqual(
            proof["VR25A_implementation"]["commit"],
            "891245d73d8e11304d4a98e841ead6f57ad68ff8",
        )
        closeout = proof["VR25A_proof_closeout"]
        self.assertEqual(
            closeout["commit"], "378e863641418e0e538f3159d073dd4bcd9c8899"
        )
        self.assertEqual(closeout["CI_run_id"], 32_605_475_758)
        self.assertEqual(closeout["base_python_job_id"], 97_109_778_233)
        self.assertEqual(closeout["optional_neuro_job_id"], 97_109_778_216)
        self.assertTrue(closeout["both_required_jobs_green"])
        self.assertFalse(closeout["generated_qualification_repeated"])
        self.assertFalse(closeout["private_operation_performed"])

    def test_every_fixed_artifact_is_current_and_tracked(self):
        total = 0
        roles = set()
        for binding in self.request["fixed_committed_artifacts"]:
            path = ROOT / binding["path"]
            payload = path.read_bytes()
            with self.subTest(role=binding["role"]):
                self.assertNotIn(binding["role"], roles)
                roles.add(binding["role"])
                self.assertEqual(len(payload), binding["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])
                total += binding["bytes"]
        summary = self.request["fixed_artifact_summary"]
        self.assertEqual((len(roles), total), (14, 175_543))
        self.assertEqual(summary["count"], len(roles))
        self.assertEqual(summary["bytes"], total)
        self.assertTrue(summary["all_paths_tracked_and_not_Git_ignored"])

    def test_all_current_authority_and_operations_are_false_or_zero(self):
        self.assertTrue(
            all(
                value is False
                for value in self.request["current_authorization_flags"].values()
            )
        )
        self.assertTrue(
            all(
                value == 0
                for value in self.request["current_operation_counters"].values()
            )
        )

    def test_source_identity_is_bound_without_private_count_or_access(self):
        source = self.request["private_source_identity"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["regular_files"], 1_025)
        self.assertEqual(source["directories"], 202)
        self.assertEqual(source["required_eligible_bundles"], 195)
        self.assertIsNone(source["observed_complete_bundle_count"])
        self.assertIsNone(source["observed_count_difference_or_direction"])
        self.assertFalse(source["observed_count_may_be_inferred_or_published"])
        self.assertEqual(source["current_path_checks"], 0)
        self.assertEqual(source["current_content_opens"], 0)
        self.assertEqual(source["current_bytes_read"], 0)
        self.assertEqual(source["future_content_open_limit"], 1)

    def test_future_paths_are_fixed_new_and_distinct_from_consumed_paths(self):
        paths = self.request["future_fixed_paths"]
        self.assertIn("vr26p", paths["fresh_readiness_certificate"])
        self.assertIn("selection_boundary", paths["new_output_root"])
        self.assertNotIn(paths["new_output_root"], paths["named_consumed_paths"])
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertTrue(paths["new_output_root_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertFalse(paths["source_or_output_substitution_allowed"])
        self.assertFalse(
            paths["generic_path_URL_output_threshold_retry_or_execute_override_allowed"]
        )

    def test_future_firewall_is_exact_and_does_not_relax_neighbors(self):
        firewall = self.request["future_firewall_contract"]
        self.assertEqual(
            firewall["exact_function"],
            "neurodecodekit.datasets.marc2_selection_boundary_firewall.apply_selection_boundary_firewall",
        )
        self.assertEqual(firewall["exact_real_calls"], 1)
        self.assertEqual(
            firewall["VR25A_success_routes"],
            ["MARC2VR25A-G1", "MARC2VR25A-G2"],
        )
        self.assertEqual(
            firewall["private_success_routes"],
            ["MARC2VR26P-R1", "MARC2VR26P-R2"],
        )
        self.assertTrue(firewall["public_compatibility_boolean_allowed"])
        self.assertFalse(
            firewall["observed_complete_bundle_count_difference_or_direction_allowed"]
        )
        self.assertTrue(firewall["exact_eligible_distribution_required"])
        self.assertTrue(firewall["known_ineligible_quarantine_required"])
        self.assertFalse(
            firewall["identity_task_companion_taxonomy_or_eligibility_broadening_allowed"]
        )
        self.assertFalse(firewall["cap_rank_split_or_selection_relaxation_allowed"])

    def test_success_freezes_one_exact_structural_cohort_only(self):
        cohort = self.request["future_cohort_freeze_contract"]
        self.assertEqual(cohort["selected_subjects"], 16)
        self.assertEqual(cohort["selected_run_bundles"], 96)
        self.assertEqual(cohort["fit_run_bundles"], 48)
        self.assertEqual(cohort["heldout_run_bundles"], 48)
        self.assertEqual(cohort["selected_core_members"], 384)
        self.assertEqual(cohort["payload_reservation_cap_bytes"], 8 * 1024**3)
        self.assertTrue(cohort["private_manifest_contains_source_exact_rows"])
        self.assertFalse(cohort["public_per_item_identity_allowed"])
        self.assertFalse(cohort["archive_member_or_payload_opened"])
        self.assertFalse(cohort["FW2_authorized_by_success"])
        self.assertTrue(cohort["FW2_preregistration_eligible_after_success"])
        self.assertFalse(cohort["CIL1_authorized_by_success"])

    def test_generated_stage_and_private_sequence_are_one_shot(self):
        generated = self.request["future_generated_qualification"]
        self.assertEqual(generated["required_paths"], 40)
        self.assertEqual(generated["required_VR25A_calls"], 40)
        self.assertGreaterEqual(generated["minimum_direct_refusals"], 90)
        self.assertFalse(generated["private_or_Git_ignored_path_operation"])
        self.assertEqual(generated["retained_generated_output_bytes"], 0)
        sequence = self.request["requested_future_sequence"]
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["VR25A_firewall_call_limit"], 1)
        self.assertEqual(sequence["private_cohort_manifest_write_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)
        self.assertEqual(sequence["resume_limit"], 0)

    def test_resources_are_bounded_and_payload_network_remain_zero(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["private_source_input_bytes"], 418_755)
        self.assertLessEqual(caps["combined_incremental_output_bytes"], 2 * 1024**2)
        self.assertLess(caps["peak_RSS_bytes_maximum_exclusive"], 257 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["signal_sample_bytes"], 0)
        self.assertEqual(caps["target_or_label_bytes"], 0)

    def test_decision_is_fresh_nonretroactive_and_staged(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(
            protocol["proof_closeout_commit_push_and_both_remote_jobs_green_required"]
        )
        self.assertTrue(protocol["request_must_be_identified_as_sole_active_Tier_C_packet"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_is_retroactive_authority"])
        self.assertTrue(
            protocol["decision_commit_push_and_both_remote_jobs_green_before_implementation"]
        )
        self.assertTrue(
            protocol["exact_future_implementation_and_closeout_green_before_private_open"]
        )
        self.assertFalse(protocol["packet_or_decision_alone_authorizes_private_open"])

    def test_request_verification_is_complete_without_execution(self):
        verification = self.request["request_verification"]
        self.assertEqual(verification["focused_request_tests_passed"], 14)
        self.assertEqual(verification["combined_VR25A_and_VR26P_tests_passed"], 45)
        self.assertEqual(verification["complete_dependency_light_tests_passed"], 4_987)
        self.assertEqual(verification["expected_skips"], 204)
        self.assertEqual(verification["test_delta"], 14)
        self.assertEqual(verification["new_failures"], 0)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["request_JSON_valid"])
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertFalse(verification["generated_qualification_or_private_operation_run"])

    def test_next_gate_keeps_every_private_and_scientific_action_closed(self):
        gate = self.request["next_gate"]
        self.assertTrue(gate["exact_request_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["proof_closeout_commit_push_and_both_jobs_green_required"])
        for key, value in gate.items():
            if key.endswith("allowed_now"):
                with self.subTest(key=key):
                    self.assertFalse(value)

    def test_public_packet_contains_no_selected_identity_or_scientific_upgrade(self):
        text = self.request_bytes.decode("utf-8")
        for forbidden in (
            '"selected_subject_ids"',
            '"member_name"',
            '"participant_id"',
            '"targets"',
            '"predictions"',
            '"probabilities"',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)
        claim = self.request["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        for key, value in claim.items():
            if key not in {"engineering_capability_requested", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("not retroactive Tier C", text)
        self.assertIn("would not authorize FW2", text)


if __name__ == "__main__":
    unittest.main()
