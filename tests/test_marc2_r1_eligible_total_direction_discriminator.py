import copy
import unittest

from neurodecodekit.datasets import (
    marc2_r1_eligible_total_direction_discriminator as subject,
)


class Marc2R1EligibleTotalDirectionDiscriminatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = subject.load_registered_contract()

    def test_plan_is_generated_only(self):
        plan = subject.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR31A")
        self.assertEqual(plan["paths"], 32)
        self.assertEqual(plan["VR29A_calls"], 32)
        self.assertEqual(plan["R1_direction_comparisons"], 8)
        self.assertFalse(plan["private_executor_available"])
        self.assertFalse(plan["FW2_or_CIL1_authorized"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_exact_generated_routes_and_source_immutability(self):
        expected = {
            "exact_public_control": (
                subject.SUCCESS_ROUTES[0],
                subject.vr29a.SUCCESS_ROUTES[0],
                0,
            ),
            "single_session_exclusion_removed": (
                subject.SUCCESS_ROUTES[1],
                subject.vr29a.SUCCESS_ROUTES[1],
                0,
            ),
            "eligible_bundle_removed": (
                subject.BELOW_EXPECTED_ROUTE,
                subject.vr29a.INVENTORY_TOTAL_ROUTE,
                1,
            ),
            "eligible_bundle_added": (
                subject.ABOVE_EXPECTED_ROUTE,
                subject.vr29a.INVENTORY_TOTAL_ROUTE,
                1,
            ),
            "eligible_distribution_shift": (
                subject.OUT_OF_SCOPE_ROUTE,
                subject.vr29a.DISTRIBUTION_ROUTE,
                0,
            ),
            "eligible_distribution_shift_second": (
                subject.OUT_OF_SCOPE_ROUTE,
                subject.vr29a.DISTRIBUTION_ROUTE,
                0,
            ),
            "unknown_participant_bundle": (
                subject.OUT_OF_SCOPE_ROUTE,
                subject.vr29a.OUT_OF_SCOPE_ROUTE,
                0,
            ),
            "incomplete_companion_set": (
                subject.OUT_OF_SCOPE_ROUTE,
                subject.vr29a.OUT_OF_SCOPE_ROUTE,
                0,
            ),
        }
        for order in subject.ORDERS:
            for case in subject.CASES:
                source = subject._build_case(case, order)
                before = subject.vr29a.vr25a._source_bytes(source)
                self.assertEqual(
                    subject.discriminate_generated_source(source),
                    expected[case],
                )
                self.assertEqual(subject.vr29a.vr25a._source_bytes(source), before)

    def test_below_and_above_routes_never_return_count(self):
        for case, route in (
            ("eligible_bundle_removed", subject.BELOW_EXPECTED_ROUTE),
            ("eligible_bundle_added", subject.ABOVE_EXPECTED_ROUTE),
        ):
            result = subject.discriminate_generated_source(
                subject._build_case(case, "canonical")
            )
            self.assertEqual(result[0], route)
            self.assertEqual(len(result), 3)
            self.assertTrue(all(not isinstance(value, dict) for value in result))

    def test_threshold_ast_binding_is_exact(self):
        self.assertEqual(subject._verify_threshold_predicate(self.contract), 1)
        changed = copy.deepcopy(self.contract)
        changed["immutable_threshold_predicate"]["expected_total"] = 194
        with self.assertRaises(subject.R1EligibleTotalDirectionDiscriminatorRefusal):
            subject._verify_threshold_predicate(changed)

    def test_private_fields_are_rejected(self):
        for field in subject.PRIVATE_PAYLOAD_FIELDS:
            with self.assertRaises(
                subject.R1EligibleTotalDirectionDiscriminatorRefusal
            ):
                subject._assert_public_report_safe({field: "forbidden"})

    def test_contract_and_environment_fail_closed(self):
        changed = copy.deepcopy(self.contract)
        changed["lane_id"] = "MARC2-VR31A-mutated"
        with self.assertRaises(subject.R1EligibleTotalDirectionDiscriminatorRefusal):
            subject._verify_contract_mapping(changed)
        environment = dict(subject.THREAD_ENVIRONMENT)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaises(subject.R1EligibleTotalDirectionDiscriminatorRefusal):
            subject._validate_thread_environment(environment)

    def test_direct_refusal_floor_passes(self):
        self.assertGreaterEqual(subject._run_direct_refusals(self.contract), 70)

    def test_resources_fail_closed(self):
        caps = self.contract["resource_limits"]
        with self.assertRaises(subject.R1EligibleTotalDirectionDiscriminatorRefusal):
            subject._assert_resources(
                runtime_seconds=caps["runtime_seconds"] + 1,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                contract=self.contract,
            )


if __name__ == "__main__":
    unittest.main()
