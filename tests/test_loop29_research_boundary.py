import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop29_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_29_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "docs" / "POST_20_ROADMAP.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop29ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_research_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(
            boundary["schema_name"], "neurodecodekit.loop29_research_boundary"
        )
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_device_and_acquisition_execution_blocked",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 24)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_storage_envelope_is_exact_bounded_and_not_download_permission(self):
        storage = self.boundary["storage_envelope"]
        self.assertEqual(storage["preferred_incremental_storage_bytes"], 5_000_000_000)
        self.assertEqual(storage["absolute_incremental_storage_bytes"], 10_000_000_000)
        self.assertFalse(storage["storage_permission_is_download_authorization"])
        self.assertEqual(storage["current_loop29_download_budget_bytes"], 0)
        self.assertEqual(storage["current_downloaded_payload_bytes"], 0)
        self.assertEqual(storage["combined_selected_future_bundle_bytes"], 1_106_030_247)
        self.assertEqual(storage["preferred_margin_after_both_bundles_bytes"], 3_893_969_753)
        self.assertEqual(storage["absolute_margin_after_both_bundles_bytes"], 8_893_969_753)
        self.assertTrue(storage["unused_capacity_is_not_a_collection_target"])
        self.assertFalse(storage["full_spanishbcbl_download_allowed"])

    def test_brain2qwerty_sensor_ablation_is_not_portable_modality_evidence(self):
        reference = self.boundary["brain2qwerty_reference_boundary"]
        self.assertEqual(reference["v1_eeg"]["mean_character_error_rate"], 0.65)
        self.assertEqual(reference["v1_eeg"]["meg_mean_character_error_rate"], 0.29)
        self.assertEqual(reference["v2_meg"]["channels_total"], 306)
        self.assertEqual(
            reference["v2_meg"]["random_sensor_ablation_counts"], [76, 153, 230]
        )
        self.assertFalse(reference["v2_meg"]["opm_sentence_decoding_measured"])
        self.assertFalse(
            reference["v2_meg"]["random_cryogenic_sensor_ablation_counts_as_opm_evidence"]
        )
        self.assertFalse(
            reference["v2_meg"]["random_cryogenic_sensor_ablation_counts_as_eeg_evidence"]
        )

    def test_pathway_decision_has_four_noninterchangeable_lanes(self):
        decision = self.boundary["portable_pathway_decision"]
        self.assertEqual(
            decision["immediate_accessibility_lane"],
            "scalp_EEG_local_first_research_and_qualification",
        )
        self.assertEqual(
            decision["same_modality_partner_lane"], "OPM_MEG_partner_lab_translation"
        )
        self.assertEqual(decision["scientific_reference_lane"], "cryogenic_MEGIN_MEG")
        self.assertEqual(decision["non_neural_lane"], "peripheral_and_behavioral_controls_only")
        self.assertIsNone(decision["selected_device_id"])
        self.assertFalse(decision["device_purchase_recommended_now"])
        self.assertFalse(decision["opm_at_home_ready"])
        self.assertFalse(
            decision["scalp_eeg_at_home_open_vocabulary_thought_typing_demonstrated"]
        )

    def test_modality_profiles_keep_units_reference_and_environment_separate(self):
        profiles = {
            row["profile_id"]: row for row in self.boundary["modality_profiles"]
        }
        self.assertEqual(len(profiles), 4)
        cryogenic = profiles["cryogenic_megin_meg_reference"]
        opm = profiles["opm_meg_partner_lab"]
        eeg = profiles["scalp_eeg_local_first"]
        peripheral = profiles["non_neural_wearables_control_only"]
        self.assertFalse(cryogenic["reference_scheme_required"])
        self.assertTrue(opm["active_field_nulling_required"])
        self.assertFalse(opm["at_home_ready"])
        self.assertTrue(eeg["reference_scheme_required"])
        self.assertTrue(eeg["ground_scheme_required"])
        self.assertTrue(eeg["electrode_contact_or_impedance_required"])
        self.assertFalse(peripheral["may_be_called_brain_signal"])

    def test_requirement_matrix_is_complete_and_has_no_equivalence_shortcut(self):
        matrix = self.boundary["requirement_matrix"]
        self.assertEqual(len(matrix), 15)
        ids = [row["requirement_id"] for row in matrix]
        self.assertEqual(len(ids), len(set(ids)))
        for row in matrix:
            for modality in ("cryogenic_meg", "opm_meg", "scalp_eeg", "non_neural"):
                self.assertIn(modality, row)
            self.assertTrue(row["minimum_future_evidence"])
        self.assertIn("electrical_reference_and_ground", ids)
        self.assertIn("shielding_field_control_and_environment", ids)
        self.assertIn("timestamp_clock_and_latency_provenance", ids)
        self.assertIn("local_raw_export_network_and_privacy", ids)

    def test_opm_evidence_stays_speech_tracking_and_specialist_environment_only(self):
        opm = self.boundary["opm_evidence_boundary"]
        self.assertEqual(opm["speech_tracking_study_participants"], 4)
        self.assertEqual(opm["speech_tracking_sensor_count_range"], [45, 46])
        self.assertFalse(opm["speech_tracking_is_sentence_production_decoding"])
        self.assertFalse(opm["speech_tracking_is_brain_to_text"])
        self.assertFalse(opm["real_time_opm_interface_is_text_decoding"])
        self.assertGreater(opm["state_of_art_msr_mass_greater_than_kg"], 9_999)
        self.assertFalse(opm["lightly_shielded_room_is_unshielded_home"])
        self.assertTrue(opm["partner_data_gate_required"])

    def test_eeg_evidence_separates_home_mechanics_from_text_decoding(self):
        eeg = self.boundary["eeg_evidence_boundary"]
        self.assertEqual(eeg["brain2qwerty_v1_task_matched_eeg_cer"], 0.65)
        self.assertEqual(eeg["brain2qwerty_v1_task_matched_meg_cer"], 0.29)
        self.assertFalse(eeg["dewave_is_thought_typing"])
        self.assertEqual(eeg["at_home_repeated_dry_eeg_participants_total"], 80)
        self.assertFalse(eeg["at_home_task_is_language_decoding"])
        self.assertTrue(eeg["dry_eeg_low_frequency_below_6_hz_reliability_warning"])
        self.assertTrue(eeg["motion_and_jaw_artifact_warning"])

    def test_device_specs_are_evidence_records_not_qualifications(self):
        records = {
            row["record_id"]: row
            for row in self.boundary["representative_device_class_evidence"]
        }
        self.assertEqual(len(records), 4)
        self.assertEqual(records["openbci_cyton_official_spec"]["eeg_channels"], 8)
        self.assertEqual(records["openbci_cyton_official_spec"]["sampling_rate_hz"], 250)
        self.assertEqual(
            records["openbci_cyton_daisy_official_spec"][
                "effective_per_channel_sampling_rate_hz"
            ],
            125,
        )
        self.assertTrue(
            records["brainflow_transport_contract"][
                "some_board_timestamps_generated_on_host_receipt"
            ]
        )
        self.assertTrue(
            all(
                "spec" in row["qualification_status"]
                or "documentation" in row["qualification_status"]
                for row in records.values()
            )
        )

    def test_fresh_real_data_path_is_small_exact_and_still_unauthorized(self):
        path = self.boundary["fresh_real_data_path"]
        s20 = path["first_result_candidate"]
        s25 = path["final_transfer_candidate"]
        self.assertEqual(s20["bundle_bytes"], 96_090_264)
        self.assertEqual(s20["files"], 4)
        self.assertFalse(s20["authorized"])
        self.assertFalse(s20["portable_device_result"])
        self.assertEqual(s25["bundle_bytes"], 1_009_939_983)
        self.assertFalse(s25["authorized"])
        self.assertFalse(s25["packet_prepared"])
        self.assertEqual(path["combined_bundle_bytes"], 1_106_030_247)
        self.assertEqual(path["additional_source_blocks_selected_now"], 0)

    def test_device_packet_and_qualification_ladder_are_strict(self):
        gates = self.boundary["future_device_packet_minimum_gates"]
        self.assertEqual(len(gates), 12)
        self.assertTrue(any("network_off" in gate for gate in gates))
        self.assertTrue(any("no_silent_interpolation" in gate for gate in gates))
        self.assertTrue(any("peripheral_controls" in gate for gate in gates))
        levels = self.boundary["qualification_levels"]
        self.assertEqual([row["level"] for row in levels], list(range(6)))
        self.assertFalse(levels[0]["decoding_claim"])
        self.assertFalse(levels[3]["decoding_claim"])
        self.assertEqual(
            levels[5]["decoding_claim"], "only_exact_person_session_task_device_and_split"
        )

    def test_dependencies_keep_execution_blocked_but_feed_later_loops(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop29_planning_research_complete"])
        self.assertFalse(dependencies["loop29_preregistration_prepared"])
        self.assertFalse(dependencies["loop29_authorization_request_prepared"])
        self.assertTrue(dependencies["loop27_metadata_dependency_satisfied"])
        self.assertFalse(dependencies["device_specific_packet_dependency_satisfied"])
        self.assertTrue(dependencies["s20_packet_exists"])
        self.assertFalse(dependencies["s20_packet_authorized"])
        self.assertTrue(dependencies["loop36_geometry_research_can_use_this_matrix"])
        self.assertTrue(dependencies["loop42_device_selection_can_use_this_matrix"])

    def test_resources_and_protected_access_are_zero_or_explicitly_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_workers"], 1)
        self.assertEqual(resources["current_downloaded_payload_bytes"], 0)
        self.assertEqual(resources["current_generated_planning_artifact_cap_bytes"], 8 * 1024**2)
        self.assertIsNone(resources["external_browser_peak_rss_bytes"])
        self.assertIsNone(resources["end_to_end_research_runtime_sec"])
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 14)
        protected = {
            key: value
            for key, value in counters.items()
            if key != "high_level_public_web_research_operations"
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_and_human_note_cover_the_decision_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 18)
        self.assertEqual(len({row["source_id"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        for phrase in (
            "Sensor Count Is Not A Modality",
            "OPM-MEG Preserves Modality, Not Environment",
            "EEG Is Accessible And Scientifically Hard",
            "1,106,030,247",
            "Home recording is not home text decoding",
            "does not establish",
        ):
            self.assertIn(phrase, self.research)

    def test_roadmap_keeps_loop29_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 29)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(
            row["research_registry"], "registries/loop29_research_boundary.v0.json"
        )
        self.assertFalse(row["preregistration_prepared"])
        self.assertEqual(row["selected_accessibility_lane"], "scalp_EEG_local_first")
        self.assertEqual(row["selected_partner_lane"], "OPM_MEG_partner_lab")

    def test_no_loop29_runtime_packet_device_or_payload_exists(self):
        forbidden = (
            "docs/LOOP_29_PORTABLE_SENSING_PREREGISTRATION.md",
            "docs/LOOP_29_AUTHORIZATION_PACKET.md",
            "registries/loop29_portable_sensing_contract.v0.json",
            "registries/loop29_authorization_request.v0.json",
            "selections/loop29_device.json",
            "src/neurodecodekit/devices/portable_sensing.py",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))

    def test_public_status_keeps_research_separate_from_execution(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                lowered = contents.lower()
                self.assertIn("loop 29", lowered)
                self.assertIn("planning research", lowered)
                self.assertIn("not started", lowered)
                self.assertIn("opm", lowered)
                self.assertIn("eeg", lowered)
        combined = "\n".join(self.public_status.values())
        self.assertIn("1,106,030,247", combined)
        self.assertNotIn("Loop 29 is complete", combined)


if __name__ == "__main__":
    unittest.main()
