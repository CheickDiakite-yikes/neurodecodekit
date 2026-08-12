from __future__ import annotations

import copy
import os
import pickle
import stat
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_paginated_live_metadata as live
from neurodecodekit.datasets import marc1_versioned_pagination as pagination


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {key: "1" for key in live.THREAD_ENV_KEYS}


class _Disk:
    free = live.MINIMUM_FREE_DISK_BYTES


class MARC1PaginatedLiveMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = pagination.build_generated_wrist_rows()
        cls.body = live._canonical_json_bytes(cls.rows)

    def temporary_directory(self):
        return tempfile.TemporaryDirectory(dir=live._canonical_temp_parent())

    def qualify(self, output: Path) -> live.QualificationOutcome:
        ticks = iter((100.0, 100.125))
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            return live.qualify_generated(
                output,
                repo_root=ROOT,
                clock=lambda: next(ticks),
                rss_reader=lambda: 32 * 1024**2,
            )

    def fetch(self, response: live.FixtureResponse):
        ledger = live.AccessLedger()
        result = live.fetch_and_validate(
            opener=live.FixtureOpener(response),
            pagination=pagination,
            ledger=ledger,
            real_network=False,
        )
        return result, ledger

    def test_green_decision_request_and_source_hashes_are_exact(self) -> None:
        ledger = live.AccessLedger()
        decision = live.load_green_decision(ROOT, ledger=ledger)
        self.assertEqual(decision["lane_id"], live.LANE_ID)
        self.assertEqual(live.GREEN_DECISION_COMMIT, "060a365a24e75da4297a5c4a3422ff730467ec36")
        self.assertEqual(live.GREEN_DECISION_CI_RUN_ID, 31604608307)
        self.assertEqual(live.GREEN_DECISION_BASE_JOB_ID, 94140250333)
        self.assertEqual(live.GREEN_DECISION_OPTIONAL_JOB_ID, 94140250412)
        self.assertEqual(ledger.values["decision_loads"], 1)
        self.assertEqual(ledger.values["repository_reads"], 4)

    def test_source_surface_is_dependency_light_and_has_no_consumed_executor(self) -> None:
        surface = live.inspect_source_surface()
        self.assertTrue(surface["standard_library_only_at_module_scope"])
        self.assertEqual(surface["forbidden_imports"], [])
        self.assertFalse(surface["payload_or_model_command"])
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])

    def test_plan_is_fixed_and_does_not_construct_a_network_opener(self) -> None:
        with mock.patch.object(live, "_real_opener", side_effect=AssertionError("network")):
            plan = live.registered_plan()
        self.assertEqual(plan["request_query"], "page=1&page_size=1000")
        self.assertEqual(plan["request_attempts"], 1)
        self.assertEqual(plan["payload_requests"], 0)
        self.assertFalse(plan["scientific_claim_established"])

    def test_output_capability_is_first_process_local_and_nonserializable(self) -> None:
        with self.temporary_directory() as temporary:
            ledger = live.AccessLedger()
            capability = live.acquire_output_capability(Path(temporary) / "out", ledger=ledger)
            try:
                self.assertEqual(ledger.values["capability_acquisitions"], 1)
                self.assertTrue(all(value == 0 for value in ledger.early_snapshot().values()))
                with self.assertRaisesRegex(TypeError, "process-local"):
                    pickle.dumps(capability)
            finally:
                capability.close()

    def test_capability_refuses_early_work_and_existing_output(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            ledger = live.AccessLedger()
            ledger.increment("repository_reads")
            with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F01"):
                live.acquire_output_capability(output, ledger=ledger)
            output.mkdir()
            with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F01"):
                live.acquire_output_capability(output, ledger=live.AccessLedger())

    def test_generated_qualifier_refuses_registered_path_without_touching_it(self) -> None:
        with mock.patch.object(
            live,
            "acquire_output_capability",
            side_effect=AssertionError("registered path touched"),
        ) as acquire:
            with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F01"):
                live.qualify_generated(live.REGISTERED_OUTPUT_PATH, repo_root=ROOT)
        acquire.assert_not_called()

    def test_request_serialization_is_exact_and_body_or_query_drift_refuses(self) -> None:
        summary = live.validate_request(live._request())
        self.assertEqual(summary["method"], "GET")
        self.assertEqual(summary["query"], live.REQUEST_QUERY)
        self.assertEqual(len(summary["canonical_request_sha256"]), 64)
        for request in (
            urllib.request.Request(
                live.REQUEST_URL.replace("page=1", "page=2"),
                method="GET",
                headers={"Accept": "application/json", "Accept-Encoding": "identity"},
            ),
            urllib.request.Request(
                live.REQUEST_URL,
                data=b"x",
                method="GET",
                headers={"Accept": "application/json", "Accept-Encoding": "identity"},
            ),
        ):
            with self.subTest(url=request.full_url), self.assertRaisesRegex(
                live.PaginatedMetadataRefusal, "MARC1LM-F02"
            ):
                live.validate_request(request)

    def test_four_transport_cases_have_identical_semantic_and_selection_hashes(self) -> None:
        results = [
            self.fetch(live._fixture_response(self.body, case=case))[0]
            for case in ("close", "content_length", "identity_length", "chunked")
        ]
        self.assertEqual(
            {result[0]["bound_inventory_sha256"] for result in results},
            {results[0][0]["bound_inventory_sha256"]},
        )
        self.assertEqual(
            {result[1]["selection_sha256"] for result in results},
            {results[0][1]["selection_sha256"]},
        )
        self.assertEqual(
            {result[2]["framing"] for result in results},
            {"connection-close", "content-length", "chunked"},
        )

    def test_transport_refuses_redirect_encoding_ambiguity_and_overflow(self) -> None:
        cases = (
            live._fixture_response(self.body, status=302),
            live.FixtureResponse(
                self.body,
                headers=(("Content-Type", "application/json"), ("Content-Encoding", "gzip")),
            ),
            live.FixtureResponse(
                self.body,
                headers=(
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(self.body))),
                    ("Transfer-Encoding", "chunked"),
                ),
            ),
            live._fixture_response(b"x" * (live.MAX_BODY_BYTES + 1), case="close"),
        )
        for response in cases:
            with self.subTest(headers=response.headers), self.assertRaisesRegex(
                live.PaginatedMetadataRefusal, "MARC1LM-F03"
            ):
                self.fetch(response)

    def test_duplicate_JSON_and_target_like_fields_refuse(self) -> None:
        target_rows = copy.deepcopy(self.rows)
        target_rows[0]["target"] = "forbidden"
        for body in (b'[{"id":1,"id":2}]', live._canonical_json_bytes(target_rows)):
            with self.subTest(size=len(body)), self.assertRaisesRegex(
                live.PaginatedMetadataRefusal, "MARC1LM-F04"
            ):
                self.fetch(live._fixture_response(body))

    def test_inventory_and_frozen_split_are_exact_and_target_free(self) -> None:
        (inventory, selection, _transport), ledger = self.fetch(
            live._fixture_response(self.body)
        )
        self.assertEqual(inventory["participant_archives"], 45)
        self.assertEqual(inventory["supplementary_rows"], 10)
        self.assertEqual(inventory["declared_bytes"], 3_683_416_050)
        self.assertEqual(selection["selected_count"], 12)
        self.assertEqual(selection["fit_runs"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(selection["heldout_runs"], [7, 8])
        self.assertEqual(selection["fit_heldout_overlap"], 0)
        self.assertEqual(ledger.values["target_reads"], 0)

    def test_private_manifest_and_selection_replay_are_deterministic(self) -> None:
        inventory = live.parse_inventory(self.body, pagination, ledger=live.AccessLedger())
        first = live.select_frozen_cohort(inventory, ledger=live.AccessLedger())
        second = live.select_frozen_cohort(inventory, ledger=live.AccessLedger())
        self.assertEqual(first["private_bytes"], second["private_bytes"])
        self.assertEqual(first["selection_sha256"], second["selection_sha256"])
        self.assertNotIn(b'"target"', first["private_bytes"])
        self.assertNotIn(b'"label"', first["private_bytes"])

    def test_all_36_required_mutations_refuse_on_registered_routes(self) -> None:
        ledger = live.AccessLedger()
        routes = live.run_required_mutations(
            pagination,
            self.body,
            repo_root=ROOT,
            ledger=ledger,
        )
        self.assertEqual(tuple(routes), live.REQUIRED_MUTATIONS)
        self.assertEqual(len(routes), 36)
        self.assertTrue(all(route in live.FAILURE_ROUTES for route in routes.values()))
        self.assertEqual(ledger.values["real_network_requests"], 0)

    def test_public_validator_allows_aggregate_row_count_and_refuses_private_rows(self) -> None:
        with self.temporary_directory() as temporary:
            report = copy.deepcopy(self.qualify(Path(temporary) / "out").report)
        live.validate_public_report(report)
        report["inventory_summary"]["rows"] = [{"id": 1}]
        with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F06"):
            live.validate_public_report(report)

    def test_failure_receipt_is_aggregate_public_only_and_marker_is_mode_0600(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            ledger = live.AccessLedger()
            capability = live.acquire_output_capability(output, ledger=ledger)
            try:
                live._create_output(capability)
                marker = live._marker_bytes(generated=False, implementation_commit="a" * 40)
                live._write_relative(capability, live.MARKER_NAME, marker, mode=0o600)
                report = live._write_consumed_failure_report(
                    capability,
                    live.PaginatedMetadataRefusal("MARC1LM-F03", "generated refusal"),
                    stage="public_metadata_transport",
                    ledger=ledger,
                    machine={"threads": 1, "workers": 1, "numerical_jobs": 1},
                    started=100.0,
                    marker=marker,
                    clock=lambda: 100.125,
                    rss_reader=lambda: 32 * 1024**2,
                )
                self.assertEqual(report["status"], "consumed_failed_real_metadata")
                self.assertEqual(report["route"], "MARC1LM-F03")
                self.assertEqual(report["access_counters"]["target_reads"], 0)
                marker_stat = os.stat(
                    live.MARKER_NAME,
                    dir_fd=capability.output_fd,
                    follow_symlinks=False,
                )
                report_stat = os.stat(
                    live.REPORT_NAME,
                    dir_fd=capability.output_fd,
                    follow_symlinks=False,
                )
                self.assertEqual(stat.S_IMODE(marker_stat.st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(report_stat.st_mode), 0o644)
                with self.assertRaises(FileNotFoundError):
                    os.stat(
                        live.PRIVATE_NAME,
                        dir_fd=capability.output_fd,
                        follow_symlinks=False,
                    )
            finally:
                live._cleanup_generated_output(capability)
                capability.close()

    def test_inspector_rejects_private_name_before_any_file_read(self) -> None:
        private_path = Path(live._canonical_temp_parent()) / live.PRIVATE_NAME
        with mock.patch.object(live.os, "lstat", side_effect=AssertionError("read")) as lstat:
            with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F06"):
                live.inspect_public_result(private_path)
        lstat.assert_not_called()

    def test_machine_gate_enforces_threads_disk_load_and_RSS(self) -> None:
        report = live.preconsumption_machine_gate(
            live._canonical_temp_parent(),
            environ=THREAD_ENV,
            disk_usage_reader=lambda _path: _Disk(),
            cpu_count_reader=lambda: 8,
            loadavg_reader=lambda: (0.0, 0.0, 0.0),
            rss_reader=lambda: 32 * 1024**2,
        )
        self.assertEqual(report["threads"], 1)
        cases = (
            ({**THREAD_ENV, live.THREAD_ENV_KEYS[0]: "2"}, _Disk.free, 0.0, 32 * 1024**2),
            (THREAD_ENV, 1, 0.0, 32 * 1024**2),
            (THREAD_ENV, _Disk.free, 9.0, 32 * 1024**2),
            (THREAD_ENV, _Disk.free, 0.0, live.MAX_PEAK_RSS_BYTES + 1),
        )
        for environ, free, load, rss in cases:
            with self.subTest(free=free, load=load, rss=rss), self.assertRaisesRegex(
                live.PaginatedMetadataRefusal, "MARC1LM-F01"
            ):
                live.preconsumption_machine_gate(
                    live._canonical_temp_parent(),
                    environ=environ,
                    disk_usage_reader=lambda _path, value=free: type(
                        "Disk", (), {"free": value}
                    )(),
                    cpu_count_reader=lambda: 8,
                    loadavg_reader=lambda value=load: (value, 0.0, 0.0),
                    rss_reader=lambda value=rss: value,
                )

    def test_resource_caps_and_retry_or_rerun_refuse(self) -> None:
        operations = (
            lambda: live._enforce_resources(live.MAX_RUNTIME_SECONDS + 1, 0, 0),
            lambda: live._enforce_resources(0, live.MAX_PEAK_RSS_BYTES + 1, 0),
            lambda: live._enforce_resources(0, 0, live.MAX_COMBINED_OUTPUT_BYTES + 1),
            lambda: live._require_single_execution(1, retry_count=1),
            lambda: live._require_single_execution(2, retry_count=0),
        )
        for operation in operations:
            with self.assertRaises(live.PaginatedMetadataRefusal):
                operation()

    def test_green_implementation_proof_refuses_wrong_HEAD_before_live_open(self) -> None:
        evidence = live.GreenImplementationEvidence(
            implementation_commit="a" * 40,
            implementation_registry_sha256="b" * 64,
            CI_run_id=1,
            base_python_job_id=2,
            optional_neuro_job_id=3,
        )
        with mock.patch.object(live, "_real_opener", side_effect=AssertionError("network")):
            with self.assertRaisesRegex(live.PaginatedMetadataRefusal, "MARC1LM-F00"):
                live.verify_green_implementation(ROOT, evidence, ledger=live.AccessLedger())

    def test_full_generated_roundtrip_is_bounded_publicly_inspected_and_removed(self) -> None:
        with self.temporary_directory() as temporary:
            output = Path(temporary) / "out"
            outcome = self.qualify(output)
            self.assertFalse(output.exists())
        report = outcome.report
        self.assertEqual(report["route"], live.GENERATED_ROUTE)
        self.assertEqual(report["mutation_summary"]["passed"], 36)
        self.assertEqual(report["inventory_summary"]["rows"], 55)
        self.assertEqual(report["cohort_summary"]["selected_subjects"], 12)
        self.assertEqual(report["access_counters"]["output_files_created"], 3)
        self.assertEqual(report["access_counters"]["public_report_inspections"], 1)
        self.assertEqual(report["access_counters"]["cleanup_file_unlinks"], 3)
        self.assertEqual(report["access_counters"]["real_network_requests"], 0)
        self.assertEqual(report["access_counters"]["payload_bytes"], 0)
        self.assertEqual(report["access_counters"]["target_reads"], 0)
        self.assertEqual(report["access_counters"]["model_runs"], 0)
        self.assertEqual(report["access_counters"]["scoring_events"], 0)
        self.assertEqual(
            report["measurements"]["combined_output_bytes"],
            outcome.generated_output_bytes,
        )
        self.assertLess(outcome.generated_output_bytes, live.MAX_COMBINED_OUTPUT_BYTES)
        self.assertTrue(outcome.output_removed)

    def test_consumed_entrypoints_are_never_called_by_qualification(self) -> None:
        with self.temporary_directory() as temporary, mock.patch.object(
            pagination,
            "qualify_generated_pagination",
            side_effect=AssertionError("consumed qualifier called"),
        ) as qualify, mock.patch.object(
            pagination,
            "_assert_new_output_directory",
            side_effect=AssertionError("consumed output guard called"),
        ) as guard, mock.patch.object(
            pagination,
            "main",
            side_effect=AssertionError("consumed CLI called"),
        ) as main:
            outcome = self.qualify(Path(temporary) / "out")
        self.assertEqual(outcome.report["route"], live.GENERATED_ROUTE)
        qualify.assert_not_called()
        guard.assert_not_called()
        main.assert_not_called()


if __name__ == "__main__":
    unittest.main()
