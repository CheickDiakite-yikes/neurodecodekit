import contextlib
import copy
import hashlib
import io
import json
import os
import stat
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import (
    marc2_live_domain_eligibility_adapter as domain_adapter,
)
from neurodecodekit.datasets import (
    marc2_variable_domain_private_recovery as recovery,
)

ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in recovery.THREAD_ENVIRONMENT}


class Marc2VariableDomainPrivateRecoveryGeneratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = domain_adapter.load_registered_contract(ROOT)
        cls.source = domain_adapter.build_generated_live_source(
            profile="A", contract=cls.contract
        )

    def test_decision_request_and_fixed_proof_are_exact(self):
        decision, request = recovery._validate_decision_and_request(ROOT)
        self.assertEqual(
            recovery.DECISION_COMMIT,
            "944b6e8af434c2a6820435e0f18fe9490bf44248",
        )
        self.assertEqual(decision["lane_id"], "MARC2-VR3")
        self.assertEqual(request["lane_id"], "MARC2-VR3")
        self.assertTrue(decision["green_request"]["both_required_jobs_green"])
        self.assertFalse(request["authorized"])
        self.assertTrue(all(not value for value in request["authorization_flags"].values()))

    def test_native_registry_and_certificate_use_distinct_lanes(self):
        registry = recovery._load_native_registry(ROOT)
        payload = recovery._load_certificate_bytes(ROOT)
        certificate = json.loads(payload)
        self.assertEqual(registry["lane_id"], "MARC2-VR3")
        self.assertEqual(certificate["lane_id"], "MARC2-FW1B")
        self.assertNotEqual(
            recovery.NATIVE_REGISTRY_RELATIVE_PATH,
            recovery.PROOF_CERTIFICATE_RELATIVE_PATH,
        )
        recovery._validate_certificate_generated(ROOT, payload)

    def test_all_32_wrapper_mutations_refuse_in_registered_order(self):
        observed = recovery.run_wrapper_mutation_matrix()
        self.assertEqual(tuple(observed), recovery.WRAPPER_MUTATIONS)
        self.assertEqual(len(observed), 32)
        self.assertEqual(Counter(observed.values()), Counter(recovery.WRAPPER_MUTATION_ROUTES.values()))
        self.assertEqual(set(observed.values()), set(recovery.REFUSAL_ROUTES))

    def test_all_eight_profile_order_paths_replay_one_selection(self):
        identities = set()
        source_hashes = {profile: set() for profile in ("A", "B", "C", "D")}
        for profile in source_hashes:
            for row_order in ("canonical", "reversed"):
                source = domain_adapter.build_generated_live_source(
                    profile=profile,
                    row_order=row_order,
                    contract=self.contract,
                )
                result = recovery._adapt_once(source, contract=self.contract)
                identities.add(result.selection.selection_hashes["selection_identity_sha256"])
                source_hashes[profile].add(result.source_sha256)
        self.assertEqual(
            identities,
            {"dee065bfdb5f8439fe711042eaadbea0dca3d83f8be0d6b7b9d1637e84d9f641"},
        )
        self.assertTrue(all(len(values) == 1 for values in source_hashes.values()))

    def test_adapter_is_called_once_and_source_remains_unchanged(self):
        source = copy.deepcopy(self.source)
        before = domain_adapter._canonical_source_bytes(source)
        calls = 0

        def counted_adapter(value, *, contract):
            nonlocal calls
            calls += 1
            return domain_adapter.adapt_live_domain_source(value, contract=contract)

        result = recovery._adapt_once(
            source,
            contract=self.contract,
            adapter=counted_adapter,
        )
        self.assertEqual(calls, 1)
        self.assertEqual(before, domain_adapter._canonical_source_bytes(source))
        self.assertEqual(sum(result.predicate_counts.values()), 238)
        self.assertEqual(result.predicate_counts["MARC2VR2-P01"], 195)

    def test_source_mutation_and_mutable_alias_fail_closed(self):
        def mutating_adapter(value, *, contract):
            result = domain_adapter.adapt_live_domain_source(value, contract=contract)
            value["entries"].reverse()
            return result

        with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal) as caught:
            recovery._adapt_once(
                copy.deepcopy(self.source),
                contract=self.contract,
                adapter=mutating_adapter,
            )
        self.assertEqual(caught.exception.route, "MARC2VDR-F03")

        real_result = domain_adapter.adapt_live_domain_source(
            copy.deepcopy(self.source), contract=self.contract
        )
        aliased = copy.deepcopy(self.source)
        shared = aliased["entries"]
        private_manifest = dict(real_result.selection.private_manifest)
        private_manifest["rows"] = shared
        selection = type(real_result.selection)(
            private_manifest=private_manifest,
            cohort_summary=real_result.selection.cohort_summary,
            split_summary=real_result.selection.split_summary,
            byte_summary=real_result.selection.byte_summary,
            selection_hashes=real_result.selection.selection_hashes,
        )
        aliased_result = type(real_result)(
            predicate_counts=real_result.predicate_counts,
            source_sha256=real_result.source_sha256,
            eligible_keys=real_result.eligible_keys,
            selection=selection,
        )
        with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal) as caught:
            recovery._adapt_once(
                aliased,
                contract=self.contract,
                adapter=lambda *_args, **_kwargs: aliased_result,
            )
        self.assertEqual(caught.exception.route, "MARC2VDR-F03")

    def test_strict_json_rejects_duplicate_nonfinite_BOM_and_nonobject(self):
        malformed = (
            b'{"x":1,"x":2}',
            b'{"x":NaN}',
            b'\xef\xbb\xbf{"x":1}',
            b'[]',
        )
        for payload in malformed:
            with self.subTest(payload=payload):
                with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal) as caught:
                    recovery._strict_json(payload)
                self.assertEqual(caught.exception.route, "MARC2VDR-F02")

    def test_generated_no_follow_reader_opens_once_and_reconciles_fstat(self):
        payload = domain_adapter._canonical_json_bytes(self.source)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "fixture" / "source.json"
            path.parent.mkdir()
            path.write_bytes(payload)
            path.chmod(0o600)
            source_path, info, checks = recovery._preflight_relative_regular_file(
                root,
                Path("fixture/source.json"),
                expected_size=len(payload),
                expected_mode=0o600,
                expected_uid=os.getuid(),
            )
            original_open = recovery.os.open
            source_opens = 0

            def counted_open(candidate, flags, *args):
                nonlocal source_opens
                if Path(candidate) == path:
                    source_opens += 1
                return original_open(candidate, flags, *args)

            with mock.patch.object(recovery.os, "open", side_effect=counted_open):
                loaded = recovery._read_source_once(
                    source_path,
                    info,
                    expected_sha256=hashlib.sha256(payload).hexdigest(),
                    expected_size=len(payload),
                    component_checks=checks,
                )
        self.assertEqual(source_opens, 1)
        self.assertEqual(loaded.bytes_read, len(payload))
        self.assertEqual(loaded.source["schema_name"], self.source["schema_name"])

    def test_no_follow_preflight_rejects_symlink_mode_and_size(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / "fixture"
            fixture.mkdir()
            source = fixture / "source.json"
            source.write_text("{}", encoding="utf-8")
            source.chmod(0o600)
            symlink = root / "alias"
            symlink.symlink_to(fixture, target_is_directory=True)
            cases = (
                (Path("alias/source.json"), 2, 0o600),
                (Path("fixture/source.json"), 3, 0o600),
                (Path("fixture/source.json"), 2, 0o640),
            )
            for relative, size, mode in cases:
                with self.subTest(relative=relative, size=size, mode=mode):
                    with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal) as caught:
                        recovery._preflight_relative_regular_file(
                            root,
                            relative,
                            expected_size=size,
                            expected_mode=mode,
                            expected_uid=os.getuid(),
                        )
                    self.assertEqual(caught.exception.route, "MARC2VDR-F01")

    def test_machine_preflight_is_one_thread_and_bounded(self):
        with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
            result = recovery._machine_preflight(
                ROOT,
                load_reader=lambda: (1.0, 1.0, 1.0),
                cpu_reader=lambda: 8,
                disk_reader=lambda _path: os.statvfs(ROOT) and type(
                    "Disk", (), {"free": 20 * 1024**3}
                )(),
                rss_reader=lambda: 64 * 1024**2,
            )
        self.assertEqual(result["normalized_one_minute_load"], 0.125)
        with mock.patch.dict(
            os.environ,
            {**THREAD_ENVIRONMENT, "OMP_NUM_THREADS": "2"},
            clear=True,
        ):
            with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal):
                recovery._machine_preflight(ROOT)

    def test_generated_qualification_is_deterministic_and_private_free(self):
        def run_once():
            times = iter((100.0, 100.5))
            with mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
                return recovery.qualify_generated(
                    repo_root=ROOT,
                    clock=lambda: next(times),
                    rss_reader=lambda: 48 * 1024**2,
                )

        first = run_once()
        second = run_once()
        self.assertEqual(first, second)
        self.assertEqual(first["route"], "MARC2VDR-G1")
        self.assertEqual(first["source_summary"]["generated_success_paths"], 8)
        self.assertTrue(all(value == 0 for value in first["access_counters"].values()))
        self.assertTrue(all(first["acceptance_gates"].values()))
        recovery.validate_aggregate_report(first)

    def test_generated_full_execution_writes_only_three_bounded_files(self):
        payload = domain_adapter._canonical_json_bytes(self.source)
        digest = hashlib.sha256(payload).hexdigest()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / recovery.PRIVATE_SOURCE_RELATIVE_PATH
            source.parent.mkdir(parents=True)
            source.write_bytes(payload)
            source.chmod(0o600)
            (root / ".codex_work").chmod(0o700)
            evidence = recovery.ExecutionEvidence("a" * 40, 1, 2, 3)
            times = iter((1.0, 1.5))
            machine = {
                "logical_CPUs": 8,
                "normalized_one_minute_load": 0.1,
                "free_disk_bytes": 20 * 1024**3,
                "preflight_RSS_bytes": 32 * 1024**2,
            }
            with mock.patch.object(
                recovery, "_verify_execution_proof", return_value=None
            ), mock.patch.object(
                recovery, "_machine_preflight", return_value=machine
            ), mock.patch.object(
                domain_adapter,
                "load_registered_contract",
                return_value=self.contract,
            ), mock.patch.object(
                recovery, "EXPECTED_PRIVATE_BYTES", len(payload)
            ), mock.patch.object(
                recovery, "EXPECTED_PRIVATE_SHA256", digest
            ), mock.patch.dict(os.environ, THREAD_ENVIRONMENT, clear=True):
                outcome = recovery.execute_registered(
                    evidence,
                    repo_root=root,
                    clock=lambda: next(times),
                    rss_reader=lambda: 48 * 1024**2,
                )
            output = root / recovery.OUTPUT_ROOT_RELATIVE_PATH
            names = {path.name for path in output.iterdir()}
            self.assertEqual(
                names,
                {
                    recovery.MARKER_NAME,
                    recovery.PRIVATE_MANIFEST_NAME,
                    recovery.AGGREGATE_REPORT_NAME,
                },
            )
            self.assertEqual(stat.S_IMODE((output / recovery.MARKER_NAME).stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE((output / recovery.PRIVATE_MANIFEST_NAME).stat().st_mode), 0o600)
            inspected = recovery.inspect_aggregate_report(
                output / recovery.AGGREGATE_REPORT_NAME
            )
        self.assertEqual(outcome.report, inspected)
        self.assertEqual(inspected["route"], "MARC2VDR-R1")
        self.assertLess(inspected["measurements"]["output_bytes"], 2 * 1024**2)
        self.assertEqual(inspected["access_counters"]["signal_sample_reads"], 0)

    def test_aggregate_inspector_refuses_private_schema_and_leakage(self):
        private = {
            "schema_name": recovery.PRIVATE_SCHEMA_NAME,
            "rows": [{"member_name": "secret"}],
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / recovery.AGGREGATE_REPORT_NAME
            path.write_text(json.dumps(private), encoding="utf-8")
            with self.assertRaises(recovery.VariableDomainPrivateRecoveryRefusal) as caught:
                recovery.inspect_aggregate_report(path)
        self.assertEqual(caught.exception.route, "MARC2VDR-F05")

    def test_plan_help_and_surface_have_no_source_or_output_override(self):
        plan = recovery.build_plan_summary()
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertFalse(plan["MARC2_FW2_authorized"])
        parser = recovery._build_parser()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as caught:
                parser.parse_args(["execute", "--help"])
        self.assertEqual(caught.exception.code, 0)
        help_text = output.getvalue().lower()
        self.assertNotIn("--source", help_text)
        self.assertNotIn("--output", help_text)
        self.assertNotIn("--url", help_text)
        self.assertIn("--implementation-commit", help_text)

    def test_module_has_no_heavy_or_consumed_executor_import(self):
        source = Path(recovery.__file__).read_text(encoding="utf-8")
        for dependency in ("numpy", "scipy", "mne", "torch", "sklearn"):
            self.assertNotIn(f"import {dependency}", source)
        self.assertNotIn("import marc2_live_schema_adapter_recovery", source)
        self.assertNotIn("import marc2_freewill_private_selection", source)
        self.assertNotIn("live_alias_recovery_v2", source)


if __name__ == "__main__":
    unittest.main()
