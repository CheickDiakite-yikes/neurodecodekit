import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/physionet_low_frequency_cohort_confirmation_implementation.v0.json"
)
DOCUMENT_PATH = (
    ROOT / "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_IMPLEMENTATION.md"
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhysioNetLowFrequencyImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_requires_remote_green_before_real_access(self):
        self.assertEqual(
            self.registry["status"],
            "fixture_qualified_exact_implementation_requires_remote_green_before_real_access",
        )
        state = self.registry["execution_state"]
        self.assertFalse(state["acquisition_consumed"])
        self.assertFalse(state["real_analysis_consumed"])
        self.assertFalse(state["prediction_freeze_created"])
        self.assertFalse(state["final_targets_delivered"])
        self.assertFalse(state["scoring_consumed"])

    def test_green_packet_bound_decision_is_exact(self):
        self.assertEqual(
            self.registry["green_authorization_decision"],
            {
                "commit": "1efeac7f0b7b316bb94effb1a2eeeb1bbf99f50a",
                "push_ci_run_id": 31355944651,
                "base_python_job_id": 93355535398,
                "optional_neuro_job_id": 93355535361,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            self.registry["authorization_decision_sha256"],
            sha256(
                ROOT
                / "registries/physionet_low_frequency_cohort_confirmation_"
                "authorization_decision.v0.json"
            ),
        )

    def test_all_owned_implementation_hashes_are_current(self):
        paths = set()
        for row in self.registry["tracked_file_hashes"]:
            self.assertNotIn(row["path"], paths)
            paths.add(row["path"])
            self.assertEqual(row["sha256"], sha256(ROOT / row["path"]), row["path"])
        for required in (
            "src/neurodecodekit/datasets/physionet_low_frequency_acquisition.py",
            "src/neurodecodekit/experiments/physionet_low_frequency_cohort_confirmation.py",
            "src/neurodecodekit/cli.py",
            "tests/test_physionet_low_frequency_acquisition.py",
            "tests/test_physionet_low_frequency_cohort_confirmation.py",
            "tests/test_physionet_low_frequency_cohort_confirmation_implementation.py",
            "docs/PHYSIONET_LOW_FREQUENCY_COHORT_CONFIRMATION_IMPLEMENTATION.md",
        ):
            self.assertIn(required, paths)

    def test_fixture_qualification_is_exact_measured_and_non_scientific(self):
        qualification = self.registry["fixture_qualification"]
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["synthetic_runs"], 72)
        self.assertEqual(qualification["synthetic_events"], 1080)
        self.assertEqual(qualification["fit_rows"], 720)
        self.assertEqual(qualification["final_rows"], 360)
        self.assertEqual(qualification["parameter_update_fits"], 144)
        self.assertEqual(qualification["target_blind_model_inference_runs"], 216)
        self.assertEqual(qualification["participant_condition_prediction_sets"], 216)
        self.assertEqual(qualification["generated_bytes"], 4_215_687)
        self.assertEqual(qualification["real_data_reads"], 0)
        self.assertEqual(qualification["real_target_reads"], 0)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertFalse(qualification["scientific_claim_upgrade"])

    def test_one_shot_firewall_counts_and_resources_are_frozen(self):
        interface = self.registry["registered_interface"]
        self.assertEqual(interface["files"], 72)
        self.assertEqual(interface["input_payload_bytes"], 184_252_032)
        self.assertEqual(interface["fit_rows"], 720)
        self.assertEqual(interface["sealed_final_rows"], 360)
        self.assertEqual(interface["parameter_update_fits"], 144)
        self.assertEqual(interface["condition_families"], 18)
        self.assertEqual(interface["target_blind_inference_runs"], 216)
        self.assertEqual(interface["participant_condition_prediction_sets"], 216)
        self.assertEqual(interface["final_target_deliveries"], 1)
        self.assertEqual(interface["scoring_events"], 1)
        self.assertEqual(interface["retries"], 0)
        self.assertEqual(interface["reruns"], 0)
        self.assertTrue(self.registry["access_order"]["analysis_consumed_before_bundle_access"])
        self.assertTrue(self.registry["access_order"]["score_consumed_before_target_access"])

    def test_every_real_or_forbidden_implementation_counter_is_zero(self):
        for name, value in self.registry["implementation_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_document_preserves_engineering_and_claim_boundaries(self):
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real S004-S015 EDF or target was opened", document)
        self.assertIn("must be committed,\npushed, and remotely green", document)


if __name__ == "__main__":
    unittest.main()
