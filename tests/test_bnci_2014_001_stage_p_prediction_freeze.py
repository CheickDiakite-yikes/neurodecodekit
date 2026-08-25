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

from neurodecodekit.evaluation import bnci_2014_001_stage_t_live as stage_t  # noqa: E402
from neurodecodekit.experiments import bnci_2014_001_stage_p_live as stage_p  # noqa: E402


FREEZE_PATH = ROOT / stage_p.PUBLIC_FREEZE_RELATIVE_PATH
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_P_RESULT.md"


class BNCIStagePPredictionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = FREEZE_PATH.read_bytes()
        cls.freeze = json.loads(cls.payload)

    def test_exact_public_artifact_identity(self) -> None:
        self.assertEqual(len(self.payload), 5_037)
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "468fd77f45645620ff2636a3b00f587986d1ce0f73c4cad88896a8bd9b354057",
        )
        stage_t.validate_public_freeze(self.freeze)

    def test_complete_target_blind_schedule_and_caps(self) -> None:
        counters = self.freeze["operation_counters"]
        self.assertEqual(counters["parameter_update_fits"], 468)
        self.assertEqual(counters["model_inference_runs"], 495)
        self.assertEqual(counters["prediction_sets"], 495)
        self.assertEqual(counters["target_deliveries"], 0)
        self.assertEqual(counters["scores"], 0)
        self.assertEqual(counters["post_target_updates"], 0)
        self.assertEqual(counters["reruns"], 0)
        self.assertEqual(self.freeze["private_prediction_rows"], 41_472)
        self.assertEqual(self.freeze["held_out_T_rows_used"], 0)
        self.assertTrue(all(self.freeze["acceptance_gates"].values()))

    def test_measured_resources_are_inside_registered_bounds(self) -> None:
        measured = self.freeze["measurements"]
        caps = self.freeze["registered_caps"]
        self.assertLessEqual(measured["runtime_seconds"], caps["runtime_seconds_maximum"])
        self.assertLessEqual(
            measured["peak_process_tree_RSS_bytes"],
            caps["peak_RSS_bytes_maximum"],
        )
        self.assertLessEqual(
            measured["private_generated_bytes"],
            caps["private_generated_bytes_maximum"],
        )
        self.assertLessEqual(measured["public_freeze_bytes"], caps["public_output_bytes_maximum"])
        self.assertEqual(caps["network_bytes"], 0)

    def test_only_aggregate_selection_is_public(self) -> None:
        self.assertEqual(
            self.freeze["aggregate_model_selection"],
            {
                "E1_selected_folds": 9,
                "E2_selected_folds": 0,
                "participant_level_selection_public": False,
            },
        )
        serialized = self.payload.decode("utf-8")
        for forbidden in (
            ".codex_work",
            "predictions.private",
            '"probabilities":',
            '"participant":',
            '"target":',
            "scoring_key_vault_sealed_until_T.private",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_claim_boundary_and_runtime_warning_are_explicit(self) -> None:
        self.assertFalse(self.freeze["scientific_claim_established"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("ConvergenceWarning", text)
        self.assertIn("exact warning count is unavailable", text)
        self.assertIn("targets remain sealed", text)


if __name__ == "__main__":
    unittest.main()
