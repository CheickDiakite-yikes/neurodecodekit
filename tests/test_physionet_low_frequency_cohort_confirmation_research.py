import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/physionet_low_frequency_cohort_confirmation_research.v0.json"
DOC_PATH = ROOT / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_PRIMARY_SOURCE_RESEARCH.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyCohortConfirmationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_scope_is_research_only_and_every_irreversible_flag_is_false(self):
        scope = self.registry["scope"]
        self.assertTrue(scope["tier_a_research_only"])
        self.assertTrue(scope["additive_work_order_without_renumbering_10_through_20"])
        self.assertTrue(scope["cohort_selected_from_public_metadata"])
        self.assertTrue(
            all(
                value is False
                for key, value in scope.items()
                if key
                not in {
                    "tier_a_research_only",
                    "additive_work_order_without_renumbering_10_through_20",
                    "cohort_selected_from_public_metadata",
                }
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.registry["current_access_counters"].values())
        )

    def test_inherited_result_is_exact_and_consumed(self):
        inherited = self.registry["inherited_evidence"]
        for key in (
            "work_order_9_result_document",
            "work_order_9_result_registry",
            "work_order_9_contract",
        ):
            binding = inherited[key]
            self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))
        self.assertEqual(inherited["consumed_verdict"], "WO9-V1")
        self.assertEqual(inherited["secondary_correct"], 36)
        self.assertEqual(inherited["secondary_final_event_count"], 45)
        self.assertAlmostEqual(
            inherited["secondary_pooled_balanced_accuracy"],
            0.8003952569169961,
        )
        self.assertFalse(inherited["private_artifact_reuse_allowed"])
        self.assertFalse(inherited["consumed_target_reopen_allowed"])
        self.assertFalse(inherited["post_result_tuning_allowed"])

    def test_new_cohort_is_contiguous_untouched_and_nonoverlapping(self):
        cohort = self.registry["prospective_cohort"]
        expected = [f"S{index:03d}" for index in range(4, 16)]
        self.assertEqual(cohort["participants"], expected)
        self.assertEqual(cohort["participant_count"], 12)
        self.assertEqual(cohort["overlap_with_consumed_cohort"], [])
        self.assertEqual(cohort["execution_fit_runs"], ["03", "07"])
        self.assertEqual(cohort["execution_sealed_final_run"], "11")
        self.assertEqual(cohort["imagery_fit_runs"], ["04", "08"])
        self.assertEqual(cohort["imagery_sealed_final_run"], "12")
        self.assertEqual(cohort["prospective_edf_count"], 72)
        self.assertEqual(cohort["event_sidecar_count"], 0)
        self.assertTrue(cohort["exact_paths_sizes_and_sha256_required_before_authorization"])
        self.assertFalse(cohort["substitution_participants_or_runs_allowed"])

    def test_primary_model_carries_the_prespecified_comparator_forward_exactly(self):
        model = self.registry["frozen_primary_model_template"]
        self.assertEqual(model["family_id"], "fixed_low_frequency_shrinkage_lda")
        self.assertEqual(model["passband_hz"], [0.5, 4.0])
        self.assertEqual(model["decision_window_seconds_from_cue"], [1.0, 3.0])
        self.assertEqual(model["time_bins"], 4)
        self.assertEqual(model["slopes_per_channel"], 1)
        self.assertEqual(model["expected_feature_dimension_at_64_channels"], 320)
        self.assertEqual(model["lda_shrinkage"], 0.1)
        self.assertEqual(model["selection_candidate_count"], 1)
        self.assertEqual(model["hyperparameter_search_runs"], 0)
        self.assertEqual(model["right_context_seconds_relative_to_decision"], 0.0)
        self.assertIn("cue_causal_only", model["causal_claim"])

    def test_native_and_cross_task_questions_are_all_target_blind(self):
        questions = self.registry["prediction_questions"]
        self.assertEqual(
            [row["question_id"] for row in questions],
            [
                "execution_native_primary",
                "imagery_native",
                "execution_to_imagery",
                "imagery_to_execution",
            ],
        )
        self.assertEqual(questions[0]["fit_runs"], ["03", "07"])
        self.assertEqual(questions[0]["predict_run"], "11")
        self.assertEqual(questions[1]["fit_runs"], ["04", "08"])
        self.assertEqual(questions[1]["predict_run"], "12")
        self.assertEqual(questions[2]["predict_run"], "12")
        self.assertEqual(questions[3]["predict_run"], "11")

    def test_controls_cover_spatial_temporal_label_and_no_signal_failures(self):
        controls = set(self.registry["mandatory_views_and_controls"])
        required = {
            "central_sensorimotor_only",
            "frontal_polar_ocular_sensitive",
            "occipital_visual_sensitive",
            "left_minus_right_frontal_asymmetry",
            "early_cue_window_whole_head",
            "pre_cue_window",
            "event_index_and_timing_only",
            "train_only_no_signal_prior",
            "all_zero_final_signal",
            "fixed_train_label_derangement",
            "fixed_one_trial_final_signal_displacement",
            "fixed_channel_derangement",
            "fixed_left_right_hemisphere_swap",
        }
        self.assertTrue(required.issubset(controls))
        self.assertGreaterEqual(len(controls), 17)

    def test_gates_use_participants_and_keep_localization_conjunctive(self):
        gates = self.registry["prospective_gates"]
        h1 = gates["H1_execution_cohort_confirmation"]
        self.assertEqual(h1["expected_final_event_count"], 180)
        self.assertEqual(h1["minimum_correct_count"], 117)
        self.assertEqual(h1["minimum_pooled_balanced_accuracy"], 0.65)
        self.assertEqual(h1["minimum_participants_above_0_5_balanced_accuracy"], 9)
        self.assertLessEqual(h1["maximum_exact_participant_sign_flip_p"], 0.01)
        h3 = gates["H3_motor_compatible_localization"]
        self.assertEqual(h3["minimum_central_minus_strongest_proxy_margin"], 0.05)
        self.assertFalse(h3["dedicated_EOG_available"])
        self.assertFalse(h3["dedicated_EMG_available"])
        self.assertFalse(h3["proxy_failure_proves_cortical_origin"])

    def test_router_is_ordered_and_never_reaches_brain_specific_claim(self):
        router = self.registry["ordered_verdict_router"]
        self.assertEqual(
            [row["verdict"] for row in router],
            ["WO9R-R0", "WO9R-R1", "WO9R-R2", "WO9R-R3", "WO9R-R4"],
        )
        self.assertIn("not_brain_specific", router[-1]["maximum_claim"])
        boundary = self.registry["claim_boundary"]
        self.assertIn("No new participant payload", boundary["scientific_claim_not_established"])
        self.assertIn(
            "still without brain-specific origin", boundary["maximum_future_WO9R_R4_claim"]
        )

    def test_resource_envelope_is_small_and_one_shot(self):
        resources = self.registry["future_resource_envelope"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["concurrent_numerical_jobs"], 1)
        self.assertLessEqual(resources["maximum_peak_rss_bytes"], 1 << 30)
        self.assertLessEqual(resources["expected_payload_ceiling_bytes"], 256 << 20)
        self.assertGreaterEqual(
            resources["minimum_free_disk_bytes_before_tier_c_operation"],
            20 << 30,
        )
        self.assertEqual(resources["retries"], 0)
        self.assertEqual(resources["reruns"], 0)
        self.assertEqual(resources["post_final_updates"], 0)

    def test_document_and_queue_preserve_the_planning_only_boundary(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Why This Is The Right Next Experiment", document)
        self.assertIn("S004-S015", document)
        self.assertIn("WO9R-R4", document)
        self.assertIn("Scientific claim not established", document)
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Work order 9R", queue)
        self.assertIn("Research and preregistration complete", queue)
        self.assertEqual(sum(line.startswith("| ") for line in queue.splitlines()), 21)


if __name__ == "__main__":
    unittest.main()
