import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_published_task_selector_repair_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_published_task_selector_repair_result.v0.json"
IMPLEMENTATION_DOC = (
    ROOT / "docs/MARC_2_PUBLISHED_TASK_SELECTOR_REPAIR_IMPLEMENTATION.md"
)
RESULT_DOC = ROOT / "docs/MARC_2_PUBLISHED_TASK_SELECTOR_REPAIR_RESULT.md"


class Marc2PublishedTaskSelectorRepairRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_route_and_registration_proof_are_exact(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR20A")
        self.assertEqual(self.result["lane_id"], "MARC2-VR20A")
        self.assertEqual(self.result["route"], "MARC2VR20A-G1")
        expected = {
            "commit": "cd71807ac68f449796b6bc97745e9a0b200b2cd3",
            "CI_run_id": 32_484_725_113,
            "base_python_job_id": 96_778_573_327,
            "optional_neuro_job_id": 96_778_573_092,
            "both_required_jobs_green": True,
        }
        self.assertEqual(self.implementation["registration_proof"], expected)
        self.assertEqual(self.result["registration_proof"], expected)

    def test_owned_artifacts_are_byte_exact(self):
        bindings = self.implementation["owned_artifacts"]
        self.assertEqual(bindings, self.result["artifact_bindings"])
        for row in bindings:
            with self.subTest(path=row["path"]):
                payload = (ROOT / row["path"]).read_bytes()
                self.assertEqual(len(payload), row["bytes"])
                self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_matrix_identity_and_refusals_are_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["success_paths"], 20)
        self.assertEqual(matrix["selected_subjects"], 16)
        self.assertEqual(matrix["selected_run_bundles"], 96)
        self.assertEqual(matrix["selected_core_members"], 384)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertTrue(matrix["source_objects_immutable"])
        self.assertEqual(self.result["refusals"]["direct_refusals"], 53)
        self.assertEqual(sum(self.result["refusals"]["route_counts"].values()), 53)

    def test_measurements_are_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["fixed_input_bytes"], 232_361)
        self.assertEqual(measured["generated_input_bytes"], 17_273_948)
        self.assertEqual(measured["temporary_peak_bytes"], 885_477)
        self.assertEqual(measured["aggregate_output_bytes"], 3_050)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["runtime_seconds"], 1.7907995419809595)
        self.assertEqual(measured["peak_RSS_bytes"], 35_143_680)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)

    def test_authority_proof_and_claim_boundary_remain_closed(self):
        self.assertIsNone(self.implementation["remote_implementation_proof"])
        self.assertIsNone(self.result["remote_implementation_proof"])
        self.assertTrue(
            all(value == 0 for value in self.result["operation_counters"].values())
        )
        self.assertFalse(
            self.result["next_gate"]["private_confirmation_packet_eligible_now"]
        )
        claims = self.result["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value, key)

    def test_human_docs_separate_engineering_from_science(self):
        implementation = IMPLEMENTATION_DOC.read_text(encoding="utf-8")
        result = RESULT_DOC.read_text(encoding="utf-8")
        for text in (implementation, result):
            self.assertIn("Engineering capability", text)
            self.assertIn("Scientific claim not established", text)
        self.assertIn("source-exact", result)
        self.assertIn("no neural", result.lower())


if __name__ == "__main__":
    unittest.main()
