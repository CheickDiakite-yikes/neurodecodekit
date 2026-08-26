from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/bnci_2014_001_artifact_postmortem_result.v0.json"
DOC_PATH = ROOT / "docs/BNCI_2014_001_ARTIFACT_POSTMORTEM_RESULT.md"


class BNCIArtifactPostmortemResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_exact_result_identity_and_status(self) -> None:
        self.assertEqual(len(self.payload), 6_091)
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "b211f894658beb642cebc40e54dba9c33a9bd3cf7664b91a6170b086dfd96c8a",
        )
        self.assertEqual(
            self.result["status"], "completed_artifact_only_descriptive_postmortem"
        )
        self.assertEqual(
            self.result["proof_posture"],
            "post_outcome_descriptive_not_prospective_validation",
        )
        self.assertFalse(self.result["analysis"]["root_cause_established"])

    def test_failure_localization_is_exact(self) -> None:
        states = {
            row["id"]: row["state"] for row in self.result["analysis"]["diagnostics"]
        }
        self.assertEqual(states["D1"], "supported_descriptively")
        self.assertEqual(
            states["D2"], "failed_posterior_control_outperformed_selected_E"
        )
        self.assertEqual(
            states["D3"], "failed_selected_E_log_loss_worse_than_equal_prior"
        )
        self.assertEqual(states["D4"], "weak_directional_only_not_validated")
        self.assertEqual(states["D5"], "failed")
        self.assertEqual(states["D6"], "unavailable_from_aggregate_artifact")

    def test_run_stayed_aggregate_only_and_bounded(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(counters["committed_aggregate_JSON_reads"], 1)
        self.assertEqual(counters["committed_aggregate_bytes_read"], 4_951)
        for key in (
            "git_ignored_or_private_artifact_reads",
            "individual_prediction_probability_or_participant_outcome_reads",
            "raw_MAT_or_EEG_reads",
            "target_or_label_reads",
            "model_or_checkpoint_reads",
            "training_runs",
            "inference_runs",
            "scientific_reruns",
            "claim_upgrades",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertLessEqual(
            self.result["measurements"]["peak_process_RSS_bytes"], 256 * 1024 * 1024
        )
        self.assertLessEqual(self.result["measurements"]["public_output_bytes"], 1 << 20)

    def test_closeout_keeps_the_scientific_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Posterior EEG slightly outperformed", text)
        self.assertIn("These are design signals, not positive scientific endpoints.", text)
        self.assertIn("Scientific claim not established", text)
        self.assertNotIn("root cause established", text.lower())


if __name__ == "__main__":
    unittest.main()
