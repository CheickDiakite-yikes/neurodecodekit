from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    ROOT / "registries/marc1_output_capability_recovery_implementation.v0.json"
)
DOCUMENT_PATH = ROOT / "docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_IMPLEMENTATION.md"
REGISTRY_SHA256 = "d2ea78bd173ab290b6f5eb56e67f8ed73d324ecdaae1fdee8fea4852f801506c"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1OutputCapabilityRecoveryImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.record = json.loads(cls.registry_bytes)

    def test_identity_hash_and_generated_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 10342)
        self.assertEqual(
            self.record["schema_name"],
            "neurodecodekit.marc1_output_capability_recovery_implementation",
        )
        self.assertEqual(self.record["schema_version"], "0.1.0")
        self.assertEqual(self.record["lane_id"], "MARC1-OP1")
        self.assertEqual(
            self.record["status"],
            "generated_only_implementation_qualified_registered_probe_and_closeout_not_executed",
        )

    def test_all_artifact_bindings_match(self) -> None:
        for binding in self.record["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_contract_proof_precedes_implementation(self) -> None:
        proof = self.record["green_contract_proof"]
        self.assertEqual(
            proof["commit"], "baade51146309bd3b3fa6c1750a36482669a0ff2"
        )
        self.assertEqual(proof["CI_run_id"], 31597291352)
        self.assertEqual(proof["base_python_job_id"], 94115807028)
        self.assertEqual(proof["optional_neuro_job_id"], 94115807008)
        self.assertTrue(proof["both_required_jobs_green_before_implementation"])

    def test_consumed_lane_remains_closed_and_byte_identical(self) -> None:
        boundary = self.record["consumed_lane_boundary"]
        self.assertEqual(boundary["consumed_lane"], "MARC1-PG1")
        self.assertEqual(boundary["consumed_route"], "MARC1PG-F07")
        self.assertEqual(boundary["consumed_qualifier_calls"], 0)
        self.assertEqual(boundary["consumed_source_modifications"], 0)
        self.assertFalse(boundary["retry_rerun_or_amendment"])
        self.assertTrue(boundary["pure_helper_composition_only"])

    def test_surface_is_dependency_light_deferred_and_narrow(self) -> None:
        surface = self.record["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertTrue(surface["python_S_compatible"])
        self.assertEqual(surface["base_dependency_delta"], 0)
        self.assertEqual(surface["commands"], ["plan", "preflight", "qualify", "inspect"])
        self.assertEqual(surface["module_scope_consumed_pagination_imports"], 0)
        self.assertEqual(surface["deferred_consumed_pagination_imports_after_capability"], 1)
        self.assertTrue(all(value == 0 for value in surface["forbidden_consumed_calls"].values()))
        for key in (
            "network_client",
            "live_URL_or_source_path",
            "consumed_root_name",
            "payload_signal_target_model_or_score_interface",
            "retry_fallback_automatic_pagination_or_substitution",
        ):
            with self.subTest(key=key):
                self.assertFalse(surface[key])

    def test_capability_and_output_lifecycle_are_exact(self) -> None:
        capability = self.record["output_capability"]
        self.assertTrue(capability["process_local_only"])
        self.assertFalse(capability["serialized"])
        self.assertEqual(
            capability["first_callable_operation_in_preflight_and_qualify"],
            "acquire_output_capability",
        )
        self.assertTrue(capability["parent_device_inode_and_type_bound"])
        self.assertTrue(capability["output_absence_checked_at_acquisition_and_prewrite"])
        self.assertEqual(capability["absolute_path_file_writes"], 0)
        lifecycle = self.record["output_lifecycle"]
        self.assertEqual(lifecycle["allowlisted_files"], 2)
        self.assertEqual(lifecycle["files_created"], 2)
        self.assertEqual(lifecycle["public_report_inspections"], 1)
        self.assertEqual(lifecycle["private_peer_inspections"], 0)
        self.assertEqual(lifecycle["cleanup_file_unlinks"], 2)
        self.assertFalse(lifecycle["output_exists_after_return"])

    def test_qualification_matrix_and_semantics_are_exact(self) -> None:
        qualification = self.record["generated_qualification"]
        self.assertEqual(qualification["accepted_cases_passed"], 6)
        self.assertEqual(qualification["refusal_cases_passed"], 32)
        self.assertEqual(qualification["precapability_refusals"], 19)
        self.assertEqual(qualification["postcapability_refusals"], 13)
        self.assertEqual(qualification["acceptance_gates_passed"], 20)
        identity = self.record["semantic_and_selection_identity"]
        self.assertEqual(identity["request_query"], "page=1&page_size=1000")
        self.assertEqual(identity["Wrist_rows"], 55)
        self.assertEqual(identity["selected_subjects_per_axis"], 12)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        self.assertTrue(identity["selection_target_label_quality_size_checksum_and_outcome_free"])

    def test_final_development_measurement_is_bounded_and_removed(self) -> None:
        measurement = self.record["final_development_measurement"]
        caps = self.record["resource_caps"]
        self.assertEqual(measurement["route"], "MARC1OP-G1")
        self.assertFalse(measurement["output_path_is_registered_closeout_path"])
        self.assertLess(measurement["runtime_seconds"], caps["runtime_seconds"])
        self.assertLess(measurement["reported_peak_RSS_bytes"], caps["peak_RSS_bytes"])
        self.assertLess(measurement["generated_input_bytes"], caps["generated_input_bytes"])
        self.assertLess(measurement["combined_output_bytes"], caps["combined_output_bytes"])
        self.assertTrue(measurement["temporary_output_removed"])
        self.assertEqual(measurement["network_bytes"], 0)
        self.assertEqual(measurement["real_or_private_input_bytes"], 0)

    def test_final_access_ledger_matches_measured_output(self) -> None:
        ledger = self.record["final_public_access_ledger"]
        measurement = self.record["final_development_measurement"]
        self.assertEqual(ledger["capability_acquisitions"], 1)
        self.assertEqual(ledger["capability_revalidations"], 1)
        self.assertEqual(ledger["repository_reads"], 10)
        self.assertEqual(ledger["contract_loads"], 2)
        self.assertEqual(ledger["output_files_created"], 2)
        self.assertEqual(ledger["output_bytes_allocated"], measurement["combined_output_bytes"])
        self.assertEqual(ledger["public_report_inspections"], 1)
        self.assertEqual(ledger["cleanup_file_unlinks"], 2)

    def test_all_forbidden_access_and_claim_counters_are_zero(self) -> None:
        counters = self.record["implementation_access_counters"]
        self.assertTrue(all(value == 0 for value in counters.values()))
        registered = self.record["registered_sequence"]
        self.assertEqual(registered["output_path_operations_during_implementation"], 0)
        self.assertFalse(registered["path_only_preflight_executed"])
        self.assertFalse(registered["generated_qualifier_executed"])

    def test_next_gate_is_remote_green_then_one_shot_registered_sequence(self) -> None:
        verification = self.record["qualification_tests"]
        self.assertEqual(verification["status"], "complete_all_acceptance_gates_passed")
        self.assertEqual(verification["focused_tests_passed"], 36)
        self.assertEqual(verification["final_MARC1_tests"], 587)
        self.assertEqual(verification["dependency_light_tests"], 2726)
        self.assertEqual(verification["optional_neuro_tests"], 2797)
        self.assertEqual(verification["additional_skips"], 0)
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["compile_passed"])
        self.assertTrue(verification["CLI_help_plan_preflight_qualify_inspect_passed"])
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertTrue(all(self.record["next_gate"].values()))
        registered = self.record["registered_sequence"]
        self.assertEqual(registered["preflight_success_route"], "MARC1OP-P0")
        self.assertEqual(registered["qualifier_success_route"], "MARC1OP-G1")
        self.assertTrue(
            registered["failure_parks_without_retry_rerun_substitution_or_amendment"]
        )

    def test_document_states_same_path_and_scientific_boundary(self) -> None:
        claim = self.record["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "It is not a scientific pivot.",
            "Engineering capability added:",
            "Scientific claim not established:",
            "registered generated closeout remain closed",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
