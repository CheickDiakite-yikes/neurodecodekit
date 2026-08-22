import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_selection_boundary_firewall_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_selection_boundary_firewall_result.v0.json"
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_SELECTION_BOUNDARY_FIREWALL_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "891245d73d8e11304d4a98e841ead6f57ad68ff8",
    "CI_run_id": 32_604_761_988,
    "base_python_job_id": 97_108_121_455,
    "optional_neuro_job_id": 97_108_121_321,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR25A-G1",
    "preproof_implementation_registry_bytes": 5_474,
    "preproof_implementation_registry_sha256": (
        "33fef70bed08a229d846fd8da49c1a7e7bc808d554ed9a6c3b4d98ce63bb03d3"
    ),
    "preproof_result_registry_bytes": 4_704,
    "preproof_result_registry_sha256": (
        "71d19f0bc22778ef1e3208821ccadad1c30df0078f54691e43c79e0064922c27"
    ),
    "implementation_module_Git_blob": "d5394abea69547c321eaad2647e9bff0b0691ad5",
    "behavior_test_Git_blob": "4bb6ecee067ad0827a4a4a84e864cb9736adacc3",
    "implementation_test_Git_blob": "df31491fcca83ed2175183749f71ab9fe2c8552a",
    "result_test_Git_blob": "569b8dbd647308db83e317a2f3a3b31c0a463500",
    "implementation_document_Git_blob": (
        "a7ba43d9fdc6b87dc50ad2b70d21039047a1ed53"
    ),
    "preproof_implementation_registry_Git_blob": (
        "f87786d0e9698bafb68893b4ff7c370be7832190"
    ),
    "preproof_result_registry_Git_blob": (
        "027bd428dee9bdb3606734bfceefc66fc14ce475"
    ),
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2SelectionBoundaryFirewallProofCloseoutTests(unittest.TestCase):
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

    def test_closeout_binds_every_preproof_git_blob(self):
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, self.document)

    def test_closeout_repeats_no_qualification_or_private_operation(self):
        self.assertFalse(
            EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"]
        )
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)
        for record in (self.implementation, self.result):
            self.assertTrue(
                all(value == 0 for value in record["operation_counters"].values())
            )

    def test_private_packet_eligibility_has_delayed_effect(self):
        for record in (self.implementation, self.result):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["private_confirmation_packet_eligible_now"])
            self.assertTrue(
                gate["private_confirmation_packet_eligible_after_exact_closeout_green"]
            )
            self.assertFalse(gate["private_access_or_real_executor_authorized"])
            self.assertFalse(gate["FW2_or_CIL1_authorized"])

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("no real cohort", self.document)


if __name__ == "__main__":
    unittest.main()
