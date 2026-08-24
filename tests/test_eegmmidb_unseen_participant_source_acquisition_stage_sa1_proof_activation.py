import hashlib
import json
import subprocess
import unittest
from pathlib import Path

from neurodecodekit.datasets import eegmmidb_unseen_participant_source_acquisition as source

ROOT = Path(__file__).resolve().parents[1]
ACTIVATION = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_proof_activation.v0.json"
)
PROOF = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_stage_sa1_proof_closeout.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_STAGE_SA1_PROOF_ACTIVATION.md"
)


class EEGMMIDBUnseenParticipantSourceAcquisitionStageSA1ProofActivationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_proof_closeout_was_green_before_activation(self):
        green = self.activation["green_proof_closeout_commit"]
        self.assertEqual(green["commit"], "b3902cf50bef478055255570d1b78813207fb8d1")
        self.assertEqual(green["CI_run_id"], 32735141922)
        self.assertEqual(green["base_python_job_id"], 97456050452)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97456050604)
        self.assertTrue(green["both_required_jobs_green"])

    def test_three_preactivation_artifacts_are_bound_from_green_revision(self):
        rows = self.activation["preactivation_artifacts"]
        revision = rows[0]["git_revision"]
        revision_available = subprocess.run(
            ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
        ).returncode == 0
        if revision_available:
            for row in rows:
                payload = subprocess.check_output(
                    ["git", "show", f"{row['git_revision']}:{row['path']}"], cwd=ROOT
                )
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
                blob = subprocess.check_output(
                    ["git", "rev-parse", f"{row['git_revision']}:{row['path']}"],
                    cwd=ROOT,
                    text=True,
                ).strip()
                self.assertEqual(blob, row["git_blob"])
        else:
            shallow = subprocess.check_output(
                ["git", "rev-parse", "--is-shallow-repository"],
                cwd=ROOT,
                text=True,
            ).strip()
            self.assertEqual(shallow, "true")
            self.assertTrue(all(row["git_revision"] == revision for row in rows))
            self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))
            self.assertTrue(all(len(row["git_blob"]) == 40 for row in rows))
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.activation["preactivation_artifact_summary"]
        self.assertEqual(summary["count"], 3)
        self.assertEqual(summary["bytes"], 16883)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_proof_registry_contains_exact_green_fields(self):
        activated = self.activation["activated_proof_registry"]
        payload = PROOF.read_bytes()
        self.assertEqual(len(payload), activated["bytes"])
        self.assertEqual(hashlib.sha256(payload).hexdigest(), activated["sha256"])
        self.assertTrue(self.proof["both_required_stages_remotely_green"])
        closeout = self.proof["green_proof_closeout"]
        self.assertEqual(closeout["commit"], "b3902cf50bef478055255570d1b78813207fb8d1")
        self.assertEqual(closeout["CI_run_id"], 32735141922)
        self.assertEqual(closeout["base_python_job_id"], 97456050452)
        self.assertEqual(closeout["optional_neuro_job_id"], 97456050604)
        self.assertTrue(closeout["both_required_jobs_green"])

    def test_future_evidence_exactly_matches_frozen_executor_fields(self):
        evidence = self.activation["future_exact_evidence"]
        activated = self.activation["activated_proof_registry"]
        self.assertEqual(evidence["proof_closeout_registry_sha256"], activated["sha256"])
        self.assertEqual(
            evidence["implementation_commit"],
            self.proof["green_implementation"]["commit"],
        )
        self.assertEqual(
            evidence["implementation_CI_run_id"],
            self.proof["green_implementation"]["CI_run_id"],
        )
        self.assertEqual(
            evidence["proof_closeout_commit"], self.proof["green_proof_closeout"]["commit"]
        )
        self.assertEqual(
            evidence["proof_closeout_CI_run_id"],
            self.proof["green_proof_closeout"]["CI_run_id"],
        )

    def test_frozen_proof_reader_accepts_exact_activation_without_live_opener(self):
        evidence = self.activation["future_exact_evidence"]
        source._read_green_sa1_proof(
            ROOT,
            source.SA1ProofEvidence(
                implementation_commit=evidence["implementation_commit"],
                implementation_ci_run_id=evidence["implementation_CI_run_id"],
                implementation_base_job_id=evidence["implementation_base_job_id"],
                implementation_optional_job_id=evidence[
                    "implementation_optional_job_id"
                ],
                proof_closeout_commit=evidence["proof_closeout_commit"],
                proof_closeout_ci_run_id=evidence["proof_closeout_CI_run_id"],
                proof_closeout_base_job_id=evidence["proof_closeout_base_job_id"],
                proof_closeout_optional_job_id=evidence[
                    "proof_closeout_optional_job_id"
                ],
                proof_closeout_registry_sha256=evidence[
                    "proof_closeout_registry_sha256"
                ],
            ),
        )

    def test_activation_performs_no_real_or_scientific_operation(self):
        counters = self.activation["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 3)
        self.assertEqual(counters["Git_proof_reads"], 3)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )
        transition = self.activation["transition"]
        self.assertFalse(transition["effective_before_this_activation_commit_remote_green"])
        self.assertTrue(
            transition[
                "activation_commit_push_and_both_CI_jobs_green_required_before_stage_SA2"
            ]
        )
        self.assertFalse(transition["stage_SA2_authorized_now"])
        self.assertFalse(transition["network_or_payload_access_performed_by_activation"])

    def test_human_activation_separates_engineering_and_science(self):
        boundary = self.activation["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no live\nopener may be constructed", document)


if __name__ == "__main__":
    unittest.main()
