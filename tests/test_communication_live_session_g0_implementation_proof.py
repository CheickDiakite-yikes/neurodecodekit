from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_live_g0_generated as experiment


ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT / "registries/communication_live_session_g0_implementation_proof.v0.json"
)
DOC_PATH = ROOT / "docs/COMMUNICATION_LIVE_SESSION_G0_IMPLEMENTATION_PROOF.md"


class CommunicationLiveSessionG0ImplementationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_proof_is_accepted_by_the_fail_closed_runtime_validator(self) -> None:
        validated = experiment._validate_future_implementation_proof(ROOT)
        self.assertEqual(validated, self.proof)

    def test_remote_green_identity_is_exact(self) -> None:
        self.assertEqual(self.proof["status"], "implementation_remotely_green")
        self.assertEqual(
            self.proof["implementation_commit"],
            "bc9bb109c9c82b56afe06d983d82b5b8ece669cf",
        )
        remote = self.proof["remote_proof"]
        self.assertEqual(remote["CI_run_id"], 33_123_115_516)
        self.assertEqual(
            {(row["name"], row["conclusion"]) for row in remote["jobs"]},
            {("Base Python", "success"), ("Optional Neuro Readers", "success")},
        )
        self.assertEqual(
            {row["job_id"] for row in remote["jobs"]},
            {98_694_674_092, 98_694_674_289},
        )

    def test_all_eight_artifacts_match_bytes_hashes_and_git_blobs(self) -> None:
        rows = self.proof["artifacts"]
        self.assertEqual(len(rows), self.proof["artifact_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), 214_757)
        self.assertEqual(
            {row["path"] for row in rows},
            set(experiment.REQUIRED_IMPLEMENTATION_ARTIFACTS),
        )
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"], row["path"])

    def test_proof_runs_nothing_and_keeps_qualification_closed(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.proof["proof_operations"].values())
        )
        transition = self.proof["proof_transition"]
        self.assertTrue(
            transition[
                "this_proof_commit_push_and_both_jobs_green_required_before_official_qualification"
            ]
        )
        self.assertFalse(
            transition[
                "official_qualification_authorized_before_this_proof_is_remotely_green"
            ]
        )
        self.assertFalse(transition["rerun_or_output_substitution_allowed"])

    def test_human_closeout_preserves_scientific_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("No official generated qualification ran", text)


if __name__ == "__main__":
    unittest.main()
