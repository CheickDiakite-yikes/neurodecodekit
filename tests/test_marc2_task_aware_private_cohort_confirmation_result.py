import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = json.loads(
    (
        ROOT
        / "registries/marc2_task_aware_private_cohort_confirmation_result.v0.json"
    ).read_text(encoding="utf-8")
)
IMPLEMENTATION = json.loads(
    (
        ROOT
        / "registries/marc2_task_aware_private_cohort_confirmation_implementation.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT / "docs/MARC_2_TASK_AWARE_PRIVATE_COHORT_CONFIRMATION_IMPLEMENTATION.md"
).read_text(encoding="utf-8")


class TaskAwarePrivateCohortResultTests(unittest.TestCase):
    def test_identity_and_single_qualification_are_exact(self):
        self.assertEqual(RESULT["lane_id"], "MARC2-VR36P")
        self.assertEqual(RESULT["route"], "MARC2VR36P-G1")
        self.assertEqual(RESULT["qualification_invocations"], 1)
        self.assertFalse(RESULT["qualification_may_be_repeated"])
        self.assertEqual(
            RESULT["proof"]["decision_commit"],
            "fd08dd6ee40b16d3b4f4312601fed3370b7e2ca5",
        )
        self.assertEqual(RESULT["proof"]["decision_CI_run_id"], 32_648_347_577)

    def test_matrix_and_route_counts_are_exact(self):
        matrix = RESULT["matrix"]
        self.assertEqual(matrix["paths"], 40)
        self.assertEqual(matrix["VR33A_calls"], 40)
        self.assertEqual(matrix["readiness_provider_calls"], 120)
        self.assertEqual(matrix["readiness_sleeper_calls"], 80)
        self.assertEqual(matrix["source_constructions"], 20)
        self.assertEqual(matrix["source_content_opens"], 20)
        self.assertEqual(matrix["VR35A_calls"], 20)
        self.assertEqual(matrix["cohort_file_writes"], 8)
        self.assertEqual(
            matrix["VR36P_route_counts"],
            {
                "MARC2VR36P-R1": 4,
                "MARC2VR36P-R2": 4,
                "MARC2VR36P-R3": 4,
                "MARC2VR36P-R4": 4,
                "MARC2VR36P-R5": 4,
                "MARC2VR36P-R6": 20,
            },
        )
        self.assertEqual(set(matrix["VR35A_route_counts"].values()), {4})

    def test_replay_firewalls_and_refusals_passed(self):
        matrix = RESULT["matrix"]
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["fixed_path_state_machine_qualified"])
        self.assertTrue(matrix["marker_preceded_every_source_construction_and_open"])
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertEqual(matrix["nonpassing_readiness_source_constructions"], 0)
        self.assertEqual(matrix["nonpassing_readiness_VR35A_calls"], 0)
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 100)

    def test_resources_and_zero_retention_are_within_caps(self):
        measured = RESULT["measurements"]
        self.assertEqual(measured["fixed_input_bytes"], 211_512)
        self.assertEqual(measured["generated_input_bytes"], 8_847_228)
        self.assertLess(measured["runtime_seconds"], 90)
        self.assertLess(measured["peak_RSS_bytes"], 268_435_456)
        self.assertLessEqual(measured["peak_incremental_output_bytes"], 2_097_152)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(measured["network_bytes"], 0)
        self.assertEqual(measured["new_payload_bytes"], 0)

    def test_all_private_and_scientific_operations_are_zero(self):
        self.assertTrue(all(value == 0 for value in RESULT["operation_counters"].values()))
        claims = RESULT["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_implementation_artifacts_match_exact_hashes(self):
        for row in IMPLEMENTATION["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_private_execute_proof_transition_preserves_boundaries(self):
        proof = IMPLEMENTATION["remote_implementation_proof"]
        if proof is None:
            self.assertFalse(IMPLEMENTATION["private_execution_authorized_now"])
        else:
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(proof["scope_changed_after_qualification"])
            self.assertEqual(proof["qualification_route"], "MARC2VR36P-G1")
            self.assertFalse(proof["qualification_repeated_for_proof_closeout"])
            self.assertEqual(proof["private_operations_during_proof_closeout"], 0)
        self.assertEqual(IMPLEMENTATION["qualification_invocations"], 1)
        self.assertFalse(IMPLEMENTATION["qualification_may_be_repeated"])

    def test_document_states_engineering_and_scientific_boundaries(self):
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("may not be repeated", DOC)
        self.assertIn("MARC2VR36P-F02", DOC)


if __name__ == "__main__":
    unittest.main()
