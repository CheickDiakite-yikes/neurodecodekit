import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc2_live_selection_recovery_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveSelectionRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_lane_and_all_false_status_are_exact(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_live_selection_recovery_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC2-FW1C")
        self.assertEqual(
            self.request["request_id"],
            "MARC-2-FW1C-live-selection-recovery-authorization-request-v0",
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

    def test_green_shared_validator_implementation_is_exact(self):
        proof = self.request["green_shared_validator_implementation"]
        self.assertEqual(
            proof["commit"],
            "6f613b339dfe8a7bd2df69a48c1ac32b72554f7b",
        )
        self.assertEqual(proof["CI_run_id"], 31_768_593_977)
        self.assertEqual(proof["base_python_job_id"], 94_669_566_174)
        self.assertEqual(proof["optional_neuro_job_id"], 94_669_566_187)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["implementation_registry_sha256"],
            "2b1ff6c9d41d7bae14686cbf16a2aa129d702842622ca990468a3263f68e66b6",
        )

    def test_old_lane_is_consumed_and_cannot_be_reused(self):
        boundary = self.request["consumed_and_generated_boundaries"]
        self.assertTrue(boundary["MARC2_FW1A_consumed"])
        self.assertFalse(boundary["MARC2_FW1A_retry_repair_or_reuse"])
        self.assertTrue(boundary["MARC2_FW1B_generated_only"])
        self.assertEqual(boundary["MARC2_FW1B_private_execution_limit"], 0)
        self.assertFalse(boundary["MARC2_FW2_eligible"])

    def test_future_sequence_has_decision_wrapper_and_private_green_gates(self):
        sequence = self.request["proposed_sequence"]
        self.assertEqual([stage["ordinal"] for stage in sequence], [1, 2])
        self.assertEqual(sequence[0]["stage_id"], "MARC2-FW1C-wrapper")
        self.assertEqual(sequence[1]["stage_id"], "MARC2-FW1C-private-selection")
        self.assertTrue(sequence[0]["green_decision_required_first"])
        self.assertTrue(sequence[1]["green_wrapper_required_first"])
        self.assertFalse(sequence[0]["currently_authorized"])
        self.assertFalse(sequence[1]["currently_authorized"])

    def test_certificate_and_native_registry_have_distinct_exact_lanes(self):
        design = self.request["future_proof_certificate"]
        self.assertEqual(design["certificate_schema_lane"], "MARC2-FW1B")
        self.assertEqual(design["native_wrapper_registry_lane"], "MARC2-FW1C")
        self.assertEqual(
            design["shared_validator_module"],
            "neurodecodekit.datasets.marc2_proof_record_recovery",
        )
        self.assertEqual(
            design["shared_validator_symbol"],
            "validate_implementation_record",
        )
        self.assertTrue(design["certificate_binds_wrapper_module_and_registry"])
        self.assertTrue(design["expected_and_observed_proofs_bind_wrapper_HEAD"])
        self.assertFalse(design["older_validator_HEAD_substituted_for_wrapper_HEAD"])

    def test_future_wrapper_is_additive_and_forbids_consumed_import(self):
        wrapper = self.request["future_wrapper_surface"]
        self.assertEqual(
            wrapper["module"],
            "neurodecodekit.datasets.marc2_freewill_private_selection_recovery",
        )
        self.assertEqual(wrapper["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(wrapper["standard_library_only"])
        self.assertTrue(wrapper["shared_validator_import_required"])
        self.assertFalse(wrapper["consumed_FW1A_import_call_or_edit_allowed"])
        self.assertFalse(wrapper["generic_source_or_output_override_available"])

    def test_private_source_identity_is_exact_and_currently_closed(self):
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
        self.assertFalse(source["path_stat_resolve_open_hash_or_parse_authorized_now"])

    def test_new_output_root_is_distinct_absent_and_currently_untouched(self):
        output = self.request["future_output_contract"]
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_freewill_prefix/live_selection_recovery_v1",
        )
        self.assertNotEqual(output["root"], output["forbidden_consumed_v0_root"])
        self.assertTrue(output["root_must_be_absent_and_non_symlink_at_execution"])
        self.assertFalse(output["root_stat_create_or_reserve_authorized_now"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertFalse(output["overwrite_allowed"])

    def test_path_protocol_is_one_open_no_follow_and_no_siblings(self):
        path = self.request["future_path_protocol"]
        self.assertFalse(path["resolve_glob_listdir_or_sibling_access_allowed"])
        self.assertTrue(path["no_follow_component_and_final_checks_required"])
        self.assertEqual(path["content_opens"], 1)
        self.assertEqual(path["sequential_reads"], 1)
        self.assertEqual(path["SHA256_passes"], 1)
        self.assertEqual(path["strict_JSON_parses"], 1)
        self.assertFalse(path["second_open_retry_rerun_or_resume_allowed"])

    def test_selection_rule_remains_exact_target_free_and_storage_bounded(self):
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
        self.assertFalse(rule["target_label_event_quality_signal_or_outcome_input_allowed"])

    def test_future_generated_qualification_has_all_three_matrices(self):
        qualification = self.request["future_wrapper_qualification"]
        self.assertEqual(qualification["proof_record_mutations"], 32)
        self.assertEqual(qualification["selector_mutations"], 40)
        self.assertEqual(qualification["wrapper_mutations"], 18)
        self.assertEqual(qualification["total_mutations"], 90)
        self.assertTrue(qualification["actual_native_registry_must_pass_own_loader"])
        self.assertTrue(qualification["actual_certificate_must_pass_shared_validator"])
        self.assertEqual(qualification["private_source_operations"], 0)

    def test_router_consumes_and_success_stops_before_payload(self):
        router = self.request["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC2FWC-R1")
        self.assertTrue(router["every_route_consumes_invocation"])
        self.assertFalse(router["success_authorizes_archive_member_or_payload"])
        self.assertFalse(router["success_authorizes_MARC2_FW2"])
        self.assertFalse(router["success_is_scientific_result"])

    def test_resource_caps_are_small_and_payload_is_zero(self):
        caps = self.request["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["runtime_seconds"], 30)
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

    def test_exclusions_keep_payload_neural_model_and_claim_work_closed(self):
        exclusions = self.request["explicit_exclusions"]
        for key in (
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
        self.assertTrue(gate["wrapper_commit_push_and_green_before_private_read_required"])
        self.assertFalse(gate["current_or_earlier_message_is_retroactive_authority"])

    def test_claim_boundary_is_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertIn(
            "shared proof validator",
            boundary["engineering_capability_requested"],
        )
        self.assertIn(
            "reads no human neural data",
            boundary["scientific_claim_not_established"],
        )
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
