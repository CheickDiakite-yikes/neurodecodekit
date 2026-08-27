from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_r0_generated as experiment


ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_generated_postfailure_hardening.v0.json"
)
DOC = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_INDEPENDENT_REPLICATION_GENERATED_POSTFAILURE_HARDENING.md"
)


class CommR0GeneratedPostfailureHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_current_artifacts_match_additive_hardening_record(self) -> None:
        for artifact in self.record["changed_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["after_bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(),
                artifact["after_sha256"],
                artifact["path"],
            )

    def test_historical_execution_hash_is_preserved(self) -> None:
        source = self.record["changed_artifacts"][0]
        self.assertEqual(
            source["before_sha256"],
            "032dc10eccb35eebf02126cec0b7e2a539a294e737e448b83d5beca775e32aa8",
        )
        self.assertNotEqual(source["before_sha256"], source["after_sha256"])
        self.assertEqual(
            self.record["failure_binding"]["failure_proof_binding_commit"],
            "efef655907cda403ccc13da5399e824f2a5d2ff4",
        )
        self.assertTrue(
            self.record["failure_binding"]["both_required_failure_proof_jobs_green"]
        )

    def test_consumed_entrypoint_refuses_without_replay(self) -> None:
        with self.assertRaisesRegex(experiment.CommR0GeneratedRefusal, "R0G-CONSUMED"):
            experiment._assert_generated_qualification_not_consumed(ROOT)
        self.assertFalse(self.record["hardening"]["official_qualification_executed"])
        self.assertFalse(self.record["hardening"]["development_full_replay_executed"])

    def test_no_real_operation_or_claim_upgrade(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        claims = self.record["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_capability_added":
                self.assertFalse(value, key)
        self.assertEqual(self.record["active_gate"]["gate_id"], "DREYER-C5R-1-HL")
        self.assertTrue(self.record["active_gate"]["all_authority_flags_false"])

    def test_document_is_explicit_about_no_rerun_and_no_science(self) -> None:
        normalized = " ".join(DOC.read_text(encoding="utf-8").split())
        for phrase in (
            "does not rerun",
            "R0G-CONSUMED",
            "historical implementation record retains the exact hashes that ran",
            "No real or private path",
            "Scientific claim not established",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
