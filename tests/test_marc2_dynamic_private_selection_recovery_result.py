import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_dynamic_private_selection_recovery_failure_result.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_DYNAMIC_PRIVATE_SELECTION_RECOVERY_RESULT.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2DynamicPrivateSelectionRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_routes_and_consumption_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_dynamic_private_selection_recovery_failure_result",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR7P")
        self.assertEqual(self.record["route"], "MARC2VR7P-F07")
        self.assertEqual(self.record["upstream_VR6_route"], "MARC2VR6-F02")
        disposition = self.record["disposition"]
        self.assertTrue(disposition["registered_execution_consumed"])
        self.assertEqual(disposition["retry_rerun_or_resume_limit"], 0)

    def test_green_implementation_proof_is_exact(self):
        proof = self.record["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "154852c58af080904087a2e4cef71991dcb6179d"
        )
        self.assertEqual(proof["CI_run_id"], 31_982_672_176)
        self.assertEqual(proof["base_python_job_id"], 95_252_133_987)
        self.assertEqual(proof["optional_neuro_job_id"], 95_252_133_958)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])
        result_proof = self.record["verification"]["remote_proof"]
        self.assertFalse(self.record["verification"]["remote_CI_pending"])
        self.assertEqual(
            result_proof["commit"],
            "ae75423ce9e60c08599ba31fc40f3a6ea584d70e",
        )
        self.assertEqual(result_proof["CI_run_id"], 31_983_281_390)
        self.assertEqual(result_proof["base_python_job_id"], 95_253_771_315)
        self.assertEqual(result_proof["optional_neuro_job_id"], 95_253_771_324)
        self.assertTrue(result_proof["both_required_jobs_green"])

    def test_bound_public_artifact_hashes_match(self):
        seen = set()
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])
        self.assertGreaterEqual(len(seen), 7)

    def test_one_read_and_both_adapter_boundaries_are_recorded(self):
        execution = self.record["private_execution"]
        self.assertTrue(execution["exact_remote_proof_validation_passed"])
        self.assertTrue(execution["fresh_readiness_passed"])
        self.assertEqual(execution["consumed_markers"], 1)
        self.assertEqual(execution["private_structural_content_opens"], 1)
        self.assertEqual(execution["private_structural_bytes"], 418_755)
        self.assertTrue(execution["private_structural_registered_SHA256_matched"])
        self.assertEqual(execution["strict_JSON_parses"], 1)
        self.assertEqual(execution["VR6_adapter_calls"], 1)
        self.assertEqual(execution["VR6_adapter_successes"], 0)
        self.assertEqual(execution["VR2_validation_calls"], 1)

    def test_refusal_preceded_cohort_and_reports(self):
        stop = self.record["stop_result"]
        self.assertEqual(stop["stage"], "VR6_upstream_VR2_validation")
        self.assertEqual(stop["aggregate_safe_reason"], "dynamic live selection refused")
        self.assertFalse(stop["nested_VR2_route_available"])
        self.assertFalse(stop["exact_failed_predicate_available"])
        execution = self.record["private_execution"]
        self.assertEqual(execution["private_selection_manifests"], 0)
        self.assertEqual(execution["aggregate_reports"], 0)
        self.assertEqual(execution["real_cohort_freezes"], 0)

    def test_measurements_preserve_unavailable_values(self):
        measurements = self.record["measurements"]
        self.assertGreaterEqual(
            measurements["external_observed_wait_lower_bound_seconds"], 60
        )
        self.assertTrue(measurements["completed_below_650_second_cap"])
        for key in (
            "external_invocation_wall_seconds",
            "internal_runtime_seconds",
            "peak_RSS_bytes",
            "fresh_readiness_sample_count",
            "retained_output_bytes",
            "minimum_free_disk_bytes",
            "maximum_normalized_load",
        ):
            self.assertIsNone(measurements[key])

    def test_forbidden_operations_are_zero(self):
        self.assertTrue(
            all(
                value == 0
                for value in self.record["forbidden_operation_counters"].values()
            )
        )

    def test_no_cohort_and_FW2_remains_closed(self):
        selection = self.record["selection_result"]
        self.assertFalse(selection["real_cohort_identity_available"])
        self.assertEqual(selection["persisted_selected_subjects"], 0)
        self.assertEqual(selection["persisted_selected_bundles"], 0)
        self.assertEqual(selection["persisted_selected_members"], 0)
        self.assertFalse(self.record["disposition"]["MARC2_FW2_eligible"])

    def test_warnings_and_unavailable_fields_are_explicit(self):
        warnings = " ".join(self.record["warnings"]).lower()
        unavailable = " ".join(self.record["unavailable_fields"]).lower()
        self.assertIn("no retry", warnings)
        self.assertIn("do not", warnings)
        self.assertIn("nested vr2", unavailable)
        self.assertIn("readiness", unavailable)
        self.assertIn("neural", unavailable)

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("`MARC2-FW2` and `MARC2-CIL1` remain", text)
        self.assertIn("no retry, rerun, resume", text.lower())


if __name__ == "__main__":
    unittest.main()
