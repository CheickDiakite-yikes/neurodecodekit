import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_eligible_total_direction_private_discriminator as wrapper,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/"
    "marc2_eligible_total_direction_private_discriminator_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/"
    "MARC_2_ELIGIBLE_TOTAL_DIRECTION_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)


class Marc2EligibleTotalDirectionPrivateDiscriminatorProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "bae648e269e56dde45eb15295224fbafcc3c8706"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_631_907_880)
        self.assertEqual(self.proof["base_job_id"], 97_175_866_956)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_175_866_782)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshots_are_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 9214)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "85e91a754383d6b53bb1d13d9f3acacf1580778c5da1476086931e6b32e8195a",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "03002305987b5338eebe72238278a6bb18101624",
        )
        self.assertEqual(self.proof["result_registry_preproof_bytes"], 4071)
        self.assertEqual(
            self.proof["result_registry_preproof_sha256"],
            "95dced1c56c7758e11f54855f666b59304267dcc9ef26e255f147117339596be",
        )
        self.assertEqual(
            self.proof["result_registry_preproof_git_blob"],
            "c4d06d69ecc9e75682bc9875231d80e5cf3afdf0",
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
        self.assertEqual(self.proof["qualification_route"], "MARC2VR32P-G1")
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
