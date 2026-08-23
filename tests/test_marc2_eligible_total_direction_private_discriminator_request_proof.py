import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/marc2_eligible_total_direction_private_discriminator_authorization_request.v0.json"
)
PROOF = (
    ROOT
    / "registries/marc2_eligible_total_direction_private_discriminator_request_proof.v0.json"
)
DOC = (
    ROOT
    / "docs/MARC_2_ELIGIBLE_TOTAL_DIRECTION_PRIVATE_DISCRIMINATOR_REQUEST_PROOF_CLOSEOUT.md"
)


class Marc2EligibleTotalDirectionPrivateDiscriminatorRequestProofTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.proof = json.loads(PROOF.read_text(encoding="utf-8"))

    def test_exact_remote_request_proof_is_bound(self):
        remote = self.proof["request_remote_proof"]
        self.assertEqual(
            remote["commit"], "9dc13cb29804a7adfeaa45aa821e36e160a0f6ee"
        )
        self.assertEqual(remote["CI_run_id"], 32_629_224_038)
        self.assertEqual(remote["base_python_job_id"], 97_169_278_061)
        self.assertEqual(remote["optional_neuro_job_id"], 97_169_278_037)
        self.assertTrue(remote["both_required_jobs_green"])

    def test_exact_request_artifacts_match(self):
        total = 0
        for item in self.proof["exact_request_artifacts"]:
            payload = (ROOT / item["path"]).read_bytes()
            self.assertEqual(len(payload), item["bytes"], item["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), item["sha256"])
            git_blob = hashlib.sha1(
                f"blob {len(payload)}\0".encode("ascii") + payload
            ).hexdigest()
            self.assertEqual(git_blob, item["Git_blob"], item["path"])
            total += len(payload)
        self.assertEqual(total, self.proof["exact_request_artifact_bytes"])
        self.assertEqual(len(self.proof["exact_request_artifacts"]), 3)

    def test_scope_matches_unchanged_request(self):
        scope = self.proof["scope_unchanged"]
        self.assertEqual(scope["fixed_input_bytes"], self.request["fixed_input_bytes"])
        self.assertEqual(scope["future_private_source_bytes"], 418_755)
        self.assertEqual(scope["future_private_source_content_opens"], 1)
        self.assertFalse(scope["observed_total_or_difference_allowed"])
        self.assertFalse(scope["cohort_freeze_allowed"])
        self.assertTrue(scope["request_authorization_fields_all_false"])
        self.assertTrue(scope["request_operation_counters_all_zero"])
        self.assertTrue(
            all(value is False for value in self.request["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.request["operation_counters"].values())
        )

    def test_closeout_performs_zero_operations(self):
        self.assertTrue(
            all(value == 0 for value in self.proof["closeout_operations"].values())
        )
        self.assertTrue(
            all(value is False for value in self.proof["authorization_state"].values())
        )

    def test_next_gate_requires_fresh_decision(self):
        gate = self.proof["next_gate"]
        self.assertTrue(gate["proof_closeout_commit_push_and_both_jobs_green_required"])
        self.assertTrue(gate["sole_active_Tier_C_packet_identification_after_green_required"])
        self.assertTrue(gate["fresh_packet_bound_maintainer_decision_required"])
        self.assertFalse(gate["implementation_authorized_now"])
        self.assertFalse(gate["private_read_authorized_now"])

    def test_human_closeout_preserves_both_boundaries(self):
        text = DOC.read_text(encoding="utf-8")
        self.assertIn("current `continue` predates this proof barrier", text)
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)


if __name__ == "__main__":
    unittest.main()
