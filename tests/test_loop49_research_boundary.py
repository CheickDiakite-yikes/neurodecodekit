import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop49_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_49_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
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


class Loop49ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_metadata_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop49_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_metadata_candidate_selected_qualification_pending",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "metadata_only_development_candidate_selected_no_download_or_payload_access",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 25)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_dependencies_keep_stage_b_and_s25_closed(self):
        dependencies = self.boundary["dependencies"]
        self.assertFalse(dependencies["loop48_stage_b_result_available"])
        self.assertTrue(
            dependencies["decision_0083_requires_stage_b_before_new_loop49_acquisition"]
        )
        self.assertFalse(dependencies["loop49_preregistration_prepared"])
        self.assertFalse(dependencies["loop49_acquisition_request_prepared"])
        self.assertFalse(dependencies["loop49_experiment_started"])
        self.assertTrue(dependencies["s25_remains_final_only_and_unopened"])

    def test_metadata_pass_is_exact_and_payload_free(self):
        snapshot = self.boundary["official_metadata_snapshot"]
        self.assertEqual(
            snapshot["revision"],
            "88f9096c6ce3a3fb17cc7b8e3131ff7f96da5684",
        )
        self.assertEqual(snapshot["metadata_rows_observed_current_pass"], 396)
        self.assertEqual(snapshot["prior_loop27_strict_single_fif_log_pairs"], 23)
        self.assertEqual(snapshot["prior_loop27_eligible_pairs_after_exclusions"], 16)
        self.assertEqual(snapshot["measured_metadata_runtime_sec"], 3.51)
        self.assertEqual(snapshot["measured_metadata_peak_rss_bytes"], 62685184)
        self.assertEqual(snapshot["metadata_cpu_threads"], 1)
        self.assertEqual(snapshot["metadata_workers"], 1)
        self.assertFalse(snapshot["remote_signal_or_log_payload_downloaded"])
        self.assertEqual(snapshot["remote_payload_download_bytes"], 0)

    def test_policy_excludes_sources_final_person_and_official_invalid_subject(self):
        policy = self.boundary["selection_policy"]
        self.assertEqual(policy["required_role"], "development_only_never_final")
        self.assertEqual(policy["exclude_subject_ids"], ["S7", "S20", "S21", "S25"])
        self.assertEqual(
            policy["exclude_observed_s21_canonical_person_ids"],
            ["S5", "S10", "S21"],
        )
        self.assertEqual(policy["exclude_official_dataset_card_ids"], ["S23"])
        self.assertEqual(policy["official_s23_exclusion_reason"], "metallic_implant")
        self.assertFalse(policy["automatic_backup_after_protected_access"])
        self.assertTrue(policy["selection_does_not_establish_trial_floor"])

    def test_selected_s24_candidate_identity_and_file_hashes_are_exact(self):
        candidate = self.boundary["selected_candidate"]
        self.assertEqual(
            candidate["candidate_id"],
            "spanishbcbl-meg-s24-session2-block2-development-v0",
        )
        self.assertEqual(candidate["subject"], "S24")
        self.assertEqual(candidate["canonical_person"], "spanishbcbl-person-s24")
        self.assertEqual((candidate["session"], candidate["block"]), (2, 2))
        self.assertIsNone(candidate["published_alias_group"])
        self.assertEqual(candidate["intended_future_role"], "development_fit_and_selection_only")
        self.assertEqual(candidate["prohibited_future_role"], "final_unseen_person_evidence")

        fif, mat = candidate["files"]
        self.assertEqual(fif["path"], "MEG/FIF/24_7010/240531/block2.fif")
        self.assertEqual(fif["size_bytes"], 1048357252)
        self.assertEqual(
            fif["lfs_sha256"],
            "b75a60d1dc7210fc6abb2b65e959b392057bc09a884296ccbe15979bd332fb1a",
        )
        self.assertEqual(mat["path"], "MEG/logs/S24-session2_block2_list1.mat")
        self.assertEqual(mat["size_bytes"], 222475)
        self.assertEqual(
            mat["lfs_sha256"],
            "4da5387cf099364071bd806970c7db715577b6bcee218296361538a86928ebb3",
        )
        for row in (fif, mat):
            self.assertFalse(row["local_presence_checked_this_pass"])
            self.assertIsNone(row["local_presence"])
            self.assertFalse(row["content_opened_this_pass"])

    def test_selected_bundle_arithmetic_and_caps_are_exact(self):
        candidate = self.boundary["selected_candidate"]
        self.assertEqual(candidate["exact_file_count"], 2)
        self.assertEqual(
            candidate["exact_total_bytes"],
            sum(row["size_bytes"] for row in candidate["files"]),
        )
        self.assertEqual(candidate["exact_total_bytes"], 1048579727)
        self.assertEqual(candidate["future_download_cap_bytes"], int(1.25 * 1024**3))
        self.assertEqual(
            candidate["cap_margin_bytes"],
            candidate["future_download_cap_bytes"] - candidate["exact_total_bytes"],
        )
        self.assertEqual(candidate["cap_margin_bytes"], 293597553)
        self.assertEqual(candidate["one_gib_margin_bytes"], 1024**3 - 1048579727)
        self.assertEqual(
            candidate["remaining_cumulative_envelope_after_bundle_bytes"],
            10_000_000_000 - candidate["exact_total_bytes"],
        )

    def test_clean_identity_is_preferred_over_small_s18_byte_saving(self):
        comparison = {row["candidate_id"]: row for row in self.boundary["candidate_comparison"]}
        s18 = comparison["S18-session2-block2"]
        s24 = comparison["S24-session2-block2"]
        self.assertEqual(s18["bytes_relative_to_selected"], -29701559)
        self.assertEqual(s18["decision"], "not_selected")
        self.assertIn("alias", s18["reason"])
        self.assertEqual(s24["decision"], "selected_metadata_only")
        self.assertEqual(comparison["S25-session2-block2"]["decision"], "reserved_final_only")
        self.assertEqual(comparison["S23-session2-block2"]["decision"], "ineligible")
        self.assertEqual(comparison["S20"]["decision"], "separate_accessible_eeg_lane")

    def test_eligibility_distinguishes_metadata_selection_from_qualification(self):
        eligibility = self.boundary["eligibility_boundary"]
        for key in (
            "identity_independent_from_observed_s21_canonical_person",
            "not_reserved_s25_final_person",
            "same_modality_as_source_model",
            "same_nominal_meg_system",
            "same_prompted_typing_task",
            "license_verified_noncommercial",
            "exact_remote_file_identities_and_bytes_verified",
            "future_bundle_within_1_25_gib_cap",
            "eligible_for_metadata_selection",
        ):
            self.assertTrue(eligibility[key], key)
        for key in (
            "exact_sensor_names_and_order_verified",
            "exact_geometry_compatibility_verified",
            "exact_recording_duration_verified",
            "exact_performed_trial_count_verified",
            "minimum_48_usable_unique_trials_verified",
            "sentence_overlap_with_s21_source_train_verified",
            "qualified_as_loop49_development_cohort_now",
            "eligible_for_preregistration_now",
            "eligible_for_acquisition_execution_now",
            "eligible_for_signal_target_split_or_model_use_now",
        ):
            self.assertFalse(eligibility[key], key)

    def test_future_split_is_text_grouped_development_only_and_target_isolated(self):
        split = self.boundary["future_development_split_recommendation"]
        self.assertEqual(split["minimum_usable_unique_rows"], 48)
        self.assertEqual(split["selection_unique_sentence_hashes"], 16)
        self.assertEqual(split["minimum_fit_unique_sentence_hashes_at_gate"], 32)
        self.assertEqual(split["nominal_fit_unique_sentence_hashes_if_64_usable"], 48)
        self.assertEqual(split["final_or_test_rows"], 0)
        self.assertEqual(split["assignment_unit"], "canonical_sentence_text_hash_group")
        self.assertEqual(split["assignment_digest"], "SHA-256")
        self.assertTrue(split["same_text_across_rows_and_people_must_share_partition"])
        self.assertTrue(
            split[
                "s21_source_train_rows_matching_s24_selection_text_must_be_excluded_from_future_fit"
            ]
        )
        self.assertTrue(split["s21_validation_source_test_and_session2_rows_may_not_be_used"])
        self.assertTrue(split["raw_sentence_hashes_may_not_be_persisted"])
        self.assertTrue(split["sentence_plaintext_may_not_be_emitted"])
        self.assertTrue(
            split[
                "selection_targets_may_open_only_after_prediction_freeze_commit_push_and_green_ci"
            ]
        )
        self.assertTrue(split["s24_may_never_be_relabelled_as_independent_or_final_evidence"])
        self.assertIn("not a prospective power claim", split["minimum_row_reason"])

    def test_redacted_audit_forbids_plaintext_hashes_and_target_conditioned_selection(self):
        audit = self.boundary["future_redacted_audit_recommendation"]
        self.assertTrue(audit["mat_log_stays_opaque_today"])
        self.assertIn("performed_trial_count", audit["allowed_outputs"])
        self.assertIn("opaque_split_manifest_sha256", audit["allowed_outputs"])
        self.assertIn("sentence_plaintext", audit["forbidden_outputs"])
        self.assertIn("typed_response_plaintext", audit["forbidden_outputs"])
        self.assertIn("raw_canonical_sentence_hashes", audit["forbidden_outputs"])
        self.assertFalse(audit["audit_authorized_now"])

    def test_claim_ceiling_is_development_qualification_not_performance(self):
        claim = self.boundary["scientific_claim_boundary"]
        self.assertIn(
            "development cohort", claim["maximum_future_loop49_claim_if_all_intake_gates_pass"]
        )
        self.assertIn(
            "development evidence", claim["maximum_future_loop50_claim_if_its_separate_gates_pass"]
        )
        unavailable = " ".join(claim["not_established"])
        for term in ("48", "no-signal", "unseen-person", "Brain-specific", "Real-time"):
            self.assertIn(term, unavailable)

    def test_resources_and_access_counters_preserve_machine_and_payload_boundaries(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_remote_payload_download_bytes"], 0)
        self.assertEqual(resources["current_real_payload_read_bytes"], 0)
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_workers"], 1)
        self.assertEqual(resources["future_exact_bundle_bytes"], 1048579727)
        self.assertEqual(resources["future_download_cap_bytes"], int(1.25 * 1024**3))
        self.assertEqual(resources["future_minimum_free_disk_bytes"], 20 * 1024**3)
        self.assertGreater(resources["measured_free_disk_bytes_before_documentation"], 20 * 1024**3)
        self.assertFalse(resources["tracked_workbook_reopened_this_pass"])

        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_remote_metadata_api_operations"], 1)
        self.assertEqual(counters["remote_metadata_rows_received"], 396)
        protected = {
            key: value
            for key, value in counters.items()
            if key
            not in {"high_level_remote_metadata_api_operations", "remote_metadata_rows_received"}
        }
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_findings_blockers_and_access_order_are_complete(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        self.assertEqual(len({row["source_id"] for row in sources}), 8)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        self.assertEqual(len(self.boundary["primary_source_findings"]), 7)
        self.assertEqual(len(self.boundary["preregistration_blockers"]), 7)
        self.assertEqual(len(self.boundary["future_access_order"]), 10)
        self.assertIn("Stage B", self.boundary["preregistration_blockers"][0])
        self.assertIn("48", " ".join(self.boundary["preregistration_blockers"]))

    def test_human_note_covers_selection_resources_and_claim_boundary(self):
        for phrase in (
            "S24 session 2 block 2",
            "1,048,579,727 bytes",
            "293,597,553 bytes",
            "29,701,559 bytes",
            ">=48",
            "16 selection + 32 fit",
            "CC BY-NC 4.0",
            "does not establish",
        ):
            self.assertIn(phrase, self.research)

    def test_machine_roadmap_keeps_loop49_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 49)
        self.assertEqual(row["status"], "Not Started")
        self.assertFalse(row["execution_authorized"])
        self.assertIn("loop49_research_boundary.v0.json", row["build_deliverable"])
        self.assertIn("S24", row["data_scope"])
        self.assertIn(">=48", row["acceptance_gate"])
        self.assertIn("not download permission", row["authorization_boundary"])

    def test_public_status_names_planning_result_without_promoting_loop49(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertIn("Loop 49", contents)
                self.assertIn("S24", contents)
        combined = "\n".join(self.public_status.values())
        self.assertIn("1,048,579,727", combined)
        self.assertIn("Not Started", combined)
        self.assertIn("S25", combined)
        self.assertNotIn("Loop 49 is complete", combined)

    def test_no_loop49_preregistration_request_runtime_or_derivative_exists(self):
        forbidden = (
            "docs/LOOP_49_DEVELOPMENT_PERSON_PREREGISTRATION.md",
            "docs/LOOP_49_ACQUISITION_AUTHORIZATION_PACKET.md",
            "registries/loop49_development_person_contract.v0.json",
            "registries/loop49_authorization_request.v0.json",
            "selections/loop49_s24_development.json",
            "src/neurodecodekit/experiments/loop49_development_person.py",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))


if __name__ == "__main__":
    unittest.main()
