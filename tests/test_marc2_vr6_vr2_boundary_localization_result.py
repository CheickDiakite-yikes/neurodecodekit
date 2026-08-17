import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries/marc2_vr6_vr2_boundary_localization_result.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_VR6_VR2_BOUNDARY_LOCALIZATION_IMPLEMENTATION.md"


class Marc2Vr6Vr2BoundaryLocalizationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_route_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_vr6_vr2_boundary_localization_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR8A")
        self.assertEqual(self.result["route"], "MARC2VR8A-R1")
        self.assertEqual(
            self.result["status"],
            "completed_artifact_only_VR6_to_VR2_boundary_localization_remotely_green",
        )

    def test_exact_implementation_is_remotely_green(self):
        verification = self.result["verification"]
        self.assertFalse(verification["remote_CI_pending"])
        proof = verification["remote_proof"]
        self.assertEqual(
            proof["commit"], "1addd5df9fdccda6e716f71f9e6624f199677713"
        )
        self.assertEqual(proof["CI_run_id"], 31_986_089_529)
        self.assertEqual(proof["base_python_job_id"], 95_261_271_737)
        self.assertEqual(proof["optional_neuro_job_id"], 95_261_271_709)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_bound_artifact_hash_matches(self):
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
        self.assertGreaterEqual(len(seen), 7)

    def test_envelope_is_excluded_but_private_route_is_not_invented(self):
        localization = self.result["localization_result"]
        self.assertTrue(localization["VR2_F02_envelope_route_excluded"])
        self.assertEqual(
            localization["remaining_compatible_VR2_routes"],
            ["MARC2VR2-F03", "MARC2VR2-F04"],
        )
        self.assertFalse(localization["exact_private_F03_or_F04_route_available"])
        self.assertFalse(localization["exact_private_predicate_or_value_available"])

    def test_nested_route_loss_and_fixture_gap_are_explicit(self):
        relay = self.result["route_relay"]
        self.assertTrue(relay["VR6_stores_nested_allowlisted_VR2_route"])
        self.assertTrue(relay["VR7P_forwards_only_outer_VR6_route"])
        self.assertTrue(relay["nested_route_relay_loss_proven"])
        self.assertFalse(relay["nested_reason_or_private_context_preserved"])
        fixture = self.result["fixture_boundary"]
        self.assertEqual(fixture["VR2_generated_success_rows"], 1_227)
        self.assertEqual(fixture["exact_producer_generated_fixture_rows"], 18)
        self.assertFalse(fixture["full_scale_producer_to_VR2_fixture_exists"])

    def test_measurements_and_acceptance_gates_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_artifact_count"], 18)
        self.assertEqual(measured["input_bytes"], 587_523)
        self.assertEqual(measured["Python_AST_parses"], 7)
        self.assertEqual(measured["strict_JSON_parses"], 11)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_forbidden_operations_and_scientific_claims_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )
        claim = self.result["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])

    def test_next_repair_and_document_boundary_are_explicit(self):
        repair = self.result["prospective_repair"]
        self.assertTrue(repair["new_generated_only_lane_required"])
        self.assertTrue(repair["preserve_outer_VR6_route_code"])
        self.assertTrue(repair["preserve_nested_allowlisted_VR2_route_code"])
        self.assertFalse(repair["preserve_reason_private_value_or_context"])
        self.assertFalse(repair["relax_F03_or_F04_before_observed_route"])
        self.assertTrue(repair["future_private_read_requires_new_Tier_C_decision"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("Do not relax F03 or F04 yet", text)


if __name__ == "__main__":
    unittest.main()
