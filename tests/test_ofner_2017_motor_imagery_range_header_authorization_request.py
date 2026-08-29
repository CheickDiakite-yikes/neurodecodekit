from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUEST = (
    ROOT
    / "registries/ofner_2017_motor_imagery_range_header_authorization_request.v0.json"
)
DOCUMENT = ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_RANGE_HEADER_AUTHORIZATION_PACKET.md"
FRONTIER = ROOT / "registries/current_research_frontier.v4.json"


class OfnerRangeHeaderAuthorizationRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.request = json.loads(REQUEST.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_exact_green_proof_chain_is_bound(self) -> None:
        proof = self.request["proof_anchors"]
        self.assertEqual(
            proof["generated_header_successor_commit"],
            "ca5d1db35a34762905d4df823766a6d353516c66",
        )
        self.assertEqual(
            proof["proof_closeout_commit"],
            "6815338609176b0f1599cbb2e11b4ce3acc8bad9",
        )
        self.assertEqual(proof["proof_closeout_CI_run_id"], 33_272_310_252)
        self.assertTrue(proof["all_named_jobs_green"])
        self.assertTrue(proof["all_named_commits_on_GitHub_main"])

    def test_bound_artifact_set_is_exact(self) -> None:
        artifact_set = self.request["artifact_set"]
        rows = artifact_set["artifacts"]
        self.assertEqual(artifact_set["artifact_count"], 12)
        self.assertEqual(artifact_set["artifact_bytes"], 86_180)
        self.assertEqual(sum(row["bytes"] for row in rows), 86_180)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(), artifact_set["canonical_sha256"]
        )

    def test_exact_member_and_minimum_byte_ranges_are_frozen(self) -> None:
        member = self.request["exact_member"]
        self.assertEqual(member["participant"], 1)
        self.assertEqual(member["run"], 1)
        self.assertEqual(member["declared_payload_bytes"], 105_365_484)
        self.assertFalse(member["full_payload_hash_recomputed_by_checkpoint"])
        stage = self.request["ordered_stage_HL2_real_checkpoint"]
        self.assertEqual(stage["success_manifest_GET_requests_exact"], 1)
        self.assertEqual(stage["success_GDF_range_GET_requests_exact"], 2)
        self.assertEqual(stage["first_range"], "bytes=0-255")
        self.assertEqual(stage["combined_GDF_body_bytes_maximum"], 65_536)
        self.assertEqual(stage["expected_H1_complete_header_bytes"], 24_832)
        self.assertFalse(stage["whole_file_request"])
        self.assertFalse(stage["full_payload_hash_pass"])

    def test_representation_gate_and_resources_are_strict(self) -> None:
        gate = self.request["header_gate"]
        self.assertEqual(
            [
                gate["EEG_channels_H1_exact"],
                gate["EOG_channels_H1_exact"],
                gate["glove_channels_H1_exact"],
                gate["arm_channels_H1_exact"],
            ],
            [61, 3, 19, 13],
        )
        self.assertEqual(gate["sampling_rate_hz_H1_exact"], 512)
        self.assertFalse(gate["transport_H0_has_biological_interpretation"])
        caps = self.request["resource_envelope"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["peak_process_tree_RSS_bytes_maximum"], 268_435_456)
        self.assertEqual(caps["total_response_body_bytes_maximum"], 2_162_688)
        self.assertEqual(caps["incremental_disk_bytes_maximum"], 4_194_304)
        self.assertEqual(caps["reruns"], 0)

    def test_every_authority_and_operation_is_false_or_zero(self) -> None:
        self.assertTrue(all(value is False for value in self.request["authority"].values()))
        self.assertTrue(
            all(value == 0 for value in self.request["operation_counters_at_request"].values())
        )
        decision = self.request["decision_boundary"]
        self.assertTrue(decision["all_authority_flags_false"])
        self.assertIsNone(decision["active_Tier_C_packet_now"])
        self.assertFalse(decision["earlier_continue_or_general_approval_retroactive"])

    def test_frontier_and_document_keep_packet_inactive(self) -> None:
        self.assertEqual(self.frontier["active_lane_id"], "NO_ACTIVE_TIER_C_GATE")
        self.assertFalse(self.frontier["queued_packet"]["active_now"])
        self.assertFalse(self.frontier["next_gate"]["real_data_authority_created"])
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("every authority flag remains false", document)
        self.assertIn("Engineering capability requested:", document)
        self.assertIn("Scientific claim not established:", document)


if __name__ == "__main__":
    unittest.main()
