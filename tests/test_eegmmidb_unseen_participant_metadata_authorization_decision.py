import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "registries/eegmmidb_unseen_participant_metadata_authorization_request.v0.json"
DECISION = ROOT / "registries/eegmmidb_unseen_participant_metadata_authorization_decision.v0.json"
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_AUTHORIZATION_DECISION.md"


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class EEGMMIDBUnseenParticipantMetadataAuthorizationDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_identity_and_exact_short_form_are_bound(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.eegmmidb_unseen_participant_metadata_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "EEGMMIDB-UG1-M")
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"], hashlib.sha256(b"continue").hexdigest()
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "EEGMMIDB-UG1-M")
        self.assertFalse(user["message_silently_corrected"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertTrue(user["one_registered_two_stage_sequence_only"])

    def test_exact_green_request_and_proof_are_bound(self):
        request = self.decision["green_request"]
        self.assertEqual(request["commit"], "e2647d609a99997ac417dac5d8efb2dad61863a0")
        self.assertEqual(request["CI_run_id"], 32_709_110_804)
        self.assertEqual(request["base_python_job_id"], 97_376_524_550)
        self.assertEqual(request["optional_neuro_job_id"], 97_376_524_804)
        self.assertTrue(request["both_required_jobs_green"])
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(proof["commit"], "e9c11da94730e790aace3acc818e029abcbdc165")
        self.assertEqual(proof["CI_run_id"], 32_710_175_884)
        self.assertEqual(proof["base_python_job_id"], 97_379_680_508)
        self.assertEqual(proof["optional_neuro_job_id"], 97_379_680_751)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_six_packet_artifacts_are_byte_hash_and_git_bound(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 29_320)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            self.assertEqual(_git_blob_sha1(payload), row["Git_blob"])

    def test_decision_artifacts_are_hash_bound(self):
        for row in self.decision["decision_artifacts"]:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])

    def test_decision_has_delayed_effect_and_strict_barriers(self):
        self.assertTrue(
            self.decision[
                "effective_only_after_this_record_is_committed_pushed_and_both_CI_jobs_green"
            ]
        )
        order = self.decision["required_execution_order"]
        self.assertEqual(order[0], "decision_commit_pushed_and_both_CI_jobs_green")
        self.assertEqual(
            order[3], "stage_M1_proof_closeout_commit_pushed_and_both_CI_jobs_green"
        )
        self.assertEqual(
            order[-1],
            "stop_before_source_acquisition_local_real_path_EDF_payload_target_model_or_score",
        )
        auth = self.decision["authorization"]
        self.assertTrue(
            auth["stage_M1_generated_metadata_client_implementation_after_decision_green"]
        )
        self.assertTrue(
            auth["stage_M2_one_real_metadata_invocation_after_stage_M1_proof_green"]
        )
        for key, value in auth.items():
            if key.endswith("authorized_now"):
                self.assertFalse(value, key)

    def test_metadata_identity_and_transport_match_request(self):
        identity = self.decision["dataset_identity"]
        self.assertEqual(identity["host"], "physionet.org")
        self.assertEqual(identity["files_exact"], 36)
        self.assertEqual(identity["source_files_exact"], 6)
        self.assertEqual(identity["fresh_files_exact"], 30)
        contract = self.decision["metadata_contract"]
        self.assertEqual(contract["HTTP_method"], "HEAD")
        self.assertEqual(contract["success_status_exact"], 200)
        self.assertEqual(contract["requests_exact"], 36)
        self.assertEqual(contract["redirects"], 0)
        self.assertEqual(contract["retries"], 0)
        self.assertEqual(contract["response_body_bytes"], 0)
        self.assertTrue(contract["content_length_required"])
        self.assertFalse(contract["fallback_GET_or_Range_allowed"])
        self.assertFalse(contract["partial_inventory_is_success"])
        self.assertEqual(
            contract["combined_declared_payload_bytes_maximum"],
            self.request["metadata_contract"]["combined_declared_payload_bytes_maximum"],
        )

    def test_resources_are_bounded_and_recording_did_no_operation(self):
        caps = self.decision["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["metadata_requests"], 36)
        self.assertLessEqual(caps["wall_time_seconds"], 300)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 256 << 20)
        self.assertEqual(caps["network_payload_body_bytes"], 0)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertTrue(
            all(value == 0 for value in self.decision["decision_only_counters"].values())
        )

    def test_claim_boundary_and_human_record_are_explicit(self):
        claims = self.decision["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {"engineering_capability_authorized_after_green", "scientific_ceiling"}:
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Scientific claim not established", document)
        self.assertIn("Stage M1", document)
        self.assertIn("Stage M2", document)
        self.assertIn("response-body", document)


if __name__ == "__main__":
    unittest.main()
