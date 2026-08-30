from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTIER = ROOT / "registries/current_research_frontier.v12.json"
PREDECESSOR = ROOT / "registries/current_research_frontier.v11.json"


class CurrentResearchFrontierV12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))

    def test_v12_exactly_supersedes_v11(self) -> None:
        self.assertEqual(self.frontier["schema_version"], "0.13.0")
        self.assertEqual(
            self.frontier["superseded_registry_sha256"],
            hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest(),
        )

    def test_decision_is_recorded_but_not_yet_effective(self) -> None:
        self.assertEqual(self.frontier["active_lane_id"], "FMSR1-DISCOVERY-M0")
        decision = self.frontier["pending_decision"]
        self.assertEqual(decision["decision_id"], "FMSR1-DISCOVERY-M0-D0")
        self.assertTrue(decision["effective_only_after_this_exact_commit_remote_green"])
        self.assertFalse(decision["implementation_allowed_before_decision_green"])
        self.assertFalse(decision["network_allowed_before_implementation_green"])

    def test_every_present_operation_authority_is_false(self) -> None:
        for key, value in self.frontier["operation_authority_now"].items():
            self.assertFalse(value, key)
        self.assertFalse(self.frontier["next_gate"]["describes_present_authority"])

    def test_hard_scientific_route_is_ordered(self) -> None:
        self.assertEqual(
            self.frontier["governing_hard_decision_tree"],
            "docs/SCIENTIFIC_RESULT_HARD_DECISION_TREE.md",
        )
        tree = (ROOT / self.frontier["governing_hard_decision_tree"]).read_text(
            encoding="utf-8"
        )
        for required in (
            "3D Attribution Cube Inside A 5D Evidence Map",
            "Three Positive-Control Gates",
            "Independent replication fails",
            "No third path of indefinite dataset hunting is allowed",
        ):
            self.assertIn(required, tree)
        architecture = self.frontier["scientific_evidence_architecture"]
        self.assertEqual(len(architecture["attribution_cube_dimensions_1_to_3"]), 3)
        self.assertEqual(len(architecture["outer_evidence_dimensions_4_to_5"]), 2)
        self.assertEqual(
            architecture["translation_dimension_6"],
            [
                "offline_evaluation",
                "causal_replay",
                "shadow_stream",
                "prospective_live",
            ],
        )
        self.assertTrue(architecture["correct_attribution_corner_required"])
        self.assertEqual(len(architecture["attribution_cube_primary_edges"]), 6)
        self.assertEqual(
            architecture["primary_cube_rule"],
            "intersection_union_minimum_across_participant_macro_edges",
        )
        self.assertTrue(
            architecture[
                "posterior_EEG_is_neural_spatial_comparator_not_non_neural_nuisance"
            ]
        )
        self.assertFalse(architecture["no_signal_win_alone_establishes_attribution"])
        self.assertFalse(
            architecture["translation_can_rescue_failed_attribution_or_evidence_dimension"]
        )
        self.assertFalse(architecture["live_motor_success_validates_language_decoding"])
        self.assertTrue(
            architecture[
                "communication_requires_separate_preregistration_and_independent_LM_only_baseline"
            ]
        )
        self.assertEqual(
            self.frontier["hard_scientific_route_after_source_admission"],
            [
                "within_person_positive_control",
                "unseen_person_EEG_increment_over_joint_nuisance_and_derangement",
                "fresh_independent_replication",
                "causal_shadow_then_live_motor_decoding",
                "separate_communication_language_program_with_independent_LM_prior",
            ],
        )
        coordinate = self.frontier["current_evidence_coordinate"]
        self.assertEqual(set(coordinate), {
            "dimension_1_spatial",
            "dimension_2_temporal",
            "dimension_3_physiological",
            "dimension_4_task_autonomy",
            "dimension_5_population_generalization",
            "dimension_6_translation",
            "scientific_claim_upgrade",
        })
        self.assertFalse(coordinate["scientific_claim_upgrade"])
        self.assertTrue(all(value is False for value in self.frontier["claim_boundary"].values()))


if __name__ == "__main__":
    unittest.main()
