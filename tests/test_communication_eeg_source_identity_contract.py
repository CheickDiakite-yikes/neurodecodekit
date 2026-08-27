import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT / "registries" / "communication_eeg_source_identity_contract.v0.json"
)
DOCUMENT_PATH = ROOT / "docs" / "COMMUNICATION_EEG_SOURCE_IDENTITY_PREREGISTRATION.md"
FRONTIER_PATH = ROOT / "registries" / "current_research_frontier.v0.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CommunicationEEGSourceIdentityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.document = DOCUMENT_PATH.read_text(encoding="utf-8")
        cls.frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))

    def test_schema_status_and_human_contract(self):
        self.assertEqual(
            self.contract["schema_name"],
            "neurodecodekit.communication_eeg_source_identity_contract",
        )
        self.assertEqual(self.contract["schema_version"], "0.1.0")
        self.assertEqual(
            self.contract["contract_id"], "COMM-L0-source-identity-contract-v0"
        )
        self.assertIn("GraphQL_unauthorized", self.contract["status"])
        self.assertIn("## Deterministic Bounded Selection", self.document)
        self.assertIn("## Claim Boundary", self.document)

    def test_parent_program_is_exact_and_green(self):
        parent = self.contract["parent_program"]
        self.assertEqual(
            parent["green_commit"],
            "acc4defe6ca79b2e8bd2091e424d373bb87ff526",
        )
        self.assertEqual(parent["CI_run_id"], 33_034_671_642)
        self.assertEqual(parent["base_python_job_id"], 98_394_689_906)
        self.assertEqual(parent["optional_neuro_readers_job_id"], 98_394_690_075)
        self.assertTrue(parent["both_required_jobs_green"])
        for binding in (parent["document"], parent["registry"], parent["test"]):
            self.assertEqual(sha256_file(ROOT / binding["path"]), binding["sha256"])

    def test_active_dreyer_packet_is_unchanged_and_unapproved(self):
        gate = self.contract["active_gate_preserved"]
        self.assertEqual(gate["gate_id"], "DREYER-C5R-1-HL")
        self.assertEqual(self.frontier["active_lane_id"], gate["gate_id"])
        self.assertTrue(gate["sole_active_Tier_C_packet"])
        self.assertFalse(gate["fresh_packet_bound_maintainer_decision_received"])
        self.assertFalse(gate["authority_changed_by_this_contract"])
        self.assertFalse(gate["communication_metadata_packet_active_now"])

    def test_exact_query_and_request_body_are_hash_bound(self):
        query = self.contract["GraphQL_contract"]
        query_bytes = query["query_text"].encode("utf-8")
        self.assertEqual(len(query_bytes), query["query_utf8_bytes"])
        self.assertEqual(hashlib.sha256(query_bytes).hexdigest(), query["query_sha256"])
        request_body = (
            json.dumps(
                {"query": query["query_text"]},
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=True,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(len(request_body), query["request_body_bytes"])
        self.assertEqual(
            hashlib.sha256(request_body).hexdigest(), query["request_body_sha256"]
        )
        self.assertIn('datasetId: "ds003626"', query["query_text"])
        self.assertIn('tag: "2.1.2"', query["query_text"])
        self.assertEqual(query["requests_if_future_authorized"], 1)
        self.assertFalse(query["variables_or_fallbacks_allowed"])

    def test_snapshot_and_tree_are_strict_but_not_prefit(self):
        snapshot = self.contract["snapshot_anchor_contract"]
        tree = self.contract["recursive_tree_contract"]
        self.assertEqual(snapshot["id"], "ds003626:2.1.2")
        self.assertEqual(snapshot["tag"], "2.1.2")
        self.assertTrue(snapshot["description_id_must_equal_hexsha"])
        self.assertTrue(snapshot["description_values_are_observed_not_prefit"])
        self.assertIsNone(tree["file_count_prefit"])
        self.assertIsNone(tree["total_bytes_prefit"])
        self.assertTrue(tree["full_relative_paths_unique_and_safe"])
        self.assertTrue(tree["public_S3_versionId_required"])
        self.assertFalse(tree["source_order_is_identity"])
        self.assertFalse(tree["individual_rows_public"])

    def test_selection_keeps_all_people_and_one_common_session(self):
        selection = self.contract["selected_inventory_contract"]
        self.assertEqual(
            selection["participant_ids_required_exactly"],
            [f"sub-{index:02d}" for index in range(1, 11)],
        )
        self.assertEqual(selection["complete_raw_sessions_per_participant_required"], 3)
        self.assertTrue(selection["common_session_label_set_required"])
        self.assertEqual(
            selection["session_selection_rule"],
            "lexicographically_first_common_complete_raw_session_label_for_all_ten_participants",
        )
        self.assertEqual(selection["participants_selected"], 10)
        self.assertEqual(selection["sessions_per_selected_participant"], 1)
        self.assertEqual(selection["raw_BDFs_selected"], 10)
        self.assertEqual(selection["raw_BDF_count_per_complete_session"], 1)
        self.assertIn("direct_children_only", selection["raw_session_directory_rule"])
        self.assertIn("all_non_BDF_direct_child_files", selection["required_companion_rule"])
        self.assertFalse(selection["companion_roles_inferred_from_contents"])
        self.assertFalse(selection["participant_dropping_or_substitution_allowed"])
        self.assertFalse(selection["fallback_query_or_selection_allowed"])

    def test_primary_slice_preserves_peripherals_and_rejects_processed_only(self):
        reported = self.contract["paper_reported_structure_not_yet_semantically_verified"]
        selection = self.contract["selected_inventory_contract"]
        self.assertEqual(reported["EEG_channels"], 128)
        self.assertEqual(reported["EOG_channels"], 4)
        self.assertEqual(reported["oral_EMG_channels"], 2)
        self.assertTrue(reported["raw_session_BDF_contains_EEG_EXG_and_tagged_events"])
        self.assertTrue(reported["processed_EEG_ICA_removed_EXG_correlated_sources"])
        self.assertFalse(reported["these_values_are_scientific_acceptance_identity_now"])
        self.assertIn("all_EXG", selection["required_primary_payload_role"])
        self.assertFalse(selection["derivatives_allowed"])
        self.assertFalse(selection["processed_EEG_or_EXG_arrays_allowed_as_primary_payload"])

    def test_selection_is_target_free_and_bounded(self):
        selection = self.contract["selected_inventory_contract"]
        firewall = self.contract["metadata_stage_firewall"]
        self.assertEqual(selection["maximum_selected_bytes"], 10 << 30)
        self.assertTrue(selection["park_if_structure_differs_or_cap_exceeded"])
        self.assertFalse(
            selection[
                "participant_or_session_selection_by_size_target_count_class_balance_signal_quality_or_result_allowed"
            ]
        )
        self.assertTrue(all(value == 0 for value in firewall.values()))

    def test_generated_stage_waits_for_green_and_has_no_scientific_value(self):
        generated = self.contract["generated_qualification_contract"]
        stages = self.contract["ordered_stages"]
        self.assertTrue(generated["allowed_only_after_green_registration"])
        self.assertGreaterEqual(len(generated["required_case_families"]), 18)
        self.assertFalse(
            generated["URL_opener_socket_HTTP_client_endpoint_or_execute_mode_allowed"]
        )
        self.assertFalse(generated["real_or_private_dataset_path_allowed"])
        self.assertFalse(generated["scientific_claim_value"])
        self.assertTrue(
            stages["generated_implementation_and_qualification"][
                "requires_green_registration"
            ]
        )
        self.assertFalse(
            stages["generated_implementation_and_qualification"]["authorized_now"]
        )

    def test_resource_caps_are_small_and_metadata_only(self):
        resources = self.contract["resource_caps"]
        self.assertEqual(resources["CPU_threads"], 1)
        self.assertEqual(resources["workers"], 1)
        self.assertEqual(resources["numerical_jobs"], 1)
        self.assertEqual(resources["wall_time_seconds"], 30)
        self.assertEqual(resources["peak_RSS_bytes"], 256 << 20)
        self.assertEqual(resources["generated_or_future_response_cap_bytes"], 2 << 20)
        self.assertEqual(resources["combined_generated_or_public_output_bytes"], 1 << 20)
        self.assertEqual(resources["network_bytes_now"], 0)
        self.assertEqual(resources["payload_network_bytes_now_or_future_metadata_stage"], 0)
        self.assertEqual(resources["maximum_future_payload_slice_bytes"], 10 << 30)
        self.assertEqual(
            resources["maximum_total_incremental_research_storage_bytes"], 20 << 30
        )
        self.assertTrue(
            resources[
                "future_payload_contract_must_reserve_full_projected_footprint_before_consumption"
            ]
        )
        self.assertFalse(resources["storage_allowance_expands_selected_cohort"])
        self.assertFalse(
            resources[
                "operation_outside_NeuroDecodeKit_or_cleanup_of_other_projects_allowed"
            ]
        )

    def test_all_authority_and_operation_counters_remain_zero(self):
        self.assertTrue(
            all(not value for value in self.contract["authorization_state"].values())
        )
        self.assertTrue(
            all(value == 0 for value in self.contract["operation_counters"].values())
        )
        decision = self.contract["ordered_stages"]["tier_C_metadata_decision"]
        self.assertTrue(decision["fresh_packet_bound_message_required"])
        self.assertFalse(decision["current_automatic_continuation_is_authorization"])

    def test_router_and_claim_ceiling_are_non_scientific(self):
        router = self.contract["router"]
        self.assertEqual(router["success_route"], "COMM-L0-R1")
        self.assertEqual(len(router["ordered_failure_routes"]), 8)
        self.assertFalse(router["success_is_scientific_result"])
        boundary = self.contract["claim_boundary"]
        self.assertIn("source-identity", boundary["engineering_capability_proposed"])
        self.assertIn("No dataset-specific response", boundary["scientific_claim_not_established"])


if __name__ == "__main__":
    unittest.main()
