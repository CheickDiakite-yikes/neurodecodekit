import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF_PATH = (
    ROOT
    / "registries/marc2_inventory_taxonomy_private_discriminator_request_proof.v0.json"
)


class InventoryTaxonomyPrivateDiscriminatorRequestProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))

    def test_request_remote_proof_is_exact(self):
        proof = self.proof["request_remote_proof"]
        self.assertEqual(
            proof["commit"], "4e5895fc0fc8bc3cf2c91f5211406115a8e2e6d5"
        )
        self.assertEqual(proof["CI_run_id"], 32_613_575_234)
        self.assertEqual(proof["base_python_job_id"], 97_130_420_447)
        self.assertEqual(proof["optional_neuro_job_id"], 97_130_420_507)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_every_request_artifact_matches_bytes_hash_and_git_blob(self):
        rows = self.proof["exact_request_artifacts"]
        self.assertEqual(len(rows), 3)
        self.assertEqual(sum(row["bytes"] for row in rows), 30_187)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.run(
                ["git", "hash-object", row["path"]],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
            self.assertEqual(blob, row["Git_blob"])

    def test_scope_is_unchanged_and_aggregate_only(self):
        scope = self.proof["scope_unchanged"]
        self.assertEqual(scope["fixed_input_count"], 13)
        self.assertEqual(scope["fixed_input_bytes"], 149_233)
        self.assertEqual(scope["future_private_source_bytes"], 418_755)
        self.assertEqual(scope["future_private_source_content_opens"], 1)
        self.assertEqual(scope["private_route_count"], 5)
        self.assertEqual(scope["private_answer_route_count"], 2)
        self.assertFalse(scope["private_detail_retention_allowed"])
        self.assertFalse(scope["cohort_freeze_allowed"])
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
        self.assertTrue(
            gate["sole_active_Tier_C_packet_identification_after_green_required"]
        )
        self.assertTrue(gate["fresh_packet_bound_maintainer_decision_required"])
        self.assertTrue(
            gate["decision_commit_push_and_both_jobs_green_before_implementation_required"]
        )
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])

    def test_claim_boundary_remains_scientifically_empty(self):
        claims = self.proof["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_request", "scientific_ceiling"}:
                self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
