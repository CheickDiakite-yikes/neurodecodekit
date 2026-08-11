import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT / "registries" / "iackd_snapshot_identity_authorization_request.v0.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSnapshotIdentityAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_awaiting_a_fresh_decision(self) -> None:
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.iackd_snapshot_identity_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "IACKD-M1A")
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_green_registration_and_implementation_are_exact(self) -> None:
        registration = self.request["green_registration"]
        self.assertEqual(registration["commit"], "1667e302e262ad23695f204a88d5a0997ac38270")
        self.assertEqual(registration["push_CI_run_id"], 31481270697)
        self.assertEqual(registration["base_python_job_id"], 93746523491)
        self.assertEqual(registration["optional_neuro_job_id"], 93746523322)
        self.assertTrue(registration["both_required_jobs_green"])
        implementation = self.request["green_implementation"]
        self.assertEqual(implementation["commit"], "7b8f47ba4b192953f4f60126521ba1839b828c85")
        self.assertEqual(implementation["push_CI_run_id"], 31483435801)
        self.assertEqual(implementation["base_python_job_id"], 93753325035)
        self.assertEqual(implementation["optional_neuro_job_id"], 93753324999)
        self.assertTrue(implementation["both_required_jobs_green"])

    def test_every_target_artifact_hash_matches(self) -> None:
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_exact_query_request_and_one_response_are_frozen(self) -> None:
        scope = self.request["requested_scope"]
        self.assertEqual(scope["provider"], "OpenNeuro")
        self.assertEqual(scope["dataset_id"], "ds006840")
        self.assertEqual(scope["snapshot_id"], "ds006840:1.0.0")
        self.assertEqual(scope["GraphQL_requests"], 1)
        self.assertEqual(scope["query_UTF8_bytes"], 316)
        self.assertEqual(
            scope["query_SHA256"],
            "246db737c72bcd001c60191b6f31bef24d5bfc9a40ca5fa61b8ba215b30e3db0",
        )
        self.assertEqual(scope["request_body_bytes"], 355)
        self.assertEqual(
            scope["request_body_SHA256"],
            "913b033e430cbbb28ae14850dd744a50bd0418ecb64206645f4367d32ddd8896",
        )
        self.assertEqual(scope["response_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(scope["S3_payload_requests"], 0)
        self.assertEqual((scope["retries"], scope["reruns"]), (0, 0))

    def test_wrapper_and_public_execution_are_strictly_ordered(self) -> None:
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_transport_wrapper_implementation"),
        )
        self.assertLess(
            order.index("exact_wrapper_commit_pushed_and_both_CI_jobs_green"),
            order.index("pre_consumption_machine_gate_and_private_marker"),
        )
        self.assertLess(
            order.index("pre_consumption_machine_gate_and_private_marker"),
            order.index("one_exact_public_GraphQL_request"),
        )
        wrapper = self.request["future_wrapper_contract"]
        self.assertTrue(wrapper["generated_and_mocked_only_before_green_commit"])
        self.assertFalse(wrapper["real_endpoint_available_before_green_commit"])
        self.assertFalse(wrapper["local_IACKD_path_interface_exists"])
        self.assertFalse(wrapper["consumed_executor_import_or_call_exists"])

    def test_every_current_authorization_flag_is_false(self) -> None:
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

    def test_transport_canonicalization_privacy_and_claim_boundaries_hold(self) -> None:
        transport = self.request["public_transport_contract"]
        self.assertEqual(transport["HTTP_status"], 200)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["read_calls"], 1)
        self.assertEqual(transport["read_call_limit_bytes"], 2 * 1024 * 1024 + 1)
        self.assertFalse(transport["raw_body_persisted"])
        canonical = self.request["canonicalization_and_output_contract"]
        self.assertEqual(canonical["expected_success_route"], "IACKDM-R1")
        self.assertEqual(canonical["tree_rows"], 1679)
        self.assertEqual(canonical["selected_rows"], 1340)
        self.assertTrue(canonical["private_manifest_Git_ignored"])
        self.assertFalse(canonical["individual_rows_public"])
        self.assertFalse(canonical["success_is_scientific_result"])
        self.assertFalse(canonical["success_authorizes_EEG_payload"])

    def test_machine_and_resource_caps_protect_the_computer(self) -> None:
        resources = self.request["resource_caps"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 2 * 1024 * 1024 * 1024)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["public_execution_wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertEqual(resources["public_network_cap_bytes"], 355 + 2 * 1024 * 1024)
        self.assertEqual(resources["combined_output_cap_bytes"], 1024 * 1024)

    def test_all_counters_are_zero_and_next_gate_is_closed(self) -> None:
        self.assertTrue(all(value == 0 for value in self.request["current_access_counters"].values()))
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_required"])
        self.assertTrue(gate["request_commit_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertFalse(gate["fresh_packet_bound_user_decision_received"])
        self.assertFalse(gate["decision_record_exists"])
        self.assertFalse(gate["wrapper_implementation_may_begin"])
        self.assertFalse(gate["public_execution_may_begin"])
        self.assertFalse(gate["EEG_payload_access_may_begin"])

    def test_short_form_requires_prior_identification_and_actual_words(self) -> None:
        short_form = self.request["packet_bound_short_form"]
        self.assertTrue(short_form["eligible_only_after_request_commit_is_pushed_and_both_CI_jobs_are_green"])
        self.assertTrue(short_form["eligible_only_if_this_is_the_sole_active_Tier_C_packet"])
        self.assertTrue(short_form["assistant_must_identify_packet_commit_CI_scope_and_boundary_first"])
        self.assertTrue(short_form["decision_artifact_quotes_actual_user_words"])
        self.assertFalse(short_form["long_scope_may_be_fabricated_as_user_words"])
        self.assertFalse(short_form["ambiguous_or_multiple_packet_short_form_allowed"])

    def test_human_packet_separates_engineering_and_scientific_claims(self) -> None:
        packet = (
            ROOT / "docs" / "IACKD_SNAPSHOT_IDENTITY_AUTHORIZATION_PACKET.md"
        ).read_text(encoding="utf-8")
        self.assertIn("This packet authorizes nothing by itself.", packet)
        self.assertIn("Engineering capability requested:", packet)
        self.assertIn("Scientific claim not established by this request:", packet)
        self.assertIn("No EEG payload object may be requested", packet)
        claim = self.request["claim_boundary"]
        self.assertIn(
            "one",
            claim["engineering_capability_if_future_sequence_passes"].casefold(),
        )
        self.assertIn("no neural effect", claim["scientific_claim_not_established_by_request"])


if __name__ == "__main__":
    unittest.main()
