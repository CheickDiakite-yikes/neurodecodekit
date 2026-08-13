import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "marc2_freewill_prefix_selection_contract.v0.json"


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


class Marc2FreewillPrefixSelectionPreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc2_freewill_prefix_selection_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"],
            "MARC-2-FW1-freewill-prefix-selection-generated-contract-v0",
        )
        self.assertEqual(
            self.contract["status"],
            "generated_fixture_only_contract_frozen_implementation_not_started",
        )

    def test_artifact_bindings_are_current(self) -> None:
        for binding in self.contract["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_research_anchor_is_exact(self) -> None:
        proof = self.contract["green_research_proof"]
        self.assertEqual(
            proof["commit"], "ae4d43aabbbe058658c1d77057431f7de331c958"
        )
        self.assertEqual(proof["CI_run_id"], 31_675_452_031)
        self.assertEqual(proof["base_job_id"], 94_368_928_633)
        self.assertEqual(proof["optional_neuro_job_id"], 94_368_928_658)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_source_identity_binds_retained_inventory_without_reading_it(self) -> None:
        source = self.contract["source_identity"]
        self.assertEqual(source["DOI"], "10.6084/m9.figshare.28632599.v1")
        self.assertEqual(source["archive_bytes"], 13_591_548_048)
        self.assertEqual(source["inventory_entries"], 1_227)
        self.assertEqual(source["private_manifest_bytes"], 418_755)
        self.assertEqual(
            source["private_manifest_sha256"],
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
        )
        self.assertFalse(source["private_manifest_read_authorized"])
        self.assertFalse(source["archive_or_member_payload_authorized"])

    def test_public_eligibility_is_exact(self) -> None:
        eligibility = self.contract["public_eligibility"]
        self.assertEqual(eligibility["published_participants"], 23)
        self.assertEqual(eligibility["sampling_rate_hz"], 250)
        self.assertEqual(eligibility["single_session_exclusions"], ["sub-02", "sub-17"])
        self.assertEqual(eligibility["sampling_tier_exclusions"], ["sub-13", "sub-15"])
        self.assertEqual(len(eligibility["eligible_subject_ids"]), 19)
        self.assertEqual(len(set(eligibility["eligible_subject_ids"])), 19)

    def test_preserved_full_rank_replays(self) -> None:
        rank = self.contract["participant_rank"]
        eligible = self.contract["public_eligibility"]["eligible_subject_ids"]
        self.assertEqual(rank_subjects(rank["selection_seed"], eligible), rank["full_rank"])
        self.assertEqual(
            rank["full_rank"][:12],
            [
                "sub-08", "sub-10", "sub-07", "sub-22", "sub-19", "sub-16",
                "sub-14", "sub-04", "sub-05", "sub-03", "sub-09", "sub-11",
            ],
        )
        self.assertTrue(rank["preserves_MARC1_P1_seed"])
        self.assertFalse(rank["override_available"])

    def test_run_bundle_and_split_are_exact(self) -> None:
        bundle = self.contract["run_bundle_and_split"]
        self.assertEqual(bundle["fit_session"], "ses-01")
        self.assertEqual(bundle["heldout_session"], "ses-02")
        self.assertEqual(bundle["run_bundles_per_subject"], 6)
        self.assertEqual(bundle["members_per_subject"], 24)
        self.assertEqual(
            bundle["required_suffixes"],
            ["_eeg.eeg", "_eeg.vhdr", "_eeg.vmrk", "_events.tsv"],
        )
        self.assertFalse(bundle["backfill_or_substitution_allowed"])
        self.assertFalse(bundle["sessions_after_ses_02_used"])

    def test_prefix_rule_has_floor_ceiling_and_no_skips(self) -> None:
        rule = self.contract["prefix_selection_rule"]
        self.assertEqual(rule["minimum_subjects"], 12)
        self.assertEqual(rule["maximum_subjects"], 19)
        self.assertEqual(rule["payload_reservation_cap_bytes"], 8 << 30)
        self.assertEqual(
            rule["member_reservation_formula"],
            "compressed_size + 30 + UTF8_member_name_bytes + 65535",
        )
        self.assertTrue(rule["maximal_contiguous_prefix_required"])
        self.assertFalse(rule["skip_after_first_nonfitting_subject_allowed"])
        self.assertFalse(rule["knapsack_or_size_reordering_allowed"])
        self.assertFalse(rule["participant_or_run_substitution_allowed"])

    def test_generated_fixture_expands_to_sixteen_without_payload(self) -> None:
        fixture = self.contract["generated_fixture_contract"]
        self.assertEqual(fixture["inventory_rows"], 1_227)
        self.assertEqual(fixture["eligible_subjects"], 19)
        self.assertEqual(fixture["complete_run_bundles"], 114)
        self.assertEqual(fixture["complete_core_members"], 456)
        self.assertEqual(fixture["compressed_bytes_per_subject"], 505_000_000)
        self.assertEqual(fixture["expected_selected_subjects"], 16)
        self.assertEqual(fixture["expected_selected_run_bundles"], 96)
        self.assertEqual(fixture["expected_selected_core_members"], 384)
        self.assertEqual(fixture["real_path_or_network_operations"], 0)

    def test_target_firewall_excludes_content_and_outcomes(self) -> None:
        firewall = self.contract["target_firewall"]
        self.assertTrue(firewall["selection_is_target_free"])
        for key in (
            "event_parser_available",
            "neuro_reader_available",
            "archive_extractor_available",
            "model_predictor_trainer_or_scorer_available",
        ):
            self.assertFalse(firewall[key], key)
        self.assertIn("target_or_label", firewall["forbidden_selection_inputs"])
        self.assertIn("technical_validation_outcome", firewall["forbidden_selection_inputs"])

    def test_interface_is_generated_only(self) -> None:
        interface = self.contract["interface"]
        self.assertEqual(interface["generated_commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(interface["execute_command_available"])
        self.assertFalse(interface["real_path_URL_host_or_credential_argument_available"])
        self.assertFalse(interface["seed_cap_subject_split_or_member_override_available"])
        self.assertFalse(interface["target_model_prediction_or_score_argument_available"])

    def test_privacy_separates_private_and_aggregate_surfaces(self) -> None:
        privacy = self.contract["privacy_contract"]
        self.assertEqual(privacy["private_output_mode"], "0600")
        self.assertTrue(privacy["public_selected_subject_ids_allowed"])
        self.assertFalse(privacy["public_member_names_offsets_or_CRC_allowed"])
        self.assertFalse(privacy["public_URLs_local_paths_raw_rows_or_headers_allowed"])
        self.assertFalse(privacy["inspect_accepts_private_manifest"])
        self.assertFalse(privacy["overwrite_allowed"])

    def test_resource_caps_preserve_storage_and_one_thread(self) -> None:
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["generated_CPU_threads"], 1)
        self.assertEqual(caps["generated_runtime_seconds"], 30)
        self.assertEqual(caps["generated_peak_RSS_bytes"], 256 << 20)
        self.assertEqual(caps["future_selected_reservation_bytes"], 8 << 30)
        self.assertEqual(caps["future_incremental_data_bytes"], 8 << 30)
        self.assertEqual(caps["future_minimum_free_disk_bytes"], 15 << 30)
        self.assertEqual(caps["future_private_derivative_bytes"], 64 << 20)

    def test_mutations_router_and_acceptance_are_frozen(self) -> None:
        mutations = self.contract["required_mutations"]
        self.assertEqual(len(mutations), 40)
        self.assertEqual(len(set(mutations)), 40)
        self.assertEqual(mutations[0], "contract_or_artifact_hash_mismatch")
        self.assertEqual(mutations[-1], "output_symlink_overwrite_cap_cleanup_or_replay_mismatch")
        router = self.contract["router"]
        self.assertEqual(len(router["ordered_refusal_routes"]), 6)
        self.assertEqual(router["success_route"], "MARC2FWG-R1")
        self.assertFalse(router["success_is_scientific_result"])
        self.assertFalse(router["success_authorizes_private_or_payload_access"])
        self.assertEqual(len(self.contract["acceptance_gates"]), 15)

    def test_all_current_authority_and_access_are_zero(self) -> None:
        self.assertTrue(
            all(value is False for value in self.contract["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.contract["access_counters"].values()))

    def test_next_gate_requires_green_milestones_and_fresh_decision(self) -> None:
        gate = self.contract["next_gate"]
        self.assertTrue(gate["generated_implementation_requires_this_contract_green"])
        self.assertTrue(gate["generated_closeout_requires_exact_implementation_green"])
        self.assertTrue(gate["private_selection_requires_later_all_false_Tier_C_packet"])
        self.assertTrue(gate["private_selection_requires_fresh_packet_bound_decision"])
        self.assertFalse(gate["member_acquisition_eligible_after_generated_success"])
        self.assertFalse(gate["current_maintainer_message_is_retroactive_private_authority"])

    def test_human_contract_preserves_two_claim_sentences(self) -> None:
        document = (
            ROOT / "docs" / "MARC_2_FREEWILL_PREFIX_SELECTION_PREREGISTRATION.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Engineering capability added if successful:", document)
        self.assertIn("Scientific claim not established even if successful:", document)
        self.assertIn("not retroactive authority for the private read", document)


if __name__ == "__main__":
    unittest.main()
