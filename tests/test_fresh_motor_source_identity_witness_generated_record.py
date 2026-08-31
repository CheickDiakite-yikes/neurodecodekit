from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = (
    ROOT
    / "registries/fresh_motor_source_identity_witness_generated_implementation.v0.json"
)


def _git_blob(path: Path) -> str:
    payload = path.read_bytes()
    return hashlib.sha1(f"blob {len(payload)}\0".encode() + payload).hexdigest()


class FreshMotorSourceIdentityWitnessGeneratedRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_exact_implementation_artifacts_are_bound(self) -> None:
        rows = self.record["implementation_artifacts"]
        self.assertEqual(len(rows), self.record["implementation_artifact_summary"]["count"])
        self.assertEqual(
            sum(row["bytes"] for row in rows),
            self.record["implementation_artifact_summary"]["bytes"],
        )
        for row in rows:
            path = ROOT / row["path"]
            payload = path.read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(hashlib.sha256(payload).hexdigest(), row["sha256"], row["path"])
            self.assertEqual(_git_blob(path), row["git_blob"], row["path"])

    def test_generated_qualification_is_passed_consumed_and_bounded(self) -> None:
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], "GENERATED_WITNESS_QUALIFIED")
        self.assertTrue(result["consumed"])
        self.assertFalse(result["rerun_allowed"])
        self.assertEqual(result["deterministic_replays"], 2)
        self.assertEqual(
            [result["profile_count"], result["root_count"], result["page_count"]],
            [5, 17, 34],
        )
        self.assertEqual(result["refusal_observations"], 22)
        self.assertTrue(all(self.record["qualification_caps"].values()))

    def test_no_real_or_scientific_operation_is_claimed(self) -> None:
        counters = self.record["operation_counters"]
        protected = (
            "network_requests",
            "network_bytes",
            "official_index_requests",
            "candidate_semantic_operations",
            "source_selections",
            "payload_or_neural_reads",
            "target_or_label_reads",
            "model_runs",
            "training_runs",
            "prediction_sets",
            "scoring_events",
            "scientific_claim_upgrades",
        )
        self.assertTrue(all(counters[name] == 0 for name in protected))
        self.assertTrue(all(value is False for value in self.record["claim_boundary"].values()))

    def test_live_witness_still_requires_fresh_words_and_separate_decision(self) -> None:
        gate = self.record["next_gate"]
        self.assertTrue(gate["fresh_second_execution_bound_maintainer_words_required"])
        self.assertTrue(gate["separate_exact_execution_decision_required"])
        self.assertFalse(gate["network_authorized_now"])
        authority = self.record["authority_now"]
        self.assertFalse(authority["GitHub_API_or_official_index_network"])
        self.assertFalse(authority["live_source_identity_witness"])


if __name__ == "__main__":
    unittest.main()
