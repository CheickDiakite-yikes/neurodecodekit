from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/ofner_2017_motor_imagery_source_reselection.v0.json"
DOCUMENT = ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_SOURCE_RESELECTION_2026_08_29.md"
FRONTIER = ROOT / "registries/current_research_frontier.v2.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v1.json"


class Ofner2017MotorImagerySourceReselectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_source_identity_is_immutable_and_licensed(self) -> None:
        source = self.record["source_identity"]
        self.assertEqual(source["NEMAR_dataset"], "nm000173")
        self.assertEqual(source["NEMAR_version"], "v1.0.3")
        self.assertEqual(
            source["NEMAR_git_tag_object"],
            "4e1329ceb93e0cc5e81d0d2d5d1839527299b251",
        )
        self.assertEqual(source["license"], "CC-BY-4.0")
        self.assertEqual(source["raw_manifest_first_observed_bytes"], 1_352_270)
        self.assertEqual(len(set(source["raw_manifest_sha256_observations"])), 2)
        self.assertFalse(source["raw_manifest_hash_stable"])
        self.assertEqual(source["canonical_manifest_bytes"], 748_162)
        self.assertEqual(
            source["canonical_manifest_sha256"],
            "5e889976bf5f5c91970d35c968f5a7ee4b1075aeca0ede984414d4666845aa34",
        )
        self.assertEqual(source["canonical_manifest_matching_replays"], 2)

    def test_exact_original_gdf_surface_fits_allowance(self) -> None:
        surface = self.record["selected_surface"]
        storage = self.record["storage_envelope"]
        self.assertEqual(surface["participants"], 15)
        self.assertEqual(surface["runs_per_participant"], 10)
        self.assertEqual(surface["files"], 150)
        self.assertEqual(surface["payload_bytes"], 13_748_417_608)
        self.assertEqual(surface["unique_checksums"], 150)
        self.assertEqual(surface["missing_stable_bytes_urls"], 0)
        self.assertEqual(
            storage["remaining_headroom_bytes"],
            storage["maintainer_allowance_bytes"] - surface["payload_bytes"],
        )
        self.assertTrue(storage["selected_payload_within_allowance"])
        self.assertEqual(storage["payload_bytes_downloaded_now"], 0)

    def test_required_nuisance_measurements_and_limit_are_explicit(self) -> None:
        measurement = self.record["reported_measurement_contract"]
        self.assertEqual(measurement["EEG_channels"], 61)
        self.assertEqual(measurement["EOG_channels"], 3)
        self.assertEqual(measurement["data_glove_channels"], 19)
        self.assertEqual(measurement["exoskeleton_or_arm_channels"], 13)
        self.assertEqual(measurement["total_channels"], 96)
        self.assertEqual(measurement["sampling_rate_hz"], 512)
        self.assertEqual(measurement["recorded_EMG_channels"], 0)
        self.assertFalse(measurement["measurement_contract_verified_from_signal_header"])

    def test_smaller_derivative_is_rejected_for_missing_controls(self) -> None:
        derivative = self.record["rejected_derivative"]
        self.assertEqual(derivative["BDF_files"], 150)
        self.assertEqual(derivative["total_bytes"], 4_578_904_696)
        self.assertEqual(derivative["public_channel_sidecar_EEG_channels"], 61)
        self.assertEqual(derivative["public_channel_sidecar_EOG_channels"], 0)
        self.assertEqual(derivative["public_channel_sidecar_movement_channels"], 0)
        self.assertFalse(derivative["acceptable_for_frozen_nuisance_question"])

    def test_target_firewall_and_claim_ceiling_are_strict(self) -> None:
        requirements = self.record["confirmation_requirements"]
        self.assertEqual(requirements["outer_split"], "leave_one_participant_out_all_15_people")
        self.assertEqual(requirements["held_out_person_calibration"], "zero")
        self.assertTrue(requirements["prediction_freeze_before_target_delivery"])
        self.assertTrue(requirements["single_frozen_score"])
        self.assertFalse(requirements["target_derived_exclusions"])
        self.assertFalse(requirements["post_target_tuning_or_rerun"])
        boundary = self.record["claim_boundary"]
        self.assertTrue(boundary["source_selected"])
        self.assertFalse(boundary["real_Ofner_EEG_accessed"])
        for key, value in boundary.items():
            if key not in {
                "source_selected",
                "license_qualified",
                "manifest_identity_qualified",
                "storage_feasible_under_20_GiB",
            }:
                self.assertFalse(value, key)

    def test_no_irreversible_operation_or_authority_occurred(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        authority = self.record["authority"]
        self.assertIsNone(authority["active_Tier_C_packet"])
        self.assertTrue(authority["all_irreversible_authority_flags_false"])
        for key, value in authority.items():
            if key not in {"tier", "active_Tier_C_packet", "all_irreversible_authority_flags_false"}:
                self.assertFalse(value, key)

    def test_frontier_is_compact_additive_successor(self) -> None:
        frontier = self.frontier
        self.assertEqual(frontier["schema_version"], "0.3.0")
        self.assertEqual(frontier["active_lane_id"], "NO_ACTIVE_TIER_C_GATE")
        self.assertEqual(frontier["scientific_strategy"]["flagship_experiment"], "EXP-OFNER-C6R-1")
        self.assertEqual(frontier["source_reselection"]["payload_bytes"], 13_748_417_608)
        self.assertFalse(frontier["source_reselection"]["acquisition_authorized"])
        self.assertTrue(frontier["parked_predecessor"]["registered_invocation_consumed"])
        predecessor_bytes = PREDECESSOR.read_bytes()
        self.assertEqual(
            hashlib.sha256(predecessor_bytes).hexdigest(),
            frontier["superseded_registry_sha256"],
        )
        self.assertLess(FRONTIER.stat().st_size, PREDECESSOR.stat().st_size)

    def test_document_has_capability_and_nonclaim_sentences(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no recorded EMG", document)
        self.assertIn("No Tier C packet is active", document)


if __name__ == "__main__":
    unittest.main()
