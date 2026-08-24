import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = json.loads(
    (
        ROOT / "registries/marc2_selection_sufficiency_private_cohort_freeze_result.v0.json"
    ).read_text(encoding="utf-8")
)


class SelectionSufficiencyPrivateCohortFreezeResultTests(unittest.TestCase):
    def test_identity_and_single_qualification_are_exact(self):
        self.assertEqual(RESULT["lane_id"], "MARC2-VR39P")
        self.assertEqual(RESULT["route"], "MARC2VR39P-G1")
        self.assertEqual(RESULT["qualification_invocations"], 1)
        self.assertFalse(RESULT["qualification_may_be_repeated"])
        self.assertEqual(
            RESULT["proof"]["decision_commit"],
            "dbde5f84b3fac0ac0b23208afd56e00d678aff00",
        )
        self.assertEqual(RESULT["proof"]["decision_CI_run_id"], 32_681_510_484)

    def test_matrix_and_route_counts_are_exact(self):
        matrix = RESULT["matrix"]
        self.assertEqual(matrix["paths"], 168)
        self.assertEqual(matrix["VR33A_calls"], 168)
        self.assertEqual(matrix["readiness_provider_calls"], 504)
        self.assertEqual(matrix["readiness_sleeper_calls"], 336)
        self.assertEqual(matrix["source_constructions"], 84)
        self.assertEqual(matrix["source_content_opens"], 84)
        self.assertEqual(matrix["VR38A_calls"], 84)
        self.assertEqual(matrix["cohort_file_writes"], 64)
        self.assertEqual(
            matrix["VR39P_route_counts"],
            {"MARC2VR39P-R1": 64, "MARC2VR39P-R2": 104},
        )
        self.assertEqual(
            matrix["VR38A_route_counts"],
            {
                "MARC2VR38A-G1": 36,
                "MARC2VR38A-G2": 32,
                "MARC2VR38A-R1": 8,
                "MARC2VR38A-R2": 4,
                "MARC2VR38A-R3": 4,
            },
        )

    def test_replay_ordering_and_refusal_evidence_passed(self):
        matrix = RESULT["matrix"]
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["fixed_path_state_machine_qualified"])
        self.assertTrue(matrix["marker_preceded_every_source_construction_and_open"])
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertEqual(matrix["nonpassing_readiness_source_constructions"], 0)
        self.assertEqual(matrix["nonpassing_readiness_VR38A_calls"], 0)
        self.assertEqual(matrix["direct_refusals_passed"], 268)
        self.assertEqual(len(matrix["critical_refusal_witness_class_counts"]), 12)
        self.assertEqual(set(matrix["critical_refusal_witness_class_counts"].values()), {1})

    def test_resources_and_zero_retention_are_within_caps(self):
        measured = RESULT["measurements"]
        self.assertEqual(measured["fixed_input_bytes"], 374_043)
        self.assertLessEqual(measured["generated_input_bytes"], 67_108_864)
        self.assertLess(measured["runtime_seconds"], 120)
        self.assertLess(measured["peak_RSS_bytes"], 268_435_456)
        self.assertLessEqual(measured["peak_incremental_output_bytes"], 2_097_152)
        self.assertLessEqual(measured["peak_materialized_case_bytes"], 69_206_016)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["new_payload_bytes"], 0)

    def test_every_private_and_scientific_operation_is_zero(self):
        self.assertTrue(all(value == 0 for value in RESULT["operation_counters"].values()))
        claims = RESULT["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_measurements_report_no_model_or_latency_result(self):
        measured = RESULT["measurements"]
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])


if __name__ == "__main__":
    unittest.main()
