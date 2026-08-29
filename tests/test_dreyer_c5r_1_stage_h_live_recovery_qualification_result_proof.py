import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_live_recovery_qualification_result_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/DREYER_C5R_1_STAGE_H_LIVE_RECOVERY_QUALIFICATION_RESULT_PROOF_CLOSEOUT.md"
)


class DreyerStageHLiveRecoveryQualificationResultProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_result_closeout_and_both_jobs_are_green(self):
        green = self.proof["green_result_closeout"]
        self.assertEqual(
            green["commit"], "cb7e7f831a1056dfcf878ca23ed53aa6fd4738dc"
        )
        self.assertEqual(green["CI_run_id"], 33_254_474_440)
        self.assertEqual(green["base_python_job_id"], 99_105_690_584)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_105_690_672)
        self.assertEqual(green["base_python_conclusion"], "success")
        self.assertEqual(green["optional_neuro_readers_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_bound_result_artifacts_are_exact_and_canonical(self):
        rows = self.proof["bound_artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(
            rows, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        summary = self.proof["bound_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 13_827)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closed_result_is_consumed_generated_engineering_only(self):
        result = self.proof["closed_result"]
        self.assertEqual(result["matrix_cases_passed"], 65)
        self.assertEqual(result["registered_attempts_consumed"], 1)
        self.assertEqual(result["real_or_private_operations"], 0)
        self.assertFalse(result["qualification_may_be_repeated"])
        self.assertEqual(
            result["scientific_value"], "none_generated_engineering_only"
        )

    def test_proof_reopened_nothing_and_performed_no_protected_operation(self):
        operations = self.proof["proof_only_operations"]
        self.assertEqual(operations["GitHub_CI_verification_calls"], 1)
        self.assertEqual(operations["committed_aggregate_artifact_reads"], 3)
        for key, value in operations.items():
            if key not in {
                "GitHub_CI_verification_calls",
                "committed_aggregate_artifact_reads",
            }:
                self.assertEqual(value, 0, key)

    def test_HL2_is_only_the_next_all_false_request(self):
        gate = self.proof["next_gate"]
        self.assertTrue(
            gate["HL2_all_false_request_preparation_is_next_after_proof_green"]
        )
        self.assertFalse(gate["HL2_request_prepared"])
        self.assertFalse(gate["HL2_authority"])
        self.assertFalse(gate["real_EDF_access_allowed"])
        self.assertFalse(gate["retry_rerun_resume_repair_or_substitution_allowed"])

    def test_claim_boundary_remains_generated_engineering_only(self):
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_capability":
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real EEG was accessed or tested", document)


if __name__ == "__main__":
    unittest.main()
