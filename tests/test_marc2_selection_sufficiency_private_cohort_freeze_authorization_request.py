import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_request.v0.json"
)
DOC = ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_AUTHORIZATION_PACKET.md"


class SelectionSufficiencyPrivateCohortFreezeRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(self.request["lane_id"], "MARC2-VR39P")
        self.assertEqual(
            self.request["status"],
            "all_false_Tier_C_request_local_remote_proof_pending",
        )
        self.assertEqual(
            self.request["proof_posture"],
            "request_only_no_private_real_or_scientific_operation_authorized",
        )

    def test_green_vr38a_closeout_is_bound(self):
        proof = self.request["green_predecessor_proof"]["VR38A_proof_closeout"]
        self.assertEqual(proof["commit"], "a599adf3e0320ad420e1c2f5647a0432e645c246")
        self.assertEqual(proof["CI_run_id"], 32_673_882_729)
        self.assertEqual(proof["base_python_job_id"], 97_278_761_357)
        self.assertEqual(proof["optional_neuro_job_id"], 97_278_761_303)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["qualification_repeated"])
        self.assertFalse(proof["private_operation_performed"])

    def test_fixed_artifacts_match_without_private_access(self):
        total = 0
        for row in self.request["fixed_committed_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            total += len(payload)
        summary = self.request["fixed_artifact_summary"]
        self.assertEqual(total, summary["bytes"])
        self.assertEqual(len(self.request["fixed_committed_artifacts"]), summary["count"])
        self.assertTrue(summary["all_paths_tracked_and_not_Git_ignored"])

    def test_request_artifacts_match(self):
        artifacts = self.request["request_artifacts"]
        for role in ("document", "test"):
            payload = (ROOT / artifacts[f"{role}_path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifacts[f"{role}_sha256"])

    def test_future_source_identity_is_copied_only(self):
        source = self.request["future_private_source"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["rows"], 1_227)
        self.assertTrue(source["identity_copied_from_committed_records_only"])
        self.assertFalse(source["path_checked_during_packet_preparation"])
        self.assertFalse(source["content_opened_during_packet_preparation"])
        self.assertEqual(source["bytes_read_during_packet_preparation"], 0)

    def test_requested_sequence_is_terminal_and_one_shot(self):
        sequence = self.request["requested_future_sequence"]
        self.assertTrue(sequence["stage_1_generated_mock_wrapper_after_decision_green"])
        self.assertTrue(sequence["stage_2_one_terminal_cohort_attempt_after_closeout_green"])
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["strict_JSON_parse_limit"], 1)
        self.assertEqual(sequence["VR38A_call_limit"], 1)
        self.assertEqual(sequence["private_cohort_manifest_write_limit"], 1)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)
        self.assertEqual(sequence["topology_successor_limit"], 0)

    def test_public_routes_collapse_success_and_every_failure(self):
        routes = self.request["future_route_contract"]
        self.assertEqual(routes["public_routes"], ["MARC2VR39P-R1", "MARC2VR39P-R2"])
        self.assertEqual(
            routes["VR38A_success_routes_collapsed_to"],
            {"MARC2VR38A-G1": "MARC2VR39P-R1", "MARC2VR38A-G2": "MARC2VR39P-R1"},
        )
        self.assertEqual(routes["every_failure_route"], "MARC2VR39P-R2")
        self.assertTrue(routes["R2_permanently_parks_Freewill_and_CIL1"])
        for key, value in routes["public_detail_permissions"].items():
            with self.subTest(key=key):
                self.assertFalse(value)

    def test_private_cohort_contract_is_variable_strict_and_target_free(self):
        cohort = self.request["future_private_cohort_contract"]
        self.assertEqual(cohort["minimum_selected_subjects"], 12)
        self.assertEqual(cohort["maximum_selected_subjects"], 19)
        self.assertEqual(cohort["fit_session"], "ses-01")
        self.assertEqual(cohort["heldout_session"], "ses-02")
        self.assertEqual(cohort["required_runs_per_session"], [1, 2, 3])
        self.assertEqual(cohort["selected_bundles_per_subject"], 6)
        self.assertEqual(cohort["selected_core_members_per_subject"], 24)
        self.assertTrue(cohort["maximal_contiguous_rank_prefix_required"])
        self.assertTrue(cohort["target_quality_and_outcome_free_required"])
        self.assertFalse(cohort["row_random_split_allowed"])
        self.assertFalse(cohort["generated_provenance_allowed_in_private_manifest"])

    def test_private_commitment_prevents_small_space_enumeration(self):
        commitment = self.request["future_private_commitment_contract"]
        self.assertEqual(commitment["private_nonce_bytes"], 32)
        self.assertTrue(commitment["nonce_generated_once_with_system_CSPRNG"])
        self.assertTrue(commitment["nonce_stored_only_in_private_manifest"])
        self.assertTrue(commitment["domain_separated_SHA256_required"])
        self.assertFalse(commitment["nonce_allowed_in_public_output"])
        self.assertFalse(commitment["unsalted_private_manifest_hash_allowed_in_public_output"])
        self.assertEqual(commitment["scheme"], "HMAC-SHA256-v0")
        self.assertTrue(commitment["constant_time_future_verification_required"])

    def test_compressed_and_uncompressed_storage_are_bounded(self):
        storage = self.request["future_storage_feasibility_contract"]
        self.assertEqual(storage["selected_compressed_payload_bytes_maximum"], 8 * 1024**3)
        self.assertEqual(storage["selected_uncompressed_payload_bytes_hard_maximum"], 10 * 1024**3)
        self.assertEqual(storage["derivative_reserve_bytes"], 1024**3)
        self.assertEqual(storage["temporary_overhead_reserve_bytes"], 256 * 1024**2)
        self.assertEqual(storage["peak_incremental_disk_bytes_maximum"], 10 * 1024**3)
        self.assertEqual(
            storage["selected_uncompressed_payload_bytes_maximum"]
            + storage["derivative_reserve_bytes"]
            + storage["temporary_overhead_reserve_bytes"],
            storage["peak_incremental_disk_bytes_maximum"],
        )
        self.assertTrue(storage["both_limits_must_pass_before_cohort_write"])
        self.assertFalse(storage["budget_increase_or_partial_cohort_allowed"])
        self.assertFalse(storage["exact_private_totals_allowed_in_public_output"])

    def test_generated_stage_arithmetic_is_exact_and_private_free(self):
        stage = self.request["future_generated_qualification"]
        self.assertEqual(stage["successful_cardinalities"], list(range(12, 20)))
        self.assertEqual(len(stage["cases"]), 21)
        self.assertEqual(stage["VR38A_success_routes_per_cardinality"], 2)
        self.assertEqual(stage["required_paths"], 168)
        self.assertEqual(stage["required_VR33A_calls"], 168)
        self.assertEqual(stage["required_readiness_provider_calls"], 504)
        self.assertEqual(stage["required_readiness_sleeper_calls"], 336)
        self.assertEqual(stage["required_VR38A_calls"], 84)
        self.assertEqual(stage["required_generated_cohort_writes"], 64)
        self.assertEqual(
            stage["required_route_counts"],
            {"MARC2VR39P-R1": 64, "MARC2VR39P-R2": 104},
        )
        self.assertGreaterEqual(stage["minimum_direct_refusals"], 200)
        self.assertEqual(stage["additional_nonpassing_readiness_patterns_directly_tested"], 6)
        self.assertTrue(stage["crash_injection_before_every_write_required"])
        self.assertTrue(stage["missing_completion_marker_always_parks"])
        self.assertEqual(stage["private_or_Git_ignored_path_operation_limit"], 0)
        self.assertEqual(stage["retained_generated_output_bytes"], 0)

    def test_output_protocol_consumes_before_readiness_and_completes_last(self):
        output = self.request["future_output_contract"]
        self.assertTrue(output["output_root_and_consumed_marker_before_readiness"])
        self.assertTrue(output["completion_marker_written_last"])
        self.assertFalse(output["overwrite_existing_output_allowed"])
        self.assertFalse(output["cleanup_or_partial_state_reuse_allowed"])
        self.assertTrue(output["no_follow_ancestor_directory_traversal_required"])
        self.assertTrue(output["lstat_open_fstat_inode_and_device_binding_required"])
        self.assertTrue(
            output["all_nonmarker_outputs_precomputed_and_cap_checked_before_first_write"]
        )
        self.assertEqual(
            output["public_allowlist_fields"],
            [
                "schema_name",
                "schema_version",
                "lane_id",
                "route",
                "status",
                "proof_anchors",
                "commitment_scheme",
                "cohort_commitment_sha256",
                "warnings",
                "unavailable_fields",
                "claim_boundary",
            ],
        )
        self.assertTrue(output["every_R2_public_report_byte_identical"])
        self.assertTrue(output["R1_noncommitment_fields_byte_identical"])

    def test_resource_caps_are_small_and_payload_free(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertLess(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2 + 1)
        self.assertEqual(caps["private_source_input_bytes"], 418_755)
        self.assertLessEqual(caps["combined_incremental_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["signal_sample_bytes"], 0)
        self.assertEqual(caps["target_or_label_bytes"], 0)

    def test_every_current_authority_and_operation_is_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )

    def test_decision_protocol_rejects_retroactive_authority(self):
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["proof_closeout_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
        self.assertFalse(protocol["current_or_earlier_continue_approve_or_lets_go_is_retroactive"])
        self.assertFalse(protocol["packet_or_decision_alone_authorizes_private_open"])

    def test_next_gate_and_claim_boundary_remain_closed(self):
        gate = self.request["next_gate"]
        self.assertFalse(gate["packet_identification_or_fresh_decision_allowed_now"])
        self.assertFalse(gate["generated_wrapper_implementation_allowed_now"])
        self.assertFalse(gate["private_structural_cohort_attempt_allowed_now"])
        self.assertFalse(gate["cohort_freeze_allowed_now"])
        self.assertFalse(gate["FW2_or_CIL1_allowed_now"])
        claims = self.request["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["real_or_private_data_accessed_by_request"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("not retroactive", text)


if __name__ == "__main__":
    unittest.main()
