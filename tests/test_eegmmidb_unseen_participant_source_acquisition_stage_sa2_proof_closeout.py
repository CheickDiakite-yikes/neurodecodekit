import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa2_proof_closeout.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_STAGE_SA2_PROOF_CLOSEOUT.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionStageSA2ProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_result_was_remotely_green_before_closeout(self):
        result = self.proof["green_result"]
        self.assertEqual(
            result["commit"], "ba8645e66d98020daa0139d561e92e33551b9255"
        )
        self.assertEqual(result["CI_run_id"], 32740773041)
        self.assertEqual(result["base_python_job_id"], 97474420839)
        self.assertEqual(result["optional_neuro_readers_job_id"], 97474421286)
        self.assertTrue(result["both_required_jobs_green"])

    def test_six_bound_artifacts_are_exact_in_current_tree(self):
        rows = self.proof["bound_artifacts"]
        self.assertEqual(len(rows), 6)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

    def test_artifact_summary_replays_exactly(self):
        rows = self.proof["bound_artifacts"]
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["artifact_summary"]
        self.assertEqual(summary["count"], 6)
        self.assertEqual(summary["bytes"], 108663)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_has_only_tracked_and_Git_proof_reads(self):
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 6)
        self.assertEqual(counters["Git_proof_reads"], 6)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_terminal_boundary_forbids_retry_and_marker_access(self):
        boundary = self.proof["terminal_boundary"]
        self.assertTrue(boundary["stage_SA2_consumed"])
        self.assertTrue(boundary["stage_SA2_permanently_parked"])
        self.assertFalse(
            boundary["retry_rerun_repair_resume_bypass_fallback_or_substitution_allowed"]
        )
        self.assertFalse(boundary["consumed_marker_may_be_opened_modified_or_deleted"])
        self.assertFalse(boundary["dependent_UG1_source_LOSO_executable"])

    def test_verification_counts_and_claim_ceiling_are_explicit(self):
        verification = self.proof["verification"]
        self.assertEqual(verification["focused_tests_passed"], 23)
        self.assertEqual(verification["closeout_base_tests_passed"], 5920)
        self.assertEqual(verification["net_new_tests_passed"], 7)
        claim = self.proof["claim_boundary"]
        self.assertFalse(claim["scientific_claim_established"])
        self.assertFalse(claim["real_EEG_accessed_by_closeout"])

    def test_human_closeout_separates_engineering_and_science(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Proof recorded", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("does not inspect the ignored consumed marker", document)


if __name__ == "__main__":
    unittest.main()
