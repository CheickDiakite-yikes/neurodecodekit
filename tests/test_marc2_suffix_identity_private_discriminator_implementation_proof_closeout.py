import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_COMMIT = "2acfb3318beb46ade294fdc3ff0fc21765e3ea17"
PROOF_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_implementation_proof_closeout.v0.json"
)


class Marc2SuffixIdentityPrivateDiscriminatorProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_remote_implementation_proof_is_exact(self):
        proof = self.proof["implementation_remote_proof"]
        self.assertEqual(
            proof["commit"], "28a734df3fb0cb83c3cddb4994b76d8c9453830b"
        )
        self.assertEqual(proof["CI_run_id"], 32_454_196_219)
        self.assertEqual(proof["base_python_job_id"], 96_688_236_516)
        self.assertEqual(proof["optional_neuro_job_id"], 96_688_236_752)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_all_artifacts_match_bytes_hashes_and_git_blobs(self):
        rows = self.proof["exact_implementation_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 77_152)
        for row in rows:
            payload = subprocess.run(
                ["git", "show", f"{PROOF_COMMIT}:{row['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "rev-parse", f"{PROOF_COMMIT}:{row['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_closeout_repeats_nothing_and_touches_no_private_path(self):
        self.assertTrue(self.proof["qualification_not_repeated"])
        self.assertEqual(self.proof["proof_metadata_artifacts_updated"], 3)
        self.assertFalse(self.proof["activation_proof_created_now"])
        self.assertFalse(self.proof["private_execution_authorized_now"])
        self.assertTrue(
            all(value == 0 for value in self.proof["closeout_operations"].values())
        )

    def test_next_gate_requires_closeout_and_activation_green(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["this_closeout_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_tracked_clean_activation_proof_required"])
        self.assertTrue(gate["activation_proof_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["explicit_one_shot_arming_required"])
        self.assertFalse(gate["private_source_or_readiness_access_authorized_now"])
        self.assertFalse(gate["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
