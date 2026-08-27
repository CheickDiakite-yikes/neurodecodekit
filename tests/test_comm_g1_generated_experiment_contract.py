from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/comm_g1_generated_experiment_contract.v0.json"
DOCUMENT_PATH = ROOT / "docs/COMM_G1_GENERATED_EXPERIMENT_PREREGISTRATION.md"
FRONTIER_PATH = ROOT / "registries/current_research_frontier.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CommG1GeneratedExperimentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))

    def test_schema_status_and_human_contract(self) -> None:
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.comm_g1_generated_experiment_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"],
            "COMM-G1-generated-experiment-contract-v0",
        )
        self.assertIn("all_real_authority_false", self.contract["status"])
        self.assertIn("## Target Firewall And Freeze", self.document)
        self.assertIn("## Claim Boundary", self.document)

    def test_parent_proofs_are_exact_green_and_hash_bound(self) -> None:
        parents = self.contract["parent_proofs"]
        self.assertEqual(
            parents["replication_source_refresh"]["commit"],
            "efa0268f5d852922dcd8a5d1f6665582824425df",
        )
        self.assertEqual(
            parents["replication_source_refresh"]["CI_run_id"],
            33_041_561_259,
        )
        for parent in ("communication_program", "replication_source_refresh"):
            self.assertTrue(parents[parent]["both_required_jobs_green"])
            for artifact in parents[parent]["artifacts"]:
                path = ROOT / artifact["path"]
                self.assertEqual(path.stat().st_size, artifact["bytes"])
                self.assertEqual(sha256_file(path), artifact["sha256"])
        self.assertTrue(parents["COMM_L0_generated_proof"]["both_required_jobs_green"])
        self.assertTrue(parents["COMM_L0_generated_proof"]["generated_qualification_consumed"])

    def test_real_source_readiness_is_all_false(self) -> None:
        readiness = self.contract["real_source_readiness"]
        self.assertEqual(readiness["source_id"], "OpenNeuro_ds003626_v2.1.2")
        self.assertTrue(
            all(
                not value
                for key, value in readiness.items()
                if key not in {"source_id", "source_role"}
            )
        )

    def test_generated_cohort_is_small_and_participant_held_out(self) -> None:
        cohort = self.contract["generated_cohort"]
        self.assertEqual(cohort["participants"], 6)
        self.assertEqual(cohort["total_rows"], 144)
        self.assertEqual(cohort["outer_folds"], 6)
        self.assertEqual(cohort["source_participants_per_fold"], 5)
        self.assertEqual(cohort["held_out_participants_per_fold"], 1)
        self.assertEqual(cohort["held_out_participant_calibration_rows"], 0)
        self.assertFalse(cohort["row_random_split_allowed"])
        self.assertFalse(cohort["real_words_reference_text_or_intended_text"])

    def test_generated_signal_roles_and_causal_features_are_exact(self) -> None:
        signals = self.contract["generated_signals"]
        features = self.contract["causal_features"]
        self.assertEqual(signals["sampling_rate_hz"], 128)
        self.assertEqual(signals["EEG_channels"]["total"], 8)
        self.assertEqual(signals["EOG_channels"], 4)
        self.assertEqual(signals["bilateral_oral_EMG_channels"], 2)
        self.assertTrue(features["producer_causal"])
        self.assertEqual(features["right_context_seconds"], 0.0)
        self.assertTrue(features["true_lengths_and_masks_preserved"])
        self.assertIn("future_samples", features["forbidden"])
        self.assertIn("held_out_person_normalization", features["forbidden"])

    def test_fixed_model_controls_and_derangement(self) -> None:
        self.assertEqual(
            self.contract["conditions"],
            [
                "equal_prior",
                "source_class_prior",
                "cue_plus_timing",
                "EOG_only",
                "oral_EMG_only",
                "peripheral_context_P",
                "selected_EEG_only",
                "posterior_EEG_only",
                "P_plus_residual_EEG",
                "P_plus_deranged_residual_EEG",
            ],
        )
        classifier = self.contract["classifier"]
        self.assertEqual(classifier["C"], 0.1)
        self.assertFalse(classifier["hyperparameter_selection"])
        residualizer = self.contract["residualizer"]
        self.assertFalse(residualizer["target_labels_used"])
        self.assertFalse(residualizer["held_out_rows_used_for_fit"])
        derangement = self.contract["derangement"]
        self.assertIn("participant_session_and_class", derangement["scope"])
        self.assertFalse(derangement["held_out_target_used"])

    def test_schedule_and_firewall_are_exact(self) -> None:
        schedule = self.contract["schedule"]
        self.assertEqual(schedule["total_parameter_update_fits"], 60)
        self.assertEqual(schedule["model_inference_runs"], 60)
        self.assertEqual(schedule["prediction_sets"], 60)
        self.assertEqual(schedule["prediction_rows"], 1_440)
        self.assertEqual(schedule["synthetic_target_deliveries"], 1)
        self.assertEqual(schedule["synthetic_scores"], 1)
        self.assertEqual(schedule["post_target_updates"], 0)
        self.assertEqual(schedule["reruns"], 0)
        firewall = self.contract["firewall"]
        for key in (
            "held_out_signal_fit_rows",
            "held_out_target_fit_rows",
            "held_out_calibration_rows",
            "held_out_threshold_selection_rows",
            "held_out_adaptation_rows",
        ):
            self.assertEqual(firewall[key], 0, key)
        self.assertFalse(firewall["fold_capability_can_traverse_other_fold"])
        self.assertFalse(
            firewall[
                "public_freeze_contains_individual_prediction_probability_target_or_participant_outcome"
            ]
        )

    def test_positive_and_negative_routes_have_no_scientific_value(self) -> None:
        families = self.contract["generated_case_families"]
        self.assertEqual(families["positive"], ["residual_EEG_increment"])
        self.assertEqual(len(families["shortcut_only"]), 7)
        self.assertGreaterEqual(len(families["adversarial"]), 20)
        self.assertGreaterEqual(families["minimum_independently_reachable_refusal_ids"], 30)
        router = self.contract["router"]
        self.assertEqual(router["positive_participants_required"], 6)
        self.assertEqual(router["scientific_value"], "none_generated_engineering_only")

    def test_resources_are_small_and_interfaces_have_no_real_mode(self) -> None:
        resources = self.contract["resource_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["wall_time_seconds"], 180)
        self.assertEqual(resources["peak_process_tree_RSS_bytes"], 512 << 20)
        self.assertEqual(resources["generated_input_bytes_maximum"], 32 << 20)
        self.assertEqual(resources["private_generated_bytes_maximum"], 32 << 20)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["real_or_private_dataset_bytes"], 0)
        interfaces = self.contract["interfaces"]
        self.assertEqual(interfaces["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(
            interfaces[
                "real_dataset_path_URL_request_download_execute_training_scoring_stream_device_or_provider_mode"
            ]
        )

    def test_ordered_stage_barriers_and_current_authority(self) -> None:
        stages = self.contract["ordered_stages"]
        self.assertTrue(stages["registration"]["current_stage"])
        self.assertFalse(stages["generated_implementation"]["authorized_now"])
        self.assertTrue(
            stages["generated_implementation"][
                "must_be_committed_pushed_and_remotely_green_before_qualification"
            ]
        )
        self.assertFalse(stages["generated_qualification"]["authorized_now"])
        self.assertFalse(
            stages["real_metadata_payload_semantic_model_or_score_stage"]["authorized_now"]
        )
        self.assertTrue(all(not value for value in self.contract["authorization_state"].values()))
        self.assertTrue(all(value == 0 for value in self.contract["operation_counters"].values()))

    def test_active_gate_and_claim_boundary_are_preserved(self) -> None:
        gate = self.contract["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertFalse(gate["changed_by_this_contract"])
        claims = self.contract["claim_boundary"]
        for key, value in claims.items():
            if key != "engineering_capability_proposed":
                self.assertFalse(value, key)
        self.assertIn("Scientific claim not established", self.document)

    def test_frontier_records_pending_registration_without_authority(self) -> None:
        registration = self.frontier["parallel_tier_A_communication_program"][
            "source_identity_preregistration"
        ]["generated_experiment_preregistration"]
        self.assertEqual(registration["gate_id"], "COMM-G1_GENERATED_QUALIFICATION")
        self.assertEqual(registration["generated_rows"], 144)
        self.assertEqual(registration["planned_parameter_update_fits"], 60)
        self.assertEqual(registration["planned_prediction_sets"], 60)
        self.assertFalse(registration["generated_implementation_authorized_now"])
        self.assertFalse(registration["generated_qualification_authorized_now"])
        self.assertEqual(registration["real_or_private_operations"], 0)
        self.assertFalse(registration["active_Tier_C_gate_changed"])


if __name__ == "__main__":
    unittest.main()
