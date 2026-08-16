import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_vr2_refusal_localization_result.v0.json"


class Marc2Vr2RefusalLocalizationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_result_identity_and_route_are_exact(self):
        self.assertEqual(self.result["lane_id"], "MARC2-VR5A")
        self.assertEqual(self.result["route"], "MARC2VR5-R2")
        self.assertEqual(
            self.result["status"],
            "completed_artifact_only_VR2_refusal_localization_pending_remote_green",
        )

    def test_every_bound_artifact_hash_matches(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(".codex_work", binding["path"])
                path = ROOT / binding["path"]
                self.assertTrue(path.is_file())
                self.assertEqual(
                    hashlib.sha256(path.read_bytes()).hexdigest(),
                    binding["sha256"],
                )

    def test_wrapper_diagnostic_does_not_invent_nested_route(self):
        diagnostic = self.result["wrapper_diagnostic"]
        self.assertTrue(diagnostic["collapse_proven"])
        self.assertEqual(diagnostic["diagnostic_classes_before_catch"], 8)
        self.assertEqual(diagnostic["diagnostic_classes_after_catch"], 1)
        self.assertFalse(diagnostic["nested_route_preserved"])
        accounting = self.result["route_accounting"]
        self.assertEqual(accounting["nested_routes_accounted_for"], 8)
        self.assertFalse(accounting["observed_nested_route_available"])
        self.assertFalse(accounting["observed_nested_route_inferred"])

    def test_selection_overconstraint_and_generated_semantics_are_exact(self):
        diagnostic = self.result["selection_contract_diagnostic"]
        self.assertTrue(diagnostic["live_selection_overconstraint_proven"])
        self.assertEqual(diagnostic["exact_generated_field_count"], 9)
        self.assertEqual(diagnostic["generated_selected_subjects"], 16)
        self.assertEqual(
            diagnostic["generated_selected_reservation_bytes"], 8105207776
        )
        self.assertFalse(diagnostic["dynamic_live_subject_count_accepted"])
        self.assertFalse(diagnostic["dynamic_live_reservation_bytes_accepted"])
        self.assertFalse(diagnostic["live_source_semantics_preserved"])

    def test_measurements_and_forbidden_counters_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_artifact_count"], 12)
        self.assertLessEqual(measured["input_bytes"], 1024**2)
        self.assertLess(measured["peak_RSS_bytes"], 128 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))

    def test_repair_requires_new_lane_and_new_Tier_C_decision(self):
        repair = self.result["prospective_repair"]
        self.assertTrue(repair["new_lane_required"])
        self.assertFalse(repair["patch_or_reuse_consumed_VR4P"])
        self.assertTrue(repair["preserve_nested_VR2_route_in_aggregate_failure"])
        self.assertFalse(repair["preserve_nested_reason_or_private_value"])
        self.assertTrue(
            repair["future_private_read_requires_new_Tier_C_packet_and_decision"]
        )

    def test_claim_boundary_remains_zero(self):
        claim = self.result["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
