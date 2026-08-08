import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/loop54_stage_a_registration_ci_recovery.v0.json"


class Loop54StageARegistrationCIRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_failure_is_preserved_without_calling_exact_commit_green(self):
        original = self.registry["original_registration"]
        self.assertEqual(
            original["commit"],
            "c1146233a6178ca5e1153b92565915abad029719",
        )
        self.assertEqual(original["second_attempt_status"], "completed_failure")
        self.assertTrue(original["second_attempt_head_sha_exact"])
        self.assertEqual(
            original["second_attempt_base_python"]["conclusion"],
            "failure_at_ruff",
        )
        self.assertEqual(
            original["second_attempt_optional_neuro_readers"]["conclusion"],
            "success",
        )
        failure = self.registry["failure_classification"]
        self.assertFalse(failure["historical_requirement_met"])
        self.assertEqual(
            failure["category"],
            "floating_development_dependency_toolchain_drift",
        )

    def test_frozen_registration_payload_hashes_are_current(self):
        for artifact in self.registry["immutable_registration_payload"]:
            path = ROOT / artifact["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["sha256"])
        identity = self.registry["payload_identity_checks"]
        self.assertTrue(identity["original_to_pinned_descendant_byte_identical"])
        self.assertTrue(identity["original_to_recovery_parent_byte_identical"])
        self.assertFalse(identity["frozen_artifacts_modified"])

    def test_pinned_remote_anchor_and_exact_tree_replay_passed(self):
        anchor = self.registry["pinned_remote_proof_anchor"]
        self.assertEqual(
            anchor["commit"],
            "223299381036217631374d096fc842add5f6baf7",
        )
        self.assertEqual(anchor["ruff_version"], "0.15.20")
        self.assertEqual(anchor["push_ci_run_id"], 31132586790)
        self.assertEqual(anchor["push_ci_conclusion"], "success")
        self.assertTrue(anchor["base_python_passed"])
        self.assertTrue(anchor["optional_neuro_readers_passed"])
        replay = self.registry["exact_tree_local_replay"]
        self.assertTrue(replay["ruff_passed"])
        self.assertEqual(replay["complete_tests"], 1095)
        self.assertEqual(replay["complete_expected_skips"], 3)
        self.assertTrue(replay["compileall_passed"])
        self.assertTrue(replay["all_registry_json_passed"])
        self.assertTrue(replay["cli_help_passed"])
        self.assertTrue(replay["temporary_worktree_removed"])

    def test_recovery_does_not_authorize_implementation_or_execution(self):
        authorization = self.registry["authorization"]
        self.assertFalse(authorization["implementation_authorized_now"])
        self.assertFalse(authorization["real_execution_authorized_now"])
        self.assertFalse(authorization["old_draft_request_actionable"])
        protocol = self.registry["recovery_protocol"]
        self.assertFalse(protocol["parser_implementation_may_start_from_recovery_alone"])
        self.assertFalse(protocol["real_execution_may_start_from_recovery_alone"])
        self.assertTrue(all(value == 0 for value in self.registry["access_counters"].values()))

    def test_document_binding_and_claim_boundary_are_explicit(self):
        binding = self.registry["documentation_binding"]
        document = ROOT / binding["path"]
        self.assertEqual(hashlib.sha256(document.read_bytes()).hexdigest(), binding["sha256"])
        text = document.read_text(encoding="utf-8")
        self.assertIn("failed historical run was green", text)
        self.assertIn("No parser implementation or real execution", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
