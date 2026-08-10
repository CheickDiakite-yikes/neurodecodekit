import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_PATH = ROOT / "registries" / "iackd_role_aware_dual_reversal_research.v0.json"
INVENTORY_PATH = ROOT / "registries" / "iackd_openneuro_metadata_inventory.v0.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDRoleAwareDualReversalResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.research = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"))
        cls.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    def test_schema_status_and_claim_posture_are_prospective(self) -> None:
        self.assertEqual(
            self.research["schema_name"],
            "neurodecodekit.iackd_role_aware_dual_reversal_research",
        )
        self.assertTrue(self.research["status"].startswith("tier_a_research_complete"))
        self.assertIn("target_free_code_audit_only", self.research["proof_posture"])
        self.assertIn("316 tiny public BIDS", self.research["decision"])

    def test_human_document_and_all_bound_inputs_are_current(self) -> None:
        bindings = self.research["bindings"]
        for binding_name, path_key, hash_key in (
            ("human_document", "path", "sha256"),
            ("committed_openneuro_inventory", "path", "sha256"),
            ("consumed_implementation_source", "path", "sha256"),
        ):
            binding = bindings[binding_name]
            self.assertEqual(_sha256(ROOT / binding[path_key]), binding[hash_key])
        for binding_name in ("iackd_H1_result", "consumed_iackd_1_result"):
            binding = bindings[binding_name]
            self.assertEqual(
                _sha256(ROOT / binding["document_path"]), binding["document_sha256"]
            )
            self.assertEqual(
                _sha256(ROOT / binding["registry_path"]), binding["registry_sha256"]
            )
        artifacts = self.research["public_artifact_bindings"]
        self.assertEqual(
            _sha256(ROOT / artifacts["invariant_test_path"]),
            artifacts["invariant_test_sha256"],
        )

    def test_H1_closeout_was_remote_green_and_remains_consumed(self) -> None:
        result = self.research["bindings"]["iackd_H1_result"]
        self.assertEqual(result["closeout_commit"], "a6704898cfb09f6321bac5f15e27424f02614317")
        self.assertEqual(result["push_CI_run_id"], 31425445891)
        self.assertEqual(result["base_python_job_id"], 93575925675)
        self.assertEqual(result["optional_neuro_readers_job_id"], 93575925695)
        self.assertTrue(result["both_required_jobs_green"])
        self.assertTrue(result["consumed"])
        self.assertFalse(result["retry_or_rerun_open"])
        self.assertFalse(
            self.research["bindings"]["consumed_iackd_1_result"][
                "local_bundle_reopen_allowed"
            ]
        )

    def test_measured_header_evidence_is_exact_and_not_mislabeled_EEG(self) -> None:
        evidence = self.research["measured_H1_evidence"]
        self.assertEqual(evidence["route"], "IACKDH-R5")
        self.assertEqual(evidence["input_headers"], 128)
        self.assertEqual(evidence["input_bytes"], 161792)
        self.assertEqual(evidence["unique_signature_count"], 2)
        groups = evidence["signature_groups"]
        self.assertEqual(
            [(row["occurrence_count"], row["declared_channel_count"]) for row in groups],
            [(96, 29), (32, 31)],
        )
        self.assertFalse(groups[0]["M1_present"])
        self.assertFalse(groups[0]["M2_present"])
        self.assertTrue(groups[1]["M1_present"])
        self.assertTrue(groups[1]["M2_present"])
        for row in groups:
            self.assertTrue(row["HEOG_present"])
            self.assertTrue(row["VEOG_present"])
            self.assertTrue(row["TRIGGER_present"])
            self.assertEqual(row["sampling_rate_hz"], 1024)
        self.assertFalse(evidence["actual_EEG_channel_count_known"])
        self.assertFalse(evidence["scientific_result"])

    def test_code_audit_requires_a_new_role_first_module(self) -> None:
        audit = self.research["target_free_code_audit"]
        self.assertEqual(
            {row["id"] for row in audit["findings"]},
            {
                "A1-exact-total-before-BIDS",
                "A2-invalid-EEG-count-contract",
                "A3-trigger-role-fallthrough",
                "A4-fixture-source-mismatch",
            },
        )
        self.assertEqual(audit["safe_repair"], "new_role_first_module_after_public_H2_result")
        self.assertFalse(audit["patch_consumed_IACKD1_in_place"])
        self.assertFalse(audit["replace_36_only"])

    def test_H2_surface_replays_from_committed_inventory(self) -> None:
        roles = {"channels", "eeg_sidecar", "electrodes", "coordsystem"}
        rows = [row for row in self.inventory["selected_objects"] if row["role"] in roles]
        surface = self.research["H2_public_surface"]
        self.assertEqual(len(rows), surface["objects"])
        self.assertEqual(sum(row["size_bytes"] for row in rows), surface["expected_body_bytes"])

        identity_rows = sorted(
            (
                {
                    key: row[key]
                    for key in ("path", "size_bytes", "etag", "last_modified")
                }
                for row in rows
            ),
            key=lambda row: row["path"],
        )
        encoded = json.dumps(
            identity_rows,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("utf-8")
        self.assertEqual(len(encoded), surface["canonical_identity_bytes"])
        self.assertEqual(
            hashlib.sha256(encoded).hexdigest(), surface["canonical_identity_sha256"]
        )

        for role in sorted(roles):
            selected = [row for row in rows if row["role"] == role]
            registered = surface["roles"][role]
            self.assertEqual(len(selected), registered["objects"])
            self.assertEqual(sum(row["size_bytes"] for row in selected), registered["bytes"])
            self.assertEqual(min(row["size_bytes"] for row in selected), registered["minimum_object_bytes"])
            self.assertEqual(max(row["size_bytes"] for row in selected), registered["maximum_object_bytes"])

        channel_sizes = Counter(
            row["size_bytes"] for row in rows if row["role"] == "channels"
        )
        self.assertEqual(channel_sizes, Counter({1752: 96, 1866: 32}))
        self.assertFalse(surface["existing_local_bundle_needed"])
        self.assertFalse(surface["VHDR_reread_needed"])

    def test_H2_parser_output_and_router_are_role_first(self) -> None:
        contract = self.research["H2_recommended_contract"]
        self.assertEqual(contract["parser_dependencies"], "python_standard_library_only")
        self.assertEqual(contract["required_channel_fields"], ["name", "type", "units"])
        self.assertTrue(contract["source_order_required"])
        self.assertFalse(contract["duplicate_normalized_names_allowed"])
        self.assertTrue(contract["explicit_BIDS_types_required"])
        self.assertFalse(contract["MNE_inferred_types_authoritative"])
        self.assertIn("electrode_coordinates", contract["forbidden_public_fields"])
        self.assertEqual(
            [row["route"] for row in contract["diagnostic_router"]],
            ["IACKDR-R0", "IACKDR-R1", "IACKDR-R2", "IACKDR-R3", "IACKDR-R4"],
        )
        self.assertFalse(contract["automatically_authorizes_IACKD2"])

    def test_sensor_role_map_never_uses_a_guessed_count(self) -> None:
        contract = self.research["role_first_sensor_contract"]
        self.assertIn("role_map_hash", contract["fields"])
        self.assertEqual(
            contract["predictive_EEG_selection"],
            "frozen_BIDS_role_map_not_count_subtraction",
        )
        self.assertFalse(contract["TRIGGER_predictive"])
        self.assertFalse(contract["channels_electrodes_equal_size_required"])
        self.assertFalse(contract["target_outcome_or_model_score_may_select_role_policy"])
        self.assertTrue(contract["every_derivative_prediction_and_receipt_binds_role_map_hash"])

    def test_dual_reversal_arms_make_cue_surrogate_opposite_action(self) -> None:
        design = self.research["IACKD2_dual_reversal"]
        self.assertEqual([row["arm_id"] for row in design["arms"]], ["C2I", "I2C"])
        for arm in design["arms"]:
            self.assertEqual(
                arm["fit_action_to_visual_sign"], -arm["final_action_to_visual_sign"]
            )
            self.assertTrue(arm["cue_surrogate_equals_negative_action_on_final"])
        self.assertEqual(
            design["final_target_views"],
            [
                "actual_hand_direction",
                "visual_direction_transformed_by_frozen_fit_relation",
            ],
        )
        self.assertTrue(design["same_prediction_scored_against_both_views"])
        self.assertTrue(design["both_arms_required"])
        self.assertFalse(design["one_arm_may_rescue_other"])
        firewall = design["target_firewall"]
        self.assertFalse(firewall["final_action_direction_to_predictive_code_before_freeze"])
        self.assertFalse(firewall["final_visual_direction_to_predictive_code_before_freeze"])
        self.assertTrue(firewall["all_predictions_freeze_before_one_combined_target_delivery"])

    def test_views_and_conjunction_localize_action_versus_cue(self) -> None:
        views = set(self.research["prospective_views"])
        self.assertTrue(
            {
                "role_mapped_whole_scalp_low_frequency_EEG",
                "central_C3_C4_Cz_EEG",
                "occipital_O1_Oz_O2_visual_proxy_if_H2_confirms_all_three",
                "HEOG_VEOG_only",
                "fit_only_EOG_orthogonalized_scalp_EEG",
                "train_only_no_signal_prior",
            }.issubset(views)
        )
        gates = set(self.research["prospective_evidence_conjunction"])
        self.assertIn("both_arms_above_chance_for_action_direction", gates)
        self.assertIn("both_arms_prefer_action_over_exact_opposite_cue_surrogate", gates)
        self.assertIn("neither_arm_rescues_failure_of_the_other", gates)
        self.assertIn("exact_fit_and_prediction_counts", self.research["deferred_until_H2"])

    def test_H2_caps_are_small_sequential_and_no_rerun(self) -> None:
        caps = self.research["proposed_H2_resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["concurrent_numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["requests"], 316)
        self.assertEqual(caps["expected_body_bytes"], 457602)
        self.assertLessEqual(caps["network_body_bytes"], 2 * 1024 * 1024)
        self.assertLessEqual(caps["incremental_disk_bytes"], 4 * 1024 * 1024)
        self.assertEqual((caps["retries"], caps["reruns"]), (0, 0))

    def test_every_current_access_counter_is_zero_and_real_stages_are_closed(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.research["current_access_counters"].values())
        )
        state = self.research["authorization_state"]
        self.assertTrue(state["Tier_A_research_complete"])
        self.assertTrue(all(not value for key, value in state.items() if key != "Tier_A_research_complete"))

    def test_document_states_engineering_and_scientific_boundaries(self) -> None:
        document = (ROOT / self.research["bindings"]["human_document"]["path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("Engineering capability proposed:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no new public metadata body", document)
        self.assertIn("The retained IACKD bundle remains closed", " ".join(self.research["warnings"]))
        self.assertIn("no new neural effect", self.research["claim_boundary"]["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
