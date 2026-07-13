import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop38_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_38_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop38ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop38_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 32)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_privacy_and_deletion_claims(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L38-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_stage_b_claim"],
            "L38-C2_repository_and_named_local_root_lifecycle_coverage",
        )
        self.assertFalse(decision["anonymous_neural_data_available_now"])
        self.assertFalse(decision["privacy_safe_release_available_now"])
        self.assertFalse(decision["verified_media_sanitization_available_now"])
        self.assertEqual(
            decision["unknown_copy_consent_license_or_owner_default"],
            "unresolved_and_block_sharing",
        )

    def test_dependencies_keep_consent_license_and_deletion_separate(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop37_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop37_execution_or_derivative_tree_required_for_stage_a"])
        for key in (
            "license_implies_participant_consent",
            "deidentification_implies_share_permission",
            "gitignore_implies_deletion",
            "path_absence_implies_media_sanitization",
        ):
            self.assertFalse(dependencies[key], key)
        self.assertTrue(dependencies["loop44_required_before_public_release_claim"])

    def test_standards_pins_use_stable_nist_framework(self):
        standards = self.boundary["standards_pins"]
        self.assertEqual(standards["nist_privacy_framework_stable_version"], "1.0")
        self.assertIn("initial_public_draft", standards["nist_privacy_framework_1_1_status"])
        self.assertEqual(
            standards["nist_ir_8062_privacy_objectives"],
            ["predictability", "manageability", "disassociability"],
        )
        self.assertEqual(standards["nist_sp_800_88_revision"], "2")
        self.assertTrue(standards["github_history_removal_requires_clone_coordination"])
        self.assertTrue(standards["open_brain_consent_is_template_not_local_legal_clearance"])
        self.assertTrue(
            standards["eeg_identity_results_are_risk_evidence_not_local_attack_results"]
        )

    def test_existing_evidence_is_metadata_only(self):
        rows = self.boundary["existing_evidence_inventory"]
        self.assertEqual(len(rows), 9)
        self.assertTrue(all(row["payload_read_now"] is False for row in rows))
        evidence = {row["evidence_id"]: row["finding"] for row in rows}
        self.assertIn("zero", evidence["current_tracked_payload_inventory"])
        self.assertIn("zero", evidence["all_history_payload_path_inventory"])
        self.assertIn("do not prove", evidence["ignored_local_roots"])
        self.assertIn("potentially linkable", evidence["internal_provenance_linkability"])
        self.assertIn("cannot prove", evidence["deletion_claim_boundary"])

    def test_sensitivity_and_artifact_taxonomies_are_exact(self):
        levels = self.boundary["sensitivity_levels"]
        artifacts = self.boundary["artifact_classes"]
        self.assertEqual(len(levels), 5)
        self.assertEqual(len(artifacts), 8)
        self.assertEqual(
            [row["level_id"] for row in levels],
            [
                "L38-S0_public",
                "L38-S1_internal_operational",
                "L38-S2_pseudonymous_research",
                "L38-S3_neural_or_derived_sensitive",
                "L38-S4_direct_or_governance_restricted",
            ],
        )
        profiles = {row["artifact_id"]: row for row in artifacts}
        self.assertEqual(
            profiles["L38-A4_embedding_neurotoken_or_checkpoint"]["public_release_default"],
            "forbidden_without_identity_and_inversion_review",
        )
        self.assertEqual(
            profiles["L38-A7_temporary_intermediate_or_backup"]["default_sensitivity"],
            "inherit_highest_source_sensitivity",
        )

    def test_lifecycle_fields_and_threats_cover_copy_surface(self):
        self.assertEqual(len(self.boundary["lifecycle_surfaces"]), 10)
        self.assertEqual(len(self.boundary["sensitive_field_classes"]), 12)
        self.assertEqual(len(self.boundary["threat_scenarios"]), 12)
        combined = " ".join(
            self.boundary["lifecycle_surfaces"]
            + self.boundary["sensitive_field_classes"]
            + self.boundary["threat_scenarios"]
        )
        for term in (
            "temporary",
            "backup",
            "git",
            "clone",
            "ci",
            "absolute_path",
            "participant",
            "timestamp",
            "serial",
            "secret",
            "consent",
            "target",
            "hash",
            "embedding",
            "small_cell",
        ):
            self.assertIn(term, combined)

    def test_deletion_receipts_never_overclaim_sanitization(self):
        receipts = self.boundary["deletion_receipt_levels"]
        self.assertEqual(len(receipts), 5)
        self.assertEqual(
            [row["receipt_id"] for row in receipts],
            [
                "L38-D0_not_requested_or_unknown",
                "L38-D1_scoped_path_absent",
                "L38-D2_local_manifest_rescan_clean",
                "L38-D3_repository_remote_coordination_recorded",
                "L38-D4_media_sanitization_external",
            ],
        )
        policy = self.boundary["deletion_policy"]
        self.assertEqual(policy["default_operation"], "dry_run_inventory_only")
        self.assertFalse(policy["broad_recursive_cleanup_allowed"])
        self.assertFalse(policy["unowned_root_cleanup_allowed"])
        self.assertFalse(policy["symlink_following_allowed"])
        self.assertFalse(policy["receipt_contains_payload_bytes"])
        self.assertFalse(policy["receipt_is_media_sanitization_proof"])
        self.assertEqual(policy["unknown_backup_clone_or_remote_copy_default"], "unresolved")

    def test_fixtures_stages_outcomes_and_claims_are_exact(self):
        self.assertEqual(len(self.boundary["future_fixture_families"]), 24)
        stages = self.boundary["future_stage_sequence"]
        self.assertEqual(len(stages), 4)
        self.assertTrue(all(row["separate_authorization_required"] for row in stages))
        self.assertEqual(len(self.boundary["outcome_taxonomy"]), 8)
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(claims), 6)
        self.assertEqual(claims[-2]["status"], "reserved_for_loop39")
        self.assertEqual(claims[-1]["status"], "reserved_for_loop44_and_external_governance")

    def test_gates_and_refusals_cover_full_failure_surface(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 26)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L38-G{index:02d}" for index in range(1, 27)],
        )
        self.assertEqual(len(refusals), 36)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L38-R{index:02d}" for index in range(1, 37)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "owner",
            "path",
            "participant",
            "timestamp",
            "secret",
            "consent",
            "target",
            "hash",
            "neural",
            "symlink",
            "temporary",
            "backup",
            "git",
            "clone",
            "deletion",
            "license",
            "identity",
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
        self.assertEqual(resources["future_stage_a_peak_rss_cap_bytes"], 512 * 1024**2)
        self.assertEqual(resources["future_stage_a_generated_report_cap_bytes"], 8 * 1024**2)
        self.assertEqual(resources["future_stage_a_file_count_cap"], 128)
        self.assertEqual(resources["future_stage_a_network_download_bytes"], 0)
        self.assertEqual(resources["future_stage_a_destructive_nonfixture_mutations"], 0)
        self.assertTrue(resources["standard_library_first"])
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 6)
        self.assertEqual(counters["official_or_primary_source_pages_opened"], 8)
        excluded = {
            "high_level_public_web_research_operations",
            "official_or_primary_source_pages_opened",
            "public_network_response_bytes",
            "public_network_response_bytes_unavailable_reason",
        }
        numeric = [
            value
            for key, value in counters.items()
            if key not in excluded and isinstance(value, int)
        ]
        self.assertTrue(all(value == 0 for value in numeric))

    def test_sources_are_primary_and_human_note_is_explicit(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 8)
        self.assertEqual(
            {row["source_id"] for row in sources},
            {
                "nist_privacy_framework",
                "nist_ir_8062",
                "nist_pram",
                "nist_sp_800_88_r2",
                "github_remove_sensitive_data",
                "open_brain_consent",
                "eeg_identity_privacy",
                "oecd_responsible_neurotechnology",
            },
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        for text in (
            "planning research complete",
            "experiment `Not Started`",
            "five sensitivity levels",
            "eight artifact classes",
            "ten lifecycle surfaces",
            "12 sensitive-field classes",
            "24 fixture families",
            "26 acceptance gates",
            "36 refusal IDs",
            "32 false authorization fields",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_roadmap_row_and_public_status_are_synchronized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 38)
        self.assertEqual(row["status"], "Not Started")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertEqual(
            row["research_boundary_registry"], "registries/loop38_research_boundary.v0.json"
        )
        self.assertEqual(row["primary_source_research"], "docs/LOOP_38_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(row["future_requirement_count"], 26)
        self.assertEqual(row["future_refusal_count"], 36)
        self.assertIn("unresolved", row["acceptance_boundary"])
        self.assertIn("separate Loop 38", row["authorization_boundary"])
        for path, text in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 38", text)
                self.assertIn("planning research", text)
                self.assertIn("Not Started", text)
                self.assertIn("unresolved", text)
                self.assertIn("unauthorized", text)

    def test_no_loop38_runtime_or_generated_payload_is_present(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8") for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop38", source_text)
        self.assertNotIn("privacy_lifecycle_scan", source_text)
        self.assertNotIn("deletion_receipt", source_text)
        self.assertEqual(
            self.boundary["resource_boundaries"]["current_generated_artifact_bytes"], 0
        )


if __name__ == "__main__":
    unittest.main()
