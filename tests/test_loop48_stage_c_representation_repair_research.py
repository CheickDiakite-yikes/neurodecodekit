import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop48_stage_c_representation_repair_research.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md"
PUBLIC_PATHS = (
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


class Loop48StageCRepresentationRepairResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_status_is_research_only_and_protected_work_is_false(self):
        self.assertEqual(
            self.registry["status"],
            "planning_research_complete_synthetic_calibration_not_started_protected_execution_unauthorized",
        )
        self.assertFalse(self.registry["authorized_now"])
        authorization = self.registry["authorization"]
        self.assertTrue(authorization["tier_a_research_and_documentation_authorized_now"])
        for key, value in authorization.items():
            if key.endswith("authorized_now") and key not in {
                "tier_a_research_and_documentation_authorized_now"
            }:
                self.assertFalse(value, key)

    def test_dependency_hashes_match_current_tracked_sources(self):
        for row in self.registry["dependency_bindings"].values():
            path = REPO_ROOT / row["path"]
            self.assertTrue(path.is_file(), row["path"])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])

    def test_candidate_parameter_math_context_and_causality_are_exact(self):
        model = self.registry["candidate_architecture"]
        expected = (
            model["spatial_projection"]["parameters"]
            + model["residual_temporal_blocks"]["parameters_total"]
            + model["temporal_reducer"]["parameters"]
            + model["ctc_head"]["parameters"]
        )
        self.assertEqual(expected, 7692)
        self.assertEqual(model["trainable_parameters"], expected)
        self.assertLess(model["trainable_parameters"], model["parameter_ceiling"])
        self.assertEqual(model["source_receptive_field_frames"], 48)
        self.assertEqual(model["required_left_context_frames"], 47)
        self.assertEqual(model["required_left_context_ms"], 470)
        self.assertEqual(model["right_context_frames"], 0)
        self.assertEqual(model["output_sampling_rate_hz"], 25)
        self.assertFalse(model["residual_temporal_blocks"]["normalization_may_aggregate_over_time"])
        for forbidden in (
            "conformer",
            "attention",
            "recurrence",
            "participant_identity_input",
            "geometry_conditioned_merger",
            "language_model",
            "neurotoken_semantic_target",
        ):
            self.assertFalse(model[forbidden], forbidden)

    def test_ablation_is_near_parameter_matched_and_zero_context(self):
        model = self.registry["candidate_architecture"]
        ablation = self.registry["parameter_matched_ablation"]
        expected = (
            ablation["spatial_projection_parameters"]
            + ablation["residual_and_layer_norm_parameters_total"]
            + ablation["depthwise_kernel1_stride4_parameters"]
            + ablation["ctc_head_parameters"]
        )
        self.assertEqual(expected, 7568)
        self.assertEqual(ablation["trainable_parameters"], expected)
        self.assertEqual(model["trainable_parameters"] - expected, 124)
        self.assertLessEqual(
            ablation["absolute_parameter_gap_fraction_of_candidate"],
            ablation["maximum_parameter_gap_fraction"],
        )
        self.assertEqual(ablation["required_left_context_frames"], 0)
        self.assertEqual(ablation["right_context_frames"], 0)
        self.assertEqual(ablation["output_sampling_rate_hz"], 25)

    def test_synthetic_plan_is_bounded_and_has_one_final_open(self):
        plan = self.registry["synthetic_calibration_plan"]
        self.assertEqual(plan["status"], "frozen_plan_not_implemented_not_executed")
        self.assertEqual(plan["partitions"], {"train": 24, "selection": 8, "final": 8})
        self.assertEqual(len(plan["optimizer_recipes"]), 3)
        self.assertEqual(plan["total_parameter_update_runs"], 4)
        self.assertEqual(plan["final_openings"], 1)
        self.assertEqual(plan["shared_settings"]["cpu_threads"], 1)
        self.assertEqual(plan["shared_settings"]["workers"], 1)
        self.assertEqual(plan["shared_settings"]["restarts"], 0)
        self.assertLessEqual(plan["resource_caps"]["peak_rss_bytes"], 1024**3)
        self.assertLessEqual(plan["resource_caps"]["generated_artifact_bytes"], 16 * 1024**2)
        self.assertEqual(plan["resource_caps"]["new_real_data_download_bytes"], 0)

    def test_future_protected_recommendation_excludes_consumed_and_final_rows(self):
        future = self.registry["future_protected_diagnostic_recommendation"]
        self.assertEqual(future["status"], "design_recommendation_not_preregistered_not_authorized")
        self.assertEqual(future["allowed_rows_recommended"], "the_44_stage_b_fit_rows_only")
        for key in (
            "consumed_stage_b_check_rows_recommended",
            "validation_rows_recommended",
            "source_test_rows_recommended",
            "session2_rows_recommended",
            "s24_rows_recommended",
            "s25_rows_recommended",
        ):
            self.assertEqual(future[key], 0, key)
        self.assertEqual(future["candidate_out_of_fold_fits"], 15)
        self.assertEqual(future["ablation_out_of_fold_fits"], 5)
        self.assertEqual(future["total_parameter_update_runs"], 20)

    def test_operation_counters_show_no_protected_or_model_work(self):
        counters = self.registry["planning_operation_counters"]
        self.assertEqual(counters["git_tracked_stage_b_result_reads"], 1)
        self.assertEqual(counters["git_tracked_loop10_report_reads"], 1)
        for key, value in counters.items():
            if key in {
                "git_tracked_stage_b_result_reads",
                "git_tracked_loop10_report_reads",
                "external_research_wire_bytes",
            }:
                continue
            self.assertEqual(value, 0, key)
        self.assertEqual(counters["external_research_wire_bytes"], "unavailable_by_tool_contract")

    def test_sources_have_transfer_limits_and_doc_preserves_claim_boundary(self):
        sources = self.registry["primary_source_bindings"]
        self.assertEqual(len(sources), 7)
        self.assertEqual(len({row["source_id"] for row in sources}), 7)
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        self.assertTrue(all(row["transfer_limit"] for row in sources))
        normalized = " ".join(self.doc.split())
        for phrase in (
            "temporal-context-starvation hypothesis",
            "7,692",
            "7,568",
            "470 ms",
            "Scientific claim not established",
            "no model was implemented or run",
        ):
            self.assertIn(phrase, normalized)

    def test_router_never_automatically_opens_s24_or_s25(self):
        router = self.registry["outcome_router"]
        self.assertEqual(
            [row["route_id"] for row in router],
            [
                "L48C-R01",
                "L48C-R02",
                "L48C-R03",
                "L48C-R04",
                "L48C-R05",
            ],
        )
        joined = " ".join(row["action"] for row in router)
        self.assertIn("preparation_not_execution", joined)
        self.assertNotIn("open_s25", joined)
        self.assertNotIn("download_s24", joined)

    def test_public_handoff_surfaces_reference_stage_c_boundary(self):
        for path in PUBLIC_PATHS:
            text = path.read_text(encoding="utf-8")
            self.assertIn("LOOP_48_STAGE_C_REPRESENTATION_REPAIR_RESEARCH.md", text, path)
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("470 ms causal temporal encoder", readme)
        self.assertIn("synthetic mechanics", readme)


if __name__ == "__main__":
    unittest.main()
