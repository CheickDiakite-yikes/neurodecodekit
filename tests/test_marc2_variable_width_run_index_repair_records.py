import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries"
    / "marc2_variable_width_run_index_repair_implementation.v0.json"
)
RESULT_PATH = (
    ROOT / "registries" / "marc2_variable_width_run_index_repair_result.v0.json"
)
EXPECTED_REMOTE_PROOF = {
    "commit": "6f92b84c7be67848c7d09b567f13b08a14d33f5c",
    "CI_run_id": 32_459_984_049,
    "base_python_job_id": 96_704_807_926,
    "optional_neuro_job_id": 96_704_808_178,
    "both_required_jobs_green": True,
    "implementation_module_Git_blob": "92d9bc4c2de6c34d9f26e64d728e6eb85f465e5b",
    "behavior_test_Git_blob": "c9e8bf0526e2b79748cd3a9abde324b5c109038b",
    "implementation_document_Git_blob": "bba1f88ad459f9ec4a88ee7dd08f59e5c807b434",
    "result_document_Git_blob": "aa1b32659664c655f2dfd091279feaf77a623c57",
    "preproof_implementation_registry_Git_blob": "84d8babac29ebb5ae7eea4fe1153e643ecc39b77",
    "preproof_result_registry_Git_blob": "5f001092ee20284423747c6956469a3cd04b15a9",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operation_repeated_for_proof_closeout": False,
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2VariableWidthRunIndexRepairRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8"))
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_records_bind_the_same_lane_route_and_registration(self):
        self.assertEqual(self.implementation["lane_id"], "MARC2-VR16A")
        self.assertEqual(self.result["lane_id"], "MARC2-VR16A")
        self.assertEqual(self.result["route"], "MARC2VR16A-G1")
        self.assertEqual(
            self.implementation["green_registration_proof"],
            self.result["green_registration_proof"],
        )
        self.assertEqual(
            self.implementation["remote_implementation_proof"],
            EXPECTED_REMOTE_PROOF,
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_REMOTE_PROOF)
        self.assertFalse(
            self.implementation["local_verification"]["remote_CI_pending"]
        )

    def test_owned_artifact_sizes_and_hashes_are_exact(self):
        for artifact in self.implementation["tracked_implementation_artifacts"]:
            path = ROOT / artifact["path"]
            self.assertEqual(path.stat().st_size, artifact["bytes"])
            self.assertEqual(_sha256(path), artifact["sha256"])

    def test_measured_result_is_exact_and_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_input_bytes"], 17_532_166)
        self.assertEqual(measured["aggregate_output_bytes"], 2_843)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertLess(measured["runtime_seconds"], 30)
        self.assertLess(measured["peak_RSS_bytes"], 256 * 1024**2)
        self.assertLessEqual(measured["temporary_peak_bytes"], 2 * 1024**2)

    def test_matrix_and_refusal_evidence_is_exact(self):
        matrix = self.result["matrix"]
        self.assertEqual(matrix["success_paths"], 24)
        self.assertTrue(matrix["exact_replays_match"])
        self.assertEqual(matrix["distinct_raw_source_hashes"], 6)
        self.assertEqual(
            matrix["semantic_sha256"],
            "254bca5e0a39b52ca9791b917df6af554e02dda8f18f8e01b524d0e3ce8d9cba",
        )
        self.assertEqual(self.result["refusals"]["direct_refusals"], 50)

    def test_all_forbidden_counters_and_claims_remain_false(self):
        for record in (self.implementation, self.result):
            self.assertTrue(all(value == 0 for value in record["access_counters"].values()))
            boundary = record["claim_boundary"]
            self.assertEqual(boundary["scientific_ceiling"], "none")
            self.assertTrue(
                all(value is False for key, value in boundary.items() if key not in {"engineering_ceiling", "scientific_ceiling"})
            )

    def test_documents_state_generated_only_boundary(self):
        implementation_doc = (
            ROOT / "docs" / "MARC_2_VARIABLE_WIDTH_RUN_INDEX_REPAIR_IMPLEMENTATION.md"
        ).read_text(encoding="utf-8")
        result_doc = (
            ROOT / "docs" / "MARC_2_VARIABLE_WIDTH_RUN_INDEX_REPAIR_RESULT.md"
        ).read_text(encoding="utf-8")
        for text in (implementation_doc, result_doc):
            self.assertIn("generated", text.lower())
            self.assertIn("neural payload", text.lower())
            self.assertIn("scientific", text.lower())
        self.assertIn("real cohort is not established", result_doc)


if __name__ == "__main__":
    unittest.main()
