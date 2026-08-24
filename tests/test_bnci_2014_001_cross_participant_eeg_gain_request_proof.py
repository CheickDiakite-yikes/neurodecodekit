import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_request_proof.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_REQUEST_PROOF_CLOSEOUT.md"


class BNCI2014001CrossParticipantEEGGainRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_green_request_is_bound(self):
        green = self.proof["request_green_proof"]
        self.assertEqual(green["commit"], "3197390d45bfc8d19c9df2f3675166815f56f028")
        self.assertEqual(green["CI_run_id"], 32_749_812_954)
        self.assertEqual(green["base_python_job_id"], 97_503_845_918)
        self.assertEqual(green["optional_neuro_job_id"], 97_503_846_151)
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
        self.assertEqual(summary["count"], 9)
        self.assertEqual(summary["bytes"], sum(row["bytes"] for row in rows))
        self.assertEqual(
            summary["canonical_artifact_set_sha256"],
            hashlib.sha256(canonical).hexdigest(),
        )

    def test_verification_delta_and_remote_proof_are_explicit(self):
        verification = self.proof["verification"]
        self.assertEqual(verification["focused_BNCI_tests"], 28)
        self.assertEqual(verification["full_dependency_light_tests"], 5_948)
        self.assertEqual(verification["expected_skips"], 212)
        self.assertEqual(
            verification["full_dependency_light_tests"]
            - verification["pre_change_dependency_light_tests"],
            verification["new_tests"],
        )
        self.assertTrue(verification["remote_base_python_green"])
        self.assertTrue(verification["remote_optional_neuro_green"])
        self.assertFalse(verification["local_dependency_rich_full_suite_is_authoritative"])
        self.assertEqual(verification["runtime_source_files_changed_by_request"], 0)

    def test_proof_changes_no_scope_and_grants_no_authority(self):
        self.assertTrue(all(self.proof["scope_unchanged"].values()))
        self.assertTrue(
            all(value is False for value in self.proof["current_authorization_flags"].values())
        )
        counters = self.proof["proof_operation_counters"]
        allowed_nonzero = {
            "tracked_artifact_reads": 9,
            "Git_proof_reads": 9,
            "public_GitHub_run_list_invocations": 1,
            "public_GitHub_CI_watch_invocations": 1,
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
        self.assertFalse(gate["any_generated_network_real_or_scientific_stage_authorized_now"])

    def test_document_preserves_scientific_boundary(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Proof-only closeout", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("no real-data access", document)
        self.assertIn("No earlier message is", document)


if __name__ == "__main__":
    unittest.main()
