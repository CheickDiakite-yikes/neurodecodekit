import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = json.loads(
    (
        ROOT
        / "registries/marc2_exact_task_surplus_private_discriminator_authorization_request.v0.json"
    ).read_text(encoding="utf-8")
)
PROOF = json.loads(
    (
        ROOT / "registries/marc2_exact_task_surplus_private_discriminator_request_proof.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT / "docs/MARC_2_EXACT_TASK_SURPLUS_PRIVATE_DISCRIMINATOR_REQUEST_PROOF_CLOSEOUT.md"
).read_text(encoding="utf-8")


class ExactTaskSurplusPrivateDiscriminatorRequestProofTests(unittest.TestCase):
    def test_exact_remote_green_request_is_bound(self):
        remote = PROOF["request_proof"]
        self.assertEqual(remote["commit"], "e89908adf508ca3c858b4ee0509c45fd8d29f866")
        self.assertEqual(remote["CI_run_id"], 32_656_051_436)
        self.assertEqual(remote["base_python_job_id"], 97_234_876_608)
        self.assertEqual(remote["optional_neuro_job_id"], 97_234_876_537)
        self.assertTrue(remote["both_required_jobs_green"])

    def test_request_artifacts_remain_byte_exact(self):
        total = 0
        for row in PROOF["request_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            self.assertIn(row["Git_blob"], DOC)
            total += len(payload)
        self.assertEqual(total, PROOF["request_artifact_bytes"])
        self.assertEqual(len(PROOF["request_artifacts"]), 3)

    def test_authority_and_operations_remain_zero(self):
        snapshot = PROOF["authorization_snapshot"]
        self.assertTrue(snapshot["all_request_authority_flags_false"])
        self.assertTrue(snapshot["all_request_operation_counters_zero"])
        self.assertFalse(snapshot["packet_bound_decision_received"])
        self.assertFalse(snapshot["private_read_or_discriminator_authorized"])
        self.assertTrue(
            all(value is False for value in REQUEST["current_authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in PROOF["closeout_operation_counters"].values()))

    def test_closeout_has_delayed_effect(self):
        delayed = PROOF["delayed_effect"]
        self.assertTrue(delayed["proof_closeout_commit_push_and_both_jobs_green_required"])
        self.assertFalse(delayed["packet_may_be_identified_as_sole_active_Tier_C_gate_now"])
        self.assertTrue(delayed["packet_may_be_identified_after_exact_closeout_green"])
        self.assertTrue(
            delayed["fresh_packet_bound_maintainer_message_required_after_identification"]
        )
        self.assertFalse(delayed["current_or_earlier_continue_is_retroactive_authority"])
        self.assertFalse(delayed["packet_or_decision_alone_authorizes_private_open"])

    def test_document_preserves_claim_boundary(self):
        self.assertIn("Engineering capability requested", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("not retroactive authority", DOC)
        self.assertEqual(PROOF["claim_boundary"]["scientific_ceiling"], "none")


if __name__ == "__main__":
    unittest.main()
