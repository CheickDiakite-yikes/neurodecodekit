import copy
import json
import unittest
from unittest import mock

from neurodecodekit.datasets import marc2_r5_inventory_taxonomy_discriminator as vr27a
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a


MEASURED_FRESH_PROCESS_RSS = 40_000_000


def qualify(**kwargs):
    return vr27a.qualify_generated(
        environment=vr27a.THREAD_ENVIRONMENT,
        peak_rss=lambda: MEASURED_FRESH_PROCESS_RSS,
        **kwargs,
    )


class Marc2R5InventoryTaxonomyDiscriminatorTests(unittest.TestCase):
    def test_plan_is_generated_only(self):
        plan = vr27a.build_plan()
        self.assertEqual(plan["paths"], 20)
        self.assertEqual(plan["VR25A_calls"], 20)
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_qualification_routes_are_exact(self):
        report = qualify()
        self.assertEqual(report["route"], "MARC2VR27A-G1")
        matrix = report["matrix"]
        self.assertEqual(matrix["paths"], 20)
        self.assertEqual(matrix["VR25A_calls"], 20)
        self.assertEqual(
            matrix["VR27A_route_counts"],
            {
                "MARC2VR27A-G1": 4,
                "MARC2VR27A-R1": 12,
                "MARC2VR27A-R2": 4,
            },
        )
        self.assertEqual(matrix["VR25A_route_counts"], {
            "MARC2VR25A-G1": 4,
            "MARC2VR25A-R1": 12,
            "MARC2VR25A-R2": 4,
        })
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 50)

    def test_each_matrix_path_calls_vr25a_once(self):
        original = vr25a.apply_selection_boundary_firewall
        calls = 0

        def counted(*args, **kwargs):
            nonlocal calls
            calls += 1
            return original(*args, **kwargs)

        with mock.patch.object(vr25a, "apply_selection_boundary_firewall", counted):
            report = qualify()
        self.assertEqual(calls, 20)
        self.assertEqual(report["matrix"]["VR25A_calls"], 20)

    def test_witnesses_hit_inventory_and_taxonomy_routes(self):
        for case in (
            "eligible_bundle_removed",
            "eligible_bundle_added",
            "eligible_distribution_shift",
        ):
            with self.subTest(case=case):
                source = vr27a._build_case(case, "canonical")
                self.assertEqual(
                    vr27a.discriminate_generated_source(source),
                    ("MARC2VR27A-R1", "MARC2VR25A-R1"),
                )
        source = vr27a._build_case("unknown_participant_bundle", "canonical")
        self.assertEqual(
            vr27a.discriminate_generated_source(source),
            ("MARC2VR27A-R2", "MARC2VR25A-R2"),
        )

    def test_replays_are_deterministic_and_source_immutable(self):
        first = qualify()
        second = qualify()
        self.assertEqual(
            first["matrix"]["replay_digest"],
            second["matrix"]["replay_digest"],
        )
        self.assertTrue(first["matrix"]["exact_replays_match"])
        self.assertEqual(first["matrix"]["source_mutations_after_call"], 0)

    def test_contract_mutation_is_refused(self):
        changed = copy.deepcopy(vr27a.load_registered_contract())
        changed["lane_id"] = "other"
        with self.assertRaises(vr27a.R5InventoryTaxonomyDiscriminatorRefusal) as caught:
            qualify(contract=changed)
        self.assertEqual(caught.exception.route, "MARC2VR27A-F01")

    def test_thread_drift_is_refused(self):
        environment = dict(vr27a.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(vr27a.R5InventoryTaxonomyDiscriminatorRefusal) as caught:
            vr27a.qualify_generated(environment=environment)
        self.assertEqual(caught.exception.route, "MARC2VR27A-F06")

    def test_unknown_upstream_route_is_refused(self):
        with self.assertRaises(vr27a.R5InventoryTaxonomyDiscriminatorRefusal) as caught:
            vr27a._map_upstream_route("MARC2VR25A-G2")
        self.assertEqual(caught.exception.route, "MARC2VR27A-F03")

    def test_private_payload_fields_are_refused(self):
        for field in vr27a.PRIVATE_PAYLOAD_FIELDS:
            with self.subTest(field=field):
                with self.assertRaises(
                    vr27a.R5InventoryTaxonomyDiscriminatorRefusal
                ):
                    vr27a._assert_public_report_safe({field: "x"})

    def test_measurements_and_zero_counters_obey_caps(self):
        report = qualify()
        measured = report["measurements"]
        self.assertLessEqual(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["generated_input_bytes"], 32 * 1024**2)
        self.assertLessEqual(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertTrue(
            all(value == 0 for value in report["operation_counters"].values())
        )

    def test_cli_has_no_override_surface(self):
        with self.assertRaises(SystemExit):
            vr27a.main(["qualify", "--source", "/tmp/other"])

    def test_report_is_strict_json(self):
        report = qualify()
        payload = vr27a._canonical_json_bytes(report)
        self.assertEqual(json.loads(payload), report)


if __name__ == "__main__":
    unittest.main()
