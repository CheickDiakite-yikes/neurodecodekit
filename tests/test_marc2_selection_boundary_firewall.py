import copy
import os
import unittest

from neurodecodekit.datasets import marc2_selection_boundary_firewall as firewall


THREAD_ENVIRONMENT = firewall.THREAD_ENVIRONMENT


class Marc2SelectionBoundaryFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = firewall.load_registered_contract()

    def setUp(self) -> None:
        self.previous_environment = {
            key: os.environ.get(key) for key in THREAD_ENVIRONMENT
        }
        os.environ.update(THREAD_ENVIRONMENT)

    def tearDown(self) -> None:
        for key, value in self.previous_environment.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_exact_control_and_nuisance_variants_share_selection(self):
        accepted = firewall.CASES[:5]
        identities = set()
        routes = []
        for case in accepted:
            source = firewall.build_generated_case(case, "canonical")
            before = firewall._source_bytes(source)
            outcome = firewall.apply_selection_boundary_firewall(
                source, contract=self.contract
            )
            self.assertEqual(before, firewall._source_bytes(source))
            routes.append(outcome.route)
            identities.add(
                (
                    outcome.semantic_sha256,
                    outcome.source_exact_selected_names_sha256,
                    outcome.selection.split_summary["selected_run_bundles"],
                    outcome.selection.split_summary["selected_core_members"],
                    outcome.selection.byte_summary[
                        "selected_reservation_bytes"
                    ],
                )
            )
        self.assertEqual(
            routes,
            ["MARC2VR25A-G1"] + ["MARC2VR25A-G2"] * 4,
        )
        self.assertEqual(len(identities), 1)

    def test_every_registered_case_has_the_expected_route(self):
        for case in firewall.CASES:
            for order in firewall.ORDERS:
                with self.subTest(case=case, order=order):
                    source = firewall.build_generated_case(case, order)
                    before = firewall._source_bytes(source)
                    route, _outcome = firewall._route_case(
                        source, contract=self.contract
                    )
                    self.assertEqual(route, firewall.EXPECTED_CASE_ROUTES[case])
                    self.assertEqual(before, firewall._source_bytes(source))

    def test_eligible_mutations_never_inherit_warning_success(self):
        for case in (
            "eligible_bundle_removed",
            "eligible_bundle_added",
            "eligible_distribution_shift",
        ):
            source = firewall.build_generated_case(case, "canonical")
            with self.assertRaises(firewall.SelectionBoundaryFirewallRefusal) as ctx:
                firewall.apply_selection_boundary_firewall(
                    source, contract=self.contract
                )
            self.assertEqual(ctx.exception.route, "MARC2VR25A-R1")

    def test_unknown_and_incomplete_cases_fail_closed(self):
        expectations = {
            "unknown_participant_bundle": "MARC2VR25A-R2",
            "incomplete_companion_set": "MARC2VR25A-R3",
        }
        for case, route in expectations.items():
            source = firewall.build_generated_case(case, "canonical")
            with self.assertRaises(firewall.SelectionBoundaryFirewallRefusal) as ctx:
                firewall.apply_selection_boundary_firewall(
                    source, contract=self.contract
                )
            self.assertEqual(ctx.exception.route, route)

    def test_direct_refusal_matrix_is_exact(self):
        base = firewall.build_generated_case("exact_public_control", "canonical")
        counts, input_bytes, temporary_peak = firewall._run_direct_refusals(
            base, contract=self.contract
        )
        self.assertEqual(sum(counts.values()), 72)
        self.assertGreater(input_bytes, 0)
        self.assertLessEqual(
            input_bytes,
            self.contract["resource_caps"]["generated_input_bytes"],
        )
        self.assertLessEqual(
            temporary_peak,
            self.contract["resource_caps"]["temporary_output_bytes"],
        )

    def test_contract_drift_refuses_before_source_work(self):
        changed = copy.deepcopy(self.contract)
        changed["authorization_state"][
            "private_manifest_source_or_consumed_state_access_authorized_now"
        ] = True
        with self.assertRaises(firewall.SelectionBoundaryFirewallRefusal) as ctx:
            firewall._verify_contract_mapping(changed)
        self.assertEqual(ctx.exception.route, "MARC2VR25A-F01")

    def test_plan_and_inspection_expose_no_execution_surface(self):
        plan = firewall.build_plan()
        inspection = firewall.build_inspection()
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertFalse(inspection["private_access_authorized"])
        self.assertFalse(inspection["execute_surface_available"])
        self.assertFalse(inspection["observed_bundle_count_available"])

    def test_public_firewall_rejects_private_fields(self):
        for field in ("member_name", "participant_id", "private_manifest", "target"):
            with self.assertRaises(firewall.SelectionBoundaryFirewallRefusal) as ctx:
                firewall._assert_public_report_safe({field: "forbidden"})
            self.assertEqual(ctx.exception.route, "MARC2VR25A-F03")


if __name__ == "__main__":
    unittest.main()
