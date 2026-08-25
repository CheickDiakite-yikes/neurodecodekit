from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from neurodecodekit.experiments import bnci_2014_001_stage_p_live as stage_p  # noqa: E402


ACTIVATION_PATH = ROOT / stage_p.ACTIVATION_RELATIVE_PATH
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_P_LIVE_ACTIVATION.md"


class BNCIStagePActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.activation = json.loads(ACTIVATION_PATH.read_text(encoding="utf-8"))

    def test_schema_and_green_predecessors_are_exact(self) -> None:
        value = stage_p.validate_activation_document(self.activation)
        self.assertEqual(
            value["green_implementation"]["commit"],
            "7ba4f7c30f260bc7603e8928ad8d9ff010e54872",
        )
        self.assertEqual(value["green_implementation"]["CI_run_id"], 32_906_104_408)
        self.assertEqual(value["green_implementation"]["base_python_job_id"], 97_990_455_561)
        self.assertEqual(
            value["green_implementation"]["optional_neuro_readers_job_id"],
            97_990_455_765,
        )
        self.assertTrue(value["green_implementation"]["both_required_jobs_green"])

    def test_every_implementation_artifact_identity_is_bound(self) -> None:
        for row in self.activation["implementation_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(
                row,
                {
                    "path": row["path"],
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                },
            )

    def test_authority_stops_before_targets_and_scoring(self) -> None:
        authority = self.activation["authority"]
        self.assertTrue(authority["one_real_Stage_P_execution"])
        self.assertFalse(authority["held_out_E_target_delivery"])
        self.assertFalse(authority["held_out_T_signal_or_target_delivery"])
        self.assertFalse(authority["Stage_T"])
        self.assertEqual(authority["reruns"], 0)
        self.assertEqual(authority["post_target_updates"], 0)
        self.assertFalse(authority["claim_upgrade"])

    def test_document_states_delayed_effect_and_next_barrier(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("delayed effect", text)
        self.assertIn("both required CI jobs pass", text)
        self.assertIn("hash-only prediction freeze", text)
        self.assertIn("has not run a real model", text)


if __name__ == "__main__":
    unittest.main()
