from __future__ import annotations

import copy
import importlib.util
import math
import os
import unittest
from pathlib import Path

from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_shortcut_fixtures as fixtures

ROOT = Path(__file__).resolve().parents[1]
HAS_CLASSICAL = (
    importlib.util.find_spec("numpy") is not None
    and importlib.util.find_spec("sklearn") is not None
)


@unittest.skipUnless(HAS_CLASSICAL, "requires optional classical stack")
class CommP0GeneratedShortcutFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.update(fixtures.thread_environment())
        cls.contract = core.load_contract(ROOT)
        cls.first = fixtures.run_shortcut_fixture_matrix(cls.contract)
        cls.second = fixtures.run_shortcut_fixture_matrix(cls.contract)

    def test_all_seven_routes_execute_and_route_as_frozen(self) -> None:
        self.assertEqual(
            tuple(self.contract["numerical_schedule_per_replay"]["shortcut_fixtures"]),
            tuple(str(spec["route_id"]) for spec in fixtures.ROUTE_SPECS),
        )
        self.assertEqual(
            tuple(route.route_id for route in self.first.routes),
            tuple(str(spec["route_id"]) for spec in fixtures.ROUTE_SPECS),
        )
        self.assertTrue(self.first.routes[0].neural_evidence_gate_pass)
        self.assertTrue(all(not route.neural_evidence_gate_pass for route in self.first.routes[1:]))
        self.assertTrue(all(route.shortcut_control_identified for route in self.first.routes))
        for route in self.first.routes:
            self.assertEqual(
                route.neural_evidence_gate_pass,
                route.expected_neural_evidence_gate_pass,
            )

    def test_exact_fit_inference_score_and_firewall_counters(self) -> None:
        self.assertEqual(
            self.first.counters,
            {
                "prior_fits": 42,
                "residualizer_fits": 84,
                "classifier_fits": 630,
                "temperature_calibration_fits": 630,
                "model_inference_runs": 714,
                "prediction_sets": 1_428,
                "prediction_rows": 91_392,
                "target_deliveries": 14,
                "scores": 14,
                "post_target_updates": 0,
            },
        )
        for route in self.first.routes:
            self.assertEqual(route.source_label_rows_delivered, 1_536)
            self.assertEqual(route.held_out_label_rows_delivered, 0)
            self.assertEqual(route.model_received_trial_plan_objects, 0)
            self.assertEqual(route.model_received_target_vault_capabilities, 0)

    def test_two_complete_replays_are_deterministic(self) -> None:
        self.assertEqual(
            self.first.deterministic_payload_sha256,
            self.second.deterministic_payload_sha256,
        )
        self.assertEqual(self.first.deterministic_record(), self.second.deterministic_record())

    def test_route_substitution_is_refused(self) -> None:
        substituted = dict(fixtures.ROUTE_SPECS[1])
        substituted["diagnostic_condition"] = "microphone_only"
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "required_control_condition_missing_duplicated_or_substituted",
        ):
            fixtures.validate_route_spec(substituted)

    def test_malformed_and_target_bearing_features_are_refused(self) -> None:
        spec = fixtures.ROUTE_SPECS[0]
        rows = fixtures._opaque_trial_rows(str(spec["route_id"]), self.contract)
        records = [dict(record) for record in fixtures.build_feature_records(spec, rows)]
        malformed = copy.deepcopy(records)
        malformed[0]["central"] = [math.nan] * 8
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "prediction_probability_nonfinite_or_sum_mismatch",
        ):
            fixtures.validate_feature_records(malformed)
        leaked = copy.deepcopy(records)
        leaked[0]["target"] = 0
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal,
            "target_exposed_to_decoder_operator_freezer_or_language_context",
        ):
            fixtures.validate_feature_records(leaked)

    def test_one_surface_only_and_output_caps_are_enforced(self) -> None:
        for spec in fixtures.ROUTE_SPECS:
            rows = fixtures._opaque_trial_rows(str(spec["route_id"]), self.contract)
            first = fixtures.build_feature_records(spec, rows)
            second = fixtures.build_feature_records(spec, rows)
            self.assertEqual(first, second)
            self.assertEqual(len(first), 6 * 128)
            core.assert_target_free(first)
        self.assertLessEqual(self.first.public_output_bytes, fixtures.PUBLIC_OUTPUT_CAP_BYTES)
        self.assertEqual(
            self.first.public_output_bytes,
            len(core.canonical_json_bytes(self.first.public_record())),
        )
        self.assertLessEqual(
            self.first.runtime_seconds,
            float(self.contract["resource_caps"]["wall_time_seconds"]),
        )
        self.assertEqual(self.first.CPU_threads, 1)
        self.assertEqual(self.first.workers, 1)
        self.assertEqual(self.first.numerical_jobs, 1)
        self.assertEqual(self.first.network_bytes, 0)
        self.assertEqual(self.first.real_data_reads, 0)
        self.assertEqual(self.first.device_operations, 0)
        self.assertEqual(self.first.retained_generated_payload_bytes, 0)


if __name__ == "__main__":
    unittest.main()
