from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT
    / "docs"
    / "COMMUNICATION_EEG_PROSPECTIVE_GENERATED_MODEL_WORKER_IMPLEMENTATION.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "communication_eeg_prospective_generated_model_worker_implementation.v0.json"
)


class CommunicationEEGProspectiveGeneratedModelWorkerImplementationTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_bound_artifact_hashes_are_exact(self) -> None:
        for artifact in self.record["artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_model_capability_excludes_held_out_targets_and_scorer(self) -> None:
        capability = self.record["capability"]
        self.assertEqual(len(capability["preopened_descriptors"]), 4)
        self.assertTrue(capability["opaque_item_identifiers_required_from_coordinator"])
        for key, value in capability.items():
            if key not in {
                "preopened_descriptors",
                "opaque_item_identifiers_required_from_coordinator",
            }:
                self.assertEqual(value, 0, key)

    def test_fixed_fold_schedule_has_no_delivery_score_or_update(self) -> None:
        schedule = self.record["per_fold_schedule"]
        self.assertEqual(schedule["compact_classifier_fits"], 15)
        self.assertEqual(schedule["source_only_temperature_fits"], 15)
        self.assertEqual(schedule["endpoint_separated_prediction_sets"], 34)
        self.assertEqual(schedule["prediction_rows"], 2176)
        self.assertEqual(schedule["target_deliveries"], 0)
        self.assertEqual(schedule["scores"], 0)
        self.assertEqual(schedule["post_target_updates"], 0)

    def test_remaining_controls_and_claims_are_honest(self) -> None:
        controls = self.record["remaining_coordinator_controls"]
        self.assertTrue(all(controls.values()))
        self.assertTrue(
            all(value == 0 for value in self.record["operation_counters"].values())
        )
        claims = self.record["claim_boundary"]
        self.assertTrue(claims["capability_poor_generated_model_worker_implemented"])
        for key, value in claims.items():
            if key != "capability_poor_generated_model_worker_implemented":
                self.assertFalse(value, key)
        self.assertTrue(self.record["active_gate"]["all_authority_flags_false"])

    def test_document_states_engineering_and_scientific_boundaries(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("official qualification remains inactive", document)


if __name__ == "__main__":
    unittest.main()
