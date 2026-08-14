import hashlib
import inspect
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from neurodecodekit.datasets import marc2_freewill_private_selection as live
from neurodecodekit.datasets import marc2_freewill_prefix_selection as selector


ROOT = Path(__file__).resolve().parents[1]


class Marc2FreewillPrivateSelectionTests(unittest.TestCase):
    def test_plan_is_fixed_and_stops_before_payload(self):
        plan = live.registered_plan()
        self.assertEqual(plan["lane_id"], "MARC2-FW1A")
        self.assertEqual(plan["private_source_bytes"], 418_755)
        self.assertEqual(plan["inherited_selector_mutations"], 40)
        self.assertEqual(plan["wrapper_mutations"], 18)
        self.assertEqual(plan["network_bytes"], 0)
        self.assertEqual(plan["archive_local_header_or_member_bytes"], 0)
        self.assertEqual(plan["signal_target_model_or_score_operations"], 0)

    def test_green_decision_is_exact_and_authorizes_no_payload(self):
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["lane_id"], "MARC2-FW1A")
        self.assertEqual(
            decision["user_authorization"]["actual_message_verbatim"],
            "continue",
        )
        self.assertFalse(
            decision["authorization"]["payload_acquisition_or_download_authorized_now"]
        )

    def test_module_is_dependency_free_and_has_no_consumed_executor_import(self):
        source = inspect.getsource(live)
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import torch",
            "marc1_pilot_selection_live",
            "marc1_central_directory_live",
        ):
            self.assertNotIn(forbidden, source)

    def test_module_imports_without_site_packages(self):
        command = (
            "import sys; "
            f"sys.path.insert(0, {str(ROOT / 'src')!r}); "
            "import neurodecodekit.datasets.marc2_freewill_private_selection as m; "
            "assert m.LANE_ID == 'MARC2-FW1A'"
        )
        result = subprocess.run(
            [sys.executable, "-S", "-c", command],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_source_exposes_no_generic_private_or_payload_override(self):
        source = inspect.getsource(live._build_parser)
        self.assertNotIn("--source", source)
        self.assertNotIn("--participant", source)
        self.assertNotIn("--subject", source)
        self.assertNotIn("--seed", source)
        self.assertNotIn("--cap", source)
        self.assertNotIn("--url", source)
        self.assertNotIn("--credential", source)
        self.assertNotIn("--member", source)
        self.assertNotIn("--payload", source)

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

    def test_generated_live_adapter_uses_exact_source_identity(self):
        manifest = live.build_generated_live_manifest()
        self.assertEqual(manifest["schema_name"], live.PRIVATE_SOURCE_SCHEMA)
        self.assertEqual(
            manifest["proof_posture"],
            "live_archive_private_central_directory_metadata_only",
        )
        self.assertEqual(manifest["source_identity"]["provider"], "Figshare")
        self.assertEqual(manifest["source_identity"]["file_id"], 57_518_986)
        self.assertEqual(len(manifest["entries"]), 1_227)

    def test_live_adapter_selects_frozen_generated_prefix_without_targets(self):
        manifest = live.build_generated_live_manifest()
        digest = hashlib.sha256(live._canonical_live_manifest_bytes(manifest)).hexdigest()
        selected = live.select_live_prefix(manifest, source_file_sha256=digest)
        self.assertEqual(selected.cohort_summary["selected_subjects"], 16)
        self.assertEqual(selected.split_summary["selected_run_bundles"], 96)
        self.assertEqual(selected.split_summary["selected_core_members"], 384)
        private = selected.private_manifest
        self.assertEqual(private["schema_name"], live.PRIVATE_SELECTION_SCHEMA_NAME)

        def walk_keys(value):
            if isinstance(value, dict):
                for key, nested in value.items():
                    yield key.lower()
                    yield from walk_keys(nested)
            elif isinstance(value, list):
                for nested in value:
                    yield from walk_keys(nested)

        for key in walk_keys(private):
            for forbidden in ("target", "label", "response", "sentence", "quality"):
                self.assertNotIn(forbidden, key)

    def test_reversed_rows_replay_selection_identity(self):
        first = live.build_generated_live_manifest()
        replay = live.build_generated_live_manifest(row_order="reversed")
        digest = hashlib.sha256(live._canonical_live_manifest_bytes(first)).hexdigest()
        first_result = live.select_live_prefix(first, source_file_sha256=digest)
        replay_result = live.select_live_prefix(replay, source_file_sha256=digest)
        self.assertEqual(first_result.cohort_summary, replay_result.cohort_summary)
        self.assertEqual(first_result.selection_hashes, replay_result.selection_hashes)
        self.assertEqual(
            live._canonical_json_bytes(first_result.private_manifest),
            live._canonical_json_bytes(replay_result.private_manifest),
        )

    def test_all_eighteen_wrapper_mutations_refuse_in_order(self):
        routes = live.run_wrapper_mutations()
        self.assertEqual(tuple(routes), live.WRAPPER_MUTATIONS)
        self.assertEqual(len(routes), 18)
        self.assertTrue(all(route in live.FAILURE_ROUTES for route in routes.values()))

    def test_generated_qualification_and_inspection_roundtrip(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "qualification"
            outcome = live.qualify_generated_mock_wrapper(output, rss_probe=lambda: 1)
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

    def test_generated_qualification_passes_all_fifty_eight_refusals(self):
        with tempfile.TemporaryDirectory() as temporary:
            outcome = live.qualify_generated_mock_wrapper(
                Path(temporary) / "qualification",
                rss_probe=lambda: 1,
            )
            summary = outcome.report["mutation_summary"]
            self.assertEqual(summary["inherited_passed"], 40)
            self.assertEqual(summary["wrapper_passed"], 18)
            self.assertEqual(len(summary["wrapper_names"]), 18)

    def test_qualification_rejects_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(live.PrivateSelectionRefusal) as caught:
                live.qualify_generated_mock_wrapper(temporary)
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_public_report_rejects_private_key(self):
        with self.assertRaises(live.PrivateSelectionRefusal) as caught:
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
            with self.assertRaises(live.PrivateSelectionRefusal) as caught:
                live.inspect_public_result(path)
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_combined_output_cap_refuses_one_byte_over(self):
        with self.assertRaises(live.PrivateSelectionRefusal) as caught:
            live._bounded_output_bytes(b"x" * (live.MAX_COMBINED_OUTPUT_BYTES + 1))
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[6])

    def test_locked_reader_uses_one_open_read_hash_and_parse(self):
        payload = live._canonical_json_bytes({"schema_name": "fixture"})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            counters = live._base_access_counters()
            value, observed = live.read_locked_private_manifest(
                path,
                expected_bytes=len(payload),
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                counters=counters,
            )
        self.assertEqual(value["schema_name"], "fixture")
        self.assertEqual(observed, payload)
        self.assertEqual(counters["private_manifest_content_opens"], 1)
        self.assertEqual(counters["private_manifest_body_reads"], 1)
        self.assertEqual(counters["private_manifest_hashes"], 1)
        self.assertEqual(counters["private_manifest_parses"], 1)

    def test_locked_reader_accepts_short_chunks_in_one_sequential_pass(self):
        payload = live._canonical_json_bytes({"schema_name": "fixture"})
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)

            def short_reader(descriptor, size):
                return os.read(descriptor, min(size, 3))

            value, observed = live.read_locked_private_manifest(
                path,
                expected_bytes=len(payload),
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                counters=live._base_access_counters(),
                body_reader=short_reader,
            )
        self.assertEqual(value["schema_name"], "fixture")
        self.assertEqual(observed, payload)

    def test_locked_reader_rejects_duplicate_json(self):
        payload = b'{"x":1,"x":2}\n'
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            with self.assertRaises(live.PrivateSelectionRefusal) as caught:
                live.read_locked_private_manifest(
                    path,
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
            before = os.lstat(path)
            changed = SimpleNamespace(
                st_dev=before.st_dev,
                st_ino=before.st_ino + 1,
                st_uid=before.st_uid,
                st_mode=before.st_mode,
                st_size=before.st_size,
            )
            with self.assertRaises(live.PrivateSelectionRefusal) as caught:
                live.read_locked_private_manifest(
                    path,
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
        with self.assertRaises(live.PrivateSelectionRefusal) as caught:
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
        )
        with mock.patch.object(
            live,
            "_assert_source_components",
            side_effect=AssertionError("private source must remain closed"),
        ):
            with self.assertRaises(live.PrivateSelectionRefusal) as caught:
                live.execute_registered_private_selection(
                    ROOT,
                    evidence=evidence,
                    output_root=ROOT / live.OUTPUT_ROOT_RELATIVE_PATH,
                    environ={key: "1" for key in live.THREAD_ENV_KEYS},
                )
        self.assertEqual(caught.exception.route, live.FAILURE_ROUTES[0])

    def test_consumed_failure_writes_one_aggregate_report_without_retry(self):
        evidence = live.GreenImplementationEvidence(
            implementation_commit="1" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="2" * 64,
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
                mock.patch.object(live, "_preflight_private_source"),
                mock.patch.object(
                    live,
                    "read_locked_private_manifest",
                    side_effect=live.PrivateSelectionRefusal(
                        live.FAILURE_ROUTES[2],
                        "fixture refusal",
                    ),
                ),
            ):
                with self.assertRaises(live.PrivateSelectionRefusal) as caught:
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
            self.assertEqual(
                summary["status"],
                "consumed_failed_registered_private_selection",
            )
            self.assertTrue((destination / live.CONSUMED_MARKER_NAME).is_file())
            self.assertFalse((destination / live.PRIVATE_SELECTION_NAME).exists())

    def test_cli_help_exposes_only_fixed_commands(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc2_freewill_private_selection",
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

    def test_selector_hash_and_contract_are_immutable(self):
        self.assertEqual(
            live._sha256_file(ROOT / live.SELECTOR_RELATIVE_PATH),
            live.SELECTOR_SHA256,
        )
        self.assertEqual(selector.CONTRACT_SHA256, live.selector.CONTRACT_SHA256)


if __name__ == "__main__":
    unittest.main()
