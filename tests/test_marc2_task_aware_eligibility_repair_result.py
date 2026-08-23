import ast
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT / "registries/marc2_task_aware_eligibility_repair_result.v0.json"
)
IMPLEMENTATION = (
    ROOT / "registries/marc2_task_aware_eligibility_repair_implementation.v0.json"
)
MODULE = (
    ROOT
    / "src/neurodecodekit/datasets/marc2_task_aware_eligibility_repair.py"
)
DOC = ROOT / "docs/MARC_2_TASK_AWARE_ELIGIBILITY_REPAIR_IMPLEMENTATION.md"


class Marc2TaskAwareEligibilityRepairResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION.read_text(encoding="utf-8")
        )

    def test_result_identity_and_single_invocation_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR35A")
        self.assertEqual(
            self.result["status"],
            "generated_task_aware_repair_qualified_no_private_access",
        )
        self.assertEqual(self.result["qualification_invocations"], 1)
        self.assertFalse(self.result["qualification_may_be_repeated"])

    def test_registration_proof_preceded_implementation(self):
        proof = self.result["registration_proof"]
        self.assertEqual(
            proof["commit"], "aa4c39a5ce8ca04627c9252600971ee878f20e3e"
        )
        self.assertEqual(proof["CI_run_id"], 32_643_351_246)
        self.assertEqual(proof["base_job_id"], 97_203_738_713)
        self.assertEqual(proof["optional_neuro_job_id"], 97_203_738_637)

    def test_generated_matrix_passed_exactly(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 20)
        self.assertEqual(
            matrix["route_counts"],
            {
                "MARC2VR35A-G1": 4,
                "MARC2VR35A-G2": 4,
                "MARC2VR35A-R1": 4,
                "MARC2VR35A-R2": 4,
                "MARC2VR35A-R3": 4,
            },
        )
        self.assertEqual(matrix["selection_calls"], 8)
        self.assertEqual(matrix["selection_validation_calls"], 8)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["source_immutability_checks"], 20)

    def test_mixed_task_repair_preserves_target_cohort(self):
        matrix = self.result["matrix"]
        repair = self.result["repair"]
        self.assertTrue(matrix["mixed_task_semantic_cohort_matches_baseline"])
        self.assertEqual(matrix["non_target_selected_rows"], 0)
        self.assertTrue(repair["task_projection_precedes_eligibility_arithmetic"])
        self.assertTrue(repair["mixed_task_surplus_removed"])
        self.assertTrue(repair["genuine_target_task_surplus_distinguished"])
        self.assertTrue(repair["genuine_target_task_deficit_distinguished"])

    def test_resources_are_within_frozen_caps(self):
        measurements = self.result["measurements"]
        self.assertLess(measurements["runtime_seconds"], 45)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measurements["generated_input_bytes"], 16 * 1024**2)
        self.assertLessEqual(measurements["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measurements["retained_output_bytes"], 0)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)

    def test_every_private_or_scientific_counter_is_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        measurements = self.result["measurements"]
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)

    def test_direct_refusal_minimum_passed(self):
        refusals = self.result["refusals"]
        self.assertEqual(refusals["direct_refusals"], 99)
        self.assertGreaterEqual(refusals["direct_refusals"], 80)

    def test_module_exposes_no_private_execution_command(self):
        source = MODULE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        parser_functions = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_parser"
        ]
        self.assertEqual(len(parser_functions), 1)
        segment = ast.get_source_segment(source, parser_functions[0])
        self.assertIsNotNone(segment)
        self.assertIn('choices=("plan", "qualify")', segment)
        self.assertNotIn('"execute"', segment)

    def test_implementation_artifacts_match_exact_bytes(self):
        total = 0
        for row in self.implementation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            total += len(payload)
        self.assertEqual(
            total, self.implementation["implementation_artifact_bytes"]
        )

    def test_remote_proof_and_private_next_gate_remain_closed(self):
        self.assertIsNone(self.result["remote_implementation_proof"])
        self.assertIsNone(self.implementation["remote_implementation_proof"])
        gate = self.result["next_gate"]
        self.assertTrue(gate["proof_only_closeout_required_after_green"])
        self.assertFalse(
            gate["private_execution_or_consumed_lane_reinspection_authorized"]
        )
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
