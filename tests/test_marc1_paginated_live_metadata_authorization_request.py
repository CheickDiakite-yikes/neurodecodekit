from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "marc1_paginated_live_metadata_authorization_request.v0.json"
)
PACKET_PATH = ROOT / "docs" / "MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_PACKET.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1PaginatedLiveMetadataAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_awaits_fresh_decision(self) -> None:
        self.assertEqual(
            self.request["schema_name"],
            "neurodecodekit.marc1_paginated_live_metadata_authorization_request",
        )
        self.assertEqual(self.request["schema_version"], "0.1.0")
        self.assertEqual(self.request["lane_id"], "MARC1-LM1")
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])

    def test_green_capability_result_is_exact_and_precedes_packet(self) -> None:
        proof = self.request["green_output_capability_result"]
        self.assertEqual(
            proof["commit"], "ca4679a95e3567a5d47094cc4282a63fa6986959"
        )
        self.assertEqual(proof["CI_run_id"], 31_601_329_375)
        self.assertEqual(proof["base_python_job_id"], 94_129_199_903)
        self.assertEqual(proof["optional_neuro_job_id"], 94_129_199_993)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["route"], "MARC1OP-G1")
        self.assertTrue(proof["registered_sequence_consumed"])

    def test_consumed_lanes_cannot_be_reopened_or_inferred(self) -> None:
        default_page = self.request["consumed_default_page_result"]
        generated = self.request["consumed_generated_pagination_result"]
        self.assertEqual(default_page["route"], "MARC1HTL-F04")
        self.assertFalse(default_page["actual_live_row_count_retained"])
        self.assertFalse(default_page["retry_or_rerun_available"])
        self.assertEqual(generated["route"], "MARC1PG-F07")
        self.assertFalse(generated["corrected_path_retry_available"])
        self.assertFalse(generated["retry_or_rerun_available"])

    def test_every_bound_artifact_hash_matches(self) -> None:
        for binding in self.request["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_exact_single_public_metadata_scope_is_frozen(self) -> None:
        source = self.request["requested_scope"]["Wrist_public_metadata"]
        self.assertEqual((source["record_id"], source["version"]), (29_666_735, 3))
        self.assertEqual(source["method"], "GET")
        self.assertEqual(source["query"], "page=1&page_size=1000")
        self.assertEqual(source["request_attempts"], 1)
        self.assertEqual(source["accepted_body_count"], 1)
        self.assertEqual(source["accepted_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual(source["expected_file_rows"], 55)
        self.assertEqual(source["expected_participant_archives"], 45)
        self.assertEqual(source["expected_supplementary_rows"], 10)
        self.assertEqual((source["payload_requests"], source["payload_bytes"]), (0, 0))

    def test_implementation_and_live_access_are_strictly_ordered(self) -> None:
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_wrapper_implementation"),
        )
        self.assertLess(
            order.index("exact_wrapper_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_registered_output_capability_and_consumed_marker"),
        )
        wrapper = self.request["future_wrapper_contract"]
        self.assertTrue(wrapper["generated_and_mocked_only_before_green_commit"])
        self.assertFalse(wrapper["real_endpoint_available_before_green_commit"])
        self.assertFalse(wrapper["may_import_call_modify_or_expose_consumed_executors"])
        self.assertFalse(wrapper["payload_interface_exists"])

    def test_transport_is_bounded_uncoded_and_no_retry(self) -> None:
        transport = self.request["transport_contract"]
        self.assertEqual((transport["request_attempts"], transport["redirects"]), (1, 0))
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_identity_Content_Encoding_accepted"])
        self.assertTrue(transport["other_Content_Encoding_refused"])
        self.assertTrue(transport["bounded_cap_plus_one_read"])
        self.assertTrue(transport["absent_Content_Length_accepted"])
        self.assertTrue(transport["single_exact_chunked_framing_accepted"])
        self.assertEqual(transport["content_decoding_or_decompression_operations"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_target_free_semantic_and_split_identity_is_exact(self) -> None:
        semantic = self.request["semantic_contract"]
        self.assertEqual(semantic["file_rows"], 55)
        self.assertEqual(semantic["participant_archives"], 45)
        self.assertEqual(semantic["supplementary_rows"], 10)
        self.assertEqual(semantic["declared_record_bytes"], 3_683_416_050)
        self.assertEqual(semantic["selected_Wrist_subjects"], 12)
        self.assertEqual(semantic["fit_runs"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(semantic["heldout_runs"], [7, 8])
        self.assertEqual(semantic["fit_heldout_overlap"], 0)
        self.assertFalse(semantic["target_quality_size_checksum_or_outcome_selects_rows"])

    def test_output_is_small_private_and_does_not_touch_existing_paths(self) -> None:
        output = self.request["output_contract"]
        self.assertEqual(
            output["registered_output_path"],
            "/private/tmp/neurodecodekit-marc1lm1-live-metadata-20260812",
        )
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(output["private_manifest_mode"], "0600")
        self.assertFalse(output["preexisting_path_overwrite_move_delete_or_rename"])
        self.assertFalse(output["private_rows_or_source_values_committed"])
        self.assertFalse(output["success_authorizes_payload_access"])

    def test_every_authorization_flag_and_access_counter_is_false_or_zero(self) -> None:
        authorization = self.request["authorization"]
        self.assertTrue(authorization["separate_authorization_decision_required"])
        self.assertTrue(authorization["short_form_may_bind_after_request_is_green"])
        for key, value in authorization.items():
            if key.endswith("_authorized_now") or key in {
                "packet_bound_decision_received",
                "current_or_prior_message_is_retroactive_authorization",
                "general_autonomy_is_Tier_C_authorization",
            }:
                with self.subTest(key=key):
                    self.assertFalse(value)
        self.assertTrue(
            all(value == 0 for value in self.request["current_access_counters"].values())
        )

    def test_resource_caps_protect_computer_and_storage(self) -> None:
        resources = self.request["resource_caps"]
        self.assertEqual(resources["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(resources["maximum_one_minute_load_per_logical_CPU"], 1.0)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["network_body_cap_bytes"], 2 * 1024**2)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 4 * 1024**2)
        self.assertEqual((resources["retries"], resources["reruns"]), (0, 0))

    def test_next_gate_requires_green_packet_then_fresh_user_words(self) -> None:
        gate = self.request["next_gate"]
        self.assertTrue(gate["request_commit_required"])
        self.assertTrue(gate["request_push_required"])
        self.assertTrue(gate["both_remote_CI_jobs_green_required"])
        self.assertTrue(gate["assistant_identifies_scope_before_fresh_message"])
        self.assertFalse(gate["fresh_packet_bound_user_decision_received"])
        self.assertFalse(gate["implementation_may_begin"])
        self.assertFalse(gate["live_metadata_request_may_begin"])
        self.assertFalse(gate["payload_access_may_begin"])

    def test_packet_preserves_same_path_and_scientific_boundary(self) -> None:
        packet = PACKET_PATH.read_text(encoding="utf-8")
        for phrase in (
            "This packet authorizes nothing by itself.",
            "Same Path, Not A Pivot",
            "Engineering capability requested:",
            "Scientific claim not established by this request:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, packet)
        claim = self.request["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["metadata_is_neural_or_language_evidence"])
        self.assertFalse(claim["current_scientific_claim_upgrade"])


if __name__ == "__main__":
    unittest.main()
