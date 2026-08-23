import copy
import json
import unittest
from unittest import mock

from neurodecodekit.datasets import marc2_live_domain_eligibility_adapter as vr2
from neurodecodekit.datasets import marc2_r1_inventory_distribution_discriminator as vr29a
from neurodecodekit.datasets import marc2_selection_boundary_firewall as vr25a

MEASURED_FRESH_PROCESS_RSS = 40_000_000


def qualify(**kwargs):
    return vr29a.qualify_generated(
        environment=vr29a.THREAD_ENVIRONMENT,
        peak_rss=lambda: MEASURED_FRESH_PROCESS_RSS,
        **kwargs,
    )


class Marc2R1InventoryDistributionDiscriminatorTests(unittest.TestCase):
    def test_plan_is_generated_only(self):
        plan = vr29a.build_plan()
        self.assertEqual(plan["paths"], 32)
        self.assertEqual(plan["VR25A_calls"], 32)
        self.assertEqual(plan["R1_filter_discriminator_calls"], 16)
        self.assertEqual(plan["VR2_filter_refusal_sites"], 2)
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_qualification_routes_are_exact(self):
        report = qualify()
        matrix = report["matrix"]
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR25A_calls"], 32)
        self.assertEqual(matrix["R1_filter_discriminator_calls"], 16)
        self.assertEqual(matrix["VR2_filter_refusal_sites"], 2)
        self.assertEqual(
            matrix["VR29A_route_counts"],
            {
                "MARC2VR29A-G1": 4,
                "MARC2VR29A-G2": 4,
                "MARC2VR29A-R1": 8,
                "MARC2VR29A-R2": 8,
                "MARC2VR29A-R3": 8,
            },
        )
        self.assertEqual(
            matrix["VR25A_route_counts"],
            {
                "MARC2VR25A-G1": 4,
                "MARC2VR25A-G2": 4,
                "MARC2VR25A-R1": 16,
                "MARC2VR25A-R2": 4,
                "MARC2VR25A-R3": 4,
            },
        )
        self.assertGreaterEqual(matrix["direct_refusals_passed"], 70)
        self.assertFalse(matrix["private_reason_or_value_retained"])

    def test_each_matrix_path_calls_exact_helpers(self):
        original_vr25a = vr25a.apply_selection_boundary_firewall
        original_filter = vr2._filter_and_validate_eligible
        vr25a_calls = 0
        filter_calls = 0

        def counted_vr25a(*args, **kwargs):
            nonlocal vr25a_calls
            vr25a_calls += 1
            return original_vr25a(*args, **kwargs)

        def counted_filter(*args, **kwargs):
            nonlocal filter_calls
            filter_calls += 1
            return original_filter(*args, **kwargs)

        with (
            mock.patch.object(vr25a, "apply_selection_boundary_firewall", counted_vr25a),
            mock.patch.object(vr2, "_filter_and_validate_eligible", counted_filter),
        ):
            report = qualify()
        self.assertEqual(vr25a_calls, 32)
        self.assertEqual(filter_calls, 40)
        self.assertEqual(report["matrix"]["VR25A_calls"], 32)
        self.assertEqual(report["matrix"]["R1_filter_discriminator_calls"], 16)

    def test_inventory_total_and_distribution_witnesses_separate(self):
        for case in ("eligible_bundle_removed", "eligible_bundle_added"):
            with self.subTest(case=case):
                source = vr29a._build_case(case, "canonical")
                self.assertEqual(
                    vr29a.discriminate_generated_source(source),
                    ("MARC2VR29A-R1", "MARC2VR25A-R1", 1),
                )
        for case in (
            "eligible_distribution_shift",
            "eligible_distribution_shift_second",
        ):
            with self.subTest(case=case):
                source = vr29a._build_case(case, "canonical")
                self.assertEqual(
                    vr29a.discriminate_generated_source(source),
                    ("MARC2VR29A-R2", "MARC2VR25A-R1", 1),
                )

    def test_controls_preserve_success_and_out_of_scope_routes(self):
        expected = {
            "exact_public_control": ("MARC2VR29A-G1", "MARC2VR25A-G1", 0),
            "single_session_exclusion_removed": (
                "MARC2VR29A-G2",
                "MARC2VR25A-G2",
                0,
            ),
            "unknown_participant_bundle": (
                "MARC2VR29A-R3",
                "MARC2VR25A-R2",
                0,
            ),
            "incomplete_companion_set": (
                "MARC2VR29A-R3",
                "MARC2VR25A-R3",
                0,
            ),
        }
        for case, outcome in expected.items():
            with self.subTest(case=case):
                source = vr29a._build_case(case, "canonical")
                self.assertEqual(vr29a.discriminate_generated_source(source), outcome)

    def test_replays_are_deterministic_and_source_immutable(self):
        first = qualify()
        second = qualify()
        self.assertEqual(
            first["matrix"]["replay_digest"], second["matrix"]["replay_digest"]
        )
        self.assertTrue(first["matrix"]["exact_replays_match"])
        self.assertEqual(first["matrix"]["source_mutations_after_call"], 0)

    def test_contract_mutation_is_refused(self):
        changed = copy.deepcopy(vr29a.load_registered_contract())
        changed["lane_id"] = "other"
        with self.assertRaises(
            vr29a.R1InventoryDistributionDiscriminatorRefusal
        ) as caught:
            qualify(contract=changed)
        self.assertEqual(caught.exception.route, "MARC2VR29A-F01")

    def test_thread_drift_is_refused(self):
        environment = dict(vr29a.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(
            vr29a.R1InventoryDistributionDiscriminatorRefusal
        ) as caught:
            vr29a.qualify_generated(environment=environment)
        self.assertEqual(caught.exception.route, "MARC2VR29A-F06")

    def test_unknown_filter_reason_and_upstream_route_are_refused(self):
        with self.assertRaises(vr29a.R1InventoryDistributionDiscriminatorRefusal):
            vr29a._map_filter_reason("unknown")
        with self.assertRaises(vr29a.R1InventoryDistributionDiscriminatorRefusal):
            vr29a._map_non_r1_upstream("MARC2VR25A-R4")

    def test_private_payload_fields_are_refused(self):
        for field in vr29a.PRIVATE_PAYLOAD_FIELDS:
            with self.subTest(field=field), self.assertRaises(
                vr29a.R1InventoryDistributionDiscriminatorRefusal
            ):
                vr29a._assert_public_report_safe({field: "x"})

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
            vr29a.main(["qualify", "--source", "/tmp/other"])

    def test_report_is_strict_json(self):
        report = qualify()
        payload = vr29a._canonical_json_bytes(report)
        self.assertEqual(json.loads(payload), report)


if __name__ == "__main__":
    unittest.main()
