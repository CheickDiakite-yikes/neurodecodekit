import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries"
    / "marc2_first_failure_stable_private_discriminator_request_proof.v0.json"
)


class Marc2FirstFailureStablePrivateDiscriminatorRequestProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_request_remote_proof_is_exact(self):
        proof = self.proof["request_remote_proof"]
        self.assertEqual(
            proof["commit"], "521f1de1f3141f3f970710447d072608253c2cca"
        )
        self.assertEqual(proof["CI_run_id"], 32_474_183_647)
        self.assertEqual(proof["base_python_job_id"], 96_747_013_517)
        self.assertEqual(proof["optional_neuro_job_id"], 96_747_013_910)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_request_artifact_matches_bytes_hash_and_git_blob(self):
        rows = self.proof["exact_request_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 32_886)
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_scope_is_unchanged_and_still_all_false(self):
        scope = self.proof["scope_unchanged"]
        self.assertEqual(scope["fixed_input_count"], 20)
        self.assertEqual(scope["fixed_input_bytes"], 315_255)
        self.assertEqual(scope["future_private_source_bytes"], 418_755)
        self.assertEqual(scope["future_VR16A_calls"], 1)
        self.assertEqual(scope["future_VR17C_map_calls_maximum"], 1)
        self.assertEqual(scope["private_route_count"], 8)
        self.assertTrue(scope["conditional_R1_cohort_only"])
        self.assertTrue(scope["R2_through_R8_no_cohort"])
        self.assertTrue(scope["request_authorization_fields_all_false"])
        self.assertTrue(scope["request_operation_counters_all_zero"])

    def test_closeout_operations_and_current_authority_are_zero(self):
        self.assertTrue(
            all(value == 0 for value in self.proof["closeout_operations"].values())
        )
        self.assertTrue(
            all(value is False for value in self.proof["authorization_state"].values())
        )

    def test_next_gate_requires_own_green_and_fresh_decision(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["proof_closeout_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["sole_active_Tier_C_packet_identification_after_green_required"])
        self.assertTrue(gate["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])
        self.assertFalse(gate["MARC2_FW2_or_CIL1_authorized"])

    def test_claim_boundary_remains_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_request", "scientific_ceiling"}:
                self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
