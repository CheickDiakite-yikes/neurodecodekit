from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit import bnci_c3c5_postmortem_cli as cli  # noqa: E402
from neurodecodekit.experiments import (  # noqa: E402
    bnci_2014_001_artifact_postmortem as postmortem,
)

CONTRACT_PATH = ROOT / postmortem.CONTRACT_RELATIVE_PATH
INPUT_PATH = ROOT / postmortem.INPUT_RELATIVE_PATH


class BNCIArtifactPostmortemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.stage_t = json.loads(INPUT_PATH.read_text(encoding="utf-8"))

    def test_contract_binds_one_exact_aggregate_artifact(self) -> None:
        source = self.contract["input_artifact"]
        self.assertEqual(source["path"], postmortem.INPUT_RELATIVE_PATH.as_posix())
        self.assertEqual(source["bytes"], 4_951)
        self.assertEqual(source["sha256"], postmortem.INPUT_SHA256)
        self.assertEqual(postmortem.CONTRACT_BYTES, len(CONTRACT_PATH.read_bytes()))
        self.assertEqual(
            postmortem.CONTRACT_SHA256,
            hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
        )
        self.assertEqual(self.contract["status"], "tier_a_post_outcome_artifact_only_protocol_frozen")
        self.assertFalse(self.contract["claim_boundary"]["root_cause_established"])
        self.assertTrue(all(value == 0 for value in self.contract["forbidden_operations"].values()))

    def test_exact_aggregate_produces_the_frozen_failure_map(self) -> None:
        result = postmortem.analyze_stage_t_aggregate(self.stage_t)
        c3 = result["C3_failure_map"]
        c5 = result["C5_failure_map"]
        self.assertAlmostEqual(
            c3["selected_E_minus_equal_prior_balanced_accuracy"],
            0.13348765432098764,
        )
        self.assertAlmostEqual(
            c3["selected_E_minus_posterior_EEG_balanced_accuracy"],
            -0.008873456790123468,
        )
        self.assertGreater(c3["selected_E_minus_equal_prior_log_loss"], 0.22)
        self.assertAlmostEqual(
            c5["P_plus_E_minus_P_balanced_accuracy"],
            0.015432098765432168,
        )
        states = {row["id"]: row["state"] for row in result["diagnostics"]}
        self.assertEqual(states["D1"], "supported_descriptively")
        self.assertEqual(states["D2"], "failed_posterior_control_outperformed_selected_E")
        self.assertEqual(states["D3"], "failed_selected_E_log_loss_worse_than_equal_prior")
        self.assertEqual(states["D4"], "weak_directional_only_not_validated")
        self.assertEqual(states["D5"], "failed")
        self.assertEqual(states["D6"], "unavailable_from_aggregate_artifact")
        self.assertFalse(result["root_cause_established"])

    def test_analysis_is_deterministic_and_does_not_mutate_input(self) -> None:
        original = copy.deepcopy(self.stage_t)
        first = postmortem.analyze_stage_t_aggregate(self.stage_t)
        second = postmortem.analyze_stage_t_aggregate(self.stage_t)
        self.assertEqual(first, second)
        self.assertEqual(self.stage_t, original)

    def test_malformed_or_plaintext_artifacts_fail_closed(self) -> None:
        malformed = copy.deepcopy(self.stage_t)
        malformed["route"] = "BNCIC3C5-R5"
        with self.assertRaises(postmortem.ArtifactPostmortemRefusal):
            postmortem.analyze_stage_t_aggregate(malformed)
        leaked = copy.deepcopy(self.stage_t)
        leaked["targets"] = [1, 2, 3]
        with self.assertRaises(postmortem.ArtifactPostmortemRefusal):
            postmortem._reject_plaintext_fields(leaked)

    def test_plan_and_cli_keep_the_operation_small(self) -> None:
        plan = postmortem.plan_postmortem()
        self.assertEqual(plan["input_bytes"], 4_951)
        self.assertEqual(plan["CPU_threads"], 1)
        self.assertEqual(plan["peak_RSS_bytes_maximum"], 256 * 1024**2)
        self.assertEqual(plan["model_runs"], 0)
        self.assertEqual(plan["target_reads"], 0)
        parser = cli.build_parser()
        self.assertEqual(parser.parse_args(["plan"]).command, "plan")
        self.assertEqual(parser.parse_args(["run"]).command, "run")

    def test_contract_drift_and_false_remote_proof_fail_closed(self) -> None:
        drifted = copy.deepcopy(self.contract)
        drifted["resource_caps"]["workers"] = 2
        with self.assertRaises(postmortem.ArtifactPostmortemRefusal):
            postmortem._validate_contract(drifted)
        proof = {
            "head_sha": "a" * 40,
            "remote_head_sha": "a" * 40,
            "CI_head_sha": "a" * 40,
            "CI_conclusion": "failure",
            "CI_run_id": 1,
            "base_python_job_id": 2,
            "base_python_job_name": "Base Python",
            "base_python_job_conclusion": "success",
            "optional_neuro_readers_job_id": 3,
            "optional_neuro_readers_job_name": "Optional Neuro Readers",
            "optional_neuro_readers_job_conclusion": "success",
        }
        with self.assertRaises(postmortem.ArtifactPostmortemRefusal):
            postmortem._collect_remote_green_proof(
                ROOT,
                head="a" * 40,
                collector=lambda _root: proof,
            )

    def test_complete_write_loop_and_no_clobber(self) -> None:
        payload = b"bounded-postmortem-output\n"
        real_write = os.write

        def short_writer(descriptor: int, view: memoryview) -> int:
            return real_write(descriptor, view[:3])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            postmortem._write_no_clobber(path, payload, writer=short_writer)
            self.assertEqual(path.read_bytes(), payload)
            with self.assertRaises(FileExistsError):
                postmortem._write_no_clobber(path, payload)

    def test_no_progress_write_cleans_only_its_new_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "result.json"
            with self.assertRaises(postmortem.ArtifactPostmortemRefusal):
                postmortem._write_no_clobber(
                    path,
                    b"payload",
                    writer=lambda _descriptor, _view: 0,
                )
            self.assertFalse(path.exists())

    def test_module_has_no_heavy_dependency_or_private_path(self) -> None:
        source = (SRC / "neurodecodekit/experiments/bnci_2014_001_artifact_postmortem.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "import mne",
            "import numpy",
            "import scipy",
            "import sklearn",
            "import torch",
            ".codex_work",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
