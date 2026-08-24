import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AMENDMENT = ROOT / "registries/eegmmidb_unseen_participant_generalization_amendment_1.v0.json"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_AMENDMENT_1.md"


class EEGMMIDBUnseenParticipantGeneralizationAmendment1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amendment = json.loads(AMENDMENT.read_text(encoding="utf-8"))

    def test_exact_green_authorization_decision_is_bound(self):
        green = self.amendment["green_authorization_decision"]
        self.assertEqual(green["commit"], "3e173f6dc61b1f6b32dcc9839aa74a67759b9b3f")
        self.assertEqual(green["CI_run_id"], 32694496933)
        self.assertEqual(green["base_python_job_id"], 97333988408)
        self.assertEqual(green["optional_neuro_job_id"], 97333988474)
        self.assertTrue(green["both_required_jobs_green"])

    def test_bound_artifact_hashes_sizes_blobs_and_set_hash_are_exact(self):
        rows = self.amendment["bound_pre_amendment_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.amendment["bound_pre_amendment_artifact_summary"]
        self.assertEqual(summary["count"], 15)
        self.assertEqual(summary["bytes"], sum(row["bytes"] for row in rows))
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_amendment_only_narrows_and_stage_g_stays_blocked_until_green(self):
        relation = self.amendment["scope_relation"]
        self.assertTrue(relation["participants_runs_files_dataset_and_split_unchanged"])
        self.assertTrue(relation["success_router_only_tightened"])
        self.assertTrue(relation["deterministic_implementation_details_only_added"])
        self.assertFalse(relation["operation_authority_expanded"])
        self.assertFalse(relation["network_or_payload_authority_expanded"])
        self.assertFalse(relation["retry_rerun_release_or_claim_authority_expanded"])
        gate = self.amendment["ordered_gate_effect"]
        self.assertFalse(gate["stage_G_available_before_amendment_remote_green"])
        self.assertTrue(gate["stage_G_available_after_amendment_remote_green_under_green_decision"])
        self.assertEqual(gate["qualification_invocations_allowed_after_green"], 1)

    def test_exact_channel_order_views_and_dimensions_are_frozen(self):
        channels = self.amendment["channel_contract"]
        order = channels["exact_order"]
        self.assertEqual(len(order), 64)
        self.assertEqual(len(set(order)), 64)
        self.assertEqual(len(channels["central_view"]), 18)
        self.assertEqual(len(channels["frontal_view"]), 8)
        self.assertEqual(len(channels["occipital_view"]), 8)
        self.assertTrue(set(channels["central_view"]).issubset(order))
        self.assertTrue(set(channels["frontal_view"]).issubset(order))
        self.assertTrue(set(channels["occipital_view"]).issubset(order))
        self.assertEqual(channels["whole_head_feature_dimension"], 320)
        self.assertEqual(channels["central_feature_dimension"], 90)
        self.assertEqual(channels["frontal_feature_dimension"], 40)
        self.assertTrue(channels["common_average_over_all_64_before_subset"])

    def test_causal_filter_state_dtype_and_literal_sos_are_frozen(self):
        causal = self.amendment["causal_preprocessing"]
        self.assertEqual(causal["dtype"], "float64")
        self.assertEqual(len(causal["literal_SOS"]), 4)
        self.assertTrue(all(len(section) == 6 for section in causal["literal_SOS"]))
        self.assertEqual(causal["initial_state"], "exact_zero_per_run")
        self.assertTrue(causal["run_boundary_reset"])
        self.assertFalse(causal["future_impulse_may_change_past_output"])
        self.assertFalse(causal["sosfiltfilt_reverse_eventwise_or_padded_filtering_allowed"])
        self.assertFalse(causal["baseline_correction_allowed"])

    def test_windows_and_early_cue_bins_are_executable(self):
        features = self.amendment["feature_contract"]
        windows = features["windows"]
        self.assertEqual(windows["primary_and_spatial"]["samples"], 320)
        self.assertEqual(windows["primary_and_spatial"]["samples_per_bin"], 80)
        self.assertEqual(windows["pre_cue"]["samples"], 320)
        self.assertEqual(windows["early_cue"]["samples"], 160)
        self.assertEqual(windows["early_cue"]["samples_per_bin"], 40)
        self.assertEqual(
            features["features_per_channel"],
            "four_contiguous_means_plus_one_normalized_linear_slope",
        )
        self.assertFalse(features["padding"])

    def test_identity_and_target_firewall_excludes_predictor_metadata(self):
        firewall = self.amendment["identity_and_target_firewall"]
        self.assertFalse(
            firewall[
                "participant_identity_available_to_predictor_feature_normalizer_model_threshold_or_condition_transform"
            ]
        )
        self.assertFalse(firewall["fresh_target_available_to_predictive_code"])
        self.assertFalse(firewall["fresh_class_count_available_to_predictive_code"])
        self.assertFalse(
            firewall[
                "target_derived_order_exclusion_normalization_threshold_selection_or_exception"
            ]
        )
        self.assertTrue(
            firewall[
                "target_swap_must_leave_all_predictive_outputs_logs_shapes_and_exceptions_byte_identical"
            ]
        )
        self.assertEqual(
            firewall["predictor_inputs"],
            ["ordered_feature_matrix", "frozen_model_or_fixed_control_rule"],
        )
        self.assertEqual(
            firewall["canonical_event_order"],
            "cue_sample_then_original_annotation_ordinal",
        )
        self.assertTrue(firewall["discard_T0_before_usable_event_ordinal"])
        self.assertTrue(firewall["input_annotation_reorder_must_produce_identical_canonical_rows"])

    def test_all_controls_and_literal_permutations_are_exact(self):
        controls = self.amendment["control_contract"]
        self.assertEqual(len(controls["conditions_in_canonical_order"]), 12)
        self.assertEqual(controls["equal_prior_no_signal"], "constant_T1_no_fit_no_feature_read")
        channel_permutation = controls["channel_permutation_indices"]
        label_permutation = controls["source_label_derangement_indices"]
        self.assertEqual(sorted(channel_permutation), list(range(64)))
        self.assertEqual(sorted(label_permutation), list(range(15)))
        self.assertFalse(controls["event_displacement_wrap"])
        self.assertTrue(
            controls["pre_early_central_frontal_occipital_use_separately_fitted_source_models"]
        )
        self.assertFalse(controls["fresh_target_used_to_construct_any_control"])

    def test_fit_and_prediction_schedule_is_below_original_caps(self):
        budget = self.amendment["fit_and_prediction_budget"]
        self.assertEqual(budget["source_execution_LOSO_folds"], 15)
        self.assertEqual(budget["source_execution_participants_fitted_per_fold"], 14)
        self.assertEqual(budget["parameter_update_fits_maximum_exact_schedule"], 61)
        self.assertEqual(
            budget["participant_condition_prediction_sets_maximum_exact_schedule"], 420
        )
        self.assertLessEqual(
            budget["parameter_update_fits_maximum_exact_schedule"],
            budget["original_parameter_update_fit_cap"],
        )
        self.assertLessEqual(
            budget["participant_condition_prediction_sets_maximum_exact_schedule"],
            budget["original_prediction_set_cap"],
        )

    def test_exact_completeness_and_stricter_control_gates_are_conjunctive(self):
        source = self.amendment["source_completeness"]
        self.assertEqual(source["participants_exact"], 15)
        self.assertEqual(source["usable_rows_per_participant_run_exact"], 15)
        self.assertEqual(source["execution_rows_exact"], 450)
        self.assertEqual(source["imagery_rows_exact"], 450)
        complete = self.amendment["fresh_completeness"]
        self.assertEqual(complete["participants_per_task_exact"], 15)
        self.assertEqual(complete["execution_rows_exact"], 225)
        self.assertEqual(complete["imagery_rows_exact"], 225)
        self.assertEqual(complete["sealed_target_rows_exact"], 450)
        execution = self.amendment["tightened_fresh_execution_gate"]
        self.assertEqual(execution["macro_margin_over_A_i_minimum"], 0.02)
        self.assertEqual(execution["paired_sign_flip_p_against_A_i_maximum"], 0.05)
        self.assertEqual(execution["paired_sign_flip_p_against_B_i_maximum"], 0.05)
        imagery = self.amendment["tightened_fresh_imagery_gate"]
        self.assertTrue(imagery["cannot_rescue_execution"])
        self.assertEqual(imagery["events_exact"], 225)
        self.assertEqual(imagery["macro_margin_over_A_i_minimum"], 0.02)

    def test_checkpoint_and_prediction_freeze_are_canonical_and_verified(self):
        checkpoint = self.amendment["checkpoint_contract"]
        self.assertFalse(checkpoint["pickle_or_joblib_allowed"])
        self.assertIn("allow_pickle_false", checkpoint["format"])
        self.assertTrue(
            checkpoint["load_revalidates_every_field_shape_dtype_member_and_aggregate_hash"]
        )
        freeze = self.amendment["prediction_freeze_contract"]
        self.assertEqual(freeze["private_format"], "canonical_UTF8_JSONL_one_object_per_line")
        self.assertEqual(len(freeze["row_fields_exact"]), 9)
        self.assertFalse(freeze["targets_probabilities_or_free_form_fields_allowed"])
        self.assertFalse(
            freeze["public_individual_prediction_probability_target_or_participant_outcome"]
        )
        self.assertTrue(
            freeze[
                "scorer_rehashes_private_file_and_verifies_order_counts_commitments_before_target_values"
            ]
        )

    def test_resource_guards_authority_and_claims_fail_closed(self):
        resources = self.amendment["resource_enforcement"]
        self.assertEqual(resources["CPU_threads_workers_numerical_jobs"], [1, 1, 1])
        self.assertEqual(resources["stage_wall_time_seconds_maximum"]["G"], 900)
        self.assertEqual(resources["stage_G_network_bytes"], 0)
        self.assertTrue(resources["count_temporary_and_final_bytes_cumulatively"])
        self.assertEqual(resources["retries_reruns_post_target_updates"], [0, 0, 0])
        self.assertTrue(all(value is False for value in self.amendment["authority_now"].values()))
        counters = self.amendment["amendment_operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 15)
        self.assertEqual(counters["Git_proof_reads"], 15)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )
        self.assertFalse(
            self.amendment["claim_boundary"]["scientific_claim_established_by_amendment"]
        )
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
