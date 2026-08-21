import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_f04_task_implication_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_f04_task_implication_result.v0.json"
PROOF_DOC_PATH = ROOT / "docs/MARC_2_F04_TASK_IMPLICATION_PROOF_CLOSEOUT.md"

EXPECTED_PROOF = {
    "commit": "fda3a3affc41a23997e19ea7a172e4d05e056a45",
    "CI_run_id": 32_481_785_128,
    "base_python_job_id": 96_769_521_785,
    "optional_neuro_job_id": 96_769_521_608,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR19A-G1",
    "preproof_implementation_registry_bytes": 4_799,
    "preproof_implementation_registry_sha256": (
        "243ec5f517a6e9485bab3ad0171e53fb1117bda17ccc6bb4bff9de2fb26ea45f"
    ),
    "preproof_result_registry_bytes": 3_211,
    "preproof_result_registry_sha256": (
        "3bd3c61ab6fff76f12ef671ae0a89c3cef4cef1806708147ffad69edaa086d54"
    ),
    "implementation_module_Git_blob": "f842450143ff4b99caea5452adf0065ec455aafc",
    "behavior_test_Git_blob": "4c005f58908ff301028903582309772ca49ee956",
    "implementation_document_Git_blob": (
        "74f837cd7c4d6393d91fb4373a3dea5daad1136b"
    ),
    "result_document_Git_blob": "9d02054358f7031cbf46763a6997547abc69ef5c",
    "preproof_implementation_registry_Git_blob": (
        "e4d7479a172832d115b128ed0f221eb87bc7da62"
    ),
    "preproof_result_registry_Git_blob": (
        "b0070eab91fd0183db749ff365238840104892d1"
    ),
    "preproof_record_test_Git_blob": "70a22566591377e11b149c2a9f8dbeba1af7ae9f",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2F04TaskImplicationProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.implementation = json.loads(
            IMPLEMENTATION_PATH.read_text(encoding="utf-8")
        )
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(
            self.implementation["remote_implementation_proof"], EXPECTED_PROOF
        )
        self.assertEqual(self.result["remote_implementation_proof"], EXPECTED_PROOF)

    def test_closeout_binds_all_preproof_git_blobs(self):
        text = PROOF_DOC_PATH.read_text(encoding="utf-8")
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, text)

    def test_closeout_repeats_nothing_and_opens_no_private_surface(self):
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
        self.assertNotIn("execute", self.implementation["surface"]["commands"])

    def test_next_gate_remains_non_private(self):
        self.assertIn("proof-only closeout", self.implementation["next_gate"])
        self.assertIn("proof-only closeout", self.result["next_gate"])
        self.assertFalse(self.result["claim_boundary"]["private_task_value_known"])
        self.assertEqual(self.result["claim_boundary"]["scientific_ceiling"], "none")


if __name__ == "__main__":
    unittest.main()
