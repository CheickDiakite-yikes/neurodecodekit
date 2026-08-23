import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_task_aware_private_cohort_confirmation as wrapper,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_task_aware_private_cohort_confirmation_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_TASK_AWARE_PRIVATE_COHORT_CONFIRMATION_PROOF_CLOSEOUT.md"
)


class TaskAwarePrivateCohortConfirmationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "8179f6fd4acb721ef25b023e02ac9160789f9d49"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_650_171_033)
        self.assertEqual(self.proof["base_job_id"], 97_220_389_999)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_220_389_862)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshots_are_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 5950)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "3b32c341372a8221731d399be1f93758607facb8a34821b7765df0449aa470ab",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "ad6d8e411593651544af32882ad11e82d740febc",
        )
        self.assertEqual(self.proof["result_registry_preproof_bytes"], 4647)
        self.assertEqual(
            self.proof["result_registry_preproof_sha256"],
            "286059c3b82c89875d5200d4a58d16b67bb59364d11a99536e06083b5c8b5b2e",
        )
        self.assertEqual(
            self.proof["result_registry_preproof_git_blob"],
            "4d55f03559b93e4cd5d1d014e65b3ddc97f38f71",
        )

    def test_exact_artifact_set_still_matches_worktree(self):
        artifacts = self.record["implementation_artifacts"]
        for artifact in artifacts:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
        self.assertEqual(
            hashlib.sha256(
                json.dumps(
                    artifacts,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                    allow_nan=False,
                ).encode("utf-8")
            ).hexdigest(),
            self.proof["implementation_artifact_set_sha256"],
        )
        self.assertEqual(
            self.proof["implementation_artifact_git_blobs"],
            {
                "module": "0feadaebb45397f1b314f0cebe28635c1afd3b58",
                "behavior_test": "d1d95371ed43cfe56e32e1da5ee2e287dfe49718",
                "result_registry": "4d55f03559b93e4cd5d1d014e65b3ddc97f38f71",
                "result_test": "4bd551ffb18b4df7d03ab65b96c25f8502e5463d",
                "implementation_document": (
                    "d1104b68d04acb1bef2e2a6e3b903b7ab3e126e3"
                ),
                "authorization_decision": (
                    "608df12900dd624ead8131ee55c89e5d0b52ebdb"
                ),
            },
        )
        self.assertEqual(
            wrapper._require_green_implementation(ROOT), self.proof["commit"]
        )

    def test_closeout_did_not_repeat_or_touch_private_state(self):
        self.assertEqual(self.proof["qualification_route"], "MARC2VR36P-G1")
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
