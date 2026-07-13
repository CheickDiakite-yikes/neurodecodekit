import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop39_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_39_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
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


class Loop39ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
        cls.ci = CI_PATH.read_text(encoding="utf-8")
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_every_authorization_is_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop39_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["loop_id"], 39)
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 36)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_current_and_future_claims(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L39-C0_no_cross_machine_result")
        self.assertEqual(decision["selected_future_required_cell_count"], 6)
        self.assertFalse(decision["single_host_green_ci_is_cross_machine_reproduction"])
        self.assertFalse(decision["same_rounded_metric_is_artifact_identity"])
        self.assertFalse(decision["dependency_range_is_reproducible_environment"])
        self.assertFalse(decision["tolerance_can_be_widened_after_result_access"])
        self.assertTrue(decision["unsupported_cells_must_fail_explicitly"])
        self.assertTrue(decision["loop43_required_for_independent_team_reproduction"])

    def test_dependencies_keep_later_claims_separate(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop37_planning_dependency_satisfied_now"])
        self.assertTrue(dependencies["loop38_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop37_execution_or_derivative_tree_required_for_stage_a"])
        self.assertFalse(dependencies["loop38_execution_or_lifecycle_scanner_required_for_stage_a"])
        self.assertTrue(dependencies["loop40_requires_relevant_loop39_matrix_pass"])
        self.assertTrue(dependencies["loop43_required_before_independent_reproduction_claim"])
        self.assertTrue(dependencies["loop44_required_before_release_claim"])
        self.assertFalse(dependencies["general_continuation_is_execution_authorization"])

    def test_primary_source_pins_are_explicit(self):
        standards = self.boundary["standards_pins"]
        self.assertEqual(
            standards["acm_repeatability_definition"], "same_team_same_experimental_setup"
        )
        self.assertEqual(
            standards["acm_reproducibility_definition"],
            "different_team_same_experimental_setup",
        )
        self.assertEqual(
            standards["reproducible_builds_definition"],
            "same_source_environment_and_instructions_recreate_bit_identical_specified_artifacts",
        )
        self.assertEqual(standards["pip_inspect_report_schema"], "version_1_stable")
        self.assertEqual(standards["github_runner_labels"], ["ubuntu-24.04", "macos-15"])
        self.assertFalse(standards["pytorch_cross_release_platform_bitwise_guarantee"])
        self.assertTrue(standards["scientific_python_spec0_is_support_policy_not_environment_lock"])

    def test_current_support_audit_matches_repository_metadata(self):
        audit = self.boundary["current_support_audit"]
        self.assertEqual(audit["declared_python_minimum"], "3.10")
        self.assertEqual(audit["declared_python_classifier_minors"], ["3.10", "3.11", "3.12"])
        self.assertEqual(audit["current_public_ci_os_label"], "ubuntu-latest")
        self.assertEqual(audit["current_public_ci_python_minor"], "3.12")
        self.assertEqual(audit["current_public_ci_profiles"], ["base", "optional_neuro"])
        self.assertEqual(audit["current_public_ci_cross_os_cells"], 0)
        self.assertEqual(audit["current_dependency_lockfiles"], 0)
        self.assertEqual(audit["current_wheel_or_sdist_reproducibility_jobs"], 0)
        self.assertFalse(audit["current_environment_manifest_schema"])
        self.assertFalse(audit["current_central_tolerance_registry"])
        self.assertTrue(audit["current_ci_one_thread_environment"])
        self.assertTrue(audit["current_ci_fixed_python_hash_seed"])
        self.assertFalse(audit["python310_complete_test_suite_qualified_now"])
        self.assertFalse(audit["python311_complete_test_suite_qualified_now"])
        self.assertFalse(audit["macos_complete_test_suite_qualified_now"])
        self.assertIn('requires-python = ">=3.10"', self.pyproject)
        self.assertIn('"Programming Language :: Python :: 3.10"', self.pyproject)
        self.assertIn('"Operating System :: OS Independent"', self.pyproject)
        self.assertEqual(self.ci.count("runs-on: ubuntu-latest"), 2)
        self.assertEqual(self.ci.count('python-version: "3.12"'), 2)
        self.assertNotIn("runs-on: macos", self.ci)
        self.assertNotIn("strategy:\n      matrix:", self.ci)

    def test_local_observation_is_diagnostic_only(self):
        local = self.boundary["current_support_audit"]["local_observed_environment"]
        self.assertEqual(local["status"], "diagnostic_only_not_supported_matrix_evidence")
        self.assertEqual(local["python"], "CPython 3.13.5")
        self.assertEqual(local["system"], "Darwin 25.6.0")
        self.assertEqual(local["machine"], "arm64")
        self.assertEqual(local["mne"], "1.12.1")
        self.assertIn(
            "tomllib", self.boundary["current_support_audit"]["python310_test_collection_warning"]
        )

    def test_qualification_environment_and_output_taxonomies_are_exact(self):
        self.assertEqual(len(self.boundary["qualification_levels"]), 7)
        self.assertEqual(
            [row["level_id"] for row in self.boundary["qualification_levels"]],
            [
                "L39-Q0_unavailable",
                "L39-Q1_contract_declared",
                "L39-Q2_same_process_repeatable",
                "L39-Q3_clean_root_same_host_repeatable",
                "L39-Q4_separate_host_same_cell_reproduced",
                "L39-Q5_supported_cross_platform_compatible",
                "L39-Q6_independent_team_reproduced",
            ],
        )
        self.assertEqual(len(self.boundary["environment_identity_fields"]), 18)
        self.assertEqual(len(self.boundary["output_classes"]), 8)
        self.assertEqual(len(self.boundary["comparison_classes"]), 6)
        combined = " ".join(self.boundary["environment_identity_fields"])
        for term in (
            "source_commit",
            "runner_image",
            "operating_system",
            "cpu_architecture",
            "python_implementation",
            "abi",
            "dependency_graph",
            "blas_lapack",
            "simd",
            "torch",
            "mne",
            "locale_timezone",
        ):
            self.assertIn(term, combined)

    def test_future_matrix_is_bounded_and_matches_declared_support(self):
        cells = self.boundary["future_required_matrix_cells"]
        self.assertEqual(len(cells), 6)
        self.assertEqual(
            [row["cell_id"] for row in cells],
            [
                f"L39-M{index}_" + suffix
                for index, suffix in enumerate(
                    (
                        "ubuntu2404_py310_base",
                        "ubuntu2404_py311_base",
                        "ubuntu2404_py312_base",
                        "macos15_py312_base",
                        "ubuntu2404_py312_neuro",
                        "macos15_py312_neuro",
                    ),
                    start=1,
                )
            ],
        )
        self.assertEqual({row["os"] for row in cells}, {"ubuntu-24.04", "macos-15"})
        self.assertEqual({row["profile"] for row in cells}, {"base", "optional_neuro"})
        base_pythons = {row["python"] for row in cells if row["profile"] == "base"}
        self.assertEqual(base_pythons, {"3.10", "3.11", "3.12"})
        self.assertTrue(all("latest" not in row["os"] for row in cells))

    def test_tolerance_policy_fails_closed(self):
        policy = self.boundary["tolerance_policy"]
        self.assertTrue(policy["central_registry_required"])
        self.assertFalse(policy["one_global_float_tolerance_allowed"])
        self.assertFalse(policy["semantic_fields_have_float_tolerance"])
        self.assertFalse(policy["shape_or_dtype_mismatch_can_pass_tolerance"])
        self.assertFalse(policy["nan_or_inf_is_implicit_equal"])
        self.assertTrue(policy["field_specific_max_abs_required"])
        self.assertTrue(policy["field_specific_max_rel_required"])
        self.assertTrue(policy["reference_hash_frozen_before_matrix_execution"])
        self.assertTrue(policy["tolerance_frozen_before_candidate_result_access"])
        self.assertFalse(policy["protected_or_consumed_data_may_set_tolerance"])
        self.assertFalse(policy["runtime_or_rss_may_select_semantic_winner"])

    def test_fixtures_stages_outcomes_and_claims_are_exact(self):
        self.assertEqual(len(self.boundary["future_fixture_families"]), 20)
        stages = self.boundary["future_stage_sequence"]
        self.assertEqual(len(stages), 4)
        self.assertTrue(all(row["separate_authorization_required"] for row in stages))
        self.assertEqual(len(self.boundary["outcome_taxonomy"]), 8)
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(claims), 7)
        self.assertEqual(claims[0]["status"], "current")
        self.assertEqual(claims[-2]["status"], "reserved_for_loop43")
        self.assertEqual(
            claims[-1]["status"],
            "reserved_for_independent_data_and_scientific_protocol",
        )

    def test_gates_and_refusals_cover_cross_machine_failures(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 28)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L39-G{index:02d}" for index in range(1, 29)],
        )
        self.assertEqual(len(refusals), 38)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L39-R{index:02d}" for index in range(1, 39)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "runner",
            "python",
            "workflow",
            "dependency",
            "wheel",
            "blas",
            "simd",
            "thread",
            "locale",
            "neural",
            "target",
            "training",
            "semantic_hash",
            "timestamp",
            "dtype",
            "float",
            "runtime",
            "artifact",
            "overclaim",
        ):
            self.assertIn(term, combined)

    def test_resources_and_access_counters_are_zero_and_bounded(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_max_parallel_matrix_jobs"], 2)
        self.assertEqual(resources["future_threads_per_job"], 1)
        self.assertEqual(resources["future_workers_per_job"], 1)
        self.assertEqual(resources["future_timeout_minutes_per_cell"], 20)
        self.assertEqual(resources["future_peak_rss_bytes_per_cell"], 1_073_741_824)
        self.assertEqual(resources["future_artifact_bytes_per_cell"], 4_194_304)
        self.assertEqual(resources["future_total_artifact_bytes"], 25_165_824)
        self.assertLessEqual(resources["future_total_artifact_bytes"], 32 * 1024 * 1024)
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_operations"], 6)
        self.assertEqual(counters["official_or_primary_pages_opened"], 8)
        for key, value in counters.items():
            if isinstance(value, int) and key not in {
                "high_level_public_web_operations",
                "official_or_primary_pages_opened",
            }:
                self.assertEqual(value, 0, key)

    def test_source_bindings_are_primary_and_complete(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 10)
        ids = {row["source_id"] for row in sources}
        self.assertEqual(
            ids,
            {
                "acm_artifact_badging",
                "reproducible_builds_definition",
                "python_hash_seed",
                "pip_inspect_schema",
                "pypa_pylock",
                "numpy_runtime_and_global_state",
                "pytorch_reproducibility",
                "github_hosted_runners",
                "mne_sys_info",
                "scientific_python_spec0",
            },
        )
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_research_document_contains_boundaries_and_closeout(self):
        for text in (
            "Loop 39 Primary-Source Research",
            "experiment `Not Started`",
            "six explicit Python",
            "Python 3.10",
            "`tomllib`",
            "There is no global `allclose` threshold",
            "maximum current claim",
            "Engineering capability added:",
            "Scientific claim not established:",
            "no cross-machine reproduction",
            "no fixture, environment manifest, matrix",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.19.0")
        current = self.roadmap["current_boundary"]
        self.assertTrue(current["loop39_research_packet_prepared"])
        self.assertEqual(current["loop39_qualification_level_count"], 7)
        self.assertEqual(current["loop39_environment_identity_field_count"], 18)
        self.assertEqual(current["loop39_output_class_count"], 8)
        self.assertEqual(current["loop39_comparison_class_count"], 6)
        self.assertEqual(current["loop39_required_matrix_cell_count"], 6)
        self.assertEqual(current["loop39_future_fixture_family_count"], 20)
        self.assertEqual(current["loop39_future_requirement_count"], 28)
        self.assertEqual(current["loop39_future_refusal_count"], 38)
        self.assertFalse(current["loop39_preregistration_prepared"])
        self.assertFalse(current["loop39_execution_authorized"])
        self.assertFalse(current["loop39_ci_matrix_authorized"])
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 39)
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["qualification_level_count"], 7)
        self.assertEqual(row["required_matrix_cell_count"], 6)
        for path, text in self.public_status.items():
            with self.subTest(path=path):
                self.assertIn("Loop 39", text)
                self.assertIn("planning research", text.lower())
                self.assertIn("Not Started", text)
                self.assertIn("unauthorized", text.lower())

    def test_no_loop39_runtime_or_workflow_matrix_was_added(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop39", source_text)
        self.assertNotIn("cross_machine_reproducibility_matrix", source_text)
        self.assertNotIn("strategy:\n      matrix:", self.ci)
        self.assertNotIn("runs-on: macos", self.ci)


if __name__ == "__main__":
    unittest.main()
