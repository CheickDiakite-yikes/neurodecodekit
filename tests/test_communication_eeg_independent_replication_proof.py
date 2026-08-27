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
    / "communication_eeg_independent_replication_proof.v0.json"
)
DOCUMENT = (
    ROOT / "docs" / "COMMUNICATION_EEG_INDEPENDENT_REPLICATION_PROOF_CLOSEOUT.md"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationEEGIndependentReplicationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_registration_commit_is_remotely_green(self) -> None:
        green = self.proof["green_registration_commit"]
        self.assertEqual(
            green["commit"], "dc80adb76fe5fc45add07cc515e02521a5110ae9"
        )
        self.assertEqual(green["CI_run_id"], 33075946525)
        self.assertEqual(green["base_python_job_id"], 98530039527)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98530039228)
        self.assertTrue(green["both_required_jobs_green"])

    def test_exact_registration_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_registration_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_registration_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 47205)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_scope_and_active_gate_are_unchanged(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["registration_artifacts_unchanged"])
        self.assertTrue(scope["active_DREYER_C5R_1_HL_gate_preserved"])
        self.assertTrue(scope["COMM_L0_META_remains_queued_all_false"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])

        transition = self.proof["transition"]
        self.assertTrue(transition["registration_remotely_proven_after_closeout_green"])
        self.assertTrue(transition["DREYER_C5R_1_HL_remains_sole_active_Tier_C_packet"])
        self.assertFalse(transition["COMM_L0_META_active_after_remote_green"])
        self.assertFalse(transition["network_or_real_operation_authorized_by_closeout"])
        self.assertFalse(transition["target_delivery_or_scoring_authorized_by_closeout"])

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

    def test_frontier_and_claim_language_are_explicit(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        registration = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["independent_replication_preregistration"]
        self.assertEqual(
            registration["green_registration_proof_commit"],
            "dc80adb76fe5fc45add07cc515e02521a5110ae9",
        )
        self.assertEqual(
            registration["green_registration_proof_CI_run_id"], 33075946525
        )
        self.assertTrue(
            registration["green_registration_proof_both_required_jobs_green"]
        )
        self.assertEqual(
            registration["proof_registry"],
            "registries/communication_eeg_independent_replication_proof.v0.json",
        )

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
