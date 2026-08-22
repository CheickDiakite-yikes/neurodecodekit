import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_r5_two_route_discriminator_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_r5_two_route_discriminator_result.v0.json"
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_R5_TWO_ROUTE_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "661b18d896eef93cd1135c780b4cdca2e7917d04",
    "CI_run_id": 32_560_284_291,
    "base_python_job_id": 97_000_708_150,
    "optional_neuro_job_id": 97_000_708_047,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR21A-G1",
    "preproof_implementation_registry_bytes": 4_247,
    "preproof_implementation_registry_sha256": (
        "44865540ab27aa81a501a51b0ac79a6521723bd76ae3024ffe1ca465fc917399"
    ),
    "preproof_result_registry_bytes": 3_229,
    "preproof_result_registry_sha256": (
        "58a40fee0555f1ebac2e9452e3fd3a03f8e8c22f6a04d04978d8876c48876477"
    ),
    "implementation_module_Git_blob": "cf7d7152dda9f530dc1cb84679e90f1a8de22de0",
    "behavior_test_Git_blob": "13a5a0c09936d316c64c1b1d7a99140bc764ee1f",
    "implementation_document_Git_blob": (
        "85bbe0483219e70642d4f2a1cd9b882157cda922"
    ),
    "preproof_implementation_registry_Git_blob": (
        "5f8086ebd55397d8855fe6e1eec2ed22ab600765"
    ),
    "preproof_result_registry_Git_blob": (
        "05c7fee1ac9440ed302948c15d5e3cd7998f00cd"
    ),
    "preproof_record_test_Git_blob": "d0cc72da999dde6318c3ffb86857663d4b7950ca",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2R5TwoRouteDiscriminatorProofCloseoutTests(unittest.TestCase):
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
            self.implementation["next_gate"][
                "private_discriminator_or_source_read_authorized"
            ]
        )
        self.assertFalse(
            self.result["next_gate"]["private_or_neural_access_authorized"]
        )

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("private R5 branch remains", self.document)


if __name__ == "__main__":
    unittest.main()
