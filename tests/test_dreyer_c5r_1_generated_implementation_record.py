from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/dreyer_c5r_1_generated_implementation.v0.json"
DOC_PATH = ROOT / "docs/DREYER_C5R_1_GENERATED_IMPLEMENTATION.md"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class DreyerC5R1GeneratedImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_contract_and_green_preregistration_proof_are_exact(self) -> None:
        self.assertEqual(self.record["lane_id"], "DREYER-C5R-1")
        self.assertEqual(
            self.record["contract"]["sha256"],
            "ea6357a7b079aa3de885ef0a7c0e391c7810e2b94cbbb1702f934f65cc6b8fed",
        )
        proof = self.record["preregistration_green_proof"]
        self.assertEqual(
            proof["commit"], "8d72f8b43c3c4e2f135a7a0e8654e0cac64f6414"
        )
        self.assertEqual(proof["CI_run_id"], 32_927_671_087)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_artifact_set_hashes_every_exact_implementation_input(self) -> None:
        artifact_set = self.record["artifact_set"]
        rows = artifact_set["artifacts"]
        self.assertEqual(len(rows), artifact_set["artifact_count"])
        self.assertEqual(sum(row["bytes"] for row in rows), artifact_set["artifact_bytes"])
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
        self.assertEqual(
            hashlib.sha256(_canonical_bytes(rows)).hexdigest(),
            artifact_set["canonical_sha256"],
        )

    def test_real_schedule_and_command_boundary_are_exact(self) -> None:
        self.assertEqual(
            self.record["real_schedule"],
            {
                "outer_folds": 60,
                "parameter_update_fits": 4_740,
                "model_inference_runs": 3_660,
                "held_out_prediction_sets": 1_020,
                "held_out_prediction_rows": 81_600,
            },
        )
        capabilities = self.record["capabilities"]
        self.assertFalse(capabilities["real_execute_command"])
        self.assertFalse(capabilities["real_score_command"])

    def test_no_real_operation_or_registered_qualification_is_claimed(self) -> None:
        for key, value in self.record["access_counters"].items():
            self.assertEqual(value, 0, key)
        self.assertFalse(self.record["registered_generated_qualification"]["executed"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("one registered Stage G qualification has not run", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
