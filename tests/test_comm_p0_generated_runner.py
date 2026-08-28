from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import mock

from neurodecodekit import comm_p0_runner_cli
from neurodecodekit.experiments import comm_p0_generated as core
from neurodecodekit.experiments import comm_p0_generated_runner as runner


class CommP0GeneratedRunnerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.contract = core.load_contract(cls.root)

    def test_mutation_proof_runs_every_exact_family(self) -> None:
        observations = runner.exercise_mutation_refusals(self.contract)
        expected = {
            family
            for category in self.contract["adversarial_qualification"][
                "refusal_families"
            ].values()
            for family in category
        }
        self.assertEqual(len(observations), 70)
        self.assertEqual({row["family"] for row in observations}, expected)
        self.assertTrue(all(row["state_unchanged"] for row in observations))
        for row in observations:
            self.assertEqual(row["wrapper"], f"COMM-P0-G:{row['family']}")
            self.assertEqual(row["pre_state_sha256"], row["post_state_sha256"])

    def test_mutation_proof_is_deterministic(self) -> None:
        first = runner.exercise_mutation_refusals(self.contract)
        second = runner.exercise_mutation_refusals(self.contract)
        self.assertEqual(core.sha256_json(first), core.sha256_json(second))

    def test_child_environment_excludes_credentials_and_forces_threads(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, mock.patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "must-not-cross",
                "HTTPS_PROXY": "must-not-cross",
                "OMP_NUM_THREADS": "9",
            },
            clear=False,
        ):
            environment = runner._sanitized_child_environment(Path(temporary))
        self.assertNotIn("OPENAI_API_KEY", environment)
        self.assertNotIn("HTTPS_PROXY", environment)
        self.assertEqual(environment["OMP_NUM_THREADS"], "1")
        self.assertEqual(environment["PYTHONHASHSEED"], "0")

    def test_no_replace_publication_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            value = {"schema_name": runner.RESULT_SCHEMA, "gate_id": core.GATE_ID}
            runner.publish_no_replace(path, value)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), value)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "post_score_mutation_repeat_or_output_replacement",
            ):
                runner.publish_no_replace(path, value)

    def test_publication_refuses_symlink_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            real = root / "real"
            real.mkdir()
            link = root / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(
                core.CommP0GeneratedRefusal,
                "filesystem_capability_publication_or_cleanup_escape",
            ):
                runner.publish_no_replace(link / "result.json", {"gate_id": core.GATE_ID})

    def test_official_execution_remains_activation_locked(self) -> None:
        with self.assertRaisesRegex(
            core.CommP0GeneratedRefusal, "score_before_exact_green_freeze"
        ):
            runner.run_official_qualification("unused.json", root=self.root)

    def test_cli_plan_and_qualify_lock(self) -> None:
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(comm_p0_runner_cli.main(["plan"]), 0)
        self.assertFalse(json.loads(stdout.getvalue())["official_qualification_authorized_now"])

        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(
                comm_p0_runner_cli.main(
                    [
                        "qualify",
                        "--output",
                        "unused.json",
                        "--consumed-marker",
                        "unused-marker.json",
                    ]
                ),
                2,
            )
        self.assertIn("score_before_exact_green_freeze", stdout.getvalue())

    @unittest.skipUnless(
        importlib.util.find_spec("numpy") is not None
        and importlib.util.find_spec("sklearn") is not None,
        "requires the optional classical numerical stack",
    )
    def test_reduced_replay_pair_is_isolated_deterministic_and_target_free(self) -> None:
        environment = {
            **os.environ,
            "PYTHONPATH": str(self.root / "src"),
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "VECLIB_MAXIMUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "PYTHONHASHSEED": "0",
        }
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "neurodecodekit.comm_p0_runner_cli",
                "develop",
                "--participants-per-cohort",
                "3",
                "--timeout-seconds",
                "60",
            ],
            cwd=self.root,
            env=environment,
            capture_output=True,
            text=True,
            check=True,
            timeout=90,
        )
        result = json.loads(completed.stdout)
        self.assertEqual(result["isolated_child_process_replays"], 2)
        self.assertTrue(result["distinct_replay_worker_pids"])
        self.assertTrue(result["replay_equivalent"])
        self.assertEqual(result["refusal_observations"], 140)
        self.assertEqual(result["target_deliveries"], 4)
        self.assertEqual(result["scores"], 4)
        self.assertEqual(result["post_target_updates"], 0)
        self.assertEqual(result["network_bytes"], 0)
        self.assertEqual(result["retained_generated_payload_bytes_after_proof"], 0)
        self.assertFalse(result["end_to_end_latency_measured"])
        self.assertLess(
            result["peak_process_tree_RSS_bytes"],
            self.contract["resource_caps"]["peak_process_tree_RSS_bytes"],
        )
        core.assert_target_free(result)


if __name__ == "__main__":
    unittest.main()
