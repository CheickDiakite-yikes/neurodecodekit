import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_r5_inventory_taxonomy_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT / "registries/marc2_r5_inventory_taxonomy_discriminator_result.v0.json"
)
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_R5_INVENTORY_TAXONOMY_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "3f74be383a672748b0781d6571d28181056865b7",
    "CI_run_id": 32_611_864_949,
    "base_python_job_id": 97_126_099_642,
    "optional_neuro_job_id": 97_126_099_573,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR27A-G1",
    "preproof_implementation_registry_bytes": 3_886,
    "preproof_implementation_registry_sha256": (
        "d780256f8d29246155b940a6023bdc84e80b5b24361214c8def11b60e9790a0e"
    ),
    "preproof_result_registry_bytes": 3_379,
    "preproof_result_registry_sha256": (
        "833108079a430fdd2e58c45ba31e64c3a1f2d91b00fdc4786eb5f4611c900dd2"
    ),
    "implementation_module_Git_blob": "92ab6bd62138d1a2064552edffad86b4580881c6",
    "behavior_test_Git_blob": "4d7558b1c8c95f14c67dd2f67f9a6b364fd855fa",
    "registration_test_Git_blob": "c73077d5b6b3e2d95bd7aa2bb0d8f6edaedc11db",
    "preproof_record_test_Git_blob": "e3401a15812005c0e78ecf0ad85eaa4210e46047",
    "implementation_document_Git_blob": (
        "e339a7271eb4c35569a6c30a9128394e25fc82f5"
    ),
    "preproof_implementation_registry_Git_blob": (
        "09fc1524f9ec4b59475f87856daa3aee221e927f"
    ),
    "preproof_result_registry_Git_blob": (
        "43a4fbcacad7b60286976769565febd3aeabaa30"
    ),
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2R5InventoryTaxonomyDiscriminatorProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = PROOF_DOC_PATH.read_text(encoding="utf-8")

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.implementation["proof_barrier"]["remote_implementation_proof"],
            EXPECTED_PROOF,
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
