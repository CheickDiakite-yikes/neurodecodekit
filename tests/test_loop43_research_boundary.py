import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop43_research_boundary.v0.json"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_43_PRIMARY_SOURCE_RESEARCH.md"


class Loop43ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")

    def test_identity_and_every_execution_permission_are_false(self):
        self.assertEqual(
            self.boundary["schema_name"],
            "neurodecodekit.loop43_research_boundary",
        )
        self.assertEqual(self.boundary["schema_version"], "0.1.0")
        self.assertEqual(self.boundary["loop_id"], 43)
        self.assertEqual(
            self.boundary["status"],
            "planning_research_complete_experiment_not_started",
        )
        authorization = self.boundary["authorization"]
        false_fields = {
            key: value for key, value in authorization.items() if key.endswith("_authorized_now")
        }
        self.assertEqual(len(false_fields), 48)
        self.assertTrue(all(value is False for value in false_fields.values()))
        self.assertFalse(authorization["authorization_sentence_exists"])
        self.assertFalse(authorization["authorization_request_prepared"])
        self.assertFalse(authorization["preregistration_prepared"])

    def test_decision_selects_only_a_future_target_free_artifact_lane(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(
            decision["maximum_current_claim_class"],
            "L43-C0_no_independent_result",
        )
        self.assertEqual(
            decision["selected_future_challenge_lane"],
            "target_free_neurotoken_causal_replay_artifact_reproduction",
        )
        self.assertFalse(decision["selected_future_artifact_is_currently_eligible"])
        self.assertFalse(decision["same_team_clean_root_is_independent_reproduction"])
        self.assertFalse(
            decision["different_person_with_private_maintainer_guidance_is_independent"]
        )
        self.assertFalse(decision["author_artifact_reproduction_is_scientific_replication"])
        self.assertTrue(decision["failed_or_partial_reproduction_is_retained"])
        self.assertTrue(decision["commit_reveal_order_required"])

    def test_required_execution_dependencies_are_still_unsatisfied(self):
        dependencies = self.boundary["dependencies"]
        for loop_id in (37, 38, 39):
            self.assertTrue(dependencies[f"loop{loop_id}_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop37_release_envelope_execution_satisfied_now"])
        self.assertFalse(dependencies["loop38_public_artifact_lifecycle_execution_satisfied_now"])
        self.assertFalse(dependencies["loop39_required_matrix_execution_satisfied_now"])
        self.assertFalse(dependencies["loop39_independent_handoff_stage_satisfied_now"])
        self.assertFalse(dependencies["community_participant_and_challenge_review_satisfied_now"])
        self.assertFalse(dependencies["loop44_claim_review_satisfied_now"])
        self.assertFalse(dependencies["general_continuation_is_execution_authorization"])

    def test_terminology_keeps_repeatability_reproduction_and_replication_separate(self):
        terms = self.boundary["terminology_pins"]
        self.assertIn("same_team", terms["acm_repeatability"])
        self.assertIn("different_team", terms["acm_reproducibility"])
        self.assertIn("author_artifacts", terms["acm_reproducibility"])
        self.assertIn("independently_developed", terms["acm_replicability"])
        self.assertIn("author_artifact", terms["loop43_core_scope"])
        self.assertIn("independent", terms["scientific_replication_scope"])

    def test_current_repository_audit_is_explicit_and_does_not_claim_a_result(self):
        audit = self.boundary["current_repository_audit"]
        self.assertEqual(audit["audit_commit"], "8607897")
        self.assertTrue(audit["repository_public"])
        self.assertEqual(audit["repository_license"], "Apache-2.0")
        self.assertEqual(audit["tracked_file_count"], 292)
        self.assertEqual(audit["tracked_neural_or_array_payload_file_count"], 0)
        self.assertEqual(audit["release_count"], 0)
        self.assertFalse(audit["archival_doi_exists"])
        self.assertEqual(audit["issue_form_count"], 4)
        self.assertFalse(audit["challenge_packet_schema_exists"])
        self.assertFalse(audit["challenge_submission_schema_exists"])
        self.assertFalse(audit["independent_reproducer_exists"])
        self.assertEqual(audit["current_ci_permissions"], "contents_read")
        self.assertTrue(audit["current_ci_uses_pull_request_event"])
        self.assertFalse(audit["current_ci_uses_pull_request_target_event"])

    def test_qualification_ladder_stops_scientific_replication_outside_core(self):
        levels = self.boundary["qualification_levels"]
        self.assertEqual(len(levels), 7)
        self.assertEqual(levels[0]["level_id"], "L43-Q0_unavailable")
        self.assertEqual(levels[2]["level_id"], "L43-Q2_maintainer_dry_run")
        self.assertIn("not independent", levels[2]["meaning"])
        self.assertEqual(
            levels[4]["level_id"],
            "L43-Q4_independent_artifact_reproduction",
        )
        self.assertEqual(levels[-1]["level_id"], "L43-Q6_scientific_replication")
        self.assertIn("outside", levels[-1]["meaning"])

    def test_independence_packet_and_submission_fields_are_complete(self):
        independence = self.boundary["independence_record_fields"]
        packet = self.boundary["future_challenge_packet_fields"]
        submission = self.boundary["future_submission_core_fields"]
        self.assertEqual(len(independence), 16)
        self.assertEqual(len(packet), 28)
        self.assertEqual(len(submission), 34)
        combined = " ".join(independence + packet + submission)
        for term in (
            "authorship",
            "private_guidance",
            "communication",
            "environment",
            "oracle",
            "comparison",
            "security",
            "privacy",
            "runtime",
            "network",
            "access_counters",
            "claim",
        ):
            self.assertIn(term, combined)

    def test_comparisons_and_discrepancies_are_typed(self):
        comparisons = self.boundary["comparison_classes"]
        discrepancies = self.boundary["discrepancy_classes"]
        self.assertEqual(len(comparisons), 8)
        self.assertEqual(len(discrepancies), 12)
        self.assertEqual(
            comparisons,
            [
                f"L43-K{index}_{suffix}"
                for index, suffix in enumerate(
                    [
                        "packet_source_and_instruction_identity_exact",
                        "canonical_semantic_json_hash_exact",
                        "dtype_shape_discrete_and_time_state_values_exact",
                        "float_fields_under_preregistered_loop39_policy",
                        "container_manifest_exact_bytes_only_when_frozen",
                        "warning_refusal_and_unavailable_codes_exact",
                        "runtime_rss_setup_time_and_manual_steps_descriptive",
                        "privacy_security_independence_and_ordering_fail_closed",
                    ],
                    start=1,
                )
            ],
        )
        self.assertEqual(
            [row.split("_", 1)[0] for row in discrepancies],
            [f"L43-D{index:02d}" for index in range(1, 13)],
        )

    def test_stages_outcomes_and_claims_preserve_negative_evidence(self):
        stages = self.boundary["future_stage_sequence"]
        outcomes = self.boundary["outcome_taxonomy"]
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(stages), 4)
        self.assertTrue(all(row["separate_authorization_required"] for row in stages))
        self.assertEqual(len(outcomes), 10)
        self.assertIn("L43-X04_valid_negative_nonreproduction_record", outcomes)
        self.assertEqual(len(claims), 7)
        self.assertEqual(claims[0]["status"], "current")
        self.assertIn("outside_loop43", claims[-1]["status"])

    def test_fixtures_gates_and_refusals_are_contiguous_and_broad(self):
        fixtures = self.boundary["future_fixture_families"]
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(fixtures), 32)
        self.assertEqual(len(gates), 36)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L43-G{index:02d}" for index in range(1, 37)],
        )
        self.assertEqual(len(refusals), 48)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L43-R{index:02d}" for index in range(1, 49)],
        )
        combined = " ".join(fixtures + refusals)
        for term in (
            "authorization",
            "oracle",
            "private_guidance",
            "semantic",
            "tolerance",
            "network",
            "secret",
            "participant",
            "neural",
            "negative",
            "credit",
            "scientific_replication",
        ):
            self.assertIn(term, combined)

    def test_resources_are_bounded_and_verification_incident_is_explicit(self):
        limits = self.boundary["resource_limits"]
        self.assertEqual(limits["cpu_threads"], 1)
        self.assertEqual(limits["workers"], 1)
        self.assertEqual(limits["gpu_or_accelerator_count"], 0)
        self.assertEqual(limits["future_submission_bytes"], 32 * 1024 * 1024)
        self.assertEqual(limits["future_total_generated_bytes"], 64 * 1024 * 1024)
        self.assertEqual(limits["future_runtime_network_requests_after_setup"], 0)
        self.assertEqual(limits["future_real_or_contributor_neural_payload_bytes"], 0)
        self.assertFalse(limits["paid_or_proprietary_services_allowed"])
        counters = self.boundary["current_access_and_operations"]
        self.assertEqual(counters["high_level_public_web_operations"], 5)
        self.assertEqual(counters["public_search_queries"], 8)
        self.assertEqual(counters["official_or_primary_pages_opened"], 10)
        self.assertEqual(counters["public_github_metadata_operations"], 4)
        excluded = {
            "high_level_public_web_operations",
            "public_search_queries",
            "official_or_primary_pages_opened",
            "public_github_metadata_operations",
            "local_untracked_cache_json_files_read_during_verification",
            "known_consumed_session2_json_files_read_during_verification",
            "protected_or_real_data_reads",
            "consumed_cache_reads",
            "target_or_label_reads",
        }
        for key, value in counters.items():
            if isinstance(value, int) and key not in excluded:
                self.assertEqual(value, 0, key)
        self.assertEqual(counters["local_untracked_cache_json_files_read_during_verification"], 136)
        self.assertEqual(
            counters["known_consumed_session2_json_files_read_during_verification"], 11
        )
        self.assertEqual(counters["protected_or_real_data_reads"], 11)
        self.assertEqual(counters["consumed_cache_reads"], 11)
        self.assertEqual(counters["target_or_label_reads"], 11)
        self.assertFalse(counters["data_used_for_tuning_scoring_or_claim_selection"])
        incident = self.boundary["verification_incident"]
        self.assertEqual(incident["local_json_paths_read"], 603)
        self.assertEqual(incident["local_cache_json_files_read"], 136)
        self.assertEqual(incident["known_s21_session2_cross_session_json_files_read"], 11)
        self.assertTrue(incident["zero_consumed_read_claim_withdrawn"])
        self.assertFalse(incident["model_inference_training_scoring_or_parameter_updates_run"])

    def test_sources_warnings_and_claim_boundaries_are_explicit(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 9)
        source_ids = {row["source_id"] for row in sources}
        self.assertEqual(
            source_ids,
            {
                "acm_artifact_badging",
                "codecheck_principles",
                "codecheck_project",
                "rescience_author_guidelines",
                "rescience_faq",
                "neurips_reproducibility_program",
                "fair4rs_v1",
                "github_actions_secure_use",
                "github_pull_request_target_security",
            },
        )
        self.assertEqual(len(self.boundary["warnings"]), 11)
        claims = self.boundary["claim_boundaries"]
        self.assertIn("independent_reproduction", claims["engineering_capability_added"])
        self.assertIn("no_packet", claims["scientific_claim_not_established"])

    def test_machine_roadmap_is_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.20.0")
        current = self.roadmap["current_boundary"]
        self.assertTrue(current["loop43_research_packet_prepared"])
        self.assertEqual(current["loop43_qualification_level_count"], 7)
        self.assertEqual(current["loop43_independence_field_count"], 16)
        self.assertEqual(current["loop43_packet_field_count"], 28)
        self.assertEqual(current["loop43_submission_field_count"], 34)
        self.assertEqual(current["loop43_future_requirement_count"], 36)
        self.assertEqual(current["loop43_future_refusal_count"], 48)
        self.assertEqual(current["loop43_false_authorization_field_count"], 48)
        self.assertTrue(current["loop43_local_validation_metadata_read_incident_recorded"])
        self.assertEqual(current["loop43_local_untracked_cache_json_files_read"], 136)
        self.assertEqual(current["loop43_known_consumed_session2_json_files_read"], 11)
        self.assertFalse(current["loop43_zero_consumed_read_claim_retained"])
        self.assertFalse(current["loop43_data_used_for_tuning_scoring_or_claim_selection"])
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 43)
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertFalse(row["execution_authorized"])
        self.assertFalse(row["selected_future_artifact_is_currently_eligible"])
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["authorization_request_prepared"])

    def test_public_docs_preserve_the_no_execution_boundary(self):
        docs = [
            REPO_ROOT / "README.md",
            REPO_ROOT / "START_HERE.md",
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / "CONTRIBUTING.md",
            REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
            REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
            REPO_ROOT / "docs" / "CODEX_NEXT_20_LOOPS_PROMPT.md",
            REPO_ROOT / "docs" / "LOOPS_25_44_ROADMAP.md",
            REPO_ROOT / "docs" / "NEXT_20_LOOPS_PRIMARY_SOURCE_RESEARCH.md",
            REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
            REPO_ROOT / "docs" / "POST_20_ROADMAP.md",
        ]
        for path in docs:
            text = path.read_text(encoding="utf-8")
            self.assertIn("Loop 43", text, path)
            self.assertTrue(
                "Not Started" in text or "unauthorized" in text.lower(),
                path,
            )
        for term in (
            "planning research complete",
            "Not Started",
            "independent artifact reproduction",
            "scientific replication",
            "zero",
        ):
            self.assertIn(term, self.research)

    def test_no_loop43_runtime_fixture_or_privileged_workflow_was_added(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop43", source_text)
        self.assertNotIn("codecheck", source_text)
        workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertNotIn("pull_request_target", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8").lower()
        for dependency in ("codecheck", "codeocean", "dvc", "docker"):
            self.assertNotIn(dependency, pyproject)
        self.assertFalse((REPO_ROOT / "challenge").exists())
        self.assertFalse((REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "reproduction.yml").exists())


if __name__ == "__main__":
    unittest.main()
