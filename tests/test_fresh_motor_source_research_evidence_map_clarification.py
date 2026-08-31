from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = (
    ROOT / "docs" / "FRESH_MOTOR_SOURCE_RESEARCH_EVIDENCE_MAP_CLARIFICATION.md"
)
REGISTRY = (
    ROOT
    / "registries"
    / "fresh_motor_source_research_evidence_map_clarification.v0.json"
)
PARENT = ROOT / "registries" / "fresh_motor_source_research_contract.v1.json"


class FreshMotorSourceResearchEvidenceMapClarificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.parent = json.loads(PARENT.read_text(encoding="utf-8"))

    def test_parent_fmsr1_v1_is_byte_exact_and_unchanged(self) -> None:
        binding = self.value["parent_registration"]
        payload = PARENT.read_bytes()
        self.assertEqual(binding["protocol_id"], "FMSR1-v1")
        self.assertEqual(binding["bytes"], len(payload))
        self.assertEqual(binding["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(binding["bytes"], 15280)
        self.assertEqual(
            binding["sha256"],
            "9667b31282d7e5c852fc3de1b6fe07692952ec5720b79a0ba7c31345ccfbc8cb",
        )
        self.assertTrue(binding["preserved_byte_for_byte"])
        self.assertFalse(binding["rewritten"])
        self.assertFalse(binding["superseded"])
        self.assertFalse(binding["reactivated"])

    def test_human_and_governing_sources_are_exactly_bound(self) -> None:
        human = self.value["binding"]["human_clarification"]
        document_payload = DOCUMENT.read_bytes()
        self.assertEqual(human["bytes"], len(document_payload))
        self.assertEqual(
            human["sha256"], hashlib.sha256(document_payload).hexdigest()
        )

        for source in self.value["binding"]["governing_sources"]:
            path = ROOT / source["path"]
            payload = path.read_bytes()
            self.assertEqual(source["bytes"], len(payload), source["path"])
            self.assertEqual(
                source["sha256"],
                hashlib.sha256(payload).hexdigest(),
                source["path"],
            )

    def test_3d_cube_is_nested_in_5d_map_and_translation_is_separate(self) -> None:
        architecture = self.value["governing_scientific_architecture"]
        cube = architecture["attribution_cube"]
        self.assertTrue(cube["nested_inside_5D_evidence_map"])
        self.assertEqual(
            [(item["dimension_id"], item["name"]) for item in cube["dimensions"]],
            [(1, "spatial"), (2, "temporal"), (3, "physiological")],
        )
        self.assertTrue(
            all(
                item["question"] == "what_produced_the_signal"
                for item in cube["dimensions"]
            )
        )

        outer = architecture["outer_evidence_dimensions"]
        self.assertEqual(
            [(item["dimension_id"], item["name"]) for item in outer],
            [
                (4, "task_identifiability_and_autonomy"),
                (5, "population_generalization"),
            ],
        )

        translation = architecture["translation_dimension"]
        self.assertEqual(translation["dimension_id"], 6)
        self.assertFalse(translation["nested_inside_5D_evidence_map"])
        self.assertTrue(translation["separate_from_scientific_evidence_map"])
        self.assertEqual(
            translation["ordered_stages"],
            [
                "offline_evaluation",
                "causal_replay",
                "shadow_stream",
                "prospective_live",
            ],
        )
        self.assertFalse(translation["can_rescue_failed_dimensions_1_through_5"])
        self.assertFalse(
            translation["live_motor_success_establishes_language_decoding"]
        )

    def test_spatial_temporal_and_physiological_roles_are_distinct(self) -> None:
        roles = self.value["comparator_roles"]

        spatial = roles["spatial"]
        self.assertTrue(spatial["posterior_EEG_is_separate_spatial_comparator"])
        self.assertFalse(
            spatial["posterior_EEG_is_part_of_physiological_nuisance_only_arm"]
        )

        temporal = roles["temporal"]
        self.assertIn(
            "structure_preserving_shifted_central_EEG", temporal["comparators"]
        )
        self.assertTrue(
            temporal["structure_preserving_shifted_EEG_is_temporal_comparator"]
        )
        self.assertFalse(
            temporal[
                "structure_preserving_shifted_EEG_is_part_of_physiological_nuisance_only_arm"
            ]
        )

        nuisance = roles["physiological_nuisance_only"]
        self.assertEqual(
            nuisance["components"],
            [
                "EOG",
                "task_relevant_EMG_for_every_relevant_effector",
                "non_neural_metadata_including_preregistered_cue_and_timing_covariates",
            ],
        )
        self.assertNotIn("posterior_EEG", nuisance["components"])
        self.assertNotIn(
            "structure_preserving_shifted_central_EEG", nuisance["components"]
        )
        self.assertFalse(nuisance["posterior_EEG_included"])
        self.assertFalse(nuisance["shifted_EEG_included"])
        self.assertFalse(nuisance["deranged_central_EEG_included"])

        counterfactual = roles["physiological_counterfactual"]
        self.assertEqual(
            counterfactual["base_arm"], "joint_physiological_nuisance_only"
        )
        self.assertEqual(
            counterfactual["added_component"],
            "matched_target_blind_structure_preserving_deranged_central_EEG",
        )

    def test_central_correct_window_condition_must_win_every_cube_edge(self) -> None:
        decision = self.value["cube_edge_decision"]
        self.assertEqual(
            decision["required_comparator_edges"],
            [
                "joint_physiological_nuisance_only",
                "joint_physiological_nuisance_plus_matched_deranged_central_EEG",
                "joint_physiological_nuisance_plus_geometry_matched_posterior_visual_EEG_in_correct_motor_window",
                "joint_physiological_nuisance_plus_central_EEG_in_pre_cue_window",
                "joint_physiological_nuisance_plus_central_EEG_in_cue_window",
                "joint_physiological_nuisance_plus_every_preregistered_structure_preserving_shifted_central_EEG_condition",
            ],
        )
        self.assertEqual(
            decision["shared_neural_comparator_base_arm"],
            "joint_physiological_nuisance_only",
        )
        self.assertTrue(
            decision[
                "every_neural_comparator_retains_identical_joint_nuisance_bundle"
            ]
        )
        self.assertTrue(
            decision[
                "central_correct_window_EEG_must_win_every_preregistered_cube_edge"
            ]
        )
        self.assertTrue(decision["intersection_union_rule_required"])
        self.assertFalse(
            decision["one_edge_may_average_away_or_rescue_another_failed_edge"]
        )
        self.assertFalse(decision["beating_no_signal_alone_is_sufficient"])

    def test_parent_conflict_is_observed_without_mutating_parent(self) -> None:
        parent_nuisance = self.parent["joint_comparator_contract"][
            "joint_nuisance_components"
        ]
        parent_conditions = self.parent["required_future_scientific_conditions"]
        self.assertIn("posterior_EEG", parent_nuisance)
        self.assertNotIn("structure_preserving_shifted_EEG", parent_conditions)

        conflict = self.value["parent_interpretive_conflict"]
        self.assertTrue(
            conflict["posterior_EEG_listed_inside_parent_joint_nuisance_components"]
        )
        self.assertTrue(
            conflict[
                "structure_preserving_shifted_EEG_absent_from_parent_required_future_scientific_conditions"
            ]
        )
        self.assertFalse(conflict["parent_bytes_may_be_changed_to_resolve_conflict"])

    def test_every_operational_authority_is_exactly_false(self) -> None:
        expected_keys = {
            "R1_G_scope_expansion",
            "R1_G_official_qualification",
            "generated_implementation_or_execution",
            "network_or_source_contact",
            "real_or_private_data_access",
            "payload_read_or_download",
            "model_or_checkpoint_access",
            "training",
            "inference",
            "prediction_freeze",
            "target_or_label_delivery",
            "scoring",
            "release",
            "scientific_claim_upgrade",
        }
        authority = self.value["authority_state"]
        self.assertEqual(set(authority), expected_keys)
        self.assertTrue(all(value is False for value in authority.values()))
        self.assertTrue(
            all(value == 0 for value in self.value["operation_counters"].values())
        )
        self.assertTrue(
            all(value is False for value in self.value["claim_boundary"].values())
        )

    def test_document_states_required_distinctions_and_boundaries(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        for phrase in (
            "`posterior_EEG` is a separate neural spatial comparator",
            "`structure_preserving_shifted_central_EEG` are separate temporal comparators",
            "task-relevant EMG for every relevant effector",
            "matched, target-blind, structure-preserving deranged central EEG",
            "Every neural comparator retains that identical",
            "The candidate must beat every",
            "does not expand `FMSR1-R1-G-v0`",
            "Every operational authority remains",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
