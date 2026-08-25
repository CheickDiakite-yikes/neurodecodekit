import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/bnci_2014_001_stage_a_redirect_recovery_result.v0.json"
)
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_REDIRECT_RECOVERY_RESULT.md"


class BNCIStageARedirectRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_result_is_complete_consumed_and_proof_ordered(self):
        self.assertEqual(
            self.result["status"],
            "passed_complete_consumed_no_retry_no_rerun",
        )
        evidence = self.result["ordered_evidence"]
        self.assertEqual(
            evidence["control_plane_commit"],
            "21cedd5da3c82e4378162ddfd687d669874d8c3f",
        )
        self.assertEqual(evidence["control_plane_CI_run_id"], 32_811_586_786)
        self.assertTrue(evidence["all_prior_gates_green_before_execution"])
        execution = self.result["execution"]
        self.assertTrue(execution["consumed"])
        self.assertFalse(execution["retry_allowed"])
        self.assertFalse(execution["rerun_allowed"])
        self.assertEqual(execution["registered_invocations_remaining"], 0)

    def test_exact_bundle_and_resource_caps_pass(self):
        metrics = self.result["measurements"]
        caps = self.result["registered_caps"]
        self.assertEqual(metrics["payload_files"], 18)
        self.assertEqual(metrics["accepted_payload_bytes"], 779_873_919)
        self.assertEqual(metrics["payload_network_bytes"], 779_873_919)
        self.assertLessEqual(metrics["total_network_bytes"], caps["network_bytes_maximum"])
        self.assertLessEqual(metrics["runtime_seconds"], caps["runtime_seconds_maximum"])
        self.assertLessEqual(
            metrics["peak_process_RSS_bytes"],
            caps["peak_RSS_bytes_maximum"],
        )
        self.assertGreaterEqual(
            metrics["free_disk_bytes_before"],
            caps["free_disk_bytes_minimum"],
        )
        self.assertTrue(caps["all_resource_caps_passed"])
        self.assertFalse(metrics["end_to_end_decoding_latency_measured"])
        verification = self.result["post_result_verification"]
        self.assertEqual(verification["focused_BNCI_tests_passed"], 140)
        self.assertEqual(verification["complete_suite_passed_tests"], 6_066)
        self.assertEqual(verification["complete_suite_expected_skips"], 217)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compileall_passed"])
        self.assertTrue(verification["git_diff_check_passed"])

    def test_forbidden_semantic_and_scientific_counters_are_zero(self):
        counters = self.result["operation_counters"]
        for key in (
            "MAT_semantic_content_opens",
            "MAT_semantic_parses",
            "signal_event_target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(counters[key], 0, key)
        self.assertEqual(counters["payload_requests"], 18)
        self.assertEqual(counters["opaque_post_write_hash_opens"], 18)

    def test_original_marker_and_private_evidence_are_bound(self):
        marker = self.result["original_consumed_marker"]
        self.assertTrue(marker["byte_identical"])
        self.assertEqual(marker["sha256_before"], marker["sha256_after"])
        private = self.result["private_evidence_binding"]
        self.assertEqual(private["aggregate_receipt_bytes"], 2_347)
        self.assertRegex(private["aggregate_receipt_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(private["aggregate_receipt_committed_or_uploaded"])
        self.assertFalse(private["payload_or_private_manifest_committed_or_uploaded"])

    def test_all_acceptance_gates_pass_and_scientific_goals_remain_false(self):
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        self.assertEqual(
            set(self.result["five_scientific_goals"].values()),
            {"not_established"},
        )
        next_gate = self.result["next_gate"]
        self.assertTrue(next_gate["Stage_A_complete"])
        self.assertFalse(next_gate["Stage_A_rerun_allowed"])
        self.assertFalse(next_gate["Stage_Q_started"])
        self.assertFalse(next_gate["Stage_Q_allowed_before_green_result"])

    def test_document_states_both_engineering_and_scientific_boundaries(self):
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("Stage A is complete and consumed", document)
        self.assertIn("Stage P and Stage T remain closed", document)
        self.assertIn("6,066 tests", document)


if __name__ == "__main__":
    unittest.main()
