import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc1_multimodal_artifact_resolved_movement_research.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc1MultimodalArtifactResolvedMovementResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_schema_identity_and_tier_a_status(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_multimodal_artifact_resolved_movement_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["research_id"],
            "MARC-1-multimodal-artifact-resolved-causal-movement-research-v0",
        )
        self.assertEqual(
            self.record["status"],
            "tier_A_primary_source_research_complete_no_payload_access",
        )

    def test_local_artifact_bindings_are_current(self):
        for binding in self.record["artifact_bindings"].values():
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_selected_axes_are_complementary_and_licensed(self):
        sources = self.record["source_matrix"]
        freewill = sources["freewill_23"]
        wrist = sources["wrist_45"]
        self.assertEqual(freewill["license"], "CC BY 4.0")
        self.assertTrue(freewill["selected_axis"])
        self.assertTrue(freewill["EOG_available"])
        self.assertTrue(freewill["kinematic_onset_available"])
        self.assertFalse(freewill["EMG_available"])
        self.assertEqual(wrist["license"], "CC BY 4.0")
        self.assertTrue(wrist["selected_axis"])
        self.assertTrue(wrist["EMG_available"])
        self.assertTrue(wrist["kinematic_onset_available"])
        self.assertFalse(wrist["EOG_available"])

    def test_unlicensed_candidate_is_parked(self):
        candidate = self.record["source_matrix"]["self_paced_10"]
        self.assertEqual(candidate["license"], "unavailable")
        self.assertFalse(candidate["selected_axis"])
        self.assertTrue(candidate["execution_parked"])
        self.assertFalse(candidate["payload_access_authorized"])

    def test_public_metadata_identities_are_exact(self):
        freewill = self.record["source_matrix"]["freewill_23"]
        self.assertEqual(freewill["figshare_record_id"], 28_632_599)
        self.assertEqual(freewill["archive_bytes"], 13_591_548_048)
        self.assertEqual(
            freewill["archive_md5"], "3b7c3039c5c9fb6abf1429a830301711"
        )
        wrist = self.record["source_matrix"]["wrist_45"]
        self.assertEqual(wrist["figshare_record_id"], 29_666_735)
        self.assertEqual(wrist["record_bytes"], 3_683_416_050)
        self.assertEqual(wrist["sub_01_bytes"], 33_690_749)
        self.assertEqual(
            wrist["sub_01_md5"], "6b01cf5bd30de0c670d2837d112a17fa"
        )

    def test_monolithic_archive_can_never_be_downloaded_whole(self):
        storage = self.record["storage_policy"]
        self.assertTrue(storage["full_freewill_archive_download_forbidden"])
        self.assertEqual(storage["incremental_payload_disk_cap_bytes"], 8 << 30)
        self.assertEqual(storage["incremental_network_payload_cap_bytes"], 8 << 30)
        self.assertEqual(storage["required_free_disk_bytes"], 12 << 30)
        self.assertLess(
            storage["incremental_payload_disk_cap_bytes"],
            self.record["source_matrix"]["freewill_23"]["archive_bytes"],
        )

    def test_candidate_is_small_causal_and_nonlinguistic(self):
        candidate = self.record["common_candidate"]
        self.assertEqual(candidate["frequency_band_hz"], [0.5, 4.0])
        self.assertTrue(candidate["causal"])
        self.assertTrue(candidate["right_endpoint_exclusive"])
        self.assertEqual(candidate["model_family"], "shrinkage_LDA")
        self.assertFalse(candidate["pretrained_model_allowed"])
        self.assertFalse(candidate["language_model_allowed"])
        self.assertFalse(candidate["target_or_control_stream_as_feature_allowed"])

    def test_target_firewall_requires_green_freeze(self):
        firewall = self.record["target_firewall"]
        self.assertEqual(
            firewall["physical_roles"],
            ["fit_rows", "target_blind_prediction_rows", "isolated_scorer_rows"],
        )
        self.assertTrue(firewall["whole_run_session_participant_splits_required"])
        self.assertFalse(firewall["window_random_split_allowed"])
        self.assertTrue(firewall["remote_green_prediction_freeze_required"])
        self.assertEqual(firewall["held_out_target_deliveries_after_freeze"], 1)
        self.assertEqual(firewall["post_target_updates"], 0)

    def test_comparator_matrix_covers_every_live_confound(self):
        roles = set(self.record["mandatory_comparators"])
        self.assertEqual(
            roles,
            {
                "no_signal_prevalence",
                "elapsed_time_or_trial_phase",
                "EOG_only_where_available",
                "pre_onset_EMG_only_where_available",
                "pre_onset_kinematic_only_where_available",
                "frontal_EEG_proxy_where_available",
                "occipital_EEG_proxy_where_available",
                "central_EEG_candidate",
                "EEG_residualized_against_train_only_EOG_where_available",
                "onset_shift",
                "label_derangement",
                "future_context_sentinel",
            },
        )

    def test_top_route_requires_both_axes_and_weaker_margin(self):
        conjunction = self.record["two_axis_conjunction"]
        self.assertTrue(conjunction["freewill_axis_required"])
        self.assertTrue(conjunction["wrist_axis_required"])
        self.assertEqual(conjunction["primary_effect"], "weaker_axis_margin")
        self.assertFalse(conjunction["pooled_trial_metric_is_primary"])
        self.assertEqual(
            self.record["prospective_router"]["top_route"], "MARC1-R4"
        )

    def test_current_authority_and_access_are_all_zero(self):
        for value in self.record["authorization_flags"].values():
            self.assertFalse(value)
        for value in self.record["access_counters"].values():
            self.assertEqual(value, 0)

    def test_claim_boundary_remains_sensor_level(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("two-axis", boundary["engineering_capability_added"])
        self.assertIn("no new neural", boundary["scientific_claim_not_established"])
        ceiling = boundary["future_top_route_ceiling"]
        self.assertIn("scalp-EEG sensor information", ceiling)
        for forbidden in ("thought", "typing", "clinical"):
            self.assertIn(forbidden, boundary["forbidden_claims"])


if __name__ == "__main__":
    unittest.main()
