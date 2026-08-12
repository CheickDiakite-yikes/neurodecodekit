import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc1_http_identity_live_recovery_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1HttpIdentityLiveRecoveryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_awaits_a_fresh_decision(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc1_http_identity_live_recovery_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC1-HT1A")
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_green_generated_semantics_result_is_exact(self):
        proof = self.request["green_generated_semantics_result"]
        self.assertEqual(proof["commit"], "5344d73bb74431e9bba05e3608c2a1523a84cd00")
        self.assertEqual(proof["push_CI_run_id"], 31_584_662_864)
        self.assertEqual(proof["base_python_job_id"], 94_075_586_323)
        self.assertEqual(proof["optional_neuro_job_id"], 94_075_586_171)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["route"], "MARC1HT-G1")
        self.assertTrue(proof["registered_closeout_consumed"])

    def test_consumed_prior_lane_cannot_be_reopened_or_inferred(self):
        consumed = self.request["consumed_prior_live_result"]
        self.assertEqual(consumed["route"], "MARC1PS-F03")
        self.assertFalse(consumed["retry_or_rerun_available"])
        self.assertFalse(consumed["old_private_root_or_material_may_be_opened"])
        self.assertFalse(consumed["live_header_value_retained"])
        self.assertFalse(consumed["live_header_value_may_be_inferred"])
        self.assertEqual(
            consumed["old_private_invocation_root_relative_path"],
            ".codex_work/marc1_pilot_selection/live_selection_v0",
        )

    def test_upstream_manifest_is_bound_separately_from_consumed_root(self):
        upstream = self.request["green_upstream_inventory_result"]
        private = self.request["private_manifest_contract"]
        self.assertEqual(upstream["route"], "MARC1CD-R1")
        self.assertEqual(upstream["private_manifest_bytes"], 418_755)
        self.assertEqual(upstream["private_manifest_mode"], "0600")
        self.assertFalse(upstream["private_manifest_opened_during_request_preparation"])
        self.assertTrue(
            private["upstream_sealed_artifact_is_distinct_from_consumed_invocation_root"]
        )
        self.assertFalse(private["old_consumed_root_opened"])

    def test_every_bound_artifact_hash_matches(self):
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_exact_two_input_scope_is_frozen_and_payload_free(self):
        scope = self.request["requested_scope"]
        freewill = scope["Freewill_private_inventory"]
        wrist = scope["Wrist_public_metadata"]
        self.assertEqual(freewill["bytes"], 418_755)
        self.assertEqual(freewill["mode"], "0600")
        self.assertEqual(freewill["content_opens"], 1)
        self.assertEqual(freewill["payload_opens"], 0)
        self.assertEqual((wrist["record_id"], wrist["version"]), (29_666_735, 3))
        self.assertEqual(wrist["accepted_body_count"], 1)
        self.assertEqual(wrist["accepted_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(wrist["expected_file_rows"], 55)
        self.assertEqual((wrist["payload_requests"], wrist["payload_bytes"]), (0, 0))

    def test_wrapper_and_live_selection_are_strictly_ordered_and_additive(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("additive_generated_fixture_and_mock_live_wrapper_implementation"),
        )
        self.assertLess(
            order.index("exact_additive_wrapper_commit_pushed_and_both_CI_jobs_green"),
            order.index("pre_consumption_machine_gate_and_new_isolated_private_marker"),
        )
        wrapper = self.request["future_live_wrapper_contract"]
        self.assertTrue(wrapper["generated_and_mocked_only_before_green_commit"])
        self.assertFalse(wrapper["real_private_path_available_before_green_commit"])
        self.assertFalse(wrapper["real_endpoint_available_before_green_commit"])
        self.assertFalse(wrapper["may_import_call_modify_or_expose_consumed_live_executor"])
        self.assertTrue(wrapper["old_private_invocation_root_forbidden"])
        self.assertFalse(wrapper["payload_interface_exists"])

    def test_HTTP_identity_rule_is_exact_and_never_decodes(self):
        transport = self.request["public_transport_contract"]
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_case_insensitive_identity_Content_Encoding_accepted"])
        self.assertTrue(transport["other_present_Content_Encoding_refused"])
        self.assertTrue(transport["duplicate_or_list_Content_Encoding_refused"])
        self.assertTrue(transport["Transfer_Encoding_refused"])
        self.assertEqual(transport["decoding_or_decompression_operations"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_frozen_selection_counts_splits_and_target_firewall_are_exact(self):
        selection = self.request["selection_contract"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_selected_run_bundles"], 72)
        self.assertEqual(selection["Freewill_selected_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertEqual(selection["Freewill_fit_session"], "ses-01")
        self.assertEqual(selection["Freewill_heldout_session"], "ses-02")
        self.assertEqual(selection["Wrist_fit_runs"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(selection["Wrist_heldout_runs"], [7, 8])
        self.assertFalse(selection["size_CRC_quality_target_or_outcome_may_affect_selection"])
        self.assertFalse(selection["post_input_cohort_split_or_parser_update_allowed"])

    def test_every_current_authorization_flag_and_counter_is_false_or_zero(self):
        authorization = self.request["authorization"]
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        self.assertTrue(authorization["short_form_may_bind_after_request_is_remotely_green"])
        for key, value in authorization.items():
            if key.endswith("_authorized_now") or key in {
                "exact_or_short_form_decision_received_from_user",
                "current_or_prior_continue_is_retroactive_authorization",
                "general_research_autonomy_is_exact_Tier_C_authorization",
            }:
                with self.subTest(key=key):
                    self.assertFalse(value)
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))

    def test_machine_caps_and_next_gate_protect_the_computer(self):
        resources = self.request["resource_caps"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 12 * 1024 * 1024 * 1024)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["real_selection_wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["network_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 4 * 1024 * 1024)
        gate = self.request["next_gate"]
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["fresh_packet_bound_user_decision_received"])
        self.assertFalse(gate["generated_or_mocked_live_wrapper_implementation_may_begin"])
        self.assertFalse(gate["real_metadata_selection_may_begin"])
        self.assertFalse(gate["payload_acquisition_may_begin"])

    def test_human_packet_preserves_same_path_privacy_and_claim_boundary(self):
        packet = (
            ROOT / "docs" / "MARC_1_HTTP_IDENTITY_LIVE_RECOVERY_AUTHORIZATION_PACKET.md"
        ).read_text(encoding="utf-8")
        self.assertIn("This packet authorizes nothing by itself.", packet)
        self.assertIn("Same Path, Not A Pivot", packet)
        self.assertIn("old `MARC1-P1A` invocation root", packet)
        self.assertIn("Engineering capability requested:", packet)
        self.assertIn("Scientific claim not established by this request:", packet)
        claim = self.request["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["movement_metadata_is_language_evidence"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established_by_request"])


if __name__ == "__main__":
    unittest.main()
