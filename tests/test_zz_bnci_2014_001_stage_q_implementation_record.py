from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/bnci_2014_001_stage_q_implementation.v0.json"
DOC_PATH = ROOT / "docs/BNCI_2014_001_STAGE_Q_IMPLEMENTATION.md"


class BNCIStageQImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_green_stage_a_binding(self) -> None:
        self.assertEqual(self.record["lane_id"], "BNCI-C3C5-1-Q")
        self.assertEqual(
            self.record["green_stage_a_result"]["commit"],
            "96d7f0569a54b05f8031d2e3943658ef598e38a5",
        )
        self.assertTrue(self.record["green_stage_a_result"]["both_required_jobs_green"])

    def test_scope_is_target_firewalled_and_model_free(self) -> None:
        scope = self.record["implementation_scope"]
        self.assertEqual(scope["sequential_verified_MAT_opens_maximum"], 18)
        self.assertTrue(scope["predictive_derivative_target_free"])
        self.assertEqual(scope["sealed_held_out_E_target_sets"], 9)
        self.assertEqual(scope["held_out_T_rows_exposed_per_fold"], 0)
        for field in ("analysis_network_bytes", "model_runs", "training_runs", "prediction_sets", "target_deliveries", "scores"):
            self.assertEqual(scope[field], 0)

    def test_resource_caps_and_claim_boundary(self) -> None:
        caps = self.record["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["private_derivative_bytes_maximum"], 536_870_912)
        self.assertEqual(caps["peak_RSS_bytes_maximum"], 1_073_741_824)
        self.assertFalse(self.record["claim_boundary"]["scientific_claim_established"])

    def test_declared_files_exist_and_unrelated_tracker_is_excluded(self) -> None:
        for relative in self.record["implementation_artifacts"]:
            self.assertTrue((ROOT / relative).is_file(), relative)
        self.assertNotIn(
            "docs/NEURODECODEKIT_20_LOOP_TRACKER.xlsx.inspect.ndjson",
            self.record["implementation_artifacts"],
        )
        self.assertTrue(DOC_PATH.is_file())

    def test_frozen_parent_hashes(self) -> None:
        for row in self.record["bound_public_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])


if __name__ == "__main__":
    unittest.main()
