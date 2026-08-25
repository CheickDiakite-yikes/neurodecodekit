from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/bnci_2014_001_stage_q_generated_result.v0.json"
IMPLEMENTATION_PATH = ROOT / "registries/bnci_2014_001_stage_q_implementation.v0.json"


class BNCIStageQGeneratedResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = RESULT_PATH.read_bytes()
        cls.result = json.loads(cls.payload)
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))

    def test_identity_status_and_consumption(self) -> None:
        self.assertEqual(self.result["lane_id"], "BNCI-C3C5-1-Q")
        self.assertEqual(self.result["status"], "passed_generated_only_no_private_or_real_operation")
        self.assertFalse(self.result["qualification_may_be_repeated"])
        self.assertFalse(self.result["scientific_claim_established"])
        self.assertEqual(len(self.result["case_classes"]), 6)

    def test_generated_shape_and_resources(self) -> None:
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_calibration_structs"], 3)
        self.assertEqual(measured["generated_task_runs"], 6)
        self.assertEqual(measured["generated_trials"], 288)
        self.assertLessEqual(measured["runtime_seconds"], 3600)
        self.assertLessEqual(measured["peak_process_RSS_bytes"], 1_073_741_824)

    def test_every_real_scientific_counter_is_zero(self) -> None:
        operations = self.result["operations"]
        for field in (
            "real_or_private_path_opens",
            "real_MAT_semantic_opens",
            "network_bytes",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "target_deliveries",
            "scores",
        ):
            self.assertEqual(operations[field], 0, field)

    def test_implementation_binds_exact_result(self) -> None:
        bound = self.implementation["generated_qualification"]
        self.assertEqual(bound["result_bytes"], len(self.payload))
        self.assertEqual(bound["result_sha256"], hashlib.sha256(self.payload).hexdigest())
        self.assertTrue(bound["may_be_repeated"] is False)


if __name__ == "__main__":
    unittest.main()
