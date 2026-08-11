import hashlib
import json
import re
import unittest
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries" / "iackd_role_aware_dual_reversal_contract.v0.json"
INVENTORY_PATH = ROOT / "registries" / "iackd_openneuro_metadata_inventory.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run_key(row: dict[str, object]) -> str | None:
    path = str(row["path"])
    if row["role"] in {"coordsystem", "electrodes"}:
        return None
    if "/eeg/" in path:
        match = re.search(
            r"(?P<subject>sub-[0-9]+).*acq-(?P<hand>left|right)_run-(?P<run>[0-9]+)",
            path,
        )
    else:
        match = re.search(
            r"(?P<subject>sub-[0-9]+).*run-(?P<run>[0-9]+)_hand-(?P<hand>left|right)",
            path,
        )
    if match is None:
        raise AssertionError(f"unmatched inventory path: {path}")
    return f"{match['subject']}:{match['hand']}:{match['run']}"


class IACKDRoleAwareDualReversalContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    def test_schema_status_and_scope_are_prospective(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_contract",
        )
        self.assertEqual(
            self.contract["contract_id"],
            "IACKD-2-role-aware-dual-reversal-contract-v0",
        )
        self.assertIn("unauthorized", self.contract["status"])
        self.assertIn("both opposing", self.contract["objective"])
        self.assertFalse(self.contract["authorization"]["real_or_public_payload_access"])
        self.assertFalse(self.contract["authorization"]["training_inference_or_scoring"])

    def test_bound_public_artifact_hashes_are_current(self) -> None:
        for binding in self.contract["bindings"].values():
            if not isinstance(binding, dict) or "path" not in binding:
                continue
            self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_green_H2_and_H3_proof_chain_is_exact(self) -> None:
        bindings = self.contract["bindings"]
        h2 = bindings["consumed_H2_role_geometry_result"]
        self.assertEqual(h2["commit"], "580f11fc60d2882a11bf4e765bb33b60ffc0bd04")
        self.assertEqual(h2["CI_run_id"], 31444931063)
        self.assertEqual(h2["route"], "IACKDR-R1")
        self.assertTrue(h2["consumed"])
        self.assertFalse(h2["rerun_allowed"])

        h3 = bindings["generated_H3_source_semantics_result"]
        self.assertEqual(h3["commit"], "cff8d79208a8afa11b3da036f69626236c9664e2")
        self.assertEqual(h3["CI_run_id"], 31447418426)
        self.assertTrue(h3["both_required_jobs_green"])
        self.assertFalse(h3["real_reader_validated"])

    def test_inventory_identity_and_streaming_shape_recompute(self) -> None:
        selected = self.inventory["selected_objects"]
        source = self.contract["dataset_binding"]
        self.assertEqual(len(selected), source["selected_object_count"])
        self.assertEqual(sum(row["size_bytes"] for row in selected), source["selected_payload_bytes"])
        self.assertEqual(
            self.inventory["selection"]["canonical_identity_sha256"],
            source["canonical_expanded_inventory_sha256"],
        )

        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        geometry: list[dict[str, object]] = []
        for row in selected:
            key = _run_key(row)
            if key is None:
                geometry.append(row)
            else:
                groups[key].append(row)

        streaming = self.contract["fresh_streaming_contract"]
        self.assertEqual(len(groups), streaming["run_group_count"])
        self.assertEqual(Counter(len(rows) for rows in groups.values()), Counter({10: 128}))
        self.assertEqual(max(sum(row["size_bytes"] for row in rows) for rows in groups.values()), streaming["largest_run_group_bytes"])
        self.assertEqual(max(row["size_bytes"] for row in selected), streaming["largest_individual_object_bytes"])
        self.assertEqual(len(geometry), streaming["geometry_object_count"])
        self.assertEqual(sum(row["size_bytes"] for row in geometry), streaming["geometry_bytes"])

        metadata = self.contract["metadata_reverification"]
        self.assertFalse(metadata["payload_request_before_exact_match"])
        self.assertEqual(metadata["expected_listing_pages"], 2)
        self.assertEqual(metadata["expected_listed_object_count"], 1679)
        self.assertEqual(metadata["expected_listed_total_bytes"], 7966799433)

    def test_source_semantics_preserve_three_layers(self) -> None:
        semantics = self.contract["source_semantics_contract"]
        self.assertEqual(semantics["policy_sha256"], "1117c90d77971ee0ec2f5e138bdf9ea76eef412a4b5c44c1d2b88c31f88f39f4")
        self.assertEqual(len(semantics["predictive_EEG_names"]), 26)
        self.assertEqual(len(set(semantics["predictive_EEG_names"])), 26)
        self.assertEqual(semantics["optional_nonpredictive_EEG_names"], ["M1", "M2"])
        self.assertEqual(semantics["ocular_control_names"], ["HEOG", "VEOG"])
        self.assertEqual(semantics["trigger_control_names"], ["Trigger"])
        self.assertEqual(semantics["source_type_for_controls"], "MISC")
        self.assertEqual(semantics["sampling_rate_hz"], 1024)
        self.assertEqual(semantics["regional_views"]["central"], ["C3", "C4", "Cz"])
        self.assertEqual(semantics["regional_views"]["occipital"], ["O1", "Oz", "O2"])
        self.assertFalse(semantics["MNE_inferred_types_authoritative"])

    def test_dual_arms_are_symmetric_disjoint_and_both_required(self) -> None:
        split = self.contract["split_contract"]
        arms = {row["arm_id"]: row for row in split["arms"]}
        self.assertEqual(set(arms), {"C2I", "I2C"})
        self.assertEqual(arms["C2I"]["fit_action_to_visual_sign"], 1)
        self.assertEqual(arms["C2I"]["final_action_to_visual_sign"], -1)
        self.assertEqual(arms["I2C"]["fit_action_to_visual_sign"], -1)
        self.assertEqual(arms["I2C"]["final_action_to_visual_sign"], 1)
        self.assertTrue(all(row["cue_surrogate_is_exact_negative_action_on_final"] for row in arms.values()))
        self.assertTrue(split["condition_rows_disjoint_between_arms_within_partition"])
        self.assertTrue(split["both_arms_required"])
        self.assertFalse(split["one_arm_may_rescue_other"])

        counts = split["maximum_pre_quality_control_counts"]
        self.assertEqual(counts["per_arm_fit_rows"] * 2, counts["both_arms_fit_rows"])
        self.assertEqual(counts["per_arm_final_rows"] * 2, counts["both_arms_final_rows"])
        self.assertEqual(counts["both_arms_fit_rows"] + counts["both_arms_final_rows"], 7040)

    def test_target_firewall_keeps_all_final_direction_out(self) -> None:
        firewall = self.contract["target_firewall"]
        self.assertTrue(firewall["fit_labels_arm_and_fit_partition_only"])
        self.assertTrue(firewall["same_final_prediction_scored_against_two_views"])
        self.assertTrue(firewall["final_target_views_exact_opposites"])
        self.assertTrue(firewall["all_predictions_frozen_before_target_delivery"])
        self.assertEqual(firewall["target_deliveries"], 1)
        for key, value in firewall["visible_to_predictive_code_before_freeze"].items():
            if key.endswith("_hashes") or key in {"arm_identity", "opaque_trial_identity"}:
                self.assertTrue(value, key)
            else:
                self.assertFalse(value, key)

        builder = self.contract["isolated_target_builder"]
        self.assertEqual(builder["minimum_absolute_hand_displacement_mm"], 5.0)
        self.assertEqual(builder["minimum_absolute_ball_displacement_pixels"], 5.0)
        self.assertTrue(builder["ball_move_direct_field_must_agree"])
        self.assertFalse(builder["ball_move_direct_field_is_sole_target_source"])
        self.assertFalse(builder["signed_values_visible_to_predictive_code"])

    def test_model_dimensions_and_causality_are_exact(self) -> None:
        model = self.contract["model_contract"]
        self.assertEqual(model["primary_feature_dimension"], 26 * 5)
        self.assertEqual(model["central_feature_dimension"], 3 * 5)
        self.assertEqual(model["occipital_feature_dimension"], 3 * 5)
        self.assertEqual(model["ocular_feature_dimension"], 2 * 5)
        self.assertEqual(model["half_window_feature_dimension"], 26 * 3)
        self.assertEqual(model["right_context_seconds"], 0.0)
        self.assertTrue(model["producer_is_causal_in_samples"])
        self.assertFalse(model["end_to_end_latency_measured"])
        self.assertEqual(model["selection_candidate_count"], 1)
        self.assertEqual(model["hyperparameter_search_runs"], 0)

        dependencies = self.contract["dependency_contract"]
        self.assertEqual(
            dependencies["versions"],
            {
                "numpy": "2.5.2",
                "scipy": "1.18.0",
                "mne": "1.12.1",
                "scikit_learn": "1.9.0",
            },
        )
        self.assertFalse(dependencies["dependency_install_authorized_now"])
        self.assertFalse(dependencies["network_for_dependency_resolution"])

    def test_fit_prediction_and_scoring_counts_are_exact(self) -> None:
        fits = self.contract["fit_inventory"]
        predictions = self.contract["prediction_inventory"]
        self.assertEqual(len(fits["families"]), fits["fits_per_unit_per_arm"])
        self.assertEqual(
            fits["participant_hand_units"] * fits["arm_count"] * fits["fits_per_unit_per_arm"],
            fits["required_parameter_update_fits"],
        )
        self.assertEqual(len(predictions["conditions"]), predictions["sets_per_unit_per_arm"])
        self.assertEqual(
            predictions["participant_hand_units"] * predictions["arm_count"] * predictions["sets_per_unit_per_arm"],
            predictions["required_prediction_sets"],
        )
        self.assertEqual(fits["required_parameter_update_fits"], 660)
        self.assertEqual(predictions["required_prediction_sets"], 900)
        self.assertFalse(predictions["second_target_view_creates_prediction_set"])

    def test_primary_statistic_uses_weaker_arm_per_participant(self) -> None:
        statistics = self.contract["statistical_contract"]
        self.assertEqual(statistics["participant_count"], 15)
        self.assertEqual(statistics["exact_sign_assignments"], 32768)
        self.assertEqual(
            statistics["primary_participant_value"],
            "minimum_of_C2I_and_I2C_action_minus_cue_balanced_accuracy_margins",
        )
        self.assertTrue(statistics["hands_combined_within_participant_before_inference"])
        self.assertFalse(statistics["pooled_trial_substitution_allowed"])

    def test_gates_require_both_arms_and_registered_controls(self) -> None:
        gates = self.contract["gates"]
        self.assertTrue(gates["H1_symmetric_action_over_cue"]["every_threshold_applies_to_each_arm"])
        self.assertEqual(gates["H1_symmetric_action_over_cue"]["minimum_mean_participant_minimum_arm_margin"], 0.15)
        self.assertEqual(gates["H2_recorded_peripheral_visual_and_timing_controls"]["minimum_primary_minus_occipital_action_accuracy_each_arm"], 0.03)
        self.assertTrue(gates["H3_motor_compatible_central_support"]["every_threshold_applies_to_each_arm"])
        self.assertFalse(gates["H3_motor_compatible_central_support"]["physiology_may_rescue_H1_or_H2"])

    def test_router_is_ordered_and_claim_ceiling_remains_narrow(self) -> None:
        router = self.contract["ordered_router"]
        self.assertEqual(
            [row["route"] for row in router],
            ["IACKD2-R1", "IACKD2-R2", "IACKD2-R3", "IACKD2-R4", "IACKD2-R5", "IACKD2-R0"],
        )
        self.assertIn("both_arms", router[0]["condition"])
        self.assertIn("both_arms", router[4]["condition"])
        self.assertIn("not_brain_specific", router[4]["maximum_claim"])
        self.assertEqual(router[-1]["evaluation"], "final_catch_all")

    def test_resource_caps_are_storage_safe_and_exact(self) -> None:
        caps = self.contract["resource_caps"]
        acquisition = caps["future_acquisition_and_derivative_build"]
        self.assertEqual(acquisition["payload_requests"], 1340)
        self.assertEqual(acquisition["payload_bytes"], 7249113684)
        self.assertEqual(acquisition["largest_raw_run_group_bytes"], 82064564)
        self.assertLessEqual(acquisition["peak_incremental_disk_bytes"], 1024**3)
        self.assertGreaterEqual(acquisition["minimum_free_disk_bytes"], 10 * 1024**3)
        self.assertEqual((acquisition["CPU_threads"], acquisition["workers"], acquisition["concurrent_numerical_jobs"]), (1, 1, 1))

        analysis = caps["future_fit_freeze_and_score"]
        self.assertEqual(analysis["required_parameter_update_fits"], 660)
        self.assertEqual(analysis["required_prediction_sets"], 900)
        self.assertEqual((analysis["target_deliveries"], analysis["scoring_events"]), (1, 1))
        self.assertEqual((analysis["retries"], analysis["reruns"], analysis["post_target_updates"]), (0, 0, 0))

    def test_stage_order_keeps_real_access_behind_new_Tier_C_decision(self) -> None:
        stages = self.contract["ordered_stages"]
        self.assertTrue(stages["stage_B_generated_implementation"]["eligible_only_after_registration_commit_pushed_and_both_CI_jobs_green"])
        self.assertTrue(stages["stage_B_generated_implementation"]["generated_fixtures_and_mocked_transport_only"])
        self.assertFalse(stages["stage_B_generated_implementation"]["real_or_public_data_access"])
        self.assertTrue(stages["stage_C_request_and_decision"]["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(stages["stage_C_request_and_decision"]["currently_authorized"])
        self.assertTrue(stages["stage_C_execution"]["old_retained_bundle_forbidden"])
        self.assertFalse(stages["stage_C_execution"]["currently_authorized"])

    def test_current_access_counters_are_zero(self) -> None:
        self.assertTrue(all(value == 0 for value in self.contract["current_access_counters"].values()))

    def test_document_has_required_boundaries(self) -> None:
        document = (ROOT / self.contract["bindings"]["human_preregistration"]["path"]).read_text(encoding="utf-8")
        self.assertIn("Engineering capability proposed:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("The existing Git-ignored IACKD bundle is forbidden", document)
        self.assertIn("No substitution", document)
        self.assertIn("no neural effect", self.contract["claim_boundary"]["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
