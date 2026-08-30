from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v1.json"
DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_RESEARCH_PREREGISTRATION_AMENDMENT_1.md"
V0_CONTRACT = ROOT / "registries/fresh_motor_source_research_contract.v0.json"
V0_DOCUMENT = ROOT / "docs/FRESH_MOTOR_SOURCE_RESEARCH_PREREGISTRATION.md"
FRONTIER_V9 = ROOT / "registries/current_research_frontier.v9.json"
FRONTIER_V10 = ROOT / "registries/current_research_frontier.v10.json"
LEDGER = ROOT / "registries/scientific_knowledge_ledger.v0.json"

INDEX_IDS = ["OPENNEURO", "NEMAR", "PHYSIONET", "GIGADB", "BNCI_HORIZON_2020"]
EXACT_QUERIES = [
    '"motor imagery" EEG EOG EMG',
    '"movement intention" EEG EOG EMG',
    '"motor execution" EEG EOG EMG',
    '"hand movement" EEG EOG EMG',
]
EXCLUDED_SOURCES = [
    "BNCI-2014-001__NEMAR-nm000139",
    "DREYER-DATASET-A__NEMAR-nm000250",
    "OFNER-2017__NEMAR-nm000173",
    "IACKD__OPENNEURO-ds006840",
    "PHYSIONET-EEGMMIDB",
    "SPANISHBCBL-S7-S20-S21-S24-S25",
]
STORAGE_COMPONENTS = {
    "selected_source_payload_bytes": 12 * 2**30,
    "invocation_temporary_bytes": 2 * 2**30,
    "derivative_and_frozen_prediction_bytes": 2 * 2**30,
    "atomic_publication_overhead_bytes": 1 * 2**30,
    "untouched_safety_reserve_bytes": 3 * 2**30,
}
SORT_KEYS = [
    "complete_participant_count_descending",
    "bilateral_EMG_coverage_boolean_descending",
    "kinematic_coverage_boolean_descending",
    "independent_laboratory_device_participant_component_count_descending",
    "minimum_trials_per_participant_descending",
    "storage_headroom_bytes_descending",
    "canonical_candidate_id_codepoint_ascending",
]


class FreshMotorSourceResearchV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def assert_critical_contract(self, contract: dict[str, object]) -> None:
        discovery = contract["frozen_discovery_universe"]
        self.assertEqual(
            [row["id"] for row in discovery["official_indexes"]],
            INDEX_IDS,
        )
        self.assertEqual(discovery["exact_text_queries"], EXACT_QUERIES)
        self.assertFalse(
            discovery["NO_QUALIFYING_SOURCE_allowed_after_any_index_or_pagination_cap_park"]
        )
        self.assertEqual(
            contract["freshness"]["excluded_consumed_source_ids"], EXCLUDED_SOURCES
        )
        self.assertEqual(
            contract["deterministic_candidate_selection"]["ordered_sort_keys"],
            SORT_KEYS,
        )
        self.assertFalse(
            contract["deterministic_candidate_selection"]["missing_sort_value_allowed"]
        )
        self.assertEqual(
            contract["ordered_routing"]["ELIGIBLE_FOR_METADATA_RESEARCH"]["condition"],
            "every_field_in_metadata_eligibility_predicate_is_explicitly_satisfied_by_allowlisted_index_level_fields",
        )
        storage = contract["storage_budget"]
        for key, expected in STORAGE_COMPONENTS.items():
            self.assertEqual(storage[key], expected, key)
        self.assertEqual(storage["total_incremental_disk_cap_bytes"], 20 * 2**30)
        packet = contract["future_discovery_packet_requirements"]
        self.assertEqual(packet["maximum_network_requests"], 128)
        self.assertEqual(packet["maximum_response_body_bytes_total"], 32 * 2**20)
        self.assertEqual(packet["maximum_retained_public_artifact_bytes"], 8 * 2**20)
        self.assertEqual(packet["retry_count"], 0)
        self.assertTrue(
            packet[
                "redirect_every_hop_scheme_host_port_and_resolved_method_must_match_exact_allowlist_before_contact"
            ]
        )
        self.assertFalse(packet["redirect_method_rewrite_allowed"])
        self.assertTrue(packet["ordered_redirect_transcript_must_be_recorded"])
        self.assertTrue(packet["complete_pagination_required"])
        self.assertFalse(packet["partial_or_truncated_results_may_be_ranked_or_selected"])
        self.assertFalse(
            packet["payload_range_archive_member_header_signal_event_annotation_target_or_label_request_allowed"]
        )

    def test_v1_additively_supersedes_unaccepted_v0(self) -> None:
        self.assertEqual(self.contract["protocol_id"], "FMSR1-v1")
        supersedes = self.contract["supersedes"]
        self.assertEqual(supersedes["protocol_id"], "FMSR1-v0")
        self.assertEqual(
            supersedes["human_sha256"], hashlib.sha256(V0_DOCUMENT.read_bytes()).hexdigest()
        )
        self.assertEqual(
            supersedes["machine_sha256"], hashlib.sha256(V0_CONTRACT.read_bytes()).hexdigest()
        )
        self.assertFalse(supersedes["accepted_as_scientific_registration"])
        self.assertEqual(supersedes["protected_operations"], 0)

    def test_predecessor_frontier_and_NPA1_proof_are_exact(self) -> None:
        anchors = self.contract["proof_anchors"]
        self.assertEqual(
            anchors["predecessor_frontier_sha256"],
            hashlib.sha256(FRONTIER_V9.read_bytes()).hexdigest(),
        )
        self.assertEqual(anchors["NPA1_G_CI_run_id"], 33_285_776_358)
        self.assertTrue(anchors["NPA1_G_both_required_jobs_green"])

    def test_discovery_universe_is_frozen_and_complete_or_parks(self) -> None:
        discovery = self.contract["frozen_discovery_universe"]
        self.assertEqual([row["id"] for row in discovery["official_indexes"]], INDEX_IDS)
        self.assertEqual(discovery["exact_text_queries"], EXACT_QUERIES)
        self.assertTrue(discovery["all_returned_candidates_and_exclusions_recorded"])
        self.assertFalse(discovery["general_search_engine_allowed"])
        self.assertFalse(discovery["result_truncation_allowed"])
        self.assertFalse(discovery["ad_hoc_candidate_addition_allowed"])
        self.assertEqual(discovery["cap_breach_route"], "DISCOVERY_CAP_PARK")
        self.assertFalse(
            discovery["NO_QUALIFYING_SOURCE_allowed_after_any_index_or_pagination_cap_park"]
        )

    def test_routing_is_ordered_and_not_circular(self) -> None:
        routes = self.contract["ordered_routing"]
        self.assertFalse(
            routes["DISCOVERED_CANDIDATE"]["eligible_for_candidate_specific_metadata_packet"]
        )
        self.assertTrue(
            routes["ELIGIBLE_FOR_METADATA_RESEARCH"][
                "eligible_for_candidate_specific_metadata_packet"
            ]
        )
        self.assertFalse(
            routes["ELIGIBLE_FOR_METADATA_RESEARCH"][
                "eligible_for_transport_canary_packet"
            ]
        )
        self.assertTrue(
            routes["FULL_CONFIRMATION_SOURCE"]["eligible_for_transport_canary_packet"]
        )
        self.assertIn("NO_QUALIFYING_SOURCE", routes["no_candidate_outcomes"])
        self.assertFalse(routes["criteria_may_be_weakened_after_no_candidate"])

    def test_candidate_selection_is_total_and_forbidden_inputs_are_excluded(self) -> None:
        canonical = self.contract["candidate_canonicalization"]
        self.assertEqual(
            canonical["canonical_candidate_id_components_in_order"],
            [
                "official_index_id",
                "immutable_source_identifier",
                "immutable_release_identifier",
            ],
        )
        self.assertFalse(canonical["empty_or_missing_component_allowed"])
        selection = self.contract["deterministic_candidate_selection"]
        self.assertEqual(selection["ordered_sort_keys"], SORT_KEYS)
        self.assertFalse(selection["missing_sort_value_allowed"])
        self.assertFalse(
            selection[
                "model_target_participant_outcome_hidden_payload_download_convenience_or_positive_result_input_allowed"
            ]
        )
        self.assertEqual(selection["incomplete_surface_outcome"], "DISCOVERY_CAP_PARK")

    def test_joint_nuisance_comparators_are_mandatory(self) -> None:
        conditions = self.contract["required_future_scientific_conditions"]
        self.assertIn("joint_nuisance_only", conditions)
        self.assertIn("joint_nuisance_plus_deranged_central_EEG", conditions)
        self.assertIn("joint_nuisance_plus_central_EEG", conditions)
        joint = self.contract["joint_comparator_contract"]
        self.assertIn(
            "task_relevant_EMG_for_every_relevant_effector",
            joint["joint_nuisance_components"],
        )
        self.assertFalse(joint["separate_control_wins_can_replace_joint_comparator_wins"])
        self.assertTrue(
            self.contract["noncompensatory_hard_gates"][
                "task_relevant_EMG_required_for_every_relevant_effector"
            ]
        )

    def test_storage_arithmetic_exactly_partitions_20_GiB(self) -> None:
        storage = self.contract["storage_budget"]
        for key, expected in STORAGE_COMPONENTS.items():
            self.assertEqual(storage[key], expected, key)
        components = tuple(storage[key] for key in STORAGE_COMPONENTS)
        self.assertEqual(sum(components), storage["total_incremental_disk_cap_bytes"])
        self.assertEqual(storage["total_incremental_disk_cap_bytes"], 20 * 2**30)
        self.assertFalse(storage["participant_dropping_to_fit_budget_allowed"])

    def test_consumed_sources_are_preserved_exactly(self) -> None:
        self.assertEqual(
            self.contract["freshness"]["excluded_consumed_source_ids"],
            EXCLUDED_SOURCES,
        )

    def test_future_packet_is_fully_bounded_and_target_free(self) -> None:
        packet = self.contract["future_discovery_packet_requirements"]
        self.assertTrue(packet["packet_must_bind_exact_endpoint_URL_revision_and_method_for_each_index"])
        self.assertEqual(packet["maximum_network_requests"], 128)
        self.assertEqual(packet["maximum_response_body_bytes_total"], 32 * 2**20)
        self.assertEqual(packet["maximum_retained_public_artifact_bytes"], 8 * 2**20)
        self.assertEqual(packet["maximum_runtime_seconds"], 300)
        self.assertEqual(packet["maximum_peak_RSS_bytes"], 256 * 2**20)
        self.assertEqual(packet["CPU_threads"], 1)
        self.assertEqual(packet["workers"], 1)
        self.assertEqual(packet["retry_count"], 0)
        self.assertTrue(
            packet[
                "redirect_every_hop_scheme_host_port_and_resolved_method_must_match_exact_allowlist_before_contact"
            ]
        )
        self.assertFalse(packet["redirect_method_rewrite_allowed"])
        self.assertTrue(packet["ordered_redirect_transcript_must_be_recorded"])
        self.assertTrue(packet["complete_pagination_required"])
        self.assertFalse(packet["partial_or_truncated_results_may_be_ranked_or_selected"])
        self.assertFalse(packet["authentication_cookie_or_private_credential_allowed"])
        self.assertFalse(packet["download_or_payload_URL_retention_allowed"])

    def test_storage_and_status_are_consistent_across_current_surfaces(self) -> None:
        frontier = json.loads(FRONTIER_V10.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertEqual(
            frontier["current_registration"]["storage_component_sum_bytes"],
            self.contract["storage_budget"]["total_incremental_disk_cap_bytes"],
        )
        for expected in STORAGE_COMPONENTS.values():
            self.assertIn(f"{expected:,}", text)
        evidence = {row["id"]: row for row in ledger["evidence"]}
        summary = evidence["EVID-FMSR1-V1-REGISTRATION"]["summary"]
        self.assertIn("Pending exact remote proof", summary)
        self.assertIn("12+2+2+1+3 GiB", summary)
        self.assertNotIn("NeuroDecodeKit now has", text)

    def test_critical_contract_mutations_fail(self) -> None:
        mutations = []

        def mutate_index(contract: dict[str, object]) -> None:
            contract["frozen_discovery_universe"]["official_indexes"][0]["id"] = "OTHER"

        def mutate_query(contract: dict[str, object]) -> None:
            contract["frozen_discovery_universe"]["exact_text_queries"][0] = "broad query"

        def remove_ofner_exclusion(contract: dict[str, object]) -> None:
            contract["freshness"]["excluded_consumed_source_ids"].remove(
                "OFNER-2017__NEMAR-nm000173"
            )

        def reorder_selection(contract: dict[str, object]) -> None:
            keys = contract["deterministic_candidate_selection"]["ordered_sort_keys"]
            keys[0], keys[1] = keys[1], keys[0]

        def change_temporary_budget(contract: dict[str, object]) -> None:
            contract["storage_budget"]["invocation_temporary_bytes"] += 1

        def enable_retry(contract: dict[str, object]) -> None:
            contract["future_discovery_packet_requirements"]["retry_count"] = 1

        def allow_partial_selection(contract: dict[str, object]) -> None:
            contract["future_discovery_packet_requirements"][
                "partial_or_truncated_results_may_be_ranked_or_selected"
            ] = True

        def allow_unchecked_intermediate_redirect(contract: dict[str, object]) -> None:
            contract["future_discovery_packet_requirements"][
                "redirect_every_hop_scheme_host_port_and_resolved_method_must_match_exact_allowlist_before_contact"
            ] = False

        mutations.extend(
            [
                mutate_index,
                mutate_query,
                remove_ofner_exclusion,
                reorder_selection,
                change_temporary_budget,
                enable_retry,
                allow_partial_selection,
                allow_unchecked_intermediate_redirect,
            ]
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate.__name__):
                malformed = copy.deepcopy(self.contract)
                mutate(malformed)
                with self.assertRaises(AssertionError):
                    self.assert_critical_contract(malformed)

    def test_all_authorities_counters_and_claims_are_false_or_zero(self) -> None:
        for key, value in self.contract["operation_authority"].items():
            self.assertFalse(value, key)
        for key, value in self.contract["operation_counters"].items():
            self.assertEqual(value, 0, key)
        for key, value in self.contract["claim_boundary"].items():
            self.assertFalse(value, key)
        self.assertFalse(
            self.contract["conditional_next_gate_after_exact_remote_green"][
                "describes_present_authority"
            ]
        )

    def test_document_states_capability_nonclaim_and_no_current_source(self) -> None:
        text = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("Engineering capability pending proof:", text)
        self.assertIn("Scientific claim not established:", text)
        self.assertIn("No current candidate occupies any route", text)
        self.assertIn("joint_nuisance_only", text)


if __name__ == "__main__":
    unittest.main()
