from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/fresh_motor_source_discovery_implementation_proof.v0.json"
)
DOCUMENT = (
    ROOT / "docs/FRESH_MOTOR_SOURCE_DISCOVERY_IMPLEMENTATION_PROOF_CLOSEOUT.md"
)


class FreshMotorSourceDiscoveryImplementationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_implementation_is_remotely_green(self) -> None:
        green = self.proof["green_implementation_commit"]
        self.assertEqual(
            green["commit"], "e92e9c21a044b05a187a04812f21e7e7bd5a76b6"
        )
        self.assertEqual(green["CI_run_id"], 33_337_741_165)
        self.assertEqual(green["base_python_job_id"], 99_327_605_264)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_327_605_346)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_six_exact_artifacts_are_hash_size_blob_and_set_bound(self) -> None:
        rows = self.proof["bound_implementation_and_result_artifacts"]
        canonical_lines: list[str] = []
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob_payload = f"blob {len(payload)}\0".encode() + payload
            blob = hashlib.sha1(blob_payload, usedforsecurity=False).hexdigest()
            self.assertEqual(blob, row["git_blob"], row["path"])
            canonical_lines.append(
                f'{row["path"]}|{row["bytes"]}|{row["sha256"]}|{row["git_blob"]}\n'
            )
        canonical = "".join(sorted(canonical_lines)).encode()
        summary = self.proof["bound_artifact_summary"]
        self.assertEqual(summary["count"], 6)
        self.assertEqual(summary["bytes"], 162_295)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_repeats_no_measured_run_or_protected_operation(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertFalse(scope["measured_generated_qualification_rerun"])
        self.assertFalse(scope["authority_expanded"])
        counters = self.proof["operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 6)
        self.assertEqual(counters["Git_proof_reads"], 6)
        for key, value in counters.items():
            if key not in {"tracked_artifact_reads", "Git_proof_reads"}:
                self.assertEqual(value, 0, key)

    def test_packet_stays_parked_and_claims_stay_false(self) -> None:
        defects = self.proof["unresolved_packet_defects"]
        self.assertFalse(defects["exact_official_index_revisions_packet_bound"])
        self.assertFalse(
            defects["externally_authenticated_remote_CI_attestation_implemented"]
        )
        self.assertFalse(defects["real_transport_capability_present"])
        self.assertFalse(defects["live_execution_armable"])
        self.assertTrue(defects["execute_refuses_before_DNS_or_HTTP"])
        transition = self.proof["transition"]
        self.assertFalse(transition["public_source_discovery_network_research_authorized"])
        self.assertFalse(transition["real_payload_or_header_operation_authorized"])
        self.assertIsNone(transition["active_Tier_C_packet_after_closeout"])
        boundary = self.proof["claim_boundary"]
        for key, value in boundary.items():
            if key != "engineering_proof_added":
                self.assertFalse(value, key)

    def test_document_separates_capability_nonclaim_and_next_gate(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("additive all-false correction", document)
        self.assertIn("does not expand the current packet", document)


if __name__ == "__main__":
    unittest.main()
