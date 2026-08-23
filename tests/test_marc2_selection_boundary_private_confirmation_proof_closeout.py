import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_selection_boundary_private_confirmation as wrapper

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/marc2_selection_boundary_private_confirmation_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_SELECTION_BOUNDARY_PRIVATE_CONFIRMATION_PROOF_CLOSEOUT.md"
)


class Marc2SelectionBoundaryPrivateConfirmationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.proof = cls.record["remote_implementation_proof"]

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.proof["commit"], "d5c5abd8fde15f0557101fa2aa1135382819ea4e"
        )
        self.assertEqual(self.proof["CI_run_id"], 32_609_236_180)
        self.assertEqual(self.proof["base_job_id"], 97_119_373_912)
        self.assertEqual(self.proof["optional_neuro_job_id"], 97_119_373_779)
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertFalse(self.proof["scope_changed_after_qualification"])

    def test_preproof_registry_snapshot_is_literal_and_immutable(self):
        self.assertEqual(self.proof["implementation_registry_preproof_bytes"], 7417)
        self.assertEqual(
            self.proof["implementation_registry_preproof_sha256"],
            "7fd661aad6a809b1a5bb8f814d4045533475303984be9ea72531e0c537868284",
        )
        self.assertEqual(
            self.proof["implementation_registry_preproof_git_blob"],
            "ceafc760b3d8fbfd770a895a798d253ff0272462",
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
        self.assertEqual(self.proof["qualification_route"], "MARC2VR26P-G1")
        self.assertFalse(self.proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(self.proof["private_operations_during_proof_closeout"], 0)
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_human_closeout_preserves_delayed_effect_and_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("ineffective until its own exact commit", text)
        self.assertIn("does not repeat the registered qualification", text)
        self.assertIn("one registered invocation only", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
