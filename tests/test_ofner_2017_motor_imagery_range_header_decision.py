from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = (
    ROOT / "registries/ofner_2017_motor_imagery_range_header_decision.v0.json"
)
DOCUMENT = ROOT / "docs/OFNER_2017_MOTOR_IMAGERY_RANGE_HEADER_DECISION.md"


class OfnerRangeHeaderDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.decision = json.loads(DECISION.read_text(encoding="utf-8"))

    def test_actual_maintainer_word_is_preserved(self) -> None:
        words = "continue"
        self.assertEqual(self.decision["maintainer_words"], words)
        self.assertEqual(self.decision["maintainer_words_utf8_bytes"], 8)
        self.assertEqual(
            self.decision["maintainer_words_sha256"],
            hashlib.sha256(words.encode()).hexdigest(),
        )
        authorization = self.decision["user_authorization"]
        self.assertTrue(authorization["actual_message_preserved_verbatim"])
        self.assertFalse(authorization["long_form_sentence_claimed_as_user_utterance"])
        self.assertFalse(authorization["scope_expansion_by_inference"])

    def test_green_packet_chain_is_exact(self) -> None:
        request = self.decision["green_request"]
        self.assertEqual(
            request["commit"], "af9d0247bb816c3432a9eb407fadcd286f84d87c"
        )
        self.assertEqual(request["CI_run_id"], 33_273_113_793)
        proof = self.decision["green_request_proof"]
        self.assertEqual(
            proof["commit"], "2c313d57ca3acebeea985fb788593be88877f68e"
        )
        self.assertEqual(proof["CI_run_id"], 33_273_777_182)
        frontier = self.decision["green_frontier_transition"]
        self.assertEqual(
            frontier["commit"], "845b39ef88cd747b329be49e56efa5cdf999a40d"
        )
        self.assertEqual(frontier["CI_run_id"], 33_274_520_086)
        self.assertTrue(frontier["both_required_jobs_green"])

    def test_bound_artifacts_are_exact(self) -> None:
        rows = self.decision["bound_artifacts"]
        summary = self.decision["bound_artifact_summary"]
        self.assertEqual(summary["count"], 7)
        self.assertEqual(summary["bytes"], 36_105)
        self.assertEqual(sum(row["bytes"] for row in rows), 36_105)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(
                hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"]
            )
            blob = subprocess.check_output(
                ["git", "hash-object", row["path"]], cwd=ROOT, text=True
            ).strip()
            self.assertEqual(blob, row["git_blob"], row["path"])
        canonical = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(
            hashlib.sha256(canonical).hexdigest(),
            summary["canonical_artifact_set_sha256"],
        )

    def test_authorized_sequence_and_caps_are_exact(self) -> None:
        authorization = self.decision["authorization_after_decision_green"]
        self.assertTrue(authorization["implement_HL1_additive_standard_library_wrapper"])
        self.assertEqual(authorization["run_HL1_generated_mock_qualification_maximum"], 1)
        self.assertTrue(
            authorization["create_HL2_activation_after_exact_HL1_remote_green"]
        )
        self.assertEqual(authorization["HL2_success_manifest_GET_requests_exact"], 1)
        self.assertEqual(authorization["HL2_success_GDF_range_GET_requests_exact"], 2)
        self.assertEqual(authorization["HL2_combined_GDF_body_bytes_maximum"], 65_536)
        self.assertEqual(authorization["whole_GDF_file_requests"], 0)
        self.assertEqual(authorization["event_or_annotation_reads"], 0)
        self.assertEqual(authorization["signal_sample_reads"], 0)
        caps = self.decision["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["runtime_seconds_maximum"], 120)
        self.assertEqual(caps["peak_process_tree_RSS_bytes_maximum"], 268_435_456)
        self.assertEqual(caps["incremental_disk_bytes_maximum"], 4_194_304)
        self.assertEqual(caps["redirects"], 0)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)

    def test_decision_only_counters_remain_zero(self) -> None:
        counters = self.decision["decision_only_access_counters"]
        for key, value in counters.items():
            if key == "GitHub_CI_verification_calls":
                expected = 1
            elif key == "end_to_end_latency_measured":
                expected = False
            else:
                expected = 0
            self.assertEqual(value, expected, key)

    def test_human_decision_states_both_boundaries(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("> continue", document)
        self.assertIn("Engineering capability authorized for testing:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No source or GDF operation occurred", document)


if __name__ == "__main__":
    unittest.main()
