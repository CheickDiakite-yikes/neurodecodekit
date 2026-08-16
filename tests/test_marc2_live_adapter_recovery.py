import hashlib
import inspect
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from neurodecodekit.datasets import marc2_live_schema_adapter as la1
from neurodecodekit.datasets import marc2_live_schema_adapter_recovery as live
from neurodecodekit.datasets.marc2_freewill_prefix_selection import (
    select_generated_prefix,
)
from neurodecodekit.datasets.marc2_proof_record_recovery import (
    validate_implementation_record,
)


ROOT = Path(__file__).resolve().parents[1]


class Marc2LiveAdapterRecoveryTests(unittest.TestCase):
    def test_plan_is_fixed_and_stops_before_payload(self):
        plan = live.registered_plan()
        self.assertEqual(plan["lane_id"], "MARC2-LA2")
        self.assertEqual(plan["private_source_bytes"], 418_755)
        self.assertEqual(plan["proof_certificate_mutations"], 32)
        self.assertEqual(plan["executor_mutations"], 24)
        self.assertEqual(plan["total_direct_mutations"], 56)
        self.assertEqual(plan["proof_certificate_lane_id"], "MARC2-FW1B")
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["archive_local_header_or_member_bytes"], 0)
        self.assertEqual(plan["signal_target_model_or_score_operations"], 0)
        self.assertFalse(plan["MARC2_FW2_authorized"])

    def test_green_decision_is_exact_and_authorizes_no_payload(self):
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["lane_id"], "MARC2-LA2")
        self.assertEqual(
            decision["user_authorization"]["actual_message_verbatim"],
            "continue",
        )
        self.assertFalse(
            decision["authorization"][
                "archive_local_header_member_or_payload_access_authorized_now"
            ]
        )

    def test_module_is_dependency_free_and_has_no_consumed_executor_surface(self):
        source = inspect.getsource(live)
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import torch",
            "marc2_freewill_private_selection",
            "live_selection_v0",
            "live_selection_recovery_v1",
        ):
            self.assertNotIn(forbidden, source)

    def test_module_imports_without_site_packages(self):
        command = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'src')!r}); "
            "import neurodecodekit.datasets.marc2_live_schema_adapter_recovery as m; "
            "assert m.LANE_ID == 'MARC2-LA2'"
        )
        result = subprocess.run(
            [sys.executable, "-S", "-c", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_exact_green_public_symbols_are_imported(self):
        self.assertIs(live.adapt_live_shaped_source, la1.adapt_live_shaped_source)
        self.assertIs(live.select_generated_prefix, select_generated_prefix)
        self.assertIs(
            live.validate_implementation_record,
            validate_implementation_record,
        )

    def test_source_exposes_no_generic_private_or_payload_override(self):
        source = inspect.getsource(live._build_parser)
        for forbidden in (
            "--source",
            "--participant",
            "--subject",
            "--seed",
            "--cap",
            "--url",
            "--credential",
            "--member",
            "--payload",
        ):
            self.assertNotIn(forbidden, source)

    def test_registered_path_code_never_resolves_lists_or_globs(self):
        for function in (
            live._assert_source_components,
            live._preflight_private_source,
            live.read_locked_private_manifest,
            live.execute_registered_private_selection,
        ):
            source = inspect.getsource(function)
            self.assertNotIn(".resolve(", source)
            self.assertNotIn(".glob(", source)
            self.assertNotIn("listdir", source)
            self.assertNotIn("iterdir", source)

    def test_generated_live_source_uses_exact_live_identity(self):
        manifest = live.build_generated_live_source()
        self.assertEqual(manifest["schema_name"], live.PRIVATE_SOURCE_SCHEMA)
        self.assertEqual(
            manifest["proof_posture"],
            "live_archive_private_central_directory_metadata_only",
        )
        self.assertEqual(manifest["source_identity"]["provider"], "Figshare")
        self.assertEqual(manifest["source_identity"]["file_id"], 57_518_986)
        self.assertEqual(len(manifest["entries"]), 1_227)

    def test_exact_adapter_and_selector_recover_frozen_generated_prefix(self):
        manifest = live.build_generated_live_source()
        selected = live.adapt_and_select(
            manifest,
            source_file_sha256=live._generated_source_file_sha256(manifest),
        )
        result = selected.selector_result
        self.assertEqual(result.cohort_summary["selected_subjects"], 16)
        self.assertEqual(result.split_summary["selected_run_bundles"], 96)
        self.assertEqual(result.split_summary["selected_core_members"], 384)
        self.assertEqual(selected.adapter_calls, 1)
        self.assertEqual(selected.selector_calls, 1)
        self.assertEqual(
            selected.private_manifest["schema_name"],
            live.PRIVATE_SELECTION_SCHEMA_NAME,
        )

    def test_adapter_and_selector_calls_are_single_source_operations(self):
        source = inspect.getsource(live.adapt_and_select)
        self.assertEqual(source.count("adapter_fn(source)"), 1)
        self.assertEqual(source.count("selector_fn(adapted)"), 1)

    def test_reversed_rows_replay_selection_identity_and_private_rows(self):
        first_source = live.build_generated_live_source(row_order="canonical")
        replay_source = live.build_generated_live_source(row_order="reversed")
        first = live.adapt_and_select(
            first_source,
            source_file_sha256=live._generated_source_file_sha256(first_source),
        )
        replay = live.adapt_and_select(
            replay_source,
            source_file_sha256=live._generated_source_file_sha256(replay_source),
        )
        live._assert_replay(first, replay)
        self.assertEqual(
            first.selector_result.selection_hashes,
            replay.selector_result.selection_hashes,
        )
        self.assertEqual(
            first.private_manifest["rows"],
            replay.private_manifest["rows"],
        )

    def test_all_twenty_four_executor_mutations_refuse_in_order(self):
        routes = live.run_executor_mutations()
        self.assertEqual(tuple(routes), live.EXECUTOR_MUTATIONS)
        self.assertEqual(len(routes), 24)
        self.assertTrue(all(route in live.FAILURE_ROUTES for route in routes.values()))

    def test_executor_mutations_cover_every_registered_route_class(self):
        counts = Counter(live.run_executor_mutations().values())
        self.assertEqual(set(counts), set(live.FAILURE_ROUTES))
        self.assertEqual(sum(counts.values()), 24)

    def test_actual_native_registry_and_distinct_certificate_validate(self):
        records = live.validate_local_qualification_records(ROOT)
        self.assertEqual(records["native_record"]["lane_id"], "MARC2-LA2")
        self.assertEqual(records["certificate_record"]["lane_id"], "MARC2-FW1B")
        self.assertEqual(
            records["certificate_summary"]["validator_symbol"],
            validate_implementation_record.__name__,
        )
        self.assertEqual(records["canonical_shared_validator_calls"], 2)

    def test_generated_qualification_and_inspection_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification"
            outcome = live.qualify_generated_mock_executor(
                output,
                environ={key: "1" for key in live.THREAD_ENV_KEYS},
                rss_probe=lambda: 1,
            )
            summary = live.inspect_public_result(outcome.report_path)
            self.assertEqual(summary["route"], live.GENERATED_ROUTE)
            self.assertEqual(summary["selected_subjects"], 16)
            self.assertEqual(summary["selected_run_bundles"], 96)
            self.assertEqual(summary["selected_core_members"], 384)
            self.assertLess(outcome.output_bytes, live.MAX_COMBINED_OUTPUT_BYTES)
            self.assertEqual(
                stat.S_IMODE(os.lstat(outcome.private_selection_path).st_mode),
                0o600,
            )
            self.assertFalse(any(outcome.report["access_counters"].values()))

    def test_generated_qualification_passes_all_fifty_six_direct_refusals(self):
        with tempfile.TemporaryDirectory() as temporary:
            outcome = live.qualify_generated_mock_executor(
                Path(temporary) / "qualification",
                environ={key: "1" for key in live.THREAD_ENV_KEYS},
                rss_probe=lambda: 1,
            )
            summary = outcome.report["mutation_summary"]
            self.assertEqual(summary["proof_certificate_passed"], 32)
            self.assertEqual(summary["executor_passed"], 24)
            self.assertEqual(summary["total_direct_passed"], 56)
            self.assertEqual(len(summary["executor_names"]), 24)

    def test_qualification_rejects_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.qualify_generated_mock_executor(temporary)
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[1])

    def test_public_report_rejects_private_key(self):
        with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
            live._walk_public({"member_name": "private"})
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_public_inspector_rejects_private_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "private.json"
            path.write_bytes(
                live._canonical_json_bytes(
                    {
                        "schema_name": live.PRIVATE_SELECTION_SCHEMA_NAME,
                        "schema_version": live.SCHEMA_VERSION,
                    }
                )
            )
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.inspect_public_result(path)
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_combined_output_cap_refuses_one_byte_over(self):
        with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
            live._bounded_output_bytes(b"x" * (live.MAX_COMBINED_OUTPUT_BYTES + 1))
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_locked_reader_uses_one_open_read_hash_and_parse(self):
        payload = live._canonical_json_bytes({"schema_name": "fixture"})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            observed = live._preflight_private_source(
                path,
                expected_bytes=len(payload),
            )
            counters = live._base_access_counters()
            value, actual = live.read_locked_private_manifest(
                path,
                expected_stat=observed,
                expected_bytes=len(payload),
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                counters=counters,
            )
        self.assertEqual(value["schema_name"], "fixture")
        self.assertEqual(actual, payload)
        self.assertEqual(counters["private_manifest_content_opens"], 1)
        self.assertEqual(counters["private_manifest_body_reads"], 1)
        self.assertEqual(counters["private_manifest_hashes"], 1)
        self.assertEqual(counters["private_manifest_parses"], 1)

    def test_locked_reader_accepts_short_chunks_without_reopen(self):
        payload = live._canonical_json_bytes({"schema_name": "fixture"})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            observed = live._preflight_private_source(
                path,
                expected_bytes=len(payload),
            )

            def short_reader(descriptor, size):
                return os.read(descriptor, min(size, 3))

            value, actual = live.read_locked_private_manifest(
                path,
                expected_stat=observed,
                expected_bytes=len(payload),
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                counters=live._base_access_counters(),
                body_reader=short_reader,
            )
        self.assertEqual(value["schema_name"], "fixture")
        self.assertEqual(actual, payload)

    def test_locked_reader_rejects_duplicate_json(self):
        payload = b'{"x":1,"x":2}\n'
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            observed = live._preflight_private_source(
                path,
                expected_bytes=len(payload),
            )
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.read_locked_private_manifest(
                    path,
                    expected_stat=observed,
                    expected_bytes=len(payload),
                    expected_sha256=hashlib.sha256(payload).hexdigest(),
                    counters=None,
                )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[2])

    def test_locked_reader_rejects_fstat_identity_race(self):
        payload = b"{}\n"
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            observed = live._preflight_private_source(
                path,
                expected_bytes=len(payload),
            )
            values = list(observed)
            values[1] += 1
            changed = os.stat_result(values)
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.read_locked_private_manifest(
                    path,
                    expected_stat=observed,
                    expected_bytes=len(payload),
                    expected_sha256=hashlib.sha256(payload).hexdigest(),
                    counters=None,
                    fstat_reader=lambda _descriptor: changed,
                )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[2])

    def test_machine_gate_accepts_exact_generated_caps(self):
        disk = SimpleNamespace(free=live.MINIMUM_FREE_DISK_BYTES)
        result = live.preconsumption_machine_gate(
            ROOT,
            environ={key: "1" for key in live.THREAD_ENV_KEYS},
            disk_usage_reader=lambda _path: disk,
            cpu_count_reader=lambda: 8,
            loadavg_reader=lambda: (8.0, 0.0, 0.0),
            rss_reader=lambda: live.MAX_PEAK_RSS_BYTES,
        )
        self.assertTrue(result["passed_before_consumed_marker"])
        self.assertEqual(result["one_minute_load_per_logical_CPU"], 1.0)

    def test_machine_gate_rejects_thread_expansion(self):
        with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
            live.preconsumption_machine_gate(
                ROOT,
                environ={key: "2" for key in live.THREAD_ENV_KEYS},
            )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[1])

    def test_live_execution_refuses_malformed_proof_before_private_access(self):
        evidence = live.GreenImplementationEvidence(
            implementation_commit="bad",
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="0" * 64,
            proof_certificate_sha256="1" * 64,
        )
        with mock.patch.object(
            live,
            "_assert_source_components",
            side_effect=AssertionError("private source must remain closed"),
        ):
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.execute_registered_private_selection(
                    ROOT,
                    evidence=evidence,
                    output_root=ROOT / live.OUTPUT_ROOT_RELATIVE_PATH,
                    environ={key: "1" for key in live.THREAD_ENV_KEYS},
                )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[0])

    def test_green_verifier_preserves_registered_proof_order(self):
        source = inspect.getsource(live.verify_green_implementation)
        decision = source.index("load_green_decision")
        first_certificate = source.index("validate_proof_certificate")
        native_registry = source.index("load_implementation_record")
        git_observation = source.index("_git(")
        final_certificate = source.rindex("validate_proof_certificate")
        self.assertLess(decision, first_certificate)
        self.assertLess(first_certificate, native_registry)
        self.assertLess(native_registry, git_observation)
        self.assertLess(git_observation, final_certificate)

    def test_live_execution_proves_implementation_before_output_identity(self):
        evidence = live.GreenImplementationEvidence(
            implementation_commit="1" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="2" * 64,
            proof_certificate_sha256="3" * 64,
        )
        order = []

        def verified(*_args, **_kwargs):
            order.append("proof")
            return {}

        def output_checked(*_args, **_kwargs):
            order.append("output")
            raise live.LiveAdapterRecoveryRefusal(
                live.FAILURE_ROUTES[1],
                "fixture output refusal",
            )

        with (
            mock.patch.object(live, "verify_green_implementation", side_effect=verified),
            mock.patch.object(
                live,
                "_assert_registered_output_root",
                side_effect=output_checked,
            ),
        ):
            with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                live.execute_registered_private_selection(
                    ROOT,
                    evidence=evidence,
                    output_root=ROOT / "wrong",
                    environ={key: "1" for key in live.THREAD_ENV_KEYS},
                )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[1])
        self.assertEqual(order, ["proof", "output"])

    def test_consumed_failure_writes_one_aggregate_report_without_retry(self):
        evidence = live.GreenImplementationEvidence(
            implementation_commit="1" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="2" * 64,
            proof_certificate_sha256="3" * 64,
        )
        machine = {
            "passed_before_consumed_marker": True,
            "free_disk_bytes": live.MINIMUM_FREE_DISK_BYTES,
            "logical_CPUs": 8,
            "one_minute_load": 0.0,
            "one_minute_load_per_logical_CPU": 0.0,
            "peak_RSS_bytes_before_consumption": 1,
            "CPU_threads": 1,
            "workers": 1,
            "numerical_jobs": 1,
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".codex_work").mkdir()
            destination = root / live.OUTPUT_ROOT_RELATIVE_PATH
            fixture_stat = SimpleNamespace(
                st_dev=1,
                st_ino=1,
                st_uid=os.getuid(),
                st_mode=stat.S_IFREG | 0o600,
                st_size=live.PRIVATE_SOURCE_BYTES,
            )
            with (
                mock.patch.object(live, "verify_green_implementation", return_value={}),
                mock.patch.object(
                    live,
                    "preconsumption_machine_gate",
                    return_value=machine,
                ),
                mock.patch.object(
                    live,
                    "_assert_source_components",
                    return_value=root / "source.json",
                ),
                mock.patch.object(
                    live,
                    "_preflight_private_source",
                    return_value=fixture_stat,
                ),
                mock.patch.object(
                    live,
                    "read_locked_private_manifest",
                    side_effect=live.LiveAdapterRecoveryRefusal(
                        live.FAILURE_ROUTES[2],
                        "fixture refusal",
                    ),
                ),
            ):
                with self.assertRaises(live.LiveAdapterRecoveryRefusal) as caught:
                    live.execute_registered_private_selection(
                        root,
                        evidence=evidence,
                        output_root=destination,
                        environ={key: "1" for key in live.THREAD_ENV_KEYS},
                        rss_probe=lambda: 1,
                    )
            summary = live.inspect_public_result(
                destination / live.AGGREGATE_REPORT_NAME
            )
            self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[2])
            self.assertEqual(summary["route"], live.FAILURE_ROUTES[2])
            self.assertTrue((destination / live.CONSUMED_MARKER_NAME).is_file())
            self.assertFalse((destination / live.PRIVATE_SELECTION_NAME).exists())

    def test_cli_help_exposes_only_fixed_commands(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_live_schema_adapter_recovery",
                "--help",
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("plan", "qualify", "inspect", "execute"):
            self.assertIn(command, result.stdout)

    def test_fixed_dependency_hashes_are_current(self):
        self.assertEqual(
            live._sha256_file(ROOT / live.LIVE_ADAPTER_MODULE_RELATIVE_PATH),
            live.LIVE_ADAPTER_MODULE_SHA256,
        )
        self.assertEqual(
            live._sha256_file(ROOT / live.PROOF_MODULE_RELATIVE_PATH),
            live.PROOF_MODULE_SHA256,
        )
        self.assertEqual(
            live._sha256_file(ROOT / live.SELECTOR_MODULE_RELATIVE_PATH),
            live.SELECTOR_MODULE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
