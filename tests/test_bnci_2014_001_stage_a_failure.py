import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registries/bnci_2014_001_stage_a_failure.v0.json"
DOCUMENT = ROOT / "docs/BNCI_2014_001_STAGE_A_FAILURE.md"


class BNCIStageAFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(REGISTRY.read_text(encoding="utf-8"))

    def test_exact_green_implementation_is_bound(self):
        green = self.result["green_implementation"]
        self.assertEqual(green["commit"], "619105bda3c39c063bb47bda6793af2ece9e1f53")
        self.assertEqual(green["CI_run_id"], 32_781_910_547)
        self.assertEqual(green["base_python_job_id"], 97_605_610_792)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97_605_610_605)
        self.assertTrue(green["both_required_jobs_green"])

    def test_failure_preceded_every_payload_or_scientific_operation(self):
        failure = self.result["failure"]
        self.assertEqual(failure["HTTP_status"], 302)
        self.assertTrue(failure["invocation_consumed"])
        operations = self.result["operations"]
        self.assertEqual(operations["HTTPS_requests"], 1)
        self.assertEqual(operations["payload_body_reads"], 0)
        for key in (
            "accepted_files",
            "MAT_semantic_content_opens",
            "MAT_semantic_parses",
            "signal_event_target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(operations[key], 0, key)

    def test_retained_state_and_measurements_are_exact(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["payload_network_body_bytes"], 0)
        self.assertEqual(measurements["consumed_marker_bytes"], 297)
        self.assertIsNone(measurements["peak_RSS_bytes"])
        retained = self.result["retained_private_state"]
        self.assertTrue(retained["consumed_marker_present"])
        self.assertFalse(retained["payload_bundle_present"])
        self.assertFalse(retained["receipt_present"])
        self.assertFalse(retained["partial_directory_present"])

    def test_stage_q_and_claims_remain_closed(self):
        authority = self.result["authority"]
        self.assertTrue(authority["original_Stage_A_invocation_consumed"])
        self.assertFalse(authority["retry_rerun_resume_restart_or_substitution_allowed"])
        self.assertFalse(authority["Stage_Q_allowed"])
        self.assertTrue(authority["new_narrow_recovery_decision_required"])
        self.assertFalse(self.result["claim_boundary"]["scientific_claim_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering result", document)
        self.assertIn("Scientific claim not established", document)


if __name__ == "__main__":
    unittest.main()
