import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_dynamic_private_selection_recovery_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT / "docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_AUTHORIZATION_PACKET.md"
)


class Marc2DynamicPrivateSelectionRecoveryAuthorizationRequestTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_request_identity_and_current_authority_are_exactly_false(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_dynamic_private_selection_recovery_authorization_request",
        )
        self.assertEqual(self.request["lane_id"], "MARC2-VR7P")
        self.assertTrue(
            all(
                value is False
                for value in self.request["requested_authorization_flags"].values()
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_access_counters"].values())
        )

    def test_every_fixed_artifact_is_committed_and_hash_bound(self):
        rows = self.request["fixed_committed_artifacts"]
        self.assertEqual(len(rows), 9)
        self.assertEqual(len({row["role"] for row in rows}), len(rows))
        for row in rows:
            with self.subTest(role=row["role"]):
                self.assertNotIn(".codex_work", row["path"])
                path = ROOT / row["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"]
                )

    def test_green_VR6_proof_is_exact(self):
        proof = self.request["green_predecessor_proof"]
        self.assertEqual(
            proof["VR6_implementation"]["commit"],
            "482dad55e91e2abf48b6a59a417ebca191c0cd68",
        )
        self.assertEqual(proof["VR6_implementation"]["CI_run_id"], 31975600088)
        self.assertEqual(
            proof["VR6_closeout"]["commit"],
            "5b4dde3f56e8049f24a2df4cf4c3538bd5d71683",
        )
        self.assertEqual(proof["VR6_closeout"]["CI_run_id"], 31975867040)
        self.assertTrue(
            all(record["both_required_jobs_green"] for record in proof.values())
        )

    def test_new_paths_are_fixed_and_consumed_paths_are_forbidden(self):
        paths = self.request["future_fixed_paths"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr7p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_dynamic_private_selection_recovery/v0",
        )
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertTrue(paths["new_output_root_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertGreaterEqual(len(paths["named_consumed_paths"]), 5)

    def test_readiness_precedes_every_private_operation(self):
        readiness = self.request["fresh_machine_readiness_contract"]
        self.assertEqual(readiness["consecutive_passing_samples"], 3)
        self.assertEqual(readiness["maximum_wait_seconds"], 600)
        self.assertTrue(
            readiness["bind_future_exact_executor_implementation_commit_from_proof_record"]
        )
        self.assertFalse(readiness["ambient_HEAD_binding_allowed"])
        self.assertFalse(readiness["output_or_private_path_operation_before_ready"])
        self.assertFalse(
            readiness["existing_VR4_certificate_read_stat_unlink_or_reuse_allowed"]
        )

    def test_source_identity_is_bound_but_current_reads_are_zero(self):
        source = self.request["private_source_identity"]
        self.assertEqual(source["bytes"], 418755)
        self.assertEqual(source["rows"], 1227)
        self.assertEqual(source["source_bundles"], 238)
        self.assertEqual(source["eligible_bundles"], 195)
        self.assertEqual(source["valid_ineligible_bundles"], 43)
        self.assertEqual(source["current_path_checks"], 0)
        self.assertEqual(source["current_content_opens"], 0)
        self.assertEqual(source["current_bytes_read"], 0)

    def test_dynamic_outcomes_replace_generated_expected_values(self):
        policy = self.request["dynamic_selection_invariants"]
        self.assertEqual(policy["minimum_selected_subjects"], 12)
        self.assertEqual(policy["maximum_selected_subjects"], 19)
        self.assertTrue(policy["selected_subjects_is_measured_output"])
        self.assertTrue(policy["selected_reservation_bytes_is_measured_output"])
        self.assertTrue(policy["selection_identity_sha256_is_measured_output"])
        self.assertFalse(policy["generated_expected_subject_count_allowed"])
        self.assertFalse(policy["generated_expected_reservation_bytes_allowed"])
        self.assertFalse(policy["generated_expected_selection_hash_allowed"])
        self.assertEqual(policy["run_bundles_per_subject"], 6)
        self.assertEqual(policy["core_members_per_subject"], 24)

    def test_marker_one_open_and_no_rerun_are_exact(self):
        sequence = self.request["requested_sequence"]
        output = self.request["future_output_contract"]
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["strict_JSON_parse_limit"], 1)
        self.assertEqual(sequence["VR6_adapter_call_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)
        self.assertTrue(output["marker_immediately_before_private_content_open"])
        self.assertFalse(output["aggregate_subject_or_participant_ID_allowed"])
        self.assertFalse(
            output["aggregate_upstream_reason_predicate_or_private_value_allowed"]
        )

    def test_generated_stage_and_resources_are_bounded(self):
        generated = self.request["future_generated_qualification"]
        self.assertEqual(generated["profile_subject_counts"], [12, 14, 16, 18, 19])
        self.assertEqual(generated["minimum_success_paths"], 10)
        self.assertGreaterEqual(generated["minimum_direct_mutations"], 72)
        self.assertFalse(generated["real_certificate_source_or_output_path_operation"])
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["private_source_input_bytes"], 418755)
        self.assertEqual(caps["combined_output_bytes"], 4 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)

    def test_fresh_decision_and_green_implementation_are_required(self):
        verification = self.request["local_verification"]
        self.assertEqual(verification["focused_tests"], 11)
        self.assertEqual(verification["focused_hash_binding_subtests"], 9)
        self.assertEqual(verification["complete_suite_primary_passes"], 3905)
        self.assertEqual(verification["complete_suite_skips"], 35)
        self.assertEqual(verification["new_failures_vs_pre_change_baseline"], 0)
        self.assertTrue(verification["remote_CI_pending"])
        self.assertTrue(all(self.request["decision_requirements"].values()))
        gate = self.request["next_gate"]
        self.assertEqual(gate["current_authority"], "none_request_only")
        self.assertFalse(gate["generated_wrapper_implementation_authorized"])
        self.assertFalse(gate["private_structural_pass_authorized"])
        self.assertFalse(gate["FW2_preregistration_eligible"])
        self.assertFalse(gate["FW2_or_CIL1_execution_eligible"])

    def test_packet_disclaims_science_and_retroactive_authority(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("All authorization fields false", text)
        self.assertIn("current and earlier `continue` messages are not retroactive", text)
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
