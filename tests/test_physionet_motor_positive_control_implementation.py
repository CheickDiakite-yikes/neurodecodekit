import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/physionet_motor_positive_control_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_IMPLEMENTATION.md"
TRACKER_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "src/neurodecodekit/cli.py": (
        "cbc61b66b952720606b5cf67d6c4cc0a187e69b3f2da644b351b00c9ec33fff7"
    ),
    "tests/test_physionet_motor_positive_control_implementation.py": (
        "4b4ddfec594972e5e73ec77857586377807bb5c40cc4510917a5d8b9e4207e25"
    ),
    ".github/workflows/ci.yml": (
        "0f48b968d3837d797f3770a5ec8956864c11c0765c1a8c65eb6774629612f027"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetMotorPositiveControlImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_requires_remote_green_before_real_access(self):
        self.assertEqual(
            self.registry["status"],
            "fixture_qualified_exact_implementation_requires_remote_green_before_real_access",
        )
        self.assertFalse(self.registry["execution_state"]["registered_execution_consumed"])
        self.assertFalse(self.registry["execution_state"]["prediction_freeze_created"])
        self.assertFalse(self.registry["execution_state"]["final_targets_delivered"])

    def test_green_authorization_parent_is_exact(self):
        self.assertEqual(
            self.registry["green_authorization_decision"],
            {
                "commit": "da9399c4290fc2be81834ed1036a6bede5f52154",
                "push_ci_run_id": 31348287824,
                "base_python_job_id": 93334251403,
                "optional_neuro_job_id": 93334251379,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            self.registry["authorization_decision_sha256"],
            sha256(
                ROOT
                / "registries/physionet_motor_positive_control_authorization_decision.v0.json"
            ),
        )

    def test_all_tracked_implementation_hashes_are_current(self):
        paths = set()
        for row in self.registry["tracked_file_hashes"]:
            self.assertNotIn(row["path"], paths)
            paths.add(row["path"])
            if row["path"] in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(row["sha256"], HISTORICAL_MUTABLE_BINDINGS[row["path"]])
            else:
                self.assertEqual(row["sha256"], sha256(ROOT / row["path"]), row["path"])
        self.assertIn(
            "src/neurodecodekit/experiments/physionet_motor_positive_control.py",
            paths,
        )
        self.assertIn("src/neurodecodekit/cli.py", paths)
        self.assertIn("pyproject.toml", paths)
        self.assertIn(".github/workflows/ci.yml", paths)
        current_cli = (ROOT / "src/neurodecodekit/cli.py").read_text(encoding="utf-8")
        for command in (
            '"physionet-motor-positive-control"',
            '"score-physionet-motor-positive-control"',
            '"physionet-low-frequency-cohort"',
        ):
            self.assertIn(command, current_cli)

    def test_optional_environment_is_narrow_and_base_is_unchanged(self):
        environment = self.registry["optional_environment"]
        self.assertEqual(
            environment["qualified_versions"],
            {
                "numpy": "2.5.2",
                "scipy": "1.18.0",
                "mne": "1.12.1",
                "scikit_learn": "1.9.0",
                "pyriemann": "0.12",
            },
        )
        self.assertEqual(environment["base_dependencies_added"], [])
        self.assertEqual(environment["installer_workers"], 1)
        self.assertLess(environment["download_bytes_upper_bound"], 256 * 1024 * 1024)
        self.assertLess(environment["retained_disk_bytes"], 512 * 1024 * 1024)

    def test_fixture_qualification_is_measured_and_target_free(self):
        qualification = self.registry["fixture_qualification"]
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["synthetic_runs"], 9)
        self.assertEqual(qualification["synthetic_events"], 135)
        self.assertEqual(qualification["classical_parameter_update_fits"], 33)
        self.assertEqual(qualification["target_blind_model_inference_runs"], 45)
        self.assertEqual(qualification["prediction_sets"], 12)
        self.assertEqual(qualification["generated_bytes"], 20_825_424)
        self.assertEqual(qualification["real_data_reads"], 0)
        self.assertEqual(qualification["real_target_reads"], 0)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertFalse(qualification["scientific_claim_upgrade"])

    def test_firewall_freeze_and_resource_contract_are_explicit(self):
        firewall = self.registry["target_firewall"]
        self.assertEqual(firewall["fit_target_rows"], 90)
        self.assertEqual(firewall["target_free_prediction_rows"], 45)
        self.assertEqual(firewall["sealed_target_rows"], 45)
        self.assertFalse(firewall["sealed_target_file_opened_by_model_stage"])
        freeze = self.registry["prediction_freeze"]
        self.assertEqual(freeze["prediction_set_count"], 12)
        self.assertTrue(freeze["per_condition_sha256_required"])
        self.assertTrue(freeze["code_split_configuration_and_payload_hashes_required"])
        resources = self.registry["real_execution_caps"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["wall_time_seconds"], 1800)
        self.assertEqual(resources["peak_rss_bytes"], 805_306_368)
        self.assertEqual(resources["generated_private_output_bytes"], 64 * 1024 * 1024)
        self.assertEqual(resources["retries"], 0)
        self.assertEqual(resources["reruns"], 0)

    def test_every_real_or_forbidden_implementation_counter_is_zero(self):
        for name, value in self.registry["implementation_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_document_and_tracker_preserve_claim_and_execution_gate(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("function and artifact boundary", document)
        tracker = TRACKER_PATH.read_text(encoding="utf-8")
        row = next(line for line in tracker.splitlines() if line.startswith("| 9 |"))
        self.assertIn("Implementation Qualified Locally", row)
        self.assertIn("Execution Pending Remote Green", row)


if __name__ == "__main__":
    unittest.main()
