import hashlib
import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPO_ROOT / "registries" / "loop55_causal_motor_lattice_research.v0.json"
DOC_PATH = REPO_ROOT / "docs" / "LOOP_55_CAUSAL_MOTOR_LATTICE_ARCHITECTURE_RESEARCH.md"
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


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Loop55CausalMotorLatticeResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        cls.doc = DOC_PATH.read_text(encoding="utf-8")

    def test_identity_is_additive_research_only(self):
        registry = self.registry
        self.assertEqual(
            registry["schema_name"],
            "neurodecodekit.loop55_causal_motor_lattice_research",
        )
        self.assertEqual(registry["schema_version"], "0.1.0")
        self.assertEqual(registry["created_at"], "2026-08-06")
        self.assertEqual(registry["architecture"]["candidate_id"], "CML-v0")
        self.assertIn("implementation_not_started", registry["status"])
        self.assertIn("not_a_global_novelty", registry["architecture"]["novelty_boundary"])

    def test_frozen_boundaries_are_hash_bound_and_unamended(self):
        boundary = self.registry["frozen_boundary"]
        pairs = (
            ("loop54_stage_a_research_path", "loop54_stage_a_research_sha256"),
            ("loop54_stage_a_contract_path", "loop54_stage_a_contract_sha256"),
            ("loop55_research_path", "loop55_research_sha256"),
            ("loop55_registry_path", "loop55_registry_sha256"),
            ("loop55_ai_research_path", "loop55_ai_research_sha256"),
            ("loop55_ai_policy_path", "loop55_ai_policy_sha256"),
            ("open_eeg_strategy_path", "open_eeg_strategy_sha256"),
            ("open_eeg_registry_path", "open_eeg_registry_sha256"),
        )
        for path_key, hash_key in pairs:
            with self.subTest(path=boundary[path_key]):
                self.assertEqual(boundary[hash_key], sha256(REPO_ROOT / boundary[path_key]))
        self.assertFalse(boundary["this_artifact_amends_frozen_loop54_or_loop55_artifacts"])
        self.assertFalse(boundary["this_artifact_authorizes_any_real_or_protected_action"])
        self.assertTrue(boundary["loop54_stage_a_replacement_remote_green_required"])

    def test_primary_sources_have_explicit_transfer_ceilings(self):
        sources = self.registry["primary_sources"]
        self.assertEqual(len(sources), 9)
        self.assertEqual(len(sources), len({row["source_id"] for row in sources}))
        self.assertTrue(all(row["url"].startswith("https://") for row in sources))
        self.assertTrue(all(row["transfer_ceiling"] for row in sources))
        by_id = {row["source_id"]: row for row in sources}
        self.assertIn("r=0.73", by_id["brain2qwerty_v1_nature_2026"]["finding"])
        self.assertIn("41.3 percent", by_id["eeg_handwriting_foundation_models_2026"]["finding"])
        self.assertIn("negative transfer", by_id["channel_adaptation_benchmark_2026"]["finding"])
        self.assertIn("forearm EMG", by_id["mrcp_eeg_emg_2026"]["finding"])

    def test_input_contract_is_strictly_causal_and_target_free(self):
        contract = self.registry["architecture"]["input_contract"]
        self.assertEqual(contract["analysis_window_ms_recommendation"], [-500, 0])
        self.assertTrue(contract["right_endpoint_exclusive"])
        self.assertEqual(contract["right_context_ms"], 0)
        self.assertTrue(contract["required_left_filter_context_must_be_strictly_pre_keypress"])
        forbidden = " ".join(contract["forbidden_inputs"])
        for phrase in (
            "marker description",
            "performed key",
            "intended key",
            "sample at or after",
            "EOG EMG",
            "language model",
        ):
            self.assertIn(phrase, forbidden)

    def test_three_views_are_fixed_small_and_failure_addressable(self):
        views = self.registry["architecture"]["views"]
        self.assertEqual([row["view_id"] for row in views], ["CML-V0", "CML-V1", "CML-V2"])
        self.assertEqual([row["name"] for row in views], ["potential_shape", "mu_energy", "beta_energy"])
        self.assertTrue(all(row["spatial_rank"] == 8 for row in views))
        self.assertTrue(all(row["temporal_cells"] == 3 for row in views))
        self.assertTrue(all(row["feature_count"] == 24 for row in views))
        self.assertEqual(sum(row["feature_count"] for row in views), 72)
        self.assertIn("8_to_13", views[1]["frequency_definition"])
        self.assertIn("13_to_30", views[2]["frequency_definition"])
        self.assertIn("does_not_claim", views[0]["claim_limit"])
        spatial = self.registry["architecture"]["spatial_mixer_contract"]
        self.assertEqual(spatial["rank_per_view"], 8)
        self.assertTrue(spatial["learned_row_zero_sum_before_use"])
        self.assertTrue(spatial["learned_row_unit_L2_norm_before_use"])
        self.assertEqual(spatial["added_trainable_parameters"], 0)
        self.assertFalse(spatial["uniform_common_reference_offset_visible_to_mixed_row"])
        self.assertFalse(spatial["invariant_to_every_reference_or_artifact"])

    def test_parameter_formula_is_exact_and_below_existing_cap(self):
        ledger = self.registry["architecture"]["parameter_ledger"]

        def count(channels, primitives):
            return 24 * channels + 2549 + 25 * primitives

        self.assertEqual(ledger["total_formula"], "24*C + 2549 + 25*P")
        self.assertEqual(count(61, 18), ledger["reference_channel_count_61_parameters"])
        self.assertEqual(count(64, 18), ledger["reference_channel_count_64_parameters"])
        self.assertEqual(count(64, 18), 4535)
        self.assertLessEqual(count(291, 18), ledger["existing_parameter_ceiling"])
        self.assertGreater(count(292, 18), ledger["existing_parameter_ceiling"])
        self.assertEqual(ledger["mismatch_action"], "park_without_silent_expansion")

    def test_motor_lattice_enforces_hand_key_consistency_without_text(self):
        lattice = self.registry["architecture"]["motor_lattice"]
        self.assertEqual(lattice["registered_key_class_count"], 29)
        self.assertLessEqual(lattice["maximum_primitive_count"], 18)
        self.assertTrue(lattice["incidence_map_fixed_before_training"])
        self.assertFalse(lattice["incidence_map_may_use_target_frequency_text_or_model_outcome"])
        self.assertFalse(lattice["independent_trainable_hand_head"])
        self.assertFalse(lattice["hand_key_prediction_contradiction_possible"])
        self.assertIn("renormalized_sum", lattice["hand_probability"])
        self.assertIn("tanh", lattice["final_key_logits"])
        self.assertEqual(lattice["residual_gain_range_inclusive"], [0.0, 1.0])
        self.assertFalse(lattice["residual_gain_trainable"])
        self.assertTrue(lattice["residual_gain_frozen_before_any_public_or_protected_payload"])
        self.assertFalse(lattice["intended_text_or_sentence_context_in_loss"])
        self.assertIn("never_post_outcome_assign", lattice["ambiguous_hand_classes"])

    def test_causal_dsp_and_geometry_fail_closed(self):
        dsp = self.registry["architecture"]["causal_dsp_contract"]
        self.assertTrue(dsp["future_exact_coefficients_required"])
        self.assertTrue(dsp["future_frequency_response_required"])
        self.assertTrue(dsp["future_group_delay_required"])
        self.assertFalse(dsp["centered_convolution_allowed"])
        self.assertFalse(dsp["zero_phase_filter_allowed"])
        self.assertFalse(dsp["reflected_future_padding_allowed"])
        geometry = self.registry["architecture"]["geometry_policy"]
        self.assertFalse(geometry["primary_model_requires_geometry"])
        self.assertFalse(geometry["invented_coordinates_allowed"])
        self.assertFalse(geometry["template_montage_interpolation_allowed"])
        self.assertIn("narrow_claim_ceiling", geometry["missing_geometry_action"])

    def test_same_checkpoint_escrow_is_diagnostic_not_claim_evidence(self):
        escrow = self.registry["same_checkpoint_evidence_escrow"]
        self.assertEqual(escrow["parameter_update_runs_added"], 0)
        self.assertEqual(
            [row["probe_id"] for row in escrow["probes"]],
            [f"CML-A{index}" for index in range(8)],
        )
        self.assertTrue(escrow["predictions_freeze_before_selection_or_final_targets"])
        self.assertFalse(escrow["branch_ablation_proves_cortical_physiology"])
        self.assertFalse(escrow["replaces_separately_trained_scientific_controls"])

    def test_two_axis_public_ladder_stays_unopened_and_noninterchangeable(self):
        ladder = self.registry["two_axis_public_qualification_ladder"]
        self.assertIn("cannot_qualify_both", ladder["decision"])
        p1 = ladder["axis_P1_laterality"]
        p2 = ladder["axis_P2_pre_movement_timing"]
        self.assertEqual(p1["public_metadata_bytes"], 23248224)
        self.assertIn("not_downloaded_not_authorized", p1["status"])
        self.assertIn("not_downloaded_not_authorized", p2["status"])
        self.assertEqual(p2["independent_onset_reference"], "forearm_EMG")
        self.assertFalse(p2["exact_file_list_known_now"])
        self.assertFalse(p2["exact_payload_bytes_known_now"])
        self.assertIn("left_right laterality", p2["does_not_qualify"])
        self.assertIn("stop_candidate", ladder["eligibility_rule"]["P1_fail_P2_fail"])

    def test_synthetic_gate_is_bounded_unimplemented_and_not_science(self):
        gate = self.registry["synthetic_factor_isolation_gate"]
        self.assertIn("not_implemented_not_executed", gate["status"])
        self.assertEqual(len(gate["factor_families"]), 8)
        self.assertEqual(gate["maximum_cpu_threads"], 1)
        self.assertEqual(gate["maximum_workers"], 1)
        self.assertLessEqual(gate["maximum_wall_seconds"], 600)
        self.assertLessEqual(gate["maximum_peak_rss_bytes"], 512 * 1024**2)
        self.assertLessEqual(gate["maximum_generated_output_bytes"], 4 * 1024**2)
        self.assertFalse(gate["passing_establishes_real_EEG_effect"])

    def test_current_research_artifacts_fit_the_declared_cap(self):
        artifacts = (REGISTRY_PATH, DOC_PATH, Path(__file__))
        total_bytes = sum(path.stat().st_size for path in artifacts)
        cap = self.registry["resource_boundaries"]["current_research_generated_artifact_cap_bytes"]
        self.assertLess(total_bytes, cap)
        self.assertEqual(self.registry["current_access_counters"]["network_payload_bytes"], 0)

    def test_routes_and_rejected_alternatives_prevent_scale_escalation(self):
        routes = self.registry["hypothesis_routes"]
        self.assertEqual([row["route_id"] for row in routes], [f"CML-R{index}" for index in range(9)])
        alternatives = {row["alternative"]: row for row in self.registry["alternatives_rejected_or_deferred"]}
        self.assertEqual(alternatives["EEG_foundation_model"]["decision"], "deferred_public_data_watch_lane")
        self.assertEqual(alternatives["independent_hand_and_key_heads"]["decision"], "rejected")
        self.assertEqual(alternatives["intended_text_or_language_model_correction"]["decision"], "forbidden")
        self.assertIn("stop at the first failed", " ".join(self.registry["ordered_research_strategy"]))

    def test_every_real_model_and_claim_authorization_and_counter_is_zero(self):
        authorization = dict(self.registry["authorization"])
        self.assertTrue(authorization.pop("planning_research_documentation_tests_commit_and_push_authorized_now"))
        self.assertTrue(authorization.pop("separate_exact_tier_c_decisions_required_for_every_real_stage"))
        self.assertTrue(all(value is False for value in authorization.values()))
        self.assertTrue(all(value == 0 for value in self.registry["current_access_counters"].values()))
        self.assertEqual(self.registry["resource_boundaries"]["new_download_bytes_now"], 0)

    def test_scientific_roadmap_records_architecture_without_execution(self):
        roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        loop55 = next(row for row in roadmap["loops"] if row["loop_id"] == 55)
        self.assertFalse(loop55["execution_authorized"])
        self.assertIn("loop55_causal_motor_lattice_research.v0.json", loop55["build_deliverable"])
        self.assertIn("4,535-parameter", loop55["build_deliverable"])
        self.assertIn("two-axis", " ".join(loop55["controls"]))
        self.assertIn("not implementation or execution permission", loop55["authorization_boundary"])

    def test_document_and_public_surfaces_preserve_the_boundary(self):
        for phrase in (
            "Causal Motor Lattice v0",
            "failure-addressable",
            "Two-Axis Public Qualification Ladder",
            "no independent trainable hand head",
            "4,535",
            "Scientific claim not established:",
        ):
            self.assertIn(phrase, self.doc)
        for path in PUBLIC_STATUS_PATHS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertIn("CML-v0", content)
                self.assertIn("unauthoriz", content.lower())


if __name__ == "__main__":
    unittest.main()
