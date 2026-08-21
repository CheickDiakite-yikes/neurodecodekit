import copy
import unittest

from neurodecodekit.datasets import marc2_first_failure_stable_r4_decomposition as vr17c
from neurodecodekit.datasets import marc2_variable_width_run_index_repair as vr16a


class Marc2FirstFailureStableR4DecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = vr17c.load_registered_contract()

    def test_plan_has_no_private_execution_surface(self):
        plan = vr17c.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR17C")
        self.assertEqual(plan["equivalence_paths"], 24)
        self.assertEqual(plan["residual_paths"], 20)
        self.assertEqual(plan["VR15A_calls"], 24)
        self.assertEqual(plan["VR16A_calls"], 44)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["execute_surface_available"])

    def test_collision_witness_preserves_count_and_run_token(self):
        base = vr16a.build_generated_variant("three_digit", "canonical")
        changed = vr17c.build_residual_case(
            "same_token_distinct_name_normalized_collision", "canonical"
        )
        self.assertEqual(len(changed["entries"]), len(base["entries"]))
        duplicate = next(
            row for row in changed["entries"] if "_acq-copy_run-" in row["member_name"]
        )
        match = vr16a._variable_core_match(duplicate["member_name"])
        self.assertIsNotNone(match)
        self.assertEqual(match.group("run"), "001")
        self.assertEqual(vr17c.discriminate_residual(changed), "MARC2VR17C-R3")

    def test_residual_cases_have_exact_routes_in_both_orders(self):
        for order in vr17c.ORDERS:
            for case in vr17c.RESIDUAL_CASES:
                with self.subTest(order=order, case=case):
                    source = vr17c.build_residual_case(case, order)
                    before = vr16a.vr2._canonical_source_bytes(source)
                    self.assertEqual(
                        vr17c.discriminate_residual(source), vr17c.CASE_ROUTES[case]
                    )
                    self.assertEqual(vr16a.vr2._canonical_source_bytes(source), before)

    def test_matrix_validators_reject_drift(self):
        equivalence = vr17c._run_equivalence_matrix()
        residual = vr17c._run_residual_matrix()
        vr17c._validate_equivalence_matrix(equivalence)
        vr17c._validate_residual_matrix(residual)
        changed = copy.deepcopy(equivalence)
        changed["control_paths"] = 0
        with self.assertRaises(vr17c.FirstFailureStableR4Refusal):
            vr17c._validate_equivalence_matrix(changed)
        changed = copy.deepcopy(residual)
        changed["route_counts"] = {}
        with self.assertRaises(vr17c.FirstFailureStableR4Refusal):
            vr17c._validate_residual_matrix(changed)

    def test_full_qualification_passes_every_gate(self):
        report = vr17c.qualify_generated(peak_rss=lambda: 36_569_088)
        self.assertEqual(report["route"], "MARC2VR17C-G1")
        self.assertEqual(report["equivalence"]["paths"], 24)
        self.assertEqual(report["residual"]["paths"], 20)
        self.assertEqual(
            report["residual"]["route_counts"],
            {route: 4 for route in (vr17c.SUCCESS_ROUTE, *vr17c.RESULT_ROUTES)},
        )
        self.assertTrue(all(report["hypotheses"].values()))
        self.assertGreaterEqual(report["refusals"]["direct_refusals"], 50)
        self.assertEqual(report["measurements"]["retained_generated_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in report["operation_counters"].values()))

    def test_cli_rejects_path_override(self):
        with self.assertRaises(SystemExit):
            vr17c.main(["qualify", "--source", "/tmp/other"])


if __name__ == "__main__":
    unittest.main()
