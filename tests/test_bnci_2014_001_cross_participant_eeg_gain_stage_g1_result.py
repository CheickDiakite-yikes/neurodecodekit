import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = (
    ROOT / "registries/bnci_2014_001_cross_participant_eeg_gain_implementation.v0.json"
)
RESULT = (
    ROOT
    / "registries/bnci_2014_001_cross_participant_eeg_gain_stage_g1_result.v0.json"
)
DOCUMENT = (
    ROOT / "docs/BNCI_2014_001_CROSS_PARTICIPANT_EEG_GAIN_STAGE_G1_RESULT.md"
)


class BNCIStageG1ResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.implementation = json.loads(IMPLEMENTATION.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_green_recovery_decision_preceded_the_one_shot_execution(self):
        binding = self.result["execution_binding"]
        self.assertEqual(
            binding["recovery_authorization_decision_commit"],
            "c5dd49b3d29fcb348fc836812f5a48a6c5526f04",
        )
        self.assertEqual(binding["recovery_authorization_decision_CI_run_id"], 32763519623)
        self.assertEqual(binding["base_python_job_id"], 97547643345)
        self.assertEqual(binding["optional_neuro_readers_job_id"], 97547643658)
        self.assertTrue(binding["all_required_jobs_green_before_execution"])

    def test_decision_artifacts_remain_exact(self):
        for row in self.result["decision_artifacts"]:
            path = ROOT / row["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

    def test_frozen_implementation_sources_remain_exact(self):
        registered = {
            row["path"]: row for row in self.implementation["artifacts"]
        }
        for relative in (
            "src/neurodecodekit/bnci_c3c5_cli.py",
            "src/neurodecodekit/experiments/bnci_2014_001_cross_participant_eeg_gain.py",
        ):
            row = registered[relative]
            path = ROOT / relative
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", str(path)], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob_sha1"])

    def test_recovery_was_consumed_once_and_output_is_hash_bound(self):
        binding = self.result["execution_binding"]
        self.assertEqual(binding["qualification_invocations"], 1)
        self.assertFalse(binding["qualification_may_be_repeated"])
        self.assertTrue(binding["original_refused_invocation_remains_consumed"])
        self.assertTrue(binding["replacement_recovery_invocation_consumed"])
        self.assertEqual(binding["canonical_source_output_bytes"], 3296)
        self.assertEqual(
            binding["canonical_source_output_sha256"],
            "b63ac687fcd6fad38868a7c2081ef1a50c3a3f1be3cbf3e0cfb78632d22d50c6",
        )
        self.assertFalse(binding["canonical_source_output_committed"])

    def test_all_registered_case_classes_passed(self):
        self.assertEqual(self.result["case_classes_passed"], 11)
        self.assertEqual(len(self.result["case_classes"]), 11)
        self.assertEqual(len(set(self.result["case_classes"])), 11)
        self.assertEqual(self.result["prediction_freeze_mutation_refusals"], 3)

    def test_exact_generated_schedule_and_resource_caps(self):
        result = self.result
        self.assertEqual(result["outer_folds"], 9)
        self.assertEqual(result["isolated_fold_processes"], 9)
        self.assertEqual(result["inner_source_participant_folds_per_outer"], 8)
        self.assertEqual(result["parameter_update_fits"], 468)
        self.assertEqual(result["prediction_sets"], 495)
        self.assertEqual(result["model_inference_runs"], 495)
        self.assertEqual(result["synthetic_target_deliveries"], 1)
        self.assertEqual(result["synthetic_scoring_events"], 1)
        self.assertLessEqual(result["runtime_seconds"], 3600)
        self.assertLessEqual(result["peak_process_tree_RSS_bytes"], 1073741824)
        self.assertLessEqual(result["private_generated_bytes_peak"], 536870912)
        self.assertLessEqual(result["output_bytes"], 4194304)
        self.assertGreaterEqual(result["initial_free_disk_bytes"], 5368709120)

    def test_target_firewall_cleanup_and_real_counters_are_zero(self):
        result = self.result
        self.assertEqual(result["fold_target_capabilities_with_held_targets"], 0)
        for key in (
            "network_bytes",
            "new_payload_bytes",
            "raw_data_reads",
            "real_MAT_opens",
            "real_cache_reads",
            "real_model_inference_runs",
            "real_parameter_update_fits",
            "real_prediction_sets",
            "real_scoring_events",
            "real_signal_event_artifact_target_or_label_reads",
            "real_target_deliveries",
            "retained_generated_payload_bytes",
        ):
            self.assertEqual(result[key], 0, key)
        self.assertTrue(result["producer_is_causal"])
        self.assertFalse(result["end_to_end_latency_measured"])

    def test_synthetic_route_has_no_claim_value_and_stage_A_is_closed(self):
        self.assertEqual(self.result["synthetic_router_route"], "BNCIC3C5-R2")
        self.assertIn(
            "synthetic_router_route_has_no_claim_value", self.result["warnings"]
        )
        boundary = self.result["claim_boundary"]
        for key, value in boundary.items():
            if key not in {"maximum_route", "maximum_claim"}:
                self.assertFalse(value, key)
        gate = self.result["next_gate"]
        self.assertFalse(gate["Stage_A_begun"])
        self.assertFalse(gate["Stage_A_allowed_before_result_remote_green"])
        self.assertTrue(gate["recovery_scope_stops_before_Stage_A"])
        self.assertFalse(gate["retry_rerun_resume_restart_or_second_score_allowed"])

        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real BNCI neural payload was opened or", document)


if __name__ == "__main__":
    unittest.main()
