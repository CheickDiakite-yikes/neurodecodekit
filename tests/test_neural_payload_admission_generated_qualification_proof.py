from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/neural_payload_admission_generated_qualification_proof.v0.json"
)
DOCUMENT = (
    ROOT / "docs/NEURAL_PAYLOAD_ADMISSION_GENERATED_QUALIFICATION_PROOF_CLOSEOUT.md"
)


class NeuralPayloadAdmissionGeneratedQualificationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_successor_is_remotely_green(self) -> None:
        green = self.proof["green_implementation_commit"]
        self.assertEqual(
            green["commit"], "2e164fffb00e5db79a6c6d810eabbcc2d447c5a1"
        )
        self.assertEqual(green["CI_run_id"], 33_284_320_443)
        self.assertEqual(green["base_python_job_id"], 99_184_746_988)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_184_747_065)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])
        self.assertFalse(self.proof["superseded_remote_failure"]["accepted_as_proof"])

    def test_exact_artifacts_are_hash_size_and_git_bound(self) -> None:
        rows = self.proof["bound_implementation_and_result_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.proof["bound_artifact_summary"]
        self.assertEqual(summary["count"], 6)
        self.assertEqual(summary["bytes"], 89_732)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_repeats_no_qualification_or_protected_operation(self) -> None:
        self.assertFalse(self.proof["scope_preservation"]["generated_qualification_rerun"])
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 6)
        self.assertEqual(counters["Git_proof_reads"], 6)
        for key, value in counters.items():
            if key not in {"tracked_artifact_reads", "Git_proof_reads"}:
                self.assertEqual(value, 0, key)

    def test_closeout_opens_no_real_authority_or_claim(self) -> None:
        transition = self.proof["transition"]
        self.assertFalse(transition["source_specific_metadata_network_research_authorized"])
        self.assertFalse(transition["real_transport_canary_authorized"])
        self.assertFalse(transition["real_payload_or_header_operation_authorized"])
        self.assertIsNone(transition["active_Tier_C_packet_after_closeout"])
        boundary = self.proof["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established"])
        self.assertFalse(boundary["real_EEG_accessed"])

    def test_document_states_capability_nonclaim_and_next_gate(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("all-false fresh-source research", document)


if __name__ == "__main__":
    unittest.main()
