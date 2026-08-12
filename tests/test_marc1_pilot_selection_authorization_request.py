import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc1_privacy_preserving_pilot_selection_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1PilotSelectionAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_awaits_a_fresh_decision(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc1_privacy_preserving_pilot_selection_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC1-P1A")
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_green_generated_result_proof_is_exact(self):
        proof = self.request["green_generated_result"]
        self.assertEqual(proof["commit"], "fd246294db3defecdc11460e41945f64794b21cf")
        self.assertEqual(proof["push_CI_run_id"], 31_572_950_727)
        self.assertEqual(proof["base_python_job_id"], 94_038_664_052)
        self.assertEqual(proof["optional_neuro_job_id"], 94_038_664_104)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["generated_route"], "MARC1PSG-R1")

    def test_every_target_artifact_hash_matches(self):
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_exact_two_input_scope_is_frozen(self):
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
        self.assertEqual(wrist["payload_requests"], 0)

    def test_wrapper_and_real_selection_are_strictly_ordered(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_real_selector_implementation"),
        )
        self.assertLess(
            order.index("exact_real_selector_commit_pushed_and_both_CI_jobs_green"),
            order.index("pre_consumption_machine_gate_and_new_private_marker"),
        )
        self.assertLess(
            order.index("pre_consumption_machine_gate_and_new_private_marker"),
            order.index("one_no_follow_private_manifest_open_read_hash_and_parse"),
        )
        wrapper = self.request["future_real_selector_contract"]
        self.assertTrue(wrapper["generated_and_mocked_only_before_green_commit"])
        self.assertFalse(wrapper["real_private_path_available_before_green_commit"])
        self.assertFalse(wrapper["real_endpoint_available_before_green_commit"])
        self.assertFalse(wrapper["payload_interface_exists"])

    def test_frozen_selection_counts_splits_and_caps_are_exact(self):
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

    def test_every_current_authorization_flag_is_false(self):
        authorization = self.request["authorization"]
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        self.assertTrue(authorization["short_form_may_bind_after_request_is_remotely_green"])
        for key, value in authorization.items():
            if key.endswith("_authorized_now") or key in {
                "exact_or_short_form_decision_received_from_user",
                "current_continue_is_retroactive_authorization",
                "general_research_autonomy_is_exact_Tier_C_authorization",
            }:
                with self.subTest(key=key):
                    self.assertFalse(value)

    def test_transport_privacy_and_claim_boundaries_hold(self):
        transport = self.request["public_transport_contract"]
        self.assertEqual(transport["body_response_count"], 1)
        self.assertEqual(transport["HTTP_request_attempt_cap"], 3)
        self.assertEqual(transport["bodyless_redirect_cap"], 2)
        self.assertEqual(transport["terminal_status"], 200)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))
        self.assertFalse(transport["raw_response_body_persisted"])
        output = self.request["selector_and_output_contract"]
        self.assertTrue(output["private_selection_manifest_Git_ignored"])
        self.assertFalse(output["individual_member_or_archive_rows_public"])
        self.assertFalse(output["success_is_scientific_result"])
        self.assertFalse(output["success_authorizes_payload_acquisition"])

    def test_machine_and_resource_caps_protect_the_computer(self):
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
        self.assertEqual(resources["combined_output_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 4 * 1024 * 1024)

    def test_all_counters_are_zero_and_next_gate_is_closed(self):
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["fresh_packet_bound_user_decision_received"])
        self.assertFalse(gate["decision_record_exists"])
        self.assertFalse(gate["real_selector_implementation_may_begin"])
        self.assertFalse(gate["real_metadata_selection_may_begin"])
        self.assertFalse(gate["payload_acquisition_may_begin"])

    def test_short_form_requires_prior_identification_and_actual_words(self):
        short_form = self.request["packet_bound_short_form"]
        self.assertTrue(short_form["eligible_only_after_request_commit_is_pushed_and_both_CI_jobs_are_green"])
        self.assertTrue(short_form["eligible_only_if_this_is_the_sole_active_Tier_C_packet"])
        self.assertTrue(short_form["assistant_must_identify_packet_commit_CI_scope_and_boundary_first"])
        self.assertTrue(short_form["decision_artifact_quotes_actual_user_words"])
        self.assertFalse(short_form["long_scope_may_be_fabricated_as_user_words"])
        self.assertFalse(short_form["ambiguous_or_multiple_packet_short_form_allowed"])

    def test_human_packet_preserves_same_path_and_claim_boundary(self):
        packet = (
            ROOT
            / "docs"
            / "MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_AUTHORIZATION_PACKET.md"
        ).read_text(encoding="utf-8")
        self.assertIn("This packet authorizes nothing by itself.", packet)
        self.assertIn("same research path", packet)
        self.assertIn("Engineering capability requested:", packet)
        self.assertIn("Scientific claim not established by this request:", packet)
        claim = self.request["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["movement_metadata_is_language_evidence"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established_by_request"])


if __name__ == "__main__":
    unittest.main()
