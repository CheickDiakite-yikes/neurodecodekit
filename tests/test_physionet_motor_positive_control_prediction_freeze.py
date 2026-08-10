import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.experiments import physionet_motor_positive_control as wo9


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = (
    ROOT / "registries/physionet_motor_positive_control_prediction_freeze.v0.json"
)
DOC_PATH = ROOT / "docs/PHYSIONET_MOTOR_POSITIVE_CONTROL_PREDICTION_FREEZE.md"
EXPECTED_FILE_SHA256 = "3c100daa8a6a2816ce4270c9e32cbdcc4cd30d70d1c255e37596c2ca6f665de4"


class PhysioNetMotorPositiveControlPredictionFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = json.loads(FREEZE_PATH.read_text(encoding="utf-8"))

    def test_file_and_canonical_hashes_are_exact(self):
        self.assertEqual(hashlib.sha256(FREEZE_PATH.read_bytes()).hexdigest(), EXPECTED_FILE_SHA256)
        wo9.validate_public_freeze_ledger(self.freeze)
        self.assertEqual(
            self.freeze["freeze_record_sha256"],
            "2b817b5273b6361d0636b7534f2744419b45a521e96fb94fdbe1ef4731f6292b",
        )

    def test_green_implementation_parent_is_exact(self):
        self.assertEqual(
            self.freeze["implementation_commit"],
            "52b9b15a64972a285efbe630f49600727e836983",
        )
        self.assertEqual(self.freeze["implementation_ci_run_id"], 31351728650)
        self.assertEqual(self.freeze["implementation_base_python_job_id"], 93343718364)
        self.assertEqual(self.freeze["implementation_optional_neuro_job_id"], 93343718355)

    def test_source_access_and_event_inventory_are_exact(self):
        self.assertEqual(self.freeze["source_kind"], "real_physionet")
        self.assertEqual(self.freeze["source_file_count"], 9)
        self.assertEqual(self.freeze["source_payload_bytes"], 23_248_224)
        counters = self.freeze["operation_counters"]
        for name in (
            "edf_sha256_passes",
            "edf_semantic_parses",
            "edf_header_reads",
            "edf_annotation_reads",
            "edf_signal_reads",
        ):
            self.assertEqual(counters[name], 9, name)
        self.assertEqual(counters["fit_target_rows_delivered"], 90)
        self.assertEqual(counters["run11_signal_rows_delivered"], 45)
        self.assertEqual(counters["event_sidecar_operations"], 0)

    def test_all_twelve_condition_hashes_are_present_without_outputs(self):
        self.assertEqual(tuple(self.freeze["prediction_set_ids"]), wo9.CONDITION_IDS)
        self.assertEqual(self.freeze["prediction_set_count"], 12)
        self.assertEqual(set(self.freeze["prediction_set_sha256"]), set(wo9.CONDITION_IDS))
        self.assertTrue(
            all(len(value) == 64 for value in self.freeze["prediction_set_sha256"].values())
        )
        forbidden = {
            "event_ids",
            "participant_ids",
            "predictions",
            "probabilities",
            "targets",
            "labels",
            "participant_outcomes",
        }

        def walk(value):
            if isinstance(value, dict):
                self.assertFalse(forbidden.intersection(value))
                for nested in value.values():
                    walk(nested)
            elif isinstance(value, list):
                for nested in value:
                    walk(nested)

        walk(self.freeze)

    def test_model_inventory_and_target_firewall_are_exact(self):
        counters = self.freeze["operation_counters"]
        self.assertEqual(counters["classical_parameter_update_fits"], 33)
        self.assertEqual(counters["target_blind_model_inference_runs"], 45)
        self.assertEqual(counters["train_only_no_signal_prior_fits"], 3)
        self.assertEqual(counters["prediction_sets_frozen"], 12)
        self.assertEqual(counters["final_scoring_events"], 0)
        self.assertEqual(counters["sealed_final_target_rows_delivered_to_model_stage"], 0)
        firewall = self.freeze["target_firewall"]
        self.assertEqual(firewall["run11_target_rows_available_to_model_stage"], 0)
        self.assertFalse(firewall["prediction_derivative_contains_targets"])
        self.assertFalse(firewall["individual_outputs_committed"])

    def test_resources_are_bounded_and_execution_is_one_shot(self):
        resources = self.freeze["resources_through_freeze"]
        self.assertLessEqual(resources["runtime_seconds"], 1800)
        self.assertLessEqual(resources["peak_rss_bytes"], 805_306_368)
        self.assertLessEqual(
            resources["generated_private_bytes_before_target_blind_report"],
            67_108_864,
        )
        self.assertEqual(resources["cpu_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["concurrent_numerical_jobs"], 1)
        self.assertEqual(resources["network_bytes"], 0)
        self.assertEqual(resources["new_payload_bytes"], 0)
        self.assertEqual(self.freeze["operation_counters"]["registered_executions"], 1)
        self.assertEqual(self.freeze["operation_counters"]["retries"], 0)
        self.assertEqual(self.freeze["operation_counters"]["reruns"], 0)

    def test_current_claim_is_target_blind_only(self):
        claim = self.freeze["claim_boundary"]
        self.assertEqual(
            claim["current"],
            "target_blind_prediction_hashes_only_no_scientific_result",
        )
        self.assertIn("Brain-specific origin", claim["not_established"])
        self.assertIn("end_to_end_latency_not_measured", self.freeze["warnings"])

    def test_document_and_tracker_keep_scoring_closed(self):
        document = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", document)
        self.assertIn("Scientific claim not established", document)
        self.assertIn("final targets remain sealed", document)
        tracker = (
            ROOT / "docs/NEXT_20_SYSTEMATIC_EXECUTION_2026-08-08.md"
        ).read_text(encoding="utf-8")
        row = next(line for line in tracker.splitlines() if line.startswith("| 9 |"))
        self.assertIn("Freeze Pending Remote Green", row)
        self.assertNotIn("Complete", row)


if __name__ == "__main__":
    unittest.main()
