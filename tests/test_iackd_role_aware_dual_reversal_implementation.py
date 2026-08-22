import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/iackd_role_aware_dual_reversal_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_IMPLEMENTATION.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_role_aware_dual_reversal_implementation.py": (
        "0721e83517069bed52127df2ae75234e1167233bf7c14f5d27091b22e748649b"
    ),
    ".github/workflows/ci.yml": (
        "b2dfcf8214b3b5d975e7a432e7c8ff0b6da9b0f1108fcef681cc22310ba50bba"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKD2ImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_status_requires_exact_implementation_green_before_closeout(self):
        self.assertEqual(
            self.registry["status"],
            "generated_fixture_qualified_exact_implementation_requires_remote_green_before_registered_synthetic_closeout",
        )
        state = self.registry["execution_state"]
        self.assertFalse(state["registered_synthetic_closeout_consumed"])
        self.assertFalse(state["real_execution_authorized"])
        self.assertFalse(state["real_execution_consumed"])
        self.assertFalse(state["rerun_authorized"])

    def test_green_registration_binding_is_exact(self):
        self.assertEqual(
            self.registry["green_registration"],
            {
                "commit": "5bdab3055a8a1c5200b5ec6c0037e401d8c817ce",
                "push_ci_run_id": 31448911258,
                "base_python_job_id": 93648969685,
                "optional_neuro_job_id": 93648969711,
                "both_required_jobs_green": True,
            },
        )
        self.assertEqual(
            self.registry["contract_sha256"],
            sha256(ROOT / self.registry["contract_path"]),
        )

    def test_all_owned_implementation_hashes_are_current(self):
        paths = set()
        for row in self.registry["tracked_file_hashes"]:
            self.assertNotIn(row["path"], paths)
            paths.add(row["path"])
            if row["path"] in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(row["sha256"], HISTORICAL_MUTABLE_BINDINGS[row["path"]])
            else:
                self.assertEqual(row["sha256"], sha256(ROOT / row["path"]), row["path"])
        for required in (
            "src/neurodecodekit/experiments/iackd_role_aware_dual_reversal.py",
            "tests/test_iackd_role_aware_dual_reversal.py",
            "tests/test_iackd_role_aware_dual_reversal_implementation.py",
            "docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_IMPLEMENTATION.md",
        ):
            self.assertIn(required, paths)

    def test_model_scorer_boundary_and_inventory_are_exact(self):
        interface = self.registry["registered_interface"]
        self.assertEqual(interface["arms"], 2)
        self.assertEqual(interface["participant_hand_units"], 30)
        self.assertEqual(interface["generated_source_rows"], 4096)
        self.assertEqual(interface["fit_rows"], 3136)
        self.assertEqual(interface["final_target_free_rows"], 960)
        self.assertEqual(interface["primary_parameter_update_fits"], 660)
        self.assertEqual(interface["primary_prediction_sets"], 900)
        self.assertEqual(interface["replay_parameter_update_fits"], 660)
        self.assertEqual(interface["replay_prediction_sets"], 900)
        firewall = self.registry["target_firewall"]
        self.assertEqual(firewall["final_target_rows_visible_to_model_stage"], 0)
        self.assertTrue(firewall["model_and_scorer_stage_objects_are_separate"])
        self.assertTrue(firewall["freeze_recomputed_before_generated_target_access"])
        self.assertFalse(firewall["individual_predictions_published"])

    def test_reader_preprocessing_and_router_are_frozen(self):
        reader = self.registry["generated_reader_and_preprocessing"]
        self.assertEqual(reader["source_row_counts"], [29, 31])
        self.assertEqual(reader["predictive_EEG_channels"], 26)
        self.assertEqual(reader["sampling_rate_hz"], 1024)
        self.assertEqual(reader["dimensions"], [130, 15, 15, 10, 78, 78, 130, 4])
        self.assertTrue(reader["producer_is_causal_in_samples"])
        self.assertEqual(reader["right_context_seconds"], 0.0)
        self.assertFalse(reader["end_to_end_latency_measured"])
        self.assertEqual(
            self.registry["aggregate_scorer"]["ordered_routes"],
            [
                "IACKD2-R1",
                "IACKD2-R2",
                "IACKD2-R3",
                "IACKD2-R4",
                "IACKD2-R5",
                "IACKD2-R0",
            ],
        )

    def test_disposable_development_qualification_is_non_scientific(self):
        qualification = self.registry["development_qualification"]
        self.assertTrue(qualification["all_gates_passed"])
        self.assertEqual(qualification["synthetic_route"], "IACKD2-R5")
        self.assertEqual(qualification["primary_parameter_update_fits"], 660)
        self.assertEqual(qualification["primary_prediction_sets"], 900)
        self.assertEqual(qualification["output_bytes"], 30169)
        self.assertEqual(qualification["real_or_public_payload_reads"], 0)
        self.assertEqual(qualification["network_bytes"], 0)
        self.assertTrue(qualification["generated_output_removed"])
        self.assertFalse(qualification["synthetic_route_has_scientific_value"])

    def test_every_real_or_forbidden_counter_is_zero(self):
        for name, value in self.registry["implementation_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_document_preserves_two_sentence_claim_boundary(self):
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("No real or public IACKD payload", document)
        self.assertIn("Synthetic `IACKD2-R5` has zero scientific value", document)


if __name__ == "__main__":
    unittest.main()
