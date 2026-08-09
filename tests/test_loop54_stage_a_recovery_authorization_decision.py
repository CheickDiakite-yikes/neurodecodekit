import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DECISION_PATH = (
    ROOT / "registries/loop54_stage_a_recovery_authorization_decision.v1.json"
)
REQUEST_PATH = ROOT / "registries/loop54_stage_a_recovery_authorization_request.v1.json"
CONTRACT_PATH = ROOT / "registries/loop54_stage_a_vhdr_contract.v0.json"
DOC_PATH = ROOT / "docs/LOOP_54_STAGE_A_RECOVERY_AUTHORIZATION_DECISION.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


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


class Loop54StageARecoveryAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
        cls.request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.document = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_parent_and_green_request_are_exact(self):
        decision = self.decision
        self.assertEqual(
            decision["schema_name"],
            "neurodecodekit.loop54_stage_a_recovery_authorization_decision",
        )
        self.assertEqual(decision["schema_version"], "0.1.0")
        self.assertEqual(
            decision["authorization_parent_commit"],
            "19813a86d7822954219976e4c119d1dd6693d4b3",
        )
        self.assertTrue(
            decision[
                "effective_only_after_this_record_is_tested_committed_pushed_and_ci_green"
            ]
        )
        green = decision["green_request"]
        self.assertEqual(green["push_CI_run_id"], 31283297030)
        self.assertEqual(green["push_CI_conclusion"], "success")
        self.assertEqual(green["base_python_conclusion"], "success")
        self.assertEqual(green["optional_neuro_readers_conclusion"], "success")

    def test_authorized_artifact_hashes_and_blobs_are_current(self):
        for binding in self.decision["authorized_artifacts"].values():
            path = ROOT / binding["path"]
            self.assertEqual(binding["sha256"], sha256(path), binding["path"])
            self.assertEqual(binding["git_blob_sha1"], git_blob_sha1(path), binding["path"])

    def test_exact_user_sentence_matches_request_and_document_once(self):
        sentence = self.decision["user_authorization"]["exact_sentence_verbatim"]
        request_sentence = self.request["decision"]["exact_authorization_sentence"]
        self.assertEqual(sentence, request_sentence)
        self.assertEqual(self.document.count(sentence), 1)
        user = self.decision["user_authorization"]
        self.assertTrue(user["matches_recovery_request_exact_sentence"])
        self.assertTrue(user["received_after_green_request_commit"])
        self.assertTrue(user["one_registered_real_execution_only"])

    def test_request_and_contract_remain_immutable_false_snapshots(self):
        request_flags = authorization_flags(self.request)
        self.assertTrue(request_flags)
        self.assertTrue(all(value is False for _, value in request_flags))
        contract_flags = authorization_flags(self.contract)
        self.assertEqual(contract_flags[0], ("contract_preparation_authorized_now", True))
        self.assertTrue(all(value is False for _, value in contract_flags[1:]))
        artifacts = self.decision["authorized_artifacts"]
        self.assertTrue(
            artifacts["recovery_request"]["remains_immutable_and_unauthorized_snapshot"]
        )
        self.assertTrue(
            artifacts["contract"]["remains_immutable_preregistration_snapshot"]
        )

    def test_only_synthetic_implementation_surfaces_activate_after_green(self):
        flags = dict(
            authorization_flags(self.decision["authorization_after_decision_green"])
        )
        expected_true = {
            "standard_library_parser_implementation_authorized_now",
            "generated_synthetic_VHDR_fixture_creation_authorized_now",
            "synthetic_filesystem_layout_creation_authorized_now",
            "synthetic_adversarial_qualification_authorized_now",
            "all_22_refusal_class_tests_authorized_now",
            "bounded_parser_CLI_and_report_implementation_authorized_now",
        }
        self.assertEqual({key for key, value in flags.items() if value}, expected_true)
        self.assertTrue(all(flags[key] is False for key in set(flags) - expected_true))

    def test_real_execution_is_conditional_exact_and_one_shot(self):
        real = self.decision["conditional_registered_real_execution"]
        self.assertTrue(real["authorized_by_this_exact_decision"])
        self.assertTrue(
            real[
                "eligible_only_after_exact_implementation_commit_is_pushed_and_both_CI_jobs_are_green"
            ]
        )
        self.assertFalse(real["eligible_before_green_implementation"])
        self.assertEqual(real["expected_size_bytes"], 11705)
        self.assertEqual(real["registered_real_executions"], 1)
        self.assertEqual(real["registered_VHDR_content_opens"], 1)
        self.assertFalse(real["referenced_siblings_may_be_resolved_statted_hashed_or_opened"])
        self.assertFalse(real["post_result_rerun_or_amendment"])
        order = self.decision["required_execution_order"]
        self.assertLess(
            order.index("confirm_authorization_commit_and_both_CI_jobs_are_green"),
            order.index(
                "implement_and_adversarially_test_with_generated_synthetic_VHDR_fixtures_only"
            ),
        )
        self.assertLess(
            order.index("confirm_implementation_commit_and_both_CI_jobs_are_green"),
            order.index("open_exact_registered_VHDR_once_with_no_follow_semantics"),
        )

    def test_resources_counters_and_claim_boundary_are_bounded(self):
        resources = self.decision["resource_boundary"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["maximum_combined_generated_output_bytes"], 1024**2)
        self.assertEqual(resources["network_bytes"], 0)
        measurements = self.decision["authorization_only_measurements"]
        for key, value in measurements.items():
            if key == "end_to_end_latency_measured":
                self.assertFalse(value)
            else:
                self.assertEqual(value, 0, key)
        self.assertIn(
            "cannot establish header readability",
            self.decision["claim_boundary"]["scientific_claim_not_established"],
        )


if __name__ == "__main__":
    unittest.main()
