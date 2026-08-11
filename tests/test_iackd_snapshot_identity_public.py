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

from neurodecodekit.datasets import iackd_snapshot_identity as identity
from neurodecodekit.datasets import iackd_snapshot_identity_public as public


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {key: "1" for key in public.THREAD_ENV_KEYS}


class IACKDSnapshotIdentityPublicCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = identity.load_registered_contract(ROOT)
        cls.payload = identity.make_generated_response(cls.contract)

    def safe_machine_kwargs(self) -> dict[str, object]:
        return {
            "environ": THREAD_ENV,
            "disk_usage_reader": lambda _path: SimpleNamespace(
                free=public.MINIMUM_FREE_DISK_BYTES + 1
            ),
            "cpu_count_reader": lambda: 8,
            "loadavg_reader": lambda: (4.0, 0.0, 0.0),
            "rss_reader": lambda: 32 * 1024 * 1024,
        }

    def evidence(self) -> public.GreenWrapperEvidence:
        return public.GreenWrapperEvidence(
            implementation_commit="a" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="b" * 64,
        )

    def test_frozen_query_and_request_are_byte_exact(self) -> None:
        self.assertEqual(len(public.QUERY.encode("utf-8")), 316)
        self.assertEqual(
            hashlib.sha256(public.QUERY.encode("utf-8")).hexdigest(),
            public.QUERY_SHA256,
        )
        self.assertEqual(len(public.REQUEST_BODY), 355)
        self.assertEqual(
            hashlib.sha256(public.REQUEST_BODY).hexdigest(),
            public.REQUEST_SHA256,
        )
        self.assertEqual(
            json.loads(public.REQUEST_BODY),
            {"query": public.QUERY},
        )

    def test_green_decision_and_canonicalizer_hash_are_exact(self) -> None:
        decision = public.load_green_decision(ROOT)
        self.assertEqual(decision["lane_id"], "IACKD-M1A")
        self.assertTrue(
            decision["authorization"][
                "one_public_GraphQL_request_authorized_after_wrapper_green"
            ]
        )
        self.assertFalse(
            decision["authorization"]["S3_payload_request_or_download_authorized_now"]
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / public.CANONICALIZER_RELATIVE_PATH).read_bytes()
            ).hexdigest(),
            public.CANONICALIZER_SHA256,
        )

    def test_request_has_no_credentials_variables_or_alternate_endpoint(self) -> None:
        request = public.build_locked_request()
        self.assertEqual(request.full_url, public.ENDPOINT)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.data, public.REQUEST_BODY)
        headers = {key.casefold(): value for key, value in request.header_items()}
        self.assertEqual(headers["accept-encoding"], "identity")
        self.assertNotIn("authorization", headers)
        self.assertNotIn("cookie", headers)
        self.assertNotIn(b"variables", request.data)

    def test_fixed_chunked_and_close_delimited_profiles_are_accepted(self) -> None:
        profiles = []
        responses = [
            public.FixtureResponse(self.payload),
            public.FixtureResponse(
                self.payload,
                content_length=None,
                transfer_encoding="chunked",
            ),
            public.FixtureResponse(self.payload),
        ]
        del responses[2].headers["Content-Length"]
        for response in responses:
            counters = public._base_access_counters()
            body, evidence = public.perform_locked_transport(
                public._fixture_opener(response),
                counters=counters,
                public_request=False,
            )
            self.assertEqual(body, self.payload)
            self.assertEqual(response.read_calls, 1)
            self.assertEqual(response.close_calls, 1)
            self.assertEqual(counters["mock_transport_calls"], 1)
            self.assertEqual(counters["public_GraphQL_requests"], 0)
            profiles.append(evidence.framing_profile)
        self.assertEqual(profiles, ["fixed_length", "chunked", "close_delimited"])

    def test_all_wrapper_transport_and_resource_mutations_refuse(self) -> None:
        mutations = public._run_mock_transport_mutations(self.payload)
        self.assertEqual(len(mutations), 20)
        self.assertTrue(all(value in public.REFUSAL_IDS for value in mutations.values()))

    def test_machine_gate_reports_normalized_load_before_consumption(self) -> None:
        result = public.preconsumption_machine_gate(
            ROOT,
            **self.safe_machine_kwargs(),
        )
        self.assertTrue(result["passed_before_consumed_marker"])
        self.assertEqual(result["one_minute_load_per_logical_CPU"], 0.5)
        self.assertEqual(result["CPU_threads"], 1)

    def test_generated_mock_qualification_is_bounded_and_target_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((10.0, 10.5))
            outcome = public.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            report = outcome.report
            self.assertEqual(report["route"], "IACKDMP-R0")
            self.assertEqual(report["tree_summary"]["file_count"], 1679)
            self.assertEqual(report["selected_summary"]["object_count"], 1340)
            self.assertEqual(report["measurements"]["deterministic_replays"], 2)
            self.assertEqual(report["measurements"]["mock_refusal_mutations_passed"], 20)
            self.assertLess(outcome.combined_output_bytes, 1024 * 1024)
            self.assertEqual(report["access_counters"]["mock_transport_calls"], 1)
            self.assertEqual(report["access_counters"]["public_GraphQL_requests"], 0)
            self.assertEqual(report["access_counters"]["S3_payload_requests"], 0)
            self.assertEqual(report["access_counters"]["target_label_or_trial_reads"], 0)
            self.assertEqual(report["access_counters"]["model_inference_runs"], 0)
            self.assertTrue(outcome.private_manifest_path.is_file())
            self.assertTrue(outcome.report_path.is_file())
            public.validate_public_result(report)

    def test_generated_replay_preserves_all_identity_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            outcomes = []
            for ordinal in range(2):
                ticks = iter((1.0, 1.25))
                outcomes.append(
                    public.qualify_generated_mock_wrapper(
                        Path(directory) / f"q{ordinal}",
                        repo_root=ROOT,
                        clock=lambda ticks=ticks: next(ticks),
                        **self.safe_machine_kwargs(),
                    )
                )
            for key in (
                "snapshot_anchor",
                "tree_summary",
                "selected_summary",
                "critical_metadata",
            ):
                self.assertEqual(outcomes[0].report[key], outcomes[1].report[key])

    def test_generated_output_collision_refuses_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "qualification"
            ticks = iter((1.0, 1.1))
            public.qualify_generated_mock_wrapper(
                output,
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            with self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F02"):
                public.qualify_generated_mock_wrapper(
                    output,
                    repo_root=ROOT,
                    **self.safe_machine_kwargs(),
                )

    def test_public_result_rejects_private_rows_and_nonzero_forbidden_counters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((1.0, 1.1))
            outcome = public.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            leaked = copy.deepcopy(outcome.report)
            leaked["tree_summary"]["filename"] = "sub-01/eeg/private"
            with self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F06"):
                public.validate_public_result(leaked)
            counted = copy.deepcopy(outcome.report)
            counted["access_counters"]["S3_payload_requests"] = 1
            with self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F06"):
                public.validate_public_result(counted)

    def test_aggregate_inspector_refuses_private_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            ticks = iter((1.0, 1.1))
            outcome = public.qualify_generated_mock_wrapper(
                Path(directory) / "qualification",
                repo_root=ROOT,
                clock=lambda: next(ticks),
                **self.safe_machine_kwargs(),
            )
            inspected = public.inspect_public_result(outcome.report_path)
            self.assertEqual(inspected["route"], "IACKDMP-R0")
            with self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F06"):
                public.inspect_public_result(outcome.private_manifest_path)

    def test_plan_and_default_CLI_are_network_free(self) -> None:
        with mock.patch.object(
            public.urllib.request,
            "build_opener",
            side_effect=AssertionError("network"),
        ):
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(public.main([]), 0)
            self.assertIn("public snapshot metadata", stdout.getvalue().casefold())
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(public.main(["plan"]), 0)
            plan = json.loads(stdout.getvalue())
            self.assertEqual(plan["GraphQL_requests_made"], 0)
            self.assertEqual(plan["S3_payload_requests"], 0)

    def test_malformed_green_evidence_refuses_before_network(self) -> None:
        evidence = public.GreenWrapperEvidence(
            implementation_commit="bad",
            implementation_ci_run_id=1,
            implementation_base_job_id=2,
            implementation_optional_job_id=3,
            implementation_registry_sha256="b" * 64,
        )
        with mock.patch.object(
            public.urllib.request,
            "build_opener",
            side_effect=AssertionError("network"),
        ), self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F00"):
            public.execute_registered_public_audit(ROOT, evidence=evidence)

    def test_machine_failure_precedes_marker_and_opener(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            opener = mock.Mock()
            with (
                mock.patch.object(
                    public,
                    "verify_green_wrapper_evidence",
                    return_value={"execution_state": {"public_execution_consumed": False}},
                ),
                mock.patch.object(
                    public.identity,
                    "load_registered_contract",
                    return_value=self.contract,
                ),
                self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F01"),
            ):
                public.execute_registered_public_audit(
                    root,
                    evidence=self.evidence(),
                    environ=THREAD_ENV,
                    opener=opener,
                    disk_usage_reader=lambda _path: SimpleNamespace(
                        free=public.MINIMUM_FREE_DISK_BYTES - 1
                    ),
                    cpu_count_reader=lambda: 8,
                    loadavg_reader=lambda: (0.0, 0.0, 0.0),
                    rss_reader=lambda: 1,
                )
            opener.assert_not_called()
            self.assertFalse((root / public.REAL_ROOT_RELATIVE_PATH).exists())
            self.assertFalse((root / public.REAL_PUBLIC_RESULT_RELATIVE_PATH).exists())

    def test_mocked_real_path_writes_marker_before_one_request_and_aggregate_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            response = public.FixtureResponse(self.payload)
            marker_seen = []

            def opener(request, timeout):
                marker_seen.append(
                    (root / public.REAL_ROOT_RELATIVE_PATH / public.REAL_CONSUMED_NAME).is_file()
                )
                self.assertEqual(request.data, public.REQUEST_BODY)
                self.assertEqual(timeout, 20.0)
                return response

            ticks = iter((2.0, 2.5))
            with (
                mock.patch.object(
                    public,
                    "verify_green_wrapper_evidence",
                    return_value={"execution_state": {"public_execution_consumed": False}},
                ),
                mock.patch.object(
                    public.identity,
                    "load_registered_contract",
                    return_value=self.contract,
                ),
            ):
                outcome = public.execute_registered_public_audit(
                    root,
                    evidence=self.evidence(),
                    opener=opener,
                    clock=lambda: next(ticks),
                    **self.safe_machine_kwargs(),
                )
            self.assertEqual(marker_seen, [True])
            self.assertEqual(response.read_calls, 1)
            self.assertEqual(outcome.report["route"], "IACKDM-R1")
            self.assertEqual(outcome.report["access_counters"]["public_GraphQL_requests"], 1)
            self.assertEqual(outcome.report["access_counters"]["S3_payload_requests"], 0)
            self.assertEqual(outcome.report["access_counters"]["target_label_or_trial_reads"], 0)
            self.assertTrue(outcome.private_manifest_path.is_file())
            self.assertTrue(outcome.report_path.is_file())
            mode = stat.S_IMODE(outcome.private_manifest_path.stat().st_mode)
            self.assertEqual(mode, 0o600)
            public.validate_public_result(outcome.report)

    def test_semantic_failure_is_consumed_reported_and_not_rerunnable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".codex_work").mkdir()
            (root / "registries").mkdir()
            bad_body = b'{"errors":[]}\n'
            opener = mock.Mock(return_value=public.FixtureResponse(bad_body))
            ticks = iter((1.0, 1.1))
            patches = (
                mock.patch.object(
                    public,
                    "verify_green_wrapper_evidence",
                    return_value={"execution_state": {"public_execution_consumed": False}},
                ),
                mock.patch.object(
                    public.identity,
                    "load_registered_contract",
                    return_value=self.contract,
                ),
            )
            with patches[0], patches[1], self.assertRaisesRegex(
                public.PublicSnapshotRefusal, "IACKDMP-F05"
            ):
                public.execute_registered_public_audit(
                    root,
                    evidence=self.evidence(),
                    opener=opener,
                    clock=lambda: next(ticks),
                    **self.safe_machine_kwargs(),
                )
            report_path = root / public.REAL_PUBLIC_RESULT_RELATIVE_PATH
            report = public.inspect_public_result(report_path)
            self.assertEqual(report["status"], "public_snapshot_audit_consumed_and_parked")
            self.assertEqual(report["route"], public.REFUSAL_IDS[5])
            self.assertTrue(
                (root / public.REAL_ROOT_RELATIVE_PATH / public.REAL_CONSUMED_NAME).is_file()
            )
            self.assertFalse(
                (root / public.REAL_ROOT_RELATIVE_PATH / public.REAL_PRIVATE_MANIFEST_NAME).exists()
            )
            second_opener = mock.Mock()
            with (
                mock.patch.object(
                    public,
                    "verify_green_wrapper_evidence",
                    return_value={"execution_state": {"public_execution_consumed": False}},
                ),
                mock.patch.object(
                    public.identity,
                    "load_registered_contract",
                    return_value=self.contract,
                ),
                self.assertRaisesRegex(public.PublicSnapshotRefusal, "IACKDMP-F02"),
            ):
                public.execute_registered_public_audit(
                    root,
                    evidence=self.evidence(),
                    opener=second_opener,
                    **self.safe_machine_kwargs(),
                )
            second_opener.assert_not_called()

    def test_module_has_no_heavy_dependency_or_consumed_executor_interface(self) -> None:
        source = Path(public.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import sklearn",
            "import torch",
            "iackd_role_aware_dual_reversal_real",
            ".codex_work/iackd_role_aware_dual_reversal",
            ".codex_work/iackd_transport_stable_dual_reversal",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
