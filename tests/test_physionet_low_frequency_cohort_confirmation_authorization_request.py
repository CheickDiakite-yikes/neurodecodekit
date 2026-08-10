import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_authorization_request.v0.json"
)
CONTRACT_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_contract.v0.json"
)
PACKET_PATH = (
    ROOT
    / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_AUTHORIZATION_PACKET.md"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyCohortAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_request_is_all_false_and_awaits_exact_decision(self):
        self.assertEqual(
            self.request["status"],
            "awaiting_exact_user_authorization",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        authorization = self.request["authorization"]
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        permitted_true = {"separate_authorization_only_record_required"}
        self.assertTrue(
            all(
                value is False
                for key, value in authorization.items()
                if key not in permitted_true | {"exact_authorization_sentence"}
            )
        )

    def test_registration_commit_and_remote_green_jobs_are_exact(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "716e5432498052b78cb799c9f4e3bfbae68e3ad2",
        )
        self.assertEqual(registration["push_ci_run_id"], 31_354_565_966)
        self.assertEqual(registration["base_python_job_id"], 93_351_737_101)
        self.assertEqual(registration["optional_neuro_job_id"], 93_351_737_088)
        self.assertEqual(registration["push_ci_conclusion"], "success")
        self.assertEqual(registration["base_python_job_conclusion"], "success")
        self.assertEqual(registration["optional_neuro_job_conclusion"], "success")
        self.assertTrue(registration["remote_registration_is_green"])
        self.assertEqual(registration["local_focused_tests"], 26)
        self.assertEqual(registration["local_base_suite_tests"], 1_476)
        self.assertEqual(registration["local_base_suite_expected_skips"], 168)
        self.assertEqual(registration["local_optional_suite_tests"], 1_532)
        self.assertEqual(registration["local_optional_suite_expected_skips"], 34)

    def test_every_bound_artifact_hash_matches(self):
        for key, binding in self.request["target"].items():
            if not key.endswith("_artifact"):
                continue
            path = ROOT / binding["path"]
            self.assertTrue(path.is_file(), binding["path"])
            self.assertEqual(binding["sha256"], sha256(path), binding["path"])
        self.assertTrue(
            self.request["target"]["registration_snapshot_must_remain_immutable"]
        )

    def test_git_blob_bindings_cover_the_exact_registration_tree(self):
        target = self.request["target"]
        self.assertEqual(
            target["preregistration_artifact"]["git_blob_sha1"],
            "0378754332509057646cdc95e83210a7f15007de",
        )
        self.assertEqual(
            target["contract_artifact"]["git_blob_sha1"],
            "e27b317d833496fea3afe7fb308ca914d649d648",
        )
        self.assertEqual(
            target["invariant_test_artifact"]["git_blob_sha1"],
            "86331998c5e415588ae035fd3087c101c141884d",
        )

    def test_exact_sentence_is_identical_in_packet_and_machine_request(self):
        exact_sentence = self.request["authorization"]["exact_authorization_sentence"]
        packet_section = self.packet.split("## Exact Authorization Sentence", maxsplit=1)[1]
        packet_sentence = next(
            line.removeprefix("> ")
            for line in packet_section.splitlines()
            if line.startswith("> ")
        )
        self.assertEqual(exact_sentence, packet_sentence)
        self.assertIn("184,252,032 bytes", exact_sentence)
        self.assertIn("at most 144 participant-specific parameter-update fits", exact_sentence)
        self.assertIn("216 target-blind model-inference runs", exact_sentence)
        self.assertIn("180 run-11 execution targets", exact_sentence)
        self.assertIn("180 run-12 imagery targets", exact_sentence)
        self.assertIn("zero retry, zero rerun, and zero post-target update", exact_sentence)

    def test_requested_scope_matches_the_immutable_contract(self):
        scope = self.request["requested_scope"]
        dataset = self.contract["dataset_binding"]
        self.assertEqual(scope["subjects"], dataset["participants"])
        self.assertEqual(scope["runs"], ["03", "04", "07", "08", "11", "12"])
        self.assertEqual(scope["file_count"], 72)
        self.assertEqual(scope["payload_bytes"], 184_252_032)
        self.assertEqual(
            scope["canonical_inventory_sha256"],
            "41906e8c74cafdcaa99354baab8acd4927127a73e7454939429dbca2a8c03dad",
        )
        self.assertEqual(scope["expected_fit_rows"], 720)
        self.assertEqual(scope["expected_sealed_final_rows"], 360)
        self.assertEqual(scope["maximum_parameter_update_fits"], 144)
        self.assertEqual(scope["maximum_target_blind_inference_runs"], 216)
        self.assertEqual(scope["required_prediction_condition_families"], 18)
        self.assertEqual(scope["required_participant_condition_prediction_sets"], 216)
        self.assertEqual(scope["final_target_deliveries"], 1)
        self.assertEqual(scope["final_scoring_events"], 1)
        self.assertEqual(scope["maximum_verdict"], "WO9R-R4")

    def test_acquisition_and_analysis_caps_are_exact_and_small(self):
        acquisition = self.request["resource_caps"]["acquisition"]
        self.assertEqual(acquisition["invocations"], 1)
        self.assertEqual(acquisition["cpu_threads"], 1)
        self.assertEqual(acquisition["workers"], 1)
        self.assertEqual(acquisition["payload_requests"], 72)
        self.assertEqual(acquisition["payload_bytes"], 184_252_032)
        self.assertEqual(acquisition["minimum_free_disk_bytes"], 20 << 30)
        self.assertEqual(acquisition["retries"], 0)
        self.assertEqual(acquisition["reruns"], 0)

        analysis = self.request["resource_caps"]["analysis_and_scoring"]
        self.assertEqual(analysis["registered_executions"], 1)
        self.assertEqual(analysis["cpu_threads"], 1)
        self.assertEqual(analysis["workers"], 1)
        self.assertEqual(analysis["network_bytes"], 0)
        self.assertEqual(analysis["new_payload_bytes"], 0)
        self.assertEqual(analysis["maximum_parameter_update_fits"], 144)
        self.assertEqual(analysis["maximum_target_blind_inference_runs"], 216)
        self.assertEqual(analysis["final_target_deliveries"], 1)
        self.assertEqual(analysis["final_scoring_events"], 1)
        self.assertEqual(analysis["retries"], 0)
        self.assertEqual(analysis["reruns"], 0)
        self.assertEqual(analysis["post_target_updates"], 0)

    def test_access_order_requires_green_decision_implementation_and_freeze(self):
        order = self.request["requested_access_order"]
        self.assertLess(
            order.index("authorization_only_decision_commit_pushed_and_both_CI_jobs_green"),
            order.index("generated_fixture_and_mock_transport_only_implementation"),
        )
        self.assertLess(
            order.index("implementation_commit_pushed_and_both_CI_jobs_green"),
            order.index("one_exact_72_file_acquisition"),
        )
        self.assertLess(
            order.index("one_exact_72_file_acquisition"),
            order.index("one_target_blind_72_EDF_analysis"),
        )
        self.assertLess(
            order.index("hash_only_prediction_freeze_commit_pushed_and_remotely_green"),
            order.index("one_combined_delivery_and_score_of_same_360_final_targets"),
        )

    def test_request_counters_preserve_metadata_only_history_and_zero_real_work(self):
        counters = self.request["current_access_counters"]
        self.assertEqual(counters["inherited_public_metadata_get_requests"], 13)
        self.assertEqual(counters["inherited_public_metadata_body_bytes"], 340_703)
        nonzero_metadata = {
            "inherited_public_metadata_get_requests",
            "inherited_public_metadata_body_bytes",
        }
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in nonzero_metadata)
        )

    def test_forbidden_scope_blocks_expansion_models_and_claim_upgrade(self):
        forbidden = set(self.request["forbidden_operations"])
        required = {
            "event_sidecar_operation",
            "additional_file_participant_run_dataset_download_or_substitution",
            "row_random_split_or_cross_participant_fit",
            "final_target_use_before_green_prediction_freeze",
            "target_derived_exclusion_selection_or_normalization",
            "filter_window_channel_classifier_threshold_or_hyperparameter_search",
            "larger_additional_deep_CML_pretrained_foundation_or_language_model",
            "provider_RW3_stream_device_or_hardware_operation",
            "retry_rerun_post_target_update_or_second_target_delivery",
            "claim_upgrade_beyond_WO9R_R4",
        }
        self.assertTrue(required.issubset(forbidden))
        self.assertGreaterEqual(len(forbidden), 16)

    def test_next_gate_is_request_commit_then_exact_user_sentence(self):
        next_gate = self.request["next_gate"]
        self.assertTrue(next_gate["request_commit_required"])
        self.assertTrue(next_gate["request_commit_push_required"])
        self.assertTrue(next_gate["remote_green_request_required_before_exact_sentence_acceptance"])
        self.assertFalse(next_gate["exact_sentence_received"])
        self.assertFalse(next_gate["decision_record_exists"])
        self.assertFalse(next_gate["implementation_may_begin"])
        self.assertFalse(next_gate["acquisition_may_begin"])
        self.assertFalse(next_gate["analysis_may_begin"])
        self.assertFalse(next_gate["scoring_may_begin"])

    def test_claim_ceiling_stays_within_dataset_and_not_brain_specific(self):
        boundary = self.request["claim_boundary"]
        self.assertIn("within EEGMMIDB", boundary["maximum_future_claim"])
        self.assertIn("Brain-specific origin", boundary["not_established_even_if_WO9R_R4"])
        self.assertFalse(boundary["current_scientific_claim_upgrade"])
        self.assertIn("Scientific claim not established by this request", self.packet)


if __name__ == "__main__":
    unittest.main()
