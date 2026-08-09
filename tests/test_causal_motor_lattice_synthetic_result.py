import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/causal_motor_lattice_synthetic_result.v0.json"
DOC_PATH = ROOT / "docs/CAUSAL_MOTOR_LATTICE_SYNTHETIC_RESULT.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CausalMotorLatticeSyntheticResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_is_consumed_parked_and_not_rerunnable(self):
        self.assertEqual(
            self.result["status"],
            "consumed_parked_CML_R0_no_rerun_final_not_delivered",
        )
        decision = self.result["decision"]
        self.assertEqual(decision["route"], "CML-R0")
        self.assertFalse(decision["check_passed"])
        self.assertFalse(decision["final_targets_delivered"])
        self.assertEqual(decision["final_scoring_events"], 0)
        self.assertFalse(self.result["execution_identity"]["rerun_allowed"])

    def test_contract_and_green_implementation_are_exactly_bound(self):
        contract = self.result["contract_binding"]
        implementation = self.result["implementation_binding"]
        self.assertEqual(contract["sha256"], sha256(ROOT / contract["path"]))
        self.assertEqual(implementation["sha256"], sha256(ROOT / implementation["path"]))
        self.assertEqual(implementation["commit"], "90fa467e5acf24a8a47eb8c96b1cb485a6a9076b")
        self.assertEqual(implementation["push_CI_run"], 31295430105)
        self.assertTrue(implementation["both_required_jobs_passed_before_execution"])

    def test_only_common_mode_gate_failed_at_the_exact_margin(self):
        decision = self.result["decision"]
        self.assertEqual(decision["check_gates_passed"], 18)
        self.assertEqual(decision["check_gates_total"], 19)
        self.assertEqual(decision["failed_check_gates"], ["common_mode_invariance"])
        failed = self.result["failed_gate"]
        self.assertEqual(failed["observed"], 1.9073486328125e-06)
        self.assertEqual(failed["maximum_allowed"], 1e-06)
        self.assertEqual(failed["excess_above_tolerance"], 9.073486328125e-07)
        self.assertFalse(failed["may_be_retested_under_this_contract"])

    def test_constructed_factor_and_control_metrics_are_preserved_without_overclaim(self):
        metrics = self.result["check_metrics"]
        self.assertEqual(metrics["signal_bearing_hand_accuracy"], 1.0)
        self.assertEqual(metrics["signal_bearing_key_accuracy"], 1.0)
        self.assertEqual(metrics["all_views_muted_hand_accuracy"], 0.5)
        self.assertEqual(metrics["spatial_reversal_mirrored_hand_accuracy"], 1.0)
        self.assertEqual(metrics["timing_only_pair_hand_probability_maximum_difference"], 0.0)
        self.assertEqual(metrics["pure_noise_pair_hand_probability_maximum_difference"], 0.0)
        self.assertEqual(metrics["causal_future_tail_prefix_logit_maximum_error"], 0.0)
        self.assertEqual(metrics["peripheral_proxy_only_hand_accuracy"], 1.0)
        self.assertFalse(
            self.result["branch_diagnostics"]["branch_ablation_proves_cortical_physiology"]
        )

    def test_training_replay_resources_and_access_counters_are_exact(self):
        training = self.result["training"]
        self.assertEqual(training["parameter_update_runs"], 1)
        self.assertEqual(training["optimizer_steps"], 600)
        self.assertFalse(training["checkpoint_selection"])
        self.assertFalse(training["rerun_allowed"])
        self.assertTrue(self.result["causal_and_replay_controls"]["replay_hash_match"])
        resources = self.result["resource_measurements"]
        self.assertEqual(resources["runtime_seconds"], 6.5530732499901205)
        self.assertEqual(resources["peak_RSS_bytes"], 398737408)
        self.assertEqual(resources["total_generated_output_bytes"], 37371)
        self.assertTrue(resources["all_resource_gates_passed"])
        counters = self.result["access_counters"]
        for name in (
            "real_or_public_data_reads",
            "protected_target_or_label_reads",
            "S20_path_stats_or_reads",
            "PhysioNet_downloads_or_reads",
            "network_calls",
            "provider_calls",
            "pretrained_weight_or_external_embedding_reads",
            "stream_device_or_hardware_operations",
            "release_operations",
            "scientific_claim_upgrades",
        ):
            self.assertEqual(counters[name], 0, name)

    def test_private_artifacts_are_hash_only_and_public_surfaces_preserve_claim_boundary(self):
        artifacts = self.result["private_invocation_artifact_bindings"]
        self.assertFalse(artifacts["files_committed"])
        self.assertTrue(artifacts["files_removed_after_closeout"])
        self.assertFalse((ROOT / "outputs" / "cml-v0-synthetic-5513").exists())
        self.assertFalse(artifacts["per_item_target_label_prediction_identity_text_or_path_committed"])
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        row = next(
            line
            for line in QUEUE_PATH.read_text(encoding="utf-8").splitlines()
            if line.startswith("| 13 |")
        )
        self.assertIn("Consumed", row)
        self.assertIn("Parked CML-R0", row)
        self.assertIn("No Rerun", row)


if __name__ == "__main__":
    unittest.main()
