from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc1_pilot_selection as selector
from neurodecodekit.datasets import marc1_pilot_selection_live as live


ROOT = Path(__file__).resolve().parents[1]


class _Disk:
    free = live.MINIMUM_FREE_DISK_BYTES


class _Clock:
    def __init__(self, *values: float) -> None:
        self.values = iter(values)

    def __call__(self) -> float:
        return next(self.values)


class MARC1PilotSelectionLiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = selector.load_registered_contract(ROOT)
        cls.freewill = live.build_generated_real_freewill_manifest(contract=cls.contract)
        cls.wrist_payload = live.build_generated_wrist_response()
        cls.environ = {key: "1" for key in live.THREAD_ENV_KEYS}

    def machine_kwargs(self) -> dict[str, object]:
        return {
            "environ": self.environ,
            "disk_usage_reader": lambda _path: _Disk(),
            "cpu_count_reader": lambda: 8,
            "loadavg_reader": lambda: (0.0, 0.0, 0.0),
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

    def mock_implementation(self) -> dict[str, object]:
        return {
            "execution_state": {"real_metadata_execution_consumed": False},
            "generated_qualification": {
                "mutation_routes": {
                    name: live.FAILURE_ROUTES[1] for name in live.REQUIRED_MUTATIONS
                }
            },
        }

    def make_mock_repo(self, root: Path) -> None:
        (root / ".codex_work").mkdir()
        (root / "registries").mkdir()
        shutil.copyfile(
            ROOT / selector.CONTRACT_RELATIVE_PATH,
            root / selector.CONTRACT_RELATIVE_PATH,
        )

    def generated_private_reader(self):
        manifest = copy.deepcopy(self.freewill)

        def reader(path, *, expected_bytes, expected_sha256, counters):  # noqa: ANN001
            self.assertEqual(
                path,
                path.parents[3] / live.FREEWILL_PRIVATE_RELATIVE_PATH,
            )
            self.assertEqual(expected_bytes, live.FREEWILL_PRIVATE_BYTES)
            self.assertEqual(expected_sha256, live.FREEWILL_PRIVATE_SHA256)
            counters["private_Freewill_manifest_path_operations"] += 1
            counters["private_Freewill_manifest_content_opens"] += 1
            counters["private_Freewill_manifest_body_reads"] += 1
            counters["private_Freewill_manifest_bytes"] += expected_bytes
            counters["private_Freewill_manifest_hashes"] += 1
            counters["private_Freewill_manifest_parses"] += 1
            return copy.deepcopy(manifest), b"x" * expected_bytes

        return reader

    def test_green_decision_and_all_upstream_hashes_are_exact(self) -> None:
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["lane_id"], live.LANE_ID)
        self.assertEqual(live._sha256_file(ROOT / live.DECISION_RELATIVE_PATH), live.DECISION_SHA256)
        self.assertEqual(live._sha256_file(ROOT / live.REQUEST_RELATIVE_PATH), live.REQUEST_SHA256)
        self.assertEqual(
            live._sha256_file(ROOT / live.GENERATED_SELECTOR_RELATIVE_PATH),
            live.GENERATED_SELECTOR_SHA256,
        )
        self.assertFalse(decision["authorization"]["payload_acquisition_or_download_authorized_now"])

    def test_plan_is_fixed_and_opens_no_input_or_network(self) -> None:
        with mock.patch.object(live, "_open_live_once", side_effect=AssertionError("network")):
            plan = live.registered_plan(ROOT)
        self.assertEqual(plan["public_or_private_inputs_accessed"], 0)
        self.assertEqual(plan["selected_private_rows"], 300)
        self.assertEqual(plan["payload_requests"], 0)
        self.assertEqual(plan["signal_target_model_or_score_operations"], 0)

    def test_machine_gate_requires_one_thread_disk_load_and_RSS(self) -> None:
        report = live.preconsumption_machine_gate(Path.cwd(), **self.machine_kwargs())
        self.assertTrue(report["passed_before_consumed_marker"])
        self.assertEqual(report["CPU_threads"], 1)
        mutations = (
            {**self.environ, live.THREAD_ENV_KEYS[0]: "2"},
            self.environ,
            self.environ,
            self.environ,
        )
        kwargs = (
            {},
            {"disk_usage_reader": lambda _path: type("Disk", (), {"free": 1})()},
            {"loadavg_reader": lambda: (9.0, 0.0, 0.0)},
            {"rss_reader": lambda: live.MAX_PEAK_RSS_BYTES + 1},
        )
        for environ, override in zip(mutations, kwargs, strict=True):
            values = self.machine_kwargs()
            values.update(override)
            values["environ"] = environ
            with self.subTest(override=override), self.assertRaises(live.LivePilotRefusal):
                live.preconsumption_machine_gate(Path.cwd(), **values)

    def test_private_reader_is_one_read_no_follow_exact_size_hash_and_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            payload = live._canonical_json_bytes(self.freewill)
            path.write_bytes(payload)
            path.chmod(0o600)
            counters = live._base_access_counters()
            observed, observed_payload = live.read_locked_freewill_manifest(
                path,
                expected_bytes=len(payload),
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                counters=counters,
            )
            self.assertEqual(observed, self.freewill)
            self.assertEqual(observed_payload, payload)
            self.assertEqual(counters["private_Freewill_manifest_content_opens"], 1)
            self.assertEqual(counters["private_Freewill_manifest_body_reads"], 1)
            self.assertEqual(counters["private_Freewill_manifest_hashes"], 1)
            self.assertEqual(counters["private_Freewill_manifest_parses"], 1)

    def test_private_reader_refuses_hash_mode_symlink_and_size(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "manifest.json"
            payload = live._canonical_json_bytes(self.freewill)
            path.write_bytes(payload)
            path.chmod(0o600)
            cases = (
                (path, len(payload), "0" * 64),
                (path, len(payload) + 1, hashlib.sha256(payload).hexdigest()),
            )
            for source, size, digest in cases:
                with self.subTest(size=size, digest=digest), self.assertRaises(live.LivePilotRefusal):
                    live.read_locked_freewill_manifest(
                        source,
                        expected_bytes=size,
                        expected_sha256=digest,
                        counters=None,
                    )
            path.chmod(0o644)
            with self.assertRaises(live.LivePilotRefusal):
                live.read_locked_freewill_manifest(
                    path,
                    expected_bytes=len(payload),
                    expected_sha256=hashlib.sha256(payload).hexdigest(),
                    counters=None,
                )
            path.chmod(0o600)
            link = root / "link.json"
            link.symlink_to(path)
            with self.assertRaises(live.LivePilotRefusal):
                live.read_locked_freewill_manifest(
                    link,
                    expected_bytes=len(payload),
                    expected_sha256=hashlib.sha256(payload).hexdigest(),
                    counters=None,
                )

    def test_wrist_parser_freezes_schema_name_rule_anchor_total_and_target_firewall(self) -> None:
        parsed = live.parse_wrist_metadata(self.wrist_payload, counters=None)
        self.assertEqual(len(parsed["participants"]), 45)
        self.assertEqual(parsed["supplementary_rows"], 10)
        self.assertEqual(parsed["declared_bytes"], live.WRIST_EXPECTED_BYTES)
        self.assertEqual(parsed["participants"]["sub-01"]["id"], live.WRIST_SUB01_FILE_ID)
        rows = json.loads(self.wrist_payload)
        cases = {}
        target = copy.deepcopy(rows)
        target[0]["target"] = "right"
        cases["target_field"] = target
        name = copy.deepcopy(rows)
        name[1]["name"] = "participant-02.zip"
        cases["name"] = name
        anchor = copy.deepcopy(rows)
        anchor[0]["computed_md5"] = "0" * 32
        anchor[0]["supplied_md5"] = "0" * 32
        cases["anchor"] = anchor
        total = copy.deepcopy(rows)
        total[-1]["size"] += 1
        cases["total"] = total
        for case, value in cases.items():
            with self.subTest(case=case), self.assertRaises(live.LivePilotRefusal):
                live.parse_wrist_metadata(live._canonical_json_bytes(value), counters=None)

    def test_direct_and_two_redirect_mock_transports_parse_identically(self) -> None:
        values = []
        for redirects in (0, 2):
            opener, resolver = live.generated_http_fixture(self.wrist_payload, redirects=redirects)
            payload, summary = live.fetch_wrist_metadata(
                opener,
                resolver=resolver,
                counters=None,
            )
            opener.assert_consumed()
            values.append(live.parse_wrist_metadata(payload, counters=None))
            self.assertEqual(summary["network_redirects"], redirects)
            self.assertEqual(summary["accepted_response_bodies"], 1)
        self.assertEqual(
            values[0]["canonical_source_sha256"],
            values[1]["canonical_source_sha256"],
        )

    def test_transport_refuses_overflow_duplicate_framing_and_private_redirect(self) -> None:
        cases = (
            live.FixtureHTTPResponse(
                b"x" * (live.MAX_NETWORK_BODY_BYTES + 1),
                status=200,
                url=live.WRIST_METADATA_URL,
                headers={"Content-Type": "application/json"},
            ),
            live.FixtureHTTPResponse(
                self.wrist_payload,
                status=200,
                url=live.WRIST_METADATA_URL,
                headers={"Content-Type": "application/json"},
                duplicate_headers=(("Content-Type", "application/json"),),
            ),
            live.FixtureHTTPResponse(
                self.wrist_payload,
                status=200,
                url=live.WRIST_METADATA_URL,
                headers={"Content-Type": "application/json", "Transfer-Encoding": "chunked"},
            ),
        )
        for response in cases:
            opener = live.FixtureOpener(
                [live.HTTPFixtureExchange(live.WRIST_METADATA_URL, response)]
            )
            with self.subTest(response=response), self.assertRaises(live.LivePilotRefusal):
                live.fetch_wrist_metadata(
                    opener,
                    resolver=lambda _hostname: ("8.8.8.8",),
                    counters=None,
                )
        redirect = live.FixtureHTTPResponse(
            b"",
            status=302,
            url=live.WRIST_METADATA_URL,
            headers={"Content-Length": "0", "Location": "https://private.example/files"},
        )
        opener = live.FixtureOpener(
            [live.HTTPFixtureExchange(live.WRIST_METADATA_URL, redirect)]
        )
        with self.assertRaises(live.LivePilotRefusal):
            live.fetch_wrist_metadata(
                opener,
                resolver=lambda _hostname: ("127.0.0.1",),
                counters=None,
            )

    def test_all_required_generated_mutations_refuse(self) -> None:
        mutations = live.run_required_mutations(
            self.freewill,
            self.wrist_payload,
            contract=self.contract,
        )
        self.assertEqual(tuple(mutations), live.REQUIRED_MUTATIONS)
        self.assertEqual(len(mutations), 26)
        self.assertTrue(all(route in live.FAILURE_ROUTES for route in mutations.values()))

    def test_generated_qualification_is_bounded_deterministic_and_private(self) -> None:
        hashes = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index in range(2):
                outcome = live.qualify_generated_mock_selector(
                    root / f"out-{index}",
                    repo_root=ROOT,
                    clock=_Clock(1.0, 1.2),
                    **self.machine_kwargs(),
                )
                live.validate_public_report(outcome.report)
                self.assertEqual(outcome.report["route"], live.GENERATED_ROUTE)
                self.assertFalse(any(outcome.report["access_counters"].values()))
                self.assertEqual(outcome.report["mutation_summary"]["passed_count"], 26)
                self.assertLessEqual(outcome.combined_output_bytes, live.MAX_COMBINED_OUTPUT_BYTES)
                self.assertEqual(
                    stat.S_IMODE(outcome.private_manifest_path.stat().st_mode),
                    0o600,
                )
                private = outcome.private_manifest_path.read_bytes()
                hashes.append(hashlib.sha256(private).hexdigest())
            self.assertEqual(hashes[0], hashes[1])

    def test_generated_output_collision_refuses_before_any_real_access(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "out"
            output.mkdir()
            with self.assertRaises(live.LivePilotRefusal):
                live.qualify_generated_mock_selector(
                    output,
                    repo_root=ROOT,
                    **self.machine_kwargs(),
                )

    def test_public_validator_refuses_private_fields_URLs_and_forbidden_counters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outcome = live.qualify_generated_mock_selector(
                Path(directory) / "out",
                repo_root=ROOT,
                clock=_Clock(1.0, 1.1),
                **self.machine_kwargs(),
            )
            for mutation in (
                lambda report: report["source_summary"].__setitem__("file_id", 1),
                lambda report: report["warnings"].append("https://example.invalid"),
                lambda report: report["access_counters"].__setitem__("signal_sample_reads", 1),
            ):
                report = copy.deepcopy(outcome.report)
                mutation(report)
                with self.assertRaises(live.LivePilotRefusal):
                    live.validate_public_report(report)

    def test_mocked_real_path_writes_marker_then_exact_private_and_public_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_mock_repo(root)
            opener, resolver = live.generated_http_fixture(self.wrist_payload, redirects=2)
            outcome = live.execute_registered_metadata_selection(
                root,
                evidence=self.evidence(),
                opener=opener,
                resolver=resolver,
                proof_verifier=lambda _root, _evidence: self.mock_implementation(),
                private_reader=self.generated_private_reader(),
                clock=_Clock(1.0, 1.2),
                **self.machine_kwargs(),
            )
            opener.assert_consumed()
            self.assertEqual(outcome.report["route"], live.SUCCESS_ROUTE)
            self.assertEqual(
                outcome.report["access_counters"]["private_Freewill_manifest_content_opens"],
                1,
            )
            self.assertEqual(
                outcome.report["access_counters"]["public_Wrist_metadata_body_reads"],
                1,
            )
            self.assertEqual(outcome.report["access_counters"]["real_member_or_archive_selections"], 300)
            marker = root / live.PRIVATE_ROOT_RELATIVE_PATH / live.CONSUMED_MARKER_NAME
            self.assertTrue(marker.is_file())
            self.assertEqual(stat.S_IMODE(marker.stat().st_mode), 0o600)
            self.assertTrue(outcome.private_manifest_path.is_file())
            self.assertEqual(stat.S_IMODE(outcome.private_manifest_path.stat().st_mode), 0o600)
            self.assertTrue(outcome.report_path.is_file())
            with self.assertRaises(live.LivePilotRefusal):
                live.execute_registered_metadata_selection(
                    root,
                    evidence=self.evidence(),
                    proof_verifier=lambda _root, _evidence: self.mock_implementation(),
                    private_reader=lambda *args, **kwargs: self.fail("second private read"),
                    opener=lambda *args, **kwargs: self.fail("second HTTP open"),
                    **self.machine_kwargs(),
                )

    def test_post_marker_parse_failure_is_aggregate_consumed_and_not_rerunnable(self) -> None:
        rows = json.loads(self.wrist_payload)
        rows[0]["target"] = "forbidden"
        payload = live._canonical_json_bytes(rows)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_mock_repo(root)
            opener, resolver = live.generated_http_fixture(payload, redirects=0)
            with self.assertRaises(live.LivePilotRefusal):
                live.execute_registered_metadata_selection(
                    root,
                    evidence=self.evidence(),
                    opener=opener,
                    resolver=resolver,
                    proof_verifier=lambda _root, _evidence: self.mock_implementation(),
                    private_reader=self.generated_private_reader(),
                    clock=_Clock(1.0, 1.1),
                    **self.machine_kwargs(),
                )
            marker = root / live.PRIVATE_ROOT_RELATIVE_PATH / live.CONSUMED_MARKER_NAME
            report_path = root / live.PUBLIC_RESULT_RELATIVE_PATH
            self.assertTrue(marker.is_file())
            report = live.inspect_public_result(report_path)
            self.assertIn(report["route"], live.FAILURE_ROUTES)
            self.assertFalse(report["acceptance_gates"]["real_metadata_selection_completed"])
            self.assertEqual(report["access_counters"]["public_aggregate_reports"], 1)
            self.assertFalse((root / live.PRIVATE_ROOT_RELATIVE_PATH / live.PRIVATE_SELECTION_NAME).exists())

    def test_machine_failure_precedes_marker_private_reader_and_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_mock_repo(root)
            values = self.machine_kwargs()
            values["disk_usage_reader"] = lambda _path: type("Disk", (), {"free": 1})()
            with self.assertRaises(live.LivePilotRefusal):
                live.execute_registered_metadata_selection(
                    root,
                    evidence=self.evidence(),
                    proof_verifier=lambda _root, _evidence: self.mock_implementation(),
                    private_reader=lambda *args, **kwargs: self.fail("private reader called"),
                    opener=lambda *args, **kwargs: self.fail("network opener called"),
                    **values,
                )
            self.assertFalse((root / live.PRIVATE_ROOT_RELATIVE_PATH).exists())
            self.assertFalse((root / live.PUBLIC_RESULT_RELATIVE_PATH).exists())

    def test_malformed_green_evidence_refuses_before_git_or_inputs(self) -> None:
        bad = live.GreenWrapperEvidence(
            implementation_commit="bad",
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="0" * 64,
        )
        with mock.patch.object(live, "_git", side_effect=AssertionError("git")):
            with self.assertRaises(live.LivePilotRefusal):
                live.verify_green_wrapper_evidence(ROOT, bad)

    def test_inspector_refuses_private_manifest(self) -> None:
        with self.assertRaises(live.LivePilotRefusal):
            live.inspect_public_result("marc1_pilot_selection.private.v0.json")

    def test_plan_CLI_has_no_execute_side_effect(self) -> None:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        process = subprocess.run(
            (
                sys.executable,
                "-m",
                "neurodecodekit.datasets.marc1_pilot_selection_live",
                "plan",
            ),
            cwd=ROOT,
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["public_or_private_inputs_accessed"], 0)

    def test_module_is_standard_library_plus_frozen_selector_and_has_no_payload_reader(self) -> None:
        source = (ROOT / "src/neurodecodekit/datasets/marc1_pilot_selection_live.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import torch",
            "import requests",
        ):
            self.assertNotIn(forbidden, source)
        self.assertNotIn("extractall", source)
        self.assertNotIn("ZipFile(", source)
        self.assertNotIn("--path", source)
        self.assertNotIn("--url", source)


if __name__ == "__main__":
    unittest.main()
