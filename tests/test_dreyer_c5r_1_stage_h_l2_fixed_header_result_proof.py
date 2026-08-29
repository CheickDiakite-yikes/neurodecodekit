import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_l2_fixed_header_result_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_RESULT_PROOF_CLOSEOUT.md"
)


class DreyerStageHL2FixedHeaderResultProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_result_closeout_is_on_main_and_both_jobs_are_green(self):
        green = self.proof["green_result_closeout"]
        self.assertEqual(
            green["commit"], "eec3db2a225d6ea2377e6a2426297c4d327059b1"
        )
        self.assertEqual(green["CI_run_id"], 33_263_185_054)
        self.assertEqual(green["base_python_job_id"], 99_128_522_536)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_128_522_652)
        self.assertEqual(green["base_python_conclusion"], "success")
        self.assertEqual(green["optional_neuro_readers_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_duplicate_branch_proof_is_also_green(self):
        branch = self.proof["duplicate_branch_proof"]
        self.assertEqual(branch["CI_run_id"], 33_263_182_131)
        self.assertEqual(branch["base_python_job_id"], 99_128_514_962)
        self.assertEqual(branch["optional_neuro_readers_job_id"], 99_128_514_958)
        self.assertTrue(branch["both_required_jobs_green"])

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
        self.assertEqual(summary["count"], 4)
        self.assertEqual(summary["bytes"], 14_734)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closed_result_is_consumed_transport_H0_not_biological_null(self):
        result = self.proof["closed_result"]
        self.assertEqual(result["route"], "DREYER-H0")
        self.assertEqual(result["refusal_code"], "HL2-TRANSPORT")
        self.assertEqual(result["registered_invocations_consumed"], 1)
        self.assertFalse(
            result[
                "retry_rerun_repair_resume_substitute_or_reinterpret_allowed"
            ]
        )
        self.assertEqual(result["real_network_body_bytes"], 0)
        self.assertEqual(result["real_fixed_header_reads"], 0)
        self.assertFalse(result["payload_retained"])
        self.assertFalse(result["biological_null"])

    def test_proof_performed_no_protected_or_scientific_operation(self):
        operations = self.proof["proof_only_operations"]
        self.assertEqual(operations["existing_GitHub_CI_runs_verified"], 2)
        self.assertEqual(operations["unique_committed_public_artifacts_verified"], 4)
        for key, value in operations.items():
            if key not in {
                "existing_GitHub_CI_runs_verified",
                "unique_committed_public_artifacts_verified",
            }:
                self.assertEqual(value, 0, key)

    def test_next_gate_is_reversible_source_reselection(self):
        gate = self.proof["next_gate"]
        self.assertIsNone(gate["active_Tier_C_gate_after_result_closeout"])
        self.assertTrue(gate["source_reselection_authorized_as_Tier_A_research"])
        self.assertFalse(gate["real_data_transaction_authorized"])
        self.assertFalse(gate["HL2_may_be_reopened"])

    def test_claim_boundary_and_human_closeout_are_explicit(self):
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_capability":
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("fail-closed transport result, not a biological null", document)


if __name__ == "__main__":
    unittest.main()
