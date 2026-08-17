import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc2_two_layer_private_diagnostic_result.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_2_TWO_LAYER_PRIVATE_DIAGNOSTIC_RESULT.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2TwoLayerPrivateDiagnosticResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record_bytes = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.record_bytes)

    def test_identity_routes_and_consumption_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_two_layer_private_diagnostic_result",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-VR9P")
        self.assertEqual(self.record["route"], "MARC2VR9P-R1")
        self.assertEqual(self.record["outer_VR6_route"], "MARC2VR6-F02")
        self.assertEqual(self.record["nested_VR2_route"], "MARC2VR2-F03")
        disposition = self.record["disposition"]
        self.assertTrue(disposition["registered_execution_consumed"])
        self.assertEqual(disposition["retry_rerun_or_resume_limit"], 0)

    def test_green_implementation_proof_is_exact(self):
        proof = self.record["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "0dd113a9a0259b6192e3997eae62369b9cc5a85b"
        )
        self.assertEqual(proof["CI_run_id"], 31_995_078_475)
        self.assertEqual(proof["base_python_job_id"], 95_285_174_846)
        self.assertEqual(proof["optional_neuro_job_id"], 95_285_174_911)
        self.assertTrue(proof["both_required_jobs_green_before_execution"])
        self.assertEqual(
            proof["proof_record_sha256"],
            "681239756ff301c92fb2fee95f30693d53ce4c418597223a9371b568d28bb265",
        )

    def test_bound_public_artifact_hashes_match(self):
        seen = set()
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                self.assertNotIn(binding["path"], seen)
                seen.add(binding["path"])
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])
        self.assertGreaterEqual(len(seen), 6)

    def test_one_read_and_two_layer_route_are_recorded(self):
        execution = self.record["private_execution"]
        self.assertEqual(execution["invocations"], 1)
        self.assertEqual(execution["fresh_readiness_samples"], 3)
        self.assertEqual(execution["private_structural_content_opens"], 1)
        self.assertEqual(execution["private_structural_bytes"], 418_755)
        self.assertTrue(execution["private_structural_integrity_matched"])
        self.assertEqual(execution["strict_JSON_parses"], 1)
        self.assertEqual(execution["VR6_adapter_calls"], 1)
        self.assertEqual(execution["VR2_validation_calls"], 1)
        self.assertEqual(execution["aggregate_reports"], 1)

    def test_measurements_are_exact_and_bounded(self):
        measurements = self.record["measurements"]
        self.assertEqual(measurements["source_input_bytes"], 418_755)
        self.assertAlmostEqual(measurements["runtime_seconds"], 10.044833040999947)
        self.assertEqual(measurements["peak_RSS_bytes"], 39_075_840)
        self.assertEqual(measurements["combined_output_bytes"], 6_674)
        self.assertEqual(measurements["fresh_readiness_samples"], 3)
        self.assertLessEqual(measurements["maximum_normalized_one_minute_load"], 1.0)
        self.assertGreaterEqual(measurements["minimum_free_disk_bytes"], 15 * 2**30)
        self.assertEqual(measurements["CPU_threads"], 1)
        self.assertEqual(measurements["workers"], 1)
        self.assertEqual(measurements["numerical_jobs"], 1)
        self.assertFalse(measurements["end_to_end_latency_measured"])

    def test_route_localizes_without_disclosing_predicate(self):
        localization = self.record["localization_result"]
        self.assertEqual(
            localization["aggregate_class"],
            "row_path_ZIP_BIDS_run_companion_or_structural_grouping",
        )
        self.assertTrue(localization["F04_excluded_for_exact_execution"])
        for key in (
            "exact_failed_predicate_available",
            "failed_private_value_available",
            "source_row_or_path_available",
            "candidate_selection_or_cohort_available",
        ):
            self.assertFalse(localization[key])

    def test_forbidden_operations_are_zero(self):
        self.assertTrue(
            all(
                value == 0
                for value in self.record["forbidden_operation_counters"].values()
            )
        )

    def test_public_record_does_not_copy_private_identifiers(self):
        text = self.record_bytes.decode("utf-8")
        for forbidden in (
            ".codex_work",
            "member_inventory.private",
            "2a2e48b88ee59332a199d926554bb6921222fff92046a0fc9b07cf73fd6c3031",
            "sub-",
            "ses-",
        ):
            self.assertNotIn(forbidden, text)

    def test_warnings_unavailable_fields_and_closed_FW2_are_explicit(self):
        warnings = " ".join(self.record["warnings"]).lower()
        unavailable = " ".join(self.record["unavailable_fields"]).lower()
        self.assertIn("no retry", warnings)
        self.assertIn("structural", warnings)
        self.assertIn("predicate", unavailable)
        self.assertIn("neural", unavailable)
        self.assertFalse(self.record["disposition"]["MARC2_FW2_eligible"])
        self.assertFalse(self.record["disposition"]["MARC2_CIL1_eligible"])

    def test_document_separates_engineering_and_science(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added", text)
        self.assertIn("Scientific claim not established", text)
        self.assertIn("`MARC2-FW2` and `MARC2-CIL1` remain", text)
        self.assertIn("no retry, rerun, resume", text.lower())


if __name__ == "__main__":
    unittest.main()
