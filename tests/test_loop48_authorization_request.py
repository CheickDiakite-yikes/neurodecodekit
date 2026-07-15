import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "registries" / "loop48_failure_localization_contract.v0.json"
REQUEST_PATH = REPO_ROOT / "registries" / "loop48_authorization_request.v0.json"
PACKET_PATH = REPO_ROOT / "docs" / "LOOP_48_AUTHORIZATION_PACKET.md"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_48_PRIMARY_SOURCE_RESEARCH.md"
INVARIANT_TEST_PATH = REPO_ROOT / "tests" / "test_loop48_failure_localization_contract.py"


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


class Loop48AuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.packet = PACKET_PATH.read_text(encoding="utf-8")

    def test_identity_status_and_all_authorization_flags_are_false(self):
        request = self.request
        self.assertEqual(request["schema_name"], "neurodecodekit.loop48_authorization_request")
        self.assertEqual(request["schema_version"], "0.1.0")
        self.assertEqual(request["status"], "awaiting_exact_user_authorization")
        self.assertFalse(request["authorized_now"])
        self.assertIsNone(request["user_decision"])
        flags = authorization_flags(request)
        self.assertEqual(len(flags), 18)
        self.assertTrue(all(value is False for _, value in flags), flags)

    def test_green_registration_commit_and_both_ci_runs_are_bound(self):
        registration = self.request["registration"]
        self.assertEqual(registration["commit"], "83309bfc29300c542c7a7a6dc0f193baba28d42e")
        self.assertEqual(registration["push_ci_run_id"], 29431318268)
        self.assertEqual(registration["pr_ci_run_id"], 29431347801)
        self.assertEqual(registration["push_ci_conclusion"], "success")
        self.assertEqual(registration["pr_ci_conclusion"], "success")
        self.assertEqual(registration["local_complete_suite_tests"], 762)
        self.assertEqual(registration["prechange_complete_suite_tests"], 748)
        self.assertEqual(registration["local_dependency_light_tests"], 715)
        self.assertTrue(registration["staged_secret_scan_passed"])

    def test_contract_research_and_invariant_test_hashes_are_exact(self):
        target = self.request["target"]
        for prefix, path in (("contract", CONTRACT_PATH), ("research", RESEARCH_PATH)):
            with self.subTest(path=path.name):
                self.assertEqual(target[f"{prefix}_sha256"], sha256(path))
                self.assertEqual(target[f"{prefix}_git_blob_sha1"], git_blob_sha1(path))
        self.assertEqual(
            target["invariant_test_sha256"],
            "eec77e323b7b46ea12110b33238718895df1b27ca53a7fd8aa9ea35ae2d54605",
        )
        self.assertEqual(
            target["invariant_test_git_blob_sha1"],
            "bba4f394d124ef528e2f1a6976afe2aeb772c7b1",
        )
        self.assertEqual(
            target["invariant_test_path"],
            str(INVARIANT_TEST_PATH.relative_to(REPO_ROOT)),
        )
        self.assertEqual(target["contract_schema_version"], "0.1.0")
        self.assertTrue(target["registration_snapshot_must_remain_immutable"])

    def test_allowed_inputs_are_exactly_the_contract_inputs(self):
        request_inputs = self.request["allowed_inputs"]
        contract_inputs = self.contract["committed_input_artifacts"]
        self.assertEqual(len(request_inputs), 4)
        self.assertEqual(
            [
                (row["artifact_id"], row["path"], row["bytes"], row["sha256"])
                for row in request_inputs
            ],
            [
                (row["artifact_id"], row["path"], row["bytes"], row["sha256"])
                for row in contract_inputs
            ],
        )
        self.assertEqual(sum(row["bytes"] for row in request_inputs), 155545)

    def test_exact_sentence_appears_once_and_general_autonomy_is_not_authorization(self):
        authorization = self.request["authorization"]
        sentence = authorization["exact_authorization_sentence"]
        self.assertEqual(self.packet.count(sentence), 1)
        self.assertFalse(authorization["exact_sentence_received_from_user"])
        self.assertFalse(authorization["general_research_autonomy_is_execution_authorization"])
        self.assertFalse(authorization["co_researcher_status_is_execution_authorization"])
        self.assertFalse(authorization["prior_loop26_authorization_is_transitive"])
        self.assertTrue(authorization["separate_authorization_only_record_required"])

    def test_requested_scope_and_caps_do_not_expand_the_contract(self):
        scope = self.request["requested_scope"]
        caps = self.request["resource_caps"]
        contract_caps = self.contract["resource_caps"]
        self.assertEqual(caps["current_request_artifact_bytes"], 23788)
        self.assertEqual(scope["committed_json_input_count"], 4)
        self.assertEqual(scope["model_inference_runs"], 0)
        self.assertEqual(scope["training_or_parameter_update_runs"], 0)
        self.assertEqual(scope["target_deliveries"], 0)
        self.assertEqual(caps["cpu_threads"], contract_caps["future_stage_a_cpu_threads"])
        self.assertEqual(caps["runtime_sec"], contract_caps["future_stage_a_runtime_sec"])
        self.assertEqual(caps["peak_rss_bytes"], contract_caps["future_stage_a_peak_rss_bytes"])
        self.assertEqual(
            caps["generated_output_bytes"], contract_caps["future_stage_a_generated_bytes"]
        )

    def test_sequence_requires_green_authorization_and_implementation_before_stage_a(self):
        sequence = self.request["required_sequence_after_authorization"]
        authorization_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_authorization_record"
        )
        implementation = sequence.index(
            "implement_dependency_light_analyzer_and_synthetic_isolation_tests_without_runtime_read_of_registered_inputs"
        )
        implementation_green = sequence.index(
            "test_commit_push_and_obtain_green_ci_for_implementation"
        )
        execution = sequence.index("execute_stage_a_once_over_four_exact_committed_json_inputs")
        self.assertLess(authorization_green, implementation)
        self.assertLess(implementation, implementation_green)
        self.assertLess(implementation_green, execution)

    def test_current_counters_are_all_zero_and_claim_ceiling_is_narrow(self):
        counters = self.request["current_access_counters"]
        self.assertEqual(len(counters), 19)
        self.assertTrue(all(value == 0 for value in counters.values()), counters)
        claim = self.request["claim_boundary"]
        self.assertIn("No Loop 48 implementation", claim["current"])
        self.assertIn("post-outcome", claim["maximum_after_clean_stage_a"])
        unavailable = " ".join(claim["still_unavailable_after_clean_stage_a"])
        self.assertIn("root cause", unavailable)
        self.assertIn("clinical", unavailable)

    def test_packet_discloses_resources_expected_result_and_nonclaims(self):
        for phrase in (
            "155,545",
            "30 seconds",
            "256 MiB",
            "1 MiB",
            "expected class is `F5`",
            "not new independent evidence",
            "every `authorized_now` field is false",
            "Still Not Established After A Pass",
        ):
            self.assertIn(phrase, self.packet)

    def test_request_snapshot_records_no_decision_implementation_or_result(self):
        self.assertEqual(
            self.request["proof_posture"],
            "green_hash_bound_request_only_no_implementation_or_execution",
        )
        self.assertFalse(self.request["authorized_now"])
        self.assertIsNone(self.request["user_decision"])
        self.assertIsNone(self.request["authorization_record_commit"])
        self.assertTrue(
            all(value == 0 for value in self.request["current_access_counters"].values())
        )


if __name__ == "__main__":
    unittest.main()
