import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries" / "marc2_live_domain_eligibility_adapter_result.v0.json"
)
DOC_PATH = ROOT / "docs" / "MARC_2_LIVE_DOMAIN_ELIGIBILITY_ADAPTER_RESULT.md"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveDomainEligibilityAdapterResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_result_identity_route_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_live_domain_eligibility_adapter_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(self.result["lane_id"], "MARC2-VR2")
        self.assertEqual(self.result["route"], "MARC2VR2-G1")
        self.assertEqual(
            self.result["status"],
            "completed_generated_only_qualification_consumed_no_rerun_remote_green",
        )

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"],
            "f62a3f5b9966967c569e734552cbc3f11d009401",
        )
        self.assertEqual(proof["CI_run_id"], 31_946_112_252)
        self.assertEqual(proof["base_python_job_id"], 95_162_220_059)
        self.assertEqual(proof["optional_neuro_job_id"], 95_162_220_159)
        self.assertTrue(proof["both_required_jobs_green_before_registered_closeout"])
        closeout = self.result["closeout_remote_proof"]
        self.assertEqual(
            closeout["result_commit"],
            "7b6899b987dbd64401494ff2901ade1444f1bf60",
        )
        self.assertEqual(closeout["CI_run_id"], 31_946_852_669)
        self.assertEqual(closeout["base_python_job_id"], 95_164_134_927)
        self.assertEqual(closeout["optional_neuro_job_id"], 95_164_134_941)
        self.assertTrue(closeout["both_required_jobs_green"])
        self.assertFalse(closeout["pending"])

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

    def test_all_variable_profiles_reconcile_without_live_overconstraint(self):
        source = self.result["source_domain_summary"]
        self.assertEqual(source["inventory_rows"], 1_227)
        self.assertEqual(source["complete_source_run_bundles"], 238)
        self.assertEqual(source["eligible_run_bundles_after_filter"], 195)
        self.assertEqual(source["valid_ineligible_run_bundles"], 43)
        self.assertFalse(source["exact_ineligible_breakdown_required_of_live_source"])
        self.assertFalse(source["generated_profile_identity_required_of_live_source"])
        profiles = self.result["profile_summary"]
        self.assertEqual([profile["profile"] for profile in profiles], list("ABCD"))
        self.assertEqual(
            [list(profile["predicate_counts"].values()) for profile in profiles],
            [[12, 24, 7], [8, 20, 15], [16, 12, 15], [4, 4, 35]],
        )
        self.assertTrue(
            all(profile["canonical_reversed_source_hash_equal"] for profile in profiles)
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
        self.assertEqual(replay["profiles"], 4)
        self.assertEqual(replay["row_orders_per_profile"], 2)
        self.assertEqual(replay["success_paths"], 8)
        self.assertTrue(replay["all_selection_identities_equal"])
        mutations = self.result["mutation_summary"]
        self.assertEqual(mutations["required_mutations"], 58)
        self.assertEqual(mutations["refused_mutations"], 58)
        self.assertTrue(mutations["all_registered_refusal_routes_exercised"])
        self.assertEqual(
            set(mutations["route_counts"]),
            {f"MARC2VR2-F{index:02d}" for index in range(1, 9)},
        )

    def test_measurements_are_exact_and_within_caps(self):
        measured = self.result["measurements"]
        caps = self.result["resource_caps"]
        self.assertEqual(measured["generated_input_bytes"], 3_435_280)
        self.assertEqual(measured["aggregate_output_bytes"], 4_748)
        self.assertEqual(measured["runtime_seconds"], 0.5122641660127556)
        self.assertEqual(measured["peak_RSS_bytes"], 32_620_544)
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
        self.assertIn("passed its complete generated", text)
        self.assertIn("no retry or rerun", text)
        self.assertIn("Scientific claim not established", text)
        boundary = self.result["claim_boundary"]
        self.assertIn("variable valid", boundary["engineering_capability_added"])
        self.assertIn("No private archive", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
