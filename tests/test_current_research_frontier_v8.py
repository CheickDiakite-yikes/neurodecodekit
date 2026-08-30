from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v8.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v7.json"
PROOF = ROOT / "registries/neural_payload_admission_generated_qualification_proof.v0.json"


class CurrentResearchFrontierV8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_frontier_is_exact_additive_successor(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.9.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )
        self.assertTrue(PROOF.is_file())
        self.assertIsNone(self.frontier["active_lane_id"])

    def test_generated_transport_qualification_is_exact_green(self) -> None:
        green = self.frontier["green_generated_transport_qualification"]
        self.assertEqual(
            green["implementation_commit"],
            "2e164fffb00e5db79a6c6d810eabbcc2d447c5a1",
        )
        self.assertEqual(green["CI_run_id"], 33_284_320_443)
        self.assertEqual(green["base_python_job_id"], 99_184_746_988)
        self.assertEqual(green["optional_neuro_readers_job_id"], 99_184_747_065)
        self.assertTrue(green["both_required_jobs_green"])
        self.assertEqual(green["deterministic_replays"], 2)
        self.assertEqual(green["named_adversarial_families"], 37)
        self.assertEqual(green["network_requests"], 0)

    def test_only_artifact_only_preregistration_is_next(self) -> None:
        authority = self.frontier["operation_authority"]
        self.assertTrue(authority["artifact_only_fresh_source_research_preregistration"])
        for key, value in authority.items():
            if key != "artifact_only_fresh_source_research_preregistration":
                self.assertFalse(value, key)
        self.assertEqual(self.frontier["next_gate"]["tier"], "Tier_A_artifact_only_no_network")
        self.assertFalse(self.frontier["future_transport_canary"]["authorized_now"])

    def test_claim_boundary_separates_engineering_from_science(self) -> None:
        boundary = self.frontier["claim_boundary"]
        self.assertTrue(boundary["transport_admission_architecture_frozen"])
        self.assertTrue(boundary["generated_transport_admission_proven"])
        for key, value in boundary.items():
            if key not in {
                "transport_admission_architecture_frozen",
                "generated_transport_admission_proven",
            }:
                self.assertFalse(value, key)

    def test_current_control_plane_names_v8_and_NPA1(self) -> None:
        for relative in (
            "AGENTS.md",
            "README.md",
            "START_HERE.md",
            "docs/CODEX_HANDOFF.md",
            "docs/SCIENTIFIC_CONVERGENCE_AND_INVENTION_PLAN.md",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")[:16_000]
            self.assertIn("current_research_frontier.v8.json", text, relative)
            self.assertIn("NPA1-G", text, relative)


if __name__ == "__main__":
    unittest.main()
