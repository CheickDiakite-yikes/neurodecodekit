import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc2_r5_private_discriminator_implementation.v0.json"
DOC_PATH = ROOT / "docs/MARC_2_R5_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md"


class Marc2R5PrivateDiscriminatorProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_exact_remote_implementation_proof_is_bound(self):
        proof = self.record["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"], "bc8ecc38374c57f6be9269874cce8d4497f83551"
        )
        self.assertEqual(proof["CI_run_id"], 32_594_134_914)
        self.assertEqual(proof["base_job_id"], 97_082_352_527)
        self.assertEqual(proof["optional_neuro_job_id"], 97_082_352_441)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_after_qualification"])

    def test_preproof_registry_and_artifact_set_are_exact(self):
        proof = self.record["remote_implementation_proof"]
        self.assertEqual(proof["implementation_registry_preproof_bytes"], 7292)
        self.assertEqual(
            proof["implementation_registry_preproof_sha256"],
            "834850e82a8833de96c2a734def4a2bc9a510c3c9a1377d9c8a2b062a03fa25d",
        )
        self.assertGreater(REGISTRY_PATH.stat().st_size, 7292)
        artifacts = self.record["implementation_artifacts"]
        canonical = json.dumps(
            artifacts,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            proof["implementation_artifact_set_sha256"],
        )

    def test_implementation_artifacts_remain_byte_exact(self):
        for artifact in self.record["implementation_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_closeout_repeats_no_qualification_or_private_operation(self):
        proof = self.record["remote_implementation_proof"]
        closeout = self.record["proof_closeout_verification"]
        self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
        self.assertEqual(proof["private_operations_during_proof_closeout"], 0)
        self.assertFalse(closeout["qualification_repeated"])
        self.assertEqual(closeout["private_operations"], 0)

    def test_human_closeout_preserves_delayed_effect_and_claim_boundary(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("ineffective until its own exact commit", text)
        self.assertIn("does not repeat the registered qualification", text)
        self.assertIn("one registered invocation only", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
