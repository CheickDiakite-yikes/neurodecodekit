from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/communication_eeg_prospective_generated_numerical_scorer_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/COMMUNICATION_EEG_PROSPECTIVE_GENERATED_NUMERICAL_SCORER_IMPLEMENTATION.md"


class CommunicationEEGProspectiveGeneratedNumericalScorerImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_green_core_barrier_and_exact_artifacts(self) -> None:
        barrier = self.record["green_core_barrier"]
        self.assertEqual(barrier["commit"], "9378421afb0656df188fc63ca28b6009535200bd")
        self.assertEqual(barrier["CI_run_id"], 33_139_382_019)
        self.assertTrue(barrier["both_required_jobs_green"])
        for artifact in self.record["artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"], artifact["path"])
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                artifact["sha256"],
                artifact["path"],
            )

    def test_exact_schedule_and_scorer_separation_are_bound(self) -> None:
        implemented = self.record["implemented_capabilities"]
        self.assertEqual(implemented["cohort_local_participant_held_out_folds"], 42)
        self.assertEqual(implemented["endpoint_specific_residualizer_fits_per_replay"], 84)
        self.assertEqual(implemented["multinomial_L2_classifier_fits_per_replay"], 630)
        self.assertEqual(implemented["scalar_temperature_fits_per_replay"], 630)
        self.assertEqual(implemented["prediction_sets_per_replay"], 1_428)
        self.assertEqual(implemented["prediction_rows_per_replay"], 91_392)
        self.assertTrue(implemented["aggregate_only_post_freeze_scorer"])
        self.assertTrue(implemented["discovery_hidden_output_only"])
        self.assertTrue(implemented["replication_shadow_live_separation"])

    def test_official_execution_and_claims_remain_closed(self) -> None:
        official = self.record["official_qualification"]
        self.assertFalse(official["executed"])
        self.assertFalse(official["authorized_now"])
        self.assertEqual(official["target_deliveries"], 0)
        self.assertEqual(official["scores"], 0)
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_document_names_remaining_process_barrier(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("The official coordinator is still absent", document)
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertTrue(all(self.record["pending_full_implementation"].values()))


if __name__ == "__main__":
    unittest.main()
