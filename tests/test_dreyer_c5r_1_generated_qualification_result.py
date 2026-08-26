from __future__ import annotations

import hashlib
import json
import os
import unittest
from pathlib import Path

from neurodecodekit.experiments import dreyer_c5r_1 as experiment


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/dreyer_c5r_1_generated_qualification_result.v0.json"
DOC_PATH = ROOT / "docs/DREYER_C5R_1_GENERATED_QUALIFICATION_RESULT.md"
RESULT_BYTES = 3_695
RESULT_SHA256 = "58fa7207a935edefc1337813319aa17ee8a3e9faee126970733fa52436a03a74"


class DreyerC5R1GeneratedQualificationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_exact_result_identity_and_remote_green_proof(self) -> None:
        self.assertEqual(len(self.payload), RESULT_BYTES)
        self.assertEqual(hashlib.sha256(self.payload).hexdigest(), RESULT_SHA256)
        self.assertEqual(self.result["lane_id"], "DREYER-C5R-1")
        self.assertEqual(
            self.result["status"], "passed_generated_only_no_real_or_private_data"
        )
        self.assertEqual(
            self.result["contract"]["sha256"], experiment.CONTRACT_SHA256
        )
        proof = self.result["implementation_proof"]["remote_green"]
        self.assertEqual(
            proof["head_sha"], "7fb185837ec33a9491212264f7e41a12b6a8d9c6"
        )
        self.assertEqual(proof["head_sha"], proof["remote_head_sha"])
        self.assertEqual(proof["head_sha"], proof["CI_head_sha"])
        self.assertEqual(proof["CI_run_id"], 32_930_838_438)
        self.assertEqual(proof["base_python_job_id"], 98_062_624_957)
        self.assertEqual(proof["optional_neuro_readers_job_id"], 98_062_625_144)
        self.assertEqual(proof["CI_conclusion"], "success")

    def test_generated_schedule_and_adversarial_cases_are_exact(self) -> None:
        self.assertEqual(
            self.result["schedule"],
            {
                "held_out_prediction_sets": 102,
                "model_inference_runs": 258,
                "parameter_update_fits": 330,
                "post_target_updates": 0,
                "prediction_rows": 2_040,
                "synthetic_scores": 1,
                "synthetic_target_deliveries": 1,
            },
        )
        cases = self.result["cases"]
        self.assertEqual(cases["EDF_fixed_header"]["malformed_cases_refused"], 8)
        self.assertTrue(cases["deterministic_feature_replay"])
        self.assertEqual(cases["target_delivery_before_freeze_refusals"], 1)
        self.assertEqual(cases["target_repeat_delivery_refusals"], 1)
        self.assertEqual(cases["prediction_tamper_refusals"], 1)
        self.assertEqual(
            cases["causal_spectral_feature"]["sha256"],
            "26568a6a11fc2c40d9f94a2d366d18272577d78f680ba61630ba1ee33e143c88",
        )

    def test_measurements_are_bounded_and_causality_is_explicit(self) -> None:
        measurements = self.result["measurements"]
        caps = experiment.GENERATED_QUALIFICATION_CAPS
        self.assertLessEqual(
            measurements["runtime_seconds"], caps["runtime_seconds_maximum"]
        )
        self.assertLessEqual(
            measurements["peak_process_tree_RSS_bytes"],
            caps["peak_process_tree_RSS_bytes_maximum"],
        )
        self.assertLessEqual(
            measurements["generated_input_bytes"],
            caps["generated_input_bytes_maximum"],
        )
        self.assertLessEqual(
            measurements["private_temporary_prediction_bytes"],
            caps["private_temporary_bytes_maximum"],
        )
        self.assertEqual(measurements["public_output_bytes"], RESULT_BYTES)
        self.assertTrue(measurements["producer_causal"])
        self.assertEqual(measurements["required_context_seconds"], 1.0)
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
        self.assertEqual(
            self.result["synthetic_router"]["scientific_value"],
            "none_generated_positive_control_only",
        )

    def test_consumed_result_refuses_before_remote_or_numerical_work(self) -> None:
        previous = {name: os.environ.get(name) for name in experiment.THREAD_ENVIRONMENT}
        proof_calls = 0

        def unexpected_proof(_root: str | Path) -> dict[str, object]:
            nonlocal proof_calls
            proof_calls += 1
            raise AssertionError("remote proof must remain unopened on no-clobber refusal")

        try:
            for name in experiment.THREAD_ENVIRONMENT:
                os.environ[name] = "1"
            with self.assertRaises(experiment.DreyerExperimentRefusal):
                experiment.run_generated_qualification(
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
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("Stage G is consumed and must not be rerun", text)
        self.assertIn("Stage H", text)


if __name__ == "__main__":
    unittest.main()
