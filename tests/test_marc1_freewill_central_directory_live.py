import contextlib
import copy
import hashlib
import io
import json
import stat
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from neurodecodekit.datasets import marc1_central_directory_audit as audit
from neurodecodekit.datasets import marc1_central_directory_live as live


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {key: "1" for key in live.THREAD_ENV_KEYS}


class MARC1CentralDirectoryLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = audit.build_generated_fixture()

    def safe_machine_kwargs(self) -> dict[str, object]:
        return {
            "environ": THREAD_ENV,
            "disk_usage_reader": lambda _path: SimpleNamespace(
                free=live.MINIMUM_FREE_DISK_BYTES + 1
            ),
            "cpu_count_reader": lambda: 8,
            "loadavg_reader": lambda: (4.0, 0.0, 0.0),
            "rss_reader": lambda: 32 * 1024 * 1024,
        }

    def evidence(self) -> live.GreenWrapperEvidence:
        return live.GreenWrapperEvidence(
            implementation_commit="a" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="b" * 64,
        )

    def proof(self, _root, _evidence) -> dict[str, object]:
        return {"execution_state": {"public_execution_consumed": False}}

    def test_green_decision_request_and_parser_hashes_are_exact(self) -> None:
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["lane_id"], "MARC1-CD1A")
        self.assertTrue(
            decision["authorization"][
                "one_public_metadata_tail_and_conditional_directory_invocation_authorized_after_wrapper_green"
            ]
        )
        self.assertFalse(
            decision["authorization"]["whole_archive_download_authorized_now"]
        )
        self.assertEqual(
            hashlib.sha256((ROOT / live.PARSER_RELATIVE_PATH).read_bytes()).hexdigest(),
            live.PARSER_SHA256,
        )
        self.assertEqual(
            hashlib.sha256((ROOT / live.REQUEST_RELATIVE_PATH).read_bytes()).hexdigest(),
            live.REQUEST_SHA256,
        )

    def test_plan_is_fixed_zero_network_and_no_member_access(self) -> None:
        plan = live.registered_plan(ROOT)
        self.assertEqual(plan["declared_archive_bytes"], 13_591_548_048)
        self.assertEqual(plan["tail_bytes"], 128 * 1024)
        self.assertEqual(plan["central_directory_cap_bytes"], 16 * 1024 * 1024)
        self.assertEqual(plan["accepted_response_body_cap_bytes"], 17_039_360)
        self.assertEqual(plan["HTTP_request_attempt_cap"], 5)
        self.assertEqual(plan["public_requests_made"], 0)
        self.assertEqual(plan["whole_archive_downloads"], 0)
        self.assertEqual(plan["member_payload_requests"], 0)
        self.assertTrue(plan["execution_requires_exact_green_wrapper_evidence"])

    def test_direct_and_two_redirect_generated_paths_match(self) -> None:
        direct, direct_opener = live._run_generated_path(
            self.fixture,
            redirect_count=0,
        )
        redirected, redirected_opener = live._run_generated_path(
            self.fixture,
            redirect_count=2,
        )
        self.assertEqual(direct_opener.calls, 3)
        self.assertEqual(redirected_opener.calls, 5)
        self.assertEqual(direct.transport["accepted_response_bodies"], 3)
        self.assertEqual(redirected.transport["accepted_response_bodies"], 3)
        self.assertEqual(redirected.transport["network_redirects"], 2)
        self.assertEqual(
            direct.inventory.canonical_inventory_bytes,
            redirected.inventory.canonical_inventory_bytes,
        )
        self.assertEqual(direct.inventory.aggregate_summary["entry_count"], 18)

    def test_all_inherited_and_wrapper_mutations_refuse(self) -> None:
        inherited = audit.run_required_mutations(self.fixture)
        wrapper = live._run_wrapper_mutations(self.fixture)
        self.assertEqual(len(inherited), 32)
        self.assertEqual(len(wrapper), 8)
        self.assertTrue(all(value in audit.REFUSAL_IDS for value in inherited.values()))
        self.assertTrue(all(value in live.FAILURE_ROUTES for value in wrapper.values()))

    def test_machine_gate_reports_load_and_one_thread(self) -> None:
        result = live.preconsumption_machine_gate(ROOT, **self.safe_machine_kwargs())
        self.assertTrue(result["passed_before_consumed_marker"])
        self.assertEqual(result["one_minute_load_per_logical_CPU"], 0.5)
        self.assertEqual(result["CPU_threads"], 1)
        self.assertEqual(result["free_disk_bytes"], live.MINIMUM_FREE_DISK_BYTES + 1)

    def test_generated_qualification_is_bounded_replayable_and_private(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((10.0, 10.5))
            outcome = live.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            report = outcome.report
            self.assertEqual(report["route"], live.GENERATED_ROUTE)
            self.assertEqual(report["archive_summary"]["entry_count"], 18)
            self.assertEqual(
                report["measurements"]["inherited_parser_mutations_passed"], 32
            )
            self.assertEqual(report["measurements"]["wrapper_mutations_passed"], 8)
            self.assertLess(outcome.combined_output_bytes, 1024 * 1024)
            self.assertEqual(
                report["measurements"]["combined_output_bytes"],
                outcome.combined_output_bytes,
            )
            self.assertTrue(all(report["acceptance_gates"].values()))
            self.assertEqual(sum(report["access_counters"].values()), 0)
            self.assertFalse(report["source"]["whole_archive_downloaded"])
            self.assertFalse(report["source"]["member_payload_opened"])
            self.assertTrue(outcome.private_manifest_path.is_file())
            self.assertTrue(outcome.report_path.is_file())
            private = json.loads(outcome.private_manifest_path.read_text())
            self.assertEqual(len(private["entries"]), 18)
            self.assertNotIn("entries", report["archive_summary"])
            live.validate_public_result(report)

    def test_generated_qualification_replays_identity_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outcomes = []
            for ordinal in range(2):
                ticks = iter((1.0, 1.25))
                outcomes.append(
                    live.qualify_generated_mock_wrapper(
                        Path(directory) / f"q{ordinal}",
                        repo_root=ROOT,
                        clock=lambda ticks=ticks: next(ticks),
                        **self.safe_machine_kwargs(),
                    )
                )
            for key in (
                "inventory_sha256",
                "private_manifest_sha256",
                "central_directory_bytes",
                "entry_count",
            ):
                self.assertEqual(
                    outcomes[0].report["archive_summary"][key],
                    outcomes[1].report["archive_summary"][key],
                )

    def test_generated_output_collision_refuses_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            ticks = iter((1.0, 1.1))
            live.qualify_generated_mock_wrapper(
                output,
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F01"):
                live.qualify_generated_mock_wrapper(
                    output,
                    repo_root=ROOT,
                    **self.safe_machine_kwargs(),
                )

    def test_public_validator_refuses_names_URLs_and_forbidden_counters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((1.0, 1.1))
            outcome = live.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            leaked = copy.deepcopy(outcome.report)
            leaked["archive_summary"]["member_name"] = "private.edf"
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F06"):
                live.validate_public_result(leaked)
            URL_leak = copy.deepcopy(outcome.report)
            URL_leak["warnings"].append("https://example.test/private")
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F06"):
                live.validate_public_result(URL_leak)
            counted = copy.deepcopy(outcome.report)
            counted["access_counters"]["member_payload_requests"] = 1
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F06"):
                live.validate_public_result(counted)

    def test_noncritical_duplicate_headers_are_ignored_but_framing_duplicates_refuse(
        self,
    ) -> None:
        harmless = live.FixtureHTTPResponse(
            self.fixture.metadata_body,
            status=200,
            url=audit.METADATA_URL,
            headers={"Content-Length": str(len(self.fixture.metadata_body))},
            duplicate_headers=(("Set-Cookie", "a=1"), ("Set-Cookie", "b=2")),
        )
        opener = live.FixtureOpener(
            [
                live.FixtureExchange(
                    audit.METADATA_URL,
                    {"accept": "application/json", "accept-encoding": "identity"},
                    harmless,
                )
            ]
        )
        transport = live.BoundedHTTPTransport(
            opener,
            counters=live._base_access_counters(),
            public_request=False,
        )
        response = transport.request(
            "GET",
            audit.METADATA_URL,
            {"accept": "application/json", "accept-encoding": "identity"},
        )
        self.assertEqual(response.status, 200)

        conflicting = live.FixtureHTTPResponse(
            self.fixture.metadata_body,
            status=200,
            url=audit.METADATA_URL,
            headers={"Content-Length": str(len(self.fixture.metadata_body))},
            duplicate_headers=(("Content-Length", str(len(self.fixture.metadata_body))),),
        )
        opener = live.FixtureOpener(
            [
                live.FixtureExchange(
                    audit.METADATA_URL,
                    {"accept": "application/json", "accept-encoding": "identity"},
                    conflicting,
                )
            ]
        )
        transport = live.BoundedHTTPTransport(
            opener,
            counters=live._base_access_counters(),
            public_request=False,
        )
        with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F03"):
            transport.request(
                "GET",
                audit.METADATA_URL,
                {"accept": "application/json", "accept-encoding": "identity"},
            )

    def test_transfer_encoding_is_refused_even_with_content_length(self) -> None:
        response = live.FixtureHTTPResponse(
            self.fixture.metadata_body,
            status=200,
            url=audit.METADATA_URL,
            headers={
                "Content-Length": str(len(self.fixture.metadata_body)),
                "Transfer-Encoding": "chunked",
            },
        )
        opener = live.FixtureOpener(
            [
                live.FixtureExchange(
                    audit.METADATA_URL,
                    {"accept": "application/json", "accept-encoding": "identity"},
                    response,
                )
            ]
        )
        transport = live.BoundedHTTPTransport(
            opener,
            counters=live._base_access_counters(),
            public_request=False,
        )
        with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F03"):
            transport.request(
                "GET",
                audit.METADATA_URL,
                {"accept": "application/json", "accept-encoding": "identity"},
            )

    def test_aggregate_inspector_refuses_private_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((1.0, 1.1))
            outcome = live.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            inspected = live.inspect_public_result(outcome.report_path)
            self.assertEqual(inspected["route"], live.GENERATED_ROUTE)
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F06"):
                live.inspect_public_result(outcome.private_manifest_path)

    def test_plan_and_default_CLI_do_not_open_network(self) -> None:
        with mock.patch.object(
            live.urllib.request,
            "build_opener",
            side_effect=AssertionError("network"),
        ):
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(live.main([]), 0)
            self.assertIn("metadata-range archive", stdout.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(live.main(["plan"]), 0)
            plan = json.loads(stdout.getvalue())
            self.assertEqual(plan["public_requests_made"], 0)
            self.assertEqual(plan["whole_archive_downloads"], 0)

    def test_malformed_green_evidence_refuses_before_network(self) -> None:
        evidence = live.GreenWrapperEvidence(
            implementation_commit="bad",
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="b" * 64,
        )
        with mock.patch.object(
            live.urllib.request,
            "build_opener",
            side_effect=AssertionError("network"),
        ), self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F00"):
            live.execute_registered_archive_audit(ROOT, evidence=evidence)

    def test_machine_failure_precedes_marker_and_opener(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            opener = mock.Mock()
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F01"):
                live.execute_registered_archive_audit(
                    root,
                    evidence=self.evidence(),
                    proof_verifier=self.proof,
                    environ=THREAD_ENV,
                    opener=opener,
                    disk_usage_reader=lambda _path: SimpleNamespace(
                        free=live.MINIMUM_FREE_DISK_BYTES - 1
                    ),
                    cpu_count_reader=lambda: 8,
                    loadavg_reader=lambda: (0.0, 0.0, 0.0),
                    rss_reader=lambda: 1,
                )
            opener.assert_not_called()
            self.assertFalse((root / live.REAL_ROOT_RELATIVE_PATH).exists())
            self.assertFalse((root / live.REAL_PUBLIC_RESULT_RELATIVE_PATH).exists())

    def test_mocked_public_path_writes_marker_before_three_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            exchanges, resolver = live._generated_exchanges(
                self.fixture,
                redirect_count=2,
            )
            sequence = live.FixtureOpener(exchanges)
            marker_seen = []

            def opener(request, timeout):
                marker_seen.append(
                    (
                        root
                        / live.REAL_ROOT_RELATIVE_PATH
                        / live.REAL_CONSUMED_NAME
                    ).is_file()
                )
                return sequence(request, timeout)

            ticks = iter((2.0, 2.5))
            outcome = live.execute_registered_archive_audit(
                root,
                evidence=self.evidence(),
                proof_verifier=self.proof,
                opener=opener,
                resolver=resolver,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            sequence.assert_consumed()
            self.assertEqual(marker_seen, [True] * 5)
            self.assertEqual(outcome.report["route"], live.SUCCESS_ROUTE)
            counters = outcome.report["access_counters"]
            self.assertEqual(counters["HTTP_request_attempts"], 5)
            self.assertEqual(counters["accepted_response_bodies"], 3)
            self.assertEqual(counters["network_redirects"], 2)
            self.assertEqual(counters["member_payload_requests"], 0)
            self.assertEqual(counters["signal_sample_reads"], 0)
            self.assertEqual(counters["model_inference_runs"], 0)
            self.assertTrue(outcome.private_manifest_path.is_file())
            self.assertTrue(outcome.report_path.is_file())
            self.assertEqual(
                stat.S_IMODE(outcome.private_manifest_path.stat().st_mode),
                0o600,
            )
            live.validate_public_result(outcome.report)

    def test_directory_redirect_failure_is_consumed_and_not_rerunnable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            exchanges, resolver = live._generated_exchanges(
                self.fixture,
                redirect_count=0,
            )
            terminal = exchanges[-1].url
            exchanges[-1] = live.FixtureExchange(
                terminal,
                exchanges[-1].request_headers,
                live.FixtureHTTPResponse(
                    b"",
                    status=302,
                    url=terminal,
                    headers={
                        "Content-Length": "0",
                        "Location": "https://cdn-c.example.net/archive",
                    },
                ),
            )
            opener = live.FixtureOpener(exchanges)
            ticks = iter((1.0, 1.1))
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F03"):
                live.execute_registered_archive_audit(
                    root,
                    evidence=self.evidence(),
                    proof_verifier=self.proof,
                    opener=opener,
                    resolver=resolver,
                    clock=lambda: next(ticks),
                    **self.safe_machine_kwargs(),
                )
            report = live.inspect_public_result(root / live.REAL_PUBLIC_RESULT_RELATIVE_PATH)
            self.assertEqual(report["route"], "MARC1CD-F03")
            self.assertEqual(report["status"], "consumed_failed_live_archive_inventory")
            self.assertTrue(
                (
                    root / live.REAL_ROOT_RELATIVE_PATH / live.REAL_CONSUMED_NAME
                ).is_file()
            )
            self.assertFalse(
                (
                    root / live.REAL_ROOT_RELATIVE_PATH / live.REAL_PRIVATE_MANIFEST_NAME
                ).exists()
            )
            second_opener = mock.Mock()
            with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F01"):
                live.execute_registered_archive_audit(
                    root,
                    evidence=self.evidence(),
                    proof_verifier=self.proof,
                    opener=second_opener,
                    **self.safe_machine_kwargs(),
                )
            second_opener.assert_not_called()

    def test_redirect_to_private_address_refuses_after_bodyless_response(self) -> None:
        exchanges, _ = live._generated_exchanges(self.fixture, redirect_count=2)
        opener = live.FixtureOpener(exchanges)
        transport = live.BoundedHTTPTransport(
            opener,
            counters=live._base_access_counters(),
            public_request=False,
        )
        with self.assertRaisesRegex(live.LiveArchiveRefusal, "MARC1CD-F03"):
            live.perform_inventory(
                transport,
                resolver=lambda _hostname: ("127.0.0.1",),
                counters=live._base_access_counters(),
                public_request=False,
            )
        self.assertEqual(opener.calls, 2)

    def test_module_has_no_heavy_dependency_or_whole_archive_interface(self) -> None:
        source = Path(live.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import sklearn",
            "import torch",
            "download_full_archive",
            "extract_member",
            "read_member_payload",
            "ZipFile(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
