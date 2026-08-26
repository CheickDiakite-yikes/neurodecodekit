from __future__ import annotations

import hashlib
import json
import os
import unittest
from pathlib import Path

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h

ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/dreyer_c5r_1_stage_h_generated_qualification_result.v0.json"
)
DOC_PATH = ROOT / "docs/DREYER_C5R_1_STAGE_H_GENERATED_QUALIFICATION_RESULT.md"
RESULT_BYTES = 4_707
RESULT_SHA256 = "3472c0b8e391ea2464491cf2347aefcf62994726543f818a492d298babc4cd10"


class DreyerC5R1StageHGeneratedQualificationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_exact_result_identity_and_remote_green_proof(self) -> None:
        self.assertEqual(len(self.payload), RESULT_BYTES)
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), RESULT_SHA256)
        self.assertEqual(self.result["lane_id"], "DREYER-C5R-1-H")
        self.assertEqual(
            self.result["status"], "passed_generated_mock_only_no_real_data_or_network"
        )
        self.assertEqual(self.result["contract"]["sha256"], stage_h.CONTRACT_SHA256)
        proof = self.result["implementation_proof"]["remote_green"]
        self.assertEqual(
            proof["head_sha"], "634fc9826f16352abb4fa1fc940c7bc6c2a0a795"
        )
        self.assertEqual(proof["head_sha"], proof["remote_head_sha"])
        self.assertEqual(proof["head_sha"], proof["CI_head_sha"])
        self.assertEqual(proof["CI_run_id"], 32_933_431_849)
        self.assertEqual(proof["base_python_job_id"], 98_069_988_213)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 98_069_988_451)

    def test_exact_generated_cases_and_sensor_contract_passed(self) -> None:
        cases = self.result["cases"]
        self.assertEqual(cases["valid_cases_passed"], 2)
        self.assertEqual(cases["adversarial_cases_refused"], 18)
        self.assertTrue(cases["deterministic_replay"])
        sensor = cases["sensor_contract"]
        self.assertEqual(sensor["EEG_channel_count"], 27)
        self.assertEqual(sensor["EOG_channel_count"], 3)
        self.assertEqual(sensor["EMG_channel_count"], 2)
        self.assertEqual(sensor["physiological_sampling_rate_hz"], 512.0)

    def test_measurements_are_exact_and_bounded(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["generated_input_bytes"], 194_048)
        self.assertEqual(measurements["private_temporary_bytes"], 19_456)
        self.assertEqual(measurements["public_output_bytes"], RESULT_BYTES)
        self.assertEqual(measurements["peak_process_tree_RSS_bytes"], 69_681_152)
        self.assertLessEqual(
            measurements["runtime_seconds"],
            stage_h.GENERATED_CAPS["runtime_seconds_maximum"],
        )
        self.assertFalse(measurements["producer_causal"])
        self.assertIsNone(measurements["required_context_seconds"])
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_every_real_operation_and_claim_counter_is_zero(self) -> None:
        counters = self.result["access_counters"]
        self.assertEqual(counters["pre_qualification_Git_remote_metadata_calls"], 1)
        self.assertEqual(counters["pre_qualification_GitHub_Actions_metadata_calls"], 2)
        for key, value in counters.items():
            if key not in {
                "pre_qualification_Git_remote_metadata_calls",
                "pre_qualification_GitHub_Actions_metadata_calls",
            }:
                self.assertEqual(value, 0, key)
        self.assertFalse(self.result["planned_real_preflight"]["real_authority"])

    def test_consumed_result_refuses_before_remote_or_fixture_work(self) -> None:
        previous = {
            name: os.environ.get(name) for name in stage_h.parent.THREAD_ENVIRONMENT
        }
        proof_calls = 0

        def unexpected_proof(_root: str | Path) -> dict[str, object]:
            nonlocal proof_calls
            proof_calls += 1
            raise AssertionError("consumed result must refuse before remote proof")

        try:
            os.environ.update(
                {name: "1" for name in stage_h.parent.THREAD_ENVIRONMENT}
            )
            with self.assertRaises(stage_h.parent.DreyerExperimentRefusal):
                stage_h.run_generated_qualification(
                    RESULT_PATH,
                    root=ROOT,
                    remote_proof_collector=unexpected_proof,
                )
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
        self.assertEqual(proof_calls, 0)

    def test_closeout_states_engineering_result_and_scientific_nonclaim(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Stage H generated qualification is consumed", text)
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("all-false Tier C authorization packet", text)


if __name__ == "__main__":
    unittest.main()
