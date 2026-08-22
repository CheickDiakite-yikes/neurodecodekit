import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_f06_five_route_decomposition as vr23a
from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a


ROOT = Path(__file__).resolve().parents[1]
MEASURED_FRESH_PROCESS_RSS = 38_000_000


def qualify(**kwargs):
    return vr23a.qualify_generated(
        environment=vr23a.THREAD_ENVIRONMENT,
        peak_rss=lambda: MEASURED_FRESH_PROCESS_RSS,
        **kwargs,
    )


class Marc2F06FiveRouteDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = qualify()

    def test_plan_is_generated_only(self):
        plan = vr23a.build_plan()
        self.assertEqual(plan["paths"], 24)
        self.assertEqual(plan["VR20A_calls"], 24)
        self.assertEqual(plan["reachable_F06_classes"], 5)
        self.assertEqual(plan["non_independent_defensive_guards"], 2)
        self.assertFalse(plan["private_executor_available"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_static_inventory_and_redundancy_proofs_pass(self):
        proof = self.report["static_proof"]
        self.assertEqual(proof["VR20A_F06_wrapper_call_sites"], 2)
        self.assertEqual(proof["VR2_bound_safe_reasons"], 7)
        self.assertEqual(proof["non_independent_defensive_reasons"], 2)
        self.assertTrue(proof["eligible_count_implication_checked"])
        self.assertGreater(proof["known_taxonomy_classifications_checked"], 60)

    def test_matrix_routes_and_upstream_agreement_are_exact(self):
        matrix = self.report["matrix"]
        self.assertEqual(matrix["paths"], 24)
        self.assertEqual(matrix["VR20A_calls"], 24)
        self.assertEqual(
            matrix["VR23A_route_counts"],
            {"MARC2VR23A-G1": 4}
            | {f"MARC2VR23A-R{index}": 4 for index in range(1, 6)},
        )
        self.assertEqual(
            matrix["VR20A_route_counts"],
            {"MARC2VR20A-F06": 20, "MARC2VR20A-G1": 4},
        )
        self.assertEqual(matrix["source_mutations_after_call"], 0)
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 60)

    def test_each_generated_case_hits_its_exact_route(self):
        expected = ["MARC2VR23A-G1"] + [
            f"MARC2VR23A-R{index}" for index in range(1, 6)
        ]
        for case, route in zip(vr23a.CASES, expected, strict=True):
            with self.subTest(case=case):
                source = vr23a._build_case(case, "canonical")
                observed, upstream = vr23a.discriminate_generated_source(source)
                self.assertEqual(observed, route)
                self.assertEqual(
                    upstream,
                    vr20a.SUCCESS_ROUTE
                    if route == vr23a.SUCCESS_ROUTE
                    else vr20a.REFUSAL_ROUTES[5],
                )

    def test_qualification_calls_unchanged_vr20a_once_per_path(self):
        original = vr20a.adapt_published_task_source
        calls = 0

        def counted(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        with mock.patch.object(vr20a, "adapt_published_task_source", counted):
            report = qualify()
        self.assertEqual(calls, 24)
        self.assertEqual(report["matrix"]["VR20A_calls"], 24)

    def test_replays_are_exact_and_source_is_immutable(self):
        matrix = self.report["matrix"]
        self.assertEqual(
            matrix["replay_source_hashes"][0],
            matrix["replay_source_hashes"][1],
        )
        self.assertEqual(matrix["replay_routes"][0], matrix["replay_routes"][1])
        source = vr23a._build_case("classification_arithmetic_drift", "canonical")
        before = vr20a.vr2._canonical_source_bytes(source)
        vr23a.discriminate_generated_source(source)
        self.assertEqual(vr20a.vr2._canonical_source_bytes(source), before)

    def test_contract_and_thread_drift_refuse(self):
        changed = copy.deepcopy(vr23a.load_registered_contract())
        changed["lane_id"] = "other"
        with self.assertRaises(vr23a.F06FiveRouteDecompositionRefusal):
            qualify(contract=changed)
        environment = dict(vr23a.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(vr23a.F06FiveRouteDecompositionRefusal):
            vr23a.qualify_generated(environment=environment)

    def test_measurements_and_zero_counters_obey_caps(self):
        measured = self.report["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 45)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 24 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in self.report["operation_counters"].values())
        )

    def test_public_report_has_no_private_fields(self):
        vr23a._assert_public_report_safe(self.report)
        for field in vr23a.PRIVATE_PAYLOAD_FIELDS:
            with self.subTest(field=field):
                with self.assertRaises(vr23a.F06FiveRouteDecompositionRefusal):
                    vr23a._assert_public_report_safe({field: "x"})

    def test_cli_has_no_override_surface_and_report_is_strict_json(self):
        with self.assertRaises(SystemExit):
            vr23a.main(["qualify", "--source", "/tmp/other"])
        payload = vr23a._canonical_json_bytes(self.report)
        self.assertEqual(json.loads(payload), self.report)


if __name__ == "__main__":
    unittest.main()
