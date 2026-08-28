from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_QUALIFICATION_HARDENING_IMPLEMENTATION_V1.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_qualification_hardening_implementation.v1.json"
)
REHEARSAL_REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_full_scale_rehearsal_result.v0.json"
)


class CommunicationEEGProspectiveGeneratedQualificationHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.rehearsal = json.loads(REHEARSAL_REGISTRY.read_text(encoding="utf-8"))

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
        self.assertEqual(measured["maximum_prediction_rows_buffered"], 1)
        self.assertFalse(measured["complete_prediction_records_materialized"])
        self.assertEqual(measured["numerical_shortcut_fixture_executions_per_replay"], 7)
        self.assertEqual(measured["shortcut_prediction_rows_per_replay"], 91392)
        self.assertEqual(measured["refusal_observations"], 140)
        self.assertEqual(measured["main_target_deliveries"], 2)
        self.assertEqual(measured["main_scores"], 2)
        self.assertEqual(measured["shortcut_target_deliveries_per_replay"], 14)
        self.assertEqual(measured["shortcut_scores_per_replay"], 14)
        self.assertEqual(measured["post_target_updates"], 0)
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["real_or_private_reads"], 0)
        self.assertLess(measured["peak_process_tree_RSS_bytes"], 512 * 1024 * 1024)
        self.assertLess(
            measured["private_generated_output_bytes_maximum_replay"], 128 * 1024 * 1024
        )

    def test_full_scale_rehearsal_is_bounded_and_nonofficial(self) -> None:
        rehearsal = self.rehearsal
        self.assertFalse(rehearsal["official_qualification"])
        self.assertEqual(rehearsal["participants_per_cohort"], 21)
        self.assertEqual(rehearsal["cohorts"], 2)
        self.assertEqual(rehearsal["prediction_rows"], 91392)
        self.assertEqual(rehearsal["prediction_sets"], 1428)
        self.assertEqual(rehearsal["maximum_prediction_rows_buffered"], 1)
        self.assertFalse(rehearsal["complete_prediction_records_materialized"])
        self.assertEqual(rehearsal["numerical_shortcut_fixture_executions"], 7)
        self.assertEqual(rehearsal["post_target_updates"], 0)
        self.assertEqual(rehearsal["network_bytes"], 0)
        self.assertEqual(rehearsal["real_or_private_reads"], 0)
        self.assertEqual(rehearsal["retained_generated_payload_bytes"], 0)
        self.assertLess(rehearsal["peak_process_tree_RSS_bytes"], 512 * 1024 * 1024)
        self.assertLess(rehearsal["private_generated_output_bytes"], 128 * 1024 * 1024)

    def test_remaining_blocker_is_explicit(self) -> None:
        measured = self.record["development_measurement"]
        self.assertFalse(measured["complete_prediction_records_materialized"])
        self.assertEqual(measured["numerical_shortcut_fixture_executions_per_replay"], 7)
        self.assertEqual(len(self.record["remaining_activation_blockers"]), 1)
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
