from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit import comm_live_g0_cli  # noqa: E402
from neurodecodekit.experiments import comm_live_g0_generated as experiment  # noqa: E402


CHILD_ENVIRONMENT_KEYS = (
    "PATH",
    "HOME",
    "TMPDIR",
    "TMP",
    "TEMP",
    "LANG",
    "LC_ALL",
    "LD_LIBRARY_PATH",
    "DYLD_LIBRARY_PATH",
    "PYTHONHASHSEED",
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
)


class CommunicationLiveSessionG0ImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        environment = {
            key: os.environ[key] for key in CHILD_ENVIRONMENT_KEYS if key in os.environ
        }
        environment["PYTHONPATH"] = str(SRC)
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import json,sys; "
                    "from neurodecodekit.experiments.comm_live_g0_generated "
                    "import run_development_qualification; "
                    "print(json.dumps(run_development_qualification(sys.argv[1]), "
                    "sort_keys=True))"
                ),
                str(ROOT),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=40,
            env=environment,
        )
        if completed.returncode != 0:
            raise AssertionError(
                "isolated development qualification failed: "
                f"returncode={completed.returncode}; stderr={completed.stderr!r}"
            )
        cls.development = json.loads(completed.stdout)

    def test_plan_binds_exact_generated_inventory(self) -> None:
        plan = experiment.plan(ROOT)
        self.assertEqual(plan["lane_id"], "COMM-LIVE-G0")
        self.assertEqual(plan["fictional_sessions"], 4)
        self.assertEqual(plan["deterministic_replays"], 2)
        self.assertEqual(
            plan["partition_schedules"],
            ["one_sample", "fixed_width", "jittered", "whole_stream"],
        )
        self.assertEqual(
            plan["control_schedules"], ["gap_reconnect", "quality_confidence"]
        )
        self.assertEqual(
            plan["session_schedule_assignments"],
            [list(value) for value in experiment.SESSION_SCHEDULE_ASSIGNMENTS],
        )
        self.assertEqual(plan["required_adversarial_family_count"], 33)
        self.assertFalse(plan["official_qualification_available_now"])
        self.assertEqual(plan["real_network_provider_device_model_operations"], 0)

    def test_development_replay_is_complete_and_nonconsuming(self) -> None:
        result = self.development
        self.assertEqual(result["status"], "development_only_repeatable_not_official")
        self.assertEqual(result["route"], "COMM-LIVE-G0-DEVELOPMENT-PASS")
        self.assertFalse(result["official_invocation_consumed"])
        replay = result["replay_equivalence"]
        self.assertEqual(replay["deterministic_replays"], 2)
        self.assertTrue(replay["byte_equivalent"])
        self.assertEqual(replay["fictional_sessions"], 4)
        self.assertEqual(len(replay["partition_schedules"]), 4)
        self.assertEqual(len(replay["control_schedules"]), 2)
        self.assertEqual(
            replay["session_schedule_assignments"],
            [list(value) for value in experiment.SESSION_SCHEDULE_ASSIGNMENTS],
        )
        self.assertGreater(result["aggregate_proof"]["positive_control_commit_count"], 0)

    def test_all_33_exact_refusal_family_ids_are_bound_once(self) -> None:
        adversarial = self.development["adversarial_qualification"]
        self.assertEqual(adversarial["refusal_count"], 33)
        self.assertEqual(
            adversarial["refusal_ids"], list(experiment.REQUIRED_REFUSAL_FAMILIES)
        )
        self.assertEqual(len(set(adversarial["refusal_ids"])), 33)
        self.assertTrue(adversarial["every_named_family_executed"])
        self.assertTrue(
            all(row["refused"] for row in adversarial["observed"])
        )
        self.assertTrue(
            all(row["exact_family_id_bound"] for row in adversarial["observed"])
        )
        self.assertEqual(
            {
                row["family_id"]: row["observed_internal_refusal"]
                for row in adversarial["observed"]
            },
            dict(experiment.EXPECTED_INTERNAL_REFUSALS),
        )

    def test_wrong_internal_refusal_cannot_satisfy_registered_family(self) -> None:
        def wrong_refusal() -> None:
            raise experiment.CommLiveG0GeneratedRefusal("some_other_refusal")

        with self.assertRaises(experiment.CommLiveG0GeneratedRefusal) as caught:
            experiment._expect_refusal("source_identity_mismatch", wrong_refusal)
        self.assertEqual(
            caught.exception.refusal_id, "COMM-LIVE-G0-WRONG-INTERNAL-REFUSAL"
        )

    def test_resources_and_forbidden_operations_remain_zero(self) -> None:
        measurements = self.development["measurements"]
        self.assertLessEqual(measurements["runtime_seconds"], 30)
        self.assertLessEqual(measurements["peak_RSS_bytes"], 256 * 1024 * 1024)
        self.assertLessEqual(measurements["public_output_bytes"], 1024 * 1024)
        self.assertEqual(measurements["temporary_generated_bytes"], 0)
        self.assertEqual(measurements["cpu_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertTrue(
            all(value == 0 for value in self.development["operation_counters"].values())
        )
        claims = self.development["claim_boundary"]
        self.assertEqual(claims["scientific_value"], "none_generated_engineering_only")
        self.assertTrue(
            all(value is False for key, value in claims.items() if key != "scientific_value")
        )

    def test_official_qualification_fails_before_output_without_future_proof(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "official.json"
            with self.assertRaises(experiment.CommLiveG0GeneratedRefusal) as caught:
                comm_live_g0_cli.main(["qualify", "--output", str(output)])
            self.assertEqual(
                caught.exception.refusal_id,
                "COMM-LIVE-G0-IMPLEMENTATION-PROOF-MISSING",
            )
            self.assertFalse(output.exists())
            self.assertFalse(
                output.with_name(f".{output.name}.comm-live-g0-consumed.json").exists()
            )

    def test_plan_and_inspect_cli_are_small_and_inspectable(self) -> None:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(comm_live_g0_cli.main(["plan"]), 0)
        cli_plan = json.loads(stdout.getvalue())
        self.assertEqual(cli_plan["required_adversarial_family_count"], 33)

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "development.json"
            path.write_bytes(experiment.canonical_json_bytes(self.development))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(
                    comm_live_g0_cli.main(["inspect", str(path)]), 0
                )
            inspected = json.loads(stdout.getvalue())
            self.assertEqual(inspected["lane_id"], "COMM-LIVE-G0")
            self.assertFalse(inspected["official_invocation_consumed"])
            self.assertEqual(inspected["adversarial_qualification"]["refusal_count"], 33)


if __name__ == "__main__":
    unittest.main()
