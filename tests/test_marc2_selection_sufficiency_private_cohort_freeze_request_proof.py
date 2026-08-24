import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = json.loads(
    (
        ROOT
        / "registries/marc2_selection_sufficiency_private_cohort_freeze_authorization_request.v0.json"
    ).read_text(encoding="utf-8")
)
PROOF = json.loads(
    (
        ROOT / "registries/marc2_selection_sufficiency_private_cohort_freeze_request_proof.v0.json"
    ).read_text(encoding="utf-8")
)
DOC = (
    ROOT / "docs/MARC_2_SELECTION_SUFFICIENCY_PRIVATE_COHORT_FREEZE_REQUEST_PROOF_CLOSEOUT.md"
).read_text(encoding="utf-8")


class SelectionSufficiencyPrivateCohortFreezeRequestProofTests(unittest.TestCase):
    def test_exact_remote_green_request_is_bound(self):
        remote = PROOF["request_proof"]
        self.assertEqual(remote["commit"], "6c805a817fa44375b7b0e120abcb2c748c78ca07")
        self.assertEqual(remote["CI_run_id"], 32_675_925_646)
        self.assertEqual(remote["base_python_job_id"], 97_283_907_786)
        self.assertEqual(remote["optional_neuro_job_id"], 97_283_907_932)
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

    def test_terminal_scope_is_unchanged(self):
        snapshot = PROOF["request_scope_snapshot"]
        self.assertEqual(snapshot["generated_paths"], 168)
        self.assertEqual(snapshot["successful_cardinalities"], list(range(12, 20)))
        self.assertEqual(snapshot["public_routes"], ["MARC2VR39P-R1", "MARC2VR39P-R2"])
        self.assertEqual(snapshot["commitment_scheme"], "HMAC-SHA256-v0")
        self.assertEqual(snapshot["retry_rerun_resume_limit"], 0)
        self.assertFalse(PROOF["scope_changed_after_request_proof"])

    def test_authority_and_operations_remain_zero(self):
        snapshot = PROOF["authorization_snapshot"]
        self.assertTrue(snapshot["all_request_authority_flags_false"])
        self.assertTrue(snapshot["all_request_operation_counters_zero"])
        self.assertFalse(snapshot["packet_bound_decision_received"])
        self.assertFalse(snapshot["private_read_or_cohort_attempt_authorized"])
        self.assertTrue(
            all(value is False for value in REQUEST["current_authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in REQUEST["current_operation_counters"].values()))

        closeout = PROOF["closeout_operation_counters"]
        expected_nonzero = {
            "repository_root_directory_listings": 1,
            "Git_ignored_root_entry_metadata_observations": 1,
        }
        self.assertEqual(
            {key: value for key, value in closeout.items() if value != 0},
            expected_nonzero,
        )

    def test_metadata_only_deviation_is_explicit_and_content_free(self):
        deviation = PROOF["metadata_only_protocol_deviation"]
        self.assertTrue(deviation["occurred"])
        self.assertFalse(deviation["observed_mode_owner_size_or_timestamp_retained"])
        self.assertFalse(deviation["descendant_or_content_access_occurred"])
        self.assertFalse(deviation["private_source_or_consumed_state_content_access_occurred"])
        self.assertFalse(deviation["authorizes_implementation_or_private_access"])
        self.assertFalse(deviation["consumes_generated_or_private_stage"])
        self.assertIn("metadata-only protocol deviation", DOC)

    def test_closeout_has_delayed_effect(self):
        delayed = PROOF["delayed_effect"]
        self.assertTrue(delayed["proof_closeout_commit_push_and_both_jobs_green_required"])
        self.assertFalse(delayed["packet_may_be_identified_as_sole_active_Tier_C_gate_now"])
        self.assertTrue(delayed["packet_may_be_identified_after_exact_closeout_green"])
        self.assertTrue(
            delayed["fresh_packet_bound_maintainer_message_required_after_identification"]
        )
        self.assertFalse(
            delayed["current_or_earlier_continue_approve_or_lets_go_is_retroactive_authority"]
        )
        self.assertFalse(delayed["packet_or_decision_alone_authorizes_private_open"])

    def test_document_preserves_claim_boundary(self):
        self.assertIn("Engineering capability requested", DOC)
        self.assertIn("Scientific claim not established", DOC)
        self.assertIn("not retroactive", DOC)
        self.assertEqual(PROOF["claim_boundary"]["scientific_ceiling"], "none")


if __name__ == "__main__":
    unittest.main()
