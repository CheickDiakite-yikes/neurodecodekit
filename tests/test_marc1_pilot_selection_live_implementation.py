from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / (
    "registries/marc1_privacy_preserving_pilot_selection_live_implementation.v0.json"
)
DOC_PATH = ROOT / "docs/MARC_1_PRIVACY_PRESERVING_PILOT_SELECTION_LIVE_IMPLEMENTATION.md"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class MARC1PilotSelectionLiveImplementationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_identity_and_status_are_exact(self) -> None:
        self.assertEqual(
            self.registry["schema_name"],
            "neurodecodekit.marc1_privacy_preserving_pilot_selection_live_implementation",
        )
        self.assertEqual(self.registry["schema_version"], "0.1.0")
        self.assertEqual(self.registry["lane_id"], "MARC1-P1A")
        self.assertEqual(
            self.registry["status"],
            "generated_mock_live_selector_qualified_requires_remote_green_before_real_metadata",
        )

    def test_green_decision_proof_is_bound(self) -> None:
        proof = self.registry["green_decision"]
        self.assertEqual(proof["commit"], "9726d07ab08e9c2815dbe68398659f454693be5e")
        self.assertEqual(proof["push_CI_run_id"], 31574870204)
        self.assertEqual(proof["base_python_job_id"], 94044627592)
        self.assertEqual(proof["optional_neuro_job_id"], 94044627647)
        self.assertTrue(proof["both_required_jobs_green"])
        self.assertEqual(
            proof["decision_registry_SHA256"],
            "fb97887d332749bc50e1dcdc69418b7f63b631a166032e6823565442c5c3fb39",
        )

    def test_every_tracked_hash_matches(self) -> None:
        for binding in self.registry["tracked_file_hashes"]:
            with self.subTest(path=binding["path"]):
                self.assertEqual(_sha256(ROOT / binding["path"]), binding["sha256"])

    def test_surface_is_additive_standard_library_and_payload_free(self) -> None:
        surface = self.registry["implementation_surface"]
        self.assertTrue(surface["standard_library_only"])
        self.assertEqual(surface["base_install_dependency_delta"], 0)
        self.assertTrue(surface["green_generated_selector_imported_without_modification"])
        self.assertFalse(surface["user_selected_path_endpoint_record_version_provider_or_credential_arguments"])
        self.assertFalse(surface["local_header_member_archive_or_payload_interface"])
        self.assertFalse(surface["signal_event_target_quality_model_or_score_interface"])
        self.assertFalse(surface["retry_rerun_resume_fallback_or_substitution_interface"])

    def test_private_reader_contract_is_exact_and_single_pass(self) -> None:
        source = self.registry["private_Freewill_contract"]
        self.assertEqual(source["bytes"], 418755)
        self.assertEqual(source["mode"], "0600")
        self.assertEqual(source["content_opens"], 1)
        self.assertEqual(source["bounded_reads"], 1)
        self.assertEqual(source["SHA256_passes"], 1)
        self.assertEqual(source["strict_JSON_parses"], 1)
        self.assertEqual(source["archive_member_sibling_or_payload_operations"], 0)
        self.assertFalse(source["private_input_published"])

    def test_wrist_parser_transport_and_target_firewall_are_frozen(self) -> None:
        wrist = self.registry["Wrist_transport_and_parser_contract"]
        self.assertEqual(wrist["record_id"], 29666735)
        self.assertEqual(wrist["version"], 3)
        self.assertEqual(wrist["accepted_response_body_count"], 1)
        self.assertEqual(wrist["accepted_response_body_cap_bytes"], 2097152)
        self.assertEqual(wrist["HTTP_request_attempt_cap"], 3)
        self.assertEqual(wrist["bodyless_redirect_cap"], 2)
        self.assertEqual(wrist["exact_file_rows"], 55)
        self.assertEqual(wrist["participant_archives"], 45)
        self.assertEqual(wrist["participant_name_rule"], "sub-01.zip_through_sub-45.zip_exactly_once")
        self.assertEqual(wrist["supplementary_rows"], 10)
        self.assertEqual(wrist["declared_record_bytes"], 3683416050)
        self.assertTrue(wrist["target_like_extra_fields_refused"])
        self.assertFalse(wrist["post_response_fallback_parser_or_rule_amendment"])
        self.assertEqual(wrist["payload_requests"], 0)

    def test_selection_privacy_and_output_contract_is_exact(self) -> None:
        selection = self.registry["selection_and_privacy_contract"]
        self.assertEqual(selection["selected_subjects_per_axis"], 12)
        self.assertEqual(selection["Freewill_selected_run_bundles"], 72)
        self.assertEqual(selection["Freewill_selected_core_members"], 288)
        self.assertEqual(selection["Wrist_selected_archives"], 12)
        self.assertEqual(selection["private_selected_rows"], 300)
        self.assertFalse(selection["selection_uses_target_quality_outcome_or_model_output"])
        self.assertFalse(selection["substitution_backfill_or_post_input_rule_change"])
        self.assertFalse(selection["public_individual_member_or_archive_rows"])
        self.assertTrue(selection["consumed_marker_precedes_first_real_input"])
        self.assertTrue(selection["second_invocation_refused"])

    def test_generated_qualification_measurements_and_hashes_are_bound(self) -> None:
        result = self.registry["generated_qualification"]
        self.assertEqual(result["route"], "MARC1PSL-G1")
        self.assertTrue(result["all_gates_passed"])
        self.assertEqual(result["acceptance_gates_passed"], 15)
        self.assertEqual(result["generated_input_bytes"], 866578)
        self.assertEqual(result["selected_private_rows"], 300)
        self.assertEqual(result["required_mutations_passed"], 26)
        self.assertEqual(len(result["mutation_routes"]), 26)
        self.assertLessEqual(result["runtime_seconds"], 30)
        self.assertLessEqual(result["reported_peak_RSS_bytes"], 268435456)
        self.assertEqual(result["aggregate_report_bytes"], 8044)
        self.assertEqual(result["private_manifest_bytes"], 206509)
        self.assertEqual(result["combined_output_bytes"], 214553)
        self.assertEqual(result["public_or_real_network_calls"], 0)
        self.assertEqual(result["real_or_forbidden_counter_sum"], 0)
        self.assertTrue(result["temporary_outputs_removed"])
        self.assertFalse(result["generated_artifacts_committed"])
        self.assertFalse(result["scientific_value"])

    def test_all_implementation_access_counters_are_zero(self) -> None:
        counters = self.registry["implementation_access_counters"]
        self.assertTrue(counters)
        self.assertTrue(all(value == 0 for value in counters.values()))

    def test_resource_caps_protect_machine_and_storage(self) -> None:
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

    def test_execution_is_closed_until_exact_wrapper_is_remotely_green(self) -> None:
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

    def test_human_record_has_two_sentence_claim_boundary(self) -> None:
        text = DOC_PATH.read_text(encoding="utf-8")
        self.assertIn("Engineering capability added:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("same research path", text.lower())
        self.assertIn("thought-to-text", text)
        boundary = self.registry["claim_boundary"]
        self.assertTrue(boundary["same_thought_to_text_path"])
        self.assertFalse(boundary["is_pivot"])
        self.assertIn("no neural effect", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
