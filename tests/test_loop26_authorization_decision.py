import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop26_authorization_decision.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop26_authorization_request.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop26_shared_validation_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_26_AUTHORIZATION_DECISION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path):
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode()
    return hashlib.sha1(header + payload).hexdigest()


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


class Loop26AuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_hash_bindings_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.loop26_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(decision["status"], "authorized_no_implementation_yet")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "8572c14af005363cca08d4215a11a4d64455cac7",
        )
        self.assertTrue(
            decision["effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"]
        )
        contract = decision["authorized_contract"]
        request = decision["authorization_request"]
        self.assertEqual(contract["contract_id"], self.contract["contract_id"])
        self.assertEqual(contract["registration_commit"][:7], "881145d")
        self.assertEqual(contract["contract_sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(contract["contract_git_blob_sha1"], git_blob_sha1(CONTRACT_PATH))
        self.assertEqual(request["request_sha256"], sha256(REQUEST_PATH))
        self.assertEqual(request["request_git_blob_sha1"], git_blob_sha1(REQUEST_PATH))
        self.assertTrue(contract["contract_remains_immutable_preregistration_snapshot"])
        self.assertTrue(request["request_remains_immutable_and_unauthorized"])

    def test_exact_user_sentence_matches_request_contract_and_doc(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(
            sentence,
            self.request["authorization"]["exact_authorization_sentence"],
        )
        self.assertEqual(
            sentence,
            self.contract["authorization"]["exact_authorization_sentence"],
        )
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_packet_exact_sentence"])
        self.assertTrue(user["explicit_loop26_31_33_authorization_intent"])
        self.assertTrue(user["one_registered_execution_only"])
        self.assertTrue(
            user[
                "computer_storage_and_other_project_safety_remains_governing_operational_constraint"
            ]
        )

    def test_only_registered_surfaces_are_authorized(self):
        authorization = self.decision["authorization"]
        expected_true = {
            "loop26_implementation_authorized_now",
            "bounded_row_reader_authorized_now",
            "source_cache_single_hash_pass_authorized_now",
            "opaque_archive_member_traversal_authorized_now",
            "train_signal_and_target_derivative_authorized_now",
            "target_free_validation_signal_derivative_authorized_now",
            "registered_training_and_parameter_updates_authorized_now",
            "registered_checkpoint_write_and_read_authorized_now",
            "target_blind_model_inference_authorized_now",
            "train_only_prior_fits_authorized_now",
            "registered_control_conditions_authorized_now",
            "prediction_freeze_authorized_now",
            "hash_only_prediction_freeze_record_authorized_now",
            "conditional_validation_target_delivery_authorized_now",
            "conditional_validation_scoring_authorized_now",
        }
        flags = dict(authorization_flags(authorization))
        self.assertEqual(set(flags), set(authorization))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        for forbidden in [
            "source_test_or_session2_authorized_now",
            "raw_fif_or_mat_read_authorized_now",
            "s7_s20_or_s25_authorized_now",
            "new_download_authorized_now",
            "larger_model_or_restart_authorized_now",
            "language_model_or_neurotoken_authorized_now",
            "post_target_tuning_or_rerun_authorized_now",
            "rw3_stream_device_or_hardware_authorized_now",
            "loop27_or_later_execution_authorized_now",
        ]:
            self.assertFalse(flags[forbidden])

    def test_request_and_contract_remain_immutable_unauthorized_snapshots(self):
        for payload in [self.request, self.contract]:
            flags = authorization_flags(payload)
            self.assertTrue(flags)
            self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        self.assertEqual(
            self.request["status"],
            "awaiting_exact_user_authorization",
        )

    def test_access_order_keeps_values_after_green_implementation_and_targets_last(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(
            order[:3],
            [
                "test_this_authorization_record_and_all_existing_contract_invariants",
                "commit_and_push_authorization_only_changes_before_implementation",
                "confirm_the_pushed_authorization_commit_and_both_ci_jobs_are_green",
            ],
        )
        implementation = order.index(
            "implement_the_reader_model_controls_freezer_scorer_and_synthetic_tests_without_real_cache_access"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_the_implementation"
        )
        derivative = order.index(
            "hash_the_source_cache_once_and_create_only_the_train_and_target_free_validation_input_derivatives"
        )
        freeze_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_the_hash_only_prediction_freeze_record"
        )
        target = order.index("deliver_the_same_six_validation_targets_to_one_isolated_scorer_once")
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, derivative)
        self.assertLess(derivative, freeze_green)
        self.assertLess(freeze_green, target)
        rules = self.decision["conditional_access_rules"]
        self.assertFalse(rules["source_test_derivative_allowed"])
        self.assertFalse(rules["prediction_process_receives_validation_targets"])
        self.assertFalse(rules["post_target_parameter_updates_or_reruns_allowed"])

    def test_registered_counts_and_resources_are_exact(self):
        run = self.decision["registered_execution"]
        self.assertEqual((run["train_rows"], run["validation_rows"]), (55, 6))
        self.assertEqual(run["closed_source_test_rows"], 5)
        self.assertEqual(
            (run["candidate_parameters"], run["linear_comparator_parameters"]), (2908, 2884)
        )
        self.assertEqual(run["training_seeds"], [2601, 2602, 2603])
        self.assertEqual(run["nested_train_sizes"], [8, 16, 24, 32, 44, 55])
        self.assertEqual(run["parameter_update_runs"], 21)
        self.assertEqual(run["optimizer_steps"], 5040)
        self.assertEqual(run["target_blind_model_inference_runs"], 24)
        self.assertEqual(run["train_only_prior_fits"], 6)
        self.assertEqual(run["prediction_sets"], 31)
        self.assertEqual(run["validation_scoring_deliveries"], 1)
        self.assertEqual(run["restarts"], 0)
        self.assertEqual(run["post_target_reruns"], 0)

        resources = self.decision["resource_boundary"]
        contract_resources = self.contract["resource_caps"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["candidate_parameter_ceiling"], 2908)
        self.assertEqual(resources["maximum_peak_rss_bytes"], 1 << 30)
        self.assertEqual(resources["maximum_generated_artifact_bytes"], 32 << 20)
        for key, value in resources.items():
            contract_key = {
                "maximum_peak_rss_bytes": "peak_rss_bytes",
                "maximum_generated_artifact_bytes": "total_generated_artifact_bytes",
            }.get(key, key)
            self.assertEqual(value, contract_resources[contract_key], key)

    def test_authorization_only_measurements_are_zero(self):
        measurements = self.decision["authorization_only_measurements"]
        for key, value in measurements.items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_human_decision_matches_machine_scope_and_claim_ceiling(self):
        for term in [
            "Authorized after this record is tested, committed, pushed",
            "21 / 5,040",
            "31",
            "<= 1 GiB",
            "<= 32 MiB",
            "source-test or session-2 rows:               0",
            self.decision["authorized_contract"]["contract_sha256"],
            self.decision["authorization_parent_commit"],
        ]:
            self.assertIn(term, self.doc)
        claims = " ".join(self.decision["claim_boundary"])
        for term in [
            "sensor-signal-dependent",
            "unseen-person",
            "real-time",
            "portable",
            "clinical",
        ]:
            self.assertIn(term, claims)


if __name__ == "__main__":
    unittest.main()
