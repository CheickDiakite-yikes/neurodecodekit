import copy
import shutil
import stat
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from neurodecodekit.datasets import marc2_machine_readiness as readiness


ROOT = Path(__file__).resolve().parents[1]


class Marc2MachineReadinessTests(unittest.TestCase):
    def test_registered_contract_loads_by_exact_hash(self):
        contract = readiness.load_registered_contract(ROOT)
        self.assertEqual(contract["lane_id"], "MARC2-VR4")
        self.assertEqual(
            readiness._sha256_file(ROOT / readiness.CONTRACT_RELATIVE_PATH),
            readiness.CONTRACT_SHA256,
        )

    def test_plan_has_only_registered_commands(self):
        plan = readiness.build_plan_summary()
        self.assertEqual(plan["commands"], ["plan", "qualify", "inspect", "readiness"])
        self.assertNotIn("execute", plan["commands"])
        self.assertEqual(plan["private_content_opens"], 0)
        self.assertFalse(plan["FW2_authorized"])

    def test_three_passing_samples_are_ready(self):
        certificate = readiness._generated_certificate("three_pass")
        self.assertTrue(certificate["ready"])
        self.assertEqual(certificate["route"], "MARC2RDY-G1")
        self.assertEqual(certificate["measurements"]["consecutive_passing_tail"], 3)
        readiness.validate_certificate(certificate)

    def test_one_failure_then_three_passes_recovers(self):
        certificate = readiness._generated_certificate("recover")
        self.assertTrue(certificate["ready"])
        self.assertEqual(len(certificate["samples"]), 4)
        self.assertFalse(certificate["samples"][0]["passing"])
        self.assertTrue(all(sample["passing"] for sample in certificate["samples"][1:]))

    def test_exact_inclusive_and_exclusive_boundaries_pass(self):
        certificate = readiness._generated_certificate("boundary")
        sample = certificate["samples"][0]
        self.assertEqual(sample["normalized_one_minute_load"], 1.0)
        self.assertEqual(sample["process_peak_RSS_bytes"], 256 * 1024**2 - 1)
        self.assertEqual(sample["free_disk_bytes"], 15 * 1024**3)
        self.assertTrue(certificate["ready"])

    def test_timeout_shape_is_not_ready_but_valid(self):
        certificate = readiness._generated_certificate("timeout")
        self.assertFalse(certificate["ready"])
        self.assertEqual(certificate["route"], "MARC2RDY-F02")
        readiness.validate_certificate(certificate, allow_not_ready=True)
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F02"):
            readiness.validate_certificate(certificate)

    def test_generated_replay_is_byte_identical(self):
        first = readiness._canonical_json_bytes(readiness._generated_certificate())
        second = readiness._canonical_json_bytes(readiness._generated_certificate())
        self.assertEqual(first, second)
        self.assertLess(len(first), readiness.MAX_CERTIFICATE_BYTES)

    def test_nonfinite_normalized_load_refuses(self):
        samples = readiness._generated_samples("three_pass")
        samples[0]["normalized_one_minute_load"] = float("nan")
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F01"):
            readiness.build_certificate(
                samples,
                implementation_commit="a" * 40,
                thread_environment={key: "1" for key in readiness.THREAD_ENVIRONMENT},
                proof_posture="generated_only_non_authoritative",
                certificate_path="<generated-fixture>",
            )

    def test_zero_logical_cpu_refuses(self):
        samples = readiness._generated_samples("three_pass")
        samples[0]["logical_CPUs"] = 0
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F01"):
            readiness.build_certificate(
                samples,
                implementation_commit="a" * 40,
                thread_environment={key: "1" for key in readiness.THREAD_ENVIRONMENT},
                proof_posture="generated_only_non_authoritative",
                certificate_path="<generated-fixture>",
            )

    def test_timestamp_regression_refuses(self):
        samples = readiness._generated_samples("three_pass")
        samples[1]["observed_at_UTC"] = samples[0]["observed_at_UTC"]
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F02"):
            readiness.build_certificate(
                samples,
                implementation_commit="a" * 40,
                thread_environment={key: "1" for key in readiness.THREAD_ENVIRONMENT},
                proof_posture="generated_only_non_authoritative",
                certificate_path="<generated-fixture>",
            )

    def test_short_sample_interval_refuses(self):
        samples = readiness._generated_samples("three_pass")
        first = datetime.fromisoformat(samples[0]["observed_at_UTC"][:-1] + "+00:00")
        samples[1]["observed_at_UTC"] = readiness._format_utc(first + timedelta(seconds=4))
        samples[1]["monotonic_seconds"] = samples[0]["monotonic_seconds"] + 4
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F02"):
            readiness.build_certificate(
                samples,
                implementation_commit="a" * 40,
                thread_environment={key: "1" for key in readiness.THREAD_ENVIRONMENT},
                proof_posture="generated_only_non_authoritative",
                certificate_path="<generated-fixture>",
            )

    def test_thread_drift_yields_diagnostic_not_ready_certificate(self):
        values = {key: "1" for key in readiness.THREAD_ENVIRONMENT}
        values["OMP_NUM_THREADS"] = "2"
        certificate = readiness.build_certificate(
            readiness._generated_samples("three_pass"),
            implementation_commit="a" * 40,
            thread_environment=values,
            proof_posture="generated_only_non_authoritative",
            certificate_path="<generated-fixture>",
        )
        self.assertFalse(certificate["ready"])
        self.assertEqual(certificate["route"], "MARC2RDY-F01")
        self.assertIn("OMP_NUM_THREADS", certificate["measurements"]["refusal_reasons"][0])

    def test_each_sample_emits_values_thresholds_checks_and_reasons(self):
        certificate = readiness._generated_certificate("recover")
        for index, sample in enumerate(certificate["samples"], start=1):
            self.assertEqual(set(sample), readiness.SAMPLE_FIELDS)
            self.assertEqual(sample["sequence"], index)
            self.assertIn("normalized_one_minute_load_maximum", sample["thresholds"])
            self.assertIn("free_disk_at_or_above_minimum", sample["checks"])
            self.assertIsInstance(sample["refusal_reasons"], list)

    def test_expired_certificate_refuses(self):
        certificate = readiness._generated_certificate()
        expiry = datetime.fromisoformat(certificate["expires_at_UTC"][:-1] + "+00:00")
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F03"):
            readiness.validate_certificate(
                certificate, now_UTC=expiry + timedelta(microseconds=1)
            )

    def test_counter_leak_refuses(self):
        certificate = readiness._generated_certificate()
        certificate["access_counters"]["private_content_opens"] = 1
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F05"):
            readiness.validate_certificate(certificate)

    def test_claim_upgrade_refuses(self):
        certificate = readiness._generated_certificate()
        certificate["claim_boundary"]["scientific_claim_not_established"] = "effect proven"
        with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F05"):
            readiness.validate_certificate(certificate)

    def test_inspect_accepts_only_canonical_mode_0600_generated_file(self):
        payload = readiness._canonical_json_bytes(readiness._generated_certificate())
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "certificate.json"
            path.write_bytes(payload)
            path.chmod(0o600)
            inspected = readiness.inspect_certificate_file(
                path,
                now_UTC=datetime(2026, 8, 16, 12, 1, tzinfo=timezone.utc),
            )
            self.assertTrue(inspected["ready"])

    def test_inspect_refuses_symlink_mode_drift_and_oversize(self):
        payload = readiness._canonical_json_bytes(readiness._generated_certificate())
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target.json"
            target.write_bytes(payload)
            target.chmod(0o600)
            symlink = root / "link.json"
            symlink.symlink_to(target)
            with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F04"):
                readiness.inspect_certificate_file(symlink)
            mode = root / "mode.json"
            mode.write_bytes(payload)
            mode.chmod(0o644)
            with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F04"):
                readiness.inspect_certificate_file(mode)
            large = root / "large.json"
            large.write_bytes(b"x" * (readiness.MAX_CERTIFICATE_BYTES + 1))
            large.chmod(0o600)
            with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F04"):
                readiness.inspect_certificate_file(large)

    def test_generated_qualification_exercises_all_36_mutations(self):
        report = readiness.qualify_generated(
            repo_root=ROOT,
            rss_reader=lambda: 32 * 1024**2,
        )
        self.assertEqual(report["route"], "MARC2RDY-G1")
        self.assertEqual(report["mutation_summary"]["count"], 36)
        self.assertEqual(
            report["mutation_summary"]["ordered_names"],
            list(readiness.ORDERED_MUTATIONS),
        )
        self.assertTrue(all(report["acceptance_gates"].values()))
        self.assertTrue(
            all(
                report["access_counters"][key] == 0
                for key in readiness.ZERO_SCIENTIFIC_COUNTERS
            )
        )
        self.assertEqual(
            report["measurements"]["report_bytes"],
            len(readiness._canonical_json_bytes(report)),
        )

    def test_generated_qualification_removes_temporary_output(self):
        report = readiness.qualify_generated(
            repo_root=ROOT,
            rss_reader=lambda: 32 * 1024**2,
        )
        self.assertEqual(report["measurements"]["retained_generated_output_bytes"], 0)
        self.assertTrue(report["measurements"]["temporary_generated_output_removed"])

    def test_run_readiness_writes_only_fixed_mode_0600_certificate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            registry = root / readiness.CONTRACT_RELATIVE_PATH
            registry.parent.mkdir(parents=True)
            shutil.copy2(ROOT / readiness.CONTRACT_RELATIVE_PATH, registry)
            git_dir = root / ".git"
            git_dir.mkdir()
            (git_dir / "HEAD").write_text("b" * 40 + "\n", encoding="ascii")
            samples = iter(readiness._generated_samples("three_pass"))

            def sampler(_root, _sequence):
                return next(samples)

            certificate = readiness.run_readiness(
                repo_root=root,
                sampler=sampler,
                sleeper=lambda _seconds: None,
                environ={key: "1" for key in readiness.THREAD_ENVIRONMENT},
            )
            destination = root / readiness.CERTIFICATE_RELATIVE_PATH
            self.assertTrue(destination.is_file())
            self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o600)
            self.assertEqual(certificate["implementation_commit"], "b" * 40)
            self.assertEqual(certificate["proof_posture"], "machine_only_non_scientific")
            self.assertTrue(certificate["ready"])
            inventory = [path for path in root.rglob("*") if path.is_file()]
            self.assertEqual(
                sorted(path.relative_to(root).as_posix() for path in inventory),
                [
                    ".codex_work/marc2_machine_readiness/vr4/readiness.v0.json",
                    ".git/HEAD",
                    readiness.CONTRACT_RELATIVE_PATH.as_posix(),
                ],
            )

    def test_fixed_certificate_overwrite_is_refused(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            destination = root / readiness.CERTIFICATE_RELATIVE_PATH
            destination.parent.mkdir(parents=True)
            destination.write_text("existing", encoding="ascii")
            destination.chmod(0o600)
            certificate = copy.deepcopy(readiness._generated_certificate())
            certificate["proof_posture"] = "machine_only_non_scientific"
            certificate["certificate_path"] = readiness.CERTIFICATE_RELATIVE_PATH.as_posix()
            readiness.validate_certificate(certificate)
            with self.assertRaisesRegex(readiness.MachineReadinessRefusal, "MARC2RDY-F04"):
                readiness._write_fixed_certificate(root, certificate)

    def test_module_has_no_private_or_model_execution_surface(self):
        source = Path(readiness.__file__).read_text(encoding="utf-8")
        self.assertNotIn("def execute", source)
        self.assertNotIn("import mne", source)
        self.assertNotIn("import numpy", source)
        self.assertNotIn("import torch", source)
        self.assertNotIn("import requests", source)
        self.assertNotIn("import urllib", source)

    def test_cli_parser_has_no_machine_override_arguments(self):
        parser = readiness._build_parser()
        help_text = parser.format_help()
        for forbidden in ("--root", "--threshold", "--interval", "--samples", "--wait"):
            self.assertNotIn(forbidden, help_text)


if __name__ == "__main__":
    unittest.main()
