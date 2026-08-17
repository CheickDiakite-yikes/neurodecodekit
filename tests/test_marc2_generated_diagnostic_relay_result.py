import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_generated_diagnostic_relay_result.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_GENERATED_DIAGNOSTIC_RELAY_RESULT.md"
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_generated_diagnostic_relay_implementation.v0.json"
)


class Marc2GeneratedDiagnosticRelayResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )

    def test_identity_route_and_proof_posture_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_generated_diagnostic_relay_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR8B")
        self.assertEqual(self.result["result_id"], "MARC2VR8B-G1")
        self.assertEqual(self.result["route"], "MARC2VR8B-G1")
        self.assertIn(
            self.result["status"],
            {
                "completed_generated_only_full_scale_diagnostic_relay_remote_proof_pending",
                "completed_generated_only_full_scale_diagnostic_relay_remotely_green",
            },
        )
        self.assertIn("no_private_or_scientific_value", self.result["proof_posture"])

    def test_every_bound_artifact_size_and_hash_matches(self):
        seen = set()
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                payload = path.read_bytes()
                self.assertEqual(len(payload), binding["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), binding["sha256"])
        self.assertEqual(len(seen), 8)

    def test_route_matrix_preserves_outer_and_nested_codes_only(self):
        matrix = self.result["route_matrix"]
        self.assertEqual(
            [row["case"] for row in matrix],
            ["success", "F02", "F03", "F04"],
        )
        self.assertEqual(matrix[0]["selected_subject_count"], 16)
        self.assertEqual(matrix[0]["selected_run_bundles"], 96)
        for row, nested in zip(
            matrix[1:],
            ("MARC2VR2-F02", "MARC2VR2-F03", "MARC2VR2-F04"),
            strict=True,
        ):
            self.assertEqual(
                set(row),
                {"case", "disposition", "outer_VR6_route", "nested_VR2_route"},
            )
            self.assertEqual(row["outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["nested_VR2_route"], nested)

    def test_order_sensitive_provenance_is_separate_from_cohort_identity(self):
        replay = self.result["replay_and_identity"]
        self.assertFalse(replay["upstream_VR6_provenance_hash_equal_across_orders"])
        self.assertTrue(
            replay["normalized_generated_cohort_identity_equal_across_orders"]
        )
        self.assertEqual(
            replay["normalized_selection_identity_sha256"],
            "812ecbe8f402ae49eab22f166964390b8024639e0afc8b793f9fe89105f20923",
        )
        self.assertTrue(replay["route_and_mechanics_replay_byte_identical"])
        self.assertEqual(replay["exact_replays"], 2)

    def test_mechanics_and_resource_measurements_are_bounded(self):
        mechanics = self.result["mechanics"]
        self.assertEqual(mechanics["entry_count_each_path"], 1_227)
        self.assertEqual(mechanics["exact_parser_entry_visits_total"], 19_632)
        self.assertEqual(mechanics["member_local_header_bytes"], 0)
        self.assertEqual(mechanics["member_payload_bytes"], 0)
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 4_650_480)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_all_gates_refusals_and_zero_counters_pass(self):
        self.assertTrue(all(self.result["acceptance_gates"].values()))
        refusals = self.result["direct_refusals"]
        self.assertEqual(refusals["count"], 29)
        self.assertEqual(sum(refusals["routes"].values()), 29)
        self.assertEqual(len(refusals["required_mutations"]), 29)
        self.assertTrue(refusals["all_six_routes_covered"])
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )

    def test_remote_proof_state_is_honest(self):
        verification = self.result["verification"]
        implementation = self.implementation["qualification"]
        if verification["remote_CI_pending"]:
            self.assertIsNone(verification["remote_proof"])
            self.assertTrue(implementation["remote_CI_pending"])
            self.assertFalse(implementation["complete_local_suites_pending"])
        else:
            proof = verification["remote_proof"]
            self.assertIsInstance(proof, dict)
            self.assertTrue(proof["both_required_jobs_green"])
            self.assertFalse(implementation["remote_CI_pending"])

    def test_complete_local_suites_add_exactly_twenty_one_tests(self):
        verification = self.result["verification"]
        implementation = self.implementation["qualification"]
        self.assertFalse(verification["complete_local_suites_pending"])
        self.assertTrue(verification["complete_repository_fresh_process_split_passed"])
        self.assertEqual(verification["dependency_light_tests"], 3_948)
        self.assertEqual(verification["complete_optional_tests"], 4_019)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertEqual(verification["tests_added_after_green_registration"], 21)
        self.assertEqual(verification["new_failures_versus_registration_baseline"], 0)
        self.assertTrue(verification["all_three_exact_isolated_reruns_passed"])
        self.assertEqual(
            implementation["tests_added_after_green_registration"], 21
        )

    def test_claim_boundary_and_human_result_are_explicit(self):
        claim = self.result["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("does not reveal whether", text)


if __name__ == "__main__":
    unittest.main()
