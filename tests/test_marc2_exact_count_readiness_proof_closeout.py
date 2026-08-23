import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT / "registries/marc2_exact_count_readiness_repair_implementation.v0.json"
)
RESULT_PATH = ROOT / "registries/marc2_exact_count_readiness_repair_result.v0.json"
PROOF_DOC_PATH = (
    ROOT / "docs/MARC_2_EXACT_COUNT_READINESS_REPAIR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "92baa516b5e0bc16e75a8bc05c57b057b3c3bf73",
    "CI_run_id": 32_635_352_814,
    "base_python_job_id": 97_184_143_923,
    "optional_neuro_job_id": 97_184_144_015,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR33A-G1",
    "preproof_implementation_registry_bytes": 4_414,
    "preproof_implementation_registry_sha256": (
        "fde699a125df38c08f6f4bfee76751a9f77ed5fb257227176283f4a2cf820f90"
    ),
    "preproof_result_registry_bytes": 2_865,
    "preproof_result_registry_sha256": (
        "f490c52e0ac13fb624aa44f969acd86ac61bc62d9da6f552f0efbd4298c395ff"
    ),
    "implementation_module_Git_blob": "b6bf1989f116669e06e3abc47e70136d4aa6bbff",
    "behavior_test_Git_blob": "c1716d4313ab65ee7a52ec45e917c688ac43863a",
    "registration_test_Git_blob": "50380975ea7d31bb57303cee036363542e7152ed",
    "result_record_test_Git_blob": "ce1e128f33c75cded26b96824b1cdaacb8198741",
    "implementation_document_Git_blob": "ee2034b08ed6ad7a03364c05501857fe60265c05",
    "contract_Git_blob": "0fa8be94c54bf8fc34533b89843f0843ea1dfd40",
    "preproof_implementation_registry_Git_blob": (
        "6559ebdd9e264930ae61fac3410cdb165db44e82"
    ),
    "preproof_result_registry_Git_blob": "4b80d0df1bd11ac9120c804342762a3f5546a5ab",
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2ExactCountReadinessProofCloseoutTests(unittest.TestCase):
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

    def test_generated_closeout_has_delayed_effect(self):
        for record in (self.implementation, self.result):
            gate = record["next_gate"]
            self.assertTrue(gate["proof_only_closeout_commit_green_pending"])
            self.assertFalse(gate["generated_lane_remotely_closed_now"])
            self.assertTrue(
                gate["generated_lane_remotely_closed_after_exact_closeout_green"]
            )
            self.assertFalse(gate["qualification_may_be_repeated"])

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("cannot", self.document)
        self.assertIn("retry", self.document)


if __name__ == "__main__":
    unittest.main()
