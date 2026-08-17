import copy
import json
import unittest

from neurodecodekit.datasets import marc2_f03_predicate_decomposition as f03

THREAD_ENV = {name: "1" for name in f03.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((100.0, 100.25))
    return lambda: next(values)


class Marc2F03PredicateDecompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = f03.load_registered_contract()
        cls.report = f03.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )

    def test_plan_is_bounded_and_has_no_private_authority(self):
        plan = f03.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR10A")
        self.assertEqual(plan["leaf_predicates"], 20)
        self.assertEqual(plan["excluded_predicates"], 15)
        self.assertEqual(plan["unresolved_predicates"], 5)
        self.assertEqual(plan["generated_cases"], 6)
        self.assertEqual(plan["required_paths"], 24)
        self.assertFalse(plan["private_access_authorized"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_bytes"], 0)

    def test_ast_inventory_matches_exact_twenty_leaf_partition(self):
        inventory = self.report["predicate_inventory"]
        self.assertEqual(len(inventory), 20)
        self.assertEqual(
            [row["predicate_id"] for row in inventory],
            [row.predicate_id for row in f03.PREDICATE_SIGNATURES],
        )
        statuses = [row["status"] for row in inventory]
        self.assertEqual(statuses.count("excluded_by_committed_evidence"), 15)
        self.assertEqual(statuses.count("unresolved_source_dependent"), 5)
        self.assertEqual(
            [
                row["predicate_id"]
                for row in inventory
                if row["status"] == "unresolved_source_dependent"
            ],
            [
                "F03P03_member_name_UTF8_length_at_most_1024",
                "F03P15_suffix_bearing_BIDS_identity",
                "F03P16_exact_freewill_task_token",
                "F03P18_unique_logical_run_companion",
                "F03P19_complete_four_companion_set",
            ],
        )

    def test_all_five_witnesses_relay_only_outer_f02_nested_f03(self):
        matrix = self.report["witness_matrix"]
        self.assertEqual([row["case"] for row in matrix], list(f03.CASES))
        control = matrix[0]
        self.assertEqual(control["disposition"], "VR6_success")
        self.assertEqual(control["outer_VR6_route"], "VR6_success")
        self.assertIsNone(control["nested_VR2_route"])
        self.assertIsNone(control["predicate_id"])
        for row in matrix[1:]:
            self.assertEqual(row["disposition"], "aggregate_refusal")
            self.assertEqual(row["outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["nested_VR2_route"], "MARC2VR2-F03")
            self.assertEqual(row["predicate_id"], f03.CASE_PREDICATES[row["case"]])
            self.assertEqual(len(row["outcome_digest_sha256"]), 64)

    def test_replay_counts_and_exact_parser_mechanics_are_frozen(self):
        replay = self.report["replay_summary"]
        self.assertEqual(replay["exact_replays"], 2)
        self.assertEqual(replay["paths_per_replay"], 12)
        self.assertEqual(replay["total_paths"], 24)
        self.assertEqual(replay["exact_parser_entry_visits"], 29_448)
        self.assertEqual(replay["exact_VR6_calls"], 24)
        self.assertEqual(replay["control_success_paths"], 4)
        self.assertEqual(replay["nested_F03_paths"], 20)
        self.assertTrue(replay["route_and_mechanics_replay_byte_identical"])
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["entry_count_each"], 1_227)
        self.assertEqual(mechanics["regular_file_rows_each"], 1_025)
        self.assertEqual(mechanics["directory_rows_each"], 202)
        self.assertEqual(mechanics["witness_mutations_before_exact_parser"], 20)
        self.assertEqual(mechanics["control_paths_without_witness_mutation"], 4)
        self.assertEqual(mechanics["post_parser_witness_mutations"], 0)
        self.assertEqual(
            mechanics["synthetic_normalization_fields"],
            ["transport_body_sha256"],
        )
        self.assertEqual(mechanics["member_local_header_bytes"], 0)
        self.assertEqual(mechanics["member_payload_bytes"], 0)

    def test_measurements_and_output_are_bounded(self):
        measurements = self.report["measurements"]
        caps = self.contract["resource_caps"]
        self.assertEqual(measurements["fixed_artifact_count"], 17)
        self.assertEqual(measurements["fixed_artifact_bytes"], 480_963)
        self.assertEqual(measurements["runtime_seconds"], 0.25)
        self.assertEqual(measurements["peak_RSS_bytes"], 64 * 1024 * 1024)
        self.assertLessEqual(
            measurements["generated_input_bytes"], caps["generated_input_bytes"]
        )
        self.assertLessEqual(
            measurements["aggregate_output_bytes"], caps["aggregate_output_bytes"]
        )
        self.assertEqual(measurements["retained_generated_output_bytes"], 0)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)
        self.assertEqual(measurements["raw_data_reads"], 0)
        self.assertEqual(measurements["real_cache_reads"], 0)
        self.assertEqual(measurements["model_runs"], 0)
        self.assertEqual(measurements["training_runs"], 0)
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_every_forbidden_operation_and_claim_remains_zero(self):
        self.assertTrue(all(value == 0 for value in self.report["access_counters"].values()))
        self.assertTrue(all(self.report["acceptance_gates"].values()))
        claims = self.report["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_ceiling", "scientific_ceiling"}:
                self.assertFalse(value)
        next_gate = self.report["next_gate"]
        self.assertFalse(next_gate["future_private_discriminator_authorized"])
        self.assertFalse(next_gate["consumed_VR9P_reuse_allowed"])
        self.assertFalse(next_gate["F03_rule_relaxation_allowed"])
        self.assertFalse(next_gate["MARC2_FW2_or_CIL1_authorized"])

    def test_direct_refusal_inventory_exceeds_frozen_minimum(self):
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 40)
        self.assertTrue(set(refusals.values()).issubset(set(f03.REFUSAL_ROUTES)))
        for signature in f03.PREDICATE_SIGNATURES:
            self.assertIn(f"missing_{signature.predicate_id}", refusals)

    def test_deterministic_replay_with_fixed_resource_probes(self):
        replayed = f03.qualify_generated(
            clock=deterministic_clock(),
            rss_reader=lambda: 64 * 1024 * 1024,
            environment=THREAD_ENV,
        )
        self.assertEqual(
            f03._canonical_json_bytes(replayed),
            f03._canonical_json_bytes(self.report),
        )

    def test_contract_partition_and_report_mutations_refuse(self):
        changed = copy.deepcopy(self.contract)
        changed["partition_summary"]["unresolved_source_dependent"] = 4
        with self.assertRaises(f03.F03PredicateDecompositionRefusal) as partition:
            f03._verify_contract_mapping(changed)
        self.assertEqual(partition.exception.route, "MARC2VR10A-F02")

        changed_report = copy.deepcopy(self.report)
        changed_report["witness_matrix"][1]["nested_VR2_route"] = "MARC2VR2-F04"
        with self.assertRaises(f03.F03PredicateDecompositionRefusal) as route:
            f03._validate_public_report(changed_report)
        self.assertEqual(route.exception.route, "MARC2VR10A-F05")

        leaked = copy.deepcopy(self.report)
        leaked["member_name"] = "hidden"
        with self.assertRaises(f03.F03PredicateDecompositionRefusal) as privacy:
            f03._validate_public_report(leaked)
        self.assertEqual(privacy.exception.route, "MARC2VR10A-F05")

    def test_thread_and_resource_drift_refuse_closed(self):
        with self.assertRaises(f03.F03PredicateDecompositionRefusal) as thread:
            f03._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR10A-F06")
        with self.assertRaises(f03.F03PredicateDecompositionRefusal) as resource:
            f03._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=self.contract,
            )
        self.assertEqual(resource.exception.route, "MARC2VR10A-F06")

    def test_cli_surface_has_no_path_or_execute_arguments(self):
        parser = f03._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        option_strings = {
            option
            for action in parser._actions
            for option in action.option_strings
        }
        self.assertNotIn("--path", option_strings)
        self.assertNotIn("--output", option_strings)
        self.assertNotIn("--execute", option_strings)

    def test_public_report_is_strict_json_and_contains_no_private_shapes(self):
        payload = f03._canonical_json_bytes(self.report)
        decoded = json.loads(payload)
        self.assertEqual(decoded["route"], "MARC2VR10A-G1")
        f03._validate_public_report(decoded)
        lowered = payload.decode("ascii").lower()
        self.assertNotIn(".codex_work", lowered)
        self.assertNotIn('"member_name":', lowered)
        self.assertNotIn('"private_manifest":', lowered)
        self.assertNotIn('"target":', lowered)
        self.assertNotIn('"prediction":', lowered)


if __name__ == "__main__":
    unittest.main()
