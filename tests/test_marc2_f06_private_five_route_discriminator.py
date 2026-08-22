import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from neurodecodekit.datasets import (
    marc2_f06_private_five_route_discriminator as wrapper,
)


ROOT = Path(__file__).resolve().parents[1]
THREAD_ENV = {name: "1" for name in wrapper.THREAD_ENVIRONMENT}


class Marc2F06PrivateFiveRouteDiscriminatorTests(unittest.TestCase):
    def test_decision_and_plan_are_exact_and_target_free(self):
        decision = wrapper.load_decision()
        plan = wrapper.build_plan()
        self.assertEqual(decision["lane_id"], "MARC2-VR24P")
        self.assertEqual(
            decision["user_authorization"]["actual_message_verbatim"], "continue"
        )
        self.assertEqual(plan["generated_paths"], 24)
        self.assertEqual(plan["generated_success_paths"], 4)
        self.assertEqual(plan["generated_refusal_paths"], 20)
        self.assertEqual(plan["VR23A_calls"], 24)
        self.assertEqual(plan["nested_VR20A_calls"], 24)
        self.assertEqual(plan["direct_refusal_minimum"], 80)
        self.assertFalse(plan["FW2_authorized"])
        self.assertFalse(plan["CIL1_authorized"])

    def test_module_import_is_standard_library_only_beyond_repo_modules(self):
        code = """
import sys
import neurodecodekit.datasets.marc2_f06_private_five_route_discriminator
for name in ('numpy', 'scipy', 'mne', 'torch', 'sklearn'):
    assert name not in sys.modules, name
"""
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "src")
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_generated_qualification_passes_matrix_and_refusal_floor(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            report = wrapper.qualify_generated(peak_rss=lambda: 32 * 1024**2)
        matrix = report["matrix"]
        self.assertEqual(report["route"], "MARC2VR24P-G1")
        self.assertEqual(matrix["paths"], 24)
        self.assertEqual(matrix["success_paths"], 4)
        self.assertEqual(matrix["refusal_paths"], 20)
        self.assertEqual(
            matrix["route_counts"],
            {route: 4 for route in wrapper.GENERATED_CASE_ROUTES.values()},
        )
        self.assertEqual(matrix["VR23A_calls"], 24)
        self.assertEqual(matrix["nested_VR20A_calls"], 24)
        self.assertEqual(matrix["generated_source_content_opens"], 24)
        self.assertTrue(
            all(
                len(set(values)) == 1
                for values in matrix["replay_source_hashes"].values()
            )
        )
        self.assertGreaterEqual(report["refusals"]["direct_refusals"], 80)
        self.assertEqual(report["measurements"]["retained_generated_output_bytes"], 0)
        self.assertTrue(all(value == 0 for value in report["operation_counters"].values()))

    def test_qualification_replays_deterministically(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            first = wrapper.qualify_generated(peak_rss=lambda: 32 * 1024**2)
            second = wrapper.qualify_generated(peak_rss=lambda: 32 * 1024**2)
        for key in (
            "success_paths",
            "refusal_paths",
            "route_counts",
            "VR23A_calls",
            "nested_VR20A_calls",
            "replay_source_hashes",
        ):
            self.assertEqual(first["matrix"][key], second["matrix"][key])
        self.assertEqual(first["refusals"], second["refusals"])

    def test_every_envelope_mutation_fails_closed(self):
        counts = wrapper._run_direct_refusals()
        self.assertEqual(
            sum(counts.values()),
            len(wrapper._ENVELOPE_EXPECTED)
            + 2
            + len(wrapper.FORBIDDEN_PUBLIC_KEYS),
        )
        self.assertGreaterEqual(sum(counts.values()), 80)
        self.assertGreaterEqual(sum(value > 0 for value in counts.values()), 8)

    def test_strict_json_rejects_duplicate_nonfinite_and_nonobject(self):
        for payload in (b'{"a":1,"a":2}', b'{"a":NaN}', b"[]"):
            with self.subTest(payload=payload):
                with self.assertRaises(
                    wrapper.F06PrivateFiveRouteDiscriminatorRefusal
                ) as caught:
                    wrapper._strict_json(payload)
                self.assertEqual(caught.exception.route, "MARC2VR24P-F07")

    def test_generated_fixed_path_control_writes_no_private_manifest(self):
        source = wrapper._build_generated_case("control_success", "canonical")
        result, output = self._run_generated_case(source, "control_success")
        self.assertEqual(result["report"]["route"], "MARC2VR24P-G1")
        self.assertEqual(result["VR23A_calls"], 1)
        self.assertEqual(result["nested_VR20A_calls"], 1)
        self.assertEqual(
            sorted(path.name for path in output.iterdir()),
            [wrapper.MARKER_RELATIVE_NAME, wrapper.REPORT_RELATIVE_NAME],
        )
        self.assertLessEqual(result["combined_output_bytes"], 1 * 1024**2)

    def test_generated_F06_cases_map_to_exact_five_routes(self):
        expected = {
            case: f"MARC2VR24P-R{index}"
            for index, case in enumerate(wrapper.GENERATED_CASES[1:], start=1)
        }
        for case, route in expected.items():
            with self.subTest(case=case):
                source = wrapper._build_generated_case(case, "canonical")
                result, _output = self._run_generated_case(source, case)
                self.assertEqual(result["report"]["route"], route)
                self.assertEqual(result["VR23A_calls"], 1)
                self.assertEqual(result["nested_VR20A_calls"], 1)

    def _run_generated_case(
        self, source: dict[str, object], case: str
    ) -> tuple[dict[str, object], Path]:
        payload = wrapper._canonical_json_bytes(source)
        identity = {
            "mode": 0o600,
            "bytes": len(payload),
            "sha256": wrapper._sha256_bytes(payload),
        }
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        source_path = root / wrapper.PRIVATE_SOURCE_RELATIVE_PATH
        source_path.parent.mkdir(parents=True)
        source_path.write_bytes(payload)
        os.chmod(source_path, 0o600)
        result = wrapper._run_fixed_sequence(
            root,
            samples=wrapper._generated_samples(),
            source_identity=identity,
            implementation_commit="generated-implementation-pending",
            generated=True,
            generated_case=case,
            peak_rss=lambda: 32 * 1024**2,
        )
        return result, root / wrapper.OUTPUT_ROOT_RELATIVE_PATH

    def test_source_mode_drift_refuses_at_R7(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.json"
            source.write_text("{}", encoding="utf-8")
            os.chmod(source, 0o644)
            identity = {
                "mode": 0o600,
                "bytes": 2,
                "sha256": wrapper._sha256_bytes(b"{}"),
            }
            with self.assertRaises(
                wrapper.F06PrivateFiveRouteDiscriminatorRefusal
            ) as caught:
                wrapper._read_source_once(source, identity)
            self.assertEqual(caught.exception.route, "MARC2VR24P-R7")

    def test_mock_private_parse_failure_writes_only_aggregate_R7_report(self):
        payload = b'{"a":NaN}'
        identity = {
            "mode": 0o600,
            "bytes": len(payload),
            "sha256": wrapper._sha256_bytes(payload),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / wrapper.PRIVATE_SOURCE_RELATIVE_PATH
            source_path.parent.mkdir(parents=True)
            source_path.write_bytes(payload)
            os.chmod(source_path, 0o600)
            result = wrapper._run_fixed_sequence(
                root,
                samples=wrapper._generated_samples(),
                source_identity=identity,
                implementation_commit="generated-failure-fixture",
                generated=False,
                peak_rss=lambda: 32 * 1024**2,
            )
            output = root / wrapper.OUTPUT_ROOT_RELATIVE_PATH
            report_path = output / wrapper.REPORT_RELATIVE_NAME
            self.assertEqual(result["report"]["route"], "MARC2VR24P-R7")
            self.assertEqual(
                sorted(path.name for path in output.iterdir()),
                [wrapper.MARKER_RELATIVE_NAME, wrapper.REPORT_RELATIVE_NAME],
            )
            self.assertEqual(report_path.stat().st_mode & 0o777, 0o644)
            self.assertEqual(
                result["report"]["operation_counters"][
                    "private_structural_source_reads"
                ],
                1,
            )

    def test_public_execute_refuses_before_readiness_when_proof_is_null(self):
        record = {
            "schema_name": (
                "neurodecodekit."
                "marc2_f06_private_five_route_discriminator_implementation"
            ),
            "lane_id": "MARC2-VR24P",
            "remote_implementation_proof": None,
        }
        with mock.patch.object(wrapper, "load_decision", return_value=wrapper.load_decision()):
            with mock.patch.object(wrapper, "_load_implementation", return_value=record):
                with mock.patch.object(wrapper, "_collect_readiness") as readiness:
                    with self.assertRaises(
                        wrapper.F06PrivateFiveRouteDiscriminatorRefusal
                    ) as caught:
                        wrapper.execute_registered()
        self.assertEqual(caught.exception.route, "MARC2VR24P-F01")
        readiness.assert_not_called()

    def test_green_proof_shape_is_strict(self):
        for proof in (
            None,
            {},
            {"both_required_jobs_green": False},
            {
                "both_required_jobs_green": True,
                "scope_changed_after_qualification": True,
                "commit": "a" * 40,
            },
        ):
            with self.subTest(proof=proof):
                with self.assertRaises(
                    wrapper.F06PrivateFiveRouteDiscriminatorRefusal
                ):
                    wrapper._require_green_implementation(
                        {"remote_implementation_proof": proof}
                    )

    def test_green_proof_binds_exact_artifact_set(self):
        record = json.loads(
            (ROOT / wrapper.IMPLEMENTATION_RELATIVE_PATH).read_text(encoding="utf-8")
        )
        proof = {
            "commit": "a" * 40,
            "CI_run_id": 1,
            "base_job_id": 2,
            "optional_neuro_job_id": 3,
            "both_required_jobs_green": True,
            "scope_changed_after_qualification": False,
            "qualification_route": "MARC2VR24P-G1",
            "qualification_repeated_for_proof_closeout": False,
            "private_operations_during_proof_closeout": 0,
            "implementation_registry_preproof_bytes": 1,
            "implementation_registry_preproof_sha256": "b" * 64,
            "implementation_artifact_set_sha256": wrapper._sha256_bytes(
                wrapper._canonical_json_bytes(record["implementation_artifacts"])
            ),
        }
        record["remote_implementation_proof"] = proof
        self.assertEqual(wrapper._require_green_implementation(record, ROOT), "a" * 40)
        proof["implementation_artifact_set_sha256"] = "c" * 64
        with self.assertRaises(wrapper.F06PrivateFiveRouteDiscriminatorRefusal):
            wrapper._require_green_implementation(record, ROOT)

    def test_resource_and_output_caps_fail_closed(self):
        for values in (
            (61.0, 1, 1),
            (1.0, 256 * 1024**2, 1),
            (1.0, 1, 1 * 1024**2 + 1),
        ):
            with self.subTest(values=values):
                with self.assertRaises(
                    wrapper.F06PrivateFiveRouteDiscriminatorRefusal
                ) as caught:
                    wrapper._assert_resources(*values)
                self.assertEqual(caught.exception.route, "MARC2VR24P-F11")
        wrapper._assert_resources(61.0, 1, 1, generated=False)
        with self.assertRaises(wrapper.F06PrivateFiveRouteDiscriminatorRefusal):
            wrapper._assert_resources(651.0, 1, 1, generated=False)

    def test_public_report_firewall_rejects_private_keys(self):
        for key in wrapper.FORBIDDEN_PUBLIC_KEYS:
            with self.subTest(key=key):
                with self.assertRaises(
                    wrapper.F06PrivateFiveRouteDiscriminatorRefusal
                ):
                    wrapper._walk_public({key: "private"})

    def test_cli_has_only_fixed_commands_and_no_path_overrides(self):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.datasets."
                "marc2_f06_private_five_route_discriminator",
                "--help",
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("{plan,qualify,inspect,execute}", result.stdout)
        for forbidden in ("--source", "--output", "--retry", "--threshold"):
            self.assertNotIn(forbidden, result.stdout)

    def test_qualification_report_is_aggregate_only(self):
        with mock.patch.dict(os.environ, THREAD_ENV, clear=False):
            report = wrapper.qualify_generated(peak_rss=lambda: 32 * 1024**2)
        encoded = json.dumps(report, sort_keys=True)
        for forbidden in (
            '"member_name"',
            '"selected_subject_ids"',
            '"target"',
            '"prediction"',
            '"score"',
        ):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
