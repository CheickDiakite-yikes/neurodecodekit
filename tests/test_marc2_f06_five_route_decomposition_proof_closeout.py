import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_f06_five_route_decomposition_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_f06_five_route_decomposition_result.v0.json"
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_F06_FIVE_ROUTE_DECOMPOSITION_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "9e1b12139ad9cd9bcd2245a1eb74b85d7a3cbeeb",
    "CI_run_id": 32_596_999_769,
    "base_python_job_id": 97_089_462_251,
    "optional_neuro_job_id": 97_089_462_366,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR23A-G1",
    "preproof_implementation_registry_bytes": 4_819,
    "preproof_implementation_registry_sha256": (
        "a3391ea235a2b0019dce0d66299c864befdf825ab620e8fabafc1949d9591e49"
    ),
    "preproof_result_registry_bytes": 4_441,
    "preproof_result_registry_sha256": (
        "4e8906af52f485f3b8aeb2c0351728bedb949986e8827af110390eecf7f079d5"
    ),
    "implementation_module_Git_blob": "05a9d426e5b60009d959f8e436592c437a2b6eaa",
    "behavior_test_Git_blob": "a51dd78c00489e50cd7a9c9bced6555260e474d0",
    "implementation_record_test_Git_blob": (
        "326cf8a0a69df863fec6d85a1610dbcba23a4da7"
    ),
    "result_record_test_Git_blob": "d9363b3f094f83babb36f7152e3dd21d16f9aebd",
    "implementation_document_Git_blob": (
        "54e5d056463d73d09f21f1e4117a5f8055431031"
    ),
    "preproof_implementation_registry_Git_blob": (
        "bbbad7f29ac9b184fa4e5f5ec410cf3c3bdf1762"
    ),
    "preproof_result_registry_Git_blob": (
        "fe19f224b27cf3e08f144bfec237b40a310c868d"
    ),
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2F06FiveRouteDecompositionProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = PROOF_DOC_PATH.read_text(encoding="utf-8")

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.implementation["remote_implementation_proof"], EXPECTED_PROOF
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_PROOF)

    def test_closeout_binds_all_preproof_git_blobs(self):
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, self.document)

    def test_closeout_repeats_no_qualification_or_private_operation(self):
        self.assertFalse(
            EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        self.assertTrue(
            all(
                value == 0
                for value in self.implementation["operation_counters"].values()
            )
        )

    def test_private_packet_eligibility_has_delayed_effect(self):
        for record in (self.implementation, self.result):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["private_discriminator_packet_eligible_now"])
            self.assertTrue(
                gate[
                    "private_discriminator_packet_eligible_after_exact_closeout_green"
                ]
            )
        self.assertFalse(
            self.implementation["next_gate"]["private_or_neural_execution_authorized"]
        )
        self.assertFalse(
            self.result["next_gate"][
                "private_neural_target_model_score_FW2_or_CIL1_authorized"
            ]
        )

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("real VR22P F06 class remains unresolved", self.document)


if __name__ == "__main__":
    unittest.main()
