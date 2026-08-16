import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc2_live_adapter_recovery_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveAdapterRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_lane_and_all_false_status_are_exact(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_live_adapter_recovery_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-LA2")
        self.assertEqual(
            self.request["request_id"],
            "MARC-2-LA2-live-adapter-recovery-authorization-request-v0",
        )
        self.assertEqual(self.request["status"], "all_false_request_not_authorized")
        self.assertFalse(self.request["authorized"])

    def test_all_artifact_bindings_are_current(self):
        for binding in self.request["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_green_live_adapter_and_closeout_proofs_are_exact(self):
        proof = self.request["green_live_schema_adapter_proof"]
        self.assertEqual(
            proof["implementation_commit"],
            "3e3f8b86cfb8ac6f23730fb2fcc9fc5da549aac7",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 31_935_754_822)
        self.assertEqual(proof["implementation_base_job_id"], 95_137_289_730)
        self.assertEqual(proof["implementation_optional_job_id"], 95_137_289_704)
        self.assertEqual(
            proof["closeout_commit"],
            "52eabc63751aa692536cec5fe602fe05aa879eae",
        )
        self.assertEqual(proof["closeout_CI_run_id"], 31_936_399_968)
        self.assertEqual(proof["closeout_base_job_id"], 95_138_912_293)
        self.assertEqual(proof["closeout_optional_job_id"], 95_138_912_287)
        self.assertTrue(proof["both_required_closeout_jobs_green"])

    def test_consumed_lanes_cannot_be_reused(self):
        boundary = self.request["consumed_and_generated_boundaries"]
        self.assertTrue(boundary["MARC2_FW1C_consumed"])
        self.assertEqual(boundary["MARC2_FW1C_route"], "MARC2FWC-F02")
        self.assertFalse(boundary["MARC2_FW1C_retry_repair_or_reuse"])
        self.assertTrue(boundary["MARC2_LA1_generated_only"])
        self.assertEqual(boundary["MARC2_LA1_private_execution_limit"], 0)
        self.assertFalse(boundary["MARC2_FW2_eligible"])

    def test_future_sequence_has_decision_implementation_and_private_gates(self):
        stages = self.request["proposed_sequence"]
        self.assertEqual([stage["ordinal"] for stage in stages], [1, 2])
        self.assertEqual(stages[0]["stage_id"], "MARC2-LA2-executor")
        self.assertEqual(stages[1]["stage_id"], "MARC2-LA2-private-selection")
        self.assertTrue(stages[0]["green_decision_required_first"])
        self.assertTrue(stages[1]["green_executor_required_first"])
        self.assertFalse(stages[0]["currently_authorized"])
        self.assertFalse(stages[1]["currently_authorized"])

    def test_proof_certificate_and_native_registry_are_distinct(self):
        proof = self.request["future_proof_certificate"]
        self.assertEqual(proof["certificate_schema_lane"], "MARC2-FW1B")
        self.assertEqual(proof["native_executor_registry_lane"], "MARC2-LA2")
        self.assertEqual(
            proof["shared_validator_symbol"],
            "validate_implementation_record",
        )
        self.assertTrue(proof["certificate_binds_executor_module_and_registry"])
        self.assertTrue(proof["expected_and_observed_proofs_bind_executor_HEAD"])
        self.assertFalse(proof["older_HEAD_substitution_allowed"])
        self.assertFalse(proof["certificate_self_hash_allowed"])

    def test_future_executor_is_additive_and_uses_exact_public_functions(self):
        surface = self.request["future_executor_surface"]
        self.assertEqual(
            surface["module"],
            "neurodecodekit.datasets.marc2_live_schema_adapter_recovery",
        )
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(
            surface["live_adapter_symbol"],
            "adapt_live_shaped_source",
        )
        self.assertEqual(surface["selector_symbol"], "select_generated_prefix")
        self.assertFalse(surface["consumed_executor_import_call_or_edit_allowed"])
        self.assertFalse(surface["generic_source_or_output_override_available"])

    def test_private_source_identity_is_exact_and_closed_now(self):
        source = self.request["private_source"]
        self.assertEqual(
            source["path"],
            ".codex_work/marc1_central_directory/live_audit_v0/"
            "member_inventory.private.v0.json",
        )
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(
            source["sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertEqual(source["entries"], 1_227)
        self.assertEqual(source["regular_entries"], 1_025)
        self.assertEqual(source["directory_entries"], 202)
        self.assertFalse(source["path_stat_resolve_open_hash_or_parse_authorized_now"])

    def test_path_protocol_is_one_open_no_follow_and_no_siblings(self):
        protocol = self.request["future_path_protocol"]
        self.assertFalse(protocol["resolve_glob_listdir_or_sibling_access_allowed"])
        self.assertTrue(protocol["no_follow_component_and_final_checks_required"])
        self.assertTrue(protocol["O_NOFOLLOW_required"])
        self.assertEqual(protocol["content_opens"], 1)
        self.assertEqual(protocol["sequential_reads"], 1)
        self.assertEqual(protocol["SHA256_passes"], 1)
        self.assertEqual(protocol["strict_JSON_parses"], 1)
        self.assertFalse(protocol["second_open_retry_rerun_or_resume_allowed"])

    def test_output_root_is_new_bounded_and_untouched(self):
        output = self.request["future_output_contract"]
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_freewill_prefix/live_alias_recovery_v2",
        )
        self.assertNotIn(output["root"], output["forbidden_consumed_roots"])
        self.assertTrue(output["root_must_be_absent_and_non_symlink_at_execution"])
        self.assertFalse(output["root_stat_create_or_reserve_authorized_now"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertTrue(output["consumed_marker_written_before_private_content_open"])
        self.assertFalse(output["overwrite_allowed"])

    def test_frozen_processing_calls_adapter_and_selector_once(self):
        processing = self.request["frozen_processing"]
        self.assertEqual(processing["live_adapter_calls"], 1)
        self.assertEqual(processing["selector_calls"], 1)
        self.assertTrue(processing["source_object_must_remain_unchanged"])
        self.assertTrue(processing["mutable_alias_forbidden"])
        self.assertEqual(
            processing["only_transport_key_mapping"],
            {"source": "directory", "selector": "central_directory"},
        )
        self.assertTrue(processing["transport_values_and_digests_preserved"])

    def test_selector_rule_is_target_free_and_storage_bounded(self):
        rule = self.request["frozen_selection_rule"]
        self.assertEqual(rule["public_eligible_subjects"], 19)
        self.assertEqual(rule["minimum_subjects"], 12)
        self.assertEqual(rule["maximum_subjects"], 19)
        self.assertEqual(rule["fit_session"], "ses-01")
        self.assertEqual(rule["heldout_session"], "ses-02")
        self.assertEqual(rule["run_bundles_per_subject"], 6)
        self.assertEqual(rule["members_per_subject"], 24)
        self.assertEqual(rule["reservation_cap_bytes"], 8 * 1024**3)
        self.assertTrue(rule["maximal_contiguous_prefix_required"])
        self.assertFalse(rule["real_selection_identity_assumed_from_generated"])
        self.assertFalse(rule["target_label_event_quality_signal_or_outcome_input_allowed"])

    def test_generated_qualification_is_bounded_and_private_free(self):
        qualification = self.request["future_generated_qualification"]
        self.assertEqual(qualification["proof_certificate_mutations"], 32)
        self.assertEqual(qualification["wrapper_mutations"], 24)
        self.assertEqual(qualification["total_direct_mutations"], 56)
        self.assertTrue(qualification["inherited_LA1_tests_run_in_complete_suite"])
        self.assertEqual(qualification["private_source_operations"], 0)
        self.assertEqual(qualification["network_operations"], 0)

    def test_router_consumes_and_stops_before_payload(self):
        router = self.request["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC2LAR-R1")
        self.assertTrue(router["every_route_consumes_invocation"])
        self.assertFalse(router["success_authorizes_archive_member_or_payload"])
        self.assertFalse(router["success_authorizes_MARC2_FW2"])
        self.assertFalse(router["success_is_scientific_result"])

    def test_resource_caps_are_small_and_payload_is_zero(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds_per_stage"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["private_input_opens"], 1)
        self.assertEqual(caps["private_input_bytes"], 418_755)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_local_header_or_member_bytes"], 0)
        self.assertEqual(caps["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(caps["incremental_disk_bytes"], 4 * 1024**2)
        self.assertEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)

    def test_every_authority_flag_and_operation_counter_is_false_or_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.request["access_counters"].values()))

    def test_exclusions_keep_neural_model_provider_and_claim_work_closed(self):
        exclusions = self.request["explicit_exclusions"]
        for key in (
            "operation_before_green_decision_or_green_executor",
            "old_consumed_executors_roots_markers_reports_or_results",
            "network_or_download",
            "archive_local_header_member_or_payload",
            "signal_event_target_quality_or_channel",
            "derivative_cache_feature_split_or_neurotoken",
            "training_inference_prediction_freeze_delivery_or_score",
            "MARC2_FW2_CIL1_ORTH1_or_NDK_LANG1",
            "provider_language_model_stream_device_or_hardware",
            "release_publication_or_claim_upgrade",
        ):
            self.assertTrue(exclusions[key], key)

    def test_fresh_packet_bound_decision_is_required(self):
        gate = self.request["decision_gate"]
        self.assertTrue(gate["packet_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["sole_active_Tier_C_packet_identification_required"])
        self.assertTrue(gate["fresh_unambiguous_maintainer_words_required"])
        self.assertTrue(gate["separate_decision_commit_push_and_green_required"])
        self.assertTrue(gate["executor_commit_push_and_green_before_private_read_required"])
        self.assertFalse(gate["current_or_earlier_message_is_retroactive_authority"])

    def test_claim_boundary_is_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertIn("exact green live-schema adapter", boundary["engineering_capability_requested"])
        self.assertIn("reads no neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
