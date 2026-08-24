import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_authorization_request.v0.json"
)
DECISION = (
    ROOT
    / "registries/eegmmidb_unseen_participant_source_acquisition_authorization_decision.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_SOURCE_ACQUISITION_AUTHORIZATION_DECISION.md"
)


def _git_blob_sha1(payload: bytes) -> str:
    return hashlib.sha1(f"blob {len(payload)}\0".encode("ascii") + payload).hexdigest()


class EEGMMIDBUnseenParticipantSourceAcquisitionAuthorizationDecisionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_identity_and_exact_short_form_are_bound(self):
        self.assertEqual(
            self.decision["schema_name"],
            "neurodecodekit.eegmmidb_unseen_participant_source_acquisition_authorization_decision",
        )
        self.assertEqual(self.decision["lane_id"], "EEGMMIDB-UG1-SA")
        user = self.decision["user_authorization"]
        self.assertEqual(user["actual_message_verbatim"], "continue")
        self.assertEqual(user["actual_message_UTF8_bytes"], 8)
        self.assertEqual(
            user["actual_message_SHA256"], hashlib.sha256(b"continue").hexdigest()
        )
        self.assertEqual(user["sole_active_Tier_C_packet"], "EEGMMIDB-UG1-SA")
        self.assertFalse(user["message_silently_corrected"])
        self.assertFalse(user["long_form_packet_claimed_as_user_utterance"])
        self.assertTrue(user["substantive_registered_scope_unchanged"])
        self.assertTrue(user["one_registered_two_stage_sequence_only"])

    def test_exact_green_request_and_proof_are_bound(self):
        request = self.decision["green_request"]
        self.assertEqual(request["commit"], "2085ea061d936bb18ef08e93fb7d3f874ef0f9d8")
        self.assertEqual(request["CI_run_id"], 32_722_744_301)
        self.assertEqual(request["base_python_job_id"], 97_417_435_948)
        self.assertEqual(request["optional_neuro_job_id"], 97_417_435_670)
        self.assertTrue(request["both_required_jobs_green"])
        proof = self.decision["green_proof_closeout"]
        self.assertEqual(proof["commit"], "b0b4632ffbdaca10c1e4bbc93ad26ebd8e1368ca")
        self.assertEqual(proof["CI_run_id"], 32_724_357_118)
        self.assertEqual(proof["base_python_job_id"], 97_422_237_667)
        self.assertEqual(proof["optional_neuro_job_id"], 97_422_237_272)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertFalse(proof["scope_changed_from_request"])

    def test_six_packet_artifacts_are_byte_hash_and_git_bound(self):
        rows = self.decision["bound_packet_artifacts"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(row["bytes"] for row in rows), 44_910)
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
            order[3], "stage_SA1_proof_closeout_commit_pushed_and_both_CI_jobs_green"
        )
        self.assertEqual(order[-1], "stage_SA2_result_stop_before_EDF_parse_or_stage_S")
        auth = self.decision["authorization"]
        self.assertTrue(
            auth["stage_SA1_generated_source_acquisition_implementation_after_decision_green"]
        )
        self.assertTrue(
            auth["stage_SA2_one_real_source_acquisition_after_stage_SA1_proof_green"]
        )
        for key, value in auth.items():
            if key.endswith("authorized_now"):
                self.assertFalse(value, key)

    def test_source_identity_transport_and_caps_match_request(self):
        source = self.decision["source_boundary"]
        self.assertEqual(source["participants"], ["S001", "S002", "S003"])
        self.assertEqual(source["runs"], ["04", "08"])
        self.assertEqual(source["files_exact"], 6)
        self.assertEqual(source["successful_payload_bytes_exact"], 15_498_816)
        transport = self.decision["transport_contract"]
        self.assertEqual(transport["checksum_manifest_requests_exact"], 1)
        self.assertEqual(transport["EDF_requests_exact"], 6)
        self.assertEqual(transport["redirects"], 0)
        self.assertEqual(transport["retries"], 0)
        self.assertEqual(transport["reruns"], 0)
        self.assertFalse(transport["EDF_semantic_parse_allowed"])
        caps = self.decision["resource_caps"]
        self.assertEqual(
            (caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]),
            (1, 1, 1),
        )
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 256 << 20)
        self.assertLessEqual(caps["payload_network_body_bytes"], 16 << 20)
        self.assertLessEqual(caps["incremental_disk_bytes"], 64 << 20)
        self.assertEqual(caps["minimum_free_disk_bytes"], 2 << 30)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertEqual(
            caps["successful_payload_body_bytes_exact"],
            self.request["resource_caps"]["successful_payload_body_bytes_exact"],
        )

    def test_recording_did_no_operation_and_preserved_firewalls(self):
        self.assertTrue(
            all(value == 0 for value in self.decision["decision_only_counters"].values())
        )
        firewall = self.decision["firewalls"]
        self.assertEqual(firewall["retained_source_files"], 54)
        self.assertEqual(firewall["fresh_final_files"], 30)
        self.assertEqual(firewall["retained_source_operations"], 0)
        self.assertEqual(firewall["fresh_final_operations"], 0)
        self.assertFalse(firewall["EDF_semantic_access_allowed"])

    def test_claim_boundary_and_human_record_are_explicit(self):
        claims = self.decision["claim_boundary"]
        self.assertEqual(claims["scientific_ceiling"], "none")
        for key, value in claims.items():
            if key not in {
                "engineering_capability_authorized_after_green",
                "scientific_ceiling",
            }:
                self.assertFalse(value, key)
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Scientific claim not established", document)
        self.assertIn("Stage S-A1", document)
        self.assertIn("Stage S-A2", document)
        self.assertIn("six opaque", document)


if __name__ == "__main__":
    unittest.main()
