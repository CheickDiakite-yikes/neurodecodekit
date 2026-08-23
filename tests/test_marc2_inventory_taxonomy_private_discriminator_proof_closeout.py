import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_inventory_taxonomy_private_discriminator as wrapper,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_inventory_taxonomy_private_discriminator_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_INVENTORY_TAXONOMY_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)


class Marc2InventoryTaxonomyPrivateDiscriminatorProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "6d3b770d0e67c8b394c6a1a7581c21ae7b202909"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_616_632_414)
        self.assertEqual(self.proof["base_job_id"], 97_138_335_047)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_138_335_116)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshots_are_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 7743)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "418b8b09e42ff5e8d12b3c07275afd5ea2160f52788b816c32accb6e94c25fcd",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "ac951c78eff270f921f21539dd6a25348fb97b18",
        )
        self.assertEqual(self.proof["result_registry_preproof_bytes"], 3580)
        self.assertEqual(
            self.proof["result_registry_preproof_sha256"],
            "87daeedaa49d6c6a1f8c86e902fc87ef9db15bef889de18d9964cbbd434e608b",
        )
        self.assertEqual(
            self.proof["result_registry_preproof_git_blob"],
            "1456c16d0250f7ee87bfdcaab3cdfeded0b4ee12",
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
        self.assertEqual(self.proof["qualification_route"], "MARC2VR28P-G1")
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
