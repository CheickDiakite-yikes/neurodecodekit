from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "registries/fresh_motor_source_admission_generated_qualification_contract.v0.json"
)
DOCUMENT = (
    ROOT
    / "docs/FRESH_MOTOR_SOURCE_ADMISSION_GENERATED_QUALIFICATION_PREREGISTRATION.md"
)


class FreshMotorSourceAdmissionGeneratedQualificationContractTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_green_correction_state_is_exactly_bound(self) -> None:
        predecessor = self.contract["predecessor"]
        self.assertEqual(
            predecessor["exact_green_state_commit"],
            "8fe98df7e08e7e1e40860e6023832c3b092d78d2",
        )
        self.assertEqual(predecessor["main_CI_run_id"], 33_340_527_773)
        self.assertEqual(predecessor["main_base_python_job_id"], 99_335_260_650)
        self.assertEqual(
            predecessor["main_optional_neuro_readers_job_id"], 99_335_260_756
        )
        self.assertTrue(predecessor["both_required_main_jobs_green"])
        self.assertTrue(predecessor["both_required_branch_jobs_green"])
        self.assertEqual(predecessor["bound_artifact_count"], 6)
        self.assertEqual(predecessor["bound_artifact_bytes"], 92_513)

    def test_surface_is_new_generated_only_and_has_no_execute(self) -> None:
        surface = self.contract["additive_surface"]
        self.assertEqual(
            surface["module"],
            "src/neurodecodekit/datasets/fresh_motor_source_admission.py",
        )
        self.assertEqual(surface["commands"], ["plan", "qualify-generated"])
        self.assertFalse(surface["execute_command_present"])
        self.assertFalse(surface["URL_host_credential_or_source_path_option_present"])
        self.assertEqual(surface["network_imports_allowed"], [])
        self.assertFalse(surface["existing_discovery_module_modified"])
        self.assertFalse(surface["base_dependency_added"])

    def test_revision_modes_close_parallel_array_and_surrogate_ambiguity(self) -> None:
        modes = self.contract["revision_modes"]
        self.assertTrue(modes["exactly_one_mode_payload_required"])
        self.assertFalse(modes["generated_mode_assignment_admits_real_source"])
        global_revision = modes["SOURCE_GLOBAL_REVISION"]
        self.assertTrue(global_revision["pre_and_post_observations_must_match"])
        self.assertIn("revision_raw_bytes", global_revision["required_fields"])
        self.assertIn("ETag", global_revision["prohibited_standalone_surrogates"])
        snapshot = modes["OPAQUE_COMPLETE_SNAPSHOT_REPLAY"]
        self.assertFalse(snapshot["parallel_arrays_allowed"])
        self.assertEqual(snapshot["ordered_pages_field"], "pages")
        self.assertTrue(snapshot["poison_candidate_fixture_required"])
        self.assertFalse(snapshot["candidate_fields_parsed_retained_ranked_or_selected"])

    def test_CI_profile_is_attempt_specific_and_not_a_current_ref_check(self) -> None:
        profile = self.contract["generated_CI_profile"]
        self.assertEqual(profile["response_count"], 2)
        self.assertEqual(profile["run_endpoint_kind"], "exact_workflow_run_attempt")
        self.assertFalse(profile["current_refs_heads_main_request_present"])
        self.assertEqual(profile["run_attempt"], 1)
        self.assertEqual(profile["required_jobs"], ["Base Python", "Optional Neuro Readers"])
        self.assertEqual(profile["job_total_count"], 2)
        self.assertFalse(profile["job_pagination_allowed"])
        self.assertFalse(profile["workflow_blob_hash_proven_by_run_and_jobs_responses"])
        self.assertFalse(profile["live_profile_armable"])

    def test_marker_contract_is_durable_and_narrow(self) -> None:
        marker = self.contract["consumed_marker_contract"]
        self.assertEqual(
            marker["open_flags"],
            ["O_CREAT", "O_EXCL", "O_WRONLY", "O_NOFOLLOW"],
        )
        self.assertEqual(marker["file_mode_octal"], "0600")
        self.assertTrue(marker["file_fsync_before_close"])
        self.assertTrue(marker["no_follow_parent_directory_fsync"])
        self.assertTrue(marker["exactly_one_creator"])
        self.assertFalse(marker["receipt_resume_after_process_exit"])
        self.assertEqual(
            marker["cleanup_scope"],
            "only_invocation_created_generated_temporary_directory",
        )

    def test_exact_refusal_matrix_and_precedence_are_frozen(self) -> None:
        precedence = self.contract["refusal_precedence"]
        self.assertEqual(precedence[0], "AUTHORITY_REFUSE")
        self.assertEqual(precedence[1], "QUALIFICATION_NETWORK_REFUSE")
        mutations = self.contract["refusal_mutations"]
        observed = sum(len(rows) for rows in mutations.values())
        self.assertEqual(observed, 82)
        self.assertEqual(observed, self.contract["refusal_mutation_count"])
        self.assertEqual(len(set(name for rows in mutations.values() for name in rows)), 82)

    def test_resources_and_all_protected_authorities_are_closed(self) -> None:
        resources = self.contract["resource_contract"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["maximum_runtime_seconds"], 30)
        self.assertEqual(resources["maximum_absolute_peak_RSS_bytes"], 256 * 1024**2)
        self.assertEqual(resources["maximum_aggregate_report_bytes"], 1024**2)
        self.assertEqual(resources["network_bytes"], 0)
        authority = self.contract["operation_authority_after_exact_registration_green"]
        self.assertTrue(authority["additive_generated_only_implementation"])
        self.assertTrue(authority["generated_fixture_tests"])
        for key, value in authority.items():
            if key in {
                "additive_generated_only_implementation",
                "generated_fixture_tests",
                "one_bounded_generated_only_qualification_after_implementation_exact_green",
                "cleanup_only_invocation_created_generated_temporary_directory",
            }:
                self.assertTrue(value, key)
            else:
                self.assertFalse(value, key)

    def test_scientific_coordinates_and_language_boundary_do_not_move(self) -> None:
        coordinate = self.contract["scientific_evidence_coordinate"]
        self.assertFalse(coordinate["live_CI_parser_is_live_neural_translation"])
        self.assertFalse(coordinate["live_motor_success_validates_language"])
        self.assertTrue(coordinate["communication_requires_separate_preregistration"])
        for dimension in range(1, 7):
            suffix = {
                1: "spatial",
                2: "temporal",
                3: "physiological",
                4: "task_autonomy",
                5: "population_generalization",
                6: "translation",
            }[dimension]
            self.assertTrue(coordinate[f"dimension_{dimension}_{suffix}"].startswith("unchanged_"))

    def test_human_document_states_engineering_and_nonclaim_separately(self) -> None:
        document = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability specified:", document)
        self.assertIn("Scientific claim not established:", document)
        self.assertIn("Exactly 82 named mutations", document)
        self.assertIn("no `execute`", document)


if __name__ == "__main__":
    unittest.main()
