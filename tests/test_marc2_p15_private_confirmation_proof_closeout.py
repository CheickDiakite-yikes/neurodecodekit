import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_p15_private_confirmation as wrapper


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/marc2_p15_private_confirmation_implementation.v0.json"


class Marc2P15PrivateConfirmationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(self.proof["commit"], "d98a0115d2fd113929d512dfc7fb372a38b8f5c8")
        self.assertEqual(self.proof["CI_run_id"], 32197145780)
        self.assertEqual(self.proof["base_job_id"], 95903371693)
        self.assertEqual(self.proof["optional_neuro_job_id"], 95903371721)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshot_is_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 6984)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "63f45df1f3ae184e29c296b9b7caf4ba0c02985aaae482080800988c4ffcd8ca",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "65c3652fe2519abfa965e32b840b4c5d970a9db1",
        )

    def test_exact_artifact_set_still_matches_worktree(self):
        artifacts = self.record["implementation_artifacts"]
        for artifact in artifacts:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
        self.assertEqual(
            wrapper._sha256_bytes(wrapper._canonical_json_bytes(artifacts)),
            self.proof["implementation_artifact_set_sha256"],
        )
        self.assertEqual(
            wrapper._require_green_implementation(self.record, ROOT),
            self.proof["commit"],
        )

    def test_closeout_did_not_repeat_or_touch_private_state(self):
        self.assertEqual(self.proof["qualification_route"], "MARC2VR12P-G1")
        self.assertFalse(self.proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(self.proof["private_operations_during_proof_closeout"], 0)
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_stage_2_remains_delayed_until_closeout_is_green(self):
        status = self.record["stage_2_status"]
        self.assertFalse(status["private_execution_available_now"])
        self.assertTrue(status["private_execution_available_after_closeout_is_remotely_green"])
        self.assertEqual(status["registered_private_invocation_limit_after_proof"], 1)
        self.assertEqual(status["retry_rerun_resume_fallback_or_substitution_limit"], 0)


if __name__ == "__main__":
    unittest.main()
