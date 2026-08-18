import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "registries/marc2_p15_private_confirmation_authorization_request.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_P15_PRIVATE_CONFIRMATION_AUTHORIZATION_PACKET.md"


class Marc2P15PrivateConfirmationAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request_bytes = REQUEST_PATH.read_bytes()
        cls.request = json.loads(cls.request_bytes)

    def test_identity_is_all_false_remotely_green_request(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_p15_private_confirmation_authorization_request",
        )
        self.assertEqual(self.request["lane_id"], "MARC2-VR12P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_remotely_green_proof_closeout_pending",
        )
        proof = self.request["remote_green_request_proof"]
        self.assertEqual(
            proof["request_commit"],
            "816589473eafabdebe66be2b4e921b005f04a959",
        )
        self.assertEqual(proof["CI_run_id"], 32_171_993_061)
        self.assertEqual(proof["base_python_job_id"], 95_825_074_164)
        self.assertEqual(proof["optional_neuro_job_id"], 95_825_073_430)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_by_proof_record"])
        self.assertEqual(proof["private_real_or_scientific_operation_sum"], 0)

    def test_remote_green_request_snapshot_is_immutable(self):
        proof = self.request["remote_green_request_proof"]
        for binding in proof["request_artifacts_at_commit"]:
            payload = subprocess.run(
                [
                    "git",
                    "show",
                    f"{proof['request_commit']}:{binding['path']}",
                ],
                cwd=ROOT,
                capture_output=True,
                check=True,
            ).stdout
            with self.subTest(role=binding["role"]):
                self.assertEqual(len(payload), binding["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])

    def test_all_current_authority_and_operations_are_false_or_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )

    def test_green_predecessor_order_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["VR12A_registration"]["commit"],
            "5107eb3d714f7713a216b9ad4e21c06300cd8c21",
        )
        self.assertEqual(
            proof["VR12A_implementation"]["commit"],
            "873484aaf270bc5b1499e4b0449c9e8ef138c623",
        )
        closeout = proof["VR12A_proof_closeout"]
        self.assertEqual(closeout["commit"], "8f2ad163f3beacaf3cbcc0287fe305575a34b6cc")
        self.assertEqual(closeout["CI_run_id"], 32_170_855_368)
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
        self.assertEqual(len(roles), summary["count"])
        self.assertEqual(total, summary["bytes"])
        self.assertEqual((len(roles), total), (14, 206_793))

    def test_source_identity_is_bound_but_currently_untouched(self):
        source = self.request["private_source_identity"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["source_bundles"], 238)
        self.assertEqual(source["eligible_bundles"], 195)
        self.assertEqual(source["valid_ineligible_bundles"], 43)
        self.assertEqual(source["current_path_checks"], 0)
        self.assertEqual(source["current_content_opens"], 0)
        self.assertEqual(source["current_bytes_read"], 0)
        self.assertEqual(source["future_content_open_limit"], 1)

    def test_future_paths_are_new_fixed_and_distinct_from_consumed_paths(self):
        paths = self.request["future_fixed_paths"]
        self.assertIn("vr12p", paths["fresh_readiness_certificate"])
        self.assertIn("p15_private_confirmation", paths["new_output_root"])
        self.assertNotIn(paths["new_output_root"], paths["named_consumed_paths"])
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertTrue(paths["new_output_root_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertFalse(paths["source_or_output_substitution_allowed"])

    def test_future_adapter_is_exact_and_does_not_relax_p15_neighbors(self):
        adapter = self.request["future_adapter_contract"]
        self.assertEqual(
            adapter["exact_function"],
            "neurodecodekit.datasets.marc2_p15_run_index_repair.adapt_repaired_source",
        )
        self.assertEqual(adapter["exact_real_calls"], 1)
        self.assertEqual(adapter["accepted_run_digit_widths"], [1, 2])
        self.assertTrue(adapter["source_exact_selected_names_required"])
        self.assertTrue(adapter["source_exact_reservation_required"])
        self.assertFalse(adapter["subject_session_task_suffix_or_path_broadening_allowed"])
        self.assertFalse(adapter["cap_rank_split_or_companion_relaxation_allowed"])

    def test_success_freezes_only_a_bounded_structural_cohort(self):
        cohort = self.request["future_cohort_freeze_contract"]
        self.assertEqual((cohort["minimum_subjects"], cohort["maximum_subjects"]), (12, 19))
        self.assertEqual(
            (
                cohort["minimum_selected_run_bundles"],
                cohort["maximum_selected_run_bundles"],
            ),
            (72, 114),
        )
        self.assertEqual(
            (
                cohort["minimum_selected_core_members"],
                cohort["maximum_selected_core_members"],
            ),
            (288, 456),
        )
        self.assertEqual(cohort["payload_reservation_cap_bytes"], 8 * 1024**3)
        self.assertFalse(cohort["archive_member_or_payload_opened"])
        self.assertFalse(cohort["FW2_authorized_by_R1"])
        self.assertTrue(cohort["FW2_preregistration_eligible_after_R1"])
        self.assertFalse(cohort["CIL1_authorized_by_R1"])

    def test_generated_stage_and_private_sequence_are_one_shot(self):
        generated = self.request["future_generated_qualification"]
        self.assertEqual(generated["required_success_paths"], 12)
        self.assertEqual(generated["required_VR12A_calls"], 12)
        self.assertGreaterEqual(generated["minimum_direct_refusals"], 50)
        self.assertFalse(generated["private_or_Git_ignored_path_operation"])
        self.assertEqual(generated["retained_generated_output_bytes"], 0)
        sequence = self.request["requested_future_sequence"]
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["VR12A_adapter_call_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)

    def test_resources_are_small_and_payload_network_remain_zero(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["private_source_input_bytes"], 418_755)
        self.assertLessEqual(caps["combined_incremental_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["signal_sample_bytes"], 0)
        self.assertEqual(caps["target_or_label_bytes"], 0)

    def test_decision_is_fresh_nonretroactive_and_staged(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["proof_closeout_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_is_retroactive_authority"])
        self.assertTrue(
            protocol["decision_commit_push_and_both_remote_jobs_green_before_implementation"]
        )
        self.assertTrue(
            protocol["exact_future_implementation_and_closeout_green_before_private_open"]
        )
        self.assertFalse(protocol["packet_or_decision_alone_authorizes_private_open"])
        self.assertFalse(
            self.request["next_gate"]["exact_request_commit_push_and_both_jobs_green_required"]
        )
        self.assertTrue(
            self.request["next_gate"]["proof_closeout_commit_push_and_both_jobs_green_required"]
        )

    def test_public_packet_contains_no_selected_identity_or_scientific_upgrade(self):
        text = self.request_bytes.decode("utf-8")
        for forbidden in (
            '"selected_subject_ids"',
            '"member_name"',
            '"participant_id"',
            '"target"',
            '"targets"',
            '"prediction"',
            '"predictions"',
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)
        self.assertFalse(self.request["next_gate"]["private_structural_confirmation_allowed_now"])
        self.assertFalse(
            self.request["next_gate"][
                "archive_payload_neural_target_model_prediction_or_score_allowed_now"
            ]
        )

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("retroactive Tier C authority", text)
        self.assertIn("not authorize FW2", text)


if __name__ == "__main__":
    unittest.main()
