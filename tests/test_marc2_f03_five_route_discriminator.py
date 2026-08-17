import copy
import json
import unittest
from dataclasses import fields

from neurodecodekit.datasets import marc2_f03_five_route_discriminator as five

THREAD_ENV = {name: "1" for name in five.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((100.0, 100.5))
    return lambda: next(values)


class Marc2F03FiveRouteDiscriminatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = five.load_registered_contract()
        cls.report = five.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )

    def test_plan_is_bounded_and_has_no_private_authority(self):
        plan = five.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR10B")
        self.assertEqual(plan["fixed_input_count"], 10)
        self.assertEqual(plan["fixed_input_bytes"], 390_842)
        self.assertEqual(plan["ordered_result_routes"], list(five.RESULT_ROUTES))
        self.assertEqual(plan["generated_control_route"], "MARC2VR10B-G1")
        self.assertEqual(plan["generated_cases"], 6)
        self.assertEqual(plan["required_paths"], 24)
        self.assertEqual(plan["required_VR6_calls"], 24)
        self.assertEqual(plan["required_discriminator_calls"], 24)
        self.assertFalse(plan["private_access_authorized"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_bytes"], 0)

    def test_every_generated_class_has_one_exact_coarse_route(self):
        routes = self.report["route_summary"]
        self.assertEqual(
            routes["ordered_routes"],
            [five.SUCCESS_ROUTE, *five.RESULT_ROUTES],
        )
        self.assertEqual(routes["route_counts"], five._expected_route_counts())
        self.assertEqual(routes["broad_VR6_success_paths"], 4)
        self.assertEqual(routes["broad_outer_F02_nested_F03_paths"], 20)
        self.assertTrue(routes["one_route_per_decision"])
        self.assertEqual(routes["failed_values_retained"], 0)
        self.assertEqual(routes["per_item_outcomes_retained"], 0)

    def test_replay_counts_and_parser_mechanics_are_frozen(self):
        replay = self.report["replay_summary"]
        self.assertEqual(replay["exact_replays"], 2)
        self.assertEqual(replay["paths_per_replay"], 12)
        self.assertEqual(replay["total_paths"], 24)
        self.assertEqual(replay["exact_parser_entry_visits"], 29_448)
        self.assertEqual(replay["exact_VR6_calls"], 24)
        self.assertEqual(replay["exact_discriminator_calls"], 24)
        self.assertTrue(replay["order_invariant"])
        self.assertTrue(replay["byte_identical_replay"])
        self.assertEqual(len(replay["internal_matrix_digest_sha256"]), 64)
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["entry_count_each"], 1_227)
        self.assertEqual(mechanics["regular_file_rows_each"], 1_025)
        self.assertEqual(mechanics["directory_rows_each"], 202)
        self.assertEqual(mechanics["witness_mutations_before_exact_parser"], 20)
        self.assertEqual(mechanics["control_paths_without_witness_mutation"], 4)
        self.assertEqual(mechanics["post_parser_witness_mutations"], 0)
        self.assertEqual(mechanics["source_mutations_by_discriminator"], 0)

    def test_direct_classifier_matches_all_six_witnesses_without_mutation(self):
        vr2_contract = five.decomp.relay.vr2.load_registered_contract()
        selector_contract = five.decomp.relay.selector.load_registered_contract()
        for case in five.CASES:
            with self.subTest(case=case):
                composed = five.decomp._compose_witness(
                    case,
                    "canonical",
                    vr2_contract=vr2_contract,
                    selector_contract=selector_contract,
                )
                before = five.decomp.relay.vr2._canonical_source_bytes(
                    composed.source
                )
                decision = five.discriminate_generated_source(
                    composed.source, vr2_contract=vr2_contract
                )
                after = five.decomp.relay.vr2._canonical_source_bytes(
                    composed.source
                )
                self.assertEqual(decision.route, five.CASE_ROUTES[case])
                self.assertEqual(before, after)
                self.assertEqual([field.name for field in fields(decision)], ["route"])

    def test_malformed_nonclassifier_source_refuses_without_class_route(self):
        vr2_contract = five.decomp.relay.vr2.load_registered_contract()
        selector_contract = five.decomp.relay.selector.load_registered_contract()
        composed = five.decomp._compose_witness(
            "control_success",
            "canonical",
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
        changed = copy.deepcopy(composed.source)
        changed["entries"][0] = "not-a-row"
        with self.assertRaises(five.FiveRouteDiscriminatorRefusal) as refusal:
            five.discriminate_generated_source(
                changed, vr2_contract=vr2_contract
            )
        self.assertEqual(refusal.exception.route, "MARC2VR10B-F03")

    def test_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        caps = self.contract["resource_caps"]
        self.assertEqual(measured["fixed_artifact_count"], 13)
        self.assertEqual(measured["fixed_artifact_bytes"], 417_533)
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

    def test_every_forbidden_operation_and_claim_remains_zero(self):
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
        self.assertFalse(gate["consumed_VR9P_reuse_allowed"])
        self.assertFalse(gate["F03_rule_relaxation_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_direct_refusal_inventory_exceeds_frozen_minimum(self):
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 45)
        self.assertTrue(set(refusals.values()).issubset(set(five.REFUSAL_ROUTES)))
        for index in range(1, 6):
            self.assertIn(f"route_priority_drift_{index:02d}", refusals)
        for index in range(1, 7):
            self.assertIn(f"matrix_route_drift_{index:02d}", refusals)

    def test_deterministic_replay_with_fixed_resource_probes(self):
        replayed = five.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )
        self.assertEqual(
            five._canonical_json_bytes(replayed),
            five._canonical_json_bytes(self.report),
        )

    def test_report_and_resource_mutations_refuse_closed(self):
        changed = copy.deepcopy(self.report)
        changed["route_summary"]["route_counts"][five.RESULT_ROUTES[0]] = 3
        with self.assertRaises(five.FiveRouteDiscriminatorRefusal) as route:
            five._validate_public_report(changed)
        self.assertEqual(route.exception.route, "MARC2VR10B-F04")

        leaked = copy.deepcopy(self.report)
        leaked["member_name"] = "redacted"
        with self.assertRaises(five.FiveRouteDiscriminatorRefusal) as privacy:
            five._validate_public_report(leaked)
        self.assertEqual(privacy.exception.route, "MARC2VR10B-F05")

        with self.assertRaises(five.FiveRouteDiscriminatorRefusal) as resource:
            five._assert_resources(
                runtime_seconds=46.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=self.contract,
            )
        self.assertEqual(resource.exception.route, "MARC2VR10B-F06")

    def test_thread_and_cli_surfaces_are_strict(self):
        with self.assertRaises(five.FiveRouteDiscriminatorRefusal) as thread:
            five._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR10B-F06")
        parser = five._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        option_strings = {
            option for action in parser._actions for option in action.option_strings
        }
        self.assertNotIn("--path", option_strings)
        self.assertNotIn("--output", option_strings)
        self.assertNotIn("--execute", option_strings)

    def test_public_report_is_strict_and_has_no_per_item_shape(self):
        payload = five._canonical_json_bytes(self.report)
        decoded = json.loads(payload)
        self.assertEqual(decoded["route"], "MARC2VR10B-G1")
        five._validate_public_report(decoded)
        lowered = payload.decode("ascii").lower()
        self.assertNotIn('"member_name":', lowered)
        self.assertNotIn('"row_index":', lowered)
        self.assertNotIn('"private_manifest":', lowered)
        self.assertNotIn('"target":', lowered)
        self.assertNotIn('"prediction":', lowered)
        self.assertNotIn('"case":', lowered)


if __name__ == "__main__":
    unittest.main()
