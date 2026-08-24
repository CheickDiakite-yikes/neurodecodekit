import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_proof_closeout.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_STAGE_SA1_PROOF_CLOSEOUT.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionStageSA1ProofCloseoutTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_implementation_and_result_were_remotely_green(self):
        implementation = self.proof["green_implementation"]
        self.assertEqual(
            implementation["commit"],
            "37808bef8c59bc862345f342fd932aa04373b3fd",
        )
        self.assertEqual(implementation["CI_run_id"], 32730673153)
        self.assertEqual(implementation["base_python_job_id"], 97441967842)
        self.assertEqual(implementation["optional_neuro_job_id"], 97441968304)
        self.assertTrue(implementation["both_required_jobs_green"])

        result = self.proof["green_result_commit"]
        self.assertEqual(result["commit"], "e2965cfc90ac73a0371689333d0bad67de2634fd")
        self.assertEqual(result["CI_run_id"], 32733249548)
        self.assertEqual(result["base_python_job_id"], 97450079515)
        self.assertEqual(result["optional_neuro_readers_job_id"], 97450079739)
        self.assertTrue(result["both_required_jobs_green"])

    def test_nine_artifacts_are_byte_hash_and_git_bound(self):
        rows = self.proof["bound_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["artifact_summary"]
        self.assertEqual(summary["count"], 9)
        self.assertEqual(summary["bytes"], 130558)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_counter_discrepancy_is_bound_without_normalization_or_rerun(self):
        counter = self.proof["counter_discrepancy_binding"]
        self.assertEqual(counter["raw_top_level_mock_requests"], 56)
        self.assertEqual(counter["raw_nested_mock_checksum_requests"], 0)
        self.assertEqual(counter["raw_nested_mock_EDF_requests"], 0)
        self.assertEqual(counter["deterministically_recovered_mock_checksum_requests"], 21)
        self.assertEqual(counter["deterministically_recovered_mock_EDF_requests"], 35)
        self.assertEqual(counter["recovered_total"], 56)
        self.assertTrue(counter["discrepancy_is_non_scientific"])
        self.assertFalse(counter["execution_ambiguity_created"])
        self.assertFalse(counter["qualified_implementation_modified"])
        self.assertFalse(counter["qualification_repeated"])

    def test_closeout_repeats_no_qualification_or_real_operation(self):
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 9)
        self.assertEqual(counters["Git_proof_reads"], 9)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )
        scope = self.proof["scope_preservation"]
        self.assertFalse(scope["qualification_repeated"])
        self.assertFalse(scope["result_reconstructed_amended_or_replaced"])
        self.assertFalse(scope["counter_discrepancy_hidden_or_normalized"])
        self.assertFalse(scope["authority_expanded"])

    def test_transition_is_fail_closed_before_and_after_proof_activation(self):
        closeout = self.proof["green_proof_closeout"]
        activated = self.proof["both_required_stages_remotely_green"]
        if closeout is None:
            self.assertFalse(activated)
        else:
            self.assertTrue(activated)
            self.assertEqual(
                set(closeout),
                {
                    "commit",
                    "CI_run_id",
                    "base_python_job_id",
                    "optional_neuro_job_id",
                    "both_required_jobs_green",
                },
            )
            self.assertTrue(closeout["both_required_jobs_green"])
            for key in (
                "commit",
                "CI_run_id",
                "base_python_job_id",
                "optional_neuro_job_id",
            ):
                self.assertTrue(closeout[key])

        transition = self.proof["transition"]
        self.assertFalse(transition["effective_before_this_closeout_commit_remote_green"])
        self.assertTrue(
            transition[
                "stage_SA2_eligible_after_exact_closeout_remote_green_under_existing_decision"
            ]
        )
        self.assertFalse(transition["stage_SA2_armed_by_this_pre_green_record"])
        self.assertTrue(transition["separate_green_proof_activation_required_before_live_opener"])
        self.assertFalse(transition["stage_SA2_authorized_now"])

    def test_human_closeout_separates_engineering_and_science(self):
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("separate exact\ngreen proof-activation record", document)


if __name__ == "__main__":
    unittest.main()
