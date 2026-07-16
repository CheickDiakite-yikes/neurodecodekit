import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    REPO_ROOT
    / "registries"
    / "loop56_cross_modality_accessibility_research.v0.json"
)
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_56_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_scientific_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "BUILD_NOTES.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "DECISIONS.md",
    REPO_ROOT / "docs" / "LOOPS_45_64_SCIENTIFIC_ROADMAP.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "prompts" / "CODEX_START_PROMPT.md",
)


def authorization_flags(value):
    flags = []
    if isinstance(value, dict):
        for key, nested in value.items():
            if key.endswith("authorized_now"):
                flags.append((key, nested))
            flags.extend(authorization_flags(nested))
    elif isinstance(value, list):
        for nested in value:
            flags.extend(authorization_flags(nested))
    return flags


class Loop56CrossModalityAccessibilityResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_planning_only_and_verdict_is_unauthorized(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop56_cross_modality_accessibility_research",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["loop_id"], 56)
        self.assertEqual(registry["current_verdict_status"], "Not Started")
        self.assertIn("loop55_result_dependent", registry["status"])
        flags = authorization_flags(registry)
        self.assertEqual(flags[0], ("planning_research_authorized_now", True))
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(
            registry["authorization"][
                "separate_exact_tier_c_claim_decision_required_for_final_verdict"
            ]
        )

    def test_dependencies_are_hash_bound_and_pending_results_stay_unavailable(self):
        dependencies = self.registry["dependencies"]
        expected = {
            "loop15_cross_session_sha256": "2890a94abf3ce469ebb0d14c58da7b24492d4dcaa225f194fdb1a02cd5587d18",
            "loop19_eeg_bridge_sha256": "c778d15c51ca43a638df51cb1251c74105467b59ac65b6a8e35c845bcfcf4930",
            "loop26_shared_validation_result_sha256": "7577c84eaea7579250b5c1fcdf53234a3d56fdab4640df2edebaee9ae8bd31b4",
            "loop29_modality_sha256": "22a514203413107c2c4a0ce6827d43d50ec65fe0e647e43d4bedacc62f1b0811",
            "loop36_geometry_sha256": "a621d79a46a8ac20af75cfd077e933a901d4f8a38e39648cdb5e0bff4c6897b4",
            "loop42_device_sha256": "5274dfa5e1ec0535a8b4a068268249c7f0fd5062c5b9ad19e6d4f24e81feb994",
            "loop54_qualification_research_sha256": "ab158abf5b7425c63c66e201ed341c096b9a622aff0eef8ba1b3bdeacf7f5ec7",
            "loop55_effect_research_sha256": "032157b8a90be68a16cc5963bf0c1c513e626a50b417b1e76ce7c06715d9c9af",
        }
        for key, expected_hash in expected.items():
            self.assertEqual(dependencies[key], expected_hash, key)
            path_key = key.replace("_sha256", "_path")
            path = REPO_ROOT / dependencies[path_key]
            actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(actual_hash, expected_hash, path)
        self.assertFalse(dependencies["loop54_final_result_exists_now"])
        self.assertFalse(dependencies["loop55_final_result_exists_now"])
        self.assertTrue(dependencies["S20_S24_S25_payload_access_forbidden"])

    def test_sources_define_seven_nontransferable_findings(self):
        findings = self.registry["primary_source_findings"]
        sources = self.registry["source_bindings"]
        self.assertEqual(len(findings), 7)
        self.assertEqual(len(sources), 7)
        self.assertEqual(
            [row["finding_id"] for row in findings],
            [f"L56-S{index:02d}" for index in range(1, 8)],
        )
        combined = " ".join(row["finding"] for row in findings)
        for phrase in (
            "61 EEG plus three ocular channels",
            "29 percent for MEG and 65 percent for EEG",
            "Continuous input is a distinct capability",
            "noncausal",
            "EEG reference scheme",
            "sensor equivalence",
            "Packet mechanics do not establish",
        ):
            self.assertIn(phrase, combined)

    def test_verdict_classes_are_complete_and_forbid_signal_transfer(self):
        classes = self.registry["verdict_classes"]
        self.assertEqual(
            [row["class_id"] for row in classes],
            [f"L56-X{index}" for index in range(5)],
        )
        self.assertEqual(
            [row["name"] for row in classes],
            [
                "shared_proven_artifact",
                "shared_interface_only",
                "modality_specific_requalification",
                "unavailable",
                "prohibited_inference",
            ],
        )
        self.assertFalse(classes[0]["score_or_signal_value_may_use_class"])
        self.assertIn("home EEG decoding", classes[-1]["example"])

    def test_capability_ladder_is_ordered_and_non_skippable(self):
        ladder = self.registry["capability_ladder"]
        self.assertEqual(
            [row["level_id"] for row in ladder],
            [f"L56-C{index}" for index in range(12)],
        )
        self.assertEqual(ladder[6]["name"], "continuous_input")
        self.assertEqual(ladder[7]["name"], "causal_incremental_output")
        self.assertEqual(ladder[8]["name"], "measured_end_to_end_latency")
        semantics = self.registry["capability_semantics"]
        self.assertTrue(all(value is False for value in semantics.values()))

    def test_local_results_remain_negative_or_unavailable_not_comparative(self):
        local = self.registry["current_local_evidence"]
        meg = local["cryogenic_MEG"]
        eeg = local["scalp_EEG"]
        self.assertIn("worse_than_prior_by_0_142491", meg["same_person_cross_session_prediction"]["status"])
        self.assertIn("macro_CER_0_938177_prior_0_751235", meg["registered_sensor_signal_effect"]["status"])
        self.assertIn("accuracy_0_009091_prior_0_122727", eeg["historical_sensor_signal_effect"]["status"])
        self.assertIn("removed_EOG", eeg["historical_fresh_claim_eligibility"]["status"])
        self.assertIn("loop54_not_executed", eeg["fresh_signal_quality_and_trials"]["status"])
        self.assertIn("loop55_not_executed", eeg["fresh_causal_hand_or_key_effect"]["status"])
        self.assertEqual(self.registry["provisional_outcome_id"], "L56-O2")

    def test_external_results_cannot_reverse_or_pool_with_local_evidence(self):
        external = self.registry["external_evidence_separation"]
        v1 = external["brain2qwerty_v1"]
        self.assertEqual(v1["MEG_mean_sentence_CER"], 0.29)
        self.assertEqual(v1["EEG_mean_sentence_CER"], 0.65)
        self.assertFalse(v1["may_define_local_threshold"])
        self.assertFalse(v1["may_reverse_local_negative_result"])
        self.assertFalse(v1["may_be_pooled_with_local_scores"])
        v2 = external["brain2qwerty_v2"]
        self.assertTrue(v2["continuous_input"])
        self.assertFalse(v2["causal_architecture"])
        self.assertTrue(v2["entire_sentence_context"])
        self.assertFalse(v2["EEG_evidence"])
        self.assertFalse(v2["home_device_evidence"])

    def test_dimension_matrix_preserves_modality_specific_values(self):
        matrix = self.registry["dimension_matrix"]
        self.assertEqual(len(matrix), 18)
        self.assertEqual(
            [row["dimension_id"] for row in matrix],
            [f"L56-D{index:02d}" for index in range(1, 19)],
        )
        self.assertTrue(all(row["score_pooling_allowed"] is False for row in matrix))
        names = {row["name"] for row in matrix}
        for expected in (
            "source_identity_and_provenance",
            "sensor_electrode_and_channel_ontology",
            "geometry_frame_orientation_and_transforms",
            "continuous_causal_and_latency_status",
            "device_burden_portability_home_use_and_safety",
        ):
            self.assertIn(expected, names)

    def test_claim_contract_and_at_home_conjunction_are_complete(self):
        fields = self.registry["claim_sentence_required_fields"]
        self.assertEqual(len(fields), 16)
        for phrase in (
            "evidence origin",
            "performed versus intended",
            "causal or noncausal",
            "language model contribution",
            "warnings and unavailable",
        ):
            self.assertIn(phrase, " ".join(fields))
        self.assertEqual(len(self.registry["at_home_conjunction"]), 12)
        self.assertFalse(self.registry["at_home_conjunction_complete_now"])
        self.assertFalse(
            self.registry[
                "openbci_specification_satisfies_complete_at_home_conjunction"
            ]
        )

    def test_future_verdict_is_artifact_only_and_cannot_create_new_science(self):
        verdict = self.registry["future_artifact_only_verdict"]
        self.assertIn("not_started", verdict["status"])
        self.assertIn("committed aggregate", verdict["allowed_input_class"])
        self.assertFalse(verdict["raw_ignored_private_or_protected_input_allowed"])
        self.assertFalse(verdict["cache_array_target_prediction_checkpoint_or_model_input_allowed"])
        self.assertFalse(verdict["score_recomputation_allowed"])
        self.assertTrue(verdict["separate_exact_tier_c_claim_decision_required"])
        self.assertEqual(
            [row["outcome_id"] for row in self.registry["outcome_taxonomy"]],
            [f"L56-O{index}" for index in range(8)],
        )
        self.assertIn("new neural advantage", self.registry["claim_boundary"]["claims_never_created_by_loop56"])

    def test_resources_gates_refusals_and_current_access_are_bounded(self):
        resources = self.registry["resource_boundaries"]
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["maximum_wall_time_seconds"], 600)
        self.assertEqual(resources["maximum_peak_rss_bytes"], 256 * 1024**2)
        self.assertEqual(resources["maximum_generated_output_bytes"], 16 * 1024**2)
        self.assertEqual(len(self.registry["future_acceptance_gates"]), 28)
        refusals = self.registry["future_refusal_ids"]
        self.assertEqual(len(refusals), 34)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L56-F{index:02d}" for index in range(1, 35)],
        )
        counters = self.registry["research_access_counters"]
        for key, value in counters.items():
            if key not in {
                "public_primary_or_official_sources_consulted",
                "committed_local_evidence_boundaries_read",
            }:
                self.assertEqual(value, 0, key)

    def test_research_doc_keeps_claim_ceiling_explicit(self):
        for phrase in (
            "Planning research is complete",
            "verdict remains `Not Started`",
            "Continuous input is not causal real-time output",
            "Five Verdict Classes",
            "Capability Ladder",
            "Eighteen-Dimension Verdict Matrix",
            "16 claim fields",
            "28 acceptance gates",
            "34 refusal",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.research)

    def test_scientific_roadmap_marks_research_complete_but_verdict_unauthorized(self):
        loop56 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 56)
        self.assertEqual(loop56["status"], "Planning Research Complete; Loop 55 Result Dependent")
        self.assertFalse(loop56["execution_authorized"])
        self.assertIn("loop56_cross_modality_accessibility_research.v0.json", loop56["build_deliverable"])
        self.assertIn("not equivalence", loop56["scientific_claim_target"])
        self.assertIn("separate exact Tier C", loop56["authorization_boundary"])

    def test_public_status_surfaces_share_the_loop56_boundary(self):
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 56", content)
                self.assertIn("cross-modality", content.lower())
                self.assertIn("authoriz", content.lower())


if __name__ == "__main__":
    unittest.main()
