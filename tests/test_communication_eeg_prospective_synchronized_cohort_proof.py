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
    / "communication_eeg_prospective_synchronized_cohort_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_SYNCHRONIZED_COHORT_PROOF_CLOSEOUT.md"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommunicationEEGProspectiveSynchronizedCohortProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_registration_commit_is_remotely_green_and_on_main(self) -> None:
        green = self.proof["green_registration_commit"]
        self.assertEqual(
            green["commit"], "df3266ed09132017cc8a9dcc10e8a7d61ea92f61"
        )
        self.assertEqual(green["CI_run_id"], 33_134_791_405)
        self.assertEqual(green["base_python_job_id"], 98_732_241_444)
        self.assertEqual(green["optional_neuro_readers_job_id"], 98_732_241_603)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["working_branch_matches_exact_commit"])
        self.assertTrue(green["GitHub_main_matches_exact_commit"])

    def test_registration_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_registration_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_registration_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 38_364)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_preserves_scope_and_delays_generated_execution(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["registration_artifacts_unchanged"])
        self.assertTrue(scope["target_firewall_and_control_matrix_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["active_Tier_C_gate_changed"])
        self.assertFalse(scope["claim_boundary_changed"])

        transition = self.proof["transition"]
        self.assertTrue(
            transition[
                "generated_qualification_design_may_begin_after_closeout_and_amendment_remote_green"
            ]
        )
        self.assertTrue(
            transition[
                "amendment_1_required_to_resolve_stable_commit_coverage_mismatch"
            ]
        )
        self.assertFalse(transition["generated_implementation_authorized_now"])
        self.assertFalse(
            transition["generated_qualification_execution_authorized_now"]
        )
        self.assertTrue(transition["fresh_ordered_proof_barriers_required"])
        self.assertTrue(
            transition["DREYER_C5R_1_HL_remains_sole_active_Tier_C_packet"]
        )

    def test_only_proof_metadata_reads_are_nonzero(self) -> None:
        allowed = {
            "tracked_artifact_reads": 3,
            "Git_proof_reads": 3,
            "GitHub_CI_metadata_reads": 1,
            "GitHub_ref_reads": 1,
        }
        for key, value in self.proof["operation_counters"].items():
            self.assertEqual(value, allowed.get(key, 0), key)

    def test_storage_and_claim_boundaries_remain_closed(self) -> None:
        storage = self.proof["storage_boundary"]
        self.assertEqual(storage["raw_ceiling_bytes"], 10 * 1024**3)
        self.assertEqual(storage["total_research_storage_ceiling_bytes"], 20 * 1024**3)
        self.assertEqual(storage["new_payload_bytes"], 0)
        self.assertEqual(storage["cleanup_operations"], 0)

        claims = self.proof["claim_boundary"]
        self.assertTrue(claims["engineering_registration_remotely_green"])
        for key, value in claims.items():
            if key != "engineering_registration_remotely_green":
                self.assertFalse(value, key)

    def test_frontier_and_document_state_the_exact_boundary(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        registration = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["prospective_synchronized_cohort_preregistration"]
        proof = registration["proof_only_closeout"]
        self.assertEqual(
            registration["green_registration_commit"],
            self.proof["green_registration_commit"]["commit"],
        )
        self.assertEqual(
            registration["status"],
            "registration_remotely_green_proof_and_amendment_pending_own_remote_CI",
        )
        self.assertEqual(registration["amendment_1"]["authoritative_value"], 0.70)
        self.assertTrue(registration["amendment_1"]["generated_implementation_paused"])
        self.assertEqual(proof["status"], "pending_own_remote_CI")
        self.assertFalse(proof["generated_execution_authorized_now"])

        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)


if __name__ == "__main__":
    unittest.main()
