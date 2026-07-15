import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_train_only_discrimination_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop48_stage_b_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_48_STAGE_B_AUTHORIZATION_PACKET.md"
PREREGISTRATION_PATH = REPO_ROOT / "docs" / "LOOP_48_TRAIN_ONLY_DISCRIMINATION_PREREGISTRATION.md"
INVARIANT_TEST_PATH = REPO_ROOT / "tests" / "test_loop48_train_only_discrimination_contract.py"


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


class Loop48StageBAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")
        cls.preregistration = PREREGISTRATION_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_every_authorization_flag_is_false(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.loop48_stage_b_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])
        flags = authorization_flags(request)
        self.assertGreaterEqual(len(flags), 20)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_preregistration_commit_and_both_ci_runs_are_bound(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "0ee0ab7cd3abae4ce654af9954854a6e236c8a0e",
        )
        self.assertEqual(registration["push_ci_run_id"], 29452286159)
        self.assertEqual(registration["pr_ci_run_id"], 29452288520)
        self.assertEqual(registration["push_ci_conclusion"], "success")
        self.assertEqual(registration["pr_ci_conclusion"], "success")
        for prefix in ("push", "pr"):
            self.assertEqual(registration[f"{prefix}_base_python_job_conclusion"], "success")
            self.assertEqual(registration[f"{prefix}_optional_neuro_job_conclusion"], "success")
        self.assertEqual(registration["local_dependency_light_tests"], 795)
        self.assertEqual(registration["prechange_dependency_light_tests"], 781)
        self.assertEqual(registration["local_optional_neuro_tests"], 842)
        self.assertEqual(registration["prechange_optional_neuro_tests"], 828)
        self.assertEqual(registration["focused_loop48_and_roadmap_tests"], 100)
        self.assertTrue(registration["staged_secret_scan_passed"])

    def test_preregistration_contract_and_test_hashes_are_exact(self):
        target = self.request["target"]
        for prefix, path in (
            ("preregistration", PREREGISTRATION_PATH),
            ("contract", CONTRACT_PATH),
            ("invariant_test", INVARIANT_TEST_PATH),
        ):
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_bytes"], path.stat().st_size)
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(target["contract_schema_name"], self.contract["schema_name"])
        self.assertEqual(target["contract_schema_version"], self.contract["schema_version"])
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_requested_source_scope_matches_the_contract(self):
        scope = self.request["requested_scope"]
        source = self.contract["source_contract"]
        cache = source["cache"]
        self.assertEqual(scope["source_cache_path"], cache["path"])
        self.assertEqual(scope["source_cache_bytes"], cache["bytes"])
        self.assertEqual(scope["source_cache_sha256"], cache["sha256"])
        self.assertEqual(scope["source_partition"], source["allowed_source_partition"])
        self.assertEqual(scope["source_partition_rows"], 55)
        self.assertEqual(scope["fit_signal_rows_delivered"], 44)
        self.assertEqual(scope["fit_target_rows_delivered"], 44)
        self.assertEqual(scope["check_signal_rows_delivered"], 11)
        self.assertEqual(scope["check_target_rows_delivered_before_green_freeze"], 0)
        self.assertEqual(scope["check_target_rows_delivered_after_green_freeze"], 11)
        self.assertEqual(scope["validation_rows_delivered"], 0)
        self.assertEqual(scope["source_test_rows_delivered"], 0)
        self.assertEqual(scope["session2_rows_delivered"], 0)
        self.assertEqual(len(self.request["allowed_inputs"]), 2)

    def test_exact_sentence_matches_contract_and_appears_once(self):
        authorization = self.request["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertEqual(sentence, self.contract["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.packet.count(sentence), 1)
        self.assertEqual(self.preregistration.count(sentence), 1)
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertFalse(authorization["general_research_autonomy_is_execution_authorization"])
        self.assertFalse(authorization["co_researcher_status_is_execution_authorization"])
        self.assertFalse(authorization["draft_autonomy_charter_is_execution_authorization"])
        self.assertFalse(authorization["stage_a_or_loop26_authorization_is_transitive"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])

    def test_operation_inventory_and_caps_do_not_expand_contract(self):
        scope = self.request["requested_scope"]
        caps = self.request["resource_caps"]
        contract_caps = self.contract["resource_caps"]
        self.assertEqual(scope["parameter_update_runs"], 20)
        self.assertEqual(scope["target_blind_model_inference_runs"], 35)
        self.assertEqual(scope["train_only_no_signal_prior_fits"], 5)
        self.assertEqual(scope["prediction_sets"], 41)
        self.assertEqual(scope["check_scoring_events"], 1)
        self.assertEqual(scope["reruns_after_check_scoring"], 0)
        for request_key, contract_key in (
            ("cpu_threads", "cpu_threads"),
            ("workers", "workers"),
            ("peak_rss_bytes", "peak_rss_bytes"),
            ("parameter_update_runtime_sec", "parameter_update_runtime_sec"),
            ("end_to_end_runtime_sec", "end_to_end_runtime_sec"),
            ("total_generated_artifact_bytes", "total_generated_artifact_bytes"),
            (
                "minimum_free_disk_bytes_before_execution",
                "minimum_free_disk_bytes_before_execution",
            ),
        ):
            self.assertEqual(caps[request_key], contract_caps[contract_key])
        self.assertEqual(caps["new_download_bytes"], 0)

    def test_frozen_experiment_arithmetic_is_exact(self):
        frozen = self.request["frozen_experiment"]
        training = self.contract["training_contract"]
        inventory = self.contract["prediction_inventory"]
        self.assertEqual(frozen["fit_prefix_sizes"], [8, 16, 24, 32, 44])
        self.assertEqual(frozen["seeds"], [4801, 4802, 4803])
        self.assertEqual(frozen["parameter_update_runs"], training["total_parameter_update_runs"])
        self.assertEqual(frozen["model_inference_runs"], 35)
        self.assertEqual(frozen["prediction_sets"], inventory["prediction_sets_exact"])
        self.assertEqual(frozen["exact_sign_assignments"], 2**11)
        self.assertEqual(frozen["primary_macro_cer_margin"], 0.05)
        self.assertEqual(frozen["fine_shift_bonferroni_p_max"], 0.0125)
        self.assertEqual(frozen["post_check_parameter_updates"], 0)
        self.assertEqual(frozen["reruns"], 0)

    def test_required_sequence_preserves_two_green_firewalls(self):
        sequence = self.request["required_sequence_after_authorization"]
        authorization_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation = sequence.index(
            "implement_isolation_training_controls_freezer_and_scorer_with_synthetic_only_tests_without_protected_access"
        )
        implementation_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        cache_hash = sequence.index("one_source_cache_sha256_pass")
        prediction_freeze = sequence.index(
            "commit_push_and_obtain_green_ci_for_hash_only_prediction_freeze_record"
        )
        target_delivery = sequence.index(
            "deliver_exactly_11_check_targets_to_one_isolated_scorer_once"
        )
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, cache_hash)
        self.assertLess(cache_hash, prediction_freeze)
        self.assertLess(prediction_freeze, target_delivery)

    def test_request_preparation_and_protected_counters_are_honest(self):
        ledger = self.request["request_preparation_ledger"]
        self.assertEqual(ledger["green_ci_run_inspections"], 2)
        protected_keys = {
            "source_cache_stat_reads",
            "source_cache_hash_passes",
            "source_cache_member_reads",
            "ignored_file_content_reads",
            "signal_reads",
            "target_reads",
            "checkpoint_or_private_prediction_reads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "generated_experiment_artifacts",
            "network_download_bytes",
            "rw3_stream_device_or_hardware_operations",
        }
        self.assertTrue(all(ledger[key] == 0 for key in protected_keys))
        counters = self.request["current_protected_access_counters"]
        self.assertEqual(
            set(counters),
            set(self.contract["required_runtime_access_counters"]),
        )
        self.assertTrue(all(value == 0 for value in counters.values()), counters)

    def test_claim_ceiling_keeps_historical_use_and_nonclaims_explicit(self):
        claim = self.request["claim_boundary"]
        self.assertEqual(claim["maximum_evidence_level"], "E2_pipeline_discriminative")
        self.assertIn("post-outcome", claim["maximum_after_clean_stage_b"])
        unavailable = " ".join(claim["still_unavailable_after_clean_stage_b"])
        for phrase in (
            "independent validation",
            "neural advantage",
            "brain-specific origin",
            "unseen-person generalization",
            "real-time",
            "clinical",
        ):
            self.assertIn(phrase, unavailable)
        warnings = " ".join(self.request["warnings"])
        self.assertIn("All 55 rows were used historically", warnings)
        self.assertIn("No Stage B outcome is predicted", warnings)

    def test_packet_discloses_scope_resources_and_nonclaims(self):
        for phrase in (
            "No outcome is predicted",
            "44-fit/11-check",
            "20 tiny models",
            "35 target-blind inferences",
            "41 prediction sets",
            "2^11 = 2,048",
            "1 GiB",
            "32 MiB",
            "E2 pipeline-discriminative",
            "every `authorized_now` field is false",
            "Still Not Established After A Pass",
        ):
            self.assertIn(phrase, self.packet)

    def test_request_snapshot_records_no_decision_implementation_or_result(self):
        self.assertEqual(
            self.request["proof_posture"],
            "green_hash_bound_preregistration_request_only_no_implementation_or_protected_execution",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        self.assertTrue(
            all(value == 0 for value in self.request["current_protected_access_counters"].values())
        )


if __name__ == "__main__":
    unittest.main()
