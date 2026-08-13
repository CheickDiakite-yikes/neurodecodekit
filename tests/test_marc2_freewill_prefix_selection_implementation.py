import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_freewill_prefix_selection as prefix


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_prefix_selection_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrefixSelectionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_freewill_prefix_selection_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["implementation_id"],
            "MARC-2-FW1-freewill-prefix-selection-generated-implementation-v0",
        )
        self.assertEqual(
            self.record["status"],
            "generated_mock_implementation_complete_locally_qualified_remote_green_required",
        )

    def test_all_artifact_bindings_are_current(self):
        for binding in self.record["artifact_bindings"].values():
            with self.subTest(path=binding["path"]):
                self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_green_contract_proof_is_exact(self):
        proof = self.record["green_contract_proof"]
        self.assertEqual(
            proof["commit"], "a12edebdab8b1252be546600d37fdb04503394d6"
        )
        self.assertEqual(proof["CI_run_id"], 31_676_261_134)
        self.assertEqual(proof["base_job_id"], 94_371_385_720)
        self.assertEqual(proof["optional_neuro_job_id"], 94_371_385_628)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["contract_sha256"], prefix.CONTRACT_SHA256)

    def test_surface_is_generated_only_and_dependency_light(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect"])
        self.assertFalse(surface["execute_command_available"])
        self.assertFalse(surface["network_client_available"])
        self.assertFalse(surface["real_path_or_credential_argument_available"])
        self.assertFalse(surface["archive_or_member_reader_available"])
        self.assertFalse(surface["event_or_neuro_reader_available"])
        self.assertFalse(surface["target_model_predictor_trainer_or_scorer_available"])
        self.assertEqual(surface["heavy_dependency_imports"], 0)

    def test_fixture_scale_and_content_firewall_are_exact(self):
        fixture = self.record["generated_fixture"]
        self.assertEqual(fixture["rows"], 1_227)
        self.assertEqual(fixture["regular_rows"], 1_025)
        self.assertEqual(fixture["directory_rows"], 202)
        self.assertEqual(fixture["source_run_bundles"], 195)
        self.assertEqual(fixture["eligible_subjects"], 19)
        self.assertEqual(fixture["candidate_run_bundles"], 114)
        self.assertEqual(fixture["candidate_core_members"], 456)
        self.assertFalse(fixture["contains_human_content"])
        self.assertFalse(fixture["contains_target_or_label"])

    def test_main_result_is_maximal_sixteen_person_prefix(self):
        result = self.record["main_selection_result"]
        contract = json.loads(
            (ROOT / "registries" / "marc2_freewill_prefix_selection_contract.v0.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result["route"], "MARC2FWG-R1")
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(
            result["selected_subject_ids"],
            contract["participant_rank"]["full_rank"][:16],
        )
        self.assertEqual(result["first_nonfitting_subject_id"], "sub-18")
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertTrue(result["selection_is_maximal_contiguous_prefix"])
        self.assertFalse(result["fallback_skip_substitution_or_budget_increase_used"])

    def test_main_reservation_is_bounded_and_next_subject_does_not_fit(self):
        result = self.record["main_selection_result"]
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["remaining_reservation_bytes"], 484_726_816)
        self.assertEqual(
            result["first_nonfitting_subject_reservation_bytes"],
            506_575_486,
        )
        self.assertEqual(result["reservation_cap_bytes"], 8 * 1024**3)
        self.assertGreater(
            result["selected_reservation_bytes"]
            + result["first_nonfitting_subject_reservation_bytes"],
            result["reservation_cap_bytes"],
        )

    def test_all_boundaries_pass(self):
        boundaries = self.record["boundary_results"]
        self.assertEqual(set(boundaries), {"floor_12", "all_19", "exact_cap", "cap_plus_one"})
        self.assertTrue(all(item["passed"] for item in boundaries.values()))
        self.assertEqual(boundaries["floor_12"]["selected_subjects"], 12)
        self.assertEqual(boundaries["all_19"]["selected_subjects"], 19)
        self.assertEqual(boundaries["exact_cap"]["selected_reservation_bytes"], 8 * 1024**3)
        self.assertEqual(boundaries["cap_plus_one"]["refusal_route"], prefix.REFUSAL_IDS[4])

    def test_all_mutations_pass_with_exact_route_counts(self):
        mutations = self.record["mutation_results"]
        self.assertEqual(mutations["required"], 40)
        self.assertEqual(mutations["passed"], 40)
        self.assertEqual(sum(mutations["route_counts"].values()), 40)
        self.assertEqual(
            mutations["route_counts"],
            {
                prefix.REFUSAL_IDS[0]: 3,
                prefix.REFUSAL_IDS[1]: 5,
                prefix.REFUSAL_IDS[2]: 12,
                prefix.REFUSAL_IDS[3]: 12,
                prefix.REFUSAL_IDS[4]: 4,
                prefix.REFUSAL_IDS[5]: 4,
            },
        )

    def test_measured_qualification_is_within_caps(self):
        measured = self.record["measured_development_qualification"]
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertLess(measured["internal_runtime_seconds"], 30)
        self.assertLess(measured["reported_peak_RSS_bytes"], 256 * 1024**2)
        self.assertLess(measured["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(
            measured["aggregate_report_bytes"] + measured["private_output_bytes"],
            measured["combined_output_bytes"],
        )
        self.assertTrue(measured["temporary_output_removed"])
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertEqual(measured["producer_is_causal"], "not_applicable_metadata_only")

    def test_verification_preserves_remote_green_boundary(self):
        verification = self.record["verification"]
        self.assertEqual(verification["focused_implementation_tests"], 30)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["contract_hash_passed"])
        self.assertTrue(verification["row_order_replay_passed"])
        self.assertTrue(verification["private_mode_0600_passed"])
        self.assertTrue(verification["aggregate_privacy_walk_passed"])
        self.assertTrue(verification["CLI_help_and_plan_passed"])
        self.assertEqual(verification["focused_registry_tests"], 14)
        self.assertEqual(verification["complete_base_tests"], 2_990)
        self.assertEqual(verification["complete_base_skips"], 204)
        self.assertEqual(verification["complete_optional_tests"], 3_061)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertFalse(verification["complete_base_suite_pending"])
        self.assertFalse(verification["complete_optional_suite_pending"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_all_authority_and_real_access_are_zero(self):
        self.assertTrue(
            all(value is False for value in self.record["authorization_flags"].values())
        )
        self.assertTrue(all(value == 0 for value in self.record["access_counters"].values()))

    def test_next_gate_requires_green_implementation_then_generated_closeout(self):
        gate = self.record["next_gate"]
        self.assertTrue(gate["commit_push_and_remote_green_exact_implementation_required"])
        self.assertTrue(gate["one_registered_generated_closeout_after_green_implementation"])
        self.assertTrue(gate["private_read_packet_only_after_green_generated_result"])
        self.assertTrue(gate["private_inventory_read_requires_fresh_packet_bound_Tier_C_decision"])
        self.assertFalse(gate["member_acquisition_or_MARC2_FW2_eligible"])

    def test_claim_boundary_is_explicit(self):
        boundary = self.record["claim_boundary"]
        self.assertIn("storage ceiling", boundary["engineering_capability_added"])
        self.assertIn("no human neural signal", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
