from __future__ import annotations

import ast
import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit import eegmmidb_ug1_source_acquisition_cli as source_cli
from neurodecodekit.datasets import eegmmidb_unseen_participant_source_acquisition as source


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in source.THREAD_ENV_KEYS}


class EEGMMIDBUnseenParticipantSourceAcquisitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="ndk-ug1-sa1-")
        self.workspace = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_pass(self, *, name: str = "pass", exchanges=None, **kwargs):
        opener = source.FixtureGetOpener(
            source.build_generated_exchanges(ROOT) if exchanges is None else exchanges
        )
        outcome = source.run_source_acquisition(
            repo_root=ROOT,
            opener=opener,
            generated=True,
            workspace_root=self.workspace,
            layout=source._generated_layout(name),
            environ=kwargs.pop("environ", THREAD_ENV),
            clock=kwargs.pop("clock", lambda: 10.0),
            rss_reader=kwargs.pop("rss_reader", lambda: 32 * 1024 * 1024),
            **kwargs,
        )
        return outcome, opener

    def test_green_decision_and_locked_source_scope_are_exact(self) -> None:
        decision, request, inventory = source._load_locked_scope(ROOT)
        self.assertEqual(source.GREEN_DECISION_COMMIT, "1b5c9195f384e5867f18131aa7d669f7c9cd0e2b")
        self.assertEqual(source.GREEN_DECISION_CI_RUN_ID, 32_725_633_524)
        self.assertEqual(source.GREEN_DECISION_BASE_JOB_ID, 97_426_157_639)
        self.assertEqual(source.GREEN_DECISION_OPTIONAL_JOB_ID, 97_426_157_381)
        self.assertEqual(decision["lane_id"], source.LANE_ID)
        self.assertEqual(request["request_id"], source.LANE_ID)
        self.assertEqual(inventory["file_count"], 36)
        self.assertEqual(len(source._source_specs(ROOT)), 6)
        self.assertEqual(
            sum(row.size_bytes for row in source._source_specs(ROOT)),
            source.EXACT_PAYLOAD_BYTES,
        )

    def test_plan_is_dry_aggregate_and_does_not_construct_live_transport(self) -> None:
        with mock.patch.object(
            source,
            "StandardLibraryGetOpener",
            side_effect=AssertionError("plan constructed live transport"),
        ):
            plan = source.registered_source_acquisition_plan(ROOT)
        self.assertEqual(plan["file_count"], 6)
        self.assertEqual(plan["payload_bytes_exact"], 15_498_816)
        self.assertNotIn("files", plan)
        self.assertTrue(all(value == 0 for value in plan["operation_counters"].values()))

    def test_generated_complete_bundle_streams_exact_bytes_and_is_opaque(self) -> None:
        exchanges = source.build_generated_exchanges(ROOT)
        outcome, opener = self.run_pass(exchanges=exchanges)
        self.assertEqual(len(opener.calls), 7)
        self.assertTrue(all(call["method"] == "GET" for call in opener.calls))
        self.assertEqual(outcome.manifest["file_count"], 6)
        self.assertEqual(outcome.manifest["payload_bytes"], 15_498_816)
        self.assertEqual(outcome.measurements["payload_body_bytes"], 15_498_816)
        self.assertEqual(outcome.measurements["opaque_post_write_passes"], 6)
        self.assertLessEqual(
            outcome.measurements["maximum_requested_stream_read_bytes"],
            1_048_576,
        )
        self.assertEqual(outcome.manifest["integrity"]["EDF_semantic_reads"], 0)
        self.assertTrue(outcome.payload_root.is_dir())
        self.assertTrue(outcome.marker_path.is_file())
        self.assertEqual(
            len(tuple(outcome.payload_root.glob("S*/S*R*.edf"))),
            6,
        )
        public = outcome.receipt_bytes.decode("ascii").lower()
        for forbidden in ("s001", ".edf", "physionet.org", "sha256", "etag"):
            self.assertNotIn(forbidden, public)

    def test_generated_replay_is_byte_exact(self) -> None:
        first, _ = self.run_pass(name="first")
        second, _ = self.run_pass(name="second")
        self.assertEqual(first.manifest_bytes, second.manifest_bytes)
        self.assertEqual(first.receipt_bytes, second.receipt_bytes)

    def test_checksum_parser_refuses_missing_duplicate_alias_uppercase_and_non_ascii(self) -> None:
        specs = source._source_specs(ROOT)
        exchanges = source.build_generated_exchanges(ROOT)
        payload = exchanges[0].response._payload
        self.assertIsNotNone(payload)
        assert payload is not None
        parsed = source.parse_checksum_manifest(payload, specs)
        self.assertEqual(tuple(parsed), tuple(row.repository_path for row in specs))
        lines = payload.decode("ascii").splitlines()
        bad = (
            ("\n".join(lines[:-1]) + "\n").encode("ascii"),
            ("\n".join([*lines, lines[0]]) + "\n").encode("ascii"),
            (lines[0].replace("  ", "  ./", 1) + "\n" + "\n".join(lines[1:]) + "\n").encode("ascii"),
            (lines[0].upper() + "\n" + "\n".join(lines[1:]) + "\n").encode("ascii"),
            b"\xff\n",
        )
        for value in bad:
            with self.subTest(value=value[:20]), self.assertRaises(source.UG1SourceAcquisitionRefusal):
                source.parse_checksum_manifest(value, specs)

    def test_response_identity_and_body_failures_leave_marker_but_no_temporary_payload(self) -> None:
        cases = {}
        redirect = list(source.build_generated_exchanges(ROOT))
        first = redirect[1]
        redirect[1] = source.FixtureExchange(
            first.url,
            source.FixtureGetResponse(
                url=f"{first.url}.redirect",
                headers=tuple(first.response.headers.raw_items()),
                spec=first.response._spec,
                spec_index=first.response._spec_index,
            ),
            first.expected_headers,
        )
        cases["redirect"] = redirect
        compressed = list(source.build_generated_exchanges(ROOT))
        compressed[1] = source._replace_header(compressed[1], "Content-Encoding", "identity")
        cases["compressed"] = compressed
        short = list(source.build_generated_exchanges(ROOT))
        first = short[1]
        short[1] = source.FixtureExchange(
            first.url,
            source.FixtureGetResponse(
                url=first.url,
                headers=tuple(first.response.headers.raw_items()),
                spec=first.response._spec,
                spec_index=first.response._spec_index,
                body_size=first.response._body_size - 1,
            ),
            first.expected_headers,
        )
        cases["short"] = short
        for name, exchanges in cases.items():
            layout = source._generated_layout(name)
            opener = source.FixtureGetOpener(exchanges)
            with self.subTest(name=name), self.assertRaises(source.UG1SourceAcquisitionRefusal):
                source.run_source_acquisition(
                    repo_root=ROOT,
                    opener=opener,
                    generated=True,
                    workspace_root=self.workspace,
                    layout=layout,
                    environ=THREAD_ENV,
                    clock=lambda: 10.0,
                    rss_reader=lambda: 32 * 1024 * 1024,
                )
            self.assertTrue((self.workspace / layout.marker_relative).is_file())
            self.assertFalse((self.workspace / layout.temporary_relative).exists())
            self.assertFalse((self.workspace / layout.payload_relative).exists())

    def test_collision_second_invocation_and_resource_caps_refuse_before_extra_calls(self) -> None:
        collision = self.workspace / "collision"
        collision.mkdir()
        (collision / "bundle").write_bytes(b"existing")
        opener = source.FixtureGetOpener(source.build_generated_exchanges(ROOT))
        with self.assertRaises(source.UG1SourceAcquisitionRefusal):
            source.run_source_acquisition(
                repo_root=ROOT,
                opener=opener,
                generated=True,
                workspace_root=self.workspace,
                layout=source._generated_layout("collision"),
                environ=THREAD_ENV,
                clock=lambda: 10.0,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
        self.assertEqual(opener.calls, [])
        self.assertEqual((collision / "bundle").read_bytes(), b"existing")

        self.run_pass(name="consumed")
        second = source.FixtureGetOpener(source.build_generated_exchanges(ROOT))
        with self.assertRaises(source.UG1SourceAcquisitionRefusal):
            source.run_source_acquisition(
                repo_root=ROOT,
                opener=second,
                generated=True,
                workspace_root=self.workspace,
                layout=source._generated_layout("consumed"),
                environ=THREAD_ENV,
                clock=lambda: 10.0,
                rss_reader=lambda: 32 * 1024 * 1024,
            )
        self.assertEqual(second.calls, [])

        for kwargs in (
            {"environ": {**THREAD_ENV, source.THREAD_ENV_KEYS[0]: "2"}},
            {"rss_reader": lambda: source.MAX_PEAK_RSS_BYTES + 1},
            {"disk_usage_reader": lambda _path: type("Disk", (), {"free": 0})()},
            {"clock": iter((0.0, source.MAX_WALL_SECONDS + 1)).__next__},
        ):
            guarded = source.FixtureGetOpener(source.build_generated_exchanges(ROOT))
            values = {
                "repo_root": ROOT,
                "opener": guarded,
                "generated": True,
                "workspace_root": self.workspace,
                "layout": source._generated_layout(f"cap-{len(guarded.calls)}-{id(guarded)}"),
                "environ": THREAD_ENV,
                "clock": lambda: 10.0,
                "rss_reader": lambda: 32 * 1024 * 1024,
            }
            values.update(kwargs)
            with self.assertRaises(source.UG1SourceAcquisitionRefusal):
                source.run_source_acquisition(**values)
            self.assertEqual(guarded.calls, [])

    def test_live_entry_refuses_without_exact_proof_before_transport_construction(self) -> None:
        evidence = source.SA1ProofEvidence(
            implementation_commit="0" * 40,
            implementation_ci_run_id=1,
            implementation_base_job_id=1,
            implementation_optional_job_id=1,
            proof_closeout_commit="0" * 40,
            proof_closeout_ci_run_id=1,
            proof_closeout_base_job_id=1,
            proof_closeout_optional_job_id=1,
            proof_closeout_registry_sha256="0" * 64,
        )
        with (
            mock.patch.object(
                source,
                "StandardLibraryGetOpener",
                side_effect=AssertionError("live transport constructed before proof"),
            ),
            self.assertRaises(source.UG1SourceAcquisitionRefusal),
        ):
            source.execute_registered_source_acquisition(
                ROOT,
                evidence=evidence,
                environ=THREAD_ENV,
            )

    def test_cli_exposes_only_plan_and_qualify(self) -> None:
        parser = source_cli.build_parser()
        help_text = parser.format_help()
        self.assertIn("plan", help_text)
        self.assertIn("qualify", help_text)
        self.assertNotIn("execute", help_text)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(source_cli.main(["plan"]), 0)
        self.assertIn('"file_count": 6', stdout.getvalue())
        self.assertIn("no network", stdout.getvalue().lower())

    def test_summary_is_canonical_bounded_and_no_clobber(self) -> None:
        summary = {
            "schema_name": "neurodecodekit.eegmmidb_ug1_source_acquisition_stage_sa1_result",
            "route": source.GENERATED_ROUTE,
        }
        destination = self.workspace / "summary.json"
        size, digest = source.write_generated_summary(destination, summary)
        self.assertEqual(size, destination.stat().st_size)
        self.assertEqual(digest, hashlib.sha256(destination.read_bytes()).hexdigest())
        with self.assertRaises(Exception):
            source.write_generated_summary(destination, summary)

    def test_module_has_no_heavy_reader_model_or_subprocess_surface(self) -> None:
        module_source = Path(source.__file__).read_text(encoding="utf-8")
        imports: set[str] = set()
        for node in ast.walk(ast.parse(module_source)):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertTrue(imports.isdisjoint({"mne", "numpy", "scipy", "sklearn", "torch"}))
        self.assertNotIn("read_raw_edf", module_source)
        self.assertNotIn("subprocess", imports)
        self.assertNotIn("add_parser(\"execute\"", Path(source_cli.__file__).read_text())


if __name__ == "__main__":
    unittest.main()
