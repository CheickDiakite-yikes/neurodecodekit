import copy
import json
import unittest
from dataclasses import fields

from neurodecodekit.datasets import (
    marc2_suffix_identity_grammar_decomposition as grammar,
)

THREAD_ENV = {name: "1" for name in grammar.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((100.0, 100.5))
    return lambda: next(values)


class Marc2SuffixIdentityGrammarDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = grammar.load_registered_contract()
        cls.report = grammar.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )

    def test_plan_is_bounded_and_has_no_private_authority(self):
        plan = grammar.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR15A")
        self.assertEqual(plan["fixed_input_count"], 11)
        self.assertEqual(plan["fixed_input_bytes"], 215_394)
        self.assertEqual(plan["generated_cases"], 17)
        self.assertEqual(plan["required_paths"], 68)
        self.assertEqual(plan["required_VR12A_calls"], 68)
        self.assertEqual(plan["direct_refusal_minimum"], 70)
        self.assertFalse(plan["private_access_authorized"])
        self.assertFalse(plan["MARC2_FW2_or_CIL1_authorized"])

    def test_registration_proof_is_exact_and_green(self):
        inspected = grammar.build_inspection_summary()
        self.assertEqual(
            inspected["registration_commit"],
            "185fbc54366fd0eaf0ed4e994511e4485514b53e",
        )
        self.assertEqual(inspected["registration_CI_run_id"], 32_447_836_662)
        self.assertTrue(inspected["both_jobs_green"])
        self.assertEqual(inspected["grammar_class_count"], 16)
        self.assertFalse(inspected["private_access_authorized"])

    def test_static_regex_suffixes_and_p15_guard_are_bound(self):
        payloads = grammar._fixed_payloads(self.contract)
        self.assertEqual(grammar._verify_static_grammar(self.contract, payloads), 1)
        self.assertEqual(
            grammar.vr12a.REPAIRED_CORE_MEMBER_RE.pattern,
            grammar.EXPECTED_REPAIRED_PATTERN,
        )
        self.assertEqual(
            tuple(grammar.vr12a.selector.REQUIRED_SUFFIXES),
            ("_eeg.eeg", "_eeg.vhdr", "_eeg.vmrk", "_events.tsv"),
        )

    def test_all_routes_appear_four_times(self):
        summary = self.report["route_summary"]
        self.assertEqual(
            summary["ordered_routes"],
            [grammar.SUCCESS_ROUTE, *grammar.RESULT_ROUTES],
        )
        self.assertEqual(summary["route_counts"], grammar._expected_route_counts())
        self.assertTrue(summary["one_route_per_generated_source"])
        self.assertEqual(summary["failure_details_retained"], 0)
        self.assertEqual(summary["per_source_outcomes_retained"], 0)

    def test_exact_matrix_and_replay_mechanics(self):
        replay = self.report["replay_summary"]
        self.assertEqual(replay["generated_cases"], 17)
        self.assertEqual(replay["source_orders"], 2)
        self.assertEqual(replay["exact_replays"], 2)
        self.assertEqual(replay["total_paths"], 68)
        self.assertEqual(replay["exact_VR12A_calls"], 68)
        self.assertTrue(replay["byte_identical_replay"])
        self.assertTrue(replay["order_invariant_routes"])
        self.assertEqual(len(replay["internal_matrix_digest_sha256"]), 64)
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["entry_count_each"], 1_227)
        self.assertEqual(mechanics["single_class_P15_paths"], 60)
        self.assertEqual(mechanics["multiple_class_P15_paths"], 4)
        self.assertEqual(mechanics["control_paths"], 4)
        self.assertEqual(mechanics["source_mutations_by_VR12A"], 0)

    def test_every_case_reaches_exact_route_without_mutation(self):
        for order in grammar.ORDERS:
            for case in grammar.CASES:
                with self.subTest(order=order, case=case):
                    source = grammar._build_case(case, order)
                    before = grammar.vr12a.vr2._canonical_source_bytes(source)
                    decision = grammar.discriminate_generated_source(source)
                    after = grammar.vr12a.vr2._canonical_source_bytes(source)
                    self.assertEqual(decision.route, grammar.CASE_ROUTES[case])
                    self.assertEqual(before, after)
                    self.assertEqual([field.name for field in fields(decision)], ["route"])

    def test_single_failure_witnesses_hit_exact_vr12a_p15(self):
        for case in grammar.SINGLE_CLASS_CASES:
            with self.subTest(case=case):
                source = grammar._build_case(case, "canonical")
                with self.assertRaises(grammar.vr12a.P15RunIndexRepairRefusal) as refusal:
                    grammar.vr12a.adapt_repaired_source(source)
                self.assertEqual(
                    (refusal.exception.route, refusal.exception.safe_reason),
                    grammar.EXPECTED_P15,
                )

    def test_ordered_classifier_is_mutually_discriminating(self):
        for index, case in enumerate(grammar.SINGLE_CLASS_CASES):
            source = grammar._build_case(case, "canonical")
            names = grammar._p15_names(source)
            self.assertEqual(len(names), 1)
            self.assertEqual(
                grammar._classify_identity_name(names[0]),
                grammar.RESULT_ROUTES[index],
            )
        multiple = grammar._build_case("multiple_identity_classes", "canonical")
        routes = {grammar._classify_identity_name(name) for name in grammar._p15_names(multiple)}
        self.assertGreater(len(routes), 1)

    def test_measurements_and_output_are_bounded(self):
        measured = self.report["measurements"]
        caps = self.contract["resource_caps"]
        self.assertEqual(measured["fixed_artifact_count"], 12)
        self.assertEqual(measured["fixed_artifact_bytes"], 224_681)
        self.assertEqual(measured["runtime_seconds"], 0.5)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024 * 1024)
        self.assertLessEqual(
            measured["generated_input_bytes"],
            caps["generated_input_bytes_maximum"],
        )
        self.assertLessEqual(
            measured["aggregate_output_bytes"],
            caps["aggregate_output_bytes_maximum"],
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

    def test_direct_refusal_inventory_meets_frozen_minimum(self):
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 70)
        self.assertTrue(set(refusals.values()).issubset(grammar.REFUSAL_ROUTES))
        for index in range(1, 24):
            self.assertIn(f"matrix_drift_{index:02d}", refusals)
        for index in range(1, 16):
            self.assertIn(f"public_firewall_{index:02d}", refusals)

    def test_public_report_is_strict_and_target_free(self):
        payload = grammar._canonical_json_bytes(self.report)
        decoded = json.loads(payload)
        grammar._validate_public_report(decoded)
        self.assertEqual(len(payload), self.report["measurements"]["aggregate_output_bytes"])
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
        with self.assertRaises(grammar.SuffixIdentityGrammarRefusal) as privacy:
            grammar._validate_public_report(leaked)
        self.assertEqual(privacy.exception.route, "MARC2VR15A-F04")

        changed = copy.deepcopy(self.report)
        changed["route_summary"]["route_counts"][grammar.RESULT_ROUTES[0]] = 3
        with self.assertRaises(grammar.SuffixIdentityGrammarRefusal) as shape:
            grammar._validate_public_report(changed)
        self.assertEqual(shape.exception.route, "MARC2VR15A-F04")

        with self.assertRaises(grammar.SuffixIdentityGrammarRefusal) as resource:
            grammar._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=self.contract,
            )
        self.assertEqual(resource.exception.route, "MARC2VR15A-F06")

    def test_deterministic_replay_with_fixed_resource_probes(self):
        replayed = grammar.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )
        self.assertEqual(
            grammar._canonical_json_bytes(replayed),
            grammar._canonical_json_bytes(self.report),
        )

    def test_claim_and_operation_boundaries_remain_closed(self):
        self.assertTrue(all(value == 0 for value in self.report["access_counters"].values()))
        self.assertTrue(all(self.report["acceptance_gates"].values()))
        claims = self.report["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_ceiling", "scientific_ceiling"}:
                self.assertFalse(value)
        gate = self.report["next_gate"]
        self.assertFalse(gate["future_private_discriminator_authorized"])
        self.assertFalse(gate["consumed_VR13P_or_VR14P_reuse_allowed"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_thread_and_cli_surfaces_are_strict(self):
        with self.assertRaises(grammar.SuffixIdentityGrammarRefusal) as thread:
            grammar._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR15A-F06")
        parser = grammar._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["inspect"]).command, "inspect")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        options = {option for action in parser._actions for option in action.option_strings}
        self.assertNotIn("--path", options)
        self.assertNotIn("--output", options)
        self.assertNotIn("--execute", options)


if __name__ == "__main__":
    unittest.main()
