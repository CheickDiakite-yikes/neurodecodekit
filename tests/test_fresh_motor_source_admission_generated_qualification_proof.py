from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/fresh_motor_source_admission_generated_qualification_proof.v0.json"
FRONTIER = ROOT / "registries/current_research_frontier.v20.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_ADMISSION_GENERATED_QUALIFICATION_PROOF_CLOSEOUT.md"


def _git_blob(payload: bytes) -> str:
    prefix = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(prefix + payload).hexdigest()


class FreshMotorSourceAdmissionGeneratedQualificationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_green_result_and_failed_predecessor_are_exact(self) -> None:
        green = self.proof["green_result"]
        self.assertEqual(green["commit"], "9f5ff18ff85988581f49b65a121ce80d75b67048")
        self.assertEqual(green["CI_run_id"], 33_352_074_929)
        self.assertEqual(green["base_python_job_id"], 99_367_259_645)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_367_259_785)
        self.assertTrue(green["both_required_jobs_green"])
        failed = self.proof["failed_result_predecessor"]
        self.assertEqual(failed["CI_run_id"], 33_351_221_770)
        self.assertFalse(failed["both_required_jobs_green"])
        self.assertEqual(failed["qualification_reruns_during_correction"], 0)

    def test_four_result_artifacts_are_exact(self) -> None:
        rows = self.proof["bound_result_artifacts"]
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(row["bytes"] for row in rows), 30_764)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            self.assertEqual(_git_blob(payload), row["git_blob"], row["path"])

    def test_proof_did_not_repeat_or_expand_work(self) -> None:
        counters = self.proof["proof_operation_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))
        authority = self.proof["authority_after_own_remote_green"]
        self.assertFalse(authority["additional_generated_qualification_or_rehearsal"])
        self.assertTrue(authority["prepare_one_all_false_R1_W_source_identity_witness_packet"])
        self.assertFalse(authority["execute_R1_W_without_fresh_packet_bound_Tier_C_decision"])

    def test_frontier_preserves_scientific_boundary(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v19.json",
        )
        self.assertTrue(self.frontier["green_generated_result"]["consumed"])
        self.assertFalse(
            self.frontier["operation_authority_now"][
                "additional_generated_qualification_or_rehearsal"
            ]
        )
        self.assertFalse(self.frontier["claim_boundary"]["real_EEG_accessed"])
        self.assertFalse(self.frontier["claim_boundary"]["neural_advantage_established"])

    def test_human_closeout_separates_engineering_and_science(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
