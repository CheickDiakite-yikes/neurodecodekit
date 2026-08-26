from __future__ import annotations

import json
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/dreyer_c5r_1_contract.v0.json"
DOC_PATH = ROOT / "docs/DREYER_C5R_1_PREREGISTRATION.md"


class DreyerC5R1PreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_identity_sequence_and_cohort_are_exact(self) -> None:
        self.assertEqual(self.contract["lane_id"], "DREYER-C5R-1")
        self.assertEqual(
            self.contract["status"], "prospectively_frozen_no_real_data_authority"
        )
        self.assertEqual(
            self.contract["evidence_sequence"],
            [
                "G_generated_qualification",
                "H_one_source_EDF_header_preflight",
                "A_exact_120_member_bundle_completion",
                "Q_target_firewalled_semantic_derivatives",
                "P_source_only_models_and_hash_frozen_predictions",
                "T_one_target_delivery_and_one_frozen_score",
            ],
        )
        cohort = self.contract["cohort"]
        self.assertEqual(cohort["participants"], 60)
        self.assertEqual(cohort["total_trials"], 4_800)
        self.assertEqual(cohort["source_participants_per_fold"], 59)
        self.assertEqual(cohort["held_out_participants_per_fold"], 1)
        bindings = self.contract["bindings"]
        self.assertEqual(bindings["research_registry_bytes"], 4_381)
        self.assertEqual(
            bindings["research_registry_sha256"],
            "13547e5dd8c02b73edf89dc5d471c0e641559e0c7ec8610f36b4dd5e4f188201",
        )

    def test_feature_and_model_family_are_fixed(self) -> None:
        features = self.contract["features"]
        self.assertEqual(features["central_dimensions"], 27)
        self.assertEqual(features["windows_seconds"]["late"], [[5.0, 6.0], [6.0, 7.0], [7.0, 8.0]])
        self.assertTrue(features["producer_causal"])
        self.assertFalse(features["end_to_end_latency_measured"])
        model = self.contract["classifier"]
        self.assertEqual(model["family"], "sklearn_LogisticRegression_L2")
        self.assertEqual(model["C"], 0.1)
        self.assertEqual(model["max_iter"], 1_000)
        self.assertEqual(self.contract["residualization"]["alpha"], 10.0)
        self.assertFalse(self.contract["residualization"]["labels_used"])

    def test_schedule_is_internally_consistent(self) -> None:
        schedule = self.contract["schedule"]
        self.assertEqual(len(self.contract["conditions"]), 17)
        self.assertEqual(
            schedule["held_out_prediction_sets"],
            schedule["outer_folds"] * schedule["conditions_per_fold"],
        )
        self.assertEqual(
            schedule["held_out_prediction_rows"],
            schedule["held_out_prediction_sets"] * 80,
        )
        self.assertEqual(schedule["parameter_update_fits"], 4_740)
        self.assertEqual(schedule["post_target_updates"], 0)
        self.assertEqual(schedule["reruns"], 0)

    def test_gate_requires_effect_specificity_consistency_and_calibration(self) -> None:
        gate = self.contract["primary_gate"]
        self.assertEqual(gate["nuisance_log_loss_delta_minimum"], 0.02)
        self.assertEqual(gate["deranged_log_loss_delta_minimum"], 0.02)
        self.assertEqual(gate["positive_participants_minimum_each_coprimary"], 39)
        self.assertEqual(
            gate["one_sided_exact_binomial_sign_p_maximum_each_coprimary"], 0.025
        )
        self.assertAlmostEqual(
            gate["late_N_plus_R_log_loss_maximum_exclusive"], math.log(2.0)
        )
        self.assertEqual(gate["late_N_plus_R_ECE_maximum"], 0.1)
        self.assertTrue(gate["structural_and_firewall_assertions_all_required"])

    def test_real_authority_remains_false(self) -> None:
        authority = self.contract["authority"]
        for key in (
            "real_header_payload_or_semantic_access",
            "real_acquisition",
            "real_training_or_inference",
            "real_target_delivery_or_scoring",
            "claim_upgrade",
        ):
            self.assertFalse(authority[key], key)
        self.assertIn("Tier_B", authority["generated_qualification"])

    def test_document_keeps_target_and_claim_boundaries_explicit(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("nuisance + residual central EEG", text)
        self.assertIn("completely unseen participant", text)
        self.assertIn("Target Firewall And Publication", text)
        self.assertIn("does not measure acquisition", text)
        self.assertIn("would not establish spontaneous intention", text)


if __name__ == "__main__":
    unittest.main()
