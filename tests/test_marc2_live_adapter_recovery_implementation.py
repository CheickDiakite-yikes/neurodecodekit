import hashlib
import json
import unittest
from pathlib import Path

from neurodecodekit.datasets import marc2_live_schema_adapter_recovery as live


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT
    / "registries"
    / "marc2_live_adapter_recovery_implementation.v0.json"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Marc2LiveAdapterRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_identity_and_status_are_exact(self):
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc2_live_adapter_recovery_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC2-LA2")
        self.assertEqual(
            self.record["implementation_id"],
            "MARC-2-LA2-live-adapter-recovery-implementation-v0",
        )
        self.assertEqual(
            self.record["status"],
            "generated_mock_live_adapter_recovery_qualified_requires_remote_green_before_private_selection",
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

    def test_surface_is_fixed_dependency_light_and_additive(self):
        surface = self.record["implementation_surface"]
        self.assertEqual(surface["commands"], ["plan", "qualify", "inspect", "execute"])
        self.assertTrue(surface["execute_requires_exact_remote_green_proof"])
        self.assertTrue(surface["exact_shared_validator_import_and_call"])
        self.assertTrue(surface["exact_LA1_adapter_import_and_call"])
        self.assertTrue(surface["exact_selector_import_and_call"])
        self.assertFalse(surface["generic_source_or_output_override"])
        self.assertFalse(surface["consumed_executor_import_call_edit_copy_or_expose"])
        self.assertFalse(surface["network_client_available"])
        self.assertFalse(surface["archive_local_header_or_member_reader_available"])
        self.assertEqual(surface["heavy_dependency_imports"], 0)

    def test_native_registry_and_shared_certificate_are_distinct(self):
        certificate = self.record["proof_certificate"]
        self.assertEqual(certificate["lane_id"], "MARC2-FW1B")
        self.assertEqual(certificate["native_registry_lane_id"], "MARC2-LA2")
        self.assertEqual(
            certificate["path"],
            live.PROOF_CERTIFICATE_RELATIVE_PATH.as_posix(),
        )
        self.assertEqual(
            certificate["shared_validator_symbol"],
            live.validate_implementation_record.__name__,
        )
        self.assertTrue(certificate["sha256_bound_by_green_evidence"])
        records = live.validate_local_qualification_records(ROOT)
        self.assertEqual(records["certificate_record"]["lane_id"], "MARC2-FW1B")
        self.assertEqual(records["native_record"]["lane_id"], "MARC2-LA2")

    def test_private_source_is_bound_but_was_not_accessed(self):
        source = self.record["private_source_binding"]
        self.assertEqual(source["path"], str(live.PRIVATE_SOURCE_RELATIVE_PATH))
        self.assertEqual(source["bytes"], live.PRIVATE_SOURCE_BYTES)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["sha256"], live.PRIVATE_SOURCE_SHA256)
        self.assertEqual(source["entries"], live.PRIVATE_SOURCE_ENTRIES)
        self.assertFalse(source["path_stat_open_hash_or_parse_during_implementation"])

    def test_private_protocol_is_one_shot_and_stops_before_payload(self):
        protocol = self.record["private_protocol"]
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

    def test_generated_selection_matches_frozen_prefix(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["route"], live.GENERATED_ROUTE)
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["selected_subjects"], 16)
        self.assertEqual(result["selected_run_bundles"], 96)
        self.assertEqual(result["selected_core_members"], 384)
        self.assertEqual(result["selected_reservation_bytes"], 8_105_207_776)
        self.assertEqual(result["reservation_cap_bytes"], 8 * 1024**3)

    def test_all_fifty_six_direct_refusals_are_bound(self):
        result = self.record["generated_qualification"]
        self.assertEqual(result["proof_certificate_mutations_passed"], 32)
        self.assertEqual(result["executor_mutations_passed"], 24)
        self.assertEqual(result["total_direct_mutations_passed"], 56)
        self.assertEqual(
            tuple(result["proof_certificate_mutation_order"]),
            live.PROOF_MUTATIONS,
        )
        self.assertEqual(
            tuple(result["executor_mutation_routes"]),
            live.EXECUTOR_MUTATIONS,
        )
        self.assertTrue(
            all(
                route in live.FAILURE_ROUTES
                for route in result["executor_mutation_routes"].values()
            )
        )
        self.assertEqual(sum(result["executor_route_counts"].values()), 24)

    def test_resource_envelope_and_measurement_semantics_are_exact(self):
        measured = self.record["generated_qualification"]
        self.assertEqual(measured["generated_input_bytes"], 846_696)
        self.assertEqual(measured["combined_output_bytes"], 221_863)
        self.assertEqual(measured["aggregate_report_bytes"], 8_083)
        self.assertEqual(measured["private_selection_fixture_bytes"], 213_780)
        self.assertEqual(
            measured["aggregate_report_sha256"],
            "cc9fd833b315f2f761a76d2ac511eed7edcb8dea18db06b7b026cc457109ba98",
        )
        self.assertEqual(
            measured["private_selection_fixture_sha256"],
            "bc84340e1ddb323060cc7ed3d58205d41f49cbaaa117b030e51edb51434fc378",
        )
        self.assertEqual(measured["internal_runtime_seconds"], 0.27368504100013524)
        self.assertEqual(measured["reported_peak_RSS_bytes"], 37_978_112)
        self.assertEqual(measured["CPU_threads"], 1)
        self.assertEqual(measured["workers"], 1)
        self.assertEqual(measured["numerical_jobs"], 1)
        self.assertFalse(measured["end_to_end_latency_measured"])
        self.assertEqual(measured["producer_is_causal"], "not_applicable_metadata_only")
        self.assertTrue(measured["temporary_output_removed"])
        resources = self.record["resource_caps"]
        self.assertEqual(resources["runtime_seconds_per_stage"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["combined_output_bytes"], 2 * 1024**2)
        self.assertEqual(resources["incremental_disk_bytes"], 4 * 1024**2)
        self.assertEqual(resources["minimum_free_disk_bytes"], 15 * 1024**3)

    def test_verification_records_local_passes_and_pending_remote_CI(self):
        verification = self.record["verification"]
        self.assertGreaterEqual(verification["focused_functional_tests"], 30)
        self.assertGreaterEqual(verification["focused_registry_tests"], 14)
        self.assertGreaterEqual(verification["complete_base_tests"], 3_400)
        self.assertEqual(verification["complete_base_skips"], 204)
        self.assertGreaterEqual(verification["complete_optional_tests"], 3_470)
        self.assertEqual(verification["complete_optional_skips"], 35)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertTrue(verification["consumed_failure_receipt_test_passed"])
        self.assertTrue(verification["remote_CI_pending"])

    def test_execution_state_is_unconsumed_and_FW2_is_closed(self):
        state = self.record["execution_state"]
        self.assertFalse(state["registered_private_execution_consumed"])
        self.assertEqual(state["registered_execution_limit"], 1)
        self.assertEqual(state["retry_rerun_or_resume_limit"], 0)
        self.assertFalse(state["private_selection_result_available"])
        self.assertFalse(state["MARC2_FW2_eligible"])

    def test_authority_stops_after_conditional_private_selection(self):
        authority = self.record["authorization_flags"]
        self.assertTrue(authority["one_private_selection_after_exact_executor_remote_green"])
        self.assertFalse(authority["private_selection_before_exact_executor_remote_green"])
        for key, value in authority.items():
            if key == "one_private_selection_after_exact_executor_remote_green":
                continue
            self.assertFalse(value, key)

    def test_every_implementation_access_counter_is_zero(self):
        counters = self.record["implementation_access_counters"]
        self.assertGreaterEqual(len(counters), 25)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_next_gate_and_claim_boundary_are_explicit(self):
        gate = self.record["next_gate"]
        self.assertTrue(gate["commit_push_and_remote_green_exact_executor_required"])
        self.assertTrue(gate["one_registered_private_selection_after_green_executor"])
        self.assertTrue(gate["inspect_aggregate_result_only"])
        self.assertFalse(gate["archive_member_or_payload_access_after_success"])
        self.assertTrue(gate["MARC2_FW2_requires_new_all_false_packet_and_Tier_C_decision"])
        boundary = self.record["claim_boundary"]
        self.assertIn("proof-gated", boundary["engineering_capability_added"])
        self.assertIn("no human neural signal", boundary["scientific_claim_not_established"])
        self.assertIn("thought-to-text", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
