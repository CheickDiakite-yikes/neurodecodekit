from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FAILURE = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_generated_failure.v0.json"
)
DOC = ROOT / "docs" / "COMMUNICATION_EEG_INDEPENDENT_REPLICATION_GENERATED_FAILURE.md"
RESULT = (
    ROOT
    / "registries"
    / "communication_eeg_independent_replication_generated_result.v0.json"
)
FRONTIER = ROOT / "registries" / "current_research_frontier.v0.json"


class CommR0GeneratedFailureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.failure = json.loads(FAILURE.read_text(encoding="utf-8"))

    def test_exact_green_execution_head_is_bound(self) -> None:
        binding = self.failure["execution_binding"]
        self.assertEqual(
            binding["execution_HEAD"],
            "0071843687be30aa27c650f12c350e5c16c8e68c",
        )
        self.assertEqual(binding["activation_proof_CI_run_id"], 33095990523)
        self.assertEqual(binding["activation_proof_base_python_job_id"], 98600920033)
        self.assertEqual(
            binding["activation_proof_optional_neuro_readers_job_id"], 98600920329
        )
        self.assertTrue(binding["both_required_activation_proof_jobs_green_before_execution"])

    def test_expected_adversarial_fixture_caused_fail_closed_result(self) -> None:
        observed = self.failure["observed_failure"]
        self.assertEqual(observed["refusal_id"], "G2-TEMPORARY-SYMLINK")
        self.assertTrue(observed["adversarial_symlink_was_expected_fixture"])
        self.assertFalse(observed["unexpected_external_symlink_detected"])
        self.assertFalse(observed["intended_result_published"])
        self.assertFalse(RESULT.exists())

    def test_invocation_is_consumed_and_cleanup_completed(self) -> None:
        binding = self.failure["execution_binding"]
        self.assertEqual(binding["registered_invocations"], 1)
        self.assertFalse(binding["retry_allowed"])
        self.assertFalse(binding["rerun_allowed"])
        self.assertFalse(binding["repair_in_place_allowed"])
        post = self.failure["postfailure_state"]
        self.assertTrue(post["temporary_cleanup_completed"])
        self.assertFalse(post["invocation_temporary_directory_exists"])
        self.assertFalse(post["generated_prediction_or_target_artifacts_retained"])

    def test_failure_closeout_is_remotely_green(self) -> None:
        proof = self.failure["closeout_proof"]
        self.assertEqual(
            proof["failure_record_commit"],
            "9876cf92e7c15503064a38c976fef454915687cd",
        )
        self.assertEqual(proof["failure_record_CI_run_id"], 33097495998)
        self.assertEqual(proof["failure_record_base_python_job_id"], 98606113010)
        self.assertEqual(
            proof["failure_record_optional_neuro_readers_job_id"], 98606113427
        )
        self.assertTrue(proof["both_required_jobs_green"])

    def test_generated_schedule_is_not_mislabeled_as_science(self) -> None:
        completed = self.failure["completed_generated_work_before_failure"]
        self.assertEqual(completed["planned_parameter_update_fits_executed"], 312)
        self.assertEqual(completed["planned_model_inference_runs_executed"], 288)
        self.assertEqual(completed["planned_prediction_sets_created"], 360)
        self.assertEqual(completed["planned_prediction_rows_created"], 8640)
        self.assertFalse(completed["accepted_official_generated_score"])
        self.assertEqual(completed["scientific_value"], "none_generated_engineering_only")

    def test_unavailable_measurements_are_null_not_zero(self) -> None:
        measurements = self.failure["measurements"]
        for field in (
            "exact_executor_runtime_seconds",
            "peak_process_tree_RSS_bytes",
            "generated_input_bytes",
            "private_generated_output_bytes",
            "temporary_disk_bytes",
            "producer_is_causal",
        ):
            self.assertIsNone(measurements[field])
        self.assertEqual(measurements["public_result_bytes"], 0)

    def test_real_counters_and_claims_remain_zero_or_false(self) -> None:
        measurements = self.failure["measurements"]
        real_counters = {
            key: value
            for key, value in measurements.items()
            if key.startswith("real_") or key == "analysis_network_bytes"
        }
        self.assertTrue(all(value == 0 for value in real_counters.values()))
        claims = self.failure["claim_boundary"]
        claim_flags = {key: value for key, value in claims.items() if key != "engineering_result"}
        self.assertTrue(all(value is False for value in claim_flags.values()))

    def test_frontier_closes_generated_lane_and_preserves_dreyer(self) -> None:
        frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
        generated = frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["independent_replication_preregistration"]["generated_implementation"]
        self.assertEqual(generated["status"], "failed_closed_consumed_no_rerun")
        self.assertEqual(generated["official_generated_qualification_invocations"], 1)
        self.assertFalse(generated["official_generated_qualification_rerun_allowed"])
        self.assertEqual(frontier["active_lane_id"], "DREYER-C5R-1-HL")

    def test_document_is_plain_about_failure_and_limits(self) -> None:
        normalized = " ".join(DOC.read_text(encoding="utf-8").split())
        for phrase in (
            "G2-TEMPORARY-SYMLINK",
            "consumed and may not be rerun",
            "No retry or rerun was attempted",
            "No real EEG was accessed",
            "DREYER-C5R-1-HL",
        ):
            self.assertIn(phrase, normalized)


if __name__ == "__main__":
    unittest.main()
