import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop54_eeg_trial_geometry_research.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_54_PRIMARY_SOURCE_RESEARCH.md"
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


class Loop54EEGTrialGeometryResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {
            path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS
        }

    def test_identity_is_planning_only_and_real_stages_are_unauthorized(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop54_eeg_trial_geometry_research",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["loop_id"], 54)
        self.assertEqual(registry["current_experiment_status"], "Not Started")
        self.assertIn("acquisition_dependent", registry["status"])
        flags = authorization_flags(registry)
        self.assertEqual(flags[0], ("planning_research_authorized_now", True))
        self.assertTrue(all(value is False for _, value in flags[1:]), flags)
        self.assertTrue(
            registry["authorization"][
                "separate_exact_tier_c_authorization_required_for_each_real_stage"
            ]
        )

    def test_loop53_loop35_and_loop36_dependencies_are_hash_bound(self):
        dependencies = self.registry["dependencies"]
        self.assertEqual(
            dependencies["loop53_contract_sha256"],
            "bc7d86a1ce6ef3dc71dacca0af97cb5813df87620ac35d4f34ecd343f97e65ac",
        )
        self.assertEqual(
            dependencies["loop35_contract_sha256"],
            "b68e0721ed964138feb608af404f8e80bc80fa94418215b7efe914cd93de5fcf",
        )
        self.assertEqual(
            dependencies["loop36_contract_sha256"],
            "a621d79a46a8ac20af75cfd077e933a901d4f8a38e39648cdb5e0bff4c6897b4",
        )
        self.assertFalse(dependencies["loop53_status_satisfied_now"])
        self.assertTrue(dependencies["loop55_preregistration_blocked_until_loop54_result"])
        self.assertTrue(dependencies["S7_consumed_and_forbidden"])
        self.assertTrue(dependencies["S21_S24_S25_forbidden"])

    def test_primary_sources_distinguish_header_marker_signal_and_event_roles(self):
        findings = self.registry["primary_source_findings"]
        sources = self.registry["source_bindings"]
        self.assertEqual(len(findings), 6)
        self.assertEqual(len(sources), 6)
        self.assertEqual(
            {row["finding_id"] for row in findings},
            {f"L54-S{index:02d}" for index in range(1, 7)},
        )
        combined = " ".join(row["finding"] for row in findings)
        for term in ("VHDR", "VMRK", "EEG", "annotations", "reference", "61 EEG"):
            self.assertIn(term, combined)

    def test_legacy_extractor_is_explicitly_ineligible_for_claim_path(self):
        audit = self.registry["current_code_audit"]
        self.assertIn("not_eligible", audit["classification"])
        self.assertEqual(len(audit["findings"]), 5)
        self.assertEqual(
            audit["sha256"],
            "6aa8fcfff84a165cd88432bfd27ced3bab36af254261b28642ae12d9529ef7e9",
        )
        combined = " ".join(row["finding"] for row in audit["findings"])
        for term in ("annotations", "EOG", "MAT", "loadmat", "Plaintext labels"):
            self.assertIn(term, combined)
        self.assertEqual(len(audit["required_replacement_properties"]), 5)

    def test_sensitivity_classes_treat_marker_content_as_target_bearing(self):
        classes = self.registry["sensitivity_classes"]
        self.assertEqual([row["class_id"] for row in classes], [f"L54-D{i}" for i in range(5)])
        self.assertFalse(classes[1]["target_bearing"])
        self.assertFalse(classes[2]["target_bearing"])
        self.assertTrue(classes[3]["target_bearing"])
        self.assertTrue(classes[4]["target_bearing"])
        self.assertIn("marker description", " ".join(classes[4]["examples"]))

    def test_stage_inputs_are_disjoint_and_ordered(self):
        stages = self.registry["future_stage_protocol"]
        self.assertEqual([row["stage_id"] for row in stages], ["L54-A", "L54-B", "L54-C", "L54-D"])
        stage_a, stage_b, stage_c, stage_d = stages
        self.assertFalse(stage_a["mne_reader_allowed"])
        self.assertEqual(stage_a["allowed_inputs"], ["020_DECOMEG_S2_11966_task2.vhdr"])
        self.assertEqual(
            stage_b["allowed_inputs"],
            ["020_DECOMEG_S2_11966_task2.vhdr", "020_DECOMEG_S2_11966_task2.eeg"],
        )
        self.assertNotIn("020_DECOMEG_S2_11966_task2.vmrk", stage_b["allowed_inputs"])
        self.assertNotIn("S20_session2_block2_list1.mat", stage_b["allowed_inputs"])
        self.assertNotIn("020_DECOMEG_S2_11966_task2.eeg", stage_c["allowed_inputs"])
        self.assertTrue(stage_c["isolated_process_required"])
        self.assertFalse(stage_c["plaintext_marker_description_or_target_in_public_output"])
        self.assertNotIn("raw S20 payload", stage_d["allowed_inputs"])

    def test_channel_preservation_and_no_transform_policy_are_strict(self):
        stage_b = self.registry["future_stage_protocol"][1]
        self.assertTrue(stage_b["all_source_channels_retained"])
        forbidden = set(stage_b["forbidden_transforms"])
        self.assertTrue(
            {
                "EOG exclusion",
                "channel deletion",
                "rereference",
                "interpolation",
                "ICA",
                "filtering",
                "resampling",
                "target-aligned windowing",
            }.issubset(forbidden)
        )
        self.assertFalse(stage_b["raw_signal_derivative_allowed"])

    def test_trial_unit_floor_and_future_split_firewall_are_exact(self):
        rules = self.registry["future_trial_and_split_rules"]
        self.assertEqual(rules["minimum_unique_performed_trials_for_loop54_acceptance"], 48)
        self.assertTrue(rules["trial_is_unit_of_identity_and_future_inference"])
        self.assertTrue(rules["event_windows_are_not_independent_trials"])
        self.assertFalse(rules["training_validation_test_split_created_in_loop54"])
        self.assertFalse(rules["exact_loop55_partition_counts_known_now"])
        self.assertTrue(rules["target_values_may_not_choose_partitions"])
        self.assertEqual(rules["if_usable_unique_trials_below_48"], "park_without_training")

    def test_resources_gates_refusals_and_current_access_are_bounded(self):
        resources = self.registry["resource_boundaries"]
        self.assertEqual(resources["cpu_threads_per_future_stage"], 1)
        self.assertEqual(resources["workers_per_future_stage"], 1)
        self.assertLessEqual(resources["maximum_future_peak_rss_bytes"], 1024**3)
        self.assertLessEqual(
            resources["maximum_combined_generated_public_output_bytes"], 32 * 1024**2
        )
        self.assertEqual(resources["new_download_bytes"], 0)
        self.assertEqual(len(self.registry["future_acceptance_gates"]), 22)
        refusals = self.registry["future_refusal_ids"]
        self.assertEqual(len(refusals), 30)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L54-F{index:02d}" for index in range(1, 31)],
        )
        counters = self.registry["research_access_counters"]
        protected = {key: value for key, value in counters.items() if key.startswith("S20_")}
        self.assertTrue(all(value == 0 for value in protected.values()))
        for key in (
            "target_or_label_reads",
            "model_inference_runs",
            "training_or_parameter_update_runs",
            "scoring_runs",
            "downloads",
            "device_or_hardware_operations",
            "generated_experiment_bytes",
        ):
            self.assertEqual(counters[key], 0, key)

    def test_claims_and_docs_keep_science_unavailable(self):
        claims = self.registry["future_claim_classes"]
        self.assertEqual(len(claims), 7)
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        self.assertIn("Never available", claims[-1]["boundary"])
        for phrase in (
            "planning research complete",
            "experiment `Not Started`",
            "MNE is disallowed",
            "at least 48 unique performed trials",
            "32 MiB",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.research)

    def test_scientific_roadmap_marks_loop54_research_complete_but_unauthorized(self):
        loop54 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 54)
        self.assertEqual(loop54["status"], "Planning Research Complete; Acquisition Dependent")
        self.assertFalse(loop54["execution_authorized"])
        self.assertIn("loop54_eeg_trial_geometry_research.v0.json", loop54["build_deliverable"])
        self.assertIn("does not create a split", loop54["build_deliverable"])
        self.assertIn("separate exact Tier C", loop54["authorization_boundary"])

    def test_public_status_surfaces_share_the_loop54_boundary(self):
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 54", content)
                self.assertIn("VHDR", content)
                self.assertIn("VMRK", content)
                self.assertIn("48", content)
                self.assertIn("unauthoriz", content.lower())


if __name__ == "__main__":
    unittest.main()
