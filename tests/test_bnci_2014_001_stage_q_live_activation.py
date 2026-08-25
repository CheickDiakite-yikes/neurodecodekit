from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.datasets import bnci_2014_001_stage_q as core  # noqa: E402
from neurodecodekit.datasets import bnci_2014_001_stage_q_live as live  # noqa: E402


ACTIVATION_PATH = ROOT / live.LIVE_ACTIVATION_RELATIVE_PATH
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_Q_LIVE_ACTIVATION.md"


class BNCIStageQLiveActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.activation = json.loads(ACTIVATION_PATH.read_text(encoding="utf-8"))

    def test_schema_and_green_predecessors_are_exact(self) -> None:
        validated = live.validate_activation_document(self.activation)
        self.assertEqual(validated["lane_id"], core.LANE_ID)
        green = validated["green_implementation"]
        self.assertEqual(green["commit"], "e5ca6a24f65beab12b89eddad938c96fe4ecaf00")
        self.assertEqual(green["CI_head_sha"], green["commit"])
        self.assertEqual(green["CI_run_id"], 32_822_604_745)
        self.assertEqual(green["base_python_job_id"], 97_723_744_136)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97_723_744_450)
        self.assertTrue(green["both_required_jobs_green"])

    def test_every_implementation_artifact_matches_green_commit(self) -> None:
        commit = self.activation["green_implementation"]["commit"]
        for row in self.activation["implementation_artifacts"]:
            committed = subprocess.run(
                ["git", "show", f"{commit}:{row['path']}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(len(committed), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(committed).hexdigest(), row["sha256"], row["path"]
            )

    def test_qualified_runtime_artifacts_remain_byte_identical(self) -> None:
        commit = self.activation["green_implementation"]["commit"]
        runtime_paths = {
            row["path"]
            for row in self.activation["implementation_artifacts"]
            if not row["path"].startswith("tests/")
        }
        for path in runtime_paths:
            committed = subprocess.run(
                ["git", "show", f"{commit}:{path}"],
                cwd=ROOT,
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual((ROOT / path).read_bytes(), committed, path)

    def test_authority_is_one_Q_only_and_scientific_work_remains_closed(self) -> None:
        authority = self.activation["authority"]
        self.assertTrue(authority["one_live_Stage_Q_execution"])
        for field in (
            "network_bytes",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
            "reruns",
        ):
            self.assertEqual(authority[field], 0, field)
        self.assertFalse(authority["Stage_P"])
        self.assertFalse(authority["Stage_T"])
        self.assertFalse(authority["claim_upgrade"])

    def test_activation_document_states_delayed_effect_and_claim_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("delayed effect", text)
        self.assertIn("both required CI jobs pass", text)
        self.assertIn("has not", text)
        self.assertIn("EEG beyond", text)
        self.assertFalse((ROOT / core.ACTIVATION_RELATIVE_PATH).exists())


if __name__ == "__main__":
    unittest.main()
