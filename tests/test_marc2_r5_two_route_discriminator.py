import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_published_task_selector_repair as vr20a
from neurodecodekit.datasets import marc2_r5_two_route_discriminator as vr21a


ROOT = Path(__file__).resolve().parents[1]
MEASURED_FRESH_PROCESS_RSS = 32_636_928


def qualify(**kwargs):
    return vr21a.qualify_generated(
        environment=vr21a.THREAD_ENVIRONMENT,
        peak_rss=lambda: MEASURED_FRESH_PROCESS_RSS,
        **kwargs,
    )


class Marc2R5TwoRouteDiscriminatorTests(unittest.TestCase):
    def test_plan_is_generated_only(self):
        plan = vr21a.build_plan()
        self.assertEqual(plan["paths"], 12)
        self.assertEqual(plan["VR20A_calls"], 12)
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_qualification_routes_are_exact(self):
        report = qualify()
        self.assertEqual(report["route"], "MARC2VR21A-G1")
        matrix = report["matrix"]
        self.assertEqual(matrix["paths"], 12)
        self.assertEqual(matrix["VR20A_calls"], 12)
        self.assertEqual(
            matrix["VR21A_route_counts"],
            {
                "MARC2VR21A-G1": 4,
                "MARC2VR21A-R1": 4,
                "MARC2VR21A-R2": 4,
            },
        )
        self.assertEqual(
            matrix["VR20A_route_counts"],
            {
                "MARC2VR20A-F06": 4,
                "MARC2VR20A-F07": 4,
                "MARC2VR20A-G1": 4,
            },
        )
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 40)

    def test_each_matrix_path_calls_vr20a_once(self):
        original = vr20a.adapt_published_task_source
        calls = 0

        def counted(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        with mock.patch.object(vr20a, "adapt_published_task_source", counted):
            report = qualify()
        self.assertEqual(calls, 12)
        self.assertEqual(report["matrix"]["VR20A_calls"], 12)

    def test_witnesses_hit_f06_and_f07(self):
        taxonomy = vr21a._build_case("unknown_participant_taxonomy", "canonical")
        selection = vr21a._build_case("semantic_run_zero", "canonical")
        self.assertEqual(
            vr21a.discriminate_generated_source(taxonomy),
            ("MARC2VR21A-R1", "MARC2VR20A-F06"),
        )
        self.assertEqual(
            vr21a.discriminate_generated_source(selection),
            ("MARC2VR21A-R2", "MARC2VR20A-F07"),
        )

    def test_replays_are_deterministic_and_source_immutable(self):
        first = qualify()
        second = qualify()
        self.assertEqual(
            first["matrix"]["replay_source_hashes"],
            second["matrix"]["replay_source_hashes"],
        )
        self.assertEqual(first["matrix"]["source_mutations_after_call"], 0)
        self.assertEqual(second["matrix"]["source_mutations_after_call"], 0)

    def test_contract_mutation_is_refused(self):
        contract = vr21a.load_registered_contract()
        changed = copy.deepcopy(contract)
        changed["lane_id"] = "other"
        with self.assertRaises(vr21a.R5TwoRouteDiscriminatorRefusal) as caught:
            qualify(
                contract=changed,
            )
        self.assertEqual(caught.exception.route, "MARC2VR21A-F01")

    def test_thread_drift_is_refused(self):
        environment = dict(vr21a.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(vr21a.R5TwoRouteDiscriminatorRefusal) as caught:
            vr21a.qualify_generated(environment=environment)
        self.assertEqual(caught.exception.route, "MARC2VR21A-F06")

    def test_unknown_upstream_route_is_refused(self):
        with self.assertRaises(vr21a.R5TwoRouteDiscriminatorRefusal) as caught:
            vr21a._map_upstream_route("MARC2VR20A-F05")
        self.assertEqual(caught.exception.route, "MARC2VR21A-F03")

    def test_private_payload_fields_are_refused(self):
        for field in vr21a.PRIVATE_PAYLOAD_FIELDS:
            with self.subTest(field=field):
                with self.assertRaises(vr21a.R5TwoRouteDiscriminatorRefusal):
                    vr21a._assert_public_report_safe({field: "x"})

    def test_measurements_and_zero_counters_obey_caps(self):
        report = qualify()
        measured = report["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in report["operation_counters"].values()))

    def test_cli_has_no_override_surface(self):
        with self.assertRaises(SystemExit):
            vr21a.main(["qualify", "--source", "/tmp/other"])

    def test_report_is_strict_json(self):
        report = qualify()
        payload = vr21a._canonical_json_bytes(report)
        self.assertEqual(json.loads(payload), report)


if __name__ == "__main__":
    unittest.main()
