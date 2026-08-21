import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/marc2_suffix_identity_private_discriminator_implementation_proof_closeout.v0.json"
)
EXPECTED_ARTIFACT_BINDINGS = [
    (
        "implementation_registry_with_remote_proof",
        "registries/marc2_suffix_identity_private_discriminator_implementation.v0.json",
        7357,
        "41b8de7c22546e5e630485b92557c5a63f094b77a0edd93e09e927dbd33d11f9",
        "86bbaca247f785bd3e67d928f4386b9a2aeb674e",
    ),
    (
        "implementation_module",
        "src/neurodecodekit/datasets/marc2_suffix_identity_private_discriminator.py",
        50366,
        "1bc86181b8eea40c77c5bd453dea5c8856dbf0b35427b6ff2f3692ed514a2b6e",
        "74d16480f28755ce6782205b12d08dc97972b00f",
    ),
    (
        "behavior_test",
        "tests/test_marc2_suffix_identity_private_discriminator.py",
        7707,
        "d45787f7eecc1f76a79c25d462581ff910c82bdb2a1569663529616495722c89",
        "00dcc942cf1746929905bca24ea52713f94a4fa8",
    ),
    (
        "implementation_document",
        "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_IMPLEMENTATION.md",
        3784,
        "b97267ad4b2c2abdbbc9233d02ca32773d3cd1c9999cc1a0fa0e1d7cf5c145bf",
        "a0eef3ad1779967314cf62b1b9ece4d8deeeeecb",
    ),
    (
        "generated_result_document",
        "docs/MARC_2_SUFFIX_IDENTITY_PRIVATE_DISCRIMINATOR_GENERATED_RESULT.md",
        2719,
        "8f5d6c8041d573eefa45b2f96639543fd7cf08b4a3233bea543d2d93d745f34c",
        "ba508fda8ee4933f3377dccce0c029e147f57500",
    ),
    (
        "implementation_record_test_with_remote_proof",
        "tests/test_marc2_suffix_identity_private_discriminator_implementation.py",
        5219,
        "951676d27afc58af31dbec622533d0880afb257c3b1ee24e315467c1c4f5adee",
        "27afdba54175b0872474ea6d1ffa51279b6bd326",
    ),
]


class Marc2SuffixIdentityPrivateDiscriminatorProofCloseoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_remote_implementation_proof_is_exact(self):
        proof = self.proof["implementation_remote_proof"]
        self.assertEqual(
            proof["commit"], "28a734df3fb0cb83c3cddb4994b76d8c9453830b"
        )
        self.assertEqual(proof["CI_run_id"], 32_454_196_219)
        self.assertEqual(proof["base_python_job_id"], 96_688_236_516)
        self.assertEqual(proof["optional_neuro_job_id"], 96_688_236_752)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_historical_artifact_binding_is_exact(self):
        rows = self.proof["exact_implementation_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 77_152)
        observed = [
            (row["role"], row["path"], row["bytes"], row["sha256"], row["Git_blob"])
            for row in rows
        ]
        self.assertEqual(observed, EXPECTED_ARTIFACT_BINDINGS)

    def test_closeout_repeats_nothing_and_touches_no_private_path(self):
        self.assertTrue(self.proof["qualification_not_repeated"])
        self.assertEqual(self.proof["proof_metadata_artifacts_updated"], 3)
        self.assertFalse(self.proof["activation_proof_created_now"])
        self.assertFalse(self.proof["private_execution_authorized_now"])
        self.assertTrue(
            all(value == 0 for value in self.proof["closeout_operations"].values())
        )

    def test_next_gate_requires_closeout_and_activation_green(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["this_closeout_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["separate_tracked_clean_activation_proof_required"])
        self.assertTrue(gate["activation_proof_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["explicit_one_shot_arming_required"])
        self.assertFalse(gate["private_source_or_readiness_access_authorized_now"])
        self.assertFalse(gate["FW2_or_CIL1_authorized"])

    def test_claim_boundary_is_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
