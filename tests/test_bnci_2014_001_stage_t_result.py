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


RESULT_PATH = ROOT / stage_t.RESULT_RELATIVE_PATH
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_T_RESULT.md"


class BNCIStageTResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)

    def test_exact_public_result_identity_and_route(self) -> None:
        self.assertEqual(len(self.payload), 4_951)
        self.assertEqual(
            hashlib.sha256(self.payload).hexdigest(),
            "e836cefb9daf9df090f6f74a12ad90ae6448156d73850414fcca3367e81da9b2",
        )
        self.assertEqual(self.result["route"], "BNCIC3C5-R2")
        self.assertFalse(self.result["C3_passed"])
        self.assertFalse(self.result["C5_partial_passed"])

    def test_c3_near_miss_is_exact_and_not_upgraded(self) -> None:
        metrics = self.result["aggregate_metrics"]
        accuracy = metrics["participant_macro_balanced_accuracy"]
        self.assertAlmostEqual(accuracy["selected_E"], 0.38348765432098764)
        self.assertAlmostEqual(accuracy["timing_only"], 0.2966820987654321)
        self.assertAlmostEqual(accuracy["posterior_EEG"], 0.3923611111111111)
        self.assertAlmostEqual(metrics["C3_macro_no_signal_timing_margin"], 0.08680555555555552)
        self.assertAlmostEqual(metrics["C3_macro_control_margin"], -0.008873456790123468)
        self.assertEqual(metrics["C3_positive_participant_margins"], 5)
        self.assertAlmostEqual(metrics["C3_exact_one_sided_sign_flip_p"], 0.06640625)

    def test_c5_directional_gain_fails_every_registered_component(self) -> None:
        metrics = self.result["aggregate_metrics"]
        loss = metrics["participant_macro_log_loss"]
        self.assertLess(loss["P_plus_E"], loss["P"])
        self.assertLess(loss["P_plus_E"], loss["P_plus_D_E"])
        self.assertAlmostEqual(metrics["C5_macro_EOG_delta"], 0.025523996696223097)
        self.assertAlmostEqual(metrics["C5_macro_deranged_delta"], 0.018430851535548427)
        self.assertEqual(metrics["C5_positive_EOG_deltas"], 6)
        self.assertEqual(metrics["C5_positive_deranged_deltas"], 6)
        self.assertFalse(any(metrics["C5_partial_components"].values()))

    def test_one_score_resource_and_firewall_counters_are_exact(self) -> None:
        inventory = self.result["inventory"]
        counters = self.result["operation_counters"]
        self.assertEqual(inventory["participants"], 9)
        self.assertEqual(inventory["target_rows"], 2_592)
        self.assertEqual(inventory["prediction_rows"], 41_472)
        self.assertEqual(inventory["held_out_T_rows_used"], 0)
        self.assertEqual(counters["target_deliveries"], 1)
        self.assertEqual(counters["scores"], 1)
        self.assertEqual(counters["post_target_updates"], 0)
        self.assertEqual(counters["reruns"], 0)
        self.assertFalse(self.result["measurements"]["end_to_end_live_decoding_latency_measured"])
        self.assertFalse(self.result["rerun_allowed"])

    def test_public_result_is_aggregate_only_and_closeout_is_honest(self) -> None:
        serialized = self.payload.decode("utf-8")
        for forbidden in (
            ".codex_work",
            '"participant":',
            '"target":',
            '"probabilities":',
            "predictions.private",
        ):
            self.assertNotIn(forbidden, serialized)
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("real held-out EEG candidate did better than chance", text)
        self.assertIn("posterior EEG was 0.887 points", text)
        self.assertIn("better than selected EEG", text)
        self.assertIn("neither registered gate passed", text)


if __name__ == "__main__":
    unittest.main()
