import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/dreyer_c5r_1_stage_h_l2_fixed_header_activation_request_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_ACTIVATION_REQUEST_PROOF_CLOSEOUT.md"
)


class DreyerStageHL2FixedHeaderActivationRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_request_commit_and_both_jobs_are_green(self):
        green = self.proof["green_request"]
        self.assertEqual(
            green["commit"], "a97fc191106e5fe42859d871d78e59930bef79ac"
        )
        self.assertEqual(green["CI_run_id"], 33_255_920_346)
        self.assertEqual(green["base_python_job_id"], 99_109_482_999)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_109_482_995)
        self.assertEqual(green["base_python_conclusion"], "success")
        self.assertEqual(green["optional_neuro_readers_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_bound_request_artifacts_are_exact_and_canonical(self):
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
        self.assertEqual(summary["bytes"], 18_035)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_proof_performed_no_authority_bearing_operation(self):
        operations = self.proof["proof_only_operations"]
        self.assertEqual(operations["GitHub_CI_verification_calls"], 1)
        self.assertEqual(operations["committed_request_artifact_reads"], 3)
        for key, value in operations.items():
            if key not in {
                "GitHub_CI_verification_calls",
                "committed_request_artifact_reads",
            }:
                self.assertEqual(value, 0, key)

    def test_fresh_post_packet_decision_is_required(self):
        gate = self.proof["next_gate"]
        self.assertTrue(
            gate["fresh_packet_bound_maintainer_words_required_after_proof_green"]
        )
        self.assertFalse(gate["predating_maintainer_words_may_activate"])
        self.assertFalse(gate["decision_recorded"])
        self.assertFalse(gate["HL2_authority"])
        self.assertFalse(gate["real_EDF_access_allowed"])

    def test_claim_boundary_remains_request_engineering_only(self):
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_capability":
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("earlier `continue` predates this packet", document)


if __name__ == "__main__":
    unittest.main()
