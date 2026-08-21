import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/marc2_incident_aggregate_recovery_implementation_proof.v0.json"
)


class Marc2IncidentAggregateRecoveryActivationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_exact_green_barriers_are_bound(self):
        self.assertEqual(
            self.proof["implementation_commit"],
            "046013a4a8089f5a9f3a91fc246420cac21a1d20",
        )
        self.assertEqual(self.proof["implementation_CI_run_id"], 32_445_483_857)
        self.assertEqual(
            self.proof["implementation_base_python_job_id"], 96_664_169_190
        )
        self.assertEqual(
            self.proof["implementation_optional_neuro_job_id"], 96_664_169_147
        )
        self.assertTrue(self.proof["both_required_jobs_green"])
        self.assertEqual(
            self.proof["proof_closeout_commit"],
            "f352c1b50d15ab81f641dca21732e1ffffa7a6b8",
        )
        self.assertEqual(self.proof["proof_closeout_CI_run_id"], 32_446_071_998)
        self.assertEqual(
            self.proof["proof_closeout_base_python_job_id"], 96_665_759_734
        )
        self.assertEqual(
            self.proof["proof_closeout_optional_neuro_job_id"], 96_665_759_548
        )
        self.assertTrue(self.proof["proof_closeout_both_required_jobs_green"])

    def test_closeout_artifacts_match_bytes_hashes_and_blobs(self):
        rows = self.proof["exact_bound_closeout_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 8_959)
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

    def test_activation_itself_performs_no_execution(self):
        self.assertTrue(
            all(value == 0 for value in self.proof["activation_operations"].values())
        )
        gate = self.proof["execution_gate"]
        self.assertTrue(gate["this_activation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["tracked_and_clean_activation_record_required"])
        self.assertTrue(gate["explicit_one_shot_arming_required"])
        self.assertFalse(
            gate[
                "aggregate_report_read_authorized_before_this_record_is_remotely_green"
            ]
        )

    def test_execution_scope_is_single_and_fixed(self):
        self.assertTrue(self.proof["aggregate_report_content_opens_authorized"])
        self.assertEqual(self.proof["aggregate_report_content_open_count"], 1)
        self.assertEqual(self.proof["aggregate_report_bytes_maximum"], 65_536)
        self.assertEqual(self.proof["recovery_receipt_count_maximum"], 1)
        self.assertFalse(self.proof["retry_rerun_resume_allowed"])
        self.assertEqual(self.proof["structural_source_operations_allowed"], 0)
        self.assertEqual(self.proof["private_manifest_operations_allowed"], 0)
        self.assertFalse(self.proof["execution_gate"]["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
