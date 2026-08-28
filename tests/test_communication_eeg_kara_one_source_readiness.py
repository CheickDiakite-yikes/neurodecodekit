from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/communication_eeg_kara_one_source_readiness.v0.json"
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_KARA_ONE_SOURCE_READINESS_2026_08_27.md"
DATASETS = ROOT / "registries/datasets.v0.json"
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"
CONTRACT = ROOT / "registries/communication_eeg_independent_replication_contract.v0.json"


class CommunicationEEGKaraOneSourceReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_public_surface_and_participant_discrepancy(self) -> None:
        surface = self.record["verified_public_surface"]
        self.assertEqual(surface["listed_participant_archives"], 14)
        self.assertEqual(surface["reported_total_bytes_decimal"], 24_000_000_000)
        self.assertEqual(surface["reported_EEG_cap_channels"], 64)
        self.assertEqual(surface["reported_ocular_electrodes"], 4)
        self.assertEqual(surface["reported_sampling_rate_hz"], 1_000)
        self.assertEqual(surface["reported_paper_recruited_participants"], 12)
        self.assertEqual(surface["reported_paper_analyzed_participants"], 8)
        self.assertFalse(surface["release_and_paper_participant_counts_agree"])
        self.assertFalse(surface["CNT_channel_named_EMG_is_oral_EMG"])

    def test_frozen_contract_forbids_over_cap_participant_subsetting(self) -> None:
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        router = contract["source_routes"]["deterministic_router"]
        requirements = self.record["frozen_route_requirements"]
        self.assertEqual(requirements["selected_raw_cap_bytes"], 10 * 1024**3)
        self.assertEqual(requirements["participant_rule"], router["participant_rule"])
        self.assertEqual(
            requirements["over_cap_or_unsplittable_action"],
            router["over_cap_or_unsplittable_action"],
        )
        self.assertFalse(requirements["participant_dropping_allowed"])

    def test_source_lock_is_strictly_unqualified(self) -> None:
        source_lock = self.record["operational_source_lock"]
        self.assertTrue(source_lock["reachable_dataset_page"])
        self.assertTrue(source_lock["recorded_EOG_verified"])
        self.assertTrue(source_lock["recorded_face_tracking_verified"])
        self.assertFalse(source_lock["immutable_dataset_revision_verified"])
        self.assertFalse(source_lock["per_archive_bytes_verified"])
        self.assertFalse(source_lock["per_archive_hashes_verified"])
        self.assertFalse(source_lock["member_level_selective_transfer_verified"])
        self.assertFalse(source_lock["exact_target_free_eligible_participant_set_verified"])
        self.assertFalse(source_lock["all_public_participant_archives_within_cap"])
        self.assertFalse(source_lock["acquisition_ready"])

    def test_router_parks_all_public_partial_replication(self) -> None:
        decision = self.record["router_decision"]
        self.assertTrue(decision["parked_under_frozen_contract"])
        self.assertFalse(decision["operationally_qualified_now"])
        self.assertFalse(decision["may_be_rescued_by_participant_subsetting"])
        self.assertEqual(len(decision["park_reasons"]), 5)

        outcome = self.record["public_replication_router_outcome"]
        self.assertFalse(outcome["TESSCCo_partial_route_qualified"])
        self.assertFalse(outcome["Kara_One_partial_route_qualified"])
        self.assertEqual(outcome["qualified_public_partial_routes"], [])
        self.assertTrue(outcome["public_replication_parked"])
        self.assertTrue(
            outcome[
                "prospective_synchronized_EEG_EOG_bilateral_oral_EMG_fallback_preserved"
            ]
        )

    def test_measured_research_made_no_archive_or_protected_operation(self) -> None:
        measured = self.record["measured_public_research"]
        self.assertEqual(measured["dataset_page_retrievals"], 1)
        self.assertEqual(measured["associated_paper_retrievals"], 1)
        self.assertEqual(measured["participant_archive_requests"], 0)
        self.assertEqual(measured["dataset_payload_requests"], 0)
        self.assertEqual(measured["dataset_payload_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )

    def test_dataset_and_frontier_registries_match_parked_boundary(self) -> None:
        datasets = json.loads(DATASETS.read_text(encoding="utf-8"))["records"]
        row = next(item for item in datasets if item["id"] == "kara_one")
        self.assertFalse(row["storage"]["registered_route"]["acquisition_ready"])
        self.assertTrue(row["storage"]["registered_route"]["parked_under_10_GiB_cap"])
        self.assertEqual(row["proof_posture"], "public_partial_route_parked_by_frozen_source_lock")

        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        refresh = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["triangulated_replication_refresh"]
        kara = refresh["Kara_One_source_readiness"]
        self.assertTrue(kara["parked_under_frozen_contract"])
        self.assertFalse(kara["acquisition_ready"])
        self.assertTrue(refresh["public_replication_parked"])

    def test_document_states_capability_nonclaim_and_gate(self) -> None:
        boundary = self.record["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", " ".join(document.split()))


if __name__ == "__main__":
    unittest.main()
