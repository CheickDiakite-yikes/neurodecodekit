import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = REPO_ROOT / "registries" / "loop48_stage_c_synthetic_result.v0.json"
IMPLEMENTATION_PATH = (
    REPO_ROOT / "registries" / "loop48_stage_c_synthetic_implementation.v0.json"
)
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
CLOSEOUT_PATH = REPO_ROOT / "docs" / "LOOP_48_STAGE_C_SYNTHETIC_RESULT.md"
RESULT_SHA256 = "3c1c0d7286526f00a51325c04493b2c07bd5a989f683df03c50d2181f6fa738a"


class Loop48StageCSyntheticResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result_bytes = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.result_bytes)
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.closeout = CLOSEOUT_PATH.read_text(encoding="utf-8")

    def test_result_identity_and_no_rerun_status_are_exact(self):
        self.assertEqual(hashlib.sha256(self.result_bytes).hexdigest(), RESULT_SHA256)
        self.assertEqual(len(self.result_bytes), 7546)
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.loop48_stage_c_synthetic_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["status"], "consumed_parked_gate_failed_no_rerun")
        self.assertEqual(self.result["execution"]["one_shot_execution_count"], 1)
        self.assertEqual(self.result["execution"]["rerun_count"], 0)
        self.assertFalse(
            self.result["authorization"]["synthetic_rerun_authorized_now"]
        )

    def test_remote_green_correction_preceded_execution(self):
        identity = self.result["identity"]
        self.assertEqual(
            identity["preflight_correction_commit"],
            "2836ecceafed3d35c6f255714ad1c7a9b71e2e25",
        )
        self.assertEqual(identity["preflight_correction_push_ci_run_id"], 29467415680)
        self.assertEqual(
            identity["preflight_correction_pull_request_ci_run_id"], 29467416894
        )
        self.assertTrue(identity["all_remote_workflows_green_before_execution"])
        binding = self.implementation["consumed_synthetic_result"]
        self.assertEqual(binding["path"], RESULT_PATH.relative_to(REPO_ROOT).as_posix())
        self.assertEqual(binding["sha256"], RESULT_SHA256)

    def test_frozen_selection_and_final_metrics_are_exact(self):
        selection = self.result["selection"]
        self.assertEqual(selection["selected_recipe_id"], "L48C-SYN-OPT0")
        self.assertAlmostEqual(selection["L48C-SYN-OPT0_macro_cer"], 0.5104166666666666)
        self.assertAlmostEqual(selection["L48C-SYN-OPT1_macro_cer"], 1.0)
        self.assertAlmostEqual(selection["L48C-SYN-OPT2_macro_cer"], 0.5333333333333333)
        self.assertTrue(selection["selection_rule_applied_unchanged"])

        final = self.result["final_metrics"]
        self.assertEqual(final["rows"], 8)
        self.assertAlmostEqual(final["candidate_macro_cer"], 0.43333333333333335)
        self.assertEqual(final["candidate_exact_sequences"], 1)
        self.assertAlmostEqual(final["ablation_macro_cer"], 1.0)
        self.assertEqual(final["ablation_exact_sequences"], 0)
        self.assertAlmostEqual(
            final["candidate_minus_ablation_cer_improvement"],
            0.5666666666666667,
        )

    def test_relative_gate_passes_but_absolute_gate_fails(self):
        gates = self.result["gates"]
        self.assertTrue(gates["candidate_minus_ablation_passed"])
        self.assertFalse(gates["candidate_final_cer_passed"])
        self.assertFalse(gates["candidate_final_exact_sequences_passed"])
        self.assertTrue(gates["deterministic_checkpoint_replay_passed"])
        self.assertTrue(gates["future_mutation_controls_passed"])
        self.assertTrue(gates["prefix_resume_equivalence_passed"])
        self.assertFalse(gates["aggregate_gate_passed"])

    def test_operation_and_resource_ledgers_are_bounded(self):
        execution = self.result["execution"]
        self.assertEqual(execution["training_runs"], 4)
        self.assertEqual(execution["optimizer_steps"], 1680)
        self.assertEqual(execution["model_inference_runs"], 8)
        self.assertEqual(execution["synthetic_final_rows_opened_once"], 8)
        self.assertFalse(execution["plaintext_targets_or_predictions_emitted"])

        resources = self.result["resources"]
        self.assertLessEqual(
            resources["generated_artifact_bytes"],
            resources["generated_artifact_cap_bytes"],
        )
        self.assertLessEqual(
            resources["internal_peak_rss_bytes"],
            resources["peak_rss_cap_bytes"],
        )
        self.assertGreaterEqual(
            resources["free_disk_before_bytes"],
            resources["minimum_free_disk_bytes"],
        )
        self.assertTrue(resources["all_resource_caps_passed"])

    def test_all_real_protected_and_hardware_counters_are_zero(self):
        counters = self.result["access_counters"]
        for key, value in counters.items():
            self.assertEqual(value, 0, key)
        self.assertTrue(self.result["producer"]["causal"])
        self.assertEqual(self.result["producer"]["right_context_frames"], 0)
        self.assertFalse(self.result["producer"]["end_to_end_latency_measured"])

    def test_no_plaintext_target_or_prediction_is_committed(self):
        serialized = json.dumps(self.result, sort_keys=True)
        for forbidden in (
            '"target_texts"',
            '"prediction_text"',
            '"predictions"',
            '"source_targets"',
        ):
            self.assertNotIn(forbidden, serialized)

    def test_closeout_and_roadmap_preserve_the_claim_boundary(self):
        normalized = " ".join(self.closeout.split())
        for phrase in (
            "0.433333",
            "1/8",
            "0.566667",
            "consumed and parked",
            "no rerun",
            "Scientific claim not established",
            RESULT_SHA256,
        ):
            self.assertIn(phrase, normalized)
        loop48 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 48)
        self.assertEqual(loop48["status"], "Complete A/B; Stage C Consumed and Parked")
        self.assertFalse(loop48["execution_authorized"])
        self.assertIn("failed both absolute synthetic gates", loop48["kill_or_park_rule"])
        self.assertIn("Stage C is consumed and parked", loop48["authorization_boundary"])


if __name__ == "__main__":
    unittest.main()
