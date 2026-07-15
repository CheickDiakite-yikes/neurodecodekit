import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = REPO_ROOT / "registries" / "loop48_authorization_decision.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop48_authorization_request.v0.json"
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_failure_localization_contract.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_48_AUTHORIZATION_DECISION.md"


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


class Loop48AuthorizationDecisionTests(unittest.TestCase):
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
            "neurodecodekit.loop48_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(decision["status"], "authorized_no_implementation_or_execution_yet")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "8c96c7f009d9f3b5b5d93178f3f7e43771bdce61",
        )
        self.assertTrue(
            decision["effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"]
        )

        contract = decision["authorized_contract"]
        request = decision["authorization_request"]
        self.assertEqual(contract["contract_sha256"], sha256(CONTRACT_PATH))
        self.assertEqual(contract["contract_git_blob_sha1"], git_blob_sha1(CONTRACT_PATH))
        self.assertEqual(request["request_sha256"], sha256(REQUEST_PATH))
        self.assertEqual(request["request_git_blob_sha1"], git_blob_sha1(REQUEST_PATH))
        self.assertEqual(request["request_commit"][:7], "0ffdf47")
        self.assertTrue(contract["contract_remains_immutable_preregistration_snapshot"])
        self.assertTrue(request["request_remains_immutable_and_unauthorized"])

    def test_historical_registration_snapshot_remains_hash_bound(self):
        snapshot = self.decision["registration_snapshot"]
        target = self.request["target"]
        self.assertEqual(snapshot["research_sha256"], target["research_sha256"])
        self.assertEqual(snapshot["research_git_blob_sha1"], target["research_git_blob_sha1"])
        self.assertEqual(
            snapshot["historical_invariant_test_sha256"],
            target["invariant_test_sha256"],
        )
        self.assertEqual(
            snapshot["historical_invariant_test_git_blob_sha1"],
            target["invariant_test_git_blob_sha1"],
        )
        self.assertTrue(snapshot["historical_test_blob_remains_bound_by_request_and_git_history"])

    def test_exact_user_sentence_matches_request_packet_and_doc(self):
        user = self.decision["user_authorization"]
        sentence = user["exact_sentence_verbatim"]
        self.assertEqual(sentence, self.request["authorization"]["exact_authorization_sentence"])
        self.assertEqual(self.doc.count(sentence), 1)
        self.assertTrue(user["matches_packet_exact_sentence"])
        self.assertTrue(user["explicit_loop48_stage_a_authorization_intent"])
        self.assertTrue(user["one_registered_execution_only"])
        self.assertTrue(
            user[
                "computer_storage_and_other_project_safety_remains_governing_operational_constraint"
            ]
        )
        self.assertTrue(user["scope_may_not_expand_by_inference"])

    def test_only_registered_surfaces_are_authorized(self):
        expected_true = {
            "loop48_artifact_only_implementation_authorized_now",
            "exact_four_committed_json_reads_authorized_now",
            "exact_input_sha256_verification_authorized_now",
            "frozen_aggregate_recomputation_authorized_now",
            "fixed_prefix_seed_dispersion_checks_authorized_now",
            "ordered_eight_class_tree_authorized_now",
            "one_aggregate_target_free_report_authorized_now",
            "one_stage_a_execution_authorized_now",
        }
        flags = dict(authorization_flags(self.decision["authorization"]))
        self.assertEqual(set(flags), set(self.decision["authorization"]))
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertEqual(len(flags), 24)

    def test_contract_and_request_remain_immutable_unauthorized_snapshots(self):
        for payload in (self.contract, self.request):
            flags = authorization_flags(payload)
            self.assertTrue(flags)
            self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertEqual(self.contract["status"], "preregistered_authorization_pending")
        self.assertEqual(self.request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])

    def test_allowed_inputs_and_operations_are_exactly_contract_bound(self):
        run = self.decision["registered_execution"]
        contract_inputs = self.contract["committed_input_artifacts"]
        self.assertEqual(run["committed_json_input_count"], 4)
        self.assertEqual(run["committed_json_input_bytes"], 155545)
        self.assertEqual(
            [
                (row["artifact_id"], row["path"], row["bytes"], row["sha256"])
                for row in run["allowed_inputs"]
            ],
            [
                (row["artifact_id"], row["path"], row["bytes"], row["sha256"])
                for row in contract_inputs
            ],
        )
        self.assertEqual(
            run["operations_in_order"],
            self.contract["future_artifact_only_stage_a"]["operations_in_order"],
        )
        self.assertEqual(run["aggregate_report_writes"], 1)
        for key in (
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "target_deliveries",
            "protected_cache_or_member_reads",
            "network_calls",
            "new_download_bytes",
            "reruns_after_stage_a",
        ):
            self.assertEqual(run[key], 0, key)

    def test_access_order_requires_two_green_milestones_before_stage_a(self):
        order = self.decision["required_execution_order"]
        self.assertEqual(
            order[:3],
            [
                "test_this_authorization_record_and_all_existing_contract_invariants",
                "commit_and_push_authorization_only_changes_before_implementation",
                "confirm_the_pushed_authorization_commit_and_both_ci_jobs_are_green",
            ],
        )
        authorization_green = order.index(
            "confirm_the_pushed_authorization_commit_and_both_ci_jobs_are_green"
        )
        implementation = order.index(
            "implement_dependency_light_analyzer_and_synthetic_isolation_tests_without_runtime_read_of_registered_inputs"
        )
        implementation_green = order.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        execution = order.index("execute_stage_a_once_over_four_exact_committed_json_inputs")
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, execution)

        rules = self.decision["conditional_access_rules"]
        self.assertFalse(
            rules["registered_artifacts_may_be_read_during_implementation_or_synthetic_tests"]
        )
        self.assertFalse(rules["stage_a_may_run_more_than_once"])
        self.assertFalse(rules["post_stage_a_tuning_selection_or_rerun_allowed"])

    def test_resource_caps_match_the_frozen_contract(self):
        resources = self.decision["resource_boundary"]
        contract_resources = self.contract["resource_caps"]
        mapping = {
            "cpu_threads": "future_stage_a_cpu_threads",
            "workers": "future_stage_a_workers",
            "runtime_sec": "future_stage_a_runtime_sec",
            "peak_rss_bytes": "future_stage_a_peak_rss_bytes",
            "generated_output_bytes": "future_stage_a_generated_bytes",
            "network_calls": "future_stage_a_network_calls",
            "new_download_bytes": "future_stage_a_downloaded_bytes",
            "model_inference_runs": "future_stage_a_model_runs",
            "training_or_parameter_update_runs": "future_stage_a_training_runs",
        }
        for key, contract_key in mapping.items():
            self.assertEqual(resources[key], contract_resources[contract_key], key)
        self.assertEqual(resources["peak_rss_bytes"], 256 * 1024**2)
        self.assertEqual(resources["generated_output_bytes"], 1024**2)

    def test_authorization_only_measurements_are_zero(self):
        measurements = self.decision["authorization_only_measurements"]
        for key, value in measurements.items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)

    def test_human_decision_matches_machine_scope_and_claim_ceiling(self):
        for term in (
            "Authorized after this record is tested, committed, pushed",
            "exactly 4 / 155,545 bytes",
            "<= 30 seconds",
            "<= 256 MiB",
            "<= 1 MiB",
            self.decision["authorized_contract"]["contract_sha256"],
            self.decision["authorization_parent_commit"],
        ):
            self.assertIn(term, self.doc)
        claims = " ".join(self.decision["claim_boundary"].values())
        for term in (
            "causal root cause",
            "neural advantage",
            "unseen-person",
            "real-time",
            "portable",
            "clinical",
        ):
            self.assertIn(term, claims)


if __name__ == "__main__":
    unittest.main()
