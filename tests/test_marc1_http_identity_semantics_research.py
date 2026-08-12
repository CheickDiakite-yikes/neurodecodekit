from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc1_http_identity_semantics_recovery_research.v0.json"
)
DOCUMENT_PATH = ROOT / "docs" / "MARC_1_HTTP_IDENTITY_SEMANTICS_RECOVERY_RESEARCH.md"
RESULT_PATH = (
    ROOT / "registries" / "marc1_privacy_preserving_pilot_selection_live_result.v0.json"
)


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


class MARC1HTTPIdentitySemanticsResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_identity_and_artifact_only_status_are_exact(self) -> None:
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_http_identity_semantics_recovery_research",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(
            self.registry["status"],
            "artifact_only_research_complete_no_implementation_or_real_access_authorized",
        )
        self.assertIn("not_a_pivot", self.registry["same_path_statement"])

    def test_green_consumed_result_anchor_is_exact(self) -> None:
        anchor = self.registry["green_consumed_result_anchor"]
        self.assertEqual(
            anchor["commit"],
            "8d9cae1f1b5e43e0871ccfb63b4ea3afd1e09eaa",
        )
        self.assertEqual(anchor["CI_run_id"], 31579626846)
        self.assertEqual(anchor["base_python_job_id"], 94059509924)
        self.assertEqual(anchor["optional_neuro_job_id"], 94059509836)
        self.assertTrue(anchor["both_required_jobs_green"])
        self.assertTrue(anchor["result_consumed"])
        self.assertFalse(anchor["retry_or_rerun_available"])
        self.assertEqual(anchor["result_route"], "MARC1PS-F03")
        self.assertEqual(
            hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest(),
            anchor["result_SHA256"],
        )

    def test_observed_evidence_does_not_infer_unretained_header(self) -> None:
        evidence = self.registry["observed_evidence"]
        self.assertEqual(evidence["private_Freewill_manifest_reads"], 1)
        self.assertEqual(evidence["public_Wrist_metadata_requests"], 1)
        self.assertEqual(evidence["public_Wrist_response_opens"], 1)
        self.assertEqual(evidence["public_Wrist_body_reads"], 0)
        self.assertEqual(evidence["public_Wrist_body_bytes"], 0)
        self.assertFalse(evidence["raw_terminal_content_encoding_value_retained"])
        self.assertFalse(evidence["actual_live_header_value_inferred"])

    def test_primary_sources_are_only_official_rfc_sections(self) -> None:
        sources = self.registry["primary_sources"]
        self.assertEqual(len(sources), 2)
        self.assertEqual(
            {source["URL"] for source in sources},
            {
                "https://www.rfc-editor.org/rfc/rfc9110.html#section-8.4",
                "https://www.rfc-editor.org/rfc/rfc9110.html#section-12.5.3",
            },
        )
        self.assertTrue(all(source["publisher"] == "RFC Editor" for source in sources))

    def test_candidate_policy_accepts_only_two_uncoded_forms(self) -> None:
        policy = self.registry["candidate_transport_policy"]
        encoding = policy["terminal_Content_Encoding"]
        self.assertEqual(
            encoding,
            {
                "header_absent": "accept_as_no_content_coding",
                "single_identity_token_case_insensitive": (
                    "accept_as_narrow_compatibility_tolerance"
                ),
                "all_other_present_values": "refuse",
            },
        )
        self.assertEqual(policy["request_Accept_Encoding"], "identity")
        self.assertEqual(policy["Transfer_Encoding"], "refuse_if_present")
        self.assertEqual(policy["decompression_or_decoding_operations"], 0)

    def test_candidate_policy_hash_is_canonical(self) -> None:
        self.assertEqual(
            _canonical_sha256(self.registry["candidate_transport_policy"]),
            self.registry["candidate_transport_policy_SHA256"],
        )

    def test_future_cases_cover_success_and_strict_refusal(self) -> None:
        accepted = self.registry["future_generated_acceptance_cases"]
        refused = self.registry["future_generated_refusal_cases"]
        self.assertEqual(len(accepted), 4)
        self.assertEqual(len(refused), 20)
        self.assertIn("Content_Encoding_absent", accepted)
        self.assertIn("Content_Encoding_identity_plus_gzip", refused)
        self.assertIn("duplicate_Content_Encoding", refused)
        self.assertIn("Transfer_Encoding_present", refused)
        self.assertIn("second_invocation", refused)

    def test_all_current_authorization_flags_are_false(self) -> None:
        flags = self.registry["authorization_flags"]
        self.assertEqual(len(flags), 17)
        self.assertTrue(all(value is False for value in flags.values()))

    def test_research_counters_show_no_real_or_scientific_operation(self) -> None:
        counters = self.registry["research_access_counters"]
        self.assertEqual(counters["committed_public_result_reads"], 1)
        self.assertEqual(counters["primary_source_page_reads"], 2)
        forbidden = set(counters) - {
            "committed_public_result_reads",
            "primary_source_page_reads",
        }
        self.assertTrue(all(counters[key] == 0 for key in forbidden))

    def test_document_preserves_same_path_and_claim_boundary(self) -> None:
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for value in (
            "MARC1-P1A",
            "MARC1PS-F03",
            "same-path",
            "not a new scientific direction",
            "must not be inferred",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            self.assertIn(value, document)


if __name__ == "__main__":
    unittest.main()
