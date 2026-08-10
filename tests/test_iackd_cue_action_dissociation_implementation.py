import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/iackd_cue_action_dissociation_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/IACKD_CUE_ACTION_DISSOCIATION_IMPLEMENTATION.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDCueActionDissociationImplementationTests(unittest.TestCase):
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
                "commit": "1f48b3011e19ba8da35a18c3d3395813f159adc2",
                "push_ci_run_id": 31403012709,
                "base_python_job_id": 93502398308,
                "optional_neuro_job_id": 93502398753,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            self.registry["authorization_decision_sha256"],
            sha256(
                ROOT
                / "registries/iackd_cue_action_dissociation_"
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
            "src/neurodecodekit/datasets/iackd_cue_action_acquisition.py",
            "src/neurodecodekit/experiments/iackd_cue_action_dissociation.py",
            "src/neurodecodekit/cli.py",
            "tests/test_iackd_cue_action_acquisition.py",
            "tests/test_iackd_cue_action_dissociation.py",
            "tests/test_iackd_cue_action_dissociation_implementation.py",
            "docs/IACKD_CUE_ACTION_DISSOCIATION_IMPLEMENTATION.md",
            ".github/workflows/ci.yml",
        ):
            self.assertIn(required, paths)

    def test_fixture_qualification_is_measured_and_non_scientific(self):
        qualification = self.registry["fixture_qualification"]
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["synthetic_runs"], 128)
        self.assertEqual(qualification["synthetic_trials"], 2048)
        self.assertEqual(qualification["fit_rows"], 1568)
        self.assertEqual(qualification["final_rows"], 480)
        self.assertEqual(qualification["parameter_update_fits"], 300)
        self.assertEqual(qualification["target_blind_model_inference_calls"], 420)
        self.assertEqual(qualification["prediction_sets"], 420)
        self.assertEqual(qualification["generated_bytes"], 5_683_285)
        self.assertEqual(qualification["real_data_reads"], 0)
        self.assertEqual(qualification["real_target_reads"], 0)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertFalse(qualification["scientific_claim_upgrade"])

    def test_firewall_freeze_counts_and_resources_are_frozen(self):
        interface = self.registry["registered_interface"]
        self.assertEqual(interface["objects"], 1340)
        self.assertEqual(interface["input_payload_bytes"], 7_249_113_684)
        self.assertEqual(interface["participant_hand_units"], 30)
        self.assertEqual(interface["parameter_update_fits"], 300)
        self.assertEqual(interface["condition_families"], 14)
        self.assertEqual(interface["target_blind_inference_calls"], 420)
        self.assertEqual(interface["prediction_sets"], 420)
        self.assertEqual(interface["final_target_deliveries"], 1)
        self.assertEqual(interface["scoring_events"], 1)
        self.assertEqual(interface["retries"], 0)
        self.assertEqual(interface["reruns"], 0)
        firewall = self.registry["target_firewall"]
        self.assertEqual(firewall["final_target_rows_available_to_model_stage"], 0)
        self.assertFalse(firewall["sealed_target_file_opened_by_model_stage"])
        self.assertTrue(firewall["both_target_views_frozen_together"])
        self.assertTrue(self.registry["access_order"]["analysis_consumed_before_bundle_access"])
        self.assertTrue(self.registry["access_order"]["score_consumed_before_target_access"])

    def test_optional_environment_is_exact_and_base_unchanged(self):
        environment = self.registry["optional_environment"]
        self.assertEqual(
            environment["qualified_versions"],
            {
                "numpy": "2.5.2",
                "scipy": "1.18.0",
                "mne": "1.12.1",
                "scikit_learn": "1.9.0",
            },
        )
        self.assertFalse(environment["base_dependency_changes"])
        self.assertEqual(environment["dependency_installs"], 0)

    def test_every_real_or_forbidden_implementation_counter_is_zero(self):
        for name, value in self.registry["implementation_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_document_preserves_engineering_and_claim_boundaries(self):
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("no real IACKD payload or target was opened", document)
        self.assertIn("pushed, and remotely green before the registered acquisition", document)


if __name__ == "__main__":
    unittest.main()
