import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_freewill_private_selection as live


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_freewill_private_selection_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2FreewillPrivateSelectionImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_freewill_private_selection_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(
            self.record["implementation_id"],
            "MARC-2-FW1A-private-selection-wrapper-implementation-v0",
        )
        self.assertEqual(
            self.record["status"],
            "generated_mock_wrapper_qualified_requires_remote_green_before_private_selection",
        )

    def test_all_tracked_file_hashes_are_current(self):
        for binding in self.record["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(
                    sha256_file(ROOT / binding["path"]),
                    binding["sha256"],
                )

    def test_green_decision_proof_is_exact(self):
        proof = self.record["green_decision"]
        self.assertEqual(proof["commit"], live.GREEN_DECISION_COMMIT)
        self.assertEqual(proof["CI_run_id"], live.GREEN_DECISION_CI_RUN_ID)
        self.assertEqual(proof["base_job_id"], live.GREEN_DECISION_BASE_JOB_ID)
        self.assertEqual(
            proof["optional_neuro_job_id"],
            live.GREEN_DECISION_OPTIONAL_JOB_ID,
        )
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(proof["decision_registry_sha256"], live.DECISION_SHA256)

    def test_surface_is_fixed_dependency_light_and_proof_gated(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["execute_requires_exact_remote_green_proof"])
        self.assertFalse(
            surface[
                "generic_source_subject_seed_cap_split_member_URL_credential_or_model_override"
            ]
        )
        self.assertFalse(surface["consumed_MARC1_executor_import_or_call"])
        self.assertFalse(surface["network_client_available"])
        self.assertFalse(surface["archive_local_header_or_member_reader_available"])
        self.assertEqual(surface["heavy_dependency_imports"], 0)

    def test_private_source_is_bound_but_was_not_accessed(self):
        source = self.record["private_source_binding"]
        self.assertEqual(source["path"], str(live.PRIVATE_SOURCE_RELATIVE_PATH))
        self.assertEqual(source["bytes"], live.PRIVATE_SOURCE_BYTES)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["sha256"], live.PRIVATE_SOURCE_SHA256)
        self.assertEqual(source["entries"], live.PRIVATE_SOURCE_ENTRIES)
        self.assertFalse(source["path_stat_open_hash_or_parse_during_implementation"])

    def test_live_protocol_is_one_shot_and_stops_before_payload(self):
        protocol = self.record["live_protocol"]
        self.assertEqual(protocol["output_root"], str(live.OUTPUT_ROOT_RELATIVE_PATH))
        self.assertEqual(protocol["content_opens"], 1)
        self.assertEqual(protocol["sequential_read_passes"], 1)
        self.assertEqual(protocol["SHA256_passes"], 1)
        self.assertEqual(protocol["strict_JSON_parses"], 1)
        self.assertTrue(protocol["short_reads_supported_without_reopen"])
        self.assertTrue(protocol["consumed_marker_before_private_content_open"])
        self.assertTrue(protocol["aggregate_failure_receipt_after_consumed_marker"])
        self.assertFalse(protocol["retry_rerun_resume_repair_or_fallback_available"])
        self.assertEqual(protocol["network_bytes"], 0)
        self.assertEqual(protocol["archive_local_header_or_member_bytes"], 0)

    def test_generated_selection_matches_the_frozen_prefix(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], live.GENERATED_ROUTE)
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["reservation_cap_bytes"], 8 * 1024**3)
        contract = live.selector.load_registered_contract(ROOT)
        self.assertEqual(
            result["selected_subject_ids"],
            contract["participant_rank"]["full_rank"][:16],
        )

    def test_all_fifty_eight_refusals_are_bound(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["inherited_selector_mutations_passed"], 40)
        self.assertEqual(result["wrapper_mutations_passed"], 18)
        self.assertEqual(
            tuple(result["wrapper_mutation_routes"]),
            live.WRAPPER_MUTATIONS,
        )
        self.assertTrue(
            all(
                route in live.FAILURE_ROUTES
                for route in result["wrapper_mutation_routes"].values()
            )
        )
        self.assertEqual(sum(result["wrapper_route_counts"].values()), 18)

    def test_measured_qualification_is_within_every_cap(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["generated_input_bytes"], 846_712)
        self.assertEqual(measured["combined_output_bytes"], 296_659)
        self.assertLess(measured["internal_runtime_seconds"], live.MAX_RUNTIME_SECONDS)
        self.assertLess(measured["reported_peak_RSS_bytes"], live.MAX_PEAK_RSS_BYTES)
        self.assertLess(measured["combined_output_bytes"], live.MAX_COMBINED_OUTPUT_BYTES)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertEqual(measured["producer_is_causal"], "not_applicable_metadata_only")

    def test_verification_records_local_passes_and_pending_remote_CI(self):
        verification = self.record["verification"]
        self.assertEqual(verification["focused_functional_tests"], 26)
        self.assertEqual(verification["focused_registry_tests"], 14)
        self.assertEqual(verification["complete_base_tests"], 3_071)
        self.assertEqual(verification["complete_base_skips"], 204)
        self.assertEqual(verification["complete_optional_tests"], 3_142)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertTrue(verification["consumed_failure_receipt_test_passed"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_execution_state_is_unconsumed_and_marc2_fw2_is_closed(self):
        state = self.record["execution_state"]
        self.assertFalse(state["registered_private_execution_consumed"])
        self.assertEqual(state["registered_execution_limit"], 1)
        self.assertEqual(state["retry_rerun_or_resume_limit"], 0)
        self.assertFalse(state["private_selection_result_available"])
        self.assertFalse(state["MARC2_FW2_eligible"])

    def test_authority_stops_after_conditional_private_selection(self):
        authority = self.record["authorization_flags"]
        self.assertTrue(authority["one_private_selection_after_exact_wrapper_remote_green"])
        self.assertFalse(authority["private_selection_before_exact_wrapper_remote_green"])
        for key, value in authority.items():
            if key == "one_private_selection_after_exact_wrapper_remote_green":
                continue
            self.assertFalse(value, key)

    def test_every_implementation_access_counter_is_zero(self):
        counters = self.record["implementation_access_counters"]
        self.assertGreaterEqual(len(counters), 25)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_next_gate_and_claim_boundary_are_explicit(self):
        gate = self.record["next_gate"]
        self.assertTrue(gate["commit_push_and_remote_green_exact_wrapper_required"])
        self.assertTrue(gate["one_registered_private_selection_after_green_wrapper"])
        self.assertTrue(gate["inspect_aggregate_result_only"])
        self.assertFalse(gate["archive_member_or_payload_access_after_success"])
        self.assertTrue(gate["MARC2_FW2_requires_new_all_false_packet_and_Tier_C_decision"])
        boundary = self.record["claim_boundary"]
        self.assertIn("proof-gated", boundary["engineering_capability_added"])
        self.assertIn("no human neural signal", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
