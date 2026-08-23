import copy
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from neurodecodekit.datasets import (
    marc2_task_aware_eligibility_repair as vr35a,
)


class Marc2TaskAwareEligibilityRepairTests(unittest.TestCase):
    def test_registered_plan_is_generated_only(self):
        plan = vr35a.build_plan()
        self.assertEqual(plan["lane_id"], "MARC2-VR35A")
        self.assertEqual(plan["paths"], 20)
        self.assertEqual(plan["published_task"], "reachingandgrasping")
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["real_cohort_freeze_authorized"])
        self.assertFalse(plan["execute_surface_available"])
        self.assertEqual(plan["scientific_ceiling"], "none")

    def test_all_generated_cases_follow_frozen_routes(self):
        expected = {
            "baseline_exact_task_exact_total": "MARC2VR35A-G1",
            "mixed_task_surplus": "MARC2VR35A-G2",
            "target_task_surplus": "MARC2VR35A-R1",
            "target_task_deficit": "MARC2VR35A-R2",
            "selection_or_task_firewall_refusal": "MARC2VR35A-R3",
        }
        for order in vr35a.ORDERS:
            for case, route in expected.items():
                with self.subTest(case=case, order=order):
                    source = vr35a.build_generated_case(case, order)
                    before = vr35a._source_bytes(source)
                    observed, _ = vr35a._route_case(source)
                    self.assertEqual(observed, route)
                    self.assertEqual(vr35a._source_bytes(source), before)

    def test_mixed_task_surplus_reproduces_baseline_semantics(self):
        baseline = vr35a.adapt_task_aware_source(
            vr35a.build_generated_case(
                "baseline_exact_task_exact_total", "canonical"
            )
        )
        mixed = vr35a.adapt_task_aware_source(
            vr35a.build_generated_case("mixed_task_surplus", "canonical")
        )
        self.assertEqual(baseline.route, "MARC2VR35A-G1")
        self.assertEqual(mixed.route, "MARC2VR35A-G2")
        self.assertFalse(baseline.task_blind_surplus_removed)
        self.assertTrue(mixed.task_blind_surplus_removed)
        self.assertEqual(baseline.semantic_sha256, mixed.semantic_sha256)

    def test_successful_selections_contain_only_exact_published_task(self):
        for case in (
            "baseline_exact_task_exact_total",
            "mixed_task_surplus",
        ):
            with self.subTest(case=case):
                outcome = vr35a.adapt_task_aware_source(
                    vr35a.build_generated_case(case, "reversed")
                )
                rows = outcome.selection.private_manifest["rows"]
                self.assertEqual(len(rows), 16 * 24)
                for row in rows:
                    match = vr35a.vr20a._core_match(row["member_name"])
                    self.assertIsNotNone(match)
                    self.assertEqual(match.group("task"), vr35a.PUBLISHED_TASK)

    def test_order_invariance_is_exact(self):
        for case in (
            "baseline_exact_task_exact_total",
            "mixed_task_surplus",
        ):
            with self.subTest(case=case):
                canonical = vr35a.adapt_task_aware_source(
                    vr35a.build_generated_case(case, "canonical")
                )
                reversed_order = vr35a.adapt_task_aware_source(
                    vr35a.build_generated_case(case, "reversed")
                )
                self.assertEqual(
                    canonical.semantic_sha256,
                    reversed_order.semantic_sha256,
                )
                self.assertEqual(
                    canonical.source_exact_selected_names_sha256,
                    reversed_order.source_exact_selected_names_sha256,
                )

    def test_task_is_a_grouping_dimension_before_projection(self):
        source = vr35a.build_generated_case("mixed_task_surplus", "canonical")
        vr2_contract = vr35a.vr2.load_registered_contract()
        entries = vr35a.vr2._validate_live_envelope(source, vr2_contract)
        grouped, _ = vr35a._group_task_rows(entries)
        projected = vr35a._project_published_task(grouped)
        self.assertTrue(any(key[2] == "motorimagery" for key in grouped))
        self.assertTrue(all(key[2] != "motorimagery" for key in projected))

    def test_uppercase_task_token_fails_closed(self):
        source = vr35a.build_generated_case(
            "baseline_exact_task_exact_total", "canonical"
        )
        row = next(
            row
            for row in source["entries"]
            if vr35a.vr20a._core_match(row.get("member_name", "")) is not None
        )
        match = vr35a.vr20a._core_match(row["member_name"])
        self.assertIsNotNone(match)
        row["member_name"] = vr35a.vr20a._replace_group(
            row["member_name"], match, "task", "MotorImagery"
        )
        route, outcome = vr35a._route_case(source)
        self.assertEqual(route, "MARC2VR35A-R3")
        self.assertIsNone(outcome)

    def test_incomplete_task_companion_set_fails_closed(self):
        source = vr35a.build_generated_case(
            "selection_or_task_firewall_refusal", "canonical"
        )
        route, outcome = vr35a._route_case(source)
        self.assertEqual(route, "MARC2VR35A-R3")
        self.assertIsNone(outcome)

    def test_contract_drift_fails_before_generated_selection(self):
        contract = vr35a.load_registered_contract()
        changed = copy.deepcopy(contract)
        changed["repair_contract"]["published_task_label"] = "changed"
        with self.assertRaises(vr35a.TaskAwareEligibilityRepairRefusal) as caught:
            vr35a.adapt_task_aware_source(
                vr35a.build_generated_case(
                    "baseline_exact_task_exact_total", "canonical"
                ),
                contract=changed,
            )
        self.assertEqual(caught.exception.route, "MARC2VR35A-F01")

    def test_public_output_firewall_rejects_private_fields(self):
        for key in (
            "actual_count",
            "member_name",
            "private_manifest",
            "subject_id",
            "task_distribution",
        ):
            with self.subTest(key=key):
                with self.assertRaises(
                    vr35a.TaskAwareEligibilityRepairRefusal
                ) as caught:
                    vr35a._assert_public_report_safe({key: "forbidden"})
                self.assertEqual(caught.exception.route, "MARC2VR35A-F05")

    def test_resource_caps_fail_closed(self):
        contract = vr35a.load_registered_contract()
        limits = contract["resource_limits"]
        with self.assertRaises(vr35a.TaskAwareEligibilityRepairRefusal) as caught:
            vr35a._assert_resources(
                runtime_seconds=limits["runtime_seconds"] + 1,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                contract=contract,
            )
        self.assertEqual(caught.exception.route, "MARC2VR35A-F06")

    def test_cli_has_no_private_execute_surface(self):
        stderr = io.StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit):
            vr35a.main(["execute"])
        self.assertIn("invalid choice", stderr.getvalue())

    def test_plan_cli_is_canonical_and_target_free(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            status = vr35a.main(["plan"])
        self.assertEqual(status, 0)
        payload = vr35a.json.loads(stdout.getvalue())
        self.assertFalse(payload["private_access_authorized"])
        self.assertFalse(payload["execute_surface_available"])
        self.assertNotIn("cohort", payload)


if __name__ == "__main__":
    unittest.main()
