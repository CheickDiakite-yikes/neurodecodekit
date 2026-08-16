import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT / "registries/marc2_validation_coverage_localization_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def walk(value):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key, nested
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class Marc2ValidationCoverageLocalizationResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_route_and_posture_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_validation_coverage_localization_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VL1")
        self.assertEqual(self.result["route"], "MARC2VL-R2")
        self.assertIn("artifact", self.result["proof_posture"])

    def test_upstream_consumed_result_was_remotely_green(self):
        proof = self.result["upstream_consumed_result_proof"]
        self.assertEqual(
            proof["commit"], "b19a6e253c7d52aff9a6ec22e314a09e8017d644"
        )
        self.assertEqual(proof["CI_run_id"], 31_939_990_034)
        self.assertEqual(proof["base_python_job_id"], 95_147_662_770)
        self.assertEqual(proof["optional_neuro_job_id"], 95_147_662_795)
        self.assertTrue(proof["both_required_jobs_green_before_localization"])
        self.assertFalse(proof["exact_private_predicate_available"])

    def test_contract_and_tracked_hashes_are_current(self):
        contract = self.result["contract"]
        self.assertEqual(sha256_file(ROOT / contract["path"]), contract["sha256"])
        for binding in self.result["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_public_source_and_eligible_subset_counts_are_exact(self):
        source = self.result["public_source_space"]
        self.assertEqual(source["inventory_rows"], 1227)
        self.assertEqual(source["regular_file_rows"], 1025)
        self.assertEqual(source["directory_rows"], 202)
        self.assertEqual(source["published_participants"], 23)
        self.assertEqual(source["published_runs"], 238)
        self.assertEqual(source["eligible_participants"], 19)
        self.assertEqual(source["eligible_session_1_2_runs"], 195)

    def test_generated_fixture_gap_is_exact(self):
        coverage = self.result["generated_fixture_coverage"]
        self.assertEqual(coverage["published_minus_eligible_participants"], 4)
        self.assertEqual(coverage["published_minus_eligible_runs"], 43)
        self.assertEqual(coverage["required_companions_per_run"], 4)
        self.assertEqual(coverage["generated_eligible_core_rows"], 780)
        self.assertEqual(coverage["published_space_companion_slots"], 952)
        self.assertEqual(coverage["generated_coverage_gap_companion_slots"], 172)
        self.assertEqual(coverage["generated_auxiliary_regular_rows"], 245)
        self.assertTrue(coverage["source_domain_coverage_blind_spot"])

    def test_validator_applies_global_total_before_eligibility(self):
        order = self.result["validator_order"]
        self.assertLess(
            order["global_group_total_line"], order["eligibility_lookup_line"]
        )
        self.assertTrue(
            order["global_exact_group_total_precedes_eligibility_counting"]
        )

    def test_route_class_is_localized_without_private_predicate(self):
        route = self.result["route_class_localization"]
        self.assertEqual(route["LA1_F02_maps_to_outer_failure_index"], 2)
        self.assertTrue(route["source_envelope_or_entry_class_consistent"])
        self.assertFalse(route["transport_or_digest_class_reached"])
        self.assertFalse(route["identity_bridge_class_reached"])
        self.assertFalse(route["green_adapter_or_selector_execution_reached"])
        self.assertFalse(route["exact_private_predicate_identified"])

    def test_root_cause_is_fixture_and_validator_engineering(self):
        root_cause = self.result["root_cause"]
        self.assertEqual(root_cause["omitted_published_run_slots"], 43)
        self.assertEqual(root_cause["omitted_four_companion_slots"], 172)
        self.assertFalse(root_cause["exact_private_predicate_proven"])
        self.assertFalse(root_cause["private_source_malformed_inferred"])
        self.assertFalse(root_cause["data_or_scientific_failure"])

    def test_prospective_repair_filters_before_counting(self):
        design = self.result["prospective_repair_design"]
        self.assertTrue(design["separate_source_validity_from_selection_eligibility"])
        self.assertTrue(design["filter_eligibility_before_exact_195_run_comparison"])
        self.assertTrue(
            design[
                "represent_all_43_omitted_published_run_slots_as_Freewill_shaped_generated_adversaries"
            ]
        )
        self.assertFalse(design["patch_retry_or_reuse_consumed_LA2"])
        self.assertTrue(design["future_private_read_requires_new_contract_and_Tier_C_decision"])

    def test_measurements_are_exact_and_within_caps(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["input_artifact_count"], 10)
        self.assertEqual(measured["input_bytes"], 411_305)
        self.assertEqual(measured["Python_AST_parses"], 5)
        self.assertEqual(measured["strict_JSON_parses"], 5)
        self.assertLess(measured["runtime_seconds"], 10)
        self.assertLess(measured["peak_RSS_bytes"], 128 * 1024**2)
        self.assertLess(measured["aggregate_output_bytes"], 1024**2)
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertEqual(measured["CPU_threads"], 1)

    def test_every_forbidden_operation_counter_is_zero(self):
        counters = self.result["access_counters"]
        self.assertEqual(counters["committed_contract_and_artifact_reads"], 10)
        self.assertTrue(
            all(
                value == 0
                for key, value in counters.items()
                if key != "committed_contract_and_artifact_reads"
            )
        )

    def test_result_contains_no_private_path_or_payload_detail(self):
        forbidden_keys = {
            "crc32",
            "decoded_text",
            "labels",
            "member_name",
            "predictions",
            "private_path",
            "signal",
            "target",
            "targets",
        }
        for key, value in walk(self.result):
            self.assertNotIn(key.lower(), forbidden_keys)
            if isinstance(value, str):
                self.assertNotIn(".codex_work", value)
                self.assertNotIn("_eeg.", value)

    def test_disposition_keeps_consumed_root_and_FW2_closed(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["artifact_only_diagnosis_complete"])
        self.assertTrue(disposition["MARC2_LA2_consumed"])
        self.assertFalse(
            disposition["consumed_executor_may_be_modified_reused_retried_or_resumed"]
        )
        self.assertFalse(disposition["private_source_or_output_reinspection_allowed"])
        self.assertFalse(disposition["MARC2_FW2_eligible"])

    def test_claim_boundary_stays_engineering_only(self):
        claim = self.result["claim_boundary"]
        self.assertIn("43 published run slots", claim["engineering_capability_added"])
        scientific = claim["scientific_claim_not_established"].lower()
        self.assertIn("no private manifest", scientific)
        self.assertIn("no neural effect", scientific)
        self.assertIn("thought-to-text", scientific)


if __name__ == "__main__":
    unittest.main()
