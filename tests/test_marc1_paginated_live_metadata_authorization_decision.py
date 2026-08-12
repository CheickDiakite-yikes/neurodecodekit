from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT
    / "registries"
    / "marc1_paginated_live_metadata_authorization_decision.v0.json"
)
DOCUMENT_PATH = ROOT / "docs" / "MARC_1_PAGINATED_LIVE_METADATA_AUTHORIZATION_DECISION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1PaginatedLiveMetadataAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))

    def test_decision_identity_and_effective_green_gate_are_exact(self) -> None:
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.marc1_paginated_live_metadata_authorization_decision",
        )
        self.assertEqual(self.decision["schema_version"], "0.1.0")
        self.assertEqual(self.decision["lane_id"], "MARC1-LM1")
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )

    def test_green_request_commit_CI_jobs_and_hash_are_exact(self) -> None:
        request = self.decision["green_request"]
        self.assertEqual(
            request["commit"], "4d3eb19690676d48ce42ed16c5c00cc041d8bb4b"
        )
        self.assertEqual(request["CI_run_id"], 31_603_530_015)
        self.assertEqual(request["base_python_job_id"], 94_136_577_454)
        self.assertEqual(request["optional_neuro_job_id"], 94_136_577_639)
        self.assertTrue(request["both_required_jobs_green"])
        self.assertEqual(
            request["request_SHA256"],
            "798d05a52e86891467b54a6807475602d9f3530468bd5a4005768e9f966dac9d",
        )

    def test_every_bound_artifact_hash_and_blob_matches(self) -> None:
        for binding in self.decision["bound_artifacts"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_actual_user_message_is_verbatim_and_hash_bound(self) -> None:
        user = self.decision["user_authorization"]
        message = "approved, continue, achieve a scientific claim, achieve thought to text 😎"
        payload = message.encode("utf-8")
        self.assertEqual(user["actual_message_verbatim"], message)
        self.assertEqual(len(payload), 76)
        self.assertEqual(user["actual_message_UTF8_bytes"], 76)
        self.assertEqual(hashlib.sha256(payload).hexdigest(), user["actual_message_SHA256"])
        self.assertFalse(user["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(user["positive_result_predeclared"])

    def test_short_form_rule_preserves_exact_packet_scope(self) -> None:
        rule = self.decision["short_form_packet_rule"]
        self.assertTrue(rule["separate_Tier_C_permission_satisfied_for_this_packet"])
        self.assertTrue(rule["packet_and_request_green_before_message"])
        self.assertTrue(rule["assistant_named_scope_and_fresh_decision_gate"])
        self.assertTrue(rule["decision_quotes_actual_words_and_binds_scope"])
        self.assertFalse(rule["scope_expansion_by_short_form_allowed"])
        self.assertFalse(rule["aspirational_goal_predeclares_scientific_outcome"])

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

    def test_exact_one_response_scope_and_zero_payload_are_preserved(self) -> None:
        source = self.decision["registered_sequence"]["Wrist_public_metadata"]
        self.assertEqual(source["query"], "page=1&page_size=1000")
        self.assertEqual((source["request_attempts"], source["redirects"]), (1, 0))
        self.assertEqual(source["accepted_body_count"], 1)
        self.assertEqual(source["accepted_body_cap_bytes"], 2 * 1024 * 1024)
        self.assertEqual((source["payload_requests"], source["payload_bytes"]), (0, 0))

    def test_semantic_and_target_free_split_identity_is_exact(self) -> None:
        semantic = self.decision["semantic_contract"]
        self.assertEqual(
            (
                semantic["file_rows"],
                semantic["participant_archives"],
                semantic["supplementary_rows"],
            ),
            (55, 45, 10),
        )
        self.assertEqual(semantic["declared_record_bytes"], 3_683_416_050)
        self.assertEqual(semantic["selected_Wrist_subjects"], 12)
        self.assertEqual(semantic["fit_runs"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(semantic["heldout_runs"], [7, 8])
        self.assertFalse(semantic["target_quality_size_checksum_or_outcome_selects_rows"])

    def test_transport_remains_uncoded_bounded_and_no_retry(self) -> None:
        transport = self.decision["transport_contract"]
        self.assertTrue(transport["bounded_cap_plus_one_read"])
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_identity_Content_Encoding_accepted"])
        self.assertTrue(transport["other_Content_Encoding_refused"])
        self.assertEqual(transport["content_decoding_or_decompression_operations"], 0)
        self.assertEqual((transport["retries"], transport["reruns"]), (0, 0))

    def test_output_and_machine_caps_protect_existing_storage(self) -> None:
        output = self.decision["output_contract"]
        resources = self.decision["resource_boundary"]
        self.assertEqual(output["maximum_files"], 3)
        self.assertEqual(output["private_manifest_mode"], "0600")
        self.assertFalse(output["preexisting_path_overwrite_move_delete_or_rename"])
        self.assertEqual(resources["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["incremental_disk_cap_bytes"], 4 * 1024**2)
        self.assertEqual(
            (resources["CPU_threads"], resources["workers"], resources["numerical_jobs"]),
            (1, 1, 1),
        )

    def test_authorized_operations_are_conditional_and_forbidden_stay_false(self) -> None:
        authorization = self.decision["authorization"]
        self.assertTrue(authorization["wrapper_implementation_after_decision_green"])
        self.assertTrue(authorization["one_live_metadata_request_after_wrapper_green"])
        for key, value in authorization.items():
            if key.endswith("_authorized_now"):
                with self.subTest(key=key):
                    self.assertFalse(value)

    def test_decision_only_counters_are_zero(self) -> None:
        counters = self.decision["decision_only_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))
        self.assertFalse(self.decision["end_to_end_latency_measured"])

    def test_document_preserves_same_path_and_scientific_boundary(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "This record preserves those exact 76 UTF-8 bytes.",
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
