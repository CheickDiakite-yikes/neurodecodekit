from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc1_source_aware_live_metadata_authorization_decision.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs" / "MARC_1_SOURCE_AWARE_LIVE_METADATA_AUTHORIZATION_DECISION.md"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_blob_sha1(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(
        b"blob " + str(len(body)).encode("ascii") + b"\0" + body
    ).hexdigest()


class MARC1SourceAwareLiveMetadataAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_decision_identity_and_green_effective_gate_are_exact(self) -> None:
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc1_source_aware_live_metadata_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC1-SA1A")
        self.assertEqual(
            self.decision["authorization_parent_commit"],
            "b0775501e8d7dc5b28b81692dbc7fb02d423be95",
        )
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_commit_CI_jobs_and_hashes_are_exact(self) -> None:
        request = self.decision["green_request"]
        self.assertEqual(request["commit"], self.decision["authorization_parent_commit"])
        self.assertEqual(request["CI_run_id"], 31_621_794_066)
        self.assertEqual(request["base_python_job_id"], 94_198_174_069)
        self.assertEqual(request["optional_neuro_job_id"], 94_198_173_901)
        self.assertEqual(request["base_python_conclusion"], "success")
        self.assertEqual(request["optional_neuro_conclusion"], "success")
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(
            request["request_SHA256"],
            "f5421681fe5ceb6a4b154de692bff81619c87338c832e4e04640bfcad9ca4659",
        )

    def test_every_bound_artifact_hash_size_and_blob_match(self) -> None:
        for binding in self.decision["bound_artifacts"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])
                self.assertEqual(_git_blob_sha1(path), binding["git_blob_sha1"])

    def test_actual_user_message_is_verbatim_and_hash_bound(self) -> None:
        user = self.decision["user_authorization"]
        message = "let’s do those 5 systemically"
        payload = message.encode("utf-8")
        self.assertEqual(user["actual_message_verbatim"], message)
        self.assertEqual(len(payload), 31)
        self.assertEqual(user["actual_message_UTF8_bytes"], 31)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), user["actual_message_SHA256"])
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(user["later_unpacketized_steps_authorized_by_this_record"])
        self.assertFalse(user["positive_result_predeclared"])

    def test_short_form_rule_binds_only_the_identified_packet(self) -> None:
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["exactly_one_active_packet_required"])
        self.assertTrue(rule["packet_and_request_green_before_message"])
        self.assertTrue(rule["assistant_named_scope_and_fresh_decision_gate"])
        self.assertTrue(rule["maintainer_unambiguously_directed_execution"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(
            rule[
                "future_acquisition_experiment_score_replication_or_language_authority_inferred"
            ]
        )

    def test_order_requires_green_decision_then_green_wrapper(self) -> None:
        order = self.decision["required_execution_order"]
        self.assertLess(
            order.index("decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_and_mocked_wrapper_implementation"),
        )
        self.assertLess(
            order.index("exact_wrapper_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_registered_live_metadata_invocation"),
        )
        self.assertLess(
            order.index("one_registered_live_metadata_invocation"),
            order.index("stop_before_payload_and_prepare_only_route_conditioned_future_contracts"),
        )

    def test_exact_one_response_scope_and_zero_payload_are_preserved(self) -> None:
        source = self.decision["registered_sequence"]["Wrist_public_metadata"]
        self.assertEqual((source["record_id"], source["version"]), (29_666_735, 3))
        self.assertEqual(source["query"], "page=1&page_size=1000")
        self.assertEqual((source["request_attempts"], source["redirects"]), (1, 0))
        self.assertEqual(source["accepted_body_count"], 1)
        self.assertEqual(source["accepted_body_cap_bytes"], 2 * 1024**2)
        self.assertEqual((source["payload_requests"], source["payload_bytes"]), (0, 0))

    def test_source_schema_and_historical_split_identity_are_exact(self) -> None:
        semantic = self.decision["semantic_contract"]
        self.assertEqual(
            semantic["required_public_core_fields"],
            ["id", "name", "size", "is_link_only", "download_url"],
        )
        self.assertEqual(
            semantic["known_optional_MD5_fields"],
            ["supplied_md5", "computed_md5"],
        )
        self.assertEqual(
            (
                semantic["historical_file_rows"],
                semantic["historical_participant_archives"],
                semantic["historical_supplementary_rows"],
            ),
            (55, 45, 10),
        )
        self.assertEqual(semantic["historical_declared_record_bytes"], 3_683_416_050)
        self.assertEqual(
            semantic["selected_Wrist_subjects_only_if_complete_historical_match"], 12
        )
        self.assertEqual(semantic["fit_runs_if_eligible"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(semantic["heldout_runs_if_eligible"], [7, 8])
        self.assertFalse(semantic["target_quality_checksum_or_outcome_selects_rows"])

    def test_source_aware_routes_block_drift_and_every_route_stops(self) -> None:
        routes = self.decision["route_contract"]
        for route in ("MARC1SA-R1", "MARC1SA-R2"):
            self.assertEqual(routes[route]["wrapper_route"], "MARC1SAL-R1")
            self.assertTrue(routes[route]["selection_available"])
            self.assertFalse(routes[route]["payload_available"])
        for route in ("MARC1SA-R3", "MARC1SA-R4"):
            self.assertEqual(routes[route]["wrapper_route"], "MARC1SAL-R2")
            self.assertFalse(routes[route]["selection_available"])
            self.assertFalse(routes[route]["payload_available"])
        self.assertEqual(len(routes["failure_routes"]), 5)
        self.assertTrue(routes["every_result_or_failure_consumes_lane"])
        self.assertFalse(routes["post_response_route_or_selection_update_allowed"])

    def test_transport_is_bounded_uncoded_and_no_retry(self) -> None:
        transport = self.decision["transport_contract"]
        self.assertTrue(transport["bounded_cap_plus_one_read"])
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_identity_Content_Encoding_accepted"])
        self.assertTrue(transport["other_Content_Encoding_refused"])
        self.assertTrue(transport["duplicate_or_conflicting_framing_refused"])
        self.assertEqual(transport["content_decoding_or_decompression_operations"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_output_and_resource_caps_protect_storage_and_other_projects(self) -> None:
        output = self.decision["output_contract"]
        resources = self.decision["resource_boundary"]
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(output["private_manifest_mode"], "0600")
        self.assertFalse(output["unknown_extension_values_persisted"])
        self.assertFalse(output["preexisting_path_overwrite_move_delete_or_rename"])
        self.assertEqual(resources["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 4 * 1024**2)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertFalse(resources["operation_on_another_project"])

    def test_conditional_authority_and_decision_only_counters_are_exact(self) -> None:
        authorization = self.decision["authorization"]
        self.assertTrue(authorization["wrapper_implementation_after_decision_green"])
        self.assertTrue(authorization["one_live_metadata_request_after_wrapper_green"])
        for key, value in authorization.items():
            if key.endswith("_authorized_now"):
                with self.subTest(key=key):
                    self.assertFalse(value)
        counters = self.decision["decision_only_counters"]
        for key, value in counters.items():
            if key != "GitHub_CI_verification_calls":
                with self.subTest(key=key):
                    self.assertEqual(value, 0)
        self.assertEqual(counters["GitHub_CI_verification_calls"], 1)
        self.assertFalse(self.decision["end_to_end_latency_measured"])

    def test_document_preserves_exact_words_and_scientific_boundary(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "> let’s do those 5 systemically",
            "This record preserves those exact 31 UTF-8 bytes",
            "Only the first packeted sequence is authorized here.",
            "Engineering capability authorized for testing:",
            "Scientific claim not established:",
            "Research objective preserved:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)
        claim = self.decision["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        self.assertFalse(claim["current_scientific_claim_upgrade"])


if __name__ == "__main__":
    unittest.main()
