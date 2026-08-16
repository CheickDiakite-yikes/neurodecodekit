import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_machine_stable_cohort_and_neural_control_research.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_MACHINE_STABLE_COHORT_AND_NEURAL_CONTROL_RESEARCH.md"


class Marc2MachineStableCohortAndNeuralControlResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_is_research_only(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_machine_stable_cohort_and_neural_control_research",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["status"],
            "tier_A_architecture_research_no_private_or_scientific_authority",
        )

    def test_predecessor_preserves_consumed_failure(self):
        predecessor = self.record["predecessor"]
        self.assertEqual(predecessor["lane_id"], "MARC2-VR3")
        self.assertEqual(predecessor["result_route"], "MARC2VDR-F01")
        self.assertEqual(predecessor["result_CI_run_id"], 31964995980)
        self.assertTrue(predecessor["result_both_required_jobs_green"])
        self.assertEqual(predecessor["private_input_bytes"], 0)
        self.assertFalse(predecessor["real_cohort_identity_available"])
        self.assertFalse(predecessor["retry_or_rerun_available"])

    def test_ordered_work_orders_keep_science_after_cohort(self):
        orders = self.record["architecture"]["ordered_work_orders"]
        self.assertEqual(
            orders,
            [
                "MARC2-VR4-machine-stable-structural-freeze",
                "MARC2-FW2-bounded-member-acquisition-and-semantic-qualification",
                "MARC2-CIL1-target-firewalled-neural-control-experiment",
            ],
        )
        self.assertFalse(self.record["architecture"]["FW2_before_real_cohort_freeze"])

    def test_machine_readiness_is_reversible_and_diagnostic(self):
        design = self.record["VR4_design"]
        self.assertTrue(design["reversible_readiness_precedes_irreversible_consumption"])
        self.assertFalse(design["machine_only_timeout_consumes_private_content_open"])
        self.assertEqual(design["maximum_wait_seconds"], 600)
        self.assertEqual(design["minimum_poll_interval_seconds"], 5)
        self.assertEqual(design["consecutive_passing_samples"], 3)
        self.assertTrue(design["specific_machine_refusal_and_exact_safe_value_required"])
        self.assertFalse(design["output_root_or_private_path_operation_before_readiness"])

    def test_irreversible_boundary_and_source_invariants_are_preserved(self):
        design = self.record["VR4_design"]
        self.assertIn("marker", design["consumption_boundary"])
        self.assertEqual(design["post_marker_retry_rerun_resume_repair_or_fallback_limit"], 0)
        self.assertEqual(design["private_source_bytes"], 418755)
        self.assertEqual(design["source_rows"], 1227)
        self.assertEqual(design["source_bundles"], 238)
        self.assertEqual(design["eligible_bundles"], 195)
        self.assertEqual(design["valid_ineligible_bundles"], 43)

    def test_FW2_stays_bounded_and_cannot_download_whole_archive(self):
        design = self.record["FW2_design"]
        self.assertFalse(design["whole_archive_download_allowed"])
        self.assertTrue(design["selected_member_range_streaming_only"])
        self.assertLess(design["network_transfer_cap_bytes"], design["whole_archive_bytes"])
        self.assertEqual(design["network_transfer_cap_bytes"], 10 * 1024**3)
        self.assertFalse(design["heldout_target_delivery_to_model"])

    def test_four_requested_control_anchors_are_exact(self):
        mapping = self.record["CIL1_design"]["maintainer_anchor_mapping"]
        self.assertEqual(
            mapping,
            {
                "signal": "P-plus-E-matched-signal",
                "derangement": "P-plus-D-E-target-independent-derangement",
                "timing": "B1-timing",
                "no_signal": "B0-no-signal",
            },
        )

    def test_target_firewall_and_derangement_are_strict(self):
        design = self.record["CIL1_design"]
        self.assertTrue(design["derangement_is_target_independent"])
        self.assertTrue(design["derangement_has_no_fixed_points"])
        self.assertTrue(design["continuous_target_blind_heldout_probability_streams"])
        self.assertFalse(design["heldout_onsets_available_to_model_stage"])
        self.assertFalse(design["heldout_targets_available_to_model_stage"])
        self.assertTrue(
            design["prediction_freeze_remote_green_before_combined_onset_and_target_delivery"]
        )

    def test_primary_endpoint_and_candidate_thresholds_are_not_preregistered(self):
        design = self.record["CIL1_design"]
        self.assertEqual(
            design["primary_endpoint"],
            "participant_macro_log_loss_P_minus_P_plus_E",
        )
        self.assertEqual(design["candidate_minimum_mean_gain_nats_per_trial"], 0.02)
        self.assertFalse(design["candidate_thresholds_are_preregistered_now"])
        self.assertTrue(design["participant_level_inference_primary"])
        self.assertFalse(design["pooled_trial_significance_scientific"])

    def test_compute_and_storage_ceilings_are_small(self):
        resources = self.record["future_resource_ceilings"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertLessEqual(resources["maximum_model_fits"], 304)
        self.assertLessEqual(resources["maximum_target_blind_prediction_sets"], 512)
        self.assertLessEqual(resources["analysis_peak_RSS_bytes"], 768 * 1024**2)
        self.assertEqual(resources["provider_calls"], 0)
        self.assertEqual(resources["hardware_operations"], 0)

    def test_every_authority_and_access_counter_is_zero(self):
        self.assertTrue(all(not value for value in self.record["authorization_state"].values()))
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_next_gates_require_cohort_semantics_freeze_and_score_order(self):
        gates = self.record["next_gates"]
        self.assertTrue(gates["fresh_Tier_C_decision_required_for_one_private_content_open"])
        self.assertTrue(gates["real_cohort_freeze_required_before_FW2_preregistration"])
        self.assertTrue(gates["FW2_semantic_qualification_required_before_CIL1_preregistration"])
        self.assertTrue(gates["target_blind_prediction_freeze_required_before_one_score"])

    def test_claim_boundary_stays_narrow(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("Within-person", boundary["maximum_future_claim"])
        self.assertIn("timing EOG", boundary["maximum_future_claim"])
        self.assertIn("thought decoding", boundary["not_established_even_after_future_pass"])
        self.assertFalse(boundary["current_scientific_value"])

    def test_document_is_explicit_about_research_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("This document is not the VR4 or FW2 preregistration", text)
        self.assertIn("P+D(E)", text)
        self.assertIn("Engineering capability specified", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
