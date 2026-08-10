import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "registries/physionet_motor_positive_control_contract.v0.json"
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREREGISTRATION.md"
RESEARCH_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PRIMARY_SOURCE_RESEARCH.md"
QUEUE_PATH = ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetMotorPositiveControlContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_registration_authorizes_no_real_or_model_operation(self):
        self.assertEqual(
            self.contract["status"],
            "preregistered_tier_c_not_authorized_not_implemented_not_executed",
        )
        scope = self.contract["scope"]
        self.assertTrue(scope["planning_and_preregistration_only_now"])
        self.assertTrue(scope["separate_exact_tier_c_decision_required"])
        self.assertTrue(
            all(
                value is False
                for key, value in scope.items()
                if key
                not in {
                    "planning_and_preregistration_only_now",
                    "separate_exact_tier_c_decision_required",
                }
            )
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )

    def test_source_bindings_match_exact_committed_or_new_artifacts(self):
        for source in self.contract["source_bindings"].values():
            path = ROOT / source["path"]
            self.assertTrue(path.is_file(), source["path"])
            self.assertEqual(source["sha256"], sha256(path), source["path"])

    def test_exact_acquired_inventory_is_reused_without_expansion(self):
        dataset = self.contract["dataset_binding"]
        self.assertEqual(dataset["subjects"], ["S001", "S002", "S003"])
        self.assertEqual(dataset["fit_and_selection_runs"], ["03", "07"])
        self.assertEqual(dataset["sealed_final_run"], "11")
        self.assertEqual(dataset["file_count"], 9)
        self.assertEqual(dataset["payload_bytes"], 23_248_224)
        self.assertEqual(dataset["event_sidecars"], 0)

        files = self.contract["selected_files"]
        self.assertEqual(len(files), 9)
        self.assertEqual(sum(row["size_bytes"] for row in files), 23_248_224)
        self.assertEqual(len({row["path"] for row in files}), 9)
        self.assertEqual(len({row["sha256"] for row in files}), 9)
        self.assertEqual(sum(row["role"] == "sealed_final" for row in files), 3)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in files))

    def test_event_split_and_target_firewall_are_strict(self):
        observed = self.contract["required_real_observations"]
        self.assertEqual(observed["sampling_rate_hz"], 160)
        self.assertEqual(observed["eeg_channel_count"], 64)
        self.assertEqual(observed["task_events_per_file"], 15)
        self.assertEqual(observed["task_events_total"], 135)
        self.assertEqual(observed["fit_and_selection_task_events"], 90)
        self.assertEqual(observed["sealed_final_task_events"], 45)

        derivative = self.contract["reader_and_derivative_contract"]
        self.assertEqual(derivative["fit_derivative_contains_runs"], ["03", "07"])
        self.assertEqual(derivative["prediction_derivative_contains_runs"], ["11"])
        self.assertFalse(derivative["prediction_derivative_contains_targets"])
        self.assertFalse(derivative["sealed_target_values_printed_logged_or_committed"])
        self.assertFalse(derivative["individual_predictions_probabilities_or_outcomes_committed"])

    def test_causal_view_models_and_selection_are_frozen(self):
        causal = self.contract["causal_preprocessing"]
        self.assertEqual(causal["passband_hz"], [8.0, 30.0])
        self.assertEqual(causal["primary_window_seconds_from_cue"], [1.0, 3.0])
        self.assertEqual(causal["right_context_seconds_relative_to_decision"], 0.0)
        self.assertEqual(causal["causal_claim"], "cue_causal_only_not_pre_movement")

        families = self.contract["candidate_families"]
        self.assertEqual(
            [row["family_id"] for row in families],
            ["fixed_8_to_30_hz_csp_lda", "regularized_riemannian_mdm"],
        )
        self.assertEqual(families[0]["CSP_components"], 4)
        self.assertEqual(families[1]["metric"], "riemann")
        selection = self.contract["split_and_selection"]
        self.assertFalse(selection["row_random_split"])
        self.assertFalse(selection["run_11_used_for_family_threshold_channel_or_parameter_selection"])
        self.assertEqual(selection["exact_tie_winner"], "fixed_8_to_30_hz_csp_lda")
        self.assertFalse(selection["post_target_selection_or_update"])

    def test_prediction_physiology_and_confound_axes_are_conjunctive(self):
        self.assertEqual(len(self.contract["mandatory_final_prediction_sets"]), 12)
        self.assertEqual(self.contract["primary_gate"]["minimum_correct_count"], 30)
        self.assertEqual(
            self.contract["primary_gate"]["minimum_pooled_balanced_accuracy"], 0.65
        )
        self.assertTrue(
            self.contract["physiology_gate"]["independent_of_model_selection"]
        )
        self.assertEqual(
            self.contract["confound_gate"][
                "central_minus_frontal_occipital_minimum_balanced_accuracy_margin"
            ],
            0.05,
        )
        self.assertFalse(
            self.contract["confound_gate"][
                "proxy_failure_proves_no_ocular_or_muscle_confound"
            ]
        )

        router = self.contract["ordered_verdict_router"]
        self.assertEqual([row["verdict"] for row in router], ["WO9-V0", "WO9-V1", "WO9-V2", "WO9-V3"])
        self.assertIn("three_person", router[-1]["maximum_claim"])

    def test_remote_green_prediction_freeze_precedes_one_final_score(self):
        freeze = self.contract["prediction_freeze"]
        self.assertTrue(freeze["public_hash_only_ledger_required"])
        self.assertTrue(freeze["ledger_commit_must_be_pushed"])
        self.assertTrue(freeze["base_python_and_optional_neuro_jobs_must_be_green"])
        self.assertFalse(freeze["run_11_target_open_before_remote_green_freeze"])
        self.assertEqual(freeze["final_target_deliveries"], 1)
        self.assertEqual(freeze["final_scoring_events"], 1)

    def test_resource_caps_and_forbidden_operations_are_bounded(self):
        caps = self.contract["resource_caps"]
        self.assertEqual(caps["registered_executions"], 1)
        self.assertEqual(caps["cpu_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["concurrent_numerical_jobs"], 1)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["new_payload_bytes"], 0)
        self.assertEqual(caps["maximum_classical_parameter_update_fits"], 40)
        self.assertEqual(caps["maximum_prediction_sets"], 64)
        self.assertEqual(caps["retries"], 0)
        self.assertEqual(caps["reruns"], 0)
        self.assertGreaterEqual(len(self.contract["forbidden_operations"]), 14)

    def test_docs_state_the_claim_ceiling_and_tracker_keeps_work_order_gated(self):
        prereg = DOC_PATH.read_text(encoding="utf-8")
        research = RESEARCH_PATH.read_text(encoding="utf-8")
        queue = QUEUE_PATH.read_text(encoding="utf-8")
        self.assertIn("Accuracy by itself cannot pass", prereg)
        self.assertIn("Scientific claim not established", prereg)
        self.assertIn("Why Accuracy Alone Is Not Enough", research)
        row = next(line for line in queue.splitlines() if line.startswith("| 9 |"))
        self.assertIn("Gated", row)


if __name__ == "__main__":
    unittest.main()
