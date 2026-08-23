import copy
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

from neurodecodekit.datasets import (
    marc2_exact_task_surplus_decomposition as vr37a,
)


class Marc2ExactTaskSurplusDecompositionTests(unittest.TestCase):
    def test_registered_plan_is_generated_only(self):
        plan = vr37a.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR37A")
        self.assertEqual(plan["paths"], 24)
        self.assertEqual(plan["VR35A_calls"], 24)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["real_cohort_freeze_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_all_generated_cases_follow_frozen_routes(self):
        expected = dict(zip(vr37a.CASES, vr37a.ROUTES, strict=True))
        for order in vr37a.ORDERS:
            for case, route in expected.items():
                with self.subTest(case=case, order=order):
                    source = vr37a.build_generated_case(case, order)
                    before = vr37a._source_bytes(source)
                    self.assertEqual(vr37a.classify_generated_source(source), route)
                    self.assertEqual(vr37a._source_bytes(source), before)

    def test_each_path_calls_vr35a_exactly_once(self):
        source = vr37a.build_generated_case("single_cell_contiguous_extension", "canonical")
        original = vr37a.vr35a._route_case
        with mock.patch.object(vr37a.vr35a, "_route_case", wraps=original) as route_case:
            self.assertEqual(vr37a.classify_generated_source(source), "MARC2VR37A-R1")
        self.assertEqual(route_case.call_count, 1)

    def test_single_cell_routes_are_separated_by_prefix_contiguity(self):
        contiguous = vr37a.build_generated_case("single_cell_contiguous_extension", "canonical")
        gapped = vr37a.build_generated_case("single_cell_noncontiguous_extension", "canonical")
        self.assertEqual(vr37a.classify_generated_source(contiguous), "MARC2VR37A-R1")
        self.assertEqual(vr37a.classify_generated_source(gapped), "MARC2VR37A-R2")

    def test_multi_cell_and_mixed_topologies_are_separated(self):
        pure = vr37a.build_generated_case("multi_cell_pure_surplus", "reversed")
        mixed = vr37a.build_generated_case("mixed_surplus_and_deficit_net_positive", "reversed")
        self.assertEqual(vr37a.classify_generated_source(pure), "MARC2VR37A-R3")
        self.assertEqual(vr37a.classify_generated_source(mixed), "MARC2VR37A-R4")

    def test_order_invariance_is_exact(self):
        for case in vr37a.CASES:
            with self.subTest(case=case):
                canonical = vr37a.build_generated_case(case, "canonical")
                reversed_order = vr37a.build_generated_case(case, "reversed")
                self.assertEqual(
                    vr37a.classify_generated_source(canonical),
                    vr37a.classify_generated_source(reversed_order),
                )

    def test_contract_drift_fails_before_upstream_call(self):
        contract = vr37a.load_registered_contract()
        changed = copy.deepcopy(contract)
        changed["generated_matrix"]["VR35A_calls"] = 25
        source = vr37a.build_generated_case("public_map_exact_control", "canonical")
        with mock.patch.object(vr37a.vr35a, "_route_case") as route_case:
            with self.assertRaises(vr37a.ExactTaskSurplusDecompositionRefusal) as caught:
                vr37a.classify_generated_source(source, contract=changed)
        self.assertEqual(caught.exception.route, "MARC2VR37A-F01")
        route_case.assert_not_called()

    def test_public_output_firewall_rejects_private_fields(self):
        for key in (
            "cell_delta",
            "member_name",
            "private_manifest",
            "run_index",
            "subject_id",
        ):
            with self.subTest(key=key):
                with self.assertRaises(vr37a.ExactTaskSurplusDecompositionRefusal) as caught:
                    vr37a._assert_public_report_safe({key: "forbidden"})
                self.assertEqual(caught.exception.route, "MARC2VR37A-F05")

    def test_resource_caps_fail_closed(self):
        contract = vr37a.load_registered_contract()
        limits = contract["resource_limits"]
        with self.assertRaises(vr37a.ExactTaskSurplusDecompositionRefusal) as caught:
            vr37a._assert_resources(
                runtime_seconds=limits["runtime_seconds_maximum"] + 1,
                peak_rss_bytes=1,
                aggregate_output_bytes=1,
                contract=contract,
            )
        self.assertEqual(caught.exception.route, "MARC2VR37A-F06")

    def test_cli_has_no_private_execute_surface(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            vr37a.main(["execute"])
        self.assertIn("invalid choice", stderr.getvalue())

    def test_plan_cli_is_canonical_and_private_free(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = vr37a.main(["plan"])
        self.assertEqual(status, 0)
        payload = vr37a.json.loads(stdout.getvalue())
        self.assertFalse(payload["private_access_authorized"])
        self.assertFalse(payload["execute_surface_available"])
        self.assertNotIn("cohort", payload)


if __name__ == "__main__":
    unittest.main()
