from __future__ import annotations

import ast
import io
import json
import os
import stat
import tempfile
import unittest
import urllib.request
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from neurodecodekit.datasets import marc1_source_aware_inventory_attestation as attestor
from neurodecodekit.datasets import marc1_source_aware_live_metadata as live


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = (
    ROOT / "src" / "neurodecodekit" / "datasets" / "marc1_source_aware_live_metadata.py"
)
THREAD_ENVIRONMENT = {key: "1" for key in live.THREAD_ENV_KEYS}


def _temporary_directory() -> tempfile.TemporaryDirectory[str]:
    return tempfile.TemporaryDirectory(dir=os.path.realpath(tempfile.gettempdir()))


def _body(family: str = "observed_extension_exact") -> bytes:
    return live._canonical_json_bytes(attestor.build_generated_family(family))


def _response(
    body: bytes,
    *,
    headers: list[tuple[str, str]] | None = None,
    status: int = 200,
    url: str = live.SOURCE_URL,
) -> live._MemoryResponse:
    return live._MemoryResponse(body, headers=headers, status=status, url=url)


def _evidence() -> live.GreenWrapperEvidence:
    return live.GreenWrapperEvidence(
        implementation_commit="a" * 40,
        implementation_ci_run_id=1,
        implementation_base_job_id=2,
        implementation_optional_job_id=3,
        implementation_registry_sha256="b" * 64,
    )


def _proof_verifier(
    root: str | Path,
    evidence: live.GreenWrapperEvidence,
    ledger: live.AccessLedger,
) -> dict:
    del root, evidence
    ledger.increment("proof_validations")
    return {"execution_state": {"public_execution_consumed": False}}


class MARC1SourceAwareLiveMetadataTests(unittest.TestCase):
    def test_source_surface_is_additive_standard_library_and_not_consumed(self) -> None:
        source = SOURCE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        allowed = {
            "__future__",
            "argparse",
            "dataclasses",
            "hashlib",
            "io",
            "json",
            "math",
            "neurodecodekit",
            "os",
            "pathlib",
            "re",
            "resource",
            "shutil",
            "stat",
            "subprocess",
            "sys",
            "tempfile",
            "time",
            "typing",
            "urllib",
        }
        self.assertEqual(imports - allowed, set())
        self.assertNotIn("marc1_paginated_live_metadata", source)
        self.assertNotIn("torch", imports)
        self.assertNotIn("mne", imports)
        self.assertNotIn("numpy", imports)

    def test_registered_plan_is_zero_payload_and_same_path(self) -> None:
        plan = live.registered_plan()
        self.assertEqual(plan["lane_id"], "MARC1-SA1A")
        self.assertEqual(plan["green_parent_decision"]["commit"], live.GREEN_DECISION_COMMIT)
        self.assertEqual(plan["source"]["request_attempts"], 1)
        self.assertEqual(plan["source"]["response_cap_bytes"], 2 * 1024**2)
        self.assertEqual((plan["payload_requests"], plan["payload_bytes"]), (0, 0))
        self.assertEqual(plan["signal_target_model_score_operations"], 0)
        self.assertFalse(plan["scientific_claim_upgrade"])

    def test_request_identity_is_fixed_and_credentials_are_refused(self) -> None:
        request = live.build_registered_request()
        self.assertEqual(request.full_url, live.SOURCE_URL)
        self.assertEqual(request.get_method(), "GET")
        self.assertIsNone(request.data)
        live.validate_registered_request(request)
        request.add_header("Authorization", "Bearer forbidden")
        with self.assertRaisesRegex(live.LiveMetadataRefusal, "registered request differs"):
            live.validate_registered_request(request)

    def test_response_accepts_exact_three_framing_forms(self) -> None:
        body = _body()
        cases = (
            (
                [("Content-Type", "application/json")],
                "close",
            ),
            (
                [
                    ("Content-Type", "application/json; charset=UTF-8"),
                    ("Content-Length", str(len(body))),
                ],
                "content_length",
            ),
            (
                [
                    ("Content-Type", "application/json"),
                    ("Transfer-Encoding", "chunked"),
                ],
                "chunked",
            ),
        )
        for headers, framing in cases:
            with self.subTest(framing=framing):
                result = live.read_registered_response(_response(body, headers=headers))
                self.assertEqual(result.body, body)
                self.assertEqual(result.framing, framing)
                self.assertEqual(result.observed_bytes, len(body))

    def test_response_refuses_status_redirect_coding_framing_and_overflow(self) -> None:
        body = _body()
        cases = (
            _response(body, status=404),
            _response(body, url=live.SOURCE_URL + "&next=1"),
            _response(
                body,
                headers=[("Content-Type", "application/json"), ("Content-Encoding", "gzip")],
            ),
            _response(
                body,
                headers=[
                    ("Content-Type", "application/json"),
                    ("Content-Length", str(len(body))),
                    ("Transfer-Encoding", "chunked"),
                ],
            ),
            _response(b"x" * (live.MAX_RESPONSE_BYTES + 1)),
        )
        for response in cases:
            with self.subTest(headers=response.headers.raw_items()):
                with self.assertRaises(live.LiveMetadataRefusal):
                    live.read_registered_response(response)

    def test_every_source_family_reaches_the_frozen_wrapper_route(self) -> None:
        for family, source_route in attestor.FAMILY_ROUTES.items():
            with self.subTest(family=family):
                ledger = live.AccessLedger()
                result = live.fetch_and_attest(
                    opener=live._memory_opener(_body(family)),
                    ledger=ledger,
                    public_request=False,
                )
                self.assertEqual(result.source_attestation.route, source_route)
                self.assertEqual(result.wrapper_route, live.SOURCE_ROUTE_MAP[source_route])
                self.assertEqual(ledger.values["public_HTTP_requests"], 0)
                self.assertEqual(ledger.values["payload_bytes"], 0)

    def test_drift_and_unknown_extensions_never_expose_selection(self) -> None:
        for family in ("single_historical_drift", "unknown_non_target_extension"):
            result = live.fetch_and_attest(
                opener=live._memory_opener(_body(family)),
                ledger=live.AccessLedger(),
                public_request=False,
            )
            self.assertEqual(result.wrapper_route, live.BLOCKED_ROUTE)
            self.assertFalse(result.source_attestation.selection_available)
            self.assertIsNone(
                result.source_attestation.private_record["private_selection"]
            )

    def test_target_duplicate_JSON_and_MD5_disagreement_fail_closed(self) -> None:
        target_rows = attestor.build_generated_family("observed_extension_exact")
        target_rows[0]["target_text"] = "forbidden"
        md5_rows = attestor.build_generated_family("observed_extension_exact")
        md5_rows[0]["computed_md5"] = "0" * 32
        cases = (
            (live._canonical_json_bytes(target_rows), live.FAILURE_ROUTES["target_or_semantics"]),
            (b'[{"id":1,"id":2}]', live.FAILURE_ROUTES["transport_or_json"]),
            (live._canonical_json_bytes(md5_rows), live.FAILURE_ROUTES["target_or_semantics"]),
        )
        for body, route in cases:
            with self.subTest(route=route):
                with self.assertRaises(live.LiveMetadataRefusal) as raised:
                    live.fetch_and_attest(
                        opener=live._memory_opener(body),
                        ledger=live.AccessLedger(),
                        public_request=False,
                    )
                self.assertEqual(raised.exception.route, route)

    def test_generated_qualification_replays_cleans_and_stays_target_free(self) -> None:
        with _temporary_directory() as tmp:
            output = Path(tmp) / "qualification"
            clock_values = iter((10.0, 10.1))
            outcome = live.qualify_generated_mock_wrapper(
                output,
                repo_root=ROOT,
                environ=THREAD_ENVIRONMENT,
                clock=lambda: next(clock_values),
                rss_reader=lambda: 20 * 1024**2,
            )
        report = outcome.report
        self.assertEqual(report["route"], live.GENERATED_ROUTE)
        self.assertTrue(report["deterministic_replay"])
        self.assertEqual(
            report["generated_family_routes"], dict(attestor.FAMILY_ROUTES)
        )
        self.assertEqual(report["refusal_summary"]["passed"], len(live.GENERATED_REFUSALS))
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertEqual(report["access_counters"]["public_HTTP_requests"], 0)
        self.assertEqual(report["access_counters"]["payload_bytes"], 0)
        self.assertEqual(report["access_counters"]["target_reads"], 0)
        self.assertEqual(report["access_counters"]["model_runs"], 0)
        self.assertTrue(outcome.output_removed)
        self.assertFalse(output.exists())

    def test_generated_qualification_is_deterministic_under_fixed_resources(self) -> None:
        reports = []
        with _temporary_directory() as tmp:
            for index in range(2):
                values = iter((4.0, 4.25))
                outcome = live.qualify_generated_mock_wrapper(
                    Path(tmp) / f"qualification-{index}",
                    repo_root=ROOT,
                    environ=THREAD_ENVIRONMENT,
                    clock=lambda values=values: next(values),
                    rss_reader=lambda: 16 * 1024**2,
                )
                reports.append(live._canonical_json_bytes(outcome.report))
        self.assertEqual(reports[0], reports[1])

    def test_live_mock_success_writes_exact_modes_and_refuses_second_invocation(self) -> None:
        calls = []

        def opener(request: urllib.request.Request, timeout: float):
            calls.append((request.full_url, timeout))
            return _response(_body())

        with _temporary_directory() as tmp:
            root = Path(tmp)
            values = iter((1.0, 1.1))
            outcome = live.execute_registered_metadata_check(
                root,
                evidence=_evidence(),
                environ=THREAD_ENVIRONMENT,
                opener=opener,
                proof_verifier=_proof_verifier,
                disk_usage_reader=lambda path: SimpleNamespace(free=20 * 1024**3),
                cpu_count_reader=lambda: 8,
                loadavg_reader=lambda: (0.8, 0.8, 0.8),
                clock=lambda: next(values),
                rss_reader=lambda: 20 * 1024**2,
            )
            output = root / live.REAL_ROOT_RELATIVE_PATH
            self.assertEqual(set(path.name for path in output.iterdir()), set(live.OUTPUT_NAMES))
            self.assertEqual(stat.S_IMODE((output / live.MARKER_NAME).stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((output / live.PRIVATE_NAME).stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((output / live.REPORT_NAME).stat().st_mode), 0o644)
            public = live.inspect_public_result(output / live.REPORT_NAME)
            private = json.loads((output / live.PRIVATE_NAME).read_text(encoding="utf-8"))
            self.assertEqual(public["route"], live.SUCCESS_ROUTE)
            self.assertTrue(public["source_aware_summary"]["selection_available"])
            self.assertEqual(len(private["attestation"]["private_selection"]["subjects"]), 12)
            with self.assertRaisesRegex(live.LiveMetadataRefusal, "output already exists"):
                live.execute_registered_metadata_check(
                    root,
                    evidence=_evidence(),
                    environ=THREAD_ENVIRONMENT,
                    opener=opener,
                    proof_verifier=_proof_verifier,
                )
            self.assertEqual(len(calls), 1)
            self.assertFalse(outcome.output_removed)

    def test_live_mock_drift_blocks_selection_without_payload(self) -> None:
        with _temporary_directory() as tmp:
            root = Path(tmp)
            values = iter((2.0, 2.1))
            outcome = live.execute_registered_metadata_check(
                root,
                evidence=_evidence(),
                environ=THREAD_ENVIRONMENT,
                opener=live._memory_opener(_body("single_historical_drift")),
                proof_verifier=_proof_verifier,
                disk_usage_reader=lambda path: SimpleNamespace(free=20 * 1024**3),
                cpu_count_reader=lambda: 8,
                loadavg_reader=lambda: (0.8, 0.8, 0.8),
                clock=lambda: next(values),
                rss_reader=lambda: 20 * 1024**2,
            )
            private = json.loads(outcome.private_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(outcome.report["route"], live.BLOCKED_ROUTE)
        self.assertFalse(outcome.report["source_aware_summary"]["selection_available"])
        self.assertIsNone(private["attestation"]["private_selection"])
        self.assertEqual(outcome.report["access_counters"]["payload_bytes"], 0)

    def test_post_marker_target_failure_retains_only_marker_and_aggregate_receipt(self) -> None:
        rows = attestor.build_generated_family("observed_extension_exact")
        rows[0]["target_text"] = "forbidden"
        with _temporary_directory() as tmp:
            root = Path(tmp)
            values = iter((3.0, 3.1, 3.2))
            with self.assertRaises(live.LiveMetadataRefusal) as raised:
                live.execute_registered_metadata_check(
                    root,
                    evidence=_evidence(),
                    environ=THREAD_ENVIRONMENT,
                    opener=live._memory_opener(live._canonical_json_bytes(rows)),
                    proof_verifier=_proof_verifier,
                    disk_usage_reader=lambda path: SimpleNamespace(free=20 * 1024**3),
                    cpu_count_reader=lambda: 8,
                    loadavg_reader=lambda: (0.8, 0.8, 0.8),
                    clock=lambda: next(values),
                    rss_reader=lambda: 20 * 1024**2,
                )
            output = root / live.REAL_ROOT_RELATIVE_PATH
            names = {path.name for path in output.iterdir()}
            self.assertEqual(names, {live.MARKER_NAME, live.REPORT_NAME})
            report = json.loads((output / live.REPORT_NAME).read_text(encoding="utf-8"))
        self.assertEqual(raised.exception.route, live.FAILURE_ROUTES["target_or_semantics"])
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["route"], live.FAILURE_ROUTES["target_or_semantics"])

    def test_machine_refusal_occurs_before_root_marker_or_request(self) -> None:
        calls = []
        with _temporary_directory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(live.LiveMetadataRefusal, "thread environment"):
                live.execute_registered_metadata_check(
                    root,
                    evidence=_evidence(),
                    environ={**THREAD_ENVIRONMENT, live.THREAD_ENV_KEYS[0]: "2"},
                    opener=lambda request, timeout: calls.append((request, timeout)),
                    proof_verifier=_proof_verifier,
                )
            self.assertFalse((root / live.REAL_ROOT_RELATIVE_PATH).exists())
        self.assertEqual(calls, [])

    def test_public_report_rejects_individual_identity_and_private_inspection(self) -> None:
        with _temporary_directory() as tmp:
            output = Path(tmp) / "result"
            output.mkdir()
            private = output / live.PRIVATE_NAME
            private.write_text("{}", encoding="utf-8")
            with self.assertRaises(live.LiveMetadataRefusal):
                live.inspect_public_result(private)
        with self.assertRaisesRegex(live.LiveMetadataRefusal, "private-value"):
            live._walk_public({"warning": "sub-01"})

    def test_resource_caps_fail_closed(self) -> None:
        with self.assertRaisesRegex(live.LiveMetadataRefusal, "resource cap"):
            live._enforce_resources(
                runtime_seconds=31.0,
                peak_rss_bytes=1,
                combined_output_bytes=1,
                report_bytes=1,
                environ=THREAD_ENVIRONMENT,
            )
        with self.assertRaisesRegex(live.LiveMetadataRefusal, "resource cap"):
            live._enforce_resources(
                runtime_seconds=1.0,
                peak_rss_bytes=live.MAX_PEAK_RSS_BYTES + 1,
                combined_output_bytes=1,
                report_bytes=1,
                environ=THREAD_ENVIRONMENT,
            )

    def test_cli_help_plan_and_missing_command_make_no_live_request(self) -> None:
        for args in ([], ["plan"]):
            stream = io.StringIO()
            with patch.object(live, "_open_live_once") as opener, redirect_stdout(stream):
                self.assertEqual(live.main(args), 0)
                opener.assert_not_called()
            self.assertTrue(stream.getvalue())


if __name__ == "__main__":
    unittest.main()
