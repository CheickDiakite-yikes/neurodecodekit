import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries/marc2_live_adapter_recovery_failure_result.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveAdapterRecoveryFailureResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_is_consumed_F02_without_retry(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_live_adapter_recovery_failure_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-LA2")
        self.assertEqual(self.result["route"], "MARC2LAR-F02")
        self.assertEqual(
            self.result["status"],
            "consumed_failed_LA1_source_refusal_no_retry_or_rerun",
        )

    def test_all_committed_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_exact_implementation_was_remotely_green_before_execution(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "5390e068bff24beaf878ac1facff7708c5449249",
        )
        self.assertEqual(proof["CI_run_id"], 31_939_483_560)
        self.assertEqual(proof["base_python_job_id"], 95_146_470_514)
        self.assertEqual(proof["optional_neuro_job_id"], 95_146_470_539)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])

    def test_private_source_was_read_once_and_integrity_gated(self):
        execution = self.result["private_execution"]
        self.assertEqual(execution["private_manifest_bytes"], 418_755)
        self.assertEqual(execution["content_opens"], 1)
        self.assertEqual(execution["body_reads"], 1)
        self.assertEqual(execution["SHA256_passes"], 1)
        self.assertEqual(execution["strict_JSON_parses"], 1)
        self.assertTrue(execution["registered_size_and_SHA256_passed"])
        self.assertTrue(execution["consumed_marker_preceded_content_open"])

    def test_LA1_refused_before_selector_or_selection(self):
        stop = self.result["stop_result"]
        self.assertEqual(stop["stage"], "live_adapter_and_frozen_selector")
        self.assertEqual(stop["aggregate_safe_reason"], "LA1 adapter refused source")
        self.assertFalse(stop["nested_LA1_predicate_available"])
        self.assertEqual(stop["LA1_success_calls"], 0)
        self.assertEqual(stop["selector_calls"], 0)
        selection = self.result["selection_result"]
        self.assertTrue(all(value == 0 for value in selection.values()))

    def test_runtime_and_machine_measurements_are_bounded(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["runtime_seconds"], 0.06782554200617597)
        self.assertEqual(measured["peak_RSS_bytes"], 29_425_664)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertGreaterEqual(measured["free_disk_bytes_before_consumption"], 15 * 1024**3)

    def test_output_measurement_discrepancy_is_explicit(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["aggregate_receipt_observed_bytes"], 5_695)
        self.assertEqual(measured["receipt_reported_output_bytes"], 6_096)
        self.assertEqual(measured["output_measurement_difference_bytes"], 401)
        self.assertEqual(
            measured["aggregate_receipt_sha256"],
            "22900982d87a5d6565da2734011358fc6ef137cfc2fc002ddc9c4cb26c7a9f90",
        )
        self.assertFalse(measured["consumed_marker_bytes_inspected"])

    def test_every_forbidden_operation_counter_is_zero(self):
        counters = self.result["forbidden_operation_counters"]
        self.assertGreaterEqual(len(counters), 18)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_execution_is_parked_and_FW2_is_closed(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["registered_execution_consumed"])
        self.assertEqual(disposition["retry_rerun_or_resume_limit"], 0)
        self.assertFalse(disposition["private_reinspection_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])
        self.assertTrue(disposition["new_Tier_C_decision_required_for_any_private_read"])

    def test_claim_boundary_and_unavailable_predicate_are_explicit(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("failed closed", boundary["engineering_capability_added"])
        scientific = boundary["scientific_claim_not_established"].lower()
        self.assertIn("no neural payload", scientific)
        self.assertIn("thought-to-text", scientific)
        self.assertIn("nested LA1 refusal predicate", self.result["unavailable_fields"])


if __name__ == "__main__":
    unittest.main()
