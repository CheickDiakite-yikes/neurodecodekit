import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    REPO_ROOT / "registries" / "loop26_shared_validation_contract.v0.json"
)
PREREGISTRATION_PATH = (
    REPO_ROOT / "docs" / "LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


class Loop26SharedValidationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.preregistration = PREREGISTRATION_PATH.read_text(encoding="utf-8")

    def test_identity_scope_and_every_authorization_flag_are_exact(self):
        contract = self.contract
        self.assertEqual(
            contract["schema_name"],
            "neurodecodekit.loop26_shared_validation_contract",
        )
        self.assertEqual(contract["schema_version"], "0.1.0")
        self.assertEqual(
            contract["status"],
            "preregistered_not_authorized_no_protected_execution",
        )
        self.assertEqual(contract["scope"]["numbered_loops"], [26, 31, 33])
        self.assertEqual(contract["scope"]["scientific_roadmap_loops"], [46])
        self.assertEqual(
            (
                contract["scope"]["source_train_items"],
                contract["scope"]["shared_validation_items"],
                contract["scope"]["source_test_items"],
            ),
            (55, 6, 5),
        )
        flags = authorization_flags(contract)
        self.assertEqual(len(flags), 21)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_exact_authorization_sentence_is_single_and_not_satisfied(self):
        authorization = self.contract["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertTrue(sentence.startswith("Authorize the Loop 26/31/33"))
        self.assertEqual(self.preregistration.count(sentence), 1)
        self.assertIn(
            "general research autonomy\ndoes not substitute",
            self.preregistration,
        )
        self.assertTrue(
            authorization["authorization_must_be_recorded_in_separate_commit"]
        )
        self.assertTrue(
            authorization["authorization_commit_must_be_pushed_and_remotely_green"]
        )

    def test_committed_dependency_and_local_evidence_hashes_match(self):
        bindings = {}
        bindings.update(self.contract["dependency_bindings"])
        bindings.update(self.contract["local_evidence_bindings"])
        self.assertEqual(len(bindings), 12)
        for binding_id, binding in bindings.items():
            with self.subTest(binding=binding_id):
                path = REPO_ROOT / binding["path"]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(binding["sha256"], sha256(path))
        audit = self.contract["legacy_archive_access_audit"]
        self.assertEqual(
            audit["legacy_loader_sha256"],
            self.contract["local_evidence_bindings"]
            ["legacy_sentence_cache_loader"]["sha256"],
        )

    def test_source_identity_split_scaler_and_causality_are_frozen(self):
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
        self.assertEqual(source["frozen_scaler"]["fit_rows"], 55)
        self.assertEqual(source["frozen_scaler"]["validation_fit_rows"], 0)
        self.assertEqual(source["frozen_scaler"]["test_fit_rows"], 0)
        causality = source["upstream_causality"]
        self.assertFalse(causality["cache_preprocessing_is_causal"])
        self.assertTrue(causality["whole_recording_fft_resample_used"])
        self.assertTrue(causality["zero_phase_filtering_used"])
        self.assertFalse(causality["end_to_end_causal_or_realtime_claim_allowed"])

    def test_archive_access_correction_withdraws_only_the_false_claim(self):
        audit = self.contract["legacy_archive_access_audit"]
        self.assertEqual(audit["archive_format"], "deflated_npz")
        self.assertFalse(audit["row_selective_random_access_available"])
        self.assertTrue(audit["legacy_loader_materializes_all_required_arrays"])
        self.assertGreaterEqual(audit["known_minimum_prior_full_cache_loads"], 2)
        self.assertIsNone(audit["exact_prior_full_cache_load_count"])
        self.assertTrue(
            audit["validation_target_bytes_were_physically_materialized_by_legacy_loader"]
        )
        self.assertFalse(
            audit["validation_targets_were_used_for_prior_loss_selection_or_scoring"]
        )
        self.assertTrue(audit["physical_never_opened_validation_target_claim_withdrawn"])
        self.assertIn("not been used", audit["remaining_prospective_claim"])

    def test_isolation_derivatives_forbid_target_and_test_leakage(self):
        isolation = self.contract["isolation_derivative_contract"]
        self.assertFalse(isolation["standard_numpy_full_array_loader_allowed"])
        self.assertEqual(isolation["source_cache_hash_passes_exact"], 1)
        outputs = {row["artifact_id"]: row for row in isolation["pre_score_outputs"]}
        self.assertEqual(outputs["train_bundle"]["rows"], 55)
        self.assertTrue(outputs["train_bundle"]["contains_targets"])
        self.assertEqual(outputs["validation_inputs"]["rows"], 6)
        self.assertFalse(outputs["validation_inputs"]["contains_targets"])
        self.assertFalse(outputs["validation_inputs"]["contains_plaintext_targets"])
        self.assertEqual(isolation["post_freeze_output"]["rows"], 6)
        self.assertTrue(
            isolation["post_freeze_output"]
            ["created_only_after_green_prediction_freeze_commit"]
        )
        self.assertEqual(isolation["source_test_outputs"], 0)
        self.assertEqual(
            isolation["source_test_rows_delivered_to_training_inference_or_scoring"],
            0,
        )

    def test_candidate_and_linear_parameter_math_are_exact(self):
        candidate = self.contract["candidate_model"]
        calculated = (102 * 16 + 16) + (16 * 16 * 3 + 16) + (16 * 28 + 28)
        self.assertEqual(calculated, 2_908)
        self.assertEqual(candidate["parameter_count"], calculated)
        self.assertEqual(candidate["right_context_samples"], 0)
        self.assertEqual(candidate["left_history_samples"], 2)
        self.assertTrue(candidate["model_causal"])
        self.assertFalse(candidate["whole_pipeline_causal"])
        linear = self.contract["linear_comparator"]
        self.assertEqual(linear["parameter_count"], 102 * 28 + 28)
        self.assertEqual(linear["parameter_difference_from_candidate"], 24)

    def test_training_run_prediction_and_step_accounting_are_exact(self):
        training = self.contract["training_contract"]
        self.assertEqual(training["seeds"], [2601, 2602, 2603])
        self.assertEqual(training["restarts"], 0)
        self.assertFalse(training["best_of_seed_selection"])
        self.assertEqual(training["optimizer_steps_per_fit"], 240)
        fit_total = sum(
            training[name]
            for name in (
                "candidate_fits",
                "target_derangement_fits",
                "timing_only_fits",
                "linear_comparator_fits",
            )
        )
        self.assertEqual(fit_total, 21)
        self.assertEqual(training["total_parameter_update_runs"], fit_total)
        self.assertEqual(training["total_optimizer_steps"], 21 * 240)
        self.assertEqual(training["target_blind_model_inference_runs"], 24)
        self.assertEqual(training["target_blind_prediction_sets"], 31)
        self.assertFalse(training["loss"]["zero_infinity"])

    def test_condition_matrix_and_transforms_are_target_blind(self):
        rows = self.contract["encoder_condition_matrix"]
        self.assertEqual([row["id"] for row in rows], [f"L31-E0{i}" for i in range(10)])
        self.assertFalse(next(row for row in rows if row["id"] == "L31-E07")["required"])
        required = {row["id"] for row in rows if row["required"]}
        self.assertEqual(required, {f"L31-E0{i}" for i in range(10)} - {"L31-E07"})
        transforms = self.contract["control_transform_contract"]
        self.assertEqual(transforms["validation_row_derangement"]["fixed_points"], 0)
        self.assertEqual(transforms["channel_derangement"]["fixed_points"], 0)
        self.assertEqual(transforms["train_target_derangement"]["fixed_points"], 0)
        self.assertFalse(transforms["train_target_derangement"]["validation_targets_used"])
        self.assertFalse(transforms["timing_only"]["signal_values_used"])
        self.assertFalse(transforms["time_displacement"]["wrapping"])

    def test_scaling_and_prediction_freeze_contracts_are_exact(self):
        scaling = self.contract["scaling_contract"]
        self.assertEqual(scaling["prefix_sizes"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(scaling["seeds_per_prefix"], 3)
        self.assertEqual(scaling["candidate_fits"], 18)
        self.assertTrue(scaling["strictly_nested"])
        self.assertFalse(scaling["formal_slope_p_value"])
        self.assertFalse(scaling["acquisition_authorized_by_positive_curve"])
        freeze = self.contract["prediction_freeze_contract"]
        self.assertEqual(
            freeze["prediction_sets_exact"],
            freeze["candidate_curve_sets"]
            + freeze["matched_prior_sets"]
            + freeze["additional_encoder_control_sets"],
        )
        self.assertEqual(freeze["prediction_sets_exact"], 31)
        self.assertFalse(freeze["validation_targets_available_to_prediction_process"])
        self.assertTrue(freeze["freeze_record_must_be_tested_committed_pushed_and_remotely_green"])

    def test_scoring_gate_has_exact_resolution_and_all_required_controls(self):
        scoring = self.contract["scoring_contract"]
        self.assertEqual(scoring["validation_items"], 6)
        self.assertEqual(scoring["target_delivery_events_exact"], 1)
        self.assertEqual(scoring["exact_sign_assignments"], 2**6)
        self.assertEqual(scoring["primary_one_sided_alpha"], 0.05)
        self.assertEqual(scoring["primary_macro_cer_margin_min"], 0.05)
        self.assertTrue(scoring["primary_requires_six_strict_sentence_wins"])
        self.assertEqual(len(scoring["required_exact_control_ids"]), 7)
        self.assertTrue(scoring["candidate_must_have_lower_macro_cer_than_linear_E09"])
        self.assertTrue(scoring["intersection_union_gate"])
        self.assertTrue(scoring["missing_condition_is_failure"])
        self.assertFalse(scoring["post_score_restart_or_threshold_change"])

    def test_access_sequence_places_target_delivery_after_green_freeze(self):
        sequence = self.contract["access_sequence"]
        authorization = sequence.index(
            "separate_exact_authorization_commit_tested_pushed_and_remotely_green"
        )
        cache_access = sequence.index("one_source_cache_hash_pass")
        freeze = sequence.index(
            "commit_push_and_obtain_green_ci_for_hash_only_prediction_freeze_record"
        )
        target_delivery = sequence.index(
            "stream_exactly_six_validation_targets_into_isolated_scorer_once"
        )
        self.assertLess(authorization, cache_access)
        self.assertLess(cache_access, freeze)
        self.assertLess(freeze, target_delivery)
        self.assertEqual(sequence[-1].split("_")[0], "close")

    def test_resource_caps_refusals_and_preregistration_ledger_are_bounded(self):
        resources = self.contract["resource_caps"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["candidate_parameter_ceiling"], 2_908)
        self.assertEqual(resources["total_end_to_end_runtime_sec"], 1_500)
        self.assertEqual(resources["peak_rss_bytes"], 1 << 30)
        self.assertEqual(resources["total_generated_artifact_bytes"], 32 << 20)
        self.assertEqual(resources["new_download_bytes"], 0)
        refusals = self.contract["refusal_ids"]
        self.assertEqual(len(refusals), 40)
        self.assertEqual(len(set(refusals)), 40)
        counters = self.contract["required_runtime_access_counters"]
        self.assertEqual(len(counters), len(set(counters)))
        ledger = self.contract["preregistration_access_ledger"]
        for name in (
            "source_cache_signal_value_reads",
            "source_cache_target_value_reads",
            "raw_fif_or_mat_reads",
            "model_or_checkpoint_runs",
            "training_runs",
            "parameter_updates",
            "validation_scoring_runs",
            "new_generated_experiment_payload_bytes",
        ):
            self.assertEqual(ledger[name], 0, name)
        self.assertEqual(ledger["public_web_operations"], 6)
        self.assertFalse(ledger["sidecar_used_as_scientific_evidence"])

    def test_claim_ceiling_remains_narrow_even_after_a_future_pass(self):
        claims = self.contract["claim_boundaries"]
        allowed = " ".join(claims["may_claim_if_every_registered_gate_passes"])
        forbidden = " ".join(claims["must_not_claim_even_if_every_gate_passes"])
        self.assertIn("one person session task split", allowed)
        for phrase in (
            "unseen-person",
            "brain-specific",
            "Brain2Qwerty v2 equivalence",
            "EEG OPM wearable portable",
            "clinical",
        ):
            self.assertIn(phrase, forbidden)
        self.assertEqual(
            claims["current_claim"],
            "Preregistration and archive-access audit only; no scientific result.",
        )


if __name__ == "__main__":
    unittest.main()
