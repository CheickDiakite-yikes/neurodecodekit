from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_HARDENING_IMPLEMENTATION.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_qualification_hardening_implementation.v0.json"
)


class CommunicationEEGProspectiveGeneratedQualificationHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_artifact_hashes_are_exact(self) -> None:
        for artifact in self.record["artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_measurement_is_bounded_generated_and_replayed(self) -> None:
        measured = self.record["development_measurement"]
        self.assertEqual(measured["isolated_replays"], 2)
        self.assertTrue(measured["replay_equivalent"])
        self.assertEqual(measured["prediction_rows_per_replay"], 13056)
        self.assertEqual(measured["prediction_sets_per_replay"], 204)
        self.assertEqual(measured["refusal_observations"], 140)
        self.assertEqual(measured["target_deliveries"], 2)
        self.assertEqual(measured["scores"], 2)
        self.assertEqual(measured["post_target_updates"], 0)
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["real_or_private_reads"], 0)
        self.assertLess(measured["peak_process_tree_RSS_bytes"], 512 * 1024 * 1024)
        self.assertLess(
            measured["private_generated_output_bytes_maximum_replay"], 128 * 1024 * 1024
        )

    def test_remaining_blockers_are_explicit(self) -> None:
        measured = self.record["development_measurement"]
        self.assertTrue(measured["complete_prediction_records_materialized_for_scoring"])
        self.assertEqual(measured["numerical_shortcut_fixture_executions"], 0)
        self.assertEqual(len(self.record["remaining_activation_blockers"]), 4)
        self.assertTrue(self.record["capabilities"]["official_entry_activation_locked"])

    def test_authority_and_claims_remain_closed(self) -> None:
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        claims = self.record["claim_boundary"]
        self.assertTrue(claims["generated_hardening_capability_established"])
        for key, value in claims.items():
            if key != "generated_hardening_capability_established":
                self.assertFalse(value, key)
        self.assertTrue(self.record["active_gate"]["all_authority_flags_false"])

    def test_document_has_separate_engineering_and_scientific_sentences(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("official qualification remains inactive", document)


if __name__ == "__main__":
    unittest.main()
