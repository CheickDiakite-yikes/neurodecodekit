import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENTATION_PATH = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_implementation.v0.json"
)
RESULT_PATH = (
    ROOT
    / "registries/marc2_r1_eligible_total_direction_discriminator_result.v0.json"
)
PROOF_DOC_PATH = (
    ROOT
    / "docs/MARC_2_R1_ELIGIBLE_TOTAL_DIRECTION_DISCRIMINATOR_PROOF_CLOSEOUT.md"
)

EXPECTED_PROOF = {
    "commit": "3553fa4f7d3d7e4b5e3813ac3f6219cf6ba759ab",
    "CI_run_id": 32_627_856_478,
    "base_python_job_id": 97_165_896_566,
    "optional_neuro_job_id": 97_165_896_610,
    "both_required_jobs_green": True,
    "scope_changed_after_qualification": False,
    "qualification_route": "MARC2VR31A-G1",
    "preproof_implementation_registry_bytes": 4_817,
    "preproof_implementation_registry_sha256": (
        "b613b3374462b0aad7eaea248f7f35f619a7cd3f726b26e786b1d64fdc928c3f"
    ),
    "preproof_result_registry_bytes": 3_546,
    "preproof_result_registry_sha256": (
        "6c65e6cd76b7da53f448b5169046bc292198c861349728538d81df7bdab6cf2d"
    ),
    "implementation_module_Git_blob": "8b9df9724872ab9925cee58995939f40892bfc4b",
    "behavior_test_Git_blob": "ace0be65ea0dfa088b137019588b521427f8d105",
    "registration_test_Git_blob": "e3426e948162d7c8b50d6a851f90c56d0ff570cf",
    "implementation_record_test_Git_blob": (
        "b8acca186c187a785e7e8e7fed509aab53c2709a"
    ),
    "result_record_test_Git_blob": "ab60423aaf7e66735a1c2216bf31502231a90917",
    "implementation_document_Git_blob": "594adc60fd41c1846736b7e3c5d9053be309cd3a",
    "preproof_implementation_registry_Git_blob": (
        "7324dbc2138afccdaf90d4f1eeed8d6e9ea0beb3"
    ),
    "preproof_result_registry_Git_blob": (
        "2abfaaa6f327531be3945b08e1b23936aa5ea2ee"
    ),
    "generated_qualification_repeated_for_proof_closeout": False,
    "private_operations_during_proof_closeout": 0,
}


class Marc2R1EligibleTotalDirectionDiscriminatorProofCloseoutTests(
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
            self.assertFalse(gate["private_direction_packet_eligible_now"])
            self.assertTrue(
                gate[
                    "private_direction_packet_eligible_after_exact_closeout_green"
                ]
            )
        self.assertFalse(
            self.implementation["next_gate"][
                "private_direction_or_source_read_authorized"
            ]
        )
        self.assertFalse(
            self.result["next_gate"]["private_or_neural_access_authorized"]
        )

    def test_document_separates_engineering_and_scientific_claims(self):
        self.assertIn("Engineering capability added", self.document)
        self.assertIn("Scientific claim not established", self.document)
        self.assertIn("private direction remains", self.document)


if __name__ == "__main__":
    unittest.main()
