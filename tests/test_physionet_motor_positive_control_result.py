import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/physionet_motor_positive_control_result.v0.json"
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_RESULT.md"
EXPECTED_SHA256 = "017c62162774b5cd32a635f58bb4c503f903a8e901cb2b696efa0890a1040579"


class PhysioNetMotorPositiveControlResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_status_and_hash_are_exact(self):
        self.assertEqual(hashlib.sha256(RESULT_PATH.read_bytes()).hexdigest(), EXPECTED_SHA256)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.physionet_motor_positive_control_result",
        )
        self.assertEqual(self.result["status"], "consumed_one_final_score_no_retry_no_rerun")
        self.assertEqual(self.result["verdict"], "WO9-V1")

    def test_remote_green_freeze_parent_is_exact(self):
        freeze = self.result["prediction_freeze"]
        self.assertEqual(freeze["commit"], "01eeff6e9a5ead1790e0f91aa52a443402eb397c")
        self.assertEqual(freeze["ci_run_id"], 31352250838)
        self.assertEqual(freeze["base_python_job_id"], 93345130576)
        self.assertEqual(freeze["optional_neuro_job_id"], 93345130569)
        self.assertEqual(
            freeze["ledger_sha256"],
            "3c100daa8a6a2816ce4270c9e32cbdcc4cd30d70d1c255e37596c2ca6f665de4",
        )

    def test_registered_primary_failed_without_post_target_promotion(self):
        primary = self.result["primary_gate"]
        self.assertFalse(primary["passed"])
        self.assertFalse(primary["threshold_components_passed"])
        self.assertTrue(primary["beats_train_only_no_signal"])
        metrics = primary["metrics"]
        self.assertEqual(metrics["correct_count"], 27)
        self.assertAlmostEqual(metrics["pooled_balanced_accuracy"], 0.6037549407114624)
        self.assertAlmostEqual(metrics["one_sided_within_participant_permutation_p"], 0.13739013671875)
        self.assertEqual(self.result["selected_family"], "fixed_8_to_30_hz_csp_lda")

    def test_prespecified_low_frequency_comparator_is_strong_but_secondary(self):
        metrics = self.result["condition_metrics"][
            "low_frequency_shrinkage_lda_comparator"
        ]
        self.assertEqual(metrics["correct_count"], 36)
        self.assertAlmostEqual(metrics["pooled_balanced_accuracy"], 0.8003952569169961)
        self.assertAlmostEqual(
            metrics["macro_participant_balanced_accuracy"], 0.8005952380952381
        )
        self.assertAlmostEqual(metrics["minimum_participant_balanced_accuracy"], 0.7321428571428572)
        self.assertEqual(metrics["participants_above_0_5_balanced_accuracy"], 3)
        self.assertAlmostEqual(
            metrics["one_sided_within_participant_permutation_p"],
            0.00018310546875,
        )
        self.assertNotEqual(
            self.result["selected_family"],
            "low_frequency_shrinkage_lda_comparator",
        )

    def test_physiology_and_localization_conjunction_failed(self):
        physiology = self.result["physiology_gate"]
        self.assertFalse(physiology["gate_passed"])
        self.assertEqual(physiology["participants_with_registered_direction"], 2)
        self.assertLess(physiology["pooled_contralateral_minus_ipsilateral"], 0.0)
        self.assertAlmostEqual(physiology["paired_event_sign_flip_p"], 0.10833740234375)
        confound = self.result["confound_gate"]
        self.assertFalse(confound["passed"])
        self.assertFalse(confound["components"]["central_minus_proxy_at_least_0_05"])
        self.assertTrue(confound["components"]["frontal_occipital_proxy_fails_primary"])

    def test_single_delivery_score_and_all_resource_gates_passed(self):
        self.assertTrue(all(self.result["resource_gates"].values()))
        measurements = self.result["measurements"]
        self.assertEqual(measurements["final_target_deliveries"], 1)
        self.assertEqual(measurements["final_scoring_events"], 1)
        self.assertEqual(measurements["retries"], 0)
        self.assertEqual(measurements["reruns"], 0)
        self.assertEqual(measurements["network_bytes"], 0)
        self.assertEqual(measurements["new_payload_bytes"], 0)
        self.assertLessEqual(measurements["peak_rss_bytes"], 805_306_368)
        self.assertLessEqual(measurements["generated_private_output_bytes"], 67_108_864)
        self.assertEqual(measurements["public_result_bytes"], RESULT_PATH.stat().st_size)

    def test_public_result_contains_no_individual_outputs(self):
        outputs = self.result["individual_outputs"]
        self.assertTrue(all(value is False for value in outputs.values()))
        forbidden = {
            "event_ids",
            "participant_ids",
            "predictions",
            "probabilities",
            "targets",
            "labels",
            "participant_outcomes",
            "participant_scores",
        }

        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)

        walk(self.result)

    def test_claim_ceiling_keeps_neural_and_product_claims_closed(self):
        claim = self.result["claim_boundary"]
        for phrase in (
            "Brain-specific origin",
            "unseen-person generalization",
            "typing",
            "real-time performance",
            "portable hardware",
            "clinical utility",
        ):
            self.assertIn(phrase, claim["not_established"])
        self.assertFalse(self.result["measurements"]["end_to_end_latency_measured"])

    def test_closeout_document_and_tracker_are_consumed(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Scientific result established", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("0.800 pooled balanced accuracy", document)
        tracker = (
            ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
        ).read_text(encoding="utf-8")
        row = next(line for line in tracker.splitlines() if line.startswith("| 9 |"))
        self.assertIn("Complete", row)
        self.assertIn("Consumed", row)
        self.assertIn("WO9-V1", row)
        self.assertIn("No Rerun", row)


if __name__ == "__main__":
    unittest.main()
