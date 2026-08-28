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
    / "communication_eeg_prospective_generated_qualification_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_PROOF_CLOSEOUT.md"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationEEGProspectiveGeneratedQualificationProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_registration_commit_is_green_and_on_main(self) -> None:
        green = self.proof["green_registration_commit"]
        self.assertEqual(
            green["commit"], "002128bd9cbacddd8ceea1820b3b91622c40867f"
        )
        self.assertEqual(green["CI_run_id"], 33_136_788_477)
        self.assertEqual(green["base_python_job_id"], 98_738_427_136)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_738_427_224)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["working_branch_matches_exact_commit"])
        self.assertTrue(green["GitHub_main_matches_exact_commit"])

    def test_registration_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_registration_artifacts"]
        source_commit = self.proof["bound_registration_artifact_summary"][
            "artifact_source_commit"
        ]
        for row in rows:
            payload = subprocess.check_output(
                ["git", "show", f"{source_commit}:{row['path']}"], cwd=ROOT
            )
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            blob = subprocess.check_output(
                ["git", "rev-parse", f"{source_commit}:{row['path']}"],
                cwd=ROOT,
                text=True,
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_registration_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 47_492)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_preserves_scope_and_delays_execution(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["registration_artifacts_unchanged"])
        self.assertTrue(scope["target_firewall_and_control_matrix_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["active_Tier_C_gate_changed"])
        self.assertFalse(scope["claim_boundary_changed"])

        transition = self.proof["transition"]
        self.assertTrue(
            transition[
                "generated_implementation_may_begin_after_this_closeout_is_remotely_green"
            ]
        )
        self.assertFalse(
            transition["official_generated_qualification_execution_authorized_now"]
        )
        self.assertTrue(
            transition[
                "official_execution_requires_exact_implementation_remotely_green_and_separate_activation"
            ]
        )
        self.assertTrue(
            transition["DREYER_C5R_1_HL_remains_sole_active_Tier_C_packet"]
        )

    def test_only_proof_metadata_reads_are_nonzero(self) -> None:
        allowed = {
            "tracked_artifact_reads": 3,
            "Git_proof_reads": 3,
            "GitHub_CI_metadata_reads": 1,
            "GitHub_ref_reads": 2,
        }
        for key, value in self.proof["operation_counters"].items():
            self.assertEqual(value, allowed.get(key, 0), key)

    def test_storage_and_claim_boundaries_remain_closed(self) -> None:
        storage = self.proof["storage_boundary"]
        self.assertEqual(storage["raw_ceiling_bytes"], 10 * 1024**3)
        self.assertEqual(storage["total_research_storage_ceiling_bytes"], 20 * 1024**3)
        self.assertEqual(storage["new_generated_payload_bytes"], 0)
        self.assertEqual(storage["new_real_payload_bytes"], 0)
        self.assertEqual(storage["cleanup_operations"], 0)

        claims = self.proof["claim_boundary"]
        self.assertTrue(claims["engineering_registration_remotely_green"])
        self.assertTrue(claims["registration_proof_closeout_created"])
        for key, value in claims.items():
            if key not in {
                "engineering_registration_remotely_green",
                "registration_proof_closeout_created",
            }:
                self.assertFalse(value, key)

    def test_frontier_and_document_state_the_exact_boundary(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        registration = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["prospective_synchronized_cohort_preregistration"][
            "generated_qualification_registration"
        ]
        self.assertEqual(
            registration["green_registration_commit"],
            self.proof["green_registration_commit"]["commit"],
        )
        self.assertEqual(
            registration["status"],
            "registration_remotely_green_proof_only_closeout_pending_own_remote_CI",
        )
        closeout = registration["proof_only_closeout"]
        self.assertEqual(closeout["bound_artifacts"], 3)
        self.assertEqual(closeout["bound_bytes"], 47_492)
        self.assertFalse(closeout["official_qualification_execution_authorized_now"])

        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
