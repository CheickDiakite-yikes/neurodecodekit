import ast
import copy
import io
import os
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_generated_diagnostic_relay as relay


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in relay.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((10.0, 14.0))
    return lambda: next(values)


class Marc2GeneratedDiagnosticRelayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (
            mock.patch.dict(os.environ, THREAD_ENV, clear=False),
            mock.patch.object(
                relay.parser,
                "parse_central_directory",
                wraps=relay.parser.parse_central_directory,
            ) as parse_spy,
            mock.patch.object(
                relay.producer,
                "_run_generated_path",
                wraps=relay.producer._run_generated_path,
            ) as producer_spy,
            mock.patch.object(
                relay.producer,
                "_private_manifest",
                wraps=relay.producer._private_manifest,
            ) as manifest_spy,
            mock.patch.object(
                relay.vr6,
                "adapt_dynamic_live_source",
                wraps=relay.vr6.adapt_dynamic_live_source,
            ) as vr6_spy,
        ):
            cls.report = relay.qualify_generated(
                repo_root=ROOT,
                clock=deterministic_clock(),
                rss_reader=lambda: 64 * 1024**2,
                environment=THREAD_ENV,
            )
            cls.traversal_calls = {
                "parser": parse_spy.call_count,
                "producer": producer_spy.call_count,
                "manifest": manifest_spy.call_count,
                "VR6": vr6_spy.call_count,
            }

    def test_plan_is_generated_only_and_registration_bound(self):
        plan = relay.build_plan_summary(repo_root=ROOT)
        self.assertEqual(plan["lane_id"], "MARC2-VR8B")
        self.assertEqual(plan["fixed_input_count"], 17)
        self.assertEqual(plan["fixed_input_bytes"], 622_989)
        self.assertEqual(plan["generated_matrix_paths_per_replay"], 8)
        self.assertEqual(plan["exact_replays"], 2)
        self.assertFalse(plan["private_access_authorized"])
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["real_or_private_bytes"], 0)

    def test_exact_parser_producer_and_VR6_are_traversed_for_all_paths(self):
        self.assertEqual(
            self.traversal_calls,
            {"parser": 16, "producer": 16, "manifest": 16, "VR6": 16},
        )
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["paths_per_replay"], 8)
        self.assertEqual(mechanics["exact_parser_entry_visits_per_replay"], 9_816)
        self.assertEqual(mechanics["entry_count_each"], 1_227)
        self.assertEqual(mechanics["regular_file_rows_each"], 1_025)
        self.assertEqual(mechanics["directory_rows_each"], 202)
        self.assertEqual(mechanics["member_local_header_bytes"], 0)
        self.assertEqual(mechanics["member_payload_bytes"], 0)

    def test_two_layer_route_matrix_is_exact(self):
        matrix = self.report["route_matrix"]
        self.assertEqual([row["case"] for row in matrix], list(relay.CASES))
        self.assertEqual(matrix[0]["disposition"], "VR6_success")
        self.assertEqual(matrix[0]["selected_subject_count"], 16)
        self.assertEqual(matrix[0]["selected_run_bundles"], 96)
        for row, nested in zip(
            matrix[1:],
            ("MARC2VR2-F02", "MARC2VR2-F03", "MARC2VR2-F04"),
            strict=True,
        ):
            self.assertEqual(row["disposition"], "aggregate_refusal")
            self.assertEqual(row["outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["nested_VR2_route"], nested)
            self.assertNotIn("reason", row)

    def test_normalized_cohort_identity_is_order_neutral(self):
        vr2_contract = relay.vr2.load_registered_contract(ROOT)
        selector_contract = relay.selector.load_registered_contract(ROOT)
        selections = []
        for order in relay.ORDERS:
            composed = relay._compose_source(
                "success",
                order,
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
            )
            selection = relay.vr6.adapt_dynamic_live_source(
                composed.source,
                vr2_contract=vr2_contract,
                selector_contract=selector_contract,
            )
            selections.append(selection)
            self.assertEqual(
                composed.synthetic_normalization_fields,
                ("transport_body_sha256",),
            )
        self.assertNotEqual(
            selections[0].selection_hashes["selection_identity_sha256"],
            selections[1].selection_hashes["selection_identity_sha256"],
        )
        self.assertEqual(
            relay._normalized_success_identity_sha256(selections[0]),
            relay._normalized_success_identity_sha256(selections[1]),
        )

    def test_VR6_does_not_mutate_composed_source(self):
        vr2_contract = relay.vr2.load_registered_contract(ROOT)
        selector_contract = relay.selector.load_registered_contract(ROOT)
        composed = relay._compose_source(
            "success",
            "canonical",
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
        before = copy.deepcopy(composed.source)
        relay.vr6.adapt_dynamic_live_source(
            composed.source,
            vr2_contract=vr2_contract,
            selector_contract=selector_contract,
        )
        self.assertEqual(composed.source, before)

    def test_measurements_caps_and_forbidden_operations_are_exact(self):
        measured = self.report["measurements"]
        self.assertEqual(measured["fixed_artifact_count"], 20)
        self.assertEqual(measured["fixed_artifact_bytes"], 648_432)
        self.assertEqual(measured["generated_input_bytes"], 4_650_480)
        self.assertEqual(measured["runtime_seconds"], 4.0)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(
            (measured["CPU_threads"], measured["workers"], measured["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertEqual(measured["raw_data_reads"], 0)
        self.assertEqual(measured["real_cache_reads"], 0)
        self.assertEqual(measured["model_runs"], 0)
        self.assertEqual(measured["training_runs"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertTrue(all(value == 0 for value in self.report["access_counters"].values()))

    def test_all_acceptance_gates_and_direct_refusals_pass(self):
        self.assertTrue(all(self.report["acceptance_gates"].values()))
        refusals = self.report["direct_refusals"]
        self.assertGreaterEqual(len(refusals), 24)
        for required in (
            "deterministic_replay_mismatch",
            "synthetic_normalization_field_drift",
            "thread_binding_drift",
            "local_interval_overlap",
            "private_path_leak",
            "runtime_cap_drift",
        ):
            self.assertIn(required, refusals)
        self.assertEqual(set(refusals.values()), set(relay.REFUSAL_ROUTES))

    def test_qualification_replays_byte_identically_with_fixed_probes(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            replayed = relay.qualify_generated(
                repo_root=ROOT,
                clock=deterministic_clock(),
                rss_reader=lambda: 64 * 1024**2,
                environment=THREAD_ENV,
            )
        self.assertEqual(
            relay._canonical_json_bytes(self.report),
            relay._canonical_json_bytes(replayed),
        )

    def test_thread_and_resource_drift_refuse_closed(self):
        with self.assertRaises(relay.GeneratedDiagnosticRelayRefusal) as thread:
            relay._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR8B-F06")
        contract = relay.load_registered_contract(ROOT)
        with self.assertRaises(relay.GeneratedDiagnosticRelayRefusal) as resource:
            relay._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                retained_output_bytes=0,
                contract=contract,
            )
        self.assertEqual(resource.exception.route, "MARC2VR8B-F06")

    def test_public_firewall_rejects_paths_identities_and_reasons(self):
        for value in (
            {"reason": "hidden"},
            {"member_name": "hidden"},
            {"participant_id": "hidden"},
            {"warning": ".codex_work/hidden"},
            {"warning": "sub-01"},
            {"target": "hidden"},
        ):
            with self.subTest(value=value):
                with self.assertRaises(relay.GeneratedDiagnosticRelayRefusal) as caught:
                    relay._validate_public_value(value)
                self.assertEqual(caught.exception.route, "MARC2VR8B-F04")

    def test_malformed_success_or_refusal_rows_are_rejected(self):
        for mutate in (
            lambda value: value["route_matrix"][0].__setitem__(
                "selected_subject_count", 15
            ),
            lambda value: value["route_matrix"][0].__setitem__("reason", "hidden"),
            lambda value: value["route_matrix"][1].__setitem__(
                "nested_VR2_route", "MARC2VR2-F04"
            ),
        ):
            changed = copy.deepcopy(self.report)
            mutate(changed)
            with self.assertRaises(relay.GeneratedDiagnosticRelayRefusal):
                relay._validate_public_report(changed)

    def test_cli_has_only_plan_and_qualify_without_io_arguments(self):
        parser = relay._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        with mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                parser.parse_args(["execute"])
        destinations = {action.dest for action in parser._actions}
        self.assertNotIn("path", destinations)
        self.assertNotIn("url", destinations)
        self.assertNotIn("output", destinations)
        stdout = io.StringIO()
        with mock.patch("sys.stdout", stdout):
            self.assertEqual(relay.main(["plan"]), 0)
        self.assertIn('"private_access_authorized":false', stdout.getvalue())

    def test_module_has_no_consumed_executor_network_or_heavy_surface(self):
        module_path = (
            ROOT / "src/neurodecodekit/datasets/marc2_generated_diagnostic_relay.py"
        )
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imported.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )
        self.assertFalse(imported & relay.FORBIDDEN_IMPORT_ROOTS)
        self.assertNotIn("marc2_dynamic_private_selection_recovery", source)
        self.assertNotIn("def execute", source)


if __name__ == "__main__":
    unittest.main()
