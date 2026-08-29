from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/ofner_gdf_header_generated_qualification_proof.v0.json"
DOCUMENT = (
    ROOT
    / "docs/OFNER_2017_MOTOR_IMAGERY_FIXED_HEADER_GENERATED_QUALIFICATION_PROOF_CLOSEOUT.md"
)


class OfnerGDFHeaderGeneratedQualificationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_successor_commit_is_remotely_green(self) -> None:
        green = self.proof["green_implementation_commit"]
        self.assertEqual(
            green["commit"], "ca5d1db35a34762905d4df823766a6d353516c66"
        )
        self.assertEqual(green["CI_run_id"], 33_271_860_805)
        self.assertEqual(green["base_python_job_id"], 99_151_605_412)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_151_605_230)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_exact_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_implementation_and_result_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_artifact_summary"]
        self.assertEqual(summary["count"], 5)
        self.assertEqual(summary["bytes"], 47_954)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_changes_no_authority_or_claim(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["qualified_module_unchanged"])
        self.assertTrue(scope["standalone_CLI_unchanged"])
        self.assertTrue(scope["focused_test_unchanged"])
        self.assertTrue(scope["result_artifacts_unchanged"])
        self.assertFalse(scope["qualification_rerun"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])
        transition = self.proof["transition"]
        self.assertFalse(transition["real_metadata_operation_authorized_by_closeout"])
        self.assertFalse(transition["real_payload_operation_authorized_by_closeout"])
        self.assertFalse(transition["real_header_operation_authorized_by_closeout"])
        self.assertIsNone(transition["active_Tier_C_packet_after_closeout"])

    def test_only_tracked_and_git_proof_reads_occurred(self) -> None:
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 5)
        self.assertEqual(counters["Git_proof_reads"], 5)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_document_states_capability_nonclaim_and_next_gate(self) -> None:
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("all-false Tier C request", document)


if __name__ == "__main__":
    unittest.main()
