import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_r0_generated as experiment


ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/communication_eeg_independent_replication_generated_activation_proof.v0.json"
)
RESULT_PATH = (
    ROOT / "registries/communication_eeg_independent_replication_generated_result.v0.json"
)
HARDENING_PATH = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_generated_postfailure_hardening.v0.json"
)


class CommR0GeneratedActivationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))
        hardening = json.loads(HARDENING_PATH.read_text(encoding="utf-8"))
        cls.transitions = {
            artifact["path"]: artifact for artifact in hardening["changed_artifacts"]
        }

    def test_strict_loader_accepts_the_complete_local_chain(self) -> None:
        observed = experiment.load_activation_proof(ROOT)
        self.assertEqual(observed["lane_id"], "COMM-R0-G")
        self.assertEqual(
            observed["proof_closeout_commit"],
            "91e4522ab0cb766444f221321033b864b0be7362",
        )

    def test_green_activation_and_corrected_closeout_are_exact(self) -> None:
        activation = self.proof["green_activation_commit"]
        self.assertEqual(
            activation["commit"], "9b47f15e3adc83c32359d19428878226ab06c2d4"
        )
        self.assertEqual(activation["CI_run_id"], 33_093_134_150)
        self.assertTrue(activation["both_required_jobs_green"])
        closeout = self.proof["green_proof_closeout_commit"]
        self.assertEqual(
            closeout["commit"], "91e4522ab0cb766444f221321033b864b0be7362"
        )
        self.assertEqual(closeout["CI_run_id"], 33_095_028_205)
        self.assertEqual(closeout["base_python_job_id"], 98_597_573_019)
        self.assertEqual(closeout["optional_neuro_readers_job_id"], 98_597_572_816)
        self.assertTrue(closeout["both_required_jobs_green"])

    def test_three_closeout_artifacts_are_exact(self) -> None:
        artifacts = self.proof["bound_proof_closeout_artifacts"]
        self.assertEqual(len(artifacts), 3)
        self.assertEqual(sum(row["bytes"] for row in artifacts), 7_641)
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            transition = self.transitions.get(artifact["path"])
            if transition is None:
                self.assertEqual(len(payload), artifact["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
                observed_blob = subprocess.check_output(
                    ["git", "hash-object", artifact["path"]], cwd=ROOT, text=True
                ).strip()
                self.assertEqual(observed_blob, artifact["Git_blob"])
            else:
                self.assertEqual(artifact["bytes"], transition["before_bytes"])
                self.assertEqual(artifact["sha256"], transition["before_sha256"])
                self.assertEqual(len(payload), transition["after_bytes"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(), transition["after_sha256"]
                )

    def test_proof_creation_performs_zero_operations(self) -> None:
        self.assertTrue(all(value == 0 for value in self.proof["operation_counters"].values()))
        delayed = self.proof["delayed_effect"]
        self.assertTrue(delayed["this_proof_commit_push_and_both_jobs_green_required"])
        self.assertFalse(delayed["official_generated_qualification_allowed_before_own_green"])
        self.assertFalse(delayed["real_or_private_operation_allowed"])
        self.assertFalse(delayed["rerun_allowed"])

    def test_result_transition_is_strict_when_present(self) -> None:
        if RESULT_PATH.exists():
            self.assertEqual(experiment.inspect_result(root=ROOT)["lane_id"], "COMM-R0-G")

    def test_claim_boundary_is_scientifically_empty(self) -> None:
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_value"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_value"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
