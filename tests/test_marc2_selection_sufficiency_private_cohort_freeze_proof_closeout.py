import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    marc2_selection_sufficiency_private_cohort_freeze as wrapper,
)


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_REGISTRY = (
    ROOT
    / "registries/marc2_selection_sufficiency_private_cohort_freeze_implementation.v0.json"
)
CLOSEOUT_REGISTRY = (
    ROOT
    / "registries/marc2_selection_sufficiency_private_cohort_freeze_proof_closeout.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_PROOF_CLOSEOUT.md"
)


class SelectionSufficiencyPrivateCohortFreezeProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_REGISTRY.read_text(encoding="utf-8")
        )
        cls.closeout = json.loads(CLOSEOUT_REGISTRY.read_text(encoding="utf-8"))

    def test_exact_remote_green_implementation_is_bound(self):
        proof = self.implementation["remote_implementation_proof"]
        self.assertEqual(
            proof["commit"], "4d48cb38822e3e5a819ce1fef0188069ca6bd9ac"
        )
        self.assertEqual(proof["CI_run_id"], 32_685_719_113)
        self.assertEqual(proof["base_job_id"], 97_310_285_688)
        self.assertEqual(proof["optional_neuro_job_id"], 97_310_285_728)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_after_qualification"])

    def test_preproof_snapshots_and_artifact_set_are_exact(self):
        proof = self.implementation["remote_implementation_proof"]
        self.assertEqual(proof["implementation_registry_preproof_bytes"], 5769)
        self.assertEqual(
            proof["implementation_registry_preproof_sha256"],
            "87c95602cdcb6b2a2ae7be9f41566c5c2909385d7d85b9375ccc6788be4b2e10",
        )
        self.assertEqual(proof["result_registry_preproof_bytes"], 6000)
        self.assertEqual(
            proof["result_registry_preproof_sha256"],
            "de57b975f7f3c676a0d035841ab2137225df1db3f69730553648f7fa33a6c69f",
        )
        artifacts = self.implementation["implementation_artifacts"]
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
        for artifact in artifacts:
            with self.subTest(path=artifact["path"]):
                payload = (ROOT / artifact["path"]).read_bytes()
                git_blob = hashlib.sha1(
                    f"blob {len(payload)}\0".encode("ascii") + payload,
                    usedforsecurity=False,
                ).hexdigest()
                self.assertEqual(
                    proof["implementation_artifact_git_blobs"][artifact["role"]],
                    git_blob,
                )

    def test_closeout_is_delayed_and_executor_remains_closed(self):
        self.assertEqual(
            self.closeout["status"], "proof_only_closeout_remote_proof_pending"
        )
        self.assertIsNone(self.closeout["green_proof"])
        self.assertFalse(self.closeout["qualification_repeated"])
        self.assertEqual(self.closeout["private_operations"], 0)
        self.assertFalse(self.closeout["delayed_effect"]["private_stage_eligible_now"])
        with self.assertRaises(
            wrapper.SelectionSufficiencyPrivateCohortFreezeRefusal
        ):
            wrapper._require_green_implementation(ROOT)

    def test_closeout_did_not_repeat_or_touch_private_state(self):
        self.assertEqual(self.closeout["qualification_route"], "MARC2VR39P-G1")
        self.assertTrue(
            all(value == 0 for value in self.closeout["operation_counters"].values())
        )

    def test_human_closeout_preserves_claim_boundary(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("ineffective until this exact closeout", text)
        self.assertIn("does not repeat the registered generated qualification", text)
        self.assertIn("separate proof-only activation record", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
