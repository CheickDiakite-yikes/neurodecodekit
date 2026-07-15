import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries" / "loop26_shared_validation_result.v0.json"
RESULT_SHA256 = "7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4"


class Loop26SharedValidationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_result_is_hash_bound_and_consumed(self):
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), RESULT_SHA256)
        self.assertEqual(self.result["status"], "parked_registered_gate_failed")
        self.assertEqual(
            self.result["green_prediction_freeze_commit"],
            "54bdca9e04467b4a1ab842149b55b6c20bbeb9a2",
        )
        self.assertEqual(
            self.result["prediction_freeze_sha256"],
            "10191558a68a8c646e32c4ab0516f84ee99d127b9e6a2ea277c432c6c28b2348",
        )
        self.assertEqual(self.result["validation_target_delivery_events"], 1)
        self.assertEqual(self.result["access_counters"]["validation_scoring_runs"], 1)

    def test_primary_scientific_gate_failed_against_the_prior(self):
        candidate = self.result["condition_metrics"]["L33-N55-S2601"]
        prior = self.result["condition_metrics"]["L33-P55"]
        comparison = self.result["exact_comparisons"]["L31-E01"]
        self.assertAlmostEqual(candidate["macro_sentence_cer"], 0.9381765674382471)
        self.assertAlmostEqual(prior["macro_sentence_cer"], 0.7512350583540796)
        self.assertAlmostEqual(self.result["primary_macro_cer_margin"], -0.1869415090841675)
        self.assertEqual((comparison["wins"], comparison["ties"], comparison["losses"]), (0, 1, 5))
        self.assertEqual(comparison["one_sided_greater_p"], 1.0)
        self.assertFalse(self.result["primary_gate_passed"])
        self.assertFalse(self.result["required_exact_controls_passed"])
        self.assertFalse(self.result["intersection_union_gate_passed"])

    def test_attribution_and_scaling_gates_remain_failed(self):
        self.assertTrue(self.result["linear_comparator_gate_passed"])
        self.assertFalse(self.result["scaling_gate"]["passed"])
        self.assertTrue(self.result["scaling_gate"]["rules"]["every_seed_ols_slope_negative"])
        self.assertFalse(
            self.result["scaling_gate"]["rules"]["size55_gain_over_matched_prior_at_least_0_05"]
        )
        zero = self.result["exact_comparisons"]["L31-E02"]
        self.assertEqual((zero["wins"], zero["ties"], zero["losses"]), (6, 0, 0))
        self.assertEqual(zero["one_sided_greater_p"], 0.015625)

    def test_access_firewalls_and_caps_held(self):
        counters = self.result["access_counters"]
        expected = {
            "source_cache_hash_passes": 1,
            "train_signal_rows_delivered": 55,
            "train_target_rows_delivered": 55,
            "validation_signal_rows_delivered": 6,
            "validation_target_rows_delivered_before_prediction_freeze": 0,
            "validation_target_rows_delivered_after_prediction_freeze": 6,
            "candidate_training_runs": 18,
            "control_training_runs": 3,
            "optimizer_steps": 5040,
            "target_blind_model_inference_runs": 24,
            "no_signal_prior_fits": 6,
            "prediction_sets_frozen": 31,
        }
        for key, value in expected.items():
            self.assertEqual(counters[key], value, key)
        for key in (
            "raw_fif_or_mat_reads",
            "source_test_rows_delivered",
            "source_test_scoring_runs",
            "session2_rows_delivered",
            "session2_scoring_runs",
            "new_downloads",
            "external_network_calls",
            "language_model_or_neurotoken_runs",
            "rw3_stream_device_or_hardware_operations",
            "post_target_parameter_updates",
            "post_target_configuration_changes",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertLess(self.result["peak_rss_bytes"], 1 << 30)
        self.assertLess(self.result["generated_artifact_bytes"], 32 << 20)
        self.assertFalse(self.result["plaintext_targets_or_predictions_present"])


if __name__ == "__main__":
    unittest.main()
