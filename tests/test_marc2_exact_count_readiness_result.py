import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "registries/marc2_exact_count_readiness_repair_result.v0.json"
IMPLEMENTATION = (
    ROOT / "registries/marc2_exact_count_readiness_repair_implementation.v0.json"
)
DOC = ROOT / "docs/MARC_2_EXACT_COUNT_READINESS_REPAIR_IMPLEMENTATION.md"


class Marc2ExactCountReadinessResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION.read_text(encoding="utf-8")
        )

    def test_result_identity_and_registration_proof_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR33A")
        self.assertEqual(self.result["route"], "MARC2VR33A-G1")
        proof = self.result["proof"]
        self.assertEqual(
            proof["registration_commit"],
            "23adf07a328824d3b671e8fd8edf3c9b8d1f15ba",
        )
        self.assertEqual(proof["registration_CI_run_id"], 32_634_409_230)
        self.assertEqual(proof["registration_base_job_id"], 97_181_894_886)
        self.assertEqual(
            proof["registration_optional_neuro_job_id"], 97_181_895_045
        )

    def test_matrix_counts_are_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 16)
        self.assertEqual(matrix["provider_calls"], 48)
        self.assertEqual(matrix["sleeper_calls"], 32)
        self.assertEqual(matrix["returned_samples"], 48)
        self.assertEqual(matrix["ready_paths"], 2)
        self.assertEqual(matrix["not_ready_paths"], 14)
        self.assertEqual(matrix["ready_patterns"], ["PPP"])
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertEqual(matrix["direct_refusals_passed"], 67)

    def test_resources_are_within_contract(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["fixed_input_bytes"], 75_965)
        self.assertEqual(measurements["generated_input_bytes"], 4_136)
        self.assertEqual(measurements["aggregate_output_bytes"], 2_390)
        self.assertEqual(measurements["retained_output_bytes"], 0)
        self.assertLess(measurements["runtime_seconds"], 15)
        self.assertLess(measurements["peak_RSS_bytes"], 128 * 1024**2)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)

    def test_all_forbidden_operation_counters_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_implementation_record_matches_result_and_remote_proof(self):
        qualification = self.implementation["qualification"]
        self.assertEqual(qualification["route"], self.result["route"])
        self.assertEqual(
            qualification["provider_calls"],
            self.result["matrix"]["provider_calls"],
        )
        self.assertEqual(
            self.implementation["resources"]["generated_input_bytes"],
            self.result["measurements"]["generated_input_bytes"],
        )
        self.assertEqual(
            self.implementation["remote_implementation_proof"],
            self.result["remote_implementation_proof"],
        )

    def test_implementation_artifacts_match_exact_bytes(self):
        total = 0
        historical_roles = {"result_tests", "generated_result"}
        for item in self.implementation["implementation_artifacts"]:
            if item["role"] not in historical_roles:
                payload = (ROOT / item["path"]).read_bytes()
                self.assertEqual(len(payload), item["bytes"], item["path"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(),
                    item["sha256"],
                    item["path"],
                )
            total += item["bytes"]
        self.assertEqual(
            len(self.implementation["implementation_artifacts"]),
            self.implementation["implementation_artifact_count"],
        )
        self.assertEqual(total, self.implementation["implementation_artifact_bytes"])

    def test_human_result_states_both_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("67 direct refusals", text)
        self.assertIn("zero retained output", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
