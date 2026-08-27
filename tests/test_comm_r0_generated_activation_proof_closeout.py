import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_PATH = (
    ROOT
    / "registries/communication_eeg_independent_replication_generated_activation_proof_closeout.v0.json"
)


class CommR0GeneratedActivationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.closeout = json.loads(CLOSEOUT_PATH.read_text(encoding="utf-8"))

    def test_exact_green_activation_is_bound(self) -> None:
        green = self.closeout["green_activation_commit"]
        self.assertEqual(
            green["commit"], "9b47f15e3adc83c32359d19428878226ab06c2d4"
        )
        self.assertEqual(green["CI_run_id"], 33_093_134_150)
        self.assertEqual(green["base_python_job_id"], 98_590_992_544)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_590_992_988)
        self.assertTrue(green["both_required_jobs_green"])

    def test_three_activation_artifacts_are_exact(self) -> None:
        artifacts = self.closeout["bound_activation_artifacts"]
        self.assertEqual(len(artifacts), 3)
        self.assertEqual(sum(row["bytes"] for row in artifacts), 9_968)
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
            observed_blob = subprocess.check_output(
                ["git", "hash-object", artifact["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(observed_blob, artifact["Git_blob"])

    def test_closeout_runs_no_generated_or_scientific_operation(self) -> None:
        operations = self.closeout["proof_operations"]
        self.assertEqual(operations["tracked_artifact_reads"], 3)
        self.assertEqual(operations["Git_proof_reads"], 3)
        for key, value in operations.items():
            if key not in {"tracked_artifact_reads", "Git_proof_reads"}:
                self.assertEqual(value, 0)

    def test_next_gate_remains_fail_closed(self) -> None:
        gate = self.closeout["next_gate"]
        self.assertTrue(gate["tracked_activation_proof_required"])
        self.assertTrue(gate["tracked_activation_proof_must_bind_this_closeout_green_commit"])
        self.assertTrue(gate["tracked_activation_proof_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["official_generated_qualification_allowed_now"])
        self.assertFalse(gate["real_or_private_operation_allowed"])

    def test_claim_boundary_is_scientifically_empty(self) -> None:
        claims = self.closeout["claim_boundary"]
        self.assertEqual(claims["scientific_value"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_value"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
