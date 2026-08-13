import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_prefix_selection_synthetic_result.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrefixSelectionSyntheticResultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    def test_identity_route_and_consumed_status_are_exact(self):
        self.assertEqual(
            self.result["schema_name"],
            "neurodecodekit.marc2_freewill_prefix_selection_synthetic_result",
        )
        self.assertEqual(self.result["schema_version"], "0.1.0")
        self.assertEqual(
            self.result["result_id"],
            "MARC-2-FW1-freewill-prefix-selection-registered-generated-result-v0",
        )
        self.assertEqual(self.result["route"], "MARC2FWG-R1")
        self.assertEqual(self.result["status"], "passed_consumed_no_retry_or_rerun")
        self.assertTrue(self.result["consumed"])

    def test_artifact_bindings_are_current(self):
        for binding in self.result["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_implementation_proof_is_exact(self):
        proof = self.result["green_implementation_proof"]
        self.assertEqual(
            proof["commit"], "36f87759967f03dd7ac5d543f6f5a24afb571365"
        )
        self.assertEqual(proof["CI_run_id"], 31_677_757_466)
        self.assertEqual(proof["base_job_id"], 94_375_991_713)
        self.assertEqual(proof["optional_neuro_job_id"], 94_375_991_770)
        self.assertTrue(proof["both_required_jobs_green"])

    def test_exact_public_prefix_and_counts_are_preserved(self):
        selection = self.result["selection_result"]
        self.assertEqual(selection["selected_subjects"], 16)
        self.assertEqual(selection["candidate_subjects_examined"], 17)
        self.assertEqual(selection["first_nonfitting_subject_id"], "sub-18")
        self.assertEqual(selection["fit_run_bundles"], 48)
        self.assertEqual(selection["heldout_run_bundles"], 48)
        self.assertEqual(selection["selected_run_bundles"], 96)
        self.assertEqual(selection["selected_core_members"], 384)
        self.assertTrue(selection["selection_is_maximal_contiguous_prefix"])

    def test_reservation_stops_before_next_participant(self):
        selection = self.result["selection_result"]
        self.assertEqual(selection["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(selection["reservation_cap_bytes"], 8 * 1024**3)
        self.assertEqual(selection["remaining_reservation_bytes"], 484_726_816)
        self.assertEqual(
            selection["first_nonfitting_subject_reservation_bytes"],
            506_575_486,
        )
        self.assertGreater(
            selection["first_nonfitting_subject_reservation_bytes"],
            selection["remaining_reservation_bytes"],
        )

    def test_boundaries_and_mutations_all_pass(self):
        self.assertEqual(self.result["boundary_result"]["passed"], 4)
        self.assertEqual(self.result["boundary_result"]["required"], 4)
        self.assertEqual(self.result["mutation_result"]["passed"], 40)
        self.assertEqual(self.result["mutation_result"]["required"], 40)
        self.assertEqual(sum(self.result["mutation_result"]["route_counts"].values()), 40)

    def test_measurements_fit_every_cap(self):
        measured = self.result["measurements"]
        self.assertEqual(measured["registered_executions"], 1)
        self.assertLess(measured["internal_runtime_seconds"], 30)
        self.assertLess(measured["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["combined_generated_output_bytes"], 2 * 1024**2)
        self.assertEqual(
            measured["aggregate_report_bytes"] + measured["private_generated_output_bytes"],
            measured["combined_generated_output_bytes"],
        )
        self.assertEqual(measured["private_output_mode"], "0600")
        self.assertFalse(measured["temporary_root_exists_after_cleanup"])
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertEqual(measured["producer_is_causal"], "not_applicable_metadata_only")
        verification = self.result["verification"]
        self.assertEqual(verification["focused_result_tests"], 12)
        self.assertEqual(verification["complete_base_tests"], 3_002)
        self.assertEqual(verification["complete_base_skips"], 204)
        self.assertEqual(verification["complete_optional_tests"], 3_073)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["all_registry_JSON_passed"])
        self.assertTrue(verification["artifact_hashes_passed"])
        self.assertFalse(verification["consumed_closeout_rerun_for_verification"])

    def test_output_hashes_are_recorded_without_retaining_outputs(self):
        outputs = self.result["output_receipt"]
        self.assertRegex(outputs["aggregate_report_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(outputs["private_output_sha256"], r"^[0-9a-f]{64}$")
        self.assertFalse(outputs["aggregate_report_retained"])
        self.assertFalse(outputs["private_output_retained"])
        self.assertFalse(outputs["temporary_root_retained"])
        self.assertTrue(outputs["private_output_hashed_opaquely"])
        self.assertFalse(outputs["private_output_parsed_for_result"])

    def test_all_real_access_and_scientific_counters_are_zero(self):
        self.assertTrue(all(value == 0 for value in self.result["access_counters"].values()))

    def test_no_retry_rerun_or_real_authority_remains(self):
        disposition = self.result["disposition"]
        self.assertFalse(disposition["retry_allowed"])
        self.assertFalse(disposition["rerun_allowed"])
        self.assertFalse(disposition["resume_allowed"])
        self.assertFalse(disposition["fixture_tuning_allowed"])
        self.assertFalse(disposition["private_inventory_read_authorized"])
        self.assertFalse(disposition["member_acquisition_or_MARC2_FW2_authorized"])

    def test_next_gate_is_all_false_packet_only(self):
        gate = self.result["next_gate"]
        self.assertTrue(gate["result_commit_push_and_remote_green_required"])
        self.assertTrue(gate["all_false_private_read_packet_after_green_result"])
        self.assertTrue(gate["fresh_packet_bound_Tier_C_decision_required"])
        self.assertFalse(gate["private_read_or_selection_currently_authorized"])
        self.assertFalse(gate["archive_member_or_payload_currently_authorized"])

    def test_claim_boundary_preserves_generated_only_ceiling(self):
        boundary = self.result["claim_boundary"]
        self.assertIn("full-scale generated inventory", boundary["engineering_capability_added"])
        self.assertIn("no human neural data", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
