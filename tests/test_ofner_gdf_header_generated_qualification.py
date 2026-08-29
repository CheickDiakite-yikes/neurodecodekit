from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/ofner_gdf_header_generated_qualification.v0.json"
DOCUMENT = ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_FIXED_HEADER_GENERATED_QUALIFICATION.md"


class OfnerGDFHeaderGeneratedQualificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_registration_basis_is_exact_and_green(self) -> None:
        green = self.result["green_registration_basis"]
        self.assertEqual(
            green["commit"], "25fe4521150a6441426d236eacbf5ab27d3bb12d"
        )
        self.assertEqual(green["CI_run_id"], 33_268_675_964)
        self.assertEqual(green["base_python_job_id"], 99_143_134_373)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_143_134_445)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertTrue(green["on_GitHub_main"])

    def test_implementation_artifact_hashes_are_exact(self) -> None:
        for artifact in self.result["implementation_artifacts"]:
            payload = (ROOT / artifact["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), artifact["sha256"])

    def test_measurements_satisfy_registered_caps(self) -> None:
        measurements = self.result["measurements"]
        self.assertEqual(measurements["generated_replays"], 2)
        self.assertEqual(measurements["generated_header_bytes_per_replay"], 24_832)
        self.assertEqual(measurements["combined_range_body_bytes_per_replay"], 24_832)
        self.assertEqual(measurements["named_adversarial_refusals"], 41)
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["peak_rss_bytes"], 268_435_456)
        self.assertEqual(measurements["network_bytes"], 0)
        self.assertEqual(measurements["retained_generated_payload_bytes"], 0)

    def test_parsed_header_is_exact_and_deterministic(self) -> None:
        parsed = self.result["parsed_header"]
        self.assertEqual(parsed["number_of_signals"], 96)
        self.assertEqual(parsed["sampling_rate_hz"], 512)
        self.assertEqual(
            [
                parsed["EEG_channels"],
                parsed["EOG_channels"],
                parsed["glove_channels"],
                parsed["arm_channels"],
            ],
            [61, 3, 19, 13],
        )
        self.assertEqual(parsed["unique_normalized_labels"], 96)
        self.assertTrue(self.result["determinism"]["replay_summaries_equal"])
        self.assertTrue(self.result["determinism"]["transcript_digests_equal"])

    def test_refusal_coverage_and_capability_absences_are_explicit(self) -> None:
        refusal_ids = self.result["refusal_ids"]
        self.assertEqual(len(refusal_ids), 41)
        self.assertEqual(len(set(refusal_ids)), 41)
        capabilities = self.result["capabilities"]
        self.assertTrue(capabilities["GDF_2x_header_parser_present"])
        self.assertTrue(capabilities["two_range_firewall_present"])
        for key in (
            "network_client_present",
            "real_execution_command_present",
            "event_parser_present",
            "signal_parser_present",
            "model_or_scorer_present",
        ):
            self.assertFalse(capabilities[key], key)

    def test_no_real_or_scientific_operation_occurred(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("fresh packet-bound maintainer decision", document)


if __name__ == "__main__":
    unittest.main()
