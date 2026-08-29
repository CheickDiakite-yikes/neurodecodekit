import hashlib
import json
import os
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import dreyer_c5r_1_stage_h as stage_h
from neurodecodekit.datasets import dreyer_c5r_1_stage_h_live as live

ROOT = Path(__file__).resolve().parents[1]


class DreyerStageHLiveProofTests(unittest.TestCase):
    def test_green_decision_and_frozen_stage_h_artifacts_are_exact(self):
        decision = live.load_green_decision(ROOT)
        self.assertEqual(decision["maintainer_words"], "continue, make a deep push")
        self.assertEqual(live.GREEN_DECISION_COMMIT, "de6cf80f4bd243e7e60a6933445d0a65291abb90")
        self.assertEqual(live.GREEN_DECISION_CI_RUN_ID, 33_230_243_142)
        for path, digest in live.FROZEN_STAGE_H_ARTIFACTS:
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_plan_is_activation_locked_and_narrow(self):
        plan = live.registered_plan(ROOT)
        self.assertEqual(plan["status"], "activation_locked")
        self.assertFalse(plan["activation_record_present"])
        self.assertFalse(plan["real_invocation_available"])
        self.assertEqual(plan["member"]["bytes"], 14_805_604)
        self.assertEqual(plan["remaining_119_payload_requests"], 0)
        self.assertFalse(plan["scientific_claim_established"])

    def test_execute_refuses_without_activation_before_opener_or_marker(self):
        opener_calls = []

        def opener_factory():
            opener_calls.append("constructed")
            raise AssertionError("opener must remain unreachable")

        evidence = live.LiveEvidence(
            activation_sha256="a" * 64,
            activation_commit="b" * 40,
            activation_ci_run_id=1,
            activation_base_job_id=2,
            activation_optional_job_id=3,
        )
        with self.assertRaises(live.StageHLiveRefusal) as caught:
            live.execute_registered_preflight(
                evidence,
                repo_root=ROOT,
                opener_factory=opener_factory,
            )
        self.assertEqual(caught.exception.code, "HL1-PROOF")
        self.assertEqual(opener_calls, [])

    def test_remote_proof_binds_all_three_green_runs(self):
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
                    "CI_run_id": evidence.activation_ci_run_id,
                    "base_python_job_id": evidence.activation_base_job_id,
                    "optional_neuro_readers_job_id": evidence.activation_optional_job_id,
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
            with self.subTest(key=key), self.assertRaises(live.StageHLiveRefusal):
                live.validate_remote_green_proof(candidate, activation, evidence)


class DreyerStageHLiveCapabilityTests(unittest.TestCase):
    def _workspace(self, parent: Path, name: str) -> Path:
        root = parent / name
        root.mkdir(mode=0o700)
        (root / ".codex_work").mkdir(mode=0o700)
        return root

    def test_generated_H1_is_deterministic_marker_first_and_closed(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            first_root = self._workspace(parent, "first")
            second_root = self._workspace(parent, "second")
            first, first_opener, first_events = live._run_generated_valid_case(
                first_root, "result"
            )
            second, second_opener, second_events = live._run_generated_valid_case(
                second_root, "result"
            )
            self.assertEqual(first["route"], "DREYER-H1")
            self.assertEqual(second["route"], "DREYER-H1")
            self.assertEqual(first["sensor_contract"], second["sensor_contract"])
            self.assertEqual(first_events[:2], ["marker_durable", "opener_constructed"])
            self.assertEqual(second_events[:2], ["marker_durable", "opener_constructed"])
            self.assertEqual(first_opener.constructions, 1)
            self.assertEqual(first_opener.requests, 1)
            self.assertTrue(first_opener.response.closed)
            self.assertTrue(second_opener.response.closed)
            self.assertTrue(
                (
                    first_root
                    / live.PRIVATE_ROOT_RELATIVE_PATH
                    / live.CONSUMED_MARKER_NAME
                ).is_file()
            )
            self.assertTrue(
                (
                    first_root
                    / live.PRIVATE_ROOT_RELATIVE_PATH
                    / live.PRIVATE_PAYLOAD_NAME
                ).is_file()
            )

    def test_consumed_marker_refuses_rerun_before_second_opener(self):
        with tempfile.TemporaryDirectory() as name:
            root = self._workspace(Path(name), "rerun")
            live._run_generated_valid_case(root, "first")
            with self.assertRaises(live.StageHLiveRefusal) as caught:
                live._run_generated_valid_case(root, "second")
            self.assertEqual(caught.exception.code, "HL1-MARKER")

    def test_header_geometry_mismatch_routes_aggregate_H0(self):
        body = live._generated_body(wrong_geometry=True)
        original_spec = stage_h.REGISTERED_SPEC
        original_bytes = stage_h.PREFLIGHT_BYTES
        original_sha = stage_h.PREFLIGHT_SHA256
        stage_h.PREFLIGHT_BYTES = len(body)
        stage_h.PREFLIGHT_SHA256 = hashlib.sha256(body).hexdigest()
        stage_h.REGISTERED_SPEC = stage_h.PreflightSpec(
            stage_h.PREFLIGHT_URL,
            stage_h.PREFLIGHT_PATH,
            len(body),
            stage_h.PREFLIGHT_SHA256,
        )
        try:
            with tempfile.TemporaryDirectory() as name:
                root = self._workspace(Path(name), "h0")
                response = live.GeneratedResponse(body, url=stage_h.PREFLIGHT_URL)
                report = live._execute_after_proof(
                    root,
                    root / "result.json",
                    live._generated_evidence(),
                    live._generated_remote_proof(),
                    live.GeneratedOpenerFactory(response),
                    environ=live._generated_environment(),
                    disk_usage_reader=live._generated_disk_usage,
                    rss_reader=lambda: 16 * 1024**2,
                    generated_only=True,
                )
                self.assertEqual(report["route"], "DREYER-H0")
                self.assertEqual(report["refusal_code"], "HL1-HEADER")
                self.assertFalse(report["payload_retained_private"])
                self.assertIsNone(report["sensor_contract"])
                compact = json.dumps(report).casefold()
                for forbidden in ("generated-patient", "generated-recording", "raw_header"):
                    self.assertNotIn(forbidden, compact)
        finally:
            stage_h.REGISTERED_SPEC = original_spec
            stage_h.PREFLIGHT_BYTES = original_bytes
            stage_h.PREFLIGHT_SHA256 = original_sha

    def test_existing_parser_is_restored_after_success_and_refusal(self):
        original = stage_h.parse_edf_fixed_header
        with tempfile.TemporaryDirectory() as name:
            root = self._workspace(Path(name), "parser")
            live._run_generated_valid_case(root, "success")
        self.assertIs(stage_h.parse_edf_fixed_header, original)
        response = live._MonitoredResponse(
            live.GeneratedResponse(b"bad", url=stage_h.PREFLIGHT_URL),
            Path(tempfile.gettempdir()),
            live.MachineSnapshot(20 * 1024**3, 1, 0.0),
            clock=lambda: 0.0,
            rss_reader=lambda: 1,
            disk_usage_reader=live._generated_disk_usage,
        )
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaises(live.StageHLiveRefusal):
                live._stream_with_single_summary(response, Path(name) / "bad.edf")
        self.assertIs(stage_h.parse_edf_fixed_header, original)

    def test_transport_refuses_encoding_transfer_and_duplicate_length(self):
        body = live._generated_body()
        cases = {
            "content_encoding": (
                ("Content-Length", str(len(body))),
                ("Content-Encoding", "identity"),
            ),
            "transfer_encoding": (
                ("Content-Length", str(len(body))),
                ("Transfer-Encoding", "chunked"),
            ),
            "duplicate_length": (
                ("Content-Length", str(len(body))),
                ("Content-Length", str(len(body))),
            ),
        }
        original_bytes = stage_h.PREFLIGHT_BYTES
        stage_h.PREFLIGHT_BYTES = len(body)
        try:
            for name, headers in cases.items():
                response = live.GeneratedResponse(
                    body,
                    url=stage_h.PREFLIGHT_URL,
                    headers=headers,
                )
                with self.subTest(name=name), self.assertRaises(live.StageHLiveRefusal):
                    live._critical_headers(response)
        finally:
            stage_h.PREFLIGHT_BYTES = original_bytes

    def test_resource_gate_refuses_thread_disk_and_rss_drift(self):
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
                with self.assertRaises(live.StageHLiveRefusal):
                    live.preconsumption_machine_gate(
                        root,
                        environ=environ,
                        disk_usage_reader=disk_reader,
                        rss_reader=rss_reader,
                    )

    def test_capability_chain_refuses_symlink_and_non_directory(self):
        with tempfile.TemporaryDirectory() as name:
            parent = Path(name)
            symlink_root = self._workspace(parent, "symlink")
            (symlink_root / ".codex_work").rmdir()
            os.symlink(parent, symlink_root / ".codex_work")
            with self.assertRaises(live.StageHLiveRefusal):
                live._create_private_chain(symlink_root)
            file_root = self._workspace(parent, "file")
            (file_root / ".codex_work").rmdir()
            (file_root / ".codex_work").write_text("not a directory", encoding="ascii")
            with self.assertRaises(live.StageHLiveRefusal):
                live._create_private_chain(file_root)

    def test_atomic_no_replace_refuses_destination_race(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "source"
            destination = root / "destination"
            source.write_bytes(b"source")
            destination.write_bytes(b"preserve")
            with self.assertRaises(live.StageHLiveRefusal):
                live._atomic_no_replace(source, destination)
            self.assertEqual(source.read_bytes(), b"source")
            self.assertEqual(destination.read_bytes(), b"preserve")

    def test_public_report_rejects_forbidden_private_fields(self):
        report = live._public_report(
            route="DREYER-H0",
            refusal_code="HL1-HEADER",
            sensor_contract=None,
            resources={
                "runtime_seconds": 0.1,
                "peak_process_RSS_bytes": 1,
                "free_disk_bytes": 20 * 1024**3,
                "private_allocated_bytes": 1,
            },
            counters=live._base_operation_counters(),
            marker_bytes=1,
            payload_retained=False,
            remote_proof=live._generated_remote_proof(),
            generated_only=True,
        )
        report["private_path"] = "/secret"
        with self.assertRaises(live.StageHLiveRefusal):
            live._validate_public_report(report)

    def test_live_opener_disables_proxies_and_redirects(self):
        with mock.patch("urllib.request.build_opener") as build:
            build.return_value.open = mock.Mock()
            live.build_live_opener()
        handlers = build.call_args.args
        self.assertTrue(
            any(isinstance(handler, urllib.request.ProxyHandler) for handler in handlers)
        )
        proxy = next(
            handler
            for handler in handlers
            if isinstance(handler, urllib.request.ProxyHandler)
        )
        self.assertEqual(proxy.proxies, {})
        self.assertTrue(any(handler is live._NoRedirect for handler in handlers))


if __name__ == "__main__":
    unittest.main()
