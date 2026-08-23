import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = json.loads(
    (
        ROOT
        / "registries/marc2_task_aware_private_cohort_confirmation_request_proof.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT
    / "docs/MARC_2_TASK_AWARE_PRIVATE_COHORT_CONFIRMATION_REQUEST_PROOF_CLOSEOUT.md"
).read_text(encoding="utf-8")


class Marc2TaskAwarePrivateCohortRequestProofTests(unittest.TestCase):
    def test_identity_and_remote_request_proof_are_exact(self):
        self.assertEqual(PROOF["lane_id"], "MARC2-VR36P")
        self.assertEqual(
            PROOF["status"], "request_proof_closeout_local_remote_green_pending"
        )
        remote = PROOF["request_remote_proof"]
        self.assertEqual(
            remote["commit"], "8ec87ced3c0072fec62328a9635eb9774e13e605"
        )
        self.assertEqual(remote["CI_run_id"], 32_646_648_532)
        self.assertEqual(remote["base_python_job_id"], 97_211_815_865)
        self.assertEqual(remote["optional_neuro_job_id"], 97_211_815_879)
        self.assertTrue(remote["both_required_jobs_green"])

    def test_three_request_artifacts_match_exact_bytes(self):
        total = 0
        for row in PROOF["request_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            total += len(payload)
            self.assertIn(row["Git_blob"], DOC)
        self.assertEqual(len(PROOF["request_artifacts"]), 3)
        self.assertEqual(total, PROOF["request_artifact_bytes"])

    def test_scope_is_unchanged_and_all_authority_is_false(self):
        self.assertTrue(PROOF["scope_unchanged"])
        self.assertTrue(
            all(value is False for value in PROOF["authorization_flags"].values())
        )

    def test_every_operation_counter_is_zero(self):
        self.assertTrue(all(value == 0 for value in PROOF["operation_counters"].values()))
        self.assertFalse(PROOF["verification"]["implementation_or_private_operation_run"])

    def test_closeout_has_delayed_effect_and_no_retroactivity(self):
        gate = PROOF["next_gate"]
        self.assertTrue(gate["exact_closeout_commit_push_and_both_jobs_green_required"])
        self.assertFalse(gate["packet_identification_or_fresh_decision_allowed_now"])
        self.assertTrue(
            gate["packet_becomes_sole_active_Tier_C_gate_after_exact_closeout_green"]
        )
        self.assertTrue(gate["fresh_packet_bound_maintainer_message_required_after_identification"])
        self.assertFalse(gate["current_or_earlier_continue_is_retroactive_authority"])
        self.assertFalse(gate["implementation_private_read_or_cohort_freeze_authorized_now"])

    def test_claim_boundary_remains_empty(self):
        claims = PROOF["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        self.assertFalse(claims["real_or_private_data_accessed"])
        self.assertFalse(claims["real_cohort_established"])
        self.assertFalse(claims["neural_payload_accessed"])
        self.assertFalse(claims["decoding_performance_established"])

    def test_document_uses_required_two_sentence_boundary(self):
        self.assertIn("Engineering capability requested", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("not retroactive authority", DOC)
        self.assertIn("cannot open private data", DOC)


if __name__ == "__main__":
    unittest.main()
