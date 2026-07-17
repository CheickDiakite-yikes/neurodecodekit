import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries" / "loop55_ai_research_policy.v0.json"
RESEARCH = ROOT / "docs" / "LOOP_55_AI_ASSISTED_REPRESENTATION_RESEARCH.md"
PUBLIC_STATUS = [
    ROOT / "README.md",
    ROOT / "START_HERE.md",
    ROOT / "AGENTS.md",
    ROOT / "docs" / "CODEX_HANDOFF.md",
    ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    ROOT / "prompts" / "CODEX_START_PROMPT.md",
]


class Loop55AIResearchPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.research = RESEARCH.read_text(encoding="utf-8")

    def test_identity_and_status_keep_real_experiment_closed(self):
        self.assertEqual(self.policy["schema_name"], "neurodecodekit.loop55_ai_research_policy")
        self.assertEqual(self.policy["schema_version"], 0)
        self.assertEqual(self.policy["loop_id"], 55)
        self.assertIn("synthetic_policy_tooling_eligible", self.policy["status"])
        self.assertIn("real_experiment_not_started", self.policy["status"])
        authorization = self.policy["authorization"]
        self.assertTrue(authorization["planning_research_authorized"])
        self.assertTrue(authorization["synthetic_policy_validator_implementation_authorized"])
        for field, value in authorization.items():
            if field not in {
                "planning_research_authorized",
                "synthetic_policy_validator_implementation_authorized",
                "synthetic_proposal_validation_authorized",
            }:
                self.assertFalse(value, field)

    def test_scientific_objective_is_fixed_before_ai_proposals(self):
        objective = self.policy["scientific_objective"]
        self.assertEqual(objective["fixed_primary_endpoint"], "L55-E1_causal_performed_hand")
        self.assertEqual(objective["fixed_secondary_endpoint"], "L55-E2_causal_performed_key_29")
        self.assertFalse(objective["positive_result_instruction_allowed"])
        self.assertFalse(objective["endpoint_selection_after_outcomes_allowed"])

    def test_agent_roles_separate_proposal_criticism_and_model_stage(self):
        roles = self.policy["agent_roles"]
        self.assertEqual([row["role_id"] for row in roles], ["L55-AI-R1", "L55-AI-R2", "L55-AI-R3"])
        self.assertFalse(roles[0]["may_execute_code"])
        self.assertFalse(roles[0]["may_change_endpoints"])
        self.assertFalse(roles[1]["may_replace_proposal"])
        self.assertFalse(roles[2]["performed_labels_or_text_allowed_during_warmup"])
        self.assertFalse(roles[2]["current_execution_authorized"])

    def test_only_synthetic_policy_phase_is_eligible(self):
        phases = self.policy["phase_sequence"]
        self.assertEqual([row["phase_id"] for row in phases], ["L55-AI-A", "L55-AI-B", "L55-AI-C"])
        self.assertEqual([row["eligible_now"] for row in phases], [True, False, False])
        self.assertEqual(phases[0]["claim_ceiling"], "governance_mechanics_only")
        self.assertIn("separate_exact_Tier_C_decision_green", phases[2]["requires"])

    def test_proposal_contract_is_strict_causal_small_and_language_free(self):
        contract = self.policy["proposal_contract"]
        self.assertEqual(contract["proposal_schema_name"], "neurodecodekit.ai_research_proposal")
        self.assertEqual(contract["proposal_schema_version"], 0)
        self.assertEqual(contract["required_top_level_fields"], contract["allowed_top_level_fields"])
        self.assertEqual(contract["required_input_window_ms"], [-500, 0])
        self.assertTrue(contract["right_endpoint_exclusive_required"])
        self.assertTrue(contract["producer_causal_required"])
        self.assertEqual(contract["right_context_ms_required"], 0)
        self.assertEqual(contract["maximum_trainable_parameters"], 10000)
        self.assertIn("masked_reconstruction", contract["allowed_pretraining_objectives"])
        self.assertIn("contrastive_next_window", contract["allowed_pretraining_objectives"])
        self.assertEqual(
            set(contract["required_false_recipe_fields"]),
            {
                "uses_target_text",
                "uses_performed_labels_during_pretraining",
                "uses_pretrained_weights",
                "uses_language_model",
            },
        )

    def test_synthetic_budget_has_no_model_or_training_run(self):
        caps = self.policy["proposal_contract"]["synthetic_budget_caps"]
        self.assertEqual(caps["proposal_round_maximum"], 4)
        self.assertEqual(caps["parameter_update_runs"], 0)
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertLessEqual(caps["maximum_runtime_seconds"], 30)
        self.assertLessEqual(caps["maximum_peak_rss_bytes"], 256 * 1024**2)
        self.assertLessEqual(caps["maximum_generated_output_bytes"], 1024**2)

    def test_future_fit_budget_preserves_twelve_run_ceiling(self):
        budget = self.policy["future_fit_budget_recommendation"]
        allocated = sum(
            value
            for key, value in budget.items()
            if key.startswith("maximum_") and key != "maximum_total_parameter_update_runs"
        )
        self.assertEqual(budget["maximum_total_parameter_update_runs"], 12)
        self.assertEqual(allocated, 12)
        self.assertLessEqual(budget["maximum_ai_guided_train_inner_proposal_runs"], 4)
        self.assertFalse(budget["unused_capacity_authorizes_extra_work"])
        self.assertTrue(budget["trained_control_need_reduces_ai_rounds_before_total_can_expand"])

    def test_agent_visibility_excludes_protected_and_outcome_bearing_content(self):
        firewall = self.policy["future_real_visibility_firewall"]
        forbidden = set(firewall["agent_may_not_receive"])
        for field in (
            "raw_or_windowed_EEG_values",
            "individual_key_or_hand_labels",
            "intended_or_typed_text",
            "selection_or_final_metrics",
            "selection_or_final_predictions_or_targets",
        ):
            self.assertIn(field, forbidden)
        self.assertIn("obtain_a_positive_result", firewall["agent_may_not_be_instructed_to"])

    def test_access_counters_and_claims_remain_zero_or_unavailable(self):
        counters = self.policy["current_access_counters"]
        for field, value in counters.items():
            if field not in {"public_primary_source_pages_consulted", "committed_research_boundaries_read"}:
                self.assertEqual(value, 0, field)
        unavailable = set(self.policy["current_unavailable_fields"])
        self.assertIn("EEG_hand_or_key_effect", unavailable)
        self.assertIn("brain_specific_origin", unavailable)
        self.assertIn("generalization", unavailable)

    def test_research_document_keeps_positive_target_separate_from_outcome(self):
        for phrase in (
            "planning research addendum complete",
            "real experiment `Not Started`",
            "AI does not choose the scientific question",
            "at most four train-inner AI proposal rounds",
            "The optimization target must be a preregistered train-inner decision statistic",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.research)

    def test_public_status_surfaces_disclose_synthetic_only_ai_boundary(self):
        for path in PUBLIC_STATUS:
            with self.subTest(path=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("AI", content)
                self.assertIn("synthetic", content.lower())
                self.assertIn("Loop 55", content)


if __name__ == "__main__":
    unittest.main()
