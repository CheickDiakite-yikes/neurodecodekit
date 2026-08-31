from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import fresh_motor_source_admission as admission


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/fresh_motor_source_admission_generated_qualification_result.v0.json"
ACTIVATION = (
    ROOT / "registries/fresh_motor_source_admission_generated_qualification_activation.v0.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v19.json"


class FreshMotorSourceAdmissionGeneratedQualificationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT.read_bytes()
        cls.result = json.loads(cls.payload)
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_public_result_is_exact_and_valid(self) -> None:
        self.assertEqual(len(self.payload), 18_162)
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "5ed3a6deb4f3e52aee7874d2288a3ee693daf8766dc9aebb89609d0fa3af694d",
        )
        admission.validate_public_report(self.result)
        self.assertEqual(self.result["status"], "passed_generated_only_zero_network")

    def test_activation_was_green_before_execution(self) -> None:
        self.assertEqual(
            self.activation["implementation_commit"],
            "d9229c1d8e9c56e2ce31da0dec0dcf302fe73eee",
        )
        observed = self.frontier["generated_qualification"]
        self.assertEqual(
            observed["activation_commit"],
            "3de14c3d2e77181dac158f89e92e3a3f26cc10ae",
        )
        self.assertEqual(observed["activation_CI_run_id"], 33_350_175_624)
        self.assertEqual(observed["activation_base_python_job_id"], 99_361_845_630)
        self.assertEqual(observed["activation_optional_neuro_readers_job_id"], 99_361_845_491)
        self.assertTrue(observed["both_activation_jobs_green_before_execution"])
        self.assertEqual(observed["execution_observed_at_UTC"], "2026-08-31T02:26:22Z")

    def test_measured_replays_refusals_and_resources_are_exact(self) -> None:
        qualification = self.result["qualification"]
        measurements = self.result["measurements"]
        self.assertEqual(qualification["deterministic_replays"], 2)
        self.assertTrue(qualification["replay_digests_equal"])
        self.assertEqual(qualification["refusal_case_count"], 82)
        self.assertEqual(qualification["distinct_refusal_routes"], 13)
        self.assertTrue(qualification["all_refusals_passed"])
        self.assertEqual(measurements["absolute_peak_RSS_bytes"], 21_397_504)
        self.assertEqual(measurements["generated_input_bytes"], 614_976)
        self.assertEqual(measurements["generated_output_bytes"], 13_264)
        self.assertEqual(measurements["temporary_generated_bytes"], 636)
        self.assertLessEqual(measurements["runtime_seconds"], 30.0)
        observed = self.frontier["generated_qualification"]
        self.assertEqual(
            observed["canonical_report_sha256"],
            "ecca650d86088523aefb8d321f1c3034646bb28caa6154a597bb44039f71e062",
        )
        self.assertEqual(observed["durable_official_marker"]["marker_mode"], "0600")
        self.assertEqual(observed["durable_official_marker"]["marker_bytes"], 114)
        self.assertEqual(
            observed["durable_official_marker"]["marker_sha256"],
            "03c80a84f4eb1b081ea69b0f9f8156490f2a2b4ec5d5c429a7a5e5a1e8e71e67",
        )

    def test_all_protected_operation_counters_are_zero(self) -> None:
        self.assertTrue(self.result["operation_counters"])
        self.assertTrue(all(value == 0 for value in self.result["operation_counters"].values()))
        self.assertFalse(self.frontier["claim_boundary"]["real_EEG_accessed"])
        self.assertFalse(self.frontier["claim_boundary"]["neural_advantage_established"])
        self.assertFalse(
            self.frontier["operation_authority_now"]["rerun_or_repair_generated_qualification"]
        )


if __name__ == "__main__":
    unittest.main()
