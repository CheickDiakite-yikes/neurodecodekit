import copy
import json
import unittest
from dataclasses import fields

from neurodecodekit.datasets import marc2_r4_residual_decomposition as residual


THREAD_ENV = {name: "1" for name in residual.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((100.0, 100.5))
    return lambda: next(values)


class Marc2R4ResidualDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = residual.load_registered_contract()
        cls.report = residual.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )

    def test_plan_is_bounded_and_has_no_private_authority(self):
        plan = residual.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR13A")
        self.assertEqual(plan["fixed_input_count"], 15)
        self.assertEqual(plan["fixed_input_bytes"], 314_530)
        self.assertEqual(plan["generated_cases"], 8)
        self.assertEqual(plan["required_paths"], 32)
        self.assertEqual(plan["required_VR12A_calls"], 32)
        self.assertEqual(plan["direct_refusal_minimum"], 50)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["MARC2_FW2_or_CIL1_authorized"])

    def test_registration_proof_is_exact_and_green(self):
        inspected = residual.build_inspection_summary()
        self.assertEqual(
            inspected["registration_commit"],
            "1177174c1d466cf357ef3a81a4d96b39321af063",
        )
        self.assertEqual(inspected["registration_CI_run_id"], 32_424_688_012)
        self.assertTrue(inspected["both_jobs_green"])
        self.assertEqual(inspected["residual_class_count"], 7)
        self.assertFalse(inspected["private_access_authorized"])

    def test_all_routes_appear_four_times(self):
        summary = self.report["route_summary"]
        self.assertEqual(
            summary["ordered_routes"],
            [residual.SUCCESS_ROUTE, *residual.RESULT_ROUTES],
        )
        self.assertEqual(summary["route_counts"], residual._expected_route_counts())
        self.assertTrue(summary["one_route_per_generated_path"])
        self.assertEqual(summary["failure_details_retained"], 0)
        self.assertEqual(summary["per_path_outcomes_retained"], 0)

    def test_exact_matrix_and_replay_mechanics(self):
        replay = self.report["replay_summary"]
        self.assertEqual(replay["generated_cases"], 8)
        self.assertEqual(replay["orders"], 2)
        self.assertEqual(replay["exact_replays"], 2)
        self.assertEqual(replay["total_paths"], 32)
        self.assertEqual(replay["exact_VR12A_calls"], 32)
        self.assertTrue(replay["byte_identical_replay"])
        self.assertTrue(replay["order_invariant_routes"])
        self.assertEqual(len(replay["internal_matrix_digest_sha256"]), 64)
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["entry_count_each"], 1_227)
        self.assertEqual(mechanics["AST_refusal_call_sites"], 23)
        self.assertEqual(mechanics["witness_mutations_before_VR12A"], 28)
        self.assertEqual(mechanics["control_paths_without_mutation"], 4)
        self.assertEqual(mechanics["source_mutations_by_VR12A"], 0)
        self.assertEqual(mechanics["predecessor_modules_modified"], 0)

    def test_each_generated_case_reaches_exact_route_without_mutation(self):
        for order in residual.ORDERS:
            for case in residual.CASES:
                with self.subTest(order=order, case=case):
                    source = residual._build_case(case, order)
                    before = residual.vr12a.vr2._canonical_source_bytes(source)
                    decision = residual.discriminate_generated_source(source)
                    after = residual.vr12a.vr2._canonical_source_bytes(source)
                    self.assertEqual(decision.route, residual.CASE_ROUTES[case])
                    self.assertEqual(before, after)
                    self.assertEqual(
                        [field.name for field in fields(decision)], ["route"]
                    )

    def test_unknown_or_neighboring_vr12a_route_refuses(self):
        for route, reason in (
            ("MARC2VR12A-F01", "registered contract hash differs"),
            ("MARC2VR12A-F07", "repaired dynamic selection refused"),
            ("MARC2VR12A-F08", "scientific firewall refused"),
        ):
            with self.subTest(route=route):
                exc = residual.vr12a.P15RunIndexRepairRefusal(route, reason)
                with self.assertRaises(
                    residual.R4ResidualDecompositionRefusal
                ) as refusal:
                    residual._route_for_refusal(exc)
                self.assertEqual(refusal.exception.route, "MARC2VR13A-F03")

    def test_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        caps = self.contract["resource_caps"]
        self.assertEqual(measured["fixed_artifact_count"], 18)
        self.assertEqual(measured["fixed_artifact_bytes"], 342_211)
        self.assertEqual(measured["runtime_seconds"], 0.5)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024 * 1024)
        self.assertLessEqual(
            measured["generated_input_bytes"], caps["generated_input_bytes"]
        )
        self.assertLessEqual(
            measured["aggregate_output_bytes"], caps["aggregate_output_bytes"]
        )
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_direct_refusal_inventory_exceeds_frozen_minimum(self):
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 50)
        self.assertTrue(
            set(refusals.values()).issubset(set(residual.REFUSAL_ROUTES))
        )
        for index in range(1, 9):
            self.assertIn(f"residual_route_drift_{index:02d}", refusals)
        for index in range(1, 9):
            self.assertIn(f"matrix_drift_{index:02d}", refusals)

    def test_public_report_is_strict_and_target_free(self):
        payload = residual._canonical_json_bytes(self.report)
        decoded = json.loads(payload)
        residual._validate_public_report(decoded)
        self.assertEqual(
            len(payload), self.report["measurements"]["aggregate_output_bytes"]
        )
        lowered = payload.decode("ascii").lower()
        self.assertNotIn('"member_name":', lowered)
        self.assertNotIn('"row_index":', lowered)
        self.assertNotIn('"safe_reason":', lowered)
        self.assertNotIn('"private_manifest":', lowered)
        self.assertNotIn('"target":', lowered)
        self.assertNotIn('"prediction":', lowered)

    def test_report_and_resource_mutations_refuse_closed(self):
        leaked = copy.deepcopy(self.report)
        leaked["member_name"] = "redacted"
        with self.assertRaises(residual.R4ResidualDecompositionRefusal) as privacy:
            residual._validate_public_report(leaked)
        self.assertEqual(privacy.exception.route, "MARC2VR13A-F04")

        changed = copy.deepcopy(self.report)
        changed["route_summary"]["route_counts"][residual.RESULT_ROUTES[0]] = 3
        with self.assertRaises(residual.R4ResidualDecompositionRefusal) as shape:
            residual._validate_public_report(changed)
        self.assertEqual(shape.exception.route, "MARC2VR13A-F04")

        with self.assertRaises(residual.R4ResidualDecompositionRefusal) as resource:
            residual._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=self.contract,
            )
        self.assertEqual(resource.exception.route, "MARC2VR13A-F06")

    def test_deterministic_replay_with_fixed_resource_probes(self):
        replayed = residual.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )
        self.assertEqual(
            residual._canonical_json_bytes(replayed),
            residual._canonical_json_bytes(self.report),
        )

    def test_claim_and_operation_boundaries_remain_closed(self):
        self.assertTrue(
            all(value == 0 for value in self.report["access_counters"].values())
        )
        self.assertTrue(all(self.report["acceptance_gates"].values()))
        claims = self.report["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_ceiling", "scientific_ceiling"}:
                self.assertFalse(value)
        gate = self.report["next_gate"]
        self.assertFalse(gate["future_private_discriminator_authorized"])
        self.assertFalse(gate["consumed_VR11P_or_VR12P_reuse_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_thread_and_cli_surfaces_are_strict(self):
        with self.assertRaises(residual.R4ResidualDecompositionRefusal) as thread:
            residual._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR13A-F06")
        parser = residual._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["inspect"]).command, "inspect")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        option_strings = {
            option for action in parser._actions for option in action.option_strings
        }
        self.assertNotIn("--path", option_strings)
        self.assertNotIn("--output", option_strings)
        self.assertNotIn("--execute", option_strings)


if __name__ == "__main__":
    unittest.main()
