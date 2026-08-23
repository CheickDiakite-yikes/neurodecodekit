import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_inventory_distribution_private_discriminator as wrapper,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/"
    "marc2_inventory_distribution_private_discriminator_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_INVENTORY_DISTRIBUTION_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)


class Marc2InventoryDistributionPrivateDiscriminatorProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "b20d632c184382716509197c2fe1617058a8e230"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_624_543_064)
        self.assertEqual(self.proof["base_job_id"], 97_157_732_938)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_157_733_105)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshots_are_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 8930)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "1cadda0251355377ab7de95d6320c5f10ddc139d35bdf39db940304d74d3bf8b",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "8f87049d27b6ab7cc0a35ab72b6caf130593ae19",
        )
        self.assertEqual(self.proof["result_registry_preproof_bytes"], 4038)
        self.assertEqual(
            self.proof["result_registry_preproof_sha256"],
            "0dd8013e4793ce4b3ee2080091931b3515720b3263bd0f807258aae48b2c3a43",
        )
        self.assertEqual(
            self.proof["result_registry_preproof_git_blob"],
            "6bedb1467631b56e5c91a1c698754673a6d36595",
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
        self.assertEqual(self.proof["qualification_route"], "MARC2VR30P-G1")
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
