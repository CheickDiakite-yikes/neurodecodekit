import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / (
    "registries/dreyer_c5r_1_stage_h_l2_fixed_header_implementation.v0.json"
)
DOCUMENT = ROOT / "docs/DREYER_C5R_1_STAGE_H_L2_FIXED_HEADER_IMPLEMENTATION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DreyerStageHL2FixedHeaderImplementationRecordTests(unittest.TestCase):
    def test_implementation_record_binds_exact_code_and_measurements(self):
        record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(record["implementation_id"], "DREYER-C5R-1-HL2-I0")
        self.assertTrue(record["green_decision"]["both_required_jobs_green"])
        for artifact in record["tracked_implementation_artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"])
            self.assertEqual(_sha256(path), artifact["sha256"])
        result = record["generated_qualification"]
        self.assertEqual(result["transaction_case_count"], 32)
        self.assertEqual(result["attempt_count"], 33)
        self.assertEqual(result["accepted_H1_count"], 2)
        self.assertEqual(result["refusal_observation_count"], 31)
        self.assertEqual(result["retained_generated_payload_bytes"], 0)

    def test_implementation_preserves_real_and_scientific_barriers(self):
        record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(set(record["implementation_access_counters"].values()), {0})
        self.assertEqual(set(record["claim_boundary"].values()), {False})
        barriers = record["next_barriers"]
        self.assertEqual(barriers["registered_real_invocations_authorized_now"], 0)
        self.assertFalse(barriers["HL2_authority"])
        self.assertFalse(barriers["real_EDF_authority"])
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)


if __name__ == "__main__":
    unittest.main()
