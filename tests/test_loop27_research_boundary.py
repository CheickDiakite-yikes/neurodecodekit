import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop27_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_27_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop27ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_metadata_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(
            boundary["schema_name"], "neurodecodekit.loop27_research_boundary"
        )
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_preregistration_blocked",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "metadata_only_candidate_selected_no_download_or_payload_access",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 18)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_official_metadata_selection_counts_and_resources_are_exact(self):
        snapshot = self.boundary["official_metadata_snapshot"]
        self.assertEqual(snapshot["meg_metadata_file_count"], 315)
        self.assertEqual(snapshot["meg_metadata_total_bytes"], 267591914602)
        self.assertEqual(snapshot["strict_clean_single_fif_log_pairs"], 23)
        self.assertEqual(snapshot["eligible_strict_pairs_after_exclusions"], 16)
        self.assertEqual(snapshot["measured_selector_runtime_sec"], 3.1)
        self.assertEqual(snapshot["measured_selector_peak_rss_bytes"], 63766528)
        self.assertEqual(snapshot["selector_cpu_threads"], 1)
        self.assertEqual(snapshot["selector_workers"], 1)
        self.assertFalse(snapshot["remote_signal_or_log_payload_downloaded"])

    def test_selection_policy_excludes_observed_consumed_and_officially_invalid_ids(self):
        policy = self.boundary["selection_policy"]
        self.assertEqual(
            policy["exclude_observed_s21_canonical_person_ids"],
            ["S5", "S10", "S21"],
        )
        self.assertEqual(policy["exclude_consumed_cross_modality_person_ids"], ["S7"])
        self.assertEqual(policy["exclude_official_dataset_card_ids"], ["S23"])
        self.assertEqual(policy["official_s23_exclusion_reason"], "metallic_implant")
        self.assertTrue(policy["require_one_primary_fif_without_split_continuation"])
        self.assertFalse(policy["automatic_backup_after_protected_access"])

    def test_selected_s25_candidate_identity_bytes_and_cap_are_exact(self):
        candidate = self.boundary["selected_candidate"]
        self.assertEqual(
            candidate["candidate_id"], "spanishbcbl-meg-s25-session2-block2-v0"
        )
        self.assertEqual(candidate["subject"], "S25")
        self.assertEqual(candidate["canonical_person"], "spanishbcbl-person-s25")
        self.assertEqual((candidate["session"], candidate["block"]), (2, 2))
        self.assertFalse(candidate["published_alias_with_observed_s21_person"])
        self.assertFalse(candidate["published_exclusion"])
        self.assertEqual(candidate["exact_file_count"], 2)
        self.assertEqual(candidate["exact_total_bytes"], 1009939983)
        self.assertEqual(candidate["future_download_cap_bytes"], 1024**3)
        self.assertEqual(
            candidate["cap_margin_bytes"],
            candidate["future_download_cap_bytes"] - candidate["exact_total_bytes"],
        )

    def test_selected_file_metadata_and_payload_hashes_are_exact(self):
        files = self.boundary["selected_candidate"]["files"]
        self.assertEqual(len(files), 2)
        fif, mat = files
        self.assertEqual(fif["path"], "MEG/FIF/25_12032/240530/block2.fif")
        self.assertEqual(fif["size_bytes"], 1009713753)
        self.assertEqual(
            fif["lfs_sha256"],
            "ef6b36fbf3efbfc86580cf68f45edf5254f2e134083a77e1fd88b22084f654be",
        )
        self.assertEqual(
            mat["path"], "MEG/logs/S25-session2_block2_list1.mat"
        )
        self.assertEqual(mat["size_bytes"], 226230)
        self.assertEqual(
            mat["lfs_sha256"],
            "470888435ddf8ab3a7fc50ab568d015e260aff908b08cb58aeb7aabe1da97557",
        )
        self.assertTrue(mat["local_presence_observed"])
        self.assertFalse(mat["local_payload_hash_computed_this_pass"])
        self.assertFalse(mat["content_opened_this_pass"])
        self.assertFalse(fif["local_presence_observed"])
        self.assertFalse(fif["content_opened_this_pass"])

    def test_candidate_ranking_preserves_s23_and_s20_boundaries(self):
        comparison = {
            row["candidate_id"]: row for row in self.boundary["candidate_comparison"]
        }
        self.assertEqual(comparison["S25-session2-block2"]["decision"], "selected")
        self.assertEqual(
            comparison["S23-session2-block2"]["decision"], "ineligible"
        )
        self.assertIn("metallic", comparison["S23-session2-block2"]["warning"])
        self.assertEqual(
            comparison["S20-session2-block2-EEG"]["decision"],
            "separate_rw4_cohort",
        )
        self.assertIn("EEG", comparison["S20-session2-block2-EEG"]["warning"])

    def test_eligibility_is_explicit_about_available_and_unavailable_fields(self):
        eligibility = self.boundary["eligibility_boundary"]
        for key in (
            "identity_independent_from_observed_s21_canonical_person",
            "same_modality_as_source_model",
            "same_nominal_meg_system",
            "same_prompted_typing_task",
            "license_verified_noncommercial",
            "eligible_for_metadata_selection",
        ):
            self.assertTrue(eligibility[key], key)
        for key in (
            "exact_sensor_names_and_order_verified",
            "exact_geometry_compatibility_verified",
            "exact_performed_trial_count_verified",
            "exact_unique_sentence_count_verified",
            "sentence_overlap_with_source_partitions_verified",
            "candidate_target_freshness_proven_against_external_manual_access",
            "eligible_for_preregistration_now",
            "eligible_for_acquisition_authorization_now",
            "eligible_for_signal_or_target_open_now",
        ):
            self.assertFalse(eligibility[key], key)

    def test_final_only_recommendation_cannot_fit_or_split_candidate(self):
        protocol = self.boundary["future_final_only_protocol_recommendation"]
        self.assertEqual(protocol["candidate_train_rows"], 0)
        self.assertEqual(protocol["candidate_validation_rows"], 0)
        self.assertEqual(protocol["candidate_calibration_rows"], 0)
        self.assertEqual(protocol["minimum_performed_unique_rows"], 48)
        self.assertTrue(protocol["no_candidate_fit_or_threshold_selection"])
        self.assertTrue(protocol["source_model_and_controls_frozen_before_candidate_content"])
        self.assertTrue(protocol["unseen_text_claim_requires_zero_source_overlap"])
        self.assertIn("not a prospective power claim", protocol["minimum_row_reason"])

    def test_target_isolation_forbids_plaintext_and_control_freeze_is_pending(self):
        target = self.boundary["future_target_isolation_recommendation"]
        self.assertIn("sentence_plaintext", target["forbidden_outputs"])
        self.assertIn("typed_response_plaintext", target["forbidden_outputs"])
        self.assertFalse(target["target_audit_authorized_now"])
        controls = self.boundary["future_control_requirements"]
        self.assertEqual(len(controls), 4)
        self.assertTrue(all(not row["frozen_now"] for row in controls))

    def test_resources_and_protected_access_counters_are_bounded(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_downloaded_payload_bytes"], 0)
        self.assertEqual(resources["current_generated_planning_artifact_cap_bytes"], 8 * 1024**2)
        self.assertEqual(resources["future_exact_file_count"], 2)
        self.assertEqual(resources["future_exact_bundle_bytes"], 1009939983)
        self.assertEqual(resources["future_download_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_minimum_free_disk_bytes"], 4 * 1024**3)
        self.assertEqual(resources["future_workers"], 1)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_remote_metadata_api_operations"], 6)
        protected = {key: value for key, value in counters.items() if key != "high_level_remote_metadata_api_operations" and key != "local_candidate_path_metadata_checks"}
        self.assertTrue(all(value == 0 for value in protected.values()), protected)

    def test_sources_and_human_note_cover_the_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 7)
        self.assertEqual(len({row["source_id"] for row in sources}), len(sources))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        for phrase in (
            "S25 session 2 block 2",
            "1,009,939,983 bytes",
            "63,801,841 bytes",
            "metallic implant",
            "no preregistration",
            "does not establish",
        ):
            self.assertIn(phrase, self.research)

    def test_roadmap_keeps_loop27_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 27)
        self.assertEqual(row["status"], "Not Started")
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(
            row["research_registry"],
            "registries/loop27_research_boundary.v0.json",
        )
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["acquisition_request_prepared"])

    def test_no_loop27_preregistration_request_selection_or_runtime_exists(self):
        forbidden = (
            "docs/LOOP_27_FRESH_HOLDOUT_PREREGISTRATION.md",
            "docs/LOOP_27_ACQUISITION_AUTHORIZATION_PACKET.md",
            "registries/loop27_holdout_contract.v0.json",
            "registries/loop27_authorization_request.v0.json",
            "selections/loop27_s25_holdout.json",
            "src/neurodecodekit/experiments/fresh_holdout.py",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))

    def test_public_status_keeps_selection_separate_from_preregistration(self):
        for path, contents in self.public_status.items():
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                lowered = contents.lower()
                self.assertIn("loop 27", lowered)
                self.assertIn("planning research", lowered)
                self.assertIn("s25", lowered)
                self.assertIn("preregistration", lowered)
        combined = "\n".join(self.public_status.values())
        self.assertIn("1,009,939,983", combined)
        self.assertIn("Not Started", combined)
        self.assertNotIn("Loop 27 is complete", combined)


if __name__ == "__main__":
    unittest.main()
