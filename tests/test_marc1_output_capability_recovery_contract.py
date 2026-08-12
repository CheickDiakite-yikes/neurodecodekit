from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc1_output_capability_recovery_contract.v0.json"
DOCUMENT_PATH = ROOT / "docs/MARC_1_OUTPUT_CAPABILITY_RECOVERY_PREREGISTRATION.md"
REGISTRY_SHA256 = "2fe17a263a8c923c2a7af76dbba0c6422eacb601b7668de987ef0d53485c5cb6"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1OutputCapabilityRecoveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_bytes = REGISTRY_PATH.read_bytes()
        cls.contract = json.loads(cls.registry_bytes)

    def test_identity_hash_and_frozen_status_are_exact(self) -> None:
        self.assertEqual(hashlib.sha256(self.registry_bytes).hexdigest(), REGISTRY_SHA256)
        self.assertEqual(len(self.registry_bytes), 13122)
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.marc1_output_capability_recovery_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(self.contract["lane_id"], "MARC1-OP1")
        self.assertEqual(
            self.contract["status"],
            "frozen_generated_only_contract_no_implementation_or_execution",
        )

    def test_every_artifact_binding_matches(self) -> None:
        for binding in self.contract["artifact_bindings"]:
            with self.subTest(path=binding["path"]):
                path = ROOT / binding["path"]
                self.assertEqual(path.stat().st_size, binding["bytes"])
                self.assertEqual(_sha256(path), binding["sha256"])

    def test_green_research_proof_is_exact(self) -> None:
        proof = self.contract["green_research_anchor"]
        self.assertEqual(
            proof["commit"],
            "d02830b95c76bc428a297c6415db933452af5cbb",
        )
        self.assertEqual(proof["CI_run_id"], 31595996923)
        self.assertEqual(proof["base_python_job_id"], 94111539407)
        self.assertEqual(proof["optional_neuro_job_id"], 94111539431)
        self.assertTrue(proof["both_required_jobs_green_before_contract"])

    def test_consumed_lane_is_closed_but_pure_helpers_are_deferred(self) -> None:
        boundary = self.contract["consumed_lane_boundary"]
        self.assertTrue(boundary["MARC1_PG1_consumed"])
        self.assertFalse(boundary["MARC1_PG1_retry_or_rerun"])
        self.assertFalse(boundary["consumed_qualifier_may_be_called"])
        self.assertFalse(boundary["consumed_source_may_be_modified"])
        self.assertTrue(
            boundary["pure_helpers_may_be_deferred_imported_after_capability"]
        )
        self.assertFalse(boundary["live_metadata_packet_eligible_now"])

    def test_future_surface_is_narrow_and_has_no_eager_import(self) -> None:
        surface = self.contract["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(
            surface["commands"],
            ["plan", "preflight", "qualify", "inspect"],
        )
        self.assertFalse(surface["module_scope_consumed_pagination_import"])
        self.assertTrue(
            surface["deferred_hash_bound_pure_helper_import_after_capability"]
        )
        for key in (
            "network_client",
            "URL_or_local_source_input",
            "consumed_private_root_name",
            "payload_signal_target_model_or_score_interface",
            "retry_fallback_automatic_pagination_or_substitution",
        ):
            with self.subTest(key=key):
                self.assertFalse(surface[key])
        self.assertEqual(
            set(surface["forbidden_consumed_calls"]),
            {"qualify_generated_pagination", "_assert_new_output_directory", "main"},
        )

    def test_capability_is_first_held_private_and_revalidated(self) -> None:
        capability = self.contract["capability_identity"]
        self.assertTrue(capability["process_local_only"])
        self.assertFalse(capability["serialized"])
        self.assertEqual(
            capability["first_operation_in_preflight_and_qualify"],
            "acquire_output_capability",
        )
        self.assertEqual(len(capability["before_capability_zero_counters"]), 7)
        self.assertTrue(capability["all_ancestor_lstat"])
        self.assertTrue(capability["all_symlink_ancestors_refused"])
        self.assertTrue(capability["lstat_fstat_device_inode_type_match"])
        self.assertTrue(capability["held_descriptor_revalidated_prewrite"])
        self.assertFalse(capability["silent_fallback_allowed"])

    def test_write_contract_is_parent_relative_exclusive_and_allowlisted(self) -> None:
        write = self.contract["write_contract"]
        self.assertEqual(write["absolute_path_writes"], 0)
        self.assertEqual(write["output_directory_creation"], "mkdir_dir_fd")
        self.assertEqual(write["allowlisted_output_files"], 2)
        self.assertEqual(write["public_report_inspections"], 1)
        self.assertIn("O_EXCL", write["file_creation"])
        self.assertIn("dir_fd", write["file_creation"])
        self.assertFalse(write["generated_outputs_committed"])

    def test_registered_path_probe_and_qualifier_sequence_is_one_shot(self) -> None:
        sequence = self.contract["registered_local_sequence"]
        self.assertEqual(
            sequence["output_path"],
            "/private/tmp/neurodecodekit-marc1op1-registered-closeout-20260812",
        )
        self.assertFalse(sequence["output_path_statted_created_or_reserved_at_contract_time"])
        self.assertEqual(sequence["path_only_preflight_invocations"], 1)
        self.assertEqual(sequence["qualifier_invocations_after_preflight_success"], 1)
        self.assertEqual(sequence["preflight_success_route"], "MARC1OP-P0")
        self.assertTrue(sequence["preflight_failure_parks_without_retry"])
        self.assertTrue(sequence["post_capability_failure_parks_without_retry"])
        self.assertFalse(sequence["path_substitution"])
        self.assertFalse(sequence["retry_or_rerun"])

    def test_case_matrix_is_exact_unique_and_complete(self) -> None:
        accepted = self.contract["accepted_cases"]
        refused = self.contract["refusal_cases"]
        self.assertEqual(len(accepted), 6)
        self.assertEqual(len(accepted), len(set(accepted)))
        self.assertEqual(len(refused), 32)
        self.assertEqual(len(refused), len(set(refused)))
        self.assertEqual(refused[0], "relative_path")
        self.assertEqual(
            refused[-1],
            "second_registered_preflight_or_qualifier_invocation",
        )

    def test_routes_and_acceptance_gates_are_exact(self) -> None:
        routes = self.contract["routes"]
        self.assertEqual(len(routes), 10)
        self.assertEqual(
            set(routes),
            {f"MARC1OP-F0{index}" for index in range(8)}
            | {"MARC1OP-P0", "MARC1OP-G1"},
        )
        gates = self.contract["acceptance_gates"]
        self.assertEqual(len(gates), 20)
        self.assertEqual(len(gates), len(set(gates)))
        self.assertIn(
            "all_19_precapability_mutations_refuse_with_zero_early_counters",
            gates,
        )
        self.assertIn("exact_generated_cleanup", gates)

    def test_semantics_and_resources_remain_unchanged_and_bounded(self) -> None:
        identity = self.contract["unchanged_semantic_identity"]
        self.assertEqual(identity["request_query"], "page=1&page_size=1000")
        self.assertEqual(identity["Wrist_rows"], 55)
        self.assertEqual(identity["selected_subjects_per_axis"], 12)
        self.assertEqual(identity["fit_heldout_overlap"], 0)
        caps = self.contract["resource_caps"]
        self.assertEqual((caps["CPU_threads"], caps["workers"], caps["numerical_jobs"]), (1, 1, 1))
        self.assertEqual(caps["peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(caps["network_bytes"], 0)
        self.assertEqual(caps["real_or_private_input_bytes"], 0)
        verification = self.contract["verification"]
        self.assertEqual(verification["focused_contract_tests_passed"], 12)
        self.assertEqual(verification["MARC_tests_passed"], 551)
        self.assertEqual(verification["dependency_light_tests_passed"], 2690)
        self.assertEqual(verification["optional_neuro_tests_passed"], 2761)
        self.assertEqual(
            verification["optional_first_invocation_failed_existing_process_peak_RSS_tests"],
            2,
        )
        self.assertEqual(
            verification["failed_tests_passed_together_in_fresh_focused_process"],
            2,
        )
        self.assertTrue(verification["ruff_passed"])
        self.assertTrue(verification["source_and_test_compile_passed"])
        self.assertTrue(verification["git_diff_check_passed"])
        self.assertEqual(verification["forbidden_operations"], 0)

    def test_current_access_authorization_and_claim_boundary_are_closed(self) -> None:
        self.assertTrue(
            all(value == 0 for value in self.contract["current_access_counters"].values())
        )
        self.assertTrue(
            all(value is False for value in self.contract["authorization_flags"].values())
        )
        self.assertTrue(all(self.contract["next_gate"].values()))
        claim = self.contract["claim_boundary"]
        self.assertTrue(claim["same_thought_to_text_path"])
        self.assertFalse(claim["is_pivot"])
        document = DOCUMENT_PATH.read_text(encoding="utf-8")
        for phrase in (
            "MARC1OP-P0",
            "MARC1OP-G1",
            "It must not modify the consumed source file",
            "Engineering capability proposed:",
            "Scientific claim not established:",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, document)


if __name__ == "__main__":
    unittest.main()
