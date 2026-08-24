from __future__ import annotations

import ast
import contextlib
import copy
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import eegmmidb_unseen_participant_metadata as metadata
from neurodecodekit import eegmmidb_ug1_metadata_cli


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in metadata.THREAD_ENV_KEYS}


class EEGMMIDBUnseenParticipantMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ndk-ug1-metadata-")
        self.workspace = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_pass(self, exchanges=None, **kwargs):
        opener = metadata.FixtureHeadOpener(
            metadata.build_generated_exchanges() if exchanges is None else exchanges
        )
        outcome = metadata.run_metadata_pass(
            repo_root=ROOT,
            opener=opener,
            generated=True,
            environ=kwargs.pop("environ", THREAD_ENV),
            clock=kwargs.pop("clock", lambda: 10.0),
            rss_reader=kwargs.pop("rss_reader", lambda: 32 * 1024 * 1024),
            **kwargs,
        )
        return outcome, opener

    def test_green_decision_is_exact_and_stage_m1_only(self) -> None:
        decision = metadata._read_locked_decision(ROOT)
        payload = (ROOT / metadata.DECISION_RELATIVE_PATH).read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), metadata.DECISION_SHA256)
        self.assertEqual(metadata.GREEN_DECISION_COMMIT, "021bf8a1f2f12a8e7388a561535328cd0dc0dba2")
        self.assertEqual(metadata.GREEN_DECISION_CI_RUN_ID, 32_712_235_191)
        self.assertEqual(metadata.GREEN_DECISION_BASE_JOB_ID, 97_385_926_125)
        self.assertEqual(metadata.GREEN_DECISION_OPTIONAL_JOB_ID, 97_385_926_444)
        authorization = decision["authorization"]
        self.assertTrue(
            authorization[
                "stage_M1_generated_metadata_client_implementation_after_decision_green"
            ]
        )
        self.assertFalse(authorization["network_or_metadata_request_authorized_now"])

    def test_plan_is_exact_and_performs_no_transport_or_data_operation(self) -> None:
        with mock.patch.object(
            metadata,
            "StandardLibraryHeadOpener",
            side_effect=AssertionError("plan constructed live transport"),
        ):
            plan = metadata.registered_metadata_plan(ROOT)
        self.assertEqual(plan["file_count"], 36)
        self.assertEqual(plan["files"][0]["repository_path"], "S001/S001R04.edf")
        self.assertEqual(plan["files"][-1]["repository_path"], "S030/S030R12.edf")
        self.assertEqual(plan["method"], "HEAD")
        self.assertTrue(all(value == 0 for value in plan["operation_counters"].values()))

    def test_complete_mock_pass_is_head_only_body_blind_and_bounded(self) -> None:
        exchanges = metadata.build_generated_exchanges()
        outcome, opener = self.run_pass(exchanges)
        self.assertEqual(len(opener.calls), 36)
        self.assertTrue(all(call["method"] == "HEAD" for call in opener.calls))
        self.assertTrue(all(call["data"] is None for call in opener.calls))
        self.assertTrue(all(row.response.read_calls == 0 for row in exchanges))
        self.assertEqual(outcome.inventory["file_count"], 36)
        self.assertEqual(outcome.inventory["source_file_count"], 6)
        self.assertEqual(outcome.inventory["fresh_file_count"], 30)
        self.assertLess(len(outcome.inventory_bytes) + len(outcome.receipt_bytes), 1 << 20)
        self.assertEqual(outcome.measurements["mock_HEAD_requests"], 36)
        self.assertEqual(outcome.measurements["real_HEAD_requests"], 0)
        self.assertEqual(outcome.measurements["response_body_bytes"], 0)
        self.assertEqual(outcome.measurements["EDF_content_reads"], 0)
        self.assertEqual(outcome.measurements["model_runs"], 0)
        self.assertFalse(outcome.measurements["end_to_end_latency_measured"])

    def test_optional_validator_absence_is_explicit_not_inferred(self) -> None:
        outcome, _ = self.run_pass(
            metadata.build_generated_exchanges(optional_validators=False)
        )
        self.assertEqual(
            outcome.inventory["validator_availability"],
            {"etag": 0, "last_modified": 0, "accept_ranges": 0},
        )
        self.assertEqual(
            outcome.inventory["unavailable_fields"],
            ["etag", "last_modified", "accept_ranges"],
        )
        self.assertTrue(
            all(row["etag"] is None for row in outcome.inventory["files"])
        )

    def test_replay_is_byte_exact_and_source_responses_are_immutable(self) -> None:
        first_source = metadata.build_generated_exchanges()
        fingerprint = [
            (row.url, row.response.status, tuple(row.response.headers.raw_items()))
            for row in first_source
        ]
        first, _ = self.run_pass(copy.deepcopy(first_source))
        second, _ = self.run_pass(metadata.build_generated_exchanges())
        self.assertEqual(first.inventory_bytes, second.inventory_bytes)
        self.assertEqual(first.receipt_bytes, second.receipt_bytes)
        self.assertEqual(
            fingerprint,
            [
                (row.url, row.response.status, tuple(row.response.headers.raw_items()))
                for row in first_source
            ],
        )

    def test_redirect_status_framing_validator_and_body_mutations_refuse(self) -> None:
        cases = (
            "redirect",
            "status",
            "missing_content_length",
            "duplicate_content_length",
            "malformed_content_length",
            "malformed_etag",
            "malformed_last_modified",
            "malformed_accept_ranges",
            "observed_body_byte",
            "declared_byte_cap",
        )
        for case in cases:
            opener = metadata.FixtureHeadOpener(metadata._mutated_exchanges(case))
            with self.subTest(case=case), self.assertRaises(metadata.UG1MetadataRefusal):
                metadata.run_metadata_pass(
                    repo_root=ROOT,
                    opener=opener,
                    generated=True,
                    environ=THREAD_ENV,
                    clock=lambda: 10.0,
                    rss_reader=lambda: 32 * 1024 * 1024,
                )
            self.assertLessEqual(len(opener.calls), 36)

    def test_order_missing_response_and_nonallowlisted_url_refuse(self) -> None:
        reversed_first = list(metadata.build_generated_exchanges())
        reversed_first[0], reversed_first[1] = reversed_first[1], reversed_first[0]
        cases = (reversed_first, metadata.build_generated_exchanges()[:-1])
        for index, exchanges in enumerate(cases):
            opener = metadata.FixtureHeadOpener(exchanges)
            with self.subTest(index=index), self.assertRaises(metadata.UG1MetadataRefusal):
                metadata.run_metadata_pass(
                    repo_root=ROOT,
                    opener=opener,
                    generated=True,
                    environ=THREAD_ENV,
                    clock=lambda: 10.0,
                    rss_reader=lambda: 32 * 1024 * 1024,
                )
        for url in (
            "http://physionet.org/files/eegmmidb/1.0.0/S001/S001R04.edf",
            "https://example.org/files/eegmmidb/1.0.0/S001/S001R04.edf",
            "https://physionet.org/files/eegmmidb/1.0.0/S001/S001R04.edf?x=1",
        ):
            with self.subTest(url=url), self.assertRaises(metadata.UG1MetadataRefusal):
                metadata._request(url)

    def test_target_like_output_field_is_refused_and_unknown_headers_are_not_recorded(self) -> None:
        with self.assertRaisesRegex(metadata.UG1MetadataRefusal, "target-like"):
            metadata._assert_target_free({"metadata": {"target": "left"}})
        exchanges = list(metadata.build_generated_exchanges())
        first = exchanges[0]
        headers = [*first.response.headers.raw_items(), ("X-Target", "left")]
        exchanges[0] = metadata.FixtureExchange(
            first.url,
            metadata.FixtureHeadResponse(url=first.url, headers=headers),
        )
        outcome, _ = self.run_pass(exchanges)
        serialized = outcome.inventory_bytes.decode("ascii").lower()
        self.assertNotIn("x-target", serialized)
        self.assertNotIn('"target"', serialized)

    def test_output_is_atomic_no_clobber_and_inspectable(self) -> None:
        outcome, _ = self.run_pass(
            workspace_root=self.workspace,
            output_relative="metadata",
        )
        root = self.workspace / "metadata"
        self.assertEqual(root, outcome.output_root)
        self.assertEqual((root / "inventory.v0.json").read_bytes(), outcome.inventory_bytes)
        self.assertEqual((root / "receipt.md").read_bytes(), outcome.receipt_bytes)
        with self.assertRaisesRegex(metadata.UG1MetadataRefusal, "already exists"):
            self.run_pass(workspace_root=self.workspace, output_relative="metadata")
        self.assertFalse((self.workspace / ".metadata.tmp").exists())

    def test_thread_disk_rss_wall_and_output_caps_refuse(self) -> None:
        environments = {**THREAD_ENV, metadata.THREAD_ENV_KEYS[0]: "2"}
        cases = (
            {"environ": environments},
            {
                "workspace_root": self.workspace,
                "output_relative": "disk",
                "disk_usage_reader": lambda _path: type("Disk", (), {"free": 0})(),
            },
            {"rss_reader": lambda: metadata.MAX_PEAK_RSS_BYTES + 1},
            {"clock": iter((0.0, metadata.MAX_WALL_SECONDS + 1)).__next__},
            {"caps": metadata.MetadataCaps(output_bytes=1)},
        )
        for index, kwargs in enumerate(cases):
            opener = metadata.FixtureHeadOpener(metadata.build_generated_exchanges())
            values = {
                "repo_root": ROOT,
                "opener": opener,
                "generated": True,
                "environ": THREAD_ENV,
                "clock": lambda: 10.0,
                "rss_reader": lambda: 32 * 1024 * 1024,
            }
            values.update(kwargs)
            with self.subTest(index=index), self.assertRaises(metadata.UG1MetadataRefusal):
                metadata.run_metadata_pass(**values)

    def test_standard_library_transport_is_tls_verified_and_no_redirect(self) -> None:
        fake_context = object()
        fake_opener = mock.Mock()
        with (
            mock.patch.object(metadata.ssl, "create_default_context", return_value=fake_context),
            mock.patch.object(
                metadata.urllib.request,
                "HTTPSHandler",
                return_value="https-handler",
            ) as https_handler,
            mock.patch.object(
                metadata.urllib.request,
                "build_opener",
                return_value=fake_opener,
            ) as build_opener,
        ):
            live = metadata.StandardLibraryHeadOpener()
        https_handler.assert_called_once_with(context=fake_context)
        self.assertIsInstance(build_opener.call_args.args[0], metadata._NoRedirect)
        request = metadata._request(metadata.acquisition.EXPECTED_FILES[0].url)
        live(request, metadata.REQUEST_TIMEOUT_SECONDS)
        fake_opener.open.assert_called_once_with(
            request, timeout=metadata.REQUEST_TIMEOUT_SECONDS
        )

    def test_summary_publication_is_bounded_and_no_clobber(self) -> None:
        summary = {
            "schema_name": "neurodecodekit.eegmmidb_ug1_metadata_stage_m1_result",
            "route": metadata.GENERATED_ROUTE,
        }
        destination = self.workspace / "summary.json"
        size, digest = metadata.write_generated_summary(destination, summary)
        self.assertEqual(size, destination.stat().st_size)
        self.assertEqual(digest, hashlib.sha256(destination.read_bytes()).hexdigest())
        with self.assertRaises(Exception):
            metadata.write_generated_summary(destination, summary)

    def test_cli_exposes_only_plan_and_generated_qualification_for_stage_m(self) -> None:
        parser = eegmmidb_ug1_metadata_cli.build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertNotIn("execute", help_text)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(eegmmidb_ug1_metadata_cli.main(["plan"]), 0)
        plan = stdout.getvalue()
        self.assertIn('"method": "HEAD"', plan)
        self.assertIn("no network", plan.lower())

    def test_module_has_no_heavy_reader_model_or_subprocess_surface(self) -> None:
        source = Path(metadata.__file__).read_text(encoding="utf-8")
        imports: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertTrue(imports.isdisjoint({"mne", "numpy", "scipy", "sklearn", "torch"}))
        self.assertNotIn("read_raw_edf", source)
        self.assertNotIn("subprocess", imports)
        self.assertNotIn("metadata-execute", source)

    def test_fixture_response_body_is_never_read_even_when_closed(self) -> None:
        exchanges = metadata.build_generated_exchanges()
        self.run_pass(exchanges)
        self.assertTrue(all(row.response.closed for row in exchanges))
        self.assertTrue(all(row.response.read_calls == 0 for row in exchanges))


if __name__ == "__main__":
    unittest.main()
