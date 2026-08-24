import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_result_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_STAGE_G1_RESULT_PROOF_CLOSEOUT.md"
)


class BNCIStageG1ResultProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_result_commit_and_both_jobs_are_green(self):
        green = self.proof["green_result"]
        self.assertEqual(green["commit"], "4ef12dd056358907ab6734c7a2a21e6776f6f6af")
        self.assertEqual(green["CI_run_id"], 32765504463)
        self.assertEqual(green["base_python_job_id"], 97553936562)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97553936838)
        self.assertEqual(green["base_python_conclusion"], "success")
        self.assertEqual(green["optional_neuro_readers_conclusion"], "success")
        self.assertTrue(green["both_required_jobs_green"])

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
        self.assertEqual(summary["bytes"], 17134)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closed_measurements_match_the_one_shot_result(self):
        result = self.proof["closed_result"]
        self.assertEqual(result["case_classes_passed"], 11)
        self.assertEqual(result["outer_folds"], 9)
        self.assertEqual(result["parameter_update_fits"], 468)
        self.assertEqual(result["prediction_sets"], 495)
        self.assertEqual(result["synthetic_target_deliveries"], 1)
        self.assertEqual(result["synthetic_scoring_events"], 1)
        self.assertEqual(result["retained_generated_payload_bytes"], 0)
        self.assertFalse(result["qualification_may_be_repeated"])

    def test_closeout_performed_no_qualification_or_protected_operation(self):
        operations = self.proof["proof_only_operations"]
        self.assertEqual(operations["GitHub_CI_verification_calls"], 1)
        self.assertEqual(operations["committed_aggregate_artifact_reads"], 3)
        for key, value in operations.items():
            if key not in {"GitHub_CI_verification_calls", "committed_aggregate_artifact_reads"}:
                self.assertEqual(value, 0, key)

    def test_stage_A_is_next_but_not_part_of_this_closeout(self):
        gate = self.proof["next_gate"]
        self.assertFalse(gate["Stage_A_begun"])
        self.assertTrue(gate["Stage_A_is_next_ordered_milestone_after_closeout_green"])
        self.assertTrue(gate["this_closeout_stops_before_Stage_A"])
        self.assertFalse(gate["retry_rerun_resume_restart_or_second_score_allowed"])

    def test_claim_boundary_remains_generated_engineering_only(self):
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_capability":
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("generated fixtures are not neural evidence", document)


if __name__ == "__main__":
    unittest.main()
