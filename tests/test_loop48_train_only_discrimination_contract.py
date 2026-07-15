import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_train_only_discrimination_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md"


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


class Loop48TrainOnlyDiscriminationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_contract_is_preregistered_and_every_authorization_is_false(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_not_authorized_no_protected_execution",
        )
        flags = authorization_flags(self.contract)
        self.assertGreaterEqual(len(flags), 20)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(self.contract["authorization"]["exact_sentence_received_from_user"])

    def test_every_dependency_and_source_binding_matches_current_bytes(self):
        bindings = {
            **self.contract["dependency_bindings"],
            **self.contract["implementation_source_bindings"],
        }
        for name, binding in bindings.items():
            with self.subTest(binding=name):
                payload = (REPO_ROOT / binding["path"]).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])

    def test_source_identity_and_closed_partitions_are_exact(self):
        source = self.contract["source_contract"]
        cache = source["cache"]
        self.assertEqual(cache["bytes"], 10_632_576)
        self.assertEqual(cache["shape"], [66, 102, 617])
        self.assertEqual(cache["sampling_rate_hz"], 100.0)
        self.assertFalse(cache["source_content_read_during_preregistration"])
        self.assertEqual(
            source["split_report"]["partition_rows"],
            {"train": 55, "val": 6, "test": 5},
        )
        self.assertEqual(source["allowed_source_partition"], "train_only")
        self.assertFalse(source["validation_or_test_delivery_allowed"])
        self.assertFalse(source["session2_s7_s20_s25_allowed"])
        self.assertFalse(source["raw_fif_or_mat_allowed"])

    def test_claim_ceiling_accounts_for_historical_train_use(self):
        correction = self.contract["historical_use_correction"]
        ceiling = self.contract["claim_ceiling"]
        self.assertTrue(correction["all_55_source_train_rows_used_by_prior_loop26_fits"])
        self.assertFalse(correction["new_check_rows_historically_unseen"])
        self.assertFalse(correction["diagnostic_partition_is_independent_final_test"])
        self.assertEqual(ceiling["maximum_evidence_level"], "E2_pipeline_discriminative")
        self.assertTrue(ceiling["corrects_design_level_e3_for_this_exact_source"])
        for field in (
            "independent_validation_allowed",
            "neural_advantage_allowed",
            "brain_specific_origin_allowed",
            "useful_decoding_allowed",
            "unseen_person_generalization_allowed",
            "causal_preprocessing_or_realtime_allowed",
            "eeg_portable_home_or_clinical_allowed",
        ):
            self.assertFalse(ceiling[field], field)

    def test_split_is_target_independent_exact_and_nested(self):
        split = self.contract["diagnostic_split_contract"]
        self.assertEqual(split["source_rows"], 55)
        self.assertEqual(split["required_unique_semantic_ids"], 55)
        self.assertEqual(split["required_unique_row_ids"], 55)
        self.assertEqual(split["ordered_assignment"]["fit"]["rows"], 44)
        self.assertEqual(split["ordered_assignment"]["check"]["rows"], 11)
        self.assertEqual(split["fit_prefix_sizes"], [8, 16, 24, 32, 44])
        self.assertTrue(split["strictly_nested_prefixes"])
        self.assertTrue(split["fit_and_check_disjoint"])
        self.assertFalse(split["target_value_may_affect_order"])
        self.assertFalse(split["consumed_validation_metric_may_affect_order"])
        self.assertFalse(split["check_targets_available_to_fit_or_prediction_process"])

    def test_derivatives_withhold_check_targets_until_green_freeze(self):
        derivatives = self.contract["isolation_derivative_contract"]
        self.assertFalse(derivatives["legacy_full_array_loader_allowed"])
        self.assertEqual(derivatives["source_cache_sha256_passes_exact"], 1)
        fit, check = derivatives["pre_freeze_outputs"]
        self.assertEqual((fit["artifact_id"], fit["rows"]), ("fit_bundle", 44))
        self.assertTrue(fit["contains_targets"])
        self.assertEqual((check["artifact_id"], check["rows"]), ("check_inputs", 11))
        self.assertFalse(check["contains_targets"])
        post = derivatives["post_green_freeze_output"]
        self.assertEqual((post["rows"], post["delivery_events_exact"]), (11, 1))
        self.assertEqual(derivatives["validation_derivatives"], 0)
        self.assertEqual(derivatives["source_test_derivatives"], 0)

    def test_static_quality_audit_is_gross_transformed_quality_only(self):
        audit = self.contract["static_audit_contract"]
        self.assertEqual(
            audit["gross_defect_thresholds"],
            {
                "nonfinite_values_max": 0,
                "nonzero_padding_values_max": 0,
                "near_flat_channel_variance_max": 1e-08,
                "near_flat_trial_channel_fraction_min": 0.2,
            },
        )
        self.assertFalse(audit["raw_sensor_quality_available"])
        self.assertFalse(audit["bad_channel_annotations_available"])
        self.assertFalse(audit["line_noise_interpretation_available"])
        self.assertFalse(audit["head_motion_available"])
        self.assertFalse(audit["peripheral_physiology_available"])
        self.assertFalse(audit["passing_transformed_quality_audit_weighs_against_h2"])

    def test_model_training_and_telemetry_inventory_is_exact(self):
        models = self.contract["model_contract"]
        training = self.contract["training_contract"]
        self.assertEqual(models["candidate"]["parameter_count"], 2908)
        self.assertEqual(models["linear"]["parameter_count"], 2884)
        self.assertFalse(models["larger_or_additional_architecture_allowed"])
        self.assertEqual(training["seeds"], [4801, 4802, 4803])
        self.assertEqual(training["primary_seed"], 4801)
        self.assertEqual(training["candidate_fits"], 15)
        self.assertEqual(training["linear_comparator_fits"], 3)
        self.assertEqual(training["target_derangement_fits"], 1)
        self.assertEqual(training["timing_only_fits"], 1)
        self.assertEqual(training["total_parameter_update_runs"], 20)
        self.assertEqual(training["total_optimizer_steps"], 4_800)
        self.assertEqual(training["no_signal_prior_fits"], 5)
        self.assertEqual(training["telemetry_steps"], [1, 8, 16, 32, 64, 120, 180, 240])
        self.assertEqual(len(training["telemetry_fields"]), 6)
        self.assertEqual(training["restarts"], 0)
        self.assertFalse(training["best_of_seed_selection"])

    def test_control_and_prediction_arithmetic_is_exact(self):
        controls = self.contract["control_transform_contract"]
        inventory = self.contract["prediction_inventory"]
        self.assertEqual(controls["fine_time_shifts"]["offset_samples"], [-50, -25, 25, 50])
        self.assertTrue(
            controls["fine_time_shifts"]["negative_offsets_are_offline_noncausal_diagnostic_only"]
        )
        self.assertEqual(controls["severe_time_displacement"]["offset_samples"], 100)
        prediction_sum = sum(
            inventory[key]
            for key in (
                "candidate_prefix_sets",
                "matched_prior_sets",
                "linear_sets",
                "zero_signal_sets",
                "row_derangement_sets",
                "channel_derangement_sets",
                "fine_shift_sets",
                "severe_shift_sets",
                "timing_only_sets",
                "target_derangement_sets",
            )
        )
        self.assertEqual(prediction_sum, 41)
        self.assertEqual(inventory["prediction_sets_exact"], 41)
        self.assertEqual(inventory["target_blind_model_inference_runs_exact"], 35)
        self.assertTrue(inventory["all_sets_share_same_11_ordered_check_ids"])
        self.assertFalse(inventory["committed_freeze_contains_plaintext_predictions"])
        self.assertFalse(inventory["committed_freeze_contains_plaintext_targets"])

    def test_scoring_and_hypothesis_rules_are_frozen(self):
        scoring = self.contract["scoring_contract"]
        conjunction = self.contract["diagnostic_intact_signal_conjunction"]
        probes = self.contract["registered_probe_separability_rule"]
        scaling = self.contract["bounded_scaling_contract"]
        self.assertEqual(scoring["check_items"], 11)
        self.assertEqual(scoring["sign_assignments_exact"], 2**11)
        self.assertEqual(scoring["primary_practical_margin"], 0.05)
        self.assertEqual(scoring["fine_shift_bonferroni_p_max"], 0.0125)
        self.assertEqual(len(conjunction["comparators"]), 7)
        self.assertTrue(conjunction["intersection_union_all_required"])
        self.assertEqual(len(probes["candidate_sets"]), 3)
        self.assertEqual(len(probes["linear_sets"]), 3)
        self.assertEqual(probes["comparator"], "prior_size44")
        self.assertTrue(probes["support_requires_all_six_fits_finite_and_stable"])
        self.assertTrue(probes["support_requires_all_six_fail_macro_cer_margin_or_p_value"])
        self.assertTrue(probes["against_requires_one_probe_family_pass_all_three_seeds"])
        self.assertEqual(probes["primary_seed_must_pass_for_against"], 4801)
        self.assertFalse(probes["candidate_corruption_conjunction_reused_for_linear"])
        self.assertFalse(probes["linear_called_task_locked_character_probe"])
        self.assertEqual(scaling["fit_prefix_sizes"], [8, 16, 24, 32, 44])
        self.assertEqual(scaling["support_gain_min"], 0.05)
        self.assertFalse(scaling["power_law_asymptote_or_extrapolation_allowed"])
        hypotheses = self.contract["hypothesis_decision_contract"]
        self.assertEqual(
            [row["hypothesis_id"] for row in hypotheses], ["H1", "H2", "H3", "H4", "H5", "H6"]
        )
        self.assertFalse(self.contract["orthogonal_claim_threat"]["resolved_by_stage_b"])

    def test_access_order_places_check_targets_after_green_freeze(self):
        sequence = self.contract["access_sequence"]
        implementation = sequence.index(
            "implementation_and_synthetic_isolation_tests_committed_pushed_and_remotely_green"
        )
        cache_hash = sequence.index("one_source_cache_sha256_pass")
        prediction_freeze = sequence.index(
            "commit_push_and_obtain_green_ci_for_hash_only_prediction_freeze_record"
        )
        check_targets = sequence.index(
            "deliver_exactly_11_check_targets_to_one_isolated_scorer_once"
        )
        self.assertLess(implementation, cache_hash)
        self.assertLess(cache_hash, prediction_freeze)
        self.assertLess(prediction_freeze, check_targets)

    def test_resource_caps_stay_inside_machine_envelope(self):
        caps = self.contract["resource_caps"]
        self.assertEqual((caps["cpu_threads"], caps["workers"]), (1, 1))
        self.assertEqual(caps["candidate_parameter_ceiling"], 2908)
        self.assertEqual(caps["total_parameter_update_runs"], 20)
        self.assertEqual(caps["target_blind_model_inference_runs"], 35)
        self.assertEqual(caps["prediction_sets"], 41)
        self.assertEqual(caps["peak_rss_bytes"], 1 << 30)
        self.assertEqual(caps["total_generated_artifact_bytes"], 32 << 20)
        self.assertEqual(caps["minimum_free_disk_bytes_before_execution"], 20 << 30)
        self.assertEqual(caps["new_download_bytes"], 0)
        self.assertEqual(caps["external_model_or_weight_download_bytes"], 0)

    def test_preregistration_ledger_has_zero_protected_activity(self):
        ledger = self.contract["preregistration_access_ledger"]
        allowed_nonzero = {
            "committed_artifact_and_source_reads",
            "public_primary_source_documents_consulted",
            "public_source_research_passes",
            "ignored_path_name_listings",
        }
        protected = {key: value for key, value in ledger.items() if key not in allowed_nonzero}
        self.assertTrue(all(value == 0 for value in protected.values()), protected)
        self.assertEqual(ledger["public_primary_source_documents_consulted"], 6)
        self.assertEqual(ledger["ignored_file_content_reads"], 0)

    def test_doc_discloses_scope_statistics_and_claim_limits(self):
        normalized_doc = self.doc.casefold()
        for phrase in (
            "44/11 Diagnostic Split",
            "all 55 source-train rows were used",
            "E2 pipeline-discriminative evidence",
            "20 fits",
            "35 model-inference runs",
            "41 prediction sets",
            "2^11 = 2,048",
            "0.0125",
            "20 GiB",
            "General continuation",
            "Scientific claim not established",
        ):
            self.assertIn(phrase.casefold(), normalized_doc)


if __name__ == "__main__":
    unittest.main()
