import ast
import copy
import dataclasses
import hashlib
import os
import tempfile
import unittest
from pathlib import Path

from neurodecodekit.datasets import eegmmidb_unseen_participant_acquisition as acquisition


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}


class EEGMMIDBUnseenParticipantAcquisitionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="ndk-ug1-generated-")
        self.root = Path(self.temporary.name)
        self.inventory, self.transport = acquisition.build_generated_fixture()

    def tearDown(self):
        self.temporary.cleanup()

    def run_fixture(self, **kwargs):
        return acquisition.run_generated_fixture_acquisition(
            inventory=kwargs.pop("inventory", self.inventory),
            transport=kwargs.pop("transport", self.transport),
            workspace_root=kwargs.pop("workspace_root", self.root),
            execute=kwargs.pop("execute", True),
            environ=kwargs.pop("environ", THREAD_ENV),
            clock=kwargs.pop("clock", lambda: 10.0),
            rss_reader=kwargs.pop("rss_reader", lambda: 32 * 1024 * 1024),
            **kwargs,
        )

    def test_registered_plan_is_exact_target_free_and_dry(self):
        before = set(self.root.iterdir())
        plan = acquisition.registered_plan(ROOT)
        self.assertEqual(plan["mode"], "dry_run_no_output_path_stat_no_transport_call")
        self.assertEqual(plan["file_count"], 36)
        self.assertEqual(plan["source_file_count"], 6)
        self.assertEqual(plan["fresh_file_count"], 30)
        self.assertEqual(plan["files"][0]["repository_path"], "S001/S001R04.edf")
        self.assertEqual(plan["files"][-1]["repository_path"], "S030/S030R12.edf")
        self.assertFalse(plan["sizes_known"])
        self.assertEqual(plan["operation_counters"]["network_bytes"], 0)
        self.assertEqual(plan["operation_counters"]["target_deliveries"], 0)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_default_run_is_dry_and_never_calls_transport_or_touches_root(self):
        before = set(self.root.iterdir())
        outcome = acquisition.run_generated_fixture_acquisition(
            inventory=self.inventory,
        )
        self.assertEqual(outcome.status, "dry_run")
        self.assertEqual(self.transport.calls, [])
        self.assertIsNone(outcome.payload_root)
        self.assertEqual(outcome.measurements["output_bytes"], 0)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_generated_roundtrip_is_exact_bounded_and_opaque(self):
        source_fingerprints = self.transport.fixture_sha256s()
        outcome = self.run_fixture()
        self.assertEqual(outcome.status, "passed")
        self.assertEqual(len(self.transport.calls), 36)
        self.assertEqual(outcome.measurements["input_bytes"], 36 * 256)
        self.assertEqual(
            outcome.measurements["output_bytes"],
            36 * 256 + len(outcome.manifest_bytes),
        )
        self.assertEqual(
            outcome.measurements["cumulative_output_bytes"],
            2 * outcome.measurements["output_bytes"],
        )
        self.assertEqual(outcome.measurements["network_bytes"], 0)
        self.assertEqual(outcome.measurements["real_path_reads"], 0)
        self.assertEqual(outcome.measurements["parameter_update_fits"], 0)
        self.assertEqual(outcome.measurements["prediction_sets"], 0)
        self.assertEqual(outcome.measurements["target_deliveries"], 0)
        self.assertEqual(outcome.measurements["scoring_events"], 0)
        self.assertEqual(outcome.manifest_path.read_bytes(), outcome.manifest_bytes)
        self.assertEqual(self.transport.fixture_sha256s(), source_fingerprints)
        for record in self.inventory:
            payload_path = outcome.payload_root / record.repository_path
            self.assertEqual(payload_path.stat().st_size, record.size_bytes)
            self.assertEqual(hashlib.sha256(payload_path.read_bytes()).hexdigest(), record.sha256)

    def test_manifest_and_replay_are_deterministic_across_isolated_roots(self):
        first = self.run_fixture(output_relative="first")
        second_root = Path(tempfile.mkdtemp(prefix="ndk-ug1-generated-replay-"))
        self.addCleanup(
            lambda: os.path.isdir(second_root) and __import__("shutil").rmtree(second_root)
        )
        inventory, transport = acquisition.build_generated_fixture()
        second = self.run_fixture(
            inventory=inventory,
            transport=transport,
            workspace_root=second_root,
            output_relative="second",
        )
        self.assertEqual(first.manifest_bytes, second.manifest_bytes)
        self.assertEqual(first.manifest_sha256, second.manifest_sha256)
        self.assertEqual(self.inventory, inventory)

    def test_manifest_validator_refuses_protected_or_mutated_fields(self):
        outcome = self.run_fixture(output_relative="canonical")
        mutated = copy.deepcopy(outcome.manifest)
        mutated["files"][0]["label"] = "T1"
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "protected field"):
            acquisition.validate_generated_manifest(mutated, self.inventory)
        mutated = copy.deepcopy(outcome.manifest)
        mutated["payload_bytes"] += 1
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "canonical inventory"):
            acquisition.validate_generated_manifest(mutated, self.inventory)

    def test_inventory_canonicalizes_order_and_refuses_identity_drift(self):
        reversed_inventory = tuple(reversed(self.inventory))
        ordered = acquisition.validate_inventory(reversed_inventory)
        self.assertEqual([row.repository_path for row in ordered], list(acquisition.EXPECTED_PATHS))

        duplicate = list(self.inventory)
        duplicate[-1] = duplicate[0]
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "duplicate"):
            acquisition.validate_inventory(duplicate)

        forbidden_run = list(self.inventory)
        forbidden_run[0] = dataclasses.replace(
            forbidden_run[0],
            repository_path="S001/S001R11.edf",
            run="11",
        )
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "paths differ"):
            acquisition.validate_inventory(forbidden_run)

        traversal = list(self.inventory)
        traversal[0] = dataclasses.replace(traversal[0], repository_path="../fixture.edf")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "unsafe relative"):
            acquisition.validate_inventory(traversal)

    def test_inventory_refuses_size_hash_validator_and_payload_caps(self):
        malformed = list(self.inventory)
        malformed[0] = dataclasses.replace(malformed[0], size_bytes=True)
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "integer"):
            acquisition.validate_inventory(malformed)
        malformed = list(self.inventory)
        malformed[0] = dataclasses.replace(malformed[0], sha256="A" * 64)
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "lowercase"):
            acquisition.validate_inventory(malformed)
        malformed = list(self.inventory)
        malformed[0] = dataclasses.replace(malformed[0], validator="bad\nvalidator")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "generated SHA-256"):
            acquisition.validate_inventory(malformed)
        malformed = list(self.inventory)
        malformed[0] = dataclasses.replace(malformed[0], validator="T1")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "generated SHA-256"):
            acquisition.validate_inventory(malformed)
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "payload bytes exceed"):
            acquisition.validate_inventory(self.inventory, maximum_payload_bytes=1)

    def test_mock_transport_refuses_redirect_partial_oversize_status_and_nonfixture(self):
        first = acquisition.EXPECTED_FILES[0]
        record = self.inventory[0]
        valid = self.transport(first.url, record.size_bytes)
        cases = (
            dataclasses.replace(valid, final_url="https://example.invalid/redirect"),
            dataclasses.replace(valid, body=valid.body[:-1], declared_size=record.size_bytes - 1),
            dataclasses.replace(valid, body=valid.body + b"x", declared_size=record.size_bytes + 1),
            dataclasses.replace(valid, status_code=206),
            dataclasses.replace(valid, body=b"x" * record.size_bytes),
        )
        messages = ("redirect", "declared size", "declared size", "status", "sentinel")
        for index, (response, message) in enumerate(zip(cases, messages, strict=True)):
            responses = {
                planned.url: self.transport(planned.url, observed.size_bytes)
                for planned, observed in zip(
                    acquisition.EXPECTED_FILES, self.inventory, strict=True
                )
            }
            responses[first.url] = response
            transport = acquisition.GeneratedMockTransport(responses)
            with self.subTest(index=index):
                with self.assertRaisesRegex(acquisition.UG1AcquisitionFailure, message):
                    self.run_fixture(transport=transport, output_relative=f"failure-{index}")
                self.assertFalse((self.root / f"failure-{index}").exists())

    def test_hash_mismatch_and_output_caps_fail_closed(self):
        first = acquisition.EXPECTED_FILES[0]
        responses = {
            planned.url: self.transport(planned.url, observed.size_bytes)
            for planned, observed in zip(acquisition.EXPECTED_FILES, self.inventory, strict=True)
        }
        response = responses[first.url]
        changed = bytearray(response.body)
        changed[-1] ^= 1
        responses[first.url] = dataclasses.replace(response, body=bytes(changed))
        with self.assertRaisesRegex(acquisition.UG1AcquisitionFailure, "hash mismatch"):
            self.run_fixture(
                transport=acquisition.GeneratedMockTransport(responses),
                output_relative="bad-hash",
            )
        self.assertFalse((self.root / "bad-hash").exists())

        caps = acquisition.GeneratedAcquisitionCaps(cumulative_output_bytes=1)
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "output exceeds cap"):
            self.run_fixture(caps=caps, output_relative="over-cap")
        self.assertFalse((self.root / "over-cap").exists())

        disk_caps = acquisition.GeneratedAcquisitionCaps(
            minimum_free_disk_bytes=2**63,
        )
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "free disk"):
            self.run_fixture(caps=disk_caps, output_relative="disk-cap")
        self.assertFalse((self.root / "disk-cap").exists())

    def test_atomic_file_publish_refuses_a_racing_destination(self):
        destination = self.root / "atomic.json"

        def race():
            destination.write_bytes(b"race\n")

        with self.assertRaisesRegex(acquisition.UG1AcquisitionFailure, "appeared"):
            acquisition._write_atomic(destination, b"result\n", _before_publish=race)
        self.assertEqual(destination.read_bytes(), b"race\n")
        self.assertFalse((self.root / ".atomic.json.part").exists())

    def test_crash_cleans_only_owned_staging_and_never_promotes(self):
        unrelated = self.root / "unrelated.txt"
        unrelated.write_text("preserve", encoding="utf-8")

        def crash(stage):
            if stage == "after_payload_3":
                raise RuntimeError("fixture crash")

        with self.assertRaisesRegex(RuntimeError, "fixture crash"):
            self.run_fixture(output_relative="crash", fault_injector=crash)
        self.assertEqual(unrelated.read_text(encoding="utf-8"), "preserve")
        self.assertFalse((self.root / "crash").exists())
        self.assertFalse((self.root / ".crash.tmp").exists())

    def test_destination_second_invocation_symlink_and_hardlink_alias_refuse(self):
        self.run_fixture(output_relative="once")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "already exists"):
            self.run_fixture(output_relative="once")

        outside = self.root / "outside"
        outside.mkdir()
        os.symlink(outside, self.root / "linked")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "symlink"):
            self.run_fixture(output_relative="linked/result")

        source = self.root / "alias-source"
        source.write_bytes(b"fixture")
        os.link(source, self.root / ".aliased.tmp")
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "staging"):
            self.run_fixture(output_relative="aliased")
        self.assertEqual(source.read_bytes(), b"fixture")

    def test_forbidden_output_roots_thread_rss_and_wall_caps_refuse(self):
        for output in ("data/generated", ".codex_work/generated", "../escape"):
            with self.subTest(output=output):
                with self.assertRaises(acquisition.UG1AcquisitionRefusal):
                    self.run_fixture(output_relative=output)

        environment = dict(THREAD_ENV)
        environment["OMP_NUM_THREADS"] = "2"
        with self.assertRaisesRegex(acquisition.UG1AcquisitionRefusal, "one-thread"):
            self.run_fixture(environ=environment, output_relative="thread")

        with self.assertRaisesRegex(acquisition.UG1AcquisitionFailure, "RSS"):
            self.run_fixture(
                rss_reader=lambda: 2 * 1024 * 1024 * 1024,
                output_relative="rss",
            )

        values = iter((0.0, 901.0))
        with self.assertRaisesRegex(acquisition.UG1AcquisitionFailure, "wall-time"):
            self.run_fixture(clock=lambda: next(values), output_relative="wall")

    def test_module_has_no_network_or_neural_reader_capability(self):
        source = Path(acquisition.__file__).read_text(encoding="utf-8")
        imported = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".", 1)[0])
        self.assertTrue(imported.isdisjoint({"mne", "urllib", "requests", "http", "socket"}))
        self.assertNotIn("read_raw_edf", source)


if __name__ == "__main__":
    unittest.main()
