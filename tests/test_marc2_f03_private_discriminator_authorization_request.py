import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_f03_private_discriminator_authorization_request.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_F03_PRIVATE_DISCRIMINATOR_AUTHORIZATION_PACKET.md"


class Marc2F03PrivateDiscriminatorAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_is_green_request_pending_proof_closeout_and_decision(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_f03_private_discriminator_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-VR11P")
        self.assertIn("all_false_Tier_C_request", self.request["status"])
        self.assertIn("remotely_green_pending_proof_closeout", self.request["status"])
        self.assertIn("no_private_real_or_scientific", self.request["proof_posture"])

    def test_green_VR10B_implementation_and_closeout_are_exact(self):
        proof = self.request["green_predecessor_proof"]
        implementation = proof["VR10B_implementation"]
        self.assertEqual(
            implementation["commit"],
            "61bb801689eb2885b1e96aa4b56c86658dc3b333",
        )
        self.assertEqual(implementation["CI_run_id"], 32_007_641_751)
        self.assertEqual(implementation["base_python_job_id"], 95_320_325_187)
        self.assertEqual(implementation["optional_neuro_job_id"], 95_320_325_136)
        self.assertTrue(implementation["both_required_jobs_green"])
        closeout = proof["VR10B_closeout"]
        self.assertEqual(
            closeout["commit"],
            "808e8ed300b9b9ea315ee3fa62231ae8d3f545d2",
        )
        self.assertEqual(closeout["CI_run_id"], 32_008_293_036)
        self.assertEqual(closeout["base_python_job_id"], 95_322_252_607)
        self.assertEqual(closeout["optional_neuro_job_id"], 95_322_252_650)
        self.assertTrue(closeout["both_required_jobs_green"])

    def test_remote_green_request_proof_is_exact_and_scope_unchanged(self):
        proof = self.request["remote_green_request_proof"]
        self.assertEqual(
            proof["request_commit"],
            "6e72c8f797201359777454a750b1dea9704665c0",
        )
        self.assertEqual(proof["CI_run_id"], 32_009_557_248)
        self.assertEqual(proof["base_python_job_id"], 95_326_004_060)
        self.assertEqual(proof["optional_neuro_job_id"], 95_326_004_145)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["request_document_bytes_at_request_commit"], 9_454)
        self.assertEqual(
            proof["request_document_sha256_at_request_commit"],
            "346820e35bf4bb7b4cf7372a3f857e3ff1c636f4c30a09a8622284d12dfcc70b",
        )
        self.assertEqual(proof["request_registry_bytes_at_request_commit"], 19_456)
        self.assertEqual(
            proof["request_registry_sha256_at_request_commit"],
            "c1a201472ab81f73e22b5fc5d3eedaadf62a49dc1791001d9c17e7374296b3bb",
        )
        self.assertEqual(proof["request_test_bytes_at_request_commit"], 10_944)
        self.assertEqual(
            proof["request_test_sha256_at_request_commit"],
            "7fd927afb920b725cc5a0df73e861d883ee6ca7792561af13429b3b29eb85499",
        )
        self.assertFalse(proof["scope_changed_by_proof_record"])
        self.assertEqual(proof["private_real_or_scientific_operation_sum"], 0)
        self.assertTrue(
            proof[
                "proof_closeout_remote_green_required_before_packet_identification"
            ]
        )
        self.assertFalse(
            self.request["next_gate"][
                "exact_request_commit_push_and_both_jobs_green_required"
            ]
        )

    def test_all_fixed_artifacts_are_current_tracked_and_private_free(self):
        artifacts = self.request["fixed_committed_artifacts"]
        self.assertEqual(len(artifacts), 16)
        self.assertEqual(sum(row["bytes"] for row in artifacts), 295_028)
        seen = set()
        for row in artifacts:
            with self.subTest(path=row["path"]):
                self.assertNotIn(row["path"], seen)
                seen.add(row["path"])
                self.assertNotIn(".codex_work", row["path"])
                path = ROOT / row["path"]
                payload = path.read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        self.assertEqual(
            self.request["fixed_artifact_summary"],
            {
                "count": 16,
                "bytes": 295_028,
                "all_paths_tracked_and_not_Git_ignored": True,
            },
        )

    def test_request_document_and_test_are_hash_bound(self):
        for row in self.request["request_artifacts"].values():
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_requested_sequence_keeps_both_green_barriers(self):
        sequence = self.request["requested_future_sequence"]
        self.assertTrue(
            sequence["stage_1_generated_mock_wrapper_after_separate_decision_green"]
        )
        self.assertTrue(
            sequence[
                "stage_2_one_private_structural_discriminator_after_implementation_green"
            ]
        )
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["strict_JSON_parse_limit"], 1)
        self.assertEqual(sequence["VR6_adapter_call_limit"], 1)
        self.assertEqual(sequence["VR10B_discriminator_call_limit"], 1)
        self.assertEqual(sequence["private_row_or_manifest_write_limit"], 0)
        self.assertEqual(sequence["retry_limit"], 0)
        self.assertEqual(sequence["rerun_limit"], 0)
        self.assertEqual(sequence["resume_limit"], 0)

    def test_private_source_is_bound_but_completely_untouched(self):
        source = self.request["private_source_identity"]
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(
            source["sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertEqual(source["rows"], 1_227)
        self.assertEqual(source["regular_files"], 1_025)
        self.assertEqual(source["directories"], 202)
        self.assertEqual(source["source_bundles"], 238)
        self.assertEqual(source["eligible_bundles"], 195)
        self.assertEqual(source["valid_ineligible_bundles"], 43)
        self.assertEqual(source["current_path_checks"], 0)
        self.assertEqual(source["current_content_opens"], 0)
        self.assertEqual(source["current_bytes_read"], 0)

    def test_new_paths_are_fixed_and_every_consumed_VR9P_surface_is_forbidden(self):
        paths = self.request["future_fixed_paths"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr11p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_f03_private_discriminator/v0",
        )
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertTrue(paths["new_output_root_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertIn(
            ".codex_work/marc2_machine_readiness/vr9p/readiness.v0.json",
            paths["named_consumed_paths"],
        )
        self.assertIn(
            ".codex_work/marc2_two_layer_private_diagnostic/v0",
            paths["named_consumed_paths"],
        )

    def test_route_contract_accepts_only_five_coarse_private_routes(self):
        route = self.request["future_private_discriminator_contract"]
        self.assertEqual(route["expected_outer_VR6_route"], "MARC2VR6-F02")
        self.assertEqual(route["expected_nested_VR2_route"], "MARC2VR2-F03")
        self.assertEqual(
            route["VR10B_to_private_route_map"],
            {
                "MARC2VR10B-R1": "MARC2VR11P-R1",
                "MARC2VR10B-R2": "MARC2VR11P-R2",
                "MARC2VR10B-R3": "MARC2VR11P-R3",
                "MARC2VR10B-R4": "MARC2VR11P-R4",
                "MARC2VR10B-R5": "MARC2VR11P-R5",
            },
        )
        self.assertFalse(route["VR10B_G1_allowed_as_private_result"])
        self.assertFalse(route["missing_unknown_or_other_route_allowed"])
        self.assertFalse(route["reason_predicate_or_failed_value_retained"])
        self.assertFalse(route["in_memory_candidate_or_selection_retained"])
        self.assertFalse(route["F03_rule_relaxation_allowed"])

    def test_generated_qualification_is_strict_bounded_and_private_free(self):
        qualification = self.request["future_generated_qualification"]
        self.assertTrue(qualification["generated_only"])
        self.assertEqual(qualification["generated_cases"], 6)
        self.assertEqual(qualification["source_orders"], 2)
        self.assertEqual(qualification["exact_replays"], 2)
        self.assertEqual(qualification["required_paths"], 24)
        self.assertEqual(qualification["required_VR6_calls"], 24)
        self.assertEqual(qualification["required_VR10B_calls"], 24)
        self.assertGreaterEqual(qualification["minimum_direct_refusals"], 70)
        self.assertGreaterEqual(len(qualification["required_refusal_families"]), 12)
        self.assertFalse(qualification["private_or_Git_ignored_path_operation"])
        self.assertEqual(qualification["retained_generated_output_bytes"], 0)

    def test_resources_are_one_thread_small_and_zero_payload(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["generated_qualification_runtime_seconds"], 45)
        self.assertEqual(caps["future_private_command_runtime_seconds"], 650)
        self.assertEqual(caps["peak_RSS_bytes_maximum_exclusive"], 256 * 1024**2)
        self.assertEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)
        self.assertEqual(caps["private_source_input_bytes"], 418_755)
        self.assertEqual(caps["combined_incremental_output_bytes"], 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_member_or_payload_bytes"], 0)
        self.assertEqual(caps["signal_sample_bytes"], 0)
        self.assertEqual(caps["target_or_label_bytes"], 0)

    def test_every_current_authority_is_false_and_counter_zero(self):
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
        protocol = self.request["decision_protocol"]
        self.assertTrue(
            protocol["request_commit_push_and_both_remote_jobs_green_required"]
        )
        self.assertTrue(
            protocol["fresh_unambiguous_packet_bound_maintainer_message_required"]
        )
        self.assertFalse(protocol["current_or_earlier_continue_is_retroactive_authority"])
        self.assertFalse(protocol["packet_or_decision_alone_authorizes_private_open"])

    def test_failure_semantics_and_claim_ceiling_are_explicit(self):
        meaning = self.request["success_and_failure_meaning"]
        self.assertFalse(meaning["scientific_value"])
        self.assertFalse(meaning["MARC2_FW2_eligibility_after_diagnostic"])
        self.assertFalse(meaning["MARC2_CIL1_eligibility_after_diagnostic"])
        claim = self.request["claim_boundary"]
        self.assertIn("target-free structural open", claim["engineering_capability_requested"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability requested", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("not retroactive", document)
        self.assertIn("FW2", document)
        self.assertIn("CIL1 remain ineligible", document)


if __name__ == "__main__":
    unittest.main()
