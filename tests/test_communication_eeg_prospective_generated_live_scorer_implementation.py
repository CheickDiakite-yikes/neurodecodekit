from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_live_scorer_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_LIVE_SCORER_IMPLEMENTATION.md"


class CommunicationEEGProspectiveGeneratedLiveScorerImplementationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_implementation_and_artifacts(self) -> None:
        green = self.record["green_implementation"]
        self.assertEqual(
            green["commit"], "c46064d19bd0ec74bc960d155ad9752989d9c54c"
        )
        self.assertEqual(green["CI_run_id"], 33_141_715_948)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])
        for artifact in self.record["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifact["sha256"],
                artifact["path"],
            )

    def test_free_choice_is_primary_and_prompted_cannot_rescue(self) -> None:
        implemented = self.record["implemented_capabilities"]
        self.assertTrue(implemented["free_choice_is_primary_live_gate"])
        self.assertFalse(implemented["prompted_may_rescue_free_choice"])
        self.assertTrue(implemented["free_choice_and_prompted_scored_separately"])
        self.assertTrue(implemented["inactive_null_intervals_counted_once"])
        self.assertFalse(implemented["end_to_end_latency_measured"])

    def test_official_operation_and_claims_remain_closed(self) -> None:
        official = self.record["official_qualification"]
        self.assertFalse(official["executed"])
        self.assertFalse(official["authorized_now"])
        self.assertEqual(official["real_or_private_operations"], 0)
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_human_document_preserves_two_sentence_boundary(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("cannot rescue a failed free-choice", document)


if __name__ == "__main__":
    unittest.main()
