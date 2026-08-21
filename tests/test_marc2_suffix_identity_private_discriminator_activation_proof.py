import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLOSEOUT_COMMIT = "2acfb3318beb46ade294fdc3ff0fc21765e3ea17"
PROOF_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_implementation_proof.v0.json"
)


class Marc2SuffixIdentityPrivateDiscriminatorActivationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_exact_green_barriers_are_bound(self):
        self.assertEqual(
            self.proof["implementation_commit"],
            "28a734df3fb0cb83c3cddb4994b76d8c9453830b",
        )
        self.assertEqual(self.proof["implementation_CI_run_id"], 32_454_196_219)
        self.assertEqual(
            self.proof["implementation_base_python_job_id"], 96_688_236_516
        )
        self.assertEqual(
            self.proof["implementation_optional_neuro_job_id"], 96_688_236_752
        )
        self.assertTrue(self.proof["implementation_both_required_jobs_green"])
        self.assertEqual(
            self.proof["proof_closeout_commit"],
            "2acfb3318beb46ade294fdc3ff0fc21765e3ea17",
        )
        self.assertEqual(self.proof["proof_closeout_CI_run_id"], 32_454_892_777)
        self.assertEqual(
            self.proof["proof_closeout_base_python_job_id"], 96_690_180_933
        )
        self.assertEqual(
            self.proof["proof_closeout_optional_neuro_job_id"], 96_690_181_096
        )
        self.assertTrue(self.proof["proof_closeout_both_required_jobs_green"])

    def test_closeout_artifacts_match_bytes_hashes_and_blobs(self):
        rows = self.proof["exact_bound_closeout_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 9_513)
        for row in rows:
            payload = subprocess.run(
                ["git", "show", f"{CLOSEOUT_COMMIT}:{row['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "rev-parse", f"{CLOSEOUT_COMMIT}:{row['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_activation_itself_performs_no_private_operation(self):
        self.assertTrue(
            all(value == 0 for value in self.proof["activation_operations"].values())
        )
        gate = self.proof["execution_gate"]
        self.assertTrue(gate["this_activation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["tracked_and_clean_activation_record_required"])
        self.assertTrue(gate["exact_one_shot_arm_required"])
        self.assertFalse(gate["private_access_authorized_before_this_record_is_remotely_green"])

    def test_private_scope_is_single_fixed_and_aggregate_only(self):
        self.assertTrue(self.proof["private_structural_content_open_authorized"])
        self.assertEqual(self.proof["private_structural_content_open_count"], 1)
        self.assertEqual(self.proof["private_structural_bytes"], 418_755)
        self.assertEqual(self.proof["strict_JSON_parse_count"], 1)
        self.assertEqual(self.proof["VR15A_call_count"], 1)
        self.assertEqual(self.proof["nested_VR12A_call_count"], 1)
        self.assertEqual(
            self.proof["allowed_aggregate_routes"],
            [f"MARC2VR15P-R{index}" for index in range(1, 17)],
        )
        self.assertFalse(self.proof["cohort_manifest_allowed"])
        self.assertFalse(self.proof["retry_rerun_resume_allowed"])
        self.assertFalse(self.proof["execution_gate"]["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
