import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_private_selection_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrivateSelectionAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_identity_and_all_false_status_are_exact(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc2_freewill_private_selection_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(
            self.request["request_id"],
            "MARC-2-FW1A-private-selection-authorization-request-v0",
        )
        self.assertEqual(self.request["status"], "all_false_request_not_authorized")
        self.assertFalse(self.request["authorized"])

    def test_artifact_bindings_are_current(self):
        for binding in self.request["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_generated_result_proof_is_exact(self):
        proof = self.request["green_result_proof"]
        self.assertEqual(
            proof["commit"], "a9a759aa5626a41812afe546f03aa324db7a534e"
        )
        self.assertEqual(proof["CI_run_id"], 31_678_418_324)
        self.assertEqual(proof["base_job_id"], 94_378_074_196)
        self.assertEqual(proof["optional_neuro_job_id"], 94_378_074_181)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["result_route"], "MARC2FWG-R1")
        self.assertTrue(proof["result_consumed"])

    def test_future_sequence_has_two_separate_green_stages(self):
        sequence = self.request["proposed_sequence"]
        self.assertEqual(
            [stage["stage_id"] for stage in sequence],
            ["MARC2-FW1A-wrapper", "MARC2-FW1A-private-execution"],
        )
        self.assertTrue(sequence[0]["decision_must_be_remotely_green_first"])
        self.assertTrue(sequence[1]["exact_wrapper_must_be_remotely_green_first"])
        self.assertFalse(sequence[0]["currently_authorized"])
        self.assertFalse(sequence[1]["currently_authorized"])

    def test_private_source_identity_is_exact_and_currently_closed(self):
        source = self.request["private_source"]
        self.assertEqual(
            source["path"],
            ".codex_work/marc1_central_directory/live_audit_v0/member_inventory.private.v0.json",
        )
        self.assertEqual(source["bytes"], 418_755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(
            source["sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertEqual(source["entries"], 1_227)
        self.assertFalse(source["path_stat_resolve_or_open_currently_authorized"])
        self.assertFalse(source["sibling_inspection_authorized"])

    def test_future_path_operations_are_no_follow_and_single_open(self):
        path = self.request["future_path_protocol"]
        self.assertFalse(path["resolve_glob_listdir_or_sibling_access_allowed"])
        self.assertTrue(path["no_follow_parent_and_final_checks_required"])
        self.assertTrue(path["O_NOFOLLOW_required"])
        self.assertEqual(path["content_opens"], 1)
        self.assertEqual(path["sequential_reads"], 1)
        self.assertEqual(path["SHA256_passes"], 1)
        self.assertEqual(path["strict_JSON_parses"], 1)
        self.assertTrue(path["open_fstat_identity_reconciliation_required"])

    def test_output_root_and_three_file_limit_are_exact(self):
        output = self.request["future_output_contract"]
        self.assertEqual(
            output["root"],
            ".codex_work/marc2_freewill_prefix/live_selection_v0",
        )
        self.assertTrue(output["root_must_be_absent_and_non_symlink"])
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(
            output["files"],
            ["consumed_marker", "private_selection_manifest", "aggregate_report"],
        )
        self.assertEqual(output["consumed_marker_mode"], "0600")
        self.assertEqual(output["private_selection_mode"], "0600")
        self.assertFalse(output["overwrite_allowed"])

    def test_selection_rule_is_exact_and_target_free(self):
        rule = self.request["frozen_selection_rule"]
        self.assertEqual(rule["minimum_subjects"], 12)
        self.assertEqual(rule["maximum_subjects"], 19)
        self.assertEqual(rule["fit_session"], "ses-01")
        self.assertEqual(rule["heldout_session"], "ses-02")
        self.assertEqual(rule["run_bundles_per_subject"], 6)
        self.assertEqual(rule["members_per_subject"], 24)
        self.assertEqual(rule["reservation_cap_bytes"], 8 * 1024**3)
        self.assertTrue(rule["maximal_contiguous_prefix_required"])
        self.assertFalse(rule["skip_substitute_backfill_or_cap_change_allowed"])
        self.assertFalse(rule["event_target_quality_signal_or_outcome_input_allowed"])

    def test_wrapper_qualification_adds_eighteen_refusals(self):
        qualification = self.request["future_wrapper_qualification"]
        self.assertEqual(qualification["inherited_selector_mutations"], 40)
        self.assertEqual(qualification["wrapper_specific_mutations"], 18)
        self.assertEqual(qualification["total_mutations"], 58)
        self.assertEqual(len(qualification["wrapper_specific_refusals"]), 18)
        self.assertEqual(
            qualification["commands"],
            ["plan", "qualify", "inspect", "execute"],
        )
        self.assertTrue(qualification["execute_proof_disabled_until_green"])

    def test_router_is_ordered_and_success_stops_before_payload(self):
        router = self.request["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC2FWS-R1")
        self.assertFalse(router["success_authorizes_archive_or_member_access"])
        self.assertFalse(router["success_is_scientific_result"])
        self.assertTrue(router["every_route_consumes_invocation"])

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

    def test_every_current_authority_and_operation_is_false_or_zero(self):
        self.assertTrue(
            all(value is False for value in self.request["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.request["access_counters"].values()))

    def test_exclusions_keep_all_later_work_closed(self):
        exclusions = self.request["explicit_exclusions"]
        for key in (
            "network_or_download",
            "archive_local_header_member_or_payload",
            "signal_event_target_quality_or_channel",
            "derivative_feature_cache_or_model_input",
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
        self.assertFalse(gate["current_or_earlier_message_is_retroactive_authority"])

    def test_claim_boundary_is_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertIn("private ZIP-directory manifest", boundary["engineering_capability_requested"])
        self.assertIn("reads no human neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
