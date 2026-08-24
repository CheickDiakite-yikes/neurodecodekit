import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_request_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_REQUEST_PROOF_CLOSEOUT.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionRequestProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_request_commit_is_remotely_green(self):
        green = self.proof["green_request_commit"]
        self.assertEqual(
            green["commit"], "2085ea061d936bb18ef08e93fb7d3f874ef0f9d8"
        )
        self.assertEqual(green["CI_run_id"], 32722744301)
        self.assertEqual(green["base_python_job_id"], 97417435948)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97417435670)
        self.assertTrue(green["both_required_jobs_green"])

    def test_request_artifacts_are_hash_size_and_git_bound(self):
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
        self.assertEqual(summary["bytes"], 33704)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_scope_is_unchanged_and_authority_is_not_expanded(self):
        scope = self.proof["scope_preservation"]
        self.assertTrue(scope["request_artifacts_unchanged"])
        self.assertTrue(
            scope["source_participants_runs_paths_sizes_order_and_total_unchanged"]
        )
        self.assertTrue(scope["retained_source_and_fresh_final_firewalls_unchanged"])
        self.assertTrue(scope["generated_first_and_remote_green_barriers_unchanged"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["claim_boundary_changed"])

    def test_only_tracked_and_git_proof_reads_occurred(self):
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

    def test_next_gate_does_not_authorize_implementation_or_acquisition(self):
        transition = self.proof["transition"]
        self.assertTrue(
            transition["may_identify_as_sole_active_Tier_C_packet_after_remote_green"]
        )
        self.assertFalse(transition["implementation_authorized_by_closeout"])
        self.assertFalse(transition["generated_qualification_authorized_by_closeout"])
        self.assertFalse(transition["network_or_real_acquisition_authorized_by_closeout"])
        self.assertTrue(transition["fresh_packet_bound_maintainer_words_required"])
        self.assertTrue(
            transition[
                "authorization_decision_must_be_remotely_green_before_stage_SA1"
            ]
        )

    def test_claim_and_next_gate_language_are_explicit(self):
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("sole active Tier C packet", document)
        self.assertIn("six proposed source payloads remain inaccessible", document)


if __name__ == "__main__":
    unittest.main()
