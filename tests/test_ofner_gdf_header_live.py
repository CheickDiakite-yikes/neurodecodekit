import json
import os
import subprocess
import sys
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import ofner_gdf_header_live as live

ROOT = Path(__file__).resolve().parents[1]


class OfnerGDFHeaderLiveProofTests(unittest.TestCase):
    def test_green_decision_and_frozen_prerequisites_are_exact(self):
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["maintainer_words"], "continue")
        self.assertEqual(live.GREEN_DECISION_COMMIT, "8ed4b7c93ad1a53c30bdacac63934a30d9f6a2f4")
        self.assertEqual(live.GREEN_DECISION_CI_RUN_ID, 33_275_389_198)

    def test_plan_is_activation_locked_and_narrow(self):
        plan = live.registered_plan(ROOT)
        activation_present = (ROOT / live.ACTIVATION_RELATIVE_PATH).is_file()
        expected_status = (
            "activation_record_present" if activation_present else "activation_locked"
        )
        self.assertEqual(plan["status"], expected_status)
        self.assertEqual(plan["activation_record_present"], activation_present)
        self.assertFalse(plan["real_invocation_available"])
        self.assertEqual(plan["member"]["bytes"], 105_365_484)
        self.assertEqual(plan["whole_file_requests"], 0)
        self.assertFalse(plan["scientific_claim_established"])

    def test_execute_refuses_without_activation_before_opener_or_marker(self):
        calls = []

        def opener_factory():
            calls.append("constructed")
            raise AssertionError("opener must remain unreachable")

        evidence = live.LiveEvidence("a" * 64, "b" * 40, 1, 2, 3)
        with self.assertRaises(live.OfnerGDFHeaderLiveRefusal) as caught:
            live.execute_registered_checkpoint(
                evidence,
                repo_root=ROOT,
                opener_factory=opener_factory,
            )
        self.assertEqual(caught.exception.code, "OHL-PROOF")
        self.assertEqual(calls, [])

    def test_remote_proof_binds_three_exact_runs(self):
        evidence = live._generated_evidence()
        activation = {
            "green_implementation": {
                "commit": "c" * 40,
                "CI_run_id": 4,
                "base_python_job_id": 5,
                "optional_neuro_readers_job_id": 6,
            }
        }
        proof = {
            "remote_main_commit": evidence.activation_commit,
            "activation_is_remote_main": True,
            "fresh_git_remote_calls": 1,
            "fresh_GitHub_Actions_calls": 3,
            "runs": [
                {
                    "commit": live.GREEN_DECISION_COMMIT,
                    "CI_run_id": live.GREEN_DECISION_CI_RUN_ID,
                    "base_python_job_id": live.GREEN_DECISION_BASE_JOB_ID,
                    "optional_neuro_readers_job_id": live.GREEN_DECISION_OPTIONAL_JOB_ID,
                    "both_required_jobs_green": True,
                },
                {
                    "commit": "c" * 40,
                    "CI_run_id": 4,
                    "base_python_job_id": 5,
                    "optional_neuro_readers_job_id": 6,
                    "both_required_jobs_green": True,
                },
                {
                    "commit": evidence.activation_commit,
                    "CI_run_id": 1,
                    "base_python_job_id": 2,
                    "optional_neuro_readers_job_id": 3,
                    "both_required_jobs_green": True,
                },
            ],
        }
        live.validate_remote_green_proof(proof, activation, evidence)
        for key, replacement in (
            ("remote_main_commit", "d" * 40),
            ("activation_is_remote_main", False),
            ("fresh_git_remote_calls", 0),
            ("fresh_GitHub_Actions_calls", 2),
        ):
            candidate = json.loads(json.dumps(proof))
            candidate[key] = replacement
            with self.subTest(key=key), self.assertRaises(live.OfnerGDFHeaderLiveRefusal):
                live.validate_remote_green_proof(candidate, activation, evidence)


class OfnerGDFHeaderLiveCapabilityTests(unittest.TestCase):
    def workspace(self, parent: Path, name: str) -> Path:
        root = parent / name
        root.mkdir(mode=0o700)
        (root / ".codex_work").mkdir(mode=0o700)
        return root

    def test_generated_H1_is_deterministic_marker_first_and_body_free(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            first, opener, events = live._run_generated_case(
                self.workspace(parent, "first"), "result"
            )
            replay, replay_opener, replay_events = live._run_generated_case(
                self.workspace(parent, "replay"), "result"
            )
            self.assertEqual(first["route"], "OFNER-H1")
            self.assertEqual(replay["route"], "OFNER-H1")
            self.assertEqual(first["measurement_contract"], replay["measurement_contract"])
            self.assertEqual(events[:2], ["marker_durable", "opener_constructed"])
            self.assertEqual(replay_events[:2], ["marker_durable", "opener_constructed"])
            self.assertEqual(len(opener.requests), 3)
            self.assertEqual(len(replay_opener.requests), 3)
            self.assertEqual(first["payload_retained_bytes"], 0)
            self.assertTrue(all(response.closed for response in opener.responses))

    def test_request_schedule_is_manifest_then_two_exact_ranges(self):
        with tempfile.TemporaryDirectory() as name:
            root = self.workspace(Path(name), "requests")
            _report, opener, _events = live._run_generated_case(root, "result")
            self.assertEqual(
                [request.full_url for request in opener.requests],
                [live.MANIFEST_URL, live.MEMBER_URL, live.MEMBER_URL],
            )
            self.assertEqual(
                [live._request_headers(request).get("range") for request in opener.requests],
                [None, "bytes=0-255", "bytes=256-24831"],
            )

    def test_consumed_marker_refuses_rerun_before_second_opener(self):
        with tempfile.TemporaryDirectory() as name:
            root = self.workspace(Path(name), "rerun")
            live._run_generated_case(root, "first")
            with self.assertRaises(live.OfnerGDFHeaderLiveRefusal) as caught:
                live._run_generated_case(root, "second")
            self.assertEqual(caught.exception.code, "OHL-MARKER")

    def test_transport_and_representation_routes_remain_distinct(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)

            def bad_status(values):
                values[1].status = 200

            transport, _opener, _events = live._run_generated_case(
                self.workspace(parent, "transport"),
                "result",
                response_mutator=bad_status,
            )

            def bad_version(payload):
                value = bytearray(payload)
                value[:8] = b"GDF 1.25"
                return bytes(value)

            representation, _opener, _events = live._run_generated_case(
                self.workspace(parent, "representation"),
                "result",
                fixture_mutator=bad_version,
            )
            self.assertEqual(transport["route"], "OFNER-H0-TRANSPORT")
            self.assertEqual(representation["route"], "OFNER-H0-REPRESENTATION")

    def test_resource_gate_refuses_threads_disk_and_rss(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            cases = (
                ({}, live._generated_disk_usage, lambda: 1),
                (
                    live._generated_environment(),
                    lambda _path: type(
                        "Usage", (), {"free": live.MINIMUM_FREE_DISK_BYTES - 1}
                    )(),
                    lambda: 1,
                ),
                (
                    live._generated_environment(),
                    live._generated_disk_usage,
                    lambda: live.MAX_PEAK_RSS_BYTES + 1,
                ),
            )
            for environ, disk_reader, rss_reader in cases:
                with self.assertRaises(live.OfnerGDFHeaderLiveRefusal):
                    live.preconsumption_machine_gate(
                        root,
                        environ=environ,
                        disk_usage_reader=disk_reader,
                        rss_reader=rss_reader,
                    )

    def test_capability_chain_refuses_symlink(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            root = self.workspace(parent, "symlink")
            (root / ".codex_work").rmdir()
            os.symlink(parent, root / ".codex_work")
            with self.assertRaises(live.OfnerGDFHeaderLiveRefusal):
                live._create_private_chain(root)

    def test_public_report_rejects_forbidden_fields(self):
        report = live._public_report(
            route="OFNER-H0-TRANSPORT",
            refusal_code="OHL-TRANSPORT",
            parsed=None,
            resources={
                "runtime_seconds": 0.1,
                "peak_process_RSS_bytes": 1,
                "free_disk_bytes": 3 * 1024**3,
                "private_allocated_bytes": 1,
            },
            counters=live._base_operation_counters(),
            marker_bytes=1,
            remote_proof=live._generated_remote_proof(),
            generated_only=True,
        )
        report["private_path"] = "/secret"
        with self.assertRaises(live.OfnerGDFHeaderLiveRefusal):
            live._validate_public_report(report)

    def test_live_opener_disables_proxy_and_redirects(self):
        with mock.patch("urllib.request.build_opener") as build:
            build.return_value.open = mock.Mock()
            live.build_live_opener()
        handlers = build.call_args.args
        proxy = next(
            handler for handler in handlers if isinstance(handler, urllib.request.ProxyHandler)
        )
        self.assertEqual(proxy.proxies, {})
        self.assertTrue(any(handler is live._NoRedirect for handler in handlers))

    def test_cli_help_exposes_activation_arguments(self):
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        completed = subprocess.run(
            [sys.executable, "-m", "neurodecodekit.ofner_gdf_header_live_cli", "--help"],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("qualify", completed.stdout)
        self.assertIn("execute", completed.stdout)
        execute = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.ofner_gdf_header_live_cli",
                "execute",
                "--help",
            ],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn("--activation-sha256", execute.stdout)


if __name__ == "__main__":
    unittest.main()
