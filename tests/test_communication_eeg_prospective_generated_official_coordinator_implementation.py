from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated_qualification as qualification


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_OFFICIAL_COORDINATOR_IMPLEMENTATION.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_official_coordinator_implementation.v0.json"
)


class CommunicationEEGProspectiveGeneratedOfficialCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_bound_artifacts_are_exact(self) -> None:
        for artifact in self.record["artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(len(payload), artifact["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_official_contract_counts_are_explicit(self) -> None:
        counts = self.record["official_schedule_per_replay"]
        self.assertEqual(counts["fictional_complete_participants"], 42)
        self.assertEqual(counts["prediction_rows"], 91_392)
        self.assertEqual(counts["prediction_sets"], 1_428)
        self.assertEqual(counts["cohort_target_deliveries"], 2)
        self.assertEqual(counts["cohort_scores"], 2)
        self.assertEqual(counts["post_target_updates"], 0)

    def test_activation_and_official_execution_remain_closed(self) -> None:
        self.assertFalse(qualification.OFFICIAL_IMPLEMENTATION_ACTIVATED)
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        self.assertFalse(self.record["official_qualification"]["activated"])
        self.assertFalse(self.record["official_qualification"]["executed"])
        self.assertFalse(self.record["official_qualification"]["consumed"])
        self.assertGreaterEqual(len(self.record["remaining_barriers"]), 3)

    def test_claims_remain_closed(self) -> None:
        claims = self.record["claim_boundary"]
        self.assertTrue(claims["generated_official_coordinator_implemented"])
        for key, value in claims.items():
            if key != "generated_official_coordinator_implemented":
                self.assertFalse(value, key)

    def test_document_discloses_historical_mismatch_and_science_boundary(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("one combined target", document)
        self.assertIn("reported one delivery and one score", document)
        self.assertIn("two deliveries and two scores in each replay", document)
        self.assertIn("prior single-replay rehearsal", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
