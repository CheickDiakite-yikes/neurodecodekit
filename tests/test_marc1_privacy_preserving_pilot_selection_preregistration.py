import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "registries"
    / "marc1_privacy_preserving_pilot_selection_contract.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_subjects(seed: str, subject_ids: list[str]) -> list[str]:
    return sorted(
        subject_ids,
        key=lambda subject_id: (
            hashlib.sha256(f"{seed}\0{subject_id}".encode()).hexdigest(),
            subject_id,
        ),
    )


class MARC1PilotSelectionPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_privacy_preserving_pilot_selection_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"],
            "MARC-1-P1-privacy-preserving-pilot-selection-generated-contract-v0",
        )
        self.assertEqual(
            self.contract["status"],
            "generated_fixture_only_contract_frozen_implementation_not_started",
        )

    def test_every_artifact_binding_is_current(self) -> None:
        for binding in self.contract["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_live_inventory_proof_is_exact(self) -> None:
        proof = self.contract["green_inventory_proof"]
        self.assertEqual(
            proof["commit"], "7aee1287d1b5e4c91fde206e5a86cdee30df7ebf"
        )
        self.assertEqual(proof["CI_run_id"], 31_522_799_476)
        self.assertEqual(proof["base_job_id"], 93_883_797_813)
        self.assertEqual(proof["optional_neuro_job_id"], 93_883_797_816)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["live_result_route"], "MARC1CD-R1")
        self.assertTrue(proof["live_result_consumed"])
        self.assertEqual(proof["freewill_inventory_entries"], 1_227)
        self.assertEqual(proof["whole_archive_or_member_payload_bytes"], 0)

    def test_rank_algorithm_replays_both_frozen_cohorts(self) -> None:
        self.assertEqual(self.contract["rank_algorithm"]["selected_count_per_source"], 12)
        for axis_name in ("freewill_axis", "wrist_axis"):
            axis = self.contract[axis_name]
            eligible = (
                axis["eligibility"]["eligible_subject_ids"]
                if axis_name == "freewill_axis"
                else axis["eligible_subject_ids"]
            )
            ranked = rank_subjects(axis["selection_seed"], eligible)
            self.assertEqual(ranked[:12], axis["selected_subject_ids_in_rank_order"])
        self.assertFalse(
            self.contract["rank_algorithm"][
                "size_CRC_signal_event_target_or_outcome_may_affect_rank"
            ]
        )
        self.assertFalse(self.contract["rank_algorithm"]["post_hoc_replacement_allowed"])

    def test_freewill_eligibility_is_published_and_preinspection(self) -> None:
        axis = self.contract["freewill_axis"]
        eligibility = axis["eligibility"]
        self.assertEqual(axis["published_participants"], 23)
        self.assertEqual(axis["published_sessions"], 49)
        self.assertEqual(axis["published_runs"], 238)
        self.assertEqual(axis["published_trials"], 6_808)
        self.assertEqual(eligibility["sampling_rate_hz"], 250)
        self.assertEqual(eligibility["single_session_exclusions"], ["sub-02", "sub-17"])
        self.assertEqual(eligibility["sampling_tier_exclusions"], ["sub-13", "sub-15"])
        self.assertEqual(len(eligibility["eligible_subject_ids"]), 19)
        self.assertTrue(
            all(min(counts) >= 3 for counts in eligibility["published_session_1_2_run_counts"].values())
        )

    def test_freewill_split_and_bundle_counts_are_exact(self) -> None:
        bundle = self.contract["freewill_axis"]["run_bundle"]
        self.assertEqual(bundle["required_suffixes"], [
            "_eeg.eeg",
            "_eeg.vhdr",
            "_eeg.vmrk",
            "_events.tsv",
        ])
        self.assertEqual(bundle["fit_run_bundles"], 36)
        self.assertEqual(bundle["heldout_run_bundles"], 36)
        self.assertEqual(bundle["selected_run_bundles"], 72)
        self.assertEqual(bundle["selected_core_members"], 288)
        self.assertFalse(bundle["sessions_after_ses_02_used"])
        self.assertFalse(bundle["missing_companion_backfill_allowed"])
        self.assertFalse(bundle["member_size_or_CRC_may_change_run_selection"])

    def test_freewill_selection_reads_metadata_rows_only(self) -> None:
        reads = self.contract["freewill_axis"]["selector_reads"]
        self.assertTrue(reads["private_central_directory_manifest"])
        for key, value in reads.items():
            if key != "private_central_directory_manifest":
                self.assertFalse(value, key)

    def test_wrist_cohort_and_run_split_are_exact(self) -> None:
        axis = self.contract["wrist_axis"]
        self.assertEqual(axis["published_participants"], 45)
        self.assertEqual(len(axis["eligible_subject_ids"]), 45)
        self.assertEqual(axis["participant_archive_selection"]["archives"], 12)
        split = axis["later_split"]
        self.assertEqual(split["fit_runs"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(split["heldout_runs"], [7, 8])
        self.assertEqual(split["fit_runs_total"], 72)
        self.assertEqual(split["heldout_runs_total"], 24)
        self.assertEqual(split["expected_fit_trials"], 2_880)
        self.assertEqual(split["expected_heldout_trials"], 960)
        self.assertFalse(split["row_random_split_allowed"])

    def test_target_firewall_excludes_content_and_outcomes(self) -> None:
        firewall = self.contract["target_firewall"]
        self.assertTrue(firewall["selection_stage_is_target_free"])
        self.assertFalse(firewall["selection_stage_has_event_parser"])
        self.assertFalse(firewall["selection_stage_has_neuro_reader"])
        self.assertFalse(firewall["selection_stage_has_archive_extractor"])
        self.assertFalse(firewall["selection_stage_has_model_or_scorer"])
        self.assertIn("signal_quality", firewall["forbidden_selection_inputs"])
        self.assertIn("technical_validation_outcome", firewall["forbidden_selection_inputs"])
        self.assertFalse(firewall["post_target_update_or_rerun_allowed"])

    def test_storage_caps_fit_maintainer_and_prior_research_ceiling(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["future_Freewill_network_payload_bytes"], 6 * 1024**3)
        self.assertEqual(caps["future_Wrist_network_payload_bytes"], 2 * 1024**3)
        self.assertEqual(caps["future_combined_network_payload_bytes"], 8 * 1024**3)
        self.assertEqual(caps["future_incremental_disk_bytes"], 8 * 1024**3)
        self.assertEqual(caps["future_minimum_free_disk_bytes"], 12 * 1024**3)
        self.assertEqual(caps["future_private_derivative_bytes"], 64 * 1024**2)
        self.assertFalse(caps["fallback_cohort_reduction_or_budget_increase_allowed"])

    def test_generated_qualification_matches_real_inventory_scale(self) -> None:
        fixture = self.contract["generated_fixture_contract"]
        self.assertEqual(fixture["Freewill_inventory_rows"], 1_227)
        self.assertEqual(fixture["Wrist_metadata_rows"], 55)
        self.assertEqual(fixture["Freewill_eligible_subjects"], 19)
        self.assertEqual(fixture["Wrist_eligible_subjects"], 45)
        self.assertEqual(fixture["selected_subjects_per_source"], 12)
        self.assertEqual(fixture["selected_Freewill_run_bundles"], 72)
        self.assertEqual(fixture["selected_Freewill_core_members"], 288)
        self.assertEqual(fixture["selected_Wrist_archives"], 12)
        self.assertEqual(fixture["real_path_or_network_operations"], 0)

    def test_privacy_keeps_exact_member_and_file_fields_private(self) -> None:
        privacy = self.contract["privacy_contract"]
        self.assertEqual(privacy["private_output_mode"], "0600")
        self.assertTrue(privacy["public_selected_subject_ids_allowed"])
        self.assertFalse(privacy["public_Freewill_member_names_offsets_or_CRC_allowed"])
        self.assertFalse(privacy["public_Wrist_file_ids_archive_names_or_URLs_allowed"])
        self.assertFalse(privacy["public_local_paths_raw_bodies_or_raw_headers_allowed"])
        self.assertFalse(privacy["inspect_accepts_private_manifest"])
        self.assertFalse(privacy["overwrite_allowed"])

    def test_interface_has_no_real_or_override_surface(self) -> None:
        interface = self.contract["interface"]
        self.assertEqual(interface["generated_commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(interface["execute_command_available"])
        self.assertFalse(interface["real_path_URL_host_or_credential_argument_available"])
        self.assertFalse(interface["participant_seed_size_or_split_override_available"])
        self.assertFalse(interface["archive_open_target_model_or_score_argument_available"])

    def test_mutations_and_router_are_frozen(self) -> None:
        mutations = self.contract["required_mutations"]
        self.assertEqual(len(mutations), 36)
        self.assertEqual(len(set(mutations)), 36)
        self.assertEqual(mutations[0], "contract_or_artifact_hash_mismatch")
        self.assertEqual(mutations[-1], "output_symlink_overwrite_cap_or_replay_mismatch")
        router = self.contract["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 7)
        self.assertEqual(router["success_route"], "MARC1PSG-R1")
        self.assertFalse(router["success_is_scientific_result"])
        self.assertFalse(router["success_authorizes_member_acquisition_or_analysis"])

    def test_all_current_authority_and_access_are_zero(self) -> None:
        self.assertTrue(all(value is False for value in self.contract["authorization_flags"].values()))
        self.assertTrue(all(value == 0 for value in self.contract["access_counters"].values()))

    def test_next_gate_requires_two_green_milestones_and_fresh_decision(self) -> None:
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_requires_this_contract_green"])
        self.assertTrue(gate["generated_closeout_requires_exact_implementation_green"])
        self.assertTrue(gate["real_selection_requires_later_all_false_Tier_C_packet"])
        self.assertTrue(gate["real_selection_requires_fresh_packet_bound_decision"])
        self.assertFalse(gate["member_acquisition_eligible_after_generated_success"])
        self.assertFalse(gate["current_maintainer_message_is_retroactive_real_selection_authority"])

    def test_human_preregistration_preserves_two_claim_sentences(self) -> None:
        document = (
            ROOT / "docs" / "MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_PREREGISTRATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added if successful:", document)
        self.assertIn("Scientific claim not established even if successful:", document)
        self.assertIn("The current maintainer continuation is not retroactive authority", document)


if __name__ == "__main__":
    unittest.main()
