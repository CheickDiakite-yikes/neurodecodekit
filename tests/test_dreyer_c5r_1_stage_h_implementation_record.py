from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/dreyer_c5r_1_stage_h_generated_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/DREYER_C5R_1_STAGE_H_PREFLIGHT_IMPLEMENTATION.md"


def _canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class DreyerC5R1StageHImplementationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_contract_and_stage_G_green_proof_are_exact(self) -> None:
        self.assertEqual(self.record["lane_id"], "DREYER-C5R-1-H")
        self.assertEqual(
            self.record["contract"]["sha256"],
            "5c2c795340bd90a5a361b4be47216d927fa918a474913d7d16af0310036252e9",
        )
        proof = self.record["stage_G_green_proof"]
        self.assertEqual(
            proof["commit"], "8f102541a9dd968b5f6574697ddbf7377b0a7372"
        )
        self.assertEqual(proof["CI_run_id"], 32_931_598_972)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_artifact_set_binds_every_exact_implementation_input(self) -> None:
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

    def test_generated_only_command_and_real_authority_boundary_are_exact(self) -> None:
        capabilities = self.record["capabilities"]
        self.assertTrue(capabilities["generated_mock_adversarial_qualification"])
        self.assertFalse(capabilities["base_dependency_added"])
        self.assertFalse(capabilities["live_network_opener"])
        self.assertFalse(capabilities["real_execute_command"])
        self.assertFalse(self.record["proposed_real_stage_H"]["authority_active"])

    def test_no_real_operation_or_registered_qualification_is_claimed(self) -> None:
        for key, value in self.record["access_counters"].items():
            self.assertEqual(value, 0, key)
        self.assertFalse(self.record["registered_generated_qualification"]["executed"])
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("No real request", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
