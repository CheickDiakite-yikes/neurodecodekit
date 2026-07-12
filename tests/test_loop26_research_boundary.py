import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop26_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_26_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"


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


class Loop26ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))

    def test_identity_is_research_only_and_every_authorization_flag_is_false(self):
        boundary = self.boundary
        self.assertEqual(
            boundary["schema_name"], "neurodecodekit.loop26_research_boundary"
        )
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(
            boundary["status"],
            "planning_research_complete_preregistration_blocked_on_loop25",
        )
        self.assertEqual(
            boundary["proof_posture"],
            "planning_only_no_data_target_model_training_or_execution",
        )
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 14)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_loop25_dependency_and_future_authorization_are_not_satisfied(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop25_required"])
        self.assertFalse(dependencies["loop25_dependency_satisfied"])
        self.assertTrue(dependencies["loop25_compatible_result_required"])
        self.assertTrue(
            dependencies[
                "separate_real_cache_target_training_and_validation_authorization_required"
            ]
        )
        self.assertFalse(dependencies["loop26_preregistration_prepared"])
        self.assertFalse(dependencies["loop26_authorization_request_prepared"])

    def test_local_split_and_consumed_evidence_boundaries_are_exact(self):
        local = self.boundary["local_evidence"]
        self.assertEqual(
            (
                local["source_train_rows"],
                local["source_validation_rows"],
                local["source_test_rows"],
            ),
            (55, 6, 5),
        )
        self.assertEqual(local["canonical_person_group_count"], 1)
        self.assertEqual(local["session_group_count"], 1)
        self.assertIn("reserved", local["source_validation_status"])
        self.assertIn("consumed", local["source_test_status"])
        self.assertIn("consumed", local["session2_status"])
        self.assertEqual(local["scaler_fit_split"], "train")
        self.assertEqual(local["scaler_fit_rows"], 55)
        self.assertFalse(local["source_cache_content_opened_this_research_pass"])
        self.assertFalse(local["target_content_opened_this_research_pass"])

    def test_existing_model_mismatch_and_candidate_parameter_math_are_exact(self):
        local = self.boundary["local_evidence"]
        existing = local["existing_real_model"]
        self.assertEqual(existing["parameter_count"], 2908)
        self.assertFalse(existing["causal"])
        self.assertIn("symmetric_padding", existing["noncausal_reason"])
        synthetic = local["existing_causal_model"]
        self.assertEqual(synthetic["parameter_count"], 1130)
        self.assertFalse(synthetic["real_text_compatible"])

        candidate = self.boundary["candidate_architecture_recommendation"]
        calculated = (102 * 16 + 16) + (16 * 16 * 3 + 16) + (16 * 28 + 28)
        self.assertEqual(calculated, 2908)
        self.assertEqual(candidate["parameter_count"], calculated)
        self.assertEqual(candidate["right_context_samples"], 0)
        self.assertEqual(candidate["history_samples"], 2)
        self.assertEqual(candidate["mutable_model_state_bytes_float32"], 128)
        self.assertFalse(candidate["implementation_exists"])
        self.assertFalse(candidate["measured_causality_result_exists"])

    def test_linear_comparator_is_nearly_parameter_matched(self):
        comparator = self.boundary["linear_comparator_recommendation"]
        calculated = 102 * 28 + 28
        self.assertEqual(calculated, 2884)
        self.assertEqual(comparator["parameter_count"], calculated)
        self.assertEqual(comparator["parameter_difference_from_candidate"], 24)
        self.assertAlmostEqual(
            comparator["parameter_difference_fraction"], 24 / 2908, places=15
        )
        self.assertFalse(comparator["implementation_exists"])

    def test_six_item_exact_inference_resolution_is_machine_checkable(self):
        identifiability = self.boundary["identifiability"]
        self.assertEqual(identifiability["validation_items"], 6)
        self.assertEqual(identifiability["exact_paired_sign_assignments"], 2**6)
        self.assertEqual(
            identifiability["minimum_attainable_one_sided_p"], 1 / (2**6)
        )
        self.assertEqual(
            identifiability["minimum_attainable_two_sided_p"], 2 / (2**6)
        )
        self.assertEqual(
            identifiability["minimum_two_sided_p_after_one_zero_difference"],
            2 / (2**5),
        )
        self.assertEqual(
            identifiability["exact_ordered_paired_bootstrap_index_resamples"],
            6**6,
        )
        self.assertEqual(identifiability["independent_biological_replicates"], 1)

    def test_controls_are_unique_complete_and_not_misrepresented_as_exact_nulls(self):
        controls = self.boundary["future_controls"]
        control_ids = [row["control_id"] for row in controls]
        self.assertEqual(len(control_ids), 6)
        self.assertEqual(len(control_ids), len(set(control_ids)))
        self.assertEqual(
            set(control_ids),
            {
                "train_only_no_signal_sentence_prior",
                "zero_validation_signal",
                "semantic_id_target_derangement",
                "channel_name_hash_derangement",
                "nonwrapping_zero_filled_time_displacement",
                "linear_signal_ctc",
            },
        )
        time_control = next(
            row
            for row in controls
            if row["control_id"] == "nonwrapping_zero_filled_time_displacement"
        )
        self.assertIn("not_exact_null", time_control["role"])

    def test_recommendations_are_not_frozen_thresholds_or_results(self):
        stats = self.boundary["future_statistical_recommendations"]
        self.assertEqual(stats["status"], "not_frozen_until_preregistration")
        self.assertEqual(stats["exact_primary_test"], "enumerate_all_64_paired_sign_assignments")
        self.assertTrue(stats["all_six_item_differences_must_be_reported"])
        self.assertFalse(stats["candidate_margin_is_frozen"])
        self.assertTrue(stats["exact_sequence_accuracy_is_secondary"])
        self.assertTrue(stats["all_required_controls_must_pass"])
        self.assertEqual(len(self.boundary["preregistration_prerequisites"]), 9)

    def test_access_counters_and_protected_resource_use_are_zero(self):
        counters = self.boundary["research_access_counters"]
        self.assertEqual(len(counters), 12)
        self.assertTrue(all(value == 0 for value in counters.values()))
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["future_cpu_threads"], 1)
        self.assertEqual(resources["future_workers"], 1)
        self.assertEqual(resources["future_model_parameter_ceiling"], 2908)
        self.assertEqual(resources["future_total_training_runtime_cap_sec"], 1200)
        self.assertEqual(resources["future_generated_artifact_cap_bytes"], 32 * 1024 * 1024)
        self.assertEqual(resources["future_new_real_data_download_bytes"], 0)
        self.assertEqual(resources["source_test_reads"], 0)
        self.assertEqual(resources["session2_reads"], 0)

    def test_primary_sources_and_human_note_cover_the_claim_boundary(self):
        bindings = self.boundary["source_bindings"]
        source_ids = [row["source_id"] for row in bindings]
        self.assertEqual(len(source_ids), 8)
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertTrue(all(row["url"].startswith("https://") for row in bindings))
        for phrase in (
            "2**6 = 64 assignments",
            "minimum attainable two-sided p = 2/64 = 0.03125",
            "2,908-parameter",
            "2,884-parameter",
            "does not authorize",
        ):
            self.assertIn(phrase, self.research)
        self.assertIn("planning research complete", self.research.lower())
        claims = " ".join(self.boundary["claim_boundary"])
        self.assertIn("Six validation sentences", claims)
        self.assertIn("real-time", claims)
        self.assertIn("clinical", claims)

    def test_roadmap_keeps_loop26_not_started_and_unauthorized(self):
        row = next(row for row in self.roadmap["loops"] if row["loop_id"] == 26)
        self.assertEqual(row["status"], "Not Started")
        self.assertFalse(row["execution_authorized"])
        self.assertEqual(row["proof_posture"], "planned_not_authorized")
        self.assertEqual(row["research_status"], "planning_research_complete")
        self.assertEqual(
            row["research_registry"],
            "registries/loop26_research_boundary.v0.json",
        )
        self.assertFalse(row["preregistration_prepared"])

    def test_no_loop26_runtime_or_experiment_surface_exists(self):
        forbidden = (
            "src/neurodecodekit/models/tiny_causal_sentence_ctc.py",
            "src/neurodecodekit/experiments/real_validation_encoder_gate.py",
            "registries/loop26_experiment_contract.v0.json",
            "registries/loop26_authorization_request.v0.json",
        )
        self.assertTrue(all(not (REPO_ROOT / path).exists() for path in forbidden))


if __name__ == "__main__":
    unittest.main()
