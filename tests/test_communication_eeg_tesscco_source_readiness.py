from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/communication_eeg_tesscco_source_readiness.v0.json"
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_TESSCCO_SOURCE_READINESS_2026_08_27.md"
DATASETS = ROOT / "registries/datasets.v0.json"
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


class CommunicationEEGTESSCCoSourceReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_public_identity_and_observed_unavailability(self) -> None:
        identity = self.record["verified_public_identity"]
        self.assertEqual(identity["article_DOI"], "10.1038/s41597-026-07745-8")
        self.assertEqual(identity["PubMed_id"], 42_387_018)
        self.assertEqual(identity["dataset_DOI"], "10.34740/KAGGLE/DS/9993149")
        self.assertEqual(identity["dataset_DOI_resolution_status"], 302)
        self.assertEqual(identity["dataset_landing_status"], 404)
        self.assertEqual(identity["reported_total_participants"], 24)
        self.assertEqual(identity["reported_available_epochs"], 7_936)
        self.assertEqual(identity["reported_EEG_channels"], 32)
        self.assertEqual(identity["reported_sampling_rate_hz"], 256)

    def test_source_lock_remains_strictly_unqualified(self) -> None:
        source_lock = self.record["operational_source_lock"]
        self.assertFalse(source_lock["reachable_dataset_landing"])
        self.assertFalse(source_lock["immutable_dataset_version_verified"])
        self.assertFalse(source_lock["complete_manifest_verified"])
        self.assertFalse(source_lock["dataset_license_verified"])
        self.assertFalse(source_lock["separate_EOG_verified"])
        self.assertFalse(source_lock["separate_oral_EMG_verified"])
        self.assertFalse(source_lock["acquisition_ready"])

    def test_article_license_is_not_imputed_to_dataset(self) -> None:
        license_boundary = self.record["license_boundary"]
        self.assertEqual(license_boundary["article_license"], "CC_BY_NC_ND_4.0")
        self.assertFalse(license_boundary["article_license_may_be_imputed_to_dataset"])
        self.assertIsNone(license_boundary["dataset_license"])

    def test_router_role_is_preserved_without_rescue_or_substitution(self) -> None:
        router = self.record["router_decision"]
        self.assertEqual(
            router["role"],
            "planned_independent_partial_prompted_command_transportability_key",
        )
        self.assertFalse(router["operationally_qualified_now"])
        self.assertFalse(router["full_peripheral_attribution_allowed"])
        self.assertFalse(router["may_be_substituted_after_discovery_result"])
        self.assertFalse(router["mechanistic_bridge_may_rescue_source_failure"])
        self.assertFalse(router["discovery_key_may_rescue_source_failure"])

    def test_measured_research_used_no_dataset_metadata_or_payload(self) -> None:
        measured = self.record["measured_public_research"]
        self.assertEqual(measured["article_page_GET_requests"], 1)
        self.assertEqual(measured["article_page_response_bytes"], 228_070)
        self.assertTrue(measured["advertised_PDF_endpoint_returned_HTML"])
        self.assertEqual(measured["DOI_resolution_invocations"], 1)
        self.assertEqual(measured["headers_only_HTTP_responses"], 2)
        self.assertEqual(measured["dataset_metadata_API_requests"], 0)
        self.assertEqual(measured["dataset_payload_requests"], 0)
        self.assertEqual(measured["dataset_payload_bytes"], 0)

    def test_all_protected_operation_counters_remain_zero(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )
        gate = self.record["active_gate_preserved"]
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_remain_false"])
        self.assertFalse(gate["authority_changed"])

    def test_dataset_and_frontier_registries_match_readiness_boundary(self) -> None:
        datasets = json.loads(DATASETS.read_text(encoding="utf-8"))["records"]
        row = next(item for item in datasets if item["id"] == "tesscco_2026")
        self.assertEqual(row["source_urls"][1]["url"], "https://doi.org/10.34740/KAGGLE/DS/9993149")
        self.assertFalse(row["storage"]["smallest_meaningful_slice"]["acquisition_ready"])
        self.assertEqual(row["proof_posture"], "planned_partial_replication_source_blocked_at_source_identity")

        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        refresh = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["triangulated_replication_refresh"]
        readiness = refresh["TESSCCo_source_readiness"]
        self.assertFalse(readiness["operationally_qualified"])
        self.assertFalse(readiness["acquisition_ready"])
        self.assertEqual(readiness["observed_dataset_landing_status"], 404)

    def test_document_states_capability_nonclaim_and_gate(self) -> None:
        boundary = self.record["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
