import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop55_eeg_neural_effect_research.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_55_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "BUILD_NOTES.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "DECISIONS.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
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


class Loop55EEGNeuralEffectResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_planning_only_and_execution_is_unauthorized(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop55_eeg_neural_effect_research",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["loop_id"], 55)
        self.assertEqual(registry["current_experiment_status"], "Not Started")
        self.assertIn("loop54_dependent", registry["status"])
        flags = authorization_flags(registry)
        self.assertEqual(flags[0], ("planning_research_authorized_now", True))
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(registry["authorization"]["separate_exact_tier_c_decisions_required"])

    def test_dependencies_are_hash_bound_and_unavailable(self):
        dependencies = self.registry["dependencies"]
        expected = {
            "loop53_contract_sha256": "bc7d86a1ce6ef3dc71dacca0af97cb5813df87620ac35d4f34ecd343f97e65ac",
            "loop54_research_sha256": "ab158abf5b7425c63c66e201ed341c096b9a622aff0eef8ba1b3bdeacf7f5ec7",
            "loop31_research_sha256": "5d7ae8ab0ad7f9a4023874b0317be21174ace9cc037438c319546b4c46c1c7c1",
            "loop35_research_sha256": "b68e0721ed964138feb608af404f8e80bc80fa94418215b7efe914cd93de5fcf",
            "loop48_hypothesis_sha256": "22f6a99801d7fc9259501b43a032078e584544a54581b7a1bd1eabc4c321af60",
        }
        for key, value in expected.items():
            self.assertEqual(dependencies[key], value, key)
        self.assertFalse(dependencies["loop53_complete_now"])
        self.assertFalse(dependencies["loop54_required_claim_class_available_now"])
        self.assertTrue(dependencies["S7_consumed_and_forbidden"])
        self.assertTrue(dependencies["S21_S24_S25_forbidden"])

    def test_sources_and_hypotheses_are_complete_and_ordered(self):
        findings = self.registry["primary_source_findings"]
        sources = self.registry["source_bindings"]
        hypotheses = self.registry["hypothesis_portfolio"]
        self.assertEqual(len(findings), 6)
        self.assertEqual(len(sources), 6)
        self.assertEqual(
            [row["finding_id"] for row in findings],
            [f"L55-S{index:02d}" for index in range(1, 7)],
        )
        self.assertEqual(
            [row["hypothesis_id"] for row in hypotheses],
            [f"L55-H{index}" for index in range(7)],
        )
        combined = " ".join(row["finding"] for row in findings)
        for phrase in ("-200 to +300 ms", "performed action", "EEGNet", "null data", "biological replicates"):
            self.assertIn(phrase, combined)

    def test_causal_hand_and_key_endpoints_are_noninterchangeable(self):
        hand, key, diagnostic = self.registry["ordered_endpoints"]
        self.assertEqual((hand["endpoint_id"], key["endpoint_id"]), ("L55-E1", "L55-E2"))
        self.assertEqual(hand["target"], "performed_hand_2")
        self.assertEqual(key["target"], "performed_key_29")
        for endpoint in (hand, key):
            self.assertEqual(endpoint["input_window_recommendation_ms"], [-500, 0])
            self.assertTrue(endpoint["right_endpoint_exclusive"])
            self.assertTrue(endpoint["producer_causal_required"])
            self.assertEqual(endpoint["right_context_ms"], 0)
            self.assertTrue(endpoint["complete_required_control_conjunction"])
        self.assertTrue(key["known_event_onsets_and_output_count_disclosed"])
        self.assertFalse(key["insertions_deletions_or_event_detection_tested"])
        self.assertEqual(diagnostic["input_window_ms"], [-200, 300])
        self.assertFalse(diagnostic["producer_causal"])
        self.assertFalse(diagnostic["may_rescue_or_upgrade_causal_endpoint"])

    def test_target_feature_firewall_uses_performed_action_not_intended_text(self):
        firewall = self.registry["target_and_feature_firewall"]
        self.assertEqual(
            [row["target_id"] for row in firewall["primary_targets"]],
            ["performed_key_29", "performed_hand_2"],
        )
        self.assertEqual(firewall["secondary_target"]["target_id"], "intended_sentence")
        self.assertFalse(firewall["secondary_target"]["available_to_primary_fit_or_selection"])
        self.assertFalse(firewall["secondary_target"]["may_upgrade_hand_or_key_claim"])
        forbidden = " ".join(firewall["primary_model_forbidden_inputs"])
        for phrase in ("marker type", "keypress identity", "target sentence", "future sample", "language model"):
            self.assertIn(phrase, forbidden)
        self.assertFalse(firewall["silent_post_target_event_drop_allowed"])

    def test_split_is_trial_level_grouped_and_deferred(self):
        split = self.registry["future_split_recommendation"]
        self.assertIn("not_frozen", split["status"])
        self.assertEqual(split["minimum_usable_unique_trials"], 48)
        self.assertTrue(split["trial_is_identity_and_inference_unit"])
        self.assertFalse(split["event_windows_are_independent_trials"])
        self.assertEqual(split["if_usable_count_below_48"], "park_without_split_or_training")
        self.assertEqual(split["if_usable_count_48_to_59"]["selection_trials"], 8)
        self.assertEqual(split["if_usable_count_at_least_60"]["final_trials"], 10)
        self.assertEqual(
            split["expected_but_unverified_count_64_example"],
            {"train_trials": 44, "selection_trials": 10, "final_trials": 10},
        )
        self.assertTrue(split["same_trial_events_stay_together"])
        self.assertTrue(split["exact_and_semantically_similar_intended_texts_stay_together"])
        self.assertTrue(split["isolated_target_bearing_grouper_required"])
        self.assertFalse(split["target_values_class_frequencies_signal_quality_or_model_behavior_may_choose_partition"])

    def test_model_family_is_small_causal_and_language_free(self):
        model = self.registry["future_model_recommendation"]
        self.assertIn("recommendation_only", model["status"])
        self.assertEqual(model["maximum_trainable_parameters_per_model"], 10000)
        self.assertEqual(model["output_heads"], ["performed_key_29", "performed_hand_2"])
        self.assertEqual(model["maximum_nonselectable_stability_seed_count"], 2)
        self.assertEqual(model["maximum_parameter_update_runs_recommendation"], 12)
        forbidden = set(model["forbidden_components"])
        self.assertTrue({"language model", "LLM", "pretrained weights"}.issubset(forbidden))
        transforms = " ".join(model["transform_requirements"])
        for phrase in ("train-only", "zero right context", "no zero-phase", "causal anti-aliasing"):
            self.assertIn(phrase, transforms)

    def test_condition_matrix_covers_signal_timing_peripheral_and_diagnostic_routes(self):
        conditions = self.registry["required_condition_matrix"]
        self.assertEqual(len(conditions), 12)
        self.assertEqual(
            [row["condition_id"] for row in conditions],
            [f"L55-E{index:02d}" for index in range(12)],
        )
        required = [row for row in conditions if row["required_for_causal_claim"] is True]
        self.assertEqual(len(required), 8)
        eog = conditions[8]
        self.assertEqual(eog["required_for_causal_claim"], "if_Loop54_qualifies_ocular_channels")
        self.assertFalse(conditions[9]["required_for_causal_claim"])
        self.assertFalse(conditions[10]["required_for_causal_claim"])
        self.assertFalse(conditions[11]["may_rescue_causal_failure"])

    def test_exact_trial_level_conjunction_and_one_shot_access_are_required(self):
        stats = self.registry["statistical_decision_recommendation"]
        self.assertEqual(stats["paired_unit"], "same_unique_final_performed_trial")
        self.assertEqual(stats["component_test"], "exact_one_sided_paired_sign_flip_enumeration")
        self.assertEqual(stats["assignments_with_ten_nonzero_pairs"], 1024)
        self.assertEqual(stats["component_alpha"], 0.05)
        self.assertTrue(stats["overall_claim_requires_every_component_pass"])
        self.assertFalse(stats["individual_component_claims_allowed"])
        self.assertFalse(stats["control_tie_passes"])
        sequence = self.registry["future_access_sequence"]
        self.assertEqual([row["order"] for row in sequence], list(range(1, 11)))
        self.assertEqual(sequence[-2]["stage"], "commit_push_and_remote_green_hash_only_freeze")
        self.assertEqual(sequence[-1]["stage"], "one_shot_isolated_final_scoring")
        self.assertIn("no rerun", sequence[-1]["boundary"])

    def test_resources_refusals_and_current_access_are_bounded(self):
        resources = self.registry["resource_boundaries"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertLessEqual(resources["maximum_trainable_parameters_per_model"], 10000)
        self.assertLessEqual(resources["maximum_parameter_update_runs"], 12)
        self.assertLessEqual(resources["maximum_total_cpu_seconds"], 45 * 60)
        self.assertLessEqual(resources["maximum_peak_rss_bytes"], 1024**3)
        self.assertLessEqual(resources["maximum_generated_output_bytes_including_protected_derivatives"], 64 * 1024**2)
        self.assertEqual(resources["new_download_bytes"], 0)
        self.assertEqual(len(self.registry["future_acceptance_gates"]), 30)
        refusals = self.registry["future_refusal_ids"]
        self.assertEqual(len(refusals), 36)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L55-F{index:02d}" for index in range(1, 37)],
        )
        counters = self.registry["research_access_counters"]
        for key, value in counters.items():
            if key not in {"primary_source_pages_consulted", "committed_research_boundaries_read"}:
                self.assertEqual(value, 0, key)

    def test_claims_and_research_doc_keep_science_unavailable(self):
        claims = self.registry["claim_taxonomy"]
        self.assertEqual(len(claims), 8)
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        for phrase in (
            "planning research complete",
            "experiment `Not Started`",
            "causal hand endpoint",
            "causal key endpoint",
            "performed keys, not corrected intended text",
            "1,024",
            "at most 12 parameter-update runs",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.research)

    def test_scientific_roadmap_marks_research_complete_but_execution_unauthorized(self):
        loop55 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 55)
        self.assertEqual(loop55["status"], "Planning Research Complete; Loop 54 Dependent")
        self.assertFalse(loop55["execution_authorized"])
        self.assertIn("loop55_eeg_neural_effect_research.v0.json", loop55["build_deliverable"])
        self.assertIn("performed-hand", loop55["scientific_claim_target"])
        self.assertIn("separate exact Tier C", loop55["authorization_boundary"])

    def test_public_status_surfaces_share_the_loop55_boundary(self):
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 55", content)
                self.assertIn("performed", content.lower())
                self.assertIn("causal", content.lower())
                self.assertIn("authoriz", content.lower())


if __name__ == "__main__":
    unittest.main()
