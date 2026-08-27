import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_r0_generated as experiment


ROOT = Path(__file__).resolve().parents[1]
ACTIVATION_PATH = (
    ROOT
    / "registries/communication_eeg_independent_replication_generated_activation.v0.json"
)
RESULT_PATH = (
    ROOT / "registries/communication_eeg_independent_replication_generated_result.v0.json"
)


class CommR0GeneratedActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.activation = json.loads(ACTIVATION_PATH.read_text(encoding="utf-8"))

    def test_exact_green_implementation_is_bound(self) -> None:
        green = self.activation["green_implementation_commit"]
        self.assertEqual(
            green["commit"], "e0c587c36739af597e069bb68d84430d68b6e93b"
        )
        self.assertEqual(green["CI_run_id"], 33_091_909_015)
        self.assertEqual(green["base_python_job_id"], 98_586_671_291)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_586_671_285)
        self.assertTrue(green["both_required_jobs_green"])

    def test_six_implementation_artifacts_are_exact(self) -> None:
        artifacts = self.activation["implementation_artifacts"]
        self.assertEqual(len(artifacts), 6)
        for artifact in artifacts:
            path = ROOT / artifact["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])
            observed_blob = subprocess.check_output(
                ["git", "hash-object", artifact["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(observed_blob, artifact["Git_blob"])

    def test_activation_loads_but_proof_and_result_remain_absent(self) -> None:
        self.assertEqual(experiment.load_activation(ROOT)["lane_id"], "COMM-R0-G")
        with self.assertRaisesRegex(Exception, "ACTIVATION-PROOF-ABSENT"):
            experiment.load_activation_proof(ROOT)
        self.assertFalse(RESULT_PATH.exists())

    def test_authority_is_generated_only_and_delayed(self) -> None:
        authority = self.activation["authority"]
        self.assertTrue(authority["generated_qualification"])
        self.assertEqual(authority["generated_qualification_invocations_maximum"], 1)
        for key, value in authority.items():
            if key not in {
                "generated_qualification",
                "generated_qualification_invocations_maximum",
            }:
                self.assertFalse(value)
        self.assertTrue(
            all(value == 0 for value in self.activation["operation_counters"].values())
        )
        delayed = self.activation["delayed_effect"]
        self.assertTrue(delayed["activation_commit_must_be_remotely_green"])
        self.assertTrue(delayed["separate_activation_proof_closeout_must_be_remotely_green"])
        self.assertTrue(delayed["separate_tracked_activation_proof_must_be_remotely_green"])
        self.assertFalse(delayed["qualification_allowed_before_all_barriers"])

    def test_claim_boundary_is_scientifically_empty(self) -> None:
        claims = self.activation["claim_boundary"]
        self.assertEqual(claims["scientific_value"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_value"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
