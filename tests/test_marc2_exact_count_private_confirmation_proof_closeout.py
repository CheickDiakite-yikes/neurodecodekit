import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_exact_count_private_confirmation as wrapper

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_exact_count_private_confirmation_implementation.v0.json"
)
DOC = ROOT / "docs/MARC_2_EXACT_COUNT_PRIVATE_CONFIRMATION_PROOF_CLOSEOUT.md"


class Marc2ExactCountPrivateConfirmationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "a0e36afd08bc9d6ae9429e9471d4650f6093e406"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_640_499_738)
        self.assertEqual(self.proof["base_job_id"], 97_196_742_388)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_196_742_556)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshots_are_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 9689)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "70576022c5645d063bd0170cf88ae5844460e55833959dda552d95f48bff637e",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "59de1284da98d068ecfe4bf21f5179a7b3ccac7a",
        )
        self.assertEqual(self.proof["result_registry_preproof_bytes"], 4479)
        self.assertEqual(
            self.proof["result_registry_preproof_sha256"],
            "ab216888a79b818f5345179966206c2327e2fed203cf87c7a4dba9b3b469145a",
        )
        self.assertEqual(
            self.proof["result_registry_preproof_git_blob"],
            "c929c254188e3149b75c5f17edd363fafbeb18b6",
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
            wrapper._require_green_implementation(ROOT), self.proof["commit"]
        )

    def test_closeout_did_not_repeat_or_touch_private_state(self):
        self.assertEqual(self.proof["qualification_route"], "MARC2VR34P-G1")
        self.assertFalse(self.proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(self.proof["private_operations_during_proof_closeout"], 0)
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )

    def test_human_closeout_preserves_delayed_effect_and_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("ineffective until its own exact commit", text)
        self.assertIn("does not repeat the registered generated qualification", text)
        self.assertIn("one registered invocation only", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
