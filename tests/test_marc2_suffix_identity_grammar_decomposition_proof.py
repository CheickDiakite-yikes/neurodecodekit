import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_suffix_identity_grammar_decomposition_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_suffix_identity_grammar_decomposition_result.v0.json"
PROOF_PATH = ROOT / "docs/MARC_2_SUFFIX_IDENTITY_GRAMMAR_DECOMPOSITION_PROOF_CLOSEOUT.md"
EXPECTED_BLOBS = {
    "implementation_module_Git_blob": "1709cfb2021859c14990f4eb28f1e50ba7bbb6ba",
    "behavior_test_Git_blob": "5283802921f09bdac833e818c943aad4117ab341",
    "record_test_Git_blob": "93e4eef2e4ba6fe39b0152aa8442f51a864d8abf",
    "implementation_document_Git_blob": "c89c4c24078cec33da81d131b3b456316faad96e",
    "result_document_Git_blob": "46ca59a470436b3068ad469ac19f4b377b7398da",
    "preproof_implementation_registry_Git_blob": "c7c15db577ca55c04276c33f0ed7533dadbbca9f",
    "preproof_result_registry_Git_blob": "6078c74b2b38e693474f3f3a5cfe0967ac6accfb",
}


class Marc2SuffixIdentityGrammarProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = (
            json.loads(IMPLEMENTATION_PATH.read_text(encoding="utf-8")),
            json.loads(RESULT_PATH.read_text(encoding="utf-8")),
        )

    def test_remote_proof_is_exact_in_both_records(self):
        for record in self.records:
            proof = record["remote_implementation_proof"]
            self.assertEqual(proof["commit"], "bfb0dcb7752433b4af841d57bbfcbf613a341124")
            self.assertEqual(proof["CI_run_id"], 32_449_260_503)
            self.assertEqual(proof["base_python_job_id"], 96_674_484_190)
            self.assertEqual(proof["optional_neuro_job_id"], 96_674_484_279)
            self.assertTrue(proof["both_required_jobs_green"])

    def test_git_blob_bindings_are_exact(self):
        for record in self.records:
            proof = record["remote_implementation_proof"]
            for key, value in EXPECTED_BLOBS.items():
                self.assertEqual(proof[key], value, key)

    def test_closeout_repeats_no_evidence_operation(self):
        for record in self.records:
            proof = record["remote_implementation_proof"]
            self.assertFalse(proof["generated_qualification_repeated_for_proof_closeout"])
            self.assertFalse(proof["private_operation_repeated_for_proof_closeout"])
            self.assertTrue(all(value == 0 for value in record["access_counters"].values()))

    def test_next_gate_is_eligible_but_not_authorized(self):
        for record in self.records:
            gate = record["next_gate"]
            self.assertTrue(
                gate["exact_implementation_and_result_commit_push_and_both_jobs_green_satisfied"]
            )
            self.assertFalse(gate["future_private_discriminator_authorized"])
            self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_human_proof_names_exact_remote_evidence(self):
        text = PROOF_PATH.read_text(encoding="utf-8")
        self.assertIn("bfb0dcb7752433b4af841d57bbfcbf613a341124", text)
        self.assertIn("96674484190", text)
        self.assertIn("96674484279", text)
        self.assertIn("32449260503", text)
        self.assertIn("No private read is authorized", text)


if __name__ == "__main__":
    unittest.main()
