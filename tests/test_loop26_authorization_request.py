import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop26_shared_validation_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop26_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_26_AUTHORIZATION_PACKET.md"
PREREGISTRATION_PATH = REPO_ROOT / "docs" / "LOOP_26_SHARED_VALIDATION_PREREGISTRATION.md"
INVARIANT_TEST_PATH = REPO_ROOT / "tests" / "test_loop26_shared_validation_contract.py"


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


class Loop26AuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_all_authorization_flags_are_false(self):
        request = self.request
        self.assertEqual(
            request["schema_name"],
            "neurodecodekit.loop26_authorization_request",
        )
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        self.assertIsNone(request["authorization_record_commit"])
        flags = authorization_flags(request)
        self.assertEqual(len(flags), 19)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_preregistration_commit_ci_and_local_counts_are_bound(self):
        registration = self.request["registration"]
        self.assertEqual(
            registration["commit"],
            "881145d865b1e25e3982b758c5fd2e519d16933b",
        )
        self.assertEqual(registration["commit_short"], "881145d")
        self.assertEqual(registration["ci_run_id"], 29282661766)
        self.assertEqual(registration["ci_conclusion"], "success")
        self.assertEqual(registration["base_python_job_conclusion"], "success")
        self.assertEqual(
            registration["optional_neuro_readers_job_conclusion"],
            "success",
        )
        self.assertEqual(registration["prechange_complete_suite_tests"], 684)
        self.assertEqual(registration["new_contract_tests"], 14)
        self.assertEqual(registration["local_complete_suite_tests"], 684 + 14)
        self.assertEqual(registration["local_complete_suite_skips"], 3)
        self.assertTrue(registration["staged_secret_scan_passed"])

    def test_contract_preregistration_and_test_hashes_are_exact(self):
        target = self.request["target"]
        bindings = (
            ("contract", CONTRACT_PATH),
            ("preregistration", PREREGISTRATION_PATH),
            ("invariant_test", INVARIANT_TEST_PATH),
        )
        for prefix, path in bindings:
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(target["contract_id"], self.contract["contract_id"])
        self.assertEqual(target["contract_schema_version"], "0.1.0")
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_exact_sentence_matches_contract_and_packet_once(self):
        authorization = self.request["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertEqual(
            sentence,
            self.contract["authorization"]["exact_authorization_sentence"],
        )
        self.assertEqual(self.packet.count(sentence), 1)
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertFalse(authorization["general_research_autonomy_is_execution_authorization"])
        self.assertFalse(authorization["co_researcher_status_is_execution_authorization"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])
        self.assertTrue(authorization["authorization_record_must_bind_green_request_commit"])

    def test_requested_scope_matches_the_frozen_contract(self):
        requested = self.request["requested_scope"]
        contract_scope = self.contract["scope"]
        training = self.contract["training_contract"]
        self.assertEqual(requested["numbered_loops"], contract_scope["numbered_loops"])
        self.assertEqual(requested["train_rows_delivered"], 55)
        self.assertEqual(requested["validation_signal_rows_delivered"], 6)
        self.assertEqual(
            requested["validation_target_rows_delivered_after_green_prediction_freeze"],
            6,
        )
        self.assertEqual(requested["source_test_rows_delivered"], 0)
        self.assertEqual(requested["session2_rows_delivered"], 0)
        self.assertEqual(
            requested["parameter_update_runs"],
            training["total_parameter_update_runs"],
        )
        self.assertEqual(requested["optimizer_steps"], training["total_optimizer_steps"])
        self.assertEqual(
            requested["target_blind_model_inference_runs"],
            training["target_blind_model_inference_runs"],
        )
        self.assertEqual(requested["prediction_sets"], 31)
        self.assertEqual(requested["restarts"], 0)
        self.assertEqual(requested["post_target_reruns"], 0)

    def test_archive_correction_preserves_algorithmic_target_boundary(self):
        correction = self.request["archive_access_correction"]
        self.assertTrue(correction["legacy_cache_is_monolithic_deflated_npz"])
        self.assertTrue(correction["legacy_loader_materialized_all_validation_target_bytes"])
        self.assertFalse(
            correction["validation_targets_were_used_for_prior_loss_selection_or_scoring"]
        )
        self.assertTrue(correction["physical_never_opened_validation_target_claim_withdrawn"])
        self.assertTrue(correction["future_runtime_uses_isolated_row_streaming_derivatives"])
        self.assertIn("not been used", correction["remaining_supported_statement"])

    def test_required_sequence_keeps_targets_after_green_prediction_freeze(self):
        sequence = self.request["required_sequence_after_authorization"]
        request_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_that_authorization_record"
        )
        implementation = sequence.index(
            "implement_the_reader_model_controls_freezer_scorer_and_synthetic_tests_without_real_cache_access"
        )
        cache_derivatives = sequence.index(
            "hash_the_source_cache_once_and_create_only_the_train_and_target_free_validation_input_derivatives"
        )
        freeze_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_the_hash_only_prediction_freeze_record"
        )
        target_delivery = sequence.index(
            "deliver_the_same_six_validation_targets_to_one_isolated_scorer_once"
        )
        self.assertLess(request_green, implementation)
        self.assertLess(implementation, cache_derivatives)
        self.assertLess(cache_derivatives, freeze_green)
        self.assertLess(freeze_green, target_delivery)

    def test_resource_caps_do_not_expand_the_registered_contract(self):
        requested = self.request["resource_caps"]
        contract = self.contract["resource_caps"]
        for name, value in requested.items():
            with self.subTest(resource=name):
                self.assertEqual(value, contract[name])
        self.assertEqual(requested["cpu_threads"], 1)
        self.assertEqual(requested["peak_rss_bytes"], 1 << 30)
        self.assertEqual(requested["total_generated_artifact_bytes"], 32 << 20)
        self.assertEqual(requested["new_download_bytes"], 0)

    def test_current_protected_access_and_runtime_counters_are_zero(self):
        counters = self.request["current_access_counters"]
        self.assertEqual(len(counters), 22)
        self.assertTrue(all(value == 0 for value in counters.values()), counters)
        protected = self.request["protected_evidence"]
        self.assertEqual(protected["source_test_status"], "consumed_and_closed")
        self.assertEqual(protected["session2_status"], "consumed_and_closed")
        self.assertIn("unopened", protected["s25_status"])
        self.assertFalse(protected["prediction_process_receives_validation_targets"])
        self.assertFalse(
            protected["scorer_receives_validation_targets_before_green_prediction_freeze"]
        )

    def test_packet_discloses_scope_caps_correction_and_claim_ceiling(self):
        for phrase in (
            "21",
            "5,040",
            "31",
            "1 GiB",
            "32 MiB",
            "0 bytes",
            "physically materialized",
            "every `authorized_now` field is false",
            "Still Not Established After A Pass",
        ):
            self.assertIn(phrase, self.packet)
        claim = self.request["claim_boundary"]
        self.assertIn("No Loop 26 implementation", claim["current"])
        unavailable = " ".join(claim["still_unavailable_after_full_pass"])
        self.assertIn("unseen-person", unavailable)
        self.assertIn("clinical", unavailable)


if __name__ == "__main__":
    unittest.main()
