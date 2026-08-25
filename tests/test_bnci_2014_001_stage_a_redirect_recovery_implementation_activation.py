import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.datasets import (
    bnci_2014_001_stage_a_redirect_recovery as recovery,
)


ROOT = Path(__file__).resolve().parents[1]
ACTIVATION = (
    ROOT
    / "registries/"
    "bnci_2014_001_stage_a_redirect_recovery_implementation_activation.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_IMPLEMENTATION_ACTIVATION.md"
)


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class BNCIStageARedirectRecoveryImplementationActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))

    def test_green_implementation_is_exact(self):
        green = self.activation["green_implementation"]
        self.assertEqual(green["commit"], "09a19d1c1c498bdd6e0ece2fbecb6d15917bdefa")
        self.assertEqual(green["CI_run_id"], 32_806_186_972)
        self.assertEqual(green["base_python_job_id"], 97_676_637_882)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97_676_637_728)
        self.assertTrue(green["both_required_jobs_green"])

    def test_three_artifacts_match_local_and_green_commit(self):
        rows = self.activation["implementation_artifacts"]
        self.assertEqual(len(rows), 3)
        green_commit = self.activation["green_implementation"]["commit"]
        green_available = subprocess.run(
            ["git", "cat-file", "-e", f"{green_commit}^{{commit}}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode == 0
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])
            tracked_blob = subprocess.run(
                ["git", "ls-files", "--stage", "--", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.split()[1]
            self.assertEqual(tracked_blob, row["Git_blob"])
            if green_available:
                committed = subprocess.run(
                    ["git", "show", f"{green_commit}:{row['path']}"],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                ).stdout
                self.assertEqual(payload, committed)

    def test_activation_is_delayed_and_claims_remain_closed(self):
        conditions = self.activation["activation_conditions"]
        self.assertFalse(conditions["this_activation_committed"])
        self.assertFalse(conditions["this_activation_pushed"])
        self.assertFalse(conditions["this_activation_both_required_CI_jobs_green"])
        self.assertFalse(self.activation["claim_boundary"]["scientific_claim_established"])

    def test_committed_activation_passes_runtime_proof_reader(self):
        relative = ACTIVATION.relative_to(ROOT).as_posix()
        committed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if committed.returncode != 0 or committed.stdout != ACTIVATION.read_bytes():
            self.skipTest("activation has not been committed yet")
        tracked_clean = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--"],
            cwd=ROOT,
            check=False,
        ).returncode == 0
        if not tracked_clean:
            self.skipTest("runtime proof reader requires a clean tracked tree")
        green_commit = self.activation["green_implementation"]["commit"]
        green_available = subprocess.run(
            ["git", "cat-file", "-e", f"{green_commit}^{{commit}}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode == 0
        if green_available:
            observed = recovery.read_green_implementation_activation(ROOT)
            self.assertEqual(
                observed["green_implementation"]["CI_run_id"], 32_806_186_972
            )
        else:
            with self.assertRaises(recovery.BNCIAcquisitionRefusal):
                recovery.read_green_implementation_activation(ROOT)

    def test_document_has_separate_engineering_and_scientific_sentences(self):
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering authority added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
