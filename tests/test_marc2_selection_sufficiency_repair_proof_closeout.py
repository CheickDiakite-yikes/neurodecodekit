import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION = json.loads(
    (ROOT / "registries/marc2_selection_sufficiency_repair_implementation.v0.json").read_text(
        encoding="utf-8"
    )
)
RESULT = json.loads(
    (ROOT / "registries/marc2_selection_sufficiency_repair_result.v0.json").read_text(
        encoding="utf-8"
    )
)
DOC = (ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_REPAIR_PROOF_CLOSEOUT.md").read_text(
    encoding="utf-8"
)

EXPECTED_PROOF = {
    "commit": "7ef4a8dface0c2a00e27b38f1f91b4043c12535f",
    "CI_run_id": 32_672_478_625,
    "base_python_job_id": 97_275_279_259,
    "optional_neuro_job_id": 97_275_279_380,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_invocations": 1,
    "preproof_implementation_registry_bytes": 7_182,
    "preproof_implementation_registry_sha256": (
        "81192cb39c126cf5e464d530b2a1724df0232421e9f6f8fede6777c1a5029645"
    ),
    "preproof_result_registry_bytes": 4_742,
    "preproof_result_registry_sha256": (
        "298676b47daa0ea62144cb98f46924bf3552b8847e4c76041d75a6f468fd385e"
    ),
    "implementation_module_Git_blob": "984e303a63255d909ae9eb4dd09c5f89f573570d",
    "behavior_test_Git_blob": "f0f9f4eeab2abf019f0370026ebea0b4d01bcd27",
    "registration_test_Git_blob": "7b2ea2c95ce8c3bf346041dff0d421164041f238",
    "surface_test_Git_blob": "ce34baac1af41964c1a5ca41cd0864962ce0ec2a",
    "result_record_test_Git_blob": "c76338bec65e33faa658b204b446b25c3d790b05",
    "implementation_record_test_Git_blob": "fd74d9141c8ac19bb0d25839b77aa6e6457cb3ce",
    "implementation_document_Git_blob": "f6b9b24b5a273583a20f23c5b2c807dde3601c01",
    "contract_Git_blob": "7490d781d4d640a82663bbd8c3cbbe5940e61aba",
    "preproof_implementation_registry_Git_blob": ("109ad2ff80c5037e394e88c198c2ce40863bf657"),
    "preproof_result_registry_Git_blob": "cec776feca9c22ffcb08e564e415e89ffffae68b",
    "live_domain_helper_Git_blob": "52f49b58345b1c6fad344306c9978eca70dc9d03",
    "published_task_helper_Git_blob": "33cd5e52d186a768ce8dc706e163c8d5c3a2fc92",
    "selection_firewall_helper_Git_blob": "d5394abea69547c321eaad2647e9bff0b0691ad5",
    "proof_test_additive_only": True,
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2SelectionSufficiencyRepairProofCloseoutTests(unittest.TestCase):
    def test_exact_remote_green_implementation_is_bound(self):
        self.assertEqual(IMPLEMENTATION["remote_implementation_proof"], EXPECTED_PROOF)
        self.assertEqual(RESULT["remote_implementation_proof"], EXPECTED_PROOF)

    def test_closeout_binds_all_preproof_git_blobs(self):
        for key, value in EXPECTED_PROOF.items():
            if key.endswith("Git_blob"):
                with self.subTest(key=key):
                    self.assertIn(value, DOC)

    def test_implementation_artifacts_remain_exact(self):
        self.assertEqual(
            IMPLEMENTATION["implementation_artifacts"][0]["sha256"],
            "9bed1d7a2d5350799ebf72712740895c48f8c59a827a0791c7fd1147f43391e1",
        )
        self.assertEqual(RESULT["qualification_invocations"], 1)
        self.assertFalse(RESULT["qualification_may_be_repeated"])

    def test_closeout_has_delayed_effect_and_no_private_authority(self):
        gate = IMPLEMENTATION["next_gate"]
        self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
        self.assertFalse(gate["generated_lane_remotely_closed_now"])
        self.assertTrue(gate["generated_lane_remotely_closed_after_exact_closeout_green"])
        self.assertFalse(gate["terminal_private_read_authorized"])
        self.assertFalse(EXPECTED_PROOF["generated_qualification_repeated_for_proof_closeout"])
        self.assertEqual(EXPECTED_PROOF["private_operations_during_proof_closeout"], 0)

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("freeze at least 12 participants", DOC)


if __name__ == "__main__":
    unittest.main()
