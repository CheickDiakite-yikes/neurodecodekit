from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries"
    / "communication_eeg_source_identity_metadata_request_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_SOURCE_IDENTITY_METADATA_REQUEST_PROOF_CLOSEOUT.md"
)


class CommunicationEEGSourceIdentityMetadataRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_request_commit_is_remotely_green(self) -> None:
        green = self.proof["green_request_commit"]
        self.assertEqual(
            green["commit"], "12e4e9f6e669bd1645911804b8e1c265fb04be29"
        )
        self.assertEqual(green["CI_run_id"], 33062307015)
        self.assertEqual(green["base_python_job_id"], 98483805541)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98483805735)
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_request_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_request_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_request_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 33996)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_scope_and_active_gate_are_unchanged(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["request_artifacts_unchanged"])
        self.assertTrue(scope["active_DREYER_C5R_1_HL_gate_preserved"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])
        transition = self.proof["transition"]
        self.assertFalse(transition["COMM_L0_META_active_after_remote_green"])
        self.assertTrue(transition["DREYER_C5R_1_HL_remains_sole_active_Tier_C_packet"])
        self.assertFalse(transition["implementation_authorized_by_closeout"])
        self.assertFalse(transition["network_or_real_operation_authorized_by_closeout"])

    def test_only_tracked_and_git_proof_reads_occurred(self) -> None:
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 3)
        self.assertEqual(counters["Git_proof_reads"], 3)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_claim_and_next_gate_language_are_explicit(self) -> None:
        boundary = self.proof["claim_boundary"]
        self.assertTrue(
            all(
                value is False
                for key, value in boundary.items()
                if key != "engineering_proof_added"
            )
        )
        document = " ".join(DOCUMENT.read_text(encoding="utf-8").split())
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("remains the sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
