import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop37_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_37_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop37ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop37_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 29)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_compliance_and_release_claims(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L37-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_stage_b_claim"],
            "L37-C2_validator_assessed_standard_envelope_with_nonstandard_payloads",
        )
        self.assertFalse(decision["bids_compliant_neurotoken_suffix_available_now"])
        self.assertFalse(decision["bids_compliant_npz_neurotoken_payload_available_now"])
        self.assertFalse(decision["public_release_available_now"])
        self.assertEqual(
            decision["unknown_source_uri_license_or_privacy_default"],
            "unavailable_or_refuse",
        )

    def test_dependencies_preserve_loop36_38_39_boundaries(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop36_planning_dependency_satisfied_now"])
        self.assertFalse(
            dependencies["loop36_execution_or_real_metadata_result_required_for_stage_a"]
        )
        self.assertTrue(
            dependencies["loop38_privacy_lifecycle_required_before_real_or_public_export"]
        )
        self.assertTrue(
            dependencies["loop39_cross_machine_matrix_required_before_reproducibility_claim"]
        )
        self.assertFalse(dependencies["existing_neurotoken_cache_is_standard_bids_derivative"])
        self.assertFalse(dependencies["existing_report_cards_are_standard_bids_derivatives"])

    def test_stable_standard_pins_are_exact(self):
        standards = self.boundary["standards_pins"]
        self.assertEqual(standards["bids_specification_version_researched"], "1.11.1")
        self.assertEqual(standards["bids_validator_release_researched"], "2.4.1")
        for key in (
            "dataset_description_required",
            "dataset_name_required",
            "bids_version_required",
            "derivative_generated_by_required",
            "source_files_use_bids_uris",
            "relative_source_paths_deprecated",
            "rawsources_field_deprecated",
            "readme_required",
            "transformed_file_must_not_collide_with_permissible_raw_filename",
            "validator_is_optional_external_tool_not_base_dependency",
        ):
            self.assertTrue(standards[key], key)
        self.assertEqual(standards["dataset_type_value"], "derivative")
        self.assertFalse(standards["proposed_bep028_provenance_fields_used_as_stable_standard"])

    def test_existing_evidence_has_eight_rows_and_no_payload_reads(self):
        rows = self.boundary["existing_evidence_inventory"]
        self.assertEqual(len(rows), 8)
        self.assertTrue(all(row["payload_read_now"] is False for row in rows))
        evidence = {row["evidence_id"]: row["finding"] for row in rows}
        self.assertIn("zero", evidence["tracked_payload_inventory"])
        self.assertIn("local paths", evidence["neurotoken_local_paths"])
        self.assertIn("non-standard", evidence["nonstandard_payload_status"])

    def test_export_layers_and_artifact_profiles_are_explicit(self):
        layers = self.boundary["export_layers"]
        profiles = self.boundary["artifact_profiles"]
        self.assertEqual(len(layers), 6)
        self.assertEqual(len(profiles), 5)
        self.assertEqual(
            [row["layer_id"].split("_", 1)[0] for row in layers],
            [f"L37-L{index}" for index in range(1, 7)],
        )
        status = {row["profile_id"]: row["bids_standard_status"] for row in profiles}
        self.assertEqual(status["L37-A1_neurotoken_cache"], "nonstandard_bids_organized")
        self.assertEqual(status["L37-A5_dataset_envelope"], "standard_fields_only")

    def test_standard_fields_use_bids_uris_and_never_invent_metadata(self):
        fields = self.boundary["standard_field_mapping"]
        self.assertEqual(len(fields), 15)
        mapping = {row["field"]: row["requirement"] for row in fields}
        self.assertEqual(mapping["dataset_description.BIDSVersion"], "required_pinned_1.11.1")
        self.assertIn("truthful", mapping["dataset_description.SourceDatasets"])
        self.assertIn("bids_uris", mapping["file.Sources"])
        self.assertIn("omit", mapping["unavailable_optional_fields"])
        self.assertIn("compatible", mapping["license"])

    def test_ndk_extension_fields_cover_identity_resources_and_claims(self):
        fields = self.boundary["ndk_extension_fields"]
        self.assertEqual(len(fields), 16)
        combined = " ".join(fields)
        for term in (
            "schema",
            "standardization",
            "source",
            "split",
            "configuration",
            "payload",
            "code",
            "identity",
            "masks",
            "timestamps",
            "geometry",
            "causal",
            "resource",
            "warnings",
            "claim",
            "bundle",
        ):
            self.assertIn(term, combined)

    def test_path_policy_refuses_private_or_ambiguous_paths(self):
        policy = self.boundary["path_and_identity_policy"]
        for key in (
            "absolute_paths_allowed",
            "home_usernames_allowed",
            "parent_traversal_allowed",
            "symlinks_allowed",
            "hardlinks_allowed",
            "case_folded_collisions_allowed",
            "subject_or_session_label_collisions_allowed",
            "source_labels_reused_without_privacy_review",
        ):
            self.assertFalse(policy[key], key)
        self.assertEqual(policy["overwrite_default"], "refuse")
        self.assertEqual(policy["path_separator"], "/")
        self.assertIn("opaque_hash", policy["source_identity_when_no_bids_uri"])

    def test_raw_copy_policy_is_zero_and_target_free(self):
        policy = self.boundary["raw_copy_and_payload_policy"]
        self.assertEqual(policy["raw_recording_extensions_allowlisted"], [])
        self.assertEqual(policy["raw_recording_copy_count_required"], 0)
        self.assertEqual(policy["byte_identical_raw_copy_count_required"], 0)
        self.assertEqual(policy["unrecognized_payload_default"], "refuse")
        self.assertTrue(policy["payload_and_source_must_not_share_inode"])
        self.assertEqual(
            policy["targets_prompts_response_text_and_free_text_default"],
            "forbidden",
        )
        self.assertTrue(policy["generated_tree_must_remain_git_ignored"])

    def test_compliance_language_never_upgrades_custom_payloads(self):
        policy = self.boundary["compliance_language_policy"]
        self.assertIn("non-standard", policy["allowed_future_stage_b_label"])
        self.assertIn(
            "BIDS-compliant NeuroToken derivative",
            policy["forbidden_labels_without_additional_evidence"],
        )
        self.assertTrue(policy["validator_success_does_not_validate_scientific_provenance"])
        self.assertTrue(
            policy["unknown_files_ignored_or_warned_by_validator_do_not_become_standard"]
        )

    def test_fixtures_stages_outcomes_and_claims_are_exact(self):
        self.assertEqual(len(self.boundary["future_fixture_families"]), 20)
        stages = self.boundary["future_stage_sequence"]
        self.assertEqual(len(stages), 4)
        self.assertTrue(all(row["separate_authorization_required"] for row in stages))
        self.assertEqual(len(self.boundary["outcome_taxonomy"]), 8)
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(claims), 6)
        self.assertEqual(claims[-2]["status"], "reserved_for_loop39")
        self.assertEqual(claims[-1]["status"], "reserved_for_loop38_and_loop44")

    def test_gates_and_refusals_cover_full_failure_surface(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 24)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L37-G{index:02d}" for index in range(1, 25)],
        )
        self.assertEqual(len(refusals), 32)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L37-R{index:02d}" for index in range(1, 33)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "dataset",
            "generatedby",
            "source",
            "path",
            "collision",
            "raw",
            "symlink",
            "target",
            "hash",
            "license",
            "privacy",
            "validator",
            "resource",
            "tracked",
            "overclaim",
        ):
            self.assertIn(term, combined)

    def test_resources_and_access_counters_remain_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_generated_artifact_bytes"], 0)
        self.assertEqual(resources["future_stage_a_runtime_cap_sec"], 120)
        self.assertEqual(resources["future_stage_a_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_stage_a_generated_tree_cap_bytes"], 16 * 1024**2)
        self.assertEqual(resources["future_stage_a_file_count_cap"], 128)
        self.assertEqual(resources["future_stage_a_network_download_bytes"], 0)
        self.assertEqual(resources["future_stage_a_raw_copy_bytes"], 0)
        self.assertTrue(resources["bids_validator_remains_optional"])
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 7)
        self.assertEqual(counters["official_github_repository_reads"], 2)
        excluded = {
            "high_level_public_web_research_operations",
            "official_github_repository_reads",
            "public_network_response_bytes",
            "public_network_response_bytes_unavailable_reason",
        }
        numeric = [
            value
            for key, value in counters.items()
            if key not in excluded and isinstance(value, int)
        ]
        self.assertTrue(all(value == 0 for value in numeric))

    def test_sources_and_human_note_preserve_exact_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        source_ids = {row["source_id"] for row in sources}
        self.assertEqual(
            source_ids,
            {
                "bids_derivatives",
                "bids_dataset_description",
                "bids_derivative_common_data",
                "bids_common_principles",
                "bids_extensions",
                "bids_validator",
                "bids_examples",
                "datasheets",
            },
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        for text in (
            "planning research complete",
            "experiment `Not Started`",
            "six export layers",
            "five artifact profiles",
            "15 standard-field mappings",
            "16 explicit NeuroDecodeKit extension fields",
            "20 fixture families",
            "24 acceptance gates",
            "32 refusals",
            "29 false authorization fields",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_roadmap_row_and_public_status_are_synchronized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 37)
        self.assertEqual(row["status"], "Not Started")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertEqual(
            row["research_boundary_registry"], "registries/loop37_research_boundary.v0.json"
        )
        self.assertEqual(row["primary_source_research"], "docs/LOOP_37_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(row["future_requirement_count"], 24)
        self.assertEqual(row["future_refusal_count"], 32)
        self.assertIn("non-standard", row["acceptance_boundary"])
        self.assertIn("separate Loop 37", row["authorization_boundary"])
        for path, text in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 37", text)
                self.assertIn("planning research", text)
                self.assertIn("Not Started", text)
                self.assertIn("non-standard", text)
                self.assertIn("unauthorized", text)

    def test_no_loop37_runtime_or_generated_payload_is_present(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop37", source_text)
        self.assertNotIn("bids_derivative_export", source_text)
        self.assertNotIn("make-bids-derivative", source_text)
        self.assertEqual(
            self.boundary["resource_boundaries"]["current_generated_artifact_bytes"], 0
        )


if __name__ == "__main__":
    unittest.main()
