import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/marc2_two_layer_private_diagnostic_authorization_request.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_AUTHORIZATION_PACKET.md"


class Marc2TwoLayerPrivateDiagnosticAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_is_all_false_request_pending_fresh_decision(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_two_layer_private_diagnostic_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-VR9P")
        self.assertIn("all_false_Tier_C_request", self.request["status"])
        self.assertIn("no_private_real_or_scientific", self.request["proof_posture"])

    def test_green_VR8B_implementation_and_closeout_are_exact(self):
        proof = self.request["green_predecessor_proof"]
        implementation = proof["VR8B_implementation"]
        self.assertEqual(
            implementation["commit"],
            "d7ce48baca29547ff2385ffe53d247563139439f",
        )
        self.assertEqual(implementation["CI_run_id"], 31_989_817_593)
        self.assertEqual(implementation["base_python_job_id"], 95_271_230_358)
        self.assertEqual(implementation["optional_neuro_job_id"], 95_271_230_485)
        self.assertTrue(implementation["both_required_jobs_green"])
        closeout = proof["VR8B_closeout"]
        self.assertEqual(
            closeout["commit"],
            "1d2ac3a3fb15ebdc01d8aaa23ae8dc74372b85b8",
        )
        self.assertEqual(closeout["CI_run_id"], 31_990_197_181)
        self.assertEqual(closeout["base_python_job_id"], 95_272_233_005)
        self.assertEqual(closeout["optional_neuro_job_id"], 95_272_232_926)
        self.assertTrue(closeout["both_required_jobs_green"])

    def test_all_fixed_artifacts_are_current_and_tracked(self):
        artifacts = self.request["fixed_committed_artifacts"]
        self.assertEqual(len(artifacts), 17)
        self.assertEqual(sum(row["bytes"] for row in artifacts), 328_581)
        seen = set()
        for row in artifacts:
            with self.subTest(path=row["path"]):
                self.assertNotIn(row["path"], seen)
                seen.add(row["path"])
                self.assertNotIn(".codex_work", row["path"])
                path = ROOT / row["path"]
                self.assertTrue(path.is_file())
                payload = path.read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        self.assertEqual(
            self.request["fixed_artifact_summary"],
            {
                "count": 17,
                "bytes": 328_581,
                "all_paths_tracked_and_not_Git_ignored": True,
            },
        )

    def test_request_artifacts_are_hash_bound(self):
        for row in self.request["request_artifacts"].values():
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_requested_sequence_keeps_both_green_barriers(self):
        sequence = self.request["requested_future_sequence"]
        self.assertTrue(sequence["stage_1_generated_mock_wrapper_after_separate_decision_green"])
        self.assertTrue(sequence["stage_2_one_private_structural_diagnostic_after_exact_implementation_green"])
        self.assertEqual(sequence["private_content_open_limit"], 1)
        self.assertEqual(sequence["strict_JSON_parse_limit"], 1)
        self.assertEqual(sequence["VR6_adapter_call_limit"], 1)
        self.assertEqual(sequence["VR2_validation_call_limit"], 1)
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

    def test_new_paths_are_fixed_and_consumed_paths_are_forbidden(self):
        paths = self.request["future_fixed_paths"]
        self.assertEqual(
            paths["fresh_readiness_certificate"],
            ".codex_work/marc2_machine_readiness/vr9p/readiness.v0.json",
        )
        self.assertEqual(
            paths["new_output_root"],
            ".codex_work/marc2_two_layer_private_diagnostic/v0",
        )
        self.assertTrue(paths["fresh_readiness_parent_must_be_absent"])
        self.assertTrue(paths["new_output_root_must_be_absent"])
        self.assertFalse(paths["operation_on_named_consumed_path_allowed"])
        self.assertNotIn(
            paths["new_output_root"],
            paths["named_consumed_paths"],
        )
        self.assertIn(
            ".codex_work/marc2_dynamic_private_selection_recovery/v0",
            paths["named_consumed_paths"],
        )

    def test_route_contract_accepts_only_nested_F03_or_F04(self):
        route = self.request["future_two_layer_diagnostic_contract"]
        self.assertEqual(route["expected_outer_VR6_route"], "MARC2VR6-F02")
        self.assertEqual(
            route["allowed_nested_VR2_routes"],
            ["MARC2VR2-F03", "MARC2VR2-F04"],
        )
        self.assertFalse(route["VR2_F02_envelope_route_allowed"])
        self.assertFalse(route["VR6_success_or_cohort_acceptance_allowed"])
        self.assertFalse(route["missing_unknown_or_other_nested_route_allowed"])
        self.assertFalse(route["reason_exception_text_predicate_or_failed_value_retained"])
        self.assertFalse(route["in_memory_candidate_or_selection_retained"])
        self.assertFalse(route["F03_or_F04_rule_relaxation_allowed"])
        fields = set(route["aggregate_result_fields"])
        forbidden = {
            "reason",
            "path",
            "rows",
            "participant_id",
            "selection",
            "private_hash",
        }
        self.assertTrue(fields.isdisjoint(forbidden))

    def test_generated_qualification_is_strict_bounded_and_private_free(self):
        qualification = self.request["future_generated_qualification"]
        self.assertTrue(qualification["generated_only"])
        self.assertEqual(qualification["cases"], ["F03", "F04"])
        self.assertEqual(
            qualification["central_directory_orders"],
            ["canonical", "reversed"],
        )
        self.assertEqual(qualification["exact_replays"], 2)
        self.assertGreaterEqual(qualification["minimum_direct_refusal_mutations"], 64)
        self.assertGreaterEqual(len(qualification["required_refusal_families"]), 12)
        self.assertFalse(
            qualification[
                "generic_path_URL_output_threshold_retry_resume_fallback_or_substitution_argument"
            ]
        )
        self.assertFalse(qualification["private_or_Git_ignored_path_operation"])
        self.assertEqual(qualification["retained_generated_output_bytes"], 0)

    def test_resources_are_one_thread_small_and_zero_payload(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(caps["generated_qualification_runtime_seconds"], 30)
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
            all(value is False for value in self.request["current_authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["current_operation_counters"].values())
        )
        protocol = self.request["decision_protocol"]
        self.assertTrue(protocol["request_commit_push_and_both_remote_jobs_green_required"])
        self.assertTrue(protocol["fresh_unambiguous_packet_bound_maintainer_message_required"])
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
        self.assertIn("FW2 and CIL1 remain ineligible", document)


if __name__ == "__main__":
    unittest.main()
