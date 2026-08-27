from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/communication_eeg_replication_source_refresh.v0.json"
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_REPLICATION_SOURCE_REFRESH_2026_08_27.md"
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"


class CommunicationEEGReplicationSourceRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_schema_and_active_gate_are_preserved(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_replication_source_refresh",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        decision = self.record["decision"]
        self.assertFalse(decision["full_peripheral_adjusted_independent_source_verified"])
        self.assertFalse(decision["real_data_packet_created"])
        self.assertFalse(decision["active_Tier_C_packet_changed"])
        self.assertEqual(decision["sole_active_Tier_C_packet"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], "DREYER-C5R-1-HL")

    def test_frontier_records_green_closeout_and_refresh(self) -> None:
        parallel = self.frontier["parallel_tier_A_communication_program"]
        proof = parallel["source_identity_preregistration"][
            "generated_qualification_proof_closeout"
        ]
        self.assertEqual(
            proof["proof_commit"],
            "4acd82bcc460f3e7a7668ec3c1c6a49c8d964aca",
        )
        self.assertEqual(proof["proof_CI_run_id"], 33_039_371_687)
        self.assertTrue(proof["both_required_jobs_green"])
        refresh = parallel["source_identity_preregistration"][
            "replication_source_refresh"
        ]
        self.assertFalse(refresh["full_peripheral_adjusted_independent_source_verified"])
        self.assertFalse(refresh["watchlist_source_operationally_qualified"])
        self.assertFalse(refresh["real_data_packet_created"])
        self.assertFalse(refresh["active_Tier_C_gate_changed"])
        self.assertEqual(refresh["payload_or_private_operations"], 0)

    def test_discovery_is_not_mislabeled_as_replication(self) -> None:
        discovery = self.record["discovery_source_preserved"]
        self.assertEqual(discovery["source_id"], "OpenNeuro_ds003626_v2.1.2")
        self.assertEqual(discovery["role"], "future_discovery_not_independent_replication")
        self.assertEqual(discovery["reported_EOG_channels"], 4)
        self.assertEqual(discovery["reported_oral_EMG_channels"], 2)
        self.assertFalse(discovery["payload_or_metadata_operation_authorized_by_this_record"])

    def test_silent_speech_public_surface_remains_unqualified(self) -> None:
        silent = self.record["candidate_findings"][0]
        self.assertEqual(silent["source_id"], "SilentSpeech_EEG_2026")
        self.assertEqual(silent["README_reported_public_participants"], 10)
        self.assertTrue(silent["repository_availability_statement_says_dataset_not_in_submission"])
        self.assertTrue(silent["open_missing_loader_issue_observed"])
        for key in (
            "exact_public_EOG_oral_EMG_reference_trigger_roles_verified",
            "stable_public_dataset_DOI_or_revision_verified",
            "complete_public_payload_manifest_and_hashes_verified",
            "dataset_license_verified",
            "reproducible_public_loader_verified",
            "full_peripheral_adjusted_replication_ready",
            "acquisition_authorized",
        ):
            self.assertFalse(silent[key], key)

    def test_every_candidate_is_explicitly_not_ready_or_authorized(self) -> None:
        candidates = self.record["candidate_findings"]
        self.assertEqual(
            [row["source_id"] for row in candidates],
            [
                "SilentSpeech_EEG_2026",
                "Kara_One",
                "Directional_Word_2026",
                "ArEEG_OpenNeuro_ds005262_v1.0.1",
            ],
        )
        self.assertTrue(
            all(not row["full_peripheral_adjusted_replication_ready"] for row in candidates)
        )
        self.assertTrue(all(not row["acquisition_authorized"] for row in candidates))

    def test_promotion_gate_requires_complete_peripheral_controls(self) -> None:
        gate = self.record["promotion_gate"]
        required = {key: value for key, value in gate.items() if key != "failure_action"}
        self.assertTrue(all(required.values()))
        self.assertIn("no_substitution", gate["failure_action"])
        self.assertIn("raw simultaneous EEG, EOG, and oral EMG", self.document)
        self.assertIn("processed-only EEG", self.document)

    def test_storage_and_operations_remain_zero(self) -> None:
        resources = self.record["resource_policy"]
        self.assertEqual(resources["maximum_total_incremental_research_storage_bytes"], 20 << 30)
        self.assertEqual(resources["maximum_selected_raw_bytes"], 10 << 30)
        self.assertEqual(resources["incremental_payload_bytes_this_record"], 0)
        self.assertFalse(resources["cleanup_or_deletion"])
        self.assertFalse(resources["write_outside_NeuroDecodeKit"])
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_claim_boundary_stays_false(self) -> None:
        claims = self.record["claim_boundary"]
        self.assertEqual(
            claims["engineering_capability_added"],
            "machine_tested_replication_source_acceptance_gate",
        )
        for key, value in claims.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)
        self.assertIn("Scientific claim not established", self.document)

    def test_primary_sources_are_public_and_explicit(self) -> None:
        sources = self.record["primary_sources"]
        self.assertEqual(len(sources), 8)
        self.assertTrue(all(url.startswith("https://") for url in sources.values()))


if __name__ == "__main__":
    unittest.main()
