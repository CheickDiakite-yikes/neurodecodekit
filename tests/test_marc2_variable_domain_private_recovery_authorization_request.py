import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_variable_domain_private_recovery_authorization_request.v0.json"
)
DOC_PATH = (
    ROOT
    / "docs"
    / "MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_AUTHORIZATION_PACKET.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2VariableDomainPrivateRecoveryAuthorizationRequestTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_not_authorized(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_variable_domain_private_recovery_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-VR3")
        self.assertEqual(self.request["status"], "all_false_request_not_authorized")
        self.assertFalse(self.request["authorized"])

    def test_green_VR2_proof_is_exact(self):
        proof = self.request["green_variable_domain_adapter_proof"]
        self.assertEqual(
            proof["implementation_commit"],
            "f62a3f5b9966967c569e734552cbc3f11d009401",
        )
        self.assertEqual(proof["implementation_CI_run_id"], 31_946_112_252)
        self.assertEqual(proof["result_CI_run_id"], 31_946_852_669)
        self.assertEqual(
            proof["proof_addendum_commit"],
            "bdd34d92eb7abe743597f1a1001e4b6a296225af",
        )
        self.assertEqual(proof["proof_addendum_CI_run_id"], 31_947_198_122)
        self.assertTrue(proof["all_required_jobs_green"])

    def test_every_artifact_binding_is_current(self):
        for binding in self.request["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_consumed_lanes_and_roots_cannot_be_reused(self):
        boundaries = self.request["consumed_and_generated_boundaries"]
        self.assertTrue(boundaries["MARC2_LA2_consumed"])
        self.assertEqual(boundaries["MARC2_LA2_route"], "MARC2LAR-F02")
        self.assertFalse(boundaries["MARC2_LA2_retry_repair_or_reuse"])
        self.assertTrue(boundaries["MARC2_VR2_generated_only"])
        self.assertFalse(boundaries["MARC2_VR3_currently_authorized"])
        self.assertFalse(boundaries["MARC2_FW2_eligible"])
        self.assertFalse(boundaries["old_consumed_executor_or_output_root_allowed"])

    def test_two_stage_sequence_is_proof_gated_and_currently_closed(self):
        stages = self.request["proposed_sequence"]
        self.assertEqual([stage["ordinal"] for stage in stages], [1, 2])
        self.assertTrue(stages[0]["green_decision_required_first"])
        self.assertTrue(stages[1]["green_executor_required_first"])
        self.assertTrue(all(not stage["currently_authorized"] for stage in stages))
        self.assertEqual(stages[0]["private_path_operations"], 0)
        self.assertEqual(stages[1]["registered_executions"], 1)
        self.assertEqual(stages[1]["retry_or_rerun_limit"], 0)

    def test_future_executor_is_additive_and_forbids_consumed_modules(self):
        surface = self.request["future_executor_surface"]
        self.assertEqual(
            surface["module"],
            "neurodecodekit.datasets.marc2_variable_domain_private_recovery",
        )
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertFalse(surface["consumed_executor_import_call_copy_or_edit_allowed"])
        self.assertIn(
            "neurodecodekit.datasets.marc2_live_schema_adapter_recovery",
            surface["consumed_executor_modules"],
        )
        self.assertFalse(surface["generic_source_or_output_override_available"])

    def test_private_source_identity_is_bound_without_current_access(self):
        source = self.request["private_source"]
        self.assertEqual(
            source["path"],
            ".codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json",
        )
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["entries"], 1_227)
        self.assertEqual(source["regular_entries"], 1_025)
        self.assertEqual(source["directory_entries"], 202)
        self.assertFalse(source["path_stat_resolve_open_hash_or_parse_authorized_now"])
        self.assertFalse(source["sibling_or_directory_inspection_authorized_now"])

    def test_path_protocol_is_one_open_no_follow_and_no_retry(self):
        protocol = self.request["future_path_protocol"]
        self.assertTrue(protocol["literal_relative_path_only"])
        self.assertFalse(protocol["resolve_glob_listdir_or_sibling_access_allowed"])
        self.assertTrue(protocol["O_NOFOLLOW_required"])
        self.assertEqual(protocol["content_opens"], 1)
        self.assertEqual(protocol["sequential_reads"], 1)
        self.assertEqual(protocol["SHA256_passes"], 1)
        self.assertEqual(protocol["strict_JSON_parses"], 1)
        self.assertFalse(protocol["second_open_retry_rerun_or_resume_allowed"])

    def test_new_output_root_is_distinct_absent_and_not_touched_now(self):
        output = self.request["future_output_contract"]
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_live_domain_private_recovery/v0",
        )
        self.assertIn(
            ".codex_work/marc2_freewill_prefix/live_alias_recovery_v2",
            output["forbidden_consumed_roots"],
        )
        self.assertTrue(output["root_must_be_absent_and_non_symlink_at_execution"])
        self.assertFalse(output["root_stat_create_or_reserve_authorized_now"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertFalse(output["overwrite_allowed"])

    def test_frozen_processing_uses_dynamic_VR2_classification(self):
        processing = self.request["frozen_processing"]
        self.assertEqual(processing["VR2_adapter_calls"], 1)
        self.assertEqual(
            processing["VR2_adapter_public_symbol"], "adapt_live_domain_source"
        )
        self.assertTrue(processing["all_238_bundles_validated_before_filter"])
        self.assertEqual(processing["eligible_run_bundles"], 195)
        self.assertEqual(processing["valid_ineligible_run_bundles"], 43)
        self.assertFalse(processing["exact_ineligible_predicate_breakdown_required"])
        self.assertTrue(processing["source_object_must_remain_unchanged"])
        self.assertEqual(
            processing["target_label_event_quality_signal_channel_or_outcome_inputs"],
            0,
        )

    def test_selection_rule_is_target_free_and_unchanged(self):
        selection = self.request["frozen_selection_rule"]
        self.assertEqual(selection["public_eligible_subjects"], 19)
        self.assertEqual(selection["minimum_subjects"], 12)
        self.assertEqual(selection["maximum_subjects"], 19)
        self.assertEqual(selection["fit_session"], "ses-01")
        self.assertEqual(selection["heldout_session"], "ses-02")
        self.assertEqual(selection["selected_runs_each_session"], [1, 2, 3])
        self.assertEqual(selection["reservation_cap_bytes"], 8_589_934_592)
        self.assertFalse(selection["real_selection_identity_assumed_from_generated"])
        self.assertFalse(selection["target_label_event_quality_signal_or_outcome_input_allowed"])

    def test_generated_qualification_is_bounded_and_private_free(self):
        qualification = self.request["future_generated_qualification"]
        self.assertGreaterEqual(qualification["proof_certificate_mutations"], 32)
        self.assertGreaterEqual(qualification["wrapper_mutations"], 32)
        self.assertEqual(qualification["success_profiles"], 4)
        self.assertEqual(qualification["success_paths"], 8)
        self.assertTrue(qualification["inherited_VR2_tests_run_in_complete_suite"])
        self.assertEqual(qualification["private_source_operations"], 0)
        self.assertEqual(qualification["network_operations"], 0)

    def test_router_is_ordered_consuming_and_stops_before_FW2(self):
        router = self.request["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC2VDR-R1")
        self.assertTrue(router["every_route_consumes_invocation"])
        self.assertFalse(router["success_authorizes_archive_member_or_payload"])
        self.assertFalse(router["success_authorizes_MARC2_FW2"])
        self.assertFalse(router["success_is_scientific_result"])

    def test_resources_are_small_single_thread_and_zero_network(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds_per_stage"], 30)
        self.assertEqual(caps["peak_RSS_bytes"], 268_435_456)
        self.assertEqual(caps["private_input_bytes"], 418_755)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["archive_local_header_or_member_bytes"], 0)
        self.assertEqual(caps["incremental_disk_bytes"], 4_194_304)
        self.assertGreaterEqual(caps["minimum_free_disk_bytes"], 15 * 1024**3)

    def test_every_authorization_flag_is_false_and_counter_zero(self):
        self.assertTrue(
            all(not value for value in self.request["authorization_flags"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["access_counters"].values())
        )

    def test_explicit_exclusions_remain_closed(self):
        exclusions = self.request["explicit_exclusions"]
        self.assertTrue(all(exclusions.values()))
        self.assertTrue(exclusions["old_consumed_executors_roots_or_results"])
        self.assertTrue(exclusions["network_or_download"])
        self.assertTrue(exclusions["archive_local_header_member_or_payload"])
        self.assertTrue(exclusions["training_inference_prediction_freeze_delivery_or_score"])
        self.assertTrue(exclusions["release_publication_or_claim_upgrade"])

    def test_decision_gate_requires_fresh_words_after_remote_green(self):
        gate = self.request["decision_gate"]
        self.assertTrue(gate["packet_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["sole_active_Tier_C_packet_identification_required"])
        self.assertTrue(gate["fresh_unambiguous_maintainer_words_required"])
        self.assertTrue(gate["separate_decision_commit_push_and_green_required"])
        self.assertTrue(gate["executor_commit_push_and_green_before_private_read_required"])
        self.assertFalse(gate["current_or_earlier_message_is_retroactive_authority"])

    def test_document_and_claim_boundary_are_explicit(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("All authorization flags false", text)
        self.assertIn("The current `continue to eureka`", text)
        self.assertIn("Scientific claim not established", text)
        boundary = self.request["claim_boundary"]
        self.assertIn("variable-domain adapter", boundary["engineering_capability_requested"])
        self.assertIn("reads no neural data", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
