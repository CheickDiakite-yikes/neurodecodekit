import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_source_validity_eligibility_repair_result.v0.json"
)
DOC_PATH = (
    ROOT / "docs" / "MARC_2_SOURCE_VALIDITY_ELIGIBILITY_REPAIR_RESULT.md"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2SourceValidityEligibilityRepairResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_source_validity_eligibility_repair_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR1")
        self.assertEqual(self.result["route"], "MARC2VR-G1")
        self.assertEqual(
            self.result["status"],
            "completed_generated_only_qualification_consumed_no_rerun",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "4d587dfc552f4a034d38444634cb87e22483bc54",
        )
        self.assertEqual(proof["CI_run_id"], 31_943_437_003)
        self.assertEqual(proof["base_python_job_id"], 95_155_811_373)
        self.assertEqual(proof["optional_neuro_job_id"], 95_155_811_384)
        self.assertTrue(proof["both_required_jobs_green_before_registered_closeout"])

    def test_every_tracked_input_hash_is_current(self):
        for binding in self.result["tracked_input_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]), binding["sha256"]
                )

    def test_registered_execution_is_exactly_once_and_not_reconstructed(self):
        execution = self.result["registered_execution"]
        self.assertEqual(execution["registered_execution_count"], 1)
        self.assertEqual(execution["completed_execution_count"], 1)
        self.assertEqual(execution["retry_or_rerun_count"], 0)
        self.assertFalse(execution["report_retained"])
        self.assertIsNone(execution["report_SHA256"])
        self.assertIn("not retained", execution["report_SHA256_unavailable_reason"])

    def test_source_domain_and_predicate_counts_are_exact(self):
        source = self.result["source_domain_summary"]
        self.assertEqual(source["inventory_rows"], 1_227)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["eligible_run_bundles_after_filter"], 195)
        self.assertEqual(source["source_valid_but_ineligible_run_bundles"], 43)
        self.assertTrue(source["exact_195_assertion_applied_after_filter"])
        self.assertFalse(source["global_195_assertion_applied_before_filter"])
        self.assertEqual(
            [row["bundle_count"] for row in self.result["predicate_summary"]],
            [195, 12, 24, 7],
        )

    def test_frozen_selection_replayed_without_ineligible_rows(self):
        selection = self.result["selection_summary"]
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(selection["ineligible_selected_bundles"], 0)
        self.assertEqual(selection["ineligible_selected_companions"], 0)
        self.assertFalse(selection["target_quality_or_outcome_used"])

    def test_replay_and_all_mutations_passed(self):
        replay = self.result["replay_summary"]
        self.assertEqual(replay["success_paths"], 2)
        self.assertTrue(replay["canonical_reversed_source_hash_equal"])
        self.assertTrue(replay["canonical_reversed_selection_identity_equal"])
        mutations = self.result["mutation_summary"]
        self.assertEqual(mutations["required_mutations"], 36)
        self.assertEqual(mutations["refused_mutations"], 36)
        self.assertTrue(mutations["all_registered_refusal_routes_exercised"])
        self.assertEqual(
            set(mutations["route_counts"]),
            {f"MARC2VR-F{index:02d}" for index in range(1, 9)},
        )

    def test_measurements_are_exact_and_within_caps(self):
        measured = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measured["generated_input_bytes"], 858_844)
        self.assertEqual(measured["aggregate_output_bytes"], 4_680)
        self.assertEqual(measured["runtime_seconds"], 0.20698016599635594)
        self.assertEqual(measured["peak_RSS_bytes"], 32_391_168)
        self.assertLess(measured["runtime_seconds"], caps["runtime_seconds"])
        self.assertLess(measured["peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertEqual(measured["retained_generated_output_bytes"], 0)
        self.assertFalse(measured["end_to_end_latency_measured"])

    def test_every_forbidden_counter_is_zero_and_gate_passed(self):
        self.assertTrue(
            all(value == 0 for value in self.result["access_counters"].values())
        )
        self.assertTrue(all(self.result["acceptance_gates"].values()))

    def test_disposition_closes_rerun_private_access_and_FW2(self):
        disposition = self.result["disposition"]
        self.assertTrue(disposition["generated_closeout_complete"])
        self.assertTrue(disposition["generated_closeout_consumed"])
        self.assertFalse(disposition["retry_or_rerun_allowed"])
        self.assertFalse(disposition["private_read_or_real_executor_allowed"])
        self.assertFalse(disposition["MARC2_FW2_allowed"])
        self.assertTrue(
            disposition[
                "future_private_read_requires_new_contract_generated_qualification_Tier_C_request_and_fresh_decision"
            ]
        )

    def test_document_and_claim_boundary_are_explicit(self):
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("The repair worked", text)
        self.assertIn("no retry or rerun", text)
        self.assertIn("Scientific claim not established", text)
        boundary = self.result["claim_boundary"]
        self.assertIn("full generated 238-bundle", boundary["engineering_capability_added"])
        self.assertIn("No private archive", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
