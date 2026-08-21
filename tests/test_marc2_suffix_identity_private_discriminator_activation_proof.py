import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_implementation_proof.v0.json"
)
EXPECTED_CLOSEOUT_BINDINGS = [
    (
        "proof_closeout_document",
        "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_PROOF_CLOSEOUT.md",
        2201,
        "2ee4f4fe3f7dded335667d9d9200a4f84fe05683312297eb192f0f6b5c5541ea",
        "44163d1bc0ef3e741146bf32b93032ad1bcb64dc",
    ),
    (
        "proof_closeout_machine_record",
        "registries/marc2_suffix_identity_private_discriminator_implementation_proof_closeout.v0.json",
        4196,
        "2e9b4b572a7ff1bfc724310f119f8742a124929c95ac6a22034054af1ff775e2",
        "b38a7f6ea0b3a3d8438fc1470f658ba0014ab0d2",
    ),
    (
        "proof_closeout_test",
        "tests/test_marc2_suffix_identity_private_discriminator_implementation_proof_closeout.py",
        3116,
        "f85a7a9d69ef616701ea65a67f7c5a57829485c949ac9b626ae04764df24fa88",
        "56506c1b2582a0b7350ca6f6a1f5bb33d2d7cdb2",
    ),
]


class Marc2SuffixIdentityPrivateDiscriminatorActivationProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_exact_green_barriers_are_bound(self):
        self.assertEqual(
            self.proof["implementation_commit"],
            "28a734df3fb0cb83c3cddb4994b76d8c9453830b",
        )
        self.assertEqual(self.proof["implementation_CI_run_id"], 32_454_196_219)
        self.assertEqual(
            self.proof["implementation_base_python_job_id"], 96_688_236_516
        )
        self.assertEqual(
            self.proof["implementation_optional_neuro_job_id"], 96_688_236_752
        )
        self.assertTrue(self.proof["implementation_both_required_jobs_green"])
        self.assertEqual(
            self.proof["proof_closeout_commit"],
            "2acfb3318beb46ade294fdc3ff0fc21765e3ea17",
        )
        self.assertEqual(self.proof["proof_closeout_CI_run_id"], 32_454_892_777)
        self.assertEqual(
            self.proof["proof_closeout_base_python_job_id"], 96_690_180_933
        )
        self.assertEqual(
            self.proof["proof_closeout_optional_neuro_job_id"], 96_690_181_096
        )
        self.assertTrue(self.proof["proof_closeout_both_required_jobs_green"])

    def test_historical_closeout_binding_is_exact(self):
        rows = self.proof["exact_bound_closeout_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 9_513)
        observed = [
            (row["role"], row["path"], row["bytes"], row["sha256"], row["Git_blob"])
            for row in rows
        ]
        self.assertEqual(observed, EXPECTED_CLOSEOUT_BINDINGS)

    def test_activation_itself_performs_no_private_operation(self):
        self.assertTrue(
            all(value == 0 for value in self.proof["activation_operations"].values())
        )
        gate = self.proof["execution_gate"]
        self.assertTrue(gate["this_activation_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["tracked_and_clean_activation_record_required"])
        self.assertTrue(gate["exact_one_shot_arm_required"])
        self.assertFalse(gate["private_access_authorized_before_this_record_is_remotely_green"])

    def test_private_scope_is_single_fixed_and_aggregate_only(self):
        self.assertTrue(self.proof["private_structural_content_open_authorized"])
        self.assertEqual(self.proof["private_structural_content_open_count"], 1)
        self.assertEqual(self.proof["private_structural_bytes"], 418_755)
        self.assertEqual(self.proof["strict_JSON_parse_count"], 1)
        self.assertEqual(self.proof["VR15A_call_count"], 1)
        self.assertEqual(self.proof["nested_VR12A_call_count"], 1)
        self.assertEqual(
            self.proof["allowed_aggregate_routes"],
            [f"MARC2VR15P-R{index}" for index in range(1, 17)],
        )
        self.assertFalse(self.proof["cohort_manifest_allowed"])
        self.assertFalse(self.proof["retry_rerun_resume_allowed"])
        self.assertFalse(self.proof["execution_gate"]["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
