import copy
import unittest

from neurodecodekit.datasets import marc2_f04_task_implication as vr19a
from neurodecodekit.datasets import marc2_variable_width_run_index_repair as vr16a


class Marc2F04TaskImplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = vr19a.load_registered_contract()

    def test_plan_has_no_private_or_execute_surface(self):
        plan = vr19a.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR19A")
        self.assertEqual(plan["generated_paths"], 32)
        self.assertEqual(plan["VR16A_calls"], 32)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["execute_surface_available"])

    def test_static_audit_binds_both_task_guarded_producers(self):
        source = (
            vr19a._repo_root()
            / "src/neurodecodekit/datasets/marc2_variable_width_run_index_repair.py"
        ).read_bytes()
        audit = vr19a.audit_f04_producers(source)
        self.assertEqual(audit["F04_producer_references"], 2)
        self.assertTrue(audit["translated_task_guard"])
        self.assertTrue(audit["direct_task_guard"])
        self.assertTrue(audit["exact_R4_pair_unique_to_translated_reference"])
        self.assertFalse(audit["private_value_inspected"])

    def test_all_generated_cases_have_exact_routes_in_both_orders(self):
        for order in vr19a.ORDERS:
            for case in vr19a.CASES:
                with self.subTest(order=order, case=case):
                    source = vr19a.build_generated_case(case, order)
                    before = vr16a.vr2._canonical_source_bytes(source)
                    self.assertEqual(
                        vr19a.discriminate_generated(source), vr19a.CASE_ROUTES[case]
                    )
                    self.assertEqual(vr16a.vr2._canonical_source_bytes(source), before)

    def test_matrix_is_exact_and_replays(self):
        matrix = vr19a._run_matrix()
        vr19a._validate_matrix(matrix)
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR16A_calls"], 32)
        self.assertEqual(
            matrix["route_counts"],
            {
                vr19a.SUCCESS_ROUTE: 4,
                vr19a.RESULT_ROUTES[0]: 16,
                vr19a.RESULT_ROUTES[1]: 12,
            },
        )
        self.assertEqual(len(set(matrix["replay_digests"])), 1)

    def test_matrix_validator_rejects_drift(self):
        matrix = vr19a._run_matrix()
        changed = copy.deepcopy(matrix)
        changed["route_counts"] = {}
        with self.assertRaises(vr19a.F04TaskImplicationRefusal):
            vr19a._validate_matrix(changed)

    def test_full_qualification_passes_every_gate(self):
        report = vr19a.qualify_generated(peak_rss=lambda: 36_000_000)
        self.assertEqual(report["route"], "MARC2VR19A-G1")
        self.assertEqual(report["matrix"]["paths"], 32)
        self.assertEqual(report["matrix"]["VR16A_calls"], 32)
        self.assertTrue(report["matrix"]["both_replays_equal"])
        self.assertTrue(all(report["hypotheses"].values()))
        self.assertGreaterEqual(report["refusals"]["direct_refusals"], 40)
        self.assertTrue(
            all(value == 0 for value in report["operation_counters"].values())
        )
        self.assertFalse(report["claim_boundary"]["private_task_value_known"])

    def test_cli_rejects_path_override(self):
        with self.assertRaises(SystemExit):
            vr19a.main(["qualify", "--source", "/tmp/other"])


if __name__ == "__main__":
    unittest.main()
