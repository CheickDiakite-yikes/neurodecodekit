from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT / "registries/communication_eeg_triangulated_replication_refresh.v0.json"
)
DOCUMENT = (
    ROOT / "docs/COMMUNICATION_EEG_TRIANGULATED_REPLICATION_REFRESH_2026_08_27.md"
)
FRONTIER = ROOT / "registries/current_research_frontier.v0.json"
PARENT = ROOT / "registries/communication_eeg_independent_replication_contract.v0.json"


class CommunicationEEGTriangulatedReplicationRefreshTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.document = DOCUMENT.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        cls.parent = json.loads(PARENT.read_text(encoding="utf-8"))

    def test_schema_and_active_gate_are_preserved(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.communication_eeg_triangulated_replication_refresh",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        gate = self.record["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertTrue(gate["all_authority_flags_remain_false"])
        self.assertFalse(gate["authority_changed"])

    def test_parent_preregistration_is_not_rewritten(self) -> None:
        parent = self.record["frozen_parent_contract"]
        self.assertEqual(parent["registration_id"], self.parent["registration_id"])
        self.assertFalse(parent["modified_by_this_refresh"])
        self.assertEqual(parent["minimum_full_control_participants"], 10)
        self.assertEqual(parent["minimum_partial_participants"], 12)
        self.assertEqual(
            parent["exact_one_sided_participant_sign_flip_p_maximum"],
            0.05,
        )

    def test_three_evidence_keys_are_noninterchangeable(self) -> None:
        keys = {row["key_id"]: row for row in self.record["evidence_keys"]}
        self.assertEqual(
            list(keys),
            [
                "K1_ATTRIBUTION_DISCOVERY",
                "M_FULL_SENSOR_MECHANISTIC_BRIDGE",
                "K2_INDEPENDENT_PARTIAL_TRANSPORTABILITY",
            ],
        )
        self.assertFalse(keys["K1_ATTRIBUTION_DISCOVERY"]["independent_replication"])
        self.assertFalse(
            keys["M_FULL_SENSOR_MECHANISTIC_BRIDGE"][
                "registered_p_threshold_attainable"
            ]
        )
        self.assertFalse(
            keys["K2_INDEPENDENT_PARTIAL_TRANSPORTABILITY"][
                "full_peripheral_adjusted_claim_allowed"
            ]
        )

    def test_ds007591_small_n_ceiling_is_exact(self) -> None:
        bridge = self.record["evidence_keys"][1]
        self.assertEqual(bridge["source_id"], "OpenNeuro_ds007591_v1.0.1")
        self.assertEqual(bridge["reported_participants"], 3)
        self.assertEqual(bridge["sign_flip_assignment_count"], 2**3)
        self.assertEqual(bridge["minimum_attainable_exact_one_sided_p"], 1 / 8)
        self.assertFalse(bridge["full_control_minimum_participants_met"])
        self.assertIn("descriptive", bridge["maximum_evidence_role"])
        self.assertIn("1/8 = 0.125", self.document)

    def test_new_public_sources_stay_outside_acquisition_authority(self) -> None:
        for row in self.record["evidence_keys"]:
            self.assertFalse(row["acquisition_authorized"], row["source_id"])
        for row in self.record["additional_source_findings"]:
            self.assertFalse(row["acquisition_authorized"], row["source_id"])
        large = self.record["additional_source_findings"][0]
        self.assertEqual(large["source_id"], "OpenNeuro_ds007808_v1.0.0")
        self.assertTrue(large["selected_raw_cap_exceeded"])
        self.assertFalse(large["full_control_minimum_participants_met"])

    def test_router_cannot_compose_missing_evidence_into_full_replication(self) -> None:
        router = self.record["triangulated_router"]
        self.assertEqual(
            router["mandatory_keys"],
            ["K1_ATTRIBUTION_DISCOVERY", "K2_INDEPENDENT_PARTIAL_TRANSPORTABILITY"],
        )
        self.assertTrue(router["both_mandatory_keys_required_for_narrow_triangulated_statement"])
        self.assertTrue(router["mechanistic_bridge_is_nonrouting"])
        self.assertFalse(router["keys_may_rescue_each_other"])
        self.assertFalse(router["M_bridge_inferential_replication_claim_allowed"])
        self.assertFalse(router["K2_full_peripheral_attribution_claim_allowed"])
        self.assertTrue(
            router[
                "independently_replicated_full_peripheral_attribution_requires_future_complete_N_at_least_10_source"
            ]
        )

    def test_frontier_exposes_additive_refresh_without_gate_change(self) -> None:
        refresh = self.frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["triangulated_replication_refresh"]
        self.assertEqual(refresh["refresh_id"], self.record["refresh_id"])
        self.assertEqual(refresh["mechanistic_bridge"], "OpenNeuro_ds007591_v1.0.1")
        self.assertEqual(refresh["independent_partial_replication"], "TESSCCo_2026")
        self.assertFalse(refresh["real_data_packet_created"])
        self.assertEqual(refresh["payload_or_private_operations"], 0)
        self.assertFalse(refresh["active_Tier_C_gate_changed"])

    def test_resources_operations_and_claims_remain_closed(self) -> None:
        resources = self.record["resource_policy"]
        self.assertEqual(resources["maximum_total_incremental_research_storage_bytes"], 20 << 30)
        self.assertEqual(resources["maximum_communication_selected_raw_bytes"], 10 << 30)
        self.assertEqual(resources["incremental_payload_bytes_this_record"], 0)
        self.assertFalse(resources["write_outside_NeuroDecodeKit"])
        self.assertFalse(resources["cleanup_or_deletion"])
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        claims = self.record["claim_boundary"]
        self.assertEqual(
            claims["engineering_capability_added"],
            "machine_tested_three_key_replication_router_with_exact_small_N_inference_ceiling",
        )
        for key, value in claims.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)
        self.assertIn("Scientific claim not established", self.document)

    def test_primary_sources_are_explicit(self) -> None:
        sources = self.record["primary_sources"]
        self.assertEqual(len(sources), 10)
        self.assertTrue(all(url.startswith("https://") for url in sources.values()))


if __name__ == "__main__":
    unittest.main()
