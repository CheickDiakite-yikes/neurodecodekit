import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc1_freewill_central_directory_authorization_request.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1FreewillCentralDirectoryAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_awaits_a_fresh_decision(self):
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc1_freewill_central_directory_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC1-CD1A")
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_green_result_proof_is_exact(self):
        proof = self.request["green_generated_result"]
        self.assertEqual(
            proof["commit"], "431ee8dc14118e4de5f5a3a9ae6e34a202cc238e"
        )
        self.assertEqual(proof["push_CI_run_id"], 31_512_598_915)
        self.assertEqual(proof["base_python_job_id"], 93_849_853_477)
        self.assertEqual(proof["optional_neuro_job_id"], 93_849_853_538)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["generated_route"], "MARC1CDG-R1")

    def test_every_target_artifact_hash_matches(self):
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_exact_source_identity_and_three_body_scope_are_frozen(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["provider"], "Figshare")
        self.assertEqual((scope["record_id"], scope["version"]), (28_632_599, 1))
        self.assertEqual(scope["file_id"], 57_518_986)
        self.assertEqual(scope["file_bytes"], 13_591_548_048)
        self.assertEqual(scope["tail_range_start"], 13_591_416_976)
        self.assertEqual(scope["tail_range_end"], 13_591_548_047)
        self.assertEqual(scope["tail_bytes"], 128 * 1024)
        self.assertEqual(scope["central_directory_cap_bytes"], 16 * 1024 * 1024)
        self.assertEqual(scope["accepted_response_body_count"], 3)
        self.assertEqual(scope["accepted_response_body_cap_bytes"], 17_039_360)
        self.assertEqual(scope["member_payload_requests"], 0)
        self.assertEqual((scope["retries"], scope["reruns"]), (0, 0))

    def test_wrapper_and_live_execution_are_strictly_ordered(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_live_wrapper_implementation"),
        )
        self.assertLess(
            order.index("exact_live_wrapper_commit_pushed_and_both_CI_jobs_green"),
            order.index("pre_consumption_machine_gate_and_private_marker"),
        )
        self.assertLess(
            order.index("pre_consumption_machine_gate_and_private_marker"),
            order.index("one_exact_version_metadata_request"),
        )
        wrapper = self.request["future_live_wrapper_contract"]
        self.assertTrue(wrapper["generated_and_mocked_only_before_green_commit"])
        self.assertFalse(wrapper["real_endpoint_available_before_green_commit"])
        self.assertFalse(wrapper["real_archive_path_interface_exists"])
        self.assertFalse(wrapper["member_payload_interface_exists"])

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

    def test_transport_parser_privacy_and_claim_boundaries_hold(self):
        transport = self.request["public_transport_contract"]
        self.assertEqual(transport["body_response_count"], 3)
        self.assertEqual(transport["HTTP_request_attempt_cap"], 5)
        self.assertEqual(transport["bodyless_redirect_cap"], 2)
        self.assertEqual(transport["tail_terminal_status"], 206)
        self.assertEqual(transport["directory_terminal_status"], 206)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["reruns"], 0)
        self.assertFalse(transport["raw_response_bodies_persisted"])
        output = self.request["parser_and_output_contract"]
        self.assertEqual(output["expected_success_route"], "MARC1CD-R1")
        self.assertTrue(output["private_manifest_Git_ignored"])
        self.assertFalse(output["individual_member_rows_public"])
        self.assertFalse(output["success_is_scientific_result"])
        self.assertFalse(output["success_authorizes_member_acquisition"])

    def test_machine_and_resource_caps_protect_the_computer(self):
        resources = self.request["resource_caps"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 12 * 1024 * 1024 * 1024)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["live_execution_wall_time_seconds"], 120)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["accepted_response_body_cap_bytes"], 17_039_360)
        self.assertEqual(resources["combined_output_cap_bytes"], 8 * 1024 * 1024)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 32 * 1024 * 1024)

    def test_all_counters_are_zero_and_next_gate_is_closed(self):
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_required"])
        self.assertTrue(gate["request_commit_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["fresh_packet_bound_user_decision_received"])
        self.assertFalse(gate["decision_record_exists"])
        self.assertFalse(gate["live_wrapper_implementation_may_begin"])
        self.assertFalse(gate["public_execution_may_begin"])
        self.assertFalse(gate["member_acquisition_may_begin"])

    def test_short_form_requires_prior_identification_and_actual_words(self):
        short_form = self.request["packet_bound_short_form"]
        self.assertTrue(short_form["eligible_only_after_request_commit_is_pushed_and_both_CI_jobs_are_green"])
        self.assertTrue(short_form["eligible_only_if_this_is_the_sole_active_Tier_C_packet"])
        self.assertTrue(short_form["assistant_must_identify_packet_commit_CI_scope_and_boundary_first"])
        self.assertTrue(short_form["decision_artifact_quotes_actual_user_words"])
        self.assertFalse(short_form["long_scope_may_be_fabricated_as_user_words"])
        self.assertFalse(short_form["ambiguous_or_multiple_packet_short_form_allowed"])

    def test_human_packet_separates_engineering_and_scientific_claims(self):
        packet = (
            ROOT / "docs" / "MARC_1_FREEWILL_CENTRAL_DIRECTORY_AUTHORIZATION_PACKET.md"
        ).read_text(encoding="utf-8")
        self.assertIn("This packet authorizes nothing by itself.", packet)
        self.assertIn("Engineering capability requested:", packet)
        self.assertIn("Scientific claim not established by this request:", packet)
        self.assertIn("may not download the archive", packet)
        claim = self.request["claim_boundary"]
        self.assertIn("17,039,360", claim["engineering_capability_if_future_sequence_passes"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established_by_request"])


if __name__ == "__main__":
    unittest.main()
