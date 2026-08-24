import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_recovery_request_proof.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_STAGE_G1_RECOVERY_REQUEST_PROOF_CLOSEOUT.md"


class BNCIStageG1RecoveryRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_green_request_and_repair_are_bound(self):
        green = self.proof["request_green_proof"]
        self.assertEqual(
            green["green_commit"],
            "b1f68e50823792ccedb5ef8962c584c1bb573f3a",
        )
        self.assertEqual(green["CI_run_id"], 32_759_468_410)
        self.assertEqual(green["base_python_job_id"], 97_534_565_977)
        self.assertEqual(green["optional_neuro_job_id"], 97_534_565_813)
        self.assertTrue(green["both_required_jobs_green"])

    def test_artifact_hashes_sizes_and_git_blobs_are_exact(self):
        rows = self.proof["artifacts"]
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["artifact_summary"]
        self.assertEqual(summary["count"], 7)
        self.assertEqual(summary["bytes"], sum(row["bytes"] for row in rows))
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_failed_CI_is_preserved_and_repair_changed_no_production(self):
        failed = self.proof["preceding_CI_failure"]
        self.assertEqual(failed["CI_run_id"], 32_758_324_335)
        self.assertTrue(failed["base_python_green"])
        self.assertFalse(failed["optional_neuro_green"])
        self.assertEqual(failed["failed_tests"], 2)
        verification = self.proof["verification"]
        self.assertEqual(verification["proof_closeout_full_base_tests"], 5_976)
        self.assertEqual(
            verification["proof_closeout_full_base_tests"]
            - verification["full_base_tests"],
            verification["recovery_proof_tests_added"],
        )
        self.assertEqual(verification["production_files_changed_by_CI_repair"], 0)
        self.assertFalse(verification["production_RSS_enforcement_changed"])
        self.assertTrue(verification["explicit_over_cap_refusal_test_added"])
        self.assertFalse(verification["replacement_G1_qualification_repeated"])

    def test_proof_changes_no_scope_and_grants_no_authority(self):
        self.assertTrue(all(self.proof["scope_unchanged"].values()))
        self.assertTrue(
            all(value is False for value in self.proof["current_authorization_flags"].values())
        )
        counters = self.proof["proof_operation_counters"]
        allowed_nonzero = {
            "proof_bound_tracked_artifact_reads": 7,
            "Git_proof_reads": 7,
            "public_GitHub_CI_read_invocations": 7,
        }
        self.assertEqual({key: counters[key] for key in allowed_nonzero}, allowed_nonzero)
        self.assertTrue(
            all(value == 0 for key, value in counters.items() if key not in allowed_nonzero)
        )

    def test_next_gate_requires_closeout_green_then_fresh_message(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["closeout_commit_push_and_both_CI_jobs_green_required"])
        self.assertFalse(
            gate["sole_active_Tier_C_packet_identification_allowed_before_closeout_green"]
        )
        self.assertTrue(gate["fresh_packet_bound_maintainer_message_required_after_identification"])
        self.assertFalse(gate["current_or_earlier_continue_is_retroactive"])
        self.assertFalse(gate["replacement_G1_or_any_later_stage_authorized_now"])

    def test_document_preserves_scientific_boundary(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Proof-only closeout", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("no real-data access", document)
        self.assertIn("No earlier message is", document)


if __name__ == "__main__":
    unittest.main()
