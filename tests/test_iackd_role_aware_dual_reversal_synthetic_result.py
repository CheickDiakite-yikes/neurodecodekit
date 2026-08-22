import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/iackd_role_aware_dual_reversal_synthetic_result.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_SYNTHETIC_RESULT.md"
HISTORICAL_MUTABLE_BINDINGS = {
    "tests/test_iackd_role_aware_dual_reversal_implementation.py": (
        "0721e83517069bed52127df2ae75234e1167233bf7c14f5d27091b22e748649b"
    ),
    "tests/test_iackd_role_aware_dual_reversal_synthetic_result.py": (
        "9145e431652f7aae86e1e9a9f501631ffc45dfece78658abe4a3d3cb2a96ba30"
    ),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKD2SyntheticResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_result_is_consumed_generated_only_and_not_rerunnable(self):
        self.assertEqual(
            self.result["status"],
            "registered_generated_closeout_consumed_passed_interface_only_no_scientific_result",
        )
        state = self.result["execution_state"]
        self.assertTrue(state["registered_generated_closeout_consumed"])
        self.assertFalse(state["registered_generated_closeout_rerun_available"])
        self.assertFalse(state["real_execution_authorized"])
        self.assertFalse(state["real_execution_consumed"])
        self.assertFalse(state["scientific_claim_upgraded"])

    def test_failed_and_corrected_implementation_CI_are_both_preserved(self):
        first = self.result["first_implementation_CI"]
        self.assertEqual(first["commit"], "25a569216db805db068265744b12e84df9fd7b64")
        self.assertEqual(first["push_ci_run_id"], 31451058136)
        self.assertEqual(first["conclusion"], "failure")
        self.assertFalse(first["registered_closeout_executed_after_failure"])
        green = self.result["green_exact_implementation"]
        self.assertEqual(
            green,
            {
                "commit": "af7488ab1e8f49854733425a96bbdc9c222ef02b",
                "push_ci_run_id": 31451262840,
                "base_python_job_id": 93655939217,
                "optional_neuro_job_id": 93655939167,
                "both_required_jobs_green": True,
            },
        )

    def test_bound_implementation_and_result_files_are_current(self):
        paths = set()
        for row in self.result["tracked_file_hashes"]:
            self.assertNotIn(row["path"], paths)
            paths.add(row["path"])
            if row["path"] in HISTORICAL_MUTABLE_BINDINGS:
                self.assertEqual(row["sha256"], HISTORICAL_MUTABLE_BINDINGS[row["path"]])
            else:
                self.assertEqual(row["sha256"], sha256(ROOT / row["path"]), row["path"])
        for required in (
            "registries/iackd_role_aware_dual_reversal_implementation.v0.json",
            "src/neurodecodekit/experiments/iackd_role_aware_dual_reversal.py",
            "docs/IACKD_ROLE_AWARE_DUAL_REVERSAL_SYNTHETIC_RESULT.md",
            "tests/test_iackd_role_aware_dual_reversal_synthetic_result.py",
        ):
            self.assertIn(required, paths)

    def test_execution_resources_and_replay_are_exact(self):
        execution = self.result["registered_execution"]
        self.assertEqual(execution["invocations"], 1)
        self.assertEqual(execution["runtime_seconds"], 5.024801375111565)
        self.assertEqual(execution["peak_RSS_bytes"], 257130496)
        self.assertEqual(execution["output_bytes"], 30170)
        self.assertEqual(execution["report_sha256"], "050914f9cf493ca95369dd22e39242746be211beb9d88b5ee15457945acaceeb")
        self.assertEqual(execution["primary_parameter_update_fits"], 660)
        self.assertEqual(execution["primary_prediction_sets"], 900)
        self.assertEqual(execution["replay_parameter_update_fits"], 660)
        self.assertEqual(execution["replay_prediction_sets"], 900)
        self.assertTrue(execution["deterministic_replay"])
        self.assertTrue(execution["temporary_report_removed"])

    def test_firewall_hashes_and_counts_are_exact(self):
        firewall = self.result["target_firewall_and_freeze"]
        self.assertEqual(firewall["fit_rows"], 3136)
        self.assertEqual(firewall["final_target_free_rows"], 960)
        self.assertEqual(firewall["final_target_fields_visible_to_model_stage"], 0)
        self.assertEqual(firewall["prediction_sets"], 900)
        self.assertEqual(firewall["split_sha256"], "bc2e3a7b4df65d666dc2b23598668a875b67e93d150318c7cd1206a6408dcd74")
        self.assertEqual(firewall["canonical_prediction_sha256"], "407571b8bd8146a8c54ae172e25c7c51190c712e39b5487f1036e290ce948893")
        self.assertEqual(firewall["freeze_record_sha256"], "c59d590e5e277fcb594048c3a9684448bf3e653a7c0d37854cf0fbc3e3381277")
        self.assertFalse(firewall["individual_predictions_published"])
        self.assertFalse(firewall["individual_participant_metrics_published"])

    def test_constructed_route_is_explicitly_non_scientific(self):
        route = self.result["constructed_router_result"]
        self.assertEqual(route["route"], "IACKD2-R5")
        self.assertTrue(route["H0"])
        self.assertEqual(route["H1"], {"C2I": True, "I2C": True})
        self.assertEqual(route["H2"], {"C2I": True, "I2C": True})
        self.assertEqual(route["H3"], {"C2I": True, "I2C": True})
        self.assertEqual(route["participant_minimum_arm_margin_mean"], 1.0)
        self.assertFalse(route["has_source_or_scientific_meaning"])
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_every_forbidden_counter_remains_zero(self):
        for name, value in self.result["forbidden_access_counters"].items():
            self.assertEqual(value, 0, name)

    def test_document_keeps_engineering_and_scientific_sentences_separate(self):
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("Synthetic", document)
        self.assertIn("zero scientific value", document)
        self.assertIn("No real or public IACKD payload", document)


if __name__ == "__main__":
    unittest.main()
