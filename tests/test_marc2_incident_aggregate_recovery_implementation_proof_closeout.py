import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/marc2_incident_aggregate_recovery_implementation_proof_closeout.v0.json"
)


class Marc2IncidentAggregateRecoveryImplementationProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_remote_implementation_proof_is_exact(self):
        proof = self.proof["implementation_remote_proof"]
        self.assertEqual(proof["commit"], "046013a4a8089f5a9f3a91fc246420cac21a1d20")
        self.assertEqual(proof["CI_run_id"], 32_445_483_857)
        self.assertEqual(proof["base_python_job_id"], 96_664_169_190)
        self.assertEqual(proof["optional_neuro_job_id"], 96_664_169_147)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_all_artifacts_match_bytes_hashes_and_git_blobs(self):
        rows = self.proof["exact_implementation_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 68_625)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_closeout_repeats_nothing_and_touches_no_ignored_path(self):
        self.assertTrue(self.proof["qualification_not_repeated"])
        self.assertFalse(self.proof["activation_proof_created_now"])
        self.assertFalse(self.proof["aggregate_execution_authorized_now"])
        self.assertTrue(
            all(value == 0 for value in self.proof["closeout_operations"].values())
        )

    def test_next_gate_requires_closeout_and_activation_green(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["this_closeout_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_tracked_clean_activation_proof_required"])
        self.assertTrue(gate["activation_proof_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["explicit_one_shot_arming_required"])
        self.assertFalse(gate["aggregate_report_read_authorized_now"])
        self.assertFalse(gate["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
