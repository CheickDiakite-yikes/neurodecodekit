import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries/marc2_variable_domain_private_recovery_failure_result.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_VARIABLE_DOMAIN_PRIVATE_RECOVERY_RESULT.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2VariableDomainPrivateRecoveryResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_consumed_route_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_variable_domain_private_recovery_failure_result",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR3")
        self.assertEqual(self.record["route"], "MARC2VDR-F01")
        self.assertTrue(self.record["disposition"]["registered_execution_consumed"])
        self.assertEqual(self.record["disposition"]["retry_rerun_or_resume_limit"], 0)

    def test_green_implementation_proof_is_exact(self):
        proof = self.record["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "24678760106b6a5a9ea035c14f628ec909755e61"
        )
        self.assertEqual(proof["CI_run_id"], 31964473405)
        self.assertEqual(proof["base_python_job_id"], 95207398015)
        self.assertEqual(proof["optional_neuro_job_id"], 95207398092)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_bound_artifact_hashes_match(self):
        seen = set()
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )
        self.assertGreaterEqual(len(seen), 7)

    def test_failure_preceded_every_private_or_output_operation(self):
        execution = self.record["private_execution"]
        self.assertTrue(execution["exact_remote_proof_validation_passed"])
        self.assertFalse(execution["machine_resource_preflight_passed"])
        self.assertEqual(execution["registered_output_root_operations"], 0)
        self.assertEqual(execution["consumed_markers"], 0)
        self.assertEqual(execution["registered_private_path_component_checks"], 0)
        self.assertEqual(execution["private_manifest_content_opens"], 0)
        self.assertEqual(execution["private_manifest_bytes"], 0)
        self.assertEqual(execution["VR2_adapter_calls"], 0)

    def test_exact_machine_predicate_is_unavailable(self):
        stop = self.record["stop_result"]
        self.assertEqual(stop["stage"], "machine_resource_preflight")
        self.assertEqual(stop["aggregate_safe_reason"], "machine resource preflight refused")
        self.assertFalse(stop["exact_failed_predicate_available"])
        self.assertTrue(stop["post_hoc_machine_snapshot_is_not_execution_evidence"])
        measurements = self.record["measurements"]
        for key in (
            "internal_runtime_seconds",
            "peak_RSS_bytes",
            "normalized_one_minute_load",
            "free_disk_bytes",
            "logical_CPUs",
        ):
            self.assertIsNone(measurements[key])

    def test_external_wall_and_generated_bytes_are_bounded(self):
        measurements = self.record["measurements"]
        self.assertGreater(measurements["external_invocation_wall_seconds"], 0)
        self.assertLess(measurements["external_invocation_wall_seconds"], 30)
        self.assertEqual(measurements["private_input_bytes"], 0)
        self.assertEqual(measurements["generated_output_bytes"], 0)
        self.assertEqual(measurements["incremental_disk_bytes"], 0)

    def test_every_forbidden_counter_is_zero(self):
        self.assertTrue(
            all(
                value == 0
                for value in self.record["forbidden_operation_counters"].values()
            )
        )

    def test_no_real_cohort_and_FW2_remains_closed(self):
        selection = self.record["selection_result"]
        self.assertEqual(selection["selected_subjects"], 0)
        self.assertEqual(selection["selected_run_bundles"], 0)
        self.assertEqual(selection["selected_core_members"], 0)
        disposition = self.record["disposition"]
        self.assertFalse(disposition["real_cohort_identity_available"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])
        self.assertTrue(disposition["new_Tier_C_decision_required_for_any_private_read"])

    def test_warnings_and_unavailable_fields_are_explicit(self):
        warnings = " ".join(self.record["warnings"]).lower()
        unavailable = " ".join(self.record["unavailable_fields"]).lower()
        self.assertIn("no retry", warnings)
        self.assertIn("generated", warnings)
        self.assertIn("machine", unavailable)
        self.assertIn("cohort", unavailable)
        self.assertIn("neural", unavailable)

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("zero bytes and zero content opens", text)
        self.assertIn("`MARC2-FW2` remains ineligible", text)


if __name__ == "__main__":
    unittest.main()
