from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_live_implementation_proof.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/FRESH_MOTOR_SOURCE_IDENTITY_WITNESS_LIVE_IMPLEMENTATION_PROOF_CLOSEOUT.md"
)


def git_blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload, usedforsecurity=False).hexdigest()


class FreshMotorSourceIdentityWitnessLiveImplementationProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_implementation_is_remotely_green(self) -> None:
        green = self.proof["green_implementation_commit"]
        self.assertEqual(
            green["commit"], "a2af6c4c016a81652b3c1bae13d8c8e5e56ef4e9"
        )
        self.assertEqual(green["CI_run_id"], 33_400_484_765)
        self.assertEqual(green["base_python_job_id"], 99_515_316_155)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_515_315_921)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_transitive_ledger_binds_all_sixteen_exact_artifacts(self) -> None:
        ledger_identity = self.proof["bound_artifact_ledger"]
        ledger_path = ROOT / ledger_identity["path"]
        ledger_payload = ledger_path.read_bytes()
        self.assertEqual(len(ledger_payload), ledger_identity["bytes"])
        self.assertEqual(hashlib.sha256(ledger_payload).hexdigest(), ledger_identity["sha256"])
        self.assertEqual(git_blob(ledger_payload), ledger_identity["git_blob"])

        ledger = json.loads(ledger_payload)
        rows = [*ledger["implementation_artifacts"], ledger_identity]
        self.assertEqual(len(ledger["implementation_artifacts"]), 15)
        self.assertEqual(
            sum(row["bytes"] for row in ledger["implementation_artifacts"]),
            ledger_identity["bound_entry_bytes"],
        )
        canonical_lines: list[str] = []
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(git_blob(payload), row["git_blob"])
            canonical_lines.append(
                f'{row["path"]}|{row["bytes"]}|{row["sha256"]}|{row["git_blob"]}\n'
            )

        summary = self.proof["bound_artifact_summary"]
        self.assertEqual(summary["count_including_ledger"], 16)
        self.assertEqual(summary["bytes_including_ledger"], 314_356)
        canonical = "".join(sorted(canonical_lines)).encode("ascii")
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_closeout_repeats_no_protected_operation(self) -> None:
        scope = self.proof["scope_preservation"]
        self.assertFalse(scope["generated_qualification_rerun"])
        self.assertFalse(scope["live_witness_invoked"])
        self.assertFalse(scope["authority_expanded"])
        self.assertFalse(scope["unrelated_local_changes_touched"])
        self.assertTrue(
            all(value == 0 for value in self.proof["protected_operation_counters"].values())
        )

    def test_transition_and_claims_remain_closed(self) -> None:
        transition = self.proof["transition"]
        self.assertFalse(transition["fresh_execution_bound_maintainer_words_present"])
        self.assertFalse(transition["execution_decision_created_now"])
        self.assertFalse(transition["live_witness_authorized_now"])
        self.assertFalse(transition["official_index_network_authorized_now"])
        claims = self.proof["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_proof_added":
                self.assertFalse(value, key)

    def test_document_separates_capability_nonclaim_and_next_gate(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("fresh maintainer words", document)
        self.assertIn("does not rerun qualification", document)


if __name__ == "__main__":
    unittest.main()
