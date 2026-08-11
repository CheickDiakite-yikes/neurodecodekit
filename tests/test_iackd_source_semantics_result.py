import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "registries" / "iackd_source_semantics_result.v0.json"
DOCUMENT_PATH = ROOT / "docs" / "IACKD_SOURCE_SEMANTICS_RESULT.md"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IACKDSourceSemanticsResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")

    def test_schema_status_and_proof_posture_are_generated_only(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.iackd_source_semantics_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertIn("generated_policy_mechanics_passed", self.result["status"])
        self.assertIn("zero_real_public_local_bundle", self.result["proof_posture"])

    def test_green_research_and_implementation_precede_closeout(self):
        proof = self.result["green_proof_chain"]
        self.assertEqual(proof["research"]["commit"], "ed5ce8292c2c1dc842898023cfe8cb608e9d4476")
        self.assertEqual(proof["research"]["CI_run_id"], 31_445_790_741)
        self.assertTrue(proof["research"]["both_required_jobs_green"])
        self.assertEqual(
            proof["implementation"]["commit"],
            "8c5784ad3e664f816899e2f1139600b2c66a8232",
        )
        self.assertEqual(proof["implementation"]["CI_run_id"], 31_446_902_756)
        self.assertTrue(proof["implementation"]["both_required_jobs_green"])

    def test_preflight_refused_before_semantics_and_one_closeout_completed(self):
        preflight = self.result["preflight"]
        self.assertEqual(preflight["refused_invocations"], 1)
        self.assertEqual(
            preflight["refusal_id"],
            "IACKDS-F14-output-path-write-or-resource-cap",
        )
        self.assertEqual(preflight["policy_registry_reads"], 0)
        self.assertEqual(preflight["generated_fixture_builds"], 0)
        self.assertFalse(preflight["consumed_semantic_qualification"])
        execution = self.result["execution"]
        self.assertEqual(execution["successful_semantic_qualifications"], 1)
        self.assertEqual(execution["retry_or_rerun_after_semantic_execution"], 0)
        self.assertFalse(execution["report_retained"])
        self.assertTrue(execution["only_closeout_generated_file_removed"])

    def test_measurements_are_exact_and_below_caps(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["generated_fixture_input_bytes"], 6093)
        self.assertEqual(measured["generated_output_bytes"], 6834)
        self.assertEqual(measured["generated_channel_rows"], 60)
        self.assertEqual(measured["semantic_validation_passes"], 4)
        self.assertEqual(measured["mutation_attempts"], 13)
        self.assertEqual(measured["distinct_refusal_classes"], 12)
        self.assertLess(measured["runtime_seconds_through_report_build"], 30)
        self.assertLess(measured["peak_RSS_bytes_through_report_build"], 256 * 1024 * 1024)
        self.assertIsNone(measured["producer_is_causal"])
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_fixture_groups_preserve_counts_and_fixed_predictive_core(self):
        groups = self.result["fixture_groups"]
        self.assertEqual([row["row_count"] for row in groups], [29, 31])
        self.assertEqual([row["source_EEG_count"] for row in groups], [26, 28])
        self.assertEqual([row["source_MISC_count"] for row in groups], [3, 3])
        self.assertEqual([row["predictive_EEG_count"] for row in groups], [26, 26])
        self.assertEqual([row["geometry_available_count"] for row in groups], [26, 28])
        expected = {
            "source_order_sha256",
            "source_type_count_sha256",
            "functional_role_sha256",
            "model_inclusion_mask_sha256",
            "geometry_available_mask_sha256",
        }
        self.assertTrue(all(set(row["bindings"]) == expected for row in groups))

    def test_thirteen_mutations_cover_twelve_distinct_refusals(self):
        mutations = self.result["mutation_results"]
        self.assertEqual(len(mutations), 13)
        self.assertEqual(len({row["refusal_id"] for row in mutations}), 12)
        self.assertIn(
            "IACKDS-F12-forbidden-target-or-outcome-field",
            {row["refusal_id"] for row in mutations},
        )
        self.assertIn("count_spelling", {row["mutation"] for row in mutations})

    def test_every_gate_passes_and_every_forbidden_counter_is_zero(self):
        self.assertTrue(all(self.result["acceptance_gate_results"].values()))
        permitted = {
            "policy_registry_reads",
            "generated_fixture_builds",
            "generated_fixture_semantic_parses",
            "generated_mutation_attempts",
        }
        for name, value in self.result["access_counters"].items():
            if name not in permitted:
                self.assertEqual(value, 0, name)

    def test_verification_and_public_artifact_hashes_are_exact(self):
        verification = self.result["verification"]
        self.assertEqual(verification["focused_H3_tests"], 52)
        self.assertEqual(verification["complete_base_tests"], 1833)
        self.assertEqual(verification["complete_optional_tests"], 1904)
        self.assertEqual(verification["registry_JSON_files_valid"], 136)
        self.assertTrue(
            all(
                verification[field]
                for field in (
                    "focused_passed",
                    "complete_base_suite_passed",
                    "complete_optional_suite_passed",
                    "ruff_passed",
                    "compileall_passed",
                    "result_registry_cross_checked_against_temporary_report",
                    "module_CLI_inspect_passed",
                    "git_diff_check_passed",
                )
            )
        )
        binding = self.result["public_artifact_bindings"]
        self.assertEqual(sha256(DOCUMENT_PATH), binding["document_sha256"])
        self.assertFalse(binding["contains_local_path_or_individual_identity"])

    def test_document_and_registry_keep_scientific_boundary_explicit(self):
        self.assertIn("Engineering capability added:", self.document)
        self.assertIn("Scientific claim not established:", self.document)
        self.assertIn("no exact real IACKD source order was asserted", self.document)
        claim = self.result["claim_boundary"]
        self.assertIn("version-aware", claim["engineering_capability_added"])
        self.assertIn("no neural effect", claim["scientific_claim_not_established"])
        self.assertFalse(self.result["disposition"]["real_reader_validated"])
        self.assertFalse(self.result["disposition"]["IACKD2_authorized"])


if __name__ == "__main__":
    unittest.main()
