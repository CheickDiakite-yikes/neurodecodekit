import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_f04_task_implication_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_f04_task_implication_result.v0.json"


class Marc2F04TaskImplicationRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_and_registration_proof_are_exact(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR19A")
        self.assertEqual(self.result["route"], "MARC2VR19A-G1")
        proof = self.result["green_registration_proof"]
        self.assertEqual(
            proof["commit"], "9365b0ff7bfd5dbd3b37217a80ab01e6770de212"
        )
        self.assertEqual(proof["CI_run_id"], 32_480_420_157)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_owned_artifacts_are_byte_exact(self):
        rows = self.implementation["owned_artifacts"]
        self.assertEqual(len(rows), self.implementation["owned_artifact_count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows),
            self.implementation["owned_artifact_bytes"],
        )
        for row in rows:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_static_matrix_and_measurements_are_exact(self):
        self.assertEqual(self.result["static_audit"]["F04_producer_references"], 2)
        matrix = self.result["matrix"]
        self.assertEqual(matrix["paths"], 32)
        self.assertEqual(matrix["VR16A_calls"], 32)
        self.assertEqual(sum(matrix["route_counts"].values()), 32)
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 13_748_732)
        self.assertEqual(measured["aggregate_output_bytes"], 2_326)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)

    def test_hypotheses_pass_and_forbidden_counters_are_zero(self):
        self.assertTrue(all(self.result["hypotheses"].values()))
        self.assertEqual(self.result["direct_refusals"], 40)
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        proof = self.result["remote_implementation_proof"]
        self.assertEqual(self.implementation["remote_implementation_proof"], proof)
        self.assertEqual(
            proof["commit"], "fda3a3affc41a23997e19ea7a172e4d05e056a45"
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["generated_qualification_repeated_for_proof_closeout"])
        self.assertEqual(proof["private_operations_during_proof_closeout"], 0)

    def test_documents_preserve_private_and_scientific_boundary(self):
        for name in (
            "MARC_2_F04_TASK_IMPLICATION_IMPLEMENTATION.md",
            "MARC_2_F04_TASK_IMPLICATION_RESULT.md",
        ):
            text = (ROOT / "docs" / name).read_text(encoding="utf-8")
            self.assertIn("private", text.lower())
            self.assertIn("neural", text.lower())
            self.assertIn("task", text.lower())
        boundary = self.result["claim_boundary"]
        self.assertEqual(boundary["scientific_ceiling"], "none")
        self.assertFalse(boundary["private_task_value_known"])
        self.assertFalse(boundary["decoding_accuracy"])


if __name__ == "__main__":
    unittest.main()
