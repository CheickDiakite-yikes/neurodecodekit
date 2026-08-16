import contextlib
import copy
import hashlib
import io
import json
import stat
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import marc2_machine_readiness as readiness
from neurodecodekit.datasets import (
    marc2_machine_stable_private_recovery as recovery,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENVIRONMENT = {name: "1" for name in recovery.THREAD_ENVIRONMENT}


class Marc2MachineStablePrivateRecoveryTests(unittest.TestCase):
    def test_native_registry_and_green_decision_are_exact(self):
        registry = recovery.load_implementation_registry(ROOT)
        proof = registry["green_authorization_decision"]
        self.assertEqual(
            proof["commit"], "eac37262dcf7cd4167475b7cc9145e3698d6dd9b"
        )
        self.assertEqual(proof["CI_run_id"], 31_969_063_955)
        self.assertEqual(proof["base_python_job_id"], 95_218_521_665)
        self.assertEqual(proof["optional_neuro_job_id"], 95_218_521_647)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(
            registry["real_execution_state"]["registered_real_execution_consumed"]
        )
        self.assertTrue(
            all(value == 0 for value in registry["implementation_access_counters"].values())
        )

    def test_plan_is_fixed_path_and_payload_free(self):
        plan = recovery.build_plan_summary()
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertEqual(
            plan["fixed_paths"]["private_source"],
            recovery.PRIVATE_SOURCE_RELATIVE_PATH.as_posix(),
        )
        self.assertFalse(plan["generic_path_or_root_override"])
        self.assertEqual(plan["network_or_archive_payload_bytes"], 0)

    def test_inspection_reads_only_committed_implementation_metadata(self):
        summary = recovery.build_inspection_summary()
        self.assertFalse(summary["real_execution_consumed"])
        self.assertFalse(summary["private_path_or_certificate_inspected"])
        self.assertIn("scientific_claim_not_established", summary["claim_boundary"])

    def test_generated_fixture_reaches_structural_success(self):
        outcome = recovery._run_generated_fixture(ROOT)
        report = outcome.aggregate_report
        self.assertEqual(report["route"], recovery.SUCCESS_ROUTE)
        self.assertEqual(
            report["proof_posture"],
            "generated_fixture_only_no_scientific_value",
        )
        self.assertEqual(report["cohort_summary"]["selected_subjects"], 16)
        self.assertEqual(report["cohort_summary"]["selected_bundles"], 96)
        self.assertEqual(report["cohort_summary"]["selected_members"], 384)
        self.assertEqual(report["cohort_summary"]["archive_member_or_payload_bytes"], 0)
        self.assertEqual(
            outcome.output_files,
            tuple(
                sorted(
                    (
                        recovery.MARKER_NAME,
                        recovery.PRIVATE_MANIFEST_NAME,
                        recovery.AGGREGATE_REPORT_NAME,
                    )
                )
            ),
        )
        recovery.validate_aggregate_report(report)

    def test_marker_write_immediately_precedes_source_content_open(self):
        events = []
        real_write = recovery._write_exclusive
        real_read = recovery._read_exact_nofollow

        def tracking_write(path, payload, **kwargs):
            events.append(("write", path.name))
            return real_write(path, payload, **kwargs)

        def tracking_read(root, identity, snapshot, route):
            events.append(("read", identity.relative_path.as_posix()))
            return real_read(root, identity, snapshot, route)

        with mock.patch.object(recovery, "_write_exclusive", side_effect=tracking_write), mock.patch.object(
            recovery, "_read_exact_nofollow", side_effect=tracking_read
        ):
            recovery._run_generated_fixture(ROOT)
        marker_event = ("write", recovery.MARKER_NAME)
        source_event = ("read", recovery.PRIVATE_SOURCE_RELATIVE_PATH.as_posix())
        marker_index = events.index(marker_event)
        source_index = events.index(source_event)
        self.assertEqual(source_index, marker_index + 1)

    def test_exact_adapter_call_count_is_one_per_sequence(self):
        from neurodecodekit.datasets import (
            marc2_live_domain_eligibility_adapter as adapter,
        )

        with mock.patch.object(
            adapter,
            "adapt_live_domain_source",
            wraps=adapter.adapt_live_domain_source,
        ) as wrapped:
            recovery._run_generated_fixture(ROOT)
        self.assertEqual(wrapped.call_count, 1)

    def test_generated_qualification_replays_and_refuses_all_mutations(self):
        times = iter((10.0, 10.2))
        report = recovery.qualify_generated(
            repo_root=ROOT,
            clock=lambda: next(times),
            rss_reader=lambda: 48 * 1024**2,
        )
        self.assertEqual(report["route"], recovery.SUCCESS_ROUTE)
        self.assertEqual(report["replay"]["runs"], 2)
        self.assertTrue(all(report["replay"].values()))
        self.assertEqual(report["mutation_summary"]["count"], 27)
        self.assertEqual(
            set(report["mutation_summary"]["routes"].values()),
            {
                recovery.REFUSAL_ROUTES[2],
                recovery.REFUSAL_ROUTES[3],
                recovery.REFUSAL_ROUTES[4],
                recovery.REFUSAL_ROUTES[5],
                recovery.REFUSAL_ROUTES[6],
                recovery.REFUSAL_ROUTES[7],
                recovery.REFUSAL_ROUTES[8],
            },
        )
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertTrue(all(value == 0 for value in report["real_access_counters"].values()))
        fixture = recovery._run_generated_fixture(ROOT)
        self.assertEqual(
            report["measurements"]["generated_input_bytes"],
            fixture.expired_input_bytes + fixture.source_input_bytes,
        )
        self.assertEqual(
            report["measurements"]["generated_output_bytes"],
            len(fixture.certificate_bytes)
            + len(fixture.marker_bytes)
            + len(fixture.private_manifest_bytes)
            + len(fixture.aggregate_bytes),
        )
        self.assertEqual(
            fixture.aggregate_report["measurements"]["combined_output_bytes"],
            len(fixture.certificate_bytes)
            + len(fixture.marker_bytes)
            + len(fixture.private_manifest_bytes)
            + len(fixture.aggregate_bytes),
        )

    def test_generated_qualification_is_deterministic_with_fixed_monitors(self):
        def run_once():
            times = iter((100.0, 100.25))
            return recovery.qualify_generated(
                repo_root=ROOT,
                clock=lambda: next(times),
                rss_reader=lambda: 48 * 1024**2,
            )

        self.assertEqual(run_once(), run_once())

    def test_exact_expired_cleanup_refuses_hash_drift_before_unlink(self):
        base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
        certificate = readiness.build_certificate(
            recovery._generated_raw_samples(base),
            implementation_commit="b" * 40,
            thread_environment=THREAD_ENVIRONMENT,
            proof_posture="machine_only_non_scientific",
            certificate_path=recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
        )
        payload = recovery._canonical_json_bytes(certificate)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            recovery._write_generated_fixture_file(
                root,
                recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH,
                payload,
                0o600,
            )
            identity = recovery.RegisteredFileIdentity(
                recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH,
                0o600,
                len(payload),
                "0" * 64,
            )
            snapshot = recovery._preflight_registered_file(
                root, identity, recovery.REFUSAL_ROUTES[1]
            )
            with self.assertRaisesRegex(
                recovery.MachineStableRecoveryRefusal, "MARC2MSP-F02"
            ):
                recovery._read_exact_nofollow(
                    root, identity, snapshot, recovery.REFUSAL_ROUTES[2]
                )
            self.assertTrue((root / identity.relative_path).is_file())

    def test_exact_expired_cleanup_unlinks_only_registered_file(self):
        base = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
        certificate = readiness.build_certificate(
            recovery._generated_raw_samples(base),
            implementation_commit="b" * 40,
            thread_environment=THREAD_ENVIRONMENT,
            proof_posture="machine_only_non_scientific",
            certificate_path=recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH.as_posix(),
        )
        payload = recovery._canonical_json_bytes(certificate)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            recovery._write_generated_fixture_file(
                root,
                recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH,
                payload,
                0o600,
            )
            sibling = root / recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH.parent / "keep"
            sibling.write_text("keep", encoding="ascii")
            identity = recovery.RegisteredFileIdentity(
                recovery.EXPIRED_CERTIFICATE_RELATIVE_PATH,
                0o600,
                len(payload),
                hashlib.sha256(payload).hexdigest(),
            )
            snapshot = recovery._preflight_registered_file(
                root, identity, recovery.REFUSAL_ROUTES[1]
            )
            opened = recovery._read_exact_nofollow(
                root, identity, snapshot, recovery.REFUSAL_ROUTES[2]
            )
            recovery._validate_expired_certificate(
                opened,
                implementation_commit="b" * 40,
                finished_at_UTC=certificate["finished_at_UTC"],
                expires_at_UTC=certificate["expires_at_UTC"],
                now_UTC=datetime(2026, 8, 16, 13, 0, tzinfo=timezone.utc),
            )
            recovery._unlink_exact_file(root, identity, snapshot)
            self.assertFalse((root / identity.relative_path).exists())
            self.assertEqual(sibling.read_text(encoding="ascii"), "keep")

    def test_file_mode_size_symlink_hash_and_race_mutations_refuse(self):
        routes = recovery._generated_mutations(ROOT)
        expected = {
            "registered_file_mode": recovery.REFUSAL_ROUTES[5],
            "registered_file_size": recovery.REFUSAL_ROUTES[5],
            "registered_file_symlink": recovery.REFUSAL_ROUTES[5],
            "registered_file_hash": recovery.REFUSAL_ROUTES[6],
            "registered_file_race": recovery.REFUSAL_ROUTES[6],
        }
        self.assertEqual({name: routes[name] for name in expected}, expected)

    def test_output_modes_and_inventory_are_strict(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir).resolve()
            output = recovery._create_new_output_root(root)
            recovery._write_exclusive(
                output / recovery.MARKER_NAME,
                b"{}\n",
                mode=0o600,
                route=recovery.REFUSAL_ROUTES[6],
            )
            recovery._write_exclusive(
                output / recovery.PRIVATE_MANIFEST_NAME,
                b"{}\n",
                mode=0o600,
                route=recovery.REFUSAL_ROUTES[8],
            )
            recovery._write_exclusive(
                output / recovery.AGGREGATE_REPORT_NAME,
                b"{}\n",
                mode=0o644,
                route=recovery.REFUSAL_ROUTES[8],
            )
            self.assertEqual(
                stat.S_IMODE((output / recovery.MARKER_NAME).stat().st_mode), 0o600
            )
            self.assertEqual(
                stat.S_IMODE(
                    (output / recovery.PRIVATE_MANIFEST_NAME).stat().st_mode
                ),
                0o600,
            )
            self.assertEqual(
                stat.S_IMODE(
                    (output / recovery.AGGREGATE_REPORT_NAME).stat().st_mode
                ),
                0o644,
            )

    def test_aggregate_firewall_rejects_private_identity_and_claim_upgrade(self):
        report = copy.deepcopy(recovery._run_generated_fixture(ROOT).aggregate_report)
        report["source_summary"]["subject_id"] = "sub-01"
        with self.assertRaisesRegex(
            recovery.MachineStableRecoveryRefusal, "MARC2MSP-F08"
        ):
            recovery.validate_aggregate_report(report)
        report = copy.deepcopy(recovery._run_generated_fixture(ROOT).aggregate_report)
        report["claim_boundary"]["scientific_claim_not_established"] = "effect"
        with self.assertRaisesRegex(
            recovery.MachineStableRecoveryRefusal, "MARC2MSP-F08"
        ):
            recovery.validate_aggregate_report(report)

    def test_cli_has_only_proof_arguments_and_no_path_override(self):
        parser = recovery._build_parser()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as caught:
                parser.parse_args(["execute", "--help"])
        self.assertEqual(caught.exception.code, 0)
        help_text = output.getvalue()
        for expected in (
            "--implementation-commit",
            "--ci-run-id",
            "--base-job-id",
            "--optional-job-id",
        ):
            self.assertIn(expected, help_text)
        for forbidden in ("--path", "--root", "--source", "--output", "--url"):
            self.assertNotIn(forbidden, help_text.lower())

    def test_cli_plan_and_inspect_do_not_touch_ignored_paths(self):
        for command in ("plan", "inspect"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(recovery.main([command]), 0)
            value = json.loads(output.getvalue())
            self.assertEqual(value["lane_id"], recovery.LANE_ID)

    def test_module_is_additive_and_has_no_heavy_or_consumed_executor_import(self):
        source = Path(recovery.__file__).read_text(encoding="utf-8")
        self.assertNotIn("marc2_variable_domain_private_recovery", source)
        for dependency in ("numpy", "scipy", "mne", "torch", "sklearn"):
            self.assertNotIn(f"import {dependency}", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("import requests", source)

    def test_thread_environment_is_all_one_for_generated_sequence(self):
        changed = dict(THREAD_ENVIRONMENT)
        changed[recovery.THREAD_ENVIRONMENT[0]] = "2"
        with self.assertRaisesRegex(
            recovery.MachineStableRecoveryRefusal, "MARC2MSP-F04"
        ):
            recovery._pre_marker_machine_recheck(
                ROOT,
                environ=changed,
                rss_reader=lambda: 1,
            )


if __name__ == "__main__":
    unittest.main()
