from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = (
    ROOT
    / "registries/fresh_motor_source_admission_generated_implementation.v0.json"
)
FRONTIER = ROOT / "registries/current_research_frontier.v17.json"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class FreshMotorSourceAdmissionGeneratedImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_implementation_identity_and_green_registration_are_exact(self) -> None:
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.fresh_motor_source_admission_generated_implementation",
        )
        self.assertEqual(self.record["protocol_id"], "FMSR1-R1-G-v0")
        self.assertEqual(self.record["implementation_id"], "FMSR1-R1-G-I0")
        self.assertEqual(
            self.record["green_registration"]["commit"],
            "d53f3e8870b1f3ae6f014411c9932f20474b8092",
        )
        self.assertTrue(
            self.record["green_registration"]["both_required_jobs_green"]
        )

    def test_bound_artifacts_match_exact_local_bytes(self) -> None:
        rows = self.record["bound_artifacts"]
        self.assertEqual(len(rows), 6)
        for row in rows:
            payload = (ROOT / row["path"]).read_bytes()
            self.assertEqual(len(payload), row["bytes"], row["path"])
            self.assertEqual(_sha256(payload), row["sha256"], row["path"])
        canonical = (
            json.dumps(rows, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
        summary = self.record["bound_artifact_summary"]
        self.assertEqual(sum(row["bytes"] for row in rows), summary["bytes"])
        self.assertEqual(len(canonical), summary["canonical_manifest_bytes"])
        self.assertEqual(_sha256(canonical), summary["canonical_manifest_sha256"])

    def test_official_qualification_is_explicitly_not_run(self) -> None:
        qualification = self.record["official_qualification"]
        self.assertFalse(qualification["activation_record_present"])
        self.assertFalse(qualification["implementation_exact_green"])
        self.assertEqual(qualification["official_runs"], 0)
        self.assertFalse(qualification["durable_consumed_marker_created"])
        self.assertFalse(qualification["report_emitted"])

    def test_frontier_preserves_scientific_and_live_boundaries(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v16.json",
        )
        implementation = self.frontier["R1_G_generated_only_implementation"]
        self.assertEqual(implementation["component_test_count"], 28)
        self.assertEqual(implementation["component_refusals_passed"], 82)
        self.assertEqual(
            self.frontier["independent_review"]["second_review_disposition"],
            "ACCEPT_no_remaining_blocker",
        )
        self.assertIsNone(self.frontier["active_Tier_C_packet"])
        self.assertFalse(self.frontier["claim_boundary"]["real_EEG_accessed"])
        self.assertFalse(
            self.frontier["claim_boundary"]["neural_advantage_established"]
        )
        self.assertFalse(
            self.frontier["claim_boundary"]["causal_live_decoding_established"]
        )


if __name__ == "__main__":
    unittest.main()
