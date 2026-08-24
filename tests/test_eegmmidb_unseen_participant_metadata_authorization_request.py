import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/eegmmidb_unseen_participant_metadata_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs/EEGMMIDB_UNSEEN_PARTICIPANT_METADATA_AUTHORIZATION_PACKET.md"


class EEGMMIDBUnseenParticipantMetadataAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))

    def test_green_stage_g_closeout_is_exactly_bound(self):
        green = self.request["green_stage_G_closeout"]
        self.assertEqual(
            green["commit"], "5cc3e0e9fd5739e8836ddb91252f18ca7849c824"
        )
        self.assertEqual(green["CI_run_id"], 32708050897)
        self.assertEqual(green["base_python_job_id"], 97373297588)
        self.assertEqual(green["optional_neuro_readers_job_id"], 97373297708)
        self.assertTrue(green["both_required_jobs_green"])

    def test_bound_artifacts_hash_size_blob_and_set_hash_are_exact(self):
        rows = self.request["bound_pre_request_artifacts"]
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"])

        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        summary = self.request["bound_pre_request_artifact_summary"]
        self.assertEqual(summary["count"], 20)
        self.assertEqual(summary["bytes"], 305662)
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_exact_path_cohort_is_complete_distinct_and_ordered(self):
        paths = self.request["exact_paths_in_request_order"]
        self.assertEqual(len(paths), 36)
        self.assertEqual(len(set(paths)), 36)
        self.assertEqual(paths[:6], [
            "S001/S001R04.edf", "S001/S001R08.edf",
            "S002/S002R04.edf", "S002/S002R08.edf",
            "S003/S003R04.edf", "S003/S003R08.edf",
        ])
        self.assertEqual(paths[6], "S016/S016R11.edf")
        self.assertEqual(paths[-1], "S030/S030R12.edf")
        self.assertTrue(all(path.endswith(".edf") for path in paths))
        self.assertTrue(all(".event" not in path for path in paths))

    def test_metadata_surface_is_head_only_body_blind_and_no_retry(self):
        stages = self.request["requested_ordered_stages"]
        self.assertEqual(stages[0]["network_requests"], 0)
        self.assertEqual(stages[1]["HTTP_method"], "HEAD")
        self.assertEqual(stages[1]["requests_exact"], 36)
        self.assertEqual(stages[1]["redirects"], 0)
        self.assertEqual(stages[1]["retries"], 0)
        self.assertEqual(stages[1]["response_body_bytes"], 0)
        contract = self.request["metadata_contract"]
        self.assertTrue(contract["content_length_required"])
        self.assertFalse(contract["response_body_read_allowed"])
        self.assertFalse(contract["fallback_GET_or_Range_allowed"])
        self.assertFalse(contract["partial_inventory_is_success"])

    def test_resources_are_tighter_than_parent_caps(self):
        caps = self.request["resource_caps"]
        self.assertEqual(
            [caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]],
            [1, 1, 1],
        )
        self.assertEqual(caps["wall_time_seconds"], 300)
        self.assertLessEqual(caps["peak_process_tree_RSS_bytes"], 1073741824)
        self.assertEqual(caps["metadata_requests"], 36)
        self.assertEqual(caps["network_payload_body_bytes"], 0)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)

    def test_request_authorizes_nothing_and_performs_no_operation(self):
        self.assertTrue(all(value is False for value in self.request["authority_now"].values()))
        counters = self.request["request_operation_counters"]
        self.assertEqual(counters["tracked_artifact_reads"], 20)
        self.assertEqual(counters["Git_proof_reads"], 20)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key not in {"tracked_artifact_reads", "Git_proof_reads"}
            )
        )

    def test_claim_boundary_and_packet_language_remain_explicit(self):
        boundary = self.request["claim_boundary"]
        self.assertFalse(boundary["scientific_claim_established_by_request"])
        self.assertFalse(boundary["real_EEG_accessed"])
        self.assertFalse(boundary["unseen_participant_generalization_established"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Status: **All authority false; request only**", document)
        self.assertIn("Engineering capability proposed:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
