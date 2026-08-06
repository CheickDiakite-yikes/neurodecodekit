import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "open_eeg_rd_strategy.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "OPEN_EEG_R_AND_D_STRATEGY_2026-08-06.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class OpenEEGRDStrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_and_status_are_planning_only(self):
        registry = self.registry
        self.assertEqual(registry["schema_name"], "neurodecodekit.open_eeg_rd_strategy")
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["created_at"], "2026-08-06")
        self.assertIn("no_execution_authorized", registry["status"])
        self.assertIn("positive_control", registry["decision"])

    def test_frozen_loop54_and_loop55_artifacts_are_hash_bound(self):
        boundary = self.registry["frozen_boundary"]
        for path_key, hash_key in (
            ("loop54_stage_a_contract_path", "loop54_stage_a_contract_sha256"),
            ("loop55_research_path", "loop55_research_sha256"),
            ("loop55_registry_path", "loop55_registry_sha256"),
            ("loop55_ai_research_path", "loop55_ai_research_sha256"),
            ("loop55_ai_policy_path", "loop55_ai_policy_sha256"),
        ):
            with self.subTest(path=boundary[path_key]):
                self.assertEqual(boundary[hash_key], sha256(REPO_ROOT / boundary[path_key]))
        self.assertTrue(boundary["loop54_stage_a_registration_must_remain_immutable"])
        self.assertTrue(boundary["loop54_stage_a_authorization_still_pending"])
        self.assertFalse(boundary["this_strategy_amends_frozen_artifacts"])
        self.assertFalse(boundary["this_strategy_authorizes_any_real_action"])

    def test_primary_sources_support_specialist_and_artifact_decisions(self):
        sources = {row["source_id"]: row for row in self.registry["source_snapshots"]}
        self.assertEqual(
            set(sources),
            {
                "eeg_fm_compass",
                "steegformer",
                "preprocessing_multiverse",
                "typewriting_motor_potentials",
                "premovement_direction_decoding",
                "physionet_eegmmidb",
                "mne_eegbci_run_map",
            },
        )
        self.assertIn(
            "specialist models remain competitive",
            sources["eeg_fm_compass"]["finding"],
        )
        self.assertIn("structured noise", sources["preprocessing_multiverse"]["finding"])
        self.assertIn("before movement onset", sources["premovement_direction_decoding"]["finding"])
        self.assertEqual(sources["physionet_eegmmidb"]["license"], "Open_Data_Commons_Attribution_1.0")

    def test_tool_adoption_is_optional_bounded_and_unique(self):
        tools = self.registry["tool_matrix"]
        self.assertEqual(len(tools), len({row["tool_id"] for row in tools}))
        self.assertEqual(
            {row["tool_id"] for row in tools},
            {
                "mne",
                "moabb",
                "braindecode",
                "pyriemann",
                "mne_bids",
                "open_eeg_bench",
                "zuna_1_1",
            },
        )
        self.assertTrue(all(not row["base_dependency"] for row in tools))
        by_id = {row["tool_id"]: row for row in tools}
        self.assertFalse(by_id["moabb"]["automatic_download_allowed"])
        self.assertFalse(by_id["open_eeg_bench"]["default_all_dataset_download_allowed"])
        self.assertFalse(by_id["zuna_1_1"]["primary_input_imputation_allowed"])

    def test_public_positive_control_is_exact_small_and_unauthorized(self):
        prospect = self.registry["public_positive_control_prospect"]
        self.assertEqual(prospect["status"], "research_only_not_preregistered_not_authorized")
        self.assertEqual(prospect["subjects"], ["S001", "S002", "S003"])
        self.assertEqual(prospect["runs"], [3, 7, 11])
        self.assertEqual(len(prospect["files"]), 9)
        self.assertEqual(
            prospect["total_public_metadata_size_bytes"],
            sum(row["public_metadata_size_bytes"] for row in prospect["files"]),
        )
        self.assertEqual(prospect["total_public_metadata_size_bytes"], 23248224)
        self.assertLess(
            prospect["total_public_metadata_size_bytes"],
            prospect["future_network_cap_bytes"],
        )
        self.assertEqual(prospect["prospective_fit_runs"], [3, 7])
        self.assertEqual(prospect["prospective_frozen_check_run"], 11)
        self.assertTrue(prospect["separate_exact_tier_c_contract_required"])
        self.assertFalse(prospect["download_or_payload_access_authorized_now"])

    def test_loop55_refresh_preserves_endpoints_caps_and_target_firewall(self):
        refresh = self.registry["future_loop55_design_refresh"]
        self.assertEqual(refresh["ordered_endpoints"][0], "causal_pre_keypress_performed_hand")
        self.assertTrue(refresh["physiology_assay"]["causal_pre_keypress_only"])
        self.assertTrue(refresh["physiology_assay"]["trial_level_aggregation"])
        self.assertTrue(refresh["classical_family_selected_only_from_public_positive_control"])
        self.assertFalse(refresh["S20_selection_or_final_targets_may_choose_family"])
        self.assertFalse(refresh["foundation_model_or_pretrained_weight_allowed"])
        self.assertFalse(refresh["language_model_or_target_text_allowed"])
        self.assertTrue(refresh["existing_10000_parameter_compact_ceiling_preserved"])
        self.assertTrue(refresh["existing_12_fit_ceiling_preserved"])

    def test_foundation_models_remain_a_deferred_separate_lane(self):
        gate = self.registry["foundation_model_gate"]
        self.assertEqual(gate["status"], "deferred_watch_lane")
        self.assertIn("compact_specialist_S20_result_is_frozen", gate["eligible_only_after"])
        self.assertEqual(
            set(gate["must_separate"]),
            {
                "frozen_linear_or_ridge_probe",
                "parameter_efficient_finetuning",
                "full_parameter_finetuning",
            },
        )
        self.assertFalse(gate["generative_imputation_may_support_primary_evidence"])
        self.assertFalse(gate["protected_final_targets_may_select_model_or_strategy"])

    def test_open_cohort_design_is_local_first_and_privacy_bounded(self):
        federation = self.registry["open_cohort_federation"]
        self.assertFalse(federation["raw_data_upload_default"])
        self.assertTrue(federation["local_validation_required"])
        self.assertFalse(federation["plaintext_targets_in_public_receipt"])
        self.assertFalse(federation["absolute_local_paths_in_public_receipt"])
        self.assertTrue(
            federation["raw_release_requires_separate_consent_license_and_repository_decision"]
        )
        self.assertTrue(federation["matched_protocol_required_for_scientific_aggregation"])

    def test_all_real_execution_authorizations_and_counters_are_zero(self):
        authorization = dict(self.registry["authorization"])
        self.assertTrue(authorization.pop("planning_research_and_documentation_authorized_now"))
        self.assertTrue(all(value is False for value in authorization.values()))
        self.assertTrue(all(value == 0 for value in self.registry["current_access_counters"].values()))

    def test_human_document_discloses_tools_order_and_nonclaims(self):
        for phrase in (
            "NeuroDecodeKit is still on the right path",
            "Known-Effect Positive Control",
            "A Specialist Baseline Triangle",
            "Open Cohort Federation",
            "No package in this table becomes a base dependency",
            "No PhysioNet file was downloaded or opened",
            "Scientific claim not established",
        ):
            self.assertIn(phrase, self.doc)


if __name__ == "__main__":
    unittest.main()
