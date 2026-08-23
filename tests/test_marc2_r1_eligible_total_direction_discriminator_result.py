import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_result.v0.json"
)
IMPLEMENTATION = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_implementation.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_R1_ELIGIBLE_TOTAL_DIRECTION_DISCRIMINATOR_IMPLEMENTATION.md"
)


class Marc2R1EligibleTotalDirectionDiscriminatorResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.implementation = json.loads(IMPLEMENTATION.read_text(encoding="utf-8"))

    def test_result_identity_and_proof_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR31A")
        self.assertEqual(self.result["route"], "MARC2VR31A-G1")
        self.assertEqual(
            self.result["proof"]["registration_commit"],
            "eeab6785b8eadc6d65199fa1ac519173f9c160c7",
        )
        self.assertEqual(
            self.result["proof"]["registration_CI_run_id"],
            32_626_878_097,
        )

    def test_matrix_counts_are_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR29A_calls"], 32)
        self.assertEqual(matrix["R1_direction_comparisons"], 8)
        self.assertEqual(matrix["immutable_threshold_predicates"], 1)
        self.assertEqual(
            matrix["VR31A_route_counts"],
            {
                "MARC2VR31A-G1": 4,
                "MARC2VR31A-G2": 4,
                "MARC2VR31A-R1": 4,
                "MARC2VR31A-R2": 4,
                "MARC2VR31A-R3": 16,
            },
        )
        self.assertEqual(matrix["direct_refusals_passed"], 78)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertFalse(matrix["observed_total_or_difference_retained"])

    def test_resources_are_within_contract(self):
        measurements = self.result["measurements"]
        self.assertEqual(measurements["generated_input_bytes"], 14_137_216)
        self.assertEqual(measurements["aggregate_output_bytes"], 2_957)
        self.assertEqual(measurements["retained_output_bytes"], 0)
        self.assertLess(measurements["runtime_seconds"], 30)
        self.assertLess(measurements["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)

    def test_all_forbidden_operation_counters_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )

    def test_implementation_record_matches_result(self):
        qualification = self.implementation["qualification"]
        self.assertEqual(qualification["route"], self.result["route"])
        self.assertEqual(
            qualification["VR31A_route_counts"],
            self.result["matrix"]["VR31A_route_counts"],
        )
        self.assertEqual(
            self.implementation["resources"]["generated_input_bytes"],
            self.result["measurements"]["generated_input_bytes"],
        )
        self.assertIsNone(self.implementation["remote_implementation_proof"])

    def test_human_result_states_both_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("78 direct refusals", text)
        self.assertIn("never returned, logged, hashed, serialized, or retained", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
