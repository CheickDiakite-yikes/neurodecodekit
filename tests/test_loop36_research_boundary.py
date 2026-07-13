import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_PATH = REPO_ROOT / "registries" / "loop36_research_boundary.v0.json"
RESEARCH_PATH = REPO_ROOT / "docs" / "LOOP_36_PRIMARY_SOURCE_RESEARCH.md"
ROADMAP_PATH = REPO_ROOT / "registries" / "next_20_loops.v0.json"
PUBLIC_STATUS_PATHS = (
    REPO_ROOT / "AGENTS.md",
    REPO_ROOT / "README.md",
    REPO_ROOT / "START_HERE.md",
    REPO_ROOT / "docs" / "CODEX_HANDOFF.md",
    REPO_ROOT / "docs" / "NEXT_20_LOOPS_TRACKER.md",
    REPO_ROOT / "docs" / "POST_20_ROADMAP.md",
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


class Loop36ResearchBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.boundary = json.loads(BOUNDARY_PATH.read_text(encoding="utf-8"))
        cls.research = RESEARCH_PATH.read_text(encoding="utf-8")
        cls.roadmap = json.loads(ROADMAP_PATH.read_text(encoding="utf-8"))
        cls.public_status = {path: path.read_text(encoding="utf-8") for path in PUBLIC_STATUS_PATHS}

    def test_identity_is_planning_only_and_all_authorizations_are_false(self):
        boundary = self.boundary
        self.assertEqual(boundary["schema_name"], "neurodecodekit.loop36_research_boundary")
        self.assertEqual(boundary["schema_version"], "0.1.0")
        self.assertEqual(boundary["status"], "planning_research_complete_experiment_not_started")
        self.assertIn("planning_only", boundary["proof_posture"])
        flags = authorization_flags(boundary)
        self.assertEqual(len(flags), 29)
        self.assertTrue(all(value is False for _, value in flags), flags)
        self.assertFalse(boundary["authorization"]["authorization_sentence_exists"])

    def test_decision_caps_metadata_and_numerical_claims(self):
        decision = self.boundary["decision"]
        self.assertEqual(decision["current_experiment_status"], "Not Started")
        self.assertEqual(decision["maximum_current_claim_class"], "L36-C0_no_new_result")
        self.assertEqual(
            decision["maximum_future_real_metadata_claim"],
            "L36-C2_declared_metadata_compatibility",
        )
        self.assertEqual(
            decision["maximum_future_signal_transform_claim"],
            "L36-C4_named_protocol_specific_numerical_compatibility",
        )
        self.assertFalse(decision["channel_name_equivalence_available_from_name_alone"])
        self.assertFalse(decision["device_equivalence_available_from_shared_channel_count"])
        self.assertFalse(decision["geometry_equivalence_available_from_visual_similarity"])
        self.assertEqual(decision["unknown_frame_or_reference_default"], "unavailable")

    def test_dependencies_keep_real_geometry_and_devices_unavailable(self):
        dependencies = self.boundary["dependencies"]
        self.assertTrue(dependencies["loop29_planning_dependency_satisfied_now"])
        self.assertFalse(dependencies["loop29_device_selected_now"])
        self.assertFalse(dependencies["loop29_real_header_or_signal_evidence_available_now"])
        self.assertTrue(dependencies["loop30_clock_contract_required_for_time_varying_geometry"])
        self.assertTrue(dependencies["loop35_peripheral_motion_geometry_boundary_required"])
        self.assertFalse(dependencies["existing_s21_geometry_is_complete_loop36_evidence"])
        self.assertFalse(
            dependencies["existing_s7_eeg_geometry_and_reference_are_complete_loop36_evidence"]
        )

    def test_existing_evidence_has_eight_rows_and_no_payload_reads(self):
        evidence = {row["evidence_id"]: row for row in self.boundary["existing_evidence_inventory"]}
        self.assertEqual(len(evidence), 8)
        self.assertIn("102", evidence["s21_channel_subset_boundary"]["finding"])
        self.assertIn("61 EEG", evidence["s7_eeg_boundary"]["finding"])
        self.assertIn(
            "exact channel-name order", evidence["cross_session_exact_identity"]["finding"]
        )
        self.assertTrue(all(row["payload_read_now"] is False for row in evidence.values()))

    def test_six_representation_layers_do_not_infer_missing_semantics(self):
        layers = self.boundary["representation_layers"]
        self.assertEqual(len(layers), 6)
        self.assertEqual(
            [row["layer_id"].split("_", 1)[0] for row in layers],
            [f"L36-L{index}" for index in range(6)],
        )
        self.assertTrue(all(row["may_be_inferred"] is False for row in layers))
        combined = " ".join(row["content"] for row in layers)
        for term in (
            "source cache hash",
            "ordered unique",
            "signal unit",
            "orientation",
            "4x4",
            "reference",
        ):
            self.assertIn(term, combined)

    def test_five_modality_profiles_keep_sensor_types_separate(self):
        profiles = self.boundary["modality_profiles"]
        self.assertEqual(len(profiles), 5)
        ids = [row["profile_id"].split("_", 1)[0] for row in profiles]
        self.assertEqual(ids, [f"L36-M{index}" for index in range(5)])
        self.assertEqual(profiles[0]["signal_units"], ["T", "fT"])
        self.assertIn("T/m", profiles[1]["signal_units"])
        self.assertIn("time_bound_position", profiles[2]["required_geometry"])
        self.assertIn("acquisition_reference", profiles[3]["reference_scheme"])
        self.assertEqual(profiles[4]["may_mix_with"], ["exact_same_declared_type_only"])

    def test_channel_record_has_twenty_four_unique_fields(self):
        fields = self.boundary["future_channel_record_fields"]
        self.assertEqual(len(fields), 24)
        self.assertEqual(len(fields), len(set(fields)))
        for field in (
            "source_name",
            "canonical_name",
            "signal_unit_scale_to_si",
            "position_valid_mask",
            "orientation_valid_mask",
            "reference_and_ground",
            "transform_chain_ids",
            "source_metadata_sha256",
        ):
            self.assertIn(field, fields)

    def test_twelve_operations_distinguish_identity_from_data_changes(self):
        operations = self.boundary["operation_taxonomy"]
        self.assertEqual(len(operations), 12)
        self.assertEqual(
            [row["operation_id"].split("_", 1)[0] for row in operations],
            [f"L36-O{index:02d}" for index in range(12)],
        )
        self.assertFalse(operations[0]["requires_signal_values"])
        self.assertFalse(operations[4]["requires_signal_values"])
        self.assertTrue(operations[6]["requires_signal_values"])
        self.assertIn("imputation", operations[8]["class"])
        self.assertEqual(operations[-1]["class"], "forbidden_evaluation_leakage")

    def test_alias_and_unit_policies_fail_closed(self):
        aliases = self.boundary["alias_policy"]
        self.assertTrue(aliases["source_names_must_be_unique"])
        self.assertFalse(aliases["casefold_or_strip_punctuation_automatically"])
        self.assertFalse(aliases["position_only_aliasing_allowed"])
        self.assertTrue(aliases["explicit_versioned_bijective_alias_map_required"])
        self.assertFalse(aliases["one_to_many_or_many_to_one_alias_allowed"])
        units = self.boundary["unit_policy"]
        self.assertTrue(units["signal_and_coordinate_units_are_separate"])
        self.assertEqual(
            units["coordinate_scale_factors_to_m"], {"m": 1.0, "cm": 0.01, "mm": 0.001}
        )
        self.assertFalse(units["unit_may_be_inferred_from_magnitude"])
        self.assertEqual(units["unknown_or_custom_unit_without_definition"], "unavailable")

    def test_rigid_transform_is_directional_right_handed_and_roundtrip_bound(self):
        policy = self.boundary["rigid_transform_policy"]
        self.assertEqual(policy["matrix_shape"], [4, 4])
        self.assertEqual(policy["homogeneous_last_row"], [0.0, 0.0, 0.0, 1.0])
        self.assertEqual(policy["rotation_determinant_target"], 1.0)
        self.assertFalse(policy["reflection_allowed"])
        self.assertTrue(policy["source_and_destination_frames_required"])
        self.assertTrue(policy["transform_direction_required"])
        self.assertEqual(policy["inverse_roundtrip_residual_max_m"], 1e-9)
        self.assertTrue(policy["position_and_orientation_transformed_separately"])
        self.assertFalse(policy["translation_applies_to_orientation"])

    def test_reference_and_interpolation_remain_data_changing(self):
        policy = self.boundary["reference_and_interpolation_policy"]
        self.assertTrue(policy["acquisition_reference_and_ground_preserved"])
        self.assertTrue(policy["derived_reference_operator_preserved"])
        self.assertFalse(policy["rereference_is_metadata_only"])
        self.assertFalse(policy["interpolation_is_geometry_identity"])
        self.assertTrue(policy["interpolated_channels_retain_source_missingness_flag"])
        self.assertFalse(policy["template_montage_may_replace_measured_positions"])
        self.assertTrue(
            policy["meg_compensation_and_projectors_must_match_or_be_transformed_explicitly"]
        )

    def test_fixture_and_access_sequences_are_bounded_and_ordered(self):
        fixtures = self.boundary["future_fixture_families"]
        self.assertEqual(len(fixtures), 16)
        self.assertEqual(len(fixtures), len(set(fixtures)))
        combined = " ".join(fixtures)
        for term in (
            "duplicate",
            "unit",
            "rigid",
            "reflection",
            "orientation",
            "reference",
            "interpolation",
            "accuracy",
        ):
            self.assertIn(term, combined)
        sequence = self.boundary["future_access_sequence"]
        self.assertEqual(len(sequence), 10)
        self.assertLess(
            sequence.index(
                "record a separate authorization-only decision commit and obtain green remote CI"
            ),
            sequence.index(
                "generate only target-free synthetic metadata fixtures under the Stage A cap"
            ),
        )
        self.assertLess(
            sequence.index(
                "authorize and inspect only declared headers without opening signal arrays"
            ),
            sequence.index(
                "obtain separate signal-transform authorization if rereference interpolation or unit scaling is needed"
            ),
        )

    def test_outcomes_and_claims_are_exact_and_fail_closed(self):
        outcomes = self.boundary["outcome_taxonomy"]
        claims = self.boundary["claim_taxonomy"]
        self.assertEqual(len(outcomes), 8)
        self.assertEqual(
            [row["outcome_id"].split("_", 1)[0] for row in outcomes],
            [f"L36-R{index}" for index in range(8)],
        )
        self.assertEqual(len(claims), 7)
        self.assertEqual(
            [row["claim_id"].split("_", 1)[0] for row in claims],
            [f"L36-C{index}" for index in range(7)],
        )
        self.assertTrue(claims[0]["available_now"])
        self.assertTrue(all(row["available_now"] is False for row in claims[1:]))
        self.assertIn("metadata", claims[2]["boundary"].lower())
        self.assertIn("separately authorized", claims[4]["boundary"])

    def test_gates_and_refusals_are_exact_and_comprehensive(self):
        gates = self.boundary["future_acceptance_gates"]
        refusals = self.boundary["future_refusal_ids"]
        self.assertEqual(len(gates), 22)
        self.assertEqual(
            [row["requirement_id"].split("_", 1)[0] for row in gates],
            [f"L36-G{index:02d}" for index in range(1, 23)],
        )
        self.assertEqual(len(refusals), 30)
        self.assertEqual(
            [row.split("_", 1)[0] for row in refusals],
            [f"L36-F{index:02d}" for index in range(1, 31)],
        )
        combined = " ".join(refusals)
        for term in (
            "duplicate",
            "alias",
            "unit",
            "frame",
            "transform",
            "reflection",
            "orientation",
            "reference",
            "interpolation",
            "accuracy",
            "hash",
            "overclaim",
        ):
            self.assertIn(term, combined)

    def test_resources_and_access_counters_remain_zero_or_unavailable(self):
        resources = self.boundary["resource_boundaries"]
        self.assertEqual(resources["current_cpu_threads"], 1)
        self.assertEqual(resources["current_generated_artifact_bytes"], 0)
        self.assertEqual(resources["future_stage_a_runtime_cap_sec"], 120)
        self.assertEqual(resources["future_stage_a_peak_rss_cap_bytes"], 1024**3)
        self.assertEqual(resources["future_stage_a_generated_artifact_cap_bytes"], 16 * 1024**2)
        self.assertIsNone(resources["future_real_header_byte_cap"])
        self.assertIsNone(resources["future_signal_transform_byte_cap"])
        self.assertTrue(resources["mne_remains_optional"])
        counters = self.boundary["research_access_counters"]
        self.assertEqual(counters["high_level_public_web_research_operations"], 3)
        excluded = {
            "high_level_public_web_research_operations",
            "public_network_response_bytes",
            "public_network_response_bytes_unavailable_reason",
        }
        numeric = [
            value
            for key, value in counters.items()
            if key not in excluded and isinstance(value, int)
        ]
        self.assertTrue(all(value == 0 for value in numeric))

    def test_primary_sources_and_human_note_preserve_claim_boundary(self):
        sources = self.boundary["source_bindings"]
        self.assertEqual(len(sources), 9)
        source_ids = {row["source_id"] for row in sources}
        self.assertTrue(
            {
                "bids_coordinate_systems",
                "bids_meg",
                "bids_eeg",
                "bids_units",
                "mne_coordinate_frames",
                "mne_transform",
                "mne_digmontage",
                "mne_eeg_reference",
                "mne_bad_interpolation",
            }.issubset(source_ids)
        )
        self.assertEqual(len(self.boundary["claim_boundary"]), 6)
        for text in (
            "planning research complete",
            "experiment `Not Started`",
            "six representation layers",
            "five modality profiles",
            "24-field",
            "12 operation classes",
            "16 future fixture families",
            "22 acceptance gates",
            "30 exact refusals",
            "29 false authorization fields",
            "Engineering capability added:",
            "Scientific claim not established:",
        ):
            self.assertIn(text, self.research)

    def test_machine_roadmap_and_public_status_are_synchronized(self):
        self.assertEqual(self.roadmap["schema_version"], "0.18.0")
        current = self.roadmap["current_boundary"]
        self.assertTrue(current["loop36_research_packet_prepared"])
        self.assertEqual(current["loop36_representation_layer_count"], 6)
        self.assertEqual(current["loop36_modality_profile_count"], 5)
        self.assertEqual(current["loop36_channel_record_field_count"], 24)
        self.assertEqual(current["loop36_operation_class_count"], 12)
        self.assertEqual(current["loop36_future_fixture_family_count"], 16)
        self.assertEqual(current["loop36_future_requirement_count"], 22)
        self.assertEqual(current["loop36_future_refusal_count"], 30)
        self.assertFalse(current["loop36_current_complete_geometry_reference_evidence_available"])
        self.assertEqual(
            current["loop36_maximum_future_real_metadata_claim"], "declared_metadata_compatibility"
        )
        self.assertFalse(current["loop36_preregistration_prepared"])
        self.assertFalse(current["loop36_execution_authorized"])
        loop36 = next(row for row in self.roadmap["loops"] if row["loop_id"] == 36)
        self.assertEqual(loop36["research_status"], "planning_research_complete")
        self.assertEqual(loop36["research_packet"], "docs/LOOP_36_PRIMARY_SOURCE_RESEARCH.md")
        self.assertEqual(loop36["research_registry"], "registries/loop36_research_boundary.v0.json")
        self.assertEqual(loop36["future_requirement_count"], 22)
        self.assertEqual(loop36["future_refusal_count"], 30)
        for path, content in self.public_status.items():
            with self.subTest(path=path.name):
                self.assertIn("Loop 36", content)
                self.assertIn("planning research", content.lower())
                self.assertIn("Not Started", content)
                self.assertIn("declared metadata compatibility", content)
                self.assertIn("unauthorized", content.lower())


if __name__ == "__main__":
    unittest.main()
