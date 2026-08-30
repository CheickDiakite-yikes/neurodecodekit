from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "registries/current_research_frontier.v13.json"
PREVIOUS = ROOT / "registries/current_research_frontier.v12.json"
CONSTITUTION = ROOT / "docs/SCIENTIFIC_DISCOVERY_AND_INVENTION_CONSTITUTION.md"


class CurrentResearchFrontierV13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(CURRENT.read_text(encoding="utf-8"))

    def test_supersedes_exact_v12_without_rewriting_history(self) -> None:
        self.assertEqual(
            self.frontier["supersedes"],
            "registries/current_research_frontier.v12.json",
        )
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),
        )

    def test_5d_plus_translation_architecture_remains_exact(self) -> None:
        architecture = self.frontier["scientific_evidence_architecture"]
        self.assertEqual(len(architecture["attribution_cube_dimensions_1_to_3"]), 3)
        self.assertEqual(len(architecture["outer_evidence_dimensions_4_to_5"]), 2)
        self.assertEqual(
            architecture["translation_dimension_6"],
            ["offline_evaluation", "causal_replay", "shadow_stream", "prospective_live"],
        )
        self.assertFalse(architecture["no_signal_win_alone_establishes_attribution"])
        self.assertFalse(architecture["live_motor_success_validates_language_decoding"])

    def test_constitution_carries_the_same_evidence_geometry(self) -> None:
        constitution = CONSTITUTION.read_text(encoding="utf-8")
        required = (
            "5.1 CANONICAL EVIDENCE GEOMETRY",
            "three-dimensional attribution cube nested inside a five-dimensional",
            "Spatial: central EEG versus geometry-matched posterior or visual EEG.",
            "Temporal: the correct motor window versus pre-cue, cue, and",
            "Physiological: real central EEG versus joint EOG, EMG, and metadata controls,",
            "Task identifiability and autonomy",
            "Population generalization",
            "Offline evaluation to causal replay to shadow stream to prospective live",
            "Live motor success does not validate language decoding.",
            "independently scored language-model-only baseline",
            "does not itself grant data, model,",
        )
        for phrase in required:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, constitution)

    def test_generated_implementation_does_not_open_network_or_claims(self) -> None:
        implementation = self.frontier["generated_implementation"]
        self.assertEqual(implementation["replay_count"], 2)
        self.assertEqual(implementation["refusal_case_count"], 25)
        self.assertEqual(implementation["real_network_requests"], 0)
        self.assertFalse(implementation["scientific_value"])
        authority = self.frontier["operation_authority_now"]
        self.assertTrue(authority["generated_discovery_implementation"])
        self.assertTrue(authority["generated_discovery_qualification"])
        self.assertFalse(authority["public_source_discovery_network_research"])
        self.assertFalse(authority["real_payload_or_header_access"])
        self.assertFalse(any(self.frontier["claim_boundary"].values()))

    def test_next_gate_is_proof_only_closeout_not_scientific_execution(self) -> None:
        barriers = self.frontier["execution_barriers"]
        self.assertFalse(barriers["exact_implementation_commit_pushed_to_GitHub_main"])
        self.assertFalse(barriers["proof_only_generated_implementation_closeout_exists"])
        self.assertFalse(barriers["exact_official_index_revisions_packet_bound"])
        self.assertFalse(barriers["live_execution_armable_under_current_packet"])
        self.assertFalse(barriers["sole_metadata_execution_armed"])
        self.assertFalse(self.frontier["next_gate"]["network_request_authorized_now"])


if __name__ == "__main__":
    unittest.main()
