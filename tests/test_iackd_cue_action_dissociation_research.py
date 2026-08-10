import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_PATH = ROOT / "registries/iackd_cue_action_dissociation_research.v0.json"
INVENTORY_PATH = ROOT / "registries/iackd_openneuro_metadata_inventory.v0.json"
DOC_PATH = ROOT / "docs/IACKD_CUE_ACTION_DISSOCIATION_PRIMARY_SOURCE_RESEARCH.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDCueActionDissociationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.research = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    def test_research_scope_is_metadata_only(self):
        scope = self.research["scope"]
        allowed_true = {
            "tier_a_research_only",
            "public_candidate_selected",
            "metadata_only_inventory_created",
            "primary_hypothesis_selected",
        }
        self.assertTrue(all(scope[key] for key in allowed_true))
        self.assertTrue(
            all(value is False for key, value in scope.items() if key not in allowed_true)
        )
        counters = self.research["current_access_counters"]
        irreversible = {
            "payload_url_gets",
            "payload_bytes_transferred",
            "EEG_content_opens",
            "EOG_content_opens",
            "marker_content_opens",
            "event_content_opens",
            "kinematic_content_opens",
            "target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scoring_runs",
            "downloads",
        }
        self.assertTrue(all(counters[key] == 0 for key in irreversible))

    def test_consumed_WO9R_evidence_is_hash_bound(self):
        inherited = self.research["inherited_evidence"]
        for key in ("wo9r_result_document", "wo9r_result_registry", "wo9r_contract"):
            binding = inherited[key]
            self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))
        self.assertEqual(inherited["consumed_verdict"], "WO9R-R3")
        self.assertFalse(inherited["private_artifact_reuse_allowed"])
        self.assertFalse(inherited["target_reopen_allowed"])
        self.assertFalse(inherited["rerun_allowed"])
        self.assertFalse(inherited["post_result_tuning_allowed"])

    def test_inventory_binding_and_source_identity_are_exact(self):
        binding = self.research["metadata_inventory"]
        self.assertEqual(binding["sha256"], sha256(INVENTORY_PATH))
        selection = self.inventory["selection"]
        self.assertEqual(selection["selected_object_count"], 1340)
        self.assertEqual(selection["selected_payload_bytes"], 7_249_113_684)
        self.assertEqual(selection["bids_run_count"], 128)
        self.assertEqual(selection["participant_count"], 15)
        self.assertEqual(selection["participant_hand_units"], 30)
        self.assertEqual(
            selection["canonical_identity_sha256"],
            "c30b518f9dafe3d46128849725e1f2f8fdce33239fbf6ade8603d66a64f0ffa5",
        )

        identity = [
            {
                key: row[key]
                for key in ("path", "size_bytes", "etag", "last_modified")
            }
            for row in self.inventory["selected_objects"]
        ]
        canonical = json.dumps(
            identity,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode()
        self.assertEqual(len(canonical), selection["canonical_identity_bytes"])
        self.assertEqual(hashlib.sha256(canonical).hexdigest(), selection["canonical_identity_sha256"])

    def test_inventory_contains_only_exact_raw_source_prefixes(self):
        rows = self.inventory["selected_objects"]
        self.assertEqual(len(rows), 1340)
        self.assertEqual(sum(row["size_bytes"] for row in rows), 7_249_113_684)
        self.assertEqual([row["path"] for row in rows], sorted(row["path"] for row in rows))
        self.assertTrue(
            all("/eeg/" in row["path"] or "/sourcedata/beh/" in row["path"] for row in rows)
        )
        self.assertTrue(all(not row["path"].startswith("derivatives/") for row in rows))
        self.assertTrue(all(not row["path"].endswith("_scans.tsv") for row in rows))
        self.assertEqual(
            {row["subject"] for row in rows},
            {f"sub-{index:02d}" for index in range(1, 16)},
        )
        self.assertEqual(
            {row["role"] for row in rows},
            {
                "ball_sidecar",
                "ball_stream",
                "channels",
                "coordsystem",
                "eeg_header",
                "eeg_marker",
                "eeg_sidecar",
                "eeg_signal",
                "electrodes",
                "events",
                "leap_sidecar",
                "leap_stream",
            },
        )

    def test_split_creates_a_true_cue_action_reversal(self):
        split = self.research["prospective_partition"]
        self.assertEqual(split["unit"], "participant_by_moving_hand")
        self.assertEqual(split["unit_count"], 30)
        self.assertEqual(split["fit_condition"], "congruent_red_trials_only")
        self.assertEqual(split["sealed_final_condition"], "incongruent_yellow_trials_only")
        self.assertTrue(split["same_frozen_predictions_scored_against_both_final_targets"])
        self.assertFalse(split["row_random_split_allowed"])
        self.assertFalse(split["cross_participant_fit_allowed"])
        self.assertFalse(split["cross_hand_fit_allowed"])
        self.assertFalse(split["final_condition_used_for_model_selection"])
        self.assertFalse(split["target_derived_exclusion_allowed"])
        self.assertTrue(split["all_15_participants_and_30_units_required"])

    def test_model_is_fixed_small_causal_in_samples_and_not_real_time(self):
        model = self.research["frozen_model_recommendation"]
        self.assertEqual(model["family_id"], "fixed_low_frequency_shrinkage_lda")
        self.assertEqual(model["passband_hz"], [0.5, 4.0])
        self.assertEqual(model["analysis_window_seconds_relative_to_registered_stop"], [-1.0, 0.0])
        self.assertEqual(model["time_bins"], 4)
        self.assertEqual(model["bin_duration_seconds"], 0.25)
        self.assertEqual(model["expected_feature_dimension_at_32_EEG_channels"], 160)
        self.assertEqual(model["selection_candidate_count"], 1)
        self.assertEqual(model["hyperparameter_search_runs"], 0)
        self.assertFalse(model["larger_or_deep_model_allowed"])
        self.assertEqual(model["right_context_seconds"], 0.0)
        self.assertIn("offline", model["operational_causality"])
        self.assertFalse(model["end_to_end_latency_measured"])

    def test_kinematic_guard_hides_direction_and_precedes_motion(self):
        guard = self.research["kinematic_guard_recommendation"]
        self.assertEqual(guard["onset_source"], "absolute_Leap_speed_only")
        self.assertFalse(guard["direction_sign_available_to_predictive_code"])
        self.assertEqual(guard["minimum_motion_guard_ms"], 30)
        self.assertTrue(guard["window_is_half_open"])
        self.assertEqual(guard["failed_guard_action"], "park_before_prediction_not_post_hoc_exclude")
        self.assertFalse(guard["real_time_claim_allowed"])

    def test_controls_record_EOG_and_keep_physiology_nonselecting(self):
        controls = set(self.research["mandatory_parallel_conditions"])
        required = {
            "same_primary_predictions_scored_against_visual_target",
            "central_C3_C4_Cz_EEG",
            "HEOG_VEOG_only",
            "fit_only_EOG_orthogonalized_whole_head_EEG",
            "event_index_and_timing_only",
            "train_only_no_signal_prior",
            "fixed_train_label_derangement",
            "fixed_final_run_displacement",
            "kinematic_onset_guard_audit",
        }
        self.assertTrue(required.issubset(controls))
        gates = self.research["prospective_gate_recommendations"]
        self.assertFalse(gates["H2_recorded_peripheral_and_timing_controls"]["EOG_proxy_failure_proves_brain_specific_origin"])
        self.assertFalse(gates["H3_motor_compatible_spatiotemporal_support"]["physiology_can_rescue_failed_H1_or_H2"])

    def test_primary_gate_scores_the_same_predictions_against_opposites(self):
        h1 = self.research["prospective_gate_recommendations"]["H1_action_over_cue_reversal"]
        self.assertEqual(h1["minimum_pooled_action_balanced_accuracy"], 0.6)
        self.assertEqual(h1["minimum_macro_participant_action_balanced_accuracy"], 0.6)
        self.assertEqual(h1["minimum_participants_above_0_5_action_balanced_accuracy"], 12)
        self.assertLessEqual(h1["maximum_exact_participant_sign_flip_p"], 0.01)
        self.assertEqual(h1["minimum_macro_action_minus_visual_target_margin"], 0.2)
        self.assertEqual(h1["maximum_macro_visual_target_balanced_accuracy"], 0.4)
        self.assertEqual(h1["scoring_unit"], "participant")
        self.assertFalse(h1["pooled_trial_only_claim_allowed"])

    def test_router_localizes_cue_bound_action_aligned_and_motor_compatible_outcomes(self):
        router = self.research["ordered_future_router"]
        self.assertEqual(
            [row["verdict"] for row in router],
            ["IACKD-R0", "IACKD-R1", "IACKD-R2", "IACKD-R3", "IACKD-R4"],
        )
        self.assertIn("cue_bound", router[1]["maximum_claim"])
        self.assertIn("source_unresolved", router[2]["maximum_claim"])
        self.assertIn("not_brain_specific", router[4]["maximum_claim"])

    def test_resource_envelope_fits_the_approved_machine_boundary(self):
        resources = self.research["future_resource_envelope"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["concurrent_numerical_jobs"], 1)
        self.assertLessEqual(resources["exact_selected_payload_bytes"], 10 << 30)
        self.assertLessEqual(resources["maximum_provider_payload_bytes"], 10 << 30)
        self.assertLessEqual(resources["maximum_peak_rss_bytes"], 2 << 30)
        self.assertLessEqual(resources["maximum_private_generated_bytes"], 512 << 20)
        self.assertGreaterEqual(resources["minimum_free_disk_bytes_before_acquisition"], 20 << 30)
        self.assertEqual(resources["downloaded_published_derivatives"], 0)
        self.assertEqual(resources["retries"], 0)
        self.assertEqual(resources["reruns"], 0)

    def test_document_and_queue_preserve_the_claim_boundary(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("IACKD-1 Cue-to-Action Reversal", document)
        self.assertIn("same predictions", document)
        self.assertIn("7,249,113,684", document)
        self.assertIn("IACKD-R4", document)
        self.assertIn("Scientific claim not established", document)
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("IACKD-1 Cue-to-Action Reversal", queue)
        self.assertIn("no iackd payload content", queue.lower())


if __name__ == "__main__":
    unittest.main()
