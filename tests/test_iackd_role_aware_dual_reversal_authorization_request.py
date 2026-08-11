import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_authorization_request.v0.json"
)
PACKET_PATH = (
    ROOT / "docs" / "IACKD_ROLE_AWARE_DUAL_REVERSAL_AUTHORIZATION_PACKET.md"
)
CONTRACT_PATH = (
    ROOT / "registries" / "iackd_role_aware_dual_reversal_contract.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries"
    / "iackd_role_aware_dual_reversal_synthetic_result.v0.json"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDRoleAwareDualReversalAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_request_is_all_false_and_waits_for_fresh_maintainer_words(self):
        self.assertEqual(
            self.request["status"], "awaiting_new_packet_bound_maintainer_decision"
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        authorization = self.request["authorization"]
        procedural = {
            "separate_authorization_only_record_required",
            "short_form_may_bind_after_request_is_remotely_green",
            "actual_user_words_must_be_quoted",
        }
        self.assertTrue(all(authorization[name] for name in procedural))
        self.assertTrue(
            all(
                value is False
                for name, value in authorization.items()
                if name not in procedural and isinstance(value, bool)
            )
        )
        self.assertFalse(authorization["earlier_continue_is_retroactive_authorization"])

    def test_green_registration_implementation_and_closeout_are_exact(self):
        registration = self.request["green_registration"]
        self.assertEqual(
            registration["commit"], "5bdab3055a8a1c5200b5ec6c0037e401d8c817ce"
        )
        self.assertEqual(registration["push_CI_run_id"], 31448911258)
        self.assertTrue(registration["both_required_jobs_green"])

        implementation = self.request["green_exact_generated_implementation"]
        self.assertEqual(
            implementation["commit"], "af7488ab1e8f49854733425a96bbdc9c222ef02b"
        )
        self.assertEqual(implementation["push_CI_run_id"], 31451262840)
        self.assertEqual(implementation["base_python_job_id"], 93655939217)
        self.assertEqual(implementation["optional_neuro_job_id"], 93655939167)
        self.assertTrue(implementation["both_required_jobs_green"])
        self.assertFalse(implementation["registered_closeout_followed_first_failure"])

        closeout = self.request["green_generated_closeout"]
        self.assertEqual(
            closeout["commit"], "7bc45c94f6479564385e3e4d341145343c92b037"
        )
        self.assertEqual(closeout["push_CI_run_id"], 31452614232)
        self.assertEqual(closeout["base_python_job_id"], 93659819850)
        self.assertEqual(closeout["optional_neuro_job_id"], 93659819910)
        self.assertTrue(closeout["both_required_jobs_green"])

    def test_every_bound_artifact_hash_is_current(self):
        for binding in self.request["target_artifacts"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_generated_closeout_is_consumed_and_has_no_claim_value(self):
        closeout = self.request["green_generated_closeout"]
        self.assertTrue(closeout["registered_generated_closeout_consumed"])
        self.assertFalse(closeout["registered_generated_closeout_rerun_available"])
        self.assertEqual(closeout["synthetic_route"], "IACKD2-R5")
        self.assertFalse(closeout["synthetic_route_has_scientific_value"])
        state = self.result["execution_state"]
        self.assertTrue(state["registered_generated_closeout_consumed"])
        self.assertFalse(state["registered_generated_closeout_rerun_available"])
        self.assertFalse(state["real_execution_authorized"])

    def test_scope_matches_the_frozen_public_IACKD_contract(self):
        scope = self.request["requested_scope"]
        dataset = self.contract["dataset_binding"]
        self.assertEqual(scope["provider"], "OpenNeuro")
        self.assertEqual(scope["dataset_id"], "ds006840")
        self.assertEqual(scope["version"], "1.0.0")
        self.assertEqual(scope["participant_count"], dataset["participant_count"])
        self.assertEqual(
            scope["participant_hand_units"], dataset["participant_hand_unit_count"]
        )
        self.assertEqual(scope["BIDS_run_count"], dataset["bids_run_count"])
        self.assertEqual(scope["object_count"], dataset["selected_object_count"])
        self.assertEqual(scope["payload_bytes"], dataset["selected_payload_bytes"])
        self.assertEqual(
            scope["canonical_inventory_sha256"],
            dataset["canonical_expanded_inventory_sha256"],
        )
        self.assertEqual(scope["maximum_verdict"], "IACKD2-R5")

    def test_source_semantics_arms_and_model_inventory_are_exact(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["source_row_count_variants"], [29, 31])
        self.assertEqual(scope["predictive_EEG_channels"], 26)
        self.assertFalse(scope["optional_M1_M2_predictive"])
        self.assertEqual(scope["recorded_EOG_channels"], ["HEOG", "VEOG"])
        self.assertFalse(scope["trigger_predictive"])
        self.assertEqual(set(scope["arms"]), {"C2I", "I2C"})
        self.assertEqual(scope["required_parameter_update_fits"], 660)
        self.assertEqual(scope["required_prediction_sets"], 900)
        self.assertEqual(scope["model_selection_candidates"], 1)
        self.assertEqual(scope["hyperparameter_search_runs"], 0)

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.request["requested_access_order"]
        decision = order.index(
            "authorization_only_decision_commit_pushed_and_both_CI_jobs_green"
        )
        fixture = order.index(
            "generated_fixture_and_mock_transport_real_executor_qualification"
        )
        implementation = order.index(
            "exact_real_executor_implementation_commit_pushed_and_both_CI_jobs_green"
        )
        consumed = order.index("write_private_consumed_marker_before_first_real_request")
        acquisition = order.index(
            "one_exact_1340_object_fresh_streaming_acquisition_and_derivative_build"
        )
        fit = order.index("one_target_blind_660_fit_900_prediction_execution")
        freeze = order.index(
            "emit_aggregate_hash_only_prediction_freeze_without_individual_outputs"
        )
        green_freeze = order.index(
            "prediction_freeze_commit_pushed_and_both_CI_jobs_green"
        )
        score = order.index("one_combined_delivery_and_score_of_both_final_target_views")
        self.assertLess(decision, fixture)
        self.assertLess(fixture, implementation)
        self.assertLess(implementation, consumed)
        self.assertLess(consumed, acquisition)
        self.assertLess(acquisition, fit)
        self.assertLess(fit, freeze)
        self.assertLess(freeze, green_freeze)
        self.assertLess(green_freeze, score)

    def test_transport_and_streaming_are_one_pass_and_storage_safe(self):
        response = self.request["response_contract"]
        self.assertEqual(response["metadata_requests"], 4)
        self.assertEqual(response["payload_requests"], 1340)
        self.assertTrue(response["sequential"])
        self.assertEqual(response["maximum_concurrency"], 1)
        self.assertTrue(response["final_URL_must_equal_requested_URL"])
        self.assertTrue(response["Content_Length_must_equal_registered_size"])
        self.assertTrue(response["ETag_must_equal_registered_ETag"])
        self.assertEqual(response["Content_Encoding"], "identity_only")
        self.assertEqual(response["body_SHA256_passes_per_object"], 1)
        self.assertEqual(response["semantic_parse_passes_per_run"], 1)
        self.assertEqual((response["redirects"], response["retries"]), (0, 0))

        streaming = self.request["fresh_streaming_contract"]
        self.assertTrue(streaming["old_retained_IACKD_bundle_forbidden"])
        self.assertEqual(streaming["run_groups"], 128)
        self.assertEqual(streaming["objects_per_run_group"], 10)
        self.assertEqual(streaming["geometry_objects"], 60)
        self.assertEqual(streaming["maximum_concurrent_raw_run_groups"], 1)
        self.assertFalse(streaming["complete_raw_bundle_retained"])
        self.assertTrue(streaming["raw_group_removed_only_after_derivative_promotion"])
        self.assertFalse(streaming["preexisting_path_cleanup_allowed"])

    def test_target_firewall_hides_final_views_until_green_freeze(self):
        firewall = self.request["target_firewall"]
        self.assertTrue(firewall["fit_labels_arm_and_fit_partition_only"])
        self.assertEqual(
            firewall["final_target_values_visible_to_predictive_code_before_freeze"],
            0,
        )
        self.assertEqual(
            firewall[
                "final_signed_trajectories_visible_to_predictive_code_before_freeze"
            ],
            0,
        )
        self.assertTrue(firewall["target_free_final_features_only"])
        self.assertTrue(firewall["same_final_prediction_scored_against_two_views"])
        self.assertTrue(firewall["final_target_views_exact_opposites"])
        self.assertTrue(firewall["remote_green_freeze_required_before_target_delivery"])
        self.assertFalse(firewall["individual_predictions_in_public_freeze"])
        self.assertEqual((firewall["target_deliveries"], firewall["scoring_events"]), (1, 1))

    def test_resource_caps_match_contract_and_never_retain_full_bundle(self):
        caps = self.request["resource_caps"]
        generated = caps["generated_real_executor_qualification"]
        self.assertEqual(
            (generated["CPU_threads"], generated["workers"]),
            (1, 1),
        )
        self.assertEqual(generated["real_public_or_local_payload_reads"], 0)
        self.assertEqual(generated["network_bytes"], 0)

        acquisition = caps["streaming_acquisition_and_derivative_build"]
        contract_acquisition = self.contract["resource_caps"][
            "future_acquisition_and_derivative_build"
        ]
        self.assertEqual(acquisition, contract_acquisition)
        self.assertLessEqual(acquisition["peak_incremental_disk_bytes"], 1024**3)
        self.assertGreaterEqual(acquisition["minimum_free_disk_bytes"], 10 * 1024**3)

        analysis = caps["target_blind_fit_freeze_and_score"]
        contract_analysis = self.contract["resource_caps"][
            "future_fit_freeze_and_score"
        ]
        self.assertEqual(analysis, contract_analysis)
        self.assertEqual((analysis["retries"], analysis["reruns"]), (0, 0))
        self.assertEqual(analysis["post_target_updates"], 0)

    def test_all_current_real_and_forbidden_counters_are_zero(self):
        for name, value in self.request["current_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_future_decision_shape_is_exact_and_one_shot(self):
        shape = self.request["required_decision_shape"]
        self.assertEqual(
            shape["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_authorization_decision",
        )
        self.assertTrue(shape["maintainer_words_must_be_actual_and_nonempty"])
        self.assertTrue(shape["packet_request_contract_implementation_and_closeout_hashes_bound"])
        self.assertEqual(shape["real_payload_requests"], 1340)
        self.assertEqual(shape["real_payload_bytes"], 7249113684)
        self.assertEqual(shape["fresh_streaming_acquisition_invocations"], 1)
        self.assertEqual(shape["parameter_update_fits"], 660)
        self.assertEqual(shape["prediction_sets"], 900)
        self.assertEqual(shape["prediction_freeze_commits"], 1)
        self.assertEqual((shape["target_deliveries"], shape["scoring_events"]), (1, 1))
        self.assertEqual((shape["retries"], shape["reruns"]), (0, 0))
        self.assertEqual(shape["maximum_verdict"], "IACKD2-R5")

    def test_forbidden_scope_and_claim_language_are_explicit(self):
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "open_stat_hash_parse_move_or_delete_old_retained_IACKD_bundle",
            "any_object_outside_exact_1340_object_allowlist",
            "S20_S21_S24_S25_SpanishBCBL_PhysioNet_raw_FIF_or_MAT_access",
            "target_derived_quality_filtering_exclusion_selection_normalization_or_adaptation",
            "larger_additional_deep_CML_pretrained_foundation_or_language_model",
            "preexisting_path_cleanup_or_operation_on_another_project",
            "second_target_delivery_second_score_or_post_target_update",
            "scientific_claim_upgrade_beyond_IACKD2_R5_or_to_brain_specific_origin",
        }
        self.assertTrue(required.issubset(forbidden))
        self.assertFalse(self.request["claim_boundary"]["current_scientific_claim_upgrade"])
        packet = " ".join(self.packet.split())
        self.assertIn("This packet authorizes nothing by itself", packet)
        self.assertIn("cannot authorize later content access retroactively", packet)
        self.assertIn("a fresh unambiguous `continue`", packet)
        self.assertIn("Even `IACKD2-R5` is not proof of brain-specific origin", packet)
        self.assertIn("Scientific claim not established by this request", packet)


if __name__ == "__main__":
    unittest.main()
