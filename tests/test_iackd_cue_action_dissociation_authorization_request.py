import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = ROOT / "registries/iackd_cue_action_dissociation_authorization_request.v0.json"
CONTRACT_PATH = ROOT / "registries/iackd_cue_action_dissociation_contract.v0.json"
PACKET_PATH = ROOT / "docs/IACKD_CUE_ACTION_DISSOCIATION_AUTHORIZATION_PACKET.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDCueActionDissociationAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_all_false_and_waits_for_a_new_packet_bound_decision(self):
        self.assertEqual(
            self.request["status"],
            "awaiting_new_packet_bound_maintainer_decision",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        authorization = self.request["authorization"]
        allowed_true = {
            "separate_authorization_only_record_required",
            "short_form_may_bind_after_request_is_remotely_green",
            "actual_user_words_must_be_quoted",
        }
        self.assertTrue(all(authorization[key] for key in allowed_true))
        self.assertTrue(
            all(
                value is False
                for key, value in authorization.items()
                if key not in allowed_true and isinstance(value, bool)
            )
        )
        self.assertFalse(authorization["earlier_continue_is_retroactive_authorization"])

    def test_registration_commit_CI_and_artifact_hashes_are_exact(self):
        registration = self.request["registration"]
        self.assertEqual(registration["commit"], "e42b79961d1fafe5cf406beaf868388ecbcbfb09")
        self.assertEqual(registration["push_ci_run_id"], 31_400_450_392)
        self.assertEqual(registration["base_python_job_id"], 93_493_810_963)
        self.assertEqual(registration["optional_neuro_job_id"], 93_493_811_025)
        self.assertTrue(registration["remote_registration_is_green"])
        for binding in self.request["target"].values():
            if isinstance(binding, dict) and "path" in binding:
                self.assertEqual(binding["sha256"], sha256(ROOT / binding["path"]))

    def test_scope_binds_exact_dataset_split_models_and_router(self):
        scope = self.request["requested_scope"]
        self.assertEqual(scope["provider"], "OpenNeuro")
        self.assertEqual(scope["dataset_id"], "ds006840")
        self.assertEqual(scope["version"], "1.0.0")
        self.assertEqual(scope["participant_count"], 15)
        self.assertEqual(scope["participant_hand_units"], 30)
        self.assertEqual(scope["object_count"], 1340)
        self.assertEqual(scope["payload_bytes"], 7_249_113_684)
        self.assertEqual(scope["primary_model_family"], "fixed_low_frequency_shrinkage_lda")
        self.assertEqual(scope["model_selection_candidates"], 1)
        self.assertEqual(scope["maximum_parameter_update_fits"], 300)
        self.assertEqual(scope["required_prediction_sets"], 420)
        self.assertEqual(scope["maximum_target_blind_inference_calls"], 420)
        self.assertEqual(scope["final_target_deliveries"], 1)
        self.assertEqual(scope["final_scoring_events"], 1)
        self.assertEqual(scope["maximum_verdict"], "IACKD-R4")

    def test_order_requires_green_decision_implementation_and_freeze(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_transport_only_implementation"),
        )
        self.assertLess(
            order.index("implementation_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_exact_1340_object_acquisition"),
        )
        self.assertLess(
            order.index("one_exact_1340_object_acquisition"),
            order.index("one_target_blind_128_run_analysis"),
        )
        self.assertLess(
            order.index("hash_only_prediction_freeze_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_combined_delivery_and_score_of_both_final_target_views"),
        )

    def test_resource_caps_respect_CPU_storage_and_10_GiB_ceiling(self):
        acquisition = self.request["resource_caps"]["acquisition"]
        self.assertEqual(acquisition["invocations"], 1)
        self.assertEqual(acquisition["cpu_threads"], 1)
        self.assertEqual(acquisition["workers"], 1)
        self.assertEqual(acquisition["payload_requests"], 1340)
        self.assertEqual(acquisition["payload_bytes"], 7_249_113_684)
        self.assertLessEqual(acquisition["network_payload_ceiling_bytes"], 10 << 30)
        self.assertLessEqual(acquisition["peak_incremental_disk_bytes"], 9 << 30)
        self.assertGreaterEqual(acquisition["minimum_free_disk_bytes"], 20 << 30)
        self.assertEqual(acquisition["retries"], 0)
        self.assertEqual(acquisition["reruns"], 0)

        analysis = self.request["resource_caps"]["analysis_and_scoring"]
        self.assertEqual(analysis["cpu_threads"], 1)
        self.assertEqual(analysis["maximum_parameter_update_fits"], 300)
        self.assertEqual(analysis["required_prediction_sets"], 420)
        self.assertEqual(analysis["final_target_deliveries"], 1)
        self.assertEqual(analysis["final_scoring_events"], 1)
        self.assertEqual(analysis["network_bytes"], 0)
        self.assertEqual(analysis["new_payload_bytes"], 0)
        self.assertEqual(analysis["retries"], 0)
        self.assertEqual(analysis["reruns"], 0)
        self.assertEqual(analysis["post_target_updates"], 0)

    def test_counters_preserve_metadata_history_and_zero_real_work(self):
        counters = self.request["current_access_counters"]
        allowed_nonzero = {
            "inherited_retained_S3_listing_bodies",
            "inherited_retained_openneuro_root_metadata_bodies",
            "inherited_retained_primary_article_bodies",
            "inherited_selected_object_names_observed",
        }
        self.assertTrue(all(counters[key] > 0 for key in allowed_nonzero))
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)
        )

    def test_forbidden_scope_blocks_expansion_models_and_claims(self):
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "any_object_outside_the_1340_hash_bound_allowlist",
            "published_derivative_participant_demographic_or_subject_scan_table_download",
            "S20_S21_S24_S25_SpanishBCBL_PhysioNet_raw_FIF_or_MAT_access",
            "row_random_cross_participant_or_cross_hand_fit",
            "final_target_or_signed_trajectory_use_before_green_freeze",
            "filter_window_channel_model_threshold_seed_or_hyperparameter_search",
            "larger_additional_deep_CML_pretrained_foundation_or_language_model",
            "retry_rerun_second_delivery_second_score_or_post_target_update",
            "claim_upgrade_beyond_IACKD_R4",
        }
        self.assertTrue(required.issubset(forbidden))
        self.assertGreaterEqual(len(forbidden), 18)

    def test_next_gate_requires_request_green_then_actual_user_words(self):
        next_gate = self.request["next_gate"]
        self.assertTrue(next_gate["request_commit_required"])
        self.assertTrue(next_gate["request_commit_push_required"])
        self.assertTrue(next_gate["both_remote_CI_jobs_green_required"])
        self.assertTrue(next_gate["assistant_must_identify_packet_commit_CI_and_scope"])
        self.assertFalse(next_gate["new_packet_bound_user_decision_received"])
        self.assertFalse(next_gate["decision_record_exists"])
        self.assertFalse(next_gate["implementation_may_begin"])
        self.assertFalse(next_gate["acquisition_may_begin"])
        self.assertFalse(next_gate["analysis_may_begin"])
        self.assertFalse(next_gate["scoring_may_begin"])

    def test_claim_ceiling_and_packet_language_are_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertIn("within-IACKD", boundary["maximum_future_claim"])
        self.assertIn("brain-specific origin", boundary["not_established_even_if_IACKD_R4"])
        self.assertFalse(boundary["current_scientific_claim_upgrade"])
        packet = " ".join(self.packet.split())
        self.assertIn("Scientific claim not established by this request", packet)
        self.assertIn("cannot be applied retroactively", packet)
        self.assertIn("a new unambiguous `continue`", packet)


if __name__ == "__main__":
    unittest.main()
