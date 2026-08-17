import ast
import io
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_two_layer_private_diagnostic as diagnostic


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in diagnostic.THREAD_ENVIRONMENT}


def deterministic_clock():
    values = iter((10.0, 14.0))
    return lambda: next(values)


class Marc2TwoLayerPrivateDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (
            mock.patch.dict(os.environ, THREAD_ENV, clear=False),
            mock.patch.object(
                diagnostic.relay,
                "_compose_source",
                wraps=diagnostic.relay._compose_source,
            ) as compose_spy,
            mock.patch.object(
                diagnostic.vr6,
                "adapt_dynamic_live_source",
                wraps=diagnostic.vr6.adapt_dynamic_live_source,
            ) as vr6_spy,
        ):
            cls.report = diagnostic.qualify_generated(
                repo_root=ROOT,
                clock=deterministic_clock(),
                rss_reader=lambda: 64 * 1024**2,
                environment=THREAD_ENV,
            )
            cls.compose_calls = compose_spy.call_count
            cls.vr6_calls = vr6_spy.call_count

    def test_plan_is_fixed_and_private_closed(self):
        plan = diagnostic.build_plan_summary()
        self.assertEqual(plan["lane_id"], "MARC2-VR9P")
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(
            plan["allowed_nested_routes"],
            ["MARC2VR2-F03", "MARC2VR2-F04"],
        )
        self.assertFalse(plan["private_manifest_or_cohort_output"])
        self.assertFalse(
            plan["generic_path_URL_threshold_retry_resume_or_fallback_argument"]
        )
        self.assertEqual(plan["network_archive_signal_target_or_model_bytes"], 0)
        self.assertFalse(plan["FW2_CIL1_neural_or_live_run_authorized"])

    def test_exact_generated_matrix_and_call_counts(self):
        self.assertEqual(self.compose_calls, 8)
        self.assertEqual(self.vr6_calls, 8)
        mechanics = self.report["mechanics"]
        self.assertEqual(mechanics["cases"], ["F03", "F04"])
        self.assertEqual(mechanics["orders"], ["canonical", "reversed"])
        self.assertEqual(mechanics["exact_replays"], 2)
        self.assertEqual(mechanics["paths_per_replay"], 4)
        self.assertEqual(mechanics["VR6_calls_per_path"], 1)
        self.assertEqual(mechanics["VR6_calls_total"], 8)
        self.assertEqual(mechanics["strict_JSON_parses_total"], 8)
        self.assertEqual(mechanics["private_manifest_or_cohort_outputs"], 0)

    def test_route_matrix_is_only_F03_or_F04(self):
        matrix = self.report["route_matrix"]
        self.assertEqual(
            [(row["case"], row["order"]) for row in matrix],
            [
                ("F03", "canonical"),
                ("F03", "reversed"),
                ("F04", "canonical"),
                ("F04", "reversed"),
            ],
        )
        for row in matrix:
            self.assertEqual(row["outer_VR6_route"], "MARC2VR6-F02")
            self.assertEqual(row["nested_VR2_route"], f"MARC2VR2-{row['case']}")
            self.assertEqual(
                row["route"],
                (
                    diagnostic.F03_RESULT_ROUTE
                    if row["case"] == "F03"
                    else diagnostic.F04_RESULT_ROUTE
                ),
            )
            self.assertEqual(
                row["output_files"],
                [diagnostic.MARKER_NAME, diagnostic.AGGREGATE_REPORT_NAME],
            )
            for forbidden in ("reason", "path", "candidate", "cohort"):
                self.assertNotIn(forbidden, row)

    def test_measurements_caps_and_zero_real_operations(self):
        measured = self.report["measurements"]
        self.assertEqual(measured["fixed_committed_artifact_reads"], 15)
        self.assertEqual(measured["generated_input_bytes"], 3_407_792)
        self.assertEqual(measured["runtime_seconds"], 4.0)
        self.assertEqual(measured["peak_RSS_bytes"], 64 * 1024**2)
        self.assertEqual(measured["retained_output_bytes"], 0)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
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

    def test_all_gates_and_seventy_direct_refusals_pass(self):
        self.assertTrue(all(self.report["acceptance_gates"].values()))
        refusals = self.report["direct_refusals"]
        self.assertEqual(len(refusals), 70)
        self.assertEqual(
            set(refusals.values()),
            {
                "MARC2VR9P-F01",
                "MARC2VR9P-F02",
                "MARC2VR9P-F06",
                "MARC2VR9P-F07",
                "MARC2VR9P-F08",
                "MARC2VR9P-F09",
            },
        )
        for name in (
            "decision_01",
            "implementation_18",
            "aggregate_16",
            "relay_06",
            "json_06",
            "resource_08",
            "path_04",
            "thread_02",
        ):
            self.assertIn(name, refusals)

    def test_qualification_replays_byte_identically_with_fixed_probes(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            replayed = diagnostic.qualify_generated(
                repo_root=ROOT,
                clock=deterministic_clock(),
                rss_reader=lambda: 64 * 1024**2,
                environment=THREAD_ENV,
            )
        self.assertEqual(
            diagnostic._canonical_json_bytes(self.report),
            diagnostic._canonical_json_bytes(replayed),
        )

    def test_route_firewall_rejects_success_F02_unknown_and_missing(self):
        for value in (
            mock.Mock(route="MARC2VR6-G1", upstream_route=None),
            mock.Mock(route="MARC2VR6-F02", upstream_route="MARC2VR2-F02"),
            mock.Mock(route="MARC2VR6-F02", upstream_route="MARC2VR2-F08"),
            mock.Mock(route="MARC2VR6-F02", upstream_route=None),
        ):
            with self.subTest(value=value):
                with self.assertRaises(diagnostic.TwoLayerDiagnosticRefusal) as caught:
                    diagnostic._relay_exception(value)
                self.assertEqual(caught.exception.route, "MARC2VR9P-F07")

    def test_public_firewall_rejects_private_context(self):
        for value in (
            {"reason": "hidden"},
            {"member_name": "hidden"},
            {"participant_id": "hidden"},
            {"warning": ".codex_work/hidden"},
            {"warning": "sub-01"},
            {"candidate": "hidden"},
            {"cohort": "hidden"},
        ):
            with self.subTest(value=value):
                self.assertTrue(diagnostic._contains_private_public_value(value))

    def test_strict_JSON_rejects_duplicate_nonfinite_and_nonobject(self):
        for payload in (b'{"a":1,"a":2}', b'{"a":NaN}', b"[]", b"null"):
            with self.subTest(payload=payload):
                with self.assertRaises(diagnostic.TwoLayerDiagnosticRefusal):
                    diagnostic._strict_json(payload, route="MARC2VR9P-F06")

    def test_thread_and_resource_drift_refuse_closed(self):
        with self.assertRaises(diagnostic.TwoLayerDiagnosticRefusal) as thread:
            diagnostic._validate_thread_environment({})
        self.assertEqual(thread.exception.route, "MARC2VR9P-F02")
        with self.assertRaises(diagnostic.TwoLayerDiagnosticRefusal) as resource:
            diagnostic._assert_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                generated_input_bytes=1,
                aggregate_output_bytes=1,
                combined_output_bytes=1,
                retained_output_bytes=0,
                maximum_runtime=30.0,
            )
        self.assertEqual(resource.exception.route, "MARC2VR9P-F09")

    def test_generated_readiness_certificate_is_current_and_bounded(self):
        base = datetime(2026, 8, 17, tzinfo=timezone.utc)
        certificate = diagnostic._build_readiness_certificate(
            diagnostic._generated_raw_samples(base),
            implementation_commit="a" * 40,
            thread_environment=THREAD_ENV,
        )
        diagnostic._validate_readiness_certificate(
            certificate,
            now_UTC=base.replace(second=10),
        )
        self.assertTrue(certificate["ready"])
        self.assertEqual(certificate["measurements"]["sample_count"], 3)
        self.assertLess(
            len(diagnostic._canonical_json_bytes(certificate)),
            diagnostic.readiness.MAX_CERTIFICATE_BYTES,
        )

    def test_nofollow_preflight_rejects_generated_symlink(self):
        generated_parent = Path(tempfile.gettempdir()).resolve(strict=True)
        with tempfile.TemporaryDirectory(dir=generated_parent) as temporary:
            root = Path(temporary)
            (root / "generated").mkdir()
            real = root / "generated/real.json"
            real.write_bytes(b"{}\n")
            real.chmod(0o600)
            link = root / "generated/source.json"
            link.symlink_to(real)
            identity = diagnostic.RegisteredFileIdentity(
                Path("generated/source.json"),
                0o600,
                3,
                diagnostic._sha256_bytes(b"{}\n"),
            )
            with self.assertRaises(diagnostic.TwoLayerDiagnosticRefusal) as caught:
                diagnostic._preflight_registered_file(
                    root, identity, "MARC2VR9P-F03"
                )
            self.assertEqual(caught.exception.route, "MARC2VR9P-F03")

    def test_cli_has_no_generic_IO_or_retry_arguments(self):
        parser = diagnostic._build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["qualify"]).command, "qualify")
        execute = parser.parse_args(
            [
                "execute",
                "--implementation-commit",
                "a" * 40,
                "--ci-run-id",
                "1",
                "--base-job-id",
                "2",
                "--optional-job-id",
                "3",
            ]
        )
        self.assertEqual(execute.command, "execute")
        destinations = {
            action.dest
            for command in parser._subparsers._group_actions
            for subparser in command.choices.values()
            for action in subparser._actions
        }
        for forbidden in ("path", "url", "output", "threshold", "retry", "resume"):
            self.assertNotIn(forbidden, destinations)
        stdout = io.StringIO()
        with mock.patch("sys.stdout", stdout):
            self.assertEqual(diagnostic.main(["plan"]), 0)
        self.assertIn('"private_manifest_or_cohort_output": false', stdout.getvalue())

    def test_module_has_no_consumed_executor_network_or_heavy_surface(self):
        module_path = (
            ROOT
            / "src/neurodecodekit/datasets/marc2_two_layer_private_diagnostic.py"
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
        self.assertFalse(imported & diagnostic.FORBIDDEN_IMPORT_ROOTS)
        consumed = "marc2_dynamic_" + "private_selection_recovery"
        self.assertNotIn(consumed, source)
        self.assertNotIn("urllib.request", source)

    def test_claim_boundary_stays_non_scientific(self):
        claim = self.report["claim_boundary"]
        self.assertEqual(claim["scientific_ceiling"], "none")
        self.assertFalse(claim["neural_effect"])
        self.assertFalse(claim["decoding_accuracy"])
        self.assertFalse(claim["language_or_thought_decoding"])


if __name__ == "__main__":
    unittest.main()
