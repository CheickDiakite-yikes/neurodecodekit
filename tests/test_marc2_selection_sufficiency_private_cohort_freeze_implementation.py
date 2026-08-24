import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc2_selection_sufficiency_private_cohort_freeze_implementation.v0.json"
)
REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
DOC = (
    ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_IMPLEMENTATION.md"
).read_text(encoding="utf-8")


class SelectionSufficiencyPrivateCohortFreezeImplementationTests(unittest.TestCase):
    def test_identity_decision_and_interface_are_exact(self):
        self.assertEqual(REGISTRY["lane_id"], "MARC2-VR39P")
        self.assertEqual(
            REGISTRY["green_decision_proof"]["commit"],
            "dbde5f84b3fac0ac0b23208afd56e00d678aff00",
        )
        self.assertEqual(REGISTRY["green_decision_proof"]["CI_run_id"], 32_681_510_484)
        self.assertTrue(REGISTRY["green_decision_proof"]["both_required_jobs_green"])
        self.assertEqual(
            REGISTRY["interface"]["commands"],
            ["plan", "qualify", "inspect", "execute"],
        )
        self.assertEqual(REGISTRY["interface"]["generic_override_arguments"], 0)

    def test_all_registered_artifacts_match_exact_bytes_and_hashes(self):
        total = 0
        for row in REGISTRY["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            total += len(payload)
        self.assertEqual(total, REGISTRY["implementation_artifact_bytes"])
        self.assertEqual(
            len(REGISTRY["implementation_artifacts"]),
            REGISTRY["implementation_artifact_count"],
        )

    def test_qualification_and_private_proof_states_are_fail_closed(self):
        self.assertIn(REGISTRY["qualification_invocations"], {0, 1})
        self.assertFalse(REGISTRY["qualification_may_be_repeated"])
        self.assertFalse(REGISTRY["private_execution_authorized_now"])
        proof = REGISTRY["remote_implementation_proof"]
        if proof is None:
            self.assertFalse(
                (
                    ROOT
                    / "registries/marc2_selection_sufficiency_private_cohort_freeze_proof_closeout.v0.json"
                ).exists()
            )
        else:
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
            self.assertEqual(proof["qualification_route"], "MARC2VR39P-G1")

    def test_capture_procedure_and_claim_boundaries_are_explicit(self):
        capture = REGISTRY["qualification_capture"]
        self.assertEqual(capture["expected_paths"], 168)
        self.assertEqual((capture["expected_R1"], capture["expected_R2"]), (64, 104))
        self.assertEqual(capture["named_critical_refusal_classes"], 12)
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("captured outside the", DOC)

    def test_all_private_and_scientific_operation_counters_are_zero(self):
        self.assertTrue(all(value == 0 for value in REGISTRY["operation_counters"].values()))
        self.assertEqual(REGISTRY["claim_boundary"]["scientific"], "none")


if __name__ == "__main__":
    unittest.main()
