import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/eegmmidb_unseen_participant_generalization_research.v0.json"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_GENERALIZATION_RESEARCH.md"


class EEGMMIDBUnseenParticipantGeneralizationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_research_is_operation_free(self):
        self.assertEqual(self.record["status"], "tier_A_research_complete_no_real_operation")
        self.assertTrue(all(value == 0 for value in self.record["operation_counters"].values()))

    def test_participants_are_disjoint_and_inference_is_by_person(self):
        cohorts = self.record["cohorts"]
        self.assertEqual(cohorts["source_participants"], [f"S{i:03d}" for i in range(1, 16)])
        self.assertEqual(cohorts["fresh_participants"], [f"S{i:03d}" for i in range(16, 31)])
        self.assertFalse(set(cohorts["source_participants"]) & set(cohorts["fresh_participants"]))
        self.assertEqual(cohorts["inference_unit"], "participant")

    def test_freshness_firewall_allows_zero_calibration(self):
        firewall = self.record["freshness_firewall"]
        self.assertFalse(firewall["source_final_runs_11_12_allowed_for_fit"])
        self.assertFalse(firewall["fresh_signal_before_checkpoint_freeze_allowed"])
        self.assertFalse(firewall["fresh_target_before_prediction_freeze_allowed"])
        for key in (
            "fresh_participant_calibration_rows",
            "fresh_participant_normalization_fit_rows",
            "fresh_participant_threshold_or_selection_rows",
            "post_target_updates",
        ):
            self.assertEqual(firewall[key], 0)

    def test_single_model_family_and_source_stop_gate_are_frozen(self):
        model = self.record["model"]
        self.assertEqual(model["feature_dimension"], 320)
        self.assertEqual(model["model_candidates"], 1)
        self.assertEqual(model["hyperparameter_searches"], 0)
        gate = self.record["source_stop_gate"]
        self.assertEqual(gate["folds"], 15)
        self.assertTrue(gate["failure_prevents_fresh_payload_acquisition"])

    def test_controls_and_claim_ceiling_are_honest(self):
        controls = set(self.record["controls"])
        self.assertTrue(
            {"equal_prior_no_signal", "timing_only", "early_cue", "frontal_view"}.issubset(controls)
        )
        boundary = self.record["claim_boundary"]
        self.assertEqual(boundary["maximum_future_route"], "EEGMMIDBUG1-R4")
        self.assertTrue(
            all(
                value is False
                for key, value in boundary.items()
                if key not in {"maximum_future_route", "maximum_future_claim"}
            )
        )
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("## Why This Is Next", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
