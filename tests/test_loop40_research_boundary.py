import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop40_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_40_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
CI_PATH = REPO_ROOT / ".github" / "workflows" / "ci.yml"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "CODEX_NEXT_20_LOOPS_PROMPT.md",
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


class Loop40ResearchBoundaryTests(unittest.TestCase):
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
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop40_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["loop_id"], 40)
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 40)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_keeps_backend_target_and_claims_unselected(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L40-C0_no_edge_package_result")
        self.assertFalse(decision["backend_selected_now"])
        self.assertFalse(decision["target_platform_selected_now"])
        self.assertFalse(decision["target_architecture_selected_now"])
        self.assertEqual(decision["leading_future_research_candidate"], "executorch_xnnpack")
        self.assertEqual(decision["leading_candidate_status"], "research_lead_only_not_selected")
        self.assertTrue(decision["physical_device_claim_requires_loop42"])
        self.assertFalse(decision["portable_hardware_claim_available_in_loop40"])
        self.assertFalse(decision["end_to_end_latency_measured_now"])
        self.assertFalse(decision["package_export_is_scientific_validation"])

    def test_dependencies_fail_closed(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop24_result_available_now"])
        self.assertTrue(dependencies["loop24_float32_reference_retained"])
        self.assertFalse(dependencies["loop24_overall_gate_passed"])
        self.assertFalse(dependencies["loop24_selection_seed_may_be_reopened"])
        self.assertFalse(dependencies["loop24_qualification_seed_may_be_opened"])
        self.assertTrue(dependencies["loop39_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop39_required_matrix_executed_now"])
        self.assertTrue(
            dependencies["loop39_relevant_matrix_pass_required_before_export_qualification"]
        )
        self.assertTrue(dependencies["named_target_required_before_backend_selection"])
        self.assertTrue(dependencies["loop42_required_before_physical_device_claim"])
        self.assertFalse(dependencies["general_continuation_is_execution_authorization"])

    def test_reference_audit_matches_frozen_local_source(self):
        reference = self.boundary["current_reference_audit"]
        self.assertEqual(reference["parameter_count"], 1130)
        self.assertEqual(reference["encoder_parameter_count"], 1076)
        self.assertEqual(reference["diagnostic_probe_parameter_count"], 54)
        self.assertEqual(reference["registered_float32_numeric_payload_bytes"], 5210)
        self.assertEqual(reference["frame_channels"], 5)
        self.assertEqual(reference["frame_samples"], 16)
        self.assertEqual(reference["flattened_input_features"], 80)
        self.assertEqual(reference["hidden_features"], 12)
        self.assertEqual(reference["embedding_features"], 8)
        self.assertEqual(reference["diagnostic_logit_features"], 6)
        self.assertEqual(reference["canonical_batch_size"], 1)
        self.assertEqual(reference["registered_dtype"], "float32")
        self.assertTrue(reference["producer_causal"])
        self.assertFalse(reference["host_streaming_state_inside_torch_graph"])
        self.assertFalse(reference["timestamps_inside_torch_graph"])
        self.assertFalse(reference["decoder_inside_torch_graph"])
        self.assertEqual(reference["current_export_eligibility"], "blocked")
        self.assertEqual(len(reference["blocking_reasons"]), 4)

    def test_loop24_evidence_is_pinned_without_reopening(self):
        evidence = self.boundary["loop24_evidence_pin"]
        self.assertEqual(evidence["selection_seed"], 2401)
        self.assertEqual(evidence["qualification_seed"], 2402)
        self.assertIn("consumed", evidence["selection_seed_status"])
        self.assertIn("unopened", evidence["qualification_seed_status"])
        self.assertEqual(evidence["float32_reference_status"], "retained")
        self.assertEqual(evidence["float16_producer_latency_ratio"], 1.16995)
        self.assertEqual(evidence["qint8_numeric_payload_ratio"], 0.471)
        self.assertEqual(evidence["selection_orchestration_runtime_sec"], 65.154951)
        self.assertEqual(evidence["registered_runtime_cap_sec"], 60)
        self.assertEqual(evidence["overall_outcome"], "parked_retain_float32")

    def test_taxonomies_are_exact_and_keep_host_state_separate(self):
        self.assertEqual(len(self.boundary["qualification_levels"]), 7)
        self.assertEqual(len(self.boundary["package_layers"]), 6)
        self.assertEqual(len(self.boundary["backend_profiles"]), 4)
        self.assertEqual(len(self.boundary["package_identity_fields"]), 20)
        self.assertEqual(len(self.boundary["output_classes"]), 8)
        self.assertEqual(len(self.boundary["comparison_classes"]), 6)
        self.assertEqual(len(self.boundary["future_fixture_families"]), 24)
        self.assertEqual(len(self.boundary["future_stage_sequence"]), 4)
        self.assertEqual(len(self.boundary["outcome_taxonomy"]), 8)
        self.assertEqual(len(self.boundary["claim_taxonomy"]), 7)
        combined = " ".join(self.boundary["package_identity_fields"])
        for term in (
            "target_os",
            "runtime_binary",
            "operator_set",
            "fallback",
            "host_normalization",
            "timestamp",
            "causal",
            "thermal",
            "claim_ceiling",
        ):
            self.assertIn(term, combined)
        self.assertTrue(
            all(
                row["separate_authorization_required"]
                for row in self.boundary["future_stage_sequence"]
            )
        )

    def test_backend_profiles_preserve_four_real_options(self):
        profiles = self.boundary["backend_profiles"]
        self.assertEqual(
            [row["backend_id"] for row in profiles],
            [
                "executorch_xnnpack",
                "onnx_runtime_mobile_xnnpack_or_cpu",
                "litert_torch",
                "coreml_mlprogram",
            ],
        )
        self.assertEqual(profiles[0]["status"], "leading_future_research_candidate_not_selected")
        self.assertTrue(all("not_selected" in row["status"] for row in profiles))
        self.assertIn("float16", profiles[-1]["unresolved"])

    def test_gates_and_refusals_cover_package_failures(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 30)
        self.assertEqual(
            [row["requirement_id"] for row in gates],
            [f"L40-G{index:02d}" for index in range(1, 31)],
        )
        self.assertEqual(len(refusals), 40)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L40-R{index:02d}" for index in range(1, 41)],
        )
        combined = " ".join(refusals)
        for term in (
            "authorization",
            "loop39",
            "target_platform",
            "backend",
            "install",
            "protected",
            "operator",
            "fallback",
            "dtype",
            "timestamp",
            "hash",
            "runtime",
            "rss",
            "thermal",
            "portable",
            "scientific",
        ):
            self.assertIn(term, combined)

    def test_resources_and_access_are_zero_and_bounded(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_selected_backend_count"], 1)
        self.assertEqual(resources["future_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_timeout_sec_per_measurement_worker"], 60)
        self.assertEqual(resources["future_peak_rss_bytes"], 1_073_741_824)
        self.assertEqual(resources["future_total_generated_package_and_report_bytes"], 33_554_432)
        self.assertEqual(resources["network_default"], "off")
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_operations"], 3)
        self.assertEqual(counters["official_or_primary_pages_opened"], 12)
        for key, value in counters.items():
            if isinstance(value, int) and key not in {
                "high_level_public_web_operations",
                "official_or_primary_pages_opened",
            }:
                self.assertEqual(value, 0, key)

    def test_sources_are_official_and_complete(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 11)
        ids = {row["source_id"] for row in sources}
        self.assertEqual(
            ids,
            {
                "executorch_overview",
                "executorch_getting_started",
                "executorch_memory_planning",
                "executorch_delegates",
                "executorch_runtime",
                "onnx_runtime_mobile",
                "onnx_runtime_ort_format",
                "onnx_runtime_fixed_shape",
                "litert_pytorch_conversion",
                "coreml_conversion_formats",
                "coreml_input_output_types",
            },
        )
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))

    def test_research_document_contains_boundaries_and_closeout(self):
        for text in (
            "Loop 40 Primary-Source Research",
            "experiment is `Not Started`",
            "1,130 total",
            "5,210 bytes",
            "leading future research candidate only",
            "No backend",
            "six layers",
            "40 false execution",
            "Engineering capability added:",
            "Scientific claim not established:",
            "no neural advantage",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.20.0")
        current = self.roadmap["current_boundary"]
        self.assertTrue(current["loop40_research_packet_prepared"])
        self.assertEqual(current["loop40_qualification_level_count"], 7)
        self.assertEqual(current["loop40_package_layer_count"], 6)
        self.assertEqual(current["loop40_backend_profile_count"], 4)
        self.assertEqual(current["loop40_package_identity_field_count"], 20)
        self.assertEqual(current["loop40_future_fixture_family_count"], 24)
        self.assertEqual(current["loop40_future_requirement_count"], 30)
        self.assertEqual(current["loop40_future_refusal_count"], 40)
        self.assertFalse(current["loop40_backend_selected"])
        self.assertFalse(current["loop40_preregistration_prepared"])
        self.assertFalse(current["loop40_execution_authorized"])
        self.assertFalse(current["loop40_optional_install_authorized"])
        self.assertFalse(current["loop40_package_generation_authorized"])
        self.assertFalse(current["loop40_dependency_loop39_execution_satisfied"])
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 40)
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(row["proof_posture"], "planning_research_complete_experiment_not_started")
        self.assertFalse(row["backend_selected"])
        self.assertFalse(row["preregistration_prepared"])
        self.assertFalse(row["execution_authorized"])
        for path, text in self.public_status.items():
            with self.subTest(path=path):
                self.assertIn("Loop 40", text)
                self.assertIn("planning research", text.lower())
                self.assertIn("Not Started", text)
                self.assertIn("unauthorized", text.lower())

    def test_no_loop40_runtime_dependency_or_package_was_added(self):
        source_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in (REPO_ROOT / "src").rglob("*.py")
        ).lower()
        self.assertNotIn("loop40", source_text)
        self.assertNotIn("executorch", source_text)
        self.assertNotIn("onnxruntime", source_text)
        self.assertNotIn("litert", source_text)
        self.assertNotIn("coremltools", source_text)
        pyproject_lower = self.pyproject.lower()
        for dependency in ("executorch", "onnxruntime", "litert", "coremltools"):
            self.assertNotIn(dependency, pyproject_lower)
        tracked_package_suffixes = {".pte", ".onnx", ".ort", ".tflite", ".mlmodel", ".mlpackage"}
        tracked = [
            path
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in tracked_package_suffixes
            and ".git" not in path.parts
        ]
        self.assertEqual(tracked, [])
        self.assertNotIn("executorch", self.ci.lower())


if __name__ == "__main__":
    unittest.main()
