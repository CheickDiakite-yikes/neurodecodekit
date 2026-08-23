import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_r1_inventory_distribution_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries/marc2_r1_inventory_distribution_discriminator_result.v0.json"
)
PROOF_DOC_PATH = (
    ROOT
    / "docs/MARC_2_R1_INVENTORY_DISTRIBUTION_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "2e73c9176d243b5deccbf8416bb59fdf053ba762",
    "CI_run_id": 32_620_018_855,
    "base_python_job_id": 97_146_675_300,
    "optional_neuro_job_id": 97_146_675_166,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR29A-G1",
    "preproof_implementation_registry_bytes": 4_663,
    "preproof_implementation_registry_sha256": (
        "10325d417cb6a5ce6edda91fcc6db2c1857bff71ef6536388d9e6f4e262f4775"
    ),
    "preproof_result_registry_bytes": 4_007,
    "preproof_result_registry_sha256": (
        "b50dc18ef56c2c2875bee48103f32a23763880637ddfd390d4b29ab7ef82adb5"
    ),
    "implementation_module_Git_blob": "8734b5fb860717a9caf68187e47cbaf94b456f9c",
    "behavior_test_Git_blob": "77f0807769f062cd81150de29b1f34ffadec4376",
    "registration_test_Git_blob": "8153668a780547a5d7e4e7959f66375ee7d30e57",
    "implementation_record_test_Git_blob": (
        "440a38a54da0c7ebf64b04708ba7fa1d0d6a5b4a"
    ),
    "result_record_test_Git_blob": "d40e19c19ea149be98f2224fa73c51fa464e8b84",
    "implementation_document_Git_blob": "d3251b3adb24859178f6d3a8e3bff345ab3211a7",
    "preproof_implementation_registry_Git_blob": (
        "91f1e96f1973c3314bbd29955591b35b58fc2bb4"
    ),
    "preproof_result_registry_Git_blob": (
        "0ca4048062fbf42c0b03a02e75fcf7298926d48b"
    ),
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2R1InventoryDistributionDiscriminatorProofCloseoutTests(
    unittest.TestCase
):
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
        self.assertIn("private R1 subclass remains", self.document)


if __name__ == "__main__":
    unittest.main()
