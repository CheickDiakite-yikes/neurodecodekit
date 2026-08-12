from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registries/marc1_http_identity_live_implementation.v0.json"
DOC_PATH = ROOT / "docs/MARC_1_HTTP_IDENTITY_LIVE_IMPLEMENTATION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1HTTPIdentityLiveImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_http_identity_live_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC1-HT1A")
        self.assertEqual(
            self.registry["status"],
            "generated_mock_HTTP_identity_wrapper_qualified_requires_remote_green_before_real_metadata",
        )

    def test_green_decision_proof_is_bound(self) -> None:
        proof = self.registry["green_decision"]
        self.assertEqual(proof["commit"], "9c7bd48541fbcebabcb9a783cb9047c7f2a2f57a")
        self.assertEqual(proof["push_CI_run_id"], 31587195405)
        self.assertEqual(proof["base_python_job_id"], 94083644849)
        self.assertEqual(proof["optional_neuro_job_id"], 94083644932)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["decision_registry_SHA256"],
            "949050b5c5369bc802e7015fd2c03a279dad15e88d5ab575189f547808a554ce",
        )

    def test_every_tracked_hash_matches(self) -> None:
        for binding in self.registry["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_surface_is_additive_and_consumed_executor_is_forbidden(self) -> None:
        surface = self.registry["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_install_dependency_delta"], 0)
        self.assertTrue(surface["green_HTTP_semantics_module_imported_without_modification"])
        self.assertTrue(surface["green_target_free_selector_imported_without_modification"])
        self.assertFalse(surface["consumed_executor_imported_called_or_modified"])
        self.assertFalse(surface["decoder_or_decompressor_interface"])
        self.assertFalse(surface["payload_signal_target_model_or_score_interface"])
        self.assertFalse(surface["alternate_path_endpoint_provider_or_cohort_interface"])

    def test_corrected_transport_semantics_are_exact(self) -> None:
        transport = self.registry["HTTP_identity_transport_contract"]
        self.assertEqual(
            transport["policy_SHA256"],
            "ac1b98eed57af7e545b925f1529ebf38de72b4277ea54a473ae1d6f7fe0cd3a6",
        )
        self.assertTrue(transport["absent_Content_Encoding_accepted"])
        self.assertTrue(transport["one_case_insensitive_identity_accepted"])
        self.assertTrue(transport["all_actual_codings_refused"])
        self.assertTrue(transport["empty_duplicate_and_list_values_refused"])
        self.assertTrue(transport["Transfer_Encoding_refused"])
        self.assertEqual(transport["decoding_or_decompression_operations"], 0)
        self.assertEqual(transport["accepted_terminal_body_count"], 1)
        self.assertEqual(transport["accepted_terminal_body_cap_bytes"], 2097152)

    def test_private_reader_and_root_isolation_are_exact(self) -> None:
        source = self.registry["private_Freewill_contract"]
        isolation = self.registry["private_root_isolation"]
        self.assertEqual(source["bytes"], 418755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["content_opens"], 1)
        self.assertEqual(source["SHA256_passes"], 1)
        self.assertEqual(source["strict_JSON_parses"], 1)
        self.assertEqual(source["archive_member_sibling_or_payload_operations"], 0)
        self.assertEqual(
            isolation["new_private_root"],
            ".codex_work/marc1_http_identity/live_recovery_v0",
        )
        self.assertEqual(
            isolation["old_consumed_private_root"],
            ".codex_work/marc1_pilot_selection/live_selection_v0",
        )
        self.assertTrue(isolation["old_root_lexically_refused_without_stat_or_open"])
        self.assertEqual(isolation["old_root_operations"], 0)

    def test_wrist_schema_target_firewall_and_selection_are_frozen(self) -> None:
        wrist = self.registry["Wrist_parser_contract"]
        selection = self.registry["selection_and_privacy_contract"]
        self.assertEqual(wrist["exact_file_rows"], 55)
        self.assertEqual(wrist["participant_archives"], 45)
        self.assertEqual(wrist["supplementary_rows"], 10)
        self.assertEqual(wrist["declared_record_bytes"], 3683416050)
        self.assertTrue(wrist["target_like_extra_fields_refused"])
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_selected_run_bundles"], 72)
        self.assertEqual(selection["Freewill_selected_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertEqual(selection["private_selected_rows"], 300)
        self.assertFalse(selection["selection_uses_target_quality_outcome_or_model_output"])

    def test_generated_measurements_hashes_and_refusals_are_bound(self) -> None:
        result = self.registry["generated_qualification"]
        self.assertEqual(result["route"], "MARC1HTL-G1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["accepted_response_cases"], 4)
        self.assertEqual(result["acceptance_gates_passed"], 21)
        self.assertEqual(result["generated_input_bytes"], 892922)
        self.assertEqual(result["selected_private_rows"], 300)
        self.assertEqual(result["required_mutations_passed"], 31)
        self.assertEqual(len(result["mutation_routes"]), 31)
        self.assertLessEqual(result["runtime_seconds"], 30)
        self.assertLessEqual(result["reported_peak_RSS_bytes"], 268435456)
        self.assertEqual(result["aggregate_report_bytes"], 8951)
        self.assertEqual(result["private_manifest_bytes"], 206509)
        self.assertEqual(result["combined_output_bytes"], 215460)
        self.assertEqual(result["real_or_forbidden_counter_sum"], 0)
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["generated_artifacts_committed"])
        self.assertFalse(result["scientific_value"])

    def test_all_implementation_access_counters_are_zero(self) -> None:
        counters = self.registry["implementation_access_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_resource_caps_protect_machine_storage_and_other_projects(self) -> None:
        caps = self.registry["resource_caps"]
        self.assertEqual(caps["CPU_threads"], 1)
        self.assertEqual(caps["workers"], 1)
        self.assertEqual(caps["numerical_jobs"], 1)
        self.assertEqual(caps["minimum_free_disk_bytes"], 12884901888)
        self.assertEqual(caps["peak_RSS_bytes"], 268435456)
        self.assertEqual(caps["network_body_cap_bytes"], 2097152)
        self.assertEqual(caps["incremental_disk_cap_bytes"], 4194304)
        self.assertEqual(caps["current_payload_network_bytes"], 0)
        self.assertEqual(caps["current_payload_disk_bytes"], 0)
        self.assertFalse(caps["operation_on_another_project"])

    def test_real_execution_is_closed_until_exact_wrapper_is_green(self) -> None:
        state = self.registry["execution_state"]
        gate = self.registry["next_gate"]
        self.assertFalse(state["implementation_commit_created"])
        self.assertFalse(state["implementation_pushed"])
        self.assertFalse(state["implementation_base_CI_green"])
        self.assertFalse(state["implementation_optional_neuro_CI_green"])
        self.assertFalse(state["real_metadata_execution_consumed"])
        self.assertFalse(state["real_metadata_may_begin_before_exact_green_wrapper"])
        self.assertFalse(state["retry_available"])
        self.assertFalse(state["rerun_available"])
        self.assertFalse(gate["one_private_and_one_public_metadata_selection_may_begin_now"])
        self.assertFalse(gate["payload_acquisition_may_begin"])
        self.assertFalse(gate["signal_target_model_or_score_work_may_begin"])

    def test_human_record_states_same_path_and_two_sentence_claim_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("not a pivot", text.lower())
        self.assertIn("thought-to-text", text)
        boundary = self.registry["claim_boundary"]
        self.assertTrue(boundary["same_thought_to_text_path"])
        self.assertFalse(boundary["is_pivot"])
        self.assertIn("no neural effect", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
